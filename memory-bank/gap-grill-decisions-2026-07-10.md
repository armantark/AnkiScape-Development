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

### Bank Direct-Action Contract

Status: **owner-approved design; implementation pending on `main`.**

- Replace the destructive `Discard all` Bank command with `Discard X`. The
  player chooses the quantity explicitly, and the remainder of the stack stays
  in the Bank.
- A discard is an instantaneous Bank action with its own direct-action undo
  entry. It is never tied to Answer Card undo and never costs a review.
- Replace the one-at-a-time `Add to carried layout` command with `Set carried
  quantity...` for the active target's Custom pack. The backend must use the
  canonical item stackability metadata: any positive quantity of a stackable
  occupies one slot, while each non-stackable unit occupies one slot.
- Custom-pack entries are ordered. Adding a previously absent item appends it
  to the carried queue, and bank-run packing applies entries in that saved
  order, first-come-first-served when stock or slot capacity is insufficient.
  The 4x7 grid renders the same order rather than sorting item names. Changing
  a positive quantity preserves that item's existing position; setting it to
  zero removes it, and adding it again later appends it to the end.
- Keep the Bank menu contextual and explicit. Existing source-backed verbs such
  as Equip, Eat/Drink, and Teleport urn remain; add genuine instantaneous item
  transformations such as applying weapon poison or cleaning a poisoned weapon
  as their mechanics become available. Do not add a vague generic `Use` action.
- Add Bank item search/filtering without changing saved carried-queue order.
  Do not reproduce Withdraw, Deposit, Note, Un-note, Sell, bank tabs, or
  placeholders: the flat Bank is persistent storage and the target-specific
  28-slot pack is the carried subset.

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
- Preserve the historical daily cadence through the shared answered-card market
  clock: 10 answered cards equal one simulated hour and 240 equal one simulated
  day. At each 240-card boundary, the hood refills one allowance pool to its
  current upgrade cap; unused charges do not stack. Any answered card advances
  the clock, and Anki undo restores the previous clock and allowance state.

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

- Do not add a world map or make the player wait two real hours. Star cycles use
  the same global answered-card clock as shops and the future GE: the source's
  roughly two-hour arrival becomes roughly 20 answered cards. Starting the
  activity joins the current reported communal star without simulating travel.
- Preserve the current layer, remaining communal dust, player dust, accessible
  level, and sprite state. Each successful review performs one Mining attempt;
  other simulated miners also advance communal depletion between attempts.
- Casual mode joins a sensibly populated star and automatically waits through
  inaccessible upper layers while showing the current layer/action. Advanced
  mode may save preferred starting sizes and a quiet/normal/busy population,
  trading personal dust opportunity against faster access to lower layers.
- Exchanging stardust with the released sprite is manual. Completing a star
  exposes the sprite, rewards scale to carried dust up to 200, and the exchange
  allowance resets every 240 answered cards. This preserves one reward per
  simulated game day without tying AnkiScape to the real calendar.
- Represent the first-finder tag as an occasional session-start bonus produced
  by the simulated communal population. Do not add a scouting phase, telescope
  interface, map search, or player-controlled first-finder farming.
- The source's temporary extra-ore duration stays source/balance-blocked until
  skilling-action timing is calibrated without pretending each review represents
  combat's 30 seconds.

## Fishing: Trawler, Fish Flingers, and Daemonheim Fishing

Backlog id: `fish-trawler-flingers`

Decision status: composite row split by system. Fishing Trawler design is
settled; Fish Flingers moves to the minigame/D&D pass and Daemonheim fishing to
the eventual Dungeoneering expansion.

### Period Facts

- `Fishing Trawler` oldid 6288357 (2012-09-24) establishes level 15 entry, a
  safe twelve-minute team minigame, consumable swamp paste for leaks, consumable
  rope for torn nets, reusable bailing buckets, an anti-idling activity bar,
  failure by sinking, level-shaped saltwater catches, and Fishing XP equal to
  40% of the catch's ordinary XP. Sea turtles require 79 and manta rays 81.
- `Fish Flingers` oldid 6529096 (2012-11-03) establishes a no-level, no-item
  multiplayer D&D with temporary bait/hook/weight controls, tackle-discovery
  feedback, communal depletion, big-fish cooperation, Fishing-level-scaled XP,
  two daily tickets with a ten-ticket cap, medals/tokens, and a reward shop.
- `Dungeoneering/Fishing` oldid 5812989 (2012-06-23) establishes Daemonheim-only
  fly fishing with temporary rod/feathers, tiered fish, occasional half XP,
  stackable in-floor resources after the April 2012 toolbelt update, and a
  maximum of 14 fish per generated spot.

### Fishing Trawler Activity

- Build Trawler as a persistent activity session, not an ordinary Fishing
  target and not a one-review loot roll. Track boat water, active leaks, net
  state, player contribution/activity, crew contribution, remaining action
  phases, supplies, and success or sinking.
- One successful review performs one useful Trawler duty. The global market
  clock continues to advance, but the source's twelve minutes do not collapse
  the trip into two reviews; skilling still uses action ticks rather than
  converting every review into six minutes.
- Casual joins a busy public crew and automatically performs the most urgent
  useful action that its carried supplies permit: repair leaks, bail, or repair
  the net. Advanced saves duty checkboxes, a solo/small/busy crew preference,
  and this activity's unified carried layout.
- Swamp paste and rope are consumed by their duties; the bailing bucket is a
  reusable carried tool. The source shop supplies all three through the normal
  Shop surface.
- A successful trip awards the level-shaped catch and 40% ordinary fish XP.
  Deposit the haul directly into the bank with a non-blocking summary because
  the source catch interface sits beside a deposit box; claiming costs no extra
  review. A sunk trip awards no haul.

### Scope Splits

- Fish Flingers remains a separate multiplayer D&D. Its tackle deduction,
  temporary control panel, competition state, cooperative big fish, medals,
  tokens, and visually distinct manual reward shop should be designed together
  in the future minigame/activity pass. Its ticket grants use the shared
  simulated-day clock rather than the computer date.
- Daemonheim fish belong to Dungeoneering, not the ordinary Fishing target list.
  They use the dungeon's temporary stackable inventory, generated spots, toolbelt,
  Cooking/Firemaking survival loop, and party state; nothing leaves to the bank.

## Firemaking: Pyres, Shades of Mort'ton, and the Beacon Network

Backlog id: `fm-pyres-beacons`

Decision status: composite row split by system. Pyre processing and Beacon
Network design are settled; the broader Shades of Mort'ton loop moves to the
minigame/activity pass. Exact reward rolls and active timers wait for reconciled
period/server evidence.

### Period Facts

- `Firemaking` oldid 6513361 (2012-10-31) and `Template:Pyre ships` oldid
  5501212 (2012-04-16) establish Barbarian pyre ships from one log plus chewed
  or mangled bones, level-matched Crafting and Firemaking XP, and one to five
  subsequent bones receiving enhanced Prayer XP based on the log. Mangled bones
  summon a dangerous Barbarian spirit.
- `Shades of Mort'ton (minigame)` oldid 6449451 (2012-10-21) establishes the
  quest-gated temple/sanctity loop, olive-oil blessing, two-to-four-dose pyre-log
  recipes, shade-remains compatibility, Firemaking XP, funeral-pyre cremation,
  Prayer XP, shade keys/coins, and catacomb chests.
- `All Fired Up (minigame)` oldid 6564841 (2012-11-17) establishes the quest-
  gated 14-beacon network, 20 same-type unnoted logs per beacon, optional five-
  log tending/refuelling, log-dependent burn windows, per-beacon requirements,
  simultaneous-lighting XP, and rewards at 6, 10, and 14 lit beacons.

### Pyre Actions and Shades Scope

- Add every source-backed pyre-log recipe as an ordinary Firemaking processing
  target: consume the correct sacred-oil doses and one log, produce its pyre log,
  and award the period Firemaking XP. These rows remain visually ordinary even
  while sacred-oil acquisition is not yet implemented.
- Add funeral-pyre cremation rows keyed by shade-remains family and compatible
  pyre-log tier. They consume both inputs and award the source Prayer XP plus the
  sourced key-or-coins result once those rolls are reconciled.
- Do not pretend the surrounding Shades loop is a list of Firemaking targets.
  Temple repair, personal sanctity, oil blessing, shade combat, Mort'ton danger,
  catacomb access, keys, and chests form one separate multi-skill activity.
- Add Barbarian pyre ships as separate chewed-bone and mangled-bone targets for
  each supported log tier. One completed ship consumes one log and one bone,
  awards both Crafting and Firemaking XP, and stores the sourced count of future
  bone/ash actions receiving enhanced Prayer XP. Mangled-bone variants enter the
  shared Combat/HP/food/death/undo flow for the summoned spirit.

### Beacon Network Abstraction

- Use a dedicated 14-row Beacon Network activity panel, not a world map. Each
  row owns unlock/keeper/repair state, loaded log tier/count, burn strength, and
  extinguished/weak/lit status.
- Preloading, one-time keeper preparation, repairs, lighting, refuelling, and
  abstract travel are activity phases. The system may bank-run between preload
  batches; beacon-stored logs persist and do not occupy the carried pack.
- Casual selects the highest useful accessible milestone—6, 10, or 14—and plans
  an achievable route and economical log assignment automatically. Advanced
  saves beacon checkboxes, route order, per-beacon log choices, and the unified
  carried layout; inventory presets use the existing save/apply flow.
- Active beacon burn windows advance in Beacon activity phases, calibrated from
  the period burn-time and route evidence. Do not subtract six minutes per
  review merely because the background market clock advances one hour per ten
  answered cards; both clocks advance, but they model different things.
- On reaching 6, 10, or 14 simultaneously lit beacons, expose the corresponding
  Ring of fire, Flame gloves, or Inferno adze as a manual claim. Repeated runs
  remain available for source XP after the one-time items are owned.

## Fishing: Cave Eel

Backlog id: `fish-cave-eel-stub`

Decision status: source-shaped target settled without an owner question. Exact
catch probability remains source-blocked pending Darkan/high-fidelity evidence.

### Period Facts

- `Cave eel` oldid 6357178 (2012-10-06) establishes level 38 Fishing, an
  ordinary Fishing rod plus Fishing bait, 80 Fishing XP, and Raw cave eel as a
  tradeable output. It lists Lumbridge Swamp Caves and the Meiyerditch dungeon
  as fishing locations.
- The same period page establishes the linked Cooking row at level 38, 115
  Cooking XP, and variable healing from 70 to 110 life points. That downstream
  row belongs to the Cooking/HP pass rather than changing the Fishing action.

### AnkiScape Representation

- Add `Catch cave eel` as an ordinary Fishing target. One successful review
  performs one catch action, consumes one Fishing bait, awards one Raw cave eel
  and 80 Fishing XP, and keeps the Fishing rod as a reusable carried tool.
- Use the abstract Lumbridge Swamp Caves route with no quest gate and no world
  map. Meiyerditch is an optional source location, not a universal access gate.
- The target uses the unified inventory contract: its own editable carried
  layout plus the shared save-preset/apply-preset dropdown. Do not create a
  Cave-eel-specific inventory system.
- The archived wiki row does not establish the exact catch roll. Preserve the
  source-backed level, inputs, output, and XP now, but do not fabricate a catch
  chance while the Darkan/high-fidelity parity source is pending.

## Woodcutting: Canoes and Transportation Scope

Backlog id: `wc-canoe-shaping`

Decision status: rejected from product scope.

- Do not add Log canoe, Dugout, Stable dugout, or Waka shaping targets, even
  though the live source awards Woodcutting XP for shaping them. Canoes are
  fundamentally a transportation method, and their incidental XP does not make
  them a useful AnkiScape training family.
- Do not add canoe state, river destinations, a travel interface, or persistent
  player-location state. The same boundary excludes standalone hot-air-balloon,
  lodestone, and comparable transportation systems from future parity passes.
- This does not remove activity-specific travel friction already approved for
  altar runs, beacon routes, and similar loops. Those systems may represent
  travel as an internal abstract action phase because it changes the activity's
  pacing; they must not grow into a general map or transport network.

## Cross-skill: Crafting and Fletching Potions

Backlog id: `artisan-skill-potion-runtime`

Decision status: design settled from the existing potion and inventory rules;
review-scale stat-restoration cadence remains source/balance-blocked.

- Give each Crafting and Fletching target its saved `Use potions` checkbox. A
  checked target may drink the matching potion from its actual carried layout;
  it cannot synthesize a dose or reach into the bank during an action.
- The emulator's Crafting and Fletching potions raise current level by exactly
  three. Boosted current level counts for row selectability and action gates;
  base level and XP remain unchanged.
- Auto-drink only when the selected recipe is above base level but reachable at
  the current potion cap. Re-dose only when natural decay would otherwise block
  the next action. There is no output or XP benefit to wasting doses while the
  target is already available at base level.
- Persist temporary current levels and remaining doses. Drinking, dose-item
  replacement, decay, target selection, produced items, XP, and any re-dose all
  participate in the triggering review's undo snapshot.
- The reconstruction restores temporary stats one point every 100 game ticks.
  Do not translate that through the ten-cards-per-game-hour economy clock, which
  would expire a short boost before AnkiScape could perform the enabled action.
  The later pacing pass must calibrate a review-action cadence separately.

## Cross-skill: Brawling Gloves and Wilderness Variants

Backlog id: `skilling-brawling-gloves-runtime`

Decision status: owner design settled; exact period values, acquisition, and
Wilderness-risk cadence await reconciled evidence.

- Add a saved `Train in Wilderness` checkbox to every source-supported Mining,
  Smithing, Woodcutting, Fishing, Cooking, and Firemaking target. Checking it
  selects that target's abstract Wilderness variant; it does not move the
  player, create a map, or persist a global location.
- Brawling gloves remain real equipped items in the glove slot. The checkbox
  neither creates nor equips them. A matching charged pair applies the sourced
  Wilderness multiplier when checked and the sourced non-Wilderness multiplier
  otherwise; each XP-awarding action consumes one charge and the item
  disintegrates at zero.
- The reconstruction currently specifies skill-specific maximum charges,
  level-scaled initial charges, 4x or 5x Wilderness multipliers by skill, and a
  1.5x non-Wilderness multiplier. Preserve those as leads, not final historical
  truth, until pinned pre-EOC evidence or high-fidelity Darkan corroborates them.
- A checked target uses the shared carried-layout, HP, food, bank-run, death,
  and undo systems. Wilderness XP must not become a risk-free checkbox bonus;
  the exact encounter/risk cadence is part of the later Combat/location source
  reconciliation.
- Implement this as one shared equipment-charge and XP-multiplier contract, not
  six unrelated skill-specific systems.

## Firemaking: Barbarian Bow-lighting

Backlog id: `fm-barbarian-bow-lighting`

Decision status: bow-lighting behavior settled; its permanent unlock moves to
the future Barbarian Training miniquest/activity pass.

### Period Facts

- `Barbarian Training` oldid 6476330 (2012-10-26) requires level 35
  Firemaking to learn the method from Otto and describes using a strung wooden
  bow on an oak log. The emulator dialogue sets a persistent
  `learnedBarbarianFiremaking` flag when Otto gives the instruction.
- The period page states that bow-lighting has no inherent advantage over a
  tinderbox and starts fires at the same speed. It supplies the complete
  per-log bow-lighting level/XP table: normal and achey 21/40, oak 35/60,
  willow 50/90, teak 55/105, arctic pine 62/125, maple 65/135, mahogany
  70/157.5, eucalyptus 78/193.5, yew 80/202.5, and magic 95/303.8.
- Dark, Crystal, Sacred clay, Boogie, Quickbow, and Ogre-family bows do not
  work. The method requires a strung bow made from wood.

### AnkiScape Representation

- Do not create a second set of Firemaking targets. After the unlock, existing
  eligible log targets expose a saved `Light with bow` option. The option uses
  the source's bow-specific level requirement, requires an eligible strung bow,
  consumes one log, and awards the ordinary log's XP and result.
- Casual always uses the ambient/toolbelt tinderbox because the alternative is
  source-confirmed to offer no speed, XP, output, or success advantage.
  Advanced may opt into bow-lighting for a target as a preference or carried-
  equipment constraint.
- The future Barbarian Training miniquest/activity dialogue owns the permanent
  learned flag. Do not fake the unlock through bow ownership or add a separate
  XP-bearing `learn bow-lighting` target; the first actual bow-lit log remains
  an ordinary Firemaking action.

## Cooking: Cooking Gauntlets

Backlog id: `cook-cooking-gauntlets-runtime`

Decision status: product design settled; exact affected-fish membership and
intermediate burn-rate curves remain source-blocked.

### Period Facts and Conflict

- `Cooking gauntlets` oldid 6556123 (2012-11-15) describes a non-tradeable,
  equippable Family Crest reward conversion that reduces fish-burning risk. It
  says first conversion through Caleb is available from Family gauntlets, that
  changing an already enchanted pair costs 25,000 coins, and that a lost pair
  is recovered free from Dimintheis with the same enchantment.
- Its table lists no-burn thresholds with gauntlets for tuna 63, lobster 68,
  swordfish 81, monkfish 90, and shark/cavefish/rocktail 94.
- `Cooking` oldid 6548144 (2012-11-11) instead describes the effect as applying
  to lobster, monkfish, swordfish, shark, cavefish, and rocktail, while its own
  fish-table note narrows that list further and omits monkfish. The page also
  says the exact anti-burning bonus came from player statistics rather than an
  official formula. These literal period pages therefore do not establish one
  authoritative affected-fish set or intermediate probability curve.
- `Family Crest` oldid 6548361 (2012-11-11) confirms the Family gauntlets reward,
  the three brother enchantments, and the 25,000-coin fee to change effects.

### AnkiScape Representation

- Conversion is a manual inventory/equipment context action after Family Crest:
  Family gauntlets become Cooking gauntlets free; changing from Goldsmith or
  Chaos gauntlets consumes 25,000 Coins. The NPC dialogue awards no XP and does
  not consume a review.
- Cooking gauntlets modify the existing fish targets rather than creating
  duplicate recipes. Casual auto-equips an owned available pair when it helps;
  Advanced uses the target's saved equipment selection. When worn, the effect
  is automatic, has no charges, and never changes Cooking XP.
- Persist the chosen Family-gauntlet enchantment separately from the physical
  item. A manual `Recover gauntlets` claim restores a lost pair free with the
  same enchantment, matching Dimintheis; conversion, payment, equipment state,
  recovery, cooking result, and burn/XP outcome remain undo-safe.
- Do not infer a burn formula from the published zero-burn thresholds. Reconcile
  the page conflict against high-fidelity Darkan or stronger dated evidence,
  then apply the verified fish membership and odds to the existing Cooking
  success calculation.
