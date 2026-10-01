"""Offscreen Qt coverage for Slayer progress and Slayer finishers in the review
HUD and the combat menu."""

import itertools
import unittest

import pkg_alias  # noqa: F401
from tests import test_main_menu_widget as _main_menu
from tests import test_review_strip as _review_strip

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QPoint, QRect


def _held_finisher_cases(enemy_data):
    """(target, carried, state, notice) for every finisher enemy held at 1 LP,
    with and without its finisher; the notice is the full text for the worn
    abomination and the opening words for pack finishers."""
    from ankiscape.logic_pure.logic_pure_combat_model import _combat_finisher_spec

    cases = []
    for target_id, enemy in enemy_data.items():
        finisher = _combat_finisher_spec(enemy)
        if finisher is None:
            continue
        held = {"combat_encounter": {"target_id": target_id, "enemy_lifepoints": 1}}
        worn = bool(finisher.get("must_be_worn"))
        item = finisher["item"]
        cases.append(
            (
                target_id,
                False,
                held,
                f"Wear {item} to finish" if worn else "Finisher blocked: no loaded ",
            )
        )
        carried = (
            {"equipment": {"hands": item}}
            if worn
            else {"combat_supply_loadout": {"finishers": {item: 1}}}
        )
        cases.append(
            (
                target_id,
                True,
                {**held, **carried},
                f"Finisher ready: {finisher['action_label']}",
            )
        )
    return cases


@unittest.skipUnless(
    _main_menu.HAS_AQT,
    "aqt/PyQt6 not installed (use .venv-qt)",
)
class SlayerProgressWidgetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        self.menu = _main_menu.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()

    def tearDown(self) -> None:
        self.menu.tearDown()

    def test_hud_reads_slayer_assignment_and_hides_it_when_combat_or_task_ends(
        self,
    ) -> None:
        player = _main_menu._make_player_data()
        player["slayer_assignment"] = {
            "master_id": "turael_spria",
            "family_id": "bears",
            "initial_count": 17,
            "remaining": 4,
        }
        hud = self.menu._ui.ReviewHUD(None)
        hud.set_data(player, "Combat")
        QApplication.processEvents()
        self.assertEqual(hud.slayer_lbl.text(), "Slayer: 4 of 17 left")
        self.assertTrue(hud.slayer_lbl.isVisible())
        self.assertGreaterEqual(
            hud.slayer_lbl.y(),
            hud.chips_lbl.y() + hud.chips_lbl.height(),
        )

        hud.set_data(player, "Mining")
        self.assertFalse(hud.slayer_lbl.isVisible())
        hud.set_data(player, "Combat")
        self.assertTrue(hud.slayer_lbl.isVisible())
        player["slayer_assignment"]["remaining"] = 0
        hud.set_data(player, "Combat")
        self.assertFalse(hud.slayer_lbl.isVisible())
        player["slayer_assignment"] = {}
        hud.set_data(player, "Combat")
        self.assertFalse(hud.slayer_lbl.isVisible())

    def test_combat_menu_asks_for_worn_gauntlets_not_loaded_ones(self) -> None:
        from aqt.qt import QComboBox

        player = _main_menu._make_player_data()
        player.update(
            {
                "current_combat_target": "gelatinous_abomination",
                "slayer_level": 99,
                "combat_encounter": {
                    "target_id": "gelatinous_abomination",
                    "enemy_lifepoints": 1,
                },
            }
        )
        dialog = self.menu._open(player, current_skill="Combat")
        finisher = dialog.findChild(QComboBox, "combatActionCombo").model().item(1)
        self.assertFalse(finisher.isEnabled())
        self.assertEqual(
            finisher.toolTip(), "Wear Spiked gauntlets to finish the enemy."
        )
        tree = _main_menu._find_tree_with_user_role(dialog, "gelatinous_abomination")
        self.assertIn(
            "Finisher: Crush with Spiked gauntlets at 1–1 LP · not worn",
            _main_menu._tree_row(tree, "gelatinous_abomination").toolTip(0),
        )
        dialog.deleteLater()


@unittest.skipUnless(
    _review_strip.HAS_AQT,
    "aqt/PyQt6 not installed (use .venv-qt)",
)
class SlayerProgressTextFitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _review_strip.ReviewStripTest.setUpClass()

    def setUp(self) -> None:
        self.strip = _review_strip.ReviewStripTest(methodName="runTest")
        self.strip.setUp()

    def tearDown(self) -> None:
        self.strip.tearDown()

    def test_combat_hud_keeps_every_text_whole_in_the_strip_at_both_parent_sizes(
        self,
    ) -> None:
        from tests.ui_flows.qt_text_fit import text_fit_defects

        ui = self.strip.ui
        player = self.strip._state()
        player.update(
            {
                "current_combat_target": "black_bear",
                "combat_action": "attack",
                "combat_attack_style": "aggressive",
                "combat_attack_style_type": "crush",
                "attack_level": 31,
                "strength_level": 26,
                "defense_level": 21,
                "constitution_level": 28,
                "combat_lifepoints": 280,
                "combat_kill_counts": {"black_bear": 13},
                "slayer_assignment": {
                    "master_id": "turael_spria",
                    "family_id": "bears",
                    "initial_count": 17,
                    "remaining": 4,
                },
            }
        )
        ui.update_review_hud(player, "Combat")
        hud = ui._REVIEW_HUD
        hud.show()
        for parent_size in ((1000, 700), (900, 560)):
            with self.subTest(parent_size=parent_size):
                self.strip.parent.resize(*parent_size)
                for _ in range(4):
                    QApplication.processEvents()
                self.assertEqual(hud.slayer_lbl.text(), "Slayer: 4 of 17 left")
                self.assertTrue(hud.slayer_lbl.isVisible())
                for container in (self.strip.parent, ui._REVIEW_STRIP):
                    self.assertTrue(
                        container.rect().contains(
                            QRect(hud.mapTo(container, QPoint(0, 0)), hud.size())
                        )
                    )
                self.assertEqual(text_fit_defects(hud), [])

    def _combat_scene(self, target_id, **state):
        ui = self.strip.ui
        player = self.strip._state()
        player.update(
            {
                "current_combat_target": target_id,
                "slayer_level": 99,
                "combat_kill_counts": {target_id: 21},
                "slayer_assignment": {
                    "master_id": "turael_spria",
                    "family_id": "bears",
                    "initial_count": 17,
                    "remaining": 4,
                },
                **state,
            }
        )
        ui.update_review_hud(player, "Combat")
        ui.update_review_bank_run_button(player, "combat", lambda: None)
        hud = ui._REVIEW_HUD
        hud.show()
        return hud

    def test_finisher_prompt_reads_whole_on_its_own_amber_line_for_every_finisher(
        self,
    ) -> None:
        from ankiscape.logic_pure.logic_pure_combat_model import COMBAT_ENEMY_DATA
        from tests.ui_flows.qt_text_fit import text_fit_defects

        ui = self.strip.ui
        cases = _held_finisher_cases(COMBAT_ENEMY_DATA)
        notices = {(target_id, carried): notice for target_id, carried, _, notice in cases}
        self.assertEqual(
            notices["gelatinous_abomination", False], "Wear Spiked gauntlets to finish"
        )
        self.assertEqual(
            notices["gelatinous_abomination", True],
            "Finisher ready: Crush with Spiked gauntlets",
        )
        sized_cases = itertools.product(cases, ((1000, 700), (900, 560)))
        for (target_id, carried, state, notice), parent_size in sized_cases:
            with self.subTest(
                target=target_id, carried=carried, parent_size=parent_size
            ):
                hud = self._combat_scene(target_id, **state)
                self.strip.parent.resize(*parent_size)
                for _ in range(4):
                    QApplication.processEvents()
                self.assertTrue(hud.chips_lbl.text().startswith(notice))
                self.assertEqual(
                    hud.target_lbl.text(),
                    COMBAT_ENEMY_DATA[target_id]["display_name"],
                )
                self.assertIn("#f0c75e", hud.chips_lbl.styleSheet())
                self.assertEqual(hud.chips_lbl.toolTip(), "")
                self.assertTrue(ui._BANK_RUN_BUTTON.isVisible())
                self.assertFalse(hud.slayer_lbl.isVisible())
                self.assertEqual(text_fit_defects(hud), [])

        # Once the abomination dies, the chips and the Slayer line return
        # beside the Bank run button instead of under it.
        hud = self._combat_scene("gelatinous_abomination", combat_encounter={})
        for _ in range(4):
            QApplication.processEvents()
        self.assertEqual(
            hud.chips_lbl.toolTip(), "Kills: 21 · Trains Attack • Constitution"
        )
        self.assertNotIn("#f0c75e", hud.chips_lbl.styleSheet())
        self.assertEqual(hud.slayer_lbl.text(), "Slayer: 4 of 17 left")
        self.assertTrue(ui._BANK_RUN_BUTTON.isVisible())
        self.assertEqual(text_fit_defects(hud), [])
