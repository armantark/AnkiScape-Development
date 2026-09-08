"""Whole bursts retain the Chaos Elemental unequip transaction."""

from copy import deepcopy
import unittest

import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
from ankiscape.core.constants import EQUIPMENT_DATA, ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.combat_data import COMBAT_ENEMY_DATA
from ankiscape.logic_pure.logic_pure_combat_engine import apply_combat_burst_pure


def chaos_player(**overrides):
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player.update(
        current_combat_target="chaos_elemental",
        combat_auto_flee=False,
    )
    player.update(overrides)
    return player


def unequip_burst(player, *, live):
    supplied = deepcopy(player)
    updated, ok, result = apply_combat_burst_pure(
        player,
        COMBAT_ENEMY_DATA,
        EQUIPMENT_DATA,
        ticks=1 if live else 6,
        rng=lambda: 0.12,
        live_cadence=live,
    )
    assert player == supplied
    assert ok, result
    return updated, result


class EnemyUnequipTransactionTest(unittest.TestCase):
    def test_real_weapon_unequip_preserves_live_resume_state(self):
        player = chaos_player(
            equipment={"weapon": "Bronze sword"},
            combat_encounter={
                "target_id": "chaos_elemental",
                "enemy_lifepoints": 2400,
                "player_attack_ticks_remaining": 99,
                "enemy_attack_ticks_remaining": 0,
            },
        )

        updated, result = unequip_burst(player, live=True)

        self.assertEqual(
            result["enemy_specials"],
            ({"kind": "unequip", "item": "Bronze sword", "slot": "weapon"},),
        )
        self.assertNotIn("weapon", updated["equipment"])
        self.assertEqual(updated["inventory"]["Bronze sword"], 1)
        self.assertEqual(
            updated["carried_inventory"]["chaos_elemental"]["Bronze sword"],
            1,
        )
        self.assertEqual(updated["combat_encounter"]["target_id"], "chaos_elemental")
        self.assertEqual(updated["combat_encounter"]["enemy_lifepoints"], 2400)
        self.assertGreater(
            updated["combat_encounter"]["enemy_attack_ticks_remaining"], 0
        )

    def test_legacy_unequip_uses_sorted_fallback_and_reports_no_item(self):
        for equipment, expected_item, expected_slot in (
            (
                {"shield": "Anti-dragon shield", "neck": "Amulet of power"},
                "Amulet of power",
                "neck",
            ),
            ({"weapon": "", "head": None}, "", ""),
        ):
            with self.subTest(equipment=equipment):
                updated, result = unequip_burst(
                    chaos_player(equipment=equipment), live=False
                )
                self.assertEqual(
                    result["enemy_specials"],
                    (
                        {
                            "kind": "unequip",
                            "item": expected_item,
                            "slot": expected_slot,
                        },
                    ),
                )
                if expected_item:
                    self.assertNotIn(expected_slot, updated["equipment"])
                    self.assertEqual(updated["inventory"][expected_item], 1)
                    self.assertEqual(
                        updated["carried_inventory"]["chaos_elemental"][
                            expected_item
                        ],
                        1,
                    )

    def test_condition_instance_moves_to_bank_before_combat_wear(self):
        player = chaos_player(
            equipment={"head": "Combat hood 100"},
            equipment_instances={
                "equipment-1": {
                    "family_id": "combat_hood",
                    "item_name": "Combat hood 100",
                    "condition": 72_001,
                    "location": "equipped:head",
                    "last_slot": "head",
                }
            },
            equipment_instance_next_id=2,
            combat_encounter={
                "target_id": "chaos_elemental",
                "enemy_lifepoints": 2400,
                "player_attack_ticks_remaining": 99,
                "enemy_attack_ticks_remaining": 0,
            },
        )

        updated, result = unequip_burst(player, live=True)

        self.assertEqual(result["enemy_specials"][0]["item"], "Combat hood 100")
        self.assertNotIn("head", updated["equipment"])
        self.assertEqual(updated["inventory"]["Combat hood 100"], 1)
        self.assertEqual(
            updated["carried_inventory"]["chaos_elemental"]["Combat hood 100"],
            1,
        )
        self.assertEqual(
            updated["equipment_instances"]["equipment-1"]["location"], "bank"
        )
        self.assertEqual(
            updated["equipment_instances"]["equipment-1"]["condition"], 72_001
        )


if __name__ == "__main__":
    unittest.main()
