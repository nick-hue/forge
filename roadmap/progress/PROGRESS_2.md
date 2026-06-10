# Forge — Progress

> Live status panel. Claude keeps this in sync; it always shows **only the current phase**.
> Open beside your code in VS Code: `Ctrl+Shift+V` (preview auto-refreshes on save).

---

## 📍 Current phase: **Phase 2 — Containerize, the Modern Way**

**Goal:** package the API + worker into portable, reproducible, secure-by-default images, and wire the whole stack (API + worker + Postgres + Redis) so it starts cold with a **single command**. This directly kills the "juggle terminals + hand-start everything" friction from Phase 1.

| # | Task | Status |
|---|------|--------|
| 1 | `.dockerignore` (mirror `.gitignore`) — keep junk/secrets out of the build context | ✅ Done |
| 2 | **Multi-stage** `api/Dockerfile` — uv builder stage + slim final stage | ✅ Done |
| 3 | **Multi-stage** `worker/Dockerfile` — same pattern | ✅ Done |
| 4 | Use a **slim/distroless** base image for the final stage | ✅ Done |
| 5 | Run each container as a **non-root** `USER` | ✅ Done |
| 6 | **Reproducible builds** — install from the pinned lockfile (`uv sync --frozen`) | ✅ Done |
| 7 | Build both images locally and confirm each runs on its own | ✅ Done |
| 8 | `docker-compose.yml` — four services: `api`, `worker`, `postgres`, `redis` | ✅ Done |
| 9 | Shared network + `depends_on` + **healthchecks** (esp. Postgres/Redis) for correct startup order | ✅ Done |
| 10 | Pass config (DB URL, Redis URL, …) via **environment variables**, not hardcoded | ✅ Done |
| 11 | `docker compose up` → re-run the **Phase 1 end-to-end test** against it | ✅ Done |
| 12 | Commit with conventional commits (e.g. `feat: containerize api and worker with docker compose`) | ⬜ To do |

**Done when:** the entire system starts cold with a single `docker compose up` and zero local setup — no hand-started Postgres/Redis, no juggling terminals — and the image-to-thumbnail flow still works.

---

_Legend: ✅ Done · 🔧 Needs fix · ⬜ To do_
