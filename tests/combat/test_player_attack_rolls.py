"""Whole bursts retain player formulas across real stat drains and bonuses."""

from copy import deepcopy
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
from ankiscape.core.constants import EQUIPMENT_DATA
from ankiscape.data.combat_data import COMBAT_ENEMY_DATA
from ankiscape.data.warriors_guild_data import MULTI_DAMAGE_MULTIPLIER, WARRIORS_GUILD_TOKEN_KEYS
from ankiscape.logic.warriors_guild_logic import (
    enter_warriors_guild_cyclops_room_pure, set_warriors_guild_policy_pure,
)
from ankiscape.logic_pure import logic_pure_combat_engine as engine
from tests.test_combat_logic import _player, _rng
from tests.test_warriors_guild import _player as guild_base_player


def drain_player(combat_class, target=None, prayers=()):
    weapon, style, default_target, supplies = {
        "melee": ("Bronze sword", "accurate", "cockatrice", {}),
        "ranged": ("Shortbow", "ranged_accurate", "cockatrice", {"ammo": {"Bronze arrows": 100}}),
        "magic": ("Staff", "magic_standard", "basilisk", {"runes": {"Air rune": 100, "Mind rune": 100}}),
    }[combat_class]
    return _player(
        current_combat_target=target or default_target,
        attack_level=60, strength_level=60, defense_level=99,
        ranged_level=60, magic_level=60, agility_level=60, slayer_level=99,
        constitution_level=99, combat_lifepoints=990, combat_auto_flee=False,
        combat_auto_eat_food=[], equipment={"weapon": weapon},
        combat_attack_style=style, combat_attack_style_type="stab",
        combat_supply_loadout=supplies, prayer_level=99, combat_prayer_points=990,
        combat_prayer_uptime="100", combat_selected_prayers=list(prayers),
        quests={"priest_in_peril": {"completed": True}},
    )


def charge_player(active):
    player = drain_player("magic")
    player.update(
        magic_level=99, current_combat_spell="saradomin_strike",
        equipment={"weapon": "Saradomin staff", "cape": "Saradomin cape"},
        combat_supply_loadout={"runes": {"Air rune": 40, "Fire rune": 20, "Blood rune": 20}},
        mage_arena={"step": 5, "completed": True, "alignment": "saradomin", "attuned_spells": ["saradomin_strike"]},
        magic_charge_active=active, magic_charge_ticks_remaining=700,
    )
    return player


def guild_player(payment):
    player, ok, info = set_warriors_guild_policy_pure(
        guild_base_player(), automation_mode="advanced", payment_mode=payment,
    )
    assert ok, info
    player["warriors_guild"]["tokens"] = {key: 200 for key in WARRIORS_GUILD_TOKEN_KEYS}
    player, ok, info = enter_warriors_guild_cyclops_room_pure(player)
    assert ok, info
    return player


def observe_burst(player, ticks, live=False, prefix=()):
    events = []
    original = engine._combat_player_attack_rolls

    def observe(*args):
        result = original(*args)
        events.append((deepcopy(args[0]["combat_current_levels"]), deepcopy(args[5]), result))
        return result

    supplied = deepcopy(player)
    with patch.object(engine, "_combat_player_attack_rolls", side_effect=observe), patch.object(engine, "_combat_roll_damage_lifepoints", wraps=engine._combat_roll_damage_lifepoints) as damage, patch.object(engine, "warriors_guild_cyclops_damage_multiplier_pure", wraps=engine.warriors_guild_cyclops_damage_multiplier_pure) as guild:
        result = engine.apply_combat_burst_pure(
            supplied, COMBAT_ENEMY_DATA, EQUIPMENT_DATA,
            ticks=ticks, live_cadence=live, rng=_rng(prefix),
        )
    assert supplied == player and result[1], result
    return result, events, [call.args[0] for call in damage.call_args_list], guild.call_count


class CombatPlayerAttackRollsTest(unittest.TestCase):
    def test_actual_drains_recalculate_each_class_in_both_cadences(self):
        for combat_class, skill in (("melee", "attack"), ("ranged", "ranged"), ("magic", "magic")):
            for live in (False, True):
                with self.subTest(combat_class=combat_class, live=live):
                    result, events, _damage, _guild = observe_burst(drain_player(combat_class), 19, live)
                    self.assertEqual(result[2]["combat_class"], combat_class)
                    self.assertGreater(result[2]["stat_drains"][skill], 0)
                    self.assertGreater(len(events), 1)
                    self.assertEqual(events[0][0], {})
                    self.assertLess(events[-1][0][skill], 60)
                    self.assertLess(events[-1][2][0], events[0][2][0])
                    self.assertLessEqual(events[-1][2][1], events[0][2][1])

    def test_spectre_prayer_blocks_the_drain_recalculation(self):
        plain, plain_events, _, _ = observe_burst(drain_player("magic", "aberrant_spectre"), 13)
        protected, events, _, _ = observe_burst(drain_player("magic", "aberrant_spectre", ("protect_from_magic",)), 13)
        self.assertGreater(plain[2]["stat_drains"]["magic"], 0)
        self.assertGreater(len(plain_events), 1)
        self.assertEqual(protected[2]["stat_drains"], {})
        self.assertEqual(len(events), 1)
        self.assertGreater(protected[2]["unprotected_attacks"], 0)
        self.assertEqual(plain[2]["enemy_damage"], protected[2]["enemy_damage"])

    def test_rigour_keeps_independent_attack_and_strength_factors_after_drains(self):
        _, plain, _, _ = observe_burst(drain_player("ranged"), 19)
        result, rigour, _, _ = observe_burst(drain_player("ranged", prayers=("rigour",)), 19)
        self.assertIn("rigour", result[2]["prayers"])
        self.assertGreater(result[2]["stat_drains"]["ranged"], 0)
        for index in (0, -1):
            self.assertEqual(rigour[index][1]["ranged_attack"], 1.20)
            self.assertEqual(rigour[index][1]["ranged_strength"], 1.23)
            self.assertAlmostEqual(rigour[index][2][0] / plain[index][2][0], 1.20)
            self.assertAlmostEqual((rigour[index][2][1] - 0.5) / (plain[index][2][1] - 0.5), 1.23)

    def test_charge_reaches_the_burst_damage_roll(self):
        for active, maximum in ((False, 20), (True, 30)):
            with self.subTest(active=active):
                result, events, maxima, _ = observe_burst(charge_player(active), 1, prefix=(0.0, 0.999999))
                self.assertEqual(result[2]["spell_id"], "saradomin_strike")
                self.assertEqual(events[0][2][1], maximum)
                self.assertEqual(maxima, [maximum])
                self.assertGreater(result[2]["player_damage"], 0)

    def test_guild_multiplier_stays_outside_the_formula_and_runs_once(self):
        values = []
        for payment, factor in (("single", 1.0), ("multi", MULTI_DAMAGE_MULTIPLIER)):
            result, events, maxima, calls = observe_burst(guild_player(payment), 1, prefix=(0.0, 0.999999))
            self.assertEqual(calls, 1)
            self.assertEqual(len(events), 1)
            self.assertEqual(maxima, [events[0][2][1] * factor])
            self.assertGreater(result[2]["player_damage"], 0)
            values.append(events[0][2])
        self.assertEqual(values[0], values[1])
