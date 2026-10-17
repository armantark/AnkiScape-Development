"""Offscreen coverage for the shared Qt text-fit probes."""

import unittest

import pkg_alias  # noqa: F401
from tests import test_main_menu_widget as _main_menu

if _main_menu.HAS_AQT:
    from aqt.qt import (
        QApplication,
        QMessageBox,
        QPushButton,
        QStyleFactory,
        QTreeWidget,
        QTreeWidgetItem,
        QWidget,
    )


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
        self.root.resize(480, 80)
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

    def test_tree_row_cut_short_by_its_column_is_reported(self) -> None:
        from tests.ui_flows.qt_text_fit import text_fit_defects

        tree = QTreeWidget(self.root)
        tree.setHeaderHidden(True)
        tree.setGeometry(0, 0, 480, 80)
        branch = QTreeWidgetItem(tree, ["Herblore"])
        QTreeWidgetItem(branch, ["Gather snape grass at the Hobgoblin Peninsula"])
        tree.show()
        for width, expanded, expected in ((480, True, 0), (140, False, 0), (140, True, 1)):
            with self.subTest(width=width, expanded=expanded):
                tree.resize(width, 80)
                branch.setExpanded(expanded)
                self._settle()
                defects = text_fit_defects(self.root)
                self.assertEqual(len(defects), expected, defects)
                if expected:
                    self.assertIn("'Gather snape grass at the Hobgoblin Peninsula' is clipped", defects[0])

    def test_message_box_buttons_are_measured(self) -> None:
        from tests.ui_flows.qt_text_fit import text_fit_defects

        box = QMessageBox(
            QMessageBox.Icon.Question,
            "Lamp",
            "Claim this XP lamp now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        box.setStyle(self.style)
        box.show()
        self._settle()
        self.assertEqual(text_fit_defects(box), [])
        box.close()


if __name__ == "__main__":
    unittest.main()
