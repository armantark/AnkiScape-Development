"""Shared state with unrelated custody and later quest sentinels."""

import copy

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.data.quest.elemental_workshop_iii import QUEST_ID

ENCOUNTER = "elemental_workshop_iii_earth_elemental_35"
OLD_PROOF = "Find and read the Ragged book in the workshop"


def player(stage=1, *, started=True, completed=False):
    data = migrate_loaded_data(default_player_data(ORE_DATA, ITEM_DEFINITIONS), ORE_DATA, ITEM_DEFINITIONS)
    for requirement in QUEST_DATA[QUEST_ID]["required_quests"]:
        prerequisite = requirement["quest_id"]
        data["quests"][prerequisite] = dict(
            started=True, completed=True, progress=QUEST_DATA[prerequisite]["stages"],
        )
    data.update(mining_level=20, smithing_level=33, defense_level=33)
    data["quests"][QUEST_ID] = dict(started=started, completed=completed, progress=stage)
    data["current_quest"] = QUEST_ID
    data["inventory"].update({"Coins": 17, "Slashed book": 1, "Beaten book": 2})
    data["quest_action_proofs"] = ["Unrelated earned deed"]
    data["quest_route_states"] = {QUEST_ID: ["retained_route"]}
    data["quest_combat_encounter_counts"] = {QUEST_ID: {ENCOUNTER: 1}}
    data["quest_combat_active_encounters"] = {QUEST_ID: {ENCOUNTER: 123}}
    return data


def expected_opening(before, *, acquired=True):
    from ankiscape.data.quest.elemental_workshop_iii import ACQUIRE_PROOF, READ_PROOF, RAGGED_BOOK

    expected = copy.deepcopy(before)
    expected["quests"][QUEST_ID] = dict(started=True, completed=False, progress=2)
    expected["current_quest"] = QUEST_ID
    if acquired:
        expected["inventory"][RAGGED_BOOK] = 1
    expected["quest_action_proofs"] = sorted(set(before["quest_action_proofs"]) | {
        READ_PROOF, *([ACQUIRE_PROOF] if acquired else []),
    })
    return expected
