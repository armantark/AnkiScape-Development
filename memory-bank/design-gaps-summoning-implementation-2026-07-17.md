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
- Pet growth uses 25 active reviews per stage, baby hunger gains 6 points per
  active review, adult hunger gains 3, and feeding removes 30. These are
  explicit review-native balance calibrations over the sourced stage/hunger
  model, not reconstructed wall-clock rates.
- Generic period food categories resolve only to real inventory items already
  represented by Fishing/Cooking data. Baby troll's unusual
  any-tradeable-food rule accepts a deliberately carried item; it never consumes
  remotely from Bank.
- A protected carried pet has a typed hook in the existing death transaction.
  The current Combat surface has no player-facing Items Kept selector yet, so
  ordinary unprotected carried pets are destroyed and never enter the grave.
  This is a dependency on the already-designed death-equipment surface, not a
  Summoning design fork.
