# Summoning implementation design-gap ledger (2026-07-17)

Only unresolved player-experience choices that require owner direction belong
here. Missing historical numbers are recorded as `source_blocked` in source
audits; missing code dependencies are implementation backlog, not design gaps.

## Current owner-level gaps

None. The closed contract and owner amendment at commit `d7539c9` settle every
player-facing fork encountered through the surface catalog batch.

## Implementation judgments recorded without reopening the grill

- Familiar lifetime uses the labeled two-source-duration-units-per-review
  calibration recorded in
  `source-audits/summoning-catalog-2026-07-17.md`. This is balance calibration,
  not wall-clock simulation.
- Meerkats and Ghast remain full summonable familiar definitions but do not
  appear as fabricated obelisk infusion recipes.

