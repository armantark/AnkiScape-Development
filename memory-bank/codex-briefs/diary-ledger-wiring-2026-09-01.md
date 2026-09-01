# Slice brief — wire the diary curation ledger through the generator

Date: 2026-09-01. Author: the orchestration seat. Consumer: one dispatched
implementation agent.

## 0. Read this first

`memory-bank/codex-briefs/STANDING-SLICE-CONTRACT.md` is binding. Read it
completely before you edit anything. Nothing in this brief overrides it. If
this brief and the contract disagree, stop and report both texts.

## 1. Both gates are passed

`memory-bank/diary-curation-ledger/README.md` names two gates before any
wiring. Both are passed, so this slice is authorized:

- Gate 1, the cross-lineage review, is recorded in
  `memory-bank/diary-curation-ledger/cross-lineage-review.md`. It covered all
  320 rows in two independent ranges, plus a final independent pass.
- Gate 2, the owner spot-check, passed by the owner's ruling of 2026-08-31
  (`memory-bank/design-thread-queue.md` section 4.22 ruling 3). Conformance to
  the settled contracts substitutes for an owner read of all 320 rows.

The README's own no-generator boundary lifts with gate 2. The rest of the
README still binds you, in particular the deed-only rule and the citation rule.

## 2. What the numbers actually are

Measured on `main` at `e7745b6a`, and reproduced by the orchestration seat:

```
families 10 | tiers 34 | named tasks 474 | tasks with empty conditions 320
ledger rows 320 | active 43 | translated 30 | dormant 247
empty-condition tasks absent from the ledger: 0
tiers whose empty rows carry no dormant entry: 0
```

Read the last line carefully. **No diary tier becomes claimable because of this
slice.** Every one of the 34 tiers keeps at least one dormant row. The
orchestration seat reported that to the design seat in
`memory-bank/handoffs/impl-to-design-2026-09-01-diary-tier-premise.md`. You are
not expected to move the claimable count, and a report that claims you did is
wrong.

What this slice does deliver is 73 rows that change from "no condition" to a
live, runtime-checkable condition: the 43 `active` rows and the 30 `translated`
rows.

The design seat ruled on this on 2026-09-01 (rulings ledger section 26): the
wiring ships at this scope unchanged, and **no new mechanic rides in this
slice**. A separate slice that follows yours builds the Beefy Bill banking
service, which is what actually makes `lumbridge_medium` the first claimable
tier. Do not build it, do not stub it, and do not add a condition that
anticipates it.

## 3. The shape of the change

`tools/generate_achievement_diary_data.py` does not read the curation ledger
today. Grep it: `dormant-task-ledger` appears nowhere. That is the gap.

Make the generator read
`memory-bank/diary-curation-ledger/dormant-task-ledger.jsonl` and apply it:

1. For a row whose disposition is `active` or `translated`, emit real
   conditions built from its `designed_trigger`, using the condition kinds the
   generator already supports. The row's `notes` field names the exact seam.
2. For a row whose disposition is `dormant`, emit nothing. Its catalog entry
   keeps `conditions == ()` exactly as it is today.

Do not add a dormant-trigger field to the generated catalog. The ledger is
already the record, and a second copy is the duplication the README forbids.

`resolve_condition_key` at `tools/generate_achievement_diary_data.py:240` is
the rail that makes this safe: a condition key that names nothing the runtime
writes becomes a generation failure instead of a panel that renders an honest
looking `0/1` forever. Do not weaken it, do not bypass it, and do not add a
kind to it so a trigger you could not otherwise express will pass.

**Gate.** If a `designed_trigger` cannot be expressed with an existing
condition kind against an existing seam, stop on that row and report it by
`task_id` with the exact trigger text. Do not invent a seam, do not demote the
row to `dormant` yourself, and do not weaken the rail. That decision belongs to
the design seat. A row you stopped on is a success state.

## 4. The rules that govern the content

- **Deed only.** A diary task completes when its deed occurs. Skill levels,
  quest states, inventory ownership, equipment ownership and route access are
  access gates. They must never substitute for the deed. The 22 labelled
  progression anchors are the only level-trigger exception, and they are
  outside the ledger.
- **Corrections are ledger edits.** A wrong interpretation is fixed by editing
  the ledger row and regenerating. Never hand-edit
  `data/achievement_diary_catalog.py`. The owner made this the condition of
  gate 2, so that a rebuild can never be needed again.
- **Row 135, the Fire cape row, defaults to the closer equipped-item
  candidate**, per the translation-fidelity principle. The owner can veto it
  later as a patch. Implement the default.
- **The same-frame boundary.** Several `active` rows rest on a live result seam
  that is read in the same frame, not on cumulative telemetry. Review
  resolutions 1 and the notes on rows 53, 94, 128, 165 and 274 state this. A
  wiring that reads a cumulative counter where the row means one action's
  output is a defect.
- **The rotated skill labels are already repaired.** Branch
  `goal/diary-skill-rotation-2026-08-30` is merged into `main` at `760233f0`,
  and the 25 affected notes no longer carry the wiring blocker. Do not repeat
  that repair.

## 5. Prohibitions that apply to this workspace

Forward every one of these to any child agent you spawn.

- Do not change an existing user interface without explicit owner approval.
  This slice is data and generator work. If the generated catalog gains
  anything the panel would render differently, stop and report it instead.
  State in your report whether any user interface changed.
- Do not delete any worktree, however merged or clean it looks. This is an
  owner gate.
- Do not commit to `main`. Only the orchestration seat merges to `main`.
- Do not push to any remote. Do not change git config. Do not skip hooks. Do
  not use an interactive `-i` flag.
- Do not weaken a test, an audit, or a pinned baseline so your work can pass.
- Do not ask another agent session to rule on a conflict or to grant you
  permission. The orchestration seat is your only escalation route.
- Do not fetch a newer source, and do not replace a permanent wiki link with a
  mutable one. Every citation rule in the README section "Citation rule" still
  binds.

## 6. Your worktree

Lease one through the guard, from the canonical checkout:

```
python3 tools/worktree_guard.py audit
python3 tools/worktree_guard.py lease goal/diary-ledger-wiring-2026-09-01 --holder diary-wiring
```

The last stdout line is JSON with `path` and `lease_id`. Work there. After your
commit is on the branch, release it:

```
python3 tools/worktree_guard.py release <path> --lease-id <id>
```

Run the guard audit again at the end. Never call `treehouse` directly.

## 7. Verification

**Promotion gate.** The orchestration seat re-runs both lanes on the merged
tree. Run the plain lane only, and say in your report that you did so:

```
/opt/homebrew/bin/python3 run_tests.py
```

`tests/test_achievement_diaries.py` runs the same condition-key check over the
shipped catalog, so it is your first signal and your cheap neighbour check. Run
it on its own as well as inside the lane.

Also run, and report the exact output of:

```
python3 tools/audit_docs.py
python3 tools/audit_test_quality.py
python3 tools/audit_item_reachability.py
python3 tools/worktree_guard.py audit
git diff --check
```

Prove the wiring by driving the real kernel. For at least three of the 73 rows,
covering both `active` and `translated`, perform the deed through the real
runtime path and show the task move from incomplete to complete. A test that
imports the module proves the module, not the application. This project has
shipped four defects that survived three review passes and were caught only by
execution.

Re-measure and report, before and after:

```
tasks with empty conditions (expect 320 before)
tiers claimable (expect 0 before and 0 after)
the disposition census 43 / 30 / 247
```

Regeneration must be reproducible. Run the generator twice and show that the
second run leaves the catalog byte-identical.

## 8. Your report

Write a source audit at
`memory-bank/source-audits/diary-ledger-wiring-2026-09-01.md`. Update
`memory-bank/activeContext.md` and `memory-bank/progress.md`. Append a
timestamped line to `memory-bank/papercuts.md` for every piece of friction you
hit, in the moment.

Report exact numbers, identifiers, paths and error strings verbatim, and
re-measure every number at the moment you write the report. List every row you
stopped on by `task_id`. State plainly what you did not do and why.
