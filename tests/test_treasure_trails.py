"""Easy Treasure Trails: one-clue ownership, step resolution and casket rewards.

The rule under the most pressure here is ownership. The period allows one clue
across every tier; the per-tier version an AnkiScape record carried is a 2015
mechanic. So the ownership tests assert the period rule directly — including the
part that is easy to get backwards, that a casket must stay outside the check so
a finished trail can still be opened.

Every casket reward is reached the way a player reaches it: run a trail to its
end, then open what the trail produced.
"""

import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.treasure_trails_data import (
    CASKET_ITEMS,
    CLUE_SCROLL_ITEMS,
    IMPLEMENTED_CLUE_TIERS,
    TREASURE_TRAILS_ACTIVITY_ID,
    TREASURE_TRAILS_EASY_MAX_STEPS,
    TREASURE_TRAILS_EASY_RARE_REWARDS,
    TREASURE_TRAILS_EASY_REWARD_SPOTS,
    TREASURE_TRAILS_EASY_STANDARD_REWARDS,
    TREASURE_TRAILS_EASY_STEPS,
)
from ankiscape.logic.treasure_trails_logic import (
    abandon_treasure_trail_pure,
    apply_treasure_trail_review_pure,
    apply_treasure_trails_command_pure,
    clue_ownership_reason_pure,
    emote_step_blocked_reason_pure,
    filter_clue_scroll_outputs_pure,
    open_casket_pure,
    read_clue_scroll_pure,
    sanitize_treasure_trails_state_pure,
    treasure_trails_view_pure,
)


def player(**changes):
    data = {
        "inventory": {},
        "equipment": {},
        "activity_session": {"active_id": ""},
        "treasure_trail": {},
    }
    data.update(changes)
    return data


def _draws(values):
    """A deterministic roll sequence; runs out rather than wrapping silently."""
    stream = iter(values)
    return lambda: next(stream)


def _trail(steps, index=0, tier="easy", **changes):
    data = player(
        inventory={CLUE_SCROLL_ITEMS[tier]: 1},
        activity_session={"active_id": TREASURE_TRAILS_ACTIVITY_ID},
        treasure_trail={"version": 1, "tier": tier, "steps": list(steps), "index": index},
    )
    data.update(changes)
    return data


class ClueOwnershipTest(unittest.TestCase):
    def test_a_player_holding_no_clue_may_receive_one(self):
        self.assertEqual(clue_ownership_reason_pure(player()), "")
        self.assertEqual(
            filter_clue_scroll_outputs_pure(player(), {"Clue scroll (easy)": 1, "Coins": 5}),
            {"Clue scroll (easy)": 1, "Coins": 5},
        )

    def test_a_clue_of_any_tier_blocks_a_clue_of_any_other_tier(self):
        """One clue in total, not one per tier."""
        for held in CLUE_SCROLL_ITEMS.values():
            for offered in CLUE_SCROLL_ITEMS.values():
                with self.subTest(held=held, offered=offered):
                    save = player(inventory={held: 1})
                    self.assertNotEqual(clue_ownership_reason_pure(save), "")
                    self.assertEqual(
                        filter_clue_scroll_outputs_pure(save, {offered: 1, "Coins": 5}),
                        {"Coins": 5},
                    )

    def test_a_trail_in_progress_blocks_a_new_clue_even_with_an_empty_inventory(self):
        save = _trail(["simple_port_sarim_sailor"], inventory={})
        self.assertNotEqual(clue_ownership_reason_pure(save), "")

    def test_a_casket_never_blocks_a_new_clue(self):
        """The period keeps caskets outside the ownership check."""
        for casket in CASKET_ITEMS.values():
            with self.subTest(casket=casket):
                save = player(inventory={casket: 1})
                self.assertEqual(clue_ownership_reason_pure(save), "")
                self.assertIn(
                    "Clue scroll (easy)",
                    filter_clue_scroll_outputs_pure(save, {"Clue scroll (easy)": 1}),
                )

    def test_a_payload_offering_two_clues_delivers_only_the_higher_tier(self):
        filtered = filter_clue_scroll_outputs_pure(
            player(), {"Clue scroll (hard)": 1, "Clue scroll (elite)": 1}
        )
        self.assertEqual(filtered, {"Clue scroll (elite)": 1})


class TrailStartTest(unittest.TestCase):
    def test_reading_a_clue_the_player_does_not_have_is_refused(self):
        _updated, ok, info = read_clue_scroll_pure(player(), "easy")
        self.assertFalse(ok)
        self.assertIn("no Clue scroll (easy)", info["reason"])

    def test_a_trail_runs_between_one_and_five_steps(self):
        lengths = set()
        for draw in (0.0, 0.25, 0.45, 0.65, 0.99):
            started, ok, _info = read_clue_scroll_pure(
                player(inventory={"Clue scroll (easy)": 1}), "easy", lambda d=draw: d
            )
            self.assertTrue(ok)
            lengths.add(len(started["treasure_trail"]["steps"]))
        self.assertEqual(lengths, {1, 2, 3, 4, 5})
        self.assertEqual(max(lengths), TREASURE_TRAILS_EASY_MAX_STEPS)

    def test_starting_a_trail_claims_the_activity_session(self):
        started, ok, _info = read_clue_scroll_pure(
            player(inventory={"Clue scroll (easy)": 1}), "easy", lambda: 0.0
        )
        self.assertTrue(ok)
        self.assertEqual(
            started["activity_session"]["active_id"], TREASURE_TRAILS_ACTIVITY_ID
        )
        self.assertEqual(started["current_utility"], TREASURE_TRAILS_ACTIVITY_ID)
        self.assertEqual(started["treasure_trails_started"], 1)

    def test_a_second_trail_cannot_start_while_one_is_running(self):
        _updated, ok, info = read_clue_scroll_pure(
            _trail(["simple_port_sarim_sailor"]), "easy"
        )
        self.assertFalse(ok)
        self.assertIn("already following", info["reason"])

    def test_an_unimplemented_tier_refuses_with_a_reason_rather_than_doing_nothing(self):
        for tier in set(CLUE_SCROLL_ITEMS) - set(IMPLEMENTED_CLUE_TIERS):
            with self.subTest(tier=tier):
                save = player(inventory={CLUE_SCROLL_ITEMS[tier]: 1})
                _updated, ok, info = read_clue_scroll_pure(save, tier)
                self.assertFalse(ok)
                self.assertEqual(info["tier_locked"], tier)
                self.assertIn("not built yet", info["reason"])

    def test_a_held_higher_tier_clue_is_visible_and_labelled_rather_than_silent(self):
        view = treasure_trails_view_pure(player(inventory={"Clue scroll (hard)": 1}))
        row = next(row for row in view["clue_rows"] if row["tier"] == "hard")
        self.assertFalse(row["implemented"])
        self.assertFalse(row["can_read"])
        self.assertIn("not built yet", row["locked_reason"])
        self.assertFalse(view["can_receive_clue"])


class TrailProgressTest(unittest.TestCase):
    def test_a_review_outside_a_trail_is_refused(self):
        _updated, ok, info = apply_treasure_trail_review_pure(player())
        self.assertFalse(ok)
        self.assertIn("Read a clue scroll", info["reason"])

    def test_each_review_resolves_one_step(self):
        save = _trail(["simple_port_sarim_sailor", "map_lumberyard_crate"])
        after, ok, result = apply_treasure_trail_review_pure(save)
        self.assertTrue(ok)
        self.assertFalse(result["terminal"])
        self.assertEqual(after["treasure_trail"]["index"], 1)

    def test_the_last_step_trades_the_clue_for_a_casket(self):
        save = _trail(["simple_port_sarim_sailor"])
        after, ok, result = apply_treasure_trail_review_pure(save)
        self.assertTrue(ok)
        self.assertTrue(result["terminal"])
        self.assertNotIn("Clue scroll (easy)", after["inventory"])
        self.assertEqual(after["inventory"]["Casket (easy)"], 1)
        self.assertEqual(after["treasure_trail"], {})
        self.assertEqual(after["activity_session"]["active_id"], "")
        self.assertEqual(after["treasure_trails_completed"], 1)

    def test_an_emote_step_stalls_until_the_listed_gear_is_worn(self):
        save = _trail(["emote_duel_arena_bow"])
        stalled, ok, result = apply_treasure_trail_review_pure(save)
        self.assertTrue(ok)
        self.assertTrue(result["blocked"])
        self.assertEqual(stalled["treasure_trail"]["index"], 0)
        self.assertIn("Iron chainbody", result["message"])

        geared = _trail(
            ["emote_duel_arena_bow"],
            equipment={"body": "Iron chainbody", "legs": "Leather chaps", "head": "Coif"},
        )
        done, ok, result = apply_treasure_trail_review_pure(geared)
        self.assertTrue(ok)
        self.assertTrue(result["terminal"])
        self.assertEqual(done["inventory"]["Casket (easy)"], 1)

    def test_the_bare_emote_step_stalls_while_anything_is_worn(self):
        worn = _trail(["emote_burthorpe_games_room_cheer"], equipment={"head": "Coif"})
        _stalled, ok, result = apply_treasure_trail_review_pure(worn)
        self.assertTrue(ok)
        self.assertTrue(result["blocked"])

        bare = _trail(["emote_burthorpe_games_room_cheer"])
        done, ok, result = apply_treasure_trail_review_pure(bare)
        self.assertTrue(ok)
        self.assertTrue(result["terminal"])
        self.assertEqual(done["inventory"]["Casket (easy)"], 1)

    def test_a_non_emote_step_is_never_gear_blocked(self):
        for step_id, step in TREASURE_TRAILS_EASY_STEPS.items():
            if step["kind"] == "emote":
                continue
            with self.subTest(step_id=step_id):
                self.assertEqual(
                    emote_step_blocked_reason_pure(player(equipment={}), step_id), ""
                )

    def test_abandoning_keeps_the_scroll_so_the_trail_can_be_resumed(self):
        save = _trail(["simple_port_sarim_sailor", "map_lumberyard_crate"], index=1)
        after, ok, _info = abandon_treasure_trail_pure(save)
        self.assertTrue(ok)
        self.assertEqual(after["treasure_trail"], {})
        self.assertEqual(after["inventory"]["Clue scroll (easy)"], 1)
        self.assertEqual(after["activity_session"]["active_id"], "")
        _again, ok, _info = read_clue_scroll_pure(after, "easy", lambda: 0.0)
        self.assertTrue(ok)


class CasketRewardTest(unittest.TestCase):
    def test_opening_a_casket_the_player_does_not_have_is_refused(self):
        _updated, ok, info = open_casket_pure(player(), "easy")
        self.assertFalse(ok)
        self.assertIn("no Casket (easy)", info["reason"])

    def test_a_finished_trail_opens_normally_even_while_a_new_clue_is_held(self):
        """The casket is outside the ownership check, so this must work."""
        save = player(inventory={"Casket (easy)": 1, "Clue scroll (easy)": 1})
        opened, ok, _info = open_casket_pure(save, "easy", lambda: 0.9)
        self.assertTrue(ok)
        self.assertNotIn("Casket (easy)", opened["inventory"])
        self.assertEqual(opened["inventory"]["Clue scroll (easy)"], 1)

    def test_every_casket_reward_is_reachable_through_a_real_trail(self):
        """No reward row may be gated on a state a player cannot reach.

        Each row is driven by steering the rolls onto it, but the state it is
        rolled from is always a casket a completed trail actually produced.
        """
        rows = tuple(TREASURE_TRAILS_EASY_RARE_REWARDS) + tuple(
            TREASURE_TRAILS_EASY_STANDARD_REWARDS
        )
        for row in rows:
            with self.subTest(item=row["item"]):
                rare = row in TREASURE_TRAILS_EASY_RARE_REWARDS
                table = (
                    TREASURE_TRAILS_EASY_RARE_REWARDS
                    if rare
                    else TREASURE_TRAILS_EASY_STANDARD_REWARDS
                )
                index = table.index(row)
                # Reach the casket by finishing a real one-step trail first.
                started, ok, _info = read_clue_scroll_pure(
                    player(inventory={"Clue scroll (easy)": 1}), "easy", lambda: 0.0
                )
                self.assertTrue(ok)
                finished, ok, result = apply_treasure_trail_review_pure(started)
                self.assertTrue(ok)
                self.assertTrue(result["terminal"])

                # One draw picks the number of spots, then three per spot:
                # which table, which row, and where in its quantity range.
                per_spot = (
                    0.0 if rare else 0.99,
                    (index + 0.5) / len(table),
                    0.0,
                )
                opened, ok, info = open_casket_pure(
                    finished,
                    "easy",
                    _draws((0.0,) + per_spot * TREASURE_TRAILS_EASY_REWARD_SPOTS[1]),
                )
                self.assertTrue(ok, info)
                self.assertGreaterEqual(
                    int(opened["inventory"].get(str(row["item"]), 0)),
                    int(row["minimum"]),
                )
                self.assertEqual(info["reward_spots"], TREASURE_TRAILS_EASY_REWARD_SPOTS[0])
                self.assertEqual(info["rare_hits"], 2 if rare else 0)

    def test_the_casket_rolls_between_two_and_four_reward_spots(self):
        spots = set()
        for draw in (0.0, 0.5, 0.99):
            _opened, ok, info = open_casket_pure(
                player(inventory={"Casket (easy)": 1}),
                "easy",
                _draws((draw,) + (0.99, 0.0, 0.0) * TREASURE_TRAILS_EASY_REWARD_SPOTS[1]),
            )
            self.assertTrue(ok)
            spots.add(info["reward_spots"])
        self.assertEqual(spots, {2, 3, 4})

    def test_an_unimplemented_tier_casket_is_refused_rather_than_rolled(self):
        for tier in set(CASKET_ITEMS) - set(IMPLEMENTED_CLUE_TIERS):
            with self.subTest(tier=tier):
                save = player(inventory={CASKET_ITEMS[tier]: 1})
                _updated, ok, info = open_casket_pure(save, tier)
                self.assertFalse(ok)
                self.assertIn("not built yet", info["reason"])


class PersistenceTest(unittest.TestCase):
    def test_a_corrupt_trail_is_discarded_rather_than_trusted(self):
        state = sanitize_treasure_trails_state_pure(
            {"treasure_trail": {"tier": "easy", "steps": ["not_a_step"], "index": 9}}
        )
        self.assertEqual(state["treasure_trail"], {})

    def test_a_step_cursor_past_the_end_is_pulled_back_into_range(self):
        state = sanitize_treasure_trails_state_pure(
            {
                "treasure_trail": {
                    "tier": "easy",
                    "steps": ["simple_port_sarim_sailor", "map_lumberyard_crate"],
                    "index": 99,
                }
            }
        )
        self.assertEqual(state["treasure_trail"]["index"], 1)

    def test_a_trail_is_dropped_when_another_activity_owns_the_session(self):
        state = sanitize_treasure_trails_state_pure(
            {
                "activity_session": {"active_id": "tzhaar_fight_pit"},
                "treasure_trail": {
                    "tier": "easy",
                    "steps": ["simple_port_sarim_sailor"],
                    "index": 0,
                },
            }
        )
        self.assertEqual(state["treasure_trail"], {})

    def test_a_trail_in_an_unimplemented_tier_is_discarded(self):
        state = sanitize_treasure_trails_state_pure(
            {"treasure_trail": {"tier": "elite", "steps": ["simple_port_sarim_sailor"]}}
        )
        self.assertEqual(state["treasure_trail"], {})


class CommandDispatchTest(unittest.TestCase):
    def test_an_unknown_command_changes_nothing(self):
        save = player(inventory={"Clue scroll (easy)": 1})
        updated, ok, info = apply_treasure_trails_command_pure(save, "solve_for_me", {})
        self.assertFalse(ok)
        self.assertIn("Unknown Treasure Trails command", info["reason"])
        self.assertEqual(updated["inventory"], save["inventory"])

    def test_read_follow_and_open_run_end_to_end_through_the_dispatcher(self):
        save = player(inventory={"Clue scroll (easy)": 1})
        started, ok, _info = apply_treasure_trails_command_pure(
            save, "read", {"tier": "easy"}, lambda: 0.0
        )
        self.assertTrue(ok)
        while started["treasure_trail"]:
            started, ok, _result = apply_treasure_trail_review_pure(started)
            self.assertTrue(ok)
        self.assertEqual(started["inventory"]["Casket (easy)"], 1)
        opened, ok, info = apply_treasure_trails_command_pure(
            started, "open_casket", {"tier": "easy"}, lambda: 0.9
        )
        self.assertTrue(ok)
        self.assertTrue(info["rewards"])
        self.assertEqual(opened["treasure_trails_caskets_opened"], 1)


if __name__ == "__main__":
    unittest.main()
