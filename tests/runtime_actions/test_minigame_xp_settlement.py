"""Activity receipts describe XP already settled by the real combat kernel."""

import copy
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import EQUIPMENT_DATA
from ankiscape.logic import (
    barbarian_assault_logic,
    castle_wars_logic,
    pest_control_logic,
    soul_wars_logic,
)
from ankiscape.runtime import runtime_actions
from tests.test_runtime_actions import _context


class TestMinigameXpSettlement(unittest.TestCase):
    def _enter(self, activity, logic, duty, gear):
        player = {
            "activity_session": {"active_id": ""},
            "combat_encounter": {},
            "current_combat_target": "chicken",
            "combat_lifepoints": 400,
            "combat_supply_loadout": {},
            "inventory": {},
            "equipment": {},
            "completed_achievements": [],
            "barbarian_assault_tutorial_complete": True,
            "slayer_level": 99,
            **gear,
        }
        for skill in ("attack", "strength", "defense", "constitution", "ranged", "magic", "prayer"):
            player[skill + "_level"] = 50 if activity == "castle_wars" else 40
            player[skill + "_exp"] = 1000.0
        enter = getattr(logic, f"enter_{activity}_pure")
        player, ok, info = enter(
            player, {"automation_mode": "advanced", "duty": duty, "role": duty}
        )
        self.assertTrue(ok, info)
        if activity == "soul_wars":
            player[activity].update({"control_balance": 3, "enemy_avatar_slayer": 99})
        return player

    def _assert_review(self, activity, logic, player, productive, expects_xp):
        before = copy.deepcopy(player)
        roll = 0.1 if activity == "soul_wars" else 0.5
        options = {"productive": productive, "equipment_data": EQUIPMENT_DATA}
        if activity == "castle_wars":
            options["opponent_roll"] = 0.5
        advance = getattr(logic, f"apply_{activity}_review_pure")
        settled, ok, receipt = advance(before, lambda: roll, **options)
        self.assertTrue(ok, receipt)
        rewards = receipt.get("xp_rewards", {})
        total = sum(rewards.values())
        self.assertEqual(total > 0, expects_xp, receipt)
        calls = {"xp": [], "saves": 0, "errors": []}
        ctx = _context(player, calls, random_values=[roll] * 200)
        saved = []
        ctx.save_player_data = lambda: saved.append(copy.deepcopy(player))
        handler = getattr(runtime_actions, f"handle_{activity}_answer")
        self.assertTrue(handler(ctx, productive=productive))
        self.assertEqual(len(saved), 1)
        for key in (key for key in before if key.endswith("_exp")):
            with self.subTest(activity=activity, productive=productive, skill=key):
                self.assertAlmostEqual(settled[key] - before[key], rewards.get(key, 0.0))
                self.assertAlmostEqual(player[key], settled[key])
                self.assertAlmostEqual(saved[0][key], settled[key])
        self.assertEqual(player[activity], settled[activity])
        self.assertEqual(player["combat_encounter"], settled["combat_encounter"])
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["xp"], [total] if total > 0 else [])
        expected_skills = [
            key.removesuffix("_exp").title().replace("Defense", "Defence")
            for key, amount in rewards.items() if amount > 0
        ]
        self.assertEqual(calls.get("level_checks", []), expected_skills)
        self.assertTrue(calls.get("activity"))

    def assertActivity(self, activity, logic, duty, expects_xp=True, **gear):
        player = self._enter(activity, logic, duty, gear)
        self._assert_review(activity, logic, player, True, expects_xp)
        self._assert_review(activity, logic, player, False, False)
        self._assert_review(activity, logic, player, True, expects_xp)

    def test_castle_wars_defend_settles_xp_once(self):
        self.assertActivity("castle_wars", castle_wars_logic, "defend")

    def test_pest_control_assault_settles_half_rate_xp_once(self):
        self.assertActivity("pest_control", pest_control_logic, "assault")

    def test_soul_wars_avatar_settles_xp_once(self):
        self.assertActivity("soul_wars", soul_wars_logic, "avatar")

    def test_barbarian_assault_melee_attacker_earns_no_xp(self):
        self.assertActivity("barbarian_assault", barbarian_assault_logic, "attacker", False)

    def test_barbarian_assault_attacker_spell_settles_magic_xp_once(self):
        # The front's zero multiplier removes damage XP, but each cast still pays base Magic XP.
        self.assertActivity(
            "barbarian_assault",
            barbarian_assault_logic,
            "attacker",
            equipment={"weapon": "Staff"},
            combat_attack_style="magic_standard",
            current_combat_spell="wind_strike",
            combat_supply_loadout={"runes": {"Air rune": 50, "Mind rune": 50}},
        )
