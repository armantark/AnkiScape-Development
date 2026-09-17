# Active Context

## Current focus — 2026-09-16

- This file holds the current focus, the decision boundaries, and the verification contract. Every dated entry lives in `memory-bank/progress.md` only, newest first; `tools/audit_docs.py` rejects a dated heading here. `tools/memory_bank/merge_memory_logs.py` performed the 2026-09-16 move.
- Main is `8283ad9d`, clean. The live Anki install under `addons21/ankiscape_fork` is the canonical checkout; all work runs in pooled worktrees through `tools/worktree_guard.py`.
- Pass 14 rulings are in `memory-bank/design-thread-queue.md` §4.27. The Codex brief `memory-bank/codex-briefs/pass14-owner-notes-handoff-2026-09-13.md` holds two slices, `encounter-no-lock` and `slayer-complete-dialog`. Both slices landed on main in `a6622434` and `641f6608` on 2026-09-16. The orchestrator thread is no longer blocked on Pass 14.
- Open owner gates: the spot-check of the 162 rewritten diary deeds and the 91 stat-less quest encounters (Pass 13, §4.25); native programme acceptance for the 2026-09-05 to 2026-09-08 cleanup batch (`memory-bank/goal-priority-matrix.md`).
- Parked: the papercut triage-and-fix pass (1,192 entries) until the Codex block resets; menu open time on `memory-bank/future-work-kanban.md` with a 300 ms target.
- Landed since the 2026-08-31 sweep: Pass 13 batch `f018c832` and diary sentence rewrite `d89b31ac` (2026-09-04); the goal cleanup programme of 2026-09-05 to 2026-09-08: dispatcher shared state `4fd93b0b`, quest-data split `f00f510e`, shop split `0005e1cb`, roster reconciliation `6aeebc6c`, combat reward and enemy rolls `7e19aadf`, carried processing and player attack rolls `afae5ee6`, papercut queue recency `f943385e`, combined combat batch `6dacde54`, and the prayer-drain, bank-trip, and activity-selector integration `1bf2cfe2`.

Last staleness sweep: 2026-09-16

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
