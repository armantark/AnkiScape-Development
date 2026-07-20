import unittest

from dungeoneering_logic import (
    active_bind_slots_for_level_pure,
    ammo_bind_capacity_pure,
    begin_starter_session_pure,
    build_starter_floor_graph_pure,
    calculate_completion_payout_pure,
    eligible_frozen_bosses_pure,
    floor_theme_for_floor_pure,
    maximum_floor_for_level_pure,
    prestige_value_pure,
    record_starter_death_pure,
    required_level_for_floor_pure,
    resolve_floor_replay_pure,
    resolve_starter_room_pure,
)


class DungeoneeringLogicTests(unittest.TestCase):
    def test_floor_access_theme_and_bind_boundaries(self):
        scenarios = (
            (1, 1, "frozen", 1),
            (11, 21, "frozen", 2),
            (12, 23, "abandoned_i", 2),
            (30, 59, "abandoned_ii", 3),
            (48, 95, "warped", 4),
            (60, 119, "warped", 4),
        )
        for floor, level, theme_id, bind_slots in scenarios:
            with self.subTest(floor=floor):
                self.assertEqual(required_level_for_floor_pure(floor), level)
                self.assertEqual(maximum_floor_for_level_pure(level), floor)
                self.assertEqual(floor_theme_for_floor_pure(floor).id, theme_id)
                self.assertEqual(active_bind_slots_for_level_pure(level), bind_slots)
        self.assertEqual(maximum_floor_for_level_pure(120), 60)
        self.assertEqual(active_bind_slots_for_level_pure(120), 5)
        self.assertEqual(ammo_bind_capacity_pure(), 125)
        self.assertEqual(ammo_bind_capacity_pure(salt_in_the_wound_complete=True), 225)

    def test_prestige_replay_prefers_lower_then_higher_inside_the_theme(self):
        self.assertEqual(prestige_value_pure(9, 11), 11)
        self.assertEqual(
            resolve_floor_replay_pure(5, {1, 2, 3, 4}),
            resolve_floor_replay_pure(5, (1, 2, 3, 4)),
        )
        fresh = resolve_floor_replay_pure(5, {1, 2, 3, 4})
        self.assertEqual((fresh.credited_floor, fresh.xp_floor), (5, 5))

        lower = resolve_floor_replay_pure(5, {1, 2, 3, 5})
        self.assertEqual((lower.credited_floor, lower.xp_floor), (4, 4))

        higher = resolve_floor_replay_pure(5, {1, 2, 3, 4, 5})
        self.assertEqual((higher.credited_floor, higher.xp_floor), (6, 5))

        exhausted = resolve_floor_replay_pure(5, set(range(1, 12)))
        self.assertIsNone(exhausted.credited_floor)
        self.assertTrue(exhausted.repeated_without_credit)

    def test_completion_formula_requires_explicit_source_inputs(self):
        payout = calculate_completion_payout_pure(
            active_floor_xp=1000,
            prestige_floor_xp=600,
            complexity=1,
            death_multiplier=0.9,
            bonus_multiplier=1.25,
        )
        self.assertEqual(payout.base_xp, 800)
        self.assertEqual(payout.adjusted_xp, 360)
        self.assertEqual(payout.final_xp, 450)
        self.assertEqual(payout.tokens, 45)
        with self.assertRaisesRegex(ValueError, "death_multiplier"):
            calculate_completion_payout_pure(
                active_floor_xp=100,
                prestige_floor_xp=100,
                complexity=6,
                death_multiplier=1.1,
            )

    def test_frozen_boss_roster_unlocks_by_floor_and_level(self):
        self.assertEqual(
            {boss.id for boss in eligible_frozen_bosses_pure(1, 1)},
            {"gluttonous_behemoth", "astea_frostweb", "icy_bones"},
        )
        self.assertEqual(
            {boss.id for boss in eligible_frozen_bosses_pure(6, 11)},
            {
                "gluttonous_behemoth",
                "astea_frostweb",
                "icy_bones",
                "luminescent_icefiend",
                "plane_freezer_lakhrahnaz",
            },
        )
        self.assertEqual(eligible_frozen_bosses_pure(12, 99), ())

    def test_seeded_graph_is_deterministic_connected_and_complexity_shaped(self):
        first = build_starter_floor_graph_pure(seed=4107, complexity=6)
        second = build_starter_floor_graph_pure(seed=4107, complexity=6)
        simple = build_starter_floor_graph_pure(seed=4107, complexity=1)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 8)
        self.assertEqual(first[0].family, "start")
        self.assertEqual(sum(room.family == "boss" for room in first), 1)
        self.assertIn("skill", {room.family for room in first})
        self.assertIn("resource", {room.family for room in first})
        self.assertTrue({room.family for room in simple}.isdisjoint({"skill", "resource"}))
        for room in first:
            for neighbor in room.connected_room_ids:
                with self.subTest(room=room.id, neighbor=neighbor):
                    self.assertIn(room.id, first[neighbor].connected_room_ids)
        with self.assertRaisesRegex(ValueError, "complexity 1 or 6"):
            build_starter_floor_graph_pure(seed=1, complexity=5)

    def test_session_resolves_one_room_and_death_respawns_without_erasing_the_floor(self):
        session = begin_starter_session_pure(
            floor=6,
            dungeoneering_level=11,
            complexity=6,
            seed=99,
        )
        self.assertEqual(session.resolved_room_ids, (0,))
        first_room = session.frontier_room_ids[0]
        advanced = resolve_starter_room_pure(session, first_room)
        self.assertIn(first_room, advanced.resolved_room_ids)
        self.assertEqual(session.resolved_room_ids, (0,))
        with self.assertRaisesRegex(ValueError, "revealed frontier"):
            resolve_starter_room_pure(advanced, first_room)

        restarted = record_starter_death_pure(advanced)
        self.assertEqual(restarted.death_count, 1)
        self.assertEqual(restarted.current_room_id, 0)
        self.assertEqual(restarted.resolved_room_ids, advanced.resolved_room_ids)
        self.assertEqual(restarted.frontier_room_ids, advanced.frontier_room_ids)
        self.assertFalse(restarted.completed)

        current = restarted
        while not current.completed:
            critical_frontier = [
                room_id
                for room_id in current.frontier_room_ids
                if current.rooms[room_id].critical_path
            ]
            current = resolve_starter_room_pure(current, critical_frontier[0])
        self.assertEqual(current.rooms[current.current_room_id].family, "boss")

    def test_invalid_floor_and_level_gates_fail_before_state_creation(self):
        for invalid_floor in (0, 61, "bad"):
            with self.subTest(invalid_floor=invalid_floor):
                with self.assertRaises(ValueError):
                    required_level_for_floor_pure(invalid_floor)
        with self.assertRaisesRegex(ValueError, "too low"):
            begin_starter_session_pure(
                floor=6,
                dungeoneering_level=10,
                complexity=6,
                seed=1,
            )
        with self.assertRaisesRegex(ValueError, "Frozen"):
            begin_starter_session_pure(
                floor=12,
                dungeoneering_level=23,
                complexity=6,
                seed=1,
            )


if __name__ == "__main__":
    unittest.main()
