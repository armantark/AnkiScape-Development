"""Earn ordinary prerequisites through the runtime writer; never seed deeds."""

import copy

import pkg_alias  # noqa: F401
from ankiscape.core.constants import EXP_TABLE, ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.runtime.runtime_actions import handle_quest_answer
from tests.test_runtime_actions import _context

QUEST_ID = "animal_magnetism"
OLD_SENTINEL = "Complete Animal Magnetism stage 1 objective"
SKILL_GATES = (("crafting", 19), ("ranged", 30), ("slayer", 18), ("thieving", 15), ("woodcutting", 35))


def review(player, calls=None):
    calls = calls if calls is not None else dict(xp=[], saves=0, errors=[])
    # Mid-rolls hit and deal damage through the genuine combat reducer.
    ctx = _context(player, calls, random_values=(0.5,) * 4000)
    return handle_quest_answer(ctx)


def _prepared_player():
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    for skill, level in (*SKILL_GATES, ("attack", 80), ("strength", 80), ("defense", 80), ("constitution", 80)):
        player[skill + "_level"] = level
        player[skill + "_exp"] = EXP_TABLE[level - 1]
    player["combat_lifepoints"] = 800
    player["equipment"]["weapon"] = "Rune scimitar"
    player["inventory"].update({"Fish food": 1, "Poison": 1, "Spade": 1})
    return player


def _earn_ernest(player):
    player["current_quest"] = "ernest_the_chicken"
    for stage in range(1, 9):
        assert review(player), f"Ernest stage {stage} refused"
        assert player["quests"]["ernest_the_chicken"]["progress"] == stage + 1
    assert player["quests"]["ernest_the_chicken"]["completed"]
    assert player["inventory"]["Poisoned fish food"] == 0
    assert all(player["inventory"][item] == 0 for item in ("Pressure gauge", "Rubber tube", "Oil can"))
    assert player["inventory"]["Egg"] >= 10


def _earn_restless_ghost(player):
    quest_id = "the_restless_ghost"
    player["current_quest"] = quest_id
    assert review(player)  # Ordinary amulet grant.
    assert player["inventory"]["Ghostspeak amulet"] == 1
    assert review(player)  # Talk using that amulet.
    assert review(player)  # Produce the skull.
    assert player["inventory"]["Muddy skull"] == 1
    encounter = QUEST_DATA[quest_id]["stage_requirements"][-1]["combat_encounters"][0]["encounter_id"]
    for _ in range(30):
        if encounter in player["quest_combat_encounters"].get(quest_id, ()):
            break
        assert review(player)  # Real combat, not a planted completion flag.
        assert player["quests"][quest_id]["progress"] == 4
    assert encounter in player["quest_combat_encounters"][quest_id]
    assert review(player)  # Return the produced skull.
    assert player["quests"][quest_id]["completed"]
    assert player["inventory"]["Muddy skull"] == 0
    assert player["inventory"]["Ancient bones"] >= 5


def ernest_only_player():
    player = _prepared_player()
    _earn_ernest(player)
    player["current_quest"] = QUEST_ID
    return player


def restless_only_player():
    player = _prepared_player()
    _earn_restless_ghost(player)
    player["current_quest"] = QUEST_ID
    return player


def eligible_player():
    player = ernest_only_player()
    _earn_restless_ghost(player)
    player["current_quest"] = QUEST_ID
    return player


def product_values(player):
    """Complete owned goods, XP, claims and rewards; no normal telemetry."""
    keys = {key for key in player if key.endswith("_exp") or "claim" in key or "reward" in key}
    keys.update(("quests", "quest_action_proofs", "inventory", "quest_points"))
    return copy.deepcopy({key: player[key] for key in keys})
