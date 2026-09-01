import sys
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.quest_data import (
    THE_LOST_TRIBE_STAGE_ACTION_SOURCE,
    THE_LOST_TRIBE_WIKI_SOURCE,
)
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_progress_pure,
    quest_current_stage_blocker_reasons_pure,
    start_quest_pure,
)
from tests.quest_action_proof_helpers import quest_action_proofs_for_quest
from tests.test_integration_smoke import (
    _FakeReviewer,
    _install_runtime_fakes,
    _load_addon_as_package,
)


QUEST_ID = "the_lost_tribe"
STAGE_ACTIONS = (
    "Mine the Lumbridge cellar rubble and squeeze through the resulting hole",
    "Find the stone brooch, show it to Duke Horacio and Sigmund, ask Reldo about it, then recover the Goblin symbol book",
    "Read the Goblin symbol book and question the two generals in Goblin Village about the Dorgeshuun",
    "Translate the tunnel symbols, follow the safe route, and perform Goblin Bow before Mistag, then follow him back to Lumbridge",
    "Pickpocket Sigmund's key, search his chest, recover the castle silverware, receive Duke Horacio's peace treaty, follow Kazgar, deliver the treaty to Mistag, and witness its signing",
)


def _ready_lost_tribe_player(thieving_level):
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    for prerequisite_id in ("goblin_diplomacy", "rune_mysteries"):
        prerequisite = QUEST_DATA[prerequisite_id]
        player["quests"][prerequisite_id] = {
            "started": True,
            "progress": prerequisite["stages"],
            "completed": True,
        }
    player.update(
        agility_level=13,
        mining_level=17,
        thieving_level=thieving_level,
    )
    player["inventory"]["Lit candle"] = 1
    player["toolbelt"]["mining"] = [1265]
    player, started = start_quest_pure(player, QUEST_ID, QUEST_DATA)
    if not started:
        raise AssertionError("The Lost Tribe fixture could not start the quest")
    return player


class TestLostTribeStageContract(unittest.TestCase):
    def test_all_live_stage_requirements_replace_generated_sentinels(self):
        rows = {
            row["stage"]: row
            for row in QUEST_DATA[QUEST_ID]["stage_requirements"]
        }

        self.assertEqual(set(rows), {1, 2, 3, 4, 5})
        self.assertEqual(
            tuple(rows[stage]["required_actions"] for stage in range(1, 6)),
            ((), (), (), (), ()),
        )
        self.assertEqual(
            tuple(rows[stage]["auto_actions"][0] for stage in range(1, 6)),
            STAGE_ACTIONS,
        )
        self.assertEqual(rows[1]["source"], THE_LOST_TRIBE_WIKI_SOURCE)
        self.assertEqual(
            {rows[stage]["source"] for stage in range(2, 6)},
            {THE_LOST_TRIBE_STAGE_ACTION_SOURCE},
        )
        self.assertEqual(
            rows[5]["required_skills"],
            ({"skill_id": "thieving", "display_name": "Thieving", "level": 13},),
        )

    def test_pure_quest_flow_reaches_and_enforces_the_thieving_gate(self):
        player = _ready_lost_tribe_player(thieving_level=12)

        for expected_progress in (2, 3, 4, 5):
            player, progressed, completed = apply_quest_progress_pure(
                player,
                QUEST_ID,
                QUEST_DATA,
            )
            self.assertTrue(progressed)
            self.assertFalse(completed)
            self.assertEqual(
                player["quests"][QUEST_ID]["progress"],
                expected_progress,
            )

        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(
                player,
                QUEST_ID,
                QUEST_DATA,
            ),
            ("Thieving 13",),
        )
        blocked, progressed, completed = apply_quest_progress_pure(
            player,
            QUEST_ID,
            QUEST_DATA,
        )
        self.assertFalse(progressed)
        self.assertFalse(completed)
        self.assertEqual(blocked, player)

        player["thieving_level"] = 13
        player, progressed, completed = apply_quest_progress_pure(
            player,
            QUEST_ID,
            QUEST_DATA,
        )

        self.assertTrue(progressed)
        self.assertTrue(completed)
        self.assertTrue(player["quests"][QUEST_ID]["completed"])
        self.assertEqual(player["quests"][QUEST_ID]["progress"], 6)
        self.assertEqual(quest_action_proofs_for_quest(player, QUEST_ID, QUEST_DATA), STAGE_ACTIONS)
        self.assertEqual(player["quest_points"], 1)
        self.assertEqual(player["mining_exp"], 3000.0)
        self.assertEqual(player["inventory"]["Ring of life"], 1)


class TestLostTribeProductFlow(unittest.TestCase):
    def setUp(self):
        self._original_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._original_modules)

    def test_successful_review_answers_complete_the_quest(self):
        addon = _load_addon_as_package("ankiscape_lost_tribe_e2e")
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
        addon.player_data = _ready_lost_tribe_player(thieving_level=13)
        addon.current_skill = "Quests"
        addon._REVIEW_UNDO_STACK.clear()

        for _review in range(5):
            addon.card_turned = True
            addon.answer_shown = True
            addon.exp_awarded = False
            addon.on_answer_card(
                _FakeReviewer(),
                4,
                lambda _self, _ease: "answered",
            )

        self.assertTrue(addon.player_data["quests"][QUEST_ID]["completed"])
        self.assertEqual(
            quest_action_proofs_for_quest(addon.player_data, QUEST_ID, QUEST_DATA),
            STAGE_ACTIONS,
        )
        self.assertEqual(addon.player_data["quest_points"], 1)
        self.assertEqual(addon.player_data["mining_exp"], 3000.0)
        self.assertEqual(addon.player_data["inventory"]["Ring of life"], 1)
        self.assertEqual(addon.current_skill, "Utilities")
        self.assertEqual(calls["gains"][-1], "The Lost Tribe complete")
        self.assertEqual(calls["dialogs"][-1][0], "Quest complete")
        self.assertIn("The Lost Tribe is complete", calls["dialogs"][-1][1])
        self.assertGreaterEqual(calls["saves"], 5)


if __name__ == "__main__":
    unittest.main()
