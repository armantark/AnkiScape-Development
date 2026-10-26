"""The actual final-deed bubble fits the reviewer, including after Undo."""

import copy
import json
import random
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tests import test_exp_popup_overlay as popup_fixture
from tests.one_small_favour.test_opening_feedback import FINAL_NOTICE
from tests.one_small_favour.test_opening_transactions import player
from tests.one_small_favour.test_review_dispatch import RuntimeFixture
from tests.test_combat_quest_gate import _answer_review
from ankiscape.data.quest.one_small_favour import OPENING_PROOFS, QUEST_ID

if popup_fixture.HAS_AQT:
    from aqt.qt import QApplication, QColor, QPalette


@unittest.skipUnless(popup_fixture.HAS_AQT, 'Qt is unavailable; run the Qt lane')
class OpeningPopupGeometryTest(RuntimeFixture, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        popup_fixture.ExpPopupOverlayTest.setUpClass()

    def setUp(self):
        self.app = QApplication.instance()
        self.addCleanup(self.app.setFont, self.app.font())
        # Set this before style polish: offscreen Qt uses 9pt, native Anki 13pt.
        font = self.app.font()
        font.setPointSize(13)
        self.app.setFont(font)
        # Build real Qt widgets before the registered-review harness installs
        # its fake Anki shell. The popup's sizing and placement remain real.
        self.surface = popup_fixture.ExpPopupOverlayTest(methodName='runTest')
        self.surface.setUp()
        self.addCleanup(self.surface.tearDown)
        super().setUp()
        self.addCleanup(random.setstate, random.getstate())
        timer = patch('time.time', return_value=1_793_000_000.0)
        timer.start()
        self.addCleanup(timer.stop)
        self.addCleanup(self.app.setPalette, self.app.palette())
        self.app.setStyle('Fusion')
        self.addon._show_activity_gain = self.show_activity_gain
        self.addon.mw.exp_popup = self.surface.popup
        self.addon.update_review_event_log_drawer = lambda _data: None
        self.collection.set_config = lambda key, value: self.collection._store.__setitem__(
            key, json.loads(json.dumps(value)))
        self.collection.set_config('ankiscape_floating_xp_enabled', True)

    def _palette(self, dark):
        palette = self.app.style().standardPalette()
        if dark:
            for role in (QPalette.ColorRole.Window, QPalette.ColorRole.Base, QPalette.ColorRole.Button):
                palette.setColor(role, QColor(40, 40, 40))
            for role in (QPalette.ColorRole.Text, QPalette.ColorRole.WindowText, QPalette.ColorRole.ButtonText):
                palette.setColor(role, QColor(235, 235, 235))
        self.app.setPalette(palette)

    def _assert_visible_request(self):
        popup = self.surface.popup
        for _ in range(5):
            QApplication.processEvents()
        self.assertTrue(popup.isVisible())
        self.assertEqual(' '.join(popup.text().splitlines()), OPENING_PROOFS[-1] + ' One Small Favour 2/8')
        self.assertGreater(popup.visibleRegion().boundingRect().width(), 0)
        self.assertGreaterEqual(popup.width(), popup.sizeHint().width())
        self.assertGreaterEqual(popup.height(), popup.sizeHint().height())
        # Both ends of the real float animation must stay inside the parent;
        # text equality alone would pass the original clipped one-line bubble.
        for elapsed in (0, popup._anim.duration() - 1):
            popup._anim.setCurrentTime(elapsed)
            self.assertTrue(self.surface.parent.rect().contains(popup.geometry()),
                            f'clipped popup: {popup.geometry()} in {self.surface.parent.rect()}')
            self.assertTrue(popup.visibleRegion().contains(popup.rect()))
        self.assertEqual(popup.text(), FINAL_NOTICE)

    def _answer_undo_reanswer(self):
        self.addon._state.player_data = player(6)
        self.addon.save_player_data()
        self.addon.load_player_data()
        self.addon.save_player_data()
        before = copy.deepcopy(self.addon._state.player_data)
        # This spy calls the real show_text; every assertion probes shown Qt.
        with patch.object(self.surface.popup, 'show_text', wraps=self.surface.popup.show_text) as shown:
            _answer_review(self.addon)
            self._assert_visible_request()
            after = copy.deepcopy(self.addon._state.player_data)
            self.assertEqual(after['quests'][QUEST_ID]['progress'], 2)
            self.assertEqual(after['review_event_log'][-1]['text'], FINAL_NOTICE)
            self.addon._on_state_did_undo(SimpleNamespace(operation='Answer Card'))
            self.assertEqual(self.addon._state.player_data, before)
            _answer_review(self.addon)
            self._assert_visible_request()
            self.assertEqual(self.addon._state.player_data, after)
            self.assertEqual(shown.call_count, 2)
        self.assertEqual(self.collection.get_config('ankiscape_player_data'), json.loads(json.dumps(after)))

    def test_full_request_and_counter_fit_native_window_before_and_after_undo(self):
        for dark in (False, True):
            self._palette(dark)
            # Native evidence is a 1334x1204 Retina capture (667x602 points,
            # including the title bar); also cover the 560-point laptop height.
            for width, height in ((667, 574), (720, 560)):
                with self.subTest(dark=dark, width=width, height=height):
                    self.surface.parent.resize(width, height)
                    for _ in range(5):
                        QApplication.processEvents()
                    self.assertEqual(self.surface.parent.width(), width)
                    self.assertEqual(self.surface.parent.height(), height)
                    self._answer_undo_reanswer()
