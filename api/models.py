import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class Status(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class JobCreate(BaseModel):
    image_url: str


class Job(JobCreate):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    status: Status = Status.QUEUED
    result_urls: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
