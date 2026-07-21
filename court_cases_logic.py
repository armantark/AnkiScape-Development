"""Pure entry, preparation, trial, verdict, and reward mechanics for Court Cases."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any

try:
    from .court_cases_data import (
        COURT_CASES_BATCH2_COOLDOWN_REVIEWS,
        COURT_CASE_ORDER,
        COURT_CASES,
        COURT_CASES_ACTIVITY_ID,
        COURT_ROLE_LABELS,
    )
except ImportError:  # pragma: no cover - flat test imports
    from court_cases_data import (  # type: ignore
        COURT_CASES_BATCH2_COOLDOWN_REVIEWS,
        COURT_CASE_ORDER,
        COURT_CASES,
        COURT_CASES_ACTIVITY_ID,
        COURT_ROLE_LABELS,
    )


COURT_CASES_STATE_VERSION = 1


def _int(value: Any, default: int = 0, *, maximum: int = 2_147_483_647) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(0, min(parsed, maximum))


def court_summons_can_be_received_pure(player_data: Mapping[str, Any]) -> bool:
    completed = player_data.get("court_cases_completed_ids")
    completed_ids = (
        {str(case_id) for case_id in completed}
        if isinstance(completed, (tuple, list))
        else set()
    )
    if "mugger" not in completed_ids:
        return False
    if all(case_id in completed_ids for case_id in COURT_CASE_ORDER):
        return False
    inventory = player_data.get("inventory")
    if isinstance(inventory, Mapping) and _int(inventory.get("Court summons")) > 0:
        return False
    session = player_data.get("court_cases")
    return not isinstance(session, Mapping) or not bool(session)


def filter_court_summons_outputs_pure(
    player_data: Mapping[str, Any], outputs: Mapping[str, Any]
) -> dict[str, int]:
    filtered = {
        str(item): _int(amount)
        for item, amount in outputs.items()
        if _int(amount) > 0
    }
    if "Court summons" in filtered:
        if court_summons_can_be_received_pure(player_data):
            filtered["Court summons"] = 1
        else:
            filtered.pop("Court summons", None)
    return filtered


def default_court_cases_state_pure() -> dict[str, Any]:
    return {
        "court_cases": {},
        "court_cases_policy": {
            "role": "prosecution",
            "automation_mode": "casual",
        },
        "court_cases_completed_ids": [],
        "court_cases_attempts": 0,
        "court_cases_batch2_ready_at_review": 0,
        "court_cases_last_result": "Your first case is free.",
    }


def sanitize_court_cases_policy_pure(raw: Any) -> dict[str, str]:
    source = raw if isinstance(raw, Mapping) else {}
    role = str(source.get("role", "prosecution"))
    if role not in COURT_ROLE_LABELS:
        role = "prosecution"
    mode = str(source.get("automation_mode", "casual"))
    if mode not in {"casual", "advanced"}:
        mode = "casual"
    return {"role": role, "automation_mode": mode}


def _trial_steps(case_id: str, role: str) -> tuple[Mapping[str, Any], ...]:
    spec = COURT_CASES[case_id]
    by_role = spec.get("trial_steps_by_role")
    if isinstance(by_role, Mapping):
        role_steps = by_role.get(role)
        if isinstance(role_steps, (tuple, list)):
            return tuple(role_steps)
    return tuple(spec.get("trial_steps", ()))


def _trial_choices(case_id: str, role: str, step_index: int) -> tuple[str, ...]:
    steps = _trial_steps(case_id, role)
    if not 0 <= step_index < len(steps):
        return ()
    step = steps[step_index]
    choices = tuple(dict.fromkeys((str(step["prosecution"]), str(step["defence"]))))
    if len(choices) == 1:
        choices += ("Make no point on this beat.",)
    return choices


def sanitize_court_cases_session_pure(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}
    case_id = str(raw.get("case_id", ""))
    if case_id not in COURT_CASES:
        return {}
    role = str(raw.get("role", "prosecution"))
    if role not in COURT_ROLE_LABELS:
        role = "prosecution"
    mode = str(raw.get("automation_mode", "casual"))
    if mode not in {"casual", "advanced"}:
        mode = "casual"
    spec = COURT_CASES[case_id]
    preparation_count = len(_preparation_labels(case_id, role))
    prep_index = _int(raw.get("prep_index"), maximum=preparation_count)
    phase = str(raw.get("phase", "preparation"))
    if prep_index < preparation_count:
        phase = "preparation"
    elif phase not in {"trial"}:
        phase = "trial"
    trial_count = len(_trial_steps(case_id, role))
    trial_index = _int(raw.get("trial_index"), maximum=max(0, trial_count - 1))
    pending_choice = str(raw.get("pending_choice", ""))
    if pending_choice not in _trial_choices(case_id, role, trial_index):
        pending_choice = ""
    return {
        "version": COURT_CASES_STATE_VERSION,
        "case_id": case_id,
        "role": role,
        "automation_mode": mode,
        "phase": phase,
        "prep_index": prep_index,
        "trial_index": trial_index,
        "correct_count": _int(raw.get("correct_count"), maximum=trial_count),
        "pending_choice": pending_choice,
        "verdict_attempts": _int(raw.get("verdict_attempts")),
    }


def sanitize_court_cases_state_pure(
    player_data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = dict(player_data or {})
    defaults = default_court_cases_state_pure()
    completed_raw = source.get("court_cases_completed_ids")
    completed = []
    if isinstance(completed_raw, (tuple, list)):
        for case_id in completed_raw:
            normalized = str(case_id)
            if normalized in COURT_CASES and normalized not in completed:
                completed.append(normalized)
    session = sanitize_court_cases_session_pure(source.get("court_cases"))
    active = source.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if session and active_id not in {"", COURT_CASES_ACTIVITY_ID}:
        session = {}
    return {
        "court_cases": session,
        "court_cases_policy": sanitize_court_cases_policy_pure(
            source.get("court_cases_policy")
        ),
        "court_cases_completed_ids": completed,
        "court_cases_attempts": _int(source.get("court_cases_attempts")),
        "court_cases_batch2_ready_at_review": _int(
            source.get("court_cases_batch2_ready_at_review")
        ),
        "court_cases_last_result": str(
            source.get("court_cases_last_result", defaults["court_cases_last_result"])
            or defaults["court_cases_last_result"]
        )[:500],
    }


def _quest_complete(player_data: Mapping[str, Any]) -> bool:
    quests = player_data.get("quests")
    quest = quests.get("kings_ransom") if isinstance(quests, Mapping) else None
    return isinstance(quest, Mapping) and bool(quest.get("completed"))


def _next_case_id(completed: list[str]) -> str:
    return next((case_id for case_id in COURT_CASE_ORDER if case_id not in completed), "")


def court_cases_role_locked_reasons_pure(
    player_data: Mapping[str, Any], role: str
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not _quest_complete(player_data):
        reasons.append("complete King's Ransom")
    normalized = role if role in COURT_ROLE_LABELS else "prosecution"
    skill = "attack" if normalized == "prosecution" else "defense"
    if _int(player_data.get(f"{skill}_level"), 1, maximum=99) < 65:
        reasons.append(
            f"{'Attack' if skill == 'attack' else 'Defence'} level 65"
        )
    return tuple(reasons)


def _preparation_labels(case_id: str, role: str) -> tuple[str, ...]:
    spec = COURT_CASES[case_id]
    configured = spec.get("preparation_steps")
    if isinstance(configured, (tuple, list)):
        labels: list[str] = []
        for step in configured:
            if isinstance(step, Mapping):
                labels.append(str(step.get(role, "Prepare the next case detail")))
            else:
                labels.append(str(step))
        return tuple(labels)
    labels = tuple(
        f"Read case report {index}"
        for index in range(1, _int(spec["case_reports"]) + 1)
    )
    if spec["fingerprint"]:
        labels += ("Match the crime-scene fingerprint",)
    return labels


def _answered_cards(player_data: Mapping[str, Any]) -> int:
    clock = player_data.get("shop_market_clock")
    return _int(clock.get("answered_cards")) if isinstance(clock, Mapping) else 0


def set_court_cases_policy_pure(
    player_data: Mapping[str, Any], payload: Mapping[str, Any] | None
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_court_cases_state_pure(data)
    if state["court_cases"]:
        return data, False, {"reason": "Finish or leave the active case first."}
    current = state["court_cases_policy"]
    body = dict(payload or {})
    role = str(body.get("role", current["role"]))
    mode = str(body.get("automation_mode", current["automation_mode"]))
    if role not in COURT_ROLE_LABELS:
        return data, False, {"reason": "Choose Prosecute or Defend."}
    if mode not in {"casual", "advanced"}:
        return data, False, {"reason": "Choose Casual or Advanced mode."}
    data.update(state)
    data["court_cases_policy"] = {"role": role, "automation_mode": mode}
    data["court_cases_last_result"] = (
        f"Court policy set · {COURT_ROLE_LABELS[role]} · {mode.title()}"
    )
    return data, True, {"message": data["court_cases_last_result"]}


def enter_court_case_pure(
    player_data: Mapping[str, Any], payload: Mapping[str, Any] | None = None
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_court_cases_state_pure(data)
    if state["court_cases"]:
        data.update(state)
        data["activity_session"] = {"active_id": COURT_CASES_ACTIVITY_ID}
        data["current_utility"] = COURT_CASES_ACTIVITY_ID
        return data, True, {"message": "The active court case is selected for reviews."}
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if active_id and active_id != COURT_CASES_ACTIVITY_ID:
        return data, False, {"reason": "Finish the active persistent activity first."}
    policy = dict(state["court_cases_policy"])
    body = dict(payload or {})
    role = str(body.get("role", policy["role"]))
    mode = str(body.get("automation_mode", policy["automation_mode"]))
    if role not in COURT_ROLE_LABELS or mode not in {"casual", "advanced"}:
        return data, False, {"reason": "Choose a valid court role and automation mode."}
    locked = court_cases_role_locked_reasons_pure(data, role)
    if locked:
        return data, False, {"reason": ", ".join(locked), "locked_reasons": locked}
    case_id = _next_case_id(state["court_cases_completed_ids"])
    if not case_id:
        return data, False, {"reason": "All available Court Cases are complete."}
    spec = COURT_CASES[case_id]
    if _int(spec.get("batch"), 1) == 2:
        remaining = max(
            0,
            state["court_cases_batch2_ready_at_review"] - _answered_cards(data),
        )
        if remaining:
            return data, False, {
                "reason": f"The next Batch 2 case is available in {remaining:,} reviews."
            }
    inventory = dict(data.get("inventory") or {})
    if not spec["starter"]:
        if _int(inventory.get("Court summons")) < 1:
            return data, False, {"reason": "A Court summons is required for the next case."}
        inventory["Court summons"] = _int(inventory.get("Court summons")) - 1
        if inventory["Court summons"] <= 0:
            inventory.pop("Court summons", None)
    data.update(state)
    data["inventory"] = inventory
    data["court_cases_policy"] = {"role": role, "automation_mode": mode}
    data["court_cases"] = {
        "version": COURT_CASES_STATE_VERSION,
        "case_id": case_id,
        "role": role,
        "automation_mode": mode,
        "phase": "preparation",
        "prep_index": 0,
        "trial_index": 0,
        "correct_count": 0,
        "pending_choice": "",
        "verdict_attempts": 0,
    }
    data["activity_session"] = {"active_id": COURT_CASES_ACTIVITY_ID}
    data["current_utility"] = COURT_CASES_ACTIVITY_ID
    data["court_cases_last_result"] = (
        f"Opened {spec['display_name']} · {COURT_ROLE_LABELS[role]} · first report ready"
    )
    return data, True, {"message": data["court_cases_last_result"], "case_id": case_id}


def select_court_trial_choice_pure(
    player_data: Mapping[str, Any], choice: Any
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_court_cases_state_pure(data)
    session = state["court_cases"]
    if not session or session["phase"] != "trial":
        return data, False, {"reason": "Reach the trial before choosing a courtroom action."}
    selected = str(choice or "")
    options = _trial_choices(
        session["case_id"], session["role"], session["trial_index"]
    )
    if selected not in options:
        return data, False, {"reason": "Choose one of the current courtroom actions."}
    session["pending_choice"] = selected
    data.update(state)
    data["court_cases"] = session
    data["court_cases_last_result"] = f"Queued courtroom action · {selected}"
    return data, True, {"message": data["court_cases_last_result"]}


def _finish_session(data: dict[str, Any]) -> None:
    data["court_cases"] = {}
    active = data.get("activity_session")
    if isinstance(active, Mapping) and str(active.get("active_id", "")) == COURT_CASES_ACTIVITY_ID:
        data["activity_session"] = {"active_id": ""}


def leave_court_case_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_court_cases_state_pure(data)
    if not state["court_cases"]:
        return data, False, {"reason": "No court case is active."}
    case_name = COURT_CASES[state["court_cases"]["case_id"]]["display_name"]
    data.update(state)
    _finish_session(data)
    data["court_cases_last_result"] = (
        f"Gave up {case_name}; any consumed summons was lost."
    )
    return data, True, {"message": data["court_cases_last_result"]}


def apply_court_cases_command_pure(
    player_data: Mapping[str, Any], action_id: str, payload: Mapping[str, Any] | None = None
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    if action_id == "set_policy":
        return set_court_cases_policy_pure(player_data, payload)
    if action_id == "enter":
        return enter_court_case_pure(player_data, payload)
    if action_id == "select_choice":
        return select_court_trial_choice_pure(
            player_data, (payload or {}).get("choice")
        )
    if action_id == "leave":
        return leave_court_case_pure(player_data)
    return copy.deepcopy(dict(player_data)), False, {"reason": "Unknown Court Cases action."}


def apply_court_case_review_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_court_cases_state_pure(data)
    session = state["court_cases"]
    if not session:
        return data, {"allowed": False, "reason": "Start a court case before training."}
    case_id = session["case_id"]
    spec = COURT_CASES[case_id]
    data.update(state)
    if session["phase"] == "preparation":
        labels = _preparation_labels(case_id, session["role"])
        index = session["prep_index"]
        label = labels[index]
        session["prep_index"] = index + 1
        if session["prep_index"] >= len(labels):
            session["phase"] = "trial"
            status = f"{spec['display_name']} · {label} · preparation complete; first evidence beat ready"
        else:
            status = f"{spec['display_name']} · {label} · {session['prep_index']}/{len(labels)} prepared"
        data["court_cases"] = session
        data["court_cases_last_result"] = status
        return data, {
            "allowed": True,
            "action_id": COURT_CASES_ACTIVITY_ID,
            "success": True,
            "expected_success_chance": 1.0,
            "terminal": False,
            "status": status,
        }

    step_index = session["trial_index"]
    trial_steps = _trial_steps(case_id, session["role"])
    step = trial_steps[step_index]
    correct_choice = str(step[session["role"]])
    selected = (
        correct_choice
        if session["automation_mode"] == "casual"
        else str(session.get("pending_choice", ""))
    )
    if not selected:
        return data, {
            "allowed": False,
            "reason": "Choose the next courtroom action in Advanced mode.",
        }
    correct = selected == correct_choice
    if correct:
        session["correct_count"] += 1
    session["trial_index"] += 1
    session["pending_choice"] = ""
    total_steps = len(trial_steps)
    if session["trial_index"] < total_steps:
        status = (
            f"{spec['display_name']} · {step['kind']} {step_index + 1}/{total_steps} · "
            f"{'jury persuaded' if correct else 'argument weakened'}"
        )
        data["court_cases"] = session
        data["court_cases_last_result"] = status
        return data, {
            "allowed": True,
            "action_id": COURT_CASES_ACTIVITY_ID,
            "success": correct,
            "expected_success_chance": 1.0,
            "terminal": False,
            "status": status,
        }

    data["court_cases_attempts"] = state["court_cases_attempts"] + 1
    if session["correct_count"] < total_steps:
        session["trial_index"] = 0
        session["correct_count"] = 0
        session["verdict_attempts"] += 1
        data["court_cases"] = session
        status = (
            f"{spec['display_name']} · jury undecided · preparation kept; retry the trial"
        )
        data["court_cases_last_result"] = status
        return data, {
            "allowed": True,
            "action_id": COURT_CASES_ACTIVITY_ID,
            "success": False,
            "expected_success_chance": 1.0,
            "terminal": False,
            "verdict": "undecided",
            "status": status,
        }

    role = session["role"]
    xp = float(spec["xp"])
    rewards = {str(item): _int(amount) for item, amount in dict(spec["rewards"]).items()}
    inventory = dict(data.get("inventory") or {})
    for item_name, amount in rewards.items():
        inventory[item_name] = _int(inventory.get(item_name)) + amount
    completed = list(state["court_cases_completed_ids"])
    if case_id not in completed:
        completed.append(case_id)
    data["inventory"] = inventory
    data["court_cases_completed_ids"] = completed
    if not spec["starter"]:
        data["court_cases_batch2_ready_at_review"] = (
            _answered_cards(data) + COURT_CASES_BATCH2_COOLDOWN_REVIEWS
        )
    _finish_session(data)
    verdict = "guilty" if role == "prosecution" else "not guilty"
    reward_text = "" if not rewards else " · " + ", ".join(
        f"{amount} {item}" for item, amount in rewards.items()
    )
    status = (
        f"{spec['display_name']} · {verdict} · {int(xp):,} "
        f"{'Attack' if role == 'prosecution' else 'Defence'} XP{reward_text}"
    )
    data["court_cases_last_result"] = status
    return data, {
        "allowed": True,
        "action_id": COURT_CASES_ACTIVITY_ID,
        "success": True,
        "expected_success_chance": 1.0,
        "terminal": True,
        "completed_activity": True,
        "case_id": case_id,
        "role": role,
        "xp": xp,
        "xp_skill": "attack" if role == "prosecution" else "defense",
        "rewards": rewards,
        "verdict": verdict,
        "status": status,
    }


def court_cases_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_court_cases_state_pure(player_data)
    session = state["court_cases"]
    policy = state["court_cases_policy"]
    completed = state["court_cases_completed_ids"]
    case_id = str(session.get("case_id", "")) if session else _next_case_id(completed)
    spec = COURT_CASES.get(case_id)
    role = str(session.get("role", policy["role"])) if session else policy["role"]
    mode = str(session.get("automation_mode", policy["automation_mode"])) if session else policy["automation_mode"]
    phase = str(session.get("phase", "idle")) if session else "idle"
    prep_labels = _preparation_labels(case_id, role) if spec else ()
    prep_index = _int(session.get("prep_index")) if session else 0
    trial_index = _int(session.get("trial_index")) if session else 0
    trial_steps = _trial_steps(case_id, role) if spec else ()
    current_step = trial_steps[trial_index] if phase == "trial" and trial_index < len(trial_steps) else None
    choices = _trial_choices(case_id, role, trial_index) if current_step else ()
    pending = str(session.get("pending_choice", "")) if session else ""
    locked = court_cases_role_locked_reasons_pure(player_data, role)
    if spec and not spec["starter"] and _int((player_data.get("inventory") or {}).get("Court summons")) < 1 and not session:
        locked = locked + ("carry a Court summons",)
    cooldown_reviews = 0
    if spec and _int(spec.get("batch"), 1) == 2 and not session:
        cooldown_reviews = max(
            0,
            state["court_cases_batch2_ready_at_review"] - _answered_cards(player_data),
        )
        if cooldown_reviews:
            locked = locked + (
                f"Batch 2 available in {cooldown_reviews:,} reviews",
            )
    if not spec and not session:
        locked = ("all available Court Cases complete",)
    can_review = bool(
        session
        and (
            phase == "preparation"
            or mode == "casual"
            or bool(pending)
        )
    )
    if phase == "preparation" and prep_labels:
        current_beat = prep_labels[min(prep_index, len(prep_labels) - 1)]
        progress = f"Preparation {prep_index}/{len(prep_labels)}"
    elif current_step:
        current_beat = f"{current_step['kind']} · {current_step['subject']}"
        progress = f"Trial {trial_index}/{len(trial_steps)}"
    else:
        current_beat = "All available Court Cases complete" if not spec else "Ready to open the case"
        progress = f"Cases complete {len(completed)}/{len(COURT_CASE_ORDER)}"
    return {
        "active": bool(session),
        "can_review": can_review,
        "case_id": case_id,
        "case_name": str(spec["display_name"]) if spec else "Court Cases",
        "case_summary": str(spec["summary"]) if spec else "You have completed every available Court Case.",
        "starter": bool(spec and spec["starter"]),
        "role": role,
        "role_label": COURT_ROLE_LABELS[role],
        "automation_mode": mode,
        "phase": phase,
        "progress": progress,
        "current_beat": current_beat,
        "trial_choices": choices,
        "pending_choice": pending,
        "locked_reasons": locked,
        "completed_ids": tuple(completed),
        "cases_completed": len(completed),
        "attempts": state["court_cases_attempts"],
        "cooldown_reviews": cooldown_reviews,
        "last_result": state["court_cases_last_result"],
    }
