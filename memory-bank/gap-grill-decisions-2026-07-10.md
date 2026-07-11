# Gap-Fill Owner Grill Decisions — 2026-07-10

This log closes the owner-design items from `gap-backlog.json` in rank order.
It records AnkiScape translation decisions separately from source-dependent
numbers. A design can be settled while implementation waits for the November
2012 Darkan fidelity revamp to provide concrete mechanics and rates.

## Hunter: Tracking, Pitfall, and Rabbit Snaring

Backlog id: `hunter-tracking-pitfall-snare`  
Decision status: design settled; implementation waits for the Darkan revamp.

### Scope

- Implement full non-Jadinko pre-EOC parity: polar kebbit, common kebbit,
  Feldip weasel, desert devil, penguin, and razorbacked kebbit tracking; spined
  larupia, horned graahk, and sabretooth kyatt pitfall trapping; and rabbit
  snaring.
- Gate penguin tracking behind Hunt for Red Raktuber. Rabbit snares themselves
  do not require Eagles' Peak: the quest gates catching the ferret used to flush
  rabbits. Model the real ferret requirement and its quest-gated acquisition
  rather than attaching an invented direct quest lock to the snaring action.
  Selecting a Hunter target abstracts travel to its canonical area; do not add
  persistent location or a world-map system.
- Include Jim's penguin hand-in and bonus XP, the tracking- and pitfall-fur
  clothing services, tatty/perfect fur variants, source-authentic camouflage
  and pitfall-outfit Hunter effects, rabbit-foot necklace creation, and long
  kebbit bolt creation. These may land in separate commits or worktrees, but
  this parity item is not complete while those direct reward chains are inert.

### Review and Failure Model

- One successful Anki review triggers one complete rolled Hunter attempt.
  Tracking trails, trap construction, teasing/jumping, ferret retrieval,
  snaring, and capture stages execute internally rather than consuming
  separate reviews.
- Preserve source-authentic intermediate sub-rolls, resource/tool consequences,
  perfect/tatty reward distribution, bonus awards, and failure behavior. Do not
  collapse these to an invented deterministic catch or composite curve.
- Pitfall failures may damage the shared player lifepoints. Dangerous Hunter
  targets show player HP alongside Hunter XP, consume food from the actual
  carried pack, use the existing death/grave behavior, and remain fully
  compatible with Anki undo.

### Unified Carried Inventory Contract

- Every skill, combat enemy, or activity that needs inventory management uses
  the same 28-slot carried-inventory model. There is no Hunter-only or
  Combat-only parallel loadout system.
- Casual mode uses an adaptive packing policy comparable to required supplies,
  preferred food, potions, and free loot space. Each target remembers its own
  casual policy; a global default seeds a target only on first use.
- Advanced mode saves a literal 4x7 item layout per target. A named preset
  stores a literal layout and is applied from a dropdown as an independent
  copy. Editing the selected target after applying a preset does not mutate the
  preset. The only required preset controls are `Save as preset` and `Apply
  preset`; do not add a separate copy-from-target workflow.
- A copied advanced layout is never silently rewritten to satisfy a different
  target. Surface missing requirements and let the player edit that target's
  independent layout.

### Source Gate

The owner wants full parity, not wiki-estimated replacement numbers. The design
work is complete now, but implementation waits for the November 2012 Darkan
revamp wherever the current engine is a stub or missing: success curves,
intermediate roll order, damage, tool/resource loss, reward distributions, and
bonus values must be cited from the revamped implementation and reconciled with
the pinned pre-EOC guide evidence before shipping.

## Hunter: Herblore Habitat, Jadinkos, and Grenwall Herbs

Backlog id: `hunter-habitat-jadinko`

Decision status: Habitat and jadinkos parked as a Farming-expansion seed;
grenwall herb parity split into an implementation-ready Hunter item.

### Habitat Boundary

- Do not build a one-off Farming subset or an instant-seed shortcut merely to
  make Herblore Habitat available now. Introduce Habitat and jadinkos as part of
  the eventual full Farming skill expansion.
- Preserve Habitat as persistent configuration state: the active habitat
  feature, planted flower, bush, fruit tree, and juju effect together determine
  which jadinkos are attracted. Do not flatten this into an ordinary bank-input
  action.
- The player selects a jadinko first and may use `Configure habitat for this
  jadinko`. That assisted path chooses the correct setup but still consumes or
  respects the authentic seeds, plants, growth state, potion, and other costs;
  it is not a free bypass.
- Keep this section as a design seed rather than an implementation task until
  Farming expansion work begins and the ongoing Darkan Habitat implementation
  is ready to audit.

### Independent Grenwall Slice

- Grenwall herb drops do not depend on Farming or Habitat, so they remain an
  independent Hunter parity item instead of being parked.
- The pre-cutoff `Grenwall` revision 6196272 confirms 18-21 grenwall spikes,
  bones, and random grimy herbs broadly spanning irit through dwarf weed. The
  existing fixed 18-spike reward is therefore not full parity.
- Do **not** yet lock the local Darkan table's independent 15% high-herb and
  18% mid-herb rolls. That file entered Darkan in a 2022 commit and the same
  probabilities appear on the modern RS3 page, while the pinned September 2012
  article does not state them. Treat the table as a reconstruction lead until
  a literal pre-cutoff source, period cache/script, or Wayback capture
  corroborates the probabilities and exact herb membership.

## Runecrafting: Runespan and Training-Time Calibration

Backlog id: `rc-runespan`

Decision status: design settled; implementation waits for the Darkan fidelity
revamp and a source-backed training-rate audit.

### Runespan Session Model

- Model Runespan as a persistent, geographically abstracted session rather
  than a flat list of unrelated creature and node targets. Do not introduce a
  world map.
- A fresh session simulates the complete progression: collect essence, siphon
  creatures, reach useful nodes, siphon nodes, spend runes on traversal, and
  replenish essence as needed. The review HUD always labels the current
  activity and specific target or transition.
- One review resolves one source-defined action in the current loop, such as an
  essence collection, siphon attempt, traversal, or replenishment action. Exact
  rolls, depletion, XP, and point rates remain source-gated; do not translate
  the action into simulated minutes during the current implementation pass.
- Casual mode automatically chooses a sensible accessible floor and target and
  handles beneficial yellow-wizard, runesphere, and equivalent special
  opportunities when their authentic requirements are met.
- Advanced mode groups checkboxes by floor and target type. Checked entries are
  the allowed target and detour pool; the simulator chooses among them using
  the selected XP, points, or rune priorities. Never silently fall back to an
  unchecked target when the configured pool cannot currently proceed.

### Session Lifetime and Inventory

- Runespan temporarily takes over the unified 28-slot carried pack. Ordinary
  carried items are banked on entry, allowed equipment remains active, and
  temporary essence and runes occupy real pack slots and drive traversal and
  siphoning decisions.
- Switching to any other skill or Runecrafting target deliberately exits
  Runespan and discards all temporary session essence, runes, position, and
  progress. Returning starts from essence collection again; session materials
  can never leak into the bank.
- Closing and reopening Anki while Runespan remains selected resumes the saved
  session. Application lifecycle events are not deliberate activity switches.

### Altar-Run Counterpart

- Restore the intended high-effort/faster-altars versus low-effort/slower-
  Runespan tradeoff. Runespan needs no banked essence or repeated loadout and
  yields lower effective XP than an optimized altar route while also granting
  its source-authentic points and rewards.
- Repeatable altar crafting becomes an abstracted multi-review route cycle such
  as bank/load, outbound travel, craft, and return. Casual advances the route
  automatically; Advanced uses the altar target's saved unified-inventory
  layout and route configuration. This adds simulated banking and travel
  friction without a world map.

### Global Training-Rate Rule

- This is a design and evidence-collection seed only. Do not run the global
  time-to-99 balancing or choose its compression scale until every skill and
  major training family is implemented; the system is too incomplete and in
  flux for a meaningful comparison now.
- Preserve exact source mechanics and raw XP awards. Use archived 2012 training
  guides and reconstructed XP-per-hour ranges in the later balancing pass to
  calibrate action grouping, travel, banking, and depletion rather than
  rewriting XP or success rolls to force a desired result.
- Build a method-rate catalog by level band, equipment, and material assumption
  wherever historical evidence permits. Players retain complete freedom to use
  any available method, including inefficient ones.
- Use an efficient but ordinary player following a good 2012 guide as the
  canonical level-to-99 comparison. Preserve the real game's approximate
  relative training-time ratios between skills and methods, then apply a later
  global AnkiScape compression scale. Do not claim false precision or benchmark
  against tick-perfect play or intentionally slow AFK methods.

### Source Gate

The current Darkan Runespan implementation is incomplete and internally
inconsistent for parity work: node interaction and rune production paths are
disabled or stubbed, creature XP is commented out, and its inventory/exit
economy does not yet provide a trustworthy November 2012 contract. Implement
only after the fidelity revamp can be reconciled with pinned historical guides,
including the complete pre-EOC reward shop and equipment effects.

## Firemaking: Bonfires, Fire Spirits, and Cooking Heat Sources

Backlog id: `fm-bonfires`

Decision status: design settled; exact rates and batch timing wait for a pinned
2012 wiki snapshot and the Darkan fidelity revamp.

### Firemaking Training

- Preserve the interaction-density distinction provisionally: line fires remain
  one manually initiated log per review, while a dedicated bonfire-training
  review advances an automatic feeding batch. Do not finalize comparative
  XP-per-review or time-to-99 balance until all skills are implemented.
- Dedicated bonfire training joins an abstracted busy public bonfire and always
  receives the authentic five-or-more-participant bonus. Do not add crowd
  configuration or a multiplayer/world-map system.
- Training logs use the normal unified 28-slot carried inventory and simulated
  bank-run cycle. The feeding batch consumes carried logs, rolls source XP and
  failures per log, and remains fully undoable.
- Fire-spirit rewards are claimed automatically, deposited directly into the
  bank, and announced with a small non-blocking floaty popup. A spirit never
  consumes a review, interrupts the feeding batch, or occupies a carried slot.

### Warmth and Simulated Time

- After the source-authentic contribution requirement, bonfire warmth increases
  the shared maximum player lifepoints and remains useful in Combat and
  dangerous Hunter. Use the pinned 2012 percentage, log-dependent duration,
  stacking, refresh, death, and expiry rules.
- Combat currently advances 50 game ticks, approximately 30 seconds, per base
  review. Non-combat skills currently resolve actions only and do not advance a
  simulated minute clock. Represent skilling lifetimes and expiry through
  source-gated action counters, and leave their eventual XP-per-hour calibration
  to the parked global balancing pass rather than assuming seconds per review.

### Cooking Heat Sources

Every Cooking target explicitly saves one compatible heat source; there is no
automatic optimizer or silent fallback:

- `Range`: Cooking only, using the source-authentic lower burn chance and any
  range-only recipe requirements.
- `Own fire / solo bonfire`: the ordinary-fire choice is dual Firemaking and
  Cooking. Its background solo bonfire normally cooks, but when its
  log-dependent timer expires the next review performs one automatic
  maintenance-feeding batch, consumes the selected log type from the bank, and
  awards solo-bonfire Firemaking XP before Cooking resumes. Fuel is
  intentionally excluded from the Cooking target's 28-slot layout, but it is
  not free; the target stops and reports the missing selected log when bank
  stock runs out. The exact batch size and duration remain source-gated.
- `Busy public bonfire`: grants the full authentic public-bonfire Cooking bonus
  without consuming player logs or awarding Firemaking XP. Because the player
  contributes nothing, it grants no warmth and rolls no fire spirits.

### Evidence Gate

Use a RuneScape Wiki revision or Wayback capture from the November 2012 cutoff,
not the current live page, for log lifetimes, feeding cadence, XP formulas,
participant bonuses, burn-hand failures, warmth, fire-spirit chance and reward
table, Cooking compatibility, and range-versus-fire burn behavior. Reconcile
that snapshot with the revamped Darkan implementation and record any remaining
conflicts rather than choosing the modern value by default.

## Smithing: Artisan's Workshop, Burial Armour, and Ceremonial Swords

Backlog id: `smith-artisan-burial`

Decision status: compact UI and burial flow settled; ceremonial-sword scheduling
reopened after the pre-EOC source audit; exact action timing and remaining
reward effects wait for source reconstruction and the Darkan fidelity revamp.

### Compact Workshop Activity

- Place Artisan's Workshop inside Smithing as a compact sub-UI rather than a
  separate sprawling interface. Show the selected metal and ingot grade,
  current burial assignment or active plan, Respect, and a Rewards link.
- Abstract the Workshop's internal movement. The simulator transfers ore
  between the bank, Workshop storage, and ingots while preserving authentic
  costs, storage caps, losses, requirements, and undo behavior; do not require
  a manual furnace interface.
- Burial armour automatically follows the source-assigned armour piece. The
  player selects the metal and ingot grade, then assignments advance without a
  separate piece selector.
- Ordinary members' ceremonial swords are a separate level-70 Workshop method:
  the player withdraws a Grade IV ingot, obtains a plan from Egil, and works the
  sword deliberately. They are not random plans generated by burial smithing.
- Aksel's random bronze ceremonial-sword orders are a distinct Workshop
  diversion. The prior decision incorrectly merged these orders with ordinary
  plans, so whether AnkiScape interrupts burial for an Aksel order remains an
  owner question; do not implement either behavior by inference.
- Simulate source-authentic strike placement, mistakes, breakage, XP, Respect,
  and keep-plan rewards internally. Do not reproduce the detailed hammer grid
  as a player-operated minigame.

### Burst Pipes and Rewards

- Source-gate the absolute burst-pipe repair duration. If a repair fits inside
  the normal Workshop action slice, fold it into that review and show a small
  non-blocking result; only consume a full review if the November 2012 evidence
  shows that repair took roughly a full action slice. Quick Repairs halves the
  recovered source duration, and Repair Expert grants its source XP bonus.
- Respect rewards are deliberate manual purchases. The Workshop Rewards link
  deep-links to the Shop area's Activity Rewards surface rather than embedding
  another full shop in Smithing.
- Do not expose inert individual rewards. Golden cannon, Royale cannon, and any
  other reward remain hidden until their gameplay behavior, currency spending,
  persistence, and tests work end to end.

### Global Visibility and Shop Rule

- Minimize player-facing `visible but disabled with explanation` states.
  Implementation-incomplete features stay in the backlog and out of ordinary
  UI. Disabled rows are reserved for authentic player-state locks on otherwise
  functional content, such as level, quest, item, or currency requirements.
- The top-level Shop area has two visually distinct sub-tabs: `NPC Shops` keeps
  the existing stock, buy/sell, search, and history model; `Activity Rewards`
  contains manually purchased permanent or activity-specific unlocks grouped
  by their owning activity and currency.
- As a narrow exception, Activity Rewards may show curated shop-level preview
  cards for confirmed future activities. A stub card contains only its icon,
  reward-shop name, currency name, and `Coming later`; it exposes no individual
  reward rows and never implies that its currency can already be earned.

### Evidence Gate

Literal pre-EOC wikitext now verifies Workshop storage, ingot tiers, Suak's
burial assignments, one percent Respect per 10,000 Smithing XP, the separate
Grade-IV/Egil ceremonial-sword flow, the hammering grid and breakage rules,
random Aksel bronze orders, burst-pipe XP/Respect, and the reward catalog:
`Artisans' Workshop (historical)` oldid 6547352, `Respect (Artisans' Workshop)`
oldid 5579337, and `Ceremonial sword` oldid 6492957. Exact pipe-repair action
duration and any value supplied only by a transcluded reward template remain
unverified. Reconstruct those gaps from a dated Wayback/template revision or
the fidelity-revamped Darkan source before implementation.

## Smithing: Blast Furnace, Goldsmith Gauntlets, and Cannonballs

Backlog id: `smith-blastfurnace-goldsmith`

Decision status: design settled; exact Blast Furnace rolls, action cadence, and
historical access details wait for a pinned November 2012 source snapshot and
the Darkan fidelity revamp.

### Blast Furnace Operating Model

- Treat the Blast Furnace as a busy public activity. Other participants or the
  furnace crew keep its conveyor, pedals, temperature, pump, and repairs
  operating in the background; the player is not periodically diverted into
  machinery-maintenance reviews.
- Preserve the player's own source-authentic ore loading, bar collection,
  banking, access requirements, fees, coal savings, inventory constraints, XP,
  and action results. Busy operation removes maintenance busywork, not the
  economic or route identity of the activity.
- One review completes one source-sized inventory run: withdraw the configured
  ore load, place it on the belt, let the public machinery process it, collect
  the resulting bars, and bank them. Belt and dispenser states are simulated
  within that review rather than split into alternating load and collect
  reviews.
- Roll and account for every bar in the batch independently where the source
  mechanics require it. The complete-run abstraction must not turn a full
  inventory into one all-or-nothing smelting roll.
- Below level 60 Smithing, automatically renew the source-authentic foreman
  access period from banked coins after the later source-and-balance pass maps
  its historical ten-minute window to Blast Furnace actions. Apply the equipped
  Ring of charos (a) reduction, show a small non-interrupting payment popup, and
  consume no separate review. Stop the target when renewal cannot be paid;
  level 60 and above remains free.
- Do not import Old School RuneScape's later automated-worker coffer charge into
  the November 2012 ruleset. Busy public operation is the activity abstraction,
  not permission to add a modern recurring fee.

### Target-Specific Skilling Equipment

- Treat Goldsmith gauntlets as an equipment effect on the existing gold-bar
  target at both ordinary and Blast Furnaces; do not create a duplicate
  `goldsmith-gauntlet smelting` target.
- Casual mode automatically equips applicable, owned, and available beneficial
  skilling equipment such as Goldsmith gauntlets or the Ring of charos (a).
  Advanced mode applies an item only when it is selected in that target's saved
  equipment configuration.
- Bank displaced equipment safely and restore it when the player switches away
  from the target. Enforce each item's authentic quest, ownership, equipment,
  loss, and effect requirements. This is the reusable rule for later
  target-specific skilling equipment, not a Smithing-only exception.

### Cannonballs

- Cannonball smithing is its own Smithing target gated by the authentic Dwarf
  Cannon progress, Smithing level, steel bar, and ammo-mould requirements.
- One review resolves one cannonball-smithing action: consume one steel bar,
  produce four cannonballs, and award the source per-bar XP. The original
  client's automatic Make-X queue does not collapse the whole carried load into
  one AnkiScape action.
- When carried steel bars run out, use the already-settled target-specific
  inventory and bank-run rules. In Advanced the non-toolbelt ammo mould occupies
  a real carried slot; in Casual it is an ownership gate satisfied from the
  bank.

### Evidence Gate

Use a pinned November 2012 RuneScape Wiki revision or Wayback capture for Blast
Furnace access, ore and coal ratios, iron success, belt/dispenser batching,
fees, Ring of charos (a), equipment interactions, bar XP, and action behavior.
Reconcile it with fidelity-revamped Darkan. Darkan currently provides a usable
cannonball baseline of level 35, one steel bar to four cannonballs, 25.6 XP,
the ammo mould, and the Dwarf Cannon gate, but does not implement Blast Furnace
gameplay or the Goldsmith-gauntlet XP modifier.

## Cooking: Karambwan Family, Lava Eel, and Gnome Recipes

Backlog id: `cook-karambwan-family`

Decision status: design settled; exact recipe tables, gates, rolls, and item
effects wait for the fish-transcription dependency, a pinned November 2012
source snapshot, and the Darkan fidelity revamp.

### Recipe Action Model

- Add raw karambwanji, raw karambwan, and raw lava eel as ordinary source-gated
  Cooking targets. Each review resolves one cooking action for one input item,
  including the authentic success, burn or poison outcome, XP, and heat-source
  restrictions.
- Expose every authentic gnome preparation step as its own Cooking target,
  grouped beneath its recipe family. A chain such as preparing dough, baking a
  shell, adding filling, and garnishing therefore remains a sequence of real
  player-selected targets rather than a hidden automatic workflow.
- Each review processes one item through the selected stage and creates the
  authentic intermediate or final item. Intermediate items remain ordinary
  carried and banked items, and the player switches targets when ready to batch
  the next stage.
- Do not add a duplicate finished-recipe meta-target that silently performs or
  switches stages. Every stage inherits the unified per-target Casual policy,
  Advanced layout, preset, bank-run, persistence, and undo rules.

### Karambwan Methods

- Expose `Cook poison karambwan` and `Cook karambwan thoroughly` as separate,
  deliberate targets. Never automatically prefer the edible result after it is
  unlocked, because poison karambwan is an authentic item and recipe choice,
  not merely a failed roll.
- Preserve the source-authentic level, Tai Bwo Wannai Trio progress and teaching
  gates, 80-versus-190 XP awards, burn behavior, and outputs. Source-audit the
  exact November 2012 quest-state requirement rather than trusting Darkan's
  internally inconsistent karambwan enum alone.

### Wine

- `Make wine` is one Cooking target and one player action per review. Consume
  one bunch of grapes and one jug of water, immediately resolve jug of wine
  versus bad wine, and award the source XP only on a successful result.
- Fermentation is automatic waiting rather than another player action. Do not
  create a fermentation review, persistent non-combat minute timer, or separate
  player-selected fermentation target. The unfermented state may exist inside
  the atomic action transaction for source/item fidelity but is not persisted
  between reviews.

### Scope Boundary

- This grill covers the cookable fish, drinks, wine, and complete gnome recipe
  chains only. Gnome Restaurant is a separate minigame/Activity design problem
  and must receive its own owner grill before implementation.
- Preserve the recipe-chain engine and finished items as reusable inputs for
  that later activity. Its initial design seed is recorded in
  `memory-bank/activity-minigame-design-seeds-2026-07-10.md`.

### Evidence Gate

Transcribe the complete November 2012 inputs, outputs, levels, XP, success and
burn behavior, heat-source restrictions, quest teaching flags, healing and
combat effects, utensils, intermediate items, and recipe stages. Reconcile the
pinned historical source with revamped Darkan rather than copying its current
partial implementation: its karambwan enum is internally inconsistent, its
cocktail code mishandles multi-quantity ingredients, most gnome food assembly is
absent, and its wine action skips the historical intermediate behavior.

## Fletching: Javelin Construction — Rejected

Backlog id: `fletch-javelin-construction`

Decision status: rejected as out-of-period source contamination.

- Do not add bronze-through-dragon javelin shafts, heads, Smithing recipes, or
  Fletching construction targets. November 2012 RuneScape javelins could not be
  smithed or fletched; the proposed construction chain comes from Old School
  RuneScape's 2016 Monkey Madness II and ballista content.
- Retain only independently verified period-authentic javelin acquisition and
  behavior, such as shops, monster drops, poisoning, equipment, and combat use.
  This rejection does not affect the separately source-backed crossbow assembly
  transcription.
- Global source rule: ignore every OSRS-specific mechanic, item, quest, rate,
  interface, and convenience. An OSRS page may help locate a question, but it is
  never proof of November 2012 scope. Include a mechanic only when a pinned
  pre-cutoff RuneScape source or independently valid local 2011/2012 source
  proves that the same mechanic existed by the cutoff.

## Herblore: Overload, Sanfew Serum, and Weapon Poison

Backlog id: `herb-overload-sanfew`

Decision status: owner design settled; implementation waits for the remaining
source audit and reconciled server-behavior evidence.

### Overload Mixing

- One review performs one complete overload-mixing action at level 96 Herblore:
  consume one three-dose extreme attack, strength, defence, magic, and ranging
  potion plus one clean torstol; produce one overload (3), return four empty
  vials, and award 1,000 Herblore XP.
- Do not automatically craft missing extreme potions, clean the torstol, or
  source any component. Those remain separate player-selected Herblore actions
  and real inventory/bank requirements under the unified target rules.
- Primary historical checkpoint: RuneScape Wiki `Overload` revision 6552017,
  timestamped 2012-11-13T08:39:34Z. Read its archived literal wikitext through
  the MediaWiki API rather than trusting current template or calculator output.
- That same pre-EOC revision explicitly says drinking a dose deals five hits of
  100 lifepoints and that expiry after five minutes restores 500 lifepoints.
  The restoration is a direct potion-expiry effect, not an EOC addition or a
  separate ingredient-derived heal; the article gives no deeper mechanical
  source for it.

### Combat Potion Policy

- Every combat target stores its own potion policy beside its carried-inventory
  policy. `Use potions` is the master switch; individual potion checkboxes under
  it define which potion families combat may automatically drink and re-dose.
- The controls authorize consumption; they do not create supplies or grant
  whole-bank access during a fight. The selected potion and remaining doses
  must be present in the target's actual 28-slot carried pack, with refills only
  at the normal safe bank-run boundaries.
- Casual mode may automatically select, pack, drink, and re-dose Overload only
  for the `Max output` policy. Other Casual policies never introduce a damaging
  Overload automatically.
- Advanced mode never infers Overload. It may drink and re-dose one only when
  both `Use potions` and the individual `Overload` checkbox are enabled and the
  saved per-target layout actually contains it.
- All automatic use remains source-shaped and review-safe: it obeys the
  historical drinking gate and effect timing, occurs inside the combat burst,
  and never interrupts a review with a prompt.

### Sanfew Serum Mixing

- Model Sanfew serum as three separate, player-selected Herblore targets. One
  review performs exactly one ingredient addition; do not collapse the chain
  into one complete-serum action.
- Target 1 adds unicorn horn dust to a one-, two-, three-, or four-dose Super
  restore and produces the same-dose `Mixture - step 1`, awarding respectively
  28.5, 38, 47.5, or 57 Herblore XP.
- Target 2 adds clean snake weed to the same-dose `Mixture - step 1`, produces
  `Mixture - step 2`, and awards respectively 31.5, 42, 52.5, or 63 XP.
- Target 3 adds nail beast nails to the same-dose `Mixture - step 2`, produces
  the completed same-dose Sanfew serum, and awards respectively 36, 48, 60, or
  72 XP. The complete chain therefore awards 96, 128, 160, or 192 XP according
  to dose count.
- Preserve dose count through every stage. The implementation may present each
  stage as one dose-aware target rather than four duplicate rows, but the
  selected input dose, output dose, and exact source XP must remain explicit
  and deterministic.
- Both intermediate mixtures are ordinary tradeable items and were backed by
  the Grand Exchange potion template before EOC. They remain real inventory and
  economy items, not hidden transient state.
- Historical evidence: RuneScape Wiki `Sanfew serum` oldid 6333478
  (2012-10-02), `Mixture - step 1` oldid 5500383 (2012-04-16), and `Mixture -
  step 2` oldid 5500399 (2012-04-16), read as literal archived wikitext.

### Weapon-Poison Application

- Applying weapon poison is an instantaneous carried-inventory interaction, not
  a Herblore or Utility review target. Right-click an eligible unpoisoned weapon
  or projectile stack and expose `Poison` only when a compatible vial is also
  present in the carried inventory.
- `Poison` opens a submenu containing only the compatible poison strengths
  currently carried, with the resulting `(p)`, `(p+)`, or `(p++)` tier explicit.
  Never choose or consume the strongest available poison automatically. If only
  one tier is carried, the submenu may contain that single explicit choice.
- One vial permanently converts one eligible melee weapon or up to five eligible
  projectiles into the matching `(p)`, `(p+)`, or `(p++)` item variant. A larger
  projectile stack converts five and leaves the remainder unpoisoned.
- The poisoned item state does not expire with time, attacks, or reviews. Only
  the poison status inflicted on a victim decays and expires. A cleaning cloth
  remains the source-backed manual way to return a poisoned weapon to its clean
  variant.
- Applying poison awards no XP and requires no Herblore level. Mixing Weapon
  poison, Weapon poison+, and Weapon poison++ remains ordinary Herblore training
  at the period levels, ingredients, and XP.
- Eligible item families and poison strength use the pinned period definitions;
  do not generalize poison to every weapon. Preserve the resulting poisoned item
  as a real stable inventory/equipment identity rather than a temporary combat
  flag.
- Historical evidence: RuneScape Wiki `Weapon poison` oldid 6282857
  (2012-09-22), `Weapon poison+` oldid 6565085 (2012-11-17), and `Weapon
  poison++` oldid 6392216 (2012-10-12), read as literal archived wikitext. Each
  page defines the poisoned suffix, one-melee/five-projectile application, and
  manual cleaning instead of a weapon-side expiry.

## Woodcutting: Arctic Pine, Eucalyptus, and Cursed Magic

Backlog id: `wc-arctic-euc-cursed`

Decision status: owner design settled; implementation waits for exact success,
depletion, respawn, and paired-tree behavior from reconciled period evidence.

### Period Facts

- Arctic pine is a level-54 target awarding 140.2 Woodcutting XP and Arctic
  pine logs. Splitting one log at the Neitiznot stump awards another 42.5 XP.
- Eucalyptus is a level-58 target awarding 165 Woodcutting XP and Eucalyptus
  logs. The period page identifies a usable route by Mobilising Armies that does
  not depend on the Oo'glog quest-bank shortcut.
- Cursed magic is a level-82, Spirit of Summer-gated target awarding 275
  Woodcutting XP and Cursed magic logs. Those logs can be burned only while in
  the Spirit Realm at level 75 Firemaking, for the same XP as Magic logs, and
  automatically become ordinary Magic logs on leaving.
- The cursed tree and its ordinary Magic-tree counterpart alternate across the
  two realms when felled. Preserve that source relationship as an abstracted
  target loop rather than adding a world map.
- Historical evidence: RuneScape Wiki `Arctic Pine` oldid 6069429
  (2012-08-09), `Eucalyptus tree` oldid 6491980 (2012-10-28), `Cursed magic
  tree` oldid 6368505 (2012-10-08), `Cursed magic logs` oldid 5742321
  (2012-06-10), and `Spirit Realm` oldid 6394729 (2012-10-13), read as literal
  archived wikitext.

### Approved Cursed-Magic Abstraction

- Selecting Cursed magic begins a target-local Spirit Realm session; it does
  not create a global location or world-map system.
- Cursed logs remain cursed while chopping or when switching specifically to
  the existing `Burn cursed magic logs` Firemaking target, preserving the
  authentic in-realm Firemaking use.
- A bank run, explicit exit, or switch to any unrelated target ends the session
  and converts every carried Cursed magic log into an ordinary Magic log. The
  conversion is automatic and non-interrupting.
- Abstract the paired cursed/ordinary-tree traversal inside the target loop,
  with a compact current-action label if the reconciled server implementation
  requires visible phases. Do not make the player navigate between realms.

### Arctic-Pine Splitting Fact

- `Split log` oldid 5505475 (2012-04-18) confirms that using one Arctic pine
  log on the Woodcutting stump produces one tradeable, Grand Exchange-backed
  Split log at level 54 and awards 42.5 Woodcutting XP. This is a distinct
  XP-bearing action rather than part of the chop roll.

### Arctic-Pine Splitting Decision

- Add `Split Arctic pine logs` as a separate level-54 Woodcutting processing
  target. One successful review consumes one carried Arctic pine log, produces
  one carried Split log, and awards 42.5 Woodcutting XP.
- Do not automatically split newly chopped logs. Chopping Arctic pine and
  splitting its logs remain independently selected targets with their own
  per-target carried-inventory layouts and bank-run cadence.

### Eucalyptus Safety Decision

- Treat Eucalyptus as an ordinary safe Woodcutting target. The abstract target
  assumes the player uses one of the period grove's documented safe spots, so
  chopping does not roll ambient wolf/ogress encounters or damage player HP.
- This is a location-friction abstraction, not a claim that the original grove
  lacked danger. Directly dangerous action mechanics still use the shared HP,
  food, death, and undo systems where the source requires them.

### Source-Shaped Quest Gates

- Arctic pine chopping and Split-log processing unlock once `The Fremennik
  Isles` has started and remain available through and after completion. The
  period walkthrough says every island can be visited during the quest, and the
  Arctic-pine page explicitly describes use during and after it; do not impose
  an unnecessary completion-only gate.
- Eucalyptus has no quest gate. The Mobilising Armies route is available without
  the partial `As a First Resort...` progress used only for the Oo'glog bank.
- Cursed magic chopping and its Spirit Realm session require completed `Spirit
  of Summer`, matching the period tree/log access requirement.

### Grill Cadence Rule

- Do not ask the owner to approve source transcription or conclusions already
  forced by settled AnkiScape architecture. Resolve and batch those details in
  the audit. Reserve owner questions for genuine product choices where multiple
  reasonable options would materially change play.

## Runecrafting: Ourania, Wicked Hood, and Great Orb Project

Backlog id: `rc-zmi-gop-wickedhood`

Decision status: composite backlog row split by system. Ourania and Wicked hood
design are settled; exact Ourania output rolls wait for reconciled period/server
evidence. Great Orb Project moves to the separate minigame/activity design pass.

### Period Facts

- `Ourania Runecrafting Altar` oldid 6448353 (2012-10-21) confirms that the
  altar accepts only Pure essence, needs no talisman or specific rune level,
  makes one randomly selected rune per essence, biases toward higher runes as
  Runecrafting rises, and awards twice that rune's normal XP. It documents a
  short dangerous route, a long safe route, and Eniola's 20-rune bank fee.
- `Wicked hood` oldid 6564747 (2012-11-17) confirms manual daily Essence,
  Runes, and altar Teleport functions; fed altar access; a 100-essence baseline;
  one baseline rune withdrawal, doubled by an Elemental talisman; two altar
  teleports; permanent Runespan-outfit upgrades up to 175 essence, five rune
  withdrawals, and three altar teleports; unlimited Guild/Runespan entry
  teleporting; and reclaim with fed-talisman progress preserved.
- `Talk:Wicked hood` oldid 6341451 (2012-10-03) contemporaneously records the
  daily timer resetting at 00:00 GMT rather than 24 hours after use.
- `The Great Orb Project` oldid 6564759 (2012-11-17) confirms a level-50,
  multiplayer, team-versus-team activity with altar rounds, active orb/barrier
  participation, double-XP essence crafting, per-round essence, match-result
  token awards, and a distinct manual reward shop.

### Ourania Target

- Add Ourania as one Runecrafting target using the altar-route cycle already
  settled for ordinary altar training: bank/load, outbound route, craft, return.
- Casual mode uses the long safe route and Eniola banking. Advanced mode saves
  the target's unified carried layout and may select the long safe or short
  dangerous route plus its banking configuration. The short route uses the
  shared HP, food, death, and undo systems once its damage behavior is sourced.
- Each craft phase consumes the carried Pure essence and produces one random
  eligible rune per essence at twice that rune's base XP. Do not apply ordinary
  multi-rune multipliers. Keep the exact level-weighted output distribution
  source-blocked until period evidence or reconciled high-fidelity server code
  establishes it.

### Wicked Hood Charge Interface

- Keep the period interaction manual. Operating a carried or equipped hood
  opens compact Essence, Runes, and Teleport actions with remaining allowances;
  AnkiScape never auto-claims hood resources.
- Essence and runes enter the unified carried pack and respect free slots. A
  partial essence withdrawal reduces the remaining quantity rather than
  discarding overflow. Available rune/altar choices come only from fed access.
- A charged altar teleport skips the outbound-travel phase of the corresponding
  altar route; it does not create or move the player on a world map. The
  unlimited Guild/Runespan teleport is represented only as frictionless entry
  to those activities and never consumes an altar charge.
- Preserve one hood per player. Reclaim restores the item without resetting fed
  altars or current allowances. Runespan outfit purchases permanently raise the
  hood allowances when that reward shop is implemented.
- Preserve the historical 00:00-GMT reset only as source metadata. In AnkiScape,
  a depleted allowance pool recharges through successful Runecrafting actions,
  with at most one full pool stored. The exact action budget waits for the
  cross-skill balancing pass; it never depends on login time or calendar date.

### Great Orb Project Scope Split

- Do not flatten Great Orb Project into an altar target or a one-click token
  payout. Its teams, sequential altar rounds, active participation, essence
  decisions, match result, tokens, and shop form one separate activity system.
- Park its detailed simulation as a seed for the dedicated minigame/activity
  design pass. Its reward shop will use the visually distinct minigame-shop tab
  and manual purchases already chosen for minigame currencies.

## Mining: Living Rock Caverns and Shooting Stars

Backlog id: `mine-lrc-stars`

Decision status: owner design settled; implementation waits for reconciled
Living-mineral yield and exact star/server rolls.

### Period Facts and Existing Coverage

- Concentrated coal and concentrated gold already ship as ordinary Mining
  targets; do not add duplicate LRC variants.
- `Living Rock Caverns` oldid 6547876 (2012-11-11) and `Living rock remains`
  oldid 6556376 (2012-11-15) establish level 73, 25 Mining XP, and a bundle of
  Living minerals per mined corpse. The focused remains page says 5–24 while
  the cavern overview says 5–20, so the exact range remains source-conflicted.
  Another player's corpse becomes mineable after one minute.
- `Shooting Star` oldid 6556329 (2012-11-15) establishes nine layers with
  level requirements of ten times the layer, fixed layer-wide stardust pools,
  XP per dust, communal depletion, a 200-dust ownership cap, a first-finder
  bonus of 75 times Mining level, and one sprite reward per UTC day.

### Living Rock Remains

- Add `Mine living rock remains` as one level-73 Mining target once the exact
  5–20 versus 5–24 mineral conflict is reconciled. One corpse-processing action
  awards 25 XP and its sourced mineral bundle.
- A self-killed Living Rock creature exposes its remains immediately. A busy
  public-cavern abstraction also supplies other players' remains after the
  source delay, so Combat is useful but not an artificial hard prerequisite.
- Keep the current concentrated ore rows. Any later cavern-session danger model
  must cover travel to the deposit lift consistently across Mining and Fishing,
  using the shared HP, food, death, carried-layout, and undo systems.

### Shooting Star Session

- Do not add a world map or make the player wait two real hours. Starting the
  ordinary activity joins a reported communal star through an abstract star-
  hunting network; the source's many worlds and player clans make star access
  routine without inventing navigation or a real-time arrival schedule.
- Preserve the current layer, remaining communal dust, player dust, accessible
  level, and sprite state. Each successful review performs one Mining attempt;
  other simulated miners also advance communal depletion between attempts.
- Casual mode joins a sensibly populated star and automatically waits through
  inaccessible upper layers while showing the current layer/action. Advanced
  mode may save preferred starting sizes and a quiet/normal/busy population,
  trading personal dust opportunity against faster access to lower layers.
- Exchanging stardust with the released sprite is manual. Each completed star
  may expose one exchange, with rewards scaling to carried dust up to 200. Dust
  and completing the communal activity are the repeat gate; AnkiScape does not
  enforce the historical UTC daily lock.
- Represent the first-finder tag as an occasional session-start bonus produced
  by the simulated communal population. Do not add a scouting phase, telescope
  interface, map search, or player-controlled first-finder farming.
- The source's temporary extra-ore duration stays source/balance-blocked until
  skilling-action timing is calibrated without pretending each review represents
  combat's 30 seconds.
