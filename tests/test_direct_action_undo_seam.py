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

    def test_hunter_target_selection_commits_and_restores_through_the_seam(self):
        addon = self.addon
        addon.player_data["current_hunter"] = "catch_crimson_swift"

        committed = addon._set_value("current_hunter", "catch_carrion_jadinko")

        self.assertTrue(committed)
        self.assertEqual(
            addon.player_data["current_hunter"], "catch_carrion_jadinko"
        )
        self.assertEqual(self.collection.entries, ["AnkiScape direct action"])
        addon._on_state_did_undo(
            type("Changes", (), {"operation": "AnkiScape direct action"})()
        )
        self.assertEqual(addon.player_data["current_hunter"], "catch_crimson_swift")

    def test_same_type_combat_style_change_is_one_undoable_commit(self):
        addon = self.addon
        addon.player_data["combat_attack_style"] = "Accurate"
        addon.player_data["combat_attack_style_type"] = "crush"

        self.assertTrue(addon._set_combat_attack_style(("Aggressive", "crush")))

        self.assertEqual(addon.player_data["combat_attack_style"], "Aggressive")
        self.assertEqual(self.collection.entries, ["AnkiScape direct action"])
        addon._on_state_did_undo(
            type("Changes", (), {"operation": "AnkiScape direct action"})()
        )
        self.assertEqual(addon.player_data["combat_attack_style"], "Accurate")

    def test_same_target_guild_exit_is_one_undoable_commit(self):
        addon = self.addon
        addon.player_data["current_combat_target"] = "goblin"
        addon.player_data["warriors_guild"] = {
            "in_cyclops_room": True,
            "cyclossus_pending": True,
            "token_drain_residual": 4,
        }

        self.assertTrue(addon._set_combat_target("goblin"))

        self.assertFalse(addon.player_data["warriors_guild"]["in_cyclops_room"])
        self.assertEqual(self.collection.entries, ["AnkiScape direct action"])
        addon._on_state_did_undo(
            type("Changes", (), {"operation": "AnkiScape direct action"})()
        )
        self.assertTrue(addon.player_data["warriors_guild"]["in_cyclops_room"])

    def test_activity_danger_toggle_commits_and_restores_through_the_seam(self):
        from ankiscape.logic.agility_logic import apply_agility_command_pure

        addon = self.addon
        self.assertTrue(addon.player_data["activity_auto_stop_on_danger"])

        def disable(current):
            updated, result = apply_agility_command_pure(
                current,
                "set_activity_auto_stop",
                {"enabled": False},
            )
            return updated, bool(result.get("allowed"))

        committed = self.commit(disable)

        self.assertTrue(committed)
        self.assertFalse(addon.player_data["activity_auto_stop_on_danger"])
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertTrue(addon.player_data["activity_auto_stop_on_danger"])

    def test_bank_started_treasure_trail_commits_and_restores_through_the_seam(self):
        from ankiscape.logic.treasure_trails_logic import (
            apply_treasure_trails_command_pure,
        )

        addon = self.addon
        addon.player_data["inventory"] = {"Clue scroll (easy)": 1}

        def start_trail(current):
            updated, ok, _info = apply_treasure_trails_command_pure(
                current, "start_from_bank", {"tier": "easy"}, lambda: 0.0
            )
            return updated, ok

        committed = self.commit(start_trail)

        self.assertTrue(committed)
        self.assertEqual(
            addon.player_data["activity_session"]["active_id"], "treasure_trail"
        )
        self.assertTrue(addon.player_data["treasure_trail"])
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data["inventory"], {"Clue scroll (easy)": 1})
        self.assertEqual(addon.player_data["treasure_trail"], {})

    def test_pinning_a_distraction_commits_and_restores_through_the_seam(self):
        """The reviewer badge's watch list is a preference like any other."""
        from ankiscape.data.evil_tree_data import EVIL_TREE_UTILITY_ID
        from ankiscape.logic.dnd_favourites_logic import toggle_dnd_favourite_pure

        addon = self.addon
        self.assertEqual(addon.player_data["dnd_favourites"], [])

        def pin(current):
            updated, ok, _info = toggle_dnd_favourite_pure(
                current, EVIL_TREE_UTILITY_ID
            )
            return updated, ok

        committed = self.commit(pin)

        self.assertTrue(committed)
        self.assertEqual(
            addon.player_data["dnd_favourites"], [EVIL_TREE_UTILITY_ID]
        )
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data["dnd_favourites"], [])

    def test_pinning_something_that_is_not_a_distraction_commits_nothing(self):
        from ankiscape.logic.dnd_favourites_logic import toggle_dnd_favourite_pure

        addon = self.addon

        committed = self.commit(
            lambda current: toggle_dnd_favourite_pure(current, "castle_wars")[:2]
        )

        self.assertFalse(committed)
        self.assertEqual(addon.player_data["dnd_favourites"], [])
        self.assertEqual(self.collection.entries, [])

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

    def _run_with_rng_checkpoint(self, action):
        previous_state = random.getstate()
        try:
            random.seed(20260821)
            expected_next = random.random()
            random.seed(20260821)
            result = action()
            actual_next = random.random()
        finally:
            random.setstate(previous_state)
        self.assertEqual(actual_next, expected_next)
        return result

    def _treasure_trails_handler(self):
        addon = self.addon
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda _data: None
        addon._on_main_menu(initial_skill="Activities")
        return captured["on_treasure_trails_command"]

    def test_treasure_trails_refusal_preserves_the_random_sequence(self):
        addon = self.addon
        addon.player_data["inventory"] = {}
        command = self._treasure_trails_handler()

        result = self._run_with_rng_checkpoint(
            lambda: command("open_casket", {"tier": "easy"})
        )

        self.assertEqual(
            result,
            {"ok": False, "message": "You have no Casket (easy)."},
        )

    def test_treasure_trails_undo_failure_preserves_the_random_sequence(self):
        addon = self.addon
        addon.player_data["inventory"] = {"Casket (easy)": 1}
        self.collection.accepts = False
        command = self._treasure_trails_handler()

        result = self._run_with_rng_checkpoint(
            lambda: command("open_casket", {"tier": "easy"})
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["message"], "Anki could not create an undo entry.")

    def test_treasure_trails_undo_restores_the_random_sequence(self):
        addon = self.addon
        addon.player_data["inventory"] = {"Casket (easy)": 1}
        command = self._treasure_trails_handler()

        def open_then_undo():
            result = command("open_casket", {"tier": "easy"})
            self.assertTrue(result["ok"], result)
            addon._on_state_did_undo(
                type("Changes", (), {"operation": "AnkiScape direct action"})()
            )
            return result

        self._run_with_rng_checkpoint(open_then_undo)

    def _prepare_volatile_mining_urn(self):
        from ankiscape.data.urn_data import URN_TIERS_BY_ID

        addon = self.addon
        tier = URN_TIERS_BY_ID["mining_cracked_urn"]
        addon.player_data["inventory"] = {
            tier.item_full: 1,
            "Volatile clay tool": 1,
        }
        addon.player_data["carried_inventory"] = {
            "copper": {tier.item_full: 1}
        }
        addon.player_data["current_ore"] = "copper"
        addon.player_data["mining_level"] = 40
        addon.player_data["mining_exp"] = 0.0
        addon.player_data["stealing_creation"] = {
            "active_reward_tool": "volatile",
            "reward_tools": {
                "morphic": {},
                "volatile": {
                    "kind": "volatile",
                    "form_id": "pickaxe",
                    "charge": 0.11,
                    "segments_used": 8,
                },
            },
        }
        addon.level_up_check = lambda *_args: None
        addon.check_achievements = lambda _data: None
        addon._show_exp = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon.update_review_event_log_drawer = lambda *_args: None
        addon._update_review_bank_run_surface = lambda: None
        addon._update_review_context_surface = lambda: None
        addon.ui.update_menu_visibility = lambda *_args: None
        addon.current_skill = "Mining"
        return tier

    def test_urn_teleport_refusal_preserves_the_random_sequence(self):
        addon = self.addon
        tier = self._prepare_volatile_mining_urn()
        addon.player_data["inventory"].pop(tier.item_full)
        addon.player_data["carried_inventory"] = {}

        committed = self._run_with_rng_checkpoint(
            lambda: addon.teleport_training_urn(tier.id)
        )

        self.assertFalse(committed)

    def test_urn_teleport_undo_failure_preserves_the_random_sequence(self):
        addon = self.addon
        tier = self._prepare_volatile_mining_urn()
        self.collection.accepts = False

        committed = self._run_with_rng_checkpoint(
            lambda: addon.teleport_training_urn(tier.id)
        )

        self.assertFalse(committed)

    def test_urn_teleport_undo_restores_the_random_sequence(self):
        addon = self.addon
        tier = self._prepare_volatile_mining_urn()

        def teleport_then_undo():
            committed = addon.teleport_training_urn(tier.id)
            self.assertTrue(committed)
            addon._on_state_did_undo(
                type("Changes", (), {"operation": "AnkiScape direct action"})()
            )
            return committed

        self._run_with_rng_checkpoint(teleport_then_undo)

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

    def test_mobilising_armies_investment_restores_state_and_inventory_through_the_seam(self):
        from ankiscape.data.item_values import ITEM_VALUES
        from ankiscape.logic.mobilising_armies_logic import (
            apply_mobilising_armies_command_pure,
        )

        addon = self.addon
        addon.player_data["inventory"]["Adamant bar"] = 4
        before = copy.deepcopy(addon.player_data)

        def change(current):
            updated, ok, _info = apply_mobilising_armies_command_pure(
                current,
                "invest",
                {"item_name": "Adamant bar", "quantity": 4},
                lambda: 0.5,
                item_values=ITEM_VALUES,
            )
            return updated, ok

        self.assertTrue(self.commit(change))
        self.assertEqual(
            addon.player_data["mobilising_armies_investment_credits"], 4 * 129
        )
        self.assertNotIn("Adamant bar", addon.player_data["inventory"])
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data, before)

    def test_gnome_restaurant_delivery_job_restores_through_the_seam(self):
        from ankiscape.data.gnome_restaurant_data import (
            GNOME_COCKTAIL_TARGET_IDS,
            GNOME_DISH_TARGET_IDS,
        )
        from ankiscape.logic.gnome_restaurant_logic import (
            apply_gnome_restaurant_command_pure,
        )

        addon = self.addon
        addon.player_data["action_telemetry"] = {
            "actions": {
                f"cooking:{target_id}": {"attempts": 1, "successes": 1}
                for target_id in list(GNOME_DISH_TARGET_IDS)[:4]
                + list(GNOME_COCKTAIL_TARGET_IDS)[:4]
            }
        }
        before = copy.deepcopy(addon.player_data)

        def change(current):
            updated, ok, _info = apply_gnome_restaurant_command_pure(
                current,
                "open_service",
                {},
                lambda: 0.0,
            )
            return updated, ok

        self.assertTrue(self.commit(change))
        self.assertTrue(addon.player_data["gnome_restaurant"]["service_open"])
        self.assertEqual(addon.player_data["inventory"]["Gianne dough"], 100)
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data, before)

    def test_dominion_tower_face_command_restores_through_the_seam(self):
        from ankiscape.logic.dominion_tower_logic import (
            apply_dominion_tower_command_pure,
        )

        addon = self.addon
        for skill in ("attack", "strength", "defense", "constitution", "magic", "ranged"):
            addon.player_data[f"{skill}_level"] = 99
        before = copy.deepcopy(addon.player_data)

        def change(current):
            updated, ok, _info = apply_dominion_tower_command_pure(
                current,
                "talk_to_face",
                {},
            )
            return updated, ok

        self.assertTrue(self.commit(change))
        self.assertTrue(addon.player_data["dominion_tower"]["talked_with_face"])
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

    def test_dungeoneering_entry_policy_route_and_abandon_restore_independently(self):
        from ankiscape.logic.dungeoneering_logic import (
            apply_dungeoneering_command_pure,
            dungeoneering_view_pure,
        )

        addon = self.addon
        addon.player_data["dungeoneering_level"] = 1
        before = copy.deepcopy(addon.player_data)
        self.assertTrue(
            self.commit(
                lambda current: apply_dungeoneering_command_pure(
                    current,
                    "enter",
                    {
                        "floor": 1,
                        "size": "small",
                        "complexity": 1,
                        "automation_mode": "casual",
                    },
                )[:2]
            )
        )
        self.assertTrue(addon.player_data["dungeoneering"]["active"])
        self.assertTrue(
            self.commit(
                lambda current: apply_dungeoneering_command_pure(
                    current,
                    "set_policy",
                    {"automation_mode": "advanced"},
                )[:2]
            )
        )
        room_id = dungeoneering_view_pure(
            addon.player_data,
            selected_skill="Dungeoneering",
        )["frontier_rows"][0]["room_id"]
        self.assertTrue(
            self.commit(
                lambda current: apply_dungeoneering_command_pure(
                    current,
                    "select_route",
                    {"room_id": room_id},
                )[:2]
            )
        )
        selected = copy.deepcopy(addon.player_data["dungeoneering"])
        self.assertTrue(
            self.commit(
                lambda current: apply_dungeoneering_command_pure(
                    current,
                    "abandon",
                )[:2]
            )
        )
        self.assertFalse(addon.player_data["dungeoneering"]["active"])

        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data["dungeoneering"], selected)
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data["dungeoneering"]["selected_room_id"], -1)
        self.assertEqual(
            addon.player_data["dungeoneering"]["automation_mode"],
            "advanced",
        )
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(
            addon.player_data["dungeoneering"]["automation_mode"],
            "casual",
        )
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data, before)

    def test_dungeoneering_kinship_purchase_and_fill_restore_independently(self):
        from ankiscape.logic.dungeoneering_logic import (
            apply_dungeoneering_command_pure,
        )

        addon = self.addon
        addon.player_data["dungeoneering_level"] = 35
        addon.player_data["mining_level"] = 35
        addon.player_data["dungeoneering"]["tokens"] = 10_000
        addon.player_data["inventory"]["Coal"] = 27
        before = copy.deepcopy(addon.player_data)

        def commit_command(action_id, payload):
            return self.commit(
                lambda current: apply_dungeoneering_command_pure(
                    current,
                    action_id,
                    payload,
                )[:2]
            )

        self.assertTrue(
            commit_command(
                "select_kinship_class",
                {"class_id": "gatherer"},
            )
        )
        selected = copy.deepcopy(addon.player_data)
        self.assertEqual(
            addon.player_data["dungeoneering"]["kinship_active_class"],
            "gatherer",
        )
        self.assertTrue(
            commit_command(
                "upgrade_kinship_class",
                {"class_id": "gatherer"},
            )
        )
        self.assertEqual(
            addon.player_data["dungeoneering"]["kinship_tiers"]["gatherer"],
            1,
        )
        self.assertEqual(addon.player_data["dungeoneering"]["tokens"], 9_865)
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data, selected)
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data, before)

        self.assertTrue(
            commit_command(
                "purchase_reward",
                {"reward_id": "coal_bag"},
            )
        )
        purchased = copy.deepcopy(addon.player_data)
        self.assertTrue(addon.player_data["dungeoneering"]["coal_bag_owned"])
        self.assertTrue(
            commit_command(
                "fill_coal_bag",
                {"source": "bank"},
            )
        )
        self.assertEqual(
            addon.player_data["dungeoneering"]["coal_bag_coal"],
            27,
        )
        self.assertNotIn("Coal", addon.player_data["inventory"])
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data, purchased)
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data, before)

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

    def test_troll_invasion_entry_and_reward_policy_restore_through_the_seam(self):
        from ankiscape.data.troll_invasion_data import TROLL_INVASION_REPAIR_MODE
        from ankiscape.logic.troll_invasion_logic import apply_troll_invasion_command_pure

        addon = self.addon
        before = copy.deepcopy(addon.player_data)
        self.assertTrue(
            self.commit(
                lambda current: apply_troll_invasion_command_pure(
                    current,
                    "set_policy",
                    {
                        "mode": TROLL_INVASION_REPAIR_MODE,
                        "difficulty": "standard",
                        "reward_skill": "mining",
                    },
                )[:2]
            )
        )
        self.assertEqual(
            addon.player_data["troll_invasion_policy"]["mode"],
            TROLL_INVASION_REPAIR_MODE,
        )
        self.assertTrue(
            self.commit(
                lambda current: apply_troll_invasion_command_pure(
                    current, "enter", {}
                )[:2]
            )
        )
        self.assertTrue(addon.player_data["troll_invasion"])
        active = copy.deepcopy(addon.player_data["troll_invasion"])
        self.assertTrue(
            self.commit(
                lambda current: apply_troll_invasion_command_pure(
                    current, "leave", {}
                )[:2]
            )
        )
        self.assertEqual(addon.player_data["troll_invasion"], {})
        self.assertEqual(addon.player_data["troll_invasion_exits"], 1)
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data["troll_invasion"], active)
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data["troll_invasion"], {})
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data, before)

    def test_troll_invasion_reward_book_uses_the_award_seam_and_restores_on_undo(self):
        from ankiscape.data.goblin_raids_data import (
            GOBLIN_COWER_SHIELD,
            GOBLIN_COWER_SHIELD_BONUS_BUDGET,
        )
        from ankiscape.data.troll_invasion_data import TROLL_INVASION_REWARD_BOOK
        from ankiscape.logic.goblin_raids_logic import default_goblin_raids_state_pure
        from ankiscape.logic.troll_invasion_logic import apply_troll_invasion_command_pure

        addon = self.addon
        addon.player_data["inventory"][TROLL_INVASION_REWARD_BOOK] = 1
        addon.player_data["inventory"][GOBLIN_COWER_SHIELD] = 1
        addon.player_data["equipment"]["shield"] = GOBLIN_COWER_SHIELD
        addon.player_data["goblin_raids"] = default_goblin_raids_state_pure()
        addon.player_data["goblin_raids"]["cower_shield_bonus_remaining"] = (
            GOBLIN_COWER_SHIELD_BONUS_BUDGET
        )
        addon.player_data["troll_invasion_reward_fractions"] = [1.0]
        before = copy.deepcopy(addon.player_data)
        info = {}
        gained = 0.0
        level_checks = []
        addon.level_up_check = lambda skill, _data: level_checks.append(skill)

        def change(current):
            nonlocal info
            updated, ok, info = apply_troll_invasion_command_pure(
                current, "redeem_book", {"skill_id": "attack"}
            )
            return updated, ok

        def award():
            nonlocal gained
            base = float(info["xp_rewards"]["attack_exp"])
            gained = addon._award_skill_exp(
                "attack_exp", base, action_skill_id="attack"
            )
            addon.level_up_check("Attack", addon.player_data)

        self.assertTrue(self.commit(change, after_apply=award))
        base = float(info["xp_rewards"]["attack_exp"])
        self.assertEqual(gained, base * 1.25)
        self.assertEqual(addon.player_data["attack_exp"] - before["attack_exp"], gained)
        self.assertEqual(level_checks, ["Attack"])
        self.assertEqual(addon.player_data["inventory"].get(TROLL_INVASION_REWARD_BOOK, 0), 0)
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data, before)

    def test_shattered_heart_pair_turn_in_and_xp_restore_through_the_seam(self):
        from ankiscape.data.shattered_heart_data import SHATTERED_HEART_SKILLS_BY_ID
        from ankiscape.logic.shattered_heart_logic import apply_shattered_heart_command_pure

        addon = self.addon
        for item_name in SHATTERED_HEART_SKILLS_BY_ID["agility"].rock_items:
            addon.player_data["inventory"][item_name] = 1
        before = copy.deepcopy(addon.player_data)
        info = {}
        awarded = 0.0
        level_checks = []
        addon.level_up_check = lambda skill, _data: level_checks.append(skill)

        def change(current):
            nonlocal info
            updated, ok, info = apply_shattered_heart_command_pure(
                current, "add_completed_pairs", {}
            )
            return updated, ok

        def award():
            nonlocal awarded
            amount = float(info["skill_xp"]["agility"])
            awarded = addon._award_skill_exp(
                "agility_exp", amount, action_skill_id="agility"
            )
            addon.level_up_check("Agility", addon.player_data)

        self.assertTrue(self.commit(change, after_apply=award))
        self.assertEqual(
            addon.player_data["shattered_heart"]["placed_pairs"], ["agility"]
        )
        self.assertEqual(
            addon.player_data["agility_exp"] - before["agility_exp"], awarded
        )
        self.assertEqual(level_checks, ["Agility"])
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data, before)

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

    def test_conquest_setup_entry_and_resignation_each_restore_exactly(self):
        from ankiscape.logic.conquest_logic import apply_conquest_command_pure

        addon = self.addon
        for key in (
            "attack_level",
            "strength_level",
            "defense_level",
            "constitution_level",
            "ranged_level",
            "magic_level",
            "prayer_level",
        ):
            addon.player_data[key] = 40
        addon.player_data["activity_session"] = {"active_id": ""}
        addon.player_data["combat_encounter"] = {}
        before = copy.deepcopy(addon.player_data)

        self.assertTrue(
            self.commit(
                lambda current: apply_conquest_command_pure(
                    current,
                    "set_policy",
                    {"automation_mode": "casual", "doctrine": "aggressive"},
                    lambda: 0.25,
                )[:2]
            )
        )
        after_setup = copy.deepcopy(addon.player_data)
        self.assertEqual(
            addon.player_data["conquest_policy"]["doctrine"], "aggressive"
        )
        self.assertTrue(
            self.commit(
                lambda current: apply_conquest_command_pure(
                    current, "enter", {}, lambda: 0.25
                )[:2]
            )
        )
        active = copy.deepcopy(addon.player_data)
        self.assertEqual(
            addon.player_data["activity_session"], {"active_id": "conquest"}
        )
        self.assertTrue(
            self.commit(
                lambda current: apply_conquest_command_pure(
                    current, "resign", {}, lambda: 0.25
                )[:2]
            )
        )
        self.assertEqual(addon.player_data["activity_session"], {"active_id": ""})
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data, active)
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data, after_setup)
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data, before)

    def _farming_handler(self):
        """Open the real main menu and capture the real Farming handler."""
        captured = {}
        self.addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        self.addon._on_main_menu(initial_skill="Farming")
        return captured["on_farming_action"]

    def test_farming_action_restores_through_the_seam(self):
        addon = self.addon
        # The real check_achievements opens a modal dialog on completion; under
        # a live QApplication that blocks the run forever. Patch the module
        # global the handler resolves at call time.
        addon.check_achievements = lambda _data: None
        addon.player_data["farming_level"] = 99
        before = copy.deepcopy(addon.player_data)
        handler = self._farming_handler()

        result = handler("set_plan", {"patch_id": "falador_allotment_north", "crop_id": "potato"})

        self.assertTrue(result["ok"])
        plan = addon.player_data["farm_plans"]["falador_allotment_north"]
        self.assertEqual(plan.get("crop_id"), "potato")
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data, before)

    def test_a_refused_farming_action_returns_its_own_refusal(self):
        addon = self.addon
        handler = self._farming_handler()

        result = handler("set_plan", {"patch_id": "nowhere", "crop_id": "potato"})

        self.assertFalse(result["ok"])
        self.assertNotEqual(result["message"], "Anki could not create an undo entry.")

    def test_farming_action_when_the_undo_entry_cannot_be_created(self):
        """The undo-unavailable path must never echo a successful info dict."""
        from ankiscape.logic.farming_logic import farming_frontend_projection_pure

        addon = self.addon
        addon.player_data["farming_level"] = 99
        before = copy.deepcopy(addon.player_data)
        self.collection.accepts = False
        handler = self._farming_handler()

        result = handler("set_plan", {"patch_id": "falador_allotment_north", "crop_id": "potato"})

        self.assertEqual(
            result,
            {
                "ok": False,
                "reason": "undo_unavailable",
                "message": "Anki could not create an undo entry.",
                "projection": farming_frontend_projection_pure(addon.player_data),
            },
            "a failed undo entry must be reported as such, not as success",
        )
        self.assertEqual(dict(addon.player_data), before, "nothing may be written")



    def _capture_agility_handler(self):
        """Drive the REAL handler: stub the menu dialog, keep the wiring."""
        addon = self.addon
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon._refresh_skill_availability = lambda: None
        addon._update_review_context_surface = lambda: None
        addon.update_review_hud = lambda *_args: None
        addon.check_achievements = lambda _data: None
        addon._show_exp = lambda _gained: None
        addon._award_skill_exp = lambda *args, **kwargs: 0.0
        addon.level_up_check = lambda *_args: None
        addon._on_main_menu(initial_skill="Activities")
        return captured["on_agility_command"]

    def test_agility_gnome_ball_entry_restores_through_the_real_handler(self):
        addon = self.addon
        command = self._capture_agility_handler()
        before = copy.deepcopy(addon.player_data)

        outcome = command("enter_gnome_ball", {})

        self.assertTrue(outcome["ok"], outcome)
        self.assertTrue(addon.player_data["gnome_ball"])
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data, before)

    def test_flash_powder_factory_stop_switches_to_bankstanding_and_undoes(self):
        from ankiscape.data.flash_powder_factory_data import (
            FLASH_POWDER_FACTORY_ACTIVITY_ID,
        )
        from ankiscape.logic.flash_powder_factory_logic import (
            enter_flash_powder_factory_pure,
        )

        addon = self.addon
        addon.player_data.update(
            {
                "agility_level": 75,
                "thieving_level": 75,
                "herblore_level": 50,
                "current_agility": FLASH_POWDER_FACTORY_ACTIVITY_ID,
            }
        )
        entered, allowed, info = enter_flash_powder_factory_pure(addon.player_data)
        self.assertTrue(allowed, info)
        addon.player_data.clear()
        addon.player_data.update(entered)
        command = self._capture_agility_handler()
        addon.current_skill = "Activities"
        before = copy.deepcopy(addon.player_data)

        outcome = command("abandon", {})

        self.assertTrue(outcome["ok"], outcome)
        self.assertEqual(addon.current_skill, "Utilities")
        self.assertEqual(addon.player_data["current_utility"], "bankstanding")
        self.assertEqual(
            addon.player_data["current_agility"],
            FLASH_POWDER_FACTORY_ACTIVITY_ID,
        )
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.current_skill, "Activities")
        self.assertEqual(addon.player_data, before)

    def test_agility_refusal_returns_the_refusal_and_writes_nothing(self):
        addon = self.addon
        command = self._capture_agility_handler()
        addon.player_data["equipment"] = {"weapon": "Bronze sword"}
        baseline = copy.deepcopy(dict(addon.player_data))

        outcome = command("enter_gnome_ball", {})

        self.assertFalse(outcome["ok"])
        self.assertIn("unequip your weapon", str(outcome.get("reason")))
        self.assertEqual(
            dict(addon.player_data), baseline, "a refusal must write nothing"
        )

    def test_agility_undo_entry_failure_reports_undo_unavailable(self):
        """A successful action whose undo entry fails must not look like success."""
        addon = self.addon
        addon.mw = _DummyMW(_FakeCollection(accepts=False))
        command = self._capture_agility_handler()
        baseline = copy.deepcopy(dict(addon.player_data))

        outcome = command("enter_gnome_ball", {})

        self.assertFalse(outcome["ok"])
        self.assertEqual(
            outcome["message"], "Anki could not create an undo entry"
        )
        self.assertNotIn("reason", outcome)
        self.assertEqual(
            dict(addon.player_data),
            baseline,
            "no undo entry means no change may be written",
        )



    def _guild_handler(self):
        captured = {}
        self.addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        self.addon.update_review_hud = lambda *_args: None
        self.addon._on_main_menu(initial_skill="Activities")
        return captured["on_warriors_guild_command"]

    def test_warriors_guild_room_entry_restores_through_the_seam(self):
        from ankiscape.logic.warriors_guild_logic import (
            MULTI_TOKEN_ENTRY_COST,
            WARRIORS_GUILD_TOKEN_KEYS,
        )

        addon = self.addon
        handler = self._guild_handler()
        addon.player_data["warriors_guild"]["in_cyclops_room"] = False
        addon.player_data["warriors_guild"]["automation_mode"] = "advanced"
        addon.player_data["warriors_guild"]["payment_mode"] = "multi"
        addon.player_data["attack_level"] = 99
        addon.player_data["strength_level"] = 99
        for token in WARRIORS_GUILD_TOKEN_KEYS:
            addon.player_data["warriors_guild"]["tokens"][token] = (
                MULTI_TOKEN_ENTRY_COST
            )
        before = copy.deepcopy(addon.player_data)

        result = handler("enter_room", {})

        self.assertTrue(result["ok"], result)
        self.assertTrue(addon.player_data["warriors_guild"]["in_cyclops_room"])
        self.assertEqual(self.collection.entries, ["AnkiScape direct action"])
        self.assertEqual(len(self.saves), 1, "the entry must persist")
        addon._restore_direct_action_snapshot(
            addon._DIRECT_ACTION_UNDO_STACK.pop()
        )
        self.assertEqual(addon.player_data["warriors_guild"], before["warriors_guild"])

    def test_warriors_guild_refusal_returns_the_reason_and_writes_nothing(self):
        from ankiscape.logic.warriors_guild_logic import (
            MULTI_TOKEN_ENTRY_COST,
            WARRIORS_GUILD_TOKEN_KEYS,
        )

        addon = self.addon
        handler = self._guild_handler()
        addon.player_data["warriors_guild"]["in_cyclops_room"] = False
        addon.player_data["warriors_guild"]["automation_mode"] = "advanced"
        addon.player_data["warriors_guild"]["payment_mode"] = "multi"
        addon.player_data["attack_level"] = 99
        addon.player_data["strength_level"] = 99
        for token in WARRIORS_GUILD_TOKEN_KEYS:
            addon.player_data["warriors_guild"]["tokens"][token] = 0
        before = copy.deepcopy(addon.player_data)

        result = handler("enter_room", {})

        self.assertFalse(result["ok"])
        self.assertEqual(result["message"], "Need 30 of every Warriors' Guild token")
        self.assertEqual(addon.player_data, before)
        self.assertEqual(len(self.saves), 0)

    def test_warriors_guild_undo_unavailable_reports_it_instead_of_success(self):
        from ankiscape.logic.warriors_guild_logic import (
            MULTI_TOKEN_ENTRY_COST,
            WARRIORS_GUILD_TOKEN_KEYS,
        )

        addon = self.addon
        handler = self._guild_handler()
        self.collection.accepts = False
        addon.player_data["warriors_guild"]["in_cyclops_room"] = False
        addon.player_data["warriors_guild"]["automation_mode"] = "advanced"
        addon.player_data["warriors_guild"]["payment_mode"] = "multi"
        addon.player_data["attack_level"] = 99
        addon.player_data["strength_level"] = 99
        for token in WARRIORS_GUILD_TOKEN_KEYS:
            addon.player_data["warriors_guild"]["tokens"][token] = (
                MULTI_TOKEN_ENTRY_COST
            )

        result = handler("enter_room", {})

        self.assertEqual(
            result,
            {"ok": False, "message": "Anki could not create an undo entry."},
        )



    def _big_chinchompa_handler(self):
        """Open the real main menu headless and capture the real handler."""
        captured = {}
        self.addon.ui.show_main_menu = (
            lambda *args, **kwargs: captured.update(kwargs)
        )
        self.addon._on_main_menu()
        return captured["on_big_chinchompa_command"]

    def test_big_chinchompa_reward_purchase_restores_through_the_seam(self):
        addon = self.addon
        buy_reward = self._big_chinchompa_handler()
        addon.player_data["big_chinchompa"]["competence_points"] = 5
        before = copy.deepcopy(addon.player_data)

        result = buy_reward("buy_reward", {"reward_id": "hunter_xp"})

        self.assertTrue(result["ok"])
        self.assertEqual(
            addon.player_data["big_chinchompa"]["competence_points"], 4
        )
        self.assertEqual(addon.player_data["hunter_exp"] - before["hunter_exp"], 5.0)
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data, before)

    def test_big_chinchompa_refused_purchase_returns_the_refusal(self):
        addon = self.addon
        buy_reward = self._big_chinchompa_handler()
        addon.player_data["big_chinchompa"]["competence_points"] = 0
        before = copy.deepcopy(addon.player_data)

        result = buy_reward("buy_reward", {"reward_id": "hunter_xp"})

        self.assertFalse(result["ok"])
        self.assertEqual(result["message"], "Not enough Competence points.")
        self.assertEqual(addon.player_data, before)
        self.assertEqual(len(self.saves), 0)
        self.assertEqual(
            len(addon._DIRECT_ACTION_UNDO_STACK), 0,
            "a refused purchase must not register an undo entry",
        )

    def test_big_chinchompa_purchase_without_an_undo_entry_commits_nothing(self):
        addon = self.addon
        buy_reward = self._big_chinchompa_handler()
        addon.player_data["big_chinchompa"]["competence_points"] = 5
        before = copy.deepcopy(addon.player_data)
        self.collection.accepts = False

        result = buy_reward("buy_reward", {"reward_id": "hunter_xp"})

        self.assertFalse(result["ok"])
        self.assertEqual(result["message"], "Anki could not create an undo entry.")
        self.assertEqual(addon.player_data, before)
        self.assertEqual(len(self.saves), 0)


    def test_grand_exchange_offer_restores_through_the_real_handler(self):
        """Drive _apply_ge_action itself through commit_direct_action.

        Stubbed here are only side-effect collaborators (bank run, HUD,
        achievements surface), never the seam: the handler must reach
        commit_direct_action for snapshot, undo entry and save.
        """
        addon = self.addon
        addon.player_data["inventory"] = {"Coins": 10_000}
        addon.current_skill = "Utility / Activities"
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda _data: None
        bank_runs = []

        def request_bank_run(data):
            bank_runs.append(copy.deepcopy(data))
            return copy.deepcopy(data), True, "", False

        addon._request_active_bank_run_state = request_bank_run

        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon._on_main_menu()
        before = copy.deepcopy(addon.player_data)
        guide_price = int(addon.GE_ITEM_CATALOG["Logs"]["guide_price"])
        payload = {
            "side": "buy",
            "item_name": "Logs",
            "quantity": 1,
            "unit_price": guide_price,
        }

        preview = captured["on_ge_action"]("preview_offer", payload)
        self.assertTrue(preview["ok"])
        self.assertEqual(addon._DIRECT_ACTION_UNDO_STACK, [])

        result = captured["on_ge_action"]("place_offer", payload)
        self.assertTrue(result["ok"])
        self.assertTrue(result["bank_run_triggered"])
        self.assertEqual(len(bank_runs), 1)
        self.assertEqual(addon.player_data["inventory"]["Coins"], 10_000 - guide_price)
        self.assertEqual(len(addon.player_data["ge_player_orders"]), 1)
        self.assertEqual(self.collection.entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._DIRECT_ACTION_UNDO_STACK), 1)
        self.assertEqual(len(self.saves), 1)

        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(addon.player_data, before)

    def test_ge_undo_unavailable_reports_failure_not_success(self):
        """When the undo entry cannot be created, the player must not be told
        the offer was placed. commit_direct_action returns False for a refusal
        and for a failed undo entry; only the first carries the action's info.
        """
        addon = self.addon
        addon.player_data["inventory"] = {"Coins": 10_000}
        addon.current_skill = "Utility / Activities"
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda _data: None
        addon._request_active_bank_run_state = (
            lambda data: (copy.deepcopy(data), True, "", False)
        )

        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon._on_main_menu()

        class _ClosedCollection:
            def add_custom_undo_entry(self, _operation):
                raise RuntimeError("collection closed")

            def set_config(self, *_args):
                pass

        addon.mw.col = _ClosedCollection()
        baseline = copy.deepcopy(addon.player_data)
        payload = {
            "side": "buy",
            "item_name": "Logs",
            "quantity": 1,
            "unit_price": int(addon.GE_ITEM_CATALOG["Logs"]["guide_price"]),
        }

        result = captured["on_ge_action"]("place_offer", payload)

        self.assertEqual(
            result["reason"],
            "undo_unavailable",
            "a failed undo entry must surface as undo_unavailable, not as success",
        )
        self.assertFalse(result["ok"])
        self.assertEqual(
            dict(addon.player_data),
            baseline,
            "no undo entry means no change may be written",
        )


    def test_ge_pure_refusal_reports_refusal_through_handler(self):
        """A pure-function refusal (not an undo failure) must surface the
        pure result itself, not undo_unavailable."""
        addon = self.addon
        addon.player_data["inventory"] = {"Coins": 10_000}
        addon.current_skill = "Utility / Activities"
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda _data: None
        addon._request_active_bank_run_state = (
            lambda data: (copy.deepcopy(data), True, "", False)
        )

        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon._on_main_menu()

        baseline = copy.deepcopy(addon.player_data)
        payload = {
            "side": "sideways",
            "item_name": "Logs",
            "quantity": 1,
            "unit_price": int(addon.GE_ITEM_CATALOG["Logs"]["guide_price"]),
        }

        result = captured["on_ge_action"]("place_offer", payload)

        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "invalid_side")
        self.assertNotIn("undo_unavailable", result.values())
        self.assertEqual(dict(addon.player_data), baseline)

    def _capture_mage_arena_handler(self):
        """Reach the real Mage Arena handler through the real menu wiring."""
        addon = self.addon
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        errors = []
        addon.show_error_message = lambda title, message: errors.append((title, message))
        addon._refresh_skill_availability = lambda: None
        gains = []
        addon._show_activity_gain = lambda message: gains.append(message)
        addon._on_main_menu()
        return captured["on_mage_arena_action"], errors, gains

    def test_mage_training_arena_alignment_choice_restores_through_the_real_handler(self):
        from ankiscape.logic_pure.logic_pure_landmarks import (
            MAGE_ARENA_GOD_DATA,
            sanitize_mage_arena_state_pure,
        )

        addon = self.addon
        handler, errors, gains = self._capture_mage_arena_handler()
        before = copy.deepcopy(dict(addon.player_data))

        self.assertTrue(handler("select_alignment", "guthix"))

        self.assertEqual(errors, [], "a committed choice shows no error")
        self.assertEqual(gains, [])
        state = sanitize_mage_arena_state_pure(addon.player_data.get("mage_arena"))
        self.assertEqual(state["alignment"], "guthix")
        self.assertEqual(
            self.collection.entries, ["AnkiScape direct action"]
        )
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(dict(addon.player_data), before)
        self.assertEqual(MAGE_ARENA_GOD_DATA["guthix"]["spell_id"], "claws_of_guthix")

    def test_mage_training_arena_alignment_choice_tells_the_player_when_undo_is_unavailable(
        self,
    ):
        """The seam newly made alignment contingent on the undo entry.

        Main wrote and saved without one, so a refusing collection used to be
        unreachable here. The chosen behaviour: the choice does not land and
        the player is told so — silent loss is never acceptable.
        """
        from ankiscape.logic_pure.logic_pure_landmarks import (
            sanitize_mage_arena_state_pure,
        )

        addon = self.addon
        addon.mw = _DummyMW(_FakeCollection(accepts=False))
        handler, errors, gains = self._capture_mage_arena_handler()
        before = copy.deepcopy(dict(addon.player_data))

        self.assertFalse(handler("select_alignment", "guthix"))

        self.assertEqual(len(errors), 1)
        title, message = errors[0]
        self.assertEqual(title, "Alignment unchanged")
        self.assertIn("was not applied", message)
        self.assertEqual(gains, [])
        state = sanitize_mage_arena_state_pure(addon.player_data.get("mage_arena"))
        self.assertNotEqual(state["alignment"], "guthix")
        self.assertEqual(dict(addon.player_data), before)
        self.assertEqual(self.saves, [], "nothing was written, nothing is saved")

    def test_mage_training_arena_cape_claim_restores_state_through_the_real_handler(self):
        addon = self.addon
        addon.player_data["mage_arena"] = {
            "step": 5,
            "completed": True,
            "alignment": "",
            "attuned_spells": [],
        }
        handler, errors, gains = self._capture_mage_arena_handler()
        before = copy.deepcopy(dict(addon.player_data))

        self.assertTrue(handler("cape", "zamorak"))

        self.assertEqual(errors, [])
        self.assertEqual(len(gains), 1)
        self.assertIn("Zamorak cape", gains[0])
        self.assertEqual(addon.player_data["inventory"].get("Zamorak cape"), 1)
        self.assertEqual(
            addon.player_data["mage_arena"]["alignment"], "zamorak"
        )
        addon._restore_direct_action_snapshot(addon._DIRECT_ACTION_UNDO_STACK.pop())
        self.assertEqual(dict(addon.player_data), before)

    def test_mage_training_arena_cape_refusal_shows_reason_and_writes_nothing(self):
        addon = self.addon
        handler, errors, _gains = self._capture_mage_arena_handler()
        before = copy.deepcopy(dict(addon.player_data))

        self.assertFalse(handler("cape", "zamorak"))

        self.assertEqual(
            errors,
            [("Cannot use Mage Arena statue", "mage_arena_incomplete")],
        )
        self.assertEqual(self.collection.entries, [])
        self.assertEqual(dict(addon.player_data), before)

    def test_mage_training_arena_undo_entry_failure_reports_nothing_written(self):
        """The seam refused after a successful pure step: nothing was written,
        so the handler must not show the pure step's success-flavoured info as
        an error reason."""
        addon = self.addon
        addon.player_data["mage_arena"] = {
            "step": 5,
            "completed": True,
            "alignment": "",
            "attuned_spells": [],
        }
        handler, errors, gains = self._capture_mage_arena_handler()
        addon.mw = _DummyMW(_FakeCollection(accepts=False))
        before = copy.deepcopy(dict(addon.player_data))

        self.assertFalse(handler("cape", "zamorak"))

        self.assertEqual(errors, [], "no undo entry means nothing happened; "
                                     "the pure refusal text would be wrong here")
        self.assertEqual(gains, [], "the claim toast must not fire either")
        self.assertEqual(dict(addon.player_data), before)

    def _capture_star_handler(self):
        """Reach the real Shooting Star handler the way the menu wires it."""
        addon = self.addon
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon.check_achievements = lambda *_args: None
        addon._on_main_menu()
        return addon, captured["on_shooting_star_command"]

    def _make_exchangeable_star(self, addon):
        from ankiscape.logic.shooting_star_logic import (
            advance_shooting_star_world_clock_pure,
            default_shooting_star_state_pure,
        )

        player = copy.deepcopy(addon.player_data)
        player["mining_level"] = 99
        player.setdefault("shop_market_clock", {})["answered_cards"] = 40
        player["shooting_star"] = default_shooting_star_state_pure()
        player, _ = advance_shooting_star_world_clock_pure(player)
        event = dict(player["shooting_star"]["active_event"])
        event.update(
            {
                "current_size": 0,
                "layer_remaining": 0,
                "sprite_released": True,
                "sprite_expires_card": 60,
            }
        )
        player["shooting_star"]["active_event"] = event
        player["inventory"]["Stardust"] = 99
        addon.player_data.clear()
        addon.player_data.update(player)

    def test_shooting_star_exchange_restores_through_the_seam(self):
        addon, exchange = self._capture_star_handler()
        self._make_exchangeable_star(addon)
        before = copy.deepcopy(addon.player_data)

        result = exchange("exchange", {})

        self.assertTrue(result["ok"])
        self.assertEqual(len(self.saves), 1)
        self.assertEqual(self.collection.entries, ["AnkiScape direct action"])
        self.assertEqual(len(addon._DIRECT_ACTION_UNDO_STACK), 1)
        self.assertNotEqual(addon.player_data, before)
        addon._restore_direct_action_snapshot(
            addon._DIRECT_ACTION_UNDO_STACK.pop()
        )
        self.assertEqual(addon.player_data, before)

    def test_shooting_star_exchange_when_the_collection_refuses_the_entry(self):
        addon, exchange = self._capture_star_handler()
        self.collection.accepts = False
        self._make_exchangeable_star(addon)
        before = copy.deepcopy(addon.player_data)

        result = exchange("exchange", {})

        self.assertEqual(
            result,
            {"ok": False, "message": "Anki could not create an undo entry."},
        )
        self.assertEqual(addon.player_data, before)
        self.assertEqual(self.saves, [], "nothing may persist without undo")

    def test_shooting_star_exchange_refusal_keeps_the_sprite_message(self):
        addon, exchange = self._capture_star_handler()

        result = exchange("exchange", {})

        self.assertFalse(result["ok"])
        self.assertEqual(result["message"], "No Star sprite is available.")
        self.assertEqual(self.saves, [], "nothing may persist without undo")


if __name__ == "__main__":
    unittest.main()
