"""HTTP routes for job runs."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from orbit.api.dependencies import get_run_service
from orbit.schemas.run import RunCreate, RunResponse
from orbit.services.run_service import RunNotFoundError, RunService

router = APIRouter(prefix="/runs", tags=["runs"])
RunServiceDependency = Annotated[RunService, Depends(get_run_service)]


@router.post("", response_model=RunResponse, status_code=status.HTTP_201_CREATED)
async def create_run(payload: RunCreate, service: RunServiceDependency) -> RunResponse:
    """Create a queued job run."""
    run = await service.create_run(payload.job_name)
    return RunResponse.model_validate(run)


@router.get("/{run_id}", response_model=RunResponse)
async def get_run(run_id: UUID, service: RunServiceDependency) -> RunResponse:
    """Retrieve one run by ID."""
    try:
        run = await service.get_run(run_id)
    except RunNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        ) from error
    return RunResponse.model_validate(run)


@router.get("", response_model=list[RunResponse])
async def list_runs(service: RunServiceDependency) -> list[RunResponse]:
    """List all current runs."""
    runs = await service.list_runs()
    return [RunResponse.model_validate(run) for run in runs]

