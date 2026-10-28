# Pass 18 implementer brief

Every Pass 18 implementer reads this file, then its ticket. The orchestrator
seat (Opus 5.5, the T3 thread that grilled the owner) dispatches the tickets,
lands them on the integration branch, runs the native looks in real Anki, the
full test lanes on the Mac Studio, the final review and the promotion gate.

<context>
- Spec: `memory-bank/specs/pass18-owner-notes/spec.md`. Every decision there is
  settled by the owner; his answers, word for word, are in
  `grill-decisions.md`, and they are the approval for exactly the changes the
  spec names, including the changes to existing screens. Do not relitigate a
  decision, and do not change a screen the spec does not name.
- Your ticket: `memory-bank/specs/pass18-owner-notes/tickets/<NN>-*.md`.
- Code facts with citations, taken at main `d4f7164ac` (lines may have moved):
  `memory-bank/specs/pass18-owner-notes/code-facts.md`. Read the section for
  your ticket's area before you open code. Period sources:
  `memory-bank/source-audits/pass18-woad-dyes-goblin-diplomacy-2026-10-27.md`.
- Native looks in real Anki before the build:
  `/Users/armantarkhanian/Code/ankiscape-pass18/native/look-1/` and `look-2/`
  (`verdict.json` and PNGs).
- Binding rules: `memory-bank/codex-briefs/STANDING-SLICE-CONTRACT.md`, read in
  full, and the repository `AGENTS.md` (Qt dark-mode text colors, offscreen
  screenshot rules). This brief replaces the contract's section 6 lane
  commands and its `--expected-tests` collection for Pass 18: implementers run
  the focused tests named under <build>, and the orchestrator runs the full
  plain and offscreen Qt lanes, with their collected counts, on the Mac Studio
  after each landing. The rest of section 6 still binds you, including that a
  proof that a test is load-bearing leaves no trace. Where this brief and the
  contract disagree in any other way, stop and report.
</context>

<worktree>
1. From the canonical checkout `/Users/armantarkhanian/Code/AnkiScape`, run
   `python3 tools/worktree_guard.py audit`, then
   `python3 tools/worktree_guard.py add goal/pass18-<NN>-<slug> --name pass18-<NN> --start-point goal/pass18-integration`.
   The running Sol loop holds the pooled leases; `add` is the guarded route.
2. Work only in the new worktree under
   `/Users/armantarkhanian/ankiscape_worktrees/`. Never edit, stage or test
   inside the canonical checkout, the `pass18-integration` worktree, another
   ticket's worktree, the `papercuts-2026-10-27` worktree, or any pool
   worktree under `ankiscape_worktrees/pool/`, which the Sol loop owns.
3. Run `python3 tools/worktree_guard.py audit` again after the add.
</worktree>

<build>
- Build the ticket by steps 2 and 3 of `~/fleet/skills/universal/implement/SKILL.md`, read as a file.
- Build the ticket's end-to-end behavior and nothing else. Problems directly
  adjacent to your change are yours; anything found only because of those
  fixes goes in your report, not your diff.
- Test at the seams and layers the spec's Testing Decisions name, and only
  there. Drive the real review handler or the real widget; never stub the
  system under test.
- Tests run from your worktree with `python3 run_tests.py <selectors>`; it
  re-runs under the worktree's `.venv-qt` with offscreen Qt. Run your
  focused tests and the test packages next to your change. Do not run the
  whole suite: the Sol loop shares this machine (load about 15 on 14 cores on
  2026-10-27), and the orchestrator runs the full plain and Qt lanes on the
  Mac Studio after each landing. Homebrew `python3` has no Pillow on this
  MacBook, so a test that imports it can fail on the base too; a failure that
  also fails on `goal/pass18-integration` is known, and you report it. Any
  other failure is yours.
- Use `~/fleet/skills/universal/implement/scripts/job.py` for any shell job
  longer than a few minutes; `--help` defines its operations.
- A ticket that changes what the player sees: build the main menu or the
  review HUD offscreen at the default size and 560 points tall after `show()`,
  `resize()` and several `processEvents()` passes, check `text_fit_defects`,
  and save before and after PNGs, dark (Fusion dark palette) and light, under
  `/Users/armantarkhanian/Code/ankiscape-pass18/evidence/<NN>/`. Add one line
  to `memory-bank/play-checklist.md` that names the exact screen, hover and
  setting. Capture scripts stay in the evidence folder; never commit them.
- Menu text you add is working text; ticket 10 sets the final copy. Keep it
  short and plain.
- slop-gate (the commit hook) refuses: growth of any code or test file already
  above 1000 lines, a touched function above cyclomatic or cognitive
  complexity 15 or Halstead difficulty 80, an import fan-out increase, and a
  new code file in a directory that already holds 40 (`logic/`, `logic_pure/`,
  `data/`, `tools/` and `tests/` are full; `ui/`, `core/` and test subpackages
  such as `tests/ui_flows/` have room). Hold an oversized file such as
  `ui/ui.py` at net zero by moving a self-contained block you touch into a new
  module.
  `python3 tools/maintenance/function_metrics.py --output /tmp/pass18-<NN>-metrics.json <file> <functions...>`
  measures functions exactly as the hook does. Never set `SLOP_GATE_*` and
  never pass `--no-verify`. When the hook runs longer than the foreground
  command limit, run `git commit` in the background and wait for it.
- The memory bank startup files (`activeContext.md`, `progress.md`,
  `future-work-kanban.md`, `goal-priority-matrix.md`, `loop-queue.md`) are at
  their line budget, and `papercuts.md` has its own cap. Add no lines to them.
  Report papercuts and second-level findings in your final message; the
  orchestrator records them.
- Never commit `/Users/armantarkhanian/Code/ankiscape-pass18/native/owner-player-data.json`
  or any copy of the owner's save; it is his private game data, for local
  reproduction only.
- Never push, never change git config, never force-push or hard-reset, never
  amend except after a hook changed files following your own successful
  commit. Never read secrets (`~/.config/fleet-conductor/*`,
  `~/.config/sol-loop/*`, `~/.codex/auth.json`, `~/.codex/config.toml`, any
  `.env`). pkill and killall are banned; signal only processes you started.
- Do not spawn subagents. Do not run `tools/run_remote_tests.py` or
  `tools/promotion_gate.py`, launch Anki, or post mouse or keyboard input; the
  orchestrator owns the remote lanes, the gate and the native looks.
</build>

<finish>
1. Review your own diff on two axes before the final commit: against the spec
   and ticket (missing, extra, wrong), and against the contract and this
   repo's conventions. Fix what you find.
2. In the final commit, set your ticket's `**Status:**` line to `done`, or to
   `built; native look waits for the orchestrator` for a ticket whose
   acceptance names a native look, and tick the acceptance boxes that passed.
3. The commit message opens with the problem in plain language, then the
   solution; the subject says why the change matters.
4. Rebase your branch onto the current local `goal/pass18-integration` tip
   (one local repository; no fetch) so it lands as a fast-forward; rerun your
   focused tests if the rebase brought in changes to files you touched.
5. Leave the worktree in place; the orchestrator removes it after landing.
</finish>

<report>
Write your report to `/Users/armantarkhanian/Code/ankiscape-pass18/reports/<NN>.md`
as you finish, then return the same text, with these fields:
- `commit`: the final SHA on your branch, and the branch name.
- `worktree`: the absolute path.
- `tests`: each command you ran with its exact final lines (for example
  `Ran 412 tests in 31.2s` and `OK (skipped=3)`).
- `evidence`: the PNG and table paths, if any.
- `status`: what you set the ticket's Status line to.
- `papercuts`: one line each, or none.
- `second_level`: findings outside the ticket, or none.
- `deviations`: every place you departed from the spec or ticket, and why, or
  none.
</report>
