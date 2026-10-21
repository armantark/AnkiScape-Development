from __future__ import annotations

import random
import sys
import unittest
from itertools import cycle
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import (
    COMBAT_ENEMY_DATA,
    EQUIPMENT_DATA,
    ITEM_DEFINITIONS,
    ORE_DATA,
    PRAYER_DATA,
    UTILITY_ACTIVITY_DATA,
)
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic_pure.logic_pure import (
    apply_combat_burst_pure,
    apply_prayer_action_pure,
    apply_utility_activity_pure,
    combat_target_locked_reasons_pure,
    equip_item_pure,
)
from ankiscape.runtime.runtime_actions import RuntimeActionContext, handle_utility_answer
from ankiscape.data.shop_data import SHOP_DATA
from ankiscape.logic.farming_logic import add_farm_queue_step_pure
from ankiscape.logic.shop_logic import apply_shop_buy_pure, apply_shop_service_pure
from tests.test_integration_smoke import (
    _DummyCol,
    _DummyMW,
    _FakeReviewer,
    _install_runtime_fakes,
    _load_addon_as_package,
)


def _runtime_context(player_data: dict, roll: float, activity_messages: list[str]):
    return RuntimeActionContext(
        player_data=player_data,
        random_random=lambda: roll,
        show_error_message=lambda _title, _message: None,
        deactivate_current_skill=lambda _reason=None: None,
        award_skill_exp=lambda _key, xp: xp,
        award_hidden_skill_exp=lambda _key, _level_key, _xp: None,
        level_up_check=lambda _skill, _data: None,
        check_achievements=lambda _data: None,
        save_player_data=lambda: None,
        refresh_skill_availability=lambda: None,
        show_exp=lambda _xp: None,
        show_activity_gain=activity_messages.append,
        implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda _before: None,
    )


class BoneAcquisitionToEctofuntusTests(unittest.TestCase):
    _BONES = (
        (
            "burnt_bones", "Burnt bones", "Burnt bonemeal", 4.5,
            "utility", None, {"Burnt bones": 1},
        ),
        (
            "zogre_bones", "Zogre bones", "Zogre bonemeal", 22.5,
            "combat", "zogre", {"Zogre bones": 1, "Ogre coffin key": 1},
        ),
        (
            "jogre_bones", "Jogre bones", "Jogre bonemeal", 15.0,
            "combat", "jogre", {"Jogre bones": 1},
        ),
        (
            "shaikahan_bones", "Shaikahan bones", "Shaikahan bonemeal", 25.0,
            "combat", "shaikahan",
            {
                "Raw karambwan": 0,
                "Steel spear": 0,
                "Karambwan paste": 0,
                "Steel spear (kp)": 0,
                "Shaikahan bones": 1,
            },
        ),
        (
            "fayrg_bones", "Fayrg bones", "Fayrg bonemeal", 84.0,
            "coffin", 63.5 / 125,
            {"Zogre bones": 1, "Ogre coffin key": 0, "Fayrg bones": 1},
        ),
        (
            "raurg_bones", "Raurg bones", "Raurg bonemeal", 96.0,
            "coffin", 77.5 / 125,
            {"Zogre bones": 1, "Ogre coffin key": 0, "Raurg bones": 1},
        ),
        (
            "ourg_bones", "Ourg bones", "Ourg bonemeal", 140.0,
            "coffin", 83.5 / 125,
            {"Zogre bones": 1, "Ogre coffin key": 0, "Ourg bones": 1},
        ),
        (
            "frost_dragon_bones", "Frost dragon bones", "Frost dragon bonemeal",
            180.0, "combat", "frost_dragon", {"Frost dragon bones": 1},
        ),
    )

    @staticmethod
    def _combat_player(
        target_id: str,
        inventory: dict[str, int] | None = None,
        equipment: dict[str, str] | None = None,
    ) -> dict:
        quests = {}
        if target_id == "zogre":
            quests["zogre_flesh_eaters"] = {"started": True, "completed": False}
        elif target_id == "shaikahan":
            quests["tai_bwo_wannai_trio"] = {"started": True, "completed": True}
        return {
            "inventory": dict(inventory or {}),
            "equipment": dict(equipment or {}),
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "ranged_level": 99,
            "magic_level": 99,
            "constitution_level": 99,
            "dungeoneering_level": 99,
            "attack_exp": 0.0,
            "strength_exp": 0.0,
            "defense_exp": 0.0,
            "ranged_exp": 0.0,
            "magic_exp": 0.0,
            "constitution_exp": 0.0,
            "current_combat_target": target_id,
            "combat_attack_style": "accurate",
            "combat_lifepoints": 990,
            "combat_auto_flee": False,
            "combat_supply_loadout": {},
            "combat_encounter": {"target_id": target_id, "enemy_lifepoints": 1},
            "combat_kill_counts": {},
            "quests": quests,
        }

    def _kill(
        self,
        target_id: str,
        inventory: dict[str, int] | None = None,
        equipment: dict[str, str] | None = None,
    ) -> dict:
        acquired, ok, result = apply_combat_burst_pure(
            self._combat_player(target_id, inventory, equipment),
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=lambda: 0.0,
            allow_bank_run=False,
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["kills"], 1)
        return acquired["inventory"]

    def _acquire(self, route: str, selector: object) -> dict:
        if route == "utility":
            inventory, _xp, ok, processed = apply_utility_activity_pure(
                "gather_burnt_bones", {}, UTILITY_ACTIVITY_DATA
            )
            self.assertTrue(ok)
            self.assertEqual(processed, 1)
            return inventory
        if route == "combat" and selector != "shaikahan":
            return self._kill(str(selector))
        if route == "combat":
            inventory, _xp, ok, processed = apply_utility_activity_pure(
                "grind_raw_karambwan",
                {"Raw karambwan": 1, "Steel spear": 1},
                UTILITY_ACTIVITY_DATA,
            )
            self.assertTrue(ok)
            self.assertEqual(processed, 1)
            inventory, _xp, ok, processed = apply_utility_activity_pure(
                "poison_steel_spear_with_karambwan",
                inventory,
                UTILITY_ACTIVITY_DATA,
            )
            self.assertTrue(ok)
            self.assertEqual(processed, 1)
            inventory, equipment, equipped = equip_item_pure(
                "Steel spear (kp)", inventory, {}, EQUIPMENT_DATA
            )
            self.assertTrue(equipped)
            self.assertEqual(equipment, {"weapon": "Steel spear (kp)"})
            return self._kill("shaikahan", inventory, equipment)

        inventory = self._kill("zogre")
        inventory, _xp, ok, processed = apply_utility_activity_pure(
            "loot_ogre_coffin",
            inventory,
            UTILITY_ACTIVITY_DATA,
            r_output=float(selector),
        )
        self.assertTrue(ok)
        self.assertEqual(processed, 1)
        self.assertEqual(inventory["Ogre coffin key"], 0)
        return inventory

    def test_zogre_shaikahan_and_jogre_access_gates_apply_before_kills(self):
        cases = (
            (
                "zogre",
                {},
                {},
                ("Open Jiggig during Zogre Flesh Eaters",),
                {"zogre_flesh_eaters": {"started": True, "completed": False}},
            ),
            (
                "shaikahan",
                {},
                {"weapon": "Steel spear (kp)"},
                ("Complete Tai Bwo Wannai Trio",),
                {"tai_bwo_wannai_trio": {"started": True, "completed": True}},
            ),
            ("jogre", {}, {}, (), {}),
        )
        for target_id, inventory, equipment, locked, quests in cases:
            with self.subTest(target=target_id):
                player = self._combat_player(target_id, inventory, equipment)
                player["quests"] = {}
                self.assertEqual(
                    combat_target_locked_reasons_pure(
                        player,
                        target_id,
                        COMBAT_ENEMY_DATA,
                        equipment_data=EQUIPMENT_DATA,
                    ),
                    locked,
                )
                player["quests"] = quests
                self.assertEqual(
                    combat_target_locked_reasons_pure(
                        player,
                        target_id,
                        COMBAT_ENEMY_DATA,
                        equipment_data=EQUIPMENT_DATA,
                    ),
                    (),
                )

    def test_frost_dragon_requires_level_85_dungeoneering_on_surface_and_kernel(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        expected_reasons = ("Dungeoneering level 85",)

        self.assertEqual(
            combat_target_locked_reasons_pure(
                player,
                "frost_dragon",
                COMBAT_ENEMY_DATA,
                equipment_data=EQUIPMENT_DATA,
            ),
            expected_reasons,
        )

        player["current_combat_target"] = "frost_dragon"
        unchanged, ok, result = apply_combat_burst_pure(
            player,
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=lambda: 0.0,
            allow_bank_run=False,
        )
        self.assertFalse(ok)
        self.assertEqual(result["reason"], "combat_locked")
        self.assertEqual(result["locked_reasons"], expected_reasons)
        self.assertIsNone(
            unchanged.get("combat_encounter", {}).get("target_id")
        )

        player["dungeoneering_level"] = 85
        self.assertEqual(
            combat_target_locked_reasons_pure(
                player,
                "frost_dragon",
                COMBAT_ENEMY_DATA,
                equipment_data=EQUIPMENT_DATA,
            ),
            (),
        )

    def test_all_eight_sources_complete_the_real_ectofuntus_chain(self):
        for (
            material_id,
            bone,
            bonemeal,
            base_xp,
            route,
            selector,
            acquired_inventory,
        ) in self._BONES:
            with self.subTest(bone=bone):
                inventory = self._acquire(route, selector)
                self.assertEqual(inventory, acquired_inventory)

                inventory.update({"Empty pot": 1, "Bucket": 1})
                inventory, _xp, ok, processed = apply_utility_activity_pure(
                    f"grind_prayer_{material_id}", inventory, UTILITY_ACTIVITY_DATA
                )
                self.assertTrue(ok)
                self.assertEqual(processed, 1)
                ground_inventory = {
                    **acquired_inventory,
                    bone: 0,
                    "Empty pot": 0,
                    "Bucket": 1,
                    bonemeal: 1,
                }
                self.assertEqual(inventory, ground_inventory)

                inventory, _xp, ok, processed = apply_utility_activity_pure(
                    "collect_ectofuntus_slime", inventory, UTILITY_ACTIVITY_DATA
                )
                self.assertTrue(ok)
                self.assertEqual(processed, 1)
                slime_inventory = {
                    **ground_inventory,
                    "Bucket": 0,
                    "Bucket of slime": 1,
                }
                self.assertEqual(inventory, slime_inventory)

                inventory, xp, ok, outputs = apply_prayer_action_pure(
                    f"ectofuntus_{material_id}", inventory, PRAYER_DATA
                )
                self.assertTrue(ok)
                self.assertEqual(xp, base_xp * 4)
                self.assertEqual(
                    outputs,
                    {"Bucket": 1, "Empty pot": 1, "Ecto-token": 5},
                )
                self.assertEqual(
                    inventory,
                    {
                        **slime_inventory,
                        bonemeal: 0,
                        "Bucket of slime": 0,
                        "Bucket": 1,
                        "Empty pot": 1,
                        "Ecto-token": 5,
                    },
                )

    def test_coffin_discrete_slots_preserve_exact_reward_distribution(self):
        counts = {
            "Zogre bones": 0,
            "Fayrg bones": 0,
            "Raurg bones": 0,
            "Ourg bones": 0,
            None: 0,
        }
        for slot in range(125):
            inventory, _xp, ok, processed = apply_utility_activity_pure(
                "loot_ogre_coffin",
                {"Ogre coffin key": 1},
                UTILITY_ACTIVITY_DATA,
                r_output=(slot + 0.5) / 125,
            )
            self.assertTrue(ok)
            self.assertEqual(processed, 1)
            outputs = [item for item in counts if item and inventory.get(item) == 1]
            self.assertLessEqual(len(outputs), 1)
            counts[outputs[0] if outputs else None] += 1

        self.assertEqual(
            counts,
            {
                "Zogre bones": 63,
                "Fayrg bones": 14,
                "Raurg bones": 6,
                "Ourg bones": 3,
                None: 39,
            },
        )

    def test_coffin_first_and_last_rolls_both_consume_the_key(self):
        for roll, expected_output in ((0.0, "Zogre bones"), (0.999999, None)):
            with self.subTest(roll=roll):
                inventory, _xp, ok, processed = apply_utility_activity_pure(
                    "loot_ogre_coffin",
                    {"Ogre coffin key": 1},
                    UTILITY_ACTIVITY_DATA,
                    r_output=roll,
                )
                self.assertTrue(ok)
                self.assertEqual(processed, 1)
                self.assertEqual(inventory["Ogre coffin key"], 0)
                if expected_output is None:
                    self.assertEqual(inventory, {"Ogre coffin key": 0})
                else:
                    self.assertEqual(inventory[expected_output], 1)

    def test_coffin_runtime_uses_injected_roll_and_records_actual_gain(self):
        cases = (
            (63.5 / 125, {"Fayrg bones": 1}, "+1 Fayrg bones"),
            (0.999999, {}, "Looted an Ogre coffin"),
        )
        for roll, expected_outputs, expected_message in cases:
            with self.subTest(roll=roll):
                player_data = {
                    "current_utility": "loot_ogre_coffin",
                    "inventory": {"Ogre coffin key": 1},
                    "completed_achievements": [],
                }
                activity_messages: list[str] = []

                self.assertTrue(
                    handle_utility_answer(
                        _runtime_context(player_data, roll, activity_messages)
                    )
                )

                self.assertEqual(player_data["inventory"]["Ogre coffin key"], 0)
                for item, amount in expected_outputs.items():
                    self.assertEqual(player_data["inventory"][item], amount)
                self.assertEqual(
                    player_data["action_telemetry"]["actions"][
                        "utility:loot_ogre_coffin"
                    ]["outputs"],
                    expected_outputs,
                )
                self.assertEqual(activity_messages[-1], expected_message)


class ShaikahanPlayerRouteTests(unittest.TestCase):
    def setUp(self):
        self._original_modules = dict(sys.modules)
        _install_runtime_fakes()
        self.addon = _load_addon_as_package("ankiscape_shaikahan_route")
        self.addon.mw = _DummyMW(_DummyCol({"ankiscape_cadence_kernel": True}))
        self.messages = []
        self.addon.save_player_data = lambda: None
        self.addon._refresh_skill_availability = lambda: None
        self.addon.update_review_hud = lambda *_args: None
        self.addon.update_review_status_badge = lambda *_args: None
        self.addon._show_exp = lambda _xp: None
        self.addon._show_activity_gain = self.messages.append
        self.addon.show_error_message = lambda title, message: self.messages.append(
            f"{title}: {message}"
        )
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        for skill in (
            "agility", "attack", "constitution", "cooking", "defense",
            "farming", "fishing", "herblore", "strength", "thieving",
        ):
            player[f"{skill}_level"] = 99
            player[f"{skill}_exp"] = 13034431.0
        player["combat_lifepoints"] = 990
        self.addon._state.player_data = player
        self.reviews = 0

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._original_modules)

    @property
    def player(self):
        return self.addon._state.player_data

    def _review(self, skill, target_key, target, rng=lambda: 0.5):
        self.player[target_key] = target
        self.addon._state.current_skill = skill
        self.addon._state.card_turned = True
        self.addon._state.answer_shown = True
        self.addon._state.exp_awarded = False
        with patch.object(self.addon.random, "random", rng):
            self.assertEqual(
                self.addon.on_answer_card(
                    _FakeReviewer(), 3, lambda _self, _ease: "answered"
                ),
                "answered",
            )
        self.reviews += 1
        self.assertFalse(self.player.get("combat_grave"), self.messages[-5:])

    def _collect(self, item, quantity, skill, target_key, target, rng):
        for _ in range(2000):
            if self.player["inventory"].get(item, 0) >= quantity:
                return
            self._review(skill, target_key, target, rng)
        self.fail(f"{target} did not produce {quantity} {item}: {self.messages[-5:]}")

    def _buy(self, shop_id, item, quantity=1):
        row = next(row for row in SHOP_DATA[shop_id]["stock"] if row["item_name"] == item)
        updated, result = apply_shop_buy_pure(self.player, shop_id, row["id"], quantity)
        self.assertTrue(result["allowed"], result)
        self.assertEqual(result["quantity"], quantity)
        self.player.update(updated)

    def _farm_step(self, kind, **details):
        updated, step_id, message = add_farm_queue_step_pure(
            self.player, kind, "falador_herb", **details
        )
        self.assertIsNotNone(step_id, message)
        self.player.update(updated)
        self._review("Utilities", "current_utility", "bankstanding", lambda: 0.99)
        self.assertFalse(self.player["farm_queue"])

    def _finish_quest(self, quest_id):
        self.assertTrue(self.addon.on_set_quest(quest_id), self.messages[-5:])
        for _ in range(100):
            if self.player["quests"][quest_id]["completed"]:
                return
            self._review("Quests", "current_quest", quest_id)
            self.assertNotIn("Quest blocked:", " ".join(self.messages[-1:]))
        self.fail(f"{quest_id} did not complete: {self.messages[-5:]}")

    def test_review_route_earns_trio_and_shaikahan_bone_with_both_gates(self):
        self.assertFalse(any(q["completed"] for q in self.player["quests"].values()))
        self.assertFalse(any(self.player["inventory"].values()))
        self._collect("Coins", 6000, "Thieving", "current_thieving", "pickpocket_paladin", lambda: 0.0)
        for shop_id, item, quantity in (
            ("alkharid_general_store", "Chisel", 1),
            ("gerrants_fishy_business", "Fishing rod", 1),
            ("arnolds_eclectic_supplies", "Small fishing net", 1),
            ("aemads_adventuring_supplies", "Knife", 1),
            ("aemads_adventuring_supplies", "Tinderbox", 1),
            ("aemads_adventuring_supplies", "Vial of water", 2),
            ("frincos_fabulous_herb_shop", "Pestle and mortar", 1),
            ("karamja_wines_spirits_and_beers", "Karamjan rum", 1),
            ("arheins_shop", "Seaweed", 1),
            ("trader_stans_trading_post", "Banana", 1),
            ("alices_farming_shop", "Rake", 1),
            ("alices_farming_shop", "Seed dibber", 1),
            ("alices_farming_shop", "Spade", 1),
            ("smithing_smiths_shop", "Iron scimitar", 1),
            ("alfonso_waiter_shop", "Lobster", 10),
        ):
            self._buy(shop_id, item, quantity)
        self._finish_quest("druidic_ritual")
        print("Route: Druidic Ritual completion earned through reviews")

        quest_id = "jungle_potion"
        self.assertTrue(self.addon.on_set_quest(quest_id))
        for target, grimy, clean in (
            ("clean_snake_weed", "Grimy snake weed", "Clean snake weed"),
            ("clean_ardrigal", "Grimy ardrigal", "Clean ardrigal"),
            ("clean_sito_foil", "Grimy sito foil", "Clean sito foil"),
            ("clean_volencia_moss", "Grimy volencia moss", "Clean volencia moss"),
            ("clean_rogues_purse", "Grimy rogue's purse", "Clean rogue's purse"),
        ):
            self._review("Quests", "current_quest", quest_id)
            self.assertEqual(self.player["inventory"][grimy], 1)
            self._collect(clean, 1, "Herblore", "current_herblore", target, lambda: 0.5)
            self._review("Quests", "current_quest", quest_id)
        self.assertTrue(self.player["quests"][quest_id]["completed"])
        print("Route: Jungle Potion completion earned through ordered searches and cleaning")

        farmer_rng = random.Random(20260929).random
        self._collect("Toadflax seed", 1, "Thieving", "current_thieving", "pickpocket_master_farmer", farmer_rng)
        self._farm_step("plant", crop_id="toadflax")
        for _ in range(240):
            if self.player["farm_patches"]["falador_herb"]["stage"] == 4:
                break
            self._review("Utilities", "current_utility", "bankstanding")
        self._farm_step("harvest")
        self.assertGreaterEqual(self.player["inventory"].get("Grimy toadflax", 0), 2)
        for target, output in (
            ("clean_toadflax", "Clean toadflax"),
            ("unf_toadflax", "Toadflax potion (unf)"),
        ):
            self._collect(output, 2, "Herblore", "current_herblore", target, lambda: 0.5)
        self._collect("Swamp toad", 2, "Utilities", "current_utility", "gather_swamp_toads", lambda: 0.5)
        self._collect("Toad's legs", 2, "Utilities", "current_utility", "remove_swamp_toad_legs", lambda: 0.5)
        self._collect("Agility potion (3)", 2, "Herblore", "current_herblore", "finished_agility_potion", lambda: 0.5)
        updated, result = apply_shop_service_pure(self.player, "bob_barter_decant_four", 4)
        self.assertTrue(result["allowed"], result)
        self.player.update(updated)
        self.assertEqual(self.player["inventory"]["Agility potion (4)"], 1)
        self.assertTrue(self.addon.on_equip_item("Iron scimitar"))
        combat_rolls = cycle((0.09, 0.5, 0.5, 0.5))
        self._collect("Steel spear", 2, "Combat", "current_combat_target", "hobgoblin_unarmed", lambda: next(combat_rolls))
        self._collect("Jogre bones", 1, "Combat", "current_combat_target", "jogre", lambda: 0.5)
        print("Route: supplies obtained from shops, Farming, Herblore, Utilities and full-health combat")

        quest_id = "tai_bwo_wannai_trio"
        self.assertTrue(self.addon.on_set_quest(quest_id))
        self._buy("tiadeches_karambwan_stall", "Raw karambwan", 2)
        self._review("Combat", "current_combat_target", "shaikahan")
        self.assertIn("Complete Tai Bwo Wannai Trio", " ".join(self.messages[-2:]))
        self.assertNotEqual(self.player["combat_encounter"].get("target_id"), "shaikahan")
        self.assertEqual(self.player["inventory"].get("Shaikahan bones", 0), 0)
        print("Gate: no Shaikahan bone before Trio completion")

        self._finish_quest(quest_id)
        self.assertEqual(
            set(self.player["quest_combat_encounters"][quest_id]),
            {"tai_bwo_wannai_trio_monkey", "tai_bwo_wannai_trio_jogre"},
        )
        print("Route: Trio completion earned through both real encounters, including Monkey")
        self._review("Combat", "current_combat_target", "shaikahan")
        self.assertIn("Equip a karambwan-poisoned spear", " ".join(self.messages[-2:]))
        self.assertNotEqual(self.player["combat_encounter"].get("target_id"), "shaikahan")
        self.assertEqual(self.player["inventory"].get("Shaikahan bones", 0), 0)
        self.assertEqual(self.player["equipment"]["weapon"], "Iron scimitar")
        print("Gate: wrong weapon blocks the encounter and grants no bone")

        self._buy("tiadeches_karambwan_stall", "Raw karambwan", 1)
        self._review("Utilities", "current_utility", "grind_raw_karambwan")
        self._review("Utilities", "current_utility", "poison_steel_spear_with_karambwan")
        self.assertEqual(self.player["inventory"]["Steel spear (kp)"], 1)
        self.assertTrue(self.addon.on_equip_item("Steel spear (kp)"))
        self._review("Combat", "current_combat_target", "shaikahan")
        result = self.player["combat_last_result"]
        self.assertEqual(result["target_id"], "shaikahan")
        self.assertEqual(
            result["player_damage"] + result["enemy_lifepoints"] - result["enemy_healing"],
            COMBAT_ENEMY_DATA["shaikahan"]["stats"]["hitpoints"],
        )
        self._collect("Shaikahan bones", 1, "Combat", "current_combat_target", "shaikahan", lambda: 0.5)
        self.assertEqual(self.player["inventory"]["Shaikahan bones"], 1)
        self.assertEqual(self.player["carried_inventory"]["shaikahan"]["Shaikahan bones"], 1)
        self.assertEqual(self.player["combat_kill_counts"]["shaikahan"], 1)
        self.assertEqual(self.player["equipment"]["weapon"], "Steel spear (kp)")
        print(f"Route complete: full-health Shaikahan killed; one bone in pack; {self.reviews} real reviews")


if __name__ == "__main__":
    unittest.main()
