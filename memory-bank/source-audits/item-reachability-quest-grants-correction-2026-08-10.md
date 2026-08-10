# Item reachability: quest-grant correction — 2026-08-10

Status: **implemented and verified**.

## Finding

The live item graph treated final quest rewards as acquisition sources but
ignored items granted when a quest starts and items produced at individual
quest stages. This made `Dramen branch` a false root orphan even though Lost
City stage 4 already puts one in the player's inventory. Its existing Utility
consumer, `grind_dramen_branch`, was consequently blocked from exposing
`Cinnamon` in the graph.

The defect was limited to `tools/audit_item_reachability.py`. The quest runtime
already grants `start_inventory` in `start_quest_pure()` and
`produced_inventory` in `_consume_quest_current_stage_items()`. The Lost City
integration test already drives the real stage-4 branch grant and stage-5
consumption.

## Correction

Every registered item in a live quest's `start_inventory` is now a
`quest-start:<quest_id>` seed. Every registered stage `produced_inventory`
item is a `quest-stage:<quest_id>:<stage>` seed. Final rewards keep their
existing `quest:<quest_id>` route identity.

This follows the graph's established source-node semantics: it proves that the
live product has an acquisition route, not that a fresh player currently meets
every prerequisite. No quest behavior, stage gate, item grant, recipe, UI,
asset, save state, or placeholder changed.

The live graph changes from 1,555 actions / 2,436 reachable items / 104 orphan
inputs / 103 unresolved actions to 1,555 / 2,570 / 103 / 102. The 134 newly
visible registered items were already granted by the runtime. `Dramen branch`
now resolves through `quest-stage:lost_city:4`, and `Cinnamon` resolves through
`Utility:grind_dramen_branch`.

## Verification

- The route regression fails before the correction with
  `KeyError: 'Dramen branch'`.
- Focused reachability and quest-runtime coverage passes 201 tests.
- Complete plain discovery passes 4,036 tests in 232.027 seconds with 492
  expected environment skips.
- Complete real offscreen Qt discovery passes 4,036 tests in 530.886 seconds
  with three intentional platform skips.
- Documentation, test-quality, compilation, tracked-JSON, placeholder,
  asset-normalization, diff-whitespace, and worktree gates pass.
- No native Anki or new visual behavior is claimed because this is a read-only
  audit correction.
