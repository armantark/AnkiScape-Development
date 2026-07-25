"""Data contracts for the complete pre-EOC Agility surface."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from ..data.firemaking_data import LIT_LIGHT_SOURCE_ITEMS
from ..data.flash_powder_factory_data import (
    FLASH_POWDER_FACTORY_ACTIVITY_ID,
)


_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class AgilityStage:
    id: str
    label: str
    xp: float
    can_fail: bool = False
    fail_profile: str = "default"
    failure_damage: Optional[int] = None
    position_result: str = "stay/retry"
    xp_on_fail: float = 0.0
    output_item: Optional[str] = None
    output_qty: int = 0
    cross_skill_rewards: Tuple[Tuple[str, float], ...] = ()


@dataclass(frozen=True)
class AgilityTarget:
    id: str
    display_name: str
    group: str
    level: int
    stages: Tuple[AgilityStage, ...]
    completion_bonus: float = 0.0
    quest_gate: Optional[str] = None
    required_items: Tuple[str, ...] = ()
    required_item_options: Tuple[Tuple[str, ...], ...] = ()
    source_status: str = "period"
    activity_kind: Optional[str] = None


@dataclass(frozen=True)
class AgilityShortcut:
    id: str
    display_name: str
    level: int
    xp: Optional[float]
    consumer: str = "milestone"
    other_skill_requirements: Tuple[Tuple[str, int], ...] = ()
    quest_gate: str = ""
    required_items: Tuple[str, ...] = ()
    hidey_hole_materials: Tuple[Tuple[str, int], ...] = ()
    xp_on_fail: Optional[float] = None
    source_status: str = "period"
    notes: str = ""


@dataclass(frozen=True)
class DorgeshRouteOption:
    id: str
    display_name: str
    agility_xp: Optional[float]
    ranged_xp: Optional[float] = None
    active: bool = False
    source_status: str = "source_blocked"
    notes: str = ""


def _stage(
    stage_id: str,
    label: str,
    xp: float,
    *,
    can_fail: bool = False,
    fail_profile: str = "default",
    failure_damage: Optional[int] = None,
    position_result: str = "stay/retry",
    xp_on_fail: float = 0.0,
    output_item: Optional[str] = None,
    output_qty: int = 0,
    cross_skill_rewards: Tuple[Tuple[str, float], ...] = (),
) -> AgilityStage:
    return AgilityStage(
        stage_id,
        label,
        xp,
        can_fail,
        fail_profile,
        failure_damage,
        position_result,
        xp_on_fail,
        output_item,
        output_qty,
        cross_skill_rewards,
    )


GNOME_TRUNK = (
    _stage("log_balance", "Cross the log balance", 7.5),
    _stage("obstacle_net_up", "Climb the obstacle net", 7.5),
    _stage("tree_branch_up", "Climb the tree branch", 5.0),
)

BARBARIAN_TRUNK = (
    _stage("rope_swing", "Swing across the rope", 22.0, can_fail=True, fail_profile="barbarian", position_result="checkpoint"),
    _stage("log_balance", "Cross the log balance", 13.7, can_fail=True, fail_profile="barbarian"),
)


def _pyramid_stages() -> Tuple[AgilityStage, ...]:
    definitions = (
        ("rolling_block", "Pass a rolling block", 12.0, 5, 60),
        ("low_wall", "Climb a low wall", 8.0, 4, 40),
        ("moving_block", "Pass the moving blocks", 0.0, 2, 80),
        ("ledge", "Cross a ledge", 52.0, 4, 100),
        ("plank", "Cross a plank", 56.4, 2, 100),
        ("cross_gap", "Cross a gap", 56.4, 3, 80),
        ("jump_gap", "Jump a gap", 22.0, 6, 80),
        ("stairs", "Climb to the next floor", 0.0, 5, None),
    )
    stages = []
    for kind, label, xp, count, damage in definitions:
        for index in range(1, count + 1):
            stages.append(
                _stage(
                    f"{kind}_{index}",
                    label,
                    xp,
                    can_fail=damage is not None,
                    fail_profile=f"pyramid:{kind}",
                    failure_damage=damage,
                    position_result="lower_floor" if damage is not None else "stay/retry",
                )
            )
    return tuple(stages)


COURSE_TARGETS: Tuple[AgilityTarget, ...] = (
    AgilityTarget(
        "burthorpe_course", "Burthorpe Agility Course", "courses", 1,
        (
            _stage("log_beam", "Walk the log beam", 5.5, can_fail=True, fail_profile="burthorpe"),
            _stage("wall", "Climb the wall", 5.5),
            _stage("ledge", "Cross the balancing ledge", 5.5),
            _stage("low_wall", "Climb the low wall", 5.5, can_fail=True, fail_profile="burthorpe"),
            _stage("rope_swing", "Swing across the rope", 5.5),
            _stage("monkey_bars", "Cross the monkey bars", 5.5),
            _stage("leap_of_faith", "Take the Leap of Faith", 46.5),
        ),
    ),
    AgilityTarget(
        "gnome_normal", "Gnome Stronghold Course", "courses", 1,
        GNOME_TRUNK + (
            _stage("balancing_rope", "Cross the balancing rope", 7.5),
            _stage("tree_branch_down", "Climb down the tree branch", 5.0),
            _stage("obstacle_net_down", "Climb the obstacle net", 7.5),
            _stage("obstacle_pipe", "Squeeze through the pipe", 7.5),
        ),
        completion_bonus=39.0,
    ),
    AgilityTarget(
        "gnome_advanced", "Gnome Advanced Course", "courses", 85,
        GNOME_TRUNK + (
            _stage("advanced_tree", "Climb the advanced tree", 25.0),
            _stage("signpost", "Run across the signpost", 25.0, can_fail=True, fail_profile="gnome_advanced", failure_damage=70, position_result="cross"),
            _stage("pole", "Swing from the pole", 25.0),
            _stage("barrier", "Cross the barrier", 25.0),
        ),
        completion_bonus=605.0,
    ),
    AgilityTarget(
        "barbarian_normal", "Barbarian Outpost Course", "courses", 35,
        BARBARIAN_TRUNK + (
            _stage("obstacle_net", "Climb the obstacle net", 8.2),
            _stage("balancing_ledge", "Cross the balancing ledge", 22.0, can_fail=True, fail_profile="barbarian", position_result="checkpoint"),
            _stage("wall_one", "Climb the first crumbling wall", 13.7),
            _stage("wall_two", "Climb the second crumbling wall", 13.7),
        ),
        completion_bonus=46.2,
        quest_gate="bar_crawl",
        source_status="period_gate_dependency",
    ),
    AgilityTarget(
        "barbarian_advanced", "Barbarian Advanced Course", "courses", 90,
        BARBARIAN_TRUNK + tuple(
            _stage(stage_id, label, 15.0, can_fail=stage_id in {"wall_run", "balance_beam"}, fail_profile="barbarian")
            for stage_id, label in (
                ("wall_run", "Run up the wall"),
                ("wall_climb", "Climb the wall"),
                ("spring_device", "Fire the spring device"),
                ("balance_beam", "Cross the balance beam"),
                ("roof_gap", "Jump the roof gap"),
                ("roof_slide", "Slide down the roof"),
            )
        ),
        completion_bonus=615.0,
        quest_gate="bar_crawl",
        source_status="period_gate_dependency",
    ),
    AgilityTarget(
        "wilderness_course", "Wilderness Agility Course", "courses", 53,
        (
            _stage("access_walkway", "Cross the Wilderness walkway", 15.0, can_fail=True, fail_profile="default", position_result="checkpoint"),
            _stage("pipe", "Squeeze through the obstacle pipe", 12.5),
            _stage("rope_swing", "Swing across the rope", 20.0, can_fail=True, fail_profile="wilderness", position_result="lower_floor"),
            _stage("stepping_stones", "Cross the stepping stones", 20.0, can_fail=True, fail_profile="wilderness_stones", position_result="lower_floor"),
            _stage("log_balance", "Cross the log balance", 20.0, can_fail=True, fail_profile="wilderness", position_result="lower_floor"),
            _stage("rocks", "Climb the rocks", 0.0),
        ),
        completion_bonus=499.0,
    ),
    AgilityTarget(
        "agility_pyramid", "Agility Pyramid", "courses", 30,
        _pyramid_stages() + (_stage("retrieve_top", "Retrieve the Pyramid top", 0.0, output_item="Pyramid top", output_qty=1),),
        completion_bonus=300.0,
        source_status="period_route_abstraction",
    ),
    AgilityTarget(
        "ape_atoll", "Ape Atoll Agility Course", "courses", 48,
        (
            _stage("stepping_stone", "Jump to the stepping stone", 40.0),
            _stage("tropical_tree", "Climb the tropical tree", 40.0),
            _stage("monkeybars", "Swing across the monkeybars", 40.0),
            _stage("skull_slope", "Climb the skull slope", 60.0),
            _stage("rope", "Swing across the rope", 100.0),
            _stage("climb_down", "Climb down the tropical tree", 100.0, can_fail=True, fail_profile="ape_atoll", position_result="checkpoint"),
        ),
        # The period table's final row is 100 XP in isolation or 300 XP total
        # when the ordered course is valid. The incremental lap award is 200,
        # which keeps the sourced six-stage lap total at 580 XP.
        completion_bonus=200.0,
        quest_gate="monkey_madness",
        required_items=("Small ninja monkey greegree",),
    ),
    AgilityTarget(
        "werewolf_course", "Werewolf Agility Course", "courses", 60,
        (
            _stage("stepping_stones", "Cross the stepping stones", 50.0),
            _stage("hurdles", "Jump the hurdles", 60.0),
            _stage("pipe", "Squeeze through the pipe", 15.0),
            _stage("skull_slope", "Climb the skull slope", 25.0),
            _stage("deathslide", "Take the deathslide", 200.0, can_fail=True, fail_profile="werewolf", position_result="end_partial", xp_on_fail=180.0),
            _stage("stick_hand_in", "Return the fetched stick", 190.0),
        ),
        quest_gate="creature_of_fenkenstrain",
        required_items=("Ring of charos",),
    ),
    AgilityTarget(
        "dorgesh_kaan", "Dorgesh-Kaan Agility Course", "courses", 80,
        tuple(
            _stage(f"out_{index}", label, xp, can_fail=kind in {"cable", "ladder"}, fail_profile="dorgesh", failure_damage=100, position_result="lower_floor")
            for index, (kind, label, xp) in enumerate((
                ("cable", "Balance across the cable", 25.0), ("cable", "Swing across the cable", 22.0),
                ("ladder", "Swing across the ladder", 25.0), ("cable", "Swing across the cable", 22.0),
                ("wall", "Squeeze past the wall", 7.5), ("tunnel", "Squeeze through the tunnel", 7.5),
                ("cable", "Balance across the cable", 25.0), ("ladder", "Swing across the ladder", 25.0),
            ), 1)
        )
        + (_stage("retrieve_part", "Retrieve the requested generator part", 0.0),)
        + tuple(
            _stage(f"return_{index}", label, xp, can_fail=kind in {"cable", "ladder"}, fail_profile="dorgesh", failure_damage=100, position_result="invalidate_item")
            for index, (kind, label, xp) in enumerate((
                ("ladder", "Swing across the ladder", 25.0), ("cable", "Balance across the cable", 25.0),
                ("tunnel", "Squeeze through the tunnel", 7.5), ("wall", "Squeeze past the wall", 7.5),
                ("cable", "Swing across the cable", 22.0), ("ladder", "Swing across the ladder", 25.0),
                ("cable", "Swing across the cable", 22.0), ("cable", "Balance across the cable", 25.0),
            ), 1)
        )
        + (_stage("hand_in", "Hand the generator part to Turgall", 2057.0),),
        quest_gate="death_to_the_dorgeshuun",
        required_item_options=(LIT_LIGHT_SOURCE_ITEMS,),
    ),
    AgilityTarget(
        "penguin_course", "Penguin Agility Course", "courses", 30,
        (
            _stage("ice_crushers", "Pass the ice crushers", 55.0, can_fail=True, fail_profile="penguin"),
            _stage("platforms", "Complete the platform jumps", 80.0, can_fail=True, fail_profile="penguin"),
            _stage("icicles", "Tread softly through the icicles", 160.0, can_fail=True, fail_profile="penguin"),
            _stage("ice_slope", "Cross the ice slope", 180.0, can_fail=True, fail_profile="penguin"),
        ),
        completion_bonus=65.0,
        quest_gate="cold_war",
        required_items=("Penguin suit",),
    ),
    AgilityTarget(
        "brimhaven_arena", "Brimhaven Agility Arena", "courses", 1, (),
        source_status="accepted_abstraction", activity_kind="brimhaven",
    ),
    AgilityTarget(
        "bandos_throne_room", "Bandos's Throne Room Course", "courses", 60,
        tuple(_stage(f"statue_{index}", "Jump between the statues", 2.0, can_fail=True, fail_profile="default") for index in range(1, 10))
        + (_stage("grapple", "Grapple to the throne-room ledge", 362.0, cross_skill_rewards=(("ranged", 125.0), ("strength", 125.0))),),
        quest_gate="the_chosen_commander",
        required_items=("Mith grapple", "Crossbow"),
        source_status="period_candidate",
    ),
)


ACTIVITY_TARGETS: Tuple[AgilityTarget, ...] = (
    AgilityTarget("werewolf_skullball", "Werewolf Skullball", "activities", 25, (), quest_gate="creature_of_fenkenstrain", required_items=("Ring of charos",), source_status="period_candidate", activity_kind="skullball"),
    AgilityTarget("gnome_ball", "Gnome Ball", "activities", 1, (), source_status="period_candidate", activity_kind="gnome_ball"),
    AgilityTarget("flash_powder_factory", "Flash Powder Factory", "activities", 75, (), source_status="period_candidate", activity_kind="flash_powder_factory"),
    AgilityTarget("the_pit", "The Pit", "activities", 1, (), source_status="period_candidate", activity_kind="pit"),
)

AGILITY_TARGETS: Tuple[AgilityTarget, ...] = COURSE_TARGETS + tuple(
    target
    for target in ACTIVITY_TARGETS
    if target.id
    not in {
        FLASH_POWDER_FACTORY_ACTIVITY_ID,
        "werewolf_skullball",
        "gnome_ball",
    }
)
AGILITY_TARGETS_BY_ID = {
    target.id: target for target in COURSE_TARGETS + ACTIVITY_TARGETS
}
DEFAULT_AGILITY_TARGET = "burthorpe_course"


BRIMHAVEN_OBSTACLES = (
    ("low_wall", "Low wall", 1, 8.0, 0.05),
    ("rope_swing", "Rope swing", 1, 20.0, 0.40),
    ("log_balance", "Log balance", 1, 12.0, 0.10),
    ("ledge", "Ledge", 1, 16.0, 0.10),
    ("plank", "Safe plank", 1, 6.0, 0.0),
    ("pillars", "Pillars", 1, 18.0, 0.50),
    ("monkey_bars", "Monkey bars", 1, 14.0, 0.20),
    ("rope_balance", "Rope balance", 1, 10.0, 0.45),
    ("sawblade", "Sawblade", 1, 0.0, 0.0),
    ("spiked_floor", "Spiked floor", 20, 24.0, 0.20),
    ("pressure_pads", "Pressure pads", 20, 26.0, 0.40),
    ("hand_holds", "Hand-holds", 20, 22.0, 0.30),
    ("spinning_blades", "Spinning blades", 40, 28.0, 0.30),
    ("darts", "Darts", 40, 30.0, 0.20),
)

BRIMHAVEN_XP_EXCHANGES = {1: 240.0, 10: 2480.0, 25: 6500.0, 100: 28000.0, 1000: 320000.0}
BRIMHAVEN_ITEM_EXCHANGES = {3: "Grimy toadflax", 5: "Grimy wergali", 10: "Grimy snapdragon", 800: "Pirate's hook"}


FPF_OBJECTIVES = ("Collect reagent A", "Collect reagent B", "Obtain catalyst", "Mix the powder", "Deposit the mixture")
PIT_CHALLENGES = ("Crate Expectations", "Floor Is Lava", "High-low", "Karaoke", "Hungry Sheep", "Block matching")
# Keep all three period route identities. Only the fully sourced pure-Agility
# route is executable; the grapple reward split is not guessed.
DORGESH_ROUTE_OPTIONS = (
    DorgeshRouteOption("pure", "Pure Agility route", 2375.0, active=True, source_status="period"),
    DorgeshRouteOption(
        "grapple",
        "Grapple route",
        None,
        notes="Requires the Dorgesh crossbow/grapple route; exact period payout is unresolved.",
    ),
    DorgeshRouteOption(
        "mixed",
        "Mixed Agility/grapple route",
        None,
        notes="Reserved for an atomic Agility/Ranged route when the period payout is resolved.",
    ),
)

def _shortcut(stable_id: str, name: str, level: int, xp: Optional[float], *, consumer: str = "milestone", xp_on_fail: Optional[float] = None, source_status: str = "period", notes: str = "") -> AgilityShortcut:
    return AgilityShortcut(stable_id, name, level, xp, consumer=consumer, xp_on_fail=xp_on_fail, source_status=source_status, notes=notes)


# Complete freeze-date ordinary shortcut registry. Rows without a live route
# consumer remain derived milestones; they are never fake teleport actions.
AGILITY_SHORTCUTS = (
    _shortcut("freds_stile", "Fred the Farmer's stile", 1, 3.0, source_status="period_conflict", notes="Period tables conflict between 0 and 3 XP."),
    _shortcut("falador_stile", "Falador cabbage-patch stile", 1, 3.0, source_status="period_conflict", notes="Period tables conflict between 0 and 3 XP."),
    _shortcut("yanille_climbing_rocks", "Yanille climbing rocks", 5, 25.0),
    _shortcut("falador_crumbling_wall", "Falador crumbling wall", 5, 0.5),
    _shortcut("brimhaven_west_rope_swing", "West Brimhaven rope swing", 10, 3.0),
    _shortcut("brimhaven_stepping_stones", "Brimhaven Dungeon stepping stones", 12, 3.0),
    _shortcut("lumbridge_cellar_hole", "Lumbridge cellar small hole", 13, 0.0),
    _shortcut("edgeville_monkey_bars", "Edgeville Dungeon monkey bars", 15, 20.0),
    _shortcut("cairn_isle_rock_climb", "Cairn Isle rock climb", 15, 1.0),
    _shortcut("cairn_isle_bridge", "Cairn Isle bridge", 15, 10.0),
    _shortcut("death_plateau_rocks_15", "Trollheim and Death Plateau rocks", 15, None, source_status="source_blocked"),
    _shortcut("yanille_underwall", "Yanille underwall tunnel", 16, 0.0),
    _shortcut("watchtower_trellis", "Watchtower trellis", 18, 31.0, consumer="quest"),
    _shortcut("coal_trucks_log", "Coal Trucks balancing log", 20, 8.5, consumer="route"),
    _shortcut("grand_exchange_underwall", "Grand Exchange underwall tunnel", 21, 0.0),
    _shortcut("brimhaven_dungeon_pipe", "Brimhaven Dungeon pipe squeeze", 22, 8.5),
    _shortcut("desert_pyramid_rope", "Desert pyramid rope", 25, 0.0, consumer="quest"),
    _shortcut("eagles_peak_rock", "Eagles' Peak rock climb", 25, 1.0, consumer="quest"),
    _shortcut("falador_underwall", "Falador underwall tunnel", 26, 0.0),
    _shortcut("draynor_belladonna_fence", "Draynor belladonna fence", 28, 0.0, consumer="route"),
    _shortcut("ooglog_passage", "Oo'glog passage", 29, 0.0),
    _shortcut("brimhaven_red_dragon_stones", "Brimhaven red-dragon stepping stones", 30, 0.0),
    _shortcut("draynor_stepping_stones", "Draynor stepping stones", 31, 3.0, xp_on_fail=1.0),
    _shortcut("cairn_isle_rock_slide", "Cairn Isle rock slide", 32, 0.0),
    _shortcut("ardougne_balancing_log", "Ardougne balancing log", 33, 4.0, xp_on_fail=2.0),
    _shortcut("brimhaven_dragon_pipe", "Brimhaven red and black dragon pipe", 34, 10.0),
    _shortcut("grand_tree_fallen_tree", "Grand Tree fallen tree", 37, 0.0),
    _shortcut("al_kharid_mine_rocks", "Al Kharid mine rocks", 38, 0.0, consumer="route"),
    _shortcut("yanille_chaos_druid_ledge", "Yanille Dungeon Chaos-druid ledge", 40, 22.0),
    _shortcut("trollheim_rocks_41", "Trollheim rocks (level 41)", 41, 0.0),
    _shortcut("dwarven_mine_crevice", "Dwarven Mine crevice", 42, 0.0, consumer="route"),
    _shortcut("trollheim_rocks_43", "Trollheim rocks (level 43)", 43, 0.0),
    _shortcut("trollheim_rocks_44", "Trollheim rocks (level 44)", 44, 0.0),
    _shortcut("tirannwn_balancing_log", "Tirannwn balancing log", 45, 0.0),
    _shortcut("cosmic_walkway_basic", "Cosmic altar basic walkway", 46, 10.0, consumer="route"),
    _shortcut("trollheim_rocks_47", "Trollheim rocks (level 47)", 47, 0.0),
    _shortcut("camelot_fremennik_log", "Camelot to Fremennik balancing log", 48, 0.0),
    _shortcut("yanille_sinister_pipe", "Yanille Dungeon Sinister-chest pipe", 49, 0.0),
    _shortcut("grotworm_lair_slide", "Grotworm Lair slide", 50, 0.0),
    _shortcut("edgeville_varrock_pipe", "Varrock Sewers to Edgeville pipe", 51, 0.0, source_status="period_conflict", notes="Period row is level 51 and 0 XP; emulator row is level 53 and 7.5 XP."),
    _shortcut("habitat_east_camp", "Herblore Habitat east-camp traversal", 55, 30.0, consumer="route", notes="Three ordered traversal phases award 10 XP each."),
    _shortcut("yanille_monkey_bars", "Yanille Dungeon monkey bars", 57, 18.0),
    _shortcut("ectofuntus_wall", "Ectofuntus wall shortcut", 58, 0.0, consumer="route"),
    _shortcut("arandar_rocks_59", "Arandar rocks (level 59)", 59, 0.0),
    _shortcut("god_wars_rocks", "God Wars Dungeon rocks", 60, 0.0),
    _shortcut("slayer_tower_chain_lower", "Slayer Tower lower chain", 61, 0.0),
    _shortcut("fremennik_slayer_crevice", "Fremennik Slayer Dungeon crevice", 62, 0.0),
    _shortcut("trollheim_wilderness_rocks", "Trollheim to Wilderness rocks", 64, 0.0),
    _shortcut("river_salve_railing", "River Salve railing", 65, 0.0),
    _shortcut("blood_altar_wall", "Meiyerditch to Blood altar wall", 65, 0.0, consumer="route"),
    _shortcut("cosmic_walkway_advanced", "Cosmic altar advanced walkway", 66, 10.0, consumer="route"),
    _shortcut("yanille_salarin_rubble", "Yanille rubble to Salarin", 67, 6.0),
    _shortcut("arandar_rocks_68", "Arandar rocks (level 68)", 68, 0.0),
    _shortcut("taverley_blue_dragon_pipe", "Taverley blue-dragon pipe", 70, 10.0),
    _shortcut("slayer_tower_chain_upper", "Slayer Tower upper chain", 71, 0.0),
    _shortcut("shilo_fishing_stones", "Shilo Village fly-fishing stones", 74, 1.25, consumer="route"),
    _shortcut("kethsi_gap", "Kethsi gap", 77, 2.0),
    _shortcut("taverley_spider_floor", "Taverley poison-spider floor", 80, 12.5),
    _shortcut("fremennik_slayer_chasm", "Fremennik Slayer Dungeon chasm", 81, 0.0),
    _shortcut("arandar_rocks_85", "Arandar rocks (level 85)", 85, 0.0),
    _shortcut("kuradal_metal_dragon_wall", "Kuradal metal-dragon wall", 86, 6.0),
    _shortcut("kuradal_wall_run", "Kuradal wall run", 90, 6.0),
)


AGILITY_GRAPPLE_SHORTCUTS = (
    AgilityShortcut("grapple_river_lum", "River Lum raft grapple", 8, 15.0, "route", (("strength", 19), ("ranged", 37)), required_items=("Crossbow", "Mith grapple"), hidey_hole_materials=(("Oak plank", 4), ("Steel crossbow", 1))),
    AgilityShortcut("grapple_falador_wall", "Falador wall grapple", 11, 0.0, "route", (("strength", 37), ("ranged", 19)), required_items=("Crossbow", "Mith grapple"), hidey_hole_materials=(("Plank", 4), ("Nails", 4), ("Bronze crossbow", 1))),
    AgilityShortcut("grapple_catherby_cliff", "Catherby cliff grapple", 32, 15.0, "route", (("strength", 35), ("ranged", 35)), quest_gate="fishing_contest", required_items=("Crossbow", "Mith grapple"), hidey_hole_materials=(("Oak plank", 4), ("Iron crossbow", 1))),
    AgilityShortcut("grapple_water_obelisk", "Water Obelisk tree grapple", 36, 15.0, "route", (("strength", 22), ("ranged", 39)), required_items=("Crossbow", "Mith grapple"), hidey_hole_materials=(("Teak plank", 4), ("Mithril crossbow", 1)), notes="One-way shortcut."),
    AgilityShortcut("grapple_yanille_wall", "Yanille wall grapple", 39, 15.0, "route", (("strength", 38), ("ranged", 21)), required_items=("Crossbow", "Mith grapple"), hidey_hole_materials=(("Plank", 4), ("Nails", 4), ("Bronze crossbow", 1))),
    AgilityShortcut("grapple_karamja_volcano", "Karamja volcano grapple", 53, 0.0, "route", (("strength", 21), ("ranged", 42)), required_items=("Crossbow", "Mith grapple"), hidey_hole_materials=(("Mahogany plank", 4), ("Mithril crossbow", 1))),
)

ALL_AGILITY_SHORTCUTS = AGILITY_SHORTCUTS + AGILITY_GRAPPLE_SHORTCUTS

AGILITY_REWARD_ITEMS = (
    "Agility arena ticket", "Pyramid top", "Agile top", "Agile legs", "Gnomeball",
    "Gorilla mask", "Factory mask", "Factory top", "Factory trousers", "Factory gloves",
    "Factory boots", "Rogue mask", "Rogue top", "Rogue trousers", "Rogue gloves",
    "Rogue boots", "Rogue kit", "Pirate's hook", "Werewolf stick", "Generator part",
)

AGILITY_ITEM_FILENAMES = {
    "Agility arena ticket": "agility_arena_ticket.png",
    "Pyramid top": "pyramid_top.png",
    "Agile top": "agile_top.png",
    "Agile legs": "agile_legs.png",
    "Gnomeball": "gnomeball.png",
    "Gorilla mask": "gorilla_mask.png",
    "Factory mask": "factory_mask.png",
    "Factory top": "factory_top.png",
    "Factory trousers": "factory_trousers.png",
    "Factory gloves": "factory_gloves.png",
    "Factory boots": "factory_boots.png",
    "Rogue mask": "rogue_mask.png",
    "Rogue top": "rogue_top.png",
    "Rogue trousers": "rogue_trousers.png",
    "Rogue gloves": "rogue_gloves.png",
    "Rogue boots": "rogue_boots.png",
    "Rogue kit": "rogue_kit.png",
    "Pirate's hook": "pirates_hook.png",
    "Werewolf stick": "werewolf_stick.png",
    "Generator part": "generator_part.png",
    "Acrobat hood": "acrobat_hood.png",
    "Acrobat shirt": "acrobat_shirt.png",
    "Acrobat pants": "acrobat_pants.png",
    "Acrobat shoes": "acrobat_shoes.png",
    "Toy mouse": "toy_mouse.png",
    "Boots of lightness": "boots_of_lightness.png",
    "Spotted cape": "spotted_cape.png",
    "Spottier cape": "spottier_cape.png",
    "Karamja gloves 4": "karamja_gloves_4.png",
    "Penance horn": "penance_horn.png",
    "Penance master horn": "penance_master_horn.png",
    "Brawling gloves (Agility)": "brawling_gloves_agility.png",
    "Sköll boots": "skoll_boots.png",
    "Pendant of Agility": "pendant_of_agility.png",
    "Prized pendant of Agility": "prized_pendant_of_agility.png",
    "Surefooted aura": "surefooted_aura.png",
    "Greater surefooted aura": "greater_surefooted_aura.png",
    "Agility cape": "agility_cape.png",
    "Agility hood": "agility_hood.png",
    "Agility potion (4)": "agility_potion_4.png",
    "Agility potion (3)": "agility_potion_4.png",
    "Agility potion (2)": "agility_potion_4.png",
    "Agility potion (1)": "agility_potion_4.png",
    "Agility mix (2)": "agility_mix_2.png",
    "Agility mix (1)": "agility_mix_2.png",
    "Summer pie": "summer_pie.png",
    "Half a summer pie": "summer_pie.png",
    "Mith grapple": "mith_grapple.png",
}
AGILITY_ITEM_IMAGES = {
    item_name: str(_ROOT / "agilityitems" / filename)
    for item_name, filename in AGILITY_ITEM_FILENAMES.items()
}

_AGILITY_EQUIPMENT = {
    "Gnomeball", "Agile top", "Agile legs", "Gorilla mask", "Factory mask", "Factory top",
    "Factory trousers", "Factory gloves", "Factory boots", "Rogue mask", "Rogue top",
    "Rogue trousers", "Rogue gloves", "Rogue boots", "Pirate's hook", "Acrobat hood",
    "Acrobat shirt", "Acrobat pants", "Acrobat shoes",
    "Boots of lightness", "Spotted cape", "Spottier cape", "Karamja gloves 4",
    "Brawling gloves (Agility)", "Sköll boots", "Pendant of Agility",
    "Prized pendant of Agility", "Agility cape", "Agility hood",
}
_AGILITY_CONSUMABLE_IDS = {
    "Agility potion (4)": 3032,
    "Agility potion (3)": 3034,
    "Agility potion (2)": 3036,
    "Agility potion (1)": 3038,
    "Agility mix (2)": 11461,
    "Agility mix (1)": 11463,
    "Summer pie": 7218,
    "Half a summer pie": 7220,
}
AGILITY_EXTRA_ITEM_DATA = {
    item_name: {
        "category": (
            "equipment"
            if item_name in _AGILITY_EQUIPMENT
            else "food"
            if item_name in {"Summer pie", "Half a summer pie"}
            else "material"
        ),
        "source": "Agility",
        "stackable": item_name in {"Agility arena ticket", "Rogue kit"},
        "tradeable": (
            item_name in {"Pyramid top", "Gnomeball", "Toy mouse", "Mith grapple"}
            or item_name in _AGILITY_CONSUMABLE_IDS
        ),
        "source_item_id": {
            "Agile top": 14936,
            "Agile legs": 14938,
            "Gnomeball": 751,
            **_AGILITY_CONSUMABLE_IDS,
        }.get(item_name),
    }
    for item_name in AGILITY_ITEM_FILENAMES
}


AGILITY_TARGET_IMAGES = {
    target.id: str(_ROOT / "icon" / "agility_icon.png")
    for target in AGILITY_TARGETS
}
AGILITY_TARGET_IMAGES.update({
    "brimhaven_arena": str(_ROOT / "agilityitems" / "agility_arena_ticket.png"),
    "gnome_ball": str(_ROOT / "agilityitems" / "gnomeball.png"),
    "flash_powder_factory": str(_ROOT / "agilityitems" / "factory_mask.png"),
    "the_pit": str(_ROOT / "agilityitems" / "gorilla_mask.png"),
})

AGILITY_GROUP_LABELS = {"courses": "Courses", "activities": "Activities"}
AGILITY_GROUP_ORDER = ("courses", "activities")
