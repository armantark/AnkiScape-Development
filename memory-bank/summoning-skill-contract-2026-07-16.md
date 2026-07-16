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

### 4. Beast-of-Burden cargo on expiry — settled 2026-07-16

The period game dropped all BoB cargo on expiry and gave the owner five minutes to pick
it up. AnkiScape represents that as a **separate grave-like familiar-cargo reclaim
state**, not an automatic Bank deposit and not an overload of `combat_grave`.

Each cargo pile has its own five-source-minute deadline translated through the settled
short-duration answered-card mapping. Reclaim is a free direct UI command with bounded
command undo. If the deadline passes, the cargo is destroyed; review undo restores the
pre-expiry event. Multiple drops retain independent deadlines.

The reviewer shows both ordinary graves and expiring familiar cargo as distinct small
icons above the XP/progress HUD. Grave and cargo use different period-sourced art,
labels, tooltips, countdown semantics, and click behavior. The reusable cross-system UI
contract is `review-hud-world-alerts-contract-2026-07-16.md`.

### 5. Beast-of-Burden inventory identity — source/app-pattern resolved 2026-07-16

The period game gave a BoB a separate restricted inventory, while AnkiScape already has
one target-carried 28-slot pack and automatic/custom packing. BoB storage remains a
**separate inventory** with its sourced capacity and item restrictions. Flattening it
into a larger player pack would make expiry cargo arbitrary and erase period rules such
as essence-only abyssal storage and no access during combat.

The separate inventory appears as a familiar sub-pack in Bank/Equipment and the active
familiar surface. Advanced packing gets an explicit familiar grid. Casual packing may
project target-aware automation onto the same inventory without merging the underlying
state.

### 6. Familiar selection and Beast-of-Burden packing — settled 2026-07-16

The active familiar is one **global equipment entity**, not a Combat-only loadout field.
Its canonical panel lives with Equipment and is projected read-consistently into Bank,
the reviewer, and target configuration surfaces. The canonical panel owns the live
familiar, remaining lifetime, Summoning points, Summon/Dismiss/Renew/special commands,
the global auto-renew toggle, and the separate BoB inventory. Contextual projections
never create a second copy of that state.

Familiar **selection policy is target-local** because the useful role changes between
Combat and non-combat targets:

- Casual exposes `Use best available` plus a source-role dropdown, including combat,
  skill-support, beast-of-burden, healing, foraging, teleport, and any additional roles
  established by the full catalog audit.
- Advanced pins an exact familiar and exposes its exact familiar inventory when it has
  one.
- `Best available` resolves from owned, level-valid, usable familiars in the chosen role;
  its final ordering must come from the harvested catalog rather than display-name rules.
- Automation may summon into an empty global slot but never silently dismiss or replace
  a live familiar when the target changes. A mismatched live familiar remains active and
  the target surface shows the queued policy with an explicit switch command.

Choosing a BoB policy is the Casual opt-in to its storage. While a compatible BoB is
active, Casual automatically packs its separate restricted inventory according to the
same target preset that packs the player's carried inventory. Gathering/loot may use it
as compatible overflow; processing may allocate compatible inputs to it. Advanced shows
the extra slots and lets the player arrange them directly. Both inventories share the
existing Casual/Advanced packing mode rather than creating independent mode toggles that
could contradict each other. Switching targets alone never repacks, empties, dismisses,
or drops a live familiar's cargo.

### 7. Casual Summoning-point upkeep — settled 2026-07-16

When a Casual familiar policy needs more Summoning points to summon or to perform a
configured point-gated ability, it automatically spends the **next successful answer**
on an abstracted obelisk restoration. That answer restores points instead of performing
the selected target action. Again cannot restore points because it is a decay-only idle
tick. This is an explicit foreground-action detour, not wall-clock travel or persistent
player location.

Advanced exposes a toggle for the same auto-restore behavior and retains a manual
Restore command. Exact restore values and the relationship between ordinary Summoning
points and special-move points remain source-harvest work; automation cannot silently
merge the two resources.

### 8. Casual scroll-special automation — settled 2026-07-16

Casual ships with one global **auto-special toggle**, on by default. Auto-special:

- may fire only on a successful answer, never on Again;
- consumes only a matching scroll deliberately present in the current target-carried
  inventory, never a Bank stack, plus the sourced special-move-point cost;
- uses role-shaped, source-backed trigger conditions so healing is not wasted as
  overheal, combat specials require an active encounter, and gathering/boost specials
  require an applicable current target or missing effect; and
- never replaces the manual Special command on the canonical familiar panel.

The carried-scroll boundary makes target packing the explicit depletion budget and
prevents Casual from silently draining the Bank. Advanced may configure exact behavior
from the same live familiar state, but cannot bypass sourced target, cooldown, point, or
item gates. Trigger classifications come from the harvested familiar/scroll catalog,
not display-name heuristics.

### 9. Passive familiar output on Again — settled 2026-07-16

Again means **no user foreground input**, not a world with no benefits. Genuinely passive,
duration-cadenced familiar effects continue on every answered-card world tick, including
Again. A forager may therefore produce an item and a passive healer may heal while the
player is AFK; the same tick still spends familiar lifetime and applies ordinary world
decay. Review undo restores the whole tick atomically.

Effect classification follows semantics rather than whether the result is positive:

- **Passive periodic effects** advance and may resolve on every answered-card world tick.
- **Continuous conditions** such as invisible skill boosts or light remain present while
  the familiar is active and are consulted whenever a later gate or action needs them.
- **Foreground- or encounter-dependent effects** require the corresponding successful
  action. Familiar attacks do not occur on Again because the settled encounter rule says
  neither side attacks when the player clicks away; auto-renew, obelisk restore, and
  auto-special also retain their successful-answer gates because they are commands.

The harvested catalog must classify each effect explicitly. Implementation must not infer
passivity from a familiar or scroll display name.

### 10. Familiar combat exposure — open

Period evidence already requires a healable familiar and a familiar-death path; those
states are source-shaped rather than optional. The unresolved AnkiScape choice is how an
attacking familiar becomes exposed to enemy damage inside the one-review Combat loop.

Choose whether participation makes the familiar a real second damage target under a
sourced or bounded fallback targeting rule, or whether ordinary enemy damage always
stays on the player unless a specific sourced attack names the familiar. The mapping must
also define how familiar death ends the summon, interacts with the ongoing encounter,
and routes any BoB inventory into the already-settled five-source-minute cargo reclaim
state.

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
