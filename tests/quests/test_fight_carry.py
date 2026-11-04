"""A quest card can spend its remaining ticks only on consecutive fights."""

import random

from tests.integration_smoke.fixtures import ReviewedProfile
from tests.quests.test_witchs_house import player_at
from ankiscape.data.quest.witchs_house import EXPERIMENTS


class QuestFightCarryTests(ReviewedProfile):
    def _quest(self, quest_id="witchs_house", stage=12, **fields):
        addon = self._addon("ankiscape_quest_fight_carry")
        addon.mw.col.set_config("ankiscape_review_action_multiplier", 10)
        player = player_at(stage)
        player.update(
            current_quest=quest_id,
            quests={quest_id: dict(started=True, progress=stage, completed=False)},
            attack_level=60, strength_level=60, defense_level=60,
            constitution_level=60, combat_lifepoints=600,
            equipment={"weapon": "Rune scimitar"}, combat_prayers_enabled=False,
            combat_auto_eat_food=["Lobster"],
            combat_supply_loadout={"food": {"Lobster": 14}},
        )
        player.update(fields)
        self._new_save(addon, **player)
        addon._state.current_skill = "Quests"
        random.seed(20261104)
        return addon

    def test_witchs_house_kill_spends_the_rest_on_the_next_form(self):
        first, second = (row[0] for row in EXPERIMENTS[:2])
        addon = self._quest(quest_combat_active_encounters={"witchs_house": {first: 1}})
        self._answer(addon)
        data = addon._state.player_data
        self.assertIn(first, data["quest_combat_encounters"]["witchs_house"])
        self.assertLess(data["quest_combat_active_encounters"]["witchs_house"][second], 1225)
        self.assertEqual(data["quests"]["witchs_house"]["progress"], 12)
        self.assertEqual(self.errors, [])

    def test_final_form_leaves_ball_pickup_for_another_card(self):
        addon = self._quest(
            quest_combat_encounters={"witchs_house": [row[0] for row in EXPERIMENTS[:3]]},
            quest_combat_active_encounters={"witchs_house": {EXPERIMENTS[3][0]: 1}},
        )
        self._answer(addon)
        data = addon._state.player_data
        self.assertEqual(len(data["quest_combat_encounters"]["witchs_house"]), 4)
        self.assertEqual(data["quests"]["witchs_house"]["progress"], 12)
        self.assertEqual(data["inventory"].get("Ball", 0), 0)

    def test_a_stage_with_item_work_waits_for_its_own_card(self):
        encounter = "tree_gnome_village_khazard_commander_48"
        addon = self._quest(
            "tree_gnome_village", 5,
            quest_combat_encounter_counts={"tree_gnome_village": {encounter: 1}},
            quest_combat_active_encounters={"tree_gnome_village": {encounter: 1}},
        )
        self._answer(addon)
        data = addon._state.player_data
        self.assertEqual(data["quest_combat_encounter_counts"]["tree_gnome_village"][encounter], 2)
        self.assertEqual(data["quests"]["tree_gnome_village"]["progress"], 5)
        self.assertEqual(data["inventory"].get("Orb of protection", 0), 0)

    def test_consecutive_fights_share_one_tick_budget(self):
        addon = self._quest(quest_combat_active_encounters={"witchs_house": {EXPERIMENTS[0][0]: 1}})
        ctx = addon._runtime_action_context()
        addon._spend_card_on_action(ctx, "quest", addon._registered_answer_handler("Quests"))
        self.assertEqual(ctx.card.combat_ticks_spent, 60)
        self.assertEqual(ctx.card.ticks_remaining, 0)
        self.assertEqual(ctx.card.stop_reason, "")

    def test_fight_only_stage_advances_to_the_next_fight_inside_the_card(self):
        first = "lair_of_tarn_razorlor_mutant_tarn"
        second = "lair_of_tarn_razorlor_tarn_ghost"
        addon = self._quest(
            "lair_of_tarn_razorlor", 5, slayer_level=99,
            quest_combat_active_encounters={"lair_of_tarn_razorlor": {first: 1}},
        )
        self._answer(addon)
        data = addon._state.player_data
        self.assertEqual(data["quests"]["lair_of_tarn_razorlor"]["progress"], 6)
        self.assertEqual(data["combat_last_result"]["encounter_id"], second)
        self.assertGreater(data["combat_last_result"]["player_damage"], 0)
        self.assertEqual(self.errors, [])

    def test_last_tick_kill_advances_a_fight_only_stage_without_an_extra_card(self):
        first = "lair_of_tarn_razorlor_mutant_tarn"
        addon = self._quest(
            "lair_of_tarn_razorlor", 5, slayer_level=99,
            quest_combat_active_encounters={"lair_of_tarn_razorlor": {first: 1}},
        )
        ctx = addon._runtime_action_context()
        ctx.card.ticks_remaining = 1
        addon._spend_card_on_action(ctx, "quest", addon._registered_answer_handler("Quests"))
        data = addon._state.player_data
        self.assertEqual(data["quests"]["lair_of_tarn_razorlor"]["progress"], 6)
        self.assertEqual(data["combat_last_result"]["encounter_id"], first)
        self.assertEqual(ctx.card.combat_ticks_spent, 1)

    def test_empty_prayer_on_a_kill_ends_the_card_before_the_next_form(self):
        first, second = (row[0] for row in EXPERIMENTS[:2])
        addon = self._quest(
            prayer_level=99, combat_prayer_points=1, combat_prayers_enabled=True,
            combat_selected_prayers=["thick_skin"], combat_prayer_uptime="100", combat_prayer_drain_counter=59.0,
            quest_combat_active_encounters={"witchs_house": {first: 1}},
        )
        self._answer(addon)
        data = addon._state.player_data
        self.assertEqual(data["combat_prayer_points"], 0)
        self.assertEqual(data["combat_last_result"]["encounter_id"], first)
        self.assertNotIn(second, data["quest_combat_active_encounters"].get("witchs_house", {}))
        self.assertNotIn(second, data["quest_combat_encounters"].get("witchs_house", []))

    def test_legacy_cadence_keeps_the_first_kill_boundary(self):
        first, second = (row[0] for row in EXPERIMENTS[:2])
        addon = self._quest(quest_combat_active_encounters={"witchs_house": {first: 1}})
        addon.mw.col.set_config("ankiscape_cadence_kernel", False)
        self._answer(addon)
        data = addon._state.player_data
        self.assertIn(first, data["quest_combat_encounters"]["witchs_house"])
        self.assertNotIn(second, data["quest_combat_active_encounters"].get("witchs_house", {}))
