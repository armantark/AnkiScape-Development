# Product Context

## Why This Exists

Anki already rewards consistency through memory gains, but that feedback is abstract. AnkiScape makes each successful review feel like a small piece of persistent RuneScape progress while keeping study—not game administration—the primary activity.

## Experience Principles

- Pick an action, review normally, and see concise progress.
- Game state should be deep enough to sustain years of grinding but quiet enough not to interrupt recall.
- Inventory, equipment, banking, risk, quests, and economy create meaningful choices without requiring a second real-time game.
- Historical RuneScape values establish content; AnkiScape abstractions establish how that content fits reviews.
- Casual mode chooses sensible owned supplies/equipment; Advanced preserves target-local layouts and options.
- Missing acquisition routes should emerge as ordinary material shortage, not special UI labels or invented locks.

## Experience

- Each skill's surface state (complete or partial) lives in `core/skill_registry.py`; read it there, not here.
- Unified Combat trains the partial Combat skills through equipment/style choices, with real supplies, HP, food, Prayer/Magic configuration, death/recovery, drops, poison, potions, loadouts, and target-local carried inventory.
- Quests, Utility/Activities, Bank, Equipment, NPC Shops, Stats, Achievements, Settings, Bank Claims, HUD feedback, and review undo share these foundations.
- The quest catalog holds every pre-EOC quest row; `memory-bank/future-work-kanban.md` owns quest-by-quest fidelity work.

## Completion Direction

The goal is full pre-EOC breadth translated to Anki—not a literal world simulator. Unresolved skill depth receives a product grill only when authentic loops have multiple reasonable review abstractions. Large hidden-server systems may wait for a stable high-fidelity Darkan restoration, then must still be reconciled against period evidence.

Canonical live scope: `memory-bank/future-work-kanban.md`; the 2026-07-10
completion audit is archived under `memory-bank/archive/2026-07/baselines/`.

## Boundaries

- Melvor Idle is conceptual overlap only, never a content, balance, or UI source.
- No persistent world map or transport network.
- No modern RS3/OSRS substitution for missing pre-EOC proof.
- No ordinary skilling “minutes per review”; the card clock is reserved for world/economy cadence.
- Daemonheim resources stay inside the Dungeoneering session economy, not the persistent overworld Bank or ordinary Herblore target list; only explicit persistent rewards leave a floor.
- Any public release is a separately named, independently maintained derivative
  that credits Wilson Yeh as the original creator; it must not impersonate or
  replace his existing AnkiWeb listing.
