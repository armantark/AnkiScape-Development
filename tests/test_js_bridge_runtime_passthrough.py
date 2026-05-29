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


def _install_runtime_fakes():
    aqt = types.ModuleType("aqt")
    aqt.mw = None
    aqt.gui_hooks = _FakeHooks()
    aqt_reviewer = types.ModuleType("aqt.reviewer")
    class _FakeReviewer:
        def _answerCard(self, ease):
            return None
    aqt_reviewer.Reviewer = _FakeReviewer
    sys.modules["aqt"] = aqt
    sys.modules["aqt.reviewer"] = aqt_reviewer

    anki_hooks = types.ModuleType("anki.hooks")
    def addHook(_name, _fn):
        return None
    def wrap(old, new, _mode):
        def _wrapped(self, ease):
            return new(self, ease, old)
        return _wrapped
    anki_hooks.addHook = addHook
    anki_hooks.wrap = wrap
    sys.modules["anki.hooks"] = anki_hooks


def _load_addon_as_package(mod_name="ankiscape_for_bridge_test"):
    root = Path(__file__).resolve().parents[1]
    init_py = root / "__init__.py"
    loader = SourceFileLoader(mod_name, str(init_py))
    spec = spec_from_loader(mod_name, loader, is_package=True)
    mod = module_from_spec(spec)
    mod.__path__ = [str(root)]  # type: ignore[attr-defined]
    sys.modules[mod_name] = mod
    loader.exec_module(mod)
    return mod


class TestJSBridgeRuntimePassthrough(unittest.TestCase):
    def setUp(self):
        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _get_js_handler(self):
        addon = _load_addon_as_package()
        # Explicitly register deck browser hooks, which also registers the webview js message handler
        try:
            addon._register_deck_browser_button()  # type: ignore[attr-defined]
        except Exception:
            pass
        aqt = sys.modules["aqt"]
        handlers = aqt.gui_hooks.webview_did_receive_js_message
        self.assertGreaterEqual(len(handlers), 1)
        # The only one we register should be our handler
        return handlers[-1]

    def test_core_actions_are_never_swallowed(self):
        h = self._get_js_handler()
        for msg in ("browse", "add", "stats", "sync", "open:add", "open:decks", "preview", "card-info", "addcards"):
            handled, out = h(False, msg, None)
            self.assertFalse(handled, msg)
            self.assertEqual(out, msg)

    def test_ankiscape_messages_are_handled_or_preserve(self):
        h = self._get_js_handler()
        # ankiscape_open_menu should be marked handled
        handled, out = h(False, "ankiscape_open_menu", None)
        self.assertTrue(handled)
        self.assertEqual(out, "ankiscape_open_menu")
        # ankiscape_log:* should preserve incoming handled
        handled, out = h(False, "ankiscape_log:foo", None)
        self.assertFalse(handled)
        handled, out = h(True, "ankiscape_log:foo", None)
        self.assertTrue(handled)


if __name__ == "__main__":
    unittest.main()
