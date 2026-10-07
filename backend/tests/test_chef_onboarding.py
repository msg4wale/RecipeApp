import logging
import os
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.email import TransactionalEmail
from app.main import app, get_email_sender, get_storage, token_digest
from app.models import ChefVerification, EmailVerificationToken, User
from app.storage import S3Storage, StorageBucket, UploadPolicy


VALID_PDF = b"%PDF-1.7\ncertificate"


class FakeEmailSender:
    def __init__(self) -> None:
        self.messages: list[TransactionalEmail] = []

    def send(self, message: TransactionalEmail) -> None:
        self.messages.append(message)


class MemoryS3Client:
    def __init__(self) -> None:
        self.objects: dict[tuple[str, str], bytes] = {}
        self.calls: list[str] = []

    def put_object(self, **kwargs: object) -> None:
        self.calls.append("put")
        body = kwargs["Body"]
        self.objects[(str(kwargs["Bucket"]), str(kwargs["Key"]))] = (
            body.read() if hasattr(body, "read") else body
        )

    def delete_object(self, **kwargs: object) -> None:
        self.calls.append("delete")
        self.objects.pop((str(kwargs["Bucket"]), str(kwargs["Key"])), None)


@pytest.fixture
def onboarding_client():
    sender = FakeEmailSender()
    s3_client = MemoryS3Client()
    from app.config import Settings

    storage = S3Storage(
        Settings(),
        client=s3_client,
        presign_client=s3_client,
    )
    app.dependency_overrides[get_email_sender] = lambda: sender
    app.dependency_overrides[get_storage] = lambda: storage
    with TestClient(app) as client:
        yield client, sender, storage, s3_client
    app.dependency_overrides.clear()


def register_user(client: TestClient) -> tuple[int, str]:
    email = f"applicant-{uuid4()}@example.com"
    registered = client.post(
        "/api/auth/register",
        json={"email": email, "password": "Password123!", "role": "regular"},
    )
    assert registered.status_code == 201
    login = client.post("/api/auth/login", json={"email": email, "password": "Password123!"})
    assert login.status_code == 200
    return registered.json()["user"]["id"], login.json()["token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def request_verification(client: TestClient, token: str) -> str:
    response = client.post("/api/chefs/me/email-verification", headers=auth_headers(token))
    assert response.status_code == 202
    return response.json()["message"]


def token_from_email(message: TransactionalEmail) -> str:
    link_line = next(line for line in message.text_body.splitlines() if "/verify-email?token=" in line)
    return parse_qs(urlparse(link_line).query)["token"][0]


def test_issue_and_consume_email_verification_token(onboarding_client) -> None:
    client, sender, _, _ = onboarding_client
    user_id, session_token = register_user(client)

    assert request_verification(client, session_token) == "Verification email sent"
    assert len(sender.messages) == 1
    verification_token = token_from_email(sender.messages[0])
    with SessionLocal() as db:
        stored = db.query(EmailVerificationToken).filter_by(user_id=user_id).one()
        assert stored.token_hash == token_digest(verification_token)
        assert stored.token_hash != verification_token
        expires_at = stored.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        assert expires_at > datetime.now(timezone.utc)

    verified = client.get("/api/auth/verify-email", params={"token": verification_token})
    assert verified.status_code == 200
    assert verified.json()["email_verified"] is True
    assert verified.json()["role"] == "regular"

    status_response = client.get("/api/chefs/me/status", headers=auth_headers(session_token))
    assert status_response.json() == {
        "email_verified": True,
        "application_status": "email_verified",
        "role": "regular",
    }
    with SessionLocal() as db:
        user = db.query(User).filter_by(id=user_id).one()
        stored = db.query(EmailVerificationToken).filter_by(user_id=user_id).one()
        assert user.email_verified is True
        assert user.role == "regular"
        assert stored.consumed_at is not None


@pytest.mark.parametrize(
    "request_target",
    [
        "/api/auth/verify-email?token={token}",
        "/api/auth/verify-email/?token={token}",
        "/api/auth/verify-email////?token={token}",
    ],
)
def test_verification_access_log_omits_query_string(request_target: str) -> None:
    synthetic_token = "synthetic-bearer-token-must-not-appear-in-logs"
    record = logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg='%s - "%s %s HTTP/%s" %d',
        args=(
            "127.0.0.1:1234",
            "GET",
            request_target.format(token=synthetic_token),
            "1.1",
            200,
        ),
        exc_info=None,
    )

    assert logging.getLogger("uvicorn.access").filter(record)
    logged_request = record.getMessage()
    assert "/api/auth/verify-email HTTP/1.1" in logged_request
    assert synthetic_token not in logged_request
    assert "?token=" not in logged_request


@pytest.mark.parametrize(
    ("method", "request_target"),
    [
        ("GET", "/api/auth/verify-email-extra?token={token}"),
        ("GET", "/api/auth/verify-email/child?token={token}"),
        ("POST", "/api/auth/verify-email/?token={token}"),
    ],
)
def test_verification_access_log_filter_leaves_unrelated_requests_unchanged(
    method: str, request_target: str
) -> None:
    synthetic_token = "synthetic-unrelated-request-token"
    full_target = request_target.format(token=synthetic_token)
    record = logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg='%s - "%s %s HTTP/%s" %d',
        args=("127.0.0.1:1234", method, full_target, "1.1", 200),
        exc_info=None,
    )

    assert logging.getLogger("uvicorn.access").filter(record)
    assert record.args[2] == full_target
    assert synthetic_token in record.getMessage()


def test_expired_and_reused_verification_tokens_are_rejected(onboarding_client) -> None:
    client, sender, _, _ = onboarding_client
    user_id, session_token = register_user(client)
    request_verification(client, session_token)
    expired_token = token_from_email(sender.messages[-1])

    with SessionLocal() as db:
        record = db.query(EmailVerificationToken).filter_by(user_id=user_id).one()
        record.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()
    assert client.get("/api/auth/verify-email", params={"token": expired_token}).status_code == 400

    request_verification(client, session_token)
    fresh_token = token_from_email(sender.messages[-1])
    assert client.get("/api/auth/verify-email", params={"token": fresh_token}).status_code == 200
    assert client.get("/api/auth/verify-email", params={"token": fresh_token}).status_code == 400


def test_unverified_user_cannot_upload_certificate(onboarding_client) -> None:
    client, _, _, s3_client = onboarding_client
    user_id, session_token = register_user(client)

    response = client.post(
        "/api/chefs/certificate",
        headers=auth_headers(session_token),
        files={"certificate": ("credential.pdf", VALID_PDF, "application/pdf")},
    )
    assert response.status_code == 403
    assert not s3_client.objects
    with SessionLocal() as db:
        assert db.query(ChefVerification).filter_by(user_id=user_id).count() == 0


def test_chef_application_stays_pending_without_promoting_regular_user(onboarding_client) -> None:
    client, sender, _, s3_client = onboarding_client
    user_id, session_token = register_user(client)
    request_verification(client, session_token)
    verification_token = token_from_email(sender.messages[-1])
    assert client.get("/api/auth/verify-email", params={"token": verification_token}).status_code == 200

    response = client.post(
        "/api/chefs/certificate",
        headers=auth_headers(session_token),
        files={"certificate": ("credential.pdf", VALID_PDF, "application/pdf")},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "pending_review"
    assert len(s3_client.objects) == 1
    bucket, object_key = next(iter(s3_client.objects))
    assert bucket == StorageBucket.CHEF_CERTIFICATES.value

    with SessionLocal() as db:
        application = db.query(ChefVerification).filter_by(user_id=user_id).one()
        user = db.query(User).filter_by(id=user_id).one()
        assert application.status == "pending_review"
        assert application.certificate_ref == f"{bucket}/{object_key}"
        assert user.role == "regular"
        assert user.chef_status == "pending_review"

    # Admin approval and promotion to chef are owned by BE-003.
    status_response = client.get("/api/chefs/me/status", headers=auth_headers(session_token))
    assert status_response.json() == {
        "email_verified": True,
        "application_status": "pending_review",
        "role": "regular",
    }


def test_invalid_certificate_is_rejected_without_object_or_application(onboarding_client) -> None:
    client, sender, _, s3_client = onboarding_client
    user_id, session_token = register_user(client)
    request_verification(client, session_token)
    verification_token = token_from_email(sender.messages[-1])
    client.get("/api/auth/verify-email", params={"token": verification_token})

    response = client.post(
        "/api/chefs/certificate",
        headers=auth_headers(session_token),
        files={"certificate": ("credential.pdf", b"not a PDF", "application/pdf")},
    )
    assert response.status_code == 400
    assert not s3_client.objects
    with SessionLocal() as db:
        assert db.query(ChefVerification).filter_by(user_id=user_id).count() == 0


def test_oversized_certificate_is_rejected_by_api_without_partial_application(
    onboarding_client, monkeypatch: pytest.MonkeyPatch
) -> None:
    client, sender, storage, s3_client = onboarding_client
    user_id, session_token = register_user(client)
    request_verification(client, session_token)
    verification_token = token_from_email(sender.messages[-1])
    assert client.get("/api/auth/verify-email", params={"token": verification_token}).status_code == 200
    monkeypatch.setattr(
        storage,
        "_upload_policy",
        UploadPolicy(certificate_max_bytes=len(VALID_PDF) - 1),
    )

    response = client.post(
        "/api/chefs/certificate",
        headers=auth_headers(session_token),
        files={"certificate": ("credential.pdf", VALID_PDF, "application/pdf")},
    )

    assert response.status_code == 400
    assert "exceeds" in response.json()["detail"]
    assert not s3_client.objects
    assert "put" not in s3_client.calls
    with SessionLocal() as db:
        assert db.query(ChefVerification).filter_by(user_id=user_id).count() == 0
        user = db.query(User).filter_by(id=user_id).one()
        assert user.role == "regular"
        assert user.chef_status == "email_verified"


def test_duplicate_application_is_rejected_before_another_upload(onboarding_client) -> None:
    client, sender, _, s3_client = onboarding_client
    user_id, session_token = register_user(client)
    request_verification(client, session_token)
    verification_token = token_from_email(sender.messages[-1])
    client.get("/api/auth/verify-email", params={"token": verification_token})
    payload = {"certificate": ("credential.pdf", VALID_PDF, "application/pdf")}

    assert client.post("/api/chefs/certificate", headers=auth_headers(session_token), files=payload).status_code == 201
    upload_count = s3_client.calls.count("put")
    duplicate = client.post("/api/chefs/certificate", headers=auth_headers(session_token), files=payload)
    assert duplicate.status_code == 409
    assert s3_client.calls.count("put") == upload_count
    with SessionLocal() as db:
        assert db.query(ChefVerification).filter_by(user_id=user_id).count() == 1


def test_registration_payload_cannot_promote_role(onboarding_client) -> None:
    client, _, _, _ = onboarding_client
    for role in ("chef", "admin"):
        response = client.post(
            "/api/auth/register",
            json={"email": f"{role}-{uuid4()}@example.com", "password": "Password123!", "role": role},
        )
        assert response.status_code == 422


def test_database_failure_after_upload_removes_uploaded_object(onboarding_client, monkeypatch: pytest.MonkeyPatch) -> None:
    client, sender, _, s3_client = onboarding_client
    _, session_token = register_user(client)
    request_verification(client, session_token)
    verification_token = token_from_email(sender.messages[-1])
    assert client.get("/api/auth/verify-email", params={"token": verification_token}).status_code == 200

    def fail_commit(_self: Session) -> None:
        raise RuntimeError("simulated database failure")

    monkeypatch.setattr(Session, "commit", fail_commit)
    response = client.post(
        "/api/chefs/certificate",
        headers=auth_headers(session_token),
        files={"certificate": ("credential.pdf", VALID_PDF, "application/pdf")},
    )
    assert response.status_code == 500
    assert not s3_client.objects
    assert s3_client.calls[-2:] == ["put", "delete"]