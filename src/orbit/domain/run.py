"""Domain model for a job run."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class RunStatus(StrEnum):
    """Lifecycle states currently recognized for a run."""

    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True, slots=True)
class Run:
    """One requested execution of a named job."""

    id: UUID
    job_name: str
    status: RunStatus
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if not self.job_name.strip():
            raise ValueError("job_name must not be empty")
        if self.created_at.tzinfo is None or self.updated_at.tzinfo is None:
            raise ValueError("run timestamps must be timezone-aware")
        if self.updated_at < self.created_at:
            raise ValueError("updated_at must not be earlier than created_at")

