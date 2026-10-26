"""Watchtower's full feedback fits the real floating label at laptop sizes."""

import unittest

import pkg_alias  # noqa: F401
from tests import test_exp_popup_overlay as overlay
from tests.quest_catalog import test_watchtower_opening_ui as journal_ui
from tests.quest_catalog.test_watchtower_opening import player
from tests.runtime_actions.quests.test_watchtower_review import MESSAGES
from tests.test_runtime_actions import _context
from ankiscape.runtime.runtime_actions_quest import handle_quest_answer

if overlay.HAS_AQT:
    from aqt.qt import QFont


@unittest.skipUnless(overlay.HAS_AQT, 'Qt/Anki runtime is not installed')
class WatchtowerToastTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        overlay.ExpPopupOverlayTest.setUpClass()
        cls.app = overlay.ExpPopupOverlayTest.app

    def setUp(self):
        self.harness = overlay.ExpPopupOverlayTest('runTest')
        self.harness.setUp()
        self.addCleanup(self.harness.tearDown)
        self.addCleanup(self.app.setPalette, self.app.palette())
        self.addCleanup(self.app.setStyle, self.app.style().objectName())
        self.app.setStyle('Fusion')

    def test_each_phase_fits_light_and_dark_laptop_reviewer(self):
        for dark in (False, True):
            journal_ui.WatchtowerOpeningUITest._palette(self, dark)
            for width in (560, 900):
                for font_size in (13, 16):
                    with self.subTest(dark=dark, width=width, font_size=font_size):
                        self._assert_phase_toasts_fit(width, font_size)

    def _assert_phase_toasts_fit(self, width, font_size):
        parent, popup = self.harness.parent, self.harness.popup
        parent.resize(width, 560)
        popup.setFont(QFont('Arial', font_size))
        for _ in range(3):
            self.app.processEvents()
        self.assertEqual(parent.width(), width)
        self.assertEqual(parent.height(), 560)
        data = player()
        calls = {'xp': [], 'saves': 0, 'errors': []}
        ctx = _context(data, calls)
        messages = []

        def show_gain(text):
            messages.append(text)
            popup.show_text(text)

        ctx.show_activity_gain = show_gain
        for phase, expected in enumerate(MESSAGES):
            self.assertTrue(handle_quest_answer(ctx))
            for _ in range(3):
                self.app.processEvents()
            self.assertEqual(len(messages), phase + 1)
            self.assertEqual(' '.join(popup.text().split()), expected)
            self.assertIn('\n', popup.text())
            self.assertTrue(popup.isVisible())
            self.assertTrue(parent.rect().contains(popup.geometry()), popup.geometry())
            # Geometry alone would miss a label whose own text was truncated.
            metrics = popup.fontMetrics()
            for line in popup.text().splitlines():
                self.assertLessEqual(metrics.horizontalAdvance(line), popup.contentsRect().width())
            self.assertGreaterEqual(popup.height(), metrics.lineSpacing() * len(popup.text().splitlines()))
            self.assertEqual(calls['saves'], phase + 1)
        self.assertEqual(calls['errors'], [])
