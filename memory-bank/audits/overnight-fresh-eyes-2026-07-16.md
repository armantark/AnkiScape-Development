# Overnight fresh-eyes audit — 2026-07-16

## Objective

Find and fix concrete defects and implementation imperfections across the AnkiScape repository before 09:00 America/Los_Angeles. Codex owns reproduction, implementation, tests, commits, and final decisions. Reviewer selection uses Claude Code's live `/usage` reading: Fable remains available while `Current week (Fable)` is safely below 30%, then Opus takes over. Workflow token telemetry is not treated as quota percentage.

## Fixed critic instruction

> Once again, check over everything again with fresh eyes looking for any blunders, mistakes, errors, oversights, omissions, problems, misconceptions, bugs, etc. Be SUPER thorough and meticulous!

## Inner loop

1. Select the next unreviewed scope from the coverage ledger.
2. Ask one independent Claude reviewer to inspect only that scope and report exact files, lines, failure mechanisms, and omitted areas. The reviewer may not edit, commit, or declare broad correctness.
3. Codex reproduces each candidate against current code and runtime.
4. Codex fixes only confirmed defects, with one attributable hypothesis per batch.
5. Run targeted unit, integration, end-to-end, and relevant offscreen Qt tests. Add regression tests that fail before the fix and protect real behavior.
6. Run the invariant holdouts listed below. Revert or repair any candidate that fails them.
7. Commit an accepted batch on `codex/overnight-fresh-eyes-2026-07-16`, then append evidence here and update the JSON state.

## Verifier and holdouts

- Targeted behavioral reproduction and regression tests.
- `python3 tools/worktree_guard.py audit` before and after worktree-sensitive operations.
- `/opt/homebrew/bin/python3 tools/audit_test_quality.py` after test changes.
- `python3 run_tests.py` at checkpoints and closure.
- Real offscreen Qt discovery for UI/runtime changes.
- `python3 tools/audit_item_reachability.py --json` for item/economy changes.
- `python3 -m compileall` and `git diff --check` before every accepted commit.
- Review undo, direct-action undo, deterministic RNG ordering, wall-clock prohibition, flat save migration, target-local carried inventory, and source provenance remain fixed invariants.

## Outer loop trigger

Do not change the search mechanism initially. After three consecutive independent passes with no material finding, switch from module-oriented review to a seam portfolio: producer/consumer item identity, persisted-state writer/reader symmetry, UI-selector/runtime-gate reachability, death/undo/rollback consequences, source-contract/code drift, and test-oracle blind spots. After two outer-loop passes with no material finding, stop for convergence even if the deadline has not arrived.

## Rollback and authority

Every accepted change is checkpointed in a normal commit. Failed candidates are reverted with a forward patch, never destructive Git commands. The loop may edit and commit only this worktree. It may not merge into `main`, push, publish, deploy, modify credentials, install dependencies, or expand product scope. Creative design choices that are not already settled go into the ranked morning design-gap file and remain unimplemented.

## Coverage ledger

| Pass | Scope | Reviewer | Candidates | Confirmed | Commit | Verification |
|---:|---|---|---:|---:|---|---|
| 1 | Agility, Thieving, Farming, Magic runtime seams | Fable | 14 | 9 | `01ef8d9` | 230 focused; 1 real offscreen Qt; 1,252 full; reachability; zero hard test-quality issues |
| 2 | Crafting and Magic item identity, registry, assets, reachability | Opus | 5 | 5 | `b263c15` | 252 focused; 1,258 full; reachability counts unchanged; zero hard test-quality issues |
| 3 | Lantern and lamp-oil state graph across Crafting, Smithing, Firemaking, shops, equipment, quests, assets, and saves | Fable pre-implementation; Codex verification | 7 | 7 | `37b46c5` | 270 focused; 179 real offscreen Qt; 1,265 full; 14 fewer cascade orphans; zero hard test-quality issues |
| 4 | Exact light-source identity across generated/manual quests, Dorgesh-Kaan Agility, registry, UI prose, and test oracles | Opus | 5 | 3 | `83de7e1` | 253 focused; 1,270 full; reachability unchanged; zero hard test-quality issues; compilation, diff, and worktree checks |
| 5 | Persisted item-name symmetry across carried packs, loot preferences, graves, Death's Office, equipment reclaim, shop rollback, and Magic selectors | Opus | 3 | 3 | `3953b64` | 312 focused; 1,272 full; zero hard test-quality issues; compilation, diff, and worktree checks |
| 6 | Shop services, Herblore dose conservation, Agility and Thieving activities, and achievement writer/reader symmetry | Opus | 3 | 3 | `c1ca766` | 183 focused; 1,274 full; reachability unchanged; zero hard test-quality issues; compilation, diff, and worktree checks |
| 7 | Qt lifecycle, production hook registration, bridge filter symmetry, singleton menu ownership, and runtime worktree isolation | Opus | 12 | 8 | `09aacc2` | 91 focused; 86 clean real-Qt rerun after one test-fake ordering repair; 1,273 full; zero hard test-quality issues; compilation, diff, and worktree checks |
| 8 | Canonical registry identities, generated equipment, achievements, assets, and Magic/Prayer reachability coverage | Opus | 3 | 3 | `5ab5aee` | 78 focused; 509 integration/end-to-end; 8 real offscreen Qt; 1,275 full; zero hard test-quality issues; compilation, diff, and worktree checks |
| 9 | Quest stage/reward writers, shop identities, non-Agility activity counters, achievement readers, and obtainable quest equipment | Opus | 2 | 2 | `ceaab20` | 127 registry/shop/quest plus 104 quest/runtime; 4 real offscreen Qt; 1,280 full; zero hard test-quality issues; reachability, compilation, diff, and worktree checks |
| 10 | Combat supplies, supplemental Magic state, Ranged ammo, reflected kills, fatal loot, equipment protection, and undo seams | Opus | 3 | 3 | `916b075` | 334 focused combat/runtime/integration; 8 real offscreen Qt; 1,286 full; zero hard test-quality issues; reachability unchanged; compilation, diff, and worktree checks |
| 11 | Thieving and Combat arrow outputs, NPC shops, generated Crafting and Fletching equipment, persistence, and undo seams | Opus | 2 | 2 | `9273cf4` | 263 focused; 5 real offscreen Qt; 1,291 full; zero hard test-quality issues; reachability unchanged; compilation, diff, and worktree checks |
| 12 | Consumable producer/consumer identity and state symmetry across Herblore, Cooking, Farming, shops, connected Combat consumption, registry/assets, persistence, and undo | Opus | 8 | 8 | `f794108` | 19 focused; 5 real offscreen Qt; 1,302 full; reachability 1,200 actions/273 orphans; zero hard test-quality issues; compilation, diff, and worktree checks |
| 13 | Save-schema lifecycle, defaults, migration, profile reload, persisted writer/reader symmetry, and direct-action undo | Opus | 5 | 1 | `1fb0b64` | 271 focused; 2 real offscreen Qt; 1,303 full; reachability unchanged at 1,200 actions/273 orphans; zero hard test-quality issues; compilation, diff, and worktree checks |
| 14 | Achievement predicates, production writers, dependency ordering, and exact boundary semantics | Opus | 1 | 1 | `b59c846` | 251 focused; 1 real offscreen Qt; 1,304 full; zero hard test-quality issues; compilation, diff, and worktree checks |
| 15 | Test-oracle integrity against production Shop persistence and Farming UI reachability | Opus | 6 | 2 | `1120fb4` | 242 focused; 183 real offscreen Qt; 1,305 full; zero hard test-quality issues; compilation, diff, and worktree checks |
| 16 | Prayer, Magic, Construction, Thieving, Agility, and Herblore live-surface reachability | Opus | 6 | 8 | `483eb55` | 170 focused core; 8 real offscreen Qt; 1,312 full; zero hard test-quality issues; compilation, diff, and worktree checks |

## Accepted fixes

- The Pit remains unlocked for its six-review active session, while malformed persisted session mappings are removed and cannot bypass the invitation.
- Fatal Agility failures deactivate training and report the established grave or auto-eat consequence.
- Thieving's runtime multi-pick roll now matches the inclusive `random(7)` source denominator of eight outcomes.
- Farming applies its settled watered-disease multiplier and exposes the existing Farming-spell patch selector in the Magic UI.
- Dragonstone enchant inputs use the canonical Crafting item identities.
- Thieving target metadata presents target-specific and wall-safe failure-damage ranges.
- Furnace Crafting now produces canonical unstrung amulet identities, while manual stringing and String Jewellery consume those identities and produce the separately registered strung equipment items. Existing saves keep their ambiguous legacy amulets as strung equipment, preserving the capability they already had.
- The seven unstrung and seven strung amulet assets now use distinct source images, and the asset fetcher can refresh a bounded named subset without re-downloading the full Crafting catalog.
- Lanterns now retain exact unfinished, empty, fuelled-unlit, and lit identities through Smithing, Crafting, one-review lamp-oil preparation, lighting, extinguishing, Thieving drops, shops, equipment, and quest gates.
- Lamp-oil preparation flattens swamp-tar distillation and filling into one explicit zero-XP review without using wall-clock time; candle insertion remains its own zero-XP review.
- Twenty-two distinct state sprites replace shared placeholders, and the generated-data checks cover both Mining helmet states plus the bullseye Smithing output.
- Legacy collapsed inventory names, equipped Mining helmets, persisted Miltog stock, and shop rollback events migrate to exact state names. Intrinsically ambiguous old Oil lamp keys resolve to the empty state so the complete preparation chain remains available.
- Eleven reachable ordinary lit states now replace the `Light source`/`Light sources` parser artifact in eight source-placed quest gates and the Dorgesh-Kaan Agility course. The complete eighteen-item cutoff-era classification remains recorded separately, without advertising unobtainable Seer's headbands or expired event torches.
- Tears of Guthix now preserves its exact safe-source, sapphire-conversion, and lit-sapphire sequence. Watchtower and Another Slice of H.A.M. no longer impose false start gates while their numeric placement remains `source_blocked`.
- Temple of Ikov's visible requirements no longer advertise the deleted pseudo-item, live quest overrides are covered alongside generated rows, and a regression test proves equipped items cannot satisfy consumed alternatives.
- Legacy lantern and Mining helmet names now migrate across carried views and layouts, loot overrides, grave and Death's Office item lists and stored loadouts, and the persisted Magic alchemy selector before carried-state clamping.
- Death reclaim can no longer re-equip an unregistered `Mining helmet` with zero stats or return a phantom bank item after charging the reclaim fee; it restores the exact unlit equipment state in the same session.
- Pottery Apprentice now reads the canonical `Empty pot` identity that Crafting produces and save migration preserves, keeping both it and Living Legend reachable.
- The Monkey general stall now emits the registered `Empty pot` identity instead of a zero-value legacy key that changed on reload.
- Activity Circuit now requires every live Agility activity key, including Flash Powder Factory, instead of accepting any five completion keys or letting Brimhaven substitute for an omitted family.
- AnkiScape's global webview bridge now preserves the incoming `(handled, result)` pair for messages it does not own, so it cannot erase another add-on's successful handler. Its own debug messages are consumed with the documented non-nested tuple shape.
- The bridge reserves a pending menu open before posting its zero-delay timer, so two messages in one event-queue drain cannot enter nested modal loops and overwrite singleton state.
- Profile reload replaces the existing AnkiScape menu and callback instead of appending another top-level menu; the reusable XP popup is likewise no longer recreated on every profile load.
- Main-menu dialogs use Qt's delete-on-close ownership contract, preventing each closed modal and its full widget tree from remaining parented to Anki's main window.
- The accidentally nested, unreachable duplicate bridge handler and its dead wall-clock debounce were removed. Runtime gating remains review-native; no gameplay path gained wall-clock state.
- The unsupported `DeckBrowserContent.links` hook, its orphan helper module, and four tests of a fabricated Anki API were removed. The production `deck_browser_did_render` JavaScript injector remains the single button path with its existing icon.
- Bridge tests now use Anki's real tuple contract and a deterministic timer fake, including regression proof that upstream handled results survive and a double-open schedules one callback.
- Adamantite Artisan and Runite Refiner now read the canonical `Adamant bar` and `Rune bar` identities produced by live Smithing, restoring both achievements and Living Legend reachability.
- Source item 4600 now generates and registers as the single canonical `Willow blackjack` identity used by the live shop, quest reward, Thieving gate, and equipment runtime; the obtainable weapon can be equipped instead of shadowing an unobtainable hyphenated row.
- The reachability graph now includes live Magic and Prayer producers, their rune costs, dynamic bone alternatives, and Prayer byproducts. Charged elemental orbs and Wine of zamorak are no longer false root orphans, and the audit now exposes real downstream Prayer and Onyx dependency chains that were previously outside its graph.
- Live quest normalization now guarantees one completion-sentinel state after the highest requirement row. The 152 generated quests whose last sourced objective previously sat on an unreachable stage now execute that objective before completion; Tears of Guthix, Land of the Goblins, and Hazeel Cult are pinned examples.
- Seven obtainable quest equipment identities now use generated source-config equipment data: Ice arrows, both Temple of Ikov pendants, Gnome amulet, both composite bows, and Dark bow. Their slots, bonuses, attack speeds, two-handed flags, and Ranged level gates are live instead of the Bank advertising items the equipment engine rejected.
- Staff of armadyl now follows source item 84's non-equipment config as a quest material instead of occupying a phantom weapon category, and Ice arrows use the runtime's canonical `ammunition` slot.
- Ranged ammo selection now prefers a compatible loaded stack before considering banked alternatives, so a low-tier arrow drop cannot make a higher-tier loaded quiver report `out_of_ammo` forever.
- Vengeance runes now move through the finite combat loadout, its pending reflection survives review boundaries, reflected kills count and drop normally, and an unnecessary one-book swap selection no longer incurs Spellbook Swap costs.
- Spellbook Swap payment persists for the active fight instead of charging every review, while supplemental rune requirements join ordinary safe-boundary loadout refills for melee, Ranged, and Magic presets.
- Dream remains a between-fights action and cannot consume banked runes to interrupt a live encounter.
- Kept loot earned before a same-review death is moved into the new grave after runtime loot filtering instead of surviving in a recreated carried view.
- Protect Item now preserves the highest store-value equipped item instead of the alphabetically first slot.
- Standard-arrow drops, H.A.M. pickpocket loot, and all live NPC shop rows now produce the canonical plural ammunition identities accepted by equipment and combat. Existing singular save keys and shop rollback events migrate without losing quantities or undo symmetry.
- The checked-in equipment snapshot now contains every live source-generator equipment output from Crafting and Fletching, including 29 previously craftable but rejected items. A synchronization oracle prevents future generator/snapshot drift.
- Kebab consumption now uses the live random source in every production path and records the RNG state needed for deterministic direct-action undo instead of always selecting the zero-effect branch.
- All eight registered supply packs now expose exact Bank `Open` and `Open all` actions, conserve their contents, participate in direct-action undo, and appear as producers in the reachability graph.
- Juju farming potion doses 1 through 4 can now be activated from the Farming surface, consume and preserve exact doses, apply the settled review-native farm-clock effect, and use complete registry/assets/provenance coverage.
- Magic essence potion creation now emits the source-convergent `Magic essence mix (2)` identity rather than the conflicting `Magic potion (2)` transcription. The pinned cache item ID, recipe input, and consumption handler all converge on item 11489.
- Shop resale now honors registry `tradeable=False`; Agility potion and mix dose families have canonical IDs and tradeability; Kebab and Half summer pie are food rather than Herblore products; and Summer pie uses the Bank's `Eat` verb.
- Combat presets now contain configuration only. The finite `combat_supply_loadout` is neither snapshotted into new presets nor restored from legacy preset payloads, so target pins cannot mint consumed food, ammunition, runes, or potions or delete a freshly refilled pack on the next review.
- Achievement dispatch now evaluates newly satisfied predicates to a fixed point. Living Legend unlocks atomically with the final ordinary achievement instead of requiring an unrelated later action to trigger a second check.
- Shop purchases, sales, services, Bob Barter decanting, stock/history changes, currency, and Wilderness consequences now call the canonical player-data save boundary immediately instead of surviving only in memory until an unrelated later save.
- The Farming sheet now exposes the already-implemented Juju farming potion action, chooses the fullest owned dose first, shows the active review-native harvest bonus state, and preserves the next dose through the existing pure action boundary.
- The review HUD now resolves friendly names for Herblore, Prayer, Magic, Construction, Thieving, and Agility instead of exposing their stable IDs.
- An equipped Willow blackjack now satisfies the Thieving target gate, matching the runtime's ordinary equipment semantics.
- Agility exposes all five sourced Brimhaven XP exchanges, reports command outcomes, rerenders after direct actions, and ends a paid Brimhaven stint when the player changes target or stops training.
- Construction purchase, room, servant, and style actions report success or rejection and immediately refresh the house sheet. Magic prerequisite pickers and Thieving/Agility target changes likewise rebuild dependent readiness state instead of leaving stale rows or Train buttons.

## Rejected candidates

- A future change to Thieving stall respawn data could invalidate persisted cadence credit. Current shipped data does not do so, and save migration is required only with such a data change; no speculative runtime catch was added.
- Dragonstone jewellery inputs remain intentionally acquisition-blocked, as already recorded in Crafting data; this is not a newly unreachable identity.
- Legacy `Gold amulet`-style save keys were not migrated to `(u)` keys. Before this repair those keys could already be equipped and enchanted, so treating them as strung preserves player capability; only newly smelted amulets use the unstrung identities.
- Fable's claim that cave-goblin pickpocketing drops unfinished bullseye item 4544 was rejected: Darkan's exact `pp_cavegoblin.json` row uses fuelled-unlit item 4548. The implemented Thieving key follows that exact ID.
- A full regeneration of shop and equipment snapshots was rejected because the local external source trees had unrelated drift. The pinned generated snapshots received only the exact lantern-state corrections, and their existing coverage-count tests remain unchanged.
- Opus's stage-map clamp suggestion was rejected as prospective hardening: every current explicit stage is within the pinned quest's stage count, so no present failure exists.
- Opus's Tears stage-2 option-wipe suggestion was likewise rejected as hypothetical parser drift. The current pinned parse places the light-source group at stage 1 and has no legitimate stage-2 alternative to preserve.
- The pass-2 decision not to migrate `Gold amulet`-style names was rechecked and retained: those are still valid strung equipment identities, not collapsed legacy aliases.
- Bob Barter's current dose and vial math was independently traced and retained: every supported target dose conserves total doses and containers, produces a strictly smaller remainder, remains review-neutral, and rolls back through its independent shop event.
- Renaming the Stats tab's later `initial_skill` local was rejected as prospective cleanup: the only closure read executes before that assignment, so no current behavior fails.
- Worktree-guard handling for a missing canonical `meta.json`, a future canonical checkout outside `addons21`, or a hand-copied meta-less duplicate was not changed. None occurs in the current registered layout, and the guard's present audit/add paths remain correct and non-destructive.
- Twelve generated equipment rows that are absent from the item registry were not bulk-registered: none is currently obtainable through a live producer, reward, or shop, so doing so would expose new gameplay rather than repair a writer/reader mismatch.
- Ground suqah tooth was not activated independently because its only current consumer is the intentionally source-blocked Spirit tree path.
- Empty sack and basket filling was not added speculatively: the existing Farming contract records those acquisition inputs as blocked rather than promising a live writer/reader path in this pass.
- Bake Pie's mud-pie handling remains in Magic, where its target and inputs are internally consistent; moving it into Cooking would be a product expansion rather than a repair.
- Fertile Soil's XP magnitude was not changed because the reviewer supplied no source-contract mismatch; its value remains a design/parity question, not a reproduced implementation failure.
- Six Magic keys omitted from fresh-player defaults, three lazily created Prayer/Magic side-state keys, and the retired hidden-Agility default helper were recorded as schema asymmetries but not changed: all current readers provide matching defaults and no player-visible failure reproduces.
- Source-blocked Thieving target IDs remain accepted by the load sanitizer because no live UI/runtime writer can persist those IDs; changing that dormant boundary was rejected without a current failure path.
- Stale cross-profile undo snapshots were independently rejected: every answered review advances the shop clock before snapshot recording, preserving one snapshot per generic Anki Answer undo operation and keeping the LIFO stacks aligned.
- Construction tablets contributing to Construction output counters was retained as an unsettled adjacent-method semantic rather than relabeled as a runtime failure: the Construction surface owns the output while the settled contract assigns Magic XP.
- Rune Essence Baron remains reachable through live combat drops after level 30 changes Mining output to Pure essence. Its description-to-route mismatch belongs with the catalog-wide held-item achievement semantics review, not a one-off counter rewrite.
- Jack of All Ores and Flawless Footing have difficulty labels below their required skill levels, but the existing achievement design explicitly defers a full difficulty rebalance. No isolated relabel was made without that catalog-wide decision.
- Living Legend's legacy list-length condition was not hardened against fabricated stale or duplicate names because no live writer or shipped migration produces them. The reproduced same-dispatch dependency failure was fixed independently.
- The HUD cleanup and global-bridge pending-latch branches identified by the pass-15 reviewer remain unreachable under the current production ownership contracts; no speculative cleanup was added without a failing path.
- The reachability test's broad action-count floor and partial generated-snapshot oracles were not tightened just to mirror today's exact counts. Existing semantic checks still catch current drift, and pinning incidental totals would add brittle test volume without protecting a reproduced behavior.
- Always-enabled Magic and Construction Train buttons were not converted to speculative whole-skill gates: review runtime already deactivates unavailable targets, while this pass repaired the concrete stale selector and house-action failures.

## Queued confirmed defects

None. The next pass rotates away from the six repaired skill surfaces rather than carrying an unverified candidate forward.

## Reviewer budget and availability

- Live Claude `/usage` reached 30% for Fable after the pass-3 review attempt, so no further Fable calls are permitted in this overnight run.
- The post-implementation Fable review exhausted the current Claude session before returning a verdict. An immediate Opus fallback was also blocked by the same account-wide session window and made no tool calls. Codex therefore accepted pass 3 only after its own full diff audit, targeted checks, full Python suite, real offscreen Qt suite, reachability comparison, compilation, diff check, and worktree audit. Opus resumes after the session reset.
- Pass 4 used one successful read-only Opus workflow after the session reset (`2d78f29f-d957-4bee-bf90-389253cf7125`). The required pre/post live checks both reported Fable at 30%; no Fable review call was made.
- Pass 5 used one successful read-only Opus workflow (`707070c2-c80d-4a36-a7d3-ad297f8669ab`). The required pre/post live checks again reported Fable at 30%.
- Pass 6 used one successful read-only Opus workflow (`f9ddb28f-9257-473a-afee-40ddf738d09a`). The required pre/post live checks again reported Fable at 30%, so the Fable cap remains closed.
- Pass 7 used one successful read-only Opus workflow (`0a9b2e49-9a95-4668-a9a5-8da61341607c`). The required pre/post live checks again reported Fable at 30%.
- Pass 8 used one successful read-only Opus workflow (`cfaade17-3598-450d-beb9-93ede931fa1b`). The required pre/post live checks again reported Fable at 30%; the all-model weekly reading rose to 17%, but no Fable review was made.
- Pass 9 used one successful read-only Opus workflow (`83a95201-9995-4f32-aa04-1c5280f9d7b6`). The required pre/post live checks both reported Fable at 30% and all-model weekly usage at 17%, so no Fable review was made.
- Pass 10 used one successful read-only Opus workflow (`fd4455dd-351c-4314-a98b-74af0726be7f`). The required pre/post live checks both reported Fable at 30% and all-model weekly usage at 17%; the Opus reviewer supplied three candidates, all independently reproduced, while Codex found and repaired three additional defects in the same bounded combat state path.
- Pass 11 used one successful read-only Opus workflow (`c3bb074e-f91d-472e-b62d-03fc23390dbc`). The required pre/post live checks both reported Fable at 30% and all-model weekly usage at 17%; the reviewer exposed the NPC-shop ammunition producer failure and its blind oracle, while Codex independently found matching Thieving and Combat producers plus a stale generated-equipment snapshot.
- Pass 12 used one successful read-only Opus workflow (`3f35b73d-08d0-41bc-91a9-213f0e3afde0`). The required pre/post live checks both reported Fable at 30%; all-model weekly usage rose from 17% to 18%. Six reviewer candidates were independently reproduced, and Codex found the missing supply-pack runtime plus the stronger cache-and-emulator resolution of the Magic essence mix identity conflict.
- Pass 13 used one successful read-only Opus workflow (`3007fcda-2065-4cb2-b806-cca2a0e98ce0`). The required pre/post live checks both reported Fable at 30% and all-model weekly usage at 18%; current-session usage rose from 17% to 20%. The reviewer supplied one material finite-supply exploit and four explicit non-failing asymmetries; Codex reproduced and fixed only the exploit.
- Pass 14 used one successful read-only Opus workflow (`62af823b-8024-4fda-b0bf-c9bf946c9161`). The required pre/post live checks both reported Fable at 30%; all-model weekly usage rose from 18% to 19% and current-session usage from 20% to 25%. The reviewer found no material writer mismatch, while Codex independently reproduced and fixed the same-dispatch Living Legend dependency defect that the predicate-only tests missed.
- Pass 15 used one successful read-only Opus workflow (`4f00a73a-0ac0-4bfd-bd81-c6f6a2788b85`). The required pre/post live checks both reported Fable at 30% and all-model weekly usage at 19%; current-session usage rose from 25% to 28%. The reviewer exposed the missing Juju Farming control but underrated it against the recorded acceptance claim; Codex reproduced that UI omission and independently found the stronger unsaved Shop mutation path.
- Pass 16 used one successful read-only Opus workflow (`03135f05-b39a-47bb-a2e2-d271a30e4399`). The pre-check reported current-session 0%, all-model weekly 19%, and Fable 30%; the post-check reported 8%, 20%, and 31% respectively. The reviewer supplied six concrete surface defects; Codex reproduced all six and independently found the matching stale Magic prerequisite and target-readiness refresh paths.

## Closure

Pending.
