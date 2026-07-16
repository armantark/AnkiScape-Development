# Slayer skill contract — 2026-07-15

Status: **owner grill active; implementation belongs in a later thread.**
Cutoff: `2012-11-20T00:00:00Z`.

This is the accumulating owner-decision contract for the complete Slayer
surface. Concrete historical pools, weights, sizes, levels, XP, points, rewards,
items, and gates remain subject to
`pre-eoc-source-verification-standard.md`; Darkan and game-main rows are leads
until they pass the required period reconciliation.

## Completion rule

The final contract must design every live pre-EOC Slayer master, assignment
family, qualifying monster variant, special-kill mechanic, Slayer dungeon or
task context, point/streak operation, reward, unlock, shop/equipment item,
quest/activity dependency, UI surface, asset, storage/migration path, telemetry
event, undo branch, and verification family. Missing exact evidence may leave a
value `source_blocked`; it cannot erase an attested feature.

## Settled architecture inherited from Combat

- Slayer owns masters, assignments, remaining-kill state, Slayer XP, streaks,
  points, cancellations/skips/blocks, reward unlocks, and its management UI.
- Combat remains the only fight engine. It owns target activation, attack ticks,
  ordinary Combat XP, supplies, enemy LP, player LP, drops, death/graves,
  encounter state, kill counts, and review undo.
- A qualifying Combat kill applies Slayer XP and task progress inside the same
  atomic review transaction. Fighting outside the task remains ordinary Combat
  and gives no Slayer XP or assignment progress.
- An incorrect review advances neither Combat nor Slayer action state. Shared
  answered-card calendar behavior remains governed by `systemPatterns.md`.
- Slayer creates no global player location and uses no wall-clock gameplay.
- The Skills-hub Slayer surface and Combat's Slayer intent/filter are two views
  of one task state, not two selectable combat handlers.

These boundaries continue the settled Combat contract in
`combat-design-grill-2026-06-23.md:213-216,327-329,395,506-512`.

## Owner decision 1 — assignment categories and exact target choice

**Decision:** preserve the source assignment identity. A broad assignment such
as birds, ghosts, goblins, trolls, or wolves remains a category; a specific
assignment remains specific. Every Combat enemy carries stable Slayer-category
membership rather than being matched through display-name substrings.

The player chooses the exact qualifying enemy variant. Accepting a task does not
auto-select the safest, weakest, strongest, or most profitable target. Combat
provides:

1. its ordinary reusable text search; and
2. a `Current Slayer task only` checkbox that intersects the current search and
   other Combat filters with the active task's qualifying variants.

The checkbox affects visibility only. It never changes the active Combat target,
equipment, supplies, or encounter. If the current target stops qualifying after
a task/state change, the runtime blocks Slayer credit rather than silently
retargeting combat.

### Source and code leads to reconcile

- Darkan `TaskMonster.java:24-135` represents both broad categories and specific
  families and lists multiple name variants for many categories.
- Darkan `SlayerTaskManager.java:61-69` currently performs substring matching;
  AnkiScape must replace that reconstruction shortcut with explicit stable
  membership data.
- Existing `combat_data.py` already carries many individual variants and Slayer
  XP leads, including multiple wolves, zombies, skeletons, and giants.
- Existing `ui.py` has a Shop-only `QLineEdit` search and Quest-only local filter
  controls, but no reusable list-search/filter component.

None of those local implementation facts independently proves a period pool or
value.

## Shared modular search dependency

Slayer must not add another page-local search implementation. The implementation
thread must first or concurrently extract a reusable list-search/filter seam
usable by Combat, Skills target lists, Quests, Bank, Shops, Equipment, and later
large pages where search materially helps.

The shared seam must support page-owned searchable text/metadata and optional
page-owned filters while centrally handling the search row, clear behavior,
empty state, keyboard focus, selection preservation, and dark-mode-safe styling.
Search/filter changes must never activate a row or replace a persisted target.
Slayer supplies the `Current Slayer task only` predicate; the shared component
does not know Slayer rules.

## Current source leads, not yet parity claims

- Darkan `SlayerTaskManager.java:115-170` models weighted assignment generation,
  a single active task, master eligibility, last-task exclusion, blocked tasks,
  quest/Slayer gates, and Turael replacement that clears the streak.
- Darkan `Task.java` contains master-specific category weights and kill-count
  ranges, including broad early tasks and much longer high-master tasks.
- Darkan task completion at `SlayerTaskManager.java:72-95` grants XP per kill,
  increments the streak, awards ordinary/tenth/fiftieth points, clears the task,
  and requires returning to a master for another assignment.
- game-main contains master dialogue, enchanted-gem, equipment-shop, and reward
  files, but its usable coverage and period fidelity remain to be audited.

## Owner decision 2 — assignment acquisition and stop point

Task completion is a real stop point. The player explicitly presses `Get
assignment`; the previous eligible master is preselected but may be changed
before confirming. No task chains automatically.

Choosing a master and receiving the rolled assignment is instantaneous UI and
costs no review. AnkiScape does not invent a walking, travel, dialogue, or
waiting action for visiting a Slayer master. The task roll, master, kill count,
streak-relevant state, and any source special-challenge offer commit together as
one undoable manual transaction.

This preserves the meaningful return-to-master decision without turning NPC
dialogue or absent world traversal into training.

## Cutoff exclusion — Slayer VIP tickets

Slayer VIP tickets are excluded. They released on `2014-04-14`, after the
AnkiScape cutoff, and their later choose-one-of-two assignment effect must not be
recreated under another name. See
`source-audits/slayer-vip-ticket-cutoff-2026-07-15.md`.

## Owner decision 3 — authentic task sizes

Source task kill-count rolls remain literal. One qualifying Combat kill removes
exactly one remaining kill, and long assignments may span as many reviews and
study sessions as they naturally require. AnkiScape adds no Slayer-specific
compression factor, batch credit, catch-up multiplier, or shortened review-scale
quantity.

Pacing remains the product of the source assignment roll, the chosen qualifying
enemy, Combat's existing action cadence, and the global actions-per-review
setting. The task state persists between sessions and retains the explicit
completion stop established above.

## Cutoff inclusion lead — Social Slayer

Social Slayer released on `2012-07-11`, before the cutoff. The official update
post describes two players grouping through an enchanted gem or slayer ring;
kills by either partner reduce the shared assignment, while Combat and Slayer XP
remain personal. This establishes a real period feature that must appear in the
completeness ledger, but it does not by itself authorize a fabricated solo
partner. See `source-audits/social-slayer-cutoff-recon-2026-07-15.md`.

## Owner decision 4 — park Social Slayer

Social Slayer is acknowledged in the completeness ledger and parked as a future
multiplayer dependency. The solo add-on does not simulate a partner, create an
AI contribution roll, shorten tasks in the name of co-op, expose dead co-op UI,
or add speculative shared-save state.

Reopen this branch only if AnkiScape gains genuine player-to-player shared state
and the owner explicitly authorizes multiplayer Slayer work. That outcome is
considered unlikely; the parked record exists to preserve historical
completeness, not to create an implementation promise.

## Cutoff inclusion — Slayer master challenges

All seven cutoff-live Slayer-master challenge families are attested by the
`2012-10-01` wiki revision. They are optional special assignments with distinct
compound objectives and completion rewards; the player may decline an offer for
a normal assignment without a point penalty. See
`source-audits/slayer-master-challenges-2026-07-15.md`.

## Owner decision 5 — preserve special challenges

The seven special challenges preserve their literal compound objective ledgers;
none is collapsed into an ordinary single-target assignment with a larger
reward. Location-only ceremony that AnkiScape cannot represent becomes concise
status text, while any required report or hand-in is an instantaneous,
review-free UI action.

Challenges remain occasional random offers in place of a normal assignment.
When the roll succeeds, `Get assignment` shows the chosen master's challenge
with `Accept challenge` and `Take a normal assignment`; declining has no point
penalty and immediately continues to the ordinary task roll. Challenges are not
selectable on demand.

The period sources establish an occasional roll after several consecutive tasks
for the relevant master but do not state the exact 2012 prerequisite or chance.
The modern `X/100` formula is absent from the cutoff revision and must not be
backported without corroboration. The prerequisite and probability remain
`source_blocked`; a later implementation may use only a source-closed value or
the smallest labeled hidden-roll abstraction allowed by the verification
standard.

## Quest-reactive Slayer masters

The Slayer-master roster must reflect canonical quest state. Completing While
Guthix Sleeps permanently changes Turael to Spria and Duradel to Lapalok.
Achtryn replaces Mazchna only during the relevant quest interval; Mazchna
returns afterward. The replacement carries the same functional master role,
assignment family, picker position, and management operations while changing
the displayed NPC identity, portrait, and source-appropriate copy. See
`source-audits/slayer-master-succession-2026-07-15.md`.

## Slayer master picker

There is no Slayer picker in the current runtime because Slayer implementation
has not begun. The design does require one: pressing `Get assignment` opens a
master-selection surface, preselects the last eligible master, permits choosing
another master, displays requirements and assignment/reward context, and then
performs the assignment or challenge-offer roll. Quest-reactive replacements
update this same surface rather than creating duplicate master rows.

## Owner decision 6 — progression-visible master roster

The picker always shows every cutoff-live standard Slayer-master role.
Ineligible masters remain visible but disabled, with every unmet combat, Slayer,
quest, or activity requirement stated directly on the row. A locked row cannot
be confirmed and does not participate in assignment or challenge rolls.

Eligible rows expose the master identity, requirements met, ordinary point
schedule, assignment-range summary, and challenge availability. The previous
eligible master remains preselected. Quest succession updates the identity and
portrait inside the existing role row; it never leaves the dead master visible
as another selectable master or creates a duplicate successor row.

## Next unresolved product branch

Determine what happens when While Guthix Sleeps crosses a permanent succession
boundary while a Turael- or Duradel-role assignment is already active: preserve
the exact task and original issuer provenance while the successor manages it, or
rewrite/cancel the active assignment.
