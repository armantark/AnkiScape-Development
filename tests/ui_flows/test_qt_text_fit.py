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

    def test_text_clipped_in_either_dimension_is_reported(self) -> None:
        from tests.ui_flows.qt_text_fit import text_fit_defects

        for text, width, height in (("Definitely clipped", 40, 30), ("Tall", 120, 8)):
            with self.subTest(text=text):
                button = QPushButton(text, self.root)
                button.setGeometry(20, 20, width, height)
                button.show()
                self._settle()
                defects = text_fit_defects(self.root)
                self.assertEqual(len(defects), 1)
                self.assertIn(f"'{text}' is clipped", defects[0])
                button.setParent(None)
                self._settle()


if __name__ == "__main__":
    unittest.main()
