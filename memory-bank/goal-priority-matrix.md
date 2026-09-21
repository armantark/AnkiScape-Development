# Goal priority matrix

## Authority and selection

The active contract is [the settled implementation goal](plans/goal-2026-09-05.md). The owner requires cleanup before feature work. Finish the approved responsibility splits, then simplify the exposed functions, largest first, while preserving behavior. Owner rulings §47, §48, §53, §55, §57 and §58 govern this work. The [complete scope inventory](source-audits/exposed-complexity-2026-09-05.md) covers fourteen source families; its measurements are historical, not current gate results. Untouched Farming is outside that scope.

The orchestrator selects slices and promotes verified merged trees. Dispatched authors work in leased `goal/*` worktrees. Keep tests, audits, limits and pinned baselines as fixed instruments. Require focused coverage, both full remote lanes, independent cross-lineage review and all promotion checks. Do not push. Existing UI changes remain excluded; contained new feature UI requires a taste-qualified author.

The [resume reconciliation record](source-audits/resume-queue-reconciliation-2026-09-18.md) binds this queue to inspected source and Git ancestry. Dated checkpoints and the previous matrix text live in [progress](progress.md). The goal remains unfinished. The owner explicitly resumed the goal on 2026-09-21 in Codex task `01a072a4-e63c-7f50-b40c-1381515649f2`. Complete the [handoff](handoffs/fable-grill-papercuts-2026-09-21-decisions.md) in order 4, 1, 5, 6, 2, 3, then return to gameplay. Step 1 already landed as `f7c0c7a9` before the new ordering decision. No restart is scheduled. Cleanup remains eligible, and no common blocker prevents all work. A source or owner block stops only its named unit. The [September 18 checkpoint](pause-checkpoint-2026-09-18.md) is history; the September 21 owner decisions govern current work.

Evidence rule (grill decision 12, 2026-09-21): a slice commits its gate receipt and a summary of at most 30 lines with the digest of each raw artifact; raw logs, canaries, diffs and screenshots live in the out-of-tree evidence directory keyed by commit hash, and no slice writes its own runner or checker script. Pace meter (decision 15): product landings per active orchestrator day from the landing receipts, target 10, reported at each pause. Rotation rule (decision 13): on the first session of each month, move the previous month's progress-log sections and shipped kanban cards older than 30 days into `memory-bank/archive/`.

Disposition meanings: `eligible` has a settled action; `verification_pending` lacks a required acceptance check; `source_blocked` lacks exact evidence; `dependency_blocked` waits for a named substrate; `integration_blocked` fails a fixed gate or lacks a suitable boundary; `owner_gated` needs a named owner decision; `excluded_ui` falls outside this goal; `deferred_data_depth` follows higher priorities; `closed` needs no implementation; `preserve` forbids blind adoption or removal.

## Current selection

| Priority | Unit | Disposition | Next action and acceptance boundary |
| --- | --- | --- | --- |
| 0 | Combat-magic responsibility extraction | `integration_blocked`; source candidate preserved | Source `a8137bab2566b45e52585c580794a84563241b7e` in P8 passed both focused lanes and complete differential comparisons, but its full source gate failed unchanged module-surface pins. Preserve the clean source branch and exact failures in [the wrap-up evidence](source-audits/combat-magic-wrap-up-2026-09-18/README.md). The owner has reserved the choice to merge or rework this candidate. Do not merge, rebase or rework it. Handoff step 4 runs its digest as evidence only. The old dirty P6 candidate remains preserved. No Magic landing is accepted. |
| 0 | Remaining exposed-function cleanup | `eligible`, largest first | Continue combat decomposition and the remaining functions within the fourteen-family inventory. Retain root dispatcher relocation as a separate obligation from the landed shared-state prerequisite. Retain the carried, activity, shop, quest, roster, constants, diary-generator and promotion-tool families until their scoped obligations close. Re-measure with the installed gate before selecting each boundary. Source spans and earlier green regression gates do not prove threshold closure. Shop-UI source responsibility remains recorded, but this goal authorizes no existing-UI change. |
| 0 | Shared real-reviewer acceptance | `verification_pending` | Owner §55 requires one native reviewer pass for item 2, the dispatcher seam and 2c's deferred popup after landing and before Bill (2b) ships. The retained native packet proves the guarded route and collection isolation, not an answer/undo pass or an exact loaded revision. The root owns native coordination. The September 21 owner decision also requires a native check for each new landed slice; MacBook sign-in is pending. |
| 1 | Dream transaction extraction | `dependency_blocked`; architectural boundary selected only | The [retained revised contract](source-audits/combat-dream-boundary-2026-09-18/README.md) selects `_apply_dream_transaction(data, dream_cost, max_lp_for_dream)`, which returns a result or `None`. The Magic module prerequisite is unlanded; no Dream implementation is authorized and no gate result exists. The caller retains eligibility, derived values, the final-result write and the early return. Preserve the exact revised contract, including falsy-only inventory normalization, raw debit behavior, result identity and dependency direction. |
| 1 | Remaining carried gathering settlement | `integration_blocked` for the rejected broad helper | KEEP folding is landed. The broader eight-parameter Keep/Drop candidate failed cognitive `17 > 15`; retain both rejected forms. Re-measure the current remainder, then obtain review of a smaller responsibility boundary. Do not replay the old patch, add helpers merely to bypass the gate, or change the instrument. |
| 2 | Native fixture `goal/native-review-fixture-2026-09-05`, `f7f9d505df9ae830e3a6253047bac4a4aa797078` | `verification_pending`, parked behind cleanup | Its predecessor `68f628ca` passed the historical branch gate; the later documentation-only head has no established new gate. The branch-qualified audit `memory-bank/audits/native-review-fixture-2026-09-05.md` defines reviewer selection, answer, undo and material-exhaustion checks. Keep that pending contract distinct from menu checks. Advance the fixture only if required for the shared pass; route proof does not accept this branch. |
| 3 | Emerald sickle | `dependency_blocked` | The Myreque chain must provide a real player route to Legacy of Seergaze stage 6. Preserve `refs/preserved/emerald-sickle-2026-09-17` (`85c610ed`). Its mechanics have retained proof, but its products were unreachable. Do not adopt the attempt's unrequested `tools/audit_item_reachability.py` split. |
| 3 | Silvthrill rod and Fremennik round shield | `source_blocked` | Resolve the rod transition among `7620`, `7637` and `7638`, and the shield-specific Woodcutting conflict `54` versus `56`. The [genuine-action contract](source-audits/genuine-quest-actions-2026-09-05/contract-and-plan.md) retains the settled recipes, real acquisition order, stage gates and proof requirements. Do not invent identities or choose a contradictory threshold. |
| 3 | Full Ghosts Ahoy | `source_blocked`; prerequisite `closed` | Both The Restless Ghost and Priest in Peril are enforced. Full requirements, route values, rewards and downstream unlocks remain unrecovered. The former oversized-generator prerequisite is obsolete. |
| 3 | Frost dragon bone route identity | `source_blocked` | Preserve item IDs `18830` and `18832` until a period source maps each to the Asgarnian Ice Dungeon or Daemonheim route. A matching name or client-cache identity does not settle the mapping. |
| 3 | Beefy Bill banking | `source_blocked` | The settled shop-service surface does not settle the fee, accepted items, rounding, transfers or gates. Preserve the existing shop. The [service harvest](source-audits/beefy-bill-service-harvest-2026-09-01.md) forbids treating the wiki's 10% statement as qualified mechanics. Native reviewer acceptance also remains a prerequisite before this service ships. |
| 3 | Horror from the Deep | `source_blocked` for remaining quest mechanics | Barcrawl completion and its prerequisite link are live. Keep unrecovered mother combat stats and other exact values blocked under the [harvest](source-audits/horror-from-the-deep-harvest-2026-09-02.md). Do not reopen Barcrawl as an implementation dependency. |
| 3 | Barcrawl effects and card loss | `source_blocked`; card recovery also `owner_gated` | The ten venue deeds, start/card, completion and Outpost unlock are live. Drink drains, damage, timing and dialogue remain outside the qualified route. Card-loss detection, replacement timing and progress policy remain unsettled in `design-thread-queue.md`; do not invent recovery or claim a demonstrated softlock. |
| 3 | Missing quest combat stats | `source_blocked` | Re-measure current coverage, then select one qualified bundle with source ownership assigned by the root. The Pass 13 census is historical. Do not derive combat stats from display level. All fights retain the persistent shared engine. |
| 3 | Remaining item tradeability metadata | `source_blocked` where no qualified source exists | Pouches, Archery ticket, Crayfish, Spotted cape, Spottier cape, Jade, Red topaz and Oyster have landed corrections. Reconcile any other named item against live data and its period source; old cohort arithmetic is not a current census. No shop or Grand Exchange redesign is authorized. |
| 3 | Fish Flingers payout and requested rollback | `source_blocked` | The mechanics and per-game records are live, but `fish_flingers.xp_payout` remains registered. A qualified post-2012-07-24/pre-cutoff payout and weight distribution must replace the reconstruction before an exact rollback can be calculated. |
| 4 | Generated quest sentinels and acquisition roots | `eligible` for bounded remeasurement after cleanup | Rank through the existing reachability instrument and actual player gates. Reuse pinned contracts. Distinguish startable from completable; seeded completion or proof flags do not establish acquisition. |
| 4 | Registered placeholders and newly recovered period values | `source_blocked` until each exact row has new evidence | [The placeholder register](placeholder-values.md) retains every family and its settlement condition. Select a bounded row only with a new evidence lever. Client identities do not prove server behavior. Keep source claims with the root; do not repeat exhausted sweeps or invent rates. |
| 5 | Remaining catalog, skill, activity, boss, reward, combat and rate depth | `deferred_data_depth`, with per-unit source/dependency gates | Breadth is closed. Rank a concrete player-reachable addition under its current contract after higher priorities. The class and gap-ledger tables below retain remaining depth obligations. |
| 5 | Dormant diary systems | `dependency_blocked` on named planned systems | Recheck each ledger group against its real planned contract. Do not use unsupported place or transport substitutes. Gate 2 is passed by reviewed spec-conformance; owner spot-check feedback is patch work, not a pre-wiring approval gate. Retain the named `varrock_hard_but_it_won_t_warp_you_anywhere` and `morytania_medium_izzy_wizzy_let_s_get_lizzy` feedback items. |
| 5 | Upstream AnkiScape 3.0 ideas: review-log catch-up, save outside collection config, export and restore, redo | `eligible` after cleanup; the save relocation is `owner_gated` | The kanban card "Upstream ideas from AnkiScape 3.0 — 2026-09-19" holds the accepted list and the upstream references. Review-log catch-up, export and restore, and redo are determined by Anki's own data and go straight to spec. The save relocation changes the save model: it ends the `ankiscape_player_data` collision with the original add-on, but two desktops that sync one collection and the migration of every existing save need one grill with the owner before implementation. |
| Separate | Stale Barcrawl journal and truncated main-menu navigation | `owner_gated`; existing UI `excluded_ui` | Preserve the [native evidence](evidence/native-verification-2026-09-17/README.md). No reliable journal recovery is established. Navigation truncation follows owner-settled removals of tab styling; do not revive the preserved fix branches. Changes require owner approval and a frontend-taste model. |
| Separate | Other existing UI, art, quest-boss HUD, Collections, search/help and accessibility | `excluded_ui` | Keep the kanban and design records. No icon batch, widget edit or old UI branch promotion is authorized by this goal. |
| Separate | Lease release and duplicate-branch guard proposals | Proposed; no implementation authorization | A release proposal would hold the promotion lock through detach/return, disable stale recovery, and refuse matching or unreadable markers without signals or cleanup. A lease proposal would reject a duplicate branch before allocation. The root decides a separate follow-up; do not treat proposals as assigned work. |
| Separate | Papercut triage, menu-open performance, release and standalone travel | Unassigned / `parked` / `excluded` | Papercut triage needs a separate assignment; old quota prose is not a live quota signal. Menu-open performance remains on the kanban under its owner target. No publication, transport system, post-cutoff content or remote push is authorized. |

## Closed implementation and route work

These changes are on the audited main. Preserve their receipts and source records; do not repeat implementation from stale queue text. Shared reviewer acceptance remains separate.

| Unit | Landed evidence |
| --- | --- |
| Portable Barcrawl generator fixture | `0bd11b878969a513c61c5080c5c32cf63741976a`; full source evidence retained; inclusion in canonical main is established by the final promotion receipt and ancestry |
| Root verification instrument and constants | `1932b3c0`, `9f54377b`, accepted main `518a651d` |
| Dispatcher shared state | `4fd93b0b`; the rejected globals-rebinding relocation is not accepted |
| Quest-data, shop and roster splits | `f00f510e`, `0005e1cb`, `6aeebc6c` |
| Combat rewards and enemy/player attack rolls; carried processing | `7e19aadf`, `afae5ee6` |
| Unequip, Vampyre bite, Wyvern breath, dragonfire and papercut queue recency | Combined main `6dacde54` |
| Prayer drain, bank-trip initialization and activity selector | Combined main `1bf2cfe2` |
| Enemy poison, KEEP folding, death-prayer and combat food module | Sources `5eaaf97a`, `441a1c70`, `c225c456`, `d87e51be`; combined `d1dbebf6`; landing `9f0f059f` |
| Pass 14 encounter changes and Slayer completion | `a6622434`, `641f6608`; the parked-orchestrator hold is cleared |
| Barcrawl contained route and downstream prerequisite links | `3a14d435` |
| Capes and cut gems | `074b9cd2` |
| Crayfish, Archery ticket, pouches and retained shop proof repair | `889d1cc7`, `af4ca7cb`; keep legacy-save migration separate |
| Quest-combat relocation | `3d432b55`, in `data/quest/combat_relocation.py` |
| Skippy and the Mogres, Mogre lure and nettle-tea chain | `9b933084`; title correction `3797bb7f` |
| Oyster period tradeability | `60e2aa2d`, surface record `f60b5d6d` |
| Ghosts Ahoy prerequisite | `c276ef40`; full quest remains source-blocked |
| Native route and collection-isolation guard | `49899700`; retained packet `170244d8`; route closure is not programme acceptance |
| Evil Tree refresh diagnosis | `SEEDED_INDIRECT_REFRESH_CORRECT`; the stale control omitted recovery state. No product defect was reproduced. Do not redispatch. |
| Diary ledger wiring | Gate 2 passed by reviewed spec-conformance. New owner corrections require ledger patches and regeneration. |

## Preserved branches and candidates

An unmerged ref does not prove that its behavior is absent from main. A past gate does not accept a different source tree. No accepted-but-unmerged implementation was established by the resume audit.

| Ref or work | Disposition |
| --- | --- |
| `goal/combat-magic-module-2026-09-08` and its dirty P6 candidate | Preserve. The branch head `c225c456` is landed; the uncommitted magic extraction is separate source-preparation evidence. P8 owns recovery onto current main. |
| `goal/native-review-fixture-2026-09-05` | Parked verification candidate under the current selection table. |
| `refs/preserved/emerald-sickle-2026-09-17` | Preserve the dependency-blocked attempt and exclude its unwanted reachability-tool split from any later adoption. |
| `goal/cape-tradeability-2026-09-05`, `goal/cut-gem-tradeability-2026-09-05` | Their content is on main at `074b9cd2`; do not replay their stale layouts. |
| `goal/crayfish-tradeability-implementation-2026-09-05`, `goal/archery-ticket-tradeability-2026-09-05` | Their content is on main at `889d1cc7`. |
| `goal/retained-shop-proofs-2026-09-05` | Its repair is on main at `af4ca7cb`. |
| `goal/quest-combat-relocation-2026-09-05`, `goal/skippy-mogres-2026-09-01` | Their valid behavior was ported to main at `3d432b55` and `9b933084`; do not merge the old branches as-is. Skippy override `a82c6471` remains excluded. |
| `goal/matrix-reaudit-2026-09-16` and the tradeability source refs | Superseded reconciliation or retained source evidence; they do not establish outstanding implementation. |
| `goal/split-init-dispatchers-2026-09-02`, `goal/split-batch-2-2026-09-02`, `goal/dispatcher-seam-2026-09-02`, `refs/preserved/init-dispatchers-2026-09-02` | Preserve rejected globals-rebinding designs and their evidence. Only genuine state/module boundaries can replace them. |
| `goal/secondaries-2026-08-11`, `goal/secondaries-reland-2026-08-25` | Preserve rejected or superseded attempts. Any surviving chain needs fresh source and real-player reachability proof. |
| `goal/diary-ledger-wiring-2026-09-01`, `goal/stage-satisfiability-2026-08-13` | Superseded merge/documentation records; no missing implementation is inferred. |
| `goal/full-main-tab-labels-2026-08-27`, `goal/full-main-tab-labels-ready-2026-08-27`, `goal/native-tab-overflow` | Existing UI excluded; preserve and do not promote. |
| `goal/remote-promotion-gate-2026-08-27`, `goal/remote-promotion-gate-revised-2026-08-27`, `goal/remote-promotion-gate-final-2026-08-27` | Historical tooling candidates. Current tools supersede them; never replay whole branches. |
| `goal/split-constants-2026-09-02`; preserved quest-data, roster-test and diary-catalog refs | Retain earlier source and dirty drafts. Their accepted successors are separate; recheck any proposed residual before adoption. |
| Other dirty work, `backup/*`, `promote*`, `scratch/*`, `verify/*`, and `daily-challenge-xp-depth` | Preserve. Historical path counts are not current state. These refs require overlap/source review, not automatic dispatch or deletion. |

## Remaining depth classes

The kanban, gap backlog, placeholder register and named source audits retain individual contracts. Their earlier whole-family status labels do not override newer live slices.

| Class | Disposition and next action |
| --- | --- |
| Agility, Thieving, Farming, Hunter, Slayer bestiary and master readiness | Keep each absent server value source-blocked and each missing gear, quest or acquisition route dependency-blocked. Existing live sub-slices do not close the whole family. |
| Summoning familiars, pets, effects and teleport consumers | Deferred depth with exact source/dependency gates. Client definitions do not prove hidden effects; transport-only behavior remains excluded. |
| Dungeoneering stats, scaling and unopened skill consumers | Keep source/dependency gates. Preserve live Frozen-floor, kinship, binds and economy behavior; do not label non-Frozen content or generated stats recovered. |
| Activities, minigame rewards, bosses, drops and rare selectors | Deferred depth. Select one obtainable source-backed row and all consumers, not an exhaustive harvest from an old queue. |
| Acquisition roots, item identities, equipment and held-item processing | Eligible for bounded remeasurement after cleanup. Prove actual player access and rank transitive gain; counts alone do not prove completion. |
| Diary tiers, clue steps, collections and one-time content | Deferred depth. Keep diary curation rules and real planned dependencies; existing Collections UI remains excluded. |
| Random events and timed world content | Design-blocked where visibility, interruption or expiry remains unruled. The shared review clock does not settle those choices. |
| Artisan rates, special-method rates and modifiers | Keep source/depth gates and cited cadence. Do not invent XP/hour or modify calibrated machinery. |
| Period art, unresolved sprites, Fancy/fighter boots | Existing-UI asset work excluded. Old exhausted-art lists do not authorize another harvest. |
| Search/help, polish, accessibility, modern comparator and public release | Existing UI excluded; the comparator has no parity authority; release remains parked. |

## Existing-skill gap obligations

Read `gap-backlog.json` per consumer. Its stored status labels are ledger evidence, not a fresh runtime audit.

| Item | Current boundary |
| --- | --- |
| `hunter-tracking-pitfall-snare`, `hunter-habitat-jadinko` | Live tracking/Jadinko/vine sub-slices supersede old whole-family blocks. Remaining selectors and absent targets need their own source proof. |
| `hunter-grenwall-herb-table`, `rc-runespan`, `rc-abyss`, `fm-bonfires`, `smith-artisan-burial` | Retain each exact source/design gate. Modern reconstructions do not establish period behavior. |
| `rc-method-selection` | Settled parent design. Reproduce a concrete missing route before dispatch; existing selector changes remain excluded UI. |
| `smith-blastfurnace-goldsmith` | Cannonballs are closed. Blast Furnace and Goldsmith require their named source/runtime dependencies. |
| `cook-karambwan-family`, `cook-cooking-gauntlets-runtime` | Implementation closed; retain the registered hidden burn curves or omitted intermediate reductions. |
| `fletch-javelin-construction`, `wc-canoe-shaping` | Excluded out-of-period construction and standalone transportation. |
| `herb-overload-sanfew` | Overload is closed. Sanfew, poison and application claims need a current consumer audit and qualified source. |
| `wc-arctic-euc-cursed` | Arctic pine and Eucalyptus are live. Cursed magic needs Spirit of Summer; hidden live-tree rates remain registered. |
| `rc-zmi-gop-wickedhood` | Great Orb and Wicked hood mechanics exist. Ourania selector/source gaps and Runespan reward acquisition remain separate. |
| `mine-lrc-stars` | Living rock remains and expanded Shooting Stars are closed; retain unresolved roll/range/source debt. |
| `fish-trawler-flingers` | Mechanics exist. Keep the registered Fish Flingers payout and check current runtime before any rate claim. |
| `fm-pyres-beacons` | Shades mechanics exist; separate remaining Beacon/pyre timing and catalog debt. |
| `artisan-skill-potion-runtime` | Implementation closed. |
| `fm-barbarian-bow-lighting` | The learned-flag writer belongs to Barbarian Training. Keep the dependency; no instant-completion shortcut. |

## Completion rule

The root must obtain a fresh queue audit before goal closure. It must show no eligible implementation and no accepted unmerged slice. Missing native reviewer acceptance remains explicit. If a genuine common blocker prevents all eligible work, create a new exact-evidence blocker record. Do not revive the removed stale whole-goal claim.
