# Papercuts fixed — 2026-10-14

## Slop preflight help and unsupported arguments

Disposition: fixed.

Evidence: The accompanying CLI source parses arguments before any Git/index/gate operation, against main2e7b6378871e0096515e1aaab7a64061c7aff7bc. Two original CLI regressions fail before the fix; all four existing/new cases pass after it, preserving no-argument status, diagnostics and real index bytes. Original proof: /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/slop-preflight-args/green.receipt.json. Independent source review and exact merged gate/official land remain pending.

- 2026-10-07T05:45:44.248347+00:00 Root asked tools/maintenance/slop_gate_preflight.py --help; the script has no argument parser and began a second full gate with a disposable index. Stopped only root-owned PIDs 72670,70972,70925 with SIGTERM; normal commit gate, source/index and product proof runs were preserved. Read non-argparse utility source before requesting help.
