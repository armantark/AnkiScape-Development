# Combat Quest Shared Engine - 2026-06-24

Status: implemented. Quest combat gates now use the shared bounded combat burst
engine instead of the old instant threshold resolver when the encounter has
source-backed NPC stats.

## Scope

- `apply_quest_combat_encounter_pure()` now builds a quest-scoped enemy row and
  calls `apply_combat_burst_pure()` with the same equipment-derived attack style,
  hit rolls, damage rolls, auto-eat, death, XP, and bank-run behavior used by
  ordinary Combat.
- Runtime quest reviews pass the real `50 * Actions per review` tick budget,
  runtime RNG, and `EQUIPMENT_DATA`, so in-game quest fights use the same pacing
  and survival risk as ordinary Combat.
- Direct pure calls keep a deterministic compatibility default for older source
  and catalog tests; runtime callers always pass explicit review ticks and RNG.
- Partial quest enemy lifepoints persist in the new
  `quest_combat_active_encounters` side state so a quest fight can pause without
  overwriting the player's ordinary `current_combat_target` or
  `combat_encounter`.
- Quest enemy specs carry explicit no-drop schemas because quest combat gates
  advance quest state and do not invent ordinary farming loot.
- Source `npc_configs.max_hit` is honored as an enemy max-hit override when
  present; otherwise the existing melee-shaped max-hit formula remains the
  fallback.

## Save Migration

- Storage config version is now 24.
- New and migrated saves seed/sanitize `quest_combat_active_encounters` as an
  additive flat side state. Missing or malformed values migrate to `{}`.

## Deferred

- Quest encounters without source-backed critical combat stats remain blocked.
- Encounter-specific special mechanics beyond the shared ordinary burst model
  still require focused source audits before being enabled.
- Full broad combat systems from the design grill, such as Wilderness risk,
  Dwarf multicannon, broad equipment import, broader potion effects, and
  non-standard boss mechanics, remain future Combat work.

## Verification

- `python3 -m py_compile logic_pure.py storage_pure.py runtime_actions.py tests/test_logic.py tests/test_runtime_actions.py tests/test_integration_smoke.py`
- `python3 run_tests.py`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
