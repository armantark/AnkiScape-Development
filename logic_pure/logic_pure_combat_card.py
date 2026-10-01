"""The review HUD's Combat card: the ordinary combat target, or the quest fight
the next quest review resolves."""

from ..logic.slayer_logic import slayer_assignment_progress_pure
from .logic_pure_combat_engine import combat_hud_state_pure
from .logic_pure_quest import (
    _quest_combat_enemy_spec,
    _quest_combat_resumed_encounter,
    _quest_combat_target_id,
    _quest_current_stage_encounter_by_id,
    quest_current_stage_resolvable_combat_blockers_pure,
)
from .logic_pure_state import sanitize_quest_combat_active_encounters_pure


def _card_target_text(name, state):
    return f"{name} • {state['status']}" if state["status"] else name


def _trains_text(state):
    return f"Trains {' • '.join(state['trained_skills'])}"


def combat_card_view_pure(player_data, equipment_data):
    """``chips_lead`` precedes the trained skills' icons; ``chips_text`` is the
    whole sentence, for the tooltip."""
    state = combat_hud_state_pure(player_data, equipment_data=equipment_data)
    kills = f"Kills: {state['kills_total']} · "
    return {
        **state,
        "target_text": _card_target_text(state["enemy_name"], state),
        "chips_lead": f"{kills}Trains ",
        "chips_text": kills + _trains_text(state),
        "slayer_text": slayer_assignment_progress_pure(player_data),
        "target_wraps": False,
    }


def quest_fight_card_view_pure(player_data, quest_data, equipment_data):
    """The Combat card for the current quest's next fight, or None when the next
    quest review does not fight.

    The quest resolver restores the ordinary target and encounter after every
    review, so the boss and its carried LP are projected back in here. A quest
    boss is a kill outside any Slayer task, so the chips drop the kill count and
    the Slayer line; a stage that needs several kills names how many remain, as
    its quest blocker does.
    """
    quest_id = player_data.get("current_quest")
    quest = quest_data.get(quest_id) if isinstance(quest_id, str) else None
    fights = quest_current_stage_resolvable_combat_blockers_pure(player_data, quest_id, quest_data) if quest else ()
    if not fights:
        return None
    fight = fights[0]
    encounter_id = fight["encounter_id"]
    target_id = _quest_combat_target_id(quest_id, encounter_id)
    encounter = _quest_current_stage_encounter_by_id(player_data, quest_id, quest_data, encounter_id)
    active = sanitize_quest_combat_active_encounters_pure(player_data.get("quest_combat_active_encounters"))
    saved_lifepoints = active.get(quest_id, {}).get(encounter_id, 0)
    projected = {
        **player_data,
        "current_combat_target": target_id,
        "combat_encounter": _quest_combat_resumed_encounter(player_data, target_id, saved_lifepoints),
    }
    enemy = {target_id: _quest_combat_enemy_spec(quest_id, encounter_id, encounter)}
    state = combat_hud_state_pure(projected, enemy, equipment_data)
    quest_name = str(quest.get("display_name", quest_id))
    # Some quest-only NPCs carry their quest in parentheses ("Bandit (Diamond in
    # the Rough)"); the label already names the quest once.
    boss_name = state["enemy_name"].removesuffix(f" ({quest_name})")
    remaining = f" x{fight['remaining_quantity']}" if fight["total_quantity"] > 1 else ""
    return {
        **state,
        "target_text": _card_target_text(f"{quest_name} · {boss_name}{remaining}", state),
        "chips_lead": "Trains ",
        "chips_text": _trains_text(state),
        "slayer_text": "",
        # The longest quest and boss names need a second line.
        "target_wraps": True,
    }


def review_combat_card_view_pure(player_data, skill, quest_data, equipment_data):
    """The Combat card the review HUD shows for the active skill, or None.

    The equipped weapon decides which skills the attack style trains, so the
    card needs the same equipment table the combat review resolves with.
    """
    if skill == "Quests":
        return quest_fight_card_view_pure(player_data, quest_data, equipment_data)
    return combat_card_view_pure(player_data, equipment_data) if skill == "Combat" else None
