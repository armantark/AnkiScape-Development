# AnkiScape Expansion Roadmap

## Strategy
Augment the current add-on in controlled layers. The main bet is that AnkiScape becomes much easier to grow once skills, items, and review actions are described by shared registries instead of hardcoded branches.

## Design Boundary
AnkiScape should use a compressed 2011-era RuneScape-style economy adapted to Anki pacing, not a complete RuneScape clone. The visible loop should remain close to the current plugin: select a skill/action target, review cards, and receive progress only for eligible answers. Wrong answers preserve current behavior: no penalty, no game progress.

The long-term skill taxonomy is Combat, Gathering, Artisan, and Support, plus a separate Utility/Activities bucket for visible material-only actions that award no skill XP. Magic should remain one skill with separate combat and noncombat action families.

## Phase 0: Memory And Planning
- Seed the memory bank.
- Move the working copy from the AnkiWeb numeric folder to `ankiscape_fork` so future public updates do not overwrite local work.
- Preserve the "augment, do not rebuild first" decision.
- Record current architecture and risks.

## Phase 1: Skill Registry Foundation
Backend:
- Define typed skill metadata: stable id, display name, category, implementation status, level key, XP key, action kind, target selector, and current flat save-key mapping.
- Define a minimal item manifest: stable item id, display/storage name, category, asset path, source/license note, stack behavior, level requirement, and base XP where applicable.
- Move Mining, Woodcutting, Smithing, and Crafting onto the registry with behavior parity.
- Keep existing flat save keys such as `mining_exp` and `current_ore`; generate defaults from registry metadata where practical so existing saves are preserved.
- Add storage migration helpers that can initialize skill fields and inventory categories generically without deleting unknown/custom inventory entries.
- Add unit and integration tests for registry lookup, review eligibility, item manifest coverage, asset existence, dispatch gating, and migration.

Frontend:
- Defer broad Qt redesign until the backend registry is stable.
- Eventually keep the top bar for global sections only: Skills, Bank, Stats, Achievements, Settings.
- Move skill navigation inside a Skills hub with category filters/cards and target lists like the current tree/ore/bar/craft selectors.
- Preserve settings toggles and review HUD behavior.

## Phase 2: First New Noncombat Skills
First proof point:
- Fletching: consumes logs and produces arrow shafts and unstrung bows.

Do not include flax, bowstrings, strung bows, arrows, Ranged, or combat dependencies in the first Fletching slice. Use this slice to prove that adding a skill is mostly registry data plus a small action handler.

Status: Fletching is implemented behind the registry and surfaced in the normal Skills hub with target selection.

Candidate follow-ups:
- Utility/Activities: visible material-only actions such as flax or wool gathering with no skill XP.
- Firemaking: consumes logs for XP.
- Fishing: gathers fish with level-gated spots.
- Cooking: consumes raw fish/food and produces cooked items.

## Current Priority: Skill Roster Breadth
Before resuming the GE (below), broaden the playable skill set so a real item economy exists to trade. Implemented today: Mining, Woodcutting (gathering) and Smithing, Crafting, Fletching (artisan), with their current backend/frontend parity passes complete.
- Remaining gathering skills: Fishing, Hunter, Farming.
- Basic artisan skills: Cooking, Firemaking next; then Herblore, Runecrafting, Construction.
- Each skill goes through `.cursor/skills/ankiscape-skill-expansion/` (source audit, assets, targets/recipes, Utility/Activities, achievements, tests, memory update).
- The tradable items these skills introduce become the GE's item universe when it is unparked.

## Phase 3: Item Economy And Achievements
- Expand item definitions, icons, and category metadata beyond the minimal Phase 1 manifest.
- Add an optional fake Grand Exchange-style market so non-ironman players can buy and sell tradable materials instead of manually gathering every dependency.
  - **Status: design locked and PARKED**, gated on skill-roster breadth (see Current Priority). Do not re-grill the design; resume from the checkpoint.
  - Engine is a hidden true-price + stochastic fill model (no persisted order book). GP is convenience-abundant, gated by buy limits + the market clock, and never sells XP. Undo rolls back the market tick via deterministic RNG + per-tick delta snapshot.
  - GE interaction should be optional; gathering, Utility/Activities, and production chains should remain valid and rewarding.
  - Keep account mode flexible: the default experience can allow market access, while an ironman-style self-sufficient mode can disable it later.
  - Treat prices/supply as AnkiScape balance data, separate from source XP/recipe data.
  - Detailed checkpoint: see `memory-bank/fake-grand-exchange-design.md`.
- Make achievements less dependent on hand-written lambdas where possible.
- Add collection, milestone, and cross-skill achievements.
- Consider optional drop tables for rare items.

## Phase 3.5: Special Noncombat Systems
- Farming should be an asynchronous review-clock system: the user plants/maintains patches in a separate Farming interface, eligible reviews advance growth, and harvesting awards Farming XP/items.
- Support skills should be planned but not forced into early mechanics. Thieving is the first likely active Support action. Agility can become an unlock/utility layer, Slayer should layer onto combat tasks, and Dungeoneering is late meta-progression or a rabbithole-style activity.

## Phase 4: Combat Prototype
Backend:
- Require explicit Combat mode with selected monster/action.
- Model combat as turn-like review events, not real-time gameplay.
- Good answers progress attacks or actions.
- Missed/low-quality answers initially skip progress without direct penalties.
- Add monsters, HP, combat XP, basic drops, and equipment later.
- Slayer can later assign tasks that guide monster selection once combat exists.

Frontend:
- Add a simple combat panel after noncombat registry patterns are stable.
- Keep HUD compact; do not let combat UI dominate review.

## Phase 5: Balance And Release Readiness
- Tune XP rates against real Anki session lengths.
- Add manual test instructions for Anki runtime flows.
- Expand packaging notes.
- Decide whether this remains a personal fork or becomes a public derivative release.

## Open Questions
- Which acquisition loops should supply hides, glass inputs, battlestaff parts, and other currently input-starved materials before the GE exists? Arrowtips are already smithable, and feathers now have the temporary `Scavenge chicken feathers` Utility bridge.
- How should Utility/Activities be presented so no-XP material actions feel intentional rather than punishing? Current priority and prompts live in `memory-bank/future-work-kanban.md`.
- What exact constants should the fake GE use for liquidity, volatility, aggregate order flow, and stochastic supply/demand shocks?
- What is the first Thieving target list and reward table?
- How much planned-skill catalog metadata should developer mode expose for testing?
