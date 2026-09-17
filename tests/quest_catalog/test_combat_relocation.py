import copy
import unittest
from dataclasses import replace
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.quest import catalog
from ankiscape.data.quest.combat_relocation import relocate_combat_encounters
from ankiscape.data.quest_data import QuestCombatEncounter, QuestStageRequirement


_QUEST_CASES = (
    (
        "rum_deal",
        "Rum Deal combat encounter catalog changed",
        (
            ("rum_deal_evil_spirit_150", 3, ()),
            ("rum_deal_fever_spider_49", 4, (("Fever spider body", 1),)),
        ),
    ),
    (
        "zogre_flesh_eaters",
        "Zogre Flesh Eaters combat encounter catalog changed",
        (
            ("zogre_flesh_eaters_zombie_39", 2, (("Ruined backpack", 1),)),
            (
                "zogre_flesh_eaters_slash_bash_111",
                6,
                (("Zogre bones", 2), ("Ourg bones", 3), ("Ogre artefact", 1)),
            ),
        ),
    ),
)


class TestQuestCombatRelocation(unittest.TestCase):
    def test_unregistered_quest_preserves_input_identity(self):
        requirements = object()
        self.assertIs(relocate_combat_encounters("cabin_fever", requirements), requirements)

    def test_missing_encounters_preserve_each_quest_error(self):
        for quest_id, message, encounters in _QUEST_CASES:
            with self.subTest(quest=quest_id):
                requirements = (
                    QuestStageRequirement(
                        stage=1,
                        description="Incomplete catalog",
                        combat_encounters=(QuestCombatEncounter(encounters[0][0], "Survivor"),),
                    ),
                )
                with self.assertRaises(ValueError) as caught:
                    relocate_combat_encounters(quest_id, requirements)
                self.assertEqual(str(caught.exception), message)

    def test_relocation_preserves_order_other_fields_and_input(self):
        zombie = QuestCombatEncounter(
            "zogre_flesh_eaters_zombie_39", "Zombie", level=39,
            guaranteed_drops=(("Old drop", 1),), source="Frozen source",
        )
        latest_zombie = replace(zombie, source_text="Last occurrence")
        slash_bash = QuestCombatEncounter(
            "zogre_flesh_eaters_slash_bash_111", "Slash Bash", level=111,
            npc_configs=(("attack_speed", 4),),
        )
        first = QuestCombatEncounter("unmoved_first", "First")
        second = QuestCombatEncounter("unmoved_second", "Second")
        requirements = (
            QuestStageRequirement(
                stage=6, description="Finish", required_inventory=(("Key", 1),),
                combat_encounters=(zombie, first, slash_bash, second),
            ),
            QuestStageRequirement(stage=2, description="Evidence", combat_encounters=(latest_zombie,)),
        )
        original = copy.deepcopy(requirements)

        relocated = relocate_combat_encounters("zogre_flesh_eaters", requirements)

        self.assertEqual(requirements, original)
        self.assertEqual(
            relocated,
            (
                replace(requirements[0], combat_encounters=(
                    first,
                    second,
                    replace(slash_bash, guaranteed_drops=(
                        ("Zogre bones", 2), ("Ourg bones", 3), ("Ogre artefact", 1),
                    )),
                )),
                replace(requirements[1], combat_encounters=(
                    replace(latest_zombie, guaranteed_drops=(("Ruined backpack", 1),)),
                )),
            ),
        )
        self.assertIs(relocated[0].combat_encounters[0], first)
        self.assertIs(relocated[0].combat_encounters[1], second)

    def test_relocation_does_not_depend_on_cleanup_rows(self):
        for quest_id, _message, encounters in _QUEST_CASES:
            with self.subTest(quest=quest_id):
                requirements = (
                    QuestStageRequirement(
                        stage=1, description="Before relocation",
                        combat_encounters=tuple(
                            QuestCombatEncounter(encounter_id, encounter_id)
                            for encounter_id, _stage, _drops in encounters
                        ),
                    ),
                    *(QuestStageRequirement(stage, "Destination") for _id, stage, _drops in encounters),
                )
                with patch.dict(catalog.QUEST_STAGE_REQUIREMENT_CLEANUPS_BY_ID, {}, clear=True):
                    relocated = catalog._apply_stage_requirement_cleanups(quest_id, requirements)
                self.assertEqual(relocated[0].combat_encounters, ())
                self.assertEqual(
                    tuple(
                        (encounter.encounter_id, row.stage, encounter.guaranteed_drops)
                        for row in relocated
                        for encounter in row.combat_encounters
                    ),
                    encounters,
                )


if __name__ == "__main__":
    unittest.main()
