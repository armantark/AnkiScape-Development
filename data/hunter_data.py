"""2011-era Hunter target data for AnkiScape.

Hunter mechanics are not implemented in the local 2011Scape rev-667 plugin
checkout. The row contract therefore uses 2011.rs guide rows for player-facing
levels/XP/rewards, with the local 2012scape/Darkan Hunter implementation used
only to confirm item/NPC IDs and live mechanic families.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Tuple


DARKAN_HUNTER_SOURCE_ROOT = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
    "src/main/java/com/rs/game/content/skills/hunter"
)
BOX_HUNTER_TYPE_SOURCE = f"{DARKAN_HUNTER_SOURCE_ROOT}/BoxHunterType.java"
BOX_TRAP_TYPE_SOURCE = f"{DARKAN_HUNTER_SOURCE_ROOT}/BoxTrapType.java"
FLYING_ENTITY_SOURCE = f"{DARKAN_HUNTER_SOURCE_ROOT}/FlyingEntityHunter.java"
FALCONRY_KEBBIT_SOURCE = f"{DARKAN_HUNTER_SOURCE_ROOT}/falconry/Kebbit.java"
HUNTER_SUPPLY_SHOP_SOURCE = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
    "data/items/shops/alecks_hunter_emporium.json"
)
HUNTER_IMPLING_JAR_SHOP_SOURCE = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
    "data/items/shops/elnocks_backup_supply.json"
)
HUNTER_SMALL_NET_SHOP_SOURCE = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
    "data/items/shops/lumbridge_fishing_supplies.json"
)
HUNTER_ROPE_SHOP_SOURCE = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
    "data/items/shops/shantay_pass_shop.json"
)
HUNTER_BIRD_SNARING_SOURCE = "https://www.2011.rs/kb/hunter_bird_snaring_level_1"
HUNTER_TRACKING_SOURCE = "https://runescape.wiki/w/Hunter?oldid=6484443"
HUNTER_BUTTERFLY_SOURCE = "https://www.2011.rs/kb/hunter_butterfly_netting_level_15"
HUNTER_DEADFALL_SOURCE = "https://www.2011.rs/kb/hunter_deadfall_level_23"
HUNTER_BOX_TRAPPING_SOURCE = "https://www.2011.rs/kb/hunter_box_trapping_level_27"
HUNTER_NET_TRAPPING_SOURCE = "https://www.2011.rs/kb/hunter_net_trapping_level_29"
HUNTER_MAGIC_BOX_SOURCE = "https://www.2011.rs/kb/hunter_magical_imp_boxes_level_71"
HUNTER_LOCATION_SOURCE = "https://www.2011.rs/kb/hunter_locations"
HUNTER_WIMPY_BIRD_SOURCE = "https://runescape.wiki/w/Wimpy_bird?oldid=5936660"
HERBLORE_HABITAT_SOURCE = "https://runescape.wiki/w/Herblore_Habitat?oldid=6513740"
HERBLORE_HABITAT_JADINKO_SOURCES = {
    "track_diseased_jadinko": "https://runescape.wiki/w/Diseased_jadinko?oldid=6062055",
    "track_shadow_jadinko": "https://runescape.wiki/w/Shadow_jadinko?oldid=6045371",
    "catch_cannibal_jadinko": "https://runescape.wiki/w/Cannibal_jadinko?oldid=5976665",
    "catch_guthix_jadinko": "https://runescape.wiki/w/Guthix_jadinko?oldid=6167443",
}
DARKAN_HERBLORE_HABITAT_SOURCE_ROOT = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
)

# PLACEHOLDER(hunter.herblore_habitat_success_curves): period Marasamaw and
# tracker catch routines or qualified measured tables would replace this shared fallback.
HERBLORE_HABITAT_RATE1 = 128
HERBLORE_HABITAT_RATE99 = 256

EAGLES_PEAK_SOURCE = "https://www.2011.rs/kb/eagles_peak_members"
ROCKING_OUT_SOURCE = "https://www.2011.rs/kb/rocking_out_members"
AS_A_FIRST_RESORT_SOURCE = "https://www.2011.rs/kb/as_a_first_resort_members"
PRIEST_IN_PERIL_SOURCE = "https://runescape.wiki/w/Priest_in_Peril?oldid=6487728"

DEFAULT_HUNTER_TARGET = "catch_crimson_swift"

HUNTER_GROUP_LABELS = {
    "bird_snaring": "Bird snaring",
    "tracking": "Tracking",
    "butterfly_netting": "Butterfly netting",
    "barehanded_butterflies": "Barehanded butterflies",
    "deadfall": "Deadfall",
    "box_trapping": "Box trapping",
    "net_trapping": "Net trapping",
    "falconry": "Falconry",
    "magic_box": "Magic boxes",
    "impling_puro_puro": "Implings - Puro-Puro",
    "impling_world": "Implings - world",
}
HUNTER_GROUP_ORDER = tuple(HUNTER_GROUP_LABELS.keys())
_GROUP_SORT = {group_id: index for index, group_id in enumerate(HUNTER_GROUP_ORDER)}
HUNTER_REUSABLE_TOOLS_BY_GROUP = {
    "bird_snaring": (("Bird snare", 1),),
    "tracking": (("Noose wand", 1),),
    "butterfly_netting": (("Butterfly net", 1),),
    "box_trapping": (("Box trap", 1),),
    "net_trapping": (("Small fishing net", 1), ("Rope", 1)),
    "impling_puro_puro": (("Butterfly net", 1),),
}
HUNTER_REUSABLE_TOOLS_BY_TARGET = {
    "catch_cannibal_jadinko": (("Marasamaw plant", 1),),
    "catch_guthix_jadinko": (("Marasamaw plant", 1),),
    "catch_imp_magic_box": (),
}
HUNTER_SUPPLY_BUNDLE = (
    ("Bird snare", 1),
    ("Box trap", 1),
    ("Butterfly net", 1),
    ("Butterfly jar", 10),
    ("Magic box", 1),
    ("Small fishing net", 1),
    ("Rope", 1),
    ("Noose wand", 1),
    ("Teasing stick", 1),
    ("Rabbit snare", 1),
    ("Impling jar", 10),
)


@dataclass(frozen=True)
class HunterTarget:
    id: str
    display_name: str
    group: str
    level: int
    base_exp: float
    outputs: Tuple[Tuple[str, int], ...]
    primary_output: str
    requirements: Tuple[Tuple[str, int], ...] = ()
    skill_requirements: Tuple[Tuple[str, int], ...] = ()
    xp_rewards: Tuple[Tuple[str, float], ...] = ()
    tools: Tuple[Tuple[str, int], ...] = ()
    source: str = ""
    mechanics_source: str = ""
    source_enum: str = ""
    source_npc_id: int = 0
    source_item_id: int = 0
    rate1: int = 128
    rate99: int = 256
    deterministic: bool = False
    tradeable: bool = True
    notes: str = ""
    sort_order: int = 0


def _req(*pairs: Tuple[str, int]) -> Tuple[Tuple[str, int], ...]:
    return tuple(pairs)


def _out(*pairs: Tuple[str, int]) -> Tuple[Tuple[str, int], ...]:
    return tuple(pairs)


def _target(
    id: str,
    display_name: str,
    group: str,
    level: int,
    base_exp: float,
    outputs: Tuple[Tuple[str, int], ...],
    primary_output: str,
    requirements: Tuple[Tuple[str, int], ...] = (),
    source: str = "",
    mechanics_source: str = BOX_HUNTER_TYPE_SOURCE,
    source_enum: str = "",
    source_npc_id: int = 0,
    source_item_id: int = 0,
    rate1: int = 128,
    rate99: int = 256,
    deterministic: bool = False,
    tradeable: bool = True,
    notes: str = "",
    sort_order: int = 0,
    skill_requirements: Tuple[Tuple[str, int], ...] = (),
    xp_rewards: Tuple[Tuple[str, float], ...] = (),
) -> HunterTarget:
    tools = HUNTER_REUSABLE_TOOLS_BY_TARGET.get(id, HUNTER_REUSABLE_TOOLS_BY_GROUP.get(group, ()))
    return HunterTarget(
        id=id,
        display_name=display_name,
        group=group,
        level=level,
        base_exp=base_exp,
        outputs=outputs,
        primary_output=primary_output,
        requirements=requirements,
        skill_requirements=skill_requirements,
        xp_rewards=xp_rewards,
        tools=tools,
        source=source,
        mechanics_source=mechanics_source,
        source_enum=source_enum,
        source_npc_id=source_npc_id,
        source_item_id=source_item_id,
        rate1=rate1,
        rate99=rate99,
        deterministic=deterministic,
        tradeable=tradeable,
        notes=notes,
        sort_order=sort_order,
    )


_BONES = ("Bones", 1)

HUNTER_TARGETS: Tuple[HunterTarget, ...] = (
    _target(
        "catch_crimson_swift",
        "Catch crimson swift",
        "bird_snaring",
        1,
        34.0,
        _out(_BONES, ("Raw bird meat", 1), ("Red feather", 5)),
        "Red feather",
        source=HUNTER_BIRD_SNARING_SOURCE,
        source_enum="CRIMSON_SWIFT",
        source_npc_id=5073,
        rate1=73,
        rate99=230,
        sort_order=10,
    ),
    _target(
        "catch_golden_warbler",
        "Catch golden warbler",
        "bird_snaring",
        5,
        48.0,
        _out(_BONES, ("Raw bird meat", 1), ("Yellow feather", 5)),
        "Yellow feather",
        source=HUNTER_BIRD_SNARING_SOURCE,
        source_enum="GOLDEN_WARBLER",
        source_npc_id=5075,
        rate1=60,
        rate99=190,
        sort_order=20,
    ),
    _target(
        "catch_copper_longtail",
        "Catch copper longtail",
        "bird_snaring",
        9,
        62.0,
        _out(_BONES, ("Raw bird meat", 1), ("Orange feather", 5)),
        "Orange feather",
        source=HUNTER_BIRD_SNARING_SOURCE,
        source_enum="COPPER_LONGTAIL",
        source_npc_id=5076,
        rate1=60,
        rate99=170,
        notes="2011.rs lists 62 XP; the Darkan implementation uses 61 XP.",
        sort_order=30,
    ),
    _target(
        "catch_cerulean_twitch",
        "Catch cerulean twitch",
        "bird_snaring",
        11,
        64.0,
        _out(_BONES, ("Raw bird meat", 1), ("Blue feather", 5)),
        "Blue feather",
        source=HUNTER_BIRD_SNARING_SOURCE,
        source_enum="CERULEAN_TWITCH",
        source_npc_id=5074,
        rate1=50,
        rate99=160,
        notes="2011.rs rounds this row to 64 XP; the Darkan implementation uses 64.67 XP.",
        sort_order=40,
    ),
    _target(
        "catch_tropical_wagtail",
        "Catch tropical wagtail",
        "bird_snaring",
        19,
        95.0,
        _out(_BONES, ("Raw bird meat", 1), ("Stripy feather", 5)),
        "Stripy feather",
        source=HUNTER_BIRD_SNARING_SOURCE,
        source_enum="TROPICAL_WAGTAIL",
        source_npc_id=5072,
        rate1=45,
        rate99=150,
        notes="2011.rs rounds this row to 95 XP; the Darkan implementation uses 95.2 XP.",
        sort_order=50,
    ),
    _target(
        "catch_wimpy_bird",
        "Catch wimpy bird",
        "bird_snaring",
        39,
        167.0,
        _out(_BONES, ("Raw bird meat", 1), ("Wimpy feather", 5)),
        "Wimpy feather",
        source=HUNTER_WIMPY_BIRD_SOURCE,
        source_enum="WIMPY_BIRD",
        source_npc_id=7031,
        rate1=42,
        rate99=140,
        notes=(
            "Route is tied to Oo'glog after As a First Resort; the period page "
            "lists 5-10 Wimpy feathers, and this deterministic row keeps the "
            "sourced minimum."
        ),
        sort_order=60,
    ),
    _target(
        "catch_polar_kebbit",
        "Catch polar kebbit",
        "tracking",
        1,
        30.0,
        _out(_BONES, ("Raw beast meat", 1), ("Polar kebbit fur", 1)),
        "Polar kebbit fur",
        source=HUNTER_TRACKING_SOURCE,
        mechanics_source=(
            "Hunter oldid 6484443: four or five trail searches collapse into "
            "one review transaction"
        ),
        source_item_id=10117,
        # PLACEHOLDER(hunter.polar_kebbit_success_curve): a period tracking
        # catch routine or measured table would replace this fallback.
        rate1=128,
        rate99=256,
        notes=(
            "One review represents the complete four- or five-search trail and "
            "final attack; the hidden catch curve uses the registered Hunter fallback."
        ),
        sort_order=5,
    ),
    _target(
        "track_razor_backed_kebbit",
        "Track razor-backed kebbit",
        "tracking",
        49,
        348.0,
        _out(_BONES, ("Raw beast meat", 1), ("Long kebbit spike", 1)),
        "Long kebbit spike",
        source=HUNTER_TRACKING_SOURCE,
        mechanics_source=(
            "Hunter oldid 6484443: four or five trail searches collapse into "
            "one review transaction"
        ),
        source_item_id=10107,
        # PLACEHOLDER(hunter.razor_backed_kebbit_success_curve): a period
        # tracking catch routine or measured table would replace this fallback.
        rate1=128,
        rate99=256,
        notes=(
            "One review represents the complete four- or five-search trail and "
            "final attack; the hidden catch curve uses the registered Hunter fallback."
        ),
        sort_order=10,
    ),
    _target(
        "track_shadow_jadinko",
        "Track shadow jadinko",
        "tracking",
        71,
        475.0,
        _out(("Shadow vine", 1)),
        "Shadow vine",
        source=f"{HERBLORE_HABITAT_JADINKO_SOURCES['track_shadow_jadinko']}; {HERBLORE_HABITAT_SOURCE}",
        mechanics_source=(f"{DARKAN_HERBLORE_HABITAT_SOURCE_ROOT}data/npcs/drops/hunter/" "hunter_jadinko_shadow.json"),
        source_enum="SHADOW",
        source_item_id=19977,
        rate1=HERBLORE_HABITAT_RATE1,
        rate99=HERBLORE_HABITAT_RATE99,
        tradeable=False,
        notes=("Shadow jadinko oldid 6045371 pins level 71, 475 XP, Noose-wand tracking, Shadow vine, and the red-blossom and abandoned-house Habitat setup. One review represents the complete trail and persistent setup."),
        sort_order=20,
    ),
    _target(
        "track_diseased_jadinko",
        "Track diseased jadinko",
        "tracking",
        78,
        580.5,
        _out(("Corrupt vine", 1)),
        "Corrupt vine",
        source=f"{HERBLORE_HABITAT_JADINKO_SOURCES['track_diseased_jadinko']}; {HERBLORE_HABITAT_SOURCE}",
        mechanics_source=(f"{DARKAN_HERBLORE_HABITAT_SOURCE_ROOT}data/npcs/drops/hunter/" "hunter_jadinko_diseased.json"),
        source_enum="DISEASED",
        source_item_id=19979,
        rate1=HERBLORE_HABITAT_RATE1,
        rate99=HERBLORE_HABITAT_RATE99,
        tradeable=False,
        notes=("Diseased jadinko oldid 6062055 pins level 78, 580.5 XP, Noose-wand tracking, Corrupt vine, and the boneyard and banana-tree Habitat setup. One review represents the complete trail and persistent setup."),
        sort_order=30,
    ),
    _target(
        "catch_ruby_harvest",
        "Catch ruby harvest",
        "butterfly_netting",
        15,
        24.0,
        _out(("Ruby harvest", 1)),
        "Ruby harvest",
        _req(("Butterfly jar", 1)),
        HUNTER_BUTTERFLY_SOURCE,
        HUNTER_BUTTERFLY_SOURCE,
        source_item_id=10020,
        deterministic=True,
        sort_order=10,
    ),
    _target(
        "catch_sapphire_glacialis",
        "Catch sapphire glacialis",
        "butterfly_netting",
        25,
        34.0,
        _out(("Sapphire glacialis", 1)),
        "Sapphire glacialis",
        _req(("Butterfly jar", 1)),
        HUNTER_BUTTERFLY_SOURCE,
        HUNTER_BUTTERFLY_SOURCE,
        source_item_id=10018,
        deterministic=True,
        sort_order=20,
    ),
    _target(
        "catch_snowy_knight",
        "Catch snowy knight",
        "butterfly_netting",
        35,
        44.0,
        _out(("Snowy knight", 1)),
        "Snowy knight",
        _req(("Butterfly jar", 1)),
        HUNTER_BUTTERFLY_SOURCE,
        HUNTER_BUTTERFLY_SOURCE,
        source_item_id=10016,
        deterministic=True,
        sort_order=30,
    ),
    _target(
        "catch_black_warlock",
        "Catch black warlock",
        "butterfly_netting",
        45,
        54.0,
        _out(("Black warlock", 1)),
        "Black warlock",
        _req(("Butterfly jar", 1)),
        HUNTER_BUTTERFLY_SOURCE,
        HUNTER_BUTTERFLY_SOURCE,
        source_item_id=10014,
        deterministic=True,
        sort_order=40,
    ),
    _target(
        "barehand_ruby_harvest",
        "Catch ruby harvest barehanded",
        "barehanded_butterflies",
        80,
        300.0,
        (),
        "Ruby harvest",
        skill_requirements=(('agility', 75),),
        xp_rewards=(('hunter', 300.0), ('agility', 50.0)),
        source=HUNTER_BUTTERFLY_SOURCE,
        mechanics_source="period barehanded-butterfly reward table; success roll uses the labeled Hunter fallback",
        source_item_id=10020,
        rate1=128,
        rate99=230,
        tradeable=False,
        notes="No net, jar, or retained butterfly. Requires 75 Agility.",
        sort_order=10,
    ),
    _target(
        "barehand_sapphire_glacialis",
        "Catch sapphire glacialis barehanded",
        "barehanded_butterflies",
        85,
        400.0,
        (),
        "Sapphire glacialis",
        skill_requirements=(('agility', 80),),
        xp_rewards=(('hunter', 400.0), ('agility', 70.0)),
        source=HUNTER_BUTTERFLY_SOURCE,
        mechanics_source="period barehanded-butterfly reward table; success roll uses the labeled Hunter fallback",
        source_item_id=10018,
        rate1=128,
        rate99=230,
        tradeable=False,
        notes="No net, jar, or retained butterfly. Requires 80 Agility.",
        sort_order=20,
    ),
    _target(
        "barehand_snowy_knight",
        "Catch snowy knight barehanded",
        "barehanded_butterflies",
        90,
        500.0,
        (),
        "Snowy knight",
        skill_requirements=(('agility', 85),),
        xp_rewards=(('hunter', 500.0), ('agility', 100.0)),
        source=HUNTER_BUTTERFLY_SOURCE,
        mechanics_source="period barehanded-butterfly reward table; success roll uses the labeled Hunter fallback",
        source_item_id=10016,
        rate1=128,
        rate99=230,
        tradeable=False,
        notes="No net, jar, or retained butterfly. Requires 85 Agility.",
        sort_order=30,
    ),
    _target(
        "barehand_black_warlock",
        "Catch black warlock barehanded",
        "barehanded_butterflies",
        95,
        650.0,
        (),
        "Black warlock",
        skill_requirements=(('agility', 90),),
        xp_rewards=(('hunter', 650.0), ('agility', 125.0)),
        source=HUNTER_BUTTERFLY_SOURCE,
        mechanics_source="period barehanded-butterfly reward table; success roll uses the labeled Hunter fallback",
        source_item_id=10014,
        rate1=128,
        rate99=230,
        tradeable=False,
        notes="No net, jar, or retained butterfly. Requires 90 Agility.",
        sort_order=40,
    ),
    _target(
        "catch_wild_kebbit",
        "Catch wild kebbit",
        "deadfall",
        23,
        128.0,
        _out(_BONES, ("Kebbit claws", 1)),
        "Kebbit claws",
        _req(("Logs", 1)),
        HUNTER_DEADFALL_SOURCE,
        BOX_HUNTER_TYPE_SOURCE,
        "WILD_KEBBIT",
        5089,
        rate1=128,
        rate99=256,
        sort_order=10,
    ),
    _target(
        "catch_barb_tailed_kebbit",
        "Catch barb-tailed kebbit",
        "deadfall",
        33,
        168.0,
        _out(_BONES, ("Barb-tail harpoon", 1)),
        "Barb-tail harpoon",
        _req(("Logs", 1)),
        HUNTER_DEADFALL_SOURCE,
        BOX_HUNTER_TYPE_SOURCE,
        "BARB_TAILED_KEBBIT",
        5088,
        rate1=110,
        rate99=256,
        sort_order=20,
    ),
    _target(
        "catch_prickly_kebbit",
        "Catch prickly kebbit",
        "deadfall",
        37,
        204.0,
        _out(_BONES, ("Kebbit spike", 1)),
        "Kebbit spike",
        _req(("Logs", 1)),
        HUNTER_DEADFALL_SOURCE,
        BOX_HUNTER_TYPE_SOURCE,
        "PRICKLY_KEBBIT",
        5086,
        rate1=100,
        rate99=240,
        sort_order=30,
    ),
    _target(
        "catch_sabre_toothed_kebbit",
        "Catch sabre-toothed kebbit",
        "deadfall",
        51,
        200.0,
        _out(_BONES, ("Kebbit teeth", 1)),
        "Kebbit teeth",
        _req(("Logs", 1)),
        HUNTER_DEADFALL_SOURCE,
        BOX_HUNTER_TYPE_SOURCE,
        "SABRE_TOOTHED_KEBBIT",
        5087,
        rate1=80,
        rate99=220,
        sort_order=40,
    ),
    _target(
        "catch_ferret",
        "Catch ferret",
        "box_trapping",
        27,
        115.2,
        _out(("Ferret", 1)),
        "Ferret",
        source=HUNTER_BOX_TRAPPING_SOURCE,
        source_enum="FERRET",
        source_npc_id=5081,
        source_item_id=10092,
        rate1=128,
        rate99=256,
        sort_order=10,
    ),
    _target(
        "catch_chinchompa",
        "Catch chinchompa",
        "box_trapping",
        53,
        198.5,
        _out(("Chinchompa", 1)),
        "Chinchompa",
        source=HUNTER_BOX_TRAPPING_SOURCE,
        source_enum="CHINCHOMPA",
        source_npc_id=5079,
        source_item_id=10033,
        rate1=95,
        rate99=220,
        sort_order=20,
    ),
    _target(
        "catch_red_chinchompa",
        "Catch red chinchompa",
        "box_trapping",
        63,
        265.0,
        _out(("Red chinchompa", 1)),
        "Red chinchompa",
        source=HUNTER_BOX_TRAPPING_SOURCE,
        source_enum="CARNIVOROUS_CHINCHOMPA",
        source_npc_id=5080,
        source_item_id=10034,
        rate1=75,
        rate99=200,
        sort_order=30,
    ),
    _target(
        "catch_pawya",
        "Catch pawya",
        "box_trapping",
        66,
        400.0,
        _out(_BONES, ("Raw pawya meat", 1)),
        "Raw pawya meat",
        source=HUNTER_BOX_TRAPPING_SOURCE,
        source_enum="PAWYA",
        source_npc_id=7012,
        source_item_id=12535,
        rate1=70,
        rate99=190,
        notes="Regicide-start route access is documented but not represented by the current quest-completion gate model.",
        sort_order=40,
    ),
    _target(
        "catch_cannibal_jadinko",
        "Catch cannibal jadinko",
        "box_trapping",
        75,
        475.0,
        _out(("Plant teeth", 1)),
        "Plant teeth",
        source=f"{HERBLORE_HABITAT_JADINKO_SOURCES['catch_cannibal_jadinko']}; {HERBLORE_HABITAT_SOURCE}",
        mechanics_source=(f"{DARKAN_HERBLORE_HABITAT_SOURCE_ROOT}data/npcs/drops/hunter/" "hunter_jadinko_cannibal.json"),
        source_enum="CANNIBAL_JADINKO",
        source_npc_id=13155,
        source_item_id=19975,
        rate1=HERBLORE_HABITAT_RATE1,
        rate99=HERBLORE_HABITAT_RATE99,
        tradeable=False,
        notes=("Cannibal jadinko oldid 5976665 pins level 75, 475 XP, Marasamaw plant trapping, Plant teeth, and the green-blossom, Kalferberry, tall-grass, Juju-treated Habitat setup. Persistent setup and optional bait are route context, not per-catch consumables."),
        sort_order=50,
    ),
    _target(
        "catch_guthix_jadinko",
        "Catch Guthix jadinko",
        "box_trapping",
        81,
        600.0,
        _out(("Guthix vine", 1)),
        "Guthix vine",
        source=f"{HERBLORE_HABITAT_JADINKO_SOURCES['catch_guthix_jadinko']}; {HERBLORE_HABITAT_SOURCE}",
        mechanics_source=(f"{DARKAN_HERBLORE_HABITAT_SOURCE_ROOT}data/npcs/drops/hunter/" "hunter_jadinko_guthix.json"),
        source_enum="GUTHIX_JADINKO",
        source_npc_id=13164,
        source_item_id=19982,
        rate1=HERBLORE_HABITAT_RATE1,
        rate99=HERBLORE_HABITAT_RATE99,
        tradeable=False,
        notes=("Guthix jadinko oldid 6167443 pins level 81, 600 XP, Marasamaw plant trapping, Guthix vine, a Juju-treated flower patch, and weekly player-specific preferences. Persistent setup and optional bait are route context, not per-catch consumables."),
        sort_order=60,
    ),
    _target(
        "catch_grenwall",
        "Catch grenwall",
        "box_trapping",
        77,
        1100.0,
        _out(_BONES, ("Grenwall spikes", 18)),
        "Grenwall spikes",
        source=HUNTER_BOX_TRAPPING_SOURCE,
        source_enum="GRENWALL",
        source_npc_id=7010,
        source_item_id=12539,
        rate1=60,
        rate99=180,
        notes="Source drop range is 18-21 spikes plus optional herbs; AnkiScape awards the guaranteed minimum.",
        sort_order=50,
    ),
    _target(
        "catch_swamp_lizard",
        "Catch swamp lizard",
        "net_trapping",
        29,
        152.0,
        _out(("Swamp lizard", 1)),
        "Swamp lizard",
        source=HUNTER_NET_TRAPPING_SOURCE,
        source_enum="SWAMP_LIZARD",
        source_npc_id=5117,
        source_item_id=10149,
        rate1=128,
        rate99=256,
        sort_order=10,
    ),
    _target(
        "catch_orange_salamander",
        "Catch orange salamander",
        "net_trapping",
        47,
        224.0,
        _out(("Orange salamander", 1)),
        "Orange salamander",
        source=HUNTER_NET_TRAPPING_SOURCE,
        source_enum="ORANGE_SALAMANDER",
        source_npc_id=5114,
        source_item_id=10146,
        rate1=100,
        rate99=240,
        sort_order=20,
    ),
    _target(
        "catch_red_salamander",
        "Catch red salamander",
        "net_trapping",
        59,
        272.0,
        _out(("Red salamander", 1)),
        "Red salamander",
        source=HUNTER_NET_TRAPPING_SOURCE,
        source_enum="RED_SALAMANDER",
        source_npc_id=5115,
        source_item_id=10147,
        rate1=80,
        rate99=220,
        sort_order=30,
    ),
    _target(
        "catch_black_salamander",
        "Catch black salamander",
        "net_trapping",
        67,
        319.2,
        _out(("Black salamander", 1)),
        "Black salamander",
        source=HUNTER_NET_TRAPPING_SOURCE,
        source_enum="BLACK_SALAMANDER",
        source_npc_id=5116,
        source_item_id=10148,
        rate1=70,
        rate99=200,
        notes="2011.rs lists 304 XP; the Darkan implementation uses 319.2 XP.",
        sort_order=40,
    ),
    _target(
        "catch_spotted_kebbit",
        "Catch spotted kebbit",
        "falconry",
        43,
        42.0,
        _out(_BONES, ("Spotted kebbit fur", 1)),
        "Spotted kebbit fur",
        source=FALCONRY_KEBBIT_SOURCE,
        mechanics_source=FALCONRY_KEBBIT_SOURCE,
        source_enum="SPOTTED",
        source_npc_id=5098,
        source_item_id=10125,
        deterministic=True,
        sort_order=10,
    ),
    _target(
        "catch_dark_kebbit",
        "Catch dark kebbit",
        "falconry",
        57,
        99.0,
        _out(_BONES, ("Dark kebbit fur", 1)),
        "Dark kebbit fur",
        source=FALCONRY_KEBBIT_SOURCE,
        mechanics_source=FALCONRY_KEBBIT_SOURCE,
        source_enum="DARK",
        source_npc_id=5099,
        source_item_id=10115,
        deterministic=True,
        sort_order=20,
    ),
    _target(
        "catch_dashing_kebbit",
        "Catch dashing kebbit",
        "falconry",
        69,
        156.0,
        _out(_BONES, ("Dashing kebbit fur", 1)),
        "Dashing kebbit fur",
        source=FALCONRY_KEBBIT_SOURCE,
        mechanics_source=FALCONRY_KEBBIT_SOURCE,
        source_enum="DASHING",
        source_npc_id=5100,
        source_item_id=10127,
        deterministic=True,
        sort_order=30,
    ),
    _target(
        "catch_imp_magic_box",
        "Catch imp with magic box",
        "magic_box",
        71,
        450.0,
        _out(("Imp-in-a-box (2)", 1)),
        "Imp-in-a-box (2)",
        _req(("Magic box", 1)),
        HUNTER_MAGIC_BOX_SOURCE,
        BOX_HUNTER_TYPE_SOURCE,
        "IMP",
        708,
        10027,
        rate1=70,
        rate99=220,
        sort_order=10,
    ),
)

_IMPLINGS = (
    ("baby", "Baby", 17, 20.0, 25.0, 11238, 1028),
    ("young", "Young", 22, 48.0, 65.0, 11240, 1029),
    ("gourmet", "Gourmet", 28, 82.0, 113.0, 11242, 1030),
    ("earth", "Earth", 36, 126.0, 177.0, 11244, 1031),
    ("essence", "Essence", 42, 160.0, 225.0, 11246, 1032),
    ("eclectic", "Eclectic", 50, 205.0, 289.0, 11248, 1033),
    ("spirit", "Spirit", 54, 227.0, 321.0, 15513, 7866),
    ("nature", "Nature", 58, 250.0, 353.0, 11250, 1034),
    ("magpie", "Magpie", 65, 289.0, 409.0, 11252, 1035),
    ("ninja", "Ninja", 74, 339.0, 481.0, 11254, 6053),
    ("pirate", "Pirate", 76, 350.0, 497.0, 13337, 7845),
    ("dragon", "Dragon", 83, 390.0, 553.0, 11256, 6054),
    ("zombie", "Zombie", 87, 412.0, 585.0, 15515, 7902),
    ("kingly", "Kingly", 91, 434.0, 617.0, 15517, 7903),
)


def _impling_jar_name(label: str) -> str:
    return {
        "Gourmet": "Gourm' impling jar",
        "Essence": "Ess' impling jar",
    }.get(label, f"{label} impling jar")


HUNTER_TARGETS += tuple(
    _target(
        f"catch_{slug}_impling_puro_puro",
        f"Catch {label.lower()} impling (Puro-Puro)",
        "impling_puro_puro",
        level,
        maze_xp,
        _out((_impling_jar_name(label), 1)),
        _impling_jar_name(label),
        _req(("Impling jar", 1)),
        HUNTER_BUTTERFLY_SOURCE,
        FLYING_ENTITY_SOURCE,
        label.upper(),
        npc_id,
        item_id,
        rate1=110,
        rate99=256,
        sort_order=index * 10,
    )
    for index, (slug, label, level, maze_xp, _world_xp, item_id, npc_id) in enumerate(_IMPLINGS, start=1)
)

HUNTER_TARGETS += tuple(
    _target(
        f"catch_{slug}_impling_world",
        f"Catch {label.lower()} impling (world)",
        "impling_world",
        level,
        world_xp,
        _out((_impling_jar_name(label), 1)),
        _impling_jar_name(label),
        _req(("Impling jar", 1)),
        HUNTER_BUTTERFLY_SOURCE,
        FLYING_ENTITY_SOURCE,
        label.upper(),
        npc_id,
        item_id,
        rate1=95,
        rate99=230,
        sort_order=index * 10,
    )
    for index, (slug, label, level, _maze_xp, world_xp, item_id, npc_id) in enumerate(_IMPLINGS, start=1)
)

HUNTER_TARGETS_BY_ID: Dict[str, HunterTarget] = {target.id: target for target in HUNTER_TARGETS}

HUNTER_MATERIAL_ITEMS: Mapping[str, int] = {
    "Butterfly jar": 10012,
    "Impling jar": 11260,
    "Magic box": 10025,
}

HUNTER_TOOL_ITEMS: Mapping[str, int] = {
    "Bird snare": 10006,
    "Box trap": 10008,
    "Butterfly net": 10010,
    "Noose wand": 10150,
    "Teasing stick": 10029,
    "Rabbit snare": 10031,
    "Small fishing net": 303,
    "Rope": 954,
}

HUNTER_EXTRA_ITEM_IDS: Mapping[str, int] = {
    "Bones": 526,
    "Raw bird meat": 9978,
    "Red feather": 10088,
    "Yellow feather": 10090,
    "Orange feather": 10091,
    "Blue feather": 10089,
    "Stripy feather": 10087,
    "Wimpy feather": 11525,
    "Plant teeth": 19975,
    "Shadow vine": 19977,
    "Corrupt vine": 19979,
    "Guthix vine": 19982,
    **HUNTER_MATERIAL_ITEMS,
    **HUNTER_TOOL_ITEMS,
}


def _target_as_dict(target: HunterTarget) -> Dict[str, object]:
    return {
        "id": target.id,
        "display_name": target.display_name,
        "group": target.group,
        "level": target.level,
        "exp": target.base_exp,
        "base_exp": target.base_exp,
        "requirements": dict(target.requirements),
        "skill_requirements": dict(target.skill_requirements),
        "tools": dict(target.tools),
        "outputs": dict(target.outputs),
        "output_item": target.primary_output,
        "output_qty": dict(target.outputs).get(target.primary_output, 1),
        "primary_output": target.primary_output,
        "xp_rewards": tuple(
            {"skill_id": skill_id, "amount": amount}
            for skill_id, amount in (
                target.xp_rewards or (("hunter", target.base_exp),)
            )
        ),
        "source": target.source,
        "mechanics_source": target.mechanics_source,
        "source_enum": target.source_enum,
        "source_npc_id": target.source_npc_id,
        "source_item_id": target.source_item_id,
        "rate1": target.rate1,
        "rate99": target.rate99,
        "deterministic": target.deterministic,
        "tradeable": target.tradeable,
        "notes": target.notes,
        "sort_key": (_GROUP_SORT.get(target.group, 999), target.sort_order, target.level, target.display_name),
    }


def hunter_targets_as_dict() -> Dict[str, Dict[str, object]]:
    return {target.id: _target_as_dict(target) for target in HUNTER_TARGETS}


def hunter_output_items() -> Tuple[str, ...]:
    seen: Dict[str, None] = {}
    for target in HUNTER_TARGETS:
        for item_name, _amount in target.outputs:
            seen.setdefault(item_name, None)
    return tuple(seen.keys())


def hunter_item_names() -> Tuple[str, ...]:
    seen: Dict[str, None] = {}
    for target in HUNTER_TARGETS:
        for item_name, _amount in target.outputs:
            seen.setdefault(item_name, None)
        for material, _amount in target.requirements:
            seen.setdefault(material, None)
        for tool, _amount in target.tools:
            seen.setdefault(tool, None)
    for item_name, _amount in HUNTER_SUPPLY_BUNDLE:
        seen.setdefault(item_name, None)
    return tuple(seen.keys())


def hunter_supply_item_names() -> Tuple[str, ...]:
    return tuple(item_name for item_name, _amount in HUNTER_SUPPLY_BUNDLE)


# The temporary `buy_hunter_supplies` Utility bridge was retired on 2026-07-06:
# every bundle item is individually live NPC shop stock at real cache prices
# (Aleck's Hunter Emporium, Elnock's Backup Supply, net/rope shops), so the
# flat-price bundle no longer earns its keep. HUNTER_SUPPLY_BUNDLE stays as the
# item-registration manifest for that gear.


def _hunter_extra_category(item_name: str) -> str:
    if item_name in HUNTER_TOOL_ITEMS:
        return "tool"
    if item_name in HUNTER_MATERIAL_ITEMS:
        return "material"
    return "hunter"


def _hunter_extra_source(item_name: str) -> str:
    jadinko_sources = {
        "Corrupt vine": HERBLORE_HABITAT_JADINKO_SOURCES["track_diseased_jadinko"],
        "Guthix vine": HERBLORE_HABITAT_JADINKO_SOURCES["catch_guthix_jadinko"],
        "Shadow vine": HERBLORE_HABITAT_JADINKO_SOURCES["track_shadow_jadinko"],
        "Plant teeth": HERBLORE_HABITAT_JADINKO_SOURCES["catch_cannibal_jadinko"],
    }
    if item_name in jadinko_sources:
        return jadinko_sources[item_name]
    if item_name == "Impling jar":
        return HUNTER_IMPLING_JAR_SHOP_SOURCE
    if item_name == "Small fishing net":
        return HUNTER_SMALL_NET_SHOP_SOURCE
    if item_name == "Rope":
        return HUNTER_ROPE_SHOP_SOURCE
    if item_name in HUNTER_TOOL_ITEMS or item_name in HUNTER_MATERIAL_ITEMS:
        return HUNTER_SUPPLY_SHOP_SOURCE
    return BOX_HUNTER_TYPE_SOURCE


def hunter_extra_items_as_dict() -> Dict[str, Dict[str, object]]:
    rows: Dict[str, Dict[str, object]] = {}
    for item_name, item_id in HUNTER_EXTRA_ITEM_IDS.items():
        rows[item_name] = {
            "category": _hunter_extra_category(item_name),
            "level": 1,
            "exp": 0.0,
            "source": _hunter_extra_source(item_name),
            "item_id": item_id,
            "tradeable": item_name not in {"Corrupt vine", "Guthix vine", "Shadow vine", "Plant teeth"},
            "stackable": item_name != "Rope",
        }
    return rows
