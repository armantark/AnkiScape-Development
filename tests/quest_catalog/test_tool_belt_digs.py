import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic_pure.logic_pure import quest_current_stage_blocker_reasons_pure


def _at_stage(quest_id: str, stage: int) -> dict:
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data["quests"][quest_id] = {"started": True, "completed": False, "progress": stage}
    data["inventory"].pop("Spade", None)
    return data


def _spade_blockers(data: dict, quest_id: str) -> list[str]:
    return [
        reason
        for reason in quest_current_stage_blocker_reasons_pure(data, quest_id, QUEST_DATA)
        if "Spade" in reason
    ]


class QuestSpadeDigTest(unittest.TestCase):
    def test_shilo_village_dig_needs_a_spade_in_the_bank(self) -> None:
        data = _at_stage("shilo_village", 2)
        self.assertEqual(_spade_blockers(data, "shilo_village"), ["Needs Spade x1"])
        data["inventory"]["Spade"] = 1
        self.assertEqual(_spade_blockers(data, "shilo_village"), [])

    def test_plague_city_dig_uses_the_belt_spade(self) -> None:
        data = _at_stage("plague_city", 4)
        self.assertEqual(_spade_blockers(data, "plague_city"), [])


if __name__ == "__main__":
    unittest.main()
