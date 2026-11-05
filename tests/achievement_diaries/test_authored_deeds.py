"""The ledger's authored deeds: real triggers, real gates, and durable saves."""

from __future__ import annotations

import copy
import itertools
import json
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.logic import check_achievements
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.achievement_diary_data import ACHIEVEMENT_DIARY_CATALOG
from ankiscape.logic.achievement_diary_logic import (
    claim_diary_tier_pure,
    refresh_achievement_diaries_pure,
    task_progress_pure,
    tier_claim_state_pure,
)
from ankiscape.runtime.runtime_actions import ANSWER_HANDLERS, RuntimeActionContext
from tools.achievement_diary_ledger import (
    AUTHORED_SOURCE_ID_FLOOR,
    CURATION_LEDGER_PATH,
)


def _combat(enemy):
    return {
        "current_combat_target": enemy,
        "strength_level": 99, "attack_level": 99, "defense_level": 99,
        "constitution_level": 99, "combat_lifepoints": 990,
        "combat_encounter": {"target_id": enemy, "enemy_lifepoints": 1},
    }


# What each deed's action needs beyond the row's own access gates. A deed fires
# only through the real answer handler, from a save that holds exactly the
# levels and quests its row shows the player.
_DRIVES = {
    "falador_easy_reach_level_37_strength": ("combat", _combat("guard_sword"), {}),
    "falador_medium_reach_level_60_woodcutting": ("woodcutting", {"current_tree": "yew"}, {"Bronze hatchet": 1}),
    "falador_hard_reach_level_80_mining": ("mining", {"current_ore": "concentrated_coal"}, {"Bronze pickaxe": 1}),
    "falador_elite_reach_level_93_cooking": ("cooking", {"current_cooking": "cook_cavefish"}, {"Raw cavefish": 1}),
    "fremennik_easy_reach_level_35_strength": ("fishing", {"current_fishing": "catch_tuna_swordfish"}, {"Harpoon": 1}),
    "fremennik_easy_reach_level_35_agility": ("thieving", {"current_thieving": "pickpocket_fremennik"}, {}),
    "fremennik_medium_reach_level_52_crafting": ("firemaking", {"current_firemaking": "arctic_pine_logs", "quests": {"the_fremennik_isles": {"started": True}}}, {"Arctic pine logs": 1, "Tinderbox": 1}),
    "fremennik_medium_reach_level_55_fishing": ("fishing", {"current_fishing": "catch_leaping_fish", "unlocked_abilities": ["barbarian_fishing"]}, {"Barbarian rod": 1, "Feather": 1}, (0.99, 0.1)),
    "fremennik_hard_reach_level_65_magic": ("magic", {"current_magic": "superglass_make"}, {"Astral rune": 2, "Air rune": 10, "Fire rune": 6, "Seaweed": 1, "Bucket of sand": 1}),
    "fremennik_hard_reach_level_65_slayer": ("combat", {**_combat("turoth"), "equipment": {"weapon": "Leaf-bladed sword"}}, {}),
    "fremennik_elite_reach_level_55_hunter": ("hunter", {"current_hunter": "catch_sabre_toothed_kebbit"}, {"Logs": 25, "Knife": 1, "Bronze hatchet": 1}),
    "fremennik_elite_reach_level_65_magic": ("magic", {"current_magic": "tan_leather"}, {"Astral rune": 10, "Fire rune": 25, "Body rune": 5, "Cowhide": 25}),
    "fremennik_elite_reach_level_80_herblore": ("herblore", {"current_herblore": "finished_zamorak_mix"}, {"Zamorak brew (2)": 1, "Caviar": 1}),
    "karamja_elite_reach_level_65_fishing": ("fishing", {"current_fishing": "catch_karambwan"}, {"Karambwan vessel": 1, "Raw karambwanji": 28}),
    "seers_easy_reach_level_10_crafting": ("fletching", {"current_fletch": "string_longbow"}, {"Longbow (u)": 1, "Bow string": 1}),
    "seers_easy_reach_level_30_mining": ("mining", {"current_ore": "coal"}, {"Bronze pickaxe": 1}),
    "seers_medium_reach_level_46_fishing": ("fishing", {"current_fishing": "catch_lobsters"}, {"Lobster pot": 1}),
    "seers_medium_reach_level_57_magic": ("magic", {"current_magic": "enchant_diamond_bolts"}, {"Cosmic rune": 1, "Earth rune": 10, "Law rune": 2, "Diamond bolts": 10}),
    "seers_hard_reach_level_65_fletching": ("fletching", {"current_fletch": "tip_diamond_bolts"}, {"Adamant bolts": 10, "Diamond bolt tips": 10}),
    "seers_hard_reach_level_73_smithing": ("smithing", {"current_smith": "forge_adamant_bolts_unf"}, {"Adamant bar": 1, "Hammer": 1}),
    "seers_elite_reach_level_83_magic": ("magic", {"current_magic": "catherby_teleport"}, {"Astral rune": 3, "Law rune": 3, "Water rune": 10}),
    "seers_elite_reach_level_80_fletching": ("fletching", {"current_fletch": "magic_longbow_u"}, {"Magic logs": 1, "Knife": 1}),
}


def _authored_rows():
    rows = map(json.loads, CURATION_LEDGER_PATH.read_text(encoding="utf-8").splitlines())
    return [row for row in rows if row["source_id"] >= AUTHORED_SOURCE_ID_FLOOR]


def _catalog_tasks():
    return {
        task.id: task
        for family in ACHIEVEMENT_DIARY_CATALOG
        for tier in family.tiers
        for task in tier.tasks
    }


def _player(row):
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    for gate in row["access_gates"]:
        if gate["kind"] == "skill_level":
            player[f"{gate['key']}_level"] = gate["amount"]
        else:
            player["quests"][gate["key"]] = {
                "started": True, "progress": 99, "completed": True,
            }
    return player


def _context(player, errors, rolls):
    def award(exp_key, amount):
        player[exp_key] = float(player.get(exp_key, 0.0) or 0.0) + float(amount)
        return amount

    return RuntimeActionContext(
        player_data=player, random_random=itertools.cycle(rolls).__next__,
        show_error_message=lambda title, message: errors.append((title, message)),
        deactivate_current_skill=lambda _reason=None: None, award_skill_exp=award,
        award_hidden_skill_exp=lambda *_args: None, level_up_check=lambda *_args: None,
        check_achievements=check_achievements, save_player_data=lambda: None,
        refresh_skill_availability=lambda: None, show_exp=lambda _amount: None,
        show_activity_gain=lambda _message: None, implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda _before: None,
    )


def _review(player, row, reviews, errors):
    handler, state, inventory, *rolls = _DRIVES[row["task_id"]]
    state = copy.deepcopy(state)
    player["quests"].update(state.pop("quests", {}))
    player.update(state)
    player["inventory"].update(inventory)
    for _review_number in range(reviews):
        if handler == "combat":
            player["combat_encounter"]["enemy_lifepoints"] = 1
        ANSWER_HANDLERS[handler](_context(player, errors, *(rolls or ((0.1,),))))


class AuthoredDeedCensusTest(unittest.TestCase):
    def test_no_catalog_row_is_a_bare_level_milestone(self):
        for task in _catalog_tasks().values():
            with self.subTest(task=task.id):
                kinds = {
                    condition.kind
                    for root in task.conditions
                    for condition in (root, *root.alternatives)
                }
                self.assertNotIn("skill_level", kinds)
                self.assertNotRegex(task.name, r"(?i)^reach level")

    def test_every_authored_row_is_a_live_deed_with_a_drive(self):
        rows = _authored_rows()
        tasks = _catalog_tasks()
        self.assertEqual({row["task_id"] for row in rows}, set(_DRIVES))
        self.assertEqual(len(rows), 22)
        for row in rows:
            with self.subTest(task=row["task_id"]):
                self.assertIn(row["disposition"], {"translated", "invented"})
                self.assertFalse(tasks[row["task_id"]].dormant)


class AuthoredDeedTriggerTest(unittest.TestCase):
    def setUp(self):
        popups = patch("ankiscape.core.logic._popups_enabled", return_value=False)
        popups.start()
        self.addCleanup(popups.stop)

    def test_each_deed_fires_through_its_real_handler_at_its_shown_gates(self):
        for row in _authored_rows():
            with self.subTest(task=row["task_id"]):
                player = _player(row)
                errors = []
                _review(player, row, row["wiring"][0]["amount"], errors)
                self.assertEqual(errors, [])
                self.assertIn(
                    row["task_id"], player["achievement_diaries"]["completed_tasks"]
                )

    def test_one_level_below_the_first_gate_the_deed_makes_no_progress(self):
        tasks = _catalog_tasks()
        for row in _authored_rows():
            if not row["access_gates"]:
                continue
            with self.subTest(task=row["task_id"]):
                player = _player(row)
                gate = row["access_gates"][0]
                player[f"{gate['key']}_level"] = gate["amount"] - 1
                _review(player, row, 1, [])
                self.assertFalse(task_progress_pure(player, tasks[row["task_id"]])[0])
                self.assertEqual(
                    task_progress_pure(player, tasks[row["task_id"]])[1], 0
                )


class AuthoredDeedSaveTest(unittest.TestCase):
    def test_a_save_that_completed_a_former_milestone_keeps_its_claimable_tier(self):
        family = next(f for f in ACHIEVEMENT_DIARY_CATALOG if f.id == "falador")
        tier = family.tiers[0]
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        completed = [task.id for task in tier.tasks]
        self.assertIn("falador_easy_reach_level_37_strength", completed)
        player["achievement_diaries"]["completed_tasks"] = completed

        player, newly = refresh_achievement_diaries_pure(player)

        self.assertEqual(newly, ())
        self.assertEqual(player["achievement_diaries"]["completed_tasks"], completed)
        state = tier_claim_state_pure(player, family, tier)
        self.assertEqual((state["done"], state["total"]), (12, 12))
        self.assertEqual(state["status"], "Ready to Claim")
        player, ok, _info = claim_diary_tier_pure(player, tier.id)
        self.assertTrue(ok)
        self.assertIn(tier.id, player["achievement_diaries"]["claimed_tiers"])


if __name__ == "__main__":
    unittest.main()
