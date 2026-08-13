import json
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS
from ankiscape.data.achievement_cape_data import SKILLCAPES
from ankiscape.data.bork_data import BORK_EFFIGY_ITEM
from ankiscape.data.dungeoneering_data import DUNGEONEERING_REWARDS
from ankiscape.data.evil_tree_data import EVIL_TREE_TIERS
from ankiscape.data.farming_data import FARMING_CROPS, FARMING_PATCHES_BY_ID
from ankiscape.data.farming_skill_guide_data import (
    FARMING_GUIDE_ICON_STORAGE_KEYS,
    FARMING_GUIDE_MISSING_ICON_ITEM_IDS,
    FARMING_GUIDE_ROWS,
    FARMING_GUIDE_SECTIONS,
)
from ankiscape.data.livid_farm_data import LIVID_FARM_ENTRY_LEVELS
from ankiscape.logic.skill_guide_logic import farming_skill_guide_sections_pure


_CACHE_FIXTURE = json.loads(
    Path(__file__).with_name("farming_skill_guide_cache_fixture.json").read_text(
        encoding="utf-8"
    )
)


def _player(farming_level=99):
    skills = {
        "farming": farming_level,
        "magic": 99,
        "agility": 99,
        "crafting": 99,
        "construction": 99,
        "dungeoneering": 99,
        "woodcutting": 99,
        "firemaking": 99,
    }
    player = {f"{skill}_level": level for skill, level in skills.items()}
    player["quests"] = {}
    return player


def _sections(player, rows=FARMING_GUIDE_ROWS):
    return farming_skill_guide_sections_pure(
        player,
        rows,
        FARMING_GUIDE_SECTIONS,
        icon_storage_keys=FARMING_GUIDE_ICON_STORAGE_KEYS,
        item_definitions=ITEM_DEFINITIONS,
        farming_crops=FARMING_CROPS,
        farming_patches_by_id=FARMING_PATCHES_BY_ID,
        evil_tree_tiers=EVIL_TREE_TIERS,
        livid_farm_entry_levels=LIVID_FARM_ENTRY_LEVELS,
        dungeoneering_rewards=DUNGEONEERING_REWARDS,
        bork_effigy_item=BORK_EFFIGY_ITEM,
        skillcapes=SKILLCAPES,
    )


def _row(sections, struct_id):
    for section in sections:
        for row in section.rows:
            if row.guide_struct_id == struct_id:
                return row
    raise AssertionError(f"missing struct {struct_id}")


class TestFarmingSkillGuide(unittest.TestCase):
    def test_cache_fixture_pins_every_source_field_independently(self):
        actual = []
        for row in FARMING_GUIDE_ROWS:
            actual.append(
                {
                    "struct_id": row.struct_id,
                    "name": row.name,
                    "level": row.level,
                    "icon_item_id": row.icon_item_id,
                    "guide_key": row.guide_key,
                    "category_id": row.category_id,
                    "requirement_text": row.requirement_text,
                    "requirements": [
                        {
                            "kind": requirement.kind,
                            "key": requirement.key,
                            "minimum": requirement.minimum,
                            "label": requirement.label,
                        }
                        for requirement in row.requirements
                    ],
                }
            )
        self.assertEqual(actual, _CACHE_FIXTURE)

    def test_cache_enumeration_drives_sections_membership_labels_and_icons(self):
        self.assertEqual(
            [(section_id, title, category_id) for section_id, title, category_id in FARMING_GUIDE_SECTIONS],
            [
                ("milestones", "Milestones", 1),
                ("produce", "Produce", 2),
                ("trees", "Trees", 3),
                ("special", "Special", 4),
                ("other", "Other", 5),
            ],
        )
        self.assertEqual(len(FARMING_GUIDE_ROWS), 110)
        self.assertEqual(
            {row.struct_id for row in FARMING_GUIDE_ROWS},
            set(range(3439, 3549)),
        )
        self.assertEqual(
            sum(row.category_id == 6 for row in FARMING_GUIDE_ROWS),
            22,
        )
        self.assertEqual({row.guide_key for row in FARMING_GUIDE_ROWS}, {21})
        self.assertNotIn("White tree", {row.name for row in FARMING_GUIDE_ROWS})

        sections = _sections(_player())
        self.assertEqual(
            [(section.title, len(section.rows)) for section in sections],
            [
                ("Milestones", 2),
                ("Produce", 47),
                ("Trees", 12),
                ("Special", 12),
                ("Other", 15),
            ],
        )
        self.assertEqual(_row(sections, 3473).name, "Make and place a scarecrow")
        self.assertEqual(_row(sections, 3453).name, "Oak tree")
        self.assertEqual(_row(sections, 3453).icon_item_id, 1521)
        self.assertEqual(_row(sections, 3453).icon_key, "Oak logs")
        self.assertEqual(_row(sections, 3457).icon_item_id, 1513)
        self.assertEqual(_row(sections, 3457).icon_key, "Magic logs")
        for section in sections:
            self.assertEqual(
                list(section.rows),
                sorted(
                    section.rows,
                    key=lambda row: (row.level, row.guide_struct_id),
                ),
            )

    def test_every_displayed_row_has_an_exhaustive_resolution_classification(self):
        sections = _sections(_player())
        rows = [row for section in sections for row in section.rows]
        counts = {}
        for row in rows:
            counts[row.resolution_status] = counts.get(row.resolution_status, 0) + 1
        self.assertEqual(
            counts,
            {
                "crop": 73,
                "patch_unlock": 1,
                "livid_farm": 1,
                "evil_tree": 6,
                "dungeoneering_reward": 1,
                "bork_reward": 1,
                "skillcape": 1,
                "unresolved": 4,
            },
        )
        self.assertEqual(
            {
                row.guide_struct_id
                for row in rows
                if row.resolution_status == "unresolved"
            },
            {3515, 3517, 3518, 3519},
        )
        self.assertEqual(_row(sections, 3512).resolution_status, "patch_unlock")
        self.assertEqual(_row(sections, 3513).resolution_status, "dungeoneering_reward")
        self.assertEqual(
            _row(sections, 3513).lock_reasons,
            ("Not implemented in AnkiScape",),
        )
        self.assertEqual(_row(sections, 3514).resolution_status, "livid_farm")
        self.assertEqual(_row(sections, 3516).resolution_status, "bork_reward")
        self.assertEqual(_row(sections, 3548).resolution_status, "skillcape")
        self.assertEqual(
            [_row(sections, struct_id).resolution_status for struct_id in range(3520, 3526)],
            ["evil_tree"] * 6,
        )

    def test_guide_icon_registry_resolves_73_ids_and_names_the_9_asset_gaps(self):
        rendered_rows = [
            row for row in FARMING_GUIDE_ROWS if row.category_id in {1, 2, 3, 4, 5}
        ]
        required_ids = {row.icon_item_id for row in rendered_rows}
        self.assertEqual(len(required_ids), 82)
        self.assertEqual(len(FARMING_GUIDE_ICON_STORAGE_KEYS), 73)
        self.assertEqual(
            required_ids - set(FARMING_GUIDE_ICON_STORAGE_KEYS),
            FARMING_GUIDE_MISSING_ICON_ITEM_IDS,
        )
        definitions = {item.storage_key: item for item in ITEM_DEFINITIONS}
        for storage_key in FARMING_GUIDE_ICON_STORAGE_KEYS.values():
            definition = definitions[storage_key]
            self.assertTrue(Path(definition.asset_path).is_file(), storage_key)

        sections = _sections(_player())
        for section in sections:
            for row in section.rows:
                if row.icon_item_id in FARMING_GUIDE_MISSING_ICON_ITEM_IDS:
                    self.assertIsNone(row.icon_key)
                else:
                    self.assertEqual(
                        row.icon_key,
                        FARMING_GUIDE_ICON_STORAGE_KEYS[row.icon_item_id],
                    )
        self.assertEqual(_row(sections, 3479).icon_key, "Clean marrentill")
        self.assertEqual(_row(sections, 3491).icon_key, "Clean snapdragon")
        self.assertEqual(_row(sections, 3503).icon_key, "Jade vine branch")
        self.assertEqual(_row(sections, 3504).icon_key, "Red blossom")
        self.assertEqual(_row(sections, 3511).icon_key, "Spirit sapling")
        self.assertEqual(_row(sections, 3512).icon_key, "Spirit sapling")

    def test_level_reached_remains_locked_until_quest_and_cross_skill_gates(self):
        player = _player(farming_level=60)
        sections = _sections(player)
        jade = _row(sections, 3503)
        livid = _row(sections, 3514)
        self.assertEqual(jade.level, 53)
        self.assertTrue(jade.lock_reasons)
        self.assertEqual(jade.lock_reasons, ("Back to My Roots",))
        self.assertTrue(livid.lock_reasons)
        self.assertEqual(livid.lock_reasons, ("Lunar Diplomacy",))

        player["quests"] = {
            "back_to_my_roots": {"completed": True},
            "lunar_diplomacy": {"completed": True},
        }
        sections = _sections(player)
        self.assertFalse(_row(sections, 3503).lock_reasons)
        self.assertFalse(_row(sections, 3514).lock_reasons)

        player["magic_level"] = 69
        livid = _row(_sections(player), 3514)
        self.assertTrue(livid.lock_reasons)
        self.assertEqual(livid.lock_reasons, ("Magic 70",))

    def test_evil_tree_cross_skill_requirements_are_source_driven(self):
        player = _player(farming_level=99)
        player["woodcutting_level"] = 1
        player["firemaking_level"] = 1
        sections = _sections(player)
        self.assertEqual(
            _row(sections, 3520).lock_reasons,
            ("Woodcutting 15", "Firemaking 15"),
        )
        self.assertEqual(
            _row(sections, 3525).lock_reasons,
            ("Woodcutting 85", "Firemaking 85"),
        )

        changed = list(FARMING_GUIDE_ROWS)
        index = next(i for i, row in enumerate(changed) if row.struct_id == 3520)
        from ankiscape.data.farming_skill_guide_data import FarmingGuideRequirement

        changed[index] = replace(
            changed[index],
            requirements=(FarmingGuideRequirement("skill", "woodcutting", 16),),
        )
        self.assertEqual(
            _row(_sections(player, tuple(changed)), 3520).lock_reasons,
            ("Woodcutting 16",),
        )

    def test_unrunnable_period_rows_remain_visible_but_implementation_locked(self):
        sections = _sections(_player())
        white_lily = _row(sections, 3477)
        potato = _row(sections, 3439)
        self.assertEqual(white_lily.resolution_status, "crop")
        self.assertEqual(
            white_lily.lock_reasons,
            ("Not implemented in AnkiScape",),
        )
        self.assertEqual(potato.resolution_status, "crop")
        self.assertEqual(potato.lock_reasons, ())

    def test_second_spirit_tree_resolves_against_the_secondary_patch(self):
        row = _row(_sections(_player()), 3512)
        self.assertEqual(row.resolution_status, "patch_unlock")
        without_secondary = dict(FARMING_PATCHES_BY_ID)
        without_secondary.pop("spirit_tree_secondary")
        sections = farming_skill_guide_sections_pure(
            _player(),
            FARMING_GUIDE_ROWS,
            FARMING_GUIDE_SECTIONS,
            icon_storage_keys=FARMING_GUIDE_ICON_STORAGE_KEYS,
            item_definitions=ITEM_DEFINITIONS,
            farming_crops=FARMING_CROPS,
            farming_patches_by_id=without_secondary,
            evil_tree_tiers=EVIL_TREE_TIERS,
            livid_farm_entry_levels=LIVID_FARM_ENTRY_LEVELS,
            dungeoneering_rewards=DUNGEONEERING_REWARDS,
            bork_effigy_item=BORK_EFFIGY_ITEM,
            skillcapes=SKILLCAPES,
        )
        self.assertEqual(_row(sections, 3512).resolution_status, "unresolved")

    def test_unimplemented_and_malformed_rows_are_isolated_and_locked(self):
        player = _player()
        rows = list(FARMING_GUIDE_ROWS)
        rows[0] = replace(rows[0], icon_item_id="bad")
        sections = _sections(player, tuple(rows))
        malformed = _row(sections, 3439)
        polypore = _row(sections, 3515)
        self.assertEqual(malformed.resolution_status, "malformed")
        self.assertTrue(malformed.lock_reasons)
        self.assertEqual(polypore.resolution_status, "unresolved")
        self.assertEqual(polypore.lock_reasons, ("Not implemented in AnkiScape",))
        self.assertEqual(len(sections), 5)
        self.assertEqual(sum(len(section.rows) for section in sections), 88)

        rows[0] = replace(FARMING_GUIDE_ROWS[0], category_id="bad")
        without_bad_category = _sections(player, tuple(rows))
        rows[0] = replace(
            FARMING_GUIDE_ROWS[0],
            guide_key=999,
            icon_item_id="bad",
        )
        without_foreign_malformed = _sections(player, tuple(rows))
        from ankiscape.data.farming_skill_guide_data import FarmingGuideRequirement

        rows[0] = replace(
            FARMING_GUIDE_ROWS[0],
            requirements=(FarmingGuideRequirement("skill", "magic", "bad"),),
        )
        with_bad_requirement = _sections(player, tuple(rows))
        self.assertEqual(_row(with_bad_requirement, 3439).resolution_status, "malformed")
        self.assertEqual(len(with_bad_requirement), 5)
        self.assertEqual(
            sum(len(section.rows) for section in with_bad_requirement),
            88,
        )
        with self.assertRaisesRegex(RuntimeError, "resolution failed"):
            with patch(
                "ankiscape.logic.skill_guide_logic._farming_resolution",
                side_effect=RuntimeError("resolution failed"),
            ):
                _sections(player)
        self.assertEqual(
            sum(len(section.rows) for section in without_bad_category),
            87,
        )
        self.assertEqual(
            sum(len(section.rows) for section in without_foreign_malformed),
            87,
        )

    def test_production_projection_uses_source_rows_not_crop_membership_or_runnable(self):
        source_names = {row.name for row in FARMING_GUIDE_ROWS}
        crop_names = {crop.display_name for crop in FARMING_CROPS}
        self.assertIn("Access to the Livid Farm", source_names)
        self.assertNotIn("Access to the Livid Farm", crop_names)
        self.assertIn("White tree", crop_names)
        self.assertNotIn("White tree", source_names)
        self.assertIn("White lily", source_names)
        self.assertFalse(next(crop for crop in FARMING_CROPS if crop.id == "white_lily").runnable)
        self.assertIsNotNone(_row(_sections(_player()), 3477))


if __name__ == "__main__":
    unittest.main()
