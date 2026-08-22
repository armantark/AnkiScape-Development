"""Pure, review-driven Bork daily encounter mechanics.

Bork is the engaged target for the whole encounter and the Ork legion is pure
incoming pressure. That is the settled engaged-target + pressure-roster shape
read the only way the period allows: the legions despawn the instant Bork dies
(Darkan `Bork.sendDeath` finishes every nearby npc 7135), and the pinned page
says outright that they "are usually ignored because they disappear when Bork
is killed". There is no target to choose, so the encounter presents its legion
as one collapsed pressure front.
"""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any

from ..data.bork_data import (
    BORK_ACTIVITY_ID,
    BORK_COIN_ITEM,
    BORK_COIN_RANGE,
    BORK_ELITE_COIN_RANGE,
    BORK_ELITE_REPEAT_SLAYER_XP,
    BORK_MAGE_DAMAGE_MAXIMUM,
    BORK_MAGE_DAMAGE_MINIMUM,
    BORK_MAGE_DISPLAY_NAME,
    BORK_MAGE_TICKS_PER_ATTACK,
    BORK_MAX_LIFEPOINTS,
    BORK_ORK_SUMMON_MAXIMUM,
    BORK_ORK_SUMMON_MINIMUM,
    BORK_ORK_SUMMON_THRESHOLD_LIFEPOINTS,
    BORK_QUEST_ID,
    BORK_RARE_DROPS,
    BORK_REPEAT_SLAYER_XP,
    BORK_REVIEW_TICKS,
    BORK_RING_OF_WEALTH_ITEM,
    BORK_TARGET_ID,
    BORK_VARROCK_ELITE_TIER_ID,
    BORK_WORLD_DAY_REVIEWS,
    bork_enemy_pure,
    bork_guaranteed_drops_pure,
    ork_legion_enemy_pure,
)
from ..logic_pure.logic_pure import (
    apply_combat_burst_pure,
    apply_thieving_damage_pure,
    combat_enemy_pressure_attack_pure,
    combat_target_locked_reasons_pure,
    prayer_effect_state_pure,
)
from .achievement_diary_logic import diary_tier_by_id_pure, tier_claim_state_pure
from .treasure_trails_logic import (
    clue_refusal_reason_pure,
    filter_clue_scroll_outputs_pure,
)


BORK_STATE_VERSION = 1


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


def _roll(rng) -> float:
    try:
        return float(rng())
    except (TypeError, ValueError, OverflowError):
        return 0.0


def _uniform_int(rng, low: int, high: int) -> int:
    """Inclusive uniform draw, matching Darkan's `Utils.random(low, high + 1)`."""
    return low + min(high - low, int(_roll(rng) * (high - low + 1)))


def _answered_cards(player_data: Mapping[str, Any]) -> int:
    clock = player_data.get("shop_market_clock")
    return _int(clock.get("answered_cards")) if isinstance(clock, Mapping) else 0


def _world_day(player_data: Mapping[str, Any]) -> int:
    return _answered_cards(player_data) // BORK_WORLD_DAY_REVIEWS


def _quest_complete(player_data: Mapping[str, Any]) -> bool:
    quests = player_data.get("quests")
    quest = quests.get(BORK_QUEST_ID) if isinstance(quests, Mapping) else None
    return isinstance(quest, Mapping) and bool(quest.get("completed"))


def varrock_elite_complete_pure(player_data: Mapping[str, Any]) -> bool:
    """Darkan gates the improved payout on the elite tasks, not on claiming."""
    resolved = diary_tier_by_id_pure(BORK_VARROCK_ELITE_TIER_ID)
    if resolved is None:
        return False
    family, tier = resolved
    claim = tier_claim_state_pure(player_data, family, tier)
    return bool(claim["total"]) and claim["done"] >= claim["total"]


def _ring_of_wealth_equipped(player_data: Mapping[str, Any]) -> bool:
    equipment = player_data.get("equipment")
    values = set(equipment.values()) if isinstance(equipment, Mapping) else set()
    return BORK_RING_OF_WEALTH_ITEM in values


def default_bork_state_pure() -> dict[str, Any]:
    return {
        "version": BORK_STATE_VERSION,
        "active": False,
        "lifepoints": 0,
        "ork_count": 0,
        "orks_summoned": False,
        "mage_ticks": 0,
        "encounter": {},
        "previous_combat_target": "",
        "kills": 0,
        "last_completed_world_day": -1,
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
    encounter["target_id"] = BORK_TARGET_ID
    encounter["enemy_lifepoints"] = lifepoints
    return encounter


def sanitize_bork_state_pure(raw: Any) -> dict[str, Any]:
    defaults = default_bork_state_pure()
    source = raw if isinstance(raw, Mapping) else {}
    active = bool(source.get("active", False))
    lifepoints = min(
        BORK_MAX_LIFEPOINTS,
        _int(source.get("lifepoints"), BORK_MAX_LIFEPOINTS),
    )
    if not active or lifepoints <= 0:
        active = False
        lifepoints = 0
    ork_count = min(
        BORK_ORK_SUMMON_MAXIMUM,
        _int(source.get("ork_count")) if active else 0,
    )
    orks_summoned = bool(source.get("orks_summoned", False)) and active
    return {
        **defaults,
        "active": active,
        "lifepoints": lifepoints,
        "ork_count": ork_count,
        "orks_summoned": orks_summoned or ork_count > 0,
        "mage_ticks": min(
            BORK_MAGE_TICKS_PER_ATTACK,
            _int(source.get("mage_ticks")) if active else 0,
        ),
        "encounter": _sanitize_encounter(source.get("encounter"), lifepoints),
        "previous_combat_target": str(source.get("previous_combat_target", ""))[:120],
        "kills": _int(source.get("kills")),
        "last_completed_world_day": max(
            -1,
            _int(source.get("last_completed_world_day"), -1, minimum=-1),
        ),
        "last_result": str(source.get("last_result", ""))[:500],
    }


def bork_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_bork_state_pure(player_data.get("bork"))
    missing = []
    if not _quest_complete(player_data):
        missing.append("Complete The Hunt for Surok")
    current_day = _world_day(player_data)
    daily_ready = current_day > state["last_completed_world_day"]
    varrock_elite = varrock_elite_complete_pure(player_data)
    ring_of_wealth = _ring_of_wealth_equipped(player_data)
    coin_low, coin_high = (
        BORK_ELITE_COIN_RANGE if varrock_elite else BORK_COIN_RANGE
    )
    return {
        **state,
        "requirements_met": not missing,
        "missing_requirements": tuple(missing),
        "daily_ready": daily_ready,
        "reviews_to_reset": (
            0
            if daily_ready
            else BORK_WORLD_DAY_REVIEWS
            - (_answered_cards(player_data) % BORK_WORLD_DAY_REVIEWS)
        ),
        "varrock_elite": varrock_elite,
        "ring_of_wealth": ring_of_wealth,
        "slayer_xp": (
            BORK_ELITE_REPEAT_SLAYER_XP if varrock_elite else BORK_REPEAT_SLAYER_XP
        ),
        "coin_range": (coin_low, coin_high),
        "guaranteed_drops": bork_guaranteed_drops_pure(
            varrock_elite, ring_of_wealth, 0
        ),
        "ork_threshold": BORK_ORK_SUMMON_THRESHOLD_LIFEPOINTS,
    }


def _end_encounter(
    data: dict[str, Any],
    state: dict[str, Any],
    message: str,
) -> None:
    state["active"] = False
    state["lifepoints"] = 0
    state["ork_count"] = 0
    state["orks_summoned"] = False
    state["mage_ticks"] = 0
    state["encounter"] = {}
    state["last_result"] = message[:500]
    data["bork"] = state
    data["activity_session"] = {"active_id": ""}
    data["combat_encounter"] = {}
    data["current_combat_target"] = str(state.get("previous_combat_target", ""))


def apply_bork_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
    *,
    equipment_data: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the encounter state is rebuilt as a deep copy and no
    # other nested value of the input is written.
    data = dict(player_data)
    state = sanitize_bork_state_pure(data.get("bork"))
    data["bork"] = state

    if action_id == "enter":
        if state["active"]:
            data["activity_session"] = {"active_id": BORK_ACTIVITY_ID}
            data["current_utility"] = BORK_ACTIVITY_ID
            return data, True, {"message": "Bork selected for reviews."}
        active_session = data.get("activity_session")
        if isinstance(active_session, Mapping) and active_session.get("active_id"):
            return data, False, {"reason": "Another persistent activity is active."}
        view = bork_view_pure(data)
        if not view["requirements_met"]:
            return data, False, {"reason": "; ".join(view["missing_requirements"]) + "."}
        if not view["daily_ready"]:
            return data, False, {
                "reason": (
                    "Bork has already been defeated this world day; "
                    f"{view['reviews_to_reset']:,} reviews remain."
                )
            }
        previous_target = str(data.get("current_combat_target", ""))[:120]
        encounter = {
            "target_id": BORK_TARGET_ID,
            "enemy_lifepoints": BORK_MAX_LIFEPOINTS,
        }
        state.update(
            {
                "active": True,
                "lifepoints": BORK_MAX_LIFEPOINTS,
                "ork_count": 0,
                "orks_summoned": False,
                "mage_ticks": 0,
                "encounter": encounter,
                "previous_combat_target": previous_target,
                "last_result": (
                    f"Entered Bork's chamber at {BORK_MAX_LIFEPOINTS:,} LP."
                ),
            }
        )
        data["current_combat_target"] = BORK_TARGET_ID
        data["combat_encounter"] = copy.deepcopy(encounter)
        locked = combat_target_locked_reasons_pure(
            data,
            BORK_TARGET_ID,
            {BORK_TARGET_ID: bork_enemy_pure()},
            equipment_data=equipment_data or {},
        )
        if locked:
            return dict(player_data), False, {
                "reason": "Combat loadout is not ready: " + "; ".join(locked)
            }
        data["bork"] = state
        data["activity_session"] = {"active_id": BORK_ACTIVITY_ID}
        data["current_utility"] = BORK_ACTIVITY_ID
        return data, True, {"message": state["last_result"]}

    if action_id == "leave":
        if not state["active"]:
            return data, False, {"reason": "No Bork encounter is active."}
        _end_encounter(
            data,
            state,
            "Left Bork's chamber; the daily kill was not consumed.",
        )
        return data, True, {"message": state["last_result"]}

    return data, False, {"reason": "Unknown Bork command."}


def _apply_ork_pressure(
    data: dict[str, Any],
    ork_count: int,
    equipment_data: Mapping[str, Any],
    rng,
) -> tuple[dict[str, Any], int]:
    damage = 0
    for _ in range(ork_count):
        pressure = combat_enemy_pressure_attack_pure(
            data, ork_legion_enemy_pure(), equipment_data, rng
        )
        damage += _int(pressure.get("damage"))
    return data, damage


def _apply_mage_pressure(
    data: dict[str, Any],
    state: dict[str, Any],
    rng,
) -> int:
    """One 100-250 magic bolt per 33 ticks, answered by Protect from Magic.

    Darkan zeroes the bolt outright while the prayer is on. AnkiScape's prayers
    carry an uptime fraction rather than a boolean, so the bolt takes the
    engine's own protection arithmetic: full uptime is the period's zero.
    """
    state["mage_ticks"] += BORK_REVIEW_TICKS
    if state["mage_ticks"] < BORK_MAGE_TICKS_PER_ATTACK:
        return 0
    state["mage_ticks"] -= BORK_MAGE_TICKS_PER_ATTACK
    rolled = _uniform_int(rng, BORK_MAGE_DAMAGE_MINIMUM, BORK_MAGE_DAMAGE_MAXIMUM)
    protection = _float(prayer_effect_state_pure(data).get("protect_magic"))
    return max(0, int(rolled * (1.0 - protection)))


def _award_drops(data: dict[str, Any], drops: Mapping[str, int]) -> None:
    inventory = dict(data.get("inventory", {}) or {})
    for item_name, amount in drops.items():
        if amount > 0:
            inventory[item_name] = _int(inventory.get(item_name)) + int(amount)
    data["inventory"] = inventory


def apply_bork_review_pure(
    player_data: Mapping[str, Any],
    rng,
    *,
    equipment_data: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the encounter state is rebuilt as a deep copy and the
    # combat helpers copy every nested value they touch.
    data = dict(player_data)
    state = sanitize_bork_state_pure(data.get("bork"))
    if not state["active"]:
        return data, False, {"reason": "Enter Bork's chamber before training."}
    equipment_data = equipment_data or {}

    data["current_combat_target"] = BORK_TARGET_ID
    data["combat_encounter"] = _sanitize_encounter(
        state.get("encounter"), state["lifepoints"]
    )
    data, ok, combat_result = apply_combat_burst_pure(
        data,
        {BORK_TARGET_ID: bork_enemy_pure()},
        equipment_data,
        ticks=BORK_REVIEW_TICKS,
        rng=rng,
        live_cadence=True,
        stop_after_first_kill=True,
        # The Chaos Tunnels are ordinary dangerous world, not a minigame, so
        # the live-Combat death path runs unchanged.
        safe_death=False,
        allow_bank_run=False,
    )
    if not ok:
        return dict(player_data), False, combat_result

    if combat_result.get("died") or combat_result.get("fled"):
        outcome = (
            "Defeated by Bork" if combat_result.get("died") else "Fled Bork's chamber"
        )
        _end_encounter(data, state, outcome + "; the daily kill was not consumed.")
        return data, True, {
            **combat_result,
            "outcome": state["last_result"],
            "status": state["last_result"],
        }

    killed = bool(combat_result.get("killed"))
    if not killed:
        state["lifepoints"] = max(
            1,
            _int(
                combat_result.get("enemy_lifepoints"),
                state["lifepoints"],
                minimum=1,
            ),
        )
        state["encounter"] = _sanitize_encounter(
            data.get("combat_encounter"), state["lifepoints"]
        )

    summoned_now = 0
    if (
        not state["orks_summoned"]
        and not killed
        and state["lifepoints"] <= BORK_ORK_SUMMON_THRESHOLD_LIFEPOINTS
    ):
        summoned_now = _uniform_int(
            rng, BORK_ORK_SUMMON_MINIMUM, BORK_ORK_SUMMON_MAXIMUM
        )
        state["orks_summoned"] = True
        state["ork_count"] = summoned_now

    pressure_damage = 0
    if not killed:
        data, pressure_damage = _apply_ork_pressure(
            data, state["ork_count"], equipment_data, rng
        )
        pressure_damage += _apply_mage_pressure(data, state, rng)
    pressure_result: dict[str, Any] = {"damage": 0, "died": False, "food_used": None}
    if pressure_damage > 0:
        data, pressure_result = apply_thieving_damage_pure(
            data,
            pressure_damage,
            source="bork_pressure",
            carried_target_id=BORK_TARGET_ID,
            safe_death=False,
        )
        if pressure_result.get("died"):
            _end_encounter(
                data,
                state,
                "Defeated by Bork's legion; the daily kill was not consumed.",
            )
            return data, True, {
                **combat_result,
                # The combat burst itself survived, so `combat_result["died"]`
                # is False; the legion is what killed the player, and callers
                # read this one flag for the death.
                "died": True,
                "pressure_damage": int(pressure_result.get("damage", 0) or 0),
                "outcome": state["last_result"],
                "status": state["last_result"],
            }

    if not killed:
        status = (
            f"Bork: {state['lifepoints']:,}/{BORK_MAX_LIFEPOINTS:,} LP"
        )
        if summoned_now:
            status += f" · {summoned_now} orks joined the fight"
        elif state["ork_count"]:
            status += f" · {state['ork_count']} orks attacking"
        if pressure_result.get("damage"):
            status += f" · {int(pressure_result['damage'])} LP incoming"
        state["last_result"] = status[:500]
        data["bork"] = state
        data["activity_session"] = {"active_id": BORK_ACTIVITY_ID}
        return data, True, {
            **combat_result,
            "orks_summoned": summoned_now,
            "ork_count": state["ork_count"],
            "pressure_damage": int(pressure_result.get("damage", 0) or 0),
            "pressure_food_used": pressure_result.get("food_used"),
            "status": state["last_result"],
        }

    view = bork_view_pure(data)
    varrock_elite = bool(view["varrock_elite"])
    ring_of_wealth = bool(view["ring_of_wealth"])
    slayer_xp = (
        BORK_ELITE_REPEAT_SLAYER_XP if varrock_elite else BORK_REPEAT_SLAYER_XP
    )
    data["slayer_exp"] = _float(data.get("slayer_exp")) + slayer_xp
    coin_low, coin_high = (
        BORK_ELITE_COIN_RANGE if varrock_elite else BORK_COIN_RANGE
    )
    coins = _uniform_int(rng, coin_low, coin_high)
    drops = bork_guaranteed_drops_pure(varrock_elite, ring_of_wealth, coins)
    rare_drops = {}
    for item_name, chance in BORK_RARE_DROPS:
        if _roll(rng) < chance:
            rare_drops[item_name] = rare_drops.get(item_name, 0) + 1
    filtered_rare_drops = filter_clue_scroll_outputs_pure(data, rare_drops)
    clue_refusal_reason = clue_refusal_reason_pure(
        data, rare_drops, filtered_rare_drops
    )
    rare_drops = filtered_rare_drops
    _award_drops(data, drops)
    _award_drops(data, rare_drops)
    state["kills"] += 1
    state["last_completed_world_day"] = _world_day(data)
    message = (
        f"Bork defeated · +{int(slayer_xp):,} Slayer XP · "
        f"{coins:,} coins · "
        f"{drops.get('Blue charm', 0)} blue, {drops.get('Crimson charm', 0)} crimson, "
        f"{drops.get('Green charm', 0)} green charms"
    )
    if rare_drops:
        message += " · " + ", ".join(sorted(rare_drops))
    if clue_refusal_reason:
        message += f" · {clue_refusal_reason}"
    _end_encounter(data, state, message)
    return data, True, {
        **combat_result,
        "outcome": message,
        "status": message,
        "slayer_xp": slayer_xp,
        "coins": coins,
        "drops": drops,
        "rare_drops": rare_drops,
        "clue_refusal_reason": clue_refusal_reason,
        "varrock_elite": varrock_elite,
        "ring_of_wealth": ring_of_wealth,
        "xp_rewards": {
            **(combat_result.get("xp_rewards", {}) or {}),
            "slayer_exp": _float(
                (combat_result.get("xp_rewards", {}) or {}).get("slayer_exp")
            )
            + slayer_xp,
        },
    }
