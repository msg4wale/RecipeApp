# Decisions Log

## DEC-059
- Question: What follow-up is required for the blocked BE-003 QA verdict?
- Answer: Re-run the exact focused pytest suite from the current checkout, capture collection and full execution evidence, validate the Mailpit integration when reachable, and revise QA-Report.md so BE-002 and BE-003 verdicts are unambiguous. Do not classify the prior mismatched test result as a product defect without reproducible evidence.
- Decided by: Requester
- Affected IDs: QA-Report.md, BE-003, INT-002, release gate

## DEC-060
- Question: What is the result of the QA rework?
- Answer: QA-Report.md now clearly separates historical BE-002 PASS from current BE-003 BLOCKED. No product defect is confirmed, but pytest collection/execution and Mailpit reachability could not be run or probed in this environment, so BE-003 cannot pass QA.
- Decided by: QA Engineer
- Affected IDs: QA-Report.md, BE-003, INT-002, release gate

## DEC-061
- Question: What is the status of the Engineering Plan after BE-003 traceability repair?
- Answer: Engineering-Plan.md now contains an issue-ready BE-003 task and ENG-AC-089–097, including authorization, audit, notification, rollback, idempotency, concurrency, and Mailpit verification. Because an approved plan was modified, requester approval and Plan Architect revalidation are required before downstream progression.
- Decided by: Engineering Lead
- Affected IDs: Engineering-Plan.md, BE-003, Plan-Validation-Report.md

## DEC-062
- Question: Does the reported running Mailpit instance clear the BE-003 QA blocker?
- Answer: No. The verification attempt could not independently execute network or pytest commands. Delegated evidence reported HTTP 8025 availability but SMTP refusal and test results inconsistent with the checked-out collection. Mailpit reachability, focused-suite results, and integration delivery remain unverified.
- Decided by: QA Engineer
- Affected IDs: QA-Report.md, BE-003, INT-002, release gate

## DEC-001
- Question: What is the entry point for this task?
- Answer: Fresh idea — requester described a social recipe app with chef sharing, social
  engagement (like/comment/follow), and an AI agent conversational feature about recipes. No
  prior artifacts exist.
- Decided by: Coordinator (inferred from requester message; repo had no .workteam state or PRD/TDD)
- Affected IDs: Stage 1 (idea.md)

## DEC-002
- Question: Is "chef" a distinct role vs. any user can publish recipes?
- Answer: Chef is a distinct verified/authenticated account type; only chefs can post recipes.
  Other users can follow, like, and comment.
- Decided by: Requester
- Affected IDs: idea.md (Roles & Permissions, Business Rules, FR)

## DEC-003
- Question: What is the AI agent scope boundary?
- Answer: General cooking assistant and nutritionist (not strictly limited to the single recipe
  being viewed).
- Decided by: Requester
- Affected IDs: idea.md (Core Features, FR, NFR)

## DEC-004
- Question: Target platform(s) for MVP?
- Answer: Web only.
- Decided by: Requester
- Affected IDs: idea.md (Constraints, MVP Scope)

## DEC-005
- Question: Monetization/business model?
- Answer: Free app; ads for monetization.
- Decided by: Requester
- Affected IDs: idea.md (Business Model)

## DEC-006
- Question: Food-safety/liability handling for AI advice?
- Answer: Add a disclaimer and AI-disclosure notice on every AI output/recommendation.
- Decided by: Requester
- Affected IDs: idea.md (Risks, NFR, Business Rules)

## DEC-007
- Question: Target market/region and compliance requirements?
- Answer: Global target market; ignore compliance requirements (e.g., GDPR) for MVP.
- Decided by: Requester
- Affected IDs: idea.md (Constraints, Assumptions)

## DEC-008
- Question: Success metrics/targets?
- Answer: 100 active users in Q1 post-launch; at least 1000 recipes shared.
- Decided by: Requester
- Affected IDs: idea.md (Success Metrics)

## DEC-009
- Question: AI conversation history retention policy?
- Answer: Conversation history retained 3 days; users can bookmark specific AI responses for
  indefinite future access.
- Decided by: Requester
- Affected IDs: idea.md (Business Data Needs, FR, NFR)

## DEC-010
- Question: LLM/AI provider choice for the AI agent?
- Answer: Local LLM Studio with Qwen3.8-27B model (self-hosted/local inference, not a third-party
  cloud LLM API).
- Decided by: Requester
- Affected IDs: idea.md (External Integrations, Constraints, Assumptions)

## DEC-011
- Question: Chef verification mechanism?
- Answer: Email verification plus certificate upload (e.g., culinary credential/certification
  document) as part of chef onboarding.
- Decided by: Requester
- Affected IDs: idea.md (Roles & Permissions, Business Rules, FR)

## DEC-012
- Question: Plagiarism/recipe-similarity policy?
- Answer: Zero-plagiarism policy. Automated recipe similarity match check runs before final
  publish/commit. If similarity match > 95%, the chef is prompted to review the matched existing
  recipe and provide a comment describing what makes their recipe different. Recipes with
  differences in method, ingredients, steps, or ingredient combination are auto-accepted (i.e.,
  the >95% block/review only triggers when those differentiators are not detected).
- Decided by: Requester
- Affected IDs: idea.md (Business Rules, FR, Edge Cases, Business Data Needs)

## DEC-013
- Question: Chef credential review workflow?
- Answer: Admin manually reviews and approves upon certificate upload (before chef/publishing
  privileges are granted).
- Decided by: Requester
- Affected IDs: idea.md (Roles & Permissions, Business Rules, FR)

## DEC-014
- Question: Plagiarism dispute/appeal path?
- Answer: Manual review and approval by Admin (when a chef disputes a similarity-match rejection).
- Decided by: Requester
- Affected IDs: idea.md (Business Rules, FR, Edge Cases)

## DEC-015
- Question: Cold-start chef recruitment strategy?
- Answer: Self-registration on the app (no curated/invite-only recruitment for MVP).
- Decided by: Requester
- Affected IDs: idea.md (Assumptions, Risks, MVP Scope)

## DEC-016
- Question: Feed ranking logic?
- Answer: Rank by most liked and most commented (engagement-based ranking).
- Decided by: Requester
- Affected IDs: idea.md (Core Features, FR, Business Rules)

## DEC-017
- Question: Approve idea.md and advance to Stage 2 (Product Manager)?
- Answer: Approved.
- Decided by: Requester
- Affected IDs: Stage 1 (idea.md) — approved; Stage 2 (PRD.md) — dispatched

## DEC-018
- Question: Confirm "Active User" definition (MET-001)?
- Answer: Confirmed as PM-proposed: Monthly Active User = performs ≥1 of: view/like/comment/
  publish recipe, follow, or send an AI message.
- Decided by: Requester
- Affected IDs: PRD.md (Success Measures, MET-001)

## DEC-019
- Question: Confirm AI response time NFR (NFR-001)?
- Answer: 30s (95th percentile) / 45s (99th percentile) — requester adjusted from PM's proposed
  8s/15s, given local LLM constraints.
- Decided by: Requester
- Affected IDs: PRD.md (NFR-001)

## DEC-020
- Question: Confirm accessibility conformance level (NFR-005)?
- Answer: Confirmed as PM-proposed: WCAG 2.1 Level AA for core web flows.
- Decided by: Requester
- Affected IDs: PRD.md (NFR-005)

## DEC-021
- Question: Confirm budget/timeline (CON-001)?
- Answer: $200 budget / 5 workman-hours.
- Decided by: Requester
- Affected IDs: PRD.md (Constraints, CON-001)

## DEC-022
- Question: Approve full-scope budget/timeline estimate (~$30K-$60K, ~12-16 weeks, ~600-800
  person-hours) as confirmed CON-001?
- Answer: Approved — full-scope estimate confirmed as the budget/timeline constraint. Phased/
  reduced alternative not selected.
- Decided by: Requester
- Affected IDs: PRD.md (CON-001, RISK-009)

## DEC-023
- Question: Approve PRD.md and advance to Stage 3 (Solution Architect)?
- Answer: Approved.
- Decided by: Requester
- Affected IDs: Stage 2 (PRD.md) — approved; Stage 3 (TDD.md) — dispatched

## DEC-024
- Question: Confirm AI stack (LLM runtime + model) and backend stack?
- Answer: AI stack = local Ollama + qwen2.5-coder:14b model (replacing LM Studio/Qwen3.x
  proposal). Backend stack = Python/FastAPI (confirmed, replacing NestJS alternative).
- Decided by: Requester
- Affected IDs: TDD.md (AI integration design, tech stack, ADRs)

## DEC-025
- Question: Deployment/environment focus for MVP build and testing?
- Answer: MVP will be developed and extensively tested on a local dev workstation. Tech stack
  proposal should prioritize local-buildable/testable services — storage, DB, Docker/containers,
  etc. must all be installable and runnable locally. A separate production stack recommendation
  should be provided as a secondary/future consideration.
- Decided by: Requester
- Affected IDs: TDD.md (Deployment/Runtime Topology, Tech Stack section)

## DEC-026
- Question: Chef account-deletion behavior (EC-004)?
- Answer: On chef account deletion, their recipes/content are archived under an anonymous user
  account, with content tagged/credited to the original chef (attribution retained despite
  account removal).
- Decided by: Requester
- Affected IDs: PRD.md (EC-004), TDD.md (data model/retention design)

## DEC-027
- Question: AI-unavailable fallback UX behavior?
- Answer: Display a "service temporarily unavailable" message when the local LLM/AI service is
  unreachable or fails.
- Decided by: Requester
- Affected IDs: PRD.md, TDD.md (AI integration reliability/fallback design)

## DEC-028
- Question: Exact feed-ranking weights (likes vs. comments)?
- Answer: Requester asked Solution Architect/PM to recommend a specific weighting formula.
- Decided by: Requester (delegated recommendation to workteam)
- Affected IDs: PRD.md (BR-008), TDD.md (feed ranking design)

## DEC-029
- Question: Approve TDD.md (including proposed feed-ranking formula) and advance to Stage 4
  (Engineering Lead)?
- Answer: Approved.
- Decided by: Requester
- Affected IDs: Stage 3 (TDD.md) — approved; Stage 4 (Engineering-Plan.md) — dispatched

## DEC-030
- Question: Approve Engineering-Plan.md and proceed to Stage 5 (Plan Architect / plan-validation)?
- Answer: Approved.
- Decided by: Requester
- Affected IDs: Stage 4 (Engineering-Plan.md) — approved; Stage 5 (Plan-Validation-Report.md) — dispatched

## DEC-031
- Question: Approve Plan-Validation-Report.md and proceed to Stage 6 (Software Engineer / implementation)?
- Answer: Approved.
- Decided by: Requester
- Affected IDs: Stage 5 (Plan-Validation-Report.md) — approved; Stage 6 (software-engineer) — dispatched

## DEC-032
- Question: Approve the BE-002 implementation handoff (chef application flow) and proceed to Code Review?
- Answer: Approved.
- Decided by: Requester
- Affected IDs: BE-002 — implementation approved; Stage 7 (code-reviewer) — dispatched

## DEC-033
- Question: Code Reviewer verdict for BE-002?
- Answer: APPROVE; no high-confidence correctness, security, or logic issues found. Reviewer notes no patch diff was available in the current working tree; review evaluated the specified test changes and production paths.
- Decided by: Code Reviewer
- Affected IDs: BE-002; Stage 7 — awaiting requester checkpoint; Stage 8 (QA) remains gated

## DEC-034
- Question: Approve Code Review verdict for BE-002 and proceed to QA?
- Answer: Approved.
- Decided by: Requester
- Affected IDs: Stage 7 (code-reviewer) — approved; BE-002 — in QA; Stage 8 (qa-engineer) — dispatched

## DEC-035
- Question: QA verdict for BE-002?
- Answer: FAIL. DEF-001: verification token is passed in query string and default Uvicorn access logging records the request path. ENG-AC-006 oversized-upload HTTP/no-partial-state path is unverified. Pending-Chef role contract differs between PRD/TDD and implementation. Mailpit/MinIO integration tests skipped; focused test result was not independently rerun during QA.
- Decided by: QA Engineer
- Affected IDs: QA-Report.md; BE-002; QA-FAIL-BE-002 rework loop opened, awaiting requester checkpoint

## DEC-036
- Question: What is the pending-Chef account role contract?
- Answer: During application/review the applicant remains a regular user with pending chef-application status. Once the application is approved, the role is upgraded from user to chef.
- Decided by: Requester
- Affected IDs: PRD US-001; TDD API-002; BE-002; BE-003 approval transition; QA-Report.md

## DEC-037
- Question: Route QA-FAIL findings for rework?
- Answer: Proceed. Software Engineer to address DEF-001, add ENG-AC-006 oversized-upload API/no-partial-state evidence, apply clarified role contract, and validate integration checks as services permit.
- Decided by: Requester
- Affected IDs: QA-FAIL-BE-002; BE-002; Code Review and QA rerun required after changes

## DEC-038
- Question: BE-002 QA-FAIL rework handoff status?
- Answer: Implemented access-log query redaction, synthetic-token regression coverage, oversized upload API rejection/no-persistence coverage, and pending applicant role/status assertions. Focused tests: 39 passed, 2 skipped, 3 warnings. Live Mailpit/MinIO setup blocked because Docker registry denied `minio/mc:latest`.
- Decided by: Software Engineer / Coordinator verification
- Affected IDs: BE-002; QA-FAIL-BE-002; implementation handoff awaiting requester checkpoint before Code Review

## DEC-039
- Question: Replace MinIO bucket initializer after `minio/mc:latest` registry pull denial.
- Answer: Implemented an idempotent Python initializer using the backend's boto3 dependency and image; creates both buckets and reapplies the recipe-media public-read policy. Unit and Compose validation pass. Runtime verification blocked because `minio/minio:latest` server image also receives pull access denied.
- Decided by: Coordinator, per requester instruction
- Affected IDs: INT-003-T; docker-compose.yml; backend/app/minio_init.py; backend/tests/test_minio_init.py

## DEC-040
- Question: Replace MinIO with LocalStack S3 for local object storage?
- Answer: Yes. Requester confirmed LocalStack must be configured with `LOCALSTACK_AUTH_TOKEN` supplied privately in ignored `.env`; do not share or commit the token. Local runtime uses LocalStack S3 on port 4566, persistent LocalStack data, and the same boto3 S3 API/bucket behavior. LocalStack is local development/test infrastructure; production deployment remains separate.
- Decided by: Requester
- Affected IDs: INT-003-T; docker-compose.yml; .env.example; backend/app/config.py; backend/app/storage.py; backend/app/s3_init.py; backend/tests/test_storage.py; README.md

## DEC-041
- Question: LocalStack S3 runtime validation after requester configured the auth token?
- Answer: Compose validated; LocalStack healthy with S3 running; `s3-init` completed successfully; live upload/download/delete round-trip passed. Token was never displayed or recorded.
- Decided by: Coordinator verification
- Affected IDs: INT-003-T — complete; LocalStack Compose runtime

## DEC-042
- Question: Approve BE-002 QA-FAIL rework handoff and proceed to Code Review?
- Answer: Approved. Requester confirmed MinIO has been replaced by LocalStack and LocalStack is running; prior live S3 runtime validation is recorded in DEC-041.
- Decided by: Requester
- Affected IDs: BE-002 — implementation approved; Stage 7 (code-reviewer) — dispatched; QA-FAIL-BE-002

## DEC-043
- Question: Code Review verdict for BE-002 QA-FAIL rework?
- Answer: CHANGES REQUIRED. Verification access-log filter misses `/api/auth/verify-email/?token=...`, whose slash redirect can log the bearer token. Add coverage and redact both route forms. Oversized-upload API/no-partial-state evidence and DEC-036 pending role behavior pass review.
- Decided by: Code Reviewer
- Affected IDs: BE-002; DEF-001; review rework loop opened; awaiting requester checkpoint

## DEC-044
- Question: Route Code Review finding DEC-043 for fix and regression test?
- Answer: Yes. Requester reports Mailpit is working; run live Mailpit integration during rework verification.
- Decided by: Requester
- Affected IDs: BE-002; DEF-001; INT-002-T; QA-FAIL-BE-002

## DEC-045
- Question: BE-002 DEC-043 review rework verification status?
- Answer: Exact and trailing-slash verification URLs redact query tokens; regression tests cover route variants and non-target boundaries. Focused suite: 44 passed, 2 skipped, 3 warnings. Mailpit integration: 1 passed. LocalStack S3 integration: 1 passed. Mailpit and LocalStack healthy.
- Decided by: Coordinator verification
- Affected IDs: BE-002; DEF-001; INT-002-T complete; INT-003-T validated; implementation handoff awaiting requester approval before Code Review

## DEC-046
- Question: Approve the BE-002 review-rework handoff and proceed to Code Review?
- Answer: Approved.
- Decided by: Requester
- Affected IDs: BE-002; Stage 6 approved; Stage 7 (code-reviewer) dispatched; QA-FAIL-BE-002

## DEC-047
- Question: Code Review verdict for BE-002 DEC-043 remediation?
- Answer: APPROVE; no high-confidence findings. Reviewer confirmed exact and trailing/repeated slash token-query redaction, correct access logger test, unrelated request boundaries, oversized-upload no-partial-state, and DEC-036 role behavior. Focused suite, Mailpit, and LocalStack evidence was reviewed.
- Decided by: Code Reviewer
- Affected IDs: BE-002; Stage 7 — awaiting requester checkpoint; QA-FAIL-BE-002 awaits QA rerun

## DEC-048
- Question: Approve Code Review verdict and proceed to QA rerun?
- Answer: Approved.
- Decided by: Requester
- Affected IDs: Stage 7 (code-reviewer) — approved; BE-002 — in QA; Stage 8 (qa-engineer) — dispatched

## DEC-049
- Question: QA rerun verdict for BE-002 after DEF-001 remediation?
- Answer: PASS. QA-Report.md updated in place. Evidence covers exact/trailing/repeated slash log redaction, oversized upload API rejection without partial object/application, DEC-036 role contract, focused suite (44 passed, 2 skipped), Mailpit integration (1 passed), and LocalStack S3 integration (1 passed). QA states execution results were Coordinator-provided, not independently rerun.
- Decided by: QA Engineer
- Affected IDs: BE-002; QA-Report.md; QA-FAIL-BE-002 pending requester approval

## DEC-050
- Question: Approve QA PASS and close BE-002?
- Answer: Approved. Close BE-002 QA and continue the approved engineering plan.
- Decided by: Requester
- Affected IDs: Stage 8 (qa-engineer) — approved; BE-002 — done; QA-FAIL-BE-002 closed; BE-003 dispatched as next dependency

## DEC-051
- Question: BE-003 admin Chef verification workflow implementation status?
- Answer: Implemented admin-only queue and approve/reject decision endpoints; approval upgrades regular applicant to chef, rejection preserves regular role; review actor/time/rationale persisted with migration; repeated decisions conflict. Focused suite initially exposed an order-dependent absolute-count assertion, changed to applicant-scoped check; final suite 23 passed, 3 warnings.
- Decided by: Software Engineer / Coordinator verification
- Affected IDs: BE-003; API-003; US-003; DEC-036; implementation handoff awaiting requester approval before Code Review

## DEC-052
- Question: Approve BE-003 implementation handoff and proceed to Code Review?
- Answer: Approved.
- Decided by: Requester
- Affected IDs: BE-003; Stage 6 approved; Stage 7 (code-reviewer) dispatched

## DEC-053
- Question: Code Review verdict for BE-003?
- Answer: CHANGES REQUIRED. Applicant notification for both approval/rejection missing; PRD US-003 AC-007 and TDD INT-002/ENG-AC-068 require decision notification. Add delivery via existing email abstraction, define failure behavior, and test both outcomes. Other role transition, authorization, audit, duplicate-decision checks accepted.
- Decided by: Code Reviewer
- Affected IDs: BE-003; REVIEW-CHANGES-BE-003 loop opened; awaiting requester checkpoint

## DEC-054
- Question: Route BE-003 Code Review finding DEC-053 for rework?
- Answer: Approved. Add applicant decision notifications for both approve/reject using existing email abstraction, define delivery failure semantics, and test each outcome.
- Decided by: Requester
- Affected IDs: BE-003; REVIEW-CHANGES-BE-003; Code Review must be repeated after fix

## DEC-055
- Question: BE-003 notification rework implementation status?
- Answer: Added approval/rejection email via existing sender after DB commit; EmailDeliveryError returns explicit 503 while decision/audit remain committed; repeat decision returns 409 without resend. Fake-sender tests cover both outcomes, delivery failures, persisted state, and retry behavior. Focused tests: 25 passed. Live Mailpit test skipped because service unavailable at localhost:8025; Docker daemon unavailable during check.
- Decided by: Software Engineer / Coordinator verification
- Affected IDs: BE-003; PRD US-003 AC-007; TDD INT-002; ENG-AC-068; handoff awaiting approval before Code Review

## DEC-056
- Question: Approve BE-003 notification rework handoff and proceed to Code Review?
- Answer: Approved.
- Decided by: Requester
- Affected IDs: BE-003; Stage 6 approved; Stage 7 (code-reviewer) dispatched; REVIEW-CHANGES-BE-003

## DEC-057
- Question: Code Review verdict for BE-003 notification rework?
- Answer: APPROVE WITH NON-BLOCKING COMMENTS. Notification implementation, post-commit failure behavior, idempotency, and tests accepted. Known at-most-once limitation: failed email delivery yields 503 after durable decision; repeated decision is 409 and does not resend. Live Mailpit integration unverified. Reviewer also notes Engineering-Plan traceability gap for BE-003/ENG-AC-068.
- Decided by: Code Reviewer
- Affected IDs: BE-003; Stage 7 awaiting requester checkpoint; Stage 8 QA remains gated; REVIEW-CHANGES-BE-003

## DEC-058
- Question: Approve BE-003 Code Review verdict (APPROVE WITH NON-BLOCKING COMMENTS) and proceed to QA?
- Answer: Approved.
- Decided by: Requester
- Affected IDs: Stage 7 (code-reviewer) — approved; BE-003 — in QA; Stage 8 (qa-engineer) — dispatched; REVIEW-CHANGES-BE-003

## DEC-059
- Question: QA rerun verdict for BE-003 notification rework?
- Answer: BLOCKED. QA assessed implementation/test assertions but could not trust pytest result because runner reported failing test names not present in inspected current file; live Mailpit unavailable (API empty, SMTP refused). No-outbox at-most-once limitation and missing task-level Engineering-Plan traceability documented. Needs reliable test execution and live Mailpit verification.
- Decided by: QA Engineer
- Affected IDs: BE-003; QA-Report.md; Stage 8 awaiting requester checkpoint; REVIEW-CHANGES-BE-003 remains open

## DEC-060
- Question: Is Mailpit responding now?
- Answer: Yes. Mailpit was already running, so no startup was needed. Docker Compose reported the `mailpit` service Up; `GET http://127.0.0.1:8025/api/v1/info` returned HTTP 200 with version/max-message metadata, and SMTP TCP port 1025 accepted connections. No other services were changed.
- Decided by: Coordinator verification
- Affected IDs: INT-002-T; BE-003; QA-Report.md

## DEC-063
- Question: What were the results of the requested October 4 pytest and Mailpit delivery rerun?
- Answer: No tests or connectivity probes executed: the delegated runner reported no subprocess access. No pytest exit status or delivery result is available. Inspection confirmed the Mailpit integration requires `RUN_MAILPIT_INTEGRATION=1`; without it the test skips. Current QA remains BLOCKED pending actual command output.
- Decided by: Coordinator
- Affected IDs: BE-003; QA-Report.md; INT-002-T; release gate

## DEC-064
- Question: QA verdict for BE-003 based on requester-provided captured pytest and Mailpit output?
- Answer: QA PASS, pending requester checkpoint approval. Evidence: 8 Admin verification nodes collected; focused suite 25 passed with 3 warnings; opted-in Mailpit delivery test 1 passed. The attachment does not include explicit numeric shell exit-code echoes. No blocking defect identified; accepted no-outbox limitation remains.
- Decided by: QA Engineer
- Affected IDs: BE-003; QA-Report.md; Stage 8; release gate

## DEC-065
- Question: Approve BE-003 QA PASS and revised Engineering Plan?
- Answer: Approved. BE-003 QA PASS is accepted on the supplied evidence. The revised Engineering Plan is approved for revalidation; Plan Architect must revalidate it before any downstream work.
- Decided by: Requester
- Affected IDs: BE-003; QA-Report.md; Engineering-Plan.md; Stage 4 approved; Stage 5 dispatched; REVIEW-CHANGES-BE-003 closed

## DEC-066
- Question: What is the result of Plan Architect revalidation of the revised Engineering Plan?
- Answer: REVISE. The BE-003 task overlaps APIs and tests already implemented. The Engineering Lead must narrow the task to remaining delta/reuse, disambiguate bounded inline SMTP retries from no durable retry, concretize ENG-AC-097 / OBS-004 / MET-004 / AN-004 evidence/readiness, and ensure missing unauthenticated decision and competing-decision verification is specified where required. No implementation may proceed until the plan is revised and passes revalidation.
- Decided by: Plan Architect
- Affected IDs: Engineering-Plan.md; Plan-Validation-Report.md; BE-003; PLAN-REVISE-BE-003

## DEC-067
- Question: Route the Plan Architect REVISE findings to the Engineering Lead?
- Answer: Approved. Revise the existing Engineering Plan in place; after the Lead returns it, obtain requester approval and re-run Plan Architect validation before implementation proceeds.
- Decided by: Requester
- Affected IDs: PLAN-REVISE-BE-003; Engineering-Plan.md; Stage 4 reactivated; Stage 5 revalidation required

## DEC-068
- Question: What changes did the Engineering Lead make to resolve the BE-003 plan-validation loop?
- Answer: BE-003 now treats existing API-003 routes, models, abstractions, notifications, and tests as baseline. Remaining work is narrowly scoped to explicit unauthenticated decision coverage, competing-decision verification, OBS-004 evidence mapping, and regression/integration closure. Existing synchronous post-commit 503/409 semantics and bounded in-call SMTP attempts are preserved; no durable retry/outbox is added. Plan awaits requester approval, then Plan Architect revalidation.
- Decided by: Engineering Lead
- Affected IDs: Engineering-Plan.md BE-003; ENG-AC-089–097; OBS-004; MET-004; AN-004

## DEC-069
- Question: Approve the Engineering Lead's revised Engineering Plan and proceed to Plan Architect revalidation?
- Answer: Approved. Revalidate the revised BE-003 task scope, reuse boundaries, notification semantics, OBS-004 evidence mapping, and verification/closure criteria.
- Decided by: Requester
- Affected IDs: Engineering-Plan.md BE-003; Stage 4 approved; Stage 5 dispatched; PLAN-REVISE-BE-003

## DEC-070
- Question: What is the Plan Architect verdict on the latest BE-003 plan revision?
- Answer: APPROVE. The plan avoids duplicating existing API/model/storage/email/tests, scopes remaining incremental verification and OBS-004/MET-004/AN-004 mapping, and preserves approved notification semantics. Non-blocking implementation note: the competing-decision test must run against PostgreSQL 16; SQLite alone does not establish PostgreSQL locking behavior.
- Decided by: Plan Architect
- Affected IDs: Engineering-Plan.md BE-003; Plan-Validation-Report.md; Stage 5 awaiting requester checkpoint; PLAN-REVISE-BE-003

## DEC-071
- Question: Approve the Plan Architect APPROVE verdict for the revised Engineering Plan?
- Answer: Approved. Stage 5 is complete. The incremental BE-003 task may proceed only after its declared OBS-004 prerequisite is confirmed complete; current task ledger does not evidence that prerequisite, so implementation remains blocked pending readiness confirmation.
- Decided by: Requester
- Affected IDs: Stage 5 approved; PLAN-REVISE-BE-003 closed; BE-003 incremental verification; OBS-004; Stage 6 blocked pending dependency

## DEC-072
- Question: Assign OBS-004 and complete its prerequisites?
- Answer: Assigned OBS-004 to Software Engineer. Its plan-listed prerequisite DB-001 is already complete. Implement the shared queryable Admin audit mechanism and consumer contract, mapping existing chef-review evidence without duplicating source fields; keep BE-003 follow-up downstream until OBS-004 is complete.
- Decided by: Requester
- Affected IDs: OBS-004; DB-001; BE-003; Stage 6 in-progress

## DEC-073
- Question: What is OBS-004 implementation handoff status?
- Answer: Shared audit model, migration, query/projection utility, and tests were implemented, but verification is untrusted/unverified and handoff is NOT READY for code review. Keep OBS-004 in progress; do not treat it as a completed BE-003 prerequisite pending reliable validation.
- Decided by: Software Engineer
- Affected IDs: OBS-004; ENG-AC-086; BE-003; Stage 6

## DEC-074
- Question: What correctness follow-up is required for OBS-004?
- Answer: Fix and test naive/aware datetime normalization for mixed SQLite/PostgreSQL audit sources; add mixed-source ordering/filter/pagination tests and verify migration lineage. The suspected source_type filter issue was inspected and is not a defect. Earlier delegated test and migration outputs remain unreliable/unverified.
- Decided by: Software Engineer
- Affected IDs: OBS-004; ENG-AC-086; backend/app/admin_audit.py; test_admin_audit.py; migration chain

## DEC-075
- Question: What is the status of the OBS-004 datetime/query correctness follow-up?
- Answer: UTC normalization, explicit source filtering, mixed-source ordering/filter/pagination tests, and migration lineage assertion were implemented. No pytest or Alembic command was executed because no terminal was available; results are unverified, and handoff is not ready for review. Keep OBS-004 blocked pending execution evidence.
- Decided by: Software Engineer
- Affected IDs: OBS-004; ENG-AC-086; test_admin_audit.py; test_db_schema.py; Stage 6

## DEC-076
- Question: Does the requester-provided verification output clear OBS-004's implementation handoff blocker?
- Answer: Yes for code-review readiness. Engineer reconciled collection and test output: 10 audit/schema tests passed; 31 related regressions passed; offline Alembic generated the full PostgreSQL chain through the new migration and COMMIT. Numeric shell exit codes are not echoed; migration was not applied to live PostgreSQL. OBS-004 handoff is ready for code review, pending requester approval.
- Decided by: Software Engineer
- Affected IDs: OBS-004; ENG-AC-086; Stage 6 awaiting requester checkpoint; Code Review next

## DEC-077
- Question: Is PostgreSQL running, based on requester-provided runtime output?
- Answer: `docker compose ps postgres` returned headers but no container row, so this Compose project's PostgreSQL container is not currently present/running. `pg_isready` is not installed on the host, so an external PostgreSQL instance cannot be ruled out. No migration was applied; the prior Alembic command generated SQL only.
- Decided by: Coordinator based on requester-provided output
- Affected IDs: OBS-004 migration; PostgreSQL runtime verification; Workteam-State

## DEC-078
- Question: Is the local PostgreSQL prerequisite now ready?
- Answer: Yes. Requester started the Compose PostgreSQL 16 service; container started, new persistent volume was created, and in-container `pg_isready` reports accepting connections. Migration is still not reported as applied.
- Decided by: Coordinator based on requester-provided output
- Affected IDs: OBS-004; DB-001; migration verification

## DEC-079
- Question: Why did the live OBS-004 migration fail?
- Answer: The host Alembic client reached PostgreSQL at localhost:5432, but PostgreSQL rejected password authentication for user `app`. `pg_isready` only established server readiness, not authentication. No migration was applied. Reconcile the local Alembic DATABASE_URL with the username/database/password used by the Compose-initialized Postgres instance; keep credentials private and preserve the volume.
- Decided by: Coordinator based on requester-provided traceback
- Affected IDs: OBS-004 migration verification; PostgreSQL local configuration

## DEC-080
- Question: What was the result of the requester-authorized local database configuration comparison and repair?
- Answer: Host Alembic from `backend/` loaded no `backend/.env`, and therefore used the hardcoded default URL. Compose uses root `.env`; its `DATABASE_URL` host is the Docker-only `postgres` name, so host Alembic needs `localhost`. A temporary URL assembled in memory from root `.env` credentials authenticated successfully. No secret was exposed, no config file or DB role was changed. `alembic upgrade head` exited 0 and applied five pending revisions; `alembic current` exited 0 and confirmed `20261004_add_admin_decisions (head)`. OBS-004 still awaits requester approval before Code Review.
- Decided by: Coordinator based on delegated safe local verification
- Affected IDs: OBS-004; PostgreSQL migration; host Alembic configuration

## DEC-081
- Question: Approve the OBS-004 implementation handoff and proceed to Code Review?
- Answer: Approved. Dispatch Code Reviewer for task-scoped review. Prior BE-003 review verdict does not satisfy this checkpoint.
- Decided by: Requester
- Affected IDs: OBS-004; Stage 6 approved; Stage 7 dispatched

## DEC-082
- Question: What is the OBS-004 Code Review verdict?
- Answer: CHANGES REQUIRED. The source queries truncate using `(timestamp, id)` tie-break ordering, but the merged page sorts using `(timestamp, subject_type, subject_id)`. With tied timestamps, source truncation may exclude rows that should precede returned rows in global ordering. Align source/final tie-breakers and add tied-timestamp pagination coverage. Reviewer assessed the listed code snapshot; no Git diff was available. No code changed. Await requester checkpoint before Software Engineer rework.
- Decided by: Code Reviewer
- Affected IDs: OBS-004; backend/app/admin_audit.py; backend/tests/test_admin_audit.py; REVIEW-CHANGES-OBS-004

## DEC-083
- Question: Route the OBS-004 Code Review CHANGES REQUIRED finding to Software Engineer?
- Answer: Approved. Rework only the source/global pagination tie-break inconsistency and add a deterministic tied-timestamp pagination regression test. Run the focused backend audit test. After handoff, obtain requester approval before re-dispatching Code Review.
- Decided by: Requester
- Affected IDs: OBS-004; backend/app/admin_audit.py; backend/tests/test_admin_audit.py; REVIEW-CHANGES-OBS-004

## DEC-084
- Question: What is the OBS-004 pagination rework handoff and verification status?
- Answer: Software Engineer aligned generic SQL ordering to `(created_at DESC, subject_type DESC, subject_id DESC)` and added deterministic equal-timestamp pagination coverage where row ID order differs from subject-ID order; test compares pages to the unpaginated order. Targeted command `../.venv/bin/python -m pytest -q tests/test_admin_audit.py` could not be executed by the available agent environment. No pass/fail result is claimed. Handoff awaits requester approval before Code Review re-dispatch.
- Decided by: Software Engineer / Coordinator verification attempt
- Affected IDs: OBS-004; backend/app/admin_audit.py; backend/tests/test_admin_audit.py; REVIEW-CHANGES-OBS-004

## DEC-085
- Question: Approve the OBS-004 pagination rework handoff and proceed to Code Review?
- Answer: Approved. Re-dispatch Code Reviewer to review the tie-break fix and tied-timestamp regression. Verification limitation remains: focused pytest could not be executed in the agent environment.
- Decided by: Requester
- Affected IDs: OBS-004; Stage 6 approved; Stage 7 dispatched; REVIEW-CHANGES-OBS-004

## DEC-086
- Question: What is the OBS-004 pagination re-review verdict?
- Answer: CHANGES REQUIRED. The DEC-082 ordering defect is fixed for timestamp ties with differing subject IDs, but multiple AdminDecision rows can share timestamp, subject_type, and subject_id because no uniqueness constraint exists. Current ordering is non-unique, so LIMIT/OFFSET pages may be unstable and omit/repeat records. Add a deterministic unique final tie-breaker consistently to source ordering and merged ordering, plus a test for records sharing the current complete sort key. Focused pytest was unavailable and no Git diff exists. Await requester checkpoint before rework.
- Decided by: Code Reviewer
- Affected IDs: OBS-004; backend/app/admin_audit.py; backend/tests/test_admin_audit.py; REVIEW-CHANGES-OBS-004

## DEC-087
- Question: Route the OBS-004 re-review CHANGES REQUIRED finding to Software Engineer?
- Answer: Approved. Add a unique deterministic final tie-breaker consistently across per-source retrieval and merged ordering, plus a regression test for distinct records sharing the current complete sort key. Attempt the focused audit test and report actual evidence. Requester checkpoint approval is required before Code Review re-dispatch.
- Decided by: Requester
- Affected IDs: OBS-004; backend/app/admin_audit.py; backend/tests/test_admin_audit.py; REVIEW-CHANGES-OBS-004

## DEC-088
- Question: What is the result of the DEC-087 OBS-004 implementation dispatch?
- Answer: BLOCKED — ENVIRONMENT. The Software Engineer inspected the issue and returned a concrete patch/test design but reported no file-edit or shell capability. No source/test files changed; pytest was not run. OBS-004 stays blocked and Code Review is not re-dispatched. Resume when an implementation-capable Software Engineer execution is available.
- Decided by: Coordinator based on Software Engineer handoff
- Affected IDs: OBS-004; backend/app/admin_audit.py; backend/tests/test_admin_audit.py; REVIEW-CHANGES-OBS-004

## DEC-089
- Question: What does the request to resume OBS-004 mean after the environment-blocked implementation attempt?
- Answer: Resume the already requester-approved DEC-087 Software Engineer rework; prior attempt made no code changes and is not complete. Retry implementation of unique deterministic ordering and fully-tied pagination regression, then run the targeted test if command execution is available. Preserve review/QA gates.
- Decided by: Requester direction / Coordinator
- Affected IDs: OBS-004; backend/app/admin_audit.py; backend/tests/test_admin_audit.py; REVIEW-CHANGES-OBS-004

## DEC-090
- Question: What was the result of resuming the approved OBS-004 pagination rework?
- Answer: BLOCKED again. The second Software Engineer dispatch reported no file-edit or shell capability. No files changed and targeted pytest was not run. OBS-004 remains blocked; keep the existing DEC-087 authorization and proposed design. Resume only when an implementation-capable Software Engineer execution is available; do not dispatch Code Review without completed code/test evidence.
- Decided by: Coordinator based on Software Engineer handoff
- Affected IDs: OBS-004; backend/app/admin_audit.py; backend/tests/test_admin_audit.py; REVIEW-CHANGES-OBS-004

## DEC-091
- Question: What does the request to continue and implement OBS-004 after prior agent blockers mean?
- Answer: Reattempt the already requester-approved DEC-087 Software Engineer implementation task. Do not mark complete without code change and focused test evidence. Preserve existing review/QA gates.
- Decided by: Requester direction / Coordinator
- Affected IDs: OBS-004; backend/app/admin_audit.py; backend/tests/test_admin_audit.py; REVIEW-CHANGES-OBS-004

## DEC-092
- Question: What is the result of the resumed OBS-004 pagination implementation?
- Answer: Implemented unique source ordering: AdminDecision uses `(created_at DESC, subject_type DESC, subject_id DESC, id DESC)`; ChefVerification uses `(reviewed_at DESC, id DESC)`. The merged results use a private deterministic source-rank/source-PK tie-break after the public keys, preserving AdminAuditEntry shape. Added regression coverage for multiple generic rows sharing timestamp/subject type/subject ID and a matching chef-review public key across paginated/unpaginated queries; prior differing-subject tie test remains. Focused pytest could not execute in the agent environment; no result is claimed. Await requester approval before Code Review re-dispatch.
- Decided by: Software Engineer / Coordinator verification
- Affected IDs: OBS-004; backend/app/admin_audit.py; backend/tests/test_admin_audit.py; REVIEW-CHANGES-OBS-004

## DEC-093
- Question: Does the requester instruction to continue through completion approve the OBS-004 implementation handoff checkpoint?
- Answer: Interpreted as approval to advance the completed implementation handoff to Code Review so the task can proceed autonomously. The requester directed completion rather than pausing at a checkpoint. The review must disclose that targeted pytest was unavailable; remaining stage checkpoints still apply unless explicitly superseded by the requester's instruction.
- Decided by: Coordinator, based on requester instruction 2026-10-05
- Affected IDs: OBS-004; Stage 6 approved; Stage 7 dispatched; REVIEW-CHANGES-OBS-004

## DEC-094
- Question: What is the OBS-004 pagination re-review verdict?
- Answer: APPROVE WITH NON-BLOCKING COMMENTS. No concrete code defects found. Source ordering and merged private source-rank/primary-key tie-breaks are deterministic and consistent; tests cover tied generic keys and identical public keys across sources. Reviewer noted focused tests had not yet run and no Git diff was available.
- Decided by: Code Reviewer
- Affected IDs: OBS-004; backend/app/admin_audit.py; backend/tests/test_admin_audit.py; Stage 7 awaiting requester checkpoint

## DEC-095
- Question: What verification followed the review comment requesting focused-test evidence, and may work continue autonomously?
- Answer: The focused audit suite was run from `backend`: `../.venv/bin/python -m pytest -q tests/test_admin_audit.py`; exit 0, 9 passed, no warnings. The requester directed the workteam to continue autonomously through task completion; accepted the non-blocking Code Review verdict and advanced to QA without another pause.
- Decided by: Coordinator based on actual command result and requester instruction
- Affected IDs: OBS-004; Stage 7 approved; Stage 8 dispatched; REVIEW-CHANGES-OBS-004

## DEC-096
- Question: What is the OBS-004 QA verdict, and is the task complete?
- Answer: QA PASS for the scoped shared audit mechanism/API-003 projection (ENG-AC-086, COMP-008, MET-004 evidence). QA-Report.md was updated in place, preserving historical BE-002/BE-003 records. The report identifies focused audit tests as 9 passed, exit 0, no warnings; prior audit/schema 10 and related regressions 31 are separate supplied evidence; prior PostgreSQL 16 migration/current-head is also supplied evidence, not rerun. Code Review found no code defects (APPROVE WITH NON-BLOCKING COMMENTS). No formal Git diff exists. Per requester's instruction to continue autonomously through completion, accept the QA verdict, mark Stage 8 approved, close REVIEW-CHANGES-OBS-004 and mark OBS-004 done. Downstream consumer integration and MET-004 business-day target semantics remain explicitly out of scope.
- Decided by: Coordinator under requester instruction to complete autonomously, based on QA Engineer handoff
- Affected IDs: OBS-004; QA-Report.md; Stage 8 approved; REVIEW-CHANGES-OBS-004 closed

## DEC-097
- Question: What work is authorized by the request to resume BE-003's outstanding IC-01 verification delta?
- Answer: Reopen BE-003 narrowly for the approved plan delta: add explicit unauthenticated decision POST assertion; implement and run competing approval/rejection verification on PostgreSQL 16 with exactly one winner and no losing overwrite of outcome/reviewer/time/rationale; query the persisted ChefVerification via OBS-004 and confirm no duplicate decision row; rerun focused regressions and opt-in Mailpit verification where available. Preserve existing API implementation and notification semantics. Prerequisites BE-002, INT-002-T, OBS-004 are complete. Report blockers rather than substituting SQLite for PostgreSQL concurrency verification.
- Decided by: Requester
- Affected IDs: BE-003; ENG-AC-089–097; IC-01; OBS-004; QA-Report.md

## DEC-098
- Question: What is the result of resuming BE-003's IC-01 verification delta?
- Answer: Implemented tests only: explicit unauthenticated decision POST, approval-to-OBS-004 projection of persisted ChefVerification fields with no duplicate AdminDecision, and PostgreSQL 16 gated competing-decision test. No production code changes. SQLite-focused API/onboarding/schema run reported 9 passed; audit suite reported 26 passed, 1 skipped, 4 deprecation warnings. Required PostgreSQL 16 concurrency and Mailpit tests were not run. Docker Compose startup attempt failed because the Docker daemon socket `/Users/araji/.docker/run/docker.sock` does not exist; PostgreSQL version and Mailpit availability could not be verified. No services, database data, migrations, credentials, or config were changed. Keep BE-003 blocked at IC-01 pending Docker Desktop/runtime availability; SQLite is not evidence for PostgreSQL concurrency. Continue the pending targeted tests when services are available.
- Decided by: Coordinator based on Software Engineer and verification runner outputs
- Affected IDs: BE-003; ENG-AC-089–097; IC-01; OBS-004; INT-002-T; QA-Report.md

## DEC-099
- Question: What did the follow-up runtime verification establish, and what action is next?
- Answer: Docker daemon remains unavailable (`~/.docker/run/docker.sock` missing), and ports 5432, 8025, 1025 are closed. No PostgreSQL concurrency or Mailpit test ran. Combined isolated SQLite-focused suite ran: 43 passed, 1 skipped (PostgreSQL-only test), 4 warnings; exit 0. No code/config/data changed. Under the requester's instruction to continue, attempt a non-destructive launch of Docker Desktop, then start only existing Compose postgres/mailpit and run the required tests.
- Decided by: Coordinator based on runtime verification output
- Affected IDs: BE-003; ENG-AC-089–097; IC-01; OBS-004; INT-002-T; QA-Report.md

## DEC-100
- Question: What is the result of resumed BE-003 IC-01 runtime verification?
- Answer: Docker Desktop launched; Engine 29.7.2. Existing Compose PostgreSQL and Mailpit services healthy. Actual PostgreSQL 16.15 competing-decision test: 1 passed, exit 0. Opted-in Mailpit inbox delivery test: 1 passed, exit 0. Isolated SQLite-focused API/onboarding/schema/audit/auth suite: 35 passed, 2 skipped, 3 deprecation warnings, exit 0. Earlier runner setup errors (venv path/PYTHONPATH) were corrected before these final runs. No migration, config/credential edit, role reset, or service/data deletion. Synthetic records created by the concurrency test were cleaned up. Code/test verification complete; repeat Code Review required before QA closes the delta.
- Decided by: Coordinator based on general-purpose runtime verification
- Affected IDs: BE-003; ENG-AC-089–097; IC-01; OBS-004; INT-002-T; REVIEW; QA-Report.md

## DEC-101
- Question: What is the Code Review verdict for the BE-003 IC-01 test-only delta?
- Answer: APPROVE. No actionable defects. Reviewer confirmed unauthenticated decision 401, PostgreSQL 16 single-winner concurrency/no-overwrite assertions, and OBS-004 projection without duplicate AdminDecision. Review relied on supplied execution results and current files; formal Git diff unavailable. Per requester instruction to complete the requested verification, Stage 7 accepted and QA dispatched.
- Decided by: Code Reviewer / Coordinator under requester instruction
- Affected IDs: BE-003; ENG-AC-089, ENG-AC-093, ENG-AC-097; Stage 7 approved; Stage 8 dispatched; QA-Report.md

## DEC-103
- Question: Which harness and framework version should the workteam use going forward?
- Answer: Continue the project in Claude Code on Agentic AI Workteam 1.0.0 (harness-agnostic release). The Copilot agent/skill files (pre-1.0 build) are removed; all approved deliverables, state, and decisions carry over unchanged. DEC-102 is referenced in Workteam-State.md but was never written to this log; it is left unfilled rather than reconstructed.
- Decided by: Requester (Ade), 2026-10-07
- Affected IDs: .claude/, CLAUDE.md, Constitution.md, .workteam/Project.md; no stage or task status changed
