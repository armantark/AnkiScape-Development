"""What the combat surfaces show: the HUD's health, prayer and summoning bars,
last-fight summary and finisher text, and the settings the Equipment tab's
combat setup panel draws, with the prayers and max hit its next fight gets."""

from typing import Mapping

from ..data.combat_data import COMBAT_ENEMY_DATA, COMBAT_MAGIC_SPELL_DATA, DEFAULT_COMBAT_SPELL, DEFAULT_COMBAT_TARGET
from ..data.prayer_data import COMBAT_PRAYERS, COMBAT_PRAYERS_BY_ID, DEFAULT_PRAYER_UPTIME, PRAYER_UPTIME_POLICIES
from ..logic.inventory_pure import DEFAULT_LOOT_VALUE_THRESHOLD
from .logic_pure_combat_finishers import (
    combat_finisher_notice_pure,
    combat_finisher_tooltip_pure,
)
from .logic_pure_combat_loadout import _combat_target_loadout
from .logic_pure_combat_model import combat_attack_style_for_equipment_pure, combat_max_lifepoints_pure
from .logic_pure_prayer import active_prayer_selection_pure, prayer_uptime_fraction_pure, sanitize_prayer_selection_pure
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
        "prayer_texts": _combat_hud_prayer_texts(player_data, f"{prayer_current}/{prayer_max}"),
        "summoning_points": summoning_current,
        "summoning_max_points": summoning_max,
    }


def _combat_hud_prayer_texts(player_data, points):
    """The prayer points with the running prayers, longest first: every name,
    then fewer names and "+N" for the rest, then only the count, for the strip
    to show the longest that fits."""
    names, uptime, _picked = combat_fight_prayers_pure(player_data)
    share = f" ({uptime:.0%})" if names and uptime < 1 else ""
    texts = [
        f"{points} · {', '.join(names[:shown])}{f' +{len(names) - shown}' if shown < len(names) else ''}{share}"
        for shown in range(len(names), 0, -1)
    ]
    if len(names) > 1:
        texts.append(f"{points} · {len(names)} prayers{share}")
    return texts or [points]


def combat_fight_prayers_pure(player_data):
    """The prayers the next fight with the current target runs, by name; the
    share of it they stay on; and whether the game picked them because none is
    ticked. None run while Prayers/Curses is unticked or the points are spent."""
    target_id = str(player_data.get("current_combat_target", DEFAULT_COMBAT_TARGET))
    loadout = _combat_target_loadout(player_data, target_id)
    uptime = prayer_uptime_fraction_pure(loadout)
    if uptime <= 0:
        return [], 0.0, False
    names = [COMBAT_PRAYERS_BY_ID[prayer_id].display_name for prayer_id in active_prayer_selection_pure(loadout)]
    return names, uptime, not sanitize_prayer_selection_pure(loadout, loadout.get("combat_selected_prayers", ()))


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


def combat_setup_panel_view_pure(player_data, equipment_data):
    """Every saved setting the combat setup panel shows, which spells and
    prayers it offers as unlocked, and what the next fight gets from them: the
    prayers it runs and the max hit they give."""
    target_id = str(player_data.get("current_combat_target", DEFAULT_COMBAT_TARGET))
    target_overrides = (player_data.get("combat_target_overrides", {}) or {}).get(target_id, {}) or {}
    presets = player_data.get("combat_presets", {}) or {}
    active_preset = str(player_data.get("combat_active_preset", "Default"))
    magic_mode = combat_attack_style_for_equipment_pure(player_data, equipment_data) == "magic_standard"
    pinned_preset = str((player_data.get("combat_target_presets", {}) or {}).get(target_id, "") or "")
    return {
        **_combat_setup_prayer_view(player_data),
        "finisher_chosen": player_data.get("combat_action") == "finisher",
        "magic_mode": magic_mode,
        "styles": _combat_setup_style_rows(player_data, equipment_data),
        "autocast_spell": player_data.get("current_combat_spell", DEFAULT_COMBAT_SPELL),
        "spells": _combat_setup_spell_rows(player_data),
        "borrowed_power_spell": player_data.get("combat_borrowed_power_spell"),
        "dream_thrift": bool(player_data.get("combat_dream_thrift", False)),
        "auto_prayer_training": bool(player_data.get("combat_auto_prayer_training", False)),
        "auto_eat_threshold": max(1, min(_int_or(player_data.get("combat_auto_eat_threshold_percent", 40) or 40, 40), 99)),
        "preset_names": [str(name) for name in presets] if isinstance(presets, dict) else ["Default"],
        "active_preset": active_preset,
        "max_hit_text": _combat_setup_max_hit_text(player_data, target_id, equipment_data, magic_mode),
        "vengeance": bool(player_data.get("combat_vengeance", False)),
        "spellbook_swap": str(player_data.get("combat_spellbook_swap", "") or ""),
        "pinned_preset": pinned_preset,
        "prayers_overridden": "combat_selected_prayers" in target_overrides,
        "uptime_overridden": "combat_prayer_uptime" in target_overrides,
        "target_summary": _combat_setup_target_summary(player_data, target_id, pinned_preset, target_overrides),
        "loot_threshold": max(0, _int_or(player_data.get("loot_value_threshold", DEFAULT_LOOT_VALUE_THRESHOLD), DEFAULT_LOOT_VALUE_THRESHOLD)),
    }


def _combat_setup_prayer_view(player_data):
    """The Prayer group: its settings, the boxes it ticks, and the prayers it
    lists as unlocking later."""
    uptime = str(player_data.get("combat_prayer_uptime", DEFAULT_PRAYER_UPTIME))
    rows = _combat_setup_prayer_rows(player_data)
    locked = [row["label"] for row in rows if not row["unlocked"]]
    ticked = _ticked_prayer_ids(player_data)
    enabled = bool(player_data.get("combat_prayers_enabled", True))
    picked = bool(ticked) and not _chosen_prayer_ids(player_data)
    return {
        "prayers_enabled": enabled,
        "curses_unlocked": _quest_completed(player_data, "the_temple_at_senntisten"),
        "prayer_book": player_data.get("combat_prayer_book", "standard"),
        "prayer_uptime": uptime if uptime in PRAYER_UPTIME_POLICIES else DEFAULT_PRAYER_UPTIME,
        "prayer_status": _combat_setup_prayer_status(player_data),
        "selected_prayers": set(ticked),
        "prayers_picked": picked,
        **_auto_pick_button(enabled, picked),
        "prayers": [row for row in rows if row["unlocked"]],
        "locked_prayers": locked,
        # "Hide lower-tier prayers" keeps the 15 levels below the player's own.
        "lower_tier_below": max(1, int(player_data.get("prayer_level", 1) or 1) - 15),
    }


def _auto_pick_button(enabled, picked):
    """The way back to the game's pick, saying why when it cannot be used."""
    in_use = enabled and picked
    if not enabled:
        tooltip = "Tick “Use prayers in fights” first."
    elif in_use:
        tooltip = "The blue ticks are already the best prayers for your weapon."
    else:
        tooltip = "Clear your ticks and let the game pick the best prayers for your weapon."
    return {
        "auto_pick_text": "Using the best pick" if in_use else "Pick the best for me",
        "auto_pick_enabled": enabled and not in_use,
        "auto_pick_tooltip": tooltip,
    }


def _chosen_prayer_ids(player_data):
    return sanitize_prayer_selection_pure(player_data, player_data.get("combat_selected_prayers", ()))


def _ticked_prayer_ids(player_data):
    """The boxes the grid ticks: the player's choice, or, while nothing is
    chosen, the prayers the game picks, so the grid shows what runs."""
    return _chosen_prayer_ids(player_data) or active_prayer_selection_pure(player_data)


def prayer_swap_note_pure(player_data, prayer_id, checked):
    """The note for ticking a prayer that pushes out a ticked one sharing its
    slot, so the box that unticks itself says why; empty when none does."""
    if not checked:
        return ""
    kept = set(sanitize_prayer_selection_pure(player_data, toggled_combat_prayer_selection_pure(player_data, prayer_id, True)))
    dropped = [COMBAT_PRAYERS_BY_ID[other].display_name for other in _ticked_prayer_ids(player_data) if other not in kept]
    if not dropped:
        return ""
    return f"{COMBAT_PRAYERS_BY_ID[prayer_id].display_name} replaced {_and_list(dropped)}: they cannot run together."


def toggled_combat_prayer_selection_pure(player_data, prayer_id, checked):
    """The selection after one prayer box changes, starting from the ticked
    boxes, picked ones included. A newly ticked prayer goes first, so the save
    drops only the ticked prayer that shares its slot."""
    selected = [str(pid) for pid in _ticked_prayer_ids(player_data) if str(pid) != prayer_id]
    if checked:
        selected.insert(0, prayer_id)
    return selected


def _and_list(names):
    return " and ".join((", ".join(names[:-1]), names[-1])) if len(names) > 1 else "".join(names)


def _prayer_share(uptime):
    return "the whole fight" if uptime >= 1 else f"{uptime:.0%} of the fight"


def _combat_setup_prayer_status(player_data):
    """One line saying which prayers the next fight runs, and why."""
    if not bool(player_data.get("combat_prayers_enabled", True)):
        if _chosen_prayer_ids(player_data):
            return "Off: no prayers run in fights. The greyed ticks are saved for when prayers are on."
        return "Off: no prayers run in fights."
    names, uptime, picked = combat_fight_prayers_pure(player_data)
    if not names:
        return "No prayer points left. The next bank run's altar stop restores them."
    if picked:
        return (
            f"Picked for you (blue ticks): the best for your weapon, for {_prayer_share(uptime)}. "
            "Tick or untick a box to make your own choice."
        )
    return f"Next fight runs {_and_list(names)} for {_prayer_share(uptime)}."


def _combat_setup_max_hit_text(player_data, target_id, equipment_data, magic_mode):
    """The max hit and accuracy against the target, naming the prayers they
    count, so a ticked prayer never moves the number without its reason."""
    # The engine builds its HUD state from this module.
    from .logic_pure_combat_engine import combat_target_preview_pure

    preview = combat_target_preview_pure(player_data, target_id, equipment_data=equipment_data)
    if preview.get("state") == "blocked":
        return f"Can't fight this target yet: {', '.join(preview.get('reasons') or ('locked',))}."
    accuracy = f"accuracy {float(preview.get('accuracy', 0.0) or 0.0):.0%}"
    if magic_mode:
        return f"Your max hit: {preview.get('player_max_hit', 0)} LP · {accuracy} (prayers do not change Magic hits)"
    names, uptime, picked = combat_fight_prayers_pure(player_data)
    prayers = "with no prayers"
    if names:
        prayers = f"with {_and_list(names)}{'' if uptime >= 1 else f' for {_prayer_share(uptime)}'}{' (picked for you)' if picked else ''}"
    return f"Your max hit: {preview.get('player_max_hit', 0)} LP {prayers} · {accuracy}"


def _combat_setup_target_summary(player_data, target_id, pinned_preset, target_overrides):
    """Which source wins against this target: its kept prayers and prayer
    time beat its preset, which beats the settings above."""
    loadout = _combat_target_loadout(player_data, target_id)
    preset = ((player_data.get("combat_presets", {}) or {}).get(pinned_preset) or {}) if pinned_preset else {}
    sources = []
    for field, shown in (
        ("combat_selected_prayers", _summary_prayers(loadout)),
        ("combat_prayer_uptime", _prayer_share(PRAYER_UPTIME_POLICIES.get(str(loadout.get("combat_prayer_uptime")), 1.0))),
    ):
        if field in target_overrides:
            source = "kept for this target"
        elif field in preset:
            source = f"from preset {pinned_preset}"
        else:
            source = "from above"
        sources.append(f"{shown} ({source})")
    name = COMBAT_ENEMY_DATA.get(target_id, {}).get("display_name", target_id)
    preset_part = f"preset {pinned_preset}" if pinned_preset else "no preset"
    return f"Against {name}: {preset_part} · prayers {sources[0]} · prayer time {sources[1]}"


def _summary_prayers(loadout):
    if not bool(loadout.get("combat_prayers_enabled", True)):
        return "off"
    chosen = _chosen_prayer_ids(loadout)
    return _and_list([COMBAT_PRAYERS_BY_ID[prayer_id].display_name for prayer_id in chosen]) if chosen else "picked for you"


def _combat_setup_style_rows(player_data, equipment_data):
    """Each attack style the weapon offers, named with the skills it trains
    besides Constitution, which every style trains."""
    # The engine builds its HUD state from this module.
    from .logic_pure_combat_engine import combat_weapon_style_options_pure

    return [
        {
            "label": f"{option['display_name']}: trains {_and_list([skill for skill in option['trained_skills'] if skill != 'Constitution'])}",
            "data": (option["weapon_style"], option["style_type"]),
            "current": option["is_current"],
        }
        for option in combat_weapon_style_options_pure(player_data, equipment_data)
    ]


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
    """The current book's prayers, each naming its gates on hover. A locked
    prayer's label also names them, for the line that lists what unlocks later."""
    prayer_level = int(player_data.get("prayer_level", 1) or 1)
    defence_level = int(player_data.get("defense_level", 1) or 1)
    gates = {
        "the_temple_at_senntisten": _quest_completed(player_data, "the_temple_at_senntisten"),
        "knight_waves": bool((player_data.get("knight_waves", {}) or {}).get("completed")),
    }
    rows = []
    for prayer in COMBAT_PRAYERS:
        if prayer.book != str(player_data.get("combat_prayer_book", "standard")):
            continue
        unlocked = (
            prayer.level <= prayer_level
            and prayer.defence_level <= defence_level
            and gates.get(prayer.quest_gate, True)
        )
        levels = f"Lv {prayer.level}{f', Def {prayer.defence_level}' if prayer.defence_level > 1 else ''}{', Knight Waves' if prayer.quest_gate == 'knight_waves' else ''}"
        requirements = f"{prayer.level} Prayer{f', {prayer.defence_level} Defence' if prayer.defence_level > 1 else ''}"
        rows.append({
            "id": prayer.id,
            "label": prayer.display_name if unlocked else f"{prayer.display_name} ({levels})",
            "level": prayer.level,
            "unlocked": unlocked,
            "tooltip": f"Requires {requirements}{', and Knight Waves completion' if prayer.quest_gate == 'knight_waves' else ''}.",
        })
    return rows
