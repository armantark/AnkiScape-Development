"""What the combat surfaces show: the HUD's health, prayer and summoning bars,
last-fight summary and finisher text, and the settings the Equipment tab's
combat setup panel draws."""

from typing import Mapping

from ..data.combat_data import COMBAT_MAGIC_SPELL_DATA, DEFAULT_COMBAT_SPELL
from ..data.prayer_data import COMBAT_PRAYERS
from ..logic.inventory_pure import DEFAULT_LOOT_VALUE_THRESHOLD
from .logic_pure_combat_finishers import (
    combat_finisher_notice_pure,
    combat_finisher_tooltip_pure,
)
from .logic_pure_combat_model import combat_max_lifepoints_pure
from .logic_pure_state import _non_negative_int, _positive_int


def _combat_hud_pct(value, ceiling):
    return int((min(value, ceiling) / ceiling) * 100) if ceiling > 0 else 0


def _combat_hud_player_bars(player_data):
    """Lifepoints, prayer and summoning, each clamped to its maximum."""
    max_lp = combat_max_lifepoints_pure(player_data)
    current_lp = max(0, min(_non_negative_int(player_data.get("combat_lifepoints", max_lp), max_lp), max_lp))
    prayer_max = _positive_int(player_data.get("prayer_level", 1), 1)
    prayer_current = min(
        prayer_max * 10,
        _non_negative_int(
            player_data.get("combat_prayer_points", prayer_max * 10),
            prayer_max * 10,
        ),
    ) // 10
    summoning_max = _positive_int(player_data.get("summoning_level", 1), 1)
    summoning_state = player_data.get("summoning_state", {}) or {}
    summoning_current = min(
        summoning_max,
        _non_negative_int(
            summoning_state.get("summoning_points_current", summoning_max)
            if isinstance(summoning_state, Mapping)
            else summoning_max,
            summoning_max,
        ),
    )
    return {
        "player_lifepoints": current_lp,
        "player_max_lifepoints": max_lp,
        "player_pct": _combat_hud_pct(current_lp, max_lp),
        "prayer_points": prayer_current,
        "prayer_max_points": prayer_max,
        "summoning_points": summoning_current,
        "summoning_max_points": summoning_max,
    }


def _combat_hud_enemy_bar(player_data, target_id, enemy_data):
    """The target's health, carried over only from an unfinished encounter with
    that same target."""
    enemy = enemy_data.get(target_id) if isinstance(target_id, str) else None
    if isinstance(enemy, Mapping):
        enemy_name = str(enemy.get("display_name", target_id))
        enemy_max_lp = _positive_int(enemy.get("stats", {}).get("hitpoints", 1), 1)
    else:
        enemy_name = "Enemy"
        enemy_max_lp = 0
    encounter = player_data.get("combat_encounter", {}) or {}
    carried = isinstance(encounter, Mapping) and encounter.get("target_id") == target_id and enemy_max_lp > 0
    if carried:
        enemy_lp = max(0, min(_positive_int(encounter.get("enemy_lifepoints", enemy_max_lp), enemy_max_lp), enemy_max_lp))
    else:
        enemy_lp = enemy_max_lp
    return {
        "enemy_name": enemy_name,
        "enemy_lifepoints": enemy_lp,
        "enemy_max_lifepoints": enemy_max_lp,
        "enemy_pct": _combat_hud_pct(enemy_lp, enemy_max_lp),
        "enemy_carried": bool(carried),
    }


def _combat_hud_last_fight(player_data, target_id):
    """The target's kill count and how the last burst ended."""
    kills_total = _non_negative_int((player_data.get("combat_kill_counts", {}) or {}).get(target_id, 0), 0)
    last = player_data.get("combat_last_result", {}) or {}
    last = last if isinstance(last, Mapping) else {}
    last_kills = _non_negative_int(last.get("kills", 0), 0)
    if last.get("died"):
        last_outcome = "died"
    elif last.get("fled"):
        last_outcome = "fled"
    else:
        last_outcome = ""
    return {
        "kills_total": kills_total,
        "last_kills": last_kills,
        "last_outcome": last_outcome,
    }


def _combat_hud_finisher_text(finisher):
    """The strip's finisher prompt, and the combat menu's tooltip for the
    finisher option, which reads the same HUD state."""
    return {
        "finisher_notice": combat_finisher_notice_pure(finisher),
        "finisher_tooltip": combat_finisher_tooltip_pure(finisher),
    }


def combat_setup_panel_view_pure(player_data):
    """Every saved setting the combat setup panel shows, and which spells and
    prayers it offers as unlocked."""
    target_id = str(player_data.get("current_combat_target", ""))
    target_overrides = (player_data.get("combat_target_overrides", {}) or {}).get(target_id, {}) or {}
    presets = player_data.get("combat_presets", {}) or {}
    active_preset = str(player_data.get("combat_active_preset", "Default"))
    return {
        "finisher_chosen": player_data.get("combat_action") == "finisher",
        "autocast_spell": player_data.get("current_combat_spell", DEFAULT_COMBAT_SPELL),
        "spells": _combat_setup_spell_rows(player_data),
        "borrowed_power_spell": player_data.get("combat_borrowed_power_spell"),
        "prayers_enabled": bool(player_data.get("combat_prayers_enabled", True)),
        "dream_thrift": bool(player_data.get("combat_dream_thrift", False)),
        "auto_prayer_training": bool(player_data.get("combat_auto_prayer_training", False)),
        "auto_eat_threshold": max(1, min(_int_or(player_data.get("combat_auto_eat_threshold_percent", 40) or 40, 40), 99)),
        "preset_names": [str(name) for name in presets] if isinstance(presets, dict) else ["Default"],
        "active_preset": active_preset,
        "curses_unlocked": _quest_completed(player_data, "the_temple_at_senntisten"),
        "prayer_book": player_data.get("combat_prayer_book", "standard"),
        "prayer_uptime": player_data.get("combat_prayer_uptime", "off"),
        "vengeance": bool(player_data.get("combat_vengeance", False)),
        "spellbook_swap": str(player_data.get("combat_spellbook_swap", "") or ""),
        "preset_pinned": (player_data.get("combat_target_presets", {}) or {}).get(target_id) == active_preset,
        "prayers_overridden": "combat_selected_prayers" in target_overrides,
        "uptime_overridden": "combat_prayer_uptime" in target_overrides,
        "selected_prayers": set(player_data.get("combat_selected_prayers", ()) or ()),
        "prayers": _combat_setup_prayer_rows(player_data),
        # "Hide lower-tier prayers" keeps the 15 levels below the player's own.
        "lower_tier_below": max(1, int(player_data.get("prayer_level", 1) or 1) - 15),
        "loot_threshold": max(0, _int_or(player_data.get("loot_value_threshold", DEFAULT_LOOT_VALUE_THRESHOLD), DEFAULT_LOOT_VALUE_THRESHOLD)),
    }


def toggled_combat_prayer_selection_pure(player_data, prayer_id, checked):
    """The selection after one prayer box changes; a newly ticked prayer goes
    first, so it wins any conflict when the save is sanitized."""
    selected = [str(pid) for pid in (player_data.get("combat_selected_prayers", ()) or ()) if str(pid) != prayer_id]
    if checked:
        selected.insert(0, prayer_id)
    return selected


def _int_or(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _quest_completed(player_data, quest_id):
    return bool(((player_data.get("quests", {}) or {}).get(quest_id) or {}).get("completed"))


def _combat_setup_spell_rows(player_data):
    magic_level = int(player_data.get("magic_level", 1) or 1)
    equipped_weapon = str((player_data.get("equipment", {}) or {}).get("weapon", "") or "")
    rows = []
    for spell_id, spec in COMBAT_MAGIC_SPELL_DATA.items():
        gate = str(spec.get("quest_gate", "") or "")
        if gate == "mage_arena":
            gate_done = bool((player_data.get("mage_arena", {}) or {}).get("completed"))
        else:
            gate_done = not gate or _quest_completed(player_data, gate)
        required_weapon = str(spec.get("required_weapon", "") or "")
        rows.append({
            "id": spell_id,
            "name": str(spec.get("display_name", spell_id)),
            "unlocked": (
                magic_level >= int(spec.get("required_magic_level", 1) or 1)
                and gate_done
                and (not required_weapon or equipped_weapon == required_weapon)
            ),
        })
    return rows


def _combat_setup_prayer_rows(player_data):
    """The current book's prayers; Knight Waves prayers explain their gate."""
    prayer_level = int(player_data.get("prayer_level", 1) or 1)
    defence_level = int(player_data.get("defense_level", 1) or 1)
    gates = {
        "the_temple_at_senntisten": _quest_completed(player_data, "the_temple_at_senntisten"),
        "knight_waves": bool((player_data.get("knight_waves", {}) or {}).get("completed")),
    }
    book = str(player_data.get("combat_prayer_book", "standard"))
    rows = []
    for prayer in COMBAT_PRAYERS:
        if prayer.book != book:
            continue
        requirements = [f"{prayer.level} Prayer"]
        if prayer.defence_level > 1:
            requirements.append(f"{prayer.defence_level} Defence")
        rows.append({
            "id": prayer.id,
            "label": f"{prayer.display_name} (Lv {'; '.join(requirements)})",
            "level": prayer.level,
            "unlocked": (
                prayer.level <= prayer_level
                and prayer.defence_level <= defence_level
                and gates.get(prayer.quest_gate, True)
            ),
            "tooltip": (
                f"Requires {', '.join(requirements)}, and Knight Waves completion."
                if prayer.quest_gate == "knight_waves"
                else ""
            ),
        })
    return rows
