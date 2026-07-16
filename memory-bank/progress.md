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
