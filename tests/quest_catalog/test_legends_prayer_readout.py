"""Legends' composed Prayer requirement renders without changing a save."""

import copy
import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
from .test_quest_root_prerequisites import REQUIREMENTS, _ready_legends_player

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    import aqt  # noqa: F401
    from aqt.qt import QApplication, QEvent, QLabel, QPushButton, QWidget
    HAS_AQT = True
except Exception:  # pragma: no cover - environment without aqt installed
    HAS_AQT = False


def _quest_context(player):
    return SimpleNamespace(
        player_data=player,
        selection={"active": "Mining"},
        warn_label=QLabel(),
        refreshers={},
        on_save_skill=Mock(),
        on_set_quest=Mock(),
        on_set_quest_route_choice=Mock(),
        refresh=Mock(),
    )


def _process_events():
    for _ in range(4):
        QApplication.processEvents()


def _close_widget(widget):
    widget.close()
    widget.deleteLater()
    QApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    _process_events()


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class TestLegendsPrayerReadout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_legends_requirement_readout_and_view_nonmutation(self):
        from ankiscape.ui.ui_tab_quests import build_quests_tab

        for level in (41, 42, 43):
            with self.subTest(prayer_level=level):
                player = _ready_legends_player()
                player["prayer_level"] = level
                before = copy.deepcopy(player)
                ctx = _quest_context(player)
                self.addCleanup(_close_widget, ctx.warn_label)
                page = build_quests_tab(ctx)
                self.addCleanup(_close_widget, page)
                page.show()
                page.resize(900, 560)
                _process_events()

                toggle = page.findChild(QPushButton, "questToggle_legends_quest")
                body = page.findChild(QWidget, "questBody_legends_quest")
                self.assertIsNotNone(toggle)
                self.assertIsNotNone(body)
                toggle.click()
                _process_events()
                labels = [label.text() for label in body.findChildren(QLabel)
                          if label.text().startswith("Requires: ")]
                self.assertEqual(labels, ["Requires: " + ", ".join(REQUIREMENTS)])
                self.assertIn("Prayer 42", labels[0])
                self.assertNotIn("Prayer 43", labels[0])

                toggle.click()
                _process_events()
                toggle.click()
                page.repaint()
                _process_events()
                page.close()
                _process_events()
                self.assertEqual(player, before)
                for callback in (ctx.on_save_skill, ctx.on_set_quest,
                                 ctx.on_set_quest_route_choice, ctx.refresh):
                    callback.assert_not_called()
