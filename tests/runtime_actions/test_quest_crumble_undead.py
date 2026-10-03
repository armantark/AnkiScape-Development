"""The first Boneguard cast must finish the quest deed through a real review."""

import copy
from itertools import product
import sys
from types import SimpleNamespace
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import MAGIC_DATA, MAGIC_ITEM_IMAGES, QUEST_DATA
from ankiscape.core.target_metadata import magic_target_rows
from ankiscape.logic_pure.logic_pure_quest import quest_current_stage_blockers_pure
from ankiscape.runtime.runtime_actions import handle_magic_answer
from tests.test_combat_quest_gate import _answer_review, _maxed_player_for_quest
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package
from tests.test_magic import _context


TARGET = "crumble_undead_first_boneguard"
PROOF = "Cast Crumble Undead during the boneguard fight"
OBSTACLE = "enakhras_lament_first_boneguard_crumbled"


def _player():
    player = _maxed_player_for_quest("enakhras_lament")
    player["quests"]["enakhras_lament"] = {
        "started": True, "progress": 5, "completed": False,
    }
    player["current_magic"] = TARGET
    player["current_quest"] = "enakhras_lament"
    player["magic_level"] = 39
    player["inventory"] = {"Air rune": 2, "Earth rune": 2, "Chaos rune": 1, "Candle": 1}
    return player


class QuestCrumbleUndeadTest(unittest.TestCase):
    def test_review_transforms_first_boneguard_records_required_deed_and_undo_restores_cast(self):
        original_modules = dict(sys.modules)
        try:
            _install_runtime_fakes()
            addon = _load_addon_as_package("ankiscape_crumble_undead_e2e")
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
            addon._state.player_data = player
            addon._state.current_skill = "Magic"
            addon._state.review_undo_stack.clear()
            before_inventory = copy.deepcopy(player["inventory"])
            self.assertFalse(player.get("quest_action_proofs"))
            self.assertIn(PROOF, {b.get("action_id") for b in quest_current_stage_blockers_pure(player, "enakhras_lament", QUEST_DATA)})

            _answer_review(addon)

            after = addon._state.player_data
            self.assertTrue(after.get(OBSTACLE))
            self.assertIn(PROOF, after.get("quest_action_proofs", ()))
            self.assertEqual({r: after["inventory"][r] for r in ("Air rune", "Earth rune", "Chaos rune")}, {"Air rune": 0, "Earth rune": 0, "Chaos rune": 0})
            self.assertGreater(after["inventory"].get("Big bones", 0), 0)
            self.assertNotIn(PROOF, {b.get("action_id") for b in quest_current_stage_blockers_pure(after, "enakhras_lament", QUEST_DATA)})
            self.assertIn(PROOF, saved[-1]["quest_action_proofs"])
            self.assertEqual(after["quests"]["enakhras_lament"]["progress"], 5)
            addon._state.current_skill = "Quests"
            _answer_review(addon)
            advanced = addon._state.player_data
            self.assertEqual(advanced["quests"]["enakhras_lament"]["progress"], 6, errors)
            self.assertEqual(advanced["quest_action_proofs"], [PROOF])
            addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
            returned = addon._state.player_data
            self.assertEqual(returned["quests"]["enakhras_lament"]["progress"], 5)
            self.assertEqual(returned["inventory"], after["inventory"])
            self.assertEqual(returned["quest_action_proofs"], [PROOF])
            addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
            restored = addon._state.player_data
            self.assertEqual(restored["inventory"], before_inventory)
            self.assertNotIn(PROOF, restored.get("quest_action_proofs", ()))
            self.assertFalse(restored.get(OBSTACLE))
        finally:
            sys.modules.clear()
            sys.modules.update(original_modules)

    def test_missing_level_or_each_rune_refuses_without_consumption_or_proof(self):
        for missing in ("level", "Air rune", "Earth rune", "Chaos rune"):
            with self.subTest(missing=missing):
                player = _player()
                if missing == "level":
                    player["magic_level"] = 38
                else:
                    player["inventory"][missing] -= 1
                before = copy.deepcopy(player["inventory"])
                calls = {"errors": [], "saves": 0, "shown_xp": []}
                self.assertFalse(handle_magic_answer(_context(player, calls)))
                self.assertEqual(player["inventory"], before)
                self.assertNotIn(PROOF, player.get("quest_action_proofs", ()))
                self.assertFalse(player.get(OBSTACLE))

    def test_wrong_stage_or_already_crumbled_refuses(self):
        for (stage, crumbled), cadence in product(((4, False), (6, False), (5, True)), (False, True)):
            with self.subTest(stage=stage, crumbled=crumbled, cadence=cadence):
                player = _player()
                player["quests"]["enakhras_lament"]["progress"] = stage
                calls = {"errors": [], "saves": 0, "shown_xp": []}
                ctx = _context(player, calls)
                ctx.cadence_live_enabled = cadence
                ctx.switch_to_bankstanding = lambda _reason=None: calls.__setitem__("bankstanding", True)
                if crumbled:
                    for rune in ("Air rune", "Earth rune", "Chaos rune"):
                        player["inventory"][rune] *= 2
                    self.assertTrue(handle_magic_answer(ctx))
                    self.assertTrue(player[OBSTACLE])
                    self.assertIn(PROOF, player["quest_action_proofs"])
                before = copy.deepcopy(player)
                self.assertFalse(handle_magic_answer(ctx))
                self.assertTrue(calls.get("deactivated"))
                self.assertFalse(calls.get("bankstanding"))
                self.assertEqual(player, before)

    def test_unrelated_cast_does_not_transform_or_emit(self):
        player = _player()
        player["current_magic"] = "telegrab_wine_of_zamorak"
        player["inventory"]["Law rune"] = 1
        calls = {"errors": [], "saves": 0, "shown_xp": []}
        self.assertTrue(handle_magic_answer(_context(player, calls)))
        self.assertEqual(player["inventory"]["Wine of zamorak"], 1)
        self.assertNotIn(PROOF, player.get("quest_action_proofs", ()))
        self.assertFalse(player.get(OBSTACLE))

    def test_existing_magic_list_offers_cast_and_locks_missing_runes(self):
        player = _player()
        row = next(r for r in magic_target_rows(player, MAGIC_DATA, MAGIC_ITEM_IMAGES, TARGET, {}) if r.target_id == TARGET)
        self.assertTrue(row.enabled)
        self.assertIsNotNone(row.icon_path)
        player["inventory"]["Chaos rune"] = 0
        row = next(r for r in magic_target_rows(player, MAGIC_DATA, MAGIC_ITEM_IMAGES, TARGET, {}) if r.target_id == TARGET)
        self.assertFalse(row.enabled)
        self.assertIn("Chaos rune x1", row.locked_reasons)
