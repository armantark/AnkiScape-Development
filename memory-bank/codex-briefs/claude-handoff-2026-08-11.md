# Claude handoff — 2026-08-11

## Goal

Continue the breadth program from the next high-value item root.
Keep all work away from canonical `main` until the owner approves a merge.

## Repository state

Branch `goal/breadth-2026-08-11` adds two commits to canonical `main`.

- `f6353843` closes the Wyvern bones acquisition slice.
- `424c8ab2` repairs the Wyvern closure contracts.

Canonical `main` is clean at `0071218b`.
Nothing was pushed.

The owner made a direct branch ruling on 2026-08-10.
This goal stays in the isolated worktree branch until the owner is ready to merge.
This ruling replaces the goal clause that requires one attributable commit on canonical `main`.

The owner also made a direct source-work ruling.
Luna does source harvesting at maximum effort.
Sol does a quick sanity check after the harvest.
Do not use a second full harvest.
Sol keeps implementation, verification, and closure work.

`memory-bank/activeContext.md` uses newest-first order.
Older entries are dated snapshots and are not current truth.
Use the topmost dated entry as the live state.

## Completed slice

The Wyvern bones slice is complete.
Reachability changes from `2,573` reachable items and `102` orphan inputs.
It now reports `2,585` reachable items and `90` orphan inputs.
The plain lane passes `4,061` tests with `494` skips and zero failures.
The Qt lane is clean except for two pre-existing failures.

Read the full evidence in `memory-bank/source-audits/wyvern-bones-acquisition-2026-08-11.md`.
Read the top entry in `memory-bank/activeContext.md` for the corrected closure state.

## Durable facts

### Pre-existing Qt failures

Two `test_hud_singleton_and_cleanup` results reproduce on canonical `main` at `0071218b`.

- `test_ensure_review_hud_cleans_duplicates_and_singleton` fails with `AssertionError: 0 != 2 : Each ensure should verify the strip's stable child order`.
- `test_surface_refreshes_do_not_rescan_the_qt_tree` errors because `QFrame` receives a `FakeStrip` parent.

Treat these two results as pre-existing repository debt.
Do not report them as Wyvern slice defects.

### Qt test environment

The worktree cannot contain `.venv-qt` because Git ignores that environment.
Use the Qt interpreter from the canonical checkout.
Set `PYTHONPATH="$PWD"` from the worktree.
This setting makes Python load the worktree modules.

The full unpartitioned Qt lane exits with code `137` because it exhausts memory.
Run the lane in the four recorded `a-f`, `g-l`, `m-r`, and `s-z` batches.
Use the exact commands in the top entry of `memory-bank/activeContext.md`.

### Equipment contract tests

Any slice that adds equipment rows affects three count-based contract tests.

- `test_generated_equipment_contract_shape`
- `test_only_audited_unresolved_identities_remain_buy_limit_blocked`
- `test_generated_period_rows_are_registered_and_cutoff_safe`

Update all three contracts when a source-qualified equipment change alters their counts.

### Ranging Guild source IDs

Source IDs `238` and `239` are Ranging Guild diary tasks.
They are hand edits in the generated diary data.
`tools/generate_achievement_diary_data.py` does not contain these rows.
Regeneration silently deletes both rows.
Preserve these IDs until the generator owns them.

## Process rule

Give one writer one narrow unit.
Do not give one writer a complete slice.
Five agents stopped through context exhaustion when they received a whole slice.
Decomposition fixed the failure.
Use `rg --files` to list exact paths before content searches.
Do not run broad tree-wide content searches.

## Next slice

1. Run `python3 tools/audit_item_reachability.py --rank-roots 10` from the worktree.
2. Select the top current item root.
3. Skip Emerald lens if it appears.
4. Leave Emerald lens to the parallel Darkan restoration thread.
5. Read `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/shared-source-harvest-ledger.md`.
6. Claim the selected slice in the ledger before source work starts.
7. Do not commit in `/Users/ArmanTarkhanian1/Documents/2012scape with bots`.
8. Use Luna at maximum effort for the source harvest.
9. Use Sol for the quick source sanity check.
10. Use Sol for implementation, verification, and closure.

## Required proof

Record the selected root and its fresh rank output.
Record the canonical ledger claim.
Record every source with exact revisions and identifiers.
Record the focused tests and both full lanes.
Record the final reachability counts.
Keep the worktree clean after each committed unit.
Do not push.
