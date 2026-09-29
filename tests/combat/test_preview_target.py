from copy import deepcopy
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import EQUIPMENT_DATA
from ankiscape.data.combat_data import COMBAT_ENEMY_DATA
from ankiscape.logic_pure.logic_pure_combat_engine import combat_target_preview_pure
from tests import test_combat_logic as combat_test


class PreviewTargetEligibilityTest(unittest.TestCase):
    def test_unknown_target_returns_before_reading_player_state(self):
        for enemy_data in (None, {}, {"missing_target": None}):
            with self.subTest(enemy_data=enemy_data):
                self.assertEqual(
                    combat_target_preview_pure(
                        None, "missing_target", enemy_data, EQUIPMENT_DATA
                    ),
                    {
                        "state": "blocked",
                        "risk_band": "Blocked",
                        "reasons": ("unknown enemy",),
                    },
                )

    def test_blocked_preview_preserves_the_first_entry_requirement_and_state(self):
        enemy_data = {
            "gated_rat": {
                **COMBAT_ENEMY_DATA["giant_rat"],
                "required_slayer_level": 85,
                "skill_requirements": {"agility": 30},
            }
        }
        for slayer_level, reason in ((1, "Slayer level 85"), (85, "Agility level 30")):
            with self.subTest(slayer_level=slayer_level):
                player = combat_test._player(slayer_level=slayer_level, agility_level=1)
                supplied = deepcopy(player)
                self.assertEqual(
                    combat_target_preview_pure(
                        player, "gated_rat", enemy_data, EQUIPMENT_DATA
                    ),
                    {
                        "state": "blocked",
                        "risk_band": "Blocked",
                        "reasons": (reason,),
                    },
                )
                self.assertEqual(player, supplied)
