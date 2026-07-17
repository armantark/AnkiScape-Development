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

Again is a **world-only idle tick**. It is equivalent to briefly clicking outside the
mob area: elapsed state and genuinely passive effects continue, but an already-engaged
enemy, the player, and command automation receive no foreground action. Existing generic
safe-recovery helpers do not fire merely because a card was answered; a source-classified
passive heal may. See
`simulation-time-boundary-2026-07-16.md`.

### 3. Familiar renewal policy — source/app-pattern resolved 2026-07-16

Period renewal was a deliberate button available only at 2:30 or less, consumed one
unnoted pouch of the same familiar, reset the timer, and healed the familiar. AnkiScape
ships that manual Renew command exactly, translated through the short-duration card
mapping and the direct-command undo path.

Automatic renewal is part of an **enabled target familiar policy**, not a second global
toggle. Auto-renew:

- may fire only on a successful answer, never on Again, because renewal is positive
  recovery rather than decay;
- consumes only an unnoted matching pouch in the current target-carried inventory,
  never a Bank stack;
- fires at the first eligible answer inside the period renewal window;
- performs the same timer reset and familiar heal as the manual command;
- preserves the live familiar and its cargo rather than waiting for expiry; and
- stops when the current target's familiar policy is disabled or its carried pouch
  budget is empty.

The carried-pouch requirement bounds depletion and gives target loadouts natural
control. Casual reserves matching pouches through its target preset; Advanced may place
the exact number of pouches it wants in the carried grid, including several renewals or
replacements without a bank run. Manual Renew remains available whenever its source
gates are met, even if target automation is disabled.

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
familiar, remaining lifetime, Summoning points, Summon/Dismiss/Renew commands, special
configuration/status,
the active policy/lapse reason, and the separate BoB inventory. Contextual projections
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
- Automation may summon into an empty global slot, but target navigation alone never
  dismisses or replaces a live familiar. A mismatch remains active with the new policy
  visibly queued until an explicit switch or the settled safe Bank-boundary swap.

Choosing a BoB policy is the Casual opt-in to its storage. While a compatible BoB is
active, Casual automatically packs its separate restricted inventory according to the
same target preset that packs the player's carried inventory. Gathering/loot may use it
as compatible overflow; processing may allocate compatible inputs to it. Advanced shows
the extra slots and lets the player arrange them directly. Both inventories share the
existing Casual/Advanced packing mode rather than creating independent mode toggles that
could contradict each other. Switching targets alone never repacks, empties, dismisses,
or drops a live familiar's cargo.

### 7. Unified altar + obelisk upkeep — settled 2026-07-16

When a Casual familiar policy needs more Summoning points to summon or to perform a
configured point-gated ability, it automatically spends the **next successful answer**
on an abstracted restore stop. The reviewer line reads **`Visiting altar+obelisk`** and
fully restores both ordinary Prayer points and ordinary Summoning points. That answer
restores the two pools instead of performing the selected target action. Again cannot
restore points because it has no foreground command. This is an explicit foreground-
action detour, not wall-clock travel or persistent player location.

The same rule extends Prayer's existing combat Bank-run abstraction: every completed
Bank run already includes a free altar stop, so once Summoning exists that same stop also
visits an obelisk and restores Summoning points without another review. If Prayer and
Summoning both need restoration, their requests coalesce into this one atomic action;
they never queue two travel lines. This does not merge the resources, change potion
behavior, or restore special-move points unless the source harvest separately proves
that the chosen restore surface should do so.

Advanced exposes a toggle for the same auto-restore behavior and retains a manual
Restore command. Exact potion-restore values and special-move-point recovery remain
source-harvest work; automation cannot silently merge the resources.

### 8. Casual scroll-special automation — settled 2026-07-16

Casual ships with one global **auto-special toggle**, on by default. Auto-special:

- may fire only on a successful answer, never on Again;
- consumes only a matching scroll deliberately present in the current target-carried
  inventory, never a Bank stack, plus the sourced special-move-point cost;
- uses role-shaped, source-backed trigger conditions so healing is not wasted as
  overheal, combat specials require an active encounter, and gathering/boost specials
  require an applicable current target or missing effect; and
- awards the row's exact scroll-use XP because the successful review is the collapsed
  foreground special-use action, even though the UI resolves it automatically.

The carried-scroll boundary makes target packing the explicit depletion budget and
prevents Casual from silently draining the Bank. Advanced may configure exact behavior
from the same live familiar state, but cannot bypass sourced target, cooldown, point, or
item gates. Trigger classifications come from the harvested familiar/scroll catalog,
not display-name heuristics. Advanced changes configuration precision, not whether the
player must click a separate Special action: all eligible specials resolve through
successful reviews. No direct UI command can execute a special or award XP outside the
review transaction.

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

### 10. Familiar combat exposure — settled 2026-07-16

Period evidence requires a healable familiar and a familiar-death path, but **attacking
does not automatically make the familiar a second enemy target**. Ordinary enemy damage
stays on the player unless a pinned period source proves a channel that can damage the
familiar, such as a specific retaliation rule, area effect, enemy mechanic, or explicit
aggro/tanking familiar ability.

Source silence means zero familiar damage. There is no generic fallback targeting roll
invented merely to make familiar LP or renewal healing more visible. The catalog audit
must determine whether any period scroll or ability actually redirects aggression; the
owner's tank-scroll recollection is a research lead, not evidence. If such an ability is
proved, it joins the settled role-aware auto-special system in Casual and exact behavior
in Advanced.

When a sourced channel kills the familiar, the summon ends without ending the player's
encounter or refunding the pouch. Any BoB inventory moves atomically into the settled
five-source-minute cargo reclaim state.

### 11. Replacement after death or expiry — settled 2026-07-16

An enabled target familiar policy means **maintain this familiar role**, including
automatic replacement after death or expiry. On the first eligible successful answer
after the slot becomes empty, automation atomically consumes one compatible pouch from
the current target-carried inventory and the sourced Summoning-point cost, then summons
the policy's Casual best-available or exact Advanced familiar. It may occur during an
encounter. Again never summons because it carries no positive command.

The preconditions are all-or-nothing. If the pouch or points are missing, neither is
partially consumed and the policy remains enabled but **lapsed**. Casual's settled
point-restore detour may restore insufficient points before the summon transaction is
re-evaluated. Returning resources re-arms the policy automatically; the user never has
to toggle it off and on again.

Advanced users may deliberately devote several carried-grid slots to matching pouches
and therefore renew or replace repeatedly without a bank run. Automation never consumes
a pouch directly from Bank. The familiar surface persistently and quietly shows any
lapse reason, such as `Out of carried pouches` or `Summoning points too low`, rather than
using a transient popup.

### 12. Bank-run behavior after pouch depletion — settled 2026-07-16

When an enabled familiar policy needs a replacement but its carried-pouch budget is
empty, it may spend the **next successful answer** on a one-review bank-run detour if
Bank owns a compatible pouch. The detour refills the target preset, obtains the pouch,
and summons the policy's familiar when all point and pouch preconditions hold; it does
not also perform the selected target action. Again cannot trigger a bank run.

If Bank has no compatible pouch, the policy remains visibly lapsed. If points are also
insufficient, the bank detour never burns the newly obtained pouch: the settled point-
restore detour resolves the remaining precondition before the summon transaction is
re-evaluated. Every detour and summon remains atomic with review undo.

This applies to Casual and Advanced when their familiar policy is enabled. Advanced can
avoid the detour frequency by reserving several exact pouch slots; those pouches are
consumed before any Bank access.

### 13. Safe familiar swap after a target change — settled 2026-07-16

Target switching alone never dismisses a live mismatched familiar. At the next Bank
boundary, however, the target policy may atomically replace it when success is guaranteed:
deposit any BoB cargo first, verify the desired replacement pouch and Summoning-point
preconditions, dismiss the old familiar, then summon the replacement. The operation never
creates a cargo-reclaim event because the cargo was safely deposited before dismissal.

If any replacement precondition fails, the old familiar remains active and the new target
policy stays visibly queued; automation does not destroy useful remaining duration merely
to enter a lapsed state. The explicit manual switch command remains available. A completed
safe swap is undoable as one review transaction together with its Bank boundary.

### 14. Casual fallback when the best familiar runs out — settled 2026-07-16

Casual selects `Use best available` within a source-backed role, while Advanced pins an
exact familiar. Whenever Casual needs a replacement, it resolves the strongest owned,
level-valid, currently usable familiar in the configured role. If the former best pouch
type is exhausted, it automatically falls back to the next candidate in that same role
instead of lapsing. It never crosses roles or substitutes a pouch that the catalog has
not classified as compatible with the target's policy.

Resolution uses carried pouches first and then the settled one-review Bank detour. If no
valid in-stock familiar remains in the role, the policy stays visibly lapsed. Advanced
never falls back from its exact familiar. This mode distinction is deliberate: Casual
maintains the requested role, while Advanced preserves exact identity.

### 15. Upgrading a live Casual fallback after restocking — settled 2026-07-16

If Casual is currently using a weaker same-role fallback and a stronger pouch later
becomes available, the live familiar keeps its remaining duration. Pouch-stock changes
alone never dismiss or replace it. `Best available` is re-resolved when the familiar
otherwise needs renewal or replacement after expiry or death, or when the user issues an
explicit manual switch.

This avoids consuming two pouches for overlapping familiar time and prevents ordinary
Bank restocking from causing hidden churn. The weaker fallback may remain visible for at
most its remaining sourced lifetime; the manual switch is the deliberate escape hatch
when an immediate upgrade is worth discarding that value.

### 16. Beast-of-Burden supplies during a multi-review fight — source/app-pattern resolved 2026-07-16

Period evidence says a BoB inventory could not be accessed in combat and instructed the
player to find safety before withdrawing (`Beasts of Burden`, oldid 6288415, lines
101-105 of the literal wikitext). A command boundary between consecutive successful
combat-review bursts is not itself safe: while the same enemy remains engaged, neither
Casual nor Advanced may transfer items between the player and familiar inventories.

The settled answer-time model supplies the missing safe boundary. Again represents
clicking outside the mob area and performs no foreground action. It does not withdraw
items itself, but leaves the encounter disengaged; before the next successful answer
re-engages, Casual may use its target preset to top up the player's pack from the BoB.
Enemy death, explicit retreat, and pre-encounter setup are also safe boundaries. Advanced
may use the same legal boundaries through its explicit familiar inventory controls.

Transfers never occur inside the simulated combat burst, never exceed the player's free
carried slots, and never bypass the familiar's sourced item restrictions. This makes the
BoB genuine expanded inventory without pretending that every card boundary ends combat.

### 17. Meaning of target familiar policy `Off` — settled 2026-07-16

The target option is labeled **`Off — no familiar automation`**. It never summons,
renews, replaces, or triggers specials for that target, but it does not dismiss an
already-live global familiar. The familiar keeps its paid remaining duration until it
expires or the user explicitly dismisses it; any source-applicable passive or continuous
effect remains part of that live global entity.

The target surface makes the distinction explicit: `Familiar active — not managed by
this target`, with the ordinary manual Dismiss command available from the canonical
familiar panel. This prevents navigation order from destroying a pouch while still
making `Off` a strict promise that the target will spend no additional familiar resources.

### 18. Familiarisation session shape — owner-delegated and settled 2026-07-16

Pinned period evidence in `source-audits/summoning-familiarisation-2026-07-16.md` fixes
the once-weekly spirit-plane fiction, 60-shard/focus/20-minute stop conditions, and the
choice between a shard-scaled ingredient box or shard-scaled triple eligible charm drops.
The owner delegated the unfamiliar D&D's AnkiScape shape rather than reconstructing it
from memory. It becomes a compact **four-answered-card session**, not a one-review roll.

The run starts with three abstract focus pips and zero shards. Each successful answer
gathers 15 shards; Hard, Good, and Easy are deliberately equivalent. Again consumes the
segment, gathers nothing, and removes one focus pip as hunter pressure. The run ends at
60 shards, zero focus, or four segments. These integers are labeled balance abstractions,
not claims about period shard density or hunter hit rates.

At the end, the player immediately chooses the source reward: a shard-scaled ingredient
box or shard-scaled triple eligible charm drops. The reward command costs no review.
Cooldown begins at activity entry and ends 1,680 answered-card world ticks later, matching
the source's rolling week through the simulation clock. A partially completed run persists
across Anki closure and never resolves from wall time. Every segment, completion, reward,
cooldown, and undo transition is atomic and duplicate-safe.

### 19. Familiar-forbidden targets and areas — confirmed dismissal settled 2026-07-16

The earlier `park outside` recommendation was wrong as a universal rule. Pinned period
evidence distinguishes genuinely forbidden areas, which normally blocked entry until the
familiar was gone, from the Grand Exchange, Oo'glog spas, and Varrock Museum, where it
explicitly returned to the spirit plane and later came back. Darkan independently preserves
the blocking shape for the Fight Caves, Pest Control landers, and canoe travel. The future
target/route catalog therefore carries an explicit source consequence instead of one global
`forbidden` boolean: `block_until_dismissed`, `auto_dismiss`, `summon_only_forbidden`, or
`spirit_plane_hide`.

Target selection alone still never spends the familiar. A target with
`block_until_dismissed` may be inspected, but starting its training while a familiar is
live opens the shared **Dismiss familiar?** confirmation before the target becomes active.
Cancel preserves the familiar and current training unchanged. Confirm atomically dismisses
the familiar, discards its remaining duration, and permits target activation without
spending a review. It never inserts a protective Bank detour or deposits cargo remotely.

The confirmation names the familiar, remaining lifetime, and permanent pouch loss. If a
BoB is carrying anything, it also states the occupied-slot/item count and that the cargo
will enter the already-settled temporary reclaim event rather than the Bank. General manual
Dismiss commands use the same dialog. Source-driven expiry and death do not ask for
confirmation, and `spirit_plane_hide` does not dismiss at all. Any period area that
automatically dismissed a familiar still receives this AnkiScape safety confirmation before
the destructive transition; preserving a warning is a UI safeguard, not a claim that the
period game always offered one.

### 20. Manual dismissal versus enabled automation — settled 2026-07-16

Outside a familiar-forbidden target, confirming Dismiss can conflict with an enabled target
policy. Confirming a general manual Dismiss therefore turns that target's familiar policy
Off by default; otherwise the next successful answer would consume another pouch and
silently reverse the explicit decision.

The shared dialog includes one unchecked escape hatch: **Keep auto-summon for this target
(resummons next successful answer)**. Checking it preserves the policy and makes the next
replacement deliberate rather than surprising. Area-required dismissal never changes a
saved policy because the area—not a changed preference—caused it; the policy simply cannot
act while that target forbids familiars.

### 21. Scroll-use XP under collapsed automation — settled 2026-07-16

Period scroll rows award a small separate XP amount when the player manually activates a
scroll, but explicitly award none when enchanted headgear activates it automatically.
AnkiScape does not preserve a manual-click training lane: a successful review is the
foreground action, and Casual versus Advanced changes configuration precision rather than
whether the player clicks Special. Every eligible review-triggered special therefore
consumes its scroll and points and awards the row's exact use XP in both modes. Again never
fires a special or awards that XP.

The period enchanted-headgear exception remains reserved for any future effect that truly
fires passively outside a foreground successful-review action. Such passive auto-fire would
consume its sourced resources but award no scroll-use XP. This preserves the source
distinction without penalizing AnkiScape's universal action-collapse abstraction.

### 22. Ordinary Summoning training — source/app-pattern resolved 2026-07-16

`source-audits/summoning-training-2026-07-16.md` closes the normal training shape without
an owner question. The page exposes **Infuse pouches** and **Create scrolls** as searchable
action families. One successful review infuses one pouch from its exact empty-pouch, charm,
spirit-shard, and tertiary recipe for exact creation XP, or converts one pouch into ten
matching scrolls for the row's exact creation XP. Again advances world state and creates
nothing. Ordinary carried-pack and Bank-run rules own repeated trips; a later sourced
cadence/trip pass must not change the source unit or XP.

Wolf Whistle is an optional quest reward, not a skill gate. Familiarisation and quest or
activity XP remain supporting routes. Surface-world search and filters never expose the
separate Dungeoneering pouch/scroll tables; those wait for Dungeoneering's temporary-session
economy. The complete row and acquisition harvest remains required before implementation,
but the training interaction itself needs no further owner design.

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
