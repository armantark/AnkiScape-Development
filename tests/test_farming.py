import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

import farming_logic
from constants import (
    FARMING_COMPOST_STATE_IMAGES,
    FARMING_HUD_SPROUT_ICON,
    FARMING_ITEM_IMAGES,
    FARMING_PATCH_STATE_IMAGES,
    ITEM_DEFINITIONS,
    ORE_DATA,
)
from farming_data import (
    COMPOST_BIN_CAPACITY,
    COMPOST_TIERS,
    FARMING_ASSET_MANIFEST,
    FARMING_COMPOST_BINS,
    FARMING_CROPS,
    FARMING_CROPS_BY_ID,
    FARMING_ITEM_DATA,
    FARMING_PATCHES,
    FARMING_SOURCE_BLOCKED,
)
from farming_logic import (
    CURE_PLANT_SPELL_FIRST,
    PLANT_CURE_ITEM_FIRST,
    activate_juju_farming_potion_pure,
    add_farm_queue_step_pure,
    apply_farming_frontend_action_pure,
    farming_frontend_projection_pure,
    advance_farm_clock_pure,
    apply_farming_review_with_queue_pure,
    collect_compost_bin_pure,
    consume_next_farm_queue_step_pure,
    default_farming_state_pure,
    delete_farm_preset_pure,
    duplicate_farm_preset_pure,
    execute_farm_field_step_pure,
    fill_compost_bin_pure,
    harvest_save_slots_pure,
    make_saplings_pure,
    pay_farming_protection_pure,
    queue_full_run_pure,
    queue_harvest_and_replant_same_pure,
    rename_farm_preset_pure,
    remove_farm_queue_step_pure,
    reorder_farm_queue_step_pure,
    roll_variable_harvest_count_pure,
    sanitize_farming_state_pure,
    save_farm_preset_pure,
    select_farm_preset_pure,
    set_farm_plan_pure,
    apply_farm_preset_pure,
)
from item_registry import item_definitions_by_id, item_definitions_by_storage_key
from shop_data import SHOP_DATA
from skill_registry import get_skill, review_handler_key
from storage_pure import CURRENT_CONFIG_VERSION, migrate_loaded_data
from tools.fetch_farming_assets import asset_manifest, interface_asset_manifest, item_asset_manifest
from tools.generate_npc_shop_data import SHOP_STOCK_EXCLUDED_ITEM_IDS


def _state(level=99):
    data = {
        "inventory": {},
        "farming_level": level,
        "farming_exp": 0.0,
        "woodcutting_level": 99,
        "woodcutting_exp": 0.0,
        "toolbelt": {"woodcutting": ["bronze_hatchet"]},
    }
    data.update(default_farming_state_pure())
    return data


def _plant_ready(data, patch_id="falador_allotment_north", crop_id="potato", compost="none"):
    crop = FARMING_CROPS_BY_ID[crop_id]
    data["inventory"].update({"Rake": 1, "Seed dibber": 1, "Spade": 1, crop.seed_item: crop.seeds})
    if COMPOST_TIERS[compost].item:
        data["inventory"][COMPOST_TIERS[compost].item] = 1
    planted, ok, _ = execute_farm_field_step_pure(
        data,
        {"kind": "plant", "patch_id": patch_id, "crop_id": crop_id, "compost_tier": compost},
    )
    if not ok:
        raise AssertionError("test planting failed")
    return planted


class TestFarmingData(unittest.TestCase):
    def test_repeatable_inventory_is_exact_and_stable(self):
        self.assertEqual(len(FARMING_PATCHES), 52)
        self.assertEqual(len({row.id for row in FARMING_PATCHES}), 52)
        self.assertEqual(len(FARMING_COMPOST_BINS), 6)
        self.assertEqual(len({row.id for row in FARMING_COMPOST_BINS}), 6)
        spirit_slots = [row for row in FARMING_PATCHES if row.patch_type == "spirit_tree"]
        self.assertEqual(len(spirit_slots), 2)
        self.assertEqual(spirit_slots[0].location_options, ("Etceteria", "East Port Sarim", "North Brimhaven"))
        white_tree = next(row for row in FARMING_PATCHES if row.id == "varrock_white_tree")
        self.assertEqual(white_tree.fixed_crop_id, "white_tree")
        self.assertEqual(white_tree.access_gate.key, "garden_of_tranquillity")

    def test_pinned_corrections_are_frozen(self):
        self.assertEqual(dict(FARMING_CROPS_BY_ID["sweetcorn"].protection.items), {"Jute fibre": 10})
        self.assertEqual(dict(FARMING_CROPS_BY_ID["strawberry"].protection.items), {"Apples (5)": 1})
        self.assertEqual(dict(FARMING_CROPS_BY_ID["watermelon"].protection.items), {"Curry leaf": 10})
        self.assertEqual(FARMING_CROPS_BY_ID["jute"].seeds, 3)
        self.assertEqual(FARMING_CROPS_BY_ID["scarecrow"].level, 23)
        self.assertEqual(FARMING_CROPS_BY_ID["willow"].check_health_xp, 1456.3)
        self.assertEqual(FARMING_CROPS_BY_ID["lantadyme"].planting_xp, 134.5)
        fruit_checks = [FARMING_CROPS_BY_ID[key].check_health_xp for key in ("apple", "banana", "orange", "curry", "pineapple", "papaya", "palm")]
        self.assertEqual(fruit_checks, [1199.5, 1750.5, 2470.2, 2906.9, 4605.7, 6146.4, 10150.1])
        self.assertEqual((FARMING_CROPS_BY_ID["calquat"].stages, FARMING_CROPS_BY_ID["calquat"].stage_minutes), (8, 160))
        self.assertEqual((FARMING_CROPS_BY_ID["belladonna"].stages, FARMING_CROPS_BY_ID["belladonna"].stage_minutes), (4, 80))
        self.assertEqual(FARMING_CROPS_BY_ID["lergberry"].harvest_xp, 31.5)
        self.assertEqual(FARMING_CROPS_BY_ID["kalferberry"].harvest_xp, 52.5)
        self.assertTrue(FARMING_CROPS_BY_ID["jade_vine"].runnable)
        self.assertTrue(FARMING_CROPS_BY_ID["evil_turnip"].runnable)
        self.assertEqual(COMPOST_TIERS["compost"].source_range_minutes, (35, 50))
        self.assertEqual(COMPOST_TIERS["compost"].maturation_minutes, 45)
        self.assertEqual(COMPOST_TIERS["supercompost"].maturation_minutes, 90)
        self.assertEqual((COMPOST_TIERS["compost"].application_xp, COMPOST_TIERS["supercompost"].application_xp), (18.0, 26.0))
        # Compost oldid 6337625; Jade vine oldid 6579442; Darkan 7e7d67b FarmPatch.java:455-483.
        self.assertEqual(FARMING_CROPS_BY_ID["jade_vine"].regrowth_range_minutes, (30, 60))
        for crop_id in ("cactus", "bittercap", "morchella", "belladonna", "jade_vine"):
            self.assertEqual(FARMING_CROPS_BY_ID[crop_id].disease_slots, 6)
            self.assertTrue(any("FarmPatch.java:455-483" in source for source in FARMING_CROPS_BY_ID[crop_id].sources))
        white_tree = FARMING_CROPS_BY_ID["white_tree"]
        self.assertEqual(
            (white_tree.fixed_yield, white_tree.harvest_xp, white_tree.regrowth_minutes),
            (4, 12.0, 6),
        )
        self.assertIsNone(white_tree.harvest_tool)

    def test_unresolved_rows_are_explicitly_non_runnable(self):
        expected = {
            "white_lily": "planting_xp",
            "spirit_tree": "stage_minutes",
            "wergali": "harvest_xp",
            "goutweed": "yield",
            "red_blossom": "stage_minutes",
            "kalferberry": "planting_xp",
        }
        for crop_id, blocked_field in expected.items():
            crop = FARMING_CROPS_BY_ID[crop_id]
            self.assertIn(blocked_field, crop.source_blocked)
            self.assertFalse(crop.runnable)
        for crop_id in ("red_blossom", "blue_blossom", "green_blossom", "erzille", "argway", "ugune", "shengo", "samaden", "lergberry", "kalferberry"):
            self.assertTrue(FARMING_CROPS_BY_ID[crop_id].source_blocked)
            self.assertFalse(FARMING_CROPS_BY_ID[crop_id].runnable)
        self.assertEqual(
            set(FARMING_SOURCE_BLOCKED),
            {"watering_growth_multiplier", "watering_yield_effect"},
        )
        self.assertNotIn("Patch bomb", FARMING_ITEM_DATA)
        self.assertEqual(len(FARMING_ASSET_MANIFEST), len(FARMING_ITEM_DATA))

    def test_every_data_row_has_a_unique_stable_id_and_source_citation(self):
        self.assertEqual(len(FARMING_CROPS), len(FARMING_CROPS_BY_ID))
        for row in (*FARMING_CROPS, *FARMING_PATCHES, *FARMING_COMPOST_BINS):
            self.assertRegex(row.id, r"^[a-z0-9_]+$")
            self.assertTrue(row.sources)
        self.assertEqual(
            len({row.item_id for row in FARMING_ASSET_MANIFEST}),
            len(FARMING_ASSET_MANIFEST),
        )

    def test_data_mappings_are_immutable(self):
        with self.assertRaises(TypeError):
            FARMING_CROPS_BY_ID["potato"] = FARMING_CROPS_BY_ID["onion"]


class TestFarmingStorageAndRegistry(unittest.TestCase):
    def test_v31_migration_adds_farm_state_and_preserves_unknown_data(self):
        loaded = {
            "config_version": 31,
            "future_top_level": {"keep": True},
            "inventory": {"Mystery seed": 7},
            "farm_patches": {
                "falador_allotment_north": {"crop_id": None, "future_patch_key": "keep"},
                "future_patch": {"alien": True},
            },
        }
        migrated = migrate_loaded_data(loaded, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["farming_level"], 1)
        self.assertEqual(migrated["farming_exp"], 0)
        self.assertEqual(
            len(
                [
                    key
                    for key in migrated["farm_patches"]
                    if key in {row.id for row in FARMING_PATCHES}
                ]
            ),
            52,
        )
        self.assertEqual(
            len(
                [
                    key
                    for key in migrated["farm_compost_bins"]
                    if key in {row.id for row in FARMING_COMPOST_BINS}
                ]
            ),
            6,
        )
        self.assertEqual(migrated["inventory"]["Mystery seed"], 7)
        self.assertEqual(migrated["future_top_level"], {"keep": True})
        self.assertEqual(
            migrated["farm_patches"]["falador_allotment_north"][
                "future_patch_key"
            ],
            "keep",
        )
        self.assertEqual(
            migrated["farm_patches"]["future_patch"],
            {"alien": True},
        )
        self.assertNotIn("current_farming", migrated)

    def test_white_tree_is_a_quest_gated_permanent_harvest_and_full_run_step(self):
        locked = sanitize_farming_state_pure(_state())
        self.assertIsNone(locked["farm_patches"]["varrock_white_tree"]["crop_id"])

        unlocked = _state(level=25)
        unlocked["quests"] = {"garden_of_tranquillity": {"completed": True}}
        unlocked.update(sanitize_farming_state_pure(unlocked))
        record = unlocked["farm_patches"]["varrock_white_tree"]
        self.assertEqual(record["crop_id"], "white_tree")
        self.assertEqual(record["produce_count"], 4)

        queued, step_ids = queue_full_run_pure(unlocked)
        self.assertEqual(len(step_ids), 1)
        self.assertEqual(
            queued["farm_queue"][0],
            {
                "id": step_ids[0],
                "kind": "harvest",
                "patch_id": "varrock_white_tree",
            },
        )

        harvested, consumed, info = apply_farming_review_with_queue_pure(queued)
        self.assertTrue(consumed)
        self.assertEqual(info["outputs"], {"White tree fruit": 4})
        self.assertEqual(harvested["inventory"]["White tree fruit"], 4)
        self.assertEqual(harvested["farming_exp"], 48.0)
        self.assertEqual(
            harvested["farm_patches"]["varrock_white_tree"]["produce_count"],
            0,
        )

        regrown_one, _ = advance_farm_clock_pure(harvested, 1)
        self.assertEqual(
            regrown_one["farm_patches"]["varrock_white_tree"][
                "produce_count"
            ],
            1,
        )
        regrown, _ = advance_farm_clock_pure(regrown_one, 3)
        self.assertEqual(
            regrown["farm_patches"]["varrock_white_tree"]["produce_count"],
            4,
        )

    def test_sanitation_repairs_known_rows_without_dropping_unknown_rows(self):
        state = sanitize_farming_state_pure({
            "farm_clock_minutes": -5,
            "farm_patches": {"falador_allotment_north": {"crop_id": "bogus", "stage": "bad"}, "future": {"x": 1}},
            "farm_compost_bins": {"falador_bin": {"status": "bogus"}, "future": {"x": 2}},
            "farm_queue": [None, {"id": "x", "kind": "future_action", "future": True}],
        })
        self.assertEqual(state["farm_clock_minutes"], 0)
        self.assertIsNone(state["farm_patches"]["falador_allotment_north"]["crop_id"])
        self.assertEqual(state["farm_patches"]["future"], {"x": 1})
        self.assertEqual(state["farm_compost_bins"]["future"], {"x": 2})
        self.assertEqual(state["farm_queue"], [{"id": "x", "kind": "future_action", "future": True}])

    def test_v38_migration_adds_preset_state_and_plan_policy_defaults(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 38,
                "inventory": {},
                "farm_plans": {
                    "falador_allotment_north": {
                        "crop_id": "potato",
                        "compost_tier": "none",
                    },
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["farm_presets"], {})
        self.assertEqual(migrated["farm_preset_order"], [])
        self.assertIsNone(migrated["farm_selected_preset"])
        self.assertTrue(
            migrated["farm_plans"]["falador_allotment_north"]["watering_intent"]
        )
        self.assertTrue(
            migrated["farm_plans"]["falador_allotment_north"]["cure_intent"]
        )
        self.assertEqual(
            migrated["farm_plans"]["falador_allotment_north"]["cure_route_preference"],
            PLANT_CURE_ITEM_FIRST,
        )

    def test_registry_and_every_farming_item_are_registered_without_a_target(self):
        farming = get_skill("farming")
        self.assertTrue(farming.implemented)
        self.assertTrue(farming.trainable)
        self.assertFalse(farming.participates_in_review)
        self.assertIsNone(farming.current_target_key)
        self.assertIsNone(review_handler_key("farming"))
        definitions = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        self.assertTrue(set(FARMING_ITEM_DATA).issubset(definitions))

    def test_asset_manifest_ids_join_canonical_registry_items(self):
        definitions_by_id = item_definitions_by_id(ITEM_DEFINITIONS)
        bindings = item_asset_manifest()
        self.assertEqual(len(bindings), len(FARMING_ITEM_DATA))
        for binding in bindings:
            self.assertIn(binding.item_id, definitions_by_id)
            self.assertEqual(definitions_by_id[binding.item_id].storage_key, binding.item_name)
        self.assertFalse(any("patch bomb" in binding.item_name.lower() for binding in asset_manifest()))

    def test_every_farming_asset_path_and_provenance_entry_exists(self):
        root = Path(__file__).resolve().parents[1]
        with (root / "assets_provenance.json").open(encoding="utf-8") as file_obj:
            provenance = json.load(file_obj)
        for binding in asset_manifest():
            self.assertTrue(binding.output_path.exists(), binding.output_path)
            self.assertIn(str(binding.output_path.relative_to(root)), provenance)

        definitions = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        self.assertEqual(set(FARMING_ITEM_IMAGES), set(FARMING_ITEM_DATA))
        for item_name in FARMING_ITEM_DATA:
            self.assertEqual(definitions[item_name].asset_path, FARMING_ITEM_IMAGES[item_name])
            self.assertTrue(Path(FARMING_ITEM_IMAGES[item_name]).exists(), item_name)

    def test_patch_compost_and_hud_visual_manifests_are_complete(self):
        self.assertEqual(set(FARMING_PATCH_STATE_IMAGES), {"empty", "growing", "ready", "diseased", "dead", "stump"})
        self.assertEqual(set(FARMING_COMPOST_STATE_IMAGES), {"empty", "filling", "ready"})
        self.assertTrue(Path(FARMING_HUD_SPROUT_ICON).exists())
        for binding in interface_asset_manifest():
            self.assertTrue(binding.output_path.exists(), binding.asset_id)

    def test_crop_and_shop_references_use_single_canonical_inventory_keys(self):
        references = set()
        for crop in FARMING_CROPS:
            references.add(crop.seed_item)
            if crop.output_item:
                references.add(crop.output_item)
            if crop.root_item:
                references.add(crop.root_item)
            if crop.protection:
                references.update(item for item, _amount in crop.protection.items)
        definitions_by_name = {}
        for definition in ITEM_DEFINITIONS:
            definitions_by_name.setdefault(definition.storage_key, []).append(definition)
        for item_name in references:
            self.assertIn(item_name, definitions_by_name)
            self.assertEqual(len(definitions_by_name[item_name]), 1, item_name)
        for shop in SHOP_DATA.values():
            for row in shop["stock"]:
                if row["item_name"] in references:
                    self.assertEqual(definitions_by_name[row["item_name"]][0].storage_key, row["item_name"])

    def test_papa_mambo_keeps_only_blossom_seeds(self):
        stock = {row["item_name"] for row in SHOP_DATA["papa_mambos_shop"]["stock"]}
        self.assertTrue({"Red blossom seed", "Blue blossom seed", "Green blossom seed"}.issubset(stock))
        self.assertTrue({"Erzille seed", "Ugune seed", "Argway seed", "Shengo seed", "Samaden seed"}.isdisjoint(stock))
        self.assertEqual(SHOP_STOCK_EXCLUDED_ITEM_IDS["papa_mambos_shop"], frozenset({19897, 19902, 19907, 19912, 19917}))

    def test_twenty_contract_inputs_have_no_invented_live_shop_route(self):
        crop_ids = (
            "nasturtium", "woad", "white_lily", "goutweed", "spirit_weed", "wergali", "fellstalk",
            "redberry", "cadavaberry", "dwellberry", "bittercap", "morchella", "evil_turnip",
            "erzille", "ugune", "argway", "shengo", "samaden", "lergberry", "kalferberry",
        )
        self.assertEqual(len(crop_ids), 20)
        live_stock = {
            row["item_name"]
            for shop in SHOP_DATA.values()
            for row in shop["stock"]
            if row["disposition"] == "live"
        }
        for crop_id in crop_ids:
            self.assertNotIn(FARMING_CROPS_BY_ID[crop_id].seed_item, live_stock)


class TestFarmingClockAndActions(unittest.TestCase):
    def test_clock_advances_six_minutes_and_eagerly_crosses_all_boundaries(self):
        planted = _plant_ready(_state())
        advanced, info = advance_farm_clock_pure(planted, 7, lambda: 1.0)
        record = advanced["farm_patches"]["falador_allotment_north"]
        self.assertEqual(info["minutes"], 42)
        self.assertEqual(advanced["farm_clock_minutes"], 42)
        self.assertEqual(record["stage"], 4)
        self.assertTrue(any(event["event"] == "crop_ready" for event in info["events"]))

    def test_first_stage_is_immune_then_disease_kills_at_next_boundary(self):
        planted = _plant_ready(_state())
        first, _ = advance_farm_clock_pure(planted, 2, lambda: 0.0)
        self.assertEqual(first["farm_patches"]["falador_allotment_north"]["stage"], 1)
        self.assertFalse(first["farm_patches"]["falador_allotment_north"]["diseased"])
        diseased, _ = advance_farm_clock_pure(first, 2, lambda: 0.0)
        self.assertTrue(diseased["farm_patches"]["falador_allotment_north"]["diseased"])
        dead, _ = advance_farm_clock_pure(diseased, 2, lambda: 1.0)
        self.assertTrue(dead["farm_patches"]["falador_allotment_north"]["dead"])

    def test_watering_applies_settled_point_nine_disease_factor(self):
        unwatered = _plant_ready(_state())
        watered_state = _state()
        watered_state["inventory"]["Watering can"] = 1
        watered = _plant_ready(watered_state)

        unwatered, _ = advance_farm_clock_pure(unwatered, 4, lambda: 0.22)
        watered, _ = advance_farm_clock_pure(watered, 4, lambda: 0.22)

        self.assertTrue(unwatered["farm_patches"]["falador_allotment_north"]["diseased"])
        self.assertFalse(watered["farm_patches"]["falador_allotment_north"]["diseased"])

    def test_large_clock_tick_eagerly_processes_disease_and_the_crossed_death_boundary(self):
        advanced, _ = advance_farm_clock_pure(_plant_ready(_state()), 7, lambda: 0.0)
        record = advanced["farm_patches"]["falador_allotment_north"]
        self.assertTrue(record["dead"])
        self.assertFalse(record["diseased"])

    def test_paid_protection_and_compost_lives_are_applied_at_plant(self):
        data = _state()
        data["inventory"].update({"Jute fibre": 10, "Rake": 1, "Seed dibber": 1, "Sweetcorn seed": 3, "Supercompost": 1})
        planned, ok, _ = set_farm_plan_pure(data, "falador_allotment_north", "sweetcorn", "supercompost", True)
        self.assertTrue(ok)
        paid, ok, _ = pay_farming_protection_pure(planned, "falador_allotment_north")
        self.assertTrue(ok)
        planted, ok, info = execute_farm_field_step_pure(
            paid,
            {"kind": "plant", "patch_id": "falador_allotment_north", "crop_id": "sweetcorn", "compost_tier": "supercompost"},
        )
        self.assertTrue(ok)
        record = planted["farm_patches"]["falador_allotment_north"]
        self.assertTrue(record["protected"])
        self.assertEqual(record["lives"], 5)
        self.assertEqual(info["farming_xp"], 43.0)
        safe, _ = advance_farm_clock_pure(planted, 20, lambda: 0.0)
        self.assertFalse(safe["farm_patches"]["falador_allotment_north"]["dead"])

    def test_plant_bundle_consumes_materials_adds_weeds_and_cure_awards_zero_xp(self):
        planted = _plant_ready(_state(), compost="compost")
        self.assertEqual(planted["inventory"]["Potato seed"], 0)
        self.assertEqual(planted["inventory"]["Compost"], 0)
        self.assertEqual(planted["inventory"]["Weeds"], 3)
        self.assertEqual(planted["farming_exp"], 26.0)
        self.assertEqual(planted["farming_counters"]["plants"], 1)
        planted["farm_patches"]["falador_allotment_north"]["diseased"] = True
        planted["inventory"]["Plant cure"] = 1
        cured, ok, info = execute_farm_field_step_pure(planted, {"kind": "cure", "patch_id": "falador_allotment_north"})
        self.assertTrue(ok)
        self.assertEqual(info["farming_xp"], 0.0)
        self.assertEqual(cured["farming_exp"], planted["farming_exp"])

    def test_cure_preference_uses_preferred_route_then_falls_back_atomically(self):
        base = _plant_ready(_state(), compost="compost")
        patch_id = "falador_allotment_north"
        base["farm_patches"][patch_id]["diseased"] = True
        base["magic_level"] = 66
        base["magic_exp"] = 0.0
        base["quests"] = {"lunar_diplomacy": {"completed": True}}
        base["inventory"].update({
            "Plant cure": 1,
            "Astral rune": 1,
            "Earth rune": 8,
        })

        spell_first, ok, _ = set_farm_plan_pure(
            base,
            patch_id,
            "potato",
            cure_route_preference=CURE_PLANT_SPELL_FIRST,
        )
        self.assertTrue(ok)
        queued, ids = queue_full_run_pure(spell_first)
        self.assertEqual(len(ids), 1)
        self.assertEqual(
            queued["farm_queue"][0]["cure_route_preference"],
            CURE_PLANT_SPELL_FIRST,
        )
        cured, consumed, info = apply_farming_review_with_queue_pure(
            queued, lambda: 1.0
        )
        self.assertTrue(consumed)
        self.assertEqual(info["cure_route"], "cure_plant_spell")
        self.assertEqual(cured["magic_exp"], 60.0)
        self.assertEqual(cured["inventory"]["Plant cure"], 1)
        self.assertEqual(cured["inventory"]["Astral rune"], 0)
        self.assertEqual(cured["inventory"]["Earth rune"], 0)

        item_fallback = copy.deepcopy(spell_first)
        item_fallback["farm_patches"][patch_id]["diseased"] = True
        item_fallback["inventory"]["Astral rune"] = 0
        item_fallback["inventory"]["Earth rune"] = 0
        queued, _ = queue_full_run_pure(item_fallback)
        cured, consumed, info = apply_farming_review_with_queue_pure(
            queued, lambda: 1.0
        )
        self.assertTrue(consumed)
        self.assertEqual(info["cure_route"], "plant_cure_item")
        self.assertEqual(cured["magic_exp"], 0.0)
        self.assertEqual(cured["inventory"]["Plant cure"], 0)

    def test_item_first_falls_back_to_cure_plant_and_queue_snapshots_preference(self):
        patch_id = "falador_allotment_north"
        base = _plant_ready(_state(), compost="compost")
        base["farm_patches"][patch_id]["diseased"] = True
        base["magic_level"] = 66
        base["magic_exp"] = 0.0
        base["quests"] = {"lunar_diplomacy": {"completed": True}}
        base["inventory"].update({"Astral rune": 1, "Earth rune": 8})
        planned, ok, _ = set_farm_plan_pure(
            base,
            patch_id,
            "potato",
            cure_route_preference=PLANT_CURE_ITEM_FIRST,
        )
        self.assertTrue(ok)
        queued, _ = queue_full_run_pure(planned)
        changed, ok, _ = set_farm_plan_pure(
            queued,
            patch_id,
            "potato",
            cure_route_preference=CURE_PLANT_SPELL_FIRST,
        )
        self.assertTrue(ok)
        self.assertEqual(
            changed["farm_queue"][0]["cure_route_preference"],
            PLANT_CURE_ITEM_FIRST,
        )

        cured, consumed, info = apply_farming_review_with_queue_pure(
            changed, lambda: 1.0
        )
        self.assertTrue(consumed)
        self.assertEqual(info["cure_route"], "cure_plant_spell")
        self.assertEqual(cured["magic_exp"], 60.0)

    def test_cure_preference_is_part_of_farming_preset_snapshots(self):
        patch_id = "falador_allotment_north"
        state = _state()
        state, ok, _ = set_farm_plan_pure(
            state,
            patch_id,
            "potato",
            cure_route_preference=CURE_PLANT_SPELL_FIRST,
        )
        self.assertTrue(ok)
        saved, ok, _ = save_farm_preset_pure(state, "Spell cure", [patch_id])
        self.assertTrue(ok)
        preset_id = saved["farm_selected_preset"]
        self.assertEqual(
            saved["farm_presets"][preset_id]["plans"][patch_id]["cure_route_preference"],
            CURE_PLANT_SPELL_FIRST,
        )

        changed, ok, _ = set_farm_plan_pure(
            saved,
            patch_id,
            "potato",
            cure_route_preference=PLANT_CURE_ITEM_FIRST,
        )
        self.assertTrue(ok)
        self.assertTrue(farming_frontend_projection_pure(changed)["presets"]["modified"])
        applied, ok, _ = apply_farm_preset_pure(changed, preset_id)
        self.assertTrue(ok)
        self.assertEqual(
            applied["farm_plans"][patch_id]["cure_route_preference"],
            CURE_PLANT_SPELL_FIRST,
        )

    def test_exact_save_slot_loop_and_whole_patch_harvest(self):
        potato = FARMING_CROPS_BY_ID["potato"]
        self.assertEqual(harvest_save_slots_pure(potato, 1, False), 130)
        self.assertEqual(harvest_save_slots_pure(potato, 1, True), 143)
        rolls = iter((0.0, 1.0) * 3)
        self.assertEqual(roll_variable_harvest_count_pure(3, 128, lambda: next(rolls)), 6)
        ready, _ = advance_farm_clock_pure(_plant_ready(_state()), 7, lambda: 1.0)
        rolls = iter((1.0, 1.0, 1.0))
        harvested, ok, info = execute_farm_field_step_pure(
            ready,
            {"kind": "harvest", "patch_id": "falador_allotment_north"},
            lambda: next(rolls),
        )
        self.assertTrue(ok)
        self.assertEqual(info["outputs"], {"Potato": 3})
        self.assertEqual(info["farming_xp"], 27.0)
        self.assertEqual(harvested["farming_counters"]["produce_harvested"], 3)
        self.assertIsNone(harvested["farm_patches"]["falador_allotment_north"]["crop_id"])

    def test_fixed_yield_crop_regrows_one_item_per_settled_interval(self):
        data = _state()
        data["inventory"].update({"Rake": 1, "Seed dibber": 1, "Spade": 1, "Redberry seed": 1})
        planted, ok, _ = execute_farm_field_step_pure(
            data,
            {"kind": "plant", "patch_id": "champions_bush", "crop_id": "redberry"},
        )
        self.assertTrue(ok)
        ready, _ = advance_farm_clock_pure(planted, 17, lambda: 1.0)
        ready, ok, _ = execute_farm_field_step_pure(
            ready,
            {"kind": "check_health", "patch_id": "champions_bush"},
        )
        self.assertTrue(ok)
        harvested, ok, info = execute_farm_field_step_pure(
            ready,
            {"kind": "harvest", "patch_id": "champions_bush"},
        )
        self.assertTrue(ok)
        self.assertEqual(info["outputs"], {"Redberries": 4})
        self.assertEqual(harvested["farm_patches"]["champions_bush"]["produce_count"], 0)
        regrown, _ = advance_farm_clock_pure(harvested, 4, lambda: 1.0)
        self.assertEqual(regrown["farm_patches"]["champions_bush"]["produce_count"], 1)

    def test_check_health_and_clear_stump_transactions(self):
        data = _state()
        data["inventory"].update({"Rake": 1, "Spade": 1, "Oak sapling": 1})
        planted, ok, _ = execute_farm_field_step_pure(data, {"kind": "plant", "patch_id": "lumbridge_tree", "crop_id": "oak"})
        self.assertTrue(ok)
        ready, _ = advance_farm_clock_pure(planted, 34, lambda: 1.0)
        checked, ok, info = execute_farm_field_step_pure(ready, {"kind": "check_health", "patch_id": "lumbridge_tree"})
        self.assertTrue(ok)
        self.assertEqual(info["farming_xp"], 467.3)
        self.assertEqual(checked["farming_counters"]["tree_health_checks"], 1)
        chopped, ok, info = execute_farm_field_step_pure(checked, {"kind": "chop", "patch_id": "lumbridge_tree"})
        self.assertTrue(ok)
        self.assertEqual(info["outputs"], {"Oak logs": 1})
        cleared, ok, info = execute_farm_field_step_pure(chopped, {"kind": "clear", "patch_id": "lumbridge_tree"})
        self.assertTrue(ok)
        self.assertEqual(info["outputs"], {"Oak roots": 1})
        self.assertIsNone(cleared["farm_patches"]["lumbridge_tree"]["crop_id"])


class TestFarmingQueueAndTransactions(unittest.TestCase):
    def test_queue_ids_reorder_remove_and_invalid_skip_are_durable(self):
        data, first, _ = add_farm_queue_step_pure(_state(), "harvest", "falador_allotment_north")
        data, second, _ = add_farm_queue_step_pure(data, "clear", "falador_allotment_north")
        self.assertEqual((first, second), ("farm_step_00000001", "farm_step_00000002"))
        reordered, ok = reorder_farm_queue_step_pure(data, second, 0)
        self.assertTrue(ok)
        self.assertEqual([row["id"] for row in reordered["farm_queue"]], [second, first])
        removed, ok = remove_farm_queue_step_pure(reordered, first)
        self.assertTrue(ok)
        consumed, did_consume, info = consume_next_farm_queue_step_pure(removed)
        self.assertTrue(did_consume)
        self.assertEqual(info["status"], "skipped")
        self.assertEqual(consumed["farm_queue"], [])
        self.assertEqual(consumed["farming_counters"]["queue_steps_skipped"], 1)
        self.assertEqual(consumed["farm_event_log"][-1]["event"], "queue_step_skipped")

    def test_harvest_replant_shortcut_and_full_run_use_player_plan(self):
        data = _plant_ready(_state())
        planned, ok, _ = set_farm_plan_pure(data, "falador_allotment_north", "potato", "compost")
        self.assertTrue(ok)
        ready, _ = advance_farm_clock_pure(planned, 7, lambda: 1.0)
        queued, ids, _ = queue_harvest_and_replant_same_pure(ready, "falador_allotment_north")
        self.assertEqual(len(ids), 2)
        self.assertEqual([row["kind"] for row in queued["farm_queue"]], ["harvest", "plant"])
        full, full_ids = queue_full_run_pure(ready)
        self.assertEqual(len(full_ids), 2)
        self.assertEqual([row["kind"] for row in full["farm_queue"]], ["harvest", "plant"])
        self.assertEqual(full["farm_queue"][1]["crop_id"], "potato")
        self.assertEqual(full["farming_counters"]["full_runs"], 1)

    def test_execution_time_material_validation_skips_after_earlier_use(self):
        data = _state()
        data["inventory"].update({"Rake": 1, "Seed dibber": 1, "Potato seed": 3})
        data, _, _ = add_farm_queue_step_pure(data, "plant", "falador_allotment_north", crop_id="potato")
        data, _, _ = add_farm_queue_step_pure(data, "plant", "catherby_allotment_north", crop_id="potato")
        after_first, consumed, first = consume_next_farm_queue_step_pure(data)
        self.assertTrue(consumed)
        self.assertEqual(first["status"], "executed")
        after_second, consumed, second = consume_next_farm_queue_step_pure(after_first)
        self.assertTrue(consumed)
        self.assertEqual(second["status"], "skipped")
        self.assertIn("missing seeds", second["message"])

    def test_successful_review_clock_and_queue_share_one_state_copy(self):
        data = _state()
        data["inventory"].update({"Rake": 1, "Seed dibber": 1, "Potato seed": 3})
        data, _, _ = add_farm_queue_step_pure(
            data, "plant", "falador_allotment_north", crop_id="potato"
        )

        class UnrelatedState:
            def __deepcopy__(self, _memo):
                raise AssertionError("unrelated player state must not be copied by a farm tick")

        unrelated = UnrelatedState()
        data["unrelated_state"] = unrelated
        with patch.object(
            farming_logic,
            "_copy_with_farm_state",
            wraps=farming_logic._copy_with_farm_state,
        ) as copy_state:
            updated, consumed, info = apply_farming_review_with_queue_pure(data)
        self.assertTrue(consumed)
        self.assertEqual(info["status"], "executed")
        self.assertEqual(updated["farm_clock_minutes"], 6)
        self.assertEqual(updated["farm_queue"], [])
        self.assertIs(updated["unrelated_state"], unrelated)
        self.assertEqual(copy_state.call_count, 1)

    def test_saplings_and_compost_bins_are_instant_transactions_with_clock_deadlines(self):
        data = _state()
        data["inventory"].update({"Acorn": 2, "Plant pot": 2, "Gardening trowel": 1, "Watering can": 1})
        started, count, _ = make_saplings_pure(data, "oak", 28)
        self.assertEqual(count, 2)
        self.assertEqual(started["inventory"]["Oak seedling"], 2)
        matured, _ = advance_farm_clock_pure(started, 1)
        self.assertEqual(matured["inventory"]["Oak seedling"], 0)
        self.assertEqual(matured["inventory"]["Oak sapling"], 2)

        matured["inventory"].update({"Potato": COMPOST_BIN_CAPACITY, "Bucket": COMPOST_BIN_CAPACITY})
        filled, ok, _ = fill_compost_bin_pure(matured, "falador_bin", "Potato", lambda: 0.625)
        self.assertTrue(ok)
        self.assertEqual(filled["farm_compost_bins"]["falador_bin"]["ready_at"], filled["farm_clock_minutes"] + 45)
        ready, _ = advance_farm_clock_pure(filled, 8)
        self.assertEqual(ready["farm_compost_bins"]["falador_bin"]["status"], "ready")
        collected, ok, _ = collect_compost_bin_pure(ready, "falador_bin")
        self.assertTrue(ok)
        self.assertEqual(collected["inventory"]["Compost"], 15)
        self.assertEqual(collected["farm_compost_bins"]["falador_bin"]["status"], "empty")

    def test_instant_plan_changes_are_outside_field_queue(self):
        original = _state()
        planned, ok, _ = set_farm_plan_pure(original, "falador_allotment_north", "potato", "supercompost", True)
        self.assertTrue(ok)
        self.assertEqual(original["farm_queue"], [])
        self.assertEqual(planned["farm_queue"], [])
        self.assertEqual(planned["farm_plans"]["falador_allotment_north"]["compost_tier"], "supercompost")
        self.assertNotEqual(original, planned)


class TestFarmingVerifiedRegressions(unittest.TestCase):
    def test_canonical_hops_and_fruit_sapling_storage_keys_match_live_registry(self):
        expected_hops = {
            "hammerstone": "Hammerstone seed",
            "asgarnian": "Asgarnian seed",
            "yanillian": "Yanillian seed",
            "krandorian": "Krandorian seed",
            "wildblood": "Wildblood seed",
        }
        expected_saplings = {
            "apple": "Apple sapling",
            "banana": "Banana sapling",
            "orange": "Orange sapling",
            "curry": "Curry sapling",
            "papaya": "Papaya sapling",
            "palm": "Palm sapling",
        }
        definitions = item_definitions_by_storage_key(ITEM_DEFINITIONS)
        for crop_id, item_name in {**expected_hops, **expected_saplings}.items():
            self.assertEqual(FARMING_CROPS_BY_ID[crop_id].seed_item, item_name)
            self.assertIn(item_name, definitions)

        for crop_id, item_name in expected_hops.items():
            data = _state()
            crop = FARMING_CROPS_BY_ID[crop_id]
            data["inventory"].update({"Rake": 1, "Seed dibber": 1, item_name: crop.seeds})
            planted, ok, _ = execute_farm_field_step_pure(data, {"kind": "plant", "patch_id": "lumbridge_hops", "crop_id": crop_id})
            self.assertTrue(ok, crop_id)
            self.assertEqual(planted["inventory"][item_name], 0)
        for crop_id, item_name in expected_saplings.items():
            data = _state()
            data["inventory"].update({"Rake": 1, "Spade": 1, item_name: 1})
            planted, ok, _ = execute_farm_field_step_pure(data, {"kind": "plant", "patch_id": "catherby_fruit", "crop_id": crop_id})
            self.assertTrue(ok, crop_id)
            self.assertEqual(planted["inventory"][item_name], 0)

    def test_source_blocked_crop_rejects_plan_queue_payment_and_sapling_before_mutation(self):
        data = _state()
        data["inventory"].update({"Monkey nuts": 5, "Monkey bar": 1, "Ground Suqah tooth": 1, "Spirit seed": 1, "Plant pot": 1, "Gardening trowel": 1, "Watering can": 1})
        before = copy.deepcopy(data["inventory"])
        planned, ok, _ = set_farm_plan_pure(data, "spirit_tree_primary", "spirit_tree", protection_intent=True)
        self.assertFalse(ok)
        queued, step_id, _ = add_farm_queue_step_pure(data, "plant", "spirit_tree_primary", crop_id="spirit_tree")
        self.assertIsNone(step_id)
        paid, ok, _ = pay_farming_protection_pure(planned, "spirit_tree_primary")
        self.assertFalse(ok)
        saplings, count, _ = make_saplings_pure(data, "spirit_tree")
        self.assertEqual(count, 0)
        self.assertEqual(queued["inventory"], before)
        self.assertEqual(paid["inventory"], before)
        self.assertEqual(saplings["inventory"], before)

    def test_structured_quest_region_skill_and_compound_gates_are_enforced(self):
        data = _state()
        blocked, ok, _ = set_farm_plan_pure(data, "harmony_allotment", "potato")
        self.assertFalse(ok)
        data["quests"] = {"the_great_brain_robbery": {"completed": True}}
        unlocked, ok, _ = set_farm_plan_pure(data, "harmony_allotment", "potato")
        self.assertTrue(ok)

        region_blocked, ok, _ = set_farm_plan_pure(data, "phasmatys_allotment_north", "potato")
        self.assertFalse(ok)
        data["unlocked_regions"] = ["morytania"]
        region_open, ok, _ = set_farm_plan_pure(data, "phasmatys_allotment_north", "potato")
        self.assertTrue(ok)

        data["agility_level"] = 54
        skill_blocked, ok, message = set_farm_plan_pure(data, "habitat_vine_herb_east", "ugune")
        self.assertFalse(ok)
        self.assertIn("access", message)
        data["agility_level"] = 55
        skill_open, ok, message = set_farm_plan_pure(data, "habitat_vine_herb_east", "ugune")
        self.assertFalse(ok)
        self.assertIn("source-blocked", message)

        data["farming_level"] = 86
        compound_blocked, ok, _ = set_farm_plan_pure(data, "spirit_tree_secondary", "spirit_tree")
        self.assertFalse(ok)
        data.setdefault("quests", {})["the_prisoner_of_glouphrie"] = {"completed": True}
        compound_source_blocked, ok, message = set_farm_plan_pure(data, "spirit_tree_secondary", "spirit_tree")
        self.assertFalse(ok)
        self.assertIn("source-blocked", message)
        self.assertNotEqual(blocked["farm_plans"], unlocked["farm_plans"])
        self.assertNotEqual(region_blocked["farm_plans"], region_open["farm_plans"])

    def test_habitat_east_patch_prepends_three_review_driven_agility_traversals(self):
        data = _state()
        data["agility_level"] = 55
        data["agility_exp"] = 0.0
        queued, step_id, message = add_farm_queue_step_pure(
            data,
            "harvest",
            "habitat_vine_herb_east",
        )
        self.assertIsNotNone(step_id)
        self.assertEqual(message, "queued")
        self.assertEqual(
            [step["kind"] for step in queued["farm_queue"][:4]],
            ["habitat_traverse", "habitat_traverse", "habitat_traverse", "harvest"],
        )
        for phase in range(3):
            queued, consumed, info = consume_next_farm_queue_step_pure(queued)
            self.assertTrue(consumed)
            self.assertEqual(info["kind"], "habitat_traverse")
            self.assertEqual(info["phase"], phase)
        self.assertEqual(queued["agility_exp"], 30.0)
        self.assertEqual(len(queued["farm_queue"]), 1)

    def test_compost_bin_region_gate_applies_to_fill_and_collect(self):
        data = _state()
        data["inventory"].update({"Potato": 15, "Bucket": 15})
        blocked, ok, _ = fill_compost_bin_pure(data, "phasmatys_bin", "Potato", lambda: 0.0)
        self.assertFalse(ok)
        data["unlocked_regions"] = ["morytania"]
        filled, ok, _ = fill_compost_bin_pure(data, "phasmatys_bin", "Potato", lambda: 0.0)
        self.assertTrue(ok)
        filled["farm_compost_bins"]["phasmatys_bin"]["status"] = "ready"
        filled["unlocked_regions"] = []
        collected, ok, _ = collect_compost_bin_pure(filled, "phasmatys_bin")
        self.assertFalse(ok)
        self.assertEqual(collected["inventory"]["Bucket"], 15)

    def test_semantic_planner_handles_empty_unplanned_regrower_tree_dead_and_stump_states(self):
        empty = _state()
        empty, ok, _ = set_farm_plan_pure(empty, "falador_allotment_north", "potato")
        self.assertTrue(ok)
        queued, ids = queue_full_run_pure(empty)
        self.assertEqual(len(ids), 1)
        self.assertEqual([step["kind"] for step in queued["farm_queue"]], ["plant"])

        unplanned = _plant_ready(_state(), "falador_allotment_north", "potato")
        unplanned, _ = advance_farm_clock_pure(unplanned, 7, lambda: 1.0)
        untouched, ids = queue_full_run_pure(unplanned)
        self.assertEqual(ids, ())
        self.assertEqual(untouched["farm_queue"], [])
        self.assertEqual(untouched["farming_counters"]["full_runs"], 0)

        regrower = _state()
        regrower["inventory"].update({"Rake": 1, "Seed dibber": 1, "Spade": 1, "Redberry seed": 1})
        regrower, ok, _ = set_farm_plan_pure(regrower, "champions_bush", "redberry")
        self.assertTrue(ok)
        regrower, ok, _ = execute_farm_field_step_pure(regrower, {"kind": "plant", "patch_id": "champions_bush", "crop_id": "redberry"})
        self.assertTrue(ok)
        regrower, _ = advance_farm_clock_pure(regrower, 17, lambda: 1.0)
        regrower, ok, _ = execute_farm_field_step_pure(regrower, {"kind": "check_health", "patch_id": "champions_bush"})
        self.assertTrue(ok)
        regrower, ok, _ = execute_farm_field_step_pure(regrower, {"kind": "harvest", "patch_id": "champions_bush"})
        self.assertTrue(ok)
        depleted, ids = queue_full_run_pure(regrower)
        self.assertEqual(ids, ())
        self.assertEqual(depleted["farm_queue"], [])

        tree = _state()
        tree["inventory"].update({"Rake": 1, "Spade": 1, "Oak sapling": 1})
        tree, ok, _ = set_farm_plan_pure(tree, "lumbridge_tree", "oak")
        self.assertTrue(ok)
        tree, ok, _ = execute_farm_field_step_pure(tree, {"kind": "plant", "patch_id": "lumbridge_tree", "crop_id": "oak"})
        self.assertTrue(ok)
        tree, _ = advance_farm_clock_pure(tree, 34, lambda: 1.0)
        tree_run, _ = queue_full_run_pure(tree)
        self.assertEqual([step["kind"] for step in tree_run["farm_queue"]], ["check_health", "chop", "clear", "plant"])
        tree["farm_patches"]["lumbridge_tree"]["dead"] = True
        dead_run, _ = queue_full_run_pure(tree)
        self.assertEqual([step["kind"] for step in dead_run["farm_queue"]], ["clear", "plant"])
        tree["farm_patches"]["lumbridge_tree"].update({"dead": False, "stump": True})
        stump_run, _ = queue_full_run_pure(tree)
        self.assertEqual([step["kind"] for step in stump_run["farm_queue"]], ["clear", "plant"])

        fruit = _state()
        fruit["inventory"].update({"Rake": 1, "Spade": 1, "Apple sapling": 1})
        fruit, ok, _ = set_farm_plan_pure(fruit, "catherby_fruit", "apple")
        self.assertTrue(ok)
        fruit, ok, _ = execute_farm_field_step_pure(fruit, {"kind": "plant", "patch_id": "catherby_fruit", "crop_id": "apple"})
        self.assertTrue(ok)
        fruit, _ = advance_farm_clock_pure(fruit, 160, lambda: 1.0)
        fruit_run, _ = queue_full_run_pure(fruit)
        self.assertEqual([step["kind"] for step in fruit_run["farm_queue"]], ["check_health", "harvest"])

    def test_dig_up_is_manual_zero_reward_and_full_run_replaces_a_different_regrower(self):
        state = _state()
        state["inventory"].update({
            "Rake": 1,
            "Seed dibber": 1,
            "Spade": 1,
            "Redberry seed": 1,
            "Cadavaberry seed": 1,
        })
        state, ok, _ = set_farm_plan_pure(state, "champions_bush", "redberry")
        self.assertTrue(ok)
        state, ok, _ = execute_farm_field_step_pure(
            state, {"kind": "plant", "patch_id": "champions_bush", "crop_id": "redberry"}
        )
        self.assertTrue(ok)
        state, _ = advance_farm_clock_pure(state, 17, lambda: 1.0)
        xp_before = state["farming_exp"]

        queued, ok, message = apply_farming_frontend_action_pure(
            state,
            "queue_action",
            {"patch_id": "champions_bush", "kind": "dig_up", "details": {}},
        )
        self.assertTrue(ok, message)
        self.assertEqual([step["kind"] for step in queued["farm_queue"]], ["dig_up"])
        dug, consumed, info = consume_next_farm_queue_step_pure(queued)
        self.assertTrue(consumed)
        self.assertEqual(info["status"], "executed")
        self.assertEqual(info["outputs"], {})
        self.assertEqual(dug["farming_exp"], xp_before)
        self.assertIsNone(dug["farm_patches"]["champions_bush"]["crop_id"])
        self.assertEqual(dug["farming_counters"]["dig_ups"], 1)

        state, ok, _ = set_farm_plan_pure(state, "champions_bush", "cadavaberry")
        self.assertTrue(ok)
        replacement, ids = queue_full_run_pure(state)
        self.assertEqual(len(ids), 2)
        self.assertEqual(
            [step["kind"] for step in replacement["farm_queue"]],
            ["dig_up", "plant"],
        )
        self.assertEqual(replacement["farm_queue"][1]["crop_id"], "cadavaberry")

    def test_full_run_pays_planned_gardener_or_skips_the_whole_patch(self):
        state = _state()
        state["inventory"].update({
            "Rake": 1,
            "Seed dibber": 1,
            "Potato seed": 3,
            "Compost": 2,
        })
        state, ok, _ = set_farm_plan_pure(
            state,
            "falador_allotment_north",
            "potato",
            protection_intent=True,
        )
        self.assertTrue(ok)

        queued, ids = queue_full_run_pure(state)
        self.assertEqual(len(ids), 1)
        self.assertEqual(queued["inventory"]["Compost"], 0)
        self.assertFalse(
            queued["farm_plans"]["falador_allotment_north"]["protection_paid"]
        )
        self.assertTrue(queued["farm_queue"][0]["protection_paid"])
        self.assertEqual(
            queued["farm_queue"][0]["protection_payment"],
            {"Compost": 2},
        )
        removed, ok = remove_farm_queue_step_pure(
            queued, queued["farm_queue"][0]["id"]
        )
        self.assertTrue(ok)
        self.assertEqual(removed["inventory"]["Compost"], 2)
        self.assertEqual(removed["farm_queue"], [])
        cleared, ok, _ = apply_farming_frontend_action_pure(
            queued, "queue_clear", {}
        )
        self.assertTrue(ok)
        self.assertEqual(cleared["inventory"]["Compost"], 2)
        self.assertEqual(cleared["farm_queue"], [])
        invalidated = copy.deepcopy(queued)
        invalidated["inventory"]["Potato seed"] = 0
        refunded, consumed, info = consume_next_farm_queue_step_pure(invalidated)
        self.assertTrue(consumed)
        self.assertEqual(info["status"], "skipped")
        self.assertEqual(refunded["inventory"]["Compost"], 2)

        planted, consumed, info = consume_next_farm_queue_step_pure(queued)
        self.assertTrue(consumed)
        self.assertEqual(info["status"], "executed")
        self.assertTrue(planted["farm_patches"]["falador_allotment_north"]["protected"])

        missing = copy.deepcopy(state)
        missing["inventory"]["Compost"] = 1
        skipped, ids = queue_full_run_pure(missing)
        self.assertEqual(ids, ())
        self.assertEqual(skipped["farm_queue"], [])
        self.assertEqual(skipped["inventory"]["Compost"], 1)
        self.assertEqual(
            skipped["farm_last_full_run_skips"],
            [{
                "patch_id": "falador_allotment_north",
                "patch_name": "South Falador allotment north",
                "reason": "missing gardener payment",
            }],
        )
        projection = farming_frontend_projection_pure(missing)["full_run"]
        self.assertTrue(projection["enabled"])
        self.assertEqual(projection["count"], 0)
        self.assertEqual(len(projection["skips"]), 1)
        reported, ok, message = apply_farming_frontend_action_pure(
            missing, "queue_full_run", {}
        )
        self.assertTrue(ok)
        self.assertEqual(reported["farm_queue"], [])
        self.assertEqual(reported["farming_counters"]["full_runs"], 0)
        self.assertIn("Skipped South Falador allotment north", message)

    def test_dig_up_rejects_invalid_patch_states_without_mutation(self):
        base = _state()
        base["inventory"].update({
            "Rake": 1,
            "Seed dibber": 1,
            "Spade": 1,
            "Redberry seed": 1,
            "Potato seed": 3,
        })
        bush, ok, _ = execute_farm_field_step_pure(
            base,
            {"kind": "plant", "patch_id": "champions_bush", "crop_id": "redberry"},
        )
        self.assertTrue(ok)
        mature, _ = advance_farm_clock_pure(bush, 17, lambda: 1.0)
        variants = {}
        variants["missing Spade"] = copy.deepcopy(mature)
        variants["missing Spade"]["inventory"]["Spade"] = 0
        variants["immature crop"] = copy.deepcopy(bush)
        variants["diseased crop"] = copy.deepcopy(mature)
        variants["diseased crop"]["farm_patches"]["champions_bush"]["diseased"] = True
        potato, ok, _ = execute_farm_field_step_pure(
            base,
            {
                "kind": "plant",
                "patch_id": "falador_allotment_north",
                "crop_id": "potato",
            },
        )
        self.assertTrue(ok)
        potato, _ = advance_farm_clock_pure(potato, 41, lambda: 1.0)
        variants["non-regrowth crop"] = potato

        for label, state in variants.items():
            patch_id = (
                "falador_allotment_north"
                if label == "non-regrowth crop"
                else "champions_bush"
            )
            before = copy.deepcopy(state)
            rejected, ok, _ = execute_farm_field_step_pure(
                state, {"kind": "dig_up", "patch_id": patch_id}
            )
            self.assertFalse(ok, label)
            self.assertEqual(rejected, before, label)

    def test_plan_water_and_item_cure_policies_drive_full_run(self):
        state = _state()
        state["inventory"].update({
            "Rake": 1,
            "Seed dibber": 1,
            "Potato seed": 6,
            "Watering can": 1,
            "Plant cure": 1,
        })
        state, ok, _ = set_farm_plan_pure(
            state,
            "falador_allotment_north",
            "potato",
            watering_intent=False,
            cure_intent=False,
        )
        self.assertTrue(ok)
        state, ok, _ = execute_farm_field_step_pure(
            state,
            {"kind": "plant", "patch_id": "falador_allotment_north", "crop_id": "potato"},
        )
        self.assertTrue(ok)
        self.assertFalse(state["farm_patches"]["falador_allotment_north"]["watered"])
        state["farm_patches"]["falador_allotment_north"]["diseased"] = True
        unchanged, ids = queue_full_run_pure(state)
        self.assertEqual(ids, ())
        self.assertEqual(unchanged["inventory"]["Plant cure"], 1)

        state, ok, _ = set_farm_plan_pure(
            state,
            "falador_allotment_north",
            "potato",
            watering_intent=True,
            cure_intent=True,
        )
        self.assertTrue(ok)
        queued, ids = queue_full_run_pure(state)
        self.assertEqual(len(ids), 1)
        self.assertEqual(queued["farm_queue"][0]["kind"], "cure")

    def test_presets_snapshot_only_plan_policy_and_selection_is_inert(self):
        state = _state()
        state["inventory"] = {"Coins": 10}
        state, ok, _ = set_farm_plan_pure(
            state,
            "falador_allotment_north",
            "potato",
            "compost",
            True,
            False,
            True,
        )
        self.assertTrue(ok)
        state["farm_plans"]["falador_allotment_north"]["protection_paid"] = True
        state["farm_plans"]["falador_allotment_north"]["fertile_soil_applied"] = True
        state["farm_patches"]["falador_allotment_north"]["plan"] = copy.deepcopy(
            state["farm_plans"]["falador_allotment_north"]
        )
        saved, ok, _ = save_farm_preset_pure(
            state, "Herb run", ("falador_allotment_north",)
        )
        self.assertTrue(ok)
        preset_id = saved["farm_selected_preset"]
        snapshot = saved["farm_presets"][preset_id]["plans"]["falador_allotment_north"]
        self.assertEqual(
            snapshot,
            {
                "crop_id": "potato",
                "compost_tier": "compost",
                "protection_intent": True,
                "watering_intent": False,
                "cure_intent": True,
                "cure_route_preference": PLANT_CURE_ITEM_FIRST,
            },
        )
        saved["farm_plans"]["falador_allotment_north"]["protection_paid"] = False
        saved["farm_plans"]["falador_allotment_north"]["fertile_soil_applied"] = False
        saved["farm_patches"]["falador_allotment_north"]["plan"] = copy.deepcopy(
            saved["farm_plans"]["falador_allotment_north"]
        )

        changed, ok, _ = set_farm_plan_pure(
            saved, "falador_allotment_north", "onion", watering_intent=True
        )
        self.assertTrue(ok)
        before = copy.deepcopy(changed)
        selected, ok, _ = select_farm_preset_pure(changed, preset_id)
        self.assertTrue(ok)
        self.assertEqual(selected["farm_plans"], before["farm_plans"])
        self.assertEqual(selected["inventory"], before["inventory"])
        self.assertEqual(selected["farm_queue"], before["farm_queue"])
        self.assertTrue(farming_frontend_projection_pure(selected)["presets"]["modified"])

        applied, ok, _ = apply_farm_preset_pure(selected)
        self.assertTrue(ok)
        self.assertEqual(
            applied["farm_plans"]["falador_allotment_north"]["crop_id"],
            "potato",
        )
        self.assertFalse(
            applied["farm_plans"]["falador_allotment_north"]["protection_paid"]
        )
        self.assertFalse(farming_frontend_projection_pure(applied)["presets"]["modified"])

        duplicate, ok, _ = duplicate_farm_preset_pure(applied, preset_id)
        self.assertTrue(ok)
        duplicate_id = duplicate["farm_selected_preset"]
        renamed, ok, _ = rename_farm_preset_pure(duplicate, duplicate_id, "Weekend")
        self.assertTrue(ok)
        deleted, ok, _ = delete_farm_preset_pure(renamed, duplicate_id)
        self.assertTrue(ok)
        self.assertIsNone(deleted["farm_selected_preset"])
        self.assertNotIn(duplicate_id, deleted["farm_presets"])

        long_name = "A" * 60
        long_named, ok, _ = rename_farm_preset_pure(
            deleted, preset_id, long_name
        )
        self.assertTrue(ok)
        long_copy, ok, _ = duplicate_farm_preset_pure(long_named, preset_id)
        self.assertTrue(ok)
        copy_name = long_copy["farm_presets"][
            long_copy["farm_selected_preset"]
        ]["name"]
        self.assertEqual(len(copy_name), 60)
        self.assertNotEqual(copy_name, long_name)

    def test_preset_apply_preserves_patch_local_fertile_soil_and_legacy_payment(self):
        state = _state()
        state, ok, _ = set_farm_plan_pure(
            state, "falador_allotment_north", "potato"
        )
        self.assertTrue(ok)
        saved, ok, _ = save_farm_preset_pure(
            state, "Allotment", ("falador_allotment_north",)
        )
        self.assertTrue(ok)
        preset_id = saved["farm_selected_preset"]
        changed, ok, _ = set_farm_plan_pure(
            saved, "falador_allotment_north", "onion"
        )
        self.assertTrue(ok)
        changed["farm_plans"]["falador_allotment_north"]["fertile_soil_applied"] = True
        changed["farm_patches"]["falador_allotment_north"]["plan"] = copy.deepcopy(
            changed["farm_plans"]["falador_allotment_north"]
        )
        applied, ok, _ = apply_farm_preset_pure(changed, preset_id)
        self.assertTrue(ok)
        self.assertTrue(
            applied["farm_plans"]["falador_allotment_north"]["fertile_soil_applied"]
        )

        paid = copy.deepcopy(changed)
        paid["farm_plans"]["falador_allotment_north"]["protection_paid"] = True
        paid["farm_patches"]["falador_allotment_north"]["plan"] = copy.deepcopy(
            paid["farm_plans"]["falador_allotment_north"]
        )
        before = copy.deepcopy(paid)
        rejected, ok, _ = apply_farm_preset_pure(paid, preset_id)
        self.assertFalse(ok)
        self.assertEqual(rejected, before)

    def test_gardener_intent_is_clamped_for_crops_without_a_payment(self):
        state = _state(level=99)
        planned, ok, _ = set_farm_plan_pure(
            state,
            "champions_bush",
            "poison_ivy",
            protection_intent=True,
        )
        self.assertTrue(ok)
        self.assertFalse(
            planned["farm_plans"]["champions_bush"]["protection_intent"]
        )

    def test_protection_is_exact_idempotent_live_state_and_rejects_diseased_crop(self):
        data = _state()
        data["inventory"].update({"Compost": 4, "Rake": 1, "Seed dibber": 1, "Spade": 1, "Potato seed": 3, "Watermelon seed": 3})
        planned, ok, _ = set_farm_plan_pure(data, "falador_allotment_north", "potato", protection_intent=True)
        self.assertTrue(ok)
        queued, step_id, _ = add_farm_queue_step_pure(planned, "plant", "falador_allotment_north", crop_id="potato")
        self.assertIsNotNone(step_id)
        paid, ok, _ = pay_farming_protection_pure(queued, "falador_allotment_north")
        self.assertTrue(ok)
        paid_twice, ok, _ = pay_farming_protection_pure(paid, "falador_allotment_north")
        self.assertTrue(ok)
        self.assertEqual(paid_twice["inventory"]["Compost"], 2)
        planted, _, info = consume_next_farm_queue_step_pure(paid_twice)
        self.assertEqual(info["status"], "executed")
        self.assertTrue(planted["farm_patches"]["falador_allotment_north"]["protected"])

        mismatch = copy.deepcopy(paid)
        mismatch["farm_queue"] = []
        mismatch["farm_patches"]["falador_allotment_north"] = default_farming_state_pure()["farm_patches"]["falador_allotment_north"]
        wrong, ok, _ = execute_farm_field_step_pure(mismatch, {"kind": "plant", "patch_id": "falador_allotment_north", "crop_id": "watermelon"})
        self.assertTrue(ok)
        self.assertFalse(wrong["farm_patches"]["falador_allotment_north"]["protected"])

        planted["farm_patches"]["falador_allotment_north"]["diseased"] = True
        before = planted["inventory"]["Compost"]
        rejected, ok, _ = pay_farming_protection_pure(planted, "falador_allotment_north")
        self.assertFalse(ok)
        self.assertEqual(rejected["inventory"]["Compost"], before)

    def test_taverley_is_disease_free_and_mushrooms_require_medium_tasks_for_immunity(self):
        taverley = _plant_ready(_state(), "taverley_potato", "potato")
        taverley, _ = advance_farm_clock_pure(taverley, 7, lambda: 0.0)
        self.assertFalse(taverley["farm_patches"]["taverley_potato"]["diseased"])

        mushroom = _state()
        mushroom["unlocked_regions"] = ["morytania"]
        mushroom["inventory"].update({"Rake": 1, "Seed dibber": 1, "Spade": 1, "Mushroom spore": 1})
        mushroom, ok, _ = execute_farm_field_step_pure(mushroom, {"kind": "plant", "patch_id": "canifis_mushroom", "crop_id": "bittercap"})
        self.assertTrue(ok)
        diseased, _ = advance_farm_clock_pure(mushroom, 14, lambda: 0.0)
        self.assertTrue(diseased["farm_patches"]["canifis_mushroom"]["diseased"])
        mushroom["completed_task_sets"] = ["morytania_medium"]
        immune, _ = advance_farm_clock_pure(mushroom, 14, lambda: 0.0)
        self.assertFalse(immune["farm_patches"]["canifis_mushroom"]["diseased"])

    def test_jade_vine_prunes_six_times_turns_wild_and_returns_seed_after_kill_clear(self):
        data = _state()
        data["quests"] = {"back_to_my_roots": {"completed": True}}
        data["inventory"].update({"Rake": 1, "Seed dibber": 1, "Spade": 1, "Jade vine seed": 1})
        planted, ok, _ = execute_farm_field_step_pure(data, {"kind": "plant", "patch_id": "handelmort_jade_vine", "crop_id": "jade_vine"})
        self.assertTrue(ok)
        ready, _ = advance_farm_clock_pure(planted, 160, lambda: 1.0)
        ready, ok, _ = execute_farm_field_step_pure(ready, {"kind": "check_health", "patch_id": "handelmort_jade_vine"})
        self.assertTrue(ok)
        for _ in range(6):
            ready, ok, info = execute_farm_field_step_pure(ready, {"kind": "harvest", "patch_id": "handelmort_jade_vine"}, lambda: 0.0)
            self.assertTrue(ok)
            self.assertEqual(info["outputs"], {"Jade vine branch": 1})
        self.assertEqual(ready["farm_patches"]["handelmort_jade_vine"]["jade_state"], "wild")
        killed, ok, _ = execute_farm_field_step_pure(ready, {"kind": "chop", "patch_id": "handelmort_jade_vine"})
        self.assertTrue(ok)
        cleared, ok, info = execute_farm_field_step_pure(killed, {"kind": "clear", "patch_id": "handelmort_jade_vine"})
        self.assertTrue(ok)
        self.assertEqual(info["outputs"], {"Jade vine seed": 1})
        self.assertIsNone(cleared["farm_patches"]["handelmort_jade_vine"]["crop_id"])

    def test_limpwurt_uses_level_scaled_extra_root_roll_without_extra_xp_rules(self):
        data = _state(99)
        data["inventory"].update({"Rake": 1, "Seed dibber": 1, "Spade": 1, "Limpwurt seed": 1})
        planted, ok, _ = execute_farm_field_step_pure(data, {"kind": "plant", "patch_id": "falador_flower", "crop_id": "limpwurt"})
        self.assertTrue(ok)
        ready, _ = advance_farm_clock_pure(planted, 4, lambda: 1.0)
        harvested, ok, info = execute_farm_field_step_pure(ready, {"kind": "harvest", "patch_id": "falador_flower"}, lambda: 1.0)
        self.assertTrue(ok)
        self.assertEqual(info["outputs"], {"Limpwurt root": 12})
        self.assertEqual(info["farming_xp"], 1440.0)
        self.assertEqual(harvested["inventory"]["Limpwurt root"], 12)

    def test_juju_activation_consumes_a_dose_and_bonus_herbs_award_no_extra_xp(self):
        data = _state()
        data["inventory"].update({"Rake": 1, "Seed dibber": 1, "Spade": 1, "Guam seed": 1, "Juju farming potion (3)": 1})
        planted, ok, _ = execute_farm_field_step_pure(data, {"kind": "plant", "patch_id": "falador_herb", "crop_id": "guam"})
        self.assertTrue(ok)
        ready, _ = advance_farm_clock_pure(planted, 14, lambda: 1.0)
        active, ok, _ = activate_juju_farming_potion_pure(ready)
        self.assertTrue(ok)
        self.assertEqual(active["inventory"]["Juju farming potion (2)"], 1)
        through_frontend, ok, message = apply_farming_frontend_action_pure(
            ready, "activate_juju_farming_potion", {"item_name": "Juju farming potion (3)"}
        )
        self.assertTrue(ok, message)
        self.assertEqual(through_frontend["inventory"]["Juju farming potion (2)"], 1)
        self.assertEqual(through_frontend["farm_juju_active_until"], ready["farm_clock_minutes"] + 5)
        rejected, ok, message = apply_farming_frontend_action_pure(
            ready, "activate_juju_farming_potion", {"item_name": "Beer"}
        )
        self.assertFalse(ok)
        self.assertEqual(message, "not a Juju farming potion")
        self.assertEqual(rejected["inventory"], ready["inventory"])
        active, _ = advance_farm_clock_pure(active, 1, lambda: 1.0)
        active["farm_patches"]["falador_herb"]["lives"] = 1
        rolls = iter((1.0, 0.0))
        harvested, ok, info = execute_farm_field_step_pure(active, {"kind": "harvest", "patch_id": "falador_herb"}, lambda: next(rolls))
        self.assertTrue(ok)
        self.assertEqual(info["outputs"], {"Grimy guam": 2})
        self.assertEqual(info["juju_bonus"], 1)
        self.assertEqual(info["farming_xp"], 12.5)
        self.assertEqual(harvested["inventory"]["Grimy guam"], 2)

    def test_regular_compost_and_jade_regrowth_use_injected_source_ranges(self):
        data = _state()
        data["inventory"]["Potato"] = 30
        low, ok, _ = fill_compost_bin_pure(data, "falador_bin", "Potato", lambda: 0.0)
        self.assertTrue(ok)
        self.assertEqual(low["farm_compost_bins"]["falador_bin"]["ready_at"], 35)
        high, ok, _ = fill_compost_bin_pure(data, "catherby_bin", "Potato", lambda: 1.0)
        self.assertTrue(ok)
        self.assertEqual(high["farm_compost_bins"]["catherby_bin"]["ready_at"], 50)

        vine = _state()
        vine["quests"] = {"back_to_my_roots": {"completed": True}}
        vine["inventory"].update({"Rake": 1, "Seed dibber": 1, "Spade": 1, "Jade vine seed": 1})
        vine, ok, _ = execute_farm_field_step_pure(vine, {"kind": "plant", "patch_id": "handelmort_jade_vine", "crop_id": "jade_vine"})
        self.assertTrue(ok)
        vine, _ = advance_farm_clock_pure(vine, 160, lambda: 1.0)
        vine, ok, _ = execute_farm_field_step_pure(vine, {"kind": "check_health", "patch_id": "handelmort_jade_vine"})
        self.assertTrue(ok)
        vine, ok, _ = execute_farm_field_step_pure(vine, {"kind": "harvest", "patch_id": "handelmort_jade_vine"}, lambda: 0.0)
        self.assertTrue(ok)
        self.assertEqual(vine["farm_patches"]["handelmort_jade_vine"]["next_regrowth_at"], vine["farm_clock_minutes"] + 30)

    def test_harvest_and_clear_require_spade_and_scarecrow_can_be_removed(self):
        ready, _ = advance_farm_clock_pure(_plant_ready(_state()), 7, lambda: 1.0)
        ready["inventory"].pop("Spade", None)
        unchanged, ok, _ = execute_farm_field_step_pure(ready, {"kind": "harvest", "patch_id": "falador_allotment_north"})
        self.assertFalse(ok)
        self.assertEqual(unchanged["inventory"].get("Potato", 0), 0)

        scarecrow = _state()
        scarecrow["inventory"].update({"Rake": 1, "Seed dibber": 1, "Spade": 1, "Scarecrow": 1})
        scarecrow, ok, _ = execute_farm_field_step_pure(scarecrow, {"kind": "plant", "patch_id": "falador_flower", "crop_id": "scarecrow"})
        self.assertTrue(ok)
        scarecrow, ok, info = execute_farm_field_step_pure(scarecrow, {"kind": "clear", "patch_id": "falador_flower"})
        self.assertTrue(ok)
        self.assertEqual(info["outputs"], {"Scarecrow": 1})
        self.assertIsNone(scarecrow["farm_patches"]["falador_flower"]["crop_id"])

    def test_multi_card_advancement_matches_repeated_single_card_ticks_and_rng_order(self):
        data = _state()
        for patch_id in ("falador_allotment_north", "falador_allotment_south"):
            data = _plant_ready(data, patch_id, "potato")
        batched_rolls = iter((0.0, 1.0, 0.0, 1.0, 0.0, 1.0))
        batched, batched_info = advance_farm_clock_pure(data, 7, lambda: next(batched_rolls))
        repeated = copy.deepcopy(data)
        repeated_events = []
        repeated_rolls = iter((0.0, 1.0, 0.0, 1.0, 0.0, 1.0))
        for _ in range(7):
            repeated, info = advance_farm_clock_pure(repeated, 1, lambda: next(repeated_rolls))
            repeated_events.extend(info["events"])
        self.assertEqual(batched, repeated)
        self.assertEqual(batched_info["events"], repeated_events)

    def test_numeric_sanitation_is_finite_and_event_history_is_bounded(self):
        data = _state()
        data["farm_clock_minutes"] = float("inf")
        data["farming_exp"] = float("nan")
        data["farm_event_log"] = [{"event": "old", "n": i} for i in range(500)]
        clean = sanitize_farming_state_pure(data)
        self.assertEqual(clean["farming_exp"], 0.0)
        self.assertEqual(clean["farm_clock_minutes"], 0)
        self.assertEqual(len(clean["farm_event_log"]), 200)
        advanced, _ = advance_farm_clock_pure(data, 1)
        self.assertTrue(advanced["farming_exp"] == 0.0)
        self.assertLessEqual(len(advanced["farm_event_log"]), 200)

    def test_magic_secateurs_keep_farming_tool_metadata_after_quest_merge(self):
        definition = item_definitions_by_storage_key(ITEM_DEFINITIONS)["Magic secateurs"]
        self.assertEqual(definition.category, "tool")
        self.assertFalse(definition.tradeable)


class TestFarmingFrontendProjection(unittest.TestCase):
    def test_projection_groups_all_patches_and_bins_with_stable_ids(self):
        view = farming_frontend_projection_pure(_state())
        patches = [patch for location in view["locations"] for patch in location["patches"]]
        bins = [row for location in view["locations"] for row in location["compost_bins"]]
        self.assertEqual(len(patches), 52)
        self.assertEqual(len({patch["patch_id"] for patch in patches}), 52)
        self.assertEqual(len(bins), 6)
        self.assertEqual(len({row["bin_id"] for row in bins}), 6)
        self.assertEqual(view["hud"]["priority"], "none")
        self.assertNotIn("input-starved", repr(view).lower())
        self.assertNotIn("source-blocked", repr(view).lower())

    def test_white_tree_projection_is_a_single_permanent_harvest_surface(self):
        state = _state(level=25)
        state["quests"] = {
            "garden_of_tranquillity": {"completed": True}
        }
        view = farming_frontend_projection_pure(state)
        patch = next(
            patch
            for location in view["locations"]
            for patch in location["patches"]
            if patch["patch_id"] == "varrock_white_tree"
        )

        self.assertTrue(patch["fixed_crop"])
        self.assertEqual(patch["crop_name"], "White tree")
        self.assertEqual(patch["produce_count"], 4)
        self.assertEqual(patch["produce_capacity"], 4)
        self.assertEqual(patch["crop_options"], ())
        self.assertIsNone(patch["shortcut_action"])
        self.assertEqual(patch["primary_action"]["id"], "harvest")
        self.assertEqual(
            patch["fixed_crop_note"],
            "Permanent post-quest tree · Queue full run harvests all ready fruit · One fruit regrows per answered card.",
        )

        state.update(sanitize_farming_state_pure(state))
        state["farm_patches"]["varrock_white_tree"]["produce_count"] = 0
        regrowing = farming_frontend_projection_pure(state)
        regrowing_patch = next(
            patch
            for location in regrowing["locations"]
            for patch in location["patches"]
            if patch["patch_id"] == "varrock_white_tree"
        )
        self.assertEqual(
            regrowing_patch["status_label"],
            "Regrowing · next produce in about 1 review",
        )

    def test_hud_precedence_is_alert_then_ready_then_queue_then_none(self):
        queued, step_id, _ = add_farm_queue_step_pure(_state(), "plant", "falador_allotment_north", crop_id="potato")
        self.assertIsNotNone(step_id)
        self.assertEqual(farming_frontend_projection_pure(queued)["hud"]["priority"], "queue")

        ready, _ = advance_farm_clock_pure(_plant_ready(queued), 7, lambda: 1.0)
        ready_view = farming_frontend_projection_pure(ready)
        self.assertEqual(ready_view["hud"]["priority"], "ready")
        self.assertEqual(ready_view["hud"]["queue_count"], 1)

        ready["farm_patches"]["falador_allotment_north"].update({"diseased": True, "dead": False})
        alert_view = farming_frontend_projection_pure(ready)
        self.assertEqual(alert_view["hud"]["priority"], "alert")
        self.assertEqual(alert_view["hud"]["ready_count"], 1)
        self.assertEqual(alert_view["hud"]["queue_count"], 1)

    def test_fertile_soil_projection_does_not_require_a_supercompost_bucket(self):
        data = _state(1)
        data["inventory"].update({"Rake": 1, "Seed dibber": 1, "Spade": 1, "Potato seed": 3})
        planned, ok, _ = set_farm_plan_pure(
            data, "falador_allotment_north", "potato", compost_tier="supercompost"
        )
        self.assertTrue(ok)
        planned["farm_plans"]["falador_allotment_north"]["fertile_soil_applied"] = True
        planned["farm_patches"]["falador_allotment_north"]["plan"]["fertile_soil_applied"] = True
        view = farming_frontend_projection_pure(planned)
        patch_view = next(
            patch
            for location in view["locations"]
            for patch in location["patches"]
            if patch["patch_id"] == "falador_allotment_north"
        )
        self.assertTrue(patch_view["primary_action"]["enabled"])
        self.assertNotIn("Supercompost", patch_view["primary_action"]["locked_reason"])

        ready = _plant_ready(_state(1))
        ready, _ = advance_farm_clock_pure(ready, 7, lambda: 1.0)
        ready["inventory"]["Potato seed"] = 3
        ready, ok, _ = set_farm_plan_pure(
            ready, "falador_allotment_north", "potato", compost_tier="supercompost"
        )
        self.assertTrue(ok)
        ready["farm_plans"]["falador_allotment_north"]["fertile_soil_applied"] = True
        ready["farm_patches"]["falador_allotment_north"]["plan"]["fertile_soil_applied"] = True
        view = farming_frontend_projection_pure(ready)
        patch_view = next(
            patch
            for location in view["locations"]
            for patch in location["patches"]
            if patch["patch_id"] == "falador_allotment_north"
        )
        self.assertTrue(patch_view["shortcut_action"]["enabled"])
        self.assertNotIn("Supercompost", patch_view["shortcut_action"]["locked_reason"])

    def test_projection_hides_payment_for_paid_or_flower_protected_crops(self):
        planned = _state()
        planned["inventory"]["Compost"] = 2
        planned, ok, _ = set_farm_plan_pure(
            planned, "falador_allotment_north", "potato", protection_intent=True
        )
        self.assertTrue(ok)
        paid, ok, _ = pay_farming_protection_pure(planned, "falador_allotment_north")
        self.assertTrue(ok)
        view = farming_frontend_projection_pure(paid)
        patch_view = next(
            patch
            for location in view["locations"]
            for patch in location["patches"]
            if patch["patch_id"] == "falador_allotment_north"
        )
        self.assertEqual(patch_view["protection"]["state"], "Protected")
        self.assertIsNone(patch_view["protection"]["action"])

        flowers = _state()
        flowers["inventory"].update({
            "Rake": 1,
            "Seed dibber": 1,
            "Potato seed": 3,
            "Marigold seed": 1,
            "Compost": 2,
        })
        flowers, ok, _ = execute_farm_field_step_pure(
            flowers, {"kind": "plant", "patch_id": "falador_allotment_north", "crop_id": "potato"}
        )
        self.assertTrue(ok)
        flowers, ok, _ = execute_farm_field_step_pure(
            flowers, {"kind": "plant", "patch_id": "falador_flower", "crop_id": "marigold"}
        )
        self.assertTrue(ok)
        flowers, _ = advance_farm_clock_pure(flowers, 4, lambda: 1.0)
        view = farming_frontend_projection_pure(flowers)
        patch_view = next(
            patch
            for location in view["locations"]
            for patch in location["patches"]
            if patch["patch_id"] == "falador_allotment_north"
        )
        self.assertEqual(patch_view["protection"]["state"], "Protected by nearby flowers")
        self.assertIsNone(patch_view["protection"]["action"])

    def test_unified_callback_updates_plan_queue_and_instant_inventory(self):
        data = _state()
        data["inventory"].update({"Rake": 1, "Seed dibber": 1, "Spade": 1, "Potato seed": 3, "Compost": 2})
        planned, ok, message = apply_farming_frontend_action_pure(data, "set_plan", {
            "patch_id": "falador_allotment_north", "crop_id": "potato",
            "compost_tier": "none", "protection_intent": True,
        })
        self.assertTrue(ok)
        self.assertEqual(message, "plan saved")
        queued, ok, message = apply_farming_frontend_action_pure(planned, "queue_action", {
            "patch_id": "falador_allotment_north", "kind": "plant",
            "details": {"crop_id": "potato", "compost_tier": "none"},
        })
        self.assertTrue(ok)
        self.assertEqual(len(queued["farm_queue"]), 1)
        paid, ok, message = apply_farming_frontend_action_pure(queued, "pay_protection", {"patch_id": "falador_allotment_north"})
        self.assertTrue(ok)
        self.assertEqual(message, "protection paid")
        self.assertEqual(paid["inventory"]["Compost"], 0)
        self.assertTrue(paid["farm_plans"]["falador_allotment_north"]["protection_paid"])

    def test_queue_mutations_use_stable_step_ids(self):
        data = _state()
        first, first_id, _ = add_farm_queue_step_pure(data, "plant", "falador_allotment_north", crop_id="potato")
        second, second_id, _ = add_farm_queue_step_pure(first, "plant", "falador_allotment_south", crop_id="potato")
        moved, ok, _ = apply_farming_frontend_action_pure(second, "queue_move", {"step_id": second_id, "new_index": 0})
        self.assertTrue(ok)
        self.assertEqual([row["id"] for row in moved["farm_queue"]], [second_id, first_id])
        removed, ok, _ = apply_farming_frontend_action_pure(moved, "queue_remove", {"step_id": first_id})
        self.assertTrue(ok)
        self.assertEqual([row["id"] for row in removed["farm_queue"]], [second_id])

    def test_location_groups_preserve_canonical_patch_and_bin_order(self):
        view = farming_frontend_projection_pure(_state())
        locations = view["locations"]
        self.assertEqual(
            [location["location_id"] for location in locations],
            list(dict.fromkeys(
                [patch.complex_id for patch in FARMING_PATCHES]
                + [compost_bin.complex_id for compost_bin in FARMING_COMPOST_BINS]
            )),
        )
        projected_patches = [
            patch["patch_id"]
            for location in locations
            for patch in location["patches"]
        ]
        projected_bins = [
            compost_bin["bin_id"]
            for location in locations
            for compost_bin in location["compost_bins"]
        ]
        self.assertEqual(
            projected_patches,
            [
                patch.id
                for location_id in [location["location_id"] for location in locations]
                for patch in FARMING_PATCHES
                if patch.complex_id == location_id
            ],
        )
        self.assertEqual(
            projected_bins,
            [
                compost_bin.id
                for location_id in [location["location_id"] for location in locations]
                for compost_bin in FARMING_COMPOST_BINS
                if compost_bin.complex_id == location_id
            ],
        )
        self.assertTrue(all(not location["open_by_default"] for location in locations))

        ready, _ = advance_farm_clock_pure(_plant_ready(_state()), 7, lambda: 1.0)
        ready_view = farming_frontend_projection_pure(ready)
        falador = next(location for location in ready_view["locations"] if location["location_id"] == "falador")
        self.assertTrue(falador["open_by_default"])
        self.assertEqual(falador["summary"], "1 active · 1 ready · 0 attention")

    def test_disabled_frontend_actions_do_not_mutate_any_farming_state(self):
        data = _state(level=1)
        data["inventory"] = {"Rake": 1, "Seed dibber": 1, "Potato seed": 2}
        before = copy.deepcopy(data)

        locked_plan, ok, message = apply_farming_frontend_action_pure(data, "set_plan", {
            "patch_id": "falador_allotment_north",
            "crop_id": "watermelon",
        })
        self.assertFalse(ok)
        self.assertIn("level 47", message)
        self.assertEqual(locked_plan, before)

        missing_seed, ok, message = apply_farming_frontend_action_pure(data, "set_plan", {
            "patch_id": "falador_allotment_north",
            "crop_id": "potato",
        })
        self.assertTrue(ok)
        queued, ok, message = apply_farming_frontend_action_pure(missing_seed, "queue_action", {
            "patch_id": "falador_allotment_north",
            "kind": "plant",
            "details": {"crop_id": "potato", "compost_tier": "none"},
        })
        self.assertFalse(ok)
        self.assertIn("Potato seed", message)
        self.assertEqual(queued, missing_seed)

        absent, ok, _ = apply_farming_frontend_action_pure(data, "queue_remove", {"step_id": "missing"})
        self.assertFalse(ok)
        self.assertEqual(absent, before)
        cleared, ok, _ = apply_farming_frontend_action_pure(data, "queue_clear", {})
        self.assertFalse(ok)
        self.assertEqual(cleared, before)

    def test_frontend_full_run_preview_matches_queued_stable_steps(self):
        data = _state()
        data["inventory"].update({"Rake": 1, "Seed dibber": 1, "Potato seed": 3})
        planned, ok, _ = set_farm_plan_pure(data, "falador_allotment_north", "potato")
        self.assertTrue(ok)
        preview = farming_frontend_projection_pure(planned)["full_run"]
        self.assertEqual(preview, {
            "enabled": True,
            "count": 1,
            "skips": (),
            "preview": "1 steps ready to queue",
            "locked_reason": "",
        })
        queued, ok, message = apply_farming_frontend_action_pure(planned, "queue_full_run", {})
        self.assertTrue(ok)
        self.assertEqual(message, "Queued 1 Farming steps.")
        self.assertEqual([row["id"] for row in queued["farm_queue"]], ["farm_step_00000001"])
        self.assertEqual(queued["farming_counters"]["full_runs"], 1)
        self.assertFalse(farming_frontend_projection_pure(queued)["full_run"]["enabled"])


class TestFarmingEndToEnd(unittest.TestCase):
    def test_level_one_potato_plan_grows_harvests_and_replants_through_reviews(self):
        state = _state(level=1)
        state["inventory"].update({
            "Rake": 1,
            "Seed dibber": 1,
            "Spade": 1,
            "Potato seed": 6,
        })
        state, ok, _ = set_farm_plan_pure(state, "falador_allotment_north", "potato")
        self.assertTrue(ok)
        state, ids = queue_full_run_pure(state)
        self.assertEqual(len(ids), 1)

        state, consumed, info = apply_farming_review_with_queue_pure(state, lambda: 1.0)
        self.assertTrue(consumed)
        self.assertEqual(info["status"], "executed")
        self.assertEqual(state["farm_patches"]["falador_allotment_north"]["crop_id"], "potato")
        self.assertEqual(state["inventory"]["Potato seed"], 3)

        for _ in range(7):
            state, consumed, info = apply_farming_review_with_queue_pure(state, lambda: 1.0)
            self.assertFalse(consumed)
            self.assertEqual(info["status"], "empty")
        self.assertEqual(farming_frontend_projection_pure(state)["ready_count"], 1)

        state, ids = queue_full_run_pure(state)
        self.assertEqual([step["kind"] for step in state["farm_queue"]], ["harvest", "plant"])
        self.assertEqual(len(ids), 2)
        state, consumed, harvest = apply_farming_review_with_queue_pure(state, lambda: 1.0)
        self.assertTrue(consumed)
        self.assertEqual(harvest["status"], "executed")
        self.assertGreaterEqual(state["inventory"]["Potato"], 3)
        harvested_total = state["farming_counters"]["produce_harvested"]
        self.assertGreaterEqual(harvested_total, 3)

        state, consumed, replanted = apply_farming_review_with_queue_pure(state, lambda: 1.0)
        self.assertTrue(consumed)
        self.assertEqual(replanted["status"], "executed")
        self.assertEqual(state["farm_queue"], [])
        self.assertEqual(state["farm_patches"]["falador_allotment_north"]["crop_id"], "potato")
        self.assertEqual(state["inventory"]["Potato seed"], 0)
        self.assertEqual(state["farming_counters"]["plants"], 2)
        self.assertEqual(state["farming_counters"]["produce_harvested"], harvested_total)


if __name__ == "__main__":
    unittest.main()
