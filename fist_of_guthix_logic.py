"""Pure Fist of Guthix match, reward-shop, and presentation logic."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

try:
    from .combat_data import COMBAT_MAGIC_SPELL_DATA
    from .equipment_data import EQUIPMENT_DATA
    from .equipment_instance_logic import (
        add_equipment_instance_pure,
        advance_equipped_condition_pure,
        condition_name_pure,
        sanitize_equipment_instance_state_pure,
    )
    from .fist_of_guthix_data import (
        FIST_OF_GUTHIX_ACTIVITY_ID,
        FIST_OF_GUTHIX_CHARGE_CAP,
        FIST_OF_GUTHIX_COMBAT_TICKS_PER_REVIEW,
        FIST_OF_GUTHIX_CONDITION_DATA,
        FIST_OF_GUTHIX_INITIAL_RATING,
        FIST_OF_GUTHIX_INITIAL_SUPPLIES,
        FIST_OF_GUTHIX_REWARDS,
        FIST_OF_GUTHIX_ROUND_TICKS,
        FIST_OF_GUTHIX_STANCES,
    )
    from .logic_pure import apply_combat_burst_pure, combat_max_lifepoints_pure
except ImportError:  # pragma: no cover - flat imports used by tests
    from combat_data import COMBAT_MAGIC_SPELL_DATA  # type: ignore
    from equipment_data import EQUIPMENT_DATA  # type: ignore
    from equipment_instance_logic import (  # type: ignore
        add_equipment_instance_pure,
        advance_equipped_condition_pure,
        condition_name_pure,
        sanitize_equipment_instance_state_pure,
    )
    from fist_of_guthix_data import (  # type: ignore
        FIST_OF_GUTHIX_ACTIVITY_ID,
        FIST_OF_GUTHIX_CHARGE_CAP,
        FIST_OF_GUTHIX_COMBAT_TICKS_PER_REVIEW,
        FIST_OF_GUTHIX_CONDITION_DATA,
        FIST_OF_GUTHIX_INITIAL_RATING,
        FIST_OF_GUTHIX_INITIAL_SUPPLIES,
        FIST_OF_GUTHIX_REWARDS,
        FIST_OF_GUTHIX_ROUND_TICKS,
        FIST_OF_GUTHIX_STANCES,
    )
    from logic_pure import apply_combat_burst_pure, combat_max_lifepoints_pure  # type: ignore


FIST_OF_GUTHIX_STATE_VERSION = 1
_ELEMENTAL_RUNES = frozenset({"Air rune", "Water rune", "Earth rune", "Fire rune"})
_STONE_SPEC = {
    "slot": "weapon",
    "two_handed": True,
    "equipment_type": "fist_of_guthix_stone",
    "bonuses": {},
    "attack_speed": 4,
    "weapon_type": -1,
    "skill_requirements": (),
}


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
    return max(0.0, min(0.999999999, _float(value)))


def _rng_value(rng: Callable[[], float] | None) -> float:
    if rng is None:
        return 0.5
    try:
        return _unit(rng())
    except (TypeError, ValueError, StopIteration):
        return 0.5


def default_fist_of_guthix_state_pure() -> dict[str, Any]:
    return {
        "version": FIST_OF_GUTHIX_STATE_VERSION,
        "tutorial_complete": False,
        "automation_mode": "casual",
        "selected_stance": "hybrid",
        "tokens": 0,
        "rating": FIST_OF_GUTHIX_INITIAL_RATING,
        "forfeit_penalty": False,
        "matches_started": 0,
        "wins": 0,
        "losses": 0,
        "ties": 0,
        "forfeits": 0,
        "active_match": {},
        "match_history": [],
        "last_result": "",
    }


def _sanitize_opponent(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        return {}
    level = min(138, _int(raw.get("combat_level"), 3, minimum=3))
    stats = raw.get("stats", {})
    if not isinstance(stats, Mapping):
        return {}
    return {
        "opponent_id": str(raw.get("opponent_id", "opponent"))[:80],
        "display_name": str(raw.get("display_name", "Simulated opponent"))[:80],
        "combat_level": level,
        "stats": {
            key: min(99, _int(stats.get(key), 1, minimum=1))
            for key in ("attack", "strength", "defence", "constitution", "magic", "ranged")
        },
        "stance": (
            str(raw.get("stance"))
            if str(raw.get("stance")) in FIST_OF_GUTHIX_STANCES
            else "hybrid"
        ),
    }


def _sanitize_match(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        return {}
    opponent = _sanitize_opponent(raw.get("opponent"))
    first_role = str(raw.get("first_player_role", ""))
    round_index = min(2, _int(raw.get("round_index"), 1, minimum=1))
    if not opponent or first_role not in {"hunter", "hunted"}:
        return {}
    expected_role = first_role if round_index == 1 else ("hunted" if first_role == "hunter" else "hunter")
    role = str(raw.get("player_role", expected_role))
    if role != expected_role:
        role = expected_role
    supplies = raw.get("temporary_supplies", {})
    supplies = supplies if isinstance(supplies, Mapping) else {}
    encounter = raw.get("combat_encounter", {})
    results = raw.get("round_results", ())
    return {
        "match_id": str(raw.get("match_id", "fog-match"))[:80],
        "seed": _int(raw.get("seed")),
        "opponent": opponent,
        "first_player_role": first_role,
        "round_index": round_index,
        "player_role": role,
        "player_stance": (
            str(raw.get("player_stance"))
            if str(raw.get("player_stance")) in FIST_OF_GUTHIX_STANCES
            else "hybrid"
        ),
        "round_ticks": min(FIST_OF_GUTHIX_ROUND_TICKS, _int(raw.get("round_ticks"))),
        "player_charges": min(FIST_OF_GUTHIX_CHARGE_CAP, _int(raw.get("player_charges"))),
        "opponent_charges": min(FIST_OF_GUTHIX_CHARGE_CAP, _int(raw.get("opponent_charges"))),
        "player_charge_residual": _int(raw.get("player_charge_residual")) % 5,
        "opponent_charge_residual": _int(raw.get("opponent_charge_residual")) % 5,
        "player_lifepoints": _int(raw.get("player_lifepoints"), 100, minimum=1),
        "combat_encounter": dict(encounter) if isinstance(encounter, Mapping) else {},
        "temporary_supplies": {
            item_name: min(FIST_OF_GUTHIX_INITIAL_SUPPLIES[item_name], _int(supplies.get(item_name)))
            for item_name in FIST_OF_GUTHIX_INITIAL_SUPPLIES
        },
        "round_results": [dict(row) for row in results if isinstance(row, Mapping)][-2:]
        if isinstance(results, (list, tuple))
        else [],
        "hunter_respawns": _int(raw.get("hunter_respawns")),
    }


def sanitize_fist_of_guthix_state_pure(raw: Any) -> dict[str, Any]:
    defaults = default_fist_of_guthix_state_pure()
    source = raw if isinstance(raw, Mapping) else {}
    history = source.get("match_history", ())
    return {
        **defaults,
        "tutorial_complete": bool(source.get("tutorial_complete", False)),
        "automation_mode": "advanced"
        if str(source.get("automation_mode", "casual")) == "advanced"
        else "casual",
        "selected_stance": str(source.get("selected_stance"))
        if str(source.get("selected_stance")) in FIST_OF_GUTHIX_STANCES
        else "hybrid",
        "tokens": _int(source.get("tokens")),
        "rating": _int(source.get("rating"), FIST_OF_GUTHIX_INITIAL_RATING),
        "forfeit_penalty": bool(source.get("forfeit_penalty", False)),
        "matches_started": _int(source.get("matches_started")),
        "wins": _int(source.get("wins")),
        "losses": _int(source.get("losses")),
        "ties": _int(source.get("ties")),
        "forfeits": _int(source.get("forfeits")),
        "active_match": _sanitize_match(source.get("active_match")),
        "match_history": [dict(row) for row in history if isinstance(row, Mapping)][-20:]
        if isinstance(history, (list, tuple))
        else [],
        "last_result": str(source.get("last_result", ""))[:240],
    }


def ensure_fist_of_guthix_state_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    # Shallow on purpose: sanitize_ below rebuilds the one key this owns, and a
    # whole-save deep copy here cost 2.07 ms on every review.
    data = dict(player_data)
    data["fist_of_guthix"] = sanitize_fist_of_guthix_state_pure(
        data.get("fist_of_guthix")
    )
    return data


def _player_combat_level(player_data: Mapping[str, Any]) -> int:
    defence = _int(player_data.get("defense_level"), 1, minimum=1)
    constitution = _int(player_data.get("constitution_level"), 10, minimum=1)
    prayer = _int(player_data.get("prayer_level"), 1, minimum=1)
    summoning = _int(player_data.get("summoning_level"), 1, minimum=1)
    base = (defence + constitution + prayer // 2 + summoning // 2) / 4.0
    melee = (_int(player_data.get("attack_level"), 1) + _int(player_data.get("strength_level"), 1)) * 0.325
    ranged = _int(player_data.get("ranged_level"), 1) * 0.4875
    magic = _int(player_data.get("magic_level"), 1) * 0.4875
    return max(3, min(138, int(base + max(melee, ranged, magic))))


def _total_level(player_data: Mapping[str, Any]) -> int:
    return sum(
        min(120, _int(value, 1, minimum=1))
        for key, value in player_data.items()
        if isinstance(key, str) and key.endswith("_level") and not key.startswith("combat_current_")
    )


def _generate_opponent(player_data: Mapping[str, Any], rng: Callable[[], float] | None) -> dict[str, Any]:
    level_roll = _rng_value(rng)
    variance_roll = _rng_value(rng)
    combat_level = 3 + int((level_roll**1.65) * 135)
    core = max(1, min(99, int(combat_level * 0.78 + (variance_roll - 0.5) * 18)))
    constitution = max(10, min(99, int(combat_level * 0.75 + 8)))
    stance_roll = _rng_value(rng)
    stance = "centre" if stance_roll < 0.34 else "hybrid" if stance_roll < 0.72 else "evasive"
    match_number = _int((player_data.get("fist_of_guthix") or {}).get("matches_started")) + 1
    return {
        "opponent_id": f"fog-opponent-{match_number}-{combat_level}",
        "display_name": f"Arena rival (level {combat_level})",
        "combat_level": combat_level,
        "stats": {
            "attack": core,
            "strength": core,
            "defence": core,
            "constitution": constitution,
            "magic": core,
            "ranged": core,
        },
        "stance": stance,
    }


def generate_fist_of_guthix_opponent_pure(
    player_data: Mapping[str, Any],
    rng: Callable[[], float] | None = None,
) -> dict[str, Any]:
    """Expose the bounded period-shaped opponent pool to sibling minigames."""
    return _generate_opponent(player_data, rng)


def _casual_stance(player_data: Mapping[str, Any], opponent: Mapping[str, Any]) -> str:
    player_level = _player_combat_level(player_data)
    opponent_level = _int(opponent.get("combat_level"), 3, minimum=3)
    if opponent_level >= player_level * 1.25:
        return "evasive"
    if opponent_level <= player_level * 0.75:
        return "centre"
    return "hybrid"


def start_fist_of_guthix_match_pure(
    player_data: Mapping[str, Any], rng: Callable[[], float] | None = None
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = ensure_fist_of_guthix_state_pure(player_data)
    state = data["fist_of_guthix"]
    if not state["tutorial_complete"]:
        return data, False, {"reason": "Talk to Fiara before entering the waiting room."}
    if state["active_match"]:
        return data, False, {"reason": "A Fist of Guthix match is already active."}
    opponent = _generate_opponent(data, rng)
    first_role = "hunter" if _rng_value(rng) < 0.5 else "hunted"
    stance = (
        _casual_stance(data, opponent)
        if state["automation_mode"] == "casual"
        else state["selected_stance"]
    )
    match_number = state["matches_started"] + 1
    state["matches_started"] = match_number
    state["active_match"] = {
        "match_id": f"fog-match-{match_number}",
        "seed": int(_rng_value(rng) * 2_147_483_647),
        "opponent": opponent,
        "first_player_role": first_role,
        "round_index": 1,
        "player_role": first_role,
        "player_stance": stance,
        "round_ticks": 0,
        "player_charges": 0,
        "opponent_charges": 0,
        "player_charge_residual": 0,
        "opponent_charge_residual": 0,
        "player_lifepoints": combat_max_lifepoints_pure(data),
        "combat_encounter": {},
        "temporary_supplies": dict(FIST_OF_GUTHIX_INITIAL_SUPPLIES),
        "round_results": [],
        "hunter_respawns": 0,
    }
    state["last_result"] = f"Paired with {opponent['display_name']}"
    data["fist_of_guthix"] = state
    return data, True, {
        "started": True,
        "opponent": opponent,
        "player_role": first_role,
        "stance": stance,
    }


def _allocate_generic_runes(player_data: Mapping[str, Any], supplies: Mapping[str, Any]) -> dict[str, int]:
    spell_id = str(player_data.get("current_combat_spell", "wind_strike"))
    spell = COMBAT_MAGIC_SPELL_DATA.get(spell_id, {})
    costs = spell.get("rune_cost", {}) if isinstance(spell, Mapping) else {}
    if not isinstance(costs, Mapping) or not costs:
        return {}
    elemental_cost = sum(_int(amount) for rune, amount in costs.items() if rune in _ELEMENTAL_RUNES)
    catalytic_cost = sum(_int(amount) for rune, amount in costs.items() if rune not in _ELEMENTAL_RUNES)
    cast_caps = []
    if elemental_cost:
        cast_caps.append(_int(supplies.get("Elemental rune")) // elemental_cost)
    if catalytic_cost:
        cast_caps.append(_int(supplies.get("Catalytic rune")) // catalytic_cost)
    casts = min(cast_caps) if cast_caps else 0
    return {
        str(rune_name): _int(amount) * casts
        for rune_name, amount in costs.items()
        if isinstance(rune_name, str) and _int(amount) > 0 and casts > 0
    }


def _combat_enemy(active: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    opponent = active["opponent"]
    stats = dict(opponent["stats"])
    if active["player_role"] == "hunted":
        exposure = float(FIST_OF_GUTHIX_STANCES[active["player_stance"]]["exposure_multiplier"])
        stats["attack"] = max(1, int(stats["attack"] * exposure))
        stats["strength"] = max(1, int(stats["strength"] * exposure))
    return {
        "fog_opponent": {
            "display_name": opponent["display_name"],
            "level": opponent["combat_level"],
            "group": "Fist of Guthix",
            "stats": {
                "attack": stats["attack"],
                "strength": stats["strength"],
                "defence": stats["defence"],
                "hitpoints": max(100, stats["constitution"] * 10),
                "magic": stats["magic"],
                "ranged": stats["ranged"],
            },
            "bonuses": {},
            "attack_speed": 4,
            "drops": {"guaranteed": (), "tables": ()},
            "xp_multiplier": 1.0,
            "source": "FoG bounded simulated opponent; cutoff random-pairing contract",
        }
    }


def _condition_inventory(player_data: Mapping[str, Any]) -> dict[str, int]:
    inventory = player_data.get("inventory", {})
    if not isinstance(inventory, Mapping):
        return {}
    return {
        item_name: _int(count)
        for item_name, count in inventory.items()
        if any(
            item_name in spec.get("names_by_percent", {}).values()
            for spec in FIST_OF_GUTHIX_CONDITION_DATA.values()
        )
        and _int(count) > 0
    }


def _build_combat_player(player_data: Mapping[str, Any], active: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    # Shallow on purpose: this synthetic combat player overrides every key the
    # fight writes, and the combat engine rebuilds rather than writes through
    # the rest.
    local = dict(player_data)
    supplies = dict(active["temporary_supplies"])
    local["inventory"] = _condition_inventory(player_data)
    local["current_combat_target"] = "fog_opponent"
    local["combat_encounter"] = dict(active.get("combat_encounter", {}) or {})
    local["combat_lifepoints"] = _int(
        active.get("player_lifepoints"), combat_max_lifepoints_pure(player_data), minimum=1
    )
    local["combat_current_levels"] = {}
    local["combat_status_effects"] = {}
    local["combat_auto_eat_food"] = []
    local["combat_auto_flee"] = False
    local["combat_selected_prayers"] = []
    local["combat_vengeance"] = False
    local["combat_dream_thrift"] = False
    local["combat_spellbook_swap"] = ""
    original_loadout = player_data.get("combat_supply_loadout", {})
    ammo = original_loadout.get("ammo", {}) if isinstance(original_loadout, Mapping) else {}
    local["combat_supply_loadout"] = {
        "food": {},
        "potions": {},
        "stat_potions": {},
        "ammo": dict(ammo) if isinstance(ammo, Mapping) else {},
        "runes": _allocate_generic_runes(player_data, supplies),
        "finishers": {},
        "hazards": {},
        "cannonballs": 0,
    }
    equipment_data = dict(EQUIPMENT_DATA)
    if active["player_role"] == "hunted":
        local["equipment"] = {"weapon": "Stone of power"}
        local["equipment_instances"] = {}
        equipment_data["Stone of power"] = _STONE_SPEC
    return local, equipment_data


def _use_bandage(active: dict[str, Any], maximum_lifepoints: int, roll: float) -> int:
    supplies = active["temporary_supplies"]
    current = _int(active.get("player_lifepoints"), maximum_lifepoints, minimum=1)
    if current > maximum_lifepoints * 0.40 or _int(supplies.get("Bandages")) <= 0:
        return 0
    heal_roll = 10 + int(_unit(roll) * 141)
    healed = min(heal_roll, maximum_lifepoints - current)
    if healed > 0:
        active["player_lifepoints"] = current + healed
        supplies["Bandages"] -= 1
    return healed


def _advance_charges(active: dict[str, Any], ticks: int) -> int:
    if active["player_role"] == "hunted":
        owner = "player"
        stance_id = active["player_stance"]
    else:
        owner = "opponent"
        stance_id = active["opponent"]["stance"]
    charge_key = f"{owner}_charges"
    residual_key = f"{owner}_charge_residual"
    rate = _int(FIST_OF_GUTHIX_STANCES[stance_id]["charges_per_second"])
    numerator = _int(active.get(residual_key)) + rate * 3 * ticks
    gained, residual = divmod(numerator, 5)
    before = _int(active.get(charge_key))
    after = min(FIST_OF_GUTHIX_CHARGE_CAP, before + gained)
    active[charge_key] = after
    active[residual_key] = residual if after < FIST_OF_GUTHIX_CHARGE_CAP else 0
    return after - before


def _winner_tokens(player_data: Mapping[str, Any], charges: int) -> int:
    charge_component = min(10, max(1, (max(1, charges) + 499) // 500))
    level_component = min(8, max(1, (_total_level(player_data) + 249) // 250))
    return 2 + charge_component + level_component


def _finish_match(data: dict[str, Any], result_kind: str) -> dict[str, Any]:
    state = data["fist_of_guthix"]
    active = state["active_match"]
    player_charges = _int(active.get("player_charges"))
    opponent_charges = _int(active.get("opponent_charges"))
    margin = player_charges - opponent_charges
    if result_kind == "forfeit":
        outcome = "forfeit"
        tokens = 0
        rating_delta = -50
        state["forfeits"] += 1
        state["forfeit_penalty"] = True
    elif margin > 0:
        outcome = "win"
        tokens = _winner_tokens(data, player_charges)
        if state["forfeit_penalty"]:
            tokens = max(1, tokens // 2)
        rating_delta = min(50, max(1, margin // 100 + 1))
        state["wins"] += 1
        state["forfeit_penalty"] = False
    elif margin < 0:
        outcome = "loss"
        tokens = 1
        rating_delta = -min(50, max(1, abs(margin) // 100 + 1))
        state["losses"] += 1
        state["forfeit_penalty"] = False
    else:
        outcome = "tie"
        tokens = 1
        rating_delta = -1
        state["ties"] += 1
        state["forfeit_penalty"] = False
    state["tokens"] += tokens
    state["rating"] = max(0, state["rating"] + rating_delta)
    row = {
        "match_id": active.get("match_id", ""),
        "opponent": active["opponent"]["display_name"],
        "outcome": outcome,
        "player_charges": player_charges,
        "opponent_charges": opponent_charges,
        "tokens": tokens,
        "rating_delta": rating_delta,
    }
    state["match_history"] = [*state["match_history"], row][-20:]
    state["last_result"] = (
        f"{outcome.title()} · {player_charges:,}–{opponent_charges:,} charges · "
        f"{tokens} token{'s' if tokens != 1 else ''}"
    )
    state["active_match"] = {}
    data["fist_of_guthix"] = state
    return row


def _finish_round(data: dict[str, Any], reason: str) -> dict[str, Any]:
    state = data["fist_of_guthix"]
    active = state["active_match"]
    row = {
        "round": active["round_index"],
        "hunted": "player" if active["player_role"] == "hunted" else "opponent",
        "charges": active["player_charges"]
        if active["player_role"] == "hunted"
        else active["opponent_charges"],
        "reason": reason,
    }
    active["round_results"] = [*active["round_results"], row][-2:]
    if active["round_index"] >= 2:
        match_result = _finish_match(data, "complete")
        return {"round_complete": True, "match_complete": True, "match_result": match_result, **row}
    active["round_index"] = 2
    active["player_role"] = "hunted" if active["first_player_role"] == "hunter" else "hunter"
    active["round_ticks"] = 0
    active["combat_encounter"] = {}
    active["player_lifepoints"] = combat_max_lifepoints_pure(data)
    active["hunter_respawns"] = 0
    if active["player_role"] == "hunted":
        active["player_stance"] = (
            _casual_stance(data, active["opponent"])
            if state["automation_mode"] == "casual"
            else state["selected_stance"]
        )
    state["active_match"] = active
    data["fist_of_guthix"] = state
    return {
        "round_complete": True,
        "match_complete": False,
        "next_role": active["player_role"],
        **row,
    }


def apply_fist_of_guthix_review_pure(
    player_data: Mapping[str, Any],
    *,
    rng: Callable[[], float] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = ensure_fist_of_guthix_state_pure(player_data)
    state = data["fist_of_guthix"]
    started = False
    if not state["active_match"]:
        data, ok, start_info = start_fist_of_guthix_match_pure(data, rng)
        if not ok:
            return data, False, start_info
        state = data["fist_of_guthix"]
        started = True
    active = state["active_match"]
    maximum_lifepoints = combat_max_lifepoints_pure(data)
    bandage_heal = _use_bandage(active, maximum_lifepoints, _rng_value(rng))
    requested_ticks = FIST_OF_GUTHIX_COMBAT_TICKS_PER_REVIEW
    ticks = min(requested_ticks, FIST_OF_GUTHIX_ROUND_TICKS - active["round_ticks"])
    local, equipment_data = _build_combat_player(data, active)
    combat_updated, ok, combat_result = apply_combat_burst_pure(
        local,
        _combat_enemy(active),
        equipment_data,
        ticks=ticks,
        rng=lambda: _rng_value(rng),
        live_cadence=True,
        stop_after_first_kill=True,
    )
    if not ok:
        return data, False, {
            "reason": "Fist of Guthix combat setup is not runnable.",
            "combat": combat_result,
        }
    elapsed = _int(combat_result.get("ticks_elapsed"))
    active["round_ticks"] += elapsed
    active["combat_encounter"] = dict(combat_updated.get("combat_encounter", {}) or {})
    active["player_lifepoints"] = _int(
        combat_result.get("player_lifepoints"), maximum_lifepoints, minimum=1
    )
    charge_gained = _advance_charges(active, elapsed)
    supplies = active["temporary_supplies"]
    for rune_name, used in dict(combat_result.get("runes_used", {}) or {}).items():
        pool = "Elemental rune" if rune_name in _ELEMENTAL_RUNES else "Catalytic rune"
        supplies[pool] = max(0, _int(supplies.get(pool)) - _int(used))
    # The arena halves all combat XP, including Magic's fixed cast XP. The
    # generic NPC multiplier only scales damage XP, so apply parity here.
    xp_rewards = {
        key: _float(amount) * 0.5
        for key, amount in dict(combat_result.get("xp_rewards", {}) or {}).items()
        if isinstance(key, str) and key.endswith("_exp") and _float(amount) > 0
    }
    for exp_key, amount in xp_rewards.items():
        data[exp_key] = _float(data.get(exp_key)) + amount
    if active["player_role"] == "hunter":
        conditioned, _events = advance_equipped_condition_pure(
            data, elapsed, FIST_OF_GUTHIX_CONDITION_DATA
        )
        data = conditioned
        state = data["fist_of_guthix"]
        active = state["active_match"]
    terminal_reason = ""
    if active["player_role"] == "hunter" and combat_result.get("killed"):
        terminal_reason = "hunted_defeated"
    elif active["player_role"] == "hunted" and combat_result.get("died"):
        terminal_reason = "hunted_defeated"
    elif active["player_role"] == "hunter" and combat_result.get("died"):
        active["hunter_respawns"] += 1
        active["player_lifepoints"] = maximum_lifepoints
        active["combat_encounter"] = {}
    elif active["player_role"] == "hunted" and combat_result.get("killed"):
        active["hunter_respawns"] += 1
        active["combat_encounter"] = {}
    charge_total = active["player_charges"] if active["player_role"] == "hunted" else active["opponent_charges"]
    if not terminal_reason and charge_total >= FIST_OF_GUTHIX_CHARGE_CAP:
        terminal_reason = "charge_cap"
    if not terminal_reason and active["round_ticks"] >= FIST_OF_GUTHIX_ROUND_TICKS:
        terminal_reason = "tick_limit"
    completed_role = active["player_role"]
    completed_stance = (
        active["player_stance"]
        if completed_role == "hunted"
        else active["opponent"]["stance"]
    )
    state["active_match"] = active
    data["fist_of_guthix"] = state
    boundary = _finish_round(data, terminal_reason) if terminal_reason else {}
    result = {
        "started": started,
        "ticks_elapsed": elapsed,
        "player_role": completed_role,
        "stance": completed_stance,
        "charge_gained": charge_gained,
        "charge_total": charge_total,
        "bandage_heal": bandage_heal,
        "temporary_supplies": dict(supplies),
        "xp_rewards": xp_rewards,
        "combat": combat_result,
        **boundary,
    }
    return data, True, result


def _change_bank_instance_condition(
    data: dict[str, Any], family_id: str, *, to_full: bool
) -> tuple[dict[str, Any], bool, str]:
    data = sanitize_equipment_instance_state_pure(data, FIST_OF_GUTHIX_CONDITION_DATA)
    spec = FIST_OF_GUTHIX_CONDITION_DATA[family_id]
    maximum = _int(spec["max_condition"], 1, minimum=1)
    candidates = [
        (instance_id, record)
        for instance_id, record in data["equipment_instances"].items()
        if record.get("family_id") == family_id
        and record.get("location") == "bank"
        and ((_int(record.get("condition")) == 0) if to_full else (_int(record.get("condition")) > 0))
    ]
    if not candidates:
        return data, False, "No eligible copy is in the Bank."
    if to_full:
        instance_id, record = min(candidates, key=lambda row: row[0])
        condition = maximum
    else:
        instance_id, record = min(
            candidates, key=lambda row: (_int(row[1].get("condition")), row[0])
        )
        condition = 0
    before_name = str(record["item_name"])
    after_name = condition_name_pure(family_id, condition, FIST_OF_GUTHIX_CONDITION_DATA)
    inventory = dict(data.get("inventory", {}) or {})
    inventory[before_name] = max(0, _int(inventory.get(before_name)) - 1)
    inventory[after_name] = _int(inventory.get(after_name)) + 1
    record["condition"] = condition
    record["item_name"] = after_name
    data["inventory"] = inventory
    return data, True, instance_id


def apply_fist_of_guthix_command_pure(
    player_data: Mapping[str, Any], action_id: str, payload: Mapping[str, Any] | None = None
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = ensure_fist_of_guthix_state_pure(player_data)
    state = data["fist_of_guthix"]
    payload = payload if isinstance(payload, Mapping) else {}
    if action_id == "talk_fiara":
        if state["tutorial_complete"]:
            return data, False, {"reason": "Fiara has already explained the game."}
        state["tutorial_complete"] = True
        state["last_result"] = "Fiara explained the two-round hunt."
        data["fist_of_guthix"] = state
        return data, True, {"tutorial_complete": True}
    if action_id == "set_policy":
        mode = str(payload.get("automation_mode", state["automation_mode"]))
        stance = str(payload.get("stance", state["selected_stance"]))
        if mode not in {"casual", "advanced"} or stance not in FIST_OF_GUTHIX_STANCES:
            return data, False, {"reason": "Invalid Fist of Guthix policy."}
        if state["active_match"] and state["active_match"].get("round_ticks"):
            return data, False, {"reason": "Change stance before a hunted round begins."}
        state["automation_mode"] = mode
        state["selected_stance"] = stance
        data["fist_of_guthix"] = state
        return data, True, {"automation_mode": mode, "stance": stance}
    if action_id == "tele_orb":
        active = state["active_match"]
        if not active or active.get("player_role") != "hunted":
            return data, False, {"reason": "The Tele-orb is only usable while hunted."}
        supplies = active["temporary_supplies"]
        if _int(supplies.get("Tele-orb")) <= 0:
            return data, False, {"reason": "The Tele-orb has already been used."}
        supplies["Tele-orb"] = 0
        active["player_stance"] = "centre"
        state["active_match"] = active
        data["fist_of_guthix"] = state
        return data, True, {"stance": "centre", "tele_orb_used": True}
    if action_id == "forfeit":
        if not state["active_match"]:
            return data, False, {"reason": "No Fist of Guthix match is active."}
        result = _finish_match(data, "forfeit")
        return data, True, result
    reward_id = str(payload.get("reward_id", ""))
    reward = FIST_OF_GUTHIX_REWARDS.get(reward_id)
    if action_id in {"buy_reward", "recharge_reward", "uncharge_reward"} and reward is None:
        return data, False, {"reason": "Unknown Fist of Guthix reward."}
    if action_id == "buy_reward":
        cost = _int(reward["buy_tokens"])
        if state["tokens"] < cost:
            return data, False, {"reason": f"Need {cost} Fist of Guthix tokens."}
        state["tokens"] -= cost
        data["fist_of_guthix"] = state
        data, instance_id = add_equipment_instance_pure(
            data, reward["family_id"], FIST_OF_GUTHIX_CONDITION_DATA
        )
        return data, True, {"reward_id": reward_id, "instance_id": instance_id, "tokens_spent": cost}
    if action_id == "recharge_reward":
        cost = _int(reward["recharge_tokens"])
        if state["tokens"] < cost:
            return data, False, {"reason": f"Need {cost} Fist of Guthix tokens."}
        data, ok, instance_id = _change_bank_instance_condition(
            data, reward["family_id"], to_full=True
        )
        if not ok:
            return data, False, {"reason": instance_id}
        data["fist_of_guthix"]["tokens"] -= cost
        return data, True, {"reward_id": reward_id, "instance_id": instance_id, "tokens_spent": cost}
    if action_id == "uncharge_reward":
        data, ok, instance_id = _change_bank_instance_condition(
            data, reward["family_id"], to_full=False
        )
        if not ok:
            return data, False, {"reason": instance_id}
        return data, True, {"reward_id": reward_id, "instance_id": instance_id, "tokens_spent": 0}
    return data, False, {"reason": "Unknown Fist of Guthix action."}


def fist_of_guthix_can_review_pure(player_data: Mapping[str, Any]) -> bool:
    state = sanitize_fist_of_guthix_state_pure(player_data.get("fist_of_guthix"))
    return bool(state["tutorial_complete"])


def fist_of_guthix_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    data = sanitize_equipment_instance_state_pure(
        player_data, FIST_OF_GUTHIX_CONDITION_DATA
    )
    state = sanitize_fist_of_guthix_state_pure(data.get("fist_of_guthix"))
    active = state["active_match"]
    instances = data.get("equipment_instances", {})
    instances = instances if isinstance(instances, Mapping) else {}
    reward_rows = []
    for reward_id, reward in FIST_OF_GUTHIX_REWARDS.items():
        bank_copies = tuple(
            record
            for record in instances.values()
            if isinstance(record, Mapping)
            and record.get("family_id") == reward["family_id"]
            and record.get("location") == "bank"
        )
        reward_rows.append(
            {
                "reward_id": reward_id,
                **reward,
                "bank_items": tuple(str(row.get("item_name", "")) for row in bank_copies),
                "can_buy": state["tokens"] >= reward["buy_tokens"],
                "can_recharge": state["tokens"] >= reward["recharge_tokens"]
                and any(_int(row.get("condition")) == 0 for row in bank_copies),
                "can_uncharge": any(_int(row.get("condition")) > 0 for row in bank_copies),
            }
        )
    view = {
        "activity_id": FIST_OF_GUTHIX_ACTIVITY_ID,
        "tutorial_complete": state["tutorial_complete"],
        "automation_mode": state["automation_mode"],
        "selected_stance": state["selected_stance"],
        "stances": tuple(
            {
                "stance_id": stance_id,
                "display_name": spec["display_name"],
                "charges_per_second": spec["charges_per_second"],
            }
            for stance_id, spec in FIST_OF_GUTHIX_STANCES.items()
        ),
        "tokens": state["tokens"],
        "rating": state["rating"],
        "forfeit_penalty": state["forfeit_penalty"],
        "record": {key: state[key] for key in ("wins", "losses", "ties", "forfeits")},
        "active": bool(active),
        "last_result": state["last_result"],
        "rewards": tuple(reward_rows),
    }
    if active:
        view["match"] = {
            "match_id": active["match_id"],
            "opponent": active["opponent"],
            "round_index": active["round_index"],
            "player_role": active["player_role"],
            "stance": active["player_stance"]
            if active["player_role"] == "hunted"
            else active["opponent"]["stance"],
            "round_ticks": active["round_ticks"],
            "round_ticks_remaining": FIST_OF_GUTHIX_ROUND_TICKS - active["round_ticks"],
            "player_charges": active["player_charges"],
            "opponent_charges": active["opponent_charges"],
            "player_lifepoints": active["player_lifepoints"],
            "temporary_supplies": dict(active["temporary_supplies"]),
        }
    else:
        view["match"] = {}
    return view
