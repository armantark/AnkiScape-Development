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
- Gate penguin tracking behind Hunt for Red Raktuber and rabbit snaring behind
  Eagles' Peak. Selecting a Hunter target abstracts travel to its canonical
  area; do not add persistent location or a world-map system.
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
- Port the source distribution exactly: every successful catch gives 18-21
  grenwall spikes and bones, followed by an independent 15% one-of roll for
  grimy kwuarm, cadantine, dwarf weed, lantadyme, or toadflax and an independent
  18% one-of roll for grimy ranarr, irit, or avantoe.
- Preserve both independent herb rolls, including the possibility that one
  catch awards herbs from both groups. The existing fixed 18-spike reward is
  not full parity.

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

Decision status: design settled; exact action timing, reward effects, and
ceremonial-sword rolls wait for a pinned November 2012 source snapshot and the
Darkan fidelity revamp.

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
- Ceremonial sword plans appear at their source-authentic frequency during
  burial smithing. A plan automatically pauses burial work, simulates the
  hammering puzzle across reviews while displaying its plan, progress, and
  result, then resumes the prior assignment.
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

The current Darkan implementation establishes Workshop storage, ingot tiers,
burial-assignment scaffolding, the one-percent-Respect-per-10,000-Smithing-XP
rule, and the intended reward catalog, but its ceremonial sword is only an
interface opener and burst-pipe action handling is absent. Reconstruct those
missing mechanics and timings from a pinned November 2012 Wiki revision or
Wayback capture, then reconcile them with the fidelity-revamped source before
implementation.

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
