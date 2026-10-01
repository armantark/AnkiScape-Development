import struct
from pathlib import Path
import unittest

import pkg_alias  # noqa: F401

from ankiscape.core.constants import EQUIPMENT_DATA, ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import (
    CURRENT_CONFIG_VERSION,
    default_player_data,
    migrate_loaded_data,
)
from ankiscape.data.brawling_gloves_data import BRAWLING_GLOVE_DATA
from ankiscape.data.combat_data import COMBAT_ENEMY_DATA
from ankiscape.logic.brawling_gloves_logic import (
    apply_brawling_gloves_xp_pure,
    apply_brawling_wilderness_risk_pure,
    brawling_glove_state_pure,
    set_brawling_wilderness_target_pure,
)
from ankiscape.logic_pure.logic_pure_combat_engine import apply_combat_burst_pure
from ankiscape.logic_pure.logic_pure_combat_model import (
    _combat_roll_drops,
    _combat_select_enemy_attack_pure,
)


def _player():
    return default_player_data(ORE_DATA, ITEM_DEFINITIONS)


class BrawlingGloveDataTests(unittest.TestCase):
    def test_period_identities_limits_and_multipliers(self):
        self.assertEqual(
            {
                skill_id: (
                    spec["item_id"],
                    spec["max_actions"],
                    spec["outside_multiplier"],
                    spec["wilderness_multiplier"],
                )
                for skill_id, spec in BRAWLING_GLOVE_DATA.items()
            },
            {
                "woodcutting": (13850, 732, 1.5, 4.0),
                "firemaking": (13851, 1200, 1.5, 5.0),
                "mining": (13852, 575, 1.5, 4.0),
                "smithing": (13855, 434, 1.5, 4.0),
                "fishing": (13856, 400, 1.5, 5.0),
                "cooking": (13857, 1109, 1.5, 4.0),
            },
        )
        for spec in BRAWLING_GLOVE_DATA.values():
            self.assertEqual(EQUIPMENT_DATA[spec["item_name"]].slot, "hands")

    def test_assets_are_registered_and_bounded(self):
        by_name = {definition.display_name: definition for definition in ITEM_DEFINITIONS}
        for spec in BRAWLING_GLOVE_DATA.values():
            path = Path(by_name[spec["item_name"]].asset_path)
            self.assertTrue(path.is_file(), path)
            with path.open("rb") as handle:
                self.assertEqual(handle.read(8), b"\x89PNG\r\n\x1a\n")
                length = struct.unpack(">I", handle.read(4))[0]
                self.assertEqual(handle.read(4), b"IHDR")
                width, height = struct.unpack(">II", handle.read(8))
            self.assertEqual(length, 13)
            self.assertLessEqual(max(width, height), 64)


class BrawlingGloveLogicTests(unittest.TestCase):
    def _equipped(self, skill_id="cooking"):
        data = _player()
        item_name = BRAWLING_GLOVE_DATA[skill_id]["item_name"]
        data["inventory"][item_name] = 0
        data["equipment"]["hands"] = item_name
        return migrate_loaded_data(data, ORE_DATA, ITEM_DEFINITIONS)

    def test_matching_gloves_consume_one_action_and_multiply_xp(self):
        data = self._equipped("cooking")
        before = brawling_glove_state_pure(data, "cooking")
        outside, xp, event = apply_brawling_gloves_xp_pure(
            data, "cooking", "cook_shark", 210.0
        )
        self.assertEqual(xp, 315.0)
        self.assertEqual(event["multiplier"], 1.5)
        self.assertEqual(
            brawling_glove_state_pure(outside, "cooking")["remaining_actions"],
            before["remaining_actions"] - 1,
        )

        wilderness = set_brawling_wilderness_target_pure(
            data, "cooking", "cook_shark", True
        )
        _wilderness, xp, event = apply_brawling_gloves_xp_pure(
            wilderness, "cooking", "cook_shark", 210.0
        )
        self.assertEqual(xp, 840.0)
        self.assertEqual(event["multiplier"], 4.0)

    def test_wrong_skill_and_zero_xp_do_not_consume_a_charge(self):
        data = self._equipped("cooking")
        before = brawling_glove_state_pure(data, "cooking")["remaining_actions"]
        wrong, xp, event = apply_brawling_gloves_xp_pure(
            data, "mining", "copper", 17.5
        )
        self.assertEqual(xp, 17.5)
        self.assertFalse(event["applied"])
        zero, xp, event = apply_brawling_gloves_xp_pure(
            wrong, "cooking", "cook_shark", 0
        )
        self.assertEqual(xp, 0)
        self.assertFalse(event["applied"])
        self.assertEqual(
            brawling_glove_state_pure(zero, "cooking")["remaining_actions"],
            before,
        )

    def test_last_charge_disintegrates_only_the_equipped_copy(self):
        data = self._equipped("cooking")
        item_name = BRAWLING_GLOVE_DATA["cooking"]["item_name"]
        active_id = brawling_glove_state_pure(data, "cooking")["instance_id"]
        data["equipment_instances"][active_id]["condition"] = 1
        updated, xp, event = apply_brawling_gloves_xp_pure(
            data, "cooking", "cook_shark", 210
        )
        self.assertEqual(xp, 315)
        self.assertTrue(event["disintegrated"])
        self.assertNotIn("hands", updated["equipment"])
        self.assertNotIn(active_id, updated["equipment_instances"])
        self.assertEqual(updated["inventory"].get(item_name, 0), 0)

    def test_two_copies_keep_independent_charge_records(self):
        data = self._equipped("cooking")
        item_name = BRAWLING_GLOVE_DATA["cooking"]["item_name"]
        active_id = brawling_glove_state_pure(data, "cooking")["instance_id"]
        data["inventory"][item_name] = 1
        data["equipment_instances"]["equipment-99"] = {
            "family_id": "brawling_cooking",
            "item_name": item_name,
            "condition": 321,
            "location": "bank",
        }
        updated, _xp, _event = apply_brawling_gloves_xp_pure(
            data, "cooking", "cook_shark", 210
        )
        self.assertEqual(updated["equipment_instances"]["equipment-99"]["condition"], 321)
        self.assertEqual(
            updated["equipment_instances"][active_id]["condition"],
            BRAWLING_GLOVE_DATA["cooking"]["max_actions"] - 1,
        )

    def test_wilderness_risk_uses_carried_food_and_grave_substrate(self):
        data = set_brawling_wilderness_target_pure(
            self._equipped("mining"), "mining", "runite_ore", True
        )
        data["combat_lifepoints"] = 1
        data["carried_inventory"]["runite_ore"] = {"Lobster": 1}
        updated, result = apply_brawling_wilderness_risk_pure(
            data, "mining", "runite_ore", 0.0, 0.999
        )
        self.assertTrue(result["triggered"])
        self.assertTrue(result["died"])
        self.assertEqual(updated["combat_grave"]["source"], "brawling_wilderness_pker")

    def test_storage_migration_sanitizes_policy(self):
        data = _player()
        data["config_version"] = CURRENT_CONFIG_VERSION - 1
        data["brawling_wilderness_targets"] = {
            "cooking": {"cook_shark": True, "bad": "yes"},
            "summoning": {"bogus": True},
        }
        migrated = migrate_loaded_data(data, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(
            migrated["brawling_wilderness_targets"],
            {"cooking": {"cook_shark": True}},
        )
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)


class ChaosElementalTests(unittest.TestCase):
    def test_period_identity_and_supported_drop_probability(self):
        enemy = COMBAT_ENEMY_DATA["chaos_elemental"]
        self.assertEqual(enemy["level"], 305)
        self.assertEqual(enemy["stats"]["hitpoints"], 2500)
        self.assertEqual(enemy["max_hit"], 295)
        table = enemy["drops"]["tables"][0]
        self.assertEqual(table["total"], 1_300_000)
        self.assertEqual(sum(row["slots"] for row in table["slots"]), 1_300_000)
        self.assertEqual(
            _combat_roll_drops(enemy, lambda: 0.0),
            {"Brawling gloves (wc)": 1},
        )

    def test_weighted_attack_table_reaches_every_outcome(self):
        enemy = COMBAT_ENEMY_DATA["chaos_elemental"]
        self.assertEqual(_combat_select_enemy_attack_pure(enemy, lambda: 0.00)["kind"], "teleport")
        self.assertEqual(_combat_select_enemy_attack_pure(enemy, lambda: 0.12)["kind"], "unequip")
        self.assertEqual(_combat_select_enemy_attack_pure(enemy, lambda: 0.20)["style"], "magic")
        self.assertEqual(_combat_select_enemy_attack_pure(enemy, lambda: 0.50)["style"], "ranged")
        self.assertEqual(_combat_select_enemy_attack_pure(enemy, lambda: 0.90)["style"], "melee")

    def test_generic_attack_selector_preserves_dynamic_enemy_style(self):
        self.assertEqual(
            _combat_select_enemy_attack_pure(
                {"attack_style_by_player_class": {"melee": "magic"}},
                lambda: 0.0,
            ),
            {"kind": "attack"},
        )

    def test_teleport_special_interrupts_burst_and_delays_next_attack(self):
        data = _player()
        data["current_combat_target"] = "chaos_elemental"
        rolls = iter((0.0, 0.0, 0.0, 0.0, 0.0, 1.0))
        updated, ok, result = apply_combat_burst_pure(
            data,
            enemy_data=COMBAT_ENEMY_DATA,
            equipment_data=EQUIPMENT_DATA,
            ticks=12,
            rng=lambda: next(rolls),
            live_cadence=True,
        )
        self.assertTrue(ok)
        self.assertEqual(result["enemy_specials"], ({"kind": "teleport", "delay_ticks": 5},))
        self.assertEqual(result["ticks_elapsed"], 6)
        self.assertEqual(updated["combat_encounter"]["player_attack_ticks_remaining"], 7)

    def test_unequip_special_moves_weapon_to_carried_pack_and_preserves_encounter(self):
        data = _player()
        data["current_combat_target"] = "chaos_elemental"
        data["equipment"]["weapon"] = "Bronze sword"
        updated, ok, result = apply_combat_burst_pure(
            data,
            enemy_data=COMBAT_ENEMY_DATA,
            equipment_data=EQUIPMENT_DATA,
            ticks=6,
            rng=lambda: 0.12,
            live_cadence=True,
        )
        self.assertTrue(ok)
        self.assertEqual(result["enemy_specials"][0]["kind"], "unequip")
        self.assertEqual(result["enemy_specials"][0]["item"], "Bronze sword")
        self.assertNotIn("weapon", updated["equipment"])
        self.assertEqual(updated["inventory"]["Bronze sword"], 1)
        self.assertEqual(
            updated["carried_inventory"]["chaos_elemental"]["Bronze sword"],
            1,
        )
        self.assertEqual(updated["combat_encounter"]["target_id"], "chaos_elemental")


if __name__ == "__main__":
    unittest.main()
