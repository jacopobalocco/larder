# Architecture

High-level overview of how `larder` is structured. Keep this current as the
codebase grows — it is a primary comprehension signal for agents and humans.

## Overview

<!-- TODO: Describe the system's purpose and main components once code exists. -->
The project is at the scaffolding stage; no application modules exist yet.

## Repository Layout

| Path | Purpose |
|------|---------|
| `AGENTS.md` / `CLAUDE.md` | Portable agent/contributor instructions (CLAUDE.md is a symlink). |
| `README.md` | Human-facing overview, setup, usage. |
| `docs/` | Project docs, agent-execution policy, ADRs (`docs/adr/`). |
| `specs/` | Task specifications (`specs/TEMPLATE.md`). |
| `.github/` | CI workflows, issue/PR templates, CODEOWNERS, Dependabot. |
| `.devcontainer/` | Reproducible isolated dev environment. |
| `.agent-ready/` | Agentic-readiness scan reports and scores. |

## Key Decisions

See [`docs/adr/`](docs/adr/) for Architecture Decision Records.

## Conventions

- Lint/format with `ruff` (config in `pyproject.toml`).
- Pre-commit hooks enforce hygiene before commits.
