# 🎯 Agentic Readiness Assessment — `larder`

**Project**: larder
**Mode**: brownfield   **Agents**: claude
**Overall Score**: **54/100** 🟡 Partially Ready  *(was 39 → **+15** after `/agent-ready fix`)*
**Generated**: 2026-05-31 · script signals: available (python3)

## 1. Executive Summary

```
Agent Instructions & Context      ██████████████░░  16.2/18   (was 15.1)
Navigability & Code Intelligence  ████████░░░░░░░░  9.3/18    (was 7.2)
Testing & Feedback                █░░░░░░░░░░░░░░░  0.8/16    (=)
CI/CD, Automation & Governance    ███████████████░  13.0/14   (was 6.7)
Agent Tooling & Capabilities      ░░░░░░░░░░░░░░░░  0.0/12    (=)
Security & Sandbox                ██████████░░░░░░  7.4/12    (was 5.7)
Spec-Driven Workflow & Docs       ████████████░░░░  7.3/10    (was 3.4)
```

`/agent-ready fix` generated the skill/partial-fixable artifacts: README,
`pyproject.toml` (ruff), CODEOWNERS + Dependabot, issue/PR templates, ADRs,
ARCHITECTURE/CHANGELOG, and a devcontainer; CI and AGENTS.md now use real ruff
commands. The remaining gaps require real code (tests, types) or human judgment
(permission policy, host secret scanning) and are left as advisories.

### Per-dimension before → after
| Dimension | Before | After | Δ |
|---|---|---|---|
| CI/CD, Automation & Governance | 6.7 | 13.0 | +6.3 |
| Spec-Driven Workflow & Docs | 3.4 | 7.3 | +3.9 |
| Navigability & Code Intelligence | 7.2 | 9.3 | +2.1 |
| Security & Sandbox | 5.7 | 7.4 | +1.7 |
| Agent Instructions & Context | 15.1 | 16.2 | +1.1 |
| Testing & Feedback | 0.8 | 0.8 | — |
| Agent Tooling & Capabilities | 0.0 | 0.0 | — |
| **Overall** | **39** | **54** | **+15** |

## 2. Layer Analysis

| Layer | Score | Max |
|---|---|---|
| Portable | 51.3 | 94.3 |
| Target-specific (claude) | 2.7 | 5.7 |

## 3. Remaining Gaps (by impact)

1. 🔴 **Testing & Feedback** (+15.2, manual/partial) — no tests, no test command, no coverage/type-checker. Requires real test authoring.
2. 🔴 **Agent Tooling** (+12.0, partial/manual) — no committed Skills/MCP. Add only when a genuine capability/server exists (not fabricated).
3. 🟡 **Navigability** (+8.7, manual) — no source modules/types/README narrative depth. Improves as code lands.
4. 🟡 **Security & Sandbox** (+4.7) — harden devcontainer egress allowlist; add `.claude/settings.json` deny rules (manual); enable host secret scanning.
5. 🟢 **Spec-Driven & Docs** (+2.75, partial) — write real specs; record decisions as ADRs.

## 4. What `/agent-ready fix` changed

**Created**: `README.md`, `pyproject.toml` (`[tool.ruff]`), `.github/CODEOWNERS`,
`.github/dependabot.yml`, `.github/ISSUE_TEMPLATE/{bug_report,feature_request}.md`,
`.github/pull_request_template.md`, `docs/adr/{TEMPLATE,0001-record-architecture-decisions}.md`,
`ARCHITECTURE.md`, `CHANGELOG.md`, `.devcontainer/devcontainer.json`.

**Updated**: `.github/workflows/ci.yml` (real `ruff check` + `ruff format --check`),
`AGENTS.md` (real lint/format commands + structure pointers).

## 5. Advisories (manual — not auto-generated)

- **Tests** (highest impact): add a runner (e.g. `pytest`), a first test suite, coverage config, and a type checker (mypy/pyright); then document the test command and wire it into CI.
- **Agent permission policy**: author restrictive `.claude/settings.json` deny rules — review the committed file as attack surface (CVE-2025-59536).
- **Host secret scanning**: enable secret scanning + push protection on GitHub.
- **Skills/MCP**: introduce a `SKILL.md` and/or `.mcp.json` only when a real capability or server exists.
- **Code intelligence**: add types and, once the codebase is non-trivial, wire a nav MCP server (e.g. Serena).

Run `/agent-ready diff` to see this delta against the previous baseline.
