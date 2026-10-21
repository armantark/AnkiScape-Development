"""Cold War assigns a personal greeting without adding a player action."""

import copy
import json
import random
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.data.cold_war_greeting_data import COLD_WAR_GREETING_EMOTES, COLD_WAR_GREETING_LENGTH
from ankiscape.logic.cold_war_greeting_logic import (
    cold_war_journal_lines_pure,
    ensure_cold_war_greeting_pure,
    sanitize_cold_war_greeting_pure,
)
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_progress_pure,
    quest_current_stage_blockers_pure,
    quest_journal_rows_pure,
    start_quest_pure,
)


# Concrete sequences throughout this suite are deterministic test fixtures.
GREETING = ["Wave", "Twirl", "Bow"]
GREETING_LINE = "Penguin greeting: Wave → Twirl → Bow (automatic)."
SAMPLER = "ankiscape.logic.cold_war_greeting_logic.random.sample"


def eligible_player():
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    for row in QUEST_DATA["cold_war"]["required_skills"]:
        player[row["skill_id"] + "_level"] = row["level"]
    player["inventory"] = {"Coins": 37, "Logs": 2}
    return player


def migrate(player):
    return migrate_loaded_data(copy.deepcopy(player), ORE_DATA, ITEM_DEFINITIONS)


def without_greeting_line(rows):
    return tuple(
        {**row, "lines": tuple(line for line in row["lines"] if line != GREETING_LINE)}
        for row in rows
    )


class ColdWarGreetingTest(unittest.TestCase):
    def setUp(self):
        self.addCleanup(random.setstate, random.getstate())

    def test_catalog_matches_period_names(self):
        self.assertEqual(COLD_WAR_GREETING_EMOTES, (
            "Shiver", "Twirl", "Clap", "Bow", "Cheer", "Wave", "Preen", "Flap",
        ))
        self.assertIsInstance(COLD_WAR_GREETING_EMOTES, tuple)
        self.assertEqual(COLD_WAR_GREETING_LENGTH, 3)

    def test_sanitizer_preserves_order_and_rejects_invalid_values(self):
        for raw in (list(GREETING), tuple(GREETING)):
            with self.subTest(raw=raw):
                result = sanitize_cold_war_greeting_pure(raw)
                self.assertEqual(result, GREETING)
                self.assertIsInstance(result, list)
                self.assertIsNot(result, raw)
                result.reverse()
                self.assertEqual(list(raw), GREETING)
        for raw in (None, 3, True, "Wave", {"Wave": 1, "Twirl": 1, "Bow": 1},
                    set(GREETING), iter(GREETING), [], GREETING[:2], GREETING + ["Clap"],
                    ["Wave", "Twirl", "Wave"], ["Wave", "Spin", "Bow"],
                    ["wave", "Twirl", "Bow"], ["Wave", 1, "Bow"],
                    ["Wave", ["Twirl"], "Bow"]):
            with self.subTest(raw=raw):
                self.assertEqual(sanitize_cold_war_greeting_pure(raw), [])

    def test_start_assigns_three_distinct_moves_without_other_rewards(self):
        player = eligible_player()
        before = copy.deepcopy(player)
        with patch(SAMPLER, return_value=list(GREETING)) as sample:
            result, ok = start_quest_pure(player, "cold_war", QUEST_DATA)
        self.assertTrue(ok)
        sample.assert_called_once_with(COLD_WAR_GREETING_EMOTES, 3)
        self.assertEqual(result["cold_war_greeting"], GREETING)
        self.assertEqual(len(set(result["cold_war_greeting"])), 3)
        self.assertEqual(player, before)
        expected = copy.deepcopy(before)
        expected["quests"]["cold_war"] = {"started": True, "progress": 0, "completed": False}
        expected["current_quest"] = "cold_war"
        expected["cold_war_greeting"] = GREETING
        self.assertEqual(result, expected)

        # A successful review-driven start also assigns at the transaction.
        for row in QUEST_DATA["cold_war"]["stage_requirements"]:
            if row["stage"] == 1:
                player["inventory"].update(row["required_inventory"])
                player["toolbelt"].update(row["required_tools"])
                player["quest_action_proofs"] = list(row["required_actions"])
        with patch(SAMPLER, return_value=list(GREETING)) as sample:
            result, ok, completed = apply_quest_progress_pure(player, "cold_war", QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed)
        sample.assert_called_once_with(COLD_WAR_GREETING_EMOTES, 3)
        self.assertEqual(result["cold_war_greeting"], GREETING)
        self.assertEqual(result["quests"]["cold_war"]["progress"], 2)

    def test_reselection_preserves_greeting_without_random_draw(self):
        with patch(SAMPLER, return_value=list(GREETING)):
            player, _ = start_quest_pure(eligible_player(), "cold_war", QUEST_DATA)
        before = copy.deepcopy(player)
        with patch(SAMPLER) as sample:
            for _ in range(3):
                result, ok = start_quest_pure(player, "cold_war", QUEST_DATA)
                self.assertTrue(ok)
                self.assertEqual(result, before)
                self.assertIsNot(result["cold_war_greeting"], player["cold_war_greeting"])
                player = result
        sample.assert_not_called()

    def test_refused_start_and_progress_do_not_assign_or_draw(self):
        missing_skill = eligible_player()
        missing_skill["agility_level"] = 1
        for player, operation in ((missing_skill, start_quest_pure),
                                  (missing_skill, apply_quest_progress_pure),
                                  (eligible_player(), apply_quest_progress_pure)):
            # Keep the real opening blocked by one missing Oak plank.
            if player is not missing_skill:
                row = QUEST_DATA["cold_war"]["stage_requirements"][0]
                player["inventory"].update(row["required_inventory"])
                player["toolbelt"].update(row["required_tools"])
                player["inventory"]["Oak plank"] = 9
                preview = copy.deepcopy(player)
                preview["quests"]["cold_war"]["started"] = True
                blockers = quest_current_stage_blockers_pure(preview, "cold_war", QUEST_DATA)
                self.assertEqual([row["item_name"] for row in blockers], ["Oak plank"])
            for started in (False, True) if player is not missing_skill else (False,):
                player["quests"]["cold_war"]["started"] = started
                before, random_before = copy.deepcopy(player), random.getstate()
                with self.subTest(operation=operation.__name__, started=started), patch(SAMPLER) as sample:
                    result = operation(player, "cold_war", QUEST_DATA)
                    self.assertIs(result[0], player)
                    self.assertFalse(result[1])
                    sample.assert_not_called()
                    self.assertEqual(player, before)
                    self.assertEqual(random.getstate(), random_before)

    def assert_journal_preserves_rows_and_state(self, player, quest_id, expected_count):
        before, random_before = copy.deepcopy(player), random.getstate()
        with patch("ankiscape.logic_pure.logic_pure_quest.cold_war_journal_lines_pure",
                   side_effect=lambda _p, _q, _s, lines: tuple(lines)):
            old_rows = quest_journal_rows_pure(player, quest_id, QUEST_DATA)
        with patch(SAMPLER) as sample:
            for _ in range(2):
                rows = quest_journal_rows_pure(player, quest_id, QUEST_DATA)
                self.assertEqual(sum(row["lines"].count(GREETING_LINE) for row in rows), expected_count)
                self.assertEqual(without_greeting_line(rows), old_rows)
                if expected_count:
                    self.assertEqual(rows[0]["stage"], 1)
                    self.assertEqual(rows[0]["lines"][-1], GREETING_LINE)
            sample.assert_not_called()
        self.assertEqual(player, before)
        self.assertEqual(random.getstate(), random_before)

    def test_journal_adds_exactly_one_read_only_line(self):
        for started, completed, progress, greeting, quest_id, expected_count in (
            (False, False, 0, GREETING, "cold_war", 0),
            (True, False, 0, GREETING, "cold_war", 1),
            (True, False, 4, GREETING, "cold_war", 1),
            (False, True, 7, GREETING, "cold_war", 1),
            (True, False, 2, ["Wave"] * 3, "cold_war", 0),
            (True, False, 2, None, "cold_war", 0),
            (True, False, 2, GREETING, "rune_mysteries", 0),
        ):
            with self.subTest(started=started, completed=completed, progress=progress, greeting=greeting, quest=quest_id):
                player = eligible_player()
                player["quests"][quest_id] = dict(started=started, completed=completed, progress=progress)
                player["cold_war_greeting"] = copy.deepcopy(greeting)
                self.assert_journal_preserves_rows_and_state(player, quest_id, expected_count)
        self.assertEqual(cold_war_journal_lines_pure(player, "cold_war", 2, ["existing"]), ("existing",))

    def test_storage_defaults_and_migration(self):
        with patch(SAMPLER) as sample:
            player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
            self.assertEqual(player["cold_war_greeting"], [])
            for raw in (None, GREETING, ["Wave"] * 3):
                player["cold_war_greeting"] = raw
                self.assertEqual(ensure_cold_war_greeting_pure(player), [])
                self.assertEqual(migrate(player)["cold_war_greeting"], [])
            sample.assert_not_called()
        for completed in (False, True):
            legacy = eligible_player()
            legacy.pop("cold_war_greeting")
            legacy["quests"]["cold_war"] = dict(started=not completed, completed=completed, progress=3)
            for raw in (None, [], ["Wave"] * 3, "Wave", ["Wave", "Spin", "Bow"]):
                with self.subTest(completed=completed, raw=raw):
                    old = copy.deepcopy(legacy)
                    if raw is not None:
                        old["cold_war_greeting"] = raw
                    with patch(SAMPLER, return_value=list(GREETING)) as sample:
                        result = migrate(old)
                        sample.assert_called_once_with(COLD_WAR_GREETING_EMOTES, 3)
                        self.assertEqual(result["cold_war_greeting"], GREETING)
                        again = migrate(json.loads(json.dumps(result)))
                        self.assertEqual(again, result)
                        sample.assert_called_once()
                    # Compare with the same legacy migration carrying a valid
                    # assignment: only existing migrations may change other fields.
                    with patch(SAMPLER) as sample:
                        control = migrate({**old, "cold_war_greeting": list(GREETING)})
                        sample.assert_not_called()
                    self.assertEqual(result, control)
            for valid in (list(GREETING), tuple(GREETING)):
                legacy["cold_war_greeting"] = valid
                with patch(SAMPLER) as sample:
                    result = migrate(legacy)
                    self.assertEqual(result["cold_war_greeting"], GREETING)
                    self.assertIsNot(result["cold_war_greeting"], valid)
                    self.assertEqual(migrate(json.loads(json.dumps(result))), result)
                    sample.assert_not_called()

    def test_greeting_never_changes_stage_blockers(self):
        player = eligible_player()
        player["quests"]["cold_war"]["started"] = True
        for stage in range(1, QUEST_DATA["cold_war"]["stages"] + 1):
            with self.subTest(stage=stage):
                player["quests"]["cold_war"]["progress"] = stage
                player.pop("cold_war_greeting", None)
                before = quest_current_stage_blockers_pure(player, "cold_war", QUEST_DATA)
                for greeting in (GREETING, ["Clap", "Shiver", "Flap"]):
                    player["cold_war_greeting"] = list(greeting)
                    self.assertEqual(quest_current_stage_blockers_pure(player, "cold_war", QUEST_DATA), before)
                if stage == 2:
                    self.assertEqual(before, ())


if __name__ == "__main__":
    unittest.main()
