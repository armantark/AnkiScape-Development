"""The reviewer strip decides everything here; ui.py only renders it.

The always-visible strip shows live experience bars and the Grand Exchange
fills drawer. Pass 4 keeps Distractions and Farming in separate persistent
badges and adds a retained, review-counted event-log drawer.
"""

from __future__ import annotations

import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.action_registry import (
    review_action_display_names,
    review_action_handler_key,
)
from ankiscape.core.constants import (
    DUNGEONEERING_EXP_TABLE,
    ITEM_DEFINITIONS,
    ORE_DATA,
    UTILITY_ACTIVITY_DATA,
)
from ankiscape.core.storage_pure import (
    CURRENT_CONFIG_VERSION,
    default_player_data,
    migrate_loaded_data,
)
from ankiscape.data.big_chinchompa_data import BIG_CHINCHOMPA_UTILITY_ID
from ankiscape.data.evil_tree_data import EVIL_TREE_UTILITY_ID
from ankiscape.data.fish_flingers_data import FISH_FLINGERS_ACTIVITY_ID
from ankiscape.data.goblin_raids_data import (
    GOBLIN_RAIDS_ACTIVITY_ID,
    GOBLIN_RAIDS_SPAWN_REVIEWS,
)
from ankiscape.data.shooting_star_data import SHOOTING_STAR_ACTIVITY_ID
from ankiscape.data.tears_of_guthix_data import TEARS_OF_GUTHIX_ACTIVITY_ID
from ankiscape.logic.dnd_favourites_logic import (
    DND_ACTIVITY_IDS,
    dnd_favourite_context_menu_view_pure,
    dnd_favourite_detail_button_view_pure,
    is_dnd_favourite_pure,
    sanitize_dnd_favourites_pure,
    toggle_dnd_favourite_pure,
)
from ankiscape.logic.fish_flingers_logic import enter_fish_flingers_pure
from ankiscape.logic.goblin_raids_logic import advance_goblin_raids_world_clock_pure
from ankiscape.logic.grand_exchange_logic import ge_fill_drawer_view_pure
from ankiscape.logic.review_strip_logic import (
    ACTIVITY_TRAINED_SKILLS,
    DND_NOTIFICATION_ACTIVITY_IDS,
    REVIEW_EVENT_LOG_DEFAULT_LIMIT,
    REVIEW_STRIP_HEIGHT,
    activity_awards_experience_now_pure,
    activity_trained_skills_pure,
    activity_xp_bars_pure,
    record_review_event_pure,
    request_review_bank_run_pure,
    review_bank_run_button_view_pure,
    review_bank_run_travel_view_pure,
    review_event_log_drawer_view_pure,
    review_status_badges_view_pure,
    skill_xp_bar_pure,
)
from ankiscape.logic.shooting_star_logic import (
    advance_shooting_star_world_clock_pure,
    shooting_star_view_pure,
)


def _player() -> dict:
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data["toolbelt"] = {
        "mining": ["bronze_pickaxe"],
        "woodcutting": ["bronze_hatchet"],
    }
    return data


def _with_live_star(data: dict) -> dict:
    """Run the world clock until a mineable star exists, like a real session."""
    for tick in range(1, 500):
        data["shop_market_clock"] = {"answered_cards": tick, "market_tick": tick}
        updated, _events = advance_shooting_star_world_clock_pure(data)
        data.update(updated)
        if shooting_star_view_pure(data, has_usable_pickaxe=True)["active"]:
            return data
    raise AssertionError("the world clock produced no shooting star")


class ActivityExperienceBarsTest(unittest.TestCase):
    def test_a_live_star_session_shows_the_real_mining_bar(self):
        data = _with_live_star(_player())
        data["mining_level"] = 30
        data["mining_exp"] = 14_000.0

        view = activity_xp_bars_pure(data, SHOOTING_STAR_ACTIVITY_ID)

        self.assertEqual(len(view["bars"]), 1)
        bar = view["bars"][0]
        self.assertEqual(bar["skill"], "Mining")
        self.assertEqual(bar["level"], 30)
        self.assertEqual(bar["target_level"], 31)
        self.assertGreater(bar["percent"], 0)
        self.assertLess(bar["percent"], 100)

    def test_dungeoneering_training_bar_continues_past_level_99(self):
        bar = skill_xp_bar_pure(
            {
                "dungeoneering_level": 100,
                "dungeoneering_exp": DUNGEONEERING_EXP_TABLE[99],
            },
            "Dungeoneering",
        )

        self.assertEqual(bar["level"], 100)
        self.assertEqual(bar["target_level"], 101)
        self.assertEqual(bar["percent"], 0)
        self.assertGreater(bar["remaining"], 0)

    def test_the_bar_vanishes_when_the_star_session_ends(self):
        data = _with_live_star(_player())
        self.assertTrue(activity_xp_bars_pure(data, SHOOTING_STAR_ACTIVITY_ID)["bars"])

        # The event resolving is what ends the session; the target is unchanged.
        data["shooting_star"]["active_event"] = None

        self.assertFalse(shooting_star_view_pure(data, has_usable_pickaxe=True)["active"])
        self.assertEqual(
            activity_xp_bars_pure(data, SHOOTING_STAR_ACTIVITY_ID)["bars"], ()
        )

    def test_a_session_in_another_activity_takes_the_bars_away(self):
        data = _with_live_star(_player())
        data["activity_session"] = {"active_id": "pyramid_plunder"}

        self.assertFalse(
            activity_awards_experience_now_pure(data, SHOOTING_STAR_ACTIVITY_ID)
        )
        self.assertEqual(
            activity_xp_bars_pure(data, SHOOTING_STAR_ACTIVITY_ID)["bars"], ()
        )
        self.assertTrue(
            activity_awards_experience_now_pure(data, "pyramid_plunder")
        )

    def test_the_strip_never_carries_more_than_two_bars(self):
        data = _player()
        data["activity_session"] = {"active_id": "pyramid_plunder"}

        view = activity_xp_bars_pure(data, "pyramid_plunder")

        self.assertEqual(
            [bar["skill"] for bar in view["bars"]], ["Thieving", "Strength"]
        )
        self.assertEqual(view["also_trains"], ("Runecrafting",))

    def test_the_evil_tree_names_the_skill_its_current_phase_trains(self):
        from ankiscape.logic.evil_tree_logic import (
            advance_evil_tree_world_clock_pure,
            apply_evil_tree_review_pure,
            evil_tree_view_pure,
        )

        data = _player()
        # Without a session the tree is between phases; felling is the phase a
        # player is in for most of an event, so that is the resting answer.
        self.assertEqual(
            activity_trained_skills_pure(data, EVIL_TREE_UTILITY_ID),
            ("Woodcutting",),
        )

        data["shop_market_clock"] = {"answered_cards": 20, "market_tick": 20}
        updated, _events = advance_evil_tree_world_clock_pure(
            data, tier_roll=0.0, location_roll=0.0
        )
        data.update(updated)
        data["farming_level"] = 99
        data["woodcutting_level"] = 99
        data["firemaking_level"] = 99
        updated, ok, _info = apply_evil_tree_review_pure(
            data, has_usable_hatchet=True
        )
        self.assertTrue(ok)
        data.update(updated)

        # The reducer awards Farming while nurturing, so the bar follows the
        # phase rather than the family.
        phase = evil_tree_view_pure(data, has_usable_hatchet=True)["phase"]
        expected = {
            "nurture": ("Farming",),
            "prepare": ("Woodcutting",),
            "fell": ("Woodcutting", "Firemaking"),
        }[phase]
        self.assertEqual(
            activity_trained_skills_pure(data, EVIL_TREE_UTILITY_ID), expected
        )

    def test_tears_of_guthix_follows_its_least_experience_reward_skill(self):
        data = _player()
        for skill in ("attack", "strength", "defence", "ranged", "magic"):
            data[f"{skill}_exp"] = 500_000.0

        trained = activity_trained_skills_pure(data, TEARS_OF_GUTHIX_ACTIVITY_ID)

        self.assertEqual(len(trained), 1)
        self.assertNotIn(trained[0], {"Attack", "Strength", "Magic"})

    def test_an_activity_that_grants_no_experience_shows_no_bar(self):
        data = _player()

        self.assertEqual(activity_xp_bars_pure(data, "castle_wars")["bars"], ())
        self.assertEqual(activity_xp_bars_pure(data, "")["bars"], ())

    def test_every_trained_skill_table_entry_names_a_real_activity_and_skill(self):
        from ankiscape.core.constants import UTILITY_ACTIVITY_DATA
        from ankiscape.core.skill_registry import trainable_skill_definitions

        known_skills = {
            skill.display_name for skill in trainable_skill_definitions()
        }
        for activity_id, skills in ACTIVITY_TRAINED_SKILLS.items():
            with self.subTest(activity=activity_id):
                self.assertTrue(
                    activity_id in UTILITY_ACTIVITY_DATA
                    or activity_id in DND_ACTIVITY_IDS,
                    "the table must not name an activity that does not exist",
                )
                self.assertTrue(skills)
                for skill in skills:
                    self.assertIn(skill, known_skills)

    def test_the_exhaustiveness_sweep_defects_stay_closed(self):
        # The 2026-07-29 sweep drove every family's real reducers; these six
        # granted XP the strip did not show. The expected sets are the sweep's
        # reducer-probe ground truth, not the table read back to itself.
        data = _player()
        expected = {
            "livid_farm": (
                "Magic",
                "Farming",
                "Construction",
                "Crafting",
                "Agility",
            ),
            "mage_training_arena": ("Magic",),
            "warriors_guild_attack_dummy": ("Attack",),
            "warriors_guild_catapult": ("Defence",),
            "warriors_guild_keg_balance": ("Strength",),
            "warriors_guild_shot_put": ("Strength",),
        }
        for activity_id, skills in expected.items():
            with self.subTest(activity=activity_id):
                self.assertEqual(
                    activity_trained_skills_pure(data, activity_id), skills
                )


class DistractionFavouritesTest(unittest.TestCase):
    def test_the_watchable_and_status_tables_cover_the_fixed_dnd_catalog(self):
        expected = {
            "big_chinchompa",
            "big_top_bonanza",
            "bork",
            "court_cases",
            "enchanted_key",
            "evil_tree",
            "familiarisation",
            "fish_flingers",
            "goblin_raids",
            "penguin_hide_and_seek",
            "phoenix_lair",
            "shattered_heart",
            "shooting_stars",
            "skeletal_horror",
            "tears_of_guthix",
            "treasure_trail",
            "troll_invasion",
        }

        self.assertEqual(DND_ACTIVITY_IDS, expected)
        self.assertEqual(DND_NOTIFICATION_ACTIVITY_IDS, expected)
        self.assertNotIn("castle_wars", DND_ACTIVITY_IDS)

    def test_every_distraction_gets_one_context_toggle_and_other_rows_get_none(self):
        data = _player()

        for activity_id in DND_ACTIVITY_IDS:
            with self.subTest(activity=activity_id):
                view = dnd_favourite_context_menu_view_pure(data, activity_id)
                self.assertTrue(view["visible"])
                self.assertTrue(view["enabled"])
                self.assertEqual(view["label"], "Add to notifications")

        data["dnd_favourites"] = [SHOOTING_STAR_ACTIVITY_ID]
        self.assertEqual(
            dnd_favourite_context_menu_view_pure(
                data, SHOOTING_STAR_ACTIVITY_ID
            )["label"],
            "Remove from notifications",
        )
        hidden = dnd_favourite_context_menu_view_pure(data, "castle_wars")
        self.assertFalse(hidden["visible"])
        self.assertFalse(hidden["enabled"])

    def test_detail_star_visibility_and_enabled_state_come_from_its_pure_view(self):
        data = _player()

        hidden = dnd_favourite_detail_button_view_pure(
            data,
            SHOOTING_STAR_ACTIVITY_ID,
            show_detail=False,
        )
        disabled = dnd_favourite_detail_button_view_pure(
            data,
            SHOOTING_STAR_ACTIVITY_ID,
            show_detail=True,
            can_toggle=False,
        )
        data["dnd_favourites"] = [SHOOTING_STAR_ACTIVITY_ID]
        pinned = dnd_favourite_detail_button_view_pure(
            data,
            SHOOTING_STAR_ACTIVITY_ID,
            show_detail=True,
        )
        not_watchable = dnd_favourite_detail_button_view_pure(
            data,
            "castle_wars",
            show_detail=True,
        )

        self.assertFalse(hidden["visible"])
        self.assertTrue(disabled["visible"])
        self.assertFalse(disabled["enabled"])
        self.assertEqual(disabled["text"], "☆")
        self.assertTrue(pinned["enabled"])
        self.assertEqual(pinned["text"], "★")
        self.assertIn("Stop watching", pinned["tooltip"])
        self.assertFalse(not_watchable["visible"])
        self.assertFalse(not_watchable["enabled"])

    def test_the_same_click_pins_and_unpins(self):
        data = _player()

        pinned, ok, info = toggle_dnd_favourite_pure(data, EVIL_TREE_UTILITY_ID)
        self.assertTrue(ok)
        self.assertTrue(info["favourite"])
        self.assertEqual(pinned["dnd_favourites"], [EVIL_TREE_UTILITY_ID])
        self.assertTrue(is_dnd_favourite_pure(pinned, EVIL_TREE_UTILITY_ID))

        cleared, ok, info = toggle_dnd_favourite_pure(pinned, EVIL_TREE_UTILITY_ID)
        self.assertTrue(ok)
        self.assertFalse(info["favourite"])
        self.assertEqual(cleared["dnd_favourites"], [])

    def test_pinning_something_that_is_not_a_distraction_is_refused(self):
        data = _player()

        updated, ok, info = toggle_dnd_favourite_pure(data, "castle_wars")

        self.assertFalse(ok)
        self.assertIn("reason", info)
        self.assertEqual(updated.get("dnd_favourites", []), [])

    def test_the_watch_list_is_bounded_by_the_Distractions_that_exist(self):
        data = _player()
        data["dnd_favourites"] = sorted(DND_ACTIVITY_IDS) * 3

        favourites = sanitize_dnd_favourites_pure(data["dnd_favourites"])

        self.assertEqual(len(favourites), len(DND_ACTIVITY_IDS))
        self.assertEqual(len(set(favourites)), len(favourites))

    def test_sanitize_drops_junk_duplicates_and_unknown_ids(self):
        self.assertEqual(sanitize_dnd_favourites_pure(None), [])
        self.assertEqual(sanitize_dnd_favourites_pure("shooting_stars"), [])
        self.assertEqual(
            sanitize_dnd_favourites_pure(
                [
                    SHOOTING_STAR_ACTIVITY_ID,
                    SHOOTING_STAR_ACTIVITY_ID,
                    "not_an_activity",
                    None,
                    EVIL_TREE_UTILITY_ID,
                ]
            ),
            [SHOOTING_STAR_ACTIVITY_ID, EVIL_TREE_UTILITY_ID],
        )

    def test_the_schema_migration_installs_and_repairs_the_watch_list(self):
        old = _player()
        old["config_version"] = 92
        old.pop("dnd_favourites", None)

        migrated = migrate_loaded_data(old, ORE_DATA, ITEM_DEFINITIONS)

        # The watch list arrived at v95; later families move CURRENT past it.
        self.assertGreaterEqual(CURRENT_CONFIG_VERSION, 95)
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["dnd_favourites"], [])

        migrated["dnd_favourites"] = [SHOOTING_STAR_ACTIVITY_ID, "bogus"]
        reloaded = migrate_loaded_data(migrated, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(reloaded["dnd_favourites"], [SHOOTING_STAR_ACTIVITY_ID])

    def test_v104_drops_implicit_defaults_without_erasing_explicit_pins(self):
        implicit = _with_live_star(_player())
        implicit["config_version"] = 103
        implicit.pop("dnd_favourites", None)

        migrated_implicit = migrate_loaded_data(
            implicit, ORE_DATA, ITEM_DEFINITIONS
        )

        self.assertEqual(migrated_implicit["dnd_favourites"], [])
        self.assertEqual(
            review_status_badges_view_pure(migrated_implicit)["distractions"][
                "rows"
            ],
            (),
        )

        explicit = [
            SHOOTING_STAR_ACTIVITY_ID,
            EVIL_TREE_UTILITY_ID,
            BIG_CHINCHOMPA_UTILITY_ID,
            FISH_FLINGERS_ACTIVITY_ID,
        ]
        implicit["dnd_favourites"] = explicit
        migrated_explicit = migrate_loaded_data(
            implicit, ORE_DATA, ITEM_DEFINITIONS
        )

        self.assertEqual(migrated_explicit["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated_explicit["dnd_favourites"], explicit)


class StatusBadgeViewTest(unittest.TestCase):
    def test_both_badges_keep_separate_seats_with_nothing_live(self):
        views = review_status_badges_view_pure(_player())

        dnd = views["distractions"]
        farming = views["farming"]
        self.assertTrue(dnd["visible"])
        self.assertTrue(farming["visible"])
        self.assertEqual(dnd["rows"], ())
        self.assertEqual(farming["rows"], ())
        self.assertEqual(dnd["title"], "D&D")
        self.assertEqual(farming["title"], "Farming")
        self.assertIn("Notification set is empty", dnd["tooltip"])

    def test_live_world_events_notify_only_after_the_player_opts_in(self):
        data = _with_live_star(_player())

        views = review_status_badges_view_pure(data)
        dnd = views["distractions"]
        farming = views["farming"]
        self.assertEqual(dnd["rows"], ())
        self.assertEqual(dnd["count"], 0)
        self.assertEqual(farming["rows"], ())

        data["dnd_favourites"] = [SHOOTING_STAR_ACTIVITY_ID]
        pinned = review_status_badges_view_pure(data)["distractions"]
        star_rows = [
            row
            for row in pinned["rows"]
            if row.get("activity_id") == SHOOTING_STAR_ACTIVITY_ID
        ]
        self.assertEqual(len(star_rows), 1)
        self.assertTrue(star_rows[0]["live"])
        self.assertTrue(star_rows[0]["favourite"])
        self.assertIn("stardust", star_rows[0]["status"])
        self.assertEqual(pinned["count"], 1)

    def test_a_quiet_favourite_still_gets_a_dnd_line(self):
        data = _player()
        data["dnd_favourites"] = [TEARS_OF_GUTHIX_ACTIVITY_ID]

        view = review_status_badges_view_pure(data)["distractions"]

        self.assertEqual(len(view["rows"]), 1)
        row = view["rows"][0]
        self.assertEqual(row["activity_id"], TEARS_OF_GUTHIX_ACTIVITY_ID)
        self.assertFalse(row["live"])
        self.assertTrue(row["status"])
        self.assertEqual(view["count"], 0, "a quiet line is not a notification")
        self.assertIn("Tears of Guthix", view["tooltip"])

    def test_fish_flingers_notifies_before_entry_and_reports_session_status(self):
        data = _player()
        data["dnd_favourites"] = [FISH_FLINGERS_ACTIVITY_ID]

        ready = review_status_badges_view_pure(data)["distractions"]
        self.assertEqual(ready["count"], 1)
        self.assertIn("2 Fish Flingers tickets available", ready["rows"][0]["status"])

        entered, ok, info = enter_fish_flingers_pure(data)
        self.assertTrue(ok, info)
        entered["dnd_favourites"] = [FISH_FLINGERS_ACTIVITY_ID]
        active = review_status_badges_view_pure(entered)["distractions"]

        self.assertEqual(active["count"], 1)
        self.assertEqual(active["rows"][0]["activity_id"], FISH_FLINGERS_ACTIVITY_ID)
        self.assertTrue(active["rows"][0]["live"])
        self.assertIn("Review 1/8", active["rows"][0]["status"])
        self.assertIn("stock", active["rows"][0]["status"])
        self.assertIn("tickets remaining", active["rows"][0]["status"])

    def test_announced_goblin_raid_is_a_live_notification(self):
        data = _player()
        data["dnd_favourites"] = [GOBLIN_RAIDS_ACTIVITY_ID]
        data["shop_market_clock"] = {
            "answered_cards": GOBLIN_RAIDS_SPAWN_REVIEWS,
            "market_tick": GOBLIN_RAIDS_SPAWN_REVIEWS,
        }
        data, events = advance_goblin_raids_world_clock_pure(
            data, site_roll=0.0
        )
        self.assertTrue(events)

        view = review_status_badges_view_pure(data)["distractions"]

        self.assertEqual(view["count"], 1)
        self.assertTrue(view["rows"][0]["live"])
        self.assertIn("Raid at", view["rows"][0]["status"])
        self.assertIn("reviews left", view["rows"][0]["status"])

    def test_ready_tears_of_guthix_entry_is_a_live_notification(self):
        data = _player()
        data["quests"]["tears_of_guthix"] = {
            "started": True,
            "progress": 3,
            "completed": True,
        }
        data["quest_points"] = 44
        data["dnd_favourites"] = [TEARS_OF_GUTHIX_ACTIVITY_ID]

        view = review_status_badges_view_pure(data)["distractions"]

        self.assertEqual(view["count"], 1)
        self.assertTrue(view["rows"][0]["live"])
        self.assertIn("Entry ready", view["rows"][0]["status"])
        self.assertIn("collection ticks", view["rows"][0]["status"])

    def test_farming_rows_belong_only_to_the_farming_badge(self):
        from ankiscape.logic.farming_logic import (
            advance_farm_clock_pure,
            execute_farm_field_step_pure,
        )

        data = _player()
        data["farming_level"] = 99
        data["inventory"].update(
            {"Rake": 1, "Seed dibber": 1, "Spade": 1, "Potato seed": 3}
        )
        data, ok, _info = execute_farm_field_step_pure(
            data,
            {
                "kind": "plant",
                "patch_id": "falador_allotment_north",
                "crop_id": "potato",
            },
        )
        self.assertTrue(ok)
        data, _events = advance_farm_clock_pure(data, 7, lambda: 1.0)

        views = review_status_badges_view_pure(data)
        farming_rows = views["farming"]["rows"]
        self.assertEqual(views["distractions"]["rows"], ())
        self.assertEqual(len(farming_rows), 1)
        self.assertEqual(farming_rows[0]["patch_id"], "falador_allotment_north")
        self.assertEqual(farming_rows[0]["name"], "Potato")
        self.assertTrue(farming_rows[0]["live"], "a mature crop needs the player")
        self.assertEqual(views["farming"]["count"], 1)

    def test_a_diseased_crop_keeps_the_farming_alert_form(self):
        from ankiscape.logic.farming_logic import (
            advance_farm_clock_pure,
            execute_farm_field_step_pure,
        )

        data = _player()
        data["farming_level"] = 99
        data["inventory"].update(
            {"Rake": 1, "Seed dibber": 1, "Spade": 1, "Potato seed": 3}
        )
        data, ok, _info = execute_farm_field_step_pure(
            data,
            {
                "kind": "plant",
                "patch_id": "falador_allotment_north",
                "crop_id": "potato",
            },
        )
        self.assertTrue(ok)
        data, _events = advance_farm_clock_pure(data, 2, lambda: 1.0)
        data["farm_patches"]["falador_allotment_north"].update(
            {"diseased": True, "dead": False}
        )

        self.assertTrue(review_status_badges_view_pure(data)["farming"]["alert"])


class EventLogViewTest(unittest.TestCase):
    def test_notifications_are_newest_first_and_review_counted(self):
        data = _player()
        data["shop_market_clock"] = {"answered_cards": 3, "market_tick": 3}
        data = record_review_event_pure(data, "xp", "+25 XP")
        data["shop_market_clock"] = {"answered_cards": 5, "market_tick": 5}
        data = record_review_event_pure(data, "activity", "+1 Mackerel")

        view = review_event_log_drawer_view_pure(data, expanded=True)

        self.assertTrue(view["visible"])
        self.assertEqual(
            [row["label"] for row in view["rows"]],
            ["0 reviews ago · +1 Mackerel", "2 reviews ago · +25 XP"],
        )
        self.assertEqual(view["rows"][1]["tone"], "xp")
        self.assertNotIn(
            view["rows"][1]["foreground"],
            {"#85c54b", "#e0b341"},
        )

    def test_event_log_tones_never_reuse_ge_yellow_or_green(self):
        data = _player()
        for kind in ("xp", "achievement", "activity"):
            data = record_review_event_pure(data, kind, kind)

        colours = {
            row["foreground"]
            for row in review_event_log_drawer_view_pure(data, expanded=True)["rows"]
        }

        self.assertTrue(colours.isdisjoint({"#85c54b", "#e0b341", "#f0c75e"}))

    def test_the_drawer_starts_with_ten_then_expands_lazily(self):
        data = _player()
        for review in range(25):
            data["shop_market_clock"] = {
                "answered_cards": review,
                "market_tick": review,
            }
            data = record_review_event_pure(data, "activity", f"event {review}")

        collapsed = review_event_log_drawer_view_pure(data)
        first = review_event_log_drawer_view_pure(data, expanded=True)
        second = review_event_log_drawer_view_pure(
            data,
            visible_limit=first["next_limit"],
            expanded=True,
        )

        self.assertFalse(collapsed["rows_visible"])
        self.assertEqual(len(first["rows"]), REVIEW_EVENT_LOG_DEFAULT_LIMIT)
        self.assertTrue(first["show_more_visible"])
        self.assertEqual(len(second["rows"]), 20)
        self.assertEqual(first["rows"][0]["text"], "event 24")

    def test_history_expands_past_200_without_dropping_the_first_event(self):
        data = _player()
        for review in range(201):
            data["shop_market_clock"] = {
                "answered_cards": review,
                "market_tick": review,
            }
            data = record_review_event_pure(data, "xp", f"event {review}")

        expanded = review_event_log_drawer_view_pure(
            data,
            visible_limit=201,
            expanded=True,
        )

        self.assertEqual(len(data["review_event_log"]), 201)
        self.assertEqual(data["review_event_log"][0]["text"], "event 0")
        self.assertEqual(len(expanded["rows"]), 201)
        self.assertEqual(expanded["rows"][-1]["text"], "event 0")
        self.assertFalse(expanded["show_more_enabled"])

    def test_the_retention_window_trims_oldest_first_at_the_bound(self):
        """4.15 answer 2: the save keeps a large bounded window, not forever."""
        from ankiscape.logic.review_strip_logic import (
            REVIEW_EVENT_LOG_RETAINED,
            record_review_event_pure,
        )

        data = _player()
        for review in range(REVIEW_EVENT_LOG_RETAINED + 5):
            data["shop_market_clock"] = {
                "answered_cards": review,
                "market_tick": review,
            }
            data = record_review_event_pure(data, "xp", f"event {review}")
        log = data["review_event_log"]
        self.assertEqual(len(log), REVIEW_EVENT_LOG_RETAINED)
        self.assertEqual(log[0]["text"], "event 5")
        self.assertEqual(log[-1]["text"], f"event {REVIEW_EVENT_LOG_RETAINED + 4}")

    def test_migration_repairs_malformed_rows(self):
        old = _player()
        old["config_version"] = 98
        old["review_event_log"] = [
            {"review": "4", "kind": "xp", "text": "+4 XP"},
            {"review": -2, "kind": "activity", "text": ""},
            "junk",
        ]
        migrated = migrate_loaded_data(old, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(
            migrated["review_event_log"],
            [{"review": 4, "kind": "xp", "text": "+4 XP"}],
        )


class ReviewBankRunViewTest(unittest.TestCase):
    def test_the_button_is_visible_and_enabled_for_every_registered_action(self):
        views = {
            name: review_bank_run_button_view_pure(
                _player(), review_action_handler_key(name)
            )
            for name in review_action_display_names()
        }

        self.assertTrue(views)
        for name, view in views.items():
            with self.subTest(name=name):
                self.assertEqual(view["text"], "Bank run")
                self.assertEqual(
                    view["tooltip"],
                    "Deposit inventory and restock same supplies",
                )
                self.assertTrue(view["visible"])
                self.assertTrue(view["enabled"])

    def test_a_queued_request_only_disables_its_own_target(self):
        data = {
            **_player(),
            "review_bank_run_requested_target": "copper_ore",
        }

        self.assertFalse(
            review_bank_run_button_view_pure(
                data, "mining", "copper_ore"
            )["enabled"]
        )
        self.assertTrue(
            review_bank_run_button_view_pure(
                data, "mining", "iron_ore"
            )["enabled"]
        )

    def test_combat_and_skilling_requests_enter_their_existing_state_seams(self):
        combat, ok = request_review_bank_run_pure(
            _player(), "combat", "chicken"
        )
        skilling, skilling_ok = request_review_bank_run_pure(
            _player(), "mining", "copper_ore"
        )
        utility, utility_ok = request_review_bank_run_pure(
            _player(), "utility", None
        )

        self.assertTrue(ok)
        self.assertEqual(combat["combat_bank_run"]["target_id"], "chicken")
        self.assertGreater(combat["combat_bank_run"]["reviews_remaining"], 0)
        self.assertTrue(skilling_ok)
        self.assertEqual(
            skilling["review_bank_run_requested_target"], "copper_ore"
        )
        self.assertEqual(skilling.get("skilling_bank_run", {}), {})
        self.assertTrue(utility_ok)
        self.assertEqual(utility["review_bank_run_requested_handler"], "utility")

    def test_combat_request_runs_the_route_inside_a_live_encounter(self):
        combat, ok = request_review_bank_run_pure(
            {
                **_player(),
                "combat_encounter": {"target_id": "chicken", "disengaged": False},
            },
            "combat",
            "chicken",
        )

        self.assertTrue(ok)
        self.assertEqual(
            combat["combat_bank_run"],
            {"reviews_remaining": 2, "target_id": "chicken"},
        )
        # The encounter survives the two-review trip.
        self.assertEqual(
            combat["combat_encounter"],
            {"target_id": "chicken", "disengaged": False},
        )


class BankRunTravelViewTest(unittest.TestCase):
    def test_no_bank_run_reports_inactive(self):
        view = review_bank_run_travel_view_pure(_player())

        self.assertEqual(view, {"active": False})

    def test_active_combat_run_projects_its_two_review_trip(self):
        data = _player()
        data["combat_bank_run"] = {
            "reviews_remaining": 2,
            "target_id": "chicken",
        }

        view = review_bank_run_travel_view_pure(data)

        self.assertTrue(view["active"])
        self.assertEqual(view["kind"], "combat")
        self.assertEqual(view["total"], 2)
        self.assertEqual(view["remaining"], 2)
        self.assertEqual(view["percent"], 0)

    def test_halfway_combat_run_names_the_progress(self):
        data = _player()
        data["combat_bank_run"] = {
            "reviews_remaining": 1,
            "target_id": "chicken",
        }

        view = review_bank_run_travel_view_pure(data)

        self.assertEqual(view["remaining"], 1)
        self.assertEqual(view["percent"], 50)
        self.assertEqual(
            view["text"], "Bank run — Banking supplies · 1/2 travel reviews"
        )

    def test_active_carried_run_uses_its_route_label_and_total(self):
        data = _player()
        data["skilling_bank_run"] = {
            "reviews_remaining": 3,
            "reviews_total": 10,
            "route_label": "Running to the bank",
            "route_phases": [
                {"id": "return", "label": "Heading home", "reviews": 5},
                {"id": "bank", "label": "Banking", "reviews": 5},
            ],
        }

        view = review_bank_run_travel_view_pure(data)

        self.assertTrue(view["active"])
        self.assertEqual(view["kind"], "carried")
        # Three reviews left sits inside the closing five-review Banking phase.
        self.assertEqual(view["label"], "Banking")
        self.assertEqual(view["total"], 10)
        self.assertEqual(view["remaining"], 3)
        self.assertEqual(view["percent"], 70)

    def test_queued_manual_request_shows_before_the_route_starts(self):
        data = _player()
        data["review_bank_run_requested_target"] = "copper_ore"

        view = review_bank_run_travel_view_pure(data)

        self.assertTrue(view["active"])
        self.assertEqual(view["kind"], "carried")
        self.assertEqual(view["total"], 1)

    def test_pending_request_selects_its_own_route_over_stale_states(self):
        data = _player()
        data["review_bank_run_requested_handler"] = "combat"
        data["skilling_bank_run"] = {
            "reviews_remaining": 4,
            "reviews_total": 10,
            "route_label": "Running to the bank",
        }

        view = review_bank_run_travel_view_pure(data)

        self.assertEqual(view["kind"], "combat")

    def test_coexisting_states_prefer_combat(self):
        data = _player()
        data["combat_bank_run"] = {
            "reviews_remaining": 2,
            "target_id": "chicken",
        }
        data["skilling_bank_run"] = {
            "reviews_remaining": 4,
            "reviews_total": 10,
            "route_label": "Running to the bank",
        }

        view = review_bank_run_travel_view_pure(data)

        self.assertEqual(view["kind"], "combat")


class FillDrawerViewTest(unittest.TestCase):
    def _order(self, **overrides) -> dict:
        order = {
            "id": 1,
            "side": "buy",
            "item_name": "Iron ore",
            "status": "open",
            "original_quantity": 5,
            "remaining_quantity": 5,
            "submitted_unit_price": 100,
            "escrow_coins": 500,
        }
        order.update(overrides)
        return order

    def test_the_drawer_holds_no_seat_without_an_offer(self):
        view = ge_fill_drawer_view_pure(_player())

        self.assertFalse(view["visible"])
        self.assertEqual(view["rows"], ())

    def test_an_open_offer_opens_the_seat_and_rows_run_newest_first(self):
        data = _player()
        data["ge_player_orders"] = [self._order()]
        data["ge_fill_log"] = [
            {
                "card": 8,
                "side": "buy",
                "item_name": "Iron ore",
                "completed_quantity": 3,
                "original_quantity": 5,
            },
            {
                "card": 10,
                "side": "sell",
                "item_name": "Yew logs",
                "completed_quantity": 4,
                "original_quantity": 4,
            },
        ]
        data["shop_market_clock"] = {"answered_cards": 10, "market_tick": 10}

        view = ge_fill_drawer_view_pure(data)

        self.assertTrue(view["visible"])
        self.assertEqual(view["title"], "Recent fills (2)")
        self.assertEqual(
            [row["text"] for row in view["rows"]],
            [
                "Now: Yew logs - 4/4 sold",
                "2 cards ago: Iron ore - 3/5 bought",
            ],
        )

    def test_a_full_offer_reads_complete_and_a_part_offer_reads_partial(self):
        data = _player()
        data["ge_player_orders"] = [self._order()]
        data["ge_fill_log"] = [
            {
                "card": 1,
                "side": "buy",
                "item_name": "Iron ore",
                "completed_quantity": 2,
                "original_quantity": 5,
            },
            {
                "card": 2,
                "side": "buy",
                "item_name": "Iron ore",
                "completed_quantity": 5,
                "original_quantity": 5,
            },
        ]
        data["shop_market_clock"] = {"answered_cards": 2, "market_tick": 2}

        tones = [row["tone"] for row in ge_fill_drawer_view_pure(data)["rows"]]

        self.assertEqual(tones, ["complete", "partial"])

    def test_a_filled_offer_awaiting_collection_keeps_the_drawer_open(self):
        # Otherwise the drawer disappears at the exact moment the fill it exists
        # to report arrives.
        data = _player()
        data["ge_player_orders"] = [
            self._order(
                status="complete",
                remaining_quantity=0,
                completed_quantity=5,
                collectible_items=5,
            )
        ]

        self.assertTrue(ge_fill_drawer_view_pure(data)["visible"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
