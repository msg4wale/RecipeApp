import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Barrier
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.admin_audit import CHEF_REVIEW_SUBJECT, query_admin_audit
from app.database import SessionLocal, engine
from app.email import EmailDeliveryError, TransactionalEmail
from app.main import app, get_email_sender, get_storage, hash_password
from app.models import AdminDecision, ChefVerification, User, UserSession
from app.storage import StorageError


class ReviewStorage:
    def __init__(self) -> None:
        self.calls: list[tuple[str, bool]] = []
        self.fail_presign = False

    def generate_presigned_download_url(
        self,
        bucket: str,
        object_key: str,
        *,
        private_access_authorized: bool = False,
    ) -> str:
        self.calls.append((object_key, private_access_authorized))
        if self.fail_presign:
            raise StorageError("storage unavailable")
        return f"https://storage.example/{object_key}?signed=true"


class RecordingEmailSender:
    def __init__(self) -> None:
        self.messages: list[TransactionalEmail] = []
        self.fail_delivery = False

    def send(self, message: TransactionalEmail) -> None:
        self.messages.append(message)
        if self.fail_delivery:
            raise EmailDeliveryError("simulated delivery failure")


@pytest.fixture
def recording_email_sender() -> RecordingEmailSender:
    return RecordingEmailSender()


@pytest.fixture
def admin_client(recording_email_sender: RecordingEmailSender):
    storage = ReviewStorage()
    app.dependency_overrides[get_storage] = lambda: storage
    app.dependency_overrides[get_email_sender] = lambda: recording_email_sender
    with TestClient(app) as client:
        yield client, storage
    app.dependency_overrides.clear()


def create_user(role: str, *, chef_status: str | None = None) -> tuple[int, str]:
    email = f"{role}-{uuid4()}@example.com"
    password = "Password123!"
    with SessionLocal() as db:
        user = User(
            email=email,
            display_name=f"{role.title()} User",
            password_hash=hash_password(password),
            role=role,
            chef_status=chef_status,
            email_verified=True,
        )
        db.add(user)
        db.commit()
        user_id = user.id

    return user_id, email


def login(client: TestClient, email: str) -> str:
    response = client.post("/api/auth/login", json={"email": email, "password": "Password123!"})
    assert response.status_code == 200
    return response.json()["token"]


def create_application(user_id: int, *, status: str = "pending_review") -> int:
    with SessionLocal() as db:
        application = ChefVerification(
            user_id=user_id,
            certificate_ref=f"chef-certificates/applications/{user_id}/{uuid4().hex}",
            status=status,
        )
        db.add(application)
        db.commit()
        return application.id


def headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def setup_review(
    admin_client: tuple[TestClient, ReviewStorage],
) -> tuple[TestClient, ReviewStorage, int, int, str, int]:
    client, storage = admin_client
    admin_email = f"admin-{uuid4()}@example.com"
    with SessionLocal() as db:
        admin = User(
            email=admin_email,
            display_name="Review Admin",
            password_hash=hash_password("Password123!"),
            role="admin",
        )
        db.add(admin)
        db.commit()
        admin_id = admin.id
    token = login(client, admin_email)
    user_id, _ = create_user("regular", chef_status="pending_review")
    verification_id = create_application(user_id)
    return client, storage, user_id, admin_id, token, verification_id


def test_admin_queue_requires_admin_and_returns_private_certificate_link(admin_client) -> None:
    client, storage, user_id, _, token, verification_id = setup_review(admin_client)
    regular_id, regular_email = create_user("regular")
    regular_token = login(client, regular_email)

    assert client.get("/api/admin/chef-verifications").status_code == 401
    unauthorized_decision = client.post(
        f"/api/admin/chef-verifications/{verification_id}/decision",
        json={"decision": "approve"},
    )
    assert unauthorized_decision.status_code == 401
    forbidden = client.get("/api/admin/chef-verifications", headers=headers(regular_token))
    assert forbidden.status_code == 403
    forbidden_decision = client.post(
        f"/api/admin/chef-verifications/{verification_id}/decision",
        headers=headers(regular_token),
        json={"decision": "approve"},
    )
    assert forbidden_decision.status_code == 403

    response = client.get("/api/admin/chef-verifications?status=pending", headers=headers(token))

    assert response.status_code == 200
    application = next(item for item in response.json()["items"] if item["id"] == verification_id)
    assert application["applicant"]["id"] == user_id
    assert application["status"] == "pending_review"
    assert application["certificate_url"].startswith("https://storage.example/")
    certificate_key = application["certificate_url"].split("https://storage.example/", 1)[1].split("?", 1)[0]
    assert (certificate_key, True) in storage.calls
    assert all(private_access for _, private_access in storage.calls)
    assert regular_id != user_id


def test_admin_approval_promotes_applicant_and_persists_review_audit(
    admin_client, recording_email_sender: RecordingEmailSender
) -> None:
    client, _, user_id, admin_id, token, verification_id = setup_review(admin_client)

    response = client.post(
        f"/api/admin/chef-verifications/{verification_id}/decision",
        headers=headers(token),
        json={"decision": "approve", "rationale": "Certificate verified"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "active"
    assert response.json()["decision"] == "approve"
    assert response.json()["rationale"] == "Certificate verified"
    assert response.json()["notification_status"] == "sent"
    with SessionLocal() as db:
        applicant_email = db.query(User).filter_by(id=user_id).one().email
    assert recording_email_sender.messages == [
        TransactionalEmail(
            recipient=applicant_email,
            subject="Your Chef application was approved",
            text_body=(
                "Hello Regular User,\n\n"
                "Your Chef application has been approved. Your account is now an active Chef account, "
                "and you can publish recipes.\n"
            ),
        )
    ]
    with SessionLocal() as db:
        user = db.query(User).filter_by(id=user_id).one()
        verification = db.query(ChefVerification).filter_by(id=verification_id).one()
        assert user.role == "chef"
        assert user.chef_status == "active"
        assert verification.status == "active"
        assert verification.reviewed_by_user_id == admin_id
        assert verification.reviewed_at is not None
        assert verification.rationale == "Certificate verified"

        audit_entries = query_admin_audit(
            db,
            subject_type=CHEF_REVIEW_SUBJECT,
            subject_id=verification_id,
        )
        assert len(audit_entries) == 1
        audit_entry = audit_entries[0]
        assert audit_entry.subject_type == CHEF_REVIEW_SUBJECT
        assert audit_entry.subject_id == verification_id
        assert audit_entry.actor_user_id == admin_id

        def as_utc(value: datetime) -> datetime:
            if value.tzinfo is None or value.utcoffset() is None:
                return value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)

        assert audit_entry.timestamp == as_utc(verification.reviewed_at)
        assert audit_entry.outcome == verification.status == "active"
        assert audit_entry.rationale == verification.rationale == "Certificate verified"
        assert audit_entry.submitted_at == as_utc(verification.created_at)
        assert audit_entry.turnaround_seconds == (
            as_utc(verification.reviewed_at) - as_utc(verification.created_at)
        ).total_seconds()
        assert (
            db.query(AdminDecision)
            .filter_by(subject_type=CHEF_REVIEW_SUBJECT, subject_id=verification_id)
            .count()
            == 0
        )

    repeated = client.post(
        f"/api/admin/chef-verifications/{verification_id}/decision",
        headers=headers(token),
        json={"decision": "reject", "rationale": "Repeated decision"},
    )
    assert repeated.status_code == 409
    assert len(recording_email_sender.messages) == 1
    with SessionLocal() as db:
        verification = db.query(ChefVerification).filter_by(id=verification_id).one()
        user = db.query(User).filter_by(id=user_id).one()
        assert verification.status == "active"
        assert verification.rationale == "Certificate verified"
        assert user.role == "chef"


def test_competing_decisions_have_one_postgresql_16_winner(
    admin_client,
    recording_email_sender: RecordingEmailSender,
) -> None:
    if engine.dialect.name != "postgresql":
        pytest.skip("set DATABASE_URL to the supported PostgreSQL 16 test database")

    with engine.connect() as connection:
        server_version = connection.dialect.server_version_info
        missing_tables = [
            table_name
            for table_name in ("users", "auth_sessions", "chef_verifications", "admin_decisions")
            if not inspect(connection).has_table(table_name)
        ]
    assert server_version is not None and server_version[0] == 16
    assert not missing_tables, f"PostgreSQL test schema is not already present: {missing_tables}"

    client, _ = admin_client
    user_ids: list[int] = []
    verification_id: int | None = None
    try:
        first_admin_id, first_admin_email = create_user("admin")
        user_ids.append(first_admin_id)
        second_admin_id, second_admin_email = create_user("admin")
        user_ids.append(second_admin_id)
        applicant_id, _ = create_user("regular", chef_status="pending_review")
        user_ids.append(applicant_id)
        verification_id = create_application(applicant_id)
        assert verification_id is not None

        tokens = [login(client, first_admin_email), login(client, second_admin_email)]
        requests = [
            {
                "token": tokens[0],
                "admin_id": first_admin_id,
                "decision": "approve",
                "rationale": "Competing approval",
            },
            {
                "token": tokens[1],
                "admin_id": second_admin_id,
                "decision": "reject",
                "rationale": "Competing rejection",
            },
        ]
        start = Barrier(2, timeout=5)

        def submit_decision(request: dict[str, object]):
            start.wait()
            response = client.post(
                f"/api/admin/chef-verifications/{verification_id}/decision",
                headers=headers(str(request["token"])),
                json={
                    "decision": request["decision"],
                    "rationale": request["rationale"],
                },
            )
            return request, response

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(submit_decision, request) for request in requests]
            results = [future.result(timeout=15) for future in futures]

        winners = [(request, response) for request, response in results if response.status_code == 200]
        losers = [(request, response) for request, response in results if response.status_code == 409]
        assert len(winners) == 1
        assert len(losers) == 1

        winner_request, winner_response = winners[0]
        loser_request, _ = losers[0]
        winner_body = winner_response.json()
        expected_status = "active" if winner_request["decision"] == "approve" else "rejected"
        assert winner_body["decision"] == winner_request["decision"]
        assert winner_body["status"] == expected_status
        assert winner_body["reviewed_by_user_id"] == winner_request["admin_id"]
        assert winner_body["rationale"] == winner_request["rationale"]
        assert winner_request["admin_id"] != loser_request["admin_id"]

        with SessionLocal() as db:
            verification = db.query(ChefVerification).filter_by(id=verification_id).one()
            applicant = db.query(User).filter_by(id=applicant_id).one()
            assert verification.status == expected_status
            assert verification.reviewed_by_user_id == winner_request["admin_id"]
            assert verification.reviewed_at is not None
            assert verification.reviewed_at.isoformat() == winner_body["reviewed_at"]
            assert verification.rationale == winner_request["rationale"]
            assert applicant.chef_status == expected_status
            assert applicant.role == ("chef" if expected_status == "active" else "regular")
        assert len(recording_email_sender.messages) == 1
    finally:
        with SessionLocal() as db:
            if verification_id is not None:
                db.query(ChefVerification).filter_by(id=verification_id).delete(synchronize_session=False)
            if user_ids:
                db.query(UserSession).filter(UserSession.user_id.in_(user_ids)).delete(synchronize_session=False)
                db.query(User).filter(User.id.in_(user_ids)).delete(synchronize_session=False)
            db.commit()


def test_admin_rejection_keeps_regular_role_and_persists_review_audit(
    admin_client, recording_email_sender: RecordingEmailSender
) -> None:
    client, _, user_id, _, token, verification_id = setup_review(admin_client)

    response = client.post(
        f"/api/admin/chef-verifications/{verification_id}/decision",
        headers=headers(token),
        json={"decision": "reject", "rationale": "Certificate is not valid"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"
    assert response.json()["notification_status"] == "sent"
    with SessionLocal() as db:
        applicant_email = db.query(User).filter_by(id=user_id).one().email
    assert recording_email_sender.messages == [
        TransactionalEmail(
            recipient=applicant_email,
            subject="Your Chef application was not approved",
            text_body=(
                "Hello Regular User,\n\n"
                "Your Chef application has not been approved. Your account remains a regular user "
                "and does not have Chef publishing privileges.\n"
            ),
        )
    ]
    with SessionLocal() as db:
        user = db.query(User).filter_by(id=user_id).one()
        verification = db.query(ChefVerification).filter_by(id=verification_id).one()
        assert user.role == "regular"
        assert user.chef_status == "rejected"
        assert verification.status == "rejected"
        assert verification.reviewed_by_user_id is not None
        assert verification.reviewed_at is not None
        assert verification.rationale == "Certificate is not valid"

    repeated = client.post(
        f"/api/admin/chef-verifications/{verification_id}/decision",
        headers=headers(token),
        json={"decision": "reject"},
    )
    assert repeated.status_code == 409
    assert len(recording_email_sender.messages) == 1


@pytest.mark.parametrize(
    ("decision", "expected_status"),
    [("approve", "active"), ("reject", "rejected")],
)
def test_notification_delivery_failure_is_explicit_after_committed_decision(
    admin_client,
    recording_email_sender: RecordingEmailSender,
    decision: str,
    expected_status: str,
) -> None:
    client, _, user_id, admin_id, token, verification_id = setup_review(admin_client)
    recording_email_sender.fail_delivery = True

    response = client.post(
        f"/api/admin/chef-verifications/{verification_id}/decision",
        headers=headers(token),
        json={"decision": decision, "rationale": "Reviewed application"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Chef application decision was recorded, but applicant notification delivery failed"
    )
    assert len(recording_email_sender.messages) == 1

    with SessionLocal() as db:
        applicant = db.query(User).filter_by(id=user_id).one()
        application = db.query(ChefVerification).filter_by(id=verification_id).one()
        assert applicant.chef_status == expected_status
        assert applicant.role == ("chef" if decision == "approve" else "regular")
        assert application.status == expected_status
        assert application.reviewed_by_user_id == admin_id
        assert application.reviewed_at is not None
        assert application.rationale == "Reviewed application"

    retry = client.post(
        f"/api/admin/chef-verifications/{verification_id}/decision",
        headers=headers(token),
        json={"decision": decision, "rationale": "Reviewed application"},
    )
    assert retry.status_code == 409
    assert len(recording_email_sender.messages) == 1


def test_decision_rejects_missing_or_invalid_applications(admin_client) -> None:
    client, _, _, _, token, verification_id = setup_review(admin_client)
    headers_value = headers(token)

    missing = client.post(
        "/api/admin/chef-verifications/999999/decision",
        headers=headers_value,
        json={"decision": "approve"},
    )
    invalid = client.post(
        f"/api/admin/chef-verifications/{verification_id}/decision",
        headers=headers_value,
        json={"decision": "defer"},
    )

    assert missing.status_code == 404
    assert invalid.status_code == 422


def test_queue_reports_certificate_storage_failure(admin_client) -> None:
    client, storage, _, _, token, _ = setup_review(admin_client)
    storage.fail_presign = True

    response = client.get("/api/admin/chef-verifications", headers=headers(token))

    assert response.status_code == 503


def test_decision_database_failure_rolls_back_application_and_user(
    admin_client,
    recording_email_sender: RecordingEmailSender,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _, user_id, _, token, verification_id = setup_review(admin_client)

    def fail_commit(_self: Session) -> None:
        raise RuntimeError("simulated database failure")

    monkeypatch.setattr(Session, "commit", fail_commit)
    response = client.post(
        f"/api/admin/chef-verifications/{verification_id}/decision",
        headers=headers(token),
        json={"decision": "approve"},
    )
    assert response.status_code == 500
    assert recording_email_sender.messages == []

    monkeypatch.undo()
    with SessionLocal() as db:
        user = db.query(User).filter_by(id=user_id).one()
        verification = db.query(ChefVerification).filter_by(id=verification_id).one()
        assert user.role == "regular"
        assert user.chef_status == "pending_review"
        assert verification.status == "pending_review"
        assert verification.reviewed_by_user_id is None
        assert verification.reviewed_at is None
        assert verification.rationale is None
