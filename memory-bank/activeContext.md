# Active Context

## Current focus

- Audited main baseline: `60d7bd83` (2026-10-02). The goal remains open. The [priority matrix](goal-priority-matrix.md) governs selection; the newest `pickup-*.md` (currently [pickup-2026-10-01.md](pickup-2026-10-01.md)) is the latest handoff, whose mixed branches must not be promoted wholesale.
- The live install under `addons21/ankiscape_fork` is the canonical checkout. All assigned work uses pooled worktrees through `tools/worktree_guard.py`; only the root promotes verified merged trees.
- The startup budget is under 3,000 lines across `activeContext.md`, `progress.md`, `future-work-kanban.md`, `goal-priority-matrix.md`, `loop-queue.md` and `papercuts.md` ([decision §3.37](design-thread-queue.md)); the loop queue is now archived and contributes no startup lines. Archived files are outside startup discovery; dated records belong in `progress.md` and its monthly archives.
- Progress sections dated before 2026-09-01 are in [the May–August progress archive](archive/progress-2026-05-to-08.md); rotated September 2026 sections are in [the September progress archive](archive/progress-2026-09.md), with the Pass 15 owner notes kept in the current log because they land in October; Kanban cards shipped before 2026-08-24 are in [the shipped-card archive](archive/kanban-shipped-2026.md). No session reads them by default. The matrix authority section holds the monthly rotation rule.
- P8 `goal/combat-magic-module-2026-09-18` failed its full source gate and remains unmerged. Preserve it and the dirty P6 predecessor. The owner must choose whether to merge or rework Magic. Do not merge, rebase or rework candidate `a8137bab`; step 4 used it as evidence only.
- Native acceptance for step 4 passed at `864466ca` in dedicated MacBook task `01a0c67a-3e19-76c2-804c-65d993c9dddc`: reviews, HUD, level-up, bank run, genuine Undo, loaded-source proof and real-app reopen, with the owner collection unchanged. The [native repair summary](source-audits/fable-handoff-2026-09-21/native-relaunch-summary.md) records proof. The per-slice route through the laptop Codex CLI over SSH ([remote test host notes](remote-test-host.md)) failed four times on 2026-09-23 and 2026-09-24 and reviewed 0 cards. The owner's answer to [design-thread queue §3.38](design-thread-queue.md), "Land now, one check later", released only batch `promote/game-2026-09-27b` (the `promote/runtime-batch-2026-09-23` slices plus the later game slices). It landed on main at `279be965` on 2026-09-28 after its full two-lane gate passed; the one remaining step is one in-game check of the whole batch by the owner or task `01a0c67a-3e19-76c2-804c-65d993c9dddc`, and each defect found becomes a fix slice. Every other runtime slice keeps the per-slice check of owner decision 8 and does not land on the failed route. Never run a native check while a gate lane runs, and doorbell the Darkan restoration seat before and after each AnkiScape GUI run on the MacBook.
- Open owner gates (this bullet is the record; [queue audit section 1](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/.orchestrator/tasks-2026-10-02/queue-audit-60d7bd83.md>) is provenance only): the Magic candidate and Dream combat; goal rewrite, sync-save behavior, grave reward values and grave urn policy; unanswered review-log catch-up, export/restore and redo spec questions; Slayer reward earning/reward/UI decisions; Treasure Trails belt spade; Barcrawl card recovery; journal/navigation decisions. Leech effects remain excluded by that audit. Diary-deed spot-check feedback is patch work, not a pre-wiring approval gate. Source and dependency blockers remain in the matrix.
- Old quota prose is not a live quota result. Menu-open performance remains on `memory-bank/future-work-kanban.md` under its owner target.

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
