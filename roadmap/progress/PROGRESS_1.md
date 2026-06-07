# Forge — Progress

> Live status panel. Claude keeps this in sync; it always shows **only the current phase**.
> Open beside your code in VS Code: `Ctrl+Shift+V` (preview auto-refreshes on save).

---

## 📍 Current phase: **Phase 1 — Build the Services, Run Them by Hand**

**Goal:** build the API + worker and run the whole system manually in separate terminals — and deliberately *feel the friction* of doing it by hand. That pain motivates every automation phase that follows.

| # | Task | Status |
|---|------|--------|
| 1 | Add runtime deps: `fastapi`, `uvicorn`, `redis`, `celery`/`rq`, `psycopg`, `pillow` | ✅ Done |
| 2 | Start local **PostgreSQL** + **Redis** (e.g. one `docker run` each) | ✅ Done |
| 3 | `api/models.py` — Pydantic shape of a "job" (id, image URL, status, result links) | ✅ Done |
| 4 | `api/db.py` — connect to Postgres, create `jobs` table, insert/update/read functions | ✅ Done |
| 5 | `api/queue.py` — push a new job onto Redis (or define the Celery/RQ task) | ✅ Done |
| 6 | `api/main.py` — FastAPI `POST /jobs` (enqueue, return `job_id`) + `GET /jobs/{id}` | ⬜ To do |
| 7 | `worker/thumbnails.py` — Pillow logic producing 3 thumbnail sizes | ⬜ To do |
| 8 | `worker/worker.py` — pull job, download image, thumbnail, store, update status | ⬜ To do |
| 9 | Run the API by hand: `uvicorn api.main:app --reload` | ⬜ To do |
| 10 | Run the worker by hand in a separate terminal | ⬜ To do |
| 11 | **End-to-end test:** POST an image URL → poll `GET /jobs/{id}` → confirm thumbnails | ⬜ To do |
| 12 | Write a **"friction list"** in the README — everything annoying about manual setup | ⬜ To do |
| 13 | Commit with conventional commits (e.g. `feat: add job API and worker`) | ⬜ To do |

**Done when:** you can submit an image, watch a worker process it in another terminal, retrieve finished thumbnails — and you have a written list of what was painful about doing it by hand.

---

_Legend: ✅ Done · 🔧 Needs fix · ⬜ To do_
