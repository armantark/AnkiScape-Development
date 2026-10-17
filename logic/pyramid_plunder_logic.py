"""Pure Pyramid Plunder entry, room, hazard, inventory, and exit mechanics."""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from typing import Any

from ..data.combat_data import COMBAT_ANTIPOISON_POTION_DATA, COMBAT_FOOD_DATA
from .inventory_pure import (
    CARRIED_CAPACITY,
    apply_carried_layout_pure,
    carried_has_room_for,
    carried_slots_used,
)
from ..logic_pure.logic_pure import (
    apply_combat_poison_effect_pure,
    apply_thieving_damage_pure,
    combat_poison_immunity_ticks_pure,
)
from ..data.pyramid_plunder_data import (
    PYRAMID_PLUNDER_ACTIVITY_ID,
    PYRAMID_PLUNDER_ARTIFACT_TIERS,
    PYRAMID_PLUNDER_ARTIFACT_VALUES,
    PYRAMID_PLUNDER_AUTO_FOOD_SLOTS,
    PYRAMID_PLUNDER_BLACK_IBIS,
    PYRAMID_PLUNDER_ENGRAVED_TIER_WEIGHTS,
    PYRAMID_PLUNDER_FALLBACKS,
    PYRAMID_PLUNDER_PHARAOH_SCEPTRES,
    PYRAMID_PLUNDER_PRIORITIES,
    PYRAMID_PLUNDER_ROOM_DATA,
    PYRAMID_PLUNDER_SARC_TIER_WEIGHTS,
    PYRAMID_PLUNDER_URN_TIER_WEIGHTS,
)


PYRAMID_PLUNDER_STATE_VERSION = 1


def _int(value: Any, default: int = 0, *, maximum: int = 2_147_483_647) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(0, min(parsed, maximum))


def _float(value: Any, default: float = 0.0, *, maximum: float = 1e15) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    if not math.isfinite(parsed):
        parsed = default
    return max(0.0, min(parsed, maximum))


def _roll(rng: Callable[[], float]) -> float:
    try:
        value = float(rng())
    except (TypeError, ValueError, OverflowError):
        return 0.5
    if not math.isfinite(value):
        return 0.5
    return max(0.0, min(value, 0.999999999))


def _stackable_names() -> frozenset[str]:
    from ..core.constants import ITEM_DEFINITIONS
    # Food, potion doses, and Pyramid Plunder rewards always consume one slot
    # per item even when an older generic registry row omitted stackability.
    forced_unstackable = {
        *COMBAT_FOOD_DATA,
        *COMBAT_ANTIPOISON_POTION_DATA,
        *PYRAMID_PLUNDER_ARTIFACT_VALUES,
        *PYRAMID_PLUNDER_BLACK_IBIS,
        *PYRAMID_PLUNDER_PHARAOH_SCEPTRES,
        "Sceptre of the gods",
        "Vial",
    }
    return frozenset(
        item.storage_key
        for item in ITEM_DEFINITIONS
        if item.stackable and item.storage_key not in forced_unstackable
    )


def default_pyramid_plunder_state_pure() -> dict[str, Any]:
    return {
        "pyramid_plunder": {},
        "pyramid_plunder_priority": "max_xp",
        "pyramid_plunder_runs_completed": 0,
        "pyramid_plunder_last_result": "Ready to enter",
    }


def sanitize_pyramid_plunder_session_pure(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}
    priority = str(raw.get("priority", "max_xp"))
    if priority not in PYRAMID_PLUNDER_PRIORITIES:
        priority = "max_xp"
    max_room = min(8, max(1, _int(raw.get("max_room"), 1)))
    room = min(max_room, max(1, _int(raw.get("room"), 1)))
    raw_xp = raw.get("xp") if isinstance(raw.get("xp"), Mapping) else {}
    raw_haul = raw.get("haul") if isinstance(raw.get("haul"), Mapping) else {}
    return {
        "version": PYRAMID_PLUNDER_STATE_VERSION,
        "room": room,
        "max_room": max_room,
        "priority": priority,
        "xp": {
            skill: _float(raw_xp.get(skill))
            for skill in ("thieving", "strength", "runecrafting")
        },
        "haul": {
            str(item): _int(amount)
            for item, amount in raw_haul.items()
            if isinstance(item, str) and _int(amount) > 0
        },
    }


def sanitize_pyramid_plunder_state_pure(player_data: Mapping[str, Any] | None) -> dict[str, Any]:
    source = dict(player_data or {})
    defaults = default_pyramid_plunder_state_pure()
    priority = str(source.get("pyramid_plunder_priority", defaults["pyramid_plunder_priority"]))
    if priority not in PYRAMID_PLUNDER_PRIORITIES:
        priority = "max_xp"
    session = sanitize_pyramid_plunder_session_pure(source.get("pyramid_plunder"))
    active_session = source.get("activity_session")
    active_id = str(active_session.get("active_id", "")) if isinstance(active_session, Mapping) else ""
    if session and active_id not in {"", PYRAMID_PLUNDER_ACTIVITY_ID}:
        session = {}
    state = {
        "pyramid_plunder": session,
        "pyramid_plunder_priority": priority,
        "pyramid_plunder_runs_completed": _int(source.get("pyramid_plunder_runs_completed")),
        "pyramid_plunder_last_result": str(
            source.get("pyramid_plunder_last_result", defaults["pyramid_plunder_last_result"])
            or defaults["pyramid_plunder_last_result"]
        )[:320],
    }
    carried = source.get("carried_inventory")
    if session and isinstance(carried, Mapping):
        raw_pack = carried.get(PYRAMID_PLUNDER_ACTIVITY_ID, {})
        if carried_slots_used(raw_pack, _stackable_names()) > CARRIED_CAPACITY:
            state["carried_inventory"] = dict(carried)
            _write_carried_view(state, _carried_view(source))
    return state


def _owns_item(player_data: Mapping[str, Any], item_name: str) -> bool:
    inventory = player_data.get("inventory")
    if isinstance(inventory, Mapping) and _int(inventory.get(item_name)) > 0:
        return True
    equipment = player_data.get("equipment")
    if isinstance(equipment, Mapping) and item_name in equipment.values():
        return True
    for key in ("combat_grave", "death_office"):
        state = player_data.get(key)
        if isinstance(state, Mapping) and item_name in (state.get("items") or ()):
            return True
    return False


def _has_sceptre_access(player_data: Mapping[str, Any]) -> bool:
    access_items = (*PYRAMID_PLUNDER_PHARAOH_SCEPTRES, "Sceptre of the gods")
    return any(_owns_item(player_data, item) for item in access_items)


def pyramid_plunder_locked_reasons_pure(player_data: Mapping[str, Any]) -> tuple[str, ...]:
    reasons: list[str] = []
    if _int(player_data.get("thieving_level"), 1) < 21:
        reasons.append("Thieving level 21")
    quests = player_data.get("quests")
    quest = quests.get("icthlarins_little_helper") if isinstance(quests, Mapping) else None
    quest_started = isinstance(quest, Mapping) and bool(quest.get("started") or quest.get("completed"))
    if not quest_started and not _has_sceptre_access(player_data):
        reasons.append("start Icthlarin's Little Helper or own a charged sceptre")
    return tuple(reasons)


def _maximum_room(thieving_level: Any) -> int:
    level = _int(thieving_level, 1)
    return max(room for room, spec in PYRAMID_PLUNDER_ROOM_DATA.items() if int(spec["level"]) <= level)


def _auto_pack_layout(player_data: Mapping[str, Any]) -> dict[str, int]:
    inventory = player_data.get("inventory") if isinstance(player_data.get("inventory"), Mapping) else {}
    layout: dict[str, int] = {}
    remaining_food = PYRAMID_PLUNDER_AUTO_FOOD_SLOTS
    for item_name in sorted(
        COMBAT_FOOD_DATA,
        key=lambda name: int(COMBAT_FOOD_DATA[name].get("heal_lifepoints", 0)),
        reverse=True,
    ):
        amount = min(remaining_food, _int(inventory.get(item_name)))
        if amount > 0:
            layout[item_name] = amount
            remaining_food -= amount
        if remaining_food <= 0:
            break
    antipoisons = sorted(
        COMBAT_ANTIPOISON_POTION_DATA,
        key=lambda name: (
            int(COMBAT_ANTIPOISON_POTION_DATA[name].get("immunity_ticks", 0)),
            int(name.rsplit("(", 1)[-1].rstrip(")")) if name.endswith(")") else 0,
        ),
        reverse=True,
    )
    for item_name in antipoisons:
        if _int(inventory.get(item_name)) > 0:
            layout[item_name] = 1
            break
    return layout


def _prepare_pack(player_data: Mapping[str, Any]) -> dict[str, int]:
    advanced = player_data.get("carried_advanced_targets")
    custom = isinstance(advanced, Mapping) and bool(advanced.get(PYRAMID_PLUNDER_ACTIVITY_ID))
    layouts = player_data.get("carried_layout")
    layout = (
        layouts.get(PYRAMID_PLUNDER_ACTIVITY_ID, {})
        if custom and isinstance(layouts, Mapping)
        else _auto_pack_layout(player_data)
    )
    layout = dict(layout) if isinstance(layout, Mapping) else {}
    layout.pop("Coins", None)
    return apply_carried_layout_pure(
        player_data.get("inventory", {}) if isinstance(player_data.get("inventory"), Mapping) else {},
        layout,
        CARRIED_CAPACITY,
        _stackable_names(),
    )


def enter_pyramid_plunder_pure(player_data: Mapping[str, Any]) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the plunder state and session are rebuilt fresh, and
    # the carried pack layout is rebuilt before it is edited.
    data = dict(player_data)
    state = sanitize_pyramid_plunder_state_pure(data)
    if state["pyramid_plunder"]:
        return data, False, {"reason": "A Pyramid Plunder run is already active."}
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if active_id and active_id != PYRAMID_PLUNDER_ACTIVITY_ID:
        return data, False, {"reason": "Finish the active persistent activity first."}
    locked = pyramid_plunder_locked_reasons_pure(data)
    if locked:
        return data, False, {"reason": ", ".join(locked), "locked_reasons": locked}
    priority = state["pyramid_plunder_priority"]
    max_room = _maximum_room(data.get("thieving_level", 1))
    data.update(state)
    data["pyramid_plunder"] = {
        "version": PYRAMID_PLUNDER_STATE_VERSION,
        "room": 1,
        "max_room": max_room,
        "priority": priority,
        "xp": {"thieving": 0.0, "strength": 0.0, "runecrafting": 0.0},
        "haul": {},
    }
    carried = dict(data.get("carried_inventory") or {})
    carried[PYRAMID_PLUNDER_ACTIVITY_ID] = _prepare_pack(data)
    data["carried_inventory"] = carried
    data["activity_session"] = {"active_id": PYRAMID_PLUNDER_ACTIVITY_ID}
    data["current_utility"] = PYRAMID_PLUNDER_ACTIVITY_ID
    data["pyramid_plunder_last_result"] = (
        f"Entered Pyramid Plunder · {PYRAMID_PLUNDER_PRIORITIES[priority]} · rooms 1-{max_room}"
    )
    return data, True, {
        "message": data["pyramid_plunder_last_result"],
        "max_room": max_room,
        "pack": dict(carried[PYRAMID_PLUNDER_ACTIVITY_ID]),
    }


def set_pyramid_plunder_priority_pure(
    player_data: Mapping[str, Any], priority: Any
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the plunder state and session are rebuilt fresh, and
    # the carried pack layout is rebuilt before it is edited.
    data = dict(player_data)
    if sanitize_pyramid_plunder_session_pure(data.get("pyramid_plunder")):
        return data, False, {"reason": "Finish the active run before changing priority."}
    selected = str(priority)
    if selected not in PYRAMID_PLUNDER_PRIORITIES:
        return data, False, {"reason": "Choose a Pyramid Plunder priority."}
    data["pyramid_plunder_priority"] = selected
    data["pyramid_plunder_last_result"] = f"Priority set · {PYRAMID_PLUNDER_PRIORITIES[selected]}"
    return data, True, {"message": data["pyramid_plunder_last_result"]}


def _weighted_choice(rows: tuple[tuple[str, int], ...], rng: Callable[[], float]) -> str:
    total = sum(weight for _name, weight in rows)
    cursor = int(_roll(rng) * total)
    for name, weight in rows:
        if cursor < weight:
            return name
        cursor -= weight
    return rows[-1][0]


def _ordinary_loot(rows: tuple[tuple[str, int], ...], rng: Callable[[], float]) -> str:
    tier = _weighted_choice(rows, rng)
    if tier == "jewelled_gold":
        return "Jewelled golden statuette"
    if tier == "jewelled_diamond":
        return "Jewelled diamond statuette"
    return PYRAMID_PLUNDER_ARTIFACT_TIERS[tier][
        int(_roll(rng) * len(PYRAMID_PLUNDER_ARTIFACT_TIERS[tier]))
    ]


def _retains(priority: str, item_name: str) -> bool:
    if priority == "treasure":
        return True
    if priority == "balanced":
        return PYRAMID_PLUNDER_ARTIFACT_VALUES[item_name] >= 750
    return False


def _carried_view(data: Mapping[str, Any]) -> dict[str, int]:
    carried = data.get("carried_inventory")
    raw = carried.get(PYRAMID_PLUNDER_ACTIVITY_ID, {}) if isinstance(carried, Mapping) else {}
    return apply_carried_layout_pure(
        data.get("inventory", {}), raw, CARRIED_CAPACITY, _stackable_names(),
    )


def _write_carried_view(data: dict[str, Any], view: Mapping[str, int]) -> None:
    carried = dict(data.get("carried_inventory") or {})
    clean = {str(item): _int(amount) for item, amount in view.items() if _int(amount) > 0}
    if clean:
        carried[PYRAMID_PLUNDER_ACTIVITY_ID] = clean
    else:
        carried.pop(PYRAMID_PLUNDER_ACTIVITY_ID, None)
    data["carried_inventory"] = carried


def _bank_protected(data: dict[str, Any], item_name: str) -> None:
    inventory = dict(data.get("inventory") or {})
    inventory[item_name] = _int(inventory.get(item_name)) + 1
    data["inventory"] = inventory


def _retain_ordinary(data: dict[str, Any], session: dict[str, Any], item_name: str) -> bool:
    view = _carried_view(data)
    stackables = _stackable_names()
    if not carried_has_room_for(view, item_name, 1, stackables):
        return False
    inventory = dict(data.get("inventory") or {})
    inventory[item_name] = _int(inventory.get(item_name)) + 1
    data["inventory"] = inventory
    view[item_name] = _int(view.get(item_name)) + 1
    _write_carried_view(data, view)
    haul = dict(session.get("haul") or {})
    haul[item_name] = _int(haul.get(item_name)) + 1
    session["haul"] = haul
    return carried_slots_used(view, stackables) < CARRIED_CAPACITY


def _next_ibis_piece(data: Mapping[str, Any]) -> str:
    return next((piece for piece in PYRAMID_PLUNDER_BLACK_IBIS if not _owns_item(data, piece)), "")


def _rare_denominator(data: Mapping[str, Any], base: int) -> int:
    equipment = data.get("equipment")
    values = set(equipment.values()) if isinstance(equipment, Mapping) else set()
    return max(1, int(base * (0.97 if "Ring of wealth" in values else 1.0)))


def _roll_black_ibis(data: dict[str, Any], rng: Callable[[], float]) -> str:
    piece = _next_ibis_piece(data)
    if not piece:
        return ""
    equipment = data.get("equipment")
    values = set(equipment.values()) if isinstance(equipment, Mapping) else set()
    denominator = 1150 if "Sceptre of the gods" in values else 2300
    if _roll(rng) >= 1.0 / _rare_denominator(data, denominator):
        return ""
    _bank_protected(data, piece)
    return piece


def _consume_carried_antipoison(data: dict[str, Any]) -> str:
    effects = data.get("combat_status_effects")
    if not isinstance(effects, Mapping) or "poison" not in effects:
        return ""
    view = _carried_view(data)
    for item_name in tuple(view):
        spec = COMBAT_ANTIPOISON_POTION_DATA.get(item_name)
        if spec is None or _int(view.get(item_name)) <= 0:
            continue
        inventory = dict(data.get("inventory") or {})
        inventory[item_name] = max(0, _int(inventory.get(item_name)) - 1)
        view[item_name] = max(0, _int(view.get(item_name)) - 1)
        if view[item_name] <= 0:
            view.pop(item_name, None)
        replacement = str(spec.get("replacement", ""))
        if replacement:
            inventory[replacement] = _int(inventory.get(replacement)) + 1
            view[replacement] = _int(view.get(replacement)) + 1
        clean_effects = dict(effects)
        clean_effects.pop("poison", None)
        clean_effects["poison_immunity"] = {
            "ticks_left": _int(spec.get("immunity_ticks")),
            "source": str(spec.get("source", "")),
        }
        data["inventory"] = inventory
        data["combat_status_effects"] = clean_effects
        _write_carried_view(data, view)
        return item_name
    return ""


def _apply_hazard(
    data: dict[str, Any],
    damage: int,
    *,
    source: str,
    poison: int = 0,
) -> dict[str, Any]:
    damaged, damage_result = apply_thieving_damage_pure(
        data,
        damage,
        source=source,
        carried_target_id=PYRAMID_PLUNDER_ACTIVITY_ID,
    )
    data.clear()
    data.update(damaged)
    result = {"source": source, **damage_result, "poison": 0, "antipoison": ""}
    if not damage_result.get("died") and poison > 0:
        poisoned, applied, _reason = apply_combat_poison_effect_pure(data, poison)
        data.clear()
        data.update(poisoned)
        if applied:
            result["poison"] = poison
            result["antipoison"] = _consume_carried_antipoison(data)
    return result


def _skill_success(level: int, endpoints: tuple[int, int], cap: int, rng: Callable[[], float]) -> bool:
    low, high = endpoints
    threshold = min(cap, low + ((high - low) * max(1, min(level, 99)) // 99))
    return int(_roll(rng) * 256) <= threshold


def _end_run(
    data: dict[str, Any],
    session: Mapping[str, Any],
    reason: str,
    *,
    completed: bool = False,
    grave: bool = False,
) -> None:
    data["pyramid_plunder"] = {}
    active = data.get("activity_session")
    if isinstance(active, Mapping) and str(active.get("active_id", "")) == PYRAMID_PLUNDER_ACTIVITY_ID:
        data["activity_session"] = {"active_id": ""}
    carried = dict(data.get("carried_inventory") or {})
    carried.pop(PYRAMID_PLUNDER_ACTIVITY_ID, None)
    data["carried_inventory"] = carried
    if completed:
        data["pyramid_plunder_runs_completed"] = _int(data.get("pyramid_plunder_runs_completed")) + 1
    haul_count = sum(_int(amount) for amount in (session.get("haul") or {}).values())
    destination = "sent to grave" if grave else "banked"
    data["pyramid_plunder_last_result"] = (
        f"{reason} · {haul_count} artefact{'s' if haul_count != 1 else ''} {destination}"
    )


def _loot_object(
    data: dict[str, Any],
    session: dict[str, Any],
    room: int,
    object_kind: str,
    rng: Callable[[], float],
) -> tuple[str, bool]:
    ibis = _roll_black_ibis(data, rng) if object_kind in {"urn", "sarcophagus", "engraved"} else ""
    if ibis:
        return ibis, True
    if object_kind in {"chest", "sarcophagus"}:
        denominator = _rare_denominator(data, int(PYRAMID_PLUNDER_ROOM_DATA[room]["sceptre_denominator"]))
        if _roll(rng) < 1.0 / denominator:
            item = "Pharaoh's sceptre (3)"
            _bank_protected(data, item)
            return item, False
    if object_kind == "engraved" and not _owns_item(data, "Sceptre of the gods"):
        if _roll(rng) < 1.0 / _rare_denominator(data, 650):
            _bank_protected(data, "Sceptre of the gods")
            return "Sceptre of the gods", True
    rows = (
        PYRAMID_PLUNDER_URN_TIER_WEIGHTS[room]
        if object_kind == "urn"
        else PYRAMID_PLUNDER_ENGRAVED_TIER_WEIGHTS
        if object_kind == "engraved"
        else PYRAMID_PLUNDER_SARC_TIER_WEIGHTS[room]
    )
    item = _ordinary_loot(rows, rng)
    if not _retains(str(session["priority"]), item):
        return f"discarded {item}", True
    return item, _retain_ordinary(data, session, item)


def _room_bundle(priority: str, room: int, max_room: int) -> tuple[str, ...]:
    objects: list[str] = []
    if priority in {"balanced", "treasure"}:
        objects.append("chest")
    if priority in {"max_xp", "balanced"} and room >= max(1, max_room - 1):
        objects.extend("urn" for _ in range(int(PYRAMID_PLUNDER_ROOM_DATA[room]["urns"])))
    if priority == "treasure":
        objects.append("sarcophagus")
        if room == 8:
            objects.append("engraved")
    return tuple(objects)


def apply_pyramid_plunder_review_pure(
    player_data: Mapping[str, Any],
    rng: Callable[[], float],
    *,
    rooms: int = 1,
) -> tuple[dict[str, Any], dict[str, Any]]:
    # Shallow on purpose: the plunder state and session are rebuilt fresh, and
    # the carried pack layout is rebuilt before it is edited.
    data = dict(player_data)
    session = sanitize_pyramid_plunder_session_pure(data.get("pyramid_plunder"))
    if not session:
        return data, {"allowed": False, "reason": "Enter Pyramid Plunder before training."}
    # Saved packs can predate item stackability corrections; hazards must use
    # the same capped view as entry and display without removing bank ownership.
    _write_carried_view(data, _carried_view(data))
    total_xp = {"thieving": 0.0, "strength": 0.0, "runecrafting": 0.0}
    outputs: dict[str, int] = {}
    hazards: list[dict[str, Any]] = []
    rooms_completed = 0
    terminal_reason = ""

    for _ in range(max(1, _int(rooms, 1, maximum=100))):
        room = int(session["room"])
        spec = PYRAMID_PLUNDER_ROOM_DATA[room]
        priority = str(session["priority"])
        room_terminal = False
        total_xp["thieving"] += 10.0  # sourced spear-trap XP

        for object_kind in _room_bundle(priority, room, int(session["max_room"])):
            if object_kind == "urn":
                if not _skill_success(_int(data.get("thieving_level"), 1), spec["urn_chance"], 213, rng):
                    damage = 10 + int(_roll(rng) * 31)
                    poison = 20 if _roll(rng) < float(PYRAMID_PLUNDER_FALLBACKS["snake_poison_chance"]) else 0
                    hazard = _apply_hazard(data, damage, source="pyramid_plunder_snake", poison=poison)
                    hazards.append(hazard)
                    if hazard.get("died"):
                        terminal_reason = "Pyramid Plunder run ended by a snake-bite death"
                        room_terminal = True
                        break
                    continue
                total_xp["thieving"] += float(spec["urn_xp"])
                item, room_continues = _loot_object(data, session, room, "urn", rng)
            elif object_kind == "chest":
                if _roll(rng) < float(PYRAMID_PLUNDER_FALLBACKS["scarab_trigger_chance"]):
                    hazard = _apply_hazard(
                        data,
                        int(PYRAMID_PLUNDER_FALLBACKS["scarab_damage"]),
                        source="pyramid_plunder_scarab",
                        poison=38,
                    )
                    hazards.append(hazard)
                    if hazard.get("died"):
                        terminal_reason = "Pyramid Plunder run ended by a scarab-swarm death"
                        room_terminal = True
                        break
                    continue
                total_xp["thieving"] += float(spec["chest_xp"])
                item, room_continues = _loot_object(data, session, room, "chest", rng)
            elif object_kind == "sarcophagus":
                strength_required = room * 10 + 11
                if _int(data.get("strength_level"), 1) < strength_required:
                    continue
                if not _skill_success(_int(data.get("strength_level"), 1), spec["sarc_chance"], 188, rng):
                    current_lp = _int(data.get("combat_lifepoints"), 100)
                    hazard = _apply_hazard(
                        data,
                        max(1, current_lp // 5),
                        source="pyramid_plunder_sarcophagus_failure",
                    )
                    hazards.append(hazard)
                    if hazard.get("died"):
                        terminal_reason = "Pyramid Plunder run ended by a sarcophagus failure"
                        room_terminal = True
                        break
                    continue
                total_xp["strength"] += float(spec["base_xp"])
                if _roll(rng) < float(PYRAMID_PLUNDER_FALLBACKS["mummy_trigger_chance"]):
                    hazard = _apply_hazard(
                        data,
                        int(PYRAMID_PLUNDER_FALLBACKS["mummy_damage"]),
                        source="pyramid_plunder_mummy",
                    )
                    hazards.append(hazard)
                    if hazard.get("died"):
                        terminal_reason = "Pyramid Plunder run ended by an awakened-mummy death"
                        room_terminal = True
                        break
                item, room_continues = _loot_object(data, session, room, "sarcophagus", rng)
            else:  # engraved sarcophagus in room eight
                if _int(data.get("runecrafting_level"), 1) < 75:
                    continue
                total_xp["runecrafting"] += float(spec["base_xp"])
                if _roll(rng) < float(PYRAMID_PLUNDER_FALLBACKS["mummy_trigger_chance"]):
                    hazard = _apply_hazard(
                        data,
                        int(PYRAMID_PLUNDER_FALLBACKS["mummy_damage"]),
                        source="pyramid_plunder_mummy",
                    )
                    hazards.append(hazard)
                    if hazard.get("died"):
                        terminal_reason = "Pyramid Plunder run ended by an awakened-mummy death"
                        room_terminal = True
                        break
                item, room_continues = _loot_object(data, session, room, "engraved", rng)

            if not item.startswith("discarded "):
                outputs[item] = outputs.get(item, 0) + 1
            if item == "Pharaoh's sceptre (3)":
                terminal_reason = "Found a Pharaoh's sceptre and was expelled"
                room_terminal = True
                break
            if not room_continues:
                terminal_reason = "Carried inventory filled; run ended and haul banked"
                room_terminal = True
                break

        if room_terminal:
            break
        if room < int(session["max_room"]):
            total_xp["thieving"] += float(spec["door_xp"])
        rooms_completed += 1
        if room >= int(session["max_room"]):
            terminal_reason = "Pyramid Plunder run complete"
            break
        session["room"] = room + 1

    for skill, amount in total_xp.items():
        session["xp"][skill] = _float(session["xp"].get(skill)) + amount

    completed = terminal_reason == "Pyramid Plunder run complete"
    died = "death" in terminal_reason
    if terminal_reason:
        _end_run(data, session, terminal_reason, completed=completed, grave=died)
    else:
        data["pyramid_plunder"] = session
        data["pyramid_plunder_last_result"] = (
            f"Pyramid Plunder · room {int(session['room'])}/{int(session['max_room'])} ready"
        )

    return data, {
        "allowed": True,
        "action_id": PYRAMID_PLUNDER_ACTIVITY_ID,
        "rooms_completed": rooms_completed,
        "xp": total_xp,
        "outputs": outputs,
        "hazards": tuple(hazards),
        "terminal": bool(terminal_reason),
        "completed": completed,
        "died": died,
        "reason": terminal_reason,
        "status": data["pyramid_plunder_last_result"],
    }


def leave_pyramid_plunder_pure(player_data: Mapping[str, Any]) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the plunder state and session are rebuilt fresh, and
    # the carried pack layout is rebuilt before it is edited.
    data = dict(player_data)
    session = sanitize_pyramid_plunder_session_pure(data.get("pyramid_plunder"))
    if not session:
        return data, False, {"reason": "No Pyramid Plunder run is active."}
    _end_run(data, session, "Left Pyramid Plunder", completed=False)
    return data, True, {"message": data["pyramid_plunder_last_result"]}


def pyramid_plunder_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_pyramid_plunder_state_pure(player_data)
    session = state["pyramid_plunder"]
    priority = str(session.get("priority", state["pyramid_plunder_priority"]))
    view = _carried_view(player_data)
    food = sum(_int(amount) for item, amount in view.items() if item in COMBAT_FOOD_DATA)
    antipoison = sum(_int(amount) for item, amount in view.items() if item in COMBAT_ANTIPOISON_POTION_DATA)
    return {
        "active": bool(session),
        "can_review": bool(session),
        "locked_reasons": pyramid_plunder_locked_reasons_pure(player_data),
        "priority": priority,
        "priority_label": PYRAMID_PLUNDER_PRIORITIES[priority],
        "room": int(session.get("room", 0)),
        "max_room": int(session.get("max_room", _maximum_room(max(21, _int(player_data.get("thieving_level"), 21))))),
        "xp": dict(session.get("xp") or {}),
        "haul": dict(session.get("haul") or {}),
        "pack_slots": carried_slots_used(view, _stackable_names()),
        "food": food,
        "antipoison": antipoison,
        "lifepoints": _int(player_data.get("combat_lifepoints"), 100),
        "poisoned": bool(
            isinstance(player_data.get("combat_status_effects"), Mapping)
            and "poison" in player_data.get("combat_status_effects", {})
        ),
        "poison_immunity_ticks": combat_poison_immunity_ticks_pure(player_data),
        "runs_completed": state["pyramid_plunder_runs_completed"],
        "last_result": state["pyramid_plunder_last_result"],
    }
