"""Navigation and action eligibility belong to the pure utility row projection."""

import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import BIRD_NEST_OPEN_TABLES, DEFAULT_UTILITY_ACTIVITY, UTILITY_ACTIVITY_DATA, UTILITY_ITEM_IMAGES
from ankiscape.core.target_metadata import mage_arena_attunement_rows_pure, utility_activity_rows


class UtilityRowMetadataTest(unittest.TestCase):
    def test_locked_card_can_open_without_enabling_its_action(self):
        rows = {row.target_id: row for row in utility_activity_rows(
            {}, UTILITY_ACTIVITY_DATA, UTILITY_ITEM_IMAGES, BIRD_NEST_OPEN_TABLES, DEFAULT_UTILITY_ACTIVITY,
        )}
        self.assertFalse(rows["werewolf_skullball"].enabled)
        self.assertTrue(rows["werewolf_skullball"].navigation_enabled)
        self.assertFalse(rows["make_soft_clay"].enabled)
        self.assertFalse(rows["make_soft_clay"].navigation_enabled)

    def test_attunement_requires_the_staff_in_inventory_or_equipment(self):
        for overrides, enabled in (({}, False), ({"inventory": {"Saradomin staff": 1}}, True),
                                   ({"equipment": {"weapon": "Saradomin staff"}}, True)):
            rows = {row.target_id: row for row in mage_arena_attunement_rows_pure(overrides)}
            row = rows["mage_arena_attune:saradomin"]
            self.assertEqual(row.enabled, enabled)
            self.assertEqual(row.navigation_enabled, enabled)
            self.assertEqual(bool(row.locked_reasons), not enabled)
