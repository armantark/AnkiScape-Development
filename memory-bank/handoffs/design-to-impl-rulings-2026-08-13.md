# Priority-matrix rulings — design thread to harvesting loop

Date: 2026-08-13. Author: the design thread. Consumer: the harvesting-loop
orchestrator and its dispatched agents.

## 1. Goal

This ledger replaces intuition-based work selection in the headless harvesting
loop with one scored formula. The owner approved each ruling below on
2026-08-13. When the loop selects work, the loop must obey this ledger.

## 2. Scope

The matrix governs the headless harvesting loop only: acquisition gaps,
placeholder values, catalog depth, missing content, and shared plumbing.

The matrix does not govern:

- Owner playtest passes (Pass 8, Pass 9, and later passes). The design thread
  orchestrates those directly. A new pass preempts scored work.
- Owner design decisions. Those stay in `memory-bank/design-thread-queue.md`.

## 3. Rulings

1. **R1 — no blocked class.** No item is "blocked". An item is "deferred" with
   a recorded reason. When the evidence order is exhausted and no period data
   exists, the loop must invent the value and register it in
   `memory-bank/placeholder-values.md`.
2. **R2 — score everything.** Every backlog item gets a score. A deferred item
   keeps a DEFERRED tag and its reason, and stays in the ranked list.
3. **R3 — override lane.** Three defect classes go to the front of every
   queue, before all scored work: save corruption, review blockers, and undo
   breakage. A crash without state damage is a normal scored defect.
4. **R4 — the formula.**
   `priority = Reach × StageWeight × Gap × SubstrateBump × EvidenceBump`.
5. **R5 — Reach.** Reach uses the surface tier: review-path surface = 3,
   opt-in activity = 2, endgame-only = 1. Inside one tier, the leverage number
   from `tools/audit_item_reachability.py` (transitive item and action gain)
   sets the order.
6. **R6 — StageWeight.** Early = required level 30 or lower and no quest
   gate, weight 3. Mid = level 31 to 60, or one short quest chain, weight 2.
   Late = level 61 or higher, or a deep chain, weight 1.
7. **R7 — Gap.** Player-visible defect = 3. Absent period mechanic = 2. Live
   mechanic with a placeholder value or a thin catalog = 1. Complete = 0.
8. **R8 — SubstrateBump.** An item that changes behavior in five or more
   families or call sites gets ×2. Count the call sites in code.
9. **R9 — EvidenceBump.** A row whose evidence already sits on local disk
   (the rev-727 cache, the Darkan checkout, other on-disk caches) gets ×1.5.
10. **R10 — slice first.** A large program enters as a family. The loop scores
    and works one atomic slice at a time (one quest, one placeholder row, one
    handler). On equal scores, the smaller slice goes first.
11. **R11 — re-score cadence.** The loop must re-score the ledger at each
    queue audit, after each merged batch.
12. **R12 — relation to the goal text.** This matrix is the concrete form of
    the goal sentence "prioritize shared tooling, player-visible defects,
    readily recoverable period values, registered placeholders, and recorded
    data-depth debt". The goal text does not change. When the two disagree,
    this ledger wins.

## 4. Override lane — current contents

| Item | Evidence | Size |
|---|---|---|
| Cadence kernel raises `ValueError` on an oversized persisted credit | `logic/cadence_kernel.py:243-254`; type sanitization at `:107-127` does not cover valid oversized integers; no recovery test exists | ~10 model-minutes |

Note: the owner reports the in-review lag as fixed. No override entry exists
for it. The loop does not need to act.

## 5. Initial scored ledger — top 10

The design thread scored the visible backlog on 2026-08-13. The factor columns
show the arithmetic. GATE-1 (section 6) governs this table.

| # | Item | R | S | G | Bumps | Score | Notes |
|---|---|---|---|---|---|---|---|
| 1 | Missing quests, per-quest slices | 2 | 3 | 2 | ×1.5 ev | 18 | 167 absent definitions; start with unlock chains (Jungle Potion → Cave horrors); Darkan evidence on disk; order slices by leverage |
| 2 | Bestiary expansion, per-family slices | 2 | 3 | 2 | ×1.5 ev | 18 | Beyond the current 130 enemies; Darkan and cache evidence on disk; order by leverage |
| 3 | Undo-seam migration | 2 | 3 | 1 | ×2 sub | 12 | 30 of 54 `_apply_*_command` handlers bypass `commit_direct_action` (`__init__.py:1010-1064`); one handler per slice |
| 4 | Daily Challenge reward XP | 3 | 3 | 1 | — | 9 | Placeholder `100 × required level`; branch `daily-challenge-xp-depth` holds one live commit of prior work |
| 5 | Quest rewards bypass the one-clue filter | 2 | 1 | 3 | — | 6 | `logic_pure/logic_pure_quest.py:1436-1461` skips the filter in `logic/treasure_trails_logic.py:105-164`; small route-through |
| 6 | rev-727 placeholder harvest, per-row slices | 2 | 2 | 1 | ×1.5 ev | 6 | Register rows with undecoded local evidence; harvest before more invention |
| 7 | Chaeldar readiness families | 2 | 1 | 2 | ×1.5 ev | 6 | Nine families short of 34/34; per-family slices |
| 8 | Evil Tree kindling period art | 2 | 2 | 1 | — | 4 | Last stale row from the tranche-2 art sweep; `assets_provenance.json:48054` |
| 9 | Dungeoneering payout curves | 2 | 1 | 1 | ×1.5 ev | 3 | Registered curves at `memory-bank/placeholder-values.md:177-185`; Darkan evidence |
| 10 | Housekeeping rider: stale selection records | — | — | — | — | rider | Retire `memory-bank/loop-queue.md:177` pause, the stale art row in `memory-bank/gpt-deferred-queue.md`, and the two-planned-skills framing in `memory-bank/roadmap.md` and `memory-bank/progress.md` |

## 6. GATE-1 — passed

The owner approved the section 5 table unchanged on 2026-08-13. The loop can
consume the ranked list under the section 7 rules.

## 7. Consumption rules for the loop

1. Take the override lane first.
2. Then take the highest scored slice that no agent holds.
3. Re-score at each queue audit (R11).
4. Record each new deferral reason in the item's register file.
5. When a score changes because an audit number changed, note the old and new
   score in the queue-audit record.

## 8. Corrections this ledger already applies

The 2026-08-13 read-only audit falsified these recorded claims. Do not select
work from them:

- "311 unsatisfiable quest steps" — no current audit produces that count. The
  blast-radius audit counts 994 rows that contain blockers; the reachability
  tool emits 187 first-block diagnostics. An exact count needs an enumerating
  audit without first-block short-circuits.
- Design-thread-queue 3.11 (the 24-of-25-skills Max premise) — stale.
  Dungeoneering is `partial` and trainable, and writes XP
  (`logic/dungeoneering_logic.py:2673-2702`).
- Design-gaps 5.1 ("31 handlers, no shared seam") — stale. The seam exists;
  the open work is the 30-handler migration (row 3 above).
- The GPT-queue art row — half stale. Wicked hood already has period art;
  only Evil Tree kindling remains (row 8 above).

## 9. Rulings made directly by the owner

These were given by the owner in conversation with the orchestration seat, not
relayed through the design thread. They carry full authority and outrank the
sections above where they conflict.

**O1 — Fable is out of the loop entirely.** Ruled 2026-08-13 13:49 PDT: "Fable
is critical on quota, so I need to start interfacing with you now. Do not talk
to or use Fable anymore." No dispatch to Fable, no consultation, no routing of
writing or design work to it, until the owner lifts this.

Consequences the next seat must plan around. Fable held product owner,
architect, and co-lead designer, and authored the ledger this file belongs to.
Sections 1 through 8 remain in force as written; they are a settled record, not
a live thread. Open design questions now go to the owner directly, as options
with a stated lean, at most one per report. Kimi K3 remains the other design
co-lead and the standing independent reviewer, but was itself over quota when
this was ruled.

**O2 — the goal is paused.** Ruled 2026-08-13 13:50 PDT, on the grounds that
the main quota is also over. Recorded through the goal's own pause mechanism in
`memory-bank/GOAL-BLOCKED.md`, which the goal text accepts as satisfying it.
That file names the blocker, what was tried, and the single unblocking
condition, and must be deleted before work resumes.

## 10. Queue-audit checkpoint — 2026-08-30

This audit uses `main` commit `d51f0f84df4d4cea3ab307954a01562f0b71f52d`.
It preserves sections 1 through 9 without edits.
The next section will apply the R4 formula after this checkpoint.

### Override lane verification

The cadence override defect is fixed.
`sanitize_cadence_profile_state_pure` still accepts nonnegative integers at
`logic/cadence_kernel.py:107-127`.
`advance_cadence_pure` now caps persisted credit at
`logic/cadence_kernel.py:243-253` before rate arithmetic.
A pure probe used a credit of `10^1000` with threshold `10`.
The call returned credit `0`, emitted one opportunity, and raised no exception.
No dedicated oversized persisted-credit regression test exists.
The current override lane is empty.

### Section 8 verification

| recorded claim | current result | current evidence |
| --- | --- | --- |
| `311` unsatisfiable quest steps | Still false. No tracked audit emits this measure. The current fixed point has 148 blocked quest-stage products and 284 unresolved actions. | `tools/audit_item_reachability.py:1950-1965`; `tools/audit_item_reachability.py:2036-2057` |
| Max requires 24 of 25 skills | Still false. Dungeoneering is partial and trainable. Floor completion still returns Dungeoneering XP. | `core/skill_registry.py:300-308`; `logic/dungeoneering_logic.py:2686-2702` |
| 31 direct-action handlers have no shared seam | Still false. A fresh Abstract Syntax Tree scan found 54 handlers, 54 seam calls, and 0 bypasses. | `memory-bank/design-thread-queue.md:1738-1744`; `__init__.py:1020` |
| Wicked hood has art, but Evil Tree kindling does not | Now fully false. Both asset rows and both files exist. | `assets_provenance.json:36954`; `assets_provenance.json:48402`; `woodcuttingitems/evil_tree_kindling.png:1` |

The direct-action correction in section 8 also contains a stale follow-up.
The stated 30-handler migration now has zero open handlers.
The art correction also has no open art row.

### New stale claims found by this audit

| location | stale claim | current evidence |
| --- | --- | --- |
| Section 5 row 1 | `167` quest definitions are absent. | The generated catalog has 194 rows. Two miniquests make 196 definitions. See `generated/quest_catalog_generated.py:12` and `data/quest_data.py:10844-10914`. |
| Section 5 row 3 | 30 of 54 direct-action handlers bypass the undo seam. | The fresh scan found 0 bypasses. See `memory-bank/design-thread-queue.md:1738-1744`. |
| Section 5 row 5 | Quest rewards skip the one-clue filter. | Quest completion calls the central filter at `logic_pure/logic_pure_quest.py:1530-1537`. |
| Section 5 row 8 | Evil Tree kindling is the last stale art row. | The asset and provenance row exist at `woodcuttingitems/evil_tree_kindling.png:1` and `assets_provenance.json:48402`. |
| Section 5 row 10 | All four housekeeping records remain open. | The pause record is checked at `memory-bank/loop-queue.md:200`. The roadmap uses the current skill model at `memory-bank/roadmap.md:8`. The GPT art row remains stale at `memory-bank/gpt-deferred-queue.md:21`. |

The other section 5 premises still hold at this checkpoint.
`COMBAT_ENEMY_DATA` still records 130 enemies at
`memory-bank/future-work-kanban.md:1374`.
Daily Challenge XP remains registered at
`memory-bank/placeholder-values.md:71`.
The placeholder register has 179 rows.
Chaeldar remains at 25 of 34 families at
`memory-bank/future-work-kanban.md:810`.
The Dungeoneering floor XP curve remains registered at
`memory-bank/placeholder-values.md:191`.
