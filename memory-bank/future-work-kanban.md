# AnkiScape Completion Kanban

Status: audited 2026-07-11. This is the canonical forward-work board. Detailed skill and program evidence lives in `memory-bank/completion-audit-2026-07-10.md` and `memory-bank/completion-audit.json`; the shipped-skill subledger remains `memory-bank/gap-backlog.json`.

## Label contract

- `DEEP GRILL`: owner-facing loop/UI/abstraction decisions remain.
- `SOURCE AUDIT`: design is settled, but pre-cutoff mechanics or values are incomplete/conflicting.
- `WAIT: DARKAN`: a stable high-fidelity restoration would materially reduce hidden-server guesswork; historical reconciliation still applies.
- `IMPLEMENT`: design and evidence are sufficient for a bounded backend/frontend/assets/tests slice.
- `DEPENDENCY`: another skill, activity, acquisition route, or economy surface must land first.
- `PARKED`: deliberately sequenced later, not forgotten.
- `EXCLUDED`: outside the product/cutoff boundary.

## Now — audit-backed implementation and source work

### Existing-skill parity ledger

Labels: `SOURCE AUDIT`, then `IMPLEMENT` only when evidence closes.

- Continue from `memory-bank/gap-backlog.json`; do not reconstruct merged cards or re-grill settled branches.
- Current detailed state: 22 merged, 13 design/source-blocked waits (including Grenwall), four split-scope, one Farming seed, one partially reopened/source-waiting, and two exclusions.
- Grenwall's pinned period revision proves its broad reward family but not exact spike/herb probabilities; it now explicitly waits on literal period evidence or a stable reconciled Darkan milestone (`memory-bank/source-audits/grenwall-reward-source-closure-2026-07-11.md`).
- The next implementation slice must have a pinned pre-EOC contract for its level, XP, inputs, outputs, gates, rates, and state transitions. Split proven sub-slices from blocked families as lava eel, Overload, and cannonballs already demonstrate.
- Backend acceptance: data, pure behavior, storage/migration, dispatch, acquisition semantics, telemetry, and undo.
- Frontend acceptance: `TargetRowMetadata`, real enablement/locks, target-local settings/equipment/inventory, icons, tooltips, and offscreen Qt coverage.
- Assets acceptance: period-appropriate art, explicit `--source rs3` where applicable, provenance, and path tests.

### Reconcile partial Combat skills with the skill ledger — status contract complete

Labels: `SOURCE AUDIT`, `IMPLEMENT`, `WAIT: DARKAN` for hidden enemy/equipment behavior.

- Attack, Strength, Defence, Constitution, Ranged, and Magic now use an explicit `partial` surface state with `training_source = Combat`; `implemented=False` still correctly means they do not own complete independent review surfaces.
- Keep unified Combat selection; do not add six competing hub rows merely to make the registry count look complete.
- Quest gates and XP rewards now recognize trainable partial stats, and legacy pending Combat-stat XP migrates directly. See `memory-bank/source-audits/partial-combat-skill-registry-2026-07-11.md`.
- Continue weapon/ammo/spell/equipment/enemy breadth under `memory-bank/combat-design-grill-2026-06-23.md` rather than reopening the Combat loop design.

### Prayer — grill complete, ready to build

Labels: `IMPLEMENT`, `SOURCE AUDIT` (mechanical extractions only).

- The full implementation-ready contract is `memory-bank/ankiscape-skill-expansion.md` (grill closed 2026-07-11). All product decisions are settled: bury/scatter/Ectofuntus/hosted-gilded methods, EV prayer/curse combat translation with the uptime policy toggle, prayer points and drain resistance, Rapid Restore analog, and skill-surface UI placement. Prayer selection and uptime fold into a new named combat preset system (bundling the existing supply loadout/pack mode) with per-target override.
- The Chaos Temple Wilderness bone altar was struck as an OSRS-2018 false positive (pre-EOC `oldid=5934985` shows only bone spawns and a recharge altar), which also mooted the Wilderness-risk decision.
- Remaining `SOURCE AUDIT` residue is the mechanical extraction list at the bottom of the contract: standard-book tables from game-main `prayer.kt`, the curse drain column from `oldid=6535713`, Darkan `Sap.java`/`Leech.java` step sizes, impious/accursed ash pins and demon drop wiring, bonemeal/ecto-token/slime items, Piety/Chivalry gate pins, and renewal restore rates.
- Shades of Mort'ton cremation and GE bones trail as `DEPENDENCY` on their own families; owned-POH altars trail on Construction.

### Magic — grill complete, ready to build

Labels: `IMPLEMENT`, `SOURCE AUDIT` (mechanical extractions only).

- The full implementation-ready contract is `memory-bank/magic-skill-contract-2026-07-11.md` (grill closed 2026-07-11). All product decisions are settled: uncapped full-parity alchemy with staff substitution, teleports as pure training casts, all three spellbooks with implicit book state and a strict per-preset/per-stint no-mixing rule, Spellbook Swap as the single sanctioned exception, the Dream review-cost heal policy, the casual pack-mode dial deriving prayers/uptime/Vengeance with exactly three surfaced toggles, and the per-spell salvage / pure-cast / not_applicable ledger.
- Combat ladder gap-fill rides along: surges, Wind Rush, god spells behind a Mage Arena landmark, Iban Blast, Magic Dart, Crumble Undead, Storm of Armadyl, and the bind/curse families as EV effects.
- Charge orbs close the reachability audit's elemental-orb orphan category; telegrab ships as the authentic Wine of Zamorak route.
- Remaining `SOURCE AUDIT` residue is the mechanical extraction list at the bottom of the contract (SpellbookData roster, Darkan cache alch values, enchantment/bolt tables, Ancients/Lunar wiki pins, curse/bind pins, orb/Mage Arena/telegrab pins).
- Deferred: Livid Farm spell set (its own activity card), Cure Plant / Fertile Soil real function (Farming), Plank Make consumers (Construction), Hunter Kit consumers (Hunter), Slayer staff acquisition (Slayer).

## Deep-grill queue — missing or incomplete skill surfaces

Each skill receives its own grill before implementation. Source-shaped facts should be resolved autonomously; grill only materially different AnkiScape choices.

### Farming

Labels: `DEEP GRILL`, `WAIT: DARKAN`, `SOURCE AUDIT`.

- Decide patch abstraction, review-clock growth, disease/death/protection, compost, payments, yields, tools/seeds, patch grouping, banking, and UI.
- Absorb `hunter-habitat-jadinko` only after the core Farming contract exists.
- Magic-grill handoff (owner-mandated): Cure Plant and Fertile Soil ship now as pure casts; when Farming lands they must gain real function (e.g. a farming-run option/checkbox), not stay ceremonial. See `memory-bank/magic-skill-contract-2026-07-11.md` decision 9.

### Construction

Labels: `DEEP GRILL`, `WAIT: DARKAN`, `SOURCE AUDIT`.

- Design a no-world-map POH surface for rooms, hotspots, furniture, build/remove actions, servants, storage, house services, materials, and Prayer/Farming dependencies.

### Agility

Labels: `DEEP GRILL`, `WAIT: DARKAN`, `SOURCE AUDIT`.

- Abstract courses as checkpoint/lap state without player location; decide failures/damage, tickets/rewards, run-energy benefits, shortcuts as dependency gates, equipment, and UI.

### Thieving

Labels: `DEEP GRILL`, `WAIT: DARKAN`, `SOURCE AUDIT`.

- Cover pickpockets, stalls, chests, doors, success/stun/damage, loot tables, blackjacking/gloves, inventory/banking, quest gates, and target families.

### Slayer

Labels: `DEEP GRILL`, `WAIT: DARKAN`, `SOURCE AUDIT`, `DEPENDENCY: COMBAT`.

- Reuse existing enemy Slayer metadata; add masters, assignment pools, XP, task progress, points/streaks, skips/blocks, reward shop, task-only targets, protection items, and Combat UI.

### Summoning

Labels: `DEEP GRILL`, `WAIT: DARKAN`, `SOURCE AUDIT`, `DEPENDENCY: COMBAT/ACQUISITION`.

- Cover charms/secondaries, pouch creation, points, familiars, timers, specials, beasts of burden, combat roles, death, inventory, banking, UI, and undo.

### Dungeoneering

Labels: `DEEP GRILL`, `WAIT: DARKAN`, `SOURCE AUDIT`, `DEPENDENCY: ALL SKILLS/COMBAT`.

- Define floor/session generation, solo/party abstraction, rooms, doors, keys, skill checks, combat, deaths, binds, complexity/prestige, tokens/rewards, dungeon-only items, persistence, and resumability.

## Wait for a stable Darkan restoration milestone

The local checkout was observed on `dev` at `55a7afa29`, 256 commits ahead of `origin/dev`, during an active restoration series. Treat it as moving research input until a stable milestone exists.

### 194-quest fidelity program

Labels: `WAIT: DARKAN`, `SOURCE AUDIT`.

- The catalog and stage-gate engine are scaffolding, not completion.
- Re-audit authentic stages, branches, items/transformations, combat, rewards, journals, unlocks, and missing-skill gates for every quest.
- Wait for Darkan where historical sources cannot prove hidden transitions or combat definitions; never fill gaps from modern RS3/OSRS.

### Large special methods and activities

Labels: `WAIT: DARKAN`, `SOURCE AUDIT`; add `DEEP GRILL` when activity flow is not already settled.

- Highest-value waits: Runespan; Bonfires/fire spirits; Artisan's Workshop; Blast Furnace/Goldsmith; Shooting Stars/LRC; Fish Flingers/Trawler; Great Orb Project; complex pyres/beacons; Gnome Restaurant; Hunter tracking/pitfall/snaring; Habitat/Jadinkos.
- Darkan should supply hidden state machines, rolls, currencies, and reward logic; period wiki/cache evidence still establishes cutoff and client identity.

### Missing skill server behavior

Labels: `WAIT: DARKAN`, after each `DEEP GRILL`.

- Prefer stable restored mechanics for Farming growth/yields/disease, Construction hotspots/furniture/services, Agility failures/courses, Thieving success/stun/loot, Slayer assignment/reward pools, Summoning familiar behavior, Dungeoneering floors/rooms, and Prayer/Magic hidden state.

## Cross-system program queue

### Activities, minigames, D&Ds, and reward shops

Labels: `DEEP GRILL`, `WAIT: DARKAN`, `SOURCE AUDIT`.

- Platform seed: `memory-bank/minigames-activities-design-seed.md`.
- Grill each family separately for entry/run state, review cost, event variance, currency, rewards, reward shop, persistence, expiry, and undo.
- Include the split activity cards from `gap-backlog.json`, bosses/instances, and wider pre-EOC reward activities. Never expose individual reward stubs before they work end to end.

### Bosses and instanced Combat

Labels: `DEEP GRILL`, `WAIT: DARKAN`, `DEPENDENCY: COMBAT/PRAYER/SUMMONING`.

- Fight Caves/Kiln, Barrows, God Wars, Corporeal Beast, Nex, quest bosses, and minigame enemies need authentic context and cannot become ordinary farm-target rows.

### Acquisition and item/equipment completeness

Labels: `SOURCE AUDIT`, `DEPENDENCY`, sometimes `WAIT: DARKAN`.

- Maintain `tools/audit_item_reachability.py`; its 2026-07-11 baseline found 267 orphan inputs across missing-skill/Farming, Magic/activity transformations, deferred activities, Combat/world acquisition, and potion-state plumbing. See `memory-bank/source-audits/item-reachability-audit-2026-07-11.md`.
- Close every live-but-unobtainable material through authentic drops, ground spawns, shops, claims, quests, skills, activities, or transformations. Do not seed free items or fake recipe gates.
- The source-backed Woodcutting nest → empty nest → crushed nest route is repaired and regression-covered.
- Finish equipment requirements, special attacks, poison, charges/degradation, set effects, jewellery, consumables, and source-specific use actions without creating fake recipes.

### Achievement diaries, clues, collections, and one-time content

Labels: `DEEP GRILL`, `SOURCE AUDIT`, `WAIT: DARKAN` where server state is hidden.

- Build from generic achievements and Bank Claims; add diary regions/tasks/rewards, clue step/casket state, collection tracking, one-time rewards, and their UI/undo contracts.

### Random events and timed world content

Labels: `DEEP GRILL`, `WAIT: DARKAN`, `SOURCE AUDIT`.

- Use the global 240-reviews-per-day clock for world/economy cadence only.
- Decide visibility, opt-in/interrupt behavior, expiry, missed events, rewards, persistence, and undo without adding a world map.

## Parked sequencing gates

### Grand Exchange

Labels: `PARKED`, `DEPENDENCY: SKILL/ITEM BREADTH`.

- Core design is locked in `memory-bank/fake-grand-exchange-design.md`; do not re-grill it.
- NPC shops are already live. Implement the GE after the skill/item universe is representative enough that prices, limits, and acquisition softness are meaningful.

### Level 1-99 time and economy balance

Labels: `PARKED`, `DEPENDENCY: ALL SKILLS/MAJOR METHODS`.

- Preserve source base XP now.
- After content breadth stabilizes, derive ordinary-efficient 2012 training-guide XP/hour envelopes and tune Anki pacing separately.

### Release readiness

Labels: `PARKED` until feature closure, then `IMPLEMENT`.

- Migration fixtures, manual Anki review QA, performance/accessibility, packaging/license audit, export/recovery, documentation, and personal-fork versus public-release scope.

## Explicitly excluded

- `EXCLUDED`: standalone transportation systems, persistent world map/player location, canoes, hot-air balloons, lodestones, and comparable transport-only content.
- `EXCLUDED`: post-cutoff and OSRS-only mechanics without independent pre-EOC proof; `fletch-javelin-construction` is the canonical rejected false positive, and the Chaos Temple Wilderness bone-offering altar (OSRS-2018) joined it during the Prayer grill.
- `EXCLUDED`: visible inert target/reward rows that cannot function end to end.
- `EXCLUDED`: wall-clock minutes for ordinary skilling actions; the card clock governs background/world/economy cadence only.

## Definition of done for any card

- Backend: pinned source audit, data, pure mechanics, storage/migration, runtime dispatch, inventory/acquisition, telemetry, undo, and focused tests.
- Frontend: shared target metadata, target UI, authentic locks, settings/equipment/inventory state, Bank/Stats/HUD/achievement effects, and Qt tests.
- Assets: item/target/material art, provenance, registry coverage, and existence tests.
- Balance: source base values preserved; Anki pacing isolated and documented.
- Verification: focused unit/integration/end-to-end coverage, full `python3 run_tests.py`, full offscreen Qt suite when UI exists, and manual Anki instructions.
- Memory: update this board and the detailed audit; preserve historical source audits instead of rewriting them as current status.
