from __future__ import annotations

import copy
import os
import unittest
from dataclasses import asdict
from unittest.mock import patch

from pest_control_data import (
    PEST_CONTROL_COMMENDATION_CAP,
    PEST_CONTROL_EVENT_REVIEWS,
    PEST_CONTROL_FRONTS,
    PEST_CONTROL_LANDERS_BY_ID,
    VOID_SEAL_ITEM_IDS,
    pest_control_equipment_data_as_dict,
    pest_control_portal_enemy_pure,
)
from pest_control_logic import (
    apply_pest_control_review_pure,
    buy_void_seal_pure,
    enter_pest_control_pure,
    leave_pest_control_pure,
    pest_control_view_pure,
    sanitize_pest_control_state_pure,
    set_pest_control_policy_pure,
)


def _player(**overrides):
    player = {
        "attack_level": 40,
        "strength_level": 40,
        "defense_level": 40,
        "constitution_level": 40,
        "ranged_level": 40,
        "magic_level": 40,
        "prayer_level": 40,
        "summoning_level": 1,
        "activity_session": {"active_id": ""},
        "combat_encounter": {},
        "current_combat_target": "chicken",
        "inventory": {},
        "equipment": {},
        "coins": 0,
    }
    player.update(overrides)
    return player


def _entered(**overrides):
    data, ok, info = enter_pest_control_pure(_player(**overrides))
    assert ok, info
    return data


def _combat_stub(damage: int = 0, *, died: bool = False):
    def _apply(data, _enemy_data, _equipment_data, **_kwargs):
        updated = copy.deepcopy(data)
        before = int(updated["combat_encounter"]["enemy_lifepoints"])
        after = max(0, before - damage)
        updated["combat_encounter"]["enemy_lifepoints"] = after
        return updated, True, {
            "player_damage": min(before, damage),
            "enemy_lifepoints": after,
            "killed": after == 0,
            "died": died,
            "safe_death": died,
            "xp_rewards": {"attack_exp": damage * 0.2} if damage else {},
        }

    return _apply


class PestControlDataTests(unittest.TestCase):
    def test_activity_and_all_charged_seals_are_registered_with_assets(self):
        from constants import ITEM_DEFINITIONS, UTILITY_ACTIVITY_DATA

        icon_path = UTILITY_ACTIVITY_DATA["pest_control"].get("icon_path")
        self.assertTrue(icon_path)
        self.assertTrue(os.path.exists(icon_path))
        item_definitions = {item.storage_key: item for item in ITEM_DEFINITIONS}
        for charge in range(8, 0, -1):
            item = item_definitions[f"Void seal ({charge})"]
            self.assertTrue(item.asset_path)
            self.assertTrue(os.path.exists(item.asset_path))

    def test_period_landers_front_roles_and_half_xp_portal_are_explicit(self):
        self.assertEqual(
            [
                (
                    row.combat_level,
                    row.portal_lifepoints,
                    row.commendations,
                )
                for row in PEST_CONTROL_LANDERS_BY_ID.values()
            ],
            [(40, 2000, 2), (70, 2500, 3), (100, 2500, 4)],
        )
        self.assertEqual(len(PEST_CONTROL_FRONTS), 4)
        self.assertEqual(PEST_CONTROL_FRONTS[1].role_id, "spinners")
        portal = pest_control_portal_enemy_pure("novice", 1)
        self.assertEqual(portal["stats"]["hitpoints"], 2000)
        self.assertEqual(portal["xp_multiplier"], 0.5)

    def test_all_eight_period_seal_states_keep_the_configured_neck_bonuses(self):
        equipment = pest_control_equipment_data_as_dict()
        self.assertEqual(len(equipment), 8)
        self.assertEqual(VOID_SEAL_ITEM_IDS[8], 11666)
        self.assertEqual(VOID_SEAL_ITEM_IDS[1], 11673)
        seal = equipment["Void seal (8)"]
        self.assertEqual(seal.slot, "neck")
        bonuses = asdict(seal.bonuses)
        self.assertEqual(
            {key: value for key, value in bonuses.items() if value},
            {
                "defence_stab": 1,
                "defence_slash": 1,
                "defence_crush": 1,
                "defence_magic": 1,
                "defence_ranged": 1,
            },
        )


class PestControlEntryAndStateTests(unittest.TestCase):
    def test_entry_uses_best_casual_lander_and_preserves_previous_combat_target(self):
        data = _player(
            attack_level=80,
            strength_level=80,
            defense_level=80,
            constitution_level=80,
            ranged_level=80,
            magic_level=80,
            prayer_level=80,
        )
        entered, ok, info = enter_pest_control_pure(data)
        self.assertTrue(ok, info)
        self.assertEqual(entered["pest_control"]["lander_id"], "veteran")
        self.assertEqual(entered["activity_session"], {"active_id": "pest_control"})
        self.assertEqual(entered["pest_control"]["previous_combat_target"], "chicken")

    def test_entry_enforces_combat_gate_session_and_follower_exclusion(self):
        low = _player(
            attack_level=1,
            strength_level=1,
            defense_level=1,
            constitution_level=10,
            ranged_level=1,
            magic_level=1,
            prayer_level=1,
        )
        _same, ok, info = enter_pest_control_pure(low)
        self.assertFalse(ok)
        self.assertIn("combat level 40", info["reason"])

        _same, ok, info = enter_pest_control_pure(
            _player(activity_session={"active_id": "barrows"})
        )
        self.assertFalse(ok)
        self.assertIn("persistent activity", info["reason"])

        follower = _player(
            summoning_state={
                "active_follower": {
                    "kind": "familiar",
                    "entity_id": "spirit_wolf",
                    "remaining_reviews": 3,
                    "max_reviews": 3,
                    "storage": {},
                }
            }
        )
        _same, ok, info = enter_pest_control_pure(follower)
        self.assertFalse(ok)
        self.assertTrue(info["requires_confirmation"])

    def test_advanced_policy_rejects_an_ineligible_lander(self):
        data, ok, info = set_pest_control_policy_pure(
            _player(),
            {
                "automation_mode": "advanced",
                "lander_id": "veteran",
                "duty": "assault",
            },
        )
        self.assertFalse(ok)
        self.assertIn("combat level 100", info["reason"])
        self.assertNotIn("pest_control_policy", data)

    def test_sanitizer_rejects_a_session_owned_by_another_activity(self):
        malformed = _player(
            pest_control={
                "lander_id": "unknown",
                "review": 99,
                "portal_index": 99,
                "portal_lifepoints": -4,
            },
            activity_session={"active_id": "barrows"},
        )
        state = sanitize_pest_control_state_pure(malformed)
        self.assertEqual(state["pest_control"], {})
        self.assertEqual(state["pest_control_commendations"], 0)


class PestControlAssaultTests(unittest.TestCase):
    def test_casual_shared_assault_wins_and_pays_period_rewards(self):
        data = _entered()
        with patch("pest_control_logic.apply_combat_burst_pure", _combat_stub(0)):
            for _ in range(PEST_CONTROL_EVENT_REVIEWS):
                data, ok, result = apply_pest_control_review_pure(
                    data,
                    lambda: 0.5,
                    productive=True,
                )
                self.assertTrue(ok, result)
                if result.get("terminal"):
                    break

        self.assertTrue(result["terminal"])
        self.assertTrue(result["won"])
        self.assertEqual(result["coins"], 510)
        self.assertEqual(result["commendations"], 2)
        self.assertEqual(data["pest_control"], {})
        self.assertEqual(data["current_combat_target"], "chicken")
        self.assertGreater(data["pest_control_games_won"], 0)

    def test_advanced_all_out_assault_can_lose_the_knight_for_zero_reward(self):
        player, ok, info = set_pest_control_policy_pure(
            _player(),
            {
                "automation_mode": "advanced",
                "lander_id": "novice",
                "duty": "assault",
            },
        )
        self.assertTrue(ok, info)
        data, ok, info = enter_pest_control_pure(player)
        self.assertTrue(ok, info)
        with patch("pest_control_logic.apply_combat_burst_pure", _combat_stub(0)):
            for _ in range(PEST_CONTROL_EVENT_REVIEWS):
                data, ok, result = apply_pest_control_review_pure(
                    data,
                    lambda: 0.5,
                    productive=True,
                )
                self.assertTrue(ok, result)
                if result.get("terminal"):
                    break

        self.assertFalse(result["won"])
        self.assertEqual(result["coins"], 0)
        self.assertEqual(result["commendations"], 0)
        self.assertEqual(data["pest_control_games_lost"], 1)

    def test_again_advances_crowd_and_pressure_without_player_contribution(self):
        data = _entered()
        data, ok, result = apply_pest_control_review_pure(
            data,
            lambda: 0.5,
            productive=False,
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["duty"], "idle")
        self.assertEqual(data["pest_control"]["contribution"], 0)
        self.assertLess(data["pest_control"]["portal_lifepoints"], 2000)
        self.assertLess(data["pest_control"]["knight_lifepoints"], 2000)

    def test_attack_uses_six_tick_live_combat_and_preserves_half_rate_xp(self):
        data = _entered()
        captured = {}

        def fake(data, enemies, equipment, **kwargs):
            captured.update(kwargs)
            self.assertEqual(enemies["pest_control_portal_front"]["xp_multiplier"], 0.5)
            return _combat_stub(100)(data, enemies, equipment, **kwargs)

        with patch("pest_control_logic.apply_combat_burst_pure", fake):
            updated, ok, result = apply_pest_control_review_pure(
                data,
                lambda: 0.5,
                productive=True,
            )
        self.assertTrue(ok, result)
        self.assertEqual(captured["ticks"], 6)
        self.assertTrue(captured["live_cadence"])
        self.assertEqual(updated["pest_control"]["contribution"], 100)
        self.assertEqual(result["xp_rewards"], {"attack_exp": 20.0})

    def test_safe_player_death_does_not_end_the_team_game(self):
        data = _entered()
        with patch(
            "pest_control_logic.apply_combat_burst_pure",
            _combat_stub(0, died=True),
        ):
            updated, ok, result = apply_pest_control_review_pure(
                data,
                lambda: 0.5,
                productive=True,
            )
        self.assertTrue(ok, result)
        self.assertTrue(result["died"])
        self.assertFalse(result["terminal"])
        self.assertTrue(updated["pest_control"])


class PestControlSealAndExitTests(unittest.TestCase):
    def test_reward_purchase_caps_wallet_and_banks_an_eight_charge_seal(self):
        player = _player(pest_control_commendations=12)
        bought, ok, info = buy_void_seal_pure(player)
        self.assertTrue(ok, info)
        self.assertEqual(bought["pest_control_commendations"], 2)
        self.assertEqual(bought["inventory"]["Void seal (8)"], 1)

        view = pest_control_view_pure(
            _player(pest_control_commendations=999)
        )
        self.assertEqual(view["pest_control_commendations"], PEST_CONTROL_COMMENDATION_CAP)

    def test_seal_duty_preserves_remainder_and_never_adds_contribution(self):
        player = _player(inventory={"Void seal (8)": 1})
        player, ok, info = set_pest_control_policy_pure(
            player,
            {
                "automation_mode": "advanced",
                "lander_id": "novice",
                "duty": "seal",
            },
        )
        self.assertTrue(ok, info)
        data, ok, info = enter_pest_control_pure(player)
        self.assertTrue(ok, info)
        updated, ok, result = apply_pest_control_review_pure(
            data,
            lambda: 0.5,
            productive=True,
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["duty"], "seal")
        self.assertEqual(result["seal_charges_remaining"], 7)
        self.assertEqual(updated["inventory"]["Void seal (7)"], 1)
        self.assertEqual(updated["pest_control"]["contribution"], 0)

    def test_leave_forfeits_rewards_and_restores_combat_target(self):
        data = _entered(pest_control_commendations=7, coins=50)
        left, ok, info = leave_pest_control_pure(data)
        self.assertTrue(ok, info)
        self.assertEqual(left["pest_control_commendations"], 7)
        self.assertEqual(left["coins"], 50)
        self.assertEqual(left["pest_control"], {})
        self.assertEqual(left["current_combat_target"], "chicken")


if __name__ == "__main__":
    unittest.main()
