"""Fenkenstrain's opening reviews stop before the body-part search."""

import copy
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic_pure import quest_action_proofs
from ankiscape.logic_pure.logic_pure_quest import quest_locked_reasons_pure
from ankiscape.runtime.runtime_actions import handle_quest_answer
from tests.test_combat_quest_gate import _answer_review
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package
from tests.test_runtime_actions import _context


QUEST_ID = "creature_of_fenkenstrain"
OPENING_ACTIONS = (
    "To start the quest, read the signpost in the centre of Canifis.",
    "After you've started the quest, go northeast to Fenkenstrain's Castle.",
    "Talk to Dr. Fenkenstrain and a job interview will commence.",
    'When asked to describe yourself in one word, answer "braindead" and that your best skill is gravedigging.',
    "Wear your Amulet of ghostspeak and talk to the headless Gardener Ghost.",
    "Offer to help find his head, which is buried in a grave in the Haunted Woods",
    "take him south into the Haunted Woods.",
)


def _player():
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player.update(current_quest=QUEST_ID, crafting_level=20, thieving_level=25)
    # These completed prerequisites set eligibility, not acquisition proof.
    for quest_id in ("priest_in_peril", "the_restless_ghost"):
        player["quests"][quest_id] = {
            "started": True, "progress": QUEST_DATA[quest_id]["stages"], "completed": True,
        }
    player["inventory"] = {"Ghostspeak amulet": 1, "Coins": 37, "Tinderbox": 1}
    return player


class FenkenstrainOpeningTest(unittest.TestCase):
    def test_each_missing_prerequisite_refuses_without_changes(self):
        for quest_id, name in (("priest_in_peril", "Priest in Peril"), ("the_restless_ghost", "The Restless Ghost")):
            with self.subTest(quest=quest_id):
                player = _player()
                player["quests"][quest_id] = {"started": False, "progress": 0, "completed": False}
                before = copy.deepcopy(player)
                calls = {"xp": [], "saves": 0, "errors": []}
                self.assertIn(name, quest_locked_reasons_pure(player, QUEST_ID, QUEST_DATA))
                self.assertFalse(handle_quest_answer(_context(player, calls)))
                self.assertEqual(player, before)
                self.assertEqual(calls["saves"], 0)

    def test_existing_start_skill_gates_refuse_atomically(self):
        for skill, level in (("crafting", 19), ("thieving", 24)):
            with self.subTest(skill=skill):
                player = _player()
                player[f"{skill}_level"] = level
                before = copy.deepcopy(player)
                calls = {"xp": [], "saves": 0, "errors": []}
                self.assertFalse(handle_quest_answer(_context(player, calls)))
                self.assertEqual(player, before)
                self.assertEqual(calls["saves"], 0)

    def test_neither_ghostspeak_item_refuses_before_actions(self):
        player = _player()
        del player["inventory"]["Ghostspeak amulet"]
        before = copy.deepcopy(player)
        calls = {"xp": [], "saves": 0, "errors": []}
        self.assertFalse(handle_quest_answer(_context(player, calls)))
        self.assertEqual(player, before)
        self.assertEqual(calls["saves"], 0)

    def test_owned_and_equipped_alternatives_are_retained(self):
        for item in ("Ghostspeak amulet", "Cramulet"):
            for equipped in (False, True):
                with self.subTest(item=item, equipped=equipped):
                    player = _player()
                    del player["inventory"]["Ghostspeak amulet"]
                    if equipped:
                        player["equipment"]["neck"] = item
                    else:
                        player["inventory"][item] = 1
                    inventory = copy.deepcopy(player["inventory"])
                    equipment = copy.deepcopy(player["equipment"])
                    self.assertTrue(handle_quest_answer(_context(player)))
                    self.assertEqual(player["quests"][QUEST_ID]["progress"], 2)
                    self.assertEqual(player["inventory"], inventory)
                    self.assertEqual(player["equipment"], equipment)

    def test_ordinary_amulet_grant_opens_ordered_route_and_later_stage_stays_held(self):
        player = _player()
        del player["inventory"]["Ghostspeak amulet"]
        player["quests"]["the_restless_ghost"] = {"started": False, "progress": 0, "completed": False}
        player["current_quest"] = "the_restless_ghost"
        self.assertTrue(handle_quest_answer(_context(player)))
        self.assertEqual(player["inventory"]["Ghostspeak amulet"], 1)
        # The ordinary grant above proves acquisition; completion here sets eligibility only.
        player["quests"]["the_restless_ghost"] = {
            "started": True, "progress": QUEST_DATA["the_restless_ghost"]["stages"], "completed": True,
        }
        player["current_quest"] = QUEST_ID
        before_inventory = copy.deepcopy(player["inventory"])
        before_xp = {key: value for key, value in player.items() if key.endswith("_exp")}
        with patch.object(
            quest_action_proofs, "quest_action_proofs_after_event_pure",
            wraps=quest_action_proofs.quest_action_proofs_after_event_pure,
        ) as events:
            self.assertTrue(handle_quest_answer(_context(player)))
        self.assertEqual(
            [call.args[2] for call in events.call_args_list if call.args[1] == "quest_stage"],
            [f"{QUEST_ID}:{action}" for action in OPENING_ACTIONS],
        )
        self.assertEqual(player["quests"][QUEST_ID], {"started": True, "progress": 2, "completed": False})
        self.assertEqual(player["inventory"], before_inventory)
        self.assertEqual({key: player[key] for key in before_xp}, before_xp)
        self.assertEqual(player["quest_points"], 0)
        held = copy.deepcopy(player)
        for _ in range(2):
            self.assertFalse(handle_quest_answer(_context(player)))
            self.assertEqual(player, held)

    def test_saved_opening_and_review_undo_restore_unstarted_state(self):
        original_modules = dict(sys.modules)
        try:
            _install_runtime_fakes()
            addon = _load_addon_as_package("ankiscape_fenkenstrain_e2e")
            saved = []
            addon.show_error_message = lambda *_args: None
            addon.save_player_data = lambda: saved.append(copy.deepcopy(addon._state.player_data))
            addon.check_achievements = lambda _data: None
            addon._refresh_skill_availability = lambda: None
            addon._show_activity_gain = lambda _text: None
            addon._show_exp = lambda _amount: None
            addon.level_up_check = lambda *_args: None
            addon.update_review_hud = lambda *_args: None
            addon._state.player_data = _player()
            addon._state.current_skill = "Quests"
            addon._state.review_undo_stack.clear()
            inventory = copy.deepcopy(addon._state.player_data["inventory"])
            _answer_review(addon)
            self.assertEqual(saved[-1]["quests"][QUEST_ID]["progress"], 2)
            self.assertEqual(saved[-1]["quest_action_proofs"], sorted(OPENING_ACTIONS))
            self.assertEqual(saved[-1]["inventory"], inventory)
            addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
            self.assertFalse(addon._state.player_data["quests"][QUEST_ID]["started"])
            self.assertFalse(addon._state.player_data.get("quest_action_proofs"))
            self.assertEqual(addon._state.player_data["inventory"], inventory)
            addon._state.current_skill = "Quests"
            _answer_review(addon)
            self.assertEqual(saved[-1]["quests"][QUEST_ID]["progress"], 2)
            self.assertEqual(saved[-1]["inventory"], inventory)
        finally:
            sys.modules.clear()
            sys.modules.update(original_modules)
