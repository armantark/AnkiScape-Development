"""Daily Challenges: the period five-slot queue, credit, hand-in and rewards.

The failure this family exists to avoid is on record: an earlier AnkiScape note
gave the Challenge System a skip/reroll action that the cutoff revision never
mentions. So the queue tests here assert what the revision says — five slots,
one new challenge per day, oldest-first displacement, one pinned task, per-skill
blocks only for maxed skills — rather than what any single code path happens to
do.

Most reward tests start from `_finished`, which writes the finished state
directly. That is deliberate — it isolates one reward rule per test — but it
proves nothing about reachability, so `RewardsThroughRealGameplayTest` drives the
mystery bag and the lamp from a real assignment through real credit to the claim
and the reward's own use.
"""

import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.daily_challenges_data import (
    DAILY_CHALLENGE_ACTIVE_LIMIT,
    DAILY_CHALLENGE_DATA,
    DAILY_CHALLENGE_MYSTERY_BAG_ITEM,
    DAILY_CHALLENGE_REVIEW_DAY,
    DAILY_CHALLENGE_XP_LAMP_ITEM,
)
from ankiscape.logic.daily_challenges_logic import (
    advance_daily_challenges_day_pure,
    apply_daily_challenges_command_pure,
    claim_daily_challenge_pure,
    credit_daily_challenge_progress_pure,
    daily_challenges_view_pure,
    default_daily_challenges_state_pure,
    eligible_daily_challenge_ids_pure,
    open_challenge_mystery_bag_pure,
    pin_daily_challenge_pure,
    rub_challenge_xp_lamp_pure,
    sanitize_daily_challenges_state_pure,
    set_daily_challenge_skill_block_pure,
)


def player(day_reviews=0, **changes):
    data = {
        "attack_level": 1,
        "strength_level": 1,
        "defense_level": 1,
        "constitution_level": 10,
        "ranged_level": 1,
        "magic_level": 1,
        "prayer_level": 1,
        "summoning_level": 1,
        "mining_level": 1,
        "cooking_level": 1,
        "fishing_level": 1,
        "firemaking_level": 1,
        "woodcutting_level": 1,
        "inventory": {},
        "shop_market_clock": {"version": 1, "answered_cards": day_reviews, "market_tick": 0},
    }
    data.update(default_daily_challenges_state_pure())
    data.update(changes)
    return data


def _advance_days(data, days, draw=None):
    """Play forward `days` review-days, one assignment per day."""
    for day in range(1, days + 1):
        data = dict(data)
        data["shop_market_clock"] = {
            "version": 1,
            "answered_cards": day * DAILY_CHALLENGE_REVIEW_DAY,
            "market_tick": 0,
        }
        data, _events = advance_daily_challenges_day_pure(data, draw or (lambda: 0.0))
    return data


class ChallengeQueueTest(unittest.TestCase):
    def test_no_challenge_arrives_before_a_full_review_day(self):
        data = player(DAILY_CHALLENGE_REVIEW_DAY - 1)
        updated, events = advance_daily_challenges_day_pure(data, lambda: 0.0)
        self.assertEqual(events["assigned"], ())
        self.assertEqual(updated["daily_challenges"], [])

    def test_one_challenge_arrives_per_review_day(self):
        data = _advance_days(player(), 3)
        self.assertEqual(len(data["daily_challenges"]), 3)
        self.assertEqual(data["daily_challenge_assigned"], 3)
        self.assertEqual([row["day"] for row in data["daily_challenges"]], [1, 2, 3])

    def test_the_queue_never_exceeds_the_period_slot_limit(self):
        data = _advance_days(player(), DAILY_CHALLENGE_ACTIVE_LIMIT + 2)
        self.assertEqual(len(data["daily_challenges"]), DAILY_CHALLENGE_ACTIVE_LIMIT)

    def test_a_sixth_challenge_removes_the_oldest_not_the_newest(self):
        five = _advance_days(player(), DAILY_CHALLENGE_ACTIVE_LIMIT)
        oldest = five["daily_challenges"][0]["instance_id"]
        newest = five["daily_challenges"][-1]["instance_id"]
        six = _advance_days(five, DAILY_CHALLENGE_ACTIVE_LIMIT + 1)
        held = [row["instance_id"] for row in six["daily_challenges"]]
        self.assertNotIn(oldest, held)
        self.assertIn(newest, held)

    def test_an_expired_challenge_pays_nothing_even_when_it_was_finished(self):
        """"the Quartermaster will NOT reward them for their efforts"."""
        data = _advance_days(player(), 1)
        finished = data["daily_challenges"][0]
        spec = DAILY_CHALLENGE_DATA[finished["challenge_id"]]
        finished["progress"] = int(spec["required"])
        data = _advance_days(data, DAILY_CHALLENGE_ACTIVE_LIMIT + 1)

        self.assertNotIn(
            finished["instance_id"],
            [row["instance_id"] for row in data["daily_challenges"]],
        )
        self.assertEqual(data["daily_challenge_completed"], 0)
        self.assertEqual(data["daily_challenge_expired"], 1)
        _updated, ok, info = claim_daily_challenge_pure(data, finished["instance_id"])
        self.assertFalse(ok)
        self.assertIn("no longer on the noticeboard", info["reason"])

    def test_a_challenge_above_the_players_level_is_never_assigned(self):
        """"Challenges ... are always possible at your current skill levels"."""
        low = player()
        self.assertNotIn("woodcutting_oak_logs", eligible_daily_challenge_ids_pure(low))
        high = player(woodcutting_level=15)
        self.assertIn("woodcutting_oak_logs", eligible_daily_challenge_ids_pure(high))

    def test_assignment_gives_each_eligible_skill_one_equal_interval(self):
        """The cutoff guide states one-in-four for one desired skill out of four."""
        data = player(DAILY_CHALLENGE_REVIEW_DAY)
        pool = eligible_daily_challenge_ids_pure(data)
        skills = tuple(
            dict.fromkeys(DAILY_CHALLENGE_DATA[row]["skill"] for row in pool)
        )
        self.assertGreater(
            sum(DAILY_CHALLENGE_DATA[row]["skill"] == "mining" for row in pool),
            1,
        )

        for index, skill in enumerate(skills):
            assigned, events = advance_daily_challenges_day_pure(
                data,
                lambda index=index: (index + 0.5) / len(skills),
            )
            challenge_id = events["assigned"][0]["challenge_id"]
            self.assertEqual(DAILY_CHALLENGE_DATA[challenge_id]["skill"], skill)
            self.assertEqual(len(assigned["daily_challenges"]), 1)

    def test_only_one_task_can_be_pinned_at_a_time(self):
        data = _advance_days(player(), 2)
        first, second = (row["instance_id"] for row in data["daily_challenges"])
        pinned, ok, _info = pin_daily_challenge_pure(data, first)
        self.assertTrue(ok)
        repinned, ok, _info = pin_daily_challenge_pure(pinned, second)
        self.assertTrue(ok)
        self.assertEqual(repinned["daily_challenge_pinned"], second)

    def test_pinning_a_challenge_that_is_gone_is_refused(self):
        _updated, ok, info = pin_daily_challenge_pure(player(), "rampage_mk_i-9")
        self.assertFalse(ok)
        self.assertIn("no longer on the noticeboard", info["reason"])

    def test_displacing_the_pinned_task_unpins_it(self):
        data = _advance_days(player(), 1)
        pinned_id = data["daily_challenges"][0]["instance_id"]
        data, _ok, _info = pin_daily_challenge_pure(data, pinned_id)
        data = _advance_days(data, DAILY_CHALLENGE_ACTIVE_LIMIT + 1)
        self.assertEqual(data["daily_challenge_pinned"], "")


class SkillBlockTest(unittest.TestCase):
    def test_a_skill_below_99_cannot_be_blocked(self):
        """"players may choose not to receive new challenges in their max level
        skills. This is not a blanket turn off"."""
        _updated, ok, info = set_daily_challenge_skill_block_pure(player(), "mining", True)
        self.assertFalse(ok)
        self.assertIn("only blocks maxed skills", info["reason"])

    def test_a_maxed_skill_can_be_blocked_and_stops_being_assigned(self):
        maxed = player(mining_level=99)
        blocked, ok, _info = set_daily_challenge_skill_block_pure(maxed, "mining", True)
        self.assertTrue(ok)
        self.assertEqual(blocked["daily_challenge_blocked_skills"], ["mining"])
        pool = eligible_daily_challenge_ids_pure(blocked)
        self.assertEqual(
            [
                challenge_id
                for challenge_id in pool
                if DAILY_CHALLENGE_DATA[challenge_id]["skill"] == "mining"
            ],
            [],
        )

    def test_a_block_can_be_lifted_again(self):
        maxed = player(mining_level=99)
        blocked, _ok, _info = set_daily_challenge_skill_block_pure(maxed, "mining", True)
        lifted, ok, _info = set_daily_challenge_skill_block_pure(blocked, "mining", False)
        self.assertTrue(ok)
        self.assertEqual(lifted["daily_challenge_blocked_skills"], [])


class CreditTest(unittest.TestCase):
    def _with(self, challenge_id, **changes):
        data = player(**changes)
        data["daily_challenges"] = [
            {
                "instance_id": f"{challenge_id}-1",
                "challenge_id": challenge_id,
                "day": 1,
                "progress": 0,
                "credited": {},
            }
        ]
        return data

    def test_gathering_the_named_item_advances_the_challenge(self):
        data = self._with("mining_copper_ore")
        updated, events = credit_daily_challenge_progress_pure(
            data, "mining", "copper", output_items={"Copper ore": 3}
        )
        self.assertEqual(updated["daily_challenges"][0]["progress"], 3)
        self.assertEqual(updated["daily_challenges"][0]["credited"], {"Copper ore": 3})
        self.assertEqual(events["credited"][0]["required"], 25)

    def test_a_different_item_in_the_same_skill_credits_nothing(self):
        data = self._with("mining_copper_ore")
        updated, events = credit_daily_challenge_progress_pure(
            data, "mining", "tin", output_items={"Tin ore": 5}
        )
        self.assertEqual(updated["daily_challenges"][0]["progress"], 0)
        self.assertEqual(events["credited"], ())

    def test_a_multi_item_challenge_accepts_any_of_its_items(self):
        data = self._with("cooking_seafood_buffet")
        updated, _events = credit_daily_challenge_progress_pure(
            data, "cooking", "cook_sardine", output_items={"Sardine": 2}
        )
        updated, _events = credit_daily_challenge_progress_pure(
            updated, "cooking", "cook_shrimps", output_items={"Shrimps": 4}
        )
        self.assertEqual(updated["daily_challenges"][0]["progress"], 6)
        self.assertEqual(
            updated["daily_challenges"][0]["credited"], {"Sardine": 2, "Shrimps": 4}
        )

    def test_an_action_challenge_counts_the_action_not_its_output(self):
        data = self._with("firemaking_normal_logs")
        updated, _events = credit_daily_challenge_progress_pure(
            data, "firemaking", "logs", output_items={"Ashes": 1}
        )
        self.assertEqual(updated["daily_challenges"][0]["progress"], 1)
        self.assertEqual(updated["daily_challenges"][0]["credited"], {})

    def test_a_kill_below_the_named_combat_level_does_not_count(self):
        data = self._with("rampage_mk_i")
        low, _events = credit_daily_challenge_progress_pure(
            data, "combat", "chicken", kills=1, enemy_combat_level=1
        )
        self.assertEqual(low["daily_challenges"][0]["progress"], 0)
        high, _events = credit_daily_challenge_progress_pure(
            data, "combat", "goblin_level_2_unarmed", kills=1, enemy_combat_level=2
        )
        self.assertEqual(high["daily_challenges"][0]["progress"], 1)

    def test_credit_never_exceeds_the_required_quantity(self):
        data = self._with("cooking_chicken")
        updated, _events = credit_daily_challenge_progress_pure(
            data, "cooking", "cook_chicken", output_items={"Cooked chicken": 99}
        )
        instance = updated["daily_challenges"][0]
        self.assertEqual(instance["progress"], 3)
        self.assertEqual(instance["credited"], {"Cooked chicken": 3})

    def test_two_active_challenges_for_the_same_work_both_advance(self):
        data = self._with("cooking_chicken")
        data["daily_challenges"].append(
            {
                "instance_id": "cooking_seafood_buffet-2",
                "challenge_id": "cooking_seafood_buffet",
                "day": 2,
                "progress": 0,
                "credited": {},
            }
        )
        updated, _events = credit_daily_challenge_progress_pure(
            data, "cooking", "cook_crayfish", output_items={"Crayfish": 2}
        )
        progress = {row["challenge_id"]: row["progress"] for row in updated["daily_challenges"]}
        self.assertEqual(progress["cooking_chicken"], 0)
        self.assertEqual(progress["cooking_seafood_buffet"], 2)


def _finished(challenge_id, inventory=None, **changes):
    """A synthetic finished challenge, for isolating one reward rule at a time.

    This writes maximum progress, credited items and inventory straight into the
    save. It says nothing about whether real gameplay can reach that state;
    `RewardsThroughRealGameplayTest` is what covers that.
    """
    data = player(**changes)
    spec = DAILY_CHALLENGE_DATA[challenge_id]
    credited = {}
    if spec["credit"]["kind"] == "output_item":
        credited = {spec["credit"]["items"][0]: int(spec["required"])}
    data["daily_challenges"] = [
        {
            "instance_id": f"{challenge_id}-1",
            "challenge_id": challenge_id,
            "day": 1,
            "progress": int(spec["required"]),
            "credited": credited,
        }
    ]
    data["inventory"] = dict(inventory if inventory is not None else credited)
    return data


class HandInAndRewardTest(unittest.TestCase):
    def test_an_unfinished_challenge_cannot_be_handed_in(self):
        data = _finished("mining_copper_ore")
        data["daily_challenges"][0]["progress"] = 1
        _updated, ok, info = claim_daily_challenge_pure(data, "mining_copper_ore-1")
        self.assertFalse(ok)
        self.assertIn("1/25", info["reason"])

    def test_a_hand_in_without_the_items_is_refused_and_names_the_shortfall(self):
        data = _finished("cooking_chicken", inventory={"Cooked chicken": 1})
        updated, ok, info = claim_daily_challenge_pure(data, "cooking_chicken-1")
        self.assertFalse(ok)
        self.assertEqual(info["missing"], {"Cooked chicken": 2})
        self.assertEqual(len(updated["daily_challenges"]), 1)

    def test_a_hand_in_takes_the_items_and_pays_bonus_xp_and_a_mystery_bag(self):
        data = _finished("cooking_chicken")
        updated, ok, info = claim_daily_challenge_pure(
            data, "cooking_chicken-1", {"Cooked chicken": 50}
        )
        self.assertTrue(ok)
        self.assertNotIn("Cooked chicken", updated["inventory"])
        self.assertEqual(
            updated["cooking_exp"],
            float(DAILY_CHALLENGE_DATA["cooking_chicken"]["reward_xp"]),
        )
        self.assertEqual(updated["inventory"][DAILY_CHALLENGE_MYSTERY_BAG_ITEM], 1)
        self.assertEqual(info["mystery_bag"], 150)
        self.assertEqual(updated["daily_challenges"], [])
        self.assertEqual(updated["daily_challenge_completed"], 1)

    def test_a_no_hand_in_challenge_pays_xp_without_taking_anything(self):
        data = _finished("firemaking_normal_logs", inventory={"Logs": 4})
        updated, ok, _info = claim_daily_challenge_pure(data, "firemaking_normal_logs-1")
        self.assertTrue(ok)
        self.assertEqual(updated["inventory"], {"Logs": 4})
        self.assertEqual(
            updated["firemaking_exp"],
            float(DAILY_CHALLENGE_DATA["firemaking_normal_logs"]["reward_xp"]),
        )

    def test_a_combat_challenge_pays_an_xp_lamp_instead_of_a_fixed_skill(self):
        """"players may be given a Challenge XP Lamp from which to choose which
        skill to earn experience in"."""
        data = _finished("rampage_mk_i")
        updated, ok, info = claim_daily_challenge_pure(data, "rampage_mk_i-1")
        self.assertTrue(ok)
        self.assertEqual(updated["inventory"][DAILY_CHALLENGE_XP_LAMP_ITEM], 1)
        self.assertEqual(
            info["xp_lamp"], DAILY_CHALLENGE_DATA["rampage_mk_i"]["reward_xp"]
        )
        self.assertNotIn("xp_rewards", info)

    def test_the_lamp_refuses_a_skill_it_never_offered(self):
        data = _finished("rampage_mk_i")
        claimed, _ok, _info = claim_daily_challenge_pure(data, "rampage_mk_i-1")
        _updated, ok, info = rub_challenge_xp_lamp_pure(claimed, "mining")
        self.assertFalse(ok)
        self.assertIn("cannot be spent in that skill", info["reason"])

    def test_the_mystery_bag_pays_back_the_value_of_what_was_handed_in(self):
        data = _finished("mining_copper_ore")
        claimed, _ok, _info = claim_daily_challenge_pure(
            data, "mining_copper_ore-1", {"Copper ore": 8}
        )
        opened, ok, info = open_challenge_mystery_bag_pure(claimed)
        self.assertTrue(ok)
        self.assertEqual(info["coins"], 25 * 8)
        self.assertEqual(opened["inventory"]["Coins"], 200)
        self.assertNotIn(DAILY_CHALLENGE_MYSTERY_BAG_ITEM, opened["inventory"])

    def test_opening_a_bag_you_do_not_have_is_refused(self):
        _updated, ok, info = open_challenge_mystery_bag_pure(player())
        self.assertFalse(ok)
        self.assertIn("no Challenge Mystery Bag", info["reason"])

    def test_rubbing_a_lamp_you_do_not_have_is_refused(self):
        _updated, ok, info = rub_challenge_xp_lamp_pure(player(), "strength")
        self.assertFalse(ok)
        self.assertIn("no Challenge XP Lamp", info["reason"])


class RewardsThroughRealGameplayTest(unittest.TestCase):
    """Both rewards, reached only through assignment, credit and hand-in.

    Nothing here writes progress, credited items or a reward ledger directly. The
    one thing these tests do choose is which challenge the day's two-stage draw
    lands on, because a player cannot pick either.
    """

    def _assign(self, data, challenge_id, day=1):
        data = dict(data)
        data["shop_market_clock"] = {
            "version": 1,
            "answered_cards": day * DAILY_CHALLENGE_REVIEW_DAY,
            "market_tick": 0,
        }
        pool = eligible_daily_challenge_ids_pure(data)
        self.assertIn(challenge_id, pool)
        skills = tuple(
            dict.fromkeys(DAILY_CHALLENGE_DATA[row]["skill"] for row in pool)
        )
        skill = DAILY_CHALLENGE_DATA[challenge_id]["skill"]
        skill_index = skills.index(skill)
        skill_pool = tuple(
            row for row in pool if DAILY_CHALLENGE_DATA[row]["skill"] == skill
        )
        challenge_index = skill_pool.index(challenge_id)
        roll = (
            skill_index + (challenge_index + 0.5) / len(skill_pool)
        ) / len(skills)
        data, events = advance_daily_challenges_day_pure(
            data, lambda: roll
        )
        self.assertEqual(
            [row["challenge_id"] for row in events["assigned"]], [challenge_id]
        )
        return data, events["assigned"][0]["instance_id"]

    def test_a_cooking_challenge_reaches_its_mystery_bag_and_opens_it(self):
        data, instance_id = self._assign(player(), "cooking_chicken")
        required = int(DAILY_CHALLENGE_DATA["cooking_chicken"]["required"])
        for _cooked in range(required):
            # Each real cook credits the challenge and leaves the food behind;
            # the inventory gain belongs to the Cooking family, not to this one.
            data, events = credit_daily_challenge_progress_pure(
                data, "cooking", "cook_chicken", output_items={"Cooked chicken": 1}
            )
            self.assertEqual(len(events["credited"]), 1)
            inventory = dict(data["inventory"])
            inventory["Cooked chicken"] = inventory.get("Cooked chicken", 0) + 1
            data["inventory"] = inventory
        self.assertEqual(data["daily_challenges"][0]["progress"], required)

        claimed, ok, info = claim_daily_challenge_pure(
            data, instance_id, {"Cooked chicken": 50}
        )
        self.assertTrue(ok, info)
        self.assertNotIn("Cooked chicken", claimed["inventory"])
        self.assertEqual(claimed["inventory"][DAILY_CHALLENGE_MYSTERY_BAG_ITEM], 1)
        self.assertEqual(claimed["daily_challenges"], [])

        opened, ok, info = open_challenge_mystery_bag_pure(claimed)
        self.assertTrue(ok, info)
        self.assertEqual(info["coins"], 50 * required)
        self.assertEqual(opened["inventory"]["Coins"], 50 * required)
        self.assertNotIn(DAILY_CHALLENGE_MYSTERY_BAG_ITEM, opened["inventory"])

    def test_a_combat_challenge_reaches_its_xp_lamp_and_rubs_it(self):
        data, instance_id = self._assign(player(), "rampage_mk_i")
        required = int(DAILY_CHALLENGE_DATA["rampage_mk_i"]["required"])
        for _kill in range(required):
            data, events = credit_daily_challenge_progress_pure(
                data, "combat", "attack", kills=1, enemy_combat_level=2
            )
            self.assertEqual(len(events["credited"]), 1)
        self.assertEqual(data["daily_challenges"][0]["progress"], required)

        claimed, ok, info = claim_daily_challenge_pure(data, instance_id)
        self.assertTrue(ok, info)
        self.assertEqual(claimed["inventory"][DAILY_CHALLENGE_XP_LAMP_ITEM], 1)
        self.assertEqual(claimed["daily_challenges"], [])

        rubbed, ok, info = rub_challenge_xp_lamp_pure(claimed, "strength")
        self.assertTrue(ok, info)
        self.assertEqual(
            rubbed["strength_exp"],
            float(DAILY_CHALLENGE_DATA["rampage_mk_i"]["reward_xp"]),
        )
        self.assertNotIn(DAILY_CHALLENGE_XP_LAMP_ITEM, rubbed["inventory"])


class PersistenceTest(unittest.TestCase):
    def test_a_corrupt_save_is_repaired_rather_than_trusted(self):
        state = sanitize_daily_challenges_state_pure(
            {
                "daily_challenges": [
                    {"challenge_id": "not_a_challenge", "progress": 5},
                    {"challenge_id": "mining_clay", "progress": "999", "day": 2},
                ],
                "daily_challenge_pinned": "gone",
                "daily_challenge_blocked_skills": ["mining", "not_a_skill", "mining"],
                "daily_challenge_day": -4,
            }
        )
        self.assertEqual(len(state["daily_challenges"]), 1)
        self.assertEqual(state["daily_challenges"][0]["progress"], 42)
        self.assertEqual(state["daily_challenge_pinned"], "")
        self.assertEqual(state["daily_challenge_blocked_skills"], ["mining"])
        self.assertEqual(state["daily_challenge_day"], 0)

    def test_an_overlong_queue_is_trimmed_from_the_oldest_end(self):
        rows = [
            {
                "instance_id": f"mining_clay-{day}",
                "challenge_id": "mining_clay",
                "day": day,
                "progress": 0,
            }
            for day in range(DAILY_CHALLENGE_ACTIVE_LIMIT + 3)
        ]
        state = sanitize_daily_challenges_state_pure({"daily_challenges": rows})
        self.assertEqual(len(state["daily_challenges"]), DAILY_CHALLENGE_ACTIVE_LIMIT)
        self.assertEqual(state["daily_challenges"][-1]["day"], DAILY_CHALLENGE_ACTIVE_LIMIT + 2)

    def test_reward_ledgers_never_outnumber_the_items_they_describe(self):
        state = sanitize_daily_challenges_state_pure(
            {
                "inventory": {DAILY_CHALLENGE_MYSTERY_BAG_ITEM: 1},
                "daily_challenge_bag_values": [10, 20, 30],
                "daily_challenge_lamp_xp": [40],
            }
        )
        self.assertEqual(state["daily_challenge_bag_values"], [10])
        self.assertEqual(state["daily_challenge_lamp_xp"], [])


class ViewTest(unittest.TestCase):
    def test_the_view_publishes_the_queue_rule_so_no_panel_re_derives_it(self):
        data = _advance_days(player(), DAILY_CHALLENGE_ACTIVE_LIMIT)
        view = daily_challenges_view_pure(data)
        self.assertEqual(view["slots_used"], DAILY_CHALLENGE_ACTIVE_LIMIT)
        self.assertEqual(view["slot_limit"], DAILY_CHALLENGE_ACTIVE_LIMIT)
        self.assertEqual(
            view["next_assignment_displaces"], data["daily_challenges"][0]["instance_id"]
        )
        self.assertEqual(view["reviews_until_next_challenge"], DAILY_CHALLENGE_REVIEW_DAY)

    def test_a_queue_below_the_limit_displaces_nothing(self):
        view = daily_challenges_view_pure(_advance_days(player(), 1))
        self.assertEqual(view["next_assignment_displaces"], "")
        self.assertEqual(view["next_assignment_displaces_name"], "")

    def test_the_view_reports_why_a_finished_hand_in_cannot_be_claimed(self):
        data = _finished("cooking_chicken", inventory={})
        row = daily_challenges_view_pure(data)["rows"][0]
        self.assertTrue(row["complete"])
        self.assertFalse(row["can_claim"])
        self.assertIn("3 Cooked chicken", row["claim_blocked_reason"])

    def test_every_challenge_in_the_catalog_can_appear_on_the_noticeboard(self):
        """No catalog row may be unreachable: each one must be assignable to a
        player who meets its level requirement."""
        capable = player(
            mining_level=99,
            cooking_level=99,
            fishing_level=99,
            firemaking_level=99,
            woodcutting_level=99,
        )
        self.assertEqual(
            sorted(eligible_daily_challenge_ids_pure(capable)),
            sorted(DAILY_CHALLENGE_DATA),
        )

    def test_the_skill_block_rows_report_which_skills_may_be_blocked(self):
        view = daily_challenges_view_pure(player(mining_level=99))
        blockable = {row["skill_id"] for row in view["skill_blocks"] if row["can_block"]}
        self.assertEqual(blockable, {"mining"})


class CommandDispatchTest(unittest.TestCase):
    def test_an_unknown_command_changes_nothing(self):
        data = _advance_days(player(), 1)
        updated, ok, info = apply_daily_challenges_command_pure(data, "reroll", {})
        self.assertFalse(ok)
        self.assertIn("Unknown Daily Challenge command", info["reason"])
        self.assertEqual(updated["daily_challenges"], data["daily_challenges"])

    def test_every_command_the_panel_sends_is_dispatched(self):
        data = _finished("mining_copper_ore")
        pinned, ok, _info = apply_daily_challenges_command_pure(
            data, "pin", {"instance_id": "mining_copper_ore-1"}
        )
        self.assertTrue(ok)
        claimed, ok, _info = apply_daily_challenges_command_pure(
            pinned, "claim", {"instance_id": "mining_copper_ore-1"}, {"Copper ore": 3}
        )
        self.assertTrue(ok)
        self.assertEqual(claimed["daily_challenge_pinned"], "")
        opened, ok, info = apply_daily_challenges_command_pure(claimed, "open_bag", {})
        self.assertTrue(ok)
        self.assertEqual(info["coins"], 75)
        blocked, ok, _info = apply_daily_challenges_command_pure(
            {**opened, "mining_level": 99}, "set_skill_block", {"skill_id": "mining", "blocked": True}
        )
        self.assertTrue(ok)
        self.assertEqual(blocked["daily_challenge_blocked_skills"], ["mining"])


if __name__ == "__main__":
    unittest.main()
