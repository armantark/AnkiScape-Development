"""Pinned Crucible entry gate, rank ladder, bounty fee and Trophy bone shop.

The Crucible is dangerous player-versus-player content, so every rule here is
carried from a source that states it. Where the period plainly had a value we
could not recover, the value is a registered `PLACEHOLDER`, never an invention.

Two sources were read independently and agree on the whole reward price table:
the pinned wiki article and the rev-727 cache's own reward enums. Where they
disagree with Darkan, the note at the constant says so.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .equipment_data import EquipmentBonuses, EquipmentItem


CRUCIBLE_ACTIVITY_ID = "crucible"
CRUCIBLE_COMBAT_TARGET_ID = "crucible_target"
CRUCIBLE_CURRENCY = "Trophy bones"
CRUCIBLE_SUPREME_HELM = "Supreme champion's helm"

CRUCIBLE_SOURCE = (
    "RuneScape Wiki Crucible oldid=6538845 (2012-11-06T11:34:47Z); "
    "Update:The Crucible oldid=5778674 (2012-06-19T12:15:18Z); "
    "Trophy bones oldid=5971782 (2012-07-22T02:00:10Z); "
    "Supreme champion's helm oldid=6555268 (2012-11-14T13:40:17Z); "
    "OpenRS2 cache rev 727 (2012-07-24) enums 2118/5899/5900/5901, CS2 "
    "scripts 6284/6288/6275 and interfaces 1292/1296/1297/1298; Darkan "
    "minigames/crucible/CrucibleController.java and Potions.kt "
    "checkPVPPotionBoosts at c95aca409f397cab12c13b6d5269b73f6cd8abe9"
)

# Sourced entry gate. Membership plus combat level 60 buys full participation;
# below that a player reaches the waiting room and the four lessons only.
CRUCIBLE_MINIMUM_COMBAT_LEVEL = 60

# The arena is dangerous, full stop. Darkan's `Crucible.entrance` offers a
# "Which Bounty Hunter mode would you like to enter as?" safe/dangerous choice,
# but that prompt names Bounty Hunter rather than the Crucible and no period
# source describes a selectable safe mode. Both pinned wiki revisions say
# ordinary Crucible combat was dangerous, and the rev-727 warning interface 1292
# reads "If you die you will lose all the items you are carrying." The arena
# became safe only for the Supreme Champion event, which is modelled below.
#
# The same two revisions state that Protect Item prayers and curses were
# disabled here, so unlike the Clan Wars red portal nothing is saved.
CRUCIBLE_PROTECT_ITEM_ALLOWED = False

# Four lessons, each awarding one set of Trophy bones, are the only bone route
# that does not require defeating a target. They are also what a player under
# the combat gate can reach.
CRUCIBLE_LESSONS = (
    "Fighting in the Crucible",
    "Crucible Looting",
    "Crucible Key",
    "Crucible Rewards",
)
# PLACEHOLDER(crucible.lesson_bone_award): the size of the "one set of Trophy
# bones" each lesson pays. Both revisions state the four-lesson cap without ever
# stating the set size, and no recovered enum holds it.
CRUCIBLE_LESSON_BONE_AWARD = 1

# PLACEHOLDER(crucible.bones_per_kill): Trophy bones for defeating an ordinary
# target. The launch update says vanquished players dropped Trophy bones and the
# item page calls them the Crucible's reward currency, but no pre-cutoff
# revision and no recovered cache enum states the quantity.
CRUCIBLE_BONES_PER_KILL = 2

# PLACEHOLDER(crucible.rank_point_thresholds): the point totals that promote a
# player between the client's tiers. Rev-727 script 6284 proves the tier list
# exactly — it maps tiers 0..6 to the displayed "6".."1" and Supreme Champions —
# but it receives an already-computed tier and reads no varp, so the thresholds
# are server-side and unrecovered. Darkan's controller stores `rank` and `points`
# but never changes either; its UI bridge only forwards them to scripts 6284 and
# 6288. The article says only that "every few rank points" raised a rank.
CRUCIBLE_RANKS = (
    (0, "Rank 6", 1),
    (1, "Rank 5", 3),
    (2, "Rank 4", 6),
    (3, "Rank 3", 10),
    (4, "Rank 2", 15),
    (5, "Rank 1", 25),
)
CRUCIBLE_SUPREME_TIER = 6
CRUCIBLE_SUPREME_RANK_NAME = "Supreme Champion"
CRUCIBLE_UNRANKED_TIER = -1
CRUCIBLE_UNRANKED_NAME = "Unranked"

# PLACEHOLDER(crucible.points_per_kill): rank points for an ordinary kill. The
# launch update says points were earned "for every target slain" without a
# number. The complete pre-cutoff article history adds only the exact one-point
# Supreme Champion hit rule below. Darkan initializes rank and points but never
# awards either; rev-727 script 6288 only renders an already-computed delta.
CRUCIBLE_POINTS_PER_KILL = 1

# Exact. The article states that each successful hit on the Supreme Champion
# awarded one rank point, which is the only numeric point rule any source gives.
CRUCIBLE_POINTS_PER_CHAMPION_HIT = 1

# Exact event shape from the launch update: the event runs two and a half
# minutes, the champion is invulnerable for the first two, and the arena is safe
# for its whole duration. The article adds that it fires every half hour.
#
# Half an hour maps onto the house review clock the same way every other world
# event does: `shop_market_clock.answered_cards` runs 240 cards to the game day,
# so a half-hourly event is one every five answered cards.
#
# The invulnerable share is 2 of the 2.5 minutes. At one review per event there is
# no fifth of a window to be vulnerable in, so THE INVULNERABLE PHASE IS NOT
# MODELLED: the champion is attackable for the whole event. Recorded as design
# fork 3.6 rather than left to be read out of these two constants, because
# lengthening the event is a design call and not a source question.
CRUCIBLE_EVENT_INTERVAL_REVIEWS = 5
CRUCIBLE_EVENT_REVIEWS = 1

# Rivals are other players, and the article says the Crucible matched a player
# against another of equivalent or similar combat skill while its criticism
# section records that the matching was imperfect and could pair a low-combat
# player against a maxed one. Both halves of that are modelled by drawing the
# target's level from a spread around the player's own.
#
# A rival's stats are a player's stats, so they are rebuilt from the same combat
# level formula the player uses rather than a fixed fraction of the level. A
# fixed fraction cannot lose to the player at any level, which is exactly how an
# earlier family shipped a match no one could win or lose.
#
# PLACEHOLDER(crucible.target_level_offsets): the actual spread the period matcher
# used. The article says "equivalent or similar combat skill" and its criticism
# section says the matching could pair a low-combat player against a maxed one,
# but no revision states the range, and the rev-727 interfaces hold no matching
# table. These four offsets reproduce the described shape and nothing more.
CRUCIBLE_TARGET_LEVEL_OFFSETS = (-8, 0, 8, 20)

# An AnkiScape abstraction, not a period value: the period game had no answered
# card, so nothing can state how much combat one review is worth. Six ticks is the
# cadence the live Combat activities already run at, which is why it is reused
# here rather than chosen. Tears of Guthix makes the same conversion and it is
# queued as design fork 3.3; changing that answer should change this constant too.
CRUCIBLE_COMBAT_TICKS = 6

# Exact, from Darkan `Potions.kt` `checkPVPPotionBoosts`, which
# `CrucibleController.start` calls on entry and its `sendDeath` calls again on
# every respawn: each combat skill is lowered to `base + flat + base *
# multiplier` whenever a boost has carried it higher.
CRUCIBLE_PVP_BOOST_CAPS = (
    ("attack", 5, 0.15),
    ("strength", 5, 0.15),
    ("defense", 5, 0.15),
    ("ranged", 5, 0.10),
    ("magic", 5, 0.0),
)

# The bounty fee, exactly as rev-727 interface 1298 states it:
#
#     F = ( X - Y ) + Z
#
# X is the risk expected of the player's combat levels, Y is the value of the
# items actually risked, and Z is the target-abandonment amount. The fee leaves
# the money pouch on entry and object 72936 in rev 742 carries a "Get fee"
# option, matching the interface text that some or all of it comes back at an
# arena bank. The article assigns the (X - Y) part to the victor on a death and
# the Z part to the opponent when a player abandons a live target.
#
# PLACEHOLDER(crucible.risk_expectation_per_level): the coins of risk X expects
# per combat level. No pre-cutoff revision states the schedule, the interface
# holds placeholders rather than constants, and the one recorded figure — 518,000
# coins refunded to a maxed player carrying nothing — comes from a money-pouch
# exploit report and is not a fee table.
CRUCIBLE_RISK_EXPECTATION_PER_LEVEL = 400
# PLACEHOLDER(crucible.abandonment_fee): the flat Z component. Stated to exist
# and to be paid to the opponent on abandonment; never given a value.
CRUCIBLE_ABANDONMENT_FEE = 5_000


@dataclass(frozen=True)
class CrucibleUnlock:
    id: str
    kind: str
    display_name: str
    cost: int


def _unlocks(kind: str, rows: tuple[tuple[str, int], ...]) -> tuple[CrucibleUnlock, ...]:
    return tuple(
        CrucibleUnlock(
            f"{kind}_{index}",
            kind,
            name,
            cost,
        )
        for index, (name, cost) in enumerate(rows, start=1)
    )


# Exact names from rev-727 enum 2118 and exact costs from enum 5899, which the
# pinned article's reward table reproduces row for row.
CRUCIBLE_TAUNTS = _unlocks(
    "taunt",
    (
        ("Crazy Laughing", 12),
        ("Chicken Bwak", 12),
        ("Unlucky nubcake!", 36),
        ("Funeral dirge", 36),
        ("You FAIL!", 36),
        ("Sad melody", 36),
        ("Hysterical crowd", 36),
        ("Game over, mortal!", 36),
        ("Muahahaha", 36),
        ("Gothic tune", 36),
    ),
)

# Exact names from the pinned article's reward table and exact costs from
# rev-727 enum 5900. `[name]` is the defeated target's name, as the period
# rendered it.
CRUCIBLE_TITLES = _unlocks(
    "title",
    (
        ("Cowardly [name]", 12),
        ("[name] the Redundant", 12),
        ("Everyone attack [name]", 30),
        ("Smelly [name]", 30),
        ("[name] the Idiot", 30),
        ("Sir Lame [name]", 30),
        ("[name] the Flamboyant", 30),
        ("Weakling [name]", 30),
        ("[name] was punished.", 30),
        ("[name] lost", 30),
        ("[name]... you fail", 30),
        ("No-mates [name]", 30),
        ("[name] ate dirt", 30),
        ("Delusional [name]", 30),
        ("[name] the Respawner", 30),
        ("Cutey-pie [name]", 30),
        ("[name] the Fail Magnet", 30),
        ("[name] was terminated", 30),
        ("Lazy [name]", 30),
        ("[name]? Who?", 30),
    ),
)

CRUCIBLE_UNLOCKS = CRUCIBLE_TAUNTS + CRUCIBLE_TITLES
CRUCIBLE_UNLOCKS_BY_ID = {row.id: row for row in CRUCIBLE_UNLOCKS}

# Exact, from rev-727 enum 5901 and the article's reward table, which agree.
# The helm additionally requires having been Supreme Champion at least once.
CRUCIBLE_SUPREME_HELM_COST = 60
CRUCIBLE_SUPREME_HELM_ITEM_ID = 24463
CRUCIBLE_TROPHY_BONES_ITEM_ID = 24444

# Three fissure energy boosts (24, 36 and 48 bones) and a 15-bone Rogue glove
# repair complete the period reward interface. Both are deliberately not shipped:
# AnkiScape has no fissure travel and no Rogue glove, so either row would be a
# purchase that changes nothing. An omitted row is honest; an inert one is not.


CRUCIBLE_ASSET_MANIFEST = (
    {
        "item_name": "The Crucible",
        "wiki_title": "Crucible symbol.png",
        "output_path": "activityicons/crucible.png",
        "size": 64,
    },
)


def crucible_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        CRUCIBLE_ACTIVITY_ID: {
            "display_name": "The Crucible",
            "requirements": {},
            "skill_requirements": {},
            "outputs": (),
            "batch_size": 1,
            "group": "minigames",
            "source": CRUCIBLE_SOURCE,
        }
    }


def crucible_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    """Register the currency and the helm the generated tables have no row for."""
    return {
        CRUCIBLE_CURRENCY: {
            "category": "currency",
            "source_item_id": CRUCIBLE_TROPHY_BONES_ITEM_ID,
            "stackable": True,
            "tradeable": False,
            "source": CRUCIBLE_SOURCE,
        },
        CRUCIBLE_SUPREME_HELM: {
            "category": "equipment",
            "source_item_id": CRUCIBLE_SUPREME_HELM_ITEM_ID,
            "stackable": False,
            "tradeable": False,
            "equipment_slot": "head",
            "source": CRUCIBLE_SOURCE,
        },
    }


def crucible_equipment_data_as_dict() -> dict[str, EquipmentItem]:
    """The helm is cosmetic; the pinned item revision gives it no bonuses."""
    return {
        CRUCIBLE_SUPREME_HELM: EquipmentItem(
            item_name=CRUCIBLE_SUPREME_HELM,
            slot="head",
            combat_skill=None,
            required_level=1,
            two_handed=False,
            equipment_type="crucible_helm",
            bonuses=EquipmentBonuses(),
            attack_speed=4,
            source_item_id=CRUCIBLE_SUPREME_HELM_ITEM_ID,
            source=CRUCIBLE_SOURCE,
            source_status="pinned period cosmetic reward, no combat bonuses",
            skill_requirements=(),
            weapon_type=-1,
        ),
    }


def crucible_enemy_pure() -> dict[str, Any]:
    """Hidden registry row; live target stats are persisted per arena visit."""
    return {
        "display_name": "Crucible target",
        "level": 3,
        "group": "Crucible",
        "stats": {
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "hitpoints": 100,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {},
        "attack_style": "melee",
        "attack_speed": 4,
        "drops": {"guaranteed": (), "tables": ()},
        "xp_multiplier": 1.0,
        "source": CRUCIBLE_SOURCE + "; hidden dynamic-target registry row",
    }
