# Staleness sweep — 2026-10-01

The previous sweep was on 2026-09-23. This sweep starts from main at `dd788d72` on branch `goal/staleness-sweep-2026-10-01`. The sweep obeys the "Dated sweep" procedure of the `cline-rules` skill.

## Method

1. The sweep ran `tools/audit_citation_drift.py` first and fixed its actionable rows.
2. Three read-only checkers (GPT-6.1 Sol) checked the claims in the core files. The sweep ran a command for each reported claim before it changed the text.
3. The sweep did the three steps that `jev-fit-decision-2026-09-23.md` assigns to it.
4. The sweep listed point-in-time phrases in the durable files as nominations. It did not apply them.

## Citation drift

The audit counts a citation as actionable when its cited lines moved, or when its file or lines no longer exist.

| Run | Markdown files | Citations | Actionable |
| --- | --- | --- | --- |
| Before, with the audit on main | 839 | 2,922 | 735 |
| After the first pass | 835 | 2,474 | 18 |
| After the applied nominations | 827 | 2,470 | 8 |

The two counts do not measure the same set. Three audit changes on this branch removed rows that were not drift:

- 84 rows cited Darkan files such as `data/npcs/drops/blue_dragon.json`. The audit called them local files because this repository also has a `data/` directory. Commit `8779da17` resolves them against the Darkan sources.
- 120 rows were in `papercuts.md` and the `papercuts-fixed-*.md` logs. `move_papercuts.py check` keeps each papercut line verbatim, so nobody can repoint them. Commit `07f76ac5` removes these logs from the audit scan.
- Commit `e3da75f9` makes the audit skip a citation with a commit prefix, such as `a468d18a:memory-bank/design-thread-queue.md:1698`. A file at a fixed commit cannot move.

The new tool `tools/memory_bank/fix_citation_drift.py` did the mechanical work. `systemPatterns.md` now gives the procedure.

- It moved 338 citations to the lines where the audit found the same text.
- It traced 68 citations to code that moved into split modules, for example from `data/quest_data.py` into `data/quest/`.
- It pinned 74 citations to code that no longer exists, as `<sha>:path:line`. The pin names the commit that held the cited lines.
- The tool also changed 94 citations in the papercut logs. Commit `9c893380` put those logs back to their text on main, and `move_papercuts.py check dd788d72` passes.
- The sweep fixed 34 more citations by hand in commit `9c0650b3`.
- The sweep repointed 10 more citations that moved when this sweep added three Kanban cards and corrected `systemPatterns.md`.
- A check found that all 56 distinct pins resolve with `git cat-file -e`. One pinned range ran past the end of its file and now ends at line 1498.

After the first pass, these 18 rows stayed as written. The applied nominations below fixed 10 of them: the 2 staged papercut rows, 6 of the 7 Darkan rows, and the 2 cape tradeability rows.

- 2 rows in `archive/progress-2026-09.md` cite lines 11 and 12 of `GOAL-BLOCKED.md`. That file was never committed.
- 1 row in `audits/papercut-remediation-2026-08-09.md` cites a line range in an uncommitted snapshot of the papercut log.
- 2 rows in `handoffs/design-to-impl-rulings-2026-08-13.md` quote the bad worktree-guard citation that ruling 52.1 retracts.
- 2 rows in `pending/*-papercuts-2026-09-05.md` are verbatim papercut entries that quote `git diff --check` output.
- 7 rows in five Darkan source audits cite Darkan files. The audit takes the commit from prose above the citation, and that commit does not hold the cited lines.
- 2 rows in the cape tradeability records cite `logic/shop_logic.py` line numbers from an implementation branch that is not in this repository.
- 1 row in `papercut-cleanup-2026-09-18/guard-review.md` cites a Codex memory file outside this repository.
- 1 row in `resume-queue-reconciliation-2026-09-18/GOAL-BLOCKED-2026-09-17.md` is a verbatim copy of an old blocker file.

## Claims in the core files

| File | Claims rewritten | Example |
| --- | --- | --- |
| `activeContext.md` | 0 | All six handoff SHAs, `279be965`, `9b933084`, and the unmerged `a8137bab` agree with `git merge-base --is-ancestor`. |
| `progress.md` | 0 | `231cdd1a` is on main; the equipment count 1,049 and the 90 quest encounters without stats agree with a census. |
| `projectbrief.md` | 1 | The gap backlog line (Jev step 3). |
| `productContext.md` | 0 | 19 complete skill surfaces agree with `core/skill_registry.py`. |
| `systemPatterns.md` | 18 | Magic was listed as a partial skill; `core/skill_registry.py` gives it a complete surface. |
| `techContext.md` | 13 | Quest repairs were batched by line distance in `data/quest_data.py`, which is a re-export facade since `5c87ba05`. |
| `future-work-kanban.md` head | 0 | The `__init__.py:5501` answer citation is correct. |
| `goal-priority-matrix.md` head | 1 | Keep/Drop settlement got its own step at `6f0f0a03`. |

The `systemPatterns.md` rewrites:

1. Eight lines named `logic_pure/logic_pure.py` or `data/quest_data.py` as the owner of code. Both files are re-export facades; the lines name the `logic_pure_*` modules and the `data/quest/` package.
2. The review strip has five seats that `_sync_review_strip_layout()` selects by width, not three fixed seats.
3. Skills get their XP curve from `exp_table_for_skill()`; Dungeoneering has its own table.
4. `_build_target_selector()` picks the flat or grouped renderer from the row count and the groups, not from a fixed skill list.
5. The Activities column has separate routes for the master tree, Minigames, and D&D. It has no previous and next pager.
6. Magic has a complete review surface. Only Attack, Strength, Defence, Constitution, and Ranged are partial.
7. The Stronghold of Player Safety is a source-backed landmark inside `UTILITY_ACTIVITY_DATA`. The step-counter landmarks stay outside it.
8. Dungeon Herblore chains run against the Dungeoneering session inventory.
9. `magic_melee`, ranged, and magic enemy attacks have their own bonus paths.
10. The Summoning altar and obelisk detour is contract text. The runtime has only the `Visit obelisk` command, which restores Summoning points.

The `techContext.md` rewrites:

1. The quest batching rule now says that each parallel writer gets a different module under `data/quest/`. The dated incident history stays.
2. Rune Mysteries is in `data/quest/definitions/free/rune_mysteries.py`, and the Wicked hood claim is in `data/quest/ledger.py`.
3. Woodcutting, Firemaking, and Runecrafting logic is in `logic_pure_gathering.py`, `logic_pure_production.py`, and `logic_pure_runecrafting.py`. `logic_pure/logic_pure.py` only re-exports. These are three rewrites.
4. The focused-test example takes its count from `python3 run_tests.py --count`. The file has 32 tests, not 19.
5. Every skill icon is period highscores art, as `assets_provenance.json` records. The old text said to use the wiki "(detail)" variant.
6. The Firemaking, Runecrafting, and Herblore icon lines name their highscores files. These are three rewrites.
7. The Herblore line does not give a count. The count was 113; the catalog has 119 rows.
8. Activity icons come from the RuneScape Wiki, not the OSRS wiki.
9. Commit `3e4a5cb2` removed the hard-coded review link, so the public release rule no longer asks for its removal.

## Jev follow-up

`gap-backlog.json` last changed on 2026-08-28. It has 45 rows; 24 say `merged`.

1. The Kanban parity ledger now names the owning card for each of the 21 other rows.
2. Four rows had no card. Three new parity-ledger cards cover them: Runecrafting route selection with the Abyss, the Herblore work left after Overload, and Barbarian Firemaking bow lighting.
3. The README, the roadmap, the project brief, and three Kanban lines now call the backlog a closed historical record. The two lines in `archive/progress-2026-09.md` stay as written, because they are dated records.

## Pruned

- The October rotation wrote a 113-line block into `archive/progress-2026-09.md` two times. Lines 2031 to 2143 were the same as lines 1584 to 1696. The sweep removed the second copy.

## Applied on 2026-10-01

The owner ruled on 2026-10-01 that the sweep applies the wording changes itself. The sweep applied 17 of the 18 nominations; it left nomination 13 to the orchestrator.

1. `productContext.md`: the "Experience" section now points at `core/skill_registry.py` for surface states and at the Kanban for quest fidelity work. The section no longer lists live surfaces.
2. `techContext.md` and `systemPatterns.md`: the reachability lines say that the audit measures declared routes, and that a claim of player acquisition needs a check of runtime access gates.
3. `techContext.md`: the package line says that the add-on has no runtime package dependency.
4. `techContext.md`: the Crafting line sends acquisition gaps to the Kanban.
5. `techContext.md`: the cropping line says that the UI does no runtime cropping.
6. `techContext.md`: the activity-icon line has no "now".
7. `techContext.md`: the five copies of the provenance rule are gone. One sentence in "Asset Scraping (icons)" points at the rule in `systemPatterns.md`.
8. `techContext.md`: the "Optional cloud test lane" stays unchanged. Its first sentence already limits it to a plan that includes the lane.
9. `systemPatterns.md`: 17 lines lost "now", "still", or "right now". The sweep found two more such lines than it nominated.
10. `systemPatterns.md`: the ability-gate line gives its two IDs as examples, without "currently".
11. `systemPatterns.md`: the public release section states the license, acknowledgement, provenance, and gate requirements.
12. `systemPatterns.md`: the world-alert strip bullet and the four familiar-policy bullets say that they are contract text, and that the runtime has no such implementation.
13. Not applied. The orchestrator triages the papercut entries in `memory-bank/pending/` separately.
14. `tools/audit_citation_drift.py` leaves the staged `pending/*papercuts*.md` files out of its scan (commit `4ee5b037`).
15. Six of the seven Darkan citations now name, on their own line, the Darkan commit where `git show` holds the cited lines (commit `9d96e45d`). The sweep skipped the `Cooking.java` citation in the bonfire audit, because its named commit `d52f13c99` does not resolve in `darkan-world-server`, `darkan-client`, `darkan-cache`, or this repository.
16. `refs/preserved/combat-magic-module-2026-09-18` holds `a8137bab`, and `refs/preserved/secondaries-handoff-2026-08-11` holds `3c05da03`. `tools/worktree_guard.py preserved list` shows both, and the matrix's preserved table records them (commit `cb33b83a`).
17. `tools/audit_docs.py` reports `repeated_progress_section` when a progress log repeats a `## ` section word for word (commit `f751964f`). `tests/memory_bank_tools/test_progress_rotation_audit.py` covers it, and `tests/memory_bank_tools/test_fix_citation_drift.py` covers the citation fixer (commit `5b4b1d1a`).
18. The cape tradeability records name `_item_tradeable` and `_sell_price_for_item`, which have since moved to `logic/shop/state.py` (commit `6d5340ff`).

These 8 rows stay as written:

- 2 rows in `archive/progress-2026-09.md` cite lines of `GOAL-BLOCKED.md`, which was never committed.
- 1 row in `audits/papercut-remediation-2026-08-09.md` cites a line range in an uncommitted snapshot of the papercut log.
- 2 rows in `handoffs/design-to-impl-rulings-2026-08-13.md` quote the bad worktree-guard citation that ruling 52.1 retracts.
- 1 row in the bonfire source audit cites `Cooking.java` at a commit that does not resolve.
- 1 row in `papercut-cleanup-2026-09-18/guard-review.md` cites a Codex memory file outside this repository.
- 1 row in `resume-queue-reconciliation-2026-09-18/GOAL-BLOCKED-2026-09-17.md` is a verbatim copy of an old blocker file.
