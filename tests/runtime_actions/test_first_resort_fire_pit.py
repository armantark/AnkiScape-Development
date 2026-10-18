"""The deduplicated fire-pit journal is one atomic inventory handoff."""

import copy
import dataclasses
import json
import random
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import QUEST_DATA, QUEST_UNLOCK_RULES
from ankiscape.data.shop_data import SHOP_DATA
from ankiscape.logic.shop_logic import apply_shop_buy_pure
from ankiscape.logic_pure import quest_action_proofs
from ankiscape.logic_pure.logic_pure_quest import (
    quest_current_stage_blocker_reasons_pure,
    target_unlock_locked_reasons_pure,
)
from ankiscape.runtime.runtime_actions import (
    handle_combat_answer,
    handle_quest_answer,
    handle_utility_answer,
)
from tests.runtime_actions.test_first_resort_opening import QUEST_ID, _player
from tests.test_combat_quest_gate import _answer_review
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package
from tests.test_runtime_actions import _context


FIRE_PIT_ACTIONS = (
    "Talk to Chargurr.",
    "Give her four Spears.",
    "Use two raw chompies on the spears.",
    "Use a Tinderbox on the fire pit.",
    "Talk to Balnea.",
    "Talk to Snurgh who is in a building in the Southeast corner of Oo'glog.",
)
SPEARS = (
    "Bronze spear", "Iron spear", "Steel spear", "Black spear",
    "Mithril spear", "Adamant spear", "Rune spear", "Dragon spear",
)


def _reach_fire_pit():
    player = _player()
    player["inventory"].update({"Achey tree logs": 8, "Eucalyptus logs": 10})
    if not handle_quest_answer(_context(player)) or not handle_quest_answer(_context(player)):
        raise AssertionError("First Resort opening/log actions did not reach the fire pit")
    return player


class FirstResortFirePitTest(unittest.TestCase):
    def test_each_registered_plain_spear_consumes_four_and_preserves_surplus_and_equipment(self):
        for spear in SPEARS:
            with self.subTest(spear=spear):
                player = _reach_fire_pit()
                player["inventory"].update({spear: 7, "Raw chompy": 5, "Primweed": 9})
                player["equipment"]["weapon"] = spear
                expected = {**player["inventory"], spear: 3, "Raw chompy": 3}
                equipment = copy.deepcopy(player["equipment"])
                self.assertTrue(handle_quest_answer(_context(player)))
                self.assertEqual(player["inventory"], expected)
                self.assertEqual(player["equipment"], equipment)
                self.assertEqual(player["quests"][QUEST_ID]["progress"], 4)

    def test_short_and_mixed_stacks_and_equipped_spear_refuse_atomically(self):
        for stacks in ({}, {"Bronze spear": 3}, {"Bronze spear": 3, "Iron spear": 1},
                       {"Bronze spear": 2, "Iron spear": 2}):
            with self.subTest(stacks=stacks):
                player = _reach_fire_pit()
                player["inventory"].update({**stacks, "Raw chompy": 2})
                player["equipment"]["weapon"] = "Bronze spear"
                before = copy.deepcopy(player)
                calls = {"xp": [], "saves": 0, "errors": []}
                self.assertFalse(handle_quest_answer(_context(player, calls)))
                self.assertEqual(player, before)
                self.assertEqual(calls["saves"], 0)

    def test_generic_bone_poisoned_and_specialised_spears_never_supply_the_handoff(self):
        excluded = ("Spears", "Bone spear", "Bronze spear(p)", "Bronze spear(p+)",
                    "Bronze spear(p++)", "Bronze spear(kp)", "Leaf-bladed spear")
        for item in excluded:
            with self.subTest(item=item):
                player = _reach_fire_pit()
                player["inventory"].update({item: 4, "Raw chompy": 2})
                before = copy.deepcopy(player)
                self.assertFalse(handle_quest_answer(_context(player)))
                self.assertEqual(player, before)

    def test_insufficient_chompies_refuse_without_consuming_spears_or_recording_proofs(self):
        for count in (0, 1):
            with self.subTest(chompies=count):
                player = _reach_fire_pit()
                player["inventory"].update({"Rune spear": 4, "Raw chompy": count})
                before = copy.deepcopy(player)
                self.assertFalse(handle_quest_answer(_context(player)))
                self.assertEqual(player, before)
                player["inventory"]["Raw chompy"] = 2
                self.assertTrue(handle_quest_answer(_context(player)))
                self.assertEqual(player["inventory"]["Rune spear"], 0)
                self.assertEqual(player["inventory"]["Raw chompy"], 0)

    def test_competing_stacks_consume_only_the_first_sufficient_alternative(self):
        for bronze, expected in ((5, (1, 6)), (3, (3, 2))):
            with self.subTest(bronze=bronze):
                player = _reach_fire_pit()
                player["inventory"].update({"Iron spear": 6, "Bronze spear": bronze, "Raw chompy": 2})
                self.assertTrue(handle_quest_answer(_context(player)))
                self.assertEqual((player["inventory"]["Bronze spear"], player["inventory"]["Iron spear"]), expected)

    def test_tool_belt_supplies_tinderbox_and_six_proofs_precede_held_stage_four(self):
        player = _reach_fire_pit()
        del player["inventory"]["Tinderbox"]
        player["inventory"].update({"Steel spear": 4, "Raw chompy": 2, "Stripy feather": 8,
                                    "Wolf bones": 4, "Larupia fur": 8})
        before = copy.deepcopy(player)
        calls = {"xp": [], "saves": 0, "errors": []}
        with patch.object(quest_action_proofs, "quest_action_proofs_after_event_pure",
                          wraps=quest_action_proofs.quest_action_proofs_after_event_pure) as events:
            self.assertTrue(handle_quest_answer(_context(player, calls)))
        action_events = [call.args[2] for call in events.call_args_list if call.args[1] == "quest_stage"]
        self.assertEqual(action_events, [f"{QUEST_ID}:{action}" for action in FIRE_PIT_ACTIONS])
        self.assertEqual(player["quest_action_proofs"], sorted(set(before["quest_action_proofs"]) | set(FIRE_PIT_ACTIONS)))
        self.assertEqual(player["inventory"], {**before["inventory"], "Steel spear": 0, "Raw chompy": 0})
        self.assertNotIn("Tinderbox", player["inventory"])
        self.assertEqual({key: value for key, value in player.items() if key.endswith("_exp")},
                         {key: value for key, value in before.items() if key.endswith("_exp")})
        self.assertEqual(player["quest_points"], before["quest_points"])
        self.assertEqual(player["quests"][QUEST_ID], {"started": True, "progress": 4, "completed": False})
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["saves"], 1)
        telemetry = player["action_telemetry"]["actions"][f"quest:{QUEST_ID}"]
        self.assertEqual(telemetry["successes"], 3)
        self.assertEqual(telemetry["attempts"], 3)
        self.assertEqual(telemetry["outputs"], {})
        held = copy.deepcopy(player)
        for _ in range(3):
            self.assertEqual(quest_current_stage_blocker_reasons_pure(player, QUEST_ID, QUEST_DATA),
                             ("Action required: Complete As a First Resort stage 4 objective",))
            self.assertFalse(handle_quest_answer(_context(player)))
            self.assertEqual(player, held)
        for skill, target in (("mining", "red_sandstone"), ("hunter", "catch_wimpy_bird"),
                              ("utility", "make_robust_glass")):
            self.assertTrue(target_unlock_locked_reasons_pure(player, skill, target, QUEST_UNLOCK_RULES))
        self.assertEqual(QUEST_DATA[QUEST_ID]["journal_stages"][4][0], "Give her eight Stripy feathers.")

    def test_saved_fire_pit_and_answer_card_undo_restore_the_complete_prior_player(self):
        original_modules = dict(sys.modules)
        try:
            _install_runtime_fakes()
            addon = _load_addon_as_package("ankiscape_first_resort_fire_pit_e2e")
            saved = []
            errors = []
            addon.show_error_message = lambda title, message: errors.append((title, message))
            addon.save_player_data = lambda: saved.append(copy.deepcopy(addon._state.player_data))
            addon.check_achievements = lambda _data: None
            addon._refresh_skill_availability = lambda: None
            addon._show_activity_gain = lambda _text: None
            addon._show_exp = lambda _amount: None
            addon.level_up_check = lambda *_args: None
            addon.update_review_hud = lambda *_args: None
            player = _player()
            player["inventory"].update({"Achey tree logs": 8, "Eucalyptus logs": 10,
                                        "Adamant spear": 6, "Raw chompy": 3})
            addon._state.player_data = player
            addon._state.current_skill = "Quests"
            addon._state.review_undo_stack.clear()
            _answer_review(addon)
            _answer_review(addon)
            before = copy.deepcopy(addon._state.player_data)
            _answer_review(addon)
            self.assertEqual(saved[-1]["quests"][QUEST_ID]["progress"], 4, errors)
            self.assertEqual(saved[-1]["inventory"]["Adamant spear"], 2)
            self.assertEqual(saved[-1]["inventory"]["Raw chompy"], 1)
            self.assertTrue(set(FIRE_PIT_ACTIONS).issubset(saved[-1]["quest_action_proofs"]))
            restored_save = json.loads(json.dumps(saved[-1]))
            self.assertEqual(restored_save["inventory"], saved[-1]["inventory"])
            self.assertEqual(restored_save["quests"], saved[-1]["quests"])
            self.assertEqual(restored_save["quest_action_proofs"], saved[-1]["quest_action_proofs"])
            addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
            self.assertEqual(addon._state.player_data, before)
            self.assertEqual(saved[-1], before)
            addon._state.current_skill = "Quests"
            _answer_review(addon)
            self.assertEqual(addon._state.player_data["quests"][QUEST_ID]["progress"], 4, errors)
            self.assertEqual(addon._state.player_data["inventory"]["Adamant spear"], 2)
        finally:
            sys.modules.clear()
            sys.modules.update(original_modules)

    def test_existing_shop_combat_utility_and_quest_handlers_supply_the_fire_pit(self):
        # Zogre completion and starting skills are seeded eligibility; Big Chompy,
        # its bow, Goblin drops and both hunting outputs use real model handlers.
        player = _player()
        player.update(cooking_level=30, fletching_level=5, ranged_level=30,
                      attack_level=70, strength_level=70, defense_level=70,
                      constitution_level=70, combat_lifepoints=700)
        player["inventory"].update({"Coins": 1000, "Feather": 1, "Wolf bones": 6})
        player["current_utility"] = "hunt_chompy_birds"
        before = copy.deepcopy(player)
        self.assertFalse(handle_utility_answer(_context(player)))
        self.assertEqual(player, before)
        player["current_quest"] = "big_chompy_bird_hunting"
        rng = random.Random(0)
        for _ in range(60):
            self.assertTrue(handle_quest_answer(dataclasses.replace(_context(player), random_random=rng.random)))
            if player["quests"]["big_chompy_bird_hunting"]["completed"]:
                break
        self.assertTrue(player["quests"]["big_chompy_bird_hunting"]["completed"])
        self.assertEqual(player["inventory"]["Ogre bow"], 1)
        arrow = next(row for row in SHOP_DATA["gift_shop"]["stock"] if row["item_name"] == "Ogre arrow")
        bought, result = apply_shop_buy_pure(player, "gift_shop", arrow["id"], 2)
        self.assertTrue(result["allowed"], result)
        self.assertEqual(result["quantity"], 2)
        player.update(bought)
        for _ in range(2):
            count = player["inventory"].get("Raw chompy", 0)
            self.assertTrue(handle_utility_answer(_context(player)))
            self.assertEqual(player["inventory"]["Raw chompy"], count + 1)
        self.assertEqual(player["inventory"]["Ogre bow"], 1)
        self.assertEqual(player["inventory"]["Ogre arrow"], 0)
        player["current_combat_target"] = "goblin_level_5"
        player["equipment"]["weapon"] = "Rune scimitar"
        rng = random.Random(9)
        for _ in range(500):
            self.assertTrue(handle_combat_answer(dataclasses.replace(_context(player), random_random=rng.random)))
            if player["inventory"].get("Bronze spear", 0) >= 4:
                break
        self.assertGreaterEqual(player["inventory"].get("Bronze spear", 0), 4)
        player["current_quest"] = QUEST_ID
        player["inventory"].update({"Achey tree logs": 8, "Eucalyptus logs": 10})
        self.assertFalse(player["quests"][QUEST_ID]["started"])
        self.assertTrue(handle_quest_answer(_context(player)))
        self.assertTrue(handle_quest_answer(_context(player)))
        before_inventory = copy.deepcopy(player["inventory"])
        self.assertTrue(handle_quest_answer(_context(player)))
        self.assertEqual(player["inventory"], {**before_inventory,
                         "Bronze spear": before_inventory["Bronze spear"] - 4,
                         "Raw chompy": before_inventory["Raw chompy"] - 2})
        self.assertEqual(player["quests"][QUEST_ID]["progress"], 4)
        self.assertFalse(player["quests"][QUEST_ID]["completed"])
