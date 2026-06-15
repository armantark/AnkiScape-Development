# Future Work Kanban

Status: 2026-06-15

Use this board as the handoff source for near-term AnkiScape follow-up threads. It captures the current owner priorities after the Crafting/Fletching/Smithing parity pass.

## Current Decisions

- Arrowtips are not an unresolved source gap. They are smithable through Smithing.
- Feathers are still an unresolved Fletching input gap.
- The Grand Exchange is a valid future candidate, but it is not a high-priority next step.
- Dependency-heavy Crafting acquisition loops are intentionally deferred for now.
- Special Mining and Woodcutting content should stay parked for now.
- Firemaking can be implemented in a separate thread and does not need to block this cleanup plan.
- Existing skill architecture and old implementation debt are the best high-leverage work to do next.
- Utility and Activities should get their own icon set so non-skill actions feel first-class.

## Priority Board

### P0 - Existing Skill Architecture And Old Debt

User story: As a future skill implementer, I want existing skill and activity behavior to be driven by registry metadata and shared action plumbing, so adding the next skill does not require editing scattered UI, runtime, and review-dispatch branches.

Why now: The repo has enough real skills to reveal recurring pressure in skill selection UI, target-list metadata, stats rendering, action dispatch, icon registration, storage shape, and achievements. Cleaning this up before the next broad skill makes every future expansion cheaper.

Backend scope:

- Audit current Mining, Woodcutting, Smithing, Crafting, Fletching, and Utility/Activities paths.
- Continue moving action behavior and target-list metadata behind registries instead of per-skill hardcoding.
- Keep the current flat save format unless a specific refactor proves it must change.
- Preserve current XP, item, undo, and review behavior.

Frontend scope:

- Remove hardcoded skill assumptions only where the backend contract can already describe the screen.
- Keep existing visual behavior stable unless the refactor explicitly supports a cleaner display contract.
- Leave clear handoff notes if backend metadata is ready but the UI migration should happen separately.

Acceptance criteria:

- Existing Mining, Woodcutting, Smithing, Crafting, Fletching, and Utility flows behave the same after the refactor.
- The review answer path still resolves actions through the intended handler key.
- Existing tests pass, and targeted tests cover any changed registry/action dispatch behavior.
- The follow-up Firemaking thread has fewer places to edit than the previous skill-expansion threads.

Future thread prompt:

```text
In the AnkiScape repo, use memory-bank/future-work-kanban.md as the source of truth. Work on P0: existing skill architecture and old debt. Audit Mining, Woodcutting, Smithing, Crafting, Fletching, and Utility/Activities, then make the smallest registry/action-dispatch refactor that reduces hardcoded skill branches without changing behavior. Keep backend and frontend work explicitly split, preserve the flat save model unless unavoidable, add targeted tests, update the Memory Bank, and commit the result.
```

### P1 - Utility And Activities Icon Set

User story: As a player, I want Utility and Activities rows to have purpose-built icons, so non-XP support actions feel intentional instead of like second-class placeholders.

Why now: Utility and Activities are already part of the active loop, but their presentation lags behind skill content. A small icon pass improves polish without reopening deferred acquisition systems.

Backend scope:

- Ensure Utility/Activities actions expose stable icon keys or item/category artwork paths.
- Avoid turning this into new gameplay logic unless the icon contract requires a small metadata addition.
- Record asset provenance in the Memory Bank or source audit notes.

Frontend scope:

- Add or wire icons for current Utility/Activities actions such as soft clay preparation, flax/wool gathering, nest opening, and related support rows.
- Keep icons visually distinct from skill icons while matching existing asset style and size.
- Add graceful fallbacks for missing icon paths.

Acceptance criteria:

- Utility/Activities rows resolve to their own icons in the UI.
- Existing skill and item art remains unchanged.
- Tests or lightweight verification cover the metadata path used by the UI.
- Provenance is recorded for new art or source-derived assets.

Future thread prompt:

```text
In the AnkiScape repo, use memory-bank/future-work-kanban.md as the source of truth. Work on P1: Utility and Activities icon set. Add a small, purpose-built icon contract and assets for existing Utility/Activities rows without adding new gameplay systems. Keep backend metadata and frontend display work explicitly split, verify the UI, update the Memory Bank, and commit the result.
```

### P2 - Feather Source For Fletching

User story: As a Fletching player, I want a legitimate source for feathers, so arrow recipes can progress without seeded materials or a full economy feature.

Why now: Fletching is functional, and Smithing already supplies arrowtips. Feathers are the remaining obvious arrow-making input gap.

Backend scope:

- Pick one intentionally narrow feather source. A Utility/Activities action is the smallest likely path.
- Do not duplicate arrowtip acquisition, because Smithing already owns that loop.
- Keep this separate from broader Crafting acquisition loops unless the user reprioritizes them.

Frontend scope:

- Surface the chosen feather source in Utility/Activities or wherever the backend action contract places it.
- Reuse the Utility icon work if it already exists; otherwise add a simple specific icon path or fallback.

Acceptance criteria:

- Feathers can be acquired through one non-dev route.
- Arrowtip production remains owned by Smithing.
- Fletching recipe definitions do not need source hacks or free-material assumptions.
- Undo/action multiplier behavior is tested if the source is an activity action.

Future thread prompt:

```text
In the AnkiScape repo, use memory-bank/future-work-kanban.md as the source of truth. Work on P2: feather source for Fletching. Arrowtips are already smithable, so only solve feathers. Implement one narrow, legitimate acquisition route, likely a Utility/Activities action, without reopening broader Crafting input loops or the Grand Exchange. Add targeted tests, update the Memory Bank, and commit the result.
```

### P3 - Grand Exchange V1 Candidate

User story: As a normal-mode player, I want optional market access for tradable items, so missing acquisition loops can be softened without forcing every source chain to be implemented first.

Why later: The design is useful, but the current priority is architecture debt and small polish. GE should not crowd out existing-skill cleanup unless the owner explicitly moves it up.

Backend-first scope:

- Use `memory-bank/fake-grand-exchange-design.md`; do not re-grill the core design unless requirements change.
- Keep v1 local-only and deterministic.
- Implement tradability metadata, coins, offer storage, matching/tick behavior, and tests before frontend work.
- Avoid recipe-aware bulk buying and other economy conveniences in v1.

Frontend follow-up scope:

- Add a top-level GE section only after backend contracts are real.
- Include search, buy/sell offer creation, offer status, collect, and cancel flows.
- Keep Bankstanding as a Utility activity only if the backend needs it.

Acceptance criteria:

- GE behavior follows the parked design file.
- Backend tests prove offer creation, matching, cancellation, collection, persistence, and tick behavior.
- Frontend work starts from a backend contract note, not guesswork.

Future thread prompt:

```text
In the AnkiScape repo, use memory-bank/future-work-kanban.md and memory-bank/fake-grand-exchange-design.md. Work on P3 only if the owner has explicitly reprioritized the Grand Exchange. Implement backend first: tradability metadata, coins, local offer matching, storage, ticks, and tests. Do not build recipe-aware buying. Leave a frontend handoff note before any UI thread starts.
```

### Parked - Crafting Dependency-Heavy Acquisition Loops

User story: As a player, I eventually want Crafting inputs to come from real source chains, but those chains should wait until their supporting systems are worth implementing.

Parked examples:

- Dragonstone and onyx supply.
- Leather and hide chains beyond current practical needs.
- Molten glass, battlestaves, orbs, roots, and rune-dependent flows.
- Any broader acquisition loop that mainly exists to support Crafting completeness.

Move out of parked only when:

- The owner explicitly reprioritizes the loop.
- A new skill makes the loop naturally useful.
- The GE implementation needs a specific tradable input classification.

Future thread prompt:

```text
In the AnkiScape repo, do not work on Crafting dependency-heavy acquisition loops unless the owner explicitly reprioritizes them. If reprioritized, start from memory-bank/source-audits/crafting-2011scape-2026-06-03.md, keep the scope to one source chain, and avoid broad economy or drop-table work.
```

### Parked - Mining And Woodcutting Special Content

User story: As a player, I eventually want special skilling content, but it should land after the supporting systems exist.

Parked examples:

- Mining concentrated coal/gold.
- Mining gem-rock Ring of wealth bonus.
- Shooting Stars.
- Woodcutting Inferno adze.
- Bird nest downstream uses that require Farming, Herblore, or broader loot systems.

Move out of parked only when:

- The owner explicitly reprioritizes special content.
- A supporting system such as Magic, Firemaking, Farming, Herblore, or a special reward framework is already in place.

Future thread prompt:

```text
In the AnkiScape repo, keep Mining and Woodcutting special content parked unless the owner explicitly reprioritizes it. If reprioritized, start from the relevant source audit in memory-bank/source-audits/ and implement one narrow special-content slice with tests and provenance notes.
```

## Parallel Firemaking Thread

Firemaking is still a valid separate skill-expansion thread. It can proceed independently from this Kanban if the owner wants a new skill before the architecture cleanup.

Future thread prompt:

```text
In the AnkiScape repo, implement Firemaking as a separate skill-expansion thread. Use the ankiscape-skill-expansion skill and the current Memory Bank. Do not use this as a reason to unpark Mining/Woodcutting special content unless the owner explicitly asks for it. Keep backend and frontend work split, add targeted tests, update the Memory Bank, and commit the result.
```
