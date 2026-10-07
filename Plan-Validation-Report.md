# Plan Validation Report

## Status
- Verdict: APPROVE
- Plan Reviewed: `Engineering-Plan.md` v1.1, requester-approved latest revision; BE-003 revalidation on 2026-10-04
- Last Updated: 2026-10-04
- Revalidation Scope: BE-003, prior loop-backs, notification behavior, OBS-004/MET-004/AN-004 evidence, dependencies, and cross-references.

## Summary

The latest BE-003 revision resolves the earlier REVISE findings. It explicitly treats the existing API-003 routes, model fields, storage/email abstractions, and tests as the baseline; narrows remaining work to the missing unauthenticated decision-POST assertion, supported-database competing-decision verification, and the OBS-004 evidence handoff; and prohibits broad reimplementation. Repository inspection confirms these are real incremental gaps rather than duplicated implementation.

The task's acceptance and verification criteria preserve the approved synchronous post-commit notification limitation while expressly retaining bounded SMTP attempts within one `SmtpEmailSender.send` call. OBS-004 is an explicit prerequisite to BE-003 closure. The task dependency declarations and dependency-matrix/cross-reference entries are consistent. No blocking codebase-fit or readiness issue remains.

## Per-Task Findings
| Task ID | Classification | Existing Reuse Target(s) | Duplication? | Recommendation | Severity |
|---|---|---|---|---|---|
| BE-003 | extend-existing | `backend/app/main.py`: `get_admin_user`, `list_pending_chef_verifications`, `decide_chef_verification`, `ChefVerificationDecisionRequest`; `backend/app/models.py`: `User`, `ChefVerification`; `backend/app/storage.py`: `S3Storage.generate_presigned_download_url`; `backend/app/email.py`: `TransactionalEmail`, `TransactionalEmailSender`, `SmtpEmailSender.send`; `backend/tests/test_admin_chef_verification.py` | No. The revision identifies existing behavior as reuse/regression baseline and limits remaining work to verification and the bounded OBS-004 handoff. | Preserve the current implementation; implement only the stated test additions and any narrowly demonstrated OBS-004 mapping gap. | None |

## Reuse Opportunities

- **API/RBAC/request validation:** Reuse the existing Admin dependency, handlers, and decision request model in `backend/app/main.py`. The existing handlers already provide both API-003 operations, server-side Admin authorization, pending-only decisions, and decision transitions.
- **Model and audit source evidence:** Reuse `ChefVerification.created_at`, `reviewed_at`, `reviewed_by_user_id`, `status`, and `rationale` in `backend/app/models.py`. These support AN-004's submission/decision timestamps and MET-004's elapsed turnaround without duplicate decision fields.
- **Private certificate storage:** Reuse the existing `S3Storage.generate_presigned_download_url` call path in `backend/app/storage.py`.
- **Email contract and semantics:** Reuse `TransactionalEmail` / `SmtpEmailSender` in `backend/app/email.py` and the existing sender dependency seam in `backend/app/main.py`; do not add a provider-specific route path or second email abstraction.
- **Regression tests:** Extend `backend/tests/test_admin_chef_verification.py`, which already covers queue authorization, non-Admin decision denial, private certificate links, approval/rejection, repeated decisions, rollback, and post-commit delivery failure.
- **Competing-decision test:** Use the plan's PostgreSQL 16 local test stack for the concurrency verification. The existing test module uses an in-memory SQLite default; it is useful for ordinary regression tests but alone does not establish PostgreSQL row-lock behavior.
- **Observability mapping:** OBS-004 is correctly scoped as the new shared audit/query contract; API-003 should map/reference the existing ChefVerification record rather than duplicate its decision fields or emit duplicate decision telemetry.

## Duplication Flags

- None for BE-003. The plan explicitly prohibits recreating or replacing existing API-003 routes, authorization, state transitions, model fields, storage/email abstractions, and already-covered tests.
- The planned OBS-004 shared audit capability is not an existing backend API/model implementation duplicated by BE-003. The BE-003 mapping uses existing ChefVerification evidence as its source.

## Interface / Acceptance Traceability

- BE-003's routes and source requirements trace to PRD US-003 / AC-006–007 / FR-013 / MET-004 / AN-004 and TDD COMP-001 / COMP-008 / API-003 / INT-002.
- **Unauthenticated decision POST:** ENG-AC-089 and Verification Requirements now explicitly require an unauthenticated `POST /api/admin/chef-verifications/{id}/decision` assertion, alongside the existing unauthenticated queue and non-Admin assertions. This is a real gap in `backend/tests/test_admin_chef_verification.py` and is properly scoped as a test addition, not route reimplementation.
- **Competing decisions:** ENG-AC-093 and Verification Requirements specify the single-winner invariant, losing-request conflict, no overwrite of outcome/reviewer/time/rationale, supported database execution, and a non-sleep-based test. This is incremental verification of the existing conditional update/transaction behavior, consistent with TDD §8.5–8.6.
- **OBS-004 / MET-004 / AN-004:** ENG-AC-097 identifies the existing source fields and their mapping. PRD AN-004 requires submission and decision timestamps; PRD MET-004 measures review turnaround; TDD COMP-008/API-003 and audit logging specify the Admin actor/time/outcome/rationale evidence. OBS-004's acceptance and verification criteria require the API-003 mapping to be queryable at IC-01. QA-011 remains the later verification of sample turnaround calculations; its Wave 3/IC-06 placement and dependency on BE-003, BE-007, BE-016, and OBS-004 are consistent with this handoff.
- **Notification behavior:** ENG-AC-094–096 and the technical constraints preserve successful `notification_status: sent`, commit-before-send, post-commit HTTP 503 with persisted decision, repeat-decision 409 without a second endpoint-level send, and rollback/no notification on pre-commit failure. They explicitly preserve up to three bounded in-call SMTP attempts for transient SMTP/OS errors and exclude only durable/background retry or recovery. This matches `decide_chef_verification` and `SmtpEmailSender.send`.

## Dependencies, Readiness, and Verification Coverage

- BE-003 explicitly depends on BE-002, INT-002-T, and OBS-004. Its conditional parallel-safety note requires all three to complete before BE-003 runs; OBS-004 explicitly requires the chef-review contract before BE-003 closes at IC-01. Same-wave placement does not override this dependency gate.
- Dependency/cross-reference entries agree: OBS-004 depends on DB-001 and blocks BE-003 / QA-011; BE-003 blocks QA-011; QA-011 depends on BE-003, BE-007, BE-016, and OBS-004. The coverage matrix identifies BE-003, OBS-004, and QA-011 for US-003/MET-004 and for AN-004 evidence. QA-011's later IC-06 calculation check is not a prerequisite to BE-003 closure; BE-003 verifies the IC-01 mapping and hands off the source evidence.
- The test additions and IC-01 mapping check are bounded, acceptance-linked, and verifiable. The existing focused regression tests are explicitly rerun rather than duplicated. No production code or tests were run as part of this read-only plan validation.

## Loop-Back Items for Engineering Lead

- None. The previous loop-backs—narrowing BE-003 to the actual delta, clarifying in-call SMTP versus durable retry, specifying ENG-AC-097 evidence, and making OBS-004 ordering explicit—are resolved in the reviewed revision.

## Non-Blocking Reuse Notes (for Software Engineer)

- Use PostgreSQL 16 from the local stack for the competing-decision integration test; keep the existing SQLite-based tests for focused non-concurrency regressions.
- At IC-01, verify that OBS-004 can query/map the persisted ChefVerification evidence. QA-011 at IC-06 performs the downstream sample MET-004/MET-005 calculation after its declared dependencies are available.
- Keep the direct synchronous send after commit. A post-commit delivery error still returns 503 without rolling back; a repeated decision still returns 409 and does not initiate a second endpoint-level send. Preserve the bounded SMTP attempts made within a single sender invocation.

## Open Questions

- None blocking this validation. The production email provider remains the separately tracked non-blocking OTQ-001 decision; local Mailpit verification remains applicable.
