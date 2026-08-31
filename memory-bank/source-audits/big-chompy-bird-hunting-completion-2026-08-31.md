# Big Chompy Bird Hunting completion and Raw chompy source audit — 2026-08-31

## Scope

This audit replaces all three generated stage sentinels that blocked Big Chompy Bird Hunting and adds the Chompy-hunting acquisition route that the quest unlocks. The route produces one `Raw chompy`, requires completion of Big Chompy Bird Hunting, consumes one `Ogre arrow`, and requires an `Ogre bow` as a non-consumed hunting tool.

The cutoff remains `2012-11-20T00:00:00Z`. No placeholder value is introduced. Zogre Flesh Eaters and `bone_sources.ogre_coffin_selector_weights` remain unchanged.

## Primary authorities

The quest walkthrough, hunting equipment, and rewards use the pinned period article:

- `https://runescape.wiki/w/Big_Chompy_Bird_Hunting?oldid=6408629`
- Revision timestamp: `2012-10-14T23:42:29Z`, recorded in `generated/quest_catalog_generated.py`.
- The article requires Cooking `30`, Ranged `30`, and Fletching `5`; describes making ogre arrows, retrieving ogre bellows and preparing toad bait, then luring a Chompy bird and killing it with an ogre bow and ogre arrows; and rewards an Ogre bow plus the ability to cook Chompy birds.
- After the kill, the walkthrough requires plucking the bird, taking the raw chompy to Rantz, gathering the three requested seasonings from Rantz, Fycie and Bugs, and spit-roasting the seasoned bird for Rantz.

The acquired item and quantity use the pinned period item article and the recorded acquisition audit:

- `https://runescape.wiki/w/Raw_chompy?oldid=6286360`
- The article states that `Raw chompy` is obtained by killing a Chompy bird, is an ingredient in Wild pie, and that the ability to hunt chompies is unlocked during Big Chompy Bird Hunting.
- `memory-bank/audits/acquisition-queue-final-2026-08-12.md:90-95` records the same revision as quantity `1`, rarity `Always` from Chompy bird.

`Raw_chompy?oldid=6286360` does not establish the ogre-bow or ogre-arrow gate by itself. That gate is supported by the Big Chompy Bird Hunting walkthrough above.

The local Darkan authority is pinned to revision `a2568b880390ef697b1b17e825fdef7868bed67f`:

- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/drops/chompy_bird.json` gives item `2876` at minimum `1`, maximum `1`, alongside feathers and bones in always-run tables.
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs/uncategorized/chompy_bird (noanims).json` gives the Chompy bird its checked-in combat definition and passive attack behavior.
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/skills/fletching/Fletching.java:33-63,156-160` identifies Feather `314`, Wolf bones `2859`, Ogre arrow shaft `2864`, Flighted ogre arrow `2865`, Ogre arrow `2866`, and the Achey-log Fletching row.
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/miniquests/recipe_for_disaster/freeing_skrach_uglogwee/FreeingSkrachUglogwee.kt:25-30,126-183` is the local executable reuse of the ogre-bow, ogre-arrow, lure, kill, and pluck mechanic. It also requires Big Chompy Bird Hunting before that miniquest can begin.

Darkan registers `BIG_CHOMPY_BIRD_HUNTING(102, 20)` in `com/rs/engine/quest/Quest.java:57`, but has no quest implementation package for it. The stage actions therefore use the pinned quest walkthrough as the direct stage authority and cite the local reusable mechanic as corroborating implementation evidence. No missing Darkan quest class is inferred.

## Stage mapping

| AnkiScape stage | Source-backed action | Existing gate retained |
| ---: | --- | --- |
| `1` | Fletch ogre arrows from achey logs, feathers, and wolfbone arrowtips, then give six arrows to Rantz. | Fletching `5`; `Feather` ×1; `Wolf bones` ×6. |
| `2` | Retrieve the ogre bellows, fill them with swamp gas, inflate swamp toads, and place the bait for Rantz. | The existing generated Chompy bird combat encounter. |
| `3` | Lure and kill a Chompy bird with an ogre bow and ogre arrows, pluck it, take the raw chompy to Rantz, gather the three seasonings from Rantz, Fycie and Bugs, then spit-roast the seasoned chompy for him. | Cooking `30` and Ranged `30` remain quest-start requirements. |

Each cleanup removes its exact `Complete Big Chompy Bird Hunting stage N objective` sentinel and adds one same-stage automatic action. This order is required because `logic_pure/logic_pure_quest.py:1329-1330` returns on blockers before a stage can record its automatic action.

The readable cleanup specifications live in `data/chompy_hunting_data.py` and all cite `BIG_CHOMPY_BIRD_HUNTING_STAGE_ACTION_SOURCE`, which combines the pinned quest revision and the resolved pinned local miniquest path. `data/quest_data.py` converts those specifications into its existing `QuestStageRequirementCleanup` contract. The generated item and combat gates remain intact.

## Acquisition route translation

`Utility:hunt_chompy_birds` uses the existing no-XP Utility/Activity producer contract:

- `QUEST_UNLOCK_RULES` requires completed Big Chompy Bird Hunting.
- `requirements` consumes one `Ogre arrow` per successful hunting action.
- `required_item_options` requires one `Ogre bow` without consuming it.
- The action produces `Raw chompy` quantity `1`.
- `UTILITY_ITEM_IMAGES` explicitly maps `Raw chompy` to `cookingitems/raw_chompy.png`, so the existing Utilities row renders its cooking asset.
- `UTILITY_ITEM_IMAGES` maps the consumed `Ogre arrow` to the existing `shopitems/ogre_arrow.png` before utility inputs are registered, so its canonical item definition and visible shop row retain an asset.

The consumable requirement also keeps the existing player-facing contracts honest. `core/target_metadata.py:1915-1917` now lists the Ogre arrow in the tooltip, and `runtime/runtime_actions_utility.py:790-799` can name the missing arrow in the out-of-materials message instead of showing an empty-material tooltip and a generic activity failure.

A generic combat-target row was not used. The live item registry and `data/quest_data.py:1031` use the canonical singular `Ogre arrow`, while `EQUIPMENT_DATA` contains the incompatible plural key `Ogre arrows`; `Ogre bow` has no equipment row. A player therefore cannot equip either required hunting identity through the combat equipment system. Closing the missing bow metadata and singular/plural ammunition mismatch is a separate follow-on slice, not a reason to invent combat equipment values here.

## Reachability instrument output

The baseline was measured from `a303496436ba61850ca6dcd2667eecd96d47e811`; the result was measured from the implementation tree. These are the values the current audit reports and therefore the values pinned in `tests/test_item_reachability_audit.py`.

| Measure | Before | After |
| --- | ---: | ---: |
| `action_count` | `1608` | `1609` |
| `reachable_item_count` | `2244` | `2257` |
| `orphan_input_count` | `190` | `179` |
| `root_orphan_count` | `39` | `37` |
| `cascade_orphan_count` | `151` | `142` |
| `unresolved_action_count` | `277` | `266` |
| `seed_item_count` | `1179` | `1182` |
| blocked quest-stage rows | `144` | `143` |
| completable quests | `45` | `46` |

Big Chompy Bird Hunting is the sole newly completable quest. This slice actually delivers exactly four newly reachable items:

- `Ogre bow` → `quest:big_chompy_bird_hunting`
- `Raw chompy` → `Utility:hunt_chompy_birds`
- `Raw wild pie` → `Utility:assemble_wild_pie`
- `Wild pie` → `Cooking:cook_wild_pie`

## Audit over-credit and excluded follow-on

The current reachability instrument also credits `Fayrg bonemeal`, `Fayrg bones`, `Ogre coffin key`, `Ourg bonemeal`, `Ourg bones`, `Raurg bonemeal`, `Raurg bones`, `Zogre bonemeal`, and `Zogre bones`. Those nine items are phantom additions, not delivered by this slice.

`tools/audit_item_reachability.py:943-948` builds the audit's `startable` quest set from required quests and required quest points without consulting required skills. At runtime, Zogre Flesh Eaters carries `QuestSkillRequirement(skill_id="combat", level=89)`, and `logic_pure/logic_pure_quest.py:146` returns the permanent sentinel `Combat 89 (not implemented)` because `combat` is a skill category rather than a registered `SkillDefinition`. `start_quest_pure` therefore refuses every player, so the Zogre target never opens.

The same audit gap affects `dream_mentor` combat `85`, `grim_tales` `100`, `legends_quest` `75`, `smoking_kills` `85`, `underground_pass` `79`, and `zogre_flesh_eaters` `89`. Fixing the audit or the combat-category requirement is explicitly outside this slice. The pinned values continue to record what the instrument reports; the prose does not treat its phantom nine as player-reachable work.
