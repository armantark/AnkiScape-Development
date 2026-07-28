"""Pure, persistent TzHaar Fight Cave session mechanics."""

from __future__ import annotations

import copy
from typing import Any, Mapping

from ..data.fight_caves_data import (
    FIGHT_CAVES_ACTIVITY_ID,
    FIGHT_CAVES_CAPE_ITEM,
    FIGHT_CAVES_COMBAT_TARGET_ID,
    FIGHT_CAVES_COMPLETION_TOKKUL,
    FIGHT_CAVES_ENEMY_DATA,
    FIGHT_CAVES_PARTIAL_TOKKUL_BASE,
    FIGHT_CAVES_TOKKUL_ITEM,
    FIGHT_CAVES_WAVE_COUNT,
    FIGHT_CAVES_WAVES,
)
from ..logic_pure.logic_pure import (
    apply_combat_burst_pure,
    apply_thieving_damage_pure,
    combat_enemy_pressure_attack_pure,
    combat_max_lifepoints_pure,
)
from .pet_logic import store_active_pet_pure
from .summoning_logic import dismiss_familiar_pure


FIGHT_CAVES_STATE_VERSION = 1
FIGHT_CAVES_JAD_STYLES = ("ranged", "magic")


def _int(value: Any, default: int = 0, *, minimum: int = 0) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(minimum, parsed)


def _active_follower(player_data: Mapping[str, Any]) -> Mapping[str, Any]:
    state = player_data.get("summoning_state")
    if not isinstance(state, Mapping):
        return {}
    follower = state.get("active_follower")
    return follower if isinstance(follower, Mapping) else {}


def _empty_session() -> dict[str, Any]:
    return {"active_id": ""}


def default_fight_caves_state_pure() -> dict[str, Any]:
    return {
        "version": FIGHT_CAVES_STATE_VERSION,
        "active": False,
        "wave": 1,
        "roster": [],
        "engaged_instance_id": "",
        "next_instance_id": 1,
        "automation_mode": "casual",
        "previous_combat_target": "",
        "total_kills": 0,
        "wave_kills": 0,
        "kill_counts": {},
        "clears": 0,
        "healer_generation": 0,
        "jad_healed_full": False,
        "jad_next_style": "ranged",
        "last_result": "",
    }


def _sanitize_encounter(raw: Any, lifepoints: int) -> dict[str, Any]:
    source = raw if isinstance(raw, Mapping) else {}
    encounter = {
        str(key): copy.deepcopy(value)
        for key, value in source.items()
        if isinstance(key, str)
    }
    encounter["target_id"] = FIGHT_CAVES_COMBAT_TARGET_ID
    encounter["enemy_lifepoints"] = lifepoints
    return encounter


def sanitize_fight_caves_state_pure(raw: Any) -> dict[str, Any]:
    defaults = default_fight_caves_state_pure()
    source = raw if isinstance(raw, Mapping) else {}
    roster = []
    seen = set()
    for raw_member in source.get("roster", ()) or ():
        if not isinstance(raw_member, Mapping):
            continue
        enemy_id = str(raw_member.get("enemy_id", ""))
        spec = FIGHT_CAVES_ENEMY_DATA.get(enemy_id)
        instance_id = str(raw_member.get("instance_id", ""))[:80]
        if spec is None or not instance_id or instance_id in seen:
            continue
        seen.add(instance_id)
        maximum = _int(spec["stats"]["hitpoints"], 1, minimum=1)
        lifepoints = min(
            maximum,
            _int(raw_member.get("lifepoints"), maximum),
        )
        if lifepoints <= 0:
            continue
        roster.append(
            {
                "instance_id": instance_id,
                "enemy_id": enemy_id,
                "lifepoints": lifepoints,
                "encounter": _sanitize_encounter(
                    raw_member.get("encounter"), lifepoints
                ),
                "heal_counter": _int(raw_member.get("heal_counter")),
            }
        )
    wave = min(
        FIGHT_CAVES_WAVE_COUNT,
        _int(source.get("wave"), 1, minimum=1),
    )
    engaged = str(source.get("engaged_instance_id", ""))[:80]
    if engaged not in seen:
        engaged = ""
    mode = str(source.get("automation_mode", "casual"))
    if mode not in {"casual", "advanced"}:
        mode = "casual"
    jad_style = str(source.get("jad_next_style", "ranged"))
    if jad_style not in FIGHT_CAVES_JAD_STYLES:
        jad_style = "ranged"
    raw_kill_counts = source.get("kill_counts")
    ket_zek_kills = (
        _int(raw_kill_counts.get("ket_zek"))
        if isinstance(raw_kill_counts, Mapping)
        else 0
    )
    kill_counts = {"ket_zek": ket_zek_kills} if ket_zek_kills else {}
    return {
        **defaults,
        "active": bool(source.get("active", False)),
        "wave": wave,
        "roster": roster,
        "engaged_instance_id": engaged,
        "next_instance_id": max(
            len(roster) + 1,
            _int(source.get("next_instance_id"), 1, minimum=1),
        ),
        "automation_mode": mode,
        "previous_combat_target": str(
            source.get("previous_combat_target", "")
        )[:120],
        "total_kills": _int(source.get("total_kills")),
        "wave_kills": _int(source.get("wave_kills")),
        "kill_counts": kill_counts,
        "clears": _int(source.get("clears")),
        "healer_generation": min(2, _int(source.get("healer_generation"))),
        "jad_healed_full": bool(source.get("jad_healed_full", False)),
        "jad_next_style": jad_style,
        "last_result": str(source.get("last_result", ""))[:500],
    }


def _new_member(state: dict[str, Any], enemy_id: str) -> dict[str, Any]:
    instance_id = f"fight-caves-{state['next_instance_id']}"
    state["next_instance_id"] += 1
    lifepoints = _int(
        FIGHT_CAVES_ENEMY_DATA[enemy_id]["stats"]["hitpoints"], 1, minimum=1
    )
    return {
        "instance_id": instance_id,
        "enemy_id": enemy_id,
        "lifepoints": lifepoints,
        "encounter": _sanitize_encounter({}, lifepoints),
        "heal_counter": 0,
    }


def _spawn_wave(state: dict[str, Any]) -> None:
    state["roster"] = [
        _new_member(state, enemy_id)
        for enemy_id in FIGHT_CAVES_WAVES[state["wave"] - 1]
    ]
    state["engaged_instance_id"] = ""
    state["wave_kills"] = 0
    state["healer_generation"] = 0
    state["jad_healed_full"] = False
    state["jad_next_style"] = "ranged"


def _member_by_id(
    state: Mapping[str, Any], instance_id: str
) -> dict[str, Any] | None:
    return next(
        (
            member
            for member in state.get("roster", ())
            if member.get("instance_id") == instance_id
        ),
        None,
    )


def _casual_member(state: Mapping[str, Any]) -> dict[str, Any] | None:
    roster = list(state.get("roster", ()) or ())
    if not roster:
        return None
    return min(
        roster,
        key=lambda member: (
            _int(FIGHT_CAVES_ENEMY_DATA[member["enemy_id"]].get("priority"), 99),
            str(member["instance_id"]),
        ),
    )


def _engaged_member(state: dict[str, Any]) -> dict[str, Any] | None:
    selected = _member_by_id(state, state["engaged_instance_id"])
    if state["automation_mode"] == "advanced" and selected is not None:
        return selected
    selected = _casual_member(state)
    if selected is not None:
        state["engaged_instance_id"] = selected["instance_id"]
    return selected


def fight_caves_partial_tokkul_pure(wave: Any) -> int:
    current = min(FIGHT_CAVES_WAVE_COUNT, _int(wave, 1, minimum=1))
    if current <= 1:
        return 0
    return current * FIGHT_CAVES_PARTIAL_TOKKUL_BASE // FIGHT_CAVES_WAVE_COUNT


def fight_caves_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_fight_caves_state_pure(player_data.get("fight_caves"))
    if state["active"] and not state["roster"]:
        _spawn_wave(state)
    display_state = copy.deepcopy(state)
    display_engaged = _engaged_member(display_state)
    display_engaged_id = (
        str(display_engaged["instance_id"]) if display_engaged is not None else ""
    )
    follower = _active_follower(player_data)
    return {
        **state,
        "follower_active": bool(follower),
        "follower_kind": str(follower.get("kind", "")),
        "partial_tokkul": fight_caves_partial_tokkul_pure(state["wave"]),
        "roster_view": tuple(
            {
                "instance_id": member["instance_id"],
                "enemy_id": member["enemy_id"],
                "display_name": FIGHT_CAVES_ENEMY_DATA[member["enemy_id"]][
                    "display_name"
                ],
                "lifepoints": member["lifepoints"],
                "max_lifepoints": FIGHT_CAVES_ENEMY_DATA[member["enemy_id"]][
                    "stats"
                ]["hitpoints"],
                "attack_style": (
                    state["jad_next_style"]
                    if member["enemy_id"] == "tztok_jad"
                    else FIGHT_CAVES_ENEMY_DATA[member["enemy_id"]]["attack_style"]
                ),
                "engaged": member["instance_id"] == display_engaged_id,
            }
            for member in state["roster"]
        ),
    }


def _dismiss_follower(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, str]:
    follower = _active_follower(player_data)
    kind = str(follower.get("kind", ""))
    if not kind:
        # Shallow on purpose: nothing was dismissed, and the only caller writes
        # top-level keys on the result and rebuilds every nested value it stores.
        return dict(player_data), True, ""
    if kind == "familiar":
        updated, ok, _info = dismiss_familiar_pure(player_data)
        return updated, ok, kind
    if kind == "pet":
        updated, ok = store_active_pet_pure(player_data, location="bank")
        return updated, ok, kind
    # Shallow on purpose: the failure is passed straight to the caller's
    # rollback, which discards this save without writing into it.
    return dict(player_data), False, kind


def _award_inventory(data: dict[str, Any], item_name: str, amount: int) -> None:
    if amount <= 0:
        return
    inventory = dict(data.get("inventory", {}) or {})
    inventory[item_name] = _int(inventory.get(item_name)) + amount
    data["inventory"] = inventory


def _end_session(
    data: dict[str, Any],
    state: dict[str, Any],
    *,
    outcome: str,
    tokkul: int,
    fire_cape: bool = False,
) -> dict[str, Any]:
    _award_inventory(data, FIGHT_CAVES_TOKKUL_ITEM, tokkul)
    if fire_cape:
        _award_inventory(data, FIGHT_CAVES_CAPE_ITEM, 1)
        state["clears"] += 1
    state["active"] = False
    state["roster"] = []
    state["engaged_instance_id"] = ""
    state["last_result"] = outcome[:500]
    data["fight_caves"] = state
    data["activity_session"] = _empty_session()
    data["combat_encounter"] = {}
    previous = state.get("previous_combat_target")
    if previous:
        data["current_combat_target"] = previous
    return {
        "outcome": outcome,
        "tokkul": tokkul,
        "fire_cape": fire_cape,
        "wave": state["wave"],
    }


def apply_fight_caves_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the run state and its encounter are rebuilt as deep
    # copies, and the follower alias this module reads is never written.
    data = dict(player_data)
    state = sanitize_fight_caves_state_pure(data.get("fight_caves"))
    data["fight_caves"] = state
    payload = payload if isinstance(payload, Mapping) else {}

    if action_id == "enter":
        if state["active"]:
            data["activity_session"] = {"active_id": FIGHT_CAVES_ACTIVITY_ID}
            return data, True, {"message": f"Resumed Fight Cave wave {state['wave']}."}
        active_session = data.get("activity_session")
        if isinstance(active_session, Mapping) and active_session.get("active_id"):
            return data, False, {"reason": "Another persistent activity is active."}
        encounter = data.get("combat_encounter")
        if isinstance(encounter, Mapping) and encounter:
            return data, False, {"reason": "Finish or leave the current Combat encounter first."}
        follower = _active_follower(data)
        if follower and not bool(payload.get("confirm_dismiss_follower", False)):
            return data, False, {
                "reason": "Your active follower must be dismissed before entering.",
                "requires_confirmation": True,
                "follower_kind": str(follower.get("kind", "follower")),
            }
        if follower:
            data, ok, kind = _dismiss_follower(data)
            if not ok:
                # Shallow rollback: no nested value of the input was written,
                # and _apply_fight_caves_command reads only the reason when the
                # command fails, so the returned save is never stored.
                return dict(player_data), False, {
                    "reason": "The active follower could not be dismissed safely."
                }
            state = sanitize_fight_caves_state_pure(data.get("fight_caves"))
        else:
            kind = ""
        state["active"] = True
        state["wave"] = 1
        state["previous_combat_target"] = str(
            data.get("current_combat_target", "")
        )[:120]
        _spawn_wave(state)
        state["last_result"] = "Entered the Fight Cave. Wave 1 is ready."
        data["fight_caves"] = state
        data["activity_session"] = {"active_id": FIGHT_CAVES_ACTIVITY_ID}
        data["current_utility"] = FIGHT_CAVES_ACTIVITY_ID
        return data, True, {
            "message": state["last_result"],
            "dismissed_follower": kind,
        }

    if action_id == "leave":
        if not state["active"]:
            return data, False, {"reason": "No Fight Cave session is active."}
        reward = fight_caves_partial_tokkul_pure(state["wave"])
        result = _end_session(
            data,
            state,
            outcome=f"Left the Fight Cave on wave {state['wave']}.",
            tokkul=reward,
        )
        return data, True, {"message": result["outcome"], **result}

    if action_id == "set_mode":
        mode = str(payload.get("automation_mode", ""))
        if mode not in {"casual", "advanced"}:
            return data, False, {"reason": "Unknown Fight Cave automation mode."}
        state["automation_mode"] = mode
        data["fight_caves"] = state
        return data, True, {"message": f"Fight Cave mode set to {mode}."}

    if action_id == "select_target":
        instance_id = str(payload.get("instance_id", ""))
        if _member_by_id(state, instance_id) is None:
            return data, False, {"reason": "That Fight Cave target is no longer present."}
        state["engaged_instance_id"] = instance_id
        data["fight_caves"] = state
        return data, True, {"message": "Engaged target updated."}

    return data, False, {"reason": "Unknown Fight Cave command."}


def _spawn_jad_healers(state: dict[str, Any]) -> bool:
    jad = next(
        (member for member in state["roster"] if member["enemy_id"] == "tztok_jad"),
        None,
    )
    if jad is None:
        return False
    maximum = FIGHT_CAVES_ENEMY_DATA["tztok_jad"]["stats"]["hitpoints"]
    healers_alive = any(
        member["enemy_id"] == "yt_hurkot" for member in state["roster"]
    )
    can_spawn = (
        jad["lifepoints"] <= maximum // 2
        and not healers_alive
        and (
            state["healer_generation"] == 0
            or (state["healer_generation"] == 1 and state["jad_healed_full"])
        )
    )
    if not can_spawn:
        return False
    state["roster"].extend(_new_member(state, "yt_hurkot") for _ in range(4))
    state["healer_generation"] += 1
    return True


def _apply_roster_healing(state: dict[str, Any]) -> int:
    healed = 0
    jad = next(
        (member for member in state["roster"] if member["enemy_id"] == "tztok_jad"),
        None,
    )
    healers = [
        member for member in state["roster"] if member["enemy_id"] == "yt_hurkot"
    ]
    if jad is not None and healers:
        maximum = FIGHT_CAVES_ENEMY_DATA["tztok_jad"]["stats"]["hitpoints"]
        for _healer in healers:
            amount = min(100, maximum - jad["lifepoints"])
            jad["lifepoints"] += amount
            healed += amount
        jad["encounter"]["enemy_lifepoints"] = jad["lifepoints"]
        if jad["lifepoints"] >= maximum:
            state["jad_healed_full"] = True

    for healer in state["roster"]:
        if healer["enemy_id"] != "yt_mejkot":
            continue
        healer["heal_counter"] += 1
        if healer["heal_counter"] % 2:
            continue
        injured = [
            member
            for member in state["roster"]
            if member["lifepoints"]
            < FIGHT_CAVES_ENEMY_DATA[member["enemy_id"]]["stats"]["hitpoints"]
        ]
        if not injured:
            continue
        target = min(injured, key=lambda member: member["lifepoints"])
        maximum = FIGHT_CAVES_ENEMY_DATA[target["enemy_id"]]["stats"]["hitpoints"]
        amount = min(100, maximum - target["lifepoints"])
        target["lifepoints"] += amount
        target["encounter"]["enemy_lifepoints"] = target["lifepoints"]
        healed += amount
    return healed


def apply_fight_caves_review_pure(
    player_data: Mapping[str, Any],
    rng,
    *,
    equipment_data=None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the run state and its encounter are rebuilt as deep
    # copies, and the follower alias this module reads is never written.
    data = dict(player_data)
    state = sanitize_fight_caves_state_pure(data.get("fight_caves"))
    if not state["active"]:
        return data, False, {"reason": "Enter the Fight Cave before training it."}
    if not state["roster"]:
        _spawn_wave(state)
    data["fight_caves"] = state
    existing_ids = {member["instance_id"] for member in state["roster"]}
    roster_healing = _apply_roster_healing(state)
    engaged = _engaged_member(state)
    if engaged is None:
        return data, False, {"reason": "The current Fight Cave wave has no target."}

    enemy_id = engaged["enemy_id"]
    enemy = copy.deepcopy(FIGHT_CAVES_ENEMY_DATA[enemy_id])
    if enemy_id == "tztok_jad":
        enemy["attack_style"] = state["jad_next_style"]
        enemy["max_hit"] = 970
    data["current_combat_target"] = FIGHT_CAVES_COMBAT_TARGET_ID
    data["combat_encounter"] = _sanitize_encounter(
        engaged.get("encounter"), engaged["lifepoints"]
    )
    # The bounded encounter cannot be left mid-fight, so the engine's
    # auto-flee is suspended for the burst and restored after — the engine
    # reads the boolean combat_auto_flee, not the old percent key, which
    # this family zeroed for months without effect.
    auto_flee = data.get("combat_auto_flee", True)
    data["combat_auto_flee"] = False
    data, ok, combat_result = apply_combat_burst_pure(
        data,
        {FIGHT_CAVES_COMBAT_TARGET_ID: enemy},
        equipment_data or {},
        ticks=6,
        rng=rng,
        live_cadence=True,
        stop_after_first_kill=True,
        safe_death=True,
        allow_bank_run=False,
    )
    data["combat_auto_flee"] = auto_flee
    if not ok:
        # Shallow rollback: apply_combat_burst_pure copies nested values before
        # touching them, so nothing of the input was written, and
        # _handle_fight_caves_answer reads only the result when ok is False.
        return dict(player_data), False, combat_result

    engaged_died = bool(combat_result.get("killed"))
    player_died = bool(combat_result.get("died"))
    split_members: list[dict[str, Any]] = []
    if engaged_died:
        state["roster"] = [
            member
            for member in state["roster"]
            if member["instance_id"] != engaged["instance_id"]
        ]
        state["total_kills"] += 1
        state["wave_kills"] += 1
        if enemy_id == "ket_zek":
            kill_counts = dict(state.get("kill_counts", {}) or {})
            kill_counts[enemy_id] = _int(kill_counts.get(enemy_id)) + 1
            state["kill_counts"] = kill_counts
        for split_id in enemy.get("splits_into", ()) or ():
            split_members.append(_new_member(state, str(split_id)))
        state["roster"].extend(split_members)
        data["combat_encounter"] = {}
    else:
        engaged["lifepoints"] = max(
            1, _int(combat_result.get("enemy_lifepoints"), engaged["lifepoints"], minimum=1)
        )
        engaged["encounter"] = _sanitize_encounter(
            data.get("combat_encounter"), engaged["lifepoints"]
        )

    if enemy_id == "tztok_jad" and engaged_died:
        result = _end_session(
            data,
            state,
            outcome="Defeated TzTok-Jad and completed the Fight Cave.",
            tokkul=FIGHT_CAVES_COMPLETION_TOKKUL,
            fire_cape=True,
        )
        return data, True, {
            **combat_result,
            **result,
            "status": (
                "Fight Cave complete · +16,064 TokKul · +1 Fire cape"
            ),
            "roster_healing": roster_healing,
        }

    if player_died:
        reward = fight_caves_partial_tokkul_pure(state["wave"])
        result = _end_session(
            data,
            state,
            outcome=f"Defeated safely in Fight Cave wave {state['wave']}.",
            tokkul=reward,
        )
        return data, True, {
            **combat_result,
            **result,
            "status": f"Safe defeat on wave {state['wave']} · +{reward:,} TokKul",
            "roster_healing": roster_healing,
        }

    healers_spawned = _spawn_jad_healers(state)
    pressure_damage = 0
    pressure_styles: list[str] = []
    pressure_prayer_drain = 0
    for member in list(state["roster"]):
        if (
            member["instance_id"] == engaged["instance_id"]
            or member["instance_id"] not in existing_ids
        ):
            continue
        pressure_enemy = copy.deepcopy(FIGHT_CAVES_ENEMY_DATA[member["enemy_id"]])
        if member["enemy_id"] == "tztok_jad":
            pressure_enemy["attack_style"] = state["jad_next_style"]
            pressure_enemy["max_hit"] = 970
        pressure = combat_enemy_pressure_attack_pure(
            data, pressure_enemy, equipment_data or {}, rng
        )
        pressure_damage += _int(pressure.get("damage"))
        pressure_styles.append(str(pressure.get("attack_style", "melee")))
        base_drain = _int(pressure_enemy.get("prayer_drain_base"))
        if base_drain:
            drain = base_drain
            if pressure_enemy.get("prayer_drain_damage"):
                drain += _int(pressure.get("raw_damage"))
            available = _int(data.get("combat_prayer_points"))
            applied = min(available, drain)
            data["combat_prayer_points"] = available - applied
            pressure_prayer_drain += applied
    pressure_result = {"damage": 0, "died": False, "food_used": None}
    if pressure_damage > 0:
        data, pressure_result = apply_thieving_damage_pure(
            data,
            pressure_damage,
            source="fight_caves_pressure",
            carried_target_id=FIGHT_CAVES_COMBAT_TARGET_ID,
            safe_death=True,
        )
    if _int(data.get("combat_prayer_points")) <= 0:
        data["combat_selected_prayers"] = []

    if pressure_result.get("died"):
        reward = fight_caves_partial_tokkul_pure(state["wave"])
        result = _end_session(
            data,
            state,
            outcome=f"Defeated safely in Fight Cave wave {state['wave']}.",
            tokkul=reward,
        )
        return data, True, {
            **combat_result,
            **result,
            "pressure_damage": pressure_result["damage"],
            "status": f"Safe defeat on wave {state['wave']} · +{reward:,} TokKul",
            "roster_healing": roster_healing,
        }

    wave_completed = not state["roster"]
    if wave_completed:
        state["wave"] += 1
        _spawn_wave(state)
        data["combat_encounter"] = {}
    if enemy_id == "tztok_jad" and not engaged_died:
        try:
            state["jad_next_style"] = (
                "magic" if float(rng()) < 0.5 else "ranged"
            )
        except (TypeError, ValueError):
            state["jad_next_style"] = "ranged"

    engaged_name = enemy["display_name"]
    status = (
        f"Wave {state['wave'] - 1} complete · wave {state['wave']} ready"
        if wave_completed
        else f"Wave {state['wave']} · {engaged_name}: {engaged.get('lifepoints', 0)} LP"
    )
    if pressure_result.get("damage"):
        status += f" · roster pressure {int(pressure_result['damage'])} LP"
    if healers_spawned:
        status += " · four Yt-HurKot joined Jad"
    if enemy_id == "tztok_jad":
        status += f" · next Jad attack: {state['jad_next_style']}"
    state["last_result"] = status[:500]
    data["fight_caves"] = state
    data["activity_session"] = {"active_id": FIGHT_CAVES_ACTIVITY_ID}
    return data, True, {
        **combat_result,
        "wave": state["wave"],
        "wave_completed": wave_completed,
        "engaged_enemy_id": enemy_id,
        "engaged_instance_id": engaged["instance_id"],
        "split_count": len(split_members),
        "roster_healing": roster_healing,
        "healers_spawned": healers_spawned,
        "pressure_damage": int(pressure_result.get("damage", 0) or 0),
        "pressure_styles": tuple(pressure_styles),
        "pressure_prayer_drain": pressure_prayer_drain,
        "pressure_food_used": pressure_result.get("food_used"),
        "status": state["last_result"],
        "jad_next_style": state["jad_next_style"],
    }
