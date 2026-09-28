import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic_pure.logic_pure import apply_consumable_pure


class TestFoodOverheal(unittest.TestCase):
    def test_ordinary_food_caps_its_heal_without_removing_overheal(self):
        # Constitution 99 is 990 max LP; a Tiger shark overheal leaves 1090.
        overhealed = {
            "inventory": {"White tree fruit": 1},
            "constitution_level": 99,
            "combat_lifepoints": 1090,
        }
        after, result = apply_consumable_pure(overhealed, "White tree fruit")
        self.assertTrue(result["allowed"])
        self.assertEqual(result["healed"], 0)
        self.assertEqual(after["combat_lifepoints"], 1090)

        near_max = dict(overhealed, combat_lifepoints=980)
        after_near, near_result = apply_consumable_pure(near_max, "White tree fruit")
        self.assertEqual(near_result["healed"], 10)
        self.assertEqual(after_near["combat_lifepoints"], 990)


if __name__ == "__main__":
    unittest.main()
