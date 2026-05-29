import unittest

# We avoid importing aqt; test pure helpers and gating logic entry-points
from ui import get_config_bool

class DummyCol:
    def __init__(self, store):
        self._store = dict(store)
    def get_config(self, key, default=None):
        return self._store.get(key, default)
    def set_config(self, key, val):
        self._store[key] = val

class DummyMW:
    def __init__(self, col):
        self.col = col

class TestSettingsToggles(unittest.TestCase):
    def test_get_config_bool_defaults_true(self):
        # No mw present; should return default
        import ui
        prev_mw = getattr(ui, 'mw', None)
        try:
            ui.mw = None
            self.assertTrue(get_config_bool('missing_key', True))
            self.assertFalse(get_config_bool('missing_key', False))
        finally:
            ui.mw = prev_mw

    def test_get_config_bool_reads_profile(self):
        import ui
        prev_mw = getattr(ui, 'mw', None)
        try:
            col = DummyCol({'ankiscape_review_hud_enabled': False, 'ankiscape_popups_enabled': True})
            ui.mw = DummyMW(col)
            self.assertFalse(get_config_bool('ankiscape_review_hud_enabled', True))
            self.assertTrue(get_config_bool('ankiscape_popups_enabled', False))
        finally:
            ui.mw = prev_mw

    def test_experience_toggle_default_true_and_persist(self):
        import ui
        prev_mw = getattr(ui, 'mw', None)
        try:
            ui.mw = None
            # default True when no profile
            self.assertTrue(get_config_bool('ankiscape_review_hud_enabled', True))
            # simulate persistence
            col = DummyCol({'ankiscape_review_hud_enabled': False})
            ui.mw = DummyMW(col)
            self.assertFalse(get_config_bool('ankiscape_review_hud_enabled', True))
            ui.mw.col.set_config('ankiscape_review_hud_enabled', True)
            self.assertTrue(get_config_bool('ankiscape_review_hud_enabled', False))
        finally:
            ui.mw = prev_mw

if __name__ == '__main__':
    unittest.main()
