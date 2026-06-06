# Phase 2 — Containerize, the Modern Way

**Goal:** package the API and the worker into portable, reproducible, secure-by-default container images, and wire the whole system (API + worker + Postgres + Redis) together so it starts cold with a *single command*. This directly kills the "five terminals, manual setup" friction you felt in Phase 1.

**Estimated time:** 2–3 days

---

## Tasks

Complete every box before moving to Phase 3.

- [ ] Write a `.dockerignore` (mirror your `.gitignore`) so junk and secrets stay out of the build context and images stay small.
- [ ] Write a **multi-stage** `api/Dockerfile`: a builder stage that installs dependencies with uv, and a slim final stage that copies only what's needed to run.
- [ ] Write a **multi-stage** `worker/Dockerfile` the same way.
- [ ] Use a **slim** (or **distroless**) base image for the final stage so there's less to ship, scan, and attack.
- [ ] Run each container as a **non-root** `USER` in the final stage (modern security baseline).
- [ ] Ensure **reproducible builds** by installing from the pinned lockfile (e.g. `uv sync --frozen`), not floating versions.
- [ ] Build both images locally and confirm each runs on its own.
- [ ] Write `docker-compose.yml` defining four services: `api`, `worker`, `postgres`, `redis`.
- [ ] Give the services a **shared network**, `depends_on`, and **healthchecks** (especially for Postgres/Redis) so they come up in the right order.
- [ ] Pass configuration (DB URL, Redis URL, etc.) via **environment variables** in Compose instead of hardcoding it.
- [ ] Bring the whole stack up with `docker compose up` and re-run the **Phase 1 end-to-end test** against it.
- [ ] Commit your work with conventional commits (e.g. `feat: containerize api and worker with docker compose`).

**Done when:** the entire system starts cold with a single `docker compose up` and zero local setup — no hand-started Postgres/Redis, no juggling terminals — and the end-to-end image-to-thumbnail flow still works.

---

## What each task did

Writing a `.dockerignore` first means every later build skips your `.venv`, caches, and `.env` — keeping images small, builds fast, and secrets out of the image. The **multi-stage Dockerfiles** for the API and worker are the heart of this phase: a heavy builder stage installs dependencies, then a clean **slim/distroless** final stage copies only the finished application and its runtime deps, so the image you actually ship is small and contains none of the build tooling. Running as a **non-root user** and installing from the **pinned lockfile** are the two modern defaults that make the image both safer (a compromised process isn't root) and reproducible (the same build today and in six months), which is exactly what a real CI pipeline and cluster expect.

The `docker-compose.yml` then ties the four pieces — API, worker, Postgres, Redis — into one declared stack on a shared network, with `depends_on` and **healthchecks** so the app doesn't start talking to a database that isn't ready yet, and **environment variables** so configuration lives outside the image. Bringing it all up with one `docker compose up` and re-running the Phase 1 end-to-end test is the win condition: the painful manual startup from Phase 1 collapses into a single command that works the same on any machine. This is also the moment your code stops being "works on my machine" and becomes a portable unit — the exact unit Kubernetes will later run in Phase 4. Committing with conventional messages keeps the clean, machine-readable history going.

---

## Repo after this phase

```
forge/
├── api/
│   ├── Dockerfile       ← new  (multi-stage, non-root image for the API)
│   ├── main.py
│   ├── queue.py
│   ├── db.py
│   └── models.py
├── worker/
│   ├── Dockerfile       ← new  (multi-stage, non-root image for the worker)
│   ├── worker.py
│   └── thumbnails.py
├── deploy/
├── .github/
├── docker-compose.yml   ← new  (starts API + worker + Postgres + Redis at once)
├── .dockerignore        ← new  (keeps junk out of the image build)
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
└── README.md
```

---

## Tools introduced this phase

- **Docker** — packages each service plus its dependencies into a portable image/container. *Why here:* solves "works on my machine" and is the unit Kubernetes will later run. *Implement / look up:* `Dockerfile` syntax, **multi-stage builds**, running as a **non-root USER**.
- **Docker Compose** — runs multiple containers together from one YAML file. *Why here:* spins up API + worker + Postgres + Redis as one local stack with `docker compose up`. *Implement / look up:* `docker-compose.yml` services, `depends_on`, healthchecks, shared networks.
- **slim / distroless base images** *(technique)* — minimal container base images. *Why here:* smaller, faster, far less to attack/scan. *Look up:* `python:3.x-slim`, Google's `distroless` images.
- **.dockerignore** *(file)* — excludes files from the build context. *Why here:* keeps images small and builds fast. *Look up:* `.dockerignore` syntax (mirror your `.gitignore`).
