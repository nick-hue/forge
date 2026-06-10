import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from api.db import create_table, get_job, insert_job
from api.models import Job, JobCreate
from api.queue import enqueue_job


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_table()
    yield

app = FastAPI(lifespan=lifespan)


@app.post("/jobs", status_code=202)
async def create_job(payload: JobCreate):
    job = Job(image_url=payload.image_url)

    insert_job(job)
    enqueue_job(job)

    return {"job_id": job.id}


@app.get("/jobs/{job_id}")
async def read_job(job_id: uuid.UUID):
    job = get_job(job_id=job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"job": job}
