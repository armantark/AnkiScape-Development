import copy
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import (
    COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA,
)
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic_pure.logic_pure_combat_engine import apply_combat_burst_pure
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_combat_encounter_pure, apply_quest_progress_pure, start_quest_pure,
)
from ankiscape.runtime.runtime_actions import handle_quest_answer
from tests.test_runtime_actions import _context, _quest_combat_mid_rolls


class QuestAutoFleeTest(unittest.TestCase):
    def setUp(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player, ok = start_quest_pure(player, "vampyre_slayer", QUEST_DATA)
        self.assertTrue(ok)
        for _ in range(2):
            player, ok, completed = apply_quest_progress_pure(player, "vampyre_slayer", QUEST_DATA)
            self.assertTrue(ok)
            self.assertFalse(completed)
        player.update(
            attack_level=40, strength_level=40, defense_level=35,
            constitution_level=40, prayer_level=20, combat_lifepoints=400,
            current_combat_target="chicken",
            combat_encounter={"target_id": "chicken", "enemy_lifepoints": 10},
        )
        self.player = player

    def test_partial_quest_fight_preserves_preference_for_regular_combat(self):
        for preference in (True, False, None):
            with self.subTest(preference=preference):
                player = copy.deepcopy(self.player)
                player["combat_auto_flee"] = preference
                if preference is None:
                    player.pop("combat_auto_flee")
                before = copy.deepcopy(player)
                fought, ok, result = apply_quest_combat_encounter_pure(
                    player, "vampyre_slayer", QUEST_DATA, ticks=1,
                    rng=lambda: 0.5, equipment_data=EQUIPMENT_DATA,
                )
                self.assertTrue(ok, result)
                self.assertFalse(result["killed"])
                self.assertFalse(result["died"])
                self.assertGreater(result["player_damage"], 0)
                self.assertEqual(player, before)
                self.assertEqual(fought["combat_encounter"], before["combat_encounter"])
                self.assertEqual(fought["current_combat_target"], "chicken")
                self.assertEqual(fought["combat_auto_flee"], preference is not False)
                fought["combat_lifepoints"] = 1
                _, ok, regular = apply_combat_burst_pure(
                    fought, COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=1, rng=lambda: 0.0,
                )
                self.assertTrue(ok, regular)
                self.assertEqual(regular["fled"], preference is not False)

    def test_quest_death_preserves_preference_without_fleeing(self):
        for preference in (True, False):
            with self.subTest(preference=preference):
                player = dict(self.player, combat_lifepoints=1, combat_auto_flee=preference)
                defeated, ok, result = apply_quest_combat_encounter_pure(
                    player, "vampyre_slayer", QUEST_DATA, ticks=500,
                    rng=lambda: 0.0, equipment_data=EQUIPMENT_DATA,
                )
                self.assertTrue(ok, result)
                self.assertTrue(result["died"])
                self.assertFalse(result["fled"])
                self.assertEqual(defeated["combat_auto_flee"], preference)
                self.assertEqual(defeated["combat_encounter"], {})

    def test_runtime_saves_preference_after_quest_kill(self):
        for preference in (True, False):
            with self.subTest(preference=preference):
                player = copy.deepcopy(self.player)
                player["combat_auto_flee"] = preference
                saved = []
                ctx = _context(
                    player, random_values=_quest_combat_mid_rolls(), review_action_multiplier=10,
                )
                ctx.save_player_data = lambda: saved.append(copy.deepcopy(player))
                self.assertTrue(handle_quest_answer(ctx))
                self.assertEqual(len(saved), 1)
                self.assertTrue(saved[0]["combat_last_result"]["killed"])
                self.assertEqual(saved[0]["combat_auto_flee"], preference)
