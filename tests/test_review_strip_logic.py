"""The reviewer strip decides everything here; ui.py only renders it.

The always-visible strip shows live experience bars and the Grand Exchange
fills drawer. Pass 4 keeps Distractions and Farming in separate persistent
badges and adds a retained, review-counted event-log drawer.
"""

from __future__ import annotations

import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
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
from ankiscape.logic.grand_exchange_logic import ge_fill_drawer_view_pure
from ankiscape.logic.review_strip_logic import (
    ACTIVITY_TRAINED_SKILLS,
    REVIEW_EVENT_LOG_DEFAULT_LIMIT,
    activity_awards_experience_now_pure,
    activity_trained_skills_pure,
    activity_xp_bars_pure,
    record_review_event_pure,
    review_event_log_drawer_view_pure,
    review_overlay_layout_view_pure,
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
    def test_the_watchable_set_covers_the_complete_dnd_catalog(self):
        catalog_ids = {
            activity_id
            for activity_id, spec in UTILITY_ACTIVITY_DATA.items()
            if spec.get("group") == "distractions_and_diversions"
        }
        catalog_ids.add(EVIL_TREE_UTILITY_ID)

        self.assertEqual(DND_ACTIVITY_IDS, catalog_ids)
        self.assertIn(FISH_FLINGERS_ACTIVITY_ID, DND_ACTIVITY_IDS)
        self.assertIn(SHOOTING_STAR_ACTIVITY_ID, DND_ACTIVITY_IDS)
        self.assertIn(BIG_CHINCHOMPA_UTILITY_ID, DND_ACTIVITY_IDS)
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

    def test_v104_clears_the_old_default_trio_but_keeps_other_opt_ins(self):
        old = _player()
        old["config_version"] = 103
        old["dnd_favourites"] = [
            SHOOTING_STAR_ACTIVITY_ID,
            EVIL_TREE_UTILITY_ID,
            BIG_CHINCHOMPA_UTILITY_ID,
            FISH_FLINGERS_ACTIVITY_ID,
        ]

        migrated = migrate_loaded_data(old, ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["dnd_favourites"], [FISH_FLINGERS_ACTIVITY_ID])


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

    def test_an_active_fish_flingers_session_is_a_navigable_notification(self):
        data = _player()
        data["dnd_favourites"] = [FISH_FLINGERS_ACTIVITY_ID]
        data["current_utility"] = FISH_FLINGERS_ACTIVITY_ID
        data["activity_session"] = {"active_id": FISH_FLINGERS_ACTIVITY_ID}

        view = review_status_badges_view_pure(data)["distractions"]

        self.assertEqual(view["count"], 1)
        self.assertEqual(
            view["rows"],
            ({
                "activity_id": FISH_FLINGERS_ACTIVITY_ID,
                "name": "Fish Flingers",
                "status": "Active session",
                "live": True,
                "favourite": True,
            },),
        )

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


class OverlayLayoutViewTest(unittest.TestCase):
    def test_the_card_viewport_wins_and_the_cluster_docks_below_it(self):
        view = review_overlay_layout_view_pure(
            parent_size=(1000, 700),
            content_rect=(20, 20, 960, 500),
            cluster_size=(700, 130),
        )
        self.assertTrue(view["visible"])
        self.assertEqual(view["dock"], "below")
        self.assertGreaterEqual(view["y"], 540)

    def test_a_full_viewport_card_gets_the_padded_overlay_bottom_dock(self):
        # A scrolling card leaves no outside rectangle; the cluster must stay
        # visible over the viewport bottom (the UI pads the document to match)
        # rather than vanish — the 2026-07-29 tall-card regression.
        view = review_overlay_layout_view_pure(
            parent_size=(600, 500),
            content_rect=(0, 0, 600, 500),
            cluster_size=(500, 100),
        )
        self.assertTrue(view["visible"])
        self.assertEqual(view["dock"], "overlay-bottom")
        self.assertEqual(view["y"], 500 - 100 - 8)


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
