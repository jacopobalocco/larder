# 🎯 Agentic Readiness Assessment — `larder`

**Project**: larder
**Mode**: brownfield   **Agents**: claude
**Overall Score**: **39/100** 🟡 Partially Ready
**Generated**: 2026-05-31 · script signals: available (python3)

## 1. Executive Summary

```
Agent Instructions & Context      █████████████░░░  15.1/18
Navigability & Code Intelligence  ██████░░░░░░░░░░  7.2/18
Testing & Feedback                █░░░░░░░░░░░░░░░  0.8/16
CI/CD, Automation & Governance    ████████░░░░░░░░  6.7/14
Agent Tooling & Capabilities      ░░░░░░░░░░░░░░░░  0.0/12
Security & Sandbox                ████████░░░░░░░░  5.7/12
Spec-Driven Workflow & Docs       █████░░░░░░░░░░░  3.4/10
```

The agent-ready baseline is in place: a concise canonical `AGENTS.md` bridged to
`CLAUDE.md`, full secret-hygiene `.gitignore`, a documented execution policy, a
CI skeleton and pre-commit hooks. The score is held back by the project being
**empty of source code** (no tests, no README, no repo map, no committed
tooling) — expected for a freshly scaffolded greenfield repo.

### Top 5 Gaps (by impact)
1. 🔴 **Testing & Feedback › test_suite/commands** (+15.2) — no tests or real test command. fix: add a suite and document the command (partial/skill).
2. 🔴 **Agent Tooling › skills/MCP** (+12.0) — nothing committed in-repo. fix: add `SKILL.md` and/or `.mcp.json` (partial).
3. 🟡 **Navigability › README/repo map/manifest** (+10.8) — no code yet. fix: add `README.md`, first modules, `pyproject.toml` (partial/manual).
4. 🟡 **CI/CD & Governance** (+7.4) — CI steps are placeholders; no CODEOWNERS/Dependabot. fix: real test+lint, add governance (partial/skill).
5. 🟡 **Spec-Driven & Docs** (+6.6) — only a spec template; no real specs/ADR/architecture doc (partial/manual).

## 2. Layer Analysis

| Layer | Score | Max |
|---|---|---|
| Portable | 36.2 | 94.3 |
| Target-specific (claude) | 2.7 | 5.7 |

The target layer (claude) is small by design: only `cross_agent_bridge`,
`agent_permission_policy`, and `custom_commands` are claude-specific. The
`CLAUDE.md` symlink already earns full bridge credit; the remaining target gaps
are a `.claude/settings.json` permission policy and custom commands.

## 3. Per-Dimension Detail

### 1. Agent Instructions & Context — 15.1/18 (raw 83.75)
- ✅ `primary_instruction_file` (100): `AGENTS.md` present and structured.
- ⚠️ `instruction_quality` (50): build/test/lint are TODO placeholders, not yet project-specific. **Fix** (partial, Med): add real paths, conventions, commands.
- ✅ `instruction_conciseness` (100): 55 lines, no boilerplate.
- 🟡 `hierarchical_instructions` (75): single root file — fine at this size. **Fix** (manual, Med): add per-package files only as it grows.
- ✅ `cross_agent_bridge` (100): `CLAUDE.md` → `AGENTS.md` symlink, no drift.

### 2. Navigability & Code Intelligence — 7.2/18 (raw 40.0)
- ⚠️ `repo_map_availability` (25): 0 source files to map. **Fix** (partial, Med): commit a repo map once code exists.
- ⚠️ `semantic_nav_amenability` (25): no code / LSP configs. **Fix** (manual, High): add types + language-server configs.
- ⚠️ `dependency_structure_clarity` (25): no `pyproject.toml`/modules. **Fix** (manual, Med): add manifest + module boundaries.
- ⚠️ `readme_overview` (25): no `README.md`. **Fix** (partial, Low): add overview/setup/usage.
- 🟡 `machine_readable_contracts` (50): no API boundaries (not yet applicable). **Fix** (manual, High): add OpenAPI/Protobuf/GraphQL when boundaries exist.
- ✅ `file_size_sanity` (100): no oversized files.

### 3. Testing & Feedback — 0.8/16 (raw 5.0)
- 🔴 `test_suite_present` (0): no tests. **Fix** (partial, High): add unit + integration tests.
- ⚠️ `test_commands_documented` (25): placeholder only. **Fix** (skill, Low): document the real test command in `AGENTS.md`.
- 🔴 `fast_feedback_loop` (0). **Fix** (manual, Med): add quick subset/watch mode/markers.
- 🔴 `feedback_quality` (0): no tests/type-checker. **Fix** (manual, Med): assertion messages + mypy/pyright.
- 🔴 `coverage_reasonable` (0). **Fix** (partial, Med): add coverage config + breadth.

### 4. CI/CD, Automation & Governance — 6.7/14 (raw 47.5)
- ⚠️ `ci_runs_tests_lint` (50): `ci.yml` exists but steps are `echo` placeholders. **Fix** (partial, Med): real test + lint.
- ⚠️ `lint_format_automated` (50): ruff via pre-commit, no `[tool.ruff]` config. **Fix** (skill, Low): add ruff config to `pyproject.toml`.
- ✅ `pre_commit_hooks` (100): ruff, ruff-format, detect-secrets, hygiene hooks.
- 🔴 `governance` (0): no CODEOWNERS/Dependabot. **Fix** (skill, Low): add both.

### 5. Agent Tooling & Capabilities — 0.0/12 (raw 0.0)
- 🔴 `standard_skills` (0): no `SKILL.md` in repo. **Fix** (partial, Med).
- 🔴 `bundled_helper_scripts` (0). **Fix** (partial, Med).
- 🔴 `mcp_declaration` (0): no `.mcp.json`. **Fix** (partial, Med).
- 🔴 `nav_comprehension_mcp_servers` (0): no Serena/Sourcegraph. **Fix** (partial, Med).
- 🔴 `custom_commands` (0, target): no `.claude/commands/`. **Fix** (partial, Low).

### 6. Security & Sandbox — 5.7/12 (raw 47.5)
- 🔴 `committed_isolation_config` (0): no `.devcontainer/`. **Fix** (partial, Med): add devcontainer with egress allowlist.
- ✅ `documented_execution_policy` (100): `docs/agent-execution.md` + AGENTS.md security section.
- 🔴 `agent_permission_policy` (0, target): no `.claude/settings.json` deny rules. **Fix** (partial, Med).
- 🟡 `secret_hygiene` (75): 100% `.gitignore` coverage + `.env.example`; missing CI secret scanning. **Fix** (skill, Low).
- ⚠️ `supply_chain_pinning` (25): no lockfile/Dependabot yet. **Fix** (partial, Low): commit lockfile once deps added.
- ✅ `injection_hygiene` (100): instructions only in trusted files.

### 7. Spec-Driven Workflow & Docs — 3.4/10 (raw 33.75)
- ⚠️ `spec_tasks_dir` (50): only `TEMPLATE.md`. **Fix** (partial, Med): add real specs.
- 🟡 `acceptance_criteria` (75): template includes the section. **Fix** (partial, Low): fill in real specs.
- 🔴 `issue_pr_templates` (0). **Fix** (skill, Low).
- 🔴 `adr_decisions` (0). **Fix** (manual, Med): add `docs/adr/`.
- ⚠️ `docs_comprehension_signals` (25): docs/ exists; no architecture doc/changelog. **Fix** (partial, Med).

## 4. Remediation Roadmap

**Quick wins (`/agent-ready fix` — skill/partial, Low effort):**
- Document real test/lint commands in `AGENTS.md`; add `[tool.ruff]` to `pyproject.toml`.
- Add CODEOWNERS + Dependabot; add issue/PR templates.
- Add CI secret scanning / push protection.

**As the project gains code (manual/partial, Med–High):**
- Add `README.md`, first modules, `pyproject.toml` (+ lockfile committed).
- Add a real test suite, coverage config, and a type checker (mypy/pyright).
- Replace CI placeholders with real `pytest`/`ruff` runs.
- Add `.devcontainer/` and a `.claude/settings.json` permission policy.
- Wire a nav/comprehension MCP server (e.g. Serena) once the codebase is non-trivial.
- Add real specs, ADRs, and an architecture doc.

Run `/agent-ready fix` to auto-generate the skill-fixable items, then
`/agent-ready diff` to track progress against this baseline.
