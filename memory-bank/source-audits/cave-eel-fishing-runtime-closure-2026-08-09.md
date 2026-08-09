# Cave eel Fishing runtime closure — 2026-08-09

Backlog id: `fish-cave-eel-stub`

Status: implemented and verified. This audit supersedes the runtime block in
`gap-grill-15-cave-eel-provenance-2026-07-10.md`; that file remains the period
source record and its settled product shape remains authoritative.

## Evidence and reconciliation

- RuneScape Wiki `Cave eel` oldid `6357178`, dated `2012-10-06`, pins level 38
  Fishing, an ordinary Fishing rod, one Fishing bait for a successful catch,
  the Lumbridge Swamp Caves and alternate Meiyerditch dungeon locations, 80
  Fishing XP, tradeable Raw cave eel output, and the linked level-38 Cooking
  row.
- The local rev-667 reconstruction has an unbound `Fish.CAVE_EEL` row with item
  id 5001 and the standard 10/80 Fishing interpolation endpoints, but no
  `FishingTool` or `FishingSpot` binding. Its level 28 conflicts with the dated
  period page and is rejected; the live target uses level 38.
- No period server catch roll was recovered. The 10/80 unbound-row endpoints
  are registered as `fishing.cave_eel_catch_roll`. They reuse the existing
  one-review Fishing interpolation and can be replaced without changing the
  target contract.

## Live implementation

- `Catch cave eel` is an ordinary level-38 Fishing target on the abstract
  Lumbridge Swamp Caves route. Meiyerditch remains an alternate source location
  rather than a false universal gate or a new map.
- Each successful review consumes one Fishing bait, produces one Raw cave eel,
  and awards 80 Fishing XP. A dry attempt consumes nothing. The reusable rod is
  represented by the existing Fishing method/tool metadata, matching every
  other ordinary Fishing target rather than adding a Cave-eel-only tool UI.
- The established target-local carried layout, bank-run flow, target selection,
  persistence, review undo, telemetry, urn, outfit, brawling-glove, and XP
  paths require no new state or migration.
- The dormant deferred-content wrapper was removed after its only row became
  live. Raw cave eel reuses the existing normalized, provenance-recorded
  Cooking item sprite in Fishing lists and inventory surfaces.
- This adds one row to the established Fishing selector. It does not introduce
  a new UI surface, control, layout, or interaction pattern, so no additional
  Kimi or Fable taste pass is required.

## Manual Anki check

1. Open Skills, Gathering, Fishing at level 38 or higher.
2. Confirm `Catch cave eel (Lvl 38)` has the Raw cave eel icon and can be
   selected like every other Fishing target.
3. With one Fishing bait in the target carried pack, answer until a catch.
   Confirm the bait is consumed only on success, Raw cave eel is added, and 80
   Fishing XP is awarded.
4. Use Anki Undo and confirm bait, output, XP, telemetry, carried state, and the
   random state return atomically.

## Explicit omissions

- The exact catch roll remains a registered placeholder, not a period claim.
- This slice does not add a world map, Meiyerditch gate, quest requirement, new
  Fishing-rod item system, or Cave-eel-specific policy.

## Verification

- Focused data, pure logic, runtime, placeholder, and real offscreen Qt
  coverage passed 199 plain tests and 1 Qt target-row test.
- Full plain discovery passed 3,974 tests in 218.163 seconds with 486 expected
  skips.
- Full real offscreen Qt discovery passed 3,974 tests in 528.980 seconds with 3
  intentional skips.
- Documentation passes for 538 Markdown and 431 HTML files. Test quality finds
  3,940 test methods across 180 files, zero hard issues, and 19 known
  structural-clone groups.
- Compilation, backlog JSON, diff, and worktree-safety checks pass.
- Reachability records 1,538 actions, 2,341 reachable items, 167 orphan
  inputs, and 187 unresolved actions. This slice removes one orphan and one
  unresolved action from the established dependency ledger.
- Native Computer Use timed out for both `Anki` and `net.ankiweb.launcher` with
  `Computer Use server error -10005: timeoutReached`; native interaction is not
  claimed for this slice.
