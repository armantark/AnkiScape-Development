import sys
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, QUEST_DATA
from ankiscape.data.cabin_fever_data import (
    CABIN_FEVER_STAGE_SOURCE,
    CABIN_FEVER_UNLOCKS,
)
from ankiscape.data.quest_data import QUEST_STAGE_REQUIREMENT_CLEANUPS_BY_ID
from ankiscape.data.slayer_data import CHAELDAR_FAMILIES_BY_ID
from ankiscape.logic.slayer_logic import slayer_family_locked_reasons_pure
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_progress_pure,
    quest_locked_reasons_pure,
    start_quest_pure,
)
from tests.quest_action_proof_helpers import quest_action_proofs_for_quest
from tests.test_combat_quest_gate import _answer_review, _maxed_player_for_quest
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package


QUEST_ID = "cabin_fever"
STAGE_CLEANUPS = QUEST_STAGE_REQUIREMENT_CLEANUPS_BY_ID[QUEST_ID]
# Stage 1 preserves its existing route pin. Stages 2-4 are literal oracles from /Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/evidence/static/cabin-fever-target-contract.json, quest_route.enemy_cannon through completion.
STAGE_ACTIONS = (
    "Reach the Port Phasmatys charter route",
    "Swing between the ships, consuming one quest rope per swing, disable the enemy cannon with one fuse and a retained tinderbox, then repair exactly three hull holes with two repair planks, ten tacks, and one swamp paste each",
    "Steal exactly ten plunder from the enemy hold and store it once aboard The Adventurous",
    "Repair the broken cannon with one barrel, load every shot in gunpowder-ramrod-payload-fuse order, then score one canister hit and three cannonball hits with the retained tinderbox, cleaning between shots",
)


def _cabin_fever_player() -> dict:
    player = _maxed_player_for_quest(QUEST_ID)
    player["inventory"].update({"Coins": 3500, "Tinderbox": 1})
    return player


def _inventory_delta(before: dict, after: dict) -> dict:
    return {
        item: after.get(item, 0) - before.get(item, 0)
        for item in before.keys() | after.keys()
        if after.get(item, 0) != before.get(item, 0)
    }


class TestCabinFeverStageContract(unittest.TestCase):
    def test_three_stage_sentinels_are_replaced_by_the_frozen_route(self):
        quest = QUEST_DATA[QUEST_ID]
        stage_rows = quest["stage_requirements"]
        self.assertEqual(len(stage_rows), 4)
        rows = {row["stage"]: row for row in stage_rows}
        self.assertEqual(set(rows), set(range(1, 5)))
        self.assertEqual(
            tuple(rows[stage]["required_actions"] for stage in range(1, 5)),
            ((), (), (), ()),
        )
        self.assertEqual(
            tuple(rows[stage]["auto_actions"][0] for stage in range(1, 5)),
            STAGE_ACTIONS,
        )
        self.assertEqual(
            tuple(
                cleanup.remove_required_actions
                for cleanup in STAGE_CLEANUPS
                if cleanup.stage in (2, 3, 4)
            ),
            tuple(
                (f"Complete Cabin Fever stage {stage} objective",)
                for stage in range(2, 5)
            ),
        )
        self.assertEqual(
            {rows[stage]["source"] for stage in range(1, 5)},
            {CABIN_FEVER_STAGE_SOURCE},
        )
        self.assertEqual(
            tuple(rows[stage]["combat_encounters"] for stage in range(1, 5)),
            ((), (), (), ()),
        )
        self.assertEqual(
            tuple(rows[stage]["required_inventory"] for stage in range(2, 5)),
            ({}, {}, {}),
        )
        self.assertEqual(
            tuple(rows[stage]["required_tools"] for stage in range(2, 5)),
            ({}, {}, {}),
        )

        self.assertEqual(
            tuple(
                (requirement["quest_id"], requirement["display_name"])
                for requirement in quest["required_quests"]
            ),
            (("pirates_treasure", "Pirate's Treasure"), ("rum_deal", "Rum Deal")),
        )
        self.assertEqual(
            tuple(
                (requirement["skill_id"], requirement["level"])
                for requirement in quest["required_skills"]
            ),
            (("agility", 42), ("crafting", 45), ("ranged", 40), ("smithing", 50)),
        )
        self.assertEqual(quest["point_reward"], 2)
        self.assertEqual(
            quest["xp_rewards"],
            (
                {"skill_id": "agility", "amount": 7000.0},
                {"skill_id": "crafting", "amount": 7000.0},
                {"skill_id": "smithing", "amount": 7000.0},
            ),
        )
        self.assertEqual(quest["rewards"], {"Book o' piracy": 1})
        self.assertEqual(quest["unlocks"], CABIN_FEVER_UNLOCKS)
        registered_items = {definition.storage_key for definition in ITEM_DEFINITIONS}
        self.assertIn("Book o' piracy", registered_items)

    def test_completion_unlocks_fever_spider_assignments(self):
        family = CHAELDAR_FAMILIES_BY_ID["fever_spiders"]
        player = {"slayer_level": 99, "quests": {}}
        self.assertEqual(
            slayer_family_locked_reasons_pure(player, family),
            ("Complete Cabin Fever",),
        )
        player["quests"][QUEST_ID] = {"completed": True}
        self.assertEqual(slayer_family_locked_reasons_pure(player, family), ())


class TestCabinFeverPureFlow(unittest.TestCase):
    def test_skill_gates_and_source_backed_stages_lead_to_completion(self):
        low_player = _cabin_fever_player()
        low_player["agility_level"] = 41
        self.assertEqual(
            quest_locked_reasons_pure(low_player, QUEST_ID, QUEST_DATA),
            ("Agility 42",),
        )

        player = _cabin_fever_player()
        before_inventory = dict(player["inventory"])
        player, started = start_quest_pure(player, QUEST_ID, QUEST_DATA)
        self.assertTrue(started)

        for expected_progress in range(2, 5):
            player, progressed, completed = apply_quest_progress_pure(
                player,
                QUEST_ID,
                QUEST_DATA,
            )
            self.assertTrue(progressed)
            self.assertFalse(completed)
            self.assertEqual(player["quests"][QUEST_ID]["progress"], expected_progress)
            self.assertEqual(
                quest_action_proofs_for_quest(player, QUEST_ID, QUEST_DATA),
                STAGE_ACTIONS[: expected_progress - 1],
            )

        player, progressed, completed = apply_quest_progress_pure(
            player,
            QUEST_ID,
            QUEST_DATA,
        )
        self.assertTrue(progressed)
        self.assertTrue(completed)
        self.assertTrue(player["quests"][QUEST_ID]["completed"])
        self.assertEqual(player["quests"][QUEST_ID]["progress"], 5)
        self.assertEqual(
            quest_action_proofs_for_quest(player, QUEST_ID, QUEST_DATA),
            STAGE_ACTIONS,
        )
        self.assertEqual(_inventory_delta(before_inventory, player["inventory"]), {"Book o' piracy": 1})
        self.assertEqual(player["quest_points"], 1002)
        self.assertEqual(player["agility_exp"], 7000.0)
        self.assertEqual(player["crafting_exp"], 7000.0)
        self.assertEqual(player["smithing_exp"], 7000.0)


class TestCabinFeverProductFlow(unittest.TestCase):
    def setUp(self) -> None:
        self._original_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._original_modules)

    def test_successful_review_answers_complete_the_loaded_quest(self):
        addon = _load_addon_as_package("ankiscape_cabin_fever_e2e")
        stage_rows = addon.QUEST_DATA[QUEST_ID]["stage_requirements"]
        self.assertEqual(len(stage_rows), 4)
        self.assertEqual({row["stage"] for row in stage_rows}, set(range(1, 5)))

        calls = {"gains": [], "dialogs": [], "saves": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__(
            "saves",
            calls["saves"] + 1,
        )
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda text: calls["gains"].append(text)
        addon._show_exp = lambda _amount: None
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: calls["dialogs"].append(
            (title, message)
        )
        addon.player_data = _cabin_fever_player()
        before_inventory = dict(addon.player_data["inventory"])
        addon.current_skill = "Quests"
        addon._REVIEW_UNDO_STACK.clear()

        self.assertTrue(addon.on_set_quest(QUEST_ID), calls["dialogs"])
        for review_count in range(1, 11):
            _answer_review(addon)
            if addon.player_data["quests"][QUEST_ID]["completed"]:
                break
        else:
            self.fail("Cabin Fever did not complete within 10 reviews")

        self.assertTrue(addon.player_data["quests"][QUEST_ID]["completed"])
        self.assertEqual(
            quest_action_proofs_for_quest(
                addon.player_data,
                QUEST_ID,
                addon.QUEST_DATA,
            ),
            STAGE_ACTIONS,
        )
        self.assertEqual(
            _inventory_delta(before_inventory, addon.player_data["inventory"]),
            {"Book o' piracy": 1},
        )
        self.assertEqual(addon.player_data["quest_points"], 1002)
        self.assertEqual(addon.player_data["agility_exp"], 7000.0)
        self.assertEqual(addon.player_data["crafting_exp"], 7000.0)
        self.assertEqual(addon.player_data["smithing_exp"], 7000.0)
        self.assertEqual(addon.current_skill, "Utilities")
        self.assertEqual(calls["gains"][-1], "Cabin Fever complete")
        self.assertEqual(calls["dialogs"][-1][0], "Quest complete")
        self.assertIn("Cabin Fever is complete", calls["dialogs"][-1][1])
        self.assertGreaterEqual(calls["saves"], review_count)


if __name__ == "__main__":
    unittest.main()
