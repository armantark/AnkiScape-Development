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
            "mining_exp": 0,
            "woodcutting_exp": 0,
            "smithing_exp": 0,
            "crafting_exp": 0,
            "current_ore": "Rune essence",
            "current_tree": "",
            "current_bar": "Bronze bar",
            "current_craft": "",
        }
        addon.current_skill = "Mining"

        calls["good_answer"] = 0
        def fake_good_answer():
            calls["good_answer"] += 1
        addon.on_good_answer = fake_good_answer

        addon.current_skill = "Fletching"
        addon.card_turned = True
        addon.answer_shown = True
        addon.exp_awarded = False
        result = addon.on_answer_card(_FakeReviewer(), 4, lambda _self, _ease: "answered")
        self.assertEqual(result, "answered")
        self.assertEqual(calls["good_answer"], 0)

        addon.current_skill = "Mining"
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


if __name__ == "__main__":
    unittest.main()
