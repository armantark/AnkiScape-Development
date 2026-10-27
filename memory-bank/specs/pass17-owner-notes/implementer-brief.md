# Pass 17 implementer brief

Every Pass 17 implementer reads this file, then its ticket. The orchestrator
seat (Opus 5.5, T3 thread 9e1bb552) dispatches the tickets, lands them on the
integration branch, runs the hill-climb probes and votes, the final review,
the Codex native check and the promotion gate.

<context>
- Spec: `memory-bank/specs/pass17-owner-notes/spec.md`. Every decision there is
  settled by the owner (answers quoted in `grill-decisions.md`); do not
  relitigate it.
- Your ticket: `memory-bank/specs/pass17-owner-notes/tickets/<NN>-*.md`.
- Code facts with citations (taken at main `2e885047f`; lines may have
  moved): `memory-bank/specs/pass17-owner-notes/code-facts.md`. Read the
  section for your ticket's area before you open code.
- Binding rules: `memory-bank/codex-briefs/STANDING-SLICE-CONTRACT.md`, read in
  full, and the repository `AGENTS.md` (Qt dark-mode text colors, offscreen
  screenshot rules). Where this brief and the contract disagree, stop and
  report.
</context>

<worktree>
1. From the canonical checkout `/Users/armantarkhanian/Code/AnkiScape`, run
   `python3 tools/worktree_guard.py audit`, then
   `python3 tools/worktree_guard.py add goal/pass17-<NN>-<slug> --name pass17-<NN> --start-point goal/pass17-integration`.
   The pooled lease is full while the paused Sol loops hold all 16 slots;
   `add` is the guarded route.
2. Work only in the new worktree under
   `/Users/armantarkhanian/ankiscape_worktrees/`. Never edit, stage or test
   inside the canonical checkout, the `pass17-integration` worktree, or the
   `papercuts-2026-10-27` worktree, which another agent owns.
3. Run `python3 tools/worktree_guard.py audit` again after the add.
</worktree>

<build>
- Build the ticket's end-to-end behavior and nothing else. Problems directly
  adjacent to your change are yours; anything found only because of those
  fixes goes in your report, not your diff.
- Test at the seams and layers the spec's Testing Decisions name, and only
  there. Drive the real review handler or the real widget; never stub the
  system under test.
- Focused tests, run from your worktree, one lane after the other:
  `python3 run_tests.py <selectors>` (plain) and
  `QT_QPA_PLATFORM=offscreen /Users/armantarkhanian/Code/AnkiScape/.venv-qt/bin/python -m unittest <modules>` (Qt).
- Before your final ticket commit, run the full plain lane once:
  `python3 run_tests.py`, in the background with a two-hour timeout, because
  parallel implementers share the machine and one lane took over 30 minutes
  on 2026-10-27. Hill-climb round commits need only your focused tests.
  The promotion gate runs the full offscreen Qt lane later; you run the Qt
  tests your change touches. Homebrew `python3` has no Pillow on this
  MacBook, so tests that import it can fail on the base too; a failure that
  also fails on `goal/pass17-integration` is known, and you report it. Any
  other failure is yours.
- A ticket that changes what the player sees: build the main menu or the
  reviewer strip offscreen at 560 points tall after `show()`, `resize()` and
  several `processEvents()` passes, check `text_fit_defects`, and save before
  and after PNGs, dark (Fusion dark palette) and light, under
  `/Users/armantarkhanian/Code/ankiscape-pass17/evidence/<NN>/`. Add one line
  to `memory-bank/play-checklist.md` that names the exact screen, hover and
  setting. Capture scripts stay in the evidence folder; never commit them.
- slop-gate (the commit hook) refuses: growth of any code or test file already
  above 1000 lines, a touched function above cyclomatic or cognitive
  complexity 15 or Halstead difficulty 80, and a new code file in a directory
  that already holds 40 (`logic/`, `logic_pure/`, `data/`, `tools/` and
  `tests/` are full; `ui/`, `core/` and test subpackages such as
  `tests/ui_flows/` have room). Hold an oversized file at net zero by moving a
  self-contained block you touch into a new module.
  `python3 tools/maintenance/function_metrics.py --output /tmp/pass17-<NN>-metrics.json <file> <functions...>`
  measures functions exactly as the hook does. Never set `SLOP_GATE_*` and
  never pass `--no-verify`. When the hook runs longer than the foreground
  command limit, run `git commit` in the background and wait for it.
- The memory bank startup files (`activeContext.md`, `progress.md`,
  `future-work-kanban.md`, `goal-priority-matrix.md`, `loop-queue.md`,
  `papercuts.md`) hold 2,999 of their 3,000-line budget. Add no lines to them.
  Report papercuts and second-level findings in your final message; the
  orchestrator records them.
- Never push, never change git config, never force-push or hard-reset, never
  amend except after a hook changed files following your own successful
  commit. Never read secrets (`~/.config/fleet-conductor/*`,
  `~/.config/sol-loop/*`, `~/.codex/auth.json`, any `.env`). pkill and killall
  are banned.
- Do not spawn subagents. Do not run `tools/run_remote_tests.py` or
  `tools/promotion_gate.py`, launch Anki, or post mouse or keyboard input; the
  orchestrator owns the gate and the native check.
</build>

<hill-climb>
Tickets 02, 04 and 07 rebuild a screen through the loop in the spec's "The
hill-climb loop" section. You are the maker; you never judge your own
candidate.
1. Build a candidate. Capture its screenshots (560 points tall, dark and
   light) under `/Users/armantarkhanian/Code/ankiscape-pass17/evidence/<NN>/round-<R>/`
   with a `candidate.md` that says in plain words what changed since the last
   round and why.
2. Commit the candidate on your branch, then return a report with
   `hill_climb: round <R> ready` and the round folder. Stop there.
3. The orchestrator gives the screenshots and the ticket's task list to a
   fresh naive model and to a taste reviewer of another lineage, then resumes
   you with their results. Keep the candidate or revert to the best earlier
   round, build the next round from the findings, and repeat.
4. When the orchestrator reports a pass, or after round 5, finish the ticket
   with the best candidate as below.
</hill-climb>

<finish>
1. Review your own diff on two axes before the final commit: against the spec
   and ticket (missing, extra, wrong), and against the contract and this
   repo's conventions. Fix what you find.
2. In the final commit, set your ticket's `**Status:**` line to `done`, and
   tick its acceptance boxes that passed.
3. The commit message opens with the problem in plain language, then the
   solution; the subject says why the change matters.
4. Rebase your branch onto the current local `goal/pass17-integration` tip
   (one local repository; no fetch) so it lands as a fast-forward; rerun your
   focused tests if the rebase brought in changes to files you touched.
5. Leave the worktree in place; the orchestrator removes it after landing.
</finish>

<report>
Return plain text with these fields:
- `commit`: the final SHA on your branch, and the branch name.
- `worktree`: the absolute path.
- `tests`: each command you ran with its exact final lines (for example
  `Ran 412 tests in 31.2s` and `OK (skipped=3)`).
- `evidence`: the PNG paths, if any.
- `status`: what you set the ticket's Status line to, or `hill_climb: round <R> ready`.
- `papercuts`: one line each, or none.
- `second_level`: findings outside the ticket, or none.
- `deviations`: every place you departed from the spec or ticket, and why, or
  none.
</report>
