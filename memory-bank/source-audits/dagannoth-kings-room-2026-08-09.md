# Dagannoth Kings room — 2026-08-09

Target cutoff: 2012-11-20, immediately before EOC.

## Result

The Dagannoth Kings are live as one persistent dangerous Combat room under
Activities. Entering spawns Prime, Supreme, and Rex together. One king is the
engaged target for the live six-tick Combat slice; every other living king
applies ordinary style-aware roster pressure. Casual targeting prioritizes
Prime, then Supreme, then Rex. Advanced targeting lets the player choose any
living king. Kills, lifepoints, respawns, trip counts, total counts, mode, and
selection persist across reviews. Leave is explicit, and death uses ordinary
dangerous Combat loss.

The room uses the shared boss-room substrate rather than a bespoke combat
engine. Combat remains authoritative for accuracy, damage, protection prayers,
food, drops, XP, Slayer tasks, death, and review undo. Direct room commands use
the established direct-action undo transaction.

The minimum reward catalog contains the two sourced guaranteed drops and the
Dragon hatchet acquisition seam needed by five live Farming actions. Exhaustive
ring, armour, resource, clue, and rare-drop-table catalogs remain later data
depth rather than mechanical blockers.

## Period evidence

- Dagannoth Rex oldid `6505723`, dated `2012-10-30T19:38:16Z`, pins level 303,
  2,550 lifepoints, melee, approximate maximum hit 280, 334 Slayer XP,
  guaranteed Dagannoth bones and hide, and a rare Dragon hatchet.
- Dagannoth Prime oldid `6457675`, dated `2012-10-23T01:41:21Z`, pins level
  303, 2,550 lifepoints, Magic, maximum hit 610, 255 Slayer XP, the same two
  guaranteed drops, a rare Dragon hatchet, and calls Prime the most dangerous
  king.
- Dagannoth Supreme oldid `6535937`, dated `2012-11-05T15:54:14Z`, pins level
  303, 2,560 lifepoints, Ranged, four-tick attack speed, approximate maximum hit
  300, 255 Slayer XP, the same guaranteed drops, and a rare Dragon hatchet.
- Immutable copies live in the Darkan repository at
  `memory-bank/audit/sources/dagannoth-rex-oldid-6505723.json`,
  `dagannoth-prime-oldid-6457675.json`, and
  `dagannoth-supreme-oldid-6535937.json`.
- Darkan combat definitions pin the three five-stat blocks and agree on a
  59-tick respawn reconstruction. Its three executable drop tables identify
  Dagannoth bones `6729`, Dagannoth hide `6155`, and Dragon hatchet `6739`.
  These records live under
  `darkan-world-server/data/npcs/combatdefs/uncategorized/` and
  `darkan-world-server/data/npcs/drops/`.

## Honest source boundary

The cutoff pages do not state Prime's or Rex's attack interval, the respawn
interval, or a numeric Dragon-hatchet rate. The live values are marked and
registered as `dagannoth_kings.attack_speed`,
`dagannoth_kings.respawn_ticks`, and
`dagannoth_kings.dragon_hatchet_drop_rate`. No exhaustive drop catalog is
claimed.

The period pages establish Waterbirth Island but no quest requirement. Travel,
door co-operation, ladder routing, and safespot geometry are intentionally
flattened by the settled boss-instance and multi-enemy contracts. There is no
wall-clock gameplay and no invented entry currency.

## UI and assets

The room is an Activities card, separate from Utilities, inside the existing
paginated card surface with no nested scroll area. It shows a visible roster,
alive/dead state, engaged target, review-based respawn count, Casual/Advanced
policy, trip totals, persistent status, explicit Leave, and a standalone
dangerous-death warning.

The three normalized NPC sprites predate the cutoff. Their provenance rows are:

- Rex: `2012-03-09T17:07:44Z`, SHA-1
  `e9550564db6e48b4c21c2d242fde4b4b5fbbe819`.
- Prime: `2012-03-09T16:42:51Z`, SHA-1
  `de31b278597597bf9f90e2ba94127eaaf9ae5cbd`.
- Supreme: `2012-02-24T03:18:01Z`, SHA-1
  `0a07c318a498579c39174656e649250c7e425af8`.

Kimi K3 and Opus reviewed the new card. Accepted corrections close dynamic
height clipping, normalized icon scaling, warning hierarchy, dead-row visual
weight, selector guidance, and primary/secondary action balance. A 900×560
render plus a geometry regression proves that the action row stays above the
pagination control. This remains offscreen Qt evidence, not native Anki proof.

## Verification

- Broad focused data/Combat/Slayer/runtime/storage/cadence/immutability checks:
  663 tests passed.
- Direct-action undo integration and the placeholder register passed.
- Focused real offscreen Qt card check: 1 test passed.
- Full plain discovery: 4,004 tests passed with 488 expected skips.
- Full real offscreen Qt discovery: 4,004 tests passed with 3 skips.
- Documentation: 543 Markdown and 431 HTML files passed.
- Test quality: 3,969 methods across 181 files, zero hard issues.
- Reachability: 1,547 actions, 2,354 reachable items, 159 orphan inputs, and
  179 blocked actions. Dragon hatchet and the two guaranteed drops are live.
- The 900×560 render is `/tmp/ankiscape-dagannoth-kings-ui.png`; the geometry
  regression proves that its action row stays above the pagination control.
- Compilation, tracked JSON, diff, asset normalization, and worktree safety
  passed.

Native Anki interaction is not claimed. Manual acceptance in the real profile:
open Activities > Activities > Dagannoth Kings; enter the room; confirm all
three period sprites and attack styles; switch to Advanced and select Rex;
answer reviews and confirm the engaged LP, other-king pressure, food/prayer,
death handling, and review-based respawns; use Anki Undo after a review and
after a direct room command; then leave and confirm the prior Combat target is
restored.
