"""Shadow attraction, isolated upkeep, ordinary Farming care and replacement."""

import copy
import subprocess
import sys
import unittest
from itertools import product
from unittest.mock import Mock, patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import HUNTER_DATA, QUEST_UNLOCK_RULES
from ankiscape.data.farming_data import FARMING_CROPS_BY_ID
from ankiscape.logic import farming_logic as farm
from ankiscape.logic.farming.habitat import FLOWER_REASON
from ankiscape.logic.farming.habitat_state import HOUSE_REASON, apply_abandoned_house_pure
from ankiscape.logic.farming_logic import apply_shadow_setup_step_pure, shadow_setup_preview_pure
from ankiscape.logic.farming.habitat_state import shadow_attraction_reasons_pure
from ankiscape.logic_pure.logic_pure import (
    apply_hunter_action_pure, can_hunt_target_pure, hunter_target_locked_reasons_pure,
)
from tests.habitat.fixtures import ready_shadow_habitat, setup_state, established_state, TARGET, PATCH


def catch(data, context=True):
    return apply_hunter_action_pure(
        TARGET, data["inventory"], HUNTER_DATA, 71, 0.0,
        r_secondary_rolls=((0.0, 0.0),) * 3,
        player_data=data if context else None,
    )


class ShadowAttractionTest(unittest.TestCase):
    def test_existing_farming_paths_reexport_shared_state_and_care(self):
        from ankiscape.logic.farming import care, state

        self.assertIs(farm._default_patch_record, state._default_patch_record)
        self.assertIs(farm._sanitize_plan, state._sanitize_plan)
        self.assertIs(farm._is_mature, care._is_mature)

    def test_habitat_modules_import_without_farming_or_aggregators(self):
        result = subprocess.run(
            [sys.executable, "-c", """
import sys
import pkg_alias
from ankiscape.logic.farming.habitat_state import shadow_attraction_reasons_pure
assert shadow_attraction_reasons_pure({})
assert 'ankiscape.logic.farming_logic' not in sys.modules
assert 'ankiscape.core.constants' not in sys.modules
assert 'ankiscape.logic_pure.logic_pure' not in sys.modules
from ankiscape.logic.farming.habitat import preview_shadow_field_setup
assert preview_shadow_field_setup({}, None)['status'] == 'blocked'
assert 'ankiscape.logic.farming_logic' not in sys.modules
"""],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_strict_state_matrix_refuses_without_rewards_or_debits(self):
        cases = [({}, ("Abandoned house", "healthy planted Red blossom"))]
        for changes in ({"crop_id":
            None}, {"crop_id": "green_blossom"}, {"diseased": True}, {"dead": True}, {"stump": True}, {"stage": -1}, {"stage": "0"}, {"stage": 0.0}, {"stage": True}, {"diseased": None}):
            cases.append((established_state(**changes), ("healthy planted Red blossom",)))
        data = established_state()
        data["habitat_feature"] = "boneyard"
        cases.append((data, ("Abandoned house",)))
        for patches in (None, [], {PATCH:
            []}, {PATCH: {"crop_id": "red_blossom"}}):
            data = established_state()
            data["farm_patches"] = patches
            cases.append((data, ("healthy planted Red blossom",)))
        for data, reasons in cases:
            with self.subTest(data=data):
                self.assertEqual(shadow_attraction_reasons_pure(data), reasons)
                data.setdefault("inventory", {"Noose wand": 1, "Red blossom seed": 10, "Red blossom": 10})
                before = copy.deepcopy(data)
                inv, xp, ok, output, rewards = catch(data)
                self.assertEqual((inv, xp, ok, output, rewards), (data["inventory"], 0, False, None, ()))
                self.assertEqual(data, before)

    def test_stage_zero_and_mature_attract_without_care_gates_or_spare_seed(self):
        for stage in (0, 4):
            data = established_state(stage=stage)
            data["inventory"] = {"Noose wand": 1, "Juju hunter potion (4)": 1}
            data["farming_level"] = 1
            data["construction_level"] = 1
            before = copy.deepcopy(data)
            self.assertEqual(shadow_attraction_reasons_pure(data), ())
            for _ in range(3):
                inv, xp, ok, output, _ = catch(data)
                self.assertTrue(ok)
                self.assertEqual((xp, output), (475, "Shadow vine"))
                self.assertEqual(inv["Noose wand"], 1)
                self.assertEqual(inv["Juju hunter potion (4)"], 1)
            self.assertEqual(data, before)
            self.assertEqual(shadow_setup_preview_pure(data)["status"], "ready")

    def test_inventory_and_plans_are_not_a_planting(self):
        data = setup_state()
        data["habitat_feature"] = "abandoned_house"
        data["inventory"]["Red blossom"] = 20
        data["farm_plans"][PATCH] = {"crop_id": "red_blossom"}
        data["farm_queue"] = [{"kind": "plant", "patch_id": PATCH, "crop_id": "red_blossom"}]
        self.assertEqual(shadow_attraction_reasons_pure(data), ("healthy planted Red blossom",))
        self.assertFalse(catch(data)[2])

    def test_bush_tree_and_potion_do_not_change_predicate(self):
        data = established_state()
        for occupied in (False, True):
            data["farm_patches"]["habitat_vine_bush"] = {"crop_id": "kalferberry" if occupied else None}
            data["farm_patches"]["habitat_fruit"] = {"crop_id": "banana" if occupied else None}
            data["inventory"]["Juju hunter potion (4)"] = int(occupied)
            before = copy.deepcopy(data)
            updated, info = apply_shadow_setup_step_pure(data, Mock(side_effect=AssertionError("random draw")))
            self.assertEqual(info["status"], "ready")
            self.assertEqual(updated, before)

    def test_pure_catch_requires_context_only_for_shadow(self):
        data = established_state()
        self.assertFalse(catch(data, context=False)[2])
        self.assertFalse(can_hunt_target_pure(71, data["inventory"], TARGET, HUNTER_DATA))
        self.assertTrue(can_hunt_target_pure(71, data["inventory"], TARGET, HUNTER_DATA, player_data=data))
        result = apply_hunter_action_pure("track_diseased_jadinko", {"Noose wand": 1}, HUNTER_DATA, 78, 0.0)
        self.assertTrue(result[2])
        self.assertEqual(result[1], 580.5)

    def test_selectable_work_and_waiting_but_blocked_resources_disable(self):
        data = setup_state()
        self.assertEqual(hunter_target_locked_reasons_pure(data, TARGET, HUNTER_DATA, QUEST_UNLOCK_RULES), ())
        data["inventory"]["Red blossom seed"] = 0
        self.assertIn("missing seeds or compost", hunter_target_locked_reasons_pure(data, TARGET, HUNTER_DATA, QUEST_UNLOCK_RULES))
        data = established_state(crop_id="green_blossom")
        self.assertEqual(hunter_target_locked_reasons_pure(data, TARGET, HUNTER_DATA, QUEST_UNLOCK_RULES), ())


class ShadowSetupTest(unittest.TestCase):
    def test_preview_is_read_only_for_all_next_steps(self):
        states = [setup_state(), established_state(), established_state(dead=True), established_state(diseased=True), established_state(crop_id="green_blossom"), established_state(crop_id="blue_blossom")]
        for malformed in (None, [], {"crop_id":
            []}, {"crop_id": {}}, {"crop_id": "unknown"}):
            data = established_state()
            data["farm_patches"][PATCH] = malformed
            self.assertEqual(shadow_setup_preview_pure(data)["status"], "blocked")
            states.append(data)
        for data in states:
            before = copy.deepcopy(data)
            a = shadow_setup_preview_pure(data)
            self.assertEqual(a, shadow_setup_preview_pure(data))
            self.assertEqual(data, before)

    def test_preview_probes_only_disposable_copies_with_executor_default_randomness(self):
        from ankiscape.logic.farming.habitat import preview_shadow_field_setup

        data = established_state(crop_id="green_blossom", stage=4, produce_count=1)
        before = copy.deepcopy(data)
        steps = []

        def execute(probe, step):
            self.assertIsNot(probe, data)
            steps.append(step["kind"])
            result = farm.execute_farm_field_step_pure(probe, step)
            probe["inventory"].clear()
            return result

        with patch("random.random", side_effect=AssertionError("preview gameplay RNG")):
            preview = preview_shadow_field_setup(data, execute)
        self.assertEqual(preview["status"], "field")
        self.assertEqual(steps, ["plant", "harvest"])
        self.assertEqual(data, before)

    def test_plant_uses_one_seed_ordinary_xp_weeds_and_free_house(self):
        data = setup_state()
        before = copy.deepcopy(data)
        updated, info = apply_shadow_setup_step_pure(data, Mock(side_effect=AssertionError("plant RNG")))
        self.assertEqual(data, before)
        self.assertEqual(info["status"], "field")
        self.assertEqual(info["verb"], "plant")
        self.assertEqual(info["field_result"]["status"], "executed")
        self.assertEqual(updated["inventory"]["Red blossom seed"], 0)
        self.assertEqual(updated["inventory"]["Weeds"], 3)
        self.assertEqual(updated["inventory"]["Coins"], 100000)
        self.assertEqual(updated["farming_exp"], 52)
        self.assertEqual(updated["construction_exp"], 0)
        self.assertNotIn("construction_actions_completed", updated)
        self.assertNotIn("hunter_exp", updated)
        self.assertEqual(updated["habitat_feature"], "abandoned_house")
        self.assertEqual(updated["farm_patches"][PATCH]["stage"], 0)
        self.assertTrue(catch(updated)[2])

    def test_free_house_uses_current_level_and_replaces_single_feature(self):
        data = established_state()
        data["habitat_feature"] = "boneyard"
        data["construction_level"] = 99
        data["skilling_current_levels"] = {"construction": 56}
        self.assertEqual(shadow_setup_preview_pure(data), {"status": "blocked", "reason": HOUSE_REASON})
        data["skilling_current_levels"]["construction"] = 57
        updated, info = apply_shadow_setup_step_pure(data, lambda: 1)
        self.assertEqual(info["status"], "ready")
        self.assertEqual(updated["habitat_feature"], "abandoned_house")
        self.assertEqual(updated["inventory"], data["inventory"])

    def test_blocked_setup_never_spends_or_builds(self):
        for missing in ("level", "seed", "farming", "compost"):
            data = setup_state()
            data["habitat_feature"] = "boneyard"
            if missing == "level":
                data["construction_level"] = 56
            if missing == "seed":
                data["inventory"]["Red blossom seed"] = 0
            if missing == "farming":
                data["farming_level"] = 53
            if missing == "compost":
                data["farm_plans"][PATCH] = {"crop_id": "red_blossom", "compost_tier": "supercompost"}
            before = copy.deepcopy(data)
            updated, info = apply_shadow_setup_step_pure(data, Mock(side_effect=AssertionError("blocked RNG")))
            self.assertEqual(info["status"], "blocked", missing)
            self.assertEqual(updated, before)
            self.assertEqual(data, before)

    def test_matching_red_plan_reuses_compost_watering_and_prepaid_fertile_soil(self):
        for prepaid in (False, True):
            data = setup_state()
            data["inventory"].update({"Watering can (8)": 1, "Supercompost": int(not prepaid)})
            data["farm_plans"][PATCH] = {"crop_id": "red_blossom", "compost_tier": "supercompost", "watering_intent": False, "fertile_soil_applied": prepaid}
            data, _, _ = farm.save_farm_preset_pure(data, "My Red plan", [PATCH])
            updated, info = apply_shadow_setup_step_pure(data, lambda: 1)
            self.assertEqual(info["status"], "field")
            self.assertFalse(updated["farm_patches"][PATCH]["watered"])
            self.assertEqual(updated["farm_patches"][PATCH]["compost_tier"], "supercompost")
            self.assertFalse(updated["farm_plans"][PATCH]["fertile_soil_applied"])
            self.assertEqual(updated["farm_presets"], data["farm_presets"])
            self.assertEqual(updated["inventory"]["Supercompost"], 0)

    def test_dead_and_stump_clear_then_plant_on_separate_steps(self):
        for flag in ("dead", "stump"):
            data = established_state(**{flag: True})
            cleared, info = apply_shadow_setup_step_pure(data, lambda: 1)
            self.assertEqual(info["verb"], "clear")
            self.assertIsNone(cleared["farm_patches"][PATCH]["crop_id"])
            self.assertEqual(cleared["inventory"]["Red blossom seed"], 1)
            self.assertFalse(catch(cleared)[2])
            planted, info = apply_shadow_setup_step_pure(cleared, lambda: 1)
            self.assertEqual(info["verb"], "plant")
            self.assertTrue(catch(planted)[2])

    def test_replacement_preflight_preserves_occupant_without_completion_supplies(self):
        occupants = ({"dead": True}, {"stump": True}, {"crop_id": "green_blossom", "stage": 4, "produce_count": 1})
        shortages = {
            "seed": lambda data: data["inventory"].update({"Red blossom seed": 0}),
            "level": lambda data: data.update(farming_level=53),
            "compost": lambda data: data["farm_plans"].update({PATCH: {"crop_id": "red_blossom", "compost_tier": "compost"}}),
            "house": lambda data: data.update(habitat_feature=None, construction_level=56),
        }
        for flags, missing in product(occupants, shortages):
            with self.subTest(flags=flags, missing=missing):
                data = established_state(**flags)
                shortages[missing](data)
                before = copy.deepcopy(data)
                updated, info = apply_shadow_setup_step_pure(data, lambda: 1)
                self.assertEqual(info["status"], "blocked")
                self.assertEqual(updated, before)

    def test_preflight_reuses_normal_retained_tool_checks(self):
        data = established_state(dead=True)
        with patch.object(farm, "tool_on_belt", side_effect=lambda _data, name: name != "Seed dibber"):
            updated, info = apply_shadow_setup_step_pure(data, lambda: 1)
        self.assertEqual(info["status"], "blocked")
        self.assertIn("Seed dibber", info["reason"])
        self.assertEqual(updated, data)

    def test_replacement_preflight_preserves_stored_red_plan(self):
        data = established_state(dead=True)
        data["farm_patches"][PATCH]["plan"] = {
            "crop_id": "red_blossom", "compost_tier": "supercompost",
            "watering_intent": False,
        }
        before = copy.deepcopy(data)
        updated, info = apply_shadow_setup_step_pure(data, lambda: 1)
        self.assertEqual(info["status"], "blocked")
        self.assertEqual(updated, before)
        data["inventory"]["Supercompost"] = 1
        cleared, info = apply_shadow_setup_step_pure(data, lambda: 1)
        self.assertEqual(info["verb"], "clear")
        self.assertEqual(cleared["inventory"]["Supercompost"], 1)
        planted, info = apply_shadow_setup_step_pure(cleared, lambda: 1)
        self.assertEqual(info["verb"], "plant")
        self.assertEqual(planted["farm_patches"][PATCH]["compost_tier"], "supercompost")
        self.assertFalse(planted["farm_patches"][PATCH]["watered"])

    def test_free_house_does_not_follow_clear_or_failed_field_operation(self):
        data = established_state(dead=True)
        data["habitat_feature"] = None
        data["inventory"]["Spade"] = 0
        with patch.object(farm, "tool_on_belt", side_effect=lambda _data, name: name != "Spade"):
            updated, info = apply_shadow_setup_step_pure(data, lambda: 1)
        self.assertEqual(info["status"], "blocked")
        self.assertEqual(updated, data)
        data["inventory"]["Spade"] = 1
        updated, info = apply_shadow_setup_step_pure(data, lambda: 1)
        self.assertEqual(info["verb"], "clear")
        self.assertIsNone(updated["habitat_feature"])

    def test_green_waits_grows_and_harvests_ordinary_reward_then_plants(self):
        data = setup_state()
        data["inventory"]["Green blossom seed"] = 1
        green, ok, _ = farm.execute_farm_field_step_pure(data, {"kind": "plant", "patch_id": PATCH, "crop_id": "green_blossom"})
        self.assertTrue(ok)
        self.assertEqual(shadow_setup_preview_pure(green)["status"], "waiting")
        grown, _ = farm.advance_farm_clock_pure(green, 20, lambda: 1)
        harvested, info = apply_shadow_setup_step_pure(grown, lambda: 1)
        self.assertEqual(info["verb"], "harvest")
        self.assertEqual(harvested["inventory"]["Green blossom"], 1)
        self.assertEqual(harvested["farming_exp"], 52 + 255)
        planted, info = apply_shadow_setup_step_pure(harvested, lambda: 1)
        self.assertEqual(info["verb"], "plant")
        self.assertEqual(planted["farming_exp"], 52 + 255 + 52)
        self.assertEqual(planted["habitat_feature"], "abandoned_house")

    def test_unsupported_blue_remains_blocked(self):
        data = established_state(crop_id="blue_blossom")
        before = copy.deepcopy(data)
        updated, info = apply_shadow_setup_step_pure(data, lambda: 1)
        self.assertEqual(info, {"status": "blocked", "reason": FLOWER_REASON})
        self.assertEqual(updated, before)

    def test_manual_red_harvest_clears_and_replant_required_before_catch(self):
        data = established_state(stage=4, produce_count=1)
        harvested, ok, info = farm.execute_farm_field_step_pure(data, {"kind": "harvest", "patch_id": PATCH})
        self.assertTrue(ok)
        self.assertEqual(info["farming_xp"], 255)
        self.assertEqual(info["outputs"], {"Red blossom": 1})
        self.assertIsNone(harvested["farm_patches"][PATCH]["crop_id"])
        self.assertFalse(catch(harvested)[2])
        replanted, info = apply_shadow_setup_step_pure(harvested, lambda: 1)
        self.assertEqual(info["verb"], "plant")
        self.assertTrue(catch(replanted)[2])


class ShadowCareTest(unittest.TestCase):
    def test_spell_fallback_requires_owned_runes_and_magic_admission(self):
        for magic, astral, earth in ((65, 1, 8), (66, 0, 8), (66, 1, 7)):
            data = established_state(diseased=True)
            data.update(magic_level=magic, quests={"lunar_diplomacy": {"completed": True}})
            data["inventory"].update({"Astral rune": astral, "Earth rune": earth})
            before = copy.deepcopy(data)
            updated, info = apply_shadow_setup_step_pure(data, lambda: 1)
            self.assertEqual(info["status"], "waiting")
            self.assertEqual(updated, before)

    def test_default_item_cure_and_plan_disabled_wait(self):
        data = established_state(diseased=True)
        data["inventory"]["Plant cure"] = 1
        cured, info = apply_shadow_setup_step_pure(data, lambda: 1)
        self.assertEqual(info["field_result"]["cure_route"], "plant_cure_item")
        self.assertFalse(cured["farm_patches"][PATCH]["diseased"])
        self.assertEqual(cured["inventory"]["Plant cure"], 0)
        self.assertEqual(cured["farming_exp"], 0)
        data["farm_plans"][PATCH] = {"crop_id": "red_blossom", "cure_intent": False}
        waited, info = apply_shadow_setup_step_pure(data, lambda: 1)
        self.assertEqual(info["status"], "waiting")
        self.assertEqual(waited, data)
        # A nonmatching plan must not suppress the default item route.
        data["farm_plans"][PATCH]["crop_id"] = "green_blossom"
        self.assertEqual(shadow_setup_preview_pure(data)["status"], "field")

    def test_real_spell_preference_fallback_admission_and_rune_costs(self):
        data = established_state(diseased=True)
        data.update(magic_level=66, magic_exp=0.0, quests={"lunar_diplomacy": {"completed": True}})
        data["inventory"].update({"Astral rune": 1, "Earth rune": 8, "Plant cure": 1})
        data["farm_plans"][PATCH] = {"crop_id": "red_blossom", "cure_route_preference": farm.CURE_PLANT_SPELL_FIRST}
        cured, info = apply_shadow_setup_step_pure(data, lambda: 1)
        self.assertEqual(info["field_result"]["cure_route"], "cure_plant_spell")
        self.assertEqual(cured["magic_exp"], 60)
        self.assertEqual(cured["inventory"]["Plant cure"], 1)
        self.assertEqual(cured["inventory"]["Astral rune"], 0)
        self.assertEqual(cured["inventory"]["Earth rune"], 0)
        # Spell first falls back to owned item if the spell fails admission.
        data["quests"] = {}
        cured, info = apply_shadow_setup_step_pure(data, lambda: 1)
        self.assertEqual(info["field_result"]["cure_route"], "plant_cure_item")
        self.assertEqual(cured["inventory"]["Astral rune"], 1)
        self.assertEqual(cured["inventory"]["Earth rune"], 8)
        # Item first still validates the real spell fallback.
        data["inventory"]["Plant cure"] = 0
        waited, info = apply_shadow_setup_step_pure(data, lambda: 1)
        self.assertEqual(info["status"], "waiting")
        self.assertEqual(waited, data)
        data["quests"] = {"lunar_diplomacy": {"completed": True}}
        data["farm_plans"][PATCH]["cure_route_preference"] = farm.PLANT_CURE_ITEM_FIRST
        self.assertEqual(apply_shadow_setup_step_pure(data, lambda: 1)[1]["field_result"]["cure_route"], "cure_plant_spell")

    def test_unavailable_cure_waits_and_dead_red_is_not_cured(self):
        data = established_state(diseased=True)
        before = copy.deepcopy(data)
        updated, info = apply_shadow_setup_step_pure(data, lambda: 1)
        self.assertEqual(info["status"], "waiting")
        self.assertEqual(updated, before)
        data["farm_patches"][PATCH]["dead"] = True
        data["inventory"]["Plant cure"] = 1
        updated, info = apply_shadow_setup_step_pure(data, lambda: 1)
        self.assertEqual(info["verb"], "clear")
        self.assertEqual(updated["inventory"]["Plant cure"], 1)

    def test_red_automatic_watering_needs_can_and_intent_without_extra_xp(self):
        for can in (None, "Watering can", "Watering can (8)"):
            for intent in (False, True):
                data = setup_state()
                if can:
                    data["inventory"][can] = 1
                data["farm_plans"][PATCH] = {"crop_id": "red_blossom", "watering_intent": intent}
                updated, _ = apply_shadow_setup_step_pure(data, lambda: 1)
                self.assertEqual(updated["farm_patches"][PATCH]["watered"], bool(can and intent))
                if can:
                    self.assertEqual(updated["inventory"][can], 1)
                self.assertEqual(updated["farming_exp"], 52)
        # A nonmatching plan uses ordinary default watering intent.
        data = setup_state()
        data["inventory"]["Watering can"] = 1
        data["farm_plans"][PATCH] = {"crop_id": "green_blossom", "watering_intent": False}
        self.assertTrue(apply_shadow_setup_step_pure(data, lambda: 1)[0]["farm_patches"][PATCH]["watered"])

    def test_disease_boundary_applies_water_factor_before_floor(self):
        # Six slots become floor(6 * .9) == 5, separating these exact rolls.
        for watered in (False, True):
            data = established_state(stage=1, watered=watered)
            data["farm_clock_minutes"] = 5
            grown, _ = farm.advance_farm_clock_pure(data, 5, lambda: 5.5 / 128)
            self.assertEqual(grown["farm_patches"][PATCH]["diseased"], not watered)
        # Green remains unwatered when planted, preserving other crop behavior.
        data = setup_state()
        data["inventory"].update({"Green blossom seed": 1, "Watering can": 1})
        green, ok, _ = farm.execute_farm_field_step_pure(data, {"kind": "plant", "patch_id": PATCH, "crop_id": "green_blossom"})
        self.assertTrue(ok)
        self.assertFalse(green["farm_patches"][PATCH]["watered"])
        self.assertEqual((FARMING_CROPS_BY_ID["red_blossom"].stages, FARMING_CROPS_BY_ID["red_blossom"].stage_minutes), (4, 5))
