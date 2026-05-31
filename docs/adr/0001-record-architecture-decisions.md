# ADR-0001: Record architecture decisions

- **Status**: Accepted
- **Date**: 2026-05-31

## Context

The project needs a lightweight, durable way to capture *why* significant
technical decisions were made, so that future contributors (human and agent) do
not re-litigate settled trade-offs or accidentally reverse intentional choices.

## Decision

We will record architecturally significant decisions as Architecture Decision
Records (ADRs) in `docs/adr/`, using the format in [`TEMPLATE.md`](TEMPLATE.md),
numbered sequentially (`NNNN-title.md`).

## Consequences

- Decision rationale is preserved next to the code, in version control.
- Each significant change should add or update an ADR.
- Superseded decisions are kept and marked, preserving history.
