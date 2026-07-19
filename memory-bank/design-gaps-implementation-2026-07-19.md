# Implementation design conflicts

Date: 2026-07-19

Status: **resolved by owner; no open design conflicts.**

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
