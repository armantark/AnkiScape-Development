import unittest

from managing_miscellania_logic import (
    advance_managing_miscellania_world_clock_pure,
    apply_managing_miscellania_command_pure,
    apply_managing_miscellania_review_pure,
    default_managing_miscellania_state_pure,
    managing_miscellania_view_pure,
    sanitize_managing_miscellania_player_state_pure,
)
from constants import ORE_DATA
from storage_pure import migrate_loaded_data


def _player(*, royal: bool = False, answered_cards: int = 0):
    quests = {
        "throne_of_miscellania": {"completed": True},
        "royal_trouble": {"completed": royal},
    }
    data = {
        "quests": quests,
        "shop_market_clock": {"answered_cards": answered_cards},
        "inventory": {"Coins": 8_000_000},
        "woodcutting_level": 45,
        "woodcutting_exp": 0.0,
    }
    data.update(default_managing_miscellania_state_pure(answered_cards))
    return data


class ManagingMiscellaniaLogicTest(unittest.TestCase):
    def test_new_state_starts_at_current_review_day_without_retroactive_production(self):
        data = _player(answered_cards=4_800)
        updated, events = advance_managing_miscellania_world_clock_pure(data)

        self.assertEqual(events, ())
        self.assertEqual(updated["managing_miscellania"]["last_world_day"], 20)
        self.assertEqual(updated["managing_miscellania"]["production_credit"], 0)

    def test_daily_boundary_decays_approval_pays_salary_and_builds_credit(self):
        data = _player(answered_cards=239)
        data["managing_miscellania"]["coffer"] = 500_000
        data["shop_market_clock"]["answered_cards"] = 240

        updated, events = advance_managing_miscellania_world_clock_pure(data)

        state = updated["managing_miscellania"]
        self.assertEqual(len(events), 1)
        self.assertEqual(state["approval_basis_points"], 9_750)
        self.assertEqual(state["coffer"], 450_000)
        self.assertEqual(state["production_credit"], 975_000)
        self.assertEqual(state["days_funded"], 1)

    def test_royal_trouble_expands_limits_and_reduces_decay(self):
        data = _player(royal=True, answered_cards=239)
        data["managing_miscellania"]["coffer"] = 750_000
        data["shop_market_clock"]["answered_cards"] = 240

        updated, _events = advance_managing_miscellania_world_clock_pure(data)
        view = managing_miscellania_view_pure(updated)

        self.assertEqual(updated["managing_miscellania"]["approval_basis_points"], 9_900)
        self.assertEqual(updated["managing_miscellania"]["coffer"], 675_000)
        self.assertEqual(updated["managing_miscellania"]["production_credit"], 990_000)
        self.assertEqual((view["subjects"], view["coffer_cap"]), (15, 7_500_000))

    def test_current_allocation_applies_to_entire_unclaimed_credit(self):
        data = _player()
        data["managing_miscellania"]["production_credit"] = 2_000_000
        data, ok, _ = apply_managing_miscellania_command_pure(
            data,
            "set_workers",
            {"family_id": "wood", "workers": 10},
        )
        self.assertTrue(ok)

        data, ok, info = apply_managing_miscellania_command_pure(data, "collect")

        self.assertTrue(ok, info)
        self.assertEqual(data["inventory"]["Maple logs"], 1_784)
        self.assertEqual(data["inventory"]["Bird's nest (seeds)"], 17)
        self.assertEqual(data["managing_miscellania"]["production_credit"], 0)

    def test_fractional_credit_does_not_enable_empty_collection(self):
        data = _player()
        data["managing_miscellania"]["production_credit"] = 20_000
        data["managing_miscellania"]["allocations"]["hardwood"] = 1

        view = managing_miscellania_view_pure(data)
        self.assertEqual(view["preview"], {})
        self.assertFalse(view["can_collect"])

        unchanged, ok, info = apply_managing_miscellania_command_pure(
            data, "collect"
        )
        self.assertFalse(ok)
        self.assertEqual(unchanged, data)
        self.assertIn("whole resources", info["reason"])

    def test_worker_total_and_hardwood_variant_are_validated(self):
        data = _player()
        data, ok, _ = apply_managing_miscellania_command_pure(
            data, "set_workers", {"family_id": "mining", "workers": 10}
        )
        self.assertTrue(ok)
        unchanged, ok, info = apply_managing_miscellania_command_pure(
            data, "set_workers", {"family_id": "wood", "workers": 1}
        )
        self.assertFalse(ok)
        self.assertIn("unassigned", info["reason"])
        self.assertEqual(unchanged, data)

        data, ok, _ = apply_managing_miscellania_command_pure(
            data, "set_variant", {"family_id": "hardwood", "variant_id": "mixed"}
        )
        self.assertTrue(ok)
        self.assertEqual(data["managing_miscellania"]["variants"]["hardwood"], "mixed")

    def test_corrupt_allocations_and_coffer_sanitize_to_live_quest_limits(self):
        data = _player()
        data["managing_miscellania"]["allocations"] = {
            "mining": 10,
            "wood": 10,
            "hardwood": 10,
        }
        data["managing_miscellania"]["coffer"] = 7_500_000

        state = sanitize_managing_miscellania_player_state_pure(data)[
            "managing_miscellania"
        ]

        self.assertEqual(sum(state["allocations"].values()), 10)
        self.assertEqual(state["coffer"], 5_000_000)

    def test_funding_presets_and_exact_withdrawal_preserve_remainder(self):
        data = _player()
        data, ok, _ = apply_managing_miscellania_command_pure(
            data, "fund_days", {"days": 7}
        )
        self.assertTrue(ok)
        self.assertEqual(data["managing_miscellania"]["coffer"], 800_000)
        self.assertEqual(data["inventory"]["Coins"], 7_200_000)

        data, ok, _ = apply_managing_miscellania_command_pure(
            data, "withdraw", {"quantity": 125_000}
        )
        self.assertTrue(ok)
        self.assertEqual(data["managing_miscellania"]["coffer"], 675_000)
        self.assertEqual(data["inventory"]["Coins"], 7_325_000)

    def test_approval_review_requires_quest_level_and_missing_approval(self):
        data = _player()
        data["managing_miscellania"]["approval_basis_points"] = 9_900

        updated, result = apply_managing_miscellania_review_pure(data)

        self.assertTrue(result["allowed"])
        self.assertEqual(result["xp"], 100.0)
        self.assertEqual(updated["managing_miscellania"]["approval_basis_points"], 10_000)
        self.assertEqual(data["managing_miscellania"]["approval_basis_points"], 9_900)

        updated, result = apply_managing_miscellania_review_pure(updated)
        self.assertFalse(result["allowed"])
        self.assertIn("100%", result["reason"])

    def test_approval_chore_selection_is_persistent_and_level_gated(self):
        data = _player()
        data, ok, info = apply_managing_miscellania_command_pure(
            data, "set_approval_chore", {"chore_id": "chop_maple"}
        )
        self.assertTrue(ok, info)
        self.assertEqual(
            data["managing_miscellania"]["approval_chore"], "chop_maple"
        )

        data["woodcutting_level"] = 44
        unchanged, ok, info = apply_managing_miscellania_command_pure(
            data, "set_approval_chore", {"chore_id": "chop_maple"}
        )
        self.assertFalse(ok)
        self.assertEqual(unchanged, data)
        self.assertIn("eligible", info["reason"])

    def test_locked_kingdom_cannot_be_managed(self):
        data = _player()
        data["quests"]["throne_of_miscellania"]["completed"] = False

        updated, ok, info = apply_managing_miscellania_command_pure(
            data, "deposit", {"quantity": 1}
        )

        self.assertFalse(ok)
        self.assertEqual(updated, data)
        self.assertIn("Throne of Miscellania", info["reason"])

    def test_v67_migration_anchors_new_kingdom_to_current_review_day(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 66,
                "shop_market_clock": {"answered_cards": 4_800},
            },
            ORE_DATA,
        )

        self.assertEqual(migrated["config_version"], 67)
        self.assertEqual(migrated["managing_miscellania"]["last_world_day"], 20)
        self.assertEqual(migrated["managing_miscellania"]["production_credit"], 0)


if __name__ == "__main__":
    unittest.main()
