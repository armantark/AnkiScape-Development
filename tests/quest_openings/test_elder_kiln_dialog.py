"""The hatching dialog's real controls, terminal rendering and geometry in both palettes."""

import copy
import unittest

import pkg_alias  # noqa: F401
from tests import allow_modal_dialogs, test_main_menu_widget as fixture
from tests.main_menu import fixtures as menu_fixture
from tests.quest_openings.test_elder_kiln_data import PROOF, QUEST_ID, player
from tests.quest_openings.test_elder_kiln_logic import best_command
from ankiscape.data.quest.elder_kiln import FAILURE_COPY, REQUEST_COPY, STATE_KEY, SUCCESS_COPY, SPELL_IDS
from ankiscape.logic_pure.logic_pure_quest import start_quest_pure
from ankiscape.core.constants import QUEST_DATA

if fixture.HAS_AQT:
    from aqt.qt import QPoint, QRect, QTimer
    from ankiscape.core import logic as core_logic
    from ankiscape.runtime.elder_kiln_review import _HatchingSession
    from ankiscape.ui.elder_kiln_hatching_dialog import ElderKilnHatchingDialog, WINDOW_TITLE

SIZES = ((720, 640), (720, 560))


@unittest.skipUnless(fixture.HAS_AQT, "Qt/Anki runtime is not installed")
class ElderKilnDialogTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        menu_fixture.MainMenuWidgetTest.setUpClass()
        cls.app = menu_fixture.MainMenuWidgetTest.app

    def setUp(self):
        original = self.app.palette()
        self.addCleanup(self.app.setPalette, original)
        self.app.setStyle("Fusion")
        self.session = self._session()

    def _session(self):
        data, ok = start_quest_pure(player(started=True), QUEST_ID, QUEST_DATA)
        self.assertTrue(ok)
        return _HatchingSession(data, QUEST_ID, lambda: 0.5)

    def _palette(self, dark):
        palette = fixture.QPalette()
        roles = fixture.QPalette.ColorRole
        colors = {
            roles.Window: "#2d2d2d" if dark else "#eeeeee",
            roles.WindowText: "#eeeeee" if dark else "#202020",
            roles.Base: "#202020" if dark else "#ffffff",
            roles.Text: "#eeeeee" if dark else "#202020",
            roles.Button: "#373737" if dark else "#eeeeee",
            roles.ButtonText: "#eeeeee" if dark else "#202020",
            roles.Mid: "#080808" if dark else "#888888",
        }
        for role, color in colors.items():
            palette.setColor(role, fixture.QColor(color))
        self.app.setPalette(palette)

    def _settle(self):
        for _ in range(4):
            self.app.processEvents()

    def _open(self, size=SIZES[0]):
        dialog = ElderKilnHatchingDialog(self.session.command, self.session.observation())
        self.addCleanup(dialog.deleteLater)
        dialog.show()
        dialog.resize(*size)
        self._settle()
        return dialog

    def _button(self, dialog, name):
        return dialog.findChild(fixture.QPushButton, name)

    def _spells(self, dialog):
        return [self._button(dialog, f"elderKilnSpell_{spell}") for spell in SPELL_IDS]

    def _text(self, dialog, name):
        return dialog.findChild(fixture.QLabel, name).text()

    def _click_until(self, dialog, phase, chooser):
        for _ in range(600):
            if self.session.data[STATE_KEY]["phase"] == phase:
                return
            name = chooser(self.session.data[STATE_KEY])
            target = "elderKilnWaitStep" if name == "wait_step" else f"elderKilnSpell_{name.removeprefix('cast:')}"
            self._button(dialog, target).click()
        self.fail(f"never reached {phase}")

    def test_offer_spell_and_wait_controls_run_real_commands(self):
        dialog = self._open()
        self.assertEqual(dialog.windowTitle(), WINDOW_TITLE)
        self.assertEqual(WINDOW_TITLE, "The Elder Kiln — egg-hatching review exercise")
        self.assertEqual(self._text(dialog, "elderKilnStory"), REQUEST_COPY)
        self.assertFalse(any(button.isEnabled() for button in self._spells(dialog)))
        self._button(dialog, "elderKilnOffer").click()
        self.assertEqual(self.session.data[STATE_KEY]["phase"], "preparing")
        self.assertFalse(self._button(dialog, "elderKilnOffer").isVisible())
        self.assertTrue(all(button.isEnabled() for button in self._spells(dialog)))
        self.assertEqual(self._text(dialog, "elderKilnHelper_0"), "Mej-Ak: Firing now!")
        self.assertEqual(self._text(dialog, "elderKilnHelper_1"), "Mej-Jeh is watching the egg.")
        self._button(dialog, "elderKilnSpell_fire_blast").click()
        state = self.session.data[STATE_KEY]
        self.assertEqual((state["heat"], state["steps"]), (9, 1))
        self.assertIn("Heat 9", self._text(dialog, "elderKilnHeat"))
        self._button(dialog, "elderKilnWaitStep").click()
        self.assertEqual(self.session.data[STATE_KEY]["steps"], 2)
        self._button(dialog, "elderKilnWaitChange").click()
        state = self.session.data[STATE_KEY]
        self.assertEqual(state["steps"], 5)
        self.assertEqual(dialog.findChild(fixture.QProgressBar, "elderKilnProgress").value(), state["progress"])
        self.assertEqual(self._text(dialog, "elderKilnProgressText"), f"Hatching {state['progress']}%")
        self.assertIn("Mej-Ak’s fire spell warmed the egg.", self._text(dialog, "elderKilnEvents"))

    def test_close_escape_and_window_close_pause_without_a_command(self):
        for close in ("button", "escape", "window"):
            with self.subTest(close=close):
                dialog = self._open()
                self._button(dialog, "elderKilnOffer").click()
                before = copy.deepcopy(self.session.data)
                if close == "button":
                    self._button(dialog, "elderKilnClose").click()
                elif close == "escape":
                    fixture.QTest.keyClick(dialog, fixture.Qt.Key.Key_Escape)
                else:
                    dialog.close()
                self._settle()
                self.assertFalse(dialog.isVisible())
                self.assertEqual(self.session.data, before)

    def test_failure_disables_play_and_enables_retry(self):
        dialog = self._open()
        self._button(dialog, "elderKilnOffer").click()
        self._click_until(dialog, "active", lambda _state: "wait_step")
        self._click_until(dialog, "failed", lambda _state: "cast:water_wave")
        self._settle()
        self.assertEqual(self._text(dialog, "elderKilnStory"), FAILURE_COPY)
        retry = self._button(dialog, "elderKilnRetry")
        self.assertTrue(retry.isEnabled())
        for name in ("elderKilnWaitStep", "elderKilnWaitChange"):
            self.assertFalse(self._button(dialog, name).isEnabled())
        self.assertFalse(any(button.isEnabled() for button in self._spells(dialog)))
        retry.click()
        self.assertEqual(self.session.data[STATE_KEY]["phase"], "preparing")
        self.assertFalse(retry.isEnabled())

    def test_success_keeps_the_outcome_until_close(self):
        dialog = self._open()
        self._button(dialog, "elderKilnOffer").click()
        self._click_until(dialog, "hatched", best_command)
        for _ in range(3):
            self._settle()
            self.assertTrue(dialog.isVisible())
        self.assertEqual(self._text(dialog, "elderKilnStory"), SUCCESS_COPY)
        self.assertEqual(self.session.data["quest_action_proofs"], [PROOF])
        simulation = [*self._spells(dialog), *(self._button(dialog, name) for name in (
            "elderKilnWaitStep", "elderKilnWaitChange", "elderKilnRetry"))]
        self.assertFalse(any(button.isEnabled() for button in simulation))
        self.assertFalse(self._button(dialog, "elderKilnOffer").isVisible())
        self.assertTrue(self._button(dialog, "elderKilnClose").isEnabled())
        self._button(dialog, "elderKilnClose").click()
        self._settle()
        self.assertFalse(dialog.isVisible())

    def test_bridge_runs_the_dialog_modally_until_the_player_closes_it(self):
        seen = []

        def drive():
            dialog = next(widget for widget in self.app.topLevelWidgets()
                          if isinstance(widget, ElderKilnHatchingDialog) and widget.isVisible())
            seen.append(dialog.isModal())
            self._button(dialog, "elderKilnOffer").click()
            dialog.reject()

        QTimer.singleShot(0, drive)
        with allow_modal_dialogs():
            core_logic.present_elder_kiln_hatching(self.session.command, self.session.observation())
        self.assertEqual(seen, [True])
        self.assertEqual(self.session.data[STATE_KEY]["phase"], "preparing")

    def test_wrapped_text_and_reachable_controls_in_both_palettes(self):
        for dark in (False, True):
            for size in SIZES:
                for phase in ("request", "active", "hatched"):
                    with self.subTest(dark=dark, size=size, phase=phase):
                        self._palette(dark)
                        self.session = self._session()
                        dialog = self._open(size)
                        if phase != "request":
                            self._button(dialog, "elderKilnOffer").click()
                            self._click_until(dialog, phase, best_command)
                            self._settle()
                        self._assert_geometry(dialog, size)

    def _assert_geometry(self, dialog, size):
        self.assertEqual((dialog.width(), dialog.height()), size)
        self.assertLessEqual(dialog.minimumSizeHint().height(), 560)
        bounds = dialog.rect()
        widgets = [widget for widget in dialog.findChildren(fixture.QWidget)
                   if widget.isVisible() and isinstance(widget, (fixture.QPushButton, fixture.QLabel, fixture.QProgressBar))]
        boxes = {}
        for widget in widgets:
            box = QRect(widget.mapTo(dialog, QPoint(0, 0)), widget.size())
            self.assertTrue(bounds.contains(box), widget.objectName())
            self.assertNotIn("palette(mid)", widget.styleSheet())
            if isinstance(widget, fixture.QLabel):
                self.assertTrue(widget.wordWrap(), widget.objectName())
                self.assertGreaterEqual(widget.height(), widget.heightForWidth(widget.width()), widget.objectName())
            if isinstance(widget, fixture.QPushButton):
                self.assertGreaterEqual(widget.width(), widget.sizeHint().width(), widget.text())
            boxes[widget.objectName() or str(id(widget))] = box
        names = sorted(boxes)
        for index, first in enumerate(names):
            for second in names[index + 1:]:
                self.assertFalse(boxes[first].intersects(boxes[second]), (first, second))


@unittest.skipUnless(fixture.HAS_AQT, "Qt/Anki runtime is not installed")
class QuestsSurfaceActivationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        menu_fixture.MainMenuWidgetTest.setUpClass()
        cls.app = menu_fixture.MainMenuWidgetTest.app

    def setUp(self):
        self.harness = menu_fixture.MainMenuWidgetTest("runTest")
        self.harness.setUp()
        self.addCleanup(self.harness.tearDown)

    def _action(self, data):
        dialog = self.harness._open(data, current_skill="Mining")
        dialog.show()
        dialog.resize(900, 560)
        self.app.processEvents()
        fixture._open_quests_tab(dialog)
        fixture._expand_quest_card(dialog, QUEST_ID)
        return dialog.findChild(fixture.QPushButton, f"questAction_{QUEST_ID}")

    def test_admitted_opening_activates_and_underleveled_save_does_not(self):
        self.assertTrue(self._action(player(started=True)).isEnabled())
        self.assertFalse(self._action(player(started=True, levels={"magic": 74})).isEnabled())


if __name__ == "__main__":
    unittest.main()
