"""Pure Stealing Creation session, score-race, and reward-tool mechanics."""

from __future__ import annotations

import copy
from collections.abc import Callable, Mapping
from typing import Any

try:
    from .fist_of_guthix_logic import generate_fist_of_guthix_opponent_pure
    from .logic_pure import (
        apply_combat_burst_pure,
        combat_max_lifepoints_pure,
        prayer_effect_state_pure,
    )
    from .pet_logic import store_active_pet_pure
    from .stealing_creation_data import (
        STEALING_CREATION_ACTIVITY_ID,
        STEALING_CREATION_CLASS_REQUIREMENTS,
        STEALING_CREATION_CLAY_PER_GATHER_REVIEW,
        STEALING_CREATION_COMBAT_TARGET_ID,
        STEALING_CREATION_COMBAT_TICKS_PER_REVIEW,
        STEALING_CREATION_GATHER_METHODS,
        STEALING_CREATION_OPPONENT_CLAY_PER_REVIEW,
        STEALING_CREATION_RAID_INTERVAL_REVIEWS,
        STEALING_CREATION_RECIPES,
        STEALING_CREATION_REWARD_COST,
        STEALING_CREATION_REWARD_FORM_BY_ID,
        STEALING_CREATION_REWARD_FORMS,
        STEALING_CREATION_SCORE_PER_CLASS,
        STEALING_CREATION_SESSION_EQUIPMENT,
        STEALING_CREATION_SESSION_REVIEWS,
    )
    from .summoning_logic import dismiss_familiar_pure
except ImportError:  # pragma: no cover - flat imports used by tests
    from fist_of_guthix_logic import generate_fist_of_guthix_opponent_pure  # type: ignore
    from logic_pure import (  # type: ignore
        apply_combat_burst_pure,
        combat_max_lifepoints_pure,
        prayer_effect_state_pure,
    )
    from pet_logic import store_active_pet_pure  # type: ignore
    from stealing_creation_data import (  # type: ignore
        STEALING_CREATION_ACTIVITY_ID,
        STEALING_CREATION_CLASS_REQUIREMENTS,
        STEALING_CREATION_CLAY_PER_GATHER_REVIEW,
        STEALING_CREATION_COMBAT_TARGET_ID,
        STEALING_CREATION_COMBAT_TICKS_PER_REVIEW,
        STEALING_CREATION_GATHER_METHODS,
        STEALING_CREATION_OPPONENT_CLAY_PER_REVIEW,
        STEALING_CREATION_RAID_INTERVAL_REVIEWS,
        STEALING_CREATION_RECIPES,
        STEALING_CREATION_REWARD_COST,
        STEALING_CREATION_REWARD_FORM_BY_ID,
        STEALING_CREATION_REWARD_FORMS,
        STEALING_CREATION_SCORE_PER_CLASS,
        STEALING_CREATION_SESSION_EQUIPMENT,
        STEALING_CREATION_SESSION_REVIEWS,
    )
    from summoning_logic import dismiss_familiar_pure  # type: ignore


STEALING_CREATION_STATE_VERSION = 1
_VALID_MODES = frozenset({"casual", "advanced"})
_VALID_DUTIES = frozenset({"gather", "process", "deposit"})
_TOOL_ITEM_NAMES = {"morphic": "Proto-tool", "volatile": "Volatile clay tool"}


def _int(value: Any, default: int = 0, *, minimum: int = 0) -> int:
    if isinstance(value, bool):
        return default
    try:
        return max(minimum, int(value))
    except (TypeError, ValueError, OverflowError):
        return default


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError, OverflowError):
        return default


def _unit(value: Any) -> float:
    return max(0.0, min(0.999999999, _float(value, 0.5)))


def _rng_value(rng: Callable[[], float] | None) -> float:
    if rng is None:
        return 0.5
    try:
        return _unit(rng())
    except (TypeError, ValueError, StopIteration):
        return 0.5


def _random_form_id(rng: Callable[[], float] | None) -> str:
    index = min(
        len(STEALING_CREATION_REWARD_FORMS) - 1,
        int(_rng_value(rng) * len(STEALING_CREATION_REWARD_FORMS)),
    )
    return STEALING_CREATION_REWARD_FORMS[index].id


def _empty_session() -> dict[str, Any]:
    return {"active_id": ""}


def _default_reward_tool() -> dict[str, Any]:
    return {}


def default_stealing_creation_state_pure() -> dict[str, Any]:
    return {
        "version": STEALING_CREATION_STATE_VERSION,
        "automation_mode": "casual",
        "selected_duty": "gather",
        "selected_gather_method": "chop",
        "selected_class": 5,
        "selected_recipe": "scimitar",
        "points": 0,
        "games": 0,
        "wins": 0,
        "losses": 0,
        "ties": 0,
        "deaths": 0,
        "active_session": {},
        "reward_tools": {
            "morphic": _default_reward_tool(),
            "volatile": _default_reward_tool(),
        },
        "active_reward_tool": "",
        "last_result": "",
    }


def _sanitize_reward_tool(raw: Any, kind: str) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        return {}
    form_id = str(raw.get("form_id", ""))
    if form_id not in STEALING_CREATION_REWARD_FORM_BY_ID:
        return {}
    charge = max(0.0, min(1.0, _float(raw.get("charge"), 0.0)))
    if charge <= 0:
        return {}
    return {
        "kind": kind,
        "form_id": form_id,
        "charge": charge,
        "segments_used": min(10, _int(raw.get("segments_used"))),
    }


def _sanitize_session(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        return {}
    active = bool(raw.get("active", False))
    if not active:
        return {}
    clay_raw = raw.get("clay", {})
    clay_raw = clay_raw if isinstance(clay_raw, Mapping) else {}
    equipment_raw = raw.get("equipment", {})
    equipment_raw = equipment_raw if isinstance(equipment_raw, Mapping) else {}
    raider_raw = raw.get("raider", {})
    raider_raw = raider_raw if isinstance(raider_raw, Mapping) else {}
    raider_stats = raider_raw.get("stats", {})
    raider_valid = (
        isinstance(raider_stats, Mapping)
        and bool(str(raider_raw.get("display_name", "")))
        and all(
            _int(raider_stats.get(key), 0) > 0
            for key in ("attack", "strength", "defence", "constitution", "magic", "ranged")
        )
    )
    return {
        "active": True,
        "review": min(
            STEALING_CREATION_SESSION_REVIEWS,
            _int(raw.get("review")),
        ),
        "player_score": _int(raw.get("player_score")),
        "opponent_score": _int(raw.get("opponent_score")),
        "clay": {
            str(tier): _int(clay_raw.get(str(tier))) for tier in range(1, 6)
        },
        "equipment": {
            slot: min(5, _int(equipment_raw.get(slot)))
            for slot in ("tool", "weapon", "armour", "barrier")
        },
        "barrier_pieces": min(3, _int(raw.get("barrier_pieces"))),
        "barrier_piece_tier": min(5, _int(raw.get("barrier_piece_tier"))),
        "barrier_durability": min(20, _int(raw.get("barrier_durability"))),
        "lifepoints": _int(raw.get("lifepoints"), 100, minimum=1),
        "raider": copy.deepcopy(dict(raider_raw)) if raider_valid else {},
        "combat_encounter": copy.deepcopy(
            dict(raw.get("combat_encounter", {}))
            if raider_valid and isinstance(raw.get("combat_encounter"), Mapping)
            else {}
        ),
        "next_raid_review": min(
            STEALING_CREATION_SESSION_REVIEWS,
            _int(raw.get("next_raid_review"), 4, minimum=1),
        ),
        "raids_won": _int(raw.get("raids_won")),
        "gathered": _int(raw.get("gathered")),
        "processed": _int(raw.get("processed")),
        "deposited": _int(raw.get("deposited")),
        "last_action": str(raw.get("last_action", ""))[:240],
    }


def sanitize_stealing_creation_state_pure(raw: Any) -> dict[str, Any]:
    defaults = default_stealing_creation_state_pure()
    source = raw if isinstance(raw, Mapping) else {}
    raw_tools = source.get("reward_tools", {})
    raw_tools = raw_tools if isinstance(raw_tools, Mapping) else {}
    tools = {
        kind: _sanitize_reward_tool(raw_tools.get(kind), kind)
        for kind in ("morphic", "volatile")
    }
    active_tool = str(source.get("active_reward_tool", ""))
    if active_tool not in tools or not tools.get(active_tool):
        active_tool = ""
    mode = str(source.get("automation_mode", "casual"))
    duty = str(source.get("selected_duty", "gather"))
    gather_method = str(source.get("selected_gather_method", "chop"))
    recipe = str(source.get("selected_recipe", "scimitar"))
    return {
        **defaults,
        "automation_mode": mode if mode in _VALID_MODES else "casual",
        "selected_duty": duty if duty in _VALID_DUTIES else "gather",
        "selected_gather_method": (
            gather_method if gather_method in STEALING_CREATION_GATHER_METHODS else "chop"
        ),
        "selected_class": min(5, _int(source.get("selected_class"), 5, minimum=1)),
        "selected_recipe": recipe if recipe in STEALING_CREATION_RECIPES else "scimitar",
        "points": _int(source.get("points")),
        "games": _int(source.get("games")),
        "wins": _int(source.get("wins")),
        "losses": _int(source.get("losses")),
        "ties": _int(source.get("ties")),
        "deaths": _int(source.get("deaths")),
        "active_session": _sanitize_session(source.get("active_session")),
        "reward_tools": tools,
        "active_reward_tool": active_tool,
        "last_result": str(source.get("last_result", ""))[:500],
    }


def ensure_stealing_creation_state_pure(
    player_data: Mapping[str, Any],
) -> dict[str, Any]:
    # Shallow on purpose: the whole stealing_creation subtree is replaced below
    # with sanitize output, and that is the only key consumers write.
    data = dict(player_data)
    state = sanitize_stealing_creation_state_pure(data.get("stealing_creation"))
    inventory = data.get("inventory", {})
    inventory = inventory if isinstance(inventory, Mapping) else {}
    for kind, item_name in _TOOL_ITEM_NAMES.items():
        if _int(inventory.get(item_name)) <= 0:
            state["reward_tools"][kind] = {}
            if state["active_reward_tool"] == kind:
                state["active_reward_tool"] = ""
    data["stealing_creation"] = state
    return data


def stealing_creation_points_for_score_pure(score: Any) -> int:
    value = _int(score)
    if value < 20_000:
        return value // 1_000
    if value < 22_000:
        return 20
    if value < 26_000:
        return 21
    if value < 34_000:
        return 22
    if value < 50_000:
        return 23
    if value < 82_000:
        return 24
    if value < 146_000:
        return 25
    return 26


def _available_class(player_data: Mapping[str, Any], method_id: str) -> int:
    spec = STEALING_CREATION_GATHER_METHODS[method_id]
    level_key = str(spec["skill_level_key"])
    if not level_key:
        return 1
    level = _int(player_data.get(level_key), 1, minimum=1)
    available = max(
        tier
        for tier, requirement in STEALING_CREATION_CLASS_REQUIREMENTS.items()
        if level >= requirement
    )
    return min(_int(spec["class_cap"], 1, minimum=1), available)


def _recipe_available_class(player_data: Mapping[str, Any], recipe_id: str) -> int:
    level = _int(
        player_data.get(STEALING_CREATION_RECIPES[recipe_id]["skill_level_key"]),
        1,
        minimum=1,
    )
    return max(
        tier
        for tier, requirement in STEALING_CREATION_CLASS_REQUIREMENTS.items()
        if level >= requirement
    )


def _casual_gather_plan(player_data: Mapping[str, Any]) -> tuple[str, int]:
    method_id = max(
        STEALING_CREATION_GATHER_METHODS,
        key=lambda candidate: (
            _available_class(player_data, candidate),
            candidate != "fragments",
            candidate,
        ),
    )
    essential_class = min(
        _recipe_available_class(player_data, recipe_id)
        for recipe_id in ("hatchet", "scimitar", "platebody", "barrier")
    )
    return method_id, min(_available_class(player_data, method_id), essential_class)


def stealing_creation_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_stealing_creation_state_pure(player_data.get("stealing_creation"))
    session = state["active_session"]
    casual_method_id, casual_class = _casual_gather_plan(player_data)
    tools = []
    for kind in ("morphic", "volatile"):
        tool = state["reward_tools"].get(kind, {})
        form = STEALING_CREATION_REWARD_FORM_BY_ID.get(str(tool.get("form_id", "")))
        tools.append(
            {
                "kind": kind,
                "display_name": "Morphic proto-tool" if kind == "morphic" else "Volatile clay tool",
                "owned": bool(tool),
                "active": state["active_reward_tool"] == kind,
                "form_id": form.id if form else "",
                "form_name": form.display_name if form else "",
                "charge_percent": int(round(_float(tool.get("charge")) * 100)) if tool else 0,
            }
        )
    return {
        **state,
        "active": bool(session),
        "reviews_remaining": max(
            0,
            STEALING_CREATION_SESSION_REVIEWS - _int(session.get("review")),
        )
        if session
        else STEALING_CREATION_SESSION_REVIEWS,
        "gather_methods": tuple(
            {
                "id": method_id,
                "display_name": spec["display_name"],
                "available_class": _available_class(player_data, method_id),
            }
            for method_id, spec in STEALING_CREATION_GATHER_METHODS.items()
        ),
        "recipes": tuple(
            {
                "id": recipe_id,
                "display_name": spec["display_name"],
                "available_class": _recipe_available_class(player_data, recipe_id),
            }
            for recipe_id, spec in STEALING_CREATION_RECIPES.items()
        ),
        "reward_forms": tuple(
            {"id": form.id, "display_name": form.display_name}
            for form in STEALING_CREATION_REWARD_FORMS
        ),
        "tools": tuple(tools),
        "reward_cost": STEALING_CREATION_REWARD_COST,
        "casual_plan": {
            "method_id": casual_method_id,
            "method_name": STEALING_CREATION_GATHER_METHODS[casual_method_id][
                "display_name"
            ],
            "clay_class": casual_class,
        },
    }


def _active_follower(player_data: Mapping[str, Any]) -> Mapping[str, Any]:
    state = player_data.get("summoning_state")
    follower = state.get("active_follower") if isinstance(state, Mapping) else None
    return follower if isinstance(follower, Mapping) else {}


def _dismiss_follower(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool]:
    follower = _active_follower(player_data)
    kind = str(follower.get("kind", ""))
    if not kind:
        return copy.deepcopy(dict(player_data)), True
    if kind == "familiar":
        updated, ok, _info = dismiss_familiar_pure(player_data)
        return updated, ok
    if kind == "pet":
        updated, ok = store_active_pet_pure(player_data, location="bank")
        return updated, ok
    return copy.deepcopy(dict(player_data)), False


def _next_raid_review(current: int, rng: Callable[[], float] | None) -> int:
    low, high = STEALING_CREATION_RAID_INTERVAL_REVIEWS
    interval = low + int(_rng_value(rng) * (high - low + 1))
    return min(STEALING_CREATION_SESSION_REVIEWS, current + interval)


def start_stealing_creation_session_pure(
    player_data: Mapping[str, Any],
    rng: Callable[[], float] | None = None,
    *,
    confirm_dismiss_follower: bool = False,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = ensure_stealing_creation_state_pure(player_data)
    state = data["stealing_creation"]
    if state["active_session"]:
        data["activity_session"] = {"active_id": STEALING_CREATION_ACTIVITY_ID}
        data["current_utility"] = STEALING_CREATION_ACTIVITY_ID
        return data, True, {"started": False, "resumed": True}
    activity_session = data.get("activity_session", {})
    active_id = str(activity_session.get("active_id", "")) if isinstance(activity_session, Mapping) else ""
    if active_id and active_id != STEALING_CREATION_ACTIVITY_ID:
        return data, False, {"reason": "Finish the active persistent activity first."}
    encounter = data.get("combat_encounter")
    if isinstance(encounter, Mapping) and encounter:
        return data, False, {"reason": "Finish or leave the current Combat encounter first."}
    if _active_follower(data) and not confirm_dismiss_follower:
        return data, False, {
            "reason": "Stealing Creation does not admit outside followers.",
            "requires_confirmation": True,
        }
    if _active_follower(data):
        data, ok = _dismiss_follower(data)
        if not ok:
            return data, False, {"reason": "The active follower could not be dismissed."}
        state = data["stealing_creation"]
    maximum = combat_max_lifepoints_pure(data)
    state["active_session"] = {
        "active": True,
        "review": 0,
        "player_score": 0,
        "opponent_score": 0,
        "clay": {str(tier): 0 for tier in range(1, 6)},
        "equipment": {slot: 0 for slot in ("tool", "weapon", "armour", "barrier")},
        "barrier_pieces": 0,
        "barrier_piece_tier": 0,
        "barrier_durability": 0,
        "lifepoints": maximum,
        "raider": {},
        "combat_encounter": {},
        "next_raid_review": _next_raid_review(0, rng),
        "raids_won": 0,
        "gathered": 0,
        "processed": 0,
        "deposited": 0,
        "last_action": "Entered the temporary battlefield.",
    }
    state["games"] += 1
    state["last_result"] = "Stealing Creation session started."
    data["stealing_creation"] = state
    data["activity_session"] = {"active_id": STEALING_CREATION_ACTIVITY_ID}
    data["current_utility"] = STEALING_CREATION_ACTIVITY_ID
    return data, True, {"started": True}


def _highest_clay(session: Mapping[str, Any], maximum: int = 5) -> int:
    clay = session.get("clay", {})
    clay = clay if isinstance(clay, Mapping) else {}
    return next(
        (tier for tier in range(min(5, maximum), 0, -1) if _int(clay.get(str(tier))) > 0),
        0,
    )


def _gather(
    data: dict[str, Any], state: dict[str, Any], session: dict[str, Any]
) -> dict[str, Any]:
    if state["automation_mode"] == "casual":
        method_id, tier = _casual_gather_plan(data)
    else:
        method_id = state["selected_gather_method"]
        available = _available_class(data, method_id)
        tier = min(available, state["selected_class"])
    quantity = STEALING_CREATION_CLAY_PER_GATHER_REVIEW * (
        2 if _int(session["equipment"].get("tool")) > 0 else 1
    )
    session["clay"][str(tier)] += quantity
    session["gathered"] += quantity
    score = STEALING_CREATION_SCORE_PER_CLASS * tier * quantity
    session["player_score"] += score
    return {
        "action": "gather",
        "tier": tier,
        "quantity": quantity,
        "score": score,
        "status": f"Gathered {quantity} class {tier} sacred clay (+{score} score)",
    }


def _casual_recipe(session: Mapping[str, Any]) -> str:
    equipment = session.get("equipment", {})
    equipment = equipment if isinstance(equipment, Mapping) else {}
    if _int(equipment.get("tool")) <= 0:
        return "hatchet"
    if _int(equipment.get("weapon")) <= 0:
        return "scimitar"
    if _int(equipment.get("armour")) <= 0:
        return "platebody"
    if _int(equipment.get("barrier")) <= 0:
        return "barrier"
    return "scimitar"


def _process(
    data: dict[str, Any], state: dict[str, Any], session: dict[str, Any]
) -> dict[str, Any]:
    recipe_id = state["selected_recipe"] if state["automation_mode"] == "advanced" else _casual_recipe(session)
    available = _recipe_available_class(data, recipe_id)
    tier = _highest_clay(session, available)
    if tier <= 0:
        return _gather(data, state, session)
    session["clay"][str(tier)] -= 1
    session["processed"] += 1
    score = STEALING_CREATION_SCORE_PER_CLASS * tier
    session["player_score"] += score
    slot = str(STEALING_CREATION_RECIPES[recipe_id]["session_slot"])
    if slot == "barrier":
        if session["barrier_piece_tier"] not in {0, tier}:
            session["barrier_pieces"] = 0
        session["barrier_piece_tier"] = tier
        session["barrier_pieces"] += 1
        if session["barrier_pieces"] >= 4:
            session["equipment"]["barrier"] = max(session["equipment"]["barrier"], tier)
            session["barrier_durability"] = max(session["barrier_durability"], tier * 2)
            session["barrier_pieces"] = 0
            session["barrier_piece_tier"] = 0
            detail = "completed a four-piece barrier"
        else:
            detail = f"made barrier piece {session['barrier_pieces']}/4"
    else:
        session["equipment"][slot] = max(session["equipment"][slot], tier)
        detail = f"equipped class {tier} {recipe_id}"
    return {
        "action": "process",
        "tier": tier,
        "recipe_id": recipe_id,
        "score": score,
        "status": f"Kiln: {detail} (+{score} score)",
    }


def _deposit(session: dict[str, Any]) -> dict[str, Any]:
    deposited = 0
    score = 0
    for tier in range(1, 6):
        quantity = _int(session["clay"].get(str(tier)))
        deposited += quantity
        score += STEALING_CREATION_SCORE_PER_CLASS * tier * quantity
        session["clay"][str(tier)] = 0
    if deposited <= 0:
        return {"action": "deposit", "score": 0, "status": "The deposit table was empty."}
    session["deposited"] += deposited
    session["player_score"] += score
    return {
        "action": "deposit",
        "quantity": deposited,
        "score": score,
        "status": f"Deposited {deposited} sacred clay (+{score} score)",
    }


def _casual_duty(session: Mapping[str, Any]) -> str:
    equipment = session.get("equipment", {})
    if not isinstance(equipment, Mapping):
        return "gather"
    clay_total = sum(_int(value) for value in (session.get("clay", {}) or {}).values())
    if (
        _int(equipment.get("tool")) <= 0
        or _int(equipment.get("weapon")) <= 0
        or _int(equipment.get("armour")) <= 0
        or _int(equipment.get("barrier")) <= 0
    ):
        return "process" if clay_total > 0 else "gather"
    return "deposit" if clay_total >= 2 else "gather"


def _opponent_score(session: dict[str, Any], rng: Callable[[], float] | None) -> int:
    # Each opposing duty beat uses the source 15-per-class score, an explicit
    # five-clay batch, and a bounded class 1-5 population draw.
    tier = 1 + min(4, int(_rng_value(rng) * 5))
    gained = (
        STEALING_CREATION_SCORE_PER_CLASS
        * tier
        * STEALING_CREATION_OPPONENT_CLAY_PER_REVIEW
    )
    session["opponent_score"] += gained
    return gained


def _start_raider(
    data: Mapping[str, Any], session: dict[str, Any], rng: Callable[[], float] | None
) -> None:
    opponent = generate_fist_of_guthix_opponent_pure(data, rng)
    stats = opponent["stats"]
    tier = max(1, min(5, (_int(opponent["combat_level"], 3, minimum=3) + 26) // 27))
    session["raider"] = {
        **opponent,
        "display_name": f"Creation raider (level {_int(opponent['combat_level'], 3)})",
        "tier": tier,
        "max_lifepoints": max(75, _int(stats.get("constitution"), 10) * 3),
    }
    session["combat_encounter"] = {}


def _session_enemy(session: Mapping[str, Any]) -> dict[str, Any]:
    raider = session["raider"]
    stats = raider["stats"]
    barrier_tier = _int(session.get("equipment", {}).get("barrier"))
    barrier_active = _int(session.get("barrier_durability")) > 0
    pressure_scale = max(0.5, 1.0 - (0.1 * barrier_tier)) if barrier_active else 1.0
    return {
        "display_name": str(raider.get("display_name", "Creation raider")),
        "level": _int(raider.get("combat_level"), 3, minimum=3),
        "group": "Stealing Creation",
        "stats": {
            "attack": max(1, int(_int(stats.get("attack"), 1, minimum=1) * pressure_scale)),
            "strength": max(1, int(_int(stats.get("strength"), 1, minimum=1) * pressure_scale)),
            "defence": _int(stats.get("defence"), 1, minimum=1),
            "magic": _int(stats.get("magic"), 1, minimum=1),
            "ranged": _int(stats.get("ranged"), 1, minimum=1),
            "hitpoints": _int(raider.get("max_lifepoints"), 100, minimum=1),
        },
        "bonuses": {},
        "attack_style": "melee",
        "attack_speed": 4,
        "max_hit": max(10, int(_int(raider.get("combat_level"), 3) * 2.5 * pressure_scale)),
        "drops": {"guaranteed": (), "tables": ()},
        "slayer_xp": 0.0,
        "source": "FoG bounded opponent pool; Stealing Creation six-tick raid abstraction",
    }


def _highest_session_item(session: Mapping[str, Any]) -> tuple[str, int]:
    equipment = session.get("equipment", {})
    equipment = equipment if isinstance(equipment, Mapping) else {}
    candidates = [
        (str(slot), _int(tier)) for slot, tier in equipment.items() if _int(tier) > 0
    ]
    for tier, quantity in (session.get("clay", {}) or {}).items():
        if _int(quantity) > 0:
            candidates.append((f"clay:{tier}", _int(tier)))
    return max(candidates, key=lambda row: (row[1], row[0])) if candidates else ("", 0)


def _apply_safe_death_loss(session: dict[str, Any], *, protect_item: bool) -> int:
    protected, _tier = _highest_session_item(session) if protect_item else ("", 0)
    lost_score = 0
    for tier in range(1, 6):
        quantity = _int(session["clay"].get(str(tier)))
        if protected == f"clay:{tier}" and quantity > 0:
            quantity -= 1
            session["clay"][str(tier)] = 1
        else:
            session["clay"][str(tier)] = 0
        lost_score += STEALING_CREATION_SCORE_PER_CLASS * tier * quantity
    for slot in tuple(session["equipment"]):
        if protected != slot:
            session["equipment"][slot] = 0
    if protected != "barrier":
        session["barrier_durability"] = 0
    session["barrier_pieces"] = 0
    session["barrier_piece_tier"] = 0
    session["opponent_score"] += lost_score
    return lost_score


def _raid_review(
    data: dict[str, Any],
    state: dict[str, Any],
    session: dict[str, Any],
    rng: Callable[[], float] | None,
) -> dict[str, Any]:
    if not session["raider"]:
        _start_raider(data, session, rng)
    raider = session["raider"]
    temp = copy.deepcopy(data)
    weapon_tier = _int(session["equipment"].get("weapon"))
    armour_tier = _int(session["equipment"].get("armour"))
    temp["equipment"] = {}
    if weapon_tier:
        temp["equipment"]["weapon"] = f"Sacred clay scimitar (class {weapon_tier})"
    if armour_tier:
        temp["equipment"]["body"] = f"Sacred clay platebody (class {armour_tier})"
    temp["current_combat_target"] = STEALING_CREATION_COMBAT_TARGET_ID
    temp["combat_attack_style"] = "accurate"
    temp["combat_lifepoints"] = _int(session["lifepoints"], 100, minimum=1)
    temp["combat_encounter"] = copy.deepcopy(session["combat_encounter"])
    temp["inventory"] = {}
    temp["combat_current_levels"] = {}
    temp["combat_status_effects"] = {}
    temp["combat_auto_eat_food"] = []
    temp["combat_auto_flee"] = False
    temp["combat_auto_flee_percent"] = 0
    temp["combat_selected_prayers"] = []
    temp["combat_vengeance"] = False
    temp["combat_dream_thrift"] = False
    temp["combat_spellbook_swap"] = ""
    temp["combat_supply_loadout"] = {
        "food": {},
        "potions": {},
        "stat_potions": {},
        "ammo": {},
        "runes": {},
        "finishers": {},
        "hazards": {},
        "cannonballs": 0,
    }
    updated, ok, result = apply_combat_burst_pure(
        temp,
        {STEALING_CREATION_COMBAT_TARGET_ID: _session_enemy(session)},
        STEALING_CREATION_SESSION_EQUIPMENT,
        ticks=STEALING_CREATION_COMBAT_TICKS_PER_REVIEW,
        rng=rng,
        live_cadence=True,
        stop_after_first_kill=True,
        safe_death=True,
        allow_bank_run=False,
    )
    if not ok:
        session["raider"] = {}
        session["combat_encounter"] = {}
        session["next_raid_review"] = _next_raid_review(session["review"], rng)
        return {"action": "raid", "status": "The simulated raider disengaged."}
    session["lifepoints"] = _int(updated.get("combat_lifepoints"), session["lifepoints"], minimum=1)
    session["combat_encounter"] = copy.deepcopy(updated.get("combat_encounter", {}))
    if _int(session.get("barrier_durability")) > 0:
        session["barrier_durability"] -= 1
        if session["barrier_durability"] <= 0:
            session["equipment"]["barrier"] = 0
    if result.get("died"):
        protected = bool(prayer_effect_state_pure(data).get("protect_item"))
        transferred = _apply_safe_death_loss(session, protect_item=protected)
        session["lifepoints"] = combat_max_lifepoints_pure(data)
        session["raider"] = {}
        session["combat_encounter"] = {}
        state["deaths"] += 1
        session["next_raid_review"] = _next_raid_review(session["review"], rng)
        return {
            "action": "raid",
            "died": True,
            "transferred_score": transferred,
            "status": f"Safe death: carried clay worth {transferred} score went to the opposing team.",
        }
    if result.get("killed"):
        session["raider"] = {}
        session["combat_encounter"] = {}
        session["raids_won"] += 1
        session["next_raid_review"] = _next_raid_review(session["review"], rng)
        return {
            "action": "raid",
            "killed": True,
            "status": f"Defeated {raider['display_name']} with the temporary loadout.",
        }
    if result.get("fled"):
        session["raider"] = {}
        session["combat_encounter"] = {}
        session["next_raid_review"] = _next_raid_review(session["review"], rng)
        return {
            "action": "raid",
            "fled": True,
            "status": f"{raider['display_name']} broke off the raid.",
        }
    enemy_lp = _int(session["combat_encounter"].get("enemy_lifepoints"))
    return {
        "action": "raid",
        "status": f"Raid exchange: {enemy_lp:,} raider LP remain.",
    }


def _finish_session(
    data: dict[str, Any], state: dict[str, Any], session: dict[str, Any]
) -> dict[str, Any]:
    player_score = _int(session["player_score"])
    opponent_score = _int(session["opponent_score"])
    outcome = "win" if player_score > opponent_score else "loss" if player_score < opponent_score else "tie"
    reward_score = player_score * 110 // 100 if outcome == "win" else player_score
    points = stealing_creation_points_for_score_pure(reward_score)
    state["points"] += points
    if outcome == "win":
        state["wins"] += 1
    elif outcome == "loss":
        state["losses"] += 1
    else:
        state["ties"] += 1
    state["active_session"] = {}
    state["last_result"] = (
        f"{outcome.title()} {player_score:,}–{opponent_score:,}; +{points} Stealing Creation points."
    )
    data["activity_session"] = _empty_session()
    return {
        "complete": True,
        "outcome": outcome,
        "player_score": player_score,
        "opponent_score": opponent_score,
        "reward_score": reward_score,
        "points": points,
        "status": state["last_result"],
    }


def apply_stealing_creation_review_pure(
    player_data: Mapping[str, Any],
    rng: Callable[[], float] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = ensure_stealing_creation_state_pure(player_data)
    state = data["stealing_creation"]
    session = state["active_session"]
    if not session:
        return data, False, {"reason": "Enter Stealing Creation before training."}
    session["review"] += 1
    opposing_gain = _opponent_score(session, rng)
    if session["raider"] or session["review"] >= session["next_raid_review"]:
        result = _raid_review(data, state, session, rng)
    else:
        duty = state["selected_duty"] if state["automation_mode"] == "advanced" else _casual_duty(session)
        if duty == "process":
            result = _process(data, state, session)
        elif duty == "deposit":
            result = _deposit(session)
        else:
            result = _gather(data, state, session)
    session["last_action"] = str(result.get("status", ""))[:240]
    result["opponent_score_gained"] = opposing_gain
    if session["review"] >= STEALING_CREATION_SESSION_REVIEWS:
        result.update(_finish_session(data, state, session))
    else:
        state["active_session"] = session
    data["stealing_creation"] = state
    return data, True, result


def _award_inventory(data: dict[str, Any], item_name: str, amount: int) -> None:
    inventory = dict(data.get("inventory", {}) or {})
    inventory[item_name] = _int(inventory.get(item_name)) + amount
    data["inventory"] = inventory


def _remove_inventory(data: dict[str, Any], item_name: str, amount: int) -> None:
    inventory = dict(data.get("inventory", {}) or {})
    inventory[item_name] = max(0, _int(inventory.get(item_name)) - amount)
    data["inventory"] = inventory


def purchase_stealing_creation_tool_pure(
    player_data: Mapping[str, Any],
    kind: str,
    *,
    form_id: str = "hammer",
    rng: Callable[[], float] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = ensure_stealing_creation_state_pure(player_data)
    state = data["stealing_creation"]
    if kind not in _TOOL_ITEM_NAMES:
        return data, False, {"reason": "Unknown Stealing Creation reward tool."}
    if state["reward_tools"].get(kind):
        return data, False, {"reason": "Use the owned tool before buying another of that type."}
    if state["points"] < STEALING_CREATION_REWARD_COST:
        return data, False, {"reason": f"Need {STEALING_CREATION_REWARD_COST} Stealing Creation points."}
    if kind == "morphic" and form_id not in STEALING_CREATION_REWARD_FORM_BY_ID:
        return data, False, {"reason": "Choose a valid morphic tool form."}
    selected = form_id if kind == "morphic" else _random_form_id(rng)
    state["points"] -= STEALING_CREATION_REWARD_COST
    state["reward_tools"][kind] = {
        "kind": kind,
        "form_id": selected,
        "charge": 1.0,
        "segments_used": 0,
    }
    state["active_reward_tool"] = kind
    _award_inventory(data, _TOOL_ITEM_NAMES[kind], 1)
    state["last_result"] = f"Bought and activated {_TOOL_ITEM_NAMES[kind]}."
    data["stealing_creation"] = state
    return data, True, {"kind": kind, "form_id": selected, "status": state["last_result"]}


def apply_stealing_creation_xp_bonus_pure(
    player_data: Mapping[str, Any],
    exp_key: str,
    base_xp: float,
    rng: Callable[[], float] | None = None,
    *,
    action_skill_id: str | None = None,
) -> tuple[dict[str, Any], float, dict[str, Any]]:
    data = ensure_stealing_creation_state_pure(player_data)
    state = data["stealing_creation"]
    kind = state["active_reward_tool"]
    tool = state["reward_tools"].get(kind, {}) if kind else {}
    form = STEALING_CREATION_REWARD_FORM_BY_ID.get(str(tool.get("form_id", "")))
    base = max(0.0, _float(base_xp))
    if not tool or form is None or exp_key not in form.exp_keys or base <= 0:
        return data, 0.0, {"applied": False}
    exp_skill_id = exp_key.removesuffix("_exp")
    if action_skill_id is not None and str(action_skill_id).lower() != exp_skill_id:
        return data, 0.0, {
            "applied": False,
            "reason": "tool_not_used_by_action_family",
        }
    if kind == "volatile":
        level_key = exp_key.removesuffix("_exp") + "_level"
        if _int(data.get(level_key), 1, minimum=1) < 40:
            return data, 0.0, {
                "applied": False,
                "reason": "volatile_level_40",
            }
    multiplier = 1.0 if kind == "morphic" else 1.2
    capacity = dict(form.bonus_xp_capacity_by_exp_key).get(
        exp_key,
        form.bonus_xp_capacity,
    )
    remaining_bonus = _float(tool["charge"]) * capacity
    bonus = min(base * multiplier, remaining_bonus)
    old_charge = _float(tool["charge"])
    new_charge = max(0.0, old_charge - bonus / capacity)
    old_segments = min(10, int((1.0 - old_charge + 1e-12) * 10))
    new_segments = min(10, int((1.0 - new_charge + 1e-12) * 10))
    transformed = False
    if kind == "volatile" and new_charge > 0 and new_segments > old_segments:
        tool["form_id"] = _random_form_id(rng)
        transformed = True
    tool["charge"] = new_charge
    tool["segments_used"] = new_segments
    crumbled = new_charge <= 0
    if crumbled:
        _remove_inventory(data, _TOOL_ITEM_NAMES[kind], 1)
        state["reward_tools"][kind] = {}
        state["active_reward_tool"] = ""
    else:
        state["reward_tools"][kind] = tool
    data["stealing_creation"] = state
    return data, bonus, {
        "applied": True,
        "kind": kind,
        "form_id": form.id,
        "bonus_xp": bonus,
        "charge": new_charge,
        "transformed": transformed,
        "next_form_id": str(tool.get("form_id", "")) if not crumbled else "",
        "crumbled": crumbled,
    }


def stealing_creation_tool_can_apply_pure(
    player_data: Mapping[str, Any],
    exp_key: str,
    action_skill_id: str,
) -> bool:
    """Fast hot-path gate before the immutable reward reducer copies a save."""
    state = player_data.get("stealing_creation")
    if not isinstance(state, Mapping):
        return False
    kind = str(state.get("active_reward_tool", ""))
    tools = state.get("reward_tools")
    tool = tools.get(kind) if isinstance(tools, Mapping) else None
    if not isinstance(tool, Mapping) or _float(tool.get("charge")) <= 0:
        return False
    form = STEALING_CREATION_REWARD_FORM_BY_ID.get(str(tool.get("form_id", "")))
    if form is None or exp_key not in form.exp_keys:
        return False
    skill_id = exp_key.removesuffix("_exp")
    if str(action_skill_id).lower() != skill_id:
        return False
    if kind == "volatile" and _int(player_data.get(f"{skill_id}_level"), 1) < 40:
        return False
    return True


def apply_stealing_creation_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
    rng: Callable[[], float] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    payload = payload if isinstance(payload, Mapping) else {}
    data = ensure_stealing_creation_state_pure(player_data)
    state = data["stealing_creation"]
    if action_id == "enter":
        return start_stealing_creation_session_pure(
            data,
            rng,
            confirm_dismiss_follower=bool(payload.get("confirm_dismiss_follower", False)),
        )
    if action_id == "leave":
        if not state["active_session"]:
            return data, False, {"reason": "No Stealing Creation session is active."}
        state["active_session"] = {}
        state["last_result"] = "Left Stealing Creation; temporary clay and equipment vanished."
        data["stealing_creation"] = state
        data["activity_session"] = _empty_session()
        return data, True, {"status": state["last_result"], "forfeited": True}
    if action_id == "set_policy":
        mode = str(payload.get("automation_mode", state["automation_mode"]))
        duty = str(payload.get("selected_duty", state["selected_duty"]))
        method = str(payload.get("selected_gather_method", state["selected_gather_method"]))
        recipe = str(payload.get("selected_recipe", state["selected_recipe"]))
        selected_class = min(5, _int(payload.get("selected_class", state["selected_class"]), 1, minimum=1))
        if mode not in _VALID_MODES or duty not in _VALID_DUTIES:
            return data, False, {"reason": "Choose a valid automation mode and duty."}
        if method not in STEALING_CREATION_GATHER_METHODS or recipe not in STEALING_CREATION_RECIPES:
            return data, False, {"reason": "Choose a valid gathering route and kiln recipe."}
        state.update(
            {
                "automation_mode": mode,
                "selected_duty": duty,
                "selected_gather_method": method,
                "selected_recipe": recipe,
                "selected_class": selected_class,
            }
        )
        data["stealing_creation"] = state
        return data, True, {"status": "Stealing Creation policy updated."}
    if action_id == "buy_tool":
        return purchase_stealing_creation_tool_pure(
            data,
            str(payload.get("kind", "")),
            form_id=str(payload.get("form_id", "hammer")),
            rng=rng,
        )
    if action_id == "activate_tool":
        kind = str(payload.get("kind", ""))
        if kind not in {"", "morphic", "volatile"}:
            return data, False, {"reason": "Unknown reward tool."}
        if kind and not state["reward_tools"].get(kind):
            return data, False, {"reason": "That reward tool is not owned."}
        state["active_reward_tool"] = kind
        data["stealing_creation"] = state
        return data, True, {"status": "Reward tool selection updated."}
    if action_id == "morph_tool":
        form_id = str(payload.get("form_id", ""))
        tool = state["reward_tools"].get("morphic", {})
        if not tool:
            return data, False, {"reason": "No morphic proto-tool is owned."}
        if form_id not in STEALING_CREATION_REWARD_FORM_BY_ID:
            return data, False, {"reason": "Choose a valid morphic form."}
        tool["form_id"] = form_id
        state["reward_tools"]["morphic"] = tool
        data["stealing_creation"] = state
        return data, True, {"status": "Morphic proto-tool transformed.", "form_id": form_id}
    return data, False, {"reason": "Unknown Stealing Creation action."}
