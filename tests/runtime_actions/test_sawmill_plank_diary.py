"""The paid normal-log conversion is the sawmill deed of Plank You Very Much."""

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.logic import check_achievements
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.logic.achievement_diary_logic import diary_tier_by_id_pure, tier_claim_state_pure
from ankiscape.logic.shop_logic import apply_shop_buy_pure
from ankiscape.runtime.runtime_actions import (
    handle_magic_answer,
    handle_thieving_answer,
    handle_utility_answer,
    handle_woodcutting_answer,
)
from tests.test_achievement_diary_ledger_wiring import _runtime_context
from tests.test_combat_quest_gate import _answer_review
from tests.test_integration_smoke import (
    _DummyCol, _DummyMW, _install_runtime_fakes, _load_addon_as_package,
)
from tests.test_magic import _quest_state


TASK_ID = "varrock_easy_plank_you_very_much"
CONVERSION = "convert_logs_to_planks"


class _JsonCollection(_DummyCol):
    def __init__(self, directory):
        super().__init__()
        self.path = Path(directory) / "config.json"
        self.path.write_text("{}", encoding="utf-8")

    def get_config(self, key, default=None):
        return json.loads(self.path.read_text(encoding="utf-8")).get(key, default)

    def set_config(self, key, value):
        values = json.loads(self.path.read_text(encoding="utf-8"))
        values[key] = value
        self.path.write_text(json.dumps(values), encoding="utf-8")


class SawmillPlankDiaryTest(unittest.TestCase):
    def setUp(self):
        popups = patch("ankiscape.core.logic._popups_enabled", return_value=False)
        popups.start()
        self.addCleanup(popups.stop)

    def _review(self, handler, player, rolls=()):
        errors = []
        ok = handler(_runtime_context(player, errors, rolls))
        self.assertEqual(errors, [])
        return ok

    def _pickpocket(self, player, times):
        player["current_thieving"] = "pickpocket_man"
        for _ in range(times):
            # The first roll succeeds; the high rest keep Shattered Heart from replacing coins.
            self.assertTrue(self._review(handle_thieving_answer, player, (0.0,) + (0.99,) * 7))

    def _chop_log(self, player):
        player["current_tree"] = "tree"
        self.assertTrue(self._review(handle_woodcutting_answer, player, (0.0,) + (0.99,) * 8))
        player["current_utility"] = CONVERSION

    def _earned_player(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        self._pickpocket(player, 39)
        self.assertEqual(player["inventory"]["Coins"], 117)
        player, result = apply_shop_buy_pure(player, "bobs_brilliant_axes", "bobs_brilliant_axes:0:1351")
        self.assertTrue(result["allowed"], result)
        self.assertEqual(player["inventory"]["Bronze hatchet"], 1)
        self._chop_log(player)
        self.assertEqual((player["inventory"]["Logs"], player["inventory"]["Coins"]), (1, 101))
        return player

    @staticmethod
    def _completions(player):
        return player.get("achievement_diaries", {}).get("completed_tasks", []).count(TASK_ID)

    @staticmethod
    def _deed_count(player):
        _family, tier = diary_tier_by_id_pure("varrock_easy")
        task = next(task for task in tier.tasks if task.id == TASK_ID)
        token = task.conditions[0].key.rsplit(".", 1)[-1]
        return player["achievement_diaries"]["event_counts"].get(token, 0)

    @staticmethod
    def _materials(player):
        return {item: player["inventory"].get(item, 0) for item in ("Logs", "Coins", "Plank")}

    def test_earned_paid_conversion_completes_the_deed_once_and_keeps_the_plank(self):
        player = self._earned_player()
        self.assertEqual(self._completions(player), 0)
        self.assertTrue(self._review(handle_utility_answer, player))
        self.assertEqual(self._materials(player), {"Logs": 0, "Coins": 1, "Plank": 1})
        self.assertEqual(self._completions(player), 1)
        self.assertEqual(self._deed_count(player), 1)

        self._pickpocket(player, 33)
        self._chop_log(player)
        self.assertTrue(self._review(handle_utility_answer, player))
        self.assertEqual(self._materials(player), {"Logs": 0, "Coins": 0, "Plank": 2})
        self.assertEqual(self._completions(player), 1)
        self.assertEqual(self._deed_count(player), 1)
        family, tier = diary_tier_by_id_pure("varrock_easy")
        claim = tier_claim_state_pure(player, family, tier)
        self.assertEqual((claim["done"], claim["ready"]), (1, False))

    def test_refusal_for_a_missing_input_moves_nothing_and_resumes_on_the_earned_input(self):
        # Negative fixtures: each case removes one earned input before the conversion review.
        cases = (("Coins", 2, lambda p: self._pickpocket(p, 1)), ("Logs", 1, self._chop_log))
        for missing, removed, earn in cases:
            with self.subTest(missing=missing):
                player = self._earned_player()
                player["inventory"][missing] -= removed
                inventory = dict(player["inventory"])
                diary = json.dumps(player["achievement_diaries"], sort_keys=True)
                self.assertFalse(self._review(handle_utility_answer, player))
                self.assertEqual(player["inventory"], inventory)
                self.assertEqual(json.dumps(player["achievement_diaries"], sort_keys=True), diary)
                self.assertNotIn(f"utility:{CONVERSION}", player["action_telemetry"]["actions"])
                earn(player)
                player["current_utility"] = CONVERSION
                self.assertTrue(self._review(handle_utility_answer, player))
                self.assertEqual(self._completions(player), 1)

    def test_other_plank_methods_and_old_records_give_no_credit(self):
        # Negative fixtures: seeded inputs for methods that must not count as the sawmill deed.
        for wood, fee in (("Oak", 250), ("Teak", 500), ("Mahogany", 1500)):
            with self.subTest(wood=wood):
                player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
                player["current_utility"] = f"convert_{wood.lower()}_logs_to_{wood.lower()}_planks"
                player["inventory"].update({f"{wood} logs": 1, "Coins": fee})
                self.assertTrue(self._review(handle_utility_answer, player))
                self.assertEqual(player["inventory"][f"{wood} plank"], 1)
                self.assertEqual(self._completions(player), 0)

        spell = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        spell.update(magic_level=99, current_magic="plank_make_logs")
        spell["quests"].update(_quest_state("dream_mentor"))
        spell["inventory"].update(
            {"Astral rune": 2, "Nature rune": 1, "Earth rune": 15, "Coins": 70, "Logs": 1}
        )
        self.assertTrue(self._review(handle_magic_answer, spell, (0.99,) * 8))
        self.assertEqual(spell["inventory"]["Plank"], 1)

        old = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        old["inventory"]["Plank"] = 5
        old["achievement_progress"] = {
            "skills": {"utility": {"actions": {CONVERSION: 5}, "outputs": {"Plank": 5}}}
        }
        old["action_telemetry"]["actions"][f"utility:{CONVERSION}"] = {
            "skill_id": "utility", "action_id": CONVERSION,
            "attempts": 5, "successes": 5, "outputs": {"Plank": 5},
        }
        check_achievements(old)
        reloaded = migrate_loaded_data(json.loads(json.dumps(old)), ORE_DATA, ITEM_DEFINITIONS)
        check_achievements(reloaded)
        for player in (spell, old, reloaded):
            self.assertEqual(self._completions(player), 0)

    def test_saved_review_round_trips_through_json_and_undo_then_replay_credits_once(self):
        player = self._earned_player()
        original_modules = dict(sys.modules)
        try:
            _install_runtime_fakes()
            directory = TemporaryDirectory()
            self.addCleanup(directory.cleanup)
            collection = _JsonCollection(directory.name)
            sys.modules["aqt"].mw = _DummyMW(collection)
            addon = _load_addon_as_package("ankiscape_sawmill_plank_diary")
            package = addon.__name__
            addon._refresh_skill_availability = lambda: None
            addon._show_activity_gain = lambda _text: None
            addon.update_review_hud = lambda *_args: None
            addon._state.player_data = player
            addon._state.current_skill = "Utilities"
            addon._state.review_undo_stack.clear()
            with (
                patch.object(sys.modules[f"{package}.core.logic"], "_popups_enabled", return_value=False),
                patch.object(addon.random, "random", return_value=0.99),
            ):
                _answer_review(addon)
                loaded, skill = addon.storage_load_player_data()
                self.assertEqual(skill, "Utilities")
                self.assertEqual(self._completions(loaded), 1)
                self.assertEqual(self._deed_count(loaded), 1)
                self.assertEqual(self._materials(loaded), {"Logs": 0, "Coins": 1, "Plank": 1})

                addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
                restored = addon._state.player_data
                self.assertEqual(self._completions(restored), 0)
                self.assertEqual(self._deed_count(restored), 0)
                self.assertEqual(self._materials(restored), {"Logs": 1, "Coins": 101, "Plank": 0})
                undone, _skill = addon.storage_load_player_data()
                self.assertEqual(self._completions(undone), 0)
                self.assertEqual(self._materials(undone), self._materials(restored))

                _answer_review(addon)
            replayed, _skill = addon.storage_load_player_data()
            self.assertEqual(self._completions(replayed), 1)
            self.assertEqual(self._deed_count(replayed), 1)
            self.assertEqual(self._materials(replayed), {"Logs": 0, "Coins": 1, "Plank": 1})
        finally:
            sys.modules.clear()
            sys.modules.update(original_modules)


if __name__ == "__main__":
    unittest.main()
