# ADR 0001: Start as a modular monolith

- **Status:** Accepted
- **Date:** 2026-08-27

## Context

Orbit is intended eventually to teach distributed job orchestration and may grow
into several independently deployed processes. The planned capabilities include an
API, scheduling, execution, reconciliation, event projection, and an MCP adapter.

Beginning with microservices would require service discovery, network contracts,
deployment coordination, distributed tracing, message delivery, and cross-service
failure handling before Orbit has validated its core domain model. That operational
work would obscure early lessons about job semantics and create boundaries based on
speculation rather than observed needs.

## Decision

Orbit will begin as a modular monolith. Domain responsibilities will have explicit
module boundaries and narrow interfaces, but they may run in one process or share a
codebase and PostgreSQL schema during early phases.

The API and worker may become separate processes when asynchronous execution is
introduced, while continuing to share deliberately scoped domain packages. Other
components, including scheduler and reconciler responsibilities, will be extracted
only when isolation, independent scaling, reliability, or ownership creates a
demonstrated reason.

We will not scaffold empty future services or create separate databases merely to
resemble the eventual topology.

## Consequences

### Benefits

- The core state machine and business rules can be learned and tested without
  distributed operational overhead.
- Refactoring module boundaries is cheaper before network contracts harden them.
- Local development remains fast and free.
- Each later service extraction can teach a real tradeoff and solve a measured
  problem.

### Costs and risks

- Module boundaries rely on engineering discipline rather than network isolation.
- Shared deployment initially prevents independent scaling and release cycles.
- Careless imports or a generic shared package could create tight coupling and make
  later extraction difficult.

These risks are managed with framework-independent domain logic, cohesive packages,
explicit interfaces, tests, and architecture reviews before significant changes.

## Alternatives considered

### Start with microservices

Rejected because it introduces distributed failure modes and deployment complexity
before the domain and scaling requirements are known.

### Build an unstructured monolith and split it later

Rejected because implicit boundaries make later extraction costly. A modular
monolith preserves simplicity while still making ownership and dependencies
deliberate.

### Build all planned deployables in one repository immediately

Rejected because empty scaffolding creates false structure, encourages premature
contracts, and conflicts with Orbit's phased learning approach.

