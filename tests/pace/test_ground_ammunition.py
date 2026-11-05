"""Shot custody and expiry through real combat cards, not balance snapshots."""

import copy
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import COMBAT_ENEMY_DATA, ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import migrate_loaded_data
from ankiscape.logic_pure.combat.ammunition import (
    equipped_ammo, ground_ammo_count, pickup_ground_ammo_pure,
)
from ankiscape.runtime.runtime_actions_combat import handle_combat_answer
from tests.test_combat_logic import _player
from tests.test_runtime_actions import _context


class GroundAmmunitionTests(unittest.TestCase):
    def setUp(self):
        enemy = {**COMBAT_ENEMY_DATA["chicken"], "stats": {**COMBAT_ENEMY_DATA["chicken"]["stats"], "hitpoints": 100000000}}
        patcher = patch.dict(COMBAT_ENEMY_DATA, {"chicken": enemy})
        patcher.start()
        self.addCleanup(patcher.stop)

    def fight(self, speed=10, cape=None, roll=0.75):
        player = _player(
            equipment={"weapon": "Shortbow", "ammunition": "Bronze arrows", **({"cape": cape} if cape else {})},
            equipment_ammunition_count=1000, combat_prayers_enabled=False,
            combat_auto_flee=False, combat_auto_eat_food=[],
            combat_encounter={"target_id": "chicken", "enemy_lifepoints": 1000000},
            combat_ava_incidental_items=False,
        )
        ctx = _context(player, review_action_multiplier=speed)
        ctx.cadence_live_enabled = True
        ctx.random_random = lambda: roll
        return ctx

    def test_no_device_grows_a_pile_and_click_returns_all_without_time(self):
        ctx = self.fight()
        for _ in range(3):
            self.assertTrue(handle_combat_answer(ctx))
        pile = ground_ammo_count(ctx.player_data)
        self.assertGreater(pile, 0)
        self.assertEqual(equipped_ammo(ctx.player_data)["Bronze arrows"], 1000 - pile)
        before = copy.deepcopy(ctx.player_data)
        picked, ok = pickup_ground_ammo_pure(ctx.player_data)
        self.assertTrue(ok)
        self.assertEqual(ground_ammo_count(picked), 0)
        self.assertEqual(equipped_ammo(picked), {"Bronze arrows": 1000})
        self.assertEqual(picked["ground_ammunition_tick"], before["ground_ammunition_tick"])
        self.assertEqual(picked["combat_encounter"], before["combat_encounter"])
        self.assertEqual(ctx.player_data, before)
        self.assertEqual(picked["review_event_log"][-1]["text"], f"Picked up {pile} ammo")

    def test_arrows_expire_on_the_card_that_reaches_their_tick_at_both_speeds(self):
        for speed in (1, 10):
            with self.subTest(speed=speed):
                ctx = self.fight(speed=speed)
                self.assertTrue(handle_combat_answer(ctx))
                first = copy.deepcopy(ctx.player_data["ground_ammunition"])
                self.assertEqual(first[0]["expires_at"], 351)
                # Further shots break, leaving only the original card's arrows.
                ctx.random_random = lambda: 0.99
                while ctx.player_data["ground_ammunition_tick"] + 6 * speed < 351:
                    self.assertTrue(handle_combat_answer(ctx))
                self.assertEqual(ctx.player_data["ground_ammunition"], first)
                self.assertTrue(handle_combat_answer(ctx))
                self.assertNotIn(first[0], ctx.player_data["ground_ammunition"])
                if speed == 10:
                    self.assertTrue(any(row in ctx.player_data["ground_ammunition"] for row in first[1:]))

    def test_each_device_returns_its_share_and_only_unbroken_remainder_lands(self):
        for cape, returned, landed in ((None, 0, 80), ("Ava's attractor", 60, 20),
                                       ("Ava's accumulator", 72, 8), ("Ava's alerter", 72, 8)):
            with self.subTest(cape=cape):
                ctx = self.fight(cape=cape)
                # Isolate the shot draw from damage/accuracy without replacing combat.
                from ankiscape.logic_pure.combat.ammunition import consume_ammo
                rolls = iter((i + 0.5) / 100 for i in range(100))

                def shot(data, spec, target, _rng, **kwargs):
                    return consume_ammo(data, spec, target, lambda: next(rolls), **kwargs)
                fired = broken = on_ground = 0
                with patch("ankiscape.logic_pure.logic_pure_combat_engine._combat_consume_ranged_ammo", side_effect=shot):
                    for _ in range(20):
                        if fired == 100:
                            break
                        ctx.card.ticks_remaining = min(60, (100 - fired) * 4)
                        self.assertTrue(handle_combat_answer(ctx))
                        result = ctx.player_data["combat_last_result"]
                        fired += sum(result["ammo_used"].values())
                        broken += result["ammo_broken"]
                        on_ground += result["ammo_landed"]
                        # Pick up each card so expiry cannot remove the measured share.
                        picked, _ = pickup_ground_ammo_pure(ctx.player_data)
                        ctx.player_data.update(picked)
                self.assertEqual((fired, broken, on_ground), (100, 20, landed))
                self.assertEqual(equipped_ammo(ctx.player_data), {"Bronze arrows": 980})
                self.assertEqual(fired - broken - on_ground, returned)

    def test_reload_and_target_change_keep_pile_and_pickup_routes_changed_type_to_bank(self):
        ctx = self.fight()
        self.assertTrue(handle_combat_answer(ctx))
        pile = ground_ammo_count(ctx.player_data)
        player = migrate_loaded_data(copy.deepcopy(ctx.player_data), ORE_DATA, ITEM_DEFINITIONS)
        player["current_combat_target"] = "cow"
        player["equipment"]["ammunition"] = "Iron arrows"
        player["equipment_ammunition_count"] = 7
        picked, ok = pickup_ground_ammo_pure(player)
        self.assertTrue(ok)
        self.assertEqual(picked["inventory"]["Bronze arrows"], pile)
        self.assertEqual(equipped_ammo(picked), {"Iron arrows": 7})
        self.assertEqual(ground_ammo_count(migrate_loaded_data({}, ORE_DATA, ITEM_DEFINITIONS)), 0)
