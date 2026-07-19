import unittest

from combat_data import COMBAT_ENEMY_DATA
from slayer_data import (
    MAZCHNA_FAMILIES,
    MAZCHNA_FAMILIES_BY_ID,
    MAZCHNA_MASTER,
    TURAEL_FAMILIES,
    TURAEL_FAMILIES_BY_ID,
    VANNAKA_FAMILIES,
    VANNAKA_FAMILIES_BY_ID,
    VANNAKA_MASTER,
)
from slayer_logic import (
    apply_slayer_kills_pure,
    eligible_slayer_families_pure,
    get_slayer_assignment_pure,
    sanitize_slayer_state_pure,
    slayer_master_display_name_pure,
    slayer_target_ids_for_assignment_pure,
)
from slayer_readiness import (
    slayer_catalog_integrity_issues_pure,
    slayer_master_readiness_pure,
)


class SlayerAssignmentDataTest(unittest.TestCase):
    def test_turael_pool_preserves_complete_reconciled_denominator(self):
        self.assertEqual(len(TURAEL_FAMILIES), 23)
        self.assertEqual(sum(family.weight for family in TURAEL_FAMILIES), 355)
        self.assertEqual(
            (
                TURAEL_FAMILIES_BY_ID["icefiends"].count_min,
                TURAEL_FAMILIES_BY_ID["icefiends"].count_max,
            ),
            (10, 20),
        )
        self.assertEqual(
            (
                TURAEL_FAMILIES_BY_ID["grotworms"].count_min,
                TURAEL_FAMILIES_BY_ID["grotworms"].count_max,
            ),
            (15, 30),
        )

    def test_hidden_mazchna_pool_preserves_complete_master_specific_rows(self):
        self.assertEqual(len(MAZCHNA_FAMILIES), 27)
        self.assertEqual(sum(family.weight for family in MAZCHNA_FAMILIES), 325)
        self.assertEqual(
            (
                MAZCHNA_FAMILIES_BY_ID["cyclopes"].count_min,
                MAZCHNA_FAMILIES_BY_ID["cyclopes"].count_max,
            ),
            (30, 60),
        )
        self.assertEqual(
            (
                MAZCHNA_FAMILIES_BY_ID["wall_beasts"].count_min,
                MAZCHNA_FAMILIES_BY_ID["wall_beasts"].count_max,
            ),
            (10, 20),
        )
        self.assertEqual(MAZCHNA_MASTER.required_combat_level, 20)
        self.assertEqual(MAZCHNA_MASTER.required_quest_id, "priest_in_peril")
        self.assertEqual(MAZCHNA_MASTER.alternate_display_name, "Achtryn")
        self.assertFalse(MAZCHNA_MASTER.runtime_enabled)

    def test_mazchna_readiness_is_derived_and_keeps_partial_pool_hidden(self):
        readiness = slayer_master_readiness_pure(
            MAZCHNA_MASTER.id, COMBAT_ENEMY_DATA
        )

        self.assertFalse(readiness["certified"])
        self.assertFalse(readiness["runtime_enabled"])
        self.assertEqual(readiness["family_count"], 27)
        self.assertEqual(readiness["ready_family_count"], 26)
        self.assertEqual(
            set(readiness["blockers"]),
            {"mogres:combat_target"},
        )
        self.assertNotIn("hobgoblins:slayer_xp", readiness["blockers"])
        self.assertEqual(
            eligible_slayer_families_pure(
                {
                    "slayer_level": 99,
                    "combat_level": 126,
                    "quests": {"priest_in_peril": {"completed": True}},
                },
                MAZCHNA_MASTER.id,
            ),
            (),
        )

    def test_hidden_vannaka_pool_preserves_complete_master_specific_rows(self):
        self.assertEqual(len(VANNAKA_FAMILIES), 35)
        self.assertEqual(sum(family.weight for family in VANNAKA_FAMILIES), 460)
        self.assertEqual(
            (
                VANNAKA_FAMILIES_BY_ID["crocodiles"].count_min,
                VANNAKA_FAMILIES_BY_ID["crocodiles"].count_max,
            ),
            (30, 60),
        )
        self.assertEqual(
            (
                VANNAKA_FAMILIES_BY_ID["grotworms"].count_min,
                VANNAKA_FAMILIES_BY_ID["grotworms"].count_max,
            ),
            (60, 120),
        )
        self.assertEqual(VANNAKA_MASTER.required_combat_level, 40)
        self.assertFalse(VANNAKA_MASTER.runtime_enabled)

    def test_vannaka_readiness_is_derived_and_keeps_partial_pool_hidden(self):
        readiness = slayer_master_readiness_pure(
            VANNAKA_MASTER.id, COMBAT_ENEMY_DATA
        )

        self.assertFalse(readiness["certified"])
        self.assertFalse(readiness["runtime_enabled"])
        self.assertEqual(readiness["family_count"], 35)
        self.assertEqual(readiness["ready_family_count"], 26)
        self.assertEqual(
            set(readiness["blockers"]),
            {
                "brine_rats:combat_target",
                "earth_warriors:wilderness_risk",
                "green_dragons:combat_target",
                "harpie_bug_swarms:combat_target",
                "killerwatts:combat_target",
                "mogres:combat_target",
                "molanisks:combat_target",
                "sea_snakes:combat_target",
                "turoth:combat_target",
            },
        )
        self.assertEqual(
            eligible_slayer_families_pure(
                {"slayer_level": 99, "combat_level": 126, "quests": {}},
                VANNAKA_MASTER.id,
            ),
            (),
        )

    def test_slayer_catalog_integrity_rejects_no_live_or_stale_master_state(self):
        self.assertEqual(
            slayer_catalog_integrity_issues_pure(COMBAT_ENEMY_DATA),
            (),
        )

    def test_every_assignable_family_has_a_live_combat_target(self):
        missing = {
            target_id
            for family in TURAEL_FAMILIES
            for target_id in family.target_ids
            if target_id not in COMBAT_ENEMY_DATA
        }
        self.assertEqual(missing, set())

    def test_new_turael_targets_preserve_period_identity_and_slayer_xp(self):
        expected = {
            "gelatinous_abomination": (2, 50, 5.0),
            "young_grotworm": (10, 150, 15.0),
            "monkey": (3, 60, 6.0),
        }
        for target_id, (level, lifepoints, slayer_xp) in expected.items():
            with self.subTest(target_id=target_id):
                target = COMBAT_ENEMY_DATA[target_id]
                self.assertEqual(target["level"], level)
                self.assertEqual(target["stats"]["hitpoints"], lifepoints)
                self.assertEqual(target["slayer_xp"], slayer_xp)
                self.assertIn("oldid=", target["source"])

        finisher = COMBAT_ENEMY_DATA["gelatinous_abomination"]["finisher"]
        self.assertEqual(finisher["item"], "Spiked gauntlets")
        self.assertTrue(finisher["must_be_worn"])
        self.assertFalse(finisher["consume"])

    def test_player_gates_filter_families_without_hiding_baseline_rows(self):
        level_one = {"slayer_level": 1, "quests": {}}
        family_ids = {family.id for family in eligible_slayer_families_pure(level_one)}

        self.assertIn("gelatinous_abominations", family_ids)
        self.assertIn("grotworms", family_ids)
        self.assertNotIn("cave_bugs", family_ids)
        self.assertNotIn("banshees", family_ids)

        unlocked = {
            "slayer_level": 22,
            "quests": {"priest_in_peril": {"completed": True}},
        }
        unlocked_ids = {family.id for family in eligible_slayer_families_pure(unlocked)}
        self.assertEqual(
            unlocked_ids,
            {family.id for family in TURAEL_FAMILIES},
        )


class SlayerAssignmentLogicTest(unittest.TestCase):
    def test_assignment_roll_uses_weight_then_exact_inclusive_count_range(self):
        rolls = iter((0.0, 0.999999))
        data, ok, result = get_slayer_assignment_pure(
            {"slayer_level": 1, "quests": {}},
            rng=lambda: next(rolls),
        )

        self.assertTrue(ok)
        self.assertEqual(result["family_display_name"], "Bats")
        self.assertEqual(data["slayer_assignment"]["initial_count"], 50)
        self.assertEqual(data["slayer_assignment"]["remaining"], 50)

    def test_previous_family_is_excluded_when_an_alternative_exists(self):
        rolls = iter((0.0, 0.0))
        data, ok, _result = get_slayer_assignment_pure(
            {
                "slayer_level": 1,
                "quests": {},
                "slayer_last_family_id": "bats",
            },
            rng=lambda: next(rolls),
        )

        self.assertTrue(ok)
        self.assertEqual(data["slayer_assignment"]["family_id"], "bears")

    def test_only_matching_targets_credit_task_and_slayer_xp(self):
        player = {
            "slayer_exp": 0.0,
            "slayer_points": 9,
            "slayer_qualifying_streak": 4,
            "slayer_assignment": {
                "master_id": "turael_spria",
                "family_id": "bats",
                "initial_count": 2,
                "remaining": 2,
            },
        }
        enemy_data = {
            "giant_bat": {"slayer_xp": 32.0},
            "black_bear": {"slayer_xp": 25.0},
        }

        unchanged, miss = apply_slayer_kills_pure(
            player, target_id="black_bear", kills=1, enemy_data=enemy_data
        )
        self.assertEqual(miss["credited_kills"], 0)
        self.assertEqual(unchanged["slayer_assignment"]["remaining"], 2)

        completed, hit = apply_slayer_kills_pure(
            player, target_id="giant_bat", kills=3, enemy_data=enemy_data
        )
        self.assertEqual(hit["credited_kills"], 2)
        self.assertEqual(hit["slayer_xp"], 64.0)
        self.assertTrue(hit["completed"])
        self.assertEqual(completed["slayer_exp"], 64.0)
        self.assertEqual(completed["slayer_tasks_completed"], 1)
        self.assertEqual(completed["slayer_last_family_id"], "bats")
        self.assertEqual(completed["slayer_points"], 9)
        self.assertEqual(completed["slayer_qualifying_streak"], 4)
        self.assertEqual(slayer_target_ids_for_assignment_pure(completed), ())

    def test_sanitizer_repairs_invalid_assignment_and_spria_is_quest_reactive(self):
        sanitized = sanitize_slayer_state_pure(
            {
                "slayer_assignment": {
                    "master_id": "turael_spria",
                    "family_id": "not_a_family",
                    "remaining": -4,
                },
                "slayer_tasks_completed": -1,
                "slayer_combat_filter": 1,
            }
        )

        self.assertEqual(sanitized["slayer_assignment"], {})
        self.assertEqual(sanitized["slayer_tasks_completed"], 0)
        self.assertTrue(sanitized["slayer_combat_filter"])
        self.assertEqual(
            slayer_master_display_name_pure(
                {"quests": {"while_guthix_sleeps": {"completed": True}}}
            ),
            "Spria",
        )


if __name__ == "__main__":
    unittest.main()
