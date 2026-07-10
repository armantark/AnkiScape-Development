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
