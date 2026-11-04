"""Opening feedback keeps every word visible and survives saved Undo/replay."""

import copy
import json
import unittest
from unittest.mock import Mock, patch

from tests import test_exp_popup_overlay as popup_fixture
from tests.grand_tree.test_opening_persistence import snapshot, undo
from tests.grand_tree.test_opening_review import review_session, activate, PLAYER_KEY
from tests.test_early_quest_item_routes import _answer_review
from tests.ui_flows.test_grand_tree_message import _fusion_palette
from ankiscape.data.quest.grand_tree import PHASE_NOTICES

if popup_fixture.HAS_AQT:
    from aqt.qt import QApplication


def use_popup(addon, collection, popup):
    addon.mw.exp_popup = popup
    addon.update_review_event_log_drawer = lambda _data: None
    collection.set_config('ankiscape_floating_xp_enabled', True)


class OpeningNoticeFeedbackTest(unittest.TestCase):
    @patch('time.time', return_value=1_793_000_000.0)
    def test_full_notices_survive_real_feedback_save_undo_and_replay(self, _time):
        with review_session(capture_notices=False) as (addon, collection, errors, _notices):
            popup = Mock()
            use_popup(addon, collection, popup)
            activate(addon)
            for phase, notice in PHASE_NOTICES.items():
                with self.subTest(phase=phase):
                    addon.save_player_data()
                    before = snapshot(addon, collection)
                    _answer_review(addon)
                    rendered = popup.show_text.call_args.args[0]
                    self.assertEqual(' '.join(rendered.splitlines()), notice)
                    if phase == 'report_warning':
                        self.assertIn('\n', rendered)
                    self.assertEqual(addon._state.player_data['review_event_log'][-1]['text'], rendered)
                    after = snapshot(addon, collection)
                    self.assertEqual(json.loads(json.dumps(collection.get_config(PLAYER_KEY))),
                                     json.loads(json.dumps(after['live'])))
                    undo(addon)
                    self.assertEqual(snapshot(addon, collection), before)
                    _answer_review(addon)
                    self.assertEqual(snapshot(addon, collection), after)
                    popup.show_text.assert_called_with(rendered)
            self.assertEqual(popup.show_text.call_count, 8)
            self.assertEqual(errors, [])


@unittest.skipUnless(popup_fixture.HAS_AQT, 'Qt is unavailable; run the Qt lane')
class OpeningNoticeGeometryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        popup_fixture.ExpPopupOverlayTest.setUpClass()

    def setUp(self):
        self.app = QApplication.instance()
        self.addCleanup(self.app.setFont, self.app.font())
        self.addCleanup(self.app.setPalette, self.app.palette())
        self.addCleanup(self.app.setStyle, self.app.style().objectName())
        # Native Anki uses 13pt; offscreen's smaller default can hide clipping.
        font = self.app.font()
        font.setPointSize(13)
        self.app.setFont(font)
        self.app.setStyle('Fusion')
        self.surface = popup_fixture.ExpPopupOverlayTest(methodName='runTest')
        self.surface.setUp()
        self.addCleanup(self.surface.tearDown)

    def _assert_visible(self, expected):
        popup = self.surface.popup
        for _ in range(5):
            QApplication.processEvents()
        self.assertTrue(popup.isVisible())
        self.assertEqual(' '.join(popup.text().splitlines()), expected)
        self.assertGreaterEqual(popup.width(), popup.sizeHint().width())
        self.assertGreaterEqual(popup.height(), popup.sizeHint().height())
        for elapsed in (0, popup._anim.duration() - 1):
            popup._anim.setCurrentTime(elapsed)
            self.assertTrue(self.surface.parent.rect().contains(popup.geometry()),
                            f'clipped popup: {popup.geometry()} in {self.surface.parent.rect()}')
            self.assertTrue(popup.visibleRegion().contains(popup.rect()))

    def _assert_opening_notices_visible(self):
        with review_session(capture_notices=False) as (addon, collection, errors, _notices):
            use_popup(addon, collection, self.surface.popup)
            activate(addon)
            for phase, notice in PHASE_NOTICES.items():
                with self.subTest(phase=phase):
                    _answer_review(addon)
                    before = copy.deepcopy(addon._state.player_data)
                    self._assert_visible(notice)
                    self.assertEqual(addon._state.player_data, before)
            self.assertEqual(errors, [])

    def test_all_four_notices_fit_native_reviewer_in_light_and_dark(self):
        default_size = self.surface.parent.size()
        for dark in (False, True):
            self.app.setPalette(_fusion_palette(dark))
            # The real reviewer is shown by the fixture before any resize.
            for size in ((default_size.width(), default_size.height()), (720, 560), (667, 574)):
                with self.subTest(dark=dark, size=size):
                    self.surface.parent.resize(*size)
                    self._assert_opening_notices_visible()
