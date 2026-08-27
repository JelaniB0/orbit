"""Health-check route."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    """Report that the API process is responsive."""
    return {"status": "ok"}

