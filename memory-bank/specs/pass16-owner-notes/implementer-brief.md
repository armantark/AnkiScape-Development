# Pass 16 implementer brief

Every Pass 16 implementer reads this file, then its ticket. The orchestrator
seat (Opus 5.5, T3 thread 66e7da34) dispatches the tickets, lands them on the
integration branch, runs the final review and the promotion gate.

<context>
- Spec: `memory-bank/specs/pass16-owner-notes/spec.md`. Every decision there is
  settled by the owner; do not relitigate it.
- Your ticket: `memory-bank/specs/pass16-owner-notes/tickets/<NN>-*.md`.
- Fact-finding with code citations (taken at main `839b86a7`; lines may have
  moved): `/Users/ArmanTarkhanian1/Documents/ankiscape-pass16/facts.md`. Read
  the section for your ticket's area before you open code.
- Binding rules: `memory-bank/codex-briefs/STANDING-SLICE-CONTRACT.md`, read in
  full, and the repository `AGENTS.md` (Qt dark-mode text colors, offscreen
  screenshot rules). Where this brief and the contract disagree, stop and
  report.
</context>

<worktree>
1. From the canonical checkout
   `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork`,
   run `python3 tools/worktree_guard.py audit`, then
   `python3 tools/worktree_guard.py add goal/pass16-<NN>-<slug> --name pass16-<NN> --start-point goal/pass16-integration`.
   The pooled lease is full; `add` is the guarded route.
2. Work only in the new worktree under
   `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/`.
   Never edit, stage or test inside the canonical checkout or the
   `pass16-integration` worktree.
3. Run `python3 tools/worktree_guard.py audit` again after the add.
</worktree>

<build>
- Build the ticket's end-to-end behavior and nothing else. Problems directly
  adjacent to your change are yours; anything found only because of those
  fixes goes in your report, not your diff.
- Test at the seams and layers the spec's Testing Decisions name, and only
  there. Drive the real review handler or the real widget; never stub the
  system under test.
- Focused tests: `python3 run_tests.py <selectors>` (plain) and
  `QT_QPA_PLATFORM=offscreen "/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.venv-qt/bin/python" -m unittest <modules>`
  run from your worktree. Run the two lanes one after the other.
- Before you commit, run the full plain lane once:
  `python3 run_tests.py` from your worktree. The promotion gate runs the full
  offscreen Qt lane later; you run the Qt tests your change touches.
  Homebrew `python3` has no Pillow, so three tests fail in the local plain
  lane on the base too: `test_every_small_ui_asset_is_tight_cropped`,
  `test_shop_outputs_and_period_activity_icon_are_reachable` and
  `test_vinesweeper_logic_does_not_mutate_input`. Report them as known; any
  other failure is yours.
- A ticket that changes what the player sees: build the main menu offscreen at
  560 px tall (and 720 px wide where the ticket says so) after `show()`,
  `resize()` and several `processEvents()` passes, check `text_fit_defects`,
  and save before and after PNGs under
  `/Users/ArmanTarkhanian1/Documents/ankiscape-pass16/evidence/<NN>/`. Check
  dark mode with a Fusion dark palette for any new text color. Add one line to
  `memory-bank/play-checklist.md`. Capture scripts stay in that evidence
  folder; never commit them to the repository.
- slop-gate (the commit hook) refuses: growth of any code or test file already
  above 1000 lines, a touched function above cyclomatic or cognitive
  complexity 15 or Halstead difficulty 80, and a new code file in a directory
  that already holds 40 (`logic/`, `logic_pure/`, `data/`, `tools/` and
  `tests/` are full; `ui/`, `core/` and test subpackages such as
  `tests/ui_flows/` have room). Hold an oversized file at net zero by moving a
  self-contained block you touch into a new module.
  `python3 tools/maintenance/function_metrics.py --output /tmp/pass16-<NN>-metrics.json <file> <functions...>`
  measures functions exactly as the hook does. Never set `SLOP_GATE_*` and
  never pass `--no-verify`.
- Do not add lines to the startup records `memory-bank/activeContext.md`,
  `progress.md`, `future-work-kanban.md`, `goal-priority-matrix.md` or
  `papercuts.md`: the docs audit caps them at 3,000 lines together and they
  hold 2,991. Report papercuts and second-level findings in your final
  message; the orchestrator records them.
- Do not spawn subagents. Do not run `tools/run_remote_tests.py`, launch Anki,
  or touch the MacBook; the native-check goal owns them.
</build>

<finish>
1. Review your own diff on two axes before you commit: against the spec and
   ticket (missing, extra, wrong), and against the contract and this repo's
   conventions. Fix what you find.
2. In the same commit, set your ticket's `**Status:**` line to `done`, or to
   `built; <layer> waits for the owner` where the ticket says so, and tick its
   acceptance boxes that passed.
3. Commit once on your branch. The message opens with the problem in plain
   language, then the solution; the subject says why the change matters.
4. Rebase your branch onto the current local `goal/pass16-integration` tip
   (one local repository; no fetch) so it lands as a fast-forward;
   rerun your focused tests if the rebase brought in changes to files you
   touched.
5. Leave the worktree in place; the orchestrator removes it after landing.
</finish>

<report>
Return plain text with these fields:
- `commit`: the final SHA on your branch, and the branch name.
- `worktree`: the absolute path.
- `tests`: each command you ran with its exact final lines (for example
  `Ran 412 tests in 31.2s` and `OK (skipped=3)`).
- `evidence`: the PNG paths, if any.
- `status`: what you set the ticket's Status line to.
- `papercuts`: one line each, or none.
- `second_level`: findings outside the ticket, or none.
- `deviations`: every place you departed from the spec or ticket, and why, or
  none.
</report>
