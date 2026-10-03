# Papercuts fixed — 2026-10-02

## Entry 004 — Bounded-context searches must account for the shell wrapper

Disposition: documented.

Evidence: memory-bank/techContext.md:406 records the historical ugrep trap. The review shell resolves /usr/bin/grep (BSD grep 2.6.0-FreeBSD), produces aaa for the reported regex, and has no ugrep command; the current-wrapper assertion is not reproduced. Checked probes: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/review-resolution-probes.json. Both original occurrences remain verbatim.

- 2026-10-01T10:54-07:00 — Staleness sweep: `grep` on this machine is ugrep, and a `.{0,90}` context pattern around a match failed with `ugrep: error: error at position 84 ... exceeds complexity limits`; use `rg -o '.{0,90}PATTERN.{0,90}'` or Python for bounded context.

## Entry 005 — Citation provenance requires a committed tree

Disposition: documented.

Evidence: memory-bank/techContext.md:394. Checked on this tree; host and archive probes are in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/environment-checks.json and /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/archived-packet-checks.json.

- 2026-10-01T10:54-07:00 — Staleness sweep: `tools/audit_citation_drift.py` dates each citation by `git blame`, so editing a record line changes the commit its citation is checked against, and a revert commit hides drift on the reverted lines; re-run the audit only on committed trees.

## Entry 006 — Public wiki requests must use a project User-Agent

Disposition: documented.

Evidence: memory-bank/techContext.md:408 prevents the repeated identity disclosure. tools/audit_quest_historical_wiki_combat_stats.py:29 already uses AnkiScape parity audit. The operator request remains an incident even when project clients use a safe identity.

- 2026-10-01T11:16-07:00 — Pass 15b quest-data slice (GPT-5.6 Sol): one failed RuneScape Wiki request put the owner's injected account email in its public User-Agent; later requests used `AnkiScape parity audit`. Briefs that send agents to curl the wiki must name the User-Agent to use, because agents reach for the only contact string in context.

## Entry 007 — Stacked branches need an explicit start point

Disposition: documented.

Evidence: tools/worktree_guard.py:377 defaults --start-point to main. memory-bank/techContext.md:407 states the repeatable branch-start trap and the plain-merge alternative. The Git refusal is correct, but the brief must match the starting history.

- 2026-10-01 12:45 PDT — Fast-forwarding `goal/pass15b-mogre-gear` to `goal/papercuts-misc` failed because the branches diverged: `fatal: Not possible to fast-forward, aborting.`

## Entry 008 — Checkout correctly protects an uncommitted log

Disposition: record_only.

Evidence: Git refused to overwrite memory-bank/papercuts.md. The refusal protects existing work; the historical stash suggestion is retained only as evidence, not an instruction. memory-bank/techContext.md:400 documents the shared resource.

- 2026-10-01 12:46 PDT — Repointing the feature branch to the prerequisite tip could not preserve the papercut append across checkout: `error: Your local changes to the following files would be overwritten by checkout: memory-bank/papercuts.md`; stash the append before realignment.

## Entry 009 — The source archive has no Git history

Disposition: documented.

Evidence: memory-bank/techContext.md:395. Checked on this tree; host and archive probes are in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/environment-checks.json and /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/archived-packet-checks.json.

- 2026-10-01 12:47 PDT — Checking `game-main` source provenance with `git -C /Users/ArmanTarkhanian1/Downloads/game-main` failed because that cache copy has no `.git`: `fatal: not a git repository (or any of the parent directories): .git`; treat the checked-in source path as cache data, not repository provenance.

## Entry 010 — The agent API correctly refused an unavailable option

Disposition: record_only.

Evidence: The original message explicitly reports a subagent-only API scope refusal and automatic completion notifications. No application code calls SendMessage or notify_when_idle (read-only Python source search); this is an expected tool refusal.

- 2026-10-01 10:10 PDT — While waiting for background research agents, `SendMessage(..., notify_when_idle=true)` failed three times with `notify_when_idle is only available from the main conversation of this session (not from a subagent or teammate).`; background Agent completion notifications are automatic from this subagent context.

## Entry 011 — Tests need an explicit worktree directory

Disposition: documented.

Evidence: memory-bank/techContext.md:396. Checked on this tree; host and archive probes are in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/environment-checks.json and /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/archived-packet-checks.json.

- 2026-10-01 10:12 PDT — A baseline `python -m unittest` command without an explicit worktree `cd` ran from the canonical checkout because agent Bash calls reset to the primary working directory; future worktree tests must set the working directory in the command.

## Entry 012 — The logged jq path is absent

Disposition: documented.

Evidence: memory-bank/techContext.md:397. Checked on this tree; host and archive probes are in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/environment-checks.json and /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/archived-packet-checks.json. The public User-Agent mistake is operator-only, as entry 006 records; project clients were inspected there.

- 2026-10-01 10:15 PDT — A source-verification command failed with `(eval):11: no such file or directory: /opt/homebrew/bin/jq` and also incorrectly placed the injected user email in a public RuneScape Wiki User-Agent; use Python JSON parsing and a generic project User-Agent for external requests.

## Entry 013 — A probe imported a nonexistent export

Disposition: record_only.

Evidence: core/constants.py:42 constructs QUEST_DATA. The probe guessed the data facade export; runtime imports use the constants facade. No missing runtime export is established.

- 2026-10-01 10:23 PDT — The first focused Count Draynor test command failed with `ImportError: cannot import name 'QUEST_DATA' from 'ankiscape.data.quest_data'`; runtime `QUEST_DATA` is exported from `ankiscape.core.constants`.

## Entry 014 — Count Draynor logic no longer grows the large quest module

Disposition: fixed.

Evidence: Ancestor commit 47d76dea extracts quest_combat_modifiers.py; ancestor 05808396 places the shared evaluation in quest_runtime_rules.py. logic_pure/quest_runtime_rules.py:126 owns the evaluator. The refused growth is absent from the landed solution.

- 2026-10-01 10:26 PDT — The first Count Draynor commit failed with `slop-gate: code files above 1000 lines were grown: logic_pure/logic_pure_quest.py: 1594 lines (was 1567)`; the quest-specific modifier had to move to a cohesive `logic_pure` module and existing duplicate imports offset the caller growth.

## Entry 015 — Changed surfaces no longer fail frozen digest pins

Disposition: fixed.

Evidence: Ancestor cd9034ea removes the digest-only assertions from tests/test_module_surface.py. The remaining tests check import/export behavior and normalization, not frozen module digest values.

- 2026-10-01 10:29 PDT — `python -m unittest tests.test_module_surface` failed 9 digest checks after the Count Draynor quest data source changed, including `core/constants.py`, `data/quest_data.py`, `runtime/runtime_actions_carried.py`, `runtime/runtime_actions_activities.py`, and Qt `__init__.py`; the transitive module-surface pins require regeneration with the test-prescribed plain/Qt commands.

## Entry 016 — Fremennik Isles stages now lead to the shield action

Disposition: fixed.

Evidence: Ancestor df52231b repairs the real stage route. tests/test_fremennik_isles_lamps.py:84 rejects generated sentinels; line 111 checks the runtime walk to the round shield. The stage-1 sentinel cause is gone.

- 2026-10-01T10:56:54-0700 — Purchase-proof reachability: the new stage-5 `craft_fremennik_round_shield` action remains unresolved in the whole-catalog closure even with reachable materials, because The Fremennik Isles still stops at its unrelated generated stage-1 `Complete The Fremennik Isles stage 1 objective` sentinel; prove the stage-5 runtime path directly and report the earlier sentinel separately rather than weakening the rites gate.

## Entry 017 — The purchase-proof evaluator landed after spacing and complexity repairs

Disposition: fixed.

Evidence: Ancestor 05808396 is the successful repair after the reported refusal. logic_pure/quest_runtime_rules.py:126 contains the flattened evaluator; runtime/runtime_actions_production.py contains the separated top-level crafting handler. The rejected implementation is not the landed tree.

- 2026-10-01 11:08 PDT — The first purchase-proof commit failed because slop-gate found `runtime/runtime_actions_production.py: E302 x1 (was 0)`, `logic_pure/quest_runtime_rules.py: target_unlock_locked_reasons_pure 21` cyclomatic complexity, and cognitive complexity `33`; restore top-level spacing and flatten the unlock evaluator before retrying.

## Entry 018 — Bounded-context searches must account for the shell wrapper

Disposition: documented.

Evidence: memory-bank/techContext.md:406 records the historical ugrep trap. The review shell resolves /usr/bin/grep (BSD grep 2.6.0-FreeBSD), produces aaa for the reported regex, and has no ugrep command; the current-wrapper assertion is not reproduced. Checked probes: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/review-resolution-probes.json. Both original occurrences remain verbatim.

- 2026-10-01T10:54-07:00 — Staleness sweep: `grep` on this machine is ugrep, and a `.{0,90}` context pattern around a match failed with `ugrep: error: error at position 84 ... exceeds complexity limits`; use `rg -o '.{0,90}PATTERN.{0,90}'` or Python for bounded context.

## Entry 019 — Citation provenance requires a committed tree

Disposition: documented.

Evidence: memory-bank/techContext.md:394. Checked on this tree; host and archive probes are in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/environment-checks.json and /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/archived-packet-checks.json. This repeated record has the same checked disposition as entry 005; both original occurrences are retained.

- 2026-10-01T10:54-07:00 — Staleness sweep: `tools/audit_citation_drift.py` dates each citation by `git blame`, so editing a record line changes the commit its citation is checked against, and a revert commit hides drift on the reverted lines; re-run the audit only on committed trees.

## Entry 020 — Public wiki requests must use a project User-Agent

Disposition: documented.

Evidence: memory-bank/techContext.md:408 prevents the repeated identity disclosure. tools/audit_quest_historical_wiki_combat_stats.py:29 already uses AnkiScape parity audit. The operator request remains an incident even when project clients use a safe identity.

- 2026-10-01T11:16-07:00 — Pass 15b quest-data slice (GPT-5.6 Sol): one failed RuneScape Wiki request put the owner's injected account email in its public User-Agent; later requests used `AnkiScape parity audit`. Briefs that send agents to curl the wiki must name the User-Agent to use, because agents reach for the only contact string in context.

## Entry 021 — Stacked branches need an explicit start point

Disposition: documented.

Evidence: tools/worktree_guard.py:377 defaults --start-point to main. memory-bank/techContext.md:407 states the repeatable branch-start trap and the plain-merge alternative. The Git refusal is correct, but the brief must match the starting history.

- 2026-10-01 12:00:34 PDT — Creating `goal/pass15b-quest-gaps` from current `main` made the required `git merge --ff-only goal/pass15b-quest-data` fail with `fatal: Not possible to fast-forward, aborting.` because `main` had four newer documentation commits; rebased the new branch onto the quest-data slice instead.

## Entry 022 — Quest packets were deliberately retained outside the checkout

Disposition: documented.

Evidence: memory-bank/techContext.md:398. Checked on this tree; host and archive probes are in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/environment-checks.json and /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/archived-packet-checks.json. The SUMMARY manifest contains 17 paths; every retained file exists and matches its SHA-256, including period-sources.json. No evidence file is missing.

- 2026-10-01 12:03:37 PDT — Following `memory-bank/source-audits/genuine-quest-actions-2026-09-05/contract-and-plan.md` to its stated `period-sources.json` evidence failed with `FileNotFoundError: [Errno 2] No such file or directory`; the audit references packet files that are not present beside the committed report.

## Entry 023 — Collection discrepancies need the same checkout

Disposition: documented.

Evidence: memory-bank/techContext.md:396 requires an explicit checkout and comparison of module paths and test IDs. The cited whole-name matching landed in 8f70a917 on 2026-09-27, before this 2026-10-01 incident, so it is not the repair. The retained current collection check agrees at 21 tests, but does not establish the historical cause; wrong-checkout loading remains a hypothesis, supported by entries 011 and 026. Checked history: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/review-resolution-probes.json.

- 2026-10-01 12:07:02 PDT — `run_tests.py --list tests.test_quest_action_proofs` reported `Matching tests: 21`, while `/opt/homebrew/bin/python3 -m unittest tests.test_quest_action_proofs` reported `Ran 20 tests`; focused-count tooling and direct unittest disagree on this module.

## Entry 024 — Ignored research inputs do not populate worktrees

Disposition: documented.

Evidence: memory-bank/techContext.md:399. Checked on this tree; host and archive probes are in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/environment-checks.json and /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/archived-packet-checks.json.

- 2026-10-01 12:10:37 PDT — Inspecting the quest generator cache in the isolated worktree failed with `bfs: error: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/pass15b-quest-gaps/tools/.cache/pre_eoc_quest_catalog: No such file or directory.`; the ignored cache exists only in the canonical checkout.

## Entry 025 — A broad ad hoc search exceeded the output budget

Disposition: record_only.

Evidence: memory-bank/techContext.md:43 already requires bounded search through tools/repo_search.py and exact paths. A broad Arctic pine alternation is a probe choice, not a source or runtime defect.

- 2026-10-01 12:15:45 PDT — Resolving the split-log item with a broad `rg` alternation produced `Output too large (344.2KB)` because the pattern matched every Arctic pine log reference; use an exact output-item probe instead.

## Entry 026 — Tests need an explicit worktree directory

Disposition: documented.

Evidence: memory-bank/techContext.md:396. Checked on this tree; host and archive probes are in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/environment-checks.json and /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/archived-packet-checks.json. The named class now exists at tests/test_fremennik_isles_lamps.py:83.

- 2026-10-01 12:16:56 PDT — Running `python -m unittest tests.test_fremennik_isles_lamps.TestFremennikIslesStageRoute` without changing from the canonical checkout loaded the canonical test module and failed with `AttributeError: module 'tests.test_fremennik_isles_lamps' has no attribute 'TestFremennikIslesStageRoute'`; focused tests must run with the worktree as cwd.

## Entry 027 — A broad item search exceeded the output budget

Disposition: record_only.

Evidence: memory-bank/techContext.md:43 already requires bounded search through tools/repo_search.py and exact paths. A broad Arctic pine alternation is a probe choice, not a source or runtime defect. The jester-costume probe used the same broad-search pattern; no missing item behavior was demonstrated.

- 2026-10-01 12:24:28 PDT — Checking jester costume inventory support with a broad `rg` over `data/` produced `Output too large (169.5KB)` because generated source fragments contain many walkthrough mentions; probe exact item names in generated item values instead.

## Entry 028 — Valid quest proofs no longer hit a pinned total

Disposition: fixed.

Evidence: Ancestor af2e5ca2 removes the total-count assertion. tests/test_quest_action_proofs.py:921 checks action ownership; the 564 != 559 change detector is absent.

- 2026-10-01 12:27:01 PDT — The neighboring proof suite failed after adding five source-backed auto-actions with `AssertionError: 564 != 559`; `tests/test_quest_action_proofs.py` pinned the total action count even though its behavior check already validates unique proof ownership.

## Entry 029 — Changed surfaces no longer fail frozen digest pins

Disposition: fixed.

Evidence: Ancestor cd9034ea removes the digest-only assertions from tests/test_module_surface.py. The remaining tests check import/export behavior and normalization, not frozen module digest values.

- 2026-10-01 12:34:22 PDT — `python -m unittest tests.test_module_surface` failed 9 digest assertions after the prerequisite slice and these quest overlays changed published runtime/catalog data; regenerated the four affected module pins and the Qt root pin with `tools/module_surface.py --digest-only` in both interpreters.

## Entry 031 — The agent API correctly refused an unavailable option

Disposition: record_only.

Evidence: The original message explicitly reports a subagent-only API scope refusal and automatic completion notifications. No application code calls SendMessage or notify_when_idle (read-only Python source search); this is an expected tool refusal.

- 2026-10-01 12:39:58 PDT — Asking the parallel width-fix agent for an idle notification failed with `notify_when_idle is only available from the main conversation of this session (not from a subagent or teammate).`; the queued direct message remains the only handoff path from this subagent.

## Entry 032 — A probe guessed a test class name

Disposition: record_only.

Evidence: tests/quest_catalog/test_literal_mappings.py:51 defines TestLiteralQuestMappings. run_tests.py:74 refuses unknown selectors and provides discovery advice. No missing test class is a product defect.

- 2026-10-01 13:00:41 PDT — The final focused proving command used the guessed class name `TestQuestLiteralMappings` and failed with `AttributeError: module 'tests.quest_catalog.test_literal_mappings' has no attribute 'TestQuestLiteralMappings'`; the existing class is `TestLiteralQuestMappings`.

## Entry 033 — Ignored research inputs do not populate worktrees

Disposition: documented.

Evidence: memory-bank/techContext.md:399. Checked on this tree; host and archive probes are in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/environment-checks.json and /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/archived-packet-checks.json. The tracked evidence directory is memory-bank/source-audits, confirmed by Git file discovery.

- 2026-10-01T10:54:00-07:00 — Quest-stat worktree omitted ignored tools/.cache/pre_eoc_quest_catalog (ls: tools/.cache/pre_eoc_quest_catalog: No such file or directory); copied canonical cached research inputs before generation. The source-audits directory is absent; source evidence lives under memory-bank.

## Entry 034 — The source archive has no Git history

Disposition: documented.

Evidence: memory-bank/techContext.md:395. Checked on this tree; host and archive probes are in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/environment-checks.json and /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/archived-packet-checks.json.

- 2026-10-01T10:59:00-07:00 — Combat source provenance: git log in /Users/ArmanTarkhanian1/Downloads/game-main failed with fatal: not a git repository (or any of the parent directories): .git; this input is an extracted archive, so retain file hashes for the independent corroboration and exact commits for Darkan.

## Entry 035 — Quest regeneration repeats the earlier source-drift cause

Disposition: duplicate.

Evidence: Keep the earliest open regeneration entry, original base papercuts.md:5 (2026-09-30T23:03:30-07:00), now memory-bank/papercuts.md:5. Its quest-source drift remains open in entry 003. The failed ad hoc Bear assertion mixed damage with a kill and respawn; that assertion is not an additional runtime defect.

- 2026-10-01T11:09:00-07:00 — Quest catalog regeneration picked up Darkan source drift in five already-sourced rows; tests.test_quest_catalog raised KeyError: strength because the ranged Lava monster no longer stores a zero strength stub. The live-cadence quest proof must not use the legacy 50-tick fixture: a completed Bear burst returned enemy_lifepoints 221 after consuming the saved 62 LP and respawning, so damage subtraction across a kill is not a valid assertion.

## Entry 036 — The browser endpoint correctly enforced session scope

Disposition: record_only.

Evidence: The original response explicitly states session_scope_forbidden and safeControlledEnvironmentOnly. The same entry records successful tab-scoped proof and native screenshot inspection. This expected endpoint refusal does not establish an add-on defect.

- 2026-10-01T11:19:00-07:00 — Pinchtab opened the isolated local visual proof but instances returned Error 403: {"code":"session_scope_forbidden","details":{"safeControlledEnvironmentOnly":true},"error":"agent session is not allowed to access this endpoint"}; used tab-scoped text and inspected all four native screenshots without requesting a potentially focus-stealing browser screenshot.

## Entry 037 — A source probe assumed the wrong schema

Disposition: record_only.

Evidence: tools/combat/quest_stat_sources.json:30 contains a wiki object; tools/combat/quest_stat_sources.py:12 reads the actual row schema. The entry states that source loading was unaffected; the ad hoc list assumption is not runtime behavior.

- 2026-10-01T11:29:24-07:00 — Quest source-ledger inspection assumed every wiki field was a list; already-sourced rows use an object, so the probe raised TypeError: string indices must be integers, not str. Source loading is unaffected; inspect the row schema before traversing evidence.

## Entry 039 — Historical stat lookup keeps literal pages and scalar fields

Disposition: fixed.

Evidence: Ancestor 69bf80e7 retains the literal cache namespace and repairs parsing. tools/audit_quest_historical_wiki_combat_stats.py:26 separates literal caches; line 85 descends nested templates; line 147 accepts only scalar stat values; lines 236-247 omit modern redirects. tests/test_quest_historical_wiki_combat_stats.py covers nested variants and ambiguous values.

- 2026-10-01T11:41:26-07:00 — Period quest-stat audit followed current MediaWiki redirects: Evil Chicken (Recipe for Disaster) returned noncombat Evil Chicken oldid=6564219 instead of its own combat oldid=6126305 (2012-08-22T15:24:08Z). Nested Switch infobox templates were also skipped, and LP=(Level 3: 67) 53 / 50 / 100 became 3. Fix literal-title queries, nested traversal, and scalar-only stat extraction; isolate literal-response caches.

## Entry 040 — A proof assumed counts where runtime stores a list

Disposition: record_only.

Evidence: logic_pure/logic_pure_quest.py:1312 stores completed encounter IDs as a list and line 1325 normalizes set membership. The failed probe used .items() on that expected representation; no runtime defect is established.

- 2026-10-01T11:49:49-07:00 — New rat fight proof treated quest_combat_encounters as a count dictionary; runtime normalizes completed encounter IDs to a list, so the assertion raised AttributeError: list object has no attribute items. Use the persisted list shape and set inclusion for prior-kill retention.

## Entry 041 — A visual fixture expected more than the designed summary

Disposition: record_only.

Evidence: ui/ui_tab_quests.py:142 deliberately adds +N more after the first blockers. The entry records a fixture adjustment and an unrun chained command, not a failed product behavior or a passing fresh test.

- 2026-10-01T11:51:15-07:00 — Rat visual proof initially expected every encounter in the status label, but Quests shows only the first blockers plus +6 more. Set the fixture to the real post-six-kills state to expose Giant rat level 6; the failed visual command prevented the chained test rerun, leaving the previous test log untouched.

## Entry 042 — Reviewed stat variants use the full quest key

Disposition: fixed.

Evidence: Ancestor 69bf80e7 retains explicit quest_id/display_name/input_level keys. tools/combat/quest_stat_sources.py:14 constructs that tuple; tests/test_pre_eoc_quest_catalog_builder.py:125 rejects leakage to other quests and levels.

- 2026-10-01T11:53:44-07:00 — Source-decision drafting keyed by display name also touched The Path of Glouphrie/Evil creature/1 when only The Eyes of Glouphrie/Evil creature/0 was under review. Restored the unrelated row and changed the decision input to explicit quest_id/display_name/input_level records, matching the ledger loader key.

## Entry 043 — Stashes are shared across linked worktrees

Disposition: documented.

Evidence: memory-bank/techContext.md:400. Checked on this tree; host and archive probes are in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/environment-checks.json and /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/archived-packet-checks.json.

- 2026-10-01 10:30 PDT (pass15b-tool-belt): splitting one dirty file across two commits with `git stash push --keep-index -u` then committing made `git stash pop` conflict ("Recorded preimage for 'tests/test_module_surface.py'", "The stash entry is kept in case you need it again."), and the stash list is shared by every linked worktree, so a stray entry lands beside other agents' stashes; verify a staged-only state with `git checkout-index -a --prefix=<tmpdir>/` instead.

## Entry 044 — Stacked branches need an explicit start point

Disposition: documented.

Evidence: tools/worktree_guard.py:377 defaults --start-point to main. memory-bank/techContext.md:407 states the repeatable branch-start trap and the plain-merge alternative. The Git refusal is correct, but the brief must match the starting history.

- 2026-10-01 11:29 PDT (pass15b-bank-quest-fit): `git merge --ff-only goal/pass15b-tool-belt` in a fresh guard worktree failed with "fatal: Not possible to fast-forward, aborting." because `worktree_guard.py add` cuts from main b3960491, four docs commits past the slice's base b0f410bf; a plain merge commit was needed.

## Entry 045 — Tool icons and names wrap as whole widgets

Disposition: fixed.

Evidence: Ancestor 7fd60fee replaces rich-text tool rows with whole icon/name widgets. ui/ui_flow_layout.py:1 explains the Qt constraint; ui/ui_tool_belt.py builds the chip widgets. The inline-image break no longer affects tool-belt rows.

- 2026-10-01 11:37 PDT (pass15b-bank-quest-fit): a Qt rich-text QLabel breaks the line after every inline `<img>`, so `&nbsp;`, U+2060 word joiner and `white-space: nowrap` all failed to keep a tool belt icon with its name; only separate widgets in a flow layout wrap them together.

## Entry 046 — zsh file lists require arrays

Disposition: documented.

Evidence: memory-bank/techContext.md:401. Checked on this tree; host and archive probes are in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/environment-checks.json and /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/archived-packet-checks.json.

- 2026-10-01 11:59 PDT (pass15b-bank-quest-fit): zsh does not word-split `$F`, so `git diff -- $F` with a space-separated file list wrote an empty patch and `git checkout -- $F` failed with "error: pathspec '... ...' did not match any file(s) known to git"; use a zsh array `F=(a b)`.

## Entry 047 — Saving a Qt option icon requires a value copy

Disposition: documented.

Evidence: memory-bank/techContext.md:409. A fresh PyQt6 probe starts with two non-null icons; clearing opt.icon makes the alias null while QIcon(opt.icon) remains non-null. Retained probe: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/review-resolution-probes.json. The absence of a shipped delegate defect does not remove this repeatable trap.

- 2026-10-01 10:25 Pass 15b prototypes: in PyQt6, `QStyleOptionViewItem.icon` returns a live reference, so `icon = opt.icon; opt.icon = QIcon()` blanks the saved icon too and a custom delegate paints rows with no icon; copy it with `QIcon(opt.icon)` first.

## Entry 049 — Gate verdicts need full output and early static checks

Disposition: documented.

Evidence: memory-bank/techContext.md:402. Checked on this tree; host and archive probes are in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/environment-checks.json and /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/archived-packet-checks.json. The fixed instrument must remain unchanged; the historical ~20-minute rounds are not a new timing measurement.

- 2026-10-01 11:47 PDT (pass15b-quest-fight-card) Committing a ui/ui.py change took three ~20-minute slop-gate runs: the first refused 'ui/ui.py: set_data 67 (was 63)' and 'ui/ui.py: fan-out 165 (was 164)', the second 'E305 x1 (was 0)'; the gate reports one class at a time, so run pycodestyle and count new imports and branches in set_data before the first attempt.

## Entry 050 — Rich labels use rendered size and stacked branches need a start point

Disposition: fixed.

Evidence: Ancestor ad5bbdfd repairs the rich-text probe by using sizeHint() after the word-wrap branch; tests/ui_flows/qt_text_fit.py:58 retains it. The second cause is a repeatable branch-start trap, documented at memory-bank/techContext.md:407, not a Git defect. Checked repair diff: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/review-resolution-probes.json.

- 2026-10-01 12:02 Pass 15b picks: the brief's `git merge --ff-only goal/pass15b-quest-fight-card` failed ('fatal: Not possible to fast-forward, aborting.') because worktree_guard add starts the branch at current main b3960491 while that slice branched from b0f410bf; a plain merge was needed. Also tests/ui_flows/qt_text_fit.py measured rich-text labels as raw markup, so an <img> label reads as clipped unless it gets a sizeHint check placed after the word-wrap branch.

## Entry 051 — The commit gate correctly refused increased complexity

Disposition: record_only.

Evidence: The original entry records an expected slop-gate refusal whose verdict the operator truncated with tail. memory-bank/techContext.md:402 requires full verdict retention and preflight checks; this triage does not change the fixed gate.

- 2026-10-01 10:40 pass15b-shops-guide-clips: `git commit` was refused by slop-gate with its reason cut off by my own `| tail -5` (ui_tab_shop.py grew 15 lines, build_shop_tab complexity 628 to 630); running `git add` then `python3 /Users/ArmanTarkhanian1/fleet/config/git/hooks/slop_gate.py` shows the full verdict without committing (about 2 minutes).

## Entry 052 — Wrapping layouts no longer make the Skills parent rigid

Disposition: fixed.

Evidence: Ancestor 91f5d42b repairs the narrow Skills layout. ui/ui_text_fit.py:6 states that its row layouts do not use heightForWidth; these rows size from the last allocated width instead. The unrelated whole-widget toolbelt flow is a different layout.

- 2026-10-01 10:50 pass15b-shops-guide-clips: a nested QLayout with hasHeightForWidth() true makes its whole parent widget rigid in a vertical QBoxLayout (the Agility target list shrank to its hfw height and squeezed the check boxes above it, offscreen probe showed the check box at 20 px instead of 34); wrap-on-narrow layouts here report no heightForWidth and size from the last width instead (ui/ui_text_fit.py).

## Entry 053 — zsh must not expand literal option patterns

Disposition: documented.

Evidence: memory-bank/techContext.md:403. Checked on this tree; host and archive probes are in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/environment-checks.json and /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/archived-packet-checks.json.

- 2026-10-01 10:46 pass15b-shops-guide-clips: `grep -rn x --include=*.py .` fails in zsh with `no matches found: --include=*.py` unless the glob is quoted ('--include=*.py').

## Entry 054 — The pyflakes shim points at a removed interpreter

Disposition: documented.

Evidence: memory-bank/techContext.md:404. Checked on this tree; host and archive probes are in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/environment-checks.json and /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/archived-packet-checks.json. The shim shebang and missing interpreter were checked without installing a package or changing the host.

- 2026-10-01 14:01 PDT — Integration static check: `/opt/homebrew/bin/pyflakes` printed only `bad interpreter: /opt/homebrew/opt/python@3.12/bin/python3.12: no such file or directory` on stderr, so a grep over its output read as a clean undefined-name check; `uvx pyflakes` works and found a real FlowLayout name clash in ui/ui.py.

## Entry 056 — The reported routing mismatch is absent from the live configuration

Disposition: record_only.

Evidence: The current /Users/ArmanTarkhanian1/fleet/skills/variants/model-routing/rubric.md:17 names gpt-6.1-sol@high. /Users/ArmanTarkhanian1/.local/state/cliproxyapi/config.yaml:36-38 lists legacy models under oauth-excluded-models, not active providers. The historical operator dispatch is retained; no live AnkiScape defect follows from those excluded names.

- 2026-10-01T14:41-07:00 — Pass 15b orchestration dispatched 8 agents to GPT-5.6 Sol because ~/fleet/skills/variants/model-routing/rubric.md line 18 still scores gpt-5.6-sol@high and the session environment names it for cheap bounded coding; the owner ruled 2026-10-01 14:40 that GPT-6.1 Sol replaces GPT-5.6 Sol and Astra is reserved for review. ~/.local/state/cliproxyapi/config.yaml still lists gpt-5.6-sol, -luna, -terra and their -fast twins (12 lines).

## Entry 057 — Use the actual runner and bounded exact-path reads

Disposition: documented.

Evidence: memory-bank/techContext.md:405. Checked on this tree; host and archive probes are in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/environment-checks.json and /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/archived-packet-checks.json.

- 2026-10-02 papercut triage — The requested count command names tools/run_tests.py, but this tree has only root run_tests.py; an initial broad read also exceeded the tool output budget, and guessed tests/test_quest_cleanup_emitters.py and ui/ui_tab_slayer.py paths were absent. Use the root runner and discover exact paths before bounded reads.

## Entry 058 — zsh must not expand literal path patterns

Disposition: documented.

Evidence: memory-bank/techContext.md:403. Checked on this tree; host and archive probes are in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/environment-checks.json and /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/archived-packet-checks.json.

- 2026-10-02 papercut triage — A read-only rg command used unquoted memory-bank/source-audits/genuine-quest-actions-2026-09-05/README* and zsh refused it with no matches found before rg ran; discover filenames with rg --files instead of an unmatched shell glob.

## Entry 059 — The shared remote mirror correctly serialized test launches

Disposition: record_only.

Evidence: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-papercut-triage-2026-10-02/remote-tests.log retains the mirror-busy result. tools/run_remote_tests.py:657-662 waits for the shared lock before sync and launch; this is expected resource contention, not a test or add-on defect.

- 2026-10-02T17:45:49-07:00 — The docs-focused remote runner reported Remote mirror busy; waiting without a deadline for /Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.lock. --timeout starts after launch; run this command as a background task. The shared mirror lock delayed launch; no test had failed.

## Entry 060 — Review probes need bounded reads and exact paths

Disposition: record_only.

Evidence: memory-bank/techContext.md:403-405 already requires literal-pattern quoting, exact file discovery and bounded reads. The corrected review used Python path checks and bounded reads; no application defect follows.

- 2026-10-02 review resolution — Reading the memory-bank files in one tool result exceeded the output budget; use bounded per-file reads before reviewing evidence.

## Entry 061 — Review probes need bounded reads and exact paths

Disposition: record_only.

Evidence: memory-bank/techContext.md:403-405 already requires literal-pattern quoting, exact file discovery and bounded reads. The corrected review used Python path checks and bounded reads; no application defect follows.

- 2026-10-02 review resolution — A source read used an unquoted /Users/ArmanTarkhanian1/fleet/config/shell/*.zsh glob; zsh returned no matches found before rg ran. Use exact paths discovered with rg --files or Python path checks.

## Entry 062 — Remote selections require repeated flags

Disposition: record_only.

Evidence: tools/run_remote_tests.py:683 uses argparse action=append and requires one --select per selector. The corrected command repeats the flag; the initial refusal launched no remote lane. review-resolution-remote-tests.log retains the refusal and corrected run.

- 2026-10-02 review resolution — The remote docs command passed two separate values to --select; argparse refused tests.memory_bank_tools with unrecognized arguments. run_remote_tests.py requires one --select flag per selector.
# Papercuts fixed — 2026-10-02

## Quest catalog generation reads only retained inputs — 2026-10-02

Disposition: fixed.

Evidence: `tools/build_pre_eoc_quest_catalog.py` reads checked-in `tools/generation/quest_sources.json.gz` and the reviewed quest-specific stat ledger. Both rebuilds exit 0 with no catalog diff. The regression reproduces the checked-in bytes with missing emulator roots and denied network. Equipment generation already reproduces its file; the control rebuild also exits 0 with an exact byte comparison. Raw command logs and input/output hashes are retained under the assigned `.git/ankiscape-promotion-evidence/goal-quest-catalog-reproducible-2026-10-02/` directory.

- 2026-09-30T23:03:30-07:00 — Pass 15 S4 equipment regeneration: `python3 tools/generate_equipment_data.py` does not reproduce the checked-in `data/equipment_data.py` (it drops the hand-added `Steel spear (kp)` and adds `Mudskipper hat`, `Flippers` and six `Brawling gloves (*)` rows), and `python3 tools/build_pre_eoc_quest_catalog.py` rewrites unrelated Darkan-derived combat stats in `generated/quest_catalog_generated.py`; both outputs were spliced so only this slice's rows and category fields changed (goal-priority-matrix Handoff 3 records the equipment drift).

## Quest source refresh review

- 2026-10-02T19:28:09-07:00 — Quest review commit refused: slop-gate reported _load_local_npc_stats cyclomatic 16/cognitive 34, _load_darkan_npc_stats cognitive 16, parse_2011scape_journals cognitive 20, trim_manifest cognitive 16, builder 2440 lines (was 2422), and tools 150 code files (was 149); queued focused snapshot was cancelled before sync after these code changes. The gate remained unchanged. Resolved in 64dc7372: cohesive generation modules, flat parser control flow, unchanged gate.
- 2026-10-02T19:31:23-07:00 — The next pre-commit attempt reported `tools/build_pre_eoc_quest_catalog.py: E303 x1 (was 0)` and `tools/generation/refresh_quest_sources.py: E303 x3 (was 0)`; removed the four extra blank lines. Commit 64dc7372 passed without changing the hook.

## Quest mirror provenance and verification

- 2026-10-02T19:38:27-07:00 — Read-only quest verification queue inspection treated tools.run_remote_tests._ssh as a CompletedProcess and raised `AttributeError: 'str' object has no attribute 'stdout'`; the helper returns stdout text directly. No remote state changed. Resolved: canonical NPC and journal paths precede formatting in 8858f7d1 and 144f081d; the SSH helper result is used as text. The unchanged MacBook regression passed in plain-1790998782-f42118f5.
- 2026-10-02T20:02:31-07:00 — MacBook quest review focused run plain-1790996389-287a99ea failed test_rebuild_is_exact_without_external_sources_or_network at tests/test_pre_eoc_quest_catalog_builder.py:45: `Ran 49 tests in 1.576s`, `FAILED (failures=1)`, `error: remote plain lane failed with exit 1`; expanding NPC pin paths against mirror roots before pprint changed wrapping before canonical replacement. Exact assertion output is in review-remote-focused-accepted.log in the quest slice promotion-evidence folder. No baseline or test assertion changed. Resolved: canonical NPC and journal paths precede formatting in 8858f7d1 and 144f081d; the SSH helper result is used as text. The unchanged MacBook regression passed in plain-1790998782-f42118f5.
- 2026-10-02T20:12:39-07:00 — Quest refresh canary with emulator-root aliases `game with spaces` and `world with spaces` exited 1 with `RuntimeError: Refreshed sources do not reproduce --check-catalog; pin was not written`; journal provenance still came from a mirror root before pprint. Exact output: review-mirror-spaces-before.log in the quest slice promotion-evidence folder. Resolved: canonical NPC and journal paths precede formatting in 8858f7d1 and 144f081d; the SSH helper result is used as text. The unchanged MacBook regression passed in plain-1790998782-f42118f5.

## Quest refresh review controls

Disposition: fixed.

Evidence: Verification retains complete tool results and persisted logs. The named transport request function passes the unchanged slop gate. Evidence: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-quest-catalog-reproducible-2026-10-02/review2-preflight.log.

- 2026-10-02 — Quest review verification: a tool wrapper printed only command output and lost the background session handle; subsequent checks capture the complete tool result and persist logs.
- 2026-10-02 — Quest review preflight: slop-gate refused `tools/generation/refresh_quest_sources.py: WikiSources::read 20 (was 13)` with `cognitive complexity above 15 was introduced`; transport retries now have a separate named request function, with the unchanged gate pending.
# Papercuts fixed — 2026-10-02

## Telegrab pins approved by the orchestrator

Disposition: fixed.

Evidence: Orchestrator ruling 2026-10-02 18:51 permits action_count 1671 → 1672, reachable_item_count 2354 → 2355, and Magic count 114 → 115; the repository pin assertions are updated and audit_item_reachability.py --check exits 0.

- 2026-10-02T18:39:38-07:00 — Telegrab emitter verification: `tests/test_magic.py:186` in `test_three_books_and_stable_ids_are_complete` pins 114 Magic targets; the new ancestral-key target produces `AssertionError: 115 != 114` in the remote 229-test selection. Fixed-instrument rules prohibit this author from re-pinning it; the orchestrator must resolve it alongside `action_count: expected 1671, observed 1672` and `reachable_item_count: expected 2354, observed 2355`.

## Quest review tests use the quest package

Disposition: fixed.

Evidence: Move the unchanged test blob 93d442d7057a5aa37db5cd89896f2ce2e8a0095b from tests/test_quest_telegrab.py to tests/quest_catalog/test_quest_telegrab.py. The root no longer gains a code file; discovery still collects 229 selected tests and 5161 total tests.

- 2026-10-02T20:16:56-07:00 — Telegrab branch commit refused by slop-gate: `slop-gate: code files were added to directories already at 40 files:` / `tests: 237 code files (was 236)` / `-> Create a cohesive subdirectory instead of widening this directory.` The new test is relocated without content changes to `tests/quest_catalog/test_quest_telegrab.py`; verification and a fresh commit attempt follow.
# Papercuts fixed — 2026-10-02

## Evergreen sap authoring gates

Disposition: fixed.

Evidence: The redundant retained-tool branch was removed: core/tool_belt.py always supplies Knife and every live Utility row has no retained tool outside that belt. logic_pure/logic_pure_production.py is byte-identical to HEAD. The unchanged tests moved into the existing tests/quest_catalog/ package, preserving the root file count. Evidence: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-quest-sap-emitter-2026-10-02/hook-fix-equivalence.log.

- 2026-10-02T20:45:12-07:00 — Evergreen sap commit: slop-gate refused `utility_activity_locked_reasons_pure` at cyclomatic complexity `17 (was 15)` and cognitive complexity `20 (was 19)`, plus `tests: 237 code files (was 236)` under the 40-file directory cap; raw output: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-quest-sap-emitter-2026-10-02/commit.log`.
