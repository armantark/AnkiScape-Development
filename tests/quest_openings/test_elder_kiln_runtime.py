"""Actual quest-answer ingress for the hatching exercise, driven by a scripted presenter."""

import copy
from contextlib import contextmanager
import random
import sys
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core import elder_kiln_dialog
from ankiscape.core.constants import QUEST_DATA
from ankiscape.data.quest.elder_kiln import FAILURE_COPY, STATE_KEY
from ankiscape.logic_pure.logic_pure_quest import can_attempt_quest_review_pure
from ankiscape.logic_pure.logic_pure_telemetry import action_telemetry_key_pure
from ankiscape.runtime.runtime_actions import handle_quest_answer
from tests.quest_openings.test_elder_kiln_data import PROOF, QUEST_ID, player
from tests.quest_openings.test_elder_kiln_logic import best_command
from tests.test_combat_quest_gate import _answer_review
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package
from tests.test_runtime_actions import _context

RESOURCE_KEYS = (
    "inventory", "carried_inventory", "equipment", "toolbelt", "magic_exp", "magic_level", "agility_exp",
    "agility_level", "mining_exp", "mining_level", "combat_lifepoints", "combat_prayer_points", "claims",
    "quest_points", "quest_route_states", "quest_combat_encounters", "quest_combat_encounter_counts",
    "current_combat_spell", "combat_spellbook_swap", "pending_skill_exp_rewards", "combat_current_levels",
)


class Script:
    """Plays real commands; a step is a command name or a callable deciding from the observation."""

    def __init__(self, *steps, raises=None):
        self.steps, self.raises = steps, raises
        self.calls, self.opened = 0, []

    def __call__(self, command, observation):
        self.calls += 1
        self.opened.append(observation)
        for step in self.steps:
            observation = step(command, observation) if callable(step) else command(step)
        self.last = observation
        if self.raises:
            raise self.raises


def play_until(phase, chooser=None):
    def run(command, observation):
        for _ in range(600):
            if observation["phase"] == phase:
                return observation
            observation = command((chooser or best_command)(observation))
        raise AssertionError(f"never reached {phase}")
    return run


def sink(observation):
    return "cast:water_wave" if observation["phase"] == "active" else "wait_step"


def telemetry(data, event_id):
    return data["action_telemetry"]["actions"][action_telemetry_key_pure("quest", event_id)]


def resources(data):
    return {key: copy.deepcopy(data.get(key)) for key in RESOURCE_KEYS}


def opening(**kwargs):
    data = player(**kwargs)
    data["inventory"], data["toolbelt"] = {}, {}
    return data


class IngressTest(unittest.TestCase):
    def _answer(self, data, script, calls=None, rng=None):
        calls = calls if calls is not None else {"xp": [], "saves": 0, "errors": []}
        ctx = _context(data, calls)
        ctx.random_random = rng or random.Random(1440).random
        with patch.object(elder_kiln_dialog, "present_elder_kiln_hatching", script):
            result = handle_quest_answer(ctx)
        return result, calls

    def test_opening_is_reachable_despite_its_own_missing_proof(self):
        data = opening(started=True)
        self.assertTrue(can_attempt_quest_review_pure(data, QUEST_ID, QUEST_DATA))
        script = Script()
        ok, calls = self._answer(data, script)
        self.assertTrue(ok)
        self.assertEqual(script.calls, 1)
        self.assertEqual(script.opened[0]["phase"], "request")
        self.assertEqual(calls["errors"], [])

    def test_each_skill_boundary_refuses_with_its_name_and_no_mutation(self):
        boosted = {
            "magic": {"combat_current_levels": {"magic": 80}},
            "agility": {"skilling_current_levels": {"agility": 64}, "agility_effective_boost": 5,
                        "agility_boost_actions_remaining": 3},
            "mining": {},
        }
        for skill, level, label in (("magic", 74, "Magic 75"), ("agility", 59, "Agility 60"), ("mining", 40, "Mining 41")):
            for started in (False, True):
                with self.subTest(skill=skill, started=started):
                    data = dict(opening(started=started, levels={skill: level}), **boosted[skill])
                    before = copy.deepcopy(data)
                    script = Script("offer")
                    ok, calls = self._answer(data, script)
                    self.assertFalse(ok)
                    self.assertEqual(script.calls, 0)
                    self.assertEqual(data, before)
                    self.assertEqual(calls["saves"], 0)
                    self.assertIn(f"• Requires {label}", calls["errors"][0][1])
                    self.assertTrue(calls.get("deactivated"))

    def test_boundary_levels_admit_without_suggested_quests_pickaxe_or_supplies(self):
        data = opening()
        for suggested in ("temple_at_senntisten", "toktz_ket_dill"):
            self.assertFalse(data["quests"].get(suggested, {}).get("completed"))
        script = Script("offer")
        ok, calls = self._answer(data, script)
        self.assertTrue(ok)
        self.assertEqual(script.calls, 1)
        self.assertEqual(data["quests"][QUEST_ID], dict(started=True, completed=False, progress=0))
        self.assertEqual(data[STATE_KEY]["phase"], "preparing")
        self.assertEqual((data["inventory"], data["toolbelt"]), ({}, {}))

    def test_pause_commits_the_attempt_and_reopens_it_unchanged(self):
        data = opening(started=True)
        ok, calls = self._answer(data, Script("offer", "cast:fire_blast", "wait_step", "wait_change"))
        self.assertTrue(ok)
        paused = copy.deepcopy(data[STATE_KEY])
        self.assertIn(paused["phase"], ("preparing", "active"))
        self.assertEqual(data["quests"][QUEST_ID]["progress"], 0)
        self.assertEqual(data["quest_action_proofs"], [])
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["activity"], [f"The Elder Kiln: hatching paused at {paused['progress']}%"])
        attempt_record = telemetry(data, "elder_kiln_first_egg_attempt")
        self.assertEqual((attempt_record["successes"], attempt_record["failure_kinds"]), (0, {"paused": 1}))
        script = Script()
        self._answer(data, script)
        reopened = {key: script.opened[0][key] for key in paused}
        self.assertEqual(reopened, paused)
        self.assertEqual(data[STATE_KEY], paused)

    def test_failure_then_retry_on_another_answer(self):
        data = opening(started=True)
        ok, calls = self._answer(data, Script("offer", play_until("failed", sink)))
        self.assertTrue(ok)
        self.assertEqual(data[STATE_KEY]["phase"], "failed")
        self.assertEqual(calls["activity"], [f"The Elder Kiln: {FAILURE_COPY}"])
        self.assertEqual(telemetry(data, "elder_kiln_first_egg_failure")["failure_kinds"], {"failed": 1})
        self.assertEqual((data["quests"][QUEST_ID]["progress"], data["quest_action_proofs"]), (0, []))
        script = Script("cast:fire_bolt", "retry")
        self._answer(data, script)
        self.assertEqual(script.opened[0]["phase"], "failed")
        self.assertEqual((data[STATE_KEY]["phase"], data[STATE_KEY]["attempt"]), ("preparing", 2))

    def test_hatch_advances_exactly_one_stage_without_resources_or_rewards(self):
        for carried in ({}, {"agility_course": {f"Item {index}": 1 for index in range(28)}}):
            with self.subTest(carried=bool(carried)):
                data = opening(started=True)
                data.update(carried_inventory=carried, current_combat_spell="ice_barrage", combat_spellbook_swap="ancient",
                            inventory={"Fire rune": 3, "Water rune": 2})
                before = resources(data)
                script = Script("offer", play_until("hatched"))
                ok, calls = self._answer(data, script)
                self.assertTrue(ok)
                self.assertEqual(script.last["phase"], "hatched")
                self.assertEqual(data["quests"][QUEST_ID], dict(started=True, completed=False, progress=2))
                self.assertEqual(data["quest_action_proofs"].count(PROOF), 1)
                self.assertEqual(resources(data), before)
                self.assertEqual(calls["xp"], [])
                self.assertEqual(calls["activity"], ["The Elder Kiln: the egg hatched (2/7)"])
                self.assertEqual(telemetry(data, "elder_kiln_first_egg_hatch")["successes"], 1)
                self._assert_no_second_entry(data)

    def test_existing_progress_one_holds_until_the_hatch(self):
        data = opening(progress=1, started=True)
        self._answer(data, Script("offer", "wait_step"))
        self.assertEqual(data["quests"][QUEST_ID], dict(started=True, completed=False, progress=1))
        self._answer(data, Script(play_until("hatched")))
        self.assertEqual(data["quests"][QUEST_ID], dict(started=True, completed=False, progress=2))
        self.assertEqual(data["quest_action_proofs"], [PROOF])

    def _assert_no_second_entry(self, data):
        before = copy.deepcopy(data)
        script = Script("offer")
        ok, calls = self._answer(data, script)
        self.assertFalse(ok)
        self.assertEqual(script.calls, 0)
        self.assertEqual(data["quests"], before["quests"])
        self.assertEqual(data["quest_action_proofs"], before["quest_action_proofs"])
        self.assertIn("Complete The Elder Kiln stage 2 objective", calls["errors"][0][1])

    def test_later_and_completed_saves_never_open_the_exercise(self):
        for data in (opening(progress=3, started=True), opening(progress=7, started=True, completed=True)):
            with self.subTest(progress=data["quests"][QUEST_ID]["progress"]):
                script = Script("offer")
                self._answer(data, script)
                self.assertEqual(script.calls, 0)
                self.assertNotIn(PROOF, data["quest_action_proofs"])

    def test_presenter_exception_commits_nothing(self):
        data = opening(started=True)
        before = copy.deepcopy(data)
        script = Script("offer", play_until("hatched"), raises=RuntimeError("dialog failed"))
        with self.assertRaisesRegex(RuntimeError, "dialog failed"):
            self._answer(data, script, calls={"xp": [], "saves": 0, "errors": []})
        self.assertEqual(script.last["phase"], "hatched")
        self.assertEqual(data, before)


@contextmanager
def review_session(data):
    original_modules, original_rng = dict(sys.modules), random.getstate()
    try:
        _install_runtime_fakes()
        addon = _load_addon_as_package("ankiscape_elder_kiln_runtime")
        saved, messages = [], []
        addon.save_player_data = lambda: saved.append(copy.deepcopy(addon._state.player_data))
        addon.show_error_message = lambda *_args: None
        addon.check_achievements = lambda _data: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = messages.append
        addon._show_exp = lambda _amount: None
        addon.level_up_check = lambda *_args: None
        addon.update_review_hud = lambda *_args: None
        addon._state.player_data = data
        addon._state.current_skill = "Quests"
        addon._state.review_undo_stack.clear()
        yield addon, saved, messages
    finally:
        random.setstate(original_rng)
        sys.modules.clear()
        sys.modules.update(original_modules)


class AnswerWrapperTest(unittest.TestCase):
    def _patch(self, addon, script):
        module = sys.modules[f"{addon.__name__}.core.elder_kiln_dialog"]
        return patch.object(module, "present_elder_kiln_hatching", script)

    def test_again_neither_opens_nor_advances(self):
        with review_session(opening(started=True)) as (addon, saved, _messages):
            before = copy.deepcopy(addon._state.player_data[STATE_KEY])
            script = Script("offer")
            addon._state.card_turned = addon._state.answer_shown = True
            addon._state.exp_awarded = False
            with self._patch(addon, script):
                addon.on_answer_card(object(), 1, lambda *_args: "answered")
            self.assertEqual(script.calls, 0)
            self.assertEqual(addon._state.player_data[STATE_KEY], before)

    def test_multiplier_opens_once_and_hatching_effects_are_resource_free(self):
        for multiplier in (1, 5):
            with self.subTest(multiplier=multiplier):
                with review_session(opening(started=True)) as (addon, saved, _messages):
                    addon._review_action_multiplier = lambda: multiplier
                    before = resources(addon._state.player_data)
                    script = Script("offer", play_until("hatched"))
                    with self._patch(addon, script):
                        _answer_review(addon)
                    data = addon._state.player_data
                    self.assertEqual(script.calls, 1)
                    self.assertEqual(data["quests"][QUEST_ID]["progress"], 2)
                    self.assertEqual(data["quest_action_proofs"].count(PROOF), 1)
                    # The ordinary Answer still moves clocks; the hatch moves no resources.
                    self.assertEqual(resources(data), before)
                    self.assertEqual(len(saved), 1)
                    self.assertEqual(len(addon._state.review_undo_stack), 1)


if __name__ == "__main__":
    unittest.main()
