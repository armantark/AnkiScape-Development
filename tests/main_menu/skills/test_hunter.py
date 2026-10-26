from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_named_label,
    _goto_hunter,
    _hunter_group_node,
    _hunter_row,
    _make_player_data,
    _panel_title,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QCheckBox, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_hunter_is_selectable_and_shows_grouped_source_targets(self) -> None:
        pd = _make_player_data()
        pd["hunter_level"] = 99
        pd["inventory"] = {"Logs": 1, "Impling jar": 1}
        pd["current_hunter"] = "catch_wild_kebbit"
        dialog = self._open(pd)
        tree = _goto_hunter(dialog)

        title = _panel_title(dialog)
        self.assertTrue(
            title.startswith("Hunter"),
            f"panel did not switch to Hunter; still shows {title!r}",
        )
        group_roles = [
            tree.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole)
            for i in range(tree.topLevelItemCount())
        ]
        self.assertIn("__hunter_group__:bird_snaring", group_roles)
        self.assertIn("__hunter_group__:tracking", group_roles)
        self.assertIn("__hunter_group__:deadfall", group_roles)
        self.assertIn("__hunter_group__:impling_world", group_roles)
        self.assertEqual(_hunter_group_node(tree, "deadfall").text(0), "Deadfall  (4)")
        self.assertEqual(_hunter_group_node(tree, "tracking").text(0), "Tracking  (5)")

        wild = _hunter_row(tree, "catch_wild_kebbit")
        ferret = _hunter_row(tree, "catch_ferret")
        pirate = _hunter_row(tree, "catch_pirate_impling_world")
        polar = _hunter_row(tree, "catch_polar_kebbit")
        razor_backed = _hunter_row(tree, "track_razor_backed_kebbit")
        self.assertIs(wild, tree.currentItem())
        self.assertFalse(wild.isDisabled())
        self.assertFalse(wild.icon(0).isNull(), "Hunter target row has no icon")
        self.assertIn("Outputs: Bones x1, Kebbit claws x1", wild.toolTip(0))
        self.assertIn("Base XP: 128 per successful catch", wild.toolTip(0))
        self.assertIn("Success chance:", wild.toolTip(0))
        self.assertIn("Logs x1 (you have 1)", wild.toolTip(0))
        self.assertTrue(ferret.isDisabled())
        self.assertIn("Eagles' Peak", ferret.toolTip(0))
        self.assertTrue(pirate.isDisabled())
        self.assertIn("Rocking Out", pirate.toolTip(0))
        self.assertTrue(polar.isDisabled())
        self.assertIn("Outputs: Bones x1, Raw beast meat x1, Polar kebbit fur x1", polar.toolTip(0))
        self.assertIn("Noose wand x1 (you have 0)", polar.toolTip(0))
        self.assertFalse(polar.icon(0).isNull())
        self.assertTrue(razor_backed.isDisabled())
        self.assertIn("Noose wand x1 (you have 0)", razor_backed.toolTip(0))
        self.assertFalse(razor_backed.icon(0).isNull())

        before = list(self._hunter_calls)
        tree.itemClicked.emit(ferret, 0)
        QApplication.processEvents()
        self.assertEqual(self._hunter_calls, before, "quest-locked hunter target must not be selectable")

        tree.itemClicked.emit(wild, 0)
        QApplication.processEvents()
        self.assertEqual(self._hunter_calls[-1], "catch_wild_kebbit")

    def test_hunter_private_ground_control_uses_carried_ticket_count(self) -> None:
        ticket = "Swamp lizard quota ticket"
        pd = _make_player_data()
        pd.update(
            {
                "hunter_level": 99,
                "current_hunter": "catch_swamp_lizard",
                "carried_inventory": {
                    "catch_swamp_lizard": {ticket: 2},
                },
                "hunter_private_ground_targets": [],
            }
        )
        pd["inventory"][ticket] = 2
        dialog = self._open(pd)
        _goto_hunter(dialog)

        control = dialog.findChild(QCheckBox, "hunterPrivateGroundCheck")
        hint = _find_named_label(dialog, "hunterPrivateGroundHint")
        self.assertFalse(control.isHidden())
        self.assertTrue(control.isEnabled())
        self.assertIn("2 carried", control.text())
        self.assertIn("only after a successful catch", hint.text())

        control.setChecked(True)
        QApplication.processEvents()
        self.assertEqual(
            pd["hunter_private_ground_targets"],
            ["catch_swamp_lizard"],
        )
        self.assertEqual(
            self._big_chinchompa_calls[-1],
            (
                "set_private_ground",
                {"target_id": "catch_swamp_lizard", "enabled": True},
            ),
        )

        pd["carried_inventory"]["catch_swamp_lizard"] = {}
        empty_dialog = self._open(pd)
        _goto_hunter(empty_dialog)
        configured_without_tickets = empty_dialog.findChild(
            QCheckBox, "hunterPrivateGroundCheck"
        )
        self.assertTrue(configured_without_tickets.isChecked())
        self.assertTrue(
            configured_without_tickets.isEnabled(),
            "A configured target must remain possible to uncheck after tickets run out.",
        )
