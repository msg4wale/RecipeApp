# Workteam Project Manifest

The portable record of this project's workteam run. It is harness-neutral (agents referenced by slug, deliverables by root path) and travels with the repo via git, so the project can be resumed in any installed harness.

- Project: RecipeApp
- Framework Version: 1.0.0
- Installed Harnesses: [claude-code]
- Last Active Harness: claude-code @ 2026-10-07 (previously copilot; transfer recorded below)
- Current Stage: software-engineer — next task BE-004  (mirrors Workteam-State.md)

## Deliverables
| Artifact | Present | Approved |
|---|---|---|
| idea.md | yes | yes |
| PRD.md | yes | yes |
| TDD.md | yes | yes |
| Engineering-Plan.md | yes | yes |
| Plan-Validation-Report.md | yes | yes |
| QA-Report.md | yes | yes (per task; latest BE-003 IC-01) |
| Deployment-Plan.md | no | — |
| Deployment-Report.md | no | — |

## Transfer Log
| Timestamp | From Harness | To Harness | At Stage | Notes |
|---|---|---|---|---|
| 2026-10-07 | copilot | claude-code | software-engineer (BE-004 next) | Framework upgraded from pre-1.0 Copilot build (upstream 83fefde) to 1.0.0 Claude Code package. Old `.github/agents` + `.github/skills` removed. State ledgers carried over unchanged. Note: DEC-102 is referenced in Workteam-State.md but missing from Decisions-Log.md (not flushed before the switch). |
