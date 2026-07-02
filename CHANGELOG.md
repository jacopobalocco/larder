# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project aims
to follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Agent-ready baseline: `AGENTS.md` (+ `CLAUDE.md` bridge), secret-hygiene
  `.gitignore`, `.env.example`, `docs/agent-execution.md`, CI workflow,
  pre-commit config, and a spec template.
- Project scaffolding: `README.md`, `pyproject.toml` (ruff config),
  `ARCHITECTURE.md`, ADRs (`docs/adr/`), issue/PR templates, CODEOWNERS,
  Dependabot config, and a devcontainer.

### Changed
- Meal plan AI generation (`/meal-plan/auto-distribute`, `/meal-plan/auto-plan`)
  now calls Groq directly via the official SDK instead of proxying through the
  external `home-ai` service. Configure `GROQ_API_KEY` (required) and
  `GROQ_MODEL` (optional) in `.env`. See ADR-0003.

### Removed
- Dependency on the external `home-ai` proxy and the `HOME_AI_URL` env var.
