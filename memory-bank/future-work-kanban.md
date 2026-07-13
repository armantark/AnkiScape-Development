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

### Prayer — SHIPPED 2026-07-11 (commit ed1327b)

Labels: none remaining on the build itself; trailing `DEPENDENCY` items only.

- Implemented in full from `memory-bank/ankiscape-skill-expansion.md`: bury/scatter/Ectofuntus/hosted-gilded methods, the EV prayer/curse combat translation with the uptime policy, prayer points/drain, the named combat preset system with per-target pins (storage v29), and the Knight Waves landmark. Verified at 1,016 pure + 1,016 offscreen Qt tests.
- Trailing `DEPENDENCY` items: Shades of Mort'ton cremation and GE bones on their own families; owned-POH altars and burners on Construction (the Construction grill has since settled the burner rule: clean marrentill consumed per burner, no finding roll for an owned house).
- The implementation report's conservative calls (pinned Rapid Renewal 65/230 over the emulator, no Ancient bonemeal, renewal gradual formula omitted as unproven) are recorded in the results artifact.

### Magic — SHIPPED 2026-07-11 (commit 24fbafd)

Labels: none remaining on the build itself; trailing `DEPENDENCY` items only.

- Implemented in full from `memory-bank/magic-skill-contract-2026-07-11.md`: 94 noncombat targets across all three spellbooks, uncapped 40%/60% alchemy with staff substitution, the combat roster gap-fill (god spells behind the five-review Mage Arena landmark, all 16 ordinary Ancients, four Miasmics), preset-schema extension for spellbook/autocast/Vengeance/Dream/Swap (storage v30), and the curated three casual controls. Verified at 1,031 pure + 1,031 offscreen Qt tests.
- Charge orbs closed the reachability audit's elemental-orb orphan category; telegrab ships as the authentic Wine of Zamorak route.
- Trailing `DEPENDENCY` items: Livid Farm spell set (its own activity card), Cure Plant / Fertile Soil real function (Farming), Plank Make consumers (Construction — closed by the Construction ship), Hunter Kit consumers (Hunter), Slayer staff acquisition (Slayer), Bones to Peaches behind a future Mage Training Arena activity.

### Construction — SHIPPED 2026-07-11 (commit c628f0d)

Labels: none remaining on the build itself; trailing `DEPENDENCY` items only.

- Implemented in full from `memory-bank/construction-skill-contract-2026-07-11.md`: 544 targets (all 447 Darkan HouseObjects builds, 82 wiki-pinned flatpacks, 15 lectern tablets awarding Magic XP), the v31 house sheet (1,000-coin rung-zero purchase granting Garden + Parlour, room ladder, servants as wage-paid batch boosts 6/10/16/20/26, seven house styles), the owned gilded-altar Prayer variant (no finding roll, one marrentill per lit burner per stint, 350% max), the crystal saw +3 behind The Eyes of Glouphrie, teak/mahogany sawmill tiers, and the limestone-brick Crafting row. Verified at 1,050 pure + 1,050 offscreen Qt tests.
- `construction_data.py` is generated byte-reproducibly by `tools/generate_construction_data.py` from the pinned Darkan checkout (`7e7d67b`) — line count is not a completeness signal.
- Conservative calls: nail bend rates are an era-compatible 2009scape numeric gap-fill (the pre-EOC pins are qualitative only, cited per row); two Darkan typos corrected with citations (TEAKTOYBOX level 968 → 68, Fremennik style 20,000 → 25,000, both also in the restoration handoff).
- Trailing `DEPENDENCY` items: Menagerie pet function (pet system), whetstone/armour-stand repairs (equipment degradation), consumable-producing builds whose outputs stay orphaned until their systems exist, and spicy stew on the RFD/Evil Dave side.

## Deep-grill queue — missing or incomplete skill surfaces

Each skill receives its own grill before implementation. Source-shaped facts should be resolved autonomously; grill only materially different AnkiScape choices.

### Farming — grill CLOSED 2026-07-11

Labels: `SOURCE AUDIT` (the 38-pin wiki gate), then `IMPLEMENT`.

- The contract is `memory-bank/farming-skill-contract-2026-07-11.md`; the source dossier is `memory-bank/source-audits/farming-source-dossier-2026-07-11.md`. Do not re-grill.
- Settled: review-ticked clock (240 answered cards = 24 h; failures tick), pure background archetype (no target list; queued 1-review detours preempt the active skill; harvest-and-replant-same shortcut), owner-approved verb cost table, full-parity GM disease with unattended death, full Nov-2012 location-gated patch map, all authentic seed routes, no auto crop suggestions.
- Remaining before build: resolve the dossier's 38 wiki pins (fruit-tree check XP, calquat timing, allotment payments, jute seeds, white lily, plant-cure XP, specials, patch inventory), the seed-source audit, and storage v32.
- Absorb `hunter-habitat-jadinko` only after the core Farming build lands (Habitat patches ship live but seed-starved until then).
- Magic-grill handoff (owner-mandated): Cure Plant and Fertile Soil ship now as pure casts; when Farming lands they must gain real function (e.g. a farming-run option/checkbox), not stay ceremonial. See `memory-bank/magic-skill-contract-2026-07-11.md` decision 9.

### Agility

Labels: `DEEP GRILL`, `WAIT: DARKAN`, `SOURCE AUDIT`.

- Abstract courses as checkpoint/lap state without player location; decide failures/damage, tickets/rewards, run-energy benefits, shortcuts as dependency gates, equipment, and UI.

### Thieving — grill IN PROGRESS 2026-07-13

Labels: `DEEP GRILL` (closing), `SOURCE AUDIT`.

- Owner-settled so far: full-parity failure stake (a failed attempt costs the review, applies sourced damage to the shared combat lifepoint pool, and stuns, so the next review only clears the stun); a Thieving-scoped food loadout on the existing `combat_supply_loadout` substrate; a single "Fight back when caught" toggle (default off) governing both stall guards and blackjack thugs, where unchecked means you flee for one round of damage and checked means a real combat encounter; three casual controls total; targets are ordinary target rows like every other skill.
- Scope: five engine-native loops — pickpocketing, stalls, chests, wall safes, blackjacking. Doors pending the source dossier.
- **Pyramid Plunder is EXCLUDED from the skill** and belongs to the Activities program: it grants Strength and Runecrafting XP, gates on a Strength level, spawns a combat NPC, and sells artefacts for up to 12,500 coins (`PyramidPlunder.kt:110-147`, `SimonTempleton.kt:48-61`). Sorceress's Garden, the Rogues' Den maze, and the Thieves' Guild go with it. The Rogues' Den *wall safes* are separable and do ship.
- The Feud ships with this build (gates blackjacking). Dorgesh-Kaan chests and Lletya elves ship gated and dark behind their quests.
- Blocked rewards: rogue outfit (×1.025 XP, Rogues' Den maze only) and Ardougne cloak (achievement diaries). Both listed on their owning cards.
- Source dossier in flight: `memory-bank/source-audits/thieving-source-dossier-2026-07-13.md`. Open question it must close: whether stalls have a per-attempt caught roll at all, and whether the *stall owner* can call you out independently of guards.

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

### 167 missing playable quests, plus fidelity for the 27 that exist

Labels: `WAIT: DARKAN`, `SOURCE AUDIT`, `IMPLEMENT`.

- Sized honestly 2026-07-13: `quest_catalog_generated.py` carries all 194 pre-cutoff quests as metadata, but `quest_data.py` defines only **27 playable** `QuestDefinition`s. The other 167 exist as catalog rows and, in some cases, as loose id constants plus stage fragments — which reads like the quest is present when it is not. The Feud (`quest_data.py:84`), Death to the Dorgeshuun, and Mourning's End Part I are all in that half-present state.
- Two distinct workstreams, do not conflate them: **build the 167 missing definitions**, and **re-audit the 27 that exist** for authentic stages, branches, item transformations, combat, rewards, journals, unlocks, and missing-skill gates.
- Prioritise by what a quest unblocks. Skill grills surface these: Thieving alone needs The Feud (blackjacking), Death to the Dorgeshuun (Dorgesh-Kaan chests), and Mourning's End Part I (Lletya elves).
- The Feud is being built as part of the Thieving expansion because it gates a core training method; it is the precedent, not an exception to the queue.
- Wait for Darkan where historical sources cannot prove hidden transitions or combat definitions; never fill gaps from modern RS3/OSRS.

### Complete pre-EOC bestiary

Labels: `SOURCE AUDIT`, `IMPLEMENT`, `WAIT: DARKAN`.

- Sized honestly 2026-07-13: `COMBAT_ENEMY_DATA` holds **130 enemies**; Darkan ships roughly **2,600 NPC combat definitions** under `data/npcs/combatdefs/`. Every attackable pre-cutoff NPC should exist.
- This was previously only a bullet under the Combat card ("continue enemy breadth"), which badly understated it.
- Skill work keeps discovering holes here — Thieving needs `market_guard` (present) for stall guards and the Menaphite thug (absent) for blackjacking, and Slayer will need the task-only roster wholesale.
- Source from Darkan combatdefs reconciled against the dated caches for NPC identity/options, then a pinned wiki revision for levels and drops.

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
- **Content gap found by the XP/hour audit (2026-07-13): barehand butterfly catching is missing.** Hunter's `catch_black_warlock` implements only the butterfly-**net** variant (54 XP). The period game also has **barehand** catching at Hunter 95 for **650 XP/catch**, which the 2012 guide rates at **140,000 XP/hr** — the best Hunter training in the game (Hunter training, oldid 6549266). So the skill's actual endgame method does not exist here. Found because grading the net variant against the barehand rate produced a phantom inversion; see `memory-bank/source-audits/xp-hour-provenance-ledger-2026-07-13.md`. Expect the same class of gap wherever a skill's best period method is missing — the audit surfaces them for free.

### Achievement diaries, clues, collections, and one-time content

Labels: `DEEP GRILL`, `SOURCE AUDIT`, `WAIT: DARKAN` where server state is hidden.

- Build from generic achievements and Bank Claims; add diary regions/tasks/rewards, clue step/casket state, collection tracking, one-time rewards, and their UI/undo contracts.
- **Grill seed (owner, 2026-07-13):** the owner has a rudimentary idea for diary rewards built on our existing *fabricated* achievements, which have no source backing. That tension — invented achievement tasks handing out authentic pre-cutoff reward items — is the central thing the grill has to resolve, and it cannot be resolved by sourcing alone.
- `memory-bank/achievement-diary-item-grants-design.md` is still a stub. Until this grill closes, diary reward items have no acquisition route and must not ship.
- **Blocked on this card:** the Ardougne cloak's Thieving bonus (Darkan gives +0.1 to the blackjack knock-out roll). Switch it on when diaries land rather than rediscovering it.

### Random events and timed world content

Labels: `DEEP GRILL`, `WAIT: DARKAN`, `SOURCE AUDIT`.

- Use the global 240-reviews-per-day clock for world/economy cadence only.
- Decide visibility, opt-in/interrupt behavior, expiry, missed events, rewards, persistence, and undo without adding a world map.

## Parked sequencing gates

### Grand Exchange

Labels: `PARKED`, `DEPENDENCY: SKILL/ITEM BREADTH`.

- Core design is locked in `memory-bank/fake-grand-exchange-design.md`; do not re-grill it.
- NPC shops are already live. Implement the GE after the skill/item universe is representative enough that prices, limits, and acquisition softness are meaningful.

### Level 1-99 time and economy balance — the XP/hour invariant

Labels: `PARKED`, `DEPENDENCY: ALL SKILLS/MAJOR METHODS`.

**The invariant (owner-stated 2026-07-13).** One review is one unit of game
time, so the quantity that must hold across the whole game is:

```
effective XP per review  ∝  real pre-EOC XP per hour
```

Not XP per action. AnkiScape pays per review and therefore inherits XP-per-action
unless something corrects it, but XP/hour is what Jagex actually balanced.

**MEASURED, 2026-07-13.** This is no longer a hypothesis. `tools/xp_rate_audit.py`
grades the *shipped* probability functions against pinned pre-EOC rates. Full
analysis: `memory-bank/source-audits/xp-hour-provenance-ledger-2026-07-13.md`.
Regression tests: `tests/test_xp_hour_parity.py` (3 `expectedFailure`s pinning the
defects; they turn the suite red the moment they're fixed, forcing removal).

**There are TWO independent defects, and a skill can have either alone.**

| Defect | Breaks | Cause | Victims |
|---|---|---|---|
| Invented adapter | *ordering* | `0.20 + 0.72·√p` (`logic_pure.py:388`) inflates rare actions | Woodcutting, Fishing (Mining directionally) |
| Unmodelled dead time | *rate* | one review per action, whatever the real wait | Hunter (traps), Thieving stalls (respawn), Combat (30s burst) |

*Adapter.* Its damage scales with how rare the action is: near `p=1` the square
root is nearly the identity, but a 6.3% action becomes 38%. In RuneScape a rare
action is the signature of a **money** method — that is why it was made rare — so
the adapter promotes exactly the content the period game made unattractive to
train. Magic logs are our 2nd-best Woodcutting method and 2012's 2nd-worst.
Sharks are our 3rd-best Fishing method and 2012's *worst* ("only 20k experience
per hour"). Hunter and Cooking escape only because their rolls sit near certainty.

*Dead time.* Already shipped, in **Hunter** — trap catches make you wait, and we
charge one review per catch and ignore the wait. Hunter's ordering looks fine,
which is why nobody noticed; its *rate* is 2–4× too generous. This was previously
believed to be a Thieving-only problem that Thieving would be first to hit. It is
not.

*Combat.* Its `R` is a **definition, not a measurement**: 50 ticks/review = 30s =
120 reviews/hour. Every other skill *derives* R from a sourced rate and lands near
1,000–1,475. So one combat card buys **5.5×–8.6×** more game time than a Mining
card. The engine itself is faithful (moss giants at 50 ticks/review yield ~37k
XP/hr, a plausible period rate) — it is the *review conversion* that is wrong.
**This cannot be fixed later by lowering XP**, because XP/action is frozen by the
parity contract. Cadence is the only lever.

**Do NOT naively model respawn as the fix.** `XP ÷ respawn` makes the level-2
vegetable stall the best XP in Thieving and the level-75 gem stall the worst —
the period E.P.S. column confirms the single-stall rates really do invert, because
real players world-hop rather than wait.

**Remaining deliverables:**
- Sourced XP/hour + modifier provenance for the artisan skills (Smithing, Crafting,
  Fletching, Runecrafting, Herblore, Construction, Magic, Prayer).
- Preserve source base XP throughout. The correction always rides cadence or an
  explicitly-recorded invention, **never** the XP value.
- Every rate must declare what is baked into it (urns, gauntlets, familiars,
  dropping). The F2P Mining guide quotes iron at 45k *with urns*; contract on that
  and grant urns again and you land at 54k.

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
