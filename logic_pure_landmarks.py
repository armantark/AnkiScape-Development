"""logic_pure_landmarks.py - split out of logic_pure.py; see that module's header."""

from typing import Iterable, Mapping, Optional

try:
    from .logic_pure_state import (  # noqa: F401  (re-export)
        COMBAT_BANK_RUN_REVIEWS,
        COMBAT_GRAVE_RECOVERY_REVIEWS,
        _COMBAT_DRAGONFIRE_POTION_BY_DOSE,
        _COMBAT_DRAGONFIRE_POTION_ITEM_NAMES,
        _COMBAT_STAT_POTION_BY_DOSE,
        _COMBAT_STAT_POTION_ITEM_NAMES,
        _build_combat_potion_dose_lookup,
        _combat_grave_items,
        _combat_stored_loadout,
        _copy_player_data_with_nested,
        _non_negative_float,
        _non_negative_int,
        _positive_int,
        _requirements_from_spec,
        _sanitize_combat_bank_run,
        _sanitize_combat_grave_state,
        _sanitize_combat_supply_loadout,
        _sanitize_death_office_state,
        _signed_int,
        default_combat_supply_loadout_pure,
        quest_completed_pure,
        quest_state_pure,
        sanitize_quest_combat_active_encounters_pure,
    )
except ImportError:  # pragma: no cover - flat test imports
    from logic_pure_state import (  # type: ignore  # noqa: F401
        COMBAT_BANK_RUN_REVIEWS,
        COMBAT_GRAVE_RECOVERY_REVIEWS,
        _COMBAT_DRAGONFIRE_POTION_BY_DOSE,
        _COMBAT_DRAGONFIRE_POTION_ITEM_NAMES,
        _COMBAT_STAT_POTION_BY_DOSE,
        _COMBAT_STAT_POTION_ITEM_NAMES,
        _build_combat_potion_dose_lookup,
        _combat_grave_items,
        _combat_stored_loadout,
        _copy_player_data_with_nested,
        _non_negative_float,
        _non_negative_int,
        _positive_int,
        _requirements_from_spec,
        _sanitize_combat_bank_run,
        _sanitize_combat_grave_state,
        _sanitize_combat_supply_loadout,
        _sanitize_death_office_state,
        _signed_int,
        default_combat_supply_loadout_pure,
        quest_completed_pure,
        quest_state_pure,
        sanitize_quest_combat_active_encounters_pure,
    )

try:
    from .logic_pure_state import (
        _copy_player_data_with_nested,
        _non_negative_int,
        _positive_int,
    )
except ImportError:  # pragma: no cover - flat test imports
    from logic_pure_state import (  # type: ignore
        _copy_player_data_with_nested,
        _non_negative_int,
        _positive_int,
    )


# --- Stronghold of Security (one-time landmark) ---------------------------
# The Stronghold has four levels, one per horseman of the apocalypse. The
# player walks one level per review; finishing the last level unlocks a choice
# between two stat-identical boots plus a 10k-coin cash bag (2011Scape reward).
STRONGHOLD_STEP_NAMES = (
    "Vault of War",
    "Catacomb of Famine",
    "Pit of Pestilence",
    "Sepulchre of Death",
)


STRONGHOLD_TOTAL_STEPS = len(STRONGHOLD_STEP_NAMES)


STRONGHOLD_REWARD_COINS = 10000


STRONGHOLD_BOOT_CHOICES = ("Fancy boots", "Fighting boots")


def default_stronghold_state_pure():
    """Fresh Stronghold progress: not started, no reward taken."""
    return {"step": 0, "completed": False, "boots_choice": None}


def sanitize_stronghold_state_pure(raw):
    """Coerce a loaded Stronghold blob back into shape, clamping the step and
    keeping ``completed`` consistent with it."""
    state = default_stronghold_state_pure()
    if isinstance(raw, Mapping):
        try:
            step = int(raw.get("step", 0))
        except (TypeError, ValueError):
            step = 0
        state["step"] = max(0, min(step, STRONGHOLD_TOTAL_STEPS))
        state["completed"] = bool(raw.get("completed")) or state["step"] >= STRONGHOLD_TOTAL_STEPS
        choice = raw.get("boots_choice")
        state["boots_choice"] = choice if choice in STRONGHOLD_BOOT_CHOICES else None
    return state


def apply_stronghold_step_pure(player_data):
    """Advance the Stronghold of Security by one level (one review = one step).

    Steps run 0 -> STRONGHOLD_TOTAL_STEPS with no XP or items earned en route;
    reaching the final level flips ``completed``. A no-op once completed.
    Returns {"advanced", "step", "completed", "just_completed"}.
    """
    state = player_data.setdefault("stronghold_of_security", default_stronghold_state_pure())
    if state.get("completed"):
        return {
            "advanced": False,
            "step": int(state.get("step", STRONGHOLD_TOTAL_STEPS)),
            "completed": True,
            "just_completed": False,
        }
    step = min(int(state.get("step", 0)) + 1, STRONGHOLD_TOTAL_STEPS)
    just_completed = step >= STRONGHOLD_TOTAL_STEPS
    state["step"] = step
    state["completed"] = just_completed
    return {"advanced": True, "step": step, "completed": just_completed, "just_completed": just_completed}


def grant_stronghold_reward_pure(player_data, boots_choice):
    """One-time completion reward: STRONGHOLD_REWARD_COINS coins plus the chosen
    boots. Guarded on an unset ``boots_choice`` so it can fire only once.
    Returns True when the reward was granted.
    """
    if boots_choice not in STRONGHOLD_BOOT_CHOICES:
        return False
    state = player_data.setdefault("stronghold_of_security", default_stronghold_state_pure())
    if not state.get("completed") or state.get("boots_choice") is not None:
        return False
    inventory = player_data.setdefault("inventory", {})
    inventory["Coins"] = inventory.get("Coins", 0) + STRONGHOLD_REWARD_COINS
    inventory[boots_choice] = inventory.get(boots_choice, 0) + 1
    state["boots_choice"] = boots_choice
    return True


# King's Ransom oldid=6548731: 65 Defence and 45 Magic to start.
# Knight Waves oldid=6575464: eight knights and 20,000 XP in each listed stat.
KNIGHT_WAVES_TOTAL_STEPS = 8


KNIGHT_WAVES_XP_REWARD = 20000


MAGE_ARENA_STEP_NAMES = ("Human", "Ogre", "Giant spider", "Ghost", "Black demon")


MAGE_ARENA_TOTAL_STEPS = len(MAGE_ARENA_STEP_NAMES)


MAGE_ARENA_GOD_DATA = {
    "saradomin": {
        "display_name": "Saradomin",
        "cape": "Saradomin cape",
        "staff": "Saradomin staff",
        "spell_id": "saradomin_strike",
        "spell_name": "Saradomin Strike",
    },
    "guthix": {
        "display_name": "Guthix",
        "cape": "Guthix cape",
        "staff": "Guthix staff",
        "spell_id": "claws_of_guthix",
        "spell_name": "Claws of Guthix",
    },
    "zamorak": {
        "display_name": "Zamorak",
        "cape": "Zamorak cape",
        "staff": "Zamorak staff",
        "spell_id": "flames_of_zamorak",
        "spell_name": "Flames of Zamorak",
    },
}


MAGE_ARENA_GOD_CAPES = frozenset(
    row["cape"] for row in MAGE_ARENA_GOD_DATA.values()
)


MAGE_ARENA_GOD_STAVES = frozenset(
    row["staff"] for row in MAGE_ARENA_GOD_DATA.values()
)


MAGE_ARENA_SPELL_TO_GOD = {
    row["spell_id"]: god_id for god_id, row in MAGE_ARENA_GOD_DATA.items()
}


def default_knight_waves_state_pure():
    return {"step": 0, "completed": False}


def sanitize_knight_waves_state_pure(raw):
    state = default_knight_waves_state_pure()
    if isinstance(raw, Mapping):
        state["step"] = min(KNIGHT_WAVES_TOTAL_STEPS, _non_negative_int(raw.get("step", 0), 0))
        state["completed"] = bool(raw.get("completed")) or state["step"] >= KNIGHT_WAVES_TOTAL_STEPS
    return state


def knight_waves_locked_reasons_pure(player_data):
    reasons = []
    quests = player_data.get("quests", {}) or {}
    if not bool((quests.get("kings_ransom") or {}).get("completed")):
        reasons.append("King's Ransom")
    if _positive_int(player_data.get("defense_level", 1), 1) < 65:
        reasons.append("Defence level 65")
    if _positive_int(player_data.get("magic_level", 1), 1) < 45:
        reasons.append("Magic level 45")
    if sanitize_knight_waves_state_pure(player_data.get("knight_waves"))["completed"]:
        reasons.append("already completed")
    return tuple(reasons)


def apply_knight_waves_step_pure(player_data):
    data = _copy_player_data_with_nested(player_data)
    reasons = knight_waves_locked_reasons_pure(data)
    if reasons:
        return data, False, {"reason": "knight_waves_locked", "locked_reasons": reasons}
    state = sanitize_knight_waves_state_pure(data.get("knight_waves"))
    state["step"] += 1
    just_completed = state["step"] >= KNIGHT_WAVES_TOTAL_STEPS
    state["completed"] = just_completed
    rewards = {}
    if just_completed:
        for skill in ("attack", "strength", "defense", "constitution"):
            key = f"{skill}_exp"
            data[key] = float(data.get(key, 0.0) or 0.0) + KNIGHT_WAVES_XP_REWARD
            rewards[key] = KNIGHT_WAVES_XP_REWARD
    data["knight_waves"] = state
    return data, True, {"reason": "knight_waves", "step": state["step"], "completed": just_completed, "xp_rewards": rewards}


def mage_arena_locked_reasons_pure(player_data):
    reasons = []
    if _positive_int(player_data.get("magic_level", 1), 1) < 60:
        reasons.append("Magic level 60")
    state = sanitize_mage_arena_state_pure(player_data.get("mage_arena"))
    if bool(state.get("completed")):
        reasons.append("already completed")
    elif state["step"] == MAGE_ARENA_TOTAL_STEPS - 1 and not state["alignment"]:
        reasons.append("Choose a god alignment")
    return tuple(reasons)


def default_mage_arena_state_pure():
    return {
        "step": 0,
        "completed": False,
        "alignment": "",
        "attuned_spells": [],
    }


def sanitize_mage_arena_state_pure(raw):
    state = default_mage_arena_state_pure()
    if not isinstance(raw, Mapping):
        return state
    state["step"] = min(
        MAGE_ARENA_TOTAL_STEPS,
        _non_negative_int(raw.get("step", 0), 0),
    )
    state["completed"] = (
        bool(raw.get("completed")) or state["step"] >= MAGE_ARENA_TOTAL_STEPS
    )
    alignment = str(raw.get("alignment", "") or "")
    state["alignment"] = alignment if alignment in MAGE_ARENA_GOD_DATA else ""
    raw_attuned = raw.get("attuned_spells", ())
    if isinstance(raw_attuned, (list, tuple, set, frozenset)):
        state["attuned_spells"] = [
            spell_id
            for spell_id in MAGE_ARENA_SPELL_TO_GOD
            if spell_id in raw_attuned
        ]
    return state


def set_mage_arena_alignment_pure(player_data, god_id):
    data = _copy_player_data_with_nested(player_data)
    state = sanitize_mage_arena_state_pure(data.get("mage_arena"))
    if god_id not in MAGE_ARENA_GOD_DATA:
        return data, False, {"reason": "unknown_alignment"}
    if state["completed"]:
        return data, False, {"reason": "mage_arena_completed"}
    state["alignment"] = god_id
    data["mage_arena"] = state
    return data, True, {"reason": "alignment_selected", "alignment": god_id}


def _owns_or_equips_pure(player_data, item_name):
    inventory = player_data.get("inventory", {}) or {}
    equipment = player_data.get("equipment", {}) or {}
    return (
        _non_negative_int(inventory.get(item_name, 0), 0) > 0
        or item_name in equipment.values()
    )


def attune_mage_arena_spell_pure(player_data, god_id):
    data = _copy_player_data_with_nested(player_data)
    state = sanitize_mage_arena_state_pure(data.get("mage_arena"))
    row = MAGE_ARENA_GOD_DATA.get(god_id)
    if not state["completed"]:
        return data, False, {"reason": "mage_arena_incomplete"}
    if row is None:
        return data, False, {"reason": "unknown_alignment"}
    if row["spell_id"] in state["attuned_spells"]:
        return data, False, {"reason": "already_attuned"}
    if not _owns_or_equips_pure(data, row["staff"]):
        return data, False, {"reason": "missing_staff", "staff": row["staff"]}
    state["attuned_spells"].append(row["spell_id"])
    data["mage_arena"] = state
    return data, True, {
        "reason": "spell_attuned",
        "alignment": god_id,
        "spell_id": row["spell_id"],
        "spell_name": row["spell_name"],
    }


def apply_mage_arena_cape_action_pure(player_data, god_id):
    data = _copy_player_data_with_nested(player_data)
    state = sanitize_mage_arena_state_pure(data.get("mage_arena"))
    legacy_first_claim = not state["alignment"]
    row = MAGE_ARENA_GOD_DATA.get(god_id)
    if not state["completed"]:
        return data, False, {"reason": "mage_arena_incomplete"}
    if row is None:
        return data, False, {"reason": "unknown_alignment"}

    inventory = data.setdefault("inventory", {})
    equipment = data.setdefault("equipment", {})
    equipped_cape = equipment.get("cape")
    target_is_equipped = equipped_cape == row["cape"]
    if equipped_cape in MAGE_ARENA_GOD_CAPES and not target_is_equipped:
        equipment.pop("cape", None)
    for cape_name in MAGE_ARENA_GOD_CAPES:
        inventory[cape_name] = 0
    if not target_is_equipped:
        inventory[row["cape"]] = 1
    if legacy_first_claim:
        if not _owns_or_equips_pure(data, row["staff"]):
            inventory[row["staff"]] = 1
        if row["spell_id"] not in state["attuned_spells"]:
            state["attuned_spells"].append(row["spell_id"])
    state["alignment"] = god_id
    data["mage_arena"] = state
    return data, True, {
        "reason": (
            "legacy_alignment_claimed"
            if legacy_first_claim
            else "cape_reclaimed" if target_is_equipped else "cape_replaced"
        ),
        "alignment": god_id,
        "cape": row["cape"],
        "staff": row["staff"] if legacy_first_claim else "",
        "spell_id": row["spell_id"] if legacy_first_claim else "",
    }


def apply_mage_arena_step_pure(player_data):
    """Defeat one Kolodion form; the fifth grants and attunes one god loadout."""
    data = _copy_player_data_with_nested(player_data)
    reasons = mage_arena_locked_reasons_pure(data)
    if reasons:
        reason = (
            "mage_arena_alignment_required"
            if reasons == ("Choose a god alignment",)
            else "mage_arena_locked"
        )
        return data, False, {"reason": reason, "locked_reasons": reasons}
    state = sanitize_mage_arena_state_pure(data.get("mage_arena"))
    step = min(MAGE_ARENA_TOTAL_STEPS, state["step"] + 1)
    completed = step >= MAGE_ARENA_TOTAL_STEPS
    state["step"] = step
    state["completed"] = completed
    rewards = {}
    if completed:
        row = MAGE_ARENA_GOD_DATA[state["alignment"]]
        inventory = data.setdefault("inventory", {})
        equipment = data.setdefault("equipment", {})
        for cape_name in MAGE_ARENA_GOD_CAPES:
            inventory[cape_name] = 0
        if equipment.get("cape") in MAGE_ARENA_GOD_CAPES:
            equipment.pop("cape", None)
        inventory[row["cape"]] = 1
        if not _owns_or_equips_pure(data, row["staff"]):
            inventory[row["staff"]] = 1
        state["attuned_spells"] = [row["spell_id"]]
        rewards = {
            "alignment": state["alignment"],
            "cape": row["cape"],
            "staff": row["staff"],
            "spell_id": row["spell_id"],
        }
    data["mage_arena"] = state
    return data, True, {
        "reason": "mage_arena",
        "step": step,
        "completed": completed,
        **rewards,
    }


# --- Landmark HUD progress ------------------------------------------------
# Step-counter landmarks are deliberately absent from UTILITY_ACTIVITY_DATA, so
# the reviewer HUD had no step count to show and hid its progress bar for the
# whole utility branch: a Stronghold walk looked identical to bankstanding.
# The rows below are derived from each landmark's own step list so the HUD can
# never drift from the Activities tree. Each entry is
# (display_name, step_names, state_key, step_field, sanitizer).
try:
    from .stronghold_player_safety_data import STRONGHOLD_LANDMARKS
    from .stronghold_player_safety_logic import (
        sanitize_stronghold_player_safety_state_pure,
    )
except ImportError:  # pragma: no cover - flat test imports
    from stronghold_player_safety_data import STRONGHOLD_LANDMARKS  # type: ignore
    from stronghold_player_safety_logic import (  # type: ignore
        sanitize_stronghold_player_safety_state_pure,
    )


LANDMARK_HUD_ROWS = {
    "stronghold_of_security": (
        "Stronghold of Security",
        STRONGHOLD_STEP_NAMES,
        "stronghold_of_security",
        "step",
        sanitize_stronghold_state_pure,
    ),
    # The eight knights are fought in sequence and the source does not fix an
    # order, so the waves are numbered rather than named.
    "knight_waves": (
        "Knight Waves Training Ground",
        tuple(f"Wave {index}" for index in range(1, KNIGHT_WAVES_TOTAL_STEPS + 1)),
        "knight_waves",
        "step",
        sanitize_knight_waves_state_pure,
    ),
    "mage_arena": (
        "Mage Arena",
        MAGE_ARENA_STEP_NAMES,
        "mage_arena",
        "step",
        sanitize_mage_arena_state_pure,
    ),
    "stronghold_player_safety": (
        "Stronghold of Player Safety",
        tuple(str(row["label"]) for row in STRONGHOLD_LANDMARKS),
        "stronghold_player_safety",
        "stage",
        sanitize_stronghold_player_safety_state_pure,
    ),
}


def landmark_hud_progress_pure(player_data, target_id):
    """Progress row for a step-counter landmark, or None when not one.

    Returns {"display_name", "step", "total", "percent", "next_step_name",
    "completed"}. ``next_step_name`` names the step the player is walking into
    (empty once finished), matching the Activities tree's "next:" label; the
    step just cleared is already named by the review toast.
    """
    row = LANDMARK_HUD_ROWS.get(str(target_id or ""))
    if row is None:
        return None
    display_name, step_names, state_key, step_field, sanitize = row
    total = len(step_names)
    state = sanitize(player_data.get(state_key))
    step = min(total, _non_negative_int(state.get(step_field, 0), 0))
    return {
        "display_name": display_name,
        "step": step,
        "total": total,
        "percent": int(round(100 * step / total)) if total else 0,
        "next_step_name": step_names[step] if step < total else "",
        "completed": step >= total,
    }
