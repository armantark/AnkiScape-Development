"""Atomic Lazim transactions and read-only opening projections."""

from collections.abc import Mapping

from ...core.tool_belt import tool_on_belt
from ...data.quest.enakhra_opening import (
    QUEST_ID, MASS_KEY, TARGET_KG, SANDSTONE, BLOCK_ID, BLOCK, BASE_ID, BASE,
    CHISEL, SPLIT_OUTPUTS, PROOFS, EVENT_PREFIX, NOTICES,
)
from ..logic_pure_state import _copy_player_data_with_nested, quest_state_pure
from ..quest_action_proofs import (
    quest_action_proof_completed_pure, record_runtime_quest_action_proofs_pure,
)

INCONSISTENT = "Opening progress is inconsistent; no items were changed"
LEGACY_JOURNAL = ("Lazim wants a sandstone statue. Its base takes 32 kg of sandstone.",)
_ORDER = ("offer_help", "deliver_sandstone", "receive_32kg", "chisel_base", "talk_after_base", "place_base")
_PHASE_ACTIONS = {"offer_help": "offer_help", "supply": "deliver_sandstone", "chisel_base": "chisel_base",
                  "talk_after_base": "talk_after_base", "place_base": "place_base"}


def _proved(player_data, action):
    return quest_action_proof_completed_pure(player_data, PROOFS[action])


def _valid_quantity(value):
    return type(value) is int and value >= 0


def _active(player_data):
    state = quest_state_pure(player_data, QUEST_ID)
    return state["started"] and not state["completed"] and state["progress"] in (0, 1)


def _proof_error(player_data):
    total = player_data.get(MASS_KEY, 0)
    if not _valid_quantity(total) or total > TARGET_KG:
        return INCONSISTENT
    help_given, supplied, received, chiseled, talked, placed = (_proved(player_data, action) for action in _ORDER)
    if supplied != (total > 0) or received != (total == TARGET_KG):
        return INCONSISTENT
    if any((supplied and not help_given, received and not supplied, chiseled and not received,
            talked and not chiseled, placed and not talked)):
        return INCONSISTENT
    if any(_proved(player_data, action) and not help_given for action in ("split_10kg", "split_5kg", "split_2kg")):
        return INCONSISTENT
    return ""


def enakhra_opening_phase_pure(player_data):
    if not _active(player_data):
        return None
    if _proof_error(player_data):
        return "inconsistent"
    for action, phase in (("offer_help", "offer_help"), ("receive_32kg", "supply"),
                          ("chisel_base", "chisel_base"), ("talk_after_base", "talk_after_base"),
                          ("place_base", "place_base")):
        if not _proved(player_data, action):
            return phase
    return "placed"


def _expected_custody(player_data):
    if _proved(player_data, "place_base"):
        return 0, 0
    if _proved(player_data, "chisel_base"):
        return 0, 1
    return (1, 0) if _proved(player_data, "receive_32kg") else (0, 0)


def _custody_error(player_data):
    inventory = player_data.get("inventory", {})
    if not isinstance(inventory, Mapping):
        return INCONSISTENT
    names = (*[name for name, _ in SANDSTONE.values()], BLOCK, BASE, CHISEL)
    if any(not _valid_quantity(inventory.get(name, 0)) for name in names):
        return INCONSISTENT
    block, base = inventory.get(BLOCK, 0), inventory.get(BASE, 0)
    expected_block, expected_base = _expected_custody(player_data)
    if block > expected_block or base > expected_base:
        return INCONSISTENT
    if block < expected_block:
        return "Needs Lazim's 32kg sandstone block"
    if base < expected_base:
        return "Needs the sandstone base"
    return ""


def _has_chisel(player_data):
    return player_data.get("inventory", {}).get(CHISEL, 0) > 0 or tool_on_belt(player_data, CHISEL)


def _descriptor(action, item_id=None, mass=None, total=0, reason=""):
    return dict(action_id=action, event=("quest_service", EVENT_PREFIX + action),
                item_id=item_id, input_mass=mass,
                notice=reason or NOTICES.get(action, "").format(mass=mass, total=total))


def _select_supply(player_data):
    inventory = player_data.get("inventory", {})
    remaining = TARGET_KG - player_data.get(MASS_KEY, 0)
    for item_id in (6977, 6975, 6973, 6971):
        name, mass = SANDSTONE[item_id]
        if inventory.get(name, 0) > 0 and mass <= remaining:
            action = "receive_32kg" if mass == remaining else "deliver_sandstone"
            return _descriptor(action, item_id, mass, TARGET_KG - remaining + mass)
    for item_id in (6977, 6975, 6973):
        name, mass = SANDSTONE[item_id]
        if inventory.get(name, 0) > 0:
            reason = "" if _has_chisel(player_data) else "Needs Chisel"
            return _descriptor(f"split_{mass}kg", item_id, mass, reason=reason)
    return _descriptor("deliver_sandstone", reason=f"Needs sandstone: {remaining} kg still to give Lazim")


def enakhra_opening_next_action_pure(player_data):
    phase = enakhra_opening_phase_pure(player_data)
    if phase is None:
        state = quest_state_pure(player_data, QUEST_ID)
        return _descriptor("offer_help") if not state["started"] and not state["completed"] else None
    error = _proof_error(player_data) or _custody_error(player_data)
    if error:
        return _descriptor(_PHASE_ACTIONS.get(phase, ""), reason=error)
    if phase == "supply":
        return _select_supply(player_data)
    if phase == "chisel_base":
        return _descriptor(phase, BLOCK_ID, reason="" if _has_chisel(player_data) else "Needs Chisel")
    if phase == "place_base":
        return _descriptor(phase, BASE_ID)
    return _descriptor(phase) if phase in _PHASE_ACTIONS else None


def _delivery_plan(player_data, action, item_id):
    if type(item_id) is not int or item_id not in SANDSTONE:
        return None, "Select an ordinary sandstone block"
    name, mass = SANDSTONE[item_id]
    total = player_data.get(MASS_KEY, 0) + mass
    if player_data.get("inventory", {}).get(name, 0) < 1:
        return None, "Needs the selected sandstone block"
    if total > TARGET_KG:
        return None, "Lazim needs exactly 32 kg; this block would exceed it"
    if action == "receive_32kg" and total != TARGET_KG:
        return None, "Give Lazim exactly 32 kg before receiving his block"
    event = "receive_32kg" if total == TARGET_KG else "deliver_sandstone"
    outputs = ((BLOCK, 1),) if total == TARGET_KG else ()
    return (((name, 1),), outputs, total, _descriptor(event, item_id, mass, total)), ""


def _split_plan(player_data, action, item_id):
    expected_id = {"split_10kg": 6977, "split_5kg": 6975, "split_2kg": 6973}[action]
    if item_id is None:
        item_id = expected_id
    if type(item_id) is not int or item_id != expected_id:
        return None, "Select the matching ordinary sandstone block"
    name, mass = SANDSTONE[item_id]
    if player_data.get("inventory", {}).get(name, 0) < 1:
        return None, "Needs the selected sandstone block"
    if not _has_chisel(player_data):
        return None, "Needs Chisel"
    outputs = tuple((SANDSTONE[output_id][0], count) for output_id, count in SPLIT_OUTPUTS[item_id])
    return (((name, 1),), outputs, player_data.get(MASS_KEY, 0), _descriptor(action, item_id, mass)), ""


def _chisel_plan(player_data, action, item_id):
    if item_id is not None and (type(item_id) is not int or item_id != BLOCK_ID):
        return None, "Select Lazim's 32kg sandstone block"
    if not _has_chisel(player_data):
        return None, "Needs Chisel"
    return (((BLOCK, 1),), ((BASE, 1),), TARGET_KG, _descriptor(action, BLOCK_ID)), ""


def _place_plan(player_data, action, item_id):
    if item_id is not None and (type(item_id) is not int or item_id != BASE_ID):
        return None, "Select the sandstone base"
    return (((BASE, 1),), (), TARGET_KG, _descriptor(action, BASE_ID)), ""


def _conversation_plan(player_data, action, item_id):
    if item_id is not None:
        return None, "This conversation takes no item"
    return ((), (), player_data.get(MASS_KEY, 0), _descriptor(action)), ""


_PLANNERS = {"offer_help": _conversation_plan, "deliver_sandstone": _delivery_plan,
             "receive_32kg": _delivery_plan, "chisel_base": _chisel_plan,
             "talk_after_base": _conversation_plan, "place_base": _place_plan,
             **{f"split_{mass}kg": _split_plan for mass in (10, 5, 2)}}


def _action_error(player_data, action):
    phase = enakhra_opening_phase_pure(player_data)
    if phase is None:
        return "Lazim's opening is not active"
    error = _proof_error(player_data) or _custody_error(player_data)
    if error:
        return error
    expected = _PHASE_ACTIONS.get(phase)
    supply_action = action in ("deliver_sandstone", "receive_32kg", "split_10kg", "split_5kg", "split_2kg")
    if action == expected or (phase == "supply" and supply_action):
        return ""
    return "Complete the next opening action first"


def _exchange(candidate, inputs, outputs):
    inventory = candidate["inventory"]
    for name, count in inputs:
        inventory[name] -= count
    for name, count in outputs:
        inventory[name] = inventory.get(name, 0) + count


def apply_enakhra_opening_action_pure(player_data, action_id, item_id=None):
    action = action_id.removeprefix(EVENT_PREFIX) if isinstance(action_id, str) else ""
    error = _action_error(player_data, action)
    planner = _PLANNERS.get(action)
    if error or planner is None:
        return player_data, False, _descriptor(action, item_id, reason=error or "Unknown opening action")
    plan, error = planner(player_data, action, item_id)
    if error:
        return player_data, False, _descriptor(action, item_id, reason=error)
    inputs, outputs, total, descriptor = plan
    candidate = _copy_player_data_with_nested(player_data)
    _exchange(candidate, inputs, outputs)
    candidate[MASS_KEY] = total
    record_runtime_quest_action_proofs_pure(candidate, *descriptor["event"])
    return candidate, True, descriptor


def enakhra_opening_blockers_pure(player_data, quest_id=QUEST_ID):
    if quest_id != QUEST_ID or not _active(player_data):
        return ()
    descriptor = enakhra_opening_next_action_pure(player_data)
    if descriptor is None:
        return ()
    # Run only validation/planning: no copied candidate, exchange or proof recording.
    action, item_id = descriptor["action_id"], descriptor["item_id"]
    error = _action_error(player_data, action)
    if not error:
        _, error = _PLANNERS[action](player_data, action, item_id)
    if not error:
        return ()
    if action == "deliver_sandstone" and item_id is None and not _proof_error(player_data) and not _custody_error(player_data):
        error = descriptor["notice"]
    return (dict(stage=1, kind="opening_state", reason=error),)


def migrate_enakhra_opening_state(data):
    total = data.get(MASS_KEY, 0)
    data[MASS_KEY] = total if _valid_quantity(total) and total <= TARGET_KG else 0


def _performed_lines(player_data):
    lines = []
    for action in ("offer_help", "split_10kg", "split_5kg", "split_2kg"):
        if _proved(player_data, action):
            lines.append(NOTICES[action])
    # A boolean supply proof supports the neutral total, not the last input's mass or provenance.
    if _proved(player_data, "deliver_sandstone"):
        lines.append(f"Sandstone given to Lazim: {player_data.get(MASS_KEY, 0)}/32 kg.")
    if _proved(player_data, "receive_32kg"):
        lines.append("Lazim joined the sandstone into one 32kg block.")
    for action in ("chisel_base", "talk_after_base", "place_base"):
        if _proved(player_data, action):
            lines.append(NOTICES[action])
    for proof, sentence in (("Mine sandstone", "I have mined sandstone."), ("Mine coal", "I have mined coal.")):
        if quest_action_proof_completed_pure(player_data, proof):
            lines.append(sentence)
    return tuple(lines)


def enakhra_opening_journal_row_pure(player_data, quest_id, row):
    if quest_id != QUEST_ID or row["stage"] != 1:
        return row
    placed = _proved(player_data, "place_base")
    if not row["current"] and not placed:
        return dict(row, completed=False, current=False, lines=LEGACY_JOURNAL)
    deeds = _performed_lines(player_data)
    if placed:
        return dict(row, completed=True, lines=deeds)
    instructions = {
        "offer_help": "Offer to help Lazim.", "supply": "Supply the remaining sandstone to Lazim.",
        "chisel_base": "Chisel Lazim's 32kg sandstone block into a base.",
        "talk_after_base": "Talk to Lazim again about the sandstone base.",
        "place_base": "Place the base on the flat ground beside Lazim.",
        "inconsistent": INCONSISTENT,
    }
    context = tuple(row["lines"][:3]) + (
        "Supply 32 kg of sandstone to Lazim. Bring sandstone, or mine it in the quarry at Mining 35.",
        "Each quest review gives Lazim one block, using the largest block that fits. If none fits, a review splits an oversized block with your chisel.",
        instructions.get(enakhra_opening_phase_pure(player_data), "Offer to help Lazim."),
        "Mine 1 coal if you did not bring one; it is needed later.",
    )
    total = () if _proved(player_data, "deliver_sandstone") else (f"Sandstone given to Lazim: {player_data.get(MASS_KEY, 0)}/32 kg.",)
    return dict(row, lines=context + deeds + total)
