import copy
import dataclasses
import sys
import types
import unittest
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from pathlib import Path

class _FakeHooks:
    def __init__(self):
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
        self.custom_undo_entries = []
    def get_config(self, key, default=None):
        return self._store.get(key, default)
    def set_config(self, key, value):
        self._store[key] = value
    def add_custom_undo_entry(self, name):
        self.custom_undo_entries.append(name)
        return len(self.custom_undo_entries)

class _DummyMW:
    def __init__(self, col):
        self.col = col
        self.undo_updates = 0
    def update_undo_actions(self):
        self.undo_updates += 1


def _install_runtime_fakes():
    # aqt base module
    aqt = types.ModuleType("aqt")
    aqt.mw = None
    aqt.gui_hooks = _FakeHooks()

    # Give each package load a pristine reviewer class. Add-on wrapping mutates
    # the class method, so reusing _FakeReviewer would nest stale wrappers.
    class _RuntimeReviewer(_FakeReviewer):
        pass

    aqt_reviewer = types.ModuleType("aqt.reviewer")
    aqt_reviewer.Reviewer = _RuntimeReviewer

    # Shadow stale real-Qt imports without unloading their process-global types.
    sys.modules["aqt.qt"] = types.ModuleType("aqt.qt")
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


def _install_quest_combat_mid_rolls(testcase, addon, repeats=2000):
    original_random = addon.random.random
    original_review_multiplier = addon._review_action_multiplier
    rolls = iter((0.5,) * repeats)
    addon.random.random = lambda: next(rolls, 1.0)
    addon._review_action_multiplier = lambda: 10
    testcase.addCleanup(setattr, addon.random, "random", original_random)
    testcase.addCleanup(setattr, addon, "_review_action_multiplier", original_review_multiplier)


import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import QUEST_DATA
from tests.quest_action_proof_helpers import quest_action_proofs_for_quest


if __name__ == "__main__":
    unittest.main()
