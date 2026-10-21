"""Period Falador lamps in the existing Bank chooser and Cabinet labels."""

import unittest
from unittest import mock

from tests import test_main_menu_widget as _main_menu
from tests.test_main_menu_widget import HAS_AQT
from tests.ui_flows import test_bank_claim_lamps as bank
from tests.achievement_diaries.test_period_lamp_rewards import expected_ids

if HAS_AQT:
    from aqt.qt import QApplication, QColor, QLabel, QPalette


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class DiaryPeriodLampsUITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self):
        # Use the Bank harness without inheriting and rediscovering its tests.
        self.bank = bank.BankClaimLampsTest(methodName="runTest")
        self.bank.setUp()
        self.data = self.bank.data
        self.data["quests"] = {}
        self.data["achievement_diaries"] = {"claimed_tiers": ["falador_elite"]}
        self.data["claims"].update({key: {"claimed": False} for key in expected_ids("falador_elite")})
        self.data["attack_level"] = 72
        self.data["attack_exp"] = 0
        self.data["mining_level"] = 99  # Keeps every chooser open while Attack crosses floors.
        self.old_style = QApplication.style().objectName()
        self.old_palette = QApplication.palette()

    def tearDown(self):
        self.bank.tearDown()
        QApplication.setStyle(self.old_style)
        QApplication.setPalette(self.old_palette)

    def _palette(self, dark):
        QApplication.setStyle("Fusion")
        palette = QApplication.style().standardPalette()
        if dark:
            for role, color in (
                (QPalette.ColorRole.Window, QColor(40, 40, 40)),
                (QPalette.ColorRole.Base, QColor(24, 24, 24)),
                (QPalette.ColorRole.AlternateBase, QColor(48, 48, 48)),
                (QPalette.ColorRole.Button, QColor(48, 48, 48)),
                (QPalette.ColorRole.Text, QColor(238, 238, 238)),
                (QPalette.ColorRole.WindowText, QColor(238, 238, 238)),
                (QPalette.ColorRole.ButtonText, QColor(238, 238, 238)),
                (QPalette.ColorRole.Mid, QColor(8, 8, 8)),
                (QPalette.ColorRole.Highlight, QColor(42, 130, 218)),
                (QPalette.ColorRole.HighlightedText, QColor(255, 255, 255)),
            ):
                palette.setColor(role, color)
        QApplication.setPalette(palette)

    def _diary_rows(self, dialog):
        return {title: row for title, row in bank._rows(dialog).items() if title.startswith("Falador Elite:")}

    def _assert_falador_lamp_flow(self, dark):
        from ankiscape.ui.ui_tab_achievements import build_achievements_tab
        from tests.test_achievement_diaries_ui import _Ctx

        self._palette(dark)
        dialog = self.bank._open_bank(720)  # show, resize(720, 560), process events
        ids = expected_ids("falador_elite")
        amounts = (50000, 50000, 30000, 30000)
        floors = (84, 72, 90, 90)
        titles = tuple(f"Falador Elite: reward lamp {i} of 4 ({xp:,} XP)" for i, xp in enumerate(amounts, 1))
        self.assertEqual(set(self._diary_rows(dialog)), set(titles))
        self.assertEqual(len(self._diary_rows(dialog)), 4)
        for level in (72, 84, 90):
            self.data["attack_level"] = level
            dialog = self.bank._open_bank(720)
            rows = self._diary_rows(dialog)
            self.assertEqual(set(rows), set(titles))
            for title, floor in zip(titles, floors):
                with self.subTest(dark=dark, level=level, title=title):
                    # This observes the chooser's actual offered skills, with
                    # cancellation so checking one row cannot consume another.
                    with mock.patch.object(self.bank.menu._ui, "_choose_xp_lamp_skill", return_value=None) as chooser:
                        bank._button(rows[title], "Choose skill").click()
                        bank._pump()
                    offered = chooser.call_args.args[2]
                    self.assertEqual("attack" in offered, level >= floor)
                    self.assertFalse(self.data["claims"][ids[titles.index(title)]]["claimed"])

        # Drive the real modal chooser at the missing lamp's exact 72 boundary.
        self.data["attack_level"] = 72
        dialog = self.bank._open_bank(720)
        before_xp = self.data["attack_exp"]
        seen = self.bank._choose_lamp(self._diary_rows(dialog)[titles[1]])
        self.assertIn("attack", seen["skills"])
        self.assertTrue(seen["selected_enabled"])
        self.assertEqual(self.data["attack_exp"] - before_xp, 50000)
        self.assertTrue(self.data["claims"][ids[1]]["claimed"])
        self.assertEqual(set(self._diary_rows(dialog)), {titles[0], titles[2], titles[3]})
        for claim_id in (ids[0], ids[2], ids[3]):
            self.assertEqual(self.data["claims"][claim_id], {"claimed": False})

        cabinet = build_achievements_tab(_Ctx(self.data))
        cabinet.show()
        cabinet.resize(720, 560)
        bank._pump()
        entries = "; ".join(f"{xp:,} XP (level {floor}+)" for xp, floor in zip(amounts, floors))
        text = f"4 reward lamps will be placed in Bank Claims: {entries}."
        labels = [label for label in cabinet.findChildren(QLabel) if text in label.text()]
        self.assertTrue(labels, "Cabinet reward label must list all four lamps")
        for label in labels:
            self.assertTrue(label.wordWrap())
            self.assertNotIn("color: palette(mid)", label.styleSheet())
        cabinet.close()
        cabinet.deleteLater()
        bank._pump()

    def test_falador_rows_boundaries_spend_and_cabinet_with_explicit_light_palette(self):
        self._assert_falador_lamp_flow(False)

    def test_falador_rows_boundaries_spend_and_cabinet_with_fusion_dark_palette(self):
        self._assert_falador_lamp_flow(True)
