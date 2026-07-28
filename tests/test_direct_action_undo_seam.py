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

    def test_mage_training_arena_plan_restores_through_the_seam(self):
        from ankiscape.logic.mage_training_arena_logic import (
            apply_mage_training_arena_command_pure,
        )

        addon = self.addon
        before = copy.deepcopy(addon.player_data["mage_training_arena"])
        committed = self.commit(
            lambda current: (
                apply_mage_training_arena_command_pure(
                    current,
                    "set_policy",
                    {
                        "room_policy": "enchantment",
                        "approach": "conserve_runes",
                        "reward_goal": "cosmic_rune",
                    },
                )[0],
                True,
            )
        )
        self.assertTrue(committed)
        self.assertEqual(
            addon.player_data["mage_training_arena"]["room_policy"],
            "enchantment",
        )
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data["mage_training_arena"], before)

    def test_mage_training_arena_purchase_restores_points_and_item_through_the_seam(self):
        from ankiscape.logic.mage_training_arena_logic import (
            apply_mage_training_arena_command_pure,
        )

        addon = self.addon
        state = addon.player_data["mage_training_arena"]
        state["wallets"].update(
            {"telekinetic": 1, "alchemist": 2, "enchantment": 20, "graveyard": 2}
        )
        before = copy.deepcopy(addon.player_data)
        committed = self.commit(
            lambda current: (
                apply_mage_training_arena_command_pure(
                    current,
                    "purchase",
                    {"reward_id": "battlestaff"},
                )[0],
                True,
            )
        )
        self.assertTrue(committed)
        self.assertEqual(addon.player_data["inventory"]["Battlestaff"], 1)
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data, before)

    def test_temple_trekking_food_command_restores_state_and_inventory_through_the_seam(self):
        from ankiscape.logic.temple_trekking_logic import (
            apply_temple_trekking_command_pure,
        )

        addon = self.addon
        addon.player_data["inventory"]["Lobster"] = 28
        before = copy.deepcopy(addon.player_data)

        def change(current):
            updated, ok, _info = apply_temple_trekking_command_pure(
                current,
                "stock_food",
                {"quantity": 28},
            )
            return updated, ok

        self.assertTrue(self.commit(change))
        self.assertEqual(addon.player_data["temple_trekking"]["companion_food"], 28)
        self.assertEqual(addon.player_data["inventory"]["Lobster"], 0)
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data, before)

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

    def test_crucible_lesson_and_purchase_restore_through_the_seam(self):
        """The Crucible spends a currency, so both mutations must be undoable."""
        from ankiscape.data.crucible_data import (
            CRUCIBLE_CURRENCY,
            CRUCIBLE_LESSONS,
            CRUCIBLE_TAUNTS,
        )
        from ankiscape.logic.crucible_logic import apply_crucible_command_pure

        addon = self.addon
        addon.player_data["inventory"] = {CRUCIBLE_CURRENCY: 12}
        before = copy.deepcopy(addon.player_data["inventory"])

        self.assertTrue(
            self.commit(
                lambda current: apply_crucible_command_pure(
                    current, "take_lesson", {"lesson": CRUCIBLE_LESSONS[0]}
                )[:2]
            )
        )
        self.assertEqual(addon.player_data["inventory"][CRUCIBLE_CURRENCY], 13)

        self.assertTrue(
            self.commit(
                lambda current: apply_crucible_command_pure(
                    current, "buy_unlock", {"unlock_id": CRUCIBLE_TAUNTS[0].id}
                )[:2]
            )
        )
        self.assertEqual(
            addon.player_data["crucible_unlocks"], (CRUCIBLE_TAUNTS[0].id,)
        )
        self.assertEqual(addon.player_data["inventory"][CRUCIBLE_CURRENCY], 1)

        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data["crucible_unlocks"], ())
        self.assertEqual(addon.player_data["inventory"][CRUCIBLE_CURRENCY], 13)
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data["inventory"], before)
        self.assertEqual(addon.player_data["crucible_lessons_taken"], ())

    def test_goblin_raids_intimidation_restores_through_the_seam(self):
        """Intimidating Hollowtoof grants three items, so it must be undoable."""
        from ankiscape.data.goblin_raids_data import (
            GOBLIN_RAIDS_RAID_MODE,
            RAIDER_SET_ITEM_NAMES,
        )
        from ankiscape.logic.goblin_raids_logic import (
            advance_goblin_raids_world_clock_pure,
            apply_goblin_raids_command_pure,
        )

        addon = self.addon
        for key in (
            "attack_level",
            "strength_level",
            "defense_level",
            "constitution_level",
        ):
            addon.player_data[key] = 90
        addon.player_data["inventory"] = {}
        addon.player_data["shop_market_clock"] = {"answered_cards": 5}
        updated, _events = advance_goblin_raids_world_clock_pure(
            addon.player_data
        )
        addon.player_data.update(updated)
        self.assertTrue(addon.player_data["goblin_raids"]["active_raid"])

        self.assertTrue(
            self.commit(
                lambda current: apply_goblin_raids_command_pure(
                    current, "join", {"mode": GOBLIN_RAIDS_RAID_MODE}
                )[:2]
            )
        )
        before = copy.deepcopy(addon.player_data["inventory"])
        self.assertTrue(
            self.commit(
                lambda current: apply_goblin_raids_command_pure(
                    current, "intimidate", {}
                )[:2]
            )
        )
        for item_name in RAIDER_SET_ITEM_NAMES:
            self.assertEqual(addon.player_data["inventory"][item_name], 1)

        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data["inventory"], before)
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data["goblin_raids"]["session"], {})

    def test_enchanted_key_site_choice_restores_through_the_seam(self):
        from ankiscape.data.enchanted_key_data import ENCHANTED_KEY_SITE_IDS
        from ankiscape.logic.enchanted_key_logic import (
            apply_enchanted_key_command_pure,
        )

        addon = self.addon
        addon.player_data["quests"]["making_history"] = {
            "started": True,
            "progress": 4,
            "completed": True,
        }
        before = copy.deepcopy(addon.player_data["enchanted_key"])

        committed = self.commit(
            lambda current: (
                apply_enchanted_key_command_pure(
                    current,
                    "select_site",
                    {"site_id": ENCHANTED_KEY_SITE_IDS[0]},
                )[0],
                True,
            )
        )

        self.assertTrue(committed)
        self.assertEqual(
            addon.player_data["enchanted_key"]["selected_site_id"],
            ENCHANTED_KEY_SITE_IDS[0],
        )
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data["enchanted_key"], before)


if __name__ == "__main__":
    unittest.main()
