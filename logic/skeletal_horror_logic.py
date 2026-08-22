"""Pure, review-driven Skeletal Horror boss-instance mechanics."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any

from ..data.skeletal_horror_data import (
    SKELETAL_HORROR_ACTIVITY_ID,
    SKELETAL_HORROR_ELITE_CLUE_CHANCE,
    SKELETAL_HORROR_ELITE_CLUE_ITEM,
    SKELETAL_HORROR_ENTRY_CAP,
    SKELETAL_HORROR_FIRST_REWARDS,
    SKELETAL_HORROR_FUR_WISH_LIST_SLAYER_LEVEL,
    SKELETAL_HORROR_LIMBS,
    SKELETAL_HORROR_MAX_LIFEPOINTS,
    SKELETAL_HORROR_PHASES,
    SKELETAL_HORROR_REPEAT_REWARDS,
    SKELETAL_HORROR_TARGET_ID,
    SKELETAL_HORROR_WEEK_REVIEWS,
    skeletal_horror_enemy_pure,
)
from ..logic_pure.logic_pure import (
    apply_combat_burst_pure,
    combat_target_locked_reasons_pure,
)
from .treasure_trails_logic import (
    clue_ownership_reason_pure,
    filter_clue_scroll_outputs_pure,
)


SKELETAL_HORROR_STATE_VERSION = 1
# Darkan SkeletalHorror.kt:114-121 uses Utils.random(2): 0 selects Melee,
# otherwise Magic, so both styles have equal probability while available.
SKELETAL_HORROR_MAGIC_STYLE_CHANCE = 0.5


def _int(value: Any, default: int = 0, *, minimum: int = 0) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(minimum, parsed)


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError, OverflowError):
        return default


def _answered_cards(player_data: Mapping[str, Any]) -> int:
    clock = player_data.get("shop_market_clock")
    return _int(clock.get("answered_cards")) if isinstance(clock, Mapping) else 0


def _world_week(player_data: Mapping[str, Any]) -> int:
    return _answered_cards(player_data) // SKELETAL_HORROR_WEEK_REVIEWS


def _quest_complete(player_data: Mapping[str, Any], quest_id: str) -> bool:
    quests = player_data.get("quests")
    quest = quests.get(quest_id) if isinstance(quests, Mapping) else None
    return isinstance(quest, Mapping) and bool(quest.get("completed"))


def _phase_index_for_lifepoints(lifepoints: int) -> int:
    """The phase table owns the thresholds; never restate them here."""
    index = 0
    for candidate, phase in enumerate(SKELETAL_HORROR_PHASES):
        if lifepoints <= phase["remaining_lifepoints"]:
            index = candidate
    return index


def default_skeletal_horror_state_pure() -> dict[str, Any]:
    return {
        "version": SKELETAL_HORROR_STATE_VERSION,
        "rag_wish_list_complete": False,
        "fur_wish_list_complete": False,
        "active": False,
        "lifepoints": 0,
        "phase_index": 0,
        "encounter": {},
        "previous_combat_target": "",
        "kills": 0,
        "allowance_week_index": -1,
        "available_entries": 0,
        "last_result": "",
    }


def _sanitize_encounter(raw: Any, lifepoints: int) -> dict[str, Any]:
    if lifepoints <= 0:
        return {}
    source = raw if isinstance(raw, Mapping) else {}
    encounter = {
        str(key): copy.deepcopy(value)
        for key, value in source.items()
        if isinstance(key, str)
    }
    encounter["target_id"] = SKELETAL_HORROR_TARGET_ID
    encounter["enemy_lifepoints"] = lifepoints
    return encounter


def sanitize_skeletal_horror_state_pure(raw: Any) -> dict[str, Any]:
    defaults = default_skeletal_horror_state_pure()
    source = raw if isinstance(raw, Mapping) else {}
    active = bool(source.get("active", False))
    lifepoints = min(
        SKELETAL_HORROR_MAX_LIFEPOINTS,
        _int(source.get("lifepoints"), SKELETAL_HORROR_MAX_LIFEPOINTS),
    )
    if not active or lifepoints <= 0:
        active = False
        lifepoints = 0
    kills = _int(source.get("kills"))
    return {
        **defaults,
        "rag_wish_list_complete": bool(source.get("rag_wish_list_complete", False)),
        "fur_wish_list_complete": bool(source.get("fur_wish_list_complete", False)),
        "active": active,
        "lifepoints": lifepoints,
        "phase_index": _phase_index_for_lifepoints(lifepoints) if active else 0,
        "encounter": _sanitize_encounter(source.get("encounter"), lifepoints),
        "previous_combat_target": str(source.get("previous_combat_target", ""))[:120],
        "kills": kills,
        "allowance_week_index": max(
            -1,
            _int(source.get("allowance_week_index"), -1, minimum=-1),
        ),
        "available_entries": min(
            SKELETAL_HORROR_ENTRY_CAP,
            _int(source.get("available_entries")),
        ),
        "last_result": str(source.get("last_result", ""))[:500],
    }


def _sync_entries(
    state: Mapping[str, Any],
    player_data: Mapping[str, Any],
) -> dict[str, Any]:
    synced = dict(state)
    if _int(synced.get("kills")) <= 0:
        return synced
    current_week = _world_week(player_data)
    previous_week = _int(
        synced.get("allowance_week_index"),
        current_week,
        minimum=-1,
    )
    if previous_week < 0:
        synced["allowance_week_index"] = current_week
        return synced
    if current_week > previous_week:
        synced["available_entries"] = min(
            SKELETAL_HORROR_ENTRY_CAP,
            _int(synced.get("available_entries")) + current_week - previous_week,
        )
        synced["allowance_week_index"] = current_week
    return synced


def skeletal_horror_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = _sync_entries(
        sanitize_skeletal_horror_state_pure(player_data.get("skeletal_horror")),
        player_data,
    )
    rag_ready = _quest_complete(player_data, "rag_and_bone_man")
    fur_ready = _quest_complete(player_data, "fur_n_seek") and (
        _int(player_data.get("slayer_level"), 1, minimum=1)
        >= SKELETAL_HORROR_FUR_WISH_LIST_SLAYER_LEVEL
    )
    missing = []
    if not rag_ready:
        missing.append("Complete Rag and Bone Man")
    elif not state["rag_wish_list_complete"]:
        missing.append("Complete Rag and Bone Man's wish list")
    if not _quest_complete(player_data, "fur_n_seek"):
        missing.append("Complete Fur 'n Seek")
    if (
        _int(player_data.get("slayer_level"), 1, minimum=1)
        < SKELETAL_HORROR_FUR_WISH_LIST_SLAYER_LEVEL
    ):
        missing.append(
            f"Slayer level {SKELETAL_HORROR_FUR_WISH_LIST_SLAYER_LEVEL}"
        )
    elif not state["fur_wish_list_complete"]:
        missing.append("Complete Fur 'n Seek's wish list")
    first_ready = state["kills"] == 0
    entry_ready = first_ready or state["available_entries"] > 0
    reviews_to_entry = 0
    if state["kills"] > 0 and state["available_entries"] <= 0:
        remainder = _answered_cards(player_data) % SKELETAL_HORROR_WEEK_REVIEWS
        reviews_to_entry = SKELETAL_HORROR_WEEK_REVIEWS - remainder
    phase = SKELETAL_HORROR_PHASES[state["phase_index"]]
    return {
        **state,
        "requirements_met": not missing,
        "missing_requirements": tuple(missing),
        "rag_wish_list_ready": rag_ready,
        "fur_wish_list_ready": fur_ready,
        "first_ready": first_ready,
        "entry_ready": entry_ready,
        "reviews_to_entry": reviews_to_entry,
        "combat_level": phase["combat_level"],
        "attack_styles": tuple(phase["attack_styles"]),
        "limbs_removed": tuple(SKELETAL_HORROR_LIMBS[: state["phase_index"]]),
    }


def _end_encounter(
    data: dict[str, Any],
    state: dict[str, Any],
    message: str,
) -> None:
    state["active"] = False
    state["lifepoints"] = 0
    state["phase_index"] = 0
    state["encounter"] = {}
    state["last_result"] = message[:500]
    data["skeletal_horror"] = state
    data["activity_session"] = {"active_id": ""}
    data["combat_encounter"] = {}
    data["current_combat_target"] = str(state.get("previous_combat_target", ""))


def apply_skeletal_horror_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
    *,
    equipment_data: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = _sync_entries(
        sanitize_skeletal_horror_state_pure(data.get("skeletal_horror")),
        data,
    )
    data["skeletal_horror"] = state

    if action_id == "complete_rag_wish_list":
        if state["rag_wish_list_complete"]:
            return data, False, {"reason": "Rag and Bone Man's wish list is already complete."}
        if not _quest_complete(data, "rag_and_bone_man"):
            return data, False, {"reason": "Complete Rag and Bone Man first."}
        state["rag_wish_list_complete"] = True
        state["last_result"] = "Completed Rag and Bone Man's post-quest wish list."
        return data, True, {"message": state["last_result"]}

    if action_id == "complete_fur_wish_list":
        if state["fur_wish_list_complete"]:
            return data, False, {"reason": "Fur 'n Seek's wish list is already complete."}
        if not _quest_complete(data, "fur_n_seek"):
            return data, False, {"reason": "Complete Fur 'n Seek first."}
        if (
            _int(data.get("slayer_level"), 1, minimum=1)
            < SKELETAL_HORROR_FUR_WISH_LIST_SLAYER_LEVEL
        ):
            return data, False, {
                "reason": (
                    "Fur 'n Seek's wish list requires Slayer level "
                    f"{SKELETAL_HORROR_FUR_WISH_LIST_SLAYER_LEVEL}."
                )
            }
        state["fur_wish_list_complete"] = True
        state["last_result"] = "Completed Fur 'n Seek's post-quest wish list."
        return data, True, {"message": state["last_result"]}

    if action_id == "enter":
        if state["active"]:
            data["activity_session"] = {"active_id": SKELETAL_HORROR_ACTIVITY_ID}
            data["current_utility"] = SKELETAL_HORROR_ACTIVITY_ID
            return data, True, {"message": "Skeletal Horror selected for reviews."}
        active_session = data.get("activity_session")
        if isinstance(active_session, Mapping) and active_session.get("active_id"):
            return data, False, {"reason": "Another persistent activity is active."}
        view = skeletal_horror_view_pure(data)
        if not view["requirements_met"]:
            return data, False, {"reason": "; ".join(view["missing_requirements"]) + "."}
        if not view["entry_ready"]:
            return data, False, {
                "reason": (
                    "No weekly Skeletal Horror entry is banked; "
                    f"{view['reviews_to_entry']:,} reviews remain."
                )
            }
        previous_target = str(data.get("current_combat_target", ""))[:120]
        encounter = {
            "target_id": SKELETAL_HORROR_TARGET_ID,
            "enemy_lifepoints": SKELETAL_HORROR_MAX_LIFEPOINTS,
        }
        state.update(
            {
                "active": True,
                "lifepoints": SKELETAL_HORROR_MAX_LIFEPOINTS,
                "phase_index": 0,
                "encounter": encounter,
                "previous_combat_target": previous_target,
                "last_result": (
                    "Entered the Skeletal Horror lair at "
                    f"{SKELETAL_HORROR_MAX_LIFEPOINTS:,} LP."
                ),
            }
        )
        data["current_combat_target"] = SKELETAL_HORROR_TARGET_ID
        data["combat_encounter"] = copy.deepcopy(encounter)
        locked = combat_target_locked_reasons_pure(
            data,
            SKELETAL_HORROR_TARGET_ID,
            {
                SKELETAL_HORROR_TARGET_ID: skeletal_horror_enemy_pure(
                    0, "melee"
                )
            },
            equipment_data=equipment_data or {},
        )
        if locked:
            return dict(player_data), False, {
                "reason": "Combat loadout is not ready: " + "; ".join(locked)
            }
        data["skeletal_horror"] = state
        data["activity_session"] = {"active_id": SKELETAL_HORROR_ACTIVITY_ID}
        data["current_utility"] = SKELETAL_HORROR_ACTIVITY_ID
        return data, True, {"message": state["last_result"]}

    if action_id == "leave":
        if not state["active"]:
            return data, False, {"reason": "No Skeletal Horror encounter is active."}
        _end_encounter(
            data,
            state,
            "Left the Skeletal Horror lair; the weekly entry was not consumed.",
        )
        return data, True, {"message": state["last_result"]}

    return data, False, {"reason": "Unknown Skeletal Horror command."}


def _roll_attack_style(phase_index: int, rng) -> str:
    styles = SKELETAL_HORROR_PHASES[phase_index]["attack_styles"]
    if len(styles) == 1:
        return styles[0]
    try:
        return "magic" if float(rng()) < SKELETAL_HORROR_MAGIC_STYLE_CHANCE else "melee"
    except (TypeError, ValueError, OverflowError):
        return "melee"


def _merge_xp_rewards(*rows: Mapping[str, Any]) -> dict[str, float]:
    merged: dict[str, float] = {}
    for row in rows:
        for key, amount in row.items():
            merged[str(key)] = merged.get(str(key), 0.0) + _float(amount)
    return merged


def apply_skeletal_horror_review_pure(
    player_data: Mapping[str, Any],
    rng,
    *,
    equipment_data: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = _sync_entries(
        sanitize_skeletal_horror_state_pure(data.get("skeletal_horror")),
        data,
    )
    if not state["active"]:
        return data, False, {"reason": "Enter the Skeletal Horror lair before training."}

    old_phase = state["phase_index"]
    attack_style = _roll_attack_style(old_phase, rng)
    data["current_combat_target"] = SKELETAL_HORROR_TARGET_ID
    data["combat_encounter"] = _sanitize_encounter(
        state.get("encounter"),
        state["lifepoints"],
    )
    data, ok, combat_result = apply_combat_burst_pure(
        data,
        {
            SKELETAL_HORROR_TARGET_ID: skeletal_horror_enemy_pure(
                old_phase,
                attack_style,
            )
        },
        equipment_data or {},
        ticks=6,
        rng=rng,
        live_cadence=True,
        stop_after_first_kill=True,
        # "Death places the player's grave outside the encounter" — the lair is
        # dangerous, so the ordinary live-Combat death path runs.
        safe_death=False,
        allow_bank_run=False,
    )
    if not ok:
        return dict(player_data), False, combat_result

    if combat_result.get("died") or combat_result.get("fled"):
        outcome = (
            "Defeated safely by the Skeletal Horror"
            if combat_result.get("died")
            else "Fled the Skeletal Horror"
        )
        _end_encounter(
            data,
            state,
            outcome + "; the weekly entry was not consumed.",
        )
        return data, True, {
            **combat_result,
            "outcome": state["last_result"],
            "status": state["last_result"],
        }

    if not combat_result.get("killed"):
        lifepoints = max(
            1,
            _int(
                combat_result.get("enemy_lifepoints"),
                state["lifepoints"],
                minimum=1,
            ),
        )
        new_phase = _phase_index_for_lifepoints(lifepoints)
        removed_limbs = tuple(SKELETAL_HORROR_LIMBS[old_phase:new_phase])
        state["lifepoints"] = lifepoints
        state["phase_index"] = new_phase
        state["encounter"] = _sanitize_encounter(
            data.get("combat_encounter"),
            lifepoints,
        )
        phase = SKELETAL_HORROR_PHASES[new_phase]
        transition = (
            " · removed and buried " + ", ".join(removed_limbs)
            if removed_limbs
            else ""
        )
        state["last_result"] = (
            f"Skeletal Horror: {lifepoints:,}/{SKELETAL_HORROR_MAX_LIFEPOINTS:,} LP "
            f"· level {phase['combat_level']} · {'/'.join(phase['attack_styles'])}"
            + transition
        )
        data["skeletal_horror"] = state
        data["activity_session"] = {"active_id": SKELETAL_HORROR_ACTIVITY_ID}
        return data, True, {
            **combat_result,
            "attack_style": attack_style,
            "removed_limbs": removed_limbs,
            "phase_index": new_phase,
            "status": state["last_result"],
        }

    first_completion = state["kills"] == 0
    completion_rewards = (
        SKELETAL_HORROR_FIRST_REWARDS
        if first_completion
        else SKELETAL_HORROR_REPEAT_REWARDS
    )
    for exp_key, amount in completion_rewards.items():
        data[exp_key] = _float(data.get(exp_key)) + amount
    clue_dropped = False
    if not first_completion:
        try:
            clue_dropped = float(rng()) < SKELETAL_HORROR_ELITE_CLUE_CHANCE
        except (TypeError, ValueError, OverflowError):
            clue_dropped = False
    clue_refusal_reason = ""
    if clue_dropped:
        ownership_reason = clue_ownership_reason_pure(data)
        clue_outputs = filter_clue_scroll_outputs_pure(
            data, {SKELETAL_HORROR_ELITE_CLUE_ITEM: 1}
        )
        clue_dropped = SKELETAL_HORROR_ELITE_CLUE_ITEM in clue_outputs
        if ownership_reason and not clue_dropped:
            clue_refusal_reason = ownership_reason
        if clue_dropped:
            inventory = dict(data.get("inventory", {}) or {})
            inventory[SKELETAL_HORROR_ELITE_CLUE_ITEM] = (
                _int(inventory.get(SKELETAL_HORROR_ELITE_CLUE_ITEM)) + 1
            )
            data["inventory"] = inventory
    state["kills"] += 1
    state["allowance_week_index"] = _world_week(data)
    if not first_completion:
        state["available_entries"] = max(0, state["available_entries"] - 1)
    message = (
        "Skeletal Horror rebuilt and defeated"
        if first_completion
        else "Skeletal Horror defeated"
    )
    message += (
        f" · +{int(completion_rewards['slayer_exp']):,} Slayer XP"
        f" · +{int(completion_rewards['prayer_exp']):,} Prayer XP"
        + (" · elite clue scroll" if clue_dropped else "")
        + (f" · {clue_refusal_reason}" if clue_refusal_reason else "")
    )
    _end_encounter(data, state, message)
    data["skeletal_horror"] = state
    return data, True, {
        **combat_result,
        "outcome": message,
        "status": message,
        "first_completion": first_completion,
        "clue_dropped": clue_dropped,
        "clue_refusal_reason": clue_refusal_reason,
        "removed_limbs": tuple(SKELETAL_HORROR_LIMBS[old_phase:]),
        "xp_rewards": _merge_xp_rewards(
            combat_result.get("xp_rewards", {}) or {},
            completion_rewards,
        ),
    }
