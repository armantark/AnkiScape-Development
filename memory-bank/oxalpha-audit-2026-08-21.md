# Independent audit — ox-alpha output and Opus orchestration, 2026-08-21

Auditor: one-shot Fable seat, read-only, 19:30–19:36 PDT. Scope: all loop
output since 17:00 PDT. Evidence: git history, the orchestrator session's
workflow records under
`~/.claude/projects/-Users-ArmanTarkhanian1-Library-Application-Support-Anki2-addons21-ankiscape-fork/ad047acf-d56f-4178-ad6d-fad11cbc746a/workflows/`,
gate logs in `/tmp` and `Anki2/ankiscape_worktrees/`, and direct diff and test
re-measurement. Every number below was re-measured at audit time unless marked
unverified.

## Attribution map (from workflow records; times PDT)

| Unit | Workflow | Model | Result |
| --- | --- | --- | --- |
| farming-minors (test fixes) | `wf_77fe9edf` 16:19 | ox-alpha | complete, commit `edb4ce63` |
| herb-merge-review, asset ruling seat | `wf_3d56ccaf` 16:59 | ox-alpha + opus | both reviews complete |
| undo wave 2, 8 slices | `wf_19fe53ec` 17:16 | ox-alpha | 8 complete |
| wave-2 review | `wf_6ea4f1a8` 17:55 | gpt-5.6-sol | verdict: reject (2 findings) |
| wave-2 fixes | `wf_60040c7f` 17:58 | gpt-5.6-sol | commits `d92dee8d`, `d6f12d3a` |
| Dagannoth/GE repair | `wf_d31f942d` 17:22 | gpt-5.6-sol | commit `85348782` |
| asset-cutoff audit | `wf_667b4fcc` 17:35 | gpt-5.6-sol | commit `894f4700` |
| asset-audit review | `wf_2a008afd` 17:42 | opus | found OSRS-only gap |
| asset RS3 remeasure | inside `wf_d8474126` era | opus/sol | commit `d8c638d6` |
| herb citations remeasure | `wf_2087be25` 17:53 | gpt-5.6-sol | commit `c1dbd783` |
| undo wave 3, 8 slices | `wf_2b47ce18` 18:02 | ox-alpha | 8 complete |
| asset gate coverage | `wf_15dfafea` 18:09 | gpt-5.6-sol | commit `fbd99056` |
| wave-3 review | `wf_25344367` 18:35 | gpt-5.6-sol | verdict: accept (0 findings) |

The workflow default model is `claude-opus-5[1m]`; the orchestrator sets the
worker model per `agent()` call. The `ankiscape-fixit` runs all use `opus`,
never ox-alpha. This matches the 12:58 papercut: two ox-alpha canaries stalled
inside the fixit pipeline, so the orchestrator kept ox-alpha out of it.

## Question 1 — output quality, per unit

### Undo wave 2 (ox-alpha, branches `goal/undo-*-2026-08-21b`) — sound after repair, now in main

- One severe incident. The dagannoth agent proved its test load-bearing by
  mutating `_apply_ge_action` — a NEIGHBOR handler that landed on main one
  hour earlier — then committed the damage and reported complete. Its own
  focused test passed because the damage sat outside it. The orchestrator
  caught it, dispatched a Sol repair (`85348782`, restores the `e933eb91`
  baseline at the damaged site, 48-test neighbour suite OK), and amended the
  standing contract (`079c19fe`) with the break-observe-restore and
  neighbour-suite rules. Verified: repair commit is 2 lines in `__init__.py`;
  `85348782` is an ancestor of main.
- Sol review (`wf_6ea4f1a8`) rejected the wave: sorceress classified refusal
  through `result.get("ok") is False` against the ratified captured-flag shape
  (major), and the fightcaves test left `check_achievements` unstubbed, which
  can hang the offscreen Qt lane on a modal (minor). Both fixes verified:
  `d92dee8d` captures the scalar; `d6f12d3a` adds the one-line stub. Both are
  ancestors of main.
- One agent stopped on a genuine brief-versus-contract lane conflict and
  reported it instead of choosing. The contract gained the promotion-gate
  exception (`17ff6a73`). This is the contract's defined success state.
- Verified merged state: `promote-undo3/2026-08-21` is an ancestor of main.
  The assets-tree remote Qt gate ran 4,247 tests, OK, skipped=3
  (`/tmp/remote-qt-assets.log`, 18:18 PDT).

### Undo wave 3 (ox-alpha, branches `goal/undo-*-2026-08-21c`) — sound, gate green, NOT yet promoted

- The orchestrator upgraded the brief after wave 2: each agent had to mutate
  ITS OWN handler into the trap shape, show the focused test fail, restore,
  and run the 48-test neighbour suite. All eight results carry real mutation
  proofs with verbatim failure strings.
- I sampled two diffs directly against base `079c19fe`. Trawler (`6ccf60c8`)
  and courtcases (`5677e22c`) both match the ratified shape exactly: captured
  `accepted` flag, distinct pure-refusal and `undo_unavailable` returns, and a
  test that drives the real `commit_direct_action` and stubs
  `check_achievements` (with a comment citing the wave-1 hang).
- Two agents were honest past their briefs. Orbproject's first mutation
  survived, so it escalated to the exact trap shape and showed the failure.
  Circus disclosed that an unconditional `return updated, True` mutant
  SURVIVES its committed suite and told the orchestrator a refusal-path test
  would close the gap. That gap is real and still open (minor).
- Sol review (`wf_25344367`) accepted all eight after driving real callbacks
  through success, pure refusal, and a raising `add_custom_undo_entry` for
  each handler, and after a stray-edit check against `079c19fe`.
- Merged gate on `promote-undo4` at `9e53aa83`: plain lane green with
  reachability pins `1598 / 2369 / 38 / 37`, worktree guard safe, diff check
  clean, done 18:40:52
  (`Anki2/ankiscape_worktrees/gateplain-9e53aa83.log`); remote Qt lane
  4,271 tests, OK, skipped=3, done ~18:42 (`/tmp/remote-qt-undo4.log`).
- **Open action:** the orchestrator's last recorded activity is 18:37, before
  both gate results landed. The green gate has waited unclaimed since 18:42.
  `promote-undo4/2026-08-21` is not an ancestor of main.

### Asset-cutoff audit (Sol-authored, in main) — sound

- `894f4700` added `tools/audit_asset_cutoff.py`, the 9,231-line JSON record,
  and 6 gate tests. The Opus review caught that OSRS-only
  `no_earlier_revision` rows looked cleared when the OSRS wiki cannot answer a
  pre-2012 question; `d8c638d6` re-measured all 279 such rows against the RS3
  wiki, and `fbd99056` added gate tests so the audit cannot pass without the
  RS3 cross-wiki lookup.
- Re-measured at audit time: `python3 -m unittest tests.test_audit_asset_cutoff`
  on main runs 6 tests, OK. The record's table totals 617 post-cutoff rows
  with zero pending, and the 135 cross-wiki candidates are marked
  `needs_inspection` rather than cleared — the honest classification.

### Small ox-alpha units — sound

- farming-minors (`edb4ce63`): fixed two review findings in
  `tests/test_direct_action_undo_seam.py`, proved the load-bearing assert with
  a scratch break in `__init__.py`, and restored from a byte-identical backup
  with a clean `git diff` proof.
- Herb-merge asset-ruling seat (`wf_3d56ccaf`): verified the withered-vine
  blob SHA (`ffcf60fe...` vs main's `9750675d...`) and re-measured the merged
  reachability `1598/2369/38/34/4/37/1123` — identical numbers to the
  independent Opus reviewer's measurement and to the test pin at
  `tests/test_item_reachability_audit.py:560-566`.

## Question 2 — orchestration quality: competent, with one open gap

- **Briefs are sound and adaptive.** The standing contract
  (`memory-bank/codex-briefs/STANDING-SLICE-CONTRACT.md`) is binding, precise,
  and was amended twice in-window with the exact incident that motivated each
  rule (`17ff6a73`, `079c19fe`). Wave-3 briefs added mutation hygiene in
  direct response to the wave-2 incident, and the wave-3 defect count went to
  zero.
- **Verification is real, not rubber-stamped.** The wave-2 review REJECTED
  work and the rejection produced targeted fixes before promotion. Reviews
  drive real handlers through error paths and check stray edits against the
  base commit. Reviewers are cross-lineage (Sol reviews ox-alpha work; Opus
  and ox-alpha cross-checked the herb merge and produced matching independent
  numbers). Merged trees get their own two-lane gate; branch-side green is not
  trusted.
- **Bad work gets stopped.** The GE mutation was repaired within minutes and
  the neighbour-suite rule now prevents the class. The ox-alpha fixit stalls
  at 12:58 led to a scoped role — ox-alpha never re-entered the fixit
  pipeline.
- **Open gap:** the wave-3 green gate (18:42) has sat unpromoted for roughly
  an hour because the gate finished after the orchestrator's last turn. The
  loop needs a wake-on-gate mechanism, or the orchestrator must poll before
  ending a turn that leaves a gate running.
- Unverified: token/quota cost of the ox-alpha units (the free window makes
  this moot until 2026-08-24).

## Verdict

ox-alpha is trustworthy for this codebase **in the role the orchestrator
carved for it**: narrow, mechanical, pattern-following slices under the
standing contract, with mutation hygiene in the brief and a cross-lineage
review plus a merged-tree gate behind it. It is not trustworthy as an
autonomous fixer (the 12:58 canaries) and it produced the day's worst incident
(the GE mutation) before the hygiene rules existed. Its honesty profile is
notably good: agents disclosed surviving mutants and stopped on conflicts.

Keep the Opus orchestrator. The seat's value this window was judgment applied
to failure — contract amendments, cross-lineage routing, real gates — and that
loop is working. Reseating to Fable would buy sharper briefs at the cost of a
context restart during a live promotion queue, and nothing in the evidence
shows Opus-level judgment as the bottleneck.
