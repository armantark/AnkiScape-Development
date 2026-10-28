"""The main menu keeps every tab name whole, with one scroll arrow at each end of the bar that reaches every tab."""

from __future__ import annotations

import unittest

import pkg_alias  # noqa: F401
from tests import test_main_menu_widget as _main_menu
from tests.main_menu import fixtures as test_main_menu_widget_behavior

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QStyle, QStyleFactory, QStyleOptionTab, Qt, QToolButton


def _pump() -> None:
    for _ in range(30):
        QApplication.processEvents()


def _label_is_whole(bar: "QTabBar", index: int) -> bool:
    option = QStyleOptionTab()
    option.initFrom(bar)
    option.rect = bar.tabRect(index)
    option.text = bar.tabText(index)
    option.icon = bar.tabIcon(index)
    option.iconSize = bar.iconSize()
    option.shape = bar.shape()
    option.documentMode = bar.documentMode()
    # QTabBar's paint event elides each label to exactly this rectangle, so the
    # check sees the tab's padding, icon and margins the way Qt draws them.
    text_rect = bar.style().subElementRect(QStyle.SubElement.SE_TabBarTabText, option, bar)
    elided = option.fontMetrics.elidedText(
        option.text, Qt.TextElideMode.ElideRight, text_rect.width(), Qt.TextFlag.TextShowMnemonic.value
    )
    return elided == option.text


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
        test_main_menu_widget_behavior.MainMenuWidgetTest.setUpClass()
        # The owner saw truncated names under Qt's macOS style, which elides tab
        # text and hides the scroll arrows unless the menu asks otherwise. The
        # menu builds its arrow style on the application style.
        cls._style_name = QApplication.style().name()
        QApplication.setStyle(QStyleFactory.create("macOS"))

    @classmethod
    def tearDownClass(cls) -> None:
        QApplication.setStyle(QStyleFactory.create(cls._style_name))

    def setUp(self) -> None:
        self.menu = test_main_menu_widget_behavior.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()

    def tearDown(self) -> None:
        self.menu.tearDown()

    def test_macos_style_keeps_tab_names_whole_with_an_arrow_at_each_end_that_reaches_every_tab(self) -> None:
        for width in (720, 980):
            with self.subTest(width=width):
                dialog = self.menu._open(_main_menu._make_player_data(), current_skill="Mining")
                dialog.show()
                dialog.resize(width, 560)
                tabs = _main_menu._find_main_tabs(dialog)
                bar = tabs.tabBar()
                _pump()

                cut = [bar.tabText(index) for index in range(bar.count()) if not _label_is_whole(bar, index)]
                self.assertEqual(cut, [])

                arrows = {button.arrowType(): button for button in bar.findChildren(QToolButton)}
                right, left = arrows[Qt.ArrowType.RightArrow], arrows[Qt.ArrowType.LeftArrow]
                self.assertTrue(left.isVisible() and right.isVisible())
                self.assertEqual((left.x(), right.geometry().right()), (0, bar.width() - 1))
                self.assertEqual((left.isEnabled(), right.isEnabled()), (False, True))

                _scroll_to_end(right, bar.count())
                self.assertEqual((left.isEnabled(), right.isEnabled()), (True, False))
                self.assertLess(bar.tabRect(bar.count() - 1).right(), right.x())
                _scroll_to_end(left, bar.count())
                self.assertEqual((left.isEnabled(), right.isEnabled()), (False, True))
                self.assertGreater(bar.tabRect(0).left(), left.geometry().right())

                hidden = []
                for index in [*range(bar.count()), *reversed(range(bar.count()))]:
                    tabs.setCurrentIndex(index)
                    _pump()
                    rect = bar.tabRect(index)
                    if rect.left() <= left.geometry().right() or rect.right() >= right.x():
                        hidden.append((bar.tabText(index), rect.left(), rect.right()))
                self.assertEqual(hidden, [])


if __name__ == "__main__":
    unittest.main()
