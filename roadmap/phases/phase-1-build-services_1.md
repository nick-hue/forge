# Phase 1 — Build the Services, Run Them by Hand

**Goal:** build the actual working software — the API and the worker — and run the whole system manually, in separate terminals. The point is to make it *work*, but also to deliberately *feel the friction* of running it by hand, because that pain is what motivates every automation phase that follows.

**Estimated time:** 3–5 days

---

## Tasks

Complete every box before moving to Phase 2.

- [ ] Add runtime dependencies with uv: `fastapi`, `uvicorn`, `redis`, `celery` (or `rq`), a Postgres driver (`psycopg`), and `pillow`.
- [ ] Start a local **PostgreSQL** and a local **Redis** (simplest: one `docker run` each) so the app has a database and a queue to talk to.
- [ ] Write `api/models.py` — define the shape of a "job" (id, image URL, status, result links) with Pydantic.
- [ ] Write `api/db.py` — connect to Postgres, create the `jobs` table, and add functions to insert/update/read a job.
- [ ] Write `api/queue.py` — push a new job onto Redis (or define the Celery/RQ task).
- [ ] Write `api/main.py` — the FastAPI app with `POST /jobs` (create a job, enqueue it, return a `job_id`) and `GET /jobs/{id}` (return status + result links).
- [ ] Write `worker/thumbnails.py` — the Pillow logic that takes an image and produces 3 thumbnail sizes.
- [ ] Write `worker/worker.py` — pull a job off the queue, download the image, call the thumbnail logic, store the outputs, and update the job's status in Postgres.
- [ ] Run the API by hand: `uvicorn api.main:app --reload`.
- [ ] Run the worker by hand in a separate terminal.
- [ ] **End-to-end test:** `POST` an image URL, poll `GET /jobs/{id}` until it's done, and confirm the thumbnails were produced.
- [ ] Write down a short **"friction list"** in your README — everything annoying about starting and wiring this up manually.
- [ ] Commit your work with conventional commits (e.g. `feat: add job API and worker`).

**Done when:** you can submit an image, watch a worker process it in another terminal, and retrieve finished thumbnails — and you have a written list of what was painful about doing it by hand.

---

## What each task did

Adding the dependencies and starting **Postgres** and **Redis** gave the application the two stateful services it depends on: a durable database to remember jobs and a fast in-memory store to act as the queue between the API and the workers. Writing `models.py`, `db.py`, and `queue.py` built the API's three internal jobs — defining *what a job is*, *how it's stored and retrieved*, and *how it gets handed off to be worked on* — keeping each concern in its own small file so the code stays readable and testable later. Building `api/main.py` tied those together into the actual front door: `POST /jobs` accepts work and immediately returns a ticket (`job_id`) instead of making the caller wait, and `GET /jobs/{id}` lets them check back later — this is the "coat-check" behavior that makes the system asynchronous rather than a blocking script.

On the worker side, `thumbnails.py` isolated the real CPU work (resizing images with Pillow) from everything else, and `worker.py` wrapped it in the loop that makes the system distributed: pull a job, do the work, store the result, mark it done. Running the API and the worker by hand in **separate terminals**, and then doing the **end-to-end test**, proved the whole pipeline actually flows — request in, queued, processed independently, result out — which is the core distributed-backend pattern working end to end. The **friction list** is the most important non-code deliverable of this phase: by writing down every annoyance (juggling multiple terminals, manually starting Postgres and Redis, wiring environment variables, "it works on my machine" fragility), you create the explicit motivation for the next phases — Docker and Compose exist to kill the startup pain, CI exists to catch the mistakes, and Kubernetes exists to run the workers reliably and at scale. Committing with conventional messages keeps the history clean and continues the habit you'll lean on once GitOps takes over deployment.
