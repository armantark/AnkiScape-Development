# AnkiScape simulation-time boundary (2026-07-16)

Status: **base invariant and active-encounter behavior owner-settled; consumer
reconciliation active.** This
contract formalizes behavior that shops and Farming already implement, then records the
remaining foreground-state fork without changing runtime code during the design grill.

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
| Farming growth, disease, jobs, and regrowth | Every answered card | Settled and compliant (`__init__.py:1541-1546`, `runtime_actions.py:943-947`). |
| Daily/weekly eligibility such as the Agility Circus | Shared answered-card calendar | Settled and compliant (`agility_logic.py:198-229`). |
| Ordinary skilling, quests, Combat, Thieving, and Agility actions | Successful answer only | Settled and compliant (`__init__.py:1530-1553`). |
| Future familiar lifetime | Every answered card | Owner-settled in the Summoning grill. Uses short-duration conversion, not the six-minute calendar mapping. |
| Future familiar Summoning-point drain | Every answered card while summoned | Source-shaped consequence of the same lifetime: points drain during the familiar's life and remain separate from expiry. |
| Enemy attacks | Successful Combat action only | Current behavior; whether an active encounter attacks on Again is open. |
| Prayer drain | Combat-action burst only | Current behavior (`logic_pure.py:4857-4869`); reconcile with the active-encounter decision. |
| Poison and poison immunity | Combat or successful safe-recovery ticks only | Current behavior (`logic_pure.py:4070-4124`, `:4641`, `:5000`); reconcile with the active-encounter decision. |
| Out-of-combat LP/stat/special recovery | Successful non-Combat review only | Current behavior (`__init__.py:1517-1518`, `logic_pure.py:4613-4648`); reconcile so Again cannot become free healing inside a frozen encounter. |
| Agility boost and Surefooted budgets | Agility actions | Settled action budgets (`agility_logic.py:417-431`), despite older comments using review/hour pacing. |

## Decision 1 — idle during an active Combat encounter (settled 2026-07-16)

The owner selected **decay-only idle with no in-encounter recovery**. Again is
equivalent to briefly clicking outside the mob area: an already-active enemy does not
receive an attack beat, but elapsed state continues to decay. The paused encounter also
does not grant positive LP, stat, Prayer, or special-attack recovery.

The rejected alternative was:

- **Hostile idle:** the enemy receives one bounded combat beat on Again, alongside all
  elapsed-state decay. This is closer to literally standing AFK beside an attacking
  monster, but makes a learning failure directly deal damage and may encourage dishonest
  Hard grading.

The settled rule formalizes “punishing but not too punishing,” preserves the existing
rule that entities act only on a successful review, and avoids turning Anki grading into
a survival choice. Fable's strongest counterargument was simulation purity: a genuinely
engaged RuneScape enemy would keep attacking. The owner resolved that abstraction in
favor of decay-only idle.

## Reconciliation work after the owner answer

- Inventory every persisted duration, cooldown, drain, immunity, recovery, and reset.
- Classify it as calendar/world duration, short world duration, foreground action
  budget, explicit UI command, or encounter-owned beat.
- Correct misleading field names/comments only during the later implementation pass;
  do not perform a mechanical global rename without migration and undo tests.
- Add one dispatcher-level contract test proving Again advances world consumers but not
  foreground actions, then focused tests for each reclassified consumer.
