from __future__ import annotations

import copy
import unittest
from pathlib import Path
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import (
    EQUIPMENT_DATA,
    ITEM_DEFINITIONS,
    ORE_DATA,
    UTILITY_ACTIVITY_DATA,
)
from ankiscape.data.fight_caves_data import (
    FIGHT_CAVES_COMPLETION_TOKKUL,
    FIGHT_CAVES_ENEMY_DATA,
    FIGHT_CAVES_WAVES,
)
from ankiscape.logic.fight_caves_logic import (
    apply_fight_caves_command_pure,
    apply_fight_caves_review_pure,
    default_fight_caves_state_pure,
    fight_caves_partial_tokkul_pure,
    fight_caves_view_pure,
    sanitize_fight_caves_state_pure,
)
from ankiscape.runtime.runtime_actions import RuntimeActionContext, handle_utility_answer
from ankiscape.core.storage_pure import CURRENT_CONFIG_VERSION, default_player_data, migrate_loaded_data


def _player(**overrides):
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data.update(
        {
            "attack_level": 80,
            "strength_level": 80,
            "defense_level": 80,
            "ranged_level": 80,
            "magic_level": 80,
            "prayer_level": 80,
            "constitution_level": 80,
            "combat_lifepoints": 800,
            "combat_prayer_points": 800,
            "combat_auto_eat_food": [],
            "combat_auto_flee_percent": 0,
            "inventory": {"Shark": 4},
            "equipment": {"cape": "Fire cape"},
            "current_combat_target": "chicken",
        }
    )
    data.update(overrides)
    return data


def _entered(**overrides):
    data, ok, info = apply_fight_caves_command_pure(_player(**overrides), "enter")
    assert ok, info
    return data


def _combat_result(*, killed=False, died=False, lifepoints=None):
    def _apply(data, _enemies, _equipment, **_kwargs):
        updated = copy.deepcopy(data)
        before = int(updated["combat_encounter"]["enemy_lifepoints"])
        after = 0 if killed else int(lifepoints if lifepoints is not None else before)
        updated["combat_encounter"]["enemy_lifepoints"] = max(0, after)
        if died:
            updated["combat_lifepoints"] = updated["constitution_level"] * 10
            updated["combat_encounter"] = {}
        return updated, True, {
            "killed": killed,
            "died": died,
            "enemy_lifepoints": after,
            "xp_rewards": {"attack_exp": 4.0} if killed else {},
            "enemy_prayer_drain": 0,
            "safe_death": died,
        }

    return _apply


class FightCavesDataTests(unittest.TestCase):
    def test_period_wave_table_and_rewards_are_registered(self):
        self.assertEqual(len(FIGHT_CAVES_WAVES), 63)
        self.assertEqual(sum(map(len, FIGHT_CAVES_WAVES)), 192)
        self.assertEqual(FIGHT_CAVES_WAVES[0], ("tz_kih",))
        self.assertEqual(FIGHT_CAVES_WAVES[62], ("tztok_jad",))
        self.assertEqual(FIGHT_CAVES_ENEMY_DATA["tztok_jad"]["stats"]["hitpoints"], 2550)
        self.assertEqual(FIGHT_CAVES_ENEMY_DATA["yt_mejkot"]["max_hit"], 280)
        self.assertEqual(FIGHT_CAVES_ENEMY_DATA["yt_hurkot"]["priority"], 0)

        activity = UTILITY_ACTIVITY_DATA["fight_caves"]
        self.assertEqual(activity["group"], "minigames")
        self.assertEqual(activity["outputs"], ("Tokkul", "Fire cape"))
        self.assertTrue(Path(activity["icon_path"]).is_file())
        items = {definition.storage_key: definition for definition in ITEM_DEFINITIONS}
        self.assertEqual(items["Fire cape"].source_item_id, 6570)
        self.assertFalse(items["Fire cape"].tradeable)
        self.assertEqual(items["Tokkul"].source_item_id, 6529)
        self.assertTrue(items["Tokkul"].stackable)
        self.assertEqual(EQUIPMENT_DATA["Fire cape"].bonuses.prayer, 2)

    def test_partial_reward_uses_the_period_controller_formula(self):
        self.assertEqual(fight_caves_partial_tokkul_pure(1), 0)
        self.assertEqual(fight_caves_partial_tokkul_pure(32), 4_079)
        self.assertEqual(fight_caves_partial_tokkul_pure(63), 8_032)


class FightCavesStateAndCommandTests(unittest.TestCase):
    def test_entry_is_persistent_and_leave_is_explicit(self):
        original = _player()
        entered, ok, info = apply_fight_caves_command_pure(original, "enter")
        self.assertTrue(ok, info)
        self.assertFalse(original.get("fight_caves", {}).get("active", False))
        self.assertTrue(entered["fight_caves"]["active"])
        self.assertEqual(entered["activity_session"], {"active_id": "fight_caves"})
        self.assertEqual(entered["fight_caves"]["previous_combat_target"], "chicken")

        entered["fight_caves"]["wave"] = 32
        resumed, ok, _ = apply_fight_caves_command_pure(entered, "enter")
        self.assertTrue(ok)
        self.assertEqual(resumed["fight_caves"]["wave"], 32)
        left, ok, info = apply_fight_caves_command_pure(resumed, "leave")
        self.assertTrue(ok, info)
        self.assertFalse(left["fight_caves"]["active"])
        self.assertEqual(left["inventory"]["Tokkul"], 4_079)
        self.assertEqual(left["current_combat_target"], "chicken")

    def test_follower_and_competing_session_require_safe_resolution(self):
        data = _player(activity_session={"active_id": "fist_of_guthix"})
        _blocked, ok, info = apply_fight_caves_command_pure(data, "enter")
        self.assertFalse(ok)
        self.assertIn("persistent activity", info["reason"])

        data = _player()
        data["summoning_state"]["active_follower"] = {
            "kind": "familiar",
            "entity_id": "spiritwolf",
            "remaining_reviews": 3,
            "max_reviews": 3,
            "storage": {},
        }
        unchanged, ok, info = apply_fight_caves_command_pure(data, "enter")
        self.assertFalse(ok)
        self.assertTrue(info["requires_confirmation"])
        self.assertTrue(unchanged["summoning_state"]["active_follower"])
        entered, ok, info = apply_fight_caves_command_pure(
            data, "enter", {"confirm_dismiss_follower": True}
        )
        self.assertTrue(ok, info)
        self.assertEqual(entered["summoning_state"]["active_follower"], {})

    def test_advanced_mode_preserves_explicit_target(self):
        data = _entered()
        state = data["fight_caves"]
        state["wave"] = 8
        state["roster"] = []
        state["engaged_instance_id"] = ""
        view = fight_caves_view_pure(data)
        target = view["roster_view"][1]["instance_id"]
        self.assertEqual(
            [member["enemy_id"] for member in view["roster_view"] if member["engaged"]],
            ["tz_kih"],
        )
        data["fight_caves"] = view
        data, ok, _ = apply_fight_caves_command_pure(
            data, "set_mode", {"automation_mode": "advanced"}
        )
        self.assertTrue(ok)
        data, ok, _ = apply_fight_caves_command_pure(
            data, "select_target", {"instance_id": target}
        )
        self.assertTrue(ok)
        self.assertEqual(data["fight_caves"]["engaged_instance_id"], target)

    def test_migration_repairs_active_session_and_rejects_hidden_timer_state(self):
        raw = {
            "active": True,
            "wave": 1,
            "timer": 900,
            "roster": [
                {
                    "instance_id": "one",
                    "enemy_id": "tz_kih",
                    "lifepoints": 50,
                }
            ],
        }
        sanitized = sanitize_fight_caves_state_pure(raw)
        self.assertNotIn("timer", sanitized)
        self.assertEqual(sanitized["roster"][0]["lifepoints"], 50)
        migrated = migrate_loaded_data({"fight_caves": raw}, {}, ())
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["activity_session"], {"active_id": "fight_caves"})


class FightCavesMechanicsTests(unittest.TestCase):
    def test_review_persists_damage_and_tz_kih_drains_prayer_on_later_attacks(self):
        data = _entered(
            attack_level=1,
            strength_level=1,
            defense_level=1,
            constitution_level=99,
            combat_lifepoints=990,
            combat_prayer_points=990,
        )
        first, ok, _ = apply_fight_caves_review_pure(
            data, lambda: 0.0, equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok)
        first_hp = first["fight_caves"]["roster"][0]["lifepoints"]
        second, ok, result = apply_fight_caves_review_pure(
            first, lambda: 0.0, equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok)
        self.assertLessEqual(second["fight_caves"]["roster"][0]["lifepoints"], first_hp)
        self.assertGreaterEqual(result["enemy_prayer_drain"], 10)
        self.assertLess(second["combat_prayer_points"], 990)

    def test_wave_completion_and_tz_kek_split_use_stable_roster_instances(self):
        data = _entered()
        with patch(
            "ankiscape.logic.fight_caves_logic.apply_combat_burst_pure",
            side_effect=_combat_result(killed=True),
        ):
            advanced, ok, result = apply_fight_caves_review_pure(data, lambda: 0.5)
        self.assertTrue(ok)
        self.assertTrue(result["wave_completed"])
        self.assertEqual(advanced["fight_caves"]["wave"], 2)

        advanced["fight_caves"]["wave"] = 3
        advanced["fight_caves"]["roster"] = []
        with patch(
            "ankiscape.logic.fight_caves_logic.apply_combat_burst_pure",
            side_effect=_combat_result(killed=True),
        ):
            split, ok, result = apply_fight_caves_review_pure(advanced, lambda: 0.5)
        self.assertTrue(ok)
        self.assertEqual(result["split_count"], 2)
        self.assertEqual(
            [member["enemy_id"] for member in split["fight_caves"]["roster"]],
            ["tz_kek_small", "tz_kek_small"],
        )
        self.assertEqual(
            len({member["instance_id"] for member in split["fight_caves"]["roster"]}),
            2,
        )

    def test_real_ket_zek_kill_records_the_exact_diary_variant(self):
        data = _entered(
            attack_level=99,
            strength_level=99,
            defense_level=99,
            constitution_level=99,
            combat_lifepoints=990,
            equipment={},
        )
        data["fight_caves"].update(
            wave=31,
            roster=[
                {
                    "instance_id": "diary-ket-zek",
                    "enemy_id": "ket_zek",
                    "lifepoints": 1,
                }
            ],
            engaged_instance_id="diary-ket-zek",
        )
        updated, ok, result = apply_fight_caves_review_pure(
            data, lambda: 0.0, equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, result)
        self.assertEqual(updated["fight_caves"]["kill_counts"], {"ket_zek": 1})

    def test_a_mid_instance_kill_never_unloads_or_refills_the_real_bank(self):
        # A stale melee loadout (runes loaded) must ride out the instance
        # untouched: the burst engine may not unload it into the real bank nor
        # restock the pack from it mid-run.
        data = _entered(
            combat_supply_loadout={"runes": {"Air rune": 5, "Mind rune": 5}},
        )
        data["fight_caves"].update(
            roster=[
                {
                    "instance_id": "stale-loadout-kill",
                    "enemy_id": "tz_kih",
                    "lifepoints": 1,
                }
            ],
            engaged_instance_id="stale-loadout-kill",
        )
        bank_before = copy.deepcopy(data["inventory"])

        updated, ok, result = apply_fight_caves_review_pure(
            data, lambda: 0.0, equipment_data=EQUIPMENT_DATA
        )

        self.assertTrue(ok, result)
        self.assertTrue(result["wave_completed"])
        self.assertEqual(updated["inventory"], bank_before)
        self.assertEqual(
            updated["combat_supply_loadout"]["runes"],
            {"Air rune": 5, "Mind rune": 5},
        )
        self.assertEqual(updated["combat_supply_loadout"]["food"], {})

    def test_fight_caves_kill_count_sanitizer_rejects_other_variants(self):
        sanitized = sanitize_fight_caves_state_pure(
            {
                "kill_counts": {
                    "ket_zek": "2",
                    "tz_kih": 99,
                    "not_an_enemy": 100,
                }
            }
        )
        self.assertEqual(sanitized["kill_counts"], {"ket_zek": 2})
        self.assertEqual(
            sanitize_fight_caves_state_pure({"kill_counts": []})["kill_counts"],
            {},
        )

    def test_tz_kek_melee_recoil_uses_the_shared_combat_slice(self):
        data = _entered(
            attack_level=99,
            strength_level=99,
            defense_level=99,
            constitution_level=99,
            combat_lifepoints=990,
        )
        data["fight_caves"]["wave"] = 3
        data["fight_caves"]["roster"] = []
        updated, ok, result = apply_fight_caves_review_pure(
            data, lambda: 0.0, equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok)
        self.assertGreaterEqual(result["melee_recoil_damage"], 10)
        self.assertEqual(
            updated["combat_lifepoints"],
            990 - result["melee_recoil_damage"],
        )

    def test_unengaged_pressure_uses_real_defence_and_protection_prayers(self):
        def _wave_eight(praying: bool):
            data = _entered(
                defense_level=1,
                constitution_level=99,
                combat_lifepoints=990,
                combat_selected_prayers=(
                    ["protect_from_missiles"] if praying else []
                ),
                combat_prayer_uptime="100",
                combat_prayer_points=990,
            )
            data["fight_caves"]["wave"] = 8
            data["fight_caves"]["roster"] = []
            view = fight_caves_view_pure(data)
            data["fight_caves"] = view
            data["fight_caves"]["automation_mode"] = "advanced"
            data["fight_caves"]["engaged_instance_id"] = next(
                member["instance_id"]
                for member in view["roster"]
                if member["enemy_id"] == "tz_kih"
            )
            return data

        with patch(
            "ankiscape.logic.fight_caves_logic.apply_combat_burst_pure",
            side_effect=_combat_result(lifepoints=100),
        ):
            _unprotected, ok, unprotected = apply_fight_caves_review_pure(
                _wave_eight(False), lambda: 0.5
            )
            _protected, protected_ok, protected = apply_fight_caves_review_pure(
                _wave_eight(True), lambda: 0.5
            )
        self.assertTrue(ok)
        self.assertTrue(protected_ok)
        self.assertGreater(unprotected["pressure_damage"], 0)
        self.assertEqual(protected["pressure_damage"], 0)
        self.assertEqual(protected["pressure_styles"], ("ranged",))

    def test_yt_mejkot_heals_an_injured_roster_member_every_second_review(self):
        data = _entered()
        data["fight_caves"]["wave"] = 16
        data["fight_caves"]["roster"] = []
        view = fight_caves_view_pure(data)
        data["fight_caves"] = view
        data["fight_caves"]["automation_mode"] = "advanced"
        kih = next(
            member
            for member in data["fight_caves"]["roster"]
            if member["enemy_id"] == "tz_kih"
        )
        kih["lifepoints"] = 20
        kih["encounter"]["enemy_lifepoints"] = 20
        data["fight_caves"]["engaged_instance_id"] = kih["instance_id"]
        with patch(
            "ankiscape.logic.fight_caves_logic.apply_combat_burst_pure",
            side_effect=_combat_result(),
        ):
            first, ok, first_result = apply_fight_caves_review_pure(
                data, lambda: 0.5
            )
            second, second_ok, second_result = apply_fight_caves_review_pure(
                first, lambda: 0.5
            )
        self.assertTrue(ok)
        self.assertTrue(second_ok)
        self.assertEqual(first_result["roster_healing"], 0)
        self.assertEqual(second_result["roster_healing"], 80)
        healed_kih = next(
            member
            for member in second["fight_caves"]["roster"]
            if member["enemy_id"] == "tz_kih"
        )
        self.assertEqual(healed_kih["lifepoints"], 100)

    def test_jad_telegraph_healers_and_completion_rewards_are_live(self):
        data = _entered()
        data["fight_caves"]["wave"] = 63
        data["fight_caves"]["roster"] = []
        with patch(
            "ankiscape.logic.fight_caves_logic.apply_combat_burst_pure",
            side_effect=_combat_result(lifepoints=1200),
        ):
            fighting, ok, result = apply_fight_caves_review_pure(data, lambda: 0.0)
        self.assertTrue(ok)
        self.assertTrue(result["healers_spawned"])
        self.assertEqual(
            sum(
                member["enemy_id"] == "yt_hurkot"
                for member in fighting["fight_caves"]["roster"]
            ),
            4,
        )
        self.assertEqual(fighting["fight_caves"]["jad_next_style"], "magic")
        casual = fight_caves_view_pure(fighting)
        healer = next(
            member for member in casual["roster_view"] if member["enemy_id"] == "yt_hurkot"
        )
        self.assertEqual(FIGHT_CAVES_ENEMY_DATA["yt_hurkot"]["priority"], 0)

        fighting["fight_caves"]["automation_mode"] = "advanced"
        jad = next(
            member for member in fighting["fight_caves"]["roster"]
            if member["enemy_id"] == "tztok_jad"
        )
        fighting["fight_caves"]["engaged_instance_id"] = jad["instance_id"]
        with patch(
            "ankiscape.logic.fight_caves_logic.apply_combat_burst_pure",
            side_effect=_combat_result(killed=True),
        ):
            won, ok, result = apply_fight_caves_review_pure(fighting, lambda: 0.5)
        self.assertTrue(ok)
        self.assertTrue(result["fire_cape"])
        self.assertEqual(result["tokkul"], FIGHT_CAVES_COMPLETION_TOKKUL)
        self.assertEqual(won["inventory"]["Fire cape"], 1)
        self.assertEqual(won["inventory"]["Tokkul"], FIGHT_CAVES_COMPLETION_TOKKUL)
        self.assertFalse(won["fight_caves"]["active"])
        self.assertEqual(healer["display_name"], "Yt-HurKot")

    def test_safe_death_preserves_possessions_and_pays_partial_reward(self):
        data = _entered(
            inventory={"Shark": 4, "Coins": 123},
            equipment={"cape": "Fire cape"},
            carried_inventory={"fight_caves": {"Shark": 2}},
        )
        data["fight_caves"]["wave"] = 40
        before_inventory = copy.deepcopy(data["inventory"])
        before_equipment = copy.deepcopy(data["equipment"])
        before_carried = copy.deepcopy(data["carried_inventory"])
        with patch(
            "ankiscape.logic.fight_caves_logic.apply_combat_burst_pure",
            side_effect=_combat_result(died=True),
        ):
            defeated, ok, result = apply_fight_caves_review_pure(data, lambda: 0.5)
        self.assertTrue(ok)
        self.assertTrue(result["safe_death"])
        self.assertEqual(defeated["equipment"], before_equipment)
        self.assertEqual(defeated["carried_inventory"], before_carried)
        for item, quantity in before_inventory.items():
            self.assertEqual(defeated["inventory"][item], quantity)
        self.assertEqual(
            defeated["inventory"]["Tokkul"], fight_caves_partial_tokkul_pure(40)
        )


class FightCavesRuntimeTests(unittest.TestCase):
    def test_review_dispatch_uses_live_combat_without_banking_or_deactivation(self):
        player = _entered(
            attack_level=1,
            strength_level=1,
            defense_level=1,
            constitution_level=99,
            combat_lifepoints=990,
        )
        saved = []
        gains = []
        deactivated = []
        ctx = RuntimeActionContext(
            player_data=player,
            random_random=lambda: 0.0,
            show_error_message=lambda *_args: self.fail("unexpected runtime error"),
            deactivate_current_skill=lambda: deactivated.append(True),
            award_skill_exp=lambda *_args: self.fail("combat reducer owns its XP"),
            award_hidden_skill_exp=lambda *_args: None,
            level_up_check=lambda *_args: None,
            check_achievements=lambda *_args: None,
            save_player_data=lambda: saved.append(True),
            refresh_skill_availability=lambda: None,
            show_exp=lambda amount: gains.append(float(amount)),
            show_activity_gain=lambda message: gains.append(str(message)),
            implemented_exp_keys_snapshot=lambda: {},
            show_quest_exp_delta=lambda *_args: None,
        )

        self.assertTrue(handle_utility_answer(ctx))
        self.assertEqual(player.get("combat_bank_run", {}), {})
        self.assertTrue(player["fight_caves"]["active"])
        self.assertEqual(player["activity_session"], {"active_id": "fight_caves"})
        self.assertEqual(saved, [True])
        self.assertEqual(deactivated, [])
        self.assertTrue(any("Wave 1" in str(value) for value in gains))


class FightCavesAutoFleeSuppressionTests(unittest.TestCase):
    def test_a_starving_low_lp_player_does_not_silently_flee_the_cave(self):
        """The cave cannot be left mid-fight, so the engine's auto-flee must be
        suspended for the burst. The old code zeroed combat_auto_flee_percent, a
        key the engine never reads, so a player at the auto-eat threshold with no
        food silently fled every burst while believing they were still fighting.
        """
        player = _player(
            combat_lifepoints=40,  # far below the 40% auto-eat threshold of 800
            inventory={},          # nothing to eat
        )
        player["combat_auto_flee"] = True  # the engine default, explicit here
        entered, ok, _ = apply_fight_caves_command_pure(player, "enter")
        self.assertTrue(ok)

        updated, ok, result = apply_fight_caves_review_pure(
            entered, lambda: 0.5, equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, result)
        combat = updated.get("combat_last_result") or {}
        self.assertFalse(
            combat.get("fled", False),
            "the bounded cave burst must never resolve as a flee",
        )
        # The suspension is scoped to the burst: the player's own setting survives.
        self.assertTrue(updated.get("combat_auto_flee", True))


if __name__ == "__main__":
    unittest.main()
