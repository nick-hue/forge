from redis import Redis
from rq import Queue

from api.models import Job

red = Redis()
q = Queue(connection=red)


def enqueue_job(job: Job):
    return q.enqueue("worker.worker.process_job", str(job.id))
