# Phase 0 — Foundations

**Goal:** stand up an empty, well-tooled repository so that quality and version control are automatic from the very first line of code. No application logic yet — just the scaffolding everything else hangs off.

**Estimated time:** ~½ day

---

## Tasks

Complete every box before moving to Phase 1.

- [ ] Install **uv** (the Python package/env manager) on your machine.
- [ ] Create a project folder `forge/` and run `git init` inside it.
- [ ] Create the empty folder skeleton: `api/`, `worker/`, `deploy/`, `.github/`.
- [ ] Run `uv init` to generate `pyproject.toml`.
- [ ] Add **ruff** as a dev dependency (`uv add --dev ruff`) and add a `[tool.ruff]` section to `pyproject.toml`.
- [ ] Create a Python `.gitignore` (ignore `.venv/`, `__pycache__/`, `.env`, etc.).
- [ ] Add **pre-commit** (`uv add --dev pre-commit`), create `.pre-commit-config.yaml` with the ruff hooks, then run `pre-commit install`.
- [ ] Write a one-paragraph `README.md` describing what Forge is.
- [ ] Create a new repository on **GitHub** and add it as the `origin` remote.
- [ ] Make your first commit using a **conventional commit** message (e.g. `chore: initial project scaffold`) and push to `main`.

**Done when:** the repo is on GitHub, `pre-commit run --all-files` passes, and a fresh clone could set up its environment with a single `uv sync`.

---

## What each task did

Installing **uv** and running `uv init` gave you a single, fast tool to manage your Python version, virtual environment, and dependencies, all recorded in `pyproject.toml` — which means anyone (including future-you on the Arch laptop) can reproduce the exact environment with one command instead of fighting mismatched package versions. Running `git init` and creating the four folders (`api/`, `worker/`, `deploy/`, `.github/`) laid down the skeleton that mirrors the system's three concerns — the HTTP service, the background processor, and everything needed to deploy them — so every file you write later has an obvious home.

Adding **ruff** and wiring up **pre-commit** turned code quality into something that happens *to* you automatically rather than something you have to remember: every time you commit, ruff lints and formats your code, so style stays consistent and obvious mistakes get caught before they ever reach the repo. The **.gitignore** keeps generated junk and — critically — secrets like `.env` files out of version control from day one, a habit that matters enormously once GitOps makes the repo your source of truth.

Finally, creating the **GitHub** repo and pushing your first **conventional commit** connected your local work to the remote that will later run your CI pipeline and host your container images, while the commit-message convention (`chore:`, `feat:`, `fix:`) sets up a clean, machine-readable history that supports automated versioning down the line. The one-paragraph **README** is small now but becomes the front door of your portfolio project — you'll grow it as the system grows. None of this is glamorous, but it's exactly the unglamorous setup real teams do before writing a line of product code: when you reach Phase 5 and the repo literally becomes production, you'll be glad it was disciplined from commit #1.
