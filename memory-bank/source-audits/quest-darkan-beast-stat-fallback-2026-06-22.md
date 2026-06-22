# Quest Darkan Beast Stat Fallback - 2026-06-22

## Scope

This slice continues the quest-stage/combat parity goal, but it is not a full
every-quest completion. It adds a conservative generated-catalog fallback for
Darkan/2012scape combat definitions that have hitpoints/configs but zero or
missing resolver stats. The fallback uses Darkan `developer-information/beasts.txt`
only for attack, defence, magic, and ranged, and only when the merged row still
satisfies the existing style-aware resolver contract.

## Source Order

1. Local 2011Scape remains preferred where it has quest or NPC mechanics.
2. Darkan/2012scape combat definitions remain the next source for generated
   combat payloads.
3. Darkan `developer-information/beasts.txt` is now a narrow fallback for
   missing or zero attack/defence/magic/ranged fields.
4. Historical runescape.wiki old revisions remain the quest prose/source-text
   basis for generated combat rows.
5. OSRS wiki remains cross-check only.

## Source Evidence

- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs/uncategorized/lava_monster/lava_monster_(47) (nostats) (noanims).json`
  provides Lava monster hitpoints 260, maxHit 80, and `attackStyle: RANGE`.
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/developer-information/beasts.txt`
  provides Lava monster id 7772 attack 28, defence 38, magic 0, and ranged 38.
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs/uncategorized/nomad (nostats) (noanims).json`
  provides Nomad hitpoints 10000, maxHit 322, and `attackStyle: RANGE`.
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/developer-information/beasts.txt`
  provides Nomad id 8528 attack 75, defence 75, magic 75, and ranged 75.
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/developer-information/npcList.txt`
  supplies Darkan NPC identity rows used by the exact-ID and unambiguous
  name/level matching layer.
- Historical quest prose still comes from the pinned generated catalog sources:
  `TokTz-Ket-Dill?oldid=6493266` and `Nomad's_Requiem?oldid=6386610`.

## Backend

- `tools/build_pre_eoc_quest_catalog.py` now loads
  `DARKAN_BEASTS_PATH` and merges beast attack/defence/magic/ranged only into
  zero or missing Darkan combatdef stat fields.
- Matching is intentionally narrow: exact combatdef `ids` first, then
  unambiguous name/level identity through Darkan `npcList.txt`.
- The generator still rejects the row unless
  `_combat_payload_has_resolver_stats()` passes after the merge.
- Beast metadata does not contain Strength, so melee/unknown rows that lack
  sourced Strength remain blocked.
- `npc_stats_source` mentions `beasts.txt` only when a beast value actually
  contributed to the generated stats.

## Frontend

- No new Qt widget contract was needed. Existing quest availability states and
  blocker copy already show mixed current-stage blockers.
- TokTz-Ket-Dill stage 6 now shows a resolvable Lava monster battle while the
  TokTz-Ket-Dill and Fire monster rows remain `combat_missing_stats`.
- The Quests tab keeps started-but-blocked quests visible when hiding
  unable-to-start quests, preserving startability vs finishability.

## Current Audit

`python3 tools/audit_quest_stage_gate_coverage.py`:

- 194/194 quests have at least one stage requirement.
- 171 quests have item/tool/option blockers.
- 119 quests have combat blockers.
- 285 combat encounter rows exist.
- 159 combat encounter rows have resolver-ready source-backed stats.

`python3 tools/audit_quest_combat_stat_gaps.py`:

- 126 statless combat rows remain.
- 56 are Darkan hitpoints-only metadata rows.
- 18 are Darkan rows missing style-critical resolver stats.
- 9 are same-name/wrong-level rows.
- 16 have no local source match yet.
- 27 are parser/variant-level rows.

## Deferred Gaps

- This does not complete every quest down to minute detail.
- Exact per-stage placement, route flags, action flags, partner/branch state,
  puzzle state, and quest-item transformations remain open.
- Combat simulation remains out of scope; current support resolves one
  source-backed current-stage encounter id per Quest review.
- Melee encounters without sourced Strength remain hard-blocked.
- Examples still blocked include Fight Arena's Khazard scorpion/ogre, Monkey
  Madness's Jungle demon, TokTz-Ket-Dill itself, and many hitpoints-only Darkan
  rows.

## Tests And Manual Anki Instructions

- Unit: `tests/test_quest_catalog.py`, `tests/test_logic.py`, and
  `tests/test_quest_combat_stat_gap_audit.py` cover generated payloads,
  style-aware resolver readiness, and the reduced statless gap counts.
- Integration: `tests/test_runtime_actions.py` and
  `tests/test_integration_smoke.py` cover Quest review resolving Lava monster
  without advancing or completing TokTz-Ket-Dill.
- Qt/offscreen: `tests/test_main_menu_widget.py` covers the Quests tab showing
  mixed missing-stats plus battle-required blockers while allowing selection.
- Manual Anki check:
  1. Start Anki with this add-on enabled.
  2. Open AnkiScape, enable developer mode if needed, and set Quest combat
     resolver config on for the test save.
  3. Put TokTz-Ket-Dill in progress at stage 6 with combat levels around 50.
  4. Open Quests and confirm the quest row shows TokTz-Ket-Dill and Fire
     monster as stat blockers plus Lava monster as a battle requirement.
  5. Select TokTz-Ket-Dill as the active Quest and answer one review.
  6. Confirm the floating gain says `Defeated Lava monster`, the quest remains
     at stage 6, and no quest XP/reward fires.
