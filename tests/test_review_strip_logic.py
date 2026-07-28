"""The reviewer strip decides everything here; ui.py only renders it.

Design-thread section 4.8: the always-visible strip shows what is live right
now — the running activity's real experience bars, the Grand Exchange fills
drawer while an offer is open — plus one permanent seat for the Distractions and
Farming badge, which is the player's notification system.
"""

from __future__ import annotations

import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import (
    CURRENT_CONFIG_VERSION,
    default_player_data,
    migrate_loaded_data,
)
from ankiscape.data.big_chinchompa_data import BIG_CHINCHOMPA_UTILITY_ID
from ankiscape.data.evil_tree_data import EVIL_TREE_UTILITY_ID
from ankiscape.data.shooting_star_data import SHOOTING_STAR_ACTIVITY_ID
from ankiscape.data.tears_of_guthix_data import TEARS_OF_GUTHIX_ACTIVITY_ID
from ankiscape.logic.dnd_favourites_logic import (
    DND_ACTIVITY_IDS,
    is_dnd_favourite_pure,
    sanitize_dnd_favourites_pure,
    toggle_dnd_favourite_pure,
)
from ankiscape.logic.grand_exchange_logic import ge_fill_drawer_view_pure
from ankiscape.logic.review_strip_logic import (
    ACTIVITY_TRAINED_SKILLS,
    activity_awards_experience_now_pure,
    activity_trained_skills_pure,
    activity_xp_bars_pure,
    review_status_badge_view_pure,
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


class DistractionFavouritesTest(unittest.TestCase):
    def test_the_evil_tree_can_be_watched_even_without_an_activity_spec(self):
        # It is a special activity target rather than a UTILITY_ACTIVITY_DATA
        # row, and it is one of the two events the owner named.
        self.assertIn(EVIL_TREE_UTILITY_ID, DND_ACTIVITY_IDS)
        self.assertIn(SHOOTING_STAR_ACTIVITY_ID, DND_ACTIVITY_IDS)
        self.assertIn(BIG_CHINCHOMPA_UTILITY_ID, DND_ACTIVITY_IDS)
        self.assertNotIn("castle_wars", DND_ACTIVITY_IDS)

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

        self.assertEqual(CURRENT_CONFIG_VERSION, 95)
        self.assertEqual(migrated["config_version"], 95)
        self.assertEqual(migrated["dnd_favourites"], [])

        migrated["dnd_favourites"] = [SHOOTING_STAR_ACTIVITY_ID, "bogus"]
        reloaded = migrate_loaded_data(migrated, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(reloaded["dnd_favourites"], [SHOOTING_STAR_ACTIVITY_ID])


class StatusBadgeViewTest(unittest.TestCase):
    def test_the_badge_keeps_its_seat_with_nothing_live(self):
        view = review_status_badge_view_pure(_player())

        self.assertEqual(view["rows"], ())
        self.assertEqual(view["count"], 0)
        self.assertFalse(view["alert"])
        self.assertIn("Pin a Distraction", view["tooltip"])

    def test_a_live_event_becomes_a_row_whether_or_not_it_is_pinned(self):
        data = _with_live_star(_player())

        view = review_status_badge_view_pure(data)
        star_rows = [
            row
            for row in view["rows"]
            if row.get("activity_id") == SHOOTING_STAR_ACTIVITY_ID
        ]
        self.assertEqual(len(star_rows), 1)
        self.assertTrue(star_rows[0]["live"])
        self.assertFalse(star_rows[0]["favourite"])
        self.assertIn("stardust", star_rows[0]["status"])
        self.assertEqual(view["count"], 1)

        data["dnd_favourites"] = [SHOOTING_STAR_ACTIVITY_ID]
        pinned = review_status_badge_view_pure(data)
        star_rows = [
            row
            for row in pinned["rows"]
            if row.get("activity_id") == SHOOTING_STAR_ACTIVITY_ID
        ]
        self.assertEqual(len(star_rows), 1, "a pin must not duplicate a live row")
        self.assertTrue(star_rows[0]["favourite"])

    def test_a_quiet_favourite_still_gets_a_line_and_carries_its_own_status(self):
        data = _player()
        data["dnd_favourites"] = [TEARS_OF_GUTHIX_ACTIVITY_ID]

        view = review_status_badge_view_pure(data)

        self.assertEqual(len(view["rows"]), 1)
        row = view["rows"][0]
        self.assertEqual(row["activity_id"], TEARS_OF_GUTHIX_ACTIVITY_ID)
        self.assertEqual(row["kind"], "distraction")
        self.assertFalse(row["live"])
        self.assertTrue(row["status"])
        self.assertEqual(view["count"], 0, "a quiet line is not a notification")
        self.assertIn("Tears of Guthix", view["tooltip"])

    def test_farming_rows_join_the_same_popover_with_their_patch(self):
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

        view = review_status_badge_view_pure(data)
        farming_rows = [row for row in view["rows"] if row["kind"] == "farming"]
        self.assertEqual(len(farming_rows), 1)
        self.assertEqual(farming_rows[0]["patch_id"], "falador_allotment_north")
        self.assertEqual(farming_rows[0]["name"], "Potato")
        self.assertTrue(farming_rows[0]["live"], "a mature crop needs the player")
        self.assertEqual(view["count"], 1)

    def test_a_diseased_crop_keeps_the_alert_form(self):
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

        self.assertTrue(review_status_badge_view_pure(data)["alert"])


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
