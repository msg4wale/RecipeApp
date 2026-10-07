"""Shared query and projection contract for COMP-008 Admin decision evidence.

Decision-owning components persist their own source-of-truth state. Generic
COMP-008 decisions use ``admin_decisions``; API-003 chef reviews are projected
from ``ChefVerification`` and must not be copied into that table.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AdminDecision, ChefVerification

CHEF_REVIEW_SUBJECT = "chef_verification"
DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 500


def _normalize_datetime(value: datetime) -> datetime:
    """Represent timestamps consistently as UTC, treating naive values as UTC."""

    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class AdminAuditEntry:
    """Stable read shape shared by audit consumers.

    ``timestamp`` is the decision time. ``submitted_at`` and
    ``turnaround_seconds`` are populated for chef reviews so MET-004 can be
    computed from the source application's ``created_at`` and ``reviewed_at``.
    """

    subject_type: str
    subject_id: int
    actor_user_id: int
    timestamp: datetime
    outcome: str
    rationale: Optional[str]
    submitted_at: Optional[datetime] = None
    turnaround_seconds: Optional[float] = None


def map_chef_verification(verification: ChefVerification) -> Optional[AdminAuditEntry]:
    """Project a decided API-003 source record into the shared audit shape.

    Pending/unreviewed applications are not Admin decisions and are omitted.
    The persisted decision fields are referenced directly; no second decision
    record or copy is created.
    """

    if verification.reviewed_at is None or verification.reviewed_by_user_id is None:
        return None

    reviewed_at = _normalize_datetime(verification.reviewed_at)
    created_at = _normalize_datetime(verification.created_at)
    return AdminAuditEntry(
        subject_type=CHEF_REVIEW_SUBJECT,
        subject_id=verification.id,
        actor_user_id=verification.reviewed_by_user_id,
        timestamp=reviewed_at,
        outcome=verification.status,
        rationale=verification.rationale,
        submitted_at=created_at,
        turnaround_seconds=(reviewed_at - created_at).total_seconds(),
    )


def record_admin_decision(
    db: Session,
    *,
    subject_type: str,
    subject_id: int,
    actor_user_id: int,
    outcome: str,
    rationale: Optional[str],
) -> AdminDecision:
    """Stage a shared audit record in the caller's transaction.

    This helper intentionally flushes but never commits: decision state and
    its audit evidence must participate in the owning component's transaction.
    """

    decision = AdminDecision(
        subject_type=subject_type,
        subject_id=subject_id,
        actor_user_id=actor_user_id,
        outcome=outcome,
        rationale=rationale,
    )
    db.add(decision)
    db.flush()
    return decision


def query_admin_audit(
    db: Session,
    *,
    subject_type: Optional[str] = None,
    subject_id: Optional[int] = None,
    actor_user_id: Optional[int] = None,
    outcome: Optional[str] = None,
    limit: int = DEFAULT_PAGE_SIZE,
    offset: int = 0,
) -> list[AdminAuditEntry]:
    """Return a newest-first page across shared decisions and API-003 reviews.

    The API-003 projection reads directly from ChefVerification. Both sources
    use the same filters and result shape, so future COMP-008 consumers can
    query audit evidence without taking ownership of another component's
    decision fields.
    """

    if limit < 1 or limit > MAX_PAGE_SIZE:
        raise ValueError(f"limit must be between 1 and {MAX_PAGE_SIZE}")
    if offset < 0:
        raise ValueError("offset must be non-negative")

    page_end = offset + limit
    generic_stmt = select(AdminDecision).order_by(
        AdminDecision.created_at.desc(),
        AdminDecision.subject_type.desc(),
        AdminDecision.subject_id.desc(),
        AdminDecision.id.desc(),
    )
    if subject_type is not None:
        generic_stmt = generic_stmt.where(AdminDecision.subject_type == subject_type)
    if subject_id is not None:
        generic_stmt = generic_stmt.where(AdminDecision.subject_id == subject_id)
    if actor_user_id is not None:
        generic_stmt = generic_stmt.where(AdminDecision.actor_user_id == actor_user_id)
    if outcome is not None:
        generic_stmt = generic_stmt.where(AdminDecision.outcome == outcome)
    generic_decisions = db.scalars(generic_stmt.limit(page_end)).all()

    chef_reviews: list[ChefVerification] = []
    if subject_type is None or subject_type == CHEF_REVIEW_SUBJECT:
        chef_stmt = select(ChefVerification).where(
            ChefVerification.reviewed_at.is_not(None),
            ChefVerification.reviewed_by_user_id.is_not(None),
        )
        if subject_id is not None:
            chef_stmt = chef_stmt.where(ChefVerification.id == subject_id)
        if actor_user_id is not None:
            chef_stmt = chef_stmt.where(ChefVerification.reviewed_by_user_id == actor_user_id)
        if outcome is not None:
            chef_stmt = chef_stmt.where(ChefVerification.status == outcome)
        chef_reviews = db.scalars(
            chef_stmt.order_by(ChefVerification.reviewed_at.desc(), ChefVerification.id.desc()).limit(page_end)
        ).all()

    # Keep source identity private to the merge so the public audit entry
    # shape remains stable while ties across sources are deterministic.
    ranked_entries = [
        (
            AdminAuditEntry(
                subject_type=decision.subject_type,
                subject_id=decision.subject_id,
                actor_user_id=decision.actor_user_id,
                timestamp=_normalize_datetime(decision.created_at),
                outcome=decision.outcome,
                rationale=decision.rationale,
            ),
            1,  # Shared AdminDecision precedes a chef review for identical public keys.
            decision.id,
        )
        for decision in generic_decisions
    ]
    ranked_entries.extend(
        (entry, 0, verification.id)
        for verification in chef_reviews
        if (entry := map_chef_verification(verification)) is not None
    )
    ranked_entries.sort(
        key=lambda ranked: (
            ranked[0].timestamp,
            ranked[0].subject_type,
            ranked[0].subject_id,
            ranked[1],
            ranked[2],
        ),
        reverse=True,
    )
    return [entry for entry, _, _ in ranked_entries[offset:page_end]]
