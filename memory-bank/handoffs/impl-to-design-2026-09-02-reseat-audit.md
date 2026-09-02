# Branch audit after the reseat, and the six lanes it started

Seat: orchestrator, reseated 2026-09-02 08:46 PDT. Work order: ledger section 46.
Main at `0e1c57a1`. Canonical checkout clean.

## 1. What the dead seat left

| branch | head | own commits | state |
| --- | --- | --- | --- |
| `goal/split-constants-2026-09-02` | `b9c788d8` | 2 | complete, unverified |
| `goal/diary-curation-pass-two-2026-09-02` | `7e6e85d3` | 1 curation commit on 8 diary-wiring commits | complete, unverified |
| `goal/split-diary-catalog-2026-09-02` | `6ab9c330` | 0 | work is uncommitted, preserved as a ref |

The constants split leaves `core/constants.py` at 805 lines and adds 12 modules
under `core/constants_parts/`; the largest is 582 lines. No module exceeds 1,000
lines. I treat both branches as unverified drafts, as instructed.

## 2. Item 2 has not landed, and 2c sits on top of it

The eight commits below the curation commit are the diary-ledger-wiring slice
(`026f9452` and below). None of them is on main. So the 2c curation branch cannot
land alone: a landing of 2c lands item 2 with it. The design seat must decide
whether the two go through one gate together or whether the wiring lands first on
its own branch. I made no decision here.

## 3. The preserved splits are intact

`git for-each-ref refs/preserved` lists all four refs. I checked one against its
worktree: `refs/preserved/quest-data-2026-09-02` (`1ebf5a12`) holds 89 changed
files, 15,159 insertions and 12,685 deletions, and its pooled worktree (slot 6)
would stage exactly 89 paths. The other three worktrees (slots 4, 5, 10) are still
dirty and untouched. Every dispatched agent carries a written prohibition against
touching them or deleting a preserved ref.

## 4. The land lock is stale, and main is not frozen

`.git/ankiscape-promotion-land.lock` still holds the record written at 05:07:25 PDT
for commit `6ab9c330ed6b6c57f14e2eaa5d2f5fdcf9aca18b`, pid 26419. That pid is dead
and that landing succeeded. The freeze hook reports:

```
Landing freeze stale after 3h 39m for 6ab9c330ed6b6c57f14e2eaa5d2f5fdcf9aca18b (PID 26419); allowing commit.
```

So the staleness rule of ruling 40 works and main accepts commits. I left the lock
file in place as evidence for the follow-up slice.

## 5. Pool capacity

Nine of ten pooled worktrees were leased, and only one was free. I released the
three that were clean and whose branches are on main (`module-surface-harness`,
`gate-hardening`, `batch1`). Release refuses a dirty tree, so it could not have
reached the preserved work. Four slots are now free.

## 6. Six lanes running

| lane | model | subject |
| --- | --- | --- |
| verification | `gpt-5.6-sol` | constants split: plain lane, five audits, surface digests under both interpreters, ratchet check |
| review | `opus` | constants split: is it only a move |
| review | `glm-5.3-flash` | constants split: extra cross-lineage vote |
| conformance | `gpt-5.6-sol` | 2c: 131 resolved rows and 5 re-pointed rows against ruling 31 |
| review | `glm-5.3-flash` | 2c: extra cross-lineage vote on the curation itself |
| implementation | `gpt-5.6-sol` | promotion-gate follow-up: the leaked land lock and the linked-worktree hook warning |

Kimi is over quota by 2 requests with the next block 13 hours out, so the split
architecture reviewer of ruling 37 is not seated on the constants split. Opus
holds that seat for this one slice, with GLM as the second lineage.

## 7. Not done

- The four preserved splits stay held. I did not reshape them and will not until
  you relay the owner's ruling on 42.3.
- No landing window is open, so no gate is running.
- The harvest lanes are not restarted yet: item 3 and item 5 both already have
  harvest records (`memory-bank/source-audits/proof-bindings-harvest-2026-09-01.md`,
  `next-sentinel-quest-selection-2026-09-01.md`, `ghosts-ahoy-harvest-2026-09-01.md`).
  Tell me which unit the next harvest should pin, or I will run ahead on the quest
  after Ghosts Ahoy.
