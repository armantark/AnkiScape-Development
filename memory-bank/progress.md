# Progress

## Current Baseline — 2026-07-16

AnkiScape now has 18 complete skill surfaces, five partial Combat-trained skills, and two planned skills. Canonical live status is in `future-work-kanban.md`; the dated 2026-07-10 completion audit is archived baseline evidence.

## Slayer Spiritual-family authority stop — 2026-07-19

- Stopped before source-to-runtime implementation because the settled Sumona,
  Duradel/Lapalok, and Kuradal records require four god variants, while the
  supposedly complete registry names only one Saradomin target for each of the
  Spiritual-mage and Spiritual-warrior families.
- Confirmed rev-727 independently exposes four attackable identities per
  generic family. The rev-742 exact-name surface differs and therefore needs
  later source reconciliation rather than an inferred variant collapse.
- Left both families non-certifying at `combat_target`; no target-local God
  Wars context, Combat row, asset, or test was changed.
- Sumona remains hidden and unrenormalized at 20/37. Durable conflict record:
  `audits/slayer-spiritual-families-registry-conflict-2026-07-19.md`.

## Slayer Terror-dog source boundary — 2026-07-19

- Closed the ordinary level-110 identity, real combat levels, Slayer-40 gate
  and 87 XP, six-tick melee, 150 approximate maximum, Haunted Mine route,
  target-local Prayer drain, Big-bones split, Granite helm, cache IDs, and
  named drop set.
- Reproduced Darkan's exact 128-slot selector and found a material conflict:
  five slots yield Coins ×11, while every quantity-bearing pre-cutoff article
  revision permits only ×44–200 and later ×440.
- Inspected all 329 pre-cutoff article revisions plus the cutoff talk record;
  neither supplies or validates ×11. The talk page independently confirms the
  level-110 Big-bones split.
- Left `terror_dog`, its two-tick Prayer residual, Granite-helm item/asset, and
  all tests untouched rather than cherry-picking around the conflict. Sumona
  remains hidden and unrenormalized at 20/37.
- No owner-facing design decision is pending. Durable evidence:
  `source-audits/slayer-terror-dog-combat-2026-07-19.md`.

## Slayer Mutated-jadinko authority/source stop — 2026-07-19

- Stopped before implementation because all three settled master-pool records
  define baby, guard, and male variants at Slayer 80/86/91, while the runtime
  registry contains only the baby behind a family-level Slayer-80 gate.
- Confirmed the cutoff family page and both rev-727/rev-742 caches independently
  enumerate all three identities, so a baby-only readiness certificate would
  be false.
- Harvested all three cutoff LP/XP/style/speed/maximum envelopes, cache IDs,
  Darkan definitions, and drop leads without changing runtime.
- Kept every variant source-blocked: all three Darkan combat definitions are
  explicitly `nostats`, no independent implementation supplies the five
  combat levels, and Darkan's guaranteed Mutated-vine/Excrescence quantities
  conflict with the cutoff pages.
- Sumona remains hidden and unrenormalized at 20/37. This is an authority
  conflict plus a source dependency, not a creative-design fork. Evidence:
  `audits/slayer-mutated-jadinko-registry-conflict-2026-07-19.md` and
  `source-audits/slayer-mutated-jadinko-combat-2026-07-19.md`.

## Slayer Fever-spider source boundary — 2026-07-19

- Closed the source-ready Fever-spider identity, route, protection, ordinary
  drop-selector, and quest-only body boundaries.
- Reproduced a material disease conflict: the cutoff requires three Relicym's
  balm doses, while Darkan's disclosed severity-15/four-point reconstruction
  requires four. The exact unprotected hit formula is likewise not period
  closed.
- Left `fever_spider` absent rather than shipping persuasive but unsupported
  disease numbers. Chaeldar remains hidden at 25/34 with the same nine
  blockers; no design decision is pending.
- Recorded the no-session Workflows run
  `f2c763f0-4b3b-4ee7-abd6-6273dd05c186` and completed the audit independently.

## Slayer Elf warrior Combat closure — 2026-07-19

- Added separate ordinary level-90 ranged and level-108 melee Elf-warrior
  targets with exact period LP, Slayer XP, six-tick cadence, maximum hits, and
  completed-Regicide access.
- Preserved Darkan's hidden combat levels, exact defences, 39-tick respawn,
  guaranteed Bones, one 128-slot ordinary selector, the losslessly enumerated
  1,212-slot charm selector, and an independent 1/128 hard clue.
- Registered the unstackable, untradeable Crystal teleport seed and labeled
  the no-position combination of Lletya crystal drops and Elf-Camp charms as a
  location-flattening abstraction.
- Pinned distinct archived 2010 ranged and melee sprites while preserving
  their honest post-migration upload timestamps in provenance.
- Advanced Chaeldar to 25/34 while leaving its partial pool hidden and
  unrenormalized. Nine Combat-family blockers remain.
- No owner-facing design fork emerged. Durable evidence:
  `source-audits/slayer-elf-warrior-combat-2026-07-19.md`.
- Focused Combat/Slayer/metadata coverage passes 361 tests, and the focused
  real offscreen Qt picker passes.
- Full non-Qt discovery passes all 1,679 tests with 215 declared environment
  skips; full real offscreen Qt discovery passes all 1,679 tests with zero
  skips or failures. Test quality has zero hard issues across 73 files and
  1,679 methods. Reachability remains at 1,253 actions, 1,866 reachable items,
  288 orphan inputs, and 313 blocked actions.
- Documentation, compilation, provenance JSON, diff, readiness,
  declared-baseline reachability, and worktree-safety gates pass.
- Results:
  `status-updates/slayer-elf-warrior-results-2026-07-19.html`; mobile copy:
  <https://hp6p2ourxwdr.postplan.dev>.

## Slayer Dagannoth Combat closure — 2026-07-18

- Added separate ordinary level-74 ranged and level-92 melee Dagannoth targets
  with exact period LP, Slayer XP, six-tick cadence, and distinct combat
  identities.
- Preserved Darkan's exact levels, defences, 80-LP maxima, 59-tick respawn,
  and guaranteed Bones for both forms.
- Combined every nonzero generic Darkan drop row into one exact 1,100-slot
  selector: 1,086 occupied slots and 14 explicit empty slots. The independent
  selector channels preserve 68/26/212/6 charm slots out of 1,212 and a 1/128
  medium clue.
- Kept Waterbirth, Chaos-Tunnel, King, quest, and Daemonheim contexts
  separate. The baseline Slayer family does not receive a false
  Lighthouse-only quest gate.
- Pinned distinct pre-cutoff ranged and melee sprites with provenance.
- Advanced Chaeldar to 24/34 while leaving its partial pool hidden and
  unrenormalized. Ten Combat-family blockers remain.
- No owner-facing design fork emerged. Durable evidence:
  `source-audits/slayer-dagannoth-combat-2026-07-18.md`.
- Focused Combat/Slayer/metadata coverage passes 359 tests, and the focused
  real offscreen Qt picker passes.
- Full non-Qt and real offscreen Qt discovery each pass all 1,677 tests; the
  real Qt run has zero skips or failures. Test quality has zero hard issues
  across 73 files and 1,677 methods. Reachability remains at 1,253 actions,
  1,865 reachable items, 288 orphan inputs, and 313 blocked actions.
- Results:
  `status-updates/slayer-dagannoth-results-2026-07-18.html`; mobile copy:
  <https://vzhh6w72sawc.postplan.dev>.

## Slayer Cave horror Combat closure — 2026-07-18

- Added the ordinary level-80 Cave horror with Slayer 58, 550 LP, 55 Slayer
  XP, Cabin Fever and lit-light-source access, four-tick magical melee, and a
  90-LP ordinary maximum.
- Extended protective equipment to source-declared alternative slots and
  combat classes: close combat accepts a Witchwood icon or any Slayer-helmet
  variant, while ranged/Magic safespot loadouts do not receive a false
  equipment warning.
- Preserved the cutoff 87-LP scream endpoint and one-random-stat-by-5 drain.
  Protect/Deflect Melee blocks scream damage but not the drain.
- Preserved exact Darkan stats, zero bonuses, 39-tick respawn, one 128-slot
  ordinary selector including its empty slot, the exact variable-allotment
  nested table, a losslessly enumerated 1,212-slot charm selector,
  Long/Curved bones, 1/512 Black mask (10), and 1/128 hard clue.
- Pinned the pre-cutoff Cave horror icon and its provenance.
- Advanced Chaeldar to 23/34 while leaving its partial pool hidden and
  unrenormalized. Eleven Combat-family blockers remain.
- No owner-facing design fork emerged. Durable evidence:
  `source-audits/slayer-cave-horror-combat-2026-07-18.md`.
- Focused Combat/Slayer/metadata coverage passes 409 tests, and the focused
  real offscreen Qt picker passes.
- Full non-Qt and real offscreen Qt discovery each pass all 1,675 tests; the
  real Qt run has zero skips or failures. Test quality has zero hard issues
  across 73 files and 1,675 methods. Documentation, compilation, provenance
  JSON, diff, readiness, reachability, and worktree-safety gates pass.
- Results:
  `status-updates/slayer-cave-horror-results-2026-07-18.html`; mobile copy:
  <https://pmzz0dpygpxu.postplan.dev>.

## Slayer Bronze dragon Combat closure — 2026-07-18

- Added the ordinary level-131 Bronze dragon with 1,220 LP, 125 Slayer XP,
  six-tick melee plus metal-dragon dragonfire, a 123-LP melee maximum, and a
  conservative 500-LP dragonfire maximum.
- Reused shared shield/antifire protection and labeled Darkan's exact adjacent
  1/2 melee-versus-fire selector as the no-position encounter abstraction.
- Preserved exact Darkan levels, defences, respawn, guaranteed Dragon bones
  and five Bronze bars, the 128-slot ordinary selector including its empty
  slot, the losslessly enumerated 1,212-slot charm selector, independent
  1/2,048 plate drops, and 1/128 hard plus 1/500 elite clues.
- Pinned the pre-cutoff Bronze dragon sprite and its provenance.
- Advanced Chaeldar to 22/34 while leaving its partial pool hidden and
  unrenormalized. Twelve Combat-family blockers remain.
- Excluded location, route, quest-only, post-cutoff, and Dungeoneering
  contexts. No owner-facing design fork emerged. Durable evidence:
  `source-audits/slayer-bronze-dragon-combat-2026-07-18.md`.
- Focused Combat/Slayer/metadata coverage passes 352 tests, and the focused
  real offscreen Qt picker passes.
- Full non-Qt and real offscreen Qt discovery each pass all 1,670 tests; the
  real Qt run has zero skips or failures. Test quality has zero hard issues
  across 73 files and 1,670 methods. Documentation, compilation, provenance
  JSON, diff, readiness, reachability, and worktree-safety gates pass.
- Results:
  `status-updates/slayer-bronze-dragon-results-2026-07-18.html`; mobile copy:
  <https://pbdlptcksw7s.postplan.dev>.

## Slayer Blue dragon family Combat closure — 2026-07-18

- Added the ordinary level-111 Blue dragon and level-48 Baby blue dragon as
  separate, source-backed target choices that both count for the family.
- Preserved the adult's 1,100 LP, 107.6 Slayer XP, six-tick melee, 110-LP
  melee maximum, dragonfire, exact emulator defences/respawn, guaranteed Blue
  dragonhide and Dragon bones, 128-slot ordinary table, 404-slot charm table,
  1/128 hard clue, and Summoning-99 1/2,000 egg gate.
- Kept the baby melee-only with 510 LP, 50 Slayer XP, no dragonfire, and
  guaranteed Baby dragon bones.
- Added generic player-skill gates to Combat drop tables and integration
  coverage proving a kill forwards player levels without consuming a gated
  table's RNG when locked.
- Pinned both pre-cutoff enemy sprites and their provenance.
- Advanced Chaeldar to 21/34 while leaving its partial pool hidden and
  unrenormalized. Thirteen Combat-family blockers remain.
- Excluded location, quest-route, Daemonheim, and Dungeoneering contexts. No
  owner-facing design fork emerged. Durable evidence:
  `source-audits/slayer-blue-dragon-family-combat-2026-07-18.md`.
- Focused Combat/Slayer/metadata coverage passes 350 tests, and the focused
  real offscreen Qt picker passes. Full non-Qt and real offscreen Qt discovery
  each pass all 1,668 tests; the real Qt run has zero skips or failures.
- Test quality has zero hard issues across 73 files and 1,668 methods.
  Documentation, compilation, provenance JSON, diff, readiness, reachability,
  and worktree-safety gates pass.
- Results:
  `status-updates/slayer-blue-dragon-family-results-2026-07-18.html`; mobile
  copy: <https://ez10f8mr9lib.postplan.dev>.

## Slayer Fire giant Combat closure — 2026-07-18

- Added the ordinary level-86 Fire giant with 1,110 LP, 111 Slayer XP,
  five-tick melee, a 116-LP maximum, period poison behavior, guaranteed Big
  bones, exact Darkan stats, and a 59-tick respawn.
- Preserved one exact 128-slot ordinary selector, including nested herb, gem,
  and standard-rare tables; losslessly enumerated Darkan's inclusive charm
  behavior into 404 slots; and kept Long/Curved bones independent at 1/400 and
  1/5,000.
- Pinned the pre-cutoff `Fire giant.png` revision and its provenance.
- Advanced Chaeldar to 20/34 while leaving its partial pool hidden and
  unrenormalized. Fourteen Combat-family blockers remain.
- Excluded location-only quest/Wilderness/Smoke-Dungeon contexts and all
  Daemonheim/Dungeoneering variants from the ordinary representative.
- No owner-facing design fork emerged. Durable evidence:
  `source-audits/slayer-fire-giant-combat-2026-07-18.md`.
- Focused Combat/Slayer/metadata coverage passes 347 tests, and the focused
  real offscreen Qt picker passes. Full non-Qt and real offscreen Qt discovery
  each pass all 1,665 tests; the real Qt run has zero skips or failures.
- Test quality has zero hard issues across 73 files and 1,665 methods.
  Compilation, diff, readiness, reachability, and worktree-safety audits pass
  or match their declared baseline.
- Results: `status-updates/slayer-fire-giant-results-2026-07-18.html`; mobile
  copy: <https://6v3lhweptj0p.postplan.dev>.

## Slayer Chaeldar hidden registry — 2026-07-18

- Encoded all 34 source-reconciled master rows with their exact current count
  ranges and provisional 388-point hidden denominator.
- Added seventeen stable family identities plus source-declared Slayer,
  Combat-skill, quest, protection, finisher, restricted-weapon,
  assignment-only, disease, neem-oil, and crystal-chime completeness gates.
- Registered Chaeldar at Combat 70 behind Lost City while keeping
  `runtime_enabled=False`; live master selection cannot see or renormalize the
  partial pool.
- Derived 25/34 readiness after the Fire giant, Blue dragon, Bronze dragon,
  Cave horror, Dagannoth, and Elf-warrior closures. Nine absent target identities each report one
  deterministic `combat_target` blocker, while Gargoyles and Mutated
  zygomites reuse their already-live finisher mechanics.
- Preserved the source-blocked Rum Deal stage boundary for Fever spiders
  instead of misrepresenting it as quest-completion access.
- Added focused pool, range, gate, hidden-runtime, blocker, and catalog
  integrity regressions. Slayer/Combat/metadata coverage passes 89 tests.
- Full non-Qt discovery passes all 1,663 tests with 215 declared environment
  skips; full real offscreen Qt discovery passes all 1,663 with no skips,
  failures, or errors. Documentation, test quality, compilation, diff,
  readiness, reachability, and worktree-safety checks pass.
- No owner-facing design fork emerged. Durable evidence:
  `source-audits/slayer-chaeldar-registry-2026-07-18.md`. Results:
  `status-updates/slayer-chaeldar-registry-results-2026-07-18.html`; mobile
  copy: <https://dkvu5eb3h0w8.postplan.dev>.

## Slayer Turoth Combat closure — 2026-07-18

- Added the ordinary level-83 Turoth with Slayer 55, 760 LP, 76 Slayer XP,
  passive six-tick melee, a 97-LP maximum, poison immunity, and Darkan's exact
  stats, bonuses, and 59-tick respawn.
- Enforced the period damage restriction before a review can be spent:
  Leaf-bladed spear or sword for melee, Broad arrows or Broad-tipped bolts for
  Ranged, or Magic Dart with the canonical `Slayer's staff`.
- Added source-backed Broad-arrow bow compatibility, Broad-tipped-bolt support,
  ammunition-level locks, the Rune crossbow's exact Ranged-61 item-config gate,
  and Magic-staff recognition for `Slayer's staff`.
- Preserved one exact 100,000-slot Darkan ordinary selector, the losslessly
  enumerated 1,212-slot Darkan charm selector, and an independent 1/128 hard
  clue.
- Generated the light Mystic bottom and Leaf-bladed sword, corrected the
  Leaf-bladed spear's Attack-50/Slayer-55 requirements, and pinned cutoff enemy
  and rare-drop art with provenance.
- Advanced Vannaka to 34/35 while leaving the partial pool hidden and
  unrenormalized. Mogres remain the sole quest-owned blocker.
- No owner-facing design fork emerged. Durable evidence:
  `source-audits/slayer-turoth-combat-2026-07-18.md`. Results:
  `status-updates/slayer-turoth-results-2026-07-18.html`.
- Published the mobile closure report at
  <https://gimdeversiok.postplan.dev>.
- Focused coverage passes 622 methods with 211 expected non-Qt skips. Full
  non-Qt discovery passes all 1,661 methods with 215 expected Qt-environment
  skips; full real offscreen Qt executes all 1,661 with zero skips, failures,
  or errors. Documentation, test quality, generated-data determinism,
  compilation, JSON, diff, readiness, reachability, and worktree-safety gates
  pass.

## Slayer Molanisk Combat closure — 2026-07-18

- Added the ordinary level-51 Molanisk with Slayer 39, 520 LP, 52 Slayer XP,
  six-tick passive melee, a 53-LP maximum, exact Darkan stats/bonuses, and a
  59-tick respawn.
- Reused the completed Death to the Dorgeshuun quest, live 150-coin Slayer bell,
  and existing Firemaking light-source graph. One bell is required but not
  consumed; any reachable lit source may be carried or equipped.
- Flattened the wall interaction into one visible line: each Combat encounter
  starts by ringing the bell to lure one Molanisk, with no redundant target,
  wall-clock state, or pseudo-item.
- Preserved guaranteed Bones, one exact 100,000-slot cumulative Darkan
  selector with 211 empty slots, and an independent 1/128 easy clue. Darkan
  has no Molanisk charm row, so none was invented.
- Added cache-backed Swamp weed and Mole claw identities with period art and
  pinned the cutoff Molanisk sprite.
- Advanced Vannaka to 33/35 while leaving the partial pool hidden and
  unrenormalized. Mogres and Turoth remain.
- No owner-facing design fork emerged. Durable evidence:
  `source-audits/slayer-molanisk-combat-2026-07-18.md`. Results:
  `status-updates/slayer-molanisk-results-2026-07-18.html`.
- Published the mobile closure report at
  <https://2a1t6lht0q8n.postplan.dev>.
- Focused coverage passes 602 methods with 211 expected non-Qt skips; the
  focused real offscreen Qt picker passes. Full non-Qt and real offscreen Qt
  discovery each pass all 1,657 methods, with no real-Qt skips. Documentation
  passes across 326 Markdown and 342 HTML files; test quality reports zero hard
  issues across 73 files. Compilation, JSON, diff, worktree-safety, readiness,
  and reachability audits were rerun.

## Slayer Brine rat Combat closure — 2026-07-18

- Added the ordinary level-70 Brine rat with Slayer 47, 500 LP, 50 Slayer XP,
  six-tick passive melee, a 93-LP maximum, zero bonuses, and a 59-tick respawn.
- Added a non-consumed real-Spade cavern gate. The target records the sourced
  Olaf's Quest stage-40 permission while conservatively consuming stable quest
  completion until the Darkan thread exports that semantic state.
- Preserved guaranteed Bones and Raw rat meat, one exact 512-slot cumulative
  ordinary selector including the 1/512 Brine sabre, the exact 606-slot Darkan
  charm selector, and an independent 1/128 medium clue.
- Registered Brine sabre item 11037 and generated its exact Attack-40,
  one-handed, four-tick equipment block with +7 stab, +47 slash, -2 crush, and
  +46 melee strength.
- Pinned cutoff Brine-rat and Brine-sabre assets. The underwater-only Liquefy
  special remains an explicit future Combat capability rather than a fake
  ordinary effect.
- Advanced Vannaka to 32/35 while leaving the partial pool hidden and
  unrenormalized. Mogres, Molanisks, and Turoth remain.
- Kept quest ownership clean in
  `codex-briefs/darkan-quest-handoff-brine-rat-2026-07-18.md`.
- No owner-facing design fork emerged. Durable evidence:
  `source-audits/slayer-brine-rat-combat-2026-07-18.md`. Results:
  `status-updates/slayer-brine-rat-results-2026-07-18.html`.
- Focused verification passes 614 methods. Full non-Qt discovery passes all
  1,653 methods with 215 expected Qt-environment skips; full real offscreen Qt
  discovery executes all 1,653 with zero skips, failures, or errors.
- Documentation, test-quality, generated-data, diff, readiness, reachability,
  provenance, and worktree-safety gates pass.
- Published the mobile closure report at
  <https://cf55icb0rmwe.postplan.dev>.

## Slayer Sea snakes Combat closure — 2026-07-18

- Added ordinary Sea Snake Hatchling and Sea Snake Young Combat targets with
  their cutoff levels, LP, Slayer gates/XP, melee maxima, poison consequences,
  and Royal Trouble route.
- Reconciled Darkan's generated hatchling stats, exact young-snake stats, zero
  bonuses, 59-tick respawns, complete ordinary tables, tertiary bone table,
  and independent 1/128 medium-clue rows.
- Preserved Darkan's exact cumulative 13,000-slot hatchling ordinary selector:
  11,700 Casket slots, 26 one-slot rares, and 1,274 empty slots. One kill
  cannot emit both a Casket and a rare row.
- Represented the young snake's post-quest 68-LP poison as the visible nearest
  70-LP value required by the integer old-scale poison channel. The six-tick
  cadence is labeled corroborated rather than period exact.
- Reused canonical `Broad arrows` item 4160 rather than reviving its retired
  singular storage alias, registered Edible seaweed item 403 with canonical
  inventory shape and a real item asset, and pinned both pre-cutoff enemy
  sprites.
- Kept quest ownership clean: Combat uses conservative Royal Trouble
  completion until Darkan exposes a stable mid-quest dungeon-permission state.
  The follow-up is recorded in
  `codex-briefs/darkan-quest-handoff-sea-snakes-2026-07-18.md`.
- Advanced Vannaka to 31/35 while leaving the partial pool hidden and
  unrenormalized. Brine rats, Mogres, Molanisks, and Turoth remain.
- Focused verification passes 682 tests. Full non-Qt discovery passes 1,649
  tests with 215 expected Qt-environment skips; full real offscreen Qt
  discovery executes all 1,649 with zero skips, failures, or errors.
- Documentation, test-quality, generated-data, compilation, diff, readiness,
  reachability-ledger, provenance, and worktree-safety gates pass.
- No owner-facing design fork emerged. Durable evidence:
  `source-audits/slayer-sea-snakes-combat-2026-07-18.md`. Results:
  `status-updates/slayer-sea-snakes-results-2026-07-18.html`; mobile copy:
  <https://i3lix9qo57d8.postplan.dev>.

## Slayer Killerwatt Combat closure — 2026-07-18

- Added the ordinary level-71 Killerwatt with Slayer 37, existing
  Ernest-the-Chicken access, 510 LP, 51 Slayer XP, eight-tick attacks, and a
  64-LP maximum.
- Preserved its distance-sensitive attack contract: melee play receives
  magical melee against Magic defence and Protect from Melee, while Ranged and
  Magic play receive Ranged attacks and Protect from Missiles.
- Made the same resolved channel drive Casual max-safety prayer selection.
- Preserved the non-blocking boots consequence. Insulated boots suppress the
  hazard; without them, one labeled 0–140 LP thundercloud roll is added to each
  incoming attack. This is a bounded review-native cadence abstraction.
- Restored the source's Slayer-37 Insulated-boots wear requirement in generated
  equipment data while retaining the existing 200-coin Slayer-master stock.
- Added guaranteed Impious ashes, Darkan's exact 100,000-slot ordinary
  selector, and the independently derived 303-slot charm selector.
- Made Combat enemy asset fetching cutoff-aware and fetched the 2011 Killerwatt
  sprite rather than the modern replacement.
- Advanced Vannaka to 30/35 while leaving the incomplete master hidden and
  unrenormalized. No quest/catalog work or owner-facing design fork was added.
- Focused verification passes 747 tests. Full non-Qt discovery passes 1,645
  tests with 215 expected Qt-environment skips; full real offscreen Qt
  discovery executes all 1,645 with zero skips, failures, or errors.
- Documentation, test-quality, generated-data, compilation, JSON, diff,
  readiness, reachability-ledger, and worktree-safety checks pass.
- Durable evidence:
  `source-audits/slayer-killerwatt-combat-2026-07-18.md`. Results:
  `status-updates/slayer-killerwatt-results-2026-07-18.html`; mobile copy:
  <https://4wz22cbm89jb.postplan.dev>.

## Slayer Harpie Bug Swarm Combat closure — 2026-07-18

- Added the ordinary level-46 Harpie Bug Swarm with Slayer 33, 250 LP, 25
  Slayer XP, six-tick melee, and a 60-LP maximum hit.
- Preserved the source's literal continuous damage gate: lit bug lantern item
  7053 must occupy the shield slot when every Combat review begins, including
  an already-active encounter.
- Added Firemaking 33 lighting and ungated extinguishing as zero-XP Utility
  item swaps, generated the lit lantern as wearable zero-bonus shield
  equipment, and preserved the existing 130-coin Slayer-master acquisition.
- Excluded the lit bug lantern from functional light-source gates because the
  cutoff item page explicitly says it cannot illuminate caves.
- Encoded Darkan's exact 100,000-slot ordinary selector and independently
  derived 202-slot charm selector. The cutoff wiki's different drop contents
  are recorded as a source conflict.
- Advanced Vannaka to 29/35 while leaving the incomplete master hidden and
  unrenormalized. Six missing Combat representatives remain. No owner-facing
  design fork emerged.
- Durable evidence:
  `source-audits/slayer-harpie-bug-swarm-combat-2026-07-18.md`. Results:
  `status-updates/slayer-harpie-bug-swarm-results-2026-07-18.html`
  (<https://lwn2getn9lo2.postplan.dev>).
- Verification closed with 747 focused tests, 1,640 full non-Qt tests
  (215 declared Qt-only skips), and all 1,640 tests in the real offscreen Qt
  environment with zero skips, failures, or errors. Documentation,
  test-quality, generated-data, reachability, and worktree audits were rerun.

## Slayer Green dragon Combat closure — 2026-07-18

- Added the ordinary Wilderness level-79 Green dragon with 750 LP, 75 Slayer
  XP, six-tick attacks, an 85-LP melee maximum, guaranteed Dragon bones and
  Green dragonhide, and the pinned imported drop selectors.
- Added reusable dragonfire tiers: 500 LP unprotected, 50 LP with one layer,
  and zero with complete protection. The hidden 1/4 breath frequency is
  explicitly `provisional/darkan` because game-main conflicts at 1/10.
- Registered complete Antifire and Super antifire vial/flask families,
  preserving every remaining dose and exact six-minute/600-game-tick duration.
  Combat auto-loads one bottle and can refresh it inside a long review without
  using wall-clock time.
- Generated Anti-dragon shield item 1540 as wearable shield equipment with its
  exact cache bonuses and reused the existing Dragon Slayer acquisition path.
- Combined dragonfire state and Wilderness loss consequences in one target
  preview and confirmation. Exact charm rates remain `source_blocked`.
- Advanced Vannaka to 28/35 while leaving the incomplete master hidden and
  unrenormalized. Seven missing Combat representatives remain. No owner-facing
  design fork emerged.
- Durable evidence:
  `source-audits/slayer-green-dragon-combat-2026-07-18.md`. Results:
  `status-updates/slayer-green-dragon-results-2026-07-18.html`
  (<https://blwhzxpwaa52.postplan.dev>).

## Slayer Earth warrior Wilderness-risk closure — 2026-07-18

- Applied the owner-approved 1%/250-LP bounded PKer abstraction after each
  successful Earth-warrior Combat review and reset the encounter on a trigger.
- Added separate Wilderness death semantics: three highest-value equipped items
  kept, Protect Item adds one, other equipped items permanently lost, ordinary
  inventory retained, and no new grave.
- Added a process-local risk fingerprint so Anki restart or a material
  kept/lost-set change requires fresh confirmation before any review can
  advance.
- Exposed chance, maximum hit, kept/lost counts, no-grave behavior, and the
  distinct Wilderness-risk state in the Combat target surface.
- Safe-skill reviews now discard active Wilderness encounter progress.
- Advanced Vannaka to 27/35 while keeping the incomplete pool hidden and
  unrenormalized. Eight missing Combat representatives remain. No owner-facing
  design fork emerged.
- Durable evidence:
  `source-audits/slayer-earth-warrior-wilderness-risk-2026-07-18.md`. Results:
  `status-updates/slayer-earth-warrior-wilderness-results-2026-07-18.html`
  (<https://73amt4x2o23l.postplan.dev>).

## Slayer Dust devil Combat closure — 2026-07-18

- Added the ordinary level-93 Dust devil with Slayer 65, 1,050 LP, 105 Slayer
  XP, six-tick melee, and a 90-LP maximum hit.
- Preserved the cutoff's literal damage gate: Face mask, Masked earmuffs, or
  an accepted Slayer helmet must remain equipped throughout the fight.
- Used the cutoff-attested Chaos Tunnels route rather than inventing a Desert
  Treasure quest dependency or duplicating quest work.
- Encoded Darkan's exact 32,768-slot ordinary selector, exact nested herb/gem
  tables, and independent 606-way charm selector.
- Generated Dragon chainbody item 3140 as Defence-60 body equipment and fixed
  the generator to prefer an exact drop-row source ID over ambiguous name
  fallback.
- Advanced Vannaka to 26/35 while keeping the incomplete master hidden and
  unrenormalized. Eight Combat targets plus Earth warrior's Wilderness risk
  remain. No owner-facing design fork emerged.
- Durable evidence:
  `source-audits/slayer-dust-devil-combat-2026-07-18.md`. Results:
  `status-updates/slayer-dust-devil-results-2026-07-18.html`
  (<https://dylce5d5v14s.postplan.dev>).

## Darkan ordinary-drop selector correction — 2026-07-18

- Reproduced Darkan's executable `DropList` behavior: all nonzero sibling rows
  in one NPC drop JSON share one cumulative random selector; rate-zero always
  rows and the separately invoked charm path remain distinct.
- Corrected eleven live targets: Warriors' Guild Cyclops, Cyclossus, Young
  grotworm, Desert lizard, Rockslug, Gargoyle, Mutated zygomite,
  Jungle horror, Shadow warrior, Infernal Mage, and Basilisk.
- Preserved every individual marginal probability while removing impossible
  sibling multi-drop combinations. Cyclossus's period-common Dragon defender
  and Mutated zygomite's Fungicide remain separate labeled abstractions rather
  than being passed off as Darkan rows.
- Added denominator, boundary-reachability, mutual-exclusion, charm-separation,
  generated-equipment, and real offscreen Qt regression coverage.
- Corrected the affected source audits, live Memory Bank summaries, and
  published status artifacts. No owner design input was required. Durable
  evidence is
  `source-audits/slayer-darkan-drop-selector-correction-2026-07-18.md`;
  results are in
  `status-updates/slayer-darkan-drop-selector-correction-results-2026-07-18.html`
  (<https://pk45017w1z2j.postplan.dev>).

## Slayer Shadow warrior Combat closure — 2026-07-18

- Added the ordinary level-48 Shadow warrior as a Legends'-Quest-gated Combat
  target with 670 LP, 67 Slayer XP, six-tick melee, and maximum hit 65.
- Preserved Darkan's executable ordinary-drop shape as one 128-way selector
  with 106 occupied and 22 empty slots.
- Derived the exact executable Darkan charm distribution from its inclusive
  threshold-and-uniform-selection algorithm rather than treating the four
  source numbers as independent percentages.
- Reused the existing Legends' Quest completion state without adding or
  duplicating quest stages.
- Advanced Vannaka from 23/35 to 24/35 without exposing or renormalizing the
  incomplete master. Ten missing targets and Earth warrior's Wilderness
  context remain.
- Focused checks and the real offscreen Qt picker pass. Exact period defensive
  bonuses remain `source_blocked`; no owner design input was required. Durable
  evidence is
  `source-audits/slayer-shadow-warrior-combat-2026-07-18.md`. Results:
  `status-updates/slayer-shadow-warrior-results-2026-07-18.html`
  (<https://4c0ztjs0b4cs.postplan.dev>).

## Slayer Jungle horror Combat closure — 2026-07-18

- Added the ordinary level-70 Jungle horror as a Cabin-Fever-gated Combat
  target with 450 LP, 45 Slayer XP, six-tick melee, and maximum hit 84.
- Preserved Darkan's executable drop shape: guaranteed Bones plus one exact
  100,000-slot selector containing all 32 nonzero JSON rows.
- Reused the existing Cabin Fever completion state without adding or
  duplicating quest stages.
- Advanced Vannaka from 22/35 to 23/35 without exposing or renormalizing the
  incomplete master. Eleven missing targets and Earth warrior's Wilderness
  context remain.
- Focused checks, the real offscreen Qt picker, and a bounded read-only
  Sol-high workflow review pass. Exact period charm distribution remains
  `source_blocked`; no owner design input was required. Durable evidence is
  `source-audits/slayer-jungle-horror-combat-2026-07-18.md`. Results:
  `status-updates/slayer-jungle-horror-results-2026-07-18.html`
  (<https://7s9qx4vwmhao.postplan.dev>).

## Slayer Otherworldly being Combat closure — 2026-07-18

- Added the ordinary level-64 Otherworldly being as a Lost-City-gated Combat
  target with 660 LP, 66 Slayer XP, six-tick melee, and maximum hit 70.
- Encoded Darkan's exact 128-slot ordinary table, including nested minor-herb
  and gem rolls plus 18 explicit empty slots.
- Reused the existing Lost City completion state without adding or duplicating
  quest stages.
- Advanced Vannaka from 21/35 to 22/35 without exposing or renormalizing the
  incomplete master. Twelve missing targets and Earth warrior's Wilderness
  context remain.
- Focused checks and the real offscreen Qt picker pass. Durable evidence is
  `source-audits/slayer-otherworldly-being-combat-2026-07-18.md`; no owner
  design input was required. Results:
  `status-updates/slayer-otherworldly-being-results-2026-07-18.html`
  (<https://q57byaii1o36.postplan.dev>).

## Slayer Crocodile Combat closure — 2026-07-18

- Added the ordinary level-63 River Elid Crocodile as a Slayer-10 Combat target
  with 630 LP, 62 Slayer XP, five-tick melee, and maximum hit 67.
- Preserved the exact level-63 drop boundary: guaranteed Bones and no other
  table. Darkan's merged level-63/89 Bones-plus-Big-bones row is rejected.
- Reused the existing filled-Waterskin desert hazard with dose preservation,
  review-driven consumption, pack capacity, bank runs, and atomic undo.
- Advanced Vannaka from 20/35 to 21/35 without exposing or renormalizing the
  incomplete master. Thirteen missing targets and Earth warrior's Wilderness
  context remain.
- Focused checks and the real offscreen Qt picker pass. Durable evidence is
  `source-audits/slayer-crocodile-combat-2026-07-18.md`; no owner design input
  was required. Results:
  `status-updates/slayer-crocodile-results-2026-07-18.html`
  (<https://kjy22255e4a6.postplan.dev>).

## Slayer Basilisk Combat closure — 2026-07-18

- Added the ordinary level-61 Basilisk as a Slayer-40 Combat target with 750
  LP, 75 Slayer XP, six-tick melee, maximum hit 59, and guaranteed Bones.
- Reused the equipped Mirror-shield contract while preserving Basilisk's
  distinct source behavior: Protect from Melee blocks the unshielded damage
  but not its random five-level stat drain.
- Encoded the exact 64,000-slot Darkan selector containing the 128-based
  ordinary rows, 1/512 light-Mystic row, and 1/2,000 Basilisk-head row. Charm
  distribution remains `source_blocked`.
- Registered Mystic hat (light) as generated Defence-20/Magic-20 equipment and
  corrected Basilisk head to its non-stackable, untradeable item-7977 identity.
- Advanced Vannaka from 19/35 to 20/35 without exposing or renormalizing the
  incomplete master. Fourteen missing targets and Earth warrior's Wilderness
  context remain.
- Focused checks and the real offscreen Qt picker pass. Durable evidence is
  `source-audits/slayer-basilisk-combat-2026-07-18.md`; no owner design input
  was required. Results:
  `status-updates/slayer-basilisk-results-2026-07-18.html`
  (<https://12bv7z5x53a2.postplan.dev>).

## Slayer Infernal Mage Combat closure — 2026-07-18

- Added the ordinary level-66 Infernal Mage as a Slayer-45 Combat target with
  600 LP, 60 Slayer XP, six-tick Magic attacks, maximum hit 89, and guaranteed
  Bones.
- Preserved Darkan's executable source shape as one exact 64,000-slot
  selector containing the 128-based ordinary rows, both 1/512 dark-mystic
  rows, and the 1/1,000 Lava battlestaff row.
- Registered Lava battlestaff, dark Mystic hat, and dark Mystic boots as
  generated equipment with exact period requirements, bonuses, and weapon
  speed.
- Advanced Vannaka from 18/35 to 19/35 without exposing or renormalizing the
  incomplete master. Fifteen missing targets and Earth warrior's Wilderness
  context remain.
- Charm distribution remains explicitly `source_blocked`. Focused checks, the
  real offscreen Qt picker, and all 1,604 pure tests pass. Durable evidence is
  `source-audits/slayer-infernal-mage-combat-2026-07-18.md`; no owner design
  input was required. Results:
  `status-updates/slayer-infernal-mage-results-2026-07-18.html`
  (<https://6zhziqqts1l7.postplan.dev>).

## Slayer Bloodveld Combat closure — 2026-07-18

- Added the ordinary level-76 Bloodveld as a Slayer-50 Combat target with 1,200
  LP, 120 Slayer XP, six-tick magic-based melee, maximum hit 59, and guaranteed
  Bones.
- Encoded Darkan's 123 named ordinary slots plus five explicit empty slots at
  the exact denominator 128; no absent rare-table or herb rows were invented.
- Registered Black boots item 4125 as generated Defence-10 feet equipment with
  exact 2011Scape bonuses and an item asset.
- Advanced Vannaka from 17/35 to 18/35 without exposing or renormalizing the
  incomplete master. Sixteen missing targets and Earth warrior's Wilderness
  context remain.
- Focused checks, the real offscreen Qt picker, and all 1,601 pure tests pass.
  Durable evidence is
  `source-audits/slayer-bloodveld-combat-2026-07-18.md`; no owner design input
  was required. Results:
  `status-updates/slayer-bloodveld-results-2026-07-18.html`
  (<https://k9ynbzcx5a8u.postplan.dev>).

## Slayer Jelly Combat closure — 2026-07-18

- Added the ordinary level-78 Jelly as a Slayer-52 Combat target with 750 LP,
  75 Slayer XP, six-tick magic-based melee, and the reconciled 60-LP maximum
  hit.
- Encoded Darkan's exact mutually exclusive 128-slot ordinary drop table and
  deliberately excluded Soul Wars' separate fragment/PvP variant.
- Registered Mithril boots item 4127 as generated Defence-20 feet equipment
  with exact 2011Scape bonuses, item identity, acquisition, and asset surface.
- Advanced the generated Vannaka ledger from 16/35 to 17/35 without exposing or
  renormalizing the incomplete master. Seventeen missing targets and Earth
  warrior's Wilderness context remain.
- Focused checks and the current 1,599-test pure suite pass; the production
  state also passed the 1,601-test real offscreen Qt suite before two redundant
  pure test methods were consolidated. Durable evidence is
  `source-audits/slayer-jelly-combat-2026-07-18.md`; no owner design input was
  required. Results: `status-updates/slayer-jelly-results-2026-07-18.html`
  (<https://qvrpp85jnouq.postplan.dev>).

## Slayer Vannaka pool and Ogre Combat closure — 2026-07-18

- Encoded all 35 cutoff Vannaka families, their reconciled weights/count
  ranges, and the provisional 460-point denominator without exposing a partial
  master or renormalizing around missing families.
- Extended the executable readiness audit to report Vannaka at 16/35 and name
  all 19 remaining target/context blockers from live registry state.
- Added the ordinary level-53 Ogre with 600 LP, 60 Slayer XP, guaranteed Big
  bones, Darkan's exact 1,000-slot common-seed subtable behind its `19/128`
  roll, independent long/curved-bone tertiary rolls, and a provenance-pinned
  pre-cutoff sprite.
- Kept quest ownership clean: Mogres still depend on the Darkan-owned
  `skippy_and_the_mogres` completion ID, and this slice adds no quest/catalog
  substitute.
- Focused checks, all 1,597 pure tests, and all 1,597 real offscreen Qt tests
  pass. Durable evidence is
  `source-audits/slayer-vannaka-ogre-combat-2026-07-18.md`; no owner design
  input was required. Results:
  `status-updates/slayer-vannaka-ogre-results-2026-07-18.html`
  (<https://o849m34h9y3r.postplan.dev>).

## Warriors' Guild and Cyclopes closure — 2026-07-18

- Implemented all five source activities and token balances, Casual/Advanced
  automation, single/multi Cyclops-room entry and exact residual drain,
  progressive defender showing/drops, multi-token benefits, and explicit room
  exit/depletion/death cleanup.
- Added source-backed Cyclops and Cyclossus Combat targets. Cyclossus spawns
  only after Rune has been shown, interrupts the ordinary target, requires a
  worn Rune or Dragon defender, and returns to Cyclops after defeat.
- Registered all eight defenders and the cosmetic Cyclopean helmet as equipment
  with period bonuses/requirements, source-shaped drops, provenance-tracked
  activity/enemy/item assets, and a compact real Qt control surface.
- Advanced live Mazchna/Achtryn readiness from 25/27 to 26/27. Mogres is now
  the sole blocker and remains correctly assigned to the Darkan quest pass for
  `skippy_and_the_mogres`; the incomplete master stays hidden.
- Exact missing rates remain explicit abstractions rather than invented parity
  claims. The complete evidence boundary is
  `source-audits/warriors-guild-live-implementation-2026-07-18.md`; no owner
  design input was required.
- Moved defender and Cyclopean-helmet registration into
  `tools/generate_equipment_data.py` after full discovery caught a brittle
  manual-tail boundary. Focused pure and Qt checks, all 1,592 core tests, all
  1,592 real offscreen Qt tests, documentation, test-quality, readiness,
  provenance, and worktree checks pass. Results:
  `status-updates/warriors-guild-results-2026-07-18.html`
  (<https://vsx8a7pxsimj.postplan.dev>).

## Slayer Kalphite Soldier Combat closure — 2026-07-18

- Added the ordinary level-85 Kalphite Soldier as an executable Combat target
  with 900 LP, 90 Slayer XP, a six-tick melee attack, an approximate 80-LP
  maximum hit, and a pre-cutoff target image.
- Encoded Darkan's exact 128-slot mutually exclusive drop table using the
  existing item registry plus shared gem and minor-herb tables; no name-only
  economy item was introduced.
- Reused the shared poison runtime and made the unavoidable magnitude
  abstraction explicit: the period page gives 48 LP, while the
  game-main-shaped integer unit can represent only ten-LP increments, so the
  target uses the nearest value of 50 LP rather than 480 or 40.
- Advanced executable Mazchna/Achtryn readiness from 22/27 to 23/27 without
  exposing the partial master. Cyclopes, Mogres, Vampyres, and Wall beasts are
  the four exact remaining Combat-target blockers.
- Focused pure and real offscreen Qt regressions pass. Full core discovery
  passes all 1,566 methods with 213 declared environment skips; full real
  offscreen Qt discovery passes all 1,566 methods without failures or skips.
  Test quality reports zero hard issues, and documentation, compilation, diff,
  readiness, and worktree checks pass. The expected reachability debt ledger
  remains 1,231 actions, 1,811 reachable items, 285 orphan inputs, and 311
  blocked actions.
- Durable evidence is
  `source-audits/slayer-kalphite-soldier-combat-2026-07-18.md`; the visual
  report is
  `status-updates/slayer-kalphite-soldier-combat-results-2026-07-18.html`
  (<https://trn4s92bn2a4.postplan.dev>). No owner design decision was required.

## Slayer Pyrefiend Combat closure — 2026-07-18

- Added the ordinary level-43 Pyrefiend as a Slayer-30 Combat target with 450
  LP, 45 Slayer XP, a 44-LP maximum hit, guaranteed Impious ashes, the exact
  128-slot ordinary drop table, and a pre-cutoff target image.
- Implemented the source's distinct magic-based-melee contract: enemy Attack
  plus stab bonus rolls against player Magic defence, while Protect from Melee
  remains the relevant protection prayer. Casual max-safety and the Combat
  picker expose the same semantics.
- Registered Steel boots item 4123 as real Defence-5 feet equipment with exact
  bonuses, source identity, asset provenance, reachability, and generated-data
  coverage.
- Advanced the executable Mazchna/Achtryn readiness ledger from 21/27 to 22/27
  without exposing a partial master. Cyclopes, Kalphites, Mogres, Vampyres, and
  Wall beasts remain the five exact Combat-target blockers.
- Focused backend and real picker regressions pass. Full core discovery passes
  all 1,565 methods with 213 declared environment skips; full real offscreen Qt
  discovery passes all 1,565 methods without failures or skips.
- Durable evidence:
  `source-audits/slayer-pyrefiend-combat-2026-07-18.md`; the visual report is
  `status-updates/slayer-pyrefiend-combat-results-2026-07-18.html`
  (<https://0ga1wxb9wpb8.postplan.dev>). No owner design decision was required.

## Slayer Mazchna/Achtryn hidden-pool readiness — 2026-07-18

- Split stable Slayer family identities from master-specific assignment rows,
  preserving Turael's live values while encoding all 27 Mazchna/Achtryn rows
  and the exact provisional 325-point denominator.
- Kept Mazchna/Achtryn runtime-disabled; Achtryn's While Guthix Sleeps interval
  remains source metadata rather than an exposed partial role.
- Added an executable readiness audit over live Combat targets, Slayer XP, and
  required poison/protection/finisher mechanics. It certifies Turael/Spria at
  23/23 and reports Mazchna/Achtryn at 22/27.
- Closed the stale Hobgoblin blocker with the pinned pre-EOC 29/49 Slayer XP.
  The only remaining Mazchna target blockers are Cyclopes, Kalphites, Mogres,
  Vampyres, and Wall beasts.
- Added pure regression coverage for master-specific rows, hidden-master
  behavior, exact blocker derivation, and catalog-integrity failures. No owner
  design question emerged.
- Full core and real offscreen Qt discovery each pass all 1,560 methods.
  Focused Slayer/Combat/runtime/integration coverage, test quality,
  documentation, compilation, JSON, diff, reachability, and worktree-safety
  checks pass.
- Published
  `status-updates/slayer-mazchna-readiness-results-2026-07-18.html`
  (<https://ir3cpm2ptnfp.postplan.dev>).

## Slayer Mutated zygomite Combat closure — 2026-07-18

- Added both ordinary Mutated zygomite variants with period Slayer/quest gates,
  LP, Slayer XP, maximum hit, sprites, and the one-line reveal interaction.
- Implemented charge-preserving Fungicide spray states `10 → 0`, canister
  reloads, manual and quick finishing parity, and capacity-safe Combat refills.
- Registered cache items `7421–7432` with non-stackable/non-tradeable inventory
  shape and shared dose-state icon fallback.
- Reconciled the Darkan selector probabilities only where period
  identity/quantity evidence allows it; unresolved rows and the 140-LP spore
  frequency remain explicit `source_blocked` omissions.
- Focused pure, runtime, registry, metadata, provenance, and reachability
  coverage passes 391 methods. Full core discovery passes all 1,557 methods
  with 213 declared environment skips; full real offscreen Qt discovery passes
  all 1,557 methods without skips or failures.
- Test-quality, documentation, JSON, reachability-route, diff, and worktree
  safety checks pass. The visual report is
  `status-updates/slayer-mutated-zygomite-results-2026-07-18.html`; mobile
  copy: <https://ujk2cg24j80q.postplan.dev>.

## Public derivative release disposition — 2026-07-17

- Settled the former personal-fork-versus-public-release question in favor of
  preparing a distinct public derivative release.
- Measured the lineage at a fixed Git snapshot: about 2.2% of current
  production code is surviving unchanged original code under a conservative
  comparison, while about 70.0% of Wilson's original production code still
  survives. This supports “radically expanded derivative fork,” not minor
  update or independent rewrite.
- Locked prominent Wilson Yeh original-creator credit, Arman Tarkhanian
  independent-maintainer identity, a new AnkiWeb listing, explicit compatible
  licensing, complete source links, and a corrected in-product review link.
- Kept publication gated on written license clarification or acknowledgement,
  public-repository synchronization, asset redistribution provenance, packaging,
  migration, real-profile, performance/accessibility, export/recovery, and
  post-upload verification.
- Durable record:
  `public-release-lineage-and-license-2026-07-17.md`.

## Shared catalog search seam — 2026-07-17

- Added one reusable `CatalogFilterBar` for Shop, Quests, Combat, and future
  large catalog surfaces. Pages own their metadata and predicates; the shared
  widget owns dark-mode-safe search chrome, clear/Escape behavior, optional
  filter placement, and count summaries.
- Added live Combat text search over exact target ids, labels, tooltips, and
  groups. Filtering preserves the persisted target, expands matching groups,
  restores the current row after clear, and renders an inert empty state.
- Added Quest text search that composes with access, difficulty, length,
  timeline, completion, and start-eligibility filters. Migrated Shop's existing
  source-backed search input onto the same component without changing backend
  result semantics.
- Kept `Current Slayer task only` out until real assignment state lands; no
  disabled placeholder or invented task state is exposed.
- Verification passes all 1,478 pure/core methods and all 1,478 real offscreen
  Qt methods with no failures or skips, plus focused interaction checks, visual
  offscreen rendering, test-quality, documentation, compilation, and
  worktree-safety gates.
- Published
  `status-updates/slayer-search-seam-results-2026-07-17.html` and its mobile-safe
  copy at <https://s1kaasu9wfmq.postplan.dev>.

## Slayer Dogs-family Combat slice — 2026-07-17

- Added the level-21 Jackal as an ordinary Combat target and the first
  executable representative of Slayer's Dogs family.
- Preserved the cutoff 270 LP, 27 Slayer XP, guaranteed Bones, aggression, and
  explicit 80 LP maximum hit. Darkan independently supplies its Attack 17,
  Strength 18, Defence 15, melee identity, and respawn row.
- Added a sourced 48px target asset and provenance, exact data/preview
  regressions, and a real offscreen Qt picker assertion covering the row,
  tooltip, and rendered icon.
- Verification passes all 1,481 core methods, 337 focused
  Combat/target/runtime/cadence methods, the real offscreen Qt picker check,
  documentation, compilation, test-quality, diff, and worktree-safety gates.
- Kept Turael/Spria and Mazchna/Achtryn hidden. This certifies one baseline
  family dependency; it does not renormalize either incomplete master pool.
- Durable evidence:
  `source-audits/slayer-dogs-jackal-combat-2026-07-17.md`.

## Slayer Icefiend Combat slice — 2026-07-17

- Added the ordinary level-13 Icefiend as an executable Slayer-family target;
  God Wars, Ghorrock, quest, Revenant, and Daemonheim variants remain distinct.
- Preserved the cutoff 150 LP, 15 Slayer XP, melee identity, passive stance,
  guaranteed Impious ashes, and explicit 20 LP maximum hit. game-main and the
  matching Darkan level-13 row converge on Attack 10, Strength 10, and Defence
  12; the cutoff page overrides game-main's conflicting 7 XP and hybrid style.
- Added game-main's exact 128-slot ordinary drop table, a sourced target asset,
  provenance, exact roster/preview regressions, and real offscreen Qt picker
  coverage.
- Verification passes all 1,482 core methods, 339 focused
  Combat/target/runtime/cadence methods, the real offscreen Qt picker check,
  documentation, compilation, test-quality, diff, and worktree-safety gates.
  Reachability remains the declared 290-orphan debt ledger rather than a green
  gate.
- Kept Turael/Spria hidden. The family dependency is ready, but the incomplete
  master pool is not renormalized or exposed.
- Durable evidence:
  `source-audits/slayer-icefiend-combat-2026-07-17.md`.

## Live cadence activation — 2026-07-17

- Made the `R = 1000` cadence kernel default-on with an explicit boolean-false
  legacy rollback.
- Added complete handler/route coverage, exact lower-endpoint residual admission
  for compatible ranged evidence, authentic embedded-probability routes, and
  source-blocked passthrough for incompatible rows.
- Changed ordinary Combat to `6 × M` immediate ticks with persistent encounter,
  prayer/curse, status, special-regeneration, and RNG phase. Again grants no
  encounter beat; terminal boundaries cannot chain another enemy.
- Preserved one collapsed quest stage per eligible review while keeping
  flag-off quest combat at its legacy 50 ticks.
- Replaced the three retired XP-parity expected failures and obsolete runtime
  shadow integration tests with live route, residual, RNG, continuity, undo,
  and coverage tests.
- Reconciled Design 2 timing decisions: Loyalty and Veteran counts remain on the
  independent 240-answer world day; Aura windows are eligible-action budgets;
  recurring entries reuse world-calendar boundaries; Tears beats are
  activity-progress actions; Castle Wars retains 5,000 games but drops the
  invalid 16,667-review calendar conversion.
- Final post-review verification passes all 1,476 core methods (1,275 ordinary
  passes and 201 environment skips) and all 1,476 real offscreen Qt methods
  with no skips. The focused
  cadence/kernel/parity/combat/runtime/Summoning/Thieving slice passes 363
  methods. Documentation, compilation, reachability, asset integrity, worktree
  safety, and test-quality gates also pass; the quality audit reports zero hard
  issues across 71 test files.
- Fixed the final independent-review blocker: successful Combat answers no
  longer mark a live encounter disengaged and therefore cannot trigger
  between-fight Dream healing mid-encounter. Again still marks disengagement,
  and the next successful slice resumes the exact combat/RNG phase.
- Published `status-updates/cadence-kernel-live-results-2026-07-17.html` and
  its mobile-safe copy at <https://nl2rgoy9pvqk.postplan.dev>.

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

## Slayer Cockatrice and Banshee protective equipment (2026-07-17)

- Pinned the cutoff Mirror-shield trigger, fixed eye-beam hit, one-quarter stat
  floor, item identity, slot, equip gate, and Slayer-shop acquisition.
- Reconciled the hidden damage function as the smallest labeled mapping:
  Darkan's maximum-LP/6 fixed hit capped at the period page's 110 LP.
- Reconciled the repeated drain from the period one-quarter floor and
  2011Scape's 25%-of-base Attack, Strength, Defence, Ranged, and Agility set.
- Added the data-driven Combat consequence, fixed-hit/prayer bypass, persistent
  current-level drains, ordinary food/death/retreat/undo integration, and a
  non-blocking target warning.
- Added Banshee's complete head-slot protection family, fixed maximum-LP/10
  scream capped at 80 LP, and the period-proven eight affected skills.
- Reconciled the unresolved drain rule as the smallest labeled abstraction:
  Darkan's flat five-level magnitude applied to the period's complete skill set,
  floored at level 1. Summoning is now implemented and no longer a dependency
  blocker.
- Verification passes 236 focused Combat/roster/metadata tests, one real
  offscreen Qt picker check, and all 1,485 current core methods with 203 skips.
  Test quality has zero hard issues and no new clone group; documentation,
  compilation, diff and worktree-safety checks pass.

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
- At this checkpoint all four finisher families remained hidden: target data,
  context-correct drops, enemy assets, and reachable finisher runtime were not
  yet jointly certified.

## Slayer Desert lizard and generic finisher runtime — 2026-07-17

- Added the cutoff level-24 Desert lizard with Slayer 22, 250 LP, maximum hit
  40 LP, 25 Slayer XP, reconciled Darkan stats, guaranteed Bones, and one exact
  100,000-slot source-probability drop selector.
- Added a generic loaded-finisher pack and manual action. Lethal damage holds a
  required target at 1 LP; the valid action atomically spends one Ice cooler,
  awards the kill/drops, clears the encounter, and resets to Attack.
- Added the 400-point automatic-finisher seam. It still requires and consumes
  the item, supports player-side lethal damage sources, and cannot spend a
  second item after the target is already dead.
- Flattened Desert heat into a labeled, wall-clock-free supply rule: one
  Waterskin dose per damaging Combat review. Dose remainders, eight-skin pack
  loading, carried-slot cost, depletion, and the existing two-review bank run
  are executable. Exact historical heat interval/damage remains
  `source_blocked`.
- Added a sourced 48px sprite/provenance row, tooltip and pack legibility,
  persistence migration, runtime telemetry, and real offscreen Qt action-state
  coverage.
- Kept every incomplete Slayer master hidden. This certifies Desert lizards as
  a family dependency and makes the finisher engine reusable by Rockslug,
  Gargoyle, and Mutated zygomite; it does not renormalize a master pool.
- Durable evidence:
  `source-audits/slayer-desert-lizard-combat-2026-07-17.md`.
- Final verification: 1,497 core methods (1,293 ordinary passes and 204
  expected environment skips), 1,497 real offscreen Qt ordinary passes, zero
  hard test-quality issues, and passing documentation, compilation, diff,
  item-reachability, and worktree-safety audits.

## Slayer Rockslug and Gargoyle Combat slices — 2026-07-17

- Added Rockslug with Slayer 20, 270 LP, maximum hit 41, exact 27 Slayer XP,
  the cutoff 1–39 LP Bag-of-salt finisher, and a latched 10-LP
  frozen/no-retaliation state.
- Added Gargoyle with Slayer 75, 1,050 LP, maximum hit 119, exact 105 Slayer
  XP, the cutoff below-90 LP reusable Rock-hammer action, and continuous
  regeneration represented as `12/5` LP per gameplay tick with a persisted
  integer residual.
- Reconciled one Darkan ordinary selector per target with separate 2011Scape
  charm tables. The ordinary Gargoyle target excludes the
  Kuradal's-Dungeon-only Ferocious ring.
- Corrected Combat supply refill so changing targets returns obsolete finisher
  and hazard supplies, loads one copy of a reusable non-stackable tool, and
  counts non-stackable finisher slots accurately.
- Added period RuneScape Wiki icons and changed the Combat asset fetcher to
  prefer RuneScape Wiki files over same-named OSRS fallbacks.
- Focused backend verification passes 374 methods and the real offscreen Qt
  action/picker check. The complete core suite passes 1,504 methods, with 1,300
  ordinary passes and 204 declared environment skips. All 200 real main-menu
  widget tests pass. Their harness now flushes deferred dialog deletion after
  each test, reducing the measured peak resident memory from 9.7 GB to 1.22 GB
  and removing the pathological application-style recomputation tail. The
  complete real offscreen Qt suite passes all 1,504 methods without skips or
  failures in 490.6 seconds.
- Durable evidence:
  `source-audits/slayer-rockslug-gargoyle-combat-2026-07-17.md`.
- Results artifact:
  `status-updates/slayer-rockslug-gargoyle-results-2026-07-17.html`
  (<https://887yman86rqy.postplan.dev>).

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

## Stolen Hearts quest dependency — 2026-07-17

- Replaced all five generated objective placeholders with a playable,
  source-backed quest chain covering the Skulls infiltration, Khnum pursuit,
  three mercenary fights, temporary-item custody, rooftop/treasury traversal,
  Het's scales, the Kharid-ib, and Osman's handoff.
- Corrected the generated rewards by removing the bogus Khnum item and
  separating direct 250 Constitution XP from the three authentic 250-XP lamp
  claims; the quest now awards 2,500 coins and preserves its three quest
  points.
- Registered rev-742 item identities 25127 and 25128, added the two
  period-named quest-item icons with provenance, and removed one statless
  Combat row from the catalog debt ledger.
- Added pure, live-dispatch, source-contract, asset, and real offscreen Qt
  regressions. The complete core suite passes all 1,508 methods with 1,303
  ordinary passes and 205 declared environment skips; the complete real
  offscreen Qt suite passes all 1,508 methods without skips or failures.
  Test-quality, documentation, compilation, diff, quest-audit, asset, and
  worktree-safety gates pass. Diamond in the Rough is next.
- Published `status-updates/quest-stolen-hearts-results-2026-07-17.html` and
  its mobile-safe copy at <https://4sptl2883909.postplan.dev>.

## Diamond in the Rough quest dependency — 2026-07-17

- Replaced four generated objective placeholders with a playable chain
  covering the Heavy weight, six-enemy sundial ambush, Sundial gnomon,
  quicksand/Kalphite nursery, three retained gems, Apep/Heru finale, and Prince
  Ali rescue.
- Corrected the reward parser boundary: ordinary completion grants 250
  Agility, Constitution, and Thieving XP plus the existing Combat lamp; the two
  optional 20,000-XP level-80 fissure actions are no longer auto-awarded.
- Registered rev-742 item identities 25116 and 25118, installed their original
  September 2012 sprites with provenance, and reduced the statless quest
  Combat ledger from 102 to 98 rows.
- Added source-contract, pure full-chain, live-dispatch, asset, and real
  offscreen Qt regressions. The complete core suite passes all 1,512 methods
  with 1,306 ordinary passes and 206 declared environment skips; the complete
  real offscreen Qt suite passes all 1,512 methods without skips or failures.
  Test-quality, documentation, compilation, diff, quest-audit, asset,
  reachability, and worktree-safety gates pass. Icthlarin's Little Helper is
  next.
- Published
  `status-updates/quest-diamond-in-the-rough-results-2026-07-17.html` and its
  mobile-safe copy at <https://6vqmrgu0eo7j.postplan.dev>.

## Icthlarin's Little Helper quest dependency — 2026-07-17

- Replaced the generated placeholders and statless Combat rows with a playable
  nine-step quest chain covering hypnosis, canopic-jar custody, the Sphinx
  riddle and token, exactly one jar-bound guardian, the Sophanem ceremony, both
  quest symbols, the Possessed Priest, and the final report.
- Split the guardian and priest fights from their adjacent inventory
  transactions. The canopic jar and unholy symbol now leave the carried pack
  before Combat, while ceremony supplies are required only after the guardian
  dies.
- Preserved exact ordinary rewards: two quest points, 4,500 Thieving XP, 4,000
  Agility XP, 4,000 Woodcutting XP, and one Catspeak amulet. Priest drops remain
  explicit implementation/source debt because the quest encounter schema has
  no drop transaction and the random potion distribution is not pinned.
- Registered seven period quest-item icons with pre-cutoff provenance and
  extended the reusable asset fetcher with cutoff-aware historical file
  revision lookup.
- Added source-contract, complete pure-chain, live-dispatch, registry, asset,
  quest-debt, and real offscreen Qt regressions. The complete core suite passes
  all 1,517 methods with 1,310 ordinary passes and 207 declared environment
  skips; real offscreen Qt discovery passes all 1,517 methods without skips or
  failures. Smoking Kills is now complete; Contact! was not a cutoff
  prerequisite.
- Durable evidence:
  `source-audits/quest-icthlarins-little-helper-playable-2026-07-17.md`.
- Published
  `status-updates/quest-icthlarins-little-helper-results-2026-07-17.html` and
  its mobile-safe copy at <https://llzbgu6xic8d.postplan.dev>.

## Slayer Turael/Spria runtime closure — 2026-07-17

- Activated the first complete Slayer master role from the reconciled
  23-family Turael/Spria pool.
- Added Gelatinous abomination, Young grotworm, and Monkey as executable Combat
  representatives with period stats, Slayer XP, drops, and assets.
- Implemented the worn-only reusable Spiked-gauntlet finishing rule and
  recovered item `23035` across all eight Slayer shops even though the legacy
  item source omits it.
- Registered Coral bolts and Royal cape as source-backed equipment drops with
  their period identities, stackability, tradeability, slots, bonuses, and
  pinned sprites.
- Added assignment, Combat-credit, migration, undo, task-filter, hub, shop
  generator, and real offscreen Qt regression coverage. Complete core discovery
  passes 1,537 methods with 1,326 ordinary passes and 211 declared environment
  skips; complete real offscreen Qt discovery passes all 1,536 methods without
  skips or failures, with the latest item-only seams covered by a targeted
  holdout.
- Fable's bounded UI review found no wiring or dark-mode defects and surfaced
  two real copy problems: internal readiness jargon and a task-filter dead-end
  message. Both are fixed.
- No new design gap emerged. Smoking Kills is now complete.
- Published
  `status-updates/slayer-turael-runtime-results-2026-07-17.html`
  (<https://5k6wxpak7xkj.postplan.dev>).

## Smoking Kills playable Slayer dependency — 2026-07-18

- Replaced four generated placeholders, the malformed grouped combat parser
  row, and six bogus completion-item rewards with a playable thirteen-journal
  quest whose twelve requirements cover both tomb wings, both Mummy Warriors
  and path keys, Catolax's Masked-earmuffs transformation, the Mighty banshee
  and voice, the barrier, the Banshee Mistress, and Sumona's report.
- Kept the period half-health assassin phase visible while collapsing its four
  temporary adds into the one boss battle they actually support. Tomb waves,
  Mummy hidden stats, and the Banshee voice rate use explicit bounded
  abstractions where the period evidence is `source_blocked`.
- Added optional quest-combat `minimum_player_combat` metadata. Smoking Kills
  therefore shows its level-90 and level-111 enemies while retaining the
  quest's sourced Combat 85 player gate; every existing encounter keeps its
  prior default.
- Canonicalized the Restless Ghost reward name to the already-live
  `Ghostspeak amulet`, registered cache identities 552, 1555, 13259, 13260,
  13276, and 13277, generated real neck/head equipment rows, and pinned five
  pre-cutoff quest sprites.
- Completion grants exactly one quest point and 5,000 Slayer XP. Sumona and the
  existing reward surface become reachable, while `slayer_points` and
  `slayer_qualifying_streak` remain unchanged so no pre-quest task earns
  retroactive points.
- A bounded Fable UI/copy review approved the fixed tomb order and stage
  density, and caught the hidden Combat-111 player gate plus four presentation
  hazards. All reproduced findings were fixed; no owner-level design gap
  emerged.
- Focused catalog, pure, integration, registry, equipment, debt-ledger, and
  real offscreen Qt checks pass. Full core discovery passes 1,542 methods with
  1,330 ordinary passes and 212 declared environment skips; full real offscreen
  Qt discovery passes all 1,542 methods without skips or failures.
- Test-quality audit reports zero hard issues across 72 files. Documentation
  audit passes 279 Markdown and 315 HTML files. Reachability is 1,220 actions,
  1,789 reachable items, 288 orphan inputs, and 314 blocked actions; this batch
  introduces no orphaned Smoking Kills stage item. Compilation, provenance
  JSON, combat-debt, diff, and worktree-safety checks pass.
- Durable evidence:
  `source-audits/quest-smoking-kills-playable-2026-07-18.md`.
- Published
  `status-updates/quest-smoking-kills-results-2026-07-18.html`
  (<https://0hj7sz8kn416.postplan.dev>).
- The next Slayer implementation dependency is Shilo Village and the complete
  transitive black-mask / Slayer-helmet route.

## Shilo Village playable Slayer dependency — 2026-07-18

- Replaced seven generated objective buttons with eleven review-native
  requirements plus the completion sentinel, covering Ah Za Rhoon, Zadimus,
  Bervirius, every quest-item transformation, Rashiliyia's tomb, and her release.
- Replaced the generated single boss placeholder with ordered level-91 zombie,
  level-68 skeleton, and level-93 ghost encounters using complete Darkan
  resolver definitions.
- Registered all thirteen rev-742 quest-item identities and pre-cutoff sprites;
  Beads of the dead now generate as real neck equipment.
- Preserved the period-optional Stone-plaque without making it a progression
  gate. The collapsed temple review includes the item automatically, and the
  UI does not promise Yanni's separate post-quest sale service.
- A bounded Fable UI/copy review accepted the route and found five concrete
  seams. Optionality wording, absent-sale wording, the pre-quest supply list,
  Ah Za Rhoon geography, and the cache citation are all corrected.
- Full core discovery passes all 1,546 methods with 213 declared environment
  skips. Full real offscreen Qt discovery passes all 1,546 methods without
  skips or failures. The final 355-method focused backend set and three-method
  real Qt holdout also pass.
- Test quality reports zero hard issues across 72 files. Documentation,
  compilation, provenance JSON, combat-gap, diff, reachability, and worktree
  safety audits pass; the known reachability ledger remains 1,220 actions,
  1,789 reachable items, 288 orphan inputs, and 314 blocked actions.
- Durable evidence:
  `source-audits/quest-shilo-village-playable-2026-07-18.md`.
- Published
  `status-updates/quest-shilo-village-results-2026-07-18.html`
  (<https://tqgeemw7wsuo.postplan.dev>).
- Next: repair Jungle Potion's remaining generated stage buttons, then continue
  Big Chompy Bird Hunting → Zogre Flesh Eaters → Rum Deal → Cabin Fever before
  the Mos Le'Harmless, Cave horror, Black mask, and Slayer-helmet runtime.

## Wall beast playable Slayer target — 2026-07-18

- Added the ordinary level-49 Wall beast with cutoff combat identity, Slayer
  gate/XP, maximum hit, Darkan stats/respawn, a reconciled 100,000-slot drop
  table, and its pre-cutoff icon.
- Added a reusable start-only equipment gate. Spiny helmet is checked when a
  fight begins, not on every attack; an active beast survives a legal helmet
  swap, while the next spawn again requires the helmet.
- Enforced the cutoff poison immunity against the existing Ancient Smoke-spell
  poison effect.
- Reused every existing canonical item identity, including cache item 4544 as
  `Bullseye lantern (unf)` and item 4089 as `Mystic hat`; no parallel registry
  names were introduced.
- Mazchna/Achtryn now derives at 24/27 ready families. Cyclopes, Mogres, and
  Vampyres are the remaining exact blockers.
- Focused pure and real offscreen Qt checks pass. Complete core discovery passes
  all 1,570 methods with 213 declared environment skips; complete real
  offscreen Qt discovery passes all 1,570 methods without failures or skips.
- Durable evidence:
  `source-audits/slayer-wall-beast-combat-2026-07-18.md`.
- Published
  `status-updates/slayer-wall-beast-combat-results-2026-07-18.html`
  (<https://0aaltfsrmyrn.postplan.dev>).

## Slayer Mogre source closure and quest handoff — 2026-07-18

- Closed the ordinary level-60 Mogre combat contract from cutoff Wiki
  revisions and Darkan: Slayer 32/48 XP, atomic Fishing-explosive lure,
  poison immunity, exact melee cadence and damage, a 128-slot main drop table,
  guaranteed Big bones, and independent long/curved-bone tertiaries.
- Recovered the complete non-combat Skippy supply chain and its sole gameplay
  reward. The live Slayer family already names the correct completion ID,
  `skippy_and_the_mogres`, but the quest catalog does not implement it.
- Kept Mazchna/Achtryn at 24/27 rather than adding a permanently locked partial
  Combat target. The exact quest implementation handoff is appended to
  `codex-briefs/darkan-quest-agent-handoff-2026-07-18.md`.
- Recorded missing Mudskipper hat/Flippers identities and icons, the optional
  Super fishing explosive acquisition dependency, and the Rag and Bone Man
  context restriction without inventing routes or weights.
- No owner design decision was required. Durable evidence:
  `source-audits/slayer-mogre-combat-2026-07-18.md`.

## Feral vampyre playable Slayer target — 2026-07-18

- Added the ordinary level-61 Feral vampyre with cutoff combat identity,
  Priest in Peril access, 40 Slayer XP, 74-LP maximum hit, Darkan
  stats/respawn, a guaranteed Vampyre dust drop, and a losslessly reconciled
  100,000-slot table.
- Added data-declared weakening-equipment behavior. Wearing the existing
  ordinary Holy symbol reduces the Vampyre's enemy accuracy and maximum hit by
  20% in both preview and live Combat.
- Added the source-described occasional bite using a labeled bounded
  abstraction: 1/8 of landed damaging attacks, at most 20 LP healed, and one
  random implemented skill drained by one current level.
- Installed the pre-cutoff level-61 historical sprite with provenance and
  exposed the weakness and bite outcome on the existing Combat UI/runtime
  surfaces.
- Mazchna/Achtryn now derives at 25/27 ready families. Mogres wait on the
  Darkan-owned Skippy miniquest; Cyclopes wait on the full Warriors' Guild
  activity rather than a context-free Combat row.
- Focused pure coverage passes 332 methods and the focused real offscreen Qt
  picker surface passes. Complete core discovery passes all 1,574 methods with
  213 declared environment skips; complete real offscreen Qt discovery passes
  all 1,574 methods without failures or skips.
- Durable evidence:
  `source-audits/slayer-feral-vampyre-combat-2026-07-18.md`.
- Published
  `status-updates/slayer-feral-vampyre-results-2026-07-18.html`
  (<https://v0w3h4u00jo4.postplan.dev>).

## Aberrant spectre playable Slayer target — 2026-07-18

- Added the ordinary level-96 Aberrant spectre with its Priest in Peril and
  Slayer-60 gates, 900 LP, 90 Slayer XP, six-tick Magic cadence, and exact
  protected/unprotected hit behavior.
- Added a data-declared stench rule: Nose peg and Slayer helmets protect
  completely; otherwise max-LP/10 damage always lands while Protect from Magic
  blocks only the random five-level combat-stat drain.
- Encoded Darkan's ten weighted ordinary rows as its executable 512-slot
  mutually exclusive selector, plus exact nested herb, rare-seed, gem, and
  mega-rare tables and the independent 1,212-way charm selector.
- Generated Mystic robe bottom (dark) as real legs equipment and installed
  provenanced sprites for the target, Mystic bottom, and Vecna skull.
  Regeneration also repaired the latent Adamant spear and Black dagger (p)
  equipment rows from the preceding Shadow-warrior slice.
- Vannaka now derives at 25/35 ready families. Nine Combat targets plus Earth
  warrior's Wilderness-risk behavior remain; the master stays hidden and
  unrenormalized. No quest files were touched and no owner design gap emerged.
- Durable evidence:
  `source-audits/slayer-aberrant-spectre-combat-2026-07-18.md`.
- Focused pure/registry coverage passes 331 checks and the real offscreen Qt
  picker regression passes. Full discovery runs 1,614 methods: 1,400 ordinary
  passes and 214 declared skips.
- Published
  `status-updates/slayer-aberrant-spectre-results-2026-07-18.html`
  (<https://fr3fmom6akth.postplan.dev>).

## Slayer Fungal-mage source boundary — 2026-07-19

- Closed the cutoff-visible Fungal-mage contract: level 120, 1,200 LP,
  Slayer 1/120 XP, Magic-50 assignment gate, six-tick Magic, 114-LP maximum,
  poison immunity, 2–3-LP proximity infestation, and the roughly 20-second
  Neem-oil weakening loop.
- Pinned rev-742 NPC/item identities and Darkan's combat, infestation, oil,
  drops, cache bonuses, and exact 606-slot charm lead.
- Kept the target blocked because Darkan's `nostats` definition explicitly
  generates non-real combat levels, the period sources conflict on the exact
  Melee/Ranged reducer, the ordinary sources disagree on two quantities, and
  the canonical Neem-drupe/jug/oil acquisition chain is not live.
- Chaeldar remains hidden and unrenormalized at 25/34. No owner design fork was
  reopened. Durable evidence:
  `source-audits/slayer-fungal-mage-combat-2026-07-19.md`.

## Slayer Grifolic-creatures source boundary — 2026-07-19

- Closed the period-visible Grifolapine and Grifolaroo identities, Slayer and
  Magic gates, hybrid attacks, fungal hazards, neem transitions, client IDs,
  and named resource/drop sets.
- Kept both targets blocked because their Darkan `nostats` rows explicitly
  generate non-real combat levels; Grifolaroo also conflicts on LP/maximum,
  Grifolapine conflicts on infestation damage, and the shared handler never
  performs the cutoff Magic-to-Ranged neem transition.
- Confirmed the two Darkan ordinary-drop files are duplicated reconstruction
  stubs despite the cutoff monsters having materially different tables.
- Chaeldar remains hidden and unrenormalized at 25/34. No owner design fork was
  reopened. Durable evidence:
  `source-audits/slayer-grifolic-creatures-combat-2026-07-19.md`.

## Slayer Jungle-strykewyrm source boundary — 2026-07-19

- Closed the period-visible Jungle-strykewyrm identity, Slayer-73
  assignment-only gate, hybrid attack cadence, poison families, tunnelling
  concept, client IDs, and named drop set.
- Kept the target blocked because Darkan's `nostats` row generates non-real
  combat levels and its custom handler contradicts the cutoff melee-poison and
  burrow damage/poison consequences.
- Confirmed the ordinary-drop reconstruction conflicts with visible cutoff
  coin, Papaya-fruit, and herb quantities, while the current one-channel
  poison schema cannot represent three attack-conditional poison outcomes.
- Chaeldar remains hidden and unrenormalized at 25/34. No owner design fork was
  reopened. Durable evidence:
  `source-audits/slayer-jungle-strykewyrm-combat-2026-07-19.md`.

## Slayer Kurask source boundary — 2026-07-19

- Closed the complete real combat row, Slayer-70 gate/97 XP, aggressive
  six-tick melee, 120-LP maximum, cache bonuses, respawn, and every effective
  leaf/broad/Magic-Dart route.
- Confirmed the existing Turoth `restricted_weapon` seam can represent the
  settled Kurask kill loop without new design.
- Kept the target blocked because Darkan's ordinary selector conflicts with
  visible cutoff quantities, most clearly 20 noted Big bones against one or
  two ordinary Big bones, and fails to preserve the complete named drop set.
- Chaeldar remains hidden and unrenormalized at 25/34. No owner design fork was
  reopened. Durable evidence:
  `source-audits/slayer-kurask-combat-2026-07-19.md`.

## Slayer Troll registry stop — 2026-07-19

- Stopped before implementing Trolls because the settled broad-category
  contract and pool audit require explicit stable mountain/ice/river/undead
  membership, while `slayer_data.py` binds the complete family to only
  `("troll",)`.
- Confirmed one generic target would make readiness falsely certify the whole
  category and that Darkan's substring/name-fragment row cannot supply the
  required stable boundary.
- Made no runtime, variant, asset, or test changes. Chaeldar remains hidden and
  unrenormalized at 25/34. Durable conflict report:
  `audits/slayer-troll-registry-conflict-2026-07-19.md`.

## Slayer Vyrewatch and Warped-tortoise source boundaries — 2026-07-19

- Closed cutoff-visible identities, gates, combat concepts, restricted/chime
  interactions, cache identities, and named drops for both remaining
  independent Chaeldar families.
- Kept Vyrewatch blocked on the incomplete broad-family registry, conflicting
  level-110 maximum/drop data, uncorroborated hidden levels, and a
  quest-granted Ivandis flail which is not executable as Combat equipment.
- Kept Warped tortoise blocked on generated non-real combat levels, the
  106/120 maximum conflict, absent Crystal-chime handler/acquisition action,
  and a selector which conflicts with or omits major cutoff rows.
- Added a second durable registry-authority report for Vyrewatch rather than
  allowing one representative to falsely certify its multi-variant family.
- Read-only Workflow `338d915a-364d-4e18-aa81-8ab4531c01b8` was canceled
  without using either leaf: the Warped-tortoise leaf produced no telemetry,
  while the Vyrewatch leaf expanded to 135,162 tokens without a final report.
  The primary independently reproduced every recorded source and code finding.
- Chaeldar remains hidden and unrenormalized at 25/34. Evidence:
  `source-audits/slayer-vyrewatch-combat-2026-07-19.md`,
  `source-audits/slayer-warped-tortoise-combat-2026-07-19.md`, and
  `audits/slayer-vyrewatch-registry-conflict-2026-07-19.md`.

## Slayer Sumona hidden-pool encoding — 2026-07-19

- Encoded all 37 source-settled Sumona rows and their provisional 407-point
  denominator without activating the incomplete master.
- Added stable family identities for the 14 families first needed above
  Chaeldar, preserving Slayer gates and distinctive readiness features rather
  than allowing generic Combat rows to certify missing mechanics.
- Derived 18/37 families ready from current Combat data. Abyssal demon remains
  blocked on teleport interruption and Nechryael on Death spawns; 17 other
  families still report `combat_target`.
- Preserved Combat 85, Slayer 35, and the playable Smoking Kills completion
  gate. Eligible-family generation remains empty while Sumona is hidden, so no
  partial table can be rolled or silently renormalized.
- Added regression coverage for the complete row count, denominator, unusual
  count ranges, master gates, exact blocker ledger, and hidden-role behavior.
- Verification: `tests.test_slayer_logic` passes 17 tests; the focused
  Slayer/quest integration slice passes 19 tests; real offscreen Qt coverage
  passes 2 focused tests and the complete 1,681-test discovery suite. The core
  runner passes 1,681 tests with 215 environment skips. Documentation,
  test-quality, compile, readiness, diff, and worktree audits pass. The
  repository-wide reachability audit retains its pre-existing orphan/action
  backlog and reports no Sumona-specific item regression.
- Codex Workflows run `9e94a9cc-ea1b-448b-b432-19cce62202b5` produced no
  review result: one Sol-high leaf timed out after 540 seconds and the second
  never established a session before the 600-second run timeout. Its telemetry
  was not used as evidence; the root independently reproduced and verified the
  complete slice.
- Results artifact:
  `status-updates/slayer-sumona-hidden-pool-results-2026-07-19.html`
  ([mobile copy](https://c00hpkv6e9ws.postplan.dev)).

## Slayer Abyssal/Nechryael special-mechanic harvest — 2026-07-19

- Pinned the cutoff Abyssal teleport behavior and Nechryael/Death-spawn roster
  behavior from exact pre-EOC revisions and checked their last relevant
  pre-cutoff talk revisions.
- Kept both families non-certifying. Abyssal teleport chance and interruption
  magnitude remain source-blocked. Nechryael summon probability and spawn
  lifetime remain source-blocked.
- Recorded the emulator conflict instead of resolving it: Darkan removes Death
  spawns when the summoner dies, while the cutoff strategy text describes
  killing the Nechryael before handling or avoiding the surviving spawn.
- Located the future implementation inside the pure Combat burst transaction
  and the settled engaged-target plus pressure-roster contract. No global map,
  wall clock, partial special loop, or owner design fork was introduced.
- Read-only Workflow `3c11e193-9b94-48cd-9e02-5d6bb15c4101` was canceled
  without using either leaf. The Abyssal leaf expanded to 85,033 generated
  tokens and remained stuck in a wait without a final report; the Nechryael
  leaf never established a session and emitted no telemetry. The primary
  independently reproduced every accepted source finding.

## Slayer Iron dragon Combat target — 2026-07-19

- Added the ordinary level-189 Iron dragon as Sumona's nineteenth certifying
  family, preserving 1,650 LP, 173.2 Slayer XP, six-tick attacks, and the
  existing bounded metal-dragon dragonfire model.
- Imported Darkan's exact Combat stats, defences, 59-tick respawn, guaranteed
  Dragon bones and five Iron bars, the 128-slot ordinary selector including
  its explicit empty slot, a losslessly enumerated quantity-two charm table,
  and independent plate, visage, and hard-clue rolls.
- Added the pre-cutoff target image and provenance plus roster, selector,
  readiness, and real offscreen Qt coverage.
- Sumona now derives 19/37 families ready and remains hidden and
  unrenormalized. No owner-facing design gap emerged.
- Verification: 319 focused Slayer/Combat tests pass; the real offscreen Qt
  Combat-target/tooltip check passes; the complete core runner passes 1,683
  tests with 215 environment skips. Documentation, test-quality, compile,
  provenance JSON, readiness, diff, and worktree audits pass. The
  repository-wide reachability audit retains its known 288-orphan/313-blocked
  backlog and reports no Iron-dragon-specific regression.
- Results artifact:
  `status-updates/slayer-iron-dragon-results-2026-07-19.html`
  ([mobile copy](https://za9osdb8btx6.postplan.dev)).

## Slayer Red dragon family Combat targets — 2026-07-19

- Added the ordinary level-152 Red dragon and level-48 Baby red dragon as
  Sumona's twentieth certifying family, preserving the cutoff substitution
  relationship and adult-only dragonfire.
- Preserved the direct period adult maximum of 158 LP and recorded Darkan's
  conflicting 144-LP value as a rejected lower-tier lead rather than silently
  selecting the convenient emulator value.
- Imported exact executable combat levels, defences, respawns, guaranteed
  drops, the adult's 128-slot ordinary table with three real empty slots,
  losslessly enumerated charms, Summoning-gated egg, and hard clue.
- Added both pre-cutoff target images and provenance plus roster, selector,
  readiness, and real offscreen Qt coverage.
- Sumona now derives 20/37 families ready and remains hidden and
  unrenormalized. No owner-facing design gap emerged.
- Verification: 321 focused Slayer/Combat tests pass; the real offscreen Qt
  Combat-target/tooltip check passes; the complete core runner passes 1,685
  tests with 215 environment skips. Documentation, test-quality, compile,
  provenance JSON, readiness, diff, and worktree audits pass. Reachability
  improves from 288 orphan inputs / 313 blocked actions to 286 / 309.
- Read-only Workflow `fe36e1d0-6431-4163-88a3-938428bec3d0` was canceled
  after roughly nine minutes because both Sol-high leaves remained before
  session creation: no worker PID, provider session, stdout/stderr path,
  token, tool, or progress telemetry was ever produced. No partial result was
  used; the primary independently reproduced and verified the complete slice.
- Results artifact:
  `status-updates/slayer-red-dragon-family-results-2026-07-19.html`
  ([mobile copy](https://2365habrkscc.postplan.dev)).

## Slayer Scabaras lancer source boundary — 2026-07-19

- Pinned the cutoff level-112, 900-LP, 90-XP Scabaras lancer with melee,
  approximate 130 maximum, poison behavior, guaranteed Bones, Sumona
  assignment, and explicit Scabarites qualification.
- Confirmed the rev-742 ID and Attack option and harvested Darkan's 59-tick
  respawn, defensive bonuses, denominator-bearing drops, and hard-clue row.
- Kept the target source-blocked because Darkan explicitly marks the combat
  definition `nostats`; the cache cannot supply server levels, and game-main
  has spawn rows but no combat definition. Attack, Strength, Defence, Magic,
  and Ranged remain absent.
- Excluded the post-EOC bestiary row, which conflicts at level 77 and 2,750 LP,
  and did not infer non-roll content from combat level 112.
- Sumona remains hidden and unrenormalized at 20/37. No owner-facing design
  gap emerged.
