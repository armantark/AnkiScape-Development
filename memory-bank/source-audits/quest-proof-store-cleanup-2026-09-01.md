# Quest proof store cleanup source audit — 2026-09-01

## Authority and boundary

The branch started from `c42d66bc4db162f567cc4025adf41a4e1e30da40`, the commit that introduced the global `quest_action_proofs` ledger and moved quest `required_actions` gates onto it. This slice completes that migration. It removes the retired quest-local `quest_stage_actions` model while preserving cleanup for saves that still contain the key. It also adds migration-time retirement for global proof names without inventing a retirement.

No user interface changed. The read-only checkout at `/Users/ArmanTarkhanian1/Documents/2012scape with bots/` was not modified. `tools/audit_asset_cutoff.py` was not run.

## Retired local store

New player data no longer contains `quest_stage_actions`, copied player state no longer preserves it, and completed quest stages now call `record_quest_stage_action_proofs_pure` directly. The private `_mark_quest_stage_actions` writer and its six split-module re-exports are removed.

The recursive production census still includes root `__init__.py`, nested modules, and `generated/`. Its AST pass detects direct assignment, alias-backed assignment, and mutating methods. Production has no write sites. The only remaining production mention is the migration removal in `core/storage_pure.py`.

## Save and proof migration

The save schema moves from config version 122 to 123.

- Saves below version 122 still start with an empty proof ledger. Inventory, telemetry, completed quests, and the retired local ledger do not backfill proofs.
- Version-122 saves retain their sanitized non-retired proofs while upgrading to version 123.
- `_migrate_quest_stage_side_state` drops `quest_stage_actions` from saves at every source version.
- `RETIRED_QUEST_ACTION_PROOFS` is subtracted whenever a save is older than `CURRENT_CONFIG_VERSION`. The set is empty because no proof name is genuinely retired today.
- Focused migration tests temporarily supply one retired name. The name is removed, its quest gate blocks again, an unrelated proof survives unchanged, and a simulated version-124 bump scrubs version-123 saves.

## Assertion migration and line budget

The base tree contained 213 assertion calls whose source mentioned `quest_stage_actions`. All 213 were moved to the proof ledger or to migration-removal expectations; no assertion was deleted. The current six mentions are the explicit `assertNotIn("quest_stage_actions", migrated)` cleanup checks. Stage-trace assertions use `tests/quest_action_proof_helpers.py` to read the new global ledger in quest catalog order.

The helper lives in a new 18-line test file because every large test file in this slice is above the 1,000-line hook threshold. No explanatory prose was deleted to pay the line budget. No oversized code file grew:

| File | Base lines | Final lines |
| --- | ---: | ---: |
| `core/storage_pure.py` | 2609 | 2601 |
| `logic_pure/logic_pure_quest.py` | 1649 | 1621 |
| `tests/test_logic.py` | 12559 | 12557 |
| `tests/test_runtime_actions.py` | 6042 | 6034 |
| `tests/test_integration_smoke.py` | 9561 | 9558 |
| `tests/test_main_menu_widget.py` | 20011 | 20007 |
| `tests/test_storage_pure.py` | 2318 | 2312 |

## Reachability measurements

The report intentionally exits 1 because unresolved inputs remain. No pin moved.

| Measure | Before | After |
| --- | ---: | ---: |
| `action_count` | 1663 | 1663 |
| `reachable_item_count` | 2301 | 2301 |
| `orphan_input_count` | 165 | 165 |
| `root_orphan_count` | 32 | 32 |
| `cascade_orphan_count` | 133 | 133 |
| `unresolved_action_count` | 252 | 252 |
| `seed_item_count` | 1215 | 1215 |
| blocked quest-stage rows | 139 | 139 |
| `completable_quest_count` | 51 | 51 |

## Global action-ID safety

The catalog contains 528 unique `auto_actions` IDs. Every ID has exactly one quest owner, and no `required_actions` ID is satisfied by a different quest's auto-action proof. The catalog pin fails when either a duplicate owner or a cross-quest gate is injected.

The Fishing Contest pure-runtime and dynamically loaded integration assertions also fail when stage 1 is mutated to emit stage 4's `Catch the winning giant carp` proof.

## Focused verification

- The proof migration, writer-census, and catalog-ownership module passes 16 tests.
- The three strengthened runtime and integration assertions pass.
- The storage migration module passes 75 tests.
- The five affected offscreen Qt quest-tab tests pass.

## Complete verification

```text
/opt/homebrew/bin/python3 run_tests.py
Ran 4601 tests in 769.861s
OK (skipped=515)

QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests
Ran 4601 tests in 1036.410s
OK (skipped=3)
```
