"""Pydantic schemas for the runs API."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints

from orbit.domain.run import RunStatus


JobName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=255),
]


class RunCreate(BaseModel):
    """Payload accepted when creating a run."""

    job_name: JobName


class RunResponse(BaseModel):
    """Public representation of a job run."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_name: str
    status: RunStatus
    created_at: datetime
    updated_at: datetime
