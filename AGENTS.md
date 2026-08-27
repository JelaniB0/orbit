# Repository Instructions

These instructions apply to the entire Orbit repository.

## Project intent

Orbit is a learning-focused distributed job orchestration project. Its purpose is
to teach production backend engineering and distributed-systems practices through
deliberate, incremental implementation.

- Explain important architectural changes and their tradeoffs before implementing
  them. Preserve opportunities for the project owner to learn and make decisions.
- Prefer the simplest implementation that satisfies the current phase over
  premature abstraction or speculative infrastructure.
- Follow `docs/ROADMAP.md`. Do not introduce a roadmap technology before its phase
  or create placeholder scaffolding for future phases.
- Do not prematurely split Orbit into microservices. Begin as a modular monolith
  with explicit internal boundaries and extract deployable services only when a
  demonstrated operational or scaling need justifies the split.

## Implementation standards

- Explain the purpose and tradeoffs of every new dependency before adding it.
- Include appropriate tests with every implementation change.
- Run the relevant tests after changing code and report the results. If tests
  cannot be run, explain why.
- Use Python type hints throughout application and test code.
- Use structured logging instead of `print` statements in application code.
- Read runtime configuration and secrets from environment variables. Never commit
  credentials, tokens, private keys, or other secrets.
- Keep domain and business logic independent of web frameworks, message brokers,
  databases, and other infrastructure where practical.
- Do not create a generic `common` package that accumulates unrelated logic. Name
  shared packages after a cohesive capability and keep their APIs narrow.
- Preserve explicit job state transitions and make concurrent operations
  idempotent where required.

## Architecture and data rules

- PostgreSQL is Orbit's authoritative durable source of truth.
- Redis may contain only ephemeral or reconstructable data. Loss of Redis data
  must not cause loss of durable job state.
- When Kafka is introduced, design for at-least-once delivery and idempotent
  consumers. Kafka is transport and an event log, not the sole store of current
  user-visible state.
- MCP is an adapter over the Orbit API and must not access the database directly.
- Observability failures must not prevent core job processing.

## Documentation

- Keep documentation synchronized with behavior and architecture.
- Update architectural documentation when an architectural decision changes.
- Record major architectural decisions and meaningful reversals as ADRs under
  `docs/adr/`.
- Do not rewrite an accepted ADR to hide a later decision. Add a new ADR that
  supersedes it.

