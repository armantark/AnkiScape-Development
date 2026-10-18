"""Observatory reviews reach the kitchen key, then retain the later-stage stop."""

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
from ankiscape.data.shop_data import SHOP_DATA
from ankiscape.logic.shop_logic import apply_shop_buy_pure
from ankiscape.logic_pure import quest_action_proofs
from ankiscape.logic_pure import logic_pure_quest as quest_logic
from ankiscape.logic_pure.logic_pure_quest import quest_locked_reasons_pure
from ankiscape.runtime.runtime_actions import (
    handle_crafting_answer, handle_mining_answer, handle_quest_answer,
    handle_smithing_answer, handle_utility_answer, handle_woodcutting_answer,
)
from tests.test_combat_quest_gate import _answer_review
from tests.test_integration_smoke import (
    _DummyCol, _DummyMW, _FakeReviewer, _install_runtime_fakes, _load_addon_as_package,
)
from tests.test_runtime_actions import _context


QUEST_ID = "observatory_quest"
OPENING_ACTIONS = (
    "Talk to the Observatory professor in the house near the Observatory which is located North of Castle Wars.",
    "Talk to his assistant.",
)
MATERIAL_ACTIONS = (
    "Talk to the assistant then the professor to hand over the three planks, bronze bar and molten glass.",
    "Leave the house and go east to the abandoned buildings.",
    "Climb down the stairs in the western building.",
    'Search the dungeon chests, clicking "Click here to continue", until you find the Goblin kitchen key.',
    "Return to the staircase at the entrance without exiting the dungeon.",
)
MATERIALS = {"Plank": 3, "Bronze bar": 1, "Molten glass": 1}


def _player():
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player.update(current_quest=QUEST_ID, crafting_level=10)
    player["inventory"] = {"Coins": 37, "Tinderbox": 1, "Lobster": 4, "Bronze sword": 1}
    player["equipment"]["weapon"] = "Bronze sword"
    player["quests"]["rune_mysteries"] = {"started": True, "progress": 2, "completed": False}
    return player


def _material_player():
    player = _player()
    if not handle_quest_answer(_context(player)):
        raise AssertionError("Observatory opening did not reach the material stage")
    player["inventory"].update(MATERIALS)
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

    def test_missing_materials_refuse_without_mutating_state_or_proofs(self):
        for item, required in MATERIALS.items():
            for quantity in range(required):
                with self.subTest(item=item, quantity=quantity):
                    player = _material_player()
                    player["inventory"][item] = quantity
                    before = copy.deepcopy(player)
                    calls = {"xp": [], "saves": 0, "errors": []}
                    self.assertFalse(handle_quest_answer(_context(player, calls)))
                    self.assertEqual(player, before)
                    self.assertEqual(calls["saves"], 0)
                    self.assertIn(item, calls["errors"][-1][1])

    def test_material_review_records_complete_ordered_path_and_preserves_resources(self):
        player = _material_player()
        before = copy.deepcopy(player)
        calls = {"xp": [], "saves": 0, "errors": []}
        with patch.object(
            quest_action_proofs, "quest_action_proofs_after_event_pure",
            wraps=quest_action_proofs.quest_action_proofs_after_event_pure,
        ) as events:
            self.assertTrue(handle_quest_answer(_context(player, calls)))
        self.assertEqual(
            [call.args[2] for call in events.call_args_list if call.args[1] == "quest_stage"],
            [f"{QUEST_ID}:{action}" for action in MATERIAL_ACTIONS],
        )
        expected = copy.deepcopy(before)
        expected["quests"][QUEST_ID]["progress"] = 3
        expected["quest_action_proofs"] = sorted(OPENING_ACTIONS + MATERIAL_ACTIONS)
        telemetry = expected["action_telemetry"]["actions"][f"quest:{QUEST_ID}"]
        for counter in ("attempts", "successes", "expected_successes"):
            telemetry[counter] += 1
        expected["achievement_progress"]["skills"]["quest"]["actions"][QUEST_ID] += 1
        self.assertEqual(player, expected)
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["errors"], [])

    def test_normal_gathering_production_and_shop_supply_the_material_review(self):
        player = _player()
        player["inventory"]["Coins"] = 1_000
        self.assertTrue(handle_quest_answer(_context(player)))
        for item in MATERIALS:
            self.assertEqual(player["inventory"].get(item, 0), 0)
        player.update(current_tree="tree", current_utility="convert_logs_to_planks")
        for _ in range(3):
            self.assertTrue(handle_woodcutting_answer(_context(player, random_values=(0.0,) + (0.99,) * 20)))
            self.assertEqual(player["inventory"]["Logs"], 1)
            self.assertTrue(handle_utility_answer(_context(player)))
            self.assertEqual(player["inventory"]["Logs"], 0)
        for ore, item in (("copper", "Copper ore"), ("tin", "Tin ore")):
            player["current_ore"] = ore
            self.assertTrue(handle_mining_answer(_context(player, random_values=(0.0,) + (0.99,) * 20)))
            self.assertEqual(player["inventory"][item], 1)
        player["current_smith"] = "smelt_bronze_bar"
        self.assertTrue(handle_smithing_answer(_context(player, random_values=(0.99,) * 20)))
        shop_id = "trader_stans_trading_post"
        for item in ("Soda ash", "Bucket of sand"):
            row = next(row for row in SHOP_DATA[shop_id]["stock"] if row["item_name"] == item)
            player, bought = apply_shop_buy_pure(player, shop_id, row["id"], 1)
            self.assertTrue(bought["allowed"], bought)
            self.assertEqual(bought["total_price"], 2)
        player["current_craft"] = "glass_molten_glass"
        self.assertTrue(handle_crafting_answer(_context(player, random_values=(0.99,) * 20)))
        self.assertEqual({item: player["inventory"][item] for item in MATERIALS}, MATERIALS)
        self.assertEqual(player["inventory"]["Coins"], 696)
        self.assertEqual(player["inventory"]["Bucket"], 1)
        before = copy.deepcopy(player)
        self.assertTrue(handle_quest_answer(_context(player)))
        self.assertEqual(player["inventory"], before["inventory"])
        self.assertEqual(player["quests"][QUEST_ID]["progress"], 3)
        self.assertEqual(player["quest_action_proofs"], sorted(OPENING_ACTIONS + MATERIAL_ACTIONS))
        for key in before["action_telemetry"]["actions"]:
            if key != f"quest:{QUEST_ID}":
                self.assertEqual(player["action_telemetry"]["actions"][key], before["action_telemetry"]["actions"][key])

    def test_next_reviews_fight_real_spider_then_refuse_generic_objective(self):
        player = _material_player()
        self.assertTrue(handle_quest_answer(_context(player)))
        player.update(attack_level=40, strength_level=20, defense_level=40,
                      constitution_level=40, combat_lifepoints=400)
        encounter_id = "observatory_quest_poisonous_spider_31"
        calls = {"xp": [], "saves": 0, "errors": []}
        rng = random.Random(9)
        ctx = _context(player, calls, random_values=(rng.random() for _ in range(10000)))
        ctx.cadence_live_enabled = True
        with patch.object(quest_logic, "apply_combat_burst_pure", wraps=quest_logic.apply_combat_burst_pure) as fight:
            self.assertTrue(handle_quest_answer(ctx))
            for _ in range(10):
                if encounter_id in player.get("quest_combat_active_encounters", {}).get(QUEST_ID, {}):
                    break
                self.assertTrue(handle_quest_answer(ctx))
                self.assertEqual(player["quests"][QUEST_ID]["progress"], 3)
        enemy = next(iter(fight.call_args.args[1].values()))
        self.assertEqual(enemy["stats"], {"hitpoints": 250, "attack": 28, "strength": 28, "defence": 28})
        remaining = player["quest_combat_active_encounters"][QUEST_ID][encounter_id]
        self.assertGreater(remaining, 0)
        self.assertLess(remaining, 250)
        for _ in range(100):
            if encounter_id in player.get("quest_combat_encounters", {}).get(QUEST_ID, ()):
                break
            self.assertTrue(handle_quest_answer(ctx))
            self.assertEqual(player["quests"][QUEST_ID]["progress"], 3)
        self.assertIn(encounter_id, player["quest_combat_encounters"][QUEST_ID])
        self.assertEqual(calls["activity"][-1], "Defeated Poisonous Spider")
        before = copy.deepcopy(player)
        saves = calls["saves"]
        for _ in range(2):
            self.assertFalse(handle_quest_answer(ctx))
            self.assertEqual(player, before)
        self.assertEqual(calls["saves"], saves)
        self.assertIn("Complete Observatory Quest stage 3 objective", calls["errors"][-1][1])
        self.assertFalse(player["quests"][QUEST_ID]["completed"])
        self.assertEqual(player["quest_points"], 0)

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
        self.assertEqual(second["required_actions"], ())
        self.assertEqual(second["auto_actions"], MATERIAL_ACTIONS)
        for key in ("required_tools", "consumed_inventory", "produced_inventory"):
            self.assertFalse(second[key])

    def test_answer_card_save_reopen_undo_and_rereview_restore_whole_state(self):
        original_modules = dict(sys.modules)
        rng_state = random.getstate()
        try:
            random.seed(5706277)
            _install_runtime_fakes()
            addon = _load_addon_as_package("ankiscape_observatory_e2e")
            collection = _DummyCol({"ankiscape_floating_xp_enabled": False})
            collection.set_config = lambda key, value: collection._store.__setitem__(key, copy.deepcopy(value))
            addon.mw = _DummyMW(collection)
            storage = sys.modules[f"{addon.__name__}.core.storage"]
            storage.mw = addon.mw
            addon.storage_save_player_data = storage.save_player_data
            addon.storage_load_player_data = storage.load_player_data
            addon.ui.update_menu_visibility = lambda _skill: None
            addon.show_error_message = lambda *_args: None
            addon._show_activity_gain = lambda _text: None
            addon._show_exp = lambda _amount: None
            addon.update_review_hud = lambda *_args: None
            addon._state.player_data = _player()
            addon._state.current_skill = "Quests"
            addon._state.review_undo_stack.clear()
            addon.save_player_data()
            addon.load_player_data()
            before = copy.deepcopy(addon._state.player_data)
            _answer_review(addon)
            after = copy.deepcopy(addon._state.player_data)
            self.assertEqual(collection.get_config("ankiscape_player_data"), after)
            self.assertEqual(after["quests"][QUEST_ID], {"started": True, "progress": 2, "completed": False})
            self.assertEqual(after["quest_action_proofs"], sorted(OPENING_ACTIONS))
            self.assertEqual(after["inventory"], before["inventory"])
            self.assertEqual(after["equipment"], before["equipment"])
            self.assertEqual(after["quest_points"], before["quest_points"])
            addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
            self.assertEqual(addon._state.player_data, before)
            self.assertEqual(collection.get_config("ankiscape_player_data"), before)
            addon._state.current_skill = "Quests"
            _answer_review(addon)
            self.assertEqual(addon._state.player_data, after)
            addon._state.player_data["inventory"].update(MATERIALS)
            addon.save_player_data()
            addon.load_player_data()
            material_before = copy.deepcopy(addon._state.player_data)
            addon._state.card_turned = addon._state.answer_shown = True
            addon._state.exp_awarded = False
            addon.on_answer_card(_FakeReviewer(), 1, lambda _self, _ease: "answered")
            unsuccessful = addon._state.player_data
            for key in ("quests", "quest_action_proofs", "inventory", "equipment", "action_telemetry"):
                self.assertEqual(unsuccessful[key], material_before[key])
            addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
            self.assertEqual(addon._state.player_data, material_before)
            _answer_review(addon)
            material_after = copy.deepcopy(addon._state.player_data)
            self.assertEqual(material_after["quests"][QUEST_ID], {"started": True, "progress": 3, "completed": False})
            self.assertEqual(material_after["quest_action_proofs"], sorted(OPENING_ACTIONS + MATERIAL_ACTIONS))
            for key in ("inventory", "equipment", "quest_points", "pending_skill_exp_rewards"):
                self.assertEqual(material_after[key], material_before[key])
            self.assertEqual(collection.get_config("ankiscape_player_data"), material_after)
            addon._state.player_data = {}
            addon.load_player_data()
            self.assertEqual(addon._state.player_data, material_after)
            self.assertEqual(addon._state.current_skill, "Quests")
            addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
            self.assertEqual(addon._state.player_data, material_before)
            self.assertEqual(collection.get_config("ankiscape_player_data"), material_before)
            _answer_review(addon)
            self.assertEqual(addon._state.player_data, material_after)
            self.assertEqual(collection.get_config("ankiscape_player_data"), material_after)
        finally:
            random.setstate(rng_state)
            sys.modules.clear()
            sys.modules.update(original_modules)
