"""Dimintheis replacement, rather than the original reward, earns Hand-Me-Downs."""

import copy
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic.achievement_diary_logic import diary_tier_by_id_pure, tier_claim_state_pure
from ankiscape.runtime.runtime_actions import handle_quest_answer
from tests.runtime_actions.test_sawmill_plank_diary import _JsonCollection
from tests.test_achievement_diary_ledger_wiring import _runtime_context
from tests.test_integration_smoke import _DummyMW, _install_runtime_fakes, _load_addon_as_package


TASK_ID = "varrock_hard_hand_me_downs"


class FamilyGauntletDiaryTest(unittest.TestCase):
    def setUp(self):
        self.original_modules = dict(sys.modules)
        _install_runtime_fakes()
        self.addCleanup(self._restore_modules)
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.collection = _JsonCollection(directory.name)
        sys.modules["aqt"].mw = _DummyMW(self.collection)
        self.addon = _load_addon_as_package("ankiscape_family_gauntlet_diary")
        addon = self.addon
        addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        addon._state.current_skill = "Bankstanding"
        addon._state.direct_action_undo_stack.clear()
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _text: None
        addon.update_review_hud = lambda *_args: None
        popups = patch.object(sys.modules[f"{addon.__name__}.core.logic"], "_popups_enabled", return_value=False)
        popups.start()
        self.addCleanup(popups.stop)
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon._on_main_menu(initial_skill="Bank")
        self.command = captured["on_cooking_gauntlets_command"]

    def _restore_modules(self):
        sys.modules.clear()
        sys.modules.update(self.original_modules)

    @staticmethod
    def _completions(player):
        return player["achievement_diaries"]["completed_tasks"].count(TASK_ID)

    @staticmethod
    def _deed_count(player):
        _family, tier = diary_tier_by_id_pure("varrock_hard")
        task = next(task for task in tier.tasks if task.id == TASK_ID)
        token = task.conditions[0].key.rsplit(".", 1)[-1]
        return player["achievement_diaries"]["event_counts"].get(token, 0)

    def _earn_pair(self):
        player = self.addon._state.player_data
        # Prepared skill/material fixture; quest progress, proofs and gauntlets are earned below.
        player.update(current_quest="family_crest", crafting_level=40, mining_level=40,
                      smithing_level=40, magic_level=59, attack_level=99, strength_level=99,
                      defense_level=99, constitution_level=99)
        player["inventory"].update({"Shrimps": 1, "Salmon": 1, "Tuna": 1, "Bass": 1,
                                    "Swordfish": 1, "Ruby": 2, "Antipoison (4)": 1, "Shark": 20})
        player["equipment"]["weapon"] = "Abyssal whip"
        errors = []
        for _ in range(300):
            if player["quests"]["family_crest"]["completed"]:
                break
            self.assertTrue(handle_quest_answer(_runtime_context(player, errors, (0.5,) * 100)))
        self.assertTrue(player["quests"]["family_crest"]["completed"])
        self.assertEqual([title for title, _message in errors], ["Quest complete"])
        self.assertEqual(player["inventory"]["Family gauntlets"], 1)
        self.assertEqual(self._completions(player), 0)
        return player

    def test_earned_pair_and_conversion_do_not_count_but_recovery_counts_once(self):
        player = self._earn_pair()
        self.assertTrue(self.command("convert", {"item_name": "Family gauntlets"})["ok"])
        self.assertEqual(player["inventory"]["Cooking gauntlets"], 1)
        self.assertEqual(self._completions(player), 0)
        for _ in range(2):
            self.assertTrue(self.addon.on_discard_item("Cooking gauntlets", 1))
            self.assertTrue(self.command("recover")["ok"])
            self.assertEqual(player["inventory"]["Cooking gauntlets"], 1)
            self.assertEqual(self._completions(player), 1)
            self.assertEqual(self._deed_count(player), 1)
        family, tier = diary_tier_by_id_pure("varrock_hard")
        self.assertFalse(tier_claim_state_pure(player, family, tier)["ready"])

    def test_uncompleted_quest_and_any_owned_pair_refuse_without_writes(self):
        player = self.addon._state.player_data
        before = copy.deepcopy(player)
        self.assertFalse(self.command("recover")["ok"])
        self.assertEqual(player, before)
        self.assertEqual(self.addon._state.direct_action_undo_stack, [])
        player["quests"]["family_crest"] = {"started": True, "progress": 16, "completed": True}
        for item in ("Family gauntlets", "Cooking gauntlets", "Goldsmith gauntlets", "Chaos gauntlets"):
            for worn in (False, True):
                with self.subTest(item=item, worn=worn):
                    player["inventory"] = {} if worn else {item: 1}
                    player["equipment"] = {"hands": item} if worn else {}
                    before = copy.deepcopy(player)
                    self.assertFalse(self.command("recover")["ok"])
                    self.assertEqual(player, before)
                    self.assertEqual(self.addon._state.direct_action_undo_stack, [])
        self.assertEqual(self.collection.path.read_text(), "{}")

    def test_recovery_without_an_anki_undo_entry_is_atomic(self):
        player = self._earn_pair()
        self.assertTrue(self.addon.on_discard_item("Family gauntlets", 1))
        before = copy.deepcopy(player)
        saved = self.collection.path.read_text()
        with patch.object(self.collection, "add_custom_undo_entry", side_effect=RuntimeError("refused")):
            self.assertFalse(self.command("recover")["ok"])
        self.assertEqual(player, before)
        self.assertEqual(self.collection.path.read_text(), saved)

    def test_json_save_undo_and_replay_restore_the_whole_transaction(self):
        player = self._earn_pair()
        self.assertTrue(self.addon.on_discard_item("Family gauntlets", 1))
        # A reload of the genuinely completed quest and lost pair gives no retrospective credit.
        before, _skill = self.addon.storage_load_player_data()
        self.addon._state.player_data = before
        self.addon.check_achievements(before)
        self.assertEqual(self._completions(before), 0)
        self.assertTrue(self.command("recover")["ok"])
        recovered, _skill = self.addon.storage_load_player_data()
        self.assertEqual(recovered["inventory"]["Family gauntlets"], 1)
        self.assertEqual(self._completions(recovered), 1)
        self.assertEqual(self._deed_count(recovered), 1)
        self.addon._on_state_did_undo(SimpleNamespace(operation="AnkiScape direct action"))
        undone, _skill = self.addon.storage_load_player_data()
        self.assertEqual(undone, before)
        self.assertEqual(self._deed_count(undone), 0)
        self.assertTrue(self.command("recover")["ok"])
        replayed, _skill = self.addon.storage_load_player_data()
        self.assertEqual(replayed, recovered)


if __name__ == "__main__":
    unittest.main()
