# Slayer Warped-terrorbird assignment-gate conflict — 2026-07-19

Status: **authority conflict; implementation stopped**.  
Scope: the hidden Duradel/Lapalok Warped-terrorbird family.

## Conflict

The nearest cutoff article, RuneScape Wiki `Warped terrorbird` oldid
`6555103` at `2012-11-14T10:32:24Z`, says:

- Slayer 56 and a carried Crystal chime are required to kill the monster; and
- players must have **at least started** The Path of Glouphrie before receiving
  the assignment.

Source:
<https://runescape.wiki/w/Warped_terrorbird?oldid=6555103>.

Current `slayer_data.py:825-832` stores
`required_quest_id="the_path_of_glouphrie"`. Current
`slayer_logic.py:42-46,82-90` interprets that field only as a completed quest
and renders `Complete The Path Of Glouphrie`.

The owning Duradel/Lapalok pool audit says only `Path of Glouphrie`; it does
not name an exact quest-stage predicate. The Warped-tortoise audit separately
pins completion for that different family, so it cannot resolve the
Terrorbird-specific “at least started” statement.

## Stop boundary

No quest-gate field, stage predicate, family row, target, item, or test was
changed. Choosing any-start, first-stage completion, Crystal-chime acquisition,
Poison-Waste access, or full quest completion would silently define a
predicate the settled registry schema does not currently express.

The complete independent source boundary is recorded at
`../source-audits/slayer-warped-terrorbird-combat-2026-07-19.md`.
Duradel/Lapalok remains hidden and unrenormalized at **14/35** with
`warped_terrorbirds:combat_target`.

## Required authority correction

A newer Memory Bank record must name the exact executable assignment predicate
and its owning quest-stage field. This is an authority/schema correction, not a
new creative-design fork. After that record exists, implementation can proceed
without reopening the settled family, count, Slayer level, or Crystal-chime
contract.
