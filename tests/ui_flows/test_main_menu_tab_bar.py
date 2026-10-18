"""The main menu keeps every tab name whole and its scroll arrows reach every tab."""

from __future__ import annotations

import unittest

import pkg_alias  # noqa: F401
from tests import test_main_menu_widget as _main_menu

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QStyleFactory, Qt, QToolButton


def _pump() -> None:
    for _ in range(30):
        QApplication.processEvents()


def _scroll_to_end(arrow: "QToolButton", tab_count: int) -> None:
    for _ in range(tab_count):
        if not arrow.isEnabled():
            return
        arrow.click()
        _pump()


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuTabBarTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        self.menu = _main_menu.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()

    def tearDown(self) -> None:
        self.menu.tearDown()

    def test_macos_style_keeps_tab_names_whole_and_scrolls_to_every_tab(self) -> None:
        # The owner saw truncated names under Qt's macOS style, which elides tab
        # text and hides the scroll arrows unless the menu asks otherwise.
        for width in (720, 980):
            with self.subTest(width=width):
                dialog = self.menu._open(_main_menu._make_player_data(), current_skill="Mining")
                dialog.show()
                dialog.resize(width, 560)
                tabs = _main_menu._find_main_tabs(dialog)
                bar = tabs.tabBar()
                style = QStyleFactory.create("macOS")
                style.setParent(dialog)
                tabs.setStyle(style)
                bar.setStyle(style)
                _pump()

                for index in range(bar.count()):
                    label = bar.tabText(index)
                    text_width = bar.fontMetrics().horizontalAdvance(label) + tabs.iconSize().width()
                    self.assertGreaterEqual(bar.tabRect(index).width(), text_width, label)

                arrows = {button.arrowType(): button for button in bar.findChildren(QToolButton)}
                right, left = arrows[Qt.ArrowType.RightArrow], arrows[Qt.ArrowType.LeftArrow]
                self.assertTrue(right.isVisible() and right.isEnabled())
                _scroll_to_end(right, bar.count())
                self.assertLessEqual(bar.tabRect(bar.count() - 1).right(), bar.width())
                _scroll_to_end(left, bar.count())
                self.assertGreaterEqual(bar.tabRect(0).left(), 0)


if __name__ == "__main__":
    unittest.main()
