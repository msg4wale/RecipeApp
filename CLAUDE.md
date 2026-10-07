# Agentic AI Workteam (Claude Code)

- Framework Version: 1.0.0

A coordinator-orchestrated SDLC workteam. Subagents live in `.claude/agents/` and reusable skills in `.claude/skills/`. In this project the **main Claude Code session plays the Coordinator** (see *Running the Coordinator* below): it dispatches the other agents as subagents, stops at each stage for your approval, and keeps durable, transferable state under `.workteam/`.

**Capability bindings:** ASK_USER → AskUserQuestion · SUBAGENT → Agent (formerly `Task`; the agent files still list `Task`, which Claude Code accepts as an alias) · READ/SEARCH/EDIT/SHELL → Read / Grep,Glob / Edit,Write / Bash.

**Transferable project:** read `.workteam/Project.md` and `.workteam/Workteam-State.md` first; if another harness was last active, reconcile and resume at the first unapproved stage. All agents honour `Constitution.md`.

## Agents

| slug | role | capabilities |
|---|---|---|
| `code-reviewer` | Code Reviewer | READ, SEARCH, EDIT, SHELL, ASK_USER, SUBAGENT |
| `coordinator` | Coordinator | READ, SEARCH, EDIT, ASK_USER, SUBAGENT |
| `devops-engineer` | DevOps Engineer | READ, SEARCH, EDIT, SHELL, ASK_USER, SUBAGENT |
| `engineering-lead` | Engineering Lead | READ, SEARCH, EDIT, ASK_USER |
| `idea-discovery` | Idea Discovery | READ, SEARCH, EDIT, ASK_USER |
| `plan-architect` | Plan Architect | READ, SEARCH, EDIT, SHELL, ASK_USER, SUBAGENT |
| `product-manager` | Product Manager | READ, SEARCH, EDIT, ASK_USER |
| `qa-engineer` | QA Engineer | READ, SEARCH, EDIT, SHELL, ASK_USER, SUBAGENT |
| `software-engineer` | Software Engineer | READ, SEARCH, EDIT, SHELL, ASK_USER, SUBAGENT |
| `solution-architect` | Solution Architect | READ, SEARCH, EDIT, ASK_USER |

## Running the Coordinator

Claude Code subagents cannot start other subagents. So do **not** launch `coordinator` as a subagent:
the main session reads `.claude/agents/coordinator.md` and follows it directly, dispatching each worker
(`software-engineer`, `code-reviewer`, `qa-engineer`, …) with the Agent tool. The same limit applies inside
`code-reviewer`, `qa-engineer`, `plan-architect`, and `software-engineer`: when running as a subagent they
work through their perspectives sequentially. For truly parallel, blind review/QA perspectives, the main
session dispatches one subagent per perspective skill and then runs the consolidation skill
(`review-decision-validation` / `qa-decision-defect-reporting`).

## RecipeApp: where the run stands

- Project moved here from GitHub Copilot (VS Code) on 2026-10-07; see `.workteam/Project.md` Transfer Log.
- Stages 1–5 approved (`idea.md`, `PRD.md`, `TDD.md`, `Engineering-Plan.md`, `Plan-Validation-Report.md`).
- Implementation is task-by-task (Stages 6–8 per task). Done: PLAT-001, DB-001, OBS-004, BE-001,
  INT-002-T, INT-003-T, SEC-002, BE-002, BE-003. In progress: PLAT-005. **Next: BE-004.**
- Stage 9 (DevOps Engineer) is new in framework 1.0.0 and has not run yet.
- Source of truth is `.workteam/Workteam-State.md` and `.workteam/Decisions-Log.md`, not this summary.

To continue, ask Claude Code something like: *"Act as the coordinator in `.claude/agents/coordinator.md`
and resume the workteam run."*

## RecipeApp: stack and commands

- Backend: FastAPI + SQLAlchemy + Alembic (`backend/`), tests in `backend/tests/` (pytest).
- Frontend: React + TypeScript + Vite (`frontend/`).
- Local stack: `docker compose up` (Postgres 16, LocalStack S3, Ollama, Mailpit, API, worker, frontend).
  Copy `.env.example` to `.env` first; never commit `.env`.
- Concurrency/locking checks must run against PostgreSQL 16, not SQLite (Plan Architect note on PLAN-REVISE-BE-003 in `.workteam/Workteam-State.md`).
- Run backend tests from `backend/` with a virtualenv that has pytest (it is not in `requirements.txt`): `python -m pytest -q`. `VERIFICATION-GUIDE.md` has the BE-003 runtime checks.
