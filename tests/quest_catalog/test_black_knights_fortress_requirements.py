import unittest

import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
from ankiscape.data.quest_data import quests_as_dict


class TestBlackKnightsFortressRequirements(unittest.TestCase):
    def test_readout_requires_thirteen_quest_points(self):
        quest = quests_as_dict()["black_knights_fortress"]
        self.assertEqual(quest["requirements"][0], "13 Quest Points")
