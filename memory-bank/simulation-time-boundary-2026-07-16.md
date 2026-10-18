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
  this band. Daily, weekly and monthly resets read their day from the one shared world
  clock, `logic/pace/world_clock.py`, which owns the day's length (2026-10-18).
- **Short activity-duration consumers** count game ticks of their source duration and
  drain by each card's time budget, `6 × speed` ticks (owner assumption 4, 2026-10-15;
  classification below). They never reuse the calendar's six minutes per card, so a
  four-minute familiar lasts 67 cards at ×1 and seven at ×10.
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
| Familiar lifetime and Summoning-point drain | Every answered card while summoned | Ticks of the source minutes (`logic/pace/summoning_clock.py`); the drain spreads over the ticks lived, renewal resets phase and zero points create no debt. |
| Enemy attacks | Successful Combat action only | Owner-settled: an active encounter receives no attack beat on Again. |
| Prayer drain | Live Combat ticks only | Reconciled at `6 × M` immediate ticks with exact persisted counter state; Again grants no combat or Prayer-drain beat. |
| Poison and poison immunity | Combat or successful safe-recovery ticks only | Current behavior (`logic_pure/logic_pure_combat_supplies.py:1467-1521`, `:4641`, `:5000`); reconcile with the active-encounter decision. |
| Generic out-of-combat LP/stat/special recovery | Successful non-Combat review only | Current behavior (`__init__.py:5300-5301`, `ba2c5418:logic_pure.py:4613-4648`); this unsourced convenience recovery does not fire on Again. Source-classified passive effects are separate world consumers and may heal on Again. |
| Agility boost and Surefooted budgets | Agility actions | Settled action budgets (`agility_logic.py:609-623`), despite older comments using review/hour pacing. |
| Familiar passive healing and special-point recharge | Every answered card | Exact 25- and 50-tick residuals fed by the card's ticks; passive benefits may resolve on Again. |

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

### Short timers on the card's time budget (2026-10-18)

Owner assumption 4 of the pace decisions (2026-10-15): short timers count down by the
time budget of each card, `6 × speed` game ticks, so a timer lasts the same play time
at every speed. The rule applied to each countdown: it becomes a tick count only when
its source value is a duration of time; a count of actions stays a count; a calendar
duration (a day or longer) stays on the shared world clock; a countdown in cards with
no sourced duration stays in cards. One source minute is 100 ticks of 0.6 seconds. A
timer keeps the answers that drain it (every answer, or successful answers only).

| Timer | Source value | Class | Result |
|---|---|---|---|
| Familiar lifetime | Per-familiar `Time (minutes)` column, wiki oldid 6579789 (`summoning-familiar-lifecycle-2026-07-16.md:38`); `duration_minutes` in the generated catalog | Short duration | Ticks: `duration × 100`, every answer. A 44-minute familiar lasts 74 cards at ×10 and 734 at ×1. |
| Summoning-point drain | `required level − initial cost` over the familiar's life, oldid 6542597 (`summoning-familiar-lifecycle-2026-07-16.md:41`) | Follows the lifetime | Spread over the lifetime in ticks; residual in point-ticks. |
| Special-move recharge | 15 points every 30 seconds, oldid 5907879 (`summoning-familiar-lifecycle-2026-07-16.md:51`) | Short duration, already 15 per 50 ticks | Every answer adds the card's ticks instead of a flat 6. |
| Bunyip healing | 20 life points every 15 seconds (`summoning-familiar-effects-2026-07-17.md:23-24`) | Short duration, already 20 per 25 ticks | Every answer adds the card's ticks instead of a flat 6. |
| Triple charms | 40 seconds per raw shard, rounded to the minute (`summoning-familiarisation-2026-07-16.md:24-25`) | Short duration | Ticks: `minutes × 100`, every answer. |
| Cargo reclaim | Five-minute retrieval window after expiry, oldid 6288415 (`summoning-familiar-lifecycle-2026-07-16.md:49`) | Short duration | 500 ticks, every answer. |
| Renewal window | Renew at 2:30 or less, oldid 6093772 (`summoning-familiar-lifecycle-2026-07-16.md:47`) | Short duration | 250 ticks of lifetime left. |
| Gnome Restaurant delivery window | Easy six and hard eleven source minutes (`data/gnome_restaurant_data.py:29-34`) | Short duration | 600 and 1,100 ticks, successful other-target answers only; Again still pauses (2026-10-14 ruling). The easy window is 10 cards at ×10. |
| Gnome Restaurant hard-decline wait | Five source minutes (`data/gnome_restaurant_data.py:36-37`) | Short duration | 500 ticks, every answer. |
| Magic charge, antifire, super antifire, Shooting Star ore bonus, skilling temporary levels | Charge seven minutes (`magic-charge-reconciliation-2026-07-17.md:21`); antifire six minutes (`parity-deviation-ledger-2026-07-06.md:30`); ore bonus fifteen minutes (`data/shooting_star_data.py:25-27`); all stored in ticks | Short duration, already ticks | Successful non-Combat cards drain the card's ticks instead of 50 per unit of speed; live Combat keeps its elapsed ticks. |
| Thieving stun | `stun_ticks` per target (`data/thieving_data.py`) | Short duration, already ticks | Already a tick debt on the running budget; unchanged here. |
| Wild jade vine bind | Six ticks on the same debt | Short duration, already ticks | Already a tick debt; unchanged here. |
| Evil Tree blessing | Six to thirty minutes by tier, wiki Evil Tree oldid 6569638 (`evil-tree-implementation-harvest-2026-07-19.md:39-47`) | Short duration | Ticks: `minutes × 100`, every answer. |
| Livid Farm More Planks Please | Twenty minutes (`livid-farm-loop-2026-07-18.md:301`) | Short duration | 2,000 ticks, every answer. |
| Surefooted and Greater Surefooted window and cooldown | 20 and 40 minutes, two-hour cooldown, oldids 5832212 and 6151870 (`agility-complete-content-inventory-2026-07-15.md:198`) | Short duration, already in six-tick Agility steps (333, 667, 2,000) | Unchanged: Agility spends one six-tick step per obstacle, so both drain by the budget while Agility runs. Their "reviews" labels count Agility steps. |
| Shades of Mort'ton sanctity decay | About one point per 30 seconds (`shades-of-mortton-loop-2026-07-18.md:19`) | Short duration, already one point per ten six-tick steps | Unchanged: one decay beat per Shades step. |
| Prayer hosted-house search, 1 to 10 | Modeled review friction, no source duration (`action-unit-normalisation-2026-08-22.md:59`, `:63`) | Count of Prayer steps | Unchanged. |
| Pet growth and hunger | 25 cards per stage, 6 or 3 hunger per card; per-pet rates remain harvest work (`summoning-pets-2026-07-16.md:75-76`) | Cards, no sourced duration | Unchanged. |
| Familiarisation segments | Four successful answers of 15 shards, a balance abstraction (`summoning-familiarisation-2026-07-16.md`, "Settled AnkiScape translation") | Count of successes | Unchanged. |
| Familiarisation cooldown | One week after participation (`summoning-familiarisation-2026-07-16.md:27-28`); 1,680 cards | Calendar duration | Unchanged here; belongs on world days with the calendar. |
| Court Cases Batch 2 cooldown | Fourteen days (`data/court_cases_data.py:9`); `14 ×` the default world day | Calendar duration | Unchanged here; belongs on world days with the calendar. |

Bank trips, graves and rest healing count cards with no sourced trip length and stay
in cards. World events that spawn and expire on the card clock follow the calendar.

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
