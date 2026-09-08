"""Unproductive dispatch keeps selection lazy and leaves execution in the caller."""

import copy
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.runtime import runtime_actions as actions


class EqualitySelection:
    def __init__(self, target):
        self.target = target
        self.compared = []

    def __eq__(self, other):
        self.compared.append(other)
        return other == self.target

    def __ne__(self, other):
        raise AssertionError("Selection must use equality, not inequality.")

    def __hash__(self):
        raise AssertionError("Selection must not hash activity IDs.")


class TestUnproductiveActivitySelector(unittest.TestCase):
    def test_predicates_and_handlers_resolve_after_import_only_when_selected(self):
        player = {"current_utility": actions.CASTLE_WARS_ACTIVITY_ID}
        original = copy.deepcopy(player)
        selected = object()
        with patch.object(actions, "trouble_brewing_view_pure", side_effect=AssertionError("eager view")), \
                patch.object(actions, "castle_wars_view_pure", return_value={"active": True}) as view, \
                patch.object(actions, "handle_castle_wars_answer", selected):
            self.assertIs(actions.unproductive_activity_answer_handler(player, "utility"), selected)
            view.assert_called_once_with(player)
            view.return_value = {"active": False}
            self.assertIsNone(actions.unproductive_activity_answer_handler(player, "utility"))
            view.side_effect = ValueError("view failed")
            with self.assertRaisesRegex(ValueError, "view failed"):
                actions.unproductive_activity_answer_handler(player, "utility")
        self.assertEqual(player, original)

    def test_irregular_predicates_keep_their_original_meaning(self):
        player = {"current_utility": actions.GNOME_RESTAURANT_ACTIVITY_ID}
        with patch.object(actions, "gnome_restaurant_view_pure", return_value={"active": True}):
            self.assertIsNone(actions.unproductive_activity_answer_handler(player, "utility"))
        with patch.object(actions, "gnome_restaurant_view_pure", return_value={"order": {"id": 1}}):
            self.assertIs(actions.unproductive_activity_answer_handler(player, "utility"),
                          actions.handle_gnome_restaurant_answer)
        player = {"current_utility": actions.TROLL_INVASION_ACTIVITY_ID, "troll_invasion": {"active": False}}
        with patch.object(actions, "troll_invasion_view_pure", side_effect=AssertionError("raw state required")):
            self.assertIs(actions.unproductive_activity_answer_handler(player, "utility"),
                          actions.handle_troll_invasion_answer)
        for name in ("mobilising_armies", "temple_trekking"):
            with self.subTest(name=name), patch.object(actions, name + "_can_review_pure", return_value=True):
                player = {"current_utility": getattr(actions, name.upper() + "_ACTIVITY_ID")}
                self.assertIs(actions.unproductive_activity_answer_handler(player, "utility"),
                              getattr(actions, "handle_" + name + "_answer"))

    def test_flash_powder_routes_and_sequential_equality(self):
        flash = actions.FLASH_POWDER_FACTORY_ACTIVITY_ID
        for key in ("utility", "agility"):
            player = {"current_" + key: flash, "agility_activity_state": {flash: {"active": False}}}
            self.assertIs(actions.unproductive_activity_answer_handler(player, key),
                          actions.handle_flash_powder_factory_answer)
            player["agility_activity_state"] = ["truthy non-dict"]
            self.assertIsNone(actions.unproductive_activity_answer_handler(player, key))
        self.assertIsNone(actions.unproductive_activity_answer_handler({"current_utility": []}, "utility"))
        selection = EqualitySelection(actions.CASTLE_WARS_ACTIVITY_ID)
        with patch.object(actions, "castle_wars_view_pure", return_value={"active": True}):
            selected = actions.unproductive_activity_answer_handler({"current_utility": selection}, "utility")
        self.assertIs(selected, actions.handle_castle_wars_answer)
        self.assertEqual(selection.compared, [flash, actions.TROUBLE_BREWING_ACTIVITY_ID,
                                             actions.CASTLE_WARS_ACTIVITY_ID])
