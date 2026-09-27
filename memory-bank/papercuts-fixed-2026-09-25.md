# Papercuts fixed — 2026-09-25

These lines were moved verbatim from `memory-bank/papercuts.md` at main `d0904603`. A per-line triage on 2026-09-25 gave each line a disposition with evidence checked against main, and a grouping pass merged the lines into cause classes. Each heading is a merged class; the line below it gives the disposition and the evidence. Open-defect and paused-feature lines stay in `papercuts.md`.

## Test discovery gives tests the wrong names — 1 occurrence

Disposition: fixed before this triage (`fixed-before`). Evidence: `4b5e4485` moved `tests/ui/` to `tests/ui_flows/` with an `__init__.py`, and main tracks no file under `tests/ui/`. The root cause (discovery with `tests/` as the import root) stays open with lines 48, 50 and 64 in `papercuts.md`.

- 2026-09-24T03:19:40-0700 — UI test discovery slice: adding an empty `tests/ui/__init__.py` did not make the tests run; both lanes discovered `unittest.loader._FailedTest.ui.test_activity_one_click` (and the other two) with `ModuleNotFoundError: No module named 'ui.test_encounter_transitions'`, because discovery imports test subpackages as top-level names and the product `ui/` package at the repo root already owns `ui`; a test subpackage must not share a name with a root package.

## A short selector also picks up sibling modules — 1 occurrence

Disposition: operator error (`operator-error`). Evidence: `run_tests.py:81-84` documents selectors as case-insensitive fragments, and `--list` (`run_tests.py:86-89`) previews matches. The selector design itself stays open with line 60 in `papercuts.md`.

- 2026-09-24T04:08:35-0700 — Diary counter-key check, focused run: `run_tests.py` selectors are case-insensitive substrings of the test id, so the bare module name `test_achievement_diaries` also selects `test_achievement_diaries_integration` and the Qt-only `test_achievement_diaries_ui` (16 tests), which the no-skip remote plain run would refuse; the selector needs the trailing dot, `test_achievement_diaries.`.

## Remote focused runs are only checked on the remote host, after the lock wait — 6 occurrences

Disposition: operator error (`operator-error`). Evidence: `tools/run_remote_tests.py:422-423` rejects `--select` without `--expected-tests` on purpose (`0e543a4d`, 2026-09-19), and `memory-bank/techContext.md:50-53` documents the paired form; `tests/test_remote_test_host.py:22-25` pins the refusal. The late selector check stays open with line 43 in `papercuts.md`.

- 2026-09-23T19:33:26-07:00 — Commit-stage remote selection first exited 2 with `run_remote_tests.py: error: --select and --expected-tests must be supplied together`; include the measured test count for every selected run.
- 2026-09-23T19:04:45-07:00 — A selected remote documentation-test run exited 2 with `run_remote_tests.py: error: --select and --expected-tests must be supplied together`; count selected tests before invoking the runner.
- 2026-09-23T17:22:10-0700 Running the focused remote plain lane: the dispatch omitted its required --expected-tests companion for --select; argparse stopped with '--select and --expected-tests must be supplied together'.
- 2026-09-23T19:49:30-0700 Reachability-exit slice: the dispatched runner command `/opt/homebrew/bin/python3 tools/run_remote_tests.py "$PWD" plain --select <selector>` stopped with exact `run_remote_tests.py: error: --select and --expected-tests must be supplied together`; count the selected tests with `unittest.defaultTestLoader.loadTestsFromName(...).countTestCases()` and pass `--expected-tests`.
- 2026-09-23T21:08:31-0700 Reachability-exit second review fix: the review dispatch again prescribed `run_remote_tests.py "$PWD" plain --select <selector>` without `--expected-tests`, and it stopped again with exact `run_remote_tests.py: error: --select and --expected-tests must be supplied together`; the orchestrator brief template should carry `--expected-tests N`.
- 2026-09-23T19:42:28-07:00 — The slice brief gave `run_remote_tests.py "$PWD" plain --select <selector>` without a count; the runner refused with `run_remote_tests.py: error: --select and --expected-tests must be supplied together`. Adding `--expected-tests 33` (19 native guard tests plus 14 worktree guard tests, counted with `unittest` loader) let the focused run start.

## An orphaned remote lane makes the next run fail at once — 1 occurrence

Disposition: design decision (`design-decision`). Evidence: `ef6f3801` (2026-09-05) added the fail-closed pending-run check at `tools/run_remote_tests.py:185-192` so no sync changes the mirror before the worker finishes. The fail-at-once behavior stays open with lines 51, 63 and 67 in `papercuts.md`.

- 2026-09-23T23:13:43-0700 — Diary-generator review-fix rerun: focused MacBook plain lane waited on the mirror lock, then exited 1 with `error: previous remote lane has no completion report; sync blocked; pending record: /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.pending.json; run: plain-1790230291-55e1095b` (another slice's run); reran the runner as its message directs.

## Papercut lines have no fixed format and moves are done by hand — 1 occurrence

Disposition: operator error (`operator-error`). Evidence: the agent's own split script dropped a line, and the sorted no-loss diff caught it before the report (the proof paragraph of "2026-09-23 — Papercut follow-up: today's 56 new lines classified", `memory-bank/progress.md:977`). The missing format and move tool stay open with line 46 in `papercuts.md`.

- 2026-09-23T21:44:09-07:00 — Papercut follow-up second review: a scripted section split dropped the 18:27:13 broken-links line from its template; the sorted no-loss `diff` caught it (89 vs 90 lines) and the line was restored before reporting.

## Codex CLI `review --uncommitted` drift in a global skill — 4 occurrences

Disposition: external blocker (`external-blocker`). Evidence: the Codex CLI refuses `--uncommitted` with a prompt (`the argument '--uncommitted' cannot be used with '[PROMPT]'`) while its help still lists both; the stale command is in `/Users/ArmanTarkhanian1/.claude/skills/codex-review/SKILL.md:38`, outside this repository.

- 2026-08-24 14:08 PDT — The codex-review skill's documented `review --uncommitted - < prompt` shape failed with `error: the argument '--uncommitted' cannot be used with '[PROMPT]'`; the bundled CLI now expects the review prompt as a positional string rather than `-`.
- 2026-08-25 07:55 PDT — The codex-review skill's positional-prompt form `/Applications/ChatGPT.app/Contents/Resources/codex review --uncommitted "$PROMPT"` failed with `error: the argument '--uncommitted' cannot be used with '[PROMPT]'` even though `--help` prints `codex review --uncommitted [PROMPT]`; inspect the installed CLI syntax before retrying.
- 2026-08-25 10:06 PDT — The codex-review skill's `review --uncommitted - < prompt` command is stale for the bundled Codex CLI, which rejected it with `the argument '--uncommitted' cannot be used with '[PROMPT]'`; pass the prompt as the single positional argument instead.
- 2026-08-27 03:40 PDT: The checked-in `codex-review` skill's documented `codex review --uncommitted - < prompt` command exited 2 with `the argument '--uncommitted' cannot be used with '[PROMPT]'`; the installed Codex CLI no longer accepts the skill's stdin `-` prompt shape for an uncommitted review.

## Stop hook replaces the subagent's final text — 2 occurrences

Disposition: external blocker (`external-blocker`). Evidence: the only Stop hook is in the global `/Users/ArmanTarkhanian1/.claude/settings.json:131`; the repository's `.claude/settings.local.json` holds permissions only.

- 2026-09-19T17:03:45+00:00: Claude text output after a stop-hook follow-up contained only the hook correction, omitting the preceding substantive review. Root recovered the assistant review from session 7b5b10d2-4372-4399-9b28-bddcc10b5030.jsonl and resolved its alias findings. The complete review text is retained, not inferred from the final correction.
- 2026-09-21T18:30:39-07:00 Opus review stdout retained only a later stop-hook response (`The review above is complete.`), losing the actual findings from the returned text; recovered the original findings from session `17c55674-58cf-4144-b7bd-f1b5c4b4d328` into out-of-tree `opus-review-complete.txt`, without rerunning the review.

## Docs audit rejected nested module selectors — 2 occurrences

Disposition: fixed before this triage (`fixed-before`). Evidence: `fc14c8f9` (2026-09-23) adds `selectors.add(module)` at `tools/audit_docs.py:132`, with a regression case in `tests/test_docs_audit.py`.

- 2026-09-19T17:03:45+00:00: Full source gate 8898f8780213c265b693a28b992ee8fbc903e938 passed both lanes but failed audit_docs (exit 1): guard-review.md:22: dangling_test_selector: tests.promotion.test_worktree_release. The documentation matcher treats a nested module selector as a method reference. Preserved the exact report as guard-review.md.gz and used the equivalent file-path selector in readable reproduction guidance. No gate receipt was issued.
2026-09-21T19:19:42-07:00: Full native-repair gate passed both suites but audit_docs rejected `native-relaunch-summary.md:6: dangling_test_selector: tests.native.test_session_bootstrap`; the valid nested-module command matched the selector scanner. Re-ran and documented unittest file paths; no validator change.

## zsh expansion rules (no word-splitting, nomatch, `=`) — 6 occurrences

Disposition: operator error (`operator-error`). Evidence: zsh leaves unquoted parameters unsplit (SH_WORD_SPLIT off), aborts on an unmatched glob (NOMATCH) and expands a leading `=` (EQUALS), all documented defaults; `tools/run_remote_tests.py:408-409` documents one `--select` per selector.

- 2026-09-23T21:18:56-07:00 — Papercut follow-up: an optional `ls memory-bank/evidence/*.md` glob aborted with `(eval):1: no matches found: memory-bank/evidence/*.md` because the summaries sit one directory deeper; use `find -name SUMMARY.md` for optional globs.
- 2026-09-23T23:37:31-0700 — Qt-lane speed slice: a zsh loop passed `$s` holding several selectors as one argument (zsh does not word-split unquoted parameters), so `run_tests.py --list` matched nothing and printed 2 lines instead of the count.
- 2026-09-24T01:20:23-0700 — Qt-lane speed review fix: the same zsh word-splitting trap again, an unquoted `$SEL` reached `tools/run_remote_tests.py` as one merged `--select` argument (exit 2, `unrecognized arguments`), and the out-of-tree measure harness reported `ran=0` with exit 0; build selector lists as bash arrays.
- 2026-09-23T21:27:53-0700 — Diary-generator metrics: `lizard --csv $FILES` with `FILES="a.py b.py"` in zsh passed one space-joined path (zsh does not word-split unquoted variables), and lizard exited quietly with an empty CSV; pass analyzer paths as separate arguments.
- 2026-09-24T03:41:24-0700 — Diary-generator cleanup, metric baseline: in zsh, `F="a.py b.py c.py"; lizard $F` passes one path with spaces, so lizard printed `0 file analyzed.` and complexipy printed `Please check file/folder exists or check syntax` instead of refusing; a bash array (`FILES=(...); lizard "${FILES[@]}"`) measured correctly.
- 2026-09-24T06:05:41-0700 — Ledger slice: `echo ===` between commands in a zsh one-liner failed with '(eval):1: == not found' because zsh expands a leading '=' word as a command path; use a quoted separator such as `echo "---"`.

## Slop-gate size limits — 3 occurrences

Disposition: design decision (`design-decision`). Evidence: owner ruling §34 in `memory-bank/handoffs/design-to-impl-rulings-2026-08-13.md:2363-2370` makes the slop gate a fixed instrument; `/Users/ArmanTarkhanian1/fleet/config/git/hooks/slop_gate.py:64` sets `FILE_LINES_MAX` to 1000.

- 2026-09-24T01:21:39-0700 — First commit attempt of the gate lock-wait slice was refused by slop-gate: `tools/promotion/lane_execution.py: _run_gate_checks 30 (was 15)` cognitive complexity and `tests/test_promotion_gate.py: 1026 lines (was 935)`; the review had not run the slop gate, so the loop moved to `_run_check_sequence` and the timing tests to `tests/promotion/test_remote_mirror_lock.py`, then the focused MacBook run was repeated.
- 2026-09-24T01:52:04-0700 — Qt-lane speed commit: the global slop gate refused the first commit with `tests/test_item_reachability_audit.py: 1905 lines (was 1904)`, `tests/test_main_menu_widget.py: 19893 lines (was 19883)` and `tests: 237 code files (was 236)`, a check the review stage never ran; moved the shared report into tests/reachability/ and rewrote both edits so neither file grows.
- 2026-09-24T05:02:07-0700 — Diary counter-key check, commit: the slop-gate pre-commit hook refused `tests/test_achievement_diary_ledger_wiring.py: 1068 lines (was 1054)` because a code file above 1000 lines may not grow, so the new generator test moved to `tests/achievement_diaries/test_condition_keys.py` after review; check a test file's length before adding to it.

## Throwaway probes built on a wrong assumption — 9 occurrences

Disposition: operator error (`operator-error`). Evidence: each failure was in an agent's one-off probe, not repository code: currency is modeled apart from item rows, `ITEM_DEFINITIONS` is a tuple (assigned from `apply_item_asset_overrides` at `core/constants.py:499`, whose return type is `Tuple[ItemDefinition, ...]` at `core/item_registry.py:317`), `data.item_registry` never existed, the reachability audit already builds the real seed set (`tools/audit_item_reachability.py:709-882`), tools find their root from their own path, and Python salts string hashes per process.

- 2026-08-24 08:47:43 PDT — A reward-definition probe treated `Coins` like an ordinary `ITEM_DEFINITIONS` row, but currency is modeled separately; limit undefined-key proof to the two affected empty penguin quest reward lists.
- 2026-08-25 10:04 PDT — Direct `_claim_item_sources()` testing passed an empty maximum-level map, so its default Runecrafting level 1 gate rejected even a claim with `required_runecrafting_level=0`; supply the audit's real minimum level context in unit probes.
- 2026-08-26 07:38 PDT — The base-registry comparison extracted the `_apply_equipment_metadata(...)` argument with its closing call parenthesis and `eval` failed with `SyntaxError: unmatched ')'`; strip the wrapper's final `)` before evaluating the dict expression.
- 2026-08-26 22:18 PDT — The Ritual counterfactual reused the all-registered-items action-completeness probe and failed with `StopIteration` because that model makes `Catspeak amulet (e)` available; use the audit closure’s real reachable seed set when diagnosing post-stub item blockers.
- 2026-08-26 22:05 PDT — While enumerating canonical item families, I assumed `ITEM_DEFINITIONS` was keyed by item name; it is a tuple of `ItemDefinition` records, so one-off registry probes must use `.storage_key`.
- 2026-08-26 22:53 PDT — A quest-stage registry probe assumed `data.item_registry`, but the final `ITEM_DEFINITIONS` registry is exported from `core.constants`; locate the owning module before importing audit data.
- 2026-08-26 23:35 PDT — Executing the committed quest module in an isolated `ModuleType` failed because Python 3.14 dataclasses look up `cls.__module__` in `sys.modules`; baseline probes must register the temporary module before `exec`.
- 2026-09-23T21:27:41-0700 — Old-vs-new equivalence probe: a `git show HEAD:tools/generate_achievement_diary_data.py` copy loaded from `/tmp/diary-old/` derived `ROOT` from its own `__file__`, scanned `/tmp` for ledger write sites, and reported 14 false `resolve_condition_key` mismatches (`mining:shooting_stars`, `woodcutting:evil_tree_fell`, `dungeoneering:*`) until the probe set `old.ROOT` to the worktree.
- 2026-09-24T03:46:12-0700 — Roster-test mutation proof: comparing HEAD's and the worktree's assertion messages showed two false differences, `'legs' not found in {'feet', 'head', 'shield', 'neck'}` versus the same set in another order, because a set literal's display order follows the `.pyc` compiled under a different hash seed; compiling both copies fresh in one process (`PYTHONPYCACHEPREFIX=<tmp>`) made all 18 messages identical.

## Tests written from a guessed expectation — 2 occurrences

Disposition: operator error (`operator-error`). Evidence: `logic_pure/logic_pure_quest.py:731` emits `Needs {item} x{amount}` and `tests/test_logic.py:8568` now pins it; `core/constants_parts/skill_assets.py:207-208` merges Big Chinchompa into the Hunter aggregate openly, and `tests/test_skill_and_item_registry.py:2391` tests the owning manifest.

- 2026-08-22 17:10 PDT — The Black Knights kernel regression expected `Needs Cabbage`, but consumed-inventory blockers retain the explicit unit as `Needs Cabbage x1`; copy exact blocker text from the kernel when pinning stage gates.
- 2026-08-25 10:04 PDT — The first focused regression compared against `HUNTER_EXTRA_ITEM_DATA`, but that aggregate also contains seven Big Chinchompa rows and failed with them as unexpected; test `hunter_extra_items_as_dict()` for the owning manifest, then verify those rows in the final registry.

## Raw SSH work on the MacBook outside the runner — 3 occurrences

Disposition: external blocker (`external-blocker`) for lines 52 and 55, operator error (`operator-error`) for line 56. Evidence: the runner's rsync touches only the mirror (`tools/run_remote_tests.py:200-213`) and uses no GNU `timeout`; `memory-bank/techContext.md:32-34` and `memory-bank/remote-test-host.md:56-62` route MacBook work through `tools/run_remote_tests.py` and its flock.

- 2026-09-24T00:21:36-0700 — Private MacBook scratch copies /Users/armantarkhanian/ankiscape-remote-test-host/qt-speed-scratch and qt-speed-profile vanished between 23:50 and 00:21 while idle, so a test-id comparison silently ran in the wrong directory after `cd` failed; re-synced and repeated it.
- 2026-09-23T22:08:02-0700 — Qt-lane speed slice: `timeout` is not on the MacBook test host PATH, so a guarded SSH profiling command failed with `zsh:1: command not found: timeout`.
- 2026-09-23T23:33:41-0700 — Qt-lane speed slice: early profiling runs over SSH in `/Users/armantarkhanian/ankiscape-remote-test-host/qt-speed-profile` used the MacBook CPU outside the mirror lock and pushed promotion-gate lanes past their fixed limits twice; every MacBook measurement must go through `tools/run_remote_tests.py`.

## 600 s tool cap against long remote waits — 2 occurrences

Disposition: operator error (`operator-error`) for line 26, design decision (`design-decision`) for line 65. Evidence: `memory-bank/codex-briefs/STANDING-SLICE-CONTRACT.md:140-143` says the full Qt lane sits above the tool cap and to run it detached; `tools/run_remote_tests.py:5` and `:383-394` make the mirror-lock wait untimed on purpose.

- 2026-08-27 07:38 PDT — The full offscreen Qt lane was first launched as a harness-owned background command capped at 600000 ms even though the standing contract records a 600-760 second runtime; stop it before restart and use detached `nohup` for the uncapped run.
- 2026-09-23T22:43:07-0700 — Diary-generator review rerun: focused MacBook plain lane sat behind `Remote mirror busy; waiting for /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock` for over 10 minutes while two other slices' runners (started 22:11 and 22:22, pending run `plain-1790227311-e697fe2c`) held the mirror; a 600-second Bash wait timed out and was moved to the background.

## Computer use cannot drive the native Anki app — 2 occurrences

Disposition: external blocker (`external-blocker`). Evidence: `memory-bank/design-thread-queue.md:1101-1116` (§3.38) records that shell `screencapture -x` works while computer-use capture and input fail. The owner has not yet chosen a native-acceptance route from the three options in §3.38 (`memory-bank/design-thread-queue.md:1124-1127`).

- 2026-09-24T03:03-07:00 — Third native check of 0f67a3f6 stopped with 'Screenshot unavailable for /var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/ankiscape-native-kcvlz7a2/AnkiScape Native Test.app.' with the screen free, no Darkan client and load 8.44 (guard verify exit 0, unchanged:true); ssh 'screencapture -x /tmp/sshcap-test.png' exited 0 (4036277 bytes), so only the computer-use per-app capture of the copied test app fails.
- 2026-09-24T03:17-07:00 — Fourth native check of 0f67a3f6, observing through shell screencapture, proved the loaded paths in the disposable base but reviewed 0 cards: computer-use input failed with 'cannotClickOffscreenElement', 'noWindowsAvailable', timeouts and delayed actions. The SSH Codex CLI route cannot drive the copied app; owner decision in design-thread-queue.md §3.38.

## git read a commit hash after `--` as a path — 1 occurrence

Disposition: operator error (`operator-error`). Evidence: `git log [<options>] [<revision-range>] [[--] <path>...]`; everything after `--` is a path.

- 2026-08-22 23:01 PDT — While inspecting prior quest emitter commits, `git show -- <paths> <commit>` treated the commit as a path and returned no diff; put the commit before `--`.

## Widget tests fail only in the Qt lane — 1 occurrence

Disposition: design decision (`design-decision`). Evidence: `tools/promotion/landing.py:35` refuses to land without the Qt lane (`714fea03`, 2026-08-22).

- 2026-08-23 05:34 PDT — A quest repair silently invalidated a widget test that used that quest as its example, and only the Qt lane could see it; this was the second such failure tonight.

## Immutability gates replay whole suites, so one stale test fails every gate — 1 occurrence

Disposition: design decision (`design-decision`). Evidence: `tests/immutability_gate.py:91-124` replays the module suites on purpose; the stale Sheep Herder test was fixed in `88d65f83`.

- 2026-08-23 15:13 PDT — The full plain lane replayed one stale Sheep Herder runtime blocker expectation through nine immutability gates, so two direct stale tests appeared as 11 failures; fix the direct expectations before interpreting the gate fan-out.

## EnterWorktree refuses to enter an existing worktree from the repository root — 1 occurrence

Disposition: external blocker (`external-blocker`). Evidence: Claude Code's EnterWorktree tool; this repository creates worktrees through `tools/worktree_guard.py`.

- 2026-08-24 14:08 PDT — `EnterWorktree` refused an existing guarded worktree from the canonical repository root with `Cannot enter worktree: the current working directory ... is the repository root, not an isolated worktree`, so cwd-sensitive review skills cannot be safely aimed at a manually guarded worktree from this session.

## The quest schema could not express worn equipment — 1 occurrence

Disposition: fixed before this triage (`fixed-before`). Evidence: `2e12b506` removed the single-token gates (`data/quest/stage_cleanups.py:60`, `:558`, `:732`) and added the rule to report a missing worn-state predicate.

- 2026-08-27 00:53 PDT — Pinned source review found surviving loadout gates were still malformed: Rocking Out needs three pirate-clothing pieces worn, Mourning's End Part II needs full mourner clothes worn, and Within the Light needs two sets plus worn/give-away state; each live row encoded a single inventory token.

## Edit refused an old string that is not unique — 1 occurrence

Disposition: operator error (`operator-error`). Evidence: the Edit tool documents that `old_string` must be unique.

- 2026-08-27T07:03:49-07:00 — A surgical `Edit` for the Agility command handler matched six identical `commit_direct_action(_change, after_apply=_after_apply)` lines and was rejected; include the surrounding handler context before replacing repeated call shapes.

## Focused runs needed a hand-written rsync destination — 1 occurrence

Disposition: fixed before this triage (`fixed-before`). Evidence: `0e543a4d` added `--select`/`--expected-tests` to `tools/run_remote_tests.py`, which builds the destination itself (`:29`, `:225`).

- 2026-08-27 17:54 PDT — The first revised focused-test sync targeted `/Users/armantarkhanian/ankiscape-remote-test-host/` instead of its `repo/` child, so `rsync --delete` warned that environment and repository directories were not empty and the requested test modules were absent; guarded manual sync commands must preserve the runner's exact remote repository destination.

## A new worktree had no Qt interpreter — 1 occurrence

Disposition: fixed before this triage (`fixed-before`). Evidence: `b861cdec` links `.venv-qt` on creation (`tools/worktree_guard.py:160`), and `3336d4ba` does the same for leases.

- 2026-08-30 10:06 PDT — This guarded worktree predated the main-branch fix that symlinks the Qt environment at creation, so `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/diary-skill-rotation-2026-08-30/.venv-qt/bin/python` was initially missing; the coordinator linked it after the plain lane, making the required Qt lane runnable without changing tracked files.

## The reachability report had no completable-quest count — 1 occurrence

Disposition: fixed before this triage (`fixed-before`). Evidence: `c42d66bc` added `completable_quest_count` at `tools/audit_item_reachability.py:2023`, pinned by `tests/test_item_reachability_audit.py:1415-1417`.

- 2026-08-30 10:42 PDT — The reachability JSON stores `blocked_quest_stage_products` as a list and omits the derived quest-count fields; inspect the report schema before probing aggregate names.

## A computer-use relaunch escaped the disposable collection — 1 occurrence

Disposition: fixed before this triage (`fixed-before`). Evidence: `864466ca` binds each test app's startup to its disposable base (`tools/native/session_guard.py:200-219`, `tests/native/test_session_bootstrap.py`).

- 2026-09-21T17:43:23-07:00 — Cleanup call `call_OEymOlqPcC0HhKC7LHDNojkz` combined Escape, Command-Q and `app.getAXState()`; guarded PID `9715` exited and PID `10134` appeared without `-b`. After shutdown the owner collection SHA256 changed from `c913926adb106cfece8e618386fdd485b65bfd8bbe5d6cf8154f78c859aa73eb` to `cb453baf09dc92e2803f18a2c3479d00a19924e34d49fbf621d7e32133c50023`. The exact pre-run backup proves only config key `lastUnburied` changed; native isolation still failed. The trace does not prove the relaunch cause. Anki is closed; do not repeat this route against the owner's profile.

## The isolation check measured the collection while Anki could still write — 1 occurrence

Disposition: fixed before this triage (`fixed-before`). Evidence: `c15cb07d` calls `require_anki_stopped()` in `verify()` (`tools/native/session_guard.py:234`), with `test_verify_refuses_while_anki_runs`.

- 2026-09-21T17:43:23-07:00 — `guard-final-verify.stdout` reported `unchanged: true` before the unintended Anki process quit. The authoritative `guard-post-quit-verify.stdout` reports `unchanged: false`, exit 1; an early filename is not evidence of final isolation.

## Retiring scripts without a coverage map — 1 occurrence

Disposition: fixed before this triage (`fixed-before`). Evidence: `4147d0ae` mapped all 18 retired scripts to named tests before removing them (`memory-bank/progress.md:21-40`).

- 2026-09-23T18:13:32-0700 — The 18 proposed `tools/combat/check_*` and `tools/combat/run_*_remote.py` removals had no migration-index rows or named tests covering their source-guard and resume checks; restoring them preserves the checks rather than mislabeling gameplay tests as operational coverage.

## A quoted test count was not re-measured — 1 occurrence

Disposition: operator error (`operator-error`). Evidence: the global rule to re-measure every number at report time (decided 2026-08-15) already covers this.

- 2026-09-24T00:22:17-0700 — The Qt-lane speed brief quoted 5,731 discovered tests at main a45c92d8; `run_tests.py --list` on an exported a45c92d8 tree gives 5730 on both lanes, and the runner's full Qt lane reported `Ran 5730 tests`.

## Stale Homebrew pyflakes points at a removed Python — 1 occurrence

Disposition: external blocker (`external-blocker`). Evidence: the `/opt/homebrew/bin/pyflakes` shebang names `python@3.12`, which is gone; the repository declares no linter.

- 2026-09-24T03:47:03-0700 — Diary-generator cleanup, lint: `/opt/homebrew/bin/pyflakes` fails with `bad interpreter: /opt/homebrew/opt/python@3.12/bin/python3.12: no such file or directory`, and `python3 -m pyflakes` gives `No module named pyflakes`; vulture 2.16 and `py_compile` stood in, and `ruff` is not installed.

## A stale Qt cleanup ran after the shared teardown — 1 occurrence

Disposition: fixed before this triage (`fixed-before`). Evidence: `4b5e4485` removed `addCleanup(hud.close)`; the shared main-menu `tearDown` disposes of the HUD.

- 2026-09-24T03:40:44-0700 — UI test discovery slice: the focused Qt runner printed only `RuntimeError: wrapped C/C++ object of type ReviewHUD has been deleted` with no traceback, so the failing line had to be inferred from the unittest cleanup order (tearDown before addCleanup callbacks) and confirmed by rerunning without the cleanup.

## A focused selection included a deliberately skipped test — 1 occurrence

Disposition: design decision (`design-decision`). Evidence: `tools/run_remote_tests.py:435` refuses any focused skip on purpose, as triaged in `memory-bank/papercuts-fixed-2026-09-23.md:2833-2835`.

- 2026-09-24T04:08:35-0700 — Diary counter-key check, focused run: `CurationLedgerRuntimeExecutionTest` cannot be selected as a class on the no-skip remote runner because `test_real_blood_altar_tablet_checks_diary_before_next_teleport` carries a permanent `@unittest.skip` (Great Orb item 13 pending the owner's ruling), so its other 14 tests had to be selected one method name at a time.

## The Qt lane ran close to its time limit — 1 occurrence

Disposition: fixed before this triage (`fixed-before`). Evidence: `13ae5bc4` cut the Qt lane to `Ran 5737 tests in 783.949s` against `QT_LANE_TIMEOUT = 1300.0`, and `ec293a82` stopped the limit from counting the lock wait.

- 2026-09-23T21:53-07:00 — Gate on runtime batch 7b039d76 failed on host load, not on a test: Qt 'TIMEOUT: exceeded 1300 seconds' / 'FAILED: exit 124 (TIMEOUT)' at MacBook load 8.99/11.17/12.52, the third such failure that evening; its orphaned Qt lane qt-1790225120-677f3cf4 finished at 22:05 with 'Ran 5731 tests in 1164.657s' 'OK (skipped=5)', about 10% under the limit. A remote kill with a multi-PID variable failed with 'zsh:kill:1: illegal pid: 91572' and the second PID '91574' on the next line of the same message; pass each PID as its own argument.

## A resumed workflow agent became a second writer — 1 occurrence

Disposition: operator error (`operator-error`). Evidence: the one-owner rule for shared resources, and the orchestration rule at `memory-bank/progress.md:1090` adopted after this incident.

- 2026-09-24T00:53-07:00 — A SendMessage to the finished qt-lane-speed author a1df31f9e79c0091a resumed it while the workflow's review and fix stage worked in the same worktree, so two writers edited goal-qt-lane-speed-2026-09-23 (a duplicate data-step 6 results item and duplicate papercut lines); never message a workflow agent after its stage returned.
