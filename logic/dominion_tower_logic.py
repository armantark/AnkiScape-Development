"""Pure, persistent Dominion Tower mechanics.

The tower is a boss-instance family under
`memory-bank/boss-instance-contract-2026-07-18.md`, and its multi-NPC arenas
resolve through `memory-bank/multi-enemy-encounter-contract-2026-07-18.md`: one
engaged target takes the six-tick Combat slice while every other NPA still on the
field applies bounded incoming pressure.

Every rule here is pinned in `data/dominion_tower_data.py` and in
`memory-bank/source-audits/dominion-tower-harvest-2026-07-28.md`.
"""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any

from ..data.dominion_tower_data import (
    DOMINION_TOWER_ACHIEVEMENTS,
    DOMINION_TOWER_ACTIVITY_ID,
    DOMINION_TOWER_ASCENDANCY_KILL_REQUIREMENT,
    DOMINION_TOWER_ASCENDANCY_MINE,
    DOMINION_TOWER_ASCENDANCY_MINES_PER_CLAIM,
    DOMINION_TOWER_BOMBS_PER_MATCH,
    DOMINION_TOWER_BOSS_CLASS_MIN_FLOOR,
    DOMINION_TOWER_CLIMBER,
    DOMINION_TOWER_COLOSSAL_BOMB_FACTOR,
    DOMINION_TOWER_COMBAT_LEVEL_REQUIREMENT,
    DOMINION_TOWER_DREADNIP,
    DOMINION_TOWER_DREADNIP_KILL_REQUIREMENT,
    DOMINION_TOWER_DREADNIP_PER_CREDIT,
    DOMINION_TOWER_ENCOUNTERS,
    DOMINION_TOWER_ENCOUNTERS_BY_ID,
    DOMINION_TOWER_ENDURANCE,
    DOMINION_TOWER_ENDURANCE_REDUCED_DIVISOR,
    DOMINION_TOWER_ENDURANCE_REDUCED_FLOOR,
    DOMINION_TOWER_EXCHANGE_FACTOR_PER_ITEM,
    DOMINION_TOWER_EXCHANGEABLE_ITEMS,
    DOMINION_TOWER_FREESTYLE,
    DOMINION_TOWER_GLOVE_KILL_REQUIREMENT,
    DOMINION_TOWER_GLOVE_SETS,
    DOMINION_TOWER_HANDICAP_NUDGE_LIMIT,
    DOMINION_TOWER_HANDICAP_REDUCTION_FRACTION,
    DOMINION_TOWER_HANDICAP_RESPIN_LIMIT,
    DOMINION_TOWER_HANDICAPS,
    DOMINION_TOWER_HANDICAPS_BY_ID,
    DOMINION_TOWER_HANDICAP_COUNT,
    DOMINION_TOWER_HANDICAP_IDS,
    DOMINION_TOWER_HELP_HORN,
    DOMINION_TOWER_HELP_HORN_USES,
    DOMINION_TOWER_JOURNAL_PAGE,
    DOMINION_TOWER_JOURNAL_PAGE_CHANCE,
    DOMINION_TOWER_JOURNAL_PAGE_COUNT,
    DOMINION_TOWER_LIFE_SAVER_THRESHOLD_PERCENT,
    DOMINION_TOWER_MARKER,
    DOMINION_TOWER_MARKER_STAGE_BOOSTS,
    DOMINION_TOWER_MAX_FACTOR,
    DOMINION_TOWER_MEDALLION,
    DOMINION_TOWER_MINE,
    DOMINION_TOWER_MINE_COST,
    DOMINION_TOWER_MINE_KILL_REQUIREMENT,
    DOMINION_TOWER_MINE_SPECIAL_MATCH_IDS,
    DOMINION_TOWER_MODES_BY_ID,
    DOMINION_TOWER_MONSTER_STUN_TICKS,
    DOMINION_TOWER_NPCS,
    DOMINION_TOWER_POTIONS_BY_ITEM,
    DOMINION_TOWER_POWERUPS_BY_ITEM,
    DOMINION_TOWER_QUEST_POOL,
    DOMINION_TOWER_QUEST_REQUIREMENT,
    DOMINION_TOWER_REWARD_BOX_ITEM_CAP,
    DOMINION_TOWER_REWARD_BOX_ITEMS,
    DOMINION_TOWER_REWARD_BOX_ROLLS,
    DOMINION_TOWER_REWARD_CREDIT_CAP,
    DOMINION_TOWER_REWARD_CREDIT_KILLS,
    DOMINION_TOWER_SCORPION_MEAT,
    DOMINION_TOWER_SCORPION_MEAT_HEAL,
    DOMINION_TOWER_SOURCE,
    DOMINION_TOWER_SPECIAL,
    DOMINION_TOWER_SPECIAL_MATCHES,
    DOMINION_TOWER_SPECIAL_MATCHES_BY_ID,
    DOMINION_TOWER_STAFF_POWERUPS,
    DOMINION_TOWER_SUPER_MEDALLION,
    DOMINION_TOWER_TARGET_ID,
    DOMINION_TOWER_WEAPON_POWERUP_DAMAGE_MULTIPLIER,
    DOMINION_TOWER_WEAPON_POWERUPS,
    DOMINION_TOWER_XP_BOOK,
    DOMINION_TOWER_XP_BOOK_FACTOR_SCALE,
    DOMINION_TOWER_XP_BOOK_SKILL_LEVEL,
    DOMINION_TOWER_XP_BOOK_SKILL_RATIOS,
    DOMINION_TOWER_XP_BOOK_SKILLS,
    RECIPE_FOR_DISASTER_REQUIREMENT_ID,
    RECIPE_FOR_DISASTER_SUBQUESTS,
    dominion_tower_enemy_pure,
)
from ..logic_pure.logic_pure import (
    apply_combat_burst_pure,
    apply_combat_poison_effect_pure,
    apply_combat_stat_delta_pure,
    apply_thieving_damage_pure,
    combat_enemy_pressure_attack_pure,
    combat_max_lifepoints_pure,
    player_combat_level_pure,
)


DOMINION_TOWER_STATE_VERSION = 1
DOMINION_TOWER_REVIEW_TICKS = 6
# Disease "periodically reduces one randomly-chosen skill by 14 points. Disease
# does not affect Constitution."
DOMINION_TOWER_DISEASE_DRAIN = 14
DOMINION_TOWER_DISEASE_SKILLS = (
    "attack",
    "strength",
    "defense",
    "ranged",
    "magic",
    "prayer",
)
_REWARD_ITEMS_BY_UNLOCK = {
    "powerup_help_horn": DOMINION_TOWER_HELP_HORN,
    "super_medallion": DOMINION_TOWER_SUPER_MEDALLION,
}


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


def _roll(rng, default: float = 0.0) -> float:
    try:
        return float(rng())
    except (TypeError, ValueError, OverflowError):
        return default


def _pick(rng, rows):
    rows = tuple(rows)
    if not rows:
        return None
    index = min(len(rows) - 1, int(max(0.0, min(_roll(rng), 0.999999999)) * len(rows)))
    return rows[index]


def _str_list(raw: Any, *, allowed: Any = None, limit: int = 256) -> list[str]:
    if not isinstance(raw, (list, tuple)):
        return []
    out: list[str] = []
    for value in raw:
        if not isinstance(value, str) or value in out:
            continue
        if allowed is not None and value not in allowed:
            continue
        out.append(value)
        if len(out) >= limit:
            break
    return out


# ---------------------------------------------------------------------------
# Quest ledger
# ---------------------------------------------------------------------------


def _quest_complete(player_data: Mapping[str, Any], quest_id: str) -> bool:
    if quest_id == RECIPE_FOR_DISASTER_REQUIREMENT_ID:
        return all(
            _quest_complete(player_data, subquest)
            for subquest in RECIPE_FOR_DISASTER_SUBQUESTS
        )
    quests = player_data.get("quests")
    quest = quests.get(quest_id) if isinstance(quests, Mapping) else None
    return isinstance(quest, Mapping) and bool(quest.get("completed"))


def dominion_tower_completed_quests_pure(
    player_data: Mapping[str, Any],
) -> tuple[str, ...]:
    """Which of the tower's own 38 quests the real ledger says are done."""
    return tuple(
        quest_id
        for quest_id in DOMINION_TOWER_QUEST_POOL
        if _quest_complete(player_data, quest_id)
    )


def dominion_tower_available_encounters_pure(
    player_data: Mapping[str, Any],
    floor: int = 1,
) -> tuple[str, ...]:
    """Bosses the tower can offer: quest complete and the floor gate passed."""
    completed = set(dominion_tower_completed_quests_pure(player_data))
    # The Lair of Tarn Razorlor is a miniquest outside the tower's 38, so its
    # boss is gated on that ledger entry rather than on the pool.
    return tuple(
        row["id"]
        for row in DOMINION_TOWER_ENCOUNTERS
        if (row["quest_id"] in completed or _quest_complete(player_data, row["quest_id"]))
        and max(1, _int(floor, 1, minimum=1)) >= row["min_floor"]
    )


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------


def default_dominion_tower_state_pure() -> dict[str, Any]:
    return {
        "version": DOMINION_TOWER_STATE_VERSION,
        "talked_with_face": False,
        "mode": "",
        "progress": 0,
        "dominion_factor": 0,
        "last_round_factor": 0,
        "total_score": 0,
        "boss_kills": 0,
        "max_floor_climber": 0,
        "max_floor_endurance": 0,
        "encounter_id": "",
        "special_id": "",
        "roster": [],
        "engaged_instance_id": 0,
        "next_instance_id": 1,
        "handicaps": [],
        "suffered_handicaps": [],
        "offer": {},
        "match": {},
        "journal_pages": 0,
        "defeated": {},
        "faced": [],
        "specials_done": [],
        "spectated": False,
        "powerups_used": [],
        "weapon_powerup": {},
        "reward_credits": 0,
        "credit_kill_marker": 0,
        "ascendancy_claims": 0,
        "help_horn_charges": 0,
        "claimed": [],
        "marker_stage": 0,
        "xp_book_factor": 0,
        "previous_combat_target": "",
        "last_result": "",
    }


def _sanitize_member(raw: Any, next_id: int) -> dict[str, Any] | None:
    if not isinstance(raw, Mapping):
        return None
    npc_key = str(raw.get("npc_key", ""))
    if npc_key not in DOMINION_TOWER_NPCS:
        return None
    npc = DOMINION_TOWER_NPCS[npc_key]
    maximum = _int(raw.get("max_lifepoints"), npc["lifepoints"], minimum=1)
    maximum = min(maximum, npc["lifepoints"])
    lifepoints = min(maximum, _int(raw.get("lifepoints"), maximum, minimum=1))
    encounter = raw.get("encounter")
    return {
        "instance_id": _int(raw.get("instance_id"), next_id, minimum=1),
        "npc_key": npc_key,
        "max_lifepoints": maximum,
        "lifepoints": lifepoints,
        "encounter": {
            "target_id": DOMINION_TOWER_TARGET_ID,
            "enemy_lifepoints": lifepoints,
            **(
                {
                    str(key): copy.deepcopy(value)
                    for key, value in encounter.items()
                    if isinstance(key, str)
                    and key not in ("target_id", "enemy_lifepoints")
                }
                if isinstance(encounter, Mapping)
                else {}
            ),
        },
    }


def _sanitize_match(raw: Any) -> dict[str, Any]:
    source = raw if isinstance(raw, Mapping) else {}
    return {
        "stun_ticks": _int(source.get("stun_ticks")),
        "life_saver_used": bool(source.get("life_saver_used", False)),
        "bombs_used": min(
            DOMINION_TOWER_BOMBS_PER_MATCH, _int(source.get("bombs_used"))
        ),
        "survive_ticks": _int(source.get("survive_ticks")),
        "ticks_survived": _int(source.get("ticks_survived")),
        "halved_applied": bool(source.get("halved_applied", False)),
    }


def _sanitize_offer(raw: Any) -> dict[str, Any]:
    source = raw if isinstance(raw, Mapping) else {}
    handicap_id = str(source.get("handicap_id", ""))
    if handicap_id not in DOMINION_TOWER_HANDICAPS_BY_ID:
        return {}
    return {
        "handicap_id": handicap_id,
        "respins_used": min(
            DOMINION_TOWER_HANDICAP_RESPIN_LIMIT, _int(source.get("respins_used"))
        ),
        "nudges_used": min(
            DOMINION_TOWER_HANDICAP_NUDGE_LIMIT, _int(source.get("nudges_used"))
        ),
    }


def sanitize_dominion_tower_state_pure(raw: Any) -> dict[str, Any]:
    defaults = default_dominion_tower_state_pure()
    source = raw if isinstance(raw, Mapping) else {}
    mode = str(source.get("mode", ""))
    if mode not in DOMINION_TOWER_MODES_BY_ID:
        mode = ""
    encounter_id = str(source.get("encounter_id", ""))
    if encounter_id not in DOMINION_TOWER_ENCOUNTERS_BY_ID:
        encounter_id = ""
    special_id = str(source.get("special_id", ""))
    if special_id not in DOMINION_TOWER_SPECIAL_MATCHES_BY_ID:
        special_id = ""
    next_instance_id = _int(source.get("next_instance_id"), 1, minimum=1)
    roster: list[dict[str, Any]] = []
    raw_roster = source.get("roster")
    if isinstance(raw_roster, (list, tuple)):
        for index, entry in enumerate(raw_roster):
            member = _sanitize_member(entry, next_instance_id + index)
            if member is not None:
                roster.append(member)
    if not mode or (not encounter_id and not special_id):
        mode = ""
        encounter_id = ""
        special_id = ""
        roster = []
    next_instance_id = max(
        next_instance_id, *(member["instance_id"] + 1 for member in roster)
    ) if roster else next_instance_id
    engaged = _int(source.get("engaged_instance_id"))
    if engaged not in {member["instance_id"] for member in roster}:
        engaged = roster[0]["instance_id"] if roster else 0
    defeated_raw = source.get("defeated")
    defeated = {
        str(key): _int(value)
        for key, value in (defeated_raw or {}).items()
        if isinstance(key, str)
        and key in DOMINION_TOWER_ENCOUNTERS_BY_ID
        and _int(value) > 0
    } if isinstance(defeated_raw, Mapping) else {}
    weapon_raw = source.get("weapon_powerup")
    weapon: dict[str, Any] = {}
    if isinstance(weapon_raw, Mapping):
        item_name = str(weapon_raw.get("item", ""))
        charges = _int(weapon_raw.get("charges"))
        if item_name in DOMINION_TOWER_WEAPON_POWERUPS and charges > 0:
            weapon = {"item": item_name, "charges": charges}
    boss_kills = _int(source.get("boss_kills"))
    return {
        **defaults,
        "talked_with_face": bool(source.get("talked_with_face", False)),
        "mode": mode,
        "progress": _int(source.get("progress")),
        "dominion_factor": min(
            DOMINION_TOWER_MAX_FACTOR, _int(source.get("dominion_factor"))
        ),
        "last_round_factor": _int(source.get("last_round_factor")),
        "total_score": _int(source.get("total_score")),
        "boss_kills": boss_kills,
        "max_floor_climber": _int(source.get("max_floor_climber")),
        "max_floor_endurance": _int(source.get("max_floor_endurance")),
        "encounter_id": encounter_id,
        "special_id": special_id,
        "roster": roster,
        "engaged_instance_id": engaged,
        "next_instance_id": next_instance_id,
        "handicaps": _str_list(
            source.get("handicaps"), allowed=DOMINION_TOWER_HANDICAPS_BY_ID
        ),
        "suffered_handicaps": _str_list(
            source.get("suffered_handicaps"), allowed=DOMINION_TOWER_HANDICAPS_BY_ID
        ),
        "offer": _sanitize_offer(source.get("offer")) if mode else {},
        "match": _sanitize_match(source.get("match")) if roster else {},
        "journal_pages": min(
            DOMINION_TOWER_JOURNAL_PAGE_COUNT, _int(source.get("journal_pages"))
        ),
        "defeated": defeated,
        "faced": _str_list(source.get("faced"), allowed=DOMINION_TOWER_ENCOUNTERS_BY_ID),
        "specials_done": _str_list(
            source.get("specials_done"), allowed=DOMINION_TOWER_SPECIAL_MATCHES_BY_ID
        ),
        "spectated": bool(source.get("spectated", False)),
        "powerups_used": _str_list(
            source.get("powerups_used"), allowed=set(DOMINION_TOWER_STAFF_POWERUPS)
        ),
        "weapon_powerup": weapon,
        "reward_credits": min(
            DOMINION_TOWER_REWARD_CREDIT_CAP, _int(source.get("reward_credits"))
        ),
        "credit_kill_marker": _int(source.get("credit_kill_marker")),
        "ascendancy_claims": _int(source.get("ascendancy_claims")),
        "help_horn_charges": min(
            DOMINION_TOWER_HELP_HORN_USES, _int(source.get("help_horn_charges"))
        ),
        "claimed": _str_list(source.get("claimed")),
        "marker_stage": min(4, _int(source.get("marker_stage"))),
        "xp_book_factor": _int(source.get("xp_book_factor")),
        "previous_combat_target": str(source.get("previous_combat_target", ""))[:120],
        "last_result": str(source.get("last_result", ""))[:500],
    }


# ---------------------------------------------------------------------------
# Achievements
# ---------------------------------------------------------------------------


def _glove_set_complete(state: Mapping[str, Any], set_id: str) -> bool:
    row = next((s for s in DOMINION_TOWER_GLOVE_SETS if s["id"] == set_id), None)
    if row is None:
        return False
    defeated = state.get("defeated") or {}
    return _int(state.get("boss_kills")) >= DOMINION_TOWER_GLOVE_KILL_REQUIREMENT and all(
        _int(defeated.get(encounter_id)) > 0 for encounter_id in row["encounters"]
    )


def _achievement_met(state: Mapping[str, Any], row: Mapping[str, Any]) -> bool:
    kind = str(row["kind"])
    if kind == "max_floor_climber":
        return _int(state.get("max_floor_climber")) >= _int(row["value"])
    if kind == "max_floor_endurance":
        return _int(state.get("max_floor_endurance")) >= _int(row["value"])
    if kind == "handicaps_suffered":
        return len(state.get("suffered_handicaps") or ()) >= _int(row["value"])
    if kind == "journal_pages":
        return _int(state.get("journal_pages")) >= _int(row["value"])
    if kind == "journal_pages_and_factor":
        return _int(state.get("journal_pages")) >= _int(row["value"]) and _int(
            state.get("dominion_factor")
        ) >= _int(row["factor"])
    if kind == "powerups_used_in_arena":
        return len(state.get("powerups_used") or ()) >= _int(row["value"])
    if kind == "boss_kills":
        return _int(state.get("boss_kills")) >= _int(row["value"])
    if kind == "kills_and_specials":
        return _int(state.get("boss_kills")) >= _int(row["value"]) and set(
            DOMINION_TOWER_MINE_SPECIAL_MATCH_IDS
        ) <= set(state.get("specials_done") or ())
    if kind == "kills_and_spectate":
        return _int(state.get("boss_kills")) >= _int(row["value"]) and bool(
            state.get("spectated")
        )
    if kind == "glove_set":
        return _glove_set_complete(state, str(row["value"]))
    if kind == "all_other_achievements":
        return all(
            _achievement_met(state, other)
            for other in DOMINION_TOWER_ACHIEVEMENTS
            if other["kind"] != "all_other_achievements"
        )
    return False


def dominion_tower_achievements_pure(
    state: Mapping[str, Any],
) -> tuple[dict[str, Any], ...]:
    return tuple(
        {**row, "met": _achievement_met(state, row)}
        for row in DOMINION_TOWER_ACHIEVEMENTS
    )


def _unlocked_rewards(state: Mapping[str, Any]) -> frozenset[str]:
    return frozenset(
        str(row["reward"])
        for row in DOMINION_TOWER_ACHIEVEMENTS
        if _achievement_met(state, row)
    )


def _marker_stage(state: Mapping[str, Any]) -> int:
    unlocked = _unlocked_rewards(state)
    for stage in (4, 3, 2, 1):
        if f"marker_stage_{stage}" in unlocked:
            return stage
    return 0


# ---------------------------------------------------------------------------
# Factor arithmetic
# ---------------------------------------------------------------------------


def _roster_total_level(state: Mapping[str, Any]) -> int:
    return sum(
        _int(DOMINION_TOWER_NPCS[member["npc_key"]]["level"])
        for member in state.get("roster") or ()
    )


def _starting_total_level(state: Mapping[str, Any]) -> int:
    """The arena's own level total: what the factor formula multiplies."""
    encounter_id = str(state.get("encounter_id", ""))
    special_id = str(state.get("special_id", ""))
    if special_id:
        match = DOMINION_TOWER_SPECIAL_MATCHES_BY_ID[special_id]
        return sum(_int(DOMINION_TOWER_NPCS[key]["level"]) for key in match["npcs"])
    if encounter_id:
        row = DOMINION_TOWER_ENCOUNTERS_BY_ID[encounter_id]
        return sum(_int(DOMINION_TOWER_NPCS[key]["level"]) for key in row["npcs"])
    return 0


def dominion_tower_round_factor_pure(state: Mapping[str, Any]) -> int:
    """Darkan's product, adjusted by the wheel's own per-round factor deltas."""
    mode = str(state.get("mode", ""))
    row = DOMINION_TOWER_MODES_BY_ID.get(mode)
    if row is None or not row["rewards"]:
        return 0
    factor = _starting_total_level(state) * _int(row["factor_multiplier"])
    if mode == DOMINION_TOWER_ENDURANCE and _int(
        state.get("progress")
    ) >= DOMINION_TOWER_ENDURANCE_REDUCED_FLOOR:
        factor //= DOMINION_TOWER_ENDURANCE_REDUCED_DIVISOR
    for handicap_id in state.get("handicaps") or ():
        factor += _int(
            DOMINION_TOWER_HANDICAPS_BY_ID[handicap_id]["factor_delta"], minimum=-10_000
        )
    return max(0, factor)


# ---------------------------------------------------------------------------
# Handicaps
# ---------------------------------------------------------------------------


def _handicap_effects(handicaps) -> frozenset[str]:
    return frozenset(
        str(DOMINION_TOWER_HANDICAPS_BY_ID[handicap_id]["effect"])
        for handicap_id in handicaps
    )


def _reduced_classes(handicaps, effect: str) -> frozenset[str]:
    return frozenset(
        str(DOMINION_TOWER_HANDICAPS_BY_ID[handicap_id].get("combat_class", ""))
        for handicap_id in handicaps
        if DOMINION_TOWER_HANDICAPS_BY_ID[handicap_id]["effect"] == effect
    )


def _offer_new_handicap(state: dict[str, Any], rng) -> dict[str, Any]:
    """A handicap the player does not already have, drawn at random."""
    remaining = [
        handicap_id
        for handicap_id in DOMINION_TOWER_HANDICAP_IDS
        if handicap_id not in (state.get("handicaps") or ())
    ]
    picked = _pick(rng, remaining)
    if picked is None:
        return {}
    return {"handicap_id": picked, "respins_used": 0, "nudges_used": 0}


def _nudged_handicap(handicap_id: str) -> str:
    """A nudge lands on the handicap before this one, wrapping to the bottom."""
    index = DOMINION_TOWER_HANDICAP_IDS.index(handicap_id)
    return DOMINION_TOWER_HANDICAP_IDS[(index - 1) % DOMINION_TOWER_HANDICAP_COUNT]


def _apply_handicap_start_effect(
    data: dict[str, Any],
    state: dict[str, Any],
    handicap_id: str,
    rng,
) -> tuple[dict[str, Any], str]:
    """What one handicap does the moment the match it applies to begins."""
    row = DOMINION_TOWER_HANDICAPS_BY_ID[handicap_id]
    match = state.setdefault("match", _sanitize_match({}))
    effect = str(row["effect"])
    if effect == "monster_stun":
        match["stun_ticks"] = DOMINION_TOWER_MONSTER_STUN_TICKS
        return data, "foes stunned"
    if effect == "halved_lifepoints" and not match.get("halved_applied"):
        maximum = combat_max_lifepoints_pure(data)
        current = _int(data.get("combat_lifepoints"), maximum, minimum=0)
        data["combat_lifepoints"] = min(current, max(1, maximum // 2))
        match["halved_applied"] = True
        return data, "life points halved"
    if effect == "poison":
        poisoned, applied, _reason = apply_combat_poison_effect_pure(
            data, _int(row["initial_damage"], 98)
        )
        data.clear()
        data.update(poisoned)
        return data, "poisoned" if applied else ""
    if effect == "disease":
        skill = _pick(rng, DOMINION_TOWER_DISEASE_SKILLS)
        if skill:
            apply_combat_stat_delta_pure(data, skill, -DOMINION_TOWER_DISEASE_DRAIN)
            return data, f"{skill} diseased"
    return data, ""


def _apply_match_start_handicaps(
    data: dict[str, Any],
    state: dict[str, Any],
    rng,
) -> tuple[dict[str, Any], list[str]]:
    """Everything the wheel does at the moment a match begins."""
    notes: list[str] = []
    for handicap_id in state.get("handicaps") or ():
        data, note = _apply_handicap_start_effect(data, state, handicap_id, rng)
        if note:
            notes.append(note)
    return data, notes


def _apply_burst_handicaps(
    data: dict[str, Any],
    state: Mapping[str, Any],
    rng,
) -> tuple[dict[str, Any], float]:
    """Handicaps that constrain one six-tick slice, and the damage they cost."""
    handicaps = state.get("handicaps") or ()
    effects = _handicap_effects(handicaps)
    multiplier = 1.0
    if "no_prayer" in effects:
        data["combat_selected_prayers"] = []
        data["combat_prayer_uptime"] = "off"
    if "no_special_attacks" in effects:
        data["combat_special_attack_energy"] = 0
    if "no_food" in effects or "no_potions" in effects:
        loadout = data.get("combat_supply_loadout")
        if isinstance(loadout, Mapping):
            data["combat_supply_loadout"] = {
                key: value
                for key, value in loadout.items()
                if not (
                    ("no_food" in effects and str(key) == "food")
                    or ("no_potions" in effects and str(key) != "food")
                )
            }
        if "no_food" in effects:
            data["combat_auto_eat_food"] = ""
    for slot in ("body", "shield"):
        if f"strip_{slot}" in effects or (
            "strip_slot" in effects
            and slot
            in {
                str(DOMINION_TOWER_HANDICAPS_BY_ID[handicap_id].get("slot", ""))
                for handicap_id in handicaps
                if DOMINION_TOWER_HANDICAPS_BY_ID[handicap_id]["effect"] == "strip_slot"
            }
        ):
            equipment = data.get("equipment")
            if isinstance(equipment, Mapping) and equipment.get(slot):
                data["equipment"] = {
                    key: value for key, value in equipment.items() if str(key) != slot
                }
    reduced_attack = _reduced_classes(handicaps, "reduce_player_attack")
    if reduced_attack:
        multiplier *= DOMINION_TOWER_HANDICAP_REDUCTION_FRACTION
    for handicap_id in handicaps:
        if DOMINION_TOWER_HANDICAPS_BY_ID[handicap_id]["effect"] != "lose_attack_time":
            continue
        from ..data.dominion_tower_data import DOMINION_TOWER_LOST_ATTACK_TIME_CHANCE

        if _roll(rng) < DOMINION_TOWER_LOST_ATTACK_TIME_CHANCE:
            multiplier *= 0.5
    weapon = state.get("weapon_powerup") or {}
    if weapon and "no_powerups" not in effects:
        multiplier *= DOMINION_TOWER_WEAPON_POWERUP_DAMAGE_MULTIPLIER
    return data, max(0.0, multiplier)


def _enemy_for_member(
    state: Mapping[str, Any],
    member: Mapping[str, Any],
    attack_style: str,
) -> dict[str, Any]:
    npc = copy.deepcopy(DOMINION_TOWER_NPCS[member["npc_key"]])
    handicaps = state.get("handicaps") or ()
    reduced_defence = _reduced_classes(handicaps, "reduce_player_defence")
    if reduced_defence:
        # A reduced player defence bonus lands on the incoming side, which this
        # family owns: the arena's foes hit harder for the whole run.
        npc["max_hit"] = int(
            npc["max_hit"] / max(0.01, DOMINION_TOWER_HANDICAP_REDUCTION_FRACTION)
        )
    if _int((state.get("match") or {}).get("stun_ticks")) > 0:
        npc["max_hit"] = 0
    enemy = dominion_tower_enemy_pure(npc, attack_style)
    enemy["stats"] = dict(enemy["stats"], hitpoints=_int(member["max_lifepoints"], 1, minimum=1))
    return enemy


# ---------------------------------------------------------------------------
# Session lifecycle
# ---------------------------------------------------------------------------


def _spawn_roster(
    state: dict[str, Any],
    npc_keys,
    *,
    lifepoint_fraction: tuple[int, int] | None = None,
) -> None:
    roster: list[dict[str, Any]] = []
    next_id = _int(state.get("next_instance_id"), 1, minimum=1)
    for npc_key in npc_keys:
        npc = DOMINION_TOWER_NPCS[npc_key]
        maximum = _int(npc["lifepoints"], 1, minimum=1)
        if lifepoint_fraction:
            numerator, denominator = lifepoint_fraction
            maximum = max(1, maximum * numerator // denominator)
        roster.append(
            {
                "instance_id": next_id,
                "npc_key": npc_key,
                "max_lifepoints": maximum,
                "lifepoints": maximum,
                "encounter": {
                    "target_id": DOMINION_TOWER_TARGET_ID,
                    "enemy_lifepoints": maximum,
                },
            }
        )
        next_id += 1
    state["roster"] = roster
    state["next_instance_id"] = next_id
    state["engaged_instance_id"] = roster[0]["instance_id"] if roster else 0
    state["match"] = _sanitize_match({})


def _engaged_member(state: Mapping[str, Any]) -> dict[str, Any] | None:
    """The engaged target, with healers taken first per the roster contract."""
    roster = state.get("roster") or ()
    engaged = _int(state.get("engaged_instance_id"))
    for member in roster:
        if member["instance_id"] == engaged:
            return member
    healers = [
        member
        for member in roster
        if DOMINION_TOWER_NPCS[member["npc_key"]]["role"] == "healer"
    ]
    if healers:
        return healers[0]
    return roster[0] if roster else None


def _clear_session(data: dict[str, Any], state: dict[str, Any], message: str) -> None:
    state["mode"] = ""
    state["encounter_id"] = ""
    state["special_id"] = ""
    state["roster"] = []
    state["engaged_instance_id"] = 0
    state["handicaps"] = []
    state["offer"] = {}
    state["match"] = {}
    state["progress"] = 0
    state["weapon_powerup"] = {}
    state["last_result"] = message[:500]
    data["dominion_tower"] = state
    data["activity_session"] = {"active_id": ""}
    data["combat_encounter"] = {}
    data["current_combat_target"] = str(state.get("previous_combat_target", ""))


def _entry_reasons(
    player_data: Mapping[str, Any],
    state: Mapping[str, Any],
    *,
    waive_combat: bool = False,
) -> tuple[str, ...]:
    reasons: list[str] = []
    level = player_combat_level_pure(player_data)
    if not waive_combat and level < DOMINION_TOWER_COMBAT_LEVEL_REQUIREMENT:
        reasons.append(
            f"Combat level {DOMINION_TOWER_COMBAT_LEVEL_REQUIREMENT} "
            f"(you are {level})"
        )
    completed = len(dominion_tower_completed_quests_pure(player_data))
    if completed < DOMINION_TOWER_QUEST_REQUIREMENT:
        reasons.append(
            f"{DOMINION_TOWER_QUEST_REQUIREMENT} of the tower's 38 quests "
            f"({completed} complete)"
        )
    if not state.get("talked_with_face"):
        reasons.append("Talk to the Strange face")
    return tuple(reasons)


# ---------------------------------------------------------------------------
# View
# ---------------------------------------------------------------------------


def dominion_tower_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_dominion_tower_state_pure(player_data.get("dominion_tower"))
    # The credit ledger is derived, so the view shows the same figure the next
    # command will act on rather than a stale one.
    _accrue_reward_credits(state)
    active = bool(state["mode"] and state["roster"])
    floor = _int(state["progress"]) + 1
    available = dominion_tower_available_encounters_pure(player_data, floor)
    entry_reasons = _entry_reasons(player_data, state)
    unlocked = _unlocked_rewards(state)
    engaged = _engaged_member(state)
    engaged_npc = DOMINION_TOWER_NPCS[engaged["npc_key"]] if engaged else None
    inventory = player_data.get("inventory") or {}
    special_rows = tuple(
        {
            "id": row["id"],
            "display_name": row["display_name"],
            "unlocked": (
                not row["requires_encounter"]
                or row["requires_encounter"] in state["faced"]
            ),
            "completed": row["id"] in state["specials_done"],
            "handicaps": tuple(
                DOMINION_TOWER_HANDICAPS_BY_ID[handicap_id]["display_name"]
                for handicap_id in row["handicaps"]
            ),
        }
        for row in DOMINION_TOWER_SPECIAL_MATCHES
    )
    claimable = tuple(
        row["item_name"]
        for row in DOMINION_TOWER_GLOVE_SETS
        if _glove_set_complete(state, row["id"])
    )
    return {
        **state,
        "active": active,
        "floor": floor,
        "requirements_met": not entry_reasons,
        "entry_reasons": entry_reasons,
        "completed_quests": len(dominion_tower_completed_quests_pure(player_data)),
        "quest_requirement": DOMINION_TOWER_QUEST_REQUIREMENT,
        "available_encounters": available,
        "available_encounter_rows": tuple(
            {
                "id": encounter_id,
                "display_name": DOMINION_TOWER_ENCOUNTERS_BY_ID[encounter_id][
                    "display_name"
                ],
                "class": DOMINION_TOWER_ENCOUNTERS_BY_ID[encounter_id]["class"],
                "defeated": _int((state["defeated"] or {}).get(encounter_id)),
            }
            for encounter_id in available
        ),
        "freestyle_encounters": tuple(
            encounter_id
            for encounter_id in (state["defeated"] or {})
            if _int((state["defeated"] or {}).get(encounter_id)) > 0
        ),
        "special_rows": special_rows,
        "mode_rows": tuple(
            {
                "id": row["id"],
                "display_name": row["display_name"],
                "handicaps": bool(row["handicaps"]),
                "rewards": bool(row["rewards"]),
            }
            for row in DOMINION_TOWER_MODES_BY_ID.values()
        ),
        "engaged_name": engaged_npc["display_name"] if engaged_npc else "",
        "engaged_lifepoints": _int(engaged["lifepoints"]) if engaged else 0,
        "engaged_max_lifepoints": _int(engaged["max_lifepoints"]) if engaged else 0,
        "roster_names": tuple(
            DOMINION_TOWER_NPCS[member["npc_key"]]["display_name"]
            for member in state["roster"]
        ),
        "encounter_name": (
            DOMINION_TOWER_SPECIAL_MATCHES_BY_ID[state["special_id"]]["display_name"]
            if state["special_id"]
            else DOMINION_TOWER_ENCOUNTERS_BY_ID[state["encounter_id"]]["display_name"]
            if state["encounter_id"]
            else ""
        ),
        "handicap_rows": tuple(
            {
                "id": handicap_id,
                "display_name": DOMINION_TOWER_HANDICAPS_BY_ID[handicap_id][
                    "display_name"
                ],
                "factor_delta": DOMINION_TOWER_HANDICAPS_BY_ID[handicap_id][
                    "factor_delta"
                ],
                "description": DOMINION_TOWER_HANDICAPS_BY_ID[handicap_id][
                    "description"
                ],
            }
            for handicap_id in state["handicaps"]
        ),
        "offer_row": (
            {
                "id": state["offer"]["handicap_id"],
                "display_name": DOMINION_TOWER_HANDICAPS_BY_ID[
                    state["offer"]["handicap_id"]
                ]["display_name"],
                "factor_delta": DOMINION_TOWER_HANDICAPS_BY_ID[
                    state["offer"]["handicap_id"]
                ]["factor_delta"],
                "can_respin": state["offer"]["respins_used"]
                < DOMINION_TOWER_HANDICAP_RESPIN_LIMIT,
                "can_nudge": state["offer"]["nudges_used"]
                < DOMINION_TOWER_HANDICAP_NUDGE_LIMIT,
            }
            if state["offer"]
            else {}
        ),
        "round_factor": dominion_tower_round_factor_pure(state),
        "achievements": dominion_tower_achievements_pure(state),
        "unlocked_rewards": tuple(sorted(unlocked)),
        "marker_stage": _marker_stage(state),
        "marker_boost": DOMINION_TOWER_MARKER_STAGE_BOOSTS.get(_marker_stage(state), 0),
        "claimable_gloves": claimable,
        "dreadnip_ready": "dreadnip" in unlocked and state["reward_credits"] > 0,
        "ascendancy_ready": "ascendancy_mines" in unlocked,
        "mines_ready": "mines" in unlocked,
        "exchangeable_items": tuple(
            item_name
            for item_name in DOMINION_TOWER_EXCHANGEABLE_ITEMS
            if _int(inventory.get(item_name)) > 0
        ),
        "xp_book_skills": DOMINION_TOWER_XP_BOOK_SKILLS,
        "xp_books_held": _int(inventory.get(DOMINION_TOWER_XP_BOOK)),
        "primary_label": "Continue in the Tower" if active else "Enter the Tower",
        "primary_enabled": bool(active or not entry_reasons),
        "leave_visible": bool(state["mode"]),
        "claim_enabled": _int(state["dominion_factor"]) > 0,
        "source": DOMINION_TOWER_SOURCE,
    }


def dominion_tower_can_review_pure(player_data: Mapping[str, Any]) -> bool:
    view = dominion_tower_view_pure(player_data)
    return bool(view["active"] and not view["offer_row"])


# ---------------------------------------------------------------------------
# Rewards
# ---------------------------------------------------------------------------


def _grant(data: dict[str, Any], item_name: str, quantity: int) -> None:
    inventory = dict(data.get("inventory", {}) or {})
    inventory[item_name] = _int(inventory.get(item_name)) + max(0, int(quantity))
    data["inventory"] = inventory


def _consume(data: dict[str, Any], item_name: str, quantity: int) -> bool:
    inventory = dict(data.get("inventory", {}) or {})
    held = _int(inventory.get(item_name))
    if held < quantity:
        return False
    inventory[item_name] = held - quantity
    data["inventory"] = inventory
    return True


def dominion_tower_xp_book_amount_pure(factor: int, skill_id: str) -> float:
    """The book's experience: factor-scaled, with the stated per-skill ratios."""
    ratio = _float(DOMINION_TOWER_XP_BOOK_SKILL_RATIOS.get(skill_id), 0.0)
    return round(max(0, _int(factor)) * DOMINION_TOWER_XP_BOOK_FACTOR_SCALE * ratio, 1)


def _accrue_reward_credits(state: dict[str, Any]) -> int:
    """The unlock itself grants one credit; another arrives every five kills.

    "Kill 500 bosses ... this is the total number of dreadnips and gloves
    available to claim", then "an extra will become available every 5 boss
    kills". So the first credit lands with the unlock and the counter starts
    from the kill total the unlock was reached on.
    """
    unlocked = _unlocked_rewards(state)
    if not unlocked & {"dreadnip", "goliath_gloves", "spellcaster_gloves", "swift_gloves"}:
        return 0
    kills = _int(state.get("boss_kills"))
    before = _int(state.get("reward_credits"))
    marker = _int(state.get("credit_kill_marker"))
    if marker <= 0:
        state["credit_kill_marker"] = kills
        state["reward_credits"] = min(DOMINION_TOWER_REWARD_CREDIT_CAP, max(before, 1))
        return state["reward_credits"] - before
    earned = max(0, (kills - marker) // DOMINION_TOWER_REWARD_CREDIT_KILLS)
    if earned <= 0:
        return 0
    state["reward_credits"] = min(
        DOMINION_TOWER_REWARD_CREDIT_CAP, before + earned
    )
    state["credit_kill_marker"] = marker + earned * DOMINION_TOWER_REWARD_CREDIT_KILLS
    return state["reward_credits"] - before


def _open_reward_box(
    data: dict[str, Any],
    state: dict[str, Any],
    rng,
) -> dict[str, Any]:
    """Claim the box: one Xp book plus the stated draws, then reset progress."""
    factor = _int(state.get("dominion_factor"))
    granted: dict[str, int] = {}
    _grant(data, DOMINION_TOWER_XP_BOOK, 1)
    granted[DOMINION_TOWER_XP_BOOK] = 1
    for _ in range(DOMINION_TOWER_REWARD_BOX_ROLLS):
        row = _pick(rng, DOMINION_TOWER_REWARD_BOX_ITEMS)
        if row is None:
            continue
        quantity = _int(row["quantity"], 1, minimum=1)
        if row["capped"]:
            quantity = min(quantity, DOMINION_TOWER_REWARD_BOX_ITEM_CAP)
        _grant(data, str(row["item_name"]), quantity)
        granted[str(row["item_name"])] = granted.get(str(row["item_name"]), 0) + quantity
    page_found = False
    if _int(state.get("journal_pages")) < DOMINION_TOWER_JOURNAL_PAGE_COUNT and _roll(
        rng
    ) < DOMINION_TOWER_JOURNAL_PAGE_CHANCE:
        state["journal_pages"] = _int(state["journal_pages"]) + 1
        _grant(data, DOMINION_TOWER_JOURNAL_PAGE, 1)
        granted[DOMINION_TOWER_JOURNAL_PAGE] = 1
        page_found = True
    unlocked = _unlocked_rewards(state)
    for unlock_id, item_name in _REWARD_ITEMS_BY_UNLOCK.items():
        if unlock_id in unlocked and item_name not in (state.get("claimed") or ()):
            _grant(data, item_name, 1)
            granted[item_name] = granted.get(item_name, 0) + 1
            state["claimed"] = [*state["claimed"], item_name]
            if item_name == DOMINION_TOWER_HELP_HORN:
                state["help_horn_charges"] = DOMINION_TOWER_HELP_HORN_USES
    for powerup_item, powerup in DOMINION_TOWER_POWERUPS_BY_ITEM.items():
        if powerup["unlock"] in unlocked and powerup_item not in granted:
            _grant(data, powerup_item, 1)
            granted[powerup_item] = 1
    state["dominion_factor"] = 0
    state["progress"] = 0
    state["xp_book_factor"] = factor
    data["dominion_tower"] = state
    return {"granted": granted, "factor": factor, "journal_page": page_found}


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def _start_match(
    data: dict[str, Any],
    state: dict[str, Any],
    rng,
    *,
    npc_keys,
    lifepoint_fraction=None,
    survive_ticks: int = 0,
) -> None:
    previous_target = str(data.get("current_combat_target", ""))[:120]
    if previous_target != DOMINION_TOWER_TARGET_ID:
        state["previous_combat_target"] = previous_target
    _spawn_roster(state, npc_keys, lifepoint_fraction=lifepoint_fraction)
    state["match"]["survive_ticks"] = max(0, int(survive_ticks))
    data, _notes = _apply_match_start_handicaps(data, state, rng)
    engaged = _engaged_member(state)
    data["current_combat_target"] = DOMINION_TOWER_TARGET_ID
    data["combat_encounter"] = copy.deepcopy(engaged["encounter"]) if engaged else {}
    data["dominion_tower"] = state
    data["activity_session"] = {"active_id": DOMINION_TOWER_ACTIVITY_ID}
    data["current_utility"] = DOMINION_TOWER_ACTIVITY_ID


def apply_dominion_tower_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
    rng=None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    payload = payload if isinstance(payload, Mapping) else {}
    rng = rng or (lambda: 0.0)
    state = sanitize_dominion_tower_state_pure(data.get("dominion_tower"))
    # Spectating and a glove set's last boss can both unlock a credit reward
    # outside a win, so the ledger is refreshed before any command reads it.
    _accrue_reward_credits(state)
    data["dominion_tower"] = state
    action_id = str(action_id)

    if action_id == "talk_to_face":
        if state["talked_with_face"]:
            return data, False, {"reason": "You have already spoken to the Strange face."}
        level = player_combat_level_pure(data)
        if level < DOMINION_TOWER_COMBAT_LEVEL_REQUIREMENT:
            return data, False, {
                "reason": (
                    "You need at least level "
                    f"{DOMINION_TOWER_COMBAT_LEVEL_REQUIREMENT} combat to use this tower."
                )
            }
        state["talked_with_face"] = True
        state["last_result"] = "The Strange face agrees to generate opponents for you."
        return data, True, {"message": state["last_result"]}

    if action_id == "spectate":
        if not state["talked_with_face"]:
            return data, False, {"reason": "Talk to the Strange face first."}
        if state["spectated"]:
            return data, False, {"reason": "You have already spectated a match."}
        state["spectated"] = True
        state["last_result"] = "Watched another warrior's match from the stars."
        return data, True, {"message": state["last_result"]}

    if action_id == "start_mode":
        mode = str(payload.get("mode", ""))
        row = DOMINION_TOWER_MODES_BY_ID.get(mode)
        if row is None:
            return data, False, {"reason": "Choose Climber, Endurance, Special or Freestyle."}
        if state["roster"]:
            return data, False, {"reason": "Finish or leave the current match first."}
        session = data.get("activity_session")
        if isinstance(session, Mapping) and session.get("active_id") not in (
            "",
            DOMINION_TOWER_ACTIVITY_ID,
        ):
            return data, False, {"reason": "Another persistent activity is active."}
        if state["mode"] and state["mode"] != mode:
            return data, False, {
                "reason": (
                    f"{DOMINION_TOWER_MODES_BY_ID[state['mode']]['display_name']} mode "
                    "is still running; claim your rewards or leave first."
                )
            }
        special_id = str(payload.get("special_id", ""))
        waive = bool(
            mode == DOMINION_TOWER_SPECIAL
            and DOMINION_TOWER_SPECIAL_MATCHES_BY_ID.get(special_id, {}).get(
                "waives_combat_requirement"
            )
        )
        reasons = _entry_reasons(data, state, waive_combat=waive)
        if reasons:
            return data, False, {"reason": "; ".join(reasons) + "."}
        if mode == DOMINION_TOWER_SPECIAL:
            match = DOMINION_TOWER_SPECIAL_MATCHES_BY_ID.get(special_id)
            if match is None:
                return data, False, {"reason": "Choose a special match."}
            required = str(match["requires_encounter"])
            if required and required not in state["faced"]:
                return data, False, {
                    "reason": (
                        "Face "
                        f"{DOMINION_TOWER_ENCOUNTERS_BY_ID[required]['display_name']}"
                        " in Climber mode first."
                    )
                }
            state["mode"] = mode
            state["special_id"] = special_id
            state["encounter_id"] = ""
            state["handicaps"] = list(match["handicaps"])
            state["suffered_handicaps"] = sorted(
                set(state["suffered_handicaps"]) | set(match["handicaps"])
            )
            _start_match(
                data,
                state,
                rng,
                npc_keys=match["npcs"],
                lifepoint_fraction=match.get("lifepoint_fraction"),
                survive_ticks=_int(match.get("survive_ticks")),
            )
            state["last_result"] = f"{match['display_name']} begins."
            return data, True, {"message": state["last_result"]}

        if mode == DOMINION_TOWER_FREESTYLE:
            encounter_id = str(payload.get("encounter_id", ""))
            if _int((state["defeated"] or {}).get(encounter_id)) <= 0:
                return data, False, {
                    "reason": "Defeat a boss elsewhere in the tower before choosing it."
                }
            chosen = _str_list(
                payload.get("handicaps"), allowed=DOMINION_TOWER_HANDICAPS_BY_ID
            )
            state["mode"] = mode
            state["encounter_id"] = encounter_id
            state["special_id"] = ""
            state["handicaps"] = chosen
            _start_match(
                data,
                state,
                rng,
                npc_keys=DOMINION_TOWER_ENCOUNTERS_BY_ID[encounter_id]["npcs"],
            )
            state["last_result"] = (
                f"Freestyle: {DOMINION_TOWER_ENCOUNTERS_BY_ID[encounter_id]['display_name']}"
                " · no rewards"
            )
            return data, True, {"message": state["last_result"]}

        floor = _int(state["progress"]) + 1
        available = dominion_tower_available_encounters_pure(data, floor)
        if not available:
            return data, False, {
                "reason": "No boss you have unlocked can appear on this floor."
            }
        max_floor = _int(row["max_floor"])
        if max_floor and floor > max_floor:
            return data, False, {
                "reason": f"Endurance mode ends after floor {max_floor}."
            }
        state["mode"] = mode
        state["special_id"] = ""
        state["encounter_id"] = str(_pick(rng, available))
        if row["handicaps"] and mode == DOMINION_TOWER_CLIMBER:
            state["offer"] = _offer_new_handicap(state, rng)
        _start_match(
            data,
            state,
            rng,
            npc_keys=DOMINION_TOWER_ENCOUNTERS_BY_ID[state["encounter_id"]]["npcs"],
        )
        if state["encounter_id"] not in state["faced"]:
            state["faced"] = [*state["faced"], state["encounter_id"]]
        state["last_result"] = (
            f"{row['display_name']} floor {floor}: "
            f"{DOMINION_TOWER_ENCOUNTERS_BY_ID[state['encounter_id']]['display_name']}"
        )
        return data, True, {"message": state["last_result"]}

    if action_id in ("accept_handicap", "respin_handicap", "nudge_handicap"):
        offer = state["offer"]
        if not offer:
            return data, False, {"reason": "No handicap is on the spinner."}
        if action_id == "respin_handicap":
            if offer["respins_used"] >= DOMINION_TOWER_HANDICAP_RESPIN_LIMIT:
                return data, False, {"reason": "You have already respun the spinner."}
            respun = _offer_new_handicap(state, rng)
            if not respun:
                return data, False, {"reason": "Every handicap is already active."}
            state["offer"] = {
                **respun,
                "respins_used": offer["respins_used"] + 1,
                "nudges_used": offer["nudges_used"],
            }
            return data, True, {
                "message": (
                    "Respun to "
                    f"{DOMINION_TOWER_HANDICAPS_BY_ID[state['offer']['handicap_id']]['display_name']}."
                )
            }
        if action_id == "nudge_handicap":
            if offer["nudges_used"] >= DOMINION_TOWER_HANDICAP_NUDGE_LIMIT:
                return data, False, {"reason": "The spinner will not nudge further."}
            state["offer"] = {
                "handicap_id": _nudged_handicap(offer["handicap_id"]),
                "respins_used": offer["respins_used"],
                "nudges_used": offer["nudges_used"] + 1,
            }
            return data, True, {
                "message": (
                    "Nudged to "
                    f"{DOMINION_TOWER_HANDICAPS_BY_ID[state['offer']['handicap_id']]['display_name']}."
                )
            }
        handicap_id = offer["handicap_id"]
        if handicap_id not in state["handicaps"]:
            state["handicaps"] = [*state["handicaps"], handicap_id]
        if handicap_id not in state["suffered_handicaps"]:
            state["suffered_handicaps"] = [*state["suffered_handicaps"], handicap_id]
        state["offer"] = {}
        data, note = _apply_handicap_start_effect(data, state, handicap_id, rng)
        row = DOMINION_TOWER_HANDICAPS_BY_ID[handicap_id]
        state["last_result"] = f"Handicap incurred: {row['display_name']}" + (
            f" · {note}." if note else "."
        )
        data["dominion_tower"] = state
        return data, True, {"message": state["last_result"], "handicap_id": handicap_id}

    if action_id == "leave":
        if not state["mode"]:
            return data, False, {"reason": "You are not in the tower."}
        banked = _int(state["dominion_factor"])
        _clear_session(
            data,
            state,
            f"Left the tower holding a Dominion Factor of {banked:,}.",
        )
        return data, True, {"message": state["last_result"]}

    if action_id == "claim_rewards":
        if not state["talked_with_face"]:
            return data, False, {"reason": "Talk to the Strange face first."}
        if _int(state["dominion_factor"]) <= 0:
            return data, False, {
                "reason": "You have no dominion factor to claim anything with."
            }
        if state["roster"]:
            return data, False, {"reason": "Finish the current match first."}
        result = _open_reward_box(data, state, rng)
        _clear_session(
            data,
            state,
            "Claimed the reward box for a Dominion Factor of "
            f"{result['factor']:,} · " + ", ".join(sorted(result["granted"])),
        )
        return data, True, {"message": state["last_result"], **result}

    if action_id == "exchange_rewards":
        inventory = data.get("inventory") or {}
        held = {
            item_name: _int(inventory.get(item_name))
            for item_name in DOMINION_TOWER_EXCHANGEABLE_ITEMS
            if _int(inventory.get(item_name)) > 0
        }
        if not held:
            return data, False, {"reason": "You hold no rewards to exchange."}
        total = sum(held.values())
        for item_name, quantity in held.items():
            _consume(data, item_name, quantity)
        _grant(data, DOMINION_TOWER_XP_BOOK, 1)
        state["xp_book_factor"] = total * DOMINION_TOWER_EXCHANGE_FACTOR_PER_ITEM
        state["last_result"] = f"Exchanged {total} rewards for an Xp book."
        return data, True, {
            "message": state["last_result"],
            "exchanged": total,
            "book_factor": state["xp_book_factor"],
        }

    if action_id == "read_xp_book":
        skill_id = str(payload.get("skill", ""))
        if skill_id not in DOMINION_TOWER_XP_BOOK_SKILLS:
            return data, False, {"reason": "Choose a combat skill for the book."}
        level = _int(data.get(f"{skill_id}_level"), 1, minimum=1)
        if level < DOMINION_TOWER_XP_BOOK_SKILL_LEVEL:
            return data, False, {
                "reason": (
                    "The chosen skill must be at least level "
                    f"{DOMINION_TOWER_XP_BOOK_SKILL_LEVEL}."
                )
            }
        if not _consume(data, DOMINION_TOWER_XP_BOOK, 1):
            return data, False, {"reason": "You hold no Xp book."}
        amount = dominion_tower_xp_book_amount_pure(
            _int(state.get("xp_book_factor")), skill_id
        )
        data[f"{skill_id}_exp"] = _float(data.get(f"{skill_id}_exp")) + amount
        state["last_result"] = f"Read the Xp book for {amount:,.0f} {skill_id} XP."
        return data, True, {
            "message": state["last_result"],
            "xp_rewards": {f"{skill_id}_exp": amount},
        }

    if action_id == "claim_reward":
        reward_id = str(payload.get("reward_id", ""))
        unlocked = _unlocked_rewards(state)
        if reward_id == "ascendancy_mines":
            required = DOMINION_TOWER_ASCENDANCY_KILL_REQUIREMENT * (
                _int(state["ascendancy_claims"]) + 1
            )
            if _int(state["boss_kills"]) < required:
                return data, False, {
                    "reason": f"Ascendancy mines need {required:,} boss kills."
                }
            state["ascendancy_claims"] = _int(state["ascendancy_claims"]) + 1
            _grant(
                data, DOMINION_TOWER_ASCENDANCY_MINE, DOMINION_TOWER_ASCENDANCY_MINES_PER_CLAIM
            )
            state["last_result"] = (
                f"Claimed {DOMINION_TOWER_ASCENDANCY_MINES_PER_CLAIM} Ascendancy mines."
            )
            return data, True, {"message": state["last_result"]}
        credit_rewards = {
            "goliath_gloves": "Goliath gloves",
            "spellcaster_gloves": "Spellcaster gloves",
            "swift_gloves": "Swift gloves",
            "dreadnip": DOMINION_TOWER_DREADNIP,
        }
        if reward_id not in credit_rewards:
            return data, False, {"reason": "That reward is not claimable here."}
        if reward_id not in unlocked:
            return data, False, {"reason": "That reward is still locked."}
        if _int(state["reward_credits"]) <= 0:
            return data, False, {
                "reason": (
                    "No reward credits banked; five more boss kills earn the next one."
                )
            }
        state["reward_credits"] = _int(state["reward_credits"]) - 1
        item_name = credit_rewards[reward_id]
        quantity = (
            DOMINION_TOWER_DREADNIP_PER_CREDIT if reward_id == "dreadnip" else 1
        )
        _grant(data, item_name, quantity)
        if reward_id not in state["claimed"]:
            state["claimed"] = [*state["claimed"], reward_id]
        state["last_result"] = f"Claimed {quantity} × {item_name}."
        return data, True, {"message": state["last_result"], "item_name": item_name}

    if action_id == "buy_mines":
        if "mines" not in _unlocked_rewards(state):
            return data, False, {
                "reason": (
                    f"Dominion mines need {DOMINION_TOWER_MINE_KILL_REQUIREMENT} boss "
                    "kills and every special match except Sunfreet."
                )
            }
        quantity = max(1, _int(payload.get("quantity"), 1, minimum=1))
        cost = quantity * DOMINION_TOWER_MINE_COST
        if not _consume(data, "Coins", cost):
            return data, False, {"reason": f"You need {cost:,} coins."}
        _grant(data, DOMINION_TOWER_MINE, quantity)
        state["last_result"] = f"Bought {quantity} Dominion mines for {cost:,} coins."
        return data, True, {"message": state["last_result"]}

    if action_id == "use_powerup":
        return _use_powerup(data, state, str(payload.get("item", "")), rng)

    if action_id == "drink_potion":
        return _drink_potion(data, state, str(payload.get("item", "")))

    if action_id == "eat_scorpion_meat":
        if not state["roster"]:
            return data, False, {
                "reason": "Scorpion meat can only be eaten in the Dominion Tower."
            }
        if not _consume(data, DOMINION_TOWER_SCORPION_MEAT, 1):
            return data, False, {"reason": "You hold no scorpion meat."}
        maximum = combat_max_lifepoints_pure(data)
        current = _int(data.get("combat_lifepoints"), maximum, minimum=0)
        healed = min(DOMINION_TOWER_SCORPION_MEAT_HEAL, maximum - current)
        data["combat_lifepoints"] = current + healed
        state["last_result"] = f"Ate scorpion meat for {healed} life points."
        return data, True, {"message": state["last_result"], "healed": healed}

    return data, False, {"reason": "Unknown Dominion Tower command."}


def _use_powerup(
    data: dict[str, Any],
    state: dict[str, Any],
    item_name: str,
    rng,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    powerup = DOMINION_TOWER_POWERUPS_BY_ITEM.get(item_name)
    if powerup is None:
        return data, False, {"reason": "That is not a Dominion Tower power-up."}
    if not state["roster"]:
        return data, False, {"reason": "Power-ups only work inside an arena."}
    if "no_powerups" in _handicap_effects(state["handicaps"]):
        return data, False, {"reason": "The No Power-ups handicap blocks that."}
    required = powerup.get("required_skill")
    if required:
        skill_id, level = required
        if _int(data.get(f"{skill_id}_level"), 1, minimum=1) < _int(level):
            return data, False, {
                "reason": f"That power-up needs level {level} {skill_id.title()}."
            }
    if powerup["effect"] == "spawn_food":
        if _int(state["help_horn_charges"]) <= 0:
            return data, False, {"reason": "The help horn is out of charges."}
        state["help_horn_charges"] = _int(state["help_horn_charges"]) - 1
        _grant(data, DOMINION_TOWER_SCORPION_MEAT, 1)
        outcome = "The horn calls a piece of scorpion meat into the arena."
    elif powerup["effect"] == "bomb":
        match = state["match"]
        if _int(match.get("bombs_used")) >= DOMINION_TOWER_BOMBS_PER_MATCH:
            return data, False, {
                "reason": f"Only {DOMINION_TOWER_BOMBS_PER_MATCH} bombs may be used per match."
            }
        if not _consume(data, item_name, 1):
            return data, False, {"reason": f"You hold no {item_name}."}
        numerator, denominator = powerup["fraction"]
        targets = _int(powerup["targets"])
        hit = state["roster"] if targets <= 0 else state["roster"][:targets]
        total = 0
        for member in hit:
            damage = max(1, member["lifepoints"] * numerator // denominator)
            member["lifepoints"] = max(1, member["lifepoints"] - damage)
            member["encounter"]["enemy_lifepoints"] = member["lifepoints"]
            total += damage
        match["bombs_used"] = _int(match.get("bombs_used")) + 1
        outcome = f"{item_name} deals {total:,} damage across {len(hit)} foes."
    else:
        if _int((state.get("weapon_powerup") or {}).get("charges")) > 0:
            return data, False, {"reason": "A tower weapon is already in hand."}
        if not _consume(data, item_name, 1):
            return data, False, {"reason": f"You hold no {item_name}."}
        state["weapon_powerup"] = {
            "item": item_name,
            "charges": _int(powerup["charges"], 1, minimum=1),
        }
        outcome = f"Wielding the {item_name} for this match."
    if item_name in DOMINION_TOWER_STAFF_POWERUPS and item_name not in state["powerups_used"]:
        state["powerups_used"] = [*state["powerups_used"], item_name]
    engaged = _engaged_member(state)
    if engaged is not None:
        data["combat_encounter"] = copy.deepcopy(engaged["encounter"])
    state["last_result"] = outcome
    data["dominion_tower"] = state
    return data, True, {"message": outcome}


def _drink_potion(
    data: dict[str, Any],
    state: dict[str, Any],
    item_name: str,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    potion = DOMINION_TOWER_POTIONS_BY_ITEM.get(item_name)
    if potion is None:
        return data, False, {"reason": "That is not a Dominion Tower potion."}
    if not state["roster"]:
        return data, False, {"reason": "Tower potions only work inside the tower."}
    if "no_potions" in _handicap_effects(state["handicaps"]):
        return data, False, {"reason": "The No Potions handicap blocks that."}
    if not _consume(data, item_name, 1):
        return data, False, {"reason": f"You hold no {item_name}."}
    effect = str(potion["effect"])
    outcome = f"Drank {item_name}."
    if effect == "super_prayer":
        data["combat_prayer_points"] = _int(data.get("prayer_level"), 1, minimum=1) * 10
        outcome = "Prayer points restored."
    elif effect == "super_restore":
        for skill_id in ("attack", "strength", "defense", "ranged", "magic"):
            base = _int(data.get(f"{skill_id}_level"), 1, minimum=1)
            current = _int(data.get(f"{skill_id}_current_level"), base, minimum=1)
            if current < base:
                apply_combat_stat_delta_pure(data, skill_id, base - current)
        data["combat_prayer_points"] = _int(data.get("prayer_level"), 1, minimum=1) * 10
        outcome = "Stats and prayer restored."
    elif effect == "super_antipoison":
        effects = dict(data.get("combat_status_effects", {}) or {})
        effects.pop("poison", None)
        data["combat_status_effects"] = effects
        outcome = "Poison cured."
    else:
        maximum = combat_max_lifepoints_pure(data)
        current = _int(data.get("combat_lifepoints"), maximum, minimum=0)
        healed = min(max(1, maximum // 6), maximum - current)
        data["combat_lifepoints"] = current + healed
        outcome = f"Saradomin brew healed {healed} life points."
    state["last_result"] = outcome
    data["dominion_tower"] = state
    return data, True, {"message": outcome}


# ---------------------------------------------------------------------------
# Review loop
# ---------------------------------------------------------------------------


def _record_win(
    data: dict[str, Any],
    state: dict[str, Any],
    rng,
) -> dict[str, Any]:
    """A cleared arena: factor, floor, kill count and the next boss."""
    mode = state["mode"]
    row = DOMINION_TOWER_MODES_BY_ID[mode]
    factor = dominion_tower_round_factor_pure(state)
    state["last_round_factor"] = factor
    if factor:
        state["dominion_factor"] = min(
            DOMINION_TOWER_MAX_FACTOR, _int(state["dominion_factor"]) + factor
        )
        state["total_score"] = _int(state["total_score"]) + factor
    state["progress"] = _int(state["progress"]) + 1
    if mode == DOMINION_TOWER_CLIMBER:
        state["max_floor_climber"] = max(
            _int(state["max_floor_climber"]), state["progress"]
        )
    elif mode == DOMINION_TOWER_ENDURANCE:
        state["max_floor_endurance"] = max(
            _int(state["max_floor_endurance"]), state["progress"]
        )
    # Every glove unlock counts "a total of 500 bosses in either Climber or
    # Endurance matches", and a special fight "only counts as 1 boss killed".
    # Freestyle, which the article says carries no rewards, counts nothing.
    if row["rewards"]:
        state["boss_kills"] = _int(state["boss_kills"]) + 1
    if state["special_id"]:
        if state["special_id"] not in state["specials_done"]:
            state["specials_done"] = [*state["specials_done"], state["special_id"]]
        for encounter_id in _special_encounter_credits(state["special_id"]):
            defeated = dict(state["defeated"])
            defeated[encounter_id] = _int(defeated.get(encounter_id)) + 1
            state["defeated"] = defeated
    elif state["encounter_id"]:
        defeated = dict(state["defeated"])
        defeated[state["encounter_id"]] = _int(defeated.get(state["encounter_id"])) + 1
        state["defeated"] = defeated
    credits_gained = _accrue_reward_credits(state)
    state["marker_stage"] = _marker_stage(state)
    return {"factor": factor, "credits_gained": credits_gained, "rewards": bool(row["rewards"])}


def _special_encounter_credits(special_id: str) -> tuple[str, ...]:
    """Which climber encounters a cleared special match counts as defeated."""
    match = DOMINION_TOWER_SPECIAL_MATCHES_BY_ID[special_id]
    keys = set(match["npcs"])
    return tuple(
        row["id"]
        for row in DOMINION_TOWER_ENCOUNTERS
        if set(row["npcs"]) <= keys
    )


def _advance_to_next_boss(
    data: dict[str, Any],
    state: dict[str, Any],
    rng,
) -> bool:
    """Set up the next floor, or report that the run has reached its ceiling."""
    row = DOMINION_TOWER_MODES_BY_ID[state["mode"]]
    if state["special_id"] or state["mode"] == DOMINION_TOWER_FREESTYLE:
        return False
    floor = _int(state["progress"]) + 1
    max_floor = _int(row["max_floor"])
    if max_floor and floor > max_floor:
        return False
    available = dominion_tower_available_encounters_pure(data, floor)
    if not available:
        return False
    state["encounter_id"] = str(_pick(rng, available))
    if state["encounter_id"] not in state["faced"]:
        state["faced"] = [*state["faced"], state["encounter_id"]]
    if row["handicaps"] and state["mode"] == DOMINION_TOWER_CLIMBER:
        state["offer"] = _offer_new_handicap(state, rng)
    _start_match(
        data,
        state,
        rng,
        npc_keys=DOMINION_TOWER_ENCOUNTERS_BY_ID[state["encounter_id"]]["npcs"],
    )
    return True


def _apply_life_saver(data: dict[str, Any], state: dict[str, Any]) -> bool:
    if "life_saver" not in _handicap_effects(state["handicaps"]):
        return False
    match = state["match"]
    if match.get("life_saver_used"):
        return False
    maximum = combat_max_lifepoints_pure(data)
    current = _int(data.get("combat_lifepoints"), maximum, minimum=0)
    if current * 100 > maximum * DOMINION_TOWER_LIFE_SAVER_THRESHOLD_PERCENT:
        return False
    data["combat_lifepoints"] = maximum
    data["combat_prayer_points"] = _int(data.get("prayer_level"), 1, minimum=1) * 10
    match["life_saver_used"] = True
    return True


def apply_dominion_tower_review_pure(
    player_data: Mapping[str, Any],
    rng,
    *,
    equipment_data: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_dominion_tower_state_pure(data.get("dominion_tower"))
    if not state["mode"] or not state["roster"]:
        return data, False, {"reason": "Enter the Dominion Tower before training it."}
    if state["offer"]:
        # "When entering doors to begin a fight on a floor, the player receives
        # one new handicap": the wheel is not optional, only respinnable.
        return data, False, {
            "reason": (
                "Take the handicap on the spinner before the doors open: "
                f"{DOMINION_TOWER_HANDICAPS_BY_ID[state['offer']['handicap_id']]['display_name']}."
            )
        }
    data["dominion_tower"] = state
    engaged = _engaged_member(state)
    if engaged is None:
        return data, False, {"reason": "The arena is empty."}

    npc = DOMINION_TOWER_NPCS[engaged["npc_key"]]
    attack_style = str(_pick(rng, npc["attack_styles"]) or npc["attack_styles"][0])
    enemy = _enemy_for_member(state, engaged, attack_style)
    data["current_combat_target"] = DOMINION_TOWER_TARGET_ID
    data["combat_encounter"] = copy.deepcopy(engaged["encounter"])
    burst_data, damage_multiplier = _apply_burst_handicaps(dict(data), state, rng)
    # The arena gates lock behind the player, so the ordinary auto-flee stance
    # cannot apply: "you cannot leave a match once it begins, until you win or
    # lose". It is restored the moment the slice resolves.
    auto_flee = burst_data.get("combat_auto_flee", True)
    burst_data["combat_auto_flee"] = False
    burst_data, ok, combat_result = apply_combat_burst_pure(
        burst_data,
        {DOMINION_TOWER_TARGET_ID: enemy},
        equipment_data or {},
        ticks=DOMINION_TOWER_REVIEW_TICKS,
        rng=rng,
        live_cadence=True,
        stop_after_first_kill=True,
        # "Although the Dominion Tower is a safe minigame and you will not lose
        # items", so every defeat here is a safe defeat.
        safe_death=True,
        allow_bank_run=False,
        player_damage_multiplier=damage_multiplier,
    )
    burst_data["combat_auto_flee"] = auto_flee
    if not ok:
        return dict(player_data), False, combat_result
    data = burst_data
    data["dominion_tower"] = state

    match = state["match"]
    if _int(match.get("stun_ticks")) > 0:
        match["stun_ticks"] = max(0, _int(match["stun_ticks"]) - DOMINION_TOWER_REVIEW_TICKS)
    weapon = state.get("weapon_powerup") or {}
    if weapon:
        charges = _int(weapon.get("charges")) - DOMINION_TOWER_REVIEW_TICKS
        state["weapon_powerup"] = (
            {"item": weapon["item"], "charges": charges} if charges > 0 else {}
        )

    engaged_died = bool(combat_result.get("killed"))
    if engaged_died:
        state["roster"] = [
            member
            for member in state["roster"]
            if member["instance_id"] != engaged["instance_id"]
        ]
        state["engaged_instance_id"] = (
            state["roster"][0]["instance_id"] if state["roster"] else 0
        )
        data["combat_encounter"] = {}
    else:
        engaged["lifepoints"] = max(
            1,
            _int(combat_result.get("enemy_lifepoints"), engaged["lifepoints"], minimum=1),
        )
        engaged["encounter"] = {
            "target_id": DOMINION_TOWER_TARGET_ID,
            "enemy_lifepoints": engaged["lifepoints"],
        }

    # Pest drones heal the queen for as long as any of them is still alive.
    healing = 0
    for member in state["roster"]:
        amount = _int(DOMINION_TOWER_NPCS[member["npc_key"]]["heals_boss"])
        if amount <= 0:
            continue
        injured = [
            other
            for other in state["roster"]
            if DOMINION_TOWER_NPCS[other["npc_key"]]["heals_boss"] <= 0
            and other["lifepoints"] < other["max_lifepoints"]
        ]
        if not injured:
            continue
        target = min(injured, key=lambda row: row["lifepoints"])
        healed = min(amount, target["max_lifepoints"] - target["lifepoints"])
        target["lifepoints"] += healed
        target["encounter"]["enemy_lifepoints"] = target["lifepoints"]
        healing += healed

    pressure_damage = 0
    pressure_styles: list[str] = []
    if _int(match.get("stun_ticks")) <= 0:
        for member in state["roster"]:
            if member["instance_id"] == engaged["instance_id"] and not engaged_died:
                continue
            member_npc = DOMINION_TOWER_NPCS[member["npc_key"]]
            if member_npc["role"] == "healer" or _int(member_npc["max_hit"]) <= 0:
                continue
            pressure = combat_enemy_pressure_attack_pure(
                data,
                _enemy_for_member(state, member, member_npc["attack_styles"][0]),
                equipment_data or {},
                rng,
            )
            pressure_damage += _int(pressure.get("damage"))
            pressure_styles.append(str(pressure.get("attack_style", "melee")))
    pressure_result: dict[str, Any] = {"damage": 0, "died": False}
    if pressure_damage > 0:
        data, pressure_result = apply_thieving_damage_pure(
            data,
            pressure_damage,
            source="dominion_tower_pressure",
            carried_target_id=DOMINION_TOWER_TARGET_ID,
            safe_death=True,
        )
    life_saved = _apply_life_saver(data, state)

    player_died = bool(combat_result.get("died") or pressure_result.get("died"))
    match["ticks_survived"] = _int(match.get("ticks_survived")) + DOMINION_TOWER_REVIEW_TICKS
    survive_target = _int(match.get("survive_ticks"))
    survived = bool(survive_target and match["ticks_survived"] >= survive_target)

    if player_died:
        forfeited = _int(state["last_round_factor"])
        state["dominion_factor"] = max(0, _int(state["dominion_factor"]) - forfeited)
        state["last_round_factor"] = 0
        floor = _int(state["progress"]) + 1
        _clear_session(
            data,
            state,
            f"Defeated on floor {floor}; the Dominion Factor falls to "
            f"{state['dominion_factor']:,}.",
        )
        return data, True, {
            **combat_result,
            "player_died": True,
            "terminal": True,
            "pressure_damage": int(pressure_result.get("damage", 0) or 0),
            "outcome": state["last_result"],
            "status": state["last_result"],
        }

    arena_cleared = survived or not state["roster"]
    if not arena_cleared:
        state["last_result"] = (
            f"{DOMINION_TOWER_NPCS[_engaged_member(state)['npc_key']]['display_name']}: "
            f"{_engaged_member(state)['lifepoints']:,} LP · "
            f"{len(state['roster'])} in the arena"
        )
        if pressure_damage:
            state["last_result"] += f" · roster pressure {pressure_damage} LP"
        if healing:
            state["last_result"] += f" · drones healed {healing} LP"
        if life_saved:
            state["last_result"] += " · Life Saver triggered"
        data["dominion_tower"] = state
        data["activity_session"] = {"active_id": DOMINION_TOWER_ACTIVITY_ID}
        engaged_now = _engaged_member(state)
        data["combat_encounter"] = copy.deepcopy(engaged_now["encounter"]) if engaged_now else {}
        return data, True, {
            **combat_result,
            "status": state["last_result"],
            "pressure_damage": pressure_damage,
            "pressure_styles": tuple(pressure_styles),
            "roster_healing": healing,
            "life_saved": life_saved,
        }

    win = _record_win(data, state, rng)
    cleared_name = (
        DOMINION_TOWER_SPECIAL_MATCHES_BY_ID[state["special_id"]]["display_name"]
        if state["special_id"]
        else DOMINION_TOWER_ENCOUNTERS_BY_ID[state["encounter_id"]]["display_name"]
    )
    message = f"Defeated {cleared_name}"
    if win["factor"]:
        message += (
            f" · +{win['factor']:,} Dominion Factor "
            f"({state['dominion_factor']:,} banked)"
        )
    if win["credits_gained"]:
        message += f" · +{win['credits_gained']} reward credit"
    continued = _advance_to_next_boss(data, state, rng)
    if continued:
        message += (
            f" · floor {_int(state['progress']) + 1}: "
            f"{DOMINION_TOWER_ENCOUNTERS_BY_ID[state['encounter_id']]['display_name']}"
        )
        state["last_result"] = message[:500]
        data["dominion_tower"] = state
        data["activity_session"] = {"active_id": DOMINION_TOWER_ACTIVITY_ID}
    else:
        banked = _int(state["dominion_factor"])
        keep = {
            key: state[key]
            for key in (
                "dominion_factor",
                "total_score",
                "boss_kills",
                "max_floor_climber",
                "max_floor_endurance",
                "journal_pages",
                "defeated",
                "faced",
                "specials_done",
                "suffered_handicaps",
                "reward_credits",
                "credit_kill_marker",
            )
        }
        _clear_session(data, state, message)
        state.update(keep)
        state["last_result"] = (
            message + f" · claim the reward box for {banked:,} Dominion Factor"
        )[:500]
        data["dominion_tower"] = state
    return data, True, {
        **combat_result,
        "won": True,
        "factor": win["factor"],
        "credits_gained": win["credits_gained"],
        "terminal": not continued,
        "pressure_damage": pressure_damage,
        "roster_healing": healing,
        "life_saved": life_saved,
        "outcome": message,
        "status": state["last_result"],
    }
