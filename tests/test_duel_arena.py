from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import (
    ITEM_DEFINITIONS,
    ORE_DATA,
    UTILITY_ACTIVITY_DATA,
)
from ankiscape.core.storage_pure import (
    CURRENT_CONFIG_VERSION,
    default_player_data,
    migrate_loaded_data,
)
from ankiscape.data.duel_arena_data import (
    DUEL_ARENA_ACTIVITY_ID,
    DUEL_ARENA_MAX_COMBAT_LEVEL,
    DUEL_ARENA_MAX_REVIEWS,
    DUEL_ARENA_MIN_COMBAT_LEVEL,
    DUEL_ARENA_RULE_PRESETS,
    DUELLISTS_CAP_TIERS,
)
from ankiscape.logic.duel_arena_logic import (
    abandon_duel_arena_pure,
    apply_duel_arena_review_pure,
    claim_duellists_cap_pure,
    default_duel_arena_state_pure,
    duel_arena_view_pure,
    enter_duel_arena_pure,
    sanitize_duel_arena_state_pure,
    set_duel_arena_rules_pure,
)
from ankiscape.logic_pure.logic_pure import combat_max_lifepoints_pure
from ankiscape.runtime.runtime_actions import (
    RuntimeActionContext,
    handle_utility_answer,
)


ROOT = Path(__file__).resolve().parents[1]


def _player() -> dict:
    player = {
        "inventory": {"Coins": 12_345, "Lobster": 4},
        "equipment": {},
        "combat_encounter": {},
        "activity_session": {"active_id": ""},
        "current_combat_target": "chicken",
        "current_utility": "make_soft_clay",
        "attack_level": 60,
        "strength_level": 60,
        "defense_level": 60,
        "constitution_level": 60,
        "ranged_level": 40,
        "magic_level": 40,
        "prayer_level": 43,
        "summoning_level": 1,
        "combat_lifepoints": 1,
        "combat_prayer_points": 0,
        "combat_special_attack_energy": 0,
        "combat_current_levels": {"attack": 3, "defense": 4},
        "combat_status_effects": {"poison": 50, "attack": -7},
        "agility_run_energy_credit_pct": 0,
        "completed_achievements": [],
    }
    player.update(default_duel_arena_state_pure())
    return player


def _win_duel(player: dict) -> dict:
    player, ok, _ = enter_duel_arena_pure(player, ())
    if not ok:
        raise AssertionError("test player could not enter a duel")
    for _ in range(3):
        player, ok, result = apply_duel_arena_review_pure(
            player,
            lambda: 0.0,
        )
        if not ok:
            raise AssertionError(result)
    if result.get("outcome") != "win":
        raise AssertionError(result)
    return player


def _context(player_data: dict, calls: dict) -> RuntimeActionContext:
    return RuntimeActionContext(
        player_data=player_data,
        random_random=lambda: 0.0,
        show_error_message=lambda title, message: calls["errors"].append(
            (title, message)
        ),
        deactivate_current_skill=lambda: calls.__setitem__("deactivated", True),
        award_skill_exp=lambda _key, amount: amount,
        award_hidden_skill_exp=lambda *_args: None,
        level_up_check=lambda *_args: None,
        check_achievements=lambda _data: calls.__setitem__(
            "achievements", True
        ),
        save_player_data=lambda: calls.__setitem__("saves", calls["saves"] + 1),
        refresh_skill_availability=lambda: calls.__setitem__("refresh", True),
        refresh_skill_availability_partial=lambda *_args: None,
        can_smith_any=lambda: False,
        show_exp=lambda amount: calls["xp"].append(amount),
        show_activity_gain=lambda message: calls["activity"].append(message),
        implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda _before: None,
    )


class DuelArenaDataTest(unittest.TestCase):
    def test_period_rule_and_cap_definitions_are_complete(self):
        self.assertEqual(len(DUEL_ARENA_RULE_PRESETS), 11)
        self.assertEqual(
            tuple(rule.id for rule in DUEL_ARENA_RULE_PRESETS),
            (
                "no_ranged",
                "no_melee",
                "no_magic",
                "no_special_attacks",
                "fun_weapons",
                "no_forfeit",
                "no_drinks",
                "no_food",
                "no_prayer",
                "no_movement",
                "obstacles",
            ),
        )
        self.assertEqual(
            tuple(tier.minimum_wins for tier in DUELLISTS_CAP_TIERS),
            (0, 10, 100, 500, 2_000, 5_000),
        )
        self.assertEqual(
            tuple(tier.source_item_id for tier in DUELLISTS_CAP_TIERS),
            tuple(range(20_795, 20_801)),
        )

    def test_activity_cap_items_and_assets_are_registered(self):
        activity = UTILITY_ACTIVITY_DATA[DUEL_ARENA_ACTIVITY_ID]
        self.assertEqual(activity["surface"], "activities")
        self.assertTrue(Path(activity["icon_path"]).is_file())
        definitions = {item.storage_key: item for item in ITEM_DEFINITIONS}
        provenance = json.loads(
            (ROOT / "assets_provenance.json").read_text(encoding="utf-8")
        )
        self.assertIn("activityicons/duel_arena.png", provenance)
        for tier in DUELLISTS_CAP_TIERS:
            definition = definitions[tier.item_name]
            self.assertEqual(definition.source_item_id, tier.source_item_id)
            self.assertTrue(Path(definition.asset_path).is_file())
            self.assertIn(
                f"activityitems/{tier.asset_filename}",
                provenance,
            )


class DuelArenaPureTest(unittest.TestCase):
    def test_rules_configure_and_reject_invalid_combinations(self):
        original = _player()
        updated, ok, result = set_duel_arena_rules_pure(
            original,
            ("no_food", "no_prayer"),
        )
        self.assertTrue(ok)
        self.assertEqual(updated["duel_arena_rule_ids"], ("no_food", "no_prayer"))
        self.assertEqual(original["duel_arena_rule_ids"], ())
        self.assertIn("Saved 2", result["message"])
        for preset in DUEL_ARENA_RULE_PRESETS:
            with self.subTest(rule_id=preset.id):
                configured, ok, _ = set_duel_arena_rules_pure(
                    original,
                    (preset.id,),
                )
                self.assertTrue(ok)
                self.assertEqual(configured["duel_arena_rule_ids"], (preset.id,))

        _, ok, result = set_duel_arena_rules_pure(
            original,
            ("no_ranged", "no_melee", "no_magic"),
        )
        self.assertFalse(ok)
        self.assertIn("combat style", result["reason"])
        _, ok, result = set_duel_arena_rules_pure(
            original,
            ("no_movement", "obstacles"),
        )
        self.assertFalse(ok)
        self.assertIn("cannot", result["reason"])
        _, ok, result = set_duel_arena_rules_pure(original, ("invented_rule",))
        self.assertFalse(ok)
        self.assertIn("Unknown", result["reason"])

    def test_entry_is_free_deterministic_and_bounded(self):
        original = _player()
        inventory = copy.deepcopy(original["inventory"])
        first, ok, _ = enter_duel_arena_pure(original, ("no_food",))
        self.assertTrue(ok)
        second, ok, _ = enter_duel_arena_pure(original, ("no_food",))
        self.assertTrue(ok)
        self.assertEqual(
            first["duel_arena"]["opponent"],
            second["duel_arena"]["opponent"],
        )
        level = first["duel_arena"]["opponent"]["combat_level"]
        self.assertGreaterEqual(level, DUEL_ARENA_MIN_COMBAT_LEVEL)
        self.assertLessEqual(level, DUEL_ARENA_MAX_COMBAT_LEVEL)
        self.assertEqual(first["inventory"], inventory)
        self.assertEqual(original["inventory"], inventory)
        self.assertEqual(first["current_utility"], DUEL_ARENA_ACTIVITY_ID)
        self.assertEqual(
            first["activity_session"]["active_id"],
            DUEL_ARENA_ACTIVITY_ID,
        )

        low, ok, _ = enter_duel_arena_pure(original, (), opponent_level=-999)
        self.assertTrue(ok)
        self.assertEqual(
            low["duel_arena"]["opponent"]["combat_level"],
            DUEL_ARENA_MIN_COMBAT_LEVEL,
        )
        high, ok, _ = enter_duel_arena_pure(original, (), opponent_level=999)
        self.assertTrue(ok)
        self.assertEqual(
            high["duel_arena"]["opponent"]["combat_level"],
            DUEL_ARENA_MAX_COMBAT_LEVEL,
        )

    def test_review_failures_and_nonproductive_reviews_do_not_advance(self):
        player = _player()
        unchanged, ok, result = apply_duel_arena_review_pure(player)
        self.assertFalse(ok)
        self.assertEqual(unchanged, player)
        self.assertIn("Enter", result["reason"])

        player, ok, _ = enter_duel_arena_pure(player, ())
        self.assertTrue(ok)
        unchanged, ok, result = apply_duel_arena_review_pure(
            player,
            productive=False,
        )
        self.assertTrue(ok)
        self.assertFalse(result["advanced"])
        self.assertEqual(unchanged["duel_arena"]["review"], 0)

    def test_alternating_simulation_terminates_at_the_five_review_bound(self):
        player, ok, _ = enter_duel_arena_pure(_player(), ())
        self.assertTrue(ok)
        draws = iter((0.0, 1.0, 0.0, 1.0, 0.0))
        for review in range(DUEL_ARENA_MAX_REVIEWS):
            player, ok, result = apply_duel_arena_review_pure(
                player,
                lambda: next(draws),
            )
            self.assertTrue(ok)
        self.assertTrue(result["terminal"])
        self.assertEqual(review + 1, DUEL_ARENA_MAX_REVIEWS)
        self.assertEqual(result["outcome"], "win")
        self.assertEqual(
            (result["player_points"], result["opponent_points"]),
            (3, 2),
        )

    def test_every_cap_tier_is_reachable_and_owned_through_real_wins(self):
        player, ok, result = claim_duellists_cap_pure(_player())
        self.assertTrue(ok)
        self.assertEqual(result["cap"]["tier"], 1)
        self.assertEqual(player["inventory"][DUELLISTS_CAP_TIERS[0].item_name], 1)
        expected_tiers = {10: 2, 100: 3, 500: 4, 2_000: 5, 5_000: 6}
        for win_count in range(1, 5_001):
            player = _win_duel(player)
            if win_count in expected_tiers:
                with self.subTest(win_count=win_count):
                    view = duel_arena_view_pure(player)
                    tier = expected_tiers[win_count]
                    item_name = DUELLISTS_CAP_TIERS[tier - 1].item_name
                    self.assertEqual(view["cap"]["tier"], tier)
                    self.assertEqual(view["owned_cap_item"], item_name)
                    self.assertEqual(player["inventory"][item_name], 1)
                    self.assertEqual(
                        sum(
                            int(player["inventory"].get(row.item_name, 0))
                            for row in DUELLISTS_CAP_TIERS
                        ),
                        1,
                    )
        self.assertEqual(player["duel_arena_wins"], 5_000)
        self.assertEqual(player["inventory"]["Coins"], 12_345)

    def test_safe_loss_restores_all_stats_without_coin_or_item_mutation(self):
        player = _player()
        inventory = copy.deepcopy(player["inventory"])
        player, ok, _ = enter_duel_arena_pure(player, ())
        self.assertTrue(ok)
        for review in range(DUEL_ARENA_MAX_REVIEWS):
            player, ok, result = apply_duel_arena_review_pure(
                player,
                lambda: 1.0,
            )
            self.assertTrue(ok)
            if result.get("terminal"):
                break
        self.assertLessEqual(review + 1, DUEL_ARENA_MAX_REVIEWS)
        self.assertEqual(result["outcome"], "loss")
        self.assertEqual(player["inventory"], inventory)
        self.assertEqual(
            player["combat_lifepoints"],
            combat_max_lifepoints_pure(player),
        )
        self.assertEqual(player["combat_prayer_points"], 430)
        self.assertEqual(player["combat_special_attack_energy"], 100)
        self.assertEqual(player["combat_current_levels"], {})
        self.assertEqual(player["combat_status_effects"], {})
        self.assertEqual(player["agility_run_energy_credit_pct"], 100)
        self.assertEqual(player["combat_encounter"], {})
        self.assertEqual(player["current_combat_target"], "chicken")

    def test_abandon_is_safe_and_no_forfeit_is_enforced(self):
        player = _player()
        _, ok, result = abandon_duel_arena_pure(player)
        self.assertFalse(ok)
        self.assertIn("No Duel Arena", result["reason"])

        no_forfeit, ok, _ = enter_duel_arena_pure(
            player,
            ("no_forfeit",),
        )
        self.assertTrue(ok)
        no_forfeit["combat_lifepoints"] = 1
        unchanged, ok, result = abandon_duel_arena_pure(no_forfeit)
        self.assertFalse(ok)
        self.assertIn("No Forfeit", result["reason"])
        self.assertEqual(unchanged["combat_lifepoints"], 1)
        self.assertTrue(unchanged["duel_arena"])

        player, ok, _ = enter_duel_arena_pure(player, ())
        self.assertTrue(ok)
        player["combat_lifepoints"] = 1
        player, ok, result = abandon_duel_arena_pure(player)
        self.assertTrue(ok)
        self.assertEqual(result["outcome"], "abandon")
        self.assertEqual(player["duel_arena_abandons"], 1)
        self.assertEqual(
            player["combat_lifepoints"],
            combat_max_lifepoints_pure(player),
        )
        self.assertEqual(player["inventory"]["Coins"], 12_345)

    def test_persistence_normalizes_owned_keys_and_preserves_unknown_data(self):
        state = sanitize_duel_arena_state_pure(
            {
                "duel_arena_wins": 120,
                "duel_arena_rule_ids": ("no_food", "unknown"),
                "duel_arena_losses": -2,
            }
        )
        self.assertEqual(
            duel_arena_view_pure(state)["cap"]["tier"],
            3,
        )
        self.assertEqual(state["duel_arena_rule_ids"], ("no_food",))
        self.assertEqual(state["duel_arena_losses"], 0)

        old = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        old["config_version"] = 81
        old["unrelated_future_key"] = {"keep": True}
        for key in default_duel_arena_state_pure():
            old.pop(key, None)
        migrated = migrate_loaded_data(old, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["duel_arena"], {})
        self.assertNotIn("duel_arena_cap_tier", migrated)
        self.assertEqual(migrated["unrelated_future_key"], {"keep": True})


class DuelArenaRuntimeIntegrationTest(unittest.TestCase):
    def test_selected_duel_dispatches_reviews_and_saves_terminal_result(self):
        player, ok, _ = enter_duel_arena_pure(_player(), ())
        self.assertTrue(ok)
        calls = {
            "errors": [],
            "activity": [],
            "xp": [],
            "saves": 0,
            "deactivated": False,
        }
        context = _context(player, calls)
        for _ in range(3):
            self.assertTrue(handle_utility_answer(context))
        self.assertEqual(player["duel_arena_wins"], 1)
        self.assertEqual(player["duel_arena"], {})
        self.assertEqual(calls["saves"], 3)
        self.assertTrue(calls["deactivated"])
        self.assertIn("Duel won", calls["activity"][-1])
        telemetry = player["action_telemetry"]["actions"]
        self.assertEqual(
            telemetry[f"utility:{DUEL_ARENA_ACTIVITY_ID}"]["attempts"],
            3,
        )


if __name__ == "__main__":
    unittest.main()
