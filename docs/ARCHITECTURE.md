# Orbit Architecture

## Status and scope

This document describes Orbit's intended architecture. Orbit is currently in
Phase 1. Only the single-process API and in-memory repository are implemented; the
remaining services and infrastructure below are architectural targets.

Orbit begins as a modular monolith. Domain boundaries will be represented in code
before they become independently deployable services. Components should be split
only when isolation, scaling, reliability, or ownership provides a concrete reason.

## Core model

Orbit distinguishes three related concepts:

- A **job definition** describes reusable work: its task type, validated inputs,
  timeout, retry policy, and other execution requirements.
- A **job run** represents one requested or scheduled execution of a job
  definition. It owns the user-visible lifecycle and terminal outcome.
- A **job attempt** represents one execution attempt within a run. Retries create
  new attempts rather than erasing the history of earlier ones.

The exact state machine will be specified before implementation. Its expected shape
includes queued, dispatched, running, succeeded, failed, retry-waiting, and
cancelled states. All transitions must be explicit and guarded so duplicate or
concurrent operations are safe.

## Planned components and responsibilities

### API

The API is Orbit's public control plane. It will:

- create and inspect job definitions, schedules, runs, and execution history;
- accept submissions, cancellations, and retries;
- validate input and later enforce authentication and authorization;
- durably accept a run before returning its identifier;
- provide health and readiness endpoints; and
- publish accepted work asynchronously once Kafka is introduced.

FastAPI is planned for the HTTP boundary, while business rules should remain in
framework-independent domain code where practical.

### Scheduler

The scheduler determines when scheduled work is due. It will create runs, prevent
duplicate schedule occurrences, dispatch runnable work, define catch-up behavior,
and recover occurrences missed during downtime. It initially uses PostgreSQL and
may begin as a process sharing the modular monolith's domain code.

### Worker

Workers execute supported task types outside the API request lifecycle. A worker
claims an attempt, runs it, records timing and results, emits heartbeats for
long-running work, observes cancellation and timeouts, and reports its outcome.
Early task types will be controlled and safe; arbitrary user-supplied shell
execution is outside the initial scope because it requires strong isolation.

### Reconciler

The reconciler repairs state after crashes and partial failures. It detects expired
leases and stuck runs, requeues retryable work, marks exhausted or timed-out work,
and repairs missed schedules. It should initially live with scheduler functionality
and become separately deployable only if justified.

### Event projector

After Kafka exists, a projector may consume lifecycle events to maintain
read-friendly status, timelines, and operational summaries. Before that phase,
PostgreSQL directly serves authoritative writes and reads. Any projected view is
derived and rebuildable.

### MCP server

MCP is an adapter over the Orbit API. It may expose bounded tools for submitting,
inspecting, listing, and cancelling runs, but it must use the same API contracts and
authorization rules as other clients. It must not query or mutate PostgreSQL
directly and must not duplicate domain logic.

## Communication model

### Synchronous communication

HTTP is appropriate when a caller needs an immediate control-plane response:

- managing job definitions and schedules;
- submitting a run and receiving its identifier;
- reading status and execution history;
- requesting cancellation or retry;
- MCP-to-API calls; and
- health and readiness probes.

A submission will eventually return after durable acceptance, normally as
`202 Accepted` with a run identifier, rather than waiting for execution. During
the in-memory Phase 1 API, creating the run resource returns `201 Created`.
Internal synchronous
chains through the scheduler and worker are avoided because they couple user-facing
availability and latency to background execution.

### Asynchronous communication

Work that benefits from buffering, independent scaling, or retry is asynchronous:

- dispatching runs;
- worker lifecycle and heartbeat events;
- completion and failure reporting;
- retry requests;
- projections, audit consumers, and future notifications.

Cancellation begins as a synchronous request that durably records intent. Applying
that intent to running work is asynchronous and subject to explicit race rules.

## Data ownership

Orbit starts with one PostgreSQL instance and one logical application schema. It
does not begin with a database per module. PostgreSQL is authoritative for job
definitions, schedules, runs, attempts, retry counters, cancellation intent,
leases, idempotency records, audit metadata, and transactional outbox records.

Logical ownership is enforced before physical separation:

- job management owns definitions and submission;
- scheduling owns evaluation of schedules and occurrence creation;
- execution owns attempts, leases, and execution outcomes; and
- projection owns only derived, rebuildable read models.

Modules should interact through explicit interfaces rather than opportunistically
depending on one another's persistence details. Separate databases are considered
only if independently operating a component later makes them necessary.

Redis will be introduced only for a measured need such as rate limiting, caches,
short-lived worker presence, or concurrency tokens. Redis data must remain
ephemeral or reconstructable; deleting it must not destroy durable job state.

## Eventual Kafka flow

Kafka is introduced only after the API, PostgreSQL persistence, and reliable basic
execution work. A likely initial topic design is:

- `orbit.run.commands` for executable run commands;
- `orbit.run.events` for run and attempt lifecycle events;
- `orbit.worker.events` for worker lifecycle information; and
- `orbit.dead-letter` for records that exhaust bounded processing retries.

The intended flow is:

1. In one PostgreSQL transaction, the API inserts a queued run and a `RunRequested`
   outbox record.
2. An outbox publisher sends the record to `orbit.run.commands` and records that it
   was published.
3. A worker consumes the command and atomically claims the run or attempt.
4. The worker executes it and emits events such as `RunStarted`, `RunSucceeded`, or
   `RunFailed`.
5. Control-plane consumers apply valid state transitions and project read models.

The transactional outbox prevents a committed run from being stranded when a
process crashes before publication. Kafka uses at-least-once delivery semantics;
producers and consumers must tolerate duplicates. Events carry stable identifiers,
and consumers use identifiers and expected state or version to behave idempotently.
Where per-run ordering matters, `run_id` is the partition key. Global ordering is
not assumed.

Kafka is transport and a durable event log, not the only source of current
user-visible truth. A dead-letter topic supports investigation and recovery; it is
not a substitute for monitoring or ownership of failures.

## Failure model

Orbit assumes processes can crash, networks can partition or time out, messages can
be duplicated, and dependencies can be unavailable.

| Failure | Intended response |
| --- | --- |
| Client retries after a timeout | Use an idempotency key and return the existing run. |
| Kafka delivers a command more than once | Claim atomically and make consumers and state transitions idempotent. |
| Worker crashes before starting | Expire its dispatch lease and let reconciliation safely requeue work. |
| Worker crashes during execution | Expire heartbeats, retain attempt history, and retry only under explicit policy. External side effects require task-level idempotency. |
| Database commit succeeds but publication fails | Persist an outbox record in the same transaction and retry publication. |
| Publication succeeds but acknowledgement is lost | Deduplicate with stable event identifiers and idempotent handling. |
| Multiple scheduler instances see the same occurrence | Use database constraints, row locking, and occurrence identifiers. |
| Kafka is unavailable | Continue durable acceptance within capacity and accumulate outbox records for later publication. |
| PostgreSQL is unavailable | Reject durable writes clearly, normally with `503`; never claim a run was accepted. |
| A poison event repeatedly fails | Validate schemas, use bounded retries, dead-letter it, and alert. |
| A dependency causes a retry storm | Apply exponential backoff, jitter, attempt limits, and concurrency controls. |
| Completion races with cancellation | Resolve with explicit atomic transition rules and preserve the winning durable outcome. |
| Scheduler downtime or clock error | Use UTC, database time where important, unique occurrence identities, and documented catch-up policy. |

Not every external side effect can be made exactly once. Orbit will expose this
reality rather than promise impossible guarantees; tasks may need idempotency keys
or a review-required/unknown outcome.

## Observability architecture

Once the workflow crosses process boundaries, Orbit will emit correlated structured
logs, metrics, and traces. Run, attempt, event, and trace identifiers will support
navigation across signals.

- Application processes emit OpenTelemetry telemetry.
- An OpenTelemetry Collector receives, processes, and exports it.
- Prometheus stores and queries operational metrics.
- Grafana presents dashboards and alerts.
- A local trace backend such as Jaeger or Grafana Tempo may store distributed
  traces when tracing is introduced.

Key signals will include submission and execution rates, queue delay, end-to-end
latency, failure and retry rates, stuck runs, lease expiration, consumer lag, and
outbox backlog. Observability is best-effort: an unavailable telemetry pipeline
must not prevent durable acceptance or execution of jobs.

## Deployment evolution

Orbit must work through its simpler deployment model before adopting the next one:

1. local processes;
2. Docker Compose;
3. a complete local distributed system including Kafka and observability;
4. local Kubernetes with Helm; and
5. AWS infrastructure managed by Terraform.

The repository gains directories and deployment assets only when their roadmap
phase begins.
