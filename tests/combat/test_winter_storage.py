import copy
import unittest

from tests import test_combat_logic as combat


class WinterStorageTest(unittest.TestCase):
    def setUp(self):
        carried = {"Bones": 2, "Coins": 2, "Big bones": 1, "Winter storage scroll": 1}
        self.player = {
            "inventory": dict(carried),
            "carried_inventory": {"chicken": dict(carried)},
            "current_combat_target": "chicken",
            "combat_supply_loadout": {},
            "combat_encounter": {"target_id": "chicken", "enemy_lifepoints": 3},
            "combat_last_result": {"stop_reason": "ticks", "player_damage": 7},
            "summoning_exp": 10.0,
            "summoning_state": {
                "active_follower": {"kind": "familiar", "entity_id": "packyak"},
                "special_move_points_current": 60,
                "target_policies": {
                    "chicken": {"winter_storage_priority": ["Bones", "Coins", "Big bones"]}
                },
                "event_log": [{"kind": "summon"}],
            },
        }

    def store(self, player):
        return combat._combat_try_pack_yak_winter_storage(
            player, "chicken", "melee", {}, {}, {}, combat.COMBAT_ENEMY_DATA
        )

    def test_custom_supplies_and_multi_item_stacks_are_not_selected(self):
        self.player["carried_advanced_targets"] = {"chicken": True}
        self.player["carried_layout"] = {"chicken": {"Bones": 2}}
        before = copy.deepcopy(self.player)

        self.assertTrue(self.store(self.player))

        self.assertEqual(self.player["carried_inventory"]["chicken"], {"Bones": 2, "Coins": 2})
        self.assertEqual(self.player["inventory"]["Bones"], 2)
        self.assertEqual(self.player["inventory"]["Big bones"], 1)
        self.assertEqual(self.player["inventory"]["Winter storage scroll"], 0)
        self.assertEqual(self.player["combat_encounter"], before["combat_encounter"])
        self.assertEqual(self.player["combat_last_result"], before["combat_last_result"])
        self.assertEqual(self.player["summoning_state"]["event_log"][-1], {
            "kind": "winter_storage", "target_id": "chicken", "item": "Big bones", "xp": 4.8,
        })

    def test_priority_accepts_one_stack_item_or_a_string(self):
        for priority, selected in (([None, "Winter storage scroll", "Coins", "Bones"], "Coins"), ("Bones", "Bones")):
            with self.subTest(priority=priority):
                player = copy.deepcopy(self.player)
                player["carried_inventory"]["chicken"]["Coins"] = 1
                player["summoning_state"]["target_policies"]["chicken"]["winter_storage_priority"] = priority

                self.assertTrue(self.store(player))

                self.assertEqual(player["summoning_state"]["event_log"][-1]["item"], selected)
                self.assertEqual(player["summoning_state"]["special_move_points_current"], 48)
                self.assertEqual(player["summoning_exp"], 14.8)

    def test_no_eligible_loot_preserves_supplies_and_fight(self):
        for priority in ([], 3, ["Coins"], ["Winter storage scroll"], ["missing"]):
            with self.subTest(priority=priority):
                player = copy.deepcopy(self.player)
                player["summoning_state"]["target_policies"]["chicken"]["winter_storage_priority"] = priority
                before = copy.deepcopy(player)
                original_carried = player["carried_inventory"]
                original_state = player["summoning_state"]

                self.assertFalse(self.store(player))

                self.assertEqual(player, before)
                self.assertIs(player["carried_inventory"], original_carried)
                self.assertIs(player["summoning_state"], original_state)

    def test_candidate_that_still_needs_a_bank_run_preserves_every_field(self):
        for needs_food in (False, True):
            with self.subTest(needs_food=needs_food):
                player = copy.deepcopy(self.player)
                if needs_food:
                    player["inventory"]["Shark"] = 3
                    player["combat_auto_eat_food"] = ["Shark"]
                else:
                    loot = {f"Loot {index}": 1 for index in range(30)}
                    player["inventory"].update(loot)
                    player["carried_inventory"]["chicken"].update(loot)
                before = copy.deepcopy(player)
                original_encounter = player["combat_encounter"]
                original_state = player["summoning_state"]

                self.assertFalse(self.store(player))

                self.assertEqual(player, before)
                self.assertIs(player["combat_encounter"], original_encounter)
                self.assertIs(player["summoning_state"], original_state)
