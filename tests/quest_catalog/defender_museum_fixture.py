"""Earn Shield on its live Phoenix route; prepare only unrelated start gates."""

import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic_pure.logic_pure import (
    apply_quest_combat_encounter_pure,
    apply_quest_progress_pure,
    apply_quest_route_choice_pure,
    start_quest_pure,
)

from tests.quest_action_proof_helpers import quest_action_proofs_for_quest

SHIELD = "shield_of_arrav"
DEFENDER = "defender_of_varrock"
CLAIM_REASON = "Claim Varrock Museum Kudos for completing Shield of Arrav"
PREREQUISITES = (
    (SHIELD, "Shield of Arrav"),
    ("the_knights_sword", "The Knight's Sword"),
    ("family_crest", "Family Crest"),
    ("what_lies_below", "What Lies Below"),
    ("demon_slayer", "Demon Slayer"),
    ("temple_of_ikov", "Temple of Ikov"),
    ("garden_of_tranquillity", "Garden of Tranquillity"),
)
LEVELS = (("agility", 51), ("hunter", 51), ("mining", 59), ("smithing", 54))


def typed_snapshot(value):
    if isinstance(value, dict):
        return type(value), {(type(key), key): typed_snapshot(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return type(value), tuple(typed_snapshot(item) for item in value)
    return type(value), value


def prepare_completion(player, quest_id):
    """Gate isolation only: this does not certify acquisition of this quest."""
    player["quests"][quest_id] = {
        "started": True, "completed": True, "progress": QUEST_DATA[quest_id]["stages"],
    }


def _progress(player, stage, proofs, completed=False):
    check = unittest.TestCase()
    updated, ok, completed_now = apply_quest_progress_pure(player, SHIELD, QUEST_DATA)
    check.assertTrue(ok)
    check.assertEqual(completed_now, completed)
    check.assertEqual(updated["quests"][SHIELD]["progress"], stage)
    check.assertEqual(quest_action_proofs_for_quest(updated, SHIELD, QUEST_DATA), proofs)
    return updated


def earned_shield_player():
    check = unittest.TestCase()
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    check.assertFalse(player["quests"][SHIELD]["started"])
    # Existing test combat inputs, not period quest requirements.
    player["inventory"]["Coins"] = 20
    for skill in ("attack", "strength", "defense", "constitution"):
        player[f"{skill}_level"] = 99
    player, ok = start_quest_pure(player, SHIELD, QUEST_DATA)
    check.assertTrue(ok)
    check.assertEqual(quest_action_proofs_for_quest(player, SHIELD, QUEST_DATA), ())
    common = (
        "Find and read the Shield of Arrav book",
        "Ask Reldo about the Phoenix Gang",
        "Bribe Baraek for the Phoenix hideout",
    )
    for count in (1, 2, 3):
        player = _progress(player, count + 1, common[:count])
    check.assertEqual(player["inventory"]["Coins"], 0)
    player, ok = apply_quest_route_choice_pure(player, SHIELD, QUEST_DATA, "Join the Phoenix Gang")
    check.assertTrue(ok)
    route = (
        "Ask Straven for the Phoenix loyalty task",
        "Hand Straven Jonny's intelligence report",
        "Search the Phoenix Gang shield chest",
        "Show King Roald the Phoenix shield half",
        "Have Curator Haig Halen authenticate the Phoenix shield half",
        "Claim the Shield of Arrav reward from King Roald",
    )
    player = _progress(player, 5, common + route[:1])
    player, ok, result = apply_quest_combat_encounter_pure(
        player, SHIELD, QUEST_DATA, "shield_of_arrav_jonny_the_beard_2",
    )
    check.assertTrue(ok)
    check.assertEqual(result["reason"], "combat_resolved")
    player = _progress(player, 6, common + route[:1])
    check.assertEqual(player["inventory"]["Intel report"], 1)
    for stage, count in ((6, 2), (7, 3), (8, 4), (9, 5), (10, 5), (11, 6)):
        player = _progress(player, stage + 1, common + route[:count], stage == 11)
    check.assertTrue(player["quests"][SHIELD]["completed"])
    check.assertEqual(player["inventory"]["Coins"], 600)
    check.assertEqual(player["quest_points"], 1)
    check.assertEqual(player["inventory"].get("Certificate", 0), 0)
    check.assertEqual(player["inventory"].get("Broken shield (Phoenix half)", 0), 0)
    return player


def ready_defender_player():
    player = earned_shield_player()
    for quest_id, _name in PREREQUISITES[1:]:
        prepare_completion(player, quest_id)
    for skill, level in LEVELS:
        player[f"{skill}_level"] = level
    # Unrelated history isolates the ordinary Minas command to the earned Shield.
    player["varrock_museum"]["quest_stories_claimed"] = ["demon_slayer", "temple_of_ikov"]
    return player
