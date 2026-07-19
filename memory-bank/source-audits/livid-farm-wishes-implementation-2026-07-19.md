# Livid Farm source-ready wishes implementation — 2026-07-19

Status: **implemented, fully verified, and committed for closure.**

This record is newer than the remaining-wishes paragraph in
`livid-farm-core-implementation-2026-07-19.md`. It implements only the
source-ready reward commands and preserves every explicit source or dependency
boundary from `livid-farm-loop-2026-07-18.md`.

## Implemented

- `Vial My Herbs` spends 5,500 Produce and converts up to 50 of each eligible
  clean herb in the Livid Farm carried pack into its canonical unfinished
  potion. Dungeoneering herbs and Cave nightshade are excluded. The flat Bank
  identity intentionally collapses noted and unnoted items under the existing
  rule in `item-pack-and-magic-essence-identity-2026-07-16.md`.
- `Turn Lunar Lumber Into Runes` spends 5,500 Produce and converts every
  carried Lunar lumber. One persisted 0–27 lumber residual makes arbitrary
  partial conversions add to the exact 28-lumber output of 25 Astral runes and
  10 each Nature, Death, Earth, Cosmic, and Water runes.
- `More Planks Please` spends 18,000 Produce and installs ten answered-card
  world ticks, preserving the settled two-source-minutes-per-review
  short-duration mapping. Every answered card, including Again, spends one
  tick. An eligible Plank Make cast during an active tick uses the source
  approximately-one-in-ten extra-output roll.
- `Gimme Herbs` spends 18,000 Produce and grants the exact canonical Bank
  bundle: 3 grimy kwuarm, 3 grimy irit, 2 grimy cadantine, 2 grimy avantoe,
  and 1 grimy lantadyme.
- `Let it Rain Awesome Seeds` spends 55,000 Produce and grants exactly
  4 ranarr, 4 watermelon, 6 curry-tree, 2 pineapple, 2 papaya-tree, and
  4 willow seeds.
- Purchases are instantaneous direct commands. They create the shared
  `AnkiScape direct action` undo entry before mutating the live save. An
  unavailable purchase or failed undo registration changes nothing.
- Storage schema 47 sanitizes the new residual and duration state. A claimed
  Borrowed Power capstone now repairs the complete prerequisite unlock ladder,
  preventing an impossible finished-capstone/unfinished-progress save.

The direct reward implementation lives in `livid_farm_logic.py`; the
answered-card boundary is wired in `__init__.py`; Plank Make consumes the
active-tick marker through the ordinary Magic transaction in `logic_pure.py`.

## UI

The existing compact Livid Farm panel now exposes one wish selector and one
direct action button after Borrowed Power is claimed. Source- and
dependency-blocked wishes remain visible, use a dim picker row, disable the
action, and replace the main status line with a concise honest reason. The
terminal unlock progress bar collapses after the capstone so it cannot crowd
the reward controls.

Fable and Kimi K3 independently reviewed the wide and 900×560 renders.
Accepted changes:

- removed developer-facing `substrate` and `source_blocked` copy;
- visually distinguished unavailable picker rows;
- moved the More Planks countdown to the account status line;
- shortened the routine selector and moved its detail into tooltips;
- removed duplicated picker-side prices;
- collapsed terminal progress chrome; and
- added authoritative horizontal and vertical geometry assertions at the
  laptop size.

The final screenshot renderer remains
`tools/render_livid_farm_ui.py`.

## Explicit boundaries retained

- `Let it rain seeds`: exact period quantities remain `source_blocked`.
- `Reduce The Fish I Burn`: exact period burn-rate magnitude remains
  `source_blocked`.
- `Give me an Arcane Capacitor`: waits for the Borrowed Power equipment and
  charge substrate.
- `I'd Like a New Patch!`: waits for the one-use Livid allotment substrate.
- `Protect a Patch for me!`: waits for the selected ten-tree protection
  substrate.
- Lunar lumber conversion is live but its ordinary acquisition route is not
  claimed here.
- The shared cross-system temporary-effect HUD remains a separate settled UI
  substrate; the reward panel shows the More Planks countdown until that
  registry exists.

These are implementation or source dependencies, not new owner-design gaps.

## Verification

- Focused Livid/Magic/storage/runtime/integration suite: 269 tests passed.
- Final focused pure wish suite: 16 tests passed.
- Real offscreen Qt pre-capstone progress and post-capstone reward/900×560
  geometry: 2 focused tests passed.
- Full non-Qt suite: 1,802 tests passed with 229 expected environment skips.
- Full real-Qt offscreen suite: 1,802 tests passed with 1 intentional skip.
- Test-quality audit: 1,802 tests across 78 files, 0 hard issues.
- Final documentation audit: 399 Markdown and 369 HTML files passed.
- Compilation, diff integrity, and guarded worktree-layout checks passed.
- Reachability remains at the existing 284 orphan inputs and 305 blocked
  actions across 1,257 routes. The wish slice adds no false acquisition seed.
- Fable and Kimi K3 taste gates completed; every accepted issue was
  independently reproduced before editing.
- A fully quit and relaunched macOS Anki process opened exactly one AnkiScape
  menu from the floating button and rendered the native Utility surface. The
  user's low-level save correctly kept the Livid panel locked, so it was not
  modified merely to expose post-capstone controls. The final unlocked surface
  is proven by the real-Qt geometry test and the wide/laptop renders. A second
  post-test restart was unavailable because the Mac had locked; the two later
  changes were confined to zero-count inventory cleanup and a hidden
  pre-capstone status guard.
- Read-only Codex Workflows run
  `4b515306-4d92-4182-a516-d54bd258ebef` was canceled after prolonged shared
  startup contention and yielded no usable dependency report. Root work did
  not depend on it.

No new owner-design gap surfaced.

Results:

- `memory-bank/status-updates/livid-farm-wishes-results-2026-07-19.html`
- <https://r3408ncs6wyw.postplan.dev>
