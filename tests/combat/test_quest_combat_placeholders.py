import random
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import EQUIPMENT_DATA, QUEST_DATA
from ankiscape.logic_pure.logic_pure import (
    equip_item_pure,
    quest_current_stage_resolvable_combat_blockers_pure,
)
from ankiscape.runtime.runtime_actions import handle_quest_answer
from tests.test_combat_quest_gate import _maxed_player_for_quest
from tests.test_runtime_actions import _context
from tools.combat.quest_stat_sources import reviewed_sources


class TestQuestCombatPlaceholders(unittest.TestCase):
    def test_a_placeholder_row_cannot_feed_the_catalog_builder(self):
        """A payload here becomes unmarked generated stats on the next build.

        `matching_quest_stats` returns a reviewed row's payload straight to
        `parse_combat_encounters`, which writes it into the generated catalog
        with no `PLACEHOLDER(...)` marker. The marked replacement is the only
        home these values may have, so an admitted row carries no payload.

        The key is `placeholder_admission`, not the status string: a row renamed
        out of `registered_placeholder` while it still borrows Darkan fields
        would otherwise reopen the unmarked path unseen.
        """
        admitted = {
            key: row for key, row in reviewed_sources().items()
            if "placeholder_admission" in row
        }
        self.assertTrue(admitted, "no row carries an admission, so this guard proves nothing")

        with_payload = sorted(key for key, row in admitted.items() if "payload" in row)
        self.assertEqual(with_payload, [])

    def test_othanian_resumes_through_reviews_to_a_recorded_win(self):
        quest_id = "underground_pass"
        encounter_id = "underground_pass_othanian_91"
        player = _maxed_player_for_quest(quest_id)
        player.update(current_quest=quest_id, combat_lifepoints=990)
        player["quests"][quest_id] = {"started": True, "progress": 6, "completed": False}
        prior_kills = [f"underground_pass_{suffix}" for suffix in (
            "kalrag_89", "sir_harry_62", "sir_jerro_62", "sir_carl_62", "doomion_91",
        )]
        player["quest_combat_encounters"] = {quest_id: list(prior_kills)}
        calls = {"xp": [], "saves": 0, "errors": []}
        rng = random.Random(9)
        ctx = _context(player, calls, random_values=(rng.random() for _ in range(10000)))
        ctx.cadence_live_enabled = True

        self.assertTrue(handle_quest_answer(ctx))
        remaining = player.get("quest_combat_active_encounters", {}).get(quest_id, {}).get(encounter_id)
        self.assertIsNotNone(remaining, calls["errors"])
        self.assertGreater(remaining, 0)
        self.assertLess(remaining, 900)
        for _ in range(100):
            if encounter_id in player["quest_combat_encounters"][quest_id]:
                break
            self.assertTrue(handle_quest_answer(ctx))
        self.assertIn(encounter_id, player["quest_combat_encounters"][quest_id])
        self.assertTrue(set(prior_kills) <= set(player["quest_combat_encounters"][quest_id]))
        self.assertEqual(calls["activity"][-1], "Defeated Othanian")
        self.assertFalse(calls["errors"])

    def test_solus_with_zero_hidden_levels_resolves_to_a_recorded_win(self):
        """Solus carries attack, strength and defence 0 and lives on its max hit.

        Othanian cannot cover this: its hidden levels are positive, so it takes
        the ordinary branch of `quest_combat_encounter_has_stats_pure`. Solus
        passes only through the all-zero branch, which needs a positive max hit,
        and then fights on the levels the enemy spec raises from 0 to 1. If the
        qualified max hit 40 were lost, the stage would report the fight as not
        modelled and Wanted! stage 5 would become an unfinishable row.
        """
        quest_id = "wanted"
        encounter_id = "wanted_solus_dellagar_2"
        player = _maxed_player_for_quest(quest_id)
        player.update(current_quest=quest_id, combat_lifepoints=990)
        player["inventory"]["Lit torch"] = 1
        player["quests"][quest_id] = {"started": True, "progress": 5, "completed": False}
        player["quest_combat_encounters"] = {quest_id: ["wanted_black_knight_34"]}
        calls = {"xp": [], "saves": 0, "errors": []}
        rng = random.Random(17)
        ctx = _context(player, calls, random_values=(rng.random() for _ in range(10000)))
        ctx.cadence_live_enabled = True

        offered = quest_current_stage_resolvable_combat_blockers_pure(player, quest_id, QUEST_DATA)
        self.assertEqual(tuple(blocker["encounter_id"] for blocker in offered), (encounter_id,))

        for _ in range(100):
            self.assertTrue(handle_quest_answer(ctx), calls["errors"])
            if encounter_id in player["quest_combat_encounters"][quest_id]:
                break
        self.assertIn(encounter_id, player["quest_combat_encounters"][quest_id])
        self.assertIn("wanted_black_knight_34", player["quest_combat_encounters"][quest_id])
        self.assertEqual(calls["activity"][-1], "Defeated Solus Dellagar")
        self.assertFalse(calls["errors"])

    def test_sir_leye_with_zero_hidden_levels_resumes_to_a_recorded_win(self):
        quest_id = "recruitment_drive"
        encounter_id = "recruitment_drive_sir_leye_20"
        player = _maxed_player_for_quest(quest_id)
        player.update(current_quest=quest_id, combat_lifepoints=990)
        player["quests"][quest_id] = {"started": True, "progress": 4, "completed": False}
        calls = {"xp": [], "saves": 0, "errors": []}
        rng = random.Random(9)
        ctx = _context(player, calls, random_values=(rng.random() for _ in range(10000)))
        ctx.cadence_live_enabled = True

        offered = quest_current_stage_resolvable_combat_blockers_pure(player, quest_id, QUEST_DATA)
        self.assertEqual(tuple(blocker["encounter_id"] for blocker in offered), (encounter_id,))
        requirement = next(row for row in QUEST_DATA[quest_id]["stage_requirements"] if row["stage"] == 4)
        stats = requirement["combat_encounters"][0]["npc_stats"]
        self.assertEqual(tuple(stats[key] for key in ("attack", "strength", "defence", "magic", "ranged")), (0,) * 5)
        self.assertEqual(player["equipment"], {})

        self.assertTrue(handle_quest_answer(ctx), calls["errors"])
        remaining = player["quest_combat_active_encounters"][quest_id][encounter_id]
        self.assertGreater(remaining, 0)
        self.assertLess(remaining, stats["hitpoints"])
        self.assertEqual(calls["saves"], 1)
        self.assertIn(f"{remaining} LP left", calls["activity"][-1])
        for _ in range(100):
            self.assertTrue(handle_quest_answer(ctx), calls["errors"])
            result = player["combat_last_result"]
            self.assertEqual(result["enemy_lifepoints"], max(0, remaining - result["player_damage"]))
            self.assertFalse(result["died"])
            if result["killed"]:
                break
            remaining = player["quest_combat_active_encounters"][quest_id][encounter_id]
        self.assertEqual(player["quest_combat_encounters"][quest_id], [encounter_id])
        self.assertEqual(player["quest_combat_encounter_counts"][quest_id][encounter_id], 1)
        self.assertNotIn(encounter_id, player["quest_combat_active_encounters"].get(quest_id, {}))
        self.assertEqual(player["quests"][quest_id]["progress"], 4)
        self.assertEqual(calls["activity"][-1], "Defeated Sir Leye")
        self.assertEqual(calls["saves"], len(calls["activity"]))
        self.assertFalse(calls["errors"])

    def test_the_illusive_preserves_prior_wins_and_resumes_to_a_recorded_win(self):
        quest_id = "dream_mentor"
        encounter_id = "dream_mentor_the_illusive_108"
        player = _maxed_player_for_quest(quest_id)
        player.update(current_quest=quest_id, combat_lifepoints=990)
        player["quests"][quest_id] = {"started": True, "progress": 4, "completed": False}
        prior_kills = [f"dream_mentor_{suffix}" for suffix in (
            "the_inadequacy_343", "the_everlasting_223", "the_untouchable_274",
        )]
        player["quest_combat_encounters"] = {quest_id: list(prior_kills)}
        calls = {"xp": [], "saves": 0, "errors": []}
        rng = random.Random(17)
        ctx = _context(player, calls, random_values=(rng.random() for _ in range(10000)))
        ctx.cadence_live_enabled = True

        offered = quest_current_stage_resolvable_combat_blockers_pure(player, quest_id, QUEST_DATA)
        self.assertEqual(tuple(blocker["encounter_id"] for blocker in offered), (encounter_id,))
        self.assertTrue(handle_quest_answer(ctx), calls["errors"])
        remaining = player["quest_combat_active_encounters"][quest_id][encounter_id]
        self.assertGreater(remaining, 0)
        self.assertLess(remaining, 1400)
        self.assertEqual(calls["saves"], 1)
        self.assertIn(f"{remaining} LP left", calls["activity"][-1])
        for _ in range(100):
            self.assertTrue(handle_quest_answer(ctx), calls["errors"])
            result = player["combat_last_result"]
            self.assertEqual(result["enemy_lifepoints"], max(0, remaining - result["player_damage"]))
            self.assertFalse(result["died"])
            self.assertTrue(set(prior_kills) <= set(player["quest_combat_encounters"][quest_id]))
            if result["killed"]:
                break
            remaining = player["quest_combat_active_encounters"][quest_id][encounter_id]
        self.assertCountEqual(player["quest_combat_encounters"][quest_id], [*prior_kills, encounter_id])
        self.assertEqual(player["quest_combat_encounter_counts"][quest_id][encounter_id], 1)
        self.assertNotIn(encounter_id, player["quest_combat_active_encounters"].get(quest_id, {}))
        self.assertEqual(player["quests"][quest_id]["progress"], 4)
        self.assertEqual(calls["activity"][-1], "Defeated The Illusive")
        self.assertEqual(calls["saves"], len(calls["activity"]))
        self.assertFalse(calls["errors"])

    def test_ice_troll_group_records_all_ten_kills_before_completion(self):
        quest_id = "the_fremennik_isles"
        encounter_id = "the_fremennik_isles_ice_troll_82"
        king_id = "the_fremennik_isles_ice_troll_king_122"
        player = _maxed_player_for_quest(quest_id)
        player.update(current_quest=quest_id, combat_lifepoints=990)
        player["quests"][quest_id] = {"started": True, "progress": 5, "completed": False}
        for item_name in ("Rune scimitar", "Rune chainbody"):
            player["inventory"][item_name] = 1
            inventory, equipment, ok = equip_item_pure(
                item_name, player["inventory"], player["equipment"], EQUIPMENT_DATA
            )
            self.assertTrue(ok)
            player.update(inventory=inventory, equipment=equipment)
        player["combat_supply_loadout"] = {"food": {"Shark": 28}}
        calls = {"xp": [], "saves": 0, "errors": []}
        rng = random.Random(9)
        ctx = _context(player, calls, random_values=(rng.random() for _ in range(10000)))
        ctx.cadence_live_enabled = True

        offered = quest_current_stage_resolvable_combat_blockers_pure(player, quest_id, QUEST_DATA)
        self.assertEqual(tuple(blocker["encounter_id"] for blocker in offered), (encounter_id, king_id))
        self.assertEqual(offered[0]["remaining_quantity"], 10)
        self.assertTrue(handle_quest_answer(ctx), calls["errors"])
        remaining = player["quest_combat_active_encounters"][quest_id][encounter_id]
        self.assertGreater(remaining, 0)
        self.assertLess(remaining, 800)
        self.assertIn(f"{remaining} LP left", calls["activity"][-1])
        kills = 0
        for _ in range(300):
            self.assertTrue(handle_quest_answer(ctx), calls["errors"])
            result = player["combat_last_result"]
            self.assertEqual(result["encounter_id"], encounter_id)
            self.assertEqual(result["enemy_lifepoints"], max(0, remaining - result["player_damage"]))
            self.assertFalse(result["died"])
            if result["killed"]:
                kills += 1
                self.assertEqual(player["quest_combat_encounter_counts"][quest_id][encounter_id], kills)
                self.assertEqual(result["remaining_quantity"], 10 - kills)
                self.assertEqual(result["quest_combat_completed"], kills == 10)
                self.assertEqual(calls["activity"][-1], "Defeated Ice troll")
                remaining = 800
            else:
                remaining = player["quest_combat_active_encounters"][quest_id][encounter_id]
            self.assertEqual(player["quests"][quest_id]["progress"], 5)
            completed = player["quest_combat_encounters"].get(quest_id, [])
            self.assertEqual(encounter_id in completed, kills == 10)
            self.assertNotIn(king_id, completed)
            if kills == 10:
                break
            offered = quest_current_stage_resolvable_combat_blockers_pure(player, quest_id, QUEST_DATA)
            self.assertEqual(offered[0]["encounter_id"], encounter_id)
            self.assertEqual(offered[0]["remaining_quantity"], 10 - kills)
        self.assertEqual(kills, 10)
        self.assertEqual(calls["activity"].count("Defeated Ice troll"), 10)
        self.assertNotIn(encounter_id, player["quest_combat_active_encounters"].get(quest_id, {}))
        self.assertEqual(calls["saves"], len(calls["activity"]))
        self.assertFalse(calls["errors"])
