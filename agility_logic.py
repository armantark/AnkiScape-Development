"""Pure Agility course, activity, reward, and storage mechanics."""

from __future__ import annotations

import copy
import math
from typing import Any, Mapping, Optional

try:
    from .agility_data import (
        AGILITY_TARGETS_BY_ID,
        BRIMHAVEN_ITEM_EXCHANGES,
        BRIMHAVEN_OBSTACLES,
        BRIMHAVEN_XP_EXCHANGES,
        CIRCUS_ACROBAT_REWARDS,
        CIRCUS_TRICKS,
        DEFAULT_AGILITY_TARGET,
        GNOME_BALL_XP,
        PIT_CHALLENGES,
        AgilityStage,
        AgilityTarget,
    )
except ImportError:  # pragma: no cover - flat test imports
    from agility_data import (  # type: ignore
        AGILITY_TARGETS_BY_ID,
        BRIMHAVEN_ITEM_EXCHANGES,
        BRIMHAVEN_OBSTACLES,
        BRIMHAVEN_XP_EXCHANGES,
        CIRCUS_ACROBAT_REWARDS,
        CIRCUS_TRICKS,
        DEFAULT_AGILITY_TARGET,
        GNOME_BALL_XP,
        PIT_CHALLENGES,
        AgilityStage,
        AgilityTarget,
    )

try:
    from .agility_travel import agility_carried_weight_pure
except ImportError:  # pragma: no cover - flat test imports
    from agility_travel import agility_carried_weight_pure  # type: ignore

try:
    from .inventory_pure import clamp_carried_view_to_bank
except ImportError:  # pragma: no cover - flat test imports
    from inventory_pure import clamp_carried_view_to_bank  # type: ignore

try:
    from .flash_powder_factory_data import FLASH_POWDER_FACTORY_ACTIVITY_ID
    from .flash_powder_factory_logic import (
        apply_flash_powder_factory_review_pure,
        enter_flash_powder_factory_pure,
        flash_powder_factory_locked_reasons_pure,
        leave_flash_powder_factory_pure,
        redeem_flash_powder_factory_item_pure,
        redeem_flash_powder_factory_xp_pure,
        sanitize_flash_powder_factory_policy_pure,
        sanitize_flash_powder_factory_session_pure,
        set_flash_powder_factory_policy_pure,
    )
except ImportError:  # pragma: no cover - flat test imports
    from flash_powder_factory_data import (  # type: ignore
        FLASH_POWDER_FACTORY_ACTIVITY_ID,
    )
    from flash_powder_factory_logic import (  # type: ignore
        apply_flash_powder_factory_review_pure,
        enter_flash_powder_factory_pure,
        flash_powder_factory_locked_reasons_pure,
        leave_flash_powder_factory_pure,
        redeem_flash_powder_factory_item_pure,
        redeem_flash_powder_factory_xp_pure,
        sanitize_flash_powder_factory_policy_pure,
        sanitize_flash_powder_factory_session_pure,
        set_flash_powder_factory_policy_pure,
    )

try:
    from .review_context import (
        PIT_REWARD_CONTEXT_ID,
        remember_review_context_choice_pure,
    )
except ImportError:  # pragma: no cover - flat test imports
    from review_context import (  # type: ignore
        PIT_REWARD_CONTEXT_ID,
        remember_review_context_choice_pure,
    )


WILDERNESS_PKER_AMBUSH_CHANCE = 0.01
WILDERNESS_PKER_MAX_HIT_LP = 250
PIT_INVITATION_COURSE_IDS = frozenset(
    {
        "gnome_normal",
        "gnome_advanced",
        "barbarian_normal",
        "barbarian_advanced",
        "agility_pyramid",
        "ape_atoll",
        "wilderness_course",
        "werewolf_course",
        "dorgesh_kaan",
    }
)


def _int(value: Any, default: int = 0, *, minimum: int = 0, maximum: int = 2_147_483_647) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        return default
    return max(minimum, min(parsed, maximum))


def _float(value: Any, default: float = 0.0, *, minimum: float = 0.0, maximum: float = 1e12) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        return default
    if not math.isfinite(parsed):
        return default
    return max(minimum, min(parsed, maximum))


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))


def default_agility_state_pure() -> dict[str, Any]:
    return {
        "current_agility": DEFAULT_AGILITY_TARGET,
        "agility_course_state": {
            "target": DEFAULT_AGILITY_TARGET,
            "stage": 0,
            "checkpoint": "start",
            "flawless": True,
            "lap_xp_valid": True,
            "requested_item_valid": True,
            "status": "Ready to start",
        },
        "agility_lap_counts": {
            "total": 0,
            "flawless": 0,
            "gnome_advanced_flawless": 0,
            "barbarian_advanced_flawless": 0,
            "agile_legs_unlocked": False,
            "agile_top_unlocked": False,
        },
        "agility_activity_state": {},
        "agility_activity_currencies": {
            "brianpoints": 0,
            "circus_audience": 0,
        },
        "agility_flash_powder_factory_policy": {
            "version": 1,
            "automation_mode": "casual",
            "strategy": "max_points",
            "apparatus_policy": "ignore",
        },
        "agility_shortcut_options": {},
        "agility_effect_charges": {},
        "agility_effective_boost": 0,
        "agility_boost_actions_remaining": 0,
        "agility_run_energy_credit_pct": 0,
        "agility_actions_completed": 0,
        "agility_pit_offer": False,
        "agility_pit_origin_course": "",
        "agility_pit_auto_accept": True,
        "agility_pit_successes": 0,
        "agility_activity_completions": {},
        "agility_circus_last_week": -1,
        "agility_toy_mouse_pending": False,
        "agility_status": "Ready to start",
    }


def sanitize_agility_state_pure(player_data: Optional[Mapping[str, Any]]) -> dict[str, Any]:
    source = dict(player_data or {})
    defaults = default_agility_state_pure()
    target_id = str(source.get("current_agility", DEFAULT_AGILITY_TARGET) or DEFAULT_AGILITY_TARGET)
    if target_id not in AGILITY_TARGETS_BY_ID:
        target_id = DEFAULT_AGILITY_TARGET
    source["current_agility"] = target_id

    raw_course = source.get("agility_course_state")
    raw_course = raw_course if isinstance(raw_course, Mapping) else {}
    course_target = str(raw_course.get("target", target_id) or target_id)
    if course_target not in AGILITY_TARGETS_BY_ID:
        course_target = target_id
    max_stage = max(0, len(AGILITY_TARGETS_BY_ID[course_target].stages) - 1)
    source["agility_course_state"] = {
        "target": course_target,
        "stage": _int(raw_course.get("stage"), maximum=max_stage),
        "checkpoint": str(raw_course.get("checkpoint", "start") or "start")[:80],
        "flawless": bool(raw_course.get("flawless", True)),
        "lap_xp_valid": bool(raw_course.get("lap_xp_valid", True)),
        "requested_item_valid": bool(raw_course.get("requested_item_valid", True)),
        "status": str(raw_course.get("status", "Ready to start") or "Ready to start")[:240],
    }

    raw_counts = source.get("agility_lap_counts")
    raw_counts = raw_counts if isinstance(raw_counts, Mapping) else {}
    counts = defaults["agility_lap_counts"]
    source["agility_lap_counts"] = {
        "total": _int(raw_counts.get("total")),
        "flawless": _int(raw_counts.get("flawless")),
        "gnome_advanced_flawless": _int(raw_counts.get("gnome_advanced_flawless")),
        "barbarian_advanced_flawless": _int(raw_counts.get("barbarian_advanced_flawless")),
        "agile_legs_unlocked": bool(raw_counts.get("agile_legs_unlocked", False)),
        "agile_top_unlocked": bool(raw_counts.get("agile_top_unlocked", False)),
    }

    raw_activity = source.get("agility_activity_state")
    activities = copy.deepcopy(raw_activity) if isinstance(raw_activity, Mapping) else {}
    raw_pit = activities.get("pit")
    pit_reviews = _int(raw_pit.get("reviews"), maximum=5) if isinstance(raw_pit, Mapping) else 0
    pit_challenge = str(raw_pit.get("challenge", "")) if isinstance(raw_pit, Mapping) else ""
    if 1 <= pit_reviews <= 5 and pit_challenge in PIT_CHALLENGES:
        pit_session_origin = str(raw_pit.get("origin_course", "") or "")
        activities["pit"] = {
            "challenge": pit_challenge,
            "reviews": pit_reviews,
            "successes": _int(raw_pit.get("successes"), maximum=pit_reviews),
            "origin_course": (
                pit_session_origin
                if pit_session_origin in PIT_INVITATION_COURSE_IDS
                else DEFAULT_AGILITY_TARGET
            ),
        }
    else:
        activities.pop("pit", None)
    flash_powder_session = sanitize_flash_powder_factory_session_pure(
        activities.get(FLASH_POWDER_FACTORY_ACTIVITY_ID)
    )
    if flash_powder_session:
        activities[FLASH_POWDER_FACTORY_ACTIVITY_ID] = flash_powder_session
        persistent_session = source.get("activity_session")
        persistent_id = (
            str(persistent_session.get("active_id", ""))
            if isinstance(persistent_session, Mapping)
            else ""
        )
        if not persistent_id:
            source["activity_session"] = {
                "active_id": FLASH_POWDER_FACTORY_ACTIVITY_ID
            }
    else:
        activities.pop(FLASH_POWDER_FACTORY_ACTIVITY_ID, None)
    source["agility_activity_state"] = activities
    raw_currencies = source.get("agility_activity_currencies")
    raw_currencies = raw_currencies if isinstance(raw_currencies, Mapping) else {}
    source["agility_activity_currencies"] = {
        "brianpoints": _int(raw_currencies.get("brianpoints")),
        "circus_audience": _int(raw_currencies.get("circus_audience")),
    }
    source["agility_flash_powder_factory_policy"] = (
        sanitize_flash_powder_factory_policy_pure(
            source.get("agility_flash_powder_factory_policy")
        )
    )
    raw_shortcuts = source.get("agility_shortcut_options")
    source["agility_shortcut_options"] = copy.deepcopy(raw_shortcuts) if isinstance(raw_shortcuts, Mapping) else {}
    raw_charges = source.get("agility_effect_charges")
    source["agility_effect_charges"] = {
        str(key): _int(value, maximum=1_000_000)
        for key, value in raw_charges.items()
        if isinstance(raw_charges, Mapping) and isinstance(key, str) and _int(value) > 0
    } if isinstance(raw_charges, Mapping) else {}
    source["agility_effective_boost"] = _int(source.get("agility_effective_boost"), maximum=20)
    source["agility_boost_actions_remaining"] = _int(source.get("agility_boost_actions_remaining"), maximum=10_000)
    if source["agility_boost_actions_remaining"] <= 0:
        source["agility_effective_boost"] = 0
    source["agility_run_energy_credit_pct"] = _int(
        source.get("agility_run_energy_credit_pct"),
        maximum=100,
    )
    source["agility_actions_completed"] = _int(source.get("agility_actions_completed"))
    source["agility_pit_offer"] = bool(source.get("agility_pit_offer", False))
    pit_origin = str(source.get("agility_pit_origin_course", "") or "")
    source["agility_pit_origin_course"] = (
        pit_origin if pit_origin in PIT_INVITATION_COURSE_IDS else ""
    )
    source["agility_pit_auto_accept"] = bool(
        source.get("agility_pit_auto_accept", True)
    )
    source["agility_pit_successes"] = _int(source.get("agility_pit_successes"))
    source["agility_circus_last_week"] = _int(
        source.get("agility_circus_last_week"), -1, minimum=-1
    )
    source["agility_toy_mouse_pending"] = bool(source.get("agility_toy_mouse_pending", False))
    raw_completions = source.get("agility_activity_completions")
    source["agility_activity_completions"] = {
        str(activity_id): _int(count)
        for activity_id, count in raw_completions.items()
        if isinstance(raw_completions, Mapping) and isinstance(activity_id, str) and _int(count) > 0
    } if isinstance(raw_completions, Mapping) else {}
    source["agility_status"] = str(source.get("agility_status", "Ready to start") or "Ready to start")[:240]
    return source


def _quest_complete(player_data: Mapping[str, Any], quest_id: str) -> bool:
    if quest_id == "bar_crawl":
        return bool(player_data.get("bar_crawl_completed", False))
    quests = player_data.get("quests")
    return bool(isinstance(quests, Mapping) and isinstance(quests.get(quest_id), Mapping) and quests[quest_id].get("completed"))


def _owns_item(player_data: Mapping[str, Any], item_name: str) -> bool:
    inventory = player_data.get("inventory")
    equipment = player_data.get("equipment")
    collections = (inventory if isinstance(inventory, Mapping) else {}, equipment if isinstance(equipment, Mapping) else {})
    wanted = item_name.casefold()
    for collection in collections:
        for key, value in collection.items():
            candidate = str(value if collection is equipment else key)
            if candidate.casefold() == wanted or (wanted == "crossbow" and "crossbow" in candidate.casefold()):
                if collection is equipment or _int(value) > 0:
                    return True
    return False


def _answered_card_week(player_data: Mapping[str, Any]) -> int:
    clock = player_data.get("shop_market_clock")
    answered = _int(clock.get("answered_cards")) if isinstance(clock, Mapping) else 0
    return answered // (240 * 7)


def agility_target_locked_reasons_pure(player_data: Mapping[str, Any], target_id: str) -> tuple[str, ...]:
    target = AGILITY_TARGETS_BY_ID.get(target_id)
    if target is None:
        return ("unknown target",)
    reasons = []
    level = _int(player_data.get("agility_level"), 1, minimum=1, maximum=120)
    if level < target.level:
        reasons.append(f"Agility level {target.level}")
    if target.quest_gate and not _quest_complete(player_data, target.quest_gate):
        reasons.append(target.quest_gate.replace("_", " ").title())
    for item_name in target.required_items:
        if not _owns_item(player_data, item_name):
            reasons.append(item_name)
    for item_options in target.required_item_options:
        if not any(_owns_item(player_data, item_name) for item_name in item_options):
            reasons.append(f"{item_options[0]} or another valid alternative")
    if target.id == FLASH_POWDER_FACTORY_ACTIVITY_ID:
        reasons.extend(
            reason
            for reason in flash_powder_factory_locked_reasons_pure(player_data)
            if reason not in reasons
        )
    pit_session = (player_data.get("agility_activity_state") or {}).get("pit")
    if (
        target.id == "the_pit"
        and not bool(player_data.get("agility_pit_offer"))
        and not bool(pit_session)
    ):
        reasons.append("Talent Scout invitation")
    if (
        target.id == "circus_agility"
        and _int(player_data.get("agility_circus_last_week"), -1, minimum=-1)
        == _answered_card_week(player_data)
    ):
        reasons.append("next answered-card week")
    if target.id == "brimhaven_arena" and not _quest_complete(player_data, "rocking_out"):
        inventory = player_data.get("inventory")
        coins = _int(inventory.get("Coins")) if isinstance(inventory, Mapping) else 0
        active = bool((player_data.get("agility_activity_state") or {}).get("brimhaven", {}).get("stint_active"))
        if not active and coins < 200:
            reasons.append("200 coins")
    return tuple(reasons)


def agility_failure_probability_pure(
    stage: AgilityStage,
    target: AgilityTarget,
    agility_level: int,
    *,
    strength_level: int = 1,
    carried_weight_kg: float = 0.0,
) -> float:
    if not stage.can_fail:
        return 0.0
    level = max(target.level, int(agility_level))
    profile = stage.fail_profile
    if profile == "gnome_advanced":
        return .40 * max(0, 89 - level) / 4
    if profile == "barbarian":
        return .20 * max(0, 93 - level) / max(1, 93 - target.level)
    if profile == "burthorpe":
        return .20 * max(0, 5 - level) / 4
    if profile.startswith("pyramid:"):
        bands = {"low_wall": .05, "rolling_block": .125, "moving_block": .20, "ledge": .20, "plank": .25, "cross_gap": .35, "jump_gap": .40}
        band = bands.get(profile.split(":", 1)[1], .20)
        return band * (1 - .50 * _clamp((level - 30) / 69, 0, 1))
    if profile == "ape_atoll":
        return .20 * max(0, 75 - level) / 27
    if profile == "werewolf":
        if level >= 93:
            return 0.0
        return _clamp(.25 - .0125 * max(0, level - 60) - .0025 * max(0, strength_level - 60) + .0025 * max(0.0, carried_weight_kg), 0.0, .50)
    if profile == "dorgesh":
        return .20 - .15 * _clamp((level - 80) / 19, 0, 1)
    if profile == "wilderness_stones":
        return .20 - .15 * _clamp((level - 53) / 46, 0, 1)
    return .20 - .15 * _clamp((level - target.level) / max(1, 99 - target.level), 0, 1)


def _failure_damage(stage: AgilityStage, target_id: str, current_lp: int) -> int:
    if target_id == "ape_atoll":
        return int(_clamp(round(current_lp / 10), 30, 80))
    if stage.failure_damage is not None:
        return max(0, int(stage.failure_damage))
    if stage.fail_profile == "wilderness_stones":
        return max(1, int(math.floor(max(1, current_lp) * .266)))
    return int(_clamp(math.floor(max(1, current_lp) / 10), 10, 100))


def _active_familiar_pure(data: Mapping[str, Any]) -> bool:
    summoning_state = data.get("summoning_state")
    follower = (
        summoning_state.get("active_follower")
        if isinstance(summoning_state, Mapping)
        else None
    )
    return isinstance(follower, Mapping) and follower.get("kind") == "familiar"


def _stow_pit_hand_equipment_pure(data: dict[str, Any]) -> None:
    equipment = dict(data.get("equipment") or {})
    inventory = dict(data.get("inventory") or {})
    for slot_id in ("weapon", "shield"):
        item_name = equipment.pop(slot_id, None)
        if item_name:
            inventory[str(item_name)] = _int(inventory.get(str(item_name))) + 1
    data["equipment"] = equipment
    data["inventory"] = inventory


def _arm_pit_offer_pure(data: dict[str, Any]) -> None:
    if not data.get("agility_pit_offer"):
        return
    _stow_pit_hand_equipment_pure(data)
    data["current_agility"] = "the_pit"
    data["agility_status"] = "The Pit · Talent Scout invitation accepted"


def _finish_lap(data: dict[str, Any], target: AgilityTarget, state: dict[str, Any], reward_roll: float) -> dict[str, Any]:
    counts = dict(data["agility_lap_counts"])
    counts["total"] += 1
    if state.get("flawless", True):
        counts["flawless"] += 1
        key = f"{target.id}_flawless"
        if key in counts:
            counts[key] += 1
    if counts["gnome_advanced_flawless"] >= 250:
        counts["agile_legs_unlocked"] = True
    if counts["barbarian_advanced_flawless"] >= 250:
        counts["agile_top_unlocked"] = True
    data["agility_lap_counts"] = counts
    if target.id in PIT_INVITATION_COURSE_IDS and reward_roll < .125:
        data["agility_pit_offer"] = True
        data["agility_pit_origin_course"] = target.id
        if data.get("agility_pit_auto_accept", True) and not _active_familiar_pure(data):
            _arm_pit_offer_pure(data)
    return counts


def _standard_course_review(
    data: dict[str, Any],
    target: AgilityTarget,
    roll: float,
    reward_roll: float,
    carried_weight_kg: float,
) -> dict[str, Any]:
    raw_state = data["agility_course_state"]
    state = dict(raw_state)
    if state.get("target") != target.id:
        state = {"target": target.id, "stage": 0, "checkpoint": "start", "flawless": True, "lap_xp_valid": True, "requested_item_valid": True, "status": "Ready to start"}
    stage_index = _int(state.get("stage"), maximum=max(0, len(target.stages) - 1))
    stage = target.stages[stage_index]
    level = _int(data.get("agility_level"), 1, minimum=1, maximum=120)
    effective = level + _int(data.get("agility_effective_boost"), maximum=20)
    probability = agility_failure_probability_pure(
        stage,
        target,
        effective,
        strength_level=_int(data.get("strength_level"), 1, minimum=1, maximum=120),
        carried_weight_kg=carried_weight_kg,
    )
    if _int((data.get("agility_effect_charges") or {}).get("surefooted_reviews")) > 0:
        probability = 0.0
    success = float(roll) >= probability
    result = {
        "target_id": target.id,
        "action_id": stage.id,
        "success": success,
        "expected_success_chance": 1.0 - probability,
        "xp": stage.xp if success else stage.xp_on_fail,
        "damage": 0,
        "outputs": {},
        "cross_skill_rewards": list(stage.cross_skill_rewards),
        "completed_lap": False,
        "failure_kind": None,
    }
    if success:
        next_stage = stage_index + 1
        if stage.output_item and stage.output_qty > 0:
            result["outputs"][stage.output_item] = stage.output_qty
        if next_stage >= len(target.stages):
            result["xp"] += target.completion_bonus
            result["completed_lap"] = True
            _finish_lap(data, target, state, reward_roll)
            state.update({"stage": 0, "checkpoint": "start", "flawless": True, "lap_xp_valid": True, "requested_item_valid": True})
            state["status"] = (
                f"{stage.label} · lap complete · Talent Scout invitation accepted"
                if data.get("current_agility") == "the_pit"
                else f"{stage.label} · lap complete"
            )
        else:
            state["stage"] = next_stage
            state["status"] = f"{stage.label} · success · {next_stage}/{len(target.stages)}"
    else:
        state["flawless"] = False
        result["failure_kind"] = stage.position_result
        result["damage"] = _failure_damage(stage, target.id, _int(data.get("combat_lifepoints"), 1000, minimum=1, maximum=10000))
        if stage.position_result == "cross":
            state["stage"] = min(stage_index + 1, len(target.stages) - 1)
        elif stage.position_result == "end_partial":
            state["stage"] = min(stage_index + 1, len(target.stages) - 1)
        elif stage.position_result == "lower_floor":
            state["stage"] = 0
            state["checkpoint"] = "lower_floor"
        elif stage.position_result == "checkpoint":
            state["stage"] = 0
            state["checkpoint"] = "start"
        elif stage.position_result == "invalidate_item":
            state["requested_item_valid"] = False
            state["stage"] = 8
        state["status"] = f"{stage.label} · failed · {state['stage']}/{len(target.stages)}"
    data["agility_course_state"] = state
    data["agility_status"] = state["status"]
    return result


_HORN_EXCLUDED_TARGETS = {"agility_pyramid", "penguin_course"}


def _apply_agility_xp_modifiers(data: dict[str, Any], target: AgilityTarget, result: dict[str, Any]) -> None:
    base_xp = _float(result.get("xp"))
    if base_xp <= 0 or result.get("modifier_eligible") is False:
        return
    inventory = data.get("inventory") or {}
    equipment = data.get("equipment") or {}
    owned = set(equipment.values()) if isinstance(equipment, Mapping) else set()
    if isinstance(inventory, Mapping):
        owned.update(item for item, amount in inventory.items() if _int(amount) > 0)
    charges = dict(data.get("agility_effect_charges") or {})
    modifiers: list[tuple[str, float]] = []

    horn = next((item for item in ("Penance master horn", "Penance horn") if item in owned and _int(charges.get(item)) > 0), None)
    skoll = "Sköll boots" if "Sköll boots" in owned and _int(charges.get("Sköll boots")) > 0 else None
    horn_eligible = target.activity_kind is None and target.id not in _HORN_EXCLUDED_TARGETS and not (
        target.id == "dorgesh_kaan" and result.get("action_id") == "hand_in"
    )
    if horn_eligible and horn:
        modifiers.append((horn, 2.0))
        charges[horn] = _int(charges.get(horn)) - 1
    elif horn_eligible and skoll:
        modifiers.append((skoll, 2.0))
        charges[skoll] = _int(charges.get(skoll)) - 1

    pendant = next((item for item in ("Prized pendant of Agility", "Pendant of Agility") if item in owned and _int(charges.get(item)) > 0), None)
    if pendant and target.activity_kind is None:
        modifiers.append((pendant, 2.0 if pendant.startswith("Prized") else 1.5))
        charges[pendant] = _int(charges.get(pendant)) - 1

    if target.id == "wilderness_course" and "Brawling gloves (Agility)" in owned and _int(charges.get("Brawling gloves (Agility)")) > 0:
        modifiers.append(("Brawling gloves (Agility)", 4.0))
        charges["Brawling gloves (Agility)"] = _int(charges.get("Brawling gloves (Agility)")) - 1

    multiplier = math.prod(value for _name, value in modifiers) if modifiers else 1.0
    result["base_xp"] = base_xp
    result["xp"] = base_xp * multiplier
    result["xp_modifiers"] = tuple({"item": item, "multiplier": value} for item, value in modifiers)
    data["agility_effect_charges"] = {key: value for key, value in charges.items() if _int(value) > 0}


def _advance_agility_effect_budgets(data: dict[str, Any], *, standard_course: bool) -> None:
    remaining = _int(data.get("agility_boost_actions_remaining"))
    if remaining > 0:
        remaining -= 1
        data["agility_boost_actions_remaining"] = remaining
        if remaining <= 0:
            data["agility_effective_boost"] = 0
    charges = dict(data.get("agility_effect_charges") or {})
    if standard_course and _int(charges.get("surefooted_reviews")) > 0:
        charges["surefooted_reviews"] -= 1
    if _int(charges.get("surefooted_cooldown_reviews")) > 0:
        charges["surefooted_cooldown_reviews"] -= 1
    data["agility_effect_charges"] = {key: value for key, value in charges.items() if _int(value) > 0}


def _activity_session(data: dict[str, Any], activity_id: str) -> dict[str, Any]:
    activities = dict(data.get("agility_activity_state") or {})
    raw = activities.get(activity_id)
    session = dict(raw) if isinstance(raw, Mapping) else {}
    activities[activity_id] = session
    data["agility_activity_state"] = activities
    return session


def _skullball_review(data: dict[str, Any], roll: float) -> dict[str, Any]:
    session = _activity_session(data, "skullball")
    goals = _int(session.get("goals"), maximum=10)
    attempts = _int(session.get("attempts"), maximum=30) + 1
    success = roll >= .20
    if success:
        goals += 1
    done = goals >= 10 or attempts >= 30
    xp = 0.0
    if done:
        performance = max(.50, 1.0 - .025 * max(0, attempts - 10))
        xp = 750.0 * (goals / 10) * performance
        session.clear()
    else:
        session.update({"goals": goals, "attempts": attempts})
    status = f"Skullball · {'goal' if success else 'miss'} · {goals}/10 goals · {attempts}/30 attempts"
    data["agility_status"] = status
    return {"target_id": "werewolf_skullball", "action_id": f"goal_{goals + (0 if success else 1)}", "success": success, "expected_success_chance": .80, "xp": xp, "damage": 0, "outputs": {}, "cross_skill_rewards": [], "completed_activity": done, "failure_kind": None if success else "retry", "status": status}


def _gnome_ball_review(data: dict[str, Any], roll: float) -> dict[str, Any]:
    session = _activity_session(data, "gnome_ball")
    goal = _int(session.get("goal"), maximum=4)
    success = roll >= .25
    xp = GNOME_BALL_XP[goal] if success else 0.0
    outputs = {}
    completed = False
    if success:
        goal += 1
        if goal >= 5:
            completed = True
            inventory = data.get("inventory") or {}
            if _int(inventory.get("Gnomeball")) <= 0:
                outputs["Gnomeball"] = 1
            session.clear()
        else:
            session["goal"] = goal
    status = f"Gnome Ball · {'scored' if success else 'tackled'} · {goal}/5 goals"
    data["agility_status"] = status
    return {"target_id": "gnome_ball", "action_id": f"possession_{goal or 1}", "success": success, "expected_success_chance": .75, "xp": xp, "damage": 0 if success else 10, "outputs": outputs, "cross_skill_rewards": [("ranged", xp)] if xp else [], "completed_activity": completed, "failure_kind": None if success else "tackle", "status": status}


def _next_missing_reward(data: Mapping[str, Any], rewards: tuple[str, ...]) -> Optional[str]:
    return next((item for item in rewards if not _owns_item(data, item)), None)


def _pit_review(data: dict[str, Any], roll: float, reward_roll: float) -> dict[str, Any]:
    session = _activity_session(data, "pit")
    if not session:
        challenge = PIT_CHALLENGES[min(int(reward_roll * len(PIT_CHALLENGES)), len(PIT_CHALLENGES) - 1)]
        origin_course = str(data.get("agility_pit_origin_course", "") or "")
        session.update(
            {
                "challenge": challenge,
                "reviews": 0,
                "successes": 0,
                "origin_course": (
                    origin_course
                    if origin_course in PIT_INVITATION_COURSE_IDS
                    else DEFAULT_AGILITY_TARGET
                ),
            }
        )
        data["agility_pit_offer"] = False
    review = _int(session.get("reviews"), maximum=5) + 1
    successes = _int(session.get("successes"), maximum=6)
    success = roll >= .25
    if success:
        successes += 1
    done = review >= 6
    xp = 0.0
    outputs = {}
    if done:
        passed = successes >= 4
        level = _int(data.get("agility_level"), 1, minimum=1, maximum=99)
        xp = float(level * (20 if passed else 5))
        if passed:
            prior_successes = _int(data.get("agility_pit_successes"))
            data["agility_pit_successes"] = prior_successes + 1
            if prior_successes == 0:
                outputs["Gorilla mask"] = 1
        activities = dict(data.get("agility_activity_state") or {})
        origin_course = str(session.get("origin_course", DEFAULT_AGILITY_TARGET))
        if origin_course not in PIT_INVITATION_COURSE_IDS:
            origin_course = DEFAULT_AGILITY_TARGET
        activities["pit_reward"] = {"xp": xp, "course": origin_course}
        data["agility_activity_state"] = activities
        data["agility_pit_origin_course"] = ""
        data["current_agility"] = origin_course
        session.clear()
    else:
        session.update({"reviews": review, "successes": successes})
    status = f"The Pit · {session.get('challenge', 'challenge')} · {successes}/4 successes · {review}/6 actions"
    data["agility_status"] = status
    return {"target_id": "the_pit", "action_id": f"challenge_{review}", "success": success, "expected_success_chance": .75, "xp": 0.0 if done else xp, "damage": 0, "outputs": outputs, "cross_skill_rewards": [], "completed_activity": done, "failure_kind": None if success else "challenge_step", "status": status, "pending_pit_xp": xp if done else 0.0}


def _circus_review(data: dict[str, Any], roll: float) -> dict[str, Any]:
    session = _activity_session(data, "circus")
    attempted = list(session.get("attempted", [])) if isinstance(session.get("attempted"), list) else []
    session_score = _int(session.get("audience_score"))
    level = _int(data.get("agility_level"), 1, minimum=1, maximum=99)
    eligible = [trick for trick in CIRCUS_TRICKS if trick[2] <= level and trick[0] not in attempted]
    if not eligible:
        session.clear()
        data["agility_circus_last_week"] = _answered_card_week(data)
        data["agility_status"] = "Circus · visit complete"
        return {"target_id": "circus_agility", "action_id": "visit_complete", "success": True, "expected_success_chance": 1.0, "xp": 0.0, "damage": 0, "outputs": {}, "cross_skill_rewards": [], "completed_activity": True, "failure_kind": None, "status": data["agility_status"]}
    trick_id, label, required, xp_value = eligible[0]
    success_chance = _clamp(.55 + .01 * (level - required), .55, .95)
    success = roll < success_chance
    attempted.append(trick_id)
    session["attempted"] = attempted
    audience = dict(data["agility_activity_currencies"])
    if success:
        audience["circus_audience"] += required
        session_score += required
    data["agility_activity_currencies"] = audience
    session["audience_score"] = session_score
    done = len(attempted) >= len([trick for trick in CIRCUS_TRICKS if trick[2] <= level])
    outputs: dict[str, int] = {}
    if done:
        data["agility_circus_last_week"] = _answered_card_week(data)
        if session_score >= 501:
            reward = _next_missing_reward(data, CIRCUS_ACROBAT_REWARDS)
            if reward:
                outputs[reward] = 1
        session.clear()
    status = f"Circus · {label} · {'success' if success else 'failed'} · {len(attempted)} actions · {session_score} audience"
    data["agility_status"] = status
    return {"target_id": "circus_agility", "action_id": trick_id, "success": success, "expected_success_chance": success_chance, "xp": xp_value if success else 0.0, "damage": 0, "outputs": outputs, "cross_skill_rewards": [], "completed_activity": done, "failure_kind": None if success else "trick", "status": status}


def _new_brimhaven_chase(session: dict[str, Any], agility_level: int, route_roll: float, obstacle_roll: float) -> None:
    distance = 1 + min(7, int(max(0.0, min(route_roll, .999999)) * 8))
    eligible = [row for row in BRIMHAVEN_OBSTACLES if row[2] <= agility_level]
    obstacle = eligible[min(int(max(0.0, min(obstacle_roll, .999999)) * len(eligible)), len(eligible) - 1)]
    session.update({"crossings_remaining": distance, "attempts_remaining": 8, "obstacle_id": obstacle[0], "obstacle_label": obstacle[1], "obstacle_xp": obstacle[3], "obstacle_fail": obstacle[4], "temporary_drain": 0, "needs_chase": False})


def _brimhaven_review(data: dict[str, Any], rolls: tuple[float, ...]) -> dict[str, Any]:
    session = _activity_session(data, "brimhaven")
    inventory = dict(data.get("inventory") or {})
    if not session.get("stint_active"):
        if not _quest_complete(data, "rocking_out"):
            inventory["Coins"] = _int(inventory.get("Coins")) - 200
            data["inventory"] = inventory
        session.update({"stint_active": True, "activated": False, "needs_chase": True})
    level = _int(data.get("agility_level"), 1, minimum=1, maximum=99)
    if session.get("needs_chase", True):
        _new_brimhaven_chase(session, max(1, level - _int(session.get("temporary_drain"))), rolls[0], rolls[1])
    fail_chance = _float(session.get("obstacle_fail"), maximum=1.0)
    success = rolls[2] >= fail_chance
    xp = _float(session.get("obstacle_xp")) if success else 0.0
    if success and any(
        item in (data.get("equipment") or {}).values()
        for item in ("Karamja gloves 2", "Karamja gloves 3", "Karamja gloves 4")
    ):
        xp *= 1.10
    damage = 0
    tickets = 0
    if success:
        session["crossings_remaining"] = _int(session.get("crossings_remaining"), 1, minimum=1, maximum=8) - 1
    else:
        current_lp = _int(data.get("combat_lifepoints"), 1000, minimum=1, maximum=10000)
        damage = int(_clamp(math.floor(current_lp / 10), 20, 60))
        if session.get("obstacle_id") == "darts":
            session["temporary_drain"] = _int(session.get("temporary_drain"), maximum=20) + 2
    session["attempts_remaining"] = _int(session.get("attempts_remaining"), 8, minimum=1, maximum=8) - 1
    tagged = success and session["crossings_remaining"] <= 0
    missed = session["attempts_remaining"] <= 0 and not tagged
    if tagged:
        if session.get("activated"):
            tickets = 1
            equipment = data.get("equipment") or {}
            if "Karamja gloves 4" in equipment.values() and rolls[3] < .25:
                tickets += 1
            inventory = dict(data.get("inventory") or {})
            inventory["Agility arena ticket"] = _int(inventory.get("Agility arena ticket")) + tickets
            data["inventory"] = inventory
        session.update({"activated": True, "needs_chase": True, "temporary_drain": 0})
    elif missed:
        session.update({"activated": False, "needs_chase": True, "temporary_drain": 0})
    status = f"{session.get('obstacle_label', 'Obstacle')} · {'crossed' if success else 'failed'} · {session.get('crossings_remaining', 0)} crossings · {session.get('attempts_remaining', 0)} attempts · {'active' if session.get('activated') else 'inactive'} · {_int((data.get('inventory') or {}).get('Agility arena ticket'))} tickets"
    data["agility_status"] = status
    return {"target_id": "brimhaven_arena", "action_id": str(session.get("obstacle_id", "obstacle")), "success": success, "expected_success_chance": 1 - fail_chance, "xp": xp, "damage": damage, "outputs": {}, "cross_skill_rewards": [], "completed_activity": tagged, "failure_kind": None if success else "obstacle", "status": status, "tickets": tickets}


def apply_agility_review_pure(player_data: Mapping[str, Any], rolls: tuple[float, ...]) -> tuple[dict[str, Any], dict[str, Any]]:
    data = sanitize_agility_state_pure(copy.deepcopy(player_data))
    target_id = data["current_agility"]
    target = AGILITY_TARGETS_BY_ID[target_id]
    if agility_target_locked_reasons_pure(data, target_id):
        return data, {"allowed": False, "target_id": target_id, "message": "Target is locked"}
    normalized = tuple(_clamp(_float(value, maximum=1.0), 0.0, 1.0) for value in rolls)
    normalized = normalized + (0.5,) * max(0, 4 - len(normalized))
    if data.get("agility_toy_mouse_pending"):
        success = normalized[0] < .80
        data["agility_toy_mouse_pending"] = False
        status = f"Toy mouse · {'caught' if success else 'escaped'} · attempt complete"
        data["agility_status"] = status
        result = {
            "target_id": "toy_mouse",
            "action_id": "catch_released_mouse",
            "success": success,
            "expected_success_chance": .80,
            "xp": 3.0 if success else 0.0,
            "damage": 0,
            "outputs": {},
            "cross_skill_rewards": [],
            "failure_kind": None if success else "escaped",
            "status": status,
            "modifier_eligible": False,
        }
    elif target.activity_kind == "skullball":
        result = _skullball_review(data, normalized[0])
    elif target.activity_kind == "gnome_ball":
        result = _gnome_ball_review(data, normalized[0])
    elif target.activity_kind == "flash_powder_factory":
        data, result = apply_flash_powder_factory_review_pure(data, normalized)
        if not result.get("allowed"):
            return data, result
    elif target.activity_kind == "pit":
        result = _pit_review(data, normalized[0], normalized[1])
    elif target.activity_kind == "circus":
        result = _circus_review(data, normalized[0])
    elif target.activity_kind == "brimhaven":
        result = _brimhaven_review(data, normalized)
    else:
        carried_views = data.get("carried_inventory")
        raw_active_view = (
            carried_views.get(target_id, {})
            if isinstance(carried_views, Mapping)
            else {}
        )
        active_view = clamp_carried_view_to_bank(raw_active_view, data.get("inventory"))
        _carried_weight, effective_weight = agility_carried_weight_pure(
            active_view,
            data.get("equipment", {}),
        )
        result = _standard_course_review(
            data,
            target,
            normalized[0],
            normalized[1],
            effective_weight,
        )
        if target_id == "wilderness_course" and result.get("completed_lap"):
            triggered = normalized[2] < WILDERNESS_PKER_AMBUSH_CHANCE
            ambush = {"triggered": triggered}
            if triggered:
                damage_roll = max(0.0, min(normalized[3], 0.999999999))
                damage = 1 + int(damage_roll * (WILDERNESS_PKER_MAX_HIT_LP - 1))
                result["damage"] = damage
                ambush["damage"] = damage
                data["agility_status"] = (
                    f"{data.get('agility_status', 'Lap complete')} · "
                    f"PKer ambush · {damage} LP"
                )
            result["wilderness_ambush"] = ambush
    result["allowed"] = True
    _apply_agility_xp_modifiers(data, target, result)
    _advance_agility_effect_budgets(
        data,
        standard_course=target.activity_kind is None and result.get("target_id") != "toy_mouse",
    )
    if target.activity_kind and result.get("completed_activity"):
        completions = dict(data.get("agility_activity_completions") or {})
        completions[target.activity_kind] = _int(completions.get(target.activity_kind)) + 1
        data["agility_activity_completions"] = completions
    data["agility_actions_completed"] = _int(data.get("agility_actions_completed")) + 1
    return data, result


def redeem_brimhaven_tickets_pure(player_data: Mapping[str, Any], ticket_count: int, *, item_reward: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
    data = sanitize_agility_state_pure(copy.deepcopy(player_data))
    inventory = dict(data.get("inventory") or {})
    count = int(ticket_count)
    table = BRIMHAVEN_ITEM_EXCHANGES if item_reward else BRIMHAVEN_XP_EXCHANGES
    if count not in table or _int(inventory.get("Agility arena ticket")) < count:
        return data, {"allowed": False, "message": "Not enough tickets"}
    inventory["Agility arena ticket"] -= count
    data["inventory"] = inventory
    if item_reward:
        item_name = str(table[count])
        inventory[item_name] = _int(inventory.get(item_name)) + 1
        return data, {"allowed": True, "item": item_name, "xp": 0.0}
    xp = float(table[count])
    equipment = data.get("equipment") or {}
    if any(item in equipment.values() for item in ("Karamja gloves 2", "Karamja gloves 3", "Karamja gloves 4")):
        xp *= 1.10
    return data, {"allowed": True, "xp": xp}


def claim_agile_piece_pure(player_data: Mapping[str, Any], piece: str) -> tuple[dict[str, Any], bool]:
    data = sanitize_agility_state_pure(copy.deepcopy(player_data))
    unlock_key = {"Agile top": "agile_top_unlocked", "Agile legs": "agile_legs_unlocked"}.get(piece)
    if unlock_key is None or not data["agility_lap_counts"].get(unlock_key):
        return data, False
    inventory = dict(data.get("inventory") or {})
    equipment = data.get("equipment") or {}
    if _int(inventory.get(piece)) <= 0 and piece not in equipment.values():
        inventory[piece] = 1
        data["inventory"] = inventory
    return data, True


def sell_pyramid_top_pure(player_data: Mapping[str, Any], count: int = 1) -> tuple[dict[str, Any], bool]:
    data = sanitize_agility_state_pure(copy.deepcopy(player_data))
    inventory = dict(data.get("inventory") or {})
    amount = max(1, int(count))
    if _int(inventory.get("Pyramid top")) < amount:
        return data, False
    inventory["Pyramid top"] -= amount
    inventory["Coins"] = _int(inventory.get("Coins")) + 1000 * amount
    data["inventory"] = inventory
    return data, True


def apply_agility_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Optional[Mapping[str, Any]] = None,
    *,
    roll: float = 0.5,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply one explicit non-review Agility operation."""

    body = dict(payload or {})
    if action_id == "enter_flash_powder_factory":
        updated, ok, info = enter_flash_powder_factory_pure(
            player_data,
            confirm_dismiss_follower=bool(body.get("confirm_dismiss_follower", False)),
        )
        return updated, {"allowed": ok, **info}
    if action_id == "set_flash_powder_factory_policy":
        updated, ok, info = set_flash_powder_factory_policy_pure(
            player_data,
            automation_mode=body.get("automation_mode"),
            strategy=body.get("strategy"),
            apparatus_policy=body.get("apparatus_policy"),
        )
        return updated, {"allowed": ok, **info}
    if action_id == "leave_flash_powder_factory":
        updated, ok, info = leave_flash_powder_factory_pure(player_data)
        return updated, {"allowed": ok, **info}
    if action_id == "redeem_flash_powder_factory_xp":
        updated, ok, info = redeem_flash_powder_factory_xp_pure(
            player_data,
            str(body.get("skill_id", "")),
            body.get("points"),
        )
        return updated, {"allowed": ok, **info}
    if action_id == "redeem_flash_powder_factory_item":
        updated, ok, info = redeem_flash_powder_factory_item_pure(
            player_data,
            str(body.get("item_name", "")),
        )
        return updated, {"allowed": ok, **info}
    if action_id == "sell_pyramid_top":
        updated, ok = sell_pyramid_top_pure(player_data, _int(body.get("count"), 1, minimum=1))
        return updated, {"allowed": ok, "message": "Sold Pyramid top" if ok else "No Pyramid top to sell"}
    if action_id == "claim_agile_piece":
        piece = str(body.get("piece", ""))
        updated, ok = claim_agile_piece_pure(player_data, piece)
        return updated, {"allowed": ok, "item": piece if ok else None, "message": f"Claimed {piece}" if ok else "That Agile piece is not unlocked"}
    if action_id == "redeem_brimhaven_xp":
        updated, result = redeem_brimhaven_tickets_pure(player_data, _int(body.get("tickets"), minimum=1))
        result.setdefault("message", "Redeemed arena tickets" if result.get("allowed") else "Not enough arena tickets")
        return updated, result
    if action_id == "redeem_brimhaven_item":
        updated, result = redeem_brimhaven_tickets_pure(player_data, _int(body.get("tickets"), minimum=1), item_reward=True)
        result.setdefault("message", "Redeemed arena tickets" if result.get("allowed") else "Not enough arena tickets")
        return updated, result
    if action_id in {"claim_pit_reward", "gamble_pit_reward"}:
        data = sanitize_agility_state_pure(copy.deepcopy(player_data))
        activities = dict(data.get("agility_activity_state") or {})
        reward = activities.get("pit_reward")
        if not isinstance(reward, Mapping) or _float(reward.get("xp")) <= 0:
            return data, {"allowed": False, "message": "No Pit reward is waiting"}
        multiplier = 1.0
        if action_id == "gamble_pit_reward":
            multiplier = (0.5, 1.0, 2.0)[min(2, int(_clamp(float(roll), 0.0, 0.999999) * 3))]
        xp = _float(reward.get("xp")) * multiplier
        activities.pop("pit_reward", None)
        data["agility_activity_state"] = activities
        if body.get("remember_choice"):
            data = remember_review_context_choice_pure(
                data,
                PIT_REWARD_CONTEXT_ID,
                "gamble" if action_id == "gamble_pit_reward" else "take_xp",
            )
        return data, {"allowed": True, "xp": xp, "multiplier": multiplier, "message": f"Claimed {xp:g} Agility XP"}
    if action_id == "set_pit_auto_accept":
        data = sanitize_agility_state_pure(copy.deepcopy(player_data))
        data["agility_pit_auto_accept"] = bool(body.get("enabled", True))
        state = "enabled" if data["agility_pit_auto_accept"] else "disabled"
        return data, {
            "allowed": True,
            "message": f"Automatic Talent Scout acceptance {state}",
        }
    if action_id == "accept_pit_offer":
        data = sanitize_agility_state_pure(copy.deepcopy(player_data))
        if not data.get("agility_pit_offer"):
            return data, {"allowed": False, "message": "No Talent Scout invitation is waiting"}
        if _active_familiar_pure(data):
            if not body.get("dismiss_familiar"):
                return data, {
                    "allowed": False,
                    "requires_familiar_dismissal": True,
                    "message": "Dismiss the active familiar before entering The Pit",
                }
            try:
                from .summoning_logic import dismiss_familiar_pure
            except ImportError:  # pragma: no cover - flat test imports
                from summoning_logic import dismiss_familiar_pure  # type: ignore
            dismissed, ok, _info = dismiss_familiar_pure(data)
            if not ok:
                return data, {"allowed": False, "message": "The familiar could not be dismissed"}
            data = sanitize_agility_state_pure(dismissed)
        _arm_pit_offer_pure(data)
        return data, {"allowed": True, "message": data["agility_status"]}
    if action_id == "decline_pit_offer":
        data = sanitize_agility_state_pure(copy.deepcopy(player_data))
        if not data.get("agility_pit_offer"):
            return data, {"allowed": False, "message": "No Talent Scout invitation is waiting"}
        data["agility_pit_offer"] = False
        data["agility_pit_origin_course"] = ""
        data["agility_status"] = "The Pit · Talent Scout invitation declined"
        return data, {"allowed": True, "message": data["agility_status"]}
    if action_id == "leave_activity":
        data = sanitize_agility_state_pure(copy.deepcopy(player_data))
        target = AGILITY_TARGETS_BY_ID[data["current_agility"]]
        if not target.activity_kind:
            return data, {"allowed": False, "message": "The selected target is not an activity"}
        if target.id == FLASH_POWDER_FACTORY_ACTIVITY_ID:
            updated, ok, info = leave_flash_powder_factory_pure(data)
            return updated, {"allowed": ok, **info}
        activities = dict(data.get("agility_activity_state") or {})
        session = activities.get(target.activity_kind)
        message_suffix = ""
        if target.activity_kind == "circus":
            data["agility_circus_last_week"] = _answered_card_week(data)
        elif target.activity_kind == "pit":
            origin_course = (
                str(session.get("origin_course", ""))
                if isinstance(session, Mapping)
                else str(data.get("agility_pit_origin_course", ""))
            )
            if origin_course not in PIT_INVITATION_COURSE_IDS:
                origin_course = DEFAULT_AGILITY_TARGET
            data["current_agility"] = origin_course
            data["agility_pit_offer"] = False
            data["agility_pit_origin_course"] = ""
            message_suffix = (
                f" and returned to "
                f"{AGILITY_TARGETS_BY_ID[origin_course].display_name}"
            )
        activities.pop(target.activity_kind, None)
        data["agility_activity_state"] = activities
        data["agility_status"] = f"Left {target.display_name}{message_suffix}"
        return data, {"allowed": True, "message": data["agility_status"]}
    if action_id == "purchase_agility_cape":
        data = sanitize_agility_state_pure(copy.deepcopy(player_data))
        if _int(data.get("agility_level"), 1, minimum=1, maximum=120) < 99:
            return data, {"allowed": False, "message": "Requires level 99 Agility"}
        inventory = dict(data.get("inventory") or {})
        if _int(inventory.get("Agility cape")) > 0 or _owns_item(data, "Agility cape"):
            return data, {"allowed": False, "message": "You already own the Agility cape"}
        if _int(inventory.get("Coins")) < 99_000:
            return data, {"allowed": False, "message": "Requires 99,000 coins"}
        inventory["Coins"] -= 99_000
        inventory["Agility cape"] = _int(inventory.get("Agility cape")) + 1
        inventory["Agility hood"] = _int(inventory.get("Agility hood")) + 1
        data["inventory"] = inventory
        return data, {"allowed": True, "message": "Bought the Agility cape and hood"}
    if action_id == "activate_agility_cape":
        data = sanitize_agility_state_pure(copy.deepcopy(player_data))
        if not _owns_item(data, "Agility cape"):
            return data, {"allowed": False, "message": "You do not own the Agility cape"}
        if _int(data.get("agility_effective_boost")) > 1:
            return data, {"allowed": False, "message": "A stronger Agility boost is already active"}
        data["agility_effective_boost"] = 1
        data["agility_boost_actions_remaining"] = 10
        return data, {"allowed": True, "message": "Agility cape boost active for 10 Agility actions"}
    if action_id == "activate_surefooted":
        data = sanitize_agility_state_pure(copy.deepcopy(player_data))
        charges = dict(data.get("agility_effect_charges") or {})
        if _int(charges.get("surefooted_cooldown_reviews")) > 0:
            return data, {"allowed": False, "message": "Surefooted is still recharging"}
        inventory = data.get("inventory") or {}
        equipment = data.get("equipment") or {}
        owned = set(equipment.values()) if isinstance(equipment, Mapping) else set()
        if isinstance(inventory, Mapping):
            owned.update(item for item, amount in inventory.items() if _int(amount) > 0)
        aura = next((item for item in ("Greater surefooted aura", "Surefooted aura") if item in owned), None)
        if aura is None:
            return data, {"allowed": False, "message": "You do not own a Surefooted aura"}
        # 20/40-minute period durations and the two-hour cooldown become
        # answered-action budgets at AnkiScape's 1,000-review/hour reference.
        charges["surefooted_reviews"] = 667 if aura.startswith("Greater") else 333
        charges["surefooted_cooldown_reviews"] = 2000
        data["agility_effect_charges"] = charges
        return data, {"allowed": True, "message": f"Activated {aura} for {charges['surefooted_reviews']} Agility actions"}
    if action_id == "wind_toy_mouse":
        data = sanitize_agility_state_pure(copy.deepcopy(player_data))
        if not _owns_item(data, "Toy mouse"):
            return data, {"allowed": False, "message": "You do not own a Toy mouse"}
        if data.get("agility_toy_mouse_pending"):
            return data, {"allowed": False, "message": "A Toy mouse catch is already waiting"}
        data["agility_toy_mouse_pending"] = True
        data["agility_status"] = "Toy mouse · wound and released · catch it on the next Agility review"
        return data, {"allowed": True, "message": data["agility_status"]}
    return sanitize_agility_state_pure(copy.deepcopy(player_data)), {"allowed": False, "message": "Unknown Agility command"}


def agility_status_line_pure(player_data: Mapping[str, Any]) -> str:
    data = sanitize_agility_state_pure(player_data)
    return data["agility_status"]
