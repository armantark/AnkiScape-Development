"""Real review cards: one ammo owner, rune capacity, recovery, migration and reload.

Failure seams: doubled Bank balances, two worn tiers, lost death quantities,
refill clearing runes, and a toggle that accidentally disables shot recovery.
"""

import copy
import random
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import EQUIPMENT_DATA, ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.equipment_change import equip_item_save_pure, unequip_slot_save_pure
from ankiscape.core.storage_pure import migrate_loaded_data
from ankiscape.core.combat_prayer_config import apply_combat_prayer_config_pure
from ankiscape.logic.inventory_pure import carried_slots_used
from ankiscape.data.item_values import STACKABLE_ITEM_NAMES
from ankiscape.logic_pure.combat.ammunition import carried_runes, equipped_ammo
from ankiscape.logic_pure.logic_pure import refill_combat_supply_loadout_pure
from ankiscape.logic_pure.logic_pure_combat_supplies import _combat_supply_slots_used
from ankiscape.runtime.runtime_actions_combat import handle_combat_answer
from tests.test_combat_logic import _player
from tests.test_runtime_actions import _context


def sample_recovery(cape, enabled, cards=500):
    player = _player(
        equipment={"weapon": "Shortbow", **({"cape": cape} if cape else {})},
        inventory={"Bronze arrows": 100000, "Shark": 10000},
        constitution_level=99, combat_lifepoints=990, combat_auto_flee=False,
        combat_prayers_enabled=False, combat_auto_eat_food=["Shark"],
        combat_ava_incidental_items=enabled,
    )
    ctx = _context(player, review_action_multiplier=10)
    rng = random.Random(211)
    ctx.random_random = rng.random
    ctx.review_action_multiplier = 10
    ctx.cadence_live_enabled = True
    fired = 0
    for _ in range(cards):
        if not handle_combat_answer(ctx):
            raise AssertionError(ctx.player_data.get("combat_last_result"))
        fired += sum(ctx.player_data["combat_last_result"].get("ammo_used", {}).values())
    remaining = ctx.player_data["inventory"].get("Bronze arrows", 0) + equipped_ammo(ctx.player_data).get("Bronze arrows", 0)
    return fired, 100000 - remaining, ctx.player_data


class AmmunitionPackTests(unittest.TestCase):
    def test_speed_ten_review_equips_the_840_arrow_stack(self):
        player = _player(equipment={"weapon": "Shortbow"}, inventory={"Bronze arrows": 840},
                         combat_prayers_enabled=False, combat_auto_flee=False)
        ctx = _context(player, random_values=(0.99,) * 1000, review_action_multiplier=10)
        ctx.cadence_live_enabled = True
        self.assertTrue(handle_combat_answer(ctx))
        self.assertTrue(handle_combat_answer(ctx))
        fired = sum(ctx.player_data["combat_last_result"]["ammo_used"].values())
        self.assertGreater(fired, 0)
        self.assertEqual(equipped_ammo(ctx.player_data), {"Bronze arrows": 840 - fired})
        self.assertEqual(ctx.player_data["inventory"]["Bronze arrows"], 0)
        self.assertNotIn("ammo", ctx.player_data["combat_supply_loadout"])

    def test_seeded_review_recovery_and_global_incidental_toggle(self):
        for cape, rate in ((None, 0.50), ("Ava's attractor", 0.60), ("Ava's accumulator", 0.72)):
            with self.subTest(cape=cape):
                fired, lost, enabled = sample_recovery(cape, True)
                fired_off, lost_off, disabled = sample_recovery(cape, False)
                self.assertGreater(fired, 1000)
                self.assertAlmostEqual(1 - lost / fired, rate, delta=0.04)
                self.assertEqual((fired, lost), (fired_off, lost_off))
                item = "Iron arrows" if cape == "Ava's attractor" else "Steel arrows"
                self.assertEqual(disabled["inventory"].get(item, 0), 0)
                if cape:
                    self.assertGreater(enabled["inventory"].get(item, 0), 0)

    def test_spells_spend_only_carried_runes_and_share_28_slots_with_food(self):
        player = _player(equipment={"weapon": "Staff"}, combat_attack_style="magic_standard",
                         inventory={"Air rune": 100, "Mind rune": 100},
                         carried_inventory={"chicken": {"Air rune": 2, "Mind rune": 2}},
                         combat_auto_eat_food=[], combat_prayers_enabled=False,
                         combat_auto_flee=False, combat_encounter={"target_id": "chicken", "enemy_lifepoints": 10000})
        ctx = _context(player, random_values=(0.99,) * 1000, review_action_multiplier=10)
        ctx.cadence_live_enabled = True
        self.assertTrue(handle_combat_answer(ctx))
        used = ctx.player_data["combat_last_result"]["runes_used"]
        self.assertEqual(used, {"Air rune": 2, "Mind rune": 2})
        self.assertEqual(ctx.player_data["inventory"]["Air rune"], 98)
        self.assertEqual(carried_runes(ctx.player_data), {})
        self.assertEqual(ctx.card.stop_reason, "out_of_runes")
        ctx.player_data["inventory"].update({"Shark": 100, "Raw beef": 14})
        ctx.player_data["carried_inventory"]["chicken"]["Raw beef"] = 14
        refilled, ok, reason = refill_combat_supply_loadout_pure(ctx.player_data, EQUIPMENT_DATA)
        self.assertTrue(ok, reason)
        self.assertEqual(carried_runes(refilled), {"Air rune": 98, "Mind rune": 98})
        self.assertLessEqual(_combat_supply_slots_used(refilled) + carried_slots_used(refilled["carried_inventory"]["chicken"], STACKABLE_ITEM_NAMES), 28)

    def test_legacy_balances_migrate_once_with_every_item_accounted_for(self):
        legacy = _player(config_version=126, equipment={"weapon": "Shortbow", "ammunition": "Bronze arrows"},
                         inventory={"Bronze arrows": 4, "Iron arrows": 5},
                         combat_supply_loadout={"ammo": {"Bronze arrows": 918, "Iron arrows": 18}, "runes": {"Air rune": 7, "Mind rune": 8}})
        migrated = migrate_loaded_data(copy.deepcopy(legacy), ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(equipped_ammo(migrated), {"Iron arrows": 18})
        self.assertEqual(migrated["inventory"]["Bronze arrows"], 923)
        self.assertEqual(migrated["inventory"]["Iron arrows"], 5)
        self.assertEqual(migrated["inventory"]["Air rune"], 7)
        self.assertEqual(migrated["inventory"]["Mind rune"], 8)
        self.assertNotIn("ammo", migrated["combat_supply_loadout"])
        self.assertNotIn("runes", migrated["combat_supply_loadout"])
        reloaded = migrate_loaded_data(migrated, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(reloaded["inventory"], migrated["inventory"])
        self.assertEqual(equipped_ammo(reloaded), equipped_ammo(migrated))

    def test_equipment_swaps_and_unequip_keep_the_whole_stack(self):
        player = _player(equipment={"weapon": "Shortbow"}, inventory={"Bronze arrows": 840, "Iron arrows": 18})
        player, ok = equip_item_save_pure(player, "Bronze arrows")
        self.assertTrue(ok)
        self.assertEqual(equipped_ammo(player), {"Bronze arrows": 840})
        player, ok = equip_item_save_pure(player, "Iron arrows")
        self.assertTrue(ok)
        self.assertEqual(player["inventory"]["Bronze arrows"], 840)
        player, ok = unequip_slot_save_pure(player, "ammunition")
        self.assertTrue(ok)
        self.assertEqual(player["inventory"]["Iron arrows"], 18)
        self.assertEqual(equipped_ammo(player), {})

    def test_the_incidental_setting_survives_reload_outside_presets(self):
        player = apply_combat_prayer_config_pure(_player(), "combat_ava_incidental_items", False)
        player = migrate_loaded_data(player, ORE_DATA, ITEM_DEFINITIONS)
        self.assertFalse(player["combat_ava_incidental_items"])
