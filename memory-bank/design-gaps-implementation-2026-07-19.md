# Implementation design conflicts

Date: 2026-07-19

Status: **one open source/contract conflict.**

## 1. Grand Exchange offer-slot count

Resolution: **six slots; period parity wins**

The newest settled design records require eight player offer slots:

- `fake-grand-exchange-design.md:27`
- `fake-grand-exchange-design.md:258`
- `ge-relitigation-2026-07-19.md:16-19`

The pre-cutoff RuneScape Wiki revision instead states that members had six
spaces and free players had two:

- RuneScape Wiki `Grand Exchange`, oldid `6367453`, timestamp
  `2012-10-08T01:30:21Z`
- <https://runescape.wiki/w/Grand_Exchange?oldid=6367453>

Owner decision, 2026-07-19: use the cutoff-faithful six slots. The superseding
authority is `grand-exchange-slot-count-supersession-2026-07-19.md`. The
implementation and current forward records must use six; the older eight-slot
clauses remain historical evidence only.

## 2. Treasure Trails clue ownership

Priority: **high — blocks the first complete Easy Treasure Trails slice**

The settled contract calls one clue per tier the authentic ownership rule:

- `treasure-trails-design-contract-2026-07-19.md:10-13`

The pinned period record instead says a player can receive another clue only
when no clue exists in inventory, bank, or Kingdom Management resources:

- RuneScape Wiki `Treasure Trails`, oldid `6473708`, timestamp
  `2012-10-26T00:01:09Z`
- <https://runescape.wiki/w/Treasure_Trails?oldid=6473708>

Later RuneScape history dates the one-per-tier rule to 2015, after the cutoff.
The implementation has stopped rather than silently reinterpret the
owner-settled contract.

Recommended resolution: **use one clue total across every tier**, matching the
2012 period rule. Keep caskets outside that ownership check so a completed trail
can be opened normally.

Separate source blocker: the exact easy-clue selection and casket reward rolls
remain `source_blocked`; see
`source-audits/treasure-trails-easy-source-boundary-2026-07-19.md`.
