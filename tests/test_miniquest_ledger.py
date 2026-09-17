"""The miniquest category and its registered rows, driven through real reducers.

Authority: memory-bank/design-thread-queue.md section 4.14 item 1 and section
3.23; memory-bank/source-audits/miniquest-ledger-2026-07-29.md.
"""
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import (
    CURRENT_CONFIG_VERSION,
    default_player_data,
    migrate_loaded_data,
)
from ankiscape.data.dominion_tower_data import DOMINION_TOWER_GLOVE_SETS
from ankiscape.data.quest_data import QUESTS_BY_ID, quests_as_dict
from ankiscape.logic.dominion_tower_logic import (
    dominion_tower_available_encounters_pure,
    dominion_tower_view_pure,
)
from ankiscape.logic_pure.logic_pure_quest import (
    # The assembled enemy has no public accessor; the flag has to be read where
    # the encounter row becomes a combat enemy.
    _quest_combat_enemy_spec,
)
from ankiscape.logic_pure.logic_pure import (
    QUEST_SECTION_MINIQUESTS,
    QUEST_SECTION_QUESTS,
    apply_quest_combat_encounter_pure,
    apply_quest_progress_pure,
    can_start_quest_pure,
    quest_catalog_sections_pure,
    quest_current_stage_blocker_reasons_pure,
    quest_locked_reasons_pure,
    start_quest_pure,
)

HUNT_FOR_SUROK = "hunt_for_surok"
LAIR_OF_TARN_RAZORLOR = "lair_of_tarn_razorlor"
BAR_CRAWL = "bar_crawl"
SKIPPY_AND_THE_MOGRES = "skippy_and_the_mogres"
MINIQUEST_IDS = (BAR_CRAWL, HUNT_FOR_SUROK, LAIR_OF_TARN_RAZORLOR, SKIPPY_AND_THE_MOGRES)


def _combat_ready_player():
    player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    for key in ("attack_level", "strength_level", "defense_level", "constitution_level"):
        player_data[key] = 99
    return player_data


def _complete_lair_of_tarn_razorlor(test, player_data):
    """Drive the whole miniquest through the real reducers, mutant then ghost."""
    player_data, started = start_quest_pure(player_data, LAIR_OF_TARN_RAZORLOR, QUEST_DATA)
    test.assertTrue(started)

    for expected_stage in (2, 3, 4, 5):
        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data, LAIR_OF_TARN_RAZORLOR, QUEST_DATA
        )
        test.assertTrue(ok)
        test.assertFalse(completed_now)
        test.assertEqual(
            player_data["quests"][LAIR_OF_TARN_RAZORLOR]["progress"], expected_stage
        )

    for encounter_id, next_stage in (
        ("lair_of_tarn_razorlor_mutant_tarn", 6),
        ("lair_of_tarn_razorlor_tarn_ghost", 7),
    ):
        player_data = _resolve_encounter(test, player_data, LAIR_OF_TARN_RAZORLOR, encounter_id)
        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data, LAIR_OF_TARN_RAZORLOR, QUEST_DATA
        )
        test.assertTrue(ok)
        test.assertFalse(completed_now)
        test.assertEqual(player_data["quests"][LAIR_OF_TARN_RAZORLOR]["progress"], next_stage)

    player_data, ok, completed_now = apply_quest_progress_pure(
        player_data, LAIR_OF_TARN_RAZORLOR, QUEST_DATA
    )
    test.assertTrue(ok)
    test.assertTrue(completed_now)
    test.assertTrue(player_data["quests"][LAIR_OF_TARN_RAZORLOR]["completed"])
    return player_data


def _resolve_encounter(test, player_data, quest_id, encounter_id):
    """Drive real combat bursts until the encounter falls, as a player would."""
    for _burst in range(20):
        player_data, ok, result = apply_quest_combat_encounter_pure(
            player_data, quest_id, QUEST_DATA, encounter_id
        )
        test.assertTrue(ok, result)
        test.assertFalse(result.get("died"), result)
        if result["reason"] == "combat_resolved":
            return player_data
    test.fail(f"{encounter_id} never resolved")


class TestMiniquestFlag(unittest.TestCase):
    def test_only_the_settled_rows_carry_the_flag(self):
        flagged = tuple(quest.id for quest in QUESTS_BY_ID.values() if quest.miniquest)
        self.assertEqual(flagged, MINIQUEST_IDS)

    def test_the_flag_survives_the_trip_into_quest_data(self):
        live = quests_as_dict()
        for quest_id in MINIQUEST_IDS:
            with self.subTest(quest_id=quest_id):
                self.assertTrue(live[quest_id]["miniquest"])
                self.assertTrue(QUEST_DATA[quest_id]["miniquest"])
        self.assertFalse(live["what_lies_below"]["miniquest"])
        self.assertFalse(QUEST_DATA["haunted_mine"]["miniquest"])

    def test_miniquests_award_no_quest_points(self):
        for quest_id in MINIQUEST_IDS:
            with self.subTest(quest_id=quest_id):
                self.assertEqual(QUEST_DATA[quest_id]["point_reward"], 0)

    def test_sections_put_miniquests_last_and_name_both_groups(self):
        rows = tuple(sorted(QUEST_DATA.items()))
        sections = quest_catalog_sections_pure(rows)

        self.assertEqual(
            tuple(section["title"] for section in sections),
            (QUEST_SECTION_QUESTS, QUEST_SECTION_MINIQUESTS),
        )
        self.assertEqual(
            tuple(quest_id for quest_id, _quest in sections[1]["rows"]),
            MINIQUEST_IDS,
        )
        self.assertNotIn(
            HUNT_FOR_SUROK,
            tuple(quest_id for quest_id, _quest in sections[0]["rows"]),
        )

    def test_a_lone_section_drops_its_heading(self):
        quest_only = ((quest_id, QUEST_DATA[quest_id]) for quest_id in ("cooks_assistant",))
        mini_only = ((quest_id, QUEST_DATA[quest_id]) for quest_id in (HUNT_FOR_SUROK,))

        for rows in (tuple(quest_only), tuple(mini_only)):
            sections = quest_catalog_sections_pure(rows)
            with self.subTest(rows=rows[0][0]):
                self.assertEqual(len(sections), 1)
                self.assertEqual(sections[0]["title"], "")

    def test_no_sections_when_every_row_is_filtered_away(self):
        self.assertEqual(quest_catalog_sections_pure(()), ())


class TestHuntForSurok(unittest.TestCase):
    def test_the_what_lies_below_gate_locks_the_row(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["mining_level"] = 42

        self.assertIn(
            "What Lies Below",
            quest_locked_reasons_pure(player_data, HUNT_FOR_SUROK, QUEST_DATA),
        )
        self.assertFalse(can_start_quest_pure(player_data, HUNT_FOR_SUROK, QUEST_DATA))

    def test_the_mining_gate_locks_the_row(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["what_lies_below"]["completed"] = True

        self.assertEqual(
            quest_locked_reasons_pure(player_data, HUNT_FOR_SUROK, QUEST_DATA),
            ("Mining 42",),
        )

    def test_the_miniquest_runs_from_the_statue_to_borks_defeat(self):
        player_data = _combat_ready_player()
        player_data["quests"]["what_lies_below"]["completed"] = True
        player_data["mining_level"] = 42
        player_data["inventory"]["Bronze pickaxe"] = 1

        self.assertTrue(can_start_quest_pure(player_data, HUNT_FOR_SUROK, QUEST_DATA))
        player_data, started = start_quest_pure(player_data, HUNT_FOR_SUROK, QUEST_DATA)
        self.assertTrue(started)

        for expected_stage in (2, 3, 4, 5):
            self.assertEqual(
                quest_current_stage_blocker_reasons_pure(player_data, HUNT_FOR_SUROK, QUEST_DATA),
                (),
            )
            player_data, ok, completed_now = apply_quest_progress_pure(
                player_data, HUNT_FOR_SUROK, QUEST_DATA
            )
            self.assertTrue(ok)
            self.assertFalse(completed_now)
            self.assertEqual(player_data["quests"][HUNT_FOR_SUROK]["progress"], expected_stage)

        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, HUNT_FOR_SUROK, QUEST_DATA),
            ("Battle required: Bork level 267",),
        )
        player_data = _resolve_encounter(
            self, player_data, HUNT_FOR_SUROK, "hunt_for_surok_bork"
        )

        player_data, ok, completed_now = apply_quest_progress_pure(
            player_data, HUNT_FOR_SUROK, QUEST_DATA
        )
        self.assertTrue(ok)
        self.assertTrue(completed_now)
        self.assertTrue(player_data["quests"][HUNT_FOR_SUROK]["completed"])
        self.assertEqual(player_data["slayer_exp"], 5000.0)
        self.assertEqual(player_data["quest_points"], 0)

    def test_the_bork_encounter_reaches_combat_immune_to_poison(self):
        """`Bork` oldid 6565904 prints `immune to poison = Yes`.

        The stage row is only half the answer: the engine reads the flag off
        the assembled enemy, so an `npc_configs` entry that the spec builder
        drops on the floor leaves Bork poisonable.
        """
        stage = next(
            stage
            for stage in QUEST_DATA[HUNT_FOR_SUROK]["stage_requirements"]
            if stage["stage"] == 5
        )
        encounter = stage["combat_encounters"][0]
        self.assertTrue(dict(encounter["npc_configs"])["poison_immune"])
        enemy = _quest_combat_enemy_spec(HUNT_FOR_SUROK, "hunt_for_surok_bork", encounter)
        self.assertTrue(enemy["poison_immune"])

    def test_the_pickaxe_gate_blocks_the_first_stage(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player_data["quests"]["what_lies_below"]["completed"] = True
        player_data["mining_level"] = 42
        player_data["inventory"].pop("Bronze pickaxe", None)
        player_data["toolbelt"] = {}
        player_data, started = start_quest_pure(player_data, HUNT_FOR_SUROK, QUEST_DATA)
        self.assertTrue(started)

        self.assertEqual(
            quest_current_stage_blocker_reasons_pure(player_data, HUNT_FOR_SUROK, QUEST_DATA),
            ("Needs Pickaxe",),
        )


class TestLairOfTarnRazorlor(unittest.TestCase):
    def test_the_haunted_mine_and_slayer_gates_lock_the_row(self):
        player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(
            quest_locked_reasons_pure(player_data, LAIR_OF_TARN_RAZORLOR, QUEST_DATA),
            ("Haunted Mine", "Slayer 40"),
        )

    def test_mutant_tarn_reaches_combat_as_a_melee_attacker_the_text_promises(self):
        """The infobox says "Melee and magic"; the strategy section overrules it.

        `Lair of Tarn Razorlor (miniquest)` oldid 6448364 says Tarn "attacks
        solely with melee if approached", and every AnkiScape battle is an
        approached battle. The shipped text must not promise an attack the
        assembled enemy cannot make.
        """
        stage = next(
            stage
            for stage in QUEST_DATA[LAIR_OF_TARN_RAZORLOR]["stage_requirements"]
            if stage["stage"] == 5
        )
        encounter = stage["combat_encounters"][0]
        enemy = _quest_combat_enemy_spec(
            LAIR_OF_TARN_RAZORLOR, "lair_of_tarn_razorlor_mutant_tarn", encounter
        )
        self.assertEqual(enemy["attack_style"], "melee")
        self.assertIn("attacks solely with melee if approached", encounter["source_text"])

    def test_mutant_tarns_borrowed_block_names_both_darkan_files(self):
        """The mutant's own file states no combat levels, so the ghost's stand in.

        A substitution has to be traceable from the row itself: the source
        string must name the file the numbers came from *and* the file that has
        none, or the reader cannot tell a copy from a reading.
        """
        stages = {
            stage["stage"]: stage
            for stage in QUEST_DATA[LAIR_OF_TARN_RAZORLOR]["stage_requirements"]
        }
        mutant = stages[5]["combat_encounters"][0]
        ghost = stages[6]["combat_encounters"][0]

        self.assertEqual(mutant["npc_stats"], ghost["npc_stats"])
        self.assertIn("mutant_tarn (nostats) (noanims).json", mutant["npc_stats_source"])
        self.assertIn("tarn (noanims).json", mutant["npc_stats_source"])

    def test_the_miniquest_runs_from_the_mine_to_tarns_diary(self):
        player_data = _combat_ready_player()
        player_data["quests"]["haunted_mine"]["completed"] = True
        player_data["slayer_level"] = 40

        self.assertTrue(can_start_quest_pure(player_data, LAIR_OF_TARN_RAZORLOR, QUEST_DATA))
        player_data = _complete_lair_of_tarn_razorlor(self, player_data)

        self.assertEqual(player_data["slayer_exp"], 5000.0)
        self.assertEqual(player_data["quest_points"], 0)

    def test_the_dominion_tower_class_h_gate_now_resolves(self):
        """Section 3.23's one unreachable boss lights up behind Haunted Mine.

        Tarn oldid 6448021's trivia pins the period gate: the Dominion fight
        needs only Haunted Mine, not the Lair miniquest. The ledger row exists
        for its own completion record and must not be required here.
        """
        player_data = _combat_ready_player()
        player_data["slayer_level"] = 40

        before = dominion_tower_view_pure(player_data)
        self.assertNotIn("tarn_razorlor", dominion_tower_available_encounters_pure(player_data, 1))
        self.assertNotIn("tarn_razorlor", before["available_encounters"])

        player_data["quests"]["haunted_mine"]["completed"] = True

        self.assertIn("tarn_razorlor", dominion_tower_available_encounters_pure(player_data, 1))
        # The Lair stays optional for the fight while still recording its own
        # completion when played.
        player_data = _complete_lair_of_tarn_razorlor(self, player_data)
        self.assertIn("tarn_razorlor", dominion_tower_available_encounters_pure(player_data, 1))
        after = dominion_tower_view_pure(player_data)
        self.assertIn("tarn_razorlor", after["available_encounters"])
        self.assertEqual(
            tuple(
                row["display_name"]
                for row in after["available_encounter_rows"]
                if row["id"] == "tarn_razorlor"
            ),
            ("Tarn Razorlor and terror dogs",),
        )
        # The tower's entry gate counts its own 38 quests; completing the
        # Lair miniquest must not inflate that count beyond Haunted Mine's own
        # contribution.
        with_mine_only = 1
        self.assertEqual(after["completed_quests"], with_mine_only)

    def test_the_tarn_encounter_belongs_to_no_glove_set(self):
        """Section 3.23's other claim: no reward was ever blocked on this boss."""
        for glove_set in DOMINION_TOWER_GLOVE_SETS:
            with self.subTest(glove_set=glove_set["id"]):
                self.assertNotIn("tarn_razorlor", glove_set["encounters"])


class TestMiniquestMigration(unittest.TestCase):
    def test_v103_adds_the_two_rows_to_an_older_save(self):
        migrated = migrate_loaded_data(
            {
                "config_version": 101,
                "quests": {"cooks_assistant": {"started": True, "progress": 1, "completed": True}},
                "quest_points": 1,
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertGreaterEqual(CURRENT_CONFIG_VERSION, 103)
        self.assertTrue(migrated["quests"]["cooks_assistant"]["completed"])
        for quest_id in MINIQUEST_IDS:
            with self.subTest(quest_id=quest_id):
                self.assertEqual(
                    migrated["quests"][quest_id],
                    {"started": False, "progress": 0, "completed": False},
                )

    def test_a_newer_save_keeps_its_miniquest_progress(self):
        migrated = migrate_loaded_data(
            {
                "config_version": CURRENT_CONFIG_VERSION,
                "quests": {
                    HUNT_FOR_SUROK: {"started": True, "progress": 3, "completed": False},
                },
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )

        self.assertEqual(
            migrated["quests"][HUNT_FOR_SUROK],
            {"started": True, "progress": 3, "completed": False},
        )


if __name__ == "__main__":
    unittest.main()
