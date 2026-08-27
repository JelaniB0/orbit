"""FastAPI dependency adapters."""

from fastapi import Request

from orbit.services.run_service import RunService


async def get_run_service(request: Request) -> RunService:
    """Return the application-scoped run service."""
    service: RunService = request.app.state.run_service
    return service
