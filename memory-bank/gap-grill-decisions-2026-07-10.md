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
- One review advances a short source-backed time slice of the current activity,
  which may contain several siphon attempts. It is not necessarily one game
  click. Exact slice lengths, rolls, depletion, XP, and point rates remain
  tunable until the fidelity and balance audits are complete.
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
  guides and reconstructed XP-per-hour ranges to calibrate simulated travel,
  banking, depletion, and activity time slices rather than rewriting XP or
  success rolls to force a desired result.
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
- Timed effects advance by the simulated duration of the activity being
  performed, not by wall-clock time and not by a universal review duration.
  Combat currently advances 50 game ticks, approximately 30 seconds, per base
  review; Cooking, Firemaking, and every other skill use their own source-backed
  action duration. Multipliers advance the corresponding simulated duration.

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

Decision status: owner grill in progress.

### Blast Furnace Operating Model

- Treat the Blast Furnace as a busy public activity. Other participants or the
  furnace crew keep its conveyor, pedals, temperature, pump, and repairs
  operating in the background; the player is not periodically diverted into
  machinery-maintenance reviews.
- Preserve the player's own source-authentic ore loading, bar collection,
  banking, access requirements, fees, coal savings, inventory constraints, XP,
  and simulated elapsed time. Busy operation removes maintenance busywork, not
  the economic or route identity of the activity.
- One review completes one source-sized inventory run: withdraw the configured
  ore load, place it on the belt, let the public machinery process it, collect
  the resulting bars, and bank them. Belt and dispenser states are simulated
  within that review rather than split into alternating load and collect
  reviews.
- Roll and account for every bar in the batch independently where the source
  mechanics require it. The complete-run abstraction must not turn a full
  inventory into one all-or-nothing smelting roll or erase the run's authentic
  elapsed time.
