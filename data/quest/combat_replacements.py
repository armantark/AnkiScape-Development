from __future__ import annotations

from .dependencies import *
from .contract import *
from .ids import *
from .sources import *

_UNDERGROUND_PASS_COMBAT_SOURCE = (
    "https://runescape.wiki/w/Othainian?oldid=6110941; "
    "https://runescape.wiki/w/Othainian?oldid=5373309; "
    "/Users/ArmanTarkhanian1/Documents/CodexWorktrees/darkan-master-integration/data/npcs/combatdefs/uncategorized/othainian (noanims).json"
)

_RECRUITMENT_DRIVE_COMBAT_SOURCE = (
    "https://runescape.wiki/w/Sir_Leye?oldid=6430968; "
    "https://runescape.wiki/w/Sir_Leye?oldid=5380553; "
    "/Users/ArmanTarkhanian1/Documents/CodexWorktrees/darkan-master-integration/data/npcs/combatdefs/uncategorized/sir_leye (nostats) (noanims).json"
)

_WANTED_COMBAT_SOURCE = (
    "https://runescape.wiki/w/Solus_Dellagar?oldid=5587768; "
    "https://runescape.wiki/w/Solus_Dellagar?oldid=6342730; "
    "/Users/ArmanTarkhanian1/Documents/CodexWorktrees/darkan-master-integration/data/npcs/combatdefs/uncategorized/solus_dellagar (nostats) (noanims).json; "
    "/Users/ArmanTarkhanian1/Documents/CodexWorktrees/darkan-master-integration/src/main/java/com/rs/game/content/quests/wanted/WantedState.kt:15 (WantedIds.SOLUS_ATTACK = 2780); "
    "/Users/ArmanTarkhanian1/Documents/CodexWorktrees/darkan-master-integration/src/main/java/com/rs/game/content/quests/wanted/Wanted.kt:284-294 (startSolusFight, hitpoints = 540 at :289)"
)

_THE_FREMENNIK_ISLES_COMBAT_SOURCE = (
    "https://runescape.wiki/w/Ice_troll_male?oldid=6288801; "
    "https://runescape.wiki/w/Ice_troll_male?oldid=5669851; "
    "/Users/ArmanTarkhanian1/Documents/CodexWorktrees/darkan-master-integration/data/npcs/combatdefs/uncategorized/ice_troll_male (noanims).json"
)

_DREAM_MENTOR_COMBAT_SOURCE = (
    "https://runescape.wiki/w/The_Illusive?oldid=5908075; "
    "https://runescape.wiki/w/The_Illusive?oldid=5668876; "
    "/Users/ArmanTarkhanian1/Documents/CodexWorktrees/darkan-master-integration/data/npcs/combatdefs/uncategorized/the_illusive (nostats) (noanims).json"
)

# The owner accepted the mother's 1,000 life points on 2026-10-20 at 19:04 PDT
# and the baby's identification and 350 life points that date at 19:59 PDT.
# These are life-point overrides only; they do not qualify other combat fields.
HORROR_FROM_THE_DEEP_LIFEPOINT_OVERRIDES = {
    "horror_from_the_deep_dagannoth_100": (
        350,
        "https://web.archive.org/web/20121105084853id_/http://www.runehq.com:80/monster/dagannoth-baby",
    ),
    "horror_from_the_deep_dagannoth_mother_horror_from_the_deep_100": (
        1000,
        "https://runescape.wiki/w/index.php?title=Dagannoth_mother_(Horror_from_the_Deep)&oldid=6448031; "
        "https://web.archive.org/web/20100824081504id_/http://www.tip.it:80/runescape/?rs2monster_id=377",
    ),
}

QUEST_COMBAT_ENCOUNTER_REPLACEMENTS_BY_ID: Dict[str, Dict[str, QuestCombatEncounterReplacement]] = {
    "underground_pass": {
        "underground_pass_othanian_91": _combat(
            "underground_pass",
            "othanian_91",
            "Othanian",
            91,
            "https://runescape.wiki/w/Underground_Pass?oldid=6582023" + "; " + _UNDERGROUND_PASS_COMBAT_SOURCE,
            "Othanian (Level 91)",
            npc_stats=(
                ("hitpoints", 900),
                # PLACEHOLDER(quests.underground_pass.othanian_91.attack): independent period combat data would settle this retained Darkan value.
                ("attack", 76),
                # PLACEHOLDER(quests.underground_pass.othanian_91.strength): independent period combat data would settle this retained Darkan value.
                ("strength", 78),
                # PLACEHOLDER(quests.underground_pass.othanian_91.defence): independent period combat data would settle this retained Darkan value.
                ("defence", 77),
                # PLACEHOLDER(quests.underground_pass.othanian_91.magic): independent period combat data would settle this retained Darkan value.
                ("magic", 1),
                # PLACEHOLDER(quests.underground_pass.othanian_91.ranged): independent period combat data would settle this retained Darkan value.
                ("ranged", 1),
            ),
            npc_configs=(
                ("attack_style", "melee"),
                ("max_hit", 93),
            ),
            npc_stats_source=_UNDERGROUND_PASS_COMBAT_SOURCE,
        ),
    },
    "recruitment_drive": {
        "recruitment_drive_sir_leye_20": _combat(
            "recruitment_drive",
            "sir_leye_20",
            "Sir Leye",
            20,
            "https://runescape.wiki/w/Recruitment_Drive?oldid=6571928" + "; " + _RECRUITMENT_DRIVE_COMBAT_SOURCE,
            "Sir Leye (level 20) without weapons or armour.",
            npc_stats=(
                ("hitpoints", 210),
                # PLACEHOLDER(quests.recruitment_drive.sir_leye_20.attack): independent period combat data would settle this retained Darkan value.
                ("attack", 0),
                # PLACEHOLDER(quests.recruitment_drive.sir_leye_20.strength): independent period combat data would settle this retained Darkan value.
                ("strength", 0),
                # PLACEHOLDER(quests.recruitment_drive.sir_leye_20.defence): independent period combat data would settle this retained Darkan value.
                ("defence", 0),
                # PLACEHOLDER(quests.recruitment_drive.sir_leye_20.magic): independent period combat data would settle this retained Darkan value.
                ("magic", 0),
                # PLACEHOLDER(quests.recruitment_drive.sir_leye_20.ranged): independent period combat data would settle this retained Darkan value.
                ("ranged", 0),
            ),
            npc_configs=(
                ("attack_style", "melee"),
                ("max_hit", 20),
            ),
            npc_stats_source=_RECRUITMENT_DRIVE_COMBAT_SOURCE,
        ),
    },
    "wanted": {
        "wanted_solus_dellagar_2": _combat(
            "wanted",
            "solus_dellagar_2",
            "Solus Dellagar",
            0,
            "https://runescape.wiki/w/Wanted%21?oldid=6510622" + "; " + _WANTED_COMBAT_SOURCE,
            "Solus Dellagar (no combat level, but is about as strong as a Black Knight)",
            npc_stats=(
                ("hitpoints", 540),
                # PLACEHOLDER(quests.wanted.solus_dellagar_2.attack): independent period combat data would settle this retained Darkan value.
                ("attack", 0),
                # PLACEHOLDER(quests.wanted.solus_dellagar_2.strength): independent period combat data would settle this retained Darkan value.
                ("strength", 0),
                # PLACEHOLDER(quests.wanted.solus_dellagar_2.defence): independent period combat data would settle this retained Darkan value.
                ("defence", 0),
                # PLACEHOLDER(quests.wanted.solus_dellagar_2.magic): independent period combat data would settle this retained Darkan value.
                ("magic", 0),
                # PLACEHOLDER(quests.wanted.solus_dellagar_2.ranged): independent period combat data would settle this retained Darkan value.
                ("ranged", 0),
            ),
            npc_configs=(
                ("attack_style", "melee"),
                ("max_hit", 40),
            ),
            npc_stats_source="https://runescape.wiki/w/Wanted%21?oldid=6510622" + "; " + _WANTED_COMBAT_SOURCE,
        ),
    },
    "the_fremennik_isles": {
        "the_fremennik_isles_ice_troll_82": _combat(
            "the_fremennik_isles",
            "ice_troll_82",
            "Ice troll",
            82,
            "https://runescape.wiki/w/The_Fremennik_Isles?oldid=6540919" + "; " + _THE_FREMENNIK_ISLES_COMBAT_SOURCE,
            "10 Ice trolls (level 82)",
            quantity=10,
            npc_stats=(
                ("hitpoints", 800),
                # PLACEHOLDER(quests.the_fremennik_isles.ice_troll_82.attack): independent period combat data would settle this retained Darkan value.
                ("attack", 80),
                # PLACEHOLDER(quests.the_fremennik_isles.ice_troll_82.strength): independent period combat data would settle this retained Darkan value.
                ("strength", 80),
                # PLACEHOLDER(quests.the_fremennik_isles.ice_troll_82.defence): independent period combat data would settle this retained Darkan value.
                ("defence", 40),
                # PLACEHOLDER(quests.the_fremennik_isles.ice_troll_82.magic): independent period combat data would settle this retained Darkan value.
                ("magic", 1),
                # PLACEHOLDER(quests.the_fremennik_isles.ice_troll_82.ranged): independent period combat data would settle this retained Darkan value.
                ("ranged", 1),
            ),
            npc_configs=(
                ("attack_style", "melee"),
                ("max_hit", 177),
            ),
            npc_stats_source=_THE_FREMENNIK_ISLES_COMBAT_SOURCE,
        ),
    },
    "dream_mentor": {
        "dream_mentor_the_illusive_108": _combat(
            "dream_mentor",
            "the_illusive_108",
            "The Illusive",
            108,
            "https://runescape.wiki/w/Dream_Mentor?oldid=6550965" + "; " + _DREAM_MENTOR_COMBAT_SOURCE,
            "The Illusive (level 108)",
            npc_stats=(
                ("hitpoints", 1400),
                # PLACEHOLDER(quests.dream_mentor.the_illusive_108.attack): independent period combat data would settle this retained Darkan value.
                ("attack", 0),
                # PLACEHOLDER(quests.dream_mentor.the_illusive_108.strength): independent period combat data would settle this retained Darkan value.
                ("strength", 0),
                # PLACEHOLDER(quests.dream_mentor.the_illusive_108.defence): independent period combat data would settle this retained Darkan value.
                ("defence", 0),
                # PLACEHOLDER(quests.dream_mentor.the_illusive_108.magic): independent period combat data would settle this retained Darkan value.
                ("magic", 0),
                # PLACEHOLDER(quests.dream_mentor.the_illusive_108.ranged): independent period combat data would settle this retained Darkan value.
                ("ranged", 0),
            ),
            npc_configs=(
                ("attack_style", "melee"),
                ("max_hit", 85),
            ),
            npc_stats_source=_DREAM_MENTOR_COMBAT_SOURCE,
        ),
    },
    SHILO_VILLAGE_ID: {
        "shilo_village_nazastarool_91": (
            _combat(
                SHILO_VILLAGE_ID,
                "nazastarool_zombie_91",
                "Nazastarool (Zombie)",
                91,
                f"{SHILO_VILLAGE_WIKI_SOURCE}; {DARKAN_NAZASTAROOL_91_NPC_SOURCE}",
                "Historical quest details say Nazastarool first appears as a level 91 Zombie.",
                npc_stats=(
                    ("hitpoints", 500),
                    ("attack", 38),
                    ("strength", 30),
                    ("defence", 38),
                    ("magic", 0),
                    ("ranged", 0),
                ),
                npc_configs=(
                    ("max_hit", 70),
                    ("attack_range", -1),
                    ("attack_style", "melee"),
                    ("attack_bonus", "crush_att"),
                    ("aggressiveness_type", "aggressive"),
                ),
                npc_stats_source=DARKAN_NAZASTAROOL_91_NPC_SOURCE,
            ),
            _combat(
                SHILO_VILLAGE_ID,
                "nazastarool_skeleton_68",
                "Nazastarool (Skeleton)",
                68,
                f"{SHILO_VILLAGE_WIKI_SOURCE}; {DARKAN_NAZASTAROOL_68_NPC_SOURCE}",
                "Historical quest details say Nazastarool's second form is a level 68 Skeleton.",
                npc_stats=(
                    ("hitpoints", 750),
                    ("attack", 38),
                    ("strength", 30),
                    ("defence", 38),
                    ("magic", 0),
                    ("ranged", 0),
                ),
                npc_configs=(
                    ("max_hit", 120),
                    ("attack_range", -1),
                    ("attack_style", "melee"),
                    ("attack_bonus", "crush_att"),
                    ("aggressiveness_type", "aggressive"),
                ),
                npc_stats_source=DARKAN_NAZASTAROOL_68_NPC_SOURCE,
            ),
            _combat(
                SHILO_VILLAGE_ID,
                "nazastarool_ghost_93",
                "Nazastarool (Ghost)",
                93,
                f"{SHILO_VILLAGE_WIKI_SOURCE}; {DARKAN_NAZASTAROOL_93_NPC_SOURCE}",
                "Historical quest details say Nazastarool's last form is a level 93 Ghost.",
                npc_stats=(
                    ("hitpoints", 1000),
                    ("attack", 38),
                    ("strength", 30),
                    ("defence", 38),
                    ("magic", 0),
                    ("ranged", 0),
                ),
                npc_configs=(
                    ("max_hit", 152),
                    ("attack_range", -1),
                    ("attack_style", "melee"),
                    ("attack_bonus", "crush_att"),
                    ("aggressiveness_type", "aggressive"),
                ),
                npc_stats_source=DARKAN_NAZASTAROOL_93_NPC_SOURCE,
            ),
        ),
    },
    LEGENDS_QUEST_ID: {
        "legends_quest_nezikchened_187": _combat(
            LEGENDS_QUEST_ID,
            "nezikchened_187",
            "Nezikchened",
            187,
            f"{LEGENDS_QUEST_WIKI_SOURCE}; {LEGENDS_QUEST_NEZIKCHENED_NPC_SOURCE}",
            "Historical quest details name Nezikchened level 187 three times.",
            quantity=3,
            npc_stats=(
                ("hitpoints", 1500),
                ("attack", 330),
                ("strength", 336),
                ("defence", 167),
                ("magic", 320),
                ("ranged", 320),
            ),
            npc_configs=(
                ("max_hit", 180),
                ("attack_range", -1),
                ("attack_style", "melee"),
                ("attack_bonus", "slash_att"),
                ("aggressiveness_type", "aggressive"),
            ),
            npc_stats_source=LEGENDS_QUEST_NEZIKCHENED_NPC_SOURCE,
        ),
    },
    DEATH_TO_THE_DORGESHUUN_ID: {
        "death_to_the_dorgeshuun_senior_guard_x3_22": _combat(
            DEATH_TO_THE_DORGESHUUN_ID,
            "senior_ham_guard_22",
            "Senior H.A.M. guard",
            22,
            f"{DEATH_TO_DORGESHUUN_WIKI_SOURCE}; {DARKAN_NPC_LIST_SOURCE}; {DEATH_TO_DORGESHUUN_HAM_GUARD_NPC_SOURCE}",
            "Historical quest details require three level 22 senior guards; Darkan NPC id 1712 supplies the level 22 H.A.M. Guard combat stats.",
            quantity=3,
            npc_stats=(
                ("hitpoints", 300),
                ("attack", 16),
                ("strength", 20),
                ("defence", 12),
                ("magic", 1),
                ("ranged", 1),
            ),
            npc_configs=(
                ("max_hit", 26),
                ("attack_range", -1),
                ("attack_style", "melee"),
                ("attack_bonus", "crush_att"),
                ("aggressiveness_type", "passive"),
            ),
            npc_stats_source=DEATH_TO_DORGESHUUN_HAM_GUARD_NPC_SOURCE,
        ),
    },
    HEROES_QUEST_ID: {
        "heroes_quest_entrana_fire_bird_2": _combat(
            HEROES_QUEST_ID,
            "entrana_fire_bird_2",
            "Entrana Fire Bird",
            2,
            f"{HEROES_QUEST_WIKI_SOURCE}; {DARKAN_NPC_LIST_SOURCE}; {HEROES_QUEST_ENTRANA_FIREBIRD_NPC_SOURCE}",
            "Historical quest details require the Entrana Fire Bird level 2; Darkan NPC id 6108 and the Entrana firebird combatdef supply these stats.",
            npc_stats=(
                ("hitpoints", 50),
                ("attack", 1),
                ("strength", 1),
                ("defence", 1),
                ("magic", 1),
                ("ranged", 1),
            ),
            npc_configs=(
                ("max_hit", 10),
                ("attack_range", -1),
                ("attack_style", "melee"),
                ("attack_bonus", "stab_att"),
                ("aggressiveness_type", "passive"),
            ),
            npc_stats_source=HEROES_QUEST_ENTRANA_FIREBIRD_NPC_SOURCE,
        ),
    },
    SPIRITS_OF_THE_ELID_ID: {
        "spirits_of_the_elid_golem_75": (
            _combat(
                SPIRITS_OF_THE_ELID_ID,
                "black_golem_75",
                "Black golem",
                75,
                f"{SPIRITS_OF_THE_ELID_WIKI_SOURCE}; {DARKAN_ENUMS_SOURCE}; {SPIRITS_BLACK_GOLEM_NPC_SOURCE}",
                "Historical quest details require three level 75 golems; Darkan enum 2791 identifies the Black golem for Spirits of the Elid and the Black golem combatdef supplies these stats.",
                npc_stats=(
                    ("hitpoints", 800),
                    ("attack", 80),
                    ("strength", 30),
                    ("defence", 80),
                    ("magic", 1),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 90),
                    ("attack_range", -1),
                    ("attack_style", "melee"),
                    ("attack_bonus", "crush_att"),
                    ("aggressiveness_type", "aggressive"),
                ),
                npc_stats_source=SPIRITS_BLACK_GOLEM_NPC_SOURCE,
            ),
            _combat(
                SPIRITS_OF_THE_ELID_ID,
                "white_golem_75",
                "White golem",
                75,
                f"{SPIRITS_OF_THE_ELID_WIKI_SOURCE}; {DARKAN_ENUMS_SOURCE}; {SPIRITS_WHITE_GOLEM_NPC_SOURCE}",
                "Historical quest details require three level 75 golems; Darkan enum 2791 identifies the White golem for Spirits of the Elid and the White golem combatdef supplies these stats.",
                npc_stats=(
                    ("hitpoints", 800),
                    ("attack", 80),
                    ("strength", 30),
                    ("defence", 80),
                    ("magic", 1),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 40),
                    ("attack_range", -1),
                    ("attack_style", "melee"),
                    ("attack_bonus", "crush_att"),
                    ("aggressiveness_type", "aggressive"),
                ),
                npc_stats_source=SPIRITS_WHITE_GOLEM_NPC_SOURCE,
            ),
            _combat(
                SPIRITS_OF_THE_ELID_ID,
                "grey_golem_75",
                "Grey golem",
                75,
                f"{SPIRITS_OF_THE_ELID_WIKI_SOURCE}; {DARKAN_ENUMS_SOURCE}; {SPIRITS_GREY_GOLEM_NPC_SOURCE}",
                "Historical quest details require three level 75 golems; Darkan enum 2791 identifies the Grey golem for Spirits of the Elid and the Grey golem combatdef supplies these stats.",
                npc_stats=(
                    ("hitpoints", 800),
                    ("attack", 80),
                    ("strength", 30),
                    ("defence", 80),
                    ("magic", 1),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 40),
                    ("attack_range", -1),
                    ("attack_style", "melee"),
                    ("attack_bonus", "crush_att"),
                    ("aggressiveness_type", "aggressive"),
                ),
                npc_stats_source=SPIRITS_GREY_GOLEM_NPC_SOURCE,
            ),
        ),
    },
    ANOTHER_SLICE_OF_H_A_M_ID: {
        "another_slice_of_h_a_m_h_a_m_ranger_30": _combat(
            ANOTHER_SLICE_OF_H_A_M_ID,
            "h_a_m_ranger_30",
            "H.A.M. ranger",
            30,
            f"{ANOTHER_SLICE_OF_H_A_M_WIKI_SOURCE}; {DARKAN_NPC_LIST_SOURCE}; {DARKAN_BEASTS_SOURCE}; {ANOTHER_SLICE_HAM_ARCHER_NPC_SOURCE}",
            "Historical quest details name a level 30 H.A.M. ranger; Darkan names the ranged level 30 NPC H.A.M. Archer id 5859 and the archer combatdef supplies the ranged payload.",
            npc_stats=(
                ("hitpoints", 350),
                ("attack", 15),
                ("strength", 0),
                ("defence", 30),
                ("magic", 0),
                ("ranged", 30),
            ),
            npc_configs=(
                ("max_hit", 40),
                ("attack_range", -1),
                ("attack_style", "range"),
                ("aggressiveness_type", "aggressive"),
            ),
            npc_stats_source=f"{ANOTHER_SLICE_HAM_ARCHER_NPC_SOURCE}; {DARKAN_BEASTS_SOURCE}",
        ),
    },
    PRIEST_IN_PERIL_ID: {
        "priest_in_peril_monk_of_zamorak_30": _combat(
            PRIEST_IN_PERIL_ID,
            "monk_of_zamorak_30",
            "Monk of Zamorak",
            30,
            f"{PRIEST_IN_PERIL_SOURCE}; {DARKAN_QUEST_SOURCE_ROOT}/priestinperil/PriestInPeril.java; {PRIEST_IN_PERIL_MONK_OF_ZAMORAK_NPC_SOURCE}",
            "Priest in Peril kills use the Paterdomus Zamorak monk NPC ids 1044-1046; the level 30 id 1046 combatdef supplies these stats.",
            npc_stats=(
                ("hitpoints", 250),
                ("attack", 25),
                ("strength", 25),
                ("defence", 25),
                ("magic", 40),
                ("ranged", 1),
            ),
            npc_configs=(
                ("max_hit", 20),
                ("attack_range", -1),
                ("attack_style", "magic"),
                ("attack_bonus", "crush_att"),
                ("aggressiveness_type", "aggressive"),
            ),
            guaranteed_drops=(("Golden key", 1),),
            npc_stats_source=PRIEST_IN_PERIL_MONK_OF_ZAMORAK_NPC_SOURCE,
        ),
    },
    TROLL_STRONGHOLD_ID: {
        "troll_stronghold_dad_101": _combat(
            TROLL_STRONGHOLD_ID,
            "dad_101",
            "Dad",
            101,
            f"https://runescape.wiki/w/Troll_Stronghold?oldid=6552397; {DARKAN_QUEST_SOURCE_ROOT}/troll_stronghold/TrollStronghold.kt; {TROLL_STRONGHOLD_DAD_NPC_SOURCE}",
            "Darkan Troll Stronghold instantiates DAD for the arena fight; the area-specific Dad combatdef supplies these stats.",
            npc_stats=(
                ("hitpoints", 1200),
                ("attack", 60),
                ("strength", 120),
                ("defence", 50),
                ("magic", 0),
                ("ranged", 0),
            ),
            npc_configs=(
                ("max_hit", 275),
                ("attack_range", -1),
                ("attack_style", "melee"),
                ("attack_bonus", "crush_att"),
                ("aggressiveness_type", "passive"),
            ),
            npc_stats_source=TROLL_STRONGHOLD_DAD_NPC_SOURCE,
        ),
    },
}

__all__ = (
    'QUEST_COMBAT_ENCOUNTER_REPLACEMENTS_BY_ID',
    'HORROR_FROM_THE_DEEP_LIFEPOINT_OVERRIDES',
    'apply_horror_from_the_deep_lifepoints',
)


def _horror_from_the_deep_encounter_lifepoints(
    encounter: QuestCombatEncounter,
    hitpoints: int,
    source: str,
) -> QuestCombatEncounter:
    if sum(key == "hitpoints" for key, _value in encounter.npc_stats) != 1:
        raise ValueError("Horror from the Deep life-point override target changed")
    return replace(
        encounter,
        npc_stats=tuple(
            (key, hitpoints) if key == "hitpoints" else (key, value)
            for key, value in encounter.npc_stats
        ),
        npc_stats_source=(
            f"hitpoints: {source}; owner accepted 2026-10-20; "
            "other combat fields retain restoration provenance, not period qualification: "
            f"{encounter.npc_stats_source}"
        ),
    )


def apply_horror_from_the_deep_lifepoints(
    quest_id: str,
    requirements: Tuple[QuestStageRequirement, ...],
) -> Tuple[QuestStageRequirement, ...]:
    if quest_id != "horror_from_the_deep":
        return requirements
    occurrences = dict.fromkeys(HORROR_FROM_THE_DEEP_LIFEPOINT_OVERRIDES, 0)
    error = "Horror from the Deep life-point override target changed"
    rows = []
    for requirement in requirements:
        encounters = []
        changed = False
        for encounter in requirement.combat_encounters:
            override = HORROR_FROM_THE_DEEP_LIFEPOINT_OVERRIDES.get(encounter.encounter_id)
            if override is not None:
                occurrences[encounter.encounter_id] += 1
                hitpoints, source = override
                encounter = _horror_from_the_deep_encounter_lifepoints(encounter, hitpoints, source)
                changed = True
            encounters.append(encounter)
        if changed:
            requirement = replace(requirement, combat_encounters=tuple(encounters))
        rows.append(requirement)
    if any(count != 1 for count in occurrences.values()):
        raise ValueError(error)
    return tuple(rows)
