"""Pure queued, per-card performance loop for Big Top Bonanza."""

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


CIRCUS_STATE_VERSION = 2
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
        "performance_queue": {
            "executing": ["agility"],
            "non_executing": [
                performance_id
                for performance_id in CIRCUS_PERFORMANCE_ORDER
                if performance_id != "agility"
            ],
        },
        "session": None,
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


def _valid_queue_ids(raw: Any) -> list[str]:
    if not isinstance(raw, (list, tuple)):
        return []
    values: list[str] = []
    for value in raw:
        performance_id = str(value)
        if performance_id in CIRCUS_PERFORMANCES and performance_id not in values:
            values.append(performance_id)
    return values


def _default_queue_for_selected(selected: str) -> dict[str, list[str]]:
    return {
        "executing": [selected],
        "non_executing": [
            performance_id
            for performance_id in CIRCUS_PERFORMANCE_ORDER
            if performance_id != selected
        ],
    }


def _sanitize_session(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, Mapping):
        return None
    active = str(raw.get("active_performance", ""))
    if active not in CIRCUS_PERFORMANCES:
        return None
    routine = _valid_routine(active, raw.get("routine"))
    if not routine:
        return None
    return {
        "active_performance": active,
        "routine": routine,
        "trick_index": _int(raw.get("trick_index"), minimum=0),
        "payout_tier_mask": _int(raw.get("payout_tier_mask"), minimum=0),
        "score": _int(raw.get("score"), minimum=0),
        "success_count": _int(raw.get("success_count"), minimum=0),
        "attempted_ids": [
            str(value)
            for value in raw.get("attempted_ids", ())
            if str(value) in {trick.id for trick in CIRCUS_PERFORMANCES[active].tricks}
        ],
    }


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
    raw_queue = source.get("performance_queue")
    if isinstance(raw_queue, Mapping):
        executing = _valid_queue_ids(raw_queue.get("executing"))
        non_executing = _valid_queue_ids(raw_queue.get("non_executing"))
        non_executing = [
            performance_id
            for performance_id in non_executing
            if performance_id not in executing
        ]
        queued = set(executing) | set(non_executing)
        non_executing.extend(
            performance_id
            for performance_id in CIRCUS_PERFORMANCE_ORDER
            if performance_id not in queued
        )
        queue = {"executing": executing, "non_executing": non_executing}
    else:
        queue = _default_queue_for_selected(selected)
    session = _sanitize_session(source.get("session"))
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
        "performance_queue": queue,
        "session": session,
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
    # Darkan f00ca9b6dfb796858cc485c52b3f8d5e7674bfbe, BigTopBonanza.kt:180-181:
    # successChance is clamp(50 + real level - difficulty, 5, 95).
    return max(5, min(95, 50 + level - suggested_level)) / 100.0


def _payout_tier(
    performance: CircusPerformance,
    level: int,
    trick: CircusTrick,
) -> CircusTrick | None:
    if trick.level <= level:
        return next(
            (candidate for candidate in _canonical_by_level(performance)
             if candidate.level == trick.level),
            None,
        )
    # Darkan f00ca9b6dfb796858cc485c52b3f8d5e7674bfbe, BigTopBonanza.kt:183-184:
    # barelyDifficulty chooses the highest tier at or below half the real level.
    target = level // 2
    return max(
        (row for row in _canonical_by_level(performance) if row.level <= target),
        key=lambda row: row.level,
        default=None,
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


def _next_executing_performance(
    player_data: Mapping[str, Any],
    state: Mapping[str, Any],
) -> CircusPerformance | None:
    current_week = _answered_card_week(player_data)
    queue = state["performance_queue"]
    for performance_id in queue["executing"]:
        performance = CIRCUS_PERFORMANCES[performance_id]
        if state["used_week_by_performance"].get(performance_id) == current_week:
            continue
        if _performance_locked_reasons(player_data, performance, state):
            continue
        return performance
    return None


def _routine_for_performance(
    performance: CircusPerformance,
    state: Mapping[str, Any],
    level: int,
) -> list[CircusTrick]:
    strategy = state["strategies"][performance.id]
    custom = state["advanced_routines"].get(performance.id, [])
    if state["automation_mode"] == "advanced" and custom:
        tricks_by_id = {trick.id: trick for trick in performance.tricks}
        return [tricks_by_id[trick_id] for trick_id in custom]
    return _routine_for_strategy(performance, level, strategy)


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
    active_session = state["session"]
    active_performance = (
        CIRCUS_PERFORMANCES[active_session["active_performance"]]
        if active_session
        else None
    )
    next_performance = _next_executing_performance(player_data, state)
    return {
        **state,
        "week_index": current_week,
        "performances": tuple(performance_rows),
        "selected_name": selected.display_name,
        "selected_skill_id": selected.skill_id,
        "selected_locked_reasons": selected_locked,
        "active_performance": active_performance.id if active_performance else "",
        "next_performance": next_performance.id if next_performance else "",
        "can_review": active_session is not None or next_performance is not None,
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
        if state["session"] is not None:
            return data, False, {"reason": "Finish the active Circus performance first."}
        state["selected_performance"] = performance_id
        state["automation_mode"] = mode
        state["strategies"][performance_id] = strategy
        state["performance_queue"] = _default_queue_for_selected(performance_id)
        data["current_utility"] = CIRCUS_ACTIVITY_ID
        state["last_result"] = (
            f"Queued {CIRCUS_PERFORMANCES[performance_id].display_name} · "
            f"{CIRCUS_STRATEGIES[strategy]} · {mode.title()}"
        )
        data["circus"] = state
        return data, True, {"message": state["last_result"]}
    if action_id == "set_queue":
        if state["session"] is not None:
            return data, False, {"reason": "Finish the active Circus performance first."}
        executing = _valid_queue_ids(body.get("executing"))
        non_executing = _valid_queue_ids(body.get("non_executing"))
        if not executing:
            return data, False, {"reason": "Choose at least one executing performance."}
        overlap = set(executing) & set(non_executing)
        if overlap:
            return data, False, {"reason": "A performance can appear in only one queue."}
        queued = set(executing) | set(non_executing)
        non_executing.extend(
            performance_id
            for performance_id in CIRCUS_PERFORMANCE_ORDER
            if performance_id not in queued
        )
        state["performance_queue"] = {
            "executing": executing,
            "non_executing": non_executing,
        }
        state["selected_performance"] = executing[0]
        data["current_utility"] = CIRCUS_ACTIVITY_ID
        state["last_result"] = (
            f"Queued {len(executing)} Circus performance"
            f"{'s' if len(executing) != 1 else ''}."
        )
        data["circus"] = state
        return data, True, {
            "message": state["last_result"],
            "executing": tuple(executing),
            "non_executing": tuple(non_executing),
        }
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
        if state["session"] is not None:
            return data, False, {"reason": "Finish the active Circus performance first."}
        routine = _valid_routine(performance_id, body.get("routine"))
        if not routine:
            return data, False, {"reason": "Choose at least one valid trick."}
        state["advanced_routines"][performance_id] = routine
        state["selected_performance"] = performance_id
        state["automation_mode"] = "advanced"
        if performance_id not in state["performance_queue"]["executing"]:
            state["performance_queue"] = _default_queue_for_selected(performance_id)
        state["last_result"] = (
            f"Saved {len(routine)}-trick routine for "
            f"{CIRCUS_PERFORMANCES[performance_id].display_name}."
        )
        data["circus"] = state
        return data, True, {"message": state["last_result"]}
    if action_id == "abandon":
        active_session = state["session"]
        performance_id = str(
            body.get(
                "performance_id",
                active_session["active_performance"]
                if isinstance(active_session, Mapping)
                else state["selected_performance"],
            )
        )
        performance = CIRCUS_PERFORMANCES.get(performance_id)
        if performance is None:
            return data, False, {"reason": "Choose a valid Circus performance."}
        if active_session is None and performance_id not in state["performance_queue"]["executing"]:
            locked = _performance_locked_reasons(data, performance, state)
            if locked:
                return data, False, {"reason": ", ".join(locked)}
        state["used_week_by_performance"][performance_id] = _answered_card_week(data)
        if (
            isinstance(active_session, Mapping)
            and active_session.get("active_performance") == performance_id
        ):
            state["session"] = None
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
    """Resolve exactly one trick for the next executing performance."""

    data = dict(player_data)
    state = sanitize_circus_state_pure(data.get("circus"))
    clean_rolls = [max(0.0, min(0.999999, _float(value))) for value in rolls]
    if not clean_rolls:
        return data, {"allowed": False, "reason": "Circus resolution needs one deterministic roll."}

    session = state["session"]
    if session is None:
        performance = _next_executing_performance(data, state)
        if performance is None:
            return data, {"allowed": False, "reason": "Choose an available executing Circus performance."}
        level = min(
            99,
            max(
                1,
                _int(
                    data.get(_SKILL_LEVEL_KEYS[performance.skill_id]),
                    1,
                    minimum=1,
                ),
            ),
        )
        routine = _routine_for_performance(performance, state, level)
        session = {
            "active_performance": performance.id,
            "routine": [trick.id for trick in routine],
            "trick_index": 0,
            "payout_tier_mask": 0,
            "score": 0,
            "success_count": 0,
            "attempted_ids": [],
        }
        state["session"] = session
        state["selected_performance"] = performance.id
    else:
        performance = CIRCUS_PERFORMANCES[session["active_performance"]]
        level = min(
            99,
            max(
                1,
                _int(
                    data.get(_SKILL_LEVEL_KEYS[performance.skill_id]),
                    1,
                    minimum=1,
                ),
            ),
        )

    tricks_by_id = {trick.id: trick for trick in performance.tricks}
    routine = [tricks_by_id[trick_id] for trick_id in session["routine"]]
    trick_index = int(session["trick_index"])
    if trick_index >= len(routine):
        return data, {"allowed": False, "reason": "The active Circus performance is out of sync."}
    trick = routine[trick_index]
    chance = _success_chance(level, trick.level)
    success = clean_rolls[0] < chance
    payout_tier = _payout_tier(performance, level, trick) if success else None
    payout_index = (
        _canonical_by_level(performance).index(payout_tier)
        if payout_tier is not None
        else -1
    )
    mask_bit = 1 << payout_index if payout_index >= 0 else 0
    # Darkan f00ca9b6dfb796858cc485c52b3f8d5e7674bfbe, BigTopBonanza.kt:94-117:
    # the once-per-tier mask is checked after the effective payout tier is
    # resolved, so two barely-successful tricks cannot pay the same tier twice.
    xp = (
        payout_tier.xp
        if payout_tier is not None and not session["payout_tier_mask"] & mask_bit
        else 0.0
    )
    if payout_tier is not None and xp > 0:
        session["payout_tier_mask"] |= mask_bit
    repeated = trick.id in session["attempted_ids"]
    session["attempted_ids"].append(trick.id)
    if success:
        session["success_count"] += 1
    score_delta = _costume_score(
        trick,
        success=success,
        strategy=state["strategies"][performance.id],
        repeated=repeated,
        unlocked_costume_count=len(state["unlocked_costumes"]),
    )
    session["score"] += score_delta
    session["trick_index"] += 1
    tier_text = str(payout_tier.level if payout_tier is not None else trick.level)
    result_text = "success" if success else "failure"
    skill_name = performance.skill_id.title()
    trick_event = (
        f"{performance.display_name} · tier {tier_text} · {result_text} · "
        f"+{xp:,.1f} {skill_name} XP · {session['success_count']} successes"
    )
    outputs: dict[str, int] = {}
    summary_event = ""
    completed_performance = session["trick_index"] >= len(routine)
    score = int(session["score"])
    if completed_performance:
        reward = _reward_for_score(performance.id, score)
        if reward and reward not in state["unlocked_costumes"]:
            state["unlocked_costumes"].append(reward)
            inventory = _inventory(data)
            inventory[reward] = inventory.get(reward, 0) + 1
            data["inventory"] = inventory
            outputs[reward] = 1
        state["used_week_by_performance"][performance.id] = _answered_card_week(data)
        state["lifetime_performances"] += 1
        state["lifetime_score"] += score
        summary_event = f"{performance.display_name} complete · score {score:,}"
        state["session"] = None
        state["last_result"] = summary_event[:500]
    else:
        state["last_result"] = trick_event[:500]

    next_performance = _next_executing_performance(data, state)
    terminal = completed_performance and next_performance is None
    data["circus"] = state
    return data, {
        "allowed": True,
        "action_id": CIRCUS_ACTIVITY_ID,
        "success": success,
        "expected_success_chance": chance,
        "terminal": terminal,
        "completed_activity": terminal,
        "completed_performance": completed_performance,
        "performance_id": performance.id,
        "skill_id": performance.skill_id,
        "xp": xp,
        "score": score,
        "score_awarded": score_delta,
        "attempts": 1,
        "successes": int(success),
        "trick_index": trick_index,
        "trick_id": trick.id,
        "trick_event": trick_event,
        "summary_event": summary_event,
        "outputs": outputs,
        "status": trick_event,
    }
