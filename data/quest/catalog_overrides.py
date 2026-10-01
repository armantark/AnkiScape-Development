from __future__ import annotations

from .dependencies import *
from .contract import *
from .ids import *
from .sources import *
from .choices import *
from .definitions import *
from .stage_overrides import *

QUEST_REQUIRED_QUEST_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestPrerequisite, ...]] = {
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
}


# Clears generated acceptance gates; the source-backed skills live on quest stages.
QUEST_REQUIRED_SKILL_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestSkillRequirement, ...]] = {
    "the_lost_tribe": (),
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
    'QUEST_REQUIRED_QUEST_REPLACEMENTS_BY_ID', 'QUEST_REQUIRED_SKILL_REPLACEMENTS_BY_ID', 'QUEST_STAGE_COUNT_REPLACEMENTS_BY_ID', 'QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID', 'QUEST_COMBAT_TEXT_REPLACEMENTS_BY_ID',
    'QUEST_ITEM_REWARD_ADDITIONS_BY_ID', 'QUEST_ITEM_REWARD_REPLACEMENTS_BY_ID', 'QUEST_UNLOCK_REPLACEMENTS_BY_ID', 'QUEST_XP_REWARD_REPLACEMENTS_BY_ID', 'QUEST_LAMP_REWARD_REPLACEMENTS_BY_ID',
)
