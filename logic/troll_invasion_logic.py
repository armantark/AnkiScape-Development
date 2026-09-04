"""Pure monthly Troll Invasion combat, repair, reward-book, and view mechanics."""

from __future__ import annotations

import copy
from collections.abc import Callable, Mapping
from typing import Any

from ..core.skill_registry import trainable_skill_definitions
from ..data.troll_invasion_data import (
    TROLL_INVASION_ACTIVITY_ID,
    TROLL_INVASION_COMBAT_MODE,
    TROLL_INVASION_COMBAT_TARGET_ID,
    TROLL_INVASION_COMBAT_TICKS,
    TROLL_INVASION_DIFFICULTIES,
    TROLL_INVASION_DYNAMITE_SUPPLY_CHANCE,
    TROLL_INVASION_HARD,
    TROLL_INVASION_HARD_WAVES,
    TROLL_INVASION_MODES,
    TROLL_INVASION_MONTH_REVIEWS,
    TROLL_INVASION_MORALE_PER_ACTION,
    TROLL_INVASION_MORALE_POWER_REPAIR,
    TROLL_INVASION_MORALE_POWER_THRESHOLD,
    TROLL_INVASION_REPAIR_ACTION_CEILING,
    TROLL_INVASION_REPAIR_JOBS,
    TROLL_INVASION_REPAIR_MODE,
    TROLL_INVASION_REPAIR_PRESSURE,
    TROLL_INVASION_REPAIR_INTERRUPTION_CHANCE,
    TROLL_INVASION_REPAIR_SEVERE_PRESSURE,
    TROLL_INVASION_REPAIR_SEVERE_PRESSURE_CHANCE,
    TROLL_INVASION_REPAIR_TROLLS_PER_ACTION,
    TROLL_INVASION_REPAIR_TROLL_TARGET,
    TROLL_INVASION_REWARD_ALLOWANCE_CAP,
    TROLL_INVASION_REWARD_BOOK,
    TROLL_INVASION_SOURCE,
    TROLL_INVASION_STANDARD,
    TROLL_INVASION_STANDARD_WAVES,
    TROLL_INVASION_SUPPLY_USES_PER_WAVE,
    troll_invasion_wave_front_pure,
)
from ..logic_pure.logic_pure import (
    apply_combat_burst_pure,
    combat_max_lifepoints_pure,
)


TROLL_INVASION_STATE_VERSION = 1
_MODE_IDS = frozenset(row["id"] for row in TROLL_INVASION_MODES)
_DIFFICULTY_IDS = frozenset(row["id"] for row in TROLL_INVASION_DIFFICULTIES)
_REPAIR_JOB_IDS = tuple(row["id"] for row in TROLL_INVASION_REPAIR_JOBS)
_REPAIR_JOBS_BY_ID = {row["id"]: row for row in TROLL_INVASION_REPAIR_JOBS}
_TRAINABLE_SKILLS_BY_ID = {skill.id: skill for skill in trainable_skill_definitions()}
_TRAINABLE_SKILL_IDS = frozenset(_TRAINABLE_SKILLS_BY_ID)


def _int(value: Any, default: int = 0, *, minimum: int = 0, maximum: int = 2_147_483_647) -> int:
    if isinstance(value, bool):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(minimum, min(parsed, maximum))


def _float(value: Any, default: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        return default
    return parsed if parsed == parsed and parsed not in (float("inf"), float("-inf")) else default


def _answered_cards(player_data: Mapping[str, Any]) -> int:
    clock = player_data.get("shop_market_clock")
    return _int(clock.get("answered_cards")) if isinstance(clock, Mapping) else 0


def _world_month(player_data: Mapping[str, Any]) -> int:
    return _answered_cards(player_data) // TROLL_INVASION_MONTH_REVIEWS


def default_troll_invasion_state_pure() -> dict[str, Any]:
    return {
        "troll_invasion": {},
        "troll_invasion_policy": {
            "mode": TROLL_INVASION_COMBAT_MODE,
            "difficulty": TROLL_INVASION_STANDARD,
            "reward_skill": "agility",
        },
        "troll_invasion_hard_unlocked": False,
        "troll_invasion_attempts": 0,
        "troll_invasion_completions": 0,
        "troll_invasion_failures": 0,
        "troll_invasion_exits": 0,
        "troll_invasion_reward_month_index": -1,
        "troll_invasion_reward_allowances": 0,
        "troll_invasion_reward_fractions": [],
        "troll_invasion_books_redeemed": 0,
        "troll_invasion_last_result": "",
    }


def _sanitize_policy(raw: Any) -> dict[str, str]:
    source = raw if isinstance(raw, Mapping) else {}
    mode = str(source.get("mode", TROLL_INVASION_COMBAT_MODE))
    difficulty = str(source.get("difficulty", TROLL_INVASION_STANDARD))
    reward_skill = str(source.get("reward_skill", "agility"))
    return {
        "mode": mode if mode in _MODE_IDS else TROLL_INVASION_COMBAT_MODE,
        "difficulty": difficulty if difficulty in _DIFFICULTY_IDS else TROLL_INVASION_STANDARD,
        "reward_skill": reward_skill if reward_skill in _TRAINABLE_SKILL_IDS else "agility",
    }


def _sanitize_components(raw: Any) -> dict[str, int]:
    source = raw if isinstance(raw, Mapping) else {}
    return {job_id: _int(source.get(job_id), 100, maximum=100) for job_id in _REPAIR_JOB_IDS}


def _sanitize_session(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}
    mode = str(raw.get("mode", ""))
    if mode not in _MODE_IDS:
        return {}
    difficulty = str(raw.get("difficulty", TROLL_INVASION_STANDARD))
    if difficulty not in _DIFFICULTY_IDS:
        difficulty = TROLL_INVASION_STANDARD
    total_waves = TROLL_INVASION_HARD_WAVES if difficulty == TROLL_INVASION_HARD else TROLL_INVASION_STANDARD_WAVES
    wave = _int(raw.get("wave"), 1, minimum=1, maximum=total_waves)
    maximum = 0
    if mode == TROLL_INVASION_COMBAT_MODE:
        front = troll_invasion_wave_front_pure(difficulty, wave)
        maximum = int(front["stats"]["hitpoints"])
    lifepoints = _int(raw.get("enemy_lifepoints"), maximum, maximum=maximum)
    encounter = raw.get("encounter")
    return {
        "version": TROLL_INVASION_STATE_VERSION,
        "mode": mode,
        "difficulty": difficulty,
        "wave": wave,
        "waves_completed": _int(raw.get("waves_completed"), maximum=total_waves),
        "enemy_lifepoints": lifepoints if mode == TROLL_INVASION_COMBAT_MODE else 0,
        "encounter": copy.deepcopy(dict(encounter)) if isinstance(encounter, Mapping) else {},
        "supply_uses": _int(raw.get("supply_uses"), TROLL_INVASION_SUPPLY_USES_PER_WAVE, maximum=TROLL_INVASION_SUPPLY_USES_PER_WAVE),
        "supply_destroyed": bool(raw.get("supply_destroyed", False)),
        "components": _sanitize_components(raw.get("components")),
        "morale": _int(raw.get("morale"), maximum=TROLL_INVASION_MORALE_POWER_THRESHOLD),
        "repair_actions": _int(raw.get("repair_actions"), maximum=TROLL_INVASION_REPAIR_ACTION_CEILING),
        "trolls_defeated": _int(raw.get("trolls_defeated"), maximum=TROLL_INVASION_REPAIR_TROLL_TARGET),
        "previous_combat_target": str(raw.get("previous_combat_target", ""))[:120],
    }


def sanitize_troll_invasion_state_pure(player_data: Mapping[str, Any] | None) -> dict[str, Any]:
    source = player_data or {}
    session = _sanitize_session(source.get("troll_invasion"))
    active = source.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if session and active_id not in {"", TROLL_INVASION_ACTIVITY_ID}:
        session = {}
    raw_fractions = source.get("troll_invasion_reward_fractions")
    fractions = []
    if isinstance(raw_fractions, (list, tuple)):
        for value in raw_fractions:
            fraction = max(0.0, min(1.0, _float(value)))
            if fraction > 0:
                fractions.append(fraction)
    inventory = source.get("inventory")
    held_books = _int(inventory.get(TROLL_INVASION_REWARD_BOOK)) if isinstance(inventory, Mapping) else 0
    fractions = fractions[:held_books]
    return {
        "troll_invasion": session,
        "troll_invasion_policy": _sanitize_policy(source.get("troll_invasion_policy")),
        "troll_invasion_hard_unlocked": bool(source.get("troll_invasion_hard_unlocked", False)),
        "troll_invasion_attempts": _int(source.get("troll_invasion_attempts")),
        "troll_invasion_completions": _int(source.get("troll_invasion_completions")),
        "troll_invasion_failures": _int(source.get("troll_invasion_failures")),
        "troll_invasion_exits": _int(source.get("troll_invasion_exits")),
        "troll_invasion_reward_month_index": max(-1, _int(source.get("troll_invasion_reward_month_index"), -1, minimum=-1)),
        "troll_invasion_reward_allowances": min(TROLL_INVASION_REWARD_ALLOWANCE_CAP, _int(source.get("troll_invasion_reward_allowances"))),
        "troll_invasion_reward_fractions": fractions,
        "troll_invasion_books_redeemed": _int(source.get("troll_invasion_books_redeemed")),
        "troll_invasion_last_result": str(source.get("troll_invasion_last_result", ""))[:500],
    }


def _sync_reward_allowances(state: Mapping[str, Any], player_data: Mapping[str, Any]) -> dict[str, Any]:
    synced = dict(state)
    current = _world_month(player_data)
    previous = _int(synced.get("troll_invasion_reward_month_index"), -1, minimum=-1)
    if previous < 0:
        synced["troll_invasion_reward_month_index"] = current
        synced["troll_invasion_reward_allowances"] = max(1, _int(synced.get("troll_invasion_reward_allowances")))
    elif current > previous:
        synced["troll_invasion_reward_allowances"] = min(
            TROLL_INVASION_REWARD_ALLOWANCE_CAP,
            _int(synced.get("troll_invasion_reward_allowances")) + current - previous,
        )
        synced["troll_invasion_reward_month_index"] = current
    return synced


def troll_invasion_reward_xp_pure(level: int, fraction: float) -> float:
    clean_level = max(1, min(99, int(level)))
    clean_fraction = max(0.0, min(1.0, float(fraction)))
    return 8.0 * clean_fraction * (clean_level * clean_level - 2 * clean_level + 100)


def _reward_skill_rows(player_data: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "id": skill.id,
            "display_name": skill.display_name,
            "level": max(1, _int(player_data.get(skill.level_key), 1, minimum=1, maximum=99)),
            "selected": False,
        }
        for skill in _TRAINABLE_SKILLS_BY_ID.values()
    )


def troll_invasion_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = _sync_reward_allowances(sanitize_troll_invasion_state_pure(player_data), player_data)
    session = state["troll_invasion"]
    policy = state["troll_invasion_policy"]
    active = player_data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    encounter = player_data.get("combat_encounter")
    reasons = []
    if active_id and active_id != TROLL_INVASION_ACTIVITY_ID:
        reasons.append("Finish the active persistent activity.")
    if not session and isinstance(encounter, Mapping) and encounter:
        reasons.append("Finish or leave the current Combat encounter.")
    difficulty = session["difficulty"] if session else policy["difficulty"]
    mode = session["mode"] if session else policy["mode"]
    total_waves = TROLL_INVASION_HARD_WAVES if difficulty == TROLL_INVASION_HARD else TROLL_INVASION_STANDARD_WAVES
    if session and mode == TROLL_INVASION_COMBAT_MODE:
        progress_value = int(session["waves_completed"])
        progress_maximum = total_waves
        progress_format = f"{progress_value}/{total_waves} waves cleared"
        summary = f"{difficulty.title()} wave {session['wave']}/{total_waves} · {session['enemy_lifepoints']} front LP"
    elif session:
        progress_value = int(session["trolls_defeated"])
        progress_maximum = TROLL_INVASION_REPAIR_TROLL_TARGET
        progress_format = f"{progress_value}/{TROLL_INVASION_REPAIR_TROLL_TARGET} trolls defeated"
        components = ", ".join(f"{key} {value}%" for key, value in session["components"].items())
        summary = f"Gatehouse repair · morale {session['morale']} · {components}"
    else:
        progress_value = 0
        progress_maximum = total_waves if mode == TROLL_INVASION_COMBAT_MODE else TROLL_INVASION_REPAIR_TROLL_TARGET
        progress_format = "Choose a route and enter"
        summary = state["troll_invasion_last_result"] or "A safe solo defence with Combat and gatehouse Repair routes."
    reward_skill_rows = []
    for row in _reward_skill_rows(player_data):
        clean = dict(row)
        clean["selected"] = clean["id"] == policy["reward_skill"]
        reward_skill_rows.append(clean)
    has_book = bool(state["troll_invasion_reward_fractions"])
    can_enter = not reasons and not session
    selected_for_reviews = str(player_data.get("current_utility", "")) == TROLL_INVASION_ACTIVITY_ID
    return {
        **state,
        "active": bool(session),
        "can_enter": can_enter,
        "entry_reasons": tuple(reasons),
        "selected_mode": mode,
        "selected_difficulty": difficulty,
        "mode_options": tuple({**row, "selectable": can_enter or row["id"] == mode} for row in TROLL_INVASION_MODES),
        "difficulty_options": tuple(
            {
                **row,
                "unlocked": row["id"] != TROLL_INVASION_HARD
                or state["troll_invasion_hard_unlocked"],
                "selectable": (
                    can_enter
                    and (
                        row["id"] != TROLL_INVASION_HARD
                        or state["troll_invasion_hard_unlocked"]
                    )
                )
                or (bool(session) and row["id"] == difficulty),
            }
            for row in TROLL_INVASION_DIFFICULTIES
        ),
        "difficulty_visible": mode == TROLL_INVASION_COMBAT_MODE,
        "summary_text": summary,
        "status_label": "ACTIVE · SAFE" if session else f"{state['troll_invasion_reward_allowances']} MONTHLY REWARD{'S' if state['troll_invasion_reward_allowances'] != 1 else ''}",
        "progress_value": progress_value,
        "progress_maximum": progress_maximum,
        "progress_format": progress_format,
        "policy_controls_enabled": can_enter,
        "primary_label": "Active for reviews" if session and selected_for_reviews else "Select for reviews" if session else "Enter invasion",
        "primary_enabled": (bool(session) and not selected_for_reviews) or can_enter,
        "leave_visible": bool(session),
        "leave_enabled": bool(session),
        "reward_skill_options": tuple(reward_skill_rows),
        "reward_visible": has_book,
        "reward_enabled": has_book and not session,
        "reward_book_count": len(state["troll_invasion_reward_fractions"]),
        "next_reward_fraction": state["troll_invasion_reward_fractions"][0] if has_book else 0.0,
        "source": TROLL_INVASION_SOURCE,
    }


def set_troll_invasion_policy_pure(player_data: Mapping[str, Any], payload: Mapping[str, Any]) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = _sync_reward_allowances(sanitize_troll_invasion_state_pure(data), data)
    if state["troll_invasion"]:
        return data, False, {"reason": "Finish or leave the active Troll Invasion first."}
    policy = dict(state["troll_invasion_policy"])
    mode = str(payload.get("mode", policy["mode"]))
    difficulty = str(payload.get("difficulty", policy["difficulty"]))
    reward_skill = str(payload.get("reward_skill", policy["reward_skill"]))
    if mode not in _MODE_IDS:
        return data, False, {"reason": "Unknown Troll Invasion route."}
    if difficulty not in _DIFFICULTY_IDS:
        return data, False, {"reason": "Unknown Troll Invasion Combat difficulty."}
    if difficulty == TROLL_INVASION_HARD and not state["troll_invasion_hard_unlocked"]:
        return data, False, {"reason": "Attempt Standard Combat once to unlock Hard Combat."}
    if reward_skill not in _TRAINABLE_SKILL_IDS:
        return data, False, {"reason": "Choose a trainable reward skill."}
    data.update(state)
    data["troll_invasion_policy"] = {"mode": mode, "difficulty": difficulty, "reward_skill": reward_skill}
    return data, True, {"message": f"Troll Invasion plan saved · {mode.title()} · {difficulty.title()} Combat · {reward_skill.title()} reward."}


def enter_troll_invasion_pure(player_data: Mapping[str, Any], payload: Mapping[str, Any] | None = None) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = _sync_reward_allowances(sanitize_troll_invasion_state_pure(data), data)
    if state["troll_invasion"]:
        data.update(state)
        data["activity_session"] = {"active_id": TROLL_INVASION_ACTIVITY_ID}
        data["current_utility"] = TROLL_INVASION_ACTIVITY_ID
        return data, True, {"message": "Troll Invasion selected for reviews."}
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if active_id and active_id != TROLL_INVASION_ACTIVITY_ID:
        return data, False, {"reason": "Finish the active persistent activity first."}
    encounter = data.get("combat_encounter")
    if isinstance(encounter, Mapping) and encounter:
        return data, False, {"reason": "Finish or leave the current Combat encounter first."}
    body = payload if isinstance(payload, Mapping) else {}
    policy = dict(state["troll_invasion_policy"])
    mode = str(body.get("mode", policy["mode"]))
    difficulty = str(body.get("difficulty", policy["difficulty"]))
    if mode not in _MODE_IDS or difficulty not in _DIFFICULTY_IDS:
        return data, False, {"reason": "Choose a valid Troll Invasion route."}
    if mode == TROLL_INVASION_COMBAT_MODE and difficulty == TROLL_INVASION_HARD and not state["troll_invasion_hard_unlocked"]:
        return data, False, {"reason": "Attempt Standard Combat once to unlock Hard Combat."}
    if mode == TROLL_INVASION_COMBAT_MODE and difficulty == TROLL_INVASION_STANDARD:
        state["troll_invasion_hard_unlocked"] = True
    previous_target = str(data.get("current_combat_target", ""))[:120]
    front = troll_invasion_wave_front_pure(difficulty, 1)
    session = {
        "version": TROLL_INVASION_STATE_VERSION,
        "mode": mode,
        "difficulty": difficulty,
        "wave": 1,
        "waves_completed": 0,
        "enemy_lifepoints": int(front["stats"]["hitpoints"]) if mode == TROLL_INVASION_COMBAT_MODE else 0,
        "encounter": {},
        "supply_uses": TROLL_INVASION_SUPPLY_USES_PER_WAVE,
        "supply_destroyed": False,
        "components": _sanitize_components(None),
        "morale": 0,
        "repair_actions": 0,
        "trolls_defeated": 0,
        "previous_combat_target": previous_target,
    }
    data.update(state)
    data["troll_invasion_attempts"] = state["troll_invasion_attempts"] + 1
    data["troll_invasion_policy"] = {**policy, "mode": mode, "difficulty": difficulty}
    data["troll_invasion"] = session
    data["activity_session"] = {"active_id": TROLL_INVASION_ACTIVITY_ID}
    data["current_utility"] = TROLL_INVASION_ACTIVITY_ID
    if mode == TROLL_INVASION_COMBAT_MODE:
        data["current_combat_target"] = TROLL_INVASION_COMBAT_TARGET_ID
        data["combat_encounter"] = {}
    message = f"Entered Troll Invasion · {mode.title()}" + (f" · {difficulty.title()}" if mode == TROLL_INVASION_COMBAT_MODE else "") + "."
    data["troll_invasion_last_result"] = message
    return data, True, {"message": message}


def _book_inventory(data: dict[str, Any], delta: int) -> None:
    inventory = dict(data.get("inventory")) if isinstance(data.get("inventory"), Mapping) else {}
    total = _int(inventory.get(TROLL_INVASION_REWARD_BOOK)) + delta
    if total > 0:
        inventory[TROLL_INVASION_REWARD_BOOK] = total
    else:
        inventory.pop(TROLL_INVASION_REWARD_BOOK, None)
    data["inventory"] = inventory


def _award_monthly_book(data: dict[str, Any], fraction: float) -> bool:
    allowances = _int(data.get("troll_invasion_reward_allowances"))
    clean = max(0.0, min(1.0, float(fraction)))
    if allowances <= 0 or clean <= 0:
        return False
    fractions = list(data.get("troll_invasion_reward_fractions") or [])
    fractions.append(clean)
    data["troll_invasion_reward_fractions"] = fractions
    data["troll_invasion_reward_allowances"] = allowances - 1
    _book_inventory(data, 1)
    return True


def _finish(data: dict[str, Any], session: Mapping[str, Any], message: str) -> None:
    data["troll_invasion"] = {}
    data["activity_session"] = {"active_id": ""}
    data["combat_encounter"] = {}
    data["current_combat_target"] = str(session.get("previous_combat_target", ""))
    data["troll_invasion_last_result"] = message[:500]


# PLACEHOLDER(troll_invasion.partial_reward_semantics): authentic partial-wave
# numerator, Repair partial fraction, and reward-book XP rounding rule.
def _completion_fraction(session: Mapping[str, Any]) -> float:
    if session["mode"] == TROLL_INVASION_COMBAT_MODE:
        total = TROLL_INVASION_HARD_WAVES if session["difficulty"] == TROLL_INVASION_HARD else TROLL_INVASION_STANDARD_WAVES
        return min(1.0, int(session["waves_completed"]) / total)
    if int(session["repair_actions"]) >= TROLL_INVASION_REPAIR_ACTION_CEILING:
        return 1.0
    return min(1.0, int(session["trolls_defeated"]) / TROLL_INVASION_REPAIR_TROLL_TARGET)


def _settle(data: dict[str, Any], session: Mapping[str, Any], outcome: str) -> dict[str, Any]:
    fraction = _completion_fraction(session)
    complete = fraction >= 1.0
    if complete:
        data["troll_invasion_completions"] = _int(data.get("troll_invasion_completions")) + 1
    elif outcome == "failure":
        data["troll_invasion_failures"] = _int(data.get("troll_invasion_failures")) + 1
    elif outcome == "exit":
        data["troll_invasion_exits"] = _int(data.get("troll_invasion_exits")) + 1
    book_awarded = _award_monthly_book(data, fraction)
    label = "Troll Invasion complete" if complete else "Troll Invasion partial cash-out"
    message = f"{label} · {fraction:.1%} completion" + (" · reward book" if book_awarded else " · no monthly book available")
    _finish(data, session, message)
    return {"terminal": True, "complete": complete, "outcome": outcome, "completion_fraction": fraction, "book_awarded": book_awarded, "message": message}


def _restore_from_supply(data: dict[str, Any], session: dict[str, Any]) -> bool:
    if session["supply_destroyed"] or session["supply_uses"] <= 0:
        return False
    maximum = combat_max_lifepoints_pure(data)
    current = _int(data.get("combat_lifepoints"), maximum, maximum=maximum)
    if current > maximum // 2:
        return False
    data["combat_lifepoints"] = maximum
    data["combat_prayer_points"] = max(1, _int(data.get("prayer_level"), 1, minimum=1)) * 10
    data["combat_status_effects"] = {}
    session["supply_uses"] -= 1
    return True


def _apply_combat_review(data: dict[str, Any], state: Mapping[str, Any], session: dict[str, Any], rng: Callable[[], float], equipment_data: Mapping[str, Any]) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    supply_used = _restore_from_supply(data, session)
    supply_destroyed_now = False
    if not session["supply_destroyed"]:
        try:
            supply_destroyed_now = float(rng()) < TROLL_INVASION_DYNAMITE_SUPPLY_CHANCE
        except (TypeError, ValueError, OverflowError):
            supply_destroyed_now = False
        if supply_destroyed_now:
            session["supply_destroyed"] = True
            session["supply_uses"] = 0
    front = troll_invasion_wave_front_pure(session["difficulty"], session["wave"])
    encounter = dict(session["encounter"])
    encounter["target_id"] = TROLL_INVASION_COMBAT_TARGET_ID
    encounter["enemy_lifepoints"] = int(session["enemy_lifepoints"])
    data["current_combat_target"] = TROLL_INVASION_COMBAT_TARGET_ID
    data["combat_encounter"] = encounter
    original_auto_flee = bool(data.get("combat_auto_flee", True))
    data["combat_auto_flee"] = False
    data, ok, combat = apply_combat_burst_pure(
        data,
        {TROLL_INVASION_COMBAT_TARGET_ID: front},
        equipment_data,
        ticks=TROLL_INVASION_COMBAT_TICKS,
        rng=rng,
        live_cadence=True,
        stop_after_first_kill=True,
        safe_death=True,
        allow_bank_run=False,
    )
    data["combat_auto_flee"] = original_auto_flee
    if not ok:
        return data, False, {"reason": "Troll Invasion combat setup is not runnable.", "combat": combat}
    if combat.get("died") or combat.get("fled"):
        data.update(state)
        data["troll_invasion"] = session
        return data, True, {"combat": combat, "supply_used": supply_used, "supply_destroyed": supply_destroyed_now, **_settle(data, session, "failure")}
    if combat.get("killed"):
        session["waves_completed"] += 1
        total = TROLL_INVASION_HARD_WAVES if session["difficulty"] == TROLL_INVASION_HARD else TROLL_INVASION_STANDARD_WAVES
        if session["waves_completed"] >= total:
            data.update(state)
            data["troll_invasion"] = session
            return data, True, {"combat": combat, "supply_used": supply_used, "supply_destroyed": supply_destroyed_now, **_settle(data, session, "complete")}
        session["wave"] += 1
        next_front = troll_invasion_wave_front_pure(session["difficulty"], session["wave"])
        session["enemy_lifepoints"] = int(next_front["stats"]["hitpoints"])
        session["encounter"] = {}
        session["supply_uses"] = 0 if session["supply_destroyed"] else TROLL_INVASION_SUPPLY_USES_PER_WAVE
        data["combat_encounter"] = {}
    else:
        encounter_after = data.get("combat_encounter")
        if isinstance(encounter_after, Mapping):
            session["enemy_lifepoints"] = _int(encounter_after.get("enemy_lifepoints"), session["enemy_lifepoints"])
            session["encounter"] = dict(encounter_after)
    data.update(state)
    data["troll_invasion"] = session
    message = f"Troll Invasion · wave {session['wave']} · {session['enemy_lifepoints']} front LP"
    if supply_used:
        message += " · supply table restored you"
    if supply_destroyed_now:
        message += " · Dynamite troll destroyed the supply table"
    data["troll_invasion_last_result"] = message
    return data, True, {"terminal": False, "combat": combat, "supply_used": supply_used, "supply_destroyed": supply_destroyed_now, "message": message}


def _apply_repair_review(
    data: dict[str, Any],
    state: Mapping[str, Any],
    session: dict[str, Any],
    rng: Callable[[], float],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    before = dict(session["components"])
    job_id = min(_REPAIR_JOB_IDS, key=lambda candidate: before[candidate])
    job = _REPAIR_JOBS_BY_ID[job_id]
    try:
        pressure_roll = max(0.0, min(0.999999, float(rng())))
    except (TypeError, ValueError, OverflowError):
        pressure_roll = 0.999999
    try:
        interruption_roll = max(0.0, min(0.999999, float(rng())))
    except (TypeError, ValueError, OverflowError):
        interruption_roll = 0.999999
    pressure = (
        TROLL_INVASION_REPAIR_SEVERE_PRESSURE
        if pressure_roll < TROLL_INVASION_REPAIR_SEVERE_PRESSURE_CHANCE
        else TROLL_INVASION_REPAIR_PRESSURE
    )
    interrupted = interruption_roll < TROLL_INVASION_REPAIR_INTERRUPTION_CHANCE
    emergency = before[job_id] <= TROLL_INVASION_REPAIR_SEVERE_PRESSURE
    components = dict(before)
    components[job_id] = min(100, components[job_id] + int(job["repair"]))
    session["repair_actions"] += 1
    credited_trolls = (
        0
        if emergency or interrupted
        else TROLL_INVASION_REPAIR_TROLLS_PER_ACTION
    )
    session["trolls_defeated"] = min(
        TROLL_INVASION_REPAIR_TROLL_TARGET,
        session["trolls_defeated"] + credited_trolls,
    )
    session["morale"] = min(
        TROLL_INVASION_MORALE_POWER_THRESHOLD,
        session["morale"] + TROLL_INVASION_MORALE_PER_ACTION,
    )
    morale_power = False
    if session["morale"] >= TROLL_INVASION_MORALE_POWER_THRESHOLD:
        weakest = min(_REPAIR_JOB_IDS, key=lambda candidate: components[candidate])
        components[weakest] = min(
            100, components[weakest] + TROLL_INVASION_MORALE_POWER_REPAIR
        )
        session["morale"] = 0
        morale_power = True
    for candidate in components:
        components[candidate] = max(0, components[candidate] - pressure)
    session["components"] = components
    data.update(state)
    data["troll_invasion"] = session
    skill_xp = {job["skill_id"]: float(job["xp"])}
    common = {
        "skill_id": job["skill_id"],
        "skill_xp": skill_xp,
        "job": job_id,
        "morale_power": morale_power,
        "interrupted": interrupted,
        "emergency": emergency,
        "pressure": pressure,
        "credited_trolls": credited_trolls,
    }
    if min(components.values()) <= 0:
        return data, True, {**common, **_settle(data, session, "failure")}
    if (
        session["trolls_defeated"] >= TROLL_INVASION_REPAIR_TROLL_TARGET
        or session["repair_actions"] >= TROLL_INVASION_REPAIR_ACTION_CEILING
    ):
        return data, True, {**common, **_settle(data, session, "complete")}
    message = (
        f"Repaired {job['display_name']} · +{job['xp']:.0f} "
        f"{job['skill_id'].title()} XP · +{credited_trolls} troll credit"
    )
    if interrupted:
        message += " · troll attack interrupted the defence credit"
    if pressure > TROLL_INVASION_REPAIR_PRESSURE:
        message += " · heavy troll pressure"
    if morale_power:
        message += " · morale reinforced the weakest component"
    data["troll_invasion_last_result"] = message
    return data, True, {"terminal": False, **common, "message": message}


def apply_troll_invasion_review_pure(
    player_data: Mapping[str, Any],
    rng: Callable[[], float],
    *,
    equipment_data: Mapping[str, Any] | None = None,
    productive: bool = True,
    steps: int = 1,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = _sync_reward_allowances(sanitize_troll_invasion_state_pure(data), data)
    session = state["troll_invasion"]
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if not session or active_id != TROLL_INVASION_ACTIVITY_ID:
        return data, False, {"reason": "Enter Troll Invasion before training it."}
    if not productive:
        return data, True, {"advanced": False, "terminal": False, "actions_resolved": 0, "message": "Troll Invasion advances only on an eligible successful review."}
    if session["mode"] == TROLL_INVASION_COMBAT_MODE:
        return _apply_combat_review(data, state, session, rng, equipment_data or {})

    combined_skill_xp: dict[str, float] = {}
    jobs: list[str] = []
    morale_powers = 0
    result: dict[str, Any] = {}
    for _ in range(max(1, int(steps))):
        data, ok, result = _apply_repair_review(data, state, session, rng)
        if not ok:
            return data, False, result
        jobs.append(str(result["job"]))
        morale_powers += int(bool(result["morale_power"]))
        for skill_id, amount in result["skill_xp"].items():
            combined_skill_xp[skill_id] = (
                combined_skill_xp.get(skill_id, 0.0) + float(amount)
            )
        if result.get("terminal"):
            break
    return data, True, {
        **result,
        "skill_xp": combined_skill_xp,
        "jobs": tuple(jobs),
        "morale_powers": morale_powers,
        "actions_resolved": len(jobs),
    }


def leave_troll_invasion_pure(player_data: Mapping[str, Any]) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = _sync_reward_allowances(sanitize_troll_invasion_state_pure(data), data)
    session = state["troll_invasion"]
    if not session:
        return data, False, {"reason": "No Troll Invasion run is active."}
    data.update(state)
    data["troll_invasion"] = session
    return data, True, _settle(data, session, "exit")


def redeem_troll_invasion_book_pure(player_data: Mapping[str, Any], skill_id: str) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = _sync_reward_allowances(sanitize_troll_invasion_state_pure(data), data)
    if state["troll_invasion"]:
        return data, False, {"reason": "Finish the active Troll Invasion before reading its reward book."}
    skill = _TRAINABLE_SKILLS_BY_ID.get(skill_id)
    if skill is None:
        return data, False, {"reason": "Choose a trainable skill for the reward book."}
    fractions = list(state["troll_invasion_reward_fractions"])
    if not fractions:
        return data, False, {"reason": "No Troll Invasion reward book is waiting."}
    fraction = float(fractions.pop(0))
    level = max(1, _int(data.get(skill.level_key), 1, minimum=1, maximum=99))
    awarded = troll_invasion_reward_xp_pure(level, fraction)
    data.update(state)
    data["troll_invasion_reward_fractions"] = fractions
    data["troll_invasion_books_redeemed"] = state["troll_invasion_books_redeemed"] + 1
    data["troll_invasion_policy"] = {**state["troll_invasion_policy"], "reward_skill": skill_id}
    _book_inventory(data, -1)
    message = f"Read the Troll Invasion reward book · +{awarded:,.0f} {skill.display_name} XP at {fraction:.1%} completion."
    data["troll_invasion_last_result"] = message
    return data, True, {"message": message, "skill_id": skill_id, "xp_rewards": {skill.exp_key: awarded}, "completion_fraction": fraction}


def apply_troll_invasion_command_pure(player_data: Mapping[str, Any], action_id: str, payload: Mapping[str, Any] | None = None) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    body = payload if isinstance(payload, Mapping) else {}
    if action_id == "set_policy":
        return set_troll_invasion_policy_pure(player_data, body)
    if action_id == "enter":
        return enter_troll_invasion_pure(player_data, body)
    if action_id == "leave":
        return leave_troll_invasion_pure(player_data)
    if action_id == "redeem_book":
        return redeem_troll_invasion_book_pure(player_data, str(body.get("skill_id", "")))
    return copy.deepcopy(dict(player_data)), False, {"reason": "Unknown Troll Invasion command."}
