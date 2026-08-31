# The Fremennik Isles combat lamp source audit — 2026-08-31

## Goal

The Fremennik Isles must not park an invalid `combat_exp` reward. Its period-correct reward is two independent 10,000 XP choices over Attack, Strength, Defence, and Constitution.

This slice changes no interface. It uses the existing quest-lamp claim contract and Bank Claims skill chooser.

## Defect

The generated catalog carried one `QuestXpReward(skill_id="combat", amount=10000.0)`. `combat` is a category, not a `SkillDefinition`, so `get_skill("combat")` returns `None`. Quest completion therefore stored the reward under `pending_skill_exp_rewards["combat_exp"]` instead of granting it.

The catalog also understated the source reward by 10,000 XP. It represented one 10,000 XP category row where the source records two separate choices.

## Period source

The pinned source is [The Fremennik Isles, oldid 6540919](https://runescape.wiki/w/The_Fremennik_Isles?oldid=6540919), timestamp `2012-11-07T09:46:34Z`. It is the closest revision before the Evolution of Combat cutoff at `2012-11-20T10:16:00Z`.

The walkthrough states:

> Talk to King Burowgar. After giving him the Ice Troll King head, the player is offered two 10,000 experience rewards to any two of Attack, Strength, Defence, or Constitution. The player can select the same skill twice if desired.

The reward list states:

```
* Two times 10,000 combat experience (choose among [[Strength]], [[Attack]], [[Defence]] or [[Constitution]])
```

The reward is two whole 10,000 XP choices. It is not one 10,000 XP reward and not a divisible 20,000 XP pool. The same skill may be selected twice. The pinned source gives no level requirement.

## Read-only implementation corroboration

The read-only Darkan implementation is `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/fremennikisles/FremennikIsles.kt`.

- Lines 128–131 define the fixed Construction 5,000, Crafting 5,000, Woodcutting 10,000, and per-choice combat 10,000 XP amounts.
- Line 180 limits combat choices to `Skills.ATTACK`, `Skills.STRENGTH`, `Skills.DEFENSE`, and `Skills.HITPOINTS`.
- Lines 496–501 grant exactly one `COMBAT_REWARD_XP` per choice and advance through two choice states without a level check.
- Lines 170–175 grant the three fixed XP rewards separately from the two combat choices.

Darkan's `Skills.HITPOINTS` and the wiki's Constitution both map to AnkiScape's `constitution`. AnkiScape uses `defense`, not `defence`.

## Implemented contract

`QUEST_XP_REWARD_REPLACEMENTS_BY_ID` now replaces The Fremennik Isles reward tuple with only the three verified fixed awards:

- Construction: 5,000 XP
- Crafting: 5,000 XP
- Woodcutting: 10,000 XP

`QUEST_LAMP_REWARD_REPLACEMENTS_BY_ID` now declares one `QuestLampReward` with amount 10,000, options `attack`, `strength`, `defense`, and `constitution`, minimum level 1, and quantity 2.

`_quest_lamp_claims()` expands that quantity into the distinct claims `the_fremennik_isles_xp_lamp_1` and `the_fremennik_isles_xp_lamp_2`. Each claim is independently validated and applied through `apply_claim_pure`. Both claims may target the same skill.

The oversized `data/quest_data.py` edit is line-neutral. The mandatory lamp replacement guard in oversized `tests/test_logic.py` shrinks that file while pinning the new entry. All new behavioral tests are in `tests/test_fremennik_isles_lamps.py`.

## Existing saves

A migration probe modeled a save that had completed the quest, still held `pending_skill_exp_rewards: {"combat_exp": 10000.0}`, and predated both new claim IDs. Loading it produced:

```
pending: {'combat_exp': 10000.0}
claim_states: {'the_fremennik_isles_xp_lamp_1': {'claimed': False}, 'the_fremennik_isles_xp_lamp_2': {'claimed': False}}
claim_eligible: {'the_fremennik_isles_xp_lamp_1': True, 'the_fremennik_isles_xp_lamp_2': True}
combat_exp_key_present: False
```

`_migrate_claim_state()` rebuilds default claim states from the live claim catalog, so completed saves automatically receive both unclaimed, eligible lamps on their next load.

`_migrate_pending_skill_exp_rewards()` preserves `combat_exp` because no trainable skill owns that experience key. No runtime consumer displays the parked category record or converts it into skill XP. It remains inert save weight while the two correct claims are available. Removing it would not fix a visible defect, so this slice adds no compatibility migration.

## Coverage

`tests/test_fremennik_isles_lamps.py` verifies:

- the fixed XP tuple contains only Construction, Crafting, and Woodcutting;
- one lamp definition expands into exactly two distinct claims;
- each claim pays 10,000 XP;
- both claims may target the same allowed skill;
- a skill outside the four options is refused;
- a real review answer completes the quest without any pending XP and exposes both claims;
- the real claim application entry point pays both claims; and
- every direct quest XP reward in `QUEST_DATA` resolves to a trainable `SkillDefinition`, naming the offending quest and skill ID on failure.

The existing replacement guard also pins the complete Fremennik lamp definition.

## Measurements

The reachability instrument did not move.

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

No reachability pin moved.


## Verification

The focused reward, claim, catalog-pin, and end-to-end selection passed five tests.

The complete plain lane reported:

```
Ran 4566 tests in 416.888s
OK (skipped=515)
```

The complete offscreen Qt lane reported:

```
Ran 4566 tests in 720.925s
OK (skipped=3)
```

An independent diff-only simplification and correctness review found no high-confidence issue or valid deletion. No interface file changed.
