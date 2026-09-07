"""Combat kill paths preserve pending loot and prayer reward ordering."""

from copy import deepcopy
import unittest

import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
from ankiscape.core.constants import EQUIPMENT_DATA
from ankiscape.data.combat_data import COMBAT_ENEMY_DATA
from ankiscape.logic_pure.logic_pure_combat_engine import apply_combat_burst_pure
from tests.test_combat_logic import _player, _rng


def _reward_enemy():
    enemy = deepcopy(COMBAT_ENEMY_DATA["chicken"])
    enemy["drops"] = {
        "guaranteed": (("Bones", 1), ("Gold charm", 1), ("Clue scroll (easy)", 1)),
        "tables": (),
    }
    return enemy


def _reflection_player():
    return _player(
        current_combat_target="reward_target",
        combat_attack_style="magic_standard",
        current_combat_spell="wind_strike",
        equipment={"weapon": "Staff of air"},
        combat_auto_flee=False,
        combat_vengeance=True,
        combat_spellbook_swap="vengeance",
        quests={"lunar_diplomacy": {"completed": True}},
        combat_supply_loadout={"runes": {"Mind rune": 1}},
        combat_encounter={
            "target_id": "reward_target",
            "enemy_lifepoints": 5,
            "spellbook_swap_paid": True,
            "vengeance_pending": True,
        },
        combat_auto_prayer_training=True,
        summoning_state={"triple_charm_reviews_remaining": 2},
    )


def _reflection_enemy():
    enemy = _reward_enemy()
    enemy.update(
        stats={"attack": 99, "strength": 20, "defence": 99, "hitpoints": 1000},
        bonuses={},
        attack_speed=1,
    )
    return enemy


class CombatKillRewardsTest(unittest.TestCase):
    def test_chained_kills_reserve_one_clue_and_record_rewards_before_burial(self):
        player = _player(
            combat_auto_prayer_training=True,
            summoning_state={"triple_charm_reviews_remaining": 2},
        )
        original = deepcopy(player)
        updated, ok, result = apply_combat_burst_pure(
            player,
            {"chicken": _reward_enemy()},
            EQUIPMENT_DATA,
            ticks=50,
            rng=lambda: 0.5,
        )

        self.assertTrue(ok, result)
        self.assertEqual(result["kills"], 9)
        self.assertEqual(player, original)
        self.assertEqual(updated["inventory"]["Clue scroll (easy)"], 1)
        self.assertEqual(result["clue_refusal_reason"], "You already have a clue scroll: Clue scroll (easy)")
        self.assertEqual(updated["inventory"]["Gold charm"], 3 * result["kills"])
        self.assertNotIn("Bones", updated["inventory"])
        self.assertEqual(result["xp_rewards"]["prayer_exp"], 4.5 * result["kills"])
        self.assertGreater(result["xp_rewards"]["attack_exp"], 0)
        observed = updated["combat_observed_drops"]["chicken"]
        self.assertEqual(observed["Bones"]["times_seen"], result["kills"])
        self.assertEqual(observed["Gold charm"]["quantity_seen"], 3 * result["kills"])
        self.assertEqual(observed["Clue scroll (easy)"]["quantity_seen"], 1)

    def test_reflected_kills_preserve_spell_xp_charms_and_burial_in_both_cadences(self):
        for live_cadence in (False, True):
            with self.subTest(live_cadence=live_cadence):
                player = _reflection_player()
                original = deepcopy(player)
                updated, ok, result = apply_combat_burst_pure(
                    player,
                    {"reward_target": _reflection_enemy()},
                    EQUIPMENT_DATA,
                    ticks=2,
                    rng=_rng([0.999999, 0.0, 0.999999]),
                    live_cadence=live_cadence,
                )

                self.assertTrue(ok, result)
                self.assertEqual(player, original)
                self.assertEqual(result["kills"], 1)
                self.assertEqual(result["player_hits_landed"], 0)
                self.assertEqual(result["drops"], {"Gold charm": 3, "Clue scroll (easy)": 1})
                self.assertEqual(result["xp_rewards"]["prayer_exp"], 4.5)
                self.assertGreater(result["xp_rewards"]["magic_exp"], 0)
                self.assertEqual(updated["combat_observed_drops"]["reward_target"]["Bones"]["quantity_seen"], 1)
