"""Shared test fixtures."""

from collections.abc import AsyncIterator

import httpx
import pytest_asyncio

from orbit.main import create_app
from orbit.repositories.in_memory_run_repository import InMemoryRunRepository


@pytest_asyncio.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    """Provide an isolated API client with fresh in-memory state."""
    application = create_app(repository=InMemoryRunRepository())
    transport = httpx.ASGITransport(app=application)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as test_client:
        yield test_client
