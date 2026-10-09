"""The complete Blood Pact opening is narration before held combat."""

import copy
import json
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.data.quest_action_proof_data import QUEST_ACTION_PROOF_RULES
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from ankiscape.logic_pure import quest_action_proofs
from ankiscape.logic_pure.logic_pure_telemetry import (
    record_action_telemetry_pure, record_achievement_progress_pure,
)
from ankiscape.runtime.runtime_actions import handle_quest_answer
from tests.test_combat_quest_gate import _answer_review
from tests.test_integration_smoke import (
    _DummyCol, _DummyMW, _FakeReviewer, _install_runtime_fakes, _load_addon_as_package,
)
from tests.test_runtime_actions import _context


QUEST_ID = "the_blood_pact"
OPENING_ACTIONS = (
    "Agree to help Xenia rescue Ilona from the Zamorakian cultists in the Lumbridge graveyard.",
    "Enter the Lumbridge Catacombs with Xenia.",
    "Watch Reese, Caitlin and Kayle take Ilona deeper into the dungeon; Reese invokes the blood pact and orders Kayle to guard the door.",
    "Proceed north into the front chamber, where Kayle stands opposite you.",
    "Kayle injures Xenia with his sling.",
    "Xenia asks you to fight on alone and defeat the cultists.",
)
RESOURCE_KEYS = (
    "inventory", "equipment", "carried_inventory", "carried_layout", "combat_lifepoints",
    "combat_prayer_points", "combat_supply_loadout", "quest_points", "pending_skill_exp_rewards",
    "music_log",
)


def _player():
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player.update(current_quest=QUEST_ID, combat_lifepoints=73, combat_prayer_points=7)
    player["inventory"].update({"Coins": 137, "Tinderbox": 1, "Bronze sword": 1, "Lobster": 4})
    player["equipment"]["weapon"] = "Bronze sword"
    player["carried_inventory"] = {"bankstanding": {"Lobster": 2}}
    player["carried_layout"] = {"bankstanding": {"Lobster": 2}}
    player["combat_supply_loadout"]["food"] = {"Lobster": 2}
    player["quest_action_proofs"] = ["Unrelated retained proof"]
    record_action_telemetry_pure(player, "quest", "cooks_assistant", True, expected_success_chance=1.0)
    record_achievement_progress_pure(player, "quest", "cooks_assistant", True)
    return migrate_loaded_data(player, ORE_DATA, ITEM_DEFINITIONS)


def _resources(player):
    return {key: copy.deepcopy(value) for key, value in player.items()
            if key in RESOURCE_KEYS or key.endswith(("_exp", "_level"))}


class _SavedCollection(_DummyCol):
    def get_config(self, key, default=None):
        return copy.deepcopy(super().get_config(key, default))

    def set_config(self, key, value):
        self._store[key] = json.loads(json.dumps(value))


class BloodPactOpeningTest(unittest.TestCase):
    def test_one_review_records_complete_ordered_opening_without_resource_effects(self):
        player = _player()
        before = copy.deepcopy(player)
        resources = _resources(player)
        calls = {"xp": [], "saves": 0, "errors": []}
        with patch.object(
            quest_action_proofs, "quest_action_proofs_after_event_pure",
            wraps=quest_action_proofs.quest_action_proofs_after_event_pure,
        ) as events:
            self.assertTrue(handle_quest_answer(_context(player, calls)))
        self.assertEqual(
            [call.args[2] for call in events.call_args_list if call.args[1] == "quest_stage"],
            [f"{QUEST_ID}:{action}" for action in OPENING_ACTIONS],
        )
        self.assertEqual(player["quests"][QUEST_ID], {"started": True, "progress": 2, "completed": False})
        self.assertEqual(player["quest_action_proofs"], sorted((*OPENING_ACTIONS, "Unrelated retained proof")))
        self.assertEqual(_resources(player), resources)
        self.assertEqual(
            {key for key in player if player[key] != before.get(key)},
            {"quests", "quest_action_proofs", "achievement_progress", "action_telemetry"},
        )
        self.assertEqual(set(player), set(before))
        progress = copy.deepcopy(player["achievement_progress"])
        self.assertEqual(progress["skills"]["quest"]["actions"].pop(QUEST_ID), 1)
        self.assertEqual(progress, before["achievement_progress"])
        telemetry = copy.deepcopy(player["action_telemetry"])
        self.assertEqual(telemetry["actions"].pop(f"quest:{QUEST_ID}"), {
            "skill_id": "quest", "action_id": QUEST_ID,
            "attempts": 1, "successes": 1, "failures": 0, "expected_successes": 1.0,
            "current_dry_streak": 0, "longest_dry_streak": 0, "outputs": {},
            "failure_kinds": {}, "last_success": True, "last_expected_success_chance": 1.0,
        })
        self.assertEqual(telemetry, before["action_telemetry"])
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["saves"], 1)
        held = copy.deepcopy(player)
        for _ in range(2):
            self.assertFalse(handle_quest_answer(_context(player)))
            self.assertEqual(player, held)

    def test_journal_and_later_stage_contracts_retain_the_combat_boundary(self):
        quest = QUEST_DATA[QUEST_ID]
        generated = next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == QUEST_ID)
        self.assertEqual(quest["journal_stages"][1], OPENING_ACTIONS)
        for stage in generated["journal_stages"]:
            if stage["stage"] > 1:
                self.assertEqual(quest["journal_stages"][stage["stage"]], stage["journal"])
        self.assertEqual(quest["journal_stages"][2][0], "Defeat Kayle.")
        self.assertEqual(quest["stages"], 4)
        self.assertNotIn(4, quest["journal_stages"])
        for action in OPENING_ACTIONS:
            self.assertNotIn(("quest_stage", f"{QUEST_ID}:{action}"), QUEST_ACTION_PROOF_RULES)

    def test_saved_opening_reopens_and_genuine_review_undo_restores_proofs(self):
        original_modules = dict(sys.modules)
        try:
            _install_runtime_fakes()
            addon = _load_addon_as_package("ankiscape_blood_pact_e2e")
            col = _SavedCollection({"ankiscape_floating_xp_enabled": False})
            addon.mw = _DummyMW(col)
            sys.modules[f"{addon.__name__}.core.storage"].mw = addon.mw
            addon._state.player_data = _player()
            addon._state.current_skill = "Quests"
            addon._state.review_undo_stack.clear()
            addon.save_player_data()
            addon.load_player_data()
            before = copy.deepcopy(addon._state.player_data)
            _answer_review(addon)
            saved = col.get_config("ankiscape_player_data")
            self.assertEqual(saved["quests"][QUEST_ID]["progress"], 2)
            self.assertEqual(saved["quest_action_proofs"], sorted((*OPENING_ACTIONS, "Unrelated retained proof")))
            self.assertEqual(_resources(saved), _resources(before))
            addon.load_player_data()
            self.assertEqual(addon._state.player_data["quests"][QUEST_ID], saved["quests"][QUEST_ID])
            self.assertEqual(addon._state.player_data["quest_action_proofs"], saved["quest_action_proofs"])
            self.assertEqual(_resources(addon._state.player_data), _resources(before))
            addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
            self.assertEqual(addon._state.player_data["quests"][QUEST_ID], before["quests"][QUEST_ID])
            self.assertEqual(addon._state.player_data["quest_action_proofs"], before["quest_action_proofs"])
            self.assertEqual(_resources(addon._state.player_data), _resources(before))
            addon.load_player_data()
            self.assertEqual(addon._state.player_data["quests"][QUEST_ID], before["quests"][QUEST_ID])
            self.assertEqual(addon._state.player_data["quest_action_proofs"], before["quest_action_proofs"])
            addon._state.current_skill = "Quests"
            _answer_review(addon)
            self.assertEqual(addon._state.player_data["quests"][QUEST_ID]["progress"], 2)
        finally:
            sys.modules.clear()
            sys.modules.update(original_modules)

    def test_unsuccessful_review_leaves_opening_unstarted(self):
        original_modules = dict(sys.modules)
        try:
            _install_runtime_fakes()
            addon = _load_addon_as_package("ankiscape_blood_pact_failed_e2e")
            col = _SavedCollection({"ankiscape_floating_xp_enabled": False})
            addon.mw = _DummyMW(col)
            sys.modules[f"{addon.__name__}.core.storage"].mw = addon.mw
            addon._state.player_data = _player()
            addon._state.current_skill = "Quests"
            addon.save_player_data()
            addon.load_player_data()
            before = copy.deepcopy(addon._state.player_data)
            addon._state.card_turned = True
            addon._state.answer_shown = True
            addon._state.exp_awarded = False
            addon.on_answer_card(_FakeReviewer(), 1, lambda _self, _ease: "answered")
            self.assertEqual(addon._state.player_data["quests"][QUEST_ID], before["quests"][QUEST_ID])
            self.assertEqual(addon._state.player_data["quest_action_proofs"], before["quest_action_proofs"])
            self.assertEqual(_resources(addon._state.player_data), _resources(before))
        finally:
            sys.modules.clear()
            sys.modules.update(original_modules)
