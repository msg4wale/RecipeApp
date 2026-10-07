# Product Idea

## Document Status
- Discovery Status: Core Decisions Confirmed — Minor Non-Blocking Items Remain
- Last Updated: 2026-08-29 (updated after requester answered open questions)
- Stakeholder Approval: Requester has confirmed key decisions (roles, AI scope, platform, monetization, disclaimers, market/compliance stance, success metrics, AI history retention). Full document re-review still recommended.
- PRD Readiness: **Ready, with minor non-blocking items noted** — all previously PRD-blocking open questions have been resolved by the requester, including AI infrastructure choice (local LLM), chef verification mechanism (email + certificate + Admin approval), plagiarism policy and appeal path (Admin-reviewed), cold-start strategy (open self-registration), and feed ranking logic (engagement-based). Remaining open items (budget/timeline, AI response-time target, accessibility level, "active user" definition) are explicitly non-blocking and may be carried into Product Manager / Solution Architect stages.

## Executive Summary
A social recipe-sharing platform where chefs publish recipes and build a following, users discover recipes through liking, commenting, and following chefs, and an AI agent feature lets users have a conversational Q&A experience about specific recipes (e.g., substitutions, techniques, scaling, dietary adaptations). The product blends social-network mechanics with content publishing and a conversational AI assistant layered on recipe content.

Because the requester provided only a one-sentence brief and no live interview was possible in this session, this idea.md documents confirmed facts (minimal), reasonable proposed scope, and — critically — a full set of labeled assumptions that must be validated with the requester before a PRD is created.

## Problem Statement

### Problem
*(Assumption — not yet confirmed by requester)* Home cooks and food enthusiasts struggle to find trustworthy, engaging recipe content and lack an easy way to get personalized guidance (substitutions, technique clarification, scaling) while cooking. Independent/aspiring chefs and food creators lack an easy platform to build an audience and monetize their recipe content compared to generic social platforms.

### Affected Users or Business Groups
- Home cooks / recipe consumers (primary users)
- Independent chefs, food creators, and influencers (content creators)
- *(Assumption)* Possibly professional chefs/restaurants seeking brand promotion

### Current Approach
*(Assumption)* Users currently rely on generic social media (Instagram, TikTok, Pinterest), recipe blogs, and general search engines/cooking assistants (e.g., generic ChatGPT) which are not tailored to a specific recipe's context or a creator-fan relationship.

### Evidence and Impact
No market data, user research, or business case has been supplied by the requester. **Open Question / PRD-blocking**: what evidence (market research, competitor analysis, personal pain point) motivates this idea?

### Why Current Approaches Are Insufficient
*(Assumption)* Generic social platforms are not optimized for recipe discovery/structure (ingredients, steps, nutrition) or creator-fan cooking interaction; generic AI chat assistants aren't grounded in a specific creator's recipe and voice.

## Vision
*(Proposed)* "Become the go-to social platform where food creators build engaged communities around their recipes, and every recipe comes with an AI cooking companion that helps users succeed in the kitchen."

## Business Goals
*(Proposed — unconfirmed)*
- Grow an engaged base of recipe creators ("chefs") and followers.
- Increase user engagement/retention via social features (likes, comments, follows).
- Differentiate via AI-assisted recipe conversation as a unique value proposition.
- *(Open Question)* Monetization goal — is this a free community product, ad-supported, subscription (creator monetization / premium AI features), or something else?

## Stakeholders
| Stakeholder / Role | Responsibilities | Expectations | Decision Ownership |
|---|---|---|---|
| Requester / Business Owner | Overall product vision, budget, priorities | Deliver a viable social recipe app with AI feature | Final decision owner (unconfirmed identity/role) |
| Chefs / Content Creators | Publish recipes, engage with followers | Tools to grow audience, possibly monetize | Content ownership |
| End Users / Home Cooks | Consume content, socially engage, use AI agent | Easy discovery, trustworthy recipes, helpful AI | N/A |
| *(Assumption)* Platform Moderation Team | Content/community moderation | Safe, spam-free platform | TBD |
| *(Assumption)* Legal/Compliance | Ensure AI response safety (e.g., food safety/allergen liability), data privacy | Avoid legal exposure | TBD |

**Open Question (PRD-blocking):** Who is the actual business decision owner reachable for follow-up discovery? No stakeholder interview was possible in this session.

## Target Users

### Persona 1 — "Creator Chef"
- Description: An individual (professional or amateur) who creates and shares original recipes.
- Context of Use: Uploads recipes with photos/video, engages with followers' comments, wants an audience.
- Goals: Build following, showcase cooking identity, *(assumption)* monetize content.
- Pain Points: Discovery/visibility, engagement management, time to interact with every follower question (motivates AI agent).
- Current Workflow: *(Assumption)* Currently posts on Instagram/TikTok/YouTube/blogs.
- Access / Permission Needs: Can create/edit/delete own recipes, view own analytics, moderate comments on own content.

### Persona 2 — "Home Cook / Follower"
- Description: A user who follows chefs, browses/searches recipes, engages socially, and cooks along.
- Context of Use: Browses feed, likes/comments/follows, opens a recipe while cooking and asks the AI agent questions.
- Goals: Find good recipes, get help while cooking, connect with favorite creators.
- Pain Points: Recipe fits dietary restriction? Ingredient substitution? Technique clarification mid-cook.
- Current Workflow: *(Assumption)* Searches recipe blogs/social media/generic AI chat.
- Access / Permission Needs: Like, comment, follow, converse with AI agent; cannot edit others' recipes.

**Open Question:** Are there other personas — e.g., a "Restaurant/Brand" account type, or an "Admin/Moderator" internal role — that should be modeled explicitly? Not confirmed.

## Business Model and Value
**Confirmed:** The app is free for all users (chefs and followers). Monetization is via advertising. No subscription tiers, creator payouts/tipping, or paywalled premium features are in scope for MVP. *(Proposed, non-blocking)* Ad placement/format and ad-tech vendor selection are not yet defined and can be addressed by Product Management/Solution Architecture.

## User Journeys

### Current Journey
Not applicable — no existing product; users currently use generic social/blog/search tools (see "Current Approach").

### Target Journey (Proposed)
1. User discovers app, creates account, selects interests (e.g., cuisines, diets).
2. User browses/searches a feed of recipes from chefs they follow or platform recommendations.
3. User opens a recipe (ingredients, steps, photos/video, nutrition info if available).
4. User likes/comments on the recipe, optionally follows the chef.
5. While viewing/cooking a recipe, user opens the AI agent chat scoped to that recipe and asks questions (e.g., "can I substitute butter with oil?", "how do I know when this is done?").
6. Chef receives notifications of likes/comments/follows and can respond to comments.
7. Chef publishes new recipe; followers are notified.

### Alternate / Exception Journeys
- New chef self-registers with zero followers — cold-start discovery relies on the confirmed engagement-based feed ranking (BR-008) and open self-registration (FEAT-011); no curated/editorial promotion mechanism is planned for MVP.
- User asks AI agent something unrelated to the recipe or off-topic/inappropriate — needs defined boundary behavior (see Edge Cases).
- Chef account impersonation / recipe plagiarism — governed by BR-005 (similarity check) and FR-015 (Admin-reviewed appeal).

## Core Features
| ID | Feature | Description | Business Value | Priority | User / Journey |
|---|---|---|---|---|---|
| FEAT-001 | Recipe Publishing | Chefs (verified chef-role accounts only) create/edit/delete recipes with ingredients, steps, photos/video, tags | Core content supply | Must Have (Confirmed) | Creator Chef |
| FEAT-002 | Social Feed & Discovery (Engagement-Ranked) | Feed of recipes from followed chefs + recommendations/search, ranked by engagement: recipes with more likes and more comments rank higher (Confirmed, BR-008) | Core engagement/discovery | Must Have (Confirmed) | Home Cook |
| FEAT-003 | Likes | Users like recipes | Engagement signal | Must Have (Confirmed) | Home Cook |
| FEAT-004 | Comments | Users comment on recipes | Engagement/community | Must Have (Confirmed) | Home Cook |
| FEAT-005 | Follow Chefs | Users follow chefs to see their content in feed | Retention/creator growth | Must Have (Confirmed) | Home Cook, Creator Chef |
| FEAT-006 | AI Cooking & Nutrition Assistant | Conversational AI acting as a general cooking assistant and nutritionist — can discuss the recipe being viewed as well as general cooking technique, ingredient, and nutrition questions beyond that single recipe | Key differentiator | Must Have (Confirmed) | Home Cook |
| FEAT-007 | Notifications | Notify chefs of likes/comments/follows; notify followers of new recipes | Engagement/retention | Should Have (Proposed) | All |
| FEAT-008 | Chef Profile / Analytics | Chef public profile + basic engagement analytics | Creator retention | Should Have (Proposed) | Creator Chef |
| FEAT-009 | Search | Search recipes by name/ingredient/cuisine/diet | Discovery | Should Have (Proposed) | Home Cook |
| FEAT-010 | Content Moderation Tools | Reporting/flagging of abusive comments/content | Trust & safety | Should Have (Proposed) | All |
| FEAT-011 | Chef Self-Registration & Admin Approval Workflow | Any prospective chef can self-register (no invite-only/curated outreach for MVP), then completes email verification + certificate upload, with an Admin manually approving before publishing privileges are granted | Enables organic chef supply/cold-start (Confirmed) | Must Have (Confirmed) | Creator Chef, Admin |

**Note:** Feature priorities for FEAT-001–FEAT-006 and FEAT-011 are Confirmed by the requester; FEAT-007–010 remain this agent's proposed (unconfirmed) prioritization.

## Business Rules
| ID | Rule | Applies To | Status |
|---|---|---|---|
| BR-001 | Only the recipe's original chef (owner) can edit/delete that recipe | Recipe Publishing | Confirmed |
| BR-002 | A user must have an account to like/comment/follow | Social features | Confirmed |
| BR-003 | The AI agent acts as a general cooking assistant and nutritionist; it is not restricted to answering only about the specific recipe currently being viewed, and may answer general cooking/nutrition questions | AI Agent | Confirmed |
| BR-004 | "Chef" is a distinct, verified/authenticated account role. Only chef-role accounts can publish recipes. Non-chef (regular) users can follow, like, and comment but cannot publish recipes | Account types | Confirmed |
| BR-005 | Zero-plagiarism policy: an automated recipe-similarity check runs before a recipe is finally published. If the similarity match to an existing recipe exceeds 95%, the submitting chef is prompted to review the matched recipe and must provide a comment explaining what differentiates their recipe. Recipes that the system detects as differing in method, ingredients, steps, or ingredient combination are automatically accepted without manual review; the >95% review gate only triggers when no such differentiator is detected. If the chef disputes the resulting rejection/hold, an Admin manually reviews the appeal and approves or denies it | Recipe Publishing | Confirmed |
| BR-006 | Every AI-generated output/recommendation must display a disclaimer (e.g., "not professional medical/nutritional/food-safety advice") and an AI-disclosure notice (clearly indicating the response is AI-generated) | AI Agent | Confirmed |
| BR-007 | Chef account applicants must complete email verification and upload a culinary credential/certification document. The account remains in a "pending" state — without chef/publishing privileges — until an Admin manually reviews and approves the uploaded certificate | Account types / Onboarding | Confirmed |
| BR-008 | Feed/discovery ranking is based on engagement: recipes with more likes and more comments rank higher | Social Feed & Discovery | Confirmed |

## Roles and Permissions
| Role | Allowed Actions | Restricted Actions | Approval / Ownership Rules |
|---|---|---|---|
| Chef (verified/authenticated distinct role) | Publish/edit/delete own recipes, respond to comments, view own analytics, follow/like/comment as any user can | Cannot edit other chefs' recipes; cannot publish while account is in "pending" (not yet Admin-approved) status | Owns own content; **Confirmed onboarding process:** self-registers, then requires email verification plus upload of a culinary credential/certification document; account remains pending until an Admin manually reviews and approves the certificate, after which chef/publishing privileges are granted (see BR-007, FR-013) |
| Regular User / Follower (non-chef) | Like, comment, follow, use AI agent, report content | Cannot publish recipes | N/A |
| Admin (Confirmed role, previously an assumption) | Manually review and approve/reject chef certificate uploads (BR-007, FR-013); manually review and approve/deny chef appeals of a >95% plagiarism-similarity rejection (BR-005, FR-015); remove content, ban/suspend accounts, resolve reports | N/A | Platform-level authority; exact broader moderator/Admin tooling scope beyond the two confirmed workflows above remains an assumption |

## Business Data Needs
- Recipe data: title, ingredients (with quantities/units), steps, photos/video, prep/cook time, servings, cuisine/diet tags, *(assumption)* nutrition info.
- User/account data: profile, account role (chef vs. regular user vs. Admin), chef verification/approval status (email-verified + certificate uploaded + Admin-approved/pending/rejected), followed chefs, liked recipes, comment history.
- Social interaction data: likes, comments, follows, notifications, and aggregate like/comment counts used to compute feed engagement ranking (BR-008, FR-016).
- AI conversation data: chat history retained for 3 days by default; users may bookmark individual AI responses for indefinite retention beyond the 3-day window (Confirmed). Each AI response record must carry its disclaimer/AI-disclosure metadata for display and audit purposes.
- Chef onboarding data: uploaded culinary credential/certification document and its Admin review/approval status (pending/approved/rejected) (Confirmed requirement; document storage/verification workflow mechanics beyond the Admin approval step are a Solution Architect decision).
- Plagiarism appeal data: chef's differentiation comment, appeal request, and Admin approve/deny decision and rationale (Confirmed requirement; underlying similarity-detection algorithm remains a Solution Architect decision).
- Recipe similarity/plagiarism check data: similarity score against existing recipes, detected differentiators (method/ingredients/steps/combination), and — where triggered — the chef's differentiation comment (Confirmed business need; the underlying similarity-detection algorithm/mechanism is **not defined here** and is a Solution Architect decision).
- *(Assumption)* Reporting/moderation data: flagged content records.

## External Systems and Integrations
| System / Service | Business Purpose | Information / Outcome Exchanged | Constraint / Dependency |
|---|---|---|---|
| **Confirmed:** Local LLM Studio (self-hosted/local inference) running the Qwen3.8-27B model | Powers the AI Cooking & Nutrition Assistant | Recipe/conversation content in, conversational answer out | **No external API dependency or per-token cost** since inference runs locally/self-hosted. Implications for Solution Architect: requires local compute/hosting infrastructure (e.g., GPU provisioning, capacity planning for concurrent users) instead of a managed cloud LLM API; potential model capability/quality tradeoffs versus cloud frontier models should be evaluated against the broadened general cooking/nutrition assistant scope (BR-003) and response-time expectations (NFR-001) |
| *(Assumption)* Media storage/CDN | Store/serve recipe photos and videos | Media upload/delivery | Not confirmed |
| *(Assumption)* Push/email notification service | Deliver notifications | Notification triggers/content | Not confirmed |
| *(Assumption)* Payment processor | If creator monetization/subscriptions exist | Payment transactions | Contingent on monetization model decision (see Business Model) |

**Note:** Aside from the confirmed local LLM choice above, no other specific technology or vendor has been mandated by the stakeholder; remaining rows are placeholders identifying that such integrations will likely be needed, not technology decisions.

## Functional Requirements
- FR-001: Users shall be able to register and create an account, selecting or being assigned a role of "Chef" (verified) or "Regular User." *(Confirmed)*
- FR-002: Only chef-role accounts shall be able to create, edit, and delete recipes containing title, ingredients, steps, and at least one photo. *(Confirmed)*
- FR-003: Users shall be able to like a published recipe once (toggle on/off). *(Confirmed)*
- FR-004: Users shall be able to post, view, and delete their own comments on a recipe. *(Confirmed)*
- FR-005: Users shall be able to follow and unfollow a chef. *(Confirmed)*
- FR-006: The system shall display a feed of recipes ranked by engagement — recipes with more likes and more comments rank higher (Confirmed, BR-008), in addition to showing recipes from followed chefs. *(Confirmed)*
- FR-007: Users shall be able to open an AI chat interface that can discuss the currently viewed recipe as well as general cooking technique and nutrition questions beyond that recipe. *(Confirmed)*
- FR-008: The system shall notify chefs of new likes, comments, and follows. *(Proposed, Should Have)*
- FR-009: The system shall allow users to search recipes by keyword. *(Proposed, Should Have)*
- FR-010: The system shall allow users to report inappropriate content or comments. *(Proposed, Should Have)*
- FR-011: Every AI agent response shall display a visible disclaimer (e.g., not professional medical/nutritional/food-safety advice) and an AI-disclosure notice identifying the content as AI-generated. *(Confirmed)*
- FR-012: The system shall retain AI conversation history for 3 days by default and automatically expire it thereafter, except for individual AI responses a user has explicitly bookmarked, which shall be retained indefinitely (or until the user removes the bookmark). *(Confirmed)*
- FR-013: The system shall allow any prospective chef to self-register (no invite-only/curated outreach for MVP), then require completion of email verification and upload of a culinary credential/certification document. The account shall remain in a "pending" state without chef/publishing privileges until an Admin manually reviews and approves the uploaded certificate. *(Confirmed)*
- FR-014: Before a recipe is finally published, the system shall run an automated similarity check against existing recipes. If the similarity score exceeds 95% and no differentiator (method, ingredients, steps, or ingredient combination) is detected, the submitting chef shall be prompted to review the matched recipe and provide a comment explaining what differentiates their recipe before publication can proceed. Recipes where the system detects a differentiator shall be automatically accepted without requiring this manual step. *(Confirmed; underlying similarity-detection algorithm is a Solution Architect decision — not defined here)*
- FR-015: If a chef disputes a >95% similarity-match rejection/hold, the system shall allow the chef to submit an appeal, which an Admin shall manually review and approve or deny. *(Confirmed)*

## Non-Functional Requirements
- NFR-001: *(Assumption/Proposed)* AI agent should respond within a few seconds for a typical query — **Open Question (non-blocking)**: exact measurable target (e.g., "under 5 seconds for 95% of queries") still to be defined with Product Management. **Note:** since the AI runs on a self-hosted local LLM (Local LLM Studio, Qwen3.8-27B) rather than a cloud API, achievable response time also depends on provisioned local compute capacity — a Solution Architect consideration.
- NFR-002: **Confirmed:** MVP targets Web only. Native iOS/Android apps are out of MVP scope and noted as a Future Enhancement.
- NFR-003: *(Open Question, non-blocking)* Expected initial scale beyond the Q1 success metrics (100 active users, 1000 recipes shared) is not otherwise specified; further growth projections can be defined with Product Management. **Note:** local/self-hosted LLM inference (vs. cloud auto-scaling APIs) makes concurrent-usage capacity planning more important — flagged for Solution Architect.
- NFR-004: **Confirmed:** Target market is global. Region-specific regulatory compliance (e.g., GDPR, regional food-safety/advertising regulation) is explicitly **out of scope for MVP** and accepted as a risk to revisit post-MVP (see RISK-006 and ASM-007).
- NFR-005: *(Open Question, non-blocking)* Accessibility requirements (e.g., WCAG conformance level) not specified.
- NFR-006: **Confirmed:** Every AI-generated output must include a disclaimer and an AI-disclosure notice (mirrors BR-006/FR-011; stated here as a quality/compliance-adjacent requirement, not merely a risk mitigation).
- NFR-007: **Confirmed (new):** The AI Cooking & Nutrition Assistant shall run on self-hosted/local inference (Local LLM Studio, Qwen3.8-27B model) rather than a third-party cloud LLM API. This eliminates per-token/external API cost and third-party data transmission for AI conversations, but requires local compute/hosting infrastructure to be provisioned and maintained, and may involve model-capability tradeoffs versus cloud frontier models that Solution Architect should evaluate against the broadened general cooking/nutrition assistant scope.

## Edge Case Requirements
- EC-001: **Confirmed (superseded):** The AI agent is a general cooking assistant and nutritionist and is permitted to answer general cooking/nutrition questions beyond the specific recipe being viewed (see BR-003, FR-007). It should still decline questions entirely unrelated to cooking/nutrition/food topics.
- EC-002: **Confirmed:** For food-safety-sensitive or nutrition-sensitive questions, the AI agent must include a disclaimer and AI-disclosure notice on every response (see BR-006, FR-011, NFR-006) rather than presenting answers as authoritative professional advice.
- EC-003: *(Proposed)* A user attempting to like/comment/follow without being logged in should be prompted to authenticate.
- EC-004: *(Proposed)* A chef deleting their account — behavior for their existing recipes, comments, and followers must be defined. **Open Question**: are recipes removed, archived, or retained/orphaned?
- EC-005: **Confirmed:** Recipe similarity/plagiarism edge cases (related to BR-005/FR-014/FR-015): (a) false-positive match — the similarity check flags a recipe above 95% similarity, but the chef believes their recipe is genuinely original; the chef's differentiation comment is captured and, if the chef disputes the resulting rejection/hold, they may submit an appeal which an Admin manually reviews and approves or denies (FR-015). (b) Borderline similarity scoring (e.g., scores near the 95% threshold, or differentiator-detection false negatives/positives) is a Solution Architect concern for the similarity-detection mechanism design, not defined here.
- EC-006: *(Proposed)* Abusive/spam comments — should be reportable and hideable; escalation path to moderator undefined pending BR/role confirmation.

## MVP Scope

### Must Have
**Confirmed:** FEAT-001 (Recipe Publishing, chef-role only), FEAT-002 (Social Feed & Discovery, engagement-ranked), FEAT-003 (Likes), FEAT-004 (Comments), FEAT-005 (Follow Chefs), FEAT-006 (AI Cooking & Nutrition Assistant), FEAT-011 (Chef Self-Registration & Admin Approval Workflow), BR-006/FR-011 (AI disclaimer + AI-disclosure notice), FR-012 (3-day AI history retention with bookmarking), BR-007/FR-013 (chef onboarding with Admin approval), BR-005/FR-014/FR-015 (plagiarism check and Admin-reviewed appeal), BR-008/FR-006 (engagement-based feed ranking) — all targeting **Web platform only**.

### Should Have
*(Proposed)* FEAT-007 (Notifications), FEAT-008 (Chef Profile/Analytics), FEAT-009 (Search), FEAT-010 (Content Moderation Tools)

### Could Have
*(Proposed)* Recipe collections/bookmarks (note: distinct from AI-response bookmarking, which is Must Have), advanced personalized recommendations, video content support beyond photos.

### Won't Have in This Release
**Confirmed:** Native iOS/Android mobile apps (Web only for MVP). Creator monetization/subscriptions/tipping (ads-only monetization for MVP). Region-specific regulatory compliance work (global launch accepted as-is for MVP; see RISK-006/ASM-007). *(Proposed, still pending confirmation)* Multi-language support, live cooking video streaming, marketplace/e-commerce for ingredients, advanced nutrition tracking/diet planning tools.

## Out of Scope
*(Proposed, pending confirmation)* Restaurant reservation/ordering features, grocery delivery integration, non-recipe general social networking (e.g., generic status posts unrelated to recipes).

## Constraints and Dependencies
- CON-001: *(Open Question, non-blocking)* Budget and timeline constraints are unknown.
- CON-002: **Confirmed:** Target platform for MVP is Web only. Native mobile apps are deferred to a future release.
- CON-003: **Confirmed:** The AI feature will run on a self-hosted/local LLM (Local LLM Studio, Qwen3.8-27B model) rather than a third-party cloud AI/LLM API. This is a stakeholder-mandated technology constraint (not a Solution Architect free choice): it requires local compute/hosting infrastructure to be provisioned (e.g., GPU capacity), removes per-token/external API cost, but may carry model-capability/quality tradeoffs versus cloud frontier models that should be evaluated by Solution Architect against the broadened AI assistant scope and response-time expectations.
- CON-004: **Confirmed:** Region-specific legal/regulatory compliance (e.g., GDPR, regional food-safety/advertising regulation) is explicitly out of scope for MVP given the global target market; this is an accepted risk to be revisited post-MVP (see RISK-006/ASM-007), not a blocking constraint for this release.
- CON-005: *(Open Question, non-blocking)* Team size/composition and existing technical assets (none found in this repository beyond agent/skill scaffolding) are unknown.

## Risks
| ID | Risk | Impact | Likelihood | Mitigation / Response | Owner |
|---|---|---|---|---|---|
| RISK-001 | AI agent (now broadened to general cooking/nutrition assistant) gives incorrect or unsafe cooking/nutrition/food-safety advice | High (health/legal liability, trust damage) | Medium *(assumption)* | **Confirmed mitigation:** mandatory disclaimer + AI-disclosure notice on every AI response (BR-006, FR-011, NFR-006) | TBD |
| RISK-002 | Cold-start problem: platform relies solely on organic self-registration (no curated/invite-only outreach) for initial chef supply, which may be slower to build critical mass than a curated approach | High (adoption failure) | Medium–High *(assumption)* | **Confirmed strategy:** self-registration open to any prospective chef via the email + certificate + Admin-approval flow (FEAT-011, BR-007, FR-013); no additional curated outreach planned for MVP | TBD |
| RISK-003 | Content moderation burden (spam, abuse, plagiarism) grows faster than moderation capability, and Admin now bears manual review responsibility for chef certificate approvals and plagiarism appeals | Medium | Medium *(assumption)* | Reporting tools, community guidelines, moderation team; monitor Admin review-queue volume as chef self-registration scales | TBD |
| RISK-004 | ~~Monetization model undefined~~ **Resolved:** Ads-only monetization confirmed for MVP; residual risk is whether ad revenue is sufficient to sustain operations | Medium | Medium *(assumption)* | Monitor ad performance; revisit monetization model post-MVP if needed | TBD |
| RISK-005 | Local self-hosted LLM (Local LLM Studio, Qwen3.8-27B) infrastructure costs/capacity, rather than cloud API usage costs, may be significant at scale, especially with a broadened general-assistant scope (cooking + nutrition) rather than narrow recipe-only Q&A; additionally, local model capability/quality may lag cloud frontier models | Medium–High *(scope broadening increases likely usage volume; local hosting shifts cost from per-token to infrastructure/capacity)* | Medium *(assumption)* | Capacity planning for local compute/hosting, usage limits, and Solution Architect evaluation of model quality vs. scope needs | TBD |
| RISK-006 | Operating globally without addressing region-specific legal/regulatory compliance (e.g., GDPR, food-safety/advertising regulation) for MVP | Medium–High | Medium *(assumption)* | **Accepted risk for MVP per requester decision;** revisit compliance posture post-MVP before scaling in regulated markets | Requester (accepted) |
| RISK-007 | Chef verification process (email + certificate upload + Admin approval) could be circumvented by fraudulent/forged credential documents, could create onboarding friction that discourages legitimate chefs from joining, or could create an Admin review bottleneck as self-registration volume grows | Medium | Medium *(assumption)* | **Confirmed mitigation:** Admin manual review/approval gate (BR-007, FR-013); Admin staffing/tooling capacity is a non-blocking open item for Product Management | TBD |
| RISK-008 | Recipe similarity/plagiarism check produces false positives (blocking/delaying legitimate original recipes) or false negatives (missing genuine plagiarism); Admin appeal review (FR-015) could also become a bottleneck at scale | Medium | Medium *(assumption)* | **Confirmed mitigation:** Admin-reviewed appeal path (BR-005, FR-015); underlying similarity-detection accuracy and Admin appeal-queue capacity are Solution Architect / Product Management concerns | TBD |

## Assumptions
| ID | Assumption | Why It Matters | Validation Needed | Owner |
|---|---|---|---|---|
| ASM-001 | ~~"Chefs" are a distinct account role~~ **Resolved — now Confirmed (BR-004)**, retained here for traceability | Drives permission model and UX design | Resolved | Requester |
| ASM-002 | ~~Primary platform is mobile~~ **Resolved — now Confirmed as Web only for MVP (NFR-002, CON-002)** | Drives cost, UX, and scope | Resolved | Requester |
| ASM-003 | ~~AI agent scoped strictly to the recipe~~ **Superseded — now Confirmed as broadened general cooking/nutrition assistant (BR-003)** | Drives AI product boundary, cost, and liability | Resolved | Requester |
| ASM-004 | ~~No monetization required for MVP~~ **Resolved — now Confirmed as ads-only monetization (Business Model section)** | Drives whether payments/subscriptions are in MVP scope | Resolved | Requester |
| ASM-005 | ~~Target market/region not yet chosen~~ **Resolved — now Confirmed as global, with regional compliance explicitly deferred post-MVP** | Drives compliance requirements | Resolved | Requester |
| ASM-006 | ~~MVP feature set reflects intended scope~~ **Resolved — now Confirmed per MVP Scope section** | Drives entire PRD scope | Resolved | Requester |
| ASM-007 | Global launch without region-specific compliance work (e.g., GDPR, food-safety/advertising regulation) will not create material legal exposure during the MVP period | Legal/regulatory risk if incorrect | Recommend legal review before scaling beyond MVP, even though deferred now | Requester (accepted risk) |
| ASM-008 | ~~No specific chef recruitment/cold-start content strategy has been defined~~ **Resolved — now Confirmed:** self-registration open to any prospective chef (no curated/invite-only outreach) via the email + certificate + Admin-approval flow (RISK-002, FEAT-011) | Adoption risk if content supply is insufficient at launch (RISK-002) | Resolved | Requester |
| ASM-009 | ~~Budget, timeline, and LLM/AI provider selection are not yet defined~~ **Partially resolved:** LLM/AI provider is now Confirmed (Local LLM Studio, Qwen3.8-27B — see CON-003, NFR-007, External Integrations). Budget and timeline remain undefined and are assumed to be addressed in later Solution Architect / planning stages | Needed for cost/timeline planning and technical design | Budget/timeline still to be addressed by Solution Architect / planning stage | Requester/Engineering |
| ASM-010 | *(New)* Local LLM (Qwen3.8-27B via Local LLM Studio) will provide sufficient response quality and latency for a general cooking/nutrition assistant use case at the confirmed target scale (100 active users, 1,000 recipes in Q1) | If model capability is insufficient, AI feature quality/UX may suffer, affecting FEAT-006/BR-003 value proposition | Solution Architect / engineering evaluation (benchmarking) recommended before/at build time | Requester/Engineering |
| ASM-011 | ~~The culinary credential/certification document uploaded during chef onboarding will be reviewed by some process (manual or automated)~~ **Resolved — now Confirmed:** Admin manually reviews and approves/rejects the certificate (BR-007, FR-013); account remains pending until approval | Onboarding UX and trust/safety design depend on this | Resolved | Requester |
| ASM-012 | *(New, non-blocking)* Self-registration-only chef onboarding (no curated outreach) combined with Admin manual review of certificates and plagiarism appeals is assumed to remain operationally manageable at the confirmed Q1 target scale (100 active users, 1,000 recipes); Admin staffing/tooling needs beyond this have not been defined | Operational risk if Admin review volume exceeds capacity (RISK-007, RISK-008) | Product Management to plan Admin staffing/tooling as volume grows | Requester/PM |

## Success Metrics
| Metric | Baseline | Target | Time Horizon | Measurement Source / Owner |
|---|---|---|---|---|
| Active users | 0 (pre-launch) | 100 active users | Q1 post-launch | **Confirmed by requester**; measurement source/analytics tooling TBD |
| Recipes shared | 0 (pre-launch) | 1,000 recipes shared | Q1 post-launch | **Confirmed by requester**; measurement source/analytics tooling TBD |

*(Note: "active users" definition — e.g., monthly active vs. weekly active, and the precise activity threshold — has not been specified. Non-blocking; Product Management should define the exact operational definition.)*

## Future Enhancements
*(Proposed, non-blocking)*
- Native iOS/Android mobile apps (deferred from MVP; Web only at launch).
- Personalized AI-driven recipe recommendations based on user history/preferences.
- Creator monetization (tipping, subscriptions, sponsored recipes) — deferred; MVP is ads-only.
- Multi-recipe meal planning powered by the AI agent.
- Video-first recipe content and live cooking sessions.
- Multi-language/localization support.
- Region-specific regulatory compliance work (e.g., GDPR, local food-safety/advertising regulation) as the platform scales beyond MVP.

## Open Questions
| Question | Why It Matters | Owner | PRD Blocking? | Required By |
|---|---|---|---|---|
| What is the budget/timeline for this initiative? | Scoping and prioritization | Requester | No | Before planning |
| What is the exact measurable AI response-time target (NFR-001), accounting for local LLM inference capacity? | Quality bar for AI feature | Requester/PM | No | Before PRD/NFR finalization |
| What accessibility conformance level (e.g., WCAG) is required (NFR-005)? | Compliance/UX scope | Requester | No | Before PRD/NFR finalization |
| What is the operational definition of "active user" for the Q1 success metric? | Measurement clarity | Requester/PM | No | Before analytics implementation |

**All previously PRD-blocking questions, and all previously non-blocking items except the four listed above (LLM/AI provider choice, chef verification mechanism, plagiarism/similarity policy and appeal path, cold-start chef recruitment strategy, feed ranking logic), have now been resolved by the requester and are reflected in the relevant sections above.** The four remaining items above are non-blocking and may be carried forward to Product Manager / Solution Architect stages.

## Glossary
- **Chef**: A verified/authenticated account role (self-registration + email verification + culinary credential/certification document + Admin approval required) that is the only role permitted to publish recipes on the platform.
- **Admin**: A platform-level role (Confirmed) that manually reviews and approves/rejects chef certificate uploads and manually reviews/decides plagiarism-similarity appeals; also holds general content moderation authority.
- **Follower / Home Cook**: A user who consumes content, engages socially, and may use the AI agent.
- **AI Cooking & Nutrition Assistant**: A conversational AI feature, running on a self-hosted local LLM (Local LLM Studio, Qwen3.8-27B), that can discuss the recipe being viewed as well as general cooking and nutrition topics.
- **MVP**: Minimum Viable Product — the initial Must-Have release scope.

## Notes
This idea.md was initially produced in a single non-interactive discovery session based solely on a one-sentence product brief. The requester has since answered all previously PRD-blocking open questions, plus a further round of previously non-blocking items: chef credential review workflow (Admin approval), plagiarism dispute/appeal path (Admin approval), cold-start chef recruitment strategy (open self-registration), and feed ranking logic (engagement-based). Those decisions are now reflected as Confirmed throughout this document. Remaining open items (budget/timeline, AI response-time target, accessibility conformance level, and the operational definition of "active user") are explicitly non-blocking per requester direction and are carried forward for the Product Manager and Solution Architect stages to address. This document remains PRD-ready.
