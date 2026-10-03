# Active Context

## Current focus

- Current main: `da02e004b55f196b60438b4cc24ccdcf6deda5c5` with tracked files clean (2026-10-03). The earlier audited baseline `0a6281292401f62a59804044ff195091559f2623` is history, and a fresh main audit remains necessary. The owner resumed [the exact governing goal](plans/goal-2026-10-03.md). The goal is unfinished. The [priority matrix](goal-priority-matrix.md) governs selection; [pickup-2026-10-03.md](pickup-2026-10-03.md) is the current handoff. The October 1 pickup is historical. Do not promote mixed branches wholesale.
- The owner permits daily pacing overages and directs root to run available quota down to zero, "while still minmaxing the agent work". The banked reset is a pending root action when the actual limit reaches 100%. Actual model and tool hard limits remain binding. Daily pace figures and copied historical quota prose are not live limit readings. The archived [pause evidence](archive/2026-10/handoffs/goal-pause-2026-10-03-evidence.md) does not stop this resumed goal.
- Main includes Equipment digests, the Pass 15 Fletching/cutoff follow-up, Telegrab, evergreen sap, first Boneguard, and potion, finisher, dragonfire and combat Winter Storage cleanups. Four cleanup-required actions still lack emitters: Oronwen trousers, clockwork penguin, Myreque sapphire and Seergaze emerald.
- Root checkpoint: three landings are on current main. The documentation batch landed at `06480995a8fea1bd6716307ea46e0a373c27779e`, normal-runner fairness (S01) at `046d5f53dbec963f52f86b89421b82bea1d4c2f4` and source URL query (S03) at `da02e004b55f196b60438b4cc24ccdcf6deda5c5`, which is current main.
- The four source-accepted cleanups compose candidate `94420078f978c2281144a144857dc805f9042cde`, whose full remote gate is historical. `94420078` is not a descendant of current main, so root must recompose the accepted cleanup heads on current main and obtain a new exact full gate and native acceptance. Native acceptance remains blocked by the locked MacBook, with zero reviews and no preparation or launch. Root waits for the owner to unlock the Mac; no new waiver exists. Root prepared disposable carried, death and composed runtime probes but did not execute them, so no new runtime proof exists. The pickup records the exact error and evidence paths.
- The matrix records the final quest head `c2c37322` with Astra source acceptance plus Kimi substantive verification, final Cache CLI (S12) head `4dc7271d` with Opus source acceptance and a focused remote proof of 39 checks in 27.099s, OK, no skips, the source-accepted carried head `0bbf4aa4` and the source-accepted death head `7e08030e`. For S12 the full branch plain lane passed 5211 tests in 476.735s, OK with 581 skips. The exact merged gate is not run and S12 is not landed. Source acceptance grants no runtime, native or visual permission. These are root checkpoint facts, not execution by this documentation leaf.
- The live install under `addons21/ankiscape_fork` is the canonical checkout. All assigned work uses pooled worktrees through `tools/worktree_guard.py`; only the root promotes verified merged trees.
- The startup budget is under 3,000 lines across `activeContext.md`, `progress.md`, `future-work-kanban.md`, `goal-priority-matrix.md`, `loop-queue.md` and `papercuts.md` ([decision §3.37](design-thread-queue.md)); the loop queue is now archived and contributes no startup lines. Archived files are outside startup discovery; dated records belong in `progress.md` and its monthly archives.
- Progress sections dated before 2026-09-01 are in [the May–August progress archive](archive/progress-2026-05-to-08.md); rotated September 2026 sections are in [the September progress archive](archive/progress-2026-09.md), with the Pass 15 owner notes kept in the current log because they land in October; Kanban cards shipped before 2026-08-24 are in [the shipped-card archive](archive/kanban-shipped-2026.md). No session reads them by default. The matrix authority section holds the monthly rotation rule.
- P8 `goal/combat-magic-module-2026-09-18` failed its full source gate and remains unmerged. Preserve it and the dirty P6 predecessor. The owner must choose whether to merge or rework Magic. Do not merge, rebase or rework candidate `a8137bab`; step 4 used it as evidence only.
- Native acceptance for step 4 passed at `864466ca` in dedicated MacBook task `01a0c67a-3e19-76c2-804c-65d993c9dddc`: reviews, HUD, level-up, bank run, genuine Undo, loaded-source proof and real-app reopen, with the owner collection unchanged. The [native repair summary](source-audits/fable-handoff-2026-09-21/native-relaunch-summary.md) records proof. The per-slice route through the laptop Codex CLI over SSH ([remote test host notes](remote-test-host.md)) failed four times on 2026-09-23 and 2026-09-24 and reviewed 0 cards. The owner's answer to [design-thread queue §3.38](design-thread-queue.md), "Land now, one check later", released only batch `promote/game-2026-09-27b` (the `promote/runtime-batch-2026-09-23` slices plus the later game slices). It landed on main at `279be965` on 2026-09-28 after its full two-lane gate passed; the one remaining step is one in-game check of the whole batch by the owner or task `01a0c67a-3e19-76c2-804c-65d993c9dddc`, and each defect found becomes a fix slice. Every other runtime slice keeps the per-slice check of owner decision 8 and does not land on the failed route. Never run a native check while a gate lane runs, and doorbell the Darkan restoration seat before and after each AnkiScape GUI run on the MacBook.
- Open owner gates (this bullet is the record; [queue audit section 1](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/.orchestrator/tasks-2026-10-02/queue-audit-60d7bd83.md>) is provenance only): the Magic candidate and Dream combat; goal rewrite, sync-save behavior, grave reward values and grave urn policy; unanswered review-log catch-up, export/restore and redo spec questions; Slayer reward earning/reward/UI decisions; Treasure Trails belt spade; Barcrawl card recovery; journal/navigation decisions. Leech effects remain excluded by that audit. Diary-deed spot-check feedback is patch work, not a pre-wiring approval gate. Source and dependency blockers remain in the matrix.
- Root owns quota/reset control, the MacBook mirror, native coordination and promotion. Independent non-runtime work can proceed while native acceptance is blocked. Menu-open performance remains on `memory-bank/future-work-kanban.md` under its owner target.

The October 3 edits are bounded queue reconciliation. No full staleness sweep ran.

Last staleness sweep: 2026-10-01

## Decision Boundaries

- The Darkan repository implements its quests and miniquests, including achievement task hooks; the thread split covers source harvesting only: for every subject, check pins and claims, doorbell, then record a claim before harvesting, with Darkan's 249 revisions already pinned; the one exception Darkan names to "AnkiScape writes no in-game quest code" is AnkiScape's 2026-08-31 `skippy_and_the_mogres` waiver, already used: that miniquest landed at `9b933084` (owner rulings 2026-09-25, [shared source ledger](shared-source-harvest-ledger.md)).
- Live cadence is default-on. Only explicit boolean false takes the
  byte/RNG-identical legacy path.
- Cadence residuals are integer-only per route. Inactive routes freeze, and the
  whole `cadence_profiles` mapping rides the existing review snapshot/undo path.
- `cadence_shadow` is historical instrumentation, separate from live
  `cadence_profiles`, and is never promoted into gameplay state.
- Missing or semantically incompatible rates always remain `source_blocked`.
  Do not substitute modern rates, midpoint a range, decompose the rocktail urn
  quote, map ordinary gold to concentrated gold, or map mixed leaping fish to a
  sturgeon-only rate.
- Full pre-EOC cutoff: `2012-11-20`.
- Do not re-grill Prayer, Magic, Construction, or Farming; their contracts are closed and implemented.
- Do not collapse source IDs 4255 and 6810 into one storage key. The earlier gap-ledger conclusion is superseded by the closure audit.
- Target-carried presence is the activation rule for urns and Prayer passives; bank ownership alone is inert.
- Review undo and direct-inventory-action undo are distinct contracts and must remain independent.
- Each wholly missing skill needs its own deep grill before implementation.
- Dungeoneering must define its temporary session inventory/equipment/reward boundary before any Daemonheim herbs or potions return to a player-facing catalog; see `dungeoneering-product-decision-deferred-2026-07-13.md`.
- Activities/minigames use Utility/Activities at the platform layer, but each family needs its own complete reward/state/source contract.
- Global level-1-to-99 balancing waits until all skills and major methods are present.

## Verification Contract

- Pure/data/unit/integration/end-to-end tests for behavior changes.
- Real offscreen `.venv-qt` tests for UI changes.
- Full `python3 run_tests.py` and full offscreen discovery before feature closure.
- `python3 tools/audit_item_reachability.py --json`, compilation, and `git diff --check` at closure.
- Manual real-profile QA remains an explicit owner checklist when a release candidate should touch the owner's Anki collection.
- Pre/post status artifacts for normal complex work.
