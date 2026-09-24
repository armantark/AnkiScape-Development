# Active Context

## Current focus

- This file holds current focus, decision boundaries and the verification contract. Dated entries belong in `memory-bank/progress.md` only.
- The live install under `addons21/ankiscape_fork` is the canonical checkout. All assigned work uses pooled worktrees through `tools/worktree_guard.py`; only the root promotes verified merged trees.
- The owner resumed the implementation goal on 2026-09-21 in Codex task `01a072a4-e63c-7f50-b40c-1381515649f2`. No scheduled restart exists. The [September 21 decisions](handoffs/fable-grill-papercuts-2026-09-21-decisions.md) set the handoff order to 4, 1, 5, 6, 2, 3, then the gameplay queue. Steps 1 to 5 landed on main: step 1 at `f7c0c7a9`; step 4 at `3d0cae26` (fast-forward, receipt `3d0cae26d28d499338784a1ffe2d1e8e63a9388e.json`, 8 checks); step 2 at `4f345789`; steps 3 and 5, with the design-progress-report skill, at `a45c92d8` (receipt `a45c92d88f7c90160f059653e9fda2bef0154681.json`). Step 3 covers Smithing and Summoning only; Equipment, NPC shops and Construction stay source-blocked. The Grand Exchange fill fix landed at `7e137e73`. Step 6, the Memory Bank rotation, created the archives below and lands with the papercut triage `bf38b68b` in one promotion: its five session-start files total 2,891 lines, and the orchestrator verifies the six-file total under 3,000 on the merged tree ([design-thread queue §3.37](design-thread-queue.md)). The handoff completes on that landing; work then follows the gameplay queue in the [priority matrix](goal-priority-matrix.md).
- Progress sections dated before 2026-09-01 are in [the progress archive](archive/progress-2026-05-to-08.md); Kanban cards shipped before 2026-08-24 are in [the shipped-card archive](archive/kanban-shipped-2026.md). No session reads them by default. The matrix authority section holds the monthly rotation rule.
- The separate one-time papercut cleanup has regression evidence and a Fable design handoff in `handoffs/fable-grill-papercuts-2026-09-19.md`. The final canonical-HEAD promotion receipt establishes acceptance; the earlier failed documentation check is retained in `source-audits/papercut-cleanup-2026-09-18/final-verification.md`. This maintenance work does not resume the goal.
- P8 `goal/combat-magic-module-2026-09-18` failed its full source gate and remains unmerged. Preserve it and the dirty P6 predecessor. The owner must choose whether to merge or rework Magic. Do not merge, rebase or rework candidate `a8137bab`; step 4 used it as evidence only.
- Pass 14's encounter and Slayer-completion slices are landed. That hold no longer blocks the orchestrator.
- Native acceptance for step 4 passed at `864466ca` in dedicated MacBook task `01a0c67a-3e19-76c2-804c-65d993c9dddc`: reviews, HUD, level-up, bank run, genuine Undo, loaded-source proof and real-app reopen, with the owner collection unchanged. The [native repair summary](source-audits/fable-handoff-2026-09-21/native-relaunch-summary.md) records proof. Per-slice native checks now use the laptop Codex CLI over SSH, recorded in [the remote test host notes](remote-test-host.md). Never run a native check while a gate lane runs, and doorbell the Darkan restoration seat before and after each AnkiScape GUI run on the MacBook.
- Open owner gates are the diary-deed spot-check feedback and the native journal/navigation UI decisions. Missing quest combat stats are source work, not a new gameplay-design question. Other exact source and dependency blockers remain in the matrix.
- Old quota prose is not a live quota result. Menu-open performance remains on `memory-bank/future-work-kanban.md` under its owner target.

Last staleness sweep: 2026-09-23

## Decision Boundaries

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
