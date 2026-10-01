import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from aqt.qt import QApplication

    HAS_AQT = True
except Exception:  # pragma: no cover - environment without aqt installed
    HAS_AQT = False

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.ui.ui import (
    compute_level_progress,
    current_target_display_name,
    grouped_inventory,
    stats_skill_progress_pure,
)
from ankiscape.core.constants import DUNGEONEERING_EXP_TABLE, EXP_TABLE
from ankiscape.logic_pure.logic_pure import (
    combat_attack_style_trained_skills_pure,
    combat_hud_state_pure,
)

class TestReviewHUDProgress(unittest.TestCase):
    def test_progress_basic_mid_level(self):
        # Choose a level and midpoint exp
        lvl = 10
        prev = EXP_TABLE[lvl-1]
        nxt = EXP_TABLE[lvl]
        mid = (prev + nxt) / 2
        pct, remain, target = compute_level_progress(lvl, mid, EXP_TABLE)
        self.assertTrue(45 <= pct <= 55)  # around 50%
        self.assertAlmostEqual(remain, nxt - mid, delta=1e-6)
        self.assertEqual(target, min(lvl+1, 99))

    def test_progress_bounds_low(self):
        pct, remain, target = compute_level_progress(1, 0.0, EXP_TABLE)
        self.assertEqual(pct, 0)
        self.assertGreaterEqual(remain, 0.0)
        self.assertEqual(target, 2)

    def test_progress_bounds_high_level(self):
        # At very high levels ensure no crash and pct in range
        pct, remain, target = compute_level_progress(98, EXP_TABLE[98] - 1, EXP_TABLE)
        self.assertTrue(0 <= pct <= 100)
        self.assertGreaterEqual(remain, 0.0)
        self.assertEqual(target, 99)

    def test_progress_overflow_exp(self):
        lvl = 20
        pct, remain, _ = compute_level_progress(lvl, EXP_TABLE[lvl] + 12345, EXP_TABLE)
        self.assertEqual(pct, 100)
        self.assertEqual(remain, 0.0)

    def test_progress_handles_bad_inputs(self):
        # Negative level and None exp should not crash
        pct, remain, target = compute_level_progress(-5, None, EXP_TABLE)  # type: ignore[arg-type]
        self.assertTrue(0 <= pct <= 100)
        self.assertGreaterEqual(remain, 0.0)
        self.assertGreaterEqual(target, 2)

    def test_progress_max_level_bounds(self):
        # Level 99 boundary uses last table values
        lvl = 99
        pct, remain, target = compute_level_progress(lvl, EXP_TABLE[-1], EXP_TABLE)
        self.assertEqual(pct, 100)
        self.assertEqual(remain, 0.0)
        self.assertEqual(target, 99)

    def test_stats_view_uses_dungeoneering_levels_above_99(self):
        level_100 = stats_skill_progress_pure(
            "Dungeoneering",
            100,
            DUNGEONEERING_EXP_TABLE[99],
        )
        self.assertEqual(level_100["percent"], 0)
        self.assertEqual(level_100["target_level"], 101)
        self.assertEqual(level_100["max_level"], 120)
        self.assertEqual(
            level_100["remaining"],
            DUNGEONEERING_EXP_TABLE[100] - DUNGEONEERING_EXP_TABLE[99],
        )

        level_120 = stats_skill_progress_pure(
            "Dungeoneering",
            120,
            DUNGEONEERING_EXP_TABLE[-1],
        )
        self.assertEqual(
            level_120,
            {"percent": 100, "remaining": 0.0, "target_level": 120, "max_level": 120},
        )


class TestCurrentTargetDisplayName(unittest.TestCase):
    def test_echoes_selected_target_display_name(self):
        pd = {"current_craft": "fire_empty_pot"}
        self.assertEqual(current_target_display_name("Crafting", pd), "Empty pot")

    def test_falls_back_to_skill_default_when_unset(self):
        # Empty player data should resolve to the registry default target.
        self.assertEqual(current_target_display_name("Mining", {}), "Rune essence")

    def test_resolves_for_each_target_skill(self):
        cases = {
            "Woodcutting": ("current_tree", "oak", "Oak"),
            "Crafting": ("current_craft", "form_pot_unfired", "Pot (unfired)"),
            "Firemaking": ("current_firemaking", "oak_logs", "Oak logs"),
            "Fishing": ("current_fishing", "catch_crayfish", "Catch crayfish"),
            "Cooking": ("current_cooking", "cook_shrimps", "Cook raw shrimps"),
            "Runecrafting": ("current_runecrafting", "craft_air_runes", "Air runes"),
            "Herblore": ("current_herblore", "clean_guam", "Clean guam"),
            "Prayer": ("current_prayer", "gilded_altar_dragon_bones", "Dragon bones"),
            "Magic": ("current_magic", "low_alchemy", "Low Level Alchemy"),
            "Construction": ("current_construction", "crude_wooden_chair", "Crude wooden chair"),
            "Thieving": ("current_thieving", "pickpocket_man", "Man / Woman"),
            "Agility": ("current_agility", "burthorpe_course", "Burthorpe Agility Course"),
            "Quests": ("current_quest", "rune_mysteries", "Rune Mysteries"),
            "Combat": ("current_combat_target", "giant_rat", "Giant rat"),
        }
        for skill, (key, target_id, expected) in cases.items():
            with self.subTest(skill=skill):
                self.assertEqual(
                    current_target_display_name(skill, {key: target_id}), expected
                )

    def test_unknown_target_id_echoes_raw_id(self):
        # Defensive: a stale/unknown id still shows something rather than blanking.
        out = current_target_display_name("Crafting", {"current_craft": "bogus_id"})
        self.assertEqual(out, "bogus_id")

    def test_returns_none_when_no_target_contract_exists(self):
        for skill in ("Attack", "Nonsense"):
            with self.subTest(skill):
                self.assertIsNone(current_target_display_name(skill, {}))


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class TestQuestReviewHudTarget(unittest.TestCase):
    def test_review_hud_names_the_boss_while_a_quest_fight_is_pending(self):
        from ankiscape.ui import ui

        self.app = QApplication.instance() or QApplication([])
        hud = ui.ReviewHUD()
        self.addCleanup(hud.deleteLater)
        player = {
            "current_quest": "demon_slayer",
            "quests": {"demon_slayer": {"started": True, "progress": 7, "completed": False}},
            "equipment": {"weapon": "Silverlight"},
        }
        hud.set_data(player, "Quests")
        self.assertEqual(hud.target_lbl.text(), "Delrith")

        player["equipment"] = {}
        hud.set_data(player, "Quests")
        self.assertEqual(hud.target_lbl.text(), "Demon Slayer")


class TestCombatAttackStyleTrainedSkills(unittest.TestCase):
    def test_melee_styles_name_their_skill_plus_constitution(self):
        self.assertEqual(
            combat_attack_style_trained_skills_pure("accurate"),
            ("Attack", "Constitution"),
        )
        self.assertEqual(
            combat_attack_style_trained_skills_pure("aggressive"),
            ("Strength", "Constitution"),
        )

    def test_controlled_trains_all_three_melee_skills(self):
        self.assertEqual(
            combat_attack_style_trained_skills_pure("controlled"),
            ("Attack", "Strength", "Defence", "Constitution"),
        )

    def test_ranged_longrange_adds_defence(self):
        self.assertEqual(
            combat_attack_style_trained_skills_pure("ranged_longrange"),
            ("Ranged", "Defence", "Constitution"),
        )

    def test_unknown_style_falls_back_to_default(self):
        self.assertEqual(
            combat_attack_style_trained_skills_pure("bogus"),
            combat_attack_style_trained_skills_pure("accurate"),
        )


class TestCombatHudStatePure(unittest.TestCase):
    def test_full_health_uncarried_enemy_reports_full_bars(self):
        state = combat_hud_state_pure({"current_combat_target": "chicken"})
        self.assertEqual(state["player_pct"], 100)
        self.assertEqual(state["enemy_pct"], 100)
        self.assertFalse(state["enemy_carried"])
        self.assertEqual(state["enemy_name"], "Chicken")
        self.assertEqual(state["enemy_lifepoints"], state["enemy_max_lifepoints"])

    def test_carried_encounter_reflects_wounded_enemy(self):
        pd = {
            "current_combat_target": "chicken",
            "combat_lifepoints": 40,
            "constitution_level": 10,
            "prayer_level": 50,
            "combat_prayer_points": 310,
            "summoning_level": 42,
            "summoning_state": {"summoning_points_current": 17},
            "combat_encounter": {"target_id": "chicken", "enemy_lifepoints": 9},
        }
        state = combat_hud_state_pure(pd)
        self.assertTrue(state["enemy_carried"])
        self.assertEqual(state["enemy_lifepoints"], 9)
        self.assertLess(state["enemy_pct"], 100)
        self.assertEqual(state["player_pct"], 40)  # 40/100
        self.assertEqual(state["prayer_points"], 31)
        self.assertEqual(state["prayer_max_points"], 50)
        self.assertEqual(state["summoning_points"], 17)
        self.assertEqual(state["summoning_max_points"], 42)

    def test_encounter_for_other_target_is_not_carried(self):
        pd = {
            "current_combat_target": "chicken",
            "combat_encounter": {"target_id": "giant_rat", "enemy_lifepoints": 1},
        }
        state = combat_hud_state_pure(pd)
        self.assertFalse(state["enemy_carried"])
        self.assertEqual(state["enemy_lifepoints"], state["enemy_max_lifepoints"])

    def test_kill_count_surfaces_from_player_data(self):
        pd = {"current_combat_target": "chicken", "combat_kill_counts": {"chicken": 7}}
        self.assertEqual(combat_hud_state_pure(pd)["kills_total"], 7)


class TestBankGrouping(unittest.TestCase):
    """The Stronghold of Security boots reached the bank with no ItemDefinition,
    so they were filed under the catch-all "Other" group instead of Equipment."""

    def test_stronghold_reward_boots_group_as_equipment(self):
        groups = dict(grouped_inventory({"Fancy boots": 1, "Fighting boots": 1}))

        self.assertNotIn("Other", groups)
        self.assertEqual(
            [name for name, _amount, _asset in groups["Equipment"]],
            ["Fancy boots", "Fighting boots"],
        )


if __name__ == "__main__":
    unittest.main()
