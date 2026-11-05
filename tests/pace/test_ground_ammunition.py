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
from tests.integration_smoke import fixtures


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


class ActivityAmmunitionLogTests(fixtures.ReviewedProfile):
    def _ranged_addon(self, name, speed=1):
        addon = self._addon(name)
        addon.mw.col.set_config("ankiscape_review_action_multiplier", speed)
        self._new_save(addon, attack_level=40, strength_level=40, defense_level=40,
                       constitution_level=40, ranged_level=40, combat_lifepoints=400,
                       equipment={"weapon": "Shortbow", "ammunition": "Bronze arrows"},
                       equipment_ammunition_count=100, combat_auto_flee=False,
                       combat_prayers_enabled=False, combat_auto_eat_food=[])
        return addon

    def test_pest_control_assault_logs_the_two_arrows_fired_by_a_one_speed_card(self):
        addon = self._ranged_addon("ankiscape_pest_control_ammo_log")
        from ankiscape.logic.pest_control_logic import enter_pest_control_pure
        data, ok, info = enter_pest_control_pure(addon._state.player_data, {"automation_mode": "advanced", "duty": "assault"})
        self.assertTrue(ok, info)
        addon._state.player_data.update(data)
        addon._state.current_skill = "Activities"
        with patch.object(addon.random, "random", return_value=0.75):
            self._answer(addon)
        save = addon._state.player_data
        self.assertEqual(equipped_ammo(save), {"Bronze arrows": 98})
        self.assertEqual(ground_ammo_count(save), 2)
        self.assertEqual([row["text"] for row in save["review_event_log"] if row["text"].startswith("Ammo:")],
                         ["Ammo: 2 fired · 0 broken · 2 landed"])
        self.assertEqual(self.errors, [])

    def test_activity_bursts_share_one_card_line_for_landed_and_broken_arrows(self):
        from ankiscape.logic.castle_wars_logic import enter_castle_wars_pure
        from ankiscape.logic.fight_caves_logic import apply_fight_caves_command_pure
        for activity in ("castle_wars", "fight_caves"):
            for roll in (0.75, 0.99):
                with self.subTest(activity=activity, roll=roll):
                    addon = self._ranged_addon("ankiscape_activity_ammo_" + activity, speed=10)
                    save = addon._state.player_data
                    if activity == "castle_wars":
                        data, ok, info = enter_castle_wars_pure(save, {"automation_mode": "advanced", "duty": "defend"})
                    else:
                        data, ok, info = apply_fight_caves_command_pure(save, "enter")
                    self.assertTrue(ok, info)
                    save.update(data)
                    addon._state.current_skill = "Activities"
                    with patch.object(addon.random, "random", return_value=roll):
                        self._answer(addon)
                    fired = 100 - save["equipment_ammunition_count"]
                    landed = ground_ammo_count(save)
                    self.assertGreater(fired, 2)
                    self.assertEqual(landed, fired if roll == 0.75 else 0)
                    self.assertEqual([row["text"] for row in save["review_event_log"] if row["text"].startswith("Ammo:")],
                                     [f"Ammo: {fired} fired · {fired - landed} broken · {landed} landed"])
                    self.assertEqual(self.errors, [])

    def test_quest_combat_logs_shots_once_and_a_later_noncombat_card_logs_none(self):
        from ankiscape.data.quest.witchs_house import EXPERIMENTS
        from tests.quests.test_witchs_house import player_at
        addon = self._ranged_addon("ankiscape_quest_ammo_log", speed=10)
        save = addon._state.player_data
        quest = player_at(12)
        save.update({key: quest[key] for key in ("current_quest", "quests", "quest_action_proofs")})
        save.update(quest_combat_encounters={"witchs_house": [row[0] for row in EXPERIMENTS[:2]]},
                    quest_combat_active_encounters={"witchs_house": {EXPERIMENTS[2][0]: 1000}})
        addon._state.current_skill = "Quests"
        with patch.object(addon.random, "random", return_value=0.75):
            self._answer(addon)
        fired = 100 - save["equipment_ammunition_count"]
        self.assertGreater(fired, 0)
        lines = [row["text"] for row in save["review_event_log"] if row["text"].startswith("Ammo:")]
        self.assertEqual(lines, [f"Ammo: {fired} fired · 0 broken · {fired} landed"])
        addon._state.current_skill = "Utilities"
        save["current_utility"] = "bankstanding"
        self._answer(addon)
        self.assertEqual([row["text"] for row in save["review_event_log"] if row["text"].startswith("Ammo:")], lines)
        self.assertEqual(self.errors, [])
