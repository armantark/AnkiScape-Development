"""Guild rewards fill the pack before ordinary Combat can chain another kill."""

from copy import deepcopy
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import EQUIPMENT_DATA
from ankiscape.data.combat_data import COMBAT_ENEMY_DATA
from ankiscape.data.item_values import STACKABLE_ITEM_NAMES
from ankiscape.data.warriors_guild_data import WARRIORS_GUILD_TOKEN_KEYS
from ankiscape.logic.inventory_pure import carried_slots_used
from ankiscape.logic_pure import logic_pure_combat_engine as engine
from ankiscape.runtime import runtime_actions_combat as combat
from tests.pace.test_chain_bank_loot import loaded_player
from tests.pace.test_combat_chain import player_hits_only
from tests.pace.test_combat_danger_stops import ENEMY, answer_combat
from tests.test_runtime_actions import _context
from tests.test_combat_logic import _player


def guild_player(*, payment_mode="multi", bones=6):
    return _player(
        current_combat_target="cyclops", combat_auto_flee=False,
        constitution_level=99, combat_lifepoints=990,
        inventory={"Big bones": bones},
        carried_inventory={"cyclops": {"Big bones": bones}},
        combat_supply_loadout={"food": {"Shrimps": 20}},
        loot_overrides={"Big bones": "keep", "Bronze defender": "leave"},
        warriors_guild={
            "automation_mode": "advanced", "payment_mode": payment_mode,
            "in_cyclops_room": True,
            "tokens": dict.fromkeys(WARRIORS_GUILD_TOKEN_KEYS, 30),
        },
        combat_encounter={"target_id": "cyclops", "enemy_lifepoints": 1},
    )


def answer_guild(player, defender_roll, *, hits=((True, 1),), enemy=None, random_values=None):
    calls = {"xp": [], "saves": 0, "errors": []}
    random_values = (0.999999, 0.999999, defender_roll) * 20 if random_values is None else random_values
    ctx = _context(player, calls, random_values=random_values, review_action_multiplier=10)
    ctx.cadence_live_enabled = True
    rolls = iter(()) if callable(hits) else iter(hits)
    with patch.object(
        engine, "_combat_roll_hit",
        side_effect=hits if callable(hits) else lambda *_args, **_kw: next(rolls, (False, 0)),
    ), patch.object(combat, "COMBAT_ENEMY_DATA", {player["current_combat_target"]: enemy or COMBAT_ENEMY_DATA[player["current_combat_target"]]}):
        ok = combat.handle_combat_answer(ctx)
    return ctx, calls, ok


class ChainBankGuildRewardsTests(unittest.TestCase):
    def test_multi_payment_bonus_bone_fills_the_pack_on_the_first_real_cyclops_kill(self):
        player = guild_player()
        ctx, _calls, ok = answer_guild(player, 0.999999)
        self.assertTrue(ok, _calls)
        result = ctx.player_data["combat_last_result"]
        self.assertEqual((result["kills"], result["ticks_elapsed"]), (1, 1))
        self.assertEqual(ctx.card.stop_reason, "bank_trip")
        self.assertEqual(result["drops"], {"Big bones": 2})
        self.assertEqual(ctx.player_data["inventory"]["Big bones"], 8)
        carried = ctx.player_data["carried_inventory"]["cyclops"]
        self.assertEqual(carried, {"Big bones": 8})
        self.assertEqual(20 + carried_slots_used(carried, STACKABLE_ITEM_NAMES), 28)
        self.assertEqual(ctx.player_data["warriors_guild"]["cyclops_kills"], 1)
        self.assertEqual(ctx.player_data["combat_kill_counts"]["cyclops"], 1)
        self.assertEqual(ctx.player_data["combat_encounter"], {})
        self.assertFalse(ctx.player_data.get("combat_bank_run"))

    def test_kept_defender_fills_the_pack_even_with_an_explicit_leave_override(self):
        player = guild_player(payment_mode="single")
        ctx, _calls, ok = answer_guild(player, 0.0)
        self.assertTrue(ok, _calls)
        result = ctx.player_data["combat_last_result"]
        self.assertEqual((result["kills"], result["ticks_elapsed"]), (1, 1))
        self.assertEqual(ctx.card.stop_reason, "bank_trip")
        self.assertEqual(result["drops"], {"Big bones": 1, "Bronze defender": 1})
        self.assertEqual(ctx.player_data["inventory"]["Bronze defender"], 1)
        self.assertEqual(ctx.player_data["inventory"]["Big bones"], 7)
        self.assertEqual(ctx.player_data["warriors_guild"]["defender_drops"], 1)
        self.assertEqual(ctx.player_data["warriors_guild"]["cyclops_kills"], 1)
        self.assertEqual(ctx.player_data["carried_inventory"]["cyclops"], {"Big bones": 7, "Bronze defender": 1})
        self.assertEqual(ctx.player_data["combat_encounter"], {})
        self.assertFalse(ctx.player_data.get("combat_bank_run"))

    def test_two_kills_accumulate_all_rewards_once_before_the_pack_fills(self):
        for mode, defender_roll, drops, carried in (
            ("multi", 0.999999, {"Big bones": 4}, {"Big bones": 8}),
            ("single", 0.0, {"Big bones": 2, "Bronze defender": 2}, {"Big bones": 6, "Bronze defender": 2}),
        ):
            with self.subTest(mode=mode):
                player = guild_player(payment_mode=mode, bones=4)
                enemy = deepcopy(COMBAT_ENEMY_DATA["cyclops"])
                enemy["stats"]["hitpoints"] = 1
                ctx, _calls, ok = answer_guild(player, defender_roll, hits=player_hits_only, enemy=enemy)
                self.assertTrue(ok, _calls)
                result = ctx.player_data["combat_last_result"]
                self.assertEqual((result["kills"], result["ticks_elapsed"]), (2, 5))
                self.assertEqual(ctx.card.stop_reason, "bank_trip")
                self.assertEqual(result["drops"], drops)
                self.assertEqual(ctx.player_data["carried_inventory"]["cyclops"], carried)
                for item, count in carried.items():
                    self.assertEqual(ctx.player_data["inventory"][item], count)
                self.assertEqual(ctx.player_data["warriors_guild"]["cyclops_kills"], 2)
                self.assertEqual(ctx.player_data["warriors_guild"]["defender_drops"], 2 if mode == "single" else 0)
                self.assertEqual(ctx.player_data["combat_observed_drops"]["cyclops"]["Big bones"]["quantity_seen"], 2)
                self.assertEqual(ctx.player_data["attack_exp"], result["xp_rewards"]["attack_exp"])
                self.assertEqual(ctx.player_data["constitution_exp"], result["xp_rewards"]["constitution_exp"])

    def test_left_or_auto_buried_ordinary_bones_do_not_cause_an_early_bank_stop(self):
        for settings, held in (({"loot_overrides": {"Big bones": "leave"}}, 6),
                               ({"combat_auto_prayer_training": True}, 7)):
            with self.subTest(settings=settings):
                player = guild_player()
                player.update(settings)
                ctx, _calls, ok = answer_guild(player, 0.999999)
                self.assertTrue(ok, _calls)
                self.assertEqual(ctx.card.stop_reason, "")
                self.assertEqual(ctx.player_data["combat_last_result"]["ticks_elapsed"], 60)
                self.assertEqual(ctx.player_data["inventory"]["Big bones"], held)
                self.assertEqual(ctx.player_data["carried_inventory"]["cyclops"], {"Big bones": held})
                if settings.get("combat_auto_prayer_training"):
                    self.assertEqual(ctx.player_data["prayer_exp"], 15.0)

    def test_cyclossus_bonus_bone_is_included_and_the_clear_settles_once(self):
        player = guild_player()
        player.update(current_combat_target="cyclossus", equipment={"shield": "Rune defender"},
                      carried_inventory={"cyclossus": {"Big bones": 6}},
                      combat_encounter={"target_id": "cyclossus", "enemy_lifepoints": 1})
        player["warriors_guild"]["cyclossus_pending"] = True
        enemy = {**COMBAT_ENEMY_DATA["cyclossus"],
                 "drops": {"guaranteed": (("Big bones", 1),), "tables": ()}}
        ctx, _calls, ok = answer_guild(player, 0.999999, enemy=enemy)
        self.assertTrue(ok, _calls)
        self.assertEqual(ctx.card.stop_reason, "bank_trip")
        self.assertEqual(ctx.player_data["combat_last_result"]["ticks_elapsed"], 1)
        self.assertEqual(ctx.player_data["inventory"]["Big bones"], 8)
        self.assertEqual(ctx.player_data["warriors_guild"]["cyclossus_kills"], 1)
        self.assertFalse(ctx.player_data["warriors_guild"]["cyclossus_pending"])
        self.assertEqual(ctx.player_data["current_combat_target"], "cyclops")

    def test_table_clues_summons_and_triple_charms_share_the_same_bank_boundary(self):
        for item, quantity in (("Clue scroll (easy)", 1), ("Court summons", 1), ("Gold charm", 3)):
            with self.subTest(item=item):
                player = loaded_player(summoning_state={"triple_charm_reviews_remaining": 2},
                                       court_cases_completed_ids=["mugger"])
                enemy = {**ENEMY, "stats": {**ENEMY["stats"], "hitpoints": 60},
                         "drops": {"guaranteed": ((item, 1),), "tables": ()}}
                ctx, _calls, ok = answer_combat(player, enemy=enemy, hits=player_hits_only)
                self.assertTrue(ok, _calls)
                result = ctx.player_data["combat_last_result"]
                self.assertEqual((result["kills"], result["ticks_elapsed"]), (1, 21))
                self.assertEqual(ctx.card.stop_reason, "bank_trip")
                self.assertEqual(result["drops"], {item: quantity})
                self.assertEqual(ctx.player_data["inventory"][item], quantity)
                self.assertEqual(ctx.player_data["carried_inventory"]["chicken"][item], quantity)

    def test_pure_burst_pays_guild_rewards_once_without_mutating_its_input(self):
        player = guild_player()
        original = deepcopy(player)
        rolls = iter(((True, 1),))
        with patch.object(engine, "_combat_roll_hit", side_effect=lambda *_args, **_kw: next(rolls, (False, 0))):
            updated, ok, result = engine.apply_combat_burst_pure(
                player, COMBAT_ENEMY_DATA, EQUIPMENT_DATA, ticks=60, rng=lambda: 0.999999,
                live_cadence=True, stop_on_danger=True,
            )
        self.assertTrue(ok, result)
        self.assertEqual(player, original)
        self.assertEqual(result["stop_reason"], "bank_trip")
        self.assertEqual(updated["inventory"]["Big bones"], 8)
        self.assertEqual(updated["warriors_guild"]["cyclops_kills"], 1)

    def test_token_payment_clears_a_spawn_on_ejection_without_replaying_rewards(self):
        for tokens, ejected, target in ((30, False, "cyclossus"), (1, True, "cyclops")):
            with self.subTest(tokens=tokens):
                player = guild_player()
                player["equipment"] = {"shield": "Rune defender"}
                player["warriors_guild"].update(
                    shown_defender_index=6, token_drain_residual=99,
                    tokens=dict.fromkeys(WARRIORS_GUILD_TOKEN_KEYS, tokens),
                )
                ctx, _calls, ok = answer_guild(
                    player, 0.999999, random_values=(0.999999, 0.999999, 0.999999, 0.0),
                )
                self.assertTrue(ok, _calls)
                result = ctx.player_data["combat_last_result"]
                self.assertEqual(ctx.card.stop_reason, "bank_trip")
                self.assertEqual(result["warriors_guild"]["tokens"]["ejected"], ejected)
                self.assertEqual(ctx.player_data["warriors_guild"]["cyclossus_pending"], not ejected)
                self.assertEqual(ctx.player_data["current_combat_target"], target)
                self.assertEqual(ctx.player_data["inventory"]["Big bones"], 8)
                self.assertEqual(ctx.player_data["warriors_guild"]["cyclops_kills"], 1)
