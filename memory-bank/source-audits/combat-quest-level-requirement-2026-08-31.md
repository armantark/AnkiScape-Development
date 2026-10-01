# Combat quest level requirement source audit — 2026-08-31

## Goal

Six quests use `combat` as a level requirement. The quest gate must use the derived player combat level.

The gate must keep the `(not implemented)` blocker for an unknown skill. This slice does not change quest stages or the user interface.

## Runtime authority

`logic_pure/logic_pure_combat_engine.py:2066-2079` computes the player combat level from eight combat stats. This is the existing game value.

`logic_pure/logic_pure_quest.py:111-130` now handles `skill_id == "combat"` before the skill registry check. A low level gives `Combat N`. A sufficient level gives no blocker.

The quest module already imported `player_combat_level_pure`. The combat engine does not import the quest module, so this change adds no import cycle.

The normal registry path is unchanged. An absent or non-trainable skill still gives `Skill N (not implemented)`.

## Affected quests

The live `QUEST_DATA` query returned exactly these six combat requirements.

| Quest | Required combat level | Result with a maxed player |
| --- | ---: | --- |
| `dream_mentor` | 85 | Starts |
| `grim_tales` | 100 | Starts |
| `legends_quest` | 75 | Starts |
| `smoking_kills` | 85 | Starts |
| `underground_pass` | 79 | Starts |
| `zogre_flesh_eaters` | 89 | Starts |

`tests/test_combat_quest_gate.py:192-228` covers the low Zogre gate and all six start results.

## Catalog guard

`tests/test_combat_quest_gate.py:142-153` scans quest-level and stage-level `required_skills` rows. Each skill ID must resolve to a trainable skill or equal the exact string `combat`.

The assertion reports the quest ID and invalid skill ID. A typo, an unknown pseudo-skill, or the wrong `Combat` case now fails the suite.

## Reachability audit decision

`tools/audit_item_reachability.py:919-950` uses prerequisite quests and quest points for quest completion and startability. It does not read `required_skills`.

The audit later builds a normal maxed player. It gives every trainable skill its maximum level and computes a derived maximum combat level.

A differential probe added a max-player skill filter around the existing quest closure. The probe did not change tracked files.

The probe measured these facts:

- The live quest catalog contains 196 quests.
- All 196 quests pass their skill requirements for the audit maxed player.
- No live quest uses an unknown or non-trainable required skill after `combat` uses the derived level.
- The audit maxed player has combat level 138.
- The skill-aware report equals the current report as a complete dictionary.

The current audit result is therefore honest after the runtime fix. This slice does not change the audit or any pin.

A future quest with an unknown required skill would expose a general audit hardening gap. No current route depends on that hypothetical case.

## Zogre product proof

`tests/test_combat_quest_gate.py:200-270` loads the real add-on module and calls `on_set_quest`. It then calls the real `on_answer_card` review entry point.

The player has combat level 89 and both prerequisite quests complete. Zogre Flesh Eaters starts at progress 0 and remains incomplete.

The test lowers only the Zogre combat stats for a deterministic one-review kill. It keeps the real quest gate, drop table, item routes, and review dispatch.

The combat review produces `Ogre coffin key` and `Zogre bones`. The quest remains at progress 0 and remains incomplete.

`tests/test_bone_sources.py:58-201,286-346` already drives the real coffin and grinding actions. It produces all four bones and all four bonemeals from the key and Zogre bones.

Together, the product review and existing route coverage prove these nine item identities after quest start:

- `Ogre coffin key`
- `Zogre bones`
- `Fayrg bones`
- `Raurg bones`
- `Ourg bones`
- `Zogre bonemeal`
- `Fayrg bonemeal`
- `Raurg bonemeal`
- `Ourg bonemeal`

The six Zogre stage sentinels remain unchanged.

## Measurements

A disposable probe measured the base commit `b62cec83` and the result tree.

| Measure | Before | After |
| --- | ---: | ---: |
| `action_count` | 1609 | 1609 |
| `reachable_item_count` | 2257 | 2257 |
| `orphan_input_count` | 179 | 179 |
| `root_orphan_count` | 37 | 37 |
| `cascade_orphan_count` | 142 | 142 |
| `unresolved_action_count` | 266 | 266 |
| `seed_item_count` | 1182 | 1182 |
| blocked quest-stage rows | 143 | 143 |
| completable quests | 46 | 46 |

No pin moved.
