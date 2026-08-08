"""Pure Goblin Raids world clock, raid stages, village boss loop and spoils."""

from __future__ import annotations

import copy
from collections.abc import Callable, Mapping
from typing import Any

from ..data.goblin_raids_data import (
    GOBLIN_COWER_SHIELD,
    GOBLIN_COWER_SHIELD_BONUS_BUDGET,
    GOBLIN_COWER_SHIELD_BONUS_RATE,
    GOBLIN_COWER_SHIELD_DROP_CHANCE,
    GOBLIN_COWER_SHIELD_EXP_KEYS,
    GOBLIN_RAID_ENEMIES_BY_ID,
    GOBLIN_RAID_SITES_BY_ID,
    GOBLIN_RAID_SITE_IDS,
    GOBLIN_RAID_VILLAGE_BOSS_IDS,
    GOBLIN_RAIDER,
    GOBLIN_RAIDS_ACTIVE_REVIEWS,
    GOBLIN_RAIDS_ACTIVITY_ID,
    GOBLIN_RAIDS_INTIMIDATION_COMBAT_LEVEL,
    GOBLIN_RAIDS_RAIDER_COUNT,
    GOBLIN_RAIDS_RAID_MODE,
    GOBLIN_RAIDS_SOURCE,
    GOBLIN_RAIDS_SPAWN_REVIEWS,
    GOBLIN_RAIDS_VILLAGE_BOSS_KILLS,
    GOBLIN_RAIDS_VILLAGE_MODE,
    GOBLIN_RAIDS_YODRI_ITEMS_PER_GOBLIN,
    HOLLOWTOOF,
    RAIDER_SET,
    RAIDER_SET_ITEM_NAMES,
    VILLAGE_GOBLIN,
)
from ..logic_pure.logic_pure import (
    apply_combat_burst_pure,
    player_combat_level_pure,
)


GOBLIN_RAIDS_STATE_VERSION = 1
GOBLIN_RAIDS_COMBAT_TICKS = 6
GOBLIN_RAIDS_STAGES = ("raiders", "leader", "spoils")
_MODES = frozenset({GOBLIN_RAIDS_RAID_MODE, GOBLIN_RAIDS_VILLAGE_MODE})


def _int(value: Any, default: int = 0, *, minimum: int = 0) -> int:
    if isinstance(value, bool):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(minimum, parsed)


def _float(value: Any, default: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(0.0, parsed)


def _roll(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        return 0.0
    return min(0.999999, max(0.0, parsed))


def _answered_cards(player_data: Mapping[str, Any]) -> int:
    clock = player_data.get("shop_market_clock")
    if not isinstance(clock, Mapping):
        return 0
    return _int(clock.get("answered_cards"))


def default_goblin_raids_state_pure() -> dict[str, Any]:
    return {
        "version": GOBLIN_RAIDS_STATE_VERSION,
        "last_world_card": 0,
        "next_spawn_card": GOBLIN_RAIDS_SPAWN_REVIEWS,
        "active_raid": {},
        "session": {},
        "village_kills": 0,
        "raids_cleared": 0,
        "raid_goblins_killed": 0,
        "bosses_felled": 0,
        "cower_shields_found": 0,
        "cower_shield_bonus_remaining": 0.0,
        "cower_shield_bonus_awarded": 0.0,
        "last_result": "",
    }


def _sanitize_spoils(raw: Any) -> dict[str, int]:
    if not isinstance(raw, Mapping):
        return {}
    return {
        str(item): count
        for item, count in ((k, _int(v)) for k, v in raw.items())
        if count > 0
    }


def _sanitize_session(raw: Any, raid: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}
    mode = str(raw.get("mode", ""))
    if mode not in _MODES:
        return {}
    if mode == GOBLIN_RAIDS_RAID_MODE:
        stage = str(raw.get("stage", ""))
        if stage not in GOBLIN_RAIDS_STAGES:
            return {}
        # Combat cannot outlive its raid. Yodri's spoils are different: he
        # arrives after the raid ends, and that pending claim survives while
        # the world clock moves on to the next incursion.
        if stage != "spoils" and (
            not raid
            or str(raw.get("raid_id", "")) != str(raid.get("raid_id", ""))
        ):
            return {}
    else:
        stage = "raiders"
    boss_id = str(raw.get("boss_id", ""))
    return {
        "mode": mode,
        "raid_id": str(raw.get("raid_id", ""))[:80],
        "site_id": (
            str(raw.get("site_id", ""))
            if str(raw.get("site_id", "")) in GOBLIN_RAID_SITES_BY_ID
            else GOBLIN_RAID_SITE_IDS[0]
        ),
        "stage": stage,
        "raiders_remaining": min(
            GOBLIN_RAIDS_RAIDER_COUNT, _int(raw.get("raiders_remaining"))
        ),
        "goblins_killed": _int(raw.get("goblins_killed")),
        "shouts": _int(raw.get("shouts")),
        "spoils": _sanitize_spoils(raw.get("spoils")),
        "boss_id": boss_id if boss_id in GOBLIN_RAID_VILLAGE_BOSS_IDS else "",
        "target_id": str(raw.get("target_id", ""))[:80],
        "enemy_lifepoints": _int(raw.get("enemy_lifepoints")),
        "encounter": (
            copy.deepcopy(dict(raw["encounter"]))
            if isinstance(raw.get("encounter"), Mapping)
            else {}
        ),
        "previous_combat_target": str(raw.get("previous_combat_target", ""))[:120],
        "intimidated": bool(raw.get("intimidated", False)),
    }


def sanitize_goblin_raids_state_pure(raw: Any) -> dict[str, Any]:
    defaults = default_goblin_raids_state_pure()
    source = raw if isinstance(raw, Mapping) else {}

    raid: dict[str, Any] = {}
    raw_raid = source.get("active_raid")
    if isinstance(raw_raid, Mapping):
        raid_id = str(raw_raid.get("raid_id", ""))
        site_id = str(raw_raid.get("site_id", ""))
        remaining = _int(raw_raid.get("reviews_remaining"))
        if raid_id and site_id in GOBLIN_RAID_SITES_BY_ID and remaining > 0:
            raid = {
                "raid_id": raid_id[:80],
                "site_id": site_id,
                "spawn_card": _int(raw_raid.get("spawn_card")),
                "reviews_remaining": min(remaining, GOBLIN_RAIDS_ACTIVE_REVIEWS),
            }
    return {
        **defaults,
        "last_world_card": _int(source.get("last_world_card")),
        "next_spawn_card": max(
            1, _int(source.get("next_spawn_card"), GOBLIN_RAIDS_SPAWN_REVIEWS)
        ),
        "active_raid": raid,
        "session": _sanitize_session(source.get("session"), raid),
        "village_kills": _int(source.get("village_kills")),
        "raids_cleared": _int(source.get("raids_cleared")),
        "raid_goblins_killed": _int(source.get("raid_goblins_killed")),
        "bosses_felled": _int(source.get("bosses_felled")),
        "cower_shields_found": _int(source.get("cower_shields_found")),
        "cower_shield_bonus_remaining": min(
            GOBLIN_COWER_SHIELD_BONUS_BUDGET,
            _float(source.get("cower_shield_bonus_remaining")),
        ),
        "cower_shield_bonus_awarded": min(
            GOBLIN_COWER_SHIELD_BONUS_BUDGET,
            _float(source.get("cower_shield_bonus_awarded")),
        ),
        "last_result": str(source.get("last_result", ""))[:300],
    }


def ensure_goblin_raids_state_pure(
    player_data: Mapping[str, Any],
) -> dict[str, Any]:
    # Shallow on purpose, matching the Evil Tree world clock: sanitize rebuilds
    # the one key this owns and a whole-save deep copy on every review is waste.
    data = dict(player_data)
    data["goblin_raids"] = sanitize_goblin_raids_state_pure(
        data.get("goblin_raids")
    )
    return data


def goblin_raids_spawn_due_pure(player_data: Mapping[str, Any]) -> bool:
    state = ensure_goblin_raids_state_pure(player_data)["goblin_raids"]
    return (
        not state["active_raid"]
        and _answered_cards(player_data) >= int(state["next_spawn_card"])
    )


def advance_goblin_raids_world_clock_pure(
    player_data: Mapping[str, Any],
    *,
    site_roll: Any = 0.0,
) -> tuple[dict[str, Any], tuple[dict[str, Any], ...]]:
    """Expire the standing raid and announce the next one.

    The host calls this once after every answered card. No wall-clock state is
    read; the sourced half-hourly announcement is
    `GOBLIN_RAIDS_SPAWN_REVIEWS` answered cards.
    """
    data = ensure_goblin_raids_state_pure(player_data)
    state = dict(data["goblin_raids"])
    answered = _answered_cards(data)
    previous = min(answered, int(state["last_world_card"]))
    elapsed = answered - previous
    events: list[dict[str, Any]] = []

    raid = dict(state["active_raid"])
    if raid and elapsed > 0:
        raid["reviews_remaining"] = max(
            0, int(raid["reviews_remaining"]) - elapsed
        )
        if raid["reviews_remaining"] <= 0:
            session = state["session"]
            if (
                session
                and session["mode"] == GOBLIN_RAIDS_RAID_MODE
                and session["raid_id"] == raid["raid_id"]
            ):
                state["session"] = {}
                state["last_result"] = (
                    "The raid was over before you finished it; the goblins "
                    "made off with their spoils."
                )
            state["active_raid"] = {}
            state["next_spawn_card"] = answered + GOBLIN_RAIDS_SPAWN_REVIEWS
            events.append({"kind": "expired", "raid_id": raid["raid_id"]})
        else:
            state["active_raid"] = raid

    if not state["active_raid"] and answered >= int(state["next_spawn_card"]):
        site_index = min(
            len(GOBLIN_RAID_SITE_IDS) - 1,
            int(_roll(site_roll) * len(GOBLIN_RAID_SITE_IDS)),
        )
        site_id = GOBLIN_RAID_SITE_IDS[site_index]
        state["active_raid"] = {
            "raid_id": f"raid-{answered}-{site_id}",
            "site_id": site_id,
            "spawn_card": answered,
            "reviews_remaining": GOBLIN_RAIDS_ACTIVE_REVIEWS,
        }
        state["next_spawn_card"] = answered + GOBLIN_RAIDS_SPAWN_REVIEWS
        events.append({"kind": "announced", "site_id": site_id})

    state["last_world_card"] = answered
    data["goblin_raids"] = state
    return data, tuple(events)


def _adjust_stack(data: dict[str, Any], item: str, amount: int) -> None:
    inventory = (
        dict(data.get("inventory"))
        if isinstance(data.get("inventory"), Mapping)
        else {}
    )
    total = _int(inventory.get(item)) + amount
    if total > 0:
        inventory[item] = total
    else:
        inventory.pop(item, None)
    data["inventory"] = inventory


def _owned_raider_pieces(player_data: Mapping[str, Any]) -> set[str]:
    owned: set[str] = set()
    inventory = player_data.get("inventory")
    if isinstance(inventory, Mapping):
        owned |= {
            name for name in RAIDER_SET_ITEM_NAMES if _int(inventory.get(name))
        }
    equipment = player_data.get("equipment")
    if isinstance(equipment, Mapping):
        owned |= {
            str(item)
            for item in equipment.values()
            if str(item) in RAIDER_SET_ITEM_NAMES
        }
    return owned


def next_raider_set_piece_pure(player_data: Mapping[str, Any]) -> str:
    """Exact: one piece per Hollowtoof kill, chainbody then axe then shield.

    The article also records that a player who already holds the whole set is
    dropped the chainbody again, and flags that as possibly unintended. It is
    what the period did, so it is what happens here.
    """
    owned = _owned_raider_pieces(player_data)
    for piece in RAIDER_SET:
        if piece.item_name not in owned:
            return piece.item_name
    return RAIDER_SET[0].item_name


def _empty_activity_session() -> dict[str, str]:
    return {"active_id": ""}


def _enemy_row(target_id: str, enemy_data: Mapping[str, Any]) -> dict[str, Any]:
    return {target_id: dict(enemy_data[target_id])}


def _finish(data: dict[str, Any], state: dict[str, Any], message: str) -> None:
    session = state["session"]
    data["activity_session"] = _empty_activity_session()
    data["combat_encounter"] = {}
    data["current_combat_target"] = str(
        session.get("previous_combat_target", "")
    )
    for key in ("carried_inventory", "carried_churn"):
        raw = data.get(key)
        target = str(session.get("target_id", ""))
        if isinstance(raw, Mapping) and target and target in raw:
            copied = copy.deepcopy(dict(raw))
            copied.pop(target, None)
            data[key] = copied
    state["session"] = {}
    state["last_result"] = message


def join_goblin_raid_pure(
    player_data: Mapping[str, Any],
    mode: str = GOBLIN_RAIDS_RAID_MODE,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_goblin_raids_state_pure(data.get("goblin_raids"))
    if state["session"]:
        return data, False, {"reason": "You are already fighting goblins."}
    if mode not in _MODES:
        return data, False, {"reason": "Unknown Goblin Raids duty."}
    active = data.get("activity_session")
    active_id = (
        str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    )
    if active_id and active_id != GOBLIN_RAIDS_ACTIVITY_ID:
        return data, False, {
            "reason": "Finish the active persistent activity first."
        }
    encounter = data.get("combat_encounter")
    if isinstance(encounter, Mapping) and encounter:
        return data, False, {
            "reason": "Finish or leave the current Combat encounter first."
        }
    raid = state["active_raid"]
    if mode == GOBLIN_RAIDS_RAID_MODE and not raid:
        return data, False, {
            "reason": (
                "No raid has been announced. Watch for the next notice, or "
                "take the Goblin Village duty instead."
            )
        }
    previous_target = str(data.get("current_combat_target", ""))[:120]
    if mode == GOBLIN_RAIDS_RAID_MODE:
        site = GOBLIN_RAID_SITES_BY_ID[raid["site_id"]]
        session = {
            "mode": mode,
            "raid_id": raid["raid_id"],
            "site_id": site.id,
            "stage": "raiders",
            "raiders_remaining": GOBLIN_RAIDS_RAIDER_COUNT,
            "goblins_killed": 0,
            "shouts": 0,
            "spoils": {},
            "boss_id": "",
            "target_id": GOBLIN_RAIDER.id,
            "enemy_lifepoints": GOBLIN_RAIDER.lifepoints,
            "encounter": {},
            "previous_combat_target": previous_target,
            "intimidated": False,
        }
        message = (
            f"Joined the raid on {site.display_name}; "
            f"{GOBLIN_RAIDS_RAIDER_COUNT} Goblin Raiders are looting it."
        )
    else:
        session = {
            "mode": mode,
            "raid_id": "",
            "site_id": GOBLIN_RAID_SITE_IDS[0],
            "stage": "raiders",
            "raiders_remaining": 0,
            "goblins_killed": 0,
            "shouts": 0,
            "spoils": {},
            "boss_id": "",
            "target_id": VILLAGE_GOBLIN.id,
            "enemy_lifepoints": VILLAGE_GOBLIN.lifepoints,
            "encounter": {},
            "previous_combat_target": previous_target,
            "intimidated": False,
        }
        remaining = GOBLIN_RAIDS_VILLAGE_BOSS_KILLS - (
            state["village_kills"] % GOBLIN_RAIDS_VILLAGE_BOSS_KILLS
        )
        message = (
            f"Started the Goblin Village duty; {remaining} more goblins "
            f"inside the gates will summon a boss."
        )
    state["session"] = session
    state["last_result"] = message
    data["goblin_raids"] = state
    data["activity_session"] = {"active_id": GOBLIN_RAIDS_ACTIVITY_ID}
    data["current_utility"] = GOBLIN_RAIDS_ACTIVITY_ID
    data["combat_encounter"] = {}
    data["current_combat_target"] = session["target_id"]
    return data, True, {"message": message, "mode": mode}


def intimidate_hollowtoof_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    """The sourced high-level shortcut: the whole set without a fight.

    Available only while ordinary raiders are still alive, which is exactly the
    window the article describes.
    """
    data = copy.deepcopy(dict(player_data))
    state = sanitize_goblin_raids_state_pure(data.get("goblin_raids"))
    session = state["session"]
    if not session or session["mode"] != GOBLIN_RAIDS_RAID_MODE:
        return data, False, {"reason": "Join a goblin raid first."}
    if session["stage"] != "raiders":
        return data, False, {
            "reason": "Hollowtoof only hands the set over while his raiders live."
        }
    level = player_combat_level_pure(data)
    if level < GOBLIN_RAIDS_INTIMIDATION_COMBAT_LEVEL:
        return data, False, {
            "reason": (
                f"Hollowtoof is not impressed. Around combat level "
                f"{GOBLIN_RAIDS_INTIMIDATION_COMBAT_LEVEL} would intimidate him; "
                f"you are {level}."
            )
        }
    granted = [
        piece.item_name
        for piece in RAIDER_SET
        if piece.item_name not in _owned_raider_pieces(data)
    ]
    if not granted:
        return data, False, {"reason": "You already own the whole Raider set."}
    for item_name in granted:
        _adjust_stack(data, item_name, 1)
    session["intimidated"] = True
    state["session"] = session
    message = (
        "Hollowtoof backs down and hands over "
        + ", ".join(granted)
        + "."
    )
    state["last_result"] = message
    data["goblin_raids"] = state
    return data, True, {"message": message, "granted": tuple(granted)}


def claim_goblin_raid_spoils_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    """Commander Yodri pays out once the raid's goblins are dead."""
    data = copy.deepcopy(dict(player_data))
    state = sanitize_goblin_raids_state_pure(data.get("goblin_raids"))
    session = state["session"]
    if not session or session["mode"] != GOBLIN_RAIDS_RAID_MODE:
        return data, False, {"reason": "Join a goblin raid first."}
    if session["stage"] != "spoils":
        return data, False, {
            "reason": "Commander Yodri arrives once the raid's goblins are dead."
        }
    site = GOBLIN_RAID_SITES_BY_ID[session["site_id"]]
    awarded = dict(session["spoils"])
    # Sourced: an item for every goblin the player slew, plus an extra suited to
    # where the raid was. Both are paid in the site's own stated material kind.
    per_goblin = int(session["goblins_killed"]) * GOBLIN_RAIDS_YODRI_ITEMS_PER_GOBLIN
    for index in range(per_goblin):
        item = site.materials[index % len(site.materials)]
        awarded[item] = awarded.get(item, 0) + 1
    for item, count in awarded.items():
        _adjust_stack(data, item, count)
    state["raids_cleared"] += 1
    message = (
        f"Commander Yodri thanks you for {session['goblins_killed']} goblins "
        f"and hands over "
        + ", ".join(f"{count} × {item}" for item, count in sorted(awarded.items()))
        + f" from {site.display_name}."
    )
    _finish(data, state, message)
    data["goblin_raids"] = state
    return data, True, {
        "message": message,
        "rewards": awarded,
        "goblins_killed": per_goblin,
    }


def leave_goblin_raids_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_goblin_raids_state_pure(data.get("goblin_raids"))
    if not state["session"]:
        return data, False, {"reason": "You are not fighting goblins."}
    dropped = dict(state["session"]["spoils"])
    message = "Walked away from the goblins."
    if dropped:
        message += " The spoils you had not claimed are lost."
    _finish(data, state, message)
    data["goblin_raids"] = state
    return data, True, {"message": message, "outcome": "left", "lost": dropped}


def _summon_village_boss(
    state: dict[str, Any],
    session: dict[str, Any],
    roll: float,
) -> str:
    index = min(
        len(GOBLIN_RAID_VILLAGE_BOSS_IDS) - 1,
        int(_roll(roll) * len(GOBLIN_RAID_VILLAGE_BOSS_IDS)),
    )
    boss_id = GOBLIN_RAID_VILLAGE_BOSS_IDS[index]
    session["boss_id"] = boss_id
    session["target_id"] = boss_id
    session["enemy_lifepoints"] = GOBLIN_RAID_ENEMIES_BY_ID[boss_id].lifepoints
    session["encounter"] = {}
    return boss_id


def apply_goblin_raids_review_pure(
    player_data: Mapping[str, Any],
    rng: Callable[[], float] | None = None,
    *,
    enemy_data: Mapping[str, Any],
    equipment_data: Mapping[str, Any] | None = None,
    productive: bool = True,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_goblin_raids_state_pure(data.get("goblin_raids"))
    session = state["session"]
    active = data.get("activity_session")
    active_id = (
        str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    )
    if not session or active_id != GOBLIN_RAIDS_ACTIVITY_ID:
        data["goblin_raids"] = state
        return data, False, {"reason": "Join a goblin raid or the village duty first."}
    if not productive:
        data["goblin_raids"] = state
        return data, True, {
            "advanced": False,
            "terminal": False,
            "message": "Goblin Raids advances only on an eligible successful review.",
        }
    draws = rng or (lambda: 0.5)
    if session["stage"] == "spoils":
        data["goblin_raids"] = state
        return data, True, {
            "advanced": False,
            "terminal": False,
            "message": (
                "The raid is over. Claim your spoils from Commander Yodri."
            ),
        }

    target_id = session["target_id"]
    data["current_combat_target"] = target_id
    encounter = copy.deepcopy(session["encounter"])
    encounter["target_id"] = target_id
    encounter["enemy_lifepoints"] = int(session["enemy_lifepoints"])
    data["combat_encounter"] = encounter
    data, ok, combat = apply_combat_burst_pure(
        data,
        _enemy_row(target_id, enemy_data),
        equipment_data or {},
        ticks=GOBLIN_RAIDS_COMBAT_TICKS,
        rng=draws,
        live_cadence=True,
        stop_after_first_kill=True,
        allow_bank_run=False,
    )
    if not ok:
        return copy.deepcopy(dict(player_data)), False, {
            "reason": "Goblin Raids combat setup is not runnable.",
            "combat": combat,
        }

    events: list[str] = []
    shield_found = False
    if combat.get("died"):
        # Raid and village goblins are ordinary open-world content, so a death
        # uses the ordinary death pipeline the burst already applied. It ends the
        # player's part in this raid.
        message = "The goblins put you down. Your part in the raid is over."
        _finish(data, state, message)
        data["goblin_raids"] = state
        return data, True, {
            "advanced": True,
            "terminal": True,
            "outcome": "death",
            "combat": combat,
            "message": message,
        }

    if combat.get("killed"):
        session["goblins_killed"] += 1
        if session["mode"] == GOBLIN_RAIDS_RAID_MODE:
            state["raid_goblins_killed"] += 1
            if session["stage"] == "raiders":
                # Each raider has been shouting and hoarding since the raid
                # began, and drops everything it took when it dies.
                site = GOBLIN_RAID_SITES_BY_ID[session["site_id"]]
                for index in range(max(1, int(session["shouts"]) + 1)):
                    item = site.materials[index % len(site.materials)]
                    session["spoils"][item] = session["spoils"].get(item, 0) + 1
                session["shouts"] = 0
                session["raiders_remaining"] = max(
                    0, int(session["raiders_remaining"]) - 1
                )
                if session["raiders_remaining"] <= 0:
                    session["stage"] = "leader"
                    session["target_id"] = HOLLOWTOOF.id
                    session["enemy_lifepoints"] = HOLLOWTOOF.lifepoints
                    session["encounter"] = {}
                    events.append(
                        "Hollowtoof shouts \"Now it's my turn!\" and turns on you."
                    )
                else:
                    session["target_id"] = GOBLIN_RAIDER.id
                    session["enemy_lifepoints"] = GOBLIN_RAIDER.lifepoints
                    session["encounter"] = {}
            else:
                piece = next_raider_set_piece_pure(data)
                _adjust_stack(data, piece, 1)
                session["stage"] = "spoils"
                session["encounter"] = {}
                state["active_raid"] = {}
                events.append(f"Hollowtoof drops the {piece}.")
        else:
            state["village_kills"] += 1
            if session["boss_id"]:
                state["bosses_felled"] += 1
                boss_name = GOBLIN_RAID_ENEMIES_BY_ID[
                    session["boss_id"]
                ].display_name
                if _roll(draws()) < GOBLIN_COWER_SHIELD_DROP_CHANCE:
                    _adjust_stack(data, GOBLIN_COWER_SHIELD, 1)
                    state["cower_shields_found"] += 1
                    state["cower_shield_bonus_remaining"] = (
                        GOBLIN_COWER_SHIELD_BONUS_BUDGET
                    )
                    state["cower_shield_bonus_awarded"] = 0.0
                    shield_found = True
                    events.append(
                        f"{boss_name} falls and drops the {GOBLIN_COWER_SHIELD}."
                    )
                else:
                    events.append(f"{boss_name} falls.")
                session["boss_id"] = ""
                session["target_id"] = VILLAGE_GOBLIN.id
                session["enemy_lifepoints"] = VILLAGE_GOBLIN.lifepoints
                session["encounter"] = {}
            elif state["village_kills"] % GOBLIN_RAIDS_VILLAGE_BOSS_KILLS == 0:
                boss_id = _summon_village_boss(state, session, draws())
                events.append(
                    f"{GOBLIN_RAID_ENEMIES_BY_ID[boss_id].display_name} "
                    f"stomps out of the village."
                )
            else:
                session["target_id"] = VILLAGE_GOBLIN.id
                session["enemy_lifepoints"] = VILLAGE_GOBLIN.lifepoints
                session["encounter"] = {}
    else:
        after = data.get("combat_encounter")
        if isinstance(after, Mapping):
            session["enemy_lifepoints"] = _int(
                after.get("enemy_lifepoints"), int(session["enemy_lifepoints"])
            )
            session["encounter"] = copy.deepcopy(dict(after))
        if session["mode"] == GOBLIN_RAIDS_RAID_MODE and session["stage"] == "raiders":
            # Every relevant shout adds one raided item to that goblin's hoard.
            session["shouts"] += 1

    state["session"] = session
    progress = (
        f"{session['raiders_remaining']} raiders left"
        if session["mode"] == GOBLIN_RAIDS_RAID_MODE
        and session["stage"] == "raiders"
        else "Hollowtoof"
        if session["mode"] == GOBLIN_RAIDS_RAID_MODE
        and session["stage"] == "leader"
        else "Commander Yodri is waiting"
        if session["stage"] == "spoils"
        else f"{state['village_kills']} village goblins felled"
    )
    state["last_result"] = " · ".join([progress] + events)
    data["goblin_raids"] = state
    return data, True, {
        "advanced": True,
        "terminal": False,
        "combat": combat,
        "stage": session["stage"],
        "events": tuple(events),
        "shield_found": shield_found,
        "spoils": dict(session["spoils"]),
        "message": state["last_result"],
    }


def goblin_cower_shield_can_apply_pure(
    player_data: Mapping[str, Any],
    exp_key: str,
) -> bool:
    """Fast hot-path gate before the bonus reducer copies anything."""
    if exp_key not in GOBLIN_COWER_SHIELD_EXP_KEYS:
        return False
    state = player_data.get("goblin_raids")
    if not isinstance(state, Mapping):
        return False
    try:
        if float(state.get("cower_shield_bonus_remaining") or 0.0) <= 0.0:
            return False
    except (TypeError, ValueError):
        return False
    equipment = player_data.get("equipment")
    return isinstance(equipment, Mapping) and GOBLIN_COWER_SHIELD in {
        str(item) for item in equipment.values()
    }


def apply_goblin_cower_shield_bonus_pure(
    player_data: Mapping[str, Any],
    exp_key: str,
    base_exp: Any,
) -> tuple[dict[str, Any], float, dict[str, Any]]:
    """Exact: 25% bonus Attack, Defence and Constitution experience, cap 1,000.

    Once the budget is spent the shield keeps its slot and stops paying, which is
    the period's "then it becomes cosmetic".
    """
    data = dict(player_data)
    if not goblin_cower_shield_can_apply_pure(data, exp_key):
        return data, 0.0, {"applied": False}
    state = sanitize_goblin_raids_state_pure(data.get("goblin_raids"))
    remaining = float(state["cower_shield_bonus_remaining"])
    bonus = min(max(0.0, float(base_exp)) * GOBLIN_COWER_SHIELD_BONUS_RATE, remaining)
    if bonus <= 0.0:
        data["goblin_raids"] = state
        return data, 0.0, {"applied": False}
    state["cower_shield_bonus_remaining"] = remaining - bonus
    state["cower_shield_bonus_awarded"] = (
        float(state["cower_shield_bonus_awarded"]) + bonus
    )
    exhausted = state["cower_shield_bonus_remaining"] <= 0.0
    if exhausted:
        state["last_result"] = (
            f"The {GOBLIN_COWER_SHIELD} has given out its bonus experience and "
            f"is now purely cosmetic."
        )
    data["goblin_raids"] = state
    return data, bonus, {
        "applied": True,
        "bonus_exp": bonus,
        "remaining": state["cower_shield_bonus_remaining"],
        "exhausted": exhausted,
    }


def apply_goblin_raids_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    body = payload if isinstance(payload, Mapping) else {}
    if action_id == "join":
        return join_goblin_raid_pure(
            player_data, str(body.get("mode", GOBLIN_RAIDS_RAID_MODE))
        )
    if action_id == "intimidate":
        return intimidate_hollowtoof_pure(player_data)
    if action_id == "claim_spoils":
        return claim_goblin_raid_spoils_pure(player_data)
    if action_id == "leave":
        return leave_goblin_raids_pure(player_data)
    return copy.deepcopy(dict(player_data)), False, {
        "reason": "Unknown Goblin Raids command."
    }


def goblin_raids_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    """Own every enable, visibility and warning decision the panel renders.

    The panel is a renderer: it reads these flags and never re-derives a rule.
    """
    state = sanitize_goblin_raids_state_pure(player_data.get("goblin_raids"))
    session = state["session"]
    raid = state["active_raid"]
    active = player_data.get("activity_session")
    active_id = (
        str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    )
    encounter = player_data.get("combat_encounter")
    answered = _answered_cards(player_data)
    combat_level = player_combat_level_pure(player_data)
    reasons: list[str] = []
    if active_id and active_id != GOBLIN_RAIDS_ACTIVITY_ID:
        reasons.append("Finish the active persistent activity.")
    if not session and isinstance(encounter, Mapping) and encounter:
        reasons.append("Finish or leave the current Combat encounter.")
    site = GOBLIN_RAID_SITES_BY_ID.get(raid.get("site_id", "")) if raid else None
    stage = str(session["stage"]) if session else ""
    mode = str(session["mode"]) if session else ""
    in_raid = mode == GOBLIN_RAIDS_RAID_MODE
    target = (
        GOBLIN_RAID_ENEMIES_BY_ID.get(str(session["target_id"]))
        if session
        else None
    )
    owned = _owned_raider_pieces(player_data)
    can_intimidate = bool(
        in_raid
        and stage == "raiders"
        and combat_level >= GOBLIN_RAIDS_INTIMIDATION_COMBAT_LEVEL
        and len(owned) < len(RAIDER_SET)
    )
    inventory = player_data.get("inventory")
    shield_held = bool(
        _int(inventory.get(GOBLIN_COWER_SHIELD))
        if isinstance(inventory, Mapping)
        else 0
    )
    return {
        **state,
        "active": bool(session),
        "raid_announced": bool(raid),
        "raid_site": site.display_name if site else "",
        "raid_site_id": site.id if site else "",
        "raid_spoil_kind": site.spoil_kind if site else "",
        "raid_reviews_remaining": int(raid["reviews_remaining"]) if raid else 0,
        "next_raid_reviews": (
            0 if raid else max(0, int(state["next_spawn_card"]) - answered)
        ),
        "announcement_interval": GOBLIN_RAIDS_SPAWN_REVIEWS,
        "entry_reasons": tuple(reasons),
        "can_join_raid": bool(raid) and not session and not reasons,
        "can_join_village": not session and not reasons,
        "mode": mode,
        "stage": stage,
        "stage_label": (
            f"{int(session['raiders_remaining'])} Goblin Raiders still looting"
            if in_raid and stage == "raiders"
            else "Hollowtoof is attackable"
            if in_raid and stage == "leader"
            else "Commander Yodri is waiting with the spoils"
            if stage == "spoils"
            else "Goblin Village duty"
            if session
            else "Watching for the next notice"
        ),
        "target_name": target.display_name if target else "",
        "combat_level": combat_level,
        "intimidation_combat_level": GOBLIN_RAIDS_INTIMIDATION_COMBAT_LEVEL,
        "intimidate_visible": bool(in_raid and stage == "raiders"),
        "intimidate_enabled": can_intimidate,
        "intimidate_reason": (
            ""
            if can_intimidate
            else "You already own the whole Raider set."
            if in_raid and len(owned) >= len(RAIDER_SET)
            else (
                f"Around combat level "
                f"{GOBLIN_RAIDS_INTIMIDATION_COMBAT_LEVEL} would intimidate "
                f"Hollowtoof; you are {combat_level}."
            )
        ),
        "claim_visible": stage == "spoils",
        "claim_enabled": stage == "spoils",
        "pending_spoils": dict(session["spoils"]) if session else {},
        "raider_set_owned": tuple(
            piece.item_name for piece in RAIDER_SET if piece.item_name in owned
        ),
        "raider_set_next": next_raider_set_piece_pure(player_data),
        "raider_set_complete": len(owned) >= len(RAIDER_SET),
        "village_boss_kills": GOBLIN_RAIDS_VILLAGE_BOSS_KILLS,
        "village_kills_to_boss": (
            GOBLIN_RAIDS_VILLAGE_BOSS_KILLS
            - (int(state["village_kills"]) % GOBLIN_RAIDS_VILLAGE_BOSS_KILLS)
        ),
        "boss_active": bool(session and session["boss_id"]),
        "cower_shield_held": shield_held,
        "cower_shield_bonus_budget": GOBLIN_COWER_SHIELD_BONUS_BUDGET,
        "cower_shield_cosmetic": bool(
            shield_held and float(state["cower_shield_bonus_remaining"]) <= 0.0
        ),
        "summary_text": state["last_result"]
        or (
            f"A raid is under way at {site.display_name}."
            if site
            else "No raid has been announced yet."
        ),
        "progress_value": (
            int(session["goblins_killed"]) if session else 0
        ),
        "progress_maximum": max(
            1,
            GOBLIN_RAIDS_RAIDER_COUNT + 1
            if in_raid
            else GOBLIN_RAIDS_VILLAGE_BOSS_KILLS,
        ),
        "progress_format": (
            f"{int(session['goblins_killed'])} of "
            f"{GOBLIN_RAIDS_RAIDER_COUNT + 1} raid goblins"
            if in_raid
            else f"{int(state['village_kills'])} village goblins felled"
            if session
            else f"Notices arrive every {GOBLIN_RAIDS_SPAWN_REVIEWS} reviews"
        ),
        "primary_label": (
            "Selected for reviews"
            if session
            and str(player_data.get("current_utility", ""))
            == GOBLIN_RAIDS_ACTIVITY_ID
            else "Select for reviews"
            if session
            else "Join the raid"
            if raid
            else "Goblin Village duty"
        ),
        "leave_visible": bool(session),
        "source": GOBLIN_RAIDS_SOURCE,
    }
