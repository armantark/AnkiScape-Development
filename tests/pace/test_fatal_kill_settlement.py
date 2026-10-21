"""A defeated enemy pays once even when the same tick ends the encounter."""

from copy import deepcopy
from itertools import product
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import EQUIPMENT_DATA
from ankiscape.data.combat_data import COMBAT_ENEMY_DATA
from ankiscape.data.warriors_guild_data import WARRIORS_GUILD_TOKEN_KEYS
from ankiscape.logic_pure import logic_pure_combat_engine as engine
from ankiscape.runtime import runtime_actions_combat as combat
from tests.test_combat_logic import _player
from tests.test_runtime_actions import _context


def fatal_player(target="cow", *, reflection="deflect", lifepoints=10, escape=False):
    player = _player(
        current_combat_target=target, combat_auto_flee=False,
        combat_lifepoints=lifepoints, prayer_level=99, combat_prayer_points=990,
        combat_prayer_book="curses", combat_selected_prayers=["deflect_melee"],
        combat_prayer_uptime="70", combat_auto_prayer_training=True,
        quests={"the_temple_at_senntisten": {"completed": True}},
        combat_supply_loadout={"food": {"Shrimps": 2}},
        combat_encounter={"target_id": target, "enemy_lifepoints": 1,
                          "player_attack_ticks_remaining": 99,
                          "enemy_attack_ticks_remaining": 0},
        warriors_guild={"automation_mode": "advanced", "payment_mode": "multi",
                        "in_cyclops_room": True,
                        "tokens": dict.fromkeys(WARRIORS_GUILD_TOKEN_KEYS, 30)},
        slayer_assignment={"master_id": "turael_spria", "family_id": "cows",
                           "initial_count": 2, "remaining": 2},
    )
    if reflection == "vengeance":
        player.update(combat_attack_style="magic_standard", equipment={"weapon": "Staff"},
                      current_combat_spell="confuse", combat_selected_prayers=[],
                      combat_supply_loadout={"food": {"Shrimps": 2}, "runes": {
                          "Water rune": 10, "Earth rune": 10, "Body rune": 10}})
        player["combat_encounter"]["vengeance_pending"] = True
    if escape:
        player["summoning_state"] = {"active_follower": {"kind": "familiar", "entity_id": "voidshifter"}}
    return player


def answer_fatal(player, *, hit=40, enemy=None):
    target = player["current_combat_target"]
    enemy = enemy or COMBAT_ENEMY_DATA[target]
    calls = {"xp": [], "saves": 0, "errors": []}
    ctx = _context(deepcopy(player), calls, random_values=(0.999999,) * 100, review_action_multiplier=10)
    ctx.cadence_live_enabled = True
    with patch.object(engine, "_combat_roll_hit", return_value=(True, hit)), patch.object(
        combat, "COMBAT_ENEMY_DATA", {target: enemy},
    ):
        ok = combat.handle_combat_answer(ctx)
    return ctx, ok, calls


class FatalKillSettlementTests(unittest.TestCase):
    def test_fatal_deflect_cyclops_pays_guild_drops_and_prayer_xp_once(self):
        player = fatal_player("cyclops")
        original = deepcopy(player)
        ctx, ok, calls = answer_fatal(player)
        self.assertTrue(ok, calls)
        result = ctx.player_data["combat_last_result"]
        self.assertEqual((result["kills"], result["ticks_elapsed"]), (1, 1))
        self.assertEqual(ctx.card.stop_reason, "died")
        self.assertTrue(result["died"])
        self.assertEqual(result["drops"], {"Big bones": 1})
        self.assertEqual(result["xp_rewards"], {"prayer_exp": 15.0})
        self.assertEqual(ctx.player_data["prayer_exp"], 15.0)
        self.assertEqual(ctx.player_data["warriors_guild"]["cyclops_kills"], 1)
        self.assertFalse(ctx.player_data["warriors_guild"]["in_cyclops_room"])
        self.assertEqual(ctx.player_data["combat_kill_counts"]["cyclops"], 1)
        self.assertEqual(ctx.player_data["combat_grave"]["items"].count("Big bones"), 1)
        control = deepcopy(player)
        control["combat_encounter"]["enemy_lifepoints"] = 1000
        control_ctx, control_ok, control_calls = answer_fatal(control)
        self.assertTrue(control_ok, control_calls)
        grave = deepcopy(ctx.player_data["combat_grave"])
        grave["items"].remove("Big bones")
        if not grave["items"]:
            grave = {}
        self.assertEqual(grave, control_ctx.player_data.get("combat_grave", {}))
        self.assertEqual(ctx.player_data["combat_supply_loadout"], control_ctx.player_data["combat_supply_loadout"])
        self.assertEqual(ctx.player_data["combat_encounter"], {})
        self.assertEqual(ctx.player_data["combat_lifepoints"], 100)
        self.assertEqual(player, original)

    def test_fatal_vengeance_pays_slayer_and_graves_kept_loot_once(self):
        ctx, ok, calls = answer_fatal(fatal_player(reflection="vengeance"))
        self.assertTrue(ok, calls)
        result = ctx.player_data["combat_last_result"]
        self.assertEqual((result["kills"], result["ticks_elapsed"]), (1, 1))
        self.assertEqual(ctx.card.stop_reason, "died")
        self.assertEqual(result["slayer"]["credited_kills"], 1)
        self.assertEqual(ctx.player_data["slayer_assignment"]["remaining"], 1)
        self.assertEqual(ctx.player_data["slayer_exp"], COMBAT_ENEMY_DATA["cow"]["slayer_xp"])
        self.assertEqual(ctx.player_data["combat_kill_counts"]["cow"], 1)
        self.assertEqual(ctx.player_data["prayer_exp"], 4.5)
        self.assertEqual(result["drops"], {"Cowhide": 1, "Raw beef": 1})
        for item in result["drops"]:
            self.assertEqual(ctx.player_data["combat_grave"]["items"].count(item), 1)
            self.assertEqual(ctx.player_data["inventory"].get(item, 0), 0)
        self.assertEqual(ctx.player_data["combat_encounter"], {})

    def test_both_reflections_pay_before_void_shifter_escape(self):
        for reflection, hit in (("deflect", 44), ("vengeance", 15)):
            with self.subTest(reflection=reflection):
                ctx, ok, calls = answer_fatal(fatal_player(reflection=reflection, lifepoints=20, escape=True), hit=hit)
                self.assertTrue(ok, calls)
                result = ctx.player_data["combat_last_result"]
                self.assertEqual((result["kills"], result["ticks_elapsed"]), (1, 1))
                self.assertEqual(ctx.card.stop_reason, "void_shifter")
                self.assertFalse(result["died"])
                self.assertTrue(result["familiar_escape"])
                self.assertEqual(result["slayer"]["credited_kills"], 1)
                self.assertEqual(ctx.player_data["slayer_assignment"]["remaining"], 1)
                self.assertEqual(ctx.player_data["prayer_exp"], 4.5)
                self.assertEqual(ctx.player_data["inventory"]["Cowhide"], 1)
                self.assertEqual(ctx.player_data["carried_inventory"]["cow"]["Cowhide"], 1)
                self.assertEqual(ctx.player_data["combat_encounter"], {})
                self.assertFalse(ctx.player_data.get("combat_grave"))

    def test_death_prayers_pay_when_enemy_hit_recoil_or_status_kills_the_player(self):
        for prayer, cause in product(("wrath", "retribution"), ("enemy_hit", "recoil", "poison")):
            with self.subTest(prayer=prayer, cause=cause):
                player = fatal_player(lifepoints=1)
                player.update(combat_prayer_book="curses" if prayer == "wrath" else "standard",
                              combat_selected_prayers=[prayer])
                player["combat_encounter"]["enemy_lifepoints"] = 2
                enemy = deepcopy(COMBAT_ENEMY_DATA["cow"])
                if cause == "recoil":
                    enemy["melee_recoil_damage"] = 1
                    player["combat_encounter"]["player_attack_ticks_remaining"] = 0
                if cause == "poison":
                    player["combat_status_effects"] = {"poison": {"ticks_left": 31, "tick_progress": 29}}
                ctx, ok, calls = answer_fatal(player, hit=1, enemy=enemy)
                self.assertTrue(ok, calls)
                result = ctx.player_data["combat_last_result"]
                self.assertEqual((result["kills"], result["ticks_elapsed"]), (1, 1))
                self.assertEqual(ctx.card.stop_reason, "died")
                self.assertTrue(result["died"])
                if cause == "poison":
                    self.assertGreater(result["status_damage"]["poison"], 0)
                self.assertEqual(result["death_prayer_damage"], 1 if cause == "recoil" else 2)
                self.assertEqual(result["slayer"]["credited_kills"], 1)
                expected_xp = {"prayer_exp": 4.5, "slayer_exp": 8.0}
                if cause == "recoil":
                    expected_xp.update(attack_exp=0.39, constitution_exp=0.129675)
                self.assertEqual(result["xp_rewards"], expected_xp)
                for skill, xp in expected_xp.items():
                    self.assertEqual(ctx.player_data[skill], xp)
                self.assertEqual(ctx.player_data["combat_grave"]["items"].count("Cowhide"), 1)
                self.assertEqual(ctx.player_data["combat_encounter"], {})

    def test_legacy_reflection_and_death_prayer_kills_pay_before_grave_settlement(self):
        for reflection in ("deflect", "vengeance", "retribution"):
            with self.subTest(reflection=reflection):
                player = fatal_player(reflection=reflection)
                if reflection == "retribution":
                    player.update(combat_prayer_book="standard", combat_selected_prayers=["retribution"])
                with patch.object(engine, "_combat_roll_hit", side_effect=lambda *_args, **kw: (False, 0) if "blocked" in kw else (True, 40)):
                    updated, ok, result = engine.apply_combat_burst_pure(
                        player, COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=5,
                        rng=lambda: 0.999999, live_cadence=False,
                    )
                self.assertTrue(ok, result)
                self.assertEqual(result["kills"], 1)
                self.assertTrue(result["died"])
                self.assertEqual(result["stop_reason"], "")
                self.assertEqual(updated["combat_kill_counts"]["cow"], 1)
                self.assertEqual(updated["prayer_exp"], 4.5)
                self.assertEqual(result["drops"], {"Cowhide": 1, "Raw beef": 1})
                self.assertEqual(updated["combat_encounter"], {})

        with self.subTest(legacy_direct_mutual_death=True):
            player = _player(current_combat_target="cow", combat_auto_flee=False,
                             equipment={"weapon": "Bronze sword"}, combat_lifepoints=10)
            enemy = deepcopy(COMBAT_ENEMY_DATA["cow"])
            enemy.update(melee_recoil_damage=10, drops={"guaranteed": (("Bones", 1),), "tables": ()})
            enemy["stats"]["hitpoints"] = 1
            with patch.object(engine, "_combat_roll_hit", side_effect=lambda *_args, **kw: (True, 1) if "blocked" in kw else (False, 0)):
                _updated, ok, result = engine.apply_combat_burst_pure(
                    player, {"cow": enemy}, EQUIPMENT_DATA, ticks=10,
                    rng=lambda: 0.999999, live_cadence=False,
                )
            self.assertTrue(ok, result)
            self.assertEqual((result["kills"], result["ticks_elapsed"], result["enemy_lifepoints"]), (3, 10, 1))
            self.assertTrue(result["died"])
            self.assertEqual(result["stop_reason"], "")
            self.assertEqual(result["drops"], {"Bones": 3})
            self.assertEqual(result["xp_rewards"], {"attack_exp": 1.17, "constitution_exp": 0.38902500000000007})

    def test_safe_death_and_no_grave_keep_their_cleanup_when_a_death_prayer_kills(self):
        for live in (False, True):
            for flags in ({"safe_death": True}, {"no_grave": True}):
                with self.subTest(live=live, flags=flags):
                    player = fatal_player()
                    player.update(combat_prayer_book="standard", combat_selected_prayers=["retribution"],
                                  equipment={"weapon": "Bronze sword"})
                    with patch.object(engine, "_combat_roll_hit", side_effect=lambda *_args, **kw: (False, 0) if "blocked" in kw else (True, 40)):
                        updated, ok, result = engine.apply_combat_burst_pure(
                            player, COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=5,
                            rng=lambda: 0.999999, live_cadence=live, **flags,
                        )
                    self.assertTrue(ok, result)
                    self.assertEqual(result["kills"], 1)
                    self.assertTrue(result["died"])
                    self.assertEqual(result["safe_death"], bool(flags.get("safe_death")))
                    self.assertEqual(result["stop_reason"], "died" if live else "")
                    self.assertEqual(updated["combat_lifepoints"], 100)
                    self.assertEqual(updated["combat_encounter"], {})
                    self.assertEqual(updated["combat_status_effects"], {})
                    self.assertFalse(updated.get("combat_grave"))
                    self.assertEqual(updated["equipment"], {"weapon": "Bronze sword"})
                    self.assertEqual(updated["combat_kill_counts"]["cow"], 1)
                    self.assertEqual(updated["prayer_exp"], 4.5)
