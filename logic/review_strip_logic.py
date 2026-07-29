"""What the always-visible reviewer strip shows, and when.

Design-thread section 4.8 settles the rule: the strip shows only what is live
right now. Every enable and visibility decision therefore lives in this module,
and ``ui.py`` renders the result without deciding anything.

Three tenants sit under the review card:

* the running target's real experience bars. A shooting star trains Mining and an
  Evil Tree trains Woodcutting, so those are the bars the strip must show; the
  old overlay replaced them with an activity caption, which is the complaint
  that produced this contract.
* the Grand Exchange fills drawer, whose own view lives with the Grand Exchange
  state in ``grand_exchange_logic``.
* the persistent Distractions-and-Farming badge, the one seat the live-only rule
  exempts, because it is the notification system rather than a status readout.
"""
from __future__ import annotations

from typing import Any, Callable, Mapping

from ..core.constants import (
    BIRD_NEST_OPEN_TABLES,
    COOKING_ITEM_IMAGES,
    DEFAULT_UTILITY_ACTIVITY,
    MINING_PICKAXE_DATA,
    exp_table_for_skill,
    QUEST_UNLOCK_RULES,
    UTILITY_ACTIVITY_DATA,
    UTILITY_ITEM_IMAGES,
    WOODCUTTING_AXE_DATA,
)
from ..core.target_metadata import utility_activity_rows
from ..data.big_chinchompa_data import BIG_CHINCHOMPA_UTILITY_ID
from ..data.evil_tree_data import EVIL_TREE_UTILITY_ID
from ..data.fish_flingers_data import FISH_FLINGERS_ACTIVITY_ID
from ..data.fishing_trawler_data import FISHING_TRAWLER_ACTIVITY_ID
from ..data.gnome_ball_data import GNOME_BALL_ACTIVITY_ID
from ..data.great_orb_project_data import GREAT_ORB_PROJECT_ACTIVITY_ID
from ..data.livid_farm_data import LIVID_FARM_ACTIVITY_ID
from ..data.managing_miscellania_data import MANAGING_MISCELLANIA_ACTIVITY_ID
from ..data.pyramid_plunder_data import PYRAMID_PLUNDER_ACTIVITY_ID
from ..data.shooting_star_data import SHOOTING_STAR_ACTIVITY_ID
from ..data.sorceress_garden_data import SORCERESS_GARDEN_ACTIVITY_ID
from ..data.tears_of_guthix_data import TEARS_OF_GUTHIX_ACTIVITY_ID
from ..data.vinesweeper_data import VINESWEEPER_ACTIVITY_ID
from ..data.werewolf_skullball_data import WEREWOLF_SKULLBALL_ACTIVITY_ID
from ..logic.big_chinchompa_logic import big_chinchompa_view_pure
from ..logic.dnd_favourites_logic import (
    dnd_activity_display_name_pure,
    sanitize_dnd_favourites_pure,
)
from ..logic.evil_tree_logic import evil_tree_view_pure
from ..logic.farming_logic import farming_frontend_projection_pure
from ..logic.shooting_star_logic import shooting_star_view_pure
from ..logic.tears_of_guthix_logic import reward_skill_pure
from ..logic_pure.logic_pure import (
    best_mining_pickaxe_pure,
    best_woodcutting_axe_pure,
    compute_level_progress,
)

# A resolved Big Chinchompa keeps reporting its outcome for this many reviews.
WORLD_EVENT_OUTCOME_REVIEWS = 10

# The strip is one compact row. Two bars is the most it can hold without
# becoming the stacked rectangle section 4.8 exists to prevent; an activity that
# trains more names the rest in its caption instead.
MAX_STRIP_XP_BARS = 2


def _has_usable_hatchet(player_data: Mapping[str, Any]) -> bool:
    return (
        best_woodcutting_axe_pure(
            int(player_data.get("woodcutting_level", 1) or 1),
            player_data.get("inventory", {}) or {},
            player_data.get("toolbelt", {}) or {},
            WOODCUTTING_AXE_DATA,
        )
        is not None
    )


def _has_usable_pickaxe(player_data: Mapping[str, Any]) -> bool:
    return (
        best_mining_pickaxe_pure(
            int(player_data.get("mining_level", 1) or 1),
            player_data.get("inventory", {}) or {},
            player_data.get("toolbelt", {}) or {},
            MINING_PICKAXE_DATA,
        )
        is not None
    )


def world_event_rows_pure(
    player_data: Mapping[str, Any], *, suppress_id: str = ""
) -> tuple[tuple[str, str], ...]:
    """(activity_id, one-line summary) for every live review-clock world event.

    Shared by the Activities hub's "Live world events" strip and the reviewer
    badge so the two can never drift. Only the three events that spawn on the
    review clock without the player asking belong here; player-started sessions
    such as Fist of Guthix already have their own counters. The activity id rides
    along so a badge click can open that event's card.
    """
    rows: list[tuple[str, str]] = []
    if suppress_id != EVIL_TREE_UTILITY_ID:
        evil_view = evil_tree_view_pure(
            player_data,
            has_usable_hatchet=_has_usable_hatchet(player_data),
        )
        if evil_view["active"]:
            rows.append((
                EVIL_TREE_UTILITY_ID,
                f"{evil_view['tier_name']} · "
                f"{evil_view['location']} · "
                f"{int(evil_view['reviews_remaining'])} reviews left",
            ))
        blessing = int(evil_view.get("blessing_reviews_remaining", 0) or 0)
        if blessing > 0:
            rows.append((
                EVIL_TREE_UTILITY_ID,
                f"Evil Tree blessing · {blessing} reviews left",
            ))
    if suppress_id != SHOOTING_STAR_ACTIVITY_ID:
        star = shooting_star_view_pure(
            player_data,
            has_usable_pickaxe=_has_usable_pickaxe(player_data),
        )
        if star["active"]:
            rows.append((
                SHOOTING_STAR_ACTIVITY_ID,
                f"Shooting Star size {int(star['current_size'])} · "
                f"{int(star['layer_remaining']):,} layer dust left · "
                f"{int(star['dust'])}/{int(star['dust_cap'])} stardust",
            ))
        elif star["sprite_available"]:
            rows.append((
                SHOOTING_STAR_ACTIVITY_ID,
                "Star sprite ready to exchange · "
                f"{int(star['sprite_reviews_remaining'])} reviews left · "
                f"{int(star['dust'])} stardust",
            ))
    if suppress_id != BIG_CHINCHOMPA_UTILITY_ID:
        big = big_chinchompa_view_pure(player_data)
        if big["active"]:
            rows.append((
                BIG_CHINCHOMPA_UTILITY_ID,
                f"Big Chinchompa · "
                f"{int(big['minutes_remaining'])} source min left · "
                f"{int(big['fullness_percent'])}% full",
            ))
        else:
            # No `or -1` fallback here: the resolution card itself reports 0,
            # which is falsy, so that idiom silently swallowed the one review
            # where the outcome matters most.
            try:
                resolved_ago = int(big.get("resolved_reviews_ago", -1))
            except (TypeError, ValueError):
                resolved_ago = -1
            result = str(big.get("last_result", "") or "")
            if result and 0 <= resolved_ago < WORLD_EVENT_OUTCOME_REVIEWS:
                rows.append((BIG_CHINCHOMPA_UTILITY_ID, result))
    return tuple(rows)


# The three world-clock Distractions exist whether or not the player asked for
# them, so selecting one is not the same as being able to train it. Every other
# activity trains the moment it is the chosen target.
_WORLD_CLOCK_LIVENESS: dict[str, Callable[[Mapping[str, Any]], bool]] = {
    EVIL_TREE_UTILITY_ID: lambda data: bool(
        evil_tree_view_pure(
            data, has_usable_hatchet=_has_usable_hatchet(data)
        )["active"]
    ),
    SHOOTING_STAR_ACTIVITY_ID: lambda data: bool(
        shooting_star_view_pure(
            data, has_usable_pickaxe=_has_usable_pickaxe(data)
        )["active"]
    ),
    BIG_CHINCHOMPA_UTILITY_ID: lambda data: bool(
        big_chinchompa_view_pure(data)["active"]
    ),
}


def activity_awards_experience_now_pure(
    player_data: Mapping[str, Any], activity_id: Any
) -> bool:
    """Whether the next review on this activity can move a skill bar at all."""

    wanted = str(activity_id or "")
    if not wanted:
        return False
    session = player_data.get("activity_session")
    open_session = str(
        session.get("active_id", "") if isinstance(session, Mapping) else ""
    )
    if open_session and open_session != wanted:
        return False
    liveness = _WORLD_CLOCK_LIVENESS.get(wanted)
    return liveness(player_data) if liveness is not None else True


def skill_xp_bar_pure(
    player_data: Mapping[str, Any], skill: str
) -> dict[str, Any]:
    """One experience bar row for a real skill, as the strip renders it."""

    level = int(player_data.get(f"{skill.lower()}_level", 1) or 1)
    exp = float(player_data.get(f"{skill.lower()}_exp", 0) or 0)
    percent, remaining, target_level = compute_level_progress(
        level,
        exp,
        exp_table_for_skill(skill),
    )
    return {
        "skill": skill,
        "level": level,
        "percent": percent,
        "remaining": remaining,
        "target_level": target_level,
    }


# The skills each activity really trains, primary first, mirroring the award
# sites in runtime/runtime_actions_activities.py — no activity spec declares
# this, so the award call is the only source of truth. An activity absent from
# the table shows no bar, which is what every activity did before this contract.
#
# Deliberately absent: the combat activities, whose skills come from the attack
# style rather than the activity, and Court Cases, the Circus, Trouble Brewing,
# Shades of Mort'ton and Troll Invasion, which pick their skill from a reward
# table or a player choice at payout. Guessing at those would put a wrong bar on
# screen, which is worse than the empty row they render today.
ACTIVITY_TRAINED_SKILLS: dict[str, tuple[str, ...]] = {
    SHOOTING_STAR_ACTIVITY_ID: ("Mining",),          # :838
    BIG_CHINCHOMPA_UTILITY_ID: ("Hunter",),          # :753
    SORCERESS_GARDEN_ACTIVITY_ID: ("Farming", "Thieving"),  # :1256, :1259
    VINESWEEPER_ACTIVITY_ID: ("Hunter",),            # :1323
    PYRAMID_PLUNDER_ACTIVITY_ID: (
        "Thieving",
        "Strength",
        "Runecrafting",
    ),                                               # :1401-1411
    WEREWOLF_SKULLBALL_ACTIVITY_ID: ("Agility",),    # :1446
    GNOME_BALL_ACTIVITY_ID: ("Agility", "Ranged"),   # :1485, :1488
    FISH_FLINGERS_ACTIVITY_ID: ("Fishing",),         # :1535
    FISHING_TRAWLER_ACTIVITY_ID: ("Fishing",),       # :1576
    GREAT_ORB_PROJECT_ACTIVITY_ID: ("Runecrafting",),  # :1619
    MANAGING_MISCELLANIA_ACTIVITY_ID: ("Woodcutting",),  # :2437
    LIVID_FARM_ACTIVITY_ID: ("Magic",),              # :581
}


def _evil_tree_trained_skills(player_data: Mapping[str, Any]) -> tuple[str, ...]:
    phase = str(
        evil_tree_view_pure(
            player_data, has_usable_hatchet=_has_usable_hatchet(player_data)
        ).get("phase", "")
        or ""
    )
    if phase == "nurture":
        return ("Farming",)
    if phase == "fell":
        return ("Woodcutting", "Firemaking")
    return ("Woodcutting",)


def _tears_of_guthix_trained_skills(
    player_data: Mapping[str, Any]
) -> tuple[str, ...]:
    return (str(reward_skill_pure(player_data)["display_name"]),)


# Two families pick their skill at award time instead of declaring it, so they
# answer for themselves: the Evil Tree by phase, Tears of Guthix by whichever
# trainable skill currently has the least experience.
_DYNAMIC_TRAINED_SKILLS: dict[
    str, Callable[[Mapping[str, Any]], tuple[str, ...]]
] = {
    EVIL_TREE_UTILITY_ID: _evil_tree_trained_skills,
    TEARS_OF_GUTHIX_ACTIVITY_ID: _tears_of_guthix_trained_skills,
}


def activity_trained_skills_pure(
    player_data: Mapping[str, Any], activity_id: Any
) -> tuple[str, ...]:
    """The real skills one activity awards experience in, primary first."""

    wanted = str(activity_id or "")
    dynamic = _DYNAMIC_TRAINED_SKILLS.get(wanted)
    if dynamic is not None:
        return dynamic(player_data)
    return ACTIVITY_TRAINED_SKILLS.get(wanted, ())


def activity_xp_bars_pure(
    player_data: Mapping[str, Any], activity_id: Any
) -> dict[str, Any]:
    """The real skill bars for one running activity, plus the skills left over.

    ``bars`` is empty whenever the activity cannot award experience on the next
    review, which is how a finished shooting star takes its Mining bar away.
    """

    trained = activity_trained_skills_pure(player_data, activity_id)
    if not trained or not activity_awards_experience_now_pure(
        player_data, activity_id
    ):
        return {"bars": (), "also_trains": ()}
    return {
        "bars": tuple(
            skill_xp_bar_pure(player_data, skill)
            for skill in trained[:MAX_STRIP_XP_BARS]
        ),
        "also_trains": tuple(trained[MAX_STRIP_XP_BARS:]),
    }


def _quiet_favourite_status_pure(row: Any) -> str:
    """One line of status for a watched Distraction with no live event.

    ``utility_activity_rows`` is the only cross-family signal that exists today:
    every other status is bespoke per family. It answers "can I go and do this
    right now", which is what a watch list is for, and the popover line opens the
    activity's own surface for everything past that.
    """

    if row is None:
        return "Nothing live right now"
    if row.locked_reasons:
        return str(row.locked_reasons[0])
    if row.current:
        return "Selected as your review target"
    return "Ready — nothing live"


def review_status_badge_view_pure(
    player_data: Mapping[str, Any]
) -> dict[str, Any]:
    """The persistent left-hand badge: live Distractions, watched ones, Farming.

    Section 4.8 gives this badge the strip's only permanent seat, so unlike the
    experience bars it renders even when every line is quiet. ``count`` counts
    only the lines that are live or need an answer, which is what the player
    reads at a glance.
    """

    favourites = sanitize_dnd_favourites_pure(player_data.get("dnd_favourites"))
    live_rows = world_event_rows_pure(player_data)
    live_by_id: dict[str, list[str]] = {}
    for activity_id, text in live_rows:
        live_by_id.setdefault(activity_id, []).append(text)
    quiet_favourites = [
        activity_id
        for activity_id in favourites
        if activity_id not in live_by_id
    ]
    # Walking every activity's requirements is only worth it when a quiet
    # favourite actually needs a status line, which for most saves is never.
    rows_by_id: dict[str, Any] = (
        {
            row.target_id: row
            for row in utility_activity_rows(
                player_data,
                UTILITY_ACTIVITY_DATA,
                {**UTILITY_ITEM_IMAGES, **COOKING_ITEM_IMAGES},
                BIRD_NEST_OPEN_TABLES,
                DEFAULT_UTILITY_ACTIVITY,
                QUEST_UNLOCK_RULES,
            )
        }
        if quiet_favourites
        else {}
    )

    rows: list[dict[str, Any]] = []
    for activity_id, text in live_rows:
        rows.append({
            "kind": "distraction",
            "activity_id": activity_id,
            "name": dnd_activity_display_name_pure(activity_id),
            "status": text,
            "live": True,
            "favourite": activity_id in favourites,
        })
    for activity_id in quiet_favourites:
        rows.append({
            "kind": "distraction",
            "activity_id": activity_id,
            "name": dnd_activity_display_name_pure(activity_id),
            "status": _quiet_favourite_status_pure(rows_by_id.get(activity_id)),
            "live": False,
            "favourite": True,
        })

    farming = farming_frontend_projection_pure(player_data)
    for crop_row in farming.get("compact_rows", ()):
        rows.append({
            "kind": "farming",
            "patch_id": str(crop_row["patch_id"]),
            "name": str(crop_row["crop_name"]),
            "status": f"{crop_row['status_label']} · {crop_row['patch_name']}",
            "live": str(crop_row["status"]) in {"ready", "diseased", "dead"},
            "favourite": False,
        })

    hud = farming.get("hud", farming)
    queued = int(hud.get("queue_count", hud.get("queued_count", 0)) or 0)
    live_count = sum(1 for row in rows if row["live"])
    tooltip_lines = [f"{row['name']} · {row['status']}" for row in rows]
    if queued:
        tooltip_lines.append(f"{queued} Farming steps queued")
    return {
        "rows": tuple(rows),
        "count": live_count,
        # A diseased or dead crop is the one line that needs the player rather
        # than merely informing them, so it keeps the old badge's "!" form.
        "alert": int(hud.get("urgent_count", 0) or 0) > 0,
        "queued_count": queued,
        "tooltip": "\n".join(tooltip_lines)
        or "Nothing live. Pin a Distraction to watch it here.",
    }
