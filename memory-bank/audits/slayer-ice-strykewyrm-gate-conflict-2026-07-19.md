# Slayer Ice-strykewyrm assignment-gate conflict — 2026-07-19

Status: **authority conflict; implementation stopped**.  
Scope: the hidden Duradel/Lapalok and Kuradal Ice-strykewyrm family.

## Conflict

The nearest cutoff article, RuneScape Wiki `Ice strykewyrm` oldid `6565909`
at `2012-11-17T10:51:54Z`, says players must have completed The Tale of the
Muspah before receiving Ice-strykewyrm assignments from Duradel/Lapalok or
Kuradal:
<https://runescape.wiki/w/Ice_strykewyrm?oldid=6565909>.

The settled Kuradal pool audit includes that quest gate. The settled
Duradel/Lapalok audit omits it, and current `data/slayer/contract.py:792-801` has no
`required_quest_id` on the global family row. That global row would affect
both masters.

## Stop boundary

No family gate, master row, quest state, target, cape item, reward-shop flag,
or test was changed. Adding `required_quest_id="the_tale_of_the_muspah"`
would agree with the direct cutoff article and Kuradal audit but would silently
rewrite the already-settled Duradel/Lapalok contract.

The complete independent source boundary is recorded at
`../source-audits/slayer-ice-strykewyrm-combat-2026-07-19.md`.
Duradel/Lapalok remains hidden and unrenormalized at **14/35** with
`ice_strykewyrms:combat_target`. Kuradal remains unencoded behind its existing
registry-schema conflict.

## Required authority correction

A newer Memory Bank record must explicitly supersede the Duradel/Lapalok
omission and name whether the Tale-of-the-Muspah completion gate belongs on
the shared family or on each applicable master-family row. This is an
authority/schema correction, not a creative-design fork.
