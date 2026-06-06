# Forge — Progress

> Live status panel. Claude keeps this in sync; it always shows **only the current phase**.
> Open beside your code in VS Code: `Ctrl+Shift+V` (preview auto-refreshes on save).

---

## 📍 Current phase: **Phase 0 — Foundations**

**Goal:** stand up an empty, well-tooled repo so quality + version control are automatic from the first line of code.

| # | Task | Status |
|---|------|--------|
| 1 | Install **uv** | ✅ Done |
| 2 | `git init` | ✅ Done |
| 3 | `uv init` → `pyproject.toml` | ✅ Done |
| 4 | `.gitignore` — add `.env` (rest already covered) | ✅ Done |
| 5 | Folder skeleton: `api/` `worker/` `deploy/` `.github/` (with `.gitkeep`) | ✅ Done |
| 6 | Add **ruff** (`uv add --dev ruff`) + `[tool.ruff]` in `pyproject.toml` | ✅ Done |
| 7 | Add **pre-commit** + `.pre-commit-config.yaml` + `pre-commit install` | ✅ Done |
| 8 | Write one-paragraph `README.md` | ✅ Done |
| 9 | Create GitHub repo + add `origin` remote | ✅ Done |
| 10 | First **conventional** commit (`chore: initial project scaffold`) + push to `main` | ✅ Done |

**Done when:** repo is on GitHub, `pre-commit run --all-files` passes, and a fresh clone sets up with a single `uv sync`.

---

_Legend: ✅ Done · 🔧 Needs fix · ⬜ To do_
