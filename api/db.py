import uuid

import psycopg

from api.models import Job, Status


def create_table():
    with psycopg.connect("dbname=test user=postgres") as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS jobs(
                    id uuid PRIMARY KEY,
                    image_url text,
                    status text,
                    result_urls text[],
                    created_at timestamptz)
                """)

            conn.commit()


def insert_job(job: Job):
    with psycopg.connect("dbname=test user=postgres") as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO jobs (id, image_url, status, result_urls, created_at) "
                "VALUES (%s, %s, %s, %s, %s)",
                (job.id, job.image_url, job.status, job.result_urls, job.created_at),
            )


def update_job(job_id: uuid.UUID, status: Status, result_urls: list[str]):
    with psycopg.connect("dbname=test user=postgres") as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE jobs SET status = %s, result_urls = %s WHERE id = %s",
                (status, result_urls, job_id),
            )


def get_job(job_id: uuid.UUID):
    with psycopg.connect("dbname=test user=postgres") as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
            row = cur.fetchone()
    return row
