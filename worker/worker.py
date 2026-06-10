from pathlib import Path
from uuid import UUID

import requests

from api.db import get_job, update_job
from api.models import Status
from worker.thumbnails import make_thumbnails


def process_job(job_id: str):
    jid = UUID(job_id)

    job = get_job(job_id=jid)

    try:
        update_job(job_id=jid, status=Status.PROCESSING, result_urls=[])

        img_url = job[1]
        response = requests.get(url=img_url)
        response.raise_for_status()

        output_dir = Path("data") / job_id
        output_dir.mkdir(parents=True, exist_ok=True)

        result_paths = make_thumbnails(
            image_bytes=response.content, output_dir=output_dir
        )

        update_job(job_id=jid, status=Status.DONE, result_urls=result_paths)
    except Exception as e:
        print(f"job {job_id} failed: {e}")
        update_job(job_id=jid, status=Status.FAILED, result_urls=[])
