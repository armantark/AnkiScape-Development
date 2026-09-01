# The diary wiring makes no tier claimable — 2026-09-01

Author: the orchestration seat, `Orchestrator [c79eb6]`.
Consumer: the design seat, `ankiscape-fork-41`.
Measured on `main` at `e7745b6a`.

## 1. Why this file exists

Section 25.2 item 2 of the rulings ledger states the reason to do the
Achievement Diary wiring first: "This is the largest player-visible item on the
board: 0 of 34 diary tiers are claimable until it lands."

The first half is true. The second half implies that the wiring changes the
count. It does not. I measured the premise before I dispatched the work, and
the measurement inverts it.

I did not dispatch item 2. Item 1, the Mogre slice, is dispatched and runs now.

## 2. The measurement

I joined the 320 ledger rows to the live catalog by `task_id`. Every empty
condition row in the catalog has a ledger row, and no row is missing.

```
families: 10 | tiers: 34 | named tasks: 474 | tasks with empty conditions: 320
ledger rows: 320 | active 43 | translated 30 | dormant 247
empty-condition tasks not found in the ledger: 0
tiers with zero dormant rows: 0
```

Every one of the 34 tiers keeps at least one dormant row after the wiring. A
dormant row has a designed trigger and no system that can fire it. So the
wiring moves 73 rows from "no condition" to a live condition, and it moves the
claimable tier count from 0 of 34 to 0 of 34.

## 3. The one tier that is close

`lumbridge_medium` is one row away. It holds 12 tasks: 8 already wired, 1
`active`, 2 `translated`, and 1 `dormant`.

Its single dormant row is `lumbridge_medium_where_s_the_beef`, and its future
system is `bank_inventory_actions`:

> Complete when a Beefy Bill service action successfully transfers at least one
> player-selected item into the bank.

That system is the smallest in the whole ledger. It carries two rows, and it
blocks two tiers:

| Row | Tier | Designed trigger needs |
| --- | --- | --- |
| `lumbridge_medium_where_s_the_beef` | `lumbridge_medium` | a bank write that records Beefy Bill as the service source |
| `lumbridge_easy_money_down_the_drayn` | `lumbridge_hard` | a bank action that carries the `draynor_village` bank identity |

The second tier does not clear, because `lumbridge_hard` has five other
blocking systems.

## 4. What actually blocks the board

The dormant rows concentrate. Two systems account for most of the block:

| Future system | Tiers blocked | Dormant rows |
| --- | ---: | ---: |
| `world_transport_actions` | 25 | 48 |
| `npc_dialogue_actions` | 20 | 38 |
| `combat_encounter_actions` | 14 | 19 |
| `location_visit_actions` | 13 | 16 |
| `item_processing_actions` | 13 | 18 |
| `skill_action_telemetry` | 12 | 17 |
| `object_interaction_actions` | 11 | 18 |
| `bank_inventory_actions` | 2 | 2 |

The full 20-row table is reproducible from the ledger and the catalog. The tail
below `object_interaction_actions` blocks 8 tiers or fewer each.

## 5. The options, with my lean

The wiring is not wasted work under any option. It is the prerequisite for
every tier, and it makes 73 deeds live. The question is only what ships with
it.

- **Option A — wire the 320 as ordered, and stop there.** Smallest diff, exact
  compliance with section 25.2. Player-visible result: no tier becomes
  claimable, and the ledger's own honest-stop note stays true.
- **Option B — wire the 320, and add `bank_inventory_actions` in the same
  slice.** Two rows, one bank identity and one service source on the existing
  bank write path. `lumbridge_medium` reaches 12 of 12 and becomes the first
  claimable tier in the product. The count moves from 0 of 34 to 1 of 34.
- **Option C — reorder the queue and build `world_transport_actions` first.**
  It blocks 25 tiers. It is also a whole movement system, so it is a program
  rather than a slice, and it needs its own harvest.

**My lean is Option B.** It is one breadth-first step out from the ordered
work, the added system is the smallest in the ledger, and it converts a slice
with no player-visible result into the first claimable diary tier. Option C is
the real unlock for the board, but it is large enough that the owner should
price it rather than an orchestrator.

The owner's row 135 default and the patch rule are unaffected by any option: a
correction stays a ledger-row edit plus a regeneration, never a hand edit of
the generated catalog.

## 6. What I do while you decide

I do not hold item 2, and I do not wait. The wiring itself is identical under
Option A and Option B, so I dispatch item 2 at Option A scope when the Mogre
slice lands. Nothing in that dispatch has to be undone later.

If you answer B, the `bank_inventory_actions` addition becomes a small
follow-on slice on top of the wiring. If you answer C, tell me where it sits in
the queue, because it is a program and not a slice.

One word is enough: A, B, or C.
