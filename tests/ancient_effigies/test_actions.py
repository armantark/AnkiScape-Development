"""Investigation and lamp reducers: thresholds, exact rewards and exact refusals."""

from __future__ import annotations

import copy
import random
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.skill_registry import ALL_SKILLS
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.ancient_effigies.catalog import LAMP_SKILL_IDS, SKILL_PAIRS, STAGES
from ankiscape.logic.ancient_effigies import actions, requests, view
from ankiscape.logic.ancient_effigies.custody import INSTANCES_KEY

_SEED = "0123456789abcdef0123456789abcdef"
_BASE = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
_EXP_KEYS = tuple(skill.exp_key for skill in ALL_SKILLS)


def effigy_player(item_id=18778, pair_index=0, *, step=0, seed=_SEED, units=1, instance_id="ancient-effigy-1", **fields):
    """A complete save owning one Bank effigy copy with a known request."""
    data = copy.deepcopy(_BASE)
    name = next(stage.name for stage in STAGES if stage.item_id == item_id)
    data["inventory"][name] = units
    data[INSTANCES_KEY] = {
        instance_id: {
            "item_id": item_id,
            "location": "bank",
            "request_seed": seed,
            "request_step": step,
            "pair_index": pair_index,
        }
    }
    data["ancient_effigy_next_id"] = 2
    data.update(fields)
    return data


def lamp_player(**fields):
    data = copy.deepcopy(_BASE)
    data[INSTANCES_KEY] = {
        "ancient-effigy-7": {
            "item_id": 18782,
            "location": "held",
            "request_seed": _SEED,
            "request_step": 3,
            "pair_index": None,
        }
    }
    data["ancient_effigy_next_id"] = 8
    data.update(fields)
    return data


def token_for(data, instance_id="ancient-effigy-1"):
    return actions.stage_token_pure(instance_id, data[INSTANCES_KEY][instance_id])


class _RefusalAssertions(unittest.TestCase):
    def assertRefused(self, reducer, data, *args, contains=""):
        before = copy.deepcopy(data)
        rng_before = random.getstate()
        updated, ok, info = reducer(data, *args)
        self.assertFalse(ok)
        self.assertIs(updated, data, "a refusal returns the caller's own input")
        self.assertEqual(data, before, "a refusal changes nothing")
        self.assertEqual(random.getstate(), rng_before, "a refusal draws no shared RNG")
        self.assertIn(contains, info["message"])
        return info


class InvestigationThresholdTest(_RefusalAssertions):
    def test_both_members_of_every_pair_at_every_stage(self):
        for stage in STAGES:
            for pair_index, pair in enumerate(SKILL_PAIRS):
                for skill_id in pair:
                    with self.subTest(stage=stage.name, skill=skill_id):
                        self._assert_threshold_case(stage, pair_index, skill_id)

    def _assert_threshold_case(self, stage, pair_index, skill_id):
        below = effigy_player(stage.item_id, pair_index, **{f"{skill_id}_level": stage.required_level - 1})
        self.assertRefused(
            actions.investigate_effigy_pure, below, token_for(below), skill_id,
            contains=f"level {stage.required_level} {actions.skill_name(skill_id)}",
        )
        data = effigy_player(stage.item_id, pair_index, **{f"{skill_id}_level": stage.required_level})
        before = copy.deepcopy(data)
        rng_before = random.getstate()
        updated, ok, info = actions.investigate_effigy_pure(data, token_for(data), skill_id)
        self.assertTrue(ok, info)
        self.assertEqual(data, before, "the caller's save is not mutated")
        self.assertEqual(random.getstate(), rng_before, "requests use a local generator")
        self.assertEqual(info["xp"], stage.reward_xp)
        for exp_key in _EXP_KEYS:
            gained = updated.get(exp_key, 0) - before.get(exp_key, 0)
            self.assertEqual(gained, stage.reward_xp if exp_key == f"{skill_id}_exp" else 0, exp_key)
        self.assertNotIn(stage.name, updated["inventory"], "the depleted input key is removed")
        record = updated[INSTANCES_KEY]["ancient-effigy-1"]
        self.assertEqual(record["item_id"], stage.output_item_id)
        self.assertEqual(record["request_seed"], _SEED)
        if stage.output_item_id == 18782:
            self.assertEqual((record["location"], record["pair_index"]), ("held", None))
            self.assertNotIn("Dragonkin lamp", updated["inventory"])
        else:
            self.assertEqual(updated["inventory"][stage.output_name], 1)
            self.assertEqual(record["location"], "bank")
            self.assertEqual(record["request_step"], 1)
            self.assertNotEqual(record["pair_index"], pair_index)
            self.assertEqual(record["pair_index"], requests.next_pair_index_pure(_SEED, 1, pair_index))


class EligibilityTest(_RefusalAssertions):
    def test_existing_visible_boost_qualifies(self):
        data = effigy_player(18779, 0, crafting_level=90, skilling_current_levels={"crafting": 93})
        updated, ok, _info = actions.investigate_effigy_pure(data, token_for(data), "crafting")
        self.assertTrue(ok)
        self.assertEqual(updated["crafting_exp"] - data["crafting_exp"], 20000)
        self.assertEqual(updated["skilling_current_levels"], {"crafting": 93}, "no potion is drunk or spent")

    def test_invisible_familiar_bonus_alone_does_not_qualify(self):
        data = effigy_player(
            18778, 6, mining_level=85,
            summoning_state={"active_follower": {"kind": "familiar", "entity_id": "lavatitan"}},
        )
        self.assertRefused(actions.investigate_effigy_pure, data, token_for(data), "mining", contains="level 91 Mining")

    def test_a_boost_that_expires_after_display_is_rechecked(self):
        data = effigy_player(18778, 0, crafting_level=90, skilling_current_levels={"crafting": 93})
        shown = view.effigy_detail_pure(data, "ancient-effigy-1")
        crafting = next(choice for choice in shown["choices"] if choice["skill_id"] == "crafting")
        self.assertTrue(crafting["eligible"])
        data["skilling_current_levels"] = {}
        self.assertRefused(actions.investigate_effigy_pure, data, shown["token"], "crafting", contains="level 91 Crafting")

    def test_either_member_or_both_may_be_eligible(self):
        data = effigy_player(18778, 1, construction_level=91, thieving_level=95)
        detail = view.effigy_detail_pure(data, "ancient-effigy-1")
        self.assertEqual([choice["eligible"] for choice in detail["choices"]], [True, True])
        data = effigy_player(18778, 1, construction_level=91, thieving_level=90)
        detail = view.effigy_detail_pure(data, "ancient-effigy-1")
        self.assertEqual([choice["eligible"] for choice in detail["choices"]], [True, False])
        self.assertEqual(detail["choices"][1]["reason"], "Needs level 91 Thieving; yours is 90.")


class InvestigationRefusalTest(_RefusalAssertions):
    def test_nonmember_and_unknown_skills(self):
        data = effigy_player(18778, 0, cooking_level=99, crafting_level=99)
        self.assertRefused(actions.investigate_effigy_pure, data, token_for(data), "cooking", contains="does not want")
        self.assertRefused(actions.investigate_effigy_pure, data, token_for(data), "sailing", contains="does not want")
        self.assertRefused(actions.investigate_effigy_pure, data, token_for(data), None, contains="does not want")

    def test_missing_unit_and_wrong_holder(self):
        data = effigy_player(18778, 0, units=0, crafting_level=99)
        self.assertRefused(actions.investigate_effigy_pure, data, token_for(data), "crafting", contains="no longer have")
        data = effigy_player(18778, 0, crafting_level=99)
        data[INSTANCES_KEY]["ancient-effigy-1"]["location"] = "grave"
        self.assertRefused(actions.investigate_effigy_pure, data, token_for(data), "crafting", contains="Reclaim")
        data = effigy_player(18778, 0, crafting_level=99)
        self.assertRefused(actions.investigate_effigy_pure, data, dict(token_for(data), instance_id="ancient-effigy-9"), "crafting")

    def test_unrevealed_pair(self):
        data = effigy_player(18778, None, crafting_level=99)
        self.assertRefused(actions.investigate_effigy_pure, data, token_for(data), "crafting", contains="Inspect")

    def test_stale_item_pair_and_step(self):
        data = effigy_player(18778, 0, crafting_level=99)
        token = token_for(data)
        for field, value in (("item_id", 18779), ("pair_index", 1), ("request_step", 1), ("request_step", True)):
            with self.subTest(field=field, value=value):
                self.assertRefused(
                    actions.investigate_effigy_pure, data, dict(token, **{field: value}), "crafting",
                    contains="changed since it was shown",
                )

    def test_a_repeated_token_is_stale_after_success(self):
        data = effigy_player(18778, 0, crafting_level=99, inventory={**_BASE["inventory"], "Starved ancient effigy": 2})
        token = token_for(data)
        updated, ok, _info = actions.investigate_effigy_pure(data, token, "crafting")
        self.assertTrue(ok)
        self.assertEqual(updated["inventory"]["Starved ancient effigy"], 1, "sibling units stay")
        self.assertRefused(actions.investigate_effigy_pure, updated, token, "crafting", contains="changed since it was shown")


class InspectionTest(_RefusalAssertions):
    def test_first_inspection_records_the_seeded_pair_and_a_second_is_a_read(self):
        data = effigy_player(18778, None)
        rng_before = random.getstate()
        updated, ok, info = actions.inspect_effigy_pure(data, "ancient-effigy-1")
        self.assertTrue(ok and info["changed"])
        self.assertEqual(random.getstate(), rng_before)
        self.assertEqual(updated[INSTANCES_KEY]["ancient-effigy-1"]["pair_index"], requests.initial_pair_index_pure(_SEED))
        again, ok, info = actions.inspect_effigy_pure(updated, "ancient-effigy-1")
        self.assertTrue(ok)
        self.assertFalse(info["changed"])
        self.assertIs(again, updated)

    def test_inspection_refuses_a_copy_outside_the_bank(self):
        data = effigy_player(18778, None)
        data[INSTANCES_KEY]["ancient-effigy-1"]["location"] = "death_office"
        self.assertRefused(actions.inspect_effigy_pure, data, "ancient-effigy-1", contains="Reclaim")
        self.assertRefused(actions.inspect_effigy_pure, data, "ancient-effigy-404", contains="no longer have")

    def test_view_never_exposes_the_seed(self):
        data = effigy_player(18778, None)
        self.assertNotIn(_SEED, repr(view.effigy_rows_pure(data)) + repr(view.effigy_detail_pure(data, "ancient-effigy-1")))
        self.assertEqual(view.effigy_detail_pure(data, "ancient-effigy-1")["pair_text"], "Inspect to reveal skills")


class NextPairTest(unittest.TestCase):
    def test_all_seven_rolls_map_around_the_previous_pair(self):
        for previous in range(8):
            mapped = [roll + 1 if roll >= previous else roll for roll in range(7)]
            self.assertEqual(sorted(mapped), [pair for pair in range(8) if pair != previous])
        seen = {}
        for step in range(1, 400):
            for previous in range(8):
                result = requests.next_pair_index_pure(_SEED, step, previous)
                self.assertNotEqual(result, previous)
                seen.setdefault(previous, set()).add(result)
        self.assertEqual(seen, {previous: set(range(8)) - {previous} for previous in range(8)})

    def test_an_earlier_pair_may_return_after_an_intervening_stage(self):
        returned = False
        for number in range(200):
            seed = f"{number:032x}"
            first = requests.initial_pair_index_pure(seed)
            second = requests.next_pair_index_pure(seed, 1, first)
            third = requests.next_pair_index_pure(seed, 2, second)
            returned = returned or third == first
        self.assertTrue(returned)

    def test_requests_are_stable_and_ignore_the_shared_random_module(self):
        random.seed(1)
        first = [requests.initial_pair_index_pure(_SEED), requests.next_pair_index_pure(_SEED, 1, 3)]
        random.random()
        self.assertEqual(first, [requests.initial_pair_index_pure(_SEED), requests.next_pair_index_pure(_SEED, 1, 3)])


class LampReducerTest(_RefusalAssertions):
    def test_redeem_reads_the_permanent_level_at_confirmation_and_consumes_once(self):
        data = lamp_player(attack_level=1, attack_exp=0, skilling_current_levels={"attack": 50})
        token = actions.lamp_token_pure("ancient-effigy-7")
        updated, ok, info = actions.redeem_lamp_pure(data, token, "attack")
        self.assertTrue(ok)
        self.assertEqual((info["level"], info["xp"]), (1, 4))
        self.assertEqual(updated["attack_exp"], 4)
        self.assertEqual(updated[INSTANCES_KEY], {})
        self.assertEqual(updated["ancient_effigy_next_id"], 8)
        self.assertRefused(actions.redeem_lamp_pure, updated, token, "attack", contains="changed since it was shown")

    def test_every_lamp_skill_is_offered_independently(self):
        data = lamp_player()
        token = actions.lamp_token_pure("ancient-effigy-7")
        for skill_id in LAMP_SKILL_IDS:
            with self.subTest(skill=skill_id):
                updated, ok, info = actions.redeem_lamp_pure(data, token, skill_id)
                self.assertTrue(ok, info)
                exp_key = "defense_exp" if skill_id == "defense" else f"{skill_id}_exp"
                self.assertEqual(updated[exp_key] - data.get(exp_key, 0), info["xp"])

    def test_lamp_refusals(self):
        data = lamp_player()
        token = actions.lamp_token_pure("ancient-effigy-7")
        self.assertRefused(actions.redeem_lamp_pure, data, token, "sailing", contains="cannot grant")
        self.assertRefused(actions.redeem_lamp_pure, data, actions.lamp_token_pure("ancient-effigy-8"), "attack")
        self.assertRefused(actions.redeem_lamp_pure, data, {"instance_id": "ancient-effigy-7", "item_id": 18781}, "attack")
        graved = lamp_player()
        graved[INSTANCES_KEY]["ancient-effigy-7"]["location"] = "grave"
        self.assertRefused(actions.redeem_lamp_pure, graved, token, "attack", contains="Reclaim")
        self.assertRefused(actions.destroy_lamp_pure, graved, token, contains="Reclaim")
        officed = lamp_player()
        officed[INSTANCES_KEY]["ancient-effigy-7"]["location"] = "death_office"
        self.assertRefused(actions.redeem_lamp_pure, officed, token, "attack", contains="Reclaim")

    def test_destroy_removes_only_the_lamp_and_awards_nothing(self):
        data = lamp_player()
        data[INSTANCES_KEY]["ancient-effigy-2"] = {
            "item_id": 18779, "location": "bank", "request_seed": _SEED, "request_step": 1, "pair_index": 4,
        }
        data["inventory"]["Nourished ancient effigy"] = 1
        updated, ok, _info = actions.destroy_lamp_pure(data, actions.lamp_token_pure("ancient-effigy-7"))
        self.assertTrue(ok)
        self.assertEqual(list(updated[INSTANCES_KEY]), ["ancient-effigy-2"])
        self.assertEqual({key: updated.get(key) for key in _EXP_KEYS}, {key: data.get(key) for key in _EXP_KEYS})
        self.assertRefused(actions.destroy_lamp_pure, updated, actions.lamp_token_pure("ancient-effigy-7"))


if __name__ == "__main__":
    unittest.main()
