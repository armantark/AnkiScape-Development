---
root: false
description: Test runners, hooks, imports, search and package map
---
Local tests: `python3 run_tests.py <selectors>`; selectors are positional, `--count` prints the selection count N. Remote: `/opt/homebrew/bin/python3 tools/run_remote_tests.py "$PWD" plain|qt --select <selectors> --expected-tests <N>`.
The commit hook is `/Users/ArmanTarkhanian1/fleet/config/git/hooks/slop_gate.py`. `python3 tools/maintenance/function_metrics.py --output <path outside the worktrees> <file> <functions...>` measures functions with the hook's instruments. Run `python3 tools/audit_docs.py` only in a git checkout, never on the MacBook mirror. Scratch imports: `import pkg_alias`, then `ankiscape.*`. Bounded search: `python3 tools/repo_search.py`. Memory Bank index: `memory-bank/README.md`.
A remote run that prints "Remote mirror busy; waiting" is queued behind other runs; let it wait.

## Repository map

- `core/`: shared constants, registries, metadata, persistence and Anki-aware orchestration.
- `logic/`: Qt-free feature logic and cross-cutting helpers.
- `logic_pure/`: the split former `logic_pure.py` monolith and its domain helpers.
- `runtime/`: review-action dispatch and state-mutating action handlers.
- `ui/`: Qt widgets, tabs, panels and dialogs.
- `data/`: source-backed gameplay definitions and catalogs.
- `generated/`: generated catalogs and source digests.
- `tools/`: maintenance, source harvesting, generators, audits and verification runners.
- `tests/`: unittest behavior suites, including pure and Qt coverage.
