from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.castle_wars_data import (
    CASTLE_WARS_BALLISTA_PARTS,
    CASTLE_WARS_MATCH_REVIEWS,
    castle_wars_equipment_data_as_dict,
    castle_wars_extra_items_as_dict,
)
from ankiscape.logic.castle_wars_logic import (
    apply_castle_wars_review_pure,
    buy_castle_wars_reward_pure,
    castle_wars_damage_multiplier_pure,
    castle_wars_view_pure,
    deploy_castle_wars_ballista_pure,
    deploy_castle_wars_chinchompa_pure,
    enter_castle_wars_pure,
    leave_castle_wars_pure,
    sanitize_castle_wars_state_pure,
    sell_castle_wars_reward_pure,
    set_castle_wars_policy_pure,
)
from ankiscape.logic_pure.logic_pure import apply_combat_burst_pure


def _player(**overrides):
    player = {
        "attack_level": 50,
        "strength_level": 50,
        "defense_level": 50,
        "constitution_level": 50,
        "ranged_level": 50,
        "magic_level": 50,
        "prayer_level": 50,
        "summoning_level": 1,
        "activity_session": {"active_id": ""},
        "combat_encounter": {},
        "current_combat_target": "chicken",
        "combat_lifepoints": 500,
        "combat_status_effects": {},
        "combat_supply_loadout": {},
        "inventory": {},
        "equipment": {},
    }
    player.update(overrides)
    return player


def _entered(**overrides):
    data, ok, info = enter_castle_wars_pure(_player(**overrides))
    assert ok, info
    return data


def _combat_stub(damage: int = 0, *, died: bool = False, killed: bool = False):
    def _apply(data, _enemies, _equipment, **_kwargs):
        updated = copy.deepcopy(data)
        enemy_lp = 0 if killed else max(1, 500 - damage)
        updated["combat_encounter"] = {
            "target_id": "castle_wars_raider",
            "enemy_lifepoints": enemy_lp,
        }
        return updated, True, {
            "player_damage": damage,
            "enemy_lifepoints": enemy_lp,
            "killed": killed,
            "died": died,
            "safe_death": died,
            "xp_rewards": {"attack_exp": damage * 0.4} if damage else {},
        }

    return _apply


class CastleWarsDataTests(unittest.TestCase):
    def test_representative_reward_items_and_equipment_are_period_identified(self):
        items = castle_wars_extra_items_as_dict()
        self.assertEqual(items["Castle wars ticket"]["source_item_id"], 4067)
        self.assertTrue(items["Castle wars ticket"]["stackable"])
        self.assertEqual(items["Saradomin halo"]["source_item_id"], 18745)
        equipment = castle_wars_equipment_data_as_dict()
        self.assertEqual(equipment["Basic decorative platebody"].slot, "body")
        self.assertEqual(equipment["Saradomin halo"].bonuses.defence_magic, 11)


class CastleWarsEntryTests(unittest.TestCase):
    def test_entry_has_no_level_gate_and_preserves_previous_combat_target(self):
        data, ok, info = enter_castle_wars_pure(
            _player(
                attack_level=1,
                strength_level=1,
                defense_level=1,
                constitution_level=10,
                ranged_level=1,
                magic_level=1,
                prayer_level=1,
            )
        )
        self.assertTrue(ok, info)
        self.assertEqual(data["activity_session"], {"active_id": "castle_wars"})
        self.assertEqual(data["castle_wars"]["previous_combat_target"], "chicken")
        self.assertEqual(data["castle_wars"]["review"], 0)

    def test_entry_enforces_activity_combat_equipment_and_food_boundaries(self):
        cases = (
            (_player(activity_session={"active_id": "barrows"}), "persistent activity"),
            (
                _player(combat_encounter={"target_id": "chicken", "enemy_lifepoints": 10}),
                "Combat encounter",
            ),
            (_player(equipment={"head": "Bronze full helm"}), "helmets and capes"),
            (_player(equipment={"head": "Saradomin halo"}), "helmets and capes"),
            (
                _player(equipment={"cape": "Castle wars hobbyist cape"}),
                "helmets and capes",
            ),
            (
                _player(combat_supply_loadout={"food": {"Lobster": 2}}),
                "carried food",
            ),
        )
        for player, reason in cases:
            with self.subTest(reason=reason):
                _same, ok, info = enter_castle_wars_pure(player)
                self.assertFalse(ok)
                self.assertIn(reason, info["reason"])

    def test_policy_is_fixed_for_the_match_and_malformed_state_is_bounded(self):
        player, ok, info = set_castle_wars_policy_pure(
            _player(),
            {"automation_mode": "advanced", "duty": "support", "team": "zamorak"},
        )
        self.assertTrue(ok, info)
        entered, ok, info = enter_castle_wars_pure(player)
        self.assertTrue(ok, info)
        self.assertEqual(
            (
                entered["castle_wars"]["automation_mode"],
                entered["castle_wars"]["duty"],
                entered["castle_wars"]["team"],
            ),
            ("advanced", "support", "zamorak"),
        )
        _same, ok, info = set_castle_wars_policy_pure(entered, {"duty": "capture"})
        self.assertFalse(ok)
        self.assertIn("current match", info["reason"])

        malformed = sanitize_castle_wars_state_pure(
            _player(
                castle_wars={"review": 999, "barricades": 999, "gate_integrity": -2},
                activity_session={"active_id": "castle_wars"},
            )
        )
        self.assertEqual(malformed["castle_wars"]["review"], 9)
        self.assertEqual(malformed["castle_wars"]["barricades"], 10)
        self.assertEqual(malformed["castle_wars"]["gate_integrity"], 0)


class CastleWarsMatchTests(unittest.TestCase):
    def test_combat_kernel_applies_the_activity_damage_multiplier_to_real_damage(self):
        player = _player(current_combat_target="target")
        enemy = {
            "target": {
                "display_name": "Target",
                "stats": {
                    "attack": 1,
                    "strength": 1,
                    "defence": 1,
                    "magic": 1,
                    "ranged": 1,
                    "hitpoints": 500,
                },
                "bonuses": {},
                "attack_style": "melee",
                "attack_speed": 4,
                "max_hit": 0,
                "drops": {"guaranteed": (), "tables": ()},
            }
        }
        for multiplier, expected_damage in ((1.0, 59), (1.10, 64)):
            rolls = iter((0.0, 0.999999))
            updated, ok, result = apply_combat_burst_pure(
                player,
                enemy,
                {},
                ticks=1,
                rng=lambda: next(rolls),
                live_cadence=True,
                stop_after_first_kill=True,
                safe_death=True,
                allow_bank_run=False,
                player_damage_multiplier=multiplier,
            )
            with self.subTest(multiplier=multiplier):
                self.assertTrue(ok, result)
                self.assertEqual(result["player_damage"], expected_damage)
                self.assertEqual(
                    updated["combat_encounter"]["enemy_lifepoints"],
                    500 - expected_damage,
                )

    def test_again_advances_the_crowd_without_personal_contribution(self):
        updated, ok, result = apply_castle_wars_review_pure(
            _entered(),
            lambda: 0.5,
            productive=False,
            opponent_roll=0.5,
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["duty"], "idle")
        self.assertEqual(updated["castle_wars"]["contribution"], 0)
        self.assertEqual(updated["castle_wars"]["review"], 1)
        self.assertLess(updated["castle_wars"]["gate_integrity"], 100)

    def test_capture_duty_and_terminal_settlement_pay_exact_ticket_rows(self):
        data = _entered()
        for _ in range(CASTLE_WARS_MATCH_REVIEWS):
            data, ok, result = apply_castle_wars_review_pure(
                data,
                lambda: 0.5,
                productive=True,
                duty="capture",
                opponent_roll=0.5,
            )
            self.assertTrue(ok, result)
        self.assertTrue(result["terminal"])
        self.assertEqual(result["result"], "win")
        self.assertEqual(result["tickets"], 2)
        self.assertEqual(data["castle_wars_tickets"], 2)
        self.assertEqual(data["castle_wars_games_played"], 1)
        self.assertEqual(data["castle_wars"], {})
        self.assertEqual(data["current_combat_target"], "chicken")

        draw = _entered()
        for _ in range(CASTLE_WARS_MATCH_REVIEWS):
            draw, ok, result = apply_castle_wars_review_pure(
                draw,
                lambda: 0.5,
                productive=False,
                opponent_roll=0.5,
            )
        self.assertEqual(result["result"], "draw")
        self.assertEqual(result["tickets"], 1)

    def test_defend_uses_live_safe_combat_and_decorative_damage_multiplier(self):
        data = _entered(
            equipment={
                "body": "Basic decorative platebody",
                "legs": "Basic decorative platelegs",
                "shield": "Basic decorative shield",
            }
        )
        captured = {}

        def fake(data, enemies, equipment, **kwargs):
            captured.update(kwargs)
            self.assertIn("castle_wars_raider", enemies)
            return _combat_stub(100, killed=True)(data, enemies, equipment, **kwargs)

        with patch("ankiscape.logic.castle_wars_logic.apply_combat_burst_pure", fake):
            updated, ok, result = apply_castle_wars_review_pure(
                data,
                lambda: 0.5,
                productive=True,
                duty="defend",
            )
        self.assertTrue(ok, result)
        self.assertEqual(captured["ticks"], 6)
        self.assertTrue(captured["live_cadence"])
        self.assertTrue(captured["safe_death"])
        self.assertFalse(captured["allow_bank_run"])
        self.assertEqual(captured["player_damage_multiplier"], 1.10)
        self.assertEqual(updated["castle_wars"]["kills"], 1)
        self.assertEqual(result["xp_rewards"], {"attack_exp": 40.0})

    def test_safe_death_respawns_inside_the_same_match_without_item_loss(self):
        data = _entered(inventory={"Coins": 50})
        data["combat_lifepoints"] = 1
        with patch(
            "ankiscape.logic.castle_wars_logic.apply_combat_burst_pure",
            _combat_stub(0, died=True),
        ):
            updated, ok, result = apply_castle_wars_review_pure(
                data,
                lambda: 0.5,
                productive=True,
                duty="defend",
            )
        self.assertTrue(ok, result)
        self.assertTrue(result["died"])
        self.assertEqual(updated["castle_wars"]["deaths"], 1)
        self.assertEqual(updated["combat_lifepoints"], 500)
        self.assertEqual(updated["inventory"]["Coins"], 50)
        self.assertTrue(updated["castle_wars"])

    def test_support_heals_cures_poison_and_restores_run_credit(self):
        data = _entered(
            combat_lifepoints=300,
            combat_status_effects={"poison": {"ticks_left": 20}},
            agility_run_energy_credit_pct=80,
        )
        updated, ok, result = apply_castle_wars_review_pure(
            data,
            lambda: 0.5,
            productive=True,
            duty="support",
        )
        self.assertTrue(ok, result)
        self.assertEqual(updated["combat_lifepoints"], 350)
        self.assertNotIn("poison", updated["combat_status_effects"])
        self.assertEqual(updated["agility_run_energy_credit_pct"], 100)

    def test_support_reinforces_the_bottleneck_when_no_bandage_effect_is_needed(self):
        data = _entered(
            combat_lifepoints=500,
            combat_status_effects={},
            agility_run_energy_credit_pct=100,
        )
        updated, ok, result = apply_castle_wars_review_pure(
            data,
            lambda: 0.5,
            productive=True,
            duty="support",
        )
        self.assertTrue(ok, result)
        self.assertEqual(updated["castle_wars"]["barricades"], 1)
        self.assertIn("Deployed 2 barricades", result["detail"])

    def test_leave_forfeits_the_unfinished_match(self):
        left, ok, info = leave_castle_wars_pure(_entered(castle_wars_tickets=7))
        self.assertTrue(ok, info)
        self.assertEqual(left["castle_wars_tickets"], 7)
        self.assertEqual(left["castle_wars"], {})
        self.assertEqual(left["current_combat_target"], "chicken")


class CastleWarsRewardTests(unittest.TestCase):
    def test_halo_reduces_only_its_period_listed_prayer_drain_by_one_third(self):
        enemy = {
            "target": {
                "display_name": "Target",
                "stats": {
                    "attack": 1,
                    "strength": 1,
                    "defence": 1,
                    "magic": 1,
                    "ranged": 1,
                    "hitpoints": 500,
                },
                "bonuses": {},
                "attack_style": "melee",
                "attack_speed": 4,
                "max_hit": 0,
                "drops": {"guaranteed": (), "tables": ()},
            }
        }
        base = _player(
            current_combat_target="target",
            combat_prayer_book="standard",
            combat_prayers_enabled=True,
            combat_selected_prayers=["burst_of_strength"],
            combat_prayer_uptime="100",
            combat_prayer_points=500,
            combat_prayer_drain_counter=0.0,
        )
        ordinary, ok, result = apply_combat_burst_pure(
            base,
            enemy,
            castle_wars_equipment_data_as_dict(),
            ticks=6,
            rng=lambda: 0.0,
            live_cadence=True,
            safe_death=True,
            allow_bank_run=False,
        )
        self.assertTrue(ok, result)
        halo_player = copy.deepcopy(base)
        halo_player["equipment"] = {"head": "Saradomin halo"}
        halo, ok, result = apply_combat_burst_pure(
            halo_player,
            enemy,
            castle_wars_equipment_data_as_dict(),
            ticks=6,
            rng=lambda: 0.0,
            live_cadence=True,
            safe_death=True,
            allow_bank_run=False,
        )
        self.assertTrue(ok, result)
        ordinary_progress = (
            (500 - ordinary["combat_prayer_points"]) * 60
            + ordinary["combat_prayer_drain_counter"]
        )
        halo_progress = (
            (500 - halo["combat_prayer_points"]) * 60
            + halo["combat_prayer_drain_counter"]
        )
        self.assertAlmostEqual(halo_progress, ordinary_progress * 2.0 / 3.0)

    def test_damage_set_has_exact_one_two_three_piece_steps(self):
        self.assertEqual(castle_wars_damage_multiplier_pure(_player()), 1.0)
        self.assertEqual(
            castle_wars_damage_multiplier_pure(
                _player(equipment={"body": "Basic decorative platebody"})
            ),
            1.04,
        )
        self.assertEqual(
            castle_wars_damage_multiplier_pure(
                _player(
                    equipment={
                        "body": "Basic decorative platebody",
                        "legs": "Basic decorative platelegs",
                    }
                )
            ),
            1.06,
        )

    def test_shop_buys_and_resells_full_bundles_at_full_ticket_value(self):
        bought, ok, info = buy_castle_wars_reward_pure(
            _player(castle_wars_tickets=10), "chinchompas"
        )
        self.assertTrue(ok, info)
        self.assertEqual(bought["inventory"]["Castlewars chinchompa"], 3)
        self.assertEqual(bought["castle_wars_tickets"], 9)
        sold, ok, info = sell_castle_wars_reward_pure(bought, "chinchompas")
        self.assertTrue(ok, info)
        self.assertEqual(sold["inventory"]["Castlewars chinchompa"], 0)
        self.assertEqual(sold["castle_wars_tickets"], 10)

    def test_hobbyist_cape_gate_and_view_are_derived_from_credited_games(self):
        _same, ok, info = buy_castle_wars_reward_pure(
            _player(castle_wars_tickets=2, castle_wars_games_played=499),
            "hobbyist_cape",
        )
        self.assertFalse(ok)
        self.assertIn("500", info["reason"])
        eligible = _player(castle_wars_tickets=2, castle_wars_games_played=500)
        bought, ok, info = buy_castle_wars_reward_pure(eligible, "hobbyist_cape")
        self.assertTrue(ok, info)
        self.assertEqual(bought["inventory"]["Castle wars hobbyist cape"], 1)
        view = castle_wars_view_pure(eligible)
        row = next(row for row in view["rewards"] if row["reward_id"] == "hobbyist_cape")
        self.assertTrue(row["can_buy"])

    def test_ballista_parts_are_reusable_but_ammo_and_chinchompas_are_consumed(self):
        inventory = {item: 1 for item in CASTLE_WARS_BALLISTA_PARTS}
        inventory.update({"Ballista ammo": 2, "Castlewars chinchompa": 1})
        data = _entered(inventory=inventory)
        data, ok, info = deploy_castle_wars_ballista_pure(data)
        self.assertTrue(ok, info)
        self.assertTrue(data["castle_wars"]["ballista_deployed"])
        self.assertTrue(all(data["inventory"][item] == 1 for item in CASTLE_WARS_BALLISTA_PARTS))

        data, ok, result = apply_castle_wars_review_pure(
            data,
            lambda: 0.5,
            productive=True,
            duty="catapult",
        )
        self.assertTrue(ok, result)
        self.assertEqual(data["inventory"]["Ballista ammo"], 1)
        data, ok, info = deploy_castle_wars_chinchompa_pure(data)
        self.assertTrue(ok, info)
        self.assertEqual(data["inventory"]["Castlewars chinchompa"], 0)


if __name__ == "__main__":
    unittest.main()
