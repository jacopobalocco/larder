# larder

<!-- TODO: One-paragraph description of what larder is and who it's for. -->
A greenfield project scaffolded with an agent-ready baseline.

## Status

Early scaffolding stage — no application code yet. The repository ships an
agent-ready baseline (portable instructions, secret hygiene, CI, pre-commit,
sandbox policy) so development starts on solid footing.

## Setup

```bash
# TODO: replace with the real toolchain once chosen (e.g. uv / pip).
# python3 -m venv .venv && source .venv/bin/activate
# pip install -e .[dev]

# Install pre-commit hooks
pip install pre-commit && pre-commit install
```

## Usage

<!-- TODO: document how to run the project once it exists. -->

## Development

- **Lint**: `ruff check .`
- **Format**: `ruff format .`
- **Test**: <!-- TODO: e.g. `pytest -q` once a test suite exists -->

See [`AGENTS.md`](AGENTS.md) for agent/contributor instructions,
[`ARCHITECTURE.md`](ARCHITECTURE.md) for the high-level design, and
[`docs/agent-execution.md`](docs/agent-execution.md) for the execution/sandbox policy.

## License

See [`LICENSE`](LICENSE).
