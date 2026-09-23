# Jev grill state (2026-09-22, paused for quota)

Source handoff: `memory-bank/handoffs/2026-09-22-jev-grill.md`. The grill paused at 19:55 PDT because the Claude 5-hour quota was at 1%. Nothing is built. The output is still a spec, written with `to-spec` after the last open question.

## Owner's goal (owner's words)

"I wanted to plug Jev into the process/SDLC for this project to make it faster/cheaper." The owner then chose less quota as the measure: "Jev is basically $1 max a day and even that is a stretch. Also I don't want to have to run a week long trial and forget it even is happening. I'd rather just get tangible effects from the getgo and calibrate from there."

The source handoff did not state this goal. The first three rounds used the handoff's frame (three named candidates) instead. Papercut commit `4fd97102` records that.

## Settled decisions

1. Jev runs only in the build pipeline. The spec states that the add-on never calls Jev.
2. Volume test: a candidate stays only if its volume makes calibration labels worth their cost, or if it sits inside a loop.
3. Jev never writes to a file. A Jev mistake must cost at most one rerun or one extra reasoning-model turn, never a lost finding or row.
4. Jev acts from the first day in that safe direction. No shadow trial. Calibration comes later from the logged decisions. (This replaces the earlier shadow-first rule and the shadow-to-sort promotion limit.)
5. Labels for later calibration: Opus 5.5 labels with the same state that Jev got. The owner checks 20 random rows blind. More than 3 disagreements in 20 rejects the labels.
6. Budget: at most $1 per day of Jev calls.
7. Scope: tools in this repo only. Harness ideas go to the fleet thread as copy-paste prompts. This repo does not change fleet files.
8. Removed candidates, with reasons:
   - Backlog triage. `memory-bank/gap-backlog.json` has 45 rows (24 `merged`, 0 `pending`), 15 distinct status strings, and no kanban-label field. `tools/gap_driver.py` starts only `pending` transcription rows and has not changed since 2026-07-09. The backlog is a historical record; the kanban board (57 cards, edited by hand) is the live list.
   - Review-finding survival. No record of rejected findings exists. Survival needs a probe against code, so it is an audit.
   - Citation drift. `tools/audit_citation_drift.py` ran once (2026-08-22): 1,432 citations; 980 `ok`, 169 `moved`, 136 `changed`, 94 `missing_file`, 34 `missing_lines`, 19 `unresolved`; 261 actionable. Jev could only sort the 305 `changed` plus `moved` rows, and the reasoning model still reads all of them, so no turns are saved.
   - Papercut classes. 2,297 entry lines, 668,095 characters (about 170K tokens) since 2026-08-05; 478, 473, 129, 114 new lines in ISO weeks 35 to 38. One Opus call per sweep classifies a week of lines with no calibration, so Jev saves almost nothing.
   - Game-value source check. Of 47 rows in `tools/sourced_xp_rates.py`, 13 store the quoted wiki text; 34 store only a reference.
   - Review-verdict screen. Reviews check code and sources, so they are audits.
   - From the fleet calibration: dispatch routing (52.6% correct seat) and claim-versus-command report screening (9 of 10 warnings false).

## Open question (Q16, owner has not answered)

The last in-repo candidate is a gate-failure screen: Jev reads a failed lane log; on "environment problem" the runner reruns that lane once and appends a papercut line. Keyword counts in `memory-bank/papercuts.md` since 2026-08-05: zsh "no matches found" 58 (agent shell error, no gate), Accessibility/AX errors 33 (native-run agent, not the runner), tool output limit 21 (harness), timeouts that name a gate/lane/suite/remote run 22, exit 137 plus Qt modal hang plus mirror lock 20, network reset 3 (already retried by `tools/run_remote_tests.py`). Counts overlap. At most about 42 orchestrator turns in 7 weeks, about 6 per week.

- (a) Recommended: the spec records that this repo has no Jev build now, with the candidates, reasons, and numbers above, and gives the fleet thread a prompt about harness-level quota (orchestrator turns spent on small judgments), where the volume is.
- (b) Build the gate screen anyway, with a papercut line for each rerun.

## Follow-ups for the spec (owner approved both)

Both belong to fleet files, so the spec carries them as copy-paste prompts for the fleet thread:

1. The global papercut rule says to propose a fix at "~25 unaddressed papercuts", but `papercuts.md` has no mark for a fixed line, so no agent can count them. Possible data-structure fix: each fix moves its lines to a separate fixed file (this repo already has `memory-bank/papercuts-fixed-2026-08-11.md`), so the unaddressed count is the line count.
2. The staleness sweep in `~/fleet/skills/universal/cline-rules` checks the core files only (the 2026-09-13 sweep used four claim checkers over six core files). Add one line: run `tools/audit_citation_drift.py` first and fix its actionable rows in the same sweep. The tool covers all 552 memory-bank files and has not run since 2026-08-22.

Third follow-up (in this repo, a one-line note in the spec): mark `memory-bank/gap-backlog.json` as a closed historical record.

## Facts for the spec

- Fleet client: `~/fleet/config/claude/hooks/typesafe_client.py`, one public function `ask(caller, session_id, state, questions)`, standard library only, 5 s timeout, 3 attempts. Load it by path; do not copy it. Key file `~/.local/state/typesafe/client.env`; never print it. Other clients need their own `User-Agent` (Cloudflare 1010).
- TypeSafe citation-check cookbook: state `{"claim", "section"}`, Choice supports / contradicts / says nothing; its 0.8 line comes from 8 test citations only.
- Choice accepts up to 255 options. Many questions in one call run in parallel.

## Next steps

1. Get the owner's answer to Q16.
2. Write the spec with `to-spec` in `memory-bank/specs/`.
