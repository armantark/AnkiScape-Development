# Progress

## Current Baseline — 2026-07-15

AnkiScape now has 16 complete skill surfaces, five partial Combat-trained skills, and four planned skills. Canonical live status is in `future-work-kanban.md`; the dated 2026-07-10 completion audit is a historical snapshot.

Phase 1 of the cadence kernel is complete on `main` at `b45aff0`. It
adds a dormant pure scheduler, additive config-v34 route residuals, the strict
off-by-default `ankiscape_cadence_kernel` flag, and exact save/load/undo and
flag-off RNG/output regression coverage. No skill behavior is routed or changed.

Phase 3 shadow observation is complete on `codex/cadence-phase3-shadow`. The
six in-scope adapters record current and proposed outcomes without mutating live
gameplay. The 175-route catalog has 24 source-ready routes and 151 explicit
`source_blocked` routes. Exact range envelopes, embedded Cooking/Firemaking
source rolls, overflow declarations, save/load sanitation, reporting, and
review undo are covered. Combat and the now-separately-shipped Thieving surface
remain outside the cadence experiment.

## Complete Skill Surfaces

- Gathering: Mining, Woodcutting, Farming, Fishing, Hunter.
- Artisan: Smithing, Crafting, Fletching, Firemaking, Cooking, Runecrafting, Herblore, Construction.
- Support/combat-adjacent: Prayer, Magic, and Thieving.

These surfaces use stable IDs, flat save state, review or background dispatch as appropriate, inventory mutation, telemetry, undo, assets/provenance, Skills-hub UI, Stats/Bank/HUD integration, and focused tests.

## Partial Combat Skills

Unified Combat trains Attack, Strength, Defence, Constitution, and Ranged. They deliberately remain `partial` because they do not own independent Skills-hub review surfaces. Magic is complete: its noncombat and combat contracts both ship.

## Planned Skills

- Summoning
- Agility — complete product/design-family contract; historical value sweep and
  implementation pending
- Dungeoneering
- Slayer

Summoning, Dungeoneering, and Slayer still need closed product/source contracts
before implementation.

Agility's design contract is now closed in
`agility-skill-contract-2026-07-15.md`, with the exhaustive design-family ledger
in `source-audits/agility-complete-content-inventory-2026-07-15.md`. Candidate
and `source_blocked` values still require the recorded historical sweep.
Implementation remains a future thread and must ship the full Agility-owned
surface atomically rather than a small course subset.

## Thieving closure

Thieving adds 17 pickpocket rows, 18 stall-family rows, one complete Menaphite
blackjack row, two visible source-blocked quest rows, exact cadence scheduling,
source-weighted loot, shared combat LP/stun/fight-back state, storage v35,
grouped Qt selection, four stable achievements, RuneScape-sourced skill and
Phoenix assets with provenance, and targeted pure/runtime/storage/Qt coverage.
Failure damage reuses Combat auto-eat/death/grave state, while encounter-only
Menaphites stay out of the ordinary Combat picker. The Feud and The Golem were
already playable in the 194-quest catalog; Thieving consumes those live
completion states.

Verification: 1,240/1,240 tests pass under Python 3.12 and under the real
offscreen Anki/Qt environment; `run_tests.py` is also green. The three expected
XP/hour parity failures predate this slice. A 609-test focused closure set,
zero Thieving/Phoenix reachability orphans, compilation, and `git diff --check`
complete the gate. See
`status-updates/thieving-skill-results-2026-07-13.html`.

## Latest Closure

The cadence Phase 3 closure adds:

- one guarded central observation seam for Mining, Woodcutting, Fishing, Hunter, Cooking, and Firemaking;
- exact rational low/high source envelopes with no midpoint collapse;
- reuse of the already-consumed live roll for Cooking and Firemaking, with no RNG drift;
- a separate transactional `cadence_shadow` namespace that never seeds live `cadence_profiles`;
- complete 175-route catalog and observed-save reporters for current, proposed, and source XP/hour;
- fail-closed handling for 151 missing or semantically incompatible source rows;
- fixed-seed flag-on/off gameplay-byte, XP, loot, call-sequence, RNG, save/load, and undo proof.

The durable closure record is `cadence-kernel-phase3-shadow-2026-07-13.md`.

## Previous Closure

The Prayer polish closure adds:

- atomic material/method selection;
- owned gilded altars at 250/300/350% with once-per-stint marrentill;
- 26 five-state training-urn tiers across Mining, Cooking, Fishing, Woodcutting, Smithing, and Prayer;
- target-carried Bonecrusher and Ectoplasmator behavior;
- direct full-urn teleport with immediate persistence and independent LIFO undo;
- substitution-aware skilling and Combat repacks;
- exact Chivalry/Rigour/Augury/Piety Defence gates;
- distinct Bonemeal and Wyvern bonemeal identities plus Prayer/Super prayer restore behavior;
- explicit RS3 provenance for the two new passive icons.

The durable source/conflict record is `source-audits/prayer-altar-urn-passives-herblore-closure-2026-07-13.md`.

## Systems That Work

- Skills hub, target metadata/renderers, Stats, Bank, Equipment, HUD, settings, and achievements.
- Utility/Activities and material processing.
- Target-local carried inventory, Advanced layouts, bank runs, Keep/Drop, Combat loadouts, and undo.
- NPC Shops, shared stock, services/actions, player selling, market clock, and shop undo.
- Bank Claims and pending future-skill XP rewards.
- A 194-row pre-EOC quest catalog with stage gates and focused audited replacements; presence remains scaffolding, not full fidelity.
- Item registry, source generators, asset scraping/provenance, reachability audit, and OpenRS2 cache queries.

## Remaining Programs

- Four planned skill loops.
- Full Combat/equipment/enemy/boss/instance breadth.
- Quest-by-quest fidelity across all 194 rows.
- Activities, minigames, D&Ds, reward currencies/shops, and timed events.
- GE and broad authentic acquisition closure.
- Achievement diaries, clue scrolls, collections, and one-time world rewards.
- Global level-1-to-99/economy pacing and release-readiness.

## Verification Baseline

- The test-signal cleanup and source-backed Thieving branches are merged into
  `main` at `526f9c2` and `63b0a28`. The quality audit now collects 1,219 tests
  across 66 files with zero hard issues and five advisory clone groups.
- The merged Thieving behavior set passes 409 focused tests; the focused real
  offscreen Qt Thieving/Herblore surface pair passes 2 tests.
- Current full Python 3.13 non-Qt discovery passes all 1,219 tests with 182
  environment skips and three expected failures.
- Current full real offscreen Anki/Qt discovery passes all 1,219 tests with no
  skips and three expected failures.

- Herblore asset, production-hook, and worktree-guard focused suites: 44 tests
  passing; focused real Qt Herblore behavior: 2 tests passing. A live Anki
  restart registers one bridge callback, one click opens one menu, and the
  corrected compact Herblore rail icon is visible.
- Compilation and `git diff --check` pass for the correction slice.

- Cadence Phase 3 focused suite: 176 tests passing, three expected failures.
- Phase 3 full non-Qt discovery: 1,219 tests passing, 187 skips, three expected failures.
- Phase 3 full real offscreen Qt discovery: 1,219 tests passing, three expected failures.
- Cadence Phase 1 targeted suite: 11 tests passing.
- Focused Prayer/passive/urn/logic/combat/Construction/runtime/storage/integration/Farming: 626 tests passing.
- Independent backend audit superset: 663 tests passing.
- `python3 run_tests.py`: 1,198 tests passing, 187 skips, 3 expected failures.
- Full real offscreen Qt discovery: 1,198 tests passing, 3 expected failures.
- Reachability: 1,102 actions, 725 consumed items, 296 orphan inputs (151 root, 145 cascade).
- Compilation and `git diff --check`: clean.

Test counts are snapshots; current runs outrank this note.

## Overnight fresh-eyes pass 4 — exact light-source identity (2026-07-16)

- Replaced the `Light source`/`Light sources` pseudo-item with eleven reachable
  exact lit states in eight source-placed quest gates and Dorgesh-Kaan Agility.
- Preserved the complete eighteen-item cutoff-era classification separately,
  without surfacing deferred Seer's headbands or expired event torches.
- Corrected the Tears of Guthix stage sequence and removed unsupported numeric
  gates from Watchtower and Another Slice of H.A.M.
- Removed Temple of Ikov's user-visible phantom requirement and repaired the
  live-vs-generated and consumed-equipment test oracles.
- Committed as `83de7e1`; 253 focused and 1,270 full tests pass, with zero hard
  test-quality issues and unchanged reachability counts.

## Overnight fresh-eyes pass 5 — persisted item-state symmetry (2026-07-16)

- Migrated legacy lantern and Mining helmet references across carried packs,
  advanced layouts, loot overrides, grave/Death's Office items and loadouts,
  and the Magic alchemy selector before carried-state sanitation.
- Prevented paid reclaim from restoring an unregistered zero-stat helmet or a
  phantom bank item during the live session.
- Reconfirmed that strung amulet identities are current items and must not be
  folded into the legacy migration map.
- Committed as `3953b64`; 312 focused and 1,272 full tests pass, with zero hard
  test-quality issues.

## Overnight fresh-eyes pass 6 — service and achievement symmetry (2026-07-16)

- Repaired Pottery Apprentice to read the canonical `Empty pot` identity and
  corrected the Monkey general stall to produce that same registered item.
- Replaced Activity Circuit's arbitrary five-key count with an exact check of
  all six live Agility activity families, including Flash Powder Factory.
- Independently cleared Bob Barter's total-dose, container, review-neutrality,
  and independent-undo paths without changing them.
- Committed as `c1ca766`; 183 focused and 1,274 full tests pass. Reachability
  remains 1,114 actions, 264 orphan inputs, and 149 cascade orphans; the test
  quality audit reports zero hard issues.

## Overnight fresh-eyes pass 7 — Qt lifecycle and bridge ownership (2026-07-16)

- Preserved upstream add-on results through Anki's tuple-valued global webview
  filter contract and consumed AnkiScape debug messages without nested tuples.
- Serialized deferred bridge opens, replaced the previous profile menu on each
  load, retained one XP popup, and marked the large main dialog for deletion on
  close.
- Removed the unreachable duplicate bridge handler and its wall-clock debounce,
  plus the unsupported `DeckBrowserContent.links` hook and four tests that
  asserted a fabricated Anki API. The real rendered-page JavaScript injector is
  unchanged and remains the sole deck-browser button path.
- Committed as `09aacc2`; 91 focused tests, 86 clean real-Qt lifecycle and
  integration tests, and 1,273 full tests pass. Compilation, diff, worktree
  safety, and the zero-hard-issue test-quality gate are clean.

## Overnight fresh-eyes pass 8 — canonical registry and graph coverage (2026-07-16)

- Repaired Adamantite Artisan and Runite Refiner to read the canonical live
  `Adamant bar` and `Rune bar` identities.
- Unified source item 4600 as `Willow blackjack` across generated equipment,
  the registry, shops, quest rewards, Thieving requirements, and equip runtime.
- Added live Magic and Prayer production to item reachability, including rune
  costs and dynamic bone inputs, and updated stale battlestaff dependency notes.
- Committed as `5ab5aee`; 78 focused, 509 integration/end-to-end, eight real
  offscreen Qt, and 1,275 full tests pass. Reachability covers 1,188 actions and
  reports 270 orphan inputs (110 root, 160 cascade); test quality remains at
  zero hard issues.

## Overnight fresh-eyes pass 9 — final quest stages and reward equipment (2026-07-16)

- Added the missing completion sentinel after every live quest's highest
  requirement, restoring the final source-backed objective in 152 generated
  quests rather than letting completion skip it.
- Generated source-config equipment records for seven obtainable quest items,
  corrected Ice arrows to the `ammunition` slot, and reclassified the
  non-equippable Staff of armadyl as quest material.
- Added catalog-wide, pure progression, runtime-handler, registry, generator,
  and level-gate regressions.
- Committed as `ceaab20`; 127 registry/shop/quest tests, 104 quest/runtime
  tests, four real offscreen Qt checks, and all 1,280 non-Qt tests pass.
  Reachability remains 1,188 actions with 270 orphan inputs, and test quality
  remains at zero hard issues.

## Overnight fresh-eyes pass 10 — Combat state and consequence symmetry (2026-07-16)

- Prioritized loaded compatible arrows over banked lower tiers, eliminating an
  ordinary-drop-triggered `out_of_ammo` stall.
- Routed Vengeance and Spellbook Swap through the finite rune loadout, persisted
  their cross-review state, kept Dream between fights, and counted reflected
  kills through the normal drop path.
- Moved filtered loot from a fatal multi-kill review into the grave and made
  Protect Item retain the highest store-value equipped item.
- Committed as `916b075`; 334 focused tests, eight real offscreen Qt checks, and
  all 1,286 tests pass. Reachability remains 1,188 actions with 270 orphan
  inputs, and test quality remains at zero hard issues.

## Overnight fresh-eyes pass 11 — ranged producer and equipment identity (2026-07-16)

- Normalized H.A.M. loot, Combat drops, and NPC shops to the canonical plural
  standard-arrow identities, with quantity-preserving save and shop-undo
  migration for legacy singular keys.
- Regenerated the equipment snapshot so all live Crafting and Fletching
  equipment outputs are accepted by the equipment engine, adding 29 missing
  rows and a synchronization oracle.
- Committed as `9273cf4`; 263 focused tests, five real offscreen Qt checks, and
  all 1,291 tests pass. Reachability remains 1,188 actions with 270 orphan
  inputs, and test quality remains at zero hard issues.

## Overnight fresh-eyes pass 12 — consumable and supply-pack state paths (2026-07-16)

- Routed Kebab through live RNG with deterministic undo and added exact Open
  and Open all actions for every registered supply pack.
- Added Juju farming potion activation with exact dose conservation and assets,
  then resolved the Magic essence mix identity conflict from pinned cache and
  emulator evidence.
- Aligned registry tradeability, Agility potion dose identities, food
  categories, assets, Bank verbs, and reachability with their live consumers.
- Committed as `f794108`; 19 focused tests, five real offscreen Qt checks, and
  all 1,302 tests pass. Reachability covers 1,200 actions with 273 orphan
  inputs, and test quality remains at zero hard issues.

## Overnight fresh-eyes pass 13 — finite Combat preset state (2026-07-16)

- Removed the owned `combat_supply_loadout` from the preset field contract, so
  saving or pinning configuration cannot snapshot real item quantities.
- Legacy presets containing the bad field are harmless on apply; the currently
  loaded finite pack remains authoritative and continues to deplete normally.
- Committed as `1fb0b64`; 271 focused tests, two real offscreen Qt checks, and
  all 1,303 tests pass. Reachability remains 1,200 actions with 273 orphan
  inputs, and test quality remains at zero hard issues.

## Overnight fresh-eyes pass 14 — atomic achievement dependencies (2026-07-16)

- Changed pure achievement dispatch to project newly satisfied completions and
  iterate until no dependent predicate becomes newly true.
- Added a catalog-backed regression proving Master Mage and Living Legend are
  returned by the same dispatch when Magic 99 closes the final ordinary gap.
- Committed as `b59c846`; 251 focused tests, one real offscreen Qt check, and
  all 1,304 tests pass with 186 skips and three expected failures. Test quality
  remains at zero hard issues; compilation, diff, and worktree safety pass.

## Overnight fresh-eyes pass 15 — production persistence and UI reachability (2026-07-16)

- Routed Shop, service, vendor, Bob Barter, and Wilderness transaction state to
  the canonical player-data save callback instead of the current-skill config
  callback, which never wrote the mutated player state.
- Added a Farming-sheet Juju potion control backed by the existing pure action
  and projection, including dose preservation and active-bonus legibility.
- Committed as `1120fb4`; 242 focused tests, all 183 real offscreen Qt tests,
  and all 1,305 core tests pass with 187 skips and three expected failures.
  Test quality remains at zero hard issues; compilation, diff, and worktree
  safety pass.

## Overnight fresh-eyes pass 16 — live skill-surface coherence (2026-07-16)

- Resolved friendly HUD target labels and equipped-blackjack readiness for the
  newest skill families.
- Made Magic, Construction, Thieving, and Agility controls refresh dependent
  state and report direct-action outcomes immediately.
- Exposed all five sourced Brimhaven XP exchanges and made target switching or
  Stop Training end the paid arena stint.
- Committed as `483eb55`; 170 focused core tests, eight real offscreen Qt
  checks, and all 1,312 core tests pass with 193 skips and three expected
  failures. Test quality remains at zero hard issues; compilation, diff, and
  worktree safety pass.

## Overnight fresh-eyes pass 17 — atomic reward consequences (2026-07-16)

- XP-lamp claims now recalculate the selected skill level before achievement
  evaluation and surface the granted XP immediately.
- Quest-bank claims and Stronghold boot/coin rewards register direct-action
  undo snapshots before mutating live state.
- Shop purchases, sales, services, and vendor actions dispatch achievements
  before the canonical save callback.
- Committed as `111b280`; 109 focused core tests and nine real offscreen Qt
  Shop checks pass. Test quality remains at zero hard issues; compilation,
  diff, and worktree safety pass. Full closure verification remains pending.

## Overnight fresh-eyes pass 18 — Combat management consequences (2026-07-16)

- Clearing the finite Combat loadout now repaints returned Bank items in the
  open dialog.
- Loadout unload and Death's Office reclaim dispatch inventory achievements
  before persistence.
- Kept automatic safe-boundary refill as the settled UI instead of reviving the
  deliberately removed manual Refill control.
- Committed as `91f0b35`; 252 focused core tests and the combat-filtered real
  offscreen Qt surface pass. Test quality remains at zero hard issues;
  compilation, diff, and worktree safety pass. Full closure remains pending.

## Overnight fresh-eyes audit closure (2026-07-16)

- Completed 18 bounded passes and 36 attributable commits in a dedicated safe
  worktree; the verified history was subsequently fast-forwarded into `main`.
- Final core: 1,314 passing in 39.163 seconds, 193 environment skips, three
  expected XP-parity failures.
- Final real offscreen Qt: 1,314 passing in 543.509 seconds, no skips, the same
  three expected failures.
- Test quality: zero hard issues across 66 files. Reachability: 1,200 actions,
  273 known orphans. Compilation, diff, and worktree safety checks pass.
- No confirmed defect remains queued; four creative-direction questions are
  ranked in `memory-bank/design-gaps-overnight-2026-07-16.md`.

## Achievement semantics foundation (2026-07-16)

- Integrated into `main` at `a0f5da4` under the repository's direct-main
  workflow.
- Classified all 168 achievements and replaced 70 action-worded Bank snapshot
  predicates with durable action-owner production progress.
- Added config v37 migration from the maximum of available telemetry history and
  current relevant holdings while preserving completed achievement names.
- Kept true Hold/Own achievements live, made finished-potion holdings invariant
  across vial doses, mixes, flasks, and Bob Barter decanting, and excluded
  Runecrafting tiaras from rune production totals.
- Defined cross-skill ownership at the action surface: Magic Superheat does not
  count as Smithing production, Construction tablets remain Construction-owned,
  and Inferno-adze logs remain Woodcutting-owned.
- Added focused unit, migration, runtime, integration, end-to-end, and undo
  regressions. All 1,323 core tests pass with 193 environment skips and three
  documented expected failures; all 1,323 tests also pass under the real
  offscreen Qt runtime with the same three expected failures and no skips.
- Test quality reports zero hard issues across 66 files. The 1,200-action
  reachability baseline remains unchanged at 273 known orphans (110 root, 163
  cascade); compilation, diff, and worktree-safety checks pass.
- Published the self-contained closure report at
  `memory-bank/status-updates/achievement-semantics-results-2026-07-16.html`.
  Diary-gear cadence and acquisition remain a separate owner grill rather than
  an implicit part of this semantics repair.
