import unittest

import ui


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


class TestNotificationGating(unittest.TestCase):
    def setUp(self):
        self.prev_mw = getattr(ui, 'mw', None)

    def tearDown(self):
        ui.mw = self.prev_mw

    def test_floating_xp_enabled_default_true(self):
        ui.mw = None
        self.assertTrue(ui.is_floating_xp_enabled())

    def test_floating_xp_respects_profile(self):
        ui.mw = DummyMW(DummyCol({'ankiscape_floating_xp_enabled': False}))
        self.assertFalse(ui.is_floating_xp_enabled())
        ui.mw.col.set_config('ankiscape_floating_xp_enabled', True)
        self.assertTrue(ui.is_floating_xp_enabled())

    def test_popups_enabled_default_true(self):
        ui.mw = None
        self.assertTrue(ui.is_popups_enabled())

    def test_popups_respects_profile(self):
        ui.mw = DummyMW(DummyCol({'ankiscape_popups_enabled': False}))
        self.assertFalse(ui.is_popups_enabled())
        ui.mw.col.set_config('ankiscape_popups_enabled', True)
        self.assertTrue(ui.is_popups_enabled())


if __name__ == '__main__':
    unittest.main()
