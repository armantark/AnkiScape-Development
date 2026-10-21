import copy
from dataclasses import replace
import unittest

import pkg_alias  # noqa: F401 (installs the ankiscape package alias)
from ankiscape.core.constants import QUEST_DATA
from ankiscape.data.quest.catalog import _catalog_combat_encounters
from ankiscape.data.quest.combat_replacements import apply_horror_from_the_deep_lifepoints
from ankiscape.data.quest.contract import QuestStageRequirement
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from ankiscape.logic_pure.logic_pure_combat_setup import _combat_enemy_start_lifepoints
from ankiscape.logic_pure.logic_pure_quest import _quest_combat_enemy_spec


QUEST_ID = "horror_from_the_deep"
BABY_ID = "horror_from_the_deep_dagannoth_100"
MOTHER_ID = "horror_from_the_deep_dagannoth_mother_horror_from_the_deep_100"
BABY_SOURCE = (
    "https://web.archive.org/web/20121105084853id_/http://www.runehq.com:80/monster/dagannoth-baby"
)
MOTHER_SOURCE = (
    "https://runescape.wiki/w/index.php?title=Dagannoth_mother_(Horror_from_the_Deep)&oldid=6448031; "
    "https://web.archive.org/web/20100824081504id_/http://www.tip.it:80/runescape/?rs2monster_id=377"
)
LIMITATION = "other combat fields retain restoration provenance, not period qualification: "
DRIFT_ERROR = "Horror from the Deep life-point override target changed"


def _generated_quest():
    return next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == QUEST_ID)


def _generated_encounters():
    return _catalog_combat_encounters(tuple(
        encounter
        for requirement in _generated_quest()["stage_requirements"]
        for encounter in requirement["combat_encounters"]
    ))


def _composed_encounters():
    return tuple(
        encounter
        for requirement in QUEST_DATA[QUEST_ID]["stage_requirements"]
        for encounter in requirement["combat_encounters"]
    )


class TestHorrorFromTheDeepLifepoints(unittest.TestCase):
    def test_composed_catalog_uses_approved_lifepoints(self):
        encounters = _composed_encounters()
        for encounter_id, hitpoints, source in (
            (BABY_ID, 350, BABY_SOURCE),
            (MOTHER_ID, 1000, MOTHER_SOURCE),
        ):
            with self.subTest(encounter_id=encounter_id):
                matches = [row for row in encounters if row["encounter_id"] == encounter_id]
                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0]["npc_stats"]["hitpoints"], hitpoints)
                self.assertIn(f"hitpoints: {source}; owner accepted 2026-10-20; ", matches[0]["npc_stats_source"])
                self.assertIn(LIMITATION, matches[0]["npc_stats_source"])

    def test_override_preserves_other_fields_and_inputs(self):
        generated_before = copy.deepcopy(_generated_quest())
        baby, mother = _generated_encounters()
        unrelated = replace(baby, encounter_id="unrelated_encounter")
        requirement = QuestStageRequirement(
            stage=6,
            description="Fight the dagannoths",
            variant="test_variant",
            required_inventory=(("Sword", 1),),
            consumed_inventory=(("Fire rune", 1),),
            produced_inventory=(("Test item", 1),),
            required_actions=("Test action",),
            required_routes=("Test route",),
            combat_encounters=(baby, unrelated, mother),
            source="Requirement provenance",
        )
        untouched = QuestStageRequirement(5, "An unrelated row", combat_encounters=(unrelated,))
        requirements = (untouched, requirement)
        before = copy.deepcopy(requirements)

        result = apply_horror_from_the_deep_lifepoints(QUEST_ID, requirements)

        self.assertEqual(requirements, before)
        self.assertEqual(_generated_quest(), generated_before)
        self.assertIs(result[0], untouched)
        self.assertIsNot(result[1], requirement)
        self.assertEqual(
            tuple(row.encounter_id for row in result[1].combat_encounters),
            (BABY_ID, "unrelated_encounter", MOTHER_ID),
        )
        self.assertIs(result[1].combat_encounters[1], unrelated)
        self.assertEqual(
            replace(result[1], combat_encounters=requirement.combat_encounters),
            requirement,
        )
        for index, hitpoints, source in ((0, 350, BABY_SOURCE), (2, 1000, MOTHER_SOURCE)):
            original = requirement.combat_encounters[index]
            updated = result[1].combat_encounters[index]
            with self.subTest(encounter_id=original.encounter_id):
                self.assertIsNot(updated, original)
                self.assertEqual(
                    replace(updated, npc_stats=original.npc_stats, npc_stats_source=original.npc_stats_source),
                    original,
                )
                self.assertEqual(
                    tuple(key for key, _value in updated.npc_stats),
                    tuple(key for key, _value in original.npc_stats),
                )
                self.assertEqual(dict(updated.npc_stats)["hitpoints"], hitpoints)
                self.assertEqual(
                    tuple(pair for pair in updated.npc_stats if pair[0] != "hitpoints"),
                    tuple(pair for pair in original.npc_stats if pair[0] != "hitpoints"),
                )
                self.assertEqual(
                    updated.npc_stats_source,
                    f"hitpoints: {source}; owner accepted 2026-10-20; {LIMITATION}{original.npc_stats_source}",
                )
        self.assertIs(apply_horror_from_the_deep_lifepoints("another_quest", requirements), requirements)

    def test_override_rejects_catalog_drift(self):
        encounters = _generated_encounters()
        for target in encounters:
            others = tuple(row for row in encounters if row is not target)
            without_hitpoints = tuple(pair for pair in target.npc_stats if pair[0] != "hitpoints")
            cases = {
                "missing target": (others,),
                "duplicated target": (encounters, (target,)),
                "missing hitpoints": ((*others, replace(target, npc_stats=without_hitpoints)),),
                "duplicated hitpoints": (
                    (*others, replace(target, npc_stats=(*target.npc_stats, ("hitpoints", 123)))),
                ),
            }
            for case, encounter_groups in cases.items():
                with self.subTest(encounter_id=target.encounter_id, case=case):
                    requirements = tuple(
                        QuestStageRequirement(index + 1, "Test fight", combat_encounters=group)
                        for index, group in enumerate(encounter_groups)
                    )
                    with self.assertRaises(ValueError) as raised:
                        apply_horror_from_the_deep_lifepoints(QUEST_ID, requirements)
                    self.assertEqual(str(raised.exception), DRIFT_ERROR)

    def test_enemy_spec_receives_approved_lifepoints(self):
        for encounter in _composed_encounters():
            encounter_id = encounter["encounter_id"]
            expected = {BABY_ID: 350, MOTHER_ID: 1000}[encounter_id]
            with self.subTest(encounter_id=encounter_id):
                enemy = _quest_combat_enemy_spec(QUEST_ID, encounter_id, encounter)
                self.assertEqual(enemy["stats"]["hitpoints"], expected)
                maximum, starting, _stop, _stopped = _combat_enemy_start_lifepoints(enemy, {}, False)
                self.assertEqual((maximum, starting), (expected, expected))

    def test_existing_baby_fight_uses_standard_lifepoint_clamp(self):
        baby = next(row for row in _composed_encounters() if row["encounter_id"] == BABY_ID)
        enemy = _quest_combat_enemy_spec(QUEST_ID, BABY_ID, baby)
        enemy_before = copy.deepcopy(enemy)
        for remaining, expected in ((700, 350), (500, 350), (350, 350), (200, 200), (1, 1)):
            with self.subTest(remaining=remaining):
                encounter = {"enemy_lifepoints": remaining, "quest_encounter_id": BABY_ID}
                before = copy.deepcopy(encounter)
                maximum, starting, _stop, _stopped = _combat_enemy_start_lifepoints(enemy, encounter, True)
                self.assertEqual((maximum, starting), (350, expected))
                self.assertEqual(encounter, before)
                self.assertEqual(enemy, enemy_before)
