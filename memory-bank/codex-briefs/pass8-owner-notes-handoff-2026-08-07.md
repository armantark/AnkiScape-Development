# Pass 8 implementation trace

Date: 2026-08-07
Authority: `pass8-owner-fable-decisions-2026-08-07.md`
Starting commit: `659a115c0f6be84c26eeb5cf05a1f1b60ffd0bf1`

This file is the running Pass 8 implementation trace. It does not change the
settled product or visual contracts.

## Batch 1: immediate interaction repairs

### Reproduction

- Fish Flingers entered the event on the first click but did not select it for
  reviews. The selection call was behind an `elif` branch.
- Combat answers could consume food without a player-facing event row. The
  runtime result already contained the consumed-food events.
- Help used the tab-strip corner. The unreleased AnkiWeb review prompt used the
  footer that Pass 8 reserves for Help.

### Change

- One Fish Flingers click now enters the event and selects it for reviews.
- Combat answers aggregate each consumed food item and write
  `Ate N × Item · M left` to the event log.
- Help now sits at the bottom-right of the main menu. The unreleased review
  prompt is removed.

### Automated verification

- `/opt/homebrew/bin/python3 -m unittest tests.test_runtime_actions`: 141 tests
  passed.
- `/opt/homebrew/bin/python3 -m unittest tests.test_fish_flingers`: 16 tests
  passed.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_review_strip`:
  31 tests passed.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget`:
  382 tests passed in 144.508 seconds.
- Frozen read-only checker workflow
  `18151277-e5b5-44d5-aa85-1cc2a0ab6d74` returned `accept` with no findings.

### Native Anki verification

The MacBook Pro Codex Connection used only the disposable add-on and profile
under `/tmp/ankiscape-probe2`. It did not touch the canonical add-on or the
owner's real profile.

- Fish Flingers one-click entry and selection: passed.
- Help at the bottom-right with no review prompt: passed at the normal menu
  size.
- Vanilla answer controls and card-content non-overlap: passed at the normal
  reviewer size.
- Combat food event row: the disposable deck ended before the event could
  render. The follow-up fixture run could not start because host
  `remote-control:env_e_6a684c98946c8321ba89026140dd59e4` disappeared from
  the Codex Connection. This is an external native-evidence blocker, not a
  headless-parity claim. The targeted runtime regression test remains green.

The disposable UI matched all three changed semantic regions and compiled.
Its full-file SHA-256 was
`b22a90e5119f4f46a02a6f116a92a2a25e90291bba4d302376e0666a200e840a`,
not the canonical batch SHA-256
`6b3e19cb01067d9746509686fcf6c7d2cd58b0025472c10400eb864470d99e9c`.
The native report records this unrelated fixture drift. The deployed runtime
matched the canonical SHA-256
`a75614fe222b4e96b9ff041c64d67c3d255f0328e044a6f03ec9c1e60e7a3e02`.

Remote evidence is in
`/tmp/ankiscape-pass8-safe-batch-codex-connection/report.md` on the MacBook Pro.

### Decision

Keep the three changes. Automated coverage and the independent checker accept
the frozen product diff. Native Anki accepts both changed UI surfaces. Record
the combat-log screenshot as blocked until the MacBook Pro Codex Connection is
available again.

## Batch 2: combat auto-burial cadence

### Reproduction

The checked-in combat cadence used one simulated tick for each automatic bone
or ash action. The source action in
`bone_burying.plugin.kts` calls `wait(2)` before it removes the bone and awards
Prayer XP. A frozen regression run produced four expected failures: the
constant was 1, one automatic item returned 1 tick, and two automatic items
returned 2 ticks.

### Change

`AUTO_PRAYER_TICKS_PER_ITEM` is now 2. Manual Prayer training still consumes
one item per review. Bonecrusher, ectoplasmator, and prayer-urn interceptions
do not add automatic-burial ticks.

### Verification

- `tests.test_prayer_passives`: 10 tests passed.
- `tests.test_prayer`: 21 tests passed.
- `tests.test_combat_logic`: 285 tests passed.
- Frozen checker workflow `44a2f316-3e5e-4336-aea4-54af051e5c51`
  returned `accept` with no findings. Its two coverage gaps were converted into
  explicit manual-one-item and bonecrusher-zero-tick regression tests.

### Decision

Keep the one-line production change and its source-bound regression coverage.
