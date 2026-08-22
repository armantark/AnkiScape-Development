"""The Managing Miscellania handler must go through the shared undo seam.

Before this migration the handler hand-rolled its snapshot, undo entry and save.
Driving the real `_apply_managing_miscellania_command` (captured from the real
main-menu wiring) through `commit_direct_action` pins the contract at the seam.
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
    return _load_addon_as_package("ankiscape_undo_seam_miscellania")


class ManagingMiscellaniaUndoSeamTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_modules = dict(sys.modules)
        self.addon = _load_addon()
        self.addon.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        self.addon.player_data["quests"]["throne_of_miscellania"]["completed"] = True
        self.saves = []
        self.addon.save_player_data = lambda: self.saves.append(True)
        self.collection = _FakeCollection()
        self.addon.mw = _DummyMW(self.collection)
        # Stub side-effect collaborators; an unstubbed achievement dialog is a
        # modal that hangs the offscreen Qt lane.
        self.addon.check_achievements = lambda _data: None
        self.addon.update_review_hud = lambda *_args: None
        self.addon._refresh_skill_availability = lambda: None

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def _miscellania_handler(self):
        """Open the real main menu and capture the real kingdom handler."""
        captured = {}
        self.addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        self.addon._on_main_menu(initial_skill="Activities")
        return captured["on_managing_miscellania_command"]

    def _give_coins(self, amount: int) -> None:
        inventory = self.addon.player_data.setdefault("inventory", {})
        inventory["Coins"] = inventory.get("Coins", 0) + amount

    def test_a_committed_kingdom_action_restores_through_the_seam(self):
        addon = self.addon
        addon.player_data["managing_miscellania"]["coffer"] = 0
        self._give_coins(1000)
        before = copy.deepcopy(addon.player_data)
        handler = self._miscellania_handler()

        result = handler("deposit", {"quantity": 250})

        self.assertTrue(result["ok"])
        self.assertEqual(
            addon.player_data["managing_miscellania"]["coffer"], 250
        )
        self.assertEqual(
            addon.player_data["inventory"]["Coins"],
            before["inventory"]["Coins"] - 250,
        )
        self.assertEqual(
            self.collection.entries, ["AnkiScape direct action"],
            "the kingdom action must register exactly one undo entry",
        )
        self.assertEqual(len(self.saves), 1)
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data, before)

    def test_a_refused_kingdom_action_reports_refusal_and_writes_nothing(self):
        addon = self.addon
        # No coins in the inventory: the deposit must be refused outright.
        addon.player_data["managing_miscellania"]["coffer"] = 0
        before = copy.deepcopy(addon.player_data)
        handler = self._miscellania_handler()

        result = handler("deposit", {"quantity": 500})

        self.assertFalse(result["ok"])
        self.assertIn("No coins can be deposited", result["message"])
        self.assertEqual(dict(addon.player_data), before, "nothing may be written")
        self.assertEqual(self.collection.entries, [], "no undo entry may exist")
        self.assertEqual(len(self.saves), 0)

    def test_a_kingdom_action_when_the_undo_entry_cannot_be_created(self):
        """A failed undo entry must be reported as such, never as success."""
        addon = self.addon
        addon.player_data["managing_miscellania"]["coffer"] = 0
        self._give_coins(1000)
        before = copy.deepcopy(addon.player_data)
        self.collection.accepts = False
        handler = self._miscellania_handler()

        result = handler("deposit", {"quantity": 250})

        self.assertEqual(
            result,
            {
                "ok": False,
                "reason": "undo_unavailable",
                "message": "Anki could not create an undo entry.",
            },
            "a failed undo entry must not echo a successful info dict",
        )
        self.assertEqual(dict(addon.player_data), before, "nothing may be written")
        self.assertEqual(len(self.saves), 0)


if __name__ == "__main__":
    unittest.main()
