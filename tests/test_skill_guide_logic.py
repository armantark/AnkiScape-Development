import unittest
from dataclasses import dataclass

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic.skill_guide_logic import skill_guide_sections_pure


@dataclass(frozen=True)
class _Target:
    id: str
    display_name: str
    level: int
    output_item: str


@dataclass(frozen=True)
class _SlayerFamily:
    id: str
    display_name: str
    target_ids: tuple[str, ...]
    required_slayer_level: int = 1


class TestSkillGuideLogic(unittest.TestCase):
    def test_projects_registry_targets_and_equipment_without_duplicate_unlocks(self):
        targets = {
            "make_widget": {
                "display_name": "Make full widget",
                "level": 12,
                "output_item": "Full widget",
                "source": "must not render",
            },
            "typed_target": _Target(
                "typed_target",
                "Catch complete creature name",
                4,
                "Complete creature",
            ),
            "missing_skill_level": {
                "display_name": "Cross-skill action without this skill's level",
                "magic_level": 87,
            },
        }
        equipment = {
            "Primary staff": {
                "combat_skill": "magic",
                "required_level": 30,
                "skill_requirements": (("magic", 30),),
                "source": "must not render",
            },
            "Secondary robe": {
                "combat_skill": "defense",
                "required_level": 20,
                "skill_requirements": (("magic", 40),),
            },
            "Unrelated sword": {
                "combat_skill": "attack",
                "required_level": 50,
                "skill_requirements": (),
            },
        }

        sections = skill_guide_sections_pure("magic", targets, equipment)

        self.assertEqual([section.title for section in sections], ["Actions", "Equipment"])
        self.assertEqual(
            [(row.level, row.name) for row in sections[0].rows],
            [(4, "Catch complete creature name"), (12, "Make full widget")],
        )
        self.assertEqual(
            [(row.level, row.name) for row in sections[1].rows],
            [(30, "Primary staff"), (40, "Secondary robe")],
        )
        self.assertEqual(len([row for row in sections[1].rows if row.name == "Primary staff"]), 1)
        self.assertNotIn("source", repr(sections).lower())

    def test_omits_empty_sections_and_normalizes_defence_identity(self):
        equipment = {
            "Shield": {
                "combat_skill": "defense",
                "required_level": 35,
                "skill_requirements": (("defense", 35),),
            }
        }

        sections = skill_guide_sections_pure("Defence", None, equipment)

        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0].title, "Equipment")
        self.assertEqual(sections[0].rows[0].name, "Shield")
        self.assertEqual(sections[0].rows[0].level, 35)

    def test_hides_milestone_capes_without_hiding_other_rows(self):
        targets = {
            "weave_milestone_cape_80": {
                "display_name": "Milestone cape (80)",
                "level": 80,
                "output_item": "Milestone cape (80)",
                "source_enum": "MILESTONE_CAPES",
            },
            "mine_runite": {
                "display_name": "Mine runite",
                "level": 85,
                "output_item": "Runite ore",
            },
        }
        equipment = {
            "Milestone cape (80)": {
                "equipment_type": "milestone_cape",
                "skill_requirements": (("mining", 80),),
            },
            "Mining cape": {
                "equipment_type": "skillcape",
                "skill_requirements": (("mining", 99),),
            },
        }

        sections = skill_guide_sections_pure("Mining", targets, equipment)

        self.assertEqual(
            [(row.level, row.name) for row in sections[0].rows],
            [(85, "Mine runite")],
        )
        self.assertEqual(
            [(row.level, row.name) for row in sections[1].rows],
            [(99, "Mining cape")],
        )

    def test_projects_slayer_families_as_level_sorted_monsters(self):
        families = {
            "abyssal_demons": _SlayerFamily(
                "abyssal_demons",
                "Abyssal demons",
                ("abyssal_demon",),
                85,
            ),
            "banshees": _SlayerFamily(
                "banshees",
                "Banshees",
                ("banshee",),
                15,
            ),
            "birds": _SlayerFamily("birds", "Birds", ("seagull",)),
        }

        sections = skill_guide_sections_pure(
            "Slayer",
            None,
            {},
            slayer_families=families,
        )

        self.assertEqual([section.title for section in sections], ["Monsters"])
        self.assertEqual(
            [
                (row.level, row.name, row.icon_key)
                for row in sections[0].rows
            ],
            [
                (1, "Birds", "seagull"),
                (15, "Banshees", "banshee"),
                (85, "Abyssal demons", "abyssal_demon"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
