"""Underground Pass opening reviews stop after the drawbridge crossing."""

import copy
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.shop_data import SHOP_DATA
from ankiscape.logic.shop_logic import apply_shop_buy_pure
from ankiscape.logic_pure import quest_action_proofs
from ankiscape.logic_pure.logic_pure_quest import quest_journal_rows_pure, quest_locked_reasons_pure
from ankiscape.runtime.runtime_actions import handle_fletching_answer, handle_quest_answer
from tests.test_combat_quest_gate import _answer_review
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package
from tests.test_runtime_actions import _context


QUEST_ID = "underground_pass"
OPENING_ACTIONS = (
    "To begin, talk to King Lathas on the first floor of the Ardougne Castle.",
    "Ask King Lathas if his scouts have found a way through the mountains.",
    "As the ruse about the plague is now known to you, West Ardougne can be accessed through the front gates, so head through and walk all the way west through the city until you find the cave entrance with Koftik standing outside.",
    "Talk to him and he'll explain more about the pass and tell you to meet him inside, next to the bridge.",
    "Walk inside (1), and you'll see three paths branching off in different directions.",
    "Climb over the rocks to go around the swamp and get to where Koftik is standing next to a fire (2).",
    "Talk to him and he'll tell you it looks like there have been others in the cave already.",
    'Use the damp cloth on an arrow, then right-click and "light arrow" - or use the arrow on the fire nearby - to get a fire arrow, or a lit arrow if you used its bronze counterpart.',
    "Equip the bow and arrow.",
    "Move into the small room (3) to your north.",
    "Click on it and you'll fire your lit arrow at the rope.",
    "If you succeed, the draw-bridge will drop and you'll automatically walk across the bridge.",
)
NEXT_INSTRUCTION = (
    "The lever next to you will drop the bridge, so do not pull it unless you want to leave. "
    "Getting back will take another arrow."
)


def _player():
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player.update(current_quest=QUEST_ID, agility_level=50, prayer_level=43, ranged_level=60, thieving_level=50)
    for skill in ("attack", "strength", "defense", "constitution"):
        player[f"{skill}_level"] = 85
    # The separate full-route checks establish availability; these states set eligibility only.
    for quest_id in ("plague_city", "biohazard"):
        player["quests"][quest_id] = {
            "started": True, "progress": QUEST_DATA[quest_id]["stages"], "completed": True,
        }
    player["inventory"] = {"Shortbow": 1, "Bronze arrows": 3, "Coins": 100, "Rope": 2, "Spade": 1}
    return player


class UndergroundPassOpeningTest(unittest.TestCase):
    def test_each_missing_prerequisite_refuses_without_actions_or_consumption(self):
        for quest_id in ("plague_city", "biohazard"):
            with self.subTest(quest=quest_id):
                player = _player()
                player["quests"][quest_id] = {"started": False, "progress": 0, "completed": False}
                before = copy.deepcopy(player)
                calls = {"xp": [], "saves": 0, "errors": []}
                self.assertTrue(quest_locked_reasons_pure(player, QUEST_ID, QUEST_DATA))
                self.assertFalse(handle_quest_answer(_context(player, calls)))
                self.assertEqual(player, before)
                self.assertEqual(calls["saves"], 0)

    def test_existing_model_skill_gates_refuse_atomically(self):
        for skill, level in (("agility", 49), ("prayer", 42), ("ranged", 24), ("thieving", 49), ("combat", 1)):
            with self.subTest(skill=skill):
                player = _player()
                if skill == "combat":
                    for combat_skill in ("attack", "strength", "defense", "constitution", "ranged", "magic", "prayer"):
                        player[f"{combat_skill}_level"] = 1
                else:
                    player[f"{skill}_level"] = level
                before = copy.deepcopy(player)
                calls = {"xp": [], "saves": 0, "errors": []}
                self.assertFalse(handle_quest_answer(_context(player, calls)))
                self.assertEqual(player, before)
                self.assertEqual(calls["saves"], 0)

    def test_missing_bow_crossbows_and_ogre_bows_refuse_without_spending_arrow(self):
        for bow in (None, "Rune crossbow", "Ogre bow", "Comp ogre bow", "Shortbow (u)"):
            with self.subTest(bow=bow):
                player = _player()
                del player["inventory"]["Shortbow"]
                if bow:
                    player["equipment"]["weapon"] = bow
                before = copy.deepcopy(player)
                calls = {"xp": [], "saves": 0, "errors": []}
                self.assertFalse(handle_quest_answer(_context(player, calls)))
                self.assertEqual(player, before)
                self.assertEqual(calls["saves"], 0)

    def test_missing_and_prohibited_arrows_refuse_and_can_resume(self):
        for arrow in (None, "Broad arrows", "Ogre arrows", "Ice arrows", "Bronze arrows (p)", "Saradomin arrows"):
            with self.subTest(arrow=arrow):
                player = _player()
                del player["inventory"]["Bronze arrows"]
                if arrow:
                    player["inventory"][arrow] = 4
                before = copy.deepcopy(player)
                calls = {"xp": [], "saves": 0, "errors": []}
                self.assertFalse(handle_quest_answer(_context(player, calls)))
                self.assertEqual(player, before)
                self.assertEqual(calls["saves"], 0)
                player["inventory"]["Iron arrows"] = 1
                self.assertTrue(handle_quest_answer(_context(player)))
                self.assertEqual(player["inventory"]["Iron arrows"], 0)
                self.assertEqual(player["quests"][QUEST_ID]["progress"], 2)

    def test_owned_and_equipped_bows_consume_only_one_selected_arrow(self):
        for bow, arrow, equipped in (("Shortbow", "Bronze arrows", False), ("Shortbow", "Iron arrows", True), ("Yew comp bow", "Rune arrows", False), ("Dark bow", "Dragon arrows", True)):
            with self.subTest(bow=bow, equipped=equipped):
                player = _player()
                player["inventory"].pop("Shortbow")
                player["inventory"].pop("Bronze arrows")
                player["inventory"].update({arrow: 3, "Broad arrows": 9})
                if equipped:
                    player["equipment"]["weapon"] = bow
                else:
                    player["inventory"][bow] = 1
                before = copy.deepcopy(player)
                self.assertTrue(handle_quest_answer(_context(player)))
                expected = copy.deepcopy(before)
                expected["inventory"][arrow] -= 1
                expected["quests"][QUEST_ID] = {"started": True, "progress": 2, "completed": False}
                expected["quest_action_proofs"] = sorted(OPENING_ACTIONS)
                expected["achievement_progress"]["skills"]["quest"] = {
                    "actions": {QUEST_ID: 1}, "outputs": {},
                }
                expected["action_telemetry"]["actions"][f"quest:{QUEST_ID}"] = {
                    "skill_id": "quest", "action_id": QUEST_ID, "attempts": 1,
                    "successes": 1, "failures": 0, "expected_successes": 1.0,
                    "current_dry_streak": 0, "longest_dry_streak": 0, "outputs": {},
                    "failure_kinds": {}, "last_success": True, "last_expected_success_chance": 1.0,
                }
                self.assertEqual(player, expected)

    def test_ordinary_shop_inputs_run_ordered_crossing_and_leave_stage_two_held(self):
        player = _player()
        del player["inventory"]["Shortbow"]
        del player["inventory"]["Bronze arrows"]
        for item, quantity in (("Shortbow", 1), ("Bronze arrows", 3)):
            row = next(row for row in SHOP_DATA["lowes_archery_emporium"]["stock"] if row["item_name"] == item)
            player, result = apply_shop_buy_pure(player, "lowes_archery_emporium", row["id"], quantity)
            self.assertTrue(result["allowed"])
        player["inventory"]["Iron arrows"] = 4
        before = copy.deepcopy(player)
        with patch.object(
            quest_action_proofs, "quest_action_proofs_after_event_pure",
            wraps=quest_action_proofs.quest_action_proofs_after_event_pure,
        ) as events:
            self.assertTrue(handle_quest_answer(_context(player)))
        self.assertEqual(
            [call.args[2] for call in events.call_args_list if call.args[1] == "quest_stage"],
            [f"{QUEST_ID}:{action}" for action in OPENING_ACTIONS],
        )
        expected = copy.deepcopy(before)
        expected["inventory"]["Bronze arrows"] -= 1
        expected["quests"][QUEST_ID] = {"started": True, "progress": 2, "completed": False}
        expected["quest_action_proofs"] = sorted(OPENING_ACTIONS)
        expected["achievement_progress"]["skills"]["quest"] = {
            "actions": {QUEST_ID: 1}, "outputs": {},
        }
        expected["action_telemetry"]["actions"][f"quest:{QUEST_ID}"] = {
            "skill_id": "quest", "action_id": QUEST_ID, "attempts": 1,
            "successes": 1, "failures": 0, "expected_successes": 1.0,
            "current_dry_streak": 0, "longest_dry_streak": 0, "outputs": {},
            "failure_kinds": {}, "last_success": True, "last_expected_success_chance": 1.0,
        }
        self.assertEqual(player, expected)
        journal = quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA)
        self.assertEqual(journal[-1]["stage"], 2)
        self.assertEqual(journal[-1]["lines"][0], NEXT_INSTRUCTION)
        for _ in range(2):
            self.assertFalse(handle_quest_answer(_context(player)))
            self.assertEqual(player, expected)

    def test_ordinary_fletching_produces_the_bow_and_arrow_consumed_by_opening(self):
        player = _player()
        player["fletching_level"] = 5
        player["inventory"] = {"Shortbow (u)": 1, "Bow string": 1, "Headless arrows": 15, "Bronze arrowtips": 15}
        for target in ("string_shortbow", "bronze_arrows"):
            player["current_fletch"] = target
            self.assertTrue(handle_fletching_answer(_context(player, random_values=(0.5, 0.5))))
        self.assertEqual(player["inventory"]["Shortbow"], 1)
        self.assertEqual(player["inventory"]["Bronze arrows"], 15)
        before_exp = {key: value for key, value in player.items() if key.endswith("_exp")}
        self.assertTrue(handle_quest_answer(_context(player)))
        self.assertEqual(player["inventory"]["Bronze arrows"], 14)
        self.assertEqual(player["inventory"]["Shortbow"], 1)
        self.assertEqual({key: value for key, value in player.items() if key.endswith("_exp")}, before_exp)
        self.assertFalse(player["quests"][QUEST_ID]["completed"])

    def test_saved_opening_and_review_undo_restore_arrow_proofs_and_stage(self):
        original_modules = dict(sys.modules)
        try:
            _install_runtime_fakes()
            addon = _load_addon_as_package("ankiscape_underground_pass_e2e")
            saved = []
            addon.show_error_message = lambda *_args: None
            addon.save_player_data = lambda: saved.append(copy.deepcopy(addon._state.player_data))
            addon.check_achievements = lambda _data: None
            addon._refresh_skill_availability = lambda: None
            addon._show_activity_gain = lambda _text: None
            addon._show_exp = lambda _amount: None
            addon.level_up_check = lambda *_args: None
            addon.update_review_hud = lambda *_args: None
            player = _player()
            addon._state.player_data = player
            addon._state.current_skill = "Quests"
            addon._state.review_undo_stack.clear()
            before_inventory = copy.deepcopy(player["inventory"])
            _answer_review(addon)
            self.assertEqual(saved[-1]["quests"][QUEST_ID]["progress"], 2)
            self.assertEqual(saved[-1]["inventory"]["Bronze arrows"], 2)
            self.assertEqual(saved[-1]["quest_action_proofs"], sorted(OPENING_ACTIONS))
            addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
            restored = addon._state.player_data
            self.assertFalse(restored["quests"][QUEST_ID]["started"])
            self.assertEqual(restored["inventory"], before_inventory)
            self.assertFalse(restored.get("quest_action_proofs"))
            addon._state.current_skill = "Quests"
            _answer_review(addon)
            self.assertEqual(saved[-1]["quests"][QUEST_ID]["progress"], 2)
            self.assertEqual(saved[-1]["inventory"]["Bronze arrows"], 2)
        finally:
            sys.modules.clear()
            sys.modules.update(original_modules)
