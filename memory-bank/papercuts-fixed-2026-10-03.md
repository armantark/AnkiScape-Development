# Papercuts fixed — 2026-10-03

## Crafting requests now use period art and the audit identity

Disposition: fixed.

Evidence: Main ancestor ac2b1aeb changes tools/fetch_crafting_assets.py:176-179 to HttpWikiClient(user_agent="AnkiScape parity audit", before_timestamp=PRE_EOC_CUTOFF). tools/fetch_assets.py:45 defines 2012-11-19T23:59:59Z. tests/test_fetch_assets.py:120 names the period-art/release-day behavior check. The checked command has a fixed identity rather than a configurable User-Agent option; the unbounded client cause is removed.

- 2026-10-01 14:01 PDT — Fetching the Fremennik round shield icon: `tools/fetch_crafting_assets.py` builds `HttpWikiClient()` without `before_timestamp`, so it saved the 2026-08-24 wiki revision (sha1 a02a2405...); passing `before_timestamp=PRE_EOC_CUTOFF` gave the 2010-03-26 revision. The script also has no User-Agent option.

## Read-only instructions do not enforce filesystem isolation

Disposition: documented.

Evidence: memory-bank/techContext.md:410 records the write-barrier constraint. The supplied environment grants unrestricted filesystem tools, and a brief cannot remove that access. The recorded accidental edit and restoration remain incident evidence; this is an operator isolation fact, not a claimed source-code repair.

- 2026-10-02T18:10-07:00 — Test-prune classification workflow (GPT-6.1 Sol classifiers, read-only by instruction, cwd = canonical checkout): at 17:48:54 an agent deleted `self.assertEqual(len(required_ids), 82)` from tests/test_farming_skill_guide.py in the canonical checkout; the orchestrator restored the file from HEAD. Workflow agents get write tools in the session cwd, so a read-only instruction alone does not keep them out of the live add-on; point read-only fan-out at a disposable snapshot worktree.

## Local inventory uses the root runner and positional selectors

Disposition: documented.

Evidence: memory-bank/techContext.md:411 records the exact command shape; README-tests.md:37-67 and the successful current count command confirm root run_tests.py. memory-bank/techContext.md:399 records ignored caches, which linked worktrees do not inherit. The absent tools/run_tests.py and optional docs/adr paths are invalid assumptions, not missing required repository files.

- 2026-10-02T17:35:54-07:00 — Carried-overlay sixth slice: the brief count command `python3 tools/run_tests.py --count` failed with `[Errno 2] No such file or directory`; the fixed instrument is root `run_tests.py`, whose selectors are positional (`--select` is remote-runner-only). Ring mould is always on the tool belt at base `60d7bd83`.
- 2026-10-02T17:35:04-07:00 | menu-dispatch cleanup inventory: the brief names `python3 tools/run_tests.py --count`, but `tools/run_tests.py` is absent at base `60d7bd835c77b08f7040c67c77db4da7a233e648`; `README-tests.md` names the existing root `run_tests.py`.
- 2026-10-02T17:33:11-07:00 — Shared alchemy slice startup: the supplied count path `tools/run_tests.py` returned `No such file or directory`; the tracked runner is `run_tests.py` at the repository root. Startup inventory also queried absent `docs/adr` and returned `rg: docs/adr: No such file or directory (os error 2)`.
- 2026-10-02T17:52:35-07:00 — Quest catalog source inspection: the requested `python3 tools/run_tests.py --count` path does not exist; section 1 and the repository use `python3 run_tests.py --count`. The assigned worktree has no ignored `tools/.cache/pre_eoc_quest_catalog`; retained inputs are read from the canonical cache without changing it.

## Second mirror-fixture subprocess warning

Disposition: duplicate.

Evidence: Same warning class and same checked mirror-fixture cleanup gap as the earliest retained open occurrence, 2026-10-02T21:36:58-07:00 (original papercuts.md line 12). That exact occurrence remains open. The two original logs are preserved; tests/promotion/test_remote_mirror_lock.py:147-148 still kills without reaping. No repair is claimed.

- 2026-10-02T22:58:23-07:00: The mirror-lock review local fixtures passed but emitted `ResourceWarning: subprocess 31795 is still running` from `/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/subprocess.py:1139`; raw output `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-gate-mirror-priority-2026-10-02/review-lock-local.log`.

## Plain package probes need Anki runtime fakes first

Disposition: documented.

Evidence: memory-bank/techContext.md:412 records the setup contract. tests/test_integration_smoke.py:45 installs aqt and anki hooks into sys.modules; :78-91 loads the package without installing those modules. The standalone omission is not a package-loader defect.

- 2026-10-02T17:47:14-07:00 | menu-dispatch differential startup: `_load_addon_as_package` needs `_install_runtime_fakes()` first in a standalone plain script; omission raised `ModuleNotFoundError: No module named 'aqt'`. The disposable harness now installs the existing runtime fakes before loading either function.

## Ordinary mirror queue waits are expected serialization

Disposition: documented.

Evidence: memory-bank/techContext.md:413 records the serialized mirror and untimed wait. tools/run_remote_tests.py:650-677 prints the recorded notice and then performs blocking admission or mirror acquisition. d6f2e09a reserves promotion-gate admission, not FIFO order among normal runners. These entries record ordinary contention only; the distinct overtaking observation at 2026-10-02T19:26:23-07:00 stays open.

- 2026-10-02T19:10:38-07:00: Equipment review-fix focused remote proof queued on the shared mirror: `Remote mirror busy; waiting without a deadline for /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock. --timeout starts after launch; run this command as a background task.`
- 2026-10-02T19:33:42-07:00 — Dragonfire cleanup baseline: `tools/run_remote_tests.py` waited on the shared mirror before execution: `Remote mirror busy; waiting without a deadline for /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock. --timeout starts after launch; run this command as a background task.`
- 2026-10-03T02:48:29.766230+00:00 — Finisher-consumption baseline: `tools/run_remote_tests.py` PID `22252` remained queued at measured elapsed `17:43`; emitted `Remote mirror busy; waiting without a deadline for /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock. --timeout starts after launch; run this command as a background task.` Evidence: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-combat-finisher-consume-2026-10-02/focused-before.log`.
- 2026-10-02T17:36:26-07:00 — Full plain alchemy verification briefly reported `Remote mirror busy; waiting without a deadline for /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock.`; the runner acquired the shared lock and launched `plain-1790987757-33849a59` without intervention.
- 2026-10-02T17:52:57-07:00 — Final Pass 15b plain and Qt lanes: `Remote mirror busy; waiting without a deadline for /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock.` The runner captured the source snapshot before the wait; left the shared lock intact.
- 2026-10-03T02:57:57.340406+00:00: Both full MacBook lane invocations waited for shared mirror ownership: "Remote mirror busy; waiting without a deadline for /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock. --timeout starts after launch; run this command as a background task." Keep the existing invocation and its captured snapshot.
- 2026-10-03T03:46:56.249787+00:00: Pass 15b final plain invocation is queued on the existing mirror lock: "Remote mirror busy; waiting without a deadline for /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock. --timeout starts after launch; run this command as a background task." Preserve this invocation and its committed code snapshot.
- 2026-10-03T04:22:01.457302+00:00: Pass 15b final qt invocation also reports "Remote mirror busy; waiting without a deadline for /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock." Keep the existing invocation; its full output is captured at /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/pass15b-logic-followups/review-finish/full-qt.log.
- 2026-10-02T19:19:10-07:00 — Quest review focused verification queued at the shared MacBook mirror: `Remote mirror busy; waiting without a deadline for /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock. --timeout starts after launch; run this command as a background task.` No mirror lock or foreign run was changed.
- 2026-10-03T05:05:43+00:00 — Quest review MacBook acceptance: the focused runner remains queued through successive shared plain and Qt lanes; exact message: `Remote mirror busy; waiting without a deadline for /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock. --timeout starts after launch; run this command as a background task.` Source snapshot is preserved; no mirror or lane was interrupted.
- 2026-10-02T23:02:23-07:00 — Quest retry review remote inventory: `Remote mirror busy; waiting without a deadline for /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock. --timeout starts after launch; run this command as a background task.` The runner preserves its launch snapshot while queued.
- 2026-10-02T22:17:04-07:00 — Telegrab review follow-up: the remote `plain --collect-only --select test_quest_telegrab` inventory remained queued on `/Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock` while other full lanes ran; the runner reported `Remote mirror busy; waiting without a deadline`; evidence `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-quest-telegrab-emitter-2026-10-02/review-red-inventory-04tdn6mg.log`.
- 2026-10-02T22:19:51-07:00 — Stage-5 sentinel verification queued across shared runs `qt-1791003209-2a6e7115`, `qt-1791003920-fb193bcd`, then `plain-1791004739-ed914082`; the evidence wrapper now retains the official mirror lock from red proof through cleanup-ready and the serial green lanes, so implementation does not incur a second queue wait.

## A subagent requested a main-conversation-only notification

Disposition: record_only.

Evidence: Main ancestor ac2b1aeb retains this exact incident in memory-bank/papercuts.md. The message itself describes an expected capability refusal; no AnkiScape caller supplies or implements notify_when_idle. The failed request does not establish an add-on defect.

- 2026-10-01 14:26 PDT — Tried to subscribe to background agent completion from a subagent; `notify_when_idle is only available from the main conversation of this session (not from a subagent or teammate).`

## Exact-edit input did not match the source

Disposition: record_only.

Evidence: The incident records a successful narrow re-read after String to replace not found in file. The checked tree no longer relies on the removed adjacent wrappers, and ac2b1aeb contains the runtime follow-up cleanup. An edit-tool match refusal is expected; no runtime defect is established by this occurrence.

- 2026-10-01 14:30 PDT — Deleting adjacent legacy wrappers with an exact Edit failed because the source has no blank line between functions; `String to replace not found in file.` required a narrow re-read.

## A source lookup guessed paths before inventory

Disposition: record_only.

Evidence: The current inventory contains split runtime/runtime_actions_*.py and tests/ui_flows/*.py modules. The incident records recovery with the actual directory listing. No required path is named as absent; this is an invalid lookup, not a source defect.

- 2026-10-01 14:42 PDT — Resuming logic follow-ups: guessed test/runtime paths returned `No such file or directory`; located the actual split modules and ui_flows tests with directory listing before further reads.

## A regression expected dictionary shape instead of behavior

Disposition: record_only.

Evidence: tests/runtime_actions/test_belt_moulds.py:47-57 checks the missing Long kebbit spike through its quantity, absent output and absent XP, matching the stated intended refusal. A zero-count Bank entry is not consumed input or a crafted output. The failed dictionary-shape expectation is a harness assumption, not a game defect.

- 2026-10-01 14:48 PDT — Fletching runtime regression expected an unchanged empty inventory, but carried overlay reconciles missing recipe inputs as zero-count Bank entries (`{'Long kebbit spike': 0}`); check no consumed input, output or XP instead of dictionary shape.

## A widget probe assumed the wrong selector class

Disposition: record_only.

Evidence: ui/ui.py:5640-5649 uses build_searchable_target_selector, and memory-bank/systemPatterns.md:22-28 records the row-count-dependent QListWidget/QTreeWidget contract. A probe must inspect the current selector and Artisan panel; the reported NoneType lookup is not evidence that the actual selector fails.

- 2026-10-01 14:56 PDT — Real Fletching widget check initially used `QListWidget` from the parallel flat-list follow-up and failed with `AttributeError: 'NoneType' object has no attribute 'count'`; this branch still uses the grouped `QTreeWidget`, so use its existing test helpers and select the Artisan panel explicitly.

## The shared cutoff now excludes EOC release-day art

Disposition: fixed.

Evidence: Main ancestor ac2b1aeb changes tools/fetch_assets.py:45 to 2012-11-19T23:59:59Z. tests/test_fetch_assets.py:57 names the actual TestFetchAssets class, and :120 contains the Crafting period-art check. The wrong class lookup was an expected refusal; the release-day cutoff cause is removed.

- 2026-10-01 15:03 PDT — Asset regression invocation guessed `FetchAssetsTests` and returned `AttributeError: module 'tests.test_fetch_assets' has no attribute 'FetchAssetsTests'`; ran the existing focused module instead. The command test also revealed that shared `PRE_EOC_CUTOFF = "2012-11-20T23:59:59Z"` included release-day art, so its expected cutoff now names the last second before 2012-11-20.

## The task-waiter canary rejected an unsupported context manager

Disposition: record_only.

Evidence: README-tests.md:80-89 explicitly describes the standalone select.kqueue context-manager failure. The incident records the contextlib.closing repair in the disposable canary. This is an expected Python API refusal outside the add-on runtime, not an unresolved repository defect.

- 2026-10-01T15:20:40-07:00: A read-only task-waiter canary raised `TypeError: 'select.kqueue' object does not support the context manager protocol (missed __exit__ method)`; use `contextlib.closing(select.kqueue())` and gate the live invocation with shell fail-fast.

## zsh refused unmatched unquoted globs

Disposition: record_only.

Evidence: memory-bank/techContext.md:401,403 records zsh scalar and glob expansion rules. The checked file inventory uses rg --files and literal patterns. These are expected shell refusals of optional guessed paths; no missing required module is established.

- 2026-10-02T17:34:19-07:00 — Shared alchemy slice inspection: shell-expanded `tests/test_*boundar*` stopped the search with `zsh: no matches found: tests/test_*boundar*`; use quoted ripgrep globs for test inventory.
- 2026-10-02T17:50:06-07:00 — Pass 15b failure diagnosis: optional shell globs (`tools/test*`, `tools/slop*`, `tests/test_source_audit*`, `tools/slop_gate*`) caused `zsh: no matches found`; use `rg --files` for optional paths. `tempfile.mkdtemp()` initially placed disposable copies under `/var/folders`; moved the copies to `/tmp/pass15b-diagnosis-emr0sp1z` and reran all four comparisons there.
- 2026-10-02T18:17:38-0700 — Quest tooling source inspection: unquoted shell globs failed in zsh with `zsh:1: no matches found: tools/build*equipment*` and `zsh:1: no matches found: tools/docs*`; source discovery uses `rg --files tools` instead.

## The focused runner correctly refused a guessed test count

Disposition: record_only.

Evidence: tools/run_remote_tests.py:731-735 requires exact expected_tests and zero skips. README-tests.md:49-67 documents collection before launch. The recorded 139 versus Matching tests: 137 mismatch is an intended safety stop, not a runner defect.

- 2026-10-02T17:34:49-07:00 — Shared alchemy remote focused plain launch transcribed `--expected-tests 139` before reading the completed local count (`Matching tests: 137`); preserve the rejection and rerun with the measured 137, without changing tests or runner checks.

## A mixed source lookup used absent paths and invalid request shape

Disposition: record_only.

Evidence: tools/build_pre_eoc_quest_catalog.py:82 names npcList.txt; the tracked tree has no AGENTS.md or required period-sources.json at the guessed locations. The recorded MediaWiki invalidparammix and unmatched glob are expected input refusals. The retained source extractor uses individual cached wiki requests; no add-on defect is established by this combined lookup.

- 2026-10-03T02:11:18.769175+00:00: Review-source lookup hit missing AGENTS.md, a missing audit period-sources.json, a zsh unmatched glob, and MediaWiki invalidparammix: rvstart/rvlimit require one page; split the Tool belt/Shades requests.

## The cutoff migration spacing defects are repaired

Disposition: fixed.

Evidence: Main ancestor ac2b1aeb contains the cutoff migration and spacing repair. A fresh unchanged pycodestyle --select E303 check of tools/fetch_achievement_diary_assets.py, tools/fetch_crafting_assets.py and tools/fetch_assets.py returned exit 0 with no output. The shared PRE_EOC_CUTOFF remains imported by the fetchers.

- 2026-10-03T02:15:16.974186+00:00: Shared cutoff migration left excess blank lines; commit hook refused with "slop-gate: PEP 8 layout violations were introduced" / E303. Restore spacing; handle bare fetch_assets imports as well as tools.fetch_assets imports.
- 2026-10-02: Cutoff spacing repair missed a comment before DIARY_REWARD_ITEMS; hook refused tools/fetch_achievement_diary_assets.py: E303 x1 (was 0). Remove the remaining excess blank line.

## The passing offscreen lane emitted Qt diagnostics

Disposition: record_only.

Evidence: run_tests.py:190-199 installs the offscreen modal guard and Sans Serif to Arial substitution; that substitution predates this incident (db14782b). The incident records font-alias cost and propagateSizeHints diagnostics without a failed test or visible defect. No new add-on defect is established, and no claim that the diagnostics are fixed is made.

- 2026-10-03T03:14:16.163486+00:00: Full MacBook Qt output includes `qt.qpa.fonts: Populating font family aliases took 95 ms. Replace uses of missing font family "Sans Serif" with one that exists to avoid this cost.` and repeated `This plugin does not support propagateSizeHints()`; preserve the lane output and wait for its final summary.

## A passing Qt lane emitted a Chromium mailbox diagnostic

Disposition: record_only.

Evidence: The original entry names a passing full Qt lane and preserves the exact Chromium diagnostic. ui/ui.py uses native Qt surfaces and the lane also loads QtWebEngine; the diagnostic alone gives no failing add-on action or persistent reproduction. Retain the original evidence without claiming a GPU or runtime repair.

- 2026-10-03T03:25:52.152180+00:00: The passing full Qt lane emitted this Chromium diagnostic: `[80899:121149256:1002/201808.405706:ERROR:../../../qtwebengine/src/3rdparty/chromium/gpu/command_buffer/service/shared_image/shared_image_manager.cc:389] SharedImageManager::ProduceSkia: Trying to Produce a Skia representation from a non-existent mailbox.`. Full output is retained in `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/pass15b-logic-followups/review-fixes/full-qt.log`; no test instrument was changed.

## The line-growth cap correctly refused a commit

Disposition: record_only.

Evidence: The incident gives the exact three files and before/after counts. ac2b1aeb subsequently lands the follow-up source through the enforced gate. The refusal is an intended cap result; the triage does not weaken the cap or claim the refusal was a defect.

- 2026-10-03T03:32:18.068581+00:00: Final review-fix commit refused: "slop-gate: code files above 1000 lines were grown:"; runtime/runtime_actions_production.py 1442 (was 1439), tests/test_runtime_actions.py 5917 (was 5916), tools/generate_equipment_data.py 1415 (was 1413). Exact output is in `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/pass15b-logic-followups/review-fixes/final-commit-blocker.txt`; stop with remaining fixes staged.

## A source read exceeded the tool output budget

Disposition: record_only.

Evidence: The recorded Warning: truncated output follows overly broad file reads. tools/repo_search.py and memory-bank/techContext.md:42-47 supply bounded source discovery. This triage used bounded source ranges in checked-tree-evidence.log and exact-entry comparisons. Tool-output truncation of a broad inspection is not an add-on defect.

- 2026-10-03T03:44:54.329328+00:00: Pass 15b finish inspection batched core memory-bank reads with diffs and exceeded the tool output budget ("Warning: truncated output"); switched to bounded reads and exact file comparisons before editing.
- 2026-10-02T19:15:32-07:00 — Quest pin review inspection batched whole files and a 1,045-response manifest, causing `Warning: truncated output`; use AST-selected functions and manifest summaries for this slice.
- 2026-10-02T23:08:53-07:00 — Quest retry follow-up: combined core-bank and repository reads exceeded the tool output budget (`Warning: truncated output`); subsequent reads use bounded, task-specific sections.
- 2026-10-03T09:11:53Z — Papercut triage startup: batched reads exceeded the tool budget ("Warning: truncated output"), and assumed tests/test_audit_docs.py, tools/remote_tests/mirror_lock.py and ui/skill_panels/magic* paths were absent; use bounded reads and rg --files before exact paths.

## The two invalid review status pages no longer exist

Disposition: fixed.

Evidence: Main ancestor 3e0f4fe9 deletes memory-bank/status-updates/pass15b-review-fixes-plan-2026-10-02.html and pass15b-review-fixes-results-2026-10-02.html. Both paths are absent on this tree. The current python3 tools/audit_docs.py baseline passes; no missing-final-newline cause remains at either path.

- 2026-10-03T03:45:26.718381+00:00: Pass 15b finish documentation audit reported missing_final_newline at memory-bank/status-updates/pass15b-review-fixes-plan-2026-10-02.html:1 and memory-bank/status-updates/pass15b-review-fixes-results-2026-10-02.html:7; added terminal newlines only, with no publication.

## The owner of a queued verification cancelled before launch

Disposition: record_only.

Evidence: tools/run_remote_tests.py snapshots source before synchronization, as README-tests.md:73-77 records. The original incident explicitly states Sync: not started, Test execution: not started and EXIT CODE: -2. Cancellation to include a later documentation edit is an intended interruption, not a remote execution failure.

- 2026-10-02T18:22:18-07:00 — Quest tooling verification: a documentation edit followed the queued full-plain snapshot; cancelled that owned runner while `Sync: not started` and `Test execution: not started`, then completed the notes before taking the final snapshot. The cancelled log reports `KeyboardInterrupt` and `EXIT CODE: -2`; no remote lane launched.

## Quest-refresh inspection guessed obsolete paths

Disposition: record_only.

Evidence: The tracked refresh tests are tests/quest_catalog/test_source_refresh.py, whose TestQuestSourceRefresh class was read. No tracked root AGENTS.md exists. The reported missing-path errors and broad-read truncation are lookup mistakes, not missing required test coverage.

- 2026-10-02T23:01:04-07:00 — Quest retry review startup: assumed paths failed with `cat: AGENTS.md: No such file or directory` and `rg: tests/test_quest_source_refresh.py: No such file or directory (os error 2)`; the refresh tests are `tests/quest_catalog/test_source_refresh.py`. Broad memory-bank listing also truncated output; use named core files and task-specific records.

## Quest retry classification no longer increases the request function complexity

Disposition: fixed.

Evidence: Main ancestor 9bc4479c includes tools/generation/refresh_quest_sources.py:236-258: _is_retryable_wiki_error owns retry classification and request_wiki_payload calls that predicate. tests/quest_catalog/test_source_refresh.py:31-63 checks transient and permanent errors. This is the checked repair of the recorded request_wiki_payload 18 (was 10) cause, not a gate relaxation.

- 2026-10-02T23:13:26-07:00 — Quest retry follow-up commit refused: `slop-gate: cognitive complexity above 15 was introduced: tools/generation/refresh_quest_sources.py: request_wiki_payload 18 (was 10)`; moved retry classification into a predicate without changing the allowlist.

## An interrupted runner had no completed result

Disposition: record_only.

Evidence: The incident records an API capacity or network stop, no EXIT CODE and no live owned runner. tools/run_remote_tests.py:1-7 distinguishes pending coordination from completed result evidence. A retained incomplete log and a new exact-count launch are recovery from an external interruption; no persistent add-on defect is established.

- 2026-10-03T00:35:42-07:00 — Quest retry acceptance resumed after an API capacity or network stop: review4-final-remote-focused.log ends at the shared mirror lock wait with no EXIT CODE and no live runner for this worktree; restarted the focused run with --expected-tests 53, preserving the incomplete log and all foreign runners.

## The asset audit writes a tracked report unless redirected

Disposition: documented.

Evidence: memory-bank/techContext.md:414 records the stable default write behavior. tools/audit_asset_cutoff.py:39-44 chooses the tracked report, :619 exposes --report, and :532 writes the report. The successful audit rewriting that report is expected CLI behavior, not an audit corruption defect.

- 2026-10-02T22:19:17-07:00 — Telegrab review follow-up: `python3 tools/audit_asset_cutoff.py` passed but rewrote its default tracked report `memory-bank/source-audits/post-cutoff-asset-revisions-2026-08-21.json` (389 additions, 3389 deletions); restored that incidental report from HEAD, kept the audit log, and use `--report` with an evidence path to avoid changing the source-audit record.

## A period sprite exists on a different source wiki

Disposition: documented.

Evidence: memory-bank/techContext.md:415 records the source-specific availability. assets_provenance.json:31288-31300 retains the first-Boneguard sprite from runescape.fandom.com at 2011-11-19T16:05:24Z with the exact original SHA-1. tools/fetch_navigation_icons.py:143-169 only queries RS3_WIKI and correctly refuses a missing revision there. The unsupported parameter in that function remains a separate open cause.

- 2026-10-02T18:46:38-07:00 — First-Boneguard spell asset: `tools.fetch_navigation_icons.period_image_info` returned `No revision at or before 2012-11-20T23:59:59Z for Crumble Undead icon.png`; the existing legacy-period source resolves the sprite at `2011-11-19T16:05:24Z`.

## The preflight correctly rejected added complexity and test-file fanout

Disposition: record_only.

Evidence: Main ancestor 91cf104a includes the completed first-Boneguard source and focused tests/runtime_actions/test_quest_crumble_undead.py. tests/test_quest_action_proofs.py no longer lists that action as un-emitted. The reported metric/fanout refusal was an intended gate result; moving domain gates and the focused module repairs the candidate without changing the instruments.

- 2026-10-02T20:02:51-07:00 — First-Boneguard preflight: `slop-gate` rejected `apply_magic_action_pure` cyclomatic 71 (was 70), cognitive 95 (was 93); `magic_target_locked_reasons_pure` cyclomatic 29 (was 24), cognitive 33 (was 27); `tests` 237 code files (was 236). The prior slice had not run the preflight; domain gating and a table now preserve dispatcher complexity, and the focused module is under `tests/runtime_actions/`.

## An evidence lookup guessed alternate module paths

Disposition: record_only.

Evidence: The checked rg --files inventory contains logic_pure/quest_action_proofs.py, runtime/runtime_actions_carried_overlay.py and tests/test_combat_logic.py; the three guessed alternate locations are absent. These are invalid lookup assumptions, not missing required source files.

- 2026-10-03T09:21:01Z — Papercut triage evidence lookup: guessed runtime/carried_overlay, tests/combat/test_combat_logic.py and logic/quest_action_proofs.py paths returned No such file or directory; the tracked proof helper is logic_pure/quest_action_proofs.py, and the root combat tests are tests/test_combat_logic.py.

## A summary counted dictionary insertion order instead of source identity

Disposition: record_only.

Evidence: The base log has exactly original lines 3 through 65. triage-decisions.json now sorts decisions by original source-line identity; the base counter filters line <= 65 and the verification asserts the exact original entry multiset. The mistaken intermediate counts never became a committed report; this was summary assembly friction, not an add-on defect.

- 2026-10-03T09:26:27Z — Papercut triage summary assembly: dictionary insertion order mixed the first 63 decision rows with a new incident and omitted original line 64, reporting open 10 and record_only 25 instead of open 11 and record_only 24; count by original source-line identity and assert complete coverage.

## The docs verifier waited for the serialized mirror

Disposition: documented.

Evidence: memory-bank/techContext.md:413 documents the untimed serialized mirror wait; tools/run_remote_tests.py:674 blocks before yielding ownership to sync. remote-tests-before-friction.log ends with KeyboardInterrupt at that flock, so the stopped owned invocation did not synchronize or launch a test lane. Exit 130 came from the local runner. No foreign process or lock was changed. The same outstanding contention on the final snapshot does not create a second incident.

- 2026-10-03T09:31:30Z — Papercut triage MacBook docs verification: owned runner PID 13256 queued on the shared mirror with Remote mirror busy; waiting without a deadline for /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock. --timeout starts after launch; run this command as a background task.; stopped only that queued invocation before sync to include this incident in the final documentation snapshot, preserving its KeyboardInterrupt log and exit 130.

## Review evidence lookup used absent paths and an oversized read

Disposition: record_only.

Evidence: The failed lookups were operator path assumptions, not required missing project files. Bounded reads of existing paths supplied the review evidence; no source repair is claimed.

- 2026-10-03T03:21:30-07:00 — Review-fix evidence lookup queried absent AGENTS.md, .githooks and /tmp/p15b/pass15b-logic-followups/review-fixes, and an absent memory-bank/status-updates/pass15* path; combined source reads exceeded the tool output budget. Use existing paths and bounded reads; no repository defect is established.
