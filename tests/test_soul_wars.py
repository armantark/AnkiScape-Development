from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from combat_data import COMBAT_ENEMY_DATA
from constants import COMBAT_ENEMY_IMAGES, UTILITY_ACTIVITY_DATA
from soul_wars_data import (
    SOUL_WARS_ACTIVITY_ID,
    SOUL_WARS_AVATAR_LIFEPOINTS,
    SOUL_WARS_CHARM_REWARDS_BY_ITEM,
    SOUL_WARS_COMBAT_TARGET_ID,
    SOUL_WARS_EVENT_REVIEWS,
    SOUL_WARS_ZEAL_CAP,
    soul_wars_avatar_enemy_pure,
    soul_wars_charm_quantity_pure,
)
from soul_wars_logic import (
    apply_soul_wars_command_pure,
    apply_soul_wars_review_pure,
    buy_soul_wars_charms_pure,
    enter_soul_wars_pure,
    leave_soul_wars_pure,
    sanitize_soul_wars_state_pure,
    set_soul_wars_policy_pure,
    soul_wars_view_pure,
)


ROOT = Path(__file__).resolve().parents[1]


def _player(**overrides):
    player = {
        "attack_level": 40,
        "strength_level": 40,
        "defense_level": 40,
        "constitution_level": 40,
        "ranged_level": 40,
        "magic_level": 40,
        "prayer_level": 40,
        "slayer_level": 40,
        "summoning_level": 40,
        "combat_lifepoints": 400,
        "combat_prayer_points": 100,
        "combat_special_attack_energy": 5,
        "agility_run_energy_credit_pct": 0,
        "summoning_state": {"summoning_points_current": 2},
        "activity_session": {"active_id": ""},
        "combat_encounter": {},
        "current_combat_target": "chicken",
        "current_utility": "gnome_restaurant",
        "combat_supply_loadout": {"food": {}},
        "inventory": {},
        "equipment": {},
    }
    player.update(overrides)
    return player


def _entered(**overrides):
    data, ok, info = enter_soul_wars_pure(_player(**overrides))
    assert ok, info
    return data


def _combat_stub(*, damage=500, died=False):
    def _apply(data, enemies, _equipment, **kwargs):
        updated = copy.deepcopy(data)
        encounter = dict(updated["combat_encounter"])
        before = int(encounter["enemy_lifepoints"])
        after = max(0, before - damage)
        encounter["enemy_lifepoints"] = after
        updated["combat_encounter"] = encounter
        updated["combat_lifepoints"] = 0 if died else int(updated["combat_lifepoints"])
        return updated, True, {
            "captured_ticks": kwargs.get("ticks"),
            "captured_live": kwargs.get("live_cadence"),
            "captured_safe": kwargs.get("safe_death"),
            "enemy": next(iter(enemies.values())),
            "player_damage": min(before, damage),
            "enemy_lifepoints": after,
            "killed": after == 0,
            "died": died,
            "safe_death": died,
            "xp_rewards": {"attack_exp": damage * 0.4},
        }

    return _apply


class SoulWarsDataTests(unittest.TestCase):
    def test_period_avatar_zeal_and_charm_bands_are_explicit(self):
        avatar = soul_wars_avatar_enemy_pure()
        self.assertEqual(avatar["level"], 525)
        self.assertEqual(avatar["stats"]["hitpoints"], 10_000)
        self.assertEqual(avatar["xp_multiplier"], 1.0)
        self.assertEqual(SOUL_WARS_ZEAL_CAP, 50_000)
        self.assertEqual(
            [soul_wars_charm_quantity_pure("Gold charm", level) for level in (13, 75, 83, 100, 109, 125, 137)],
            [6, 14, 24, 34, 41, 47, 52],
        )
        self.assertEqual(soul_wars_charm_quantity_pure("Blue charm", 83), 19)

    def test_registry_assets_and_provenance_are_reachable(self):
        activity = UTILITY_ACTIVITY_DATA[SOUL_WARS_ACTIVITY_ID]
        self.assertEqual(activity["surface"], "activities")
        self.assertEqual(activity["group"], "minigames")
        self.assertTrue(Path(activity["icon_path"]).is_file())
        self.assertIn(SOUL_WARS_COMBAT_TARGET_ID, COMBAT_ENEMY_DATA)
        self.assertTrue(Path(COMBAT_ENEMY_IMAGES[SOUL_WARS_COMBAT_TARGET_ID]).is_file())

        provenance = json.loads(
            (ROOT / "assets_provenance.json").read_text(encoding="utf-8")
        )
        for relative_path in (
            "activityicons/soul_wars.png",
            "activityitems/soul_wars_soul_fragment.png",
            "combatenemies/soul_wars_enemy_avatar.png",
        ):
            self.assertIn(relative_path, provenance)


class SoulWarsEntryAndPolicyTests(unittest.TestCase):
    def test_command_router_handles_public_actions_and_rejects_unknown_commands(self):
        player, ok, info = apply_soul_wars_command_pure(
            _player(),
            "set_policy",
            {"automation_mode": "advanced", "duty": "defend", "team": "creation"},
        )
        self.assertTrue(ok, info)
        player, ok, info = apply_soul_wars_command_pure(player, "enter")
        self.assertTrue(ok, info)
        self.assertEqual(player["soul_wars"]["duty"], "defend")

        unchanged, ok, info = apply_soul_wars_command_pure(player, "unknown")
        self.assertFalse(ok)
        self.assertEqual(unchanged, player)
        self.assertIn("Unknown", info["reason"])

    def test_entry_has_no_level_or_quest_gate_and_allows_a_familiar(self):
        low = _player(
            attack_level=1,
            strength_level=1,
            defense_level=1,
            constitution_level=10,
            ranged_level=1,
            magic_level=1,
            prayer_level=1,
            slayer_level=1,
            summoning_level=1,
            summoning_state={
                "active_follower": {"kind": "familiar", "entity_id": "spirit_wolf"},
                "summoning_points_current": 1,
            },
        )
        entered, ok, info = enter_soul_wars_pure(low)
        self.assertTrue(ok, info)
        self.assertEqual(entered["activity_session"], {"active_id": "soul_wars"})
        self.assertEqual(entered["soul_wars"]["previous_combat_target"], "chicken")
        self.assertIn("active_follower", entered["summoning_state"])

    def test_entry_blocks_the_period_cape_and_food_restrictions(self):
        for player, phrase in (
            (_player(equipment={"cape": "Cape"}), "equipped cape"),
            (
                _player(combat_supply_loadout={"food": {"Lobster": 1}}),
                "carried food",
            ),
        ):
            _same, ok, info = enter_soul_wars_pure(player)
            self.assertFalse(ok)
            self.assertIn(phrase, info["reason"])

    def test_policy_and_sanitizer_keep_only_valid_match_state(self):
        player, ok, info = set_soul_wars_policy_pure(
            _player(),
            {"automation_mode": "advanced", "duty": "defend", "team": "creation"},
        )
        self.assertTrue(ok, info)
        entered, ok, info = enter_soul_wars_pure(player)
        self.assertTrue(ok, info)
        self.assertEqual(entered["soul_wars"]["duty"], "defend")
        self.assertEqual(entered["soul_wars"]["team"], "creation")

        state = sanitize_soul_wars_state_pure(
            _player(
                soul_wars={"review": 999, "control_balance": 99},
                soul_wars_zeal=99_999,
                activity_session={"active_id": "barrows"},
            )
        )
        self.assertEqual(state["soul_wars"], {})
        self.assertEqual(state["soul_wars_zeal"], SOUL_WARS_ZEAL_CAP)


class SoulWarsObjectiveTests(unittest.TestCase):
    def test_casual_captures_then_gathers_and_offers_fragments(self):
        data = _entered(slayer_level=52)
        data, ok, result = apply_soul_wars_review_pure(
            data, lambda: 0.9, productive=True
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["duty"], "control")
        self.assertEqual(result["control"], "player")

        data, ok, result = apply_soul_wars_review_pure(
            data, lambda: 0.9, productive=True
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["duty"], "fragments")
        self.assertEqual(result["gathered"], 2)
        self.assertEqual(result["fragment_source"], "jelly")
        self.assertEqual(result["offered"], 2)
        self.assertEqual(result["requirement_reduced"], 20)
        self.assertEqual(data["soul_wars"]["enemy_avatar_slayer"], 80)

    def test_low_slayer_uses_a_dropped_fragment_without_an_invented_gate(self):
        player, ok, info = set_soul_wars_policy_pure(
            _player(slayer_level=1),
            {"automation_mode": "advanced", "duty": "fragments"},
        )
        self.assertTrue(ok, info)
        data, ok, info = enter_soul_wars_pure(player)
        self.assertTrue(ok, info)
        data["soul_wars"]["control_balance"] = 3
        data, ok, result = apply_soul_wars_review_pure(
            data, lambda: 0.9, productive=True
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["gathered"], 1)
        self.assertEqual(result["fragment_source"], "dropped fragment")

    def test_defending_uses_the_source_half_chance_and_restores_prayer(self):
        player, ok, info = set_soul_wars_policy_pure(
            _player(combat_prayer_points=0),
            {"automation_mode": "advanced", "duty": "defend"},
        )
        self.assertTrue(ok, info)
        data, ok, info = enter_soul_wars_pure(player)
        self.assertTrue(ok, info)
        data["soul_wars"]["friendly_avatar_slayer"] = 50
        data, ok, result = apply_soul_wars_review_pure(
            data, lambda: 0.49, productive=True
        )
        self.assertTrue(ok, result)
        self.assertTrue(result["avatar_requirement_raised"])
        self.assertEqual(result["prayer_restored"], 10)
        # The opposing team offered its bounded fragment pressure first; the
        # successful bone then raised the resulting requirement by one.
        self.assertEqual(data["soul_wars"]["friendly_avatar_slayer"], 39)

    def test_again_advances_the_opposition_and_three_idle_beats_kick_for_zero_zeal(self):
        data = _entered(soul_wars_zeal=7)
        friendly_before = data["soul_wars"]["friendly_avatar_slayer"]
        for index in range(3):
            data, ok, result = apply_soul_wars_review_pure(
                data, lambda: 0.9, productive=False
            )
            self.assertTrue(ok, result)
            if index < 2:
                self.assertFalse(result["terminal"])
            if index == 0:
                self.assertLess(
                    data["soul_wars"]["friendly_avatar_slayer"], friendly_before
                )
        self.assertTrue(result["terminal"])
        self.assertTrue(result["kicked"])
        self.assertEqual(result["zeal"], 0)
        self.assertEqual(data["soul_wars_zeal"], 7)
        self.assertEqual(data["soul_wars"], {})


class SoulWarsAvatarTests(unittest.TestCase):
    def _avatar_ready(self, **overrides):
        player, ok, info = set_soul_wars_policy_pure(
            _player(**overrides),
            {"automation_mode": "advanced", "duty": "avatar"},
        )
        self.assertTrue(ok, info)
        data, ok, info = enter_soul_wars_pure(player)
        self.assertTrue(ok, info)
        data["soul_wars"].update(
            {"control_balance": 3, "enemy_avatar_slayer": data["slayer_level"]}
        )
        return data

    def test_avatar_duty_uses_one_live_six_tick_engaged_target_slice(self):
        data = self._avatar_ready()
        with patch("soul_wars_logic.apply_combat_burst_pure", _combat_stub()):
            updated, ok, result = apply_soul_wars_review_pure(
                data, lambda: 0.9, productive=True
            )
        self.assertTrue(ok, result)
        self.assertEqual(result["captured_ticks"], 6)
        self.assertTrue(result["captured_live"])
        self.assertTrue(result["captured_safe"])
        self.assertEqual(result["enemy"]["stats"]["hitpoints"], 10_000)
        self.assertEqual(
            updated["soul_wars"]["enemy_avatar_lifepoints"],
            SOUL_WARS_AVATAR_LIFEPOINTS - 500 - 1_250,
        )

    def test_inaccessible_advanced_avatar_duty_consumes_activity_not_a_fake_hit(self):
        player, ok, info = set_soul_wars_policy_pure(
            _player(slayer_level=40),
            {"automation_mode": "advanced", "duty": "avatar"},
        )
        self.assertTrue(ok, info)
        data, ok, info = enter_soul_wars_pure(player)
        self.assertTrue(ok, info)
        data, ok, result = apply_soul_wars_review_pure(
            data, lambda: 0.9, productive=True
        )
        self.assertTrue(ok, result)
        self.assertTrue(result["blocked"])
        self.assertEqual(data["soul_wars"]["activity"], 2)
        self.assertEqual(data["soul_wars"]["contribution"], 0)

    def test_safe_death_loses_temporary_fragments_and_restores_resources(self):
        data = self._avatar_ready(
            combat_lifepoints=10,
            combat_prayer_points=0,
            combat_special_attack_energy=0,
            summoning_state={"summoning_points_current": 0},
        )
        data["soul_wars"]["fragments"] = 7
        with patch(
            "soul_wars_logic.apply_combat_burst_pure", _combat_stub(died=True)
        ):
            updated, ok, result = apply_soul_wars_review_pure(
                data, lambda: 0.9, productive=True
            )
        self.assertTrue(ok, result)
        self.assertTrue(result["safe_death"])
        self.assertEqual(updated["soul_wars"]["fragments"], 0)
        self.assertEqual(updated["soul_wars"]["deaths"], 1)
        self.assertEqual(updated["combat_lifepoints"], 400)
        self.assertEqual(updated["combat_prayer_points"], 400)
        self.assertEqual(updated["combat_special_attack_energy"], 100)
        self.assertEqual(updated["summoning_state"]["summoning_points_current"], 40)


class SoulWarsTerminalAndRewardTests(unittest.TestCase):
    def _finish(self, player_score, opponent_score, *, zeal=0):
        data = _entered(soul_wars_zeal=zeal)
        data["soul_wars"].update(
            {
                "review": SOUL_WARS_EVENT_REVIEWS - 1,
                "player_score": player_score,
                "opponent_score": opponent_score,
                "control_balance": 3,
                "friendly_avatar_slayer": 100,
            }
        )
        return apply_soul_wars_review_pure(data, lambda: 0.9, productive=True)

    def test_match_pays_exact_win_draw_loss_zeal_and_caps_the_wallet(self):
        for scores, outcome, zeal in (
            ((1, 0), "win", 3),
            ((0, 0), "draw", 2),
            ((0, 1), "loss", 1),
        ):
            data, ok, result = self._finish(*scores)
            self.assertTrue(ok, result)
            self.assertEqual(result["outcome"], outcome)
            self.assertEqual(result["zeal"], zeal)
            self.assertEqual(data["soul_wars_zeal"], zeal)
            self.assertEqual(data["soul_wars"], {})
            self.assertEqual(data["current_combat_target"], "chicken")

        data, ok, result = self._finish(1, 0, zeal=SOUL_WARS_ZEAL_CAP - 1)
        self.assertTrue(ok, result)
        self.assertEqual(result["zeal"], 1)
        self.assertEqual(data["soul_wars_zeal"], SOUL_WARS_ZEAL_CAP)

    def test_leaving_forfeits_only_the_unfinished_match(self):
        data = _entered(soul_wars_zeal=12)
        data["soul_wars"]["fragments"] = 8
        left, ok, info = leave_soul_wars_pure(data)
        self.assertTrue(ok, info)
        self.assertEqual(left["soul_wars"], {})
        self.assertEqual(left["soul_wars_zeal"], 12)
        self.assertEqual(left["current_combat_target"], "chicken")

    def test_nonterminal_review_and_leave_commit_the_sanitized_zeal_cap(self):
        data = _entered()
        data["soul_wars_zeal"] = SOUL_WARS_ZEAL_CAP + 100
        reviewed, ok, result = apply_soul_wars_review_pure(
            data, lambda: 0.9, productive=False
        )
        self.assertTrue(ok, result)
        self.assertEqual(reviewed["soul_wars_zeal"], SOUL_WARS_ZEAL_CAP)

        reviewed["soul_wars_zeal"] = SOUL_WARS_ZEAL_CAP + 100
        left, ok, result = leave_soul_wars_pure(reviewed)
        self.assertTrue(ok, result)
        self.assertEqual(left["soul_wars_zeal"], SOUL_WARS_ZEAL_CAP)

    def test_shop_buys_exact_combat_band_charm_quantity(self):
        self.assertEqual(SOUL_WARS_CHARM_REWARDS_BY_ITEM["Gold charm"].zeal_cost, 4)
        with patch("soul_wars_logic.player_combat_level_pure", return_value=83):
            bought, ok, info = buy_soul_wars_charms_pure(
                _player(soul_wars_zeal=10), "Gold charm"
            )
        self.assertTrue(ok, info)
        self.assertEqual(bought["soul_wars_zeal"], 6)
        self.assertEqual(bought["inventory"]["Gold charm"], 24)

        with patch("soul_wars_logic.player_combat_level_pure", return_value=12):
            _same, ok, info = buy_soul_wars_charms_pure(
                _player(soul_wars_zeal=10), "Gold charm"
            )
        self.assertFalse(ok)
        self.assertIn("combat level 13", info["reason"])

    def test_view_exposes_match_state_and_hidden_xp_catalog_boundary(self):
        data = _entered(soul_wars_zeal=30)
        view = soul_wars_view_pure(data)
        self.assertTrue(view["active"])
        self.assertEqual(view["reviews_remaining"], SOUL_WARS_EVENT_REVIEWS)
        self.assertEqual({row["item"] for row in view["rewards"]}, {
            "Gold charm", "Green charm", "Crimson charm", "Blue charm"
        })
        self.assertNotIn("xp_rewards", view)


if __name__ == "__main__":
    unittest.main(verbosity=2)
