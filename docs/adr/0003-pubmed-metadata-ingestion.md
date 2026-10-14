# ADR 0003: Persist complete PubMed metadata snapshots

- Status: Accepted
- Date: 2026-10-13

## Context

The platform can search PubMed, but search results are transient and cannot yet support an auditable evidence workflow. PubMed ESummary provides bibliographic metadata, not the full article or a reviewed scientific claim.

## Decision

The paper library imports metadata through a dedicated command rather than as a side effect of search. Every import re-runs the authoritative PubMed query and persists records only when the connector marks the response complete.

Each new record stores:

- a source snapshot identified by provider and PMID;
- a deterministic hash of normalized article metadata;
- retrieval time, query, schema version, access level, and content-trust label;
- an unreviewed paper linked to that immutable source snapshot; and
- an append-only audit event.

Imports are idempotent. PMID is the primary deduplication key and a normalized DOI is the secondary key. Re-importing a known record returns the existing paper and does not rewrite its original source snapshot.

## Consequences

The UI must present an explicit import action and label imported data as unreviewed, metadata-only material. Incomplete upstream results fail closed and leave the library unchanged. Refreshing stale metadata will require a future versioned snapshot workflow rather than silently changing provenance.
