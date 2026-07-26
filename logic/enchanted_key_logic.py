"""Pure, review-driven Enchanted key treasure hunt.

The period hunt is positional: the player walks, feels the key, reads a
temperature, and digs when it steams. AnkiScape has no map, so the walking is
flattened the way Penguin Hide and Seek flattens spotting — the player picks one
of the eleven known treasure sites to search, and one answered card is one trip
out to it. Everything the key itself does is unchanged: the reading is the
period Chebyshev ladder measured against the real site coordinates, the order is
fixed at Fremennik Province and then random per save, and the key melts once the
eleventh treasure is out of the ground.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..data.enchanted_key_data import (
    ENCHANTED_KEY_ACTIVITY_ID,
    ENCHANTED_KEY_COLDER,
    ENCHANTED_KEY_DIG_DISTANCE,
    ENCHANTED_KEY_ITEM,
    ENCHANTED_KEY_QUEST_ID,
    ENCHANTED_KEY_REPLACEMENT_BLOCKING_QUEST_ID,
    ENCHANTED_KEY_REPLACEMENT_COST,
    ENCHANTED_KEY_SAME,
    ENCHANTED_KEY_SITE_IDS,
    ENCHANTED_KEY_SITES,
    ENCHANTED_KEY_SPADE,
    ENCHANTED_KEY_WARMER,
    TreasureSite,
    enchanted_key_temperature_pure,
)


ENCHANTED_KEY_STATE_VERSION = 1
_SITES_BY_ID = {site.id: site for site in ENCHANTED_KEY_SITES}


def _int(value: Any, default: int = 0, *, minimum: int = 0) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(minimum, parsed)


def _quest_state(player_data: Mapping[str, Any], quest_id: str) -> Mapping[str, Any]:
    quests = player_data.get("quests")
    if not isinstance(quests, Mapping):
        return {}
    state = quests.get(quest_id)
    return state if isinstance(state, Mapping) else {}


def _quest_complete(player_data: Mapping[str, Any], quest_id: str) -> bool:
    return bool(_quest_state(player_data, quest_id).get("completed", False))


def _quest_started(player_data: Mapping[str, Any], quest_id: str) -> bool:
    state = _quest_state(player_data, quest_id)
    return bool(
        state.get("completed", False)
        or state.get("started", False)
        or _int(state.get("progress")) > 0
    )


def _carried(player_data: Mapping[str, Any], item_name: str) -> int:
    inventory = player_data.get("inventory")
    return _int(inventory.get(item_name)) if isinstance(inventory, Mapping) else 0


def chebyshev_distance_pure(left: TreasureSite, right: TreasureSite) -> int:
    """The period metric: diagonal steps count, obstacles do not."""
    return max(abs(left.x - right.x), abs(left.y - right.y))


def default_enchanted_key_state_pure() -> dict[str, Any]:
    return {
        "version": ENCHANTED_KEY_STATE_VERSION,
        "site_order": [],
        "found": 0,
        "selected_site_id": "",
        "last_distance": -1,
        "last_result": "",
    }


def sanitize_enchanted_key_state_pure(raw: Any) -> dict[str, Any]:
    defaults = default_enchanted_key_state_pure()
    source = raw if isinstance(raw, Mapping) else {}
    raw_order = source.get("site_order")
    order = (
        [
            site_id
            for site_id in dict.fromkeys(str(value) for value in raw_order)
            if site_id in _SITES_BY_ID
        ]
        if isinstance(raw_order, (list, tuple))
        else []
    )
    # A partial or duplicated order would silently shorten the hunt, so it is
    # dropped rather than patched.
    if len(order) != len(ENCHANTED_KEY_SITE_IDS):
        order = []
    found = min(len(ENCHANTED_KEY_SITE_IDS), _int(source.get("found")))
    if not order:
        found = 0
    selected = str(source.get("selected_site_id", ""))
    if selected not in set(order[found:] if order else ENCHANTED_KEY_SITE_IDS):
        selected = ""
    return {
        **defaults,
        "site_order": order,
        "found": found,
        "selected_site_id": selected,
        "last_distance": max(-1, _int(source.get("last_distance"), -1, minimum=-1)),
        "last_result": str(source.get("last_result", ""))[:280],
    }


def _found_ids(state: Mapping[str, Any]) -> tuple[str, ...]:
    order = list(state.get("site_order") or [])
    return tuple(order[: _int(state.get("found"))])


def enchanted_key_roster_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], ...]:
    state = sanitize_enchanted_key_state_pure(player_data.get("enchanted_key"))
    found = set(_found_ids(state))
    selected = str(state["selected_site_id"])
    return tuple(
        {
            "id": site.id,
            "display_name": site.display_name,
            "detail": site.detail,
            "rewards": site.rewards,
            "found": site.id in found,
            "selected": site.id == selected,
        }
        for site in ENCHANTED_KEY_SITES
    )


def enchanted_key_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_enchanted_key_state_pure(player_data.get("enchanted_key"))
    quest_done = _quest_complete(player_data, ENCHANTED_KEY_QUEST_ID)
    complete = state["found"] >= len(ENCHANTED_KEY_SITE_IDS)
    has_key = _carried(player_data, ENCHANTED_KEY_ITEM) > 0
    has_spade = _carried(player_data, ENCHANTED_KEY_SPADE) > 0

    missing: list[str] = []
    if not quest_done:
        missing.append("Complete Making History")
    elif not has_key and not complete:
        missing.append(f"Carry the {ENCHANTED_KEY_ITEM}")
    if not has_spade and not complete:
        missing.append(f"Carry a {ENCHANTED_KEY_SPADE} to dig")

    roster = enchanted_key_roster_pure(player_data)
    selected = next((row for row in roster if row["selected"]), None)
    can_replace = bool(
        quest_done
        and not complete
        and not has_key
        and not _quest_started(
            player_data,
            ENCHANTED_KEY_REPLACEMENT_BLOCKING_QUEST_ID,
        )
    )
    return {
        **state,
        "quest_complete": quest_done,
        "has_key": has_key,
        "has_spade": has_spade,
        "requirements_met": not missing,
        "missing_requirements": tuple(missing),
        "complete": complete,
        "roster": roster,
        "selected": selected,
        "remaining": len(ENCHANTED_KEY_SITE_IDS) - state["found"],
        "total_sites": len(ENCHANTED_KEY_SITE_IDS),
        # The panel renders these and never re-derives them.
        "can_review": bool(not missing and not complete and selected is not None),
        "selectable_site_ids": tuple(
            row["id"]
            for row in roster
            if not row["found"] and not missing and not complete
        ),
        "replacement_visible": can_replace,
        "replacement_enabled": bool(
            can_replace
            and _carried(player_data, "Coins") >= ENCHANTED_KEY_REPLACEMENT_COST
        ),
        "replacement_cost": ENCHANTED_KEY_REPLACEMENT_COST,
    }


def apply_enchanted_key_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the hunt state is rebuilt rather than written through.
    data = dict(player_data)
    state = sanitize_enchanted_key_state_pure(data.get("enchanted_key"))
    data["enchanted_key"] = state
    payload = payload if isinstance(payload, Mapping) else {}

    if action_id == "select_site":
        site_id = str(payload.get("site_id", ""))
        row = next(
            (row for row in enchanted_key_roster_pure(data) if row["id"] == site_id),
            None,
        )
        if row is None or row["found"]:
            return data, False, {
                "reason": "Choose a treasure site you have not dug up yet."
            }
        state["selected_site_id"] = site_id
        data["enchanted_key"] = state
        return data, True, {
            "site_id": site_id,
            "message": f"Heading for {row['display_name']}.",
        }

    if action_id == "replace_key":
        view = enchanted_key_view_pure(data)
        if not view["replacement_visible"]:
            return data, False, {
                "reason": "Erin only replaces a lost key before Meeting History."
            }
        if not view["replacement_enabled"]:
            return data, False, {
                "reason": (
                    f"Erin wants {ENCHANTED_KEY_REPLACEMENT_COST:,} coins for a "
                    "replacement key."
                )
            }
        inventory = dict(data.get("inventory", {}) or {})
        inventory["Coins"] = _int(inventory.get("Coins")) - ENCHANTED_KEY_REPLACEMENT_COST
        inventory[ENCHANTED_KEY_ITEM] = _int(inventory.get(ENCHANTED_KEY_ITEM)) + 1
        data["inventory"] = inventory
        state["last_distance"] = -1
        state["last_result"] = (
            f"Erin sold you a replacement {ENCHANTED_KEY_ITEM} for "
            f"{ENCHANTED_KEY_REPLACEMENT_COST:,} coins."
        )
        data["enchanted_key"] = state
        return data, True, {"message": state["last_result"]}

    return data, False, {"reason": "Unknown Enchanted key command."}


def _shuffled_order(rng) -> list[str]:
    """Fremennik Province first, then the rest in a per-save random order."""
    rest = list(ENCHANTED_KEY_SITE_IDS[1:])
    for index in range(len(rest) - 1, 0, -1):
        try:
            roll = float(rng())
        except (TypeError, ValueError, OverflowError):
            roll = 0.0
        swap = min(index, max(0, int(roll * (index + 1))))
        rest[index], rest[swap] = rest[swap], rest[index]
    return [ENCHANTED_KEY_SITE_IDS[0], *rest]


def apply_enchanted_key_review_pure(
    player_data: Mapping[str, Any],
    rng,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the hunt state and inventory are rebuilt, not written
    # through.
    data = dict(player_data)
    state = sanitize_enchanted_key_state_pure(data.get("enchanted_key"))
    data["enchanted_key"] = state
    view = enchanted_key_view_pure(data)
    if not view["can_review"]:
        if view["complete"]:
            reason = "The enchanted key melted after the last treasure."
        elif not view["requirements_met"]:
            reason = "; ".join(view["missing_requirements"]) + "."
        else:
            reason = "Choose a treasure site to search first."
        return data, False, {"reason": reason}

    if not state["site_order"]:
        state["site_order"] = _shuffled_order(rng)
    target = _SITES_BY_ID[state["site_order"][state["found"]]]
    searched = _SITES_BY_ID[state["selected_site_id"]]
    distance = chebyshev_distance_pure(searched, target)
    reading = enchanted_key_temperature_pure(distance)

    if distance > ENCHANTED_KEY_DIG_DISTANCE:
        previous = int(state["last_distance"])
        relation = (
            ""
            if previous < 0
            else ENCHANTED_KEY_WARMER
            if distance < previous
            else ENCHANTED_KEY_COLDER
            if distance > previous
            else ENCHANTED_KEY_SAME
        )
        state["last_distance"] = distance
        state["last_result"] = (
            f"{searched.display_name}: {reading}"
            + (f" {relation}" if relation else "")
        )
        data["enchanted_key"] = state
        return data, True, {
            "site_id": searched.id,
            "dug": False,
            "reading": reading,
            "relation": relation,
            "status": state["last_result"],
        }

    inventory = dict(data.get("inventory", {}) or {})
    for item_name, quantity in target.rewards:
        inventory[item_name] = _int(inventory.get(item_name)) + int(quantity)
    state["found"] += 1
    state["selected_site_id"] = ""
    state["last_distance"] = -1
    melted = state["found"] >= len(ENCHANTED_KEY_SITE_IDS)
    if melted:
        inventory[ENCHANTED_KEY_ITEM] = max(
            0,
            _int(inventory.get(ENCHANTED_KEY_ITEM)) - 1,
        )
    data["inventory"] = inventory
    state["last_result"] = (
        f"{reading} You dig up the {target.display_name} treasure: "
        + ", ".join(f"{quantity} {name}" for name, quantity in target.rewards)
        + (" The enchanted key melts away." if melted else "")
    )
    data["enchanted_key"] = state
    return data, True, {
        "site_id": target.id,
        "dug": True,
        "reading": reading,
        "relation": "",
        "rewards": target.rewards,
        "found": state["found"],
        "melted": melted,
        "outcome": state["last_result"] if melted else "",
        "status": state["last_result"],
    }


def enchanted_key_can_review_pure(player_data: Mapping[str, Any]) -> bool:
    return bool(enchanted_key_view_pure(player_data)["can_review"])


__all__ = [
    "ENCHANTED_KEY_ACTIVITY_ID",
    "apply_enchanted_key_command_pure",
    "apply_enchanted_key_review_pure",
    "chebyshev_distance_pure",
    "default_enchanted_key_state_pure",
    "enchanted_key_can_review_pure",
    "enchanted_key_roster_pure",
    "enchanted_key_view_pure",
    "sanitize_enchanted_key_state_pure",
]
