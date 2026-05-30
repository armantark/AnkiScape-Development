import sys
import types
import unittest
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from pathlib import Path

# --- Minimal fakes for Anki runtime ---
class _FakeHooks:
    def __init__(self):
        # Lists emulate VS Code/Anki gui_hooks collections with append/remove
        self.overview_did_refresh = []
        self.overview_will_refresh = []
        self.reviewer_did_show_question = []
        self.reviewer_did_show_answer = []
        self.webview_did_receive_js_message = []
        self.state_did_undo = []

class _FakeReviewer:
    def _answerCard(self, ease):
        return None

class _DummyCol:
    def __init__(self, store=None):
        self._store = dict(store or {})
    def get_config(self, key, default=None):
        return self._store.get(key, default)
    def set_config(self, key, value):
        self._store[key] = value

class _DummyMW:
    def __init__(self, col):
        self.col = col


def _install_runtime_fakes():
    # aqt base module
    aqt = types.ModuleType("aqt")
    aqt.mw = None
    aqt.gui_hooks = _FakeHooks()

    # aqt.reviewer submodule
    aqt_reviewer = types.ModuleType("aqt.reviewer")
    aqt_reviewer.Reviewer = _FakeReviewer

    # DO NOT provide aqt.qt so ui.py falls back to HAS_QT = False
    sys.modules["aqt"] = aqt
    sys.modules["aqt.reviewer"] = aqt_reviewer

    # anki.hooks module
    anki_hooks = types.ModuleType("anki.hooks")
    def addHook(_name, _fn):
        # No-op for test; registration is validated by addon behavior below
        return None
    def wrap(old, new, _mode):
        def _wrapped(self, ease):
            return new(self, ease, old)
        return _wrapped
    anki_hooks.addHook = addHook
    anki_hooks.wrap = wrap
    sys.modules["anki.hooks"] = anki_hooks


def _load_addon_as_package(mod_name="ankiscape_integration"):
    # Load top-level __init__.py as a package so relative imports (e.g., .hooks) resolve
    root = Path(__file__).resolve().parents[1]
    init_py = root / "__init__.py"
    loader = SourceFileLoader(mod_name, str(init_py))
    spec = spec_from_loader(mod_name, loader, is_package=True)
    mod = module_from_spec(spec)
    # Package modules need a __path__ so relative imports work
    mod.__path__ = [str(root)]  # type: ignore[attr-defined]
    # Ensure the package is discoverable for relative imports during exec_module
    sys.modules[mod_name] = mod
    loader.exec_module(mod)
    return mod


class TestIntegrationSmoke(unittest.TestCase):
    def setUp(self):
        # Isolate sys.modules pollution between tests
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        # Restore sys.modules to avoid interference with other tests
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_hook_flow_and_settings_gating(self):
        addon = _load_addon_as_package()

        # Replace UI/HUD side effects with counters
        calls = {"ensure": 0, "update": 0, "hide": 0, "xp": 0}
        def fake_ensure():
            calls["ensure"] += 1
        def fake_update(_pd=None, _skill=None):
            calls["update"] += 1
        def fake_hide():
            calls["hide"] += 1
        class FakeExpPopup:
            def __init__(self, _mw):
                pass
            def show_exp(self, _n):
                calls["xp"] += 1

        # Patch directly on loaded module (these names are referenced inside __init__.py)
        addon.ensure_review_hud = fake_ensure
        addon.update_review_hud = fake_update
        addon.hide_review_hud = fake_hide
        addon.ExpPopup = FakeExpPopup

        # Provide a dummy mw with default settings ON
        col = _DummyCol(
            {
                "ankiscape_review_hud_enabled": True,
                "ankiscape_floating_xp_enabled": True,
                "ankiscape_popups_enabled": True,
                "ankiscape_floating_enabled": True,
                "ankiscape_floating_position": "right",
            }
        )
        addon.mw = _DummyMW(col)
        # Ensure ui.get_config_bool reads the same mw/col
        try:
            addon.ui.mw = addon.mw  # type: ignore[attr-defined]
        except Exception:
            pass

        # Minimal player state to avoid None paths
        addon.player_data = {
            "inventory": {},
            "mining_level": 1,
            "woodcutting_level": 1,
            "smithing_level": 1,
            "crafting_level": 1,
            "fletching_level": 1,
            "mining_exp": 0,
            "woodcutting_exp": 0,
            "smithing_exp": 0,
            "crafting_exp": 0,
            "fletching_exp": 0,
            "current_ore": "Rune essence",
            "current_tree": "",
            "current_bar": "Bronze bar",
            "current_craft": "",
            "current_fletch": "arrow_shafts",
        }
        addon.current_skill = "Mining"

        calls["good_answer"] = 0
        def fake_good_answer():
            calls["good_answer"] += 1
        addon.on_good_answer = fake_good_answer

        addon.current_skill = "Thieving"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False
        result = addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        self.assertEqual(result, "answered")
        self.assertEqual(calls["good_answer"], 0)

        addon.current_skill = "Fletching"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False
        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        self.assertEqual(calls["good_answer"], 1)

        # With Experience HUD ON, both question/answer events should ensure+update
        addon._on_rev_show_question()
        addon._on_rev_show_answer()
        self.assertGreaterEqual(calls["ensure"], 1)
        self.assertGreaterEqual(calls["update"], 2)

        # Floating XP ON => popup shows once
        addon._show_exp(10)
        self.assertEqual(calls["xp"], 1)

        # Disable Experience HUD: subsequent events should not update HUD
        prev_ensure, prev_update = calls["ensure"], calls["update"]
        addon.mw.col.set_config("ankiscape_review_hud_enabled", False)
        addon._on_rev_show_question()
        addon._on_rev_show_answer()
        self.assertEqual(calls["ensure"], prev_ensure)
        self.assertEqual(calls["update"], prev_update)

        # Disable Floating XP: no additional popup
        addon.mw.col.set_config("ankiscape_floating_xp_enabled", False)
        addon._show_exp(5)
        self.assertEqual(calls["xp"], 1)

        # Navigating away hides HUD regardless of setting
        addon._on_overview_did_refresh(overview=None)
        self.assertGreaterEqual(calls["hide"], 1)

    def test_fletching_answer_updates_inventory_and_exp(self):
        addon = _load_addon_as_package("ankiscape_fletching_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon.player_data = {
            "inventory": {"Tree": 1},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }

        addon.on_fletching_answer()

        self.assertEqual(addon.player_data["inventory"]["Tree"], 0)
        self.assertEqual(addon.player_data["inventory"]["Arrow shafts"], 15)
        self.assertAlmostEqual(addon.player_data["fletching_exp"], 5.0)
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["xp"], [5.0])

    def test_utility_answer_batches_inventory_without_skill_xp(self):
        addon = _load_addon_as_package("ankiscape_utility_integration")

        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon.player_data = {
            "inventory": {"Clay": 3},
            "crafting_exp": 0,
            "current_utility": "make_soft_clay",
            "completed_achievements": [],
        }

        addon.on_utility_answer()

        self.assertEqual(addon.player_data["inventory"]["Clay"], 0)
        self.assertEqual(addon.player_data["inventory"]["Soft clay"], 3)
        self.assertEqual(addon.player_data["crafting_exp"], 0)
        self.assertEqual(calls["save"], 1)

    def test_xp_multiplier_applies_to_gathering_and_processing_rewards(self):
        addon = _load_addon_as_package("ankiscape_xp_multiplier_integration")

        calls = {"save": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_xp_multiplier": 2.0}))

        addon.player_data = {
            "inventory": {},
            "woodcutting_level": 1,
            "woodcutting_exp": 0,
            "current_tree": "Tree",
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }

        original_random = addon.random.random
        addon.random.random = lambda: 0.0
        try:
            addon.on_woodcutting_answer()
            addon.on_fletching_answer()
        finally:
            addon.random.random = original_random

        self.assertEqual(addon.player_data["inventory"]["Tree"], 0)
        self.assertEqual(addon.player_data["inventory"]["Arrow shafts"], 15)
        self.assertAlmostEqual(addon.player_data["woodcutting_exp"], 50.0)
        self.assertAlmostEqual(addon.player_data["fletching_exp"], 10.0)
        self.assertEqual(calls["xp"], [50.0, 10.0])

    def test_bad_xp_multiplier_config_falls_back_to_base_xp(self):
        addon = _load_addon_as_package("ankiscape_bad_xp_multiplier_integration")

        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._show_exp = lambda _exp: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.mw = _DummyMW(_DummyCol({"ankiscape_xp_multiplier": "not-a-number"}))
        addon.player_data = {
            "inventory": {"Tree": 1},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }

        addon.on_fletching_answer()

        self.assertAlmostEqual(addon.player_data["fletching_exp"], 5.0)

    def test_undo_after_review_restores_awarded_game_progress(self):
        addon = _load_addon_as_package("ankiscape_undo_integration")

        calls = {"save": 0, "hud": 0, "xp": []}
        addon.level_up_check = lambda _skill, _data: None
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: calls.__setitem__("hud", calls["hud"] + 1)
        addon._show_exp = lambda exp: calls["xp"].append(exp)
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)

        addon.player_data = {
            "inventory": {"Tree": 1},
            "fletching_level": 1,
            "fletching_exp": 0,
            "current_fletch": "arrow_shafts",
            "completed_achievements": [],
        }
        addon.current_skill = "Fletching"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["inventory"]["Tree"], 0)
        self.assertEqual(addon.player_data["inventory"]["Arrow shafts"], 15)
        self.assertAlmostEqual(addon.player_data["fletching_exp"], 5.0)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data["inventory"], {"Tree": 1})
        self.assertEqual(addon.player_data["fletching_exp"], 0)
        self.assertEqual(addon.player_data["current_fletch"], "arrow_shafts")
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])
        self.assertEqual(calls["xp"], [5.0])
        self.assertGreaterEqual(calls["save"], 2)

    def test_utility_review_reward_rolls_back_on_undo(self):
        addon = _load_addon_as_package("ankiscape_utility_undo_integration")

        calls = {"save": 0}
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: calls.__setitem__("save", calls["save"] + 1)
        addon.update_review_hud = lambda _data, _skill: None
        addon._refresh_skill_availability = lambda: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon.player_data = {
            "inventory": {"Clay": 2},
            "crafting_exp": 0,
            "current_utility": "make_soft_clay",
            "completed_achievements": [],
        }
        addon.current_skill = "Utility / Activities"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False

        addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")

        self.assertEqual(addon.player_data["inventory"], {"Clay": 0, "Soft clay": 2})
        self.assertEqual(addon.player_data["crafting_exp"], 0)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

        changes = types.SimpleNamespace(
            operation="Answer Card",
            changes=types.SimpleNamespace(study_queues=True, card=True),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data["inventory"], {"Clay": 2})
        self.assertEqual(addon.player_data["crafting_exp"], 0)
        self.assertEqual(addon._REVIEW_UNDO_STACK, [])
        self.assertGreaterEqual(calls["save"], 2)

    def test_unrelated_undo_does_not_consume_review_snapshot(self):
        addon = _load_addon_as_package("ankiscape_unrelated_undo_integration")

        addon.save_player_data = lambda: self.fail("unrelated undo should not save")
        addon.player_data = {
            "inventory": {"Tree": 0, "Arrow shafts": 15},
            "fletching_level": 1,
            "fletching_exp": 5.0,
            "current_fletch": "arrow_shafts",
        }
        addon._REVIEW_UNDO_STACK.append(
            {
                "values": {"inventory": {"Tree": 1}, "fletching_exp": 0},
                "remove": [],
            }
        )

        changes = types.SimpleNamespace(
            operation="Edit Note",
            changes=types.SimpleNamespace(study_queues=False, card=False),
        )
        addon._on_state_did_undo(changes)

        self.assertEqual(addon.player_data["inventory"]["Arrow shafts"], 15)
        self.assertEqual(addon.player_data["fletching_exp"], 5.0)
        self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)


if __name__ == "__main__":
    unittest.main()
