"""The existing Dream Mentor card displays its repaired opening without actions."""

import copy
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG

try:
    from aqt.qt import QApplication, QLabel, QLineEdit, QPushButton, Qt, QWidget
except ImportError:  # pragma: no cover - plain test lane
    HAS_QT = False
else:
    HAS_QT = True
    from ankiscape.ui.ui_tab_quests import build_quests_tab


def _expected_opening():
    generated = next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == "dream_mentor")
    opening = list(generated["journal_stages"][0]["journal"])
    opening.insert(6, "After four pieces of food, he opens his eyes. Speak with him.")
    opening.insert(
        8,
        "After you raise his Spirit status up, his appetite returns, so feed him four more pieces of food.",
    )
    return tuple(opening)


@unittest.skipUnless(HAS_QT, "Qt is unavailable")
class TestDreamMentorJournalDisplay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_existing_quest_card_displays_opening_once_without_mutation(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["quests"]["dream_mentor"] = dict(started=True, progress=1, completed=False)
        selection = {"active": "Mining"}
        before_player = copy.deepcopy(player)
        before_selection = copy.deepcopy(selection)
        before_catalog = copy.deepcopy(QUEST_DATA)
        ctx = SimpleNamespace(
            player_data=player, selection=selection, warn_label=QLabel(), refreshers={},
            on_save_skill=Mock(), on_set_quest=Mock(), on_set_quest_route_choice=Mock(), refresh=Mock(),
        )
        widget = build_quests_tab(ctx)
        self.addCleanup(widget.close)
        self.addCleanup(ctx.warn_label.close)
        search = widget.findChild(QLineEdit, "questSearchInput")
        self.assertIsNotNone(search)
        search.setText("Dream Mentor")
        widget.show()
        QApplication.processEvents()
        expected = _expected_opening()
        self._assert_open_card(widget, expected)
        for _ in range(2):
            toggle = widget.findChild(QPushButton, "questToggle_dream_mentor")
            toggle.click()
            QApplication.processEvents()
            self.assertTrue(widget.findChild(QWidget, "questBody_dream_mentor").isHidden())
            self._assert_open_card(widget, expected)
        ctx.refreshers["quests"]()
        QApplication.processEvents()
        self._assert_open_card(widget, expected)
        self.assertEqual(player, before_player)
        self.assertEqual(selection, before_selection)
        self.assertEqual(QUEST_DATA, before_catalog)
        for callback in (ctx.on_save_skill, ctx.on_set_quest, ctx.on_set_quest_route_choice, ctx.refresh):
            callback.assert_not_called()

    def _assert_open_card(self, widget, expected):
        toggle = widget.findChild(QPushButton, "questToggle_dream_mentor")
        body = widget.findChild(QWidget, "questBody_dream_mentor")
        self.assertIsNotNone(toggle)
        self.assertIsNotNone(body)
        if body.isHidden():
            toggle.click()
            QApplication.processEvents()
        self.assertTrue(body.isVisible())
        layout = body.layout()
        labels = tuple(layout.itemAt(i).widget() for i in range(layout.count()))
        texts = tuple(label.text() for label in labels if isinstance(label, QLabel))
        self.assertEqual(texts.count("Stage 1"), 1)
        heading = next(i for i, label in enumerate(labels) if isinstance(label, QLabel) and label.text() == "Stage 1")
        journal_labels = labels[heading + 1:]
        self.assertEqual(len(journal_labels), 11)
        self.assertEqual(tuple(label.text() for label in journal_labels), expected)
        for label in journal_labels:
            self.assertIsInstance(label, QLabel)
            self.assertEqual(texts.count(label.text()), 1)
            self.assertTrue(label.wordWrap())
            self.assertEqual(label.textFormat(), Qt.TextFormat.RichText)
            self.assertFalse(label.font().strikeOut())
            self.assertNotIn("<s>", label.text())
