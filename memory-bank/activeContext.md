# Active Context

## Current focus

- This file holds current focus, decision boundaries and the verification contract. Dated entries belong in `memory-bank/progress.md` only.
- The live install under `addons21/ankiscape_fork` is the canonical checkout. All assigned work uses pooled worktrees through `tools/worktree_guard.py`; only the root promotes verified merged trees.
- The owner resumed the implementation goal on 2026-09-21 in Codex task `01a072a4-e63c-7f50-b40c-1381515649f2`. No scheduled restart exists. The [September 21 decisions](handoffs/fable-grill-papercuts-2026-09-21-decisions.md) set the handoff order to 4, 1, 5, 6, 2, 3, then the gameplay queue. All six steps are on main, so the handoff is complete: step 1 at `f7c0c7a9`; step 4 at `3d0cae26` (fast-forward, receipt `3d0cae26d28d499338784a1ffe2d1e8e63a9388e.json`, 8 checks); step 2 at `4f345789`; steps 3 and 5, with the design-progress-report skill, at `a45c92d8` (receipt `a45c92d88f7c90160f059653e9fda2bef0154681.json`); step 6, the Memory Bank rotation that created the archives below, with the papercut triage `bf38b68b` in docs batch `db75276f` (receipt SHA-256 `4599b98d491a398718242b310969bc73e723662ba3a940d67284e19161668d41`). Step 3 covers Smithing and Summoning only; Equipment, NPC shops and Construction stay source-blocked. The Grand Exchange fill fix landed at `7e137e73`. Step 6 met its under-3,000 target with 2,990 session-start lines on its own merged tree ([design-thread queue §3.37](design-thread-queue.md)); later progress sections raised the six files to 3,045 lines at `db75276f` and 3,141 at `d0904603`, which is later growth for the monthly rotation, not a failed acceptance. Work follows the gameplay queue in the [priority matrix](goal-priority-matrix.md).
- Progress sections dated before 2026-09-01 are in [the May–August progress archive](archive/progress-2026-05-to-08.md); rotated September 2026 sections are in [the September progress archive](archive/progress-2026-09.md), with the Pass 15 owner notes kept in the current log because they land in October; Kanban cards shipped before 2026-08-24 are in [the shipped-card archive](archive/kanban-shipped-2026.md). No session reads them by default. The matrix authority section holds the monthly rotation rule.
- The separate one-time papercut cleanup has regression evidence and a Fable design handoff in `handoffs/fable-grill-papercuts-2026-09-19.md`. The final canonical-HEAD promotion receipt establishes acceptance; the earlier failed documentation check is retained in `source-audits/papercut-cleanup-2026-09-18/final-verification.md`. This maintenance work does not resume the goal.
- P8 `goal/combat-magic-module-2026-09-18` failed its full source gate and remains unmerged. Preserve it and the dirty P6 predecessor. The owner must choose whether to merge or rework Magic. Do not merge, rebase or rework candidate `a8137bab`; step 4 used it as evidence only.
- Pass 14's encounter and Slayer-completion slices are landed. That hold no longer blocks the orchestrator.
- Native acceptance for step 4 passed at `864466ca` in dedicated MacBook task `01a0c67a-3e19-76c2-804c-65d993c9dddc`: reviews, HUD, level-up, bank run, genuine Undo, loaded-source proof and real-app reopen, with the owner collection unchanged. The [native repair summary](source-audits/fable-handoff-2026-09-21/native-relaunch-summary.md) records proof. The per-slice route through the laptop Codex CLI over SSH ([remote test host notes](remote-test-host.md)) failed four times on 2026-09-23 and 2026-09-24 and reviewed 0 cards. The owner's answer to [design-thread queue §3.38](design-thread-queue.md), "Land now, one check later", released only batch `promote/game-2026-09-27b` (the `promote/runtime-batch-2026-09-23` slices plus the later game slices). It landed on main at `279be965` on 2026-09-28 after its full two-lane gate passed; the one remaining step is one in-game check of the whole batch by the owner or task `01a0c67a-3e19-76c2-804c-65d993c9dddc`, and each defect found becomes a fix slice. Every other runtime slice keeps the per-slice check of owner decision 8 and does not land on the failed route. Never run a native check while a gate lane runs, and doorbell the Darkan restoration seat before and after each AnkiScape GUI run on the MacBook.
- Open owner gates are the grave reward values ([design-thread queue §3.40](design-thread-queue.md): lamp, bag and book values do not record which copy holds which value, and `nonempty_urn_count_pure` ignores urns in a grave), for which `goal/grave-reward-values-2026-09-27` stays uncommitted until the owner answers; the Magic candidate above; the diary-deed spot-check feedback; and the native journal/navigation UI decisions. Missing quest combat stats are source work, not a new gameplay-design question. Other exact source and dependency blockers remain in the matrix.
- Old quota prose is not a live quota result. Menu-open performance remains on `memory-bank/future-work-kanban.md` under its owner target.

Last staleness sweep: 2026-09-23

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
