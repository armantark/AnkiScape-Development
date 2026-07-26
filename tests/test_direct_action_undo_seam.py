"""Policy and preference changes must be undoable, like every other mutation.

Breadth criterion 5 asks for undo at every mutation boundary. Five families
failed it in the same way: a policy or preference command saved persistent state
and registered no undo entry, so the change could not be taken back. The frontier
audit reported those as five separate family defects. They were one missing seam.

`commit_direct_action` in `__init__.py` is that seam. It snapshots the save and
the random state, registers the Anki undo entry, pushes the bounded snapshot,
commits and saves — the sequence that previously existed only inside
`resolve_review_context_action`, serving the reviewer context strip alone.

These tests pin the contract at the seam rather than at each call site, so a
sixth family wiring a policy command cannot quietly skip undo again.
"""

from __future__ import annotations

import copy
import random
import sys
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data


class _FakeCollection:
    """Records undo entries the way Anki's collection would."""

    def __init__(self, accepts: bool = True) -> None:
        self.accepts = accepts
        self.entries: list[str] = []

    def add_custom_undo_entry(self, name: str) -> None:
        if not self.accepts:
            raise RuntimeError("collection refused the undo entry")
        self.entries.append(name)


class _DummyMW:
    """The same shape the smoke tests install; the seam calls update_undo_actions."""

    def __init__(self, col):
        self.col = col
        self.undo_updates = 0

    def update_undo_actions(self):
        self.undo_updates += 1


def _load_addon():
    """Load __init__.py as a package, the way the smoke tests do.

    The `ankiscape` alias deliberately does NOT execute __init__.py, so the seam
    cannot be imported through it. Skipping instead would leave four tests that
    certify nothing, which is worse than not writing them.

    The runtime fakes must go in first. Without them __init__.py cannot import
    at all in the non-Qt lane, which is how these tests passed under Qt while
    erroring everywhere else.
    """
    from tests.test_integration_smoke import (
        _install_runtime_fakes,
        _load_addon_as_package,
    )

    _install_runtime_fakes()
    return _load_addon_as_package("ankiscape_undo_seam")


class DirectActionUndoSeamTest(unittest.TestCase):
    def setUp(self) -> None:
        # Restored in tearDown: loading the add-on installs fake aqt modules,
        # and leaving them behind would corrupt every later test in the run.
        self._orig_modules = dict(sys.modules)
        self.addon = _load_addon()
        self.commit = self.addon.commit_direct_action
        # The smoke tests assign this attribute rather than mutating it, because
        # the add-on only creates the global at profile load.
        self.addon.player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        self.saves = []
        self.addon.save_player_data = lambda: self.saves.append(True)
        self.collection = _FakeCollection()
        self.addon.mw = _DummyMW(self.collection)

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_a_committed_change_registers_exactly_one_undo_entry(self):
        addon = self.addon

        collection = self.collection
        before_depth = len(addon._DIRECT_ACTION_UNDO_STACK)

        committed = self.commit(
            lambda current: ({**current, "world_population_profile": "busy"}, True)
        )

        self.assertTrue(committed)
        self.assertEqual(collection.entries, ["AnkiScape direct action"])
        self.assertEqual(
            len(addon._DIRECT_ACTION_UNDO_STACK), before_depth + 1
        )
        self.assertEqual(
            addon.player_data["world_population_profile"], "busy"
        )
        self.assertEqual(len(self.saves), 1, "a committed change must persist")

    def test_a_refused_change_writes_nothing_and_restores_the_rng(self):
        addon = self.addon

        collection = self.collection
        baseline = copy.deepcopy(dict(addon.player_data))
        rng_before = random.getstate()

        def refuse(current):
            random.random()  # a refused action may still have drawn
            return {**current, "world_population_profile": "busy"}, False

        committed = self.commit(refuse)

        self.assertFalse(committed)
        self.assertEqual(dict(addon.player_data), baseline)
        self.assertEqual(collection.entries, [])
        self.assertEqual(self.saves, [], "a refusal must not persist anything")
        self.assertEqual(
            random.getstate(),
            rng_before,
            "a refusal must not advance the random sequence",
        )

    def test_a_collection_that_refuses_the_entry_commits_nothing(self):
        """Undo must exist before the change lands, never after."""
        addon = self.addon

        collection = _FakeCollection(accepts=False)
        addon.mw = _DummyMW(collection)
        baseline = copy.deepcopy(dict(addon.player_data))

        committed = self.commit(
            lambda current: ({**current, "world_population_profile": "busy"}, True)
        )

        self.assertFalse(committed)
        self.assertEqual(
            dict(addon.player_data),
            baseline,
            "no undo entry means no change may be written",
        )

    def test_the_snapshot_stack_stays_bounded(self):
        addon = self.addon

        cap = addon._MAX_DIRECT_ACTION_UNDO_SNAPSHOTS

        for index in range(cap + 5):
            self.commit(
                lambda current, i=index: ({**current, "_probe": i}, True)
            )

        self.assertLessEqual(len(addon._DIRECT_ACTION_UNDO_STACK), cap)

    def test_skeletal_horror_wish_list_command_restores_through_the_seam(self):
        from ankiscape.logic.skeletal_horror_logic import (
            apply_skeletal_horror_command_pure,
        )

        addon = self.addon
        addon.player_data["quests"]["rag_and_bone_man"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
        before = copy.deepcopy(addon.player_data["skeletal_horror"])

        committed = self.commit(
            lambda current: (
                apply_skeletal_horror_command_pure(
                    current,
                    "complete_rag_wish_list",
                )[0],
                True,
            )
        )

        self.assertTrue(committed)
        self.assertTrue(
            addon.player_data["skeletal_horror"]["rag_wish_list_complete"]
        )
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data["skeletal_horror"], before)

    def test_tears_of_guthix_entry_restores_through_the_seam(self):
        from ankiscape.logic.tears_of_guthix_logic import (
            apply_tears_of_guthix_command_pure,
        )

        addon = self.addon
        addon.player_data["quests"]["tears_of_guthix"] = {
            "started": True,
            "progress": 3,
            "completed": True,
        }
        addon.player_data["quest_points"] = 44
        before = copy.deepcopy(addon.player_data["tears_of_guthix"])

        committed = self.commit(
            lambda current: (
                apply_tears_of_guthix_command_pure(current, "enter")[0],
                True,
            )
        )

        self.assertTrue(committed)
        self.assertTrue(addon.player_data["tears_of_guthix"]["active"])
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data["tears_of_guthix"], before)
        self.assertFalse(addon.player_data["tears_of_guthix"]["active"])


if __name__ == "__main__":
    unittest.main()
