"""Auditable whole-addon cadence coverage catalog."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Mapping

try:
    from .agility_data import AGILITY_TARGETS_BY_ID
    from .cadence_live import cadence_declaration_dict_pure, resolve_live_cadence_route_pure
    from .constants import (
        COMBAT_ENEMY_DATA,
        COOKING_DATA,
        CRAFTING_DATA,
        FIREMAKING_DATA,
        FISHING_DATA,
        FLETCHING_DATA,
        HERBLORE_DATA,
        HUNTER_DATA,
        MAGIC_DATA,
        ORE_DATA,
        PRAYER_DATA,
        QUEST_DATA,
        RUNECRAFTING_DATA,
        SMITHING_DATA,
        TREE_DATA,
        UTILITY_ACTIVITY_DATA,
    )
    from .construction_data import CONSTRUCTION_DATA
    from .summoning_data import SUMMONING_ACTIONS_BY_ID
    from .thieving_data import THIEVING_TARGETS
except ImportError:  # pragma: no cover - flat imports used by tests/tools
    from agility_data import AGILITY_TARGETS_BY_ID  # type: ignore
    from cadence_live import cadence_declaration_dict_pure, resolve_live_cadence_route_pure  # type: ignore
    from constants import (  # type: ignore
        COMBAT_ENEMY_DATA,
        COOKING_DATA,
        CRAFTING_DATA,
        FIREMAKING_DATA,
        FISHING_DATA,
        FLETCHING_DATA,
        HERBLORE_DATA,
        HUNTER_DATA,
        MAGIC_DATA,
        ORE_DATA,
        PRAYER_DATA,
        QUEST_DATA,
        RUNECRAFTING_DATA,
        SMITHING_DATA,
        TREE_DATA,
        UTILITY_ACTIVITY_DATA,
    )
    from construction_data import CONSTRUCTION_DATA  # type: ignore
    from summoning_data import SUMMONING_ACTIONS_BY_ID  # type: ignore
    from thieving_data import THIEVING_TARGETS  # type: ignore


FOREGROUND_ROUTE_TABLES: dict[str, Mapping[str, Any]] = {
    "mining": ORE_DATA,
    "woodcutting": TREE_DATA,
    "smithing": SMITHING_DATA,
    "crafting": CRAFTING_DATA,
    "fletching": FLETCHING_DATA,
    "firemaking": FIREMAKING_DATA,
    "fishing": FISHING_DATA,
    "hunter": HUNTER_DATA,
    "cooking": COOKING_DATA,
    "runecrafting": RUNECRAFTING_DATA,
    "herblore": HERBLORE_DATA,
    "prayer": PRAYER_DATA,
    "magic": MAGIC_DATA,
    "construction": CONSTRUCTION_DATA,
    "thieving": THIEVING_TARGETS,
    "agility": AGILITY_TARGETS_BY_ID,
    "summoning": SUMMONING_ACTIONS_BY_ID,
    "combat": COMBAT_ENEMY_DATA,
}

CADENCE_DECLARED_HANDLER_KEYS = frozenset(
    {*FOREGROUND_ROUTE_TABLES, "utility", "quest"}
)


def _catalog_player_data() -> dict[str, Any]:
    target_ids = {
        str(target_id)
        for table in FOREGROUND_ROUTE_TABLES.values()
        for target_id in table
    }
    return {
        "equipment": {"weapon": "Fire staff"},
        "carried_keep_drop": {target_id: "drop" for target_id in target_ids},
    }


def cadence_coverage_rows_pure() -> list[dict[str, Any]]:
    """Return one declaration for every selectable route plus explicit exemptions."""

    player_data = _catalog_player_data()
    rows: list[dict[str, Any]] = []
    for handler_key, table in FOREGROUND_ROUTE_TABLES.items():
        for action_id in table:
            row = cadence_declaration_dict_pure(
                resolve_live_cadence_route_pure(handler_key, str(action_id), player_data)
            )
            row["route_kind"] = "foreground"
            rows.append(row)

    for action_id, spec in UTILITY_ACTIVITY_DATA.items():
        if str(action_id) == "fist_of_guthix":
            rows.append(
                {
                    "handler_key": "utility",
                    "action_id": "fist_of_guthix",
                    "mode": "activity_group",
                    "source_status": "sourced",
                    "source_row": str(spec.get("source", "")),
                    "source_reason": (
                        "One review advances exactly six Combat ticks and stops "
                        "at a kill, death, charge cap, or round boundary."
                    ),
                    "includes": (
                        "six combat ticks",
                        "one hunted-charge residual boundary",
                        "one safe arena-state transaction",
                    ),
                    "multiplier_behavior": (
                        "Never foreground-multiplied; one answered card remains "
                        "one six-tick arena interval"
                    ),
                    "undo_boundary": "one answered-card transaction",
                    "flag_off_behavior": "same six-tick activity handler",
                    "profile": None,
                    "condition": "",
                    "route_kind": "activity",
                }
            )
            continue
        elif str(action_id) == "fight_caves":
            rows.append(
                {
                    "handler_key": "utility",
                    "action_id": "fight_caves",
                    "mode": "activity_group",
                    "source_status": "sourced",
                    "source_row": str(spec.get("source", "")),
                    "source_reason": (
                        "One review advances exactly six live Combat ticks against "
                        "the engaged roster target, then resolves bounded pressure."
                    ),
                    "includes": (
                        "one engaged six-tick Combat slice",
                        "one unengaged-roster pressure boundary",
                        "one atomic wave-state transaction",
                    ),
                    "multiplier_behavior": (
                        "Never foreground-multiplied; one answered card remains "
                        "one six-tick Fight Cave interval"
                    ),
                    "undo_boundary": "one answered-card transaction",
                    "flag_off_behavior": "same six-tick activity handler",
                    "profile": None,
                    "condition": "",
                    "route_kind": "activity",
                }
            )
            continue
        elif str(action_id) == "phoenix_lair":
            rows.append(
                {
                    "handler_key": "utility",
                    "action_id": "phoenix_lair",
                    "mode": "activity_group",
                    "source_status": "bounded_abstraction",
                    "source_row": str(spec.get("source", "")),
                    "source_reason": (
                        "One review advances six live Combat ticks in either the "
                        "aggregate guardian front or Phoenix encounter; preparation "
                        "is one finite grouped review."
                    ),
                    "includes": (
                        "one six-tick Combat slice or one pyre-preparation beat",
                        "one persistent activity-state transaction",
                        "one atomic completion and daily-charge boundary",
                    ),
                    "multiplier_behavior": (
                        "Never foreground-multiplied; one answered card remains "
                        "one Phoenix Lair interval"
                    ),
                    "undo_boundary": "one answered-card transaction",
                    "flag_off_behavior": "same six-tick activity handler",
                    "profile": None,
                    "condition": "",
                    "route_kind": "activity",
                }
            )
            continue
        elif str(action_id) == "shooting_stars":
            rows.append(
                {
                    "handler_key": "utility",
                    "action_id": "shooting_stars",
                    "mode": "activity_group",
                    "source_status": "sourced",
                    "source_row": str(spec.get("source", "")),
                    "source_reason": (
                        "One successful review is one visible Mining attempt; "
                        "the shared answered-card clock advances the public crowd."
                    ),
                    "includes": (
                        "one stardust attempt",
                        "one public-crowd boundary",
                    ),
                    "multiplier_behavior": (
                        "Never foreground-multiplied; each answered card "
                        "preserves one communal depletion boundary"
                    ),
                    "undo_boundary": "one answered-card transaction",
                    "flag_off_behavior": "same single-attempt activity handler",
                    "profile": None,
                    "condition": "",
                    "route_kind": "activity",
                }
            )
            continue
        elif str(action_id) == "sorceress_garden":
            rows.append(
                {
                    "handler_key": "utility",
                    "action_id": "sorceress_garden",
                    "mode": "passthrough",
                    "source_status": "sourced",
                    "source_row": str(spec.get("source", "")),
                    "source_reason": (
                        "One successful review is one complete seasonal garden "
                        "attempt and harvest; Again owns the caught outcome."
                    ),
                    "includes": ("one seasonal route", "one harvest"),
                    "multiplier_behavior": (
                        "Never foreground-multiplied; one answered card remains "
                        "one complete garden attempt"
                    ),
                    "undo_boundary": "one answered-card transaction",
                    "flag_off_behavior": "same single-attempt activity handler",
                    "profile": None,
                    "condition": "",
                    "route_kind": "activity",
                }
            )
            continue
        elif str(action_id) == "flash_powder_factory":
            rows.append(
                {
                    "handler_key": "utility",
                    "action_id": "flash_powder_factory",
                    "mode": "activity_group",
                    "source_status": "sourced",
                    "source_row": str(spec.get("source", "")),
                    "source_reason": (
                        "One review resolves one complete reagent, catalyst, route, "
                        "and mixer production circuit inside the finite factory session."
                    ),
                    "includes": (
                        "one production circuit",
                        "one bounded obstacle and public-floor boundary",
                    ),
                    "multiplier_behavior": (
                        "Never foreground-multiplied; one answered card remains "
                        "one consequential factory circuit"
                    ),
                    "undo_boundary": "one answered-card transaction",
                    "flag_off_behavior": "same single-circuit activity handler",
                    "profile": None,
                    "condition": "",
                    "route_kind": "activity",
                }
            )
            continue
        elif str(action_id) == "pyramid_plunder":
            rows.append(
                {
                    "handler_key": "utility",
                    "action_id": "pyramid_plunder",
                    "mode": "activity_group",
                    "source_status": "sourced_with_fallbacks",
                    "source_row": str(spec.get("source", "")),
                    "source_reason": (
                        "One successful review resolves one complete room bundle. "
                        "Published room XP and Darkan object curves are pinned; hidden "
                        "hazard trigger rates use disclosed bounded abstractions."
                    ),
                    "includes": (
                        "one room's selected chest, urn, and sarcophagus policy",
                        "hazards, carried-pack pressure, banking, and terminal exits",
                    ),
                    "multiplier_behavior": (
                        "Foreground multiplier resolves up to M rooms and stops at the "
                        "first death, full-pack exit, sceptre expulsion, or completed run"
                    ),
                    "undo_boundary": "one answered-card transaction",
                    "flag_off_behavior": "same bounded room-resolution handler",
                    "profile": None,
                    "condition": "",
                    "route_kind": "activity",
                }
            )
            continue
        elif str(action_id) == "werewolf_skullball":
            rows.append(
                {
                    "handler_key": "utility",
                    "action_id": "werewolf_skullball",
                    "mode": "activity_group",
                    "source_status": "sourced_with_disclosed_translation",
                    "source_row": str(spec.get("source", "")),
                    "source_reason": (
                        "One successful review resolves one complete sourced ten-goal "
                        "route. Custom route length translates the sourced post-four-minute "
                        "XP decay without simulating wall-clock time."
                    ),
                    "includes": (
                        "one ten-goal Tap, Kick, and Shoot route",
                        "one terminal Agility XP award",
                    ),
                    "multiplier_behavior": (
                        "Never foreground-multiplied; one answered card completes exactly "
                        "one run and cannot begin a second run"
                    ),
                    "undo_boundary": "one answered-card transaction",
                    "flag_off_behavior": "same atomic ten-goal run handler",
                    "profile": None,
                    "condition": "",
                    "route_kind": "activity",
                }
            )
            continue
        elif str(action_id) == "gnome_ball":
            rows.append(
                {
                    "handler_key": "utility",
                    "action_id": "gnome_ball",
                    "mode": "source_blocked_activity",
                    "source_status": "source_blocked",
                    "source_row": str(spec.get("source", "")),
                    "source_reason": (
                        "One successful review resolves one of three settled match beats. "
                        "Period goal XP is pinned; the hidden tackle rate uses the "
                        "owner-approved bounded Agility fallback."
                    ),
                    "includes": (
                        "one grouped match beat covering one or two goals",
                        "one optional dangerous tackle and the beat's fixed XP",
                    ),
                    "multiplier_behavior": (
                        "M match beats, stopping at death or the terminal fifth goal; "
                        "the same answer cannot begin a second match"
                    ),
                    "undo_boundary": "one answered-card transaction",
                    "flag_off_behavior": "same three-beat match handler",
                    "profile": None,
                    "condition": "owner-approved bounded hidden-roll abstraction",
                    "route_kind": "activity",
                }
            )
            continue
        elif str(action_id) == "fish_flingers":
            rows.append(
                {
                    "handler_key": "utility",
                    "action_id": "fish_flingers",
                    "mode": "source_blocked_activity",
                    "source_status": "sourced_with_disclosed_translation",
                    "source_row": str(spec.get("source", "")),
                    "source_reason": (
                        "One successful review resolves one productive catch in the "
                        "settled six-review event. The three-step tackle ramp and event "
                        "XP curve are disclosed pacing translations of the source event."
                    ),
                    "includes": (
                        "one productive catch and automatic communal pressure",
                        "one terminal XP, token, and medal payout after six catches",
                    ),
                    "multiplier_behavior": (
                        "M catches within the current event, stopping after its sixth; "
                        "the same answer cannot begin another event"
                    ),
                    "undo_boundary": "one answered-card transaction",
                    "flag_off_behavior": "same six-catch event handler",
                    "profile": None,
                    "condition": "disclosed finite-event and XP translations",
                    "route_kind": "activity",
                }
            )
            continue
        elif str(action_id) == "fishing_trawler":
            rows.append(
                {
                    "handler_key": "utility",
                    "action_id": "fishing_trawler",
                    "mode": "source_blocked_activity",
                    "source_status": "sourced_with_disclosed_translation",
                    "source_row": str(spec.get("source", "")),
                    "source_reason": (
                        "One successful review resolves one useful duty and one "
                        "pressure event in the owner-settled ten-review trip. The "
                        "source twelve-minute presentation is intentionally not "
                        "mapped to wall-clock time."
                    ),
                    "includes": (
                        "one player duty plus the fixed public-crew pressure offset",
                        "one terminal banked haul or sinking loss after ten events",
                    ),
                    "multiplier_behavior": (
                        "M duties within the current trip, stopping at sinking or "
                        "the tenth event; the same answer cannot board another trip"
                    ),
                    "undo_boundary": "one answered-card transaction",
                    "flag_off_behavior": "same ten-event trip handler",
                    "profile": None,
                    "condition": "disclosed event-count and pressure compression",
                    "route_kind": "activity",
                }
            )
            continue
        elif str(action_id) == "great_orb_project":
            rows.append(
                {
                    "handler_key": "utility",
                    "action_id": "great_orb_project",
                    "mode": "source_blocked_activity",
                    "source_status": "sourced_with_disclosed_translation",
                    "source_row": str(spec.get("source", "")),
                    "source_reason": (
                        "One successful review resolves one complete altar round: "
                        "one orb/barrier duty beat, one bounded opposing-team score, "
                        "and the round's essence decision. Source wall-clock round "
                        "lengths are intentionally not gameplay inputs."
                    ),
                    "includes": (
                        "one altar-score race and participation check",
                        "one temporary-essence craft/save decision and terminal payout",
                    ),
                    "multiplier_behavior": (
                        "M sequential altar rounds, stopping after the eighth; the "
                        "same answer cannot begin another match"
                    ),
                    "undo_boundary": "one answered-card transaction",
                    "flag_off_behavior": "same eight-round activity handler",
                    "profile": None,
                    "condition": "owner-settled bounded-opponent and event-count translation",
                    "route_kind": "activity",
                }
            )
            continue
        elif str(action_id) == "managing_miscellania":
            rows.append(
                {
                    "handler_key": "utility",
                    "action_id": "managing_miscellania",
                    "mode": "passthrough",
                    "source_status": "sourced_with_disclosed_translation",
                    "source_row": str(spec.get("source", "")),
                    "source_reason": (
                        "Foreground reviews perform one exact approval chore. "
                        "Kingdom salary and production advance once per 240 answered "
                        "cards from the shared review clock, never wall time."
                    ),
                    "includes": (
                        "one Maple approval chore and its Woodcutting XP",
                        "one answered-card transaction while selected",
                    ),
                    "multiplier_behavior": (
                        "Never foreground-multiplied; passive kingdom days are owned "
                        "by the answered-card world clock"
                    ),
                    "undo_boundary": "one answered-card transaction",
                    "flag_off_behavior": "same approval-work handler",
                    "profile": None,
                    "condition": "review-day translation disclosed in the activity contract",
                    "route_kind": "activity",
                }
            )
            continue
        elif str(action_id) == "court_cases":
            rows.append(
                {
                    "handler_key": "utility",
                    "action_id": "court_cases",
                    "mode": "activity_group",
                    "source_status": "sourced",
                    "source_row": str(spec.get("source", "")),
                    "source_reason": (
                        "One review resolves one preparation or courtroom beat. "
                        "The verdict boundary stops the session on success or "
                        "returns the retained case files to trial beat one."
                    ),
                    "includes": (
                        "one case-report, fingerprint, evidence, witness, or jury beat",
                        "one atomic retry or reward boundary",
                    ),
                    "multiplier_behavior": (
                        "Never foreground-multiplied; one answered card remains "
                        "one consequential court beat"
                    ),
                    "undo_boundary": "one answered-card transaction",
                    "flag_off_behavior": "same one-beat court handler",
                    "profile": None,
                    "condition": "",
                    "route_kind": "activity",
                }
            )
            continue
        elif str(action_id) == "big_top_bonanza":
            rows.append(
                {
                    "handler_key": "utility",
                    "action_id": "big_top_bonanza",
                    "mode": "activity_group",
                    "source_status": "sourced_with_disclosed_translation",
                    "source_row": str(spec.get("source", "")),
                    "source_reason": (
                        "One successful review resolves one complete skill "
                        "performance: ten Magic, Ranged, Agility, or Thieving "
                        "attempts, or six Firemaking attempts. The hidden trick "
                        "success and audience-score curves are isolated bounded "
                        "translations over period-pinned tables."
                    ),
                    "includes": (
                        "one complete per-skill Circus performance and weekly lock",
                        "one atomic XP, audience-score, and costume-reward boundary",
                    ),
                    "multiplier_behavior": (
                        "Never foreground-multiplied; the same answer cannot begin "
                        "a second performance"
                    ),
                    "undo_boundary": "one answered-card transaction",
                    "flag_off_behavior": "same atomic whole-performance handler",
                    "profile": None,
                    "condition": "disclosed hidden-roll and score abstractions",
                    "route_kind": "activity",
                }
            )
            continue
        elif str(action_id) == "trouble_brewing":
            rows.append(
                {
                    "handler_key": "utility",
                    "action_id": "trouble_brewing",
                    "mode": "activity_group",
                    "source_status": "sourced_with_disclosed_translation",
                    "source_row": str(spec.get("source", "")),
                    "source_reason": (
                        "One review advances one of sixteen disclosed duty beats, "
                        "plus one opposing-team pressure step. Source wall-clock "
                        "duration is intentionally not a gameplay input."
                    ),
                    "includes": (
                        "one productive duty or explicit Again idle beat",
                        "one terminal rum score, multi-skill XP, and currency payout",
                    ),
                    "multiplier_behavior": (
                        "Never foreground-multiplied; one answered card remains "
                        "one race beat and cannot begin a second match"
                    ),
                    "undo_boundary": "one answered-card transaction",
                    "flag_off_behavior": "same sixteen-beat race handler",
                    "profile": None,
                    "condition": "owner-settled event-count translation",
                    "route_kind": "activity",
                }
            )
            continue
        elif str(action_id) == "penguin_hide_and_seek":
            rows.append(
                {
                    "handler_key": "utility",
                    "action_id": "penguin_hide_and_seek",
                    "mode": "passthrough",
                    "source_status": "sourced",
                    "source_row": str(spec.get("source", "")),
                    "source_reason": (
                        "One successful review abstracts travel to and spying on "
                        "one selected weekly-roster penguin."
                    ),
                    "includes": ("one roster entry", "one point award"),
                    "multiplier_behavior": (
                        "Never foreground-multiplied; one answered card remains "
                        "one selected spy action"
                    ),
                    "undo_boundary": "one answered-card transaction",
                    "flag_off_behavior": "same single-spy activity handler",
                    "profile": None,
                    "condition": "",
                    "route_kind": "activity",
                }
            )
            continue
        elif str(action_id) == "vinesweeper":
            rows.append(
                {
                    "handler_key": "utility",
                    "action_id": "vinesweeper",
                    "mode": "source_blocked_activity",
                    "source_status": "source_blocked",
                    "source_row": str(spec.get("source", "")),
                    "source_reason": (
                        "The period outcome set is pinned, but hidden field "
                        "probabilities remain unpublished and absent from local emulators."
                    ),
                    "includes": (
                        "one bounded automatic field operation",
                        "one atomic supply and reward transaction",
                    ),
                    "multiplier_behavior": (
                        "M complete operations, stopping at an unaffordable flag boundary"
                    ),
                    "undo_boundary": "one answered-card transaction",
                    "flag_off_behavior": "same bounded activity handler",
                    "profile": None,
                    "condition": "owner-approved bounded hidden-roll abstraction",
                    "route_kind": "activity",
                }
            )
            continue
        if str(action_id) == "big_chinchompa":
            rows.append(
                {
                    "handler_key": "utility",
                    "action_id": "big_chinchompa",
                    "mode": "activity_group",
                    "source_status": "sourced",
                    "source_row": str(spec.get("source", "")),
                    "source_reason": (
                        "One activity step is the owner-approved complete "
                        "fifteen-moth catch-and-feed jar circuit."
                    ),
                    "includes": ("fifteen-moth jar circuit", "world boundary"),
                    "multiplier_behavior": (
                        "M resolves up to M whole circuits before the one "
                        "per-review crowd boundary"
                    ),
                    "undo_boundary": "one answered-card transaction",
                    "flag_off_behavior": "same grouped activity handler",
                    "profile": None,
                    "condition": "",
                    "route_kind": "activity",
                }
            )
            continue
        if str(action_id) == "livid_farm":
            rows.append(
                {
                    "handler_key": "utility",
                    "action_id": "livid_farm",
                    "mode": "rate_limited",
                    "source_status": "sourced",
                    "source_row": str(spec.get("source", "")),
                    "source_reason": (
                        "The source twelve-cycle/hour rate maps exactly to "
                        "six cycles per five successful reviews."
                    ),
                    "includes": ("five-round source cycle",),
                    "multiplier_behavior": (
                        "M successful reviews advance one persisted 6/5 residual"
                    ),
                    "undo_boundary": "one answered-card transaction",
                    "flag_off_behavior": (
                        "Livid Farm retains its source-owned 6/5 activity residual"
                    ),
                    "profile": {
                        "profile_id": "utility:livid_farm",
                        "mode": "rate_limited",
                        "increment_numerator": 6,
                        "threshold_denominator": 5,
                        "cadence_version": 1,
                        "overflow_policy": None,
                    },
                    "condition": "",
                    "route_kind": "activity",
                }
            )
            continue
        rows.append(
            {
                "handler_key": "utility",
                "action_id": str(action_id),
                "mode": "exempt",
                "source_status": "not_applicable",
                "source_row": str(spec.get("source", "")) if isinstance(spec, Mapping) else "",
                "source_reason": "Utility/Activity review actions are batching or progression, not foreground XP/hour admissions",
                "includes": (),
                "multiplier_behavior": "M handler actions under the established dispatcher",
                "undo_boundary": "one answered-card transaction",
                "flag_off_behavior": "same utility handler",
                "profile": None,
                "condition": "",
                "route_kind": "utility",
            }
        )

    for action_id, reason, includes in (
        ("stronghold_of_security", "finite no-XP landmark progression", ()),
        (
            "knight_waves",
            "finite non-repeatable landmark; final combat-stat XP cannot repeat",
            ("attack", "strength", "defence", "constitution"),
        ),
        ("mage_arena", "finite no-XP landmark progression", ()),
        ("mage_arena_attune:guthix", "finite no-XP spell attunement", ()),
        ("mage_arena_attune:saradomin", "finite no-XP spell attunement", ()),
        ("mage_arena_attune:zamorak", "finite no-XP spell attunement", ()),
    ):
        rows.append(
            {
                "handler_key": "utility",
                "action_id": action_id,
                "mode": "exempt",
                "source_status": "not_applicable",
                "source_row": "",
                "source_reason": reason,
                "includes": includes,
                "multiplier_behavior": "established landmark step transaction",
                "undo_boundary": "one answered-card transaction",
                "flag_off_behavior": "same landmark handler",
                "profile": None,
                "condition": "",
                "route_kind": "utility_landmark",
            }
        )

    for quest_id, spec in QUEST_DATA.items():
        rewards = tuple(
            f"{reward.get('skill_id')}:{reward.get('amount')}"
            for reward in (spec.get("xp_rewards", ()) if isinstance(spec, Mapping) else ())
            if isinstance(reward, Mapping)
        )
        combat_stages = sum(
            bool(stage.get("combat_encounters"))
            for stage in (spec.get("stage_requirements", ()) if isinstance(spec, Mapping) else ())
            if isinstance(stage, Mapping)
        )
        rows.append(
            {
                "handler_key": "quest",
                "action_id": str(quest_id),
                "mode": "exempt",
                "source_status": "not_applicable",
                "source_row": str(spec.get("source", "")) if isinstance(spec, Mapping) else "",
                "source_reason": "finite quest-stage progression; completion XP is non-repeatable",
                "includes": rewards,
                "multiplier_behavior": "one collapsed stage per eligible review; never multiplied",
                "undo_boundary": "one answered-card transaction",
                "flag_off_behavior": "same quest handler",
                "profile": None,
                "condition": f"{combat_stages} collapsed quest-combat stage(s)" if combat_stages else "",
                "route_kind": "quest",
            }
        )

    rows.extend(
        [
            {
                "handler_key": "summoning",
                "action_id": "attached:winter_storage",
                "mode": "passthrough",
                "source_status": "sourced",
                "source_row": "Pack Yak Winter Storage",
                "source_reason": "attached modifier owned by the host foreground review",
                "includes": ("one carried scroll", "12 special points", "4.8 Summoning XP"),
                "multiplier_behavior": "at most once per host kernel step",
                "undo_boundary": "same host answered-card transaction",
                "flag_off_behavior": "same carried-overlay modifier",
                "profile": None,
                "condition": "configured full-pack bank boundary",
                "route_kind": "attached",
            },
            {
                "handler_key": "farming",
                "action_id": "queued_background_simulation",
                "mode": "exempt",
                "source_status": "not_applicable",
                "source_row": "",
                "source_reason": "answered-card background clock and explicit queue preemption",
                "includes": ("growth clock", "farm queue"),
                "multiplier_behavior": "one queue/world step; never foreground-multiplied",
                "undo_boundary": "one answered-card transaction",
                "flag_off_behavior": "same Farming simulation",
                "profile": None,
                "condition": "",
                "route_kind": "background",
            },
            {
                "handler_key": "slayer",
                "action_id": "future_attachment",
                "mode": "future_attachment",
                "source_status": "not_implemented",
                "source_row": "",
                "source_reason": "future Slayer XP must inherit the admitted ordinary Combat transaction",
                "includes": (),
                "multiplier_behavior": "inherits 6 * M combat ticks",
                "undo_boundary": "same combat review transaction",
                "flag_off_behavior": "must declare before handler registration",
                "profile": None,
                "condition": "",
                "route_kind": "planned",
            },
            {
                "handler_key": "dungeoneering",
                "action_id": "future_attachment",
                "mode": "future_attachment",
                "source_status": "not_implemented",
                "source_row": "",
                "source_reason": "future floor actions must declare cadence before handler registration",
                "includes": (),
                "multiplier_behavior": "must be settled with the implementation",
                "undo_boundary": "one answered-card transaction",
                "flag_off_behavior": "must declare before handler registration",
                "profile": None,
                "condition": "",
                "route_kind": "planned",
            },
        ]
    )
    return rows


def validate_cadence_coverage_pure(
    implemented_handler_keys: Iterable[str],
) -> dict[str, Any]:
    """Fail closed when dispatch gains a handler or a route is omitted."""

    implemented = frozenset(str(key) for key in implemented_handler_keys)
    missing_handlers = sorted(implemented - CADENCE_DECLARED_HANDLER_KEYS)
    stale_handlers = sorted(CADENCE_DECLARED_HANDLER_KEYS - implemented)
    if missing_handlers or stale_handlers:
        raise ValueError(
            f"cadence handler coverage mismatch: missing={missing_handlers}, stale={stale_handlers}"
        )

    rows = cadence_coverage_rows_pure()
    actual = Counter((row["handler_key"], row["action_id"]) for row in rows)
    duplicates = sorted(key for key, count in actual.items() if count != 1)
    expected = {
        (handler_key, str(action_id))
        for handler_key, table in FOREGROUND_ROUTE_TABLES.items()
        for action_id in table
    }
    expected.update(("utility", str(action_id)) for action_id in UTILITY_ACTIVITY_DATA)
    expected.update(("quest", str(action_id)) for action_id in QUEST_DATA)
    missing_routes = sorted(expected - set(actual))
    invalid_rows = []
    for row in rows:
        mode = str(row.get("mode", ""))
        source_status = str(row.get("source_status", ""))
        source_row = str(row.get("source_row", ""))
        source_reason = str(row.get("source_reason", ""))
        if source_status == "source_blocked" and not source_reason:
            invalid_rows.append(
                (row["handler_key"], row["action_id"], "blocked without reason")
            )
        if mode == "rate_limited" and (
            source_status != "sourced"
            or not source_row
            or not isinstance(row.get("profile"), Mapping)
        ):
            invalid_rows.append(
                (
                    row["handler_key"],
                    row["action_id"],
                    "live rate lacks sourced profile",
                )
            )
        if mode == "source_blocked" and source_status != "source_blocked":
            invalid_rows.append(
                (
                    row["handler_key"],
                    row["action_id"],
                    "blocked mode/status mismatch",
                )
            )
    if duplicates or missing_routes or invalid_rows:
        raise ValueError(
            "cadence route coverage mismatch: "
            f"duplicates={duplicates}, missing={missing_routes}, invalid={invalid_rows}"
        )
    return {
        "handlers": len(implemented),
        "foreground_routes": len(expected),
        "total_rows": len(rows),
        "modes": dict(Counter(str(row["mode"]) for row in rows)),
    }
