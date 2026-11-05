"""The Ancient Effigies window, opened from its Tools action over the real controller."""

from __future__ import annotations

import copy
import os
import random
import sys
import types
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from aqt.qt import (
        QApplication,
        QColor,
        QEvent,
        QLabel,
        QMainWindow,
        QMenu,
        QPalette,
        QPushButton,
        QScrollArea,
        QStyleFactory,
        Qt,
        QTimer,
        QToolButton,
    )
    from PyQt6.QtTest import QTest

    HAS_AQT = True
except Exception:  # pragma: no cover - environment without aqt installed
    HAS_AQT = False

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.ancient_effigies.catalog import LAMP_DESTROY_WARNING, LAMP_SKILL_IDS, SKILL_PAIRS
from ankiscape.logic.ancient_effigies.custody import INSTANCES_KEY, NEXT_ID_KEY
from tests import allow_modal_dialogs
from tests.ancient_effigies.test_runtime_undo import _Collection, _LegacyHooks

SEED_1 = "00000000000000000000000000000001"
SEED_2 = "00000000000000000000000000000002"
SEED_3 = "00000000000000000000000000000003"


def _pump():
    for _ in range(5):
        QApplication.processEvents()


def _dark_palette():
    palette = QPalette()
    for role, rgb in (
        (QPalette.ColorRole.Window, (53, 53, 53)),
        (QPalette.ColorRole.WindowText, (255, 255, 255)),
        (QPalette.ColorRole.Base, (35, 35, 35)),
        (QPalette.ColorRole.AlternateBase, (53, 53, 53)),
        (QPalette.ColorRole.Text, (255, 255, 255)),
        (QPalette.ColorRole.Button, (53, 53, 53)),
        (QPalette.ColorRole.ButtonText, (255, 255, 255)),
        (QPalette.ColorRole.Mid, (40, 40, 40)),
        (QPalette.ColorRole.Highlight, (42, 130, 218)),
        (QPalette.ColorRole.HighlightedText, (0, 0, 0)),
    ):
        palette.setColor(role, QColor(*rgb))
    return palette


def _luminance(color):
    def channel(value):
        value /= 255
        return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(color.red()) + 0.7152 * channel(color.green()) + 0.0722 * channel(color.blue())


def _contrast(foreground, background):
    alpha = foreground.alphaF()
    blended = QColor(
        round(foreground.red() * alpha + background.red() * (1 - alpha)),
        round(foreground.green() * alpha + background.green() * (1 - alpha)),
        round(foreground.blue() * alpha + background.blue() * (1 - alpha)),
    )
    light, dark = sorted((_luminance(blended), _luminance(background)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def _player(**fields):
    """Two Starved copies (one revealed for Crafting or Agility) and a carried lamp."""
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data.update(
        crafting_level=90, crafting_exp=5346332, agility_level=90, agility_exp=5346332,
        skilling_current_levels={"crafting": 93}, attack_level=1, attack_exp=0,
    )
    data["inventory"]["Starved ancient effigy"] = 2
    data[INSTANCES_KEY] = {
        "ancient-effigy-1": {"item_id": 18778, "location": "bank", "request_seed": SEED_1, "request_step": 0, "pair_index": 0},
        "ancient-effigy-2": {"item_id": 18778, "location": "bank", "request_seed": SEED_2, "request_step": 0, "pair_index": None},
        "ancient-effigy-3": {"item_id": 18782, "location": "held", "request_seed": SEED_3, "request_step": 3, "pair_index": None},
    }
    data[NEXT_ID_KEY] = 4
    data.update(fields)
    return data


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class AncientEffigiesDialogTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package

        modules = dict(sys.modules)
        style_name = self.app.style().objectName()
        palette = QPalette(self.app.palette())
        random_state = random.getstate()
        self.addCleanup(random.setstate, random_state)
        self.addCleanup(self.app.setPalette, palette)
        self.addCleanup(lambda: self.app.setStyle(QStyleFactory.create(style_name)))
        self.addCleanup(sys.modules.update, modules)
        self.addCleanup(sys.modules.clear)
        real_qt = sys.modules["aqt.qt"]
        _install_runtime_fakes()
        sys.modules["aqt.qt"] = real_qt
        self.addon = _load_addon_as_package("ankiscape_effigy_dialog")
        self.parent = QMainWindow()
        self.addCleanup(self.parent.close)
        self.parent.col = _Collection()
        self.parent.update_undo_actions = lambda: None
        self.menu = QMenu("Tools", self.parent)
        self.parent.form = types.SimpleNamespace(menuTools=self.menu)
        for module in (self.addon, self.addon.ui, sys.modules[f"{self.addon.__name__}.core.storage"], sys.modules["aqt"]):
            module.mw = self.parent
        self.feature = sys.modules[f"{self.addon.__name__}.runtime.ancient_effigies"]
        self.controller = self.feature.controller_for(self.addon.__name__)
        self.addCleanup(self.controller.close_window)
        self.addon._state.player_data = _player()
        self.addon._state.current_skill = "Crafting"
        self.addon.save_player_data()
        hooks = _LegacyHooks()
        self.feature.register_profile_hooks(self.addon.__name__, hooks.addHook, types.SimpleNamespace(profile_will_close=[]))
        hooks.run("profileLoaded")

    # Helpers

    def open_window(self, size=(680, 560)):
        actions = [action for action in self.menu.actions() if action.objectName() == "ancientEffigiesAction"]
        self.assertEqual([action.text() for action in actions], ["AnkiScape Ancient Effigies…"])
        actions[0].trigger()
        window = self.controller.window
        self.assertIsNotNone(window)
        window.show()
        window.resize(*size)
        _pump()
        return window

    def buttons(self, window, object_name):
        return [button for button in window.findChildren(QPushButton, object_name) if button.isVisibleTo(window)]

    def label(self, window, object_name):
        labels = [label for label in window.findChildren(QLabel, object_name) if label.isVisibleTo(window)]
        return labels[0].text() if labels else None

    def key_to_row(self, window, row):
        window.list.setFocus()
        QTest.keyClick(window.list, Qt.Key.Key_Home)
        for _ in range(row):
            QTest.keyClick(window.list, Qt.Key.Key_Down)
        _pump()
        return window.list.currentItem().text()

    def answer_chooser(self, skill_id, then=None, *, cancel=False):
        seen = {}

        def _answer():
            modal = QApplication.activeModalWidget()
            seen["skills"] = [button.property("skillId") for button in modal.findChildren(QToolButton, "xpLampSkillButton")]
            if cancel:
                modal.findChild(QPushButton, "xpLampCancelButton").click()
                return
            if then is not None:
                QTimer.singleShot(0, then)
            next(button for button in modal.findChildren(QToolButton, "xpLampSkillButton") if button.property("skillId") == skill_id).click()
            modal.findChild(QPushButton, "xpLampClaimButton").click()

        QTimer.singleShot(0, _answer)
        return seen

    def answer_box(self, choose, seen):
        def _answer():
            box = QApplication.activeModalWidget()
            seen["text"] = box.text()
            seen["informative"] = box.informativeText()
            seen["default"] = box.defaultButton().text()
            next(button for button in box.buttons() if button.text() == choose).click()

        return _answer

    # Behavior

    def test_two_copies_disclose_and_show_both_choices(self):
        window = self.open_window()
        self.assertEqual(window.windowTitle(), "Ancient Effigies")
        self.assertEqual(self.key_to_row(window, 0), "Starved ancient effigy · Copy 1 · In your bank")
        self.assertEqual(self.label(window, "ancientEffigiesPair"), "Requested skills: Crafting or Agility")
        self.assertIn("Requires level 91", self.label(window, "ancientEffigiesRequirement"))
        self.assertIn("15,000 XP", self.label(window, "ancientEffigiesRequirement"))
        choices = {button.text(): button.isEnabled() for button in self.buttons(window, "ancientEffigiesInvestigate")}
        self.assertEqual(choices, {"Investigate with Crafting": True, "Investigate with Agility": False})
        reasons = [label.text() for label in window.findChildren(QLabel, "ancientEffigiesChoiceReason")]
        self.assertEqual(reasons, ["Your Crafting level is 93 (boosted from 90).", "Needs level 91 Agility; yours is 90."])

        self.assertEqual(self.key_to_row(window, 1), "Starved ancient effigy · Copy 2 · In your bank")
        self.assertEqual(self.label(window, "ancientEffigiesPair"), "Inspect to reveal skills")
        self.assertEqual(self.buttons(window, "ancientEffigiesInvestigate"), [])
        entries = len(self.parent.col.entries)
        self.buttons(window, "ancientEffigiesInspect")[0].click()
        _pump()
        self.assertEqual(len(self.parent.col.entries), entries + 1)
        self.assertEqual(window.list.currentItem().text(), "Starved ancient effigy · Copy 2 · In your bank")
        self.assertEqual(self.label(window, "ancientEffigiesPair"), "Requested skills: Runecrafting or Summoning")
        self.assertEqual(
            [button.text() for button in self.buttons(window, "ancientEffigiesInvestigate")],
            ["Investigate with Runecrafting", "Investigate with Summoning"],
        )
        self.assertFalse(any(button.isEnabled() for button in self.buttons(window, "ancientEffigiesInvestigate")))
        self.assertEqual(self.addon._state.player_data[INSTANCES_KEY]["ancient-effigy-1"]["pair_index"], 0)

    def test_four_transformations_keep_the_copy_selected(self):
        data = self.addon._state.player_data
        for skill_id in {skill for pair in SKILL_PAIRS for skill in pair}:
            data[f"{skill_id}_level"] = 99
        window = self.open_window()
        self.key_to_row(window, 0)
        names = []
        for _stage in range(4):
            enabled = [button for button in self.buttons(window, "ancientEffigiesInvestigate") if button.isEnabled()]
            self.assertEqual(len(enabled), 2)
            enabled[0].click()
            _pump()
            names.append(self.label(window, "ancientEffigiesName"))
            self.assertIn("XP", self.label(window, "ancientEffigiesFeedback"))
        self.assertEqual(names, ["Nourished ancient effigy", "Sated ancient effigy", "Gorged ancient effigy", "Dragonkin lamp"])
        self.assertEqual(window.list.currentItem().text(), "Dragonkin lamp · Copy 1 · Carried")
        self.assertEqual(self.addon._state.player_data["crafting_exp"] - 5346332, 15000)
        self.assertEqual(
            [window.list.item(row).text() for row in range(window.list.count())],
            ["Dragonkin lamp · Copy 1 · Carried", "Starved ancient effigy · Copy 2 · In your bank", "Dragonkin lamp · Copy 3 · Carried"],
        )

    def test_lamp_chooser_confirmation_cancellation_and_redemption(self):
        window = self.open_window()
        self.assertEqual(self.key_to_row(window, 2), "Dragonkin lamp · Copy 3 · Carried")
        with allow_modal_dialogs():
            seen = self.answer_chooser("attack", cancel=True)
            self.buttons(window, "ancientEffigiesRub")[0].click()
            _pump()
        self.assertEqual(seen["skills"], list(LAMP_SKILL_IDS))
        self.assertIn("ancient-effigy-3", self.addon._state.player_data[INSTANCES_KEY])
        self.assertIn("still yours", self.label(window, "ancientEffigiesFeedback"))

        box = {}
        with allow_modal_dialogs():
            self.answer_chooser("attack", then=self.answer_box("Cancel", box))
            self.buttons(window, "ancientEffigiesRub")[0].click()
            _pump()
        self.assertEqual(box["text"], "Gain 4 Attack XP?")
        self.assertIn("permanent Attack level is 1", box["informative"])
        self.assertIn("ancient-effigy-3", self.addon._state.player_data[INSTANCES_KEY])
        self.assertEqual(self.addon._state.player_data["attack_exp"], 0)

        with allow_modal_dialogs():
            self.answer_chooser("attack", then=self.answer_box("Rub lamp", box))
            self.buttons(window, "ancientEffigiesRub")[0].click()
            _pump()
        self.assertNotIn("ancient-effigy-3", self.addon._state.player_data[INSTANCES_KEY])
        self.assertEqual(self.addon._state.player_data["attack_exp"], 4)
        self.assertEqual(window.list.count(), 2)
        self.assertIn("4 Attack XP", self.label(window, "ancientEffigiesFeedback"))

    def test_destroy_warns_defaults_to_cancel_and_removes_only_the_lamp(self):
        window = self.open_window()
        self.key_to_row(window, 2)
        box = {}
        with allow_modal_dialogs():
            QTimer.singleShot(0, self.answer_box("Cancel", box))
            self.buttons(window, "ancientEffigiesDestroy")[0].click()
            _pump()
        self.assertEqual(box["informative"], LAMP_DESTROY_WARNING)
        self.assertEqual(box["default"], "Cancel")
        self.assertIn("ancient-effigy-3", self.addon._state.player_data[INSTANCES_KEY])
        with allow_modal_dialogs():
            QTimer.singleShot(0, self.answer_box("Destroy", box))
            self.buttons(window, "ancientEffigiesDestroy")[0].click()
            _pump()
        self.assertEqual(list(self.addon._state.player_data[INSTANCES_KEY]), ["ancient-effigy-1", "ancient-effigy-2"])
        self.assertEqual(self.addon._state.player_data["attack_exp"], 0)

    def test_empty_state_and_reopen_read_live_ownership(self):
        self.addon._state.player_data = _player(**{INSTANCES_KEY: {}})
        self.addon._state.player_data["inventory"]["Starved ancient effigy"] = 0
        window = self.open_window()
        self.assertEqual(self.label(window, "ancientEffigiesEmpty"), "You do not own an Ancient Effigy or Dragonkin lamp.")
        self.assertFalse(window.list.isVisibleTo(window))
        window.close()
        _pump()
        self.assertIsNone(self.controller.window)
        self.addon._state.player_data["inventory"]["Starved ancient effigy"] = 1
        self.addon.save_player_data()
        window = self.open_window()
        self.assertIsNone(self.label(window, "ancientEffigiesEmpty"))
        self.assertEqual(window.list.count(), 1)

    def test_graved_copies_offer_no_use_action(self):
        data = self.addon._state.player_data
        data["inventory"]["Starved ancient effigy"] = 1
        data["combat_grave"] = {"items": ["Starved ancient effigy"], "reviews_remaining": 30, "source": "combat_death", "loadout": {}}
        data[INSTANCES_KEY]["ancient-effigy-1"] = dict(data[INSTANCES_KEY]["ancient-effigy-1"], location="grave")
        window = self.open_window()
        self.assertEqual(self.key_to_row(window, 0), "Starved ancient effigy · Copy 1 · At your gravestone")
        self.assertIn("gravestone", self.label(window, "ancientEffigiesRecovery"))
        self.assertEqual(self.buttons(window, "ancientEffigiesInvestigate"), [])

    def test_focus_refresh_shows_changes_made_elsewhere(self):
        window = self.open_window()
        self.key_to_row(window, 1)
        data = copy.deepcopy(self.addon._state.player_data)
        del data[INSTANCES_KEY]["ancient-effigy-3"]
        self.addon._state.player_data = data
        self.assertEqual(window.list.count(), 3, "nothing refreshes until the window regains focus")
        window.activateWindow()
        QApplication.sendEvent(window, QEvent(QEvent.Type.ActivationChange))
        _pump()
        self.assertTrue(window.isActiveWindow())
        self.assertEqual(window.list.count(), 2)
        self.assertEqual(window.list.currentItem().text(), "Starved ancient effigy · Copy 2 · In your bank")

    def assert_controls_reachable(self, window):
        scroll = window.findChild(QScrollArea, "ancientEffigiesDetailScroll")
        for button in window.findChildren(QPushButton):
            if button.isVisibleTo(window):
                scroll.ensureWidgetVisible(button)
                _pump()
                self.assertFalse(button.visibleRegion().isEmpty(), button.text())

    def assert_disabled_text_legible(self, window):
        background = window.palette().color(QPalette.ColorRole.Window)
        for button in self.buttons(window, "ancientEffigiesInvestigate"):
            css = button.styleSheet()
            self.assertNotIn("palette(mid);", css.replace("border: 1px solid palette(mid);", ""))
            if button.isEnabled():
                continue
            disabled = css.split("QPushButton:disabled { color: ")[1].split(";")[0]
            red, green, blue, alpha = (float(part) for part in disabled.removeprefix("rgba(").removesuffix(")").split(","))
            color = QColor(int(red), int(green), int(blue))
            color.setAlphaF(alpha)
            self.assertGreaterEqual(_contrast(color, background), 3.0)

    def test_layout_is_reachable_and_legible_in_light_and_dark(self):
        from tests.ui_flows.qt_text_fit import text_fit_defects

        self.app.setStyle(QStyleFactory.create("Fusion"))
        cases = [
            (theme, palette, size, row)
            for theme, palette in (("light", self.app.style().standardPalette()), ("dark", _dark_palette()))
            for size in ((680, 560), (560, 560))
            for row in range(3)
        ]
        for theme, palette, size, row in cases:
            with self.subTest(theme=theme, size=size, row=row):
                self.app.setPalette(palette)
                window = self.open_window(size)
                self.key_to_row(window, row)
                self.assertLessEqual(window.height(), 560)
                self.assertLessEqual(window.minimumSizeHint().height(), 560)
                self.assertEqual(text_fit_defects(window), [])
                self.assert_controls_reachable(window)
                self.assert_disabled_text_legible(window)
                window.close()
                _pump()


if __name__ == "__main__":
    unittest.main()
