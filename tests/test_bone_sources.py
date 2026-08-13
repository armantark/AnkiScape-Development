from __future__ import annotations

import unittest

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


def _runtime_context(player_data: dict, roll: float, activity_messages: list[str]):
    return RuntimeActionContext(
        player_data=player_data,
        random_random=lambda: roll,
        show_error_message=lambda _title, _message: None,
        deactivate_current_skill=lambda: None,
        award_skill_exp=lambda _key, xp: xp,
        award_hidden_skill_exp=lambda _key, _level_key, _xp: None,
        level_up_check=lambda _skill, _data: None,
        check_achievements=lambda _data: None,
        save_player_data=lambda: None,
        refresh_skill_availability=lambda: None,
        refresh_skill_availability_partial=lambda *_args: None,
        can_smith_any=lambda: False,
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


if __name__ == "__main__":
    unittest.main()
