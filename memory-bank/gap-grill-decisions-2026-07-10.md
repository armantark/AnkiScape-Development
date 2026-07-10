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
