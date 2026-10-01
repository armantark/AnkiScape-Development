"""Offscreen coverage for the shared Qt text-fit probes."""

import unittest

import pkg_alias  # noqa: F401
from tests import test_main_menu_widget as _main_menu

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QPushButton, QStyleFactory, QWidget


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class QtTextFitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        self.root = QWidget()
        self.style = QStyleFactory.create("Fusion")
        self.root.setStyle(self.style)
        self.root.show()
        self.root.resize(320, 80)
        self._settle()

    def tearDown(self) -> None:
        self.root.close()
        self.root.deleteLater()
        self._settle()

    @staticmethod
    def _settle() -> None:
        for _ in range(4):
            QApplication.processEvents()

    def _button(self, text: str, x: int, width: int, height: int = 30) -> QPushButton:
        button = QPushButton(text, self.root)
        button.setGeometry(x, 20, width, height)
        button.show()
        self._settle()
        return button

    def test_buttons_can_fit_below_the_styles_preferred_width(self) -> None:
        from tests.ui_flows.qt_text_fit import text_fit_defects

        buttons = []
        x = 0
        for text, width in (("1", 44), ("5", 44), ("10", 44), ("50", 44), ("All", 50)):
            button = self._button(text, x, width)
            buttons.append(button)
            x += width + 4

        self.assertTrue(all(button.sizeHint().width() > button.width() for button in buttons))
        self.assertEqual(text_fit_defects(self.root), [])

    def test_width_clipping_is_detected_and_clears_when_room_is_added(self) -> None:
        from tests.ui_flows.qt_text_fit import text_fit_defects

        button = self._button("Definitely clipped", 20, 40)
        self.assertEqual(len(text_fit_defects(self.root)), 1)
        self.assertIn("'Definitely clipped' is clipped", text_fit_defects(self.root)[0])

        button.resize(180, 30)
        self._settle()
        self.assertEqual(text_fit_defects(self.root), [])

    def test_height_clipping_is_detected_and_clears_when_room_is_added(self) -> None:
        from tests.ui_flows.qt_text_fit import text_fit_defects

        button = self._button("Tall", 20, 120, 8)
        self.assertEqual(len(text_fit_defects(self.root)), 1)
        self.assertIn("'Tall' is clipped", text_fit_defects(self.root)[0])

        button.resize(120, 30)
        self._settle()
        self.assertEqual(text_fit_defects(self.root), [])


if __name__ == "__main__":
    unittest.main()
