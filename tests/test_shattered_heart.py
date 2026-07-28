from __future__ import annotations

import copy
import json
import os
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import (
    EXTRA_ITEM_DATA,
    EXTRA_ITEM_IMAGES,
    ITEM_DEFINITIONS,
    ORE_DATA,
    UTILITY_ACTIVITY_DATA,
)
from ankiscape.core.storage_pure import (
    CURRENT_CONFIG_VERSION,
    default_player_data,
    migrate_loaded_data,
)
from ankiscape.data.shattered_heart_data import (
    SHATTERED_HEART_ASSET_MANIFEST,
    SHATTERED_HEART_BAG_ITEM,
    SHATTERED_HEART_BAG_ITEM_ID,
    SHATTERED_HEART_ELIGIBLE_SKILLS,
    SHATTERED_HEART_KUDOS_REWARD,
    SHATTERED_HEART_PLINTH_ITEM,
    SHATTERED_HEART_PLINTH_ITEM_ID,
    SHATTERED_HEART_REPLICA_ITEMS,
    SHATTERED_HEART_REVIEWS_PER_DAY,
    SHATTERED_HEART_ROCK_CHANCE,
    SHATTERED_HEART_ROCK_ITEMS,
    SHATTERED_HEART_SECOND_ROCK_MODIFIER,
    SHATTERED_HEART_SKILLS,
    SHATTERED_HEART_SKILLS_BY_ID,
    shattered_heart_activity_as_dict,
    shattered_heart_extra_items_as_dict,
)
from ankiscape.data.big_chinchompa_data import (
    BIG_CHINCHOMPA_EVENT_FIRST_SLOT_REVIEW,
    BIG_CHINCHOMPA_UTILITY_ID,
)
from ankiscape.logic.big_chinchompa_logic import advance_big_chinchompa_world_clock_pure
from ankiscape.logic.farming_logic import add_farm_queue_step_pure
from ankiscape.logic.shattered_heart_logic import (
    apply_shattered_heart_command_pure,
    apply_shattered_heart_skilling_hook_pure,
    default_shattered_heart_state_pure,
    sanitize_shattered_heart_state_pure,
    shattered_heart_pair_xp_pure,
    shattered_heart_view_pure,
)
from ankiscape.runtime.runtime_actions import (
    RuntimeActionContext,
    handle_farming_queue_answer,
    handle_fishing_answer,
    handle_mining_answer,
    handle_utility_answer,
    handle_woodcutting_answer,
)

try:
    from aqt.qt import QApplication, QColor, QLabel, QPalette, QProgressBar, QPushButton, QWidget
    from ankiscape.ui.shattered_heart_panel import ShatteredHeartPanel

    QT_AVAILABLE = True
except Exception:
    QT_AVAILABLE = False


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _player() -> dict:
    data = {
        "inventory": {},
        "shop_market_clock": {"answered_cards": 0},
        "house_owned": False,
        "house_rooms_bought": {},
        "shattered_heart": default_shattered_heart_state_pure(),
    }
    for skill_id in SHATTERED_HEART_ELIGIBLE_SKILLS:
        data[f"{skill_id}_level"] = 1
        data[f"{skill_id}_exp"] = 0.0
    return data


def _default_player() -> dict:
    return default_player_data(ORE_DATA, ITEM_DEFINITIONS)


def _runtime_context(player_data: dict, calls: dict) -> RuntimeActionContext:
    def award_skill_exp(exp_key, amount):
        player_data[exp_key] = float(player_data.get(exp_key, 0.0)) + float(amount)
        return float(amount)

    return RuntimeActionContext(
        player_data=player_data,
        random_random=lambda: 0.0,
        show_error_message=lambda title, message: calls["errors"].append((title, message)),
        deactivate_current_skill=lambda: calls.__setitem__("deactivated", True),
        award_skill_exp=award_skill_exp,
        award_hidden_skill_exp=lambda *_args: None,
        level_up_check=lambda skill, _data: calls["levels"].append(skill),
        check_achievements=lambda _data: calls.__setitem__("achievements", True),
        save_player_data=lambda: calls.__setitem__("saves", calls["saves"] + 1),
        refresh_skill_availability=lambda: calls.__setitem__("refresh", True),
        refresh_skill_availability_partial=lambda *_args: None,
        can_smith_any=lambda: False,
        show_exp=lambda amount: calls["xp"].append(amount),
        show_activity_gain=lambda message: calls["activity"].append(message),
        implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda _before: None,
    )


def _give_pair(data: dict, skill_id: str) -> None:
    for item_name in SHATTERED_HEART_SKILLS_BY_ID[skill_id].rock_items:
        data["inventory"][item_name] = 1


def _give_all_pairs(data: dict) -> None:
    for skill_id in SHATTERED_HEART_ELIGIBLE_SKILLS:
        _give_pair(data, skill_id)


def _add_pairs(data: dict) -> tuple[dict, dict]:
    updated, ok, info = apply_shattered_heart_command_pure(
        data, "add_completed_pairs"
    )
    if not ok:
        raise AssertionError(info)
    return updated, info


class ShatteredHeartDataTests(unittest.TestCase):
    def test_period_identity_tables_cover_exactly_the_fifteen_skill_pairs(self):
        self.assertEqual(
            SHATTERED_HEART_ELIGIBLE_SKILLS,
            (
                "agility",
                "herblore",
                "thieving",
                "crafting",
                "runecrafting",
                "mining",
                "smithing",
                "fishing",
                "cooking",
                "firemaking",
                "woodcutting",
                "fletching",
                "farming",
                "construction",
                "hunter",
            ),
        )
        self.assertEqual(
            tuple(item_id for row in SHATTERED_HEART_SKILLS for item_id in row.rock_item_ids),
            tuple(range(15_522, 15_552)),
        )
        self.assertEqual(
            tuple(item_id for row in SHATTERED_HEART_SKILLS for item_id in row.replica_item_ids),
            tuple(range(15_552, 15_582)),
        )
        self.assertEqual(len(SHATTERED_HEART_ROCK_ITEMS), 30)
        self.assertEqual(len(SHATTERED_HEART_REPLICA_ITEMS), 30)

    def test_family_owned_registrars_include_activity_bag_plinth_and_every_piece(self):
        activity = shattered_heart_activity_as_dict()["shattered_heart"]
        self.assertEqual(activity["group"], "distractions_and_diversions")
        self.assertEqual(activity["outputs"], SHATTERED_HEART_ROCK_ITEMS)
        self.assertIn("oldid=6514590", activity["source"])

        items = shattered_heart_extra_items_as_dict()
        self.assertEqual(items[SHATTERED_HEART_BAG_ITEM]["source_item_id"], SHATTERED_HEART_BAG_ITEM_ID)
        self.assertEqual(items[SHATTERED_HEART_BAG_ITEM]["weight_kg"], 10.0)
        self.assertEqual(items[SHATTERED_HEART_PLINTH_ITEM]["source_item_id"], SHATTERED_HEART_PLINTH_ITEM_ID)
        self.assertEqual(
            {items[name]["source_item_id"] for name in SHATTERED_HEART_ROCK_ITEMS},
            set(range(15_522, 15_552)),
        )
        self.assertEqual(
            {items[name]["source_item_id"] for name in SHATTERED_HEART_REPLICA_ITEMS},
            set(range(15_552, 15_582)),
        )
        self.assertFalse(any("golden" in name.casefold() for name in items))

    def test_asset_manifest_owns_the_activity_and_period_item_art_requests(self):
        paths = {str(row["output_path"]) for row in SHATTERED_HEART_ASSET_MANIFEST}
        self.assertIn("activityicons/shattered_heart.png", paths)
        self.assertIn("activityitems/statue_collection_bag.png", paths)
        self.assertIn("activityitems/statue_plinth.png", paths)
        self.assertEqual(len(paths), len(SHATTERED_HEART_ASSET_MANIFEST))

    def test_registry_assets_and_provenance_are_live(self):
        activity = UTILITY_ACTIVITY_DATA["shattered_heart"]
        self.assertEqual(activity["surface"], "activities")
        self.assertTrue(os.path.isfile(activity["icon_path"]))
        for item_name in shattered_heart_extra_items_as_dict():
            with self.subTest(item=item_name):
                self.assertIn(item_name, EXTRA_ITEM_DATA)
                self.assertTrue(os.path.isfile(EXTRA_ITEM_IMAGES[item_name]))
        with open(os.path.join(ROOT, "assets_provenance.json"), encoding="utf-8") as handle:
            provenance = json.load(handle)
        for row in SHATTERED_HEART_ASSET_MANIFEST:
            path = str(row["output_path"])
            with self.subTest(path=path):
                self.assertIn(path, provenance)
                self.assertLess(provenance[path]["timestamp"], "2012-11-20T00:00:00Z")


class ShatteredHeartStateAndViewTests(unittest.TestCase):
    def test_defaults_and_sanitizer_rebuild_only_owned_state(self):
        defaults = default_shattered_heart_state_pure()
        self.assertEqual(defaults["completion_day"], -7)
        self.assertFalse(defaults["auto_discard"])
        self.assertEqual(defaults["placed_pairs"], [])

        raw = {
            "auto_discard": 1,
            "bag_rocks": [SHATTERED_HEART_ROCK_ITEMS[0], "Golden rock", "bad"],
            "placed_pairs": [*SHATTERED_HEART_ELIGIBLE_SKILLS, "combat"],
            "last_rock_skill": "combat",
            "statues_completed": 2,
            "completion_day": -99,
            "replica_pieces_awarded": 4,
            "replica_pairs_added": ["agility", "herblore", "thieving"],
            "replica_plinth_built": 1,
            "unknown": "drop me",
        }
        state = sanitize_shattered_heart_state_pure(raw)
        self.assertTrue(state["auto_discard"])
        self.assertEqual(state["bag_rocks"], [SHATTERED_HEART_ROCK_ITEMS[0]])
        self.assertEqual(len(state["placed_pairs"]), 14)
        self.assertEqual(state["last_rock_skill"], "")
        self.assertEqual(state["completion_day"], -7)
        self.assertEqual(state["replica_pairs_added"], ["agility", "herblore"])
        self.assertNotIn("unknown", state)

    def test_the_view_owns_every_panel_flag_and_label(self):
        view = shattered_heart_view_pure(_player())
        required = {
            "status_label",
            "summary_text",
            "progress_max",
            "progress_value",
            "progress_format",
            "weekly_gate_text",
            "weekly_gate_visible",
            "claim_bag_visible",
            "claim_bag_enabled",
            "destroy_bag_visible",
            "destroy_bag_enabled",
            "add_pairs_label",
            "add_pairs_enabled",
            "auto_discard",
            "auto_discard_enabled",
            "replica_progress_max",
            "replica_progress_value",
            "replica_progress_format",
            "build_plinth_visible",
            "build_plinth_enabled",
            "add_replica_visible",
            "add_replica_enabled",
            "source",
        }
        self.assertTrue(required.issubset(view))
        self.assertTrue(view["claim_bag_visible"])
        self.assertFalse(view["destroy_bag_visible"])
        self.assertFalse(view["add_pairs_enabled"])
        self.assertFalse(view["weekly_gate_visible"])
        self.assertFalse(view["build_plinth_visible"])

    def test_state_and_inventory_inputs_are_not_mutated(self):
        data = _player()
        data["inventory"]["Raw trout"] = 1
        frozen = copy.deepcopy(data)
        updated, ok, _info = apply_shattered_heart_skilling_hook_pure(
            data, "fishing", lambda: 0.0, {"Raw trout": 1}
        )
        self.assertTrue(ok)
        self.assertEqual(data, frozen)
        self.assertIsNot(updated["inventory"], data["inventory"])
        self.assertIsNot(updated["shattered_heart"], data["shattered_heart"])


class ShatteredHeartSkillingHookTests(unittest.TestCase):
    def test_noneligible_skills_do_not_roll_or_award_rocks(self):
        def forbidden_rng():
            raise AssertionError("noneligible skills must not roll")

        data, ok, info = apply_shattered_heart_skilling_hook_pure(
            _player(), "attack", forbidden_rng
        )
        self.assertFalse(ok)
        self.assertIn("not eligible", info["reason"])
        self.assertFalse(any(data["inventory"].get(name, 0) for name in SHATTERED_HEART_ROCK_ITEMS))

    def test_one_action_can_award_both_rocks_and_replace_two_outputs(self):
        data = _player()
        data["inventory"]["Logs"] = 2
        updated, ok, info = apply_shattered_heart_skilling_hook_pure(
            data, "woodcutting", lambda: 0.0, {"Logs": 2}
        )
        self.assertTrue(ok, info)
        self.assertEqual(info["rocks"], SHATTERED_HEART_SKILLS_BY_ID["woodcutting"].rock_items)
        self.assertEqual(info["chances"], (SHATTERED_HEART_ROCK_CHANCE, SHATTERED_HEART_ROCK_CHANCE * SHATTERED_HEART_SECOND_ROCK_MODIFIER))
        self.assertEqual(info["replaced_outputs"], {"Logs": 2})
        self.assertEqual(updated["inventory"]["Logs"], 0)

    def test_the_second_rock_is_halved_until_another_skill_yields_a_rock(self):
        data = _player()
        first, second = SHATTERED_HEART_SKILLS_BY_ID["agility"].rock_items
        data["inventory"][first] = 1
        data["shattered_heart"]["last_rock_skill"] = "agility"
        between = SHATTERED_HEART_ROCK_CHANCE * 0.75

        blocked, ok, info = apply_shattered_heart_skilling_hook_pure(
            data, "agility", lambda: between
        )
        self.assertFalse(ok)
        self.assertEqual(info["chances"], (SHATTERED_HEART_ROCK_CHANCE * 0.5,))
        self.assertEqual(blocked["inventory"].get(second, 0), 0)

        data["shattered_heart"]["last_rock_skill"] = "mining"
        restored, ok, info = apply_shattered_heart_skilling_hook_pure(
            data, "agility", lambda: between
        )
        self.assertTrue(ok, info)
        self.assertEqual(info["chances"], (SHATTERED_HEART_ROCK_CHANCE,))
        self.assertEqual(restored["inventory"][second], 1)

    def test_a_carried_bag_catches_rocks_without_replacing_output(self):
        data, ok, info = apply_shattered_heart_command_pure(_player(), "claim_bag")
        self.assertTrue(ok, info)
        data["inventory"]["Raw trout"] = 2
        updated, ok, info = apply_shattered_heart_skilling_hook_pure(
            data, "fishing", lambda: 0.0, {"Raw trout": 2}
        )
        self.assertTrue(ok, info)
        self.assertEqual(info["route"], "bag")
        self.assertEqual(info["replaced_outputs"], {})
        self.assertEqual(updated["inventory"]["Raw trout"], 2)
        self.assertEqual(len(updated["shattered_heart"]["bag_rocks"]), 2)
        self.assertFalse(any(updated["inventory"].get(name, 0) for name in SHATTERED_HEART_SKILLS_BY_ID["fishing"].rock_items))

        destroyed, ok, result = apply_shattered_heart_command_pure(updated, "destroy_bag")
        self.assertTrue(ok, result)
        self.assertEqual(result["discarded_rocks"], 2)
        self.assertEqual(destroyed["shattered_heart"]["bag_rocks"], [])
        self.assertEqual(destroyed["inventory"][SHATTERED_HEART_BAG_ITEM], 0)

    def test_auto_discard_short_circuits_before_rng_or_inventory_mutation(self):
        data = _player()
        data["inventory"]["Logs"] = 1
        data, ok, info = apply_shattered_heart_command_pure(
            data, "set_auto_discard", {"enabled": True}
        )
        self.assertTrue(ok, info)
        frozen = copy.deepcopy(data)

        def forbidden_rng():
            raise AssertionError("auto-discard must suppress before rolling")

        updated, ok, info = apply_shattered_heart_skilling_hook_pure(
            data, "woodcutting", forbidden_rng, {"Logs": 1}
        )
        self.assertFalse(ok)
        self.assertIn("disabled", info["reason"])
        self.assertEqual(updated, frozen)


class ShatteredHeartMuseumTests(unittest.TestCase):
    def test_pair_xp_uses_the_source_formula_and_the_command_returns_the_award_seam(self):
        data = _player()
        data["agility_level"] = 50
        data["agility_exp"] = 12_345.0
        _give_pair(data, "agility")
        updated, info = _add_pairs(data)
        self.assertEqual(shattered_heart_pair_xp_pure(50), 2_500.0)
        self.assertEqual(info["skill_xp"], {"agility": 2_500.0})
        self.assertEqual(updated["agility_exp"], 12_345.0)
        self.assertEqual(updated["shattered_heart"]["placed_pairs"], ["agility"])

    def test_first_completion_awards_kudos_plinth_and_the_first_replica_piece(self):
        data = _player()
        for index, skill_id in enumerate(SHATTERED_HEART_ELIGIBLE_SKILLS, start=1):
            data[f"{skill_id}_level"] = index
        _give_all_pairs(data)
        updated, info = _add_pairs(data)
        self.assertEqual(len(info["pair_ids"]), 15)
        self.assertEqual(set(info["skill_xp"]), set(SHATTERED_HEART_ELIGIBLE_SKILLS))
        self.assertEqual(info["kudos"], SHATTERED_HEART_KUDOS_REWARD)
        self.assertTrue(info["plinth_awarded"])
        self.assertEqual(info["replica_items"], (SHATTERED_HEART_REPLICA_ITEMS[0],))
        self.assertEqual(updated["inventory"][SHATTERED_HEART_PLINTH_ITEM], 1)
        self.assertEqual(updated["inventory"][SHATTERED_HEART_REPLICA_ITEMS[0]], 1)
        self.assertEqual(updated["shattered_heart"]["statues_completed"], 1)
        self.assertEqual(updated["shattered_heart"]["completion_day"], 0)
        self.assertEqual(updated["shattered_heart"]["placed_pairs"], [])

    def test_only_the_final_pair_waits_until_completion_day_plus_seven(self):
        data = _player()
        _give_all_pairs(data)
        data, _info = _add_pairs(data)

        _give_all_pairs(data)
        data, info = _add_pairs(data)
        self.assertEqual(len(info["pair_ids"]), 14)
        self.assertEqual(len(data["shattered_heart"]["placed_pairs"]), 14)
        self.assertTrue(shattered_heart_view_pure(data)["weekly_gate_visible"])

        data["shop_market_clock"]["answered_cards"] = 6 * SHATTERED_HEART_REVIEWS_PER_DAY
        blocked, ok, info = apply_shattered_heart_command_pure(data, "add_completed_pairs")
        self.assertFalse(ok)
        self.assertIn("seven-day", info["reason"])
        self.assertEqual(blocked["shattered_heart"]["statues_completed"], 1)

        data["shop_market_clock"]["answered_cards"] = 7 * SHATTERED_HEART_REVIEWS_PER_DAY
        completed, info = _add_pairs(data)
        self.assertEqual(len(info["pair_ids"]), 1)
        self.assertEqual(info["kudos"], 0)
        self.assertFalse(info["plinth_awarded"])
        self.assertEqual(info["replica_items"], (SHATTERED_HEART_REPLICA_ITEMS[1],))
        self.assertEqual(completed["shattered_heart"]["statues_completed"], 2)
        self.assertEqual(completed["shattered_heart"]["completion_day"], 7)

    def test_buffered_next_statue_pair_does_not_misreport_an_open_final_gate(self):
        data = _player()
        data["shattered_heart"]["statues_completed"] = 1
        data["shattered_heart"]["completion_day"] = 0
        data["shattered_heart"]["placed_pairs"] = list(
            SHATTERED_HEART_ELIGIBLE_SKILLS[:14]
        )
        _give_pair(data, "agility")
        data["shop_market_clock"]["answered_cards"] = (
            7 * SHATTERED_HEART_REVIEWS_PER_DAY
        )
        _unchanged, ok, info = apply_shattered_heart_command_pure(
            data, "add_completed_pairs"
        )
        self.assertFalse(ok)
        self.assertEqual(info["reason"], "No completed strange-rock pair is ready.")

    def test_buffered_pairs_roll_into_the_next_statue_in_the_same_atomic_command(self):
        data = _player()
        _give_all_pairs(data)
        data, _info = _add_pairs(data)

        for skill_id in SHATTERED_HEART_ELIGIBLE_SKILLS[:14]:
            _give_pair(data, skill_id)
        data, info = _add_pairs(data)
        self.assertEqual(len(info["pair_ids"]), 14)
        for skill_id in SHATTERED_HEART_ELIGIBLE_SKILLS[:14]:
            _give_pair(data, skill_id)
        _give_pair(data, SHATTERED_HEART_ELIGIBLE_SKILLS[-1])
        data["shop_market_clock"]["answered_cards"] = 7 * SHATTERED_HEART_REVIEWS_PER_DAY

        updated, info = _add_pairs(data)
        self.assertEqual(len(info["pair_ids"]), 15)
        self.assertEqual(updated["shattered_heart"]["statues_completed"], 2)
        self.assertEqual(
            updated["shattered_heart"]["placed_pairs"],
            list(SHATTERED_HEART_ELIGIBLE_SKILLS[:14]),
        )

    def test_all_thirty_replica_rewards_arrive_and_complete_the_poh_statue(self):
        data = _player()
        data["house_owned"] = True
        data["house_rooms_bought"] = {"study": True}
        awarded = []
        for completion in range(30):
            data["shop_market_clock"]["answered_cards"] = (
                completion * 7 * SHATTERED_HEART_REVIEWS_PER_DAY
            )
            _give_all_pairs(data)
            data, info = _add_pairs(data)
            awarded.extend(info["replica_items"])
        self.assertEqual(tuple(awarded), SHATTERED_HEART_REPLICA_ITEMS)
        self.assertEqual(data["shattered_heart"]["replica_pieces_awarded"], 30)

        data, ok, info = apply_shattered_heart_command_pure(
            data, "build_replica_plinth"
        )
        self.assertTrue(ok, info)
        data, ok, info = apply_shattered_heart_command_pure(
            data, "add_replica_pairs"
        )
        self.assertTrue(ok, info)
        self.assertEqual(info["pieces_added"], 30)
        self.assertTrue(info["replica_complete"])
        self.assertEqual(
            data["shattered_heart"]["replica_pairs_added"],
            list(SHATTERED_HEART_ELIGIBLE_SKILLS),
        )

    def test_replica_plinth_requires_an_owned_study_and_consumes_complete_pairs(self):
        data = _player()
        _give_all_pairs(data)
        data, _info = _add_pairs(data)
        _give_all_pairs(data)
        data, _info = _add_pairs(data)  # fourteen pairs before the weekly boundary
        data["shop_market_clock"]["answered_cards"] = 7 * SHATTERED_HEART_REVIEWS_PER_DAY
        data, _info = _add_pairs(data)
        self.assertEqual(data["shattered_heart"]["replica_pieces_awarded"], 2)

        blocked, ok, info = apply_shattered_heart_command_pure(data, "build_replica_plinth")
        self.assertFalse(ok)
        self.assertIn("Study", info["reason"])
        self.assertFalse(blocked["shattered_heart"]["replica_plinth_built"])

        data["house_owned"] = True
        data["house_rooms_bought"] = {"study": True}
        built, ok, info = apply_shattered_heart_command_pure(data, "build_replica_plinth")
        self.assertTrue(ok, info)
        self.assertEqual(info["skill_xp"], {"construction": 1.0})
        self.assertEqual(built["inventory"][SHATTERED_HEART_PLINTH_ITEM], 0)
        self.assertTrue(built["shattered_heart"]["replica_plinth_built"])
        self.assertTrue(shattered_heart_view_pure(built)["add_replica_enabled"])

        added, ok, info = apply_shattered_heart_command_pure(built, "add_replica_pairs")
        self.assertTrue(ok, info)
        self.assertEqual(info["pair_ids"], ("agility",))
        self.assertEqual(info["pieces_added"], 2)
        self.assertEqual(added["shattered_heart"]["replica_pairs_added"], ["agility"])
        self.assertEqual(added["inventory"][SHATTERED_HEART_REPLICA_ITEMS[0]], 0)
        self.assertEqual(added["inventory"][SHATTERED_HEART_REPLICA_ITEMS[1]], 0)


class ShatteredHeartPersistenceTests(unittest.TestCase):
    def test_schema_92_migration_and_round_trip_preserve_progress(self):
        old = _default_player()
        old["config_version"] = 91
        old.pop("shattered_heart", None)
        migrated = migrate_loaded_data(old, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(CURRENT_CONFIG_VERSION, 95)
        self.assertEqual(migrated["config_version"], 95)
        self.assertEqual(
            migrated["shattered_heart"], default_shattered_heart_state_pure()
        )

        state = migrated["shattered_heart"]
        state["placed_pairs"] = list(SHATTERED_HEART_ELIGIBLE_SKILLS[:14])
        state["bag_rocks"] = [SHATTERED_HEART_ROCK_ITEMS[0]]
        state["statues_completed"] = 2
        state["completion_day"] = 9
        state["replica_pieces_awarded"] = 4
        state["replica_pairs_added"] = ["agility", "herblore"]
        loaded = migrate_loaded_data(
            json.loads(json.dumps(migrated)), ORE_DATA, ITEM_DEFINITIONS
        )
        loaded_state = loaded["shattered_heart"]
        self.assertEqual(
            loaded_state["placed_pairs"], list(SHATTERED_HEART_ELIGIBLE_SKILLS[:14])
        )
        self.assertEqual(loaded_state["bag_rocks"], [SHATTERED_HEART_ROCK_ITEMS[0]])
        self.assertEqual(loaded_state["statues_completed"], 2)
        self.assertEqual(loaded_state["completion_day"], 9)
        self.assertEqual(loaded_state["replica_pieces_awarded"], 4)
        self.assertEqual(loaded_state["replica_pairs_added"], ["agility", "herblore"])


class ShatteredHeartRuntimeIntegrationTests(unittest.TestCase):
    def test_real_mining_handler_from_fresh_defaults_awards_rocks_and_persists(self):
        player = _default_player()
        player["current_ore"] = "copper"
        player["mining_level"] = 99
        calls = {
            "errors": [],
            "levels": [],
            "activity": [],
            "xp": [],
            "saves": 0,
        }
        self.assertTrue(handle_mining_answer(_runtime_context(player, calls)))
        mining_rocks = SHATTERED_HEART_SKILLS_BY_ID["mining"].rock_items
        self.assertEqual(sum(int(player["inventory"].get(name, 0)) for name in mining_rocks), 2)
        self.assertEqual(player["shattered_heart"]["last_rock_skill"], "mining")
        self.assertTrue(any("Mining strange rocks" in text for text in calls["activity"]))
        self.assertEqual(calls["saves"], 1)
        telemetry = player["action_telemetry"]["actions"]["mining:copper"]
        self.assertEqual(telemetry["attempts"], 1)
        self.assertEqual(telemetry["successes"], 1)
        self.assertEqual(
            telemetry["outputs"].get("Copper ore", 0),
            player["inventory"].get("Copper ore", 0),
        )
        self.assertEqual(player["inventory"].get("Uncut diamond", 0), 1)
        self.assertEqual(telemetry["outputs"].get("Uncut diamond", 0), 1)

    def test_real_fishing_handler_does_not_record_a_replaced_singular_output(self):
        player = _default_player()
        player["fishing_level"] = 1
        calls = {
            "errors": [],
            "levels": [],
            "activity": [],
            "xp": [],
            "saves": 0,
        }
        self.assertTrue(handle_fishing_answer(_runtime_context(player, calls)))
        telemetry = next(
            row
            for key, row in player["action_telemetry"]["actions"].items()
            if key.startswith("fishing:")
        )
        for item_name, amount in telemetry["outputs"].items():
            self.assertEqual(amount, player["inventory"].get(item_name, 0))

    def test_inferno_adze_rocks_do_not_replace_an_incidental_bird_nest(self):
        player = _default_player()
        player["inventory"] = {"Inferno adze": 1}
        player["woodcutting_level"] = 99
        player["current_tree"] = "tree"
        calls = {
            "errors": [],
            "levels": [],
            "activity": [],
            "xp": [],
            "saves": 0,
        }
        self.assertTrue(handle_woodcutting_answer(_runtime_context(player, calls)))
        self.assertEqual(player["inventory"].get("Bird's nest (seeds)", 0), 1)
        self.assertEqual(
            sum(
                int(player["inventory"].get(item_name, 0))
                for item_name in SHATTERED_HEART_SKILLS_BY_ID["woodcutting"].rock_items
            ),
            2,
        )

    def test_real_farming_queue_and_big_chinchompa_use_their_awarded_skills(self):
        farmer = _default_player()
        farmer["inventory"].update(
            {"Potato seed": 10, "Rake": 1, "Seed dibber": 1}
        )
        farmer, _step_id, _message = add_farm_queue_step_pure(
            farmer,
            "plant",
            "falador_allotment_north",
            crop_id="potato",
        )
        calls = {
            "errors": [],
            "levels": [],
            "activity": [],
            "xp": [],
            "saves": 0,
        }
        self.assertTrue(handle_farming_queue_answer(_runtime_context(farmer, calls)))
        self.assertEqual(
            sum(
                int(farmer["inventory"].get(item_name, 0))
                for item_name in SHATTERED_HEART_SKILLS_BY_ID["farming"].rock_items
            ),
            2,
        )

        hunter = _default_player()
        hunter["current_utility"] = BIG_CHINCHOMPA_UTILITY_ID
        hunter["hunter_level"] = 99
        hunter["shop_market_clock"]["answered_cards"] = (
            BIG_CHINCHOMPA_EVENT_FIRST_SLOT_REVIEW
        )
        hunter, events = advance_big_chinchompa_world_clock_pure(hunter)
        self.assertTrue(events)
        calls = {
            "errors": [],
            "levels": [],
            "activity": [],
            "xp": [],
            "saves": 0,
        }
        self.assertTrue(handle_utility_answer(_runtime_context(hunter, calls)))
        self.assertEqual(
            sum(
                int(hunter["inventory"].get(item_name, 0))
                for item_name in SHATTERED_HEART_SKILLS_BY_ID["hunter"].rock_items
            ),
            2,
        )


@unittest.skipUnless(QT_AVAILABLE, "offscreen Qt lane only")
class ShatteredHeartQtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_panel_renders_view_owned_controls_at_laptop_height_in_dark_mode(self):
        original_palette = self.app.palette()
        dark = QPalette()
        dark.setColor(QPalette.ColorRole.Window, QColor(35, 35, 35))
        dark.setColor(QPalette.ColorRole.Base, QColor(24, 24, 24))
        dark.setColor(QPalette.ColorRole.Text, QColor(235, 235, 235))
        dark.setColor(QPalette.ColorRole.WindowText, QColor(235, 235, 235))
        self.app.setPalette(dark)
        try:
            panel = ShatteredHeartPanel(
                _default_player(),
                on_command=lambda *_args: {"ok": True},
            )
            panel.show()
            panel.resize(520, 560)
            for _ in range(4):
                self.app.processEvents()
            self.assertGreater(panel.height(), 0)
            self.assertLessEqual(panel.sizeHint().height(), 560)
            self.assertTrue(
                panel.findChild(QPushButton, "shatteredHeartClaimBagButton").isVisible()
            )
            self.assertFalse(
                panel.findChild(QPushButton, "shatteredHeartDestroyBagButton").isVisible()
            )
            self.assertEqual(
                panel.findChild(QProgressBar, "shatteredHeartProgress").maximum(), 15
            )
            gate = panel.findChild(QLabel, "shatteredHeartWeeklyGate")
            self.assertGreater(gate.palette().color(QPalette.ColorRole.Text).lightness(), 128)
            panel.close()
        finally:
            self.app.setPalette(original_palette)


if __name__ == "__main__":
    unittest.main()
