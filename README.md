# Orbit

> **Status: under active development — Phase 1 (single-process API).**

Orbit is a learning-focused distributed job orchestration platform. It is intended
to grow from a small, well-structured Python application into a locally operable
distributed system while teaching production backend engineering, distributed
systems, containers, infrastructure, and observability.

Orbit currently provides a small FastAPI control-plane API backed by process-local,
in-memory storage. It can create and retrieve queued run records, but it does not
yet execute jobs and all run data is lost when the process stops.

## Current API

- `GET /health`
- `POST /runs`
- `GET /runs`
- `GET /runs/{run_id}`

This deliberately small first implementation teaches API structure, domain
modeling, dependency injection, and testing before durable or distributed
infrastructure is introduced.

## Local development

Install the project and its development dependencies:

```console
uv sync
```

Run the test suite:

```console
uv run pytest
```

Start the API with automatic reload:

```console
uv run uvicorn orbit.main:app --reload
```

The API is then available at `http://127.0.0.1:8000`, with interactive OpenAPI
documentation at `http://127.0.0.1:8000/docs`.

## Planned technology progression

Technologies will be introduced only when the project reaches the phase where they
solve a concrete problem:

1. Python and FastAPI for the initial API and domain model
2. PostgreSQL for durable state, transactions, and coordination
3. Docker and Docker Compose for repeatable local operation
4. Apache Kafka for asynchronous commands and lifecycle events
5. Redis for explicitly ephemeral or reconstructable coordination data
6. OpenTelemetry, Prometheus, and Grafana for distributed observability
7. MCP as an adapter over Orbit's public API
8. Kubernetes and Helm after the complete system works with Docker Compose
9. GitHub Actions for automated verification and delivery workflows
10. Terraform and AWS only after the entire system works locally

The plan intentionally avoids adopting infrastructure for resume value alone. See
[the architecture](docs/ARCHITECTURE.md), [the roadmap](docs/ROADMAP.md), and
[the architecture decision records](docs/adr/) for the current design.

## Design principles

- Start as a modular monolith and split services only for demonstrated reasons.
- Keep PostgreSQL as the durable source of truth.
- Prefer explicit state transitions, idempotency, and recoverability.
- Keep domain logic as independent from frameworks and infrastructure as practical.
- Build and understand one operational layer at a time.
