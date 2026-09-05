"""The Barbarian Assault command handler must undo through the shared seam.

Like every other activity command, a Barbarian Assault action saves persistent
state and therefore has to register an Anki undo entry. Before this test the
handler hand-rolled its own snapshot and save transaction, so it could drift
from `commit_direct_action` — including the failure mode where a successful
action whose undo entry could not be created was reported to the player as
success. These tests drive the REAL handler through the REAL seam.
"""

from __future__ import annotations

import copy
import sys
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data


class _FakeCollection:
    def __init__(self, accepts: bool = True) -> None:
        self.accepts = accepts
        self.entries: list[str] = []

    def add_custom_undo_entry(self, name: str) -> None:
        if not self.accepts:
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
    return _load_addon_as_package("ankiscape_undo_seam_barbassault")


class BarbarianAssaultUndoSeamTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        self.addon = _load_addon()
        self.addon._state.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        self.addon.save_player_data = lambda: None
        self.collection = _FakeCollection()
        self.addon.mw = _DummyMW(self.collection)
        # Stub modal/surface collaborators only; the seam itself stays real.
        self.addon.check_achievements = lambda _data: None
        self.addon._refresh_skill_availability = lambda: None
        self.addon._show_activity_gain = lambda _text: None
        self.addon.update_review_hud = lambda *_args: None

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _handler(self):
        captured = {}
        self.addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        self.addon._on_main_menu(initial_skill="Activities")
        return captured["on_barbarian_assault_command"]

    def test_tutorial_completion_restores_through_the_seam(self):
        addon = self.addon
        before = copy.deepcopy(addon._state.player_data)
        handler = self._handler()

        result = handler("tutorial", {})

        self.assertTrue(result["ok"], result)
        self.assertTrue(addon._state.player_data["barbarian_assault_tutorial_complete"])
        self.assertEqual(
            self.collection.entries, ["AnkiScape direct action"]
        )
        addon._restore_direct_action_snapshot(addon._state.direct_action_undo_stack.pop())
        self.assertEqual(addon._state.player_data, before)

    def test_refusal_returns_its_own_refusal_and_writes_nothing(self):
        addon = self.addon
        handler = self._handler()
        addon._state.player_data["barbarian_assault_tutorial_complete"] = True
        baseline = copy.deepcopy(dict(addon._state.player_data))

        result = handler("tutorial", {})

        self.assertFalse(result["ok"])
        self.assertIn("already complete", result["message"])
        self.assertEqual(
            result["reason"], "Captain Cain's tutorial is already complete."
        )
        self.assertEqual(dict(addon._state.player_data), baseline)

    def test_undo_entry_failure_reports_undo_unavailable(self):
        """A successful action with no undo entry must never look like success."""
        addon = self.addon
        handler = self._handler()
        before = copy.deepcopy(addon._state.player_data)
        self.collection.accepts = False

        result = handler("tutorial", {})

        self.assertEqual(
            result,
            {
                "ok": False,
                "reason": "undo_unavailable",
                "message": "Anki could not create an undo entry.",
            },
            "a failed undo entry must be reported as such, not as success",
        )
        self.assertEqual(
            dict(addon._state.player_data), before, "nothing may be written"
        )


if __name__ == "__main__":
    unittest.main()
