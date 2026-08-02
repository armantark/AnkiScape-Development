"""Capes of Accomplishment and Distinction: buying, trimming, wearing, boosting.

The design contract
(``memory-bank/achievement-diary-item-grants-design.md``) governs this module.
Four rules of it live here:

- a skillcape needs level 99, costs 99,000 coins from that skill's master, and
  arrives with its hood;
- a second level 99 irreversibly trims every skillcape the player owns, while
  the Cabinet keeps the untrimmed keepsake of the first 99;
- an equipped skillcape keeps its worn ``Boost`` option's visible +1 active for
  success and yield rolls, and never unlocks a level-gated action; and
- the quest point, Max, Completionist and Veteran capes are bought once each
  against a durable predicate.

``effective_roll_level_pure`` is the project's single effective-level function.
It composes a worn skillcape's visible boost with a live familiar's invisible
boost, so no caller has to know there is more than one and no third mechanism
can grow beside them.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ..core.skill_registry import ALL_SKILLS, trainable_skill_definitions
from ..data.achievement_cape_data import (
    MASTER_CAPES_BY_ID,
    PRESTIGE_CAPES,
    PRESTIGE_CAPES_BY_ID,
    SKILLCAPE_LEVEL,
    SKILLCAPE_PRICE,
    CompletionistRequirement,
    MasterCape,
    Skillcape,
    completionist_requirement_definitions,
    master_cape_definitions,
    skillcape_definitions,
)
from .summoning_logic import familiar_effective_roll_level_pure


CAPE_STATE_VERSION = 1

# The worn `Boost` option is a visible +1 with a ceiling of 100. AnkiScape has
# no real-time decay clock, so the verified operate-and-decay mechanic is ported
# at full uptime while worn. See skillcape-mechanics-verification-2026-07-27.md.
SKILLCAPE_EFFECTIVE_LEVEL = 100


def _int(value: Any, default: int = 0) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError, OverflowError):
        return default


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


# ---------------------------------------------------------------------------
# Persistent state
# ---------------------------------------------------------------------------


def default_cape_state_pure() -> dict[str, Any]:
    return {
        "capes": {
            "version": CAPE_STATE_VERSION,
            # The first skill to reach 99. Display only: the Cabinet shows this
            # cape's untrimmed artwork forever, which is the honest half of the
            # period keepsake key without importing RuneCoins.
            "keepsake_skill": "",
        }
    }


def sanitize_cape_state_pure(player_data: Mapping[str, Any] | None) -> dict[str, Any]:
    source = _mapping(_mapping(player_data).get("capes"))
    keepsake = str(source.get("keepsake_skill", "") or "")
    return {
        "capes": {
            "version": CAPE_STATE_VERSION,
            "keepsake_skill": keepsake if keepsake in {cape.skill_id for cape in skillcape_definitions()} else "",
        }
    }


def _state(player_data: Mapping[str, Any]) -> dict[str, Any]:
    return sanitize_cape_state_pure(player_data)["capes"]


# ---------------------------------------------------------------------------
# Levels, trimming and the keepsake
# ---------------------------------------------------------------------------


def skills_at_99_pure(player_data: Mapping[str, Any]) -> tuple[str, ...]:
    """Skill ids at level 99 or above, in registry order."""

    return tuple(
        skill.id
        for skill in trainable_skill_definitions()
        if _int(player_data.get(f"{skill.id}_level", 1), 1) >= SKILLCAPE_LEVEL
    )


def skillcapes_are_trimmed_pure(player_data: Mapping[str, Any]) -> bool:
    """Darkan's ``checkMulti99s``: more than one 99 trims every cape."""

    return len(skills_at_99_pure(player_data)) > 1


def _owned_names(player_data: Mapping[str, Any]) -> set[str]:
    owned = {
        name for name, amount in _mapping(player_data.get("inventory")).items() if _int(amount) > 0
    }
    owned.update(str(worn) for worn in _mapping(player_data.get("equipment")).values() if worn)
    return owned


def refresh_capes_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    """Record the first-99 keepsake, trim owned capes, and unequip lost prestige capes.

    Darkan trims on the 99 level-up itself, walking equipment, inventory and
    every bank tab. AnkiScape has one Bank, so the same sweep is inventory plus
    the worn slots, run whenever state is refreshed.
    """

    data = dict(player_data)
    state = _state(data)
    reached = skills_at_99_pure(data)
    if reached and not state["keepsake_skill"]:
        state["keepsake_skill"] = reached[0]
    data["capes"] = state
    data = _unequip_ineligible_prestige_capes(data)
    if len(reached) <= 1:
        return data

    inventory = dict(_mapping(data.get("inventory")))
    equipment = dict(_mapping(data.get("equipment")))
    changed = False
    for cape in skillcape_definitions():
        held = _int(inventory.pop(cape.cape, 0))
        if held:
            inventory[cape.trimmed_cape] = _int(inventory.get(cape.trimmed_cape)) + held
            changed = True
        for slot, worn in list(equipment.items()):
            if worn == cape.cape:
                equipment[slot] = cape.trimmed_cape
                changed = True
    if changed:
        data["inventory"] = inventory
        data["equipment"] = equipment
    return data


# ---------------------------------------------------------------------------
# The single effective-level seam
# ---------------------------------------------------------------------------


def worn_skillcape_skill_pure(player_data: Mapping[str, Any], skill_id: str) -> bool:
    """Whether ``skill_id``'s cape — trimmed or not — is in a worn slot."""

    cape = next((row for row in skillcape_definitions() if row.skill_id == skill_id), None)
    names = {cape.cape, cape.trimmed_cape} if cape is not None else set()
    names.update(
        row.cape for row in master_cape_definitions() if row.skill_id == skill_id
    )
    worn = {str(item) for item in _mapping(player_data.get("equipment")).values()}
    return bool(worn & names)


def effective_roll_level_pure(
    player_data: Mapping[str, Any], skill_id: str, base_level: Any
) -> int:
    """The one effective level: familiar boost and skillcape composed together.

    Success and yield formulas take this; gates do not. The contract is explicit
    that a skillcape "does not unlock a level-gated action", so every caller
    keeps checking the raw ``<skill>_level`` before it decides an action is
    allowed, and passes this value only to the roll.
    """

    visible_level = max(1, _int(base_level, 1))
    if (
        worn_skillcape_skill_pure(player_data, skill_id)
        and visible_level < SKILLCAPE_EFFECTIVE_LEVEL
    ):
        visible_level += 1
    return familiar_effective_roll_level_pure(player_data, skill_id, visible_level)


# ---------------------------------------------------------------------------
# Eligibility
# ---------------------------------------------------------------------------


def _all_quests_complete(player_data: Mapping[str, Any]) -> bool:
    from ..data.quest_data import QUESTS

    quests = _mapping(player_data.get("quests"))
    # The frozen Completionist table lists its miniquest requirements separately,
    # and the Quest point cape gates on quests alone, so catalog miniquests must
    # not join either quest count. "Including capers" does not mean miniquests.
    pool = tuple(quest for quest in QUESTS if not quest.miniquest)
    return bool(pool) and all(
        bool(_mapping(quests.get(quest.id)).get("completed")) for quest in pool
    )


def latent_cutoff_skills_pure() -> tuple[str, ...]:
    """Cutoff skills the all-skills capes cannot ask for yet, in registry order."""

    trainable = {skill.id for skill in trainable_skill_definitions()}
    return tuple(skill.id for skill in ALL_SKILLS if skill.id not in trainable)


def _latent_skill_note() -> str:
    latent = latent_cutoff_skills_pure()
    if not latent:
        return ""
    names = ", ".join(skill_id.replace("_", " ").title() for skill_id in latent)
    return f" ({names} latent until the skill ships)"


def _answered_cards(player_data: Mapping[str, Any]) -> int:
    return _int(_mapping(player_data.get("shop_market_clock")).get("answered_cards"))


_MISSING = object()


def _path_value(player_data: Mapping[str, Any], path: Sequence[str]) -> Any:
    value: Any = player_data
    for key in path:
        if not isinstance(value, Mapping) or key not in value:
            return _MISSING
        value = value[key]
    return value


def _completionist_maxed_skills_pure(player_data: Mapping[str, Any]) -> tuple[int, int]:
    skills = trainable_skill_definitions()
    completed = sum(
        _int(player_data.get(f"{skill.id}_level", 1), 1)
        >= (120 if skill.id == "dungeoneering" else SKILLCAPE_LEVEL)
        for skill in skills
    )
    return completed, len(skills)


def _registered_requirement_value(
    player_data: Mapping[str, Any], requirement: CompletionistRequirement
) -> Any:
    """Read an owning feature's direct counter or its registry-keyed counter.

    Rows without a direct path stay latent until their feature writes the stable
    requirement id into ``completionist_counters``. No cape-logic edit is needed
    when that counter ships.
    """

    direct = (
        _path_value(player_data, requirement.counter_path)
        if requirement.counter_path
        else _MISSING
    )
    if direct is not _MISSING:
        return direct
    counters = _mapping(player_data.get("completionist_counters"))
    return counters.get(requirement.id, _MISSING)


def _completionist_requirement_view_pure(
    player_data: Mapping[str, Any], requirement: CompletionistRequirement
) -> dict[str, Any]:
    kind = requirement.predicate_kind
    have = 0
    need = 0
    latent = False
    if kind == "max_levels":
        have, need = _completionist_maxed_skills_pure(player_data)
        met = have == need and need > 0
    elif kind == "all_quests":
        met = _all_quests_complete(player_data)
    elif kind == "taskmaster":
        from .achievement_diary_logic import diary_totals_pure

        diary = diary_totals_pure(player_data)
        have, need = diary["completed"], diary["total"]
        met = bool(_mapping(player_data.get("achievement_diaries")).get("taskmaster"))
    elif kind == "music":
        from .music_log_logic import music_log_totals_pure

        music = music_log_totals_pure(player_data)
        have, need = music["unlocked"], music["total"]
        met = have >= need and need > 0
    else:
        value = _registered_requirement_value(player_data, requirement)
        latent = value is _MISSING
        if latent:
            met = False
        elif (
            kind == "collection_count"
            and isinstance(value, Sequence)
            and not isinstance(value, (str, bytes))
        ):
            have, need = len(value), requirement.threshold
            met = have >= need
        elif (
            kind == "contains_any"
            and isinstance(value, Sequence)
            and not isinstance(value, (str, bytes))
        ):
            met = any(candidate in value for candidate in requirement.accepted_values)
            have, need = int(met), 1
        elif kind == "flag" or isinstance(value, bool):
            have, need = int(bool(value)), 1
            met = bool(value)
        else:
            have, need = _int(value), requirement.threshold
            met = have >= need
    return {
        "id": requirement.id,
        "label": requirement.label,
        "owner_feature": requirement.owner_feature,
        "met": met,
        "latent": latent,
        "have": have,
        "need": need,
    }


def completionist_requirements_pure(
    player_data: Mapping[str, Any]
) -> tuple[dict[str, Any], ...]:
    """Frozen regular Completionist rows, active only when their counters exist."""

    return tuple(
        _completionist_requirement_view_pure(player_data, requirement)
        for requirement in completionist_requirement_definitions("completionist")
    )


def trimmed_completionist_requirements_pure(
    player_data: Mapping[str, Any]
) -> tuple[dict[str, Any], ...]:
    """The frozen trim-only long tail; 5,000 Castle Wars games is live today."""

    return tuple(
        _completionist_requirement_view_pure(player_data, requirement)
        for requirement in completionist_requirement_definitions("trimmed")
    )


def prestige_cape_eligible_pure(
    player_data: Mapping[str, Any], cape_id: str
) -> tuple[bool, str]:
    """Return ``(eligible, reason)`` for one Cape of Distinction."""

    cape = PRESTIGE_CAPES_BY_ID.get(cape_id)
    if cape is None:
        return False, "Unknown cape."
    if cape.requirement == "all_quests":
        return (
            (True, "")
            if _all_quests_complete(player_data)
            else (False, "Complete every quest first.")
        )
    if cape.requirement == "all_skills_99":
        missing = len(trainable_skill_definitions()) - len(skills_at_99_pure(player_data))
        if missing:
            return False, f"{missing} skills short of 99.{_latent_skill_note()}"
        return True, ""
    if cape.requirement == "answered_cards":
        have = _answered_cards(player_data)
        return (
            (True, "")
            if have >= cape.threshold
            else (False, f"{cape.threshold - have:,} more answered cards.")
        )
    if cape.requirement in {"completionist", "trimmed_completionist"}:
        rows = list(completionist_requirements_pure(player_data))
        if cape.requirement == "trimmed_completionist":
            rows.extend(trimmed_completionist_requirements_pure(player_data))
        outstanding = [
            row["label"] for row in rows if not row["met"] and not row["latent"]
        ]
        return (True, "") if not outstanding else (False, "; ".join(outstanding))
    return False, "Unknown cape requirement."


PRESTIGE_CAPES_BY_ITEM: dict[str, str] = {cape.cape: cape.id for cape in PRESTIGE_CAPES}


def prestige_cape_wear_block_pure(
    player_data: Mapping[str, Any], item_name: str
) -> str:
    """Why a Cape of Distinction cannot be worn right now, or ``""`` if it can.

    The design contract: "Losing eligibility leaves the owned cape in Bank but
    makes it unusable". The gate is the same durable predicate the purchase
    checked — the pinned Quest Cape revision has the cape lose its wear
    eligibility the moment the quest maximum rises — so it cannot be a
    ``skill_requirements`` row, and ``can_equip_item_pure`` asks here instead.
    """

    cape_id = PRESTIGE_CAPES_BY_ITEM.get(item_name)
    if cape_id is None:
        return ""
    eligible, reason = prestige_cape_eligible_pure(player_data, cape_id)
    return "" if eligible else reason


def _unequip_ineligible_prestige_capes(data: dict[str, Any]) -> dict[str, Any]:
    """Move a no-longer-earned prestige cape off the body and back into the Bank."""

    equipment = dict(_mapping(data.get("equipment")))
    returned = [
        (slot, worn)
        for slot, worn in equipment.items()
        if prestige_cape_wear_block_pure(data, str(worn))
    ]
    if not returned:
        return data
    inventory = dict(_mapping(data.get("inventory")))
    for slot, worn in returned:
        del equipment[slot]
        inventory[str(worn)] = _int(inventory.get(worn)) + 1
    data["equipment"] = equipment
    data["inventory"] = inventory
    return data


# ---------------------------------------------------------------------------
# Purchase
# ---------------------------------------------------------------------------


def _grant(data: dict[str, Any], names: Sequence[str], price: int) -> dict[str, Any]:
    inventory = dict(_mapping(data.get("inventory")))
    inventory["Coins"] = _int(inventory.get("Coins")) - price
    for name in names:
        inventory[name] = _int(inventory.get(name)) + 1
    data["inventory"] = inventory
    return data


def _replace_owned_item(data: dict[str, Any], old: str, new: str) -> dict[str, Any]:
    inventory = dict(_mapping(data.get("inventory")))
    equipment = dict(_mapping(data.get("equipment")))
    held = _int(inventory.get(old))
    if held:
        if held == 1:
            inventory.pop(old, None)
        else:
            inventory[old] = held - 1
        inventory[new] = _int(inventory.get(new)) + 1
    else:
        slot = next((slot for slot, worn in equipment.items() if worn == old), "")
        if slot:
            equipment[slot] = new
    data["inventory"] = inventory
    data["equipment"] = equipment
    return data


def purchase_cape_pure(
    player_data: Mapping[str, Any], cape_id: str
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    """Buy one cape from its period seller. Skill id or prestige id, one space."""

    data = refresh_capes_pure(player_data)
    skillcape = next(
        (cape for cape in skillcape_definitions() if cape.skill_id == cape_id), None
    )
    if skillcape is not None:
        return _purchase_skillcape(data, skillcape)
    master_cape = MASTER_CAPES_BY_ID.get(cape_id)
    if master_cape is not None and master_cape in master_cape_definitions():
        return _purchase_master_cape(data, master_cape)
    prestige = PRESTIGE_CAPES_BY_ID.get(cape_id)
    if prestige is None:
        return data, False, {"reason": "Unknown cape."}

    owned = _owned_names(data)
    if prestige.cape in owned:
        return data, False, {"reason": f"You already own the {prestige.cape}."}
    if prestige.upgrade_from and prestige.upgrade_from not in owned:
        return data, False, {"reason": f"Own the {prestige.upgrade_from} first."}
    eligible, reason = prestige_cape_eligible_pure(data, cape_id)
    if not eligible:
        return data, False, {"reason": reason}
    if prestige.upgrade_from:
        data = _replace_owned_item(data, prestige.upgrade_from, prestige.cape)
        return (
            data,
            True,
            {
                "message": f"{prestige.seller} upgrades the cape to {prestige.cape}.",
                "item": prestige.cape,
            },
        )
    if _int(_mapping(data.get("inventory")).get("Coins")) < prestige.price:
        return data, False, {"reason": f"Requires {prestige.price:,} coins."}
    data = _grant(data, (prestige.cape, prestige.hood), prestige.price)
    return (
        data,
        True,
        {
            "message": f"{prestige.seller} hands over the {prestige.cape}.",
            "item": prestige.cape,
        },
    )


def _purchase_master_cape(
    data: dict[str, Any], cape: MasterCape
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    if cape.cape in _owned_names(data):
        return data, False, {"reason": f"You already own the {cape.cape}."}
    if _int(data.get(f"{cape.skill_id}_level", 1), 1) < cape.level:
        return data, False, {"reason": f"Requires level {cape.level} Dungeoneering"}
    if _int(_mapping(data.get("inventory")).get("Coins")) < cape.price:
        return data, False, {"reason": f"Requires {cape.price:,} coins"}
    data = _grant(data, (cape.cape,), cape.price)
    return (
        data,
        True,
        {"message": f"{cape.master} hands over the {cape.cape}.", "item": cape.cape},
    )


def _purchase_skillcape(
    data: dict[str, Any], cape: Skillcape
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    owned = _owned_names(data)
    if owned & {cape.cape, cape.trimmed_cape}:
        return data, False, {"reason": f"You already own the {cape.cape}."}
    if _int(data.get(f"{cape.skill_id}_level", 1), 1) < SKILLCAPE_LEVEL:
        return data, False, {"reason": f"Requires level {SKILLCAPE_LEVEL} {cape.skill_label}"}
    if _int(_mapping(data.get("inventory")).get("Coins")) < SKILLCAPE_PRICE:
        return data, False, {"reason": f"Requires {SKILLCAPE_PRICE:,} coins"}
    granted = cape.trimmed_cape if skillcapes_are_trimmed_pure(data) else cape.cape
    data = _grant(data, (granted, cape.hood), SKILLCAPE_PRICE)
    return (
        data,
        True,
        {"message": f"{cape.master} hands over the {granted} and hood.", "item": granted},
    )


# ---------------------------------------------------------------------------
# View
# ---------------------------------------------------------------------------


def cape_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    """Every cape row the Cabinet and the shop render, with every enable flag."""

    state = _state(player_data)
    owned = _owned_names(player_data)
    trimmed = skillcapes_are_trimmed_pure(player_data)
    coins = _int(_mapping(player_data.get("inventory")).get("Coins"))

    skillcapes: list[dict[str, Any]] = []
    for cape in skillcape_definitions():
        level = _int(player_data.get(f"{cape.skill_id}_level", 1), 1)
        held = bool(owned & {cape.cape, cape.trimmed_cape})
        eligible = level >= SKILLCAPE_LEVEL
        if held:
            reason = "Owned"
        elif not eligible:
            reason = f"Level {SKILLCAPE_LEVEL} needed ({level} now)"
        elif coins < SKILLCAPE_PRICE:
            reason = f"{SKILLCAPE_PRICE:,} coins needed"
        else:
            reason = ""
        skillcapes.append(
            {
                "cape_id": cape.skill_id,
                "name": cape.trimmed_cape if trimmed else cape.cape,
                "hood": cape.hood,
                "master": cape.master,
                "price": SKILLCAPE_PRICE,
                "level": level,
                "owned": held,
                "can_buy": eligible and not held and coins >= SKILLCAPE_PRICE,
                # 24 masters would be 24 dead buttons at level 1. The shop shows
                # a cape once the player could conceivably want it; the Cabinet
                # always lists all of them with their progress.
                "show_in_shop": eligible or held,
                "reason": reason,
                "keepsake": cape.skill_id == state["keepsake_skill"],
            }
        )

    master_capes: list[dict[str, Any]] = []
    for cape in master_cape_definitions():
        level = _int(player_data.get(f"{cape.skill_id}_level", 1), 1)
        held = cape.cape in owned
        eligible = level >= cape.level
        if held:
            reason = "Owned"
        elif not eligible:
            reason = f"Level {cape.level} needed ({level} now)"
        elif coins < cape.price:
            reason = f"{cape.price:,} coins needed"
        else:
            reason = ""
        master_capes.append(
            {
                "cape_id": cape.id,
                "name": cape.cape,
                "hood": "",
                "master": cape.master,
                "price": cape.price,
                "owned": held,
                "can_buy": eligible and not held and coins >= cape.price,
                "show_in_shop": eligible or held,
                "reason": reason,
                "purchase_label": "Buy",
            }
        )

    distinctions: list[dict[str, Any]] = []
    for cape in PRESTIGE_CAPES:
        held = cape.cape in owned
        eligible, reason = prestige_cape_eligible_pure(player_data, cape.id)
        owns_source = not cape.upgrade_from or cape.upgrade_from in owned
        if held:
            reason = "Owned"
        elif cape.upgrade_from and not owns_source:
            reason = f"Own the {cape.upgrade_from} first"
        elif eligible and coins < cape.price:
            reason = f"{cape.price:,} coins needed"
        distinctions.append(
            {
                "cape_id": cape.id,
                "name": cape.cape,
                "hood": cape.hood,
                "master": cape.seller,
                "price": cape.price,
                "owned": held,
                "can_buy": eligible and owns_source and not held and coins >= cape.price,
                "reason": reason,
                "purchase_label": cape.purchase_label,
            }
        )

    return {
        "skillcapes": tuple(skillcapes),
        "master_capes": tuple(master_capes),
        "distinctions": tuple(distinctions),
        "trimmed": trimmed,
        "keepsake_skill": state["keepsake_skill"],
        "keepsake_cape": next(
            (
                cape.cape
                for cape in skillcape_definitions()
                if cape.skill_id == state["keepsake_skill"]
            ),
            "",
        ),
        "completionist": completionist_requirements_pure(player_data),
        "trimmed_completionist": trimmed_completionist_requirements_pure(player_data),
        "latent_skills": latent_cutoff_skills_pure(),
    }
