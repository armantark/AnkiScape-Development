"""Only earned opening deeds receive a completed Animal Magnetism journal."""

import copy
import json
import unittest
from dataclasses import replace
from unittest import mock

import pkg_alias  # noqa: F401
from ankiscape.core.constants import QUEST_DATA
from ankiscape.data.quest.catalog import _quest_from_catalog, _quest_with_stage_requirements
from ankiscape.data.quest.catalog_overrides import QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID
from ankiscape.data.quest.contract import QuestStageRequirementCleanup
from ankiscape.data.quest.ledger import QUESTS_BY_ID
from ankiscape.data.quest.stage_cleanups import QUEST_STAGE_REQUIREMENT_CLEANUPS_BY_ID
from ankiscape.data.quest.stage_overrides.members.later.animal_magnetism import (
    ANIMAL_MAGNETISM_CLEANUPS, COMPLETED_OPENING, OPENING_ACTIONS, PENDING_OPENING, SOURCES,
)
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from ankiscape.logic_pure.logic_pure_quest import quest_journal_rows_pure, start_quest_pure
from ankiscape.logic_pure.logic_pure_state import _positive_int, quest_state_pure
from ankiscape.logic_pure.quest.another_cook import another_cook_journal_row_pure
from ankiscape.logic_pure.quest.elder_kiln_journal import elder_kiln_journal_row_pure
from ankiscape.logic_pure.quest.elemental_workshop import opening_journal_rows_pure
from ankiscape.logic_pure.quest.enakhra import enakhra_opening_journal_row_pure
from ankiscape.logic_pure.quest.grand_tree import grand_tree_journal_rows_pure
from ankiscape.logic_pure.quest.toktz_opening import toktz_opening_journal_row_pure
from ankiscape.logic_pure.quest.hazeel_journal import hazeel_journal_row_pure
from ankiscape.logic_pure.quest.review_services import quest_review_journal_row_pure
from ankiscape.logic_pure.quest.witchs_house import witchs_house_journal_rows_pure
from tests.runtime_actions.quests.animal_magnetism_helpers import (
    OLD_SENTINEL, QUEST_ID, SKILL_GATES, eligible_player, review,
)
from tests.runtime_actions.test_cold_war_greeting import (
    PLAYER_KEY, GREETING, GREETING_LINE, eligible_player as cold_war_player, review_session,
)

STAGE_TWO = (
    "With a Ghostspeak amulet equipped, head to the farm West of the Ectofuntus.",
    "Talk to Alice.",
)


def previous_projection(player_data, quest_id, quest_data):
    """Main's projection before adding Animal Magnetism's opening evidence."""
    quest = quest_data.get(quest_id)
    if not quest:
        return tuple()
    state = quest_state_pure(player_data, quest_id)
    progress = state["progress"]
    if state["started"] and progress <= 0:
        progress = 1
    if state["completed"]:
        progress = _positive_int(quest.get("stages", progress), progress)
    journal_stages = quest.get("journal_stages", {}) or {}
    rows = tuple(
        enakhra_opening_journal_row_pure(player_data, quest_id,
            elder_kiln_journal_row_pure(player_data, quest_id,
                toktz_opening_journal_row_pure(player_data, quest_id,
                    hazeel_journal_row_pure(player_data, quest_id,
                        quest_review_journal_row_pure(player_data, quest_id,
                            another_cook_journal_row_pure(player_data, quest_id, dict(stage=stage,
             lines=journal_stages.get(stage, ()),
             completed=state["completed"] or stage < progress,
             current=not state["completed"] and stage == progress)))))))
        for stage in sorted(journal_stages) if stage <= progress
    )
    rows = opening_journal_rows_pure(player_data, quest_id, rows)
    rows = grand_tree_journal_rows_pure(player_data, quest_id, rows)
    return witchs_house_journal_rows_pure(player_data, quest_id, rows)


class AnimalMagnetismOpeningCatalogTest(unittest.TestCase):
    def test_authored_composition_changes_only_opening_and_overlap(self):
        generated = next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == QUEST_ID)
        generated_before = copy.deepcopy(generated)
        old_cleanups = {key: value for key, value in QUEST_STAGE_REQUIREMENT_CLEANUPS_BY_ID.items() if key != QUEST_ID}
        old_journals = {key: value for key, value in QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID.items() if key != QUEST_ID}
        with mock.patch.dict(QUEST_STAGE_REQUIREMENT_CLEANUPS_BY_ID, old_cleanups, clear=True), mock.patch.dict(
            QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID, old_journals, clear=True,
        ):
            baseline = _quest_with_stage_requirements(_quest_from_catalog(generated), generated)
        actual = QUESTS_BY_ID[QUEST_ID]
        self.assertEqual(replace(actual, journal_stages=baseline.journal_stages,
                                 stage_requirements=baseline.stage_requirements), baseline)
        self.assertEqual(actual.stage_requirements[1:], baseline.stage_requirements[1:])
        first = baseline.stage_requirements[0]
        expected = replace(first, required_actions=tuple(action for action in first.required_actions if action != OLD_SENTINEL),
                           auto_actions=first.auto_actions + OPENING_ACTIONS, source="; ".join(SOURCES))
        self.assertEqual(actual.stage_requirements[0], expected)
        self.assertEqual(ANIMAL_MAGNETISM_CLEANUPS, (QuestStageRequirementCleanup(
            stage=1, remove_required_actions=(OLD_SENTINEL,), add_auto_actions=OPENING_ACTIONS, source="; ".join(SOURCES),
        ),))
        self.assertEqual(actual.journal_stages[0].journal, (PENDING_OPENING,))
        self.assertEqual(actual.journal_stages[1].journal, STAGE_TWO)
        self.assertEqual(actual.journal_stages[2:], baseline.journal_stages[2:])
        self.assertEqual(QUEST_DATA[QUEST_ID]["required_quests"], generated["required_quests"])
        self.assertEqual(QUEST_DATA[QUEST_ID]["required_skills"], generated["required_skills"])
        self.assertEqual(tuple((r["skill_id"], r["level"]) for r in generated["required_skills"]), SKILL_GATES)
        self.assertEqual(tuple(r["quest_id"] for r in generated["required_quests"]), ("the_restless_ghost", "ernest_the_chicken"))
        self.assertEqual((generated["stages"], actual.stages, QUEST_DATA[QUEST_ID]["stages"]), (6, 7, 7))
        self.assertEqual(generated, generated_before)

    def assert_read_only_rows(self, player, expected):
        before = copy.deepcopy(player)
        catalog = copy.deepcopy(QUEST_DATA)
        for _ in range(3):
            self.assertEqual(quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA), expected)
            self.assertEqual(player, before)
            self.assertEqual(QUEST_DATA, catalog)

    def test_pending_and_earned_journal_are_truthful_and_read_only(self):
        player = eligible_player()
        self.assert_read_only_rows(player, ())
        selected, ok = start_quest_pure(player, QUEST_ID, QUEST_DATA)
        self.assertTrue(ok)
        pending = (dict(stage=1, lines=(PENDING_OPENING,), completed=False, current=True),)
        self.assert_read_only_rows(selected, pending)
        selected["quests"][QUEST_ID]["progress"] = 1
        self.assert_read_only_rows(selected, pending)
        self.assertTrue(review(selected))
        earned = (
            dict(stage=1, lines=(COMPLETED_OPENING,), completed=True, current=False),
            dict(stage=2, lines=STAGE_TWO, completed=False, current=True),
        )
        self.assert_read_only_rows(selected, earned)
        self.assertEqual(earned[1]["lines"][-1], "Talk to Alice.")
        self.assertFalse(earned[1]["completed"])

    def assert_legacy_roundtrip(self, addon, collection, base, progress, completed, opening_proofs):
        player = copy.deepcopy(base)
        player["quests"][QUEST_ID] = dict(started=True, progress=progress, completed=completed)
        player["quest_action_proofs"] = sorted(set(player["quest_action_proofs"]) | set(opening_proofs))
        addon._state.player_data = player
        addon.save_player_data()
        addon.load_player_data()
        before = copy.deepcopy(addon._state.player_data)
        saved = copy.deepcopy(collection._store)
        old_rows = previous_projection(before, QUEST_ID, QUEST_DATA)
        if progress <= 1:
            expected = (dict(stage=1, lines=(PENDING_OPENING,), completed=False, current=True),)
        elif len(opening_proofs) == 2:
            expected = (dict(stage=1, lines=(COMPLETED_OPENING,), completed=True, current=False), *old_rows[1:])
        else:
            expected = old_rows[1:]
        self.assert_read_only_rows(addon._state.player_data, expected)
        addon.save_player_data()
        self.assertEqual(collection._store, saved)
        addon.load_player_data()
        self.assertEqual(addon._state.player_data, before)
        self.assertEqual(before["quests"][QUEST_ID], player["quests"][QUEST_ID])
        self.assertEqual(before["quest_action_proofs"], player["quest_action_proofs"])

    def test_existing_save_progress_is_preserved_without_backfill(self):
        # Obtain the positive control from a genuine opening; partial proofs
        # model old or incomplete saves and never stand in for performance.
        base = eligible_player()
        performed = copy.deepcopy(base)
        self.assertTrue(review(performed))
        earned = tuple(action for action in OPENING_ACTIONS if action in performed["quest_action_proofs"])
        self.assertEqual(earned, OPENING_ACTIONS)
        with review_session() as (addon, collection, _errors):
            collection.set_config = lambda key, value: collection._store.__setitem__(key, json.loads(json.dumps(value)))
            addon._state.player_data = base
            addon.save_player_data()
            addon.load_player_data()
            base = copy.deepcopy(addon._state.player_data)
            for progress in range(8):
                for evidence in ((), earned[:1], earned[1:], earned):
                    with self.subTest(progress=progress, evidence=evidence):
                        self.assert_legacy_roundtrip(addon, collection, base, progress, progress == 7, evidence)

    def assert_other_projection(self, player, quest_id):
        before = copy.deepcopy(player)
        for progress in (0, 1, 2, QUEST_DATA[quest_id]["stages"]):
            for completed in (False, True):
                player["quests"][quest_id] = dict(started=True, progress=progress, completed=completed)
                current = copy.deepcopy(player)
                self.assertEqual(quest_journal_rows_pure(player, quest_id, QUEST_DATA), previous_projection(player, quest_id, QUEST_DATA))
                self.assertEqual(player, current)
        player.clear()
        player.update(before)

    def test_other_quests_and_cold_war_projection_are_unchanged(self):
        player = eligible_player()
        catalog = copy.deepcopy(QUEST_DATA)
        for quest_id in QUEST_DATA:
            if quest_id != QUEST_ID:
                self.assert_other_projection(player, quest_id)
        cold = cold_war_player()
        cold["cold_war_greeting"] = GREETING
        cold["quests"]["cold_war"] = dict(started=True, progress=1, completed=False)
        self.assert_other_projection(cold, "cold_war")
        lines = [line for row in quest_journal_rows_pure(cold, "cold_war", QUEST_DATA) for line in row["lines"]]
        self.assertEqual(lines.count(GREETING_LINE), 1)
        self.assertEqual(quest_journal_rows_pure(player, "unknown", QUEST_DATA), ())
        self.assertEqual(QUEST_DATA, catalog)
