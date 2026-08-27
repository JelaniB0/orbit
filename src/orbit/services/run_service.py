"""Use cases for creating and reading job runs."""

from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID, uuid4

from orbit.domain.run import Run, RunStatus
from orbit.repositories.run_repository import RunRepository


class RunNotFoundError(Exception):
    """Raised when a requested run does not exist."""

    def __init__(self, run_id: UUID) -> None:
        self.run_id = run_id
        super().__init__(f"run {run_id} was not found")


class RunService:
    """Coordinate run use cases independently of HTTP and storage details."""

    def __init__(
        self,
        repository: RunRepository,
        *,
        id_factory: Callable[[], UUID] = uuid4,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._repository = repository
        self._id_factory = id_factory
        self._clock = clock or (lambda: datetime.now(UTC))

    async def create_run(self, job_name: str) -> Run:
        now = self._clock()
        run = Run(
            id=self._id_factory(),
            job_name=job_name,
            status=RunStatus.QUEUED,
            created_at=now,
            updated_at=now,
        )
        await self._repository.add(run)
        return run

    async def get_run(self, run_id: UUID) -> Run:
        run = await self._repository.get(run_id)
        if run is None:
            raise RunNotFoundError(run_id)
        return run

    async def list_runs(self) -> list[Run]:
        return await self._repository.list_all()

