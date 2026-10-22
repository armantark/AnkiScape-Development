"""The next world day follows completed study days, once at its boundary."""

import sqlite3
import types
import unittest

import pkg_alias  # noqa: F401
from ankiscape.logic.pace import world_clock
from tests.pace.test_calendar_speed import clock_player


class RevlogCollection:
    def __init__(self, store=None):
        self.connection = sqlite3.connect(":memory:")
        self.connection.execute("create table revlog (id integer primary key, ease integer)")
        self.db = self
        self.sched = types.SimpleNamespace(day_cutoff=2000000000)
        self.store = dict(store or {})
        self.queries = 0

    def get_config(self, key, default=None):
        return self.store.get(key, default)

    def all(self, sql, *args):
        self.queries += 1
        return self.connection.execute(sql, args).fetchall()

    def add_day(self, days_ago, count, ease=3):
        start = (self.sched.day_cutoff - (days_ago + 1) * 86400) * 1000
        self.connection.executemany("insert into revlog values (?, ?)", ((start + index, ease) for index in range(count)))


class StudyVolumeTests(unittest.TestCase):
    def test_six_study_days_use_the_default_and_seven_use_the_clamped_median(self):
        def suggest(counts):
            return world_clock.suggested_world_day_cards_pure(world_clock.study_median_pure(counts))

        self.assertEqual(suggest([300] * 6), 240)
        self.assertEqual(suggest([0] * 53 + [300] * 7), 300)
        self.assertEqual(suggest([1, 2, 3, 4, 5, 6, 7]), 100)
        self.assertEqual(suggest([1100] * 7), 1000)
        self.assertEqual(suggest([100, 200, 400, 600, 800, 900, 1000]), 600)

    def test_only_answers_in_the_previous_sixty_complete_anki_days_count(self):
        from ankiscape.core.study_volume import daily_study_counts

        col = RevlogCollection()
        self.addCleanup(col.connection.close)
        for days_ago, count in ((61, 11), (60, 12), (59, 13), (1, 14), (0, 15)):
            col.add_day(days_ago, count)
        col.add_day(2, 9, ease=0)
        self.assertEqual(daily_study_counts(col), [12, 13, 14])
        self.assertEqual(col.queries, 1)

    def test_fixed_day_skips_the_log_and_adaptive_day_queries_only_at_boundary(self):
        from ankiscape.core.study_volume import next_world_day_length

        col = RevlogCollection({"ankiscape_world_day_follow_study_volume": True})
        self.addCleanup(col.connection.close)
        for day in range(1, 8):
            col.add_day(day, 300)
        self.assertEqual(next_world_day_length(col, clock_player(238)), 240)
        self.assertEqual(col.queries, 0)
        self.assertEqual(next_world_day_length(col, clock_player(239)), 300)
        self.assertEqual(col.queries, 1)
        col.store.update({"ankiscape_world_day_follow_study_volume": False, "ankiscape_world_day_cards": 500})
        self.assertEqual(next_world_day_length(col, clock_player(239)), 500)
        self.assertEqual(col.queries, 1)

    def test_fixed_values_are_clamped_and_bad_values_use_the_default(self):
        from ankiscape.core.study_volume import next_world_day_length

        col = RevlogCollection({"ankiscape_world_day_follow_study_volume": False})
        self.addCleanup(col.connection.close)
        for raw, expected in ((-1, 100), (1001, 1000), ("bad", 240)):
            col.store["ankiscape_world_day_cards"] = raw
            self.assertEqual(next_world_day_length(col, clock_player(239)), expected)
