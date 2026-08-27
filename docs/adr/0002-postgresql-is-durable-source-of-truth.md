# ADR 0002: PostgreSQL is the durable source of truth

- **Status:** Accepted
- **Date:** 2026-08-27

## Context

Orbit will eventually use PostgreSQL, Kafka, and Redis. Each system offers different
durability, consistency, query, and coordination characteristics. Without explicit
ownership, the same job can appear to have conflicting states across stores, and
recovery after a crash or outage becomes ambiguous.

Users need a clear, durable answer to whether a job was accepted and what its
current state is. Scheduling, retry, cancellation, and idempotency also require
transactional invariants. Kafka is valuable for buffering, decoupling, replay, and
consumer scaling, while Redis is valuable for low-latency ephemeral data; neither
should create a second authority for current job state.

## Decision

PostgreSQL is Orbit's authoritative durable source of truth. It will store job
definitions, schedules, runs, attempts, state transitions, retry and cancellation
intent, leases, idempotency records, and transactional outbox records.

When Kafka is introduced, it will serve as asynchronous transport and a durable
event log. Orbit will assume at-least-once delivery, so events have stable
identifiers and consumers are idempotent. User-visible current state remains
grounded in PostgreSQL, while Kafka-derived projections are rebuildable.

Redis, when a measured need justifies adding it, will hold only ephemeral or
reconstructable state such as caches, rate-limit counters, worker presence, or
short-lived coordination tokens. Losing all Redis data must not lose accepted jobs
or their durable history.

The API will acknowledge job acceptance only after the relevant PostgreSQL
transaction commits. When publishing to Kafka is required, the same transaction
will create an outbox record, and a publisher will retry delivery independently.

## Consequences

### Benefits

- There is one authoritative answer for current durable job state.
- Relational constraints and transactions protect state transitions and
  idempotency.
- Kafka or Redis outages do not create ambiguous ownership.
- Kafka consumers and Redis-backed features can rebuild derived state.
- The transactional outbox closes the gap between database commit and event
  publication.

### Costs and risks

- PostgreSQL is on the critical path for accepting and updating durable work.
- Its availability, backups, migrations, and capacity require careful operation.
- High write volume may eventually require optimization or partitioning.
- Applications must resist treating convenient Kafka events or Redis caches as
  authoritative.

These costs are accepted because clear correctness and recovery semantics are more
important than early independent storage or speculative scale.

## Alternatives considered

### Kafka as the sole source of truth

Rejected for the initial architecture. Event sourcing would add projection,
rebuild, schema evolution, and consistency complexity before Orbit needs it, while
making ordinary current-state queries harder to reason about.

### Redis as the job queue and state store

Rejected because durable job truth should not depend on an ephemeral coordination
system, and the early PostgreSQL design can already provide transaction-safe
claiming and scheduling.

### Separate authoritative databases per component

Rejected during the modular-monolith stages because it would introduce distributed
data ownership and consistency problems before independently deployed services are
justified.

