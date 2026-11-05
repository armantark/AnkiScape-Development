"""Combat travel spends the card's play time through the real dispatcher."""

import random

from tests.integration_smoke.fixtures import ReviewedProfile
from tests.test_combat_logic import _player


class CombatDelayTests(ReviewedProfile):
    def _fight(self, speed=10, **fields):
        addon = self._addon("ankiscape_combat_delays")
        addon.mw.col.set_config("ankiscape_review_action_multiplier", speed)
        self._new_save(addon, **_player(
            current_combat_target="citizen", combat_prayers_enabled=False,
            combat_auto_flee=False, constitution_level=99, combat_lifepoints=990,
            equipment={"weapon": "Rune scimitar"}, inventory={"Lobster": 1000},
            combat_auto_eat_food=["Lobster"],
        ))
        addon._state.player_data.update(fields)
        addon._state.current_skill = "Combat"
        return addon

    def test_bank_run_uses_100_ticks_at_every_speed_and_fights_on_arrival(self):
        for speed, cards in ((1, 17), (10, 2), (20, 1)):
            with self.subTest(speed=speed):
                addon = self._fight(speed)
                random.seed(20261103)
                for _ in range(cards - 1):
                    self._answer(addon)
                    self.assertFalse(addon._state.player_data["combat_supply_loadout"]["food"])
                self._answer(addon)
                data = addon._state.player_data
                self.assertFalse(data["combat_bank_run"])
                self.assertTrue(data["combat_supply_loadout"]["food"])
                self.assertEqual(data["inventory"]["Lobster"], 986)
                self.assertEqual(data["combat_last_result"]["reason"], "combat_burst")
                self.assertEqual(data["combat_last_result"]["ticks_elapsed"], 6 * speed)
                self.assertEqual(self.errors, [])

    def test_agility_and_run_energy_credit_shorten_but_never_skip_restock(self):
        for agility, credit, remaining in ((1, 0, 40), (99, 0, 33), (99, 50, 0)):
            with self.subTest(agility=agility, credit=credit):
                addon = self._fight(agility_level=agility, agility_run_energy_credit_pct=credit)
                self._answer(addon)
                data = addon._state.player_data
                self.assertEqual(data.get("combat_bank_run", {}).get("ticks_remaining", 0), remaining)
                self.assertEqual(data.get("agility_run_energy_credit_pct", 0), 0)
                if not remaining:
                    self.assertTrue(data["combat_supply_loadout"]["food"])

    def test_old_bank_delay_finishes_on_next_card(self):
        addon = self._fight(current_combat_target="fire_giant", combat_bank_run={"reviews_remaining": 2, "target_id": "fire_giant"})
        self._answer(addon)
        self.assertFalse(addon._state.player_data["combat_bank_run"])
        self.assertTrue(addon._state.player_data["combat_supply_loadout"]["food"])

    def test_rest_reaches_full_lifepoints_after_180_ticks_at_each_speed(self):
        for speed, cards in ((1, 30), (10, 3), (20, 2)):
            with self.subTest(speed=speed):
                addon = self._fight(speed)
                addon._state.current_skill = "Utilities"
                addon._state.player_data.update(current_utility="bankstanding", combat_lifepoints=90)
                for _ in range(cards - 1):
                    self._answer(addon)
                self.assertLess(addon._state.player_data["combat_lifepoints"], 990)
                self._answer(addon)
                self.assertEqual(addon._state.player_data["combat_lifepoints"], 990)
                self.assertEqual(addon._state.player_data["combat_rest_ticks_remaining"], 0)

    def test_grave_walk_spends_300_ticks_before_the_selected_action_resumes(self):
        addon = self._fight(20)
        addon._state.current_skill = "Mining"
        addon._state.player_data.update(
            current_ore="iron", mining_level=99, mining_exp=13034431.0,
            toolbelt={"mining": ["rune_pickaxe"]},
            combat_grave={"items": ["Bronze sword"], "reviews_remaining": 5,
                          "walk_ticks_remaining": 300, "loadout": {"weapon": "Bronze sword"}},
        )
        self._answer(addon)
        self._answer(addon)
        self.assertEqual(addon._state.player_data["combat_grave"]["walk_ticks_remaining"], 60)
        self.assertNotIn("Iron ore", addon._state.player_data["inventory"])
        self._answer(addon)
        self.assertFalse(addon._state.player_data["combat_grave"])
        self.assertEqual(addon._state.player_data["inventory"]["Bronze sword"], 1)
        self.assertGreater(addon._state.player_data["inventory"]["Iron ore"], 0)

    def test_quest_bank_arrival_keeps_the_enemy_lifepoints(self):
        from ankiscape.data.quest.witchs_house import EXPERIMENTS
        from tests.quests.test_witchs_house import player_at

        addon = self._fight(20)
        data = addon._state.player_data
        quest = player_at(12)
        data.update({key: quest[key] for key in ("current_quest", "quests", "quest_action_proofs")})
        encounter = EXPERIMENTS[2][0]
        data.update(
            quest_combat_encounters={"witchs_house": [row[0] for row in EXPERIMENTS[:2]]},
            quest_combat_active_encounters={"witchs_house": {encounter: 1000}},
        )
        addon._state.current_skill = "Quests"
        self._answer(addon)
        result = data["combat_last_result"]
        self.assertEqual(result["reason"], "quest_combat_burst")
        self.assertEqual(result["enemy_lifepoints"] + result["player_damage"], 1000)
        self.assertEqual(result["ticks_elapsed"], 120)
        self.assertFalse(data["combat_bank_run"])
        self.assertEqual(self.errors, [])

    def test_queue_handover_after_arrival_preserves_the_remaining_ticks(self):
        from ankiscape.core.action_queue import add_to_action_queue

        addon = self._fight()
        data = addon._state.player_data
        data.update(mining_level=99, mining_exp=13034431.0, toolbelt={"mining": ["rune_pickaxe"]})
        self.assertEqual(add_to_action_queue(addon, {"kind": "combat", "target": "citizen", "combat_action": "attack"}, 1), "")
        self.assertEqual(add_to_action_queue(addon, {"kind": "skill", "skill": "Mining", "target": "iron"}, 100), "")
        data["combat_bank_run"] = {"ticks_remaining": 3, "target_id": "citizen"}
        random.seed(20261103)
        self._answer(addon)
        self.assertEqual(addon._state.current_skill, "Mining")
        self.assertGreater(data["inventory"].get("Iron ore", 0), 0)
        self.assertFalse(data["combat_bank_run"])

    def test_a_kill_pays_the_trip_from_the_same_card_and_resets_the_encounter(self):
        addon = self._fight(
            combat_supply_loadout={"food": {"Lobster": 20}},
            carried_inventory={"citizen": {"Bones": 7}},
            combat_encounter={"target_id": "citizen", "enemy_lifepoints": 1},
        )
        data = addon._state.player_data
        data["inventory"]["Bones"] = 7
        random.seed(20261103)
        ctx = addon._runtime_action_context()
        addon._spend_card_on_action(ctx, "combat", addon._registered_answer_handler("Combat"))
        self.assertEqual(ctx.card.combat_ticks_spent, 60)
        self.assertEqual(ctx.card.stop_reason, "")
        self.assertEqual(data["combat_kill_counts"]["citizen"], 1)
        self.assertGreater(data["combat_bank_run"]["ticks_remaining"], 40)
        self.assertEqual(data["combat_encounter"], {})

    def test_travel_countdown_does_not_draw_from_combat_rng(self):
        addon = self._fight(1, agility_level=50)
        random.seed(20261103)
        before = random.getstate()
        for _ in range(2):
            ctx = addon._runtime_action_context()
            addon._spend_card_on_action(ctx, "combat", addon._registered_answer_handler("Combat"))
        self.assertEqual(random.getstate(), before)
        self.assertEqual(addon._state.player_data["combat_bank_run"]["ticks_remaining"], 84)

    def test_weight_and_full_run_energy_credit_keep_the_bank_transaction(self):
        addon = self._fight(
            1, agility_level=99, combat_supply_loadout={"food": {"Lobster": 20}},
            equipment={"weapon": "Rune scimitar", "feet": "Boots of lightness"},
        )
        self.assertTrue(addon.on_request_review_bank_run())
        self.assertEqual(addon._state.player_data["combat_bank_run"]["ticks_remaining"], 92)
        self._answer(addon)
        self.assertEqual(addon._state.player_data["combat_bank_run"]["ticks_remaining"], 86)

        addon._state.player_data.update(combat_bank_run={}, combat_supply_loadout={}, agility_run_energy_credit_pct=100)
        self.assertTrue(addon.on_request_review_bank_run())
        self.assertEqual(addon._state.player_data["combat_bank_run"]["ticks_remaining"], 0)
        self._answer(addon)
        self.assertTrue(addon._state.player_data["combat_supply_loadout"]["food"])
        self.assertLess(addon._state.player_data["inventory"]["Lobster"], 1000)

    def test_old_rest_and_grave_delays_finish_on_the_next_card(self):
        addon = self._fight(
            1, combat_lifepoints=90, combat_rest_reviews=1,
            combat_grave={"items": ["Bronze sword"], "reviews_remaining": 5, "walk_reviews_remaining": 3},
        )
        addon._state.current_skill = "Utilities"
        addon._state.player_data["current_utility"] = "bankstanding"
        self._answer(addon)
        self.assertEqual(addon._state.player_data["combat_lifepoints"], 990)
        self.assertFalse(addon._state.player_data["combat_grave"])
        self.assertEqual(addon._state.player_data["inventory"]["Bronze sword"], 1)
        self.assertNotIn("combat_rest_reviews", addon._state.player_data)

    def test_grave_walk_waits_for_success_and_debt_without_double_charging(self):
        from tests.test_integration_smoke import _FakeReviewer

        addon = self._fight(20, card_tick_debt=30)
        addon._state.current_skill = "Mining"
        data = addon._state.player_data
        data.update(current_ore="iron", mining_level=99, mining_exp=13034431.0,
                    toolbelt={"mining": ["rune_pickaxe"]},
                    combat_grave={"items": ["Bronze sword"], "reviews_remaining": 5,
                                  "walk_ticks_remaining": 300})
        for _ in range(3):
            addon._state.card_turned = addon._state.answer_shown = True
            addon._state.exp_awarded = False
            addon.on_answer_card(_FakeReviewer(), 1, lambda *_: "answered")
            self.assertEqual(data["combat_grave"]["walk_ticks_remaining"], 300)
            self.assertEqual(data["card_tick_debt"], 30)
            self.assertNotIn("Bronze sword", data["inventory"])
        for remaining in (210, 90):
            self._answer(addon)
            self.assertEqual(data["combat_grave"]["walk_ticks_remaining"], remaining)
            self.assertEqual(data.get("card_tick_debt", 0), 0)
            self.assertNotIn("Iron ore", data["inventory"])
        self._answer(addon)
        self.assertFalse(data["combat_grave"])
        self.assertEqual(data["inventory"]["Bronze sword"], 1)
        self.assertGreater(data["inventory"]["Iron ore"], 0)
        self.assertEqual(data.get("card_tick_debt", 0), 0)

    def test_unclaimed_grave_expires_on_again(self):
        from tests.test_integration_smoke import _FakeReviewer

        addon = self._fight(combat_grave={"items": ["Bronze sword"], "reviews_remaining": 2})
        data = addon._state.player_data
        for remaining in (1, 0):
            addon._state.card_turned = addon._state.answer_shown = True
            addon._state.exp_awarded = False
            addon.on_answer_card(_FakeReviewer(), 1, lambda *_: "answered")
            self.assertEqual(data.get("combat_grave", {}).get("reviews_remaining", 0), remaining)
        self.assertNotIn("Bronze sword", data["inventory"])

    def test_queue_segments_share_one_cards_recovery_time(self):
        from ankiscape.core.action_queue import add_to_action_queue

        addon = self._fight(combat_lifepoints=500, combat_rest_ticks_remaining=180,
                            combat_auto_eat_food=[])
        data = addon._state.player_data
        data.update(mining_level=99, mining_exp=13034431.0, toolbelt={"mining": ["rune_pickaxe"]})
        for target, count in (("iron", 1), ("copper", 1), ("iron", 100)):
            self.assertEqual(add_to_action_queue(addon,
                             {"kind": "skill", "skill": "Mining", "target": target}, count), "")
        random.seed(20261104)
        self._answer(addon)
        self.assertEqual(data["combat_rest_ticks_remaining"], 120)
        self.assertEqual(data["combat_lifepoints"], 665)
        self.assertGreater(data["inventory"]["Copper ore"], 0)
        self.assertEqual(len(data["action_queue"]["entries"]), 1)
