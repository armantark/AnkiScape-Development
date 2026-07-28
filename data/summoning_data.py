"""Typed surface data for pre-EOC Summoning.

The generated catalog holds the historical rows. This module adds the
review-native action shape used by storage, runtime dispatch, target metadata,
and the item registry.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal, Mapping, Optional

from ..generated.summoning_data_generated import SUMMONING_CATALOG, SUMMONING_SCROLLS


ActionFamily = Literal["infuse", "scroll"]
TertiaryMode = Literal["all", "any"]

DEFAULT_SUMMONING_TARGET = "infuse_spiritwolf"
SOURCE_DURATION_UNITS_PER_REVIEW = 2
SUMMONING_RENEWAL_SOURCE_MINUTES = 2.5
SCROLLS_PER_POUCH = 10

COMMON_SUMMONING_ITEM_IDS = MappingProxyType(
    {
        "Pouch": 12155,
        "Spirit shards": 12183,
        "Gold charm": 12158,
        "Green charm": 12159,
        "Crimson charm": 12160,
        "Blue charm": 12163,
    }
)


@dataclass(frozen=True)
class SummoningPouch:
    id: str
    familiar_name: str
    pouch_name: str
    pouch_item_id: int
    level: int
    shards: int
    charm: Optional[str]
    charm_item_id: Optional[int]
    tertiaries: tuple[str, ...]
    tertiary_item_ids: tuple[int, ...]
    tertiary_mode: TertiaryMode
    creation_xp: Optional[float]
    summon_xp: float
    duration_source_minutes: int
    lifetime_reviews: int
    summoning_point_cost: int
    combat: str
    lifepoints: Optional[int]
    roles: tuple[str, ...]
    bob_capacity: int
    forage_capacity: int
    delivery_mode: Optional[str]
    boost: Optional[str]
    ability_summary: Optional[str]
    scroll_id: str
    scroll_name: str
    scroll_item_id: int
    scroll_creation_xp: Optional[float]
    scroll_use_xp: Optional[float]
    special_points: int
    special_name: Optional[str]
    craftable: bool
    acquisition: Optional[str]
    bogrog_level: Optional[int]
    bogrog_shards: Optional[int]
    source: str
    scroll_source: str

    @property
    def renewal_window_reviews(self) -> int:
        ratio = SUMMONING_RENEWAL_SOURCE_MINUTES / SOURCE_DURATION_UNITS_PER_REVIEW
        return max(1, math.ceil(ratio))


@dataclass(frozen=True)
class SummoningAction:
    id: str
    display_name: str
    family: ActionFamily
    subgroup: str
    level: int
    xp: float
    familiar_id: str
    input_items: tuple[str, ...]
    output_item: str
    output_quantity: int
    source: str


def _pouch_from_row(row: Mapping[str, object]) -> SummoningPouch:
    duration = int(row["duration_minutes"])
    return SummoningPouch(
        id=str(row["id"]),
        familiar_name=str(row["familiar_name"]),
        pouch_name=str(row["pouch_name"]),
        pouch_item_id=int(row["pouch_item_id"]),
        level=int(row["level"]),
        shards=int(row["shards"]),
        charm=str(row["charm"]) if row.get("charm") else None,
        charm_item_id=(
            int(row["charm_item_id"]) if row.get("charm_item_id") else None
        ),
        tertiaries=tuple(str(item) for item in row["tertiaries"]),
        tertiary_item_ids=tuple(int(item) for item in row["tertiary_item_ids"]),
        tertiary_mode=str(row["tertiary_mode"]),
        creation_xp=(
            float(row["creation_xp"]) if row.get("creation_xp") is not None else None
        ),
        summon_xp=float(row["summon_xp"]),
        duration_source_minutes=duration,
        lifetime_reviews=max(2, math.ceil(duration / SOURCE_DURATION_UNITS_PER_REVIEW)),
        summoning_point_cost=int(row["summoning_point_cost"]),
        combat=str(row["combat"]),
        lifepoints=int(row["lifepoints"]) if row.get("lifepoints") is not None else None,
        roles=tuple(str(role) for role in row["roles"]),
        bob_capacity=int(row["bob_capacity"]),
        forage_capacity=int(row["forage_capacity"]),
        delivery_mode=(
            str(row["delivery_mode"]) if row.get("delivery_mode") else None
        ),
        boost=str(row["boost"]) if row.get("boost") else None,
        ability_summary=(
            str(row["ability_summary"]) if row.get("ability_summary") else None
        ),
        scroll_id=str(row["scroll_id"]),
        scroll_name=str(row["scroll_name"]),
        scroll_item_id=int(row["scroll_item_id"]),
        scroll_creation_xp=(
            float(row["scroll_creation_xp"])
            if row.get("scroll_creation_xp") is not None
            else None
        ),
        scroll_use_xp=(
            float(row["scroll_use_xp"])
            if row.get("scroll_use_xp") is not None
            else None
        ),
        special_points=int(row["special_points"]),
        special_name=(
            str(row["special_name"]) if row.get("special_name") else None
        ),
        craftable=bool(row["craftable"]),
        acquisition=str(row["acquisition"]) if row.get("acquisition") else None,
        bogrog_level=(
            int(row["bogrog_level"]) if row.get("bogrog_level") is not None else None
        ),
        bogrog_shards=(
            int(row["bogrog_shards"])
            if row.get("bogrog_shards") is not None
            else None
        ),
        source=str(row["source"]),
        scroll_source=str(row["scroll_source"]),
    )


SUMMONING_POUCHES = tuple(_pouch_from_row(row) for row in SUMMONING_CATALOG)
SUMMONING_POUCHES_BY_ID: Mapping[str, SummoningPouch] = MappingProxyType(
    {pouch.id: pouch for pouch in SUMMONING_POUCHES}
)
SUMMONING_POUCHES_BY_NAME: Mapping[str, SummoningPouch] = MappingProxyType(
    {pouch.pouch_name: pouch for pouch in SUMMONING_POUCHES}
)


def _actions() -> tuple[SummoningAction, ...]:
    actions: list[SummoningAction] = []
    for pouch in SUMMONING_POUCHES:
        if pouch.craftable and pouch.creation_xp is not None:
            actions.append(
                SummoningAction(
                    id=f"infuse_{pouch.id}",
                    display_name=f"Infuse {pouch.familiar_name} pouch",
                    family="infuse",
                    subgroup="Infuse pouches",
                    level=pouch.level,
                    xp=pouch.creation_xp,
                    familiar_id=pouch.id,
                    input_items=(),
                    output_item=pouch.pouch_name,
                    output_quantity=1,
                    source=pouch.source,
                )
            )
    scroll_groups: dict[str, list[SummoningPouch]] = {}
    for pouch in SUMMONING_POUCHES:
        if pouch.scroll_creation_xp is not None:
            scroll_groups.setdefault(pouch.scroll_id, []).append(pouch)
    for scroll_id, pouches in scroll_groups.items():
        pouch = pouches[0]
        actions.append(
            SummoningAction(
                id=f"scroll_{scroll_id}",
                display_name=f"Create {pouch.scroll_name}",
                family="scroll",
                subgroup="Create scrolls",
                level=min(candidate.level for candidate in pouches),
                xp=float(pouch.scroll_creation_xp),
                familiar_id=pouch.id,
                input_items=tuple(candidate.pouch_name for candidate in pouches),
                output_item=pouch.scroll_name,
                output_quantity=SCROLLS_PER_POUCH,
                source=pouch.scroll_source,
            )
        )
    return tuple(actions)


SUMMONING_ACTIONS = _actions()
SUMMONING_ACTIONS_BY_ID: Mapping[str, SummoningAction] = MappingProxyType(
    {action.id: action for action in SUMMONING_ACTIONS}
)
SUMMONING_ACTION_IDS_BY_FAMILY: Mapping[ActionFamily, tuple[str, ...]] = (
    MappingProxyType(
        {
            family: tuple(
                action.id for action in SUMMONING_ACTIONS if action.family == family
            )
            for family in ("infuse", "scroll")
        }
    )
)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")


def summoning_extra_items_as_dict() -> dict[str, dict[str, object]]:
    items: dict[str, dict[str, object]] = {
        name: {
            "source_item_id": item_id,
            "image": f"summoningitems/{_slug(name)}.png",
            "source": "2011Scape rev-667 Items.kt",
        }
        for name, item_id in COMMON_SUMMONING_ITEM_IDS.items()
    }
    for pouch in SUMMONING_POUCHES:
        items[pouch.pouch_name] = {
            "source_item_id": pouch.pouch_item_id,
            "image": f"summoningitems/{_slug(pouch.pouch_name)}.png",
            "source": pouch.source,
        }
        items[pouch.scroll_name] = {
            "source_item_id": pouch.scroll_item_id,
            "image": f"summoningitems/{_slug(pouch.scroll_name)}.png",
            "source": pouch.scroll_source,
        }
        for name, item_id in zip(pouch.tertiaries, pouch.tertiary_item_ids):
            items.setdefault(
                name,
                {
                    "source_item_id": item_id,
                    "image": f"summoningitems/{_slug(name)}.png",
                    "source": pouch.source,
                },
            )
    if "Swamp toad" in items:
        items["Swamp toad"]["stackable"] = False
        items["Swamp toad"]["tradeable"] = True
    if "Willow branch" in items:
        items["Willow branch"].update(
            {
                "source_item_id": 5933,
                "stackable": False,
                "tradeable": True,
                "source": (
                    "RuneScape Wiki Willow branch oldid=6092914 "
                    "(2012-08-14T16:12:52Z); OpenRS2 rev-742 item 5933"
                ),
            }
        )
    return items


assert len(SUMMONING_POUCHES) == 80
assert len(SUMMONING_ACTIONS) == 145
assert len({pouch.pouch_item_id for pouch in SUMMONING_POUCHES}) == 80
assert not any("dungeoneer" in action.display_name.casefold() for action in SUMMONING_ACTIONS)
