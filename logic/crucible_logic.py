"""Pure Crucible entry gate, bounty fee, arena combat and Trophy bone shop."""

from __future__ import annotations

import copy
from collections.abc import Callable, Mapping
from typing import Any

from ..data.crucible_data import (
    CRUCIBLE_ABANDONMENT_FEE,
    CRUCIBLE_ACTIVITY_ID,
    CRUCIBLE_BONES_PER_KILL,
    CRUCIBLE_COMBAT_TARGET_ID,
    CRUCIBLE_COMBAT_TICKS,
    CRUCIBLE_CURRENCY,
    CRUCIBLE_INTERVAL_TICKS,
    CRUCIBLE_ACTIVE_TICKS,
    CRUCIBLE_LESSON_BONE_AWARD,
    CRUCIBLE_LESSONS,
    CRUCIBLE_MINIMUM_COMBAT_LEVEL,
    CRUCIBLE_POINTS_PER_CHAMPION_HIT,
    CRUCIBLE_POINTS_PER_KILL,
    CRUCIBLE_PVP_BOOST_CAPS,
    CRUCIBLE_RANKS,
    CRUCIBLE_RISK_EXPECTATION_BASE,
    CRUCIBLE_RISK_EXPECTATION_PER_LEVEL,
    CRUCIBLE_SOURCE,
    CRUCIBLE_SUPREME_HELM,
    CRUCIBLE_SUPREME_HELM_COST,
    CRUCIBLE_SUPREME_RANK_NAME,
    CRUCIBLE_SUPREME_TIER,
    CRUCIBLE_TARGET_LEVEL_OFFSETS,
    CRUCIBLE_TAUNTS,
    CRUCIBLE_TITLES,
    CRUCIBLE_UNLOCKS,
    CRUCIBLE_UNLOCKS_BY_ID,
    CRUCIBLE_UNRANKED_NAME,
    CRUCIBLE_UNRANKED_TIER,
)
from ..logic_pure.logic_pure import (
    apply_combat_burst_pure,
    combat_max_lifepoints_pure,
    player_combat_level_pure,
)

from .pace.world_clock import answered_cards_pure, calendar_ticks_pure
from .pace.world_events import event_in_play_pure, event_slot_tick_pure


CRUCIBLE_STATE_VERSION = 1
_LESSONS = frozenset(CRUCIBLE_LESSONS)
_TAUNT_IDS = frozenset(row.id for row in CRUCIBLE_TAUNTS)
_TITLE_IDS = frozenset(row.id for row in CRUCIBLE_TITLES)


def _int(
    value: Any,
    default: int = 0,
    *,
    minimum: int = 0,
    maximum: int = 2_147_483_647,
) -> int:
    if isinstance(value, bool):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(minimum, min(parsed, maximum))


def _empty_activity_session() -> dict[str, str]:
    return {"active_id": ""}


def _supreme_event_active(player_data: Mapping[str, Any]) -> bool:
    return (event_in_play_pure(player_data)
            and calendar_ticks_pure(player_data) - event_slot_tick_pure(player_data, CRUCIBLE_INTERVAL_TICKS)
            < CRUCIBLE_ACTIVE_TICKS)


def default_crucible_state_pure() -> dict[str, Any]:
    return {
        "crucible": {},
        "crucible_unlocks": (),
        "crucible_taunt": "",
        "crucible_title": "",
        "crucible_lessons_taken": (),
        "crucible_rank_points": 0,
        "crucible_best_tier": CRUCIBLE_UNRANKED_TIER,
        "crucible_supreme_champion": False,
        "crucible_visits": 0,
        "crucible_kills": 0,
        "crucible_deaths": 0,
        "crucible_abandons": 0,
        "crucible_bones_earned": 0,
        "crucible_fees_paid": 0,
        "crucible_fees_won": 0,
        "crucible_last_result": "",
    }


def crucible_rank_pure(points: Any) -> dict[str, Any]:
    """Map rank points onto the client's own tier list.

    Rev-727 script 6284 proves the tier list exactly; the point totals that
    promote between them are the registered
    `PLACEHOLDER(crucible.rank_point_thresholds)` in the data module.
    """
    total = _int(points)
    tier = CRUCIBLE_UNRANKED_TIER
    name = CRUCIBLE_UNRANKED_NAME
    minimum = 0
    for row_tier, row_name, row_minimum in CRUCIBLE_RANKS:
        if total >= row_minimum:
            tier, name, minimum = row_tier, row_name, row_minimum
    next_row = next(
        (row for row in CRUCIBLE_RANKS if row[2] > total),
        None,
    )
    return {
        "tier": tier,
        "name": name,
        "minimum_points": minimum,
        "next_tier": next_row[0] if next_row else None,
        "next_name": next_row[1] if next_row else CRUCIBLE_SUPREME_RANK_NAME,
        "points_remaining": max(0, next_row[2] - total) if next_row else 0,
        "top_of_ladder": next_row is None,
    }


def _string_tuple(raw: Any, allowed: frozenset[str]) -> tuple[str, ...]:
    if not isinstance(raw, (list, tuple)):
        return ()
    seen = [str(value) for value in raw if str(value) in allowed]
    return tuple(dict.fromkeys(seen))


def _sanitize_target(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        return {}
    target_id = str(raw.get("target_id", ""))[:80]
    level = _int(raw.get("combat_level"), 3, minimum=3, maximum=138)
    maximum = _target_stats(level)["hitpoints"]
    lifepoints = _int(raw.get("lifepoints"), maximum, maximum=maximum)
    if not target_id or lifepoints <= 0:
        return {}
    encounter = raw.get("encounter")
    return {
        "target_id": target_id,
        "display_name": str(
            raw.get("display_name", f"Crucible target (level {level})")
        )[:100],
        "combat_level": level,
        "lifepoints": lifepoints,
        "maximum_lifepoints": maximum,
        "encounter": (
            copy.deepcopy(dict(encounter))
            if isinstance(encounter, Mapping)
            else {}
        ),
    }


def _sanitize_session(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}
    target = _sanitize_target(raw.get("target"))
    if not target:
        return {}
    return {
        "version": CRUCIBLE_STATE_VERSION,
        "visit_number": _int(raw.get("visit_number"), 1, minimum=1),
        "review": _int(raw.get("review")),
        "target_number": _int(
            raw.get("target_number"), 1, minimum=1, maximum=1_000_000
        ),
        "target": target,
        "risk_escrow": _int(raw.get("risk_escrow")),
        "abandon_escrow": _int(raw.get("abandon_escrow")),
        "previous_combat_target": str(
            raw.get("previous_combat_target", "")
        )[:120],
        "boosts_clamped": bool(raw.get("boosts_clamped", False)),
        "event_card": _int(raw.get("event_card")),
        "event_tick": _int(raw.get("event_tick"), -1, minimum=-1),
        "is_champion": bool(raw.get("is_champion", False)),
    }


def sanitize_crucible_state_pure(
    player_data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = dict(player_data or {})
    defaults = default_crucible_state_pure()
    session = _sanitize_session(source.get("crucible"))
    active = source.get("activity_session")
    active_id = (
        str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    )
    if session and active_id not in {"", CRUCIBLE_ACTIVITY_ID}:
        session = {}
    unlocks = _string_tuple(
        source.get("crucible_unlocks"), frozenset(CRUCIBLE_UNLOCKS_BY_ID)
    )
    taunt = str(source.get("crucible_taunt", ""))
    title = str(source.get("crucible_title", ""))
    return {
        **defaults,
        "crucible": session,
        "crucible_unlocks": unlocks,
        # An active cosmetic the player never bought would be a UI row telling a
        # lie, so both selections are validated against what is owned.
        "crucible_taunt": taunt if taunt in unlocks and taunt in _TAUNT_IDS else "",
        "crucible_title": title if title in unlocks and title in _TITLE_IDS else "",
        "crucible_lessons_taken": _string_tuple(
            source.get("crucible_lessons_taken"), _LESSONS
        ),
        "crucible_rank_points": _int(source.get("crucible_rank_points")),
        "crucible_best_tier": _int(
            source.get("crucible_best_tier"),
            CRUCIBLE_UNRANKED_TIER,
            minimum=CRUCIBLE_UNRANKED_TIER,
            maximum=CRUCIBLE_SUPREME_TIER,
        ),
        "crucible_supreme_champion": bool(
            source.get("crucible_supreme_champion", False)
        ),
        "crucible_visits": _int(source.get("crucible_visits")),
        "crucible_kills": _int(source.get("crucible_kills")),
        "crucible_deaths": _int(source.get("crucible_deaths")),
        "crucible_abandons": _int(source.get("crucible_abandons")),
        "crucible_bones_earned": _int(source.get("crucible_bones_earned")),
        "crucible_fees_paid": _int(source.get("crucible_fees_paid")),
        "crucible_fees_won": _int(source.get("crucible_fees_won")),
        "crucible_last_result": str(
            source.get("crucible_last_result", "")
        )[:500],
    }


def _target_stats(combat_level: int) -> dict[str, int]:
    """A target is another player, so build its stats like a player's.

    `player_combat_level_pure` scores a balanced melee build at 1.15 times its
    shared level, so inverting that gives the level a rival of this combat level
    would actually carry.
    """
    core = max(1, min(99, round(combat_level / 1.15)))
    return {
        "attack": core,
        "strength": core,
        "defence": core,
        "hitpoints": max(100, core * 10),
        "magic": core,
        "ranged": core,
    }


def _new_target(
    player_data: Mapping[str, Any],
    visit_number: int,
    target_number: int,
) -> dict[str, Any]:
    offset = CRUCIBLE_TARGET_LEVEL_OFFSETS[
        (max(1, target_number) - 1) % len(CRUCIBLE_TARGET_LEVEL_OFFSETS)
    ]
    level = max(3, min(138, player_combat_level_pure(player_data) + offset))
    maximum = _target_stats(level)["hitpoints"]
    return {
        "target_id": f"crucible-{visit_number}-{target_number}",
        "display_name": f"Crucible target {target_number} (level {level})",
        "combat_level": level,
        "lifepoints": maximum,
        "maximum_lifepoints": maximum,
        "encounter": {},
    }


def _enemy_for(target: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    level = int(target["combat_level"])
    return {
        CRUCIBLE_COMBAT_TARGET_ID: {
            "display_name": str(target["display_name"]),
            "level": level,
            "group": "Crucible",
            "stats": _target_stats(level),
            "bonuses": {},
            "attack_style": "melee",
            "attack_speed": 4,
            "drops": {"guaranteed": (), "tables": ()},
            "xp_multiplier": 1.0,
            "source": CRUCIBLE_SOURCE + "; assigned bounty target",
        }
    }


def _coins(data: Mapping[str, Any]) -> int:
    inventory = data.get("inventory")
    return _int(inventory.get("Coins")) if isinstance(inventory, Mapping) else 0


def _adjust_stack(data: dict[str, Any], item: str, amount: int) -> None:
    inventory = (
        dict(data.get("inventory"))
        if isinstance(data.get("inventory"), Mapping)
        else {}
    )
    total = _int(inventory.get(item)) + amount
    if total > 0:
        inventory[item] = total
    else:
        inventory.pop(item, None)
    data["inventory"] = inventory


def _risked_pack(data: Mapping[str, Any]) -> dict[str, int]:
    carried = data.get("carried_inventory")
    pack = (
        carried.get(CRUCIBLE_COMBAT_TARGET_ID)
        if isinstance(carried, Mapping)
        else None
    )
    if not isinstance(pack, Mapping):
        return {}
    return {str(item): _int(count) for item, count in pack.items()}


def _crucible_expected_risk_pure(combat_level: int) -> int:
    return CRUCIBLE_RISK_EXPECTATION_BASE + max(
        0, combat_level - CRUCIBLE_MINIMUM_COMBAT_LEVEL
    ) * CRUCIBLE_RISK_EXPECTATION_PER_LEVEL


def crucible_fee_quote_pure(
    player_data: Mapping[str, Any],
    price_catalog: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, int]:
    """Quote the bounty fee exactly as interface 1298 states it: F = (X-Y) + Z.

    X is the risk expected of the player's combat level, Y is the value of what
    the player actually risks, and Z is the flat target-abandonment component.
    The rates behind X and Z are registered placeholders; the shape is sourced.
    """
    from .grand_exchange_logic import ge_guide_prices_pure

    level = player_combat_level_pure(player_data)
    expected_risk = _crucible_expected_risk_pure(level)
    risked: dict[str, int] = {}
    equipment = player_data.get("equipment")
    if isinstance(equipment, Mapping):
        for item in equipment.values():
            if isinstance(item, str) and item:
                risked[item] = risked.get(item, 0) + 1
    for item, count in _risked_pack(player_data).items():
        risked[item] = risked.get(item, 0) + count
    prices = (
        ge_guide_prices_pure(player_data, tuple(risked), price_catalog)
        if risked and price_catalog
        else {}
    )
    risked_value = sum(
        _int(prices.get(item)) * count for item, count in risked.items()
    )
    risk_component = max(0, expected_risk - risked_value)
    return {
        "expected_risk": expected_risk,
        "risked_value": risked_value,
        "risk_component": risk_component,
        "abandon_component": CRUCIBLE_ABANDONMENT_FEE,
        "total": risk_component + CRUCIBLE_ABANDONMENT_FEE,
    }


def _clamp_pvp_boosts(data: dict[str, Any]) -> bool:
    current = data.get("combat_current_levels")
    if not isinstance(current, Mapping):
        return False
    clamped = copy.deepcopy(dict(current))
    changed = False
    for skill_id, flat, multiplier in CRUCIBLE_PVP_BOOST_CAPS:
        base_key = (
            "defense_level" if skill_id == "defense" else f"{skill_id}_level"
        )
        base = max(1, _int(data.get(base_key), 1, minimum=1, maximum=99))
        maximum = base + flat + int(base * multiplier)
        if _int(clamped.get(skill_id), base, minimum=1) > maximum:
            clamped[skill_id] = maximum
            changed = True
    data["combat_current_levels"] = clamped
    return changed


def _copy_active_carried_pack(data: dict[str, Any], previous_target: str) -> None:
    carried = data.get("carried_inventory")
    if not isinstance(carried, Mapping):
        return
    source = carried.get(previous_target)
    if not isinstance(source, Mapping):
        return
    copied = copy.deepcopy(dict(carried))
    copied[CRUCIBLE_COMBAT_TARGET_ID] = copy.deepcopy(dict(source))
    data["carried_inventory"] = copied


def _remove_activity_carried_pack(data: dict[str, Any]) -> None:
    for key in ("carried_inventory", "carried_churn"):
        raw = data.get(key)
        if not isinstance(raw, Mapping) or CRUCIBLE_COMBAT_TARGET_ID not in raw:
            continue
        copied = copy.deepcopy(dict(raw))
        copied.pop(CRUCIBLE_COMBAT_TARGET_ID, None)
        data[key] = copied


def _finish(
    data: dict[str, Any],
    session: Mapping[str, Any],
    message: str,
) -> None:
    data["crucible"] = {}
    data["activity_session"] = _empty_activity_session()
    data["combat_encounter"] = {}
    data["current_combat_target"] = str(
        session.get("previous_combat_target", "")
    )
    data["crucible_last_result"] = message
    _remove_activity_carried_pack(data)


def _record_best_tier(data: dict[str, Any], tier: int) -> None:
    if tier > _int(
        data.get("crucible_best_tier"),
        CRUCIBLE_UNRANKED_TIER,
        minimum=CRUCIBLE_UNRANKED_TIER,
    ):
        data["crucible_best_tier"] = tier


def take_crucible_lesson_pure(
    player_data: Mapping[str, Any],
    lesson: str,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    """The four lessons are the only bone route that needs no defeated target.

    They are also the whole of what a player under the combat gate can reach,
    which is why they are not themselves gated on combat level.
    """
    data = copy.deepcopy(dict(player_data))
    state = sanitize_crucible_state_pure(data)
    if state["crucible"]:
        return data, False, {"reason": "Leave the arena before taking a lesson."}
    if lesson not in _LESSONS:
        return data, False, {"reason": "Unknown Crucible lesson."}
    if lesson in state["crucible_lessons_taken"]:
        return data, False, {"reason": f"You have already taken {lesson}."}
    data.update(state)
    data["crucible_lessons_taken"] = state["crucible_lessons_taken"] + (lesson,)
    _adjust_stack(data, CRUCIBLE_CURRENCY, CRUCIBLE_LESSON_BONE_AWARD)
    data["crucible_bones_earned"] = (
        state["crucible_bones_earned"] + CRUCIBLE_LESSON_BONE_AWARD
    )
    message = (
        f"Took the {lesson} lesson for {CRUCIBLE_LESSON_BONE_AWARD} "
        f"{CRUCIBLE_CURRENCY}."
    )
    data["crucible_last_result"] = message
    return data, True, {"message": message, "lesson": lesson}


def buy_crucible_unlock_pure(
    player_data: Mapping[str, Any],
    unlock_id: str,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_crucible_state_pure(data)
    unlock = CRUCIBLE_UNLOCKS_BY_ID.get(unlock_id)
    if unlock is None:
        return data, False, {"reason": "Unknown Crucible reward."}
    if unlock_id in state["crucible_unlocks"]:
        return data, False, {"reason": f"You already own {unlock.display_name}."}
    inventory = data.get("inventory")
    held = (
        _int(inventory.get(CRUCIBLE_CURRENCY))
        if isinstance(inventory, Mapping)
        else 0
    )
    if held < unlock.cost:
        return data, False, {
            "reason": (
                f"{unlock.display_name} costs {unlock.cost} "
                f"{CRUCIBLE_CURRENCY}; you have {held}."
            )
        }
    data.update(state)
    _adjust_stack(data, CRUCIBLE_CURRENCY, -unlock.cost)
    data["crucible_unlocks"] = state["crucible_unlocks"] + (unlock_id,)
    message = f"Bought {unlock.display_name} for {unlock.cost} {CRUCIBLE_CURRENCY}."
    data["crucible_last_result"] = message
    return data, True, {"message": message, "unlock_id": unlock_id}


def buy_crucible_supreme_helm_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_crucible_state_pure(data)
    if not state["crucible_supreme_champion"]:
        return data, False, {
            "reason": (
                "The helm is sold only to someone who has been Supreme "
                "Champion at least once."
            )
        }
    inventory = data.get("inventory") if isinstance(data.get("inventory"), Mapping) else {}
    if _int(inventory.get(CRUCIBLE_SUPREME_HELM)):
        return data, False, {"reason": f"You already own the {CRUCIBLE_SUPREME_HELM}."}
    held = _int(inventory.get(CRUCIBLE_CURRENCY))
    if held < CRUCIBLE_SUPREME_HELM_COST:
        return data, False, {
            "reason": (
                f"The helm costs {CRUCIBLE_SUPREME_HELM_COST} "
                f"{CRUCIBLE_CURRENCY}; you have {held}."
            )
        }
    data.update(state)
    _adjust_stack(data, CRUCIBLE_CURRENCY, -CRUCIBLE_SUPREME_HELM_COST)
    _adjust_stack(data, CRUCIBLE_SUPREME_HELM, 1)
    message = (
        f"Bought the {CRUCIBLE_SUPREME_HELM} for "
        f"{CRUCIBLE_SUPREME_HELM_COST} {CRUCIBLE_CURRENCY}."
    )
    data["crucible_last_result"] = message
    return data, True, {"message": message}


def set_crucible_cosmetic_pure(
    player_data: Mapping[str, Any],
    kind: str,
    unlock_id: str,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_crucible_state_pure(data)
    if kind not in {"taunt", "title"}:
        return data, False, {"reason": "Unknown Crucible cosmetic."}
    if unlock_id and unlock_id not in state["crucible_unlocks"]:
        return data, False, {"reason": "Buy that reward before selecting it."}
    unlock = CRUCIBLE_UNLOCKS_BY_ID.get(unlock_id)
    if unlock_id and (unlock is None or unlock.kind != kind):
        return data, False, {"reason": f"That reward is not a death {kind}."}
    data.update(state)
    data[f"crucible_{kind}"] = unlock_id
    message = (
        f"Death {kind} set to {unlock.display_name}."
        if unlock
        else f"Death {kind} cleared."
    )
    data["crucible_last_result"] = message
    return data, True, {"message": message, "kind": kind, "unlock_id": unlock_id}


def enter_crucible_pure(
    player_data: Mapping[str, Any],
    price_catalog: Mapping[str, Mapping[str, Any]] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_crucible_state_pure(data)
    if state["crucible"]:
        return data, False, {"reason": "You are already in the arena."}
    active = data.get("activity_session")
    active_id = (
        str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    )
    if active_id and active_id != CRUCIBLE_ACTIVITY_ID:
        return data, False, {
            "reason": "Finish the active persistent activity first."
        }
    encounter = data.get("combat_encounter")
    if isinstance(encounter, Mapping) and encounter:
        return data, False, {
            "reason": "Finish or leave the current Combat encounter first."
        }
    level = player_combat_level_pure(data)
    if level < CRUCIBLE_MINIMUM_COMBAT_LEVEL:
        return data, False, {
            "reason": (
                f"Full participation needs combat level "
                f"{CRUCIBLE_MINIMUM_COMBAT_LEVEL}; you are {level}. The "
                f"lessons and the waiting room are still open to you."
            )
        }
    quote = crucible_fee_quote_pure(data, price_catalog)
    if _coins(data) < quote["total"]:
        return data, False, {
            "reason": (
                f"The bounty fee is {quote['total']} coins; you have "
                f"{_coins(data)}."
            ),
            "fee": quote,
        }

    visit_number = state["crucible_visits"] + 1
    previous_target = str(data.get("current_combat_target", ""))[:120]
    target = _new_target(data, visit_number, 1)
    boosts_clamped = _clamp_pvp_boosts(data)
    session = {
        "version": CRUCIBLE_STATE_VERSION,
        "visit_number": visit_number,
        "review": 0,
        "target_number": 1,
        "target": target,
        "risk_escrow": quote["risk_component"],
        "abandon_escrow": quote["abandon_component"],
        "previous_combat_target": previous_target,
        "boosts_clamped": boosts_clamped,
        "event_card": 0,
        "is_champion": False,
    }
    data.update(state)
    _adjust_stack(data, "Coins", -quote["total"])
    data["crucible_visits"] = visit_number
    data["crucible_fees_paid"] = state["crucible_fees_paid"] + quote["total"]
    data["crucible"] = session
    data["activity_session"] = {"active_id": CRUCIBLE_ACTIVITY_ID}
    data["current_utility"] = CRUCIBLE_ACTIVITY_ID
    data["combat_encounter"] = {}
    _copy_active_carried_pack(data, previous_target)
    data["current_combat_target"] = CRUCIBLE_COMBAT_TARGET_ID
    message = (
        f"Paid a {quote['total']} coin bounty fee and entered the arena "
        f"against {target['display_name']}."
    )
    if boosts_clamped:
        message += " Extreme or Overload boosts were reduced to super-potion caps."
    data["crucible_last_result"] = message
    return data, True, {
        "message": message,
        "fee": quote,
        "boosts_clamped": boosts_clamped,
    }


def _replace_target(data: dict[str, Any], session: dict[str, Any]) -> None:
    session["target_number"] += 1
    session["target"] = _new_target(
        data, session["visit_number"], session["target_number"]
    )
    data["combat_encounter"] = {}


def _restore_safe_resources(data: dict[str, Any]) -> None:
    data["combat_lifepoints"] = combat_max_lifepoints_pure(data)
    data["combat_prayer_points"] = max(
        1, _int(data.get("prayer_level"), 1, minimum=1)
    ) * 10
    data["combat_status_effects"] = {}


def _held_item_count(data: Mapping[str, Any], pack_items: Mapping[str, int]) -> int:
    equipment = data.get("equipment")
    worn = (
        sum(1 for item in equipment.values() if isinstance(item, str))
        if isinstance(equipment, Mapping)
        else 0
    )
    inventory = data.get("inventory")
    banked = (
        sum(_int(inventory.get(item)) for item in pack_items)
        if isinstance(inventory, Mapping)
        else 0
    )
    return worn + banked


def apply_crucible_review_pure(
    player_data: Mapping[str, Any],
    rng: Callable[[], float] | None = None,
    *,
    equipment_data: Mapping[str, Any] | None = None,
    productive: bool = True,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_crucible_state_pure(data)
    session = state["crucible"]
    active = data.get("activity_session")
    active_id = (
        str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    )
    if not session or active_id != CRUCIBLE_ACTIVITY_ID:
        return data, False, {"reason": "Enter the Crucible arena before training it."}
    data.update(state)
    # The half-hourly event belongs to the shared answered-card world clock. It
    # must not pause while the player trains elsewhere or restart on re-entry.
    in_event = _supreme_event_active(data)
    rank = crucible_rank_pure(data.get("crucible_rank_points"))
    world_card = event_slot_tick_pure(data, CRUCIBLE_INTERVAL_TICKS)
    if in_event and session.get("event_tick", -1) != world_card:
        session["event_card"] = answered_cards_pure(data)
        session["event_tick"] = world_card
        session["is_champion"] = bool(rank["top_of_ladder"])
    elif not in_event:
        session["event_card"] = 0
        session["is_champion"] = False
    is_champion = in_event and bool(session["is_champion"])
    if is_champion:
        data["crucible_supreme_champion"] = True
        _record_best_tier(data, CRUCIBLE_SUPREME_TIER)
    data["crucible"] = session

    if not productive:
        return data, True, {
            "advanced": False,
            "terminal": False,
            "message": "The Crucible advances only on an eligible successful review.",
        }

    session["review"] += 1
    review = session["review"]

    target = session["target"]
    risked_pack = _risked_pack(data) if not in_event else {}
    held_before = _held_item_count(data, risked_pack) if not in_event else 0

    data["current_combat_target"] = CRUCIBLE_COMBAT_TARGET_ID
    encounter = copy.deepcopy(target["encounter"])
    encounter["target_id"] = CRUCIBLE_COMBAT_TARGET_ID
    encounter["enemy_lifepoints"] = int(target["lifepoints"])
    data["combat_encounter"] = encounter
    original_auto_flee = bool(data.get("combat_auto_flee", True))
    data["combat_auto_flee"] = False
    # Both pinned revisions state that Protect Item prayers and curses are
    # disabled inside the Crucible, so the arena must not honour a selection the
    # player made outside it. The selection itself is left untouched.
    original_prayers = data.get("combat_selected_prayers")
    if isinstance(original_prayers, (list, tuple)):
        data["combat_selected_prayers"] = [
            prayer for prayer in original_prayers if prayer != "protect_item"
        ]
    data, ok, combat = apply_combat_burst_pure(
        data,
        _enemy_for(target),
        equipment_data or {},
        ticks=CRUCIBLE_COMBAT_TICKS,
        rng=rng or (lambda: 0.5),
        live_cadence=True,
        stop_after_first_kill=True,
        safe_death=in_event,
        no_grave=not in_event,
        allow_bank_run=False,
    )
    data["combat_auto_flee"] = original_auto_flee
    if isinstance(original_prayers, (list, tuple)):
        data["combat_selected_prayers"] = list(original_prayers)
    if not ok:
        return copy.deepcopy(dict(player_data)), False, {
            "reason": "Crucible combat setup is not runnable.",
            "combat": combat,
        }

    bones = 0
    points_gained = 0
    events: list[str] = []
    if combat.get("died"):
        data["crucible_deaths"] = state["crucible_deaths"] + 1
        if in_event:
            # The event arena is safe, so a death costs nothing and the visit
            # continues against a fresh target.
            _restore_safe_resources(data)
            _replace_target(data, session)
        else:
            destroyed = max(0, held_before - _held_item_count(data, risked_pack))
            forfeited = int(session["risk_escrow"])
            session["risk_escrow"] = 0
            refund = int(session["abandon_escrow"])
            session["abandon_escrow"] = 0
            _adjust_stack(data, "Coins", refund)
            message = (
                f"Killed in the arena. {destroyed} item"
                f"{'' if destroyed == 1 else 's'} destroyed with no grave, "
                f"{forfeited} coins of the bounty fee paid to the victor, and "
                f"{refund} coins returned at the arena bank."
            )
            data["crucible"] = session
            _finish(data, session, message)
            return data, True, {
                "advanced": True,
                "terminal": True,
                "outcome": "death",
                "combat": combat,
                "destroyed_items": destroyed,
                "fee_forfeited": forfeited,
                "fee_refunded": refund,
                "events": (),
                "message": message,
            }
    elif combat.get("killed"):
        data["crucible_kills"] = state["crucible_kills"] + 1
        defeated = str(target["display_name"])
        # The taunts and titles the shop sells are death labels applied to the
        # target you just beat. A cosmetic nobody ever sees is a purchase that
        # does nothing, so both are rendered here.
        title = CRUCIBLE_UNLOCKS_BY_ID.get(state["crucible_title"])
        if title is not None:
            events.append(title.display_name.replace("[name]", defeated))
        taunt = CRUCIBLE_UNLOCKS_BY_ID.get(state["crucible_taunt"])
        if taunt is not None:
            events.append(f"You play {taunt.display_name}.")
        bones = CRUCIBLE_BONES_PER_KILL
        points_gained = CRUCIBLE_POINTS_PER_KILL
        _adjust_stack(data, CRUCIBLE_CURRENCY, bones)
        data["crucible_bones_earned"] = state["crucible_bones_earned"] + bones
        # The defeated player's variable fee component is paid to the victor.
        # A target's own risk expectation follows its combat level, the same
        # way the player's does.
        won = _crucible_expected_risk_pure(int(target["combat_level"]))
        _adjust_stack(data, "Coins", won)
        data["crucible_fees_won"] = state["crucible_fees_won"] + won
        _replace_target(data, session)
    else:
        encounter_after = data.get("combat_encounter")
        if isinstance(encounter_after, Mapping):
            target["lifepoints"] = _int(
                encounter_after.get("enemy_lifepoints"),
                int(target["lifepoints"]),
                maximum=int(target["maximum_lifepoints"]),
            )
            target["encounter"] = copy.deepcopy(dict(encounter_after))

    # Exact: each successful hit on the Supreme Champion is worth one rank
    # point. A review is the smallest unit at which the engine reports damage,
    # so it is the hit granularity AnkiScape has to offer.
    if in_event and not is_champion and int(combat.get("player_damage") or 0):
        points_gained += CRUCIBLE_POINTS_PER_CHAMPION_HIT
    data["crucible_rank_points"] = (
        state["crucible_rank_points"] + points_gained
    )
    rank = crucible_rank_pure(data["crucible_rank_points"])
    if not is_champion:
        _record_best_tier(data, int(rank["tier"]))

    data["crucible"] = session
    parts = [
        f"Arena review {review} · {rank['name']} on "
        f"{int(data['crucible_rank_points'])} pts"
    ]
    if bones:
        parts.append(f"+{bones} {CRUCIBLE_CURRENCY}")
    if in_event:
        parts.append(
            "You are the Supreme Champion; the arena is safe."
            if is_champion
            else "A Supreme Champion event has started; the arena is safe."
        )
    parts.extend(events)
    data["crucible_last_result"] = " · ".join(parts)
    return data, True, {
        "advanced": True,
        "terminal": False,
        "combat": combat,
        "bones": bones,
        "points": int(data["crucible_rank_points"]),
        "points_gained": points_gained,
        "rank": rank,
        "event_active": in_event,
        "is_champion": is_champion,
        "events": tuple(events),
        "message": data["crucible_last_result"],
    }


def leave_crucible_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_crucible_state_pure(data)
    session = state["crucible"]
    if not session:
        return data, False, {"reason": "You are not in the Crucible arena."}
    data.update(state)
    # Leaving while a bounty target is live is abandonment, so the flat Z
    # component goes to the opponent and the rest comes back at the bank.
    forfeited = int(session["abandon_escrow"])
    refund = int(session["risk_escrow"])
    _adjust_stack(data, "Coins", refund)
    data["crucible_abandons"] = state["crucible_abandons"] + 1
    message = (
        f"Abandoned {session['target']['display_name']} on "
        f"{state['crucible_rank_points']} rank points. {forfeited} coins went to the "
        f"opponent and {refund} coins came back at the arena bank."
    )
    _finish(data, session, message)
    return data, True, {
        "message": message,
        "outcome": "abandon",
        "fee_forfeited": forfeited,
        "fee_refunded": refund,
    }


def apply_crucible_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    body = payload if isinstance(payload, Mapping) else {}
    if action_id == "take_lesson":
        return take_crucible_lesson_pure(player_data, str(body.get("lesson", "")))
    if action_id == "buy_unlock":
        return buy_crucible_unlock_pure(player_data, str(body.get("unlock_id", "")))
    if action_id == "buy_supreme_helm":
        return buy_crucible_supreme_helm_pure(player_data)
    if action_id == "set_taunt":
        return set_crucible_cosmetic_pure(
            player_data, "taunt", str(body.get("unlock_id", ""))
        )
    if action_id == "set_title":
        return set_crucible_cosmetic_pure(
            player_data, "title", str(body.get("unlock_id", ""))
        )
    if action_id == "enter":
        return enter_crucible_pure(player_data, body.get("price_catalog"))
    if action_id == "leave":
        return leave_crucible_pure(player_data)
    return copy.deepcopy(dict(player_data)), False, {
        "reason": "Unknown Crucible command."
    }


def crucible_view_pure(
    player_data: Mapping[str, Any],
    price_catalog: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Own every enable, visibility and warning decision the panel renders.

    The panel is a renderer: it reads these flags and never re-derives a rule.
    A UI-side copy of the combat gate or the fee could offer an entry the logic
    refuses, or hide a risk that is real.
    """
    state = sanitize_crucible_state_pure(player_data)
    session = state["crucible"]
    active = player_data.get("activity_session")
    active_id = (
        str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    )
    encounter = player_data.get("combat_encounter")
    inventory = player_data.get("inventory")
    bones = (
        _int(inventory.get(CRUCIBLE_CURRENCY))
        if isinstance(inventory, Mapping)
        else 0
    )
    combat_level = player_combat_level_pure(player_data)
    quote = crucible_fee_quote_pure(player_data, price_catalog)
    reasons: list[str] = []
    if active_id and active_id != CRUCIBLE_ACTIVITY_ID:
        reasons.append("Finish the active persistent activity.")
    if not session and isinstance(encounter, Mapping) and encounter:
        reasons.append("Finish or leave the current Combat encounter.")
    if combat_level < CRUCIBLE_MINIMUM_COMBAT_LEVEL:
        reasons.append(
            f"Full participation needs combat level "
            f"{CRUCIBLE_MINIMUM_COMBAT_LEVEL}; you are {combat_level}."
        )
    if _coins(player_data) < quote["total"]:
        reasons.append(f"The bounty fee is {quote['total']} coins.")
    can_enter = not reasons and not session
    in_event = bool(session) and _supreme_event_active(player_data)
    rank = crucible_rank_pure(state["crucible_rank_points"])
    if session:
        summary = (
            f"{session['target']['display_name']} · {rank['name']} on "
            f"{int(state['crucible_rank_points'])} rank points"
        )
    else:
        summary = state["crucible_last_result"] or (
            f"{state['crucible_kills']} defeated · {state['crucible_deaths']} "
            f"deaths · {bones} {CRUCIBLE_CURRENCY}"
        )
    selected_for_reviews = (
        str(player_data.get("current_utility", "")) == CRUCIBLE_ACTIVITY_ID
    )
    return {
        **state,
        "active": bool(session),
        "can_enter": can_enter,
        "entry_reasons": tuple(reasons),
        "combat_level": combat_level,
        "minimum_combat_level": CRUCIBLE_MINIMUM_COMBAT_LEVEL,
        "bones": bones,
        "fee": quote,
        "rank": rank,
        "event_active": in_event,
        "is_champion": bool(in_event and session and session["is_champion"]),
        "dangerous": not in_event,
        "status_label": (
            "ACTIVE · SAFE EVENT"
            if in_event
            else "ACTIVE · DANGEROUS"
            if session
            else "DANGEROUS"
        ),
        "entry_warning": (
            "Death here destroys every carried and worn item. There is no "
            "gravestone, no Death's Office recovery, and Protect Item is "
            "disabled. The risk part of your bounty fee goes to the victor."
            if can_enter
            else ""
        ),
        "summary_text": summary,
        "progress_value": int(state["crucible_rank_points"]),
        "progress_maximum": max(1, CRUCIBLE_RANKS[-1][2]),
        "progress_format": (
            f"{int(state['crucible_rank_points'])} rank points · {rank['name']}"
        ),
        "primary_label": (
            "Active for reviews"
            if session and selected_for_reviews
            else "Select for reviews"
            if session
            else "Pay fee and enter"
        ),
        "primary_enabled": (
            bool(session) and not selected_for_reviews
        ) or can_enter,
        "leave_visible": bool(session),
        "lesson_options": tuple(
            {
                "lesson": lesson,
                "taken": lesson in state["crucible_lessons_taken"],
                "award": CRUCIBLE_LESSON_BONE_AWARD,
                "enabled": (
                    lesson not in state["crucible_lessons_taken"]
                    and not session
                ),
            }
            for lesson in CRUCIBLE_LESSONS
        ),
        "shop_options": tuple(
            {
                "id": row.id,
                "kind": row.kind,
                "display_name": row.display_name,
                "cost": row.cost,
                "owned": row.id in state["crucible_unlocks"],
                "affordable": bones >= row.cost,
                "enabled": (
                    row.id not in state["crucible_unlocks"] and bones >= row.cost
                ),
            }
            for row in CRUCIBLE_UNLOCKS
        ),
        "supreme_helm": {
            "item_name": CRUCIBLE_SUPREME_HELM,
            "cost": CRUCIBLE_SUPREME_HELM_COST,
            "unlocked": state["crucible_supreme_champion"],
            "owned": bool(
                _int(inventory.get(CRUCIBLE_SUPREME_HELM))
                if isinstance(inventory, Mapping)
                else 0
            ),
            "enabled": (
                state["crucible_supreme_champion"]
                and bones >= CRUCIBLE_SUPREME_HELM_COST
                and not (
                    _int(inventory.get(CRUCIBLE_SUPREME_HELM))
                    if isinstance(inventory, Mapping)
                    else 0
                )
            ),
            "reason": (
                ""
                if state["crucible_supreme_champion"]
                else "Be named Supreme Champion at least once."
            ),
        },
        "shop_controls_enabled": not session,
        "source": CRUCIBLE_SOURCE,
    }
