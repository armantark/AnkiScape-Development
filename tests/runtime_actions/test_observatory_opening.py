"""Observatory opening model evidence stops before material handoff."""

import copy
import random
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from ankiscape.logic_pure import quest_action_proofs
from ankiscape.logic_pure.logic_pure_quest import quest_locked_reasons_pure
from ankiscape.runtime.runtime_actions import handle_quest_answer
from tests.test_combat_quest_gate import _answer_review
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package
from tests.test_runtime_actions import _context


QUEST_ID = "observatory_quest"
OPENING_ACTIONS = (
    "Talk to the Observatory professor in the house near the Observatory which is located North of Castle Wars.",
    "Talk to his assistant.",
)


def _player():
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player.update(current_quest=QUEST_ID, crafting_level=10)
    player["inventory"] = {"Coins": 37, "Tinderbox": 1}
    return player


class ObservatoryOpeningTest(unittest.TestCase):
    def test_crafting_nine_refuses_unstarted_quest_atomically(self):
        player = _player()
        player["crafting_level"] = 9
        before = copy.deepcopy(player)
        calls = {"xp": [], "saves": 0, "errors": []}
        self.assertIn("Crafting 10", quest_locked_reasons_pure(player, QUEST_ID, QUEST_DATA))
        self.assertFalse(handle_quest_answer(_context(player, calls)))
        self.assertEqual(player, before)
        self.assertEqual(calls["saves"], 0)

    def test_unstarted_review_executes_professor_then_assistant_without_materials(self):
        player = _player()
        before = copy.deepcopy(player)
        self.assertEqual(player["quests"][QUEST_ID], {"started": False, "progress": 0, "completed": False})
        calls = {"xp": [], "saves": 0, "errors": []}
        ctx = _context(player, calls)
        ctx.random_random = random.Random(6496978).random
        with patch.object(
            quest_action_proofs, "quest_action_proofs_after_event_pure",
            wraps=quest_action_proofs.quest_action_proofs_after_event_pure,
        ) as events:
            self.assertTrue(handle_quest_answer(ctx))
        self.assertEqual(
            [call.args[2] for call in events.call_args_list if call.args[1] == "quest_stage"],
            [f"{QUEST_ID}:{action}" for action in OPENING_ACTIONS],
        )
        self.assertEqual(player["quests"][QUEST_ID], {"started": True, "progress": 2, "completed": False})
        self.assertEqual(player["quest_action_proofs"], sorted(OPENING_ACTIONS))
        self.assertEqual(player["inventory"], before["inventory"])
        self.assertEqual(player["equipment"], before["equipment"])
        self.assertEqual({key: value for key, value in player.items() if key.endswith("_exp")},
                         {key: value for key, value in before.items() if key.endswith("_exp")})
        self.assertEqual(player["quest_points"], before["quest_points"])
        self.assertEqual(player["pending_skill_exp_rewards"], before["pending_skill_exp_rewards"])
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["xp"], [])

    def test_material_stage_refuses_even_with_all_materials_and_retains_opening_proofs(self):
        player = _player()
        self.assertTrue(handle_quest_answer(_context(player)))
        player["inventory"].update({"Bronze bar": 1, "Plank": 3, "Molten glass": 1})
        before = copy.deepcopy(player)
        calls = {"xp": [], "saves": 0, "errors": []}
        for _ in range(2):
            self.assertFalse(handle_quest_answer(_context(player, calls)))
            self.assertEqual(player, before)
        self.assertEqual(calls["saves"], 0)
        self.assertIn("Complete Observatory Quest stage 2 objective", calls["errors"][-1][1])

    def test_catalog_keeps_journal_start_gate_and_material_stage(self):
        generated = next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == QUEST_ID)
        quest = QUEST_DATA[QUEST_ID]
        self.assertEqual(quest["stages"], 5)
        self.assertEqual(quest["required_skills"], generated["required_skills"])
        self.assertEqual(quest["required_quests"], ())
        self.assertEqual(quest["required_quest_points"], 0)
        self.assertEqual(quest["journal_stages"], {
            row["stage"]: row["journal"] for row in generated["journal_stages"]
        })
        first, second = quest["stage_requirements"][:2]
        self.assertEqual(first["auto_actions"], OPENING_ACTIONS)
        self.assertEqual(first["required_actions"], ())
        for key in ("required_inventory", "required_tools", "consumed_inventory", "produced_inventory"):
            self.assertFalse(first[key])
        self.assertEqual(second["required_inventory"], {"Plank": 3, "Bronze bar": 1, "Molten glass": 1})
        self.assertEqual(second["required_actions"], ("Complete Observatory Quest stage 2 objective",))
        self.assertEqual(second["auto_actions"], ())

    def test_answer_card_save_undo_and_rereview_restore_whole_state(self):
        original_modules = dict(sys.modules)
        rng_state = random.getstate()
        try:
            random.seed(5706277)
            _install_runtime_fakes()
            addon = _load_addon_as_package("ankiscape_observatory_e2e")
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
            before = copy.deepcopy(addon._state.player_data)
            _answer_review(addon)
            after = copy.deepcopy(addon._state.player_data)
            self.assertEqual(saved[-1], after)
            self.assertEqual(after["quests"][QUEST_ID], {"started": True, "progress": 2, "completed": False})
            self.assertEqual(after["quest_action_proofs"], sorted(OPENING_ACTIONS))
            self.assertEqual(after["inventory"], before["inventory"])
            self.assertEqual(after["equipment"], before["equipment"])
            self.assertEqual(after["quest_points"], before["quest_points"])
            addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
            self.assertEqual(addon._state.player_data, before)
            self.assertEqual(saved[-1], before)
            addon._state.current_skill = "Quests"
            _answer_review(addon)
            self.assertEqual(addon._state.player_data, after)
            self.assertEqual(saved[-1], after)
        finally:
            random.setstate(rng_state)
            sys.modules.clear()
            sys.modules.update(original_modules)
