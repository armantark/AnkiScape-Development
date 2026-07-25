"""Pure atomic multi-skill performance loop for Big Top Bonanza."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ..data.circus_data import (
    CIRCUS_ACTIVITY_ID,
    CIRCUS_PERFORMANCE_ORDER,
    CIRCUS_PERFORMANCES,
    CIRCUS_REWARDS,
    CIRCUS_STRATEGIES,
    CIRCUS_WEEK_REVIEWS,
    CircusPerformance,
    CircusTrick,
)


CIRCUS_STATE_VERSION = 1
_SKILL_LEVEL_KEYS = {
    "magic": "magic_level",
    "ranged": "ranged_level",
    "agility": "agility_level",
    "firemaking": "firemaking_level",
    "thieving": "thieving_level",
}
_QUEST_GATE_LABELS = {
    "the_firemakers_curse": "The Firemaker's Curse",
    "some_like_it_cold": "Some Like It Cold",
}


def _int(value: Any, default: int = 0, *, minimum: int = 0) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(minimum, parsed)


def _float(value: Any, default: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        return default
    if parsed != parsed or parsed in (float("inf"), float("-inf")):
        return default
    return parsed


def _quest_complete(player_data: Mapping[str, Any], quest_id: str) -> bool:
    quests = player_data.get("quests")
    state = quests.get(quest_id) if isinstance(quests, Mapping) else None
    return isinstance(state, Mapping) and bool(state.get("completed", False))


def _answered_card_week(player_data: Mapping[str, Any]) -> int:
    clock = player_data.get("shop_market_clock")
    answered = _int(clock.get("answered_cards")) if isinstance(clock, Mapping) else 0
    return answered // CIRCUS_WEEK_REVIEWS


def default_circus_state_pure() -> dict[str, Any]:
    return {
        "version": CIRCUS_STATE_VERSION,
        "selected_performance": "agility",
        "automation_mode": "casual",
        "strategies": {
            performance_id: "balanced"
            for performance_id in CIRCUS_PERFORMANCE_ORDER
        },
        "advanced_routines": {},
        "used_week_by_performance": {},
        "unlocked_costumes": [],
        "lifetime_performances": 0,
        "lifetime_score": 0,
        "last_result": "",
    }


def _valid_routine(performance_id: str, raw: Any) -> list[str]:
    performance = CIRCUS_PERFORMANCES[performance_id]
    valid_ids = {trick.id for trick in performance.tricks}
    if not isinstance(raw, (list, tuple)):
        return []
    routine = [str(value) for value in raw if str(value) in valid_ids]
    return routine[: performance.max_attempts]


def sanitize_circus_state_pure(raw: Any) -> dict[str, Any]:
    source = raw if isinstance(raw, Mapping) else {}
    defaults = default_circus_state_pure()
    selected = str(source.get("selected_performance", defaults["selected_performance"]))
    if selected not in CIRCUS_PERFORMANCES:
        selected = defaults["selected_performance"]
    mode = str(source.get("automation_mode", "casual"))
    if mode not in {"casual", "advanced"}:
        mode = "casual"
    raw_strategies = source.get("strategies")
    strategies = {}
    for performance_id in CIRCUS_PERFORMANCE_ORDER:
        strategy = (
            str(raw_strategies.get(performance_id, "balanced"))
            if isinstance(raw_strategies, Mapping)
            else "balanced"
        )
        strategies[performance_id] = (
            strategy if strategy in CIRCUS_STRATEGIES else "balanced"
        )
    raw_routines = source.get("advanced_routines")
    routines = {
        performance_id: routine
        for performance_id in CIRCUS_PERFORMANCE_ORDER
        if (
            routine := _valid_routine(
                performance_id,
                raw_routines.get(performance_id) if isinstance(raw_routines, Mapping) else None,
            )
        )
    }
    raw_weeks = source.get("used_week_by_performance")
    weeks = {
        performance_id: _int(raw_weeks.get(performance_id), -1, minimum=-1)
        for performance_id in CIRCUS_PERFORMANCE_ORDER
        if isinstance(raw_weeks, Mapping)
        and _int(raw_weeks.get(performance_id), -1, minimum=-1) >= 0
    }
    raw_costumes = source.get("unlocked_costumes")
    valid_costumes = {
        str(reward["display_name"]) for reward in CIRCUS_REWARDS.values()
    }
    costumes = (
        [
            item
            for item in dict.fromkeys(str(value) for value in raw_costumes)
            if item in valid_costumes
        ]
        if isinstance(raw_costumes, (list, tuple))
        else []
    )
    return {
        **defaults,
        "selected_performance": selected,
        "automation_mode": mode,
        "strategies": strategies,
        "advanced_routines": routines,
        "used_week_by_performance": weeks,
        "unlocked_costumes": costumes,
        "lifetime_performances": _int(source.get("lifetime_performances")),
        "lifetime_score": _int(source.get("lifetime_score")),
        "last_result": str(source.get("last_result", defaults["last_result"]))[:500],
    }


def migrate_legacy_circus_state_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_circus_state_pure(player_data.get("circus"))
    legacy_week = _int(
        player_data.get("agility_circus_last_week"),
        -1,
        minimum=-1,
    )
    if legacy_week >= 0 and "agility" not in state["used_week_by_performance"]:
        state["used_week_by_performance"]["agility"] = legacy_week
    currencies = player_data.get("agility_activity_currencies")
    if isinstance(currencies, Mapping):
        state["lifetime_score"] = max(
            state["lifetime_score"], _int(currencies.get("circus_audience"))
        )
    return state


def _performance_locked_reasons(
    player_data: Mapping[str, Any],
    performance: CircusPerformance,
    state: Mapping[str, Any],
) -> tuple[str, ...]:
    reasons: list[str] = []
    if performance.quest_gate and not _quest_complete(player_data, performance.quest_gate):
        reasons.append(
            _QUEST_GATE_LABELS.get(
                performance.quest_gate,
                performance.quest_gate.replace("_", " ").title(),
            )
        )
    if state["used_week_by_performance"].get(performance.id) == _answered_card_week(player_data):
        reasons.append("next answered-card week")
    return tuple(reasons)


def _canonical_by_level(performance: CircusPerformance) -> list[CircusTrick]:
    rows: dict[int, CircusTrick] = {}
    for trick in performance.tricks:
        rows.setdefault(trick.level, trick)
    return list(rows.values())


def _routine_for_strategy(
    performance: CircusPerformance,
    level: int,
    strategy: str,
) -> list[CircusTrick]:
    canonical = _canonical_by_level(performance)
    if strategy == "max_xp":
        within = sorted(
            (trick for trick in canonical if trick.level <= level),
            key=lambda trick: trick.level,
            reverse=True,
        )
        above = sorted(
            (trick for trick in canonical if trick.level > level),
            key=lambda trick: trick.level,
        )
        ordered = within + above
        if not ordered:
            ordered = canonical
        routine = ordered[: performance.max_attempts]
        while len(routine) < performance.max_attempts:
            routine.append(ordered[len(routine) % len(ordered)])
        return routine
    if strategy == "entertain":
        ordered = sorted(
            performance.tricks,
            key=lambda trick: (trick.level, trick.variant, trick.id),
            reverse=True,
        )
        routine = ordered[: performance.max_attempts]
        while len(routine) < performance.max_attempts:
            routine.append(ordered[len(routine) % len(ordered)])
        return routine
    ordered = sorted(canonical, key=lambda trick: trick.level, reverse=True)
    if len(ordered) > performance.max_attempts:
        ordered = ordered[: performance.max_attempts]
    while len(ordered) < performance.max_attempts:
        ordered.append(canonical[len(ordered) % len(canonical)])
    return ordered


def _success_chance(level: int, suggested_level: int) -> float:
    # The period source proves non-zero under-level success and non-certain
    # over-level success but does not expose the curve. This bounded linear
    # calibration is deliberately isolated for later replacement.
    return max(0.10, min(0.95, 0.50 + (level - suggested_level) / 200.0))


def _barely_success_xp(
    performance: CircusPerformance,
    level: int,
    trick: CircusTrick,
) -> float:
    if trick.level <= level:
        return trick.xp
    # Oldid 6554790 conflicts between "40 levels below" and "half current
    # level". The detailed strategy section is used as a conservative bounded
    # translation: map to the highest available band at or below half level.
    target = max(1, level // 2)
    candidates = [row for row in _canonical_by_level(performance) if row.level <= target]
    return max(candidates, key=lambda row: row.level).xp if candidates else min(
        row.xp for row in performance.tricks
    )


def _costume_score(
    trick: CircusTrick,
    *,
    success: bool,
    strategy: str,
    repeated: bool,
    unlocked_costume_count: int,
) -> int:
    if not success:
        return 0
    # The cutoff page gives exact reward thresholds and an observed ~150-point
    # level-99 trick, but not the score algorithm. 50 + suggested level anchors
    # that observation; small declared bonuses represent emotes/requests and
    # owned costume without pretending the hidden audience formula is known.
    score = 50 + trick.level
    if strategy == "entertain":
        score += 5
    elif strategy == "balanced":
        score += 2
    if repeated:
        score -= 10
    score += min(5, unlocked_costume_count) * 5
    return max(1, score)


def _reward_for_score(performance_id: str, score: int) -> str:
    if score <= 0:
        return ""
    if score <= 500:
        reward_id = "audience"
    elif score <= 1000:
        reward_id = (
            "firemaker"
            if performance_id in {"fire_breathing", "flaming_poi"}
            else "acrobat"
        )
    elif score <= 1200:
        reward_id = "clown"
    else:
        reward_id = "ringmaster"
    return str(CIRCUS_REWARDS[reward_id]["display_name"])


def _inventory(player_data: Mapping[str, Any]) -> dict[str, int]:
    raw = player_data.get("inventory")
    if not isinstance(raw, Mapping):
        return {}
    return {str(item): _int(amount) for item, amount in raw.items()}


def circus_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_circus_state_pure(player_data.get("circus"))
    current_week = _answered_card_week(player_data)
    performance_rows = []
    for performance_id in CIRCUS_PERFORMANCE_ORDER:
        performance = CIRCUS_PERFORMANCES[performance_id]
        locked = _performance_locked_reasons(player_data, performance, state)
        performance_rows.append(
            {
                "id": performance.id,
                "display_name": performance.display_name,
                "skill_id": performance.skill_id,
                "max_attempts": performance.max_attempts,
                "quest_gate": performance.quest_gate,
                "locked_reasons": locked,
                "available": not locked,
                "used_this_week": state["used_week_by_performance"].get(performance.id)
                == current_week,
                "strategy": state["strategies"][performance.id],
                "routine": tuple(state["advanced_routines"].get(performance.id, ())),
            }
        )
    selected = CIRCUS_PERFORMANCES[state["selected_performance"]]
    selected_locked = _performance_locked_reasons(player_data, selected, state)
    return {
        **state,
        "week_index": current_week,
        "performances": tuple(performance_rows),
        "selected_name": selected.display_name,
        "selected_skill_id": selected.skill_id,
        "selected_locked_reasons": selected_locked,
        "can_review": not selected_locked,
        "remaining_count": sum(1 for row in performance_rows if row["available"]),
        "reward_rows": tuple(
            {
                "id": reward_id,
                **spec,
                "unlocked": spec["display_name"] in state["unlocked_costumes"],
            }
            for reward_id, spec in CIRCUS_REWARDS.items()
        ),
    }


def apply_circus_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: this only assigns top-level keys on the working copy;
    # the locked-reason helpers are read-only.
    data = dict(player_data)
    state = sanitize_circus_state_pure(data.get("circus"))
    body = payload if isinstance(payload, Mapping) else {}
    if action_id == "set_policy":
        performance_id = str(body.get("performance_id", state["selected_performance"]))
        mode = str(body.get("automation_mode", state["automation_mode"]))
        strategy = str(body.get("strategy", state["strategies"].get(performance_id, "balanced")))
        if performance_id not in CIRCUS_PERFORMANCES:
            return data, False, {"reason": "Choose a valid Circus performance."}
        if mode not in {"casual", "advanced"}:
            return data, False, {"reason": "Choose Casual or Advanced mode."}
        if strategy not in CIRCUS_STRATEGIES:
            return data, False, {"reason": "Choose a valid performance strategy."}
        locked = _performance_locked_reasons(
            data,
            CIRCUS_PERFORMANCES[performance_id],
            state,
        )
        if locked:
            return data, False, {"reason": ", ".join(locked)}
        state["selected_performance"] = performance_id
        state["automation_mode"] = mode
        state["strategies"][performance_id] = strategy
        data["circus"] = state
        data["current_utility"] = CIRCUS_ACTIVITY_ID
        state["last_result"] = (
            f"Armed {CIRCUS_PERFORMANCES[performance_id].display_name} · "
            f"{CIRCUS_STRATEGIES[strategy]} · {mode.title()}"
        )
        data["circus"] = state
        return data, True, {"message": state["last_result"]}
    if action_id == "set_routine":
        performance_id = str(body.get("performance_id", state["selected_performance"]))
        if performance_id not in CIRCUS_PERFORMANCES:
            return data, False, {"reason": "Choose a valid Circus performance."}
        locked = _performance_locked_reasons(
            data,
            CIRCUS_PERFORMANCES[performance_id],
            state,
        )
        if locked:
            return data, False, {"reason": ", ".join(locked)}
        routine = _valid_routine(performance_id, body.get("routine"))
        if not routine:
            return data, False, {"reason": "Choose at least one valid trick."}
        state["advanced_routines"][performance_id] = routine
        state["selected_performance"] = performance_id
        state["automation_mode"] = "advanced"
        state["last_result"] = (
            f"Saved {len(routine)}-trick routine for "
            f"{CIRCUS_PERFORMANCES[performance_id].display_name}."
        )
        data["circus"] = state
        return data, True, {"message": state["last_result"]}
    if action_id == "abandon":
        performance_id = str(body.get("performance_id", state["selected_performance"]))
        performance = CIRCUS_PERFORMANCES.get(performance_id)
        if performance is None:
            return data, False, {"reason": "Choose a valid Circus performance."}
        locked = _performance_locked_reasons(data, performance, state)
        if locked:
            return data, False, {"reason": ", ".join(locked)}
        state["used_week_by_performance"][performance_id] = _answered_card_week(data)
        state["last_result"] = f"Abandoned {performance.display_name} for this answered-card week."
        data["circus"] = state
        return data, True, {"message": state["last_result"]}
    if action_id == "reclaim_costumes":
        inventory = _inventory(data)
        equipment = data.get("equipment")
        equipped = {
            str(item_name)
            for item_name in equipment.values()
            if isinstance(equipment, Mapping) and item_name
        } if isinstance(equipment, Mapping) else set()
        restored = []
        for item_name in state["unlocked_costumes"]:
            if inventory.get(item_name, 0) <= 0 and item_name not in equipped:
                inventory[item_name] = 1
                restored.append(item_name)
        if not restored:
            return data, False, {"reason": "No unlocked Circus costume is missing."}
        data["inventory"] = inventory
        state["last_result"] = "Reclaimed " + ", ".join(restored) + "."
        data["circus"] = state
        return data, True, {
            "message": state["last_result"],
            "outputs": {item: 1 for item in restored},
        }
    return data, False, {"reason": "Unknown Big Top Bonanza action."}


def apply_circus_review_pure(
    player_data: Mapping[str, Any],
    rolls: Sequence[float],
) -> tuple[dict[str, Any], dict[str, Any]]:
    # Shallow on purpose: this only assigns top-level keys on the working copy;
    # the locked-reason helpers are read-only.
    data = dict(player_data)
    state = sanitize_circus_state_pure(data.get("circus"))
    performance = CIRCUS_PERFORMANCES[state["selected_performance"]]
    locked = _performance_locked_reasons(data, performance, state)
    if locked:
        return data, {"allowed": False, "reason": ", ".join(locked)}
    level = min(99, max(1, _int(data.get(_SKILL_LEVEL_KEYS[performance.skill_id]), 1, minimum=1)))
    strategy = state["strategies"][performance.id]
    custom = state["advanced_routines"].get(performance.id, [])
    if state["automation_mode"] == "advanced" and custom:
        tricks_by_id = {trick.id: trick for trick in performance.tricks}
        routine = [tricks_by_id[trick_id] for trick_id in custom]
    else:
        routine = _routine_for_strategy(performance, level, strategy)
    clean_rolls = [max(0.0, min(0.999999, _float(value))) for value in rolls]
    if len(clean_rolls) < len(routine):
        return data, {
            "allowed": False,
            "reason": f"Circus resolution needs {len(routine)} deterministic rolls.",
        }
    awarded_levels: set[int] = set()
    attempted_ids: list[str] = []
    notable: list[str] = []
    xp = 0.0
    score = 0
    successes = 0
    chance_total = 0.0
    for trick, roll in zip(routine, clean_rolls):
        chance = _success_chance(level, trick.level)
        chance_total += chance
        success = roll < chance
        repeated = trick.id in attempted_ids
        attempted_ids.append(trick.id)
        if success:
            successes += 1
            if trick.level not in awarded_levels:
                xp += _barely_success_xp(performance, level, trick)
                awarded_levels.add(trick.level)
        score += _costume_score(
            trick,
            success=success,
            strategy=strategy,
            repeated=repeated,
            unlocked_costume_count=len(state["unlocked_costumes"]),
        )
        if not success or trick.level >= 90:
            notable.append(f"{trick.display_name}: {'success' if success else 'failed'}")

    reward = _reward_for_score(performance.id, score)
    outputs: dict[str, int] = {}
    if reward and reward not in state["unlocked_costumes"]:
        state["unlocked_costumes"].append(reward)
        inventory = _inventory(data)
        inventory[reward] = inventory.get(reward, 0) + 1
        data["inventory"] = inventory
        outputs[reward] = 1
    state["used_week_by_performance"][performance.id] = _answered_card_week(data)
    state["lifetime_performances"] += 1
    state["lifetime_score"] += score
    result_bits = [
        f"{performance.display_name} · {successes}/{len(routine)} tricks",
        f"{xp:,.1f} {performance.skill_id.title()} XP",
        f"score {score:,}",
    ]
    if reward:
        result_bits.append(
            f"unlocked {reward}" if outputs else f"{reward} already unlocked"
        )
    if notable:
        result_bits.append("; ".join(notable[:3]))
    state["last_result"] = " · ".join(result_bits)[:500]
    data["circus"] = state
    return data, {
        "allowed": True,
        "action_id": CIRCUS_ACTIVITY_ID,
        "success": successes > 0,
        "expected_success_chance": chance_total / max(1, len(routine)),
        "terminal": True,
        "completed_activity": True,
        "performance_id": performance.id,
        "skill_id": performance.skill_id,
        "xp": xp,
        "score": score,
        "attempts": len(routine),
        "successes": successes,
        "trick_ids": tuple(attempted_ids),
        "outputs": outputs,
        "status": state["last_result"],
    }
