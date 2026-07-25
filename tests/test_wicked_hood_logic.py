import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.logic.inventory_pure import sanitize_bank_run_state
from ankiscape.logic_pure.logic_pure import apply_runecrafting_action_pure
from ankiscape.core.constants import RUNECRAFTING_DATA, RUNECRAFTING_POUCH_DATA
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.logic.wicked_hood_logic import (
    advance_wicked_hood_review_day_pure,
    apply_wicked_hood_command_pure,
    bank_run_phase_label_pure,
    consume_wicked_hood_route_teleport_pure,
    runecrafting_route_phases_pure,
    sanitize_wicked_hood_state_pure,
    wicked_hood_caps_pure,
    wicked_hood_skip_active_outbound_pure,
)


def _player():
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data["quests"]["rune_mysteries"] = {
        "started": True,
        "progress": 6,
        "completed": True,
    }
    data["claims"]["wicked_hood"] = {"claimed": True}
    data["equipment"] = {"head": "Wicked hood"}
    data["current_runecrafting"] = "craft_air_runes"
    return data


class TestWickedHoodLogic(unittest.TestCase):
    def test_route_partition_preserves_baseline_and_skips_only_outbound(self):
        full = runecrafting_route_phases_pure(20)
        teleported = runecrafting_route_phases_pure(20, skip_outbound=True)

        self.assertEqual(sum(phase["reviews"] for phase in full), 20)
        self.assertEqual(
            [(phase["id"], phase["reviews"]) for phase in full],
            [("return", 9), ("bank", 1), ("outbound", 10)],
        )
        self.assertEqual(
            [(phase["id"], phase["reviews"]) for phase in teleported],
            [("return", 9), ("bank", 1)],
        )

    def test_active_route_teleport_removes_only_unspent_outbound_tail(self):
        phases = list(runecrafting_route_phases_pure(20))
        state, removed = wicked_hood_skip_active_outbound_pure(
            {
                "target_id": "craft_air_runes",
                "reviews_total": 20,
                "reviews_remaining": 15,
                "route_phases": phases,
            }
        )
        self.assertTrue(removed)
        self.assertEqual(state["reviews_remaining"], 5)
        self.assertEqual(state["reviews_total"], 10)
        self.assertEqual(bank_run_phase_label_pure(state), "Returning to the bank")
        completed, removed = wicked_hood_skip_active_outbound_pure(
            {
                "reviews_total": 20,
                "reviews_remaining": 5,
                "route_phases": phases,
            }
        )
        self.assertTrue(removed)
        self.assertEqual(completed, {})

    def test_route_metadata_survives_bank_run_sanitization(self):
        phases = list(runecrafting_route_phases_pure(20, skip_outbound=True))

        state = sanitize_bank_run_state(
            {
                "target_id": "craft_air_runes",
                "reviews_total": 10,
                "reviews_remaining": 7,
                "route_label": "Air altar route",
                "route_phases": phases,
                "outbound_teleport_used": True,
            },
            20,
        )

        self.assertEqual(state["route_phases"], phases)
        self.assertTrue(state["outbound_teleport_used"])
        self.assertEqual(bank_run_phase_label_pure(state), "Returning to the bank")

    def test_caps_and_review_day_reset_do_not_stack_unused_allowances(self):
        state = sanitize_wicked_hood_state_pure(
            {
                "elemental_fed": True,
                "outfit_upgrades": ["Wicked cape", "Wicked robe top", "Wicked legs"],
                "allowance_day": 0,
                "essence_remaining": 17,
                "rune_withdrawals_remaining": 2,
                "teleports_remaining": 1,
            },
            0,
        )
        self.assertEqual(wicked_hood_caps_pure(state), {"essence": 175, "runes": 5, "teleports": 3})

        player = _player()
        player["wicked_hood"] = state
        player["shop_market_clock"]["answered_cards"] = 240
        updated = advance_wicked_hood_review_day_pure(player)

        self.assertEqual(updated["wicked_hood"]["allowance_day"], 1)
        self.assertEqual(updated["wicked_hood"]["essence_remaining"], 175)
        self.assertEqual(updated["wicked_hood"]["rune_withdrawals_remaining"], 5)
        self.assertEqual(updated["wicked_hood"]["teleports_remaining"], 3)

    def test_essence_withdrawal_fills_only_free_carried_slots_and_preserves_remainder(self):
        player = _player()
        player["inventory"]["Shark"] = 27
        player["carried_inventory"] = {"craft_air_runes": {"Shark": 27}}

        updated, ok, info = apply_wicked_hood_command_pure(player, "essence")

        self.assertTrue(ok)
        self.assertEqual(info["quantity"], 1)
        self.assertEqual(updated["inventory"]["Rune essence"], 1)
        self.assertEqual(updated["carried_inventory"]["craft_air_runes"]["Rune essence"], 1)
        self.assertEqual(updated["wicked_hood"]["essence_remaining"], 99)

        unchanged, ok, info = apply_wicked_hood_command_pure(updated, "essence")
        self.assertFalse(ok)
        self.assertIn("No carried-pack space", info["reason"])
        self.assertEqual(unchanged["wicked_hood"]["essence_remaining"], 99)

    def test_rune_withdrawals_use_period_quantities_and_elemental_second_use(self):
        player = _player()
        player["wicked_hood"] = sanitize_wicked_hood_state_pure(
            {"fed_altars": ["air", "cosmic"], "elemental_fed": True},
            0,
            initialize_allowances=True,
        )

        updated, ok, info = apply_wicked_hood_command_pure(
            player, "runes", {"altar_id": "air"}
        )
        self.assertTrue(ok)
        self.assertEqual(info["quantity"], 100)
        self.assertEqual(updated["inventory"]["Air rune"], 100)

        updated, ok, info = apply_wicked_hood_command_pure(
            updated, "runes", {"altar_id": "cosmic"}
        )
        self.assertTrue(ok)
        self.assertEqual(info["quantity"], 5)
        self.assertEqual(updated["inventory"]["Cosmic rune"], 5)
        self.assertEqual(updated["wicked_hood"]["rune_withdrawals_remaining"], 0)

        unchanged, ok, info = apply_wicked_hood_command_pure(
            updated, "runes", {"altar_id": "air"}
        )
        self.assertFalse(ok)
        self.assertIn("No rune withdrawals remain", info["reason"])
        self.assertEqual(unchanged["wicked_hood"]["rune_withdrawals_remaining"], 0)

    def test_omni_feed_unlocks_all_altars_and_pure_essence(self):
        player = _player()
        player["inventory"]["Omni-talisman"] = 1

        fed, _xp, ok, _message = apply_runecrafting_action_pure(
            player,
            "feed_omni_talisman_to_hood",
            RUNECRAFTING_DATA,
            RUNECRAFTING_POUCH_DATA,
        )
        self.assertTrue(ok)
        self.assertTrue(fed["wicked_hood"]["omni_fed"])

        withdrawn, ok, info = apply_wicked_hood_command_pure(fed, "essence")
        self.assertTrue(ok)
        self.assertEqual(info["item"], "Pure essence")
        self.assertEqual(withdrawn["inventory"]["Pure essence"], 28)
        self.assertEqual(withdrawn["wicked_hood"]["essence_remaining"], 72)

    def test_teleport_is_level_gated_and_consumed_only_by_matching_route(self):
        player = _player()
        player["wicked_hood"] = sanitize_wicked_hood_state_pure(
            {"fed_altars": ["air", "nature"]},
            0,
            initialize_allowances=True,
        )
        player["runecrafting_level"] = 1

        unchanged, ok, info = apply_wicked_hood_command_pure(
            player,
            "teleport",
            {"altar_id": "nature", "required_level": 44},
        )
        self.assertFalse(ok)
        self.assertIn("level 44", info["reason"])
        self.assertEqual(unchanged["wicked_hood"]["teleports_remaining"], 2)

        teleported, ok, _info = apply_wicked_hood_command_pure(
            player,
            "teleport",
            {"altar_id": "air", "required_level": 1},
        )
        self.assertTrue(ok)
        self.assertEqual(teleported["wicked_hood"]["teleports_remaining"], 1)

        unchanged, ok, info = apply_wicked_hood_command_pure(
            teleported,
            "teleport",
            {"altar_id": "nature"},
        )
        self.assertFalse(ok)
        self.assertIn("already queued", info["reason"])
        self.assertEqual(unchanged["wicked_hood"]["teleports_remaining"], 1)
        self.assertEqual(
            unchanged["wicked_hood"]["pending_altar_teleport"], "air"
        )

        other, consumed = consume_wicked_hood_route_teleport_pure(teleported, "water")
        self.assertFalse(consumed)
        self.assertEqual(other["wicked_hood"]["pending_altar_teleport"], "air")
        arrived, consumed = consume_wicked_hood_route_teleport_pure(other, "air")
        self.assertTrue(consumed)
        self.assertEqual(arrived["wicked_hood"]["pending_altar_teleport"], "")

    def test_teleport_does_not_spend_a_charge_on_a_quest_lock_or_used_route(self):
        player = _player()
        player["runecrafting_level"] = 99
        player["wicked_hood"] = sanitize_wicked_hood_state_pure(
            {"fed_altars": ["air", "death"]},
            0,
            initialize_allowances=True,
        )

        locked, ok, info = apply_wicked_hood_command_pure(
            player,
            "teleport",
            {"altar_id": "death", "locked_reason": "Mourning's End Part II"},
        )
        self.assertFalse(ok)
        self.assertEqual(info["reason"], "Mourning's End Part II")
        self.assertEqual(locked["wicked_hood"]["teleports_remaining"], 2)

        player["skilling_bank_run"] = {
            "target_id": "craft_air_runes",
            "reviews_total": 10,
            "reviews_remaining": 5,
            "outbound_teleport_used": True,
        }
        unchanged, ok, info = apply_wicked_hood_command_pure(
            player, "teleport", {"altar_id": "air"}
        )
        self.assertFalse(ok)
        self.assertIn("already been teleported", info["reason"])
        self.assertEqual(unchanged["wicked_hood"]["teleports_remaining"], 2)

    def test_reclaim_preserves_progress_and_enforces_one_hood(self):
        player = _player()
        player["wicked_hood"] = sanitize_wicked_hood_state_pure(
            {"fed_altars": ["air"], "essence_remaining": 31}, 0
        )
        player["equipment"] = {}
        player["inventory"].pop("Wicked hood", None)

        reclaimed, ok, _info = apply_wicked_hood_command_pure(player, "reclaim")
        self.assertTrue(ok)
        self.assertEqual(reclaimed["inventory"]["Wicked hood"], 1)
        self.assertEqual(reclaimed["wicked_hood"]["fed_altars"], ["air"])
        self.assertEqual(reclaimed["wicked_hood"]["essence_remaining"], 31)

        unchanged, ok, info = apply_wicked_hood_command_pure(reclaimed, "reclaim")
        self.assertFalse(ok)
        self.assertIn("already own", info["reason"])
        self.assertEqual(unchanged["inventory"]["Wicked hood"], 1)

    def test_legacy_feed_state_migrates_to_full_current_allowances(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 70,
                "wicked_hood": {"fed_altars": ["air", "air", "unknown"]},
                "shop_market_clock": {"answered_cards": 480},
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["wicked_hood"]["fed_altars"], ["air"])
        self.assertEqual(migrated["wicked_hood"]["allowance_day"], 2)
        self.assertEqual(migrated["wicked_hood"]["essence_remaining"], 100)


if __name__ == "__main__":
    unittest.main()
