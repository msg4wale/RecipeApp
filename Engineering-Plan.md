# Engineering Implementation Plan

## Document Control
- Product: Social Recipe-Sharing Platform with AI Cooking & Nutrition Assistant
- Version: 1.1
- Status: Awaiting Requester Checkpoint and Plan Architect Revalidation
- Last Updated: 2026-10-04
- Engineering Lead: Engineering Lead Agent
- Implementation Readiness: NOT READY FOR IMPLEMENTATION — this revision awaits requester checkpoint and Plan Architect revalidation
- Source PRD: PRD.md (approved, final)
- Source TDD: TDD.md (approved, final, v1.1)

## Executive Engineering Summary

This plan decomposes the approved MVP scope (Chef Onboarding & Verification, Recipe Publishing with zero-plagiarism similarity gate, Social Engagement & Discovery, AI Cooking & Nutrition Assistant, and Should-Have items — Notifications, Analytics, Search, Moderation) into dependency-sequenced, parallel-execution-aware, issue-ready engineering tasks.

This revision addresses the 2026-10-04 Plan Architect REVISE for BE-003. API-003's current handlers, state transitions, persisted fields, shared storage/email abstractions, and existing regression tests are the reuse baseline—not implementation scope. BE-003 is narrowed to incremental verification plus the explicitly bounded OBS-004 audit/analytics integration and task closure. This plan is not authorized for implementation until the requester checkpoint and Plan Architect revalidation are complete.

The MVP build/test target is a single-workstation Docker Compose stack: Postgres 16 (+pg_trgm), MinIO, Ollama (qwen2.5-coder:14b), FastAPI backend + async worker, React SPA frontend, Mailpit for local email. Production deployment (TDD §15A) is explicitly out of the MVP critical path and only receives a lightweight spike task to avoid foreclosing future options.

No product requirement or architecture decision has been changed, added, or removed. Where the TDD marks a decision "Architect-Recommended, pending requester confirmation" (OTQ-001, OTQ-005, OTQ-006) or the PRD marks an item non-blocking/open (EC-006 moderation escalation), this plan schedules an early, time-boxed spike/decision task rather than blocking dependent work, and downstream tasks default to the Architect-recommended values already specified in the TDD.

Team sizing assumption for sequencing purposes only (not a commitment): 2–3 engineers working across backend, frontend, and QA/platform concerns concurrently, consistent with the confirmed ~$30K–$60K / ~600–800 person-hour / 12–16 week envelope (PRD CON-001/CON-005). No hours, dates, or named assignments are specified anywhere in this plan.

## 1. Implementation Scope

### 1.1 MVP Engineering Scope
- EPIC-001 Chef Onboarding & Verification (US-001–003): registration, email verification, certificate upload, Admin approval workflow.
- EPIC-002 Recipe Publishing & Zero-Plagiarism (US-004–006): recipe CRUD, media/document handling, hybrid similarity-check gate (pg_trgm + Jaccard + TF-IDF cosine), hold-for-differentiation + appeal flow.
- EPIC-003 Social Engagement & Discovery (US-007–010): likes, comments, follows, engagement-ranked feed.
- EPIC-004 AI Cooking & Nutrition Assistant (US-011–013): Ollama-backed conversational chat, disclaimer/AI-disclosure, 3-day conversation retention + indefinite bookmarking, 503 fallback on LLM unavailability.
- EPIC-005 Should-Have (US-014–017): notifications, basic analytics, search, content reporting/moderation.
- Supporting non-functional scope: security (authz/rate limiting/input validation), reliability (fail-safe similarity engine per TRISK-004, Ollama fault handling), observability (health/readiness, structured logs, AI latency percentiles for NFR-001), accessibility (WCAG 2.1 AA), local Docker Compose platform stack.
- Chef account deletion (EC-004) per ADR-009: content archived under `archived_chef_placeholder` system account preserving `original_chef_display_name` attribution.

### 1.2 Engineering Non-Goals
- Production/cloud deployment topology (TDD §15A) — deferred; only a scoping spike is included.
- GDPR/compliance program work (NFR-004) — explicitly out of scope per PRD.
- Native mobile apps (NFR-002 web-only).
- Formal third-party security audit (TRISK-005) — out of scope for MVP engineering; controls are still implemented.
- Additional personas beyond Guest/User/Chef/Admin — out of scope per PRD §20.
- Ad network real integration — INT-004 is stubbed only, no real ad-serving engineering.
- Moderation escalation workflow beyond report/hide (EC-006) — non-blocking, deferred extension point only.

### 1.3 Constraints
- CON-001: Budget confirmed at ~$30,000–$60,000 USD.
- CON-002: Web-only delivery.
- CON-003 / ADR-002: Self-hosted LLM via Ollama, model `qwen2.5-coder:14b`, native `/api/chat` NDJSON streaming API.
- CON-004: No compliance/GDPR-specific engineering.
- Timeline envelope: ~12–16 weeks; ~600–800 person-hours; small team of 2–3 developers (sequencing assumption only).
- ADR-001/ADR-001B: Modular monolith, Python/FastAPI backend.
- ADR-005: Single PostgreSQL 16 instance with `pg_trgm` extension (no separate search cluster for MVP).
- ADR-006: MinIO for object storage locally (S3-compatible; cloud S3 is a later concern).
- ADR-007: React + TypeScript + Vite + Radix/shadcn frontend; no SSR for MVP.
- ADR-008: Local Docker Compose stack (api, worker, postgres, minio, ollama, frontend, mailpit) is the primary MVP build/test target; production is a separate later consideration and must not be front-loaded into the MVP critical path.
- ADR-003: Async job-queue via DB-backed outbox table (`SELECT ... FOR UPDATE SKIP LOCKED`), NDJSON→SSE translation for AI chat streaming.
- ADR-004: Hybrid similarity detection — pg_trgm top-20 candidate retrieval + Jaccard ingredient-set + TF-IDF cosine on steps text, composite = 50/50 weighted average, threshold >0.95 with no differentiator ⇒ `held_for_differentiation`.
- ADR-009: Chef account deletion archives content under `archived_chef_placeholder` / `deleted_user_placeholder` system accounts, preserving `original_chef_display_name`.

### 1.4 Assumptions
- TASM-001–009 carried forward as-is (e.g., TASM-005 off-topic guardrail may be rule-based; TASM-006 feed boost multiplier is config-tunable; TASM-007 regular Users do not require email verification, only Chefs do; TASM-008 Ollama concurrency must be benchmarked against real hardware).
- Development/test hardware may be CPU-only (TRISK-008); NFR-001 AI latency targets (30s p95 / 45s p99) are verified functionally in this environment but formally re-validated once representative hardware/GPU is available — this does not block MVP functional completion.
- Team composition is small (2–3 developers) and cross-functional; task sizing assumes engineers may pick up backend, frontend, or QA tasks as capacity allows, but each task still has one primary owner at a time (rule 23).

### 1.5 Upstream Open Items (Non-Blocking — Scheduled as Early Spikes)
| ID | Topic | Status in Source | Handling in This Plan |
|---|---|---|---|
| OTQ-001 | Final frontend framework confirmation, CI provider, transactional email provider (Mailpit is local-dev only) | Proposed, not Confirmed (TDD) | PLAT-001 spike task in Wave 0; defaults to TDD-recommended stack (React+TS+Vite) if no decision is returned in time |
| OTQ-005 | SSR/SEO decision for public recipe pages | Non-blocking (TDD) | FE-000 spike task in Wave 0; MVP defaults to ADR-007 (no SSR) until/unless overridden |
| OTQ-006 | Feed ranking formula sign-off (weights, decay constant, follow-boost multiplier) | Architect-Recommended, pending requester confirmation | BE tasks implement TDD's recommended formula behind config (TASM-006); DOC/PM confirmation tracked as open question, not a blocker |
| EC-006 | Moderation escalation path beyond report/hide | Explicitly non-blocking (PRD §20) | OBS/SEC extension point only (SEC-006); full workflow deferred |

These items do not block Wave 0 or Wave 1 start; see §20 Open Engineering Questions for full detail and required resolution timing.

## 2. Implementation Workstreams

| Workstream | Scope | Primary Architecture Components | Task Count |
|---|---|---|---|
| Backend | Identity/auth, chef onboarding, recipe CRUD, similarity engine, social engagement, feed, AI assistant orchestration, admin/trust-safety, should-have extensions | COMP-001–005, COMP-008 | 18 |
| Frontend | Registration/onboarding UI, recipe authoring UI, feed/social UI, AI chat UI, admin console UI, should-have UI | COMP-001–004, COMP-008 | 10 |
| Database | Schema/migrations for full data model, indexing for similarity + feed | ADR-005, §8.2 data model | 4 |
| Integration | Ollama, Email/Mailpit, Object Storage/MinIO, Ad-network stub | INT-001–004 | 4 |
| Platform/DevOps | Docker Compose stack, CI pipeline, environment/secrets scaffolding, production-readiness scoping spike | ADR-008, §15/§15A | 5 |
| Security | AuthZ hardening, rate limiting, upload validation, prompt-injection hygiene, moderation extension point | COMP-001, COMP-004, COMP-008 | 5 |
| Observability | Health/readiness, structured logging, AI latency metrics, audit logging | §16/§17 | 4 |
| QA/Verification | Per-epic functional, negative/edge-case, performance, resilience, security, accessibility verification | All | 14 |
| Documentation | Local setup/runbook, API reference handoff notes | — | 2 |

Total engineering tasks: **65** (see per-section listings; IDs are stable and referenced throughout the dependency matrix).

## 3. Coverage Matrix

| Product / Technical Requirement | Architecture Reference | Implementation Task(s) | Verification Task(s) | Coverage Status |
|---|---|---|---|---|
| US-001/FR-013/BR-007 Chef registration + email verification | COMP-001, API-001/002, INT-002 | BE-001, BE-002, FE-001, INT-002-T | QA-001 | Covered |
| US-002 Certificate upload | COMP-001, COMP-006, API-002 | BE-002, FE-001, INT-003-T, SEC-002 | QA-001 | Covered |
| US-003/MET-004 Admin approval workflow | COMP-001, COMP-008, API-003, AN-004 | BE-003 (baseline reuse, incremental verification/integration), FE-008, OBS-004 | QA-001, QA-011 | Covered; BE-003 closes only after OBS-004 handoff evidence |
| US-004/FR-002 Recipe CRUD | COMP-002, API-004 | BE-004, FE-002, DB-001, SEC-002 | QA-002 | Covered |
| US-005/BR-005/EC-005a/b Zero-plagiarism similarity gate | COMP-005, ADR-004, API-005 | BE-005, BE-006, DB-002 | QA-003, QA-004 | Covered |
| US-006/API-012 Appeal + Admin similarity review | COMP-008, API-012 | BE-007, FE-008, OBS-004 | QA-004 | Covered |
| US-007/API-006 Likes | COMP-003, API-006 | BE-008, FE-003 | QA-005 | Covered |
| US-008/API-007 Comments | COMP-003, API-007 | BE-008, FE-003 | QA-005 | Covered |
| US-009/API-008 Follows | COMP-003, API-008 | BE-009, FE-003 | QA-005 | Covered |
| US-010/BR-008/OTQ-006 Engagement-ranked feed | COMP-003, API-009 | BE-010, FE-004 | QA-006 | Covered (formula default pending OTQ-006 sign-off) |
| US-011/NFR-001 AI chat conversation | COMP-004, ADR-002, ADR-003, API-010 | BE-011, BE-012, FE-005, INT-001-T, PLAT-002 | QA-007, QA-008, QA-009 | Covered |
| US-012/FR-011 3-day retention + bookmarking | COMP-004, API-011 | BE-013, FE-006 | QA-007 | Covered |
| US-013/BR-006/NFR-006/EC-001/EC-002 AI disclaimer, disclosure, off-topic refusal, food-safety notice | COMP-004, TASM-005 | BE-012, FE-005, SEC-004 | QA-008 | Covered |
| AD-014/503 fallback on LLM unavailable | ADR-002, ADR-003, API-010 | BE-014, OBS-001 | QA-009 | Covered |
| EC-004/ADR-009 Chef account deletion & archival | COMP-001, COMP-002, API-014 | BE-015, FE-007, DB-004 | QA-010 | Covered |
| EC-003 Unauthenticated action prompts login | COMP-001 | FE-003 | QA-005 | Covered |
| US-014 Notifications (Should) | EPIC-005 | BE-016, FE-009 | QA-012 | Covered |
| US-015 Search (Should) | EPIC-005, ADR-005 | BE-017, FE-010 | QA-012 | Covered |
| US-016 Basic analytics (Should)/AN-001–006; MET-004/AN-004 turnaround evidence | EPIC-005, COMP-008 | BE-003 persisted source fields, OBS-004 audit mapping, BE-016 analytics consumption | QA-011, QA-012 | Covered; MET-004 derives from existing application/review timestamps |
| US-017/EC-006 Content reports/moderation (Should) | COMP-008, API-013 | BE-018, FE-008, SEC-006 | QA-012, QA-013 | Covered (EC-006 escalation itself explicitly deferred) |
| NFR-005 Accessibility (WCAG 2.1 AA) | Frontend-wide | FE-001–010 | QA-014 | Covered |
| TRISK-004 Similarity engine fail-safe | COMP-005 | BE-005 | QA-003 | Covered |
| TRISK-001/TASM-008 Ollama concurrency | COMP-004/007 | BE-011, PLAT-002 | QA-009 | Covered |
| Security controls (authN/Z, rate limiting, upload validation, prompt-injection hygiene) | §16 | SEC-001–005 | QA-015 | Covered |
| Observability (health/readiness, logging, AI latency metrics, audit logging) | §17 | OBS-001–004 | QA-009, QA-011 | Covered |
| Local Docker Compose platform (ADR-008) | §15 | PLAT-001, PLAT-003, PLAT-005 | QA-016 | Covered |
| Production scoping (§15A, deferred) | §15A | PLAT-004 (spike only) | — | Deferred, non-blocking |
| OTQ-001 Frontend/CI/email provider confirmation | §21 Open Questions | PLAT-001, PLAT-003 | — | Non-blocking spike |
| OTQ-005 SSR/SEO decision | ADR-007 | FE-000 | — | Non-blocking spike |
| OTQ-006 Feed formula sign-off | API-009 | BE-010 | QA-006 | Non-blocking, defaults to recommended values |

## 5. Frontend Tasks

### FE-000 — Spike: Confirm SSR/SEO Approach for Public Recipe Pages (OTQ-005)

**Workstream:** Frontend | **Status:** Ready | **Priority:** Should Have (spike) | **Execution Wave:** Wave 0 | **Parallel Group:** PG-00 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-00
**Related Epic(s):** EPIC-002 | **Source Requirements:** OTQ-005 | **Architecture References:** ADR-007

#### Objective
Time-boxed spike to confirm whether MVP public recipe pages need SSR/SEO treatment, or whether ADR-007's "no SSR" default is accepted as-is.

#### Scope
Produce a short written recommendation (in-repo doc) confirming ADR-007 default or flagging a follow-up task if SSR is required later. Does not implement SSR.

#### Out of Scope
Any SSR implementation itself (would be a new task if the decision changes).

#### Acceptance Criteria
- ENG-AC-046: A written decision record exists confirming the SSR/SEO approach for MVP.

#### Verification Requirements
Review of the decision record by Product/Architecture stakeholders.

#### Dependencies
**Depends On:** None
**Blocks:** FE-002 (non-blocking soft dependency — proceeds with ADR-007 default if spike is not resolved in time)
**External Dependencies:** None

#### Definition of Done
Decision recorded; FE-002 proceeds under ADR-007 default regardless of timing.

#### References
- `TDD.md`: ADR-007, OTQ-005

---

### FE-001 — Implement Registration, Login, and Chef Application UI

**Workstream:** Frontend | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 1 | **Parallel Group:** PG-01 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-01
**Related Epic(s):** EPIC-001 | **Related User Story(ies):** US-001, US-002 | **Source Requirements:** FR-013, BR-007 | **Architecture References:** COMP-001, API-001, API-002

#### Objective
Build the registration, login, email-verification-status, and Chef application (certificate upload) screens.

#### Scope
Registration/login forms with validation; certificate upload UI with progress/error states; application status display (pending/approved/rejected).

#### Out of Scope
Admin review UI (FE-008).

#### Interface / Data Impact
Consumes API-001, API-002.

#### Acceptance Criteria
- ENG-AC-047: A user can complete registration and login through the UI without console errors.
- ENG-AC-048: Certificate upload shows clear success/error/progress states.
- ENG-AC-049: Screens meet WCAG 2.1 AA basics (labels, contrast, keyboard navigation).

#### Verification Requirements
Component tests; accessibility check (axe or equivalent); manual keyboard-navigation pass.

#### Dependencies
**Depends On:** BE-001, BE-002
**Blocks:** QA-001, QA-014
**External Dependencies:** None

#### Definition of Done
Implementation, component tests, and accessibility checks passing.

#### References
- `PRD.md`: US-001, US-002, FR-013, BR-007, NFR-005
- `TDD.md`: COMP-001, API-001, API-002

---

### FE-002 — Implement Recipe Authoring and Publish Flow UI

**Workstream:** Frontend | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-05 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-02
**Related Epic(s):** EPIC-002 | **Related User Story(ies):** US-004, US-005 | **Source Requirements:** FR-002, BR-005 | **Architecture References:** COMP-002, API-004, API-005

#### Objective
Build the recipe creation/edit UI (ingredients, steps, media) and the publish flow including the mandatory differentiation-comment prompt when a recipe is held for similarity.

#### Scope
Recipe authoring form; media upload; publish action; held-for-differentiation prompt and differentiator input; appeal submission entry point (links to FE-008 flow for status).

#### Out of Scope
Admin similarity/appeal review UI (FE-008).

#### Interface / Data Impact
Consumes API-004, API-005.

#### Acceptance Criteria
- ENG-AC-050: A Chef can author and publish a recipe end-to-end through the UI.
- ENG-AC-051: A held recipe surfaces the mandatory differentiation prompt and cannot be silently republished without input.

#### Verification Requirements
Component tests; end-to-end test covering both direct-publish and held-then-differentiate paths.

#### Dependencies
**Depends On:** BE-006, FE-000 (soft)
**Blocks:** QA-002, QA-003
**External Dependencies:** None

#### Definition of Done
Implementation and tests passing.

#### References
- `PRD.md`: US-004, US-005, FR-002, BR-005
- `TDD.md`: COMP-002, API-004, API-005, ADR-007

---

### FE-003 — Implement Likes, Comments, and Follow UI

**Workstream:** Frontend | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-06 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-03
**Related Epic(s):** EPIC-003 | **Related User Story(ies):** US-007, US-008, US-009 | **Source Requirements:** BR-002, EC-003 | **Architecture References:** COMP-003, API-006, API-007, API-008

#### Objective
Build like/comment/follow controls on recipe and profile views, including the login-prompt behavior for unauthenticated users (EC-003).

#### Scope
Like toggle button; comment thread UI; follow/unfollow control; login-prompt modal/redirect for unauthenticated actions.

#### Interface / Data Impact
Consumes API-006, API-007, API-008.

#### Acceptance Criteria
- ENG-AC-052: Authenticated users can like/comment/follow through the UI with immediate feedback.
- ENG-AC-053: Unauthenticated users attempting these actions are prompted to log in (EC-003), not silently blocked.

#### Verification Requirements
Component tests; manual/automated check of the unauthenticated-action prompt.

#### Dependencies
**Depends On:** BE-008, BE-009
**Blocks:** QA-005
**External Dependencies:** None

#### Definition of Done
Implementation and tests passing.

#### References
- `PRD.md`: US-007, US-008, US-009, BR-002, EC-003
- `TDD.md`: COMP-003, API-006, API-007, API-008

---

### FE-004 — Implement Engagement-Ranked Feed UI

**Workstream:** Frontend | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-07 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-03
**Related Epic(s):** EPIC-003 | **Related User Story(ies):** US-010 | **Source Requirements:** BR-008 | **Architecture References:** API-009

#### Objective
Build the home feed view consuming the ranked feed endpoint, with pagination/infinite scroll.

#### Scope
Feed list UI; loading/empty/error states; pagination.

#### Interface / Data Impact
Consumes API-009.

#### Acceptance Criteria
- ENG-AC-054: Feed renders in the order returned by the API without client-side re-sorting that would contradict the backend ranking.

#### Verification Requirements
Component tests including empty/error states.

#### Dependencies
**Depends On:** BE-010
**Blocks:** QA-006
**External Dependencies:** None

#### Definition of Done
Implementation and tests passing.

#### References
- `PRD.md`: US-010, BR-008
- `TDD.md`: API-009

---

### FE-005 — Implement AI Chat UI

**Workstream:** Frontend | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-08 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-04
**Related Epic(s):** EPIC-004 | **Related User Story(ies):** US-011, US-013 | **Source Requirements:** BR-006, NFR-006 | **Architecture References:** API-010, ADR-003

#### Objective
Build the conversational chat UI consuming the SSE stream, displaying the mandatory AI disclosure, and handling the 503 fallback gracefully.

#### Scope
Chat input/stream rendering; persistent disclosure banner/label; 503 error-state messaging with retry guidance; loading indicator respecting NFR-001 expectations.

#### Interface / Data Impact
Consumes API-010 (202 + SSE stream).

#### Acceptance Criteria
- ENG-AC-055: Disclosure text/label is visibly present throughout any AI chat session.
- ENG-AC-056: A 503 response is presented to the user as a clear, non-technical unavailability message with retry guidance, not a broken UI state.

#### Verification Requirements
Component tests; manual verification against BE-014's fault-injection scenario.

#### Dependencies
**Depends On:** BE-012, BE-014
**Blocks:** QA-008, QA-009
**External Dependencies:** None

#### Definition of Done
Implementation and tests passing.

#### References
- `PRD.md`: US-011, US-013, BR-006, NFR-006
- `TDD.md`: API-010, ADR-003, AD-014

---

### FE-006 — Implement AI Conversation History and Bookmarking UI

**Workstream:** Frontend | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-08 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-04
**Related Epic(s):** EPIC-004 | **Related User Story(ies):** US-012 | **Source Requirements:** FR-011 | **Architecture References:** API-011

#### Objective
Build the conversation history list (respecting 3-day visibility) and bookmarking controls.

#### Scope
Conversation list UI; bookmark toggle; bookmarked-only view.

#### Interface / Data Impact
Consumes API-011.

#### Acceptance Criteria
- ENG-AC-057: Bookmarked conversations remain visible in the UI beyond the 3-day window; non-bookmarked ones do not.

#### Verification Requirements
Component tests using mocked time-boundary API responses.

#### Dependencies
**Depends On:** BE-013
**Blocks:** QA-007
**External Dependencies:** None

#### Definition of Done
Implementation and tests passing.

#### References
- `PRD.md`: US-012, FR-011
- `TDD.md`: API-011

---

### FE-007 — Implement Account Deletion Confirmation UI

**Workstream:** Frontend | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-09 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-05
**Related Epic(s):** EPIC-001 | **Source Requirements:** EC-004 | **Architecture References:** ADR-009, API-014

#### Objective
Build the account deletion confirmation flow, clearly explaining the content-archival behavior to Chef users before they proceed (ADR-009).

#### Scope
Confirmation dialog explaining archival-with-attribution behavior; final delete action.

#### Interface / Data Impact
Consumes API-014.

#### Acceptance Criteria
- ENG-AC-058: A Chef is shown a clear explanation of content archival/attribution before confirming deletion.

#### Verification Requirements
Component test; manual copy review against ADR-009 wording intent.

#### Dependencies
**Depends On:** BE-015
**Blocks:** QA-010
**External Dependencies:** None

#### Definition of Done
Implementation and tests passing.

#### References
- `PRD.md`: EC-004
- `TDD.md`: ADR-009, API-014

---

### FE-008 — Implement Admin Console (Chef Review, Similarity/Appeal Review, Content Moderation)

**Workstream:** Frontend | **Status:** Ready | **Priority:** Must Have (Admin core) / Should Have (moderation extension) | **Execution Wave:** Wave 2–3 | **Parallel Group:** PG-09 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-05
**Related Epic(s):** EPIC-001, EPIC-002, EPIC-005 | **Related User Story(ies):** US-003, US-006, US-017 | **Source Requirements:** BR-007, BR-005 | **Architecture References:** COMP-008, API-003, API-012, API-013

#### Objective
Build the Admin console screens for chef certificate review, similarity/appeal review (with score breakdown display), and content report moderation.

#### Scope
Pending-applications list/detail with approve/reject; held-recipe/appeal review list/detail showing SimilarityCheck evidence; content-report queue with hide/unhide actions.

#### Out of Scope
Full moderation escalation workflow (EC-006, deferred).

#### Interface / Data Impact
Consumes API-003, API-012, API-013.

#### Acceptance Criteria
- ENG-AC-059: An Admin can approve/reject chef applications, decide appeals with visibility into similarity evidence, and hide reported content, entirely through the UI.

#### Verification Requirements
Component tests per screen; end-to-end test for at least one full approve and one full reject path per workflow.

#### Dependencies
**Depends On:** BE-003, BE-007, BE-018
**Blocks:** QA-001, QA-004, QA-012, QA-013
**External Dependencies:** None

#### Definition of Done
Implementation and tests passing for all three Admin workflows.

#### References
- `PRD.md`: US-003, US-006, US-017, BR-005, BR-007
- `TDD.md`: COMP-008, API-003, API-012, API-013

---

### FE-009 — Implement Notifications UI (Should-Have)

**Workstream:** Frontend | **Status:** Ready | **Priority:** Should Have | **Execution Wave:** Wave 3 | **Parallel Group:** PG-10 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-06
**Related Epic(s):** EPIC-005 | **Related User Story(ies):** US-014 | **Architecture References:** EPIC-005 extension points

#### Objective
Build a basic notification indicator/list consuming BE-016's notification records.

#### Scope
Notification bell/indicator; notification list view.

#### Acceptance Criteria
- ENG-AC-060: Users can view and mark notifications as read for all event types produced by BE-016.

#### Verification Requirements
Component tests.

#### Dependencies
**Depends On:** BE-016
**Blocks:** QA-012
**External Dependencies:** None

#### Definition of Done
Implementation and tests passing.

#### References
- `PRD.md`: US-014
- `TDD.md`: EPIC-005 extension points

---

### FE-010 — Implement Search UI (Should-Have)

**Workstream:** Frontend | **Status:** Ready | **Priority:** Should Have | **Execution Wave:** Wave 3 | **Parallel Group:** PG-10 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-06
**Related Epic(s):** EPIC-005 | **Related User Story(ies):** US-015 | **Architecture References:** BE-017

#### Objective
Build a basic search bar and results view consuming BE-017's search endpoint.

#### Scope
Search input; results list with loading/empty states.

#### Acceptance Criteria
- ENG-AC-061: Search returns and displays relevant recipes for representative query fixtures.

#### Verification Requirements
Component tests.

#### Dependencies
**Depends On:** BE-017
**Blocks:** QA-012
**External Dependencies:** None

#### Definition of Done
Implementation and tests passing.

#### References
- `PRD.md`: US-015
- `TDD.md`: BE-017

---

## 6. Database / Data Tasks

### DB-001 — Implement Core Schema and Migrations (Identity, Recipe, Social)

**Workstream:** Database | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 0 | **Parallel Group:** PG-00 | **Parallel-Safe:** Yes | **Shared Write Risk:** Medium (foundational schema touched by many later tasks) | **Integration Checkpoint:** IC-00
**Related Epic(s):** All | **Architecture References:** §8.2 data model, ADR-005

#### Objective
Create the initial PostgreSQL 16 schema and migration tooling covering User, ChefVerification, Recipe, RecipeIngredient, RecipeStep, RecipeMedia, Like, Comment, Follow, per the TDD data model.

#### Scope
- Migration framework setup (e.g., Alembic) as part of the FastAPI project scaffold.
- Table definitions, foreign keys, and base indexes for the above entities.
- `pg_trgm` extension enabled (ADR-005).

#### Out of Scope
SimilarityCheck/Appeal/AiConversation/AiMessage/ContentReport tables (DB-002/DB-003).

#### Acceptance Criteria
- ENG-AC-062: All Wave-0/Wave-1 backend tasks can run their integration tests against a freshly migrated database with no manual schema steps.

#### Verification Requirements
Migration up/down test; schema review against §8.2.

#### Dependencies
**Depends On:** PLAT-001
**Blocks:** BE-001, BE-002, BE-004, BE-008, BE-009, BE-011, OBS-004
**External Dependencies:** None

#### Definition of Done
Migrations apply cleanly on a fresh Docker Compose Postgres instance; rollback verified.

#### References
- `TDD.md`: §8.2, ADR-005

---

### DB-002 — Implement Similarity/Appeal Schema and Trigram Indexing

**Workstream:** Database | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 1 | **Parallel Group:** PG-02 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-02
**Related Epic(s):** EPIC-002 | **Architecture References:** ADR-004, ADR-005, §8.2

#### Objective
Add SimilarityCheck and Appeal tables plus the trigram indexes required for BE-005's candidate retrieval step.

#### Scope
Table definitions; GIN trigram index on relevant recipe text columns.

#### Acceptance Criteria
- ENG-AC-063: pg_trgm candidate queries used by BE-005 execute using the trigram index (verified via query plan).

#### Verification Requirements
Migration test; `EXPLAIN` verification that the trigram index is used.

#### Dependencies
**Depends On:** DB-001
**Blocks:** BE-005
**External Dependencies:** None

#### Definition of Done
Migration applies cleanly; index usage confirmed.

#### References
- `TDD.md`: ADR-004, ADR-005, §8.2

---

### DB-003 — Implement AI Assistant and Content Report Schema

**Workstream:** Database | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 1 | **Parallel Group:** PG-04 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-04
**Related Epic(s):** EPIC-004, EPIC-005 | **Architecture References:** §8.2, ADR-003

#### Objective
Add AiConversation, AiMessage, outbox/job-queue table, and (Should-Have) ContentReport table.

#### Scope
Table definitions; outbox table with locking-friendly indexes supporting `SELECT ... FOR UPDATE SKIP LOCKED`.

#### Acceptance Criteria
- ENG-AC-064: Outbox table structure supports the concurrency pattern required by BE-011 without lock contention errors under test load.

#### Verification Requirements
Migration test; concurrency smoke test reused from BE-011.

#### Dependencies
**Depends On:** DB-001
**Blocks:** BE-011, BE-018
**External Dependencies:** None

#### Definition of Done
Migration applies cleanly; outbox concurrency pattern verified.

#### References
- `TDD.md`: §8.2, ADR-003

---

### DB-004 — Implement Account Deletion / Placeholder Account Data Model Support

**Workstream:** Database | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 1 | **Parallel Group:** PG-09 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-05
**Related Epic(s):** EPIC-001 | **Source Requirements:** EC-004 | **Architecture References:** ADR-009

#### Objective
Add `original_chef_display_name` snapshot column(s) and the seeded `archived_chef_placeholder` / `deleted_user_placeholder` system accounts required by ADR-009.

#### Scope
Schema column additions; seed migration creating the two placeholder system accounts.

#### Acceptance Criteria
- ENG-AC-065: Placeholder accounts exist after migration and cannot be authenticated as normal accounts.

#### Verification Requirements
Migration test; seed-data verification.

#### Dependencies
**Depends On:** DB-001
**Blocks:** BE-015
**External Dependencies:** None

#### Definition of Done
Migration and seed applied; placeholder accounts verified non-loginable.

#### References
- `TDD.md`: ADR-009

---

## 7. Integration Tasks

### INT-001-T — Integrate Ollama `/api/chat` NDJSON API

**Workstream:** Integration | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 1 | **Parallel Group:** PG-04 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-04
**Related Epic(s):** EPIC-004 | **Architecture References:** INT-001, ADR-002, COMP-007

#### Objective
Build and verify the client integration against Ollama's native `/api/chat` streaming NDJSON API for model `qwen2.5-coder:14b`, including the health-check endpoint (`/api/tags`).

#### Scope
HTTP client wrapper; NDJSON parsing; timeout/error handling primitives consumed by BE-011/BE-014.

#### Acceptance Criteria
- ENG-AC-066: Client successfully streams a chat completion from the local Ollama container and correctly parses NDJSON chunks.
- ENG-AC-067: `/api/tags` health check reliably distinguishes "available" from "unavailable" states.

#### Verification Requirements
Integration test against the Docker Compose Ollama service.

#### Dependencies
**Depends On:** PLAT-001
**Blocks:** BE-011
**External Dependencies:** `qwen2.5-coder:14b` model pulled into local Ollama instance

#### Definition of Done
Client integration tested against live local Ollama container.

#### References
- `TDD.md`: INT-001, ADR-002, COMP-007

---

### INT-002-T — Integrate Email Delivery (Mailpit local / provider TBD)

**Workstream:** Integration | **Status:** Ready with Non-Blocking Dependency | **Priority:** Must Have | **Execution Wave:** Wave 0 | **Parallel Group:** PG-00 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-01
**Related Epic(s):** EPIC-001 | **Architecture References:** INT-002

#### Objective
Build the transactional email sending abstraction, targeting Mailpit for local development/test, with the sending interface kept provider-agnostic pending OTQ-001 resolution.

#### Scope
Email-sending interface (verification emails, chef decision notifications); Mailpit SMTP configuration in Docker Compose.

#### Out of Scope
Production email provider selection/integration (tracked under OTQ-001/PLAT-001 spike).

#### Acceptance Criteria
- ENG-AC-068: Verification and decision emails are visible/inspectable in Mailpit during local development and test runs.

#### Verification Requirements
Integration test asserting an email lands in Mailpit's inbox API for each triggering event.

#### Dependencies
**Depends On:** PLAT-001
**Blocks:** BE-002, BE-003
**External Dependencies:** None locally; production provider decision (OTQ-001) is a non-blocking future dependency

#### Definition of Done
Email interface implemented; Mailpit delivery verified in tests.

#### References
- `TDD.md`: INT-002, OTQ-001

---

### INT-003-T — Integrate Object Storage (MinIO)

**Workstream:** Integration | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 0 | **Parallel Group:** PG-00 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-01
**Related Epic(s):** EPIC-001, EPIC-002 | **Architecture References:** INT-003, ADR-006, COMP-006

#### Objective
Build the storage abstraction (COMP-006) backed by MinIO for local/MVP use, S3-compatible for future cloud migration (ADR-006).

#### Scope
Upload/download/delete interface; bucket provisioning in Docker Compose; content-type/size validation hooks used by SEC-002.

#### Acceptance Criteria
- ENG-AC-069: Certificate and recipe media files can be uploaded, retrieved, and deleted through the abstraction against the local MinIO instance.

#### Verification Requirements
Integration test against the Docker Compose MinIO service.

#### Dependencies
**Depends On:** PLAT-001
**Blocks:** BE-002, BE-004
**External Dependencies:** None

#### Definition of Done
Storage abstraction implemented and tested against local MinIO.

#### References
- `TDD.md`: INT-003, ADR-006, COMP-006

---

### INT-004-T — Stub Ad Network Integration Point

**Workstream:** Integration | **Status:** Ready | **Priority:** Could Have | **Execution Wave:** Wave 3 | **Parallel Group:** PG-10 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-06
**Architecture References:** INT-004

#### Objective
Provide a stubbed, no-op ad-network integration point per the TDD's boundary definition, without implementing real ad serving.

#### Scope
Interface/stub only; no real ad network calls.

#### Acceptance Criteria
- ENG-AC-070: A stub interface exists matching INT-004's defined boundary, returning inert/no-op responses.

#### Verification Requirements
Unit test confirming stub behavior.

#### Dependencies
**Depends On:** None
**Blocks:** None
**External Dependencies:** None

#### Definition of Done
Stub implemented and tested.

#### References
- `TDD.md`: INT-004

---

## 4. Backend Tasks

### BE-001 — Implement User Registration, Authentication, and Session Management

**Workstream:** Backend
**Status:** Ready
**Priority:** Must Have
**Execution Wave:** Wave 0
**Parallel Group:** PG-00
**Parallel-Safe:** Yes
**Shared Write Risk:** Low
**Integration Checkpoint:** IC-01
**Related Epic(s):** EPIC-001
**Related User Story(ies):** US-001
**Source Requirements:** FR-013, BR-004, TASM-007
**Architecture References:** COMP-001, API-001, ADR-005

#### Objective
Implement account registration, login, logout, and session/token handling for Guest→User and User→Chef-application identity flows.

#### Context
All authenticated behaviour (likes, comments, follows, publishing, AI chat, admin actions) depends on a working identity/session layer. Regular Users register without email verification (TASM-007); Chef applicants additionally go through BE-002/BE-003.

#### Scope
- User registration (email + password) with server-side validation.
- Password hashing (argon2 or bcrypt per TDD security guidance).
- Login/logout, session/token issuance and invalidation.
- Role field on User (Guest is unauthenticated, User, Chef, Admin) per COMP-001.
- Basic account profile fields required by later features (display name used in `original_chef_display_name` snapshot later).

#### Out of Scope
- Chef certificate upload / Admin approval (BE-002, BE-003).
- Password reset UX polish (implement minimally functional flow only if referenced by PRD; otherwise note as non-goal).
- Account deletion/archival (BE-015).

#### Technical Design Constraints
- Must follow COMP-001 boundary definitions; no business logic for other components embedded here.
- Auth tokens/sessions must be usable by all other backend components without re-implementation.
- Must enforce RBAC checks server-side, not client-side only.

#### Interface / Data Impact
- User table (per §8.2 data model).
- API-001 endpoints.

#### Acceptance Criteria
- ENG-AC-001: A new User can register, log in, and log out via API-001 endpoints.
- ENG-AC-002: Passwords are never stored or logged in plaintext.
- ENG-AC-003: Unauthenticated requests to protected endpoints return the contract-defined 401/redirect behavior (supports EC-003 downstream).

#### Verification Requirements
Unit tests for registration/validation/hashing; integration test for login/logout/session expiry; negative tests for duplicate email, invalid credentials.

#### Dependencies
**Depends On:** DB-001
**Blocks:** BE-002, BE-004, BE-008, BE-009, BE-011, BE-015, BE-016, BE-018, FE-001
**External Dependencies:** None

#### Implementation Notes
Use FastAPI dependency-injection pattern for current-user/session resolution as implied by ADR-001B modular monolith structure.

#### Definition of Done
- Implementation completed
- Unit + integration tests passing
- Static analysis/lint/type checks passing
- Security requirements satisfied (password hashing, session invalidation)
- PR acceptance criteria satisfied

#### References
- `PRD.md`: US-001, FR-013, BR-004, TASM-007
- `TDD.md`: COMP-001, API-001, ADR-005

---

### BE-002 — Implement Chef Application Flow (Email Verification + Certificate Upload)

**Workstream:** Backend
**Status:** Ready
**Priority:** Must Have
**Primary Owner Role:** Backend Engineer
**Supporting Role(s):** QA Engineer (verification evidence)
**Execution Wave:** Wave 1
**Parallel Group:** PG-01
**Parallel-Safe:** Yes
**Shared Write Risk:** Low
**Integration Checkpoint:** IC-01
**Related Epic(s):** EPIC-001
**Related User Story(ies):** US-001, US-002
**Source Requirements:** FR-013, BR-007
**Architecture References:** COMP-001, COMP-006, API-002, INT-002, INT-003

#### Objective
Allow a registered User to apply for Chef status by verifying their email and uploading a qualifying certificate document.

#### Context
Chef status is a prerequisite for recipe publishing (BR-004). This task implements the applicant-facing half of onboarding; BE-003 implements the Admin-facing review half.

#### Scope
- Email verification token issuance/validation (uses INT-002 Mailpit locally).
- Certificate document upload (uses COMP-006 storage abstraction backed by MinIO/INT-003).
- ChefVerification record creation with state machine: submitted → pending_review → approved/rejected.

#### Out of Scope
- Admin review UI/decisioning logic (BE-003).
- Recipe publishing itself (BE-004/BE-005).

#### Technical Design Constraints
- Must reuse COMP-006 media/document storage abstraction rather than a bespoke file path.
- Certificate files must pass upload validation (SEC-002) before persistence.

#### Interface / Data Impact
- ChefVerification table (§8.2).
- API-002 endpoints.
- MinIO bucket for certificate documents (INT-003).

#### Acceptance Criteria
- ENG-AC-004: A registered User can submit an email-verified Chef application with an uploaded certificate file, resulting in a `pending_review` ChefVerification record.
- ENG-AC-005: Unverified-email applications cannot reach `pending_review` state.
- ENG-AC-006: Rejected uploads (wrong type/size per SEC-002) are rejected with a clear error and no partial record.

#### Verification Requirements
Integration tests for the full submit flow, email-token expiry/misuse cases, and upload validation rejection cases.

#### Dependencies
**Depends On:** BE-001, DB-001, INT-002, INT-003
**Blocks:** BE-003
**External Dependencies:** None (Mailpit and MinIO are part of the local Docker Compose stack)

#### Implementation Notes
Reuse COMP-006 for both certificate documents and later recipe media (BE-004) to avoid duplicate storage code paths.

#### Definition of Done
- Implementation completed; tests passing; upload validation enforced; audit trail of state transitions recorded.

#### References
- `PRD.md`: US-001, US-002, FR-013, BR-007
- `TDD.md`: COMP-001, COMP-006, API-002, INT-002, INT-003

---

### BE-003 — Verify, Integrate, and Close Existing Admin Chef Review Flow

**Workstream:** Backend
**Status:** Ready
**Priority:** Must Have
**Primary Owner Role:** Backend Engineer
**Supporting Role(s):** QA Engineer (verification evidence)
**Execution Wave:** Wave 1
**Parallel Group:** PG-02
**Parallel-Safe:** Conditional (run only after BE-002, INT-002-T, and OBS-004 are complete; do not overlap edits to the shared API/model/audit surfaces)
**Shared Write Risk:** Medium (existing API/model behavior is reused; any required OBS-004 call-site integration must be coordinated with its contract)
**Integration Checkpoint:** IC-01
**Related Epic(s):** EPIC-001
**Related User Story(ies):** US-003
**Source Requirements:** FR-013, BR-007, MET-004, AN-004
**Architecture References:** COMP-001, COMP-008, API-003, INT-002, §8.5–8.6

#### Objective
Close the remaining verification and observability integration gaps for the already-implemented API-003 Admin chef-review flow, preserving its behavior and reusing its routes, domain logic, data fields, abstractions, and tests. No broad API-003 reimplementation is planned.

#### Context
US-003 completes the Chef onboarding state machine started by BE-002. Repository inspection confirms that `backend/app/main.py` already provides both API-003 routes, Admin authorization, pending-queue filtering, private certificate URL generation, decision validation/transitions, transaction-before-email ordering, and the 503 delivery-failure response. `backend/app/models.py` already defines the applicable `User` and `ChefVerification` fields; `backend/app/storage.py` already provides private presigned certificate access; `backend/app/email.py` already provides the provider-neutral sender and bounded SMTP attempts; and `backend/tests/test_admin_chef_verification.py` already covers the principal decision and failure paths. Preserve this current implementation as the baseline.

#### Scope
- Treat the existing API-003 route handlers, authorization, pending queue, private certificate access, request model, state transitions, user/model fields, storage/email abstractions, and existing tests listed in Context and References as reuse/regression targets. Do not recreate or replace them.
- Extend `backend/tests/test_admin_chef_verification.py` with the missing explicit unauthenticated `POST /api/admin/chef-verifications/{id}/decision` assertion required to verify ENG-AC-089 for both operations.
- Add a competing-decision integration/concurrency verification using the supported test database and existing conditional decision/update behavior. This test is limited to the already-required single-winner pending-state guard and ENG-AC-093 (consistent with TDD §8.5–8.6 strong transaction/state-transition consistency); it does not add queueing or new product behavior. Verify exactly one competing decision can win and the losing request cannot overwrite persisted outcome, reviewer, timestamp, or rationale. If repository inspection shows the current guard does not provide this invariant, make only the smallest justified guard correction; do not reimplement API-003.
- Integrate the existing persisted review record with the shared OBS-004 audit/analytics contract where needed. Reuse `ChefVerification.created_at`, `reviewed_at`, `reviewed_by_user_id`, `status`, and `rationale` as the source evidence; do not add duplicate review fields or emit duplicate telemetry in BE-003.
- Re-run focused regression and INT-002 contract/Mailpit verification for the existing API behavior, then close the task with evidence at IC-01.

#### Out of Scope
- Applicant-facing onboarding, email verification, or certificate upload (BE-002).
- Production email-provider selection or provider-specific delivery implementation (INT-002-T / OTQ-001).
- In-app notification records (BE-016).
- A durable outbox, background retry queue, deferred retry, or recovery workflow for committed chef decisions. These are not part of the accepted current design. This exclusion does not prohibit the existing bounded in-call SMTP attempts implemented by `SmtpEmailSender.send`.
- Admin similarity/appeal and content moderation workflows (BE-007, BE-018).

#### Technical Design Constraints
- Preserve COMP-001 ownership, COMP-008 review boundary, and API-003 contracts. Do not redesign or replace the current routes, request/response behavior, state model, authorization, storage/email abstractions, or existing tests.
- Keep server-side Admin authorization, private certificate access, pending-only decision guard, and atomic state/audit-field update behavior as already implemented and regression-tested.
- Reuse the INT-002 provider-neutral sender; Mailpit is for local integration verification, not a route-level provider dependency.
- Preserve the current transaction and notification semantics: commit the decision before the synchronous send; if the sender raises a delivery error (including after its bounded transient-error attempts), return HTTP 503 while retaining the committed decision. A repeated endpoint decision then returns 409 and does not invoke a second endpoint-level send.
- `SmtpEmailSender.send` performs up to three bounded SMTP attempts within one invocation for transient SMTP/OS failures. This in-call transport behavior remains. There is no durable outbox, background retry, or post-commit delivery-recovery mechanism.
- OBS-004 owns the shared audit destination/consumer contract. BE-003 maps or exposes existing persisted review evidence to that contract; it does not invent a new analytics event schema or duplicate the source fields.

#### Interface / Data Impact
- `GET /api/admin/chef-verifications?status=pending`
- `POST /api/admin/chef-verifications/{id}/decision`
- Existing `User.role`, `User.chef_status`, `ChefVerification.status`, `created_at`, `reviewed_by_user_id`, `reviewed_at`, and `rationale`; no new decision model fields are planned.
- Existing COMP-006 private certificate access and INT-002 transactional email abstraction; OBS-004 consumes/maps the persisted decision evidence for the shared audit/analytics path.

#### Acceptance Criteria
- ENG-AC-089: Existing authorization returns 401 for unauthenticated requests and 403 for non-Admin requests on both API-003 operations; tests explicitly assert the unauthenticated decision POST as well as the already-covered queue case.
- ENG-AC-090: Existing Admin queue response includes applicant details and a private certificate URL; regression tests confirm certificate access remains restricted and requests private storage authorization.
- ENG-AC-091: Existing approval behavior atomically persists the decision, reviewer, timestamp, and rationale, changes the applicant to `chef`/`active`, and grants publishing eligibility; regression evidence confirms these results.
- ENG-AC-092: Existing rejection behavior atomically persists the decision, reviewer, timestamp, and rationale, leaves the applicant `regular`/`rejected`, and does not grant publishing eligibility; regression evidence confirms these results.
- ENG-AC-093: Existing validation/state guards preserve the defined 404/409/422 outcomes. Incremental competing-decision verification proves only one decision wins and the losing request cannot overwrite the committed outcome or reviewer/time/rationale data.
- ENG-AC-094: Existing successful approval/rejection sends the correct notification through INT-002 and returns `notification_status: sent`; regression and Mailpit/provider-contract evidence verify delivery behavior.
- ENG-AC-095: After the decision commits, a sender delivery error yields HTTP 503 and the defined failure detail while persisted state remains. `SmtpEmailSender` preserves up to three in-call attempts for transient SMTP/OS errors (recipient refusal may fail immediately). A repeated decision returns 409 and does not send again through this endpoint; no durable or background retry is scheduled.
- ENG-AC-096: Existing pre-commit database failure behavior rolls back application/user changes and sends no decision notification; preserve and verify the existing regression test.
- ENG-AC-097: Existing persisted evidence maps to the reporting/audit needs without duplicate source fields: `created_at` is the submitted/application timestamp; `reviewed_at` is the decision timestamp; `reviewed_by_user_id` is the Admin actor; `status` is the decision outcome; and `rationale` is the recorded decision rationale. The elapsed duration `reviewed_at - created_at` supports MET-004 turnaround calculation. OBS-004 exposes/consumes the actor, timestamp, outcome, and rationale through its queryable admin audit path; BE-016/QA-011 use the same persisted timestamps for analytics verification. No additional BE-003 telemetry schema is required.

#### Verification Requirements
- Regression-run the existing focused suite in `backend/tests/test_admin_chef_verification.py`; do not recreate tests already present for Admin denial, pending queue/private links, approval/rejection, repeated decisions, commit rollback, and post-commit notification failure.
- Add an explicit unauthenticated decision POST assertion. Keep existing unauthenticated queue and non-Admin assertions as regression coverage.
- Add a competing-decision test only as bounded invariant verification of the existing conditional update/transaction; run on the supported database backend, use competing approval/rejection requests, and assert exactly one committed result plus a defined conflict for the loser. No timing-dependent sleep-based race test or new concurrency architecture is intended.
- Re-run the existing commit-failure/rollback and notification-success/failure tests, including persisted-state/409 retry assertions; fake sender for deterministic failures.
- Re-run the opted-in local Mailpit integration test where available and capture collection/full-suite/delivery evidence per QA-Report.md; do not alter its accepted verdict within this task plan.
- At IC-01, verify OBS-004 can query/map the persisted review fields and that QA-011 can calculate the turnaround duration from the same record. The integration check must verify evidence mapping, not duplicate the decision data.

#### Dependencies
**Depends On:** BE-002, INT-002-T, OBS-004
**Blocks:** BE-004, BE-009, BE-016, BE-018, FE-008, QA-001, QA-011, DOC-002
**External Dependencies:** Local Mailpit service for the existing opt-in integration verification; production transactional email provider remains unresolved under OTQ-001 and is non-blocking for local/MVP task completion.

#### Implementation Notes
No API, model, storage, email, or route implementation is planned by default. First inspect and reuse the named baseline, then make only the two justified test additions and the narrow OBS-004 integration needed to meet ENG-AC-097. If those checks pass without an integration change, this task is verification/regression/closure only. Any code change must be limited to a demonstrated gap in the existing behavior or required audit-contract handoff; do not replace existing functionality.

#### Definition of Done
- Existing API-003 routes, auth, transitions, models, storage/email abstractions, notification semantics, and covered tests remain intact; no duplicate implementation is introduced.
- Explicit unauthenticated decision POST assertion and supported-database competing-decision verification pass.
- Existing focused regressions, commit rollback, post-commit failure/409 retry, and INT-002/Mailpit contract checks pass with captured evidence.
- ENG-AC-097 evidence is queryable/consumable through OBS-004 and the turnaround calculation is verified by QA-011 using the existing persisted source fields.
- Static analysis/lint/type checks pass for any changed code; no implementation code is changed if verification shows no gap.
- No durable/background notification retry or outbox is added; bounded in-call SMTP retries remain unchanged.
- PRD acceptance intent and TDD component/API boundaries remain unchanged.

#### References
- `PRD.md`: US-003, AC-006, AC-007, FR-013, BR-007, MET-004
- `TDD.md`: COMP-001, COMP-008, API-003, INT-002, AN-004
- `backend/app/main.py`: existing `get_admin_user`, `list_pending_chef_verifications`, `decide_chef_verification`, and `ChefVerificationDecisionRequest`; reuse/regression baseline
- `backend/app/models.py`: existing `User` and `ChefVerification` fields; reuse/regression baseline
- `backend/app/storage.py`: existing `S3Storage.generate_presigned_download_url`; reuse/regression baseline
- `backend/app/email.py`: existing `TransactionalEmail`, `TransactionalEmailSender`, and `SmtpEmailSender.send` with up to three bounded in-call attempts; reuse/regression baseline
- `backend/tests/test_admin_chef_verification.py`: existing Admin/queue, private-link, approval/rejection, rollback, repeated-decision, and delivery-failure coverage; extend rather than duplicate

---

### BE-004 — Implement Recipe CRUD and Media/Ingredient/Step Management

**Workstream:** Backend | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 1 | **Parallel Group:** PG-01 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-02
**Related Epic(s):** EPIC-002 | **Related User Story(ies):** US-004 | **Source Requirements:** FR-002, BR-001 | **Architecture References:** COMP-002, COMP-006, API-004, DB-001

#### Objective
Implement create/read/update/delete for Recipe plus its RecipeIngredient, RecipeStep, and RecipeMedia child records, restricted to the owning Chef.

#### Context
Foundational content model for EPIC-002/003/004; the similarity engine (BE-005), feed (BE-010), and AI assistant recipe references all read from this model.

#### Scope
- Recipe CRUD endpoints with draft/published/held state field (`state`).
- Ownership enforcement: only the owning Chef may edit/delete (BR-001).
- RecipeIngredient/RecipeStep child CRUD as part of recipe authoring.
- RecipeMedia upload via COMP-006 storage abstraction.
- Maintains `search_text` field for later search (US-015) and trigram indexing.

#### Out of Scope
- Publish-time similarity gating (BE-005).
- Feed ranking (BE-010).

#### Technical Design Constraints
- Must reuse COMP-006 storage abstraction established in BE-002.
- `state` transitions must be restricted to values defined in TDD data model (draft, pending_similarity, held_for_differentiation, published, archived).

#### Interface / Data Impact
Recipe, RecipeIngredient, RecipeStep, RecipeMedia tables; API-004 endpoints.

#### Acceptance Criteria
- ENG-AC-010: A Chef can create, edit, and delete their own draft recipes including ingredients, steps, and media.
- ENG-AC-011: A non-owning user (including other Chefs) cannot edit or delete a recipe they do not own (BR-001).
- ENG-AC-012: `search_text` is populated/updated consistently on every content-affecting write.

#### Verification Requirements
Unit tests for CRUD + ownership authorization; integration test for full recipe authoring flow including media upload.

#### Dependencies
**Depends On:** BE-001, BE-003, DB-001
**Blocks:** BE-005, BE-010, FE-002
**External Dependencies:** None

#### Implementation Notes
Keep publish-state transition logic isolated so BE-005 can intercept the draft→published transition without modifying this task's core CRUD code.

#### Definition of Done
Implementation, tests, ownership checks, and search_text maintenance verified.

#### References
- `PRD.md`: US-004, FR-002, BR-001
- `TDD.md`: COMP-002, COMP-006, API-004

---

### BE-005 — Implement Hybrid Similarity Detection Engine

**Workstream:** Backend | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-05 | **Parallel-Safe:** Conditional (owns publish-state transition; must not overlap with BE-004 state-machine edits) | **Shared Write Risk:** Medium | **Integration Checkpoint:** IC-02
**Related Epic(s):** EPIC-002 | **Related User Story(ies):** US-005 | **Source Requirements:** BR-005, EC-005a, EC-005b | **Architecture References:** COMP-005, ADR-004, API-005, DB-002

#### Objective
Implement the hybrid zero-plagiarism similarity check that gates recipe publishing: pg_trgm top-20 candidate retrieval, Jaccard ingredient-set similarity, TF-IDF cosine similarity on steps text, composite 50/50 weighted score, threshold >0.95 triggers `held_for_differentiation` unless a differentiator is present.

#### Context
This is the core zero-plagiarism guarantee (BR-005) and the single most architecture-significant piece of business logic in the MVP. TRISK-004 requires this engine to fail safe (never silently auto-publish on internal error).

#### Scope
- Candidate retrieval via pg_trgm trigram index (DB-002) over existing published recipes.
- Jaccard similarity over normalized ingredient sets.
- TF-IDF cosine similarity over steps text.
- Composite scoring (50/50 weighted average) and threshold logic per ADR-004.
- SimilarityCheck record creation capturing score breakdown for audit/appeal (BE-007).
- Fail-safe behavior: any internal engine error routes the recipe to `held_for_differentiation` rather than auto-publishing (TRISK-004).

#### Out of Scope
- Admin review/appeal decisioning UI/logic (BE-007).
- Mandatory differentiation comment UX (FE-002 handles the prompt; this task only evaluates presence/absence).

#### Technical Design Constraints
- Must use the exact scoring/threshold formula defined in ADR-004; do not substitute an alternative algorithm.
- Must never allow a silent auto-publish on error (TRISK-004) — this is a hard release gate for QA-004.
- Borderline scoring behavior (EC-005b) must be deterministic and explainable via the stored score breakdown.

#### Interface / Data Impact
SimilarityCheck table (§8.2); reads Recipe/RecipeIngredient/RecipeStep; API-005 publish endpoint invokes this engine synchronously or via the async job queue (ADR-003) depending on corpus size performance (TRISK-002).

#### Acceptance Criteria
- ENG-AC-013: Publishing a recipe with >0.95 composite similarity to an existing recipe and no differentiator results in `held_for_differentiation` state, not `published`.
- ENG-AC-014: A recipe with a genuine differentiator is published despite high similarity, and the differentiator is recorded.
- ENG-AC-015: A simulated internal engine failure (e.g., forced exception) results in `held_for_differentiation`, never `published` (TRISK-004 fail-safe).
- ENG-AC-016: SimilarityCheck record stores the pg_trgm candidate list and both component scores for later Admin/appeal review.

#### Verification Requirements
Unit tests per scoring component; integration tests for full publish-gate flow including the fail-safe path; regression fixture set covering EC-005a (false positive) and EC-005b (borderline) scenarios.

#### Dependencies
**Depends On:** BE-004, DB-002
**Blocks:** BE-006, BE-007, FE-002
**External Dependencies:** None

#### Implementation Notes
Given TRISK-002 (corpus growth degrades trigram performance), implement candidate retrieval so it can later be tuned/limited without changing the scoring contract.

#### Definition of Done
Implementation, full unit/integration test suite including fail-safe and edge-case fixtures, passing; score breakdown persisted.

#### References
- `PRD.md`: US-005, BR-005, EC-005a, EC-005b
- `TDD.md`: COMP-005, ADR-004, API-005, TRISK-002, TRISK-004

---

### BE-006 — Wire Similarity Engine into Recipe Publish Flow

**Workstream:** Backend | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-05 | **Parallel-Safe:** No (shares publish-state transition with BE-004/BE-005) | **Shared Write Risk:** Medium | **Integration Checkpoint:** IC-02
**Related Epic(s):** EPIC-002 | **Related User Story(ies):** US-005 | **Source Requirements:** BR-005 | **Architecture References:** COMP-002, COMP-005, API-005

#### Objective
Integrate BE-005's engine into the actual publish endpoint state transition, including the mandatory differentiation comment capture path.

#### Context
Separated from BE-005 to isolate "scoring logic" from "publish workflow orchestration," but sequenced immediately after it since they share the publish-state transition.

#### Scope
- API-005 publish endpoint orchestration: draft → pending_similarity → (published | held_for_differentiation).
- Mandatory differentiation comment capture when a Chef chooses to publish over a held recommendation, per BR-005.
- Notification hook on hold (BE-016 dependency).

#### Out of Scope
- Scoring algorithm internals (BE-005).
- Appeal decisioning (BE-007).

#### Technical Design Constraints
Must not duplicate or diverge from BE-005's scoring contract.

#### Interface / Data Impact
Recipe.state transitions; API-005.

#### Acceptance Criteria
- ENG-AC-017: Publish flow correctly sequences through pending_similarity before reaching a terminal state.
- ENG-AC-018: A held recipe surfaces the required differentiation prompt to the Chef and cannot silently become published without it.

#### Verification Requirements
Integration test of full end-to-end publish flow via API, including UI-triggered differentiation comment.

#### Dependencies
**Depends On:** BE-005
**Blocks:** BE-007, FE-002, QA-003
**External Dependencies:** None

#### Definition of Done
Implementation and integration tests passing; state machine matches TDD exactly.

#### References
- `PRD.md`: US-005, BR-005
- `TDD.md`: COMP-002, COMP-005, API-005

---

### BE-007 — Implement Appeal Submission and Admin Similarity/Appeal Review

**Workstream:** Backend | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-06 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-02
**Related Epic(s):** EPIC-002 | **Related User Story(ies):** US-006 | **Source Requirements:** BR-005, MET-005 | **Architecture References:** COMP-008, API-012

#### Objective
Allow a Chef to appeal a `held_for_differentiation` decision and allow an Admin to review the SimilarityCheck evidence and approve or deny the appeal.

#### Scope
- Appeal submission endpoint (Chef-facing).
- Admin review endpoint surfacing SimilarityCheck score breakdown and candidate recipe(s).
- Approve appeal → publish recipe; deny appeal → recipe remains held, reason recorded.
- Audit log entry per decision (COMP-008), supports MET-005 turnaround reporting.

#### Out of Scope
Scoring algorithm (BE-005); publish orchestration internals (BE-006).

#### Interface / Data Impact
Appeal table; API-012 endpoints.

#### Acceptance Criteria
- ENG-AC-019: A Chef can submit exactly one open appeal per held recipe.
- ENG-AC-020: Admin approval of an appeal transitions the recipe to `published`.
- ENG-AC-021: Every appeal decision is audit-logged with timestamp for MET-005 reporting.

#### Verification Requirements
Integration tests for submit/approve/deny paths and audit logging.

#### Dependencies
**Depends On:** BE-006, OBS-004
**Blocks:** FE-008
**External Dependencies:** None

#### Definition of Done
Implementation and tests passing; audit trail present.

#### References
- `PRD.md`: US-006, BR-005, MET-005
- `TDD.md`: COMP-008, API-012

---

### BE-008 — Implement Likes and Comments

**Workstream:** Backend | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 1 | **Parallel Group:** PG-03 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-03
**Related Epic(s):** EPIC-003 | **Related User Story(ies):** US-007, US-008 | **Source Requirements:** BR-002 | **Architecture References:** COMP-003, API-006, API-007

#### Objective
Implement authenticated like and comment actions on published recipes, including aggregate counters used by the feed.

#### Scope
- Like toggle endpoint with idempotency (one like per user per recipe).
- Comment create/list endpoints with basic content validation.
- Maintains aggregate like/comment counters (FR-016) consumed by BE-010 feed ranking.

#### Out of Scope
Follow relationships (BE-009); feed ranking computation (BE-010).

#### Interface / Data Impact
Like, Comment tables; API-006, API-007.

#### Acceptance Criteria
- ENG-AC-022: An authenticated User can like/unlike a recipe exactly once at a time (toggle, not duplicate).
- ENG-AC-023: An unauthenticated request to like/comment is rejected per EC-003 contract.
- ENG-AC-024: Aggregate counters remain consistent under concurrent like/unlike operations.

#### Verification Requirements
Unit + integration tests including concurrency test for counter consistency.

#### Dependencies
**Depends On:** BE-001, BE-004
**Blocks:** BE-010, FE-003
**External Dependencies:** None

#### Definition of Done
Implementation and tests passing; counters verified consistent under load.

#### References
- `PRD.md`: US-007, US-008, BR-002, FR-016
- `TDD.md`: COMP-003, API-006, API-007

---

### BE-009 — Implement Follows

**Workstream:** Backend | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 1 | **Parallel Group:** PG-03 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-03
**Related Epic(s):** EPIC-003 | **Related User Story(ies):** US-009 | **Source Requirements:** BR-002 | **Architecture References:** COMP-003, API-008

#### Objective
Implement authenticated follow/unfollow of Chefs, feeding the followed-chef boost in feed ranking (BE-010).

#### Scope
Follow/unfollow toggle endpoint; follower/following list endpoints.

#### Out of Scope
Feed ranking computation (BE-010).

#### Interface / Data Impact
Follow table; API-008.

#### Acceptance Criteria
- ENG-AC-025: A User can follow/unfollow a Chef; duplicate follow requests are idempotent.
- ENG-AC-026: Unauthenticated follow attempts are rejected per EC-003.

#### Verification Requirements
Unit + integration tests.

#### Dependencies
**Depends On:** BE-001, BE-003
**Blocks:** BE-010, FE-003
**External Dependencies:** None

#### Definition of Done
Implementation and tests passing.

#### References
- `PRD.md`: US-009, BR-002
- `TDD.md`: COMP-003, API-008

---

### BE-010 — Implement Engagement-Ranked Feed

**Workstream:** Backend | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-07 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-03
**Related Epic(s):** EPIC-003 | **Related User Story(ies):** US-010 | **Source Requirements:** BR-008 | **Architecture References:** COMP-003, API-009, TRISK-003, OTQ-006, TASM-006

#### Objective
Implement the feed endpoint computing `feed_score = (likes*1.0 + comments*2.0) * decay(age_hours)`, `decay = 1/(1+age_hours/36)`, with a ×1.15 boost for recipes from followed Chefs, per the TDD's Architect-recommended formula (OTQ-006).

#### Context
OTQ-006 marks the exact weights as pending requester confirmation; this task implements the TDD-recommended values behind configuration (TASM-006) so the formula can be tuned without a code change once sign-off occurs.

#### Scope
- Feed query/ranking implementation over published recipes only.
- Config-tunable weights/decay constant/boost multiplier.
- Pagination.
- Basic caching/consideration for read volume (TRISK-003) appropriate to MVP scale (NFR-003: 100 MAU/1000 recipes).

#### Out of Scope
Full production-scale caching infrastructure (deferred; NFR-003 scale is small for MVP).

#### Interface / Data Impact
Reads Recipe, Like, Comment, Follow; API-009.

#### Acceptance Criteria
- ENG-AC-027: Feed ordering matches the specified formula given known like/comment/age/follow inputs (verified with fixture data).
- ENG-AC-028: Ranking weights are configurable without code changes (supports future OTQ-006 sign-off).
- ENG-AC-029: Only `published` recipes appear in the feed.

#### Verification Requirements
Deterministic fixture-based ranking test; pagination test; performance smoke test at NFR-003 scale.

#### Dependencies
**Depends On:** BE-004, BE-008, BE-009
**Blocks:** FE-004, QA-006
**External Dependencies:** None

#### Definition of Done
Implementation and tests passing; formula matches TDD recommendation exactly; weights configurable.

#### References
- `PRD.md`: US-010, BR-008
- `TDD.md`: COMP-003, API-009, TRISK-003, OTQ-006, TASM-006

---

### BE-011 — Implement AI Chat Job Queue and Ollama Orchestration

**Workstream:** Backend | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 1 | **Parallel Group:** PG-04 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-04
**Related Epic(s):** EPIC-004 | **Related User Story(ies):** US-011 | **Source Requirements:** NFR-001 | **Architecture References:** COMP-004, COMP-007, ADR-002, ADR-003, API-010

#### Objective
Implement the async job-queue (DB-backed outbox, `SELECT ... FOR UPDATE SKIP LOCKED`) that submits chat requests to Ollama's native `/api/chat` NDJSON API and translates streaming output to SSE for the client.

#### Scope
- Outbox table and worker process consuming queued AI chat jobs.
- Ollama client integration (INT-001) against `qwen2.5-coder:14b`.
- NDJSON→SSE translation layer.
- 202-accepted + SSE stream contract per API-010.

#### Out of Scope
Conversation retention/bookmarking (BE-013); disclaimer/off-topic content rules (BE-012); 503 fallback behavior specifics (BE-014).

#### Interface / Data Impact
AiConversation, AiMessage tables (partial — message content); API-010; outbox table.

#### Acceptance Criteria
- ENG-AC-030: A chat request is accepted (202) and streamed back via SSE using the worker/outbox pattern.
- ENG-AC-031: Concurrent chat jobs are processed without duplicate delivery (`SKIP LOCKED` correctness).

#### Verification Requirements
Integration test against local Ollama container; concurrency test with multiple simultaneous chat sessions; latency measurement harness feeding OBS-003.

#### Dependencies
**Depends On:** BE-001, DB-001, INT-001
**Blocks:** BE-012, BE-013, BE-014, FE-005
**External Dependencies:** Local Ollama container with `qwen2.5-coder:14b` pulled

#### Implementation Notes
TASM-008: benchmark concurrency ceiling on available dev hardware; document actual throughput observed for TRISK-001 tracking.

#### Definition of Done
Implementation and tests passing; outbox correctness verified under concurrency; latency instrumentation present.

#### References
- `PRD.md`: US-011, NFR-001
- `TDD.md`: COMP-004, COMP-007, ADR-002, ADR-003, API-010, TRISK-001, TASM-008

---

### BE-012 — Implement AI Disclaimer, Disclosure, and Content Guardrails

**Workstream:** Backend | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-08 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-04
**Related Epic(s):** EPIC-004 | **Related User Story(ies):** US-013 | **Source Requirements:** BR-006, NFR-006, EC-001, EC-002 | **Architecture References:** COMP-004, TASM-005

#### Objective
Ensure every AI chat response carries the mandatory AI-disclosure and that off-topic requests and food-safety-relevant content are handled per PRD rules.

#### Scope
- Mandatory AI-disclosure marker on every AI response/session (BR-006, NFR-006).
- Off-topic refusal behavior (EC-001) — may be rule-based per TASM-005.
- Food-safety disclaimer injection for relevant responses (EC-002).
- BR-003: AI is a general assistant, not restricted only to platform recipes.

#### Out of Scope
Job queue mechanics (BE-011); retention (BE-013).

#### Interface / Data Impact
AiMessage metadata (disclosure flag); prompt construction layer.

#### Acceptance Criteria
- ENG-AC-032: Every AI response includes the required disclosure text/flag.
- ENG-AC-033: An off-topic request (per EC-001 test fixtures) receives the defined refusal behavior, not a fabricated answer.
- ENG-AC-034: Food-safety-relevant answers include the required disclaimer (EC-002).

#### Verification Requirements
Fixture-based tests for on-topic/off-topic/food-safety scenarios; content-review of disclosure presence.

#### Dependencies
**Depends On:** BE-011
**Blocks:** BE-013, FE-005, QA-008
**External Dependencies:** None

#### Definition of Done
Implementation and fixture tests passing; disclosure present on 100% of sampled responses in test suite.

#### References
- `PRD.md`: US-013, BR-003, BR-006, NFR-006, EC-001, EC-002
- `TDD.md`: COMP-004, TASM-005

---

### BE-013 — Implement Conversation Retention (3-day) and Indefinite Bookmarking

**Workstream:** Backend | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-08 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-04
**Related Epic(s):** EPIC-004 | **Related User Story(ies):** US-012 | **Source Requirements:** FR-011 | **Architecture References:** COMP-004, API-011

#### Objective
Implement the 3-day rolling retention window for AiConversation/AiMessage records and an explicit bookmarking mechanism that exempts bookmarked content from expiry.

#### Scope
- Scheduled/derived expiry of conversations older than 3 days that are not bookmarked.
- Bookmark endpoint (API-011) marking a conversation/message as indefinitely retained.
- Deletion job or query-time filtering, whichever preserves correctness most simply.

#### Out of Scope
AI response generation itself (BE-011/BE-012).

#### Interface / Data Impact
AiConversation, AiMessage tables; API-011.

#### Acceptance Criteria
- ENG-AC-035: Non-bookmarked conversations older than 3 days are no longer retrievable by the user.
- ENG-AC-036: Bookmarked conversations remain retrievable indefinitely regardless of age.

#### Verification Requirements
Time-manipulated integration tests (simulated clock) for expiry boundary and bookmark exemption.

#### Dependencies
**Depends On:** BE-012
**Blocks:** FE-006, QA-007
**External Dependencies:** None

#### Definition of Done
Implementation and tests passing including boundary-condition coverage.

#### References
- `PRD.md`: US-012, FR-011
- `TDD.md`: COMP-004, API-011

---

### BE-014 — Implement 503 Fallback for LLM Unavailability

**Workstream:** Backend | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-08 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-04
**Related Epic(s):** EPIC-004 | **Related User Story(ies):** US-011 | **Source Requirements:** NFR-001 | **Architecture References:** ADR-002, ADR-003, ADR-014 (AD-014), API-010

#### Objective
Return the TDD-confirmed 503 fallback envelope when Ollama is unreachable or times out, instead of hanging requests or generic 500 errors.

#### Scope
- Health check against Ollama (`/api/tags`) integrated into request path or background health monitor (shared with OBS-002).
- Structured 503 response body per AD-014 contract.
- Client-visible retry guidance.

#### Out of Scope
Ollama capacity scaling (out of MVP scope; TRISK-006 tracked as risk only).

#### Interface / Data Impact
API-010 error path.

#### Acceptance Criteria
- ENG-AC-037: When Ollama is stopped/unreachable, chat requests receive the defined 503 envelope within a bounded time, not a hang or unhandled 500.
- ENG-AC-038: Recovery of Ollama availability is detected without requiring an API restart.

#### Verification Requirements
Fault-injection test: stop the Ollama container mid-suite and verify 503 behavior and recovery detection.

#### Dependencies
**Depends On:** BE-011
**Blocks:** FE-005, QA-009
**External Dependencies:** None

#### Definition of Done
Implementation and fault-injection tests passing.

#### References
- `PRD.md`: NFR-001
- `TDD.md`: ADR-002, ADR-003, AD-014, API-010

---

### BE-015 — Implement Chef Account Deletion and Content Archival

**Workstream:** Backend | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-09 | **Parallel-Safe:** Yes | **Shared Write Risk:** Medium | **Integration Checkpoint:** IC-05
**Related Epic(s):** EPIC-001 | **Related User Story(ies):** — (EC-004) | **Source Requirements:** EC-004 | **Architecture References:** ADR-009, API-014

#### Objective
Implement chef account deletion such that recipes/content are reassigned to the `archived_chef_placeholder` system account while preserving the original display name via `original_chef_display_name`, per ADR-009.

#### Scope
- Account deletion endpoint (Chef- and regular-User-facing variants as applicable).
- Reassignment of Recipe/Comment/Like/Follow ownership references to placeholder accounts (`archived_chef_placeholder`, `deleted_user_placeholder`).
- Snapshot of `original_chef_display_name` on affected recipes at deletion time.

#### Out of Scope
UI confirmation flow (FE-007).

#### Interface / Data Impact
User, Recipe (and related) tables; API-014.

#### Acceptance Criteria
- ENG-AC-039: After a Chef deletes their account, their published recipes remain publicly visible, attributed to the original display name snapshot, and owned by the placeholder account.
- ENG-AC-040: The placeholder account cannot be logged into and holds no PII from the original account.

#### Verification Requirements
Integration test for full deletion→reassignment→display verification; regression test confirming recipe content/attribution integrity post-deletion.

#### Dependencies
**Depends On:** BE-001, BE-004
**Blocks:** FE-007, QA-010
**External Dependencies:** None

#### Definition of Done
Implementation and tests passing; attribution preserved; no PII leakage in placeholder account.

#### References
- `PRD.md`: EC-004
- `TDD.md`: ADR-009, API-014

---

### BE-016 — Implement Notifications and Basic Analytics (Should-Have)

**Workstream:** Backend | **Status:** Ready | **Priority:** Should Have | **Execution Wave:** Wave 3 | **Parallel Group:** PG-10 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-06
**Related Epic(s):** EPIC-005 | **Related User Story(ies):** US-014, US-016 | **Source Requirements:** AN-001–006 | **Architecture References:** EPIC-005

#### Objective
Provide basic in-app notifications for key events (chef approval/rejection, similarity hold, appeal outcome, new like/comment/follow) and capture the analytics events required for MET-001–005 reporting.

#### Scope
- Notification records/endpoints for the event types already produced by BE-003, BE-006, BE-007, BE-008, BE-009.
- Analytics event capture supporting AN-001–006 (MAU, recipe count, engagement rate, review/appeal turnaround). For MET-004/AN-004, consume the existing chef-review evidence through OBS-004: application `created_at`, `reviewed_at`, `reviewed_by_user_id`, decision `status`, and `rationale`; derive turnaround as `reviewed_at - created_at` rather than creating duplicate source fields or a second decision record.

#### Out of Scope
Push/email delivery channels beyond what INT-002 already provides; advanced analytics dashboards (FE-010 provides basic viewing only).

#### Interface / Data Impact
Notification table (new); analytics event log.

#### Acceptance Criteria
- ENG-AC-041: Each defined event type generates a retrievable in-app notification for the relevant user.
- ENG-AC-042: Analytics events are captured with sufficient fields to compute MET-001–005 without additional backfill.

#### Verification Requirements
Integration tests per event type; analytics event schema validation.

#### Dependencies
**Depends On:** BE-003, BE-006, BE-007, BE-008, BE-009, OBS-004
**Blocks:** FE-009
**External Dependencies:** None

#### Definition of Done
Implementation and tests passing for all defined event types.

#### References
- `PRD.md`: US-014, US-016, AN-001–006, MET-001–005
- `TDD.md`: EPIC-005 extension points

---

### BE-017 — Implement Recipe Search (Should-Have)

**Workstream:** Backend | **Status:** Ready | **Priority:** Should Have | **Execution Wave:** Wave 3 | **Parallel Group:** PG-10 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-06
**Related Epic(s):** EPIC-005 | **Related User Story(ies):** US-015 | **Source Requirements:** — | **Architecture References:** ADR-005, EPIC-005

#### Objective
Implement basic recipe search using the existing `search_text` field and pg_trgm/PostgreSQL full-text capability, avoiding a separate search cluster (ADR-005).

#### Scope
Search endpoint over published recipes using `search_text`; basic relevance ordering.

#### Out of Scope
Advanced faceted search, external search engine integration.

#### Interface / Data Impact
Reads Recipe.search_text; new API endpoint.

#### Acceptance Criteria
- ENG-AC-043: Search returns published recipes matching query terms against title/ingredients/steps text.

#### Verification Requirements
Integration tests for relevant/irrelevant query fixtures.

#### Dependencies
**Depends On:** BE-004
**Blocks:** FE-010
**External Dependencies:** None

#### Definition of Done
Implementation and tests passing.

#### References
- `PRD.md`: US-015
- `TDD.md`: ADR-005

---

### BE-018 — Implement Content Reporting (Should-Have)

**Workstream:** Backend | **Status:** Ready | **Priority:** Should Have | **Execution Wave:** Wave 3 | **Parallel Group:** PG-10 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-06
**Related Epic(s):** EPIC-005 | **Related User Story(ies):** US-017 | **Source Requirements:** EC-006 | **Architecture References:** COMP-008, API-013

#### Objective
Allow users to report recipes/comments for moderation and allow Admins to hide reported content; provide the extension point for EC-006 without implementing full escalation workflow (explicitly non-blocking/deferred).

#### Scope
- Report submission endpoint (API-013).
- Admin hide/unhide action with audit logging.

#### Out of Scope
Full moderation escalation workflow beyond report/hide (EC-006 — explicitly non-blocking per PRD §20).

#### Interface / Data Impact
ContentReport table; API-013.

#### Acceptance Criteria
- ENG-AC-044: A user can report a recipe/comment; an Admin can hide it, removing it from public view.
- ENG-AC-045: Hide/unhide actions are audit-logged.

#### Verification Requirements
Integration tests for report/hide/unhide flows.

#### Dependencies
**Depends On:** BE-003, BE-004, BE-008, DB-003, OBS-004
**Blocks:** FE-008
**External Dependencies:** None

#### Definition of Done
Implementation and tests passing.

#### References
- `PRD.md`: US-017, EC-006
- `TDD.md`: COMP-008, API-013

---

## 8. Platform / DevOps Tasks

### PLAT-001 — Establish Local Docker Compose Stack and Project Scaffold

**Workstream:** Platform/DevOps | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 0 | **Parallel Group:** PG-00 | **Parallel-Safe:** Yes | **Shared Write Risk:** Medium (foundational scaffold) | **Integration Checkpoint:** IC-00
**Architecture References:** ADR-001, ADR-001B, ADR-008, §15

#### Objective
Stand up the local Docker Compose stack (api, worker, postgres, minio, ollama, frontend, mailpit) and the base FastAPI/React project scaffolds that all other tasks build on.

#### Context
This is the foundational platform task; ADR-008 designates the local Compose stack as the primary MVP build/test target, not an afterthought.

#### Scope
- `docker-compose.yml` defining all seven services with health checks.
- Base FastAPI project structure (modular monolith layout per ADR-001/001B).
- Base React+TS+Vite project scaffold (ADR-007), pending OTQ-001 final confirmation (defaults to this stack).
- Environment/config file conventions (`.env` handling), no secrets committed.
- Also resolves OTQ-001 (CI provider, email provider) as a bundled early spike/decision — see Implementation Notes.

#### Out of Scope
Production deployment topology (§15A) — see PLAT-004.

#### Technical Design Constraints
Must not front-load production infrastructure concerns into this task; scope is strictly the local Compose stack.

#### Interface / Data Impact
None directly; this is the platform substrate all other tasks run on.

#### Acceptance Criteria
- ENG-AC-071: `docker compose up` brings up all seven services healthy on a clean checkout, with Postgres, MinIO, and Ollama reachable from the api/worker containers.
- ENG-AC-072: A documented decision exists for CI provider and (non-local) email provider direction, even if deferred to a later phase (OTQ-001).

#### Verification Requirements
Clean-machine smoke test bringing the full stack up; health-check verification for each service.

#### Dependencies
**Depends On:** None
**Blocks:** DB-001, INT-001-T, INT-002-T, INT-003-T, all Wave-0/1 backend and frontend tasks
**External Dependencies:** Docker/Docker Compose installed on developer machines; Ollama model pull requires internet access once, then works offline

#### Implementation Notes
Treat OTQ-001 as a bundled decision-and-scaffold task: implement against the TDD-recommended stack (React+TS+Vite, FastAPI) by default; record the CI/email-provider decision status as an explicit note in the repo README rather than blocking scaffold work.

#### Definition of Done
Full stack verified running locally; scaffold committed; OTQ-001 decision status documented.

#### References
- `TDD.md`: ADR-001, ADR-001B, ADR-008, §15, OTQ-001

---

### PLAT-002 — Benchmark and Configure Ollama Concurrency Limits

**Workstream:** Platform/DevOps | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 1 | **Parallel Group:** PG-04 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-04
**Architecture References:** TRISK-001, TASM-008, COMP-007

#### Objective
Benchmark Ollama request concurrency on representative development hardware and configure worker concurrency limits accordingly to avoid overload.

#### Scope
Load-test harness against local Ollama; configuration of worker pool size / queue throttling based on observed ceiling.

#### Acceptance Criteria
- ENG-AC-073: A documented concurrency ceiling exists, and the worker is configured not to exceed it under load.

#### Verification Requirements
Load test demonstrating stable behavior at the configured concurrency limit; degraded-but-safe behavior above it (queued, not dropped).

#### Dependencies
**Depends On:** INT-001-T
**Blocks:** BE-011 (soft — informs configuration, does not block initial implementation)
**External Dependencies:** None

#### Definition of Done
Benchmark documented; configuration applied; TRISK-001 tracked with real data.

#### References
- `TDD.md`: TRISK-001, TASM-008, COMP-007

---

### PLAT-003 — CI Pipeline for Local-Stack Test Execution

**Workstream:** Platform/DevOps | **Status:** Ready with Non-Blocking Dependency | **Priority:** Must Have | **Execution Wave:** Wave 1 | **Parallel Group:** PG-02 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-01
**Architecture References:** ADR-008, OTQ-001

#### Objective
Stand up a CI pipeline that runs backend/frontend unit and integration tests against the Docker Compose stack (or an equivalent CI-friendly service composition) on every change.

#### Scope
CI configuration invoking the same Compose-based test environment used locally; test result reporting.

#### Out of Scope
Final CI *provider* confirmation if unresolved (OTQ-001) — implement against whatever provider is available/assumed (e.g., GitHub Actions, consistent with `gh` tooling already in use) and note it as adjustable.

#### Acceptance Criteria
- ENG-AC-074: Backend and frontend automated test suites run on every pull request against a Compose-based environment and report pass/fail status.

#### Verification Requirements
A deliberately failing test confirms the pipeline correctly reports failure; a passing suite confirms success reporting.

#### Dependencies
**Depends On:** PLAT-001
**Blocks:** None (quality gate, not a hard functional dependency)
**External Dependencies:** CI provider account/access

#### Definition of Done
Pipeline runs on every PR; pass/fail clearly reported.

#### References
- `TDD.md`: ADR-008, OTQ-001

---

### PLAT-004 — Spike: Production Deployment Scoping (Non-Blocking, §15A)

**Workstream:** Platform/DevOps | **Status:** Deferred | **Priority:** Could Have | **Execution Wave:** Wave 3 | **Parallel Group:** PG-10 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-06
**Architecture References:** §15A, OTQ-004

#### Objective
Produce a lightweight scoping note on production deployment options (per TDD §15A) so future work is not foreclosed, without implementing any production infrastructure in the MVP.

#### Scope
Written scoping document only, referencing §15A and OTQ-004 (GPU host sizing for production).

#### Out of Scope
Any actual production infrastructure provisioning or configuration — explicitly out of MVP scope per user instruction.

#### Acceptance Criteria
- ENG-AC-075: A scoping note exists summarizing §15A options and OTQ-004 considerations for future planning.

#### Verification Requirements
Review by Architecture stakeholder.

#### Dependencies
**Depends On:** None
**Blocks:** None
**External Dependencies:** None

#### Definition of Done
Scoping note delivered; explicitly marked non-blocking/deferred.

#### References
- `TDD.md`: §15A, OTQ-004

---

### PLAT-005 — Secrets and Environment Configuration Conventions

**Workstream:** Platform/DevOps | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 0 | **Parallel Group:** PG-00 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-00
**Architecture References:** ADR-008, §16 Security

#### Objective
Define and document how secrets/config (DB credentials, session signing keys, MinIO keys, SMTP config) are supplied to each service in the local Compose stack without being committed to source control.

#### Scope
`.env.example` conventions; documented required variables per service; local-only defaults that are clearly unsuitable for production reuse.

#### Acceptance Criteria
- ENG-AC-076: No secret values are committed to the repository; a new developer can configure a working local environment using only the documented `.env.example` and README instructions.

#### Verification Requirements
Fresh-clone setup test following only the documented instructions.

#### Dependencies
**Depends On:** PLAT-001
**Blocks:** None
**External Dependencies:** None

#### Definition of Done
Conventions documented and verified via fresh-clone test.

#### References
- `TDD.md`: ADR-008, §16

---

## 9. Security Tasks

### SEC-001 — Enforce Server-Side RBAC Across All Protected Endpoints

**Workstream:** Security | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 1–2 (cross-cutting) | **Parallel Group:** Cross-cutting | **Parallel-Safe:** Conditional (must be reviewed against each endpoint as it is built) | **Shared Write Risk:** Medium | **Integration Checkpoint:** IC-01
**Architecture References:** COMP-001, BR-001, BR-002, BR-004

#### Objective
Ensure every protected endpoint enforces role/ownership checks server-side (never relying on client-side gating alone), consistent with BR-001/BR-002/BR-004.

#### Scope
Central authorization dependency/middleware pattern reused by BE-001 through BE-018; per-endpoint authorization review checklist applied as each backend task completes.

#### Acceptance Criteria
- ENG-AC-077: A representative negative-test suite confirms that role/ownership bypass attempts (e.g., editing another chef's recipe, non-admin calling admin endpoints) are rejected across all protected endpoints.

#### Verification Requirements
Cross-cutting negative authorization test suite exercised against every protected endpoint (feeds into QA-015).

#### Dependencies
**Depends On:** BE-001
**Blocks:** QA-015
**External Dependencies:** None

#### Definition of Done
Authorization pattern implemented and applied consistently; negative test suite passing.

#### References
- `PRD.md`: BR-001, BR-002, BR-004
- `TDD.md`: COMP-001

---

### SEC-002 — Implement File Upload Validation (Certificates and Recipe Media)

**Workstream:** Security | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 1 | **Parallel Group:** PG-02 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-01
**Architecture References:** COMP-006, INT-003

#### Objective
Validate uploaded files (content-type, size, basic malware/format sanity) for both certificate documents (BE-002) and recipe media (BE-004) before persistence.

#### Scope
Validation hooks integrated into the COMP-006 storage abstraction (INT-003-T) used by both upload paths.

#### Acceptance Criteria
- ENG-AC-078: Uploads with disallowed content-types or oversized files are rejected with a clear error before reaching storage.

#### Verification Requirements
Negative tests for invalid type/size across both certificate and recipe media upload paths.

#### Dependencies
**Depends On:** INT-003-T
**Blocks:** BE-002, BE-004
**External Dependencies:** None

#### Definition of Done
Validation implemented and enforced on both upload paths; tests passing.

#### References
- `TDD.md`: COMP-006, INT-003

---

### SEC-003 — Implement Rate Limiting on Sensitive Endpoints

**Workstream:** Security | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 1 | **Parallel Group:** PG-02 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-01
**Architecture References:** §16 Security

#### Objective
Apply rate limiting to authentication, registration, AI chat submission, and report-submission endpoints to reduce abuse risk.

#### Scope
Rate-limiting middleware/dependency; per-endpoint limits appropriate to MVP scale (NFR-003).

#### Acceptance Criteria
- ENG-AC-079: Requests exceeding the configured rate on protected endpoints receive a clear rate-limit response rather than being silently processed or crashing the service.

#### Verification Requirements
Automated test exercising the rate limit threshold on at least login and AI chat submission endpoints.

#### Dependencies
**Depends On:** BE-001
**Blocks:** QA-015
**External Dependencies:** None

#### Definition of Done
Rate limiting implemented and tested on all identified sensitive endpoints.

#### References
- `TDD.md`: §16

---

### SEC-004 — Implement Prompt-Injection Hygiene for AI Assistant

**Workstream:** Security | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-08 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-04
**Architecture References:** COMP-004, §16

#### Objective
Apply basic prompt-construction hygiene (input sanitization/delimiting, system-prompt isolation) to reduce prompt-injection risk in the AI assistant flow.

#### Scope
Prompt template isolation between system instructions (disclaimer/guardrails) and user input; sanitization of obviously malicious control sequences.

#### Acceptance Criteria
- ENG-AC-080: A set of known prompt-injection test fixtures does not override the mandatory disclosure/guardrail behavior established in BE-012.

#### Verification Requirements
Fixture-based adversarial-prompt test suite.

#### Dependencies
**Depends On:** BE-012
**Blocks:** QA-008
**External Dependencies:** None

#### Definition of Done
Hygiene measures implemented; adversarial fixture suite passing.

#### References
- `TDD.md`: COMP-004, §16

---

### SEC-005 — Security Hardening Review (Headers, CSRF, XSS, SQLi Controls)

**Workstream:** Security | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** Cross-cutting | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-05
**Architecture References:** §16 Security

#### Objective
Apply and verify baseline web security controls: security headers, CSRF protection for state-changing requests, output-encoding/XSS prevention, and parameterized-query enforcement against SQL injection.

#### Scope
Middleware/framework-level configuration review across all Wave-0/1/2 backend and frontend tasks; no new business features.

#### Acceptance Criteria
- ENG-AC-081: Automated security-header and CSRF checks pass against the running application; a representative SQLi/XSS payload test suite is rejected/neutralized.

#### Verification Requirements
Automated security scan/checklist run against the local Compose stack; feeds QA-015.

#### Dependencies
**Depends On:** BE-001, BE-004, BE-008
**Blocks:** QA-015
**External Dependencies:** None

#### Definition of Done
Controls verified present; checklist results documented.

#### References
- `TDD.md`: §16

---

### SEC-006 — Moderation Extension Point (EC-006, Non-Blocking)

**Workstream:** Security | **Status:** Deferred | **Priority:** Could Have | **Execution Wave:** Wave 3 | **Parallel Group:** PG-10 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-06
**Architecture References:** COMP-008

#### Objective
Ensure BE-018's report/hide implementation exposes a clean extension point for a future moderation escalation workflow (EC-006), without implementing the escalation workflow itself.

#### Scope
Documentation/interface note only, confirming BE-018's data model can support a future escalation state without a breaking migration.

#### Out of Scope
Any actual escalation workflow implementation (explicitly non-blocking per PRD §20).

#### Acceptance Criteria
- ENG-AC-082: A brief design note confirms the ContentReport model can be extended with an escalation state without a breaking schema change.

#### Verification Requirements
Architecture review of the note against BE-018/DB schema.

#### Dependencies
**Depends On:** BE-018
**Blocks:** None
**External Dependencies:** None

#### Definition of Done
Note delivered and reviewed.

#### References
- `PRD.md`: EC-006
- `TDD.md`: COMP-008

---

## 10. Observability / Operations Tasks

### OBS-001 — Implement Health and Readiness Endpoints

**Workstream:** Observability | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 1 | **Parallel Group:** PG-02 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-01
**Architecture References:** §17, COMP-007

#### Objective
Implement `/healthz` and `/readyz` endpoints, with `/readyz` verifying DB connectivity and Ollama availability (via `/api/tags`).

#### Scope
Endpoint implementation; used by PLAT-001's Compose health checks and BE-014's fallback logic.

#### Acceptance Criteria
- ENG-AC-083: `/readyz` correctly reports not-ready when either Postgres or Ollama is unreachable, and ready when both are reachable.

#### Verification Requirements
Fault-injection test stopping each dependency independently.

#### Dependencies
**Depends On:** BE-001, INT-001-T
**Blocks:** BE-014, PLAT-001 (health-check wiring)
**External Dependencies:** None

#### Definition of Done
Endpoints implemented and verified under fault injection.

#### References
- `TDD.md`: §17, COMP-007

---

### OBS-002 — Implement Structured JSON Logging

**Workstream:** Observability | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 1 | **Parallel Group:** Cross-cutting | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-01
**Architecture References:** §17

#### Objective
Establish a consistent structured (JSON) logging format across backend services, including correlation/request IDs.

#### Scope
Logging middleware/config; adoption across BE-001 through BE-018.

#### Acceptance Criteria
- ENG-AC-084: Log output is valid structured JSON with a consistent request-correlation field across at least three representative endpoints.

#### Verification Requirements
Log-output format test.

#### Dependencies
**Depends On:** PLAT-001
**Blocks:** None (adopted incrementally by backend tasks)
**External Dependencies:** None

#### Definition of Done
Logging convention implemented and demonstrated across representative endpoints.

#### References
- `TDD.md`: §17

---

### OBS-003 — Implement AI Latency Percentile Monitoring (NFR-001)

**Workstream:** Observability | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-08 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-04
**Architecture References:** NFR-001, COMP-004

#### Objective
Capture and expose AI chat response latency metrics (p95/p99) to verify NFR-001 targets functionally in the local environment.

#### Scope
Latency capture around BE-011's job processing; basic metrics exposition (log-based or lightweight metrics endpoint) sufficient for local verification.

#### Acceptance Criteria
- ENG-AC-085: p95/p99 latency figures for AI chat responses are observable from local test runs, supporting QA-009's NFR-001 verification.

#### Verification Requirements
Load-test run producing a latency distribution report.

#### Dependencies
**Depends On:** BE-011
**Blocks:** QA-009
**External Dependencies:** None

#### Definition of Done
Latency capture implemented; sample report produced.

#### References
- `PRD.md`: NFR-001
- `TDD.md`: COMP-004

---

### OBS-004 — Implement Admin Audit Logging

**Workstream:** Observability | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 1 (shared foundation); consumers integrate at IC-01/IC-02/IC-06 | **Parallel Group:** PG-02 | **Parallel-Safe:** Conditional (freeze the audit contract before consumer integration; avoid overlapping migration/model edits) | **Shared Write Risk:** Medium | **Integration Checkpoint:** IC-01
**Primary Owner Role:** Observability/Platform Engineer
**Architecture References:** COMP-008

#### Objective
Provide the shared, queryable Admin audit-log mechanism and consumer contract required by COMP-008, including support for mapping the existing chef-review decision record to the audit/analytics path.

#### Scope
- Implement the shared audit-log utility/table and stable event fields required by COMP-008 (Admin actor, timestamp, outcome, rationale).
- Provide a query/consumption contract for audit evidence without moving decision ownership out of COMP-001/COMP-008.
- For chef certificate review, consume/map the existing `ChefVerification` record rather than creating duplicate source-of-truth decision fields: `reviewed_by_user_id` → actor, `reviewed_at` → decision time, `status` → outcome, and `rationale` → rationale. Use `created_at` with `reviewed_at` to expose the MET-004 turnaround duration.
- Keep shared audit mechanism implementation in OBS-004. API-003 call-site use is within BE-003; appeal/content decision call-site use remains in BE-007/BE-018. Verify each consumer at its integration checkpoint.
- The chef-review audit/analytics consumer contract must be available before BE-003 closes at IC-01. Subsequent appeal and moderation consumers integrate at IC-02/IC-06.

#### Interface / Data Impact
Implement the COMP-008 `admin_decisions` audit capability with queryable actor, timestamp, outcome, and rationale. For API-003, map/reference the existing `ChefVerification` source record and its current fields rather than adding duplicate source-of-truth decision fields.

#### Acceptance Criteria
- ENG-AC-086: The shared audit mechanism provides queryable Admin decision evidence with actor, timestamp, outcome, and rationale. The API-003 mapping exposes the existing persisted reviewer/time/status/rationale without duplicating source fields; BE-007 and BE-018 adopt the same shared contract for their decisions.

#### Verification Requirements
Test the shared audit mechanism's queryable fields and the API-003 mapping at IC-01 against the existing persisted chef-review record. Reuse consumer-specific decision tests in BE-003/BE-007/BE-018 to verify each workflow exposes its own audit evidence; do not claim all consumers are complete until their checkpoints.

#### Dependencies
**Depends On:** DB-001
**Blocks:** BE-003, BE-007, BE-018, BE-016, QA-011
**External Dependencies:** None

#### Definition of Done
Shared utility/table and consumer contract are implemented and queryable; API-003 mapping is available before BE-003 closure; BE-007/BE-018 adoption is verified at their respective checkpoints. No duplicate chef-review decision fields are introduced.

#### References
- `TDD.md`: COMP-008

---

## 11. QA / Verification Tasks

### QA-001 — Verify Chef Onboarding End-to-End (Registration, Email Verification, Certificate, Admin Review)

**Workstream:** QA | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-11 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-01
**Related Epic(s):** EPIC-001 | **Source Requirements:** US-001, US-002, US-003, BR-007, MET-004

#### Objective
Verify the full chef onboarding journey functionally, including negative paths.

#### Scope
Positive: register → verify email → submit certificate → admin approves → role becomes Chef. Negative: unverified email cannot submit; invalid certificate file rejected; admin rejection does not promote role; duplicate applications handled correctly. For API-003 authorization, verify unauthenticated requests to both the pending queue and decision POST are rejected, and non-Admin callers remain forbidden.

#### Verification Requirements
End-to-end test across FE-001/BE-001/BE-002/BE-003/FE-008; reuse the explicit unauthenticated decision POST assertion and competing-decision invariant test from BE-003 rather than duplicating their implementation. Verify the persisted application/review timestamps and OBS-004 evidence at IC-01; QA-011 validates the reporting calculation.

#### Dependencies
**Depends On:** BE-003, FE-001, FE-008
**Blocks:** None
**External Dependencies:** None

#### Definition of Done
All positive and negative scenarios pass.

#### References
- `PRD.md`: US-001–003, BR-007, MET-004

---

### QA-002 — Verify Recipe CRUD and Ownership Enforcement

**Workstream:** QA | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-11 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-02
**Source Requirements:** US-004, BR-001

#### Scope
Positive CRUD lifecycle; negative ownership-bypass attempts; media/ingredient/step management.

#### Dependencies
**Depends On:** BE-004, FE-002
**Blocks:** None

#### Definition of Done
All scenarios pass, including ownership negative tests.

#### References
- `PRD.md`: US-004, BR-001

---

### QA-003 — Verify Zero-Plagiarism Publish Gate (Positive, Differentiation, Fail-Safe)

**Workstream:** QA | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-11 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-02
**Source Requirements:** US-005, BR-005, TRISK-004

#### Scope
Direct publish of a dissimilar recipe; hold-for-differentiation trigger on near-duplicate content; successful publish after adding a genuine differentiator; simulated internal engine failure confirmed to fail safe to `held_for_differentiation` (never auto-publish).

#### Verification Requirements
This is a release-gating test — TRISK-004 fail-safe behavior (ENG-AC-015) must pass before Wave-2 sign-off.

#### Dependencies
**Depends On:** BE-006, FE-002
**Blocks:** None

#### Definition of Done
All scenarios, including the fail-safe scenario, pass.

#### References
- `PRD.md`: US-005, BR-005
- `TDD.md`: TRISK-004, ADR-004

---

### QA-004 — Verify Appeal and Admin Similarity Review

**Workstream:** QA | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-11 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-02
**Source Requirements:** US-006, MET-005, EC-005a, EC-005b

#### Scope
Chef submits appeal; Admin views score breakdown; approve → publish; deny → remains held; borderline-score fixtures (EC-005b) and false-positive fixtures (EC-005a) produce correct, explainable outcomes.

#### Dependencies
**Depends On:** BE-007, FE-008
**Blocks:** None

#### Definition of Done
All scenarios pass; MET-005 timestamp fields verified present.

#### References
- `PRD.md`: US-006, MET-005, EC-005a, EC-005b

---

### QA-005 — Verify Likes, Comments, Follows, and Unauthenticated-Action Prompts

**Workstream:** QA | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-11 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-03
**Source Requirements:** US-007–009, BR-002, EC-003

#### Scope
Positive like/comment/follow flows; concurrency/idempotency check on likes; unauthenticated action correctly prompts login (EC-003) rather than failing silently or crashing.

#### Dependencies
**Depends On:** BE-008, BE-009, FE-003
**Blocks:** None

#### Definition of Done
All scenarios pass.

#### References
- `PRD.md`: US-007–009, BR-002, EC-003

---

### QA-006 — Verify Engagement-Ranked Feed Formula and Ordering

**Workstream:** QA | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-11 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-03
**Source Requirements:** US-010, BR-008, OTQ-006

#### Scope
Fixture-based verification that feed ordering exactly matches `feed_score = (likes*1.0 + comments*2.0) * decay(age_hours)`, `decay = 1/(1+age_hours/36)`, with ×1.15 followed-chef boost; pagination correctness; only-published-recipes constraint.

#### Dependencies
**Depends On:** BE-010, FE-004
**Blocks:** None

#### Definition of Done
Fixture-based ordering matches expected values exactly; deviations block sign-off pending OTQ-006 resolution or explicit acceptance of default values.

#### References
- `PRD.md`: US-010, BR-008
- `TDD.md`: API-009, OTQ-006

---

### QA-007 — Verify AI Conversation Retention and Bookmarking Boundaries

**Workstream:** QA | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-11 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-04
**Source Requirements:** US-011, US-012, FR-011

#### Scope
Conversation visible within 3 days; conversation no longer visible after 3 days unless bookmarked; bookmarked conversation remains visible indefinitely; boundary condition (exactly 3 days) tested explicitly.

#### Dependencies
**Depends On:** BE-013, FE-006
**Blocks:** None

#### Definition of Done
All boundary and non-boundary scenarios pass.

#### References
- `PRD.md`: US-011, US-012, FR-011

---

### QA-008 — Verify AI Disclaimer, Disclosure, Off-Topic Refusal, and Food-Safety Guardrails

**Workstream:** QA | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-11 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-04
**Source Requirements:** BR-003, BR-006, NFR-006, EC-001, EC-002

#### Scope
On-topic cooking/nutrition query answered normally with visible disclosure; off-topic query refused per EC-001; food-safety-relevant query includes required disclaimer (EC-002); adversarial prompt-injection fixtures (SEC-004) do not bypass guardrails.

#### Dependencies
**Depends On:** BE-012, FE-005, SEC-004
**Blocks:** None

#### Definition of Done
All fixture scenarios pass.

#### References
- `PRD.md`: BR-003, BR-006, NFR-006, EC-001, EC-002

---

### QA-009 — Verify AI Latency (NFR-001) and 503 Fallback / Recovery

**Workstream:** QA | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-11 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-04
**Source Requirements:** NFR-001

#### Scope
p95/p99 latency measured against NFR-001 targets on available local hardware (with the TRISK-008 caveat noted, not treated as a hard functional failure if hardware is CPU-only); Ollama-down fault injection confirms 503 fallback envelope and clean recovery detection without API restart.

#### Dependencies
**Depends On:** BE-014, FE-005, OBS-003
**Blocks:** None

#### Definition of Done
503 fallback/recovery scenarios pass unconditionally; latency figures recorded and compared against NFR-001 with hardware caveat documented if targets are not met on CPU-only dev hardware.

#### References
- `PRD.md`: NFR-001
- `TDD.md`: TRISK-001, TRISK-008, AD-014

---

### QA-010 — Verify Chef Account Deletion and Content Archival (ADR-009)

**Workstream:** QA | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2 | **Parallel Group:** PG-11 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-05
**Source Requirements:** EC-004

#### Scope
Chef deletes account; recipes remain published, reassigned to placeholder account, displaying `original_chef_display_name`; placeholder account cannot be logged into; no PII leakage.

#### Dependencies
**Depends On:** BE-015, FE-007
**Blocks:** None

#### Definition of Done
All scenarios pass; PII leakage check explicitly performed.

#### References
- `PRD.md`: EC-004
- `TDD.md`: ADR-009

---

### QA-011 — Verify Chef Review/Appeal Turnaround Reporting (MET-004/MET-005)

**Workstream:** QA | **Status:** Ready | **Priority:** Should Have | **Execution Wave:** Wave 3 | **Parallel Group:** PG-12 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-06
**Primary Owner Role:** QA Engineer
**Source Requirements:** MET-004, MET-005

#### Scope
For MET-004, calculate chef-certificate review turnaround from the existing application `ChefVerification.created_at` to `reviewed_at`; confirm the reviewer (`reviewed_by_user_id`), outcome (`status`), and rationale (`rationale`) are queryable through OBS-004's audit mapping and that no duplicate event/source fields or backfill are needed. For MET-005, validate the appeal timestamps/decision evidence from BE-007 through the same reporting path. Verify BE-016's analytics consumption can use these existing persisted decision timestamps to compute the applicable turnaround metrics; do not infer a new product target, reporting cadence, or business-day calendar convention not specified by the approved sources.

#### Dependencies
**Depends On:** BE-003, BE-007, BE-016, OBS-004
**Blocks:** None

#### Definition of Done
Sample MET-004 and MET-005 turnaround calculations are produced from persisted records, actor/outcome evidence is queryable, and calculation inputs/results are recorded for verification.

#### References
- `PRD.md`: MET-004, MET-005

---

### QA-012 — Verify Should-Have Extensions (Notifications, Analytics, Search)

**Workstream:** QA | **Status:** Ready | **Priority:** Should Have | **Execution Wave:** Wave 3 | **Parallel Group:** PG-12 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-06
**Source Requirements:** US-014, US-015, US-016, AN-001–006

#### Scope
Notification generation/display per event type; search relevance for representative fixtures; analytics event capture sufficient for MET-001–005.

#### Dependencies
**Depends On:** BE-016, BE-017, FE-009, FE-010
**Blocks:** None

#### Definition of Done
All Should-Have scenarios pass.

#### References
- `PRD.md`: US-014–016, AN-001–006

---

### QA-013 — Verify Content Reporting and Moderation Hide/Unhide

**Workstream:** QA | **Status:** Ready | **Priority:** Should Have | **Execution Wave:** Wave 3 | **Parallel Group:** PG-12 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-06
**Source Requirements:** US-017, EC-006

#### Scope
Report submission; admin hide removes content from public view; unhide restores it; audit log entries present. Explicitly does not test escalation-beyond-hide behavior (EC-006, deferred).

#### Dependencies
**Depends On:** BE-018, FE-008
**Blocks:** None

#### Definition of Done
All in-scope scenarios pass.

#### References
- `PRD.md`: US-017, EC-006

---

### QA-014 — Verify Accessibility (WCAG 2.1 AA) Across Core Screens

**Workstream:** QA | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 3 | **Parallel Group:** PG-12 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-06
**Source Requirements:** NFR-005

#### Scope
Automated accessibility scan plus manual keyboard-navigation and screen-reader spot check across registration, recipe authoring, feed, AI chat, and admin screens.

#### Dependencies
**Depends On:** FE-001, FE-002, FE-004, FE-005, FE-008
**Blocks:** None

#### Definition of Done
No critical/serious automated accessibility violations remain open on core screens; manual spot check documented.

#### References
- `PRD.md`: NFR-005

---

### QA-015 — Verify Security Controls (AuthZ, Rate Limiting, Headers, CSRF, XSS, SQLi)

**Workstream:** QA | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 2–3 | **Parallel Group:** PG-12 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-05
**Source Requirements:** §16 Security

#### Scope
Aggregates and re-verifies SEC-001, SEC-003, SEC-005 acceptance criteria as a consolidated security regression pass before implementation sign-off.

#### Dependencies
**Depends On:** SEC-001, SEC-003, SEC-005
**Blocks:** None

#### Definition of Done
Consolidated security regression suite passes with no unresolved high-severity findings.

#### References
- `TDD.md`: §16

---

### QA-016 — Verify Local Docker Compose Stack Reproducibility

**Workstream:** QA | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 0–1 | **Parallel Group:** PG-11 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-00
**Source Requirements:** ADR-008

#### Scope
Clean-machine (or clean-container) verification that `docker compose up` reliably brings up a fully functional stack with no undocumented manual steps, on more than one run.

#### Dependencies
**Depends On:** PLAT-001, DB-001
**Blocks:** None

#### Definition of Done
Reproducible clean-start verified at least twice independently.

#### References
- `TDD.md`: ADR-008, §15

---

## 12. Documentation / Enablement Tasks

### DOC-001 — Local Setup and Developer Runbook

**Workstream:** Documentation | **Status:** Ready | **Priority:** Must Have | **Execution Wave:** Wave 0–1 | **Parallel Group:** PG-11 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-00
**Source Requirements:** ADR-008

#### Objective
Document how to clone, configure, and run the full local Docker Compose stack, including model pulling for Ollama and common troubleshooting steps.

#### Scope
README instructions; `.env.example` reference; troubleshooting section for common local issues (e.g., Ollama model not pulled, port conflicts).

#### Acceptance Criteria
- ENG-AC-087: A new developer can go from clean clone to running stack using only this documentation.

#### Dependencies
**Depends On:** PLAT-001, PLAT-005
**Blocks:** None

#### Definition of Done
Documentation reviewed and validated via a fresh-clone walkthrough.

#### References
- `TDD.md`: ADR-008, §15

---

### DOC-002 — Operational Runbook (Health Checks, Fault Recovery, Admin Procedures)

**Workstream:** Documentation | **Status:** Ready | **Priority:** Should Have | **Execution Wave:** Wave 3 | **Parallel Group:** PG-12 | **Parallel-Safe:** Yes | **Shared Write Risk:** Low | **Integration Checkpoint:** IC-06
**Source Requirements:** §17

#### Objective
Document operational procedures: interpreting health/readiness endpoints, recovering from an Ollama outage, and the Admin decision workflows (chef review, similarity/appeal review, moderation).

#### Scope
Runbook covering OBS-001/OBS-002/OBS-003 outputs and BE-003/BE-007/BE-018 admin workflows.

#### Acceptance Criteria
- ENG-AC-088: An operator unfamiliar with the codebase can follow the runbook to diagnose an Ollama-down scenario and confirm recovery.

#### Dependencies
**Depends On:** OBS-001, OBS-003, BE-003, BE-007, BE-018
**Blocks:** None

#### Definition of Done
Runbook reviewed and validated against a simulated Ollama-down scenario.

#### References
- `TDD.md`: §17

---

## 13. Dependency Matrix

| Task | Depends On | Blocks | External Dependencies |
|---|---|---|---|
| PLAT-001 | None | DB-001, INT-001-T, INT-002-T, INT-003-T, most Wave-0/1 tasks | Docker/Compose installed |
| PLAT-005 | PLAT-001 | None | None |
| PLAT-002 | INT-001-T | BE-011 (soft) | None |
| PLAT-003 | PLAT-001 | None | CI provider access |
| PLAT-004 | None | None | None |
| DB-001 | PLAT-001 | BE-001, BE-002, BE-004, BE-008, BE-009, BE-011, OBS-004 | None |
| DB-002 | DB-001 | BE-005 | None |
| DB-003 | DB-001 | BE-011, BE-018 | None |
| DB-004 | DB-001 | BE-015 | None |
| INT-001-T | PLAT-001 | BE-011 | Ollama model pulled |
| INT-002-T | PLAT-001 | BE-002, BE-003 | Production email provider (future, non-blocking) |
| INT-003-T | PLAT-001 | BE-002, BE-004 | None |
| INT-004-T | None | None | None |
| SEC-002 | INT-003-T | BE-002, BE-004 | None |
| BE-001 | DB-001 | BE-002, BE-004, BE-008, BE-009, BE-011, BE-015, BE-016, BE-018, FE-001, SEC-001, SEC-003 | None |
| BE-002 | BE-001, DB-001, INT-002-T, INT-003-T, SEC-002 | BE-003 | None |
| BE-003 | BE-002, INT-002-T, OBS-004 | BE-004, BE-009, BE-016, BE-018, FE-008, QA-001, QA-011, DOC-002 | Local Mailpit service for opt-in integration verification; production provider decision is future/non-blocking |
| BE-004 | BE-001, BE-003, DB-001, SEC-002 | BE-005, BE-010, FE-002 | None |
| BE-005 | BE-004, DB-002 | BE-006, BE-007, FE-002 | None |
| BE-006 | BE-005 | BE-007, FE-002, QA-003 | None |
| BE-007 | BE-006, OBS-004 | FE-008 | None |
| BE-008 | BE-001, BE-004 | BE-010, FE-003 | None |
| BE-009 | BE-001, BE-003 | BE-010, FE-003 | None |
| BE-010 | BE-004, BE-008, BE-009 | FE-004, QA-006 | None |
| BE-011 | BE-001, DB-001, DB-003, INT-001-T | BE-012, BE-013, BE-014, FE-005 | Ollama model pulled |
| BE-012 | BE-011 | BE-013, FE-005, QA-008, SEC-004 | None |
| BE-013 | BE-012 | FE-006, QA-007 | None |
| BE-014 | BE-011, OBS-001 | FE-005, QA-009 | None |
| BE-015 | BE-001, BE-004, DB-004 | FE-007, QA-010 | None |
| BE-016 | BE-003, BE-006, BE-007, BE-008, BE-009, OBS-004 | FE-009 | None |
| BE-017 | BE-004 | FE-010 | None |
| BE-018 | BE-003, BE-004, BE-008, DB-003, OBS-004 | FE-008, SEC-006 | None |
| FE-000 | None | FE-002 (soft) | None |
| FE-001 | BE-001, BE-002 | QA-001, QA-014 | None |
| FE-002 | BE-006, FE-000 (soft) | QA-002, QA-003, QA-014 | None |
| FE-003 | BE-008, BE-009 | QA-005 | None |
| FE-004 | BE-010 | QA-006 | None |
| FE-005 | BE-012, BE-014 | QA-008, QA-009, QA-014 | None |
| FE-006 | BE-013 | QA-007 | None |
| FE-007 | BE-015 | QA-010 | None |
| FE-008 | BE-003, BE-007, BE-018 | QA-001, QA-004, QA-012, QA-013, QA-014 | None |
| FE-009 | BE-016 | QA-012 | None |
| FE-010 | BE-017 | QA-012 | None |
| SEC-001 | BE-001 | QA-015 | None |
| SEC-003 | BE-001 | QA-015 | None |
| SEC-004 | BE-012 | QA-008 | None |
| SEC-005 | BE-001, BE-004, BE-008 | QA-015 | None |
| SEC-006 | BE-018 | None | None |
| OBS-001 | BE-001, INT-001-T | BE-014, PLAT-001 (health-check wiring) | None |
| OBS-002 | PLAT-001 | None | None |
| OBS-003 | BE-011 | QA-009 | None |
| OBS-004 | DB-001 | BE-003, BE-007, BE-018, BE-016, QA-011 | None |
| QA-001 | BE-003, FE-001, FE-008 | None | None |
| QA-002 | BE-004, FE-002 | None | None |
| QA-003 | BE-006, FE-002 | None | None |
| QA-004 | BE-007, FE-008 | None | None |
| QA-005 | BE-008, BE-009, FE-003 | None | None |
| QA-006 | BE-010, FE-004 | None | None |
| QA-007 | BE-013, FE-006 | None | None |
| QA-008 | BE-012, FE-005, SEC-004 | None | None |
| QA-009 | BE-014, FE-005, OBS-003 | None | None |
| QA-010 | BE-015, FE-007 | None | None |
| QA-011 | BE-003, BE-007, BE-016, OBS-004 | None | None |
| QA-012 | BE-016, BE-017, FE-009, FE-010 | None | None |
| QA-013 | BE-018, FE-008 | None | None |
| QA-014 | FE-001, FE-002, FE-004, FE-005, FE-008 | None | None |
| QA-015 | SEC-001, SEC-003, SEC-005 | None | None |
| QA-016 | PLAT-001, DB-001 | None | None |
| DOC-001 | PLAT-001, PLAT-005 | None | None |
| DOC-002 | OBS-001, OBS-003, BE-003, BE-007, BE-018 | None | None |

## 14. Implementation Waves

### Wave 0 — Foundations
PLAT-001, PLAT-005, DB-001, INT-002-T, INT-003-T, FE-000, DOC-001 (started), QA-016 (started)

### Wave 1 — Core Independent Modules and Admin Audit Foundation
BE-001, BE-002, OBS-004 (shared audit contract/foundation), BE-003 (baseline verification after BE-002 and OBS-004; final closure at IC-01), BE-008 (skeleton), BE-009 (skeleton), BE-011, DB-002, DB-003, DB-004, INT-001-T, PLAT-002, PLAT-003, SEC-002, SEC-003, OBS-001, OBS-002, FE-001

### Wave 2 — Dependent Integration
BE-004, BE-005, BE-006, BE-007, BE-008 (complete), BE-009 (complete), BE-010, BE-012, BE-013, BE-014, BE-015, SEC-001, SEC-004, SEC-005, OBS-003, FE-002, FE-003, FE-004, FE-005, FE-006, FE-007, FE-008, QA-001–QA-010, QA-016 (complete)

### Wave 3 — Should-Have Extensions and Cross-Cutting Verification
BE-016, BE-017, BE-018, QA-011 (after BE-016/OBS-004), SEC-006, PLAT-004, FE-009, FE-010, INT-004-T, QA-012, QA-013, QA-014, QA-015, DOC-002

A wave is a dependency-respecting execution set, not a sprint or a duration commitment.

## 15. Parallel Execution Plan

| Parallel Group | Execution Wave | Tasks | Parallel-Safe | Shared Write Risk | Integration Checkpoint |
|---|---|---|---|---|---|
| PG-00 | Wave 0 | PLAT-001, PLAT-005, DB-001, INT-002-T, INT-003-T, FE-000 | Yes | Low–Medium (DB-001/PLAT-001 are foundational; no other task writes to them concurrently) | IC-00 |
| PG-01 | Wave 1 | BE-001, FE-001 (FE-001 starts once BE-001 contract is frozen) | Conditional | Low | IC-01 |
| PG-02 | Wave 1 | BE-002, OBS-004 foundation, BE-003 (starts after BE-002, INT-002-T, and OBS-004; INT-002-T is Wave 0), DB-002, PLAT-003, SEC-002, SEC-003, OBS-001, OBS-002 | Conditional (BE-002 and OBS-004 may work concurrently only with isolated schema/model write ownership; BE-003 is serialized behind both; other independent tasks may proceed concurrently) | Medium for shared schema/audit surfaces | IC-01 |
| PG-03 | Wave 1 | BE-008 (skeleton), BE-009 (skeleton) | Yes | Low | IC-03 |
| PG-04 | Wave 1 | BE-011, DB-003, INT-001-T, PLAT-002 | Yes | Low | IC-04 |
| PG-05 | Wave 2 | BE-004, BE-005, BE-006 (BE-004→BE-005→BE-006 sequential chain), FE-002 | No (sequential chain due to shared publish-state transition) | Medium | IC-02 |
| PG-06 | Wave 2 | BE-007, FE-003 | Yes | Low | IC-02/IC-03 |
| PG-07 | Wave 2 | BE-010, FE-004 | Yes | Low | IC-03 |
| PG-08 | Wave 2 | BE-012, BE-013, BE-014 (sequential chain from BE-011), FE-005, FE-006, SEC-004, OBS-003 | Conditional (chain sequential; FE tasks parallel once contracts frozen) | Low | IC-04 |
| PG-09 | Wave 2 | BE-015, FE-007, DB-004 | Yes | Medium (BE-015 touches many ownership references) | IC-05 |
| PG-10 | Wave 3 | PLAT-004, SEC-006, INT-004-T | Yes | Low | IC-06 |
| PG-11 | Wave 2 | QA-001–QA-010, QA-016 | Yes | Low | IC-01–IC-05 |
| PG-12 | Wave 3 | BE-016, BE-017, BE-018, FE-008 (admin moderation extension), FE-009, FE-010, QA-011, QA-012, QA-013, QA-014, QA-015, DOC-002 | Conditional (BE-018→FE-008 moderation piece sequential; QA-011 follows BE-016/OBS-004) | Low | IC-06 |

Each task within a Parallel-Safe=Yes group may be assigned to a separate Software Engineer agent/session concurrently. Sequential chains noted above (BE-004→BE-005→BE-006; BE-011→BE-012→BE-013/BE-014) must not be split across concurrent owners without an agreed interface freeze point, since they share the publish-state machine and AI orchestration contract respectively.

## 16. Parallelization Opportunities

- FE-001 may begin as soon as BE-001's API-001 contract is frozen, even before BE-001's full implementation is merged, if the API contract is documented/stubbed early.
- FE-002, FE-003, FE-004, FE-005 may all proceed in parallel once their respective backend API contracts (API-004/005, API-006/007/008, API-009, API-010) are frozen, even if backend implementation is still in progress, provided a contract-first (OpenAPI/schema) approach is used.
- BE-016 (notifications) can begin once event-producing tasks (BE-003, BE-006, BE-007, BE-008, BE-009) have frozen their event shapes, without waiting for every consumer to be complete.
- BE-003 starts only after BE-002, INT-002-T, and OBS-004 have delivered their prerequisite behavior/contracts. The dependency graph and PG-02 ordering serialize BE-003 after these prerequisites; no partial baseline-verification start is assumed.
- BE-016 and QA-011 consume the MET-004/AN-004 evidence after OBS-004 exposes the existing review record; they must not add parallel review-source fields or require a new event schema.
- QA tasks in PG-11 may be authored/scaffolded in parallel with their corresponding implementation tasks, provided fixture data does not depend on undetermined implementation details (e.g., exact error message text may be a placeholder until implementation lands).
- If OTQ-006 sign-off arrives early, BE-010/FE-004/QA-006 can be adjusted without unblocking any other task, since the formula is already isolated behind configuration.

## 17. Critical Path

```text
PLAT-001 -> DB-001 -> BE-001 -> BE-002 -> BE-003 -> BE-004 -> BE-005 -> BE-006 -> BE-007 -> FE-008 -> QA-004
                    \-> OBS-004 ------------------/
BE-003 -> BE-009 -> BE-010 -> FE-004 -> QA-006
BE-001 -> BE-011 -> BE-012 -> BE-013 -> FE-006 -> QA-007
```

OBS-004 is a second prerequisite to BE-003: its shared audit contract must be delivered before BE-003's IC-01 closure. The principal feature chain is:

`PLAT-001 → DB-001 → BE-001 → BE-002 → BE-003 → BE-004 → BE-005 → BE-006 → BE-007 → FE-008 → QA-004`

with the audit prerequisite branch:

`DB-001 → OBS-004 → BE-003`

and independent critical branches:

`BE-003 → BE-009 → BE-010 → FE-004 → QA-006`

`BE-001 → BE-011 → BE-012 → BE-013 → FE-006 → QA-007`

Should-Have tasks (BE-016–018, FE-009/010, PLAT-004, SEC-006, INT-004-T) sit outside the Must-Have critical path and can slip without affecting MVP Must-Have completion, consistent with the lean budget/timeline constraint (CON-001, TRISK-007).

## 18. Integration Checkpoints

- **IC-00** — Local Docker Compose stack up and healthy; DB schema migrated; base scaffolds committed.
- **IC-01** — Identity/auth + chef application/admin-review contract frozen; existing API-003 regression suite and incremental unauthenticated/concurrent-decision verification pass; OBS-004 exposes the existing review record fields as queryable actor/time/outcome/rationale evidence for MET-004/AN-004; FE-001 integrable. Do not close BE-003 before the OBS-004 handoff is verified.
- **IC-02** — Recipe CRUD + similarity-gated publish flow integrable end-to-end.
- **IC-03** — Social engagement (likes/comments/follows) + feed integrable end-to-end.
- **IC-04** — AI assistant chat, disclosure, retention, and 503 fallback integrable end-to-end.
- **IC-05** — Account deletion/archival and Admin console workflows integrable end-to-end.
- **IC-06** — Should-Have extensions (notifications/search/moderation) and full cross-cutting QA/security/accessibility verification complete.

## 19. Engineering Risks and Blockers

| ID | Risk / Blocker | Affected Tasks | Impact | Owner / Upstream Owner | Resolution Needed |
|---|---|---|---|---|---|
| TRISK-001 | Ollama concurrency ceiling unknown until benchmarked | BE-011, PLAT-002 | Medium — may require queue throttling tuning | Engineering (PLAT-002 benchmark) | Benchmark early in Wave 1 |
| TRISK-002 | Corpus growth degrades pg_trgm candidate retrieval performance | BE-005 | Low at MVP scale (1000 recipes, NFR-003) | Engineering | Monitor; no MVP action required |
| TRISK-003 | Feed read volume/caching at scale | BE-010 | Low at MVP scale | Engineering | Revisit if scale assumptions change |
| TRISK-004 | Similarity engine must fail-safe, never silently auto-publish | BE-005, QA-003 | High — core trust guarantee | Engineering | QA-003 is a release gate for this behavior |
| TRISK-005 | No formal security audit for MVP | SEC-001–005, QA-015 | Medium | Product/Architecture (accepted risk per TDD) | Acknowledge; not resolvable within MVP budget |
| TRISK-006 | Self-hosted LLM capacity/quality risk at scale | BE-011, BE-014 | Medium | Architecture | Monitor via OBS-003; deferred production sizing under OTQ-004 |
| TRISK-007 | Lean budget/timeline envelope | All | Medium | Requester | Should-Have scope (Wave 3) is the natural descope target if pressure arises |
| TRISK-008 | CPU-only dev hardware slower than NFR-001 targets | QA-009 | Low (functional-only impact) | Engineering | Document caveat; do not block functional sign-off |

## 20. Open Engineering Questions

| Question | Affected Tasks | Blocking? | Owner | Required Before |
|---|---|---|---|---|
| OTQ-001: Final frontend framework, CI provider, and production email provider confirmation | PLAT-001, PLAT-003, INT-002-T | No — defaults to TDD-recommended stack | Solution Architect / Product Manager | Ideally before Wave 1 completion, but does not block Wave 0/1 start |
| OTQ-005: SSR/SEO approach for public recipe pages | FE-000, FE-002 | No — defaults to ADR-007 (no SSR) | Solution Architect | Before any future SSR work is scheduled; not required for MVP |
| OTQ-006: Feed ranking formula sign-off (weights/decay/boost) | BE-010, FE-004, QA-006 | No — implemented behind config using Architect-recommended values | Product Manager | Before public launch messaging around feed behavior, not before MVP build |
| EC-006: Moderation escalation path beyond report/hide | BE-018, SEC-006, QA-013 | No — explicitly deferred per PRD §20 | Product Manager | Only if moderation volume post-launch requires it |
| MET-004/MET-005 target monitoring cadence | BE-003, BE-007, BE-016, QA-011 | No | Product Manager | Before formal metrics reporting begins |

None of the inherited open questions above block Wave 0 or Wave 1 once the separate requester checkpoint and Plan Architect revalidation gates have passed; the affected tasks use only the Architect/PRD defaults already embedded in the approved TDD/PRD.

## 21. Handoff Summary

This revised plan is **awaiting the requester checkpoint and Plan Architect revalidation**; no implementation dispatch is authorized before both gates pass. Within the proposed scope, all Must-Have PRD requirements (EPIC-001–004) and the Should-Have epic (EPIC-005) retain implementation and verification coverage. Every architecture-significant TDD component, API, data model element, ADR, and integration boundary has an implementation task. No product requirement or architecture decision has been altered.

Four product/design open items are inherited from the TDD/PRD as explicitly non-blocking (OTQ-001, OTQ-005, OTQ-006, EC-006); each has a scheduled early spike/decision task or a config-driven default so that dependent engineering work is never blocked while awaiting sign-off. The separate MET-004/MET-005 monitoring-cadence question also remains non-blocking. The production deployment topology (§15A) is deliberately excluded from the MVP critical path per explicit instruction, receiving only a lightweight scoping task (PLAT-004).

After requester checkpoint approval and Plan Architect revalidation, Software Engineering, QA, and Platform roles can begin according to the waves. BE-003 is specifically a baseline-regression, incremental-test, OBS-004 integration, and closure task; it does not authorize recreating API-003. The BE-002/OBS-004 prerequisites must precede BE-003 closure, and the sequential chains (BE-004→BE-005→BE-006 publish state machine; BE-011→BE-012→BE-013/BE-014 AI orchestration) should remain under single ownership per chain or use an explicit interface-freeze handoff.
