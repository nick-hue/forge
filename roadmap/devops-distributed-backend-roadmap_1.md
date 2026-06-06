# DevOps Roadmap: Build & Operate a Distributed Backend (Modern, Solo-Scale)

A hands-on path to learn how modern engineering organizations build, ship, run, scale, and observe a distributed backend — using current (2026) industry-standard tools and practices, deliberately scaled down so **one person can run the whole thing on a home server**.

The whole point is the **feedback loop**: build something, run it the painful manual way, feel why the pain exists, then automate it away with the same tooling real companies use. That "felt sense" is what turns DevOps from buzzwords into intuition. By the end you'll have a portfolio-grade project *and* a genuine opinion on whether you enjoy this style of work.

> **How this mirrors a real company.** The industry has moved from "DevOps" toward **platform engineering**: a small platform team builds a paved road (containers, GitOps, observability, autoscaling) that product engineers deploy onto. In this project *you are the entire platform team and the only product engineer* — the best possible way to see every layer end to end.

> **How to read each phase.** Every phase ends with two reference blocks: a **"Repo after this phase"** tree (new items marked `← new`) showing how the project grows, and a **"Tools introduced this phase"** block telling you what each new tool is, why it's there, and what to look up to implement it. The project is called `forge/`.

---

## The Project: "Forge" — a distributed thumbnail/processing service

A small but real distributed system. Users submit a job (an image URL) via an HTTP API; the work is queued; a pool of horizontally-scalable workers pulls jobs, does real CPU work (downloads the image, generates several thumbnail sizes), stores results, and records metadata. Job status is queryable via the API.

In plain terms: it's a **coat-check for image processing** — you hand it an image, get a ticket back immediately, workers do the resizing in the background, and you collect the finished thumbnails later with your ticket. The thumbnails are just an excuse for real background work; the *pattern* (API + queue + worker pool) is one of the most common backbones in real backend systems.

### Architecture

```
                    ┌─────────────┐
   client ───────►  │  API (HTTP) │   FastAPI
                    └──────┬──────┘
                           │ enqueue job
                           ▼
                    ┌─────────────┐
                    │   Broker    │   Redis (or RabbitMQ)
                    └──────┬──────┘
                           │ pull job
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         ┌────────┐   ┌────────┐   ┌────────┐
         │ Worker │   │ Worker │   │ Worker │   ← scale these
         └───┬────┘   └───┬────┘   └───┬────┘
             └────────────┼────────────┘
                          ▼
                  ┌────────────┐   ┌──────────┐
                  │ PostgreSQL │   │  Redis   │   (cache/results)
                  └────────────┘   └──────────┘

   OpenTelemetry ──► Prometheus (metrics) + Loki (logs) ──► Grafana
   Argo CD continuously syncs the cluster from your Git repo (GitOps)
```

> **On language choice.** I kept Python so you learn *DevOps* rather than fighting a new language — the platform layer is language-agnostic. But the cloud-native world (Docker, Kubernetes, Prometheus, Argo, OpenTofu) is overwhelmingly **Go**. If you finish and enjoy this, learning Go is the highest-leverage next step for a backend/platform CV, and rewriting the worker in Go is a great later challenge (tiny static-binary images too).

---

## Phase 0 — Foundations (½ day)

**Principle:** *Everything is code in Git.* Config, infrastructure, and pipelines all live in version control.

- Create the repo and folder skeleton.
- Set up **uv** for envs/deps and **ruff** for lint/format. Add **pre-commit** hooks so formatting/linting run automatically before each commit.
- Adopt modern workflow habits: **trunk-based development** (short-lived branches, merge to `main` often) and **conventional commits** (`feat:`, `fix:`…), which later enable automated versioning.
- Write a one-paragraph README; you'll grow it as you go.

### Repo after this phase

```
forge/
├── api/                      ← new  (empty for now — the HTTP service lives here)
├── worker/                   ← new  (empty for now — the background processor)
├── deploy/                   ← new  (empty for now — all deployment config)
├── .github/                  ← new  (empty for now — CI lives here)
├── .gitignore                ← new
├── .pre-commit-config.yaml   ← new  (auto-runs ruff before each commit)
├── pyproject.toml            ← new  (uv + ruff config, dependencies)
└── README.md                 ← new
```

**What was added & why:** just the empty skeleton and tooling config — no app code yet. The folders mark the three pieces of the system up front so everything has a home, and the config files mean quality and consistency are automated from commit #1.

### Tools introduced this phase

- **Git** — version control; the foundation everything else assumes. *Why now:* GitOps (Phase 5) makes Git the source of truth for production, so good habits start day one. *Implement / look up:* `git init`, a `.gitignore` for Python, and the **trunk-based development** branching model.
- **GitHub** — remote repo host; also runs your CI (Phase 3) and stores your images (ghcr, Phase 3). *Why now:* central home for code + automation. *Look up:* creating a repo, SSH keys for push access.
- **uv** — modern, very fast Python package & virtual-env manager (replaces pip + venv + poetry). *Why now:* reproducible dependency management from the start. *Implement / look up:* `uv init`, `uv add fastapi`, the `pyproject.toml` it generates.
- **ruff** — extremely fast Python linter *and* formatter in one (replaces flake8 + black + isort). *Why now:* catches mistakes and keeps style consistent automatically. *Look up:* `ruff check`, `ruff format`, configuring it in `pyproject.toml`.
- **pre-commit** — framework that runs checks (like ruff) automatically as a Git hook before each commit. *Why now:* makes quality automatic instead of relying on memory. *Implement / look up:* `.pre-commit-config.yaml`, then `pre-commit install`.
- **Conventional Commits** *(practice, not a tool)* — a commit-message convention (`feat:`, `fix:`, `chore:`). *Why now:* enables automated versioning/changelogs later and is near-universal in industry. *Look up:* the Conventional Commits spec.

---

## Phase 1 — Build the services, run them by hand (3–5 days)

**Principle:** *Feel the pain first.* Run everything manually so you understand what later automation removes.

- **API**: `POST /jobs` (accepts an image URL, returns `job_id`), `GET /jobs/{id}` (status + result links). On submit, push a task to Redis.
- **Worker**: pull a task, download the image, generate 3 thumbnail sizes (Pillow), store outputs, write metadata to Postgres, update status.
- Start Postgres, Redis, the API, and a worker in separate terminals, by hand.
- **Deliberately note the friction**: many things to start, env vars to wire, "works on my machine" fragility. That annoyance list is your motivation for everything that follows.

### Repo after this phase

```
forge/
├── api/
│   ├── main.py          ← new  (FastAPI app: POST /jobs, GET /jobs/{id})
│   ├── queue.py         ← new  (pushes a job onto Redis)
│   ├── db.py            ← new  (Postgres connection + queries)
│   └── models.py        ← new  (the shape of a "job")
├── worker/
│   ├── worker.py        ← new  (pulls jobs off the queue and runs them)
│   └── thumbnails.py    ← new  (the actual Pillow resize logic)
├── deploy/
├── .github/
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
└── README.md
```

**What was added & why:** the actual working software. `api/` is the front door that takes requests and queues work; `worker/` is the back room that does it. Everything in every later phase exists purely to ship, run, scale, and watch these two pieces reliably.

### Tools introduced this phase

- **FastAPI** — async Python web framework for the API. *Why here:* fast to write, validates requests automatically, and generates interactive API docs for free. *Implement / look up:* FastAPI "First Steps"; define `@app.post("/jobs")` and `@app.get("/jobs/{id}")`.
- **Uvicorn** — the ASGI server that actually runs your FastAPI app. *Why here:* FastAPI is the framework; Uvicorn is the engine that serves it. *Look up:* `uvicorn api.main:app --reload`.
- **Pydantic** — data-validation library (ships with FastAPI). *Why here:* defines the shape of a "job" and validates incoming requests. *Look up:* Pydantic `BaseModel` (this is your `models.py`).
- **Redis** — in-memory data store, used here as the **job queue/broker**. *Why here:* the API drops jobs in; workers pull them out. Fast and dead simple to start with. *Look up:* Redis lists/streams, or let your task library manage it.
- **Celery** (or **RQ**) — Python task-queue library that handles enqueueing jobs onto Redis and running worker processes. *Why here:* gives you retries, acknowledgements, and worker management instead of hand-rolling a queue. *Implement / look up:* Celery "First Steps with Celery" (RQ is a simpler alternative if Celery feels heavy).
- **PostgreSQL** — relational database for job metadata and results. *Why here:* the durable record of every job's status and output. *Look up:* basic `CREATE TABLE`, connecting from Python.
- **psycopg** (or **SQLAlchemy**) — the Python driver/ORM to talk to Postgres. *Why here:* this is your `db.py`. *Look up:* psycopg3 quickstart, or SQLAlchemy if you prefer an ORM.
- **Pillow** — Python image-processing library. *Why here:* does the real work — opening an image and producing thumbnail sizes. *Look up:* Pillow `Image.open()` and `.thumbnail()` (this is your `thumbnails.py`).

---

## Phase 2 — Containerize, the modern way (2–3 days)

**Principle:** *Reproducible, portable, secure-by-default environments.*

- Write **multi-stage** Dockerfiles for API and worker. Use slim/distroless final images and run as a **non-root** user (modern security baseline).
- Pin dependencies; produce reproducible builds.
- Write `docker-compose.yml` to bring up API + worker + Postgres + Redis with one command, with health checks and a shared network.
- **Win condition:** the entire system starts cold with a single command and zero local setup.

### Repo after this phase

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

**What was added & why:** a `Dockerfile` next to each service packages it into an identical, portable box that runs the same everywhere. `docker-compose.yml` wires all four pieces together so the whole system comes up with one command — directly killing the "five terminals" pain from Phase 1.

### Tools introduced this phase

- **Docker** — packages each service plus its dependencies into a portable image/container. *Why here:* solves "works on my machine" and is the unit Kubernetes will later run. *Implement / look up:* `Dockerfile` syntax, **multi-stage builds** (build deps in one stage, copy only the result into a small final image), running as a **non-root USER**.
- **Docker Compose** — runs multiple containers together from one YAML file. *Why here:* spins up API + worker + Postgres + Redis as one local stack with `docker compose up`. *Implement / look up:* `docker-compose.yml` services, `depends_on`, healthchecks, shared networks.
- **slim / distroless base images** *(technique)* — minimal container base images. *Why here:* smaller, faster, and far less to attack/scan. *Look up:* `python:3.x-slim`, Google's `distroless` images.
- **.dockerignore** *(file)* — excludes files from the build context. *Why here:* keeps images small and builds fast. *Look up:* `.dockerignore` syntax (mirror your `.gitignore`).

---

## Phase 3 — Continuous Integration with supply-chain checks (2–3 days)

**Principle:** *Catch problems automatically and early; ship only what's verified.*

- Write tests (API endpoint tests + a worker unit test).
- **GitHub Actions** on every push: install (cached) deps → lint → test → build both images.
- Add a **Trivy** scan of the built images to catch known vulnerabilities — image scanning is now expected in any serious pipeline.
- On `main`, push images to **ghcr.io** tagged with the commit SHA (immutable, traceable tags — never deploy `latest`).
- **Win condition:** a red pipeline blocks bad code; a green check means genuinely shippable, scanned images.

### Repo after this phase

```
forge/
├── api/
│   ├── tests/
│   │   └── test_api.py         ← new  (tests the endpoints)
│   ├── Dockerfile
│   └── ... (main.py, queue.py, db.py, models.py)
├── worker/
│   ├── tests/
│   │   └── test_thumbnails.py  ← new  (tests the resize logic)
│   ├── Dockerfile
│   └── ... (worker.py, thumbnails.py)
├── .github/
│   └── workflows/
│       └── ci.yml              ← new  (lint → test → build → Trivy scan → push to ghcr)
├── deploy/
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
└── README.md
```

**What was added & why:** `tests/` folders give the pipeline something to verify. `.github/workflows/ci.yml` is the robot that runs on every push — lint, test, build, scan, publish. From now on, broken or insecure code can't quietly reach a deployable state.

### Tools introduced this phase

- **GitHub Actions** — CI/CD automation that runs jobs on every push. *Why here:* this is the pipeline that enforces quality automatically. *Implement / look up:* `.github/workflows/ci.yml`, `on: push`, jobs/steps, dependency caching, the `docker/build-push-action`.
- **pytest** — Python test framework. *Why here:* defines the tests CI runs to verify your code still works. *Implement / look up:* `pytest` basics, FastAPI's `TestClient` for endpoint tests.
- **Trivy** — security scanner for container images and dependencies. *Why here:* fails the build if your image ships known vulnerabilities — now an expected pipeline step. *Implement / look up:* `aquasecurity/trivy-action` in your workflow.
- **GitHub Container Registry (ghcr.io)** — stores your built Docker images. *Why here:* the cluster pulls images from here to deploy them. *Implement / look up:* logging in with `GITHUB_TOKEN`, tagging images by commit **SHA** (never `latest`).

---

## Phase 4 — Orchestrate on k3s, by hand first (4–5 days)

**Principle:** *Declarative, self-healing infrastructure.* You declare desired state; Kubernetes maintains it.

- Install **k3s** on your Debian home server (`192.168.1.4`). Point `kubectl` at it from your laptop over Tailscale.
- Write manifests describing each piece. Expose the API via your existing **Nginx Proxy Manager** to a clean hostname over LAN/Tailscale.
- Apply manually with `kubectl apply` *this one time* to learn the primitives. Then delete a worker pod and watch it heal; `kubectl scale` the workers and watch throughput rise.
- **Win condition:** you understand Deployments, Services, and self-healing — the foundation GitOps will automate next.

### Repo after this phase

```
forge/
├── api/ ...
├── worker/ ...
├── deploy/
│   └── k8s/                          ← new  (raw Kubernetes manifests)
│       ├── api-deployment.yaml       ← new  (run N copies of the API)
│       ├── api-service.yaml          ← new  (stable network address for the API)
│       ├── worker-deployment.yaml    ← new  (run N copies of the worker)
│       ├── postgres-statefulset.yaml ← new  (the database + its persistent storage)
│       ├── redis-deployment.yaml     ← new  (the queue/cache)
│       └── configmap.yaml            ← new  (non-secret config)
├── .github/workflows/ci.yml
├── docker-compose.yml
├── ... (config files)
```

**What was added & why:** `deploy/k8s/` holds one manifest per piece — each a written declaration of "this is how many I want and how they run." It's the real-cluster equivalent of `docker-compose.yml`, but self-healing and scalable. You apply them by hand once, on purpose, before automating.

### Tools introduced this phase

- **k3s** — a lightweight, fully-conformant Kubernetes distribution in a single binary. *Why here:* real Kubernetes, but light enough for one home-server node. *Implement / look up:* the k3s install script; retrieving its kubeconfig.
- **Kubernetes** *(the platform)* — orchestrates containers: keeps the right number running, restarts crashed ones, scales them. *Why here:* the core skill of the whole roadmap. *Look up:* the objects below.
- **kubectl** — the CLI you use to talk to the cluster. *Why here:* apply manifests, inspect pods, scale, view logs. *Implement / look up:* `kubectl apply -f`, `get`, `describe`, `logs`, `scale`.
- **Kubernetes objects** *(what your manifests declare)* — *Why here:* each maps to a piece of your system. *Look up:* **Deployment** (stateless copies — API, workers), **Service** (stable internal address + load-balancing), **StatefulSet** + **PersistentVolume** (Postgres with durable storage), **ConfigMap** (non-secret config), **Secret** (sensitive config).
- **Nginx Proxy Manager** *(you already run this)* — reverse proxy / ingress. *Why here:* routes a clean hostname to the API's Service so you reach Forge over LAN/Tailscale. *Look up:* proxy hosts pointing at the k3s service address.
- **Tailscale** *(you already run this)* — private mesh VPN. *Why here:* lets your laptop's `kubectl` reach the home-server cluster securely from anywhere. *Look up:* using the Tailscale IP `100.99.6.113` in your kubeconfig.

---

## Phase 5 — GitOps: automated continuous deployment (4–6 days)

**Principle:** *Git is the single source of truth; the cluster syncs itself.* This is how modern companies do CD.

- Template the Phase 4 manifests with **Helm** (or Kustomize) so one source produces your config.
- Install **Argo CD** and point it at your repo's `deploy/` path. Now any commit CI built is **automatically reconciled onto the cluster** — nobody pushes to the cluster; the cluster pulls.
- Solve the secret-in-Git problem with **Sealed Secrets**: encrypt secrets so they're safe to commit and only the cluster can decrypt them.
- New workflow: commit → CI builds & scans → bump the image tag in Git → Argo CD syncs it → rollback is `git revert`.
- **Win condition:** you never touch the cluster directly to deploy; the repo *is* production.

### Repo after this phase

```
forge/
├── api/ ...
├── worker/ ...
├── deploy/
│   ├── chart/                      ← new  (the k8s/ manifests, now a templated Helm chart)
│   │   ├── Chart.yaml              ← new  (chart metadata)
│   │   ├── values.yaml             ← new  (image tags, replica counts — the knobs)
│   │   └── templates/              ← new  (the old manifests, now parameterized)
│   │       ├── api.yaml
│   │       ├── worker.yaml
│   │       ├── postgres.yaml
│   │       └── redis.yaml
│   ├── argocd/
│   │   └── application.yaml        ← new  (tells Argo CD which repo/path to watch)
│   └── secrets/
│       └── sealed-secret.yaml      ← new  (encrypted secrets, safe to commit)
├── .github/workflows/ci.yml
├── ... (config files)
```

**What was added & why:** the raw `k8s/` files graduate into a **Helm chart** where repeated values become knobs in `values.yaml`. `argocd/application.yaml` makes the cluster watch this repo and sync itself. `secrets/sealed-secret.yaml` lets passwords live safely in Git — the piece that makes "Git is the source of truth" actually work.

### Tools introduced this phase

- **Helm** (or **Kustomize**) — templating for Kubernetes manifests. *Why here:* removes copy-paste duplication and centralizes the "knobs" (image tag, replica count) in one `values.yaml`. *Implement / look up:* `helm create`, chart `templates/` + `values.yaml`. (Kustomize is the no-templating alternative — overlays instead of variables.)
- **Argo CD** — the GitOps continuous-deployment controller. *Why here:* watches your Git repo and continuously makes the cluster match it — the heart of modern CD. *Implement / look up:* installing Argo CD, the **Application** custom resource pointing at `deploy/chart/`, "auto-sync" + "self-heal".
- **Sealed Secrets** (or **SOPS**) — encrypts secrets so they can live safely in Git. *Why here:* GitOps needs *everything* in Git, but raw secrets can't be — this resolves that. *Implement / look up:* `kubeseal` to encrypt a Secret into a `SealedSecret` the cluster decrypts.
- **OpenTofu** (or **Terraform**) *(optional cloud stretch)* — Infrastructure as Code for provisioning cloud resources (VMs, networks). *Why here:* if you stand up a cloud node, you define it in code instead of clicking. *Implement / look up:* OpenTofu providers, `tofu plan` / `tofu apply`. (OpenTofu is the open-source fork of Terraform.)

---

## Phase 6 — Observability with OpenTelemetry (3–4 days)

**Principle:** *You can't operate what you can't see.* Modern observability = metrics + logs (+ traces), vendor-neutral.

- Instrument the API and workers with **OpenTelemetry**: request rate/latency, jobs processed, job duration, failures, and a custom **queue-depth** gauge (the heartbeat of the system).
- Deploy **Prometheus** (metrics) and **Loki** (structured JSON logs), visualized in **Grafana**. Build one dashboard: requests/sec, queue depth, worker throughput, error rate.
- *(Stretch)* Add **distributed tracing** (OTel → Tempo) to follow one job from API call through the queue to the worker.
- Wire a basic alert into your existing **Uptime Kuma** (API down, or queue depth stuck high).
- **Win condition:** with the dashboard open you can watch the system behave in real time and explain exactly what it's doing.

### Repo after this phase

```
forge/
├── api/
│   ├── telemetry.py           ← new  (OpenTelemetry setup for the API)
│   └── ...
├── worker/
│   ├── telemetry.py           ← new  (OpenTelemetry setup for the worker)
│   └── ...
├── deploy/
│   ├── chart/
│   │   └── templates/
│   │       ├── ... (api, worker, postgres, redis)
│   │       └── servicemonitor.yaml  ← new  (tells Prometheus what to scrape)
│   ├── observability/               ← new
│   │   ├── prometheus-values.yaml   ← new  (metrics collector config)
│   │   ├── loki-values.yaml         ← new  (log store config)
│   │   └── grafana-dashboard.json   ← new  (your saved dashboard)
│   ├── argocd/application.yaml
│   └── secrets/sealed-secret.yaml
├── .github/workflows/ci.yml
├── ... (config files)
```

**What was added & why:** `telemetry.py` makes each service *emit* numbers and logs about itself (the app stops being a black box). `deploy/observability/` stands up the tools that collect and display that data, and `servicemonitor.yaml` connects them by telling Prometheus where to look.

### Tools introduced this phase

- **OpenTelemetry (OTel)** — the vendor-neutral standard + SDK for emitting metrics, logs, and traces from your code. *Why here:* instrument once, send anywhere; it's what new code is written against. *Implement / look up:* the OTel Python SDK, auto-instrumentation for FastAPI, defining a custom counter/gauge (your queue-depth metric).
- **Prometheus** — time-series database that scrapes and stores metrics. *Why here:* collects the numbers your services emit and powers alerting. *Implement / look up:* the kube-prometheus-stack Helm chart, **ServiceMonitor** (how it discovers what to scrape), PromQL basics.
- **Loki** — log aggregation system (logs as a queryable store). *Why here:* centralizes your structured JSON logs next to your metrics. *Implement / look up:* Loki Helm chart, querying logs in Grafana with LogQL.
- **Grafana** — dashboards and visualization over Prometheus + Loki. *Why here:* the single pane of glass where you watch the system live. *Implement / look up:* adding data sources, building panels, exporting the dashboard JSON into your repo.
- **Tempo** *(optional stretch)* — distributed-tracing backend. *Why here:* lets you follow a single job across API → queue → worker. *Look up:* OTel traces → Tempo, viewing traces in Grafana.
- **Uptime Kuma** *(you already run this)* — uptime monitoring + alerting. *Why here:* simple, immediate alerts (API down, queue stuck) without building full alertmanager rules yet. *Look up:* HTTP/keyword monitors and notifications.

---

## Phase 7 — The demanding capstone (1 week)

This is where you find out if you actually like operating systems. Do all four:

1. **Load test & autoscale.** Hammer the API with **Locust**. Configure a **Horizontal Pod Autoscaler** to scale workers on CPU (stretch: on queue depth). Watch the system absorb a spike, then scale back; capture the Grafana graph.
2. **Chaos / reliability.** Kill a worker pod *mid-job*. Verify the job isn't lost — implement message acknowledgement so a crashed worker's job is redelivered. Teaches at-least-once delivery and idempotency.
3. **GitOps zero-downtime deploy.** Make a visible change (a 4th thumbnail size). Let CI build & scan it, bump the tag in Git, watch **Argo CD** roll it out with no dropped requests (verified by Locust running *during* the deploy), then practice instant rollback via `git revert`.
4. **Write a runbook.** One page: how a deploy flows, how to roll back, what each alert means and what to do.

### Repo after this phase (final)

```
forge/
├── api/ ...
├── worker/ ...
├── deploy/
│   ├── chart/
│   │   └── templates/
│   │       ├── ... (api, worker, postgres, redis, servicemonitor)
│   │       └── hpa.yaml          ← new  (HorizontalPodAutoscaler — auto-adds workers)
│   ├── observability/ ...
│   ├── argocd/ ...
│   └── secrets/ ...
├── loadtest/
│   └── locustfile.py             ← new  (defines the simulated traffic)
├── docs/
│   └── RUNBOOK.md                ← new  (operational playbook for the system)
├── .github/workflows/ci.yml
├── ... (config files)
```

**What was added & why:** `hpa.yaml` is the rule that scales workers up under load and back down when quiet — the payoff of the whole architecture. `loadtest/locustfile.py` generates the traffic to trigger it. `docs/RUNBOOK.md` is the human-facing operating instructions — the artifact interviewers love.

### Tools introduced this phase

- **Locust** (or **k6**) — load-testing tool that simulates many users hitting your API. *Why here:* generates the traffic that triggers autoscaling and reveals bottlenecks. *Implement / look up:* a Python `locustfile.py` with tasks hitting `POST /jobs`; the Locust web UI. (k6 is the JS/Go alternative if you prefer.)
- **HorizontalPodAutoscaler (HPA)** — built-in Kubernetes object that scales pods based on a metric. *Why here:* automatically adds/removes workers as load changes. *Implement / look up:* an `HorizontalPodAutoscaler` manifest targeting the worker Deployment, on CPU first (stretch: custom queue-depth metric).
- **metrics-server** — supplies the CPU/memory numbers HPA needs. *Why here:* HPA can't scale on CPU without it. *Look up:* installing metrics-server on k3s (it's often bundled — verify with `kubectl top pods`).
- **RUNBOOK.md** *(an artifact, not a tool)* — written operating procedures. *Why here:* proves you can *run* a system, not just build it; this is standard practice on real on-call teams. *Look up:* example SRE runbook templates.

---

## After the capstone: do you like this?

Reflect honestly — this is the real deliverable for your job search:

- Did the **build** phases (API + worker logic) energize you more than the **operate** phases (manifests, GitOps, dashboards, autoscaling)? → lean **Backend / Distributed Systems Engineer**.
- Did wiring the pipeline, watching Argo sync, and chasing the chaos failure feel like the fun part? → **Platform Engineering / SRE / DevOps** genuinely fits you.
- Enjoyed *both* roughly equally? → that's exactly the **ML Platform / Infrastructure Engineer** profile — a strong, in-demand niche.

Either way you'll have a portfolio-grade project demonstrating modern, real-world distributed-systems and platform skills.

---

## Suggested pace

A focused **6–8 weeks** part-time. Don't skip Phase 1's manual pain, the Phase 4 → 5 transition (manual `kubectl` *then* GitOps — the contrast is the lesson), or the Phase 7 chaos test. Those are where the real understanding lives.

---

## Tool index (quick lookup by phase)

| Phase | Tools introduced |
|-------|------------------|
| 0 — Foundations | Git, GitHub, uv, ruff, pre-commit, Conventional Commits |
| 1 — Build | FastAPI, Uvicorn, Pydantic, Redis, Celery/RQ, PostgreSQL, psycopg/SQLAlchemy, Pillow |
| 2 — Containerize | Docker, Docker Compose, slim/distroless images, .dockerignore |
| 3 — CI | GitHub Actions, pytest, Trivy, ghcr.io |
| 4 — Orchestrate | k3s, Kubernetes, kubectl, K8s objects (Deployment/Service/StatefulSet/ConfigMap/Secret), Nginx Proxy Manager, Tailscale |
| 5 — GitOps | Helm/Kustomize, Argo CD, Sealed Secrets/SOPS, OpenTofu (stretch) |
| 6 — Observability | OpenTelemetry, Prometheus, Loki, Grafana, Tempo (stretch), Uptime Kuma |
| 7 — Capstone | Locust/k6, HorizontalPodAutoscaler, metrics-server |
