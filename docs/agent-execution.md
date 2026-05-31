# Agent Execution & Sandbox Policy

Vendor-neutral policy describing how AI coding agents are allowed to run code in
this project. The goal is a safe-by-default posture from day one.

## Recommended sandbox options

Pick one appropriate to your environment:

- **[LINCE](https://lince.sh)** — lightweight local execution sandbox for agents.
- **Devcontainer** — `.devcontainer/` for a reproducible, isolated dev image.
- **OS-level sandbox** — e.g. the agent's built-in sandbox / `seatbelt` /
  `firejail`, restricting filesystem and network access.
- **Hosted / ephemeral** — run the agent in a disposable cloud container that is
  reclaimed after the session (no persistent secrets on disk).

## Safe-to-run commands (no confirmation needed)

- Read-only inspection: `ls`, `cat`, `git status`, `git diff`, `git log`.
- Tests and linters: the test and lint commands documented in `AGENTS.md`.
- Formatting: the format command documented in `AGENTS.md`.

## Ask-before-running

- Installing or upgrading dependencies.
- Any network egress (downloads, API calls, publishing).
- Destructive operations: deleting files, `git push`, history rewrites.
- Anything that mutates state outside the working tree.

## Secret handling

- Never echo, log, or commit secrets.
- Local config lives in `.env` (gitignored); see `.env.example`.
- `.gitignore` covers common secret patterns (`.env`, `*.pem`, `*.key`, …).
