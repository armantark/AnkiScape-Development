import unittest
import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
from tools.audit_item_reachability import _item_option_groups


class TestItemReachabilityAudit(unittest.TestCase):
    def test_item_option_groups_parse_live_nested_mapping_shape(self):
        self.assertEqual(
            _item_option_groups(
                (
                    ({"Bronze hatchet": 1}, {"Iron hatchet": 1}),
                    ({"Earth talisman": 1}, {"Omni-talisman": 1}),
                )
            ),
            (
                {"Bronze hatchet": 1, "Iron hatchet": 1},
                {"Earth talisman": 1, "Omni-talisman": 1},
            ),
        )

    def test_item_option_groups_parse_dataclass_pair_shape(self):
        self.assertEqual(
            _item_option_groups(
                (
                    (("Bronze hatchet", 1), ("Iron hatchet", 1)),
                    (("Earth talisman", 1), ("Omni-talisman", 1)),
                )
            ),
            (
                {"Bronze hatchet": 1, "Iron hatchet": 1},
                {"Earth talisman": 1, "Omni-talisman": 1},
            ),
        )
