"""The Bank and Quests tabs fit the 720 px minimum dialog without sideways scrolling."""

import unittest

import pkg_alias  # noqa: F401
from tests import test_main_menu_widget as _main_menu

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QCheckBox, QLineEdit, QPoint, QScrollArea, QToolButton, QWidget

    from tests.ui_flows.qt_text_fit import text_fit_defects

# The owner's laptop dialog: the 720 px minimum width at about 560 px tall.
_OWNER_SIZE = (720, 560)
_BANK = {
    "Coal": 120, "Logs": 3, "Iron ore": 45, "Copper ore": 9, "Tin ore": 9, "Bronze bar": 4, "Iron bar": 12,
    "Raw shrimps": 30, "Shrimps": 18, "Bones": 41, "Feather": 2000, "Air rune": 4500, "Mind rune": 300,
    "Ring mould": 1, "Gold bar": 6, "Silver bar": 3, "Bronze sword": 1, "Wooden shield": 1, "Vial": 11,
}


def _pump() -> None:
    for _ in range(6):
        QApplication.processEvents()


def _sideways_scrollers(page) -> list[str]:
    return [
        f"{scroll.objectName() or type(scroll.widget()).__name__} scrolls {scroll.horizontalScrollBar().maximum()} px"
        for scroll in page.findChildren(QScrollArea)
        if scroll.isVisibleTo(page) and scroll.horizontalScrollBar().maximum() > 0
    ]


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class BankQuestFitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        self.menu = _main_menu.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()

    def tearDown(self) -> None:
        self.menu.tearDown()

    def _open(self, data, size):
        dialog = self.menu._open(data, current_skill="Mining")
        dialog.show()
        dialog.resize(*size)
        _pump()
        return dialog

    def _bank_columns(self, dialog) -> int:
        grid_scroll = dialog.findChild(QScrollArea, "bankGridScroll")
        cells = [
            cell
            for cell in grid_scroll.widget().findChildren(QToolButton)
            if cell.objectName().startswith("bankGridItem::")
        ]
        for cell in cells:
            left = cell.mapTo(grid_scroll.viewport(), QPoint(0, 0)).x()
            self.assertGreaterEqual(left, 0, cell.objectName())
            self.assertLessEqual(left + cell.width(), grid_scroll.viewport().width(), cell.objectName())
        return len({cell.x() for cell in cells})

    def test_bank_reflows_to_the_minimum_width_and_back(self) -> None:
        data = _main_menu._make_player_data()
        data["inventory"] = dict(_BANK)
        dialog = self._open(data, (1280, 752))
        _main_menu._open_bank_tab(dialog)
        # One flat section, so every row of the grid is full.
        dialog.findChild(QCheckBox, "bankAutoCategoriesCheck").setChecked(False)
        _pump()
        self.assertEqual(self._bank_columns(dialog), 12)

        dialog.resize(*_OWNER_SIZE)
        _pump()
        page = dialog.findChild(QScrollArea, "bankTabScroll")
        self.assertEqual(_sideways_scrollers(page), [])
        self.assertLess(self._bank_columns(dialog), 12)
        self.assertGreater(self._bank_columns(dialog), 2)
        # The tool belt sits below the striped Bank and wraps its rows.
        self.assertEqual(text_fit_defects(page.widget()), [])

        dialog.resize(1280, 752)
        _pump()
        self.assertEqual(self._bank_columns(dialog), 12)

    def test_quest_cards_fit_with_long_blockers_journals_and_choices(self) -> None:
        cases = (
            ("Rag and Bone Man", "rag_and_bone_man", {"started": True, "completed": False, "progress": 3}),
            ("Shield of Arrav", "shield_of_arrav", {"started": True, "completed": False, "progress": 4}),
            ("While Guthix Sleeps", "while_guthix_sleeps", None),
            ("Culinaromancer", "recipe_for_disaster_defeating_the_culinaromancer", None),
        )
        for query, quest_id, quest_state in cases:
            with self.subTest(quest_id):
                data = _main_menu._make_player_data()
                if quest_state:
                    data["quests"][quest_id] = quest_state
                dialog = self._open(data, _OWNER_SIZE)
                _main_menu._open_quests_tab(dialog)
                dialog.findChild(QLineEdit, "questSearchInput").setText(query)
                _pump()
                _main_menu._expand_quest_card(dialog, quest_id)
                _pump()
                page = dialog.findChild(QWidget, "questSearchInputBar").parentWidget()
                self.assertEqual(_sideways_scrollers(page), [])
                self.assertEqual(text_fit_defects(page), [])
                self.assertEqual(text_fit_defects(page.findChild(QScrollArea).widget()), [])
                dialog.close()


if __name__ == "__main__":
    unittest.main()
