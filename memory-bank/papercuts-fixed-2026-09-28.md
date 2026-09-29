# Papercuts fixed — 2026-09-28

These lines were moved verbatim from `memory-bank/papercuts.md` at main `279be965`. A per-entry triage on 2026-09-28 checked each entry against that tree and gave it one of three dispositions: `fixed`, when the cause no longer exists in the tree or a tool or test now prevents it; `duplicate`, when another open entry records the same cause; or `open`, when the cause still exists. Only `fixed` and `duplicate` entries are here. Each heading is one cause; the line below it gives the disposition and the evidence, and a duplicate section names the entry that stays open for its cause. The classification script, the move plan and the probes are in `ankiscape-promotion-evidence/goal-papercut-triage-2026-09-28/` under the git common dir.

## An entry already archived as fixed stayed open — 1 occurrence

Disposition: fixed (`fixed`). Evidence: `fc14c8f9` (2026-09-23) made the docs audit accept nested test module selectors, and the bare form of this entry is already archived at `memory-bank/papercuts-fixed-2026-09-25.md:61`. The bulleted copy stayed in `papercuts.md` when the move-tool landing (`c2e17622`) added its bullet, so at `279be965` `python3 tools/memory_bank/move_papercuts.py check HEAD` printed `open and fixed:` for it. Moving the open copy here, rather than deleting it, keeps both copies counted, so `check` against a revision that holds both passes.

- 2026-09-21T19:19:42-07:00: Full native-repair gate passed both suites but audit_docs rejected `native-relaunch-summary.md:6: dangling_test_selector: tests.native.test_session_bootstrap`; the valid nested-module command matched the selector scanner. Re-ran and documented unittest file paths; no validator change.

## The quest catalog had no check for cleanup actions that nothing emits — 1 occurrence

Disposition: fixed (`fixed`). Evidence: `d4880e24` (2026-09-27) added `test_every_cleanup_required_action_has_a_runtime_emitter` at `tests/test_quest_action_proofs.py:894`. It checks every cleanup `add_required_actions` string in the catalog against the runtime emitters and pins the 8 known unemitted stages at `tests/test_quest_action_proofs.py:826-840`, so a new unemitted string fails the plain lane. The 8 pinned stages stay open with the entry `2026-09-25T15:53-07:00` ("Cleanup emitter slice: the new catalog-wide test").

- 2026-08-23 11:20 PDT — (q-light slice) The Within the Light stage-1 cleanup carried a specific `add_required_actions` string with no runtime emitter, so stage 1 was permanently blocked; the fix pattern is to check every `add_required_actions` entry against the reachability audit before landing, not just the generated stubs.

## The catalog-wide emitter test hid most of its failures — 1 occurrence

Disposition: fixed (`fixed`). Evidence: `tests/test_quest_action_proofs.py:904` sets `self.maxDiff = None` before the set assertion (`d4880e24`), so a failure names every entry.

- 2026-09-25T15:53-07:00 — Cleanup emitter slice: the first failing run printed only `First extra element 0` and `Diff is 650 characters long. Set self.maxDiff to None to see it.`, hiding 7 of 8 violations; a catalog-wide list assertion needs `self.maxDiff = None` so the failure names every entry.

## Hand-written no-loss diffs of the papercut logs — 1 occurrence

Disposition: fixed (`fixed`). Evidence: `c2e17622` added `tools/memory_bank/move_papercuts.py`: `move` proves that no line is lost before it writes, and `check <base>` (`tools/memory_bank/move_papercuts.py:124`) runs the same proof against any revision. `memory-bank/systemPatterns.md:110-118` names the tool as the route for every papercut move.

- 2026-09-25T16:22:40-07:00 — Independent no-loss proof of the move-tool dogfood run: `grep -v '^$' papercuts.head.md fixed.head.md | sort` prefixed every line with its file name, so `diff` reported `1,2719c1,2721` (646.6KB); pipe the files through `cat` first or pass `grep -h`, or use `tools/memory_bank/move_papercuts.py check <base>` instead of a hand diff.

## The failed-write regression test first used a cap that could not fail — 1 occurrence

Disposition: fixed (`fixed`). Evidence: `tests/memory_bank_tools/test_move_papercuts.py:139` sets `RLIMIT_FSIZE` to 64 bytes (`c2e17622`), below the size of any archive, so the test fails against an in-place writer.

- 2026-09-26T09:23:50-07:00 — Move-tool review fix: the first failed-write regression test (RLIMIT_FSIZE equal to the existing archive's size) passed against the unfixed in-place writer, because the new archive only appends, so a truncating rewrite cut at the old size reproduces the old bytes exactly; the cap had to sit below the archive's size (64 bytes) before the test failed on the old tool (`FAILED (failures=3)` with all three new tests).

## The lane process scan tripped over macOS lsof and ps — 3 occurrences

Disposition: fixed (`fixed`). Evidence: `a54b2be3` (2026-09-27). The scan calls `/usr/sbin/lsof` (`tools/run_remote_tests.py:63`); lane ownership is marked by the lane's own pid and log files, not by an environment variable (`tools/run_remote_tests.py:61-63`, launch at `:455-458`); and the probe holds both files itself (`exec 8<"$log_path" 9<"$pid_path"`, `:61`), so a good scan always exits 0.

- 2026-09-26T09:23:14-0700 — Orphan-lane review fix: `test_orphaned_lane_blocks_sync_while_any_of_its_work_lives` failed with `AssertionError: RuntimeError not raised` on the MacBook because a bare `lsof` is not on the lanes' `PATH=/opt/homebrew/bin:/usr/bin:/bin` (it lives in `/usr/sbin`) and `2>/dev/null` hid the `command not found`; the lane process scan now calls `/usr/sbin/lsof`.
- 2026-09-26T09:13:58-0700 — Orphan-lane review fix: tagging lane processes with an inherited environment variable was ruled out because `ps -E -ww -p 89818 -o pid=,command=` on macOS 26.6 printed only `89818 sleep 30`, no environment, for a same-user process started with `ANKISCAPE_REMOTE_RUN=probe-xyz`; ownership is marked with the lane's stdin file and `lsof -t` instead.
- 2026-09-26T15:35:17-0700 — Orphan-lane review 3: `lsof -F pfa -- A B` exits 1 when either named file has no holder (`one-held st=1`, `both-held st=0`), so its status cannot tell an empty scan from a failed one; the lane probe now holds both lane files itself so a successful scan always exits 0.

## A pending record written before lanes recorded their process group was rejected as invalid — 1 occurrence

Disposition: fixed (`fixed`). Evidence: `a54b2be3`. `_read_pending` now accepts a record without `pid_path` (`tools/run_remote_tests.py:239-243`), so such a record no longer stops a run with `invalid pending run record`. It is still judged only by its report: with no report, `_lane_confirmed_stopped` cannot confirm the stop (`:249-250`, `:268-275`) and `_reconcile_pending_run` raises (`:319-320`). That no-report case stays open with the entry `2026-09-23T19:52:04-0700` ("Quest catalog loader slice: after acquiring the mirror").

- 2026-09-26T09:42:58-0700 — Orphan-lane review fix: the final focused run exited 1 with `error: invalid pending run record; sync blocked: /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.pending.json` because another session running main's runner had in flight run `plain-1790440867-be9d7f57`, whose record has no `pid_path`; this branch's runner treats a main-format record as invalid, so any run in flight when this branch lands blocks the next run until it finishes.

## Test IDs had two forms, so hand counts and dotted selectors missed — 3 occurrences

Disposition: fixed (`fixed`). Evidence: `8f70a917` (2026-09-27) roots discovery at the checkout (`run_tests.py:160`, `top_level_dir=root`), so every ID starts with `tests.`. The discovery probe (`probe_selectors.py` in the evidence directory) printed `total 5053 unique 5053 first tests.achievement_diaries.test_catalog_scan.AchievementDiaryCatalogScanTest.test_generator_reproduces_every_shipped_task_row` and `'tests.test_agility': 31 ids`.

- 2026-09-23T17:35:00-0700 Carried pack-refill slice: I counted focused tests with `run_tests.py --list ... | grep -c "^test_"`, which misses package-qualified IDs such as `runtime_actions.test_carried_processing_reconciliation...`; the remote run passed 90 tests but exited 1 with 'remote focused lane false pass: tests=90, skipped=0; expected exactly 86 tests and no skips'. Count each selector's `--list` output instead.
- 2026-09-24T00:20:23-0700 — Carried-requirements slice: `run_tests.py` selectors are case-folded substrings of discovered test IDs such as `test_agility.TestX.test_y` and `runtime_actions.test_carried_new_bank_trip...`, so `tests.test_agility` matches nothing; count with `/opt/homebrew/bin/python3 run_tests.py --list --max-results 100000 -- <selectors>` locally before the remote run.
- 2026-09-24T06:40:03-0700 — Combat burst enemy-turn cleanup: counting focused tests with `grep -c "^tests\."` over `run_tests.py --list` output gave 0 for all 51 selectors, because the listed IDs carry no `tests.` prefix (`combat.test_vampyre_bite.VampyreBiteTest...`, `test_combat_logic....`); one `--list` call with every selector, matched per selector afterwards, also avoids 51 separate discovery passes (about two minutes).

## Short selectors picked up sibling modules and methods — 4 occurrences

Disposition: fixed (`fixed`). Evidence: `8f70a917`: `matching_ids` (`run_tests.py:32-37`) prefers whole dotted segments. The discovery probe on this tree: `test_dispatcher_state` gives 19 IDs, all in `tests.runtime_actions.test_dispatcher_state`; `test_agility` gives 31, all in `tests.test_agility`; `test_farming` gives 85, all in `tests.test_farming`; each of the three Clan Wars test names gives 1.

- 2026-09-24T05:26:00-0700 — Agility handler cleanup: counting focused tests for the 63 modules that mention Agility, bare module names as selectors (`test_farming`, `test_logic`, ...) also matched test methods in other modules by substring, pulling 171 Qt-only `MainMenuWidgetTest` tests (all skipped on the plain lane) into the selection; a trailing dot (`test_farming.`) anchors the selector to the module.
- 2026-09-25T14:57:43-0700 — Level-up dialog slice: `--select test_dispatcher_state` also matched `runtime_actions.test_dispatcher_state_coverage` because run_tests.py selects by case-folded substring, so the focused plain run refused with 'remote focused lane false pass: tests=22, skipped=0; expected exactly 21 tests and no skips'; count with `run_tests.py --list` before choosing --expected-tests.
- 2026-09-25T15:50:55-0700 — Carried overlay fourth cleanup: the brief's bare module selectors (`--select test_agility` and twelve more) listed 599 tests in `run_tests.py --list`, 21 more than the 578 the modules hold, because substring matching also picked `test_agility_…` and `test_woodcutting_split_…` methods in the Qt-only `MainMenuWidgetTest` (and its `skills.test_target_level_order` and `tests.test_main_menu_widget` aliases) that skip on the plain lane, which the no-skip remote runner refuses; the trailing-dot form `test_agility.` from the earlier papercuts is still needed.
- 2026-09-26T19:38:37-0700 — Red-portal Qt readers: three exact Clan Wars test names still selected 5 tests by case-folded substring, so the run refused with 'error: remote focused lane false pass: tests=5, skipped=0; expected exactly 3 tests and no skips' (same cause as the 2026-09-25 level-up line).

## Widget tests were discovered two or three times — 3 occurrences

Disposition: fixed (`fixed`). Evidence: `8f70a917`: one `tests.` discovery root plus the duplicate-ID refusal (`run_tests.py:73-78`, `:156-163`), and `TargetLevelOrderWidgetTest` no longer subclasses `MainMenuWidgetTest` (`tests/skills/test_target_level_order.py:140`). The discovery probe: `test_main_menu_widget.` gives 421 IDs; `test_cooking_details_expose_target_equipment_policy_and_recovery` gives 1.

- 2026-09-23T17:57:00-07:00: Focused Qt selectors by method name matched 21 inherited/rediscovered widget tests rather than 7; the runner correctly refused with "error: remote focused lane false pass: tests=21, skipped=0; expected exactly 7 tests and no skips". Fully qualified `tests.test_main_menu_widget.MainMenuWidgetTest` selectors isolate the intended seven without relaxing expected-tests.
- 2026-09-24T00:26:32-0700 — Root prayer/feedback cleanup: a focused selector `test_main_menu_widget.` matches 842 ids, not 421, because five other test modules import that module as `tests.test_main_menu_widget` and discovery collects `MainMenuWidgetTest` a second time; substring selectors cannot pick one copy.
- 2026-09-26T20:14:42-0700 — Cooking glove swap review: the qt focused run `--select test_root_initializer_digest_under_qt --select test_cooking_details_expose_target_equipment_policy_and_recovery --expected-tests 2` refused with 'remote focused lane false pass: tests=4, skipped=0; expected exactly 2 tests and no skips' because the cooking-details test is discovered three times (`tests.test_main_menu_widget`, `test_main_menu_widget`, and inherited by `skills.test_target_level_order.TargetLevelOrderWidgetTest`); count with `run_tests.py --list` first.

## UI flow tests sat in a folder that discovery skipped — 3 occurrences

Disposition: fixed (`fixed`). Evidence: `4b5e4485` (2026-09-24) moved them to `tests/ui_flows/` with an `__init__.py`; `tests/ui` no longer exists, and the discovery probe gives `test_encounter_transitions.` 12 IDs in `tests.ui_flows.test_encounter_transitions`.

- 2026-09-23T21:36:42-0700 — tests/ui/test_activity_one_click.py matches the evil_tree/shooting_star grep but has no tests/ui/__init__.py, so run_tests.py discovery never sees it ("No unambiguous unittest ID matched: test_activity_one_click.") and the remote runner cannot run it.
- 2026-09-24T04:34:34-0700 — Root review-helpers slice: this base (`promote/runtime-batch-2026-09-23`) has no `tests/ui/__init__.py`, so `unittest` discovery finds 0 tests in `tests/ui/test_encounter_transitions.py` and the selector `ui.test_encounter_transitions.` had to be dropped from the focused run.
- 2026-09-26T13:49:05-0700 — Combat burst sixth cleanup (resumed): `run_remote_tests.py ... qt --select test_encounter_transitions. --expected-tests 12` exited 1 with `No unambiguous unittest ID matched: test_encounter_transitions.`, because `tests/ui/` has no `__init__.py` and `loader.discover(start_dir=.../tests)` skips it; the three `tests/ui/` modules run in no lane.

## The root surface digest depended on the checkout folder name — 1 occurrence

Disposition: fixed (`fixed`). Evidence: `c97e04b0` (2026-09-27) fixes `ROOT_PACKAGE_NAME = "ankiscape_fork"` at `tools/module_surface.py:37`.

- 2026-09-24T00:26:32-0700 — Root prayer/feedback cleanup: `tools/module_surface.py --digest-only __init__.py` names the root package after the checkout directory, so from worktree `goal-root-prayer-feedback-2026-09-24` it printed `88df30b8c64fc382ae312220b1d2096321faa72d453ad7b849ac7ee39c617c75` instead of the pinned `74044844e6abb546bc2d895f337ec92c0afe66ddc9002931d65dc12256cd5f4e`; the same tree copied to a directory named `ankiscape_fork` printed the pinned digest, so a local root-surface check must run from a directory with that name.

## A focused run needs an exact test count that no tool gives — 4 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T09:22:34-0700` ("Runner-sync review follow-up: to learn the exact"), which records the same cause: a focused remote run needs `--expected-tests`, and the only way to get it is a hand count. Entry `2026-09-23T20:26:43-0700` also names `tests.test_docs_audit`, which now resolves (`8f70a917`). Entry `2026-09-23T20:26:43-0700` ("Docs-audit selector slice: 'run_remote_tests.py ... plain --select") also records a long wait on the shared mirror lock, which stays open with the entry `2026-09-24T00:53:15-0700` ("The one-test focused Qt proof (`--select test_cape_tradeability.CapeTradeabilityRuntimeTest.test_buy_sell_persist_in_real_anki_collection"). Entry `2026-09-23T19:23:09-0700` ("Combat preview risk slice: 'run_remote_tests.py ... plain") also records that plain-lane selections must not hold Qt-only tests, which stays open with the entry `2026-09-26T13:35:32-0700` ("Undo equipment handoff: `--select test_encounter_transitions.` also pulled").

- 2026-09-23T20:26:43-0700 Docs-audit selector slice: 'run_remote_tests.py ... plain --select tests.test_docs_audit' failed with 'error: --select and --expected-tests must be supplied together', then with 'No unambiguous unittest ID matched: tests.test_docs_audit'; the runner wants the bare 'test_docs_audit' plus '--expected-tests 8', which the dispatch brief's command omitted. Each retry waited ~10 min on the shared remote lock.
- 2026-09-23T19:23:09-0700 Combat preview risk slice: 'run_remote_tests.py ... plain --select X' refused with 'error: --select and --expected-tests must be supplied together' (rc=2); count with run_tests.select_tests over TestLoader().discover('tests'), and send widget modules to the qt lane because a focused run rejects any skip.
- 2026-09-26T15:38:06-07:00 — Barbarian lap-bonus verification: launched `--select test_agility. --expected-tests 35` before discovery completed; the list proved 31 tests. Interrupted only PID 72138 while it waited on the mirror lock, before sync or test execution; use the discovered count.
- 2026-09-26T20:18:00-0700 — Barbarian lap-bonus review fix: ran `--select test_agility. --expected-tests 33` from memory; the runner answered `error: remote focused lane false pass: tests=31, skipped=0; expected exactly 33 tests and no skips`; take the count from `run_tests.py --list`, not from memory.

## A live lane from another session fails the next run at once — 7 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T09:43:20-0700` ("Upstream-spec review fix: run_remote_tests.py waited for the"), which records the same cause: the runner waits on the mirror lock but fails at once while another session's lane is still alive. `a54b2be3` removed the commonest way to reach this state: a runner or gate that hits its time limit now stops its lane while it holds the lock (`tools/run_remote_tests.py:506-512`). A runner killed outright still leaves a live lane, and `_reconcile_pending_run` still raises `previous remote lane is not confirmed stopped; sync blocked` (`:319-320`) instead of waiting.

- 2026-09-23T23:38:11-0700 — Focused Qt proof refused with `previous remote lane has no completion report; sync blocked` because another session's Qt lane `qt-1790231314-54789936` was still running on the MacBook after its driver had released /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock; the retry passed after that run ended and its pending record was reconciled.
- 2026-09-23T21:53:35-0700 — Focused Qt proof for the diary generator stopped twice at `error: previous remote lane has no completion report; sync blocked; pending record: /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.pending.json; run: qt-1790225120-677f3cf4` while another slice's full Qt lane was still running; it succeeded only after that run's `.report` appeared on the MacBook.
- 2026-09-23T23:50:42-0700 — Diary-generator review-fix rerun: three more attempts (23:35-23:45) exited 1 with `error: previous remote lane has no completion report; sync blocked; ... run: qt-1790231314-54789936` from another slice's Qt lane; a retry loop every 120 seconds got through on the sixth attempt.
- 2026-09-26T09:44:08-0700 — Live-tree sync retirement Qt verification stopped before execution: 'error: previous remote lane has no completion report; sync blocked; pending record: /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.pending.json; run: plain-1790440867-be9d7f57; log: /Users/armantarkhanian/ankiscape-remote-test-host/reports/plain-1790440867-be9d7f57.log; report: /Users/armantarkhanian/ankiscape-remote-test-host/reports/plain-1790440867-be9d7f57.report'. Preserved the foreign pending record and stopped further remote verification; its driver must reconcile that exact run before the focused Qt and final Memory Bank checks can run.
- 2026-09-23T20:47:17-0700 Combat preview risk slice: two focused remote runs stopped at sync with 'error: previous remote lane has no completion report; sync blocked' naming other agents' runs (qt-1790216520-05d98288, plain-1790221091-b0104622) while those were still in flight; each rerun had to wait out the other slice's lane.
- 2026-09-23T19:52:26-0700 Shop access-lock slice: after waiting on the lock, both focused lanes failed at sync with `error: previous remote lane has no completion report; sync blocked; pending record: /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.pending.json; run: qt-1790216520-05d98288` while another slice's full Qt lane was still running on the MacBook; relaunched and queued again.
- 2026-09-26T09:43:46-0700 — Quota-ledger final focused run exited 1 before tests started: `error: previous remote lane has no completion report; sync blocked; pending record: /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.pending.json; run: plain-1790440867-be9d7f57; log: /Users/armantarkhanian/ankiscape-remote-test-host/reports/plain-1790440867-be9d7f57.log; report: /Users/armantarkhanian/ankiscape-remote-test-host/reports/plain-1790440867-be9d7f57.report`; the runner requests a rerun to reconcile completion before sync, with the pending record left untouched.

## The MacBook SSH key was not in the agent — 8 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-27T00:27:20-0700` ("Undo bank handlers: every `tools/run_remote_tests.py` run stopped"), which records the same cause: the passphrase-protected `~/.ssh/id_ed25519` is not loaded into `ssh-agent`, so BatchMode SSH to the MacBook fails.

- 2026-09-27T01:44:30-0700 — JavaScript review fix F7: the focused remote Qt run stopped before sync with `error: remote qt prerequisites failed with exit 255` and `Permission denied (publickey,password,keyboard-interactive).` because the MacBook SSH key was not loaded; focused proof for the fix waits on SSH.
- 2026-09-27T02:23:32-0700 — JavaScript slice commit stage: the retried 28-test focused remote Qt run again stopped before sync with `error: remote qt prerequisites failed with exit 255` and `Permission denied (publickey,password,keyboard-interactive).` (`commit-qt.log`); the F7 fix is committed without its focused remote proof.
- 2026-09-27T01:46-07:00 — Queue-records slice review fixes: the focused MacBook run could not repeat because `tools/run_remote_tests.py` fails with 'Permission denied (publickey,password,keyboard-interactive)' while the SSH key is not loaded; the 73-test rerun is recorded as owed in progress.md.
- 2026-09-27T02:27:09-0700 — Digest-race-on-proof integration: `/opt/homebrew/bin/python3 tools/run_remote_tests.py "$PWD" plain --select test_generated_skill_data. --select test_smithing_data. --select test_summoning_data. --expected-tests 24` exited 1 with "error: remote plain prerequisites failed with exit 255; stdout: ''; stderr: 'ArmanTarkhanian@armans-macbook-pro: Permission denied (publickey,password,keyboard-interactive).\n'"; no focused test could run.
- 2026-09-27T00:27:43-0700 — Upstream-spec fifth review fix: four runs of `run_remote_tests.py "$PWD" plain --select test_promotion_gate. --select test_memory_bank_queue_packet. --expected-tests 46` (three sandboxed, one unsandboxed) exited 1 at 'Remote preparation' with "error: remote plain prerequisites failed with exit 255; stdout: ''; stderr: 'ArmanTarkhanian@armans-macbook-pro: Permission denied (publickey,password,keyboard-interactive).\n'"; `ssh-add -l` reports 'The agent has no identities.', and `~/.ssh/config` pins `IdentityFile ~/.ssh/id_ed25519` with `IdentitiesOnly yes`, so the MacBook no longer accepts that key and no focused run is possible until the owner restores SSH access.
- 2026-09-27T01:52:07-0700 — Orphan-lane review 4: the focused MacBook run for the fix exited 1 with `error: remote plain prerequisites failed with exit 255; stdout: ''; stderr: 'ArmanTarkhanian@armans-macbook-pro: Permission denied (publickey,password,keyboard-interactive).\n'` because the SSH key was not loaded, so the fix was committed with its focused and load-bearing runs owed.
- 2026-09-27T00:24:06-0700 — Barbarian lap-bonus commit: the focused re-run after the hook fix refused before sync with `error: remote plain prerequisites failed with exit 255; stdout: ''; stderr: 'ArmanTarkhanian@armans-macbook-pro: Permission denied (publickey,password,keyboard-interactive).\n'`, inside and outside the sandbox; `ssh-add -l` reported `The agent has no identities.`
- 2026-09-27T01:47:35-0700 — Thieving fight-back second review: `tools/run_remote_tests.py` could not reach the MacBook, failing with 'Permission denied (publickey,password,keyboard-interactive)' because the SSH key was not loaded, so the Memory Bank focused run for this round is owed and listed in progress.md.

## Queued remote runs outlive the Bash tool's foreground limit — 9 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-24T00:53:15-0700` ("The one-test focused Qt proof (`--select test_cape_tradeability.CapeTradeabilityRuntimeTest.test_buy_sell_persist_in_real_anki_collection"), which records the same cause: the mirror-lock wait is untimed (`tools/run_remote_tests.py:541-546`), so a queued remote run outlives the Bash tool's foreground limit unless it starts in the background. Entry `2026-09-26T14:46:30-0700` ("Upstream-spec second review fix: the combined audit") also records an audit sequence that outran the Bash tool's 120-second limit, which stays open with the entry `2026-09-26T15:47:52-0700` ("Combination Runecrafting review-fix audits exceeded the Bash").

- 2026-09-26T14:46:30-0700 — Upstream-spec second review fix: the combined audit command (audit_docs, audit_test_quality, audit_item_reachability, worktree_guard audit, git diff --check) passed the Bash tool's 120s cap and moved to the background, and run_remote_tests.py then printed 'Remote mirror busy; waiting for /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock' for about 11 minutes, so a foreground wait over 600s also timed out; start both in the background and wait on their output files.
- 2026-09-23T17:55:48-0700 Carried pack-refill slice: the focused remote plain rerun took 20:11 wall time for 16.877 s of tests, waiting on `~/Library/Caches/ankiscape-remote-test-host.lock` behind four other slices' lanes, so it overran the 600 s tool cap and was moved to the background.
- 2026-09-23T17:35:00-07:00: Focused Agility remote tests waited on /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock while another slice owned the MacBook test mirror; the runner printed "Remote mirror busy; waiting for /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock".
- 2026-09-24T01:29:55Z: Continuation Agility remote plain verification waited on /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock; runner printed "Remote mirror busy; waiting for /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock" before passing.
- 2026-09-24T01:48:36Z: Reviewed Agility focused remote run exceeded the 600-second Bash foreground cap while waiting on the shared MacBook runner; command continued in the background.
- 2026-09-23T19:25:12-0700 Quest catalog loader slice: remote runner waited about 10 minutes per run on 'Remote mirror busy; waiting for /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock' while another slice held the MacBook.
- 2026-09-23T21:36:42-0700 — The focused remote plain run for the distraction-handler slice waited more than 600 seconds on /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock, so the Bash tool detached it before the lock was free.
- 2026-09-26T15:48:04-0700 — Combination Runecrafting review-fix focused proof waited for the shared test host: `Remote mirror busy; waiting for /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock`.
- 2026-09-26T19:20:14-0700 — Combination Runecrafting review verification queued behind another remote lane: `Remote mirror busy; waiting for /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock`; output is retained in `review-verify-memory-bank-1919.log` in the branch evidence directory.

## The root-initializer surface test always skips on remote lanes — 3 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T19:34:22-0700` ("Red-portal surface pins: `--select test_module_surface.` can never"), which records the same cause: `test_root_initializer_is_reported_as_unavailable_without_aqt` (`tests/test_module_surface.py:256-262`) skips on both lanes, so no focused run can select `test_module_surface.` whole. Entry `2026-09-26T14:19:26-0700` also names the selector `test_first_wave_digests.`, which now resolves (`8f70a917`). Entry `2026-09-23T19:25:12-0700` ("Quest catalog loader slice: the focused remote") also records Qt-only modules selected for the plain lane, which stays open with the entry `2026-09-26T13:35:32-0700` ("Undo equipment handoff: `--select test_encounter_transitions.` also pulled").

- 2026-09-25T16:21:18-0700 — `run_remote_tests.py "$PWD" qt --select test_module_surface. --expected-tests 9` exited 1 with `error: remote focused lane false pass: tests=9, skipped=1; expected exactly 9 tests and no skips`, because `test_root_initializer_is_reported_as_unavailable_without_aqt` runs the plain interpreter, which has no `aqt`, and skips on every remote lane; select the other eight methods by name.
- 2026-09-23T19:25:12-0700 Quest catalog loader slice: the focused remote plain lane rejects any skip, and `tests/test_module_surface.py` skips its root-initializer test without aqt ('remote focused lane false pass: tests=783, skipped=1; expected exactly 783 tests and no skips'); Qt-needing modules in a quest-importer selection (that one and `test_main_menu_widget`, 842 tests all skipped on plain) must go to the qt lane.
- 2026-09-26T14:19:26-0700 — Combat preview max-hit slice: `--select test_first_wave_digests.` made `run_tests.py --list` exit 2 with `Closest matches for 'test_first_wave_digests.': test_first_wave_digests, ...`, because it is a method of `test_module_surface`, not a module; `test_module_surface.` itself holds `test_root_initializer_is_reported_as_unavailable_without_aqt`, which skips on the plain lane, so a no-skip focused run must select that module's other methods by name.

## An unconditional skip in the diary wiring module — 2 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T13:25:35-0700` ("Prayer Off potions slice: selecting the whole"), which records the same cause: `test_achievement_diary_ledger_wiring` carries an unconditional `@unittest.skip` (`tests/test_achievement_diary_ledger_wiring.py:602`), so a whole-module focused run always fails. Entry `2026-09-23T19:23:24-0700` ("Shop access-lock slice: focused selections cannot include") also records the root-initializer skip, which stays open with the entry `2026-09-26T19:34:22-0700` ("Red-portal surface pins: `--select test_module_surface.` can never"). Entry `2026-09-23T22:11:27-0700` ("Focused remote plain rerun failed in sync") also records a live lane from another session that blocked the run, which stays open with the entry `2026-09-26T09:43:20-0700` ("Upstream-spec review fix: run_remote_tests.py waited for the").

- 2026-09-23T19:23:24-0700 Shop access-lock slice: focused selections cannot include `test_achievement_diary_ledger_wiring.CurationLedgerRuntimeExecutionTest.test_real_blood_altar_tablet_checks_diary_before_next_teleport` (permanent `@unittest.skip`) or `test_module_surface.ModuleSurfaceTest.test_root_initializer_is_reported_as_unavailable_without_aqt` on either lane (it shells out to the plain interpreter and calls `skipTest`), because the runner rejects any skip; the first plain attempt ended `FAILED (failures=1, skipped=2)`.
- 2026-09-23T22:11:27-0700 — Focused remote plain rerun failed in sync with `error: previous remote lane has no completion report; sync blocked` for another slice's still-running qt-1790225120-677f3cf4 (its local runner had released the lock); waited read-only for its .report to appear, then the rerun reconciled and passed. Separately, tests/test_achievement_diary_ledger_wiring.py carries an unconditional @unittest.skip, so whole-module focused selection always fails the runner's no-skip rule.

## A refused focused run does not name the skipped test — 3 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-24T05:30:40-0700` ("Agility handler cleanup: a focused plain-lane run"), which records the same cause: focused remote runs use `--quiet` (`tools/run_remote_tests.py:380`, `run_tests.py:183`), so the skipped test is never named, and `--list` shows no skip decorators. Entry `2026-09-26T20:02:12-0700` ("Shop-restock review fix: the focused plain run") also records a Qt-only class in a plain-lane module, which stays open with the entry `2026-09-26T13:35:32-0700` ("Undo equipment handoff: `--select test_encounter_transitions.` also pulled"). Entry `2026-09-26T20:14:14-0700` ("Thieving fight-back review fix: a plain focused") also records the unconditional diary wiring skip, which stays open with the entry `2026-09-26T13:25:35-0700` ("Prayer Off potions slice: selecting the whole"). Entry `2026-09-26T20:14:14-0700` ("Thieving fight-back review fix: a plain focused") also records a Qt-only class in a plain-lane module, which stays open with the entry `2026-09-26T13:35:32-0700` ("Undo equipment handoff: `--select test_encounter_transitions.` also pulled").

- 2026-09-24T04:52:01-0700 — Root review-helpers slice: two focused plain runs ended `OK (skipped=1)` and the runner refused (`remote focused lane false pass: tests=2052, skipped=1`), but `run_tests.py --quiet` never names the skipped test, so a runtime `skipTest` (not a decorator) could only be found by excluding candidates and paying another four-minute remote run.
- 2026-09-26T20:02:12-0700 — Shop-restock review fix: the focused plain run refused with `remote focused lane false pass: tests=117, skipped=2; expected exactly 117 tests and no skips` because `test_ranging_guild` has a `skipUnless(HAS_QT, "Qt lane only")` class and `test_cape_tradeability` a `skipIf(... "Anki runtime is not installed")` test; `run_tests.py --list` does not show skip decorators, so grep the selected modules for `skip` before counting.
- 2026-09-26T20:14:14-0700 — Thieving fight-back review fix: a plain focused run over 14 Combat-review modules refused with 'remote focused lane false pass: tests=579, skipped=3; expected exactly 579 tests and no skips', because `test_achievement_diary_ledger_wiring` carries an unconditional `@unittest.skip` and `test_encounter_transitions` has a Qt-only class; the log names no skipped test, so find them with `grep -n skip` and move Qt-only modules to the qt lane.

## Plain-lane modules hold Qt-only classes — 1 duplicate

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T13:35:32-0700` ("Undo equipment handoff: `--select test_encounter_transitions.` also pulled"), which records the same cause: a module selected for the plain lane holds Qt-only tests that skip there (for example `tests/ui_flows/test_encounter_transitions.py:401-405`), and the no-skip rule refuses the run. The 842-ID half of this entry is fixed by `8f70a917`; the discovery probe gives `test_main_menu_widget.` 421 IDs.

- 2026-09-23T19:05:21-0700 Shop access-lock slice: `run_remote_tests.py --select` rejects any skip, and the fragment `test_main_menu_widget.` selects 842 IDs (421 twice, because `tests/skills/test_target_level_order.py` imports `MainMenuWidgetTest`), so aqt-skipping modules must go to the qt lane, not the plain one.

## `run_tests.py --list` stops at 200 IDs — 2 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T19:57:18-0700` ("Shop-restock review fix: `run_tests.py --list` exited 2"), which records the same cause: `--max-results` defaults to 200 (`run_tests.py:118`).

- 2026-09-26T13:26:45-0700 — Undo equipment handoff: `run_tests.py --list` with no selector exited 2 with `Refusing to print 5764 IDs; narrow the selector or raise --max-results above 200.`; pass the focused selectors and `--max-results 5000` when counting `--expected-tests`.
- 2026-09-26T13:23:32-0700 — Urn recovery continuation: counting focused tests with `run_tests.py --list` exited 2 with 'Refusing to print 5764 IDs; narrow the selector or raise --max-results above 200.'; pass `--max-results 10000` to list every ID before choosing --expected-tests.

## Remote-host tests route fake SSH calls by command text — 2 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T14:41:12-07:00` ("Orphan-lane review 2: the first focused run"), which records the same cause: the fake SSH in `tests/test_remote_test_host.py` recognises commands by text prefixes such as `startswith("cat ")` and `".pid " in` (`tests/test_remote_test_host.py:132-150`, `:222`, `:241`, `:292`).

- 2026-09-25T15:59:09-0700 — Orphan-lane slice: `test_remote_test_host.RemoteTestHostTests.test_pending_run_only_releases_mirror_after_valid_completion` failed with `AssertionError: False is not true` because it used `startswith("cat ")` as its proxy for a read-only remote command, and the new `kill -0 -- -<group>` liveness probe sends no signal but is not a `cat`.
- 2026-09-26T09:19:49-0700 — Orphan-lane review fix: prefixing the launch with `: > <pid> &&` broke five `tests/test_remote_test_host.py` checks that identify the launch by `startswith("nohup ")`; the launch keeps that prefix and creates the pid file with the `<>` redirect instead.

## Local lsof inspection of the lane or lock files — 3 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T15:33:28-0700` ("Orphan-lane review 3: on this Mac (macOS"), which records the same cause: local `lsof` probes of the lane and lock files returned nothing or hung. On 2026-09-28 the same probes answered in 0.3 to 0.5 s (`open-cause-demos.txt` in the evidence directory), so the hang did not reproduce, but nothing in the tree prevents it.

- 2026-09-26T19:24:25-07:00 — Stale-gate review verification: `lsof '/Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock'` produced no output before the 120s command timeout moved task `bydvmxopf` to the background; stopped only that diagnostic task, while the focused remote reader tests completed normally.
- 2026-09-26T14:42:25-07:00 — JavaScript-test slice: optional `lsof -n /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock` inspection produced no output after repeated waits; stopped only its verified child processes and left the queued tests intact.
- 2026-09-26T14:45:46-07:00: Read-only `lsof /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock` did not return a lock inventory; stopped only this slice's verified lsof PIDs 69605 and 69629, leaving the runner and lock untouched.

## `select.kqueue` is not a context manager — 3 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T16:09:36-0700` ("Undo-history review-fix completion wait assumed `select.kqueue` was"), which records the same cause: `select.kqueue()` has no `__enter__` (`kqueue context manager: False` on `/opt/homebrew/bin/python3`).

- 2026-09-26T15:52:17-0700 — Stale-gate review follow-up: an inline filesystem completion watcher failed with `TypeError: 'select.kqueue' object does not support the context manager protocol (missed __exit__ method)` while the focused proof was still waiting for the remote mirror lock; the existing background task and monitor already track completion.
- 2026-09-26T16:08:07-0700 — JavaScript review fixes: a read-only completion watcher assumed `select.kqueue()` supports `with`; it exited with `TypeError: 'select.kqueue' object does not support the context manager protocol (missed __exit__ method)` while the focused test runners continued unchanged.
- 2026-09-26T15:50:17-0700 — Combination Runecrafting review-fix wait command assumed `select.kqueue()` supported `with`; Python refused with `TypeError: 'select.kqueue' object does not support the context manager protocol (missed __exit__ method)` before waiting. The focused runner was unaffected.

## A search that finds nothing stops an `&&` chain — 1 duplicate

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T19:19:30-07:00` ("Stale-gate review verification: the optional active-runner probe"), which records the same cause: a search with no match exits 1 and stops the rest of an `&&` chain.

- 2026-09-26T19:21:13-0700 — Combination Runecrafting review verification searched `review.diff` for `UI test modules were never discovered`; that heading is outside the diff context, so `grep` exited 1 and stopped the `&&` inspection chain. Reading the diff opening showed the original misplaced lines.

## `find /` for Anki source runs past the tool limit — 1 duplicate

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T14:14:55-0700` ("Reward transaction failure slice: looking for Anki's"), which records the same cause: a whole-disk `find` runs past the command limit, while the pinned `aqt` source is in the worktree's `.venv-qt`.

- 2026-09-26T20:19:56-0700 — Upstream-spec fourth review fix: `find / -path "*/aqt/sync.py"` to read Anki's full-sync code ran past the Bash tool's 120s cap and moved to the background; the installed aqt source is at `/Users/ArmanTarkhanian1/Library/Application Support/AnkiProgramFiles/.venv/lib/python3.13/site-packages/aqt/` (buildhash `d52ca669`), so read it there directly.

## Paths and globs used before they were discovered — 38 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T21:26:06Z` ("Winter Storage read-only diagnosis: guessed paths `tests/test_carried_new_bank_trip.py`"), which records the same cause: an agent read or globbed a path it had guessed instead of discovering it; `tools/repo_search.py` exists and `memory-bank/techContext.md:42-49` names it, but nothing makes an agent use it. Entry `2026-09-27T01:47:38-0700` ("Upstream-spec sixth review fix: `grep -rln "def") also records an empty search result that broke the rest of the command, which stays open with the entry `2026-09-26T19:19:30-07:00` ("Stale-gate review verification: the optional active-runner probe"). Entry `2026-09-26T19:56:40-0700` ("Undo-history second review-fix slop-gate lookup repeated the") also records that the slop gate's location is not recorded in the repository, which stays open with the entry `2026-09-26T14:04:00-0700` ("Thieving fight-back slice: the brief names the").

- 2026-09-26T14:18:00-07:00 — Stale-gate slice: attempted read of unlisted `tests/promotion/helpers.py` failed with `sed: tests/promotion/helpers.py: No such file or directory`; the existing fixture is `PromotionRepo` in `tests/test_promotion_gate.py`.
- 2026-09-26T14:19:00-07:00 — Stale-gate slice: unquoted nonexistent glob `tools/slop*` failed with `zsh:1: no matches found: tools/slop*` and prevented the next search; use `rg --files` to find tooling before reading it.
- 2026-09-26T15:43:06-07:00 — Stale-gate review follow-up: a file-length probe assumed the test module lived under `tests/promotion/`, failed with `wc: tests/promotion/test_promotion_gate.py: open: No such file or directory`, and prevented the chained reader search; locate test paths before probing them.
- 2026-09-26T14:18:03-07:00 — JavaScript-test slice: startup assumed `tests/pkg_alias.py` and `.githooks/*`; reads returned `sed: tests/pkg_alias.py: No such file or directory` and `zsh:1: no matches found: .githooks/*`; the alias is at repository root and file discovery must precede optional-path reads.
- 2026-09-27T01:47:38-0700 — Upstream-spec sixth review fix: `grep -rln "def advance_evil_tree_world_clock_pure" core/` found nothing because the world-clock functions live under `logic/`, and the empty result fed `sed -n ",40p"`, which failed with 'sed: 1: ",40p': invalid command code ,'; search `--include='*.py' .` from the repo root first.
- 2026-09-26: Promotion snapshot investigation: zsh glob tools/worktrees/*.py had no matches; use observed paths only.
- 2026-09-26T14:28:31-07:00: Promotion snapshot read-only reviewer hit `zsh:1: no matches found: requirements*`; use observed file paths instead of shell globs.
- 2026-09-26T15:58:54-0700 — Promotion snapshot review fixes: reading `tests/test_remote_mirror_lock.py` from the review's abbreviated path returned `File does not exist.`; `git ls-files '*remote_mirror_lock*'` located `tests/promotion/test_remote_mirror_lock.py`.
- 2026-09-23T17:29:00-07:00: Agility complexity preflight searched a guessed .pre-commit-config.yaml that does not exist (rg: .pre-commit-config.yaml: No such file or directory (os error 2)); repository inventory and installed analyzer binaries resolved the measurement path.
- 2026-09-26T09:34:16-0700 — Combat burst sixth cleanup: searching fixture paths with the unmatched shell glob `tests/test_carried_*.py` failed with `(eval):1: no matches found: tests/test_carried_*.py`; use `rg` file globs instead of shell-expanded path globs.
- 2026-09-26T14:17:09-0700 — Combination Runecrafting pack diagnosis tried stale test paths: `sed: tests/test_carried_inventory.py: No such file or directory`, `zsh:1: no matches found: tests/test*carried*`, and `rg: tests/runtime_actions/test_runtime_actions.py: IO error for operation on tests/runtime_actions/test_runtime_actions.py: No such file or directory (os error 2)`; `rg --files tests` located `tests/test_runtime_actions.py` and `tests/runtime_actions/`.
- 2026-09-26T14:19:08-0700 — Combination Runecrafting pack check discovery assumed hook configuration files existed: `rg: .pre-commit-config.yaml: No such file or directory (os error 2)` and `rg: pyproject.toml: No such file or directory (os error 2)`; use the installed Git hook and `rg --files` for the actual gate paths.
- 2026-09-26T14:19:54-07:00 — Combination Runecrafting pack check discovery hit `zsh:1: no matches found: tools/item_reachability*`; the reachability check is `tools/audit_item_reachability.py`, and file discovery now uses `rg --files` before reads.
- 2026-09-26T09:45:51-07:00 — Minigame XP diagnosis: zsh rejected memory-bank/*castle-wars* with 'no matches found'; discovered source-audit paths with rg --files instead.
- 2026-09-26T09:45:51-07:00 — Minigame XP diagnosis: attempted to read tests/runtime_actions/test_activity_progression.py; sed reported 'No such file or directory'; the existing activity tests are in tests/test_runtime_actions.py.
- 2026-09-26T09:55:44-07:00 — Minigame XP audit lookup: rg reported "tools/reachability/cli.py: IO error for operation on tools/reachability/cli.py: No such file or directory (os error 2)"; the check entry point is in tools/audit_item_reachability.py.
- 2026-09-26T09:45:01-0700 — Quest auto-flee repair: a zsh search glob failed with `zsh:1: no matches found: tests/test_logic_pure*`, so no search evidence file was created; use `rg` file filters instead of assumed shell globs.
- 2026-09-26T09:47:00-0700 — Quest auto-flee repair: a hook-path search returned `rg: .githooks: No such file or directory (os error 2)`; discover the hook location from Git instead of assuming a repository .githooks directory.
- 2026-09-26T09:46:57-0700 — Undo equipment diagnosis: an unmatched shell glob stopped a search with `zsh:1: no matches found: core/direct_action*`; discover filenames with `rg --files` before reading.
- 2026-09-26T09:46:57-0700 — Undo equipment diagnosis: guessed file reads failed with `rg: tests/test_combat_method_transaction.py: IO error for operation on tests/test_combat_method_transaction.py: No such file or directory (os error 2)` and `sed: core/combat_state_update.py: No such file or directory`; the relevant code is in `__init__.py` and `tests/combat/test_encounter_lifecycle.py`.
- 2026-09-26T09:51:27-0700 — Undo equipment diagnosis: another guessed path failed with `rg: logic/urn_logic.py: IO error for operation on logic/urn_logic.py: No such file or directory (os error 2)`; the zero-ore cause is the Shattered Heart hook in `runtime/runtime_actions_shared.py`.
- 2026-09-26T09:45:12-07:00 — Urn recovery inspection assumed a root AGENTS.md and stopped at `cat: AGENTS.md: No such file or directory`; the dispatch supplies the instructions, and `rg --files -g AGENTS.md` finds no repository copy.
- 2026-09-26T09:45:12-07:00 — Urn recovery test discovery used an unmatched shell glob and stopped at `zsh:1: no matches found: tests/test*death*`; bounded `rg` discovery found the tests under `tests/combat/` and `tests/test_combat_logic.py`.
- 2026-09-26T21:26:06Z — Winter Storage rollback investigation: zsh rejected the unmatched `tests/*carried*` glob with `zsh:1: no matches found: tests/*carried*`; search the `tests` directory with `rg` instead.
- 2026-09-26T21:26:06Z — Winter Storage rollback investigation: zsh rejected `runtime/*review*.py` with `zsh:7: no matches found: runtime/*review*.py`; use `rg --glob` with quoted patterns for optional file-name matches.
- 2026-09-26T21:26:06Z — Winter Storage rollback investigation: zsh rejected the optional `undo*` path with `zsh:5: no matches found: undo*`, so the dependent snapshot-search log did not exist; all following path discovery uses `rg --files` instead of shell globs.
- 2026-09-26T21:26:06Z — Winter Storage rollback investigation: the guessed `review_undo.py` search path returned `rg: review_undo.py: No such file or directory (os error 2)`; the review snapshot code is in `__init__.py`.
- 2026-09-26T15:38:32-0700 — Stack packing check discovery: a shell glob for an absent hook directory stopped the search with "zsh:1: no matches found: .githooks/*"; locate paths with rg --files before reading them.
- 2026-09-26T15:40:45-0700 — Stack packing source lookup: an unmatched shell glob again stopped a read with "zsh:3: no matches found: logic/fletching*"; subsequent source lookups use rg over literal directories without shell globs.
- 2026-09-26T15:36:16-0700 — Cooking glove swap investigation: guessed paths failed with `zsh:1: no matches found: ui/target*` and `sed: runtime/runtime_action_context.py: No such file or directory`; discover exact paths with rg --files before reading.
- 2026-09-26T15:38:28-0700 — Cooking glove swap investigation: a guessed tooling glob failed with `zsh:1: no matches found: tools/slop*`; remaining searches pass literal paths or rg --glob patterns, so zsh cannot expand guessed paths.
- 2026-09-26T14:21:21-0700 — Real undo-history audit-tool lookup repeated an unexpanded shell glob and failed with `zsh:1: no matches found: tools/*slop*`; further path searches use `rg --files` and `rg --glob` so the shell cannot expand search patterns.
- 2026-09-26T14:17:54-0700 — Real undo-history coverage inspection: a guessed glob failed with `zsh:1: no matches found: runtime/*callbacks*`, and guessed paths failed with `sed: hooks.py: No such file or directory`, `sed: hooks/__init__.py: No such file or directory`, and `sed: core/state.py: No such file or directory`; discovered paths with `rg --files` before further reads.
- 2026-09-26T16:10:36-0700 — Undo-history review-fix runner inspection guessed `tools/promotion/remote_test_host.py`; `rg` exited 2 with `rg: tools/promotion/remote_test_host.py: No such file or directory (os error 2)`. The runner implementation is in the already-known `tools/run_remote_tests.py`.
- 2026-09-26T19:56:40-0700 — Undo-history second review-fix slop-gate lookup repeated the unexpanded zsh glob and failed with `(eval):1: no matches found: tools/*slop*`; the gate lives at `core.hooksPath` `/Users/ArmanTarkhanian1/fleet/config/git/hooks/slop_gate.py`, not under `tools/`.
- 2026-09-26T15:35:46-07:00 — Shop-restock diagnosis: assumed logic/shop/transactions.py exists; sed returned "sed: logic/shop/transactions.py: No such file or directory"; enumerate the package before selecting files.
- 2026-09-26T15:36:31-07:00 — Shop-restock diagnosis: rg .git/info/exclude returned "Not a directory (os error 20)" because this linked worktree has a .git file; resolve git paths with git rev-parse.
- 2026-09-26T15:38:24-07:00 — Shop-restock diagnosis: optional lint-config lookup returned "rg: pyproject.toml: No such file or directory (os error 2)" and "rg: .pre-commit-config.yaml: No such file or directory (os error 2)"; use tools/repo_search.py to validate paths before searching.

## Complexity limits surface only at commit — 3 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-27T02:50:23Z` ("Winter Storage commit: the pre-commit slop gate"), which records the same cause: the slop gate runs only as the pre-commit hook, after review and remote proof, and no repository tool measures touched functions before then.

- 2026-09-26T09:41:53-0700 — Orphan-lane review fix: the commit failed with `slop-gate: cognitive complexity above 15 was introduced:` / `tools/promotion/lane_execution.py: _run_check_sequence 17 (was 15)` because a conditional expression inside the check loop costs 2; assigning the earlier record inside the existing `if mirror_lock is not None:` block costs 0.
- 2026-09-26T20:45:57-0700 — Orphan-lane review 3 follow-up: the first commit failed with `slop-gate: cognitive complexity above 15 was introduced:` / `tests/test_remote_test_host.py: RemoteTestHostTests::test_disconnected_launch_reconciles_same_run_and_preserves_failure 16 (was 14)` because a second `next(...)` generator costs 2; one exact `assertIn` on the whole stop script replaced it.
- 2026-09-27T00:22:47-0700 — Barbarian lap-bonus commit: the pre-commit slop gate refused the reviewed diff with `logic/agility_logic.py: _standard_course_review 17 (was 15)` (cyclomatic) and `_standard_course_review 25 (was 20)` (cognitive); the review lane had not measured the edited engine function, only the new tests, so measure every touched function with `lizard` and `complexipy` before review.

## File and directory caps refuse the natural home for new code — 6 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-25T16:25:51-07:00` ("The papercut triage named the new tool"), which records the same cause: the slop gate refuses growth of files over 1000 lines and new files in directories already at 40 (top-level `tests/` holds 236 Python files, `tools/` 137, `logic/` 87), and briefs and authors pick a home before checking. Entry `2026-09-24T05:29:04-0700` ("Equip/unequip handler cleanup: adding nine lines of") also records a slop-gate refusal that came only after remote proof had started, which stays open with the entry `2026-09-27T02:50:23Z` ("Winter Storage commit: the pre-commit slop gate"). Entry `2026-09-27T10:32:02-0700` ("Slayer text-fit commit: slop-gate refused a new") also records a slop-gate refusal that came only after all remote proof had run, which stays open with the entry `2026-09-27T02:50:23Z` ("Winter Storage commit: the pre-commit slop gate").

- 2026-09-25T15:52-07:00 — Cleanup emitter slice: the triage named `tests/test_item_reachability_audit.py` for the new test, but at 1899 lines the slop gate refuses any growth (limit 1000), and `tests/` holds 236 files (directory cap 40); the test went into `tests/test_quest_action_proofs.py` (901 lines before).
- 2026-09-24T01:51:26Z: Attempting an optional deactivation assertion in the existing Agility regression grew tests/test_runtime_actions.py; slop-gate refused "tests/test_runtime_actions.py: 5936 lines (was 5935)"; discarded the optional assertion rather than split a large test module for an already-covered behavior.
- 2026-09-24T05:29:04-0700 — Equip/unequip handler cleanup: adding nine lines of assertions to an existing test in `tests/test_integration_smoke.py` made the slop gate refuse with `slop-gate: code files above 1000 lines were grown:` / `tests/test_integration_smoke.py: 9322 lines (was 9313)`; the test moved to a new `tests/runtime_actions/test_equipment_change.py` that borrows the smoke suite's `setUp`/`tearDown`. Run the gate on a temporary index before the first remote run, because the remote run then has to be stopped and restarted.
- 2026-09-26T13:22:04-07:00 — Minigame XP finish: correcting a stale stub in tests/test_runtime_actions.py (5935 lines) could not add even a comment line, because the slop gate forbids growth of a file over 1000 lines; the fixture change was written in place on the existing line.
- 2026-09-26T13:27:12-0700 — Quest auto-flee repair continuation: reverting the previous author's shorter override comment to keep a one-line diff made the slop gate refuse `logic_pure/logic_pure_quest.py: 1582 lines (was 1581)`; the comment trim was the line offset that lets a file over 1000 lines take a new line, so check `wc -l` against the base before undoing a line-neutral edit.
- 2026-09-27T10:32:02-0700 — Slayer text-fit commit: slop-gate refused a new helper at tests/qt_text_fit.py with 'slop-gate: code files were added to directories already at 40 files: tests: 237 code files (was 236)', after all remote proof had run; put new test helpers in a subpackage such as tests/ui_flows/ from the start.

## Any new public import moves a pinned surface digest — 2 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T20:14:51-0700` ("Cooking glove swap review: adding one module-level"), which records the same cause: `tools/module_surface.py:303` hashes every public name in the module namespace, imports included.

- 2026-09-24T00:20:23-0700 — Carried-requirements slice: importing `AgilityTarget` only for a type hint moved the `tools/module_surface.py` digest of `runtime/runtime_actions_carried_requirements.py` from `526fd231...` to `f7ce6d38...`, because every imported public name is part of the surface; a refactor that must keep the surface keeps `Any` hints.
- 2026-09-26T15:31:32-0700 — Combat preview max-hit review fix: importing a new public helper into `logic_pure_combat_engine.py` failed `test_first_wave_digests` with `MODULE_SURFACE_SHA256: logic_pure/logic_pure_combat_engine.py 158292fcbad402f0fbfb8d0f9587bea05e1c324b3cf25447d3fcd0e6763ada61` against the pinned `5cb6204b91995219447dd2fa7f700734014b234b99546907c6a5a7d16b66bf7b`, because the surface digest counts every public name in the module namespace, imports included; a private `_` name leaves it unchanged (check with `python3 tools/module_surface.py --digest-only <path>` before a remote run).

## zsh globs an unquoted `--include=*.py` — 10 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T14:13:30-0700` ("Reward transaction failure slice: in zsh an"), which records the same cause: zsh expands the unquoted glob in the option and aborts with `no matches found: --include=*.py`. Entry `2026-09-25T15:44-07:00` ("Sync-overwrite investigation: two zsh one-liner slips cost") also records the zsh `=` expansion of `echo ===`, which stays open with the entry `2026-09-26T20:58:07-07:00` ("Queue-records slice: `echo ======` between two sed").

- 2026-09-25T15:44-07:00 — Sync-overwrite investigation: two zsh one-liner slips cost retries, `grep -rn ... --include=*.py` failed with '(eval):1: no matches found: --include=*.py' (unquoted glob) and `echo ===` failed again with '(eval):1: == not found' (repeat of the 2026-09-24 line); the local canonical `.venv-qt` is python3.13 and the MacBook lane python3.14, both Anki 25.09.4 d52ca669 with identical aqt line numbers, so either copy is citable.
- 2026-09-25T15:51:26-07:00 — A `grep -rn ... --include=*.py` in the harness zsh aborted with `(eval):1: no matches found: --include=*.py` before grep ran; quote glob-shaped grep options (`'--include=*.py'`) in zsh.
- 2026-09-27T01:45:53-07:00 — Move-tool R7 fix: `grep -rn move_papercuts --include=*.py --include=*.md .` aborted with `(eval):1: no matches found: --include=*.py` because zsh globs the unquoted `--include=*.py`; quote the pattern (`--include='*.py'`).
- 2026-09-26T09:38:02-0700 — Upstream-spec review fix: `grep -rl QTimer --include=*.py .` in a zsh one-liner failed with '(eval):1: no matches found: --include=*.py' because zsh expands the unquoted glob before grep runs; quote it as `--include='*.py'`.
- 2026-09-24T00:14:20-0700 — `grep -rn ... --include=*.py .` in the agent's zsh shell failed with `(eval):1: no matches found: --include=*.py`; zsh globs the unquoted pattern, so quote it as `--include='*.py'`.
- 2026-09-25T15:10:23-0700 — Combat burst player-attack cleanup: `grep -rn ... --include=*.py .` failed with `(eval):1: no matches found: --include=*.py`, because zsh expands the unquoted glob before grep runs; `--include='*.py'` works.
- 2026-09-26T13:20:50-07:00 — Minigame XP finish: an unquoted `grep -rn ... --include=*.py` failed in zsh with '(eval):1: no matches found: --include=*.py'; quote the glob as `--include='*.py'`.
- 2026-09-26T13:23:18-0700 — Quest auto-flee repair continuation: `grep -rn "combat_auto_flee" --include=*.py .` failed with `(eval):1: no matches found: --include=*.py` because zsh expands the unquoted glob in the flag; quote the pattern or use `rg -g '*.py'`.
- 2026-09-26T13:22:16-0700 — Undo equipment handoff: `grep -rn "def attach_tool_to_toolbelt_pure" -A40 --include=*.py logic core` stopped with `(eval):1: no matches found: --include=*.py` because zsh expands the unquoted glob before grep runs; quote it (`--include='*.py'`).
- 2026-09-26T13:56:53-0700 — Processing exception inventory fix: `grep -rn "run_answer_with_carried_overlay" --include=*.py .` failed in zsh with `(eval):1: no matches found: --include=*.py` before grep ran, because zsh treats the unquoted `*.py` in the option as a glob with no match; quote it as `--include='*.py'`.

## zsh expands a word that starts with `=` — 3 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T20:58:07-07:00` ("Queue-records slice: `echo ======` between two sed"), which records the same cause: zsh `=word` expansion makes `echo =====` fail with `==== not found`.

- 2026-09-27T02:25:22-0700 — Digest-race-on-proof integration: `echo ======` in a zsh one-liner printed "(eval):29: ===== not found" again; the 2026-09-24T06:05:41-0700 line above already records this zsh `=` expansion.
- 2026-09-25T15:20:07-0700 — Combat burst player-attack cleanup: `echo ====` as a separator in a zsh command failed with `(eval):1: === not found` and exit code 1, because zsh `=word` expansion looks up a command named after the text; quote it (`echo '===='`).
- 2026-09-26T13:19:56-07:00 — Minigame XP finish: `sed ... && echo ===== && sed ...` failed in zsh with '(eval):1: ==== not found' because zsh expands a word that starts with `=` as a command path; use `echo ---` as a separator.

## zsh does not word-split an unquoted variable — 13 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T13:24:03-0700` ("Combat burst sixth cleanup (resumed): a zsh"), which records the same cause: zsh passes an unquoted `$F` holding several words as one argument. Entry `2026-09-24T04:32:00-0700` ("Livid Farm / Temple Trekking handler cleanup: counting") also names bare module selectors, which now match whole segments (`8f70a917`).

- 2026-09-26T09:19-07:00 — Sync-overwrite review fix: a zsh loop over command strings (`for c in "python3 tools/audit_docs.py" ...; do $c; done`) ran nothing, each failing with '(eval):10: no such file or directory: python3 tools/audit_docs.py' exit 127, because zsh does not word-split an unquoted $c; use ${=c} or run the commands one by one.
- 2026-09-23T19:23:09-0700 Combat preview risk slice: zsh does not word-split an unquoted $F holding two paths, so 'lizard --csv $F' and complexipy/radon silently measured nothing (empty grep, exit 0); pass each path literally.
- 2026-09-23T19:05:21-0700 Shop access-lock slice: zsh does not word-split an unquoted `$MODS` in `for f in $MODS`, so the loop saw one argument; read the list with `while read -r` into an array instead.
- 2026-09-23T21:25:28-0700 — Building the remote runner's repeated --select flags in one zsh string variable passed them as a single argument, so tools/run_remote_tests.py exited 2 with "error: unrecognized arguments:  --select test_cadence_live. ..."; a zsh array ("${S[@]}") fixed it.
- 2026-09-23T21:28:41-0700 — Measuring handler complexity with `F="a.py b.py"; complexipy $F` under zsh passed one unsplit path, so complexipy and radon wrote empty results (`[]`, `{}`) with no error; quoted per-file arguments fixed it.
- 2026-09-24T00:20:23-0700 — Carried-requirements slice: the first remote focused run exited 2 with `run_remote_tests.py: error: unrecognized arguments:  --select tests.test_agility ...` because zsh does not word-split an unquoted `$S` string of flags; build the selectors as a zsh array (`ARGS+=(--select "$s")`) instead.
- 2026-09-24T00:18:14-0700 — A `for c in "python3 tools/audit_docs.py" ...; do $c; done` audit loop exited 127 with `no such file or directory: python3 tools/audit_docs.py` because zsh does not word-split unquoted parameters; run the five audits as explicit commands.
- 2026-09-24T04:32:00-0700 — Livid Farm / Temple Trekking handler cleanup: counting focused tests with `run_tests.py --list`, an unquoted zsh `$MODS` again reached the runner as one selector (`No unambiguous unittest ID matched: test_bankstanding_notice test_dispatcher_state ...`, exit 2); `${=MODS}` splits it. Bare module selectors such as `test_farming` also substring-match `MainMenuWidgetTest.test_farming_*` and pull in Qt tests, so plain-lane selectors need the trailing dot.
- 2026-09-24T04:33:44-0700 — Combat HUD cleanup: counting focused tests with `run_tests.py --list`, an unquoted zsh `$P` holding ten selectors reached the script as one argument and it printed `No unambiguous unittest ID matched:` with all ten names joined; a zsh array (`"${P[@]}"`) fixed it. The open log already holds seven other lines naming this word-splitting trap.
- 2026-09-25T15:50:55-0700 — Carried overlay fourth cleanup: `python3 tools/module_surface.py --digest-only $M` with three module names in one zsh variable reached the tool as one argument (`No module named 'ankiscape.runtime.runtime_actions_carried_overlay ankiscape'`); zsh does not word-split unquoted variables, and the tool takes file paths such as `runtime/runtime_actions_carried_overlay.py`.
- 2026-09-26T19:45:28-0700 — Combination Runecrafting commit-stage checks looped over quoted command strings in zsh, which does not word-split `$c`, so every check refused with `(eval):1: no such file or directory: python3 tools/audit_docs.py` (exit 127); rerunning through `eval "$c"` fixed it.
- 2026-09-26T20:53:20-0700 — Reward transaction failure slice: in zsh a `--select` list built into one variable (`SEL=$(... | tr '\n' ' ')`) reaches run_remote_tests.py as one argument and fails with `run_remote_tests.py: error: unrecognized arguments: --select test_undo_seam_circus. ...`; expand it with `${=SEL}`.
- 2026-09-26T19:57:32-0700 — Shop-restock review fix: building `--select` flags in a zsh variable passed them as one word, and the runner exited 2 with `run_remote_tests.py: error: unrecognized arguments:  --select test_shop_restock. ...`; zsh does not word-split unquoted `$S`, so write the flags out.

## A zsh loop variable named `path` replaces the command search path — 3 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T16:03:16-0700` ("Undo-history review-fix reader search used `for path"), which records the same cause: zsh ties `path` to `PATH`, so a loop variable of that name breaks command lookup.

- 2026-09-26T15:43:45-07:00 — Stale-gate review follow-up: the documentation reader search used zsh's special `path` variable as a loop variable and ended with `(eval):1: command not found: rg`; that variable changes command lookup, so use a non-special variable name.
- 2026-09-26T15:59:50-0700 — Promotion snapshot review inventory: a zsh loop variable named `path` replaced the shell command search path; later commands failed with `(eval):1: command not found: git` and `(eval):1: command not found: tail`; use `changed_file` instead.
- 2026-09-26T09:46:25-0700 — Combat burst sixth cleanup: a zsh loop named its variable `path`, which replaced zsh’s special `path` array and made the next command fail with `(eval):1: command not found: git`; use `relative_path` for file loops so command lookup is unchanged.

## Mutation proofs done by hand leave or lose changes — 4 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T20:14:39-0700` ("Reward transaction failure slice: a review round's"), which records the same cause: red-proof mutations are made and restored by hand, so a proof can leave a mutant, revert too much or too little, or be cut off before it restores. Entry `2026-09-26T14:10-0700` ("Test-tools cleanup slice: the stopped earlier author") also records a stopped author whose handover could not be trusted, which stays open with the entry `2026-09-26T20:40:32-0700` ("Orphan-lane review 3 follow-up: the dispatch found"). Entry `2026-09-26T09:33:45-0700` ("Orphan-lane review fix: a session restart at") also records a session restart that cut the proof off, which stays open with the entry `2026-09-26T20:40:32-0700` ("Orphan-lane review 3 follow-up: the dispatch found").

- 2026-09-26T14:10-0700 — Test-tools cleanup slice: the stopped earlier author left its load-bearing mutation (`"max_room": 8` in `logic/pyramid_plunder_logic.py`) in the uncommitted diff it handed over, so a resumed agent that keeps "what is correct" from `git diff` can ship a broken sanitizer; check every non-test hunk of an inherited diff for a leftover mutation.
- 2026-09-26T09:33:45-0700 — Orphan-lane review fix: a session restart at 09:23 left the worktree mid mutation proof, with `if (0)` in the lane process scan, `timeout=None` in `_ssh` and `is None` in `_stop_timed_out_remote_lane`, and the correct files only in the evidence directory as `run_remote_tests.py.bak` and `lane_execution.py.bak`; a mutation proof must restore before anything that can end the session, or name its backups in the worktree.
- 2026-09-26T15:13:30-07:00 — Orphan-lane review 2: the first mutation proof reverted the carried driver's SSH wrapper as `def launch_ssh(text, *, label, repeat_safe=False, **options)`, so the leftover `**options` still swallowed `deadline` and the TypeError was not reproduced; a second run with the exact original signature raised `TypeError: launch_job.<locals>.launch_ssh() got an unexpected keyword argument 'deadline'`.
- 2026-09-26T19:52:03-0700 — Shop-restock review fix: `git stash push logic/shop/state.py logic/shop_logic.py` to prove the buy-side regression red reverted the whole slice, not only the buy call site, so the run returned `Ran 1 test` / `OK` against a base where every transaction drops restock time anyway; revert only the one line under test, as the rerun did (`AssertionError: 1 != 0`).

## A stopped session leaves proof that cannot be trusted — 3 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T20:40:32-0700` ("Orphan-lane review 3 follow-up: the dispatch found"), which records the same cause: a session that stops mid-proof leaves partial evidence, a stale gate log or a lost background run, and the next agent cannot tell what was proven. Entry `2026-09-26T19:35:00-0700` ("Bunyip Daemonheim restructure: the author's final report") also records evidence that describes an earlier tree than the one reported, which stays open with the entry `2026-09-25T15:20:07-0700` ("Combat burst player-attack cleanup: a docstring edit").

- 2026-09-26T09:35:40-07:00 — Move-tool review fix: a session restart at 09:23 stopped the fix mid-proof, leaving staged edits and a `remote-plain-review-fix-final.txt` that held only the `Remote mirror busy; waiting for /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock` line; the resumed run had to re-run the focused lane before committing, since the half-written evidence proved nothing.
- 2026-09-26T19:35:00-0700 — Bunyip Daemonheim restructure: the author's final report quoted `slop-gate.log` written at 15:43, before it extracted the heal helper; the gate re-run on that author's final diff no longer reported complexity but `logic/summoning_logic.py: 1172 lines (was 1168)` (`slop-gate-opus-before.log`), which the restructure then brought back to 1168 lines, so a stopped author's quoted gate output can describe an earlier diff (re-run the gate on the final diff before quoting it).
- 2026-09-26T13:19:51-0700 — Quota-ledger review-fix focused run started at 09:58 logged only `Remote mirror busy; waiting for /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock` and ended with no exit record; by 13:19 no runner process remained, so the review stage had to rerun the focused proof from scratch.

## Broad reads overflow the tool output budget — 16 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T15:35:38-07:00` ("Barbarian lap-bonus investigation: combined repository reads exceeded"), which records the same cause: a broad search or batched read exceeds the tool output budget and is truncated; `memory-bank/techContext.md:45-49` already warns against broad searches, which has not stopped it. Entry `2026-09-26:` ("Promotion snapshot investigation: initial broad Memory Bank") also records an assumed root `AGENTS.md`, which stays open with the entry `2026-09-26T21:26:06Z` ("Winter Storage read-only diagnosis: guessed paths `tests/test_carried_new_bank_trip.py`").

- 2026-09-26T14:17:18-07:00 — Stale-gate slice: broad Memory Bank and tool searches exceeded the output budget (`Warning: truncated output (original token count: 20927)`); subsequent reads use bounded line ranges and saved search logs.
- 2026-09-26T14:17:36-07:00 — JavaScript-test slice: bundled startup file reads exceeded the tool output budget (`Warning: truncated output`); use bounded reads and evidence-file redirection for subsequent output.
- 2026-09-26: Promotion snapshot investigation: initial broad Memory Bank search was truncated; use bounded line ranges and evidence files. Root AGENTS.md is absent; dispatch supplies the rules.
- 2026-09-26T14:25:40-07:00: Promotion snapshot investigation: process command lines included the full dispatch prompt and truncated the inventory; future process inspection must bound fields or capture output in the evidence directory.
- 2026-09-26T16:19:57-0700 — Promotion review final evidence scan: unbounded `rg` over `memory-bank/progress.md` returned `Output too large (78KB).`; use line-bounded ranges and retain raw output in the evidence directory.
- 2026-09-26T14:17:09-0700 — Combined source and Memory Bank reads exceeded the output cap (`Warning: truncated output`); narrowed subsequent reads to the relevant function ranges and kept long evidence in the branch evidence directory.
- 2026-09-26T09:44:48-07:00 — Minigame XP diagnosis: initial batched Memory Bank search output was truncated (original token count: 10784); subsequent long output goes to the branch evidence directory and is read by bounded range.
- 2026-09-26T09:45:01-0700 — Quest auto-flee repair: broad startup reads exceeded the tool output budget (`Warning: truncated output`); use bounded ranges and evidence-file searches.
- 2026-09-26T09:44:45-0700 — Undo equipment diagnosis: the initial combined Memory Bank search exceeded the tool output limit (`Warning: truncated output (original token count: 21228)`); subsequent searches use bounded excerpts and out-of-tree logs.
- 2026-09-26T09:45:12-07:00 — Urn recovery inspection combined too many source ranges and tool output was truncated; read narrower ranges and retain long output in the branch evidence directory.
- 2026-09-26T21:26:06Z — Winter Storage rollback investigation: the combined Memory Bank search exceeded the tool output budget (`Warning: truncated output (original token count: 14641)`); redirect broad searches to the evidence directory and read bounded matches.
- 2026-09-26T21:34:45Z — Winter Storage verification: a broad process-command search matched another task prompt and exceeded the output budget (`Warning: truncated output (original token count: 2796)`); inspect only this task's runner logs and tool session handles.
- 2026-09-26T15:36:27-0700 — Stack packing investigation: combined source reads exceeded the tool output budget and were truncated; use bounded reads and keep full evidence in the branch evidence directory.
- 2026-09-26T15:35:36-0700 — Cooking glove swap investigation: a batched Memory Bank read exceeded the tool output budget (`Warning: truncated output (original token count: 13912)`); use smaller line ranges and redirect long outputs to the branch evidence directory.
- 2026-09-26T15:36:16-0700 — Cooking glove swap investigation: another batched read was truncated (`Warning: truncated output (original token count: 10093)`); subsequent reads use one bounded range per call.
- 2026-09-26T14:17:54-0700 — Real undo-history coverage inspection: a broad Memory Bank grep emitted `Warning: truncated output (original token count: 37496)`; switched to narrow ranges and out-of-tree logs.

## Generated shop data keeps whole tables on single lines — 1 duplicate

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-24T00:16:41-0700` ("`grep -n "wilderness" data/shop_data.py` returned 1.9MB because"), which records the same cause: `data/shop_data.py` has a 1,989,738-character line, so a plain grep returns megabytes; `tools/repo_search.py` caps columns, but nothing makes an agent use it. Entry `2026-09-26T15:35:46-07:00` ("Shop-restock diagnosis: unbounded searches truncated Memory Bank") also records unbounded searches that overflowed the tool output budget, which stays open with the entry `2026-09-26T15:35:38-07:00` ("Barbarian lap-bonus investigation: combined repository reads exceeded").

- 2026-09-26T15:35:46-07:00 — Shop-restock diagnosis: unbounded searches truncated Memory Bank output and matched the single-line generated data/shop_data.py catalog; use bounded ranges and redirect search output to the promotion evidence directory.

## complexipy writes its report into the working directory — 6 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-24T05:32:54-0700` ("Carried Pack yak slice: `complexipy runtime/runtime_actions_carried_overlay.py --output-format"), which records the same cause: complexipy writes `complexipy-results.json` and `.complexipy_cache/` into the current directory, and `--output` to a missing path writes a file, not a directory.

- 2026-09-23T19:05:21-0700 Shop access-lock slice: `complexipy logic/shop/state.py --output-format json` without `--output` wrote `complexipy-results.json` and `.complexipy_cache/` into the worktree root; pass `--output <evidence dir> -q` as `slop_gate.py` does.
- 2026-09-24T00:20:23-0700 — Carried-requirements slice: `complexipy <file>` writes an ignored `.complexipy_cache/` into the current directory and later runs report `last:` deltas from it; run it from the worktree and delete the cache afterwards.
- 2026-09-24T04:34:34-0700 — Root review-helpers slice: `complexipy __init__.py core/skill_availability.py -spi` wrote an untracked `complexipy-results.json` into the worktree root; it was moved to the out-of-tree evidence directory before review.
- 2026-09-24T05:25:04-0700 — Combat burst settlement cleanup: `complexipy logic_pure/logic_pure_combat_engine.py --output-format json -q -i` wrote `complexipy-results.json` into the worktree root as an untracked file; `--output <path outside the tree>` keeps metric runs from dirtying the checkout.
- 2026-09-24T06:16:46-0700 — Carried overlay bank-trip cleanup: `complexipy runtime/runtime_actions_carried_overlay.py --output-format json -q -i --output <evidence>/cx-before` wrote the JSON report as a plain file named `cx-before` because that path did not exist yet, so reading `cx-before/complexipy-results.json` (the layout `slop_gate.py` gets by passing an existing directory) failed with `NotADirectoryError: [Errno 20] Not a directory`; give `--output` a file path for a single-file metric run.
- 2026-09-26T09:52:59-07:00 — Reading the urn complexity baseline assumed `complexipy --output` created a directory, producing `NotADirectoryError: [Errno 20] Not a directory` for `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-urn-grave-progress-2026-09-26/baseline-complexity/complexipy-results.json`; the tool wrote JSON directly to `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-urn-grave-progress-2026-09-26/baseline-complexity`.

## complexipy exits 1 on functions the change did not touch — 1 duplicate

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T09:52:24-07:00` ("A whole-file `complexipy data/urn_data.py` census exited 1"), which records the same cause: complexipy exits 1 whenever any function in the file is over its limit, including unchanged ones.

- 2026-09-23T17:38:00-07:00: The first after-metrics shell chain stopped at complexipy --output-format json -q -i because existing above-threshold functions give exit 1 even though valid JSON was written; read that JSON and ran Radon separately instead.

## Hand-written readers of radon output — 2 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T15:39:57-07:00` ("Barbarian lap-bonus metrics: reading `radon hal --json`"), which records the same cause: each slice reads radon's JSON with its own parser, and radon's Halstead output nests functions in a mapping.

- 2026-09-26T14:24:57-07:00 — JavaScript-test slice: the Halstead result reader assumed function pairs, but radon emits a function-name mapping; it raised `ValueError: too many values to unpack (expected 2)`.
- 2026-09-24T01:50:14Z: Corrected Agility Radon summary initially assumed function metrics were top-level and got "KeyError: '_apply_agility_damage'"; they are nested under "functions".

## A hand-written comprehension over radon output referenced an undefined name — 1 duplicate

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-24T01:29:55Z:` ("Agility metric remeasurement first used a faulty"), which records the same cause: a slice's own comprehension over radon's JSON raised `NameError: name 'name' is not defined`.

- 2026-09-24T01:49:56Z: Agility remeasurement summary reused a malformed Radon comprehension and raised "NameError: name 'name' is not defined" after metric artifacts had been written; correcting only the summary extraction.

## Probes must run from the repository root — 2 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T14:53:27-07:00` ("Minigame XP review fix: a one-off /tmp"), which records the same cause: `pkg_alias.py` lives at the repository root and the packages import only through it.

- 2026-09-24T04:32:00-0700 — Livid Farm / Temple Trekking handler cleanup: a disposable probe run from `tests/` failed with `ModuleNotFoundError: No module named 'pkg_alias'`; `pkg_alias.py` lives at the repository root, so probes must run from the root.
- 2026-09-26T14:19:26-0700 — Combat preview max-hit slice: a probe script with `sys.path.insert(0, "tests")` failed with `ModuleNotFoundError: No module named 'pkg_alias'` because `pkg_alias.py` lives at the repository root; run such probes from the worktree root with `PYTHONPATH=.`.

## Probe output depends on the hash seed — 1 duplicate

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-24T05:30:33-0700` ("Agility handler cleanup: an out-of-tree before/after probe"), which records the same cause: set and dict iteration order changes with the per-process hash seed, so two runs of identical code differ unless `PYTHONHASHSEED=0`.

- 2026-09-24T04:39:06-0700 — Shop services cleanup probe: two runs of the same out-of-tree probe over every catalog item name differed at line 1151 (90 reordered `_item_tradeable` lines, identical when sorted), because the name set gathered from the catalog iterates in hash-seed order; before/after probes must run with `PYTHONHASHSEED=0`, the before side from a `git archive HEAD` snapshot.

## Differential probes miss the paths under change — 9 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-25T15:07:10-0700` ("Carried overlay third cleanup: the inherited 12000-scenario"), which records the same cause: hand-built differential probes are not measured for which paths they reach, so a mutation can change 0 cases.

- 2026-09-24T00:17:46-0700 — The shop before/after capture seeded 7 of every sampled item name, which included `Coins`, so every Wilderness buy was clamped and no ambush fired; re-seed the currency after the bulk inventory update when a capture needs purchases.
- 2026-09-24T04:33:44-0700 — Combat HUD cleanup: an out-of-tree probe that set `player_data["equipment"]["weapon"]` to every weapon still reported unarmed slots for all of them, because `_combat_weapon_type_id` reads `weapon_type` only from the `equipment_data` argument and `combat_hud_state_pure(player_data)` (the HUD's only call shape) passes none; the probe needed `equipment_data=EQUIPMENT_DATA` to reach the two-handed-sword SHARED chips.
- 2026-09-24T05:32:54-0700 — Carried Pack yak slice: the first uniform random probe of `_try_pack_yak_winter_storage_overlay` reached the scroll-spending path in only 41 of 40000 cases, because four independent gates must all pass; count the path you mean to prove and bias the generator before trusting an identical diff.
- 2026-09-24T06:40:03-0700 — Combat burst enemy-turn cleanup: in the settlement slice's differential probe every setup selected prayers but kept the `tests.test_combat_logic._player` default `combat_prayer_uptime` of `"off"`, so `prayer_uptime_fraction_pure` returned 0.0 and every selected prayer was inert; an in-memory mutation that skipped protection prayers and one that disabled Redemption each changed 0 of 49200 cases until the setups set `combat_prayer_uptime` (then 3148 and 761 cases).
- 2026-09-25T15:07:10-0700 — Carried overlay third cleanup: mutating against only the first 2000 probe scenarios, as the previous overlay slice did, misses Winter Storage, which spends a scroll in 29 of 96000 reviews; skipping the post-Winter-Storage bank refresh changed 0 of the first 16000 reviews and 17 of the full 96000.
- 2026-09-25T15:50:55-0700 — Carried overlay fourth cleanup: the inherited overlay probe (`probe.py`, SHA-256 `4be86d954401fa5206a5f8e3af87e1becb26aa76bfe7ac5ea696eb4c993e3a4d`) never lets its handler advance a cadence scheduler, so removing the handler-owned-scheduler guard in the cadence rollback changed 0 of 96000 reviews; only the remote `test_wall_safe_failure_consumes_one_multiplied_review_and_undoes_cadence` caught it (`KeyError: 'thieving:wall_safe'`).
- 2026-09-25T15:10:23-0700 — Combat burst player-attack cleanup: no enemy in `COMBAT_ENEMY_DATA` (0 of 203) has `melee_recoil_damage` or `protect_from_player_class`; they exist only for Tz-Kek in `data/fight_caves_data.py` and for Akrisae through `logic/barrows_logic.py:597`, so the earlier roster-only burst probes never reached melee recoil or class protection; adding the Fight Caves and Barrows enemies to the probe gave 131 recoil cases and 240 class-protected cases out of 61830.
- 2026-09-25T16:07:27-0700 — Combat burst curses cleanup: the player-attack slice's differential probe never activated a Sap or Leech curse, because `sanitize_prayer_selection_pure` keeps only the first curse offence family selected, so its `curses_ramp` setup `["soul_split", "turmoil", "sap_warrior", "leech_attack", "deflect_melee"]` sanitizes to `('soul_split', 'turmoil')`; and the roster's 1% Wilderness ambush fired 7 times in 61830 cases. One setup per curse family and Wilderness enemy copies with `ambush_chance` 1.0 gave 4142 Sap, 8284 Leech and 1444 ambush cases out of 80370.
- 2026-09-25T16:42:46-0700 — Combat burst set-up cleanup: the earlier probes' `melee_strong` setup selects `["protect_from_melee", "piety"]`, but `active_prayer_selection_pure` returns `('protect_from_melee',)` for that fixture player because Piety is gated, so no probe case ever had Piety up; the halo setup had to use `ultimate_strength` and `incredible_reflexes`, which survive sanitizing.

## Test fixtures built on guessed defaults — 3 duplicates

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T09:49:48-07:00` ("Quest auto-flee repair: the death fixture used"), which records the same cause: a new test's fixture used a guessed RNG roll, resource ID or level, so it failed or passed for the wrong reason.

- 2026-09-26T09:51:23-07:00 — Minigame XP regression setup: Castle Wars at level 40 and RNG 0.5 missed (player_accuracy 0.43953676272555886); Soul Wars returned 'Enemy avatar requires Slayer 100; current level is 99.'; these fixture failures did not reproduce the XP defect.
- 2026-09-26T09:46:24-07:00 — The first urn recovery regression used `impious_ashes` as the charging resource ID and failed setup with `AssertionError: False is not true` (`Ran 3 tests in 0.001s`, `FAILED (failures=3)`); inspect the checked-in accepted resource IDs before treating this as defect evidence.
- 2026-09-26T15:40:45-0700 — Stack packing regression fixture: the default helper roll of 0.0 awarded Shattered Heart rocks from a fresh save, so the initial output assertion failed with "AssertionError: 13 != 15"; fixed by providing non-awarding RNG draws while keeping the real handler and assertions.

## The test-quality audit does not see `_assert_` helpers — 1 duplicate

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T13:37:55-0700` ("Undo equipment handoff: `audit_test_quality.py` counts only calls"), which records the same cause: `tools/audit_test_quality.py:53` counts only calls whose name starts with `assert`, and `_call_name` (`:40-45`) keeps a leading underscore.

- 2026-09-26T09:51:23-07:00 — Minigame XP regression audit: audit_test_quality.py exited 1 with 'hard issues: 4' and 'test contains no assertion or assertion helper call'; new test entry points called an _assert_activity helper, which the fixed audit does not recognize.

## An appended record ends with an extra blank line — 1 duplicate

Disposition: duplicate (`duplicate`). Kept open: the `papercuts.md` entry `2026-09-26T09:44:58-0700` ("Combat burst sixth cleanup: the final documentation"), which records the same cause: an appended Memory Bank record ends with a blank line that `git diff --check` then rejects.

- 2026-09-23T18:04:00-07:00: Final `git diff --check` rejected the appended progress entry with "memory-bank/progress.md:13697: new blank line at EOF." Removed the extra blank line without changing the proof text, then reran the fixed check.

## 2026-09-29 — Unbounded reads exceed the tool output budget — 4 duplicates

Disposition: duplicate (`duplicate`), triaged on 2026-09-29 against main `98eb13f2`. Kept open: papercuts.md entry `2026-09-26T15:35:38-07:00`. Broad grep output, a raw lane-progress line, and combined record reads all exceed the output budget. Existing bounded search and the unittest-summary parser are available, but no command preflight makes the caller use them.

- 2026-09-29T10:49:39-0700 — Combat-state sanitizer cleanup: a repository-wide evidence grep for prior slop-gate commands produced 39.6KB and was truncated; inspect one known evidence directory or bound the search before reading results.
- 2026-09-29T11:28:25-0700 — Combat respawn-reset review follow-up: the first label search across Python, JSON, and Markdown produced 2.4 MB of results and was persisted out of view; limit UI-label searches to the rendering module and exact terms before widening.
- 2026-09-29T14:09:53-07:00 — Combat bank-run full-lane report: printing the last 22 log lines included an unbounded dot-progress line and returned `Warning: truncated output (original token count: 1041)`; use the existing `parse_unittest_summary` structured result for report output instead of raw log tails. The complete log is preserved.
- 2026-09-29T15:42:27-0700 — Papercut triage records slice: combined contract/tool/history reads returned 122.5KB and combined progress/test reads returned 32.2KB as persisted output instead of inline content; use one file or bounded sections per read and save broad history to the evidence directory.

## 2026-09-29 — Startup reads are too broad and guess an absent rules file — 1 duplicate

Disposition: duplicate (`duplicate`), triaged on 2026-09-29 against main `98eb13f2`. Kept open: papercuts.md entry `2026-09-26T15:35:38-07:00`; papercuts.md entry `2026-09-26T21:26:06Z`. This compound entry records both output-budget overflow and a guessed nonexistent AGENTS.md path. The two named open entries retain both causes; neither is treated as fixed.

- 2026-09-29T13:34:00-07:00 — Combat bank-run cleanup resume: broad startup reads returned truncated output (25895 and 32454 tokens); root AGENTS.md is absent (`cat: AGENTS.md: No such file or directory`). Use bounded reads and the supplied task rules.

## 2026-09-29 — Paths and optional globs are used before discovery — 5 duplicates

Disposition: duplicate (`duplicate`), triaged on 2026-09-29 against main `98eb13f2`. Kept open: papercuts.md entry `2026-09-26T21:26:06Z`. The retained Winter Storage entry records both guessed split-module/test paths and unmatched optional shell globs. The listed failures are the same causes, not literal mistyping of a verified absolute path. tools/repo_search.py --names already offers bounded filename discovery; the failure remains when the caller bypasses it.

- 2026-09-29T10:39:11-0700 — Root-menu cleanup: a guessed convention lookup failed with `sed: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/goal-root-menu-dispatch-2026-09-29/runtime/runtime_actions_farm_trekking.py: No such file or directory`; inspect the directory listing before choosing the split-module path.
- 2026-09-29 14:09 PDT: PvM death cleanup coverage search stopped with `(eval):1: no matches found: tests/test*death*`; use `rg` over `tests` instead of optional shell globs.
- 2026-09-29 14:10 PDT: Cleanup convention lookup guessed nonexistent `logic_pure/combat_attack_type.py`; use the actual file listing before reading a helper path.
- 2026-09-29 14:18 PDT: Adjacent-suite path lookup used `tests/test_encounter_lifecycle.py`, which does not exist; `rg --files tests` locates `tests/combat/test_encounter_lifecycle.py`. Resolve test paths from the file listing before content searches.
- 2026-09-29T15:43:29-0700 — Papercut triage records slice: an unlock-key grep included the guessed path `data/default_player_data.py` and emitted `No such file or directory`; the subsequent repository file search located all references without that nonexistent path. Use filename discovery before choosing a data-module path.

## 2026-09-29 — Root surface selections contain tests that skip — 3 duplicates

Disposition: duplicate (`duplicate`), triaged on 2026-09-29 against main `98eb13f2`. Kept open: papercuts.md entry `2026-09-26T19:34:22-0700`; papercuts.md entry `2026-09-26T13:35:32-0700`. The first retained entry records the root sentinel that always skips in a focused lane; the second also retains plain selections containing Qt-only checks. Completion or cancellation of the slice-owned waiting runner does not remove either selection cause. No no-skip gate was weakened.

- 2026-09-29T10:55:41-0700 — Root-menu neighbor proof: selecting all of test_module_surface in the plain focused lane produced `Ran 315 tests in 152.978s` / `OK (skipped=1)` but the runner correctly refused `error: remote focused lane false pass: tests=315, skipped=1; expected exactly 315 tests and no skips`; the plain root-import test skips without aqt, so select the Qt-backed root and first-wave pin tests explicitly for a skip-free focused proof, keeping the full module in the final plain lane.
- 2026-09-29T13:55:37-07:00 — Combat bank-run neighbour selection: `test_module_surface.` includes two environment-dependent Qt/root checks but focused runs require zero skips; cancelled only slice-owned runner PID 83352 while its log contained only the mirror-lock wait. Inventory the seven applicable checks explicitly; Qt/root checks stay in the merged-tree Qt gate.
- 2026-09-29 14:21 PDT: PvM cleanup neighbour selection included `test_root_initializer_is_reported_as_unavailable_without_aqt`, which calls `self.skipTest("root initializer requires aqt; use the offscreen Qt interpreter")`; the fixed runner rejected `Ran 380 tests in 95.534s` / `OK (skipped=1)` with `error: remote focused lane false pass: tests=380, skipped=1; expected exactly 380 tests and no skips`. Exclude both root-initializer tests from this plain focused selection; keep the fixed first-wave module-surface pins.

## 2026-09-29 — zsh refuses assignment to its read-only status parameter — 1 duplicate

Disposition: duplicate (`duplicate`), triaged on 2026-09-29 against main `98eb13f2`. Kept open: papercuts.md entry `2026-09-29T10:50:00-0700`. The earlier new entry remains open: assigning status fails before the command wrapper can preserve its exit. This is distinct from overwriting the writable special path array, so the status entry is not collapsed into that older cause.

- 2026-09-29T11:01:26-0700 — Combat respawn-reset slice: a combined audit wrapper assigned zsh’s read-only `status` parameter after `git diff --check`, ending with `(eval):1: read-only variable: status`; use a neutral name such as `rc` when preserving command exits in zsh.

## 2026-09-29 — Shared mirror-lock waits outlive foreground commands — 2 duplicates

Disposition: duplicate (`duplicate`), triaged on 2026-09-29 against main `98eb13f2`. Kept open: papercuts.md entry `2026-09-24T00:53:15-0700`. The shared runner waits on the same untimed mirror lock. A successful eventual run proves serialization, not removal of the caller-facing foreground timeout or queue delay.

- 2026-09-29T11:21:17-0700 — Combat-state sanitizer cleanup: the remote 46-test Memory Bank reader run waited beyond the Bash 600-second cap and moved to background task `bbkhfttzc`; when the shared mirror lock can exceed the cap, launch the foreground-equivalent runner with `run_in_background` and wait for its completion notification.
- 2026-09-29T13:50:33-0700 — Combat respawn-reset line-neutral verification: after the shared gate logged `gate exit 0`, the neighbour run logged `Remote mirror busy; waiting for /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock`; the runner waited and completed with `Ran 306 tests in 0.072s` / `OK` (`line-neutral-neighbours.log`).

## 2026-09-29 — Whole-module metric exit and capped test inventory — 1 duplicate

Disposition: duplicate (`duplicate`), triaged on 2026-09-29 against main `98eb13f2`. Kept open: papercuts.md entry `2026-09-26T09:52:24-07:00`; papercuts.md entry `2026-09-26T19:57:18-0700`. This compound entry records two independent causes: unchanged over-limit functions make complexipy exit 1, and --list refuses inventories above --max-results. Main now prints Matching tests: N even when refusing the long list, but still refuses that inventory with exit 2 (run_tests.py:177-190).

- 2026-09-29T13:37:31-07:00 — Combat bank-run metrics: complexipy whole-module measurement exited 1 despite `-i` because existing functions exceed its default limit; measure the new helper alone without changing limits. Neighbour listing refused `349 IDs` at its default `--max-results 200`; request 400 for the inventory.

## 2026-09-29 — Broad test listings still hit the print cap — 2 duplicates

Disposition: duplicate (`duplicate`), triaged on 2026-09-29 against main `98eb13f2`. Kept open: papercuts.md entry `2026-09-26T19:57:18-0700`. Commit 28b48067 added a count summary, not an uncapped inventory or a successful count-only mode. The exact refusal remains at run_tests.py:182-188; these entries request the missing IDs or rerun with a larger cap.

- 2026-09-29T14:14:35-0700 — Target-lock neighbor listing returned exit 2 with `Matching tests: 373. Refusing to print the last 173; narrow the selector or pass --max-results 373.` Use an explicit high `--max-results` for broad module selections.
- 2026-09-29T14:21:29-0700 — Finisher-refill baseline listing: `python3 run_tests.py --list test_combat_logic. test_ranged_finisher. test_finisher_families.` exited 2 with `Matching tests: 299. Refusing to print the last 99; narrow the selector or pass --max-results 299.`; reran the collect-only listing with `--max-results 500` before starting the remote baseline.

## 2026-09-29 — complexipy output path is a file, not a new directory — 1 duplicate

Disposition: duplicate (`duplicate`), triaged on 2026-09-29 against main `98eb13f2`. Kept open: papercuts.md entry `2026-09-29T14:12:20-0700`, which names the same mistaken file-versus-directory expectation for complexipy --output. Fixing that expectation also fixes this entry. The keeper is compound; its separate exit-1 part remains represented by papercuts.md entry `2026-09-26T09:52:24-07:00`. Redirecting stdout or relocating the default report/cache in `2026-09-24T05:32:54-0700` would not fix this output-path type error.

- 2026-09-29 14:12 PDT: Installed `complexipy --output` writes the named file, not a directory containing `complexipy-results.json`; reading the presumed child raised `NotADirectoryError: [Errno 20] Not a directory`, so read the named output file directly.

## 2026-09-29 — An optional no-match search stops a required command — 1 duplicate

Disposition: duplicate (`duplicate`), triaged on 2026-09-29 against main `98eb13f2`. Kept open: papercuts.md entry `2026-09-26T19:19:30-07:00`. rg and the older process grep both legitimately exit 1 when no match exists. Chaining the required listing or reader search with && then prevents it from running.

- 2026-09-29T14:14:00-0700 — Target-lock neighbor discovery: `rg` found no skip guards and returned 1, so an `&&` chain never ran the test listing. Keep exploratory searches separate from commands whose execution is required.

## 2026-09-29 — Record appends leave an extra blank line at EOF — 1 duplicate

Disposition: duplicate (`duplicate`), triaged on 2026-09-29 against main `98eb13f2`. Kept open: papercuts.md entry `2026-09-26T09:44:58-0700`. Normalizing one append repaired that record, but the recurring append-formatting cause is still covered by the older open entry.

- 2026-09-29T14:33:57-07:00 — Target-lock completion record: the final audit-output append left an extra blank line, and `git diff --check` returned `memory-bank/progress.md:2989: new blank line at EOF.` Finish generated record appends with exactly one terminal newline.
