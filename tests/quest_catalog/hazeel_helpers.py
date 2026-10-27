"""Ordinary opening helpers: start, review, choose and perform real deeds.

Adversarial/legacy fixtures live explicitly in their individual tests.
"""

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ORE_DATA, ITEM_DEFINITIONS, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.quest.hazeel_opening import QUEST_ID, BRANCH_ROUTES
from ankiscape.logic_pure.logic_pure_quest import (
    start_quest_pure, apply_quest_progress_pure, apply_quest_route_choice_pure,
)
from ankiscape.logic_pure.quest.hazeel import hazeel_opening_next_action_pure


def fresh_player():
    return default_player_data(ORE_DATA, ITEM_DEFINITIONS)


def started_player():
    player, ok = start_quest_pure(fresh_player(), QUEST_ID, QUEST_DATA)
    assert ok
    return player


def review(player):
    updated, ok, completed = apply_quest_progress_pure(player, QUEST_ID, QUEST_DATA)
    assert ok and not completed
    return updated


def shared_player():
    player = started_player()
    for _ in range(2):
        player = review(player)
    return player


def choose(player, branch):
    player, ok = apply_quest_route_choice_pure(player, QUEST_ID, QUEST_DATA, BRANCH_ROUTES[branch])
    assert ok
    return player


def branch_player(branch):
    return choose(shared_player(), branch)


def before_valves(branch):
    player = branch_player(branch)
    while not hazeel_opening_next_action_pure(player).direction:
        player = review(player)
    return player


def complete_opening(branch):
    player = branch_player(branch)
    while player['quests'][QUEST_ID]['progress'] < 2:
        player = review(player)
    return player
