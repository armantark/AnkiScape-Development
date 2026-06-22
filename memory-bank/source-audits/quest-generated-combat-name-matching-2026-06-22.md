# Quest Generated Combat Name Matching

Date: 2026-06-22

## Scope

Backend-only generator/parser slice for the pre-EOC quest catalog. This does
not claim minute-detail quest parity. It improves safe source matching for
generated combat rows where the historical quest details already name a fight
and local 2011Scape/Darkan data already contains an exact or safely normalized
NPC source row.

No frontend surface changed in this slice. The existing Quests tab consumes the
same serialized `stage_requirements` contract and automatically benefits from
the richer generated combat payloads.

## Sources

- `tools/.cache/pre_eoc_quest_catalog` cached historical RuneScape Wiki
  revisions, regenerated through `tools/build_pre_eoc_quest_catalog.py`.
- Local 2011Scape NPC combat definitions under
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions`.
- Local Darkan/2012scape combat definitions under
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs`.

Specific rows improved:

- Temple of Ikov:
  - Historical row: `Several Guardians of Armadyl (level 45) ...`.
  - Safe normalized match: plural `Guardians of Armadyl` -> Darkan
    `Guardian of Armadyl` level 45.
  - Resolver stats now come from
    `guardian_of_armadyl_(45).json`.
- Observatory Quest:
  - Historical row: `Poisonous Spider (level 31) (10 approx.)`.
  - Alias match: `Poisonous Spider` -> local 2011Scape `Poison Spider`
    level 31.
  - Resolver stats now come from
    `poison_spider_lvl_31.plugin.kts`.
- Dwarf Cannon:
  - Historical row: `Lvl 2 Goblins`.
  - Parser now preserves the NPC name as `Goblins` instead of the old
    placeholder `Combat encounter`.
  - The local 2011Scape goblin file is attached as partial metadata only. It
    contains ID-dependent attack/defence expressions, so the generated row
    still fails closed as not resolver-ready until a focused Dwarf Cannon row
    identifies the exact quest spawn.

## Implementation Notes

- `tools/build_pre_eoc_quest_catalog.py` now normalizes NPC lookup through
  token-safe variants rather than raw substring matching. This prevents false
  positives such as `Bear` matching `Johnny The Beard`.
- Safe plural handling is token based, so rows such as `Guardians of Armadyl`
  can match an exact singular source row at the same combat level.
- `Poisonous Spider` is an explicit alias because the local 2011Scape source
  names the same level-31 enemy `Poison Spider`.
- Level-prefixed source text such as `Lvl 2 Goblins` is parsed into the combat
  display name instead of becoming a generic placeholder.

## Audit Delta

Before this slice:

- `combat_encounters_with_resolver_stats`: 177/285
- `statless_combat_encounters`: 108

After this slice:

- `combat_encounters_with_resolver_stats`: 179/285
- `statless_combat_encounters`: 106
- Remaining statless classifications:
  - `darkan_hitpoints_only_metadata`: 51
  - `darkan_missing_resolver_stats`: 18
  - `darkan_same_name_wrong_level`: 7
  - `local_exact_available`: 1
  - `no_local_source_match`: 10
  - `parser_or_variant_level`: 19

The single `local_exact_available` row is Dwarf Cannon's level-2 goblins. It is
not treated as complete because the local source has conditional NPC stats and
the generator cannot safely choose the exact variant.

## Verification

Targeted checks:

```bash
python3 -m unittest tests.test_pre_eoc_quest_catalog_builder tests.test_quest_catalog.TestQuestCatalog.test_generated_catalog_enriches_safe_combat_name_matches tests.test_quest_combat_stat_gap_audit
python3 tools/audit_quest_stage_gate_coverage.py
python3 tools/audit_quest_combat_stat_gaps.py
```

Manual Anki check for this backend-only slice:

1. Start Temple of Ikov and advance to the generated combat stage.
2. With `quest_combat_config.resolver_enabled = False`, confirm the row is
   still globally combat-locked.
3. Enable the resolver and set player combat high enough for level 45.
4. Confirm the Guardian of Armadyl row is a battle requirement instead of a
   missing-stats blocker.
5. Repeat for Observatory Quest's level-31 Poisonous Spider.
6. Confirm Dwarf Cannon still reports combat stats required for level-2
   Goblins instead of silently advancing.

Full-suite verification is tracked in the commit summary for this slice.
