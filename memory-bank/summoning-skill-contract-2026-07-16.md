# Summoning skill contract — owner grill (2026-07-16)

Status: **owner grill active; implementation deliberately not started.** This contract
is the durable decision ledger for the complete pre-EOC Summoning surface frozen at
2012-11-20. Historical facts and AnkiScape abstractions must stay visibly distinct.

## Product boundary

Summoning is the next missing skill to design because it is a bounded skill/economy
system that can reuse Combat, target-carried inventory, equipment, death, banking,
consumables, quests, undo, and the existing card-action clock. It must close before
Dungeoneering because Daemonheim is a later temporary-economy variant of several
ordinary skills, including Summoning. Slayer may consume Summoning outputs and award
charms, but neither skill may silently own the other's core loop.

There is no wall-clock gameplay. Any period mechanic expressed in seconds or minutes
must be translated into answered-card or explicit-action state. Source ratios and
ordering are preserved where they carry gameplay meaning; the conversion magnitude is
a labeled AnkiScape abstraction.

## Atomic completion rule

Implementation is complete only when all of these families are designed, sourced, and
shipped together or explicitly parked behind a named external dependency without being
made falsely player-visible:

1. **Acquisition:** the four ordinary charm families, tertiary ingredients, empty
   pouches, spirit shards, Talon Beast charms, abyssal/quest/activity inputs, drop and
   shop ownership, Bogrog shard returns, and saved-item compatibility.
2. **Training:** pouch infusion at obelisks, level/ingredient/shard/XP rows, pouch-to-
   scroll conversion, scroll quantities, Familiarisation rewards, boosts, and any
   period alternate training routes.
3. **Resource state:** maximum and current Summoning points, summon cost, continuing
   drain, obelisk/small-obelisk restore, potions/restores, death, and undo.
4. **Familiar lifecycle:** summon, one-active-familiar rule, duration, renewal,
   dismissal, expiry, death, forbidden contexts, persistence, switching targets, and
   what happens to carried familiar inventory.
5. **Abilities:** combat familiars, healers, beasts of burden, foragers, skill boosts,
   resource gatherers, teleports, light enhancers, remote viewing, passive effects,
   right-click abilities, scroll specials, special-move points, and familiar combat XP.
6. **Inventory and banking:** target-carried versus bank activation, BoB capacity and
   restrictions, deposit/withdrawal, bank-run interaction, death recovery, full-pack
   behavior, and item conservation.
7. **Cross-system hooks:** Combat presets and encounters, skilling targets, Agility
   travel hooks, Slayer drops/tasks, quests and pending XP, equipment, achievements,
   shops, activities, and future Dungeoneering isolation.
8. **UI and assets:** a Summoning skill page, training target families, pouch/scroll/
   familiar artwork, active-familiar and point readouts, summon/dismiss/renew/special/
   inventory controls, meaningful locks, search where the catalog needs it, and no
   decorative control that lacks runtime behavior.
9. **Persistence and proof:** storage migration, sanitization, deterministic RNG,
   review undo plus command undo where appropriate, pure/unit/integration/end-to-end
   tests, real offscreen Qt coverage, item reachability, and manual QA.

Completeness means the full period catalog, not a curated subset called a first version.
Rows whose hidden values remain unprovable may use the smallest clearly labeled
abstraction after a final source search; the feature itself is not deleted for lack of a
server-side number.

## Inherited AnkiScape rules

- One answered card or explicit UI action is the only permitted unit of progression.
- Target-carried presence activates gameplay items unless this grill records a narrower
  familiar-specific rule. Bank ownership alone is inert.
- Review undo and direct UI command undo remain separate, bounded histories.
- A familiar cannot create a second live copy of an item through expiry, dismissal,
  death, switching, banking, or undo.
- Existing Combat LP/death, inventory, equipment, quest, and consumable substrates are
  extended rather than duplicated.
- Ordinary Summoning state cannot leak into Daemonheim. Dungeoneering familiars and
  items belong to the future closed-session economy.

## Period baseline established before the first question

The closest pre-cutoff wiki revisions establish that:

- A pouch summoned one familiar and was consumed; only one familiar could be active.
- Each familiar had its own duration in minutes and its own initial point cost.
- Summoning points continued to drain over the familiar's life, but reaching zero did
  not dismiss it; zero disabled right-click abilities until points were restored.
- Scroll specials were separate from those right-click abilities and did not consume
  ordinary Summoning points.
- Obelisks, small obelisks, Summoning potions, and super restores restored points.
- Familiars covered materially different roles: combat, boosts, beasts of burden,
  healing, foraging, teleporting, and other bespoke abilities.

Evidence and confidence are recorded in
`source-audits/summoning-familiar-lifecycle-2026-07-16.md`.

## Open decision ledger

### 1. Familiar lifetime clock — settled 2026-07-16

**Every answered card** spends familiar lifetime, including Again. Again represents the
player idling for one simulation interval while the world continues; it never performs
the selected foreground action. This is the closest non-wall-clock analogue to global
uptime, keeps long-duration familiars and renewal meaningful across target switches, and
prevents duration freezing through an ineligible action.

The short-duration conversion preserves every familiar's sourced relative duration but
does **not** automatically reuse the calendar/economy scale of six simulated minutes per
card. That would reduce the shortest familiars to one card and make a 44-minute familiar
last about eight. The cross-system event/magnitude contract is
`simulation-time-boundary-2026-07-16.md`; exact short-duration calibration remains a
labeled balance abstraction.

Summoning-point drain follows the same answered-card lifetime while a familiar is out.
It remains a separate resource: reaching zero disables point-gated abilities but does
not dismiss the familiar.

### 2. Again during an active Combat encounter — settled 2026-07-16

Again is a **decay-only idle tick**. It is equivalent to briefly clicking outside the
mob area: elapsed state continues, but an already-engaged enemy receives no attack and
the paused encounter grants no positive recovery. See
`simulation-time-boundary-2026-07-16.md`.

### 3. Familiar renewal policy — source/app-pattern resolved 2026-07-16

Period renewal was a deliberate button available only at 2:30 or less, consumed one
unnoted pouch of the same familiar, reset the timer, and healed the familiar. AnkiScape
ships that manual Renew command exactly, translated through the short-duration card
mapping and the direct-command undo path.

It also ships one **global auto-renew toggle**, on by default. Auto-renew:

- may fire only on a successful answer, never on Again, because renewal is positive
  recovery rather than decay;
- consumes only an unnoted matching pouch in the current target-carried inventory,
  never a Bank stack;
- fires at the first eligible answer inside the period renewal window;
- performs the same timer reset and familiar heal as the manual command;
- never summons a replacement after expiry; and
- is global because the active familiar is global. A target-local toggle would silently
  change the same entity's survival policy when the player switches targets.

The carried-pouch requirement bounds depletion and gives target loadouts natural
control: a target that carries no spare matching pouch cannot auto-renew. Manual Renew
remains available regardless of the toggle when its source gates are met.

### 4. Beast-of-Burden cargo on expiry — open

The period game dropped all BoB cargo on expiry and gave the owner five minutes to pick
it up. AnkiScape has no ground or player-location state, so it must choose between a
lossless automatic Bank deposit and a review-timed reclaim buffer whose unclaimed cargo
is eventually destroyed.

## Source/open-work queue

- Harvest the complete pouch, familiar, duration, point, scroll, special-move-point,
  capacity, boost, combat, foraging, healing, teleport, and creation-XP tables.
- Reconcile pinned wiki revisions with the closest stable Darkan/2011Scape behavior for
  hidden rolls and state transitions.
- Inventory every period Summoning quest/activity/area gate and acquisition route.
- Audit existing charm, potion, quest, item, combat, inventory, death, and Agility hooks
  before asking the owner any question the repository already answers.
- Continue the owner grill one genuine design fork at a time. Each answer closes this
  ledger before the next question is asked.
