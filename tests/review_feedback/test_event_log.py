"""The retained event log and the reviewer strip's drawer over it.

The drawer lists what each review said, newest first, by review age, and
folds one review's identical rows into one row that names their count.
"""

from __future__ import annotations

import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.review_event_log import REVIEW_EVENT_LOG_RETAINED, record_review_event_pure
from ankiscape.core.storage_pure import (
    CURRENT_CONFIG_VERSION,
    default_player_data,
    migrate_loaded_data,
)
from ankiscape.logic.review_strip_logic import (
    REVIEW_EVENT_LOG_DEFAULT_LIMIT,
    review_event_log_drawer_view_pure,
)


def _player() -> dict:
    return default_player_data(ORE_DATA, ITEM_DEFINITIONS)


def _at_review(data: dict, review: int) -> dict:
    data["shop_market_clock"] = {"answered_cards": review, "market_tick": review}
    return data


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

        rows = review_event_log_drawer_view_pure(data, expanded=True)["rows"]
        colours = {row["foreground"] for row in rows} | {row["repeat_foreground"] for row in rows}

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

    def test_one_reviews_identical_rows_fold_across_other_rows_and_never_cross_a_review_age(self):
        impure = "The ore was too impure"
        data = _at_review(_player(), 4)
        for _ in range(2):
            data = record_review_event_pure(data, "activity", impure)
        data = _at_review(data, 5)
        data = record_review_event_pure(data, "xp", "+62 XP · Smithing")
        for _ in range(5):
            data = record_review_event_pure(data, "activity", impure)
        data = record_review_event_pure(data, "activity", "Bank run — arrived and restocked")
        data = record_review_event_pure(data, "activity", impure)

        view = review_event_log_drawer_view_pure(data, expanded=True)

        self.assertEqual(
            [row["label"] for row in view["rows"]],
            [
                f"0 reviews ago · {impure} - x6",
                "0 reviews ago · Bank run — arrived and restocked",
                "0 reviews ago · +62 XP · Smithing",
                f"1 review ago · {impure} - x2",
            ],
        )
        self.assertEqual([row["repeat_label"] for row in view["rows"]], ["x6", "", "", "x2"])
        self.assertEqual(view["title"], "Event log (4)")
        self.assertEqual(len(data["review_event_log"]), 10)

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


if __name__ == "__main__":
    unittest.main()
