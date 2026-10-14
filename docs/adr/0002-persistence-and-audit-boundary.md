# ADR 0002: Transactional persistence and audit boundary

- Status: Accepted
- Date: 2026-10-13

## Context

Projects and research plans must survive process restarts and retain enough history for later scientific audit. The API also needs isolated asynchronous sessions so concurrent requests never share mutable transaction state.

## Decision

Use SQLAlchemy 2.x asynchronous engines and one `AsyncSession` per request. PostgreSQL with the asyncpg driver is the production and local-compose database; SQLite with aiosqlite is used only for isolated automated tests.

Alembic owns schema evolution. The application does not call `create_all` during startup. Local Docker Compose applies migrations before starting the API, while production deployment must run the same migration command as a controlled release step.

The initial migration creates `projects`, `sources`, `papers`, `claims`, `research_runs`, and `audit_events`. Creating a project or planning a research run writes its domain row and audit event in the same transaction. Audit events have no application update or delete path.

References checked on 2026-10-13:

- https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- https://alembic.sqlalchemy.org/en/latest/cookbook.html#using-asyncio-with-alembic

## Consequences

- A research run must reference an existing project UUID; placeholder project identifiers are rejected.
- Failed transactions cannot leave a successful domain write without its corresponding audit event.
- Database migrations are explicit, reviewable artifacts and can be tested independently of API startup.
- Database-level append-only enforcement and cryptographic audit chaining remain future hardening work; the current boundary prevents mutation through the application API only.
