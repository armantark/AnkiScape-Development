"""The Fishing Trawler command handler must go through the shared undo seam.

Before this migration `_apply_fishing_trawler_command` hand-rolled its own
snapshot, undo entry and save transaction. These tests drive the REAL handler
through `commit_direct_action` and pin that a committed change is undoable and
that a refused or unwritten change reports honestly.
"""

from __future__ import annotations

import sys
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data


class _FakeCollection:
    def __init__(self, raises: bool = False) -> None:
        self.raises = raises
        self.entries: list[str] = []

    def add_custom_undo_entry(self, name: str) -> None:
        if self.raises:
            raise RuntimeError("collection refused the undo entry")
        self.entries.append(name)


class _DummyMW:
    def __init__(self, col):
        self.col = col

    def update_undo_actions(self):
        pass


def _load_addon():
    from tests.test_integration_smoke import (
        _install_runtime_fakes,
        _load_addon_as_package,
    )

    _install_runtime_fakes()
    return _load_addon_as_package("ankiscape_undo_seam_trawler")


class TrawlerUndoSeamTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        addon = _load_addon()
        addon.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        self.saves: list[bool] = []
        addon.save_player_data = lambda: self.saves.append(True)
        # Stub modal and HUD surfaces; an unstubbed achievement dialog hung the
        # offscreen Qt lane in the first wave of migrations.
        addon.check_achievements = lambda _pd: None
        addon._refresh_skill_availability = lambda: None
        addon.update_review_hud = lambda *_a, **_k: None
        shown: list[str] = []
        addon._show_activity_gain = shown.append
        self.shown = shown
        self.addon = addon
        # The handler lives inside _on_main_menu; capture it from the menu
        # builder exactly the way the smoke tests do.
        self.captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: self.captured.update(
            kwargs
        )
        self.handler = None

    def _get_handler(self):
        if self.handler is None:
            self.addon._on_main_menu(initial_activity_id="fishing_trawler")
            self.handler = self.captured["on_fishing_trawler_command"]
        return self.handler

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_policy_change_commits_and_undores_through_the_seam(self):
        addon = self.addon
        collection = _FakeCollection()
        addon.mw = _DummyMW(collection)

        result = self._get_handler()(
            "set_fishing_trawler_policy",
            {"automation_mode": "advanced"},
        )

        self.assertTrue(result["ok"], result)
        self.assertEqual(
            addon.player_data["fishing_trawler_policy"]["automation_mode"],
            "advanced",
        )
        self.assertEqual(collection.entries, ["AnkiScape direct action"])
        self.assertEqual(len(self.saves), 1)
        self.assertEqual(
            self.shown, [result.get("message", "Fishing Trawler plan saved.")]
        )
        before_depth = len(addon._DIRECT_ACTION_UNDO_STACK)
        snapshot = addon._DIRECT_ACTION_UNDO_STACK.pop()
        self.assertEqual(len(addon._DIRECT_ACTION_UNDO_STACK), before_depth - 1)
        addon._restore_direct_action_snapshot(snapshot)
        self.assertEqual(
            addon.player_data["fishing_trawler_policy"]["automation_mode"],
            "casual",
        )

    def test_refused_action_reports_the_refusal_and_writes_nothing(self):
        addon = self.addon
        collection = _FakeCollection()
        addon.mw = _DummyMW(collection)

        from ankiscape.logic.fishing_trawler_logic import (
            apply_fishing_trawler_command_pure,
        )

        result = self._get_handler()("bogus_action", {})

        self.assertFalse(result["ok"])
        expected = apply_fishing_trawler_command_pure(
            dict(addon.player_data), "bogus_action", {}
        )[2]["reason"]
        self.assertEqual(result["message"], str(expected))
        self.assertEqual(collection.entries, [])
        self.assertEqual(len(self.saves), 0)

    def test_undo_unavailable_reports_failure_not_success(self):
        addon = self.addon
        addon.mw = _DummyMW(_FakeCollection(raises=True))

        result = self._get_handler()(
            "set_fishing_trawler_policy",
            {"automation_mode": "advanced"},
        )

        self.assertEqual(
            result,
            {
                "ok": False,
                "reason": "undo_unavailable",
                "message": "Anki could not create an undo entry.",
            },
        )
        self.assertEqual(len(self.saves), 0, "nothing was written, so no save")
        self.assertEqual(
            addon.player_data["fishing_trawler_policy"]["automation_mode"],
            "casual",
            "the player data must not carry the accepted change",
        )


if __name__ == "__main__":
    unittest.main()
