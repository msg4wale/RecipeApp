# Product Requirements Document

## Document Control
- Product: Social Recipe-Sharing Platform with AI Cooking & Nutrition Assistant
- Version: 1.0
- Status: Draft — Architecture Ready (all previously flagged non-blocking open items and the RISK-009 feasibility concern are now resolved)
- Last Updated: 2026-08-29 (revision 3 — requester-approved PM-recommended budget/timeline for CON-001; RISK-009 resolved)
- Product Owner: Requester (Business Owner) — role identity not otherwise specified in idea.md
- PRD Readiness: **ARCHITECTURE READY WITH NON-BLOCKING OPEN ITEMS** (remaining items are minor/non-blocking edge-case and fallback-behavior decisions only — see § 20; all budget/timeline, NFR, and metric-definition items are now Confirmed)
- Source Discovery Artifact: idea.md

## Executive Summary
A web-only social recipe-sharing platform where verified "Chef" accounts publish original recipes and build a following, and "Regular User" accounts discover recipes through an engagement-ranked feed, like, comment, and follow chefs. A conversational AI Cooking & Nutrition Assistant — running on a self-hosted local LLM (Qwen3.8-27B via Local LLM Studio) — helps users with the recipe they are viewing as well as general cooking and nutrition questions. The MVP is free to use and monetized solely through advertising. Trust and safety are protected through an Admin-gated chef verification process and an automated recipe-similarity (zero-plagiarism) check with an Admin-reviewed appeal path. Success for the initial release is measured by reaching 100 active users and 1,000 recipes shared within Q1 post-launch.

This PRD carries forward all decisions confirmed in `idea.md` without reinterpretation. Four items were explicitly deferred by the requester to this stage (budget/timeline, AI response-time target, accessibility conformance level, and the operational definition of "active user"); all four have since been reviewed and confirmed by the requester (2026-08-29): Active User = Monthly Active User with defined actions; AI response time = 30s/95th percentile, 45s/99th percentile; Accessibility = WCAG 2.1 Level AA; Budget/timeline = ~12–16 weeks / ~600–800 person-hours / ~$30,000–$60,000 USD (a PM-recommended estimate that replaced the requester's originally stated $200/5-hour figure, flagged as infeasible via RISK-009, and subsequently approved by the requester). RISK-009 is now resolved, with a residual note that the approved budget remains lean relative to scope and should be monitored during execution.

## 1. Product Context

### 1.1 Problem Statement
*(Status: Assumption, inherited from idea.md)* Home cooks and food enthusiasts struggle to find trustworthy, engaging recipe content and lack an easy way to get personalized in-context guidance (substitutions, technique clarification, scaling, nutrition) while cooking. Independent/aspiring chefs lack a purpose-built platform to build an audience around their recipes, distinct from generic social media not optimized for recipe structure (ingredients, steps, nutrition) or creator-fan cooking interaction.

Traceability: idea.md § Problem Statement, § Why Current Approaches Are Insufficient.

### 1.2 Product Vision
*(Status: Proposed, inherited from idea.md)* "Become the go-to social platform where food creators build engaged communities around their recipes, and every recipe comes with an AI cooking companion that helps users succeed in the kitchen."

Traceability: idea.md § Vision.

### 1.3 Value Proposition
- For **Chefs**: a dedicated platform to publish recipes, build a following, and engage with fans without competing against unrelated generic social content.
- For **Home Cooks**: trustworthy, structured recipe content plus an always-available AI cooking and nutrition companion that goes beyond a single recipe.
- Differentiator: the AI Cooking & Nutrition Assistant is a conversational, general-purpose cooking/nutrition companion (not limited to Q&A on one recipe), running on self-hosted infrastructure with mandatory transparency (AI-disclosure + disclaimer).

Status: Confirmed (BR-003, FEAT-006) / Proposed (overall value-prop framing). Traceability: idea.md § Business Goals, § Core Features (FEAT-006), § Business Rules (BR-003).

### 1.4 Product Goals
| ID | Goal | Status | Traceability |
|---|---|---|---|
| PG-001 | Grow an engaged base of recipe creators (chefs) and followers | Proposed | idea.md § Business Goals |
| PG-002 | Increase user engagement/retention via social features (likes, comments, follows) | Proposed | idea.md § Business Goals |
| PG-003 | Differentiate via a general-purpose AI cooking/nutrition conversational assistant | Confirmed | idea.md BR-003, FEAT-006 |
| PG-004 | Maintain platform trust and content integrity via chef verification and zero-plagiarism enforcement | Confirmed | idea.md BR-005, BR-007 |
| PG-005 | Generate ad revenue while keeping the platform free for all users | Confirmed | idea.md § Business Model and Value |
| PG-006 | Reach defined adoption milestones within Q1 post-launch (100 active users, 1,000 recipes shared) | Confirmed | idea.md § Success Metrics |

### 1.5 Non-Goals
- Native iOS/Android mobile apps in this release (Confirmed — Future Enhancement). Traceability: NFR-002, CON-002.
- Creator monetization (subscriptions, tipping, payouts, sponsored recipes) in this release (Confirmed — ads-only MVP). Traceability: § Business Model, RISK-004.
- Region-specific regulatory compliance work (e.g., GDPR, food-safety/advertising regulation) in this release (Confirmed — accepted risk). Traceability: NFR-004, CON-004, RISK-006, ASM-007.
- Restaurant reservation/ordering, grocery delivery integration, non-recipe general social networking (Proposed Out of Scope). Traceability: idea.md § Out of Scope.
- Multi-language/localization, live cooking video streaming, marketplace/e-commerce for ingredients, advanced nutrition tracking/diet planning tools (Proposed Won't Have). Traceability: idea.md § MVP Scope — Won't Have.

## 2. Success Measures

| ID | Product Goal | Metric | Baseline | Target | Time Horizon | Measurement Owner |
|---|---|---|---|---|---|---|
| MET-001 | PG-001, PG-006 | Active users (see ASM-Def below for proposed operational definition) | 0 (pre-launch) | 100 active users | Q1 post-launch | Requester / Analytics (TBD) |
| MET-002 | PG-001, PG-006 | Recipes shared (published recipes, cumulative) | 0 (pre-launch) | 1,000 recipes shared | Q1 post-launch | Requester / Analytics (TBD) |
| MET-003 (Proposed) | PG-002 | Engagement rate: average likes + comments per published recipe | Not yet measured | Baseline to be established at launch; target TBD post-baseline | Q1 post-launch, reassessed thereafter | Product Management |
| MET-004 (Proposed) | PG-004 | Chef certificate approval turnaround time (Admin review queue) | Not yet measured | Proposed target: reviewed within 3 business days | Ongoing from launch | Admin / Operations |
| MET-005 (Proposed) | PG-004 | Plagiarism appeal resolution time | Not yet measured | Proposed target: resolved within 3 business days | Ongoing from launch | Admin / Operations |

**Confirmed operational definition of "Active User" (MET-001)** — *Requester-approved 2026-08-29*:
> An "active user" for the Q1 metric is a registered account (Chef or Regular User) that performs at least one of the following actions within a given calendar month: views a recipe, likes a recipe, comments on a recipe, follows a chef, publishes a recipe (chef only), or sends at least one message to the AI Cooking & Nutrition Assistant. The Q1 target (100 active users) is measured as **Monthly Active Users (MAU)** in the final month of the Q1 window post-launch.
>
> Status: `Confirmed` (requester-approved; previously PM Proposed).

## 3. Stakeholders

| Stakeholder / Role | Responsibility | Decision Ownership |
|---|---|---|
| Requester / Business Owner | Overall product vision, budget, priorities | Final decision owner (identity not otherwise specified) |
| Chefs / Content Creators | Publish recipes, engage with followers | Content ownership |
| Regular Users / Home Cooks | Consume content, engage socially, use AI agent | N/A |
| Admin | Approve/reject chef certificates; resolve plagiarism appeals; general content moderation | Platform-level trust & safety authority |
| *(Assumption)* Platform Moderation Team | Content/community moderation support to Admin | TBD |
| *(Assumption)* Legal/Compliance | Evaluate AI liability and data-privacy exposure, particularly post-MVP | TBD |

Traceability: idea.md § Stakeholders.

## 4. Target Users and Personas

### Persona: Creator Chef
- Description: An individual (professional or amateur) who creates and shares original recipes.
- Goals: Build a following, showcase cooking identity.
- Pain Points: Discovery/visibility; time to respond to every follower question (motivates AI agent as a scalable support tool, though the AI agent is user-facing, not chef-facing, per confirmed scope).
- Context: Uploads recipes with photos/video, engages with followers' comments.
- Permissions / Responsibilities: Create/edit/delete own recipes; respond to comments; view own analytics (Should Have); cannot edit other chefs' recipes; cannot publish while account is "pending."
- Traceability: idea.md Persona 1, BR-001, BR-004, FEAT-001, FEAT-008.

### Persona: Home Cook / Follower (Regular User)
- Description: A user who follows chefs, browses/searches recipes, engages socially, and uses the AI assistant while cooking.
- Goals: Find trustworthy recipes; get help while cooking; connect with favorite creators.
- Pain Points: Dietary-fit uncertainty, ingredient substitutions, technique clarification mid-cook.
- Context: Browses feed, likes/comments/follows, opens the AI chat while viewing/cooking a recipe.
- Permissions / Responsibilities: Like, comment, follow, converse with AI agent, report content; cannot publish recipes or edit others' content.
- Traceability: idea.md Persona 2, BR-002, BR-004, FEAT-002–006.

### Persona: Admin
- Description: Platform-level trust & safety role.
- Goals: Maintain content integrity and account trust without becoming an operational bottleneck.
- Context: Reviews chef certificate submissions; reviews plagiarism appeal disputes; handles reported content/moderation.
- Permissions / Responsibilities: Approve/reject chef certificates (BR-007); approve/deny plagiarism appeals (BR-005); remove content; ban/suspend accounts; resolve reports.
- Traceability: idea.md § Roles and Permissions (Admin row), BR-005, BR-007, FR-013, FR-015.

**Open Item (Not Confirmed):** Additional persona types (e.g., "Restaurant/Brand" account) were raised as an open question in idea.md but not resolved; not modeled in this PRD. Status: `Out of Scope` for this release unless the requester raises it.

## 5. Product Scope

### 5.1 MVP Release Goal
Launch a web-only platform where verified chefs can publish original recipes, users can discover and socially engage with that content via an engagement-ranked feed, and users can converse with a general-purpose AI Cooking & Nutrition Assistant — all governed by a chef verification workflow and a zero-plagiarism policy — sufficient to reach 100 active users and 1,000 recipes shared within Q1 post-launch. Status: Confirmed (composed from idea.md MVP Scope + Success Metrics).

### 5.2 Must Have
| ID | Item | Status |
|---|---|---|
| FEAT-001 | Recipe Publishing (chef-role only) | Confirmed |
| FEAT-002 | Social Feed & Discovery (engagement-ranked) | Confirmed |
| FEAT-003 | Likes | Confirmed |
| FEAT-004 | Comments | Confirmed |
| FEAT-005 | Follow Chefs | Confirmed |
| FEAT-006 | AI Cooking & Nutrition Assistant | Confirmed |
| FEAT-011 | Chef Self-Registration & Admin Approval Workflow | Confirmed |
| — | AI disclaimer + AI-disclosure notice on every AI output (BR-006/FR-011) | Confirmed |
| — | AI conversation 3-day retention with indefinite bookmarking (FR-012) | Confirmed |
| — | Zero-plagiarism similarity check + Admin-reviewed appeal (BR-005/FR-014/FR-015) | Confirmed |
| — | Engagement-based feed ranking (BR-008/FR-006) | Confirmed |

All Must Have items target **Web platform only**. Traceability: idea.md § MVP Scope — Must Have.

### 5.3 Should Have
| ID | Item | Status |
|---|---|---|
| FEAT-007 | Notifications (likes/comments/follows/new recipes) | Proposed |
| FEAT-008 | Chef Profile / Analytics | Proposed |
| FEAT-009 | Search (by name/ingredient/cuisine/diet) | Proposed |
| FEAT-010 | Content Moderation Tools (reporting/flagging) | Proposed |

Traceability: idea.md § MVP Scope — Should Have, § Core Features.

### 5.4 Could Have
- Recipe collections/bookmarks (distinct from AI-response bookmarking, which is Must Have)
- Advanced personalized recommendations
- Video content support beyond photos

Status: Proposed. Traceability: idea.md § MVP Scope — Could Have.

### 5.5 Won't Have in This Release
- Native iOS/Android mobile apps (Confirmed)
- Creator monetization/subscriptions/tipping (Confirmed — ads-only MVP)
- Region-specific regulatory compliance work (Confirmed — accepted risk for MVP)
- Multi-language support, live cooking video streaming, marketplace/e-commerce for ingredients, advanced nutrition tracking/diet planning tools (Proposed, pending confirmation)

Traceability: idea.md § MVP Scope — Won't Have.

### 5.6 Out of Scope
- Restaurant reservation/ordering features
- Grocery delivery integration
- Non-recipe general social networking (e.g., generic status posts unrelated to recipes)

Status: Proposed, pending confirmation. Traceability: idea.md § Out of Scope.

### 5.7 Future Enhancements
- Native iOS/Android mobile apps
- Personalized AI-driven recipe recommendations based on user history/preferences
- Creator monetization (tipping, subscriptions, sponsored recipes)
- Multi-recipe meal planning powered by the AI agent
- Video-first recipe content and live cooking sessions
- Multi-language/localization support
- Region-specific regulatory compliance work as the platform scales beyond MVP

Status: Proposed, non-blocking. Traceability: idea.md § Future Enhancements.

## 6. User Journeys

### Journey 1 — Home Cook Discovers and Engages with a Recipe
- Actor: Home Cook / Follower
- Trigger: User opens the app/feed.
- Preconditions: User has an account (registration required for like/comment/follow per BR-002; browsing may be possible without an account, not otherwise specified).
- Main Flow:
  1. User browses a feed of recipes ranked by engagement (most likes/comments first) and recipes from followed chefs.
  2. User opens a recipe (ingredients, steps, photos/video).
  3. User likes and/or comments on the recipe, optionally follows the chef.
  4. User opens the AI chat while viewing/cooking the recipe and asks a recipe-specific or general cooking/nutrition question.
  5. AI responds with an answer accompanied by a disclaimer and AI-disclosure notice.
- Alternate / Exception Flow: User is not logged in when attempting to like/comment/follow → prompted to authenticate (EC-003, Proposed).
- Completion State: User has engaged with content and/or received AI guidance.
- Traceability: idea.md § User Journeys — Target Journey steps 1–5, FEAT-002–006, BR-006, EC-003.

### Journey 2 — Chef Onboarding and Recipe Publishing
- Actor: Prospective/Verified Chef
- Trigger: A user chooses to register as a chef.
- Preconditions: None (open self-registration).
- Main Flow:
  1. User self-registers and selects/is routed to the chef onboarding path.
  2. User completes email verification.
  3. User uploads a culinary credential/certification document.
  4. Account enters "pending" state without publishing privileges.
  5. Admin manually reviews and approves the certificate.
  6. Chef privileges are granted; chef publishes a recipe (title, ingredients, steps, ≥1 photo).
  7. System runs an automated similarity check; if no differentiator is detected and similarity exceeds 95%, chef is prompted to review the matched recipe and provide a differentiation comment before publishing proceeds; otherwise the recipe auto-publishes.
- Alternate / Exception Flow: Admin rejects certificate (account remains non-chef); chef disputes a similarity-based hold → submits appeal → Admin manually reviews and approves/denies (BR-005, FR-015).
- Completion State: Recipe is published and visible in the feed, or chef receives rejection/appeal outcome.
- Traceability: idea.md § User Journeys, FEAT-011, BR-004, BR-005, BR-007, FR-013, FR-014, FR-015.

### Journey 3 — Chef Engagement Loop
- Actor: Creator Chef
- Trigger: Followers like/comment/follow, or chef publishes a new recipe.
- Preconditions: Chef account is approved (not pending).
- Main Flow:
  1. Chef receives notification of new likes/comments/follows (Should Have, FEAT-007).
  2. Chef responds to comments on their recipe.
  3. Chef publishes a new recipe; followers are notified.
- Alternate / Exception Flow: Notifications feature not yet built (Should Have, not Must Have) — chef must check profile/recipe directly for engagement in MVP if FEAT-007 is deferred within the release.
- Completion State: Chef sustains engagement with their follower base.
- Traceability: idea.md § User Journeys step 6–7, FEAT-007 (Should Have).

### Journey 4 — AI Cooking & Nutrition Conversation Beyond a Single Recipe
- Actor: Home Cook / Follower
- Trigger: User opens AI chat with a general cooking/nutrition question not tied to a specific recipe currently open.
- Preconditions: User has an account.
- Main Flow:
  1. User asks a general cooking or nutrition question (not restricted to a specific recipe, per BR-003).
  2. AI responds with an answer, disclaimer, and AI-disclosure notice.
  3. Conversation history is retained for 3 days by default.
  4. User may bookmark an individual AI response to retain it indefinitely.
- Alternate / Exception Flow: User asks a question entirely unrelated to cooking/nutrition/food topics → AI declines (EC-001).
- Completion State: User receives guidance; conversation is retained per retention policy or bookmarked.
- Traceability: BR-003, FR-007, FR-012, EC-001, BR-006.

## 7. Epics

### EPIC-001 — Chef Onboarding & Verification
- Objective: Enable trustworthy chef account creation gated by identity/credential verification.
- User / Persona: Creator Chef, Admin
- Business Value: Content integrity, trust & safety, organic cold-start supply of chefs (PG-004, PG-001).
- Related Product Goal: PG-001, PG-004
- Related Features: FEAT-011
- Priority: Must Have
- Dependencies: None upstream; blocks EPIC-002 (a recipe cannot be published without an approved chef account).

#### User Stories

##### US-001 — Self-Register as a Prospective Chef
**Story:** As a prospective chef, I want to self-register for a chef account, so that I can begin the process of becoming a verified content creator.

**Source / Traceability**
- Product Goal: PG-001, PG-004
- Journey: Journey 2
- Feature: FEAT-011
- Business Rules: BR-004, BR-007
- Functional Requirements: FR-001, FR-013

**Acceptance Criteria**
- AC-001: Given a new user on the registration page, when they choose to register as a chef, then the system creates an account with role "Chef (pending)" without publishing privileges.
- AC-002: Given a chef registration, when the account is created, then the user is prompted to complete email verification before proceeding.

**Priority:** Must

##### US-002 — Complete Email Verification and Certificate Upload
**Story:** As a prospective chef, I want to verify my email and upload my culinary credential/certification document, so that my account can be reviewed for chef privileges.

**Source / Traceability**
- Product Goal: PG-004
- Journey: Journey 2
- Feature: FEAT-011
- Business Rules: BR-007
- Functional Requirements: FR-013

**Acceptance Criteria**
- AC-003: Given an unverified chef account, when the user clicks the email verification link, then the account's email-verified flag is set to true.
- AC-004: Given a verified-email chef account, when the user uploads a culinary credential/certification document, then the account status is set to "pending Admin review."
- AC-005: Given a chef account in "pending" status, when the chef attempts to publish a recipe, then the system blocks publishing and communicates the pending status to the user.

**Edge / Exception Behaviour**
- EC-Ref: EC-004-related account-deletion behavior for pending chefs is not separately defined (Open Item, see § 20).

**Priority:** Must

##### US-003 — Admin Reviews and Approves/Rejects Chef Certificate
**Story:** As an Admin, I want to manually review an uploaded chef certificate, so that I can approve legitimate chefs and reject fraudulent or invalid submissions.

**Source / Traceability**
- Product Goal: PG-004
- Journey: Journey 2
- Feature: FEAT-011
- Business Rules: BR-007
- Functional Requirements: FR-013

**Acceptance Criteria**
- AC-006: Given a chef account in "pending Admin review" status, when the Admin approves the certificate, then the account status becomes "Chef (active)" and publishing privileges are granted.
- AC-007: Given a chef account in "pending Admin review" status, when the Admin rejects the certificate, then the account status becomes "Chef (rejected)" and the user is notified; the user does not gain publishing privileges.

**Priority:** Must

---

### EPIC-002 — Recipe Publishing & Zero-Plagiarism Enforcement
- Objective: Allow verified chefs to publish original recipes while protecting content originality.
- User / Persona: Creator Chef, Admin
- Business Value: Core content supply; platform trust and content integrity (PG-001, PG-004).
- Related Product Goal: PG-001, PG-004
- Related Features: FEAT-001
- Priority: Must Have
- Dependencies: EPIC-001 (chef must be approved).

#### User Stories

##### US-004 — Publish a New Recipe
**Story:** As a verified chef, I want to create and publish a recipe with ingredients, steps, and photos, so that followers and other users can discover and engage with it.

**Source / Traceability**
- Product Goal: PG-001
- Journey: Journey 2
- Feature: FEAT-001
- Business Rules: BR-001, BR-004
- Functional Requirements: FR-002

**Acceptance Criteria**
- AC-008: Given an approved chef account, when the chef submits a recipe with title, ingredients, steps, and at least one photo, then the recipe is created in a pre-publish state pending the similarity check (US-005).
- AC-009: Given a non-chef (regular) user, when they attempt to access the recipe-creation function, then the system denies access.
- AC-010: Given a recipe owned by Chef A, when Chef B (a different chef) attempts to edit or delete it, then the system denies the action (BR-001).

**Priority:** Must

##### US-005 — Automated Similarity Check Before Publishing
**Story:** As a verified chef, I want my submitted recipe to be automatically checked for similarity to existing recipes, so that original content is published without unnecessary friction while near-duplicate content is flagged.

**Source / Traceability**
- Product Goal: PG-004
- Journey: Journey 2
- Feature: FEAT-001
- Business Rules: BR-005
- Functional Requirements: FR-014

**Acceptance Criteria**
- AC-011: Given a submitted recipe, when the system detects a differentiator (method, ingredients, steps, or ingredient combination) relative to existing recipes, then the recipe is automatically published without manual review, regardless of similarity score.
- AC-012: Given a submitted recipe with similarity score exceeding 95% and no detected differentiator, when the check completes, then the chef is prompted to review the matched recipe and must provide a differentiation comment before the recipe can be published.
- AC-013: Given a submitted recipe with similarity score at or below 95%, when the check completes, then the recipe is published without requiring a differentiation comment.

**Edge / Exception Behaviour**
- EC-005(a): False-positive match — chef's differentiation comment is captured; if the chef disputes a resulting rejection/hold, the case proceeds to US-006 appeal.
- EC-005(b): Borderline similarity scoring / differentiator-detection accuracy is a Solution Architect concern (algorithm design not defined here).

**Priority:** Must

##### US-006 — Chef Appeals a Plagiarism-Similarity Rejection
**Story:** As a verified chef, I want to appeal a >95% similarity-match rejection/hold, so that a genuinely original recipe of mine is not unfairly blocked.

**Source / Traceability**
- Product Goal: PG-004
- Journey: Journea 2
- Feature: FEAT-001
- Business Rules: BR-005
- Functional Requirements: FR-015

**Acceptance Criteria**
- AC-014: Given a recipe held pending differentiation-comment review, when the chef disputes the outcome, then the chef can submit an appeal.
- AC-015: Given a submitted appeal, when an Admin reviews it, then the Admin can approve (recipe is published) or deny (recipe remains unpublished) the appeal, and the chef is notified of the outcome.

**Priority:** Must

---

### EPIC-003 — Social Engagement & Discovery
- Objective: Enable users to discover recipes and engage socially with chefs and content.
- User / Persona: Home Cook / Follower, Creator Chef
- Business Value: Core engagement/discovery driving retention (PG-002).
- Related Product Goal: PG-002, PG-006
- Related Features: FEAT-002, FEAT-003, FEAT-004, FEAT-005
- Priority: Must Have
- Dependencies: EPIC-002 (recipes must exist to engage with).

#### User Stories

##### US-007 — Browse Engagement-Ranked Feed
**Story:** As a home cook, I want to browse a feed of recipes ranked by engagement and from chefs I follow, so that I discover popular and relevant content.

**Source / Traceability**
- Product Goal: PG-002
- Journey: Journey 1
- Feature: FEAT-002
- Business Rules: BR-008
- Functional Requirements: FR-006

**Acceptance Criteria**
- AC-016: Given two published recipes with different combined like+comment counts, when the feed is rendered, then the recipe with the higher combined count ranks higher.
- AC-017: Given a user follows one or more chefs, when the feed is rendered, then recipes from followed chefs are represented in the feed in addition to engagement-ranked content.

**Priority:** Must

##### US-008 — Like a Recipe
**Story:** As a registered user, I want to like a recipe, so that I can show appreciation and influence its feed ranking.

**Source / Traceability**
- Product Goal: PG-002
- Feature: FEAT-003
- Business Rules: BR-002, BR-008
- Functional Requirements: FR-003

**Acceptance Criteria**
- AC-018: Given a logged-in user viewing a published recipe, when they tap "like," then the like is recorded once and the recipe's like count increments.
- AC-019: Given a user has already liked a recipe, when they tap "like" again, then the like is removed (toggle off) and the count decrements.
- AC-020: Given a user is not logged in, when they attempt to like a recipe, then they are prompted to authenticate (EC-003).

**Priority:** Must

##### US-009 — Comment on a Recipe
**Story:** As a registered user, I want to post and view comments on a recipe, so that I can engage with the chef and community.

**Source / Traceability**
- Product Goal: PG-002
- Feature: FEAT-004
- Business Rules: BR-002, BR-008
- Functional Requirements: FR-004

**Acceptance Criteria**
- AC-021: Given a logged-in user, when they post a comment on a published recipe, then the comment is visible on the recipe and the recipe's comment count increments.
- AC-022: Given a user's own comment, when they choose to delete it, then the comment is removed and the count decrements.
- AC-023: Given a user is not logged in, when they attempt to comment, then they are prompted to authenticate (EC-003).

**Priority:** Must

##### US-010 — Follow a Chef
**Story:** As a registered user, I want to follow a chef, so that their recipes are represented in my feed and I can stay updated on their new content.

**Source / Traceability**
- Product Goal: PG-001, PG-002
- Feature: FEAT-005
- Business Rules: BR-002
- Functional Requirements: FR-005

**Acceptance Criteria**
- AC-024: Given a logged-in user viewing a chef's profile or recipe, when they tap "follow," then the chef is added to the user's followed list.
- AC-025: Given a user follows a chef, when they tap "unfollow," then the chef is removed from the user's followed list.

**Priority:** Must

---

### EPIC-004 — AI Cooking & Nutrition Assistant
- Objective: Provide a conversational AI assistant for cooking and nutrition guidance, both recipe-scoped and general.
- User / Persona: Home Cook / Follower
- Business Value: Key product differentiator (PG-003).
- Related Product Goal: PG-003
- Related Features: FEAT-006
- Priority: Must Have
- Dependencies: Local LLM infrastructure (CON-003) — Solution Architect concern.

#### User Stories

##### US-011 — Ask the AI Assistant About the Current Recipe
**Story:** As a home cook viewing a recipe, I want to ask the AI assistant questions about that recipe (e.g., substitutions, technique, scaling), so that I get contextual help while cooking.

**Source / Traceability**
- Product Goal: PG-003
- Journey: Journey 1, Journey 4
- Feature: FEAT-006
- Business Rules: BR-003, BR-006
- Functional Requirements: FR-007, FR-011

**Acceptance Criteria**
- AC-026: Given a user viewing a recipe, when they open the AI chat and ask a question about that recipe, then the AI responds with an answer relevant to the recipe's context.
- AC-027: Given any AI response, when it is displayed, then it includes a visible disclaimer and an AI-disclosure notice (BR-006).

**Priority:** Must

##### US-012 — Ask the AI Assistant General Cooking/Nutrition Questions
**Story:** As a home cook, I want to ask the AI assistant general cooking and nutrition questions not tied to a specific recipe, so that I can get broader culinary guidance.

**Source / Traceability**
- Product Goal: PG-003
- Journey: Journey 4
- Feature: FEAT-006
- Business Rules: BR-003, BR-006
- Functional Requirements: FR-007, FR-011

**Acceptance Criteria**
- AC-028: Given a user opens the AI chat without an active recipe context (or asks a question unrelated to the current recipe), when they submit a general cooking or nutrition question, then the AI responds (with disclaimer + disclosure notice).
- AC-029: Given a user asks a question entirely unrelated to cooking/nutrition/food topics, when submitted, then the AI declines to answer and indicates the topic is out of scope (EC-001).

**Priority:** Must

##### US-013 — AI Conversation Retention and Bookmarking
**Story:** As a user of the AI assistant, I want my conversation history retained for a limited time, with the option to bookmark specific responses indefinitely, so that I can revisit useful guidance without unbounded data retention.

**Source / Traceability**
- Product Goal: PG-003
- Journey: Journey 4
- Feature: FEAT-006
- Functional Requirements: FR-012

**Acceptance Criteria**
- AC-030: Given an AI conversation, when 3 days have elapsed since a message was generated, then that message is automatically expired/removed from history, unless bookmarked.
- AC-031: Given an AI response, when the user bookmarks it, then it remains accessible indefinitely (or until the user removes the bookmark) regardless of the 3-day retention window.

**Priority:** Must

---

### EPIC-005 (Should Have) — Notifications, Chef Analytics, Search, Moderation
- Objective: Support engagement, creator retention, discovery, and trust & safety beyond MVP core.
- User / Persona: All
- Business Value: Retention, creator satisfaction, discoverability, safety (PG-002, PG-004).
- Related Product Goal: PG-002, PG-004
- Related Features: FEAT-007, FEAT-008, FEAT-009, FEAT-010
- Priority: Should Have
- Dependencies: EPIC-002, EPIC-003.

#### User Stories

##### US-014 — Receive Notifications of Engagement
**Story:** As a chef, I want to be notified when my recipe receives a like, comment, or new follower, so that I can respond and stay engaged with my audience.

**Source / Traceability**
- Feature: FEAT-007
- Functional Requirements: FR-008

**Acceptance Criteria**
- AC-032: Given a chef's recipe receives a new like, comment, or follow, when the event occurs, then the chef receives a notification referencing the event.

**Priority:** Should

##### US-015 — View Chef Profile and Basic Analytics
**Story:** As a chef, I want a public profile and basic engagement analytics, so that I can showcase my content and understand my audience.

**Source / Traceability**
- Feature: FEAT-008

**Acceptance Criteria**
- AC-033: Given a chef account, when another user visits the chef's profile, then published recipes, follower count, and basic identity information are displayed.
- AC-034: Given a chef account, when the chef views their own analytics, then aggregate like/comment/follower metrics for their recipes are displayed.

**Priority:** Should

##### US-016 — Search Recipes
**Story:** As a home cook, I want to search recipes by keyword, ingredient, cuisine, or diet, so that I can find recipes matching my needs.

**Source / Traceability**
- Feature: FEAT-009
- Functional Requirements: FR-009

**Acceptance Criteria**
- AC-035: Given a search query matching recipe title/ingredient/cuisine/diet tags, when submitted, then matching published recipes are returned.

**Priority:** Should

##### US-017 — Report Inappropriate Content
**Story:** As a user, I want to report an inappropriate recipe or comment, so that Admins can review and moderate it.

**Source / Traceability**
- Feature: FEAT-010
- Functional Requirements: FR-010

**Acceptance Criteria**
- AC-036: Given a user views a recipe or comment, when they submit a report with a reason, then the report is logged for Admin review.
- AC-037: Given a reported item, when an Admin reviews it, then the Admin can remove the content, warn/ban the account, or dismiss the report.

**Edge / Exception Behaviour**
- EC-006: Escalation path beyond initial report/hide is Proposed and not fully defined (see § 20).

**Priority:** Should

## 8. Functional Requirements

| ID | Requirement | Actor / Scope | Related Story | Business Rule | Status |
|---|---|---|---|---|---|
| FR-001 | Users shall register and create an account, selecting/being assigned role Chef or Regular User | All | US-001 | BR-004 | Confirmed |
| FR-002 | Only chef-role accounts may create/edit/delete recipes with title, ingredients, steps, ≥1 photo | Chef | US-004 | BR-001, BR-004 | Confirmed |
| FR-003 | Users may like a published recipe once, toggleable | Regular User, Chef | US-008 | BR-002, BR-008 | Confirmed |
| FR-004 | Users may post, view, delete their own comments on a recipe | Regular User, Chef | US-009 | BR-002 | Confirmed |
| FR-005 | Users may follow/unfollow a chef | Regular User, Chef | US-010 | BR-002 | Confirmed |
| FR-006 | System displays feed ranked by engagement (likes+comments), plus followed-chef content | All | US-007 | BR-008 | Confirmed |
| FR-007 | Users may open an AI chat that discusses the current recipe and general cooking/nutrition topics | Regular User, Chef | US-011, US-012 | BR-003 | Confirmed |
| FR-008 | System notifies chefs of new likes, comments, follows | Chef | US-014 | — | Proposed (Should Have) |
| FR-009 | System allows keyword search of recipes | All | US-016 | — | Proposed (Should Have) |
| FR-010 | System allows users to report inappropriate content/comments | All | US-017 | — | Proposed (Should Have) |
| FR-011 | Every AI response displays a disclaimer and AI-disclosure notice | All (AI users) | US-011, US-012 | BR-006 | Confirmed |
| FR-012 | AI conversation history retained 3 days by default; bookmarked responses retained indefinitely | All (AI users) | US-013 | — | Confirmed |
| FR-013 | Prospective chefs self-register; require email verification + certificate upload; account "pending" until Admin approval | Chef, Admin | US-001, US-002, US-003 | BR-007 | Confirmed |
| FR-014 | Automated similarity check before publish; >95% similarity with no differentiator triggers mandatory differentiation comment; differentiated recipes auto-publish | Chef | US-005 | BR-005 | Confirmed |
| FR-015 | Chef may appeal a similarity-based rejection/hold; Admin manually approves/denies | Chef, Admin | US-006 | BR-005 | Confirmed |
| FR-016 | System computes and stores aggregate like/comment counts per recipe to drive feed ranking | All | US-007 | BR-008 | Confirmed (inherited, idea.md § Business Data Needs) |

## 9. Business Rules

| ID | Rule | Applies To | Related Story / Requirement | Status |
|---|---|---|---|---|
| BR-001 | Only the recipe's original chef (owner) can edit/delete that recipe | Recipe Publishing | US-004, FR-002 | Confirmed |
| BR-002 | A user must have an account to like/comment/follow | Social features | US-008, US-009, US-010 | Confirmed |
| BR-003 | The AI agent acts as a general cooking assistant and nutritionist, not restricted to the currently viewed recipe | AI Agent | US-011, US-012, FR-007 | Confirmed |
| BR-004 | "Chef" is a distinct, verified account role; only chefs may publish recipes | Account types | US-001, FR-001, FR-002 | Confirmed |
| BR-005 | Zero-plagiarism policy: automated similarity check; >95% with no differentiator triggers mandatory differentiation comment; auto-accept when differentiator detected; disputed rejections go to Admin appeal | Recipe Publishing | US-005, US-006, FR-014, FR-015 | Confirmed |
| BR-006 | Every AI output must display a disclaimer and AI-disclosure notice | AI Agent | US-011, US-012, FR-011 | Confirmed |
| BR-007 | Chef applicants must complete email verification and certificate upload; account remains pending until Admin approves | Onboarding | US-002, US-003, FR-013 | Confirmed |
| BR-008 | Feed ranking is based on engagement (likes + comments) | Feed & Discovery | US-007, FR-006 | Confirmed |

## 10. Roles and Permissions

| Role | Allowed Actions | Restricted Actions | Approval / Ownership Rules |
|---|---|---|---|
| Chef (verified) | Publish/edit/delete own recipes; respond to comments; view own analytics (Should Have); like/comment/follow as any user can | Cannot edit other chefs' recipes; cannot publish while "pending" | Self-registers; requires email verification + certificate upload; Admin approval required before publishing privileges granted (BR-007, FR-013) |
| Regular User / Follower | Like, comment, follow, use AI agent, report content | Cannot publish recipes | N/A |
| Admin | Approve/reject chef certificates (BR-007, FR-013); approve/deny plagiarism appeals (BR-005, FR-015); remove content; ban/suspend accounts; resolve reports | N/A | Platform-level authority; broader moderation tooling scope beyond the two confirmed workflows is an Assumption (ASM-012) |

Traceability: idea.md § Roles and Permissions.

## 11. Business Data Requirements

| Business Information / Record | Purpose | Actor | Sensitivity / Retention Requirement | Source of Record if Known |
|---|---|---|---|---|
| Recipe data (title, ingredients, quantities/units, steps, photos/video, prep/cook time, servings, cuisine/diet tags, nutrition info) | Core content | Chef | Standard; nutrition info is Assumption | Chef-submitted |
| User/account data (profile, role, chef verification status, followed chefs, liked recipes, comment history) | Identity, permissions, personalization | All | Standard account data | User-submitted / system-derived |
| Social interaction data (likes, comments, follows, notifications, aggregate counts) | Feed ranking, engagement, notifications | All | Standard; aggregate counts feed BR-008 | System-generated |
| AI conversation data (chat history, bookmarks, disclaimer/disclosure metadata) | Conversational context, retention/bookmarking, audit | Regular User, Chef | 3-day default retention; bookmarked items indefinite; each response must carry disclaimer/disclosure metadata | System-generated |
| Chef onboarding data (uploaded certificate, Admin review status) | Trust & safety gate | Chef, Admin | Sensitive (identity/credential document); document storage/verification mechanics are Solution Architect decision | Chef-submitted / Admin-reviewed |
| Plagiarism appeal data (differentiation comment, appeal request, Admin decision + rationale) | Dispute resolution, audit trail | Chef, Admin | Standard; underlying similarity algorithm is Solution Architect decision | Chef-submitted / Admin-reviewed |
| Recipe similarity/plagiarism check data (similarity score, detected differentiators, differentiation comment) | Zero-plagiarism enforcement | System, Chef | Standard; algorithm/mechanism not defined here (Solution Architect) | System-generated |
| Reporting/moderation data (flagged content records) | Trust & safety | All, Admin | Standard | User-submitted / Assumption |

## 12. External Systems and Product Dependencies

| System / Dependency | Business Purpose | Information / Outcome Exchanged | Criticality | Expected Product Behaviour if Unavailable |
|---|---|---|---|---|
| Local LLM Studio (self-hosted, Qwen3.8-27B) | Powers AI Cooking & Nutrition Assistant | Recipe/conversation content in; conversational answer out | Critical for FEAT-006 (PG-003) | *(Proposed, Open Item)* Product should degrade gracefully — AI chat unavailable message displayed rather than app-wide failure; exact fallback behavior not yet defined (see § 20) |
| *(Assumption)* Media storage/CDN | Store/serve recipe photos and videos | Media upload/delivery | Critical for FEAT-001 | Not defined; Solution Architect concern |
| *(Assumption)* Push/email notification service | Deliver notifications (FEAT-007, email verification) | Notification triggers/content | Important for FR-008, FR-013 (email verification) | Not defined; Solution Architect concern |
| *(Assumption)* Payment processor | Contingent on future monetization model | Payment transactions | Not applicable to MVP (ads-only) | Not Applicable — no payment integration in MVP |

Note: Aside from the confirmed local LLM choice, no other vendor/technology has been mandated by the stakeholder. Selection of remaining integrations is a Solution Architect responsibility.

## 13. Non-Functional Requirements

| ID | Category | Requirement / Target | Scope | Source |
|---|---|---|---|---|
| NFR-001 | Performance | **Confirmed (requester-approved 2026-08-29):** AI assistant shall respond within 30 seconds for 95% of typical queries, and within 45 seconds for 99% of queries, accounting for local/self-hosted LLM (Qwen3.8-27B) inference capacity constraints. | AI Cooking & Nutrition Assistant | Requester decision, supersedes PM-proposed 8s/15s draft; idea.md NFR-001 (Open Question, now resolved) |
| NFR-002 | Platform | MVP targets Web only; native mobile apps are Future Enhancement | All | Confirmed, idea.md NFR-002 |
| NFR-003 | Scalability | System must support initial scale sufficient for Q1 targets (100 active users, 1,000 recipes); concurrent-usage capacity planning for local LLM inference is a Solution Architect concern | AI Assistant, overall platform | Confirmed target scale; capacity planning Open Item, idea.md NFR-003 |
| NFR-004 | Compliance | Region-specific regulatory compliance (GDPR, food-safety/advertising regulation) explicitly out of scope for MVP; accepted risk | Global market | Confirmed, idea.md NFR-004, RISK-006, ASM-007 |
| NFR-005 | Accessibility | **Confirmed (requester-approved 2026-08-29):** MVP shall target WCAG 2.1 Level AA conformance for core user-facing web flows (registration, feed, recipe view, AI chat). | Web platform | Requester decision; idea.md NFR-005 (Open Question, now resolved) |
| NFR-006 | Transparency/Compliance-adjacent | Every AI output must include a disclaimer and AI-disclosure notice | AI Assistant | Confirmed, idea.md NFR-006, BR-006, FR-011 |
| NFR-007 | Infrastructure (context only, not a product requirement to design) | AI Assistant runs on self-hosted local inference (Local LLM Studio, Qwen3.8-27B); no external API dependency or per-token cost, but requires local compute/hosting infrastructure | AI Assistant | Confirmed, idea.md NFR-007, CON-003 |

## 14. Edge Cases and Exception Behaviour

| ID | Scenario | Trigger | Expected Behaviour | Recovery / Escalation | Related Story / Requirement |
|---|---|---|---|---|---|
| EC-001 | AI asked an off-topic question unrelated to cooking/nutrition/food | User submits unrelated query | AI declines to answer, indicating the topic is out of scope | N/A | US-012, BR-003 |
| EC-002 | Food-safety/nutrition-sensitive AI question | User asks sensitive question | AI response includes disclaimer + AI-disclosure notice; not presented as authoritative professional advice | N/A | US-011, US-012, BR-006 |
| EC-003 | Unauthenticated user attempts to like/comment/follow | Action attempted while logged out | User is prompted to authenticate | User logs in/registers, then retries action | US-008, US-009, US-010 |
| EC-004 (Open Item) | Chef deletes their account | Chef initiates account deletion | **Not yet defined** — behavior for existing recipes, comments, and followers is an open product decision (removed, archived, or retained/orphaned) | Pending requester decision | § 20 Open Questions |
| EC-005(a) | False-positive plagiarism match | Similarity check flags >95% with no differentiator, but chef believes recipe is original | Chef provides differentiation comment; may appeal if rejected/held; Admin reviews appeal | Admin approves/denies appeal | US-005, US-006, BR-005 |
| EC-005(b) | Borderline similarity scoring / differentiator-detection false positive/negative | Algorithm edge case | Not defined here — Solution Architect concern for similarity-detection mechanism design | Solution Architect design | US-005 |
| EC-006 (Proposed, Open Item) | Abusive/spam comments | User reports or content is flagged | Content should be reportable and hideable; **escalation path to Admin/moderator beyond initial report is not fully defined** | Pending further PM/requester definition | US-017, FEAT-010 |

## 15. Product Analytics and Measurement Requirements

| ID | What Must Be Measurable | Why | Related Metric / Goal | Actor / Journey |
|---|---|---|---|---|
| AN-001 | Distinct-account activity events (recipe view, like, comment, follow, recipe publish, AI message sent) attributable to a user and timestamped | Compute Active Users (MET-001) per Proposed operational definition | MET-001, PG-001, PG-006 | All |
| AN-002 | Count of recipes successfully published (post similarity-check resolution) | Compute Recipes Shared (MET-002) | MET-002, PG-001, PG-006 | Chef |
| AN-003 | Per-recipe like count and comment count over time | Feed ranking (BR-008) and engagement metric (MET-003) | MET-003, PG-002 | All |
| AN-004 | Chef certificate submission timestamp and Admin decision timestamp | Measure Admin review turnaround (MET-004) | MET-004, PG-004 | Admin |
| AN-005 | Plagiarism appeal submission timestamp and Admin decision timestamp | Measure appeal resolution time (MET-005) | MET-005, PG-004 | Admin |
| AN-006 | AI conversation message count, response latency, and disclaimer/disclosure display confirmation | Measure AI feature usage and NFR-001 compliance | NFR-001, PG-003 | All (AI users) |

## 16. Constraints

| ID | Constraint | Impact on Product | Source |
|---|---|---|---|
| CON-001 | **Confirmed (requester-approved 2026-08-29):** Budget/timeline for the confirmed MVP Must-Have scope is **~12–16 weeks calendar time, ~600–800 total person-hours, delivered by a small team of 2–3 developers (backend/full-stack + frontend, plus part-time design/PM support), at an estimated cost of ~$30,000–$60,000 USD** (assuming a blended contractor/freelance rate of ~$50/hr; scale up or down based on actual team composition/location/rates). This figure replaces the requester's originally stated $200 / 5 workman-hours, which was assessed as infeasible for the documented scope (RISK-009, now resolved). This is a PM-level sizing estimate for planning purposes; Engineering Lead/Solution Architect should refine it once technical design is complete. **A phased/reduced-scope alternative (~6–8 weeks / ~250–350 person-hours / ~$12,500–$17,500, deferring the AI Assistant and Should-Have items, simplifying the plagiarism check) was considered but not selected by the requester** — retained here for historical traceability only, not as a live option. | Provides Engineering Lead/Solution Architect a requester-approved realistic planning baseline for the full confirmed MVP scope. | Requester decision (2026-08-29); supersedes idea.md CON-001 and the original $200/5-hour figure |
| CON-002 | MVP targets Web only; native mobile deferred | Scope boundary for this release | Confirmed, idea.md CON-002 |
| CON-003 | AI feature must run on self-hosted local LLM (Qwen3.8-27B via Local LLM Studio), not a third-party cloud API | Stakeholder-mandated technology constraint; affects NFR-001, NFR-003, RISK-005 | Confirmed, idea.md CON-003 |
| CON-004 | Region-specific legal/regulatory compliance is explicitly out of scope for MVP | Accepted risk; no compliance work required this release | Confirmed, idea.md CON-004, RISK-006 |
| CON-005 (Open Item) | Team size/composition and existing technical assets are unknown | Non-blocking; addressed at planning/Solution Architecture stage | idea.md CON-005 |

## 17. Assumptions

| ID | Assumption | Validation Needed | Consequence if False | Owner |
|---|---|---|---|---|
| ASM-007 | Global launch without region-specific compliance work will not create material legal exposure during the MVP period | Legal review recommended before scaling beyond MVP | Legal/regulatory exposure in specific markets | Requester (accepted risk) |
| ASM-009 | Budget and timeline remain undefined and are assumed to be addressed in later Solution Architect/planning stages | Requester to confirm budget/timeline | Planning/resourcing risk | Requester/Engineering |
| ASM-010 | Local LLM (Qwen3.8-27B) will provide sufficient response quality and latency for the general cooking/nutrition assistant use case at target Q1 scale | Solution Architect/engineering benchmarking before/at build time | AI feature quality/UX may suffer, undermining PG-003 | Requester/Engineering |
| ASM-012 | Self-registration-only chef onboarding combined with Admin manual review remains operationally manageable at Q1 target scale | PM to plan Admin staffing/tooling as volume grows | Admin review bottleneck (RISK-007, RISK-008) | Requester/PM |
| ASM-013 | ~~The Proposed "Active User" operational definition (MAU, defined actions) is an acceptable measurement standard for MET-001~~ **Resolved — now Confirmed by requester (2026-08-29)** | Resolved | N/A | Requester |
| ASM-014 | ~~The Proposed NFR-001 and NFR-005 targets are acceptable quality bars for MVP~~ **Resolved — now Confirmed by requester (2026-08-29)**: NFR-001 set at 30s/95th, 45s/99th percentile (requester-adjusted from PM's initial 8s/15s draft); NFR-005 confirmed at WCAG 2.1 AA as proposed | Resolved | N/A | Requester |
| ASM-015 | ~~The requester's stated $200 / 5 workman-hour budget-timeline constraint (CON-001) is assumed to be intentional and accurately stated~~ **Resolved:** requester approved the PM-recommended replacement figure (~12–16 weeks / ~600–800 hrs / ~$30,000–$60,000) on 2026-08-29; now Confirmed in CON-001 | Resolved | N/A | Requester |

## 18. Risks

| ID | Risk | Impact | Likelihood | Product Response / Mitigation | Owner |
|---|---|---|---|---|---|
| RISK-001 | AI agent gives incorrect/unsafe cooking/nutrition/food-safety advice | High | Medium | Mandatory disclaimer + AI-disclosure notice on every AI response (BR-006, FR-011, NFR-006) | TBD |
| RISK-002 | Cold-start: reliance solely on organic self-registration for chef supply | High | Medium–High | Open self-registration via email + certificate + Admin approval (FEAT-011); no additional curated outreach planned for MVP | TBD |
| RISK-003 | Content moderation burden grows faster than moderation capability; Admin bears manual review load | Medium | Medium | Reporting tools (FEAT-010), community guidelines, moderation team; monitor Admin queue volume | TBD |
| RISK-004 | Ad revenue may be insufficient to sustain operations (monetization model itself is resolved as ads-only) | Medium | Medium | Monitor ad performance; revisit monetization model post-MVP if needed | TBD |
| RISK-005 | Local self-hosted LLM infrastructure costs/capacity may be significant at scale; model capability may lag cloud frontier models | Medium–High | Medium | Capacity planning for local compute/hosting, usage limits, Solution Architect evaluation of model quality vs. scope needs | TBD |
| RISK-006 | Operating globally without region-specific compliance for MVP | Medium–High | Medium | Accepted risk for MVP per requester decision; revisit post-MVP before scaling in regulated markets | Requester (accepted) |
| RISK-007 | Chef verification could be circumvented by forged documents, create onboarding friction, or create Admin review bottleneck | Medium | Medium | Admin manual review/approval gate (BR-007, FR-013); Admin staffing/tooling capacity is a non-blocking open item for PM | TBD |
| RISK-008 | Similarity check produces false positives/negatives; Admin appeal review could become a bottleneck at scale | Medium | Medium | Admin-reviewed appeal path (BR-005, FR-015); similarity-detection accuracy and appeal-queue capacity are Solution Architect/PM concerns | TBD |
| RISK-009 (Resolved) | **Scope-feasibility mismatch — Resolved (requester-approved 2026-08-29):** The requester's originally stated budget/timeline constraint ($200 / 5 workman-hours total) was grossly insufficient to build the confirmed MVP scope. The requester has since reviewed and **approved** the PM-recommended realistic budget/timeline of **~12–16 weeks, ~600–800 person-hours, ~$30,000–$60,000** (CON-001), which is now `Confirmed`. This risk is no longer an open blocker. **Residual note:** ~$30,000–$60,000 remains a lean budget for the full scope (multi-role platform, chef verification, zero-plagiarism detection, self-hosted AI assistant); delivery risk (scope creep, underestimation, local LLM infrastructure surprises) should continue to be monitored during execution by Engineering Lead/Solution Architect, but this is now a standard execution-risk-management concern rather than an open feasibility gap. | Low (residual monitoring only) | Low–Medium (standard delivery risk) | Confirmed budget/timeline (CON-001) adopted; Engineering Lead/Solution Architect to monitor actual burn against this baseline during execution and flag early if scope or infrastructure costs threaten to exceed it | Requester (approved) / Engineering Lead (execution monitoring) |

## 19. Product Dependencies and Sequencing

1. EPIC-001 (Chef Onboarding & Verification) must be functionally available before EPIC-002 (Recipe Publishing) can produce content, since only Admin-approved chefs may publish.
2. EPIC-002 (Recipe Publishing) must produce published recipes before EPIC-003 (Social Engagement & Discovery) has content to rank, like, comment on, or follow around.
3. EPIC-004 (AI Cooking & Nutrition Assistant) can be developed in parallel with EPIC-001–003 but requires recipe content (EPIC-002) to fully exercise recipe-scoped conversations (US-011); general-assistant conversations (US-012) do not require recipe content to function.
4. EPIC-005 (Should Have: Notifications, Analytics, Search, Moderation) depends on EPIC-002 and EPIC-003 producing content and engagement events to notify on, analyze, search, or moderate.
5. All epics target Web platform only per CON-002; no mobile-specific sequencing applies in this release.

Status: PM Derived from confirmed epic dependencies; no engineering estimates or sprint plans included.

## 20. Open Questions and Pending Decisions

The four items previously listed here (Active User definition, AI response-time NFR-001, accessibility NFR-005, budget/timeline CON-001) were reviewed and resolved by the requester on 2026-08-29 and are now `Confirmed` throughout this PRD (see § 2, § 13, § 16). They are removed from this table. **Note:** resolving CON-001 introduced a new, explicitly flagged feasibility concern — see RISK-009 in § 18, which remains an open decision point (scope reduction vs. constraint revision) but does not block Solution Architecture handoff, per requester direction that the constraint stands as stated pending further review.

| Question / Decision | Why It Matters | Owner | Architecture Blocking? | Required By |
|---|---|---|---|---|
| Chef account deletion behavior for existing recipes/comments/followers (EC-004) | Determines data retention/orphaning product behavior | Requester | No (non-blocking, but should be resolved before EPIC-001/002 detailed design) | Before detailed design of account deletion flow |
| Moderation escalation path beyond initial report/hide (EC-006) | Trust & safety completeness for FEAT-010 (Should Have) | Requester/PM | No | Before FEAT-010 detailed design |
| AI assistant fallback behavior if local LLM infrastructure is unavailable | User experience continuity | Requester/PM/Solution Architect | No (non-blocking, but recommended before launch) | Before launch readiness review |
| Additional persona types (e.g., Restaurant/Brand account) | Scope of role model | Requester | No — currently Out of Scope by default | If raised by requester |
| **Approval of PM-recommended budget/timeline for CON-001 (~12–16 weeks / ~600–800 person-hours / ~$30,000–$60,000), replacing the original $200/5-hour figure** | RISK-009 flagged the original constraint as infeasible; a realistic planning baseline is needed before Engineering Lead/Solution Architect can plan implementation | Requester | No (Solution Architecture may proceed with scope/design work), but **strongly recommended to resolve before implementation/estimation planning and resourcing begins** | Before implementation/estimation planning |

All items above are explicitly non-blocking for Solution Architecture handoff, consistent with idea.md § Open Questions and § Notes. RISK-009 is a material feasibility concern flagged for requester and downstream Engineering Lead awareness, distinct from a PRD-blocking gap.

## 21. Traceability Summary

| Product Goal | Epic | User Story | FR / BR | Success Metric |
|---|---|---|---|---|
| PG-001 | EPIC-001 | US-001, US-002, US-003 | FR-001, FR-013, BR-004, BR-007 | MET-001, MET-002 |
| PG-004 | EPIC-001, EPIC-002 | US-001–US-006 | FR-013, FR-014, FR-015, BR-005, BR-007 | MET-004, MET-005 |
| PG-001, PG-002 | EPIC-003 | US-007–US-010 | FR-003, FR-004, FR-005, FR-006, FR-016, BR-002, BR-008 | MET-002, MET-003 |
| PG-003 | EPIC-004 | US-011, US-012, US-013 | FR-007, FR-011, FR-012, BR-003, BR-006 | MET-001 (usage contributes to activity definition) |
| PG-002, PG-004 | EPIC-005 (Should Have) | US-014–US-017 | FR-008, FR-009, FR-010 | MET-003 |
| PG-005 | (Not epic-decomposed — business model, not a user-facing epic) | N/A | § Business Model (ads-only monetization) | Not directly metered in MVP; ad performance tracking is a future/operational concern |
| PG-006 | All Must-Have epics | All Must-Have stories | All Must-Have FR/BR | MET-001, MET-002 |

## 22. Glossary
- **Chef**: A verified/authenticated account role (self-registration + email verification + culinary credential/certification document + Admin approval required) that is the only role permitted to publish recipes.
- **Regular User / Home Cook / Follower**: A user who consumes content, engages socially, and may use the AI agent, but cannot publish recipes.
- **Admin**: A platform-level role that manually reviews/approves chef certificates and plagiarism appeals; holds general content moderation authority.
- **AI Cooking & Nutrition Assistant**: A conversational AI feature, running on a self-hosted local LLM (Local LLM Studio, Qwen3.8-27B), that discusses the recipe being viewed as well as general cooking and nutrition topics.
- **Zero-Plagiarism Policy**: The confirmed business rule (BR-005) requiring an automated similarity check before publish, with a >95%-similarity/no-differentiator gate triggering mandatory chef differentiation commentary and an Admin-reviewed appeal path.
- **MVP**: Minimum Viable Product — the initial Must-Have release scope, targeting Web only.
- **Active User**: Per Proposed operational definition (§ 2), an account performing at least one defined engagement action within a calendar month; measured as Monthly Active Users (MAU). Pending requester confirmation.
