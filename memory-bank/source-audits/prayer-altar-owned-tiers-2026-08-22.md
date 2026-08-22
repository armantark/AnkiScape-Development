# Owned POH altar tiers wired into Prayer (2026-08-22)

## Problem

Construction data carried all seven altar build rows (Oak through Gilded),
but `owned_gilded_altar_access_reasons_pure` gated owned-mode Prayer on the
gilded flag alone and `effective_gilded_altar_multiplier_pure` hardcoded the
2.5 gilded base. The six non-gilded altars were inert for Prayer.

## Sourced values

Darkan `src/main/java/com/rs/game/content/skills/prayer/BoneAltar.java`
Altar enum @ commit `3b47cfdfae8b95d543edc2c360aaad5086047804`
(file last touched by `1de4da89ead0088fa7bdec11d8af6bb990f1b412`, lines 54-60):

| Altar | Object ID | Base multiplier |
| --- | --- | --- |
| Oak | 13179 | 1.0 |
| Teak | 13182 | 1.1 |
| Cloth | 13185 | 1.25 |
| Mahogany | 13188 | 1.5 |
| Limestone | 13191 | 1.75 |
| Marble | 13194 | 2.0 |
| Gilded | 13197 | 2.5 |

`getMultiplier(litBurners)` (line 84): base + min(max(burners,0),2) * 0.5.
Burner lighting consumes one Clean marrentill per burner (lines ~200-210).
Build rows corroborate HouseObjects.kt:604-610 @ 7e7d67b481f1b94599de38a98c470419ab7c96b3
(already pinned in `data/construction_data.py`). This matches the settled design
line in `ankiscape-skill-expansion.md`: "tier ladder Oak→Gilded 100%–250%,
+50% of base per lit burner, max 3.5×".

## Model decision

A period chapel holds one altar, so the owned rate derives from the highest
tier present in `house_built_flags` (`owned_altar_id_pure`); building a higher
tier replaces it. Hosted mode stays flat 3.5×.

## Verification

`tests/test_construction.py::test_six_non_gilded_altars_build_and_set_the_owned_prayer_rate`
drives the real runtime handlers: builds each of the six tiers through
`handle_construction_answer`, then prays one Dragon bones (72 XP base)
through `handle_prayer_answer`, asserting 72 / 79.2 / 90 / 108 / 126 / 144 XP,
and 180 after upgrading to the gilded altar. Load-bearing proof: removing
`teak_altar` from `_OWNED_ALTAR_TIERS` fails the test with
`AssertionError: False is not true`; restored from a kept copy, passes again.
Plain lane: 4306 tests, OK (skipped=502). Offscreen Qt lane deferred to the
orchestrator's promotion gate per the standing contract's exception.
Reachability audit unchanged: 1598 actions; 2369 reachable items;
38 orphan inputs; 37 blocked actions.
