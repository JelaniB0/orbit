"""In-memory run persistence for the first implementation phase."""

import asyncio
from uuid import UUID

from orbit.domain.run import Run


class InMemoryRunRepository:
    """Store runs in one process; all data is lost on restart."""

    def __init__(self) -> None:
        self._runs: dict[UUID, Run] = {}
        self._lock = asyncio.Lock()

    async def add(self, run: Run) -> None:
        async with self._lock:
            self._runs[run.id] = run

    async def get(self, run_id: UUID) -> Run | None:
        async with self._lock:
            return self._runs.get(run_id)

    async def list_all(self) -> list[Run]:
        async with self._lock:
            return list(self._runs.values())

