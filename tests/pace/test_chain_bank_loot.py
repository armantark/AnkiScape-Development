"""A kill fills the pack before another enemy starts, without paying loot twice."""

import unittest

import pkg_alias  # noqa: F401
from ankiscape.data.item_values import STACKABLE_ITEM_NAMES
from ankiscape.logic.inventory_pure import carried_slots_used
from tests.pace.test_combat_chain import player_hits_only
from tests.pace.test_combat_danger_stops import ENEMY, answer_combat
from tests.test_combat_logic import _player


def loaded_player(**overrides):
    loadout = overrides.pop("combat_supply_loadout", {"food": {"Shrimps": 20}})
    return _player(
        combat_auto_flee=False,
        combat_supply_loadout=loadout,
        inventory={"Bones": 7},
        carried_inventory={"chicken": {"Bones": 7}},
        **overrides,
    )


class ChainBankLootTests(unittest.TestCase):
    def test_the_first_kill_fills_the_pack_and_awards_its_loot_and_xp_once(self):
        player = loaded_player()
        enemy = {**ENEMY, "stats": {**ENEMY["stats"], "hitpoints": 60}}
        ctx, _calls, ok = answer_combat(player, enemy=enemy, hits=player_hits_only)
        self.assertTrue(ok)
        result = ctx.player_data["combat_last_result"]
        self.assertEqual((result["kills"], result["ticks_elapsed"]), (1, 21))
        self.assertEqual(ctx.card.stop_reason, "bank_trip")
        self.assertEqual(result["drops"], {"Bones": 1})
        self.assertEqual(ctx.player_data["inventory"]["Bones"], 8)
        carried = ctx.player_data["carried_inventory"]["chicken"]
        self.assertEqual(carried, {"Bones": 8})
        self.assertEqual(20 + carried_slots_used(carried, STACKABLE_ITEM_NAMES), 28)
        self.assertEqual(ctx.player_data["combat_kill_counts"]["chicken"], 1)
        self.assertEqual(ctx.player_data["attack_exp"], result["xp_rewards"]["attack_exp"])
        self.assertEqual(ctx.player_data["constitution_exp"], result["xp_rewards"]["constitution_exp"])
        self.assertEqual(ctx.player_data["combat_encounter"], {})
        self.assertFalse(ctx.player_data.get("combat_bank_run"))

    def test_pending_loot_from_both_kills_counts_and_each_reward_settles_once(self):
        player = loaded_player()
        player["inventory"]["Bones"] = 6
        player["carried_inventory"]["chicken"]["Bones"] = 6
        enemy = {**ENEMY, "stats": {**ENEMY["stats"], "hitpoints": 60}}
        ctx, _calls, ok = answer_combat(player, enemy=enemy, hits=player_hits_only)
        self.assertTrue(ok)
        result = ctx.player_data["combat_last_result"]
        self.assertEqual((result["kills"], result["ticks_elapsed"]), (2, 45))
        self.assertEqual(ctx.card.stop_reason, "bank_trip")
        self.assertEqual(result["drops"], {"Bones": 2})
        self.assertEqual(ctx.player_data["inventory"]["Bones"], 8)
        self.assertEqual(ctx.player_data["carried_inventory"]["chicken"], {"Bones": 8})
        self.assertEqual(ctx.player_data["attack_exp"], result["xp_rewards"]["attack_exp"])
        self.assertEqual(ctx.player_data["constitution_exp"], result["xp_rewards"]["constitution_exp"])
        self.assertEqual(ctx.player_data["combat_observed_drops"]["chicken"]["Bones"]["quantity_seen"], 2)

    def test_a_known_below_threshold_drop_is_left_without_a_bank_stop(self):
        player = loaded_player(combat_observed_drops={"chicken": {"Bones": {"times_seen": 1, "quantity_seen": 1}}},
                               loot_value_threshold=1000000)
        enemy = {**ENEMY, "stats": {**ENEMY["stats"], "hitpoints": 60}}
        ctx, _calls, ok = answer_combat(player, enemy=enemy, hits=player_hits_only)
        self.assertTrue(ok)
        self.assertEqual(ctx.player_data["combat_last_result"]["kills"], 2)
        self.assertEqual(ctx.card.stop_reason, "")
        self.assertEqual(ctx.player_data["inventory"]["Bones"], 7)

    def test_a_reflected_kill_fills_the_pack_before_the_next_enemy(self):
        player = loaded_player(
            combat_attack_style="magic_standard", current_combat_spell="confuse",
            equipment={"weapon": "Staff"},
            combat_supply_loadout={"food": {"Shrimps": 17},
                                   "runes": {"Water rune": 100, "Earth rune": 100, "Body rune": 100}},
            combat_encounter={"target_id": "chicken", "enemy_lifepoints": 1,
                              "player_attack_ticks_remaining": 99,
                              "enemy_attack_ticks_remaining": 0, "vengeance_pending": True},
        )
        ctx, _calls, ok = answer_combat(player, hits=((True, 10),))
        self.assertTrue(ok)
        result = ctx.player_data["combat_last_result"]
        self.assertEqual((result["kills"], result["ticks_elapsed"]), (1, 1))
        self.assertEqual(ctx.card.stop_reason, "bank_trip")
        self.assertEqual(result["drops"], {"Bones": 1})
        self.assertEqual(ctx.player_data["inventory"]["Bones"], 8)
        self.assertEqual(ctx.player_data["carried_inventory"]["chicken"], {"Bones": 8})
        self.assertEqual(ctx.player_data["combat_encounter"], {})

    def test_left_loot_and_auto_buried_bones_do_not_fill_the_pack(self):
        for setting in ({"loot_overrides": {"Bones": "leave"}}, {"combat_auto_prayer_training": True}):
            with self.subTest(setting=setting):
                enemy = {**ENEMY, "stats": {**ENEMY["stats"], "hitpoints": 60}}
                ctx, _calls, ok = answer_combat(loaded_player(**setting), enemy=enemy, hits=player_hits_only)
                self.assertTrue(ok)
                result = ctx.player_data["combat_last_result"]
                self.assertEqual((result["kills"], result["ticks_elapsed"]), (2, 60))
                self.assertEqual(ctx.card.stop_reason, "")
                self.assertEqual(ctx.player_data["inventory"]["Bones"], 7)
                self.assertEqual(ctx.player_data["carried_inventory"]["chicken"], {"Bones": 7})
                if setting.get("combat_auto_prayer_training"):
                    self.assertEqual(ctx.player_data["prayer_exp"], 9.0)
