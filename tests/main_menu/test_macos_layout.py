"""Every main-menu tab keeps its text whole and no two widgets of a row overlap, as macOS lays them out.

macOS lays a check box out by a rect it trims from the native box (2 px left,
3 top, 9 right, 4 bottom, measured under Qt 6 on macOS 26). The combat panel's
stylesheet draws a smaller box, so the trimmed rect no longer held its text,
and in native Anki "Use prayers in fights" ran under "Book". Offscreen Fusion
trims nothing, so this suite runs the real widgets under a style that trims as
macOS does, with the application font at 125% of its size, at the dialog's
default 900 by 560 and at its 720 minimum width.
"""

from __future__ import annotations

import unittest

from tests.main_menu import fixtures
from tests.test_main_menu_widget import HAS_AQT, _find_main_tabs, _make_player_data, _open_equipment_tab

if HAS_AQT:
    from aqt.qt import QApplication, QFont, QProxyStyle, QStyle, QStyleFactory, Qt, QWidget

    from tests.ui_flows.qt_text_fit import text_fit_defects

    class _MacLayoutItemStyle(QProxyStyle):
        def subElementRect(self, element, option, widget):
            if element == QStyle.SubElement.SE_CheckBoxLayoutItem:
                return option.rect.adjusted(2, 3, -9, -4)
            return super().subElementRect(element, option, widget)


def _pump() -> None:
    for _ in range(6):
        QApplication.processEvents()


def _overlaps(root) -> list[str]:
    """Each pair of visible sibling widgets under ``root`` whose rects intersect."""
    found = []
    for parent in [root, *root.findChildren(QWidget)]:
        children = [
            child
            for child in parent.findChildren(QWidget, options=Qt.FindChildOption.FindDirectChildrenOnly)
            if child.isVisibleTo(root) and not child.isWindow()
        ]
        for index, first in enumerate(children):
            for second in children[index + 1 :]:
                if first.geometry().intersects(second.geometry()):
                    found.append(
                        f"{first.objectName() or type(first).__name__} {first.geometry().getRect()}"
                        f" x {second.objectName() or type(second).__name__} {second.geometry().getRect()}"
                    )
    return found


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MacLayoutTest(fixtures.MainMenuWidgetTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls._style_name = cls.app.style().name()
        cls._font = QFont(cls.app.font())
        cls.app.setStyle(_MacLayoutItemStyle(QStyleFactory.create("Fusion")))
        wide = QFont(cls._font)
        wide.setPointSizeF(cls._font.pointSizeF() * 1.25)
        cls.app.setFont(wide)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.setStyle(QStyleFactory.create(cls._style_name))
        cls.app.setFont(cls._font)
        super().tearDownClass()

    def _equipment_menu(self, width: int):
        from ankiscape.core.action_queue import action_queue_pure, add_queue_entry_pure

        queue = action_queue_pure({})
        for count in (50, 60):
            queue, _ok = add_queue_entry_pure(
                queue, {"kind": "skill", "skill": "Smithing", "target": "smelt_iron_bar"}, count
            )
        player = _make_player_data()
        player.update({
            "attack_level": 70, "strength_level": 72, "defense_level": 70, "prayer_level": 43,
            "combat_prayer_points": 430, "magic_level": 94, "current_combat_target": "cave_crawler",
            "equipment": {"weapon": "Rune scimitar"}, "action_queue": queue,
        })
        dialog = self._open(
            player,
            current_skill="Combat",
            loot_override_rows=({"item": "Bones", "mode": "keep"}, {"item": "Feather", "mode": "leave"}),
            on_action_queue_command=lambda _command, _payload: None,
        )
        dialog.show()
        dialog.resize(width, 560)
        _pump()
        _open_equipment_tab(dialog)
        _pump()
        return dialog

    def test_no_font_or_style_margin_makes_two_widgets_of_a_row_overlap(self):
        for width in (720, 900):
            with self.subTest(width=width):
                dialog = self._equipment_menu(width)
                for name in ("equipmentCombatSetupPanel", "actionQueuePanel"):
                    panel = dialog.findChild(QWidget, name)
                    self.assertTrue(panel.isVisible(), name)
                    self.assertEqual(_overlaps(panel), [], name)
                dialog.close()

    def test_every_tab_keeps_its_text_whole_without_two_widgets_of_a_row_overlapping(self):
        for width in (900, 720):
            dialog = self._open(_make_player_data(), current_skill="Mining")
            dialog.show()
            dialog.resize(width, 560)
            _pump()
            tabs = _find_main_tabs(dialog)
            for index in range(tabs.count()):
                with self.subTest(width=width, tab=tabs.tabText(index)):
                    tabs.setCurrentIndex(index)
                    _pump()
                    page = tabs.widget(index)
                    self.assertEqual(text_fit_defects(page), [])
                    self.assertEqual(_overlaps(page), [])
            dialog.close()


if __name__ == "__main__":
    unittest.main()
