from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _find_stats_button, _make_player_data
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QLabel, QPoint, QPushButton, QScrollArea, QToolButton, QWidget
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_stats_skill_guide_renders_registry_rows_locks_and_current_level_focus(self) -> None:
        player_data = _make_player_data()
        player_data["mining_level"] = 70
        dialog = self._open(player_data, current_skill="Mining")
        dialog.resize(1280, 752)
        dialog.show()
        for _ in range(6):
            QApplication.processEvents()
        try:
            guide = dialog.findChild(QScrollArea, "statsSkillGuideScroll")
            content = dialog.findChild(QWidget, "statsSkillGuideContent")
            actions = dialog.findChild(QLabel, "statsGuideSectionTitle::actions")
            equipment = dialog.findChild(QLabel, "statsGuideSectionTitle::equipment")
            divider = dialog.findChild(QLabel, "statsGuideCurrentDivider::actions")
            equipment_divider = dialog.findChild(
                QLabel,
                "statsGuideCurrentDivider::equipment",
            )
            unlocked = dialog.findChild(QWidget, "statsGuideRow::action:adamantite")
            locked = dialog.findChild(QWidget, "statsGuideRow::action:concentrated_coal")
            milestone_cape = dialog.findChild(
                QWidget,
                "statsGuideRow::equipment:Milestone cape (80)",
            )
            locked_equipment = dialog.findChild(
                QWidget,
                "statsGuideRow::equipment:Mining cape",
            )
            locked_name = dialog.findChild(QLabel, "statsGuideName::action:concentrated_coal")
            locked_badge = dialog.findChild(QLabel, "statsGuideLevelBadge::action:concentrated_coal")

            self.assertIsNotNone(guide)
            self.assertIsNotNone(content)
            self.assertEqual(actions.text(), "Actions")
            self.assertEqual(equipment.text(), "Equipment")
            self.assertEqual(divider.text(), "Current level 70")
            self.assertEqual(equipment_divider.text(), "Current level 70")
            self.assertEqual(locked_name.text(), "Concentrated coal")
            self.assertEqual(locked_badge.text(), "77")
            self.assertIsNone(unlocked.graphicsEffect())
            self.assertIsNotNone(locked.graphicsEffect())
            self.assertAlmostEqual(locked.graphicsEffect().opacity(), 0.45)
            self.assertIsNotNone(locked_equipment.graphicsEffect())
            self.assertAlmostEqual(
                locked_equipment.graphicsEffect().opacity(),
                0.45,
            )
            self.assertIsNone(milestone_cape)
            self.assertGreater(guide.verticalScrollBar().value(), 0)
            divider_y = divider.mapTo(guide.viewport(), QPoint(0, 0)).y()
            self.assertGreaterEqual(divider_y, 0)
            self.assertLess(divider_y, guide.viewport().height())

            rendered_text = " ".join(label.text() for label in content.findChildren(QLabel)).lower()
            self.assertNotIn("source:", rendered_text)
            self.assertNotIn("trace", rendered_text)
            self.assertEqual(content.findChildren(QPushButton), [])
            self.assertEqual(content.findChildren(QToolButton), [])

            _find_stats_button(dialog, "attack").click()
            QApplication.processEvents()
            self.assertIsNone(dialog.findChild(QLabel, "statsGuideSectionTitle::actions"))
            self.assertEqual(
                dialog.findChild(QLabel, "statsGuideSectionTitle::equipment").text(),
                "Equipment",
            )
            self.assertIsNotNone(
                dialog.findChild(QWidget, "statsGuideRow::equipment:Bronze dagger")
            )
        finally:
            dialog.deleteLater()

    def test_farming_skill_guide_renders_source_sections_rows_and_quest_gates(self) -> None:
        player_data = _make_player_data()
        player_data.update(
            {
                "farming_level": 60,
                "magic_level": 70,
                "agility_level": 60,
                "crafting_level": 60,
                "construction_level": 50,
                "woodcutting_level": 1,
                "firemaking_level": 1,
            }
        )
        dialog = self._open(player_data, current_skill="Farming")
        dialog.resize(1280, 752)
        dialog.show()
        for _ in range(6):
            QApplication.processEvents()
        try:
            content = dialog.findChild(QWidget, "statsSkillGuideContent")
            sections = [
                dialog.findChild(QLabel, f"statsGuideSectionTitle::{section_id}")
                for section_id in ("milestones", "produce", "trees", "special", "other")
            ]
            self.assertEqual(
                [section.text() for section in sections],
                ["Milestones", "Produce", "Trees", "Special", "Other"],
            )
            expected_counts = {
                "milestones": 2,
                "produce": 47,
                "trees": 12,
                "special": 12,
                "other": 15,
            }
            all_rows = [
                row
                for row in content.findChildren(QWidget)
                if row.objectName().startswith("statsGuideRow::farming-struct:")
            ]
            for index, (section_id, expected_count) in enumerate(expected_counts.items()):
                lower = sections[index].y()
                upper = sections[index + 1].y() if index + 1 < len(sections) else content.height()
                self.assertEqual(
                    sum(lower < row.y() < upper for row in all_rows),
                    expected_count,
                )

            potato = dialog.findChild(QWidget, "statsGuideRow::farming-struct:3439")
            oak = dialog.findChild(QWidget, "statsGuideRow::farming-struct:3453")
            scarecrow = dialog.findChild(QWidget, "statsGuideRow::farming-struct:3473")
            jade = dialog.findChild(QWidget, "statsGuideRow::farming-struct:3503")
            livid = dialog.findChild(QWidget, "statsGuideRow::farming-struct:3514")
            evil_oak = dialog.findChild(QWidget, "statsGuideRow::farming-struct:3520")
            white_lily = dialog.findChild(QWidget, "statsGuideRow::farming-struct:3477")
            dividers = {
                section_id: dialog.findChild(
                    QLabel,
                    f"statsGuideCurrentDivider::{section_id}",
                )
                for section_id in ("milestones", "produce", "trees", "special", "other")
            }
            self.assertIsNotNone(potato)
            self.assertIsNotNone(oak)
            self.assertIsNotNone(scarecrow)
            self.assertIsNotNone(jade)
            self.assertIsNotNone(livid)
            self.assertIsNotNone(evil_oak)
            self.assertIsNotNone(white_lily)
            self.assertEqual(
                {section_id: divider.text() for section_id, divider in dividers.items()},
                {
                    "milestones": "Current level 60",
                    "produce": "Current level 60",
                    "trees": "Current level 60",
                    "special": "Current level 60",
                    "other": "Current level 60",
                },
            )
            first_above_level = {
                "milestones": "farming-struct:3548",
                "produce": "farming-struct:3491",
                "trees": "farming-struct:3464",
                "special": "farming-struct:3506",
                "other": "farming-struct:3515",
            }
            guide_layout = content.layout()
            for section_id, row_id in first_above_level.items():
                divider_widget = dividers[section_id].parentWidget()
                row_widget = dialog.findChild(QWidget, f"statsGuideRow::{row_id}")
                self.assertEqual(
                    guide_layout.indexOf(divider_widget) + 1,
                    guide_layout.indexOf(row_widget),
                )
            self.assertEqual(
                dialog.findChild(QLabel, "statsGuideName::farming-struct:3453").text(),
                "Oak tree",
            )
            self.assertEqual(
                dialog.findChild(QLabel, "statsGuideName::farming-struct:3473").text(),
                "Make and place a scarecrow",
            )
            oak_icon = dialog.findChild(QLabel, "statsGuideIcon::farming-struct:3453")
            self.assertIsNotNone(oak_icon)
            self.assertFalse(oak_icon.pixmap().isNull())
            self.assertIsNotNone(jade.graphicsEffect())
            self.assertAlmostEqual(jade.graphicsEffect().opacity(), 0.45)
            self.assertEqual(
                dialog.findChild(QLabel, "statsGuideName::farming-struct:3503").toolTip(),
                "Requires: Back to My Roots",
            )
            self.assertIsNotNone(livid.graphicsEffect())
            self.assertEqual(
                dialog.findChild(QLabel, "statsGuideName::farming-struct:3514").toolTip(),
                "Requires: Lunar Diplomacy",
            )
            self.assertIsNone(white_lily.graphicsEffect())
            self.assertEqual(
                dialog.findChild(QLabel, "statsGuideName::farming-struct:3477").toolTip(),
                "",
            )
            evil_oak_tooltip = dialog.findChild(
                QLabel,
                "statsGuideName::farming-struct:3520",
            ).toolTip()
            self.assertIn("Woodcutting 15", evil_oak_tooltip)
            self.assertIn("Firemaking 15", evil_oak_tooltip)
            self.assertEqual(len(all_rows), 88)
            self.assertIsNone(dialog.findChild(QWidget, "statsGuideRow::farming-struct:3526"))
        finally:
            dialog.deleteLater()

    def test_slayer_skill_guide_lists_every_registry_family(self) -> None:
        dialog = self._open(_make_player_data(), current_skill="Slayer")
        try:
            content = dialog.findChild(QWidget, "statsSkillGuideContent")
            monsters = dialog.findChild(
                QLabel,
                "statsGuideSectionTitle::monsters",
            )
            rows = [
                row
                for row in content.findChildren(QWidget)
                if row.objectName().startswith("statsGuideRow::monster:")
            ]
            wall_beasts = dialog.findChild(
                QWidget,
                "statsGuideRow::monster:wall_beasts",
            )
            wall_beasts_badge = dialog.findChild(
                QLabel,
                "statsGuideLevelBadge::monster:wall_beasts",
            )
            wall_beasts_icon = dialog.findChild(
                QLabel,
                "statsGuideIcon::monster:wall_beasts",
            )

            self.assertEqual(monsters.text(), "Monsters")
            self.assertEqual(len(rows), 105)
            self.assertIsNotNone(wall_beasts)
            self.assertEqual(wall_beasts_badge.text(), "35")
            self.assertFalse(wall_beasts_icon.pixmap().isNull())
        finally:
            dialog.deleteLater()
