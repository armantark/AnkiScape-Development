from __future__ import annotations

import unittest
from dataclasses import asdict

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.trouble_brewing_data import (
    TROUBLE_BREWING_EVENT_REVIEWS,
    TROUBLE_BREWING_REWARDS,
    trouble_brewing_equipment_data_as_dict,
)
from ankiscape.data.treasure_trails_data import CLUE_SCROLL_ITEMS
from ankiscape.logic.trouble_brewing_logic import (
    apply_trouble_brewing_command_pure,
    apply_trouble_brewing_review_pure,
    buy_trouble_brewing_reward_pure,
    drink_trouble_brewing_rum_pure,
    enter_trouble_brewing_pure,
    leave_trouble_brewing_pure,
    sanitize_trouble_brewing_state_pure,
    set_trouble_brewing_policy_pure,
    trouble_brewing_view_pure,
)


def _player(**overrides):
    player = {
        "cooking_level": 40,
        "quests": {"cabin_fever": {"completed": True}},
        "activity_session": {"active_id": ""},
        "inventory": {},
    }
    player.update(overrides)
    return player


def _entered(**overrides):
    player, ok, info = enter_trouble_brewing_pure(_player(**overrides))
    assert ok, info
    return player


class TroubleBrewingEntryTests(unittest.TestCase):
    def test_complete_cosmetic_catalog_has_authentic_zero_stat_equipment(self):
        expected = (
            ("Blue naval shirt", 100, 8952),
            ("Blue tricorn hat", 50, 8959),
            ("Blue navy slacks", 100, 8991),
            ("Green naval shirt", 100, 8953),
            ("Green tricorn hat", 50, 8960),
            ("Green navy slacks", 100, 8992),
            ("Red naval shirt", 100, 8954),
            ("Red tricorn hat", 50, 8961),
            ("Red navy slacks", 100, 8993),
            ("Brown naval shirt", 100, 8955),
            ("Brown tricorn hat", 50, 8962),
            ("Brown navy slacks", 100, 8994),
            ("Black naval shirt", 100, 8956),
            ("Black tricorn hat", 50, 8963),
            ("Black navy slacks", 100, 8995),
            ("Purple naval shirt", 100, 8957),
            ("Purple tricorn hat", 50, 8964),
            ("Purple navy slacks", 100, 8996),
            ("Grey naval shirt", 100, 8958),
            ("Grey tricorn hat", 50, 8965),
            ("Grey navy slacks", 100, 8997),
            ("Cutthroat flag", 200, 8966),
            ("Guilded smile flag", 200, 8967),
            ("Bronze fist flag", 300, 8968),
            ("Lucky shot flag", 400, 8969),
            ("Treasure flag", 500, 8970),
            ("Phasmatys flag", 600, 8971),
            ("The stuff", 5, 8988),
            ("Red rum", 2, 8940),
            ("Blue rum", 2, 8941),
            ("Clue scroll (medium)", 5_000, 2801),
        )
        self.assertEqual(
            tuple(
                (
                    reward.display_name,
                    reward.pieces_of_eight,
                    reward.source_item_id,
                )
                for reward in TROUBLE_BREWING_REWARDS
            ),
            expected,
        )
        equipment = trouble_brewing_equipment_data_as_dict()
        self.assertEqual(len(equipment), len(expected) - 4)
        for item in equipment.values():
            self.assertTrue(
                all(value == 0 for value in asdict(item.bonuses).values()),
                item.item_name,
            )
        self.assertEqual(equipment["Blue naval shirt"].slot, "body")
        self.assertEqual(equipment["Blue tricorn hat"].slot, "head")
        self.assertEqual(equipment["Blue navy slacks"].slot, "legs")
        self.assertEqual(equipment["Cutthroat flag"].slot, "weapon")
        self.assertFalse(equipment["Cutthroat flag"].two_handed)
        self.assertTrue(equipment["Phasmatys flag"].two_handed)
        self.assertEqual(equipment["Guilded smile flag"].attack_speed, 2)
        self.assertEqual(equipment["Guilded smile flag"].weapon_type, 14)

    def test_the_stuff_is_a_five_piece_nontradeable_material_reward(self):
        from ankiscape.data.trouble_brewing_data import trouble_brewing_extra_items_as_dict

        bought, ok, info = buy_trouble_brewing_reward_pure(
            _player(trouble_brewing_pieces_of_eight=5), "the_stuff"
        )
        self.assertTrue(ok, info)
        self.assertEqual(bought["trouble_brewing_pieces_of_eight"], 0)
        self.assertEqual(bought["inventory"]["The stuff"], 1)
        item = trouble_brewing_extra_items_as_dict()["The stuff"]
        self.assertEqual(item["category"], "material")
        self.assertFalse(item["stackable"])
        self.assertFalse(item["tradeable"])

    def test_entry_requires_cooking_40_cabin_fever_and_free_activity_slot(self):
        for player, reason in (
            (_player(cooking_level=39), "Cooking"),
            (_player(quests={}), "Cabin Fever"),
            (_player(activity_session={"active_id": "barrows"}), "persistent activity"),
        ):
            with self.subTest(reason=reason):
                _unchanged, ok, info = enter_trouble_brewing_pure(player)
                self.assertFalse(ok)
                self.assertIn(reason, info["reason"])

        entered = _entered()
        self.assertEqual(entered["activity_session"], {"active_id": "trouble_brewing"})
        self.assertEqual(len(entered["trouble_brewing"]["boilers"]), 3)

    def test_policy_is_saved_before_entry_and_cannot_change_mid_game(self):
        player, ok, _info = set_trouble_brewing_policy_pure(
            _player(), {"automation_mode": "advanced", "duty": "sabotage"}
        )
        self.assertTrue(ok)
        entered, ok, _info = enter_trouble_brewing_pure(player)
        self.assertTrue(ok)
        self.assertEqual(entered["trouble_brewing"]["automation_mode"], "advanced")
        self.assertEqual(entered["trouble_brewing"]["duty"], "sabotage")
        _unchanged, ok, info = set_trouble_brewing_policy_pure(
            entered, {"duty": "water"}
        )
        self.assertFalse(ok)
        self.assertIn("current game", info["reason"])

    def test_sanitizer_repairs_malformed_session_without_deleting_other_state(self):
        malformed = _player(
            trouble_brewing={
                "review": "999",
                "stores": {"water": -4},
                "boilers": [99],
                "automation_mode": "unknown",
            },
            activity_session={"active_id": "trouble_brewing"},
            unrelated={"kept": True},
        )
        state = sanitize_trouble_brewing_state_pure(malformed)
        session = state["trouble_brewing"]
        self.assertEqual(session["review"], TROUBLE_BREWING_EVENT_REVIEWS - 1)
        self.assertEqual(session["stores"]["water"], 0)
        self.assertEqual(session["boilers"], [10, 3, 3])
        self.assertEqual(session["automation_mode"], "casual")
        self.assertEqual(malformed["unrelated"], {"kept": True})


class TroubleBrewingRaceTests(unittest.TestCase):
    def test_casual_completes_source_recipe_packs_rum_and_pays_exact_rewards(self):
        player = _entered()
        duties = []
        total_xp = {}
        for _ in range(TROUBLE_BREWING_EVENT_REVIEWS):
            player, result = apply_trouble_brewing_review_pure(
                player,
                productive=True,
                opponent_roll=0.9,
                sabotage_roll=0.9,
            )
            duties.append(result["duty"])
            for skill, amount in result["skill_xp"].items():
                total_xp[skill] = total_xp.get(skill, 0.0) + amount

        self.assertTrue(result["terminal"])
        self.assertEqual(result["player_rum"], 1)
        self.assertEqual(result["opponent_rum"], 1)
        self.assertEqual(result["outcome"], "drew")
        self.assertEqual(result["pieces_of_eight"], 69)
        self.assertEqual(
            total_xp,
            {
                "agility": 30.0,
                "cooking": 810.0,
                "crafting": 100.0,
                "firemaking": 1950.0,
                "woodcutting": 50.0,
            },
        )
        self.assertIn("pack_rum", duties)
        self.assertIn("tend_boilers", duties)
        self.assertEqual(player["trouble_brewing"], {})
        self.assertEqual(player["activity_session"], {"active_id": ""})

    def test_duty_xp_is_immediate_and_survives_leaving_the_match(self):
        player, ok, info = enter_trouble_brewing_pure(
            _player(), {"automation_mode": "advanced", "duty": "coloured_water"}
        )
        self.assertTrue(ok, info)
        player, result = apply_trouble_brewing_review_pure(
            player,
            productive=True,
            opponent_roll=0.9,
            sabotage_roll=0.9,
        )
        self.assertEqual(result["skill_xp"], {"cooking": 120.0})
        player, ok, _info = leave_trouble_brewing_pure(player)
        self.assertTrue(ok)
        self.assertEqual(player["trouble_brewing"], {})

    def test_again_advances_the_race_without_doing_a_player_duty(self):
        player = _entered()
        player, result = apply_trouble_brewing_review_pure(
            player,
            productive=False,
            opponent_roll=0.0,
            sabotage_roll=0.9,
        )
        session = player["trouble_brewing"]
        self.assertEqual(result["duty"], "idle")
        self.assertEqual(session["stores"], {key: 0 for key in session["stores"]})
        self.assertEqual(session["opponent_progress"], 2)
        self.assertEqual(session["review"], 1)

    def test_opponent_sabotage_forces_the_next_productive_review_to_repair(self):
        player = _entered()
        for _ in range(3):
            player, _result = apply_trouble_brewing_review_pure(
                player,
                productive=True,
                opponent_roll=0.9,
                sabotage_roll=0.0,
            )
        self.assertTrue(player["trouble_brewing"]["repair_required"])
        player, result = apply_trouble_brewing_review_pure(
            player,
            productive=True,
            duty="sabotage",
            opponent_roll=0.9,
            sabotage_roll=0.0,
        )
        self.assertEqual(result["duty"], "repair")
        self.assertIn("Repaired", result["status"])
        self.assertFalse(player["trouble_brewing"]["repair_required"])
        self.assertEqual(player["trouble_brewing"]["xp"]["crafting"], 25.0)

    def test_advanced_forced_repair_cannot_be_replaced_or_immediately_retriggered(self):
        player, ok, _info = enter_trouble_brewing_pure(
            _player(), {"automation_mode": "advanced", "duty": "sabotage"}
        )
        self.assertTrue(ok)
        player["trouble_brewing"]["review"] = 3
        player["trouble_brewing"]["repair_required"] = True
        player, result = apply_trouble_brewing_review_pure(
            player,
            productive=True,
            duty="sabotage",
            opponent_roll=0.9,
            sabotage_roll=0.0,
        )
        self.assertEqual(result["duty"], "repair")
        self.assertFalse(player["trouble_brewing"]["repair_required"])
        self.assertEqual(player["trouble_brewing"]["opponent_slowed"], 0)

    def test_conflicting_activity_owner_cannot_be_advanced_or_cleared(self):
        player = _entered()
        player["activity_session"] = {"active_id": "barrows"}
        unchanged, result = apply_trouble_brewing_review_pure(
            player,
            productive=True,
        )
        self.assertIn("No Trouble Brewing", result["reason"])
        self.assertEqual(unchanged["activity_session"], {"active_id": "barrows"})
        self.assertEqual(unchanged["trouble_brewing"]["review"], 0)

        unchanged, ok, info = leave_trouble_brewing_pure(player)
        self.assertFalse(ok)
        self.assertIn("No Trouble Brewing", info["reason"])
        self.assertEqual(unchanged["activity_session"], {"active_id": "barrows"})
        self.assertTrue(unchanged["trouble_brewing"])

    def test_advanced_sabotage_reduces_and_temporarily_stops_opponent_progress(self):
        player, ok, _info = enter_trouble_brewing_pure(
            _player(), {"automation_mode": "advanced", "duty": "sabotage"}
        )
        self.assertTrue(ok)
        player["trouble_brewing"]["opponent_progress"] = 7
        player, result = apply_trouble_brewing_review_pure(
            player,
            productive=True,
            opponent_roll=0.0,
            sabotage_roll=0.9,
        )
        self.assertEqual(result["duty"], "sabotage")
        self.assertEqual(player["trouble_brewing"]["opponent_progress"], 4)
        self.assertEqual(player["trouble_brewing"]["opponent_slowed"], 1)
        self.assertEqual(player["trouble_brewing"]["xp"]["firemaking"], 50.0)

    def test_unpacked_bottle_is_lost_when_the_next_batch_finishes(self):
        player = _entered()
        session = player["trouble_brewing"]
        session["stores"] = {
            "water": 5,
            "coloured_water": 3,
            "sweetgrubs": 1,
            "scrapey_bark": 1,
            "bitternut": 1,
        }
        session["boilers"] = [10, 10, 10]
        session["pending_bottle"] = True
        player, result = apply_trouble_brewing_review_pure(
            player,
            productive=False,
            opponent_roll=0.9,
            sabotage_roll=0.9,
        )
        self.assertTrue(result["brewed"])
        self.assertTrue(player["trouble_brewing"]["pending_bottle"])
        self.assertEqual(player["trouble_brewing"]["spilled_rum"], 1)

    def test_leave_forfeits_match_rewards(self):
        player = _entered(trouble_brewing_pieces_of_eight=7)
        player["trouble_brewing"]["contribution"] = 99
        left, ok, info = leave_trouble_brewing_pure(player)
        self.assertTrue(ok)
        self.assertEqual(left["trouble_brewing_pieces_of_eight"], 7)
        self.assertEqual(left["trouble_brewing"], {})
        self.assertIn("forfeited", info["message"])


class TroubleBrewingRewardTests(unittest.TestCase):
    def test_reward_shop_spends_wallet_and_banks_the_zero_stat_hat(self):
        player = _player(trouble_brewing_pieces_of_eight=50)
        bought, ok, info = buy_trouble_brewing_reward_pure(
            player, "blue_tricorn_hat"
        )
        self.assertTrue(ok, info)
        self.assertEqual(bought["trouble_brewing_pieces_of_eight"], 0)
        self.assertEqual(bought["inventory"]["Blue tricorn hat"], 1)
        view = trouble_brewing_view_pure(bought)
        blue_hat = next(
            reward
            for reward in view["rewards"]
            if reward["reward_id"] == "blue_tricorn_hat"
        )
        self.assertEqual(blue_hat["pieces_of_eight"], 50)

        _same, ok, info = buy_trouble_brewing_reward_pure(
            bought, "blue_tricorn_hat"
        )
        self.assertFalse(ok)
        self.assertIn("Requires 50", info["reason"])

    def test_expensive_flag_uses_the_same_atomic_purchase_path(self):
        player = _player(trouble_brewing_pieces_of_eight=600)
        bought, ok, info = buy_trouble_brewing_reward_pure(
            player, "phasmatys_flag"
        )
        self.assertTrue(ok, info)
        self.assertEqual(bought["trouble_brewing_pieces_of_eight"], 0)
        self.assertEqual(bought["inventory"]["Phasmatys flag"], 1)
        self.assertNotIn("Phasmatys flag", player["inventory"])

    def test_each_coloured_rum_is_bought_drunk_consumed_and_teleports(self):
        for reward_id, item_name in (("red_rum", "Red rum"), ("blue_rum", "Blue rum")):
            with self.subTest(item=item_name):
                bought, ok, info = buy_trouble_brewing_reward_pure(
                    _player(trouble_brewing_pieces_of_eight=2), reward_id
                )
                self.assertTrue(ok, info)
                self.assertEqual(bought["inventory"][item_name], 1)
                teleported, ok, info = drink_trouble_brewing_rum_pure(
                    bought, item_name
                )
                self.assertTrue(ok, info)
                self.assertNotIn(item_name, teleported["inventory"])
                self.assertEqual(info["destination"], "Trouble Brewing")
                self.assertIn("teleported to Trouble Brewing", info["message"])

    def test_rum_refuses_unknown_missing_and_mid_match_uses_without_mutation(self):
        for player, item_name, reason in (
            (_player(), "Karamja rum", "not Trouble Brewing"),
            (_player(), "Red rum", "No Red rum"),
            (_entered(inventory={"Blue rum": 1}), "Blue rum", "current game"),
        ):
            with self.subTest(reason=reason):
                unchanged, ok, info = drink_trouble_brewing_rum_pure(
                    player, item_name
                )
                self.assertFalse(ok)
                self.assertIn(reason, info["reason"])
                self.assertEqual(unchanged, player)

    def test_medium_clue_service_charges_once_and_obeys_one_clue_total(self):
        bought, ok, info = buy_trouble_brewing_reward_pure(
            _player(trouble_brewing_pieces_of_eight=5_000),
            "medium_clue",
        )
        self.assertTrue(ok, info)
        self.assertEqual(bought["inventory"][CLUE_SCROLL_ITEMS["medium"]], 1)
        self.assertEqual(bought["trouble_brewing_pieces_of_eight"], 0)

        for held_item in CLUE_SCROLL_ITEMS.values():
            with self.subTest(held=held_item):
                player = _player(
                    inventory={held_item: 1},
                    trouble_brewing_pieces_of_eight=5_000,
                )
                unchanged, ok, info = buy_trouble_brewing_reward_pure(
                    player,
                    "medium_clue",
                )
                self.assertFalse(ok)
                self.assertIn("already have a clue scroll", info["reason"])
                self.assertEqual(unchanged, player)

    def test_medium_clue_view_exposes_the_central_ownership_blocker(self):
        available = trouble_brewing_view_pure(
            _player(trouble_brewing_pieces_of_eight=5_000)
        )
        available_row = next(
            row for row in available["rewards"] if row["reward_id"] == "medium_clue"
        )
        self.assertEqual(available_row["clue_tier"], "medium")
        self.assertEqual(available_row["blocked_reason"], "")

        blocked = trouble_brewing_view_pure(
            _player(
                inventory={CLUE_SCROLL_ITEMS["hard"]: 1},
                trouble_brewing_pieces_of_eight=5_000,
            )
        )
        blocked_row = next(
            row for row in blocked["rewards"] if row["reward_id"] == "medium_clue"
        )
        self.assertIn("Clue scroll (hard)", blocked_row["blocked_reason"])

    def test_command_router_blocks_shopping_during_a_live_game(self):
        player = _entered(trouble_brewing_pieces_of_eight=50)
        unchanged, ok, info = apply_trouble_brewing_command_pure(
            player,
            "buy_reward",
            {"reward_id": "blue_tricorn_hat"},
        )
        self.assertFalse(ok)
        self.assertIn("current game", info["reason"])
        self.assertEqual(unchanged["trouble_brewing_pieces_of_eight"], 50)
        self.assertEqual(unchanged["inventory"], {})


if __name__ == "__main__":
    unittest.main()
