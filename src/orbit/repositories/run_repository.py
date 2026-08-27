"""Persistence contract for job runs."""

from typing import Protocol
from uuid import UUID

from orbit.domain.run import Run


class RunRepository(Protocol):
    """Storage operations required by the run service."""

    async def add(self, run: Run) -> None:
        """Store a newly created run."""
        ...

    async def get(self, run_id: UUID) -> Run | None:
        """Return a run by ID, or None when it does not exist."""
        ...

    async def list_all(self) -> list[Run]:
        """Return all stored runs."""
        ...

