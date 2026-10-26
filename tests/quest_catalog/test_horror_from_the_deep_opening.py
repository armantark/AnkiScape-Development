"""The source-backed opening stops on arrival at the Barbarian Outpost."""

import copy
import json
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.data.combat.consumables import CONSUMABLE_DATA
from ankiscape.data.quest.stage_overrides.members.later.horror_from_the_deep import (
    HORROR_FROM_THE_DEEP_OPENING_ACTIONS,
)
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from ankiscape.logic_pure import quest_action_proofs
from ankiscape.logic_pure.logic_pure_consumables import apply_consumable_pure
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_progress_pure,
    quest_current_stage_blocker_reasons_pure,
    quest_journal_rows_pure,
    quest_locked_reasons_pure,
    start_quest_pure,
)
from ankiscape.logic_pure.quest.skill_requirements import (
    _quest_requirement_level, _skill_requirement_reason,
)


QUEST_ID = "horror_from_the_deep"
OPENING_ACTIONS = (
    "Accept Larrissa's request to find her missing boyfriend Jossik in the dark, locked lighthouse; she asks you to seek Gunnjorn's spare key and repair the eastern bridge.",
    "Travel south across the basalt platforms to the Barbarian Outpost.",
)
OPENED = {"started": True, "progress": 2, "completed": False}


def _player():
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player["current_quest"] = QUEST_ID
    player["quests"]["bar_crawl"] = {"started": True, "progress": QUEST_DATA["bar_crawl"]["stages"], "completed": True}
    player["agility_level"] = 35
    player["prayer_level"] = 1
    player["inventory"] = {"Coins": 37, "Logs": 2, "Jug of water": 1}
    player["quest_action_proofs"] = ["Unrelated deed"]
    return player


def _expected_opening(player):
    expected = copy.deepcopy(player)
    expected["quests"][QUEST_ID] = dict(OPENED)
    expected["quest_action_proofs"] = sorted(set(player["quest_action_proofs"]) | set(OPENING_ACTIONS))
    return expected


class HorrorFromTheDeepOpeningTest(unittest.TestCase):
    def test_prerequisite_gate_preserves_reasons_and_lifecycle(self):
        player = _player()
        player["agility_level"] = 34
        player["quest_points"] = 0
        player["inventory"]["Logs"] = 0
        player["quests"]["completed_guide"] = {"started": True, "progress": 1, "completed": True}
        quest = {
            "required_quests": (
                None, "ignored", 7, {}, {"quest_id": None}, {"quest_id": 3},
                {"quest_id": "missing_guide", "display_name": "Missing guide"},
                {"quest_id": "unmet_guide", "display_name": "Unmet guide"},
                {"quest_id": "unmet_guide", "display_name": "Unmet guide"},
                {"quest_id": "completed_guide", "display_name": "Completed guide"},
            ),
            "required_skills": ({"skill_id": "agility", "level": 35},),
            "required_quest_points": 2,
            "required_items": {"Logs": 2},
        }
        catalog = {
            "opening_gate_fixture": quest,
            "missing_guide": "unavailable",
            "unmet_guide": {"name": "Unmet guide"},
            "completed_guide": {"name": "Completed guide"},
        }
        before = copy.deepcopy(player)
        self.assertEqual(quest_locked_reasons_pure(player, "opening_gate_fixture", catalog), (
            "Missing guide (not implemented)", "Unmet guide", "Agility 35", "2 quest points", "Logs x2",
        ))
        self.assertEqual(player, before)

        for prerequisite, expected in (
            ({"quest_id": "missing_title"}, ("Missing Title (not implemented)",)),
            ({"quest_id": "unmet_guide"}, ("Unmet Guide",)),
        ):
            with self.subTest(prerequisite=prerequisite):
                fallback_catalog = {**catalog, "title_fixture": {"required_quests": (prerequisite,)}}
                self.assertEqual(quest_locked_reasons_pure(player, "title_fixture", fallback_catalog), expected)
                self.assertEqual(player, before)

        for prerequisites in ((), None):
            with self.subTest(prerequisites=prerequisites):
                empty_catalog = {"empty_fixture": {"required_quests": prerequisites}}
                self.assertEqual(quest_locked_reasons_pure(player, "empty_fixture", empty_catalog), ())
                self.assertEqual(player, before)

        self.assertEqual(quest_locked_reasons_pure(player, "unknown_fixture", catalog), ("unknown quest",))
        self.assertEqual(player, before)
        for state, expected in (
            ({"started": True, "progress": 1, "completed": True}, ("completed",)),
            ({"started": True, "progress": 0, "completed": False}, ()),
        ):
            with self.subTest(state=state):
                active = copy.deepcopy(player)
                active["quests"]["opening_gate_fixture"] = state
                active_before = copy.deepcopy(active)
                self.assertEqual(quest_locked_reasons_pure(active, "opening_gate_fixture", catalog), expected)
                self.assertEqual(active, active_before)
        self.assertEqual(player, before)

    def assert_entry_refused(self, player, reason):
        before = copy.deepcopy(player)
        journal = quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA)
        self.assertIn(reason, quest_locked_reasons_pure(player, QUEST_ID, QUEST_DATA))
        started, ok = start_quest_pure(player, QUEST_ID, QUEST_DATA)
        self.assertFalse(ok)
        self.assertEqual(started, before)
        progressed, ok, completed = apply_quest_progress_pure(player, QUEST_ID, QUEST_DATA)
        self.assertFalse(ok)
        self.assertFalse(completed)
        self.assertEqual(progressed, before)
        self.assertEqual(player, before)
        self.assertEqual(quest_journal_rows_pure(progressed, QUEST_ID, QUEST_DATA), journal)

    def test_opening_catalog_and_journal(self):
        quest = QUEST_DATA[QUEST_ID]
        generated = next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == QUEST_ID)
        stage = quest["stage_requirements"][0]
        for key in (
            "required_tools", "required_inventory", "required_inventory_options",
            "consumed_inventory", "consumed_inventory_options", "produced_inventory",
            "required_actions", "required_routes", "combat_encounters", "required_skills",
        ):
            self.assertFalse(stage[key], key)
        self.assertEqual(stage["auto_actions"], OPENING_ACTIONS)
        self.assertEqual(HORROR_FROM_THE_DEEP_OPENING_ACTIONS, OPENING_ACTIONS)
        self.assertEqual(quest["journal_stages"][1], OPENING_ACTIONS)
        self.assertEqual(
            {stage: lines for stage, lines in quest["journal_stages"].items() if stage >= 2},
            {row["stage"]: row["journal"] for row in generated["journal_stages"] if row["stage"] >= 2},
        )
        self.assertEqual(quest["stages"], 8)
        self.assertEqual(len(quest["journal_stages"]), 7)
        stage6 = next(row for row in quest["stage_requirements"] if row["stage"] == 6)
        self.assertEqual(stage6["required_inventory"], {"Air rune": 1, "Earth rune": 1, "Fire rune": 1, "Water rune": 1})
        self.assertNotIn("Sword", stage6["required_tools"])
        self.assertNotIn("Arrow", stage6["required_tools"])

    def test_existing_prerequisites_and_recommendation_are_preserved(self):
        quest = QUEST_DATA[QUEST_ID]
        self.assertEqual(quest["required_quests"], ({"quest_id": "bar_crawl", "display_name": "Alfred Grimhand's Barcrawl"},))
        self.assertEqual(quest["required_skills"], ({"skill_id": "agility", "display_name": "Agility", "level": 35},))
        self.assertEqual(quest["requirements"], ("Alfred Grimhand's Barcrawl", "Agility 35"))
        player = _player()
        self.assertNotIn("Hammer", player["inventory"])
        self.assertFalse(quest_locked_reasons_pure(player, QUEST_ID, QUEST_DATA))
        result, ok, completed = apply_quest_progress_pure(player, QUEST_ID, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed)
        self.assertEqual(result, _expected_opening(player))

    def test_start_alone_does_not_credit_opening(self):
        player = _player()
        player["inventory"]["Lighthouse key"] = 1
        before = copy.deepcopy(player)
        started, ok = start_quest_pure(player, QUEST_ID, QUEST_DATA)
        self.assertTrue(ok)
        expected = copy.deepcopy(before)
        expected["quests"][QUEST_ID] = {"started": True, "progress": 0, "completed": False}
        self.assertEqual(started, expected)
        self.assertEqual(player, before)
        self.assertEqual(quest_journal_rows_pure(started, QUEST_ID, QUEST_DATA), (
            {"stage": 1, "lines": OPENING_ACTIONS, "completed": False, "current": True},
        ))
        self.assertEqual(started, expected)

    def test_success_has_exact_opening_delta(self):
        player = _player()
        before = copy.deepcopy(player)
        result, ok, completed = apply_quest_progress_pure(player, QUEST_ID, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed)
        self.assertEqual(result, _expected_opening(before))
        self.assertEqual(player, before)

    def test_entry_refusals_preserve_complete_state(self):
        incomplete = _player()
        incomplete["quests"]["bar_crawl"] = {"started": True, "progress": 3, "completed": False}
        missing = _player()
        del missing["quests"]["bar_crawl"]
        low = _player()
        low["agility_level"] = 34
        for player, reason in ((incomplete, "Alfred Grimhand's Barcrawl"), (missing, "Alfred Grimhand's Barcrawl"), (low, "Agility 35")):
            with self.subTest(reason=reason, state=player["quests"].get("bar_crawl")):
                player["agility_exp"] = 1234
                player["quest_points"] = 9
                player["pending_skill_exp_rewards"] = {"cooking": 73}
                player["quests"]["monks_friend"] = {"started": True, "progress": 3, "completed": False}
                player["combat_lifepoints"] = 47
                player["combat_status_effects"] = {"poison": 2}
                self.assert_entry_refused(player, reason)

    def test_agility_boost_boundary_uses_real_consumable_state(self):
        player = _player()
        player["agility_level"] = 34
        self.assert_entry_refused(player, "Agility 35")
        player["inventory"]["Agility potion (4)"] = 1
        boosted, consumed = apply_consumable_pure(player, "Agility potion (4)")
        self.assertTrue(consumed["allowed"])
        spec = CONSUMABLE_DATA["Agility potion (4)"]
        self.assertEqual(boosted["agility_effective_boost"], spec["boost"])
        self.assertEqual(boosted["agility_boost_actions_remaining"], spec["action_budget"])
        self.assertEqual(boosted["inventory"], {**_player()["inventory"], spec["leaves"]: 1})
        result, ok, completed = apply_quest_progress_pure(boosted, QUEST_ID, QUEST_DATA)
        self.assertTrue(ok)
        self.assertFalse(completed)
        self.assertEqual(result, _expected_opening(boosted))
        expired = copy.deepcopy(boosted)
        expired["agility_boost_actions_remaining"] = 0
        self.assert_entry_refused(expired, "Agility 35")
        too_low = copy.deepcopy(player)
        too_low["agility_level"] = 31
        too_low, consumed = apply_consumable_pure(too_low, "Agility potion (4)")
        self.assertTrue(consumed["allowed"])
        self.assert_entry_refused(too_low, "Agility 35")
        self.assertTrue(start_quest_pure(_player(), QUEST_ID, QUEST_DATA)[1])
        self.assert_base_gate_scope(boosted)

    def assert_base_gate_scope(self, boosted):
        requirement = {"skill_id": "agility", "display_name": "Agility", "level": 35}
        self.assertIsNone(_skill_requirement_reason(boosted, requirement, quest_id=QUEST_ID))
        self.assertEqual(_skill_requirement_reason(boosted, requirement), "Agility 35")
        self.assertEqual(_quest_requirement_level(boosted, "agility", "agility_level", QUEST_ID), 37)
        self.assertEqual(_quest_requirement_level(boosted, "agility", "agility_level", ""), 34)
        capped = {**boosted, "agility_effective_boost": 100}
        self.assertEqual(_quest_requirement_level(capped, "agility", "agility_level", QUEST_ID), 54)
        other = "one_small_favour"
        player = copy.deepcopy(boosted)
        for row in QUEST_DATA[other]["required_quests"]:
            player["quests"][row["quest_id"]] = {"started": True, "progress": 99, "completed": True}
        for row in QUEST_DATA[other]["required_skills"]:
            player[row["skill_id"] + "_level"] = row["level"]
        player["agility_level"] = 35
        self.assertIn("Agility 36", quest_locked_reasons_pure(player, other, QUEST_DATA))
        self.assertFalse(start_quest_pure(player, other, QUEST_DATA)[1])
        player = copy.deepcopy(boosted)
        player["quests"][QUEST_ID] = {"started": True, "progress": 1, "completed": False}
        catalog = copy.deepcopy(QUEST_DATA)
        catalog[QUEST_ID]["stage_requirements"][0]["required_skills"] = (requirement,)
        self.assertIn("Agility 35", " ".join(quest_current_stage_blocker_reasons_pure(player, QUEST_ID, catalog)))
        result, ok, completed = apply_quest_progress_pure(player, QUEST_ID, catalog)
        self.assertEqual(result, player)
        self.assertFalse(ok)
        self.assertFalse(completed)

    def test_next_stage_and_completed_refusals_do_not_replay_opening(self):
        opened, ok, _ = apply_quest_progress_pure(_player(), QUEST_ID, QUEST_DATA)
        self.assertTrue(ok)
        self.assertIn("Complete Horror from the Deep stage 2 objective", QUEST_DATA[QUEST_ID]["stage_requirements"][1]["required_actions"])
        self.assertTrue(quest_current_stage_blocker_reasons_pure(opened, QUEST_ID, QUEST_DATA))
        completed = copy.deepcopy(opened)
        completed["quests"][QUEST_ID] = {"started": True, "progress": 8, "completed": True}
        legacy_completed = copy.deepcopy(completed)
        legacy_completed["quests"][QUEST_ID]["progress"] = 7
        for player in (opened, completed, legacy_completed):
            before = copy.deepcopy(player)
            journal = quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA)
            with patch.object(quest_action_proofs, "quest_action_proofs_after_event_pure", wraps=quest_action_proofs.quest_action_proofs_after_event_pure) as events:
                result, ok, completed_now = apply_quest_progress_pure(player, QUEST_ID, QUEST_DATA)
            self.assertFalse(ok)
            self.assertFalse(completed_now)
            self.assertEqual(result, before)
            self.assertEqual(player, before)
            self.assertEqual(quest_journal_rows_pure(result, QUEST_ID, QUEST_DATA), journal)
            events.assert_not_called()

    def test_saved_progress_has_no_historical_proof_backfill(self):
        for progress, completed_save in ((0, False), (1, False), (2, False), (5, False), (7, False), (7, True), (8, True)):
            with self.subTest(progress=progress, completed=completed_save):
                player = _player()
                state = {"started": progress > 0, "progress": progress, "completed": completed_save}
                player["quests"][QUEST_ID] = dict(state)
                player["inventory"]["Lighthouse key"] = 1
                player["quest_stage_actions"] = {QUEST_ID: list(OPENING_ACTIONS)}
                player["action_telemetry"]["actions"][f"quest:{QUEST_ID}"] = {"successes": 3}
                saved = json.loads(json.dumps(player))
                migrated = migrate_loaded_data(saved, ORE_DATA, ITEM_DEFINITIONS)
                self.assertEqual(migrated["quests"][QUEST_ID], state)
                self.assertEqual(migrated["quest_action_proofs"], player["quest_action_proofs"])
                repeated = migrate_loaded_data(json.loads(json.dumps(migrated)), ORE_DATA, ITEM_DEFINITIONS)
                self.assertEqual(repeated, migrated)
                reviewed, ok, completed = apply_quest_progress_pure(migrated, QUEST_ID, QUEST_DATA)
                self.assertFalse(completed)
                if progress <= 1:
                    self.assertTrue(ok)
                    self.assertEqual(reviewed, _expected_opening(migrated))
                else:
                    self.assertFalse(ok)
                    self.assertEqual(reviewed, migrated)
