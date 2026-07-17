# Progress

## Current Baseline — 2026-07-16

AnkiScape now has 18 complete skill surfaces, five partial Combat-trained skills, and two planned skills. Canonical live status is in `future-work-kanban.md`; the dated 2026-07-10 completion audit is archived baseline evidence.

## Summoning implementation closure — 2026-07-17

- Shipped the complete 80-familiar surface catalog, 78 pouch recipes, 67
  scroll targets, exact source XP/requirements, and the ordinary Skills-hub
  training surface.
- Added persistent summon/dismiss/renew state, separate ordinary and
  special-move points, BoB storage/reclaim, four-review Familiarisation, its
  ingredient/triple-charm rewards, and answered-card world ticks.
- Restored the 47 freeze-date pets, their shared follower slot, care/growth,
  acquisition log, death/release semantics, Menagerie dependency, UI, assets,
  migration, and undo-safe commands.
- Added exact Summoning and super-restore dose families, source-ready familiar
  boosts, Bunyip healing, Void-shifter escape, Pack yak Winter Storage, and all
  78 Bogrog pouch exchanges.
- Kept Daemonheim out of the overworld and parked unsourced combat/scroll,
  forager, and teleport mechanics without fabricated substitutes. No unresolved
  owner-level design question remains.
- Verified 1,446 core methods (1,242 ordinary passes, 201 environment skips,
  three expected failures) and 1,446 real offscreen Qt methods (1,443 ordinary
  passes, three expected failures), plus focused UI, docs, test-quality,
  compilation, JSON, generator-determinism, diff, and worktree-safety gates.
  Reachability records 1,220 actions and 290 known acquisition/dependency
  orphans (112 root, 178 cascade); it remains a debt report, not a passing gate.

## Mage Arena and Farming cure-policy closure — 2026-07-17

- Completed the sourced Mage Arena reward loop: final-form alignment, the first
  matching cape/staff, one-review god-spell attunement, one-cape statue
  replacement/reclaim, matching-loadout equipment guards, and legacy-save
  compatibility.
- Completed Charge's real combat effect. The matching attuned god spell rises
  from 200 to 300 LP maximum hit only while Charge is active and the matching
  cape/staff are worn; preview and live combat share the calculation.
- Added the three period god-cape assets and generated their exact item-config
  equipment rows. Their canonical item records now retain cache IDs,
  non-stackability, non-tradeability, cape-slot metadata, and provenance. The
  generator reproduces the equipment rows rather than relying on hand edits.
- Added Farming's per-patch two-option cure priority, preset/queue snapshots,
  execution-time fallback, and canonical Cure Plant rune/quest/XP transaction.
- Archived both resolved owner questions; no non-Summoning design gap remains
  from the grill-harvest program.
- Final verification passed all 1,388 core methods and all 1,388 real offscreen
  Qt methods. Core discovery retains 196 environment skips; Qt discovery has
  none. Both contain only the three declared XP-parity expected failures, and
  test quality reports zero hard issues across 67 files.
- Published
  `status-updates/mage-arena-farming-cure-results-2026-07-17.html` and its
  mobile-safe copy at <https://q0wso578s42a.postplan.dev>.

## Slayer Turael/Spria source harvest — 2026-07-17

- Reconciled the first complete functional-master pool at 23 families and a
  355-point provisional hidden-weight denominator.
- Restored Gelatinous abominations and Grotworms from cutoff monster/tutorial
  evidence plus emulator convergence; rejected Turael Trolls as an anonymous,
  malformed wiki-table insertion contradicted by the cutoff cross-master table
  and Darkan.
- Closed the Icefiend conflict at 10–20 from the explicit Turael correction and
  two-emulator convergence. Gelatinous ordinary count remains a labeled 15–50
  Turael-default abstraction, distinct from its sourced five-kill tutorial.
- Kept Turael/Spria out of live assignment generation because six families and
  two distinctive kill/protection mechanics remain baseline blockers.
- Fixed Cave slime's omitted source `poisonDamage = 3` and added deterministic
  Combat-state coverage.
- Durable evidence:
  `source-audits/slayer-turael-spria-pool-2026-07-17.md`.

## Slayer Mazchna/Achtryn source harvest — 2026-07-17

- Reconciled the second functional-master pool at 27 families and a provisional
  325-point hidden-weight denominator.
- Rejected the anonymous Mazchna `40–85` range in favor of the earlier
  Knowledge Base correction, cutoff Achtryn table, and Darkan convergence at
  `40–70`; preserved `30–60` Cyclopes and `10–20` Wall beasts, and used the
  repaired cutoff row span to close Grotworms at `40–70` over Darkan's
  conflicting `20–40`.
- Restored the emulator-stubbed Mogre and Wall-beast rows from cutoff master,
  cross-master, and individual monster evidence. Their 10-point hidden weights
  are labeled common-baseline abstractions, not recovered facts.
- Kept Mazchna/Achtryn out of live assignment generation because ten families,
  three existing-target mechanics, and the whole assignment-family registry
  remain runtime blockers.
- Fixed Cave crawler's omitted source `poisonDamage = 8` and added deterministic
  Combat-state coverage.
- Durable evidence:
  `source-audits/slayer-mazchna-achtryn-pool-2026-07-17.md`.

## Slayer Vannaka source harvest — 2026-07-17

- Reconciled the third functional-master pool at 35 families and a provisional
  460-point hidden-weight denominator.
- Rejected Darkan's extra Troll row because the cutoff Vannaka page omits it and
  the cutoff cross-master table assigns Trolls only to Chaeldar and Sumona.
- Restored Mogres and Sea snakes from cutoff master/cross-master evidence.
  Their 10-point weights are labeled common-baseline abstractions; game-main's
  explicit 2.17% ordinary-family rows independently round from `10 / 460`.
- Kept the single observed Grotworm count of 69 as history rather than a fake
  range, and labeled Darkan's ordinary Vannaka `60–120` range as the smallest
  explicit count abstraction.
- Kept Vannaka out of live assignment generation because 23 families, the
  stable family/variant registry, and numerous quest, protection, lure, context,
  and restricted-kill mechanics remain runtime blockers.
- Corrected the Stronghold Shade to its cutoff 3.5 Slayer XP and one-quarter
  ordinary combat/Constitution damage XP, with a deterministic live-burst
  regression.
- Corrected the earlier Turael audit: current game-main does execute its
  incomplete Slayer table through the talk-to assignment path.
- Durable evidence:
  `source-audits/slayer-vannaka-pool-2026-07-17.md`.

## Slayer Chaeldar source harvest — 2026-07-17

- Reconciled the fourth functional-master pool at 34 families and a provisional
  388-point hidden-weight denominator.
- Restored Grifolapines and Grifolaroos from direct cutoff individual pages
  despite their omission from the stale master/cross-master tables.
- Restored Shadow warriors and Mutated zygomites over Darkan's omissions with
  explicit 10-point common-baseline abstractions.
- Kept Darkan's remaining weights provisional, closed Elves at `60–90`, and
  labeled Grotworms' `72–109` as an observed-history envelope rather than a
  recovered generator range.
- Restored Chaeldar's 10/50/150 point schedule from the cutoff Slayer-points
  table, both emulators, and the master page's own long-run arithmetic.
- Corrected the accepted gates where Darkan conflicts with cutoff evidence:
  Regicide for Elves, Rum Deal route access for Fever spiders, Magic 50 for
  Fungal magi, Magic 60 for Grifolapines/Grifolaroos, and Slayer 67 plus
  Branches of Darkmeyer for Vyrewatch.
- Kept Chaeldar out of live assignment generation: end-to-end family readiness
  is 0/34, 29 families have no direct target, and Banshee/Baby-blue behavior
  requires complete protection/identity mechanics.
- Corrected the live level-8 Crawling hand from game-main's conflicting 12
  Slayer XP to the cutoff 16, with a focused source regression.
- Durable evidence:
  `source-audits/slayer-chaeldar-pool-2026-07-17.md`.

## Slayer Sumona source harvest — 2026-07-17

- Reconciled the fifth functional-master pool at 37 families and a provisional
  407-point hidden-weight denominator.
- Restored Scabarites and Terror dogs from cutoff master, cross-master, and
  individual-family evidence over Darkan's commented stubs. Their 10-point
  weights are labeled common-baseline abstractions; Darkan's other 35 rows
  contribute 387 provisional points.
- Kept cutoff Black demons, Grifolapines, Grifolaroos, and Mutated jadinkos
  despite omissions in the stale cross-master table, and corrected Darkan's
  Black-demon and Gargoyle count conflicts to `120–185`.
- Closed Sumona's Combat 85, Slayer 35, Smoking Kills, and 12/60/180 point
  gates. Preserved the Kalphite Queen challenge as a 15,000-XP, 30-point,
  one-task compound objective while leaving its exact offer rule
  `source_blocked`.
- Kept Sumona out of live assignment generation: end-to-end family readiness
  is 0/37, only four ordinary families have complete Combat targets, and the
  remaining family registry, quest, target, protection, identity, special, and
  task-credit paths are absent.
- Removed the incorrect 60 Slayer XP from temporary Death spawns and added a
  cutoff-source regression.
- Durable evidence:
  `source-audits/slayer-sumona-pool-2026-07-17.md`.

## Agility carried-risk amendment — 2026-07-17

- Integrated into `main` at `69855d9`.
- Added real target-local Auto/Custom course packs, required-item gates, ordered
  food, Bank-clamped carried/equipment weight, and a one-review supply refill.
- Routed course damage through shared auto-eat, death, grave, and review undo
  while preserving dormant target packs.
- Added the approved Wilderness 1% lap-completion ambush before reward commit;
  fatal hits forfeit the pending lap atomically.
- Added live pack/weight/risk summaries without exposing Combat-only controls.
- The final checker found and the primary fixed stale saved packs contributing
  weight after Bank disposal.
- Verified 1,353 core methods, two real offscreen Qt checks, zero hard test
  quality issues, 236 Markdown and 298 HTML files, and safe diff/worktree
  closure.

## Farming replacement and preset amendment — 2026-07-17

- Integrated into `main` at `9b65f45`.
- Added the explicit one-review `Dig up` verb for healthy mature regrowth
  crops, including differing-plan full runs that queue removal before planting.
- Added user-named whole-farm presets with selected patch inclusion, inert
  selection/application, modified-state reporting, and full CRUD management.
- Added per-plan gardener, watering, and Plant-cure policies. Full runs skip and
  report patches missing gardener goods instead of silently planting
  unprotected.
- Gardener payments are validated queue escrow: successful planting consumes
  them, while queue removal, clearing, or execution skips refund them.
- The independent final checker found and the primary fixed removable payment
  ownership and maximum-length duplicate preset names.
- Verified all 1,363 core methods (1,164 ordinary passes, 196 environment
  skips, three expected failures), all 1,363 real offscreen Qt methods (1,360
  ordinary passes, three expected failures), 84 final focused Qt tests, zero
  hard test-quality issues, and safe diff/worktree closure.

## Worktree collapse — 2026-07-16

- Reconciled all seven linked worktrees into the canonical checkout and removed
  their safe-root directories. Agility/Bank decisions, Herblore assets, test
  cleanup, Thieving, and the overnight audit were already contained in `main`.
- Integrated the previously unmerged Slayer design contract and eight focused
  source audits, preserving its complete owner-grill history while reconciling
  current Memory Bank and archive structure.
- Integrated the paused Summoning design ledger through decision 22 plus its
  lifecycle, training, Familiarisation, simulation-time, reviewer-alert, and
  Help contracts. Summoning remains an active design/source program; this does
  not claim runtime implementation.
- `git worktree list` now contains only the canonical `main` checkout, and the
  worktree-guard audit passes.
- Closure artifact:
  `status-updates/worktree-collapse-results-2026-07-16.html`.

## Documentation archive closure — 2026-07-16

- Added a Memory Bank index and explicit archive policy so current entry points,
  evidence records, and historical artifacts have distinct homes.
- Archived six superseded/completed root records plus the completion audit's JSON
  companion; copied all four approved-but-unimplemented overnight decisions to
  the canonical Kanban before archiving their resolved question ledger.
- Moved 308 old status files into monthly archives while retaining the three
  current July closure reports at the top-level status entry point.
- Extended the documentation audit to validate local HTML resources and to
  tolerate staged old paths during link-safe file moves.
- Closure verification: 215 Markdown and 295 HTML documents pass the audit;
  all 1,329 core tests pass with 193 environment skips and three declared
  expected failures; test quality has zero hard issues across 67 files. All 24
  JSON files parse, compilation/diff/worktree-safety gates pass, and Qt testing
  is not required because no runtime or UI behavior changed.
- Closure artifact:
  `status-updates/documentation-archive-results-2026-07-16.html`.

## Documentation integrity closure — 2026-07-16

- Audited all 505 project Markdown/HTML documents, including this closure's
  final results artifact. The permanent `tools/audit_docs.py` gate checks UTF-8,
  final newlines, whitespace defects, Markdown fences/local links, HTML
  doctypes, parsing, and explicit element nesting.
- Reconciled current status to 17 complete, five partial, and three planned
  skills; corrected merged-branch pointers, live acquisition/reachability
  claims, and the difference between approved design and shipped behavior.
- Preserved dated evidence instead of rewriting history. Historical contracts,
  audits, briefs, and results now carry explicit status or later-integration
  notes where their original wording could be mistaken for current state.
- Full core verification ran 1,327 methods: 1,131 ordinary passes, 193
  environment skips, and three expected failures. The test-quality audit reports
  zero hard issues across 67 files; JSON parsing, compilation, diff, and
  worktree-safety checks pass.
- Closure artifact:
  `status-updates/documentation-integrity-results-2026-07-16.html`.

Phase 1 of the cadence kernel is complete on `main` at `b45aff0`. It
adds a dormant pure scheduler, additive config-v34 route residuals, the strict
off-by-default `ankiscape_cadence_kernel` flag, and exact save/load/undo and
flag-off RNG/output regression coverage. No skill behavior is routed or changed.

Phase 3 shadow observation is merged into `main` at `6422610`. The
six in-scope adapters record current and proposed outcomes without mutating live
gameplay. The 175-route catalog has 24 source-ready routes and 151 explicit
`source_blocked` routes. Exact range envelopes, embedded Cooking/Firemaking
source rolls, overflow declarations, save/load sanitation, reporting, and
review undo are covered. Combat and the now-separately-shipped Thieving surface
remain outside the cadence experiment.

## Complete Skill Surfaces

- Gathering: Mining, Woodcutting, Farming, Fishing, Hunter.
- Artisan: Smithing, Crafting, Fletching, Firemaking, Cooking, Runecrafting, Herblore, Construction.
- Support/combat-adjacent: Prayer, Magic, Thieving, Agility, and Summoning.

These surfaces use stable IDs, flat save state, review or background dispatch as appropriate, inventory mutation, telemetry, undo, assets/provenance, Skills-hub UI, Stats/Bank/HUD integration, and focused tests.

## Partial Combat Skills

Unified Combat trains Attack, Strength, Defence, Constitution, and Ranged. They deliberately remain `partial` because they do not own independent Skills-hub review surfaces. Magic is complete: its noncombat and combat contracts both ship.

## Planned Skills

- Dungeoneering
- Slayer

Dungeoneering and Slayer remain the two planned registry surfaces. Their active
design/source work is tracked independently and must be merged into the
canonical checkout before this ledger treats either as live.

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
`status-updates/archive/2026-07/thieving-skill-results-2026-07-13.html`.

## Cadence Phase 3 Closure — 2026-07-13

The cadence Phase 3 closure adds:

- one guarded central observation seam for Mining, Woodcutting, Fishing, Hunter, Cooking, and Firemaking;
- exact rational low/high source envelopes with no midpoint collapse;
- reuse of the already-consumed live roll for Cooking and Firemaking, with no RNG drift;
- a separate transactional `cadence_shadow` namespace that never seeds live `cadence_profiles`;
- complete 175-route catalog and observed-save reporters for current, proposed, and source XP/hour;
- fail-closed handling for 151 missing or semantically incompatible source rows;
- fixed-seed flag-on/off gameplay-byte, XP, loot, call-sequence, RNG, save/load, and undo proof.

The durable closure record is `cadence-kernel-phase3-shadow-2026-07-13.md`.

## Prayer Polish Closure — 2026-07-13

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

- Three planned skill loops.
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
- Final core: 1,314 methods in 39.163 seconds, comprising 1,118 ordinary passes,
  193 environment skips, and three expected XP-parity failures.
- Final real offscreen Qt: 1,314 methods in 543.509 seconds, comprising 1,311
  ordinary passes, no skips, and the same three expected failures.
- Test quality: zero hard issues across 66 files. Reachability: 1,200 actions,
  273 known orphans. Compilation, diff, and worktree safety checks pass.
- No confirmed defect remains queued. The four creative-direction questions in
  `memory-bank/archive/2026-07/resolved-queues/design-gaps-overnight-2026-07-16.md`
  are design-resolved, and their four pending implementations are recorded in
  `memory-bank/future-work-kanban.md`.

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
  regressions. The core suite ran 1,323 methods: 1,127 ordinary passes, 193
  environment skips, and three documented expected failures. The real
  offscreen Qt suite ran 1,323 methods: 1,320 ordinary passes and the same three
  expected failures, with no skips.
- Test quality reports zero hard issues across 66 files. The 1,200-action
  reachability baseline remains unchanged at 273 known orphans (110 root, 163
  cascade); compilation, diff, and worktree-safety checks pass.
- Published the self-contained closure report at
  `memory-bank/status-updates/achievement-semantics-results-2026-07-16.html`.
  Diary-gear cadence and acquisition remain a separate owner grill rather than
  an implicit part of this semantics repair.

## Slayer Duradel/Lapalok source harvest (2026-07-17)

- Reconciled 35 cutoff ordinary families and a provisional 334-point hidden
  weight denominator from 34 Darkan rows plus a labeled 10-point Scabarite
  abstraction.
- Pinned Combat 100, Slayer 50, Shilo Village access, 15/75/225 points,
  Duradel-to-Lapalok succession after While Guthix Sleeps, and the 69-kill
  Slayer Tower challenge with no per-kill Slayer XP.
- Resolved Scabarites to the observed cutoff `40–79`, corrected Kalphites to
  `130–200`, and kept four late-family count ranges explicitly provisional
  where the historical generator remains source-blocked.
- Kept the master runtime-hidden at 0/35 readiness rather than renormalizing a
  partial pool around missing families and mechanics.
- Restored Abyssal-demon source quantity distributions and the global Rare
  table, and removed the Kuradal's Dungeon-only Ferocious-ring drop from the
  generic target without changing other drop probabilities.
- Added deterministic Combat regressions for the repaired quantities, Rare
  branch and context-specific exclusion. All 345 focused holdouts and all
  1,369 core methods pass, with 196 environment skips and the three declared
  XP-parity expected failures; test quality remains at zero hard issues.
  Summoning and Dungeoneering remained outside the batch.

## Slayer Kuradal source harvest (2026-07-17)

- Reconciled 36 cutoff ordinary families and a provisional 322-point hidden
  weight denominator from 35 Darkan rows plus a labeled 10-point Terror-dog
  abstraction.
- Mapped Darkan's `VOLCANIC_CREATURES` row to ordinary TzHaar, kept the
  280-kill Fight Cave challenge separate, and resolved nine count conflicts
  from the direct cutoff master ledger.
- Pinned Combat 110, Slayer 75, Ancient Cavern access, 18/90/270 points,
  Aquanite and ice-strykewyrm reward gates, Kuradal's Dungeon/Ferocious-ring
  consequences, and the no-bonus-points Fight Cave challenge.
- Kept Kuradal runtime-hidden at 0/36 readiness rather than renormalizing a
  partial pool around absent families, contexts and mechanics.
- Restored the live level-149 TzHaar-Ket's cutoff 136 Slayer XP after a focused
  regression reproduced the missing field. All 345 focused holdouts and all
  1,369 core methods pass, with 196 environment skips and the three declared
  XP-parity expected failures; test quality remains at zero hard issues.
  Summoning and Dungeoneering remained outside the batch.

## Slayer Cockatrice protective equipment (2026-07-17)

- Pinned the cutoff Mirror-shield trigger, fixed eye-beam hit, one-quarter stat
  floor, item identity, slot, equip gate, and Slayer-shop acquisition.
- Reconciled the hidden damage function as the smallest labeled mapping:
  Darkan's maximum-LP/6 fixed hit capped at the period page's 110 LP.
- Reconciled the repeated drain from the period one-quarter floor and
  2011Scape's 25%-of-base Attack, Strength, Defence, Ranged, and Agility set.
- Added the data-driven Combat consequence, fixed-hit/prayer bypass, persistent
  current-level drains, ordinary food/death/retreat/undo integration, and a
  non-blocking target warning.
- Kept Banshee unimplemented because its exact stat-drain magnitude conflicts
  across reconstructions and the period effect includes currently excluded
  Summoning.
- Verification passes 383 focused Combat/runtime/integration tests, one real
  offscreen Qt picker check, and all 1,374 core methods with 196 skips and
  three expected failures. Test quality has zero hard issues; documentation,
  reachability, compilation, diff and worktree-safety checks pass.

## Slayer finisher-item acquisition metadata (2026-07-17)

- Reproduced a generated-data loss where shop-only items discarded their
  source item IDs and defaulted to stackable in the shared registry.
- Preserved stock-row `source_item_id` and `stackable` through the generated
  helper, including the generator template so regeneration cannot erase the
  repair.
- Pinned Bag of salt 4161 as stackable, Rock hammer 4162 as non-stackable, Ice
  cooler 6696 as stackable, and Fungicide spray 10 7421 as non-stackable.
- Passed 167 shop/registry/integration methods and three real offscreen Qt shop
  flows. Reachability remains at 1,200 actions and 273 known orphans.
- Kept all four finisher families hidden: target data, context-correct drops,
  enemy assets, and reachable finisher runtime are not yet jointly certified.

## Grill-harvest program closure (2026-07-17)

- Completed all four owner-approved post-closure amendments.
- Reconciled all seven functional Slayer-master pools and implemented every
  source-ready atomic repair found during this bounded harvest.
- Closed the remaining Slayer runtime as explicit source/dependency work
  rather than exposing incomplete masters or dead feature code.
- Final core discovery: 1,376 methods, 1,177 ordinary passes, 196 skips, and
  three expected failures.
- Final real offscreen Qt discovery: 1,376 methods, 1,373 ordinary passes, no
  skips, and three expected failures.
- Documentation, test quality, compilation, JSON, diff, reachability, and
  worktree-safety gates all pass.
- Published `status-updates/grill-harvest-results-2026-07-17.html` and its
  mobile-safe copy at <https://co9e6hzqn0pd.postplan.dev>.
