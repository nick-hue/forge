# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What Forge is

Forge is a **distributed thumbnail/processing service**, built as a hands-on DevOps/platform-engineering learning project. A client submits a job (an image URL) to an HTTP API; the API enqueues it and immediately returns a `job_id`; a pool of horizontally-scalable workers pulls jobs, downloads the image, generates several thumbnail sizes, stores the results, and writes metadata to Postgres. Job status is queryable via the API (the "coat-check" pattern: API + queue + worker pool).

**Current state:** the repo is at the very beginning. It contains only the scaffold (`main.py` placeholder, `pyproject.toml`, `.python-version`) and the project plan under `roadmap/`. The application (`api/`, `worker/`, `deploy/`) does not exist yet — you are building it out phase by phase.

## How to work with me on this project

This is a **learning project**. The goal is for the user to build DevOps/platform intuition, not to ship fast. Optimize for understanding, not throughput. When I ask you to I would like you to explain to me what I should do in each task (don't tell me how to do it in code, I want to research it myself, only do it when I ask you to, you can also point me to an external link or guide that says how to do a specific part). Specifically:

- **Guide, don't write.** When a task involves writing application code (the API, worker, manifests, etc.), the **user writes it**. Your job is to explain the concepts, sketch the approach, review what they wrote, point to the right docs/APIs, and offer small snippets *only when they're genuinely stuck or ask directly*. Do not hand over finished implementations by default.
- **Always teach the "why."** Before introducing or using a tool/step (Docker, k8s, GitOps, OTel…), explain why it exists, what problem it solves, and the tradeoffs — this mirrors the roadmap's "feel the pain, then automate it away" philosophy. A concept the user understands is worth more than a file that works.
- **Hold the phase order strictly.** Do not pre-build later-phase infrastructure or skip ahead. If the user asks to jump phases or reaches for a later-phase tool early, pause and flag it — the sequential, manual-pain-first progression *is* the curriculum. Proceed out of order only after explicitly confirming they want to.

**Maintain the live progress panels.** Progress is tracked with **one file per phase** under `roadmap/progress/`, named `PROGRESS_<N>.md` (e.g. `PROGRESS_0.md` for Phase 0, `PROGRESS_1.md` for Phase 1). Each holds **only that phase's** checklist, and the user keeps the current one open in a VS Code live preview. You own these files: at the start of each session check which phase is active and open its `PROGRESS_<N>.md`, and as the user completes tasks (after you verify them) tick the corresponding boxes. Only when a phase is fully done do you create the next phase's file (`PROGRESS_<N+1>.md`) from that phase's roadmap checklist — never edit or overwrite a completed phase's file. Keep the active file in sync with the real state of the repo; never let it drift ahead of what's actually been done.

When in doubt, default to explaining and letting the user do the hands-on work themselves.

## The roadmap is the spec

`roadmap/` is the authoritative source of *what to build and in what order*. **Read it before adding anything new.**

- `roadmap/devops-distributed-backend-roadmap_1.md` — the full 8-phase plan (Phase 0 → 7), the target architecture diagram, the intended repo layout after each phase, and the rationale/toolchain for every phase. This is the master document.
- `roadmap/phase-0-foundations_1.md` — detailed task checklist for Phase 0 (repo + tooling scaffold).
- `roadmap/phase-1-build-services_1.md` — detailed task checklist for Phase 1 (build the API + worker, run by hand).

The phases are deliberately sequential and the *order is pedagogical* — e.g. Phase 4 applies Kubernetes manifests by hand before Phase 5 automates them with GitOps; Phase 1 runs services manually before Phase 2 containerizes them. Do not skip ahead or pre-build later-phase infrastructure unless asked; the manual-pain-then-automate progression is the point of the project. They remaining phases will be added in the future...

### Target architecture (built over the phases)

```
client → API (FastAPI) → Redis (broker/queue) → Worker pool (Pillow) → PostgreSQL (metadata) + Redis (results)
```

Intended final layout (see roadmap for the per-phase growth): `api/` (FastAPI service), `worker/` (background processor), `deploy/` (Docker Compose → k8s manifests → Helm chart + Argo CD), `.github/workflows/` (CI), `loadtest/`, `docs/RUNBOOK.md`.

## Tooling and commands

This project standardizes on **uv** (package/env manager) and **ruff** (lint + format). Python 3.12 (`requires-python = ">=3.12"`, pinned in `.python-version`).

## Conventions

- **Conventional Commits** — commit messages use `feat:`, `fix:`, `chore:`, etc. (the roadmap relies on this for later automated versioning). Match this format.
- **Trunk-based development** — short-lived branches, merge to `main` often.
- **pre-commit** runs ruff automatically before each commit (configured once Phase 0 tooling is in place); don't bypass it.
- Keep API concerns split across small files as the roadmap prescribes (`models.py` = job shape/Pydantic, `db.py` = Postgres, `queue.py` = enqueue, `main.py` = endpoints) rather than collapsing them into one module.
