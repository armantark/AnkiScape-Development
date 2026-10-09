"""Explicit encounter dependencies preserve independent partially sourced fights."""

import copy
import json
import unittest
from dataclasses import replace
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import QUEST_DATA
from ankiscape.data.quest import catalog, serializers
from ankiscape.data.quest.combat_relocation import relocate_combat_encounters
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from ankiscape.logic_pure import logic_pure_quest as quest_logic
from tests.runtime_actions.test_blood_pact_opening import _player


QUEST_ID = "the_blood_pact"
KAYLE = "the_blood_pact_kayle_3"
CAITLIN = "the_blood_pact_caitlin_3"
REESE = "the_blood_pact_reese_3"


def _combat_player():
    player = _player()
    player["quests"][QUEST_ID] = {"started": True, "progress": 2, "completed": False}
    return player


def _encounters(quest):
    return {
        encounter["encounter_id"]: encounter
        for row in quest["stage_requirements"]
        for encounter in row["combat_encounters"]
    }


class QuestEncounterPrerequisitesTest(unittest.TestCase):
    def assert_refused_unchanged(self, player, quest_data, encounter_id, reason):
        before = copy.deepcopy(player)
        with patch.object(
            quest_logic, "apply_combat_burst_pure", wraps=quest_logic.apply_combat_burst_pure,
        ) as combat:
            result, ok, details = quest_logic.apply_quest_combat_encounter_pure(
                player, QUEST_ID, quest_data, encounter_id, ticks=1,
            )
        self.assertFalse(ok)
        self.assertEqual(details["reason"], reason)
        self.assertIs(result, player)
        self.assertEqual(player, before)
        combat.assert_not_called()

    def test_source_override_only_adds_the_explicit_dependencies(self):
        generated = next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == QUEST_ID)
        expected = {
            encounter.encounter_id: serializers._combat_encounter_dict(encounter)
            for row in generated["stage_requirements"]
            for encounter in catalog._catalog_combat_encounters(row["combat_encounters"])
        }
        self.assertEqual(expected[CAITLIN]["required_encounters"], ())
        expected[CAITLIN]["required_encounters"] = (KAYLE,)
        expected[REESE]["required_encounters"] = (CAITLIN,)
        self.assertEqual(_encounters(QUEST_DATA[QUEST_ID]), expected)
        self.assertFalse(expected[KAYLE]["npc_stats"])
        self.assertFalse(expected[REESE]["npc_stats"])

    def test_catalog_json_round_trip_preserves_encounter_dependencies(self):
        encounter = _encounters(QUEST_DATA[QUEST_ID])[CAITLIN]
        raw = json.loads(json.dumps(encounter))
        parsed = catalog._catalog_combat_encounters((raw,))[0]
        self.assertEqual(parsed.required_encounters, (KAYLE,))
        self.assertEqual(json.loads(json.dumps(serializers._combat_encounter_dict(parsed))), raw)

    def test_source_binding_rejects_a_missing_prerequisite_encounter(self):
        generated = next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == QUEST_ID)
        requirements = catalog._catalog_stage_requirements(generated["stage_requirements"])
        missing_kayle = tuple(
            replace(row, combat_encounters=tuple(
                encounter for encounter in row.combat_encounters if encounter.encounter_id != KAYLE
            ))
            for row in requirements
        )
        with self.assertRaisesRegex(ValueError, "The Blood Pact combat encounter catalog changed"):
            relocate_combat_encounters(QUEST_ID, missing_kayle)

    def test_partial_prerequisite_quantity_blocks_selection_and_explicit_call(self):
        quest_data = {QUEST_ID: copy.deepcopy(QUEST_DATA[QUEST_ID])}
        _encounters(quest_data[QUEST_ID])[KAYLE]["quantity"] = 2
        for count in (0, 1):
            with self.subTest(completed_quantity=count):
                player = _combat_player()
                player["quest_combat_encounter_counts"] = {QUEST_ID: {KAYLE: count}}
                self.assertEqual(
                    quest_logic.quest_current_stage_resolvable_combat_blockers_pure(player, QUEST_ID, quest_data), (),
                )
                self.assert_refused_unchanged(player, quest_data, CAITLIN, "combat_prerequisites_unmet")

    def test_complete_quantity_and_legacy_flags_admit_the_real_caitlin_fight(self):
        quest_data = {QUEST_ID: copy.deepcopy(QUEST_DATA[QUEST_ID])}
        _encounters(quest_data[QUEST_ID])[KAYLE]["quantity"] = 2
        states = (
            {"quest_combat_encounter_counts": {QUEST_ID: {KAYLE: 2}}},
            {"quest_combat_encounter_counts": {QUEST_ID: {KAYLE: 99}}},
            {"quest_combat_encounters": {QUEST_ID: [KAYLE]}},
            {"quest_combat_encounters": {QUEST_ID: KAYLE}},
            {"quest_combat_encounters": {QUEST_ID: {KAYLE: True}}},
            {"quest_combat_encounters": [KAYLE]},
        )
        for state in states:
            with self.subTest(state=state):
                player = _combat_player()
                player.update(state)
                self.assertEqual(
                    tuple(row["encounter_id"] for row in quest_logic.quest_current_stage_resolvable_combat_blockers_pure(
                        player, QUEST_ID, quest_data,
                    )), (CAITLIN,),
                )
                with patch.object(
                    quest_logic, "apply_combat_burst_pure", wraps=quest_logic.apply_combat_burst_pure,
                ) as combat:
                    _, ok, details = quest_logic.apply_quest_combat_encounter_pure(
                        player, QUEST_ID, quest_data, CAITLIN, ticks=1,
                    )
                self.assertTrue(ok)
                self.assertEqual(details["encounter_id"], CAITLIN)
                combat.assert_called_once()

    def test_prerequisite_from_an_earlier_stage_uses_its_complete_quantity(self):
        quest_data = {QUEST_ID: copy.deepcopy(QUEST_DATA[QUEST_ID])}
        rows = quest_data[QUEST_ID]["stage_requirements"]
        kayle = _encounters(quest_data[QUEST_ID])[KAYLE]
        kayle["quantity"] = 2
        for row in rows:
            row["combat_encounters"] = tuple(e for e in row["combat_encounters"] if e["encounter_id"] != KAYLE)
        rows[0]["combat_encounters"] = (kayle,)
        player = _combat_player()
        player["quest_combat_encounter_counts"] = {QUEST_ID: {KAYLE: 1}}
        self.assert_refused_unchanged(player, quest_data, CAITLIN, "combat_prerequisites_unmet")
        player["quest_combat_encounter_counts"][QUEST_ID][KAYLE] = 2
        self.assertEqual(
            tuple(row["encounter_id"] for row in quest_logic.quest_current_stage_resolvable_combat_blockers_pure(
                player, QUEST_ID, quest_data,
            )), (CAITLIN,),
        )

    def test_unknown_prerequisite_refuses_even_a_legacy_completion_flag(self):
        quest_data = {QUEST_ID: copy.deepcopy(QUEST_DATA[QUEST_ID])}
        _encounters(quest_data[QUEST_ID])[CAITLIN]["required_encounters"] = ("unknown_encounter",)
        player = _combat_player()
        player["quest_combat_encounters"] = {QUEST_ID: ["unknown_encounter"]}
        self.assertEqual(
            quest_logic.quest_current_stage_resolvable_combat_blockers_pure(player, QUEST_ID, quest_data), (),
        )
        self.assert_refused_unchanged(player, quest_data, CAITLIN, "combat_prerequisites_unmet")

    def test_empty_dependencies_preserve_an_independent_partially_sourced_fight(self):
        quest_data = {QUEST_ID: copy.deepcopy(QUEST_DATA[QUEST_ID])}
        _encounters(quest_data[QUEST_ID])[CAITLIN].pop("required_encounters")
        player = _combat_player()
        self.assertEqual(
            tuple(row["encounter_id"] for row in quest_logic.quest_current_stage_resolvable_combat_blockers_pure(
                player, QUEST_ID, quest_data,
            )), (CAITLIN,),
        )
        self.assertEqual(
            {row["encounter_id"] for row in quest_logic.quest_current_stage_blockers_pure(player, QUEST_ID, quest_data)
             if row["kind"] == "combat_missing_stats"}, {KAYLE, REESE},
        )

    def test_completed_dependency_does_not_bypass_stage_prerequisites(self):
        requirements = (
            {"required_inventory": {"Coins": 1000}},
            {"required_tools": {"Rune pickaxe": 1}},
            {"required_skills": ({"skill_id": "mining", "display_name": "Mining", "level": 50},)},
            {"required_routes": ("Unchosen route",)},
        )
        for requirement in requirements:
            with self.subTest(requirement=requirement):
                quest_data = {QUEST_ID: copy.deepcopy(QUEST_DATA[QUEST_ID])}
                for row in quest_data[QUEST_ID]["stage_requirements"]:
                    if row["stage"] == 2:
                        row.update(requirement)
                player = _combat_player()
                player["quest_combat_encounters"] = {QUEST_ID: [KAYLE]}
                self.assertEqual(
                    quest_logic.quest_current_stage_resolvable_combat_blockers_pure(player, QUEST_ID, quest_data), (),
                )
                self.assert_refused_unchanged(player, quest_data, CAITLIN, "stage_requirements_unmet")

    def test_reese_remains_unsourced_after_caitlin_is_completed(self):
        player = _combat_player()
        self.assert_refused_unchanged(player, QUEST_DATA, REESE, "combat_prerequisites_unmet")
        player["quest_combat_encounters"] = {QUEST_ID: [KAYLE, CAITLIN]}
        blockers = quest_logic.quest_current_stage_blockers_pure(player, QUEST_ID, QUEST_DATA)
        self.assertEqual(
            [(row["encounter_id"], row["kind"]) for row in blockers if "encounter_id" in row],
            [(REESE, "combat_missing_stats")],
        )
        self.assert_refused_unchanged(player, QUEST_DATA, REESE, "combat_missing_stats")
