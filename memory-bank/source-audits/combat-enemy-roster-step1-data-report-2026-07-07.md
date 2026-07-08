# Combat Enemy Roster Step-1 Data Report — 2026-07-07

## Summary

Added 36 source-backed, pure-melee gap enemies from the local 2011Scape combat definition tree to `COMBAT_ENEMY_DATA`. This was data-only: no combat engine, UI, runtime action, or combat model files were changed.

**Review correction (2026-07-07):** the first pass added 38, including `gargoyle` and `rockslug`. Both were REMOVED on review: their source gates the kill on an item the combat model cannot express (`on_item_on_npc` — a Gargoyle must be smashed with a rock hammer, "You need a rock hammer to smash the gargoyle"; a Rockslug must be salted with a bag of salt). Adding them as ordinary melee enemies would let a player kill them without the item, deviating from the source. They are blocked on a required-finisher mechanic and stay out until it exists; `tests/test_combat_enemy_roster.py` now asserts they remain absent.

Source root:
`/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/`

## Added Enemies

### Iconic / Common Training And Slayer Staples — 14

- `lesser_demon` — `demons/lesser_demon_lvl_82.plugin.kts`
- `greater_demon` — `demons/greater_demon_level_92.plugin.kts`
- `black_demon` — `demons/black_demon_lvl_172.plugin.kts`
- `abyssal_demon` — `demons/abyssal_demon_level_124.plugin.kts`
- `hellhound` — `animals/hellhound_level_122.plugin.kts`
- `rock_crab` — `critters/rock_crab_lvl_13.plugin.kts`
- `ghoul` — `undeads/ghoul_level_42.plugin.kts`
- `werewolf` — `other/werewolf_level_88.plugin.kts`
- `ice_warrior` — `other/ice_warrior_level_57.plugin.kts`
- `earth_warrior` — `other/earth_warrior_level_51.plugin.kts`
- `baby_dragon` — `dragons/baby_dragon_level_48.plugin.kts`
- `baby_black_dragon` — `dragons/baby_black_dragon_level_83.plugin.kts`
- `nechryael` — `demons/nechryael_lvl_115.plugin.kts`
- `death_spawn` — `demons/death_spawn_lvl_46.plugin.kts`

### Slayer / Regional Pure-Melee Block — 12

- `banshee` — `undeads/banshee_level_23.plugin.kts`
- `shade` — `undeads/shade_level_83.plugin.kts`
- `ghost_level_77` — `undeads/ghost_level_77.plugin.kts`
- `cave_crawler` — `critters/cave_crawler_lvl_23.plugin.kts`
- `cockatrice` — `critters/cockatrice_level_37.plugin.kts`
- `cave_bug` — `critters/cave_bug_lvl_6.plugin.kts`
- `cave_slime` — `critters/cave_slime_lvl_23.plugin.kts`
- `crawling_hand` — `other/crawling_hand_level_8.plugin.kts`
- `cave_goblin` — `other/cave_goblin_level_3.plugin.kts`
- `canifis_citizen` — `humanoids/canifis_citizen_level_24.plugin.kts`

### Stronghold Of Security Pure-Melee Block — 11

- `flesh_crawler_level_28` — `critters/flesh_crawler_lvl_28.plugin.kts`
- `flesh_crawler_level_35` — `critters/flesh_crawler_lvl_35.plugin.kts`
- `flesh_crawler_level_41` — `critters/flesh_crawler_lvl_41.plugin.kts`
- `ankou_level_75` — `undeads/ankou_lvl_75.plugin.kts`
- `ankou_level_82` — `undeads/ankou_lvl_82.plugin.kts`
- `ankou_level_86` — `undeads/ankou_lvl_86.plugin.kts`
- `catablepon_level_49` — `other/catablepon_lvl_49.plugin.kts`
- `catablepon_level_64` — `other/catablepon_lvl_64.plugin.kts`
- `catablepon_level_68` — `other/catablepon_lvl_68.plugin.kts`
- `minotaur_level_12` — `other/minotaur/minotaur_lvl_12.plugin.kts`
- `minotaur_level_27` — `other/minotaur/minotaur_lvl_27.plugin.kts`

### TzHaar Pure-Melee Block — 1

- `tzhaar_hur` — `other/tzhaar_hur_lvl_74.plugin.kts`

## Skipped Audit Candidates

### Blocked On Engine Work

- Dragonfire / boss mechanics: `dragons/green_dragon_level_79.plugin.kts`, `dragons/blue_dragon_level_111.plugin.kts`, `dragons/red_dragon_level_152.plugin.kts`, `dragons/black_dragon_level_227.plugin.kts`, `dragons/king_black_dragon_level_276.plugin.kts`.
- Magic, ranged, or hybrid enemy attacks: `demons/bloodveld_level_76.plugin.kts`, `demons/pyrefiend_lvl_43.plugin.kts`, `demons/icefiend_level_13.plugin.kts`, `humanoids/dark_wizard_lvl_7.plugin.kts`, `humanoids/dark_wizard_lvl_20.plugin.kts`, `humanoids/wizard_lvl_9.plugin.kts`, `humanoids/infernal_mage_level_66.plugin.kts`, `undeads/aberrant_spectre_lvl_96.plugin.kts`, `undeads/skeleton_warlock_lvl_11.plugin.kts`, `other/tzhaar_xil_lvl_133.plugin.kts`, `other/tzhaar_mej_lvl_103.plugin.kts`, `humanoids/guthix_battle_mage_lvl_54.plugin.kts`, `humanoids/saradomin_battle_mage_lvl_54.plugin.kts`, `humanoids/zamorak_battle_mage_lvl_54.plugin.kts`.
- Multi-style revenants: all 15 `undeads/revenants/revenant_*.plugin.kts` files.

### Audit Exclusions Not Added As Ordinary Enemies

- `critters/rocks.plugin.kts` — Rock Crab disguised form, not a distinct enemy.
- `animals/template_guardian_lvl_30.plugin.kts` — quest boss with extreme magic immunity.
- `other/living_rock_protector.plugin.kts` — mining-hybrid activity, not a normal combat target.
- `humanoids/monks_of_zamorak.plugin.kts` — duplicate id-set of the existing Monk of Zamorak roster row.
- `humanoids/gardener_lvl_4_quest.plugin.kts` — single-instance quest NPC.
- `humanoids/johnny_the_beard_level_2.plugin.kts` — single-instance quest NPC.

### Deferred By Step-1 Scope

The audit lists additional pure-melee, low-priority or quest/minigame-flavored gap enemies that were not part of the Step-1 batch used here: Count Draynor, shadow warrior, weaponsmaster, jailer, tree spirit, and the Abyssal guardian/leech/walker family. They remain legitimate source-backed candidates for a later content slice.

## Unknown Drops / Judgment Calls

- No individual drop slot was omitted for unknown item names. Item names were resolved from the 2011Scape `Items.kt` constants and `data/cfg/items.yml`.
- Global nested drop tables were preserved by referencing existing AnkiScape data constants where already present: minor herbs, allotment seeds, uncommon seeds, gems, and mega rare.
- Plugins that omit `attackStyle` but have no ranged/magic attack block and have melee-compatible stats were treated as default melee, matching the audit classification and existing roster convention.
- Non-Slayer enemies use `hitpoints / 10.0` as `slayer_xp`, matching existing roster convention for non-assignment combat XP rows.

## Verification

```text
$ python3 -m py_compile combat_data.py tests/test_combat_enemy_roster.py
passed
```

```text
$ python3 -m unittest tests.test_combat_enemy_roster -v
test_new_enemies_have_required_schema (tests.test_combat_enemy_roster.CombatEnemyRosterDataTest.test_new_enemies_have_required_schema) ... ok
test_new_enemy_drops_are_well_formed (tests.test_combat_enemy_roster.CombatEnemyRosterDataTest.test_new_enemy_drops_are_well_formed) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.001s

OK
```

```text
$ python3 run_tests.py
Ran 853 tests in 14.923s

OK (skipped=152)
```
