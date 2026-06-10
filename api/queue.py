import os

from redis import Redis
from rq import Queue

from api.models import Job

red = Redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379"))
q = Queue(connection=red)


def enqueue_job(job: Job):
    return q.enqueue("worker.worker.process_job", str(job.id))
