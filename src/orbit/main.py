"""Orbit API application composition."""

from fastapi import FastAPI

from orbit.api.health import router as health_router
from orbit.api.runs import router as runs_router
from orbit.config import Settings
from orbit.repositories.in_memory_run_repository import InMemoryRunRepository
from orbit.repositories.run_repository import RunRepository
from orbit.services.run_service import RunService


def create_app(
    *,
    settings: Settings | None = None,
    repository: RunRepository | None = None,
) -> FastAPI:
    """Create and wire an Orbit API application."""
    resolved_settings = settings or Settings.from_environment()
    resolved_repository = repository or InMemoryRunRepository()

    application = FastAPI(title=resolved_settings.app_name)
    application.state.run_service = RunService(resolved_repository)
    application.include_router(health_router)
    application.include_router(runs_router)
    return application


app = create_app()

