# Orbit Roadmap

Orbit introduces technologies gradually. Each phase should have a working,
tested outcome before the next begins, and future-phase directories should not be
created as placeholders.

## Phase 0: Architecture and project foundations — complete

- Define domain vocabulary, system boundaries, and failure assumptions.
- Document the intended run state machine before implementing it.
- Record important decisions as ADRs.
- Establish repository guidance and a learning-oriented development process.

**Exit condition:** the architecture, roadmap, and initial decisions are understood
and accepted. There is no application code in this phase.

## Phase 1: Single-process API — current

- Establish the Python project and development toolchain.
- Implement framework-independent job and run domain behavior.
- Add a FastAPI HTTP boundary and in-memory repository.
- Support a small set of safe demonstration task types.
- Define validation, HTTP errors, state transitions, and idempotent submission.
- Add unit and API tests.

The first Phase 1 slice creates and reads queued run records only. Demonstration
task execution and idempotent submission remain later Phase 1 increments rather
than being introduced before their behavior is designed.

**Learning focus:** Python packaging, typing, dependency boundaries, HTTP API
semantics, validation, and testing.

## Phase 2: PostgreSQL persistence

- Replace in-memory persistence with PostgreSQL.
- Add schema migrations, constraints, transactions, and integration tests.
- Persist definitions, runs, attempts, schedules, and idempotency records.
- Coordinate basic scheduler polling and work claiming through PostgreSQL.

**Learning focus:** relational modeling, transaction isolation, concurrency,
locking, migrations, and durable state.

## Phase 3: Docker Compose

- Containerize the working API and worker.
- Run application processes and PostgreSQL through Docker Compose.
- Add health checks, volumes, networking, migration startup behavior, and graceful
  shutdown.

**Exit condition:** the PostgreSQL-backed system is dependable under Compose before
Kafka is introduced.

**Learning focus:** image construction, container networking, process lifecycle,
and reproducible local environments.

## Phase 4: Reliable execution

- Add worker leases and heartbeats.
- Implement cancellation, timeouts, retries, backoff, and attempt history.
- Prevent duplicate schedule occurrences.
- Reconcile abandoned or stuck work.
- Add failure-injection and concurrency tests.

**Learning focus:** delivery guarantees, state machines, crash recovery,
idempotency, and operational failure handling.

## Phase 5: Kafka messaging

- Introduce asynchronous run commands and lifecycle events.
- Implement a transactional outbox publisher.
- Build idempotent consumers around at-least-once delivery.
- Add event schema versioning, consumer groups, bounded retries, dead-letter
  handling, and replay exercises.
- Keep PostgreSQL authoritative for durable current state.

**Learning focus:** event-driven design, partitions and ordering, consumer
coordination, duplicate delivery, schema evolution, and replay.

## Phase 6: Redis for measured ephemeral needs

- Identify and document a concrete need before adding Redis.
- Use it only for data such as rate limits, short-lived worker presence, caches, or
  distributed concurrency tokens.
- Demonstrate that clearing Redis does not lose durable job state.

**Learning focus:** caching, expiry, ephemeral coordination, and consistency
tradeoffs.

## Phase 7: Distributed observability

- Emit correlated structured logs, metrics, and traces.
- Add OpenTelemetry instrumentation and a local Collector.
- Add Prometheus and Grafana dashboards and alerts.
- Add a trace backend when useful.
- Write runbooks for queue delay, failures, stuck runs, retry volume, consumer lag,
  and outbox backlog.

**Learning focus:** telemetry correlation, service-level indicators, alert design,
and diagnosing distributed workflows.

## Phase 8: MCP adapter

- Expose a small, safe set of tools for submitting, inspecting, listing, and
  cancelling runs.
- Implement MCP as a client of the Orbit API, not as a database client.
- Reuse API authorization rules and test tool boundaries and result sizes.

**Learning focus:** MCP tool design, safe interfaces, and adapter architecture.

## Phase 9: Kubernetes and Helm

- Move the complete, working Compose system to a local cluster such as `kind` or
  `k3d`.
- Add Deployments, Services, configuration, secrets, probes, resource requests and
  limits, migration Jobs, scaling, and graceful termination.
- Package deployable resources with Helm and validate environment-specific values.

Running stateful dependencies in local Kubernetes is a learning exercise, not a
claim of production readiness.

**Learning focus:** orchestration, scheduling, health semantics, configuration,
resource management, and packaging.

## Phase 10: CI/CD

- Use GitHub Actions for linting, type checks, unit and integration tests.
- Validate migrations, event compatibility, containers, and Helm charts.
- Add dependency and security checks appropriate to the project.
- Automate deployment only after the corresponding manual process is reliable.

**Learning focus:** reproducible verification, build pipelines, artifact handling,
and safe delivery.

## Phase 11: Terraform and AWS

- Move to AWS only after the entire system works locally.
- Estimate costs and configure budgets and billing alarms first.
- Use Terraform for networking, IAM, compute, secrets, and managed stateful
  services where they are appropriate and affordable.
- Define backups, recovery, and environment teardown.
- Re-evaluate whether managed Kafka or a simpler transport best fits the learning
  and cost goals.

**Learning focus:** infrastructure as code, cloud networking, identity, managed
services, operational cost, backup, and recovery.

## Ongoing rule

Progress is evidence-driven rather than calendar-driven. A technology enters Orbit
only when its phase begins and its purpose, operational cost, and simpler
alternatives have been explained.
