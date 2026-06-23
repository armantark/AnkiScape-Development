# Shield of Arrav Stage Detail Audit - 2026-06-22

## Scope

Focused backend/frontend slice for Shield of Arrav. The goal was to remove the quest from the deferred branch/partner bucket without flattening Phoenix Gang and Black Arm Gang into start locks.

## Source Tiers Used

- Local 2011Scape: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/varrock/reldo.plugin.kts` confirms the local checkout has Reldo dialogue but not a full Shield of Arrav quest implementation.
- Local 2011Scape item identities: `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml` confirms Shield-specific items such as Book, Phoenix hq key, Weapon store key, Intel report, Broken shield variants, Phoenix crossbow, Certificate, and Half certificate variants.
- Darkan/2012scape quest implementation: `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/shieldofarrav/ShieldOfArrav.java` plus route dialogue files for Reldo, Baraek, Charlie, Straven, Katrine, Curator Haig Halen, King Roald, and the quest book.
- Darkan combat definitions: `jonny_the_beard.json` and `weaponsmaster.json` provide resolver-ready hitpoints, combat levels, attack/strength/defence payloads, max hit, attack style, and passive/aggression config.
- Pinned historical wiki row: `https://runescape.wiki/w/Shield_of_Arrav?oldid=6326184` is retained for release/catalog metadata and cross-checking the branch combat prose.

## Implemented Data Model

- `QuestStageRequirement.variant` now distinguishes route alternatives on the same stage. Empty variant rows remain mandatory. Non-empty variants are selected by satisfied `required_routes`, so a Phoenix player does not see Black Arm blockers and vice versa.
- Shield of Arrav is now a 12-stage focused override in `quest_data.py`.
- Stage 4 branches on `Join the Phoenix Gang` versus `Join the Black Arm Gang`.
- Stage 5 gates Phoenix behind Jonny the beard and produces `Intel report`; Black Arm now requires Phoenix-partner handoff actions, gates the Weaponsmaster battle, and produces the `Weapon store key` plus two `Phoenix crossbow` items after the stage resolves. This avoids blocking the Black Arm route on a quest-specific key the player cannot own before the partner handoff.
- Stage 6 consumes the route proof item and joins the selected gang. Phoenix also produces the `Weapon store key` for the partner route; Black Arm consumes the two crossbows.
- Stage 7 produces the selected shield half, stage 8 shows it to King Roald, stage 9 consumes it at Curator Haig Halen and produces two route-specific half certificates.
- Stage 10 consumes one Phoenix half certificate and one Black Arm half certificate to produce the full `Certificate`, making partner exchange explicit without pretending it is solved by a start lock.
- Stage 11 consumes the full certificate and stage 12 completes the quest. Completion reward is `Coins x1200`, sourced from the Darkan implementation.

## Frontend And Assets

- The Quests tab already surfaces `blocked_at_stage`; a Qt/offscreen test now verifies Shield of Arrav displays both route blockers at the branch decision.
- Quest-stage item icons were fetched with `tools/fetch_assets.py` into `questitems/` and recorded in `assets_provenance.json` for the book, intel report, weapon store key, Phoenix crossbow, both broken shield halves, both half certificates, and the certificate.

## Verification Snapshot

- Targeted pure/catalog/registry tests passed: `python3 -m unittest tests.test_logic tests.test_quest_catalog tests.test_skill_and_item_registry`.
- Targeted Qt test passed: `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_shield_of_arrav_route_branch_blockers`.
- Targeted integration smoke coverage includes `tests.test_integration_smoke.TestIntegrationSmoke.test_quest_answer_resolves_shield_of_arrav_route_combat_gate`.
- Post-slice audit at the original Shield scope: 194/194 quests with stage requirements, 440 stage requirement rows, 174 quests with item/tool blockers, 120 quests with combat blockers, 285 combat rows, and 177 resolver-ready combat rows.
- Follow-up 2026-06-23: a stricter same-quest product-order audit found the Black Arm `Weapon store key` as a remaining false blocker. The focused correction moved it to Phoenix-partner action gates and stage-local `produced_inventory`; the invariant now reports zero same-quest products required or consumed before production.
- `tools/audit_quest_combat_stat_gaps.py` still reports 108 statless combat rows. Full all-quest minute-detail parity remains open.

## Manual Anki Test Instructions

1. Start Anki with this add-on checkout active and open AnkiScape -> Quests.
2. Set or seed the save so `shield_of_arrav` is started at progress 4 with no `quest_route_states["shield_of_arrav"]`. Confirm the quest card is `blocked_at_stage` and says both route blockers: Black Arm and Phoenix.
3. Add `quest_route_states["shield_of_arrav"] = ["Join the Black Arm Gang"]`, keep `quest_combat_config.resolver_enabled` false, and confirm the blocker mentions the two Phoenix-partner key handoff actions plus the globally locked Weaponsmaster battle. It must not say `Needs Weapon store key`.
4. Add the two Black Arm key handoff action flags, set `quest_combat_config.resolver_enabled` true, and use a combat level at least 23. Answer one Quest review. Confirm it records the Weaponsmaster encounter and does not advance the stage or grant crossbows in the same review.
5. Answer another Quest review. Confirm stage 5 advances and produces `Weapon store key x1` plus `Phoenix crossbow x2`.
6. For the Phoenix branch, repeat from progress 5 with route `Join the Phoenix Gang`. Confirm Jonny the beard blocks until the battle is resolved, then the next review produces `Intel report`.
7. Complete the certificate chain by providing the opposite half certificate at stage 10. Confirm the quest only awards quest points and `Coins x1200` after the full certificate is handed to King Roald, and the reward does not fire twice.

## Remaining Gaps

- This slice resolves Shield of Arrav branch and partner certificate mechanics at the current stage-gate layer. It does not implement real trade/partner UI, combat simulation, or remaining all-quest per-stage extraction.
- OSRS wiki image files were used only as asset sprites through the existing asset tool; quest logic and combat stats came from local 2011Scape/Darkan plus the pinned historical wiki metadata row.
