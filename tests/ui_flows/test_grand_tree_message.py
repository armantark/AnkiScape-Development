"""The existing quest journal wraps Hazelmere's message without changing a save."""

import copy
import json
import unittest
from unittest.mock import Mock

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from tests import test_main_menu_widget as _main_menu
from tests.main_menu import fixtures as _main_menu_fixtures

if _main_menu.HAS_AQT:
    from aqt.qt import (
        QApplication, QColor, QLabel, QLineEdit, QPalette, QPoint,
        QPushButton, QScrollArea, QStyleFactory, QWidget,
    )


QUEST_ID = "the_grand_tree"
MESSAGE = (
    "A man came to me with the King's seal",
    "I gave the man Daconia rocks",
    "and Daconia rocks will kill the tree!",
)


def _player_data():
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player["quests"][QUEST_ID] = dict(started=True, completed=False, progress=2)
    return json.loads(json.dumps(player))


def _pump():
    for _ in range(30):
        QApplication.processEvents()


def _search(dialog, text):
    dialog.findChild(QLineEdit, "questSearchInput").setText(text)
    _pump()


def _quest_scroll(body):
    parent = body.parentWidget()
    while not isinstance(parent, QScrollArea):
        if parent is None:
            raise AssertionError("quest scroll area not found")
        parent = parent.parentWidget()
    return parent


def _fusion_palette(dark):
    palette = QStyleFactory.create("Fusion").standardPalette()
    if dark:
        for role, color in (
            (QPalette.ColorRole.Window, "#353535"),
            (QPalette.ColorRole.WindowText, "#eeeeee"),
            (QPalette.ColorRole.Base, "#252525"),
            (QPalette.ColorRole.AlternateBase, "#353535"),
            (QPalette.ColorRole.Text, "#eeeeee"),
            (QPalette.ColorRole.Button, "#353535"),
            (QPalette.ColorRole.ButtonText, "#eeeeee"),
            (QPalette.ColorRole.Highlight, "#3979b8"),
            (QPalette.ColorRole.HighlightedText, "#ffffff"),
        ):
            palette.setColor(role, QColor(color))
    return palette


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class GrandTreeMessageDisplayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _main_menu_fixtures.MainMenuWidgetTest.setUpClass()

    def setUp(self):
        self.menu = _main_menu_fixtures.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()
        self.skill_save = Mock()
        self.player_save = Mock()

    def tearDown(self):
        self.menu.tearDown()

    def _open(self, player):
        return self.menu._open(
            player_data=player, on_save_skill=self.skill_save,
            on_save_player_data=self.player_save,
        )

    def _callback_counts(self):
        return (len(self.menu._quest_calls), len(self.menu._quest_choice_calls),
                self.skill_save.call_count, self.player_save.call_count)

    def _message_labels(self, dialog):
        body = dialog.findChild(QWidget, "questBody_the_grand_tree")
        self.assertIsNotNone(body)
        labels = body.findChildren(QLabel)
        texts = [label.text() for label in labels]
        original = next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == QUEST_ID)
        original_lines = next(s["journal"] for s in original["journal_stages"] if s["stage"] == 2)
        expected = (original_lines[0], *MESSAGE, *original_lines[1:])
        start = texts.index("Stage 2") + 1
        self.assertEqual(tuple(texts[start:]), expected)
        for statement in MESSAGE:
            self.assertEqual(texts.count(statement), 1)
        return body, labels[start:start + 5]

    def _assert_layout(self, body, labels):
        scroll = _quest_scroll(body)
        for label in labels:
            scroll.ensureWidgetVisible(label)
            _pump()
            self.assertTrue(label.wordWrap())
            self.assertGreater(label.width(), 0)
            self.assertGreater(label.height(), 0)
            self.assertLessEqual(label.minimumSizeHint().width(), label.width())
            self.assertLessEqual(label.heightForWidth(label.width()), label.height())
            position = label.mapTo(scroll.viewport(), QPoint(0, 0))
            self.assertLess(position.y(), scroll.viewport().height())
            self.assertGreater(position.y() + label.height(), 0)
        for first, second in zip(labels, labels[1:]):
            self.assertLess(first.geometry().bottom(), second.geometry().top())
        self.assertEqual(scroll.horizontalScrollBar().maximum(), 0)

    def test_stage_two_message_labels_wrap_in_existing_journal(self):
        app = self.menu.app
        prior_style = app.style().objectName()
        prior_palette = QPalette(app.palette())
        try:
            for dark in (False, True):
                with self.subTest(dark=dark):
                    app.setStyle("Fusion")
                    app.setPalette(_fusion_palette(dark))
                    player = _player_data()
                    dialog = self._open(player)
                    dialog.show()
                    _pump()
                    default_size = dialog.size()
                    before = copy.deepcopy(player)
                    _main_menu._open_quests_tab(dialog)
                    _search(dialog, "The Grand Tree")
                    _main_menu._expand_quest_card(dialog, QUEST_ID)
                    body, labels = self._message_labels(dialog)
                    for width, height in ((default_size.width(), default_size.height()), (900, 560)):
                        with self.subTest(width=width, height=height):
                            dialog.show()
                            dialog.resize(width, height)
                            _pump()
                            self._assert_layout(body, labels)
                    self.assertEqual(player, before)
                    dialog.close()
        finally:
            app.setStyle(prior_style)
            app.setPalette(prior_palette)
            _pump()

    def test_journal_toggle_search_and_reopen_leave_gameplay_unchanged(self):
        player = _player_data()
        dialog = self._open(player)
        dialog.show()
        _pump()
        before = copy.deepcopy(player)
        counts = self._callback_counts()
        _main_menu._open_quests_tab(dialog)
        _search(dialog, "The Grand Tree")
        _main_menu._expand_quest_card(dialog, QUEST_ID)
        self._message_labels(dialog)
        dialog.findChild(QPushButton, "questToggle_the_grand_tree").click()
        _pump()
        self.assertTrue(dialog.findChild(QWidget, "questBody_the_grand_tree").isHidden())
        _main_menu._expand_quest_card(dialog, QUEST_ID)
        _search(dialog, "Rune Mysteries")
        self.assertIsNone(dialog.findChild(QWidget, "questBody_the_grand_tree"))
        _search(dialog, "The Grand Tree")
        _main_menu._expand_quest_card(dialog, QUEST_ID)
        self._message_labels(dialog)
        self.assertEqual(player, before)
        self.assertEqual(self._callback_counts(), counts)
        dialog.close()

        reopened = json.loads(json.dumps(player))
        dialog = self._open(reopened)
        dialog.show()
        _pump()
        _main_menu._open_quests_tab(dialog)
        _search(dialog, "The Grand Tree")
        _main_menu._expand_quest_card(dialog, QUEST_ID)
        self._message_labels(dialog)
        self.assertEqual(reopened, before)
        self.assertEqual(self._callback_counts(), counts)


if __name__ == "__main__":
    unittest.main()
