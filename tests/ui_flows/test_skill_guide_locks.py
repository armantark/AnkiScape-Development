"""The Stats skill guide dims a row for every lock its target list shows, via the real main menu."""

from __future__ import annotations

import unittest

import pkg_alias  # noqa: F401
from tests import test_main_menu_widget as _main_menu

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QLabel, QWidget


def _player(**changes) -> dict:
    player = _main_menu._make_player_data()
    player.update(changes)
    return player


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class SkillGuideLocksTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        self.menu = _main_menu.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()

    def tearDown(self) -> None:
        self.menu.tearDown()

    def _row(self, player: dict, skill: str, row_id: str) -> tuple["QWidget", "QLabel"]:
        dialog = self.menu._open(player, current_skill=skill)
        dialog.show()
        for _ in range(4):
            QApplication.processEvents()
        return (
            dialog.findChild(QWidget, f"statsGuideRow::{row_id}"),
            dialog.findChild(QLabel, f"statsGuideName::{row_id}"),
        )

    def test_quest_locked_row_at_a_reachable_level_is_dimmed_and_names_its_quest(self) -> None:
        # Gem rocks need level 40 and Shilo Village; the player is level 70.
        row, name = self._row(_player(mining_level=70), "Mining", "action:gem_rocks")
        self.assertIsNotNone(row.graphicsEffect())
        self.assertAlmostEqual(row.graphicsEffect().opacity(), 0.45)
        self.assertIn("Shilo Village", name.toolTip())
        self.assertNotIn("Mining level", name.toolTip(), "the guide's own level marker already says so")

    def test_row_undims_once_the_quest_is_done(self) -> None:
        player = _player(mining_level=70)
        player["quests"]["shilo_village"]["completed"] = True
        row, name = self._row(player, "Mining", "action:gem_rocks")
        self.assertIsNone(row.graphicsEffect())
        self.assertEqual(name.toolTip(), "")

    def test_a_missing_tool_dims_the_row_and_names_it(self) -> None:
        row, name = self._row(_player(mining_level=70, toolbelt={}), "Mining", "action:adamantite")
        self.assertIsNotNone(row.graphicsEffect())
        self.assertIn("pickaxe", name.toolTip())

    def test_other_families_dim_through_their_own_predicates(self) -> None:
        row, name = self._row(_player(fishing_level=60), "Fishing", "action:catch_slimy_eel:slimy_eel")
        self.assertIsNotNone(row.graphicsEffect())
        self.assertIn("Priest in Peril", name.toolTip())

    def test_every_skill_target_table_projects_with_its_predicate(self) -> None:
        from ankiscape.core.constants import EQUIPMENT_ITEM_DATA
        from ankiscape.logic.skill_guide_logic import skill_guide_sections_pure

        player = _player()
        for skill_id, table in self.menu._ui._SKILL_TARGET_TABLES.items():
            with self.subTest(skill=skill_id):
                rows = skill_guide_sections_pure(skill_id, table, EQUIPMENT_ITEM_DATA, player_data=player)[0].rows
                self.assertTrue(all(isinstance(reason, str) for row in rows for reason in row.lock_reasons))


if __name__ == "__main__":
    unittest.main()
