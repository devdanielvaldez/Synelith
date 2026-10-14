# ADR 0001: Initial modular monolith and PubMed boundary

- Status: Accepted
- Date: 2026-10-13

## Context

NeuroGenesis AI needs an executable starting point for its research workspace and its first literature connector. The repository specification recommends a modular monolith and requires source-level provenance, bounded external access, explicit incomplete states, and a clean boundary between provider payloads and canonical contracts.

NCBI E-utilities documentation was rechecked on 2026-10-13. It requires `tool` and `email` parameters, supports JSON for ESearch and ESummary, and documents default limits of three requests per second without an API key and ten with a key. NCBI also warns that PubMed abstracts can be copyrighted. References:

- https://www.ncbi.nlm.nih.gov/books/NBK25497/
- https://www.ncbi.nlm.nih.gov/books/NBK25499/

## Decision

Start with a TypeScript/Next.js workspace, a Python/FastAPI API, shared TypeScript response contracts, and a separately importable Python connector package. The initial PubMed path retrieves metadata only through ESearch and ESummary. It records query, retrieval time, source hash, provider, schema version, completeness, and untrusted-content status.

The connector enforces the documented rate ceiling, identifies the application, uses bounded retries for network errors, HTTP 429, and server errors, and rejects malformed payloads. API failure is observable as an upstream error; partial data is not presented as complete.

Research-run creation currently produces a `planned` workflow only. It does not execute agents or claim that scientific work has completed.

## Consequences

- The vertical slice works without a database, so persistence, authentication, and immutable audit storage remain explicit follow-up work.
- Provider-specific parsing stays outside route handlers and can be tested with synthetic fixtures.
- Abstract or full-text ingestion requires a separate licensing decision and is out of scope for this slice.
- Python 3.11 and Node.js 20 remain the supported runtime baselines.
