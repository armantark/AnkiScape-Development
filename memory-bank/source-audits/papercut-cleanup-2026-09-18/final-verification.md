# Maintenance verification

## Evidence before the final commit

The source baseline is `7f736d5c63ca0d301b1789798e75fa2737435f4c`. No digest pin, lane minimum, timeout, complexity cap or hook changed.

| Check | Result | Evidence |
| --- | --- | --- |
| Main focused plain selection | 120 tests, zero skips, passed | `papercut-focused-plain-etl0vnbz.log.gz` |
| Main focused Qt selection | 34 tests, zero skips, passed | `papercut-focused-qt-tfr14cg4.log.gz` |
| Final inert tooling selection | 37 tests, zero skips, passed | `papercut-final-inert-vrqh4bmi.log.gz` |
| Final MacBook Qt review-fix selection | 16 tests, zero skips, passed | `papercut-final-focused-qt-ebra1bxh.log.gz` |
| Qualified branch regression | Before fails; candidate selects the existing branch | `qualified-branch-before.log.gz`, `qualified-branch-after.log.gz`, `qualified-branch-canary.json` |
| Conditional ancestry and alias regressions | Positive discovery and ambiguous-binding refusal pass | `quality-conditional-evidence.json`, `quality-conditional-metrics.json` |
| Guard refusal paths | Baseline/current differential canaries and inert fixture tests pass | `guard-root-canaries.json`, `guard-root-tests.txt` |
| Inventory coverage | No gaps, duplicate assignments or source hash changes | `inventory-coverage.json`, `inventory-dispositions.json` |

The two rejected focused selections remain in the evidence. Plain ran 121 tests with one skip; Qt ran 120 tests with two skips. The exact focused runner correctly refused both. The accepted selections separate applicable environments; no skip rule changed.

The early full source run at `8898f8780213c265b693a28b992ee8fbc903e938` ran 5711 tests in each lane. Plain passed in 593.861 seconds with 1366 expected skips. Qt passed in 1115.094 seconds with 5 expected skips. The documentation audit then failed on the nested test-module selector in the review notes. No passing receipt was issued. `source-gate-8898f878.json` and its compressed log preserve that failure. `guard-review.md.gz` preserves the original notes; the readable command uses the equivalent file-path selector.

The review fixes came after that full run. Their focused evidence does not substitute for the final full gate.

## Exact final acceptance

This evidence file freezes before the final commit. Root must reconcile current main in the maintenance worktree, run the complete remote promotion gate on that exact clean commit, and land only through the guard. With unchanged main, the source and integrated candidate are the same tree. A different commit or a main collision requires fresh verification.

The final receipt is generated outside the worktree under the shared Git directory, so recording acceptance does not change the accepted commit. To read the receipt that matches the current checkout, run this from the repository root:

```sh
python3 -c 'from pathlib import Path; from tools.promotion.repository import commit_at, evidence_path_for; repo = Path.cwd(); print(evidence_path_for(repo, commit_at(repo)).read_text())'
```

It must name the exact canonical HEAD, `plain_only: false`, `remote_lanes: true`, and all eight checks: plain lane, Qt lane, documentation, test quality, reachability, worktree layout, clean worktree and diff check. The local full log is beside the safe worktree root, named `gate-<first eight commit characters>.log`.

The final landing is a local fast-forward. No remote push, automatic restart or gameplay-goal continuation is authorized.

## Scope limits

The inventory classifies historical causes; it cannot repair an external service or replace an owner decision. New maintenance incidents are appended to the main papercut log, outside the frozen source set. The independently reproduced fleet shell-wrapper defect is outside the one-level repository scope. The short-prompt mitigation was used successfully; its source remains unchanged.

The Fable handoff records architecture costs and distinguishes them from historical model and orchestration failures. Native acceptance and UI decisions remain open. The paused Magic candidates remain preserved.
