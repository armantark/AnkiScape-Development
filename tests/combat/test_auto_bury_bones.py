"""Auto-bury keeps learning drops and honours keep/drop overrides.

Owner note 2026-08-30: with "Auto-bury bones" on, the bury step consumed
every bone from the kill's drops before the drop recorder ran, so the
per-drop keep/drop control never offered Bones.
"""

import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from tests.test_runtime_actions import _context
from ankiscape.runtime import runtime_actions_combat
from ankiscape.runtime.runtime_actions import handle_combat_answer


def _chicken_player_data(**extra):
    player_data = {
        "inventory": {},
        "equipment": {},
        "current_combat_target": "chicken",
        "combat_attack_style": "accurate",
        "combat_lifepoints": 100,
        "combat_auto_eat_food": ["Shrimps"],
        "attack_level": 99,
        "strength_level": 99,
        "defense_level": 99,
        "constitution_level": 10,
        "attack_exp": 0.0,
        "strength_exp": 0.0,
        "defense_exp": 0.0,
        "constitution_exp": 0.0,
        "completed_achievements": [],
    }
    player_data.update(extra)
    return player_data


def _kill_chicken(player_data):
    calls = {"xp": [], "saves": 0, "errors": []}
    ok = handle_combat_answer(_context(player_data, calls, [0.0, 0.999999, 0.0]))
    return ok, calls


class AutoBuryBonesTest(unittest.TestCase):
    def test_auto_buried_kill_still_learns_bones_as_a_drop(self):
        player_data = _chicken_player_data(combat_auto_prayer_training=True)

        ok, _calls = _kill_chicken(player_data)

        self.assertTrue(ok)
        observed = player_data["combat_observed_drops"]["chicken"]
        self.assertIn("Bones", observed)
        self.assertEqual(observed["Bones"]["times_seen"], 1)
        self.assertEqual(observed["Bones"]["quantity_seen"], 1)
        # The bury step still consumed the learned bone, and the kill still
        # seeded the drop's Keep default for the day auto-bury turns off.
        self.assertNotIn("Bones", player_data["inventory"])
        self.assertEqual(player_data["loot_overrides"]["Bones"], "keep")
        self.assertGreater(player_data["prayer_exp"], 0.0)
        self.assertEqual(player_data["loot_overrides"].get("Raw chicken"), "keep")

    def test_auto_bury_honours_a_drop_override_by_leaving_the_bone(self):
        player_data = _chicken_player_data(
            combat_auto_prayer_training=True,
            loot_overrides={"Bones": "leave"},
        )

        ok, _calls = _kill_chicken(player_data)

        self.assertTrue(ok)
        # The override spares the bone from burial: no Prayer XP from it and no
        # pack entry — the loot filter leaves it where it fell. (The burst's
        # inventory fold is undone by the filter; only the zeroed key remains.)
        self.assertEqual(player_data["inventory"].get("Bones"), 0)
        self.assertNotIn("Bones", player_data["carried_inventory"].get("chicken", {}))
        self.assertGreater(player_data["attack_exp"], 0.0)
        self.assertEqual(player_data.get("prayer_exp", 0.0), 0.0)
        self.assertEqual(
            player_data["combat_observed_drops"]["chicken"]["Bones"]["times_seen"], 1
        )

    def test_auto_bury_off_still_sends_bones_to_the_pack(self):
        player_data = _chicken_player_data(combat_auto_prayer_training=False)

        ok, _calls = _kill_chicken(player_data)

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"]["Bones"], 1)
        self.assertEqual(player_data["carried_inventory"]["chicken"]["Bones"], 1)
        self.assertEqual(player_data["loot_overrides"]["Bones"], "keep")

    def test_turning_auto_bury_off_sends_bones_to_the_pack_after_a_buried_kill(self):
        # The first (buried) kill learns Bones and must seed its Keep default
        # even though the bone was consumed before the loot filter ran;
        # otherwise the first un-buried kill would leave the bone on the ground.
        player_data = _chicken_player_data(combat_auto_prayer_training=True)

        ok, _calls = _kill_chicken(player_data)
        self.assertTrue(ok)
        self.assertNotIn("Bones", player_data["inventory"])

        player_data["combat_auto_prayer_training"] = False
        ok, _calls = _kill_chicken(player_data)

        self.assertTrue(ok)
        self.assertEqual(player_data["inventory"]["Bones"], 1)
        self.assertEqual(player_data["carried_inventory"]["chicken"]["Bones"], 1)
        self.assertEqual(player_data["loot_overrides"]["Bones"], "keep")

    def test_finisher_kill_still_learns_bones_as_a_drop(self):
        # The finisher path records drops separately from the burst path; the
        # learning record must survive there too. Desert lizard carries the
        # guaranteed Bones drop and its Ice cooler finisher.
        player_data = _chicken_player_data(
            combat_auto_prayer_training=True,
            combat_action="finisher",
            current_combat_target="desert_lizard",
            combat_encounter={"target_id": "desert_lizard", "enemy_lifepoints": 30},
            combat_supply_loadout={
                "finishers": {"Ice cooler": 1},
                "hazards": {"Waterskin (4)": 1},
            },
            slayer_level=99,
        )

        ok, _calls = _kill_chicken(player_data)

        self.assertTrue(ok)
        self.assertEqual(player_data["combat_action"], "attack")
        observed = player_data["combat_observed_drops"]["desert_lizard"]
        self.assertIn("Bones", observed)
        self.assertEqual(observed["Bones"]["times_seen"], 1)
        # The bury step still consumed the learned bone.
        self.assertNotIn("Bones", player_data["inventory"])
        self.assertGreater(player_data["prayer_exp"], 0.0)


if __name__ == "__main__":
    unittest.main()
