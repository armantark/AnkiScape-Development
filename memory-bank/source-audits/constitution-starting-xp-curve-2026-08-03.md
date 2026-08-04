# Constitution starting XP and curve source audit

Date: 2026-08-03  
Cutoff: 2012-11-20  
Scope: Pass 7 Constitution progression defect only.

## Verdict

Constitution uses the standard RuneScape skill XP curve. A new player starts at
Constitution level 10 with 1,154 total XP. Level 11 starts at 1,358 total XP, so
the first Constitution level requires 204 earned XP.

AnkiScape had an invalid hybrid state. It started Constitution at level 10 but
stored zero total XP, then used the standard curve for later levels. This made
level 11 require 1,358 newly earned XP. Existing saves need the missing 1,154
starting XP added once. Their earned Constitution XP must remain unchanged.

## Period sources

- [Constitution oldid 6462802](https://runescape.wiki/w/Constitution?oldid=6462802),
  revision 2012-10-24: players begin at Constitution level 10.
- [Experience oldid 6545135](https://runescape.wiki/w/Experience?oldid=6545135),
  revision 2012-11-09: the generic skill formula and table give 1,154 XP for
  level 10 and 1,358 XP for level 11. The same page extends that curve through
  level 120 for Dungeoneering.
- Local 2011Scape
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/src/main/kotlin/gg/rsmod/game/model/skill/SkillSet.kt`:
  `getLevelForXp` and `getXpForLevel` use one `XP_TABLE` for every skill. The
  separate Dungeoneering constant changes its cap, not the level formula.

The local 2011Scape new-account serializer does not seed Constitution level 10,
so it is not evidence for the starting total. The pinned period pages settle
that value.

## Later exception

[Invention oldid 37105155](https://runescape.wiki/w/Invention?oldid=37105155)
records that Invention was released on 25 January 2016 as the first elite skill
and uses a different progression curve. That is a later RuneScape mechanic and
does not change the 2012 contract.

## Implementation boundary

- New saves start Constitution at level 10 and 1,154 XP.
- Saves from schema 110 or earlier receive exactly 1,154 additional Constitution
  XP during the schema-111 migration.
- The migration recalculates upward from the saved level after adding the
  baseline. It does not lower a saved level.
- The standard `EXP_TABLE` remains the Constitution curve.
- Dungeoneering remains the only cutoff-era skill with a table extension beyond
  level 99.

## Regression evidence

- `tests.test_storage_pure.TestStoragePure.test_default_player_data_has_expected_keys`
  pins the new-save level and XP pair.
- `tests.test_storage_pure.TestStoragePure.test_v111_migration_restores_constitution_starting_xp_once`
  pins a missing legacy value, the owner's persisted XP shape, the level-11
  result, and one-time migration behavior.
- `tests.test_runtime_actions.TestRuntimeActions.test_combat_level_refresh_leaves_the_old_level_for_the_level_up_gate`
  pins the runtime level-up boundary.
- `tests.test_integration_smoke.TestIntegrationSmoke.test_fractional_constitution_xp_is_not_displayed_as_zero`
  pins visible fractional Constitution XP.
