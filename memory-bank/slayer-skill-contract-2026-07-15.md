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

The picker always shows every runtime-certified cutoff-live standard
Slayer-master role. Ineligible masters remain visible but disabled, with every
unmet combat, Slayer, quest, or activity requirement stated directly on the row.
A locked row cannot be confirmed and does not participate in assignment or
challenge rolls. An uncertified role is implementation debt and therefore absent
under Owner decisions 18 and 19, not displayed as another kind of player lock.

Eligible rows expose the master identity, requirements met, ordinary point
schedule, assignment-range summary, and challenge availability. The previous
eligible master remains preselected. Quest succession updates the identity and
portrait inside the existing role row; it never leaves the dead master visible
as another selectable master or creates a duplicate successor row.

## Owner decision 7 — succession is presentation-only

Crossing a While Guthix Sleeps succession boundary never cancels, rerolls,
rewrites, or otherwise mutates an active assignment or challenge. Remaining
objectives, qualifying targets, task count, point/streak treatment, rewards, and
undo history remain exactly as they were.

The task stores the stable functional master role. Quest state derives the
current NPC name, portrait, and source-appropriate copy for that role, so Turael
becomes Spria and Duradel becomes Lapalok without a second gameplay identity.
Undoing the quest-state transition changes those presentation fields back and
still leaves the task untouched.

## Owner direction 8 — finishing requirements and Slayer upgrades are real

Required Slayer finishing mechanics must exist; targets may not be admitted as
ordinary Combat enemies that die when their LP reaches zero. The complete
cutoff-live Slayer reward and unlock catalog is likewise mandatory design scope,
not optional polish.

The cutoff finishing-blow reward supplies the reconciliation. For 400 Slayer
points, `Ability to deliver killing blows quicker` makes rockslugs, desert
lizards, zygomites, and gargoyles die normally at zero LP as long as the
required item remains in the player's active inventory. The unlock automates
the finisher; it does not waive the bag of salt, ice cooler, fungicide spray, or
rock hammer requirement. It supports ranged and magic kills and does not apply
to Chaeldar's experimental-fungicide challenge. See
`source-audits/slayer-finishing-blows-2026-07-15.md`.

Without the unlock, reaching the source finisher range creates a pending manual
finisher state. Consumable finishers spend their item or charge; reusable tools
must be present but remain owned. No kill, drops, Slayer XP, or assignment credit
commits until the finisher succeeds.

## Owner decision 9 — manual finishers consume a review

Before the 400-point unlock, using the required finisher is its own Combat
action and consumes the next correct review. That review atomically spends the
consumable item or charge where applicable, completes the kill, awards drops and
XP, decrements the assignment, and writes one undo record. An incorrect review
does none of those things.

After the unlock, a qualifying final damaging review applies the required
finisher and completes the same effects in one atomic transaction. The item
presence check and consumable spend still occur.

## Cutoff exclusion — unlimited Slayer shakers

Salt, ice, fungicide, and explosive shakers are excluded. All four unlimited
items released on `2015-06-08`, after the cutoff. Period AnkiScape therefore
uses bags of salt, ice coolers, fungicide charges, and fishing explosives as
consumables; the rock hammer remains the reusable finishing tool. See
`source-audits/slayer-finishing-blows-2026-07-15.md`.

## Owner decision 10 — no early-use item trap

The manual finisher action is disabled until the target reaches its valid
source LP threshold. AnkiScape does not encode the period ability to spend a bag
of salt, ice cooler, or fungicide charge too early for no effect. This is an
explicit UI-safety abstraction: it removes only an avoidable misclick trap and
does not remove the required item, extra review, consumable spend, or value of
the 400-point automatic-finisher unlock.

## Cutoff Slayer-point reward surface

The primary cutoff reward table is pinned in
`source-audits/slayer-points-rewards-2026-07-15.md`. It includes ordinary and
milestone task points, challenge bonuses, repeatable item/XP purchases,
permanent crafting and assignment unlocks, the quick-finisher reward, skip and
block operations, and multiplayer-only co-op rewards. Social Slayer and its
co-op purchases remain parked under Owner decision 4; the complete solo catalog
remains mandatory.

## Owner decision 11 — ring charges erase Slayer trip cost

The ring of slaying preserves its eight-charge transport value without adding a
map, location, travel review, or wall-clock delay. When the player starts Combat
at a qualifying Slayer destination, they may spend one charge to remove that
trip's abstract run-energy cost. Assignment acquisition remains instantaneous
and free; it never consumes a charge.

The charge is spent by the destination-entry operation, not by selecting a
monster, inspecting the current assignment, or resuming an encounter already in
progress. The period task-check action may remain as harmless item flavor, but
it grants no exclusive information because the active assignment is already
legible in Slayer and Combat UI. At zero charges the item becomes the period
uncharged ring and provides neither free entry nor an invented alternate effect.

This is a labeled mapless transport abstraction. It keeps the sourced finite
charge economy and the permanent ring-crafting unlock meaningful while routing
the benefit through AnkiScape's existing run-energy resource rather than a
forbidden time or location simulation.

## Owner decision 12 — source-first challenge-offer fallback

Implementation must make one focused attempt to recover a cutoff-era Slayer
master challenge prerequisite and offer probability from period implementation,
talk history, cache evidence, or an independent dated source. Any qualifying
period value supersedes the fallback below.

If that pass remains `source_blocked`, use this labeled abstraction:

- complete five consecutive assignments for the same functional master role;
- on each later assignment request from that role, roll a 10% challenge-offer
  chance;
- producing an offer resets that role's challenge counter whether the player
  accepts it or takes a normal assignment; and
- changing masters breaks the master-specific challenge sequence but does not
  alter the separate qualifying-task streak used for Slayer points.

The roll occurs only during the instantaneous `Get assignment` transaction. It
has no wall-clock cooldown, pity timer, daily limit, or hidden travel action.

## Owner decision 13 — one-trip challenges use explicit run sessions

Turael/Spria's one-basement-visit challenge and Duradel/Lapalok's one-Slayer-
Tower-trip challenge use explicit challenge-run sessions rather than global
player location. Starting the first qualifying objective begins the run and its
compound ledger persists across reviews, study sessions, Anki restarts, and
switches among targets required by that challenge.

The run resets only when the player deliberately abandons it, switches to
unrelated Combat, or dies. Pausing study, closing Anki, changing among required
challenge monsters, inspecting another UI page, banking, or changing equipment
does not count as leaving. Resetting the run clears its challenge-objective
ledger but leaves the accepted challenge active so the player may begin again.

This preserves the sourced one-visit constraint through explicit player and
Combat state transitions. It adds no wall-clock expiry, fake walking action, or
persistent map coordinate. Ordinary Slayer assignments are unaffected and keep
their already-settled cross-session progress.

## Owner decision 14 — mechanically distinct areas are Combat contexts

Slayer areas become explicit target-local Combat contexts only when the source
location changes access, enemy membership, equipment effects, risk, drops, or
another gameplay rule. Purely cosmetic duplicate locations collapse into the
same target entry and do not create map clutter.

The player chooses a qualifying context alongside the exact enemy variant.
Implemented contexts that the current player cannot yet enter remain visible
where progression legibility helps and state their unmet assignment, master,
Slayer, Combat, quest, activity, or item gates. A context whose own runtime
dependencies are not implemented does not materialize as a disabled row.
Selecting a context does not create global player location: it binds the source
rules and abstract trip-energy cost to that Combat encounter until retreat,
death, target/context change, or another established Combat reset boundary.

Kuradal's Dungeon is the flagship case and must retain its task/access and
ferocious-ring rules through this seam. Ring-of-slaying destinations also land
on qualifying contexts, letting one charge erase the selected context's trip
cost under Owner decision 11. Context selection itself is instantaneous and
review-free; only source gameplay actions consume reviews.

## Period closure — Kuradal context and ferocious ring

The November 2012 revisions pinned in
`source-audits/slayer-location-contexts-2026-07-15.md` establish Kuradal's
task-only dungeon access, its eight-monster roster, 75 Slayer/110 Combat gate,
cannon prohibition, and the complete visible ferocious-ring behavior.

The period ring has five teleports, adds a fixed 40 life points after every
successful hit in Kuradal's Dungeon, and acts as a ring of life there: dropping
below 10% LP while still above zero retreats safely and destroys the worn ring
regardless of charges. A lethal hit still kills. The fifth teleport consumes the
ring entirely. Do not substitute the modern `4% damage` summary for the pinned
fixed-40 rule.

Each teleport charge erases the abstract Kuradal-context trip cost. The reactive
emergency escape consumes no review; it atomically destroys the ring, ends the
encounter, avoids grave processing, and participates in Combat review undo.
Combining partially charged rings is a review-free inventory operation with its
own manual undo record.

## Owner decision 15 — one integrated Slayer management page

Slayer management stays inside the existing AnkiScape Skills surface and does
not open nested dialogs or independent windows. The page has three persistent
subviews:

1. `Assignment` is the default. It shows the current assignment or challenge,
   remaining objectives, functional master and current portrait, point streak,
   relevant context/item blockers, management operations, and recent progress.
2. `Masters` contains the progression-visible picker settled in Owner decision
   6. `Get assignment` changes to this subview, preserves the last eligible
   selection, and performs the review-free assignment transaction in place.
3. `Rewards` shows the point balance, repeatable purchases, permanent unlocks,
   skips, block slots, and blocked-assignment management. Assignment actions may
   deep-link to the relevant operation here without opening another window.

Every long list uses the shared modular search/filter component; local Slayer UI
must not create another bespoke search box. Search never changes persisted
selection or active task state. Empty states and locked rows explain why an
operation or result is unavailable.

Slayer does not duplicate the combat target picker. `Open in Combat` switches
the existing AnkiScape surface to Combat with `Current Slayer task only`
enabled, while leaving the exact target and context for the player to choose.
Combat remains the only fight interface and no deep-link starts an encounter.

## Owner decision 16 — Slayer owns a reachable Smoking Kills chain

The Slayer implementation scope includes a complete playable `Smoking Kills`
quest and every prerequisite quest definition that is still only generated or
otherwise incomplete. This work remains part of the canonical missing-quest
program; Slayer merely raises the chain's priority because it gates core Slayer
progression. It does not create a separate competing quest architecture.

The implementation must replace generated `Complete Smoking Kills stage N`
placeholders with source-backed stages, item transformations, encounters,
journal text, rewards, unlocks, undo behavior, and prerequisite enforcement.
Every still-missing prerequisite receives the same real playable-definition bar
rather than a completion flag or bypass.

Before quest completion:

- ordinary eligible masters, assignments, task progress, and Slayer XP remain
  playable;
- once Sumona's role is runtime-certified, her row remains visible and disabled
  with `Complete Smoking Kills` among its unmet requirements;
- the `Rewards` subview remains visible and lists the period reward catalog, but
  all point balances, purchases, skips, blocks, and permanent unlocks are locked
  behind an explicit `Complete Smoking Kills` callout; and
- no pre-quest task retroactively grants points when the quest completes.

Quest completion activates the authentic point/streak and reward systems. The
exact initialization boundary for the first-four-task counter must be reconciled
against period implementation during the quest/Slayer source pass; it may not be
silently inferred from the existing generated catalog.

## Owner decision 17 — Slayer owns the complete helmet route

The Slayer implementation must make both Duradel and the Slayer helmet reachable
end to end. It therefore owns a real playable `Shilo Village` definition and the
complete period route through `Pirate's Treasure`, `Rum Deal`, `Cabin Fever`,
Mos Le'Harmless, Cave horrors, and the black-mask drop. This is a transitive
reachability rule rather than a closed hand-written list: every authentic quest,
skill, item, encounter, and area prerequisite found beneath either route is in
scope unless it is already genuinely playable.

The pinned 2012 `Template:Questreq` revision `6552449` resolves prerequisites
lost by the generated catalog. At the cutoff, `Cabin Fever` required `Pirate's
Treasure` and `Rum Deal`; `Rum Deal` transitively required `Priest in Peril` and
`Zogre Flesh Eaters`; and that route included `Druidic Ritual`, `Big Chompy Bird
Hunting`, and `Jungle Potion`. Implementers must reconcile the complete tree from
period sources rather than copying `quest_catalog_generated.py`'s empty
`Rum Deal.required_quests` tuple.

The route is also cross-skill gated. The pinned Shilo Village and Cabin Fever
rows require 32 and 42 Agility respectively, while Agility remains planned in
the live registry. Slayer may not bypass, waive, or replace those requirements;
the route becomes usable only after the real Agility implementation can satisfy
them.

The endpoint is the crafted helmet, not merely possession of a black mask. The
player must also satisfy the period 55 Crafting requirement, complete Smoking
Kills, activate the point economy, and buy the 400-point `Craft Slayer helmets`
unlock. Cave horrors and the Mos Le'Harmless cave must arrive as real Combat
target/context and acquisition content, including the sourced protective-item,
light, access, drop, and undo rules. No free mask, quest flag, inert reward row,
or alternate acquisition shortcut is acceptable.

## Owner decision 18 — implementation gaps stay implicit

The source and completeness ledgers retain every cutoff-live assignment family,
but live Slayer surfaces and assignment rolls contain only runtime-ready
families. A family gated by an unimplemented quest, target, Combat context,
acquisition route, or other required subsystem is absent rather than rendered
as a disabled, locked, placeholder, or `coming later` row. The player must never
be asked to look at implementation debt.

Runtime readiness and player eligibility are separate predicates. First derive
whether the complete dependency graph behind a period task row is genuinely
implemented. Only then apply the authentic master, quest-completion, Slayer,
Combat, reward-unlock, block-list, and last-task eligibility rules. Rows failing
either stage do not enter the weighted roll or its normalization denominator.
This preserves the period behavior of reweighting among tasks the player can
actually receive without inventing replacement weights.

Automatic activation is part of the data contract. Assignment definitions must
reference stable quest, target, context, and unlock identities rather than copy
implementation flags into a second hand-maintained allowlist. Once all required
identities become runtime-ready, the existing family participates in UI/search
and assignment generation automatically; no save migration, row cleanup,
special release switch, or follow-up patch is allowed.

Pin each family's master weights, kill-count range, Slayer gate, and other period
data now, using `source_blocked` where the exact value cannot yet be closed.
Activation may not require filling in a second batch of family data. An audit
must enumerate every cutoff family as either runtime-ready or blocked by named,
machine-checkable stable dependency identities, reject unknown blockers, and
prove that every rollable master has a non-empty eligible pool. This tooling is
the developer-facing signal that replaces dead player-facing rows.

The same readiness predicate hides a family-specific reward purchase whose
effect cannot yet operate, including assignment unlocks such as aquanites or ice
strykewyrms. Such rows appear automatically when their dependent family is
runtime-ready. Activation changes future searches, purchases, and assignment
rolls only; it never mutates an active task, streak, points, or block list
retroactively.

This decision does not reopen the owner's explicit progression-visible surfaces.
Implemented Slayer masters remain visible when the player personally lacks
their requirements under Owner decision 6, and the implemented Rewards surface
retains its Smoking Kills progression lock under Owner decision 16. The hidden
rule applies to missing product implementation, not to every authentic player
progression gate.

## Owner decision 19 — no partial baseline master pools

A Slayer master becomes runtime-ready only when its complete ordinarily
available cutoff pool is implemented. Every baseline family must have its stable
identity and qualifying variants, per-master weight, kill-count range, Slayer
and Combat gates, target/context behavior, and required acquisition mechanics.
A missing family or unresolved implementation dependency keeps the entire
master out of live assignment generation; the runtime may not silently roll and
renormalize over a partial baseline pool.

Authentic player-dependent exclusions are not baseline omissions. Quest-gated,
reward-unlocked, blocked, previous-task, and other period eligibility rules are
applied after the master passes baseline certification. Those families enter or
leave a particular player's eligible weighted subset normally without making
the master implementation-incomplete. Each baseline/player-gated classification
must itself carry period evidence in the completeness ledger; an unclassified
family fails closed as baseline rather than gaining an exemption by omission.

Player-gated families still require their cutoff pool data to be pinned now and
remain subject to Owner decision 18's readiness audit. If a player satisfies an
authentic gate before its dependent family is implemented, that family remains
absent and the audit continues to name the gap; no no-op unlock or dead row is
exposed. The no-gap-renormalization certification guarantee applies to the
ordinary baseline pool, while authentic player eligibility continues to
reweight the receivable subset.

An exact historical value that remains `source_blocked` after the required final
source pass must receive the smallest explicit, labeled abstraction authorized
by the verification standard before its family can certify. `source_blocked`
may preserve an open research finding in the contract, but it cannot become a
missing row, zero weight, or silent reason to ship a distorted pool.

The completeness audit from Owner decision 18 certifies this boundary per
master. It must distinguish baseline implementation blockers from authentic
player eligibility, prove every baseline family has complete roll data and the
owner-set qualifying-variant coverage, and reject any master that would otherwise
roll a partial or empty baseline pool. A master absent for this reason creates no
implementation-debt row; after certification, its ordinary visible
player-progression locks follow Owner decision 6 automatically.

Optional special challenges sit outside the ordinary weighted pool and do not
block baseline certification. Their offer predicate uses the same derived
runtime-readiness rule: a master can roll ordinary tasks while an unimplemented
challenge offer remains absent, and that offer activates automatically once its
complete compound objective is ready.

## Owner decision 20 — certify families with an ordinary variant floor

A baseline assignment family satisfies the qualifying-variant portion of master
certification when its family roll data is complete and at least one fully
functional, ordinarily available qualifying variant has an end-to-end Combat
path. The certifying variant may not depend on a quest, reward purchase, special
context, or other player gate that would leave the baseline family unavailable
to an otherwise eligible player.

If the period family has no ordinarily available variant, it is classified as a
player-gated family under Owner decision 19 rather than forced through the
baseline exception. Its authentic gated variant may certify the family only once
the complete quest, reward, context, item, and acquisition chain is implemented;
the design does not invent an ungated substitute merely to satisfy this floor.

`Fully functional` includes the family's distinctive kill loop. A certifying
variant must exercise any required finisher, protective equipment consequence,
special damage rule, context rule, drop/acquisition dependency, and atomic undo
branch established by the source. A generic enemy that merely reaches zero LP
cannot certify a family whose real loop requires more.

This floor does not shrink the cutoff family definition. Every qualifying
variant and its stable family membership must be pinned in the completeness
ledger now. Unimplemented variants remain named developer-audit blockers, stay
absent from live search and selection, and enter automatically when their target,
context, acquisition, and special-mechanic dependencies become runtime-ready.
Adding a variant changes neither the active assignment nor its remaining count;
it only expands the exact targets eligible for future Slayer credit.
No temporary weight, kill-count, Slayer-XP, or other compensation is applied
because the currently implemented variants happen to be weaker or stronger.

If the implemented breadth makes a flat Combat target list unwieldy, the existing
picker may render an expandable family-to-variant hierarchy. The family row is a
non-target grouping label; only an exact child variant can be selected and
persisted. Shared search matches family and variant metadata, reveals matching
children even when their family was collapsed, and composes with `Current Slayer
task only`. Expansion state is presentation-only and cannot change the persisted
target, family, or assignment. A small family may remain flat. No fixed size
threshold is invented: use the hierarchy only when it materially improves
scanning.

This is nesting inside one list surface, not a nested window, menu, or second
fight interface. Combat remains the sole encounter surface and the Slayer page's
`Open in Combat` behavior remains unchanged.
