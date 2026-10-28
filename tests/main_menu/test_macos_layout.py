"""Every main-menu tab keeps its text whole and no two widgets of a row overlap, as macOS lays them out.

macOS lays a check box out by a rect it trims from the native box (2 px left,
3 top, 9 right, 4 bottom, measured under Qt 6 on macOS 26). The combat panel's
stylesheet draws a smaller box, so the trimmed rect no longer held its text,
and in native Anki "Use prayers in fights" ran under "Book". Offscreen Fusion
trims nothing, so this suite runs the real widgets under a style that trims as
macOS does, with the application font at 125% of its size, at the dialog's
default 900 by 560 and at its 720 minimum width.

macOS also draws its scroll bars over the content, so a bar that appears never
narrows a viewport. Fusion's reserved bars narrowed the Bank grid once more
after the tab opened, and that late resize re-laid out a grid left squeezed for
its old column count, so the style overlays bars as macOS does.
"""

from __future__ import annotations

import unittest
from itertools import combinations

from tests.main_menu import fixtures
from tests.test_main_menu_widget import HAS_AQT, _find_main_tabs, _make_player_data, _open_bank_tab, _open_equipment_tab

if HAS_AQT:
    from aqt.qt import QAbstractScrollArea, QApplication, QFont, QProxyStyle, QSize, QStyle, QStyleFactory, Qt, QWidget

    from tests.ui_flows.qt_text_fit import text_fit_defects

    class _MacLayoutItemStyle(QProxyStyle):
        def subElementRect(self, element, option, widget):
            if element == QStyle.SubElement.SE_CheckBoxLayoutItem:
                return option.rect.adjusted(2, 3, -9, -4)
            return super().subElementRect(element, option, widget)

        def styleHint(self, hint, option=None, widget=None, returnData=None):
            if hint == QStyle.StyleHint.SH_ScrollBar_Transient:
                return 1
            return super().styleHint(hint, option, widget, returnData)

        def pixelMetric(self, metric, option=None, widget=None):
            if metric == QStyle.PixelMetric.PM_ScrollView_ScrollBarOverlap:
                return super().pixelMetric(QStyle.PixelMetric.PM_ScrollBarExtent, option, widget)
            return super().pixelMetric(metric, option, widget)


def _pump() -> None:
    for _ in range(6):
        QApplication.processEvents()


def _overlaps(root) -> list[str]:
    """Each pair of visible sibling widgets under ``root`` whose rects intersect.

    A scroll area's bars overlay its viewport, as macOS draws them.
    """
    found = []
    for parent in [root, *root.findChildren(QWidget)]:
        if isinstance(parent, QAbstractScrollArea):
            continue
        children = [
            child
            for child in parent.findChildren(QWidget, options=Qt.FindChildOption.FindDirectChildrenOnly)
            if child.isVisibleTo(root) and not child.isWindow()
        ]
        for first, second in combinations(children, 2):
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

    def test_a_bank_as_big_as_the_owners_keeps_every_row_and_heading_whole(self):
        from ankiscape.core.constants import ITEM_DEFINITIONS
        from ankiscape.core.item_registry import item_definitions_by_storage_key

        kinds: dict[str, list[str]] = {}
        for definition in item_definitions_by_storage_key(ITEM_DEFINITIONS).values():
            kinds.setdefault(definition.category, []).append(definition.storage_key)
        # The owner's Bank holds 154 kinds; up to 11 from each of the 14 auto categories gives 149.
        names = [name for category_kinds in kinds.values() for name in category_kinds[:11]]
        default = None
        for size in ("default", "560 tall", "full width"):
            player = _make_player_data()
            player["inventory"] = {name: 1 + index * 541 for index, name in enumerate(names)}
            dialog = self._open(player, current_skill="Mining")
            dialog.show()
            _pump()
            default = default or dialog.size()
            dialog.resize(
                {"default": default, "560 tall": QSize(default.width(), 560), "full width": QSize(1728, default.height())}[size]
            )
            _pump()
            # The first open builds the grid, as a player's first Bank click does.
            _open_bank_tab(dialog)
            _pump()
            with self.subTest(size=size):
                self.assertEqual(_overlaps(dialog.findChild(QWidget, "bankGrid")), [])
            dialog.close()


if __name__ == "__main__":
    unittest.main()
