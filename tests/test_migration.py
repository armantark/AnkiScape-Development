import unittest

import ui

class DummyCol:
    def __init__(self, store):
        self._store = dict(store)
    def get_config(self, key, default=None):
        # Simulate Anki behavior: return default when missing
        return self._store.get(key, default)
    def set_config(self, key, val):
        self._store[key] = val

class DummyMW:
    def __init__(self, col):
        self.col = col

class TestMigration(unittest.TestCase):
    def setUp(self):
        self.prev_mw = getattr(ui, 'mw', None)

    def tearDown(self):
        ui.mw = self.prev_mw

    def test_migrate_old_progress_to_review_hud_when_new_unset(self):
        col = DummyCol({'ankiscape_hud_progress_enabled': False})
        ui.mw = DummyMW(col)
        # Ensure new key not present
        self.assertIsNone(ui.mw.col.get_config('ankiscape_review_hud_enabled', None))
        ui.migrate_legacy_settings()
        # Old False should map to new False
        self.assertEqual(ui.mw.col.get_config('ankiscape_review_hud_enabled', None), False)

    def test_migration_is_idempotent_and_does_not_override(self):
        col = DummyCol({'ankiscape_hud_progress_enabled': False, 'ankiscape_review_hud_enabled': True})
        ui.mw = DummyMW(col)
        ui.migrate_legacy_settings()
        # New key should remain True (not overridden by old False)
        self.assertTrue(ui.mw.col.get_config('ankiscape_review_hud_enabled', None))

if __name__ == '__main__':
    unittest.main()
