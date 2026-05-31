# AGENTS.md

Portable, agent-readable instructions for this project. This file is canonical
and vendor-neutral: Codex, OpenCode, and pi read it natively; Claude reads it
through the `CLAUDE.md` symlink. Keep it concise (< 200 lines).

## Project Overview

<!-- TODO: One or two sentences describing what this project does and who uses it. -->
`larder` — greenfield project scaffolded with an agent-ready baseline.

## Build · Test · Lint

These are placeholders for a Python project. Replace the TODOs with the real
commands once the toolchain (e.g. `uv` / `pip` + `pytest` + `ruff`) is set up.

```bash
# Install dependencies
# TODO: e.g. `uv sync` or `pip install -e .[dev]`

# Build (if applicable)
# TODO: e.g. `uv build`

# Run tests
# TODO: e.g. `pytest -q`

# Lint
# TODO: e.g. `ruff check .`

# Format
# TODO: e.g. `ruff format .`
```

## Code Style

<!-- TODO: Point to the formatter/linter config (e.g. ruff in pyproject.toml). -->
- Follow the project formatter; do not hand-format. Run the format command before committing.
- Prefer small, focused modules and clear names over cleverness.

## Project Structure

<!-- TODO: Update as the codebase grows. -->
- `LICENSE` — project license.
- `specs/` — task specifications (see `specs/TEMPLATE.md`).
- `docs/` — project and agent-execution docs.

## Safe-to-Run / Security

- Safe-to-run without confirmation: read-only inspection, the test and lint
  commands above, and formatting.
- Ask before: installing/upgrading dependencies, network calls, deleting files,
  pushing, or anything that mutates state outside the working tree.
- Never commit secrets. Secret patterns are covered in `.gitignore`; copy
  `.env.example` to `.env` (gitignored) for local config.
- For the agent execution / sandbox policy, see `docs/agent-execution.md`.
