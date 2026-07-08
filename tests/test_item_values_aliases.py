import unittest

from item_values import ITEM_VALUES, STACKABLE_ITEM_NAMES
from item_values_generated import ITEM_VALUES_GENERATED


class ItemValuePluralAliasTest(unittest.TestCase):
    """AnkiScape names some stacks in the plural where the Darkan cache is singular."""

    def test_plural_registry_names_resolve_to_the_singular_cache_entry(self):
        # Missing these made a stackable read as UNSTACKABLE, so 15 arrow shafts
        # counted as 15 carried slots and Fletching banked every other action.
        for plural, singular in (
            ("Arrow shafts", "Arrow shaft"),
            ("Bronze arrows", "Bronze arrow"),
            ("Headless arrows", "Headless arrow"),
        ):
            with self.subTest(item=plural):
                self.assertIn(plural, STACKABLE_ITEM_NAMES)
                self.assertEqual(ITEM_VALUES[plural], ITEM_VALUES[singular])

    def test_aliasing_never_clobbers_a_real_cache_entry(self):
        # A genuine distinct item whose name happens to be another's plural (e.g.
        # "Bones") must keep its own cache value.
        for name, value in ITEM_VALUES_GENERATED.items():
            self.assertEqual(ITEM_VALUES[name], value)


if __name__ == "__main__":
    unittest.main()
