from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.admin_audit import (
    CHEF_REVIEW_SUBJECT,
    map_chef_verification,
    query_admin_audit,
    record_admin_decision,
)
from app.models import AdminDecision, Base, ChefVerification, User


def _session() -> Session:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return Session(engine)


def _user(db: Session, *, email: str, role: str) -> User:
    user = User(
        email=email,
        display_name=role,
        password_hash="not-a-real-password-hash",
        role=role,
    )
    db.add(user)
    db.flush()
    return user


def test_query_projects_existing_chef_review_fields_and_turnaround() -> None:
    with _session() as db:
        applicant = _user(db, email="applicant@example.test", role="regular")
        admin = _user(db, email="admin@example.test", role="admin")
        submitted_at = datetime(2026, 10, 1, 12, tzinfo=timezone.utc)
        reviewed_at = submitted_at + timedelta(hours=6, minutes=30)
        verification = ChefVerification(
            user_id=applicant.id,
            certificate_ref="private/certificate.pdf",
            status="approved",
            reviewed_by_user_id=admin.id,
            reviewed_at=reviewed_at,
            rationale="Credential verified",
            created_at=submitted_at,
        )
        db.add(verification)
        db.flush()

        entries = query_admin_audit(db, subject_type=CHEF_REVIEW_SUBJECT)

        assert len(entries) == 1
        entry = entries[0]
        assert entry.subject_type == CHEF_REVIEW_SUBJECT
        assert entry.subject_id == verification.id
        assert entry.actor_user_id == admin.id
        assert entry.timestamp == reviewed_at
        assert entry.outcome == "approved"
        assert entry.rationale == "Credential verified"
        assert entry.submitted_at == submitted_at
        assert entry.turnaround_seconds == 6.5 * 60 * 60
        assert db.query(AdminDecision).count() == 0


def test_pending_chef_review_is_not_exposed_as_a_decision() -> None:
    with _session() as db:
        applicant = _user(db, email="pending@example.test", role="regular")
        db.add(
            ChefVerification(
                user_id=applicant.id,
                certificate_ref="private/pending.pdf",
                status="pending_review",
            )
        )
        db.flush()

        assert query_admin_audit(db, subject_type=CHEF_REVIEW_SUBJECT) == []


def test_shared_decisions_are_transaction_owned_and_queryable_with_filters() -> None:
    with _session() as db:
        admin = _user(db, email="shared-admin@example.test", role="admin")
        decision = record_admin_decision(
            db,
            subject_type="similarity_appeal",
            subject_id=42,
            actor_user_id=admin.id,
            outcome="denied",
            rationale="The recipes are substantially similar.",
        )

        assert decision.id is not None
        assert len(db.new) == 0
        assert db.in_transaction()
        entries = query_admin_audit(
            db,
            subject_type="similarity_appeal",
            subject_id=42,
            actor_user_id=admin.id,
            outcome="denied",
        )
        assert len(entries) == 1
        assert entries[0].actor_user_id == admin.id
        assert entries[0].outcome == "denied"
        assert entries[0].rationale == "The recipes are substantially similar."
        assert entries[0].submitted_at is None
        assert entries[0].turnaround_seconds is None


def test_chef_mapping_ignores_unreviewed_records() -> None:
    verification = ChefVerification(
        id=5,
        user_id=8,
        certificate_ref="private/unreviewed.pdf",
        status="pending_review",
        reviewed_by_user_id=None,
        reviewed_at=None,
        rationale=None,
        created_at=datetime(2026, 10, 1, tzinfo=timezone.utc),
    )

    assert map_chef_verification(verification) is None


def test_unfiltered_query_orders_mixed_source_timestamps_as_utc() -> None:
    with _session() as db:
        applicant = _user(db, email="mixed-applicant@example.test", role="regular")
        admin = _user(db, email="mixed-admin@example.test", role="admin")
        earlier = record_admin_decision(
            db,
            subject_type="similarity_appeal",
            subject_id=1,
            actor_user_id=admin.id,
            outcome="denied",
            rationale=None,
        )
        later = record_admin_decision(
            db,
            subject_type="content_report",
            subject_id=2,
            actor_user_id=admin.id,
            outcome="accepted",
            rationale=None,
        )
        chef_review = ChefVerification(
            user_id=applicant.id,
            certificate_ref="private/mixed.pdf",
            status="approved",
            reviewed_by_user_id=admin.id,
            rationale="Verified",
            created_at=datetime(2026, 10, 1, 10, 30),
        )
        db.add(chef_review)
        db.flush()

        # SQLite strips timezone metadata when persisting DateTime columns.
        # Assign values after flush to exercise the mixed values returned by
        # different database drivers in one merged query.
        earlier.created_at = datetime(2026, 10, 1, 12, tzinfo=timezone(timedelta(hours=2)))
        chef_review.reviewed_at = datetime(2026, 10, 1, 11)
        later.created_at = datetime(2026, 10, 1, 14, tzinfo=timezone(timedelta(hours=1)))

        entries = query_admin_audit(db)

        assert [entry.subject_type for entry in entries] == [
            "content_report",
            CHEF_REVIEW_SUBJECT,
            "similarity_appeal",
        ]
        assert [entry.timestamp for entry in entries] == [
            datetime(2026, 10, 1, 13, tzinfo=timezone.utc),
            datetime(2026, 10, 1, 11, tzinfo=timezone.utc),
            datetime(2026, 10, 1, 10, tzinfo=timezone.utc),
        ]
        assert all(entry.timestamp.utcoffset() == timedelta(0) for entry in entries)
        chef_entry = entries[1]
        assert chef_entry.submitted_at == datetime(2026, 10, 1, 10, 30, tzinfo=timezone.utc)
        assert chef_entry.turnaround_seconds == 30 * 60


def test_query_filters_apply_to_both_audit_sources_and_select_source_type() -> None:
    with _session() as db:
        applicant = _user(db, email="filter-applicant@example.test", role="regular")
        admin = _user(db, email="filter-admin@example.test", role="admin")
        chef_review = ChefVerification(
            user_id=applicant.id,
            certificate_ref="private/filtered.pdf",
            status="approved",
            reviewed_by_user_id=admin.id,
            reviewed_at=datetime(2026, 10, 1, 12, tzinfo=timezone.utc),
        )
        db.add(chef_review)
        decision = record_admin_decision(
            db,
            subject_type="similarity_appeal",
            subject_id=77,
            actor_user_id=admin.id,
            outcome="denied",
            rationale="Reviewed",
        )
        db.flush()

        matching_chef_review = query_admin_audit(
            db,
            subject_type=CHEF_REVIEW_SUBJECT,
            subject_id=chef_review.id,
            actor_user_id=admin.id,
            outcome="approved",
        )
        assert [entry.subject_type for entry in matching_chef_review] == [CHEF_REVIEW_SUBJECT]
        assert matching_chef_review[0].subject_id == chef_review.id
        assert query_admin_audit(db, subject_type=CHEF_REVIEW_SUBJECT, actor_user_id=applicant.id) == []
        assert [entry.subject_type for entry in query_admin_audit(db, subject_type="similarity_appeal")] == [
            "similarity_appeal"
        ]
        matching_decision = query_admin_audit(
            db,
            subject_type="similarity_appeal",
            subject_id=77,
            actor_user_id=admin.id,
            outcome="denied",
        )
        assert [entry.subject_id for entry in matching_decision] == [decision.subject_id]
        assert query_admin_audit(db, subject_type="similarity_appeal", actor_user_id=applicant.id) == []
        assert query_admin_audit(db, subject_type="unknown_source") == []


def test_query_paginates_globally_newest_first_and_validates_bounds() -> None:
    with _session() as db:
        applicant = _user(db, email="page-applicant@example.test", role="regular")
        admin = _user(db, email="page-admin@example.test", role="admin")
        oldest = record_admin_decision(
            db,
            subject_type="appeal",
            subject_id=1,
            actor_user_id=admin.id,
            outcome="denied",
            rationale=None,
        )
        middle = ChefVerification(
            user_id=applicant.id,
            certificate_ref="private/page.pdf",
            status="approved",
            reviewed_by_user_id=admin.id,
            reviewed_at=datetime(2026, 10, 1, 11),
            created_at=datetime(2026, 10, 1, 10),
        )
        newest = record_admin_decision(
            db,
            subject_type="appeal",
            subject_id=3,
            actor_user_id=admin.id,
            outcome="approved",
            rationale=None,
        )
        db.add(middle)
        db.flush()
        oldest.created_at = datetime(2026, 10, 1, 10, tzinfo=timezone.utc)
        middle.reviewed_at = datetime(2026, 10, 1, 11)
        newest.created_at = datetime(2026, 10, 1, 12, tzinfo=timezone.utc)

        all_entries = query_admin_audit(db)
        first_page = query_admin_audit(db, limit=2)
        second_page = query_admin_audit(db, limit=2, offset=1)

        assert [entry.subject_id for entry in all_entries] == [
            newest.subject_id,
            middle.id,
            oldest.subject_id,
        ]
        assert [entry.subject_id for entry in first_page] == [entry.subject_id for entry in all_entries[:2]]
        assert [entry.subject_id for entry in second_page] == [entry.subject_id for entry in all_entries[1:]]
        assert query_admin_audit(db, limit=1, offset=3) == []

        with pytest.raises(ValueError, match="limit"):
            query_admin_audit(db, limit=0)
        with pytest.raises(ValueError, match="limit"):
            query_admin_audit(db, limit=501)
        with pytest.raises(ValueError, match="offset"):
            query_admin_audit(db, offset=-1)


def test_query_pagination_matches_global_order_for_tied_generic_decisions() -> None:
    with _session() as db:
        admin = _user(db, email="tie-page-admin@example.test", role="admin")
        timestamp = datetime(2026, 10, 1, 12, tzinfo=timezone.utc)
        decisions = [
            record_admin_decision(
                db,
                subject_type="appeal",
                subject_id=10,
                actor_user_id=admin.id,
                outcome="denied",
                rationale=None,
            ),
            record_admin_decision(
                db,
                subject_type="appeal",
                subject_id=30,
                actor_user_id=admin.id,
                outcome="denied",
                rationale=None,
            ),
            record_admin_decision(
                db,
                subject_type="appeal",
                subject_id=20,
                actor_user_id=admin.id,
                outcome="denied",
                rationale=None,
            ),
        ]
        for decision in decisions:
            decision.created_at = timestamp

        unpaginated = query_admin_audit(db)
        paginated = [
            entry
            for offset in range(len(unpaginated))
            for entry in query_admin_audit(db, limit=1, offset=offset)
        ]

        expected_subject_ids = [30, 20, 10]
        id_desc_subject_ids = [
            decision.subject_id for decision in sorted(decisions, key=lambda decision: decision.id, reverse=True)
        ]
        assert id_desc_subject_ids != expected_subject_ids
        assert [entry.subject_id for entry in unpaginated] == expected_subject_ids
        assert [entry.subject_id for entry in paginated] == [entry.subject_id for entry in unpaginated]


def test_query_pagination_is_deterministic_for_identical_public_keys_across_sources() -> None:
    with _session() as db:
        applicant = _user(db, email="same-key-applicant@example.test", role="regular")
        admin = _user(db, email="same-key-admin@example.test", role="admin")
        timestamp = datetime(2026, 10, 1, 12, tzinfo=timezone.utc)
        chef_review = ChefVerification(
            user_id=applicant.id,
            certificate_ref="private/same-key.pdf",
            status="approved",
            reviewed_by_user_id=admin.id,
            reviewed_at=timestamp,
            rationale="Chef review",
        )
        db.add(chef_review)
        db.flush()

        decisions = [
            record_admin_decision(
                db,
                subject_type=CHEF_REVIEW_SUBJECT,
                subject_id=chef_review.id,
                actor_user_id=admin.id,
                outcome=f"generic-{index}",
                rationale=None,
            )
            for index in range(3)
        ]
        for decision in decisions:
            decision.created_at = timestamp

        full_order = query_admin_audit(db)
        paginated_order = [
            entry
            for offset in range(len(full_order))
            for entry in query_admin_audit(db, limit=1, offset=offset)
        ]

        assert [entry.outcome for entry in full_order] == [
            "generic-2",
            "generic-1",
            "generic-0",
            "approved",
        ]
        assert [entry.outcome for entry in paginated_order] == [
            entry.outcome for entry in full_order
        ]
