import unittest

from ui import compute_level_progress, current_target_display_name
from constants import EXP_TABLE
from logic_pure import (
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
            "combat_encounter": {"target_id": "chicken", "enemy_lifepoints": 9},
        }
        state = combat_hud_state_pure(pd)
        self.assertTrue(state["enemy_carried"])
        self.assertEqual(state["enemy_lifepoints"], 9)
        self.assertLess(state["enemy_pct"], 100)
        self.assertEqual(state["player_pct"], 40)  # 40/100

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


if __name__ == "__main__":
    unittest.main()
