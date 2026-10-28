"""Ordinary acquisition and explicitly seeded boundary fixtures."""
import copy
import json
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import EXP_TABLE, ITEM_DEFINITIONS, MAGIC_DATA, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic.shop_logic import (
    apply_shop_buy_pure, apply_shop_vendor_action_pure,
    preview_shop_vendor_action_pure, rollback_shop_event_pure,
)
from ankiscape.logic_pure import quest_action_proofs
from ankiscape.runtime.runtime_actions import (
    handle_magic_answer, handle_mining_answer, handle_quest_answer, handle_thieving_answer,
)
from tests.test_integration_smoke import _DummyCol
from tests.test_runtime_actions import _context

QUEST_ID = "creature_of_fenkenstrain"
BRAIN_CAST = "telegrab_pickled_brain"
ROAVAR = "roavar_buy_pickled_brain"
BUCKET_ROW = ("general_store", "general_store:3:1925")
SPADE_ROW = ("general_store", "general_store:5:952")
AIR_ROW = ("lundails_arena_rune_shop", "lundails_arena_rune_shop:0:556")
LAW_ROW = ("lundails_arena_rune_shop", "lundails_arena_rune_shop:10:563")
STAGE_TWO_ACTIONS = (
    "Follow the Gardener Ghost's directions closely and you should reach his grave soon enough.",
    "Make sure the grave's name matches the ghost's, dig, and you will get the head.",
    "Go to the bar in Canifis.",
    "Search the bookcase in the west room for The Joy of Gravedigging and you will find a marble amulet.",
    "Search the east room's bookcase for Handy Maggot Avoidance Techniques and you will find the obsidian amulet.",
    "Use them with each other to get a star amulet.",
)
# The bookcase amulets are made and combined inside the same review.
STAGE_OUTPUTS = {"Decapitated head": 1, "Star amulet": 1}
BRAIN_PURCHASE = {"Coins": -50, "Pickled brain": 1}
STAGE_ITEM_IDS = {
    "Decapitated head": 4197,
    "Pickled brain": 4199,
    "Marble amulet": 4187,
    "Obsidian amulet": 4188,
    "Star amulet": 4183,
}
# These Crucible and Duel Arena fields live as tuples, reach the JSON save as
# lists, and become tuples again on load; the reopen check keeps that exact gap.
JSON_LIST_FIELDS = {"crucible_lessons_taken", "crucible_unlocks", "duel_arena_rule_ids"}


def _completed(quest_id):
    return {"started": True, "progress": QUEST_DATA[quest_id]["stages"], "completed": True}


def _collect(player, handler, item, count):
    for _ in range(400):
        if player["inventory"].get(item, 0) >= count:
            return
        handler(_context(player))
    raise AssertionError(f"{handler.__name__} stopped below {count} {item}")


def _commit(player, transaction):
    updated, result = transaction
    assert result["allowed"], result
    player.clear()
    player.update(updated)


def _buy(player, shop_row):
    _commit(player, apply_shop_buy_pure(player, *shop_row, 1, rng=lambda: 0.5))


def _finish_quest(player, quest_id):
    player["current_quest"] = quest_id
    for _ in range(100):
        assert handle_quest_answer(_context(player)), quest_id
        if player["quests"][quest_id]["completed"]:
            return
    raise AssertionError(f"{quest_id} did not complete")


def _ordinary_stage_two():
    """Reach stage 2 through real reviews and shop purchases; only skill levels and life points are seeded."""
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    for skill in ("attack", "strength", "defense", "constitution"):
        player[f"{skill}_level"] = 99
    player.update(
        combat_lifepoints=990, crafting_level=20, thieving_level=25, magic_level=33,
        current_thieving="pickpocket_man", current_ore="rune_essence",
    )
    player["inventory"] = {}
    # Rune Mysteries opens essence mining; Priest in Peril takes 50 Rune essence and a Bucket.
    _finish_quest(player, "rune_mysteries")
    _collect(player, handle_mining_answer, "Rune essence", 50)
    _finish_quest(player, "the_restless_ghost")
    _collect(player, handle_thieving_answer, "Coins", 5)
    _buy(player, BUCKET_ROW)
    _buy(player, SPADE_ROW)
    _finish_quest(player, "priest_in_peril")
    player["current_quest"] = QUEST_ID
    assert handle_quest_answer(_context(player)), "Fenkenstrain opening"
    assert player["quests"][QUEST_ID]["progress"] == 2
    return player


def _at_stage_two(**inventory):
    """Seeded stage-2 state: it sets up refusals and casts, never acquisition proof."""
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player.update(current_quest=QUEST_ID, crafting_level=20, thieving_level=25, magic_level=33)
    player["magic_exp"] = float(EXP_TABLE[32])
    for quest_id in ("priest_in_peril", "the_restless_ghost"):
        player["quests"][quest_id] = _completed(quest_id)
    player["quests"][QUEST_ID] = {"started": True, "progress": 2, "completed": False}
    player["inventory"] = {"Ghostspeak amulet": 1, **inventory}
    return player


def _delta(before, after):
    names = set(before["inventory"]) | set(after["inventory"])
    changes = {name: after["inventory"].get(name, 0) - before["inventory"].get(name, 0) for name in names}
    return {name: change for name, change in changes.items() if change}


def _brain_casts(player):
    return player.get("action_telemetry", {}).get("actions", {}).get(f"magic:{BRAIN_CAST}", {}).get("successes", 0)


def _proof_events(action):
    with patch.object(
        quest_action_proofs, "quest_action_proofs_after_event_pure",
        wraps=quest_action_proofs.quest_action_proofs_after_event_pure,
    ) as events:
        result = action()
    return result, [call.args[1:3] for call in events.call_args_list]


class _JsonCollection(_DummyCol):
    """Anki keeps config values as JSON, so this store holds only the serialized text."""

    def set_config(self, key, value):
        self._store[key] = json.dumps(value)

    def get_config(self, key, default=None):
        return json.loads(self._store[key]) if key in self._store else default


