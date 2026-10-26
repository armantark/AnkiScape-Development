from __future__ import annotations

from . import watchtower_opening as _watchtower_opening
from .toktz_opening import PENDING_LINES as _TOKTZ_PENDING_LINES
from .dependencies import *
from .contract import *
from .ids import *
from .sources import *
from .choices import *
from .definitions import *
from .stage_overrides import *
from .stage_overrides.free.the_blood_pact import THE_BLOOD_PACT_STAGES
from .cold_war import COLD_WAR_JOURNAL_STAGES, COLD_WAR_UNLOCKS
from .stage_overrides.members.later.horror_from_the_deep import HORROR_FROM_THE_DEEP_JOURNAL_STAGES
from .garden_of_tranquillity import GARDEN_OF_TRANQUILLITY_JOURNAL_STAGES as _GARDEN_OF_TRANQUILLITY_JOURNAL_STAGES

QUEST_REQUIRED_QUEST_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestPrerequisite, ...]] = {
    # Template:Questreq oldid=6552449.
    "desert_treasure": (
        QuestPrerequisite("the_dig_site", "The Dig Site"),
        QuestPrerequisite("the_tourist_trap", "The Tourist Trap"),
        QuestPrerequisite("temple_of_ikov", "Temple of Ikov"),
        QuestPrerequisite("priest_in_peril", "Priest in Peril"),
        QuestPrerequisite("troll_stronghold", "Troll Stronghold"),
        QuestPrerequisite("death_plateau", "Death Plateau"),
        QuestPrerequisite("waterfall_quest", "Waterfall Quest"),
    ),
    # Template:Questreq oldid=6552449; cache struct 593 slots 13 and 99.
    "one_small_favour": (
        QuestPrerequisite("shilo_village", "Shilo Village"),
        QuestPrerequisite("jungle_potion", "Jungle Potion"),
        QuestPrerequisite("rune_mysteries", "Rune Mysteries"),
    ),
    # Seven cache links and Defender of Varrock oldid=6542570.
    "defender_of_varrock": (
        QuestPrerequisite("shield_of_arrav", "Shield of Arrav"),
        QuestPrerequisite("the_knights_sword", "The Knight's Sword"),
        QuestPrerequisite("family_crest", "Family Crest"),
        QuestPrerequisite("what_lies_below", "What Lies Below"),
        QuestPrerequisite("demon_slayer", "Demon Slayer"),
        QuestPrerequisite("temple_of_ikov", "Temple of Ikov"),
        QuestPrerequisite("garden_of_tranquillity", "Garden of Tranquillity"),
    ),
    # Template:Questreq oldids=6552449 and 5981134.
    "recruitment_drive": (
        QuestPrerequisite("black_knights_fortress", "Black Knights' Fortress"),
        QuestPrerequisite("druidic_ritual", "Druidic Ritual"),
    ),
    # Template:Questreq oldid=6552449 supplies the guide's transcluded prerequisite.
    AS_A_FIRST_RESORT_ID: (QuestPrerequisite("zogre_flesh_eaters", "Zogre Flesh Eaters"),),
    # Template:Questreq oldid=6552449.
    "creature_of_fenkenstrain": (
        QuestPrerequisite(PRIEST_IN_PERIL_ID, "Priest in Peril"),
        QuestPrerequisite(THE_RESTLESS_GHOST_ID, "The Restless Ghost"),
    ),
    # Template:Questreq oldid=5981134; corroborated in the Ghosts Ahoy source harvest.
    "ghosts_ahoy": (
        QuestPrerequisite(THE_RESTLESS_GHOST_ID, "The Restless Ghost"),
        QuestPrerequisite(PRIEST_IN_PERIL_ID, "Priest in Peril"),
    ),
    "horror_from_the_deep": (QuestPrerequisite(BAR_CRAWL_ID, "Alfred Grimhand's Barcrawl"),),
    SCORPION_CATCHER_ID: (QuestPrerequisite(BAR_CRAWL_ID, "Alfred Grimhand's Barcrawl"),),
    "the_lost_tribe": (
        QuestPrerequisite(GOBLIN_DIPLOMACY_ID, "Goblin Diplomacy"),
        QuestPrerequisite(RUNE_MYSTERIES_ID, "Rune Mysteries"),
    ),
    # Do No Evil oldid=6587790 expands Template:Questreq oldid=6552449,
    # whose Freeing King Awowogei branch explicitly includes Monkey Madness.
    "do_no_evil": (
        QuestPrerequisite("garden_of_tranquillity", "Garden of Tranquillity"),
        QuestPrerequisite("creature_of_fenkenstrain", "Creature of Fenkenstrain"),
        QuestPrerequisite("monkey_madness", "Monkey Madness"),
    ),
    # Template:Questreq oldid 6552449; Sal's Realm capture 20121018050049.
    "legends_quest": (
        QuestPrerequisite("family_crest", "Family Crest"),
        QuestPrerequisite("heroes_quest", "Heroes' Quest"),
        QuestPrerequisite("shilo_village", "Shilo Village"),
        QuestPrerequisite("underground_pass", "Underground Pass"),
        QuestPrerequisite("waterfall_quest", "Waterfall Quest"),
    ),
}


# Replace generated start gates with the source-backed required levels.
QUEST_REQUIRED_SKILL_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestSkillRequirement, ...]] = {
    "watchtower": _watchtower_opening.WATCHTOWER_SKILLS,
    # Desert Treasure oldids=5981512 and 6563639 mark Mining 50 as optional.
    "desert_treasure": (
        QuestSkillRequirement("agility", "Agility", 15),
        QuestSkillRequirement("firemaking", "Firemaking", 50),
        QuestSkillRequirement("magic", "Magic", 50),
        QuestSkillRequirement("slayer", "Slayer", 10),
        QuestSkillRequirement("thieving", "Thieving", 53),
    ),
    "horror_from_the_deep": (QuestSkillRequirement("agility", "Agility", 35),),
    "monkey_madness": (),
    "enakhras_lament": (
        QuestSkillRequirement("crafting", "Crafting", 50),
        QuestSkillRequirement("firemaking", "Firemaking", 45),
        QuestSkillRequirement("magic", "Magic", 39),
        QuestSkillRequirement("prayer", "Prayer", 43),
    ),
    "eadgars_ruse": (
        QuestSkillRequirement("agility", "Agility", 15),
        QuestSkillRequirement("herblore", "Herblore", 31),
    ),
    "nature_spirit": (),
    "the_lost_tribe": (),
    # Legends' Quest oldid 6529921 lines 28–40; Sal's capture 20121018050049.
    "legends_quest": (
        QuestSkillRequirement("agility", "Agility", 50),
        QuestSkillRequirement("crafting", "Crafting", 50),
        QuestSkillRequirement("herblore", "Herblore", 45),
        QuestSkillRequirement("magic", "Magic", 56),
        QuestSkillRequirement("mining", "Mining", 52),
        QuestSkillRequirement("prayer", "Prayer", 42),
        QuestSkillRequirement("smithing", "Smithing", 50),
        QuestSkillRequirement("strength", "Strength", 50),
        QuestSkillRequirement("thieving", "Thieving", 50),
        QuestSkillRequirement("woodcutting", "Woodcutting", 50),
    ),
}


QUEST_REQUIREMENT_TEXT_REPLACEMENTS_BY_ID: Dict[str, Tuple[str, ...]] = {
    "watchtower": _watchtower_opening.WATCHTOWER_REQUIREMENTS,
    "desert_treasure": (
        "The Dig Site", "The Tourist Trap", "Temple of Ikov", "Priest in Peril",
        "Troll Stronghold", "Death Plateau", "Waterfall Quest", "Agility 15",
        "Firemaking 50", "Magic 50", "Slayer 10", "Thieving 53",
    ),
    "one_small_favour": (
        "Shilo Village", "Jungle Potion", "Rune Mysteries", "Agility 36",
        "Crafting 25", "Herblore 18", "Smithing 30",
    ),
    "defender_of_varrock": (
        "Shield of Arrav", "The Knight's Sword", "Family Crest", "What Lies Below",
        "Demon Slayer", "Temple of Ikov", "Garden of Tranquillity", "Agility 51",
        "Hunter 51", "Mining 59", "Smithing 54",
        # Defender6542570 line 39: the Shield story must be claimed at the Museum.
        "Claim Varrock Museum Kudos for completing Shield of Arrav",
    ),
    "recruitment_drive": ("Black Knights' Fortress", "Druidic Ritual"),
    "horror_from_the_deep": ("Alfred Grimhand's Barcrawl", "Agility 35"),
    "monkey_madness": ("The Grand Tree", "Tree Gnome Village"),
    "enakhras_lament": ("Crafting 50", "Firemaking 45", "Magic 39", "Prayer 43"),
    "eadgars_ruse": (
        "Druidic Ritual", "Troll Stronghold", "Death Plateau", "Agility 15", "Herblore 31",
    ),
    "nature_spirit": ("Priest in Peril", "The Restless Ghost"),
    # Same period sources: Prayer 42 required; Combat 75 is advisory.
    "legends_quest": (
        "108 quest points", "Family Crest", "Heroes' Quest", "Shilo Village",
        "Underground Pass", "Waterfall Quest", "Agility 50",
        "Crafting 50", "Herblore 45", "Magic 56", "Mining 52", "Prayer 42",
        "Smithing 50", "Strength 50", "Thieving 50", "Woodcutting 50",
    ),
}


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


def _tower_of_life_journal_stages() -> Tuple[QuestStage, ...]:
    # Retained packet: 1300-tower-of-life-opening-journal-answers,
    # answer-source-mapping.json and source-index.json (qualified guide text).
    # W1: Tower of Life oldid 6588693, 2012-11-19T21:10:36Z, lines 48-50, 55-58.
    # https://runescape.wiki/w/index.php?title=Tower_of_Life&oldid=6588693
    # sources/tower-of-life-6588693.txt
    # SHA-256: 89a4e18f3c4f0babe03f00bab18d0606f8e9a2fadc6b14f6cd0bc3f8aed373c0
    # W2: Quick guide oldid 6190562, 2012-09-03T20:13:09Z; shares W1 wiki lineage.
    # https://runescape.wiki/w/index.php?title=Tower_of_Life%2FQuick_guide&oldid=6190562
    # sources/tower-of-life-quick-guide-6190562.txt
    # SHA-256: bb48162bc81134e5470a0707cb1674c45a4e1989b0cf1fab14efac4e5552b4d4
    # A1: independent RuneHQ guide, actual capture 20120921110403,
    # 2012-09-21T11:04:03Z; publication date and author-level ancestry unstated.
    # https://web.archive.org/web/20120921110403id_/http://www.runehq.com/quest/tower-of-life
    # sources/runehq-quest-20120921110403.html
    # SHA-256: 2bbb8e9e045aded46b1b980109a286b3e918049116f53d5fc827a735329e3d70
    # D1: canonical Darkan TowerOfLife.kt, revision
    # 517bdeaaf16dbe3cbfe80ee74a91f7fbe944aaed; last file change
    # 4a6595839e613b88b0e9dd95e708124490072fe4. Modern reconstruction corroborated
    # by the period guides, not an original server transcript.
    # sources/darkan-TowerOfLife.kt.txt
    # SHA-256: 61a8719a58d49ba041e69313e07f560f78b71050d26cb2abbfff127fcfc94628
    # Bonafido oldid 6222098 omits answers. Selected cache rows lack dialogue;
    # raw caches/scripts remain unchecked. The game-main667 negative is bounded
    # to the inspected content tree. These are not original-game journal words.
    insertions = {
        1: (
            "He will ask three questions. The answer are as follows:",
            (
                # W1:48; W2:27; A1:280-281; D1:442-443. Expand W1's 3 to 3 nails.
                "How many nails does it take to make a rocking chair? — 3 nails",
                # W1:49; W2:28; A1:282-283; D1:444-445.
                "What takes 3 planks, 3 cloth and 3 nails to make, and help remove light "
                "from a room? — Torn curtains",
                # W1:50; W2:29; A1:284-285; D1:446-447.
                "I like fish and I want to put some in my garden, but I need a special "
                "water feature. What materials would I require? — 10 clay pieces",
            ),
        ),
        2: (
            "He will give a test of which the answers are as follows:",
            (
                # W1:55; W2:46; A1:291-292; D1:460-461.
                "You've plenty of work to do, but you need a drink fast - what do you go for? — Tea",
                # W1:56; W2:48; A1:293-294; D1:462-463.
                "Now, let's hear you whistle! — Whistle for attention",
                # W1:57; W2:50; A1:295-296; D1:464-465. Correct only trowsers.
                "What's a good sign that you need to repair your trousers? — Your legs are getting a bit cold",
                # W1:58; W2:52; A1:297-298; D1:466-467.
                "What do you do if you cut your finger? — Carry on, it'll fix itself.",
            ),
        ),
    }
    raw = next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == "tower_of_life")
    stages = []
    for stage in raw["journal_stages"]:
        journal = list(stage["journal"])
        if stage["stage"] in insertions:
            prompt, answers = insertions[stage["stage"]]
            position = journal.index(prompt) + 1
            journal[position:position] = answers
        stages.append(QuestStage(stage["stage"], tuple(journal)))
    return tuple(stages)


QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStage, ...]] = {
    "watchtower": _watchtower_opening.WATCHTOWER_JOURNAL_STAGES,
    "toktz_ket_dill": tuple(
        QuestStage(row["stage"], (_TOKTZ_PENDING_LINES[0],) if row["stage"] == 1 else tuple(row["journal"]))
        for quest in PRE_EOC_QUEST_CATALOG if quest["id"] == "toktz_ket_dill"
        for row in quest["journal_stages"]
    ),
    # Dream Mentor oldid 6550965, 2012-11-13T04:35:58Z:
    # https://runescape.wiki/w/index.php?title=Dream_Mentor&oldid=6550965
    # Retained: tools/generation/quest_sources.json.gz, wiki.wikitext_dream_mentor_old.
    # Extracted literal-body SHA-256:
    # 49cbd69d53e20688ea8c743a975a72a352da41b4b83971724d86e5ff485da78b
    # Saved original and retained journal-source-map.json evidence directory:
    # /Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1480-dream-mentor-missing-opening-journal-phr/
    # Original: sources/dream-mentor-6550965.txt; mapping: journal-source-map.json.
    # Original line 72:
    # *After four pieces, his '''Health''' status starts to gain and he opens his eyes. Speak with him.
    # Original line 76:
    # *After you raise his '''Spirit''' status up, his appetite returns, so feed him four more pieces of food.
    # One-based opening paragraph -> source line:
    # 1→57, 2→59, 3→61, 4→63, 5→65, 6→70, 7→72, 8→74, 9→76, 10→78, 11→80.
    # Line 72 is a subset paraphrase; line 76 loses only marker/emphasis.
    # Sal's Realm capture 20120110170945, 2012-01-10T17:09:45Z, HTML 209–211:
    # https://web.archive.org/web/20120110170945id_/http://runescape.salmoneus.net:80/quests/dream-mentor.html
    # Saved: sources/sals-20120110170945.html in the evidence directory; SHA-256:
    # f241ad7c0da1e4b5375dd450c374857f433997f924196f5b1cf09b3c3d3c0fc8
    # Corroborates eyes/talking after four, another four after encouragement,
    # then six before the bank request; it describes Health gain per food.
    # Dissent: RuneHQ capture 20120220020240, 2012-02-20T02:02:40Z, HTML 420:
    # https://web.archive.org/web/20120220020240id_/http://www.runehq.com:80/quest/dream-mentor
    # Saved: sources/runehq-20120220020240.html; SHA-256:
    # 0cd096907823943ac3218ccdb7b23721a77d5c87fe3f17e6353a38f57bdf6fc0
    # Says feed until 40% Health before talking; no separate second-four phase.
    # Adopt the explicit dated wiki instruction corroborated by Sal's, without
    # claiming consensus, numerical Health/Spirit rules or precise standing timing.
    # Keep standing in its existing relative position. Fourteen (4+4+6) before
    # the chest is not a whole-quest total; preserve twenty-food preparation
    # and later armour approval/remaining feeding. Official overview/cache
    # definitions do not state these instructions. Darkan's later restoration
    # is reconstruction, not original server code or contemporary corroboration.
    # Retained old quick-guide has no revision/body; current quick-guide oldid
    # 36629635 (2025-01-11T19:33:40Z) supplies no period authority.
    "dream_mentor": tuple(
        QuestStage(
            stage=journal_row["stage"],
            journal=(
                (
                    *journal_row["journal"][:6],
                    "After four pieces of food, he opens his eyes. Speak with him.",
                    journal_row["journal"][6],
                    "After you raise his Spirit status up, his appetite returns, so feed him four more pieces of food.",
                    *journal_row["journal"][7:],
                )
                if journal_row["stage"] == 1
                else tuple(journal_row["journal"])
            ),
        )
        for quest_row in PRE_EOC_QUEST_CATALOG
        if quest_row["id"] == "dream_mentor"
        for journal_row in quest_row["journal_stages"]
    ),
    # Primary: https://runescape.wiki/w/index.php?title=Desert_Treasure&oldid=6563639
    # Revision 2012-11-16T08:24:12Z; literal-body SHA-256:
    # 927f963a829d508fe8b869f4cadf8a27061ea54fc1754ada6608f7de507cfeca
    # Sal's: https://web.archive.org/web/20120920041545id_/http://runescape.salmoneus.net/quests/desert-treasure.html
    # Capture 2012-09-20T04:15:45Z; literal-body SHA-256:
    # 7c7f7de84bee5960bdca721fd8f5a7abc73217d61da3701630b0cbfa3d87fa8f
    # RuneHQ: https://web.archive.org/web/20121103141524id_/http://www.runehq.com:80/quest/desert-treasure
    # Capture 2012-11-03T14:15:24Z; literal-body SHA-256:
    # b14560bbc488200108ad2eaf8078035b38a0751210ab3677c0c4244f21d1b256
    # Sal's L189 corroborates every quantity; RuneHQ L286 corroborates the
    # existing noting qualification. Darkan omits noted bones/ashes. Sal's
    # noting instructions conflict internally (L228 excludes charcoal; L232
    # includes it). The adopted wiki paragraph states no blood-rune noting rule.
    "desert_treasure": tuple(
        QuestStage(
            stage=journal_row["stage"],
            journal=(
                tuple(journal_row["journal"][:6])
                + (
                    "6 Steel bars",  # oldid 6563639 L98: *6 [[Steel bars]]
                    "12 Magic logs",  # L99: *12 [[Magic logs]]
                    "6 Molten glass",  # L100: *6 [[Molten glass]]
                    "1 Charcoal",  # L101: *1 [[Charcoal]]
                    "1 Blood rune",  # L102: *1 [[Blood rune]]
                    "1 Ashes",  # L103: *1 [[Ashes]]
                    "1 Bones",  # L104: *1 [[Bones]]
                )
                + tuple(journal_row["journal"][6:])
                if journal_row["stage"] == 1
                else tuple(journal_row["journal"])
            ),
        )
        for quest_row in PRE_EOC_QUEST_CATALOG
        if quest_row["id"] == "desert_treasure"
        for journal_row in quest_row["journal_stages"]
    ),
    # Walkthrough oldid 6387219 lines 58–65; Cyreg oldid 6222605 line 15;
    # memory-bank/design-thread-queue.md:2948. Post-completion fare timing is
    # owner-selected and lacks period consensus.
    "in_search_of_the_myreque": tuple(
        QuestStage(
            stage=journal_row["stage"],
            journal=tuple(
                {
                    "Respond to Cyreg with the following:": "Persuade Cyreg with four responses in order; the last two continue in the next journal stage:",
                    "Give him three Planks and then ten Coins.": "After all four responses, give Cyreg three ordinary planks and keep three more for the bridge. He will give you directions. To board, carry a blessed silver sickle and a Druid pouch with at least five current charges. The ten-coin fare applies after quest completion.",
                }.get(line, line)
                for line in journal_row["journal"]
            ),
        )
        for quest_row in PRE_EOC_QUEST_CATALOG
        if quest_row["id"] == "in_search_of_the_myreque"
        for journal_row in quest_row["journal_stages"]
    ),
    "cold_war": COLD_WAR_JOURNAL_STAGES,
    "horror_from_the_deep": HORROR_FROM_THE_DEEP_JOURNAL_STAGES,
    "garden_of_tranquillity": _GARDEN_OF_TRANQUILLITY_JOURNAL_STAGES,
    "the_blood_pact": THE_BLOOD_PACT_STAGES,
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
    "tower_of_life": _tower_of_life_journal_stages(),
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


QUEST_ITEM_REWARD_REPLACEMENTS_BY_ID: Dict[str, Tuple[Tuple[str, int], ...]] = {"zogre_flesh_eaters": zogre_flesh_eaters_data.ZOGRE_FLESH_EATERS_ITEM_REWARDS,
    TREE_GNOME_VILLAGE_ID: (("Gnome amulet", 1),),
    PLAGUE_CITY_ID: (("A magic scroll", 1),),
    BIOHAZARD_ID: (),
    DWARF_CANNON_ID: (("Ammo mould", 1),),
    CLOCK_TOWER_ID: (("Coins", 500),),
    MONKS_FRIEND_ID: (("Law rune", 8),),
    # Hazeel Cult oldid=6579784 grants its two artifacts from mutually
    # exclusive quest routes; only the 2,005 coins are common completion loot.
    HAZEEL_CULT_ID: (("Coins", 2005),),
    "stolen_hearts": (("Coins", 2500),),
    "diamond_in_the_rough": (),
    "icthlarins_little_helper": (("Catspeak amulet", 1),),
    SMOKING_KILLS_ID: (),
    SHEEP_HERDER_ID: (("Coins", 3100),),
    "cold_war": (),
    "hunt_for_red_raktuber": (),
    FAIRY_TALE_I_ID: (),
    "a_fairy_tale_iii_battle_at_orks_rift": (("Magic watering can", 1),),
    "a_tail_of_two_cats": (("Catspeak amulet (e)", 1), ("Doctors hat", 1)),
    ANOTHER_SLICE_OF_H_A_M_ID: (("Ancient mace", 1), ("Dorgesh-kaan sphere", 1)),
    "back_to_my_roots": (
        ("Jade vine seed", 1),
    ),
    "catapult_construction": (
        ("Adamant halberd", 1),
        ("Coins", 2000),
        ("Sailor's hat", 1),
        ("Teak plank", 30),
    ),
    "carnillean_rising": (
        # The malformed "Construction" row stood for the pinned revision's
        # construction-supplies bundle (Carnillean Rising oldid=6534490).
        ("Coins", 5000),
        ("Oak plank", 100),
        ("Philipe's sweets", 1),
        ("Teak plank", 30),
        ("Mahogany plank", 10),
        ("Treasure chest (Carnillean Rising)", 1),
    ),
    DEADLIEST_CATCH_ID: (("Small cast net", 1),),
    # The pinned revision awards Book o' piracy at completion; Bill Teach
    # gives the 10,000 coins only in a later conversation (oldid=6533785).
    "cabin_fever": (("Book o' piracy", 1),),
    "dealing_with_scabaras": (),
    "do_no_evil": (("Clue scroll (elite)", 1), ("Cramulet", 1)),
    "dream_mentor": (),
    EAGLES_PEAK_ID: (("Box trap", 1), ("Eagle costume", 1)),
    "in_aid_of_the_myreque": (),
    "let_them_eat_pie": (("Expensive spices", 1), ("Meat pie", 5)),
    "meeting_history": (("Enchanted key", 1),),
    "recipe_for_disaster_freeing_skrach_uglogwee": (),
    # The pinned reward is four sapphires; the cavern text is an access unlock,
    # not an inventory item.
    "the_tale_of_the_muspah": (("Sapphire", 4),),
    "missing_my_mummy": (("Coins", 5000),),
    "nomads_requiem": (("Soul Wars cape", 1),),
    "observatory_quest": (("Maple longbow", 1), ("Uncut sapphire", 1)),
    # Bill Teach gives the Magical cage only when spoken to after the quest
    # (Rocking Out oldid=6521879).
    ROCKING_OUT_ID: (),
    "spirit_of_summer": (("Jennica's ring", 1),),
    "the_dig_site": (("Fruit blast", 1), ("Gold bar", 2)),
    "the_golem": (),
    "the_grand_tree": (),
    SONG_FROM_THE_DEPTHS_ID: (
        ("Coral bolts", 50),
        ("Coral crossbow", 1),
        ("Remora's necklace", 1),
    ),
    SOME_LIKE_IT_COLD_ID: (("Rock costume", 1), ("Pop costume", 1)),
}

QUEST_UNLOCK_REPLACEMENTS_BY_ID: Dict[str, Tuple[str, ...]] = {
    "cold_war": COLD_WAR_UNLOCKS,
    BIOHAZARD_ID: (
        "Ability to travel freely through the West Ardougne Gate",
        "Use of the Combat Training Camp north of Ardougne",
    ),
    "a_fairy_tale_iii_battle_at_orks_rift": (
        "Free access to the Zanaris Market",
        "Ability to use the Fairy Rings and get into Zanaris without a Lunar or Dramen staff.",
        "Ability to fetch teeth to get a Tooth creature by speaking to the Tooth Fairy after the quest.",
        "Access to a new battle area in the Ork's Rift, which contains Ivory Bre'egth (cursed), Ivory Gromblod (cursed) and Ivory Shredflesh (cursed). They all have a combat level of 108 and have high gem and blue charm drop rates.",
        "Ability to sell suqah tooth to the Tooth Fairy for 2,000 coins each. You can also sell to her old teeth, monkey dentures, and kebbit teeth, for amounts ranging from 1 to 200 coins.",
        "Access to Mos Le Harmless through K'Chunk's island; code D-I-P.",
        "To have your patches automatically weeded, talk to Martin the Master Gardener after the quest "
        "to unlock the ability to have gardeners keep your farming patches weed free.",
    ),
    "a_tail_of_two_cats": (
        "Talk to Historian Minas in the Varrock Museum to receive 5 Kudos.",
    ),
    "recipe_for_disaster_freeing_skrach_uglogwee": (
        "Able to use the boat trip to travel between Karamja and Feldip Hills.",
        "(Further) access to the Culinaromancer's chest",
        "The ability to hunt Jubblies. (Counts for 1 point when hunting Chompies, though provides more range experience when killed, and Big Bones as a drop when killed, and the Raw jubbly gives more experience when cooked than a Raw chompy).",
    ),
    ANOTHER_SLICE_OF_H_A_M_ID: (
        "Ability to buy Goblin Village teleport orbs",
        "Free access to the Dorgesh-Kaan - Keldagrim Train System",
    ),
    "back_to_my_roots": (
        "Ability to slay the Jade Vine for extra Slayer and Farming experience once every 15 hours.",
        "Vine Farming Patch in East Ardougne",
        "Transportation between Eagles' Peak and Karamja using the Karamjan Jungle eagle.",
        "A new maze Jade vine maze, slightly larger than Draynor Manor, containing 8 new creatures: "
        "Giant ant soldier level 58, Giant ant worker level 40, Tenacious toucan level 70, Giant Wasp level 66, "
        "Frog level 66, Pernicious parrot level 66, Wild jade vine level 167, Karamjan Jungle eagle.",
    ),
    "catapult_construction": ("Increased damage when using the Castle Wars catapults",),
    # Keeps the generated ferret-capture and eagle-transport unlocks; the
    # rabbit line restores the pinned revision's rabbit-flushing, trapping
    # and foot-stringing capability (Eagles' Peak oldid=6579761). The strung
    # rabbit foot itself stays ungranted — it is crafted later, not awarded.
    EAGLES_PEAK_ID: (
        "Ability to capture ferrets using box traps.",
        "Access to the Eagle transport system",
        "Use captured ferrets to flush rabbits from rabbit holes, trap them with a "
        "rabbit trap, and string a dropped rabbit's foot with a ball of wool to wear "
        "as a necklace when cutting trees to increase bird-nest chances.",
    ),
    "deadliest_catch": (
        "Bank deposit box north-west of Bedabin Camp",
        "Bank deposit box south of Elf Camp",
        "Bank deposit box west of Harmony Island",
        "Bank deposit box west of Mort Myre Swamp",
        "Bank deposit box north-east of Pollnivneach",
        "Bank deposit box on the south coast of Ape Atoll",
        "Bank deposit box south of Brimhaven",
        "Piscatoris - South of Falconry",
    ),
    "dealing_with_scabaras": (
        # The pinned revision's tiara line swallows a how-to paragraph; the
        # unlock states the capability (Dealing with Scabaras oldid=6581466,
        # reward list).
        "The ability to craft an Enchanted water tiara - protects you from the Desert heat effect",
        "Simon Templeton accepts noted Pyramid Plunder treasures after his post-quest errand, "
        "but noted gold artefacts still cannot be exchanged.",
    ),
    "do_no_evil": (
        "New magic carpet destinations, connecting the Monkey colony with Shantay Pass and southern Pollnivneach.",
        "Ability to pickpocket monkey knife fighters.",
        "Ability to run chimp ice for further rewards.",
        "Access to a passageway from the desert (rockslide south of the Kalphite Hive entrance) "
        "to a new area with Kalphites. This is unlocked if you left the room from the hole while you were in it.",
        "The ability to upgrade Ava's accumulator to Ava's alerter.",
        "Access to the Monkey colony.",
        # Entering this cavern is gated on level 80 Agility (oldid=6587790);
        # its contents (20,000 Agility xp, Apmeken mask, ankh) are conditional
        # rewards awaiting a claim mechanism.
        "Players with level 80 Agility (boosts may be used) can enter the cavern "
        "in the south wall of the Monkey colony.",
        "The ability to add the camulet and catspeak amulet to the Cramulet.",
    ),
    # The pinned revision lists the Random option on NPC Contact beneath the
    # seven-spell line as a sibling reward (Dream Mentor oldid=6550965).
    "dream_mentor": (
        "Seven new spells added to the Lunar Spellbook",
        "Access to the 'Random' option on NPC Contact",
    ),
    "in_aid_of_the_myreque": (
        "Access to Burgh de Rott",
        "You can now play Temple Trekking activity.",
        "Ability to use a Gadderhammer, which is strong against shades.",
        "Ability to make and use Rod of Ivandis and Guthix balance potion to fight and defeat Vampyre Juveniles and Juvinates.",
        "Talk to Historian Minas to receive 5 Kudos in the Varrock Museum.",
    ),
    "meeting_history": (
        "Speak to Historian Minas at the Varrock Museum to earn 5 Kudos.",
    ),
    "nomads_requiem": (
        "Access to a Bloodwood tree in the Soul Wars waiting area.",
        "Soul Wars is added to the available respawn points.",
        "Decaying Avatar and Nomad become available as bosses in the Dominion Tower.",
    ),
    "observatory_quest": (
        "Talk to Historian Minas at the Varrock Museum to receive 5 Kudos.",
    ),
    ROCKING_OUT_ID: (
        # The pinned revision's line ends in a broken "{{Skill_clickpic}}"
        # template render, not real content (Rocking Out oldid=6521879).
        "Ability to catch Pirate implings with 76 Hunter",
        "Ability to steal from customs lockers",
        "Ability to buy Braindeath 'rum' from The Rusty Anchor Inn",
        "Access to the Rock Island Prison.",
        "Access to a Bank deposit box in Rimmington",
        "Ability to raise Ex-ex-parrot by speaking to Bill Teach and 50 Ships Mufassah (requires 71 Summoning)",
        "Free access to the Brimhaven Agility Arena",
        "Removes need for the Book o' piracy when speaking to pirates on Mos Le'Harmless",
    ),
    "spirit_of_summer": (
        "Access to the alternative Axe Hut, in which axeless level 42 Ghostly warriors can be fought without the need of a lockpick.",
        "Access to the Cursed Magic Tree",
        "Access to a Goth leprechaun in level 26 wilderness, as well as the flower patch he guards.",
        "Access to a new Spirit Realm",
    ),
    "the_dig_site": (
        "Ability to do Varrock Museum Specimen Cleaning to obtain Kudos and a Digsite pendant.",
        "Access through the Varrock Museum back door and gate.",
    ),
    "the_golem": (
        "Magic carpet route opened to the ruins of Uzer.",
        "Ability to collect multiple Phoenix feathers",
    ),
    "cabin_fever": cabin_fever_data.CABIN_FEVER_UNLOCKS,
    "the_grand_tree": (
        "Ability to use the Grand Tree mine under The Grand Tree",
        "Ability to use the Gnome glider transportation system",
        "Ability to use the Agility Shortcut from the Grand Tree to the Barbarian Outpost (with 37 Agility)",
        "Ability to use the Spirit Tree in the stronghold outside the Grand Tree (the Tree Gnome Village quest doesn't allow access to this tree)",
        "Talk to Historian Minas in the Varrock Museum to receive 5 Kudos.",
    ),
}


QUEST_XP_REWARD_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestXpReward, ...]] = {"zogre_flesh_eaters": tuple(QuestXpReward(*row) for row in zogre_flesh_eaters_data.ZOGRE_FLESH_EATERS_XP_REWARDS),
    "royal_trouble": (QuestXpReward("agility", 5000),),
    "grim_tales": (QuestXpReward("agility", 6000),),
    "stolen_hearts": (QuestXpReward("constitution", 250),),
    "diamond_in_the_rough": (
        QuestXpReward("agility", 250),
        QuestXpReward("constitution", 250),
        QuestXpReward("thieving", 250),
    ),
    "missing_my_mummy": (
        QuestXpReward("constitution", 7000),
        QuestXpReward("cooking", 2100),
        QuestXpReward("thieving", 3000),
        QuestXpReward("crafting", 3350),
        QuestXpReward("magic", 5000),
        QuestXpReward("prayer", 6500),
        QuestXpReward("construction", 2100),
    ),
    SONG_FROM_THE_DEPTHS_ID: (QuestXpReward("constitution", 700),),
    SOME_LIKE_IT_COLD_ID: (
        QuestXpReward("construction", 10000),
        QuestXpReward("crafting", 40000),
        QuestXpReward("fishing", 40000),
        QuestXpReward("thieving", 10000),
    ),
    THE_FREMENNIK_ISLES_ID: (
        QuestXpReward("construction", 5000),
        QuestXpReward("crafting", 5000),
        QuestXpReward("woodcutting", 10000),
    ),
}

QUEST_LAMP_REWARD_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestLampReward, ...]] = {
    CARNILLEAN_RISING_ID: (
        QuestLampReward(
            "Carnillean lamp",
            1500,
            (
                "agility", "attack", "constitution", "construction", "cooking",
                "crafting", "defense", "dungeoneering", "farming", "firemaking",
                "fishing", "fletching", "herblore", "hunter", "magic", "mining",
                "prayer", "ranged", "runecrafting", "slayer", "smithing", "strength",
                "summoning", "thieving", "woodcutting",
            ),
            31,
            "https://runescape.wiki/w/Carnillean_lamp?oldid=6153995",
            (
                "Two Carnillean lamps are awarded for completing the Carnillean Rising quest. "
                "They may be claimed from the chest by Ceril inside the Carnillean mansion. "
                "Each lamp gives 1,500 experience in a skill (above level 30) of your choice."
            ),
            quantity=2,
        ),
    ),
    THE_FREMENNIK_ISLES_ID: (
        QuestLampReward(
            "Combat experience choice",
            10000,
            ("attack", "strength", "defense", "constitution"),
            1,
            THE_FREMENNIK_ISLES_SOURCE,
            (
                "After giving him the Ice Troll King head, the player is offered two 10,000 "
                "experience rewards to any two of Attack, Strength, Defence, or Constitution. "
                "The player can select the same skill twice if desired."
            ),
            quantity=2,
        ),
    ),
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

__all__ = (
    'QUEST_REQUIREMENT_TEXT_REPLACEMENTS_BY_ID',
    'QUEST_REQUIRED_QUEST_REPLACEMENTS_BY_ID', 'QUEST_REQUIRED_SKILL_REPLACEMENTS_BY_ID', 'QUEST_STAGE_COUNT_REPLACEMENTS_BY_ID', 'QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID', 'QUEST_COMBAT_TEXT_REPLACEMENTS_BY_ID',
    'QUEST_ITEM_REWARD_ADDITIONS_BY_ID', 'QUEST_ITEM_REWARD_REPLACEMENTS_BY_ID', 'QUEST_UNLOCK_REPLACEMENTS_BY_ID', 'QUEST_XP_REWARD_REPLACEMENTS_BY_ID', 'QUEST_LAMP_REWARD_REPLACEMENTS_BY_ID',
)
