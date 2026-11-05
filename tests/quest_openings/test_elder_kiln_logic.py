"""The hatching exercise's reducers, step order, waiting and its single proof producer."""

import copy
import random
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import QUEST_DATA
from ankiscape.data.quest.elder_kiln import BANDS, SPELL_DELTAS, SPELL_IDS, STATE_KEY
from ankiscape.logic_pure.logic_pure_quest import (
    can_attempt_quest_review_pure, quest_current_stage_blockers_pure, start_quest_pure,
)
from ankiscape.logic_pure.quest import elder_kiln as kiln
from ankiscape.logic_pure.quest.eligibility import quest_eligibility_reasons_pure
from ankiscape.logic_pure.quest.elder_kiln_state import default_elder_kiln_state_pure, transient_defaults_pure
from tests.quest_openings.test_elder_kiln_data import PROOF, QUEST_ID, player


class CountingRng:
    def __init__(self, *values):
        self.values, self.calls = list(values), 0

    def __call__(self):
        self.calls += 1
        return self.values.pop(0) if self.values else 0.0


def attempt(**fields):
    """A quiet live attempt: both Mejs far into cooldown and no marker boundary next."""
    state = {"phase": "active", "heat": 30, "progress": 50, "band": 1, "steps": 1, "attempt": 1,
             "ak_phase": "cooldown", "ak_remaining": 50, "jeh_phase": "cooldown", "jeh_remaining": 50}
    state.update(fields)
    return state


def kinds(events):
    return [event[0] for event in events]


def started(**kwargs):
    data, ok = start_quest_pure(player(**kwargs), QUEST_ID, QUEST_DATA)
    assert ok
    return data


def command(data, name, rng=None):
    return kiln.apply_elder_kiln_command_pure(data, QUEST_ID, name, rng or CountingRng())


def assert_detached_refusal(test, result, data):
    """A refusal returns equal data that shares nothing the caller could change."""
    test.assertEqual(result, data)
    before = copy.deepcopy(data)
    result.setdefault(STATE_KEY, {})["heat"] = -1
    result.setdefault("quest_action_proofs", []).append("forged")
    result.setdefault("inventory", {})["Fire rune"] = 999
    result.setdefault("quests", {}).setdefault(QUEST_ID, {})["progress"] = 7
    test.assertEqual(data, before)


def best_command(state):
    """A player who aims for the middle of the current band."""
    low, high = BANDS[state["band"] - 1]
    gap = (low + high) // 2 - state["heat"]
    options = {f"cast:{spell}": delta for spell, delta in zip(SPELL_IDS, SPELL_DELTAS)}
    options["wait_step"] = 0
    return min(options, key=lambda name: abs(gap - options[name]))


class StepTest(unittest.TestCase):
    def test_every_spell_applies_its_delta_then_one_step(self):
        for spell, delta in zip(SPELL_IDS, SPELL_DELTAS):
            with self.subTest(spell=spell):
                before = attempt(heat=50, band=2)
                after, _events = kiln.cast_elder_kiln_spell_pure(before, spell, CountingRng())
                self.assertEqual(after["heat"], 50 + delta - 1)
                self.assertEqual(after["steps"], 2)

    def test_each_band_is_inclusive_and_its_neighbours_are_outside(self):
        for band, (low, high) in enumerate(BANDS, 1):
            for heat, inside in ((low - 1, False), (low, True), (high, True), (high + 1, False)):
                with self.subTest(band=band, heat=heat):
                    after, _ = kiln.elder_kiln_step_pure(attempt(band=band, heat=heat), CountingRng())
                    self.assertEqual(after["progress"], 51 if inside else 49)

    def test_heat_and_progress_clamp(self):
        hot, _ = kiln.cast_elder_kiln_spell_pure(attempt(heat=98), "fire_wave", CountingRng())
        self.assertEqual(hot["heat"], 99)
        cold, _ = kiln.cast_elder_kiln_spell_pure(attempt(heat=3), "water_wave", CountingRng())
        self.assertEqual(cold["heat"], 0)
        floor, _ = kiln.elder_kiln_step_pure(attempt(phase="preparing", progress=0, heat=0), CountingRng())
        self.assertEqual((floor["phase"], floor["progress"], floor["heat"]), ("preparing", 0, 0))

    def test_natural_cooling_after_each_nonterminal_step(self):
        after, events = kiln.elder_kiln_step_pure(attempt(heat=35), CountingRng())
        self.assertEqual((after["heat"], after["progress"], after["steps"]), (34, 51, 2))
        self.assertEqual(events, ())

    def test_initial_zero_waits_until_progress_first_becomes_positive(self):
        state = dict(default_elder_kiln_state_pure(), phase="preparing", attempt=1)
        for step in range(1, 5):
            state, events = kiln.elder_kiln_step_pure(state, CountingRng())
            self.assertEqual((state["phase"], state["progress"], state["steps"]), ("preparing", 0, step))
        # Mej-Ak's first cast is due on the fifth step and lands below the marker.
        state, events = kiln.elder_kiln_step_pure(state, CountingRng())
        self.assertEqual(kinds(events), ["helper_impact", "activated"])
        self.assertEqual((state["phase"], state["progress"], state["heat"]), ("active", 1, 24))

    def test_active_one_to_zero_fails_and_stops_the_step(self):
        rng = CountingRng()
        after, events = kiln.elder_kiln_step_pure(attempt(progress=1, heat=60, steps=19), rng)
        self.assertEqual((after["phase"], after["progress"]), ("failed", 0))
        self.assertEqual((after["heat"], after["steps"], after["band"], rng.calls), (60, 19, 1, 0))
        self.assertEqual(kinds(events), ["failed"])

    def test_hatching_at_one_hundred_is_terminal(self):
        rng = CountingRng()
        after, events = kiln.elder_kiln_step_pure(attempt(progress=99, heat=30, steps=19), rng)
        self.assertEqual((after["phase"], after["progress"], after["heat"], after["steps"], rng.calls),
                         ("hatched", 100, 30, 19, 0))
        self.assertEqual(kinds(events), ["hatched"])

    def test_retry_restores_the_contracted_transient_defaults(self):
        failed = attempt(phase="failed", progress=0, heat=77, band=3, steps=63, attempt=4,
                         ak_phase="warning", ak_remaining=2, jeh_phase="cooldown", jeh_remaining=7)
        retried, events = kiln.retry_elder_kiln_attempt_pure(failed)
        self.assertEqual(retried, {"phase": "preparing", **transient_defaults_pure(), "attempt": 5})
        self.assertEqual(transient_defaults_pure(), {
            "heat": 0, "progress": 0, "band": 1, "steps": 0,
            "ak_phase": "warning", "ak_remaining": 5, "jeh_phase": "delay", "jeh_remaining": 25,
        })
        self.assertEqual(events, (("retried",),))


class HelperTest(unittest.TestCase):
    def test_separate_countdowns_warnings_and_cooldowns(self):
        state = dict(default_elder_kiln_state_pure(), phase="active", attempt=1, progress=50)
        timeline = []
        for _ in range(90):
            # Hold the egg cold and mid-attempt so every due cast lands.
            state, events = kiln.elder_kiln_step_pure(dict(state, heat=0, progress=50), lambda: 0.0)
            timeline.extend((state["steps"], *event) for event in events if event[0].startswith("helper"))
        self.assertEqual([row[:2] for row in timeline if row[2] == "Mej-Ak"],
                         [(5, "helper_impact"), (55, "helper_warning"), (60, "helper_impact")])
        self.assertEqual([row[:2] for row in timeline if row[2] == "Mej-Jeh"],
                         [(25, "helper_warning"), (30, "helper_impact"), (80, "helper_warning"), (85, "helper_impact")])

    def test_helper_adds_heat_only_below_the_current_lower_marker(self):
        low = BANDS[1][0]
        for heat, expected in ((low - 1, "helper_impact"), (low, "helper_skip")):
            with self.subTest(heat=heat):
                state = attempt(band=2, heat=heat, ak_phase="warning", ak_remaining=1)
                after, events = kiln.elder_kiln_step_pure(state, CountingRng())
                self.assertEqual(kinds(events)[0], expected)
                self.assertEqual((after["ak_phase"], after["ak_remaining"]), ("cooldown", 50))
                self.assertEqual(after["heat"], heat + (25 if expected == "helper_impact" else 0) - 1)

    def test_mej_ak_resolves_before_mej_jeh_on_the_same_step(self):
        state = attempt(heat=0, ak_phase="warning", ak_remaining=1, jeh_phase="warning", jeh_remaining=1)
        after, events = kiln.elder_kiln_step_pure(state, CountingRng())
        self.assertEqual(list(events[:2]), [("helper_impact", "Mej-Ak"), ("helper_skip", "Mej-Jeh")])
        self.assertEqual(after["heat"], 24)

    def test_helper_heat_clamps_at_the_top(self):
        state = attempt(band=3, heat=79, ak_phase="warning", ak_remaining=1)
        after, _ = kiln.elder_kiln_step_pure(state, CountingRng())
        self.assertEqual(after["heat"], 99)


class MarkerTest(unittest.TestCase):
    def test_draws_only_on_each_twentieth_step(self):
        rng = CountingRng(0.5, 0.9)
        state = attempt(steps=0, heat=60, progress=60)
        draws = []
        for _ in range(45):
            state, events = kiln.elder_kiln_step_pure(dict(state, heat=60), rng)
            draws.extend((state["steps"], event[1]) for event in events if event[0] == "marker")
        self.assertEqual(draws, [(20, 2), (40, 3)])
        self.assertEqual(rng.calls, 2)

    def test_formula_and_repeated_band(self):
        for value, band in ((0.0, 1), (0.34, 2), (0.67, 3), (0.999999, 3), (1.0, 3)):
            with self.subTest(value=value):
                rng = CountingRng(value)
                after, events = kiln.elder_kiln_step_pure(attempt(steps=19, band=1), rng)
                self.assertEqual((after["band"], rng.calls), (band, 1))
                self.assertIn(("marker", band), events)


class WaitUntilChangeTest(unittest.TestCase):
    def _wait(self, state, rng=None):
        return kiln.wait_elder_kiln_until_change_pure(state, rng or CountingRng())

    def test_each_stopping_condition(self):
        cases = {
            "left_band": (attempt(heat=21), 2),
            "marker": (attempt(heat=60, steps=17), 3),
            "helper_warning": (attempt(heat=60, jeh_phase="delay", jeh_remaining=4), 4),
            "helper_impact": (attempt(heat=0, ak_phase="warning", ak_remaining=3), 3),
            "helper_skip": (attempt(heat=60, ak_phase="warning", ak_remaining=2), 2),
            "failed": (attempt(heat=60, progress=3), 3),
            "hatched": (attempt(heat=36, progress=97), 3),
        }
        for stop, (state, steps) in cases.items():
            with self.subTest(stop=stop):
                start = copy.deepcopy(state)
                after, events = self._wait(state)
                self.assertEqual(state, start)
                self.assertEqual(kinds(events).count(stop), 1)
                self.assertTrue(set(kinds(events)[:-1]).isdisjoint(kiln.WAIT_STOP_EVENTS - {stop}))
                taken = after["steps"] - start["steps"] if after["phase"] not in kiln.TERMINAL_PHASES else steps
                self.assertEqual(taken, steps)

    def test_next_marker_boundary_bounds_the_wait_to_twenty_steps(self):
        rng = CountingRng(0.0)
        after, events = self._wait(attempt(heat=100, band=1, steps=0, progress=60), rng)
        self.assertEqual((after["steps"], rng.calls, kinds(events)), (20, 1, ["marker"]))
        self.assertEqual(after["progress"], 40)

    def test_waiting_never_casts(self):
        after, _ = self._wait(attempt(heat=60, steps=17))
        self.assertEqual(after["heat"], 57)


class CommandTest(unittest.TestCase):
    def test_offer_increments_the_attempt_without_a_step_or_proof(self):
        data = started()
        before = copy.deepcopy(data)
        offered, ok, events = command(data, "offer")
        self.assertTrue(ok)
        self.assertEqual(data, before)
        self.assertEqual(offered[STATE_KEY], dict(default_elder_kiln_state_pure(), phase="preparing", attempt=1))
        self.assertEqual(events, (("offered",),))
        self.assertNotIn(PROOF, offered["quest_action_proofs"])
        self.assertIsNot(offered[STATE_KEY], data[STATE_KEY])

    def test_inappropriate_phases_and_unknown_commands_are_refused(self):
        request = started()
        preparing = command(request, "offer")[0]
        failed = dict(preparing, **{STATE_KEY: attempt(phase="failed", progress=0)})
        refusals = [
            (request, "retry"), (request, "wait_step"), (request, "wait_change"), (request, "cast:fire_bolt"),
            (preparing, "offer"), (preparing, "retry"), (preparing, "cast:fireball"), (preparing, "unknown"),
            (preparing, None), (failed, "offer"), (failed, "wait_step"), (failed, "wait_change"),
            (failed, "cast:water_wave"),
        ]
        for data, name in refusals:
            with self.subTest(phase=data[STATE_KEY]["phase"], command=name):
                before = copy.deepcopy(data)
                result, ok, events = command(data, name)
                self.assertEqual((ok, events), (False, ()))
                self.assertEqual(data, before)
                assert_detached_refusal(self, result, data)

    def test_ineligible_saves_cannot_enter_the_producer(self):
        live = {STATE_KEY: attempt(progress=99, heat=30)}
        saves = {
            "unstarted": player(),
            "later stage": dict(started(progress=2, started=True), **live),
            "completed": dict(player(progress=7, started=True, completed=True), **live),
            "already proven": dict(started(proofs=(PROOF,)), **live),
            "other quest": dict(started(), current_quest="rune_mysteries"),
        }
        for label, data in saves.items():
            with self.subTest(save=label):
                quest_id = "rune_mysteries" if label == "other quest" else QUEST_ID
                result, ok, _ = kiln.apply_elder_kiln_command_pure(data, quest_id, "wait_step", CountingRng())
                self.assertFalse(ok)
                assert_detached_refusal(self, result, data)

    def test_loaded_hundred_percent_cannot_become_a_hatch(self):
        for raw in (attempt(progress=100), attempt(phase="hatched", progress=100), attempt(progress="99")):
            with self.subTest(raw=raw):
                data = dict(started(), **{STATE_KEY: raw})
                result, ok, _ = command(data, "wait_step")
                self.assertFalse(ok)
                offered, ok, _ = command(data, "offer")
                self.assertTrue(ok)
                self.assertNotIn(PROOF, offered["quest_action_proofs"])
                self.assertEqual(offered[STATE_KEY]["progress"], 0)

    def test_reducers_never_mutate_or_share_their_input(self):
        state = attempt(heat=0, ak_phase="warning", ak_remaining=1, steps=19)
        for reducer in (
            lambda s: kiln.elder_kiln_step_pure(s, CountingRng()),
            lambda s: kiln.cast_elder_kiln_spell_pure(s, "fire_bolt", CountingRng()),
            lambda s: kiln.wait_elder_kiln_until_change_pure(s, CountingRng()),
            lambda s: kiln.retry_elder_kiln_attempt_pure(dict(s, phase="failed", progress=0)),
            lambda s: kiln.offer_elder_kiln_help_pure(dict(s, phase="request")),
        ):
            before = copy.deepcopy(state)
            after, _ = reducer(state)
            self.assertEqual(state, before)
            self.assertIsNot(after, state)

    def test_terminal_states_refuse_play(self):
        for phase in kiln.TERMINAL_PHASES:
            state = attempt(phase=phase, progress=0 if phase == "failed" else 100)
            self.assertIsNone(kiln.elder_kiln_step_pure(state, CountingRng()))
            self.assertIsNone(kiln.cast_elder_kiln_spell_pure(state, "fire_bolt", CountingRng()))
            self.assertIsNone(kiln.wait_elder_kiln_until_change_pure(state, CountingRng()))
            self.assertIsNone(kiln.offer_elder_kiln_help_pure(state))


class ActualPlayTest(unittest.TestCase):
    RESOURCE_KEYS = ("inventory", "carried_inventory", "equipment", "magic_exp", "magic_level",
                     "agility_exp", "mining_exp", "quests", "quest_points", "claims")

    def test_request_to_real_hatch_emits_exactly_one_proof(self):
        rng = random.Random(1440).random
        data, ok, _ = command(started(), "offer", rng)
        self.assertTrue(ok)
        resources = {key: copy.deepcopy(data.get(key)) for key in self.RESOURCE_KEYS}
        for _ in range(500):
            if data[STATE_KEY]["phase"] == "hatched":
                break
            self.assertNotIn(PROOF, data["quest_action_proofs"])
            data, ok, _ = command(data, best_command(data[STATE_KEY]), rng)
            self.assertTrue(ok)
        self.assertEqual(data[STATE_KEY]["phase"], "hatched")
        self.assertEqual(data["quest_action_proofs"], [PROOF])
        self.assertEqual({key: data.get(key) for key in self.RESOURCE_KEYS}, resources)
        again, ok, _ = command(data, "wait_step", rng)
        self.assertFalse(ok)
        assert_detached_refusal(self, again, data)

    def test_failure_and_retry_never_emit_the_proof(self):
        data, _, _ = command(started(), "offer")
        while data[STATE_KEY]["phase"] == "preparing":
            data, ok, _ = command(data, "wait_step")
        self.assertEqual(data[STATE_KEY]["phase"], "active")
        while data[STATE_KEY]["phase"] == "active":
            data, ok, events = command(data, "cast:water_wave")
        self.assertEqual(data[STATE_KEY]["phase"], "failed")
        self.assertIn(("failed",), events)
        data, ok, _ = command(data, "retry")
        self.assertTrue(ok)
        self.assertEqual(data[STATE_KEY]["attempt"], 2)
        self.assertEqual(data["quest_action_proofs"], [])

    def test_observation_reads_without_writing(self):
        data = dict(started(), **{STATE_KEY: attempt(ak_phase="warning", ak_remaining=3)})
        before = copy.deepcopy(data)
        seen = kiln.elder_kiln_observation_pure(data, (("marker", 1),))
        self.assertEqual(data, before)
        self.assertEqual((seen["band_low"], seen["band_high"], seen["in_band"]), (20, 40, True))
        self.assertEqual(seen["warnings"], ("Mej-Ak: Firing now!",))
        self.assertTrue(seen["can_play"])
        self.assertFalse(seen["can_offer"] or seen["can_retry"])


class AdmissionTest(unittest.TestCase):
    def _reasons(self, data, blockers=None):
        if blockers is None:
            blockers = quest_current_stage_blockers_pure(data, QUEST_ID, QUEST_DATA)
        return kiln.elder_kiln_admission_reasons_pure(
            data, QUEST_ID, QUEST_DATA, blockers, quest_eligibility_reasons_pure)

    def test_only_the_openings_own_missing_deed_is_permitted(self):
        data = started()
        self.assertEqual(self._reasons(data), ())
        self.assertTrue(can_attempt_quest_review_pure(data, QUEST_ID, QUEST_DATA))
        unrelated = {"kind": "missing_item", "reason": "Needs Pickaxe x1"}
        self.assertEqual(self._reasons(data, (*quest_current_stage_blockers_pure(data, QUEST_ID, QUEST_DATA), unrelated)),
                         ("Needs Pickaxe x1",))

    def test_entry_skills_are_rechecked_on_a_started_opening(self):
        for skill, level in (("magic", 74), ("agility", 59), ("mining", 40)):
            with self.subTest(skill=skill):
                data = started(started=True, levels={skill: level})
                self.assertEqual(self._reasons(data), (f"Requires {skill.title()} {level + 1}",))
                self.assertFalse(can_attempt_quest_review_pure(data, QUEST_ID, QUEST_DATA))

    def test_later_and_completed_saves_are_not_ready(self):
        for data in (started(progress=2, started=True), player(progress=7, started=True, completed=True)):
            self.assertFalse(kiln.elder_kiln_opening_applies_pure(data, QUEST_ID))
            self.assertFalse(can_attempt_quest_review_pure(data, QUEST_ID, QUEST_DATA))


if __name__ == "__main__":
    unittest.main()
