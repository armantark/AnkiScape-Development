from __future__ import annotations

from typing import Dict, Tuple

from .contract import (
    CHAELDAR_AUDIT_SOURCE,
    DURADEL_AUDIT_SOURCE,
    MAZCHNA_AUDIT_SOURCE,
    SLAYER_FAMILIES_BY_ID,
    SUMONA_AUDIT_SOURCE,
    TURAEL_AUDIT_SOURCE,
    VANNAKA_AUDIT_SOURCE,
    SlayerAssignmentFamily,
    SlayerMaster,
    SlayerMasterFamilyRow,
)


def _assignment(
    family_id: str,
    weight: int,
    count_min: int,
    count_max: int,
    source: str,
) -> SlayerAssignmentFamily:
    return SlayerAssignmentFamily(
        family=SLAYER_FAMILIES_BY_ID[family_id],
        row=SlayerMasterFamilyRow(
            family_id=family_id,
            weight=weight,
            count_min=count_min,
            count_max=count_max,
            source=source,
        ),
    )


TURAEL_FAMILIES: Tuple[SlayerAssignmentFamily, ...] = (
    _assignment("banshees", 30, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("bats", 10, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("bears", 10, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("birds", 10, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("cave_bugs", 10, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("cave_slimes", 30, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("cows", 10, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("crawling_hands", 30, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("desert_lizards", 30, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("dogs", 15, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("dwarves", 10, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("ghosts", 15, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("goblins", 10, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("gelatinous_abominations", 30, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("grotworms", 15, 15, 30, TURAEL_AUDIT_SOURCE),
    _assignment("icefiends", 10, 10, 20, TURAEL_AUDIT_SOURCE),
    _assignment("minotaurs", 10, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("monkeys", 10, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("scorpions", 10, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("skeletons", 15, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("spiders", 10, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("wolves", 15, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("zombies", 10, 15, 50, TURAEL_AUDIT_SOURCE),
)

MAZCHNA_FAMILIES: Tuple[SlayerAssignmentFamily, ...] = tuple(
    _assignment(family_id, weight, count_min, count_max, MAZCHNA_AUDIT_SOURCE)
    for family_id, weight, count_min, count_max in (
        ("banshees", 20, 40, 70),
        ("bats", 10, 40, 70),
        ("bears", 10, 40, 70),
        ("catablepon", 10, 40, 70),
        ("cave_crawlers", 20, 40, 70),
        ("cave_slimes", 10, 40, 70),
        ("cockatrice", 20, 40, 70),
        ("crawling_hands", 20, 40, 70),
        ("cyclopes", 10, 30, 60),
        ("desert_lizards", 10, 40, 70),
        ("dogs", 10, 40, 70),
        ("flesh_crawlers", 10, 40, 70),
        ("ghouls", 10, 40, 70),
        ("ghosts", 10, 40, 70),
        ("grotworms", 10, 40, 70),
        ("hill_giants", 10, 40, 70),
        ("hobgoblins", 10, 40, 70),
        ("ice_warriors", 10, 40, 70),
        ("kalphites", 10, 40, 70),
        ("mogres", 10, 40, 70),
        ("pyrefiends", 20, 40, 70),
        ("rock_slugs", 15, 40, 70),
        ("skeletons", 10, 40, 70),
        ("vampyres", 10, 40, 70),
        ("wall_beasts", 10, 10, 20),
        ("wolves", 10, 40, 70),
        ("zombies", 10, 40, 70),
    )
)

VANNAKA_FAMILIES: Tuple[SlayerAssignmentFamily, ...] = tuple(
    _assignment(family_id, weight, count_min, count_max, VANNAKA_AUDIT_SOURCE)
    for family_id, weight, count_min, count_max in (
        ("aberrant_spectres", 25, 60, 120),
        ("ankou", 10, 60, 120),
        ("banshees", 15, 60, 120),
        ("basilisks", 10, 60, 120),
        ("bloodveld", 20, 60, 120),
        ("brine_rats", 20, 60, 120),
        ("cockatrice", 10, 60, 120),
        ("crocodiles", 10, 30, 60),
        ("cyclopes", 10, 60, 120),
        ("dust_devils", 25, 60, 120),
        ("earth_warriors", 15, 30, 60),
        ("ghouls", 10, 60, 120),
        ("green_dragons", 10, 30, 60),
        ("grotworms", 15, 60, 120),
        ("harpie_bug_swarms", 20, 60, 120),
        ("hill_giants", 10, 60, 120),
        ("ice_giants", 10, 60, 120),
        ("ice_warriors", 10, 60, 120),
        ("infernal_mages", 10, 60, 120),
        ("jellies", 20, 60, 120),
        ("jungle_horrors", 10, 60, 120),
        ("killerwatts", 20, 60, 120),
        ("lesser_demons", 10, 60, 120),
        ("mogres", 10, 60, 120),
        ("molanisks", 10, 60, 120),
        ("moss_giants", 10, 60, 120),
        ("ogres", 10, 60, 120),
        ("otherworldly_beings", 10, 60, 120),
        ("pyrefiends", 10, 60, 120),
        ("sea_snakes", 10, 30, 60),
        ("shades", 10, 60, 120),
        ("shadow_warriors", 10, 60, 120),
        ("turoth", 20, 60, 120),
        ("vampyres", 15, 60, 120),
        ("werewolves", 10, 60, 120),
    )
)

CHAELDAR_FAMILIES: Tuple[SlayerAssignmentFamily, ...] = tuple(
    _assignment(family_id, weight, count_min, count_max, CHAELDAR_AUDIT_SOURCE)
    for family_id, weight, count_min, count_max in (
        ("aberrant_spectres", 15, 110, 170),
        ("banshees", 5, 110, 170),
        ("basilisks", 15, 110, 170),
        ("bloodveld", 15, 110, 170),
        ("blue_dragons", 10, 110, 170),
        ("brine_rats", 10, 110, 170),
        ("bronze_dragons", 10, 30, 60),
        ("cave_crawlers", 5, 110, 170),
        ("cave_horrors", 15, 110, 170),
        ("crawling_hands", 5, 110, 170),
        ("dagannoths", 10, 110, 170),
        ("dust_devils", 15, 110, 170),
        ("elves", 10, 60, 90),
        ("fever_spiders", 10, 110, 170),
        ("fire_giants", 10, 110, 170),
        ("fungal_magi", 10, 83, 136),
        ("gargoyles", 15, 110, 170),
        ("grifolapines", 8, 60, 100),
        ("grifolaroos", 8, 60, 100),
        ("grotworms", 15, 72, 109),
        ("harpie_bug_swarms", 20, 110, 170),
        ("jungle_strykewyrms", 12, 80, 110),
        ("infernal_mages", 10, 110, 170),
        ("jellies", 15, 110, 170),
        ("jungle_horrors", 15, 110, 170),
        ("kalphites", 10, 110, 170),
        ("kurasks", 15, 110, 170),
        ("lesser_demons", 10, 110, 170),
        ("mutated_zygomites", 10, 30, 60),
        ("shadow_warriors", 10, 110, 170),
        ("trolls", 10, 110, 170),
        ("turoth", 15, 110, 170),
        ("vyrewatch", 10, 89, 106),
        ("warped_tortoises", 10, 110, 170),
    )
)

SUMONA_FAMILIES: Tuple[SlayerAssignmentFamily, ...] = tuple(
    _assignment(family_id, weight, count_min, count_max, SUMONA_AUDIT_SOURCE)
    for family_id, weight, count_min, count_max in (
        ("aberrant_spectres", 15, 120, 185),
        ("abyssal_demons", 10, 120, 185),
        ("aquanites", 10, 120, 185),
        ("banshees", 15, 120, 185),
        ("basilisks", 15, 120, 185),
        ("black_demons", 10, 120, 185),
        ("bloodveld", 10, 120, 185),
        ("blue_dragons", 8, 120, 189),
        ("cave_crawlers", 15, 120, 185),
        ("cave_horrors", 15, 120, 185),
        ("dagannoths", 10, 120, 192),
        ("desert_strykewyrms", 14, 90, 110),
        ("dust_devils", 15, 120, 185),
        ("elves", 10, 60, 90),
        ("fire_giants", 10, 120, 185),
        ("fungal_magi", 10, 90, 150),
        ("gargoyles", 10, 120, 185),
        ("greater_demons", 10, 120, 185),
        ("grifolapines", 8, 55, 75),
        ("grifolaroos", 8, 55, 75),
        ("grotworms", 15, 70, 115),
        ("hellhounds", 10, 120, 185),
        ("iron_dragons", 7, 30, 85),
        ("jungle_strykewyrms", 12, 90, 120),
        ("kalphites", 10, 120, 189),
        ("kurasks", 15, 120, 185),
        ("mutated_jadinkos", 10, 80, 130),
        ("nechryael", 10, 120, 185),
        ("red_dragons", 5, 30, 79),
        ("scabarites", 10, 30, 60),
        ("spiritual_mages", 10, 120, 185),
        ("spiritual_warriors", 10, 120, 185),
        ("terror_dogs", 10, 30, 60),
        ("trolls", 10, 120, 191),
        ("turoth", 15, 120, 185),
        ("vyrewatch", 10, 96, 105),
        ("warped_tortoises", 10, 120, 185),
    )
)

DURADEL_FAMILIES: Tuple[SlayerAssignmentFamily, ...] = tuple(
    _assignment(family_id, weight, count_min, count_max, DURADEL_AUDIT_SOURCE)
    for family_id, weight, count_min, count_max in (
        ("aberrant_spectres", 10, 130, 200),
        ("abyssal_demons", 15, 130, 200),
        ("aquanites", 9, 130, 200),
        ("black_demons", 10, 130, 200),
        ("black_dragons", 9, 40, 80),
        ("bloodveld", 20, 130, 200),
        ("dagannoths", 10, 130, 200),
        ("dark_beasts", 15, 130, 200),
        ("desert_strykewyrms", 11, 90, 140),
        ("dust_devils", 10, 130, 200),
        ("fire_giants", 10, 130, 200),
        ("fungal_magi", 8, 100, 200),
        ("ganodermic_creatures", 6, 55, 70),
        ("gargoyles", 10, 130, 200),
        ("goraks", 5, 40, 80),
        ("greater_demons", 11, 130, 200),
        ("grifolapines", 10, 65, 80),
        ("grifolaroos", 10, 65, 80),
        ("grotworms", 10, 80, 120),
        ("hellhounds", 9, 130, 200),
        ("ice_strykewyrms", 8, 100, 200),
        ("iron_dragons", 9, 40, 80),
        ("jungle_strykewyrms", 10, 90, 120),
        ("kalphites", 10, 130, 200),
        ("mithril_dragons", 7, 4, 11),
        ("mutated_jadinkos", 8, 120, 200),
        ("nechryael", 10, 130, 200),
        ("scabarites", 10, 40, 79),
        ("skeletal_wyverns", 5, 40, 80),
        ("spiritual_mages", 10, 130, 200),
        ("steel_dragons", 7, 40, 80),
        ("suqahs", 5, 40, 80),
        ("vyrewatch", 8, 98, 118),
        ("warped_terrorbirds", 9, 130, 200),
        ("waterfiends", 10, 130, 200),
    )
)

TURAEL_MASTER = SlayerMaster(
    id="turael_spria",
    display_name="Turael",
    assignments=TURAEL_FAMILIES,
    runtime_enabled=True,
    chathead_asset_path="activityicons/turael_chathead.png",
    alternate_display_name="Spria",
    alternate_display_condition="while_guthix_sleeps_completed",
    alternate_chathead_asset_path="activityicons/spria_chathead.png",
    expected_weight_total=355,
)

MAZCHNA_MASTER = SlayerMaster(
    id="mazchna_achtryn",
    display_name="Mazchna",
    assignments=MAZCHNA_FAMILIES,
    required_combat_level=20,
    required_quest_id="priest_in_peril",
    chathead_asset_path="activityicons/mazchna_chathead.png",
    alternate_display_name="Achtryn",
    alternate_display_condition="while_guthix_sleeps_in_progress",
    alternate_chathead_asset_path="activityicons/achtryn_chathead.png",
    expected_weight_total=325,
    source=MAZCHNA_AUDIT_SOURCE,
)

VANNAKA_MASTER = SlayerMaster(
    id="vannaka",
    display_name="Vannaka",
    assignments=VANNAKA_FAMILIES,
    required_combat_level=40,
    chathead_asset_path="activityicons/vannaka_chathead.png",
    expected_weight_total=460,
    source=VANNAKA_AUDIT_SOURCE,
)

CHAELDAR_MASTER = SlayerMaster(
    id="chaeldar",
    display_name="Chaeldar",
    assignments=CHAELDAR_FAMILIES,
    required_combat_level=70,
    required_quest_id="lost_city",
    chathead_asset_path="activityicons/chaeldar_chathead.png",
    expected_weight_total=388,
    source=CHAELDAR_AUDIT_SOURCE,
)

SUMONA_MASTER = SlayerMaster(
    id="sumona",
    display_name="Sumona",
    assignments=SUMONA_FAMILIES,
    required_slayer_level=35,
    required_combat_level=85,
    required_quest_id="smoking_kills",
    chathead_asset_path="activityicons/sumona_chathead.png",
    expected_weight_total=407,
    source=SUMONA_AUDIT_SOURCE,
)

DURADEL_MASTER = SlayerMaster(
    id="duradel_lapalok",
    display_name="Duradel",
    assignments=DURADEL_FAMILIES,
    required_slayer_level=50,
    required_combat_level=100,
    required_quest_id="shilo_village",
    chathead_asset_path="activityicons/duradel_chathead.png",
    alternate_display_name="Lapalok",
    alternate_display_condition="while_guthix_sleeps_completed",
    alternate_chathead_asset_path="activityicons/lapalok_chathead.png",
    expected_weight_total=334,
    source=DURADEL_AUDIT_SOURCE,
)

SLAYER_MASTERS_BY_ID: Dict[str, SlayerMaster] = {
    master.id: master
    for master in (
        TURAEL_MASTER,
        MAZCHNA_MASTER,
        VANNAKA_MASTER,
        CHAELDAR_MASTER,
        SUMONA_MASTER,
        DURADEL_MASTER,
    )
}
LIVE_SLAYER_MASTERS_BY_ID: Dict[str, SlayerMaster] = {
    master_id: master
    for master_id, master in SLAYER_MASTERS_BY_ID.items()
    if master.runtime_enabled
}

TURAEL_FAMILIES_BY_ID: Dict[str, SlayerAssignmentFamily] = {
    family.id: family for family in TURAEL_FAMILIES
}
MAZCHNA_FAMILIES_BY_ID: Dict[str, SlayerAssignmentFamily] = {
    family.id: family for family in MAZCHNA_FAMILIES
}
VANNAKA_FAMILIES_BY_ID: Dict[str, SlayerAssignmentFamily] = {
    family.id: family for family in VANNAKA_FAMILIES
}
CHAELDAR_FAMILIES_BY_ID: Dict[str, SlayerAssignmentFamily] = {
    family.id: family for family in CHAELDAR_FAMILIES
}
SUMONA_FAMILIES_BY_ID: Dict[str, SlayerAssignmentFamily] = {
    family.id: family for family in SUMONA_FAMILIES
}
DURADEL_FAMILIES_BY_ID: Dict[str, SlayerAssignmentFamily] = {
    family.id: family for family in DURADEL_FAMILIES
}

DEFAULT_SLAYER_MASTER_ID = TURAEL_MASTER.id
