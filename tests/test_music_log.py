"""The Music Log: catalog integrity, automatic unlocks, and the 350-task track.

Design contract clause D16 of
``memory-bank/achievement-diary-item-grants-design.md``.

The load-bearing test here is ``test_every_live_track_can_actually_be_unlocked``:
it builds the state each track names and asserts the track arrives. A track
whose trigger no feature can satisfy is an inert row, which is the exact defect
the log exists to avoid. Feature-owned rows stay latent until their predicates
become obtainable, then activate without a separate music-catalog change.
"""

from __future__ import annotations

import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ORE_DATA
from ankiscape.core.storage_pure import (
    CURRENT_CONFIG_VERSION,
    default_player_data,
    migrate_loaded_data,
)
from ankiscape.data.achievement_diary_data import ACHIEVEMENT_DIARY_CATALOG
from ankiscape.data.music_log_data import MUSIC_TRACKS, TRIGGER_KINDS
from ankiscape.data.quest_data import QUESTS_BY_ID
from ankiscape.logic.achievement_diary_logic import MUSIC_UNLOCK_TASK_COUNT
from ankiscape.logic.music_log_logic import (
    music_log_totals_pure,
    music_log_view_pure,
    refresh_music_log_pure,
    track_is_latent_pure,
)


def _player(**overrides) -> dict:
    player = default_player_data(ORE_DATA)
    player.update(overrides)
    return player


def _complete_quest(player: dict, quest_id: str) -> dict:
    quests = dict(player.get("quests") or {})
    state = dict(quests.get(quest_id) or {})
    state["completed"] = True
    quests[quest_id] = state
    player["quests"] = quests
    return player


def _all_task_ids() -> list[str]:
    return [
        task.id
        for family in ACHIEVEMENT_DIARY_CATALOG
        for tier in family.tiers
        for task in tier.tasks
        if not task.dormant
    ]


class MusicCatalogTest(unittest.TestCase):
    def test_the_complete_named_cutoff_catalog_is_well_formed(self):
        self.assertEqual(len(MUSIC_TRACKS), 880)
        seen: set[int] = set()
        for track in MUSIC_TRACKS:
            self.assertNotIn(track.id, seen, track.name)
            seen.add(track.id)
            self.assertTrue(track.name)
            self.assertTrue(track.hint)
            self.assertIn(track.trigger_kind, TRIGGER_KINDS, track.name)
            self.assertIn(f"song id {track.id}", track.source)

    def test_every_quest_trigger_names_a_quest_that_actually_ships(self):
        for track in MUSIC_TRACKS:
            if track.trigger_kind == "quest":
                self.assertIn(track.trigger_key, QUESTS_BY_ID, track.name)

    def test_every_live_track_can_actually_be_unlocked(self):
        """No inert rows: build the state each track names, and watch it land."""

        for track in MUSIC_TRACKS:
            if track_is_latent_pure(track):
                continue
            player = _player()
            if track.trigger_kind == "quest":
                player = _complete_quest(player, track.trigger_key)
            elif track.trigger_kind == "activity":
                player["activity_session"] = {"active_id": track.trigger_key}
            elif track.trigger_kind == "enemy":
                player["combat_kill_counts"] = {track.trigger_key: 1}
            else:
                diaries = dict(player["achievement_diaries"])
                diaries["completed_tasks"] = _all_task_ids()
                player["achievement_diaries"] = diaries
            player, newly = refresh_music_log_pure(player)
            self.assertIn(track.name, newly, track.name)
            self.assertIn(track.id, player["music_log"]["unlocked_tracks"], track.name)

    def test_feature_owned_missing_rows_are_latent_but_stay_in_the_denominator(self):
        latent = [track for track in MUSIC_TRACKS if track_is_latent_pure(track)]
        self.assertGreater(len(latent), 600)
        self.assertGreaterEqual(len(_all_task_ids()), MUSIC_UNLOCK_TASK_COUNT)
        self.assertNotIn("The Task at Hand", {track.name for track in latent})
        self.assertTrue(any(track.trigger_kind == "latent" for track in latent))
        totals = music_log_totals_pure(_player())
        self.assertEqual(totals["latent"], len(latent))
        self.assertEqual(totals["total"], len(MUSIC_TRACKS))


class MusicUnlockTest(unittest.TestCase):
    def test_a_new_player_has_an_empty_log(self):
        totals = music_log_totals_pure(_player())
        self.assertEqual(totals["unlocked"], 0)
        self.assertEqual(totals["total"], len(MUSIC_TRACKS))
        self.assertGreater(totals["latent"], 0)

    def test_finishing_a_quest_unlocks_only_that_quest_s_tracks(self):
        quest_track = next(
            track for track in MUSIC_TRACKS if track.trigger_kind == "quest"
        )
        player = _complete_quest(_player(), quest_track.trigger_key)
        player, newly = refresh_music_log_pure(player)
        self.assertIn(quest_track.name, newly)
        expected = {
            track.name
            for track in MUSIC_TRACKS
            if track.trigger_kind == "quest" and track.trigger_key == quest_track.trigger_key
        }
        self.assertEqual(set(newly), expected)

    def test_a_general_activity_trigger_unlocks_its_tracks(self):
        track = next(
            row
            for row in MUSIC_TRACKS
            if row.trigger_kind == "activity" and row.trigger_key != "conquest"
        )
        player = _player(activity_session={"active_id": track.trigger_key})
        player, newly = refresh_music_log_pure(player)
        expected = {
            row.name
            for row in MUSIC_TRACKS
            if row.trigger_kind == "activity" and row.trigger_key == track.trigger_key
        }
        self.assertEqual(set(newly), expected)

    def test_an_enemy_trigger_reads_the_durable_kill_ledger(self):
        track = next(row for row in MUSIC_TRACKS if row.trigger_kind == "enemy")
        player = _player(combat_kill_counts={track.trigger_key: 1})
        player, newly = refresh_music_log_pure(player)
        self.assertIn(track.name, newly)
        self.assertIn(track.id, player["music_log"]["unlocked_tracks"])

    def test_the_task_at_hand_unlocks_at_the_period_task_count(self):
        """The one consumer of ``MUSIC_UNLOCK_TASK_COUNT``."""

        self.assertEqual(MUSIC_UNLOCK_TASK_COUNT, 350)
        track = next(track for track in MUSIC_TRACKS if track.trigger_kind == "task_count")
        self.assertEqual(track.name, "The Task at Hand")
        self.assertIn("350", track.hint)

        # The trigger reads the diary ledger, so drive it from the ledger. Every
        # completed id below the threshold leaves the track locked; reaching the
        # threshold unlocks it. When the roster is shorter than 350 the second
        # half is unreachable and the track is latent, which the sibling test
        # asserts rather than skipping over.
        tasks = _all_task_ids()
        player = _player()
        diaries = dict(player["achievement_diaries"])
        diaries["completed_tasks"] = tasks[: MUSIC_UNLOCK_TASK_COUNT - 1]
        player["achievement_diaries"] = diaries
        player, newly = refresh_music_log_pure(player)
        self.assertNotIn(track.name, newly)

        if len(tasks) >= MUSIC_UNLOCK_TASK_COUNT:
            diaries = dict(player["achievement_diaries"])
            diaries["completed_tasks"] = tasks[:MUSIC_UNLOCK_TASK_COUNT]
            player["achievement_diaries"] = diaries
            player, newly = refresh_music_log_pure(player)
            self.assertIn(track.name, newly)
        else:
            self.assertTrue(track_is_latent_pure(track))

    def test_an_unlocked_track_is_sticky(self):
        quest_track = next(track for track in MUSIC_TRACKS if track.trigger_kind == "quest")
        player = _complete_quest(_player(), quest_track.trigger_key)
        player, _newly = refresh_music_log_pure(player)
        player["quests"] = {}
        player, newly = refresh_music_log_pure(player)
        self.assertEqual(newly, ())
        self.assertIn(quest_track.id, player["music_log"]["unlocked_tracks"])

    def test_an_unknown_track_id_is_sanitized_out_of_the_log(self):
        player = _player()
        player["music_log"] = {"version": 1, "unlocked_tracks": [999_999, "nonsense"]}
        player, _newly = refresh_music_log_pure(player)
        self.assertEqual(player["music_log"]["unlocked_tracks"], [])


class MusicViewTest(unittest.TestCase):
    def test_the_view_owns_its_own_search_and_completion_filters(self):
        quest_track = next(track for track in MUSIC_TRACKS if track.trigger_kind == "quest")
        player = _complete_quest(_player(), quest_track.trigger_key)
        player, _newly = refresh_music_log_pure(player)

        view = music_log_view_pure(player)
        self.assertEqual(view["total"], music_log_totals_pure(player)["total"])
        self.assertGreater(view["unlocked"], 0)

        unlocked = music_log_view_pure(player, completion_filter="unlocked")
        self.assertTrue(all(row["unlocked"] for row in unlocked["tracks"]))
        locked = music_log_view_pure(player, completion_filter="locked")
        self.assertFalse(any(row["unlocked"] for row in locked["tracks"]))
        self.assertEqual(
            len(unlocked["tracks"]) + len(locked["tracks"]), len(MUSIC_TRACKS)
        )

        searched = music_log_view_pure(player, search=quest_track.name)
        row = next(row for row in searched["tracks"] if row["name"] == quest_track.name)
        self.assertEqual(row["status"], "Unlocked")
        self.assertEqual(row["source"], quest_track.source)
        self.assertEqual(row["label"], quest_track.name)

        locked_track = next(
            track for track in MUSIC_TRACKS if track.id not in player["music_log"]["unlocked_tracks"]
        )
        self.assertEqual(
            music_log_view_pure(player, search=locked_track.name)["tracks"],
            (),
        )
        locked_search = music_log_view_pure(player, search=locked_track.hint)
        locked_row = next(
            row for row in locked_search["tracks"] if row["track_id"] == locked_track.id
        )
        self.assertEqual(locked_row["label"], locked_track.hint)

        latent = music_log_view_pure(player, completion_filter="latent")
        self.assertTrue(latent["tracks"])
        self.assertTrue(all(row["status"] == "Latent" for row in latent["tracks"]))


class MusicMigrationTest(unittest.TestCase):
    def test_an_old_save_gains_the_log_and_its_earned_tracks_on_load(self):
        quest_track = next(track for track in MUSIC_TRACKS if track.trigger_kind == "quest")
        player = _complete_quest(_player(), quest_track.trigger_key)
        player.pop("music_log", None)
        player["config_version"] = 88

        migrated = migrate_loaded_data(player, ORE_DATA)
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertIn(quest_track.id, migrated["music_log"]["unlocked_tracks"])


if __name__ == "__main__":
    unittest.main()
