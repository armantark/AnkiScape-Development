# Quest Generated Pseudo-Item Cleanup - 2026-06-23

## Scope

Backend cleanup for quest-stage blockers that looked like impossible inventory requirements after the all-catalog stage-gate pass. This pass did not claim full minute-detail quest simulation. It removed audited false inventory/tool blockers, preserved legitimate external requirements, and kept unresolved generated quest detail behind action/route blockers instead of silently completing.

## Source Tiers Used

- Local 2011Scape item identities: `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml`.
- Local Darkan/2012scape quest evidence:
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/shieldofarrav/`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/dwarfcannon/NulodionD.java`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/dwarfcannon/CaptainLawgofD.java`
- Pinned generated historical wiki rows already present in `quest_catalog_generated.py`, including Rat Catchers `oldid=6589064`, Shield of Arrav `oldid=6326184`, Monkey Madness `oldid=6579359`, Elemental Workshop II quick guide `oldid=6333340`, Enlightened Journey quick guide `oldid=6332652`, King's Ransom `oldid=6548731`, Rocking Out quick guide `oldid=6537704`, The Fremennik Isles `oldid=6540919`, and the generated quick-guide rows for the route/spell cleanup quests.

## Implemented Corrections

- Shield of Arrav Black Arm stage 5 no longer requires `Weapon store key` as a pre-owned tool. This was first represented as Phoenix-partner key handoff actions, but the later 2026-06-23 quest-choice pass superseded that detail with a contextual Phoenix contact and no manual partner action blockers.
- `QuestStageRequirementCleanup` in `quest_data.py` is the focused override layer for generated parser mistakes. It removes exact quest/stage false blockers without editing `quest_catalog_generated.py`.
- Parser-shaped inventory/tool blockers converted or removed:
  - location/route text: `Lletya`, `Tears of Guthix cavern`, `Agility Pyramid`, `Rimmington`, `Port Sarim`, `Port Phasmatys`, `Ardougne`, `Rellekka`, `Pollnivneach`, `Wizard's Tower`, and generated teleport/tablet route text.
  - NPC/action/spell text: `Oronwen`, `Crafting table 3`, `Telegrab`, `Crumble Undead`, `NPC Contact`, `Enchant sapphire`, and generated jewellery-enchant spell rows.
  - quest/skill text: `Love Story`, `Ghosts Ahoy`, `Shilo Village`, `Making History`, `Elemental Workshop I`, `Let Them Eat Pie`, `Thieving`, and `Mining`.
  - broad prose buckets: `Random Bronze armours/weapons`, `Combat gear and good food`, `Food`, `Good Food`, `Armour`, and prayer-potion checklist text.
  - generated quest-flow items: Monkey Madness dentures/mould/talisman, Elemental Workshop II `Beaten Book`/`Slashed book`, Elemental Workshop III `Ragged book`, King's Ransom `Animate rock scroll`, Do No Evil `M'amulet mould`, Mourning's End Part I `Rotten apple`, Within the Light keys/crystal puzzle objects, and The Fremennik Isles yak-hide armour/round-shield crafting.
- Rat Catchers stage 1 no longer requires pre-owned `Rat poison`; it consumes `Vial`, `Clean kwuarm`, and `Red spiders' eggs`, then produces `Rat poison`.
- Dwarf Cannon completion now represents the post-quest `Ammo mould` source so Between a Rock and future cannonball gates are not blocked on an item consumed during Lawgof's handoff.
- Icthlarin's Little Helper and The Eyes of Glouphrie no longer require pre-owned `Bucket of sap`; they use an action gate to collect it from an evergreen tree.
- The live sweeps now report zero same-quest products required before production, zero route/location/skill phrase blockers in inventory/tool fields, and zero literal quest-name blockers.

## Verification Snapshot

- Targeted catalog tests passed:
  `python3 -m unittest tests.test_quest_catalog.TestQuestCatalog.test_generated_pseudo_items_are_not_inventory_stage_blockers tests.test_quest_catalog.TestQuestCatalog.test_same_quest_products_are_not_required_before_they_are_produced tests.test_quest_catalog.TestQuestCatalog.test_dwarf_cannon_has_source_backed_noncombat_stage_requirements tests.test_quest_catalog.TestQuestCatalog.test_shield_of_arrav_has_source_backed_route_stage_requirements`
- Targeted logic/integration tests passed:
  `python3 -m unittest tests.test_logic.TestLogic.test_dwarf_cannon_stage_gates_noncombat_items_actions_and_reward tests.test_logic.TestLogic.test_shield_of_arrav_black_arm_route_requires_key_and_isolates_variant_rewards`
  `python3 -m unittest tests.test_integration_smoke.TestIntegrationSmoke.test_quest_answer_progresses_dwarf_cannon_repairs_without_combat_gate tests.test_integration_smoke.TestIntegrationSmoke.test_quest_answer_resolves_shield_of_arrav_route_combat_gate`
- Targeted Qt test passed:
  `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_shield_black_arm_partner_key_action`
- Strict same-quest product-order audit reports `same_quest_required_before_produced: 0`.
- `python3 tools/audit_quest_stage_gate_coverage.py` reports 194/194 quests with stage requirements, 1,119 stage rows, 120 produced-inventory rows, 174 quests with item/tool blockers, 190 quests with action blockers, 32 quests with route blockers, 120 quests with combat blockers, and 185/288 resolver-ready combat encounters.

## Remaining Gaps

- Full minute-detail source replacement is still open for generated broad rows and external/prerequisite item reclaim routes. The cleanup sweeps removed the known parser-pseudo and same-quest quest-object blockers; remaining item blockers should be treated as real external/prerequisite requirements unless a later source audit proves otherwise.
- This pass intentionally keeps real external or prerequisite item requirements as item blockers when the item is source-backed and not an audited parser mistake.
