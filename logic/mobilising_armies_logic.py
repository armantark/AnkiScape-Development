"""Pure Mobilising Armies investment, scenario, rank, and Officer Tower logic.

A period scenario runs thirty minutes of real time. Here it runs eighteen review
beats, and one productive beat is one squad order, which keeps the sourced
ten-order rank threshold a gate the player can actually miss. Everything else —
the credit formulas, the rank ladder, the unlock chain, the shop — is the period
rule applied unchanged.
"""

from __future__ import annotations

import copy
from collections.abc import Mapping, Sequence
from typing import Any

from ..data.item_values import ITEM_VALUES
from ..data.mobilising_armies_data import (
    MOBILISING_ARMIES_ACTIVITY_ID,
    MOBILISING_ARMIES_END_ELIMINATION_PCT,
    MOBILISING_ARMIES_END_LOSS_PCT,
    MOBILISING_ARMIES_END_PRIMARY_PCT,
    MOBILISING_ARMIES_EXPLORE_HEAL_LIFEPOINTS,
    MOBILISING_ARMIES_EXPLORE_LOOT,
    MOBILISING_ARMIES_EXPLORE_LOOT_CHANCE,
    MOBILISING_ARMIES_EXPLORE_NEGATIVE_COMBAT_LOSS,
    MOBILISING_ARMIES_EXPLORE_POSITIVE_CHANCE,
    MOBILISING_ARMIES_FLOORS,
    MOBILISING_ARMIES_FLOORS_BY_ID,
    MOBILISING_ARMIES_FORMATION_IDS,
    MOBILISING_ARMIES_FORMATION_RANKS,
    MOBILISING_ARMIES_FORMATIONS,
    MOBILISING_ARMIES_HOARD_GAIN_ON_KILL,
    MOBILISING_ARMIES_HOARD_LOSS_ON_ATTACK,
    MOBILISING_ARMIES_HOARD_LOSS_ON_SQUAD_DEATH,
    MOBILISING_ARMIES_IMBUE_RINGS,
    MOBILISING_ARMIES_IMBUE_RINGS_BY_ITEM,
    MOBILISING_ARMIES_INVESTMENT_CREDIT_CAP,
    MOBILISING_ARMIES_KIT_REFUND_PCT,
    MOBILISING_ARMIES_LOCATOR_REFUND_PCT,
    MOBILISING_ARMIES_LOCATOR_SKILL_IDS,
    MOBILISING_ARMIES_LOCATOR_SKILLS,
    MOBILISING_ARMIES_LOCATOR_TARGET_KEYS,
    MOBILISING_ARMIES_LOCATORS,
    MOBILISING_ARMIES_LOCATORS_BY_ITEM,
    MOBILISING_ARMIES_OPPONENT_ORDER_DAMAGE,
    MOBILISING_ARMIES_ORDER_IDS,
    MOBILISING_ARMIES_ORDERS,
    MOBILISING_ARMIES_PREFIXES,
    MOBILISING_ARMIES_QUEST_KITS,
    MOBILISING_ARMIES_QUEST_KITS_BY_ITEM,
    MOBILISING_ARMIES_RESCUE_STEAL_PER_ORDER,
    MOBILISING_ARMIES_RACE_BEATS,
    MOBILISING_ARMIES_RANK_ACTION_MINIMUM,
    MOBILISING_ARMIES_RANK_FOR_PARTICIPATION,
    MOBILISING_ARMIES_RANK_FOR_WIN,
    MOBILISING_ARMIES_RANK_HOURLY_CAP,
    MOBILISING_ARMIES_RANK_MINIMUM_BEATS,
    MOBILISING_ARMIES_RANK_WINDOW_BEATS,
    MOBILISING_ARMIES_SCENARIO_BEATS,
    MOBILISING_ARMIES_SCENARIO_IDS,
    MOBILISING_ARMIES_SCENARIOS,
    MOBILISING_ARMIES_SCENARIOS_BY_ID,
    MOBILISING_ARMIES_SIEGE_ASSAULT_WALL_DAMAGE,
    MOBILISING_ARMIES_SIEGE_CATAPULT_PARTS,
    MOBILISING_ARMIES_SIEGE_ROCKS_PER_SHOT,
    MOBILISING_ARMIES_SIEGE_ROUTE_IDS,
    MOBILISING_ARMIES_SIEGE_ROUTES,
    MOBILISING_ARMIES_SIEGE_SHOT_WALL_DAMAGE,
    MOBILISING_ARMIES_SIEGE_TOWER_DAMAGE,
    MOBILISING_ARMIES_SPECIAL_UNIT_CAP,
    MOBILISING_ARMIES_SPECIAL_UNIT_CREDIT_COST,
    MOBILISING_ARMIES_SPECIAL_UNIT_IDS,
    MOBILISING_ARMIES_SPECIAL_UNITS,
    MOBILISING_ARMIES_SPECIAL_UNITS_BY_ID,
    MOBILISING_ARMIES_SPOILS,
    MOBILISING_ARMIES_SPOILS_CHOICES,
    MOBILISING_ARMIES_SPOILS_OFFER_SIZE,
    MOBILISING_ARMIES_SQUAD_CONTRACT_CAP,
    MOBILISING_ARMIES_SQUAD_CREDIT_COST,
    MOBILISING_ARMIES_SQUAD_IDS,
    MOBILISING_ARMIES_SQUAD_ORDER_DAMAGE,
    MOBILISING_ARMIES_SQUADS,
    MOBILISING_ARMIES_SQUADS_BY_ID,
    MOBILISING_ARMIES_SQUADS_REQUIRED,
    MOBILISING_ARMIES_TRIANGLE_MULTIPLIER,
    MOBILISING_ARMIES_UNIFORM_REFUND_PCT,
    MOBILISING_ARMIES_UNIFORMS,
    MOBILISING_ARMIES_UNIFORMS_BY_ITEM,
    mobilising_armies_investment_credits_pure,
    mobilising_armies_rank_band_pure,
    mobilising_armies_reward_credits_pure,
)


MOBILISING_ARMIES_STATE_VERSION = 1
_RACES = tuple(sorted({squad.race for squad in MOBILISING_ARMIES_SQUADS}))
_MAX_SQUAD_LIFEPOINTS = max(squad.lifepoints for squad in MOBILISING_ARMIES_SQUADS)
_SPOILS_BY_FLOOR_ITEM = {
    floor_id: {item_name: quantity for item_name, quantity in rows}
    for floor_id, rows in MOBILISING_ARMIES_SPOILS.items()
}
_REWARD_COSTS = {
    **{kit.item_name: (kit.floor, kit.credit_cost, MOBILISING_ARMIES_KIT_REFUND_PCT)
       for kit in MOBILISING_ARMIES_QUEST_KITS},
    **{locator.item_name: (locator.floor, locator.credit_cost, MOBILISING_ARMIES_LOCATOR_REFUND_PCT)
       for locator in MOBILISING_ARMIES_LOCATORS},
    **{piece.item_name: (piece.floor, piece.credit_cost, MOBILISING_ARMIES_UNIFORM_REFUND_PCT)
       for piece in MOBILISING_ARMIES_UNIFORMS},
    # The sources state refund rates only for quest kits, locators, and uniforms,
    # so imbued rings are sold and never bought back.
    **{ring.item_name: (ring.floor, ring.credit_cost, 0)
       for ring in MOBILISING_ARMIES_IMBUE_RINGS},
}


def _int(value: Any, default: int = 0, *, maximum: int = 2_147_483_647) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(0, min(parsed, maximum))


def _rng_value(rng) -> float:
    try:
        return max(0.0, min(0.999999999, float(rng())))
    except (TypeError, ValueError, StopIteration):
        return 0.5


def _pick(rng, options: Sequence[Any]) -> Any:
    return options[int(_rng_value(rng) * len(options))] if options else None


def _inventory(data: Mapping[str, Any]) -> Mapping[str, Any]:
    inventory = data.get("inventory")
    return inventory if isinstance(inventory, Mapping) else {}


def _held(data: Mapping[str, Any], item_name: str) -> int:
    return _int(_inventory(data).get(item_name))


def default_mobilising_armies_state_pure() -> dict[str, Any]:
    return {
        "mobilising_armies": {},
        "mobilising_armies_policy": {
            "scenario": MOBILISING_ARMIES_SCENARIO_IDS[0],
            "formation": MOBILISING_ARMIES_FORMATION_IDS[0],
            "order": MOBILISING_ARMIES_ORDER_IDS[0],
            "siege_route": MOBILISING_ARMIES_SIEGE_ROUTE_IDS[0],
            "squad": MOBILISING_ARMIES_SQUAD_IDS[0],
            "locator_skill": MOBILISING_ARMIES_LOCATOR_SKILL_IDS[0],
            "investment": 0,
        },
        "mobilising_armies_investment_credits": 0,
        "mobilising_armies_reward_credits": 0,
        "mobilising_armies_rank": 0,
        "mobilising_armies_squads": {},
        "mobilising_armies_special_units": {},
        "mobilising_armies_scenarios_played": [],
        "mobilising_armies_prefix": "",
        "mobilising_armies_rank_window": {"beats": 0, "points": 0},
        "mobilising_armies_spoils_offer": {},
        "mobilising_armies_games_played": 0,
        "mobilising_armies_wins": 0,
        "mobilising_armies_losses": 0,
        "mobilising_armies_last_result": "",
    }


def _sanitize_policy(raw: Any) -> dict[str, Any]:
    source = raw if isinstance(raw, Mapping) else {}

    def _one_of(key: str, options: Sequence[str]) -> str:
        value = str(source.get(key, options[0]))
        return value if value in options else options[0]

    return {
        "scenario": _one_of("scenario", MOBILISING_ARMIES_SCENARIO_IDS),
        "formation": _one_of("formation", MOBILISING_ARMIES_FORMATION_IDS),
        "order": _one_of("order", MOBILISING_ARMIES_ORDER_IDS),
        "siege_route": _one_of("siege_route", MOBILISING_ARMIES_SIEGE_ROUTE_IDS),
        "squad": _one_of("squad", MOBILISING_ARMIES_SQUAD_IDS),
        "locator_skill": _one_of("locator_skill", MOBILISING_ARMIES_LOCATOR_SKILL_IDS),
        "investment": _int(
            source.get("investment"), maximum=MOBILISING_ARMIES_INVESTMENT_CREDIT_CAP
        ),
    }


def _sanitize_counts(raw: Any, ids: Sequence[str], cap: int) -> dict[str, int]:
    source = raw if isinstance(raw, Mapping) else {}
    counts: dict[str, int] = {}
    remaining = cap
    for key in ids:
        held = min(remaining, _int(source.get(key), maximum=cap))
        if held:
            counts[key] = held
            remaining -= held
    return counts


def _sanitize_army(raw: Any, *, rival: bool) -> list[dict[str, Any]]:
    rows = raw if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)) else ()
    army: list[dict[str, Any]] = []
    for entry in list(rows)[:MOBILISING_ARMIES_SQUADS_REQUIRED]:
        if not isinstance(entry, Mapping):
            continue
        squad_id = str(entry.get("id", ""))
        squad = MOBILISING_ARMIES_SQUADS_BY_ID.get(squad_id)
        if squad is None:
            continue
        row = {
            "id": squad_id,
            "lifepoints": _int(
                entry.get("lifepoints", squad.lifepoints),
                squad.lifepoints,
                maximum=squad.lifepoints,
            ),
        }
        if not rival:
            row["combat_level"] = _int(
                entry.get("combat_level", squad.combat_level),
                squad.combat_level,
                maximum=squad.combat_level,
            )
        army.append(row)
    return army


def _sanitize_session(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}
    scenario_id = str(raw.get("scenario", ""))
    scenario = MOBILISING_ARMIES_SCENARIOS_BY_ID.get(scenario_id)
    squads = _sanitize_army(raw.get("squads"), rival=False)
    rivals = _sanitize_army(raw.get("rivals"), rival=True)
    if scenario is None or not squads or not rivals:
        return {}
    formation = str(raw.get("formation", MOBILISING_ARMIES_FORMATION_IDS[0]))
    order = str(raw.get("order", MOBILISING_ARMIES_ORDER_IDS[0]))
    route = str(raw.get("siege_route", MOBILISING_ARMIES_SIEGE_ROUTE_IDS[0]))
    return {
        "version": MOBILISING_ARMIES_STATE_VERSION,
        "scenario": scenario_id,
        "formation": formation if formation in MOBILISING_ARMIES_FORMATION_IDS else MOBILISING_ARMIES_FORMATION_IDS[0],
        "order": order if order in MOBILISING_ARMIES_ORDER_IDS else MOBILISING_ARMIES_ORDER_IDS[0],
        "siege_route": route if route in MOBILISING_ARMIES_SIEGE_ROUTE_IDS else MOBILISING_ARMIES_SIEGE_ROUTE_IDS[0],
        "investment": _int(raw.get("investment"), maximum=MOBILISING_ARMIES_INVESTMENT_CREDIT_CAP),
        "rank_modifier_pct": _int(raw.get("rank_modifier_pct"), 110, maximum=150),
        "beat": _int(raw.get("beat"), maximum=MOBILISING_ARMIES_SCENARIO_BEATS),
        "commands": _int(raw.get("commands"), maximum=MOBILISING_ARMIES_SCENARIO_BEATS),
        "objective": _int(raw.get("objective"), maximum=scenario.objective_target),
        "opponent_objective": _int(
            raw.get("opponent_objective"), maximum=scenario.objective_target
        ),
        "kills": _int(raw.get("kills"), maximum=MOBILISING_ARMIES_SQUADS_REQUIRED),
        "losses": _int(raw.get("losses"), maximum=MOBILISING_ARMIES_SQUADS_REQUIRED),
        "catapult_parts": _int(
            raw.get("catapult_parts"), maximum=MOBILISING_ARMIES_SIEGE_CATAPULT_PARTS
        ),
        "catapult_rocks": _int(
            raw.get("catapult_rocks"), maximum=MOBILISING_ARMIES_SIEGE_ROCKS_PER_SHOT
        ),
        "stalled": _int(raw.get("stalled"), maximum=MOBILISING_ARMIES_SCENARIO_BEATS),
        "shielded": _int(raw.get("shielded"), maximum=MOBILISING_ARMIES_SCENARIO_BEATS),
        "squads": squads,
        "rivals": rivals,
        "special_units": _sanitize_counts(
            raw.get("special_units"),
            MOBILISING_ARMIES_SPECIAL_UNIT_IDS,
            MOBILISING_ARMIES_SPECIAL_UNIT_CAP,
        ),
    }


def _sanitize_offer(raw: Any) -> dict[str, Any]:
    source = raw if isinstance(raw, Mapping) else {}
    floor_id = str(source.get("floor", ""))
    if floor_id not in _SPOILS_BY_FLOOR_ITEM:
        return {}
    offered = source.get("items")
    rows = offered if isinstance(offered, Sequence) and not isinstance(offered, (str, bytes)) else ()
    items = [
        str(name)
        for name in rows
        if str(name) in _SPOILS_BY_FLOOR_ITEM[floor_id]
    ][:MOBILISING_ARMIES_SPOILS_OFFER_SIZE]
    return {"floor": floor_id, "items": items} if items else {}


def sanitize_mobilising_armies_state_pure(
    player_data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = dict(player_data or {})
    session = _sanitize_session(source.get("mobilising_armies"))
    active = source.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if session and active_id not in {"", MOBILISING_ARMIES_ACTIVITY_ID}:
        session = {}
    played = source.get("mobilising_armies_scenarios_played")
    played_rows = played if isinstance(played, Sequence) and not isinstance(played, (str, bytes)) else ()
    prefix = str(source.get("mobilising_armies_prefix", "") or "")
    window = source.get("mobilising_armies_rank_window")
    window = window if isinstance(window, Mapping) else {}
    return {
        "mobilising_armies": session,
        "mobilising_armies_policy": _sanitize_policy(
            source.get("mobilising_armies_policy")
        ),
        "mobilising_armies_investment_credits": _int(
            source.get("mobilising_armies_investment_credits"),
            maximum=MOBILISING_ARMIES_INVESTMENT_CREDIT_CAP,
        ),
        "mobilising_armies_reward_credits": _int(
            source.get("mobilising_armies_reward_credits")
        ),
        "mobilising_armies_rank": _int(source.get("mobilising_armies_rank")),
        "mobilising_armies_squads": _sanitize_counts(
            source.get("mobilising_armies_squads"),
            MOBILISING_ARMIES_SQUAD_IDS,
            MOBILISING_ARMIES_SQUAD_CONTRACT_CAP,
        ),
        "mobilising_armies_special_units": _sanitize_counts(
            source.get("mobilising_armies_special_units"),
            MOBILISING_ARMIES_SPECIAL_UNIT_IDS,
            MOBILISING_ARMIES_SPECIAL_UNIT_CAP,
        ),
        "mobilising_armies_scenarios_played": [
            scenario_id
            for scenario_id in MOBILISING_ARMIES_SCENARIO_IDS
            if scenario_id in {str(row) for row in played_rows}
        ],
        "mobilising_armies_prefix": prefix if prefix in MOBILISING_ARMIES_PREFIXES else "",
        "mobilising_armies_rank_window": {
            "beats": _int(window.get("beats"), maximum=MOBILISING_ARMIES_RANK_WINDOW_BEATS),
            "points": _int(window.get("points"), maximum=MOBILISING_ARMIES_RANK_HOURLY_CAP),
        },
        "mobilising_armies_spoils_offer": _sanitize_offer(
            source.get("mobilising_armies_spoils_offer")
        ),
        "mobilising_armies_games_played": _int(
            source.get("mobilising_armies_games_played")
        ),
        "mobilising_armies_wins": _int(source.get("mobilising_armies_wins")),
        "mobilising_armies_losses": _int(source.get("mobilising_armies_losses")),
        "mobilising_armies_last_result": str(
            source.get("mobilising_armies_last_result", "") or ""
        )[:500],
    }


# --- Command centre ---------------------------------------------------------


def set_mobilising_armies_policy_pure(
    player_data: Mapping[str, Any], payload: Mapping[str, Any] | None
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the state block is rebuilt fresh and the inventory is
    # copied before it is spent.
    data = dict(player_data)
    state = sanitize_mobilising_armies_state_pure(data)
    candidate = dict(state["mobilising_armies_policy"])
    candidate.update(dict(payload or {}))
    policy = _sanitize_policy(candidate)
    rank = state["mobilising_armies_rank"]
    if MOBILISING_ARMIES_FORMATION_RANKS[policy["formation"]] > rank:
        return data, False, {
            "reason": (
                f"The {policy['formation']} formation needs rank "
                f"{MOBILISING_ARMIES_FORMATION_RANKS[policy['formation']]}."
            )
        }
    scenario = MOBILISING_ARMIES_SCENARIOS_BY_ID[policy["scenario"]]
    if scenario.unlocked_by and scenario.unlocked_by not in state[
        "mobilising_armies_scenarios_played"
    ]:
        unlock = MOBILISING_ARMIES_SCENARIOS_BY_ID[scenario.unlocked_by]
        return data, False, {
            "reason": f"Play a game of {unlock.display_name} first."
        }
    band = mobilising_armies_rank_band_pure(rank)
    if policy["investment"] > band.maximum_investment:
        return data, False, {
            "reason": f"Your rank caps the stake at {band.maximum_investment:,} credits."
        }
    if state["mobilising_armies"]:
        session = dict(state["mobilising_armies"])
        session["order"] = policy["order"]
        session["siege_route"] = policy["siege_route"]
        data.update(state)
        data["mobilising_armies"] = session
        data["mobilising_armies_policy"] = policy
        return data, True, {"message": "Squad orders updated.", "policy": policy}
    data.update(state)
    data["mobilising_armies_policy"] = policy
    return data, True, {"message": "Battle plan saved.", "policy": policy}


def invest_items_pure(
    player_data: Mapping[str, Any],
    item_name: str,
    quantity: int,
    *,
    item_values: Mapping[str, int],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_mobilising_armies_state_pure(data)
    if state["mobilising_armies"]:
        return data, False, {"reason": "Finish or forfeit the current scenario first."}
    name = str(item_name)
    wanted = _int(quantity)
    if wanted <= 0:
        return data, False, {"reason": "Choose how many items to invest."}
    held = _held(data, name)
    if held < wanted:
        return data, False, {"reason": f"You do not have {wanted} {name}."}
    per_item = mobilising_armies_investment_credits_pure(
        _int(item_values.get(name))
    )
    if per_item <= 0:
        return data, False, {"reason": f"Junior Cadet Mal will not take {name}."}
    credits_before = state["mobilising_armies_investment_credits"]
    credits_after = min(
        MOBILISING_ARMIES_INVESTMENT_CREDIT_CAP, credits_before + per_item * wanted
    )
    if credits_after == credits_before:
        return data, False, {
            "reason": (
                f"Your investment wallet is full at "
                f"{MOBILISING_ARMIES_INVESTMENT_CREDIT_CAP:,} credits."
            )
        }
    # Only invest as many items as the wallet can actually pay for.
    affordable = min(wanted, (credits_after - credits_before + per_item - 1) // per_item)
    credits_after = min(
        MOBILISING_ARMIES_INVESTMENT_CREDIT_CAP, credits_before + per_item * affordable
    )
    inventory = copy.deepcopy(dict(_inventory(data)))
    remaining = _int(inventory.get(name)) - affordable
    if remaining > 0:
        inventory[name] = remaining
    else:
        inventory.pop(name, None)
    data.update(state)
    data["inventory"] = inventory
    data["mobilising_armies_investment_credits"] = credits_after
    message = (
        f"Invested {affordable} {name} for "
        f"{credits_after - credits_before:,} investment credits."
    )
    data["mobilising_armies_last_result"] = message
    return data, True, {
        "message": message,
        "quantity": affordable,
        "credits": credits_after - credits_before,
    }


def _spend_investment_credits(
    data: dict[str, Any], state: Mapping[str, Any], amount: int
) -> None:
    data["mobilising_armies_investment_credits"] = (
        state["mobilising_armies_investment_credits"] - amount
    )


def recruit_squads_pure(
    player_data: Mapping[str, Any], squad_id: str, quantity: int
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_mobilising_armies_state_pure(data)
    if state["mobilising_armies"]:
        return data, False, {"reason": "Finish or forfeit the current scenario first."}
    squad = MOBILISING_ARMIES_SQUADS_BY_ID.get(str(squad_id))
    if squad is None:
        return data, False, {"reason": "Unknown mercenary squad."}
    wanted = _int(quantity)
    if wanted <= 0:
        return data, False, {"reason": "Choose how many squads to recruit."}
    contracts = dict(state["mobilising_armies_squads"])
    held = sum(contracts.values())
    room = MOBILISING_ARMIES_SQUAD_CONTRACT_CAP - held
    if room <= 0:
        return data, False, {
            "reason": f"You already hold {MOBILISING_ARMIES_SQUAD_CONTRACT_CAP} squad contracts."
        }
    hired = min(wanted, room)
    cost = hired * MOBILISING_ARMIES_SQUAD_CREDIT_COST
    if state["mobilising_armies_investment_credits"] < cost:
        return data, False, {"reason": f"Recruiting {hired} squads costs {cost:,} credits."}
    contracts[squad.id] = contracts.get(squad.id, 0) + hired
    data.update(state)
    data["mobilising_armies_squads"] = contracts
    _spend_investment_credits(data, state, cost)
    message = f"Recruited {hired} {squad.display_name} squads for {cost:,} credits."
    data["mobilising_armies_last_result"] = message
    return data, True, {"message": message, "quantity": hired, "cost": cost}


def buy_special_units_pure(
    player_data: Mapping[str, Any], unit_id: str, quantity: int
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_mobilising_armies_state_pure(data)
    if state["mobilising_armies"]:
        return data, False, {"reason": "Finish or forfeit the current scenario first."}
    unit = MOBILISING_ARMIES_SPECIAL_UNITS_BY_ID.get(str(unit_id))
    if unit is None:
        return data, False, {"reason": "Unknown special unit."}
    wanted = _int(quantity)
    if wanted <= 0:
        return data, False, {"reason": "Choose how many special units to buy."}
    units = dict(state["mobilising_armies_special_units"])
    room = MOBILISING_ARMIES_SPECIAL_UNIT_CAP - sum(units.values())
    if room <= 0:
        return data, False, {
            "reason": f"You already hold {MOBILISING_ARMIES_SPECIAL_UNIT_CAP} special units."
        }
    bought = min(wanted, room)
    cost = bought * MOBILISING_ARMIES_SPECIAL_UNIT_CREDIT_COST
    if state["mobilising_armies_investment_credits"] < cost:
        return data, False, {"reason": f"Buying {bought} {unit.display_name} costs {cost:,} credits."}
    units[unit.id] = units.get(unit.id, 0) + bought
    data.update(state)
    data["mobilising_armies_special_units"] = units
    _spend_investment_credits(data, state, cost)
    message = f"Signed contracts for {bought} {unit.display_name} for {cost:,} credits."
    data["mobilising_armies_last_result"] = message
    return data, True, {"message": message, "quantity": bought, "cost": cost}


# --- Scenario ---------------------------------------------------------------


def _entry_reasons(data: Mapping[str, Any], state: Mapping[str, Any]) -> tuple[str, ...]:
    reasons: list[str] = []
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if active_id and active_id != MOBILISING_ARMIES_ACTIVITY_ID:
        reasons.append("Finish the active persistent activity.")
    policy = state["mobilising_armies_policy"]
    contracts = sum(state["mobilising_armies_squads"].values())
    if contracts < MOBILISING_ARMIES_SQUADS_REQUIRED:
        reasons.append(
            f"Recruit {MOBILISING_ARMIES_SQUADS_REQUIRED - contracts} more mercenary squads."
        )
    scenario = MOBILISING_ARMIES_SCENARIOS_BY_ID[policy["scenario"]]
    if scenario.unlocked_by and scenario.unlocked_by not in state[
        "mobilising_armies_scenarios_played"
    ]:
        unlock = MOBILISING_ARMIES_SCENARIOS_BY_ID[scenario.unlocked_by]
        reasons.append(f"Play a game of {unlock.display_name} to unlock {scenario.display_name}.")
    band = mobilising_armies_rank_band_pure(state["mobilising_armies_rank"])
    if policy["investment"] > band.maximum_investment:
        reasons.append(f"Your rank caps the stake at {band.maximum_investment:,} credits.")
    if state["mobilising_armies_investment_credits"] < policy["investment"]:
        reasons.append("You cannot cover that stake.")
    return tuple(reasons)


def enter_mobilising_armies_pure(
    player_data: Mapping[str, Any],
    rng,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_mobilising_armies_state_pure(data)
    if state["mobilising_armies"]:
        return data, False, {"reason": "A scenario is already under way."}
    candidate = dict(state["mobilising_armies_policy"])
    candidate.update(dict(payload or {}))
    policy = _sanitize_policy(candidate)
    if MOBILISING_ARMIES_FORMATION_RANKS[policy["formation"]] > state["mobilising_armies_rank"]:
        policy["formation"] = MOBILISING_ARMIES_FORMATION_IDS[0]
    probe = {**state, "mobilising_armies_policy": policy}
    reasons = _entry_reasons(data, probe)
    if reasons:
        return data, False, {"reason": reasons[0], "entry_reasons": reasons}

    squads: list[dict[str, Any]] = []
    for squad_id, count in state["mobilising_armies_squads"].items():
        squad = MOBILISING_ARMIES_SQUADS_BY_ID[squad_id]
        squads.extend(
            {"id": squad.id, "lifepoints": squad.lifepoints, "combat_level": squad.combat_level}
            for _index in range(count)
        )
    # The rival army fields one race drawn on entry: the source pits a player
    # against other players' armies, whose composition AnkiScape has no way to
    # know, so one drawn race stands in for the opposing commander's choice.
    rival_race = _pick(rng, _RACES)
    rival_class = "heavy" if _rng_value(rng) < 0.5 else "light"
    rival_squad = next(
        squad
        for squad in MOBILISING_ARMIES_SQUADS
        if squad.race == rival_race and squad.squad_class == rival_class
    )
    band = mobilising_armies_rank_band_pure(state["mobilising_armies_rank"])
    data.update(state)
    data["mobilising_armies_policy"] = policy
    data["mobilising_armies_squads"] = {}
    data["mobilising_armies_special_units"] = {}
    _spend_investment_credits(data, state, policy["investment"])
    data["mobilising_armies"] = {
        "version": MOBILISING_ARMIES_STATE_VERSION,
        "scenario": policy["scenario"],
        "formation": policy["formation"],
        "order": policy["order"],
        "siege_route": policy["siege_route"],
        "investment": policy["investment"],
        "rank_modifier_pct": band.reward_modifier_pct,
        "beat": 0,
        "commands": 0,
        "objective": 0,
        "opponent_objective": 0,
        "kills": 0,
        "losses": 0,
        "catapult_parts": 0,
        "catapult_rocks": 0,
        "stalled": 0,
        "shielded": 0,
        "squads": squads,
        "rivals": [
            {"id": rival_squad.id, "lifepoints": rival_squad.lifepoints}
            for _index in range(MOBILISING_ARMIES_SQUADS_REQUIRED)
        ],
        "special_units": dict(state["mobilising_armies_special_units"]),
    }
    data["activity_session"] = {"active_id": MOBILISING_ARMIES_ACTIVITY_ID}
    data["current_utility"] = MOBILISING_ARMIES_ACTIVITY_ID
    scenario = MOBILISING_ARMIES_SCENARIOS_BY_ID[policy["scenario"]]
    message = (
        f"{scenario.display_name} begins against a {rival_squad.display_name} army · "
        f"{policy['investment']:,} credits staked · "
        f"{MOBILISING_ARMIES_SCENARIO_BEATS} orders remain"
    )
    data["mobilising_armies_last_result"] = message
    return data, True, {"message": message, "rival": rival_squad.id}


def _living(army: Sequence[Mapping[str, Any]]) -> list[int]:
    return [index for index, squad in enumerate(army) if int(squad["lifepoints"]) > 0]


def _order_damage(attacker_id: str, defender_id: str, base: int) -> int:
    attacker = MOBILISING_ARMIES_SQUADS_BY_ID[attacker_id]
    defender = MOBILISING_ARMIES_SQUADS_BY_ID[defender_id]
    if MOBILISING_ARMIES_RACE_BEATS[attacker.race] == defender.race:
        return int(base * MOBILISING_ARMIES_TRIANGLE_MULTIPLIER)
    return base


def _attack_rival(session: dict[str, Any], rng) -> dict[str, Any]:
    own = _living(session["squads"])
    rivals = _living(session["rivals"])
    if not own or not rivals:
        return {"attacked": False}
    attacker = session["squads"][own[int(_rng_value(rng) * len(own))]]
    target_index = rivals[0]
    target = session["rivals"][target_index]
    damage = _order_damage(
        str(attacker["id"]), str(target["id"]), MOBILISING_ARMIES_SQUAD_ORDER_DAMAGE
    )
    target["lifepoints"] = max(0, int(target["lifepoints"]) - damage)
    killed = int(target["lifepoints"]) <= 0
    if killed:
        session["kills"] += 1
    return {"attacked": True, "damage": damage, "killed": killed}


def _advance_objective(session: dict[str, Any], rng) -> dict[str, Any]:
    scenario = MOBILISING_ARMIES_SCENARIOS_BY_ID[str(session["scenario"])]
    if scenario.id == "conflict":
        # Conflict has one objective and it is elimination, so its objective
        # order is the attack order.
        result = _attack_rival(session, rng)
        session["objective"] = int(session["kills"])
        return {"progress": "eliminate", **result}
    if scenario.id == "siege":
        if str(session["siege_route"]) == "assault":
            own = _living(session["squads"])
            if own:
                squad = session["squads"][own[0]]
                squad["lifepoints"] = max(
                    0, int(squad["lifepoints"]) - MOBILISING_ARMIES_SIEGE_TOWER_DAMAGE
                )
                if int(squad["lifepoints"]) <= 0:
                    session["losses"] += 1
            session["objective"] = min(
                scenario.objective_target,
                int(session["objective"]) + MOBILISING_ARMIES_SIEGE_ASSAULT_WALL_DAMAGE,
            )
            return {"progress": "assault", "wall": int(session["objective"])}
        if int(session["catapult_parts"]) < MOBILISING_ARMIES_SIEGE_CATAPULT_PARTS:
            session["catapult_parts"] += 1
            return {"progress": "catapult_part", "parts": int(session["catapult_parts"])}
        session["catapult_rocks"] += 1
        if int(session["catapult_rocks"]) >= MOBILISING_ARMIES_SIEGE_ROCKS_PER_SHOT:
            session["catapult_rocks"] = 0
            session["objective"] = min(
                scenario.objective_target,
                int(session["objective"]) + MOBILISING_ARMIES_SIEGE_SHOT_WALL_DAMAGE,
            )
            return {"progress": "catapult_shot", "wall": int(session["objective"])}
        return {"progress": "catapult_rock", "rocks": int(session["catapult_rocks"])}
    session["objective"] = min(
        scenario.objective_target, int(session["objective"]) + scenario.objective_per_order
    )
    return {"progress": scenario.objective, "objective": int(session["objective"])}


def _explore(session: dict[str, Any], data: dict[str, Any], rng) -> dict[str, Any]:
    own = _living(session["squads"])
    if not own:
        return {"explored": False}
    squad_row = session["squads"][own[int(_rng_value(rng) * len(own))]]
    squad = MOBILISING_ARMIES_SQUADS_BY_ID[str(squad_row["id"])]
    result: dict[str, Any] = {"explored": True, "race": squad.race}
    if _rng_value(rng) < MOBILISING_ARMIES_EXPLORE_LOOT_CHANCE:
        pool = MOBILISING_ARMIES_EXPLORE_LOOT[squad.race]
        item_name = _pick(rng, pool)
        inventory = copy.deepcopy(dict(_inventory(data)))
        inventory[item_name] = _int(inventory.get(item_name)) + 1
        data["inventory"] = inventory
        result["loot"] = item_name
    elif _rng_value(rng) < MOBILISING_ARMIES_EXPLORE_POSITIVE_CHANCE:
        squad_row["lifepoints"] = min(
            squad.lifepoints,
            int(squad_row["lifepoints"]) + MOBILISING_ARMIES_EXPLORE_HEAL_LIFEPOINTS,
        )
        result["positive"] = MOBILISING_ARMIES_EXPLORE_HEAL_LIFEPOINTS
    else:
        squad_row["combat_level"] = max(
            1,
            int(squad_row["combat_level"]) - MOBILISING_ARMIES_EXPLORE_NEGATIVE_COMBAT_LOSS,
        )
        result["negative"] = MOBILISING_ARMIES_EXPLORE_NEGATIVE_COMBAT_LOSS
    return result


def _opponent_beat(session: dict[str, Any], rng) -> dict[str, Any]:
    scenario = MOBILISING_ARMIES_SCENARIOS_BY_ID[str(session["scenario"])]
    if int(session["shielded"]) > 0:
        session["shielded"] -= 1
        return {"opponent": "blocked"}
    if scenario.objective != "squads_defeated":
        session["opponent_objective"] = min(
            scenario.objective_target,
            int(session["opponent_objective"]) + scenario.opponent_per_beat,
        )
    result: dict[str, Any] = {"opponent": "advanced"}
    own = _living(session["squads"])
    rivals = _living(session["rivals"])
    if own and rivals:
        target = session["squads"][own[0]]
        target["lifepoints"] = max(
            0,
            int(target["lifepoints"])
            - _order_damage(
                str(session["rivals"][rivals[0]]["id"]),
                str(target["id"]),
                MOBILISING_ARMIES_OPPONENT_ORDER_DAMAGE,
            ),
        )
        if int(target["lifepoints"]) <= 0:
            session["losses"] += 1
            result["squad_lost"] = True
            if scenario.id == "hoard" and str(session["order"]) == "objective":
                session["objective"] = max(
                    0, int(session["objective"]) - MOBILISING_ARMIES_HOARD_LOSS_ON_SQUAD_DEATH
                )
                result["gold_lost"] = MOBILISING_ARMIES_HOARD_LOSS_ON_SQUAD_DEATH
        elif (
            scenario.id == "hoard"
            and str(session["order"]) == "objective"
            and _rng_value(rng) < 0.5
        ):
            session["objective"] = max(
                0, int(session["objective"]) - MOBILISING_ARMIES_HOARD_LOSS_ON_ATTACK
            )
            result["gold_lost"] = MOBILISING_ARMIES_HOARD_LOSS_ON_ATTACK
    if scenario.objective == "squads_defeated":
        # Conflict's only objective is elimination, so the rival's meter is the
        # count of the player's squads it has actually destroyed.
        session["opponent_objective"] = int(session["losses"])
    return result


def deploy_special_unit_pure(
    player_data: Mapping[str, Any], unit_id: str, rng
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_mobilising_armies_state_pure(data)
    session = copy.deepcopy(state["mobilising_armies"])
    if not session:
        return data, False, {"reason": "Enter a scenario before deploying special units."}
    unit = MOBILISING_ARMIES_SPECIAL_UNITS_BY_ID.get(str(unit_id))
    if unit is None:
        return data, False, {"reason": "Unknown special unit."}
    units = dict(session["special_units"])
    if _int(units.get(unit.id)) <= 0:
        return data, False, {"reason": f"You brought no {unit.display_name}."}
    units[unit.id] = _int(units[unit.id]) - 1
    if not units[unit.id]:
        units.pop(unit.id)
    session["special_units"] = units
    result: dict[str, Any] = {"unit": unit.id}
    if unit.maximum_damage > 0:
        damage = unit.minimum_damage + int(
            _rng_value(rng) * (unit.maximum_damage - unit.minimum_damage + 1)
        )
        hit_count = 1 if unit.targets == "single" else 2
        for index in _living(session["rivals"])[:hit_count]:
            target = session["rivals"][index]
            target["lifepoints"] = max(0, int(target["lifepoints"]) - damage)
            if int(target["lifepoints"]) <= 0:
                session["kills"] += 1
        if unit.friendly_fire:
            for index in _living(session["squads"])[:hit_count]:
                own = session["squads"][index]
                own["lifepoints"] = max(0, int(own["lifepoints"]) - damage)
                if int(own["lifepoints"]) <= 0:
                    session["losses"] += 1
        result["damage"] = damage
    elif unit.targets == "orders":
        # The Distractor disables orders on both sides for one beat.
        session["stalled"] = int(session["stalled"]) + 1
        result["stalled"] = True
    else:
        session["shielded"] = int(session["shielded"]) + 1
        result["shielded"] = True
    data.update(state)
    data["mobilising_armies"] = session
    message = f"Deployed a {unit.display_name}."
    data["mobilising_armies_last_result"] = message
    return data, True, {"message": message, **result}


def _end_scenario(data: dict[str, Any], session: Mapping[str, Any], message: str) -> None:
    survivors: dict[str, int] = {}
    for squad in session["squads"]:
        if int(squad["lifepoints"]) > 0:
            survivors[str(squad["id"])] = survivors.get(str(squad["id"]), 0) + 1
    data["mobilising_armies"] = {}
    data["mobilising_armies_squads"] = survivors
    data["mobilising_armies_special_units"] = dict(session["special_units"])
    active = data.get("activity_session")
    if isinstance(active, Mapping) and str(active.get("active_id", "")) == MOBILISING_ARMIES_ACTIVITY_ID:
        data["activity_session"] = {"active_id": ""}
    data["mobilising_armies_last_result"] = message[:500]


def _award_rank(data: dict[str, Any], state: Mapping[str, Any], points: int) -> int:
    window = dict(state["mobilising_armies_rank_window"])
    allowed = max(0, MOBILISING_ARMIES_RANK_HOURLY_CAP - _int(window.get("points")))
    granted = min(points, allowed)
    window["points"] = _int(window.get("points")) + granted
    data["mobilising_armies_rank_window"] = window
    data["mobilising_armies_rank"] = _int(data.get("mobilising_armies_rank")) + granted
    return granted


def _settle(
    data: dict[str, Any],
    state: Mapping[str, Any],
    session: dict[str, Any],
    *,
    outcome: str,
    end_condition_pct: int,
    forfeited: bool,
) -> dict[str, Any]:
    scenario = MOBILISING_ARMIES_SCENARIOS_BY_ID[str(session["scenario"])]
    eligible = (
        not forfeited
        and int(session["commands"]) >= MOBILISING_ARMIES_RANK_ACTION_MINIMUM
        and int(session["beat"]) >= MOBILISING_ARMIES_RANK_MINIMUM_BEATS
    )
    wanted_rank = 0
    if eligible:
        wanted_rank = (
            MOBILISING_ARMIES_RANK_FOR_WIN
            if outcome == "win"
            else MOBILISING_ARMIES_RANK_FOR_PARTICIPATION
        )
    rank_gained = _award_rank(data, state, wanted_rank)
    credits = 0
    if not forfeited:
        credits = mobilising_armies_reward_credits_pure(
            beats_survived=int(session["beat"]),
            kills=int(session["kills"]),
            investment=int(session["investment"]),
            rank_modifier_pct=int(session["rank_modifier_pct"]),
            end_condition_pct=end_condition_pct,
        )
        data["mobilising_armies_reward_credits"] = (
            _int(data.get("mobilising_armies_reward_credits")) + credits
        )
    data["mobilising_armies_games_played"] = (
        _int(data.get("mobilising_armies_games_played")) + 1
    )
    if outcome == "win":
        data["mobilising_armies_wins"] = _int(data.get("mobilising_armies_wins")) + 1
    elif outcome == "loss":
        data["mobilising_armies_losses"] = _int(data.get("mobilising_armies_losses")) + 1
    if not forfeited:
        played = list(state["mobilising_armies_scenarios_played"])
        if scenario.id not in played:
            played.append(scenario.id)
        data["mobilising_armies_scenarios_played"] = played
    message = (
        f"{scenario.display_name} {outcome} · {session['kills']} squads defeated · "
        f"+{rank_gained} rank · +{credits:,} reward credits"
    )
    _end_scenario(data, session, message)
    return {
        "terminal": True,
        "outcome": outcome,
        "rank_gained": rank_gained,
        "rank_eligible": eligible,
        "reward_credits": credits,
        "end_condition_pct": end_condition_pct,
        "message": message,
    }


def _terminal_outcome(session: Mapping[str, Any]) -> tuple[str, int] | None:
    scenario = MOBILISING_ARMIES_SCENARIOS_BY_ID[str(session["scenario"])]
    if int(session["objective"]) >= scenario.objective_target:
        return "win", MOBILISING_ARMIES_END_PRIMARY_PCT
    if not _living(session["rivals"]):
        return "win", (
            MOBILISING_ARMIES_END_PRIMARY_PCT
            if scenario.id == "conflict"
            else MOBILISING_ARMIES_END_ELIMINATION_PCT
        )
    if not _living(session["squads"]):
        return "loss", MOBILISING_ARMIES_END_LOSS_PCT
    if int(session["opponent_objective"]) >= scenario.objective_target:
        return "loss", MOBILISING_ARMIES_END_LOSS_PCT
    return None


def apply_mobilising_armies_review_pure(
    player_data: Mapping[str, Any],
    rng,
    *,
    productive: bool,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_mobilising_armies_state_pure(data)
    session = copy.deepcopy(state["mobilising_armies"])
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if not session or active_id != MOBILISING_ARMIES_ACTIVITY_ID:
        return data, False, {"reason": "Enter a Mobilising Armies scenario first."}

    data.update(state)
    window = dict(state["mobilising_armies_rank_window"])
    beats = _int(window.get("beats")) + 1
    if beats >= MOBILISING_ARMIES_RANK_WINDOW_BEATS:
        window = {"beats": 0, "points": 0}
    else:
        window["beats"] = beats
    data["mobilising_armies_rank_window"] = window

    session["beat"] = int(session["beat"]) + 1
    order_result: dict[str, Any] = {}
    order = str(session["order"])
    if int(session["stalled"]) > 0:
        session["stalled"] -= 1
        order = "stalled"
        order_result = {"stalled": True}
    elif productive:
        session["commands"] = int(session["commands"]) + 1
        if order == "attack":
            order_result = _attack_rival(session, rng)
            scenario = MOBILISING_ARMIES_SCENARIOS_BY_ID[str(session["scenario"])]
            if order_result.get("killed"):
                if scenario.id == "hoard":
                    session["objective"] = min(
                        scenario.objective_target,
                        int(session["objective"]) + MOBILISING_ARMIES_HOARD_GAIN_ON_KILL,
                    )
                    order_result["gold_gained"] = MOBILISING_ARMIES_HOARD_GAIN_ON_KILL
                elif scenario.id == "conflict":
                    session["objective"] = int(session["kills"])
            if scenario.id == "rescue" and order_result.get("attacked"):
                stolen = min(
                    int(session["opponent_objective"]),
                    MOBILISING_ARMIES_RESCUE_STEAL_PER_ORDER,
                )
                if stolen:
                    session["opponent_objective"] = int(session["opponent_objective"]) - stolen
                    session["objective"] = min(
                        scenario.objective_target, int(session["objective"]) + stolen
                    )
                    order_result["stolen"] = stolen
        elif order == "explore":
            order_result = _explore(session, data, rng)
        else:
            order_result = _advance_objective(session, rng)
    else:
        order = "idle"

    opponent_result = _opponent_beat(session, rng)
    data["mobilising_armies"] = session
    terminal = _terminal_outcome(session)
    if terminal is not None:
        outcome, end_pct = terminal
        return data, True, {
            "order": order,
            **order_result,
            **opponent_result,
            **_settle(
                data,
                state,
                session,
                outcome=outcome,
                end_condition_pct=end_pct,
                forfeited=False,
            ),
        }
    if int(session["beat"]) >= MOBILISING_ARMIES_SCENARIO_BEATS:
        # Exact: "In the event that time runs out, all players receive +1 rank."
        return data, True, {
            "order": order,
            **order_result,
            **opponent_result,
            **_settle(
                data,
                state,
                session,
                outcome="timeout",
                end_condition_pct=MOBILISING_ARMIES_END_LOSS_PCT,
                forfeited=False,
            ),
        }
    scenario = MOBILISING_ARMIES_SCENARIOS_BY_ID[str(session["scenario"])]
    message = (
        f"{scenario.display_name} order {session['beat']}/"
        f"{MOBILISING_ARMIES_SCENARIO_BEATS} · {order} · "
        f"objective {session['objective']:,}/{scenario.objective_target:,} · "
        f"rival {session['opponent_objective']:,}"
    )
    data["mobilising_armies_last_result"] = message
    return data, True, {
        "terminal": False,
        "order": order,
        **order_result,
        **opponent_result,
        "message": message,
    }


def forfeit_mobilising_armies_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_mobilising_armies_state_pure(data)
    session = copy.deepcopy(state["mobilising_armies"])
    if not session:
        return data, False, {"reason": "No scenario is under way."}
    data.update(state)
    return data, True, _settle(
        data,
        state,
        session,
        outcome="forfeit",
        end_condition_pct=MOBILISING_ARMIES_END_LOSS_PCT,
        forfeited=True,
    )


# --- Officer Tower ----------------------------------------------------------


def _unlocked_floors(rank: int) -> tuple[str, ...]:
    return tuple(
        floor.id for floor in MOBILISING_ARMIES_FLOORS if int(rank) >= floor.minimum_rank
    )


def roll_spoils_offer_pure(
    player_data: Mapping[str, Any], floor_id: str, rng
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_mobilising_armies_state_pure(data)
    floor = MOBILISING_ARMIES_FLOORS_BY_ID.get(str(floor_id))
    if floor is None:
        return data, False, {"reason": "Unknown Officer Tower floor."}
    if floor.id not in _unlocked_floors(state["mobilising_armies_rank"]):
        return data, False, {"reason": f"The {floor.display_name} needs rank {floor.minimum_rank}."}
    pool = [item_name for item_name, _quantity in MOBILISING_ARMIES_SPOILS[floor.id]]
    offered: list[str] = []
    while pool and len(offered) < MOBILISING_ARMIES_SPOILS_OFFER_SIZE:
        offered.append(pool.pop(int(_rng_value(rng) * len(pool))))
    data.update(state)
    data["mobilising_armies_spoils_offer"] = {"floor": floor.id, "items": offered}
    message = f"{floor.quartermaster} lays out {len(offered)} lots of spoils."
    data["mobilising_armies_last_result"] = message
    return data, True, {"message": message, "items": tuple(offered)}


def claim_spoils_pure(
    player_data: Mapping[str, Any], item_names: Sequence[str]
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_mobilising_armies_state_pure(data)
    offer = state["mobilising_armies_spoils_offer"]
    if not offer:
        return data, False, {"reason": "Look over a Spoils of War stall first."}
    floor = MOBILISING_ARMIES_FLOORS_BY_ID[str(offer["floor"])]
    chosen = [str(name) for name in (item_names or ())]
    if len(chosen) != MOBILISING_ARMIES_SPOILS_CHOICES:
        return data, False, {
            "reason": f"Choose exactly {MOBILISING_ARMIES_SPOILS_CHOICES} lots."
        }
    offered = list(offer["items"])
    for name in chosen:
        if name not in offered:
            return data, False, {"reason": f"{name} is not on this stall."}
    if state["mobilising_armies_reward_credits"] < floor.spoils_cost:
        return data, False, {
            "reason": f"Three lots cost {floor.spoils_cost:,} reward credits."
        }
    inventory = copy.deepcopy(dict(_inventory(data)))
    granted: dict[str, int] = {}
    for name in chosen:
        quantity = _SPOILS_BY_FLOOR_ITEM[floor.id][name]
        inventory[name] = _int(inventory.get(name)) + quantity
        granted[name] = granted.get(name, 0) + quantity
    data.update(state)
    data["inventory"] = inventory
    data["mobilising_armies_reward_credits"] = (
        state["mobilising_armies_reward_credits"] - floor.spoils_cost
    )
    data["mobilising_armies_spoils_offer"] = {}
    message = (
        f"Collected {', '.join(f'{count} {name}' for name, count in granted.items())} "
        f"for {floor.spoils_cost:,} reward credits."
    )
    data["mobilising_armies_last_result"] = message
    return data, True, {"message": message, "items": granted, "cost": floor.spoils_cost}


def buy_reward_pure(
    player_data: Mapping[str, Any], item_name: str
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_mobilising_armies_state_pure(data)
    name = str(item_name)
    row = _REWARD_COSTS.get(name)
    if row is None:
        return data, False, {"reason": "The Officer Tower does not stock that."}
    floor_id, cost, _refund_pct = row
    floor = MOBILISING_ARMIES_FLOORS_BY_ID[floor_id]
    if floor.id not in _unlocked_floors(state["mobilising_armies_rank"]):
        return data, False, {"reason": f"{name} needs rank {floor.minimum_rank}."}
    if state["mobilising_armies_reward_credits"] < cost:
        return data, False, {"reason": f"{name} costs {cost:,} reward credits."}
    ring = MOBILISING_ARMIES_IMBUE_RINGS_BY_ITEM.get(name)
    inventory = copy.deepcopy(dict(_inventory(data)))
    if ring is not None:
        if _int(inventory.get(ring.base_item)) <= 0:
            return data, False, {"reason": f"Bring a {ring.base_item} to imbue."}
        remaining = _int(inventory[ring.base_item]) - 1
        if remaining:
            inventory[ring.base_item] = remaining
        else:
            inventory.pop(ring.base_item, None)
    inventory[name] = _int(inventory.get(name)) + 1
    data.update(state)
    data["inventory"] = inventory
    data["mobilising_armies_reward_credits"] = (
        state["mobilising_armies_reward_credits"] - cost
    )
    message = f"{floor.quartermaster} hands over a {name} for {cost:,} reward credits."
    data["mobilising_armies_last_result"] = message
    return data, True, {"message": message, "item": name, "cost": cost}


def refund_reward_pure(
    player_data: Mapping[str, Any], item_name: str
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_mobilising_armies_state_pure(data)
    name = str(item_name)
    row = _REWARD_COSTS.get(name)
    if row is None:
        return data, False, {"reason": "The Officer Tower does not buy that back."}
    _floor_id, cost, refund_pct = row
    if refund_pct <= 0:
        return data, False, {"reason": f"A {name} cannot be refunded."}
    inventory = copy.deepcopy(dict(_inventory(data)))
    if _int(inventory.get(name)) <= 0:
        return data, False, {"reason": f"You are not carrying a {name}."}
    remaining = _int(inventory[name]) - 1
    if remaining:
        inventory[name] = remaining
    else:
        inventory.pop(name, None)
    refund = cost * refund_pct // 100
    data.update(state)
    data["inventory"] = inventory
    data["mobilising_armies_reward_credits"] = (
        state["mobilising_armies_reward_credits"] + refund
    )
    message = f"Refunded a {name} for {refund:,} reward credits ({refund_pct}%)."
    data["mobilising_armies_last_result"] = message
    return data, True, {"message": message, "item": name, "refund": refund}


def set_prefix_pure(
    player_data: Mapping[str, Any], prefix: str
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_mobilising_armies_state_pure(data)
    wanted = str(prefix)
    unlocked = _unlocked_floors(state["mobilising_armies_rank"])
    available = {
        MOBILISING_ARMIES_FLOORS_BY_ID[floor_id].prefix for floor_id in unlocked
    }
    if wanted and wanted not in available:
        return data, False, {"reason": f"You have not unlocked the {wanted} prefix."}
    data.update(state)
    data["mobilising_armies_prefix"] = wanted
    message = f"Prefix set to {wanted}." if wanted else "Prefix cleared."
    data["mobilising_armies_last_result"] = message
    return data, True, {"message": message, "prefix": wanted}


def use_locator_pure(
    player_data: Mapping[str, Any], item_name: str, skill: str, rng
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_mobilising_armies_state_pure(data)
    locator = MOBILISING_ARMIES_LOCATORS_BY_ITEM.get(str(item_name))
    if locator is None:
        return data, False, {"reason": "That is not a locator."}
    if _held(data, locator.item_name) <= 0:
        return data, False, {"reason": f"You are not carrying an {locator.item_name}."}
    chosen_skill = str(skill)
    if chosen_skill not in MOBILISING_ARMIES_LOCATOR_SKILL_IDS:
        return data, False, {"reason": "Choose a resource kind to locate."}
    targets = {
        "mining": locator.ore_targets,
        "woodcutting": locator.tree_targets,
        "fishing": locator.fishing_targets,
    }[chosen_skill]
    if not targets:
        return data, False, {
            "reason": f"An {locator.item_name} knows no {chosen_skill} sites."
        }
    target = _pick(rng, targets)
    data.update(state)
    data[MOBILISING_ARMIES_LOCATOR_TARGET_KEYS[chosen_skill]] = target
    message = f"The {locator.item_name} drops you at a random {chosen_skill} site: {target}."
    data["mobilising_armies_last_result"] = message
    return data, True, {"message": message, "skill": chosen_skill, "target": target}


def open_quest_kit_pure(
    player_data: Mapping[str, Any], item_name: str
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_mobilising_armies_state_pure(data)
    kit = MOBILISING_ARMIES_QUEST_KITS_BY_ITEM.get(str(item_name))
    if kit is None:
        return data, False, {"reason": "That is not a quest kit."}
    inventory = copy.deepcopy(dict(_inventory(data)))
    if _int(inventory.get(kit.item_name)) <= 0:
        return data, False, {"reason": f"You are not carrying a {kit.item_name}."}
    remaining = _int(inventory[kit.item_name]) - 1
    if remaining:
        inventory[kit.item_name] = remaining
    else:
        inventory.pop(kit.item_name, None)
    for content in kit.contents:
        inventory[content] = _int(inventory.get(content)) + 1
    data.update(state)
    data["inventory"] = inventory
    message = f"Emptied the {kit.item_name}: {', '.join(kit.contents)}."
    data["mobilising_armies_last_result"] = message
    return data, True, {"message": message, "contents": kit.contents}


def apply_mobilising_armies_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
    rng=None,
    *,
    item_values: Mapping[str, int] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    body = payload if isinstance(payload, Mapping) else {}
    roll = rng if rng is not None else (lambda: 0.5)
    if action_id == "set_policy":
        return set_mobilising_armies_policy_pure(player_data, body)
    if action_id == "invest":
        return invest_items_pure(
            player_data,
            str(body.get("item_name", "")),
            _int(body.get("quantity"), 1),
            item_values=item_values or {},
        )
    if action_id == "recruit":
        return recruit_squads_pure(
            player_data, str(body.get("squad", "")), _int(body.get("quantity"), 1)
        )
    if action_id == "buy_special_unit":
        return buy_special_units_pure(
            player_data, str(body.get("unit", "")), _int(body.get("quantity"), 1)
        )
    if action_id == "enter":
        return enter_mobilising_armies_pure(player_data, roll, body)
    if action_id == "deploy":
        return deploy_special_unit_pure(player_data, str(body.get("unit", "")), roll)
    if action_id == "forfeit":
        return forfeit_mobilising_armies_pure(player_data)
    if action_id == "roll_spoils":
        return roll_spoils_offer_pure(player_data, str(body.get("floor", "")), roll)
    if action_id == "claim_spoils":
        return claim_spoils_pure(player_data, body.get("items") or ())
    if action_id == "buy_reward":
        return buy_reward_pure(player_data, str(body.get("item_name", "")))
    if action_id == "refund_reward":
        return refund_reward_pure(player_data, str(body.get("item_name", "")))
    if action_id == "set_prefix":
        return set_prefix_pure(player_data, str(body.get("prefix", "")))
    if action_id == "use_locator":
        return use_locator_pure(
            player_data,
            str(body.get("item_name", "")),
            str(body.get("skill", "")),
            roll,
        )
    if action_id == "open_quest_kit":
        return open_quest_kit_pure(player_data, str(body.get("item_name", "")))
    # Shallow on purpose: nothing ran, and callers discard the save from a failed
    # command.
    return dict(player_data), False, {"reason": "Unknown Mobilising Armies command."}


def mobilising_armies_can_review_pure(player_data: Mapping[str, Any]) -> bool:
    return bool(sanitize_mobilising_armies_state_pure(player_data)["mobilising_armies"])


def mobilising_armies_view_pure(
    player_data: Mapping[str, Any],
    *,
    item_values: Mapping[str, int] | None = None,
) -> dict[str, Any]:
    state = sanitize_mobilising_armies_state_pure(player_data)
    session = state["mobilising_armies"]
    rank = state["mobilising_armies_rank"]
    band = mobilising_armies_rank_band_pure(rank)
    played = state["mobilising_armies_scenarios_played"]
    policy = state["mobilising_armies_policy"]
    reward_credits = state["mobilising_armies_reward_credits"]
    unlocked = _unlocked_floors(rank)
    contracts = sum(state["mobilising_armies_squads"].values())
    entry_reasons = _entry_reasons(player_data, state) if not session else ()
    scenario = MOBILISING_ARMIES_SCENARIOS_BY_ID[
        str(session["scenario"]) if session else policy["scenario"]
    ]
    inventory = _inventory(player_data)
    window = state["mobilising_armies_rank_window"]
    offer = state["mobilising_armies_spoils_offer"]
    values = item_values if item_values is not None else ITEM_VALUES
    investment_rows = []
    for item_name in sorted(inventory):
        held = _int(inventory.get(item_name))
        per_item = mobilising_armies_investment_credits_pure(_int(values.get(item_name)))
        if held <= 0 or per_item <= 0:
            continue
        investment_rows.append(
            {
                "id": item_name,
                "display_name": f"{item_name} x{held} · {per_item:,} credits each",
                "held": held,
                "credits_each": per_item,
                "investable": not session
                and state["mobilising_armies_investment_credits"]
                < MOBILISING_ARMIES_INVESTMENT_CREDIT_CAP,
            }
        )
    return {
        **state,
        "investment_options": tuple(investment_rows),
        "active": bool(session),
        "can_enter": not entry_reasons and not session,
        "entry_reasons": entry_reasons,
        "primary_label": "Command the battle" if session else "Enter the briefing room",
        "primary_enabled": bool(session) or not entry_reasons,
        "forfeit_visible": bool(session),
        "rank_prefix_band": band.prefix,
        "maximum_investment": band.maximum_investment,
        "reward_modifier_pct": band.reward_modifier_pct,
        "rank_points_left_this_window": max(
            0, MOBILISING_ARMIES_RANK_HOURLY_CAP - int(window["points"])
        ),
        "squad_contracts": contracts,
        "squad_contracts_required": MOBILISING_ARMIES_SQUADS_REQUIRED,
        "special_units_held": sum(state["mobilising_armies_special_units"].values()),
        "special_unit_cap": MOBILISING_ARMIES_SPECIAL_UNIT_CAP,
        "scenario_name": scenario.display_name,
        "objective_label": scenario.objective_label,
        "objective_target": scenario.objective_target,
        "objective": int(session["objective"]) if session else 0,
        "opponent_objective": int(session["opponent_objective"]) if session else 0,
        "beat": int(session["beat"]) if session else 0,
        "beat_count": MOBILISING_ARMIES_SCENARIO_BEATS,
        "commands": int(session["commands"]) if session else 0,
        "commands_required": MOBILISING_ARMIES_RANK_ACTION_MINIMUM,
        "rank_eligible": bool(
            session
            and int(session["commands"]) >= MOBILISING_ARMIES_RANK_ACTION_MINIMUM
            and int(session["beat"]) >= MOBILISING_ARMIES_RANK_MINIMUM_BEATS
        ),
        "squads_alive": len(_living(session["squads"])) if session else 0,
        "rivals_alive": len(_living(session["rivals"])) if session else 0,
        "kills": int(session["kills"]) if session else 0,
        "losses": int(session["losses"]) if session else 0,
        "scenario_options": tuple(
            {
                "id": row.id,
                "display_name": row.display_name,
                "description": row.description,
                "unlocked": not row.unlocked_by or row.unlocked_by in played,
            }
            for row in MOBILISING_ARMIES_SCENARIOS
        ),
        "formation_options": tuple(
            {
                "id": formation_id,
                "display_name": label,
                "unlocked": rank >= minimum_rank,
                "minimum_rank": minimum_rank,
            }
            for formation_id, label, minimum_rank in MOBILISING_ARMIES_FORMATIONS
        ),
        "order_options": tuple(
            {"id": order_id, "display_name": label}
            for order_id, label in MOBILISING_ARMIES_ORDERS
        ),
        "siege_route_options": tuple(
            {"id": route_id, "display_name": label}
            for route_id, label in MOBILISING_ARMIES_SIEGE_ROUTES
        ),
        "siege_route_control_enabled": (
            str(session["scenario"]) if session else policy["scenario"]
        ) == "siege",
        "squad_options": tuple(
            {
                "id": squad.id,
                "display_name": squad.display_name,
                "combat_level": squad.combat_level,
                "lifepoints": squad.lifepoints,
                "held": state["mobilising_armies_squads"].get(squad.id, 0),
                "affordable": (
                    not session
                    and contracts < MOBILISING_ARMIES_SQUAD_CONTRACT_CAP
                    and state["mobilising_armies_investment_credits"]
                    >= MOBILISING_ARMIES_SQUAD_CREDIT_COST
                ),
            }
            for squad in MOBILISING_ARMIES_SQUADS
        ),
        "special_unit_options": tuple(
            {
                "id": unit.id,
                "display_name": unit.display_name,
                "description": unit.description,
                "held": (
                    int(session["special_units"].get(unit.id, 0))
                    if session
                    else state["mobilising_armies_special_units"].get(unit.id, 0)
                ),
                "deployable": bool(session)
                and int(session["special_units"].get(unit.id, 0)) > 0,
                "affordable": (
                    not session
                    and sum(state["mobilising_armies_special_units"].values())
                    < MOBILISING_ARMIES_SPECIAL_UNIT_CAP
                    and state["mobilising_armies_investment_credits"]
                    >= MOBILISING_ARMIES_SPECIAL_UNIT_CREDIT_COST
                ),
            }
            for unit in MOBILISING_ARMIES_SPECIAL_UNITS
        ),
        "floor_options": tuple(
            {
                "id": floor.id,
                "display_name": floor.display_name,
                "quartermaster": floor.quartermaster,
                "minimum_rank": floor.minimum_rank,
                "unlocked": floor.id in unlocked,
                "spoils_cost": floor.spoils_cost,
                "prefix": floor.prefix,
            }
            for floor in MOBILISING_ARMIES_FLOORS
        ),
        "spoils_offer": tuple(
            {"item": name, "quantity": _SPOILS_BY_FLOOR_ITEM[str(offer["floor"])][name]}
            for name in offer.get("items", ())
        ),
        "spoils_offer_floor": str(offer.get("floor", "")),
        "spoils_claim_enabled": bool(
            offer
            and not session
            and reward_credits
            >= MOBILISING_ARMIES_FLOORS_BY_ID[str(offer["floor"])].spoils_cost
        ),
        "reward_options": tuple(
            {
                "item": name,
                "floor": floor_id,
                "cost": cost,
                "refund_pct": refund_pct,
                "minimum_rank": MOBILISING_ARMIES_FLOORS_BY_ID[floor_id].minimum_rank,
                "unlocked": floor_id in unlocked,
                "held": _int(inventory.get(name)),
                "base_item": (
                    MOBILISING_ARMIES_IMBUE_RINGS_BY_ITEM[name].base_item
                    if name in MOBILISING_ARMIES_IMBUE_RINGS_BY_ITEM
                    else ""
                ),
                "affordable": (
                    floor_id in unlocked
                    and reward_credits >= cost
                    and (
                        name not in MOBILISING_ARMIES_IMBUE_RINGS_BY_ITEM
                        or _int(
                            inventory.get(
                                MOBILISING_ARMIES_IMBUE_RINGS_BY_ITEM[name].base_item
                            )
                        )
                        > 0
                    )
                ),
                "refundable": refund_pct > 0 and _int(inventory.get(name)) > 0,
            }
            for name, (floor_id, cost, refund_pct) in _REWARD_COSTS.items()
        ),
        "prefix_options": tuple(
            {
                "id": floor.prefix,
                "display_name": floor.prefix,
                "unlocked": floor.id in unlocked,
            }
            for floor in MOBILISING_ARMIES_FLOORS
        ),
        "locator_options": tuple(
            {
                "item": locator.item_name,
                "held": _int(inventory.get(locator.item_name)),
                "usable": _int(inventory.get(locator.item_name)) > 0,
            }
            for locator in MOBILISING_ARMIES_LOCATORS
        ),
        "locator_skill_options": tuple(
            {"id": skill_id, "display_name": label}
            for skill_id, label in MOBILISING_ARMIES_LOCATOR_SKILLS
        ),
        "quest_kit_options": tuple(
            {
                "item": kit.item_name,
                "held": _int(inventory.get(kit.item_name)),
                "contents": kit.contents,
                "openable": _int(inventory.get(kit.item_name)) > 0,
            }
            for kit in MOBILISING_ARMIES_QUEST_KITS
        ),
    }
