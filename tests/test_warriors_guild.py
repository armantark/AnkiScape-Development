import copy
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.combat_data import (
    COMBAT_ENEMY_DATA,
    CYCLOPS_WARRIORS_GUILD_DROPS,
    CYCLOSSUS_WARRIORS_GUILD_DROPS,
)
from ankiscape.core.constants import EQUIPMENT_DATA, ITEM_DEFINITIONS, ORE_DATA
from ankiscape.logic_pure.logic_pure import (
    combat_target_locked_reasons_pure,
    combat_target_preview_pure,
)
from ankiscape.runtime.runtime_actions import RuntimeActionContext, handle_combat_answer, handle_utility_answer
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.core.target_metadata import combat_target_rows
from ankiscape.data.warriors_guild_data import (
    ANIMATED_ARMOUR_TIERS,
    DEFENDER_TIERS,
    WARRIORS_GUILD_ACTIVITY_IDS,
    WARRIORS_GUILD_TOKEN_KEYS,
)
from ankiscape.logic.warriors_guild_logic import (
    apply_warriors_guild_activity_pure,
    apply_warriors_guild_cyclops_kills_pure,
    apply_warriors_guild_cyclossus_kills_pure,
    consume_warriors_guild_cyclops_tokens_pure,
    enter_warriors_guild_cyclops_room_pure,
    next_warriors_guild_defender_index_pure,
    set_warriors_guild_policy_pure,
    show_warriors_guild_defender_pure,
    warriors_guild_activity_locked_reasons_pure,
    warriors_guild_entry_locked_reasons_pure,
)


def _player():
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data.update(
        {
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "combat_lifepoints": 990,
            "current_combat_target": "cyclops",
            "combat_attack_style": "accurate",
            "combat_attack_style_type": "stab",
            "completed_achievements": [],
        }
    )
    return data


def _context(player_data, rolls=()):
    values = iter(rolls)
    calls = {"activity": [], "errors": [], "saves": 0}

    def random_random():
        try:
            return next(values)
        except StopIteration:
            return 0.5

    return RuntimeActionContext(
        player_data=player_data,
        random_random=random_random,
        show_error_message=lambda title, message: calls["errors"].append((title, message)),
        deactivate_current_skill=lambda: calls.setdefault("deactivated", True),
        award_skill_exp=lambda _key, amount: amount,
        award_hidden_skill_exp=lambda _exp, _level, _amount: None,
        level_up_check=lambda _skill, _data: None,
        check_achievements=lambda _data: None,
        save_player_data=lambda: calls.__setitem__("saves", calls["saves"] + 1),
        refresh_skill_availability=lambda: None,
        refresh_skill_availability_partial=lambda *_args: None,
        can_smith_any=lambda: False,
        show_exp=lambda _amount: None,
        show_activity_gain=lambda text: calls["activity"].append(text),
        implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda _before: None,
        cadence_live_enabled=True,
    ), calls


class WarriorsGuildPureTests(unittest.TestCase):
    def test_entry_requires_authentic_attack_strength_threshold(self):
        self.assertEqual(
            warriors_guild_entry_locked_reasons_pure(
                {"attack_level": 64, "strength_level": 65}
            ),
            ("Attack + Strength 130, or 99 in either skill",),
        )
        self.assertEqual(
            warriors_guild_entry_locked_reasons_pure(
                {"attack_level": 65, "strength_level": 65}
            ),
            (),
        )
        self.assertEqual(
            warriors_guild_entry_locked_reasons_pure(
                {"attack_level": 99, "strength_level": 1}
            ),
            (),
        )

    def test_casual_rotates_by_lowest_token_balance(self):
        player = _player()
        player["inventory"].update(
            {
                "Rune full helm": 1,
                "Rune platebody": 1,
                "Rune platelegs": 1,
            }
        )
        first, ok, first_result = apply_warriors_guild_activity_pure(
            player,
            "warriors_guild_keg_balance",
            (0.5, 0.5),
        )
        self.assertTrue(ok)
        self.assertEqual(first_result["activity_id"], "warriors_guild_animated_armour")
        self.assertEqual(first["warriors_guild"]["tokens"]["combat"], 80)

        second, ok, second_result = apply_warriors_guild_activity_pure(
            first,
            "warriors_guild_keg_balance",
            (0.5, 0.5),
        )
        self.assertTrue(ok)
        self.assertEqual(second_result["activity_id"], "warriors_guild_attack_dummy")
        self.assertEqual(second["warriors_guild"]["tokens"]["attack"], 5)

    def test_casual_falls_back_to_fastest_viable_single_route(self):
        player = _player()
        updated, ok, result = apply_warriors_guild_activity_pure(
            player,
            "warriors_guild_attack_dummy",
            (0.0, 0.5),
        )
        self.assertTrue(ok)
        self.assertEqual(result["activity_id"], "warriors_guild_shot_put")
        self.assertGreater(result["token_gain"], 0)
        self.assertEqual(updated["warriors_guild"]["tokens"]["strength"], result["token_gain"])

    def test_advanced_runs_exact_activity_and_exposes_real_equipment_locks(self):
        player, ok, _ = set_warriors_guild_policy_pure(
            _player(), automation_mode="advanced"
        )
        self.assertTrue(ok)
        player["equipment"] = {"weapon": "Rune scimitar"}
        self.assertEqual(
            warriors_guild_activity_locked_reasons_pure(
                player, "warriors_guild_shot_put"
            ),
            ("empty weapon, shield, and hands slots",),
        )
        unchanged, ok, result = apply_warriors_guild_activity_pure(
            player,
            "warriors_guild_shot_put",
            (0.0, 0.5),
        )
        self.assertFalse(ok)
        self.assertEqual(unchanged["warriors_guild"]["tokens"]["strength"], 0)
        self.assertIn("empty weapon", result["reason"])

    def test_animated_armour_uses_period_tokens_and_visible_loss_abstraction(self):
        self.assertEqual(
            tuple(
                (tier["name"], tier["lifepoints"], tier["tokens"])
                for tier in ANIMATED_ARMOUR_TIERS
            ),
            (
                ("Bronze", 100, 5),
                ("Iron", 200, 10),
                ("Steel", 400, 15),
                ("Black", 600, 40),
                ("Mithril", 800, 50),
                ("Adamant", 990, 60),
                ("Rune", 1200, 80),
            ),
        )
        player, ok, _ = set_warriors_guild_policy_pure(
            _player(), automation_mode="advanced"
        )
        self.assertTrue(ok)
        player["inventory"].update(
            {
                "Rune full helm": 1,
                "Rune platebody": 1,
                "Rune platelegs": 1,
            }
        )
        updated, ok, result = apply_warriors_guild_activity_pure(
            player,
            "warriors_guild_animated_armour",
            (0.0, 0.0),
        )
        self.assertTrue(ok)
        self.assertEqual(result["token_gain"], 80)
        self.assertEqual(result["armour_tier"], "Rune")
        self.assertEqual(result["lost_item"], "Rune full helm")
        self.assertEqual(updated["inventory"]["Rune full helm"], 0)
        self.assertEqual(result["xp_rewards"]["attack_exp"], 480.0)

    def test_single_and_multi_entry_and_tick_residuals_are_exact(self):
        multi, ok, _ = set_warriors_guild_policy_pure(
            _player(), automation_mode="advanced", payment_mode="multi"
        )
        self.assertTrue(ok)
        multi["warriors_guild"]["tokens"] = {
            key: 30 for key in WARRIORS_GUILD_TOKEN_KEYS
        }
        multi, ok, info = enter_warriors_guild_cyclops_room_pure(multi)
        self.assertTrue(ok)
        self.assertEqual(info["payment_mode"], "multi")
        multi, first = consume_warriors_guild_cyclops_tokens_pure(multi, 50)
        multi, second = consume_warriors_guild_cyclops_tokens_pure(multi, 50)
        self.assertEqual(first["drained"], {key: 1 for key in WARRIORS_GUILD_TOKEN_KEYS})
        self.assertEqual(second["drained"], {key: 2 for key in WARRIORS_GUILD_TOKEN_KEYS})
        self.assertEqual(set(multi["warriors_guild"]["tokens"].values()), {27})

        single, ok, _ = set_warriors_guild_policy_pure(
            _player(),
            automation_mode="advanced",
            payment_mode="single",
            single_token="attack",
        )
        self.assertTrue(ok)
        single["warriors_guild"]["tokens"]["attack"] = 200
        single, ok, _ = enter_warriors_guild_cyclops_room_pure(single)
        self.assertTrue(ok)
        single, drain = consume_warriors_guild_cyclops_tokens_pure(single, 50)
        self.assertEqual(drain["drained"], {"attack": 10})
        self.assertEqual(single["warriors_guild"]["tokens"]["attack"], 190)

    def test_cyclops_room_gate_and_melee_immunity_are_live(self):
        player = _player()
        self.assertEqual(
            combat_target_locked_reasons_pure(
                player, "cyclops", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA
            ),
            ("Enter the Warriors' Guild Cyclops room",),
        )
        player, ok, _ = set_warriors_guild_policy_pure(
            player, automation_mode="advanced", payment_mode="multi"
        )
        self.assertTrue(ok)
        player["warriors_guild"]["tokens"] = {
            key: 30 for key in WARRIORS_GUILD_TOKEN_KEYS
        }
        player, ok, _ = enter_warriors_guild_cyclops_room_pure(player)
        self.assertTrue(ok)
        player["equipment"] = {"weapon": "Staff"}
        player["combat_attack_style"] = "magic_standard"
        self.assertEqual(
            combat_target_locked_reasons_pure(
                player, "cyclops", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA
            ),
            ("Melee only inside the Warriors' Guild Cyclops room",),
        )

    def test_multi_payment_applies_the_labeled_damage_bonus(self):
        player, ok, _ = set_warriors_guild_policy_pure(
            _player(), automation_mode="advanced", payment_mode="multi"
        )
        self.assertTrue(ok)
        player["warriors_guild"]["tokens"] = {
            key: 30 for key in WARRIORS_GUILD_TOKEN_KEYS
        }
        player, ok, _ = enter_warriors_guild_cyclops_room_pure(player)
        self.assertTrue(ok)
        multi_hit = combat_target_preview_pure(
            player, "cyclops", COMBAT_ENEMY_DATA, EQUIPMENT_DATA
        )["player_max_hit"]
        player["warriors_guild"]["payment_mode"] = "single"
        single_hit = combat_target_preview_pure(
            player, "cyclops", COMBAT_ENEMY_DATA, EQUIPMENT_DATA
        )["player_max_hit"]
        self.assertGreater(multi_hit, single_hit)

    def test_defender_progression_requires_showing_and_recovers_from_best_owned(self):
        player, ok, _ = set_warriors_guild_policy_pure(
            _player(), automation_mode="advanced", payment_mode="multi"
        )
        self.assertTrue(ok)
        player["warriors_guild"]["tokens"] = {
            key: 30 for key in WARRIORS_GUILD_TOKEN_KEYS
        }
        player, ok, _ = enter_warriors_guild_cyclops_room_pure(player)
        self.assertTrue(ok)
        player, result = apply_warriors_guild_cyclops_kills_pure(
            player, 1, lambda: 0.0
        )
        self.assertEqual(result["drops"], {"Bronze defender": 1})
        self.assertEqual(next_warriors_guild_defender_index_pure(player), 0)
        player, ok, shown = show_warriors_guild_defender_pure(player)
        self.assertTrue(ok)
        self.assertEqual(shown["next_defender"], "Iron defender")
        player, result = apply_warriors_guild_cyclops_kills_pure(
            player, 1, lambda: 0.0
        )
        self.assertEqual(result["drops"], {"Iron defender": 1})

        player["warriors_guild"]["shown_defender_index"] = 6
        for tier in DEFENDER_TIERS:
            player["inventory"][tier["name"]] = 0
        player["inventory"]["Mithril defender"] = 1
        self.assertEqual(next_warriors_guild_defender_index_pure(player), 5)

    def test_cyclops_drop_table_and_defender_equipment_are_registered(self):
        self.assertEqual(CYCLOPS_WARRIORS_GUILD_DROPS["guaranteed"], (("Big bones", 1),))
        tertiary, cyclops_main = CYCLOPS_WARRIORS_GUILD_DROPS["tables"]
        self.assertEqual(tertiary["total"], 100000)
        self.assertEqual(cyclops_main["total"], 100000)
        self.assertEqual(
            sum(slot["slots"] for slot in cyclops_main["slots"]), 100000
        )
        self.assertEqual(cyclops_main["slots"][-1], {"slots": 41})
        self.assertEqual(COMBAT_ENEMY_DATA["cyclops"]["max_hit"], 64)
        self.assertEqual(COMBAT_ENEMY_DATA["cyclops"]["slayer_xp"], 75.0)
        self.assertEqual(CYCLOSSUS_WARRIORS_GUILD_DROPS["guaranteed"], (("Big bones", 1),))
        cyclossus_main, dragon_defender = CYCLOSSUS_WARRIORS_GUILD_DROPS["tables"]
        self.assertEqual(cyclossus_main["total"], 100000)
        self.assertEqual(
            sum(slot["slots"] for slot in cyclossus_main["slots"]), 100000
        )
        self.assertEqual(cyclossus_main["slots"][-1], {"slots": 10610})
        self.assertEqual(
            dragon_defender["name"],
            "Period-common abstraction: Dragon defender",
        )
        self.assertEqual(COMBAT_ENEMY_DATA["cyclossus"]["stats"]["hitpoints"], 3280)
        self.assertEqual(COMBAT_ENEMY_DATA["cyclossus"]["max_hit"], 94)
        self.assertEqual(COMBAT_ENEMY_DATA["cyclossus"]["slayer_xp"], 350.0)
        self.assertEqual(EQUIPMENT_DATA["Dragon defender"].slot, "shield")
        self.assertEqual(EQUIPMENT_DATA["Dragon defender"].bonuses.melee_strength, 6)
        self.assertEqual(
            EQUIPMENT_DATA["Dragon defender"].skill_requirements,
            (("attack", 60), ("defense", 60)),
        )
        self.assertEqual(EQUIPMENT_DATA["Cyclopean helmet"].slot, "head")
        self.assertEqual(EQUIPMENT_DATA["Cyclopean helmet"].bonuses.melee_strength, 0)

    def test_cyclossus_spawn_is_progression_gated_and_requires_a_high_defender(self):
        player, ok, _ = set_warriors_guild_policy_pure(
            _player(), automation_mode="advanced", payment_mode="multi"
        )
        self.assertTrue(ok)
        player["warriors_guild"]["tokens"] = {
            key: 30 for key in WARRIORS_GUILD_TOKEN_KEYS
        }
        player, ok, _ = enter_warriors_guild_cyclops_room_pure(player)
        self.assertTrue(ok)
        player["warriors_guild"]["shown_defender_index"] = 6
        player, result = apply_warriors_guild_cyclops_kills_pure(
            player, 1, iter((0.5, 0.0)).__next__
        )
        self.assertTrue(result["cyclossus_spawned"])
        self.assertEqual(
            combat_target_locked_reasons_pure(
                player, "cyclossus", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA
            ),
            ("Equip a Rune or Dragon defender",),
        )
        player["equipment"] = {"shield": "Rune defender"}
        self.assertEqual(
            combat_target_locked_reasons_pure(
                player, "cyclossus", COMBAT_ENEMY_DATA, equipment_data=EQUIPMENT_DATA
            ),
            (),
        )
        player, cleared = apply_warriors_guild_cyclossus_kills_pure(player, 1)
        self.assertTrue(cleared["cleared"])
        self.assertFalse(player["warriors_guild"]["cyclossus_pending"])
        self.assertEqual(player["warriors_guild"]["cyclossus_kills"], 1)

    def test_cyclossus_combat_row_appears_only_for_the_live_spawn(self):
        player = _player()
        rows = combat_target_rows(
            player,
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_DATA,
            "chicken",
        )
        self.assertNotIn("cyclossus", {row.target_id for row in rows})
        player["warriors_guild"]["cyclossus_pending"] = True
        player["warriors_guild"]["in_cyclops_room"] = True
        player["warriors_guild"]["tokens"] = {
            key: 30 for key in WARRIORS_GUILD_TOKEN_KEYS
        }
        player["equipment"] = {"shield": "Rune defender"}
        rows = combat_target_rows(
            player,
            COMBAT_ENEMY_DATA,
            {},
            EQUIPMENT_DATA,
            "chicken",
        )
        cyclossus = next(row for row in rows if row.target_id == "cyclossus")
        self.assertTrue(cyclossus.enabled)

    def test_token_depletion_cannot_leave_a_stranded_cyclossus_spawn(self):
        player, ok, _ = set_warriors_guild_policy_pure(
            _player(), automation_mode="advanced", payment_mode="multi"
        )
        self.assertTrue(ok)
        player["warriors_guild"]["tokens"] = {
            key: 30 for key in WARRIORS_GUILD_TOKEN_KEYS
        }
        player, ok, _ = enter_warriors_guild_cyclops_room_pure(player)
        self.assertTrue(ok)
        player["warriors_guild"]["shown_defender_index"] = 6
        player["warriors_guild"]["tokens"] = {
            key: 1 for key in WARRIORS_GUILD_TOKEN_KEYS
        }
        player, drain = consume_warriors_guild_cyclops_tokens_pure(player, 50)
        self.assertTrue(drain["ejected"])
        player, result = apply_warriors_guild_cyclops_kills_pure(
            player, 1, iter((0.5, 0.0)).__next__
        )
        self.assertFalse(result["cyclossus_spawned"])
        self.assertFalse(player["warriors_guild"]["cyclossus_pending"])

    def test_storage_migration_seeds_and_sanitizes_guild_state(self):
        migrated = migrate_loaded_data(
            {
                "warriors_guild": {
                    "tokens": {"attack": -5, "combat": 999999},
                    "payment_mode": "nonsense",
                }
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["warriors_guild"]["tokens"]["attack"], 0)
        self.assertEqual(migrated["warriors_guild"]["tokens"]["combat"], 65535)
        self.assertEqual(migrated["warriors_guild"]["payment_mode"], "multi")
        self.assertEqual(
            set(migrated["warriors_guild"]["activity_reviews"]),
            set(WARRIORS_GUILD_ACTIVITY_IDS),
        )


class WarriorsGuildRuntimeTests(unittest.TestCase):
    def test_utility_handler_awards_tokens_xp_and_persists(self):
        player = _player()
        player["current_utility"] = "warriors_guild_attack_dummy"
        player, ok, _ = set_warriors_guild_policy_pure(
            player, automation_mode="advanced"
        )
        self.assertTrue(ok)
        ctx, calls = _context(player, (0.5, 0.5))
        self.assertTrue(handle_utility_answer(ctx))
        self.assertEqual(player["warriors_guild"]["tokens"]["attack"], 5)
        self.assertEqual(player["attack_exp"], 15.0)
        self.assertEqual(calls["saves"], 1)
        self.assertIn("+5 attack tokens", calls["activity"][0])

    def test_combat_handler_drains_tokens_and_merges_progressive_defender_drop(self):
        player, ok, _ = set_warriors_guild_policy_pure(
            _player(), automation_mode="advanced", payment_mode="multi"
        )
        self.assertTrue(ok)
        player["warriors_guild"]["tokens"] = {
            key: 30 for key in WARRIORS_GUILD_TOKEN_KEYS
        }
        player, ok, _ = enter_warriors_guild_cyclops_room_pure(player)
        self.assertTrue(ok)
        player["loot_overrides"] = {"Big bones": "keep"}
        ctx, calls = _context(player, (0.0,))

        result = {
            "reason": "combat_burst",
            "target_id": "cyclops",
            "display_name": "Cyclops",
            "ticks_elapsed": 50,
            "ticks": 50,
            "player_damage": 750,
            "enemy_damage": 0,
            "enemy_healing": 0,
            "enemy_lifepoints": 0,
            "player_lifepoints": 990,
            "killed": True,
            "kills": 1,
            "died": False,
            "fled": False,
            "drops": {"Big bones": 1},
            "xp_rewards": {"attack_exp": 300.0, "constitution_exp": 99.75},
        }
        burst_state = copy.deepcopy(player)
        burst_state["inventory"]["Big bones"] = 1
        burst_state["attack_exp"] += 300.0
        burst_state["constitution_exp"] += 99.75

        with patch(
            "ankiscape.runtime.runtime_actions_combat.apply_combat_burst_pure",
            return_value=(burst_state, True, result),
        ):
            self.assertTrue(handle_combat_answer(ctx))

        self.assertEqual(player["warriors_guild"]["tokens"]["attack"], 29)
        self.assertEqual(player["inventory"]["Bronze defender"], 1)
        self.assertEqual(player["inventory"]["Big bones"], 2)
        self.assertIn("Bronze defender", calls["activity"][0])

    def test_cyclops_kill_switches_to_a_spawned_cyclossus(self):
        player, ok, _ = set_warriors_guild_policy_pure(
            _player(), automation_mode="advanced", payment_mode="multi"
        )
        self.assertTrue(ok)
        player["warriors_guild"]["tokens"] = {
            key: 30 for key in WARRIORS_GUILD_TOKEN_KEYS
        }
        player, ok, _ = enter_warriors_guild_cyclops_room_pure(player)
        self.assertTrue(ok)
        player["warriors_guild"]["shown_defender_index"] = 6
        player["equipment"] = {"shield": "Rune defender"}
        ctx, calls = _context(player, (0.5, 0.0))
        result = {
            "reason": "combat_burst",
            "target_id": "cyclops",
            "display_name": "Cyclops",
            "ticks_elapsed": 6,
            "ticks": 6,
            "player_damage": 750,
            "enemy_damage": 0,
            "enemy_healing": 0,
            "enemy_lifepoints": 0,
            "player_lifepoints": 990,
            "killed": True,
            "kills": 1,
            "died": False,
            "fled": False,
            "drops": {},
            "xp_rewards": {},
        }
        with patch(
            "ankiscape.runtime.runtime_actions_combat.apply_combat_burst_pure",
            return_value=(copy.deepcopy(player), True, result),
        ):
            self.assertTrue(handle_combat_answer(ctx))
        self.assertEqual(player["current_combat_target"], "cyclossus")
        self.assertTrue(player["warriors_guild"]["cyclossus_pending"])
        self.assertIn("Cyclossus appeared", calls["activity"][0])


if __name__ == "__main__":
    unittest.main()
