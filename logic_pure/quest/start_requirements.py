"""Read-only conditions for starting a quest, separate from stage requirements."""

from typing import Mapping

from ...logic.varrock_museum_logic import sanitize_varrock_museum_state_pure
from ..logic_pure_state import quest_completed_pure


def _quest_prerequisite_reasons_pure(player_data, quest, quest_data):
    reasons = []
    for requirement in quest.get("required_quests", ()) or ():
        if not isinstance(requirement, Mapping):
            continue
        required_id = requirement.get("quest_id")
        display_name = requirement.get("display_name")
        if not isinstance(required_id, str):
            continue
        if not isinstance(quest_data.get(required_id), Mapping):
            reasons.append(f"{display_name or required_id.replace('_', ' ').title()} (not implemented)")
        elif not quest_completed_pure(player_data, required_id):
            reasons.append(str(display_name or required_id.replace("_", " ").title()))

    return reasons


def _quest_museum_claim_reasons_pure(player_data, quest_id):
    if quest_id != "defender_of_varrock":
        return ()
    state = sanitize_varrock_museum_state_pure(player_data.get("varrock_museum"))
    if "shield_of_arrav" in state["quest_stories_claimed"]:
        return ()
    # Defender6542570 line 39; independently Tip.It capture 20120225070338.
    return ("Claim Varrock Museum Kudos for completing Shield of Arrav",)
