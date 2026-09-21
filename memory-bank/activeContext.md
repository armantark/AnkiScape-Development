# Active Context

## Current focus

- This file holds current focus, decision boundaries and the verification contract. Dated entries belong in `memory-bank/progress.md` only.
- The live install under `addons21/ankiscape_fork` is the canonical checkout. All assigned work uses pooled worktrees through `tools/worktree_guard.py`; only the root promotes verified merged trees.
- The owner resumed the implementation goal on 2026-09-21 in Codex task `01a072a4-e63c-7f50-b40c-1381515649f2`. The goal is active. No scheduled restart exists. The [September 21 decisions](handoffs/fable-grill-papercuts-2026-09-21-decisions.md) put handoff steps 1 to 3 first, then the gameplay queue. Step 4 waits for a file split that needs it.
- The separate one-time papercut cleanup has regression evidence and a Fable design handoff in `handoffs/fable-grill-papercuts-2026-09-19.md`. The final canonical-HEAD promotion receipt establishes acceptance; the earlier failed documentation check is retained in `source-audits/papercut-cleanup-2026-09-18/final-verification.md`. This maintenance work does not resume the goal.
- P8 `goal/combat-magic-module-2026-09-18` failed its full source gate and remains unmerged. Preserve it and the dirty P6 predecessor. The owner must choose whether to merge or rework Magic. Do not merge, rebase or rework candidate `a8137bab`; a later step 4 can use it as evidence only.
- Pass 14's encounter and Slayer-completion slices are landed. That hold no longer blocks the orchestrator.
- The guarded native route works and its retained packet has verified integrity. The required shared real-reviewer answer-path pass remains unproven, and the packet does not bind an exact loaded revision. No new native run is authorized by this record.
- Open owner gates are the diary-deed spot-check feedback and the native journal/navigation UI decisions. Missing quest combat stats are source work, not a new gameplay-design question. Other exact source and dependency blockers remain in the matrix.
- Old quota prose is not a live quota result. Menu-open performance remains on `memory-bank/future-work-kanban.md` under its owner target.

Last staleness sweep: 2026-09-21

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
