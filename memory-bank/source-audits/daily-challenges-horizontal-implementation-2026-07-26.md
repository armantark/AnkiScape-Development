# Daily Challenges horizontal implementation

Date: `2026-07-26`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **breadth level one.** Every state, policy, failure mode and reward is
reachable and covered by tests.

## Sources used

| what | source | pinned id |
| --- | --- | --- |
| five-slot queue, one per day, oldest-first removal, pinning, per-skill blocks | RuneScape Wiki `Challenge System (historical)` | oldid `6579729`, 2012-11-19T02:58:19Z |
| challenge names, task text, quantities and level requirements | RuneScape Wiki `Challenge System (historical)/Challenges` | oldid `6563665`, 2012-11-16T09:49:20Z |
| Challenge Mystery Bag: hand-in only, pays back the Grand Exchange value of the items turned in | RuneScape Wiki `Challenge Mystery Bag` | oldid `6548968`, 2012-11-12T03:53:42Z |
| Challenge XP Lamp: combat challenges, player picks the skill | RuneScape Wiki `Challenge XP Lamp` | oldid `6422002`, 2012-10-15T14:50:21Z |
| item ids 25071 and 25070 | RuneScape Wiki item infoboxes (current revision; both items released 2012-09-19 and unchanged) | — |
| art | wiki file revisions dated 2012-09-19 and 2012-09-29, both pre-cutoff | — |

## What ships

Nine real period challenges across six skills, chosen as the smallest set that
exercises every mechanic:

- **Rampage Mk I** (combat, level 1, no hand-in) — kill credit above a named
  combat level, and the only route to a Challenge XP Lamp.
- **Copper Ore / Tin Ore / Clay** (mining, level 1, hand-in) — single-item
  output credit.
- **Chicken** (cooking, level 1, hand-in) and **Seafood buffet!** (cooking,
  level 1, hand-in) — single- and multi-item output credit.
- **How Shellfish** (fishing, level 1, hand-in) — multi-item credit on raw
  output.
- **Normal Logs** (firemaking, level 1, no hand-in) — action credit, where the
  thing counted is not the item produced.
- **Oak logs** (woodcutting, level 15, hand-in) — the only row above level 1,
  so the level gate is provably load-bearing.

Progress accrues from ordinary reviews through the shared post-outcome seam
`_record_action`, which is where telemetry and achievements already watch. No
challenge has its own action row.

## Decisions honoured

`design-thread-queue.md` 4.4. Five active slots, one new challenge per
240-answered-card day, oldest removed when a sixth would arrive, one pinned task,
per-skill blocking only for maxed skills. **No skip and no reroll**: the earlier
AnkiScape record invented that action and it is not implemented.

## Rewards, and how a player reaches each one

| reward | route | test |
| --- | --- | --- |
| bonus XP in the challenge's skill | finish any non-combat challenge and hand it in | `test_a_hand_in_takes_the_items_and_pays_bonus_xp_and_a_mystery_bag` |
| Challenge Mystery Bag | finish any hand-in challenge; the bag opens for the exchange value of the items turned in | `test_the_mystery_bag_pays_back_the_value_of_what_was_handed_in` |
| Challenge XP Lamp | finish Rampage Mk I, then rub the lamp in a chosen skill | `test_the_lamp_grants_its_experience_in_the_chosen_skill` |

## Failure modes

- A challenge completed but left to expire off the end of the queue pays
  nothing, matching the page's own warning about the Quartermaster.
- A hand-in with the items no longer held is refused and names the shortfall, so
  the player can re-obtain them.
- Blocking a skill below level 99 is refused; the period opt-out is maxed-skill
  only.

## Placeholders

Two, both registered in `memory-bank/placeholder-values.md`:
`daily_challenges.reward_xp` and `daily_challenges.assignment_weights`. Neither
invents content: the period had reward XP and had a selection rule; only the
numbers are unrecovered.

## Deliberate deferrals

The period catalog holds hundreds of challenges across 25 skills. Nine ship.
Widening the table adds rows, not mechanics.
