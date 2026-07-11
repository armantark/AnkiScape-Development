# AnkiScape completion audit — 2026-07-10 (reconciled 2026-07-11)

This is the project-wide completeness baseline. The machine-readable companion is `memory-bank/completion-audit.json`; the action surface is `memory-bank/future-work-kanban.md`.

## What “complete” means

AnkiScape is complete when the 25 skills and the cross-system programs below have source-faithful, review-paced loops for the pre-EOC cutoff, or are explicitly excluded by product scope. Presence in a registry, generated catalog, or UI is not enough: actions must work end to end with acquisition, inventory, persistence, undo, assets, and tests.

The target is RuneScape immediately before EOC (`2012-11-20`). Pinned historical evidence remains authoritative. A high-fidelity Darkan restoration can supply reconstructed server behavior, but it does not erase the need to reconcile against the period wiki, Wayback, and caches.

## Headline state

- 25 pre-EOC skills audited.
- 11 are registered review skills: Mining, Woodcutting, Fishing, Smithing, Crafting, Fletching, Firemaking, Cooking, Runecrafting, Hunter, and Herblore.
- Six additional stats have real partial runtime through unified Combat: Attack, Strength, Defence, Constitution, Ranged, and Magic. Their registry rows now say `partial` and identify Combat as their training source; `implemented=False` still records that they do not own complete independent skill surfaces.
- Eight skills are wholly missing: Prayer, Summoning, Construction, Farming, Agility, Dungeoneering, Slayer, and Thieving.
- Magic is the ninth missing full skill surface: its standard combat spell ladder is live, while noncombat Magic and broader spellbooks are not.
- The 194-row quest catalog is coverage scaffolding. It is not a claim that 194 quests are faithful or complete.
- `memory-bank/gap-backlog.json` remains the detailed ledger for the eleven shipped skills: 22 merged cards, 19 still active/parked/split, and two explicit exclusions at audit time.

## Skill gate matrix

| Skill | Current state | Deep grill? | Darkan value | Next gate |
|---|---|---:|---|---|
| Attack | Partial Combat runtime | No; existing Combat grill | Helpful | Source/equipment/enemy breadth |
| Strength | Partial Combat runtime | No | Helpful | Shared Combat parity |
| Defence | Partial Combat runtime | No | Helpful | Shared Combat/equipment parity; stable save id remains `defense` |
| Constitution | Partial Combat runtime | No | Helpful | Consumables, recovery, overheal, equipment and status parity |
| Ranged | Partial Combat runtime | No | Helpful | Crossbows, thrown weapons, ammo effects, specials, equipment breadth |
| Magic | Partial combat-only skill | **Yes** | **Preferred** | Resume a dedicated grill for noncombat actions, spellbooks, enchantment and gates |
| Prayer | Missing; partial grill exists | **Yes** | **Preferred** | Resolve the open Prayer decisions before building |
| Summoning | Missing | **Yes** | **Preferred** | Full pouch/familiar/points/BoB/combat loop |
| Construction | Missing | **Yes** | **Preferred** | House abstraction, rooms/hotspots, furniture, servants and services |
| Farming | Missing | **Yes** | **Preferred** | Review-clock patches, growth/disease/yields/protection and Habitat dependency |
| Agility | Missing | **Yes** | **Preferred** | Course/lap abstraction without a world map; failures, energy, tickets and shortcuts |
| Dungeoneering | Missing | **Yes** | **Preferred** | Floor/session/rooms/keys/skills/combat/binds/prestige/reward architecture |
| Slayer | Missing | **Yes** | **Preferred** | Masters, assignment pools, XP, points/streaks, reward shop and Combat integration |
| Thieving | Missing | **Yes** | **Preferred** | Pickpocket/stall/chest/door loops, success/stun/damage and loot tables |
| Mining | Registered, known gaps | No | Preferred for specials | LRC, Shooting Stars, Wilderness/brawling effects |
| Woodcutting | Registered, known gaps | No | Preferred for specials | Arctic/eucalyptus/cursed methods, Wilderness effects, downstream nest uses |
| Fishing | Registered, known gaps | No | Preferred for activities | Cave eel, Trawler, Fish Flingers and Dungeoneering dependencies |
| Smithing | Registered, known gaps | No | Preferred for specials | Artisan's Workshop, Blast Furnace and Goldsmith effects |
| Crafting | Registered, known gaps | No | Helpful | Acquisition chains, Magic orb charging and temporary boosts |
| Fletching | Registered, known gaps | No | Helpful | Boosts, Barbarian unlock integration and special ammo dependencies |
| Firemaking | Registered, known gaps | No | Preferred for specials | Bonfires, pyres, beacons, Barbarian unlock and Wilderness effects |
| Cooking | Registered, known gaps | No | Preferred for specials | Karambwan/gnome families, Restaurant, gauntlets and fire/bonfire interactions |
| Runecrafting | Registered, known gaps | No | Preferred for specials | Runespan, ZMI friction, GOP, hood dailies and Abyss/rune economy |
| Hunter | Registered, known gaps | No | Preferred for specials | Tracking/pitfall/snaring, grenwall rewards, Habitat/Jadinkos and route semantics |
| Herblore | Registered, known gaps | No | Helpful | Sanfew, weapon poison use, boost decay and missing-skill/acquisition dependencies |

“No deep grill” means the current AnkiScape loop is already settled. It does not mean the remaining source work is trivial. Split-off minigames or activities still receive their own activity grills.

## Cross-system completion programs

### Quest fidelity

Keep the 194-row catalog and machine-readable stage-gate infrastructure, but audit every quest against the source standard for authentic stages, branches, transformations, combat, rewards, journals, unlocks, and missing-skill requirements. High-fidelity Darkan is especially valuable here because many hidden server transitions and combat definitions are absent from historical prose. Wait for a stable restoration milestone where the current evidence cannot close a quest safely.

### Combat, bosses, and equipment

The Combat loop is already deeply grilled, and the six partial Combat stats now have truthful registry/status semantics. Remaining work is breadth and fidelity: ordinary enemies, equipment and requirements, special attacks, degradables and set effects, full ammo/spell families, Wilderness risk, and boss/instance contexts. Fight Caves/Kiln, Barrows, God Wars, Corporeal Beast, Nex, quest bosses, and minigame enemies must stay behind their authentic activity context.

### Activities, minigames, D&Ds, and reward shops

The Utility/Activities surface and reward-shop direction are settled only at the platform level. Each activity family needs its own deep grill and source audit: entry/run state, review cost, random/event structure, currency, rewards, shop, persistence, expiry, and undo. This includes the split items already in `gap-backlog.json` and wider pre-EOC activity coverage.

### Economy and acquisition

NPC shops are live. The fake GE design is locked, but implementation remains parked until the skill/item universe is broader. Reward currencies wait for their activities. The deterministic reachability audit now exposes 267 live action-input orphans at its 2026-07-11 baseline; close them through authentic drops, spawns, shops, claims, quests, skills, activities, and transformations without disguising missing routes as fake recipe gates (`memory-bank/source-audits/item-reachability-audit-2026-07-11.md`).

### Collections and one-time content

Generic achievements and Bank Claims are live foundations. Achievement diaries, clue scrolls, collection tracking, one-time world rewards, and random events need explicit programs, source audits, and—in cases with materially different Anki abstractions—deep grills.

### Balance and release readiness

Do not perform the level-1-to-99 time pass until all skills and major methods exist. Then derive ordinary-efficient 2012 guide XP/hour envelopes and tune review pacing separately from source base XP. Release readiness also requires migration fixtures, manual Anki review QA, performance/accessibility checks, packaging/license review, recovery/export validation, and a public-versus-personal-fork decision.

## Darkan wait policy

The local Darkan checkout was observed on `dev` at `55a7afa29` during an active restoration series and 256 commits ahead of `origin/dev`. That is a moving research source, not a stable completion baseline.

Wait for a stable milestone when a card depends on hidden server probabilities, multi-stage state machines, NPC/dialogue transitions, yields/failure rolls, assignment pools, floor/room generation, activity currencies, or complex reward logic. The highest-value wait areas are:

- all wholly missing skills, especially Dungeoneering, Construction, Farming, Summoning, Slayer, Thieving, and Agility;
- quest-by-quest fidelity and unresolved quest combat definitions;
- Runespan, Bonfires, Artisan's Workshop, Blast Furnace, Shooting Stars/LRC, Fish Flingers/Trawler, GOP, and other large activities;
- bosses, instanced encounters, minigames, reward shops, and degradable/special equipment.

Do not wait for Darkan to prove client-side IDs/options/sprites that the period caches already establish, literal values already pinned in pre-EOC wikitext, or AnkiScape product decisions only the owner can make.

## Explicit exclusions and boundaries

- No standalone transportation network, world map, or persistent player location.
- No post-cutoff or OSRS-only mechanic without independent pre-EOC proof.
- No visible inert target or reward row that does not function end to end.
- No conversion of ordinary skilling reviews into wall-clock minutes; the global card clock is for world/economy cadence.
- Canoes remain excluded and the OSRS javelin-construction false positive remains rejected.

## Canonical next-step order

1. Run deep grills for the missing skills, resuming Prayer rather than restarting it; Farming and Construction are the most connected noncombat candidates, while Magic is the most advanced partial skill.
2. Continue source-complete slices from the eleven shipped-skill gap ledger without guessing conflicting values.
3. Ingest a stable Darkan restoration milestone and rerun the quest/special-activity/server-behavior audits.
4. Build missing skills and activities in dependency order, then unpark the GE when its item universe is representative.
5. Run the global 1-99 balance, acquisition/economy closure, and release-readiness programs last.
