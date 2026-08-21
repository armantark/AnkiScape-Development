from __future__ import annotations

import copy
import itertools
import json
import os
import random
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
from ankiscape.data.enchanted_key_data import (
    ENCHANTED_KEY_ACTIVITY_ID,
    ENCHANTED_KEY_COLDEST,
    ENCHANTED_KEY_COLDER,
    ENCHANTED_KEY_DIG_DISTANCE,
    ENCHANTED_KEY_ITEM,
    ENCHANTED_KEY_MJOLNIRS,
    ENCHANTED_KEY_REPLACEMENT_BLOCKING_QUEST_ID,
    ENCHANTED_KEY_REPLACEMENT_COST,
    ENCHANTED_KEY_SITE_IDS,
    ENCHANTED_KEY_SITES,
    ENCHANTED_KEY_SPADE,
    ENCHANTED_KEY_TEMPERATURES,
    ENCHANTED_KEY_WARMER,
    enchanted_key_temperature_pure,
)
from ankiscape.logic.enchanted_key_logic import (
    apply_enchanted_key_command_pure,
    apply_enchanted_key_review_pure,
    chebyshev_distance_pure,
    default_enchanted_key_state_pure,
    enchanted_key_can_review_pure,
    enchanted_key_roster_pure,
    enchanted_key_view_pure,
    sanitize_enchanted_key_state_pure,
)
from ankiscape.runtime.runtime_actions import RuntimeActionContext, handle_utility_answer


_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SITES_BY_ID = {site.id: site for site in ENCHANTED_KEY_SITES}


def _player(**overrides):
    """A save that finished Making History and kept the key and a spade."""
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data["quests"]["making_history"] = {
        "started": True,
        "progress": 4,
        "completed": True,
    }
    data["inventory"][ENCHANTED_KEY_ITEM] = 1
    data["inventory"][ENCHANTED_KEY_SPADE] = 1
    data.update(overrides)
    return data


def _search(data, site_id, rng):
    data, ok, info = apply_enchanted_key_command_pure(
        data, "select_site", {"site_id": site_id}
    )
    if not ok:
        raise AssertionError(info)
    data, ok, result = apply_enchanted_key_review_pure(data, rng)
    if not ok:
        raise AssertionError(result)
    return data, result


def _dig_everything(data, rng, *, limit=400):
    """Play the whole hunt by sweeping the remaining sites, yielding each dig."""
    for _ in range(limit):
        view = enchanted_key_view_pure(data)
        if view["complete"]:
            return data
        for site_id in view["selectable_site_ids"]:
            data, result = _search(data, site_id, rng)
            if result["dug"]:
                yield data, result
                break
    raise AssertionError("the hunt never finished")


class EnchantedKeyDataAndGatesTests(unittest.TestCase):
    def test_the_activity_row_items_and_period_art_are_registered(self):
        spec = UTILITY_ACTIVITY_DATA[ENCHANTED_KEY_ACTIVITY_ID]
        self.assertEqual(spec["surface"], "activities")
        self.assertEqual(spec["group"], "distractions_and_diversions")
        self.assertIn("oldid=6554980", spec["source"])
        self.assertTrue(os.path.isfile(spec["icon_path"]))
        for mjolnir in ENCHANTED_KEY_MJOLNIRS:
            self.assertIn(mjolnir, EXTRA_ITEM_DATA)
            self.assertTrue(os.path.isfile(EXTRA_ITEM_IMAGES[mjolnir]), mjolnir)

    def test_every_treasure_item_the_hunt_grants_is_a_registered_item(self):
        known = {row.storage_key for row in ITEM_DEFINITIONS} | set(EXTRA_ITEM_DATA)
        for site in ENCHANTED_KEY_SITES:
            for item_name, quantity in site.rewards:
                self.assertIn(item_name, known, f"{site.id} -> {item_name}")
                self.assertGreater(quantity, 0)

    def test_period_assets_are_local_registered_and_cutoff_pinned(self):
        with open(
            os.path.join(_ROOT, "assets_provenance.json"),
            encoding="utf-8",
        ) as handle:
            provenance = json.load(handle)
        for relative in (
            "activityicons/enchanted_key.png",
            "questitems/enchanted_key.png",
            "activityitems/guthix_mjolnir.png",
            "activityitems/saradomin_mjolnir.png",
            "activityitems/zamorak_mjolnir.png",
        ):
            self.assertTrue(os.path.isfile(os.path.join(_ROOT, relative)), relative)
            self.assertIn(relative, provenance)
            self.assertLessEqual(
                provenance[relative]["timestamp"],
                "2012-11-20T00:00:00Z",
                relative,
            )

    def test_the_quest_the_key_and_the_spade_are_all_real_gates(self):
        unquested = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        self.assertIn(
            "Complete Making History",
            enchanted_key_view_pure(unquested)["missing_requirements"],
        )

        keyless = _player()
        keyless["inventory"][ENCHANTED_KEY_ITEM] = 0
        self.assertIn(
            f"Carry the {ENCHANTED_KEY_ITEM}",
            enchanted_key_view_pure(keyless)["missing_requirements"],
        )

        spadeless = _player()
        spadeless["inventory"][ENCHANTED_KEY_SPADE] = 0
        self.assertIn(
            f"Carry a {ENCHANTED_KEY_SPADE} to dig",
            enchanted_key_view_pure(spadeless)["missing_requirements"],
        )
        self.assertFalse(enchanted_key_can_review_pure(spadeless))
        blocked, ok, info = apply_enchanted_key_command_pure(
            spadeless, "select_site", {"site_id": ENCHANTED_KEY_SITE_IDS[0]}
        )
        self.assertTrue(ok, info)
        _same, ok, result = apply_enchanted_key_review_pure(blocked, lambda: 0.5)
        self.assertFalse(ok)
        self.assertIn(ENCHANTED_KEY_SPADE, result["reason"])

    def test_the_temperature_ladder_is_the_period_table(self):
        for threshold, message in ENCHANTED_KEY_TEMPERATURES:
            self.assertEqual(enchanted_key_temperature_pure(threshold), message)
            self.assertNotEqual(
                enchanted_key_temperature_pure(threshold + 1), message
            )
        self.assertEqual(enchanted_key_temperature_pure(0), "The key is steaming.")
        self.assertEqual(enchanted_key_temperature_pure(10_000), ENCHANTED_KEY_COLDEST)

    def test_the_flattened_geometry_reaches_these_bands_and_no_others(self):
        """The whole period ladder ships; the flattened hunt cannot fire it all.

        Pinned rather than left to be discovered: a search either lands on the
        treasure or on another site, and the sites are never closer than 61
        steps, so three bands are unreachable here. Trimming them would
        misrepresent the source, so they stay and this test says so out loud.
        """
        distances = [
            chebyshev_distance_pure(left, right)
            for left, right in itertools.combinations(ENCHANTED_KEY_SITES, 2)
        ]
        self.assertGreater(min(distances), ENCHANTED_KEY_DIG_DISTANCE)
        reachable = {enchanted_key_temperature_pure(0)} | {
            enchanted_key_temperature_pure(distance) for distance in distances
        }
        self.assertEqual(
            reachable,
            {
                "The key is steaming.",
                "It's hot.",
                "It's warm.",
                "It's cold.",
                "It's very cold.",
            },
        )

    def test_commands_rebuild_owned_state_without_mutating_the_input(self):
        original = _player()
        frozen = copy.deepcopy(original)
        updated, ok, info = apply_enchanted_key_command_pure(
            original, "select_site", {"site_id": ENCHANTED_KEY_SITE_IDS[0]}
        )
        self.assertTrue(ok, info)
        self.assertEqual(original, frozen)
        self.assertIsNot(updated["enchanted_key"], original["enchanted_key"])


class EnchantedKeyMechanicsTests(unittest.TestCase):
    def test_the_first_treasure_is_always_fremennik_province(self):
        for seed in range(12):
            data, result = _search(
                _player(),
                ENCHANTED_KEY_SITE_IDS[0],
                random.Random(seed).random,
            )
            self.assertTrue(result["dug"], seed)
            self.assertEqual(result["site_id"], "fremennik_province", seed)

    def test_the_rest_of_the_order_varies_between_saves(self):
        orders = set()
        for seed in range(20):
            data, _result = _search(
                _player(), ENCHANTED_KEY_SITE_IDS[0], random.Random(seed).random
            )
            order = tuple(data["enchanted_key"]["site_order"])
            self.assertEqual(order[0], ENCHANTED_KEY_SITE_IDS[0])
            self.assertEqual(sorted(order), sorted(ENCHANTED_KEY_SITE_IDS))
            orders.add(order)
        self.assertGreater(len(orders), 1)

    def test_a_wrong_site_reads_a_temperature_and_costs_the_review(self):
        data = _player()
        # Fremennik Province is the first target for every save, so searching
        # anywhere else must miss.
        data, result = _search(data, "al_kharid", random.Random(1).random)
        self.assertFalse(result["dug"])
        self.assertEqual(result["relation"], "")
        self.assertEqual(
            result["reading"],
            enchanted_key_temperature_pure(
                chebyshev_distance_pure(
                    _SITES_BY_ID["al_kharid"], _SITES_BY_ID["fremennik_province"]
                )
            ),
        )
        self.assertEqual(data["enchanted_key"]["found"], 0)
        self.assertEqual(data["inventory"]["Pure essence"], 0)

    def test_the_reading_reports_warmer_and_colder_against_the_last_search(self):
        data = _player()
        far = "al_kharid"
        near = "gnome_stronghold"
        target = _SITES_BY_ID["fremennik_province"]
        self.assertGreater(
            chebyshev_distance_pure(_SITES_BY_ID[far], target),
            chebyshev_distance_pure(_SITES_BY_ID[near], target),
        )
        rng = random.Random(2).random
        data, first = _search(data, far, rng)
        self.assertEqual(first["relation"], "")
        data, warmer = _search(data, near, rng)
        self.assertEqual(warmer["relation"], ENCHANTED_KEY_WARMER)
        data, colder = _search(data, far, rng)
        self.assertEqual(colder["relation"], ENCHANTED_KEY_COLDER)

    def test_a_dug_site_cannot_be_searched_again(self):
        data, result = _search(
            _player(), ENCHANTED_KEY_SITE_IDS[0], random.Random(3).random
        )
        self.assertTrue(result["dug"])
        roster = enchanted_key_roster_pure(data)
        dug = next(row for row in roster if row["id"] == ENCHANTED_KEY_SITE_IDS[0])
        self.assertTrue(dug["found"])
        self.assertNotIn(
            ENCHANTED_KEY_SITE_IDS[0],
            enchanted_key_view_pure(data)["selectable_site_ids"],
        )
        blocked, ok, info = apply_enchanted_key_command_pure(
            data, "select_site", {"site_id": ENCHANTED_KEY_SITE_IDS[0]}
        )
        self.assertFalse(ok)
        self.assertIn("not dug up yet", info["reason"])
        self.assertEqual(blocked["enchanted_key"]["found"], 1)

    def test_erin_replaces_a_destroyed_key_for_five_hundred_coins(self):
        data = _player()
        data["inventory"][ENCHANTED_KEY_ITEM] = 0
        view = enchanted_key_view_pure(data)
        self.assertTrue(view["replacement_visible"])
        self.assertFalse(view["replacement_enabled"])
        broke, ok, info = apply_enchanted_key_command_pure(data, "replace_key")
        self.assertFalse(ok)
        self.assertIn("coins", info["reason"])
        self.assertEqual(broke["inventory"][ENCHANTED_KEY_ITEM], 0)

        data["inventory"]["Coins"] = ENCHANTED_KEY_REPLACEMENT_COST
        replaced, ok, info = apply_enchanted_key_command_pure(data, "replace_key")
        self.assertTrue(ok, info)
        self.assertEqual(replaced["inventory"][ENCHANTED_KEY_ITEM], 1)
        self.assertEqual(replaced["inventory"]["Coins"], 0)
        self.assertTrue(enchanted_key_view_pure(replaced)["requirements_met"])

    def test_erin_stops_replacing_the_key_once_meeting_history_starts(self):
        data = _player()
        data["inventory"][ENCHANTED_KEY_ITEM] = 0
        data["inventory"]["Coins"] = 10_000
        data["quests"][ENCHANTED_KEY_REPLACEMENT_BLOCKING_QUEST_ID] = {
            "started": True,
            "progress": 1,
            "completed": False,
        }
        view = enchanted_key_view_pure(data)
        self.assertFalse(view["replacement_visible"])
        self.assertFalse(view["replacement_enabled"])
        refused, ok, info = apply_enchanted_key_command_pure(data, "replace_key")
        self.assertFalse(ok)
        self.assertIn("Meeting History", info["reason"])
        self.assertEqual(refused["inventory"]["Coins"], 10_000)

    def test_the_view_owns_every_button_decision_the_panel_renders(self):
        locked = enchanted_key_view_pure(
            default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        )
        self.assertEqual(locked["selectable_site_ids"], ())
        self.assertFalse(locked["can_review"])
        self.assertFalse(locked["replacement_visible"])

        ready = enchanted_key_view_pure(_player())
        self.assertEqual(
            set(ready["selectable_site_ids"]), set(ENCHANTED_KEY_SITE_IDS)
        )
        self.assertFalse(ready["can_review"])

        chosen, ok, info = apply_enchanted_key_command_pure(
            _player(), "select_site", {"site_id": "body_altar"}
        )
        self.assertTrue(ok, info)
        self.assertTrue(enchanted_key_view_pure(chosen)["can_review"])


class EnchantedKeyPersistenceAndRuntimeTests(unittest.TestCase):
    def test_the_sanitizer_drops_an_order_that_would_shorten_the_hunt(self):
        truncated = sanitize_enchanted_key_state_pure(
            {
                "site_order": list(ENCHANTED_KEY_SITE_IDS[:5]),
                "found": 4,
                "selected_site_id": "al_kharid",
                "last_distance": 900,
            }
        )
        self.assertEqual(truncated["site_order"], [])
        self.assertEqual(truncated["found"], 0)

        duplicated = sanitize_enchanted_key_state_pure(
            {"site_order": [ENCHANTED_KEY_SITE_IDS[0]] * 11, "found": 3}
        )
        self.assertEqual(duplicated["site_order"], [])

        good = sanitize_enchanted_key_state_pure(
            {
                "site_order": list(ENCHANTED_KEY_SITE_IDS),
                "found": 99,
                "selected_site_id": "nowhere",
                "wall_clock_expiry": 12,
            }
        )
        self.assertEqual(good["found"], len(ENCHANTED_KEY_SITE_IDS))
        self.assertEqual(good["selected_site_id"], "")
        self.assertNotIn("wall_clock_expiry", good)

    def test_migration_restores_a_hunt_in_progress(self):
        data = _player()
        rng = random.Random(9).random
        data, _result = _search(data, ENCHANTED_KEY_SITE_IDS[0], rng)
        data, ok, info = apply_enchanted_key_command_pure(
            data, "select_site", {"site_id": data["enchanted_key"]["site_order"][1]}
        )
        self.assertTrue(ok, info)

        migrated = migrate_loaded_data(
            copy.deepcopy(data),
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(
            migrated["enchanted_key"]["site_order"],
            data["enchanted_key"]["site_order"],
        )
        self.assertEqual(migrated["enchanted_key"]["found"], 1)
        self.assertEqual(
            migrated["enchanted_key"]["selected_site_id"],
            data["enchanted_key"]["selected_site_id"],
        )
        self.assertTrue(enchanted_key_can_review_pure(migrated))

    def test_a_fresh_save_starts_with_no_inert_or_wall_clock_fields(self):
        state = default_enchanted_key_state_pure()
        self.assertEqual(
            set(state),
            {
                "version",
                "site_order",
                "found",
                "selected_site_id",
                "last_distance",
                "last_result",
            },
        )
        self.assertEqual(
            default_player_data(ORE_DATA, ITEM_DEFINITIONS)["enchanted_key"],
            state,
        )
        self.assertNotIn("timestamp", enchanted_key_view_pure(_player()))

    def test_the_runtime_routes_a_selected_search_and_persists(self):
        player = _player()
        player, ok, info = apply_enchanted_key_command_pure(
            player, "select_site", {"site_id": ENCHANTED_KEY_SITE_IDS[0]}
        )
        self.assertTrue(ok, info)
        player["current_utility"] = ENCHANTED_KEY_ACTIVITY_ID
        saved = []
        gains = []
        ctx = RuntimeActionContext(
            player_data=player,
            random_random=random.Random(4).random,
            show_error_message=lambda *_args: self.fail("unexpected runtime error"),
            deactivate_current_skill=lambda: None,
            award_skill_exp=lambda *_args: self.fail("the hunt awards no XP"),
            award_hidden_skill_exp=lambda *_args: None,
            level_up_check=lambda *_args: None,
            check_achievements=lambda *_args: None,
            save_player_data=lambda: saved.append(True),
            refresh_skill_availability=lambda: None,
            show_exp=lambda amount: gains.append(float(amount)),
            show_activity_gain=lambda message: gains.append(str(message)),
            implemented_exp_keys_snapshot=lambda: {},
            show_quest_exp_delta=lambda *_args: None,
        )
        self.assertTrue(handle_utility_answer(ctx))
        self.assertEqual(saved, [True])
        self.assertEqual(player["enchanted_key"]["found"], 1)
        self.assertEqual(player["inventory"]["Law rune"], 15)
        self.assertTrue(any("Fremennik" in str(value) for value in gains))


class EnchantedKeyRealRewardPathTests(unittest.TestCase):
    """Every treasure, both mjolnir sites and the melt reached by real digs."""

    def test_the_whole_hunt_pays_every_site_once_and_then_melts_the_key(self):
        data = _player()
        rng = random.Random(20121114).random
        dug_ids = []
        for data, result in _dig_everything(data, rng):
            dug_ids.append(result["site_id"])

        self.assertEqual(sorted(dug_ids), sorted(ENCHANTED_KEY_SITE_IDS))
        self.assertEqual(dug_ids[0], "fremennik_province")

        expected: dict[str, int] = {}
        for site in ENCHANTED_KEY_SITES:
            for item_name, quantity in site.rewards:
                expected[item_name] = expected.get(item_name, 0) + quantity
        for item_name, quantity in expected.items():
            self.assertEqual(data["inventory"][item_name], quantity, item_name)

        # "This is the only way to obtain these unique weapons."
        for mjolnir in ENCHANTED_KEY_MJOLNIRS:
            self.assertEqual(data["inventory"][mjolnir], 1, mjolnir)

        # "Once all the treasure has been found, the key will melt."
        self.assertTrue(result["melted"])
        self.assertEqual(data["inventory"][ENCHANTED_KEY_ITEM], 0)
        view = enchanted_key_view_pure(data)
        self.assertTrue(view["complete"])
        self.assertEqual(view["remaining"], 0)
        self.assertEqual(view["selectable_site_ids"], ())
        self.assertFalse(view["can_review"])

    def test_a_melted_key_is_not_replaced_and_the_hunt_does_not_restart(self):
        data = _player()
        for data, _result in _dig_everything(data, random.Random(6).random):
            pass
        view = enchanted_key_view_pure(data)
        self.assertFalse(view["replacement_visible"])
        refused, ok, info = apply_enchanted_key_command_pure(data, "replace_key")
        self.assertFalse(ok)
        self.assertEqual(refused["inventory"][ENCHANTED_KEY_ITEM], 0)
        _same, ok, result = apply_enchanted_key_review_pure(data, lambda: 0.5)
        self.assertFalse(ok)
        self.assertIn("melted", result["reason"])
        self.assertEqual(data["enchanted_key"]["found"], len(ENCHANTED_KEY_SITE_IDS))

    def test_losing_the_key_mid_hunt_is_recoverable_and_keeps_the_progress(self):
        data = _player()
        rng = random.Random(8).random
        data, first = _search(data, ENCHANTED_KEY_SITE_IDS[0], rng)
        self.assertTrue(first["dug"])
        order = list(data["enchanted_key"]["site_order"])

        data["inventory"][ENCHANTED_KEY_ITEM] = 0
        self.assertFalse(enchanted_key_can_review_pure(data))
        data["inventory"]["Coins"] = ENCHANTED_KEY_REPLACEMENT_COST
        data, ok, info = apply_enchanted_key_command_pure(data, "replace_key")
        self.assertTrue(ok, info)

        data, second = _search(data, order[1], rng)
        self.assertTrue(second["dug"])
        self.assertEqual(second["site_id"], order[1])
        self.assertEqual(data["enchanted_key"]["found"], 2)
        self.assertEqual(data["enchanted_key"]["site_order"], order)


if __name__ == "__main__":
    unittest.main()
