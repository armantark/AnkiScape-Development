# AnkiScape Completion Kanban

Status: reconciled 2026-07-16. This is the canonical forward-work board. The 2026-07-10 completion audit is archived baseline evidence; the shipped-skill subledger remains `memory-bank/gap-backlog.json`.

## Label contract

- `DEEP GRILL`: owner-facing loop/UI/abstraction decisions remain.
- `SOURCE AUDIT`: design is settled, but pre-cutoff mechanics or values are incomplete/conflicting.
- `WAIT: DARKAN`: a stable high-fidelity restoration would materially reduce hidden-server guesswork; historical reconciliation still applies.
- `IMPLEMENT`: design and evidence are sufficient for a bounded backend/frontend/assets/tests slice.
- `DEPENDENCY`: another skill, activity, acquisition route, or economy surface must land first.
- `PARKED`: deliberately sequenced later, not forgotten.
- `EXCLUDED`: outside the product/cutoff boundary.

## Now — audit-backed implementation and source work

### Owner-approved post-closure amendments

Labels: none. All approved amendments and their two follow-up design questions
are now live.

Completed 2026-07-17:

- Magic Charge now uses the shared review-driven temporary-effect clock, scales
  with Actions per Review, dissipates during safe non-combat activity, and
  never reads wall time.
- Bank now provides direct-undoable `Discard X` and stack-aware absolute
  carried-quantity editing while preserving the Custom-pack queue order.
- Agility target packs carry course requirements and real food, share the
  grave/death/undo path, and resolve the bounded Wilderness PKer abstraction.
- Farming provides explicit one-review `Dig up`, user-authored whole-farm
  presets, inert application, gardener-payment escrow, and reported full-run
  skips.
- Mage Arena now grants one chosen god loadout, exposes collapsed per-spell
  attunement and one-cape statue actions, and makes Charge's matching-loadout
  +100 LP god-spell effect real.
- Farming presets now store a compact item-first/spell-first cure preference
  and use the other route as an execution-time fallback.

The resolved question ledgers are preserved at
`memory-bank/archive/2026-07/resolved-queues/design-gaps-overnight-2026-07-16.md`
and
`memory-bank/archive/2026-07/resolved-queues/design-gaps-grill-harvest-2026-07-17.md`.

### Existing-skill parity ledger

Labels: `SOURCE AUDIT`, then `IMPLEMENT` only when evidence closes.

- Continue from `memory-bank/gap-backlog.json`; do not reconstruct merged cards or re-grill settled branches.
- Current detailed state: 22 merged, 13 design/source-blocked waits (including Grenwall), four split-scope, one Farming seed, one partially reopened/source-waiting, two exclusions, one design-partial/source-waiting card, and one design-settled parent-decision card.
- Grenwall's pinned period revision proves its broad reward family but not exact spike/herb probabilities; it now explicitly waits on literal period evidence or a stable reconciled Darkan milestone (`memory-bank/source-audits/grenwall-reward-source-closure-2026-07-11.md`).
- The next implementation slice must have a pinned pre-EOC contract for its level, XP, inputs, outputs, gates, rates, and state transitions. Split proven sub-slices from blocked families as lava eel, Overload, and cannonballs already demonstrate.
- Backend acceptance: data, pure behavior, storage/migration, dispatch, acquisition semantics, telemetry, and undo.
- Frontend acceptance: `TargetRowMetadata`, real enablement/locks, target-local settings/equipment/inventory, icons, tooltips, and offscreen Qt coverage.
- Assets acceptance: period-appropriate art, explicit `--source rs3` where applicable, provenance, and path tests.

### Reconcile partial Combat skills with the skill ledger — status contract complete

Labels: `SOURCE AUDIT`, `IMPLEMENT`, `WAIT: DARKAN` for hidden enemy/equipment behavior.

- Attack, Strength, Defence, Constitution, and Ranged use an explicit `partial` surface state with `training_source = Combat`; Magic is now a complete surface.
- Keep unified Combat selection; do not add five competing hub rows merely to make the registry count look complete.
- Quest gates and XP rewards now recognize trainable partial stats, and legacy pending Combat-stat XP migrates directly. See `memory-bank/source-audits/partial-combat-skill-registry-2026-07-11.md`.
- Continue weapon/ammo/spell/equipment/enemy breadth under `memory-bank/combat-design-grill-2026-06-23.md` rather than reopening the Combat loop design.

### Prayer — SHIPPED 2026-07-11; altar/urn/passive closure 2026-07-13

Labels: none remaining on the build itself; trailing `DEPENDENCY` items only.

- Implemented in full from `memory-bank/ankiscape-skill-expansion.md`: bury/scatter/Ectofuntus/hosted-gilded methods, the EV prayer/curse combat translation with the uptime policy, prayer points/drain, the named combat preset system with per-target pins (storage v29), and the Knight Waves landmark. Verified at 1,016 pure + 1,016 offscreen Qt tests.
- The 2026-07-13 closure completes owned-POH altar runtime/UI at 250/300/350%, all 26 training-urn tiers, target-carried Bonecrusher/Ectoplasmator behavior, direct full-urn teleport with independent LIFO undo, and exact high-tier standard-Prayer Defence gates. See `memory-bank/source-audits/prayer-altar-urn-passives-herblore-closure-2026-07-13.md`.
- Trailing `DEPENDENCY` items: Shades of Mort'ton cremation and GE bones on their own families; Bonecrusher/Ectoplasmator acquisition remains intentionally absent until authentic owning activities exist.
- The implementation report's conservative calls (pinned Rapid Renewal 65/230 over the emulator, no Ancient bonemeal, renewal gradual formula omitted as unproven) are recorded in the results artifact.

### Magic — SHIPPED 2026-07-11 (commit 24fbafd)

Labels: none remaining on the build itself; trailing `DEPENDENCY` items only.

- Implemented in full from `memory-bank/magic-skill-contract-2026-07-11.md`: 94 noncombat targets across all three spellbooks, uncapped 40%/60% alchemy with staff substitution, the combat roster gap-fill (god spells behind the five-review Mage Arena landmark, all 16 ordinary Ancients, four Miasmics), preset-schema extension for spellbook/autocast/Vengeance/Dream/Swap (storage v30), and the curated three casual controls. Verified at 1,031 pure + 1,031 offscreen Qt tests.
- Charge orbs closed the reachability audit's elemental-orb orphan category; telegrab ships as the authentic Wine of Zamorak route.
- The 2026-07-17 follow-up completes Mage Arena alignment/rewards/attunement,
  god-cape equipment and assets, and Charge's real matching-loadout combat
  effect. Cure Plant is also live as a Farming preset fallback route.
- Trailing `DEPENDENCY` items: Livid Farm spell set (its own activity card), Hunter Kit consumers (Hunter), Slayer staff acquisition (Slayer), Bones to Peaches behind a future Mage Training Arena activity.

### Construction — SHIPPED 2026-07-11 (commit c628f0d)

Labels: none remaining on the build itself; trailing `DEPENDENCY` items only.

- Implemented in full from `memory-bank/construction-skill-contract-2026-07-11.md`: 544 targets (all 447 Darkan HouseObjects builds, 82 wiki-pinned flatpacks, 15 lectern tablets awarding Magic XP), the v31 house sheet (1,000-coin rung-zero purchase granting Garden + Parlour, room ladder, servants as wage-paid batch boosts 6/10/16/20/26, seven house styles), the owned gilded-altar Prayer variant (no finding roll, one marrentill per lit burner per stint, 350% max), the crystal saw +3 behind The Eyes of Glouphrie, teak/mahogany sawmill tiers, and the limestone-brick Crafting row. Verified at 1,050 pure + 1,050 offscreen Qt tests.
- `construction_data.py` is generated byte-reproducibly by `tools/generate_construction_data.py` from the pinned Darkan checkout (`7e7d67b`) — line count is not a completeness signal.
- Conservative calls: nail bend rates are an era-compatible 2009scape numeric gap-fill (the pre-EOC pins are qualitative only, cited per row); two Darkan typos corrected with citations (TEAKTOYBOX level 968 → 68, Fremennik style 20,000 → 25,000, both also in the restoration handoff).
- Trailing `DEPENDENCY` items: Menagerie pet function (pet system), whetstone/armour-stand repairs (equipment degradation), consumable-producing builds whose outputs stay orphaned until their systems exist, and spicy stew on the RFD/Evil Dave side.

## Deep-grill queue — missing or incomplete skill surfaces

Each skill receives its own grill before implementation. Source-shaped facts should be resolved autonomously; grill only materially different AnkiScape choices.

### Farming — SHIPPED 2026-07-13 (commit 9a88c56)

Labels: none remaining on the core build; trailing acquisition/activity dependencies only.

- Implemented from `memory-bank/farming-skill-contract-2026-07-11.md` and the resolved source dossier: review-ticked clock, queued one-review field detours, full disease/death/growth state, the pre-EOC patch map, protection/compost/juju behavior, source-blocked rows, HUD, storage, and Qt sheet.
- Cure Plant and Fertile Soil now have real Farming function rather than ceremonial casts.
- The replacement/preset amendment shipped at `9b65f45`: healthy mature
  regrowers can be dug up explicitly; differing full-run plans queue removal
  then planting; whole-farm presets snapshot selected plan policies without
  consuming goods; and gardener payments are escrowed by the queued planting
  step with refund on removal, clearing, or execution skip.
- The 2026-07-17 cure-policy follow-up adds a compact per-patch item-first or
  spell-first preference, persists it in presets and queued steps, and uses the
  canonical Cure Plant Magic transaction as the fallback route.
- `hunter-habitat-jadinko` remains an owning-activity/acquisition follow-up; core Farming is no longer its dependency.

### Agility — SHIPPED 2026-07-15

Labels: trailing `SOURCE AUDIT` and owning-system dependencies only.

- The atomic build in `memory-bank/agility-skill-contract-2026-07-15.md` is live:
  every audited course and activity, obstacle failures/LP/setbacks, Brimhaven,
  68 ordinary/grapple shortcuts, run-energy/actual-load travel, rewards and
  boosts, live cross-skill hooks, storage/undo, achievements, grouped Qt UI, and
  period-provenanced assets.
- Answered cards and Agility actions are the only cadence inputs. Agility
  gameplay modules have a static no-wall-clock regression test.
- Remaining dependency owners: Summoning familiars, Slayer routes,
  Daemonheim/Dungeoneering, full Blast Furnace, Livid Farm, diary acquisition,
  Barbarian Assault, and quest-owned stages. They have stable ownership
  boundaries but no fake partial implementation.
- Exact payout differences among the registered Dorgesh pure/grapple/mixed
  route identities remain `source_blocked`. See
  `memory-bank/source-audits/agility-implementation-verification-2026-07-15.md`.

### Thieving — SHIPPED 2026-07-13

Labels: trailing `SOURCE AUDIT` and owning-activity dependencies only.

- Core skill closure is implemented on `main` (merged at `63b0a28`): 17 pickpocket
  rows, all 18 2011Scape stall-family rows, wall safe, Menaphite blackjacking,
  shared LP/stun/fight-back, storage v35, grouped Qt surface, assets, and exact
  live cadence. See `memory-bank/source-audits/thieving-tables-2026-07-13.md`.
- Remaining source debt: Dorgesh-Kaan chests, Lletya elf, Pirates' Hideout, and
  incomplete blackjack variants. Activities exclusions and rogue/Ardougne
  rewards remain on their owning cards.

- Owner-settled so far: full-parity failure stake (a failed attempt costs the review, applies sourced damage to the shared combat lifepoint pool, and stuns, so the next review only clears the stun); a Thieving-scoped food loadout on the existing `combat_supply_loadout` substrate; a single "Fight back when caught" toggle (default off) governing both stall guards and blackjack thugs, where unchecked means you flee for one round of damage and checked means a real combat encounter; three casual controls total; targets are ordinary target rows like every other skill.
- Scope: five engine-native loops — pickpocketing, stalls, chests, wall safes, blackjacking. Doors pending the source dossier.
- **Pyramid Plunder is EXCLUDED from the skill** and belongs to the Activities program: it grants Strength and Runecrafting XP, gates on a Strength level, spawns a combat NPC, and sells artefacts for up to 12,500 coins (`PyramidPlunder.kt:110-147`, `SimonTempleton.kt:48-61`). Sorceress's Garden, the Rogues' Den maze, and the Thieves' Guild go with it. The Rogues' Den *wall safes* are separable and do ship.
- The Feud ships with this build (gates blackjacking). Dorgesh-Kaan chests and Lletya elves ship gated and dark behind their quests.
- Blocked rewards: rogue outfit (×1.025 XP, Rogues' Den maze only) and Ardougne cloak (achievement diaries). Both listed on their owning cards.
- Source dossier: `memory-bank/source-audits/thieving-source-dossier-2026-07-13.md`.
- **Owner-settled 2026-07-13 (grill round 2):**
  - **Ship 2011Scape's pickpocket table wholesale**, pinned `provisional/2011Scape`, including the rows OSRS cannot referee (Paladin, Gnome, Hero — all invalidated by OSRS's May-2024 "Project Rebalance: Skilling"). Cherry-picking Darkan only where the referee is absent would select the source by convenience. The cost of being wrong is small: the two tables agree *exactly* at level 99 on eight of ten rows, and the worst disagreement at any reachable level is 11pp (Rogue), 3.9pp for the Paladin.
  - **The dossier's `x/y` chance notation is NOT a fraction.** It is `minChance`/`maxChance` — the level-1 and level-99 endpoints of `interpolate(min, max, 1, 99, ceiling=255)` (`PickpocketTarget.kt: fun roll`). The ceiling is 255 for *every* target: one roll shape, not one per denominator. Reading endpoints as fractions manufactures phantom conflicts.
  - **~~Stall catching gets ONE global invented constant~~ — SUPERSEDED, see below.** The stall catch chance is **zero**, and nothing is invented.
  - **Multi-pickpocket and stun/damage**: 2011Scape's values (`random(7) == 1` with the +10/+20/+30 Thieving and +0/+10/+20 Agility overshoot gates, which the period wiki corroborates over Darkan's `getRandomInclusive(50) < 5`).
  - **Pompous Merchant ships** — on the pinned 2012 wiki page's authority (level 1, 8 XP, 3 coins, stun, 10 LP), not Darkan's. The caches' missing `Pickpocket` option is recorded as a conflict, not a veto.
  - **Desert Phoenix is NOT a Thieving target.** Both caches show `Grab-feather`; 2011Scape has it only as a spawn, absent from the pickpocket table; the pinned page states no Thieving level. Darkan alone calls it Thieving. It ships as a **Utility activity** yielding one Phoenix feather, gated on The Golem, with no Thieving level and **no XP** — the wiki's "26 XP" never names a skill, and only Darkan claims Thieving.
  - **Pirates' Hideout chest parks.** Its XP is `?` in the period record itself. Sol to hunt a pre-cutoff value while extracting the tables; ships only if one surfaces.

- **Owner-settled 2026-07-13 (grill round 3) — stalls need no invented constant at all:**
  - **Stall catch chance is ZERO.** 2011Scape calls `handleSuccess` with no roll in front of it (`Stalls.kt:33`); the only failure path is `caughtByGuard`, which is purely positional (`it.sees(player, 8)`, `Stalls.kt:65`) and applies to just two of sixteen stalls — Draynor's wine (`StallTarget.kt:157`) and seed (`:188`), both Market Guard 2236. Every other row carries `guards = listOf()` and cannot fail. AnkiScape has no location layer, so the guard cannot be modelled; zero is the *faithful* value, not a shortcut.
  - **The restock timer alone reproduces the sourced XP/hour, with no free parameters.** 2011Scape's `respawnTicks` and the 2012 wiki's experience-per-second column (pinned in `tools/sourced_xp_rates.py:90-95`) are the same numbers, derived independently and never in contact:

    | stall | lvl | xp | respawnTicks | implied xp/hr | wiki E.P.S. × 3600 |
    |---|---|---|---|---|---|
    | Vegetable | 2 | 10 | 3 (1.8s) | 20,000 | 18,000 |
    | Baker | 5 | 16 | 3 (1.8s) | 32,000 | 23,040 |
    | Silk | 20 | 24 | 8 (4.8s) | 18,000 | 10,800 |
    | Silver | 50 | 54 | 50 (30s) | **6,480** | **6,480** |
    | Spice | 65 | 81 | 133 (79.8s) | 3,654 | 3,600 |
    | Gem | 75 | 160 | 300 (180s) | 3,200 | 3,240 |

    The three high-level rows agree to within rounding. Any nonzero catch constant would push every stall *below* its own sourced rate — reintroducing the exact defect the cadence kernel exists to fix. This is the strongest corroboration in the Thieving record; the earlier "invent one global constant" decision was solving a problem that does not exist.
  - **The wall safe is the exception that proves it.** It is the only stall-family row carrying chance endpoints (`lowChance = 8, highChance = 160`, `StallTarget.kt:263-264`) — the same interpolate-against-255 shape as pickpocketing — and the only one whose 100%-success rate (70 xp / 3s = 84,000/hr) overshoots its sourced ceiling (~20,000/hr). It fails because the period game meant it to, and the source states by how much. Ship those endpoints. Note the fields are declared but unused in `Stalls.kt` — 2011Scape carried the data and never wired it.
  - **Ship the level inversion honestly.** The level-5 baker stall out-earns the level-75 gem stall by ~7×, in both sources. That is authentic: pre-EOC players camped gem stalls for the *gems*, and the wiki's own escape hatch — "ideal to world hop" — is a location mechanic AnkiScape cannot model. It is safe to ship because the bad option is never the best available one: at 75 Thieving the player already has knights of Ardougne (180,000/hr, `sourced_xp_rates.py:82`) and blackjacking (200,000–270,000/hr, `:75`). The gem stall's poor XP is the *price* of its loot table, which we do model, and that reads as a choice rather than a trap. Do **not** invent a world-hop abstraction to "fix" it.

### Phoenix feather acquisition — CLOSED

Labels: none remaining.

The live Desert Phoenix `Grab-feather` Utility activity supplies Phoenix feathers
after The Golem and makes the Super antifire chain obtainable. The route is
independent of Thieving XP even though it was discovered during the Thieving
grill.

### Slayer

Labels: `DESIGN CLOSED`, `WAIT: DARKAN`, `SOURCE AUDIT`, `DEPENDENCY: COMBAT/QUESTS/ACTIVITIES`.

- Reuse existing enemy Slayer metadata; add masters, assignment pools, XP, task progress, points/streaks, skips/blocks, reward shop, task-only targets, protection items, and Combat UI.
- Source sweep progress: Turael/Spria is reconciled at 23 families with a
  provisional 355-point denominator; Mazchna/Achtryn is reconciled at 27
  families with a provisional 325-point denominator; Vannaka is reconciled at
  35 families with a provisional 460-point denominator; Chaeldar is reconciled
  at 34 families with a provisional 388-point denominator; Sumona is reconciled
  at 37 families with a provisional 407-point denominator; Duradel/Lapalok are
  reconciled at 35 families with a provisional 334-point denominator; Kuradal
  is reconciled at 36 families with a provisional 322-point denominator. All
  seven roles remain hidden until their full Combat families and distinctive
  protection/finishing/context mechanics are executable. See the dated
  `slayer-turael-spria-pool`, `slayer-mazchna-achtryn-pool`,
  `slayer-vannaka-pool`, `slayer-chaeldar-pool`, `slayer-sumona-pool`, and
  `slayer-duradel-lapalok-pool` audits, plus `slayer-kuradal-pool`.
- The bounded 2026-07-17 harvest is closed. Resume from the per-family blocker
  identities in those audits; do not reopen the owner design or expose a
  partial master. The remaining program is implementation-time source audit
  plus Combat, quest, location, reward, and activity dependency work.
- Park Social Slayer unless genuine shared-player state ever exists; do not ship
  a simulated partner or solo co-op multiplier. Preserve all seven period Slayer
  master challenges in the design and source their compound objective ledgers.
- Add an explicit `Get assignment` master picker and make its NPC identity
  quest-reactive: Turael to Spria and Duradel to Lapalok after While Guthix
  Sleeps, with Achtryn replacing Mazchna only during the quest interval.
- Keep every period master role visible in the picker; disable ineligible rows
  and state their unmet combat, Slayer, quest, and activity requirements.
- Build the complete cutoff reward/unlock ledger. Required finishing items must
  gate rockslugs, desert lizards, zygomites, and gargoyles; the 400-point quick
  killing-blow unlock automates the finisher without removing the item check.
- Preserve the ring of slaying's eight-charge transport value by letting one
  charge erase a qualifying Slayer destination's abstract run-energy entry
  cost; do not add map state, travel reviews, or wall-clock delay.
- Represent only mechanically distinct Slayer areas as target-local Combat
  contexts, including Kuradal's Dungeon; collapse cosmetic duplicate locations.
- Keep Slayer management inside one Skills page with `Assignment`, `Masters`,
  and `Rewards` subviews; reuse shared search and deep-link into Combat rather
  than opening nested dialogs or duplicating the fight picker.
- Build `Smoking Kills` and every still-incomplete prerequisite quest definition
  in the Slayer program so Sumona, reward points, and the Rewards subview are
  genuinely reachable; feed those quests through the canonical missing-quest
  backlog and runtime rather than adding flags or bypasses.
- Build Shilo Village and the complete transitive Slayer-helmet route through
  Cabin Fever, Mos Le'Harmless, Cave horrors, the black-mask drop, and the
  400-point crafting unlock. Preserve every period quest and skill prerequisite;
  in particular, this route depends on the real Agility implementation rather
  than a Slayer-local waiver.
- Keep cutoff-live assignment families in the completeness ledger but do not
  render implementation-missing families as locked or coming-soon rows. Derive
  runtime readiness from stable dependency identities so each family enters the
  live UI and authentic weighted roll automatically when its quest, target,
  context, acquisition, and unlock dependencies are genuinely implemented. Add
  a completeness audit that names every blocking identity, rejects stale
  blockers, prevents empty rollable-master pools, and applies the same rule to
  family-specific reward purchases.
- Certify each Slayer master only after every ordinarily available family in its
  pinned cutoff pool has complete roll data and satisfies the owner-set variant
  coverage bar. Never ship a master whose baseline weights are silently
  renormalized around implementation gaps; apply authentic quest, reward,
  block-list, and other player-specific exclusions only after baseline
  certification. Optional special challenges do not block the ordinary pool;
  gate each offer on its own complete runtime readiness.
- Certify a baseline family once its roll data and one ordinarily available,
  end-to-end qualifying Combat variant are ready. Keep every remaining cutoff
  variant pinned and audit-visible but absent from player UI until its stable
  dependencies activate it automatically. If live variant breadth becomes hard
  to scan, allow expandable family-to-variant grouping inside the existing
  Combat picker; exact variants remain the only selectable targets. Inherently
  player-gated families certify only through their complete authentic gate chain,
  and every certifying variant must include its special kill/protection mechanics.
- Preserve sourced unprotected-combat consequences for Slayer protective gear
  and warn without blocking legal dangerous encounters. Hard-gate only literal
  source access/attack restrictions, and pin every family item's trigger,
  consequence, immunity, death/retreat behavior, and undo interaction in a
  focused audit before implementation.
- Cockatrice is the first completed protective-equipment slice: an equipped
  Mirror shield suppresses its source-reconciled fixed hit and stat drain, while
  the unprotected target remains legal and visibly warned. Banshee's item set
  and affected stats are pinned, but its conflicting drain magnitude and
  current Summoning-scope dependency keep that family unimplemented. See
  `source-audits/slayer-protective-equipment-cockatrice-banshee-2026-07-17.md`.
- Finisher-item acquisition metadata is now ready: Bag of salt, Rock hammer,
  Ice cooler, and Fungicide spray retain their source item IDs and real
  stackability in the shared registry. The four target families remain
  source-blocked on reconciled Combat rows, context-correct drops, and enemy
  assets; do not add a dead generic finisher engine ahead of a certifiable
  family. See `source-audits/slayer-finishing-blows-2026-07-15.md`.
- Complete the design-closure source sweep without reopening owner questions for
  source-determined behavior: close every per-master pool/weight/count/gate row,
  pin every family variant's membership/stats/Slayer-XP eligibility/context, and
  close protective, special-kill, challenge, and context state transitions.
- Turael/Spria's first pool pass is recorded in
  `source-audits/slayer-turael-spria-pool-2026-07-17.md`: 23 families and the
  provisional 355-point hidden-weight denominator are pinned, but the role
  remains runtime-blocked on six absent Combat families plus Banshee and
  Gelatinous special consequences. Mazchna/Achtryn, Vannaka, Chaeldar, and
  Sumona, Duradel/Lapalok, and Kuradal are now recorded in their corresponding
  dated pool audits. Continue the family/variant, protection, challenge and
  location-context ledgers before exposing any live assignment roll.
- Before that unlock, the finisher consumes its own correct review. Exclude the
  salt, ice, fungicide, and explosive shakers released in 2015.

### Summoning

Labels: `COMPLETE`, `SOURCE DEBT`, `DEPENDENCY: COMBAT/ACQUISITION`.

- **Implemented 2026-07-17:** `summoning-skill-contract-2026-07-16.md` now
  governs the live eighteenth skill surface. The full ordinary catalog,
  pouch/scroll training, follower lifecycle, points, BoB cargo,
  Familiarisation, pets, restoration potions, Bogrog, Winter Storage, and the
  source-ready boost/heal/escape effects are shipped with assets, persistence,
  UI, undo, and pure/Qt coverage.
- Remaining combat/special-scroll effects, forager tables/cadence, and ordinary
  familiar teleports stay source/dependency-blocked. Daemonheim remains wholly
  owned by Dungeoneering; do not leak its familiars or herbs into overworld
  Summoning.
- Familiar lifetime is settled to every answered card, including Again, with a
  separate short-duration conversion that preserves period ratios rather than
  reusing the six-minute calendar scale. Pinned evidence is in
  `source-audits/summoning-familiar-lifecycle-2026-07-16.md`; the cross-system
  reconciliation is `simulation-time-boundary-2026-07-16.md`.
- BoB expiry creates an independently timed familiar-cargo reclaim event rather
  than auto-banking. Gravestones and cargo events use the shared reviewer alert
  strip in `review-hud-world-alerts-contract-2026-07-16.md` with distinct art and
  behavior.
- Implement one global familiar slot with a canonical Equipment panel and synced
  Bank/reviewer/target projections. Casual target presets select best available by
  sourced familiar role and auto-pack an active BoB; Advanced pins the exact
  familiar and exposes its separate inventory grid. Target navigation alone never
  dismisses, replaces, or repacks the live global familiar; the settled safe Bank-
  boundary swap may later replace it when all preconditions hold.
- Casual Summoning-point upkeep inserts one `Visiting altar+obelisk` restoration
  on the next successful answer when needed, replacing that target action and fully
  restoring ordinary Prayer and Summoning points; Again never restores. Existing
  combat Bank-run altar stops coalesce the obelisk without a second review. Advanced
  exposes the same automation as a toggle plus a manual command.
- Casual auto-special is globally on by default but fires only on successful
  answers, consumes a matching target-carried scroll plus sourced special-move
  points, and uses catalog-backed role triggers that avoid inapplicable or wasted
  effects. Bank scrolls are never consumed implicitly.
- Classify every familiar effect as passive periodic, continuous, or
  foreground/encounter-dependent. Passive effects advance and may produce on every
  answered card including Again; commands and attacks retain their successful-action
  gates. The catalog must state the class rather than deriving it from names.
- Familiar LP takes enemy damage only through a pinned retaliation, area, enemy,
  or aggro/tanking mechanic; attacking alone creates no exposure, and source
  silence means zero damage rather than a fabricated fallback targeting roll.
- An enabled target familiar policy atomically renews or replaces from compatible
  carried pouches on successful answers, including mid-encounter replacement.
  Advanced chooses its exact pouch-slot budget; missing pouch/points leaves a
  persistent lapsed reason and never partially consumes resources or Bank stock.
- If carried pouches run out while the policy is enabled, a successful answer may
  become a one-review Bank refill/resummon detour when compatible stock exists.
  Again never banks; insufficient Bank stock leaves the policy visibly lapsed.
- A target-policy mismatch may swap safely at the next Bank boundary: deposit BoB
  cargo, verify the replacement can succeed, then dismiss and summon atomically.
  Failed preconditions preserve the old familiar and show the new policy as queued.
- Casual `Best available` falls back to the strongest owned, level-valid, in-stock
  familiar in the configured role whenever replacement is needed. It never crosses
  roles; Advanced remains pinned to its exact familiar and lapses rather than substituting.
- Restocking a stronger same-role pouch never interrupts a live Casual fallback.
  `Best available` re-resolves at renewal, expiry, death, or explicit manual switch,
  preserving the remaining value of the already-consumed pouch.
- A BoB cannot transfer supplies during consecutive successful bursts against a live
  enemy. Again disengages without withdrawing; Casual may preset-top-up at the next
  successful pre-engagement boundary, as it may before combat or after kill/retreat.
- `Off — no familiar automation` never summons, renews, replaces, or auto-specials for
  that target, but it preserves an already-live global familiar and its paid duration.
- Familiarisation is source-pinned as a once-weekly shard/focus D&D ending at 60 shards,
  zero focus, or its period time cap, followed by a shard-scaled ingredient-box or
  triple-charm choice. The delegated translation is four answered cards, three focus
  pips, 15 shards per success, and one lost pip/no shards on Again.
- Ordinary training is source/app-pattern resolved under
  `source-audits/summoning-training-2026-07-16.md`: searchable pouch-infusion and scroll-
  creation families process one exact source unit per successful review; Wolf Whistle is
  optional; Dungeoneering rows stay out of the surface-world catalog. Exact row,
  acquisition, and route-cost harvesting remains before implementation.
- The old universal `park outside` idea is rejected. Restricted targets need a per-area
  consequence (`block_until_dismissed`, `auto_dismiss`, `summon_only_forbidden`, or
  `spirit_plane_hide`). Starting a target that must dismiss a live familiar opens a
  confirmation naming duration/pouch loss and any BoB cargo reclaim; Cancel changes
  nothing, Confirm dismisses without a review, and cargo never auto-banks. The live owner
  decision makes general manual Dismiss turn the current target policy Off by default,
  with an unchecked `Keep auto-summon` escape hatch; area-required dismissal preserves
  policy. Successful-review specials now award exact scroll-use XP in Casual and Advanced
  because every gameplay action is collapsed into automatic review resolution; Again never
  does, and only a future genuinely passive headgear-like auto-fire keeps the period zero-XP
  exception. Forager rows retain their sourced `drop_to_player` versus distinct
  `familiar_storage` delivery modes. A full carried inventory suppresses a drop roll with a
  visible log entry and no queued, banked, or owed output; storage-type familiars continue
  to their sourced capacity of 30 before suppressing later rolls.
- Familiar teleports select target-local alternate route profiles, with every source rate
  declaring its assumed route so a familiar never double-discounts a rate that already
  includes it. Spirit graahk's sourced 60-second Nature circuit replaces the slower route;
  ordinary familiar teleports use the live familiar without consuming another pouch. Void
  shifter reuses Combat retreat only when damage leaves the player alive below 10% LP, with
  no invented cooldown. Call to Arms remains tied to the future Pest Control activity.
- Magic teleports and charged jewellery share the target-local route-profile substrate.
  Magic's pure training casts remain, while a route cast consumes exact runes and awards
  exact XP once and jewellery consumes one source charge. Bank ownership alone is inert.
- Pets are restored as Summoning's tenth atomic family and close Construction's parked
  Menagerie dependency. Bank right-click **Let out**, follower-panel **Pick up**, and a
  separately confirmed **Release permanently...** keep activation distinct from Drop.
  Active pets share the follower slot and advance sourced growth/hunger on every answered
  card; stored hunger, growth, and stage persist but freeze. Casual auto-care reserves
  compatible food in real carried slots according to sourced hunger cadence and the next
  Bank boundary, then feeds and refills without Tamagotchi-style manual management. A
  high-hunger pet reuses that packing boundary and feeds before its first hunger advance.
  Cats retain staged quest and exceptional-function state.
  Exhausted food safely returns the pet home with an `Out of pet food` lapse rather than
  silently destroying it.
- Implement the source-owned pet routes in
  `source-audits/summoning-pet-acquisition-2026-07-16.md`: period pet shops/services,
  quest grants and transformations, Hunter catches, existing and missing nest/drop eggs,
  per-pet incubation/hatching, Construction Workshop creation, and activity reward shops.
  The searchable Pets log explains and links routes but never grants pets. Pin every exact
  cost, rate, XP value, timer, colour rule, and reclaim path before implementation. The
  Discontinued event pets remain compatibility-only outside the obtainable log and
  completion counts. Individual page review found no supported
  unreclaimable-one-time-pet category; Ex-ex-parrot and Broav reacquisition remain
  `source_blocked`, and their Release action cannot ship until those rows are resolved.
  Platypus **Release for reward...** belongs to its Hunter/quest location and atomically
  consumes the pet for the sourced casket/oyster roll; generic Release never grants it.
  Cat ratting is an explicit host target, Casual wily-cat retraining preserves its
  interaction-review cost, and Tooth creature auto-care cannot silently select a permanent
  adult variant. Source-timed growth that removes a capability uses the shared reviewer
  world-alert strip without pausing the transition. Mature god-bird protection is stored
  as a stage-gated faction flag but remains numerically inert until the later
  multi-enemy/God Wars grill; do not invent a generic defensive buff in the meantime.
  Unsafe death authentically destroys an active pet and any unprotected carried pet item;
  pets never enter the gravestone or Death's Office. Banked/Menagerie pets and safe-death
  contexts remain safe. Reacquisition and replacement state are source-specific.
- Rat Catchers' King Rat stage is one ordinary quest status line with the source-required
  cat item gate. Optional food, cautious retreat, LP exchange, and cat death remain
  represented scene detail; do not add a pet-combat actor, stance selector, hidden roll,
  or false mandatory food gate.
- Pack Yak Winter Storage fires at the full-pack boundary in Casual: spend one carried
  scroll and 12 special points to bank one configured eligible item only when that prevents
  the next Bank trip. Advanced may choose item priority and an earlier threshold. Route/rate
  metadata must declare whether Pack Yak use is already assumed.

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
- Slayer likewise owns `Smoking Kills` and every still-missing prerequisite in
  its reachable chain because the quest gates Sumona and the entire reward-point
  economy.
- Slayer also raises Shilo Village and the complete black-mask/Slayer-helmet
  route to the front of this quest program. The period quest tree is transitive,
  not limited to a manually named subset; already-playable prerequisites are
  reused and generated placeholders are replaced through the canonical runtime.
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

- Prefer stable restored mechanics for still-source-blocked Agility route values,
  Thieving success/stun/loot, Slayer assignment/reward pools, Summoning familiar
  behavior, Dungeoneering floors/rooms, and still-missing special-method hidden
  state. Agility, Farming, Construction, Prayer, and Magic core loops are shipped.

## Cross-system program queue

### Shared modular list search and filters

Labels: `ARCHITECTURE`, `IMPLEMENT`, `DEPENDENCY: SLAYER UI`.

- `ui.py` currently has Shop-specific text search and Quest-specific local
  filter controls, while other large pages still lack a reusable search seam.
- Extract one shared list-search/filter component with page-owned searchable
  metadata and predicates. It must preserve active selection, never activate a
  filtered row, provide a consistent empty state and keyboard/clear behavior,
  and use dark-mode-safe styling.
- First required consumer beyond the existing pages is Combat: ordinary search
  plus a `Current Slayer task only` checkbox that intersects with every other
  filter while leaving exact monster choice to the player. Do not solve this as
  another Slayer-only nested helper in `show_main_menu`.

### In-product help and mechanics reference

Labels: `PARKED`; promote to `IMPLEMENT` when sequenced.

- Build the single-source architecture proposed in
  `help-system-contract-2026-07-16.md`: an offline searchable Help Center backed
  by versioned topic files, with each page's consistent `?` control deep-linking
  into the same corpus. Do not maintain separate contextual copy and wiki prose.
- Reuse one modular Qt search component for Help and the addon pages whose large
  catalogs already need filtering; preserve page-specific result adapters rather
  than cloning search widgets and keyboard behavior.

### Activities, minigames, D&Ds, and reward shops

Labels: `DEEP GRILL`, `WAIT: DARKAN`, `SOURCE AUDIT`.

- Platform seed: `memory-bank/minigames-activities-design-seed.md`.
- Grill each family separately for entry/run state, review cost, event variance, currency, rewards, reward shop, persistence, expiry, and undo.
- Include the split activity cards from `gap-backlog.json`, bosses/instances, and wider pre-EOC reward activities. Never expose individual reward stubs before they work end to end.

### Bosses and instanced Combat

Labels: `DEEP GRILL`, `WAIT: DARKAN`, `DEPENDENCY: COMBAT/PRAYER/SUMMONING`.

- Fight Caves/Kiln, Barrows, God Wars, Corporeal Beast, Nex, quest bosses, and minigame enemies need authentic context and cannot become ordinary farm-target rows.
- Grill multi-enemy and ambient-faction aggression as one God Wars/Combat system. That
  substrate must consume the already-defined mature Zamorak-hawk and Saradomin-owl
  protection flags; the Guthix raptor intentionally supplies none.

### Acquisition and item/equipment completeness

Labels: `SOURCE AUDIT`, `DEPENDENCY`, sometimes `WAIT: DARKAN`.

- Maintain `tools/audit_item_reachability.py`; the current run finds 1,200
  actions and 273 orphan inputs (110 root, 163 cascade) across planned skills,
  activities, Combat/world acquisition, and potion-state plumbing. Bob Barter's
  quantity-free decant routes make potion dose variants known-producer cascades;
  their remaining availability follows upstream herb and secondary acquisition.
  See the dated audits for method and `activeContext.md` for the live count.
- Close every live-but-unobtainable material through authentic drops, ground spawns, shops, claims, quests, skills, activities, or transformations. Do not seed free items or fake recipe gates.
- The source-backed Woodcutting nest → empty nest → crushed nest route is repaired and regression-covered.
- Finish equipment requirements, special attacks, poison, charges/degradation, set effects, jewellery, consumables, and source-specific use actions without creating fake recipes.
- **Closed 2026-07-15:** barehand butterfly catching now ships as the distinct
  Hunter 95 action with its exact Hunter and Agility XP awards and no captured
  item. The prior XP/hour-audit gap remains useful evidence that missing method
  variants must be checked separately from item identity; see
  `memory-bank/source-audits/xp-hour-provenance-ledger-2026-07-13.md`.

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

**Respawn IS the model — and the inversion it produces is real** (settled
2026-07-13, grill round 3; this reverses the earlier warning on this card).
`XP ÷ respawn` makes the level-2 vegetable stall the best XP in Thieving and the
level-75 gem stall the worst. That looked like a *reductio* against the model
until both sources were checked: 2011Scape's `respawnTicks` and the period
E.P.S. column agree to within rounding on every high-level row (table on the
Thieving card). The single-stall rates really do invert. Real players world-hop,
which is a location mechanic we cannot model and must not fake — and we do not
need to, because at the levels where the inversion bites, far better Thieving
methods are already open. Model the respawn, ship the inversion.

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
- When all 25 pre-EOC skill surfaces are complete or explicitly excluded,
  publish a celebratory, interactive skill-milestone postmortem before moving on
  as though it were an ordinary card. Cover the build timeline and commit
  history; skill/action/target/item/quest/achievement totals; code, test, asset,
  provenance, documentation, migration, and archive growth; source-closed versus
  `source_blocked` or invented abstractions; major architecture changes; visual
  before/afters; bugs and near-misses; owner decisions that materially shaped
  the game; and lessons for the remaining activities/economy/release program.
  Generate the statistics from repository tools and Git at milestone time rather
  than preserving hand-maintained estimates.

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
