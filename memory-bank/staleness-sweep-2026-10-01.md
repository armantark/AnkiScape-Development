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
| After | 835 | 2,446 | 18 |

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

These 18 rows stay as written:

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

## Nominations for the owner (not applied)

Each line is a nomination. The owner decides; the sweep applied none of them.

1. `productContext.md:16-22`: the "Experience" section is a status snapshot ("are live foundations", "many rows still require"). Replace it with a pointer to the surface states in `core/skill_registry.py` and to the Kanban.
2. `techContext.md:38` and `systemPatterns.md:551`: "does not yet apply (reproduce) every runtime access gate". Write: "The audit measures declared routes; check runtime access gates before a claim of player acquisition."
3. `techContext.md:209`: "in the current add-on". Write: "The add-on has no runtime package dependency; use `uv` if one becomes necessary."
4. `techContext.md:251`: "whose acquisition loop is not built yet". Delete the clause; the Kanban owns acquisition gaps.
5. `techContext.md:288`: "No runtime cropping helpers exist anymore". Write: "The UI does no runtime cropping."
6. `techContext.md:298`: "rows now use". Delete "now".
7. `techContext.md:306, 320, 332, 338, 350`: five copies of the rule "run provenance fetches one at a time because the current JSON writer is not concurrency-safe". Keep the one rule in `systemPatterns.md` ("Asset provenance writes are serialized") and delete the copies.
8. `techContext.md:172-181`: the "Optional cloud test lane" depends on what the ChatGPT plan includes. Confirm that it still applies, or delete it.
9. `systemPatterns.md:82, 189, 211, 212, 257, 410-413, 420-422, 539, 559, 564`: 15 lines describe a settled pattern with "now" or "still". Delete the time word in each.
10. `systemPatterns.md:533`: "currently including". Write: "Ability gates use stable IDs from the ability registry."
11. `systemPatterns.md:708-723`: the public release section says "missing explicit license" and "verification gate remains open". Write each one as a release requirement.
12. `systemPatterns.md:270-275` and `:281-315`: the world-alert strip and the familiar policies (`Best available`) read as implemented, but the code has no such implementation. Label each passage as contract text.
13. `memory-bank/pending/`: eight `*-papercuts-2026-09-05.md` files hold 63 papercut entries that never reached `papercuts.md`. Merge them into the papercut log, or archive them.
14. `tools/audit_citation_drift.py`: also skip the `pending/*papercuts*` files, because they are papercut entries too. That removes 2 of the 18 remaining rows.
15. Five Darkan source audits (7 rows): put the Darkan commit before each cited path, so the audit finds the commit that holds the lines. The Darkan thread knows which commit each citation meant.
16. Two pins name commits that exist only on branches: `3c05da03` on `goal/secondaries-2026-08-11` and `a8137bab` on `goal/combat-magic-module-2026-09-18`. Add a `refs/preserved/` ref for each, so the pins survive a branch deletion.
17. The October rotation wrote a 113-line block into `archive/progress-2026-09.md` two times. Add a check for repeated sections to the rotation tool or to `tools/audit_docs.py`.
18. The two cape tradeability rows: rewrite the `logic/shop_logic.py` line numbers as the function names `_item_tradeable` and `_sell_price_for_item`, or accept them as history.
