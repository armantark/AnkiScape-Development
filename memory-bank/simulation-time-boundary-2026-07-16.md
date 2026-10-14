# AnkiScape simulation-time boundary (2026-07-16)

Status: **base invariant, active-encounter behavior, live cadence, and Summoning
consumers reconciled; remaining catalog consumers active.** This contract
formalizes the shared event boundary without treating its different magnitude
classes as one literal clock.

## Settled invariant

Every valid answered card emits one **idle/world tick**, regardless of answer button.
Hard, Good, and Easy additionally emit one **foreground action** because Anki reports
them as successful (`ease > 1`). Again emits no foreground action.

In product language, **Again means the player idled for one simulation interval while
the world continued**. It is allowed to cost expiring time or background opportunity,
but it never awards XP, consumes an action queue step, attacks, gathers, processes an
item, or advances an activity stage merely for being answered.

Both channels are part of one review transaction. Anki undo restores the entire world
tick and foreground action together, including deterministic RNG consequences. The
computer wall clock never participates.

## Event and magnitude are separate

One answer always emits one world tick, but consumers do not all pretend that tick is
the same literal span of RuneScape time:

- **Calendar/economy consumers** keep the shipped scale: ten answers per simulated hour,
  240 per day, and 1,680 per week. Farming growth, shop restock, and calendar resets use
  this band.
- **Short activity-duration consumers** need a separate documented conversion. Reusing
  six minutes per answer literally would make a four-minute familiar expire within one
  card and a 44-minute Bunyip last about eight cards. The conversion must preserve
  sourced ratios without pretending ordinary actions take six minutes.
- **Foreground action budgets** count only an action that can actually use or progress
  them. A ten-Agility-action boost remains ten Agility actions; it is not a calendar
  duration merely because the period interface described some other effect in minutes.

This is not two competing clocks. It is one answered-card event with explicitly
different, labeled mappings for long calendar cadence and short gameplay cadence. The
mapping is an AnkiScape abstraction; period ratios and ordering remain source claims.

## Current implementation reconciliation

| System | Current channel | Settled/needs review |
|---|---|---|
| NPC shop/market progression | Every answered card | Settled and compliant (`__init__.py:1536-1541`, `shop_logic.py:142-149`). |
| Farming growth, disease, jobs, and regrowth | Every answered card | Settled and compliant (`__init__.py:1524-1529`, `runtime/runtime_actions_shared.py:754-758`). |
| Daily/weekly eligibility such as the Agility Circus | Shared answered-card calendar | Calendar boundary is compliant; carryover needs implementation after Decision 2 (`agility_logic.py:198-229`). |
| Ordinary skilling, quests, Combat, Thieving, and Agility actions | Successful answer only | Settled and compliant (`__init__.py:1530-1553`). |
| Familiar lifetime and Summoning-point drain | Every answered card while summoned | Implemented with exact residuals and the short-duration conversion; renewal resets phase and zero points create no debt. |
| Enemy attacks | Successful Combat action only | Owner-settled: an active encounter receives no attack beat on Again. |
| Prayer drain | Live Combat ticks only | Reconciled at `6 × M` immediate ticks with exact persisted counter state; Again grants no combat or Prayer-drain beat. |
| Poison and poison immunity | Combat or successful safe-recovery ticks only | Current behavior (`logic_pure/logic_pure_combat_supplies.py:1467-1521`, `:4641`, `:5000`); reconcile with the active-encounter decision. |
| Generic out-of-combat LP/stat/special recovery | Successful non-Combat review only | Current behavior (`__init__.py:5300-5301`, `ba2c5418:logic_pure.py:4613-4648`); this unsourced convenience recovery does not fire on Again. Source-classified passive effects are separate world consumers and may heal on Again. |
| Agility boost and Surefooted budgets | Agility actions | Settled action budgets (`agility_logic.py:609-623`), despite older comments using review/hour pacing. |
| Familiar passive healing and special-point recharge | Every answered card | Implemented as exact 6/25 and 6/50 short-duration residuals; passive benefits may resolve on Again. |

## Decision 1 — idle during an active Combat encounter (settled and clarified 2026-07-16)

The owner selected a **world-only idle tick with no foreground or encounter beat**.
Again is equivalent to briefly clicking outside the mob area: an already-active enemy
does not attack, the player does not act, and foreground commands do not fire. Elapsed
state continues and genuinely passive effects may still resolve. AFK means no user
input, not no benefit.

Generic safe LP/stat/Prayer/special recovery remains tied to successful foreground
reviews because it is an AnkiScape convenience helper rather than a sourced periodic
world effect. A sourced passive familiar heal or forage roll is different: once its
catalog row is classified as passive, it advances and may resolve on Again.

The rejected alternative was:

- **Hostile idle:** the enemy receives one bounded combat beat on Again, alongside all
  elapsed-state decay. This is closer to literally standing AFK beside an attacking
  monster, but makes a learning failure directly deal damage and may encourage dishonest
  Hard grading.

The settled rule avoids turning Anki grading into a survival choice without freezing the
world or deleting authentic passive benefits. Fable's strongest counterargument was
simulation purity: a genuinely engaged RuneScape enemy would keep attacking. The owner
resolved that abstraction in favor of pausing encounter beats while retaining passive
world behavior.

## Decision 2 — recurring-activity eligibility carryover (settled 2026-07-17)

Daily and weekly activity opportunities no longer disappear at their next
answered-card calendar boundary. Each activity banks one current entry and one
reserve, with a default cap of two. A source-specific activity may declare a
different cap only when its structure makes two materially unsuitable.

The bank stores permission to play, not the result. No XP, items, currency,
stages, or completion credit resolve automatically. The UI reports only the
available-entry count and does not warn about theoretical overflow. Banked
entries are optional content and never become progression requirements.

This supersedes the earlier design rule that daily and weekly allowances reset
without stacking, but it is not implemented yet. The existing calendar
boundary and undo behavior remain the correct substrate; consumers need a
bounded-entry migration rather than a second timer.

The rule is limited to recurring activities. Shop stock, Farming growth,
resource regeneration, equipment charges, and passive producers retain their
own source-shaped accumulation rules.

## Reconciliation work after the owner answer

- Inventory every persisted duration, cooldown, drain, immunity, recovery, and reset.
- Classify it as calendar/world duration, short world duration, foreground action
  budget, explicit UI command, or encounter-owned beat.
- Correct misleading field names/comments only during the later implementation pass;
  do not perform a mechanical global rename without migration and undo tests.
- Add one dispatcher-level contract test proving Again advances world consumers but not
  foreground actions, then focused tests for each reclassified consumer.

## Chronology moved from systemPatterns.md — 2026-09-16

### Simulation clock and eligibility decision

Original line range: 245-253.

- Historical timers use the global answered-card AnkiScape clock already shared
  by NPC shops and the parked GE: 10 answered cards equal one simulated game
  hour and 240 equal one simulated day. All answered cards advance the clock,
  regardless of skill or reward success; undo rolls time back. Daily/weekly
  allowances currently reset at simulated boundaries without stacking, never
  from the computer's wall-clock date. Owner decision 2026-07-17 supersedes
  this for recurring activity eligibility once implemented: bank one current
  entry plus one reserve by default, while rewards still require playing the
  activity. See `simulation-time-boundary-2026-07-16.md` Decision 2.
