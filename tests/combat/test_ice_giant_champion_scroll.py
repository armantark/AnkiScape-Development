"""Ice giant acquisition correction preserves bones and already-owned scrolls."""

import unittest

import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
from ankiscape.core.constants import COMBAT_ENEMY_DATA, ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.logic.cape_logic import trimmed_completionist_requirements_pure
from ankiscape.logic_pure.logic_pure import _combat_roll_drops


class IceGiantChampionScrollTests(unittest.TestCase):
    def test_removed_scroll_interval_preserves_bone_boundaries(self):
        for threshold in (0, 249, 250, 269, *range(270, 291), 99999):
            with self.subTest(threshold=threshold):
                expected = {"Big bones": 1, "Iron 2h sword": 1}
                if threshold < 250:
                    expected["Long bone"] = 1
                elif threshold < 270:
                    expected["Curved bone"] = 1

                drops = _combat_roll_drops(
                    COMBAT_ENEMY_DATA["ice_giant"],
                    iter((0.0, (threshold + 0.5) / 100000)).__next__,
                )

                self.assertEqual(drops, expected)

    def test_owned_scroll_survives_reload_without_champion_credit(self):
        saved = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        saved["inventory"]["Champion's scroll"] = 2

        loaded = migrate_loaded_data(saved, ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(loaded["inventory"]["Champion's scroll"], 2)
        champions = next(
            row for row in trimmed_completionist_requirements_pure(loaded)
            if row["id"] == "champions"
        )
        self.assertIs(champions["met"], False)
        self.assertIs(champions["latent"], True)
