import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic.cadence_coverage import cadence_coverage_rows_pure
from ankiscape.core.constants import UTILITY_ACTIVITY_DATA
from ankiscape.core.constants import EQUIPMENT_DATA
from ankiscape.data.penguin_hide_and_seek_data import (
    PENGUIN_ONE_POINT_SPAWNS,
    PENGUIN_TWO_POINT_SPAWNS,
    PENGUIN_WEEK_REVIEWS,
)
from ankiscape.logic_pure.logic_pure_equipment import equip_item_pure
from ankiscape.logic.penguin_hide_and_seek_logic import (
    apply_penguin_command_pure,
    apply_penguin_review_pure,
    default_penguin_state_pure,
    penguin_roster_pure,
    penguin_view_pure,
    sanitize_penguin_state_pure,
)
from ankiscape.runtime.runtime_actions import RuntimeActionContext, handle_utility_answer
from ankiscape.core.storage_pure import CURRENT_CONFIG_VERSION, default_player_data, migrate_loaded_data


def _player(*, answered_cards=0):
    return {
        "shop_market_clock": {"answered_cards": answered_cards},
        "inventory": {},
        "equipment": {},
        "quests": {},
        "penguin_hide_and_seek": default_penguin_state_pure(),
        "current_utility": "penguin_hide_and_seek",
        "mining_level": 10,
        "mining_exp": 0.0,
        "completed_achievements": [],
    }


def _context(player_data, calls):
    return RuntimeActionContext(
        player_data=player_data,
        random_random=lambda: 0.0,
        show_error_message=lambda title, message: calls["errors"].append((title, message)),
        deactivate_current_skill=lambda: calls.__setitem__("deactivated", True),
        award_skill_exp=lambda _key, amount: amount,
        award_hidden_skill_exp=lambda *_args: None,
        level_up_check=lambda *_args: None,
        check_achievements=lambda _data: calls.__setitem__("achievements", True),
        save_player_data=lambda: calls.__setitem__("saves", calls["saves"] + 1),
        refresh_skill_availability=lambda: calls.__setitem__("refresh", True),
        show_exp=lambda amount: calls["xp"].append(amount),
        show_activity_gain=lambda message: calls["activity"].append(message),
        implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda _before: None,
    )


class PenguinHideAndSeekPureTest(unittest.TestCase):
    def test_cutoff_spawn_catalog_is_complete_and_every_row_rotates_live(self):
        self.assertEqual(
            tuple((row.location, row.disguise) for row in PENGUIN_ONE_POINT_SPAWNS),
            (
                ("Al Kharid", "Cactus"),
                ("Barbarian Outpost", "Bush"),
                ("Brimhaven", "Bush"),
                ("Burthorpe", "Rock"),
                ("Castle Wars", "Bush"),
                ("Central Karamja", "Bush"),
                ("Digsite", "Rock"),
                ("Draynor Manor", "Crate"),
                ("Dorgesh-Kaan", "Barrel"),
                ("Eagles' Peak", "Bush"),
                ("East Karamja", "Bush"),
                ("Entrana", "Barrel"),
                ("Feldip Hills", "Rock"),
                ("Gnome Maze", "Bush"),
                ("Gnome Stronghold", "Bush"),
                ("Goblin Village", "Bush"),
                ("Ice Mountain", "Rock"),
                ("Lighthouse", "Rock"),
                ("Lumber Yard", "Crate"),
                ("Lumbridge Swamp", "Toadstool"),
                ("Mage Training Arena", "Bush"),
                ("McGrubor's Wood", "Bush"),
                ("Mining Camp", "Cactus"),
                ("Mudskipper Point", "Bush"),
                ("Musa Point", "Crate"),
                ("North Ardougne", "Bush"),
                ("Observatory", "Crate"),
                ("Pollnivneach", "Cactus"),
                ("Port Khazard", "Barrel"),
                ("Rellekka", "Rock"),
                ("White Wolf Mountain", "Rock"),
                ("Witchaven", "Rock"),
                ("Wizards' Tower", "Bush"),
                ("Zanaris", "Toadstool"),
            ),
        )
        self.assertEqual(
            tuple((row.location, row.disguise) for row in PENGUIN_TWO_POINT_SPAWNS),
            (
                ("Ape Atoll", "Barrel"),
                ("Ape Atoll", "Bush"),
                ("Arandar", "Rock"),
                ("Castle Wars", "Rock"),
                ("South KBD", "Rock"),
                ("Dragontooth Isle", "Crate"),
                ("Elf Camp", "Toadstool"),
                ("Feldip Hills", "Bush"),
                ("Haunted Woods", "Bush"),
                ("Haunted Woods", "Crate"),
                ("Jatizso", "Bush"),
                ("Jatizso", "Rock"),
                ("Jiggig", "Rock"),
                ("Keldagrim", "Rock"),
                ("North KBD", "Rock"),
                ("Lava Maze", "Rock"),
                ("Lletya", "Toadstool"),
                ("Lunar Isle", "Rock"),
                ("Miscellania", "Bush"),
                ("Mort Myre", "Bush"),
                ("Mort Myre", "Rock"),
                ("Mort Myre", "Toadstool"),
                ("Mos Le'Harmless", "Barrel"),
                ("Nardah", "Cactus"),
                ("Neitiznot", "Bush"),
                ("Neitiznot", "Rock"),
                ("Piscatoris", "Crate"),
                ("Port Phasmatys", "Barrel"),
                ("Scorpion Pit", "Rock"),
                ("Inner Sophanem", "Cactus"),
                ("Outer Sophanem", "Cactus"),
                ("Tyras Camp", "Toadstool"),
                ("Wilderness Volcano", "Rock"),
            ),
        )

        player = _player()
        player["quests"] = {
            "cold_war": {"completed": True},
            "some_like_it_cold": {"completed": True},
            "desert_treasure": {"started": True},
        }
        player["inventory"]["Ring of visibility"] = 1
        player["carried_inventory"] = {
            "penguin_hide_and_seek": {"Ring of visibility": 1}
        }
        seen_ordinary = set()
        seen_invisible_locations = set()
        for week in range(len(PENGUIN_ONE_POINT_SPAWNS)):
            player["shop_market_clock"]["answered_cards"] = week * PENGUIN_WEEK_REVIEWS
            roster = penguin_roster_pure(player)
            seen_ordinary.update(row["id"] for row in roster if row["kind"] == "ordinary")
            seen_invisible_locations.update(
                row["location"] for row in roster if row["kind"] == "invisible"
            )
        self.assertEqual(
            seen_ordinary,
            {row.id for row in (*PENGUIN_ONE_POINT_SPAWNS, *PENGUIN_TWO_POINT_SPAWNS)},
        )
        self.assertEqual(
            seen_invisible_locations,
            {row.location for row in PENGUIN_ONE_POINT_SPAWNS},
        )

    def test_weekly_roster_has_five_of_each_tier_and_rotates_without_wall_clock(self):
        player = _player()
        first = penguin_roster_pure(player)
        self.assertEqual(len(first), 10)
        self.assertEqual([row["points"] for row in first], [1] * 10)

        player["shop_market_clock"]["answered_cards"] = 1_680
        second = penguin_roster_pure(player)
        self.assertEqual(len(second), 10)
        self.assertNotEqual([row["id"] for row in first], [row["id"] for row in second])
        self.assertEqual(sum(row["points"] for row in second), 10)

    def test_quest_upgrades_require_the_visibility_ring_carried_or_equipped(self):
        player = _player()
        player["quests"] = {
            "cold_war": {"completed": True},
            "hunt_for_red_raktuber": {"completed": True},
            "some_like_it_cold": {"completed": True},
            "desert_treasure": {"started": True},
        }
        player["inventory"]["Ring of visibility"] = 1

        bank_only = penguin_roster_pure(player)
        self.assertEqual(len(bank_only), 11)
        self.assertFalse(any(row["kind"] == "invisible" for row in bank_only))

        player["carried_inventory"] = {
            "another_target": {"Ring of visibility": 1}
        }
        wrong_pack = penguin_roster_pure(player)
        self.assertFalse(any(row["kind"] == "invisible" for row in wrong_pack))

        player["carried_inventory"] = {
            "penguin_hide_and_seek": {"Ring of visibility": 1}
        }
        carried = penguin_roster_pure(player)
        self.assertEqual(len(carried), 12)
        self.assertEqual(sum(row["points"] for row in carried), 19)
        self.assertEqual(sum(row["points"] == 2 for row in carried), 5)
        self.assertTrue(any(row["kind"] == "polar_bear" for row in carried))
        self.assertTrue(any(row["kind"] == "invisible" for row in carried))

        player["inventory"].pop("Ring of visibility")
        stale_pack = penguin_roster_pure(player)
        self.assertFalse(any(row["kind"] == "invisible" for row in stale_pack))

        # Drive the equipped branch through the REAL equip path rather than
        # assigning the slot by hand. Hand-writing it is what let the invisible
        # penguin ship as an inert row: the ring had no equipment row at all, so
        # no player could ever reach the state this test was asserting.
        player["carried_inventory"] = {}
        player["inventory"]["Ring of visibility"] = 1
        inventory, equipment, equipped_ok = equip_item_pure(
            "Ring of visibility",
            player["inventory"],
            player.get("equipment", {}) or {},
            EQUIPMENT_DATA,
        )
        self.assertTrue(
            equipped_ok,
            "the ring must be equippable, or the gate's equipped branch is dead",
        )
        self.assertEqual(equipment.get("ring"), "Ring of visibility")
        player["inventory"], player["equipment"] = inventory, equipment
        equipped = penguin_roster_pure(player)
        self.assertTrue(any(row["kind"] == "invisible" for row in equipped))

    def test_spy_is_selected_then_resolves_once_and_week_reset_clears_progress(self):
        player = _player()
        spawn_id = penguin_roster_pure(player)[0]["id"]
        selected, ok, _ = apply_penguin_command_pure(
            player, "select_spy", {"spawn_id": spawn_id}
        )
        self.assertTrue(ok)
        spotted, ok, result = apply_penguin_review_pure(selected)
        self.assertTrue(ok)
        self.assertEqual(result["points_awarded"], 1)
        self.assertEqual(spotted["penguin_hide_and_seek"]["points"], 1)
        self.assertIn(spawn_id, spotted["penguin_hide_and_seek"]["spotted_ids"])
        self.assertFalse(penguin_view_pure(spotted)["can_review"])

        repeated, ok, _ = apply_penguin_command_pure(
            spotted, "select_spy", {"spawn_id": spawn_id}
        )
        self.assertFalse(ok)
        self.assertEqual(repeated, spotted)

        spotted["shop_market_clock"]["answered_cards"] = 1_680
        reset_view = penguin_view_pure(spotted)
        self.assertEqual(reset_view["spotted_count"], 0)
        self.assertEqual(reset_view["points"], 1)

    def test_point_cap_loses_overflow_but_still_marks_the_spy(self):
        player = _player()
        player["quests"]["cold_war"] = {"completed": True}
        player["penguin_hide_and_seek"]["points"] = 49
        two_point = next(row for row in penguin_roster_pure(player) if row["points"] == 2)
        player, ok, _ = apply_penguin_command_pure(
            player, "select_spy", {"spawn_id": two_point["id"]}
        )
        self.assertTrue(ok)
        player, ok, result = apply_penguin_review_pure(player)
        self.assertTrue(ok)
        self.assertEqual(result["points_awarded"], 1)
        self.assertEqual(result["points_lost"], 1)
        self.assertEqual(player["penguin_hide_and_seek"]["points"], 50)

    def test_redemptions_spend_all_points_and_preserve_current_level_formula(self):
        player = _player()
        player["penguin_hide_and_seek"]["points"] = 3
        xp_player, ok, info = apply_penguin_command_pure(
            player, "redeem_xp", {"skill_id": "mining"}
        )
        self.assertTrue(ok)
        self.assertEqual(info["xp"], 750.0)
        self.assertEqual(xp_player["mining_exp"], 750.0)
        self.assertEqual(xp_player["penguin_hide_and_seek"]["points"], 0)

        player["penguin_hide_and_seek"]["points"] = 2
        coin_player, ok, info = apply_penguin_command_pure(player, "redeem_coins")
        self.assertTrue(ok)
        self.assertEqual(info["coins"], 13_000)
        self.assertEqual(coin_player["inventory"]["Coins"], 13_000)
        self.assertEqual(coin_player["penguin_hide_and_seek"]["points"], 0)

    def test_sanitizer_registry_storage_asset_and_cadence_close_the_surface(self):
        state = sanitize_penguin_state_pure(
            {"points": 500, "week_index": -10, "spotted_ids": ["bad", "polar_bear"]}
        )
        self.assertEqual(state["points"], 50)
        self.assertEqual(state["week_index"], -1)
        self.assertEqual(state["spotted_ids"], ["polar_bear"])
        self.assertEqual(
            UTILITY_ACTIVITY_DATA["penguin_hide_and_seek"]["surface"], "activities"
        )
        self.assertTrue(UTILITY_ACTIVITY_DATA["penguin_hide_and_seek"]["icon_path"])
        defaults = default_player_data({})
        self.assertEqual(defaults["config_version"], CURRENT_CONFIG_VERSION)
        defaults["shop_market_clock"]["answered_cards"] = 1_680
        self.assertEqual(penguin_view_pure(defaults)["week_index"], 1)
        migrated = migrate_loaded_data({"config_version": 55}, {})
        self.assertEqual(migrated["penguin_hide_and_seek"]["points"], 0)
        row = next(
            row for row in cadence_coverage_rows_pure()
            if row["handler_key"] == "utility"
            and row["action_id"] == "penguin_hide_and_seek"
        )
        self.assertEqual(row["mode"], "passthrough")
        self.assertEqual(row["source_status"], "sourced")


class PenguinHideAndSeekRuntimeTest(unittest.TestCase):
    def test_runtime_spies_selected_penguin_records_action_and_saves_once(self):
        player = _player()
        spawn_id = penguin_roster_pure(player)[0]["id"]
        updated, ok, _ = apply_penguin_command_pure(
            player, "select_spy", {"spawn_id": spawn_id}
        )
        self.assertTrue(ok)
        player.clear()
        player.update(updated)
        calls = {"errors": [], "activity": [], "xp": [], "saves": 0}
        self.assertTrue(handle_utility_answer(_context(player, calls)))
        self.assertEqual(player["penguin_hide_and_seek"]["points"], 1)
        self.assertEqual(calls["saves"], 1)
        self.assertIn("Al Kharid", calls["activity"][-1])
        telemetry = player["action_telemetry"]["actions"]
        self.assertEqual(telemetry[f"utility:{spawn_id}"]["successes"], 1)


if __name__ == "__main__":
    unittest.main()
