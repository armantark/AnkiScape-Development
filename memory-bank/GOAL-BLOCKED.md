# Goal blocked: every identified acquisition route fails viability

Date: 2026-08-12

## What is blocked

The acquisition-completion program on `goal/acquire-2026-08-12` has exhausted
its identified implementable candidates. Candidate testing started from
`94358c9872941de792988029f51e94f9bbf37e87`. The common blocker is the missing
production quest-action emitter: 185 of 196 quests directly require actions that
no runtime path emits, and prerequisite closure raises the approximate impact to
190 of 196.
Most authentic acquisition routes gated on those quests are therefore inert for
an ordinary player progressing from level one.

The routes outside that common cause are blocked by their own missing mechanisms:

- the Habitat vine routes need a live, player-specific environment and attraction
  model;
- Dragon impling rewards need a filled-jar Open/Loot action;
- the Spider-on-stick chain needs a Jungle spider carcass producer, a
  thatching-spar Skewer-stick source, and consumption that returns the stick;
- Relicym's balm shop access is circular without the un-emitted Zogre Flesh
  Eaters progression that first supplies balm and unlocks Uglug; and
- Curly root needs its Jadinko-Lair curly-vine Woodcutting producer rather than
  only the existing Firemaking consumer.

## What was tried

The acquisition program examined eleven candidate roots across five families.
The routes included Snake hide and the Crab pair behind unavailable quest
progression; the Habitat-vine family behind its missing environment model; the
Dragon-impling pair behind its missing filled-jar action; the Spider chain behind
its missing Jungle-spider, thatching-spar, and returned-stick mechanisms; and the
final Relicym's balm and Curly-root viability checks. Candidate grouping overlaps
where one missing input or mechanism affects more than one downstream orphan.

Each candidate was checked for level-one gate satisfiability, quest and area
access, live runtime mechanisms through `tools/audit_item_reachability.py`,
positive controls for absence probes, pinned pre-cutoff wiki evidence, and
per-path Darkan history. Snake hide, the Habitat vines, and the Crab family were
sourced to the period standard before their mechanical blockers stopped product
work. No acquisition implementation, mutation run, full test lane, or product
commit was attempted after the final two candidates failed viability.

## Smaller independent mechanisms

Two bounded mechanisms are genuinely smaller than the quest-emitter program:

- a filled-jar Open/Loot action would independently unblock impling rewards; and
- after `goal/vines-2026-08-11` merges, a Habitat environment model plus the
  already-sourced Shadow and Corrupt vine routes is a well-specified slice.

## The single thing that would unblock it

Implement and verify the production quest-action emitter mechanism. It addresses
the large majority of blocked acquisition routes and removes the structural cause
that made the candidate list collapse.
