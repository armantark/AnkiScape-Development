# Shipped-skills gap re-audit — 2026-07-09, pass 3

## Scope and classification rule

This is the mandatory fresh pass after `mine-runtime-glory-variants` merged and the transcription lane drained. Four independent read-only comparisons covered all 11 shipped review skills plus their generic live input-preparation and light-source handlers on current `main` against the local 2011Scape rev 667 checkout at `/Users/ArmanTarkhanian1/Downloads/game-main`. A row is a transcription only when game-main supplies a live runtime binding plus authoritative data. Static, commented, unbound, emulator-absent, or integration-design-dependent content is not auto-built.

## New transcription batches

- `fletch-colored-feather-options`: every live feathering row accepts the ordinary feather plus all five coloured feather IDs. AnkiScape currently hard-requires only `Feather`, although Hunter already produces and registers the coloured inputs. Preserve every existing Fletching level, XP value, output, and quantity while consuming the selected exact feather type.
- `craft-leather-thread-semantics`: every live leather-crafting action requires Thread and consumes one Thread on the source's exact 1-in-5 roll. Needle stays implicit under the settled toolbelt convention.
- `craft-held-mould-pipe-gates`: jewellery, silver, and glassblowing actions require their matching non-consumed mould or Glassblowing pipe. The repository's settled carried-item design already specifies bank ownership in default mode and carried-slot presence in advanced mode, so this is a source-backed transcription rather than a new design decision.
- `fm-light-source-actions`: all 11 live Firemaking-gated raw-to-lit light-source transformations and their inverse extinguish actions are absent. Port exact source IDs and levels as zero-XP Utility activities; darkness, location, drop, and acquisition behavior remains out of scope.
- `herb-runtime-input-prep`: the live Vial to Vial of water and Swamp toad to Toad's legs handlers directly supply shipped unfinished-potion and Agility-potion recipes. Port the exact 1:1, zero-XP transformations under existing Utility conventions.

The first three batches share the materials, readiness, carried-overlay, and reconciliation paths, so they are explicitly serialized in that order. Firemaking and Herblore are independent and may run in parallel.

## Coverage with no additional safe gap

- Mining, Woodcutting, Fishing, and Smithing remain complete against all live source rows after the previously merged transcription batches.
- Cooking has no additional live omission beyond its existing karambwan-family stub.
- Firemaking's 13 log rows and Inferno-adze behavior remain complete; bonfires, pyres, and beacons remain existing stubs.
- Runecrafting's standard runes, combination runes, active tiaras, and pouch behavior remain represented. Spatial talisman, ruins, portal, and Abyss routing handlers do not map to the review-action skill abstraction.
- Hunter still has no live skill action tree in game-main; its missing families remain existing stubs.
- The other generic water-container rows and dairy-cow milking do not directly feed a currently shipped skill target. They are not included in the narrow shipped-skill transcription lane.

## Owner-design boundary retained

game-main has live temporary noncombat potion boosts and timed stat decay, but AnkiScape has no noncombat current-level/duration contract. Porting those handlers would require a new state model and could collide with the no-Combat implementation constraint, so the audit did not auto-build or misclassify them as a cheap transcription. This remains an owner design decision after the safe transcription lane completes.

No Combat or Prayer implementation was expanded or changed by this audit.
