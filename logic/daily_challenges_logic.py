"""Pure Challenge System queue, credit, hand-in and reward mechanics.

The five-slot queue, the oldest-first displacement rule, and the decision about
whether a new challenge may arrive all live here and nowhere else. Panels render
the flags this module publishes through `daily_challenges_view_pure`; they never
re-derive the rule, because a copy of a stateful rule diverges the moment the
state does.
"""

from __future__ import annotations

import copy
from collections.abc import Callable, Mapping
from typing import Any

from ..logic_pure.logic_pure import player_combat_level_pure
from ..data.daily_challenges_data import (
    DAILY_CHALLENGE_ACTIVE_LIMIT,
    DAILY_CHALLENGE_DATA,
    DAILY_CHALLENGE_LAMP_SKILLS,
    DAILY_CHALLENGE_MYSTERY_BAG_ITEM,
    DAILY_CHALLENGE_REVIEW_DAY,
    DAILY_CHALLENGE_SKILL_EXP_KEYS,
    DAILY_CHALLENGE_SKILL_LABELS,
    DAILY_CHALLENGE_SKILL_LEVEL_KEYS,
    DAILY_CHALLENGE_XP_LAMP_ITEM,
    DAILY_CHALLENGES_SOURCE,
)


DAILY_CHALLENGES_STATE_VERSION = 1
MAX_SKILL_LEVEL = 99

_LAMP_EXP_KEYS = {skill_id: exp_key for skill_id, _label, exp_key in DAILY_CHALLENGE_LAMP_SKILLS}


def _int(value: Any, default: int = 0, *, minimum: int = 0, maximum: int = 2_147_483_647) -> int:
    if isinstance(value, bool):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(minimum, min(parsed, maximum))


def default_daily_challenges_state_pure() -> dict[str, Any]:
    return {
        "daily_challenges": [],
        "daily_challenge_day": 0,
        "daily_challenge_pinned": "",
        "daily_challenge_blocked_skills": [],
        "daily_challenge_bag_values": [],
        "daily_challenge_lamp_xp": [],
        "daily_challenge_assigned": 0,
        "daily_challenge_completed": 0,
        "daily_challenge_expired": 0,
        "daily_challenge_last_result": "",
    }


def _sanitize_instance(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        return {}
    challenge_id = str(raw.get("challenge_id", ""))
    spec = DAILY_CHALLENGE_DATA.get(challenge_id)
    if spec is None:
        return {}
    credited_raw = raw.get("credited")
    credited = {}
    if isinstance(credited_raw, Mapping):
        for item_name, quantity in credited_raw.items():
            amount = _int(quantity)
            if amount > 0:
                credited[str(item_name)[:80]] = amount
    day = _int(raw.get("day"))
    return {
        "instance_id": str(raw.get("instance_id", "") or f"{challenge_id}-{day}")[:80],
        "challenge_id": challenge_id,
        "day": day,
        "progress": _int(raw.get("progress"), maximum=int(spec["required"])),
        "credited": credited,
    }


def sanitize_daily_challenges_state_pure(player_data: Mapping[str, Any] | None) -> dict[str, Any]:
    source = dict(player_data or {})
    state = default_daily_challenges_state_pure()

    active: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in source.get("daily_challenges", ()) or ():
        instance = _sanitize_instance(row)
        if not instance or instance["instance_id"] in seen:
            continue
        seen.add(instance["instance_id"])
        active.append(instance)
    # A save that somehow carries more than the queue allows is repaired the way
    # the period repairs it: the oldest entries fall off the end.
    state["daily_challenges"] = active[-DAILY_CHALLENGE_ACTIVE_LIMIT:]

    state["daily_challenge_day"] = _int(source.get("daily_challenge_day"))
    pinned = str(source.get("daily_challenge_pinned", ""))[:80]
    state["daily_challenge_pinned"] = pinned if pinned in {
        row["instance_id"] for row in state["daily_challenges"]
    } else ""
    blocked = source.get("daily_challenge_blocked_skills")
    state["daily_challenge_blocked_skills"] = sorted(
        {
            str(skill_id)
            for skill_id in (blocked or ())
            if str(skill_id) in DAILY_CHALLENGE_SKILL_LABELS
        }
    )

    inventory = source.get("inventory")
    inventory = inventory if isinstance(inventory, Mapping) else {}
    # The reward items are ordinary inventory rows; their per-item values ride in
    # parallel lists, so the two must never disagree about how many exist.
    state["daily_challenge_bag_values"] = _clamp_reward_list(
        source.get("daily_challenge_bag_values"),
        _int(inventory.get(DAILY_CHALLENGE_MYSTERY_BAG_ITEM)),
    )
    state["daily_challenge_lamp_xp"] = _clamp_reward_list(
        source.get("daily_challenge_lamp_xp"),
        _int(inventory.get(DAILY_CHALLENGE_XP_LAMP_ITEM)),
    )

    state["daily_challenge_assigned"] = _int(source.get("daily_challenge_assigned"))
    state["daily_challenge_completed"] = _int(source.get("daily_challenge_completed"))
    state["daily_challenge_expired"] = _int(source.get("daily_challenge_expired"))
    state["daily_challenge_last_result"] = str(source.get("daily_challenge_last_result", ""))[:500]
    return state


def _clamp_reward_list(raw: Any, held: int) -> list[int]:
    values = [_int(value) for value in (raw or ()) if _int(value) > 0]
    return values[:held]


def _spec(instance: Mapping[str, Any]) -> dict[str, Any]:
    return DAILY_CHALLENGE_DATA[str(instance["challenge_id"])]


def _is_complete(instance: Mapping[str, Any]) -> bool:
    return int(instance["progress"]) >= int(_spec(instance)["required"])


def _skill_level(player_data: Mapping[str, Any], skill_id: str) -> int:
    if skill_id == "combat":
        return player_combat_level_pure(player_data)
    return _int(player_data.get(DAILY_CHALLENGE_SKILL_LEVEL_KEYS[skill_id]), 1, minimum=1)


def eligible_daily_challenge_ids_pure(player_data: Mapping[str, Any]) -> tuple[str, ...]:
    """The pool a new assignment is drawn from.

    "Challenges ... are always possible at your current skill levels", so a row
    the player cannot yet perform is never handed out. A skill the player has
    opted out of is excluded, and a challenge already sitting in the queue is not
    duplicated into a second slot.
    """
    state = sanitize_daily_challenges_state_pure(player_data)
    blocked = set(state["daily_challenge_blocked_skills"])
    held = {str(row["challenge_id"]) for row in state["daily_challenges"]}
    return tuple(
        challenge_id
        for challenge_id, spec in DAILY_CHALLENGE_DATA.items()
        if challenge_id not in held
        and str(spec["skill"]) not in blocked
        and _skill_level(player_data, str(spec["skill"])) >= int(spec["level"])
    )


def advance_daily_challenges_day_pure(
    player_data: Mapping[str, Any],
    rng: Callable[[], float] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Hand out one challenge per elapsed 240-answered-card day."""
    data = dict(player_data)
    state = sanitize_daily_challenges_state_pure(data)
    data.update(state)
    clock = data.get("shop_market_clock")
    answered = _int(clock.get("answered_cards")) if isinstance(clock, Mapping) else 0
    current_day = answered // DAILY_CHALLENGE_REVIEW_DAY
    last_day = int(state["daily_challenge_day"])
    if current_day <= last_day:
        return data, {"assigned": (), "expired": ()}

    draw = rng or (lambda: 0.0)
    # Only the newest few days can leave a mark: an older assignment would be
    # displaced by a newer one before the player ever saw it.
    first_day = max(last_day + 1, current_day - DAILY_CHALLENGE_ACTIVE_LIMIT + 1)
    active = [dict(row) for row in state["daily_challenges"]]
    pinned = str(state["daily_challenge_pinned"])
    assigned: list[dict[str, Any]] = []
    expired: list[dict[str, Any]] = []
    for day in range(first_day, current_day + 1):
        data["daily_challenges"] = active
        pool = eligible_daily_challenge_ids_pure(data)
        if not pool:
            continue
        # Cutoff oldid 6579729 states a one-in-four chance of the desired skill
        # when four skills remain, so task-rich skills must not gain extra
        # assignment weight. The selector uses one roll split into equal skill
        # intervals and then equal task intervals inside the chosen skill.
        skills = tuple(
            dict.fromkeys(str(DAILY_CHALLENGE_DATA[row]["skill"]) for row in pool)
        )
        roll = draw()
        skill_index = min(int(roll * len(skills)), len(skills) - 1)
        skill_pool = tuple(
            row
            for row in pool
            if str(DAILY_CHALLENGE_DATA[row]["skill"]) == skills[skill_index]
        )
        within_skill_roll = roll * len(skills) - skill_index
        # PLACEHOLDER(daily_challenges.within_skill_assignment_weights): the
        # period server selector would replace the uniform task distribution.
        challenge_id = skill_pool[
            min(int(within_skill_roll * len(skill_pool)), len(skill_pool) - 1)
        ]
        instance = {
            "instance_id": f"{challenge_id}-{day}",
            "challenge_id": challenge_id,
            "day": day,
            "progress": 0,
            "credited": {},
        }
        active.append(instance)
        assigned.append(instance)
        if len(active) > DAILY_CHALLENGE_ACTIVE_LIMIT:
            dropped = active.pop(0)
            expired.append(dropped)
            if pinned == dropped["instance_id"]:
                pinned = ""

    data["daily_challenges"] = active
    data["daily_challenge_day"] = current_day
    data["daily_challenge_pinned"] = pinned
    data["daily_challenge_assigned"] = int(state["daily_challenge_assigned"]) + len(assigned)
    data["daily_challenge_expired"] = int(state["daily_challenge_expired"]) + len(expired)
    if assigned:
        newest = _spec(assigned[-1])
        data["daily_challenge_last_result"] = (
            f"New Daily Challenge: {newest['name']} · {newest['task']}"
        )
    return data, {
        "assigned": tuple(assigned),
        "expired": tuple(expired),
    }


def _credit_amount(
    spec: Mapping[str, Any],
    skill_id: str,
    action_id: str,
    output_items: Mapping[str, int],
    kills: int,
    enemy_combat_level: int,
) -> dict[str, int]:
    """What this one gameplay outcome contributes, keyed by the item it credits.

    Non-item credit (a lit log, a kill) uses an empty key, because there is
    nothing to hand in for those rows.
    """
    credit = spec["credit"]
    kind = str(credit["kind"])
    if kind == "output_item":
        if skill_id != str(spec["skill"]):
            return {}
        return {
            item_name: int(quantity)
            for item_name, quantity in output_items.items()
            if item_name in credit["items"] and int(quantity) > 0
        }
    if kind == "action":
        if skill_id != str(spec["skill"]) or action_id not in credit["actions"]:
            return {}
        return {"": 1}
    if kind == "kill":
        if skill_id != "combat" or kills <= 0:
            return {}
        if enemy_combat_level < int(credit["minimum_combat_level"]):
            return {}
        return {"": kills}
    return {}


def credit_daily_challenge_progress_pure(
    player_data: Mapping[str, Any],
    skill_id: str,
    action_id: str,
    *,
    output_items: Mapping[str, int] | None = None,
    kills: int = 0,
    enemy_combat_level: int = 0,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Advance every active challenge this gameplay outcome counts toward."""
    data = dict(player_data)
    state = sanitize_daily_challenges_state_pure(data)
    if not state["daily_challenges"]:
        return data, {"credited": ()}
    data.update(state)
    outputs = {
        str(name): _int(quantity)
        for name, quantity in (output_items or {}).items()
    }
    active = [dict(row) for row in state["daily_challenges"]]
    credited = []
    for instance in active:
        spec = _spec(instance)
        if _is_complete(instance):
            continue
        gained = _credit_amount(
            spec, str(skill_id), str(action_id), outputs, _int(kills), _int(enemy_combat_level)
        )
        total = sum(gained.values())
        if total <= 0:
            continue
        remaining = int(spec["required"]) - int(instance["progress"])
        counted = min(total, remaining)
        instance["progress"] += counted
        instance["credited"] = dict(instance["credited"])
        # Only count the items the challenge actually absorbed, so a hand-in can
        # never demand more than the challenge credited.
        left = counted
        for item_name, quantity in gained.items():
            if left <= 0:
                break
            take = min(int(quantity), left)
            left -= take
            if item_name:
                instance["credited"][item_name] = instance["credited"].get(item_name, 0) + take
        credited.append(
            {
                "instance_id": instance["instance_id"],
                "name": spec["name"],
                "progress": instance["progress"],
                "required": int(spec["required"]),
                "completed": _is_complete(instance),
            }
        )
    if not credited:
        return data, {"credited": ()}
    data["daily_challenges"] = active
    return data, {"credited": tuple(credited)}


def _find(state: Mapping[str, Any], instance_id: str) -> dict[str, Any] | None:
    return next(
        (
            dict(row)
            for row in state["daily_challenges"]
            if str(row["instance_id"]) == str(instance_id)
        ),
        None,
    )


def pin_daily_challenge_pure(
    player_data: Mapping[str, Any], instance_id: str
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the challenge list is rebuilt from sanitized copies and
    # inventory is copied before any reward is paid.
    data = dict(player_data)
    state = sanitize_daily_challenges_state_pure(data)
    data.update(state)
    if not instance_id:
        data["daily_challenge_pinned"] = ""
        return data, True, {"message": "Unpinned the active task."}
    if _find(state, instance_id) is None:
        return data, False, {"reason": "That challenge is no longer on the noticeboard."}
    # "Only one task can be pinned at a time."
    data["daily_challenge_pinned"] = str(instance_id)
    return data, True, {"message": "Pinned the task.", "instance_id": str(instance_id)}


def set_daily_challenge_skill_block_pure(
    player_data: Mapping[str, Any], skill_id: str, blocked: bool
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: see pin_daily_challenge_pure.
    data = dict(player_data)
    state = sanitize_daily_challenges_state_pure(data)
    data.update(state)
    skill_id = str(skill_id)
    if skill_id not in DAILY_CHALLENGE_SKILL_LABELS:
        return data, False, {"reason": "The Quartermaster does not set challenges in that skill."}
    current = set(state["daily_challenge_blocked_skills"])
    if blocked:
        # "players may choose not to receive new challenges in their max level
        # skills. This is not a blanket turn off."
        if _skill_level(data, skill_id) < MAX_SKILL_LEVEL:
            return data, False, {
                "reason": (
                    f"The Quartermaster only blocks maxed skills. "
                    f"{DAILY_CHALLENGE_SKILL_LABELS[skill_id]} is not level {MAX_SKILL_LEVEL}."
                )
            }
        current.add(skill_id)
        message = f"No new {DAILY_CHALLENGE_SKILL_LABELS[skill_id]} challenges will be set."
    else:
        current.discard(skill_id)
        message = f"{DAILY_CHALLENGE_SKILL_LABELS[skill_id]} challenges will be set again."
    data["daily_challenge_blocked_skills"] = sorted(current)
    return data, True, {"message": message, "blocked_skills": sorted(current)}


def claim_daily_challenge_pure(
    player_data: Mapping[str, Any],
    instance_id: str,
    item_values: Mapping[str, int] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    """Hand a finished challenge in to the Quartermaster."""
    # Shallow on purpose: see pin_daily_challenge_pure.
    data = dict(player_data)
    state = sanitize_daily_challenges_state_pure(data)
    data.update(state)
    instance = _find(state, instance_id)
    if instance is None:
        return data, False, {"reason": "That challenge is no longer on the noticeboard."}
    spec = _spec(instance)
    if not _is_complete(instance):
        return data, False, {
            "reason": (
                f"{spec['name']} is only {instance['progress']}/{int(spec['required'])} done."
            )
        }

    inventory = data.get("inventory")
    inventory = copy.deepcopy(dict(inventory)) if isinstance(inventory, Mapping) else {}
    bag_value = 0
    if bool(spec["hand_in"]):
        missing = {
            item_name: quantity - _int(inventory.get(item_name))
            for item_name, quantity in instance["credited"].items()
            if _int(inventory.get(item_name)) < quantity
        }
        if missing:
            # The period Quartermaster recognises the work but still wants the
            # goods; the player can re-obtain them and come back.
            shortfall = ", ".join(
                f"{quantity} {item_name}" for item_name, quantity in sorted(missing.items())
            )
            return data, False, {
                "reason": f"The Quartermaster still needs the items: {shortfall} short.",
                "missing": missing,
            }
        values = item_values or {}
        for item_name, quantity in instance["credited"].items():
            inventory[item_name] = _int(inventory.get(item_name)) - quantity
            if inventory[item_name] <= 0:
                del inventory[item_name]
            # "your challenge bag will give back the amount of gold in
            # items/coins using current Grand Exchange prices"
            bag_value += _int(values.get(item_name)) * quantity

    reward_xp = int(spec["reward_xp"])
    rewards: dict[str, Any] = {"reward_xp": reward_xp}
    lamp = str(spec["skill"]) == "combat"
    bag_values = list(state["daily_challenge_bag_values"])
    lamp_xp = list(state["daily_challenge_lamp_xp"])
    if lamp:
        # "In cases where multiple skills are involved, such as with combat,
        # players may be given a Challenge XP Lamp from which to choose which
        # skill to earn experience in."
        inventory[DAILY_CHALLENGE_XP_LAMP_ITEM] = _int(inventory.get(DAILY_CHALLENGE_XP_LAMP_ITEM)) + 1
        lamp_xp.append(reward_xp)
        rewards["xp_lamp"] = reward_xp
    else:
        exp_key = DAILY_CHALLENGE_SKILL_EXP_KEYS[str(spec["skill"])]
        data[exp_key] = float(data.get(exp_key, 0.0) or 0.0) + reward_xp
        rewards["xp_rewards"] = {exp_key: float(reward_xp)}
    if bool(spec["hand_in"]):
        inventory[DAILY_CHALLENGE_MYSTERY_BAG_ITEM] = (
            _int(inventory.get(DAILY_CHALLENGE_MYSTERY_BAG_ITEM)) + 1
        )
        bag_values.append(bag_value)
        rewards["mystery_bag"] = bag_value

    remaining = [
        dict(row)
        for row in state["daily_challenges"]
        if str(row["instance_id"]) != str(instance_id)
    ]
    data["inventory"] = inventory
    data["daily_challenges"] = remaining
    data["daily_challenge_bag_values"] = bag_values
    data["daily_challenge_lamp_xp"] = lamp_xp
    data["daily_challenge_completed"] = int(state["daily_challenge_completed"]) + 1
    if str(state["daily_challenge_pinned"]) == str(instance_id):
        data["daily_challenge_pinned"] = ""
    message = f"{spec['name']} complete · +{reward_xp:,} bonus XP"
    if lamp:
        message += " · Challenge XP Lamp received"
    if bool(spec["hand_in"]):
        message += f" · Challenge Mystery Bag worth {bag_value:,} coins"
    data["daily_challenge_last_result"] = message
    rewards["message"] = message
    return data, True, rewards


def open_challenge_mystery_bag_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: see pin_daily_challenge_pure.
    data = dict(player_data)
    state = sanitize_daily_challenges_state_pure(data)
    data.update(state)
    values = list(state["daily_challenge_bag_values"])
    if not values:
        return data, False, {"reason": "You have no Challenge Mystery Bag to open."}
    coins = values.pop(0)
    inventory = copy.deepcopy(dict(data.get("inventory") or {}))
    held = _int(inventory.get(DAILY_CHALLENGE_MYSTERY_BAG_ITEM))
    if held <= 1:
        inventory.pop(DAILY_CHALLENGE_MYSTERY_BAG_ITEM, None)
    else:
        inventory[DAILY_CHALLENGE_MYSTERY_BAG_ITEM] = held - 1
    inventory["Coins"] = _int(inventory.get("Coins")) + coins
    data["inventory"] = inventory
    data["daily_challenge_bag_values"] = values
    message = f"The Challenge Mystery Bag held {coins:,} coins."
    data["daily_challenge_last_result"] = message
    return data, True, {"message": message, "coins": coins}


def rub_challenge_xp_lamp_pure(
    player_data: Mapping[str, Any], skill_id: str
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: see pin_daily_challenge_pure.
    data = dict(player_data)
    state = sanitize_daily_challenges_state_pure(data)
    data.update(state)
    exp_key = _LAMP_EXP_KEYS.get(str(skill_id))
    if exp_key is None:
        return data, False, {"reason": "A Challenge XP Lamp cannot be spent in that skill."}
    amounts = list(state["daily_challenge_lamp_xp"])
    if not amounts:
        return data, False, {"reason": "You have no Challenge XP Lamp to rub."}
    amount = amounts.pop(0)
    inventory = copy.deepcopy(dict(data.get("inventory") or {}))
    held = _int(inventory.get(DAILY_CHALLENGE_XP_LAMP_ITEM))
    if held <= 1:
        inventory.pop(DAILY_CHALLENGE_XP_LAMP_ITEM, None)
    else:
        inventory[DAILY_CHALLENGE_XP_LAMP_ITEM] = held - 1
    data[exp_key] = float(data.get(exp_key, 0.0) or 0.0) + amount
    data["inventory"] = inventory
    data["daily_challenge_lamp_xp"] = amounts
    label = next(label for candidate, label, _key in DAILY_CHALLENGE_LAMP_SKILLS if candidate == skill_id)
    message = f"The lamp granted {amount:,} {label} XP."
    data["daily_challenge_last_result"] = message
    return data, True, {"message": message, "xp_rewards": {exp_key: float(amount)}}


def apply_daily_challenges_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
    item_values: Mapping[str, int] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    body = payload if isinstance(payload, Mapping) else {}
    if action_id == "pin":
        return pin_daily_challenge_pure(player_data, str(body.get("instance_id", "")))
    if action_id == "claim":
        return claim_daily_challenge_pure(
            player_data, str(body.get("instance_id", "")), item_values
        )
    if action_id == "set_skill_block":
        return set_daily_challenge_skill_block_pure(
            player_data, str(body.get("skill_id", "")), bool(body.get("blocked"))
        )
    if action_id == "open_bag":
        return open_challenge_mystery_bag_pure(player_data)
    if action_id == "rub_lamp":
        return rub_challenge_xp_lamp_pure(player_data, str(body.get("skill_id", "")))
    # Shallow: an unrecognised action changes nothing, and the caller discards
    # this save because ok is False.
    return dict(player_data), False, {"reason": "Unknown Daily Challenge command."}


def daily_challenges_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    """Everything a panel needs, with every rule already decided here."""
    state = sanitize_daily_challenges_state_pure(player_data)
    inventory = player_data.get("inventory")
    inventory = inventory if isinstance(inventory, Mapping) else {}
    rows = []
    for instance in state["daily_challenges"]:
        spec = _spec(instance)
        complete = _is_complete(instance)
        missing = {}
        if complete and bool(spec["hand_in"]):
            missing = {
                item_name: quantity - _int(inventory.get(item_name))
                for item_name, quantity in instance["credited"].items()
                if _int(inventory.get(item_name)) < quantity
            }
        rows.append(
            {
                "instance_id": instance["instance_id"],
                "challenge_id": instance["challenge_id"],
                "name": spec["name"],
                "task": spec["task"],
                "skill": spec["skill"],
                "skill_label": DAILY_CHALLENGE_SKILL_LABELS[str(spec["skill"])],
                "progress": int(instance["progress"]),
                "required": int(spec["required"]),
                "complete": complete,
                "hand_in": bool(spec["hand_in"]),
                "reward_xp": int(spec["reward_xp"]),
                "pinned": str(state["daily_challenge_pinned"]) == instance["instance_id"],
                "can_claim": complete and not missing,
                "claim_blocked_reason": (
                    "The Quartermaster still needs the items: "
                    + ", ".join(
                        f"{quantity} {item_name}" for item_name, quantity in sorted(missing.items())
                    )
                )
                if missing
                else "",
            }
        )
    clock = player_data.get("shop_market_clock")
    answered = _int(clock.get("answered_cards")) if isinstance(clock, Mapping) else 0
    blocked = set(state["daily_challenge_blocked_skills"])
    return {
        **state,
        "rows": tuple(rows),
        "slots_used": len(rows),
        "slot_limit": DAILY_CHALLENGE_ACTIVE_LIMIT,
        # Whether a new challenge can arrive, and which slot it would displace,
        # are decided here so no panel has to reproduce the queue rule.
        "next_challenge_day": int(state["daily_challenge_day"]) + 1,
        "reviews_until_next_challenge": (
            (int(state["daily_challenge_day"]) + 1) * DAILY_CHALLENGE_REVIEW_DAY - answered
        ),
        "next_assignment_displaces": rows[0]["instance_id"] if len(rows) >= DAILY_CHALLENGE_ACTIVE_LIMIT else "",
        "next_assignment_displaces_name": rows[0]["name"] if len(rows) >= DAILY_CHALLENGE_ACTIVE_LIMIT else "",
        "eligible_challenge_count": len(eligible_daily_challenge_ids_pure(player_data)),
        "mystery_bags": len(state["daily_challenge_bag_values"]),
        "xp_lamps": len(state["daily_challenge_lamp_xp"]),
        "lamp_skills": tuple(
            (skill_id, label) for skill_id, label, _key in DAILY_CHALLENGE_LAMP_SKILLS
        ),
        "skill_blocks": tuple(
            {
                "skill_id": skill_id,
                "label": label,
                "blocked": skill_id in blocked,
                "can_block": _skill_level(player_data, skill_id) >= MAX_SKILL_LEVEL,
            }
            for skill_id, label in sorted(
                DAILY_CHALLENGE_SKILL_LABELS.items(), key=lambda row: row[1]
            )
        ),
        "source": DAILY_CHALLENGES_SOURCE,
    }
