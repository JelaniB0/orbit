"""Tests for the runs API."""

from datetime import datetime
from uuid import UUID, uuid4

import httpx
import pytest


@pytest.mark.asyncio
async def test_create_run_returns_created_run_in_queued_state(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post("/runs", json={"job_name": "example-job"})

    assert response.status_code == 201
    body = response.json()
    assert UUID(body["id"])
    assert body["job_name"] == "example-job"
    assert body["status"] == "QUEUED"
    assert datetime.fromisoformat(body["created_at"]).tzinfo is not None
    assert datetime.fromisoformat(body["updated_at"]).tzinfo is not None
    assert body["created_at"] == body["updated_at"]


@pytest.mark.asyncio
async def test_retrieve_run(client: httpx.AsyncClient) -> None:
    created = (await client.post("/runs", json={"job_name": "retrievable-job"})).json()

    response = await client.get(f"/runs/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


@pytest.mark.asyncio
async def test_list_runs(client: httpx.AsyncClient) -> None:
    first = (await client.post("/runs", json={"job_name": "first-job"})).json()
    second = (await client.post("/runs", json={"job_name": "second-job"})).json()

    response = await client.get("/runs")

    assert response.status_code == 200
    assert response.json() == [first, second]


@pytest.mark.asyncio
async def test_nonexistent_run_returns_not_found(client: httpx.AsyncClient) -> None:
    response = await client.get(f"/runs/{uuid4()}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Run not found"}


@pytest.mark.asyncio
async def test_generated_run_ids_are_unique(client: httpx.AsyncClient) -> None:
    first = (await client.post("/runs", json={"job_name": "first-job"})).json()
    second = (await client.post("/runs", json={"job_name": "second-job"})).json()

    assert first["id"] != second["id"]
