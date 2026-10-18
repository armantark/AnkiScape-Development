"""Live cadence declarations and route admission.

The coverage catalog is intentionally data-driven: every selectable foreground
route must appear here, even when its shipped behavior remains passthrough or is
honestly source-blocked.  Runtime admission uses only exact rational rates and
never imports observational shadow residuals.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any, Mapping

from .cadence_kernel import (
    CAP_ONE_ACTION,
    COMBAT_TICKS,
    EMBEDDED_PROBABILITY,
    PASSTHROUGH,
    RATE_LIMITED,
    CadenceProfile,
    advance_cadence_pure,
    default_cadence_profile_state_pure,
    rate_limited_profile_pure,
)
from .cadence_shadow import SOURCE_BLOCKED, SOURCE_READY, resolve_cadence_shadow_rate_pure
from ..tools.sourced_xp_rates import DETERMINISTIC


LIVE_CADENCE_VERSION = 1
LIVE_COMBAT_TICKS_PER_REVIEW = 6
LIVE_RANGE_POLICY = "lower_source_endpoint"

_SHADOW_SKILLS = frozenset(
    {"mining", "woodcutting", "fishing", "hunter", "cooking", "firemaking"}
)
_EMBEDDED_SKILLS = frozenset({"cooking", "firemaking"})
_EXACT_BATTLESTAFF_TARGET = "battlestaff_water_battlestaff"
_RUNTIME_XP_INCOMPATIBLE_ROUTES = {
    (
        "fishing",
        "catch_trout_salmon",
    ): "the sourced 58-XP catch is a trout/salmon blend, while forced live admission does not yet preserve that output mixture",
    (
        "hunter",
        "catch_chinchompa",
    ): "the source row awards 198 Hunter XP, but the runtime action awards 198.5",
    (
        "hunter",
        "catch_black_salamander",
    ): "the source row awards 304 Hunter XP, but the runtime action awards 319.2",
    (
        "hunter",
        "catch_spotted_kebbit",
    ): "the source row awards 104 Hunter XP, but the runtime action awards 42",
    (
        "hunter",
        "catch_dark_kebbit",
    ): "the source row awards 132 Hunter XP, but the runtime action awards 99",
}


@dataclass(frozen=True)
class CadenceRouteDeclaration:
    handler_key: str
    action_id: str
    mode: str
    source_status: str
    source_row: str
    source_reason: str
    includes: tuple[str, ...]
    multiplier_behavior: str
    undo_boundary: str
    flag_off_behavior: str
    profile: CadenceProfile | None = None
    condition: str = ""


def _rate_fraction(row_key: str) -> Fraction:
    rate = DETERMINISTIC[row_key]
    return Fraction(rate.low_xp_hr, 1) / Fraction(str(rate.xp_per_action))


def _rate_profile(profile_id: str, actions_per_hour: Fraction) -> CadenceProfile:
    overflow = CAP_ONE_ACTION if actions_per_hour > 1000 else None
    return rate_limited_profile_pure(
        profile_id,
        actions_per_hour.numerator,
        actions_per_hour.denominator,
        overflow_policy=overflow,
    )


def _equipment_names(player_data: Mapping[str, Any] | None) -> frozenset[str]:
    equipment = (player_data or {}).get("equipment", {})
    if not isinstance(equipment, Mapping):
        return frozenset()
    return frozenset(str(item) for item in equipment.values() if isinstance(item, str))


def _uses_fire_staff(player_data: Mapping[str, Any] | None) -> bool:
    return any("fire staff" in item.lower() or "staff of fire" in item.lower() for item in _equipment_names(player_data))


# Handlers the dispatcher calls once per card instead of once per six-tick step.
_ONE_PER_CARD_BEHAVIOR = {
    "agility": "one established Agility stage; never foreground-multiplied",
    "dungeoneering": "one room per card at every speed; a declared divergence",
    "quest": "one stage per card at every speed; a declared divergence",
}


def resolve_live_cadence_route_pure(
    handler_key: str,
    action_id: str,
    player_data: Mapping[str, Any] | None = None,
) -> CadenceRouteDeclaration:
    """Resolve one foreground route without mutating player state."""

    skill_id = str(handler_key or "").lower()
    target_id = str(action_id or "")
    profile_id = f"{skill_id}:{target_id}"
    common = {
        "handler_key": skill_id,
        "action_id": target_id,
        "multiplier_behavior": "M six-tick steps of the card's budget",
        "undo_boundary": "one answered-card transaction",
        "flag_off_behavior": "legacy handler and RNG order",
    }

    if skill_id == "combat":
        return CadenceRouteDeclaration(
            **{**common, "multiplier_behavior": "the card's whole 6 * M tick budget in one call"},
            mode=COMBAT_TICKS,
            source_status=SOURCE_READY,
            source_row="cadence-kernel R=1000 / 6 ticks",
            source_reason="",
            includes=("attack scheduling", "combat status clocks"),
            profile=CadenceProfile(profile_id, COMBAT_TICKS),
        )

    if skill_id == "thieving":
        return CadenceRouteDeclaration(
            **{
                **common,
                "multiplier_behavior": "one established Thieving canary step; never foreground-multiplied",
            },
            mode=PASSTHROUGH,
            source_status=SOURCE_READY,
            source_row="existing Thieving canary",
            source_reason="stall and wall-safe targets retain their own exact scheduler",
            includes=("target-specific respawn",),
            condition="no second live-kernel gate",
        )

    if skill_id == "cooking" and target_id in {
        "churn_milk_cheese_wheel",
        "churn_butter_cheese_wheel",
    }:
        actions_per_hour = Fraction(750, 1)
        return CadenceRouteDeclaration(
            **common,
            mode=RATE_LIMITED,
            source_status=SOURCE_READY,
            source_row="Dairy churn oldid 6474695: 8 game ticks per dairy item",
            source_reason=(
                "lower_source_endpoint equals the exact eight-tick source "
                "endpoint: 750 actions/hour"
            ),
            includes=("dairy-churn action time only",),
            profile=_rate_profile(profile_id, actions_per_hour),
        )

    if skill_id in _SHADOW_SKILLS:
        resolved = resolve_cadence_shadow_rate_pure(skill_id, target_id)
        if resolved["source_status"] != SOURCE_READY:
            return CadenceRouteDeclaration(
                **common,
                mode=SOURCE_BLOCKED,
                source_status=SOURCE_BLOCKED,
                source_row=str(resolved.get("source_key", "")),
                source_reason=str(resolved.get("source_blocked_reason", "no compatible pre-cutoff XP/hour rate")),
                includes=tuple(str(value) for value in resolved.get("source_includes", ())),
            )
        incompatible_reason = _RUNTIME_XP_INCOMPATIBLE_ROUTES.get(
            (skill_id, target_id)
        )
        if incompatible_reason:
            return CadenceRouteDeclaration(
                **common,
                mode=SOURCE_BLOCKED,
                source_status=SOURCE_BLOCKED,
                source_row=str(resolved.get("source_key", profile_id)),
                source_reason=incompatible_reason,
                includes=tuple(
                    str(value)
                    for value in resolved.get("source_includes", ())
                ),
            )
        if skill_id in _EMBEDDED_SKILLS:
            return CadenceRouteDeclaration(
                **common,
                mode=EMBEDDED_PROBABILITY,
                source_status=SOURCE_READY,
                source_row=str(resolved.get("source_key", profile_id)),
                source_reason="",
                includes=tuple(str(value) for value in resolved.get("source_includes", ())),
                profile=CadenceProfile(profile_id, EMBEDDED_PROBABILITY),
            )
        if "dropping" in resolved.get("source_includes", ()):
            keep_drop = (player_data or {}).get("carried_keep_drop", {})
            keep = not isinstance(keep_drop, Mapping) or keep_drop.get(target_id, "keep") != "drop"
            if keep:
                return CadenceRouteDeclaration(
                    **common,
                    mode=SOURCE_BLOCKED,
                    source_status=SOURCE_BLOCKED,
                    source_row=str(resolved.get("source_key", profile_id)),
                    source_reason="the sourced rate includes dropping, but this route is configured to keep and bank outputs",
                    includes=tuple(str(value) for value in resolved.get("source_includes", ())),
                    condition="live rate applies in Drop mode",
                )
        low_rate = Fraction(*resolved["low_actions_per_hour"])
        source_includes = tuple(
            str(value) for value in resolved.get("source_includes", ())
        )
        if (skill_id, target_id) == ("hunter", "barehand_black_warlock"):
            source_includes += ("attached 125 Agility XP",)
        return CadenceRouteDeclaration(
            **common,
            mode=RATE_LIMITED,
            source_status=SOURCE_READY,
            source_row=str(resolved.get("source_key", profile_id)),
            source_reason=f"ranged evidence uses the exact {LIVE_RANGE_POLICY}",
            includes=source_includes,
            condition="Drop mode" if "dropping" in resolved.get("source_includes", ()) else "",
            profile=_rate_profile(profile_id, low_rate),
        )

    deterministic_key = ""
    condition = ""
    if skill_id == "magic" and target_id == "high_alchemy":
        deterministic_key = "magic/high_alchemy"
        condition = "equipped fire staff"
    elif skill_id == "magic" and target_id == "superheat_mithril_bar":
        deterministic_key = "magic/superheat_mithril"
        condition = "equipped fire staff"
    elif skill_id == "crafting" and target_id == "leather_green_dhide_body":
        deterministic_key = "crafting/dragonhide_body"
    elif skill_id == "crafting" and target_id == _EXACT_BATTLESTAFF_TARGET:
        deterministic_key = "crafting/battlestaves"
    elif skill_id == "prayer" and target_id == "gilded_altar_dragon_bones":
        deterministic_key = "prayer/gilded_altar_dragon_bones"

    if deterministic_key:
        rate = DETERMINISTIC[deterministic_key]
        if condition and not _uses_fire_staff(player_data):
            return CadenceRouteDeclaration(
                **common,
                mode=SOURCE_BLOCKED,
                source_status=SOURCE_BLOCKED,
                source_row=deterministic_key,
                source_reason=f"the exact source row includes {condition}",
                includes=tuple(rate.includes),
                condition=condition,
            )
        actions_per_hour = _rate_fraction(deterministic_key)
        return CadenceRouteDeclaration(
            **common,
            mode=RATE_LIMITED,
            source_status=SOURCE_READY,
            source_row=deterministic_key,
            source_reason="",
            includes=tuple(rate.includes),
            condition=condition,
            profile=_rate_profile(profile_id, actions_per_hour),
        )

    if skill_id == "crafting" and target_id.startswith(("form_", "fire_")) and "urn" in target_id:
        return CadenceRouteDeclaration(
            **common,
            mode=SOURCE_BLOCKED,
            source_status=SOURCE_BLOCKED,
            source_row="crafting/urns_ardougne",
            source_reason="the 95-XP full urn cycle is incompatible with the live split forming/firing action units",
            includes=(),
        )

    fallback_common = {
        **common,
        "multiplier_behavior": _ONE_PER_CARD_BEHAVIOR.get(
            skill_id, common["multiplier_behavior"]
        ),
    }
    return CadenceRouteDeclaration(
        **fallback_common,
        mode=PASSTHROUGH,
        source_status=SOURCE_BLOCKED,
        source_row="",
        source_reason="one review is the approved discrete action unit; no compatible period XP/hour row",
        includes=(),
    )


def advance_live_cadence_route_pure(
    player_data: dict[str, Any],
    handler_key: str,
    action_id: str,
) -> tuple[CadenceRouteDeclaration, bool]:
    """Advance a live rate-limited route, returning whether it may act."""

    declaration = resolve_live_cadence_route_pure(handler_key, action_id, player_data)
    if declaration.mode != RATE_LIMITED or declaration.profile is None:
        return declaration, True
    profiles = dict(player_data.get("cadence_profiles", {}) or {})
    profile = declaration.profile
    step = advance_cadence_pure(
        profile,
        profiles.get(profile.profile_id, default_cadence_profile_state_pure()),
    )
    profiles[profile.profile_id] = step.state
    player_data["cadence_profiles"] = profiles
    return declaration, step.emitted


def cadence_declaration_dict_pure(declaration: CadenceRouteDeclaration) -> dict[str, Any]:
    row = asdict(declaration)
    profile = declaration.profile
    row["profile"] = asdict(profile) if profile is not None else None
    return row
