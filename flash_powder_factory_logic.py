"""Pure Flash Powder Factory session, reward, and outfit mechanics."""

from __future__ import annotations

import copy
import math
from typing import Any, Mapping, Sequence

try:
    from .agility_data import DEFAULT_AGILITY_TARGET
    from .flash_powder_factory_data import (
        FLASH_POWDER_FACTORY_ACTIVITY_ID,
        FLASH_POWDER_FACTORY_APPARATUS_POLICIES,
        FLASH_POWDER_FACTORY_BASE_APPARATUS,
        FLASH_POWDER_FACTORY_BASE_CATALYST,
        FLASH_POWDER_FACTORY_BASE_SLOTS,
        FLASH_POWDER_FACTORY_EXTENDED_SLOTS,
        FLASH_POWDER_FACTORY_LONG_STAY_BONUS,
        FLASH_POWDER_FACTORY_MASK_RUBBLE_WEIGHTS,
        FLASH_POWDER_FACTORY_MAX_APPARATUS,
        FLASH_POWDER_FACTORY_MAX_BRIANPOINTS,
        FLASH_POWDER_FACTORY_OUTFIT,
        FLASH_POWDER_FACTORY_REWARD_COSTS,
        FLASH_POWDER_FACTORY_ROGUE_OUTFIT,
        FLASH_POWDER_FACTORY_RUBBLE_WEIGHTS,
        FLASH_POWDER_FACTORY_STRATEGIES,
        FLASH_POWDER_FACTORY_TROUSERS_CATALYST,
        FLASH_POWDER_FACTORY_XP_LOTS,
        FLASH_POWDER_FACTORY_XP_PER_POINT,
        ROGUE_KIT_OUTPUTS,
    )
    from .pet_logic import store_active_pet_pure
    from .summoning_logic import dismiss_familiar_pure
except ImportError:  # pragma: no cover - flat test imports
    from agility_data import DEFAULT_AGILITY_TARGET  # type: ignore
    from flash_powder_factory_data import (  # type: ignore
        FLASH_POWDER_FACTORY_ACTIVITY_ID,
        FLASH_POWDER_FACTORY_APPARATUS_POLICIES,
        FLASH_POWDER_FACTORY_BASE_APPARATUS,
        FLASH_POWDER_FACTORY_BASE_CATALYST,
        FLASH_POWDER_FACTORY_BASE_SLOTS,
        FLASH_POWDER_FACTORY_EXTENDED_SLOTS,
        FLASH_POWDER_FACTORY_LONG_STAY_BONUS,
        FLASH_POWDER_FACTORY_MASK_RUBBLE_WEIGHTS,
        FLASH_POWDER_FACTORY_MAX_APPARATUS,
        FLASH_POWDER_FACTORY_MAX_BRIANPOINTS,
        FLASH_POWDER_FACTORY_OUTFIT,
        FLASH_POWDER_FACTORY_REWARD_COSTS,
        FLASH_POWDER_FACTORY_ROGUE_OUTFIT,
        FLASH_POWDER_FACTORY_RUBBLE_WEIGHTS,
        FLASH_POWDER_FACTORY_STRATEGIES,
        FLASH_POWDER_FACTORY_TROUSERS_CATALYST,
        FLASH_POWDER_FACTORY_XP_LOTS,
        FLASH_POWDER_FACTORY_XP_PER_POINT,
        ROGUE_KIT_OUTPUTS,
    )
    from pet_logic import store_active_pet_pure  # type: ignore
    from summoning_logic import dismiss_familiar_pure  # type: ignore


FLASH_POWDER_FACTORY_STATE_VERSION = 1
_FOUR_DOSE_EXCLUDED_TARGETS = frozenset(
    {
        "finished_overload",
        "finished_serum_207",
        "finished_juju_hunting",
        "finished_scentless",
        "finished_juju_farming",
        "finished_juju_cooking",
        "finished_juju_fishing",
        "finished_juju_woodcutting",
        "finished_juju_mining",
        "finished_saradomin_blessing",
        "finished_guthix_gift",
        "finished_zamorak_favour",
    }
)
_UNFINISHED_XP_EXCLUDED_TARGETS = frozenset({"unf_spirit_weed"})
_UNFINISHED_XP_BY_OUTPUT = {
    "Weapon poison+ (unf)": 8.0,
    "Weapon poison++ (unf)": 8.75,
}


def _int(value: Any, default: int = 0, *, maximum: int = 2_147_483_647) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(0, min(parsed, maximum))


def _roll(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        return 0.5
    if not math.isfinite(parsed):
        return 0.5
    return max(0.0, min(parsed, 0.999999999))


def _equipment_values(player_data: Mapping[str, Any]) -> set[str]:
    equipment = player_data.get("equipment")
    return (
        {str(value) for value in equipment.values() if value}
        if isinstance(equipment, Mapping)
        else set()
    )


def _active_follower(player_data: Mapping[str, Any]) -> Mapping[str, Any]:
    state = player_data.get("summoning_state")
    if not isinstance(state, Mapping):
        return {}
    follower = state.get("active_follower")
    return follower if isinstance(follower, Mapping) else {}


def _dismiss_follower(player_data: Mapping[str, Any]) -> tuple[dict[str, Any], bool, str]:
    follower = _active_follower(player_data)
    kind = str(follower.get("kind", ""))
    if kind == "familiar":
        updated, ok, _info = dismiss_familiar_pure(player_data)
        return dict(updated), bool(ok), kind
    if kind == "pet":
        updated, ok = store_active_pet_pure(player_data, location="bank")
        return dict(updated), bool(ok), kind
    return dict(player_data), not bool(follower), kind


def default_flash_powder_factory_policy_pure() -> dict[str, Any]:
    return {
        "version": FLASH_POWDER_FACTORY_STATE_VERSION,
        "automation_mode": "casual",
        "strategy": "max_points",
        "apparatus_policy": "ignore",
    }


def sanitize_flash_powder_factory_policy_pure(raw: Any) -> dict[str, Any]:
    source = raw if isinstance(raw, Mapping) else {}
    automation_mode = (
        "advanced"
        if str(source.get("automation_mode", "casual")).lower() == "advanced"
        else "casual"
    )
    strategy = str(source.get("strategy", "max_points"))
    if strategy not in FLASH_POWDER_FACTORY_STRATEGIES:
        strategy = "max_points"
    apparatus_policy = str(source.get("apparatus_policy", "ignore"))
    if apparatus_policy not in FLASH_POWDER_FACTORY_APPARATUS_POLICIES:
        apparatus_policy = "ignore"
    if automation_mode == "casual":
        apparatus_policy = (
            "opportunistic" if strategy == "balanced" else "ignore"
        )
    return {
        "version": FLASH_POWDER_FACTORY_STATE_VERSION,
        "automation_mode": automation_mode,
        "strategy": strategy,
        "apparatus_policy": apparatus_policy,
    }


def sanitize_flash_powder_factory_session_pure(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}
    total_slots = _int(raw.get("total_slots"), FLASH_POWDER_FACTORY_BASE_SLOTS)
    if total_slots not in {
        FLASH_POWDER_FACTORY_BASE_SLOTS,
        FLASH_POWDER_FACTORY_EXTENDED_SLOTS,
    }:
        total_slots = FLASH_POWDER_FACTORY_BASE_SLOTS

    if "slots_used" in raw:
        slots_used = _int(raw.get("slots_used"), maximum=total_slots - 1)
        batches = _int(raw.get("batches"), maximum=slots_used)
        score = _int(raw.get("score"))
        residue = _int(raw.get("residue"), maximum=slots_used)
        catalyst = _int(raw.get("catalyst"), maximum=99)
        apparatus = _int(
            raw.get("apparatus", FLASH_POWDER_FACTORY_BASE_APPARATUS),
            maximum=FLASH_POWDER_FACTORY_MAX_APPARATUS,
        )
    else:
        legacy_budget = 27 if total_slots == FLASH_POWDER_FACTORY_EXTENDED_SLOTS else 24
        legacy_reviews = _int(raw.get("reviews"), maximum=legacy_budget - 1)
        slots_used = min(
            total_slots - 1,
            int(round(legacy_reviews * total_slots / legacy_budget)),
        )
        batches = min(slots_used, _int(raw.get("deposits")))
        score = batches * 100
        residue = batches
        catalyst = _int(
            raw.get("catalyst_charges"),
            FLASH_POWDER_FACTORY_BASE_CATALYST,
            maximum=99,
        )
        apparatus = FLASH_POWDER_FACTORY_BASE_APPARATUS

    return {
        "version": FLASH_POWDER_FACTORY_STATE_VERSION,
        "total_slots": total_slots,
        "slots_used": slots_used,
        "batches": batches,
        "score": score,
        "residue": residue,
        "catalyst": catalyst,
        "apparatus": apparatus,
    }


def flash_powder_factory_locked_reasons_pure(
    player_data: Mapping[str, Any],
) -> tuple[str, ...]:
    reasons: list[str] = []
    if _int(player_data.get("agility_level"), 1) < 75:
        reasons.append("Agility level 75")
    if _int(player_data.get("thieving_level"), 1) < 75:
        reasons.append("Thieving level 75")
    if _int(player_data.get("herblore_level"), 1) < 50:
        reasons.append("Herblore level 50")
    if bool(player_data.get("combat_wilderness_skulled", False)):
        reasons.append("remove your Wilderness skull")
    if _active_follower(player_data):
        reasons.append("dismiss your active follower")
    return tuple(reasons)


def _activities(player_data: Mapping[str, Any]) -> dict[str, Any]:
    raw = player_data.get("agility_activity_state")
    return copy.deepcopy(dict(raw)) if isinstance(raw, Mapping) else {}


def _currencies(player_data: Mapping[str, Any]) -> dict[str, int]:
    raw = player_data.get("agility_activity_currencies")
    raw = raw if isinstance(raw, Mapping) else {}
    return {
        "brianpoints": _int(raw.get("brianpoints")),
        "circus_audience": _int(raw.get("circus_audience")),
    }


def _record_completion(data: dict[str, Any]) -> None:
    completions = dict(data.get("agility_activity_completions") or {})
    completions[FLASH_POWDER_FACTORY_ACTIVITY_ID] = (
        _int(completions.get(FLASH_POWDER_FACTORY_ACTIVITY_ID)) + 1
    )
    data["agility_activity_completions"] = completions


def enter_flash_powder_factory_pure(
    player_data: Mapping[str, Any],
    *,
    confirm_dismiss_follower: bool = False,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the factory state and its activity map are rebuilt
    # fresh, and inventory is rebuilt with dict() before any write.
    data = dict(player_data)
    activities = _activities(data)
    active = sanitize_flash_powder_factory_session_pure(
        activities.get(FLASH_POWDER_FACTORY_ACTIVITY_ID)
    )
    if active:
        return data, False, {"reason": "A Flash Powder Factory session is already active."}
    persistent_session = data.get("activity_session")
    persistent_id = (
        str(persistent_session.get("active_id", ""))
        if isinstance(persistent_session, Mapping)
        else ""
    )
    if persistent_id and persistent_id != FLASH_POWDER_FACTORY_ACTIVITY_ID:
        return data, False, {"reason": "Finish the active persistent activity first."}
    locked = tuple(
        reason
        for reason in flash_powder_factory_locked_reasons_pure(data)
        if reason != "dismiss your active follower"
    )
    if locked:
        return data, False, {"reason": ", ".join(locked), "locked_reasons": locked}
    follower = _active_follower(data)
    if follower and not confirm_dismiss_follower:
        return data, False, {
            "reason": "Your active follower must be dismissed before entering.",
            "requires_follower_dismissal": True,
            "follower_kind": str(follower.get("kind", "follower")),
        }
    if follower:
        data, ok, dismissed_kind = _dismiss_follower(data)
        if not ok:
            return data, False, {"reason": "The active follower could not be dismissed safely."}
    else:
        dismissed_kind = ""

    equipment = _equipment_values(data)
    total_slots = (
        FLASH_POWDER_FACTORY_EXTENDED_SLOTS
        if {"Rogue top", "Factory top"} & equipment
        else FLASH_POWDER_FACTORY_BASE_SLOTS
    )
    catalyst = (
        FLASH_POWDER_FACTORY_TROUSERS_CATALYST
        if "Factory trousers" in equipment
        else FLASH_POWDER_FACTORY_BASE_CATALYST
    )
    activities = _activities(data)
    activities[FLASH_POWDER_FACTORY_ACTIVITY_ID] = {
        "version": FLASH_POWDER_FACTORY_STATE_VERSION,
        "total_slots": total_slots,
        "slots_used": 0,
        "batches": 0,
        "score": 0,
        "residue": 0,
        "catalyst": catalyst,
        "apparatus": FLASH_POWDER_FACTORY_BASE_APPARATUS,
    }
    data["agility_activity_state"] = activities
    data["activity_session"] = {"active_id": FLASH_POWDER_FACTORY_ACTIVITY_ID}
    data["current_utility"] = FLASH_POWDER_FACTORY_ACTIVITY_ID
    data["agility_status"] = (
        f"Flash Powder Factory · entered · 0/{total_slots} circuits"
    )
    return data, True, {
        "message": data["agility_status"],
        "dismissed_follower_kind": dismissed_kind,
        "total_slots": total_slots,
    }


def set_flash_powder_factory_policy_pure(
    player_data: Mapping[str, Any],
    *,
    automation_mode: Any = None,
    strategy: Any = None,
    apparatus_policy: Any = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the factory state and its activity map are rebuilt
    # fresh, and inventory is rebuilt with dict() before any write.
    data = dict(player_data)
    current = sanitize_flash_powder_factory_policy_pure(
        data.get("agility_flash_powder_factory_policy")
    )
    candidate = sanitize_flash_powder_factory_policy_pure(
        {
            **current,
            "automation_mode": current["automation_mode"] if automation_mode is None else automation_mode,
            "strategy": current["strategy"] if strategy is None else strategy,
            "apparatus_policy": current["apparatus_policy"] if apparatus_policy is None else apparatus_policy,
        }
    )
    data["agility_flash_powder_factory_policy"] = candidate
    return data, True, {
        "message": (
            "Flash Powder Factory policy · "
            f"{FLASH_POWDER_FACTORY_STRATEGIES[candidate['strategy']]} · "
            f"{FLASH_POWDER_FACTORY_APPARATUS_POLICIES[candidate['apparatus_policy']]}"
        )
    }


def _weighted_result(rows: Sequence[tuple[str, int]], roll: float) -> str:
    total = sum(weight for _name, weight in rows)
    cursor = int(_roll(roll) * total)
    for name, weight in rows:
        if cursor < weight:
            return name
        cursor -= weight
    return rows[-1][0]


def _next_rogue_piece(player_data: Mapping[str, Any]) -> str:
    inventory = player_data.get("inventory")
    inventory = inventory if isinstance(inventory, Mapping) else {}
    equipment = _equipment_values(player_data)
    for piece in FLASH_POWDER_FACTORY_ROGUE_OUTFIT:
        if _int(inventory.get(piece)) <= 0 and piece not in equipment:
            return piece
    return FLASH_POWDER_FACTORY_ROGUE_OUTFIT[0]


def _brianpoints_from_score(score: int, *, completed: bool, slots_used: int) -> tuple[int, int]:
    score = max(0, int(score))
    points = int(min(score, 500) * 0.20 + max(0, score - 500) * 0.05)
    if completed or slots_used >= 4:
        points += FLASH_POWDER_FACTORY_LONG_STAY_BONUS
    penalty = 0
    if not completed:
        remaining_slots = max(0, FLASH_POWDER_FACTORY_BASE_SLOTS - min(slots_used, FLASH_POWDER_FACTORY_BASE_SLOTS))
        source_band = int(math.ceil(15 * remaining_slots / FLASH_POWDER_FACTORY_BASE_SLOTS))
        if source_band >= 8:
            penalty = 50
        elif source_band == 7:
            penalty = 46
        elif source_band == 6:
            penalty = 40
        elif source_band == 5:
            penalty = 33
        elif source_band == 4:
            penalty = 26
        elif source_band == 3:
            penalty = 20
        points = int(math.floor(points * (100 - penalty) / 100))
    return min(FLASH_POWDER_FACTORY_MAX_BRIANPOINTS, points), penalty


def apply_flash_powder_factory_review_pure(
    player_data: Mapping[str, Any],
    rolls: Sequence[float],
    *,
    productive: bool = True,
) -> tuple[dict[str, Any], dict[str, Any]]:
    # Shallow on purpose: the factory state and its activity map are rebuilt
    # fresh, and inventory is rebuilt with dict() before any write.
    data = dict(player_data)
    activities = _activities(data)
    session = sanitize_flash_powder_factory_session_pure(
        activities.get(FLASH_POWDER_FACTORY_ACTIVITY_ID)
    )
    if not session:
        return data, {
            "allowed": False,
            "reason": "Enter the Flash Powder Factory before training.",
        }
    if not productive:
        session["slots_used"] += 1
        completed = session["slots_used"] >= session["total_slots"]
        points = 0
        if completed:
            points, _penalty = _brianpoints_from_score(
                session["score"],
                completed=True,
                slots_used=session["slots_used"],
            )
            currencies = _currencies(data)
            currencies["brianpoints"] += points
            data["agility_activity_currencies"] = currencies
            activities.pop(FLASH_POWDER_FACTORY_ACTIVITY_ID, None)
            if isinstance(data.get("activity_session"), Mapping) and str(
                data["activity_session"].get("active_id", "")
            ) == FLASH_POWDER_FACTORY_ACTIVITY_ID:
                data["activity_session"] = {"active_id": ""}
            if str(data.get("current_agility", "")) == FLASH_POWDER_FACTORY_ACTIVITY_ID:
                data["current_agility"] = DEFAULT_AGILITY_TARGET
            _record_completion(data)
        else:
            activities[FLASH_POWDER_FACTORY_ACTIVITY_ID] = session
        data["agility_activity_state"] = activities
        status_parts = [
            "Flash Powder Factory",
            f"idle slot {session['slots_used']}/{session['total_slots']}",
        ]
        if completed:
            status_parts.append(f"+{points} Brianpoints")
        data["agility_status"] = " · ".join(status_parts)
        return data, {
            "allowed": True,
            "success": False,
            "target_id": FLASH_POWDER_FACTORY_ACTIVITY_ID,
            "action_id": "idle_slot",
            "expected_success_chance": 1.0,
            "score_gain": 0,
            "outputs": {},
            "xp": 0.0,
            "cross_skill_rewards": [],
            "completed_activity": completed,
            "brianpoints": points,
            "status": data["agility_status"],
        }
    values = tuple(_roll(value) for value in rolls)
    values += (0.5,) * max(0, 4 - len(values))
    obstacle_roll, route_roll, rubble_roll, contest_roll = values[:4]
    policy = sanitize_flash_powder_factory_policy_pure(
        data.get("agility_flash_powder_factory_policy")
    )
    equipment = _equipment_values(data)
    full_factory_set = FLASH_POWDER_FACTORY_OUTFIT.issubset(equipment)

    catalyst_detour = session["catalyst"] <= 0
    if not catalyst_detour:
        session["catalyst"] -= 1
    obstacle_failure_chance = 0.15 * (0.70 if "Factory boots" in equipment else 1.0)
    obstacle_failed = obstacle_roll < obstacle_failure_chance

    strategy = policy["strategy"]
    charge_bonus = 0
    rubble_threshold = 0.0
    if not catalyst_detour and not obstacle_failed:
        if strategy == "max_points":
            charge_bonus = 20
            rubble_threshold = 0.10
        elif strategy == "rogue_equipment":
            rubble_threshold = 0.70
        else:
            charge_bonus = 10
            rubble_threshold = 0.35
    searched_rubble = route_roll < rubble_threshold

    contest = "none"
    apparatus_policy = policy["apparatus_policy"]
    if apparatus_policy == "opportunistic":
        gain_threshold = 0.30 if "Factory gloves" in equipment else 0.20
        if contest_roll < gain_threshold and session["apparatus"] < FLASH_POWDER_FACTORY_MAX_APPARATUS:
            session["apparatus"] += 1
            contest = "gained apparatus"
        elif (
            gain_threshold <= contest_roll < gain_threshold + 0.15
            and session["apparatus"] > 0
        ):
            session["apparatus"] -= 1
            contest = "lost apparatus"
    elif contest_roll < 0.08 and session["apparatus"] > 0:
        session["apparatus"] -= 1
        contest = "pickpocketed"

    outputs: dict[str, int] = {}
    rubble_result = ""
    rubble_score = 0
    if searched_rubble:
        rubble_result = _weighted_result(
            FLASH_POWDER_FACTORY_MASK_RUBBLE_WEIGHTS
            if "Factory mask" in equipment
            else FLASH_POWDER_FACTORY_RUBBLE_WEIGHTS,
            rubble_roll,
        )
        if rubble_result == "catalyst":
            session["catalyst"] += 1
        elif rubble_result == "apparatus":
            session["apparatus"] = min(
                FLASH_POWDER_FACTORY_MAX_APPARATUS,
                session["apparatus"] + 1,
            )
        elif rubble_result == "average_powder":
            rubble_score = 105
        elif rubble_result == "very_nice_powder":
            rubble_score = 121
        elif rubble_result == "rogue_piece":
            piece = _next_rogue_piece(data)
            outputs[piece] = 1
            inventory = dict(data.get("inventory") or {})
            inventory[piece] = _int(inventory.get(piece)) + 1
            data["inventory"] = inventory

    bonus_percent = session["apparatus"] * 2.5 + charge_bonus + session["residue"]
    batch_score = int(math.floor(100 * (1 + bonus_percent / 100)))
    if full_factory_set and batch_score >= 120:
        batch_score += 10
    score_gain = batch_score + rubble_score
    session["score"] += score_gain
    session["batches"] += 1
    session["residue"] += 1
    session["slots_used"] += 1
    completed = session["slots_used"] >= session["total_slots"]

    points = 0
    if completed:
        points, _penalty = _brianpoints_from_score(
            session["score"], completed=True, slots_used=session["slots_used"]
        )
        currencies = _currencies(data)
        currencies["brianpoints"] += points
        data["agility_activity_currencies"] = currencies
        activities.pop(FLASH_POWDER_FACTORY_ACTIVITY_ID, None)
        if isinstance(data.get("activity_session"), Mapping) and str(
            data["activity_session"].get("active_id", "")
        ) == FLASH_POWDER_FACTORY_ACTIVITY_ID:
            data["activity_session"] = {"active_id": ""}
        if str(data.get("current_agility", "")) == FLASH_POWDER_FACTORY_ACTIVITY_ID:
            data["current_agility"] = DEFAULT_AGILITY_TARGET
        _record_completion(data)
    else:
        activities[FLASH_POWDER_FACTORY_ACTIVITY_ID] = session
    data["agility_activity_state"] = activities
    status_parts = [
        "Flash Powder Factory",
        f"circuit {session['slots_used']}/{session['total_slots']}",
        f"+{score_gain} score",
    ]
    if catalyst_detour:
        status_parts.append("catalyst detour")
    if obstacle_failed:
        status_parts.append("obstacle delay")
    if searched_rubble:
        status_parts.append(f"rubble: {rubble_result.replace('_', ' ')}")
    if contest != "none":
        status_parts.append(contest)
    if completed:
        status_parts.append(f"+{points} Brianpoints")
    data["agility_status"] = " · ".join(status_parts)
    return data, {
        "allowed": True,
        "success": True,
        "target_id": FLASH_POWDER_FACTORY_ACTIVITY_ID,
        "action_id": "production_circuit",
        "expected_success_chance": 1.0,
        "score_gain": score_gain,
        "batch_score": batch_score,
        "rubble_score": rubble_score,
        "obstacle_failed": obstacle_failed,
        "obstacle_failure_chance": obstacle_failure_chance,
        "catalyst_detour": catalyst_detour,
        "rubble_result": rubble_result,
        "apparatus_contest": contest,
        "outputs": outputs,
        "xp": 0.0,
        "cross_skill_rewards": [],
        "completed_activity": completed,
        "brianpoints": points,
        "status": data["agility_status"],
    }


def leave_flash_powder_factory_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the factory state and its activity map are rebuilt
    # fresh, and inventory is rebuilt with dict() before any write.
    data = dict(player_data)
    activities = _activities(data)
    session = sanitize_flash_powder_factory_session_pure(
        activities.get(FLASH_POWDER_FACTORY_ACTIVITY_ID)
    )
    if not session:
        return data, False, {"reason": "No Flash Powder Factory session is active."}
    points, penalty = _brianpoints_from_score(
        session["score"], completed=False, slots_used=session["slots_used"]
    )
    currencies = _currencies(data)
    currencies["brianpoints"] += points
    data["agility_activity_currencies"] = currencies
    activities.pop(FLASH_POWDER_FACTORY_ACTIVITY_ID, None)
    data["agility_activity_state"] = activities
    if isinstance(data.get("activity_session"), Mapping) and str(
        data["activity_session"].get("active_id", "")
    ) == FLASH_POWDER_FACTORY_ACTIVITY_ID:
        data["activity_session"] = {"active_id": ""}
    if str(data.get("current_agility", "")) == FLASH_POWDER_FACTORY_ACTIVITY_ID:
        data["current_agility"] = DEFAULT_AGILITY_TARGET
    data["agility_status"] = (
        f"Left Flash Powder Factory · {points} Brianpoints · {penalty}% early-exit penalty"
    )
    return data, True, {
        "message": data["agility_status"],
        "brianpoints": points,
        "penalty_percent": penalty,
    }


def redeem_flash_powder_factory_xp_pure(
    player_data: Mapping[str, Any],
    skill_id: str,
    points: Any,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the factory state and its activity map are rebuilt
    # fresh, and inventory is rebuilt with dict() before any write.
    data = dict(player_data)
    skill = str(skill_id).lower()
    amount = _int(points)
    if skill not in FLASH_POWDER_FACTORY_XP_PER_POINT or amount not in FLASH_POWDER_FACTORY_XP_LOTS:
        return data, False, {"reason": "Choose a period reward lot."}
    currencies = _currencies(data)
    if currencies["brianpoints"] < amount:
        return data, False, {"reason": "Not enough Brianpoints."}
    currencies["brianpoints"] -= amount
    data["agility_activity_currencies"] = currencies
    xp = amount * FLASH_POWDER_FACTORY_XP_PER_POINT[skill]
    return data, True, {
        "message": f"Redeemed {amount:,} Brianpoints for {xp:,.0f} {skill.title()} XP",
        "skill_id": skill,
        "xp": xp,
        "points": amount,
    }


def redeem_flash_powder_factory_item_pure(
    player_data: Mapping[str, Any],
    item_name: str,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the factory state and its activity map are rebuilt
    # fresh, and inventory is rebuilt with dict() before any write.
    data = dict(player_data)
    item = str(item_name)
    cost = FLASH_POWDER_FACTORY_REWARD_COSTS.get(item)
    if cost is None:
        return data, False, {"reason": "Unknown Flash Powder Factory reward."}
    currencies = _currencies(data)
    if currencies["brianpoints"] < cost:
        return data, False, {"reason": "Not enough Brianpoints."}
    inventory = dict(data.get("inventory") or {})
    if item != "Rogue kit" and (
        _int(inventory.get(item)) > 0 or item in _equipment_values(data)
    ):
        return data, False, {"reason": f"You already own {item}."}
    currencies["brianpoints"] -= cost
    inventory[item] = _int(inventory.get(item)) + 1
    data["agility_activity_currencies"] = currencies
    data["inventory"] = inventory
    return data, True, {
        "message": f"Redeemed {item} for {cost:,} Brianpoints",
        "item": item,
        "cost": cost,
    }


def convert_rogue_kit_pure(
    player_data: Mapping[str, Any],
    output_item: str,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the factory state and its activity map are rebuilt
    # fresh, and inventory is rebuilt with dict() before any write.
    data = dict(player_data)
    output = str(output_item)
    inventory = dict(data.get("inventory") or {})
    if output not in ROGUE_KIT_OUTPUTS:
        return data, False, {"reason": "Choose a tool the Rogue kit can become."}
    if _int(inventory.get("Rogue kit")) <= 0:
        return data, False, {"reason": "No Rogue kit is available."}
    inventory["Rogue kit"] = _int(inventory.get("Rogue kit")) - 1
    if inventory["Rogue kit"] <= 0:
        inventory.pop("Rogue kit", None)
    inventory[output] = _int(inventory.get(output)) + 1
    data["inventory"] = inventory
    return data, True, {
        "message": f"Converted one Rogue kit into {output}",
        "item": output,
    }


def flash_powder_factory_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    activities = _activities(player_data)
    session = sanitize_flash_powder_factory_session_pure(
        activities.get(FLASH_POWDER_FACTORY_ACTIVITY_ID)
    )
    policy = sanitize_flash_powder_factory_policy_pure(
        player_data.get("agility_flash_powder_factory_policy")
    )
    currencies = _currencies(player_data)
    inventory = player_data.get("inventory")
    inventory = inventory if isinstance(inventory, Mapping) else {}
    equipment = _equipment_values(player_data)
    locked = flash_powder_factory_locked_reasons_pure(player_data)
    return {
        "active": bool(session),
        "can_review": bool(session),
        "locked_reasons": locked,
        "automation_mode": policy["automation_mode"],
        "strategy": policy["strategy"],
        "apparatus_policy": policy["apparatus_policy"],
        "slots_used": session.get("slots_used", 0),
        "total_slots": session.get("total_slots", FLASH_POWDER_FACTORY_BASE_SLOTS),
        "batches": session.get("batches", 0),
        "score": session.get("score", 0),
        "residue": session.get("residue", 0),
        "catalyst": session.get("catalyst", 0),
        "apparatus": session.get("apparatus", 0),
        "brianpoints": currencies["brianpoints"],
        "reward_rows": tuple(
            {
                "item_name": item,
                "cost": cost,
                "owned": item != "Rogue kit" and (
                    _int(inventory.get(item)) > 0 or item in equipment
                ),
                "affordable": currencies["brianpoints"] >= cost,
            }
            for item, cost in FLASH_POWDER_FACTORY_REWARD_COSTS.items()
        ),
        "last_result": (
            str(player_data.get("agility_status", "Ready to enter"))
            if str(player_data.get("agility_status", "")).startswith(
                "Flash Powder Factory"
            )
            else "Ready to enter"
        ),
    }


def apply_factory_outfit_herblore_bonus_pure(
    target_id: str,
    inventory: Mapping[str, Any],
    base_xp: float,
    spec: Mapping[str, Any],
    equipment: Mapping[str, Any],
    roll: Any,
    herblore_data: Mapping[str, Mapping[str, Any]],
) -> tuple[dict[str, Any], float, dict[str, Any]]:
    new_inventory = dict(inventory)
    worn = {str(value) for value in equipment.values() if value}
    factory_count = len(FLASH_POWDER_FACTORY_OUTFIT & worn)
    output_item = str(spec.get("output_item", target_id))
    info = {"four_dose": False, "unfinished_xp": 0.0}

    four_dose_chance = herblore_four_dose_bonus_chance_pure(
        target_id,
        spec,
        equipment,
    )
    if four_dose_chance > 0 and _roll(roll) < four_dose_chance:
        four_dose = output_item[:-4] + " (4)"
        remaining = max(0, _int(new_inventory.get(output_item)) - 1)
        if remaining:
            new_inventory[output_item] = remaining
        else:
            new_inventory.pop(output_item, None)
        new_inventory[four_dose] = _int(new_inventory.get(four_dose)) + 1
        info["four_dose"] = True
        info["output_item"] = four_dose

    xp = float(base_xp)
    if (
        factory_count == len(FLASH_POWDER_FACTORY_OUTFIT)
        and str(spec.get("group", "")) == "unf"
        and str(target_id) not in _UNFINISHED_XP_EXCLUDED_TARGETS
    ):
        clean_xp = _UNFINISHED_XP_BY_OUTPUT.get(output_item, 0.0)
        if clean_xp <= 0:
            clean_input = next(
                (
                    str(item_name)
                    for item_name in (spec.get("requirements") or {})
                    if str(item_name).startswith("Clean ")
                ),
                "",
            )
            clean_xp = next(
                (
                    float(row.get("exp", 0.0) or 0.0)
                    for row in herblore_data.values()
                    if str(row.get("output_item", "")) == clean_input
                ),
                0.0,
            )
        if clean_xp > 0:
            xp += clean_xp
            info["unfinished_xp"] = clean_xp
    return new_inventory, xp, info


def factory_outfit_four_dose_eligible_pure(
    target_id: str,
    spec: Mapping[str, Any],
    equipment: Mapping[str, Any],
) -> bool:
    return herblore_four_dose_bonus_chance_pure(target_id, spec, equipment) > 0


def herblore_four_dose_bonus_chance_pure(
    target_id: str,
    spec: Mapping[str, Any],
    equipment: Mapping[str, Any],
) -> float:
    worn = {str(value) for value in equipment.values() if value}
    output_item = str(spec.get("output_item", target_id))
    if (
        str(target_id) in _FOUR_DOSE_EXCLUDED_TARGETS
        or str(spec.get("group", "")) != "finished"
        or not output_item.endswith(" (3)")
    ):
        return 0.0
    chance = 0.10 if len(FLASH_POWDER_FACTORY_OUTFIT & worn) >= 3 else 0.0
    if str(target_id) == "finished_prayer_renewal" and "Morytania legs 4" in worn:
        chance += 0.20
    return chance
