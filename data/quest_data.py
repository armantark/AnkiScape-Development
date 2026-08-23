"""Quest and one-time claim data for AnkiScape."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Dict, Mapping, Tuple, Union

from ..generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG

from .runecrafting_data import RUNEMYSTERIES_SOURCE_PATH, WICKED_HOOD_ITEM

from .firemaking_data import LIT_LIGHT_SOURCE_ITEMS
from .herblore_data import (
    DARKAN_HERB_CLEANING_SOURCE_PATH,
    JUNGLE_POTION_CACHE_SOURCE,
    JUNGLE_POTION_POST_QUEST_SEARCH_SOURCE,
    JUNGLE_POTION_SEARCH_ACTIVITY_IDS,
)
from .varrock_museum_data import varrock_museum_quest_reward_additions_as_dict


RUNE_MYSTERIES_ID = "rune_mysteries"
COOKS_ASSISTANT_ID = "cooks_assistant"
SHIELD_OF_ARRAV_ID = "shield_of_arrav"
IMP_CATCHER_ID = "imp_catcher"
DRUIDIC_RITUAL_ID = "druidic_ritual"
PIRATES_TREASURE_ID = "pirates_treasure"
VAMPYRE_SLAYER_ID = "vampyre_slayer"
THE_RESTLESS_GHOST_ID = "the_restless_ghost"
LOST_CITY_ID = "lost_city"
DEMON_SLAYER_ID = "demon_slayer"
DRAGON_SLAYER_ID = "dragon_slayer"
GOBLIN_DIPLOMACY_ID = "goblin_diplomacy"
ERNEST_THE_CHICKEN_ID = "ernest_the_chicken"
BLACK_KNIGHTS_FORTRESS_ID = "black_knights_fortress"
FIGHT_ARENA_ID = "fight_arena"
LUNAR_DIPLOMACY_ID = "lunar_diplomacy"
MOURNINGS_END_PART_II_ID = "mournings_end_part_ii"
LEGACY_OF_SEERGAZE_ID = "legacy_of_seergaze"
SWAN_SONG_ID = "swan_song"
TAI_BWO_WANNAI_TRIO_ID = "tai_bwo_wannai_trio"
DEFAULT_QUEST_TARGET = RUNE_MYSTERIES_ID

THE_FREMENNIK_TRIALS_ID = "the_fremennik_trials"
SHILO_VILLAGE_ID = "shilo_village"
MOURNINGS_END_PART_I_ID = "mournings_end_part_i"
DARKNESS_OF_HALLOWVALE_ID = "the_darkness_of_hallowvale"
ONE_SMALL_FAVOUR_ID = "one_small_favour"
GARDEN_OF_TRANQUILLITY_ID = "garden_of_tranquillity"
JUNGLE_POTION_ID = "jungle_potion"
KENNITHS_CONCERNS_ID = "kenniths_concerns"
DEADLIEST_CATCH_ID = "deadliest_catch"
WOLF_WHISTLE_ID = "wolf_whistle"
SONG_FROM_THE_DEPTHS_ID = "song_from_the_depths"
CARNILLEAN_RISING_ID = "carnillean_rising"
HAZEEL_CULT_ID = "hazeel_cult"
THE_VOID_STARES_BACK_ID = "the_void_stares_back"
SOME_LIKE_IT_COLD_ID = "some_like_it_cold"
WITCHS_HOUSE_ID = "witchs_house"
MERLINS_CRYSTAL_ID = "merlins_crystal"
DWARF_CANNON_ID = "dwarf_cannon"
FISHING_CONTEST_ID = "fishing_contest"
GERTRUDES_CAT_ID = "gertrudes_cat"
SMOKING_KILLS_ID = "smoking_kills"
CLOCK_TOWER_ID = "clock_tower"
MONKS_FRIEND_ID = "monks_friend"
TRIBAL_TOTEM_ID = "tribal_totem"
SCORPION_CATCHER_ID = "scorpion_catcher"
SHEEP_HERDER_ID = "sheep_herder"
PLAGUE_CITY_ID = "plague_city"
BIOHAZARD_ID = "biohazard"
WATERFALL_QUEST_ID = "waterfall_quest"
FAMILY_CREST_ID = "family_crest"
TEMPLE_OF_IKOV_ID = "temple_of_ikov"
HOLY_GRAIL_ID = "holy_grail"
TREE_GNOME_VILLAGE_ID = "tree_gnome_village"
EAGLES_PEAK_ID = "eagles_peak"
AS_A_FIRST_RESORT_ID = "as_a_first_resort"
ROCKING_OUT_ID = "rocking_out"
THE_KNIGHTS_SWORD_ID = "the_knights_sword"
A_SOULS_BANE_ID = "a_souls_bane"
DEATH_TO_THE_DORGESHUUN_ID = "death_to_the_dorgeshuun"
HEROES_QUEST_ID = "heroes_quest"
SPIRITS_OF_THE_ELID_ID = "spirits_of_the_elid"
ANOTHER_SLICE_OF_H_A_M_ID = "another_slice_of_h_a_m"
LEGENDS_QUEST_ID = "legends_quest"
THE_FEUD_ID = "the_feud"
RFD_FREEING_SIR_AMIK_VARZE_ID = "recipe_for_disaster_freeing_sir_amik_varze"

# Miniquests share the quest ledger, storage and unlock engine; the flag below
# only moves them into their own grouping on the Quests tab. See
# memory-bank/source-audits/miniquest-ledger-2026-07-29.md.
HUNT_FOR_SUROK_ID = "hunt_for_surok"
LAIR_OF_TARN_RAZORLOR_ID = "lair_of_tarn_razorlor"
WHAT_LIES_BELOW_ID = "what_lies_below"
HAUNTED_MINE_ID = "haunted_mine"

RESTLESS_GHOST_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/quests/impl/TheRestlessGhost.kt"
)
RESTLESS_GHOST_SKULL_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/lumbridge/rock_with_skull.plugin.kts"
)
RESTLESS_GHOST_FATHER_URHNEY_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/lumbridge/father_urhney.plugin.kts"
)
RESTLESS_GHOST_DIALOGUE_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/lumbridge/restless_ghost.plugin.kts"
)
RESTLESS_GHOST_COFFIN_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/lumbridge/ghost_coffin.plugin.kts"
)
RESTLESS_GHOST_SKELETON_WARLOCK_NPC_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/npcs/definitions/undeads/skeleton_warlock_lvl_11.plugin.kts"
)
LOST_CITY_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/quests/impl/LostCity.kt"
)
LOST_CITY_WARRIOR_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/lumbridge/warrior.plugin.kts"
)
LOST_CITY_TREE_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/lumbridge/lostcity_tree.plugin.kts"
)
LOST_CITY_SHAMUS_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/lumbridge/shamus.plugin.kts"
)
LOST_CITY_ENTRANA_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/entrana/entrana.plugin.kts"
)
LOST_CITY_SHED_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/lumbridge/lostcity_shed.plugin.kts"
)
LOST_CITY_TREE_SPIRIT_NPC_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/npcs/definitions/undeads/tree_spirit_lv_101.plugin.kts"
)
LOST_CITY_KB_SOURCE = "https://2011.rs/kb/lost_city_members"
LUNAR_DIPLOMACY_SOURCE = "https://www.2011.rs/kb/sym_lunar_diplomacy_members_a_m"
MOURNINGS_END_PART_II_SOURCE = "https://www.2011.rs/kb/mourning_s_ends_part_ii_the_temple_of_light_members"
LEGACY_OF_SEERGAZE_SOURCE = "https://2011.rs/kb/legacy_of_seergaze_members"
SWAN_SONG_SOURCE = "https://www.2011.rs/kb/swan_song_members"
TAI_BWO_WANNAI_TRIO_SOURCE = "https://www.2011.rs/kb/tai_bwo_wannai_trio_members"
DARKAN_QUEST_SOURCE_ROOT = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/"
    "com/rs/game/content/quests"
)
DARKAN_MINIQUEST_SOURCE_ROOT = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/"
    "com/rs/game/content/miniquests"
)
DARKAN_TUTORIAL_SOURCE_ROOT = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/"
    "com/rs/game/content/tutorialisland"
)
DARKAN_NPC_COMBATDEF_ROOT = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs"
)
DARKAN_DEVELOPER_INFO_ROOT = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/developer-information"
)
DARKAN_NPC_LIST_SOURCE = f"{DARKAN_DEVELOPER_INFO_ROOT}/npcList.txt"
DARKAN_BEASTS_SOURCE = f"{DARKAN_DEVELOPER_INFO_ROOT}/beasts.txt"
DARKAN_ENUMS_SOURCE = f"{DARKAN_DEVELOPER_INFO_ROOT}/enums.txt"
STOLEN_HEARTS_WIKI_SOURCE = "https://runescape.wiki/w/Stolen_Hearts?oldid=6579723"
STOLEN_HEARTS_QUICK_GUIDE_SOURCE = (
    "https://runescape.wiki/w/Stolen_Hearts%2FQuick_guide?oldid=6315136"
)
STOLEN_HEARTS_CACHE_SOURCE = (
    "/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/"
    "extracted/742-2012-11-07/cache"
)
DIAMOND_IN_THE_ROUGH_WIKI_SOURCE = (
    "https://runescape.wiki/w/Diamond_in_the_Rough?oldid=6563227"
)
DIAMOND_IN_THE_ROUGH_QUICK_GUIDE_SOURCE = (
    "https://runescape.wiki/w/Diamond_in_the_Rough%2FQuick_guide?oldid=6319548"
)
DIAMOND_IN_THE_ROUGH_CACHE_SOURCE = STOLEN_HEARTS_CACHE_SOURCE
ICTHLARINS_LITTLE_HELPER_WIKI_SOURCE = (
    "https://runescape.wiki/w/Icthlarin%27s_Little_Helper?oldid=6588923"
)
ICTHLARINS_LITTLE_HELPER_CACHE_SOURCE = STOLEN_HEARTS_CACHE_SOURCE
ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE = (
    f"{DARKAN_QUEST_SOURCE_ROOT}/icthlarins_little_helper/IcthlarinsLittleHelper.kt"
)
ICTHLARINS_LITTLE_HELPER_POSSESSED_PRIEST_SOURCE = (
    f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/possessed_priest (noanims).json"
)
SMOKING_KILLS_WIKI_SOURCE = "https://runescape.wiki/w/Smoking_Kills?oldid=6548001"
SMOKING_KILLS_MUMMY_SOURCE = "https://runescape.wiki/w/Mummy_Warrior?oldid=6573394"
SMOKING_KILLS_MIGHTY_BANSHEE_SOURCE = "https://runescape.wiki/w/Mighty_banshee?oldid=6530631"
SMOKING_KILLS_MISTRESS_SOURCE = "https://runescape.wiki/w/Banshee_Mistress?oldid=6529627"
SMOKING_KILLS_MUMMY_DARKAN_SOURCE = (
    f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/mummy_warrior (nostats) (noanims).json"
)
SMOKING_KILLS_MIGHTY_BANSHEE_DARKAN_SOURCE = (
    f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/mighty_banshee (nostats).json"
)
SMOKING_KILLS_MISTRESS_DARKAN_SOURCE = (
    f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/banshee_mistress/"
    "banshee_mistress_(111) (nostats) (noanims).json"
)
MINIQUEST_LIST_SOURCE = "https://runescape.wiki/w/Miniquests?oldid=6020341"
HUNT_FOR_SUROK_WIKI_SOURCE = (
    "https://runescape.wiki/w/The_Hunt_for_Surok_%28miniquest%29?oldid=6097199"
)
HUNT_FOR_SUROK_BORK_SOURCE = "https://runescape.wiki/w/Bork?oldid=6565904"
HUNT_FOR_SUROK_DARKAN_SOURCE = f"{DARKAN_MINIQUEST_SOURCE_ROOT}/huntforsurok/HuntForSurok.kt"
HUNT_FOR_SUROK_MINIQUEST_ENUM_SOURCE = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
    "src/main/java/com/rs/engine/miniquest/Miniquest.java"
)
HUNT_FOR_SUROK_BORK_DARKAN_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/bork (nostats).json"
HUNT_FOR_SUROK_BORK_HANDLER_SOURCE = (
    f"{DARKAN_MINIQUEST_SOURCE_ROOT}/huntforsurok/bork/Bork.kt"
)
LAIR_OF_TARN_RAZORLOR_WIKI_SOURCE = (
    "https://runescape.wiki/w/Lair_of_Tarn_Razorlor_%28miniquest%29?oldid=6448364"
)
LAIR_OF_TARN_RAZORLOR_TARN_SOURCE = "https://runescape.wiki/w/Tarn?oldid=6448021"
LAIR_OF_TARN_RAZORLOR_TERROR_DOG_SOURCE = "https://runescape.wiki/w/Terror_dog?oldid=6547220"
LAIR_OF_TARN_RAZORLOR_TARN_DARKAN_SOURCE = (
    f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/tarn (noanims).json"
)
LAIR_OF_TARN_RAZORLOR_MUTANT_TARN_DARKAN_SOURCE = (
    f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/mutant_tarn (nostats) (noanims).json"
)
LAIR_OF_TARN_RAZORLOR_TERROR_DOG_DARKAN_SOURCE = (
    f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/terror_dog/terror_dog_(110) (noanims).json"
)
DARKAN_TUTORIAL_COMBAT_INSTRUCTOR_SOURCE = f"{DARKAN_TUTORIAL_SOURCE_ROOT}/CombatInstructor.java"
DARKAN_TUTORIAL_MAGIC_INSTRUCTOR_SOURCE = f"{DARKAN_TUTORIAL_SOURCE_ROOT}/MagicInstructor.java"
DARKAN_TUTORIAL_MINING_INSTRUCTOR_SOURCE = f"{DARKAN_TUTORIAL_SOURCE_ROOT}/MiningInstructor.java"
DARKAN_TUTORIAL_SURVIVAL_EXPERT_SOURCE = f"{DARKAN_TUTORIAL_SOURCE_ROOT}/SurvivalExpert.java"
DARKAN_TUTORIAL_STARTER_KIT_SOURCE = "; ".join(
    (
        f"{DARKAN_TUTORIAL_COMBAT_INSTRUCTOR_SOURCE}:50-60",
        f"{DARKAN_TUTORIAL_MAGIC_INSTRUCTOR_SOURCE}:43-47",
        f"{DARKAN_TUTORIAL_MINING_INSTRUCTOR_SOURCE}:51-59",
        f"{DARKAN_TUTORIAL_SURVIVAL_EXPERT_SOURCE}:41-50",
    )
)
DARKAN_DEMON_SLAYER_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/demonslayer"
DARKAN_DEMON_SLAYER_SOURCE = f"{DARKAN_DEMON_SLAYER_SOURCE_ROOT}/DemonSlayer.java"
DARKAN_DEMON_SLAYER_GYPSY_SOURCE = f"{DARKAN_DEMON_SLAYER_SOURCE_ROOT}/GypsyArisDemonSlayerD.java"
DARKAN_DEMON_SLAYER_SIR_PRYSIN_SOURCE = f"{DARKAN_DEMON_SLAYER_SOURCE_ROOT}/SirPrysinDemonSlayerD.java"
DARKAN_DEMON_SLAYER_TRAIBORN_SOURCE = f"{DARKAN_DEMON_SLAYER_SOURCE_ROOT}/WizardTraibornDemonSlayerD.java"
DARKAN_DEMON_SLAYER_ROVIN_SOURCE = f"{DARKAN_DEMON_SLAYER_SOURCE_ROOT}/CaptainRovinDemonSlayerD.java"
DARKAN_DEMON_SLAYER_DELRITH_SOURCE = f"{DARKAN_DEMON_SLAYER_SOURCE_ROOT}/DelrithBoss.java"
DARKAN_DEMON_SLAYER_DELRITH_CONTROLLER_SOURCE = f"{DARKAN_DEMON_SLAYER_SOURCE_ROOT}/PlayerVSDelrithController.java"
DARKAN_DEMON_SLAYER_INCANTATION_SOURCE = f"{DARKAN_DEMON_SLAYER_SOURCE_ROOT}/EncantationOptionsD.java"
DARKAN_DEMON_SLAYER_DELRITH_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/delrith (nostats).json"
DARKAN_DRAGON_SLAYER_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/dragonslayer"
DARKAN_DRAGON_SLAYER_SOURCE = f"{DARKAN_DRAGON_SLAYER_SOURCE_ROOT}/DragonSlayer.java"
DARKAN_DRAGON_SLAYER_GUILDMASTER_SOURCE = f"{DARKAN_DRAGON_SLAYER_SOURCE_ROOT}/GuildMasterDragonSlayerD.java"
DARKAN_DRAGON_SLAYER_OZIACH_SOURCE = f"{DARKAN_DRAGON_SLAYER_SOURCE_ROOT}/OziachDragonSlayerD.java"
DARKAN_DRAGON_SLAYER_ORACLE_SOURCE = f"{DARKAN_DRAGON_SLAYER_SOURCE_ROOT}/OracleDragonSlayerD.java"
DARKAN_DRAGON_SLAYER_MELZARS_MAZE_SOURCE = f"{DARKAN_DRAGON_SLAYER_SOURCE_ROOT}/MelzarsMaze.java"
DARKAN_DRAGON_SLAYER_WORMBRAIN_SOURCE = f"{DARKAN_DRAGON_SLAYER_SOURCE_ROOT}/WormBrainDragonSlayerMob.java"
DARKAN_DRAGON_SLAYER_KLARENSE_SOURCE = f"{DARKAN_DRAGON_SLAYER_SOURCE_ROOT}/KlarenseDragonSlayerD.java"
DARKAN_DRAGON_SLAYER_NED_SOURCE = f"{DARKAN_DRAGON_SLAYER_SOURCE_ROOT}/NedDragonSlayerD.java"
DARKAN_DRAGON_SLAYER_CAPTAIN_NED_SOURCE = f"{DARKAN_DRAGON_SLAYER_SOURCE_ROOT}/CaptainNedDragonSlayerD.java"
DARKAN_DRAGON_SLAYER_BOAT_SCENE_SOURCE = f"{DARKAN_DRAGON_SLAYER_SOURCE_ROOT}/DragonSlayer_BoatScene.java"
DARKAN_DRAGON_SLAYER_ELVARG_SOURCE = f"{DARKAN_DRAGON_SLAYER_SOURCE_ROOT}/ElvargBoss.java"
DARKAN_DRAGON_SLAYER_ELVARG_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/elvarg.json"
DARKAN_DRAGON_SLAYER_MELZAR_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/melzar_the_mad.json"
DARKAN_DRAGON_SLAYER_ZOMBIE_RAT_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/zombie_rat.json"
DARKAN_DRAGON_SLAYER_WORMBRAIN_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/wormbrain.json"
DARKAN_GOBLIN_DIPLOMACY_SOURCE = f"{DARKAN_QUEST_SOURCE_ROOT}/goblindiplomacy/GoblinDiplomacy.java"
DARKAN_ERNEST_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/ernestthechicken"
DARKAN_ERNEST_SOURCE = f"{DARKAN_ERNEST_SOURCE_ROOT}/ErnestTheChicken.java"
DARKAN_ERNEST_ODDENSTEIN_SOURCE = f"{DARKAN_ERNEST_SOURCE_ROOT}/OddensteinErnestChickenD.java"
DARKAN_BLACK_KNIGHTS_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/blackknightsfortress"
DARKAN_BLACK_KNIGHTS_SOURCE = f"{DARKAN_BLACK_KNIGHTS_SOURCE_ROOT}/BlackKnightsFortress.java"
DARKAN_BLACK_KNIGHTS_SIR_AMIK_SOURCE = f"{DARKAN_BLACK_KNIGHTS_SOURCE_ROOT}/SirAmikVarzeBlackKnightsFortressD.java"
DARKAN_DWARF_CANNON_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/dwarfcannon"
DARKAN_DWARF_CANNON_SOURCE = f"{DARKAN_DWARF_CANNON_SOURCE_ROOT}/DwarfCannon.java"
DARKAN_DWARF_CANNON_LAWGOF_SOURCE = f"{DARKAN_DWARF_CANNON_SOURCE_ROOT}/CaptainLawgofD.java"
DARKAN_DWARF_CANNON_LOLLK_SOURCE = f"{DARKAN_DWARF_CANNON_SOURCE_ROOT}/LollkD.java"
DARKAN_DWARF_CANNON_NULODION_SOURCE = f"{DARKAN_DWARF_CANNON_SOURCE_ROOT}/NulodionD.java"
DARKAN_FISHING_SOURCE_ROOT = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/"
    "com/rs/game/content/skills/fishing"
)
DARKAN_FISHING_SKILL_SOURCE = f"{DARKAN_FISHING_SOURCE_ROOT}/Fishing.java"
DARKAN_FISHING_FISH_SOURCE = f"{DARKAN_FISHING_SOURCE_ROOT}/Fish.java"
DARKAN_FISHING_SPOT_SOURCE = f"{DARKAN_FISHING_SOURCE_ROOT}/FishingSpot.java"
DARKAN_FISHING_CONTEST_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/fishingcontest"
DARKAN_FISHING_CONTEST_SOURCE = f"{DARKAN_FISHING_CONTEST_SOURCE_ROOT}/FishingContest.java"
DARKAN_FISHING_CONTEST_DWARF_BROTHERS_SOURCE = (
    f"{DARKAN_FISHING_CONTEST_SOURCE_ROOT}/DwarfBrothersFishingContestD.java"
)
DARKAN_FISHING_CONTEST_BONZO_SOURCE = f"{DARKAN_FISHING_CONTEST_SOURCE_ROOT}/BonzoFishingContestD.java"
DARKAN_FISHING_CONTEST_GRANDPA_JACK_SOURCE = (
    f"{DARKAN_FISHING_CONTEST_SOURCE_ROOT}/GrandpaJackFishingContestD.java"
)
DARKAN_FISHING_CONTEST_MORRIS_SOURCE = f"{DARKAN_FISHING_CONTEST_SOURCE_ROOT}/MorrisFishingContestD.java"
DARKAN_FISHING_CONTEST_WIKI_SOURCE = "https://runescape.wiki/w/Fishing_Contest?oldid=6326002"
DARKAN_GERTRUDES_CAT_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/gertrudescat"
DARKAN_GERTRUDES_CAT_SOURCE = f"{DARKAN_GERTRUDES_CAT_SOURCE_ROOT}/GertrudesCat.java"
DARKAN_GERTRUDES_CAT_GERTRUDE_SOURCE = f"{DARKAN_GERTRUDES_CAT_SOURCE_ROOT}/GertrudeD.java"
DARKAN_GERTRUDES_CAT_CHILDREN_SOURCE = f"{DARKAN_GERTRUDES_CAT_SOURCE_ROOT}/ShilopWiloughD.java"
DARKAN_CLOCK_TOWER_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/clocktower"
DARKAN_CLOCK_TOWER_SOURCE = f"{DARKAN_CLOCK_TOWER_SOURCE_ROOT}/ClockTower.java"
DARKAN_CLOCK_TOWER_DUNGEON_SOURCE = f"{DARKAN_CLOCK_TOWER_SOURCE_ROOT}/ClockTowerDungeon.java"
DARKAN_CLOCK_TOWER_KOJO_SOURCE = f"{DARKAN_CLOCK_TOWER_SOURCE_ROOT}/BrotherKojoClockTowerD.java"
DARKAN_MONKS_FRIEND_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/monksfriend"
DARKAN_MONKS_FRIEND_SOURCE = f"{DARKAN_MONKS_FRIEND_SOURCE_ROOT}/MonksFriend.java"
DARKAN_MONKS_FRIEND_OMAD_SOURCE = f"{DARKAN_MONKS_FRIEND_SOURCE_ROOT}/dialogues/BrotherOmadMonksFriendD.java"
DARKAN_MONKS_FRIEND_CEDRIC_SOURCE = f"{DARKAN_MONKS_FRIEND_SOURCE_ROOT}/dialogues/BrotherCedricMonksFriendD.java"
DARKAN_TRIBAL_TOTEM_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/tribaltotem"
DARKAN_TRIBAL_TOTEM_SOURCE = f"{DARKAN_TRIBAL_TOTEM_SOURCE_ROOT}/TribalTotem.java"
DARKAN_TRIBAL_TOTEM_KANGAI_SOURCE = f"{DARKAN_TRIBAL_TOTEM_SOURCE_ROOT}/KangaiMauTribalTotemD.java"
DARKAN_TRIBAL_TOTEM_WIZARD_SOURCE = f"{DARKAN_TRIBAL_TOTEM_SOURCE_ROOT}/WizardCrompertyTribalTotemD.java"
DARKAN_TRIBAL_TOTEM_RPDT_SOURCE = f"{DARKAN_TRIBAL_TOTEM_SOURCE_ROOT}/RPDTEmployeeTribalTotemD.java"
DARKAN_SCORPION_CATCHER_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/scorpioncatcher"
DARKAN_SCORPION_CATCHER_SOURCE = f"{DARKAN_SCORPION_CATCHER_SOURCE_ROOT}/ScorpionCatcher.java"
DARKAN_SCORPION_CATCHER_THORMAC_SOURCE = f"{DARKAN_SCORPION_CATCHER_SOURCE_ROOT}/ThormacScorpionCatcherD.java"
DARKAN_SCORPION_CATCHER_SEER_SOURCE = f"{DARKAN_SCORPION_CATCHER_SOURCE_ROOT}/SeerScorpionCatcherD.java"
DARKAN_SCORPION_CATCHER_KHAZ_SCORP_SOURCE = f"{DARKAN_SCORPION_CATCHER_SOURCE_ROOT}/KhazScorp.java"
DARKAN_SCORPION_CATCHER_JAILER_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/jailer.json"
DARKAN_SHEEP_HERDER_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/sheep_herder"
DARKAN_SHEEP_HERDER_SOURCE = f"{DARKAN_SHEEP_HERDER_SOURCE_ROOT}/SheepHerder.kt"
DARKAN_SHEEP_HERDER_COUNCILLOR_SOURCE = f"{DARKAN_SHEEP_HERDER_SOURCE_ROOT}/dialogues/CouncillorHalgrivesD.kt"
DARKAN_SHEEP_HERDER_DOCTOR_SOURCE = f"{DARKAN_SHEEP_HERDER_SOURCE_ROOT}/dialogues/DoctorOrbonD.kt"
DARKAN_SHEEP_HERDER_FARMER_SOURCE = f"{DARKAN_SHEEP_HERDER_SOURCE_ROOT}/dialogues/FarmerBrumtyD.kt"
DARKAN_SHEEP_HERDER_UTILS_SOURCE = f"{DARKAN_SHEEP_HERDER_SOURCE_ROOT}/utils/SheepHerderUtils.kt"
DARKAN_SHEEP_HERDER_CONSTANTS_SOURCE = f"{DARKAN_SHEEP_HERDER_SOURCE_ROOT}/utils/SheepHerderConstants.kt"
DARKAN_PLAGUE_CITY_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/plague_city"
DARKAN_PLAGUE_CITY_SOURCE = f"{DARKAN_PLAGUE_CITY_SOURCE_ROOT}/PlagueCity.kt"
DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE = f"{DARKAN_PLAGUE_CITY_SOURCE_ROOT}/utils/PlagueCityConstants.kt"
DARKAN_PLAGUE_CITY_UTILS_SOURCE = f"{DARKAN_PLAGUE_CITY_SOURCE_ROOT}/utils/PlagueCityUtils.kt"
DARKAN_PLAGUE_CITY_CUTSCENE_SOURCE = f"{DARKAN_PLAGUE_CITY_SOURCE_ROOT}/cutscene/PlagueCityCutscene.kt"
DARKAN_PLAGUE_CITY_EDMOND_SOURCE = f"{DARKAN_PLAGUE_CITY_SOURCE_ROOT}/dialogues/npcs/EdmondD.kt"
DARKAN_PLAGUE_CITY_ALRENA_SOURCE = f"{DARKAN_PLAGUE_CITY_SOURCE_ROOT}/dialogues/npcs/AlrenaD.kt"
DARKAN_PLAGUE_CITY_PICTURE_SPAWN_SOURCE = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/"
    "data/items/spawns/areas/kandarin.json"
)
DARKAN_PLAGUE_CITY_JETHICK_SOURCE = f"{DARKAN_PLAGUE_CITY_SOURCE_ROOT}/dialogues/npcs/JethickD.kt"
DARKAN_PLAGUE_CITY_REHNISON_DOOR_SOURCE = (
    f"{DARKAN_PLAGUE_CITY_SOURCE_ROOT}/dialogues/objects/RehnisonDoorD.kt"
)
DARKAN_PLAGUE_CITY_MARTHA_SOURCE = f"{DARKAN_PLAGUE_CITY_SOURCE_ROOT}/dialogues/npcs/MarthaRehnisonD.kt"
DARKAN_PLAGUE_CITY_MILLI_SOURCE = f"{DARKAN_PLAGUE_CITY_SOURCE_ROOT}/dialogues/npcs/MilliRehnisonD.kt"
DARKAN_PLAGUE_CITY_PRISON_DOOR_SOURCE = (
    f"{DARKAN_PLAGUE_CITY_SOURCE_ROOT}/dialogues/objects/PrisonHouseDoorsD.kt"
)
DARKAN_PLAGUE_CITY_CLERK_SOURCE = f"{DARKAN_PLAGUE_CITY_SOURCE_ROOT}/dialogues/npcs/ClerkD.kt"
DARKAN_PLAGUE_CITY_BRAVEK_SOURCE = f"{DARKAN_PLAGUE_CITY_SOURCE_ROOT}/dialogues/npcs/BravekD.kt"
DARKAN_PLAGUE_CITY_ELENA_DOOR_SOURCE = (
    f"{DARKAN_PLAGUE_CITY_SOURCE_ROOT}/dialogues/objects/ElenaPrisonDoorD.kt"
)
DARKAN_PLAGUE_CITY_ELENA_SOURCE = f"{DARKAN_PLAGUE_CITY_SOURCE_ROOT}/dialogues/npcs/ElenaD.kt"
DARKAN_BIOHAZARD_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/biohazard"
DARKAN_BIOHAZARD_SOURCE = f"{DARKAN_BIOHAZARD_SOURCE_ROOT}/Biohazard.kt"
DARKAN_BIOHAZARD_CONSTANTS_SOURCE = f"{DARKAN_BIOHAZARD_SOURCE_ROOT}/utils/BiohazardConstants.kt"
DARKAN_BIOHAZARD_UTILS_SOURCE = f"{DARKAN_BIOHAZARD_SOURCE_ROOT}/utils/BiohazardUtils.kt"
DARKAN_BIOHAZARD_ELENA_SOURCE = (
    f"{DARKAN_BIOHAZARD_SOURCE_ROOT}/dialogue/npcs/east_ardougne/ElenaD.kt"
)
DARKAN_BIOHAZARD_JERICO_SOURCE = (
    f"{DARKAN_BIOHAZARD_SOURCE_ROOT}/dialogue/npcs/east_ardougne/JericoD.kt"
)
DARKAN_BIOHAZARD_OMART_SOURCE = (
    f"{DARKAN_BIOHAZARD_SOURCE_ROOT}/dialogue/npcs/east_ardougne/OmartD.kt"
)
DARKAN_BIOHAZARD_KING_SOURCE = (
    f"{DARKAN_BIOHAZARD_SOURCE_ROOT}/dialogue/npcs/east_ardougne/KingLathasD.kt"
)
DARKAN_BIOHAZARD_KILRON_SOURCE = (
    f"{DARKAN_BIOHAZARD_SOURCE_ROOT}/dialogue/npcs/west_ardougne/KilronD.kt"
)
DARKAN_BIOHAZARD_CHEMIST_SOURCE = (
    f"{DARKAN_BIOHAZARD_SOURCE_ROOT}/dialogue/npcs/rimmington/ChemistD.kt"
)
DARKAN_BIOHAZARD_RIMMINGTON_HOPS_SOURCE = (
    f"{DARKAN_BIOHAZARD_SOURCE_ROOT}/dialogue/npcs/rimmington/HopsD.kt"
)
DARKAN_BIOHAZARD_RIMMINGTON_DA_VINCI_SOURCE = (
    f"{DARKAN_BIOHAZARD_SOURCE_ROOT}/dialogue/npcs/rimmington/DaVinciD.kt"
)
DARKAN_BIOHAZARD_RIMMINGTON_CHANCY_SOURCE = (
    f"{DARKAN_BIOHAZARD_SOURCE_ROOT}/dialogue/npcs/rimmington/ChancyD.kt"
)
DARKAN_BIOHAZARD_VARROCK_HOPS_SOURCE = (
    f"{DARKAN_BIOHAZARD_SOURCE_ROOT}/dialogue/npcs/east_varrock/HopsD.kt"
)
DARKAN_BIOHAZARD_VARROCK_DA_VINCI_SOURCE = (
    f"{DARKAN_BIOHAZARD_SOURCE_ROOT}/dialogue/npcs/east_varrock/DaVinciD.kt"
)
DARKAN_BIOHAZARD_VARROCK_CHANCY_SOURCE = (
    f"{DARKAN_BIOHAZARD_SOURCE_ROOT}/dialogue/npcs/east_varrock/ChancyD.kt"
)
DARKAN_BIOHAZARD_GUIDOR_SOURCE = (
    f"{DARKAN_BIOHAZARD_SOURCE_ROOT}/dialogue/npcs/east_varrock/GuidorD.kt"
)
DARKAN_BIOHAZARD_GUIDOR_WIFE_SOURCE = (
    f"{DARKAN_BIOHAZARD_SOURCE_ROOT}/dialogue/npcs/east_varrock/GuidorWifeD.kt"
)
DARKAN_BIOHAZARD_VARROCK_GUARD_SOURCE = (
    f"{DARKAN_BIOHAZARD_SOURCE_ROOT}/dialogue/npcs/east_varrock/GuardD.kt"
)
DARKAN_BIOHAZARD_GUIDOR_DOOR_SOURCE = (
    f"{DARKAN_BIOHAZARD_SOURCE_ROOT}/dialogue/objects/east_varrock/GuidorDoorD.kt"
)
DARKAN_BIOHAZARD_VARROCK_GATE_SOURCE = (
    f"{DARKAN_BIOHAZARD_SOURCE_ROOT}/dialogue/objects/east_varrock/GuardGateD.kt"
)
DARKAN_BIOHAZARD_MOURNER_HQ_DOORS_SOURCE = (
    f"{DARKAN_BIOHAZARD_SOURCE_ROOT}/dialogue/objects/west_ardougne/MournerHQDoorsD.kt"
)
DARKAN_BIOHAZARD_MOURNER_SOURCE = (
    f"{DARKAN_BIOHAZARD_SOURCE_ROOT}/instances/npcs/MournerWithKey.kt"
)
DARKAN_BIOHAZARD_MOURNER_NPC_SOURCE = (
    f"{DARKAN_NPC_COMBATDEF_ROOT}/areas/west_ardougne/mourner/mourner_(13).json"
)
DARKAN_WATERFALL_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/waterfallquest"
DARKAN_WATERFALL_SOURCE = f"{DARKAN_WATERFALL_SOURCE_ROOT}/WaterfallQuest.java"
DARKAN_WATERFALL_ALMERA_SOURCE = f"{DARKAN_WATERFALL_SOURCE_ROOT}/AlmeraD.java"
DARKAN_WATERFALL_HUDON_SOURCE = f"{DARKAN_WATERFALL_SOURCE_ROOT}/HudonD.java"
DARKAN_WATERFALL_GOLRIE_SOURCE = f"{DARKAN_WATERFALL_SOURCE_ROOT}/GolrieD.java"
DARKAN_WATERFALL_BOOK_SOURCE = f"{DARKAN_WATERFALL_SOURCE_ROOT}/books/BookOnBaxtorian.java"
DARKAN_FIGHT_ARENA_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/fightarena"
DARKAN_FIGHT_ARENA_SOURCE = f"{DARKAN_FIGHT_ARENA_SOURCE_ROOT}/FightArena.java"
DARKAN_FIGHT_ARENA_CUTSCENE_SOURCE = f"{DARKAN_FIGHT_ARENA_SOURCE_ROOT}/FightArenaFightCutsceneController.java"
DARKAN_FIGHT_ARENA_LADY_SOURCE = f"{DARKAN_FIGHT_ARENA_SOURCE_ROOT}/dialogue/LadyServilFightArenaD.java"
DARKAN_FIGHT_ARENA_JEREMY_SOURCE = f"{DARKAN_FIGHT_ARENA_SOURCE_ROOT}/dialogue/JeremyServilFightArenaD.java"
DARKAN_FIGHT_ARENA_LAZY_GUARD_SOURCE = f"{DARKAN_FIGHT_ARENA_SOURCE_ROOT}/dialogue/LazyGuardFightArenaD.java"
DARKAN_FIGHT_ARENA_ANGOR_SOURCE = f"{DARKAN_FIGHT_ARENA_SOURCE_ROOT}/dialogue/AngorFightArenaD.java"
DARKAN_FIGHT_ARENA_BOUNCER_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/bouncer/bouncer_(137).json"
DARKAN_FIGHT_ARENA_KHAZARD_OGRE_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/khazard_ogre (nostats).json"
DARKAN_FIGHT_ARENA_KHAZARD_SCORPION_NPC_SOURCE = (
    f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/khazard_scorpion (nostats) (noanims).json"
)
SCAPE_2011_ITEM_IDENTITY_SOURCE = "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml"
ELEMENTAL_WORKSHOP_II_DARKAN_COMMIT = "fd901261fbf3a3ccee75236c422765c9d9383f4a"
ELEMENTAL_WORKSHOP_II_DARKAN_SOURCE = (
    f"{DARKAN_QUEST_SOURCE_ROOT}/elemental_workshop/ElementalWorkshopII.kt"
    f" @ {ELEMENTAL_WORKSHOP_II_DARKAN_COMMIT}"
)
ELEMENTAL_WORKSHOP_II_REV_727_CACHE_SOURCE = (
    "/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/"
    "extracted/727-2012-07-24/cache"
)
ELEMENTAL_WORKSHOP_II_REV_742_CACHE_SOURCE = (
    "/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/"
    "extracted/742-2012-11-07/cache"
)
ELEMENTAL_WORKSHOP_II_WIKI_SOURCE = "https://runescape.wiki/w/Elemental_Workshop_II?oldid=6358871"
ELEMENTAL_WORKSHOP_II_QUICK_GUIDE_SOURCE = (
    "https://runescape.wiki/w/Elemental_Workshop_II%2FQuick_guide?oldid=6333340"
)
ELEMENTAL_WORKSHOP_II_STAGE_ONE_SOURCE = (
    f"{ELEMENTAL_WORKSHOP_II_DARKAN_SOURCE}; {ELEMENTAL_WORKSHOP_II_REV_727_CACHE_SOURCE}; "
    f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}; {ELEMENTAL_WORKSHOP_II_REV_742_CACHE_SOURCE}; "
    f"{ELEMENTAL_WORKSHOP_II_WIKI_SOURCE}; {ELEMENTAL_WORKSHOP_II_QUICK_GUIDE_SOURCE}"
)
SHIELD_OF_ARRAV_WIKI_SOURCE = "https://runescape.wiki/w/Shield_of_Arrav?oldid=6326184"
SCAPE_2011_VARROCK_RELDO_SOURCE = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/varrock/reldo.plugin.kts"
)
DARKAN_SHIELD_OF_ARRAV_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/shieldofarrav"
DARKAN_SHIELD_OF_ARRAV_SOURCE = f"{DARKAN_SHIELD_OF_ARRAV_SOURCE_ROOT}/ShieldOfArrav.java"
DARKAN_SHIELD_OF_ARRAV_RELDO_SOURCE = f"{DARKAN_SHIELD_OF_ARRAV_SOURCE_ROOT}/ReldoShieldOfArravD.java"
DARKAN_SHIELD_OF_ARRAV_BARAEK_SOURCE = f"{DARKAN_SHIELD_OF_ARRAV_SOURCE_ROOT}/BaraekShieldOfArravD.java"
DARKAN_SHIELD_OF_ARRAV_CHARLIE_SOURCE = f"{DARKAN_SHIELD_OF_ARRAV_SOURCE_ROOT}/CharlieTheTrampArravD.java"
DARKAN_SHIELD_OF_ARRAV_STRAVEN_SOURCE = f"{DARKAN_SHIELD_OF_ARRAV_SOURCE_ROOT}/StravenShieldOfArravD.java"
DARKAN_SHIELD_OF_ARRAV_KATRINE_SOURCE = f"{DARKAN_SHIELD_OF_ARRAV_SOURCE_ROOT}/KatrineShieldOfArravD.java"
DARKAN_SHIELD_OF_ARRAV_CURATOR_SOURCE = f"{DARKAN_SHIELD_OF_ARRAV_SOURCE_ROOT}/MuseumCuratorArravD.java"
DARKAN_SHIELD_OF_ARRAV_KING_SOURCE = f"{DARKAN_SHIELD_OF_ARRAV_SOURCE_ROOT}/KingRoaldShieldOfArravD.java"
DARKAN_SHIELD_OF_ARRAV_BOOK_SOURCE = f"{DARKAN_SHIELD_OF_ARRAV_SOURCE_ROOT}/BookShieldOfArrav.java"
DARKAN_SHIELD_OF_ARRAV_JONNY_DROPS_SOURCE = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/drops/johnny_the_beard.json"
)
DARKAN_SHIELD_OF_ARRAV_JONNY_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/jonny_the_beard.json"
DARKAN_SHIELD_OF_ARRAV_WEAPONSMASTER_NPC_SOURCE = (
    f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/weaponsmaster.json"
)
DARKAN_LOST_CITY_SOURCE = f"{DARKAN_QUEST_SOURCE_ROOT}/lostcity/LostCity.java"
DARKAN_JUNGLE_POTION_SOURCE = f"{DARKAN_QUEST_SOURCE_ROOT}/junglepotion/JunglePotion.java"
DARKAN_JUNGLE_POTION_TRUFITUS_SOURCE = f"{DARKAN_QUEST_SOURCE_ROOT}/TrufitusDialog.kt"
DARKAN_WOLF_WHISTLE_SOURCE = f"{DARKAN_QUEST_SOURCE_ROOT}/wolfwhistle/WolfWhistle.java"
HEROES_QUEST_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/heroesquest"
HEROES_QUEST_DARKAN_SOURCE = f"{HEROES_QUEST_SOURCE_ROOT}/HeroesQuest.java"
HEROES_QUEST_ACHIETTIES_SOURCE = f"{HEROES_QUEST_SOURCE_ROOT}/dialogues/AchiettiesHeroesQuestD.java"
HEROES_QUEST_BRIMHAVEN_SOURCE = f"{HEROES_QUEST_SOURCE_ROOT}/BrimhavenHeroesQuest.java"
HEROES_QUEST_KATRINE_SOURCE = f"{HEROES_QUEST_SOURCE_ROOT}/dialogues/KatrineHeroesQuestD.java"
HEROES_QUEST_STRAVEN_SOURCE = f"{HEROES_QUEST_SOURCE_ROOT}/dialogues/StravenHeroesQuestD.java"
HEROES_QUEST_TROBERT_SOURCE = f"{HEROES_QUEST_SOURCE_ROOT}/dialogues/TrobertHeroesQuestD.java"
HEROES_QUEST_ALFONSO_SOURCE = f"{HEROES_QUEST_SOURCE_ROOT}/dialogues/AlfonsoTheWaiterHeroesQuestD.java"
HEROES_QUEST_CHARLIE_SOURCE = f"{HEROES_QUEST_SOURCE_ROOT}/dialogues/CharlieTheCookHeroesQuestD.java"
HEROES_QUEST_MANSION_DOOR_SOURCE = f"{HEROES_QUEST_SOURCE_ROOT}/dialogues/MansionDoorHeroesQuestD.java"
HEROES_QUEST_ICE_QUEEN_DUNGEON_SOURCE = f"{HEROES_QUEST_SOURCE_ROOT}/icequeenlair/IceQueenDungeon.java"
HEROES_QUEST_PORT_SARIM_SOURCE = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/"
    "com/rs/game/content/world/areas/port_sarim/PortSarim.java"
)
HEROES_QUEST_HERBLORE_SOURCE = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/"
    "com/rs/game/content/skills/herblore/CraftablePotion.java"
)
HEROES_QUEST_FISH_SOURCE = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/"
    "com/rs/game/content/skills/fishing/Fish.java"
)
HEROES_QUEST_FISHING_SPOT_SOURCE = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/"
    "com/rs/game/content/skills/fishing/FishingSpot.java"
)
HEROES_QUEST_FISHING_SOURCE = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/"
    "com/rs/game/content/skills/fishing/Fishing.java"
)
HEROES_QUEST_COOKING_SOURCE = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/"
    "com/rs/game/content/skills/cooking/Cooking.java"
)
HEROES_QUEST_ENTRANA_FIREBIRD_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/entrana_firebird.json"
HEROES_QUEST_GRIP_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/grip.json"
HEROES_QUEST_ICE_QUEEN_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/ice_queen.json"
FAMILY_CREST_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/familycrest"
FAMILY_CREST_DARKAN_SOURCE = f"{FAMILY_CREST_SOURCE_ROOT}/FamilyCrest.kt"
FAMILY_CREST_DIMINTHEIS_SOURCE = f"{FAMILY_CREST_SOURCE_ROOT}/dialogues/DimintheisFamilyCrestD.java"
FAMILY_CREST_CALEB_SOURCE = f"{FAMILY_CREST_SOURCE_ROOT}/dialogues/CalebFamilyCrestD.java"
FAMILY_CREST_GEM_TRADER_SOURCE = f"{FAMILY_CREST_SOURCE_ROOT}/dialogues/GemTraderFamilyCrestD.java"
FAMILY_CREST_AVAN_SOURCE = f"{FAMILY_CREST_SOURCE_ROOT}/dialogues/AvanFamilyCrestD.java"
FAMILY_CREST_BOOT_SOURCE = f"{FAMILY_CREST_SOURCE_ROOT}/dialogues/BootFamilyCrestD.java"
FAMILY_CREST_JOHNATHON_SOURCE = f"{FAMILY_CREST_SOURCE_ROOT}/dialogues/JohnathonFamilyCrestD.java"
FAMILY_CREST_CHRONOZON_SOURCE = f"{FAMILY_CREST_SOURCE_ROOT}/ChronozonBoss.java"
FAMILY_CREST_WITCHHAVEN_PUZZLE_SOURCE = f"{FAMILY_CREST_SOURCE_ROOT}/WitchHavenPuzzleFamilyCrest.java"
FAMILY_CREST_CHRONOZON_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/chronozon (noanims).json"
TEMPLE_OF_IKOV_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/templeofikov"
TEMPLE_OF_IKOV_DARKAN_SOURCE = f"{TEMPLE_OF_IKOV_SOURCE_ROOT}/TempleOfIkov.java"
TEMPLE_OF_IKOV_DUNGEON_SOURCE = f"{TEMPLE_OF_IKOV_SOURCE_ROOT}/IkovDungeon.java"
TEMPLE_OF_IKOV_FIRE_WARRIOR_SOURCE = f"{TEMPLE_OF_IKOV_SOURCE_ROOT}/FireWarrior.java"
TEMPLE_OF_IKOV_LUCIEN_MOB_SOURCE = f"{TEMPLE_OF_IKOV_SOURCE_ROOT}/LucienVarrockMob.java"
TEMPLE_OF_IKOV_LUCIEN_ARDOUGNE_SOURCE = (
    f"{TEMPLE_OF_IKOV_SOURCE_ROOT}/dialogues/LucienArdougneTempleOfIkov.java"
)
TEMPLE_OF_IKOV_LUCIEN_VARROCK_SOURCE = (
    f"{TEMPLE_OF_IKOV_SOURCE_ROOT}/dialogues/LucienVarrockTempleOfIkov.java"
)
TEMPLE_OF_IKOV_GUARDIAN_SOURCE = f"{TEMPLE_OF_IKOV_SOURCE_ROOT}/dialogues/GaurdianArmadylTempleOfIkov.java"
TEMPLE_OF_IKOV_WINELDA_SOURCE = f"{TEMPLE_OF_IKOV_SOURCE_ROOT}/dialogues/WineldaWitchTempleOfIkov.java"
TEMPLE_OF_IKOV_FIRE_WARRIOR_NPC_SOURCE = (
    f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/fire_warrior_of_lesarkus.json"
)
TEMPLE_OF_IKOV_GUARDIAN_NPC_SOURCE = (
    f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/guardian_of_armadyl/guardian_of_armadyl_(45).json"
)
TEMPLE_OF_IKOV_LUCIEN_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/lucien/lucien_(14) (noanims).json"
TEMPLE_OF_IKOV_2011SCAPE_SPAWN_SOURCE = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/spawns/spawns_10650.plugin.kts"
)
HOLY_GRAIL_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/holygrail"
HOLY_GRAIL_DARKAN_SOURCE = f"{HOLY_GRAIL_SOURCE_ROOT}/HolyGrail.java"
HOLY_GRAIL_TITAN_SOURCE = f"{HOLY_GRAIL_SOURCE_ROOT}/BlackKnightTitan.java"
HOLY_GRAIL_KING_ARTHUR_SOURCE = f"{HOLY_GRAIL_SOURCE_ROOT}/dialogue/KingArthurHolyGrailD.java"
HOLY_GRAIL_MERLIN_SOURCE = f"{HOLY_GRAIL_SOURCE_ROOT}/dialogue/MerlinHolyGrailD.java"
HOLY_GRAIL_ENTRANA_SOURCE = f"{HOLY_GRAIL_SOURCE_ROOT}/dialogue/EntranaHighPriestHolyGrailD.java"
HOLY_GRAIL_GALAHAD_SOURCE = f"{HOLY_GRAIL_SOURCE_ROOT}/dialogue/SirGalahadHolyGrailD.java"
HOLY_GRAIL_FISHER_KING_SOURCE = f"{HOLY_GRAIL_SOURCE_ROOT}/dialogue/TheFisherKingHolyGrailD.java"
HOLY_GRAIL_PERCIVAL_SOURCE = f"{HOLY_GRAIL_SOURCE_ROOT}/dialogue/SirPercivalHolyGrailD.java"
HOLY_GRAIL_TITAN_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/black_knight_titan.json"
KINGS_RANSOM_DARKAN_SOURCE = (
    f"{DARKAN_QUEST_SOURCE_ROOT}/kingsransom/KingsRansom.kt "
    "(commit 38d66e0b794c1bf963866827bf8a43d899c12711; stages 55-60)"
)
KINGS_RANSOM_REV_727_ITEM_SOURCE = (
    "/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/"
    "extracted/727-2012-07-24/cache item 4428"
)
KINGS_RANSOM_2011SCAPE_ITEM_SOURCE = f"{SCAPE_2011_ITEM_IDENTITY_SOURCE} item 4428"
KINGS_RANSOM_REV_742_ITEM_SOURCE = (
    "/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/"
    "extracted/742-2012-11-07/cache item 4428"
)
KINGS_RANSOM_WIKI_SOURCE = (
    "https://runescape.wiki/w/King%27s_Ransom?oldid=6548731 "
    "(2012-11-12T01:02:00Z, Freeing King Arthur)"
)
KINGS_RANSOM_SCROLL_SOURCE = "; ".join(
    (
        KINGS_RANSOM_DARKAN_SOURCE,
        KINGS_RANSOM_REV_727_ITEM_SOURCE,
        KINGS_RANSOM_2011SCAPE_ITEM_SOURCE,
        KINGS_RANSOM_REV_742_ITEM_SOURCE,
        KINGS_RANSOM_WIKI_SOURCE,
    )
)
TREE_GNOME_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/treegnomevillage"
TREE_GNOME_DARKAN_SOURCE = f"{TREE_GNOME_SOURCE_ROOT}/TreeGnomeVillage.java"
TREE_GNOME_BOLREN_SOURCE = f"{TREE_GNOME_SOURCE_ROOT}/dialogues/KingBolrenTreeGnomeVillageD.java"
TREE_GNOME_MONTAI_SOURCE = f"{TREE_GNOME_SOURCE_ROOT}/dialogues/CommanderMontaiTreeGnomeVillageD.java"
TREE_GNOME_TRACKER1_SOURCE = f"{TREE_GNOME_SOURCE_ROOT}/dialogues/Tracker1TreeGnomeVillageD.java"
TREE_GNOME_TRACKER2_SOURCE = f"{TREE_GNOME_SOURCE_ROOT}/dialogues/Tracker2TreeGnomeVillageD.java"
TREE_GNOME_TRACKER3_SOURCE = f"{TREE_GNOME_SOURCE_ROOT}/dialogues/Tracker3TreeGnomeVillageD.java"
TREE_GNOME_KHAZARD_COMMANDER_NPC_SOURCE = (
    f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/khazard_commander (noanims).json"
)
TREE_GNOME_KHAZARD_WARLORD_NPC_SOURCE = (
    f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/khazard_warlord (noanims).json"
)
TAI_BWO_WANNAI_TRIO_JOGRE_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/jogre/jogre_(53).json"
SWAN_SONG_SEA_TROLL_QUEEN_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/sea_troll_queen (noanims).json"
PRIEST_IN_PERIL_MONK_OF_ZAMORAK_NPC_SOURCE = (
    f"{DARKAN_NPC_COMBATDEF_ROOT}/areas/paterdomus/monk_of_zamorak/monk_of_zamorak_(30).json"
)
PRIEST_IN_PERIL_CERBERUS_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/areas/paterdomus/cerberus (noanims).json"
TROLL_STRONGHOLD_DAD_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/areas/death_plateau/dad.json"
SPIRITS_BLACK_GOLEM_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/black_golem (noanims).json"
SPIRITS_WHITE_GOLEM_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/white_golem (noanims).json"
SPIRITS_GREY_GOLEM_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/grey_golem (noanims).json"
A_SOULS_BANE_FEAR_REAPER_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/fear_reaper/fear_reaper_(42) (noanims).json"
A_SOULS_BANE_CONFUSION_BEAST_NPC_SOURCE = (
    f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/confusion_beast/confusion_beast_(43) (noanims).json"
)
A_SOULS_BANE_HOPELESS_CREATURE_NPC_SOURCE = (
    f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/hopeless_creature/hopeless_creature_(40) (noanims).json"
)
A_SOULS_BANE_TOLNA_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/tolna (noanims).json"
DEATH_TO_DORGESHUUN_HAM_GUARD_NPC_SOURCE = (
    f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/h.a.m._guard/h.a.m._guard_(22) (noanims).json"
)
ANOTHER_SLICE_HAM_ARCHER_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/h.a.m._archer (noanims).json"
WITCHS_HOUSE_WIKI_SOURCE = "https://runescape.wiki/w/Witch's_House?oldid=6474931"
WITCHS_HOUSE_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/witchshouse"
WITCHS_HOUSE_SOURCE = f"{WITCHS_HOUSE_SOURCE_ROOT}/WitchsHouse.java"
WITCHS_HOUSE_BOY_SOURCE = f"{WITCHS_HOUSE_SOURCE_ROOT}/BoyWitchsHouseD.java"
WITCHS_HOUSE_DIARY_SOURCE = f"{WITCHS_HOUSE_SOURCE_ROOT}/WitchsDiary.java"
WITCHS_HOUSE_WITCH_SENTRY_SOURCE = f"{WITCHS_HOUSE_SOURCE_ROOT}/WitchSentry.java"
WITCHS_HOUSE_EXPERIMENT_NPC_SOURCE_ROOT = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/witch's_experiment"
WITCHS_HOUSE_EXPERIMENT_19_NPC_SOURCE = (
    f"{WITCHS_HOUSE_EXPERIMENT_NPC_SOURCE_ROOT}/witch's_experiment_(19) (noanims).json"
)
WITCHS_HOUSE_EXPERIMENT_30_NPC_SOURCE = (
    f"{WITCHS_HOUSE_EXPERIMENT_NPC_SOURCE_ROOT}/witch's_experiment_(30) (noanims).json"
)
WITCHS_HOUSE_EXPERIMENT_42_NPC_SOURCE = (
    f"{WITCHS_HOUSE_EXPERIMENT_NPC_SOURCE_ROOT}/witch's_experiment_(42) (noanims).json"
)
WITCHS_HOUSE_EXPERIMENT_53_NPC_SOURCE = (
    f"{WITCHS_HOUSE_EXPERIMENT_NPC_SOURCE_ROOT}/witch's_experiment_(53) (noanims).json"
)
MERLINS_CRYSTAL_WIKI_SOURCE = "https://runescape.wiki/w/Merlin's_Crystal?oldid=6569685"
MERLINS_CRYSTAL_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/merlinscrystal"
MERLINS_CRYSTAL_SOURCE = f"{MERLINS_CRYSTAL_SOURCE_ROOT}/MerlinsCrystal.java"
MERLINS_CRYSTAL_KING_ARTHUR_SOURCE = f"{MERLINS_CRYSTAL_SOURCE_ROOT}/KingArthurMerlinsCrystalD.java"
MERLINS_CRYSTAL_LADY_SOURCE = f"{MERLINS_CRYSTAL_SOURCE_ROOT}/LadyOfLakeMerlinsCrystalD.java"
MERLINS_CRYSTAL_BEGGAR_SOURCE = f"{MERLINS_CRYSTAL_SOURCE_ROOT}/BeggarMerlinsCrystalD.java"
MERLINS_CRYSTAL_MORGAN_SOURCE = f"{MERLINS_CRYSTAL_SOURCE_ROOT}/MorganMerlinsCrystalD.java"
MERLINS_CRYSTAL_MORDRED_SOURCE = f"{MERLINS_CRYSTAL_SOURCE_ROOT}/MordredMob.java"
MERLINS_CRYSTAL_KEEP_SOURCE = f"{MERLINS_CRYSTAL_SOURCE_ROOT}/KeepLaFayeMerlinsCrystalLoc.java"
MERLINS_CRYSTAL_CRATE_SCENE_SOURCE = f"{MERLINS_CRYSTAL_SOURCE_ROOT}/MerlinsCrystalCrateScene.java"
MERLINS_CRYSTAL_RITUAL_SCENE_SOURCE = f"{MERLINS_CRYSTAL_SOURCE_ROOT}/MerlinsCrystalRitualScene.java"
MERLINS_CRYSTAL_THRANTAX_SOURCE = f"{MERLINS_CRYSTAL_SOURCE_ROOT}/ThrantaxMerlinsCrystalD.java"
MERLINS_CRYSTAL_ROUND_TABLE_SOURCE_ROOT = f"{MERLINS_CRYSTAL_SOURCE_ROOT}/knightsroundtable"
MERLINS_CRYSTAL_SIR_LANCELOT_SOURCE = f"{MERLINS_CRYSTAL_ROUND_TABLE_SOURCE_ROOT}/SirLancelotMerlinsCrystalD.java"
MERLINS_CRYSTAL_SIR_LUCAN_SOURCE = f"{MERLINS_CRYSTAL_ROUND_TABLE_SOURCE_ROOT}/SirLucanMerlinsCrystalD.java"
MERLINS_CRYSTAL_SIR_GAWAIN_SOURCE = f"{MERLINS_CRYSTAL_ROUND_TABLE_SOURCE_ROOT}/SirGawainMerlinsCrystalD.java"
MERLINS_CRYSTAL_MORDRED_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/sir_mordred (noanims).json"
MERLINS_CRYSTAL_THRANTAX_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/thrantax_the_mighty (noanims).json"
MERLINS_CRYSTAL_BEEHIVE_SOURCE = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/"
    "com/rs/game/content/world/areas/seers_village/SeersVillage.java"
)
MERLINS_CRYSTAL_BEEKEEPER_SOURCE = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/"
    "com/rs/game/content/world/areas/catherby/npcs/Beekeeper.java"
)
MERLINS_CRYSTAL_2011SCAPE_CATHERBY_SPAWN_SOURCE = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/spawns/spawns_11061.plugin.kts"
)
RESTLESS_GHOST_WIKI_SOURCE = "https://runescape.wiki/w/The_Restless_Ghost?oldid=6355778"
DEMON_SLAYER_WIKI_SOURCE = "https://runescape.wiki/w/Demon_Slayer_(historical)?oldid=6448395"
DRAGON_SLAYER_WIKI_SOURCE = "https://runescape.wiki/w/Dragon_Slayer?oldid=6461164"
FIGHT_ARENA_WIKI_SOURCE = "https://runescape.wiki/w/Fight_Arena?oldid=6516173"
A_SOULS_BANE_WIKI_SOURCE = "https://runescape.wiki/w/A_Soul's_Bane?oldid=6514080"
A_SOULS_BANE_DARKAN_QUICK_GUIDE_SOURCE = "https://wiki.darkan.org/A_Soul%27s_Bane/Quick_guide?oldid=120252"
DEATH_TO_DORGESHUUN_WIKI_SOURCE = "https://runescape.wiki/w/Death_to_the_Dorgeshuun?oldid=6564288"
HEROES_QUEST_WIKI_SOURCE = "https://runescape.wiki/w/Heroes'_Quest?oldid=6534275"
FAMILY_CREST_WIKI_SOURCE = "https://runescape.wiki/w/Family_Crest?oldid=6548361"
TEMPLE_OF_IKOV_WIKI_SOURCE = "https://runescape.wiki/w/Temple_of_Ikov?oldid=6538747"
HOLY_GRAIL_WIKI_SOURCE = "https://runescape.wiki/w/Holy_Grail?oldid=6393193"
TREE_GNOME_WIKI_SOURCE = "https://runescape.wiki/w/Tree_Gnome_Village?oldid=6541699"
SPIRITS_OF_THE_ELID_WIKI_SOURCE = "https://runescape.wiki/w/Spirits_of_the_Elid?oldid=6326193"
ANOTHER_SLICE_OF_H_A_M_WIKI_SOURCE = "https://runescape.wiki/w/Another_Slice_of_H.A.M.?oldid=6548739"
JUNGLE_POTION_WIKI_SOURCE = "https://runescape.wiki/w/Jungle_Potion?oldid=6555418"
KENNITHS_CONCERNS_WIKI_SOURCE = "https://runescape.wiki/w/Kennith%27s_Concerns?oldid=6549837"
DEADLIEST_CATCH_WIKI_SOURCE = "https://runescape.wiki/w/Deadliest_Catch?oldid=6295312"
WOLF_WHISTLE_WIKI_SOURCE = "https://runescape.wiki/w/Wolf_Whistle?oldid=6327531"
SONG_FROM_THE_DEPTHS_WIKI_SOURCE = "https://runescape.wiki/w/Song_from_the_Depths?oldid=6467675"
CARNILLEAN_RISING_WIKI_SOURCE = "https://runescape.wiki/w/Carnillean_Rising?oldid=6534490"
SOME_LIKE_IT_COLD_WIKI_SOURCE = "https://runescape.wiki/w/Some_Like_It_Cold?oldid=6545099"
SOME_LIKE_IT_COLD_CACHE_SOURCE = (
    "/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/"
    "extracted/742-2012-11-07/cache"
)
SWAN_SONG_WIKI_SOURCE = "https://runescape.wiki/w/Swan_Song?oldid=6548264"
SHILO_VILLAGE_WIKI_SOURCE = "https://runescape.wiki/w/Shilo_Village?oldid=6389566"
SHILO_VILLAGE_SOURCE_ROOT = f"{DARKAN_QUEST_SOURCE_ROOT}/shilo_village"
SHILO_VILLAGE_DARKAN_SOURCE = f"{SHILO_VILLAGE_SOURCE_ROOT}/ShiloVillage.kt"
SHILO_VILLAGE_MOSOL_SOURCE = f"{SHILO_VILLAGE_SOURCE_ROOT}/MosulDialog.kt"
SHILO_VILLAGE_TRUFITUS_SOURCE = f"{DARKAN_QUEST_SOURCE_ROOT}/TrufitusDialog.kt"
SHILO_VILLAGE_CACHE_SOURCE = (
    "/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/"
    "extracted/742-2012-11-07/cache"
)
LEGENDS_QUEST_WIKI_SOURCE = "https://runescape.wiki/w/Legends'_Quest?oldid=6529921"
THE_FEUD_WIKI_SOURCE = "https://runescape.wiki/w/The_Feud?oldid=6542289"
RFD_FREEING_SIR_AMIK_VARZE_WIKI_SOURCE = (
    "https://runescape.wiki/w/Recipe_for_Disaster%3A_Freeing_Sir_Amik_Varze?oldid=6237763"
)
DARKAN_NAZASTAROOL_91_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/nazastarool/nazastarool_(91).json"
DARKAN_NAZASTAROOL_68_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/nazastarool/nazastarool_(68).json"
DARKAN_NAZASTAROOL_93_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/nazastarool/nazastarool_(93).json"
LEGENDS_QUEST_NEZIKCHENED_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/nezikchened (noanims).json"
THE_FEUD_TOUGH_GUY_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/tough_guy (noanims).json"
RFD_BLACK_DRAGON_NPC_SOURCE = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/npcs/definitions/dragons/black_dragon_level_227.plugin.kts"
)
RUNE_MYSTERIES_RELEASE_SOURCE = "https://runescape.salmoneus.net/runescape-2007/quests/rune-mysteries.html"
RUNE_MYSTERIES_DUKE_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/lumbridge/duke_horacio.plugin.kts"
)
DARKAN_LUMBRIDGE_DUKE_SOURCE = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/"
    "com/rs/game/content/world/areas/lumbridge/Lumbridge.java"
)
DRAGON_SLAYER_2011SCAPE_MAZE_SPAWNS_SOURCE = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/spawns/spawns_11670.plugin.kts"
)
DRAGON_SLAYER_2011SCAPE_GHOST_NPC_SOURCE = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/npcs/definitions/undeads/ghost_level_19.plugin.kts"
)
DRAGON_SLAYER_2011SCAPE_SKELETON_NPC_SOURCE = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/npcs/definitions/undeads/skeleton_lvl_22.plugin.kts"
)
DRAGON_SLAYER_2011SCAPE_ZOMBIE_NPC_SOURCE = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/npcs/definitions/undeads/zombie_lvl_24.plugin.kts"
)
DRAGON_SLAYER_2011SCAPE_LESSER_DEMON_NPC_SOURCE = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/npcs/definitions/demons/lesser_demon_lvl_82.plugin.kts"
)
RUNE_MYSTERIES_SEDRIDOR_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/draynor/sedridor.plugin.kts"
)
RUNE_MYSTERIES_AUBURY_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/varrock/aubury.plugin.kts"
)
RUNECRAFTING_BASICS_SOURCE = "https://www.2011.rs/kb/runecrafting_the_basics"
RUNECRAFTING_ALTARS_SOURCE = "https://www.2011.rs/kb/runecrafting_locating_the_altars"
RUNE_ESSENCE_MINE_SOURCE = "https://www.2011.rs/kb/mining_the_rune_essence_mine"
RAW_MONKFISH_SOURCE = "https://runescape.fandom.com/wiki/Raw_monkfish"
RAW_KARAMBWAN_SOURCE = "https://runescape.fandom.com/wiki/Raw_karambwan"
GEM_ROCK_SOURCE = "https://runescape.wiki/w/Gem_rock?oldid=37044944"
PRIEST_IN_PERIL_ID = "priest_in_peril"
PRIEST_IN_PERIL_SOURCE = "https://runescape.wiki/w/Priest_in_Peril?oldid=6487728"
PRIEST_IN_PERIL_QUEST_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/quests/impl/PriestInPeril.kt"
)
PRIEST_IN_PERIL_DARKAN_SOURCE = f"{DARKAN_QUEST_SOURCE_ROOT}/priestinperil/PriestInPeril.java"
PRIEST_IN_PERIL_DARKAN_CERBERUS_SOURCE = f"{DARKAN_QUEST_SOURCE_ROOT}/priestinperil/Cerberus.java"
PRIEST_IN_PERIL_DARKAN_DREZEL_JAIL_SOURCE = f"{DARKAN_QUEST_SOURCE_ROOT}/priestinperil/DrezelInJailD.java"
PRIEST_IN_PERIL_DARKAN_DREZEL_MAUSOLEUM_SOURCE = f"{DARKAN_QUEST_SOURCE_ROOT}/priestinperil/DrezelMausoleumD.java"
TROLL_STRONGHOLD_ID = "troll_stronghold"
THE_FREMENNIK_ISLES_ID = "the_fremennik_isles"
THE_FREMENNIK_ISLES_SOURCE = "https://runescape.wiki/w/The_Fremennik_Isles?oldid=6540919"
BROAD_FLETCHING_ABILITY = "broad_fletching"
BARBARIAN_FISHING_ABILITY = "barbarian_fishing"
BROAD_FLETCHING_SOURCE = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/inter/slayer/slayer_rewards.plugin.kts"
)
BARBARIAN_FISHING_SOURCE = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/skills/fishing/Fishing.kt"
)
HUNTER_EAGLES_PEAK_SOURCE = "https://www.2011.rs/kb/hunter_box_trapping_level_27"
HUNTER_AS_A_FIRST_RESORT_SOURCE = "https://www.2011.rs/kb/hunter_locations"
RED_SANDSTONE_SOURCE = "https://runescape.wiki/w/Red_sandstone?oldid=6438865"
ROBUST_GLASS_SOURCE = "https://runescape.wiki/w/Robust_glass?oldid=6504157"
HUNTER_ROCKING_OUT_SOURCE = "https://www.2011.rs/kb/hunter_butterfly_netting_level_15"
KNIGHTS_SWORD_QUEST_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/quests/impl/TheKnightsSword.kt"
)
KNIGHTS_SWORD_THURGO_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/asgarnia/thurgo.plugin.kts"
)
KNIGHTS_SWORD_SQUIRE_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/falador/squire.plugin.kts"
)
COOKS_ASSISTANT_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/quests/impl/CooksAssistant.kt"
)
COOKS_ASSISTANT_LUMBRIDGE_COOK_SOURCE = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/lumbridge/lumbridge_cook.plugin.kts"
)
COOKS_ASSISTANT_PRIZED_DAIRY_COW_SOURCE = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/lumbridge/prized_dairy_cow.plugin.kts"
)
COOKS_ASSISTANT_MILLIE_MILLER_SOURCE = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/lumbridge/millie_miller.plugin.kts"
)
COOKS_ASSISTANT_FLOUR_BIN_SOURCE = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/objs/mill/flour_bin.plugin.kts"
)
IMP_CATCHER_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/quests/impl/ImpCatcher.kt"
)
IMP_CATCHER_MIZGOG_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/draynor/mizgog.plugin.kts"
)
DRUIDIC_RITUAL_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/quests/impl/DruidicRitual.kt"
)
DRUIDIC_RITUAL_SANFEW_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/taverley/sanfew.plugin.kts"
)
DRUIDIC_RITUAL_KAQEMEEX_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/taverley/kaqemeex.plugin.kts"
)
DRUIDIC_RITUAL_CAULDRON_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/objs/cauldron_of_thunder.plugin.kts"
)
PIRATES_TREASURE_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/quests/impl/PiratesTreasure.kt"
)
PIRATES_TREASURE_REDBEARD_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/portsarim/redbeard_frank.plugin.kts"
)
PIRATES_TREASURE_CHEST_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/varrock/pirate_chest.plugin.kts"
)
VAMPYRE_SLAYER_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/quests/impl/VampyreSlayer.kt"
)
VAMPYRE_SLAYER_DR_HARLOW_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/varrock/dr_harlow.plugin.kts"
)
VAMPYRE_SLAYER_MORGAN_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/draynor/morgan.plugin.kts"
)
VAMPYRE_SLAYER_MANOR_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/draynor/draynor_manor.plugin.kts"
)
COUNT_DRAYNOR_NPC_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/npcs/definitions/undeads/count_draynor_level_37.plugin.kts"
)
HUNTER_PRIEST_IN_PERIL_SOURCE = "https://www.2011.rs/kb/hunter_net_trapping_level_29"

QUEST_REWARD_ITEM_NAME_OVERRIDES = {
    "Amulet of ghostspeak": "Ghostspeak amulet",
    "Ring of charos": "Ring of Charos",
}


@dataclass(frozen=True)
class QuestStage:
    stage: int
    journal: Tuple[str, ...]


@dataclass(frozen=True)
class QuestCombatEncounter:
    encounter_id: str
    display_name: str
    level: int = 0
    quantity: int = 1
    source: str = ""
    source_text: str = ""
    npc_stats: Tuple[Tuple[str, object], ...] = ()
    npc_bonuses: Tuple[Tuple[str, object], ...] = ()
    npc_configs: Tuple[Tuple[str, object], ...] = ()
    npc_stats_source: str = ""


@dataclass(frozen=True)
class QuestStageRequirement:
    stage: int
    description: str
    variant: str = ""
    required_inventory: Tuple[Tuple[str, int], ...] = ()
    required_inventory_options: Tuple[Tuple[Tuple[str, int], ...], ...] = ()
    consumed_inventory: Tuple[Tuple[str, int], ...] = ()
    consumed_inventory_options: Tuple[Tuple[Tuple[str, int], ...], ...] = ()
    produced_inventory: Tuple[Tuple[str, int], ...] = ()
    required_tools: Tuple[Tuple[str, int], ...] = ()
    required_actions: Tuple[str, ...] = ()
    auto_actions: Tuple[str, ...] = ()
    required_routes: Tuple[str, ...] = ()
    combat_encounters: Tuple[QuestCombatEncounter, ...] = ()
    source: str = ""


@dataclass(frozen=True)
class QuestChoiceOption:
    label: str
    route_id: str
    description: str = ""


@dataclass(frozen=True)
class QuestChoice:
    stage: int
    prompt: str
    options: Tuple[QuestChoiceOption, ...]
    source: str = ""


@dataclass(frozen=True)
class QuestPrerequisite:
    quest_id: str
    display_name: str


@dataclass(frozen=True)
class QuestSkillRequirement:
    skill_id: str
    display_name: str
    level: int


@dataclass(frozen=True)
class QuestXpReward:
    skill_id: str
    amount: float


@dataclass(frozen=True)
class QuestLampReward:
    display_name: str
    amount: float
    skill_options: Tuple[str, ...]
    minimum_level: int
    source: str
    source_text: str = ""
    quantity: int = 1


@dataclass(frozen=True)
class QuestDefinition:
    id: str
    display_name: str
    stages: int
    point_reward: int
    rewards: Tuple[Tuple[str, int], ...]
    start_point: str
    requirements: Tuple[str, ...]
    required_items: Tuple[Tuple[str, int], ...]
    combat: str
    source: str
    journal_stages: Tuple[QuestStage, ...]
    release_date: str
    members: bool
    difficulty: str
    length: str
    timeline: str
    required_quests: Tuple[QuestPrerequisite, ...] = ()
    required_skills: Tuple[QuestSkillRequirement, ...] = ()
    required_quest_points: int = 0
    xp_rewards: Tuple[QuestXpReward, ...] = ()
    lamp_rewards: Tuple[QuestLampReward, ...] = ()
    unlocks: Tuple[str, ...] = ()
    release_order: int = 0
    stage_requirements: Tuple[QuestStageRequirement, ...] = ()
    start_inventory: Tuple[Tuple[str, int], ...] = ()
    choices: Tuple[QuestChoice, ...] = ()
    # Miniquests are ordinary ledger rows that award no quest points; the flag
    # only tells the Quests tab to group them separately.
    miniquest: bool = False


@dataclass(frozen=True)
class ClaimDefinition:
    id: str
    display_name: str
    source: str
    claim_type: str = "item"
    item_name: str = ""
    quantity: int = 1
    items: Tuple[Tuple[str, int], ...] = ()
    required_quest: str = RUNE_MYSTERIES_ID
    required_runecrafting_level: int = 0
    xp_amount: float = 0.0
    skill_options: Tuple[str, ...] = ()
    minimum_level: int = 1


@dataclass(frozen=True)
class QuestReference:
    id: str
    display_name: str
    source: str
    note: str


@dataclass(frozen=True)
class QuestUnlockRule:
    quest_id: str
    gate_kind: str
    skill_id: str
    target_ids: Tuple[str, ...]
    reason: str
    source: str


@dataclass(frozen=True)
class TargetUnlockRequirement:
    kind: str
    reason: str
    source: str
    quest_id: str = ""
    ability_id: str = ""


@dataclass(frozen=True)
class TargetUnlockRule:
    gate_kind: str
    skill_id: str
    target_ids: Tuple[str, ...]
    requirements: Tuple[TargetUnlockRequirement, ...]


def _clean_journal(*lines: str) -> Tuple[str, ...]:
    cleaned = []
    for line in lines:
        stripped = re.sub(r"</?col(?:=[^>]*)?>", "", line)
        stripped = stripped.replace("<str>", "").strip()
        if stripped:
            cleaned.append(stripped)
    return tuple(cleaned)


def _simple_stage(stage: int, *lines: str) -> QuestStage:
    return QuestStage(stage, _clean_journal(*lines))


RUNE_MYSTERIES_STAGES: Tuple[QuestStage, ...] = (
    QuestStage(
        1,
        _clean_journal(
            "I spoke to Duke Horacio in Lumbridge Castle. He told me",
            "that he'd found a Strange Talisman in the Castle which",
            "might be of use to the Order of Wizards at the Wizards'",
            "Tower. He asked me to take it there and give it to a wizard",
            "called Sedridor. I can find the Wizards' Tower south west of",
            "Lumbridge, across the bridge from Draynor Village.",
        ),
    ),
    QuestStage(2, _clean_journal("I travelled toward the Wizards' Tower with the strange talisman.")),
    QuestStage(
        3,
        _clean_journal(
            "I delivered the Strange Talisman to Sedridor in the",
            "basement of the Wizards' Tower. He believes it might be",
            "key to discovering a Teleportation Incantation to the lost",
            "Rune Essence Mine. He asked me to help confirm this by",
            "delivering a Package to Aubury, an expert on",
            "Runecrafting. I can find him in his Rune Shop in south east",
            "Varrock.",
        ),
    ),
    QuestStage(4, _clean_journal("I carried Sedridor's package toward Aubury's Rune Shop in Varrock.")),
    QuestStage(
        5,
        _clean_journal(
            "I delivered the Package to Aubury at his Rune Shop in",
            "south east Varrock. He confirmed Sedridor's suspicions",
            "and asked me to take some Research Notes back to him. I",
            "can find Sedridor in the basement of the Wizards' Tower.",
        ),
    ),
    QuestStage(
        6,
        _clean_journal(
            "I spoke to Duke Horacio and he showed me a strange",
            "talisman that had been found by one of his subjects.",
            "I agreed to take it to the Wizards' Tower, South West of",
            "Lumbridge for further examination by the wizards.",
            "I gave the Talisman to the Head of the Tower and",
            "agreed to help him with his research into rune stones.",
            "I took the research package to Varrock and delivered it.",
            "Aubury was interested in the research package and gave",
            "me his own research notes to deliver to Sedridor.",
            "I brought Sedridor the research notes that Aubury had",
            "compiled so that he could compare their research. They",
            "discovered that it was now possible to create new rune",
            "stones, a skill that had been thought lost forever.",
            "In return for all of my help they taught me how to do this,",
            "and will teleport me to mine blank runes anytime.",
            "Quest complete!",
        ),
    ),
)

COOKS_ASSISTANT_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "I need to collect a super large egg near Lumbridge for the Duke's cake.",
    ),
    _simple_stage(
        2,
        "I need a bucket so I can milk the prized dairy cow for top-quality milk.",
    ),
    _simple_stage(
        3,
        "I need an empty pot so Millie's mill can produce extra fine flour.",
    ),
    _simple_stage(
        4,
        "I have the special egg, milk, and flour. I should give them to the cook.",
    ),
    _simple_stage(
        5,
        "I brought the cook all three ingredients and he made the birthday cake.",
        "Quest complete!",
    ),
)

IMP_CATCHER_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "Wizard Mizgog needs his black, red, white, and yellow beads returned.",
    ),
    _simple_stage(
        2,
        "I returned Wizard Mizgog's beads and received an Amulet of accuracy.",
        "Quest complete!",
    ),
)

DRUIDIC_RITUAL_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Kaqemeex asked me to speak with Sanfew in Taverley."),
    _simple_stage(
        2,
        "Sanfew needs raw bear meat, raw rat meat, raw beef, and raw chicken dipped in the Cauldron of Thunder.",
    ),
    _simple_stage(
        3,
        "The meats have been enchanted in the Cauldron of Thunder and should be returned through Sanfew to Kaqemeex.",
    ),
    _simple_stage(
        4,
        "Kaqemeex taught me the basics of Herblore.",
        "Quest complete!",
    ),
)

JUNGLE_POTION_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Trufitus asked me to search the marshy jungle vines to the south-west for snake weed."),
    _simple_stage(2, "I found grimy snake weed. I must clean it and give the clean herb to Trufitus."),
    _simple_stage(3, "Trufitus asked me to search the palm trees on the north-east peninsula for ardrigal."),
    _simple_stage(4, "I found grimy ardrigal. I must clean it and give the clean herb to Trufitus."),
    _simple_stage(5, "Trufitus asked me to search the scorched earth south of the village for sito foil."),
    _simple_stage(6, "I found grimy sito foil. I must clean it and give the clean herb to Trufitus."),
    _simple_stage(7, "Trufitus asked me to search the rocks south-east of the village for volencia moss."),
    _simple_stage(8, "I found grimy volencia moss. I must clean it and give the clean herb to Trufitus."),
    _simple_stage(9, "Trufitus asked me to search the fungus-covered walls in the northern caves for rogue's purse."),
    _simple_stage(10, "I found grimy rogue's purse. I must clean it and give the clean herb to Trufitus."),
    _simple_stage(
        11,
        "I collected five jungle herbs for Trufitus and he rewarded me with Herblore training.",
        "Quest complete!",
    ),
)

PIRATES_TREASURE_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Redbeard Frank wants Karamja rum in exchange for the treasure location."),
    _simple_stage(2, "Redbeard Frank gave me One-Eyed Hector's chest key for the Blue Moon Inn."),
    _simple_stage(3, "The Blue Moon Inn chest contained a pirate message pointing to Falador Park."),
    _simple_stage(4, "I dug up One-Eyed Hector's treasure in Falador Park.", "Quest complete!"),
)

SHILO_VILLAGE_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "Mosol Rei gave me a Wampum belt for Trufitus.",
        "I should deliver the belt to Trufitus in Tai Bwo Wannai.",
    ),
    _simple_stage(
        2,
        "Trufitus believes the lost Temple of Ah Za Rhoon holds the key to Rashiliyia's curse.",
        "I should search the coast east of Tai Bwo Wannai with a lit light source and rope.",
    ),
    _simple_stage(
        3,
        "I entered Ah Za Rhoon.",
        "I should recover and read every clue about Rashiliyia, Bervirius, and Zadimus.",
    ),
    _simple_stage(
        4,
        "I recovered the temple's two scrolls, stone-plaque, and Zadimus corpse.",
        "Trufitus can interpret the evidence and tell me how to lay Zadimus to rest.",
    ),
    _simple_stage(
        5,
        "Zadimus's burial left me a bone shard and pointed toward Bervirius's tomb.",
        "I should search the Cairn Isle dolmen for clues about Rashiliyia.",
    ),
    _simple_stage(
        6,
        "Bervirius's tomb held a sword pommel, locating crystal, and his notes.",
        "I should read the notes and show the evidence to Trufitus.",
    ),
    _simple_stage(
        7,
        "The clues explain how to find Rashiliyia's tomb and protect myself inside.",
        "I must carve Zadimus's Bone key and chisel the Sword pommel into Bone beads.",
    ),
    _simple_stage(
        8,
        "I carved the Bone key and Bone beads.",
        "Bronze wire will turn the beads into the protective Beads of the dead.",
    ),
    _simple_stage(
        9,
        "I have the Bone key and Beads of the dead.",
        "The locating crystal can lead me to Rashiliyia's tomb, where three regular bones open the inner door.",
    ),
    _simple_stage(
        10,
        "I entered Rashiliyia's tomb.",
        "Nazastarool will return as a zombie, skeleton, and ghost before yielding Rashiliyia's corpse.",
    ),
    _simple_stage(
        11,
        "I defeated all three forms of Nazastarool and recovered Rashiliyia's corpse.",
        "I should show it to Trufitus, then place it on Bervirius's dolmen.",
    ),
    _simple_stage(12, "Rashiliyia's spirit is finally at rest and Shilo Village is open.", "Quest complete!"),
)

VAMPYRE_SLAYER_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Morgan asked me to find Dr Harlow at the Blue Moon Inn in Varrock."),
    _simple_stage(2, "Dr Harlow agreed to help, but he wants a beer first."),
    _simple_stage(3, "Dr Harlow gave me a stake and stake hammer for Count Draynor."),
    _simple_stage(4, "Count Draynor is dead. I should tell Morgan that Draynor is safe."),
    _simple_stage(5, "Morgan rewarded me for slaying Count Draynor.", "Quest complete!"),
)

RESTLESS_GHOST_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Father Aereck asked me to speak to Father Urhney in Lumbridge Swamp."),
    _simple_stage(2, "Father Urhney gave me a ghostspeak amulet so I can talk to the ghost."),
    _simple_stage(3, "The ghost told me his skull was stolen near the mine south of Lumbridge graveyard."),
    _simple_stage(4, "I found the muddy skull and a skeleton warlock appeared."),
    _simple_stage(5, "I returned the skull to the ghost's coffin.", "Quest complete!"),
)

LOST_CITY_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "The adventurers in Lumbridge Swamp are searching for Zanaris.", "I should find out what they know."),
    _simple_stage(2, "I found Shamus hiding in a swamp tree.", "He says Zanaris is reached through the shed while carrying a dramen staff."),
    _simple_stage(3, "I travelled to Entrana to find the dramen tree.", "The tree is protected by a dangerous spirit."),
    _simple_stage(4, "I defeated the tree spirit and cut a dramen branch."),
    _simple_stage(5, "I crafted a dramen staff from the branch.", "The shed in Lumbridge Swamp should now open the way."),
    _simple_stage(6, "I entered Zanaris through the swamp shed.", "Quest complete!"),
)

DEMON_SLAYER_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "Gypsy Aris saw Delrith returning and said I must follow Wally's path.",
        "She says Sir Prysin in Varrock Palace knows where Silverlight is.",
    ),
    _simple_stage(
        2,
        "Sir Prysin says Silverlight is locked in a special box.",
        "I need three Silverlight keys before he can give me the sword.",
    ),
    _simple_stage(
        3,
        "Sir Prysin's key is stuck in the drain north-east of Varrock Castle.",
        "A bucket of water should wash it into the sewers where I can retrieve it.",
    ),
    _simple_stage(
        4,
        "Wizard Traiborn has another key.",
        "He needs twenty-five regular bones for a ritual to retrieve it.",
    ),
    _simple_stage(
        5,
        "Captain Rovin has the third key at the top of Varrock Palace's north-west tower.",
    ),
    _simple_stage(
        6,
        "I have the three Silverlight keys.",
        "Sir Prysin can now open the box and give me Silverlight.",
    ),
    _simple_stage(
        7,
        "I have Silverlight.",
        "Delrith is at the Dark Wizards' altar south of Varrock, and ordinary weapons will not hurt him.",
    ),
    _simple_stage(
        8,
        "Delrith has been weakened with Silverlight.",
        "I must recite the incantation to banish him: Aber, Gabindo, Purchai, Camerinthum, Carlem.",
    ),
    _simple_stage(
        9,
        "Quest complete!",
    ),
)

SHIELD_ROUTE_PHOENIX = "Join the Phoenix Gang"
SHIELD_ROUTE_BLACK_ARM = "Join the Black Arm Gang"
SHIELD_VARIANT_PHOENIX = "phoenix"
SHIELD_VARIANT_BLACK_ARM = "black_arm"
HEROES_ROUTE_PHOENIX = SHIELD_ROUTE_PHOENIX
HEROES_ROUTE_BLACK_ARM = SHIELD_ROUTE_BLACK_ARM
HEROES_VARIANT_PHOENIX = SHIELD_VARIANT_PHOENIX
HEROES_VARIANT_BLACK_ARM = SHIELD_VARIANT_BLACK_ARM
TEMPLE_OF_IKOV_ROUTE_GUARDIANS = "Side with the Guardians of Armadyl"
TEMPLE_OF_IKOV_ROUTE_LUCIEN = "Side with Lucien"
TEMPLE_OF_IKOV_VARIANT_GUARDIANS = "guardians"
TEMPLE_OF_IKOV_VARIANT_LUCIEN = "lucien"
HAZEEL_CULT_ROUTE_CARNILLEAN = "Side with Ceril Carnillean"
HAZEEL_CULT_ROUTE_HAZEEL = "Side with Hazeel's cult"
VOID_STARES_BACK_ROUTE_KORASI = "Sacrifice Korasi"
VOID_STARES_BACK_ROUTE_JESSIKA = "Sacrifice Jessika"
TEMPLE_OF_IKOV_BOW_OPTIONS: Tuple[Tuple[str, int], ...] = (
    ("Yew shortbow", 1),
    ("Yew longbow", 1),
    ("Yew comp bow", 1),
    ("Magic shortbow", 1),
    ("Magic longbow", 1),
    ("Magic comp bow", 1),
    ("Dark bow", 1),
)

SHIELD_OF_ARRAV_CHOICES: Tuple[QuestChoice, ...] = (
    QuestChoice(
        stage=4,
        prompt="Choose a gang.",
        options=(
            QuestChoiceOption("Phoenix Gang", SHIELD_ROUTE_PHOENIX, "Jonny the beard and the Phoenix shield half."),
            QuestChoiceOption("Black Arm Gang", SHIELD_ROUTE_BLACK_ARM, "Phoenix crossbows and the Black Arm shield half."),
        ),
        source=f"{DARKAN_SHIELD_OF_ARRAV_STRAVEN_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_KATRINE_SOURCE}; {SHIELD_OF_ARRAV_WIKI_SOURCE}",
    ),
)

HEROES_QUEST_CHOICES: Tuple[QuestChoice, ...] = (
    QuestChoice(
        stage=9,
        prompt="Choose the gang contact to use for Scarface Pete's mansion.",
        options=(
            QuestChoiceOption(
                "Phoenix Gang",
                HEROES_ROUTE_PHOENIX,
                "Use the secret panel and a Black Arm Gang partner's miscellaneous key to confront Grip.",
            ),
            QuestChoiceOption("Black Arm Gang", HEROES_ROUTE_BLACK_ARM, "Use Trobert's deputy guard route."),
        ),
        source=f"{HEROES_QUEST_KATRINE_SOURCE}; {HEROES_QUEST_STRAVEN_SOURCE}; {HEROES_QUEST_WIKI_SOURCE}",
    ),
)

TEMPLE_OF_IKOV_CHOICES: Tuple[QuestChoice, ...] = (
    QuestChoice(
        stage=9,
        prompt="Choose who to aid.",
        options=(
            QuestChoiceOption("Guardians of Armadyl", TEMPLE_OF_IKOV_ROUTE_GUARDIANS, "Receive an Armadyl pendant and confront Lucien."),
            QuestChoiceOption("Lucien", TEMPLE_OF_IKOV_ROUTE_LUCIEN, "Take the Staff of Armadyl for Lucien."),
        ),
        source=f"{TEMPLE_OF_IKOV_GUARDIAN_SOURCE}; {TEMPLE_OF_IKOV_LUCIEN_VARROCK_SOURCE}; {TEMPLE_OF_IKOV_WIKI_SOURCE}",
    ),
)

HAZEEL_CULT_CHOICES: Tuple[QuestChoice, ...] = (
    QuestChoice(
        stage=1,
        prompt="Choose who to help.",
        options=(
            QuestChoiceOption("Ceril Carnillean", HAZEEL_CULT_ROUTE_CARNILLEAN, "Stop the cult and expose Butler Jones."),
            QuestChoiceOption("Hazeel's cult", HAZEEL_CULT_ROUTE_HAZEEL, "Help revive Hazeel."),
        ),
        source="https://runescape.wiki/w/Hazeel_Cult?oldid=6579784",
    ),
)

VOID_STARES_BACK_CHOICES: Tuple[QuestChoice, ...] = (
    QuestChoice(
        stage=5,
        prompt="Choose who makes the sacrifice.",
        options=(
            QuestChoiceOption("Korasi", VOID_STARES_BACK_ROUTE_KORASI, "Korasi sacrifices herself before the Pest Queen fight."),
            QuestChoiceOption("Jessika", VOID_STARES_BACK_ROUTE_JESSIKA, "Jessika sacrifices herself before the Pest Queen fight."),
        ),
        source="https://runescape.wiki/w/The_Void_Stares_Back%2FQuick_guide?oldid=6549181",
    ),
)

QUEST_CHOICE_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestChoice, ...]] = {
    HAZEEL_CULT_ID: HAZEEL_CULT_CHOICES,
    THE_VOID_STARES_BACK_ID: VOID_STARES_BACK_CHOICES,
}

SHIELD_OF_ARRAV_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "Reldo says the Shield of Arrav book in the Varrock palace library explains where to begin.",
    ),
    _simple_stage(
        2,
        "I read about the Shield of Arrav and should ask Reldo where the Phoenix Gang is hiding.",
    ),
    _simple_stage(
        3,
        "Reldo sent me to Baraek at Varrock market for information about the Phoenix Gang.",
    ),
    _simple_stage(
        4,
        "Baraek revealed the Phoenix hideout after I bribed him.",
        "I must choose whether to join the Phoenix Gang or the Black Arm Gang.",
    ),
    _simple_stage(
        5,
        "My chosen gang needs proof of loyalty.",
        "The Phoenix route needs Jonny the beard's intelligence report; the Black Arm route needs two Phoenix crossbows.",
    ),
    _simple_stage(
        6,
        "I have the proof item for my chosen gang and should hand it in.",
    ),
    _simple_stage(
        7,
        "I joined a gang and can retrieve that gang's half of the shield.",
    ),
    _simple_stage(
        8,
        "I found a shield half and should show it to King Roald.",
    ),
    _simple_stage(
        9,
        "King Roald sent me to Curator Haig Halen to authenticate the shield half.",
    ),
    _simple_stage(
        10,
        "The curator made duplicate half certificates.",
        "My route contact can trade a duplicate half certificate so I can make the full certificate.",
    ),
    _simple_stage(
        11,
        "I have the full certificate and should give it to King Roald.",
    ),
    _simple_stage(12, "King Roald accepted the certificate and paid the reward.", "Quest complete!"),
)

SHIELD_OF_ARRAV_STAGE_REQUIREMENTS: Tuple[QuestStageRequirement, ...] = (
    QuestStageRequirement(
        stage=1,
        description="Find and read the Shield of Arrav book in Reldo's library.",
        auto_actions=("Find and read the Shield of Arrav book",),
        produced_inventory=(("Shield of Arrav book", 1),),
        source=f"{DARKAN_SHIELD_OF_ARRAV_BOOK_SOURCE}; {SCAPE_2011_VARROCK_RELDO_SOURCE}; {SHIELD_OF_ARRAV_WIKI_SOURCE}",
    ),
    QuestStageRequirement(
        stage=2,
        description="Ask Reldo where to find the Phoenix Gang.",
        auto_actions=("Ask Reldo about the Phoenix Gang",),
        source=f"{DARKAN_SHIELD_OF_ARRAV_RELDO_SOURCE}; {SCAPE_2011_VARROCK_RELDO_SOURCE}; {SHIELD_OF_ARRAV_WIKI_SOURCE}",
    ),
    QuestStageRequirement(
        stage=3,
        description="Bribe Baraek for the Phoenix hideout location.",
        consumed_inventory=(("Coins", 20),),
        auto_actions=("Bribe Baraek for the Phoenix hideout",),
        source=f"{DARKAN_SHIELD_OF_ARRAV_BARAEK_SOURCE}; {SHIELD_OF_ARRAV_WIKI_SOURCE}",
    ),
    QuestStageRequirement(
        stage=4,
        description="Choose the Phoenix Gang route with Straven.",
        variant=SHIELD_VARIANT_PHOENIX,
        required_routes=(SHIELD_ROUTE_PHOENIX,),
        auto_actions=("Ask Straven for the Phoenix loyalty task",),
        source=f"{DARKAN_SHIELD_OF_ARRAV_STRAVEN_SOURCE}; {SHIELD_OF_ARRAV_WIKI_SOURCE}",
    ),
    QuestStageRequirement(
        stage=4,
        description="Choose the Black Arm Gang route with Charlie and Katrine.",
        variant=SHIELD_VARIANT_BLACK_ARM,
        required_routes=(SHIELD_ROUTE_BLACK_ARM,),
        auto_actions=("Ask Charlie and Katrine for the Black Arm loyalty task",),
        source=(
            f"{DARKAN_SHIELD_OF_ARRAV_CHARLIE_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_KATRINE_SOURCE}; "
            f"{SHIELD_OF_ARRAV_WIKI_SOURCE}"
        ),
    ),
    QuestStageRequirement(
        stage=5,
        description="Kill Jonny the beard and take his intelligence report.",
        variant=SHIELD_VARIANT_PHOENIX,
        required_routes=(SHIELD_ROUTE_PHOENIX,),
        combat_encounters=(
            QuestCombatEncounter(
                encounter_id=f"{SHIELD_OF_ARRAV_ID}_jonny_the_beard_2",
                display_name="Jonny the beard",
                level=2,
                source=f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_JONNY_DROPS_SOURCE}; {SHIELD_OF_ARRAV_WIKI_SOURCE}",
                source_text="Jonny the beard drops the intelligence report needed to prove Phoenix Gang loyalty.",
                npc_stats=(
                    ("hitpoints", 80),
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
                    ("attack_bonus", "crush_att"),
                    ("aggressiveness_type", "passive"),
                ),
                npc_stats_source=DARKAN_SHIELD_OF_ARRAV_JONNY_NPC_SOURCE,
            ),
        ),
        produced_inventory=(("Intel report", 1),),
        source=f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_JONNY_DROPS_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_JONNY_NPC_SOURCE}",
    ),
    QuestStageRequirement(
        stage=5,
        description="Your Phoenix contact gets you into the weapon store; defeat the Weaponsmaster and steal two Phoenix crossbows.",
        variant=SHIELD_VARIANT_BLACK_ARM,
        required_routes=(SHIELD_ROUTE_BLACK_ARM,),
        combat_encounters=(
            QuestCombatEncounter(
                encounter_id=f"{SHIELD_OF_ARRAV_ID}_weaponsmaster_23",
                display_name="Weaponsmaster",
                level=23,
                source=f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_WEAPONSMASTER_NPC_SOURCE}; {SHIELD_OF_ARRAV_WIKI_SOURCE}",
                source_text="The weapon store is guarded by the Weaponsmaster before the Black Arm proof crossbows can be taken.",
                npc_stats=(
                    ("hitpoints", 200),
                    ("attack", 21),
                    ("strength", 21),
                    ("defence", 21),
                    ("magic", 1),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 50),
                    ("attack_range", -1),
                    ("attack_style", "melee"),
                    ("attack_bonus", "crush_att"),
                    ("aggressiveness_type", "passive"),
                ),
                npc_stats_source=DARKAN_SHIELD_OF_ARRAV_WEAPONSMASTER_NPC_SOURCE,
            ),
        ),
        produced_inventory=(("Weapon store key", 1), ("Phoenix crossbow", 2),),
        source=f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_WEAPONSMASTER_NPC_SOURCE}",
    ),
    QuestStageRequirement(
        stage=6,
        description="Hand Straven Jonny's intelligence report to join the Phoenix Gang.",
        variant=SHIELD_VARIANT_PHOENIX,
        required_routes=(SHIELD_ROUTE_PHOENIX,),
        consumed_inventory=(("Intel report", 1),),
        produced_inventory=(("Weapon store key", 1),),
        auto_actions=("Hand Straven Jonny's intelligence report",),
        source=f"{DARKAN_SHIELD_OF_ARRAV_STRAVEN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=6,
        description="Hand Katrine two Phoenix crossbows to join the Black Arm Gang.",
        variant=SHIELD_VARIANT_BLACK_ARM,
        required_routes=(SHIELD_ROUTE_BLACK_ARM,),
        consumed_inventory=(("Phoenix crossbow", 2),),
        auto_actions=("Hand Katrine two Phoenix crossbows",),
        source=f"{DARKAN_SHIELD_OF_ARRAV_KATRINE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=7,
        description="Search the Phoenix Gang chest for the right shield half.",
        variant=SHIELD_VARIANT_PHOENIX,
        required_routes=(SHIELD_ROUTE_PHOENIX,),
        auto_actions=("Search the Phoenix Gang shield chest",),
        produced_inventory=(("Broken shield (Phoenix half)", 1),),
        source=f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=7,
        description="Search the Black Arm Gang cupboard for the left shield half.",
        variant=SHIELD_VARIANT_BLACK_ARM,
        required_routes=(SHIELD_ROUTE_BLACK_ARM,),
        auto_actions=("Search the Black Arm Gang cupboard",),
        produced_inventory=(("Broken shield (Black Arm half)", 1),),
        source=f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=8,
        description="Show King Roald the Phoenix shield half.",
        variant=SHIELD_VARIANT_PHOENIX,
        required_routes=(SHIELD_ROUTE_PHOENIX,),
        required_inventory=(("Broken shield (Phoenix half)", 1),),
        auto_actions=("Show King Roald the Phoenix shield half",),
        source=f"{DARKAN_SHIELD_OF_ARRAV_KING_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=8,
        description="Show King Roald the Black Arm shield half.",
        variant=SHIELD_VARIANT_BLACK_ARM,
        required_routes=(SHIELD_ROUTE_BLACK_ARM,),
        required_inventory=(("Broken shield (Black Arm half)", 1),),
        auto_actions=("Show King Roald the Black Arm shield half",),
        source=f"{DARKAN_SHIELD_OF_ARRAV_KING_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=9,
        description="Have Curator Haig Halen authenticate the Phoenix shield half.",
        variant=SHIELD_VARIANT_PHOENIX,
        required_routes=(SHIELD_ROUTE_PHOENIX,),
        consumed_inventory=(("Broken shield (Phoenix half)", 1),),
        produced_inventory=(("Half certificate (Phoenix)", 2),),
        auto_actions=("Have Curator Haig Halen authenticate the Phoenix shield half",),
        source=f"{DARKAN_SHIELD_OF_ARRAV_CURATOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=9,
        description="Have Curator Haig Halen authenticate the Black Arm shield half.",
        variant=SHIELD_VARIANT_BLACK_ARM,
        required_routes=(SHIELD_ROUTE_BLACK_ARM,),
        consumed_inventory=(("Broken shield (Black Arm half)", 1),),
        produced_inventory=(("Half certificate (Black Arm)", 2),),
        auto_actions=("Have Curator Haig Halen authenticate the Black Arm shield half",),
        source=f"{DARKAN_SHIELD_OF_ARRAV_CURATOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=10,
        description="Trade one duplicate Phoenix half certificate through your Black Arm contact and combine the certificate.",
        variant=SHIELD_VARIANT_PHOENIX,
        required_routes=(SHIELD_ROUTE_PHOENIX,),
        consumed_inventory=(("Half certificate (Phoenix)", 1),),
        produced_inventory=(("Certificate", 1),),
        source=f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_CURATOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=10,
        description="Trade one duplicate Black Arm half certificate through your Phoenix contact and combine the certificate.",
        variant=SHIELD_VARIANT_BLACK_ARM,
        required_routes=(SHIELD_ROUTE_BLACK_ARM,),
        consumed_inventory=(("Half certificate (Black Arm)", 1),),
        produced_inventory=(("Certificate", 1),),
        source=f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_CURATOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=11,
        description="Give King Roald the full certificate to claim the reward.",
        consumed_inventory=(("Certificate", 1),),
        auto_actions=("Claim the Shield of Arrav reward from King Roald",),
        source=f"{DARKAN_SHIELD_OF_ARRAV_KING_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_SOURCE}",
    ),
)

DRAGON_SLAYER_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "The Guildmaster says I need to prove myself before Oziach will sell me rune platebodies."),
    _simple_stage(2, "Oziach says I must slay Elvarg on Crandor to prove myself a hero."),
    _simple_stage(3, "The Guildmaster can explain how to reach Crandor and how to survive dragonfire."),
    _simple_stage(4, "The Duke of Lumbridge has an anti-dragon shield for the fight with Elvarg."),
    _simple_stage(5, "Melzar's Maze contains one piece of the Crandor map."),
    _simple_stage(6, "Wormbrain has another piece of the Crandor map in Port Sarim jail."),
    _simple_stage(7, "The Oracle knows how to reach the third map piece under Ice Mountain."),
    _simple_stage(8, "The magic door below Ice Mountain needs the Oracle's four items."),
    _simple_stage(9, "I have all three map pieces and can assemble the Crandor map."),
    _simple_stage(10, "The Lady Lumbridge is for sale in Port Sarim."),
    _simple_stage(11, "The Lady Lumbridge needs planks, steel nails, and a hammer before it can sail."),
    _simple_stage(12, "Ned will captain the Lady Lumbridge if I show him the Crandor map."),
    _simple_stage(13, "Captain Ned is waiting at the Lady Lumbridge to sail for Crandor."),
    _simple_stage(14, "I reached Crandor. Elvarg must be slain while I am protected from dragonfire."),
    _simple_stage(15, "Elvarg is dead. Oziach needs to hear that I defeated the dragon."),
    _simple_stage(16, "Oziach accepted me as a true hero.", "Quest complete!"),
)

GOBLIN_DIPLOMACY_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "The goblin generals want to try orange goblin mail."),
    _simple_stage(2, "The generals rejected orange goblin mail and now want blue goblin mail."),
    _simple_stage(3, "The generals rejected blue goblin mail and now want regular brown goblin mail."),
    _simple_stage(4, "The generals chose brown armour and rewarded me.", "Quest complete!"),
)

ERNEST_THE_CHICKEN_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Veronica asked me to find Ernest inside Draynor Manor."),
    _simple_stage(2, "Professor Oddenstein says Ernest has been turned into a chicken."),
    _simple_stage(3, "Oddenstein needs his pressure gauge, rubber tube, and oil can to repair the machine."),
    _simple_stage(4, "I poisoned the fish food and can use it on the manor fountain."),
    _simple_stage(5, "I recovered the pressure gauge from the fountain."),
    _simple_stage(6, "A grimy key from the compost heap should open the room with the rubber tube."),
    _simple_stage(7, "I recovered the rubber tube from the locked room."),
    _simple_stage(8, "I recovered the oil can from the basement puzzle and should return all three parts to Oddenstein."),
    _simple_stage(9, "Professor Oddenstein restored Ernest and rewarded me.", "Quest complete!"),
)

BLACK_KNIGHTS_FORTRESS_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Sir Amik Varze asked me to infiltrate the Black Knights' Fortress."),
    _simple_stage(2, "I entered the fortress in disguise and need to learn the Black Knights' plan."),
    _simple_stage(3, "The Black Knights' potion can be ruined by dropping the wrong cabbage into the cauldron."),
    _simple_stage(4, "The potion is ruined. I should report back to Sir Amik Varze."),
    _simple_stage(5, "Sir Amik Varze rewarded me for stopping the Black Knights.", "Quest complete!"),
)

FIGHT_ARENA_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "Lady Servil asked me to rescue her husband and son from General Khazard's arena.",
        "I need a Khazard disguise before entering the jail.",
    ),
    _simple_stage(2, "I borrowed the Khazard helmet and armour and should wear them to enter the jail."),
    _simple_stage(3, "Jeremy says the bald, fat, lazy guard with a goatee keeps the cell keys."),
    _simple_stage(4, "The Khazard barman Angor sells Khali brew for 5 coins."),
    _simple_stage(5, "I have Khali brew and can offer it to the lazy guard."),
    _simple_stage(6, "The lazy guard is asleep. I can steal the Khazard cell keys."),
    _simple_stage(7, "I have the cell keys and can open Jeremy's cell to reach the arena."),
    _simple_stage(8, "Sir Servil is trapped in the arena with a Khazard ogre."),
    _simple_stage(9, "General Khazard sent a Khazard scorpion against me."),
    _simple_stage(10, "Bouncer is General Khazard's final mandatory arena beast."),
    _simple_stage(11, "General Khazard offered an optional fight. I can leave and return to Lady Servil."),
    _simple_stage(12, "Lady Servil rewarded me for rescuing her family.", "Quest complete!"),
)

MERLINS_CRYSTAL_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "King Arthur asked me to find out how Merlin was trapped.",
        "The knights of the round table may know how to reach Morgan Le Faye's stronghold and free Merlin.",
    ),
    _simple_stage(
        2,
        "Sir Lancelot says Morgan Le Faye's stronghold can be entered by sea.",
        "I should hide in a delivery crate near the Catherby candle-maker.",
    ),
    _simple_stage(
        3,
        "I reached Keep Le Faye.",
        "Sir Mordred guards the stronghold, and Morgan may reveal how to break Merlin's crystal if he is defeated.",
    ),
    _simple_stage(
        4,
        "Morgan Le Faye told me the ritual needs bat bones, a lit black candle, the binding words, and Excalibur.",
        "I need wax for the candle-maker before I can get a black candle.",
    ),
    _simple_stage(
        5,
        "The candle-maker made a black candle.",
        "The Lady of the Lake has Excalibur and wants me to prove I am worthy.",
    ),
    _simple_stage(
        6,
        "The Lady of the Lake gave me Excalibur after I helped the beggar.",
        "I must summon and bind Thrantax at the chaos altar with bat bones and a lit black candle.",
    ),
    _simple_stage(
        7,
        "Thrantax is bound.",
        "Merlin's crystal can now be shattered with Excalibur.",
    ),
    _simple_stage(8, "I freed Merlin and King Arthur made me a knight of the round table.", "Quest complete!"),
)


MERLINS_CRYSTAL_STAGE_REQUIREMENTS: Tuple[QuestStageRequirement, ...] = (
    QuestStageRequirement(
        stage=1,
        description="Investigate Merlin's crystal with the relevant round-table knights.",
        auto_actions=("Complete the round-table investigation with Sir Gawain, Sir Lucan, and Sir Lancelot",),
        source=(
            f"{MERLINS_CRYSTAL_SOURCE}; {MERLINS_CRYSTAL_SIR_GAWAIN_SOURCE}; "
            f"{MERLINS_CRYSTAL_SIR_LUCAN_SOURCE}; {MERLINS_CRYSTAL_SIR_LANCELOT_SOURCE}"
        ),
    ),
    QuestStageRequirement(
        stage=2,
        description="Hide in the Catherby delivery crate to enter Keep Le Faye.",
        auto_actions=("Reach Keep Le Faye through the Catherby crate delivery",),
        source=f"{MERLINS_CRYSTAL_KEEP_SOURCE}; {MERLINS_CRYSTAL_CRATE_SCENE_SOURCE}",
    ),
    QuestStageRequirement(
        stage=3,
        description="Defeat Sir Mordred in Keep Le Faye.",
        combat_encounters=(
            QuestCombatEncounter(
                encounter_id=f"{MERLINS_CRYSTAL_ID}_sir_mordred_39",
                display_name="Sir Mordred",
                level=39,
                source=f"{MERLINS_CRYSTAL_KEEP_SOURCE}; {MERLINS_CRYSTAL_MORDRED_SOURCE}; {MERLINS_CRYSTAL_MORDRED_NPC_SOURCE}",
                source_text="Sir Mordred is attacked in Keep Le Faye and Morgan appears after he is defeated.",
                npc_stats=(
                    ("hitpoints", 500),
                    ("attack", 33),
                    ("strength", 33),
                    ("defence", 33),
                    ("magic", 1),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 57),
                    ("attack_range", -1),
                    ("attack_style", "melee"),
                    ("attack_bonus", "slash_att"),
                    ("aggressiveness_type", "aggressive"),
                ),
                npc_stats_source=MERLINS_CRYSTAL_MORDRED_NPC_SOURCE,
            ),
        ),
        source=(
            f"{MERLINS_CRYSTAL_KEEP_SOURCE}; {MERLINS_CRYSTAL_MORDRED_SOURCE}; "
            f"{MERLINS_CRYSTAL_MORGAN_SOURCE}; {MERLINS_CRYSTAL_MORDRED_NPC_SOURCE}"
        ),
    ),
    QuestStageRequirement(
        stage=4,
        description="Question Morgan Le Faye and collect wax safely from a beehive.",
        required_inventory=(("Bucket", 1), ("Insect repellent", 1)),
        consumed_inventory=(("Bucket", 1),),
        produced_inventory=(("Bucket of wax", 1),),
        auto_actions=("Question Morgan Le Faye about Excalibur and the binding words",),
        source=(
            f"{MERLINS_CRYSTAL_MORGAN_SOURCE}; {MERLINS_CRYSTAL_BEEHIVE_SOURCE}; {MERLINS_CRYSTAL_BEEKEEPER_SOURCE}; "
            f"{MERLINS_CRYSTAL_2011SCAPE_CATHERBY_SPAWN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
        ),
    ),
    QuestStageRequirement(
        stage=5,
        description="Exchange the bucket of wax for a black candle.",
        consumed_inventory=(("Bucket of wax", 1),),
        produced_inventory=(("Black candle", 1),),
        auto_actions=("Ask the Catherby candle-maker for a black candle",),
        source=f"{MERLINS_CRYSTAL_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=6,
        description="Pass the Lady of the Lake's Port Sarim test and receive Excalibur.",
        consumed_inventory=(("Bread", 1),),
        produced_inventory=(("Excalibur", 1),),
        auto_actions=("Accept the Lady of the Lake's test in Taverley", "Give bread to the Port Sarim beggar"),
        source=f"{MERLINS_CRYSTAL_LADY_SOURCE}; {MERLINS_CRYSTAL_BEGGAR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=7,
        description="Bind Thrantax, shatter Merlin's crystal with Excalibur, and report to King Arthur.",
        required_inventory=(("Bat bones", 1), ("Black candle", 1)),
        consumed_inventory=(("Bat bones", 1), ("Black candle", 1)),
        produced_inventory=(("Lit black candle", 1),),
        required_tools=(("Tinderbox", 1), ("Excalibur", 1)),
        auto_actions=(
            "Read the chaos altar inscription",
            "Bind Thrantax with Snarthon Candtrick Termanto",
            "Shatter Merlin's crystal with Excalibur",
            "Report Merlin's freedom to King Arthur",
        ),
        source=(
            f"{MERLINS_CRYSTAL_SOURCE}; {MERLINS_CRYSTAL_RITUAL_SCENE_SOURCE}; "
            f"{MERLINS_CRYSTAL_THRANTAX_SOURCE}; {MERLINS_CRYSTAL_THRANTAX_NPC_SOURCE}; "
            f"{MERLINS_CRYSTAL_KING_ARTHUR_SOURCE}; "
            f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}; {MERLINS_CRYSTAL_WIKI_SOURCE}"
        ),
    ),
)

HEROES_QUEST_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "Achietties accepted my application and set three proof tasks.",
        "I need an Entranan Firebird feather, a Master Thieves' armband, and a cooked Lava eel.",
    ),
    _simple_stage(2, "Gerrant in Port Sarim can explain how to catch lava eels."),
    _simple_stage(3, "Gerrant gave me Blamish snail slime for a lava-proof rod."),
    _simple_stage(4, "I made Blamish oil from the slime and unfinished harralander."),
    _simple_stage(5, "I coated an ordinary fishing rod with Blamish oil."),
    _simple_stage(6, "I caught a raw Lava eel with the oily fishing rod."),
    _simple_stage(
        7,
        "I cooked the Lava eel.",
        "I still need Ice gloves before I can safely collect the firebird feather.",
    ),
    _simple_stage(8, "I defeated the Ice Queen and obtained Ice gloves.", "The Entranan Firebird feather remains."),
    _simple_stage(
        9,
        "I collected the Entranan Firebird feather.",
        "Now I need the Master Thieves' armband through my Shield of Arrav gang contacts.",
    ),
    _simple_stage(10, "My gang contacts can get me into Scarface Pete's mansion for Pete's candlestick."),
    _simple_stage(11, "I have Pete's candlestick and can trade it for the Master Thieves' armband."),
    _simple_stage(12, "I have the cooked Lava eel, Fire feather, and Thieves' armband for Achietties."),
    _simple_stage(13, "Achietties accepted my proof items and opened the Heroes' Guild.", "Quest complete!"),
)

HEROES_QUEST_STAGE_REQUIREMENTS: Tuple[QuestStageRequirement, ...] = (
    QuestStageRequirement(
        stage=1,
        description="Accept Achietties' three proof item challenge.",
        auto_actions=("Accept Achietties' three proof item challenge",),
        source=f"{HEROES_QUEST_DARKAN_SOURCE}; {HEROES_QUEST_ACHIETTIES_SOURCE}",
    ),
    QuestStageRequirement(
        stage=2,
        description="Ask Gerrant how to catch a lava eel and receive Blamish snail slime.",
        auto_actions=("Ask Gerrant how to catch lava eels",),
        produced_inventory=(("Blamish snail slime", 1),),
        source=f"{HEROES_QUEST_PORT_SARIM_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=3,
        description="Mix Blamish snail slime into unfinished harralander to make Blamish oil.",
        consumed_inventory=(("Blamish snail slime", 1), ("Harralander potion (unf)", 1)),
        produced_inventory=(("Blamish oil", 1),),
        source=f"{HEROES_QUEST_HERBLORE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=4,
        description="Coat a fishing rod with Blamish oil.",
        consumed_inventory=(("Blamish oil", 1), ("Fishing rod", 1)),
        produced_inventory=(("Oily fishing rod", 1),),
        source=f"{HEROES_QUEST_DARKAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=5,
        description="Catch a raw Lava eel at a lava eel fishing spot.",
        consumed_inventory=(("Fishing bait", 1),),
        produced_inventory=(("Raw lava eel", 1),),
        required_tools=(("Oily fishing rod", 1),),
        auto_actions=("Reach a lava eel fishing spot in Taverley Dungeon or the Lava Maze",),
        source=(
            f"{HEROES_QUEST_FISH_SOURCE}; {HEROES_QUEST_FISHING_SPOT_SOURCE}; "
            f"{HEROES_QUEST_FISHING_SOURCE}; {HEROES_QUEST_PORT_SARIM_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
        ),
    ),
    QuestStageRequirement(
        stage=6,
        description="Cook the raw Lava eel.",
        consumed_inventory=(("Raw lava eel", 1),),
        produced_inventory=(("Lava eel", 1),),
        auto_actions=("Cook the raw Lava eel",),
        source=f"{HEROES_QUEST_COOKING_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=7,
        description="Clear the Ice Queen lair rockslide and defeat the Ice Queen.",
        required_tools=(("Pickaxe", 1),),
        auto_actions=(
            "Clear the Ice Queen lair rockslide",
            "Reach the Ice Queen lair through a Dusty key or Agility shortcut route",
        ),
        combat_encounters=(
            QuestCombatEncounter(
                encounter_id=f"{HEROES_QUEST_ID}_ice_queen_111",
                display_name="Ice Queen",
                level=111,
                source=(
                    f"{HEROES_QUEST_ICE_QUEEN_DUNGEON_SOURCE}; {HEROES_QUEST_ICE_QUEEN_NPC_SOURCE}; "
                    f"{HEROES_QUEST_WIKI_SOURCE}"
                ),
                source_text="The Ice Queen is defeated in her lair to obtain Ice gloves before collecting the Fire feather.",
                npc_stats=(
                    ("hitpoints", 1050),
                    ("attack", 95),
                    ("strength", 94),
                    ("defence", 95),
                    ("magic", 1),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 100),
                    ("attack_range", -1),
                    ("attack_style", "melee"),
                    ("attack_bonus", "crush_att"),
                    ("aggressiveness_type", "passive"),
                ),
                npc_stats_source=HEROES_QUEST_ICE_QUEEN_NPC_SOURCE,
            ),
        ),
        produced_inventory=(("Ice gloves", 1),),
        source=f"{HEROES_QUEST_ICE_QUEEN_DUNGEON_SOURCE}; {HEROES_QUEST_ICE_QUEEN_NPC_SOURCE}",
    ),
    QuestStageRequirement(
        stage=8,
        description="Defeat the Entranan Firebird and pick up its feather with Ice gloves.",
        required_tools=(("Ice gloves", 1),),
        auto_actions=("Reach Entrana without prohibited combat equipment",),
        combat_encounters=(
            QuestCombatEncounter(
                encounter_id=f"{HEROES_QUEST_ID}_entrana_fire_bird_2",
                display_name="Entrana Fire Bird",
                level=2,
                source=f"{HEROES_QUEST_WIKI_SOURCE}; {DARKAN_NPC_LIST_SOURCE}; {HEROES_QUEST_ENTRANA_FIREBIRD_NPC_SOURCE}",
                source_text="The Fire feather is obtained by killing an Entranan Firebird and can only be picked up with Ice gloves.",
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
        ),
        produced_inventory=(("Fire feather", 1),),
        source=f"{HEROES_QUEST_DARKAN_SOURCE}; {HEROES_QUEST_ENTRANA_FIREBIRD_NPC_SOURCE}",
    ),
    QuestStageRequirement(
        stage=9,
        description="Use the Black Arm Gang contacts in Brimhaven and receive Id papers from Trobert.",
        variant=HEROES_VARIANT_BLACK_ARM,
        required_routes=(HEROES_ROUTE_BLACK_ARM,),
        auto_actions=(
            "Ask Katrine about the Scarface Pete candlestick mission",
            "Enter the Black Arm Brimhaven hideout with the Four leaved clover password",
            "Accept Trobert's deputy guard impersonation mission",
        ),
        produced_inventory=(("Id papers", 1),),
        source=(
            f"{HEROES_QUEST_KATRINE_SOURCE}; {HEROES_QUEST_BRIMHAVEN_SOURCE}; "
            f"{HEROES_QUEST_TROBERT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
        ),
    ),
    QuestStageRequirement(
        stage=9,
        description="Use the Phoenix Gang contacts in Brimhaven and learn about the mansion's secret panel.",
        variant=HEROES_VARIANT_PHOENIX,
        required_routes=(HEROES_ROUTE_PHOENIX,),
        auto_actions=(
            "Ask Straven about the Scarface Pete candlestick mission",
            "Ask Alfonse the waiter for gherkins",
            "Ask Charlie the cook about the Phoenix guard inside Scarface Pete's mansion",
        ),
        source=f"{HEROES_QUEST_STRAVEN_SOURCE}; {HEROES_QUEST_ALFONSO_SOURCE}; {HEROES_QUEST_CHARLIE_SOURCE}",
    ),
    QuestStageRequirement(
        stage=10,
        description="Enter Scarface Pete's mansion as a Black Arm deputy guard and search the candlestick chest.",
        variant=HEROES_VARIANT_BLACK_ARM,
        required_routes=(HEROES_ROUTE_BLACK_ARM,),
        required_tools=(("Black full helm", 1), ("Black platebody", 1), ("Black platelegs", 1)),
        consumed_inventory=(("Id papers", 1),),
        auto_actions=("Show the Id papers to Garv", "Search Scarface Pete's candlestick chest"),
        produced_inventory=(("Pete's candlestick", 1),),
        source=f"{HEROES_QUEST_MANSION_DOOR_SOURCE}; {HEROES_QUEST_BRIMHAVEN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=10,
        description=(
            "Use the Phoenix secret panel and a Black Arm Gang partner's key to attack Grip after "
            "that partner lures him, then receive one of the candlesticks they retrieve."
        ),
        variant=HEROES_VARIANT_PHOENIX,
        required_routes=(HEROES_ROUTE_PHOENIX,),
        auto_actions=(
            "Enter Scarface Pete's mansion through the Phoenix Gang secret panel",
            "Unlock the window room with a Black Arm Gang partner's miscellaneous key",
            "Receive one of Pete's candlesticks after the Black Arm Gang partner opens the chest with Grip's key",
        ),
        combat_encounters=(
            QuestCombatEncounter(
                encounter_id=f"{HEROES_QUEST_ID}_grip_22",
                display_name="Grip",
                level=22,
                source=f"{HEROES_QUEST_WIKI_SOURCE}; {HEROES_QUEST_TROBERT_SOURCE}; {HEROES_QUEST_GRIP_NPC_SOURCE}",
                source_text=(
                    "The Phoenix Gang member attacks Grip from the window room after a Black Arm Gang partner "
                    "lures him; Grip's death enables that partner to recover Grip's key."
                ),
                npc_stats=(
                    ("hitpoints", 250),
                    ("attack", 18),
                    ("strength", 17),
                    ("defence", 18),
                    ("magic", 1),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 30),
                    ("attack_range", -1),
                    ("attack_style", "melee"),
                    ("attack_bonus", "slash_att"),
                    ("aggressiveness_type", "passive"),
                ),
                npc_stats_source=HEROES_QUEST_GRIP_NPC_SOURCE,
            ),
        ),
        produced_inventory=(("Pete's candlestick", 1),),
        source=(
            f"{HEROES_QUEST_BRIMHAVEN_SOURCE}; {HEROES_QUEST_GRIP_NPC_SOURCE}; "
            f"{HEROES_QUEST_WIKI_SOURCE}"
        ),
    ),
    QuestStageRequirement(
        stage=11,
        description="Give Pete's candlestick to Katrine for the Master Thieves' armband.",
        variant=HEROES_VARIANT_BLACK_ARM,
        required_routes=(HEROES_ROUTE_BLACK_ARM,),
        consumed_inventory=(("Pete's candlestick", 1),),
        produced_inventory=(("Thieves' armband", 1),),
        auto_actions=("Give Pete's candlestick to Katrine",),
        source=f"{HEROES_QUEST_KATRINE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=11,
        description="Give Pete's candlestick to Straven for the Master Thieves' armband.",
        variant=HEROES_VARIANT_PHOENIX,
        required_routes=(HEROES_ROUTE_PHOENIX,),
        consumed_inventory=(("Pete's candlestick", 1),),
        produced_inventory=(("Thieves' armband", 1),),
        auto_actions=("Give Pete's candlestick to Straven",),
        source=f"{HEROES_QUEST_STRAVEN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=12,
        description="Give Achietties the cooked Lava eel, Master Thieves' armband, and Fire feather.",
        consumed_inventory=(("Lava eel", 1), ("Thieves' armband", 1), ("Fire feather", 1)),
        auto_actions=("Hand Achietties the Lava eel, Thieves' armband, and Fire feather",),
        source=f"{HEROES_QUEST_ACHIETTIES_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
)

WITCHS_HOUSE_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Harvey asked me to get his ball back from the witch's garden."),
    _simple_stage(2, "I found the front door key under a potted plant."),
    _simple_stage(3, "I entered the Witch's house and need to investigate the security system."),
    _simple_stage(4, "I found a magnet in the cupboard."),
    _simple_stage(5, "The mouse-hole mechanism needs cheese and the magnet."),
    _simple_stage(6, "The back of the house is open, but the witch patrols the hall."),
    _simple_stage(7, "I reached the electric gate and need gloves before touching it."),
    _simple_stage(8, "I passed the electric gate and should search the fountain for the shed key."),
    _simple_stage(9, "I found the backroom key and can unlock the shed."),
    _simple_stage(10, "The Witch's experiment is guarding the ball in the shed."),
    _simple_stage(11, "The experiment is defeated. I can pick up the ball and return it to Harvey."),
    _simple_stage(12, "Harvey got his ball back.", "Quest complete!"),
)

TAI_BWO_WANNAI_TRIO_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Timfraku wants his three sons to return to Tai Bwo Wannai."),
    _simple_stage(2, "I helped Tiadeche learn the way to catch karambwan."),
    _simple_stage(3, "I helped Tamayu prepare for his fight with the Shaikahan."),
    _simple_stage(4, "I helped Tinsay gather and prepare unusual food for the village."),
    _simple_stage(5, "The three sons are ready to return to Tai Bwo Wannai."),
    _simple_stage(6, "I reported back to Timfraku and restored the family.", "Quest complete!"),
)

MOURNINGS_END_PART_II_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "The head mourner has opened the route toward the excavation below West Ardougne."),
    _simple_stage(2, "I entered the Temple of Light beneath Arandar."),
    _simple_stage(3, "I worked through the temple mirrors and coloured light beams."),
    _simple_stage(4, "I reached the death altar deep in the temple."),
    _simple_stage(5, "I uncovered the mourners' plan and secured a death talisman."),
    _simple_stage(6, "I escaped the temple and returned with news of what I found."),
    _simple_stage(7, "The path to the death altar is open.", "Quest complete!"),
)

SWAN_SONG_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Herman Caranos needs help defending the Piscatoris Fishing Colony."),
    _simple_stage(2, "I recruited the Wise Old Man for one last adventure."),
    _simple_stage(3, "We repaired the colony and prepared for the sea troll attack."),
    _simple_stage(4, "I fought through the sea trolls attacking the colony."),
    _simple_stage(5, "The Sea Troll Queen was defeated and the colony was saved."),
    _simple_stage(6, "Piscatoris is secure and the monkfish grounds are available.", "Quest complete!"),
)

LUNAR_DIPLOMACY_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Lokar Searunner offered passage toward the Moon Clan."),
    _simple_stage(2, "I sailed from Rellekka through Pirates' Cove toward Lunar Isle."),
    _simple_stage(3, "I met the Moon Clan and learned why they distrust the Fremennik."),
    _simple_stage(4, "I prepared a waking sleep potion for the Oneiromancer."),
    _simple_stage(5, "I made a lunar staff and gathered ceremonial lunar clothing."),
    _simple_stage(6, "I entered the dream world and faced the Moon Clan's trials."),
    _simple_stage(7, "I defeated myself in the dream world."),
    _simple_stage(8, "The Moon Clan accepted me and the astral altar is open.", "Quest complete!"),
)

LEGACY_OF_SEERGAZE_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "A mercenary near Paterdomus reported suspicious activity in Morytania."),
    _simple_stage(2, "Drezel's discovery beneath Paterdomus pointed toward the columbarium."),
    _simple_stage(3, "I helped the Myreque investigate the Vyrewatch and Meiyerditch."),
    _simple_stage(4, "I created the Ivandis flail to fight the Vyrewatch."),
    _simple_stage(5, "I performed a cremation rite and recovered a key to the hidden storage."),
    _simple_stage(6, "I found the blood talisman and reported back to the Myreque."),
    _simple_stage(7, "The blood altar and columbarium rewards are now available.", "Quest complete!"),
)

KNIGHTS_SWORD_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "I told the Squire I would help replace the sword he lost.",
        "Reldo in Varrock Palace library may know where to find Imcando dwarves.",
    ),
    _simple_stage(
        2,
        "Reldo said some Imcando dwarves live on the southern peninsula of Asgarnia.",
        "They dislike strangers and love redberry pies.",
    ),
    _simple_stage(
        3,
        "I found Thurgo and gave him a Redberry pie.",
        "He will help now that he trusts me.",
    ),
    _simple_stage(4, "Thurgo needs a picture of the sword before he can make a replacement."),
    _simple_stage(5, "The Squire told me about a portrait in Sir Vyvin's room that shows the sword."),
    _simple_stage(
        6,
        "Thurgo needs two Iron bars and some Blurite ore to make the replica sword.",
        "Blurite ore is found below the cliff near Thurgo's house.",
    ),
    _simple_stage(
        7,
        "Thurgo made a replica of Sir Vyvin's sword and I returned it to the Squire.",
        "Quest complete!",
    ),
)

KNIGHTS_SWORD_STAGE_REQUIREMENTS: Tuple[QuestStageRequirement, ...] = (
    QuestStageRequirement(
        stage=2,
        description="Give Thurgo a Redberry pie.",
        consumed_inventory=(("Redberry pie", 1),),
        source=f"{KNIGHTS_SWORD_QUEST_SOURCE_PATH}; {KNIGHTS_SWORD_THURGO_SOURCE_PATH}",
    ),
    QuestStageRequirement(
        stage=6,
        description="Give Thurgo the materials for the replica sword.",
        consumed_inventory=(("Blurite ore", 1), ("Iron bar", 2)),
        source=f"{KNIGHTS_SWORD_QUEST_SOURCE_PATH}; {KNIGHTS_SWORD_THURGO_SOURCE_PATH}",
    ),
)

FAMILY_CREST_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Dimintheis asked me to recover the three pieces of the Fitzharmon family crest."),
    _simple_stage(2, "Caleb in Catherby has one crest piece and wants help with a cooked fish salad."),
    _simple_stage(3, "Caleb needs cooked shrimp, salmon, tuna, bass, and swordfish for his fish salad."),
    _simple_stage(4, "Caleb gave me his crest piece and said Avan was searching for treasure near Al Kharid."),
    _simple_stage(5, "The Al Kharid gem trader can point me toward Avan Fitzharmon."),
    _simple_stage(6, "Avan wants a ruby ring and ruby necklace made from perfect gold."),
    _simple_stage(7, "Boot in the Dwarven Mines knows where perfect gold can be found."),
    _simple_stage(8, "The perfect gold is in the Witchaven dungeon beyond a lever puzzle."),
    _simple_stage(9, "I smelted the perfect gold ore into perfect gold bars."),
    _simple_stage(10, "I made a perfect ruby ring and a perfect ruby necklace for Avan."),
    _simple_stage(11, "Avan gave me his crest piece and directed me to Johnathon near the Wilderness."),
    _simple_stage(12, "Johnathon is poisoned and needs an antipoison before he can help."),
    _simple_stage(13, "Chronozon has Johnathon's crest piece in Edgeville Dungeon."),
    _simple_stage(14, "I have all three crest pieces and can join them into the Family crest."),
    _simple_stage(15, "The Family crest is restored and ready to return to Dimintheis."),
    _simple_stage(16, "Dimintheis accepted the restored Family crest and gave me Family gauntlets.", "Quest complete!"),
)

FAMILY_CREST_STAGE_REQUIREMENTS: Tuple[QuestStageRequirement, ...] = (
    QuestStageRequirement(
        stage=2,
        description="Ask Caleb about his crest piece and agree to collect the cooked fish.",
        auto_actions=("Ask Caleb about the fish salad",),
        source=f"{FAMILY_CREST_CALEB_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=3,
        description="Give Caleb the cooked fish for his fish salad.",
        consumed_inventory=(
            ("Shrimps", 1),
            ("Salmon", 1),
            ("Tuna", 1),
            ("Bass", 1),
            ("Swordfish", 1),
        ),
        produced_inventory=(("Caleb crest", 1),),
        source=f"{FAMILY_CREST_CALEB_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=4,
        description="Ask Caleb where Avan might be found.",
        required_tools=(("Caleb crest", 1),),
        auto_actions=("Ask Caleb where Avan is searching for treasure",),
        source=f"{FAMILY_CREST_CALEB_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=5,
        description="Ask the Al Kharid gem trader about Avan.",
        auto_actions=("Ask the Al Kharid gem trader about Avan",),
        source=FAMILY_CREST_GEM_TRADER_SOURCE,
    ),
    QuestStageRequirement(
        stage=6,
        description="Ask Avan what he wants in exchange for his crest piece.",
        auto_actions=("Ask Avan about perfect gold jewellery",),
        source=FAMILY_CREST_AVAN_SOURCE,
    ),
    QuestStageRequirement(
        stage=7,
        description="Ask Boot where perfect gold can be found.",
        auto_actions=("Ask Boot about perfect gold",),
        source=FAMILY_CREST_BOOT_SOURCE,
    ),
    QuestStageRequirement(
        stage=8,
        description="Solve the Witchaven dungeon route and mine two perfect gold ores.",
        required_tools=(("Pickaxe", 1),),
        auto_actions=(
            "Reach the Witchaven perfect gold mine",
            "Solve the Witchaven dungeon lever puzzle",
            "Mine two perfect gold ores",
        ),
        produced_inventory=(("Perfect gold ore", 2),),
        source=(
            f"{FAMILY_CREST_DARKAN_SOURCE}; {FAMILY_CREST_WITCHHAVEN_PUZZLE_SOURCE}; "
            f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}"
        ),
    ),
    QuestStageRequirement(
        stage=9,
        description="Smelt the perfect gold ore into perfect gold bars.",
        consumed_inventory=(("Perfect gold ore", 2),),
        produced_inventory=(("Perfect gold bar", 2),),
        auto_actions=("Smelt the perfect gold ore in a furnace",),
        source=f"{FAMILY_CREST_DARKAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=10,
        description="Craft Avan's perfect ruby ring and necklace.",
        consumed_inventory=(("Perfect gold bar", 2), ("Ruby", 2)),
        produced_inventory=(("Perfect ruby ring", 1), ("Perfect ruby necklace", 1)),
        required_tools=(("Ring mould", 1), ("Necklace mould", 1),),
        auto_actions=("Craft the perfect ruby ring and perfect ruby necklace",),
        source=f"{FAMILY_CREST_DARKAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=11,
        description="Give Avan the perfect ruby jewellery for his crest piece.",
        consumed_inventory=(("Perfect ruby ring", 1), ("Perfect ruby necklace", 1)),
        produced_inventory=(("Avan crest", 1),),
        required_tools=(("Caleb crest", 1),),
        source=f"{FAMILY_CREST_AVAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=12,
        description="Use antipoison on Johnathon and ask him about Chronozon.",
        # JohnathonFamilyCrestD.java accepts item ids 2446/175/177/179 as
        # unnoted Antipoison doses and deletes one; it rejects the noted twins.
        # The pinned wiki revision asks for "Anti-poison potion (1+ recommended)".
        consumed_inventory_options=(
            (
                ("Antipoison (4)", 1),
                ("Antipoison (3)", 1),
                ("Antipoison (2)", 1),
                ("Antipoison (1)", 1),
            ),
        ),
        required_tools=(("Caleb crest", 1), ("Avan crest", 1)),
        auto_actions=("Use an unnoted antipoison on Johnathon", "Ask Johnathon about Chronozon"),
        source=f"{FAMILY_CREST_JOHNATHON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=13,
        description="Hit Chronozon with all four elemental blast spells and defeat him.",
        required_tools=(("Caleb crest", 1), ("Avan crest", 1)),
        auto_actions=(
            "Reach Chronozon's lair in Edgeville Dungeon",
            "Hit Chronozon with Air, Water, Earth, and Fire Blast",
        ),
        combat_encounters=(
            QuestCombatEncounter(
                encounter_id=f"{FAMILY_CREST_ID}_chronozon_170",
                display_name="Chronozon",
                level=170,
                source=f"{FAMILY_CREST_CHRONOZON_SOURCE}; {FAMILY_CREST_CHRONOZON_NPC_SOURCE}; {FAMILY_CREST_WIKI_SOURCE}",
                source_text="Chronozon drops Johnathon's crest piece after being hit by all four elemental blast spells.",
                npc_stats=(
                    ("hitpoints", 600),
                    ("attack", 173),
                    ("strength", 172),
                    ("defence", 173),
                    ("magic", 1),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 180),
                    ("attack_range", -1),
                    ("attack_style", "melee"),
                    ("attack_bonus", "slash_att"),
                    ("aggressiveness_type", "aggressive"),
                    # No period or Darkan source gates this fight on player combat
                    # level; defaulting to Chronozon's own level 170 would make it
                    # unreachable (see miniquest-ledger Bork/Tarn precedent).
                    ("minimum_player_combat", 1),
                ),
                npc_stats_source=FAMILY_CREST_CHRONOZON_NPC_SOURCE,
            ),
        ),
        produced_inventory=(("Johnathon crest", 1),),
        source=f"{FAMILY_CREST_CHRONOZON_SOURCE}; {FAMILY_CREST_CHRONOZON_NPC_SOURCE}; {FAMILY_CREST_WIKI_SOURCE}",
    ),
    QuestStageRequirement(
        stage=14,
        description="Combine the three crest parts into the restored Family crest.",
        consumed_inventory=(("Caleb crest", 1), ("Avan crest", 1), ("Johnathon crest", 1)),
        produced_inventory=(("Family crest", 1),),
        auto_actions=("Combine the three crest parts",),
        source=f"{FAMILY_CREST_DARKAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=15,
        description="Return the restored Family crest to Dimintheis.",
        consumed_inventory=(("Family crest", 1),),
        source=f"{FAMILY_CREST_DIMINTHEIS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
)

TEMPLE_OF_IKOV_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Lucien gave me the Pendant of lucien and sent me to the Temple of Ikov."),
    _simple_stage(2, "I entered the Temple of Ikov with a light source."),
    _simple_stage(3, "I cut through the temple web and found the Boots of lightness."),
    _simple_stage(4, "I crossed the lava bridge at low weight and picked up the lever."),
    _simple_stage(5, "I placed and pulled the lever near the temple entrance to open the ice-arrow route."),
    _simple_stage(6, "I searched the ice chamber chests and gathered ice arrows."),
    _simple_stage(7, "I disarmed the trapped lever and opened the Fire Warrior route."),
    _simple_stage(8, "I defeated the Fire Warrior of Lesarkus with ice arrows and a suitable bow."),
    _simple_stage(9, "Winelda can teleport me across the lava if I bring twenty Limpwurt roots."),
    _simple_stage(10, "I reached the Staff of Armadyl chamber and must choose whether to aid Lucien or the Guardians."),
    _simple_stage(11, "Lucien or the Guardians accepted my choice.", "Quest complete!"),
)

TEMPLE_OF_IKOV_STAGE_REQUIREMENTS: Tuple[QuestStageRequirement, ...] = (
    QuestStageRequirement(
        stage=1,
        description="Enter the Temple of Ikov with Lucien's pendant and a light source.",
        required_inventory_options=(tuple((item_name, 1) for item_name in LIT_LIGHT_SOURCE_ITEMS),),
        required_tools=(("Pendant of lucien", 1),),
        auto_actions=("Enter the Temple of Ikov",),
        source=(
            f"{TEMPLE_OF_IKOV_DARKAN_SOURCE}; {TEMPLE_OF_IKOV_DUNGEON_SOURCE}; "
            f"{TEMPLE_OF_IKOV_LUCIEN_ARDOUGNE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
        ),
    ),
    QuestStageRequirement(
        stage=2,
        description="Cut through the temple web and take the Boots of lightness.",
        required_tools=(("Knife", 1),),
        auto_actions=("Cut through the Temple of Ikov web", "Pick up the Boots of lightness"),
        produced_inventory=(("Boots of lightness", 1),),
        source=f"{TEMPLE_OF_IKOV_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=3,
        description="Cross the lava bridge at low weight and pick up the lever.",
        required_tools=(("Pendant of lucien", 1), ("Boots of lightness", 1)),
        auto_actions=(
            "Cross the Temple of Ikov lava bridge at low weight",
            "Pick up the Temple of Ikov lever",
        ),
        produced_inventory=(("Lever", 1),),
        source=f"{TEMPLE_OF_IKOV_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=4,
        description="Place and pull the lever near the entrance to open the ice-arrow route.",
        consumed_inventory=(("Lever", 1),),
        auto_actions=("Place and pull the Temple of Ikov lever near the entrance",),
        source=f"{TEMPLE_OF_IKOV_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=5,
        description="Search the ice chamber chests for ice arrows.",
        auto_actions=("Search the Temple of Ikov ice-arrow chests",),
        produced_inventory=(("Ice arrows", 1),),
        source=f"{TEMPLE_OF_IKOV_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=6,
        description="Search the trapped lever for traps, then pull it to open the Fire Warrior route.",
        auto_actions=(
            "Search and disarm the trapped Fire Warrior lever",
            "Pull the disarmed Fire Warrior lever",
        ),
        source=f"{TEMPLE_OF_IKOV_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=7,
        description="Defeat the Fire Warrior of Lesarkus with ice arrows and a compatible bow.",
        required_tools=(("Ice arrows", 1),),
        required_inventory_options=(TEMPLE_OF_IKOV_BOW_OPTIONS,),
        combat_encounters=(
            QuestCombatEncounter(
                encounter_id=f"{TEMPLE_OF_IKOV_ID}_fire_warrior_of_lesarkus_84",
                display_name="Fire Warrior of Lesarkus",
                level=84,
                source=f"{TEMPLE_OF_IKOV_FIRE_WARRIOR_SOURCE}; {TEMPLE_OF_IKOV_FIRE_WARRIOR_NPC_SOURCE}",
                source_text=(
                    "The Fire Warrior can only be damaged by ice arrows fired from a compatible bow."
                ),
                npc_stats=(
                    ("hitpoints", 590),
                    ("attack", 78),
                    ("strength", 78),
                    ("defence", 78),
                    ("magic", 62),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 80),
                    ("attack_range", -1),
                    ("attack_style", "magic"),
                    ("attack_bonus", "magic_att"),
                    ("aggressiveness_type", "passive"),
                ),
                npc_stats_source=TEMPLE_OF_IKOV_FIRE_WARRIOR_NPC_SOURCE,
            ),
        ),
        source=f"{TEMPLE_OF_IKOV_FIRE_WARRIOR_SOURCE}; {TEMPLE_OF_IKOV_FIRE_WARRIOR_NPC_SOURCE}",
    ),
    QuestStageRequirement(
        stage=8,
        description="Pay Winelda twenty Limpwurt roots for a teleport across the lava.",
        consumed_inventory=(("Limpwurt root", 20),),
        auto_actions=("Ask Winelda to teleport across the lava",),
        source=f"{TEMPLE_OF_IKOV_WINELDA_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=9,
        description="Accept the Guardian offer and receive an Armadyl pendant.",
        variant=TEMPLE_OF_IKOV_VARIANT_GUARDIANS,
        required_routes=(TEMPLE_OF_IKOV_ROUTE_GUARDIANS,),
        auto_actions=("Remove the Pendant of lucien and accept the Guardian cleansing",),
        produced_inventory=(("Armadyl pendant", 1),),
        source=f"{TEMPLE_OF_IKOV_GUARDIAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {TEMPLE_OF_IKOV_WIKI_SOURCE}",
    ),
    QuestStageRequirement(
        stage=9,
        description="Side with Lucien, defeat a blocking Guardian, and take the Staff of Armadyl.",
        variant=TEMPLE_OF_IKOV_VARIANT_LUCIEN,
        required_routes=(TEMPLE_OF_IKOV_ROUTE_LUCIEN,),
        required_tools=(("Pendant of lucien", 1),),
        auto_actions=("Take the Staff of Armadyl from the guarded chamber",),
        combat_encounters=(
            QuestCombatEncounter(
                encounter_id=f"{TEMPLE_OF_IKOV_ID}_guardian_of_armadyl_45",
                display_name="Guardian of Armadyl",
                level=45,
                source=(
                    f"{TEMPLE_OF_IKOV_DUNGEON_SOURCE}; {TEMPLE_OF_IKOV_2011SCAPE_SPAWN_SOURCE}; "
                    f"{TEMPLE_OF_IKOV_GUARDIAN_NPC_SOURCE}"
                ),
                source_text=(
                    "Darkan blocks taking the Staff of Armadyl while a Guardian has line of sight; "
                    "AnkiScape models the blocking chamber fight as one Guardian encounter."
                ),
                npc_stats=(
                    ("hitpoints", 500),
                    ("attack", 37),
                    ("strength", 37),
                    ("defence", 37),
                    ("magic", 1),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 60),
                    ("attack_range", -1),
                    ("attack_style", "melee"),
                    ("attack_bonus", "stab_att"),
                    ("aggressiveness_type", "passive"),
                ),
                npc_stats_source=TEMPLE_OF_IKOV_GUARDIAN_NPC_SOURCE,
            ),
        ),
        produced_inventory=(("Staff of armadyl", 1),),
        source=(
            f"{TEMPLE_OF_IKOV_DUNGEON_SOURCE}; {TEMPLE_OF_IKOV_GUARDIAN_NPC_SOURCE}; "
            f"{TEMPLE_OF_IKOV_2011SCAPE_SPAWN_SOURCE}"
        ),
    ),
    QuestStageRequirement(
        stage=10,
        description="Wear the Armadyl pendant and defeat Lucien in Varrock.",
        variant=TEMPLE_OF_IKOV_VARIANT_GUARDIANS,
        required_routes=(TEMPLE_OF_IKOV_ROUTE_GUARDIANS,),
        required_tools=(("Armadyl pendant", 1),),
        combat_encounters=(
            QuestCombatEncounter(
                encounter_id=f"{TEMPLE_OF_IKOV_ID}_lucien_14",
                display_name="Lucien",
                level=14,
                source=f"{TEMPLE_OF_IKOV_LUCIEN_MOB_SOURCE}; {TEMPLE_OF_IKOV_LUCIEN_NPC_SOURCE}",
                source_text="Lucien can be attacked only while wearing the Armadyl pendant.",
                npc_stats=(
                    ("hitpoints", 170),
                    ("attack", 12),
                    ("strength", 11),
                    ("defence", 10),
                    ("magic", 1),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 20),
                    ("attack_range", -1),
                    ("attack_style", "melee"),
                    ("attack_bonus", "stab_att"),
                    ("aggressiveness_type", "passive"),
                ),
                npc_stats_source=TEMPLE_OF_IKOV_LUCIEN_NPC_SOURCE,
            ),
        ),
        source=f"{TEMPLE_OF_IKOV_LUCIEN_MOB_SOURCE}; {TEMPLE_OF_IKOV_LUCIEN_NPC_SOURCE}",
    ),
    QuestStageRequirement(
        stage=10,
        description="Give the Staff of Armadyl to Lucien in Varrock.",
        variant=TEMPLE_OF_IKOV_VARIANT_LUCIEN,
        required_routes=(TEMPLE_OF_IKOV_ROUTE_LUCIEN,),
        consumed_inventory=(("Staff of armadyl", 1),),
        auto_actions=("Give the Staff of Armadyl to Lucien in Varrock",),
        source=f"{TEMPLE_OF_IKOV_LUCIEN_VARROCK_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
)

PRIEST_IN_PERIL_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "King Roald asked me to check on Drezel at Paterdomus, east of Varrock."),
    _simple_stage(2, "I spoke through the locked Paterdomus door and was told to kill the guard dog below the temple."),
    _simple_stage(3, "The Temple guardian dog is dead. I should report back to King Roald."),
    _simple_stage(4, "King Roald was furious. The voice at the door was not Drezel, and I must return to Paterdomus."),
    _simple_stage(5, "I found the real Drezel locked in a cell guarded by Zamorakian monks and a trapped vampyre."),
    _simple_stage(6, "I need the correct key from the monument to unlock Drezel's cell."),
    _simple_stage(7, "Drezel is free, but I need blessed Salve water to trap the vampyre in its coffin."),
    _simple_stage(8, "The vampyre is trapped. Drezel needs essence to purify the River Salve."),
    _simple_stage(9, "Drezel purified the Salve, blessed me, and gave me Wolfbane.", "Quest complete!"),
)


QUEST_OVERRIDES: Tuple[QuestDefinition, ...] = (
    QuestDefinition(
        id=COOKS_ASSISTANT_ID,
        display_name="Cook's Assistant",
        stages=5,
        point_reward=1,
        rewards=(("Coins", 500), ("Sardine", 20)),
        start_point="Speak to the cook in Lumbridge Castle kitchen.",
        requirements=("Used during quest: Bucket x1, Empty pot x1",),
        required_items=(),
        combat="No specific combat.",
        source=(
            f"{COOKS_ASSISTANT_SOURCE_PATH}; {COOKS_ASSISTANT_LUMBRIDGE_COOK_SOURCE}; "
            f"{COOKS_ASSISTANT_PRIZED_DAIRY_COW_SOURCE}; {COOKS_ASSISTANT_MILLIE_MILLER_SOURCE}; "
            f"{COOKS_ASSISTANT_FLOUR_BIN_SOURCE}"
        ),
        journal_stages=COOKS_ASSISTANT_STAGES,
        release_date="2001-01-04",
        members=False,
        difficulty="Novice",
        length="Short",
        timeline="Fifth Age",
        xp_rewards=(QuestXpReward("cooking", 300),),
        unlocks=("Access to the Cook's range",),
    ),
    QuestDefinition(
        id=SHIELD_OF_ARRAV_ID,
        display_name="Shield of Arrav",
        stages=12,
        point_reward=1,
        rewards=(("Coins", 600),),
        start_point="Talk to Reldo in the Varrock palace library.",
        requirements=(
            "Used during quest: Coins x20; your route contact supplies the opposite certificate half.",
            f"Route choice: {SHIELD_ROUTE_PHOENIX} or {SHIELD_ROUTE_BLACK_ARM}.",
            "Black Arm route uses a contextual Phoenix contact for the weapon store.",
        ),
        required_items=(),
        combat=(
            "Phoenix route: Jonny the beard (level 2). "
            "Black Arm route: Weaponsmaster (level 23) guards the Phoenix weapon store."
        ),
        source=(
            f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_RELDO_SOURCE}; "
            f"{DARKAN_SHIELD_OF_ARRAV_BARAEK_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_STRAVEN_SOURCE}; "
            f"{DARKAN_SHIELD_OF_ARRAV_KATRINE_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_CURATOR_SOURCE}; "
            f"{DARKAN_SHIELD_OF_ARRAV_KING_SOURCE}; {SCAPE_2011_VARROCK_RELDO_SOURCE}; "
            f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}; {SHIELD_OF_ARRAV_WIKI_SOURCE}"
        ),
        journal_stages=SHIELD_OF_ARRAV_STAGES,
        release_date="2001-01-04",
        members=False,
        difficulty="Novice",
        length="Medium",
        timeline="Fifth Age",
        stage_requirements=SHIELD_OF_ARRAV_STAGE_REQUIREMENTS,
        choices=SHIELD_OF_ARRAV_CHOICES,
    ),
    QuestDefinition(
        id=FIGHT_ARENA_ID,
        display_name="Fight Arena",
        stages=12,
        point_reward=2,
        rewards=(("Coins", 1000),),
        start_point="Talk to Lady Servil north of the Khazard fight arena town, south of Ardougne.",
        requirements=(
            "Used during quest: Coins x5.",
            "The Khazard helmet and armour are borrowed during the quest rather than required to start it.",
        ),
        required_items=(),
        combat=(
            "Mandatory arena fights: Khazard ogre (level 63), Khazard scorpion (level 44), and Bouncer (level 137). "
            "General Khazard is optional after Bouncer."
        ),
        source=(
            f"{DARKAN_FIGHT_ARENA_SOURCE}; {DARKAN_FIGHT_ARENA_CUTSCENE_SOURCE}; "
            f"{DARKAN_FIGHT_ARENA_LADY_SOURCE}; {DARKAN_FIGHT_ARENA_JEREMY_SOURCE}; "
            f"{DARKAN_FIGHT_ARENA_LAZY_GUARD_SOURCE}; {DARKAN_FIGHT_ARENA_ANGOR_SOURCE}; "
            f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}; {FIGHT_ARENA_WIKI_SOURCE}"
        ),
        journal_stages=FIGHT_ARENA_STAGES,
        release_date="2002-07-23",
        members=True,
        difficulty="Experienced",
        length="Short",
        timeline="Fifth Age",
        xp_rewards=(QuestXpReward("attack", 12175), QuestXpReward("thieving", 2175)),
    ),
    QuestDefinition(
        id=WITCHS_HOUSE_ID,
        display_name="Witch's House",
        stages=12,
        point_reward=4,
        rewards=(),
        start_point="Talk to Harvey, the crying boy west of Falador.",
        requirements=(
            "Used during quest: Cheese x1, Leather gloves x1.",
            "The keys, magnet, and ball are found during the quest rather than required to start it.",
        ),
        required_items=(),
        combat=(
            "The Witch's experiment must be defeated through four forms: "
            "Skavid level 19, Spider level 30, Bear level 42, and Wolf level 53."
        ),
        source=(
            f"{WITCHS_HOUSE_SOURCE}; {WITCHS_HOUSE_BOY_SOURCE}; {WITCHS_HOUSE_DIARY_SOURCE}; "
            f"{WITCHS_HOUSE_WITCH_SENTRY_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {WITCHS_HOUSE_WIKI_SOURCE}"
        ),
        journal_stages=WITCHS_HOUSE_STAGES,
        release_date="2002-02-27",
        members=True,
        difficulty="Novice",
        length="Short",
        timeline="Fifth Age",
        xp_rewards=(QuestXpReward("constitution", 6325),),
    ),
    QuestDefinition(
        id=MERLINS_CRYSTAL_ID,
        display_name="Merlin's Crystal",
        stages=8,
        point_reward=6,
        rewards=(),
        start_point="Talk to King Arthur in Camelot.",
        requirements=(
            "Used during quest: Bucket x1, Insect repellent x1, Bucket of wax x1, Black candle x1, "
            "Bread x1, Bat bones x1, Tinderbox x1, Excalibur x1"
        ),
        required_items=(),
        combat="Sir Mordred (level 39) must be defeated; Thrantax is bound through ritual dialogue rather than killed.",
        source=(
            f"{MERLINS_CRYSTAL_SOURCE}; {MERLINS_CRYSTAL_KING_ARTHUR_SOURCE}; "
            f"{MERLINS_CRYSTAL_SIR_GAWAIN_SOURCE}; {MERLINS_CRYSTAL_SIR_LUCAN_SOURCE}; "
            f"{MERLINS_CRYSTAL_SIR_LANCELOT_SOURCE}; {MERLINS_CRYSTAL_KEEP_SOURCE}; "
            f"{MERLINS_CRYSTAL_CRATE_SCENE_SOURCE}; {MERLINS_CRYSTAL_MORDRED_SOURCE}; "
            f"{MERLINS_CRYSTAL_MORGAN_SOURCE}; {MERLINS_CRYSTAL_LADY_SOURCE}; "
            f"{MERLINS_CRYSTAL_BEGGAR_SOURCE}; {MERLINS_CRYSTAL_RITUAL_SCENE_SOURCE}; "
            f"{MERLINS_CRYSTAL_THRANTAX_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {MERLINS_CRYSTAL_WIKI_SOURCE}"
        ),
        journal_stages=MERLINS_CRYSTAL_STAGES,
        release_date="2002-02-27",
        members=True,
        difficulty="Intermediate",
        length="Medium",
        timeline="Fifth Age",
        unlocks=("Excalibur", "Honorary Knight of the Round Table"),
        stage_requirements=MERLINS_CRYSTAL_STAGE_REQUIREMENTS,
    ),
    QuestDefinition(
        id=HEROES_QUEST_ID,
        display_name="Heroes' Quest",
        stages=13,
        point_reward=1,
        rewards=(),
        start_point="Speak with Achietties at the entrance to the Heroes' Guild in Burthorpe.",
        requirements=(
            "56 Quest Points",
            "Shield of Arrav",
            "Lost City",
            "Dragon Slayer",
            "Merlin's Crystal",
            "Druidic Ritual",
            "Cooking 53",
            "Fishing 53",
            "Herblore 25",
            "Defence 25",
            "Mining 50",
            (
                "Used during quest: Harralander potion (unf) x1, Fishing rod x1, Fishing bait x1, "
                "Pickaxe x1."
            ),
            (
                "Route choice: Phoenix Gang or Black Arm Gang from Shield of Arrav. "
                "Black Arm route uses black armour and Id papers; Phoenix route uses the secret panel and a "
                "contextual Black Arm Gang partner for the key, Grip lure, and candlestick handoff."
            ),
        ),
        required_items=(),
        combat=(
            "Ice Queen (level 111) for Ice gloves; Entranan Firebird (level 2) for Fire feather; "
            "Phoenix route: Grip (level 22). Ice Queen lair access may require the Dusty key route or an alternate shortcut."
        ),
        source=(
            f"{HEROES_QUEST_DARKAN_SOURCE}; {HEROES_QUEST_ACHIETTIES_SOURCE}; "
            f"{HEROES_QUEST_PORT_SARIM_SOURCE}; {HEROES_QUEST_HERBLORE_SOURCE}; "
            f"{HEROES_QUEST_FISH_SOURCE}; {HEROES_QUEST_FISHING_SPOT_SOURCE}; {HEROES_QUEST_COOKING_SOURCE}; "
            f"{HEROES_QUEST_ICE_QUEEN_DUNGEON_SOURCE}; {HEROES_QUEST_BRIMHAVEN_SOURCE}; "
            f"{HEROES_QUEST_KATRINE_SOURCE}; {HEROES_QUEST_STRAVEN_SOURCE}; {HEROES_QUEST_TROBERT_SOURCE}; "
            f"{HEROES_QUEST_ALFONSO_SOURCE}; {HEROES_QUEST_CHARLIE_SOURCE}; {HEROES_QUEST_MANSION_DOOR_SOURCE}; "
            f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}; {HEROES_QUEST_WIKI_SOURCE}"
        ),
        journal_stages=HEROES_QUEST_STAGES,
        release_date="2002-02-27",
        members=True,
        difficulty="Experienced",
        length="Medium to Long",
        timeline="Fifth Age",
        required_quest_points=56,
        required_quests=(
            QuestPrerequisite(SHIELD_OF_ARRAV_ID, "Shield of Arrav"),
            QuestPrerequisite(LOST_CITY_ID, "Lost City"),
            QuestPrerequisite(DRAGON_SLAYER_ID, "Dragon Slayer"),
            QuestPrerequisite(MERLINS_CRYSTAL_ID, "Merlin's Crystal"),
            QuestPrerequisite(DRUIDIC_RITUAL_ID, "Druidic Ritual"),
        ),
        required_skills=(
            QuestSkillRequirement("cooking", "Cooking", 53),
            QuestSkillRequirement("fishing", "Fishing", 53),
            QuestSkillRequirement("herblore", "Herblore", 25),
            QuestSkillRequirement("defense", "Defence", 25),
            QuestSkillRequirement("mining", "Mining", 50),
        ),
        xp_rewards=(
            QuestXpReward("attack", 3075),
            QuestXpReward("defense", 3075),
            QuestXpReward("strength", 3075),
            QuestXpReward("constitution", 3075),
            QuestXpReward("ranged", 2075),
            QuestXpReward("fishing", 2725),
            QuestXpReward("cooking", 2825),
            QuestXpReward("woodcutting", 1575),
            QuestXpReward("firemaking", 1575),
            QuestXpReward("smithing", 2257),
            QuestXpReward("mining", 2575),
            QuestXpReward("herblore", 1325),
        ),
        unlocks=(
            "Access to the Heroes' Guild",
            "Access to another Black Arm Gang hideout in Brimhaven if you are in the Black Arm Gang",
            "Access to the garden beside Scarface Pete's house if you are in the Phoenix Gang",
            "Ability to wield and buy Dragon battleaxe and Dragon mace from the Heroes' Guild weapon shop",
        ),
        stage_requirements=HEROES_QUEST_STAGE_REQUIREMENTS,
        choices=HEROES_QUEST_CHOICES,
    ),
    QuestDefinition(
        id=FAMILY_CREST_ID,
        display_name="Family Crest",
        stages=16,
        point_reward=1,
        rewards=(("Family gauntlets", 1),),
        start_point="Talk to Dimintheis in south-east Varrock, next to the Fancy Dress Shop.",
        requirements=(
            "Crafting 40",
            "Magic 59",
            "Mining 40",
            "Smithing 40",
            (
                "Used during quest: Shrimps x1, Salmon x1, Tuna x1, Bass x1, Swordfish x1, "
                "Ruby x2, Antipoison x1, Ring mould x1, Necklace mould x1, Pickaxe x1."
            ),
            (
                "Quest-made items: Caleb crest, Perfect gold ore, Perfect gold bar, Perfect ruby ring, "
                "Perfect ruby necklace, Avan crest, Johnathon crest, and Family crest."
            ),
        ),
        required_items=(),
        combat=(
            "Chronozon (level 170) must be weakened with Air, Water, Earth, and Fire Blast before defeat. "
            "The local quest handler text also says level 84, but the NPC list/combatdef row is level 170."
        ),
        source=(
            f"{FAMILY_CREST_DARKAN_SOURCE}; {FAMILY_CREST_DIMINTHEIS_SOURCE}; {FAMILY_CREST_CALEB_SOURCE}; "
            f"{FAMILY_CREST_GEM_TRADER_SOURCE}; {FAMILY_CREST_AVAN_SOURCE}; {FAMILY_CREST_BOOT_SOURCE}; "
            f"{FAMILY_CREST_JOHNATHON_SOURCE}; {FAMILY_CREST_CHRONOZON_SOURCE}; "
            f"{FAMILY_CREST_WITCHHAVEN_PUZZLE_SOURCE}; {FAMILY_CREST_CHRONOZON_NPC_SOURCE}; "
            f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}; {FAMILY_CREST_WIKI_SOURCE}"
        ),
        journal_stages=FAMILY_CREST_STAGES,
        release_date="2002-04-09",
        members=True,
        difficulty="Experienced",
        length="Medium",
        timeline="Fifth Age",
        required_skills=(
            QuestSkillRequirement("crafting", "Crafting", 40),
            QuestSkillRequirement("magic", "Magic", 59),
            QuestSkillRequirement("mining", "Mining", 40),
            QuestSkillRequirement("smithing", "Smithing", 40),
        ),
        unlocks=(
            "Access to the hellhounds in Witchaven Dungeon",
            "Ability to convert Family gauntlets into Cooking, Goldsmith, or Chaos gauntlets",
        ),
        stage_requirements=FAMILY_CREST_STAGE_REQUIREMENTS,
    ),
    QuestDefinition(
        id=TEMPLE_OF_IKOV_ID,
        display_name="Temple of Ikov",
        stages=11,
        point_reward=1,
        rewards=(("Shiny key", 1),),
        start_point="Talk to Lucien at the Flying Horse Inn in north-west East Ardougne.",
        requirements=(
            "Thieving 42",
            (
                "Used during quest: Knife x1, Limpwurt root x20, one yew, magic, or dark bow "
                "compatible with ice arrows; bring any valid lit source."
            ),
            (
                "Quest-made items: Pendant of lucien, Boots of lightness, Lever, Ice arrows, "
                "Armadyl pendant, and Staff of armadyl."
            ),
            f"Route choice: {TEMPLE_OF_IKOV_ROUTE_GUARDIANS} or {TEMPLE_OF_IKOV_ROUTE_LUCIEN}.",
        ),
        required_items=(),
        combat=(
            "Fire Warrior of Lesarkus (level 84) must be defeated with ice arrows and a suitable bow. "
            "Guardian route: Lucien (level 14). Lucien route: a blocking Guardian of Armadyl (level 45)."
        ),
        source=(
            f"{TEMPLE_OF_IKOV_DARKAN_SOURCE}; {TEMPLE_OF_IKOV_DUNGEON_SOURCE}; "
            f"{TEMPLE_OF_IKOV_FIRE_WARRIOR_SOURCE}; {TEMPLE_OF_IKOV_LUCIEN_MOB_SOURCE}; "
            f"{TEMPLE_OF_IKOV_LUCIEN_ARDOUGNE_SOURCE}; {TEMPLE_OF_IKOV_LUCIEN_VARROCK_SOURCE}; "
            f"{TEMPLE_OF_IKOV_GUARDIAN_SOURCE}; {TEMPLE_OF_IKOV_WINELDA_SOURCE}; "
            f"{TEMPLE_OF_IKOV_FIRE_WARRIOR_NPC_SOURCE}; {TEMPLE_OF_IKOV_GUARDIAN_NPC_SOURCE}; "
            f"{TEMPLE_OF_IKOV_LUCIEN_NPC_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {TEMPLE_OF_IKOV_WIKI_SOURCE}"
        ),
        journal_stages=TEMPLE_OF_IKOV_STAGES,
        release_date="2002-06-05",
        members=True,
        difficulty="Intermediate",
        length="Medium",
        timeline="Fifth Age",
        required_skills=(QuestSkillRequirement("thieving", "Thieving", 42),),
        xp_rewards=(QuestXpReward("ranged", 10500), QuestXpReward("fletching", 8000)),
        unlocks=(
            "Access to the Temple of Ikov",
            "Ability to use the Boots of lightness found during the quest",
        ),
        stage_requirements=TEMPLE_OF_IKOV_STAGE_REQUIREMENTS,
        start_inventory=(("Pendant of lucien", 1),),
        choices=TEMPLE_OF_IKOV_CHOICES,
    ),
    QuestDefinition(
        id=DEMON_SLAYER_ID,
        display_name="Demon Slayer",
        stages=9,
        point_reward=3,
        rewards=(),
        start_point="Speak to Gypsy Aris in the tent on the western side of Varrock Square.",
        requirements=(
            "Used during quest: Coins x1, Bucket of water x1, Bones x25",
            "Silverlight must be obtained before fighting Delrith.",
        ),
        required_items=(),
        combat="Delrith (level 27) is fought with Silverlight at the Dark Wizards' altar.",
        source=(
            f"{DARKAN_DEMON_SLAYER_SOURCE}; {DARKAN_DEMON_SLAYER_GYPSY_SOURCE}; "
            f"{DARKAN_DEMON_SLAYER_SIR_PRYSIN_SOURCE}; {DARKAN_DEMON_SLAYER_TRAIBORN_SOURCE}; "
            f"{DARKAN_DEMON_SLAYER_ROVIN_SOURCE}; {DARKAN_DEMON_SLAYER_DELRITH_SOURCE}; "
            f"{DARKAN_DEMON_SLAYER_DELRITH_CONTROLLER_SOURCE}; {DARKAN_DEMON_SLAYER_INCANTATION_SOURCE}; "
            f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}; {DARKAN_DEMON_SLAYER_DELRITH_NPC_SOURCE}; {DEMON_SLAYER_WIKI_SOURCE}"
        ),
        journal_stages=DEMON_SLAYER_STAGES,
        release_date="2001-01-04",
        members=False,
        difficulty="Novice",
        length="Short to Medium",
        timeline="Fifth Age",
        unlocks=("Silverlight",),
    ),
    QuestDefinition(
        id=DRAGON_SLAYER_ID,
        display_name="Dragon Slayer",
        stages=16,
        point_reward=2,
        rewards=(),
        start_point="Speak to the Guildmaster inside the Champions' Guild, south of Varrock.",
        requirements=(
            "32 Quest Points",
            (
                "Used during quest: Wizard's mind bomb x1, Silk x1, Bowl (unfired) x1, Crayfish cage or Lobster pot x1, "
                "Coins x12000, Plank x3, Steel nails x90, Hammer x1"
            ),
        ),
        required_items=(),
        combat=(
            "Melzar's Maze requires key-carrying lesser foes, Melzar the Mad, and a lesser demon; "
            "Elvarg (level 83) must be defeated with anti-dragon shield protection. "
            "Wormbrain can be killed for a map piece, but the modeled deterministic route buys it for 10,000 coins."
        ),
        source=(
            f"{DARKAN_DRAGON_SLAYER_SOURCE}; {DARKAN_DRAGON_SLAYER_GUILDMASTER_SOURCE}; "
            f"{DARKAN_DRAGON_SLAYER_OZIACH_SOURCE}; {DARKAN_DRAGON_SLAYER_MELZARS_MAZE_SOURCE}; "
            f"{DARKAN_DRAGON_SLAYER_WORMBRAIN_SOURCE}; {DARKAN_DRAGON_SLAYER_KLARENSE_SOURCE}; "
            f"{DARKAN_DRAGON_SLAYER_NED_SOURCE}; {DARKAN_DRAGON_SLAYER_CAPTAIN_NED_SOURCE}; "
            f"{DARKAN_DRAGON_SLAYER_ELVARG_SOURCE}; {RUNE_MYSTERIES_DUKE_SOURCE_PATH}; "
            f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}; {DRAGON_SLAYER_WIKI_SOURCE}"
        ),
        journal_stages=DRAGON_SLAYER_STAGES,
        release_date="2001-09-23",
        members=False,
        difficulty="Experienced",
        length="Long",
        timeline="Fifth Age",
        required_quest_points=32,
        xp_rewards=(QuestXpReward("defense", 18650), QuestXpReward("strength", 18650)),
        unlocks=(
            "The ability to equip a rune platebody and a green dragonhide body.",
            "Access to all of Crandor Island",
            "Access to Melzar's Maze",
            "Access to the dragon crest on herald capes",
        ),
    ),
    QuestDefinition(
        id=ERNEST_THE_CHICKEN_ID,
        display_name="Ernest the Chicken",
        stages=9,
        point_reward=4,
        rewards=(("Coins", 3000), ("Egg", 10), ("Feather", 300)),
        start_point="Talk to Veronica south of Draynor Manor's gates.",
        requirements=(
            "Used during quest: Fish food x1, Poison x1, Spade x1",
        ),
        required_items=(),
        combat="None required; dangerous manor enemies are avoidable.",
        source=f"{DARKAN_ERNEST_SOURCE}; {DARKAN_ERNEST_ODDENSTEIN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        journal_stages=ERNEST_THE_CHICKEN_STAGES,
        release_date="2001-01-21",
        members=False,
        difficulty="Novice",
        length="Medium",
        timeline="Fifth Age",
    ),
    QuestDefinition(
        id=BLACK_KNIGHTS_FORTRESS_ID,
        display_name="Black Knights' Fortress",
        stages=5,
        point_reward=3,
        rewards=(("Coins", 2500),),
        start_point="Speak to Sir Amik Varze on the 3rd floor of the White Knights' Castle's western tower.",
        requirements=("12 Quest Points", "Used during quest: Iron chainbody x1, Bronze med helm x1, Cabbage x1"),
        required_items=(),
        combat="Ability to evade level 33 Black Knights; no required kill.",
        source=f"{DARKAN_BLACK_KNIGHTS_SOURCE}; {DARKAN_BLACK_KNIGHTS_SIR_AMIK_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        journal_stages=BLACK_KNIGHTS_FORTRESS_STAGES,
        release_date="2001-04-06",
        members=False,
        difficulty="Novice",
        length="Short",
        timeline="Fifth Age",
        required_quest_points=12,
    ),
    QuestDefinition(
        id=GOBLIN_DIPLOMACY_ID,
        display_name="Goblin Diplomacy",
        stages=4,
        point_reward=5,
        rewards=(("Gold bar", 1),),
        start_point="Talk to General Bentnoze or General Wartface in Goblin Village.",
        requirements=("Used during quest: Orange goblin mail x1, Blue goblin mail x1, Goblin mail x1",),
        required_items=(),
        combat="None.",
        source=f"{DARKAN_GOBLIN_DIPLOMACY_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        journal_stages=GOBLIN_DIPLOMACY_STAGES,
        release_date="2001-05-08",
        members=False,
        difficulty="Novice",
        length="Short to Medium",
        timeline="Fifth Age",
        xp_rewards=(QuestXpReward("crafting", 200),),
    ),
    QuestDefinition(
        id=VAMPYRE_SLAYER_ID,
        display_name="Vampyre Slayer",
        stages=5,
        point_reward=3,
        rewards=(),
        start_point="Speak to Morgan in Draynor Village.",
        requirements=(),
        required_items=(),
        combat="Count Draynor (level 37); garlic is optional and weakens him.",
        source=(
            f"{VAMPYRE_SLAYER_SOURCE_PATH}; {VAMPYRE_SLAYER_MORGAN_SOURCE_PATH}; "
            f"{VAMPYRE_SLAYER_DR_HARLOW_SOURCE_PATH}; {VAMPYRE_SLAYER_MANOR_SOURCE_PATH}; "
            f"{COUNT_DRAYNOR_NPC_SOURCE_PATH}"
        ),
        journal_stages=VAMPYRE_SLAYER_STAGES,
        release_date="2001-01-28",
        members=False,
        difficulty="Novice",
        length="Short",
        timeline="Fifth Age",
        xp_rewards=(QuestXpReward("attack", 4825),),
    ),
    QuestDefinition(
        id=THE_RESTLESS_GHOST_ID,
        display_name="The Restless Ghost",
        stages=5,
        point_reward=1,
        rewards=(("Ancient bones", 5),),
        start_point="Speak to Father Aereck in the chapel south-east of Lumbridge Castle.",
        requirements=(),
        required_items=(),
        combat="Skeleton warlock (level 11) after taking the ghost's skull.",
        source=(
            f"{RESTLESS_GHOST_SOURCE_PATH}; {RESTLESS_GHOST_FATHER_URHNEY_SOURCE_PATH}; "
            f"{RESTLESS_GHOST_DIALOGUE_SOURCE_PATH}; {RESTLESS_GHOST_SKULL_SOURCE_PATH}; "
            f"{RESTLESS_GHOST_COFFIN_SOURCE_PATH}; {RESTLESS_GHOST_SKELETON_WARLOCK_NPC_SOURCE_PATH}"
        ),
        journal_stages=RESTLESS_GHOST_STAGES,
        release_date="2001-01-04",
        members=False,
        difficulty="Novice",
        length="Short",
        timeline="Fifth Age",
        xp_rewards=(QuestXpReward("prayer", 125),),
    ),
    QuestDefinition(
        id=IMP_CATCHER_ID,
        display_name="Imp Catcher",
        stages=2,
        point_reward=1,
        rewards=(("Amulet of accuracy", 1),),
        start_point="Talk to Wizard Mizgog in the Wizards' Tower.",
        requirements=("Used during quest: Black bead x1, Red bead x1, White bead x1, Yellow bead x1",),
        required_items=(),
        combat="Imps can drop the beads, but the quest completion gate is the four beads.",
        source=f"{IMP_CATCHER_SOURCE_PATH}; {IMP_CATCHER_MIZGOG_SOURCE_PATH}",
        journal_stages=IMP_CATCHER_STAGES,
        release_date="2001-02-16",
        members=False,
        difficulty="Novice",
        length="Short",
        timeline="Fifth Age",
        xp_rewards=(QuestXpReward("magic", 875),),
    ),
    QuestDefinition(
        id=PIRATES_TREASURE_ID,
        display_name="Pirate's Treasure",
        stages=4,
        point_reward=2,
        rewards=(("Casket (Pirate's Treasure)", 1),),
        start_point="Talk to Redbeard Frank just south of The Rusty Anchor pub in Port Sarim.",
        requirements=("Used during quest: Karamja rum x1, Spade x1",),
        required_items=(),
        combat="Optional level 4 gardener near the digging spot.",
        source=f"{PIRATES_TREASURE_SOURCE_PATH}; {PIRATES_TREASURE_REDBEARD_SOURCE_PATH}; {PIRATES_TREASURE_CHEST_SOURCE_PATH}",
        journal_stages=PIRATES_TREASURE_STAGES,
        release_date="2001-06-11",
        members=False,
        difficulty="Novice",
        length="Short to Medium",
        timeline="Fifth Age",
    ),
    QuestDefinition(
        id=JUNGLE_POTION_ID,
        display_name="Jungle Potion",
        stages=len(JUNGLE_POTION_STAGES),
        point_reward=1,
        rewards=(),
        start_point="Speak to Trufitus near Tai Bwo Wannai.",
        requirements=(
            "Druidic Ritual",
            "Herblore 3",
            "Used during quest: the five jungle herbs found and cleaned in strict order",
        ),
        required_items=(),
        combat="None required; the jungle contains environmental dangers.",
        source=(
            f"{DARKAN_JUNGLE_POTION_SOURCE}; {DARKAN_JUNGLE_POTION_TRUFITUS_SOURCE}; "
            f"{DARKAN_HERB_CLEANING_SOURCE_PATH}; {JUNGLE_POTION_CACHE_SOURCE}; "
            f"{JUNGLE_POTION_WIKI_SOURCE}"
        ),
        journal_stages=JUNGLE_POTION_STAGES,
        release_date="2002-10-23",
        members=True,
        difficulty="Novice",
        length="Short to Medium",
        timeline="Fifth Age",
        required_quests=(QuestPrerequisite(DRUIDIC_RITUAL_ID, "Druidic Ritual"),),
        required_skills=(QuestSkillRequirement("herblore", "Herblore", 3),),
        xp_rewards=(QuestXpReward("herblore", 775),),
        unlocks=(
            "Access to Tai Bwo Wannai Cleanup",
            "Access to Rionasta's parcel service",
            "Access to the Calquat gardener",
            "Eligibility to start Shilo Village",
        ),
    ),
    QuestDefinition(
        id=SHILO_VILLAGE_ID,
        display_name="Shilo Village",
        stages=len(SHILO_VILLAGE_STAGES),
        point_reward=2,
        rewards=(),
        start_point="Talk to Mosol Rei outside Shilo Village in southern Karamja.",
        requirements=(
            "Jungle Potion",
            "Smithing 4",
            "Crafting 20",
            "Agility 32",
            "Used during quest: Rope x1, lit light source x1, Spade x1, Chisel x1, Bronze wire x1, Bones x3",
        ),
        required_items=(),
        combat="Nazastarool: level 91 Zombie, level 68 Skeleton, then level 93 Ghost.",
        source=(
            f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}; "
            f"{SHILO_VILLAGE_MOSOL_SOURCE}; {SHILO_VILLAGE_TRUFITUS_SOURCE}; "
            f"{SHILO_VILLAGE_CACHE_SOURCE}"
        ),
        journal_stages=SHILO_VILLAGE_STAGES,
        release_date="2003-01-27",
        members=True,
        difficulty="Experienced",
        length="Long",
        timeline="Fifth Age",
        required_quests=(QuestPrerequisite(JUNGLE_POTION_ID, "Jungle Potion"),),
        required_skills=(
            QuestSkillRequirement("smithing", "Smithing", 4),
            QuestSkillRequirement("crafting", "Crafting", 20),
            QuestSkillRequirement("agility", "Agility", 32),
        ),
        xp_rewards=(QuestXpReward("crafting", 3875),),
        unlocks=(
            "Access to Shilo Village",
            "Access to Shilo Village gem rocks",
            "Access to the Shilo Village cart service",
        ),
        start_inventory=(("Wampum belt", 1),),
    ),
    QuestDefinition(
        id=LOST_CITY_ID,
        display_name="Lost City",
        stages=6,
        point_reward=3,
        rewards=(),
        start_point="Talk to the warrior adventurer in Lumbridge Swamp.",
        requirements=("Crafting 31", "Woodcutting 36", "Used during quest: Hatchet x1, Knife x1"),
        required_items=(),
        combat="Must be able to kill a level 63 Tree spirit.",
        source=(
            f"{LOST_CITY_SOURCE_PATH}; {LOST_CITY_WARRIOR_SOURCE_PATH}; {LOST_CITY_TREE_SOURCE_PATH}; "
            f"{LOST_CITY_SHAMUS_SOURCE_PATH}; {LOST_CITY_ENTRANA_SOURCE_PATH}; {LOST_CITY_SHED_SOURCE_PATH}; "
            f"{LOST_CITY_TREE_SPIRIT_NPC_SOURCE_PATH}"
        ),
        journal_stages=LOST_CITY_STAGES,
        release_date="2002-02-27",
        members=True,
        difficulty="Experienced",
        length="Medium",
        timeline="Fifth Age",
        required_skills=(
            QuestSkillRequirement("crafting", "Crafting", 31),
            QuestSkillRequirement("woodcutting", "Woodcutting", 36),
        ),
        unlocks=("Access to Zanaris", "Ability to craft cosmic runes"),
    ),
    QuestDefinition(
        id=DRUIDIC_RITUAL_ID,
        display_name="Druidic Ritual",
        stages=4,
        point_reward=4,
        rewards=(),
        start_point="Speak to Kaqemeex at the stone circle north of Taverley.",
        requirements=(
            "Used during quest: Raw bear meat x1, Raw rat meat x1, Raw beef x1, Raw chicken x1",
            "Access to the Cauldron of Thunder dungeon south of Taverley",
        ),
        required_items=(),
        combat="None.",
        source=(
            f"{DRUIDIC_RITUAL_SOURCE_PATH}; {DRUIDIC_RITUAL_SANFEW_SOURCE_PATH}; "
            f"{DRUIDIC_RITUAL_CAULDRON_SOURCE_PATH}; {DRUIDIC_RITUAL_KAQEMEEX_SOURCE_PATH}"
        ),
        journal_stages=DRUIDIC_RITUAL_STAGES,
        release_date="2002-02-27",
        members=True,
        difficulty="Novice",
        length="Short",
        timeline="Fifth Age",
        xp_rewards=(QuestXpReward("herblore", 250),),
        unlocks=("Access to Herblore",),
    ),
    QuestDefinition(
        id=RUNE_MYSTERIES_ID,
        display_name="Rune Mysteries",
        stages=6,
        point_reward=1,
        rewards=(("Air talisman", 1),),
        start_point="Speak to Duke Horacio, upstairs in Lumbridge Castle.",
        requirements=(),
        required_items=(),
        combat="None.",
        source=(
            f"{RUNEMYSTERIES_SOURCE_PATH}; {RUNE_MYSTERIES_DUKE_SOURCE_PATH}; "
            f"{RUNE_MYSTERIES_SEDRIDOR_SOURCE_PATH}; {RUNE_MYSTERIES_AUBURY_SOURCE_PATH}"
        ),
        journal_stages=RUNE_MYSTERIES_STAGES,
        release_date="2003-12-01",
        members=False,
        difficulty="Novice",
        length="Short",
        timeline="Fifth Age",
        start_inventory=(("Air talisman", 1),),
        unlocks=("Ability to craft runes", "Ability to mine rune essence"),
    ),
    QuestDefinition(
        id=THE_KNIGHTS_SWORD_ID,
        display_name="The Knight's Sword",
        stages=7,
        point_reward=1,
        rewards=(),
        start_point="Speak to the Squire in the courtyard of the White Knights' Castle in southern Falador.",
        requirements=("Mining 10", "Used during quest: Redberry pie x1, Blurite ore x1, Iron bar x2"),
        required_items=(),
        combat="Ability to evade level 54 Ice Warriors and level 53 Ice Giants.",
        source=f"{KNIGHTS_SWORD_QUEST_SOURCE_PATH}; {KNIGHTS_SWORD_SQUIRE_SOURCE_PATH}; {KNIGHTS_SWORD_THURGO_SOURCE_PATH}",
        journal_stages=KNIGHTS_SWORD_STAGES,
        release_date="2001-04-06",
        members=False,
        difficulty="Intermediate",
        length="Medium",
        timeline="Fifth Age",
        required_skills=(QuestSkillRequirement("mining", "Mining", 10),),
        xp_rewards=(QuestXpReward("smithing", 12725),),
        stage_requirements=KNIGHTS_SWORD_STAGE_REQUIREMENTS,
    ),
    QuestDefinition(
        id=PRIEST_IN_PERIL_ID,
        display_name="Priest in Peril",
        stages=9,
        point_reward=1,
        rewards=(("Wolfbane dagger", 1),),
        start_point="Speak to King Roald in the Varrock Palace.",
        requirements=("Used during quest: Bucket x1, Rune essence x50 or Pure essence x25",),
        required_items=(),
        combat="Temple guardian dog (level 30, Magic cannot damage it); Monk of Zamorak (level 30) for the key.",
        source=(
            f"{PRIEST_IN_PERIL_QUEST_SOURCE_PATH}; {PRIEST_IN_PERIL_DARKAN_SOURCE}; "
            f"{PRIEST_IN_PERIL_DARKAN_CERBERUS_SOURCE}; {PRIEST_IN_PERIL_SOURCE}"
        ),
        journal_stages=PRIEST_IN_PERIL_STAGES,
        release_date="2004-06-29",
        members=True,
        difficulty="Novice",
        length="Medium",
        timeline="Fifth Age",
        xp_rewards=(QuestXpReward("prayer", 1406),),
        unlocks=("Access to Morytania",),
    ),
    QuestDefinition(
        id=TAI_BWO_WANNAI_TRIO_ID,
        display_name="Tai Bwo Wannai Trio",
        stages=6,
        point_reward=2,
        rewards=(("Coins", 2000), ("Rune spear (kp)", 1)),
        start_point="Speak to Timfraku in Tai Bwo Wannai Village.",
        requirements=("Jungle Potion", "Agility 15", "Cooking 30", "Fishing 5"),
        required_items=(),
        combat="Must be able to defeat level 48 jogres.",
        source=TAI_BWO_WANNAI_TRIO_SOURCE,
        journal_stages=TAI_BWO_WANNAI_TRIO_STAGES,
        release_date="2004-09-14",
        members=True,
        difficulty="Intermediate",
        length="Long",
        timeline="Fifth Age",
        required_quests=(QuestPrerequisite(JUNGLE_POTION_ID, "Jungle Potion"),),
        required_skills=(
            QuestSkillRequirement("agility", "Agility", 15),
            QuestSkillRequirement("cooking", "Cooking", 30),
            QuestSkillRequirement("fishing", "Fishing", 5),
        ),
        xp_rewards=(
            QuestXpReward("cooking", 5000),
            QuestXpReward("fishing", 5000),
            QuestXpReward("attack", 2500),
            QuestXpReward("strength", 2500),
        ),
        unlocks=("Ability to catch karambwanji and karambwan",),
    ),
    QuestDefinition(
        id=MOURNINGS_END_PART_II_ID,
        display_name="Mourning's End Part II",
        stages=7,
        point_reward=2,
        rewards=(("Death talisman", 1),),
        start_point="Speak to the head mourner in West Ardougne.",
        requirements=("Mourning's End Part I",),
        required_items=(),
        combat="No direct boss fight; the Temple of Light is dangerous.",
        source=MOURNINGS_END_PART_II_SOURCE,
        journal_stages=MOURNINGS_END_PART_II_STAGES,
        release_date="2005-10-17",
        members=True,
        difficulty="Master",
        length="Long",
        timeline="Fifth Age",
        required_quests=(QuestPrerequisite(MOURNINGS_END_PART_I_ID, "Mourning's End Part I"),),
        xp_rewards=(QuestXpReward("agility", 20000),),
        unlocks=("Access to the Death Altar",),
    ),
    QuestDefinition(
        id=SWAN_SONG_ID,
        display_name="Swan Song",
        stages=6,
        point_reward=2,
        rewards=(("Coins", 25000),),
        start_point="Speak to Herman Caranos at the Piscatoris Fishing Colony.",
        requirements=(
            "One Small Favour",
            "Garden of Tranquillity",
            "101 Quest Points",
            "Magic 66",
            "Cooking 62",
            "Fishing 62",
            "Smithing 45",
            "Firemaking 42",
            "Crafting 40",
        ),
        required_items=(),
        combat="Must be able to fight a powerful level 170 monster.",
        source=SWAN_SONG_SOURCE,
        journal_stages=SWAN_SONG_STAGES,
        release_date="2006-05-02",
        members=True,
        difficulty="Master",
        length="Medium",
        timeline="Fifth Age",
        required_quests=(
            QuestPrerequisite(ONE_SMALL_FAVOUR_ID, "One Small Favour"),
            QuestPrerequisite(GARDEN_OF_TRANQUILLITY_ID, "Garden of Tranquillity"),
        ),
        required_skills=(
            QuestSkillRequirement("magic", "Magic", 66),
            QuestSkillRequirement("cooking", "Cooking", 62),
            QuestSkillRequirement("fishing", "Fishing", 62),
            QuestSkillRequirement("smithing", "Smithing", 45),
            QuestSkillRequirement("firemaking", "Firemaking", 42),
            QuestSkillRequirement("crafting", "Crafting", 40),
        ),
        required_quest_points=101,
        xp_rewards=(
            QuestXpReward("magic", 15000),
            QuestXpReward("fishing", 10000),
            QuestXpReward("prayer", 10000),
        ),
        unlocks=("Access to the Piscatoris Fishing Colony", "Ability to fish monkfish"),
    ),
    QuestDefinition(
        id=LUNAR_DIPLOMACY_ID,
        display_name="Lunar Diplomacy",
        stages=8,
        point_reward=2,
        rewards=(("Astral rune", 50),),
        start_point="Talk to Lokar Searunner at the docks of Rellekka.",
        requirements=(
            "The Fremennik Trials",
            "Lost City",
            "Rune Mysteries",
            "Shilo Village",
            "Crafting 61",
            "Defence 40",
            "Firemaking 49",
            "Herblore 5",
            "Magic 65",
            "Mining 60",
            "Woodcutting 55",
        ),
        required_items=(),
        combat="Must be able to defeat Suqahs and the player's dream self.",
        source=LUNAR_DIPLOMACY_SOURCE,
        journal_stages=LUNAR_DIPLOMACY_STAGES,
        release_date="2006-07-24",
        members=True,
        difficulty="Experienced",
        length="Long",
        timeline="Fifth Age",
        required_quests=(
            QuestPrerequisite(THE_FREMENNIK_TRIALS_ID, "The Fremennik Trials"),
            QuestPrerequisite(LOST_CITY_ID, "Lost City"),
            QuestPrerequisite(RUNE_MYSTERIES_ID, "Rune Mysteries"),
            QuestPrerequisite(SHILO_VILLAGE_ID, "Shilo Village"),
        ),
        required_skills=(
            QuestSkillRequirement("crafting", "Crafting", 61),
            QuestSkillRequirement("defense", "Defence", 40),
            QuestSkillRequirement("firemaking", "Firemaking", 49),
            QuestSkillRequirement("herblore", "Herblore", 5),
            QuestSkillRequirement("magic", "Magic", 65),
            QuestSkillRequirement("mining", "Mining", 60),
            QuestSkillRequirement("woodcutting", "Woodcutting", 55),
        ),
        xp_rewards=(QuestXpReward("magic", 5000), QuestXpReward("runecrafting", 5000)),
        unlocks=("Access to the Lunar Spellbook", "Access to the Astral Altar"),
    ),
    QuestDefinition(
        id=LEGACY_OF_SEERGAZE_ID,
        display_name="Legacy of Seergaze",
        stages=7,
        point_reward=2,
        rewards=(("Blood talisman", 1), ("Ivandis flail", 1), ("Tome of Experience, 2nd Ed.", 1)),
        start_point="Talk to the Mercenary Adventurer at the Burgh de Rott Ramble start point east of Paterdomus.",
        requirements=(
            "Darkness of Hallowvale",
            "Construction 20",
            "Agility 29",
            "Slayer 31",
            "Mining 35",
            "Firemaking 40",
            "Crafting 47",
            "Magic 49",
        ),
        required_items=(),
        combat="Two different combat styles are useful against level 80 guards and Vyrewatch.",
        source=LEGACY_OF_SEERGAZE_SOURCE,
        journal_stages=LEGACY_OF_SEERGAZE_STAGES,
        release_date="2008-04-22",
        members=True,
        difficulty="Experienced",
        length="Long",
        timeline="Fifth Age",
        required_quests=(QuestPrerequisite(DARKNESS_OF_HALLOWVALE_ID, "Darkness of Hallowvale"),),
        required_skills=(
            QuestSkillRequirement("construction", "Construction", 20),
            QuestSkillRequirement("agility", "Agility", 29),
            QuestSkillRequirement("slayer", "Slayer", 31),
            QuestSkillRequirement("mining", "Mining", 35),
            QuestSkillRequirement("firemaking", "Firemaking", 40),
            QuestSkillRequirement("crafting", "Crafting", 47),
            QuestSkillRequirement("magic", "Magic", 49),
        ),
        xp_rewards=(
            QuestXpReward("agility", 2000),
            QuestXpReward("construction", 1000),
            QuestXpReward("crafting", 4000),
            QuestXpReward("magic", 3000),
            QuestXpReward("mining", 2000),
            QuestXpReward("slayer", 2000),
        ),
        unlocks=("Access to the Blood Altar", "Paterdomus Columbarium rewards"),
    ),
)
QUEST_OVERRIDES_BY_ID: Dict[str, QuestDefinition] = {quest.id: quest for quest in QUEST_OVERRIDES}


def _stage_req(
    stage: int,
    description: str,
    source: str,
    *,
    variant: str = "",
    required_inventory: Tuple[Tuple[str, int], ...] = (),
    required_inventory_options: Tuple[Tuple[Tuple[str, int], ...], ...] = (),
    consumed_inventory: Tuple[Tuple[str, int], ...] = (),
    consumed_inventory_options: Tuple[Tuple[Tuple[str, int], ...], ...] = (),
    produced_inventory: Tuple[Tuple[str, int], ...] = (),
    required_tools: Tuple[Tuple[str, int], ...] = (),
    required_actions: Tuple[str, ...] = (),
    auto_actions: Tuple[str, ...] = (),
    required_routes: Tuple[str, ...] = (),
    combat_encounters: Tuple[QuestCombatEncounter, ...] = (),
) -> QuestStageRequirement:
    return QuestStageRequirement(
        stage=stage,
        description=description,
        variant=variant,
        required_inventory=required_inventory,
        required_inventory_options=required_inventory_options,
        consumed_inventory=consumed_inventory,
        consumed_inventory_options=consumed_inventory_options,
        produced_inventory=produced_inventory,
        required_tools=required_tools,
        required_actions=required_actions,
        auto_actions=auto_actions,
        required_routes=required_routes,
        combat_encounters=combat_encounters,
        source=source,
    )


def _combat(
    quest_id: str,
    encounter_id: str,
    display_name: str,
    level: int,
    source: str,
    source_text: str,
    *,
    quantity: int = 1,
    npc_stats: Tuple[Tuple[str, object], ...] = (),
    npc_bonuses: Tuple[Tuple[str, object], ...] = (),
    npc_configs: Tuple[Tuple[str, object], ...] = (),
    npc_stats_source: str = "",
) -> QuestCombatEncounter:
    return QuestCombatEncounter(
        encounter_id=f"{quest_id}_{encounter_id}",
        display_name=display_name,
        level=level,
        quantity=quantity,
        source=source,
        source_text=source_text,
        npc_stats=npc_stats,
        npc_bonuses=npc_bonuses,
        npc_configs=npc_configs,
        npc_stats_source=npc_stats_source,
    )


QuestCombatEncounterReplacement = Union[QuestCombatEncounter, Tuple[QuestCombatEncounter, ...]]


@dataclass(frozen=True)
class QuestStageRequirementCleanup:
    stage: int
    variant: str = ""
    remove_required_inventory: Tuple[str, ...] = ()
    remove_required_inventory_options: Tuple[str, ...] = ()
    remove_consumed_inventory: Tuple[str, ...] = ()
    remove_consumed_inventory_options: Tuple[str, ...] = ()
    remove_required_tools: Tuple[str, ...] = ()
    remove_required_actions: Tuple[str, ...] = ()
    add_required_actions: Tuple[str, ...] = ()
    add_auto_actions: Tuple[str, ...] = ()
    remove_required_routes: Tuple[str, ...] = ()
    add_required_routes: Tuple[str, ...] = ()
    add_consumed_inventory: Tuple[Tuple[str, int], ...] = ()
    add_produced_inventory: Tuple[Tuple[str, int], ...] = ()
    source: str = ""


FISHING_CONTEST_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Austri or Vestri can give me a pass for the Hemenster Fishing Contest."),
    _simple_stage(2, "I have a fishing pass and need to enter the contest."),
    _simple_stage(3, "The contest has started. I need to move the stranger away from the best fishing spot."),
    _simple_stage(4, "The stranger left the best spot. I need to catch the winning fish."),
    _simple_stage(5, "I caught a raw giant carp and should claim the trophy from Bonzo."),
    _simple_stage(6, "I have the fishing trophy and should return it to the dwarf brothers."),
    _simple_stage(7, "The dwarf brothers opened the White Wolf Mountain shortcut.", "Quest complete!"),
)


GERTRUDES_CAT_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Gertrude asked me to find Shilop and Wilough in Varrock Marketplace."),
    _simple_stage(2, "Shilop and Wilough know where Fluffs is hiding, but they want coins."),
    _simple_stage(3, "Fluffs is in the Lumber Yard and will not come down yet."),
    _simple_stage(4, "Fluffs is thirsty and needs milk."),
    _simple_stage(5, "Fluffs is still hungry. Doogle leaves can season a raw sardine."),
    _simple_stage(6, "I made a doogle sardine and should feed it to Fluffs."),
    _simple_stage(7, "Fluffs is worried about her kittens somewhere in the Lumber Yard."),
    _simple_stage(8, "I found the kittens and need to return them to Fluffs."),
    _simple_stage(9, "Fluffs has gone home. Gertrude should hear what happened."),
    _simple_stage(10, "Gertrude gave me a kitten.", "Quest complete!"),
)


CLOCK_TOWER_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Brother Kojo needs the Clock Tower's missing cogs replaced."),
    _simple_stage(2, "I found rat poison in the Clock Tower dungeon and should use it on the rats."),
    _simple_stage(3, "The dungeon rats are dealt with. I need to find the four cogs."),
    _simple_stage(4, "I found the four cogs. They need to be placed on their matching spindles."),
    _simple_stage(5, "The clock is repaired. I should report back to Brother Kojo."),
    _simple_stage(6, "Brother Kojo rewarded me for repairing the tower.", "Quest complete!"),
)


MONKS_FRIEND_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Brother Omad needs the child's blanket recovered from the thieves' hideout."),
    _simple_stage(2, "I recovered the child's blanket and should return it to Brother Omad."),
    _simple_stage(3, "Brother Omad can tell me what else is needed for the birthday party."),
    _simple_stage(4, "Brother Cedric is lost outside the monastery and needs a jug of water."),
    _simple_stage(5, "Brother Cedric needs logs to repair his cart."),
    _simple_stage(6, "Brother Cedric is returning. I should tell Brother Omad and join the party."),
    _simple_stage(7, "Brother Omad's party is underway.", "Quest complete!"),
)


TRIBAL_TOTEM_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Kangai Mau asked me to recover the Rantuki totem from Lord Handelmort."),
    _simple_stage(2, "Wizard Cromperty's teleport block can reach the RPDT depot."),
    _simple_stage(3, "I took the address label for Handelmort Mansion from the RPDT crate."),
    _simple_stage(4, "The teleport block has been redirected to Handelmort Mansion."),
    _simple_stage(5, "I found the Rantuki totem and need to return it to Kangai Mau."),
    _simple_stage(6, "Kangai Mau received the Rantuki totem.", "Quest complete!"),
)


SCORPION_CATCHER_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Thormac needs his three lesser Kharid scorpions recovered."),
    _simple_stage(2, "Thormac gave me a scorpion cage. The Seer can locate the missing scorpions."),
    _simple_stage(3, "The first scorpion is in Taverley Dungeon."),
    _simple_stage(4, "The second scorpion is at the Barbarian Outpost."),
    _simple_stage(5, "The third scorpion is upstairs in Edgeville Monastery."),
    _simple_stage(6, "All three scorpions are caged. I should return to Thormac."),
    _simple_stage(7, "Thormac has his scorpions back.", "Quest complete!"),
)


SHEEP_HERDER_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "Councillor Halgrive gave me poisoned sheep feed and asked me to dispose of four infected sheep.",
        "Doctor Orbon in the Ardougne chapel can sell protective clothing.",
    ),
    _simple_stage(
        2,
        "Doctor Orbon sold me a plague jacket and plague trousers.",
        "I need a cattleprod from the Ardougne sheep enclosure before handling the infected sheep.",
    ),
    _simple_stage(
        3,
        "I found the cattleprod. I need to herd and poison the red, green, blue, and yellow sheep.",
    ),
    _simple_stage(
        4,
        "The infected sheep bones need to be incinerated.",
    ),
    _simple_stage(
        5,
        "I incinerated the red, green, blue, and yellow sheep bones.",
        "Councillor Halgrive should hear that the infected sheep are gone.",
    ),
    _simple_stage(6, "Councillor Halgrive paid me for clearing the infected sheep.", "Quest complete!"),
)


PLAGUE_CITY_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "Edmond asked me to help find Elena and sent me to Alrena for plague protection.",
        "Alrena needs dwellberries to finish the gas mask.",
    ),
    _simple_stage(
        2,
        "Alrena made me a gas mask.",
        "Edmond should explain how to dig into the sewers.",
    ),
    _simple_stage(
        3,
        "Edmond said to soften the soil with water.",
        "I need four buckets of water for the mud patch.",
    ),
    _simple_stage(4, "The soil is soft enough to dig.", "I should use a spade on the mud patch."),
    _simple_stage(
        5,
        "I dug into the Ardougne sewers.",
        "The sewer grill blocks the pipe to West Ardougne.",
    ),
    _simple_stage(
        6,
        "The grill is too secure to pull off alone.",
        "Edmond suggested tying rope to the grill.",
    ),
    _simple_stage(7, "I tied rope to the sewer grill.", "Edmond should help pull it off."),
    _simple_stage(
        8,
        "Edmond and I removed the grill.",
        "I should wear the gas mask, enter West Ardougne, and find Jethick.",
    ),
    _simple_stage(
        9,
        "Jethick needs a picture of Elena.",
        "Showing him a picture should point me to the Rehnison family.",
    ),
    _simple_stage(10, "Jethick gave me a book to return.", "Ted Rehnison is expecting the book."),
    _simple_stage(
        11,
        "I returned the book to Ted Rehnison.",
        "The Rehnisons should know what happened to Elena.",
    ),
    _simple_stage(
        12,
        "Martha Rehnison sent me to Milli.",
        "Milli saw Elena taken into a plague-marked house.",
    ),
    _simple_stage(
        13,
        "The mourners refused entry to the prison house.",
        "The Clerk may let me speak to Bravek for permission.",
    ),
    _simple_stage(
        14,
        "Bravek gave me a scruffy note for a hangover cure.",
        "I need to mix a hangover cure from milk, chocolate dust, and snape grass.",
    ),
    _simple_stage(
        15,
        "I made the hangover cure.",
        "Bravek should take the cure and give me a warrant.",
    ),
    _simple_stage(
        16,
        "Bravek gave me a warrant for the plague house.",
        "I need to sneak in, find the small key, unlock Elena's cell, and report to Edmond.",
    ),
    _simple_stage(17, "Edmond rewarded me for rescuing Elena.", "Quest complete!"),
)


BIOHAZARD_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "Elena needs her distillator back from West Ardougne.",
        "Jerico may know another way over the city wall.",
    ),
    _simple_stage(
        2,
        "Jerico arranged help with a rope ladder.",
        "Omart is waiting by the south end of the West Ardougne wall.",
    ),
    _simple_stage(
        3,
        "Omart needs the watchtower mourners distracted.",
        "Jerico may have an idea involving his messenger pigeons.",
    ),
    _simple_stage(
        4,
        "Jerico suggested using his pigeons.",
        "I need bird feed and a pigeon cage to distract the mourners.",
    ),
    _simple_stage(
        5,
        "The mourners are distracted by Jerico's pigeons.",
        "Omart and Kilron should help me cross the wall.",
    ),
    _simple_stage(
        6,
        "I crossed into West Ardougne.",
        "Elena's distillator is in the Mourner HQ, but the mourners are still inside.",
    ),
    _simple_stage(
        7,
        "I found a rotten apple in the Mourner HQ garden.",
        "The apple can spoil the mourners' stew.",
    ),
    _simple_stage(
        8,
        "A rotten apple poisoned the Mourner HQ stew.",
        "A doctors' gown should let me enter and recover the distillator.",
    ),
    _simple_stage(
        9,
        "I recovered Elena's distillator from the Mourner HQ.",
        "Elena needs it back so she can prepare the plague sample reagents.",
    ),
    _simple_stage(
        10,
        "Elena gave me three vials and a plague sample for Guidor.",
        "The Rimmington chemist should provide more touch paper.",
    ),
    _simple_stage(
        11,
        "The chemist gave me touch paper and warned me about Varrock checks.",
        "His errand boys can smuggle the vials to the Dancing Donkey Inn.",
    ),
    _simple_stage(
        12,
        "Guidor found that the plague sample is harmless.",
        "Elena should hear that the plague may be a hoax.",
    ),
    _simple_stage(
        13,
        "Elena told me to take the news straight to King Lathas.",
        "King Lathas should explain what happens next.",
    ),
    _simple_stage(14, "King Lathas rewarded me for exposing the hoax.", "Quest complete!"),
)


WATERFALL_QUEST_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Almera is worried about Hudon.", "I should find Hudon by the waterfall."),
    _simple_stage(
        2,
        "Hudon mentioned treasure inside the waterfall.",
        "A book nearby may explain Baxtorian's treasure.",
    ),
    _simple_stage(
        3,
        "The book points to Golrie under Tree Gnome Village.",
        "I need the old key to free Golrie.",
    ),
    _simple_stage(
        4,
        "Golrie gave me Glarial's pebble.",
        "The pebble should open Glarial's tomb so I can recover her amulet and urn.",
    ),
    _simple_stage(
        5,
        "I recovered Glarial's amulet and urn.",
        "The waterfall tomb needs six water, air, and earth runes plus Glarial's amulet and urn.",
    ),
    _simple_stage(6, "I took Baxtorian's treasure safely.", "Quest complete!"),
)

ICTHLARINS_LITTLE_HELPER_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "The Wanderer hypnotised me and left a canopic jar in my pack.",
        "I should follow the first memory through Sophanem's southern pyramid.",
    ),
    _simple_stage(
        2,
        "The Sphinx recognised the danger in the canopic jar.",
        "Her token will make Sophanem's High Priest hear me out.",
    ),
    _simple_stage(
        3,
        "The Sphinx's token should convince the High Priest to hear my warning.",
        "I must obtain his permission and place the jar in its matching burial chamber.",
    ),
    _simple_stage(
        4,
        "The canopic guardian has risen from the jar's burial chamber.",
        "I must defeat it before the canopic jar can be recovered.",
    ),
    _simple_stage(
        5,
        "The guardian is defeated and the restored canopic jar is back in my pack.",
        "I must return it and bring willow, linen, sap, and salt for the cleansing ceremony.",
    ),
    _simple_stage(
        6,
        "The Carpenter finished the ceremony's holy symbol.",
        "The next memory will reveal how Amascut corrupted it.",
    ),
    _simple_stage(
        7,
        "Amascut transformed the holy symbol into an unholy symbol.",
        "I must hide it in the eastern sarcophagus to expose the possessed priest.",
    ),
    _simple_stage(
        8,
        "Amascut's unholy symbol is hidden in the eastern sarcophagus.",
        "I must defeat the possessed priest before Icthlarin can break the hypnosis.",
    ),
    _simple_stage(
        9,
        "The High Priest rewarded me with a Catspeak amulet and opened Sophanem.",
        "Quest complete!",
    ),
)


SMOKING_KILLS_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "Sumona asked me to rescue Jesmona from beneath the Pollnivneach well.",
        "I should take a cat and wear my Catspeak amulet before I approach the well.",
    ),
    _simple_stage(
        2,
        "Ali Cat warned me that ordinary Slayer protection cannot block both hazards below.",
        "I should follow my cat's guidance into Catolax's tomb and clear the ranged wing.",
    ),
    _simple_stage(
        3,
        "The ranged wing's guardians fell together and awakened a Mummy Warrior.",
        "I must defeat the mummy and take its Ranged path key.",
    ),
    _simple_stage(
        4,
        "I recovered the Ranged path key.",
        "The key opens the wing's inner door, where a lever will disarm its traps.",
    ),
    _simple_stage(
        5,
        "The ranged lever is set and its traps are disabled.",
        "I should break into the magic wing and bring down its four guardians together.",
    ),
    _simple_stage(
        6,
        "The magic wing's guardians awakened a second Mummy Warrior.",
        "I must defeat it and take the Magic path key.",
    ),
    _simple_stage(
        7,
        "I recovered the Magic path key.",
        "Beyond its door, Catolax can teach me how to combine a Face mask with Earmuffs.",
    ),
    _simple_stage(
        8,
        "Catolax's insight let me make Masked earmuffs from the two Slayer protections.",
        "I should wear the Masked earmuffs before climbing down the Pollnivneach well.",
    ),
    _simple_stage(
        9,
        "The Masked earmuffs protect me from the smoke and banshee screams below.",
        "I need a Banshee voice from a Mighty banshee.",
    ),
    _simple_stage(
        10,
        "I defeated a Mighty banshee and recovered its lingering voice.",
        "The Banshee voice should open the mystic barrier.",
    ),
    _simple_stage(
        11,
        "The Banshee voice broke the barrier at the dungeon's heart.",
        "At half health the Banshee Mistress calls four level 141 Insectoid Assassins into the same battle.",
    ),
    _simple_stage(
        12,
        "The Banshee Mistress is dead and Catolax has spoken to me once more.",
        "I should report my victory to Sumona in Pollnivneach.",
    ),
    _simple_stage(13, "Sumona rewarded me and opened the Slayer reward system.", "Quest complete!"),
)


DWARF_CANNON_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Captain Lawgof needs the Black Guard camp railings repaired."),
    _simple_stage(2, "Captain Lawgof gave me six railings. The broken stockade needs repair."),
    _simple_stage(3, "The six broken railings have been repaired. I should report back to Captain Lawgof."),
    _simple_stage(4, "Captain Lawgof asked me to find Gilob's remains near the watchtower."),
    _simple_stage(5, "I found Gilob's remains and should return them to Captain Lawgof."),
    _simple_stage(6, "Captain Lawgof found a child hidden in the goblin cave south-east of the camp."),
    _simple_stage(7, "I found Lollk in the goblin hideout and need to get him to safety."),
    _simple_stage(8, "Lollk is safe. Captain Lawgof has a toolkit for repairing the sabotaged cannon."),
    _simple_stage(9, "The cannon still needs to be repaired with Captain Lawgof's toolkit."),
    _simple_stage(10, "The cannon is repaired. Captain Lawgof wants help from Nulodion."),
    _simple_stage(11, "Nulodion gave me an ammo mould and notes to take back to Captain Lawgof."),
    _simple_stage(12, "Captain Lawgof needs Nulodion's ammo mould and notes."),
    _simple_stage(13, "Captain Lawgof accepted Nulodion's parts. I should receive his cannon recommendation."),
    _simple_stage(14, "Captain Lawgof gave his recommendation.", "Quest complete!"),
)


HOLY_GRAIL_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "King Arthur sent me to Merlin for clues about the Holy Grail."),
    _simple_stage(2, "Merlin believes the Grail passed through Entrana and Sir Galahad may know more."),
    _simple_stage(3, "The Entrana High Priest and crone pointed me toward Sir Galahad and the Fisher Realm."),
    _simple_stage(4, "Sir Galahad gave me a Holy table napkin from the Fisher Realm."),
    _simple_stage(5, "The Holy table napkin should reveal the Magic whistles hidden in Draynor Manor."),
    _simple_stage(
        6,
        "The Magic whistle can take me to the Fisher Realm from the six stone heads.",
        "The Black Knight Titan blocks the castle and must be defeated with Excalibur.",
    ),
    _simple_stage(7, "The Black Knight Titan is defeated. I can enter the castle and speak to the Fisher King."),
    _simple_stage(8, "The Fisher King asked me to find his son, Sir Percival."),
    _simple_stage(9, "Sir Percival can restore the Fisher Realm if I free him and show him the Magic whistle."),
    _simple_stage(10, "The Fisher Realm is restored. I should take the Holy grail to King Arthur."),
    _simple_stage(11, "King Arthur has the Holy grail.", "Quest complete!"),
)


TREE_GNOME_VILLAGE_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "King Bolren sent me to Commander Montai on the battlefield."),
    _simple_stage(2, "Commander Montai needs six normal logs to strengthen the gnome battlements."),
    _simple_stage(3, "Commander Montai is ready to explain the next phase of the attack."),
    _simple_stage(4, "I need coordinates from the three tracker gnomes so the ballista can hit the stronghold."),
    _simple_stage(5, "The ballista broke the stronghold wall. I need the first Orb of protection from the chest."),
    _simple_stage(6, "King Bolren took the first orb. A Khazard warlord has the remaining orbs."),
    _simple_stage(7, "I recovered the remaining Orbs of protection and should return them to King Bolren."),
    _simple_stage(8, "King Bolren replaced the orbs and rewarded me.", "Quest complete!"),
)


QUEST_STAGE_COUNT_REPLACEMENTS_BY_ID: Dict[str, int] = {
    "icthlarins_little_helper": len(ICTHLARINS_LITTLE_HELPER_STAGES),
    SMOKING_KILLS_ID: len(SMOKING_KILLS_STAGES),
    DWARF_CANNON_ID: len(DWARF_CANNON_STAGES),
    HOLY_GRAIL_ID: len(HOLY_GRAIL_STAGES),
    TREE_GNOME_VILLAGE_ID: len(TREE_GNOME_VILLAGE_STAGES),
    FISHING_CONTEST_ID: len(FISHING_CONTEST_STAGES),
    GERTRUDES_CAT_ID: len(GERTRUDES_CAT_STAGES),
    CLOCK_TOWER_ID: len(CLOCK_TOWER_STAGES),
    MONKS_FRIEND_ID: len(MONKS_FRIEND_STAGES),
    TRIBAL_TOTEM_ID: len(TRIBAL_TOTEM_STAGES),
    SCORPION_CATCHER_ID: len(SCORPION_CATCHER_STAGES),
    SHEEP_HERDER_ID: len(SHEEP_HERDER_STAGES),
    PLAGUE_CITY_ID: len(PLAGUE_CITY_STAGES),
    BIOHAZARD_ID: len(BIOHAZARD_STAGES),
    WATERFALL_QUEST_ID: len(WATERFALL_QUEST_STAGES),
}


QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStage, ...]] = {
    "icthlarins_little_helper": ICTHLARINS_LITTLE_HELPER_STAGES,
    SMOKING_KILLS_ID: SMOKING_KILLS_STAGES,
    DWARF_CANNON_ID: DWARF_CANNON_STAGES,
    HOLY_GRAIL_ID: HOLY_GRAIL_STAGES,
    TREE_GNOME_VILLAGE_ID: TREE_GNOME_VILLAGE_STAGES,
    FISHING_CONTEST_ID: FISHING_CONTEST_STAGES,
    GERTRUDES_CAT_ID: GERTRUDES_CAT_STAGES,
    CLOCK_TOWER_ID: CLOCK_TOWER_STAGES,
    MONKS_FRIEND_ID: MONKS_FRIEND_STAGES,
    TRIBAL_TOTEM_ID: TRIBAL_TOTEM_STAGES,
    SCORPION_CATCHER_ID: SCORPION_CATCHER_STAGES,
    SHEEP_HERDER_ID: SHEEP_HERDER_STAGES,
    PLAGUE_CITY_ID: PLAGUE_CITY_STAGES,
    BIOHAZARD_ID: BIOHAZARD_STAGES,
    WATERFALL_QUEST_ID: WATERFALL_QUEST_STAGES,
}


QUEST_COMBAT_TEXT_REPLACEMENTS_BY_ID: Dict[str, str] = {
    "icthlarins_little_helper": (
        "One canopic guardian (Apmeken, Het, Crondis, or Scabaras; level 75-81), "
        "then the level 126 Possessed Priest."
    ),
    SMOKING_KILLS_ID: (
        "Two grouped tomb-guardian waves and two level 54 Mummy Warriors; "
        "one level 90 Mighty banshee; then the level 111 Banshee Mistress, "
        "whose second phase folds her four level 141 Insectoid Assassins into one battle."
    ),
    DWARF_CANNON_ID: "None.",
    HOLY_GRAIL_ID: "Black Knight Titan (level 120), defeated only with Excalibur.",
    TREE_GNOME_VILLAGE_ID: (
        "Two Khazard commanders (level 48) can block the first orb; "
        "the Khazard warlord (level 112) holds the remaining orbs."
    ),
    FISHING_CONTEST_ID: "None.",
    GERTRUDES_CAT_ID: "None.",
    CLOCK_TOWER_ID: "None.",
    MONKS_FRIEND_ID: "Optional: two level 21 thieves and a level 25 head thief.",
    TRIBAL_TOTEM_ID: "None.",
    SCORPION_CATCHER_ID: "You will need to defeat a level 39 jailer.",
    SHEEP_HERDER_ID: "None.",
    PLAGUE_CITY_ID: "None.",
    BIOHAZARD_ID: "You will need to defeat a level 13 mourner.",
    WATERFALL_QUEST_ID: "None required, but the Waterfall Dungeon contains aggressive skeletons and spiders.",
}


QUEST_ITEM_REWARD_ADDITIONS_BY_ID = varrock_museum_quest_reward_additions_as_dict()


QUEST_ITEM_REWARD_REPLACEMENTS_BY_ID: Dict[str, Tuple[Tuple[str, int], ...]] = {
    TREE_GNOME_VILLAGE_ID: (("Gnome amulet", 1),),
    PLAGUE_CITY_ID: (("A magic scroll", 1),),
    DWARF_CANNON_ID: (("Ammo mould", 1),),
    HAZEEL_CULT_ID: (("Coins", 2005),),
    "stolen_hearts": (("Coins", 2500),),
    "diamond_in_the_rough": (),
    "icthlarins_little_helper": (("Catspeak amulet", 1),),
    SMOKING_KILLS_ID: (),
    SONG_FROM_THE_DEPTHS_ID: (
        ("Coral bolts", 50),
        ("Coral crossbow", 1),
        ("Remora's necklace", 1),
    ),
    SOME_LIKE_IT_COLD_ID: (("Rock costume", 1), ("Pop costume", 1)),
}

QUEST_XP_REWARD_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestXpReward, ...]] = {
    "royal_trouble": (QuestXpReward("agility", 5000),),
    "grim_tales": (QuestXpReward("agility", 6000),),
    "stolen_hearts": (QuestXpReward("constitution", 250),),
    "diamond_in_the_rough": (
        QuestXpReward("agility", 250),
        QuestXpReward("constitution", 250),
        QuestXpReward("thieving", 250),
    ),
    SONG_FROM_THE_DEPTHS_ID: (QuestXpReward("constitution", 700),),
    SOME_LIKE_IT_COLD_ID: (
        QuestXpReward("construction", 10000),
        QuestXpReward("crafting", 40000),
        QuestXpReward("fishing", 40000),
        QuestXpReward("thieving", 10000),
    ),
}

QUEST_LAMP_REWARD_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestLampReward, ...]] = {
    "myths_of_the_white_lands": (
        QuestLampReward(
            "Post-quest ice-cave Agility reward",
            10000,
            ("agility",),
            1,
            "https://runescape.wiki/w/Myths_of_the_White_Lands?oldid=6555850",
            "Optional reward for completing the additional ice-cave route.",
        ),
    ),
}


QUEST_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    JUNGLE_POTION_ID: (
        _stage_req(
            1,
            "Search the south-west marshy jungle vines for snake weed.",
            f"{DARKAN_JUNGLE_POTION_SOURCE}; {JUNGLE_POTION_CACHE_SOURCE}; {JUNGLE_POTION_WIKI_SOURCE}",
            produced_inventory=(("Grimy snake weed", 1),),
            auto_actions=("Search the south-west marshy jungle vines for snake weed",),
        ),
        _stage_req(
            2,
            "Clean the snake weed and give it to Trufitus.",
            f"{DARKAN_JUNGLE_POTION_TRUFITUS_SOURCE}; {DARKAN_HERB_CLEANING_SOURCE_PATH}; {JUNGLE_POTION_WIKI_SOURCE}",
            consumed_inventory=(("Clean snake weed", 1),),
            auto_actions=("Give Trufitus clean snake weed",),
        ),
        _stage_req(
            3,
            "Search the north-east palm trees for ardrigal.",
            f"{DARKAN_JUNGLE_POTION_SOURCE}; {JUNGLE_POTION_CACHE_SOURCE}; {JUNGLE_POTION_WIKI_SOURCE}",
            produced_inventory=(("Grimy ardrigal", 1),),
            auto_actions=("Search the north-east palm trees for ardrigal",),
        ),
        _stage_req(
            4,
            "Clean the ardrigal and give it to Trufitus.",
            f"{DARKAN_JUNGLE_POTION_TRUFITUS_SOURCE}; {DARKAN_HERB_CLEANING_SOURCE_PATH}; {JUNGLE_POTION_WIKI_SOURCE}",
            consumed_inventory=(("Clean ardrigal", 1),),
            auto_actions=("Give Trufitus clean ardrigal",),
        ),
        _stage_req(
            5,
            "Search the scorched earth south of the village for sito foil.",
            f"{DARKAN_JUNGLE_POTION_SOURCE}; {JUNGLE_POTION_CACHE_SOURCE}; {JUNGLE_POTION_WIKI_SOURCE}",
            produced_inventory=(("Grimy sito foil", 1),),
            auto_actions=("Search the scorched earth south of the village for sito foil",),
        ),
        _stage_req(
            6,
            "Clean the sito foil and give it to Trufitus.",
            f"{DARKAN_JUNGLE_POTION_TRUFITUS_SOURCE}; {DARKAN_HERB_CLEANING_SOURCE_PATH}; {JUNGLE_POTION_WIKI_SOURCE}",
            consumed_inventory=(("Clean sito foil", 1),),
            auto_actions=("Give Trufitus clean sito foil",),
        ),
        _stage_req(
            7,
            "Search the rocks south-east of the village for volencia moss.",
            f"{DARKAN_JUNGLE_POTION_SOURCE}; {JUNGLE_POTION_CACHE_SOURCE}; {JUNGLE_POTION_WIKI_SOURCE}",
            produced_inventory=(("Grimy volencia moss", 1),),
            auto_actions=("Search the rocks south-east of the village for volencia moss",),
        ),
        _stage_req(
            8,
            "Clean the volencia moss and give it to Trufitus.",
            f"{DARKAN_JUNGLE_POTION_TRUFITUS_SOURCE}; {DARKAN_HERB_CLEANING_SOURCE_PATH}; {JUNGLE_POTION_WIKI_SOURCE}",
            consumed_inventory=(("Clean volencia moss", 1),),
            auto_actions=("Give Trufitus clean volencia moss",),
        ),
        _stage_req(
            9,
            "Search the fungus-covered northern cavern wall for rogue's purse.",
            f"{DARKAN_JUNGLE_POTION_SOURCE}; {JUNGLE_POTION_CACHE_SOURCE}; {JUNGLE_POTION_WIKI_SOURCE}",
            produced_inventory=(("Grimy rogue's purse", 1),),
            auto_actions=("Search the fungus-covered northern cavern wall for rogue's purse",),
        ),
        _stage_req(
            10,
            "Clean the rogue's purse and give it to Trufitus.",
            f"{DARKAN_JUNGLE_POTION_TRUFITUS_SOURCE}; {DARKAN_HERB_CLEANING_SOURCE_PATH}; {JUNGLE_POTION_WIKI_SOURCE}",
            consumed_inventory=(("Clean rogue's purse", 1),),
            auto_actions=("Give Trufitus clean rogue's purse",),
        ),
    ),
    SHILO_VILLAGE_ID: (
        _stage_req(
            1,
            "Deliver Mosol Rei's Wampum belt to Trufitus and agree to search for Ah Za Rhoon.",
            f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_MOSOL_SOURCE}; {SHILO_VILLAGE_TRUFITUS_SOURCE}",
            consumed_inventory=(("Wampum belt", 1),),
            auto_actions=(
                "Accept Mosol Rei's warning and carry the Wampum belt to Trufitus",
                "Ask Trufitus about Ah Za Rhoon and agree to search for the lost temple",
            ),
        ),
        _stage_req(
            2,
            "Find the Ah Za Rhoon fissure, light the drop, secure a rope, and enter the temple.",
            f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
            consumed_inventory=(("Rope", 1),),
            consumed_inventory_options=(
                tuple((item_name, 1) for item_name in LIT_LIGHT_SOURCE_ITEMS),
            ),
            required_tools=(("Spade", 1),),
            auto_actions=(
                "Dig into the buried mound east of Tai Bwo Wannai",
                "Lower the lit light source into the fissure and secure the rope",
                "Climb into Ah Za Rhoon",
            ),
        ),
        _stage_req(
            3,
            "Read the temple scrolls, recover the plaque, and take Zadimus's remains.",
            f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}",
            produced_inventory=(
                ("Stone-plaque", 1),
                ("Tattered scroll", 1),
                ("Crumpled scroll", 1),
                ("Zadimus corpse", 1),
            ),
            auto_actions=(
                "Include the Stone-plaque in the collapsed temple search",
                "Search past the loose-rock trap and gallows gas",
                "Recover and read both Ah Za Rhoon scrolls, then take Zadimus's corpse",
            ),
        ),
        _stage_req(
            4,
            "Show the Ah Za Rhoon evidence to Trufitus and bury Zadimus on sacred ground.",
            f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}; {SHILO_VILLAGE_TRUFITUS_SOURCE}",
            required_inventory=(
                ("Tattered scroll", 1),
                ("Crumpled scroll", 1),
            ),
            consumed_inventory=(("Zadimus corpse", 1),),
            produced_inventory=(("Bone shard", 1),),
            auto_actions=(
                "Show both scrolls and Zadimus's corpse; include the plaque if it is still carried",
                "Bury Zadimus beside the tribal statue and receive his Bone shard",
            ),
        ),
        _stage_req(
            5,
            "Search Bervirius's Cairn Isle tomb for the clues left on its dolmen.",
            f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}",
            produced_inventory=(
                ("Sword pommel", 1),
                ("Locating crystal", 1),
                ("Bervirius notes", 1),
            ),
            auto_actions=(
                "Cross to Cairn Isle and descend into Bervirius's tomb",
                "Search the dolmen and recover all three clues",
            ),
        ),
        _stage_req(
            6,
            "Read Bervirius's notes and show the tomb evidence to Trufitus.",
            f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}; {SHILO_VILLAGE_TRUFITUS_SOURCE}",
            required_inventory=(
                ("Sword pommel", 1),
                ("Locating crystal", 1),
                ("Bervirius notes", 1),
            ),
            auto_actions=(
                "Read all three sections of Bervirius's notes",
                "Show the Sword pommel, Locating crystal, and notes to Trufitus",
            ),
        ),
        _stage_req(
            7,
            "Carve Zadimus's Bone key and chisel the Sword pommel into Bone beads.",
            f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}",
            required_inventory=(("Bervirius notes", 1),),
            consumed_inventory=(
                ("Bone shard", 1),
                ("Sword pommel", 1),
            ),
            produced_inventory=(("Bone key", 1), ("Bone beads", 1)),
            required_tools=(("Chisel", 1),),
            auto_actions=(
                "Carve the Bone shard into the Bone key",
                "Chisel the Sword pommel into Bone beads",
            ),
        ),
        _stage_req(
            8,
            "String the Bone beads with Bronze wire to make the protective Beads of the dead.",
            f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}",
            required_inventory=(("Bervirius notes", 1),),
            consumed_inventory=(("Bone beads", 1), ("Bronze wire", 1)),
            produced_inventory=(("Beads of the dead", 1),),
            auto_actions=("String the Bone beads with Bronze wire",),
        ),
        _stage_req(
            9,
            "Locate Rashiliyia's tomb, wear the Beads of the dead, and open its bone doors.",
            f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
            consumed_inventory=(("Bones", 3),),
            required_tools=(
                ("Bone key", 1),
                ("Beads of the dead", 1),
                ("Locating crystal", 1),
            ),
            auto_actions=(
                "Use the Locating crystal to find Rashiliyia's hidden tomb",
                "Wear the Beads of the dead and unlock the ancient door with the Bone key",
                "Fill the skeletal door's three recesses with regular bones",
            ),
        ),
        _stage_req(
            10,
            "Defeat Nazastarool's zombie, skeleton, and ghost forms in order.",
            (
                f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}; "
                f"{DARKAN_NAZASTAROOL_91_NPC_SOURCE}; "
                f"{DARKAN_NAZASTAROOL_68_NPC_SOURCE}; "
                f"{DARKAN_NAZASTAROOL_93_NPC_SOURCE}"
            ),
            produced_inventory=(("Rashiliyia corpse", 1),),
            required_tools=(("Bone key", 1), ("Beads of the dead", 1)),
            auto_actions=("Take Rashiliyia's corpse from the dolmen after the final form falls",),
            combat_encounters=(
                QuestCombatEncounter(
                    encounter_id="shilo_village_nazastarool_91",
                    display_name="Nazastarool",
                    level=91,
                    source=SHILO_VILLAGE_WIKI_SOURCE,
                ),
            ),
        ),
        _stage_req(
            11,
            "Show Rashiliyia's corpse to Trufitus, then return it to Bervirius's dolmen.",
            f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}; {SHILO_VILLAGE_TRUFITUS_SOURCE}",
            consumed_inventory=(("Rashiliyia corpse", 1),),
            auto_actions=(
                "Show Rashiliyia's corpse to Trufitus",
                "Return to Cairn Isle and place the corpse on Bervirius's dolmen",
                "Release Rashiliyia's spirit and open Shilo Village",
            ),
        ),
    ),
    "icthlarins_little_helper": (
        _stage_req(
            1,
            "Trust the Wanderer, enter Sophanem under hypnosis, and recover the canopic jar.",
            (
                f"{ICTHLARINS_LITTLE_HELPER_WIKI_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_CACHE_SOURCE}"
            ),
            required_inventory_options=(
                (
                    ("Kitten", 1),
                    ("Cat", 1),
                    ("Overgrown cat", 1),
                    ("Hellcat", 1),
                ),
            ),
            consumed_inventory=(("Tinderbox", 1), ("Waterskin (4)", 1)),
            produced_inventory=(("Canopic jar", 1),),
            auto_actions=(
                "Pick up the following cat before speaking to the Wanderer",
                "Enter Sophanem through the secret rock and survive the first pyramid memory",
                "Solve the nine-tile sarcophagus puzzle",
            ),
        ),
        _stage_req(
            2,
            "Answer the Sphinx's family riddle and take her token to the High Priest.",
            (
                f"{ICTHLARINS_LITTLE_HELPER_WIKI_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}; "
                "https://runescape.wiki/w/Sphinx%27s_token?oldid=6520569"
            ),
            required_inventory=(("Canopic jar", 1),),
            required_inventory_options=(
                (
                    ("Kitten", 1),
                    ("Cat", 1),
                    ("Overgrown cat", 1),
                    ("Hellcat", 1),
                ),
            ),
            produced_inventory=(("Sphinx's token", 1),),
            auto_actions=(
                "Answer nine to the Sphinx's riddle",
                "Ask the High Priest how to return the stolen remains",
            ),
        ),
        _stage_req(
            3,
            "Present the Sphinx's token and place the canopic jar in its burial chamber.",
            (
                f"{ICTHLARINS_LITTLE_HELPER_WIKI_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_CACHE_SOURCE}"
            ),
            consumed_inventory=(("Canopic jar", 1), ("Sphinx's token", 1)),
            auto_actions=(
                "Present the Sphinx's token to the High Priest",
                "Match the canopic jar to its burial chamber",
            ),
        ),
        _stage_req(
            4,
            "Defeat the apparition bound to the canopic jar.",
            (
                f"{ICTHLARINS_LITTLE_HELPER_WIKI_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_CACHE_SOURCE}"
            ),
            produced_inventory=(("Canopic jar", 1),),
            auto_actions=("Restore the assigned jar after the guardian falls",),
            combat_encounters=(
                _combat(
                    "icthlarins_little_helper",
                    "canopic_guardian",
                    "Canopic guardian",
                    81,
                    (
                        f"{ICTHLARINS_LITTLE_HELPER_WIKI_SOURCE}; "
                        "https://runescape.wiki/w/Apmeken_apparition?oldid=5795222; "
                        "https://runescape.wiki/w/Het_apparition?oldid=6178412; "
                        "https://runescape.wiki/w/Crondis_apparition?oldid=6342246; "
                        "https://runescape.wiki/w/Scabaras_apparition?oldid=6378180; "
                        f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}"
                    ),
                    (
                        "The assigned jar produces exactly one of four guardians. "
                        "The period range is level 75-81, 600-750 LP, and melee and/or magic."
                    ),
                    npc_stats=(
                        ("hitpoints", 750),
                        ("attack", 81),
                        ("strength", 81),
                        ("defence", 81),
                        ("magic", 81),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 90),
                        ("attack_style", "magic"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=(
                        "Period upper-bound resolver adapter across the four possible guardians; "
                        "not claimed as historical hidden combat stats"
                    ),
                ),
            ),
        ),
        _stage_req(
            5,
            "Return the restored jar and prepare the Carpenter's holy symbol and Embalmer's supplies.",
            (
                f"{ICTHLARINS_LITTLE_HELPER_WIKI_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}; "
                "https://runescape.wiki/w/Bucket_of_sap?oldid=6288759; "
                "https://runescape.wiki/w/Linen?oldid=5787786"
            ),
            required_tools=(("Knife", 1),),
            consumed_inventory=(
                ("Canopic jar", 1),
                ("Coins", 30),
                ("Willow logs", 1),
                ("Bucket", 1),
            ),
            consumed_inventory_options=((("Pile of salt", 1), ("Bag of salt", 1)),),
            produced_inventory=(("Holy symbol (Icthlarin's Little Helper)", 1),),
            auto_actions=(
                "Return the restored jar to the High Priest",
                "Buy one sheet of linen from Raetul for 30 coins",
                "Collect a bucket of sap from an evergreen tree with the knife",
                "Give the willow log to the Carpenter and the linen, sap, and salt to the Embalmer",
                "Collect the finished holy symbol without a wall-clock wait",
            ),
        ),
        _stage_req(
            6,
            "Relive Amascut's betrayal and recover the transformed unholy symbol.",
            (
                f"{ICTHLARINS_LITTLE_HELPER_WIKI_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}; "
                "https://runescape.wiki/w/Holy_symbol_%28Icthlarin%27s_Little_Helper%29?oldid=6352893; "
                "https://runescape.wiki/w/Unholy_symbol_%28Icthlarin%27s_Little_Helper%29?oldid=6315484"
            ),
            consumed_inventory=(("Holy symbol (Icthlarin's Little Helper)", 1),),
            produced_inventory=(("Unholy symbol (Icthlarin's Little Helper)", 1),),
            auto_actions=("Watch Amascut invert the holy symbol during the third memory",),
        ),
        _stage_req(
            7,
            "Hide Amascut's unholy symbol in the eastern sarcophagus.",
            (
                f"{ICTHLARINS_LITTLE_HELPER_WIKI_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}; "
                "https://runescape.wiki/w/Unholy_symbol_%28Icthlarin%27s_Little_Helper%29?oldid=6315484"
            ),
            consumed_inventory=(("Unholy symbol (Icthlarin's Little Helper)", 1),),
            auto_actions=("Hide the unholy symbol in the eastern sarcophagus",),
        ),
        _stage_req(
            8,
            "Defeat the possessed priest, break Amascut's hypnosis, and report to the High Priest.",
            (
                f"{ICTHLARINS_LITTLE_HELPER_WIKI_SOURCE}; "
                "https://runescape.wiki/w/Possessed_Priest?oldid=6032196; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_POSSESSED_PRIEST_SOURCE}"
            ),
            auto_actions=(
                "Relive Icthlarin removing Amascut's hypnosis and report to the High Priest",
            ),
            combat_encounters=(
                _combat(
                    "icthlarins_little_helper",
                    "possessed_priest",
                    "Possessed Priest",
                    126,
                    (
                        "https://runescape.wiki/w/Possessed_Priest?oldid=6032196; "
                        f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}; "
                        f"{ICTHLARINS_LITTLE_HELPER_POSSESSED_PRIEST_SOURCE}"
                    ),
                    "Level 126, 800 LP, aggressive Magic using bolt spells; approximate period max hit 140.",
                    npc_stats=(
                        ("hitpoints", 800),
                        ("attack", 90),
                        ("strength", 90),
                        ("defence", 40),
                        ("magic", 60),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 140),
                        ("attack_style", "magic"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=ICTHLARINS_LITTLE_HELPER_POSSESSED_PRIEST_SOURCE,
                ),
            ),
        ),
    ),
    SMOKING_KILLS_ID: (
        _stage_req(
            1,
            "Accept Sumona's rescue request and hear Ali Cat's warning at the Pollnivneach well.",
            SMOKING_KILLS_WIKI_SOURCE,
            required_inventory_options=(
                (
                    ("Kitten", 1),
                    ("Cat", 1),
                    ("Overgrown cat", 1),
                    ("Hellcat", 1),
                ),
            ),
            required_tools=(("Catspeak amulet", 1),),
            auto_actions=(
                "Accept Sumona's request to rescue Jesmona",
                "Approach the Pollnivneach well with a cat and hear Ali Cat's warning",
            ),
        ),
        _stage_req(
            2,
            "Break into the ranged wing of Catolax's tomb and bring down all four guardians together.",
            SMOKING_KILLS_WIKI_SOURCE,
            required_inventory_options=(
                (
                    ("Kitten", 1),
                    ("Cat", 1),
                    ("Overgrown cat", 1),
                    ("Hellcat", 1),
                ),
            ),
            required_tools=(("Catspeak amulet", 1), ("Pickaxe", 1)),
            auto_actions=(
                "Follow the cat's guidance through the Ullek swamp to Catolax's tomb",
                "Break the ranged-wing door and disable both trap banks",
                "Bring the four guardians down together before they can recover",
            ),
            combat_encounters=(
                _combat(
                    SMOKING_KILLS_ID,
                    "ranged_tomb_guardians",
                    "Ranged-wing tomb guardians",
                    20,
                    SMOKING_KILLS_WIKI_SOURCE,
                    (
                        "One grouped resolver wave represents the four roughly 200-LP, level 10-20 "
                        "guardians that must fall together; the pinned infobox and walkthrough disagree "
                        "on their exact identities."
                    ),
                    npc_stats=(
                        ("hitpoints", 800),
                        ("attack", 20),
                        ("strength", 20),
                        ("defence", 20),
                        ("magic", 20),
                        ("ranged", 20),
                    ),
                    npc_configs=(
                        ("attack_style", "ranged"),
                        ("minimum_player_combat", 85),
                    ),
                    npc_stats_source=(
                        "Review-native grouped upper-bound adapter from Smoking Kills oldid 6548001; "
                        "exact component identities and hidden stats are source_blocked"
                    ),
                ),
            ),
        ),
        _stage_req(
            3,
            "Defeat the Mummy Warrior awakened by the ranged-wing guardians.",
            f"{SMOKING_KILLS_WIKI_SOURCE}; {SMOKING_KILLS_MUMMY_SOURCE}; {SMOKING_KILLS_MUMMY_DARKAN_SOURCE}",
            produced_inventory=(("Ranged path key", 1),),
            auto_actions=("Take the Ranged path key from the fallen Mummy Warrior",),
            combat_encounters=(
                _combat(
                    SMOKING_KILLS_ID,
                    "ranged_mummy_warrior",
                    "Mummy Warrior",
                    54,
                    (
                        f"{SMOKING_KILLS_WIKI_SOURCE}; {SMOKING_KILLS_MUMMY_SOURCE}; "
                        f"{SMOKING_KILLS_MUMMY_DARKAN_SOURCE}"
                    ),
                    "The first level 54 Mummy Warrior uses melee and can hit up to 80.",
                    npc_stats=(
                        ("hitpoints", 540),
                        ("attack", 54),
                        ("strength", 54),
                        ("defence", 54),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 80),
                        ("attack_style", "melee"),
                        ("minimum_player_combat", 85),
                    ),
                    npc_stats_source=(
                        "Bounded level-based resolver adapter; period HP and hidden combat stats are source_blocked, "
                        "while level 54 and max hit 80 are sourced"
                    ),
                ),
            ),
        ),
        _stage_req(
            4,
            "Open the ranged path door and pull its lever to disarm the wing's traps.",
            SMOKING_KILLS_WIKI_SOURCE,
            consumed_inventory=(("Ranged path key", 1),),
            auto_actions=(
                "Open the ranged path door",
                "Pull the ranged-wing lever",
            ),
        ),
        _stage_req(
            5,
            "Break into the magic wing and bring down its four guardians together.",
            SMOKING_KILLS_WIKI_SOURCE,
            required_inventory_options=(
                (
                    ("Kitten", 1),
                    ("Cat", 1),
                    ("Overgrown cat", 1),
                    ("Hellcat", 1),
                ),
            ),
            required_tools=(("Catspeak amulet", 1), ("Pickaxe", 1)),
            auto_actions=(
                "Break the magic-wing door and disable both trap banks",
                "Bring the four guardians down together before they can recover",
            ),
            combat_encounters=(
                _combat(
                    SMOKING_KILLS_ID,
                    "magic_tomb_guardians",
                    "Magic-wing tomb guardians",
                    20,
                    SMOKING_KILLS_WIKI_SOURCE,
                    (
                        "One grouped resolver wave represents the four roughly 200-LP, level 10-20 "
                        "guardians that must fall together; the pinned infobox and walkthrough disagree "
                        "on their exact identities."
                    ),
                    npc_stats=(
                        ("hitpoints", 800),
                        ("attack", 20),
                        ("strength", 20),
                        ("defence", 20),
                        ("magic", 20),
                        ("ranged", 20),
                    ),
                    npc_configs=(
                        ("attack_style", "magic"),
                        ("minimum_player_combat", 85),
                    ),
                    npc_stats_source=(
                        "Review-native grouped upper-bound adapter from Smoking Kills oldid 6548001; "
                        "exact component identities and hidden stats are source_blocked"
                    ),
                ),
            ),
        ),
        _stage_req(
            6,
            "Defeat the Mummy Warrior awakened by the magic-wing guardians.",
            f"{SMOKING_KILLS_WIKI_SOURCE}; {SMOKING_KILLS_MUMMY_SOURCE}; {SMOKING_KILLS_MUMMY_DARKAN_SOURCE}",
            produced_inventory=(("Magic path key", 1),),
            auto_actions=("Take the Magic path key from the fallen Mummy Warrior",),
            combat_encounters=(
                _combat(
                    SMOKING_KILLS_ID,
                    "magic_mummy_warrior",
                    "Mummy Warrior",
                    54,
                    (
                        f"{SMOKING_KILLS_WIKI_SOURCE}; {SMOKING_KILLS_MUMMY_SOURCE}; "
                        f"{SMOKING_KILLS_MUMMY_DARKAN_SOURCE}"
                    ),
                    "The second level 54 Mummy Warrior uses melee and can hit up to 80.",
                    npc_stats=(
                        ("hitpoints", 540),
                        ("attack", 54),
                        ("strength", 54),
                        ("defence", 54),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 80),
                        ("attack_style", "melee"),
                        ("minimum_player_combat", 85),
                    ),
                    npc_stats_source=(
                        "Bounded level-based resolver adapter; period HP and hidden combat stats are source_blocked, "
                        "while level 54 and max hit 80 are sourced"
                    ),
                ),
            ),
        ),
        _stage_req(
            7,
            "Unlock the final path, speak to Catolax, and combine the two Slayer protections.",
            SMOKING_KILLS_WIKI_SOURCE,
            consumed_inventory=(
                ("Magic path key", 1),
                ("Face mask", 1),
                ("Earmuffs", 1),
            ),
            produced_inventory=(("Masked earmuffs", 1),),
            required_tools=(("Ghostspeak amulet", 1),),
            auto_actions=(
                "Open the magic path door and pull its lever",
                "Cross the disabled central traps and speak to Catolax",
                "Combine the Face mask and Earmuffs using Catolax's insight",
            ),
        ),
        _stage_req(
            8,
            "Climb down the Pollnivneach well with Masked earmuffs protecting you.",
            SMOKING_KILLS_WIKI_SOURCE,
            required_tools=(("Masked earmuffs", 1),),
            auto_actions=("Enter the Desert Slayer Dungeon through the Pollnivneach well",),
        ),
        _stage_req(
            9,
            "Defeat a Mighty banshee and take its lingering voice.",
            (
                f"{SMOKING_KILLS_WIKI_SOURCE}; {SMOKING_KILLS_MIGHTY_BANSHEE_SOURCE}; "
                f"{SMOKING_KILLS_MIGHTY_BANSHEE_DARKAN_SOURCE}"
            ),
            produced_inventory=(("Banshee voice", 1),),
            required_tools=(("Masked earmuffs", 1),),
            auto_actions=(
                "Recover one Banshee voice after the Mighty banshee falls",
            ),
            combat_encounters=(
                _combat(
                    SMOKING_KILLS_ID,
                    "mighty_banshee",
                    "Mighty banshee",
                    90,
                    (
                        f"{SMOKING_KILLS_WIKI_SOURCE}; {SMOKING_KILLS_MIGHTY_BANSHEE_SOURCE}; "
                        f"{SMOKING_KILLS_MIGHTY_BANSHEE_DARKAN_SOURCE}"
                    ),
                    (
                        "A level 90 aggressive Mighty banshee with 850 LP, magical melee, "
                        "attack speed 6, and approximate max hit 90. One deterministic quest kill "
                        "stands in for the source-blocked Banshee voice drop rate."
                    ),
                    npc_stats=(
                        ("hitpoints", 850),
                        ("attack", 90),
                        ("strength", 90),
                        ("defence", 90),
                        ("magic", 90),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 90),
                        ("attack_speed", 6),
                        ("attack_style", "melee"),
                        ("aggressiveness_type", "aggressive"),
                        ("minimum_player_combat", 85),
                    ),
                    npc_stats_source=(
                        "Period HP/max hit/style plus Darkan convergence; hidden combat stats use a bounded "
                        "level-based resolver adapter"
                    ),
                ),
            ),
        ),
        _stage_req(
            10,
            "Use the Banshee voice on the mystic barrier.",
            SMOKING_KILLS_WIKI_SOURCE,
            consumed_inventory=(("Banshee voice", 1),),
            required_tools=(("Masked earmuffs", 1),),
            auto_actions=("Release the Banshee voice into the mystic barrier",),
        ),
        _stage_req(
            11,
            "Defeat the Banshee Mistress and survive the assassins she calls at half health.",
            (
                f"{SMOKING_KILLS_WIKI_SOURCE}; {SMOKING_KILLS_MISTRESS_SOURCE}; "
                f"{SMOKING_KILLS_MISTRESS_DARKAN_SOURCE}"
            ),
            required_tools=(("Masked earmuffs", 1),),
            combat_encounters=(
                _combat(
                    SMOKING_KILLS_ID,
                    "banshee_mistress",
                    "Banshee Mistress",
                    111,
                    (
                        f"{SMOKING_KILLS_WIKI_SOURCE}; {SMOKING_KILLS_MISTRESS_SOURCE}; "
                        f"{SMOKING_KILLS_MISTRESS_DARKAN_SOURCE}"
                    ),
                    (
                        "At half health the Mistress cries \"Minions, aid me!\" and her four level 141 "
                        "Insectoid Assassins join her. AnkiScape folds their level-141 ranged pressure, "
                        "up to 200 damage each, into this single boss battle; they are not separate kills."
                    ),
                    npc_stats=(
                        ("hitpoints", 2220),
                        ("attack", 111),
                        ("strength", 111),
                        ("defence", 111),
                        ("magic", 111),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 200),
                        ("attack_style", "magic"),
                        ("aggressiveness_type", "aggressive"),
                        ("minimum_player_combat", 85),
                    ),
                    npc_stats_source=(
                        "Period 2220 LP and mixed melee/Magic boss behavior with an explicitly collapsed "
                        "half-health assassin phase; hidden combat stats use a bounded level-based adapter"
                    ),
                ),
            ),
        ),
        _stage_req(
            12,
            "Report the Banshee Mistress's defeat to Sumona.",
            SMOKING_KILLS_WIKI_SOURCE,
            auto_actions=(
                "Hear Catolax's final message",
                "Return to Pollnivneach and report the victory to Sumona",
            ),
        ),
    ),
    "diamond_in_the_rough": (
        _stage_req(
            1,
            "Take the Kharid-ib's heavy container and leave Al Kharid with Ozan.",
            (
                f"{DIAMOND_IN_THE_ROUGH_WIKI_SOURCE}; "
                f"{DIAMOND_IN_THE_ROUGH_QUICK_GUIDE_SOURCE}; "
                f"{DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}"
            ),
            produced_inventory=(("Heavy weight", 1),),
            auto_actions=(
                "Receive Osman's rescue mission and collect the Heavy weight",
                "Leave the palace by Ozan's rooftop route and reach Shantay Pass",
            ),
        ),
        _stage_req(
            2,
            "Follow Het's sundial and survive the Apmeken bandit ambush.",
            (
                f"{DIAMOND_IN_THE_ROUGH_WIKI_SOURCE}; "
                f"{DIAMOND_IN_THE_ROUGH_QUICK_GUIDE_SOURCE}; "
                f"{DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}; {DARKAN_BEASTS_SOURCE}"
            ),
            required_inventory=(("Heavy weight", 1),),
            produced_inventory=(
                ("Sundial gnomon", 1),
                ("Waterskin (4)", 4),
            ),
            auto_actions=(
                "Accept Shantay's four waterskins and align Het's sundial",
                "Recover the Sundial gnomon from the final bandit",
            ),
            combat_encounters=(
                _combat(
                    "diamond_in_the_rough",
                    "bandit",
                    "Bandit (Diamond in the Rough)",
                    2,
                    (
                        "https://runescape.wiki/w/Bandit_(Diamond_in_the_Rough)?oldid=6343462; "
                        f"{DIAMOND_IN_THE_ROUGH_QUICK_GUIDE_SOURCE}; "
                        f"{DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}; {DARKAN_BEASTS_SOURCE}"
                    ),
                    "Five level-2 bandits and their king make up the six-enemy sundial ambush.",
                    quantity=5,
                    npc_stats=(
                        ("hitpoints", 200),
                        ("attack", 5),
                        ("strength", 1),
                        ("defence", 5),
                        ("magic", 5),
                        ("ranged", 5),
                    ),
                    npc_stats_source=(
                        "https://runescape.wiki/w/Bandit_(Diamond_in_the_Rough)?oldid=6343462; "
                        f"{DARKAN_BEASTS_SOURCE}:4953-4957; "
                        "Strength 1 is the AnkiScape minimum resolver adapter"
                    ),
                ),
                _combat(
                    "diamond_in_the_rough",
                    "bandit_king",
                    "Bandit king",
                    3,
                    (
                        "https://runescape.wiki/w/Bandit_king?oldid=6538856; "
                        f"{DIAMOND_IN_THE_ROUGH_QUICK_GUIDE_SOURCE}; "
                        f"{DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}; {DARKAN_BEASTS_SOURCE}"
                    ),
                    "Defeat the Bandit king before repairing Apmeken's sundial.",
                    npc_stats=(
                        ("hitpoints", 300),
                        ("attack", 5),
                        ("strength", 1),
                        ("defence", 5),
                        ("magic", 5),
                        ("ranged", 5),
                    ),
                    npc_stats_source=(
                        "https://runescape.wiki/w/Bandit_king?oldid=6538856; "
                        f"{DARKAN_BEASTS_SOURCE}:4952; "
                        "Strength 1 is the AnkiScape minimum resolver adapter"
                    ),
                ),
            ),
        ),
        _stage_req(
            3,
            "Escape the quicksand and recover the Kharid-ib from the Kalphite nursery.",
            (
                f"{DIAMOND_IN_THE_ROUGH_WIKI_SOURCE}; "
                f"{DIAMOND_IN_THE_ROUGH_QUICK_GUIDE_SOURCE}; "
                f"{DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}"
            ),
            consumed_inventory=(
                ("Heavy weight", 1),
                ("Sundial gnomon", 1),
            ),
            produced_inventory=(
                ("Sapphire", 1),
                ("Emerald", 1),
                ("Ruby", 1),
            ),
            auto_actions=(
                "Repair Apmeken's sundial and lose the Kharid-ib in the quicksand",
                "Find Crondis's gnomon beneath Ozan and follow the crocodile sunbeam",
                "Slice sparkling Dung kalphites until the sapphire, emerald, ruby, and Kharid-ib are recovered",
                "Align the nursery sundial with the scarab",
            ),
        ),
        _stage_req(
            4,
            "Defeat Apep and Heru, then rescue Prince Ali.",
            (
                f"{DIAMOND_IN_THE_ROUGH_WIKI_SOURCE}; "
                f"{DIAMOND_IN_THE_ROUGH_QUICK_GUIDE_SOURCE}; "
                f"{DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}; {DARKAN_BEASTS_SOURCE}"
            ),
            auto_actions=(
                "Move clear of Apep's Whirling Dervish and turn away from Heru's blinding shield",
                "Rescue Prince Ali and return to Osman",
            ),
            combat_encounters=(
                _combat(
                    "diamond_in_the_rough",
                    "apep",
                    "Apep",
                    5,
                    (
                        "https://runescape.wiki/w/Apep?oldid=6488383; "
                        f"{DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}; {DARKAN_BEASTS_SOURCE}"
                    ),
                    "Apep attacks first and uses Whirling Dervish before Heru joins the fight.",
                    npc_stats=(
                        ("hitpoints", 500),
                        ("attack", 5),
                        ("strength", 1),
                        ("defence", 5),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_stats_source=(
                        f"{DARKAN_BEASTS_SOURCE}:4958; "
                        "Strength 1 is the AnkiScape minimum resolver adapter"
                    ),
                ),
                _combat(
                    "diamond_in_the_rough",
                    "heru",
                    "Heru",
                    5,
                    (
                        "https://runescape.wiki/w/Heru?oldid=6471439; "
                        f"{DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}; {DARKAN_BEASTS_SOURCE}"
                    ),
                    "Heru attacks after Apep and can interrupt the player with his blinding shield.",
                    npc_stats=(
                        ("hitpoints", 500),
                        ("attack", 5),
                        ("strength", 1),
                        ("defence", 5),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_stats_source=(
                        "https://runescape.wiki/w/Heru?oldid=6471439; "
                        f"{DARKAN_BEASTS_SOURCE}:4949; "
                        "HP and resolver stats use the explicit equal-level Apep adapter"
                    ),
                ),
            ),
        ),
    ),
    "stolen_hearts": (
        _stage_req(
            1,
            "Join the Skulls and earn Khnum's trust.",
            f"{STOLEN_HEARTS_WIKI_SOURCE}; {STOLEN_HEARTS_QUICK_GUIDE_SOURCE}",
            auto_actions=(
                "Threaten the Skullery bouncer and enter the gang cellar",
                "Pass Khnum's recruitment questions",
            ),
        ),
        _stage_req(
            2,
            "Tail Khnum to Draynor jail and uncover the kidnapping plot.",
            f"{STOLEN_HEARTS_WIKI_SOURCE}; {STOLEN_HEARTS_QUICK_GUIDE_SOURCE}",
            auto_actions=(
                "Report the Skullery to Ozan and tail Khnum",
                "Interrogate Khnum with Ozan and Leela",
            ),
        ),
        _stage_req(
            3,
            "Confront Lady Keli and recover the ransom note.",
            (
                f"{STOLEN_HEARTS_WIKI_SOURCE}; {STOLEN_HEARTS_QUICK_GUIDE_SOURCE}; "
                f"{STOLEN_HEARTS_CACHE_SOURCE}; {DARKAN_BEASTS_SOURCE}"
            ),
            produced_inventory=(("Ransom note", 1),),
            auto_actions=("Confront Lady Keli near the Wizards' Tower bridge",),
            combat_encounters=(
                _combat(
                    "stolen_hearts",
                    "mercenary_joe",
                    "Mercenary Joe",
                    2,
                    (
                        f"{STOLEN_HEARTS_WIKI_SOURCE}; {STOLEN_HEARTS_CACHE_SOURCE}; "
                        f"{DARKAN_BEASTS_SOURCE}"
                    ),
                    "Defeat Mercenary Joe and two Skulls mercenaries before collecting the ransom note.",
                    npc_stats=(
                        ("hitpoints", 500),
                        ("attack", 1),
                        ("strength", 1),
                        ("defence", 1),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_stats_source=f"{DARKAN_BEASTS_SOURCE}:4959",
                ),
                _combat(
                    "stolen_hearts",
                    "skulls_mercenary",
                    "Skulls mercenary",
                    2,
                    (
                        f"{STOLEN_HEARTS_WIKI_SOURCE}; {STOLEN_HEARTS_CACHE_SOURCE}; "
                        f"{DARKAN_BEASTS_SOURCE}"
                    ),
                    "Defeat Mercenary Joe and two Skulls mercenaries before collecting the ransom note.",
                    quantity=2,
                    npc_stats=(
                        ("hitpoints", 400),
                        ("attack", 1),
                        ("strength", 1),
                        ("defence", 1),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_stats_source=f"{DARKAN_BEASTS_SOURCE}:4960-4961",
                ),
            ),
        ),
        _stage_req(
            4,
            "Carry the ransom warning to Al Kharid and cross the rooftops with Ozan.",
            f"{STOLEN_HEARTS_WIKI_SOURCE}; {STOLEN_HEARTS_QUICK_GUIDE_SOURCE}",
            required_inventory=(("Ransom note", 1),),
            produced_inventory=(("History of the Kharid-ib", 1),),
            auto_actions=(
                "Travel with Ozan to Al Kharid",
                "Cross the Al Kharid rooftops and enter the palace treasury",
                "Read the History of the Kharid-ib",
            ),
        ),
        _stage_req(
            5,
            "Solve Het's scales, take the Kharid-ib, and identify yourself to Osman.",
            f"{STOLEN_HEARTS_WIKI_SOURCE}; {STOLEN_HEARTS_QUICK_GUIDE_SOURCE}",
            consumed_inventory=(
                ("Ransom note", 1),
                ("History of the Kharid-ib", 1),
            ),
            auto_actions=(
                "Find the heavy weight in two weighings",
                "Take the Kharid-ib and give Leela's passphrase to Osman",
            ),
        ),
    ),
    COOKS_ASSISTANT_ID: (
        _stage_req(
            1,
            "Pick up the super large egg for the Duke's cake.",
            COOKS_ASSISTANT_LUMBRIDGE_COOK_SOURCE,
            produced_inventory=(("Super large egg", 1),),
        ),
        _stage_req(
            2,
            "Milk the prized dairy cow for top-quality milk.",
            COOKS_ASSISTANT_PRIZED_DAIRY_COW_SOURCE,
            required_inventory=(("Bucket", 1),),
            consumed_inventory=(("Bucket", 1),),
            produced_inventory=(("Top-quality milk", 1),),
        ),
        _stage_req(
            3,
            "Ask Millie to prepare extra fine flour and collect it from the flour bin.",
            f"{COOKS_ASSISTANT_MILLIE_MILLER_SOURCE}; {COOKS_ASSISTANT_FLOUR_BIN_SOURCE}",
            required_inventory=(("Empty pot", 1),),
            consumed_inventory=(("Empty pot", 1),),
            produced_inventory=(("Extra fine flour", 1),),
        ),
        _stage_req(
            4,
            "Give the Lumbridge cook the three special cake ingredients.",
            f"{COOKS_ASSISTANT_SOURCE_PATH}; {COOKS_ASSISTANT_LUMBRIDGE_COOK_SOURCE}",
            consumed_inventory=(("Top-quality milk", 1), ("Extra fine flour", 1), ("Super large egg", 1)),
        ),
    ),
    HOLY_GRAIL_ID: (
        _stage_req(
            1,
            "Ask Merlin about the Holy Grail.",
            f"{HOLY_GRAIL_KING_ARTHUR_SOURCE}; {HOLY_GRAIL_MERLIN_SOURCE}",
            auto_actions=("Ask Merlin about the Holy Grail",),
        ),
        _stage_req(
            2,
            "Ask the Entrana High Priest and crone about the Grail.",
            f"{HOLY_GRAIL_MERLIN_SOURCE}; {HOLY_GRAIL_ENTRANA_SOURCE}",
            auto_actions=(
                "Travel to Entrana",
                "Ask the Entrana High Priest and crone about the Grail",
            ),
        ),
        _stage_req(
            3,
            "Ask Sir Galahad for an artifact from the Fisher Realm.",
            f"{HOLY_GRAIL_ENTRANA_SOURCE}; {HOLY_GRAIL_GALAHAD_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Ask Sir Galahad for an artifact from the Fisher Realm",),
            produced_inventory=(("Holy table napkin", 1),),
        ),
        _stage_req(
            4,
            "Find the Magic whistles in Draynor Manor while carrying the Holy table napkin.",
            f"{HOLY_GRAIL_DARKAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_tools=(("Holy table napkin", 1),),
            auto_actions=(
                "Reach the Draynor Manor whistle room",
                "Find the Magic whistles in Draynor Manor",
            ),
            produced_inventory=(("Magic whistle", 2),),
        ),
        _stage_req(
            5,
            "Blow the Magic whistle at the six stone heads and defeat the Black Knight Titan with Excalibur.",
            f"{HOLY_GRAIL_DARKAN_SOURCE}; {HOLY_GRAIL_TITAN_SOURCE}; {HOLY_GRAIL_TITAN_NPC_SOURCE}",
            required_tools=(("Magic whistle", 1), ("Excalibur", 1)),
            auto_actions=(
                "Reach the Fisher Realm crossing at the six stone heads",
                "Blow the Magic whistle at the six stone heads",
            ),
            produced_inventory=(("Grail bell", 1),),
            combat_encounters=(
                _combat(
                    HOLY_GRAIL_ID,
                    "black_knight_titan_120",
                    "Black Knight Titan",
                    120,
                    HOLY_GRAIL_WIKI_SOURCE,
                    "Black Knight Titan (level 120), defeated only with Excalibur.",
                    npc_stats=(
                        ("hitpoints", 1420),
                        ("attack", 91),
                        ("strength", 100),
                        ("defence", 91),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 150),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "crush_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=HOLY_GRAIL_TITAN_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            6,
            "Ring the Grail bell and ask the Fisher King about Percival.",
            f"{HOLY_GRAIL_DARKAN_SOURCE}; {HOLY_GRAIL_FISHER_KING_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_tools=(("Grail bell", 1),),
            auto_actions=("Ring the Grail bell and ask the Fisher King about Percival",),
        ),
        _stage_req(
            7,
            "Ask King Arthur about Sir Percival and receive the Magic gold feather.",
            f"{HOLY_GRAIL_KING_ARTHUR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Ask King Arthur about Sir Percival",),
            produced_inventory=(("Magic gold feather", 1),),
        ),
        _stage_req(
            8,
            "Use the Magic gold feather to find Sir Percival, then show him a Magic whistle.",
            f"{HOLY_GRAIL_DARKAN_SOURCE}; {HOLY_GRAIL_PERCIVAL_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_tools=(("Magic gold feather", 1),),
            consumed_inventory=(("Magic whistle", 1),),
            auto_actions=(
                "Use the Magic gold feather to find Sir Percival",
                "Free Sir Percival from the sack",
                "Show Sir Percival the Magic whistle",
            ),
        ),
        _stage_req(
            9,
            "Take the Holy grail from the restored Fisher Realm.",
            f"{HOLY_GRAIL_DARKAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Take the Holy grail from the restored Fisher Realm",),
            produced_inventory=(("Holy grail", 1),),
        ),
        _stage_req(
            10,
            "Give the Holy grail to King Arthur.",
            f"{HOLY_GRAIL_KING_ARTHUR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Holy grail", 1),),
        ),
    ),
    TREE_GNOME_VILLAGE_ID: (
        _stage_req(
            1,
            "Reach Commander Montai on the battlefield.",
            f"{TREE_GNOME_BOLREN_SOURCE}; {TREE_GNOME_MONTAI_SOURCE}",
            auto_actions=(
                "Reach Commander Montai on the battlefield",
                "Ask Commander Montai how to help the gnome battlefield",
            ),
        ),
        _stage_req(
            2,
            "Give six normal logs to Commander Montai.",
            f"{TREE_GNOME_MONTAI_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Logs", 6),),
        ),
        _stage_req(
            3,
            "Ask Commander Montai about the tracker gnomes.",
            TREE_GNOME_MONTAI_SOURCE,
            auto_actions=("Ask Commander Montai about the tracker gnomes",),
        ),
        _stage_req(
            4,
            "Get all three tracker coordinates and fire the battlefield ballista.",
            (
                f"{TREE_GNOME_MONTAI_SOURCE}; {TREE_GNOME_TRACKER1_SOURCE}; {TREE_GNOME_TRACKER2_SOURCE}; "
                f"{TREE_GNOME_TRACKER3_SOURCE}; {TREE_GNOME_DARKAN_SOURCE}"
            ),
            auto_actions=(
                "Get the first tracker coordinate",
                "Get the second tracker coordinate",
                "Get the third tracker coordinate",
                "Fire the battlefield ballista at the Khazard stronghold",
            ),
        ),
        _stage_req(
            5,
            "Enter the Khazard stronghold and recover the first Orb of protection.",
            f"{TREE_GNOME_DARKAN_SOURCE}; {TREE_GNOME_MONTAI_SOURCE}; {TREE_GNOME_KHAZARD_COMMANDER_NPC_SOURCE}",
            auto_actions=(
                "Enter the Khazard stronghold through the broken wall",
                "Search the stronghold chest for the first Orb of protection",
            ),
            produced_inventory=(("Orb of protection", 1),),
            combat_encounters=(
                _combat(
                    TREE_GNOME_VILLAGE_ID,
                    "khazard_commander_48",
                    "Khazard commander",
                    48,
                    TREE_GNOME_WIKI_SOURCE,
                    "Two Khazard commanders (level 48) can block the first Orb of protection.",
                    quantity=2,
                    npc_stats=(
                        ("hitpoints", 220),
                        ("attack", 50),
                        ("strength", 45),
                        ("defence", 50),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 50),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "stab_att"),
                        ("aggressiveness_type", "passive"),
                    ),
                    npc_stats_source=TREE_GNOME_KHAZARD_COMMANDER_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            6,
            "Return the first Orb of protection to King Bolren and recover the remaining orbs from the Khazard warlord.",
            f"{TREE_GNOME_BOLREN_SOURCE}; {TREE_GNOME_DARKAN_SOURCE}; {TREE_GNOME_KHAZARD_WARLORD_NPC_SOURCE}",
            consumed_inventory=(("Orb of protection", 1),),
            auto_actions=("Return the first Orb of protection to King Bolren",),
            produced_inventory=(("Orbs of protection", 1),),
            combat_encounters=(
                _combat(
                    TREE_GNOME_VILLAGE_ID,
                    "khazard_warlord_112",
                    "Khazard warlord",
                    112,
                    TREE_GNOME_WIKI_SOURCE,
                    "Khazard warlord (level 112) holds the remaining Orbs of protection.",
                    npc_stats=(
                        ("hitpoints", 1690),
                        ("attack", 75),
                        ("strength", 78),
                        ("defence", 80),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 92),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "crush_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=TREE_GNOME_KHAZARD_WARLORD_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            7,
            "Return the remaining Orbs of protection to King Bolren.",
            f"{TREE_GNOME_BOLREN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Orbs of protection", 1),),
        ),
    ),
    FISHING_CONTEST_ID: (
        _stage_req(
            1,
            "Receive a fishing pass from Austri or Vestri.",
            f"{DARKAN_FISHING_CONTEST_SOURCE}; {DARKAN_FISHING_CONTEST_DWARF_BROTHERS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Receive a fishing pass from Austri or Vestri",),
            produced_inventory=(("Fishing pass", 1),),
        ),
        _stage_req(
            2,
            "Show the fishing pass and pay Bonzo's contest entry fee.",
            f"{DARKAN_FISHING_CONTEST_MORRIS_SOURCE}; {DARKAN_FISHING_CONTEST_BONZO_SOURCE}",
            required_inventory=(("Fishing pass", 1),),
            consumed_inventory=(("Coins", 5),),
        ),
        _stage_req(
            3,
            "Put garlic in the pipe beside the stranger's fishing spot.",
            f"{DARKAN_FISHING_CONTEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Garlic", 1),),
        ),
        _stage_req(
            4,
            "Catch the winning giant carp at Hemenster.",
            (
                f"{DARKAN_FISHING_CONTEST_SOURCE}; {DARKAN_FISHING_CONTEST_GRANDPA_JACK_SOURCE}; "
                f"{DARKAN_FISHING_SKILL_SOURCE}; {DARKAN_FISHING_FISH_SOURCE}; "
                f"{DARKAN_FISHING_SPOT_SOURCE}; {DARKAN_FISHING_CONTEST_WIKI_SOURCE}; "
                f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            consumed_inventory_options=((("Red vine worm", 1), ("Fishing bait", 1)),),
            produced_inventory=(("Raw giant carp", 1),),
            required_tools=(("Fishing rod", 1),),
            auto_actions=("Catch the winning giant carp",),
        ),
        _stage_req(
            5,
            "Claim the Hemenster fishing trophy from Bonzo.",
            f"{DARKAN_FISHING_CONTEST_BONZO_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Raw giant carp", 1),),
            produced_inventory=(("Fishing trophy", 1),),
        ),
        _stage_req(
            6,
            "Give the fishing trophy to Austri or Vestri.",
            f"{DARKAN_FISHING_CONTEST_DWARF_BROTHERS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Fishing trophy", 1),),
        ),
    ),
    GERTRUDES_CAT_ID: (
        _stage_req(
            1,
            "Speak to Shilop or Wilough in Varrock Marketplace.",
            DARKAN_GERTRUDES_CAT_GERTRUDE_SOURCE,
            auto_actions=("Speak to Shilop and Wilough in Varrock Marketplace",),
        ),
        _stage_req(
            2,
            "Pay Shilop and Wilough for Fluffs' location.",
            DARKAN_GERTRUDES_CAT_CHILDREN_SOURCE,
            consumed_inventory=(("Coins", 100),),
        ),
        _stage_req(
            3,
            "Find Fluffs in the Lumber Yard and learn she is thirsty.",
            DARKAN_GERTRUDES_CAT_SOURCE,
            auto_actions=(
                "Reach Fluffs in the Varrock Lumber Yard",
                "Try to pick up Fluffs in the Lumber Yard",
            ),
        ),
        _stage_req(
            4,
            "Give Fluffs a bucket of milk.",
            f"{DARKAN_GERTRUDES_CAT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Bucket of milk", 1),),
            produced_inventory=(("Bucket", 1),),
        ),
        _stage_req(
            5,
            "Season a raw sardine with doogle leaves.",
            f"{DARKAN_GERTRUDES_CAT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Raw sardine", 1), ("Doogle leaves", 1)),
            produced_inventory=(("Doogle sardine", 1),),
        ),
        _stage_req(
            6,
            "Feed Fluffs the doogle sardine.",
            f"{DARKAN_GERTRUDES_CAT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Doogle sardine", 1),),
        ),
        _stage_req(
            7,
            "Find Fluffs' kittens in the Lumber Yard.",
            f"{DARKAN_GERTRUDES_CAT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Search the shaking crate for Fluffs' kittens",),
            produced_inventory=(("Three little kittens", 1),),
        ),
        _stage_req(
            8,
            "Return Fluffs' kittens to her.",
            f"{DARKAN_GERTRUDES_CAT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Three little kittens", 1),),
        ),
        _stage_req(
            9,
            "Tell Gertrude that Fluffs and the kittens are safe.",
            DARKAN_GERTRUDES_CAT_GERTRUDE_SOURCE,
            auto_actions=("Tell Gertrude that Fluffs and the kittens are safe",),
        ),
    ),
    CLOCK_TOWER_ID: (
        _stage_req(
            1,
            "Find rat poison in the Clock Tower dungeon.",
            f"{DARKAN_CLOCK_TOWER_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Pick up rat poison in the Clock Tower dungeon",),
            produced_inventory=(("Rat poison", 1),),
        ),
        _stage_req(
            2,
            "Poison the Clock Tower dungeon rats to open the blocked door.",
            f"{DARKAN_CLOCK_TOWER_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Rat poison", 1),),
            auto_actions=("Poison the Clock Tower dungeon rats",),
        ),
        _stage_req(
            3,
            "Find the four Clock Tower cogs.",
            f"{DARKAN_CLOCK_TOWER_SOURCE}; {DARKAN_CLOCK_TOWER_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Find the white, black, blue, and red Clock Tower cogs",),
            produced_inventory=(("White cog", 1), ("Black cog", 1), ("Blue cog", 1), ("Red cog", 1)),
        ),
        _stage_req(
            4,
            "Place the four Clock Tower cogs on their matching spindles.",
            f"{DARKAN_CLOCK_TOWER_SOURCE}; {DARKAN_CLOCK_TOWER_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_inventory_options=(((("Bucket of water", 1), ("Ice gloves", 1)),)),
            consumed_inventory=(("White cog", 1), ("Black cog", 1), ("Blue cog", 1), ("Red cog", 1)),
            auto_actions=("Place the four Clock Tower cogs",),
        ),
        _stage_req(
            5,
            "Report the repaired clock to Brother Kojo.",
            DARKAN_CLOCK_TOWER_KOJO_SOURCE,
            auto_actions=("Report the repaired clock to Brother Kojo",),
        ),
    ),
    MONKS_FRIEND_ID: (
        _stage_req(
            1,
            "Recover the child's blanket from the thieves' hideout.",
            f"{DARKAN_MONKS_FRIEND_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            produced_inventory=(("Child's blanket", 1),),
            auto_actions=("Recover the child's blanket from the thieves' hideout",),
        ),
        _stage_req(
            2,
            "Return the child's blanket to Brother Omad.",
            f"{DARKAN_MONKS_FRIEND_SOURCE}; {DARKAN_MONKS_FRIEND_OMAD_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Child's blanket", 1),),
        ),
        _stage_req(
            3,
            "Ask Brother Omad about Brother Cedric and the party.",
            DARKAN_MONKS_FRIEND_OMAD_SOURCE,
            auto_actions=("Ask Brother Omad about Brother Cedric and the party",),
        ),
        _stage_req(
            4,
            "Give Brother Cedric a jug of water.",
            f"{DARKAN_MONKS_FRIEND_CEDRIC_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Jug of water", 1),),
        ),
        _stage_req(
            5,
            "Give Brother Cedric logs to repair his cart.",
            f"{DARKAN_MONKS_FRIEND_CEDRIC_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Logs", 1),),
        ),
        _stage_req(
            6,
            "Return to Brother Omad and join the birthday party.",
            DARKAN_MONKS_FRIEND_OMAD_SOURCE,
            auto_actions=("Return to Brother Omad and join the birthday party",),
        ),
    ),
    TRIBAL_TOTEM_ID: (
        _stage_req(
            1,
            "Ask Wizard Cromperty about his teleportation block.",
            f"{DARKAN_TRIBAL_TOTEM_KANGAI_SOURCE}; {DARKAN_TRIBAL_TOTEM_WIZARD_SOURCE}",
            auto_actions=("Ask Wizard Cromperty about the teleportation block",),
        ),
        _stage_req(
            2,
            "Take Lord Handelmort's address label from the RPDT crate.",
            f"{DARKAN_TRIBAL_TOTEM_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Reach the Ardougne RPDT depot", "Take Lord Handelmort's address label from the RPDT crate"),
            produced_inventory=(("Address label", 1),),
        ),
        _stage_req(
            3,
            "Switch the RPDT crate address labels and request delivery.",
            f"{DARKAN_TRIBAL_TOTEM_SOURCE}; {DARKAN_TRIBAL_TOTEM_RPDT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Address label", 1),),
            auto_actions=("Switch the RPDT crate address labels and request delivery",),
        ),
        _stage_req(
            4,
            "Teleport into Handelmort Mansion, bypass the traps, and loot the Rantuki totem.",
            f"{DARKAN_TRIBAL_TOTEM_SOURCE}; {DARKAN_TRIBAL_TOTEM_WIZARD_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=(
                "Teleport into Handelmort Mansion",
                "Disarm Handelmort's trapped stairs",
                "Solve Handelmort's lock with KURT",
                "Loot the Rantuki totem",
            ),
            produced_inventory=(("Totem", 1),),
        ),
        _stage_req(
            5,
            "Return the Rantuki totem to Kangai Mau.",
            f"{DARKAN_TRIBAL_TOTEM_KANGAI_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Totem", 1),),
        ),
    ),
    SCORPION_CATCHER_ID: (
        _stage_req(
            1,
            "Accept Thormac's scorpion cage.",
            f"{DARKAN_SCORPION_CATCHER_THORMAC_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_actions=("Accept Thormac's scorpion cage",),
            produced_inventory=(("Scorpion cage", 1),),
        ),
        _stage_req(
            2,
            "Ask the Seer for all three scorpion locations.",
            f"{DARKAN_SCORPION_CATCHER_SEER_SOURCE}; {DARKAN_SCORPION_CATCHER_KHAZ_SCORP_SOURCE}",
            required_actions=("Ask the Seer for all three scorpion locations",),
        ),
        _stage_req(
            3,
            "Catch the Taverley Dungeon scorpion.",
            (
                f"{DARKAN_SCORPION_CATCHER_SOURCE}; {DARKAN_SCORPION_CATCHER_KHAZ_SCORP_SOURCE}; "
                f"{DARKAN_SCORPION_CATCHER_JAILER_NPC_SOURCE}"
            ),
            required_tools=(("Scorpion cage", 1),),
            auto_actions=("Reach the Taverley Dungeon scorpion room",),
            required_actions=("Catch the Taverley Dungeon Kharid scorpion",),
            combat_encounters=(
                _combat(
                    SCORPION_CATCHER_ID,
                    "jailer",
                    "Jailer",
                    39,
                    f"{DARKAN_SCORPION_CATCHER_SOURCE}; {DARKAN_SCORPION_CATCHER_JAILER_NPC_SOURCE}",
                    "The Scorpion Catcher quest details require a level 39 jailer for the Taverley Dungeon key route.",
                    npc_stats=(
                        ("hitpoints", 470),
                        ("attack", 40),
                        ("strength", 40),
                        ("defence", 40),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 50),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "crush_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=DARKAN_SCORPION_CATCHER_JAILER_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            4,
            "Catch the Barbarian Outpost scorpion.",
            f"{DARKAN_SCORPION_CATCHER_SOURCE}; {DARKAN_SCORPION_CATCHER_KHAZ_SCORP_SOURCE}",
            required_tools=(("Scorpion cage", 1),),
            auto_actions=("Reach the Barbarian Outpost scorpion room",),
            required_actions=("Catch the Barbarian Outpost Kharid scorpion",),
        ),
        _stage_req(
            5,
            "Catch the Edgeville Monastery scorpion.",
            f"{DARKAN_SCORPION_CATCHER_SOURCE}; {DARKAN_SCORPION_CATCHER_KHAZ_SCORP_SOURCE}",
            required_tools=(("Scorpion cage", 1),),
            auto_actions=("Reach the Edgeville Monastery scorpion room",),
            required_actions=("Catch the Edgeville Monastery Kharid scorpion",),
        ),
        _stage_req(
            6,
            "Return the caged scorpions to Thormac.",
            f"{DARKAN_SCORPION_CATCHER_THORMAC_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Scorpion cage", 1),),
            required_actions=("Return the caged scorpions to Thormac",),
        ),
    ),
    SHEEP_HERDER_ID: (
        _stage_req(
            1,
            "Accept poisoned sheep feed from Councillor Halgrive.",
            f"{DARKAN_SHEEP_HERDER_COUNCILLOR_SOURCE}; {DARKAN_SHEEP_HERDER_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_actions=("Accept poisoned sheep feed from Councillor Halgrive",),
            produced_inventory=(("Sheep feed", 1),),
        ),
        _stage_req(
            2,
            "Buy protective clothing from Doctor Orbon.",
            f"{DARKAN_SHEEP_HERDER_DOCTOR_SOURCE}; {DARKAN_SHEEP_HERDER_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Coins", 100),),
            produced_inventory=(("Plague jacket", 1), ("Plague trousers", 1)),
        ),
        _stage_req(
            3,
            "Pick up the cattleprod from the Ardougne sheep enclosure.",
            (
                f"{DARKAN_SHEEP_HERDER_SOURCE}; {DARKAN_SHEEP_HERDER_FARMER_SOURCE}; "
                f"{DARKAN_SHEEP_HERDER_UTILS_SOURCE}; {DARKAN_SHEEP_HERDER_CONSTANTS_SOURCE}; "
                f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            auto_actions=("Reach the Ardougne sheep enclosure",),
            required_actions=("Pick up the cattleprod from the sheep enclosure barn",),
            produced_inventory=(("Cattleprod", 1),),
        ),
        _stage_req(
            4,
            "Herd and poison all four infected sheep.",
            (
                f"{DARKAN_SHEEP_HERDER_SOURCE}; {DARKAN_SHEEP_HERDER_FARMER_SOURCE}; "
                f"{DARKAN_SHEEP_HERDER_UTILS_SOURCE}; {DARKAN_SHEEP_HERDER_CONSTANTS_SOURCE}; "
                f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            required_inventory=(("Sheep feed", 1),),
            required_tools=(("Plague jacket", 1), ("Plague trousers", 1), ("Cattleprod", 1)),
            auto_actions=("Reach the Ardougne sheep enclosure",),
            required_actions=(
                "Herd and poison the red sheep",
                "Herd and poison the green sheep",
                "Herd and poison the blue sheep",
                "Herd and poison the yellow sheep",
            ),
            produced_inventory=(
                ("Red sheep bones", 1),
                ("Green sheep bones", 1),
                ("Blue sheep bones", 1),
                ("Yellow sheep bones", 1),
            ),
        ),
        _stage_req(
            5,
            "Incinerate the sheep bones and report all four infected sheep.",
            (
                f"{DARKAN_SHEEP_HERDER_SOURCE}; {DARKAN_SHEEP_HERDER_FARMER_SOURCE}; "
                f"{DARKAN_SHEEP_HERDER_UTILS_SOURCE}; {DARKAN_SHEEP_HERDER_CONSTANTS_SOURCE}; "
                f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            consumed_inventory=(
                ("Red sheep bones", 1),
                ("Green sheep bones", 1),
                ("Blue sheep bones", 1),
                ("Yellow sheep bones", 1),
            ),
            required_actions=(
                "Incinerate the red sheep bones",
                "Incinerate the green sheep bones",
                "Incinerate the blue sheep bones",
                "Incinerate the yellow sheep bones",
                "Report the incinerated sheep to Councillor Halgrive",
            ),
            auto_actions=("Reach the Ardougne sheep enclosure",),
        ),
    ),
    PLAGUE_CITY_ID: (
        _stage_req(
            1,
            "Give Alrena dwellberries so she can finish the gas mask.",
            (
                f"{DARKAN_PLAGUE_CITY_ALRENA_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; "
                f"{DARKAN_PLAGUE_CITY_PICTURE_SPAWN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            auto_actions=("Pick up the picture of Elena in Alrena's house",),
            consumed_inventory=(("Dwellberries", 1),),
            produced_inventory=(("Gas mask", 1), ("Picture of Elena", 1)),
        ),
        _stage_req(
            2,
            "Talk to Edmond with the gas mask and learn the sewer plan.",
            f"{DARKAN_PLAGUE_CITY_EDMOND_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}",
            required_inventory=(("Gas mask", 1),),
            auto_actions=("Talk to Edmond with the gas mask",),
        ),
        _stage_req(
            3,
            "Pour four buckets of water on the mud patch.",
            f"{DARKAN_PLAGUE_CITY_UTILS_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Bucket of water", 4),),
            produced_inventory=(("Bucket", 4),),
            auto_actions=("Soften Edmond's mud patch with four buckets of water",),
        ),
        _stage_req(
            4,
            "Dig through the softened mud patch into the sewers.",
            f"{DARKAN_PLAGUE_CITY_UTILS_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_tools=(("Spade", 1),),
            auto_actions=("Dig through Edmond's softened mud patch",),
        ),
        _stage_req(
            5,
            "Pull the sewer grill and learn that Edmond must help.",
            f"{DARKAN_PLAGUE_CITY_UTILS_SOURCE}; {DARKAN_PLAGUE_CITY_EDMOND_SOURCE}",
            auto_actions=("Pull the sewer grill", "Ask Edmond for help with the grill"),
        ),
        _stage_req(
            6,
            "Tie rope to the sewer grill.",
            f"{DARKAN_PLAGUE_CITY_UTILS_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Rope", 1),),
            auto_actions=("Tie rope to the sewer grill",),
        ),
        _stage_req(
            7,
            "Ask Edmond to pull the rope and remove the grill.",
            f"{DARKAN_PLAGUE_CITY_EDMOND_SOURCE}; {DARKAN_PLAGUE_CITY_CUTSCENE_SOURCE}",
            auto_actions=("Ask Edmond to pull the sewer grill rope",),
        ),
        _stage_req(
            8,
            "Wear the gas mask, enter West Ardougne through the sewer, and speak to Jethick.",
            f"{DARKAN_PLAGUE_CITY_UTILS_SOURCE}; {DARKAN_PLAGUE_CITY_JETHICK_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}",
            required_tools=(("Gas mask", 1),),
            auto_actions=(
                "Reach West Ardougne through the sewer pipe",
                "Speak to Jethick about Elena",
            ),
        ),
        _stage_req(
            9,
            "Show Jethick a picture of Elena and take the Rehnison book.",
            f"{DARKAN_PLAGUE_CITY_JETHICK_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_inventory=(("Picture of Elena", 1),),
            produced_inventory=(("Turnip growing for beginners", 1),),
            auto_actions=("Show Jethick the picture of Elena", "Agree to return Jethick's book"),
        ),
        _stage_req(
            10,
            "Return Jethick's book to Ted Rehnison.",
            f"{DARKAN_PLAGUE_CITY_REHNISON_DOOR_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}",
            consumed_inventory=(("Turnip growing for beginners", 1),),
            auto_actions=("Return Jethick's book to Ted Rehnison",),
        ),
        _stage_req(
            11,
            "Ask Martha Rehnison where Elena went.",
            f"{DARKAN_PLAGUE_CITY_MARTHA_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}",
            auto_actions=("Ask Martha Rehnison about Elena",),
        ),
        _stage_req(
            12,
            "Ask Milli about Elena and challenge the mourners at the prison house.",
            (
                f"{DARKAN_PLAGUE_CITY_MILLI_SOURCE}; {DARKAN_PLAGUE_CITY_PRISON_DOOR_SOURCE}; "
                f"{DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}"
            ),
            auto_actions=(
                "Ask Milli Rehnison where Elena was taken",
                "Ask the mourners for prison house clearance",
            ),
        ),
        _stage_req(
            13,
            "Convince the Clerk to let you speak to Bravek and take Bravek's scruffy note.",
            (
                f"{DARKAN_PLAGUE_CITY_CLERK_SOURCE}; {DARKAN_PLAGUE_CITY_BRAVEK_SOURCE}; "
                f"{DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            produced_inventory=(("Scruffy note", 1),),
            auto_actions=("Convince the Clerk to let you speak to Bravek", "Ask Bravek for his cure recipe"),
        ),
        _stage_req(
            14,
            "Mix Bravek's hangover cure.",
            f"{DARKAN_PLAGUE_CITY_SOURCE}; {DARKAN_PLAGUE_CITY_ALRENA_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Chocolate dust", 1), ("Bucket of milk", 1), ("Snape grass", 1)),
            produced_inventory=(("Hangover cure", 1),),
            required_tools=(("Pestle and mortar", 1),),
            auto_actions=("Mix chocolate dust with milk and snape grass",),
        ),
        _stage_req(
            15,
            "Give Bravek the hangover cure and obtain a warrant.",
            f"{DARKAN_PLAGUE_CITY_BRAVEK_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Hangover cure", 1),),
            produced_inventory=(("Warrant", 1),),
            auto_actions=("Give Bravek the hangover cure", "Ask Bravek for a prison house warrant"),
        ),
        _stage_req(
            16,
            "Use the warrant, find the small key, free Elena, and report back to Edmond.",
            (
                f"{DARKAN_PLAGUE_CITY_PRISON_DOOR_SOURCE}; {DARKAN_PLAGUE_CITY_UTILS_SOURCE}; "
                f"{DARKAN_PLAGUE_CITY_ELENA_DOOR_SOURCE}; {DARKAN_PLAGUE_CITY_ELENA_SOURCE}; "
                f"{DARKAN_PLAGUE_CITY_EDMOND_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; "
                f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            required_inventory=(("Warrant", 1),),
            produced_inventory=(("A small key", 1),),
            auto_actions=(
                "Enter the prison house with Bravek's warrant",
                "Search the barrel for the small key",
                "Unlock Elena's cell",
                "Free Elena and report to Edmond",
            ),
        ),
    ),
    BIOHAZARD_ID: (
        _stage_req(
            1,
            "Ask Jerico for a route back into West Ardougne.",
            f"{DARKAN_BIOHAZARD_ELENA_SOURCE}; {DARKAN_BIOHAZARD_JERICO_SOURCE}",
            auto_actions=("Ask Jerico about crossing the West Ardougne wall",),
        ),
        _stage_req(
            2,
            "Meet Omart at the south end of the West Ardougne wall.",
            f"{DARKAN_BIOHAZARD_JERICO_SOURCE}; {DARKAN_BIOHAZARD_OMART_SOURCE}",
            auto_actions=("Ask Omart about the rope ladder",),
        ),
        _stage_req(
            3,
            "Ask Jerico about distracting the watchtower mourners.",
            (
                f"{DARKAN_BIOHAZARD_JERICO_SOURCE}; {DARKAN_BIOHAZARD_UTILS_SOURCE}; "
                f"{DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            produced_inventory=(("Bird feed", 1), ("Pigeon cage", 1)),
            auto_actions=(
                "Ask Jerico about using messenger pigeons",
                "Search Jerico's cupboard for bird feed",
                "Take a pigeon cage from Jerico's house",
            ),
        ),
        _stage_req(
            4,
            "Use bird feed and Jerico's pigeons to distract the watchtower mourners.",
            (
                f"{DARKAN_BIOHAZARD_UTILS_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; "
                f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            consumed_inventory=(("Bird feed", 1),),
            required_tools=(("Pigeon cage", 1),),
            auto_actions=(
                "Reach Jerico's pigeon release tile",
                "Scatter bird feed on the watchtower fence",
                "Open the pigeon cage at Jerico's release tile",
            ),
        ),
        _stage_req(
            5,
            "Cross the West Ardougne wall with Omart and Kilron's rope ladder.",
            f"{DARKAN_BIOHAZARD_OMART_SOURCE}; {DARKAN_BIOHAZARD_KILRON_SOURCE}; {DARKAN_BIOHAZARD_UTILS_SOURCE}",
            auto_actions=(
                "Reach Omart by the south West Ardougne wall",
                "Cross the West Ardougne wall with Omart and Kilron",
            ),
        ),
        _stage_req(
            6,
            "Pick up a rotten apple from the Mourner HQ garden.",
            (
                f"{DARKAN_BIOHAZARD_UTILS_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; "
                f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            auto_actions=(
                "Reach the Mourner HQ garden in West Ardougne",
                "Pick up a rotten apple from the Mourner HQ garden",
            ),
            produced_inventory=(("Rotten apple", 1),),
        ),
        _stage_req(
            7,
            "Poison the Mourner HQ stew and take a doctors' gown from the nearby box.",
            (
                f"{DARKAN_BIOHAZARD_UTILS_SOURCE}; {DARKAN_BIOHAZARD_MOURNER_HQ_DOORS_SOURCE}; "
                f"{DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            consumed_inventory=(("Rotten apple", 1),),
            produced_inventory=(("Doctors' gown", 1),),
            auto_actions=(
                "Reach the Mourner HQ garden in West Ardougne",
                "Put the rotten apple in the Mourner HQ cauldron",
                "Search the box for a doctors' gown",
            ),
        ),
        _stage_req(
            8,
            "Enter Mourner HQ as a doctor, defeat the key mourner, and recover Elena's distillator.",
            (
                f"{DARKAN_BIOHAZARD_MOURNER_HQ_DOORS_SOURCE}; {DARKAN_BIOHAZARD_MOURNER_SOURCE}; "
                f"{DARKAN_BIOHAZARD_UTILS_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; "
                f"{DARKAN_BIOHAZARD_MOURNER_NPC_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            produced_inventory=(("Key", 1), ("Distillator", 1)),
            required_tools=(("Doctors' gown", 1),),
            auto_actions=(
                "Enter Mourner HQ wearing the doctors' gown",
                "Defeat and search the level 13 mourner",
                "Unlock the distillator cage with the key",
                "Search the crate for Elena's distillator",
            ),
            combat_encounters=(
                _combat(
                    BIOHAZARD_ID,
                    "mourner_13",
                    "Mourner",
                    13,
                    f"{DARKAN_BIOHAZARD_SOURCE}; {DARKAN_BIOHAZARD_MOURNER_SOURCE}; {DARKAN_BIOHAZARD_MOURNER_NPC_SOURCE}",
                    "The Biohazard quest details require a level 13 mourner in Mourner HQ.",
                    npc_stats=(
                        ("hitpoints", 190),
                        ("attack", 24),
                        ("strength", 24),
                        ("defence", 24),
                        ("magic", 1),
                        ("ranged", 0),
                    ),
                    npc_configs=(
                        ("max_hit", 20),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("aggressiveness_type", "passive"),
                    ),
                    npc_stats_source=DARKAN_BIOHAZARD_MOURNER_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            9,
            "Return Elena's distillator so she can prepare Guidor's vials and plague sample.",
            (
                f"{DARKAN_BIOHAZARD_ELENA_SOURCE}; {DARKAN_BIOHAZARD_UTILS_SOURCE}; "
                f"{DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            consumed_inventory=(("Distillator", 1),),
            produced_inventory=(
                ("Liquid honey", 1),
                ("Ethenea", 1),
                ("Sulphuric broline", 1),
                ("Plague sample", 1),
            ),
            auto_actions=("Return Elena's distillator",),
        ),
        _stage_req(
            10,
            "Ask the Rimmington chemist for touch paper without exposing the plague sample.",
            (
                f"{DARKAN_BIOHAZARD_CHEMIST_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; "
                f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            required_inventory=(
                ("Liquid honey", 1),
                ("Ethenea", 1),
                ("Sulphuric broline", 1),
                ("Plague sample", 1),
            ),
            produced_inventory=(("Touch paper", 1),),
            auto_actions=("Ask the Rimmington chemist for touch paper for Guidor",),
        ),
        _stage_req(
            11,
            "Smuggle the vials through the chemist's errand boys and give Guidor the full test set.",
            (
                f"{DARKAN_BIOHAZARD_RIMMINGTON_HOPS_SOURCE}; {DARKAN_BIOHAZARD_RIMMINGTON_DA_VINCI_SOURCE}; "
                f"{DARKAN_BIOHAZARD_RIMMINGTON_CHANCY_SOURCE}; {DARKAN_BIOHAZARD_VARROCK_HOPS_SOURCE}; "
                f"{DARKAN_BIOHAZARD_VARROCK_DA_VINCI_SOURCE}; {DARKAN_BIOHAZARD_VARROCK_CHANCY_SOURCE}; "
                f"{DARKAN_BIOHAZARD_GUIDOR_SOURCE}; {DARKAN_BIOHAZARD_GUIDOR_WIFE_SOURCE}; "
                f"{DARKAN_BIOHAZARD_GUIDOR_DOOR_SOURCE}; {DARKAN_BIOHAZARD_VARROCK_GATE_SOURCE}; "
                f"{DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            consumed_inventory=(
                ("Liquid honey", 1),
                ("Ethenea", 1),
                ("Sulphuric broline", 1),
                ("Plague sample", 1),
                ("Touch paper", 1),
            ),
            required_tools=(("Priest gown", 2),),
            auto_actions=(
                "Reach Guidor's house without Varrock guards confiscating the vials",
                "Give sulphuric broline to Hops",
                "Give ethenea to Da Vinci",
                "Give liquid honey to Chancy",
                "Collect the sulphuric broline from Hops in Varrock",
                "Collect the ethenea from Da Vinci in Varrock",
                "Collect the liquid honey from Chancy in Varrock",
                "Enter Guidor's room wearing priest gowns",
                "Give Guidor the vials, plague sample, and touch paper",
            ),
        ),
        _stage_req(
            12,
            "Tell Elena that Guidor found the plague sample harmless.",
            f"{DARKAN_BIOHAZARD_GUIDOR_SOURCE}; {DARKAN_BIOHAZARD_ELENA_SOURCE}",
            auto_actions=("Tell Elena that Guidor found no plague",),
        ),
        _stage_req(
            13,
            "Report Elena's news to King Lathas.",
            f"{DARKAN_BIOHAZARD_ELENA_SOURCE}; {DARKAN_BIOHAZARD_KING_SOURCE}",
            auto_actions=("Report the plague hoax to King Lathas",),
        ),
    ),
    WATERFALL_QUEST_ID: (
        _stage_req(
            1,
            "Find Hudon after speaking to Almera.",
            f"{DARKAN_WATERFALL_ALMERA_SOURCE}; {DARKAN_WATERFALL_HUDON_SOURCE}",
            auto_actions=("Speak to Hudon by the waterfall",),
        ),
        _stage_req(
            2,
            "Search for and read the Book on Baxtorian.",
            f"{DARKAN_WATERFALL_SOURCE}; {DARKAN_WATERFALL_BOOK_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            produced_inventory=(("Book on Baxtorian", 1),),
            auto_actions=("Search the Baxtorian bookcase", "Read the Book on Baxtorian"),
        ),
        _stage_req(
            3,
            "Free Golrie and receive Glarial's pebble.",
            f"{DARKAN_WATERFALL_SOURCE}; {DARKAN_WATERFALL_GOLRIE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            produced_inventory=(("Old key", 1), ("Glarial's pebble", 1)),
            auto_actions=(
                "Search the Tree Gnome Village crate for the old key",
                "Unlock Golrie's prison",
                "Reach Golrie under Tree Gnome Village",
            ),
        ),
        _stage_req(
            4,
            "Use Glarial's pebble to enter the tomb and recover Glarial's amulet and urn.",
            f"{DARKAN_WATERFALL_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_inventory=(("Glarial's pebble", 1),),
            produced_inventory=(("Large old key", 1), ("Glarial's amulet", 1), ("Glarial's urn", 1)),
            required_tools=(("Rope", 1),),
            auto_actions=(
                "Search the waterfall crate for the large old key",
                "Use Glarial's pebble on Glarial's tomb",
                "Search Glarial's tomb for the amulet and urn",
            ),
        ),
        _stage_req(
            5,
            "Place the runes and Glarial's amulet, then use Glarial's urn on the chalice.",
            f"{DARKAN_WATERFALL_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(
                ("Glarial's urn", 1),
                ("Water rune", 6),
                ("Air rune", 6),
                ("Earth rune", 6),
                ("Glarial's amulet", 1),
            ),
            required_tools=(("Rope", 1),),
            auto_actions=(
                "Place six water runes on the pillars",
                "Place six air runes on the pillars",
                "Place six earth runes on the pillars",
                "Place Glarial's amulet on Glarial's statue",
                "Use Glarial's urn on the chalice",
            ),
        ),
    ),
    DWARF_CANNON_ID: (
        _stage_req(
            1,
            "Accept replacement railings from Captain Lawgof.",
            f"{DARKAN_DWARF_CANNON_LAWGOF_SOURCE}; {DARKAN_DWARF_CANNON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Accept replacement railings from Captain Lawgof",),
            produced_inventory=(("Railing", 6),),
        ),
        _stage_req(
            2,
            "Repair the six broken railings around the Black Guard camp.",
            f"{DARKAN_DWARF_CANNON_SOURCE}; {DARKAN_DWARF_CANNON_LAWGOF_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Railing", 6),),
            required_tools=(("Hammer", 1),),
        ),
        _stage_req(
            3,
            "Report the repaired stockade to Captain Lawgof.",
            DARKAN_DWARF_CANNON_LAWGOF_SOURCE,
            auto_actions=("Report the repaired stockade to Captain Lawgof",),
        ),
        _stage_req(
            4,
            "Find Gilob's remains at the watchtower.",
            f"{DARKAN_DWARF_CANNON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Take Gilob's remains from the watchtower",),
            produced_inventory=(("Dwarf remains", 1),),
        ),
        _stage_req(
            5,
            "Return Gilob's remains to Captain Lawgof.",
            f"{DARKAN_DWARF_CANNON_SOURCE}; {DARKAN_DWARF_CANNON_LAWGOF_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Dwarf remains", 1),),
        ),
        _stage_req(
            6,
            "Find the goblin hideout south-east of the camp.",
            DARKAN_DWARF_CANNON_SOURCE,
            auto_actions=("Reach the Dwarf Cannon goblin hideout",),
        ),
        _stage_req(
            7,
            "Rescue Lollk from the goblin hideout.",
            f"{DARKAN_DWARF_CANNON_SOURCE}; {DARKAN_DWARF_CANNON_LOLLK_SOURCE}",
            auto_actions=("Rescue Lollk from the goblin hideout",),
        ),
        _stage_req(
            8,
            "Return to Captain Lawgof after rescuing Lollk.",
            DARKAN_DWARF_CANNON_LAWGOF_SOURCE,
            auto_actions=("Tell Captain Lawgof that Lollk is safe",),
            produced_inventory=(("Toolkit", 1),),
        ),
        _stage_req(
            9,
            "Repair the sabotaged cannon with Captain Lawgof's toolkit.",
            f"{DARKAN_DWARF_CANNON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_tools=(("Toolkit", 1),),
            auto_actions=("Repair the sabotaged cannon",),
        ),
        _stage_req(
            10,
            "Tell Captain Lawgof that the cannon is repaired.",
            DARKAN_DWARF_CANNON_LAWGOF_SOURCE,
            auto_actions=("Tell Captain Lawgof that the cannon is repaired",),
        ),
        _stage_req(
            11,
            "Speak to Nulodion for the ammo mould and notes.",
            f"{DARKAN_DWARF_CANNON_NULODION_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Speak to Nulodion about Captain Lawgof's cannon",),
            produced_inventory=(("Ammo mould", 1), ("Nulodion's notes", 1)),
        ),
        _stage_req(
            12,
            "Bring Captain Lawgof the ammo mould and notes.",
            f"{DARKAN_DWARF_CANNON_NULODION_SOURCE}; {DARKAN_DWARF_CANNON_LAWGOF_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Ammo mould", 1), ("Nulodion's notes", 1)),
        ),
        _stage_req(
            13,
            "Receive Captain Lawgof's recommendation to buy and use a multicannon.",
            DARKAN_DWARF_CANNON_LAWGOF_SOURCE,
            auto_actions=("Receive Captain Lawgof's cannon recommendation",),
        ),
    ),
    FIGHT_ARENA_ID: (
        _stage_req(
            1,
            "Borrow the Khazard disguise from the armour stand.",
            f"{DARKAN_FIGHT_ARENA_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            produced_inventory=(("Khazard helmet", 1), ("Khazard armour", 1)),
        ),
        _stage_req(
            2,
            "Wear the Khazard helmet and armour to enter the jail.",
            f"{DARKAN_FIGHT_ARENA_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_tools=(("Khazard helmet", 1), ("Khazard armour", 1)),
        ),
        _stage_req(
            3,
            "Talk to Jeremy and learn which lazy guard has the cell keys.",
            f"{DARKAN_FIGHT_ARENA_JEREMY_SOURCE}; {DARKAN_FIGHT_ARENA_SOURCE}",
            auto_actions=("Talk to Jeremy about the key holder",),
        ),
        _stage_req(
            4,
            "Buy a Khali brew from Angor for the lazy guard.",
            f"{DARKAN_FIGHT_ARENA_ANGOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Coins", 5),),
            produced_inventory=(("Khali brew", 1),),
        ),
        _stage_req(
            5,
            "Give the Khali brew to the lazy guard.",
            f"{DARKAN_FIGHT_ARENA_LAZY_GUARD_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Khali brew", 1),),
        ),
        _stage_req(
            6,
            "Steal the Khazard cell keys from the sleeping lazy guard.",
            f"{DARKAN_FIGHT_ARENA_LAZY_GUARD_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Steal the Khazard cell keys from the lazy guard",),
            produced_inventory=(("Khazard cell keys", 1),),
        ),
        _stage_req(
            7,
            "Use the Khazard cell keys on Jeremy's cell to begin the arena sequence.",
            f"{DARKAN_FIGHT_ARENA_SOURCE}; {DARKAN_FIGHT_ARENA_CUTSCENE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_tools=(("Khazard cell keys", 1),),
            auto_actions=("Use the Khazard cell keys on Jeremy's cell",),
        ),
        _stage_req(
            8,
            "Defeat the Khazard ogre threatening Sir Servil.",
            f"{DARKAN_FIGHT_ARENA_CUTSCENE_SOURCE}; {DARKAN_FIGHT_ARENA_KHAZARD_OGRE_NPC_SOURCE}; {FIGHT_ARENA_WIKI_SOURCE}",
            combat_encounters=(
                _combat(
                    FIGHT_ARENA_ID,
                    "khazard_ogre_63",
                    "Khazard ogre",
                    63,
                    f"{DARKAN_FIGHT_ARENA_CUTSCENE_SOURCE}; {DARKAN_FIGHT_ARENA_KHAZARD_OGRE_NPC_SOURCE}; {FIGHT_ARENA_WIKI_SOURCE}",
                    "Darkan's Fight Arena cutscene targets the Khazard ogre before Sir Servil is freed; the combatdef supplies hitpoints/max-hit only, so resolver stats remain incomplete.",
                    npc_stats=(("hitpoints", 600),),
                    npc_configs=(
                        ("max_hit", 1),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=DARKAN_FIGHT_ARENA_KHAZARD_OGRE_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            9,
            "Defeat General Khazard's Khazard scorpion.",
            f"{DARKAN_FIGHT_ARENA_CUTSCENE_SOURCE}; {DARKAN_FIGHT_ARENA_KHAZARD_SCORPION_NPC_SOURCE}; {FIGHT_ARENA_WIKI_SOURCE}",
            combat_encounters=(
                _combat(
                    FIGHT_ARENA_ID,
                    "khazard_scorpion_44",
                    "Khazard scorpion",
                    44,
                    (
                        f"{DARKAN_FIGHT_ARENA_CUTSCENE_SOURCE}; "
                        f"{DARKAN_FIGHT_ARENA_KHAZARD_SCORPION_NPC_SOURCE}; {FIGHT_ARENA_WIKI_SOURCE}"
                    ),
                    "Darkan's Fight Arena cutscene spawns the Khazard scorpion after the ogre; the combatdef supplies hitpoints/max-hit only, so resolver stats remain incomplete.",
                    npc_stats=(("hitpoints", 400),),
                    npc_configs=(
                        ("max_hit", 50),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=DARKAN_FIGHT_ARENA_KHAZARD_SCORPION_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            10,
            "Defeat Bouncer in the arena.",
            f"{DARKAN_FIGHT_ARENA_CUTSCENE_SOURCE}; {DARKAN_FIGHT_ARENA_BOUNCER_NPC_SOURCE}; {FIGHT_ARENA_WIKI_SOURCE}",
            combat_encounters=(
                _combat(
                    FIGHT_ARENA_ID,
                    "bouncer_137",
                    "Bouncer",
                    137,
                    f"{DARKAN_FIGHT_ARENA_CUTSCENE_SOURCE}; {DARKAN_FIGHT_ARENA_BOUNCER_NPC_SOURCE}; {FIGHT_ARENA_WIKI_SOURCE}",
                    "Darkan's Fight Arena cutscene requires Bouncer before the player may leave; General Khazard is optional afterward.",
                    npc_stats=(
                        ("hitpoints", 1160),
                        ("attack", 120),
                        ("strength", 120),
                        ("defence", 120),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 140),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "stab_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=DARKAN_FIGHT_ARENA_BOUNCER_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            11,
            "Leave the arena and return to Lady Servil for the reward.",
            f"{DARKAN_FIGHT_ARENA_CUTSCENE_SOURCE}; {DARKAN_FIGHT_ARENA_LADY_SOURCE}",
            auto_actions=("Return to Lady Servil for the reward",),
        ),
    ),
    DEMON_SLAYER_ID: (
        _stage_req(
            1,
            "Cross Gypsy Aris's palm with silver and accept the Delrith prophecy.",
            f"{DARKAN_DEMON_SLAYER_SOURCE}; {DARKAN_DEMON_SLAYER_GYPSY_SOURCE}",
            consumed_inventory=(("Coins", 1),),
        ),
        _stage_req(
            3,
            "Wash Sir Prysin's key from the drain into the sewers and retrieve it.",
            f"{DARKAN_DEMON_SLAYER_SOURCE}; {DARKAN_DEMON_SLAYER_SIR_PRYSIN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Bucket of water", 1),),
            produced_inventory=(("Bucket", 1), ("Silverlight key", 1)),
        ),
        _stage_req(
            4,
            "Give Wizard Traiborn twenty-five bones for the key ritual.",
            f"{DARKAN_DEMON_SLAYER_SOURCE}; {DARKAN_DEMON_SLAYER_TRAIBORN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Bones", 25),),
            produced_inventory=(("Silverlight key", 1),),
        ),
        _stage_req(
            5,
            "Convince Captain Rovin to hand over his Silverlight key.",
            f"{DARKAN_DEMON_SLAYER_SOURCE}; {DARKAN_DEMON_SLAYER_ROVIN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            produced_inventory=(("Silverlight key", 1),),
        ),
        _stage_req(
            6,
            "Give Sir Prysin all three Silverlight keys and receive Silverlight.",
            f"{DARKAN_DEMON_SLAYER_SOURCE}; {DARKAN_DEMON_SLAYER_SIR_PRYSIN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Silverlight key", 3),),
            produced_inventory=(("Silverlight", 1),),
        ),
        _stage_req(
            7,
            "Fight Delrith at the Dark Wizards' altar with Silverlight.",
            (
                f"{DARKAN_DEMON_SLAYER_SOURCE}; {DARKAN_DEMON_SLAYER_DELRITH_CONTROLLER_SOURCE}; "
                f"{DARKAN_DEMON_SLAYER_DELRITH_SOURCE}; {DARKAN_DEMON_SLAYER_DELRITH_NPC_SOURCE}"
            ),
            required_tools=(("Silverlight", 1),),
            combat_encounters=(
                _combat(
                    DEMON_SLAYER_ID,
                    "delrith_27",
                    "Delrith",
                    27,
                    (
                        f"{DARKAN_DEMON_SLAYER_SOURCE}; {DARKAN_DEMON_SLAYER_DELRITH_CONTROLLER_SOURCE}; "
                        f"{DARKAN_DEMON_SLAYER_DELRITH_SOURCE}; {DARKAN_DEMON_SLAYER_DELRITH_NPC_SOURCE}"
                    ),
                    (
                        "Darkan starts the Delrith controller only after Silverlight is obtained and "
                        "DelrithBoss prevents non-Silverlight damage; the controller also spawns "
                        "supporting Dark wizards, but the required quest kill is Delrith. The local "
                        "combatdef supplies Delrith's level 27 melee stats."
                    ),
                    npc_stats=(
                        ("hitpoints", 70),
                        ("attack", 11),
                        ("strength", 10),
                        ("defence", 5),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 30),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("aggressiveness_type", "passive"),
                    ),
                    npc_stats_source=DARKAN_DEMON_SLAYER_DELRITH_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            8,
            "Recite the incantation to banish Delrith.",
            f"{DARKAN_DEMON_SLAYER_GYPSY_SOURCE}; {DARKAN_DEMON_SLAYER_INCANTATION_SOURCE}",
            auto_actions=("Recite Aber, Gabindo, Purchai, Camerinthum, Carlem",),
        ),
    ),
    DRAGON_SLAYER_ID: (
        _stage_req(
            2,
            "Accept Oziach's challenge to slay Elvarg.",
            f"{DARKAN_DRAGON_SLAYER_SOURCE}; {DARKAN_DRAGON_SLAYER_OZIACH_SOURCE}",
            auto_actions=("Accept Oziach's dragon-slaying challenge",),
        ),
        _stage_req(
            3,
            "Finish the Guildmaster's Crandor briefing and receive Melzar's Maze key.",
            f"{DARKAN_DRAGON_SLAYER_SOURCE}; {DARKAN_DRAGON_SLAYER_GUILDMASTER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Complete the Guildmaster's Crandor briefing",),
            produced_inventory=(("Maze key", 1),),
        ),
        _stage_req(
            4,
            "Ask Duke Horacio for an anti-dragon shield before facing Elvarg.",
            (
                f"{DARKAN_DRAGON_SLAYER_SOURCE}; {DARKAN_DRAGON_SLAYER_GUILDMASTER_SOURCE}; "
                f"{DARKAN_LUMBRIDGE_DUKE_SOURCE}; {RUNE_MYSTERIES_DUKE_SOURCE_PATH}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            auto_actions=("Ask Duke Horacio for an anti-dragon shield",),
            produced_inventory=(("Anti-dragon shield", 1),),
        ),
        _stage_req(
            5,
            "Clear Melzar's Maze and search the final chest for a Crandor map piece.",
            (
                f"{DARKAN_DRAGON_SLAYER_SOURCE}; {DARKAN_DRAGON_SLAYER_MELZARS_MAZE_SOURCE}; "
                f"{DRAGON_SLAYER_2011SCAPE_MAZE_SPAWNS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            required_tools=(("Maze key", 1),),
            produced_inventory=(("Map part", 1),),
            combat_encounters=(
                _combat(
                    DRAGON_SLAYER_ID,
                    "zombie_rat_3",
                    "Zombie rat",
                    3,
                    (
                        f"{DARKAN_DRAGON_SLAYER_MELZARS_MAZE_SOURCE}; "
                        f"{DRAGON_SLAYER_2011SCAPE_MAZE_SPAWNS_SOURCE}; {DARKAN_DRAGON_SLAYER_ZOMBIE_RAT_NPC_SOURCE}"
                    ),
                    "Melzar's Maze gates the red key on zombie rat combat; the Darkan combatdef supplies the level 3 stats.",
                    npc_stats=(
                        ("hitpoints", 50),
                        ("attack", 2),
                        ("strength", 3),
                        ("defence", 2),
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
                    npc_stats_source=DARKAN_DRAGON_SLAYER_ZOMBIE_RAT_NPC_SOURCE,
                ),
                _combat(
                    DRAGON_SLAYER_ID,
                    "ghost_19",
                    "Ghost",
                    19,
                    f"{DARKAN_DRAGON_SLAYER_MELZARS_MAZE_SOURCE}; {DRAGON_SLAYER_2011SCAPE_GHOST_NPC_SOURCE}",
                    "The local 2011Scape ghost definition supplies the level 19 Maze ghost combat stats.",
                    npc_stats=(
                        ("hitpoints", 250),
                        ("attack", 13),
                        ("strength", 13),
                        ("defence", 18),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_bonuses=(
                        ("defenceStab", 5),
                        ("defenceSlash", 5),
                        ("defenceCrush", 5),
                        ("defenceMagic", -5),
                        ("defenceRanged", 5),
                    ),
                    npc_configs=(("attack_speed", 4), ("attack_style", "melee")),
                    npc_stats_source=DRAGON_SLAYER_2011SCAPE_GHOST_NPC_SOURCE,
                ),
                _combat(
                    DRAGON_SLAYER_ID,
                    "skeleton_22",
                    "Skeleton",
                    22,
                    f"{DARKAN_DRAGON_SLAYER_MELZARS_MAZE_SOURCE}; {DRAGON_SLAYER_2011SCAPE_SKELETON_NPC_SOURCE}",
                    "The local 2011Scape skeleton definition supplies the level 22 Maze skeleton combat stats.",
                    npc_stats=(
                        ("hitpoints", 290),
                        ("attack", 15),
                        ("strength", 18),
                        ("defence", 17),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_bonuses=(
                        ("defenceStab", 5),
                        ("defenceSlash", 5),
                        ("defenceCrush", -5),
                        ("defenceMagic", 0),
                        ("defenceRanged", 5),
                    ),
                    npc_configs=(("attack_speed", 4), ("attack_style", "melee")),
                    npc_stats_source=DRAGON_SLAYER_2011SCAPE_SKELETON_NPC_SOURCE,
                ),
                _combat(
                    DRAGON_SLAYER_ID,
                    "zombie_24",
                    "Zombie",
                    24,
                    f"{DARKAN_DRAGON_SLAYER_MELZARS_MAZE_SOURCE}; {DRAGON_SLAYER_2011SCAPE_ZOMBIE_NPC_SOURCE}",
                    "The local 2011Scape zombie definition supplies the level 24 Maze zombie combat stats.",
                    npc_stats=(
                        ("hitpoints", 300),
                        ("attack", 19),
                        ("strength", 21),
                        ("defence", 16),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_bonuses=(
                        ("attackStab", 5),
                        ("attackCrush", 7),
                        ("defenceStab", 9),
                        ("defenceSlash", 8),
                        ("defenceCrush", 12),
                        ("defenceMagic", 10),
                        ("defenceRanged", 11),
                    ),
                    npc_configs=(("attack_speed", 5), ("attack_style", "melee")),
                    npc_stats_source=DRAGON_SLAYER_2011SCAPE_ZOMBIE_NPC_SOURCE,
                ),
                _combat(
                    DRAGON_SLAYER_ID,
                    "melzar_the_mad_43",
                    "Melzar the Mad",
                    43,
                    f"{DARKAN_DRAGON_SLAYER_MELZARS_MAZE_SOURCE}; {DARKAN_DRAGON_SLAYER_MELZAR_NPC_SOURCE}",
                    "Melzar's Maze requires killing Melzar the Mad for the magenta key; the Darkan combatdef supplies the level 43 stats.",
                    npc_stats=(
                        ("hitpoints", 440),
                        ("attack", 37),
                        ("strength", 37),
                        ("defence", 34),
                        ("magic", 40),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 50),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "crush_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=DARKAN_DRAGON_SLAYER_MELZAR_NPC_SOURCE,
                ),
                _combat(
                    DRAGON_SLAYER_ID,
                    "lesser_demon_82",
                    "Lesser demon",
                    82,
                    f"{DARKAN_DRAGON_SLAYER_MELZARS_MAZE_SOURCE}; {DRAGON_SLAYER_2011SCAPE_LESSER_DEMON_NPC_SOURCE}",
                    "Melzar's Maze requires killing the lesser demon for the final key; local 2011Scape supplies the level 82 stats.",
                    npc_stats=(
                        ("hitpoints", 790),
                        ("attack", 68),
                        ("strength", 70),
                        ("defence", 71),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_bonuses=(
                        ("attackStab", 0),
                        ("attackCrush", 0),
                        ("defenceStab", 0),
                        ("defenceSlash", 0),
                        ("defenceCrush", 0),
                        ("defenceMagic", -10),
                        ("defenceRanged", 0),
                    ),
                    npc_configs=(("attack_speed", 4), ("attack_style", "melee"), ("attack_bonus", "slash_att")),
                    npc_stats_source=DRAGON_SLAYER_2011SCAPE_LESSER_DEMON_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            6,
            "Buy Wormbrain's Crandor map piece from Port Sarim jail.",
            (
                f"{DARKAN_DRAGON_SLAYER_SOURCE}; {DARKAN_DRAGON_SLAYER_WORMBRAIN_SOURCE}; "
                f"{DARKAN_DRAGON_SLAYER_WORMBRAIN_NPC_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            consumed_inventory=(("Coins", 10000),),
            produced_inventory=(("Map part", 1),),
        ),
        _stage_req(
            7,
            "Ask the Oracle how to reach Thalzar's map piece.",
            f"{DARKAN_DRAGON_SLAYER_SOURCE}; {DARKAN_DRAGON_SLAYER_ORACLE_SOURCE}",
            auto_actions=("Ask the Oracle about Thalzar's map piece",),
        ),
        _stage_req(
            8,
            "Open the magic door below Ice Mountain with the Oracle's four items.",
            (
                f"{DARKAN_DRAGON_SLAYER_SOURCE}; {DARKAN_DRAGON_SLAYER_ORACLE_SOURCE}; "
                f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}; {DRAGON_SLAYER_WIKI_SOURCE}"
            ),
            consumed_inventory=(("Wizard's mind bomb", 1), ("Silk", 1), ("Bowl (unfired)", 1)),
            consumed_inventory_options=((("Crayfish cage", 1), ("Lobster pot", 1)),),
            produced_inventory=(("Map part", 1),),
        ),
        _stage_req(
            9,
            "Combine the three Crandor map pieces.",
            f"{DARKAN_DRAGON_SLAYER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Map part", 3),),
            produced_inventory=(("Crandor map", 1),),
        ),
        _stage_req(
            10,
            "Buy the Lady Lumbridge from Klarense.",
            f"{DARKAN_DRAGON_SLAYER_SOURCE}; {DARKAN_DRAGON_SLAYER_KLARENSE_SOURCE}",
            consumed_inventory=(("Coins", 2000),),
        ),
        _stage_req(
            11,
            "Repair the Lady Lumbridge with three planks and ninety steel nails.",
            f"{DARKAN_DRAGON_SLAYER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Plank", 3), ("Steel nails", 90)),
            required_tools=(("Hammer", 1),),
        ),
        _stage_req(
            12,
            "Recruit Ned as captain and show him the completed Crandor map.",
            f"{DARKAN_DRAGON_SLAYER_SOURCE}; {DARKAN_DRAGON_SLAYER_NED_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Crandor map", 1),),
            auto_actions=("Recruit Ned as captain of the Lady Lumbridge",),
        ),
        _stage_req(
            13,
            "Sail to Crandor with Captain Ned.",
            f"{DARKAN_DRAGON_SLAYER_CAPTAIN_NED_SOURCE}; {DARKAN_DRAGON_SLAYER_BOAT_SCENE_SOURCE}",
            auto_actions=("Sail to Crandor with Captain Ned",),
        ),
        _stage_req(
            14,
            "Fight Elvarg on Crandor while carrying the anti-dragon shield.",
            (
                f"{DARKAN_DRAGON_SLAYER_SOURCE}; {DARKAN_DRAGON_SLAYER_ELVARG_SOURCE}; "
                f"{DARKAN_DRAGON_SLAYER_ELVARG_NPC_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            required_tools=(("Anti-dragon shield", 1),),
            produced_inventory=(("Elvarg's head", 1),),
            combat_encounters=(
                _combat(
                    DRAGON_SLAYER_ID,
                    "elvarg_83",
                    "Elvarg",
                    83,
                    f"{DARKAN_DRAGON_SLAYER_ELVARG_SOURCE}; {DARKAN_DRAGON_SLAYER_ELVARG_NPC_SOURCE}",
                    "Darkan's Elvarg boss adds Elvarg's head and moves Dragon Slayer to the report stage on death; the combatdef supplies Elvarg's level 83 stats.",
                    npc_stats=(
                        ("hitpoints", 800),
                        ("attack", 70),
                        ("strength", 70),
                        ("defence", 70),
                        ("magic", 70),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 100),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=DARKAN_DRAGON_SLAYER_ELVARG_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            15,
            "Report Elvarg's death to Oziach.",
            f"{DARKAN_DRAGON_SLAYER_SOURCE}; {DARKAN_DRAGON_SLAYER_OZIACH_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_inventory=(("Elvarg's head", 1),),
            auto_actions=("Report Elvarg's death to Oziach",),
        ),
    ),
    GOBLIN_DIPLOMACY_ID: (
        _stage_req(
            1,
            "Give the goblin generals orange goblin mail.",
            f"{DARKAN_GOBLIN_DIPLOMACY_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Orange goblin mail", 1),),
        ),
        _stage_req(
            2,
            "Give the goblin generals blue goblin mail.",
            f"{DARKAN_GOBLIN_DIPLOMACY_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Blue goblin mail", 1),),
        ),
        _stage_req(
            3,
            "Give the goblin generals regular brown goblin mail.",
            f"{DARKAN_GOBLIN_DIPLOMACY_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Goblin mail", 1),),
        ),
    ),
    ERNEST_THE_CHICKEN_ID: (
        _stage_req(
            1,
            "Find Professor Oddenstein and learn what happened to Ernest.",
            f"{DARKAN_ERNEST_SOURCE}; {DARKAN_ERNEST_ODDENSTEIN_SOURCE}",
            auto_actions=("Ask Professor Oddenstein about Ernest",),
        ),
        _stage_req(
            2,
            "Agree to retrieve Oddenstein's missing machine parts.",
            f"{DARKAN_ERNEST_ODDENSTEIN_SOURCE}",
            auto_actions=("Agree to retrieve Oddenstein's machine parts",),
        ),
        _stage_req(
            3,
            "Mix fish food with poison for the manor fountain.",
            f"{DARKAN_ERNEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Fish food", 1), ("Poison", 1)),
            produced_inventory=(("Poisoned fish food", 1),),
        ),
        _stage_req(
            4,
            "Use poisoned fish food on the fountain and recover the pressure gauge.",
            f"{DARKAN_ERNEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Poisoned fish food", 1),),
            produced_inventory=(("Pressure gauge", 1),),
        ),
        _stage_req(
            5,
            "Dig in the compost heap with a spade to find the grimy key.",
            f"{DARKAN_ERNEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_tools=(("Spade", 1),),
            produced_inventory=(("Grimy key", 1),),
        ),
        _stage_req(
            6,
            "Use the grimy key to reach and recover the rubber tube.",
            f"{DARKAN_ERNEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_tools=(("Grimy key", 1),),
            produced_inventory=(("Rubber tube", 1),),
        ),
        _stage_req(
            7,
            "Solve the basement lever puzzle and recover the oil can.",
            (
                f"{DARKAN_ERNEST_SOURCE}; {DARKAN_ERNEST_SOURCE_ROOT}/PuzzleRoom.java; "
                f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            auto_actions=("Solve the Draynor Manor basement lever puzzle",),
            produced_inventory=(("Oil can", 1),),
        ),
        _stage_req(
            8,
            "Give Oddenstein the pressure gauge, rubber tube, and oil can.",
            f"{DARKAN_ERNEST_ODDENSTEIN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Pressure gauge", 1), ("Rubber tube", 1), ("Oil can", 1)),
        ),
    ),
    BLACK_KNIGHTS_FORTRESS_ID: (
        _stage_req(
            1,
            "Enter the Black Knights' Fortress in disguise.",
            f"{DARKAN_BLACK_KNIGHTS_SOURCE}; {DARKAN_BLACK_KNIGHTS_SIR_AMIK_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_tools=(("Iron chainbody", 1), ("Bronze med helm", 1)),
            auto_actions=("Infiltrate the Black Knights' Fortress",),
        ),
        _stage_req(
            2,
            "Listen at the grill and learn about the invincibility potion.",
            DARKAN_BLACK_KNIGHTS_SOURCE,
            auto_actions=("Listen at the grill above the Black Knights' meeting",),
        ),
        _stage_req(
            3,
            "Drop a non-Draynor cabbage into the cauldron through the floor hole.",
            DARKAN_BLACK_KNIGHTS_SOURCE,
            consumed_inventory=(("Cabbage", 1),),
        ),
        _stage_req(
            4,
            "Report the ruined potion to Sir Amik Varze.",
            DARKAN_BLACK_KNIGHTS_SIR_AMIK_SOURCE,
            auto_actions=("Report the ruined potion to Sir Amik Varze",),
        ),
    ),
    VAMPYRE_SLAYER_ID: (
        _stage_req(
            1,
            "Speak to Dr Harlow at the Blue Moon Inn.",
            f"{VAMPYRE_SLAYER_SOURCE_PATH}; {VAMPYRE_SLAYER_DR_HARLOW_SOURCE_PATH}",
            auto_actions=("Speak to Dr Harlow at the Blue Moon Inn",),
        ),
        _stage_req(
            2,
            "Buy Dr Harlow a beer at the Blue Moon Inn and receive vampyre-slaying gear.",
            f"{VAMPYRE_SLAYER_SOURCE_PATH}; {VAMPYRE_SLAYER_DR_HARLOW_SOURCE_PATH}",
            produced_inventory=(("Stake", 1), ("Stake hammer", 1)),
            auto_actions=("Buy Dr Harlow a beer at the Blue Moon Inn",),
        ),
        _stage_req(
            3,
            "Open Count Draynor's coffin with a stake and stake hammer, then defeat him.",
            f"{VAMPYRE_SLAYER_SOURCE_PATH}; {VAMPYRE_SLAYER_MANOR_SOURCE_PATH}; {COUNT_DRAYNOR_NPC_SOURCE_PATH}",
            required_inventory=(("Stake", 1),),
            consumed_inventory=(("Stake", 1),),
            required_tools=(("Stake hammer", 1),),
            combat_encounters=(
                _combat(
                    VAMPYRE_SLAYER_ID,
                    "count_draynor_37",
                    "Count Draynor",
                    37,
                    f"{VAMPYRE_SLAYER_SOURCE_PATH}; {VAMPYRE_SLAYER_MANOR_SOURCE_PATH}; {COUNT_DRAYNOR_NPC_SOURCE_PATH}",
                    "2011Scape removes the stake when the coffin is opened, spawns Count Draynor, and treats garlic as an optional stat weakening item.",
                    npc_stats=(
                        ("hitpoints", 350),
                        ("attack", 30),
                        ("strength", 25),
                        ("defence", 30),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_bonuses=(
                        ("defenceStab", 2),
                        ("defenceSlash", 1),
                        ("defenceCrush", 3),
                        ("defenceMagic", 0),
                        ("defenceRanged", 0),
                    ),
                    npc_configs=(("attack_speed", 4), ("attack_style", "melee")),
                    npc_stats_source=COUNT_DRAYNOR_NPC_SOURCE_PATH,
                ),
            ),
        ),
        _stage_req(
            4,
            "Tell Morgan that Count Draynor is dead.",
            f"{VAMPYRE_SLAYER_SOURCE_PATH}; {VAMPYRE_SLAYER_MORGAN_SOURCE_PATH}; {COUNT_DRAYNOR_NPC_SOURCE_PATH}",
            auto_actions=("Tell Morgan that Count Draynor is dead",),
        ),
    ),
    THE_RESTLESS_GHOST_ID: (
        _stage_req(
            1,
            "Receive the ghostspeak amulet from Father Urhney.",
            f"{RESTLESS_GHOST_SOURCE_PATH}; {RESTLESS_GHOST_FATHER_URHNEY_SOURCE_PATH}",
            auto_actions=("Receive the ghostspeak amulet from Father Urhney",),
            produced_inventory=(("Ghostspeak amulet", 1),),
        ),
        _stage_req(
            2,
            "Speak to the restless ghost while wearing the ghostspeak amulet.",
            f"{RESTLESS_GHOST_SOURCE_PATH}; {RESTLESS_GHOST_DIALOGUE_SOURCE_PATH}",
            required_inventory=(("Ghostspeak amulet", 1),),
            auto_actions=("Speak to the restless ghost",),
        ),
        _stage_req(
            3,
            "Search the Lumbridge Swamp mining spot for the muddy skull.",
            f"{RESTLESS_GHOST_SOURCE_PATH}; {RESTLESS_GHOST_SKULL_SOURCE_PATH}",
            auto_actions=("Search the mining spot for the ghost's skull",),
            produced_inventory=(("Muddy skull", 1),),
        ),
        _stage_req(
            4,
            "Defeat the skeleton warlock and return the muddy skull to the ghost's coffin.",
            (
                f"{RESTLESS_GHOST_SOURCE_PATH}; {RESTLESS_GHOST_SKULL_SOURCE_PATH}; "
                f"{RESTLESS_GHOST_COFFIN_SOURCE_PATH}; {RESTLESS_GHOST_SKELETON_WARLOCK_NPC_SOURCE_PATH}"
            ),
            required_inventory=(("Muddy skull", 1),),
            consumed_inventory=(("Muddy skull", 1),),
            auto_actions=("Return the muddy skull to the ghost's coffin",),
            combat_encounters=(
                _combat(
                    THE_RESTLESS_GHOST_ID,
                    "skeleton_warlock",
                    "Skeleton warlock",
                    11,
                    (
                        f"{RESTLESS_GHOST_SOURCE_PATH}; {RESTLESS_GHOST_SKULL_SOURCE_PATH}; "
                        f"{RESTLESS_GHOST_SKELETON_WARLOCK_NPC_SOURCE_PATH}"
                    ),
                    (
                        "The Lumbridge skull object gives the muddy skull and spawns "
                        "Npcs.SKELETON_WARLOCK; the local combat definition supplies "
                        "the magic-style battle stats."
                    ),
                    npc_stats=(
                        ("hitpoints", 180),
                        ("attack", 1),
                        ("strength", 1),
                        ("defence", 1),
                        ("magic", 8),
                    ),
                    npc_bonuses=(
                        ("attackStab", 0),
                        ("attackCrush", 0),
                        ("defenceStab", 0),
                        ("defenceSlash", 0),
                        ("defenceCrush", 0),
                        ("defenceMagic", 5),
                        ("defenceRanged", 0),
                    ),
                    npc_configs=(("attack_speed", 4), ("attack_style", "magic")),
                    npc_stats_source=RESTLESS_GHOST_SKELETON_WARLOCK_NPC_SOURCE_PATH,
                ),
            ),
        ),
    ),
    IMP_CATCHER_ID: (
        _stage_req(
            1,
            "Return Wizard Mizgog's four beads.",
            f"{IMP_CATCHER_SOURCE_PATH}; {IMP_CATCHER_MIZGOG_SOURCE_PATH}",
            consumed_inventory=(("Black bead", 1), ("Red bead", 1), ("White bead", 1), ("Yellow bead", 1)),
        ),
    ),
    PIRATES_TREASURE_ID: (
        _stage_req(
            1,
            "Give Redbeard Frank smuggled Karamja rum.",
            f"{PIRATES_TREASURE_SOURCE_PATH}; {PIRATES_TREASURE_REDBEARD_SOURCE_PATH}",
            consumed_inventory=(("Karamja rum", 1),),
            produced_inventory=(("Chest key", 1),),
            auto_actions=("Smuggle Karamja rum off Karamja",),
        ),
        _stage_req(
            2,
            "Open One-Eyed Hector's chest in the Blue Moon Inn.",
            f"{PIRATES_TREASURE_SOURCE_PATH}; {PIRATES_TREASURE_CHEST_SOURCE_PATH}",
            consumed_inventory=(("Chest key", 1),),
            produced_inventory=(("Pirate message", 1),),
            auto_actions=("Open One-Eyed Hector's chest at the Blue Moon Inn",),
        ),
        _stage_req(
            3,
            "Read the pirate message and dig in Falador Park.",
            f"{PIRATES_TREASURE_SOURCE_PATH}; {PIRATES_TREASURE_CHEST_SOURCE_PATH}",
            required_inventory=(("Pirate message", 1),),
            required_tools=(("Spade", 1),),
            auto_actions=("Read the pirate message and dig in Falador Park",),
        ),
    ),
    DRUIDIC_RITUAL_ID: (
        _stage_req(
            1,
            "Speak to Sanfew about the ritual ingredients.",
            f"{DRUIDIC_RITUAL_SOURCE_PATH}; {DRUIDIC_RITUAL_SANFEW_SOURCE_PATH}",
            auto_actions=("Speak to Sanfew about the ritual ingredients",),
        ),
        _stage_req(
            2,
            "Dip each raw meat in the Cauldron of Thunder.",
            f"{DRUIDIC_RITUAL_SOURCE_PATH}; {DRUIDIC_RITUAL_SANFEW_SOURCE_PATH}; {DRUIDIC_RITUAL_CAULDRON_SOURCE_PATH}",
            consumed_inventory=(
                ("Raw bear meat", 1),
                ("Raw rat meat", 1),
                ("Raw beef", 1),
                ("Raw chicken", 1),
            ),
            produced_inventory=(
                ("Enchanted bear meat", 1),
                ("Enchanted rat meat", 1),
                ("Enchanted beef", 1),
                ("Enchanted chicken", 1),
            ),
            auto_actions=("Dip the raw meats in the Cauldron of Thunder",),
        ),
        _stage_req(
            3,
            "Give Sanfew the enchanted meats and return to Kaqemeex.",
            f"{DRUIDIC_RITUAL_SOURCE_PATH}; {DRUIDIC_RITUAL_SANFEW_SOURCE_PATH}; {DRUIDIC_RITUAL_KAQEMEEX_SOURCE_PATH}",
            consumed_inventory=(
                ("Enchanted bear meat", 1),
                ("Enchanted rat meat", 1),
                ("Enchanted beef", 1),
                ("Enchanted chicken", 1),
            ),
            auto_actions=("Give Sanfew the enchanted meats and return to Kaqemeex",),
        ),
    ),
    RUNE_MYSTERIES_ID: (
        _stage_req(
            1,
            "Deliver the strange talisman to Sedridor and receive his research package.",
            f"{RUNEMYSTERIES_SOURCE_PATH}; {RUNE_MYSTERIES_DUKE_SOURCE_PATH}; {RUNE_MYSTERIES_SEDRIDOR_SOURCE_PATH}",
            consumed_inventory=(("Air talisman", 1),),
            produced_inventory=(("Research package", 1),),
            auto_actions=("Deliver the strange talisman to Sedridor",),
        ),
        _stage_req(
            3,
            "Deliver Sedridor's package to Aubury and receive his research notes.",
            f"{RUNEMYSTERIES_SOURCE_PATH}; {RUNE_MYSTERIES_SEDRIDOR_SOURCE_PATH}; {RUNE_MYSTERIES_AUBURY_SOURCE_PATH}",
            consumed_inventory=(("Research package", 1),),
            produced_inventory=(("Research notes", 1),),
            auto_actions=("Deliver Sedridor's package to Aubury",),
        ),
        _stage_req(
            5,
            "Return Aubury's research notes to Sedridor.",
            f"{RUNEMYSTERIES_SOURCE_PATH}; {RUNE_MYSTERIES_SEDRIDOR_SOURCE_PATH}; {RUNE_MYSTERIES_AUBURY_SOURCE_PATH}",
            consumed_inventory=(("Research notes", 1),),
            auto_actions=("Return Aubury's research notes to Sedridor",),
        ),
    ),
    PRIEST_IN_PERIL_ID: (
        _stage_req(
            1,
            "Speak through the locked Paterdomus temple door.",
            f"{PRIEST_IN_PERIL_QUEST_SOURCE_PATH}; {PRIEST_IN_PERIL_DARKAN_SOURCE}",
            auto_actions=("Speak through the Paterdomus temple door",),
        ),
        _stage_req(
            2,
            "Defeat the Temple guardian dog; Magic cannot damage it.",
            f"{PRIEST_IN_PERIL_QUEST_SOURCE_PATH}; {PRIEST_IN_PERIL_DARKAN_CERBERUS_SOURCE}; {PRIEST_IN_PERIL_CERBERUS_NPC_SOURCE}",
            combat_encounters=(
                _combat(
                    PRIEST_IN_PERIL_ID,
                    "temple_guardian_dog_30",
                    "Temple guardian dog",
                    30,
                    f"{PRIEST_IN_PERIL_QUEST_SOURCE_PATH}; {PRIEST_IN_PERIL_DARKAN_CERBERUS_SOURCE}; {PRIEST_IN_PERIL_CERBERUS_NPC_SOURCE}",
                    "2011Scape names a level 30 Temple guardian dog and forbids Magic; Darkan's Cerberus NPC zeroes magic hits and advances Priest in Peril on death.",
                    npc_stats=(
                        ("hitpoints", 450),
                        ("attack", 0),
                        ("strength", 0),
                        ("defence", 0),
                        ("magic", 0),
                        ("ranged", 0),
                    ),
                    npc_configs=(
                        ("max_hit", 30),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "stab_att"),
                        ("aggressiveness_type", "passive"),
                        ("magic_damage_immune", True),
                    ),
                    npc_stats_source=PRIEST_IN_PERIL_CERBERUS_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            3,
            "Report the dead guard dog to King Roald.",
            f"{PRIEST_IN_PERIL_QUEST_SOURCE_PATH}; {PRIEST_IN_PERIL_DARKAN_SOURCE}",
            auto_actions=("Report the dead guard dog to King Roald",),
        ),
        _stage_req(
            4,
            "Return to Paterdomus and find Drezel imprisoned upstairs.",
            f"{PRIEST_IN_PERIL_QUEST_SOURCE_PATH}; {PRIEST_IN_PERIL_DARKAN_DREZEL_JAIL_SOURCE}",
            auto_actions=("Find Drezel imprisoned in the Paterdomus cell",),
        ),
        _stage_req(
            5,
            "Defeat a Monk of Zamorak to obtain the monument key.",
            f"{PRIEST_IN_PERIL_SOURCE}; {PRIEST_IN_PERIL_DARKAN_SOURCE}; {PRIEST_IN_PERIL_MONK_OF_ZAMORAK_NPC_SOURCE}",
            combat_encounters=(
                _combat(
                    PRIEST_IN_PERIL_ID,
                    "monk_of_zamorak_30",
                    "Monk of Zamorak",
                    30,
                    f"{PRIEST_IN_PERIL_SOURCE}; {PRIEST_IN_PERIL_DARKAN_SOURCE}; {PRIEST_IN_PERIL_MONK_OF_ZAMORAK_NPC_SOURCE}",
                    "Darkan Priest in Peril drops the key from Paterdomus Zamorak monk NPC ids 1044-1046; the level 30 id 1046 combatdef supplies the stats.",
                ),
            ),
        ),
        _stage_req(
            6,
            "Swap the golden key at the monument and unlock Drezel's cell.",
            f"{PRIEST_IN_PERIL_DARKAN_SOURCE}; {PRIEST_IN_PERIL_DARKAN_DREZEL_JAIL_SOURCE}",
            auto_actions=("Swap the golden key at the Paterdomus monument", "Unlock Drezel's cell"),
        ),
        _stage_req(
            7,
            "Bless Salve water in a bucket and pour it over the vampire coffin.",
            f"{PRIEST_IN_PERIL_QUEST_SOURCE_PATH}; {PRIEST_IN_PERIL_DARKAN_SOURCE}; {PRIEST_IN_PERIL_DARKAN_DREZEL_JAIL_SOURCE}",
            required_inventory=(("Bucket", 1),),
            auto_actions=("Bless Salve water with Drezel", "Pour blessed Salve water over the vampire coffin"),
        ),
        _stage_req(
            8,
            "Give Drezel essence to purify the River Salve.",
            f"{PRIEST_IN_PERIL_QUEST_SOURCE_PATH}; {PRIEST_IN_PERIL_DARKAN_DREZEL_MAUSOLEUM_SOURCE}",
            consumed_inventory_options=((("Rune essence", 50), ("Pure essence", 25)),),
        ),
    ),
    A_SOULS_BANE_ID: (
        _stage_req(
            1,
            "Bring a rope and enter Tolna's rift.",
            f"{A_SOULS_BANE_WIKI_SOURCE}; {A_SOULS_BANE_DARKAN_QUICK_GUIDE_SOURCE}",
            required_inventory=(("Rope", 1),),
        ),
        _stage_req(
            2,
            "Fill the rage meter with the correct anger weapon before leaving the rage room.",
            f"{A_SOULS_BANE_WIKI_SOURCE}; {A_SOULS_BANE_DARKAN_QUICK_GUIDE_SOURCE}",
            auto_actions=("Fill the rage meter with an anger weapon",),
        ),
        _stage_req(
            3,
            "Clear the fear, confusion, and hopelessness rooms.",
            f"{A_SOULS_BANE_WIKI_SOURCE}; {A_SOULS_BANE_DARKAN_QUICK_GUIDE_SOURCE}; {DARKAN_NPC_LIST_SOURCE}",
            combat_encounters=(
                _combat(
                    A_SOULS_BANE_ID,
                    "fear_reaper_42",
                    "Fear reaper",
                    42,
                    f"{A_SOULS_BANE_DARKAN_QUICK_GUIDE_SOURCE}; {DARKAN_NPC_LIST_SOURCE}; {A_SOULS_BANE_FEAR_REAPER_NPC_SOURCE}",
                    "Darkan quick guide says to kill five fear reapers; Darkan NPC id 3649 supplies the level 42 Fear reaper stats.",
                    quantity=5,
                    npc_stats=(
                        ("hitpoints", 570),
                        ("attack", 39),
                        ("strength", 41),
                        ("defence", 40),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 60),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "slash_att"),
                        ("aggressiveness_type", "passive"),
                    ),
                    npc_stats_source=A_SOULS_BANE_FEAR_REAPER_NPC_SOURCE,
                ),
                _combat(
                    A_SOULS_BANE_ID,
                    "confusion_beast_43",
                    "Confusion beast",
                    43,
                    f"{A_SOULS_BANE_DARKAN_QUICK_GUIDE_SOURCE}; {DARKAN_NPC_LIST_SOURCE}; {A_SOULS_BANE_CONFUSION_BEAST_NPC_SOURCE}",
                    "Darkan quick guide says the real Confusion beast must be killed five times; Darkan NPC ids 3650-3654 supply level 43 stats.",
                    quantity=5,
                    npc_stats=(
                        ("hitpoints", 640),
                        ("attack", 42),
                        ("strength", 41),
                        ("defence", 40),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 50),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "slash_att"),
                        ("aggressiveness_type", "passive"),
                    ),
                    npc_stats_source=A_SOULS_BANE_CONFUSION_BEAST_NPC_SOURCE,
                ),
                _combat(
                    A_SOULS_BANE_ID,
                    "hopeless_creature_40",
                    "Hopeless creature",
                    40,
                    f"{A_SOULS_BANE_DARKAN_QUICK_GUIDE_SOURCE}; {DARKAN_NPC_LIST_SOURCE}; {A_SOULS_BANE_HOPELESS_CREATURE_NPC_SOURCE}",
                    "Darkan quick guide says Hopeless creatures have three forms; Darkan NPC ids 3655-3657 supply level 40 form stats.",
                    quantity=3,
                    npc_stats=(
                        ("hitpoints", 1),
                        ("attack", 38),
                        ("strength", 36),
                        ("defence", 39),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 1),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "stab_att"),
                        ("aggressiveness_type", "passive"),
                    ),
                    npc_stats_source=A_SOULS_BANE_HOPELESS_CREATURE_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            4,
            "Defeat all three Tolna heads before speaking to Tolna on the surface.",
            f"{A_SOULS_BANE_WIKI_SOURCE}; {A_SOULS_BANE_DARKAN_QUICK_GUIDE_SOURCE}; {DARKAN_NPC_LIST_SOURCE}",
            combat_encounters=(
                _combat(
                    A_SOULS_BANE_ID,
                    "tolna_head_46",
                    "Tolna head",
                    46,
                    f"{A_SOULS_BANE_DARKAN_QUICK_GUIDE_SOURCE}; {DARKAN_NPC_LIST_SOURCE}; {A_SOULS_BANE_TOLNA_NPC_SOURCE}",
                    "Darkan quick guide says all three Tolna heads must be killed; Darkan NPC ids 3658-3660 list Tolna level 46 and the Tolna combatdef supplies stats.",
                    quantity=3,
                    npc_stats=(
                        ("hitpoints", 450),
                        ("attack", 42),
                        ("strength", 41),
                        ("defence", 40),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 50),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "stab_att"),
                        ("aggressiveness_type", "passive"),
                    ),
                    npc_stats_source=A_SOULS_BANE_TOLNA_NPC_SOURCE,
                ),
            ),
        ),
    ),
    WITCHS_HOUSE_ID: (
        _stage_req(
            1,
            "Search the potted plant outside the Witch's house for the front door key.",
            f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {WITCHS_HOUSE_WIKI_SOURCE}",
            produced_inventory=(("Door key", 1),),
        ),
        _stage_req(
            2,
            "Use the door key to enter the Witch's house.",
            f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {WITCHS_HOUSE_WIKI_SOURCE}",
            required_tools=(("Door key", 1),),
            auto_actions=("Enter the Witch's house with the door key",),
        ),
        _stage_req(
            3,
            "Search the cupboard for the magnet.",
            f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {WITCHS_HOUSE_DIARY_SOURCE}",
            produced_inventory=(("Magnet", 1),),
        ),
        _stage_req(
            4,
            "Use cheese and the magnet to unlock the mouse-hole security mechanism.",
            f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {WITCHS_HOUSE_DIARY_SOURCE}",
            consumed_inventory=(("Cheese", 1),),
            required_tools=(("Magnet", 1),),
            auto_actions=("Use cheese on the mouse hole and attach the magnet to the mouse",),
        ),
        _stage_req(
            5,
            "Cross the Witch's house hallway without being seen by the witch.",
            f"{WITCHS_HOUSE_SOURCE}; {WITCHS_HOUSE_WITCH_SENTRY_SOURCE}",
            auto_actions=("Avoid the witch's patrol through the house",),
        ),
        _stage_req(
            6,
            "Use leather gloves to pass the electric gate.",
            f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_tools=(("Leather gloves", 1),),
        ),
        _stage_req(
            7,
            "Search the fountain in the garden for the backroom key.",
            f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {WITCHS_HOUSE_DIARY_SOURCE}",
            produced_inventory=(("Backroom key", 1),),
        ),
        _stage_req(
            8,
            "Use the backroom key to unlock the shed door.",
            f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_tools=(("Backroom key", 1),),
            auto_actions=("Unlock the Witch's shed door with the backroom key",),
        ),
        _stage_req(
            9,
            "Defeat the Witch's experiment through all four forms before retrieving the ball.",
            f"{WITCHS_HOUSE_SOURCE}; {WITCHS_HOUSE_WIKI_SOURCE}",
            combat_encounters=(
                _combat(
                    WITCHS_HOUSE_ID,
                    "witchs_experiment_first_form",
                    "Witch's experiment (Skavid form)",
                    19,
                    f"{WITCHS_HOUSE_WIKI_SOURCE}; {WITCHS_HOUSE_EXPERIMENT_19_NPC_SOURCE}",
                    "Historical quest text says the experiment's first stage is a Skavid level 19; Darkan NPC id 897 supplies the Witch's experiment level 19 stats.",
                    npc_stats=(
                        ("hitpoints", 1130),
                        ("attack", 18),
                        ("strength", 10),
                        ("defence", 19),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 100),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "crush_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=WITCHS_HOUSE_EXPERIMENT_19_NPC_SOURCE,
                ),
                _combat(
                    WITCHS_HOUSE_ID,
                    "witchs_experiment_second_form",
                    "Witch's experiment (Spider form)",
                    30,
                    f"{WITCHS_HOUSE_WIKI_SOURCE}; {WITCHS_HOUSE_EXPERIMENT_30_NPC_SOURCE}",
                    "Historical quest text says the experiment's second stage is a Spider level 30; Darkan NPC id 898 supplies the Witch's experiment level 30 stats.",
                    npc_stats=(
                        ("hitpoints", 1225),
                        ("attack", 28),
                        ("strength", 20),
                        ("defence", 29),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 125),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "crush_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=WITCHS_HOUSE_EXPERIMENT_30_NPC_SOURCE,
                ),
                _combat(
                    WITCHS_HOUSE_ID,
                    "witchs_experiment_third_form",
                    "Witch's experiment (Bear form)",
                    42,
                    f"{WITCHS_HOUSE_WIKI_SOURCE}; {WITCHS_HOUSE_EXPERIMENT_42_NPC_SOURCE}",
                    "Historical quest text says the experiment's third stage is a Bear level 42; Darkan NPC id 899 supplies the Witch's experiment level 42 stats.",
                    npc_stats=(
                        ("hitpoints", 1325),
                        ("attack", 38),
                        ("strength", 30),
                        ("defence", 39),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 135),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "slash_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=WITCHS_HOUSE_EXPERIMENT_42_NPC_SOURCE,
                ),
                _combat(
                    WITCHS_HOUSE_ID,
                    "witchs_experiment_fourth_form",
                    "Witch's experiment (Wolf form)",
                    53,
                    f"{WITCHS_HOUSE_WIKI_SOURCE}; {WITCHS_HOUSE_EXPERIMENT_53_NPC_SOURCE}",
                    "Historical quest text says the experiment's final stage is a Wolf level 53; Darkan NPC id 900 supplies the Witch's experiment level 53 stats.",
                    npc_stats=(
                        ("hitpoints", 1425),
                        ("attack", 48),
                        ("strength", 40),
                        ("defence", 49),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 150),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "stab_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=WITCHS_HOUSE_EXPERIMENT_53_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            10,
            "Pick up Harvey's ball from the shed.",
            f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            produced_inventory=(("Ball", 1),),
        ),
        _stage_req(
            11,
            "Return the ball to Harvey.",
            f"{WITCHS_HOUSE_SOURCE}; {WITCHS_HOUSE_BOY_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Ball", 1),),
            auto_actions=("Return the ball to Harvey",),
        ),
    ),
    LOST_CITY_ID: (
        _stage_req(
            1,
            "Find Shamus in the Lumbridge Swamp tree.",
            f"{LOST_CITY_SOURCE_PATH}; {LOST_CITY_WARRIOR_SOURCE_PATH}; {LOST_CITY_TREE_SOURCE_PATH}",
            auto_actions=("Find Shamus in the Lumbridge Swamp tree",),
        ),
        _stage_req(
            2,
            "Speak to Shamus about the dramen staff and reach Entrana.",
            f"{LOST_CITY_SOURCE_PATH}; {LOST_CITY_SHAMUS_SOURCE_PATH}; {LOST_CITY_ENTRANA_SOURCE_PATH}",
            auto_actions=(
                "Speak to Shamus about the dramen staff",
                "Reach Entrana without combat gear",
            ),
        ),
        _stage_req(
            3,
            "Defeat the tree spirit guarding the Dramen tree.",
            f"{LOST_CITY_SOURCE_PATH}; {LOST_CITY_ENTRANA_SOURCE_PATH}; {LOST_CITY_TREE_SPIRIT_NPC_SOURCE_PATH}",
            combat_encounters=(
                _combat(
                    LOST_CITY_ID,
                    "tree_spirit",
                    "Tree spirit",
                    63,
                    f"{LOST_CITY_SOURCE_PATH}; {LOST_CITY_ENTRANA_SOURCE_PATH}; {LOST_CITY_TREE_SPIRIT_NPC_SOURCE_PATH}",
                    "2011Scape Lost City text requires killing the level 63 Tree spirit; the local NPC definition supplies the melee combat stats.",
                    npc_stats=(
                        ("hitpoints", 220),
                        ("attack", 90),
                        ("strength", 95),
                        ("defence", 80),
                    ),
                    npc_bonuses=(
                        ("defenceStab", 5),
                        ("defenceSlash", 5),
                        ("defenceCrush", 5),
                        ("defenceMagic", 0),
                        ("defenceRanged", 5),
                    ),
                    npc_configs=(("attack_speed", 4), ("attack_style", "melee")),
                    npc_stats_source=LOST_CITY_TREE_SPIRIT_NPC_SOURCE_PATH,
                ),
            ),
        ),
        _stage_req(
            4,
            "Cut a dramen branch from the Dramen tree.",
            f"{LOST_CITY_SOURCE_PATH}; {LOST_CITY_ENTRANA_SOURCE_PATH}",
            required_tools=(("Hatchet", 1),),
            auto_actions=("Cut a dramen branch",),
            produced_inventory=(("Dramen branch", 1),),
        ),
        _stage_req(
            5,
            "Craft the dramen staff and enter Zanaris through the Lumbridge Swamp shed.",
            f"{LOST_CITY_SOURCE_PATH}; {LOST_CITY_ENTRANA_SOURCE_PATH}; {LOST_CITY_SHED_SOURCE_PATH}",
            required_inventory=(("Dramen branch", 1),),
            consumed_inventory=(("Dramen branch", 1),),
            produced_inventory=(("Dramen staff", 1),),
            required_tools=(("Knife", 1),),
            auto_actions=("Craft a dramen staff", "Enter Zanaris through the Lumbridge Swamp shed"),
        ),
    ),
    TAI_BWO_WANNAI_TRIO_ID: (
        _stage_req(
            2,
            "Help Tiadeche with the karambwan catching setup.",
            TAI_BWO_WANNAI_TRIO_SOURCE,
            required_inventory=(("Raw karambwan", 2),),
            required_tools=(("Small fishing net", 1),),
            auto_actions=("Catch karambwanji for Tiadeche",),
        ),
        _stage_req(
            3,
            "Prepare Tamayu to fight the Shaikahan.",
            TAI_BWO_WANNAI_TRIO_SOURCE,
            required_inventory=(("Agility potion (4)", 1), ("Steel spear", 1)),
            auto_actions=("Repair and poison Tamayu's spear",),
            combat_encounters=(
                _combat(
                    TAI_BWO_WANNAI_TRIO_ID,
                    "monkey",
                    "Monkey",
                    3,
                    "https://runescape.wiki/w/Tai_Bwo_Wannai_Trio?oldid=6529797",
                    "Quest details require killing a level 3 monkey.",
                ),
                _combat(
                    TAI_BWO_WANNAI_TRIO_ID,
                    "jogre",
                    "Jogre",
                    53,
                    f"https://runescape.wiki/w/Tai_Bwo_Wannai_Trio?oldid=6529797; {TAI_BWO_WANNAI_TRIO_JOGRE_NPC_SOURCE}",
                    "Jogre bones can be obtained during the quest by fighting a level 53 jogre.",
                    npc_stats=(
                        ("hitpoints", 600),
                        ("attack", 43),
                        ("strength", 43),
                        ("defence", 43),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 73),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "crush_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=TAI_BWO_WANNAI_TRIO_JOGRE_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            4,
            "Prepare Tinsay's unusual food requests.",
            TAI_BWO_WANNAI_TRIO_SOURCE,
            required_inventory=(("Karamjan rum", 1), ("Seaweed", 1), ("Banana", 1), ("Jogre bones", 1)),
            required_tools=(("Knife", 1), ("Tinderbox", 1), ("Pestle and mortar", 1)),
            auto_actions=("Prepare the sliced banana in rum", "Burn and grind the jogre bones"),
        ),
    ),
    CARNILLEAN_RISING_ID: (
        _stage_req(
            1,
            "Accept Xenia's request and speak to Ceril Carnillean.",
            CARNILLEAN_RISING_WIKI_SOURCE,
            auto_actions=("Speak to Xenia", "Speak to Ceril Carnillean"),
        ),
        _stage_req(
            2,
            "Gather the mansion props for Philipe's quest.",
            CARNILLEAN_RISING_WIKI_SOURCE,
            auto_actions=("Collect the Carnillean family book", "Gather the mansion props"),
        ),
        _stage_req(
            3,
            "Build the cellar quest scene.",
            CARNILLEAN_RISING_WIKI_SOURCE,
            auto_actions=("Build the cave quest hotspots", "Recruit Sarsaparilla and Claus"),
        ),
        _stage_req(
            4,
            "Guide Philipe through the staged quest.",
            CARNILLEAN_RISING_WIKI_SOURCE,
            auto_actions=("Guide Philipe through the cellar quest",),
        ),
        _stage_req(
            5,
            "Report back to Philipe, Ceril, and Xenia.",
            CARNILLEAN_RISING_WIKI_SOURCE,
            auto_actions=("Report back to Philipe", "Report back to Ceril and Xenia"),
        ),
    ),
    DEADLIEST_CATCH_ID: (
        _stage_req(
            1,
            "Pickpocket the Master fisher for the sea chart.",
            DEADLIEST_CATCH_WIKI_SOURCE,
            auto_actions=("Pickpocket the Master fisher for the sea chart",),
        ),
        _stage_req(
            2,
            "Recruit Linza and prepare the giant harpoon.",
            DEADLIEST_CATCH_WIKI_SOURCE,
            auto_actions=("Recruit Linza", "Prepare the giant harpoon"),
        ),
        _stage_req(
            3,
            "Track the Thalassus and rescue Jones.",
            DEADLIEST_CATCH_WIKI_SOURCE,
            auto_actions=("Track the Thalassus", "Rescue Jones"),
        ),
    ),
    WOLF_WHISTLE_ID: (
        _stage_req(
            1,
            "Find Scalectrix at the Taverley well.",
            f"{DARKAN_WOLF_WHISTLE_SOURCE}; {WOLF_WHISTLE_WIKI_SOURCE}",
            auto_actions=("Find Scalectrix at the Taverley well",),
        ),
        _stage_req(
            2,
            "Collect the wolpertinger pouch materials.",
            f"{DARKAN_WOLF_WHISTLE_SOURCE}; {WOLF_WHISTLE_WIKI_SOURCE}",
            auto_actions=("Collect the ancient wolf bone amulet", "Collect the embroidered pouch", "Collect the white hare meat"),
        ),
        _stage_req(
            3,
            "Infuse the giant wolpertinger pouch and save Bowloftrix.",
            f"{DARKAN_WOLF_WHISTLE_SOURCE}; {WOLF_WHISTLE_WIKI_SOURCE}",
            auto_actions=("Infuse the giant wolpertinger pouch", "Take the pouch to Scalectrix"),
        ),
    ),
    SONG_FROM_THE_DEPTHS_ID: (
        _stage_req(
            1,
            "Drink the restless sleep potion and follow the souls to the cave.",
            SONG_FROM_THE_DEPTHS_WIKI_SOURCE,
            auto_actions=("Drink the restless sleep potion", "Follow the souls to the cave entrance"),
        ),
        _stage_req(
            2,
            "Work through the dream cave puzzles.",
            SONG_FROM_THE_DEPTHS_WIKI_SOURCE,
            auto_actions=("Complete the maze doors", "Solve the symbol rooms", "Move the saplings through the dream rooms"),
        ),
        _stage_req(
            3,
            "Escape the dragon's stomach and return to Lucille.",
            SONG_FROM_THE_DEPTHS_WIKI_SOURCE,
            auto_actions=("Escape the dragon's stomach", "Return to Lucille"),
        ),
    ),
    SOME_LIKE_IT_COLD_ID: (
        _stage_req(
            1,
            "Reach the seals and learn how to enter the Iceberg.",
            SOME_LIKE_IT_COLD_WIKI_SOURCE,
            auto_actions=("Speak to Chuck again for teleport", "Entertain the seal", "Travel to the Iceberg"),
        ),
        _stage_req(
            2,
            "Build Ping and Pong's rock costumes.",
            SOME_LIKE_IT_COLD_WIKI_SOURCE,
            auto_actions=("Build Ping and Pong's rock costumes", "Give Ping and Pong their costumes"),
        ),
        _stage_req(
            3,
            "Infiltrate the Walrus camp and recover the egg.",
            SOME_LIKE_IT_COLD_WIKI_SOURCE,
            auto_actions=("Distract the Walrus", "Steal the egg from the table"),
        ),
        _stage_req(
            4,
            "Defeat Astoria and repair the submarine engine.",
            SOME_LIKE_IT_COLD_WIKI_SOURCE,
            auto_actions=(
                "Defeat Astoria in Battlefish",
                "Collect camp repair supplies",
                "Repair the submarine engine",
            ),
        ),
        _stage_req(
            5,
            "Defeat the seals in Battlefish.",
            SOME_LIKE_IT_COLD_WIKI_SOURCE,
            auto_actions=("Defeat the seals in Battlefish",),
        ),
        _stage_req(
            6,
            "Escape the Walrus camp.",
            SOME_LIKE_IT_COLD_WIKI_SOURCE,
            auto_actions=("Escape in the submarine",),
        ),
    ),
}


QUEST_STAGE_REQUIREMENT_ADDITIONS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    SWAN_SONG_ID: (
        _stage_req(
            5,
            "Defeat the Sea Troll Queen.",
            f"{SWAN_SONG_SOURCE}; {SWAN_SONG_WIKI_SOURCE}",
            combat_encounters=(
                _combat(
                    SWAN_SONG_ID,
                    "sea_troll_queen",
                    "Sea Troll Queen",
                    170,
                    f"{SWAN_SONG_WIKI_SOURCE}; {SWAN_SONG_SEA_TROLL_QUEEN_NPC_SOURCE}",
                    "Quest details require the level 170 Sea Troll Queen after the sea troll waves.",
                    npc_stats=(
                        ("hitpoints", 2000),
                        ("attack", 100),
                        ("strength", 70),
                        ("defence", 100),
                        ("magic", 150),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 2345),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "crush_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=SWAN_SONG_SEA_TROLL_QUEEN_NPC_SOURCE,
                ),
            ),
        ),
    ),
    THE_FEUD_ID: (
        _stage_req(
            4,
            "Defeat the Tough guy after the Bandit champion.",
            f"{THE_FEUD_WIKI_SOURCE}; {THE_FEUD_TOUGH_GUY_NPC_SOURCE}",
            combat_encounters=(
                _combat(
                    THE_FEUD_ID,
                    "tough_guy_75",
                    "Tough guy",
                    75,
                    f"{THE_FEUD_WIKI_SOURCE}; {THE_FEUD_TOUGH_GUY_NPC_SOURCE}",
                    "Historical quest details name Tough guy (level 75) after the Bandit champion.",
                    npc_stats=(
                        ("hitpoints", 750),
                        ("attack", 85),
                        ("strength", 50),
                        ("defence", 50),
                        ("magic", 80),
                        ("ranged", 0),
                    ),
                    npc_configs=(
                        ("max_hit", 70),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "crush_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=THE_FEUD_TOUGH_GUY_NPC_SOURCE,
                ),
            ),
        ),
    ),
    RFD_FREEING_SIR_AMIK_VARZE_ID: (
        _stage_req(
            3,
            "Defeat the Black Dragon after the Evil Chicken.",
            f"{RFD_FREEING_SIR_AMIK_VARZE_WIKI_SOURCE}; {RFD_BLACK_DRAGON_NPC_SOURCE}",
            combat_encounters=(
                _combat(
                    RFD_FREEING_SIR_AMIK_VARZE_ID,
                    "black_dragon_227",
                    "Black Dragon",
                    227,
                    f"{RFD_FREEING_SIR_AMIK_VARZE_WIKI_SOURCE}; {RFD_BLACK_DRAGON_NPC_SOURCE}",
                    "Historical quest details name Black Dragon (Level 227) after the Evil Chicken.",
                    npc_stats=(
                        ("hitpoints", 1900),
                        ("attack", 200),
                        ("strength", 200),
                        ("defence", 200),
                        ("magic", 100),
                        ("ranged", 1),
                    ),
                    npc_configs=(("attack_speed", 4),),
                    npc_stats_source=RFD_BLACK_DRAGON_NPC_SOURCE,
                ),
            ),
        ),
    ),
    KENNITHS_CONCERNS_ID: (
        _stage_req(
            1,
            "Investigate the Witchaven tunnels and speak to a villager.",
            KENNITHS_CONCERNS_WIKI_SOURCE,
            required_tools=(("Pickaxe", 1),),
            auto_actions=(
                "Reach the Witchaven shrine tunnels",
                "Talk to a villager past the rocks",
            ),
        ),
        _stage_req(
            2,
            "Warn Kennith and speak to Kent.",
            KENNITHS_CONCERNS_WIKI_SOURCE,
            auto_actions=("Warn Kennith", "Speak to Kent near the Legends' Guild"),
        ),
        _stage_req(
            3,
            "Trap the possessed villagers in the church.",
            KENNITHS_CONCERNS_WIKI_SOURCE,
            auto_actions=("Trap the possessed villagers in the church",),
        ),
        _stage_req(
            4,
            "Mine rubium and fill the steam vents.",
            KENNITHS_CONCERNS_WIKI_SOURCE,
            required_tools=(("Pickaxe", 1),),
            auto_actions=("Mine rubium and fill the steam vents",),
        ),
        _stage_req(
            5,
            "Find the toy train and rescue Kennith.",
            KENNITHS_CONCERNS_WIKI_SOURCE,
            auto_actions=("Find Kennith's toy train", "Use the toy train on Kennith"),
        ),
    ),
}


QUEST_STAGE_REQUIREMENT_CLEANUPS_BY_ID: Dict[str, Tuple[QuestStageRequirementCleanup, ...]] = {
    "monkey_madness": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Monkey Dentures", "M'Amulet mould", "Monkey talisman"),
            remove_required_actions=("Complete Monkey Madness stage 1 objective",),
            add_auto_actions=(
                "Acquire the monkey dentures, m'amulet mould, and monkey talisman during the Ape Atoll infiltration",
            ),
        ),
    ),
    "rat_catchers": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Rat poison",),
            remove_required_actions=("Complete Rat Catchers stage 1 objective",),
            add_auto_actions=("Have Hooknosed Jack make rat poison",),
            add_consumed_inventory=(("Vial", 1), ("Clean kwuarm", 1), ("Red spiders' eggs", 1)),
            add_produced_inventory=(("Rat poison", 1),),
        ),
    ),
    "mournings_end_part_i": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Lletya", "Elf teleport crystal"),
            remove_required_actions=("Complete Mourning's End Part I stage 1 objective",),
            add_auto_actions=("Reach Lletya",),
        ),
        QuestStageRequirementCleanup(
            stage=3,
            remove_required_inventory=("Oronwen",),
            add_required_actions=("Have Oronwen repair the mourner trousers",),
        ),
        QuestStageRequirementCleanup(
            stage=5,
            remove_required_inventory=("Rotten apple",),
            add_required_actions=("Use the rotten apple to sabotage the mourner food stores",),
        ),
    ),
    "death_to_the_dorgeshuun": (
        QuestStageRequirementCleanup(
            stage=5,
            remove_required_tools=("Tears of Guthix cavern",),
            remove_required_actions=("Complete Death to the Dorgeshuun stage 5 objective",),
            add_auto_actions=("Reach the Tears of Guthix cavern",),
        ),
    ),
    "elemental_workshop_ii": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Beaten Book", "Slashed book"),
            remove_required_actions=("Complete Elemental Workshop II stage 1 objective",),
            add_auto_actions=("Find the Beaten book in the Exam Centre and read its hidden scroll",),
            add_produced_inventory=(("Beaten book", 1),),
            source=ELEMENTAL_WORKSHOP_II_STAGE_ONE_SOURCE,
        ),
    ),
    "enlightened_journey": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=(
                "Ring of kinship",
                "Explorer ring",
                "Clan Vexillum",
                "Clan Camp",
                "Port Sarim",
                "Daemonheim",
            ),
            remove_required_actions=("Complete Enlightened Journey stage 1 objective",),
            add_auto_actions=("Reach Auguste on Entrana",),
        ),
        QuestStageRequirementCleanup(
            stage=2,
            add_consumed_inventory=(("Sack", 8),),
            add_produced_inventory=(("Sandbag", 8),),
        ),
        QuestStageRequirementCleanup(
            stage=3,
            remove_required_inventory=("Willow branch",),
        ),
    ),
    "making_history": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=(
                "Ardougne",
                "Enchanted lyre",
                "Rellekka",
                "Teleport to House",
                "Magic tablet",
                "Castle_Wars",
                "Ectophial",
                "Making History",
            ),
            remove_required_inventory_options=("Ecto-token", "Port Sarim", "Port Phasmatys", "Fairy Tale III - Orks Rift"),
            remove_required_actions=("Complete Making History stage 1 objective",),
            add_auto_actions=("Reach the Outpost, Rellekka, and Port Phasmatys travel legs",),
        ),
    ),
    "cabin_fever": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory_options=("Ghosts Ahoy",),
            remove_required_actions=("Complete Cabin Fever stage 1 objective",),
            add_auto_actions=("Reach the Port Phasmatys charter route",),
        ),
    ),
    "cold_war": (
        QuestStageRequirementCleanup(
            stage=2,
            remove_required_inventory=("Crafting table 3",),
            add_required_actions=("Build the clockwork penguin on a crafting table 3",),
        ),
    ),
    "kenniths_concerns": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_actions=("Complete Kennith's Concerns stage 1 objective",),
        ),
        QuestStageRequirementCleanup(
            stage=2,
            remove_required_actions=("Complete Kennith's Concerns stage 2 objective",),
        ),
        QuestStageRequirementCleanup(
            stage=3,
            remove_required_actions=("Complete Kennith's Concerns stage 3 objective",),
        ),
        QuestStageRequirementCleanup(
            stage=4,
            remove_required_actions=("Complete Kennith's Concerns stage 4 objective",),
        ),
        QuestStageRequirementCleanup(
            stage=5,
            remove_required_actions=("Complete Kennith's Concerns stage 5 objective",),
        ),
    ),
    "myths_of_the_white_lands": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=(
                "Lumbridge Teleport",
                "Glory Amulet",
                "Runecrafting guild teleport",
                "Wicked hood",
                "Fairy Ring",
                "Wizard's Tower",
            ),
            remove_required_actions=("Complete Myths of the White Lands stage 1 objective",),
            add_auto_actions=("Reach the Wizard's Tower ice cave",),
        ),
    ),
    "in_pyre_need": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory_options=("Fairy Rings", "Phoenix lair teleport"),
            remove_required_actions=("Complete In Pyre Need stage 1 objective",),
            add_auto_actions=("Reach the Phoenix lair",),
        ),
    ),
    "the_fremennik_isles": (
        QuestStageRequirementCleanup(stage=1, remove_required_inventory=("Mining",)),
        QuestStageRequirementCleanup(
            stage=5,
            remove_required_inventory=("Yak hide armour", "Fremennik round shield"),
            add_required_actions=("Cure and stitch yak-hide armour", "Make a Fremennik round shield"),
        ),
    ),
    "kings_ransom": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Animate rock scroll",),
            remove_required_actions=("Complete King's Ransom stage 1 objective",),
            add_auto_actions=(
                "Receive the animate rock scroll from Wizard Cromperty after recovering the Holy Grail",
            ),
            add_produced_inventory=(("Animate rock scroll", 1),),
            source=KINGS_RANSOM_SCROLL_SOURCE,
        ),
    ),
    "dealing_with_scabaras": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Agility Pyramid", "Random Bronze armours/weapons"),
            remove_required_actions=("Complete Dealing with Scabaras stage 1 objective",),
            add_auto_actions=(
                "Prepare bronze equipment for the High Priest's tests",
                "Reach the Agility Pyramid",
            ),
            remove_required_routes=("Reach the Agility Pyramid",),
        ),
        QuestStageRequirementCleanup(
            stage=2,
            remove_required_inventory=("Food",),
            remove_required_actions=("Complete Dealing with Scabaras stage 2 objective",),
            add_auto_actions=("Complete Dealing with Scabaras stage 2 objective",),
        ),
        QuestStageRequirementCleanup(
            stage=3,
            remove_required_actions=("Complete Dealing with Scabaras stage 3 objective",),
            add_auto_actions=("Complete Dealing with Scabaras stage 3 objective",),
        ),
        QuestStageRequirementCleanup(
            stage=4,
            remove_required_actions=("Complete Dealing with Scabaras stage 4 objective",),
            add_auto_actions=("Complete Dealing with Scabaras stage 4 objective",),
        ),
        QuestStageRequirementCleanup(
            stage=5,
            remove_required_actions=("Complete Dealing with Scabaras stage 5 objective",),
            add_auto_actions=("Complete Dealing with Scabaras stage 5 objective",),
        ),
        QuestStageRequirementCleanup(
            stage=6,
            remove_required_actions=("Complete Dealing with Scabaras stage 6 objective",),
            add_auto_actions=("Complete Dealing with Scabaras stage 6 objective",),
        ),
        QuestStageRequirementCleanup(
            stage=7,
            remove_required_actions=("Complete Dealing with Scabaras stage 7 objective",),
            add_auto_actions=("Complete Dealing with Scabaras stage 7 objective",),
        ),
    ),
    "roving_elves": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Good Food",),
        ),
    ),
    "rum_deal": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Armour", "Food"),
        ),
    ),
    "spirits_of_the_elid": (
        QuestStageRequirementCleanup(
            stage=2,
            remove_required_inventory=("Telegrab",),
            add_required_actions=("Cast Telegrab for the water channel puzzle",),
        ),
    ),
    "enakhras_lament": (
        QuestStageRequirementCleanup(
            stage=5,
            remove_required_inventory=("Crumble Undead",),
            add_required_actions=("Cast Crumble Undead during the boneguard fight",),
        ),
    ),
    "in_aid_of_the_myreque": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Food",),
        ),
        QuestStageRequirementCleanup(
            stage=6,
            remove_required_inventory_options=("Enchant sapphire",),
            add_required_actions=("Enchant sapphire for the Myreque preparations",),
        ),
    ),
    "dream_mentor": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Food",),
        ),
    ),
    "back_to_my_roots": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Food",),
            remove_required_inventory_options=("Shilo Village",),
            remove_required_actions=("Complete Back to my Roots stage 1 objective",),
            add_auto_actions=("Reach the Karamja jungle route",),
        ),
    ),
    "rocking_out": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Brimhaven tablet", "Ectophial"),
            remove_required_inventory_options=("Rimmington", "Rimmington tablet", "Love Story"),
            remove_required_actions=("Complete Rocking Out stage 1 objective",),
            add_auto_actions=("Reach the Rimmington customs office",),
        ),
    ),
    "glorious_memories": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Teleport to House", "Player-owned house", "Rellekka", "Rellekka tablet", "Ring of wealth"),
            remove_required_actions=("Complete Glorious Memories stage 1 objective",),
            add_auto_actions=("Reach Rellekka and Miscellania",),
        ),
    ),
    "elemental_workshop_iii": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Ragged book",),
            remove_required_actions=("Complete Elemental Workshop III stage 1 objective",),
            add_auto_actions=("Find and read the Ragged book in the workshop",),
        ),
        QuestStageRequirementCleanup(
            stage=7,
            remove_required_inventory=("Elemental Workshop I",),
        ),
    ),
    "the_eyes_of_glouphrie": (
        QuestStageRequirementCleanup(
            stage=3,
            remove_required_tools=("Bucket of sap",),
            add_required_actions=("Collect a bucket of sap from an evergreen tree",),
        ),
    ),
    "the_tale_of_the_muspah": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=(
                "Enchant Level 1 Jewellery",
                "Magic carpet",
                "Teleportation methods",
                "Dramen staff",
                "Lunar staff",
                "Fairy rings",
                "Enchanted lyre",
                "Rellekka tablet",
                "Pollnivneach tablet",
                "Slayer ring",
                "Broomstick",
                "Sorceress's Garden",
                "Food",
            ),
            add_auto_actions=(
                "Cast Enchant Level 1 Jewellery for the sapphire preparations",
                "Reach the Muspah cave route through Rellekka and Pollnivneach",
            ),
            remove_required_actions=("Complete The Tale of the Muspah stage 1 objective",),
        ),
        QuestStageRequirementCleanup(
            stage=2,
            remove_required_inventory=("Rellekka",),
            remove_required_actions=("Complete The Tale of the Muspah stage 2 objective",),
            add_auto_actions=("Reach Rellekka",),
        ),
        QuestStageRequirementCleanup(
            stage=3,
            remove_required_inventory=("Pollnivneach",),
            remove_required_actions=("Complete The Tale of the Muspah stage 3 objective",),
            add_auto_actions=("Reach Pollnivneach",),
        ),
        QuestStageRequirementCleanup(
            stage=4,
            remove_required_inventory=("Enchant sapphire",),
            remove_required_actions=("Complete The Tale of the Muspah stage 4 objective",),
            add_auto_actions=(
                "Bore sapphires from the ice block and enchant them",
                "Enchant the sapphires for Ali the Wise",
            ),
        ),
        QuestStageRequirementCleanup(
            stage=5,
            remove_required_actions=("Complete The Tale of the Muspah stage 5 objective",),
            add_auto_actions=("Bore and enchant the sapphires around Jhallan",),
        ),
    ),
    "legacy_of_seergaze": (
        QuestStageRequirementCleanup(
            stage=5,
            remove_required_inventory=("Enchant Level 2 Jewellery",),
            add_required_actions=("Cast Enchant Level 2 Jewellery for the emerald preparations",),
        ),
    ),
    "meeting_history": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Making History",),
        ),
    ),
    "while_guthix_sleeps": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("NPC Contact",),
            remove_required_actions=("Complete While Guthix Sleeps stage 1 objective",),
            add_auto_actions=(
                "Cast NPC Contact to reach the quest contacts",
            ),
        ),
    ),
    "blood_runs_deep": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Food", "Prayer Potion", "Armour"),
        ),
    ),
    "desert_treasure": (
        QuestStageRequirementCleanup(stage=1, remove_required_inventory=("Thieving",)),
    ),
    "troll_romance": (
        QuestStageRequirementCleanup(stage=1, remove_required_inventory=("Combat gear and good food",)),
    ),
    "do_no_evil": (
        QuestStageRequirementCleanup(
            stage=3,
            remove_required_inventory=("M'amulet mould",),
            add_required_actions=("Recover an m'amulet mould before making the monkeyspeak amulet",),
        ),
    ),
    "within_the_light": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=(
                "Ardougne",
                "Teleport crystal",
                "New key",
                "Tarnished key",
                "Crystal trinket",
                "Colour wheel",
                "Shadow",
                "Prayer potions",
            ),
            remove_required_actions=(
                "Complete Within the Light stage 1 objective",
                "Recover the Temple of Light keys and crystal puzzle pieces",
            ),
            add_auto_actions=(
                "Reach the Temple of Light through West Ardougne and Lletya",
                "Recover the Temple of Light keys and crystal puzzle pieces",
            ),
        ),
    ),
    "the_firemakers_curse": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Food", "Let Them Eat Pie"),
        ),
    ),
}


QUEST_COMBAT_ENCOUNTER_REPLACEMENTS_BY_ID: Dict[str, Dict[str, QuestCombatEncounterReplacement]] = {
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


_STAGE_COUNT_BY_LENGTH = {
    "Short": 3,
    "Short to Medium": 4,
    "Medium": 5,
    "Medium to Long": 6,
    "Long": 7,
    "Long to Very Long": 8,
    "Very Long": 9,
    "Very, Very Long": 10,
}


def _generated_stage_count(length: str) -> int:
    return _STAGE_COUNT_BY_LENGTH.get(length, 5)


def _generated_journal_stages(display_name: str, stages: int) -> Tuple[QuestStage, ...]:
    if stages <= 1:
        return (_simple_stage(1, f"I completed {display_name}.", "Quest complete!"),)
    rows = [_simple_stage(1, f"I started {display_name}.")]
    for stage in range(2, stages):
        rows.append(_simple_stage(stage, f"I made progress on {display_name}."))
    rows.append(_simple_stage(stages, f"I completed {display_name}.", "Quest complete!"))
    return tuple(rows)


def _catalog_journal_stages(row: Dict[str, object], display_name: str, stages: int) -> Tuple[QuestStage, ...]:
    raw_stages = row.get("journal_stages", ()) or ()
    rows = []
    for raw_stage in raw_stages:
        if not isinstance(raw_stage, dict):
            continue
        try:
            stage = int(raw_stage.get("stage", 0))
        except (TypeError, ValueError):
            continue
        raw_lines = raw_stage.get("journal", ()) or ()
        lines = tuple(str(line) for line in raw_lines if str(line).strip())
        if stage > 0 and lines:
            rows.append(QuestStage(stage, lines))
    if rows:
        return tuple(sorted(rows, key=lambda stage: stage.stage))
    return _generated_journal_stages(display_name, stages)


def _quest_reward_item_name(name: object) -> str:
    raw_name = str(name)
    return QUEST_REWARD_ITEM_NAME_OVERRIDES.get(raw_name, raw_name)


def _catalog_int(row: Dict[str, object], key: str, default: int = 0) -> int:
    try:
        return int(row.get(key, default))
    except (TypeError, ValueError):
        return default


def _catalog_bool(row: Dict[str, object], key: str, default: bool = False) -> bool:
    value = row.get(key, default)
    return bool(value)


def _catalog_item_pairs(value: object) -> Tuple[Tuple[str, int], ...]:
    if isinstance(value, Mapping):
        return tuple((str(name), _catalog_int({"value": amount}, "value", 1)) for name, amount in value.items())
    if isinstance(value, (tuple, list)):
        pairs = []
        for item in value:
            if isinstance(item, Mapping):
                name = item.get("item_name") or item.get("display_name")
                amount = item.get("quantity", item.get("amount", 1))
                if not isinstance(name, str) or not name:
                    for item_name, item_amount in item.items():
                        if item_name in {"item_name", "display_name", "quantity", "amount"}:
                            continue
                        pairs.append((str(item_name), _catalog_int({"value": item_amount}, "value", 1)))
                    continue
            elif isinstance(item, (tuple, list)) and len(item) >= 2:
                name, amount = item[0], item[1]
            else:
                continue
            if isinstance(name, str) and name:
                pairs.append((name, _catalog_int({"value": amount}, "value", 1)))
        return tuple(pairs)
    return ()


def _catalog_item_options(value: object) -> Tuple[Tuple[Tuple[str, int], ...], ...]:
    if not isinstance(value, (tuple, list)):
        return ()
    if value and all(isinstance(group, Mapping) for group in value):
        return (_catalog_item_pairs(value),)
    groups = []
    for group in value:
        options = _catalog_item_pairs(group)
        if options:
            groups.append(options)
    return tuple(groups)


def _catalog_object_pairs(value: object) -> Tuple[Tuple[str, object], ...]:
    if isinstance(value, Mapping):
        return tuple((str(key), item) for key, item in value.items())
    return ()


def _catalog_strings(value: object) -> Tuple[str, ...]:
    if isinstance(value, str):
        return (value,) if value else ()
    if isinstance(value, (tuple, list)):
        return tuple(str(item) for item in value if str(item))
    return ()


def _catalog_combat_encounters(value: object) -> Tuple[QuestCombatEncounter, ...]:
    if not isinstance(value, (tuple, list)):
        return ()
    encounters = []
    for raw in value:
        if not isinstance(raw, Mapping):
            continue
        encounter_id = raw.get("encounter_id")
        display_name = raw.get("display_name")
        if not isinstance(encounter_id, str) or not isinstance(display_name, str):
            continue
        encounters.append(
            QuestCombatEncounter(
                encounter_id=encounter_id,
                display_name=display_name,
                level=_catalog_int(dict(raw), "level", 0),
                quantity=_catalog_int(dict(raw), "quantity", 1),
                source=str(raw.get("source", "")),
                source_text=str(raw.get("source_text", "")),
                npc_stats=_catalog_object_pairs(raw.get("npc_stats", {})),
                npc_bonuses=_catalog_object_pairs(raw.get("npc_bonuses", {})),
                npc_configs=_catalog_object_pairs(raw.get("npc_configs", {})),
                npc_stats_source=str(raw.get("npc_stats_source", "")),
            )
        )
    return tuple(encounters)


def _catalog_stage_requirements(value: object) -> Tuple[QuestStageRequirement, ...]:
    if not isinstance(value, (tuple, list)):
        return ()
    requirements = []
    for raw in value:
        if not isinstance(raw, Mapping):
            continue
        stage = _catalog_int(dict(raw), "stage", 0)
        if stage <= 0:
            continue
        requirements.append(
            QuestStageRequirement(
                stage=stage,
                description=str(raw.get("description", "Generated quest-stage requirement.")),
                variant=str(raw.get("variant", "")),
                required_inventory=_catalog_item_pairs(raw.get("required_inventory", {})),
                required_inventory_options=_catalog_item_options(raw.get("required_inventory_options", ())),
                consumed_inventory=_catalog_item_pairs(raw.get("consumed_inventory", {})),
                consumed_inventory_options=_catalog_item_options(raw.get("consumed_inventory_options", ())),
                produced_inventory=_catalog_item_pairs(raw.get("produced_inventory", {})),
                required_tools=_catalog_item_pairs(raw.get("required_tools", {})),
                required_actions=_catalog_strings(raw.get("required_actions", ())),
                auto_actions=_catalog_strings(raw.get("auto_actions", ())),
                required_routes=_catalog_strings(raw.get("required_routes", ())),
                combat_encounters=_catalog_combat_encounters(raw.get("combat_encounters", ())),
                source=str(raw.get("source", "")),
            )
        )
    return tuple(requirements)


def _quest_from_catalog(row: Dict[str, object]) -> QuestDefinition:
    display_name = str(row.get("display_name", row.get("id", "Quest")))
    quest_id = str(row.get("id"))
    length = str(row.get("length", "Medium"))
    stages = _catalog_int(row, "stages", _generated_stage_count(length))
    required_quests = tuple(
        QuestPrerequisite(str(req.get("quest_id")), str(req.get("display_name", req.get("quest_id"))))
        for req in row.get("required_quests", ()) or ()
        if isinstance(req, dict) and req.get("quest_id")
    )
    required_skills = tuple(
        QuestSkillRequirement(
            str(req.get("skill_id")),
            str(req.get("display_name", req.get("skill_id"))),
            _catalog_int(req, "level", 1),
        )
        for req in row.get("required_skills", ()) or ()
        if isinstance(req, dict) and req.get("skill_id")
    )
    xp_rewards = tuple(
        QuestXpReward(str(reward.get("skill_id")), float(reward.get("amount", 0) or 0))
        for reward in row.get("xp_rewards", ()) or ()
        if isinstance(reward, dict) and reward.get("skill_id")
    )
    xp_rewards = QUEST_XP_REWARD_REPLACEMENTS_BY_ID.get(quest_id, xp_rewards)
    item_rewards = QUEST_ITEM_REWARD_REPLACEMENTS_BY_ID.get(quest_id)
    if item_rewards is None:
        item_rewards = tuple(
            (_quest_reward_item_name(reward.get("item_name")), _catalog_int(reward, "quantity", 1))
            for reward in row.get("item_rewards", ()) or ()
            if isinstance(reward, dict) and reward.get("item_name")
        )
    item_reward_additions = QUEST_ITEM_REWARD_ADDITIONS_BY_ID.get(quest_id, ())
    if item_reward_additions:
        item_rewards += tuple(
            (_quest_reward_item_name(reward.get("item_name")), _catalog_int(reward, "quantity", 1))
            for reward in item_reward_additions
            if isinstance(reward, dict) and reward.get("item_name")
        )
    lamp_rewards = tuple(
        QuestLampReward(
            str(reward.get("display_name", "XP lamp")),
            float(reward.get("amount", 0) or 0),
            tuple(str(skill_id) for skill_id in (reward.get("skill_options", ()) or ()) if str(skill_id)),
            _catalog_int(reward, "minimum_level", 1),
            str(reward.get("source", row.get("reward_source", row.get("source", "")))),
            str(reward.get("source_text", "")),
            _catalog_int(reward, "quantity", 1),
        )
        for reward in row.get("lamp_rewards", ()) or ()
        if isinstance(reward, dict) and reward.get("amount")
    )
    lamp_rewards = QUEST_LAMP_REWARD_REPLACEMENTS_BY_ID.get(quest_id, lamp_rewards)
    return QuestDefinition(
        id=quest_id,
        display_name=display_name,
        stages=stages,
        point_reward=_catalog_int(row, "point_reward", 0),
        rewards=item_rewards,
        start_point=str(row.get("start_point", "See the source guide for the start location.")),
        requirements=tuple(str(requirement) for requirement in (row.get("requirements", ()) or ())),
        required_items=(),
        combat=str(row.get("combat", "See the source guide.")),
        source=f"{row.get('source', '')}; {row.get('release_source', '')}",
        journal_stages=_catalog_journal_stages(row, display_name, stages),
        release_date=str(row.get("release_date", "")),
        members=_catalog_bool(row, "members", True),
        difficulty=str(row.get("difficulty", "Novice")),
        length=length,
        timeline=str(row.get("timeline", "Fifth Age")),
        required_quests=required_quests,
        required_skills=required_skills,
        required_quest_points=_catalog_int(row, "required_quest_points", 0),
        xp_rewards=xp_rewards,
        lamp_rewards=lamp_rewards,
        unlocks=tuple(str(unlock) for unlock in (row.get("unlocks", ()) or ())),
        release_order=_catalog_int(row, "release_order", 9999),
        stage_requirements=_catalog_stage_requirements(row.get("stage_requirements", ())),
        start_inventory=_catalog_item_pairs(row.get("start_inventory", {})),
    )


def _quest_catalog_row_id(row: Dict[str, object]) -> str:
    return str(row.get("id", ""))


def _dedupe_stage_requirements(requirements: Tuple[QuestStageRequirement, ...]) -> Tuple[QuestStageRequirement, ...]:
    seen = set()
    rows = []
    for requirement in sorted(requirements, key=lambda row: (row.stage, row.description, row.source)):
        key = (
            requirement.stage,
            requirement.description,
            requirement.variant,
            requirement.required_inventory,
            requirement.required_inventory_options,
            requirement.consumed_inventory,
            requirement.consumed_inventory_options,
            requirement.produced_inventory,
            requirement.required_tools,
            requirement.required_actions,
            requirement.required_routes,
            tuple(encounter.encounter_id for encounter in requirement.combat_encounters),
            requirement.source,
        )
        if key in seen:
            continue
        seen.add(key)
        rows.append(requirement)
    return tuple(rows)


def _apply_combat_encounter_replacements(
    quest_id: str,
    requirements: Tuple[QuestStageRequirement, ...],
) -> Tuple[QuestStageRequirement, ...]:
    replacements = QUEST_COMBAT_ENCOUNTER_REPLACEMENTS_BY_ID.get(quest_id, {})
    if not replacements:
        return requirements
    changed = False
    rows = []
    for requirement in requirements:
        replacement_rows = []
        for encounter in requirement.combat_encounters:
            replacement = replacements.get(encounter.encounter_id)
            if replacement is None:
                replacement_rows.append(encounter)
            elif isinstance(replacement, tuple):
                replacement_rows.extend(replacement)
            else:
                replacement_rows.append(replacement)
        combat_encounters = tuple(replacement_rows)
        if combat_encounters != requirement.combat_encounters:
            changed = True
            requirement = replace(requirement, combat_encounters=combat_encounters)
        rows.append(requirement)
    return tuple(rows) if changed else requirements


def _remove_stage_item_names(
    items: Tuple[Tuple[str, int], ...],
    item_names: Tuple[str, ...],
) -> Tuple[Tuple[str, int], ...]:
    if not item_names:
        return items
    names = set(item_names)
    return tuple((name, amount) for name, amount in items if name not in names)


def _remove_stage_option_item_names(
    option_groups: Tuple[Tuple[Tuple[str, int], ...], ...],
    item_names: Tuple[str, ...],
) -> Tuple[Tuple[Tuple[str, int], ...], ...]:
    if not item_names:
        return option_groups
    names = set(item_names)
    cleaned_groups = []
    for option_group in option_groups:
        cleaned_options = tuple((name, amount) for name, amount in option_group if name not in names)
        if cleaned_options:
            cleaned_groups.append(cleaned_options)
    return tuple(cleaned_groups)


def _append_unique_strings(existing: Tuple[str, ...], additions: Tuple[str, ...]) -> Tuple[str, ...]:
    rows = list(existing)
    for value in additions:
        if value and value not in rows:
            rows.append(value)
    return tuple(rows)


def _append_stage_item_pairs(
    existing: Tuple[Tuple[str, int], ...],
    additions: Tuple[Tuple[str, int], ...],
) -> Tuple[Tuple[str, int], ...]:
    rows = list(existing)
    names = {name for name, _ in rows}
    for name, amount in additions:
        if not name:
            continue
        if name in names:
            rows = [(row_name, max(row_amount, amount) if row_name == name else row_amount) for row_name, row_amount in rows]
            continue
        rows.append((name, amount))
        names.add(name)
    return tuple(rows)


def _apply_stage_requirement_cleanup(
    requirement: QuestStageRequirement,
    cleanup: QuestStageRequirementCleanup,
) -> QuestStageRequirement:
    required_actions = tuple(
        action for action in requirement.required_actions if action not in set(cleanup.remove_required_actions)
    )
    required_routes = tuple(
        route for route in requirement.required_routes if route not in set(cleanup.remove_required_routes)
    )
    return replace(
        requirement,
        required_inventory=_remove_stage_item_names(requirement.required_inventory, cleanup.remove_required_inventory),
        required_inventory_options=_remove_stage_option_item_names(
            requirement.required_inventory_options,
            cleanup.remove_required_inventory_options,
        ),
        consumed_inventory=_append_stage_item_pairs(
            _remove_stage_item_names(requirement.consumed_inventory, cleanup.remove_consumed_inventory),
            cleanup.add_consumed_inventory,
        ),
        consumed_inventory_options=_remove_stage_option_item_names(
            requirement.consumed_inventory_options,
            cleanup.remove_consumed_inventory_options,
        ),
        produced_inventory=_append_stage_item_pairs(requirement.produced_inventory, cleanup.add_produced_inventory),
        required_tools=_remove_stage_item_names(requirement.required_tools, cleanup.remove_required_tools),
        required_actions=_append_unique_strings(required_actions, cleanup.add_required_actions),
        auto_actions=_append_unique_strings(requirement.auto_actions, cleanup.add_auto_actions),
        required_routes=_append_unique_strings(required_routes, cleanup.add_required_routes),
        source=cleanup.source or requirement.source,
    )


def _apply_stage_requirement_cleanups(
    quest_id: str,
    requirements: Tuple[QuestStageRequirement, ...],
) -> Tuple[QuestStageRequirement, ...]:
    cleanups = QUEST_STAGE_REQUIREMENT_CLEANUPS_BY_ID.get(quest_id)
    if not cleanups:
        return requirements
    changed = False
    rows = []
    for requirement in requirements:
        updated = requirement
        for cleanup in cleanups:
            if requirement.stage != cleanup.stage:
                continue
            if cleanup.variant and cleanup.variant != requirement.variant:
                continue
            updated = _apply_stage_requirement_cleanup(updated, cleanup)
        changed = changed or updated != requirement
        rows.append(updated)
    return tuple(rows) if changed else requirements


def _quest_with_stage_requirements(quest: QuestDefinition, row: Dict[str, object]) -> QuestDefinition:
    replacements = QUEST_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID.get(quest.id)
    if replacements is not None:
        base = replacements
    elif quest.stage_requirements:
        base = quest.stage_requirements
    else:
        base = _catalog_stage_requirements(row.get("stage_requirements", ()))

    additions = QUEST_STAGE_REQUIREMENT_ADDITIONS_BY_ID.get(quest.id, ())
    requirements = _apply_combat_encounter_replacements(
        quest.id,
        _apply_stage_requirement_cleanups(
            quest.id,
            _dedupe_stage_requirements((*base, *additions)),
        ),
    )
    max_requirement_stage = max((requirement.stage for requirement in requirements), default=0)
    configured_stages = QUEST_STAGE_COUNT_REPLACEMENTS_BY_ID.get(quest.id, quest.stages)
    stages = max(configured_stages, max_requirement_stage + 1)
    journal_stages = QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID.get(quest.id, quest.journal_stages)
    combat = QUEST_COMBAT_TEXT_REPLACEMENTS_BY_ID.get(quest.id, quest.combat)
    choices = QUEST_CHOICE_REPLACEMENTS_BY_ID.get(quest.id, quest.choices)
    if (
        requirements == quest.stage_requirements
        and stages == quest.stages
        and journal_stages == quest.journal_stages
        and combat == quest.combat
        and choices == quest.choices
    ):
        return quest
    return replace(
        quest,
        stages=stages,
        journal_stages=journal_stages,
        combat=combat,
        stage_requirements=requirements,
        choices=choices,
    )


# ---- Miniquests -----------------------------------------------------------
# The pre-EOC quest catalog is built from the wiki's quest release list, which
# does not carry miniquests. These rows are written by hand from the pinned
# period record and join the same ledger, storage and unlock engine; only the
# Quests tab groups them apart. Miniquests award no quest points, which
# `Miniquests` oldid 6020341 states outright.

HUNT_FOR_SUROK_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "I can start this miniquest by speaking to Surok after mining the",
        "statue of Saradomin to gain access to the Tunnels of Chaos.",
    ),
    _simple_stage(2, "I confronted Surok outside the statue and he fled into the tunnels beneath."),
    _simple_stage(
        3,
        "I found Surok fleeing from the Tunnels of Chaos and into a portal",
        "leading into the Chaos Tunnels.",
    ),
    _simple_stage(4, "I found Surok again near the fire giants but he fled off to the south."),
    _simple_stage(
        5,
        "I found Surok again near the skeletons next to the moss giant room",
        "but he got away again fleeing to the west.",
    ),
    _simple_stage(
        6,
        "I managed to defeat Bork but Surok managed to escape somewhere unknown.",
        "Miniquest complete!",
    ),
)

LAIR_OF_TARN_RAZORLOR_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "Odovacar the banker told me that Tarn Razorlor still haunts the",
        "abandoned mine west of Burgh de Rott. I should climb down into",
        "his lair and see what became of him.",
    ),
    _simple_stage(
        2,
        "I am inside Tarn's Lair. Odovacar keeps a bank at the end of the",
        "northern hall, behind two wall traps I will have to search out.",
    ),
    _simple_stage(
        3,
        "I reached Odovacar's bank. Beyond it the lair is a maze of floor",
        "traps, swinging logs and pillars I must jump between.",
    ),
    _simple_stage(
        4,
        "I crossed the trapped halls. The last pillar room is watched by two",
        "skeleton mages; past it a stairway leads down to Tarn's chamber.",
    ),
    _simple_stage(
        5,
        "Tarn transformed into a lashing green mutant and set two terror dogs",
        "on me.",
    ),
    _simple_stage(
        6,
        "The mutant fell, but Tarn rose again as a ghost. This form is the",
        "weaker of the two.",
    ),
    _simple_stage(
        7,
        "Tarn is dead and the room beyond his chamber has opened. His diary",
        "is on the table inside.",
    ),
    _simple_stage(
        8,
        "I took Tarn's diary from his bedroom. Reading it over a salve amulet",
        "would enchant the amulet against the undead.",
        "Miniquest complete!",
    ),
)

HUNT_FOR_SUROK_STAGE_REQUIREMENTS: Tuple[QuestStageRequirement, ...] = (
    _stage_req(
        1,
        "Excavate the statue of Saradomin and confront Surok, who flees into the tunnel below.",
        f"{HUNT_FOR_SUROK_WIKI_SOURCE}; {HUNT_FOR_SUROK_DARKAN_SOURCE}",
        required_tools=(("Pickaxe", 1),),
        auto_actions=(
            "Ask Anna Jones to let you at the statue, then excavate it with a pickaxe",
            "Attempt to arrest Surok and watch him slip into the Tunnel of Chaos",
        ),
    ),
    _stage_req(
        2,
        "Follow Surok through the Tunnel of Chaos, past Dakh'thoulan Aegis, into the Chaos Tunnels.",
        f"{HUNT_FOR_SUROK_WIKI_SOURCE}; {HUNT_FOR_SUROK_DARKAN_SOURCE}",
        auto_actions=(
            "Enter the opening under the statue and head north through the Tunnel of Chaos",
            "Take the footprinted portal in Dakh'thoulan Aegis's room",
        ),
    ),
    _stage_req(
        3,
        "Catch Surok in the red spider room, where he kills two fire giants outright, and follow him south.",
        HUNT_FOR_SUROK_WIKI_SOURCE,
        auto_actions=(
            "Cross the multi-combat caverns by their footprinted portals",
            "Watch Surok destroy two fire giants and take the southern portal after him",
        ),
    ),
    _stage_req(
        4,
        "Catch Surok in the skeleton room and get past the two wolves he summons.",
        HUNT_FOR_SUROK_WIKI_SOURCE,
        auto_actions=(
            "Confront Surok among the skeletons beside the moss giant room",
            "Run past the two summoned wolves to the western portal",
        ),
    ),
    _stage_req(
        5,
        "Enter the last portal in the Dagannoth chamber and defeat Bork.",
        (
            f"{HUNT_FOR_SUROK_WIKI_SOURCE}; {HUNT_FOR_SUROK_BORK_SOURCE}; "
            f"{HUNT_FOR_SUROK_BORK_DARKAN_SOURCE}"
        ),
        auto_actions=(
            "Take the western footprinted portal out of the Dagannoth chamber",
            "Grab Bork's drops and leave before the cave collapses",
        ),
        combat_encounters=(
            _combat(
                HUNT_FOR_SUROK_ID,
                "bork",
                "Bork",
                267,
                (
                    f"{HUNT_FOR_SUROK_WIKI_SOURCE}; {HUNT_FOR_SUROK_BORK_SOURCE}; "
                    f"{HUNT_FOR_SUROK_BORK_DARKAN_SOURCE}; {HUNT_FOR_SUROK_BORK_HANDLER_SOURCE}"
                ),
                (
                    "Bork is a level 267 aggressive Ork immune to poison, with 3,000 life points, "
                    "crush attacks at speed 6 and a maximum hit of 254. At 2,000 life points he "
                    "calls three to nine level 70 orks of the Ork legion, and Surok bombards the "
                    "fight for up to 350 every fifteen seconds. A quest stage resolves one "
                    "attacker, so both pressures stay narration here; the walkthrough tells the "
                    "player to ignore the legions, and the repeatable Bork context is where every "
                    "attacker in the room is fought review by review."
                ),
                # PLACEHOLDER(dominion_tower.unsourced_boss_stat_blocks): Darkan's
                # Bork row is a "nostats" file whose combat levels are all zero, so
                # the core stats use the registered conversion exactly — 72% of the
                # combat level capped at 99, in all four stats. Copying the composite
                # level 267 straight into the stats would make him unhittable and
                # unsurvivable.
                npc_stats=(
                    ("hitpoints", 3000),
                    ("attack", 99),
                    ("strength", 99),
                    ("defence", 99),
                    ("magic", 99),
                ),
                npc_configs=(
                    ("max_hit", 254),
                    ("attack_speed", 6),
                    ("attack_style", "melee"),
                    ("attack_bonus", "crush_att"),
                    ("aggressiveness_type", "aggressive"),
                    # `Bork` oldid 6565904 prints `immune to poison = Yes`, and
                    # Darkan's `Bork.processEntity()` resets poison every tick.
                    ("poison_immune", True),
                    # The period states no player combat requirement for Bork — his own
                    # Slayer requirement is level 1 — so the miniquest gate is the only
                    # gate, and the enemy level must not become an invented one.
                    ("minimum_player_combat", 1),
                ),
                npc_stats_source=(
                    "Period life points, maximum hit, attack speed and crush style, matched by "
                    "Darkan's combat definition; hidden combat stats use the settled "
                    "72%-of-combat-level conversion, capped at 99"
                ),
            ),
        ),
    ),
)

LAIR_OF_TARN_RAZORLOR_STAGE_REQUIREMENTS: Tuple[QuestStageRequirement, ...] = (
    _stage_req(
        1,
        "Climb into the abandoned mine west of Burgh de Rott and follow the path north into Tarn's Lair.",
        f"{LAIR_OF_TARN_RAZORLOR_WIKI_SOURCE}; {MINIQUEST_LIST_SOURCE}",
        auto_actions=(
            "Climb over the mine cart and crawl down the cart tunnel",
            "Follow the first level of the mine north to its end",
        ),
    ),
    _stage_req(
        2,
        "Search out the two wall traps on the northern hall and reach Odovacar's bank room.",
        LAIR_OF_TARN_RAZORLOR_WIKI_SOURCE,
        auto_actions=(
            "Pass the floor traps east to the end of the entrance passage",
            "Disarm the southern and northern wall traps by searching them",
        ),
    ),
    _stage_req(
        3,
        "Take the D-S-T route through the floor traps to the western pillar room and drop the log swing.",
        LAIR_OF_TARN_RAZORLOR_WIKI_SOURCE,
        auto_actions=(
            "Cross the six-trap room through Doorway S and the three-trap room through Doorway T",
            "Jump the southern pillars and search the flagstone to deactivate the log swing",
        ),
    ),
    _stage_req(
        4,
        "Time the pit room's walls, cross the second pillar room past two level 94 skeleton mages, and take Doorway U.",
        LAIR_OF_TARN_RAZORLOR_WIKI_SOURCE,
        auto_actions=(
            "Time the shifting walls so the pit never takes you",
            "Zigzag the pillars while the skeleton mages fire, then descend Doorway U",
        ),
    ),
    _stage_req(
        5,
        "Defeat Tarn's mutant form with two level 110 terror dogs loose in the chamber.",
        (
            f"{LAIR_OF_TARN_RAZORLOR_WIKI_SOURCE}; {LAIR_OF_TARN_RAZORLOR_TARN_SOURCE}; "
            f"{LAIR_OF_TARN_RAZORLOR_TERROR_DOG_SOURCE}; "
            f"{LAIR_OF_TARN_RAZORLOR_MUTANT_TARN_DARKAN_SOURCE}; "
            f"{LAIR_OF_TARN_RAZORLOR_TERROR_DOG_DARKAN_SOURCE}"
        ),
        combat_encounters=(
            _combat(
                LAIR_OF_TARN_RAZORLOR_ID,
                "mutant_tarn",
                "Mutant tarn",
                69,
                (
                    f"{LAIR_OF_TARN_RAZORLOR_WIKI_SOURCE}; {LAIR_OF_TARN_RAZORLOR_TARN_SOURCE}; "
                    f"{LAIR_OF_TARN_RAZORLOR_MUTANT_TARN_DARKAN_SOURCE}"
                ),
                (
                    "The cutscene turns Tarn into a level 69 mutant with 650 life points, attacks "
                    "at speed 5 and an approximate maximum hit of 190. The infobox lists melee and "
                    "magic, but the same revision's strategy section says he \"attacks solely with "
                    "melee if approached\" — which is every AnkiScape battle — so this fight is "
                    "melee, exactly as Darkan's file has it. Two level 110 terror dogs enter with "
                    "him. A quest stage resolves one attacker, so they stay narration on the same "
                    "terms as Bork's legions; the source says Tarn is the only monster that must "
                    "die, and the period lets a player manoeuvre the dogs behind him to escape "
                    "them entirely."
                ),
                # PLACEHOLDER(lair_of_tarn_razorlor.mutant_tarn_stat_block): Darkan's
                # mutant file is a "nostats" row with every combat level zeroed, so
                # the ghost form's block stands in for the mutant's. The two forms
                # share a level, life-point total, maximum hit and attack speed in the
                # period record, which is why the substitution is the same body twice.
                npc_stats=(
                    ("hitpoints", 650),
                    ("attack", 40),
                    ("strength", 80),
                    ("defence", 40),
                    ("magic", 1),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 190),
                    ("attack_speed", 5),
                    ("attack_style", "melee"),
                    ("attack_bonus", "crush_att"),
                    ("aggressiveness_type", "aggressive"),
                    # Slayer 40 is the period gate and it is already a quest requirement,
                    # so the enemy level must not add a second, unsourced one.
                    ("minimum_player_combat", 1),
                ),
                npc_stats_source=(
                    f"Period level, life points, maximum hit and attack speed from "
                    f"{LAIR_OF_TARN_RAZORLOR_MUTANT_TARN_DARKAN_SOURCE}, which states no combat "
                    f"levels; the block stands in from the ghost form's "
                    f"{LAIR_OF_TARN_RAZORLOR_TARN_DARKAN_SOURCE}"
                ),
            ),
        ),
    ),
    _stage_req(
        6,
        "Defeat the ghost Tarn rises as when his mutant form falls.",
        (
            f"{LAIR_OF_TARN_RAZORLOR_WIKI_SOURCE}; {LAIR_OF_TARN_RAZORLOR_TARN_SOURCE}; "
            f"{LAIR_OF_TARN_RAZORLOR_TARN_DARKAN_SOURCE}"
        ),
        combat_encounters=(
            _combat(
                LAIR_OF_TARN_RAZORLOR_ID,
                "tarn_ghost",
                "Tarn",
                69,
                (
                    f"{LAIR_OF_TARN_RAZORLOR_WIKI_SOURCE}; {LAIR_OF_TARN_RAZORLOR_TARN_SOURCE}; "
                    f"{LAIR_OF_TARN_RAZORLOR_TARN_DARKAN_SOURCE}"
                ),
                (
                    "Tarn's ghost keeps level 69, 650 life points and the approximate 190 maximum "
                    "hit, but attacks with melee alone, which is why the source calls it the easier "
                    "form. Poison carried over from the mutant form persists."
                ),
                npc_stats=(
                    ("hitpoints", 650),
                    ("attack", 40),
                    ("strength", 80),
                    ("defence", 40),
                    ("magic", 1),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 190),
                    ("attack_speed", 5),
                    ("attack_style", "melee"),
                    ("attack_bonus", "crush_att"),
                    ("aggressiveness_type", "aggressive"),
                    ("minimum_player_combat", 1),
                ),
                npc_stats_source=(
                    f"Period level, life points, maximum hit and attack speed; combat levels from "
                    f"{LAIR_OF_TARN_RAZORLOR_TARN_DARKAN_SOURCE}"
                ),
            ),
        ),
    ),
    _stage_req(
        7,
        "Take Tarn's diary from the table in the room his death opens.",
        LAIR_OF_TARN_RAZORLOR_WIKI_SOURCE,
        auto_actions=(
            "Enter Tarn's bedroom once the wall opens",
            "Take Tarn's diary from the table",
        ),
    ),
)


MINIQUESTS: Tuple[QuestDefinition, ...] = (
    QuestDefinition(
        id=HUNT_FOR_SUROK_ID,
        display_name="The Hunt for Surok",
        stages=len(HUNT_FOR_SUROK_STAGES),
        point_reward=0,
        rewards=(),
        start_point="Speak to Surok by the statue of Saradomin, east of Varrock.",
        requirements=("What Lies Below", "Mining 42"),
        required_items=(),
        combat="Bork: level 267, 3,000 life points, maximum hit 254.",
        source=(
            f"{HUNT_FOR_SUROK_WIKI_SOURCE}; {MINIQUEST_LIST_SOURCE}; "
            f"{HUNT_FOR_SUROK_DARKAN_SOURCE}; {HUNT_FOR_SUROK_MINIQUEST_ENUM_SOURCE}"
        ),
        journal_stages=HUNT_FOR_SUROK_STAGES,
        release_date="2008-03-04",
        members=True,
        # PLACEHOLDER(hunt_for_surok.difficulty_label): the pinned page's quest
        # details block carries `wdifficulty=4` and no difficulty word, and the
        # miniquest list carries no difficulty column at all.
        difficulty="Special",
        length="Short to Medium",
        timeline="Fifth Age",
        # The release list the catalog is built from carries no miniquests, so
        # they take the catalog's own unknown-order value and sort last.
        release_order=9999,
        required_quests=(QuestPrerequisite(WHAT_LIES_BELOW_ID, "What Lies Below"),),
        # What Lies Below already demands Mining 42, so this row can never be the
        # binding gate. It is kept because it is the miniquest's own stated
        # requirement and stage 1 spends it on the statue; the prerequisite quest
        # is a separate fact that happens to cover it today. Its unannotated
        # sibling Slayer 44 is dropped instead — see the source audit, which
        # records both readings.
        required_skills=(QuestSkillRequirement("mining", "Mining", 42),),
        xp_rewards=(QuestXpReward("slayer", 5000),),
        unlocks=(
            "Ability to fight Bork in the Chaos Tunnels once per day",
            "Ability to wear Dagon'hai robes",
        ),
        stage_requirements=HUNT_FOR_SUROK_STAGE_REQUIREMENTS,
        miniquest=True,
    ),
    QuestDefinition(
        id=LAIR_OF_TARN_RAZORLOR_ID,
        display_name="The Lair of Tarn Razorlor",
        stages=len(LAIR_OF_TARN_RAZORLOR_STAGES),
        point_reward=0,
        rewards=(),
        start_point=(
            "Talk to Odovacar the banker in the abandoned mine west of Burgh de Rott."
        ),
        requirements=("Haunted Mine", "Slayer 40"),
        required_items=(),
        combat="Tarn Razorlor: a level 69 mutant form, then a level 69 ghost form.",
        source=(
            f"{LAIR_OF_TARN_RAZORLOR_WIKI_SOURCE}; {MINIQUEST_LIST_SOURCE}; "
            f"{LAIR_OF_TARN_RAZORLOR_TARN_SOURCE}"
        ),
        journal_stages=LAIR_OF_TARN_RAZORLOR_STAGES,
        release_date="2007-01-22",
        members=True,
        # PLACEHOLDER(lair_of_tarn_razorlor.difficulty_label): the pinned page
        # carries no quest details block, so it states neither a difficulty word
        # nor the numeric grade its sibling page carries.
        difficulty="Special",
        # PLACEHOLDER(lair_of_tarn_razorlor.length_label): the same missing block
        # is the only place a length would have been stated.
        length="Short",
        timeline="Fifth Age",
        release_order=9999,
        required_quests=(QuestPrerequisite(HAUNTED_MINE_ID, "Haunted Mine"),),
        required_skills=(QuestSkillRequirement("slayer", "Slayer", 40),),
        xp_rewards=(QuestXpReward("slayer", 5000),),
        unlocks=(
            "Tarn's diary",
            "Ability to enchant a salve amulet into a Salve amulet (e)",
        ),
        stage_requirements=LAIR_OF_TARN_RAZORLOR_STAGE_REQUIREMENTS,
        miniquest=True,
    ),
)

QUESTS: Tuple[QuestDefinition, ...] = tuple(
    _quest_with_stage_requirements(
        replace(QUEST_OVERRIDES_BY_ID[row_id], release_order=_catalog_int(row, "release_order", 9999))
        if row_id in QUEST_OVERRIDES_BY_ID
        else _quest_from_catalog(row),
        row,
    )
    for row in PRE_EOC_QUEST_CATALOG
    for row_id in (_quest_catalog_row_id(row),)
) + tuple(
    _quest_with_stage_requirements(quest, {}) for quest in MINIQUESTS
)
QUESTS_BY_ID: Dict[str, QuestDefinition] = {quest.id: quest for quest in QUESTS}
QUEST_DISPLAY_NAMES: Dict[str, str] = {quest.id: quest.display_name for quest in QUESTS}

# Compatibility export retained for callers that were added during the first
# quest-lock pass. Unlock quest ids now all resolve to playable QuestDefinition
# rows, so there are no state-only references left.
QUEST_REFERENCES: Tuple[QuestReference, ...] = ()
QUEST_REFERENCES_BY_ID: Dict[str, QuestReference] = {}

QUEST_UNLOCK_RULES: Tuple[QuestUnlockRule, ...] = (
    QuestUnlockRule(RUNE_MYSTERIES_ID, "target", "mining", ("rune_essence",), "Rune Mysteries", RUNE_ESSENCE_MINE_SOURCE),
    QuestUnlockRule(
        LOST_CITY_ID,
        "target",
        "runecrafting",
        ("craft_cosmic_runes", "bind_cosmic_tiara", "feed_cosmic_talisman_to_hood", "feed_cosmic_tiara_to_hood"),
        "Lost City",
        RUNECRAFTING_BASICS_SOURCE,
    ),
    QuestUnlockRule(LUNAR_DIPLOMACY_ID, "target", "runecrafting", ("craft_astral_runes",), "Lunar Diplomacy", RUNECRAFTING_ALTARS_SOURCE),
    QuestUnlockRule(
        MOURNINGS_END_PART_II_ID,
        "target",
        "runecrafting",
        ("craft_death_runes", "bind_death_tiara", "feed_death_talisman_to_hood", "feed_death_tiara_to_hood"),
        "Mourning's End Part II",
        RUNECRAFTING_BASICS_SOURCE,
    ),
    QuestUnlockRule(
        LEGACY_OF_SEERGAZE_ID,
        "target",
        "runecrafting",
        ("craft_blood_runes", "bind_blood_tiara", "feed_blood_talisman_to_hood", "feed_blood_tiara_to_hood"),
        "Legacy of Seergaze",
        RUNECRAFTING_BASICS_SOURCE,
    ),
    QuestUnlockRule(SWAN_SONG_ID, "target", "fishing", ("catch_monkfish",), "Swan Song", RAW_MONKFISH_SOURCE),
    QuestUnlockRule(TAI_BWO_WANNAI_TRIO_ID, "target", "fishing", ("catch_karambwan",), "Tai Bwo Wannai Trio", RAW_KARAMBWAN_SOURCE),
    QuestUnlockRule(
        TAI_BWO_WANNAI_TRIO_ID,
        "target",
        "cooking",
        ("cook_karambwan_thoroughly",),
        "Tai Bwo Wannai Trio + Tiadeche instruction",
        "https://runescape.wiki/w/Cooked_karambwan?oldid=6154936",
    ),
    QuestUnlockRule(
        TAI_BWO_WANNAI_TRIO_ID,
        "target",
        "cooking",
        ("cook_karambwanji",),
        "Tai Bwo Wannai Trio",
        "https://runescape.wiki/w/Karambwanji?oldid=5838218",
    ),
    QuestUnlockRule(SHILO_VILLAGE_ID, "target", "mining", ("gem_rocks",), "Shilo Village", GEM_ROCK_SOURCE),
    QuestUnlockRule(
        JUNGLE_POTION_ID,
        "target",
        "utility",
        JUNGLE_POTION_SEARCH_ACTIVITY_IDS,
        "Jungle Potion",
        JUNGLE_POTION_POST_QUEST_SEARCH_SOURCE,
    ),
    QuestUnlockRule(PRIEST_IN_PERIL_ID, "target", "fishing", ("catch_slimy_eel",), "Priest in Peril", PRIEST_IN_PERIL_SOURCE),
    QuestUnlockRule(
        PRIEST_IN_PERIL_ID,
        "target",
        "cooking",
        ("cook_slimy_eel", "cook_thin_snail", "cook_lean_snail", "cook_fat_snail"),
        "Priest in Peril",
        PRIEST_IN_PERIL_SOURCE,
    ),
    QuestUnlockRule(
        PRIEST_IN_PERIL_ID,
        "target",
        "utility",
        ("gather_lean_snails", "gather_fat_snails"),
        "Priest in Peril",
        PRIEST_IN_PERIL_SOURCE,
    ),
    QuestUnlockRule(THE_FREMENNIK_ISLES_ID, "target", "cooking", ("cook_yak",), "The Fremennik Isles", THE_FREMENNIK_ISLES_SOURCE),
    QuestUnlockRule(DWARF_CANNON_ID, "target", "smithing", ("forge_cannonballs",), "Dwarf Cannon", "https://runescape.wiki/w/Cannonball?oldid=6541276"),
    # scavenge_raw_yak_meat retired 2026-07-07 (Raw yak meat is live shop
    # stock); the cook_yak Cooking rule below keeps the Fremennik Isles gate.
    QuestUnlockRule(EAGLES_PEAK_ID, "target", "hunter", ("catch_ferret",), "Eagles' Peak", HUNTER_EAGLES_PEAK_SOURCE),
    QuestUnlockRule(AS_A_FIRST_RESORT_ID, "target", "hunter", ("catch_wimpy_bird",), "As a First Resort", HUNTER_AS_A_FIRST_RESORT_SOURCE),
    QuestUnlockRule(AS_A_FIRST_RESORT_ID, "target", "mining", ("red_sandstone",), "As a First Resort", RED_SANDSTONE_SOURCE),
    QuestUnlockRule(AS_A_FIRST_RESORT_ID, "target", "utility", ("make_robust_glass",), "As a First Resort", ROBUST_GLASS_SOURCE),
    QuestUnlockRule(ROCKING_OUT_ID, "target", "hunter", ("catch_pirate_impling_puro_puro", "catch_pirate_impling_world"), "Rocking Out", HUNTER_ROCKING_OUT_SOURCE),
    QuestUnlockRule(PRIEST_IN_PERIL_ID, "target", "hunter", ("catch_swamp_lizard",), "Priest in Peril", HUNTER_PRIEST_IN_PERIL_SOURCE),
    QuestUnlockRule(
        "the_golem",
        "target",
        "utility",
        ("grab_desert_phoenix_feather",),
        "The Golem",
        "https://runescape.wiki/w/Desert_Phoenix?oldid=6295341",
    ),
    QuestUnlockRule(
        "throne_of_miscellania",
        "target",
        "utility",
        ("managing_miscellania",),
        "Throne of Miscellania",
        "https://runescape.wiki/w/Managing_Miscellania?oldid=6500793",
    ),
)


def _quest_target_unlock_rule(rule: QuestUnlockRule) -> TargetUnlockRule:
    return TargetUnlockRule(
        gate_kind=rule.gate_kind,
        skill_id=rule.skill_id,
        target_ids=rule.target_ids,
        requirements=(
            TargetUnlockRequirement(
                kind="quest_completed",
                reason=rule.reason,
                source=rule.source,
                quest_id=rule.quest_id,
            ),
        ),
    )


TARGET_UNLOCK_RULES: Tuple[TargetUnlockRule, ...] = tuple(
    _quest_target_unlock_rule(rule) for rule in QUEST_UNLOCK_RULES
) + (
    TargetUnlockRule(
        gate_kind="target",
        skill_id="cooking",
        target_ids=("cook_poison_karambwan",),
        requirements=(
            TargetUnlockRequirement(
                kind="quest_started",
                reason="Start Tai Bwo Wannai Trio",
                source="https://runescape.wiki/w/Poison_karambwan?oldid=6250179",
                quest_id=TAI_BWO_WANNAI_TRIO_ID,
            ),
        ),
    ),
    TargetUnlockRule(
        gate_kind="target",
        skill_id="firemaking",
        target_ids=("arctic_pine_logs",),
        requirements=(
            TargetUnlockRequirement(
                kind="quest_started",
                reason="Start The Fremennik Isles",
                source=THE_FREMENNIK_ISLES_SOURCE,
                quest_id=THE_FREMENNIK_ISLES_ID,
            ),
        ),
    ),
    TargetUnlockRule(
        gate_kind="target",
        skill_id="woodcutting",
        target_ids=("arctic_pine", "split_arctic_pine_logs"),
        requirements=(
            TargetUnlockRequirement(
                kind="quest_started",
                reason="Start The Fremennik Isles",
                source=THE_FREMENNIK_ISLES_SOURCE,
                quest_id=THE_FREMENNIK_ISLES_ID,
            ),
        ),
    ),
    TargetUnlockRule(
        gate_kind="target",
        skill_id="fletching",
        target_ids=("broad_arrows", "feather_broad_bolts"),
        requirements=(
            TargetUnlockRequirement(
                kind="ability_unlocked",
                reason="Broad Fletching",
                source=BROAD_FLETCHING_SOURCE,
                ability_id=BROAD_FLETCHING_ABILITY,
            ),
        ),
    ),
    TargetUnlockRule(
        gate_kind="target",
        skill_id="fishing",
        target_ids=("catch_leaping_fish",),
        requirements=(
            TargetUnlockRequirement(
                kind="ability_unlocked",
                reason="Barbarian Fishing",
                source=BARBARIAN_FISHING_SOURCE,
                ability_id=BARBARIAN_FISHING_ABILITY,
            ),
        ),
    ),
)


def _lamp_claim_id(quest: QuestDefinition, index: int) -> str:
    return f"{quest.id}_xp_lamp_{index}"


def _quest_lamp_claims() -> Tuple[ClaimDefinition, ...]:
    claims = []
    for quest in QUESTS:
        lamp_index = 1
        for lamp in quest.lamp_rewards:
            if lamp.amount <= 0 or not lamp.skill_options:
                continue
            for _ in range(max(1, int(lamp.quantity))):
                claims.append(
                    ClaimDefinition(
                        id=_lamp_claim_id(quest, lamp_index),
                        display_name=f"{quest.display_name}: {lamp.display_name} ({int(lamp.amount):,} XP)",
                        source=lamp.source or quest.source,
                        claim_type="xp_lamp",
                        required_quest=quest.id,
                        xp_amount=lamp.amount,
                        skill_options=lamp.skill_options,
                        minimum_level=max(1, int(lamp.minimum_level)),
                    )
                )
                lamp_index += 1
    return tuple(claims)


TUTORIAL_ISLAND_STARTER_KIT_ITEMS: Tuple[Tuple[str, int], ...] = (
    ("Bronze sword", 1),
    ("Wooden shield", 1),
    ("Shortbow", 1),
    ("Bronze arrows", 50),
    ("Air rune", 5),
    ("Mind rune", 5),
    ("Bronze pickaxe", 1),
    ("Hammer", 1),
    ("Bronze hatchet", 1),
    ("Tinderbox", 1),
    ("Small fishing net", 1),
)


CLAIMS: Tuple[ClaimDefinition, ...] = (
    ClaimDefinition(
        id="wicked_hood",
        display_name="Wicked hood",
        source="https://runescape.wiki/w/Wicked_hood",
        item_name=WICKED_HOOD_ITEM,
        quantity=1,
    ),
    ClaimDefinition(
        id="tutorial_island_starter_kit",
        display_name="Tutorial Island starter kit",
        source=DARKAN_TUTORIAL_STARTER_KIT_SOURCE,
        claim_type="item_bundle",
        item_name="Bronze sword",
        items=TUTORIAL_ISLAND_STARTER_KIT_ITEMS,
        required_quest="",
    ),
    ClaimDefinition(
        id="diamond_in_the_rough_scabaras_tomb",
        display_name="Mine the Scabaras tomb fissure",
        source=f"{DIAMOND_IN_THE_ROUGH_WIKI_SOURCE}; {DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}",
        claim_type="skill_reward",
        item_name="Scabaras mask",
        items=(("Scabaras mask", 1), ("Was", 1)),
        required_quest="diamond_in_the_rough",
        xp_amount=20000,
        skill_options=("mining",),
        minimum_level=80,
    ),
    ClaimDefinition(
        id="diamond_in_the_rough_apmeken_tomb",
        display_name="Climb into the Apmeken tomb fissure",
        source=f"{DIAMOND_IN_THE_ROUGH_WIKI_SOURCE}; {DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}",
        claim_type="skill_reward",
        item_name="Apmeken mask",
        items=(("Apmeken mask", 1), ("Ankh", 1)),
        required_quest="diamond_in_the_rough",
        xp_amount=20000,
        skill_options=("agility",),
        minimum_level=80,
    ),
    *_quest_lamp_claims(),
)
CLAIMS_BY_ID: Dict[str, ClaimDefinition] = {claim.id: claim for claim in CLAIMS}


def default_quest_states() -> Dict[str, Dict[str, object]]:
    return {quest.id: {"started": False, "progress": 0, "completed": False} for quest in QUESTS}


def default_claim_states() -> Dict[str, Dict[str, object]]:
    return {claim.id: {"claimed": False} for claim in CLAIMS}


def _quest_requirement_dict(requirement: QuestPrerequisite) -> Dict[str, object]:
    return {"quest_id": requirement.quest_id, "display_name": requirement.display_name}


def _skill_requirement_dict(requirement: QuestSkillRequirement) -> Dict[str, object]:
    return {"skill_id": requirement.skill_id, "display_name": requirement.display_name, "level": requirement.level}


def _xp_reward_dict(reward: QuestXpReward) -> Dict[str, object]:
    return {"skill_id": reward.skill_id, "amount": reward.amount}


def _lamp_reward_dict(reward: QuestLampReward) -> Dict[str, object]:
    return {
        "display_name": reward.display_name,
        "amount": reward.amount,
        "skill_options": reward.skill_options,
        "minimum_level": reward.minimum_level,
        "source": reward.source,
        "source_text": reward.source_text,
        "quantity": reward.quantity,
    }


def _quest_choice_option_dict(option: QuestChoiceOption) -> Dict[str, object]:
    return {"label": option.label, "route_id": option.route_id, "description": option.description}


def _quest_choice_dict(choice: QuestChoice) -> Dict[str, object]:
    return {
        "stage": choice.stage,
        "prompt": choice.prompt,
        "options": tuple(_quest_choice_option_dict(option) for option in choice.options),
        "source": choice.source,
    }


def _combat_encounter_dict(encounter: QuestCombatEncounter) -> Dict[str, object]:
    return {
        "encounter_id": encounter.encounter_id,
        "display_name": encounter.display_name,
        "level": encounter.level,
        "quantity": encounter.quantity,
        "source": encounter.source,
        "source_text": encounter.source_text,
        "npc_stats": dict(encounter.npc_stats),
        "npc_bonuses": dict(encounter.npc_bonuses),
        "npc_configs": dict(encounter.npc_configs),
        "npc_stats_source": encounter.npc_stats_source,
    }


def _stage_requirement_dict(requirement: QuestStageRequirement) -> Dict[str, object]:
    return {
        "stage": requirement.stage,
        "description": requirement.description,
        "variant": requirement.variant,
        "required_inventory": dict(requirement.required_inventory),
        "required_inventory_options": tuple(
            tuple({item_name: amount} for item_name, amount in option_group)
            for option_group in requirement.required_inventory_options
        ),
        "consumed_inventory": dict(requirement.consumed_inventory),
        "consumed_inventory_options": tuple(
            tuple({item_name: amount} for item_name, amount in option_group)
            for option_group in requirement.consumed_inventory_options
        ),
        "produced_inventory": dict(requirement.produced_inventory),
        "required_tools": dict(requirement.required_tools),
        "required_actions": requirement.required_actions,
        "auto_actions": requirement.auto_actions,
        "required_routes": requirement.required_routes,
        "combat_encounters": tuple(_combat_encounter_dict(encounter) for encounter in requirement.combat_encounters),
        "source": requirement.source,
    }


def quests_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        quest.id: {
            "id": quest.id,
            "display_name": quest.display_name,
            "stages": quest.stages,
            "point_reward": quest.point_reward,
            "rewards": dict(quest.rewards),
            "start_point": quest.start_point,
            "requirements": quest.requirements,
            "required_items": dict(quest.required_items),
            "start_inventory": dict(quest.start_inventory),
            "required_quests": tuple(_quest_requirement_dict(req) for req in quest.required_quests),
            "required_skills": tuple(_skill_requirement_dict(req) for req in quest.required_skills),
            "required_quest_points": quest.required_quest_points,
            "xp_rewards": tuple(_xp_reward_dict(reward) for reward in quest.xp_rewards),
            "lamp_rewards": tuple(_lamp_reward_dict(reward) for reward in quest.lamp_rewards),
            "combat": quest.combat,
            "source": quest.source,
            "release_date": quest.release_date,
            "release_order": quest.release_order,
            "members": quest.members,
            "difficulty": quest.difficulty,
            "length": quest.length,
            "timeline": quest.timeline,
            "unlocks": quest.unlocks,
            "miniquest": quest.miniquest,
            "journal_stages": {stage.stage: stage.journal for stage in quest.journal_stages},
            "stage_requirements": tuple(_stage_requirement_dict(req) for req in quest.stage_requirements),
            "choices": tuple(_quest_choice_dict(choice) for choice in quest.choices),
        }
        for quest in QUESTS
    }


def quest_references_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        quest.id: {"id": quest.id, "display_name": quest.display_name, "source": quest.source, "note": quest.note}
        for quest in QUEST_REFERENCES
    }


def target_unlock_rules_as_dict() -> Tuple[Dict[str, object], ...]:
    return tuple(
        {
            "gate_kind": rule.gate_kind,
            "skill_id": rule.skill_id,
            "target_ids": rule.target_ids,
            "requirements": tuple(
                {
                    "kind": requirement.kind,
                    "quest_id": requirement.quest_id,
                    "ability_id": requirement.ability_id,
                    "reason": requirement.reason,
                    "source": requirement.source,
                }
                for requirement in rule.requirements
            ),
        }
        for rule in TARGET_UNLOCK_RULES
    )


def quest_unlock_rules_as_dict() -> Tuple[Dict[str, object], ...]:
    return target_unlock_rules_as_dict()


def quest_reward_items_as_dict() -> Dict[str, Dict[str, object]]:
    generated_items: Dict[str, Dict[str, object]] = {}
    for row in PRE_EOC_QUEST_CATALOG:
        for reward in row.get("item_rewards", ()) or ():
            if not isinstance(reward, dict):
                continue
            item_name = _quest_reward_item_name(reward.get("item_name"))
            if not isinstance(item_name, str) or not item_name:
                continue
            generated_items[item_name] = {
                "category": str(reward.get("category", "material")),
                "source": str(reward.get("source", row.get("reward_source", row.get("source", "")))),
            }
    for rewards in QUEST_ITEM_REWARD_ADDITIONS_BY_ID.values():
        for reward in rewards:
            item_name = _quest_reward_item_name(reward.get("item_name"))
            if not isinstance(item_name, str) or not item_name:
                continue
            generated_items[item_name] = {
                "category": str(reward.get("category", "material")),
                "source": str(reward.get("source", "")),
            }
    generated_items.update({
        "Coins": {"category": "material", "source": "RuneScape currency"},
        "Rock costume": {
            "category": "material",
            "item_id": 24863,
            "tradeable": False,
            "stackable": False,
            "source": f"{SOME_LIKE_IT_COLD_WIKI_SOURCE}; {SOME_LIKE_IT_COLD_CACHE_SOURCE}",
        },
        "Pop costume": {
            "category": "material",
            "item_id": 24864,
            "tradeable": False,
            "stackable": False,
            "source": f"{SOME_LIKE_IT_COLD_WIKI_SOURCE}; {SOME_LIKE_IT_COLD_CACHE_SOURCE}",
        },
        "Ransom note": {
            "category": "material",
            "item_id": 25127,
            "tradeable": False,
            "source": (
                f"{STOLEN_HEARTS_WIKI_SOURCE}; {STOLEN_HEARTS_CACHE_SOURCE}; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "History of the Kharid-ib": {
            "category": "material",
            "item_id": 25128,
            "tradeable": False,
            "source": (
                f"{STOLEN_HEARTS_WIKI_SOURCE}; {STOLEN_HEARTS_CACHE_SOURCE}; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "Heavy weight": {
            "category": "material",
            "item_id": 25116,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{DIAMOND_IN_THE_ROUGH_WIKI_SOURCE}; "
                "https://runescape.wiki/w/Heavy_weight?oldid=6320315; "
                f"{DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "Sundial gnomon": {
            "category": "material",
            "item_id": 25118,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{DIAMOND_IN_THE_ROUGH_WIKI_SOURCE}; "
                "https://runescape.wiki/w/Sundial_gnomon?oldid=6360192; "
                f"{DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "Apmeken mask": {
            "category": "equipment",
            "equipment_slot": "head",
            "item_id": 25122,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{DIAMOND_IN_THE_ROUGH_WIKI_SOURCE}; {DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "Ankh": {
            "category": "equipment",
            "equipment_slot": "shield",
            "item_id": 25123,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{DIAMOND_IN_THE_ROUGH_WIKI_SOURCE}; {DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "Scabaras mask": {
            "category": "equipment",
            "equipment_slot": "head",
            "item_id": 25124,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{DIAMOND_IN_THE_ROUGH_WIKI_SOURCE}; {DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "Was": {
            "category": "equipment",
            "equipment_slot": "weapon",
            "item_id": 25125,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{DIAMOND_IN_THE_ROUGH_WIKI_SOURCE}; {DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "Canopic jar": {
            "category": "material",
            "item_id": 4678,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{ICTHLARINS_LITTLE_HELPER_WIKI_SOURCE}; "
                "https://runescape.wiki/w/Canopic_jar?oldid=6315491; "
                f"{ICTHLARINS_LITTLE_HELPER_CACHE_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}"
            ),
        },
        "Sphinx's token": {
            "category": "material",
            "item_id": 4691,
            "tradeable": False,
            "stackable": False,
            "source": (
                "https://runescape.wiki/w/Sphinx%27s_token?oldid=6520569; "
                f"{ICTHLARINS_LITTLE_HELPER_CACHE_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}"
            ),
        },
        "Holy symbol (Icthlarin's Little Helper)": {
            "category": "material",
            "item_id": 4682,
            "tradeable": False,
            "stackable": False,
            "source": (
                "https://runescape.wiki/w/Holy_symbol_%28Icthlarin%27s_Little_Helper%29?oldid=6352893; "
                f"{ICTHLARINS_LITTLE_HELPER_CACHE_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}"
            ),
        },
        "Unholy symbol (Icthlarin's Little Helper)": {
            "category": "material",
            "item_id": 4683,
            "tradeable": False,
            "stackable": False,
            "source": (
                "https://runescape.wiki/w/Unholy_symbol_%28Icthlarin%27s_Little_Helper%29?oldid=6315484; "
                f"{ICTHLARINS_LITTLE_HELPER_CACHE_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}"
            ),
        },
        "Bucket of sap": {
            "category": "material",
            "item_id": 4687,
            "tradeable": False,
            "stackable": False,
            "source": (
                "https://runescape.wiki/w/Bucket_of_sap?oldid=6288759; "
                f"{ICTHLARINS_LITTLE_HELPER_CACHE_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}"
            ),
        },
        "Pile of salt": {
            "category": "material",
            "item_id": 4689,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{ICTHLARINS_LITTLE_HELPER_WIKI_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_CACHE_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}"
            ),
        },
        "Catspeak amulet": {
            "category": "equipment",
            "item_id": 4677,
            "tradeable": False,
            "stackable": False,
            "source": (
                "https://runescape.wiki/w/Catspeak_amulet?oldid=6357174; "
                f"{ICTHLARINS_LITTLE_HELPER_CACHE_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}"
            ),
        },
        "Ghostspeak amulet": {
            "category": "equipment",
            "item_id": 552,
            "tradeable": False,
            "stackable": False,
            "source": (
                "https://runescape.wiki/w/Ghostspeak_amulet?oldid=6358472; "
                "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml item 552; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "Kitten": {
            "category": "material",
            "item_id": 1555,
            "tradeable": False,
            "stackable": False,
            "source": (
                "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml item 1555; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "Ranged path key": {
            "category": "material",
            "item_id": 13259,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{SMOKING_KILLS_WIKI_SOURCE}; "
                "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml item 13259; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "Magic path key": {
            "category": "material",
            "item_id": 13260,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{SMOKING_KILLS_WIKI_SOURCE}; "
                "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml item 13260; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "Banshee voice": {
            "category": "material",
            "item_id": 13276,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{SMOKING_KILLS_WIKI_SOURCE}; "
                "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml item 13276; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "Masked earmuffs": {
            "category": "equipment",
            "item_id": 13277,
            "tradeable": False,
            "stackable": False,
            "source": (
                "https://runescape.wiki/w/Masked_earmuffs?oldid=6283360; "
                "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml item 13277; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "Bone shard": {
            "category": "material",
            "item_id": 604,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
        },
        "Bone key": {
            "category": "material",
            "item_id": 605,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
        },
        "Stone-plaque": {
            "category": "material",
            "item_id": 606,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
        },
        "Tattered scroll": {
            "category": "material",
            "item_id": 607,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
        },
        "Crumpled scroll": {
            "category": "material",
            "item_id": 608,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
        },
        "Rashiliyia corpse": {
            "category": "material",
            "item_id": 609,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
        },
        "Zadimus corpse": {
            "category": "material",
            "item_id": 610,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
        },
        "Locating crystal": {
            "category": "material",
            "item_id": 611,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
        },
        "Beads of the dead": {
            "category": "equipment",
            "item_id": 616,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
        },
        "Bone beads": {
            "category": "material",
            "item_id": 618,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
        },
        "Sword pommel": {
            "category": "material",
            "item_id": 623,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
        },
        "Bervirius notes": {
            "category": "material",
            "item_id": 624,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
        },
        "Wampum belt": {
            "category": "material",
            "item_id": 625,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_MOSOL_SOURCE}",
        },
        "Fishing pass": {
            "category": "material",
            "source": f"{DARKAN_FISHING_CONTEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Red vine worm": {
            "category": "material",
            "source": f"{DARKAN_FISHING_CONTEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Raw giant carp": {
            "category": "fish",
            "source": f"{DARKAN_FISHING_FISH_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Fishing trophy": {
            "category": "material",
            "source": f"{DARKAN_FISHING_CONTEST_BONZO_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Garlic": {
            "category": "material",
            "source": f"{DARKAN_FISHING_CONTEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Fishing rod": {
            "category": "tool",
            "source": f"{DARKAN_FISHING_SPOT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Blamish snail slime": {
            "category": "material",
            "source": f"{HEROES_QUEST_PORT_SARIM_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Harralander potion (unf)": {
            "category": "material",
            "source": f"{HEROES_QUEST_HERBLORE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Blamish oil": {
            "category": "material",
            "source": f"{HEROES_QUEST_HERBLORE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Oily fishing rod": {
            "category": "tool",
            "source": f"{HEROES_QUEST_DARKAN_SOURCE}; {HEROES_QUEST_FISHING_SPOT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Raw lava eel": {
            "category": "fish",
            "source": f"{HEROES_QUEST_FISH_SOURCE}; {HEROES_QUEST_FISHING_SPOT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Lava eel": {
            "category": "food",
            "source": f"{HEROES_QUEST_COOKING_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Bucket of milk": {
            "category": "material",
            "source": f"{DARKAN_GERTRUDES_CAT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Doogle leaves": {
            "category": "material",
            "source": f"{DARKAN_GERTRUDES_CAT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Doogle sardine": {
            "category": "food",
            "source": f"{DARKAN_GERTRUDES_CAT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Three little kittens": {
            "category": "material",
            "source": f"{DARKAN_GERTRUDES_CAT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Pet kitten": {
            "category": "material",
            "source": f"{DARKAN_GERTRUDES_CAT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "White cog": {
            "category": "material",
            "source": f"{DARKAN_CLOCK_TOWER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Black cog": {
            "category": "material",
            "source": f"{DARKAN_CLOCK_TOWER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Blue cog": {
            "category": "material",
            "source": f"{DARKAN_CLOCK_TOWER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Red cog": {
            "category": "material",
            "source": f"{DARKAN_CLOCK_TOWER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Rat poison": {
            "category": "material",
            "source": f"{DARKAN_CLOCK_TOWER_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Ice gloves": {
            "category": "equipment",
            "source": f"{HEROES_QUEST_ICE_QUEEN_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Fire feather": {
            "category": "material",
            "source": f"{HEROES_QUEST_DARKAN_SOURCE}; {HEROES_QUEST_ENTRANA_FIREBIRD_NPC_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Id papers": {
            "category": "material",
            "source": f"{HEROES_QUEST_TROBERT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Black full helm": {
            "category": "equipment",
            "source": f"{HEROES_QUEST_MANSION_DOOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Black platebody": {
            "category": "equipment",
            "source": f"{HEROES_QUEST_MANSION_DOOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Black platelegs": {
            "category": "equipment",
            "source": f"{HEROES_QUEST_MANSION_DOOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Pete's candlestick": {
            "category": "material",
            "source": f"{HEROES_QUEST_BRIMHAVEN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Thieves' armband": {
            "category": "material",
            "source": f"{HEROES_QUEST_KATRINE_SOURCE}; {HEROES_QUEST_STRAVEN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Ring mould": {
            "category": "tool",
            "source": f"{FAMILY_CREST_DARKAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Necklace mould": {
            "category": "tool",
            "source": f"{FAMILY_CREST_DARKAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Antipoison": {
            "category": "material",
            "source": f"{FAMILY_CREST_JOHNATHON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Perfect gold ore": {
            "category": "ore",
            "source": f"{FAMILY_CREST_DARKAN_SOURCE}; {FAMILY_CREST_WITCHHAVEN_PUZZLE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Perfect gold bar": {
            "category": "material",
            "source": f"{FAMILY_CREST_DARKAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Perfect ruby ring": {
            "category": "crafted",
            "source": f"{FAMILY_CREST_DARKAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Perfect ruby necklace": {
            "category": "crafted",
            "source": f"{FAMILY_CREST_DARKAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Caleb crest": {
            "category": "material",
            "source": f"{FAMILY_CREST_CALEB_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Avan crest": {
            "category": "material",
            "source": f"{FAMILY_CREST_AVAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Johnathon crest": {
            "category": "material",
            "source": f"{FAMILY_CREST_CHRONOZON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Family crest": {
            "category": "material",
            "source": f"{FAMILY_CREST_DARKAN_SOURCE}; {FAMILY_CREST_DIMINTHEIS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Family gauntlets": {
            "category": "equipment",
            "source": f"{FAMILY_CREST_DARKAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Cooking gauntlets": {
            "category": "equipment",
            "source": f"{FAMILY_CREST_CALEB_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Goldsmith gauntlets": {
            "category": "equipment",
            "source": f"{FAMILY_CREST_AVAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Chaos gauntlets": {
            "category": "equipment",
            "source": f"{FAMILY_CREST_JOHNATHON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Limpwurt root": {
            "category": "material",
            "source": f"{TEMPLE_OF_IKOV_WINELDA_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Ice arrows": {
            "category": "equipment",
            "equipment_slot": "ammunition",
            "item_id": 78,
            "tradeable": False,
            "source": f"{TEMPLE_OF_IKOV_DUNGEON_SOURCE}; {TEMPLE_OF_IKOV_FIRE_WARRIOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Lever": {
            "category": "material",
            "tradeable": False,
            "source": f"{TEMPLE_OF_IKOV_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Staff of armadyl": {
            "category": "material",
            "item_id": 84,
            "tradeable": False,
            "source": f"{TEMPLE_OF_IKOV_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Shiny key": {
            "category": "material",
            "tradeable": False,
            "source": f"{TEMPLE_OF_IKOV_WIKI_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Pendant of lucien": {
            "category": "equipment",
            "equipment_slot": "neck",
            "item_id": 86,
            "tradeable": False,
            "source": f"{TEMPLE_OF_IKOV_LUCIEN_ARDOUGNE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Armadyl pendant": {
            "category": "equipment",
            "equipment_slot": "neck",
            "item_id": 87,
            "tradeable": False,
            "source": f"{TEMPLE_OF_IKOV_GUARDIAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Boots of lightness": {
            "category": "equipment",
            "equipment_slot": "feet",
            "tradeable": False,
            "source": f"{TEMPLE_OF_IKOV_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Yew comp bow": {
            "category": "equipment",
            "equipment_slot": "weapon",
            "item_id": 10282,
            "source": f"{TEMPLE_OF_IKOV_FIRE_WARRIOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Magic comp bow": {
            "category": "equipment",
            "equipment_slot": "weapon",
            "item_id": 10284,
            "source": f"{TEMPLE_OF_IKOV_FIRE_WARRIOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Dark bow": {
            "category": "equipment",
            "equipment_slot": "weapon",
            "item_id": 11235,
            "source": f"{TEMPLE_OF_IKOV_FIRE_WARRIOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Child's blanket": {
            "category": "material",
            "source": f"{DARKAN_MONKS_FRIEND_OMAD_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Jug of water": {
            "category": "material",
            "source": f"{DARKAN_MONKS_FRIEND_CEDRIC_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Address label": {
            "category": "material",
            "source": f"{DARKAN_TRIBAL_TOTEM_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Totem": {
            "category": "material",
            "source": f"{DARKAN_TRIBAL_TOTEM_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Scorpion cage": {
            "category": "tool",
            "source": f"{DARKAN_SCORPION_CATCHER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Sheep feed": {
            "category": "material",
            "source": f"{DARKAN_SHEEP_HERDER_COUNCILLOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Plague jacket": {
            "category": "equipment",
            "source": f"{DARKAN_SHEEP_HERDER_DOCTOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Plague trousers": {
            "category": "equipment",
            "source": f"{DARKAN_SHEEP_HERDER_DOCTOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Cattleprod": {
            "category": "tool",
            "source": f"{DARKAN_SHEEP_HERDER_FARMER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Red sheep bones": {
            "category": "material",
            "source": f"{DARKAN_SHEEP_HERDER_UTILS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Green sheep bones": {
            "category": "material",
            "source": f"{DARKAN_SHEEP_HERDER_UTILS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Blue sheep bones": {
            "category": "material",
            "source": f"{DARKAN_SHEEP_HERDER_UTILS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Yellow sheep bones": {
            "category": "material",
            "source": f"{DARKAN_SHEEP_HERDER_UTILS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Dwellberries": {
            "category": "material",
            "source": f"{DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Picture of Elena": {
            "category": "material",
            "source": f"{DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Turnip growing for beginners": {
            "category": "material",
            "source": f"{DARKAN_PLAGUE_CITY_JETHICK_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Scruffy note": {
            "category": "material",
            "source": f"{DARKAN_PLAGUE_CITY_BRAVEK_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Hangover cure": {
            "category": "material",
            "source": f"{DARKAN_PLAGUE_CITY_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Warrant": {
            "category": "material",
            "source": f"{DARKAN_PLAGUE_CITY_BRAVEK_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "A small key": {
            "category": "material",
            "source": f"{DARKAN_PLAGUE_CITY_UTILS_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Chocolate dust": {
            "category": "material",
            "source": f"{DARKAN_PLAGUE_CITY_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Snape grass": {
            "category": "material",
            "source": f"{DARKAN_PLAGUE_CITY_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Bucket": {
            "category": "material",
            "source": f"{DARKAN_PLAGUE_CITY_UTILS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Pestle and mortar": {
            "category": "tool",
            "source": f"{DARKAN_PLAGUE_CITY_ALRENA_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Spade": {
            "category": "tool",
            "source": f"{DARKAN_PLAGUE_CITY_UTILS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Bird feed": {
            "category": "material",
            "source": f"{DARKAN_BIOHAZARD_UTILS_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Pigeon cage": {
            "category": "tool",
            "source": f"{DARKAN_BIOHAZARD_UTILS_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Rotten apple": {
            "category": "material",
            "source": f"{DARKAN_BIOHAZARD_UTILS_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Doctors' gown": {
            "category": "equipment",
            "source": f"{DARKAN_BIOHAZARD_UTILS_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Key": {
            "category": "material",
            "source": f"{DARKAN_BIOHAZARD_MOURNER_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Distillator": {
            "category": "material",
            "source": f"{DARKAN_BIOHAZARD_ELENA_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Liquid honey": {
            "category": "material",
            "source": f"{DARKAN_BIOHAZARD_ELENA_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Ethenea": {
            "category": "material",
            "source": f"{DARKAN_BIOHAZARD_ELENA_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Sulphuric broline": {
            "category": "material",
            "source": f"{DARKAN_BIOHAZARD_ELENA_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Plague sample": {
            "category": "material",
            "source": f"{DARKAN_BIOHAZARD_ELENA_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Touch paper": {
            "category": "material",
            "source": f"{DARKAN_BIOHAZARD_CHEMIST_SOURCE}; {DARKAN_BIOHAZARD_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Priest gown": {
            "category": "equipment",
            "source": f"{DARKAN_BIOHAZARD_GUIDOR_WIFE_SOURCE}; {DARKAN_BIOHAZARD_GUIDOR_DOOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Book on Baxtorian": {
            "category": "material",
            "source": f"{DARKAN_WATERFALL_BOOK_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Old key": {
            "category": "material",
            "source": f"{DARKAN_WATERFALL_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Large old key": {
            "category": "material",
            "source": f"{DARKAN_WATERFALL_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Glarial's pebble": {
            "category": "material",
            "source": f"{DARKAN_WATERFALL_GOLRIE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Glarial's amulet": {
            "category": "equipment",
            "source": f"{DARKAN_WATERFALL_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Glarial's urn": {
            "category": "material",
            "source": f"{DARKAN_WATERFALL_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Railing": {
            "category": "material",
            "source": f"{DARKAN_DWARF_CANNON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Dwarf remains": {
            "category": "material",
            "source": f"{DARKAN_DWARF_CANNON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Toolkit": {
            "category": "tool",
            "source": f"{DARKAN_DWARF_CANNON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Nulodion's notes": {
            "category": "material",
            "source": f"{DARKAN_DWARF_CANNON_NULODION_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Ammo mould": {
            "category": "tool",
            "source": f"{DARKAN_DWARF_CANNON_NULODION_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Shield of Arrav book": {
            "category": "material",
            "source": f"{DARKAN_SHIELD_OF_ARRAV_BOOK_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Intel report": {
            "category": "material",
            "source": (
                f"{DARKAN_SHIELD_OF_ARRAV_STRAVEN_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_JONNY_DROPS_SOURCE}; "
                f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
        },
        "Weapon store key": {
            "category": "tool",
            "source": f"{DARKAN_SHIELD_OF_ARRAV_STRAVEN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Phoenix crossbow": {
            "category": "equipment",
            "source": f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Broken shield (Phoenix half)": {
            "category": "material",
            "source": f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Broken shield (Black Arm half)": {
            "category": "material",
            "source": f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Half certificate (Phoenix)": {
            "category": "material",
            "source": f"{DARKAN_SHIELD_OF_ARRAV_CURATOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Half certificate (Black Arm)": {
            "category": "material",
            "source": f"{DARKAN_SHIELD_OF_ARRAV_CURATOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Certificate": {
            "category": "material",
            "source": f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Dramen staff": {"category": "material", "source": LOST_CITY_SOURCE_PATH},
        "Silverlight": {
            "category": "equipment",
            "source": f"{DARKAN_DEMON_SLAYER_SIR_PRYSIN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Silverlight key": {
            "category": "material",
            "source": f"{DARKAN_DEMON_SLAYER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Orange goblin mail": {
            "category": "material",
            "source": f"{DARKAN_GOBLIN_DIPLOMACY_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Blue goblin mail": {
            "category": "material",
            "source": f"{DARKAN_GOBLIN_DIPLOMACY_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Goblin mail": {
            "category": "material",
            "source": f"{DARKAN_GOBLIN_DIPLOMACY_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Fish food": {
            "category": "material",
            "source": f"{DARKAN_ERNEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Poison": {
            "category": "material",
            "source": f"{DARKAN_ERNEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Poisoned fish food": {
            "category": "material",
            "source": f"{DARKAN_ERNEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Pressure gauge": {
            "category": "material",
            "source": f"{DARKAN_ERNEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Grimy key": {
            "category": "material",
            "source": f"{DARKAN_ERNEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Rubber tube": {
            "category": "material",
            "source": f"{DARKAN_ERNEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Oil can": {
            "category": "material",
            "source": f"{DARKAN_ERNEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Maze key": {
            "category": "material",
            "source": f"{DARKAN_DRAGON_SLAYER_GUILDMASTER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Anti-dragon shield": {
            "category": "equipment",
            "source": f"{DARKAN_LUMBRIDGE_DUKE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Map part": {
            "category": "material",
            "source": f"{DARKAN_DRAGON_SLAYER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Crandor map": {
            "category": "material",
            "source": f"{DARKAN_DRAGON_SLAYER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Wizard's mind bomb": {
            "category": "material",
            "source": f"{DARKAN_DRAGON_SLAYER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Silk": {
            "category": "material",
            "source": f"{DARKAN_DRAGON_SLAYER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Crayfish cage": {
            "category": "tool",
            "source": f"{DARKAN_DRAGON_SLAYER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Lobster pot": {
            "category": "tool",
            "source": f"{DARKAN_DRAGON_SLAYER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Plank": {
            "category": "material",
            "source": f"{DARKAN_DRAGON_SLAYER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Hammer": {
            "category": "tool",
            "source": f"{DARKAN_DRAGON_SLAYER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Elvarg's head": {
            "category": "material",
            "source": f"{DARKAN_DRAGON_SLAYER_ELVARG_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Khazard helmet": {
            "category": "equipment",
            "source": f"{DARKAN_FIGHT_ARENA_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Khazard armour": {
            "category": "equipment",
            "source": f"{DARKAN_FIGHT_ARENA_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Khali brew": {
            "category": "material",
            "source": f"{DARKAN_FIGHT_ARENA_ANGOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Khazard cell keys": {
            "category": "tool",
            "source": f"{DARKAN_FIGHT_ARENA_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Door key": {
            "category": "tool",
            "source": f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Magnet": {
            "category": "tool",
            "source": f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Backroom key": {
            "category": "tool",
            "source": f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Ball": {
            "category": "material",
            "source": f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Insect repellent": {
            "category": "tool",
            "source": (
                f"{MERLINS_CRYSTAL_BEEKEEPER_SOURCE}; {MERLINS_CRYSTAL_2011SCAPE_CATHERBY_SPAWN_SOURCE}; "
                f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
        },
        "Bucket of wax": {
            "category": "material",
            "source": f"{MERLINS_CRYSTAL_BEEHIVE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Black candle": {
            "category": "material",
            "source": f"{MERLINS_CRYSTAL_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Lit black candle": {
            "category": "material",
            "source": f"{MERLINS_CRYSTAL_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Excalibur": {
            "category": "equipment",
            "source": f"{MERLINS_CRYSTAL_LADY_SOURCE}; {MERLINS_CRYSTAL_BEGGAR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Holy table napkin": {
            "category": "material",
            "tradeable": False,
            "source": f"{HOLY_GRAIL_GALAHAD_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Magic whistle": {
            "category": "tool",
            "tradeable": False,
            "source": f"{HOLY_GRAIL_DARKAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Grail bell": {
            "category": "tool",
            "tradeable": False,
            "source": f"{HOLY_GRAIL_DARKAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Magic gold feather": {
            "category": "tool",
            "tradeable": False,
            "source": f"{HOLY_GRAIL_KING_ARTHUR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Holy grail": {
            "category": "material",
            "tradeable": False,
            "source": f"{HOLY_GRAIL_DARKAN_SOURCE}; {HOLY_GRAIL_KING_ARTHUR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Orb of protection": {
            "category": "material",
            "tradeable": False,
            "source": f"{TREE_GNOME_DARKAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Orbs of protection": {
            "category": "material",
            "tradeable": False,
            "source": f"{TREE_GNOME_DARKAN_SOURCE}; {TREE_GNOME_BOLREN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Gnome amulet": {
            "category": "equipment",
            "equipment_slot": "neck",
            "item_id": 589,
            "tradeable": False,
            "source": f"{TREE_GNOME_DARKAN_SOURCE}; {TREE_GNOME_BOLREN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Bat bones": {
            "category": "material",
            "source": f"{MERLINS_CRYSTAL_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Rune spear (kp)": {"category": "equipment", "source": TAI_BWO_WANNAI_TRIO_SOURCE},
        "Ivandis flail": {"category": "equipment", "source": LEGACY_OF_SEERGAZE_SOURCE},
        "Tome of Experience, 2nd Ed.": {"category": "material", "source": LEGACY_OF_SEERGAZE_SOURCE},
    })
    generated_items.pop("Queen Black Dragon", None)
    generated_items.pop("Penguin Hide and Seek", None)
    return generated_items


def claims_as_dict() -> Dict[str, Dict[str, object]]:
    claims = {
        claim.id: {
            "id": claim.id,
            "display_name": claim.display_name,
            "claim_type": claim.claim_type,
            "item_name": claim.item_name,
            "quantity": claim.quantity,
            "items": claim.items,
            "source": claim.source,
            "required_quest": claim.required_quest,
            "required_runecrafting_level": claim.required_runecrafting_level,
            "xp_amount": claim.xp_amount,
            "skill_options": claim.skill_options,
            "minimum_level": claim.minimum_level,
        }
        for claim in CLAIMS
    }
    from .achievement_diary_data import diary_lamp_claims_as_dict

    claims.update(diary_lamp_claims_as_dict())
    return claims
