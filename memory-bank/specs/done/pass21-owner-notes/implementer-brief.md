# Pass 21 implementer brief

Every Pass 21 implementer reads this file, then its ticket. The orchestrator seat dispatches the tickets, lands them on the integration branch, and runs the full test lanes, the native checks, the final review and the promotion gate.

<context>
- Spec: `memory-bank/specs/pass21-owner-notes/spec.md`. Every decision there is settled by the owner. His answers, word for word, are in `grill.md`, and they are the approval for exactly the changes the spec names, including changes to existing screens. Do not relitigate a decision, and do not change a screen the spec does not name.
- Ticket: `memory-bank/specs/pass21-owner-notes/tickets/<NN>-*.md`.
- Code facts with citations (lines can have moved): `facts.md`. Read the section for your ticket before you open code.
- Binding rules: `memory-bank/codex-briefs/STANDING-SLICE-CONTRACT.md`, read in full, and the repository `AGENTS.md`. This brief replaces the contract's section 6 lane commands and its `--expected-tests` collection: implementers run the focused tests under <build>, and the orchestrator runs the full plain and offscreen Qt lanes. The rest of section 6 still binds you. Where this brief and the contract disagree in any other way, stop and report.
</context>

<worktree>
1. From the canonical checkout `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork`, run `python3 tools/worktree_guard.py audit`, then `python3 tools/worktree_guard.py add goal/pass21-<NN> --name pass21-<NN> --start-point goal/pass21-integration`.
2. Work only in the new worktree. Never edit, stage or test inside the canonical checkout, which Anki loads as the live add-on, the `pass20-integration` worktree, another ticket's worktree or any pool worktree.
3. Run `python3 tools/worktree_guard.py audit` again after the add.
</worktree>

<build>
- Build the ticket by steps 2 and 3 of `~/fleet/skills/universal/implement/SKILL.md`, read as a file.
- Build the ticket's end-to-end behavior and nothing else. Problems directly adjacent to your change are yours; anything found only because of those fixes goes in your report, not your diff.
- Test at the seams the spec's Testing Decisions name, and only there. Drive the real review handler or the real widget; never stub the system under test.
- Tests run from your worktree with `python3 run_tests.py <selectors>`. Run your focused tests and the test packages next to your change. Do not run the whole suite; the orchestrator runs it. A failure that also fails on `goal/pass21-integration` is known, and you report it. Any other failure is yours.
- A ticket that adds or removes a player action moves the item-reachability census: run `python3 run_tests.py test_report_baseline` and `python3 tools/audit_item_reachability.py --check`, and update the pins for exactly your change.
- Use `~/fleet/skills/universal/implement/scripts/job.py` for any shell job longer than a few minutes; `--help` defines its operations. Declare named outputs at start, keep the same handle for status, bounded waits and cancellation, and read final evidence from a `succeeded` record's `outputs`.
- A ticket that changes what the player sees: build the main menu or the review HUD offscreen at the default size and 560 points tall after `show()`, `resize()` and several `processEvents()` passes, check `text_fit_defects`, and save PNGs, dark (Fusion dark palette) and light, under `/Users/ArmanTarkhanian1/Documents/ankiscape-pass21/evidence/<NN>/`. Add one line to `memory-bank/play-checklist.md` that names the exact screen, hover and setting. Capture scripts stay in the evidence folder; never commit them.
- Menu text is elegant and minimal, and American English. Qt text colors follow the `AGENTS.md` dark-mode rule.
- The commit hook refuses: growth of any code or test file already above 1000 lines, a touched function above cyclomatic or cognitive complexity 15 or Halstead difficulty 80, an import fan-out increase, and a new code file in a directory that already holds 40. On 2026-11-04, `logic/`, `logic_pure/`, `data/`, `tools/`, `tests/`, `tests/ui_flows/` and `core/` were full, `ui/` had one place left, and `runtime/`, `tests/action_queue/`, `tests/main_menu/`, `tests/quests/`, `tests/pace/`, `logic_pure/quest/` and `logic/pace/` had room; count with `ls <dir>/*.py | wc -l` before you add a file. Hold an oversized file such as `ui/ui.py` at net zero by moving a self-contained block you touch into a new module. `python3 tools/maintenance/function_metrics.py --output /tmp/pass21-<NN>-metrics.json <file> <functions...>` measures functions as the hook does. Never set `SLOP_GATE_*` and never pass `--no-verify`. When the hook runs longer than the foreground command limit, run `git commit` in the background and wait for it.
- Add no lines to the memory bank startup files (`activeContext.md`, `progress.md`, `future-work-kanban.md`, `goal-priority-matrix.md`) or `papercuts.md`. Report papercuts and second-level findings in your final message.
- Never open an Anki profile database (`collection.anki2`, `prefs21.db`) or read or copy the owner's save. Never launch Anki or post mouse or keyboard input.
- Never push, never change git config, never force-push or hard-reset, never amend except after a hook changed files following your own successful commit. Never read secrets (`~/.config/fleet-conductor/*`, `~/.config/sol-loop/*`, `~/.codex/auth.json`, `~/.codex/config.toml`, any `.env`). `pkill` and `killall` are banned; signal only processes you started.
- Do not spawn subagents. Do not run `tools/run_remote_tests.py` or `tools/promotion_gate.py`; the orchestrator owns them. No quota percentage stops you; the orchestrator owns the budget.
- Commit as you go with `git commit -- <paths>`, because your worktree is the record, and commit before you report.
</build>

<finish>
1. Review your own diff against the spec and ticket (missing, extra, wrong) and against the contract and this repo's conventions. Fix what you find.
2. In the final commit, set the ticket's `**Status:**` line to `done`, or to `built; <the check> waits for the orchestrator` when the acceptance needs a native look, and tick the acceptance boxes that passed. An unticked box needs a reason in your report.
3. The commit message opens with the problem in plain language, then the solution, and the subject says why the change matters. End it with `Co-Authored-By: <your model> <noreply@openai.com>` or the Anthropic form that fits you.
4. Rebase your branch onto the current local `goal/pass21-integration` tip so it lands as a fast-forward; rerun your focused tests if the rebase brought changes to files you touched. Do not move the integration branch.
5. Leave the worktree in place; the orchestrator removes it after landing.
</finish>

<report>
Write your report to `/Users/ArmanTarkhanian1/Documents/ankiscape-pass21/reports/<NN>.md` as you finish, then return the same text, with these fields:
- `commit`: the final SHA on your branch, and the branch name.
- `worktree`: the absolute path.
- `tests`: each command you ran with its exact final lines.
- `evidence`: PNG and table paths, if any.
- `status`: what you set the ticket's Status line to.
- `papercuts`: one line each, or none.
- `second_level`: findings outside the ticket, or none.
- `deviations`: every place you departed from the spec or ticket, and why, or none.
</report>
