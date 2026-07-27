# Agility implementation verification — 2026-07-15

Status: implemented and verified in the canonical checkout. This record maps
the settled design/source dossier onto the shipped code; it does not replace the
per-value evidence in the earlier Agility source audits.

## Shipped surface

- `agility_data.py`: 18 course/activity targets, stage XP, failure metadata,
  rewards, 68 ordinary/grapple shortcuts, Dorgesh route identities, travel
  inputs, item effects, and asset paths.
- `agility_logic.py`: storage sanitation, locks, obstacle/action resolution,
  failure damage and setback, lap/activity state, Brimhaven, reward commands,
  boost charges, direct-command undo payloads, and status text.
- `agility_travel.py`: target-specific trip profiles, carried-load calculation,
  weight reduction, level scaling, and residual review scheduling.
- `runtime_actions.py`, `__init__.py`, and `storage_pure.py`: one Agility action
  per answered review, shared LP/death and XP plumbing, persistence v36, review
  undo, bounded direct-command undo, and UI refresh.
- `target_metadata.py`, `skill_registry.py`, and `ui.py`: complete Support-skill
  registration, grouped Courses/Activities tree, real lock guards, live status,
  Benefits summary, reward commands, compact icon, and dark-mode-safe text.

## Live-owner integrations

- Hunter level-95 barehand butterfly variants award their exact Hunter and
  Agility XP and do not create a captured item.
- Tuna, swordfish, and shark have the labeled 10% Agility double-catch benefit;
  a double output does not award extra Fishing XP and does not affect Baron
  sharks.
- Herblore Agility potions/mixes and summer pie feed the Agility boost state.
- Habitat east-patch traversal, Farming travel, quest rewards, generic lamps,
  achievements, inventory, equipment, and LP/death use the existing owning
  surfaces rather than parallel Agility-only systems.

## Review-native abstractions

- Circus cadence is `answered_cards // (240 * 7)`. One completed visit remains
  closed until the next simulated answered-card week.
- Flash Powder Factory uses 24 reviews per session. Factory top adds three
  reviews as the proportional representation of its period two-minute benefit;
  the other outfit effects apply to failure, catalyst, rubble, and score/reward
  behavior.
- **Superseded 2026-07-26 by `design-thread-queue.md` 4.8:** the former
  ten-action activation was invented. The period +1 boost now holds passively
  while the Agility cape is equipped and does not apply from inventory.
- Source-blocked standard failures use the contract's global 20% entry curve,
  decaying to the sourced mastery point or 5% at level 99. Sourced obstacle
  consequences always override it.
- No Agility gameplay module imports `time` or `datetime`; an AST regression
  test enforces that boundary.

## Explicit future-owner boundaries

Summoning familiars, Slayer routes, Daemonheim/Dungeoneering, full Blast
Furnace, Livid Farm, diary acquisition, Barbarian Assault, and quest-owned
stages remain inert until their owners ship. Dorgesh pure/grapple/mixed route
identities are stable; exact grapple and mixed payout differences remain
`source_blocked`.

## Assets

`tools/fetch_agility_assets.py` reproduces the period asset set. The canonical
checkout contains the compact skill icon plus 42 Agility item images, with all
manifest entries recorded in `assets_provenance.json`. Path and provenance
coverage is exercised by `tests/test_agility.py`.

## Verification

- Focused backend regression: 354 tests passed.
- Full Python discovery: 1,241 tests passed; 183 non-Qt skips and three
  pre-existing expected XP-parity failures.
- Repository runner: 1,241 tests passed with the same expected-failure set.
- Full real offscreen Qt discovery: all 1,241 tests passed with no skips and the
  same three pre-existing expected XP-parity failures (537.838 seconds).
- Item reachability audit: 1,061 actions, 701 consumed items, and 271 orphan
  inputs (137 root, 134 cascade). The only Agility-named root is the authentic
  but currently unobtainable four-dose potion; its lower-dose entries are
  cascades, and decanting remains a future acquisition owner rather than a fake
  recipe added to this skill.
- Required closure checks: compilation, `git diff --check`, and worktree guard
  audit are rerun immediately before the checkpoint commit.

## Manual real-profile checklist

1. Open the Skills menu once and confirm one dialog opens, then select Agility.
2. Select an unlocked course and activity; verify locked rows cannot replace the
   current target.
3. Answer reviews through one success, one failure, one lap, and one activity
   completion; check XP, LP, setback, rewards, and status copy.
4. Exercise one reward command and both review/direct-command undo paths.
5. Restart Anki mid-course and confirm the stage/activity resumes exactly.
6. Equip one weight-reduction item and verify the Benefits travel summary changes.

## Carried-risk amendment verification — 2026-07-17

The post-closure owner amendment is now live:

- Auto and Custom use the existing target-local carried-layout owner rather
  than an Agility-only inventory. Auto projects course requirements before the
  player's ordered real-food preferences; Custom preserves the exact saved
  order and cannot borrow an omitted requirement from the Bank.
- The first selected-course engagement primes its pack for free. Later supply
  exhaustion schedules the ordinary one-review skilling bank trip before a
  refill; the refill comparison uses the complete projected layout rather than
  assuming that all remaining slots hold the first preferred food.
- Failure chance reads actual active-pack and equipment weight. The covered
  standard food and course requirements have reproduced or source-blocked
  nominal weights in
  `source-audits/agility-carried-weight-inputs-2026-07-15.md`.
- Course damage consumes active-pack food at the saved threshold. Fatal damage
  graves that target's pack and equipped gear without disturbing dormant
  target packs.
- The Wilderness course rolls its labeled 1% ambush only after completing a
  lap and before committing its award. A fatal hit forfeits the uncommitted lap
  reward and restores lap/Pit/modifier bookkeeping; normal review undo restores
  the complete pre-review state.
- Target readiness and the Auto summary expose requirements, food, weight,
  bank-trip state, and Wilderness risk. Generic non-Combat targets do not show
  Combat-only supply-mode or finite-loadout controls.

Verification added focused pure/runtime/integration/target-metadata coverage,
an exact fatal-ambush undo regression, and real offscreen Qt checks for both
the Agility summary and preserved Combat controls. The full core and full
offscreen Qt baselines are rerun at batch closure.
