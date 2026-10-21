from __future__ import annotations

from .dependencies import *
from .contract import *
from .ids import *
from .sources import *
from .stage_additions import CAT_FOLLOWER_STATE_NAMES
from .cold_war import COLD_WAR_STAGE_CLEANUPS
from .stage_overrides.members.later.mournings_end_part_i import MOURNINGS_END_PART_I_CLEANUPS
from .stage_overrides.free.the_blood_pact import THE_BLOOD_PACT_CLEANUPS
from .stage_overrides.members.later.as_a_first_resort import AS_A_FIRST_RESORT_STAGE_CLEANUPS
from .stage_overrides.members.later.creature_of_fenkenstrain import CREATURE_OF_FENKENSTRAIN_CLEANUPS
from .stage_overrides.members.later.underground_pass import UNDERGROUND_PASS_CLEANUPS
from .stage_overrides.members.classic.observatory_quest import OBSERVATORY_QUEST_CLEANUPS

QUEST_STAGE_REQUIREMENT_CLEANUPS_BY_ID: Dict[str, Tuple[QuestStageRequirementCleanup, ...]] = {BIG_CHOMPY_BIRD_HUNTING_ID: tuple(QuestStageRequirementCleanup(**row) for row in chompy_hunting_data.BIG_CHOMPY_STAGE_REQUIREMENT_CLEANUPS),
    "zogre_flesh_eaters": tuple(QuestStageRequirementCleanup(**row) for row in zogre_flesh_eaters_data.ZOGRE_FLESH_EATERS_STAGE_REQUIREMENT_CLEANUPS),
    "creature_of_fenkenstrain": CREATURE_OF_FENKENSTRAIN_CLEANUPS,
    "underground_pass": UNDERGROUND_PASS_CLEANUPS,
    "the_blood_pact": THE_BLOOD_PACT_CLEANUPS,
    "observatory_quest": OBSERVATORY_QUEST_CLEANUPS,
    "the_lost_tribe": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_tools=("Tinderbox",),
            remove_required_actions=("Complete The Lost Tribe stage 1 objective",),
            add_required_inventory_options=(
                tuple((item_name, 1) for item_name in LIT_LIGHT_SOURCE_ITEMS),
            ),
            add_required_tools=(("Pickaxe", 1),),
            add_required_skills=(
                QuestSkillRequirement("agility", "Agility", 13),
                QuestSkillRequirement("mining", "Mining", 17),
            ),
            add_auto_actions=(
                "Mine the Lumbridge cellar rubble and squeeze through the resulting hole",
            ),
            source=THE_LOST_TRIBE_WIKI_SOURCE,
        ),
        QuestStageRequirementCleanup(stage=2, remove_required_inventory_options=LIT_LIGHT_SOURCE_ITEMS, remove_required_tools=("Pickaxe",), remove_required_actions=("Complete The Lost Tribe stage 2 objective",),
            add_auto_actions=("Find the stone brooch, show it to Duke Horacio and Sigmund, ask Reldo about it, then recover the Goblin symbol book",), source=THE_LOST_TRIBE_STAGE_ACTION_SOURCE),
        QuestStageRequirementCleanup(stage=3, remove_required_actions=("Complete The Lost Tribe stage 3 objective",), add_auto_actions=("Read the Goblin symbol book and question the two generals in Goblin Village about the Dorgeshuun",), source=THE_LOST_TRIBE_STAGE_ACTION_SOURCE),
        QuestStageRequirementCleanup(stage=4, remove_required_actions=("Complete The Lost Tribe stage 4 objective",), add_auto_actions=("Translate the tunnel symbols, follow the safe route, and perform Goblin Bow before Mistag, then follow him back to Lumbridge",), source=THE_LOST_TRIBE_STAGE_ACTION_SOURCE),
        QuestStageRequirementCleanup(stage=5, add_required_skills=(QuestSkillRequirement("thieving", "Thieving", 13),), remove_required_actions=("Complete The Lost Tribe stage 5 objective",),
            add_auto_actions=("Pickpocket Sigmund's key, search his chest, recover the castle silverware, receive Duke Horacio's peace treaty, follow Kazgar, deliver the treaty to Mistag, and witness its signing",), source=THE_LOST_TRIBE_STAGE_ACTION_SOURCE),
    ),
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
            remove_required_inventory_options=CAT_FOLLOWER_STATE_NAMES,
            remove_required_actions=("Complete Rat Catchers stage 1 objective",),
            add_auto_actions=("Have Hooknosed Jack make rat poison",),
            add_consumed_inventory=(("Vial", 1), ("Clean kwuarm", 1), ("Red spiders' eggs", 1)),
            add_produced_inventory=(("Rat poison", 1),),
        ),
    ),
    "mournings_end_part_ii": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Mourner gear",),
        ),
    ),
    "mournings_end_part_i": MOURNINGS_END_PART_I_CLEANUPS,
    "icthlarins_little_helper": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory_options=CAT_FOLLOWER_STATE_NAMES,
        ),
        QuestStageRequirementCleanup(
            stage=2,
            remove_required_inventory_options=CAT_FOLLOWER_STATE_NAMES,
        ),
    ),
    "a_tail_of_two_cats": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory_options=CAT_FOLLOWER_STATE_NAMES,
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
    "a_fairy_tale_ii_cure_a_queen": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_actions=("Complete A Fairy Tale II - Cure a Queen stage 1 objective",),
            add_auto_actions=("The crops are still failing. I should investigate Fairy Nuff's grotto in Zanaris.",),
            source=FAIRY_TALE_II_STAGE_ACTION_SOURCE,
        ),
        QuestStageRequirementCleanup(
            stage=2,
            remove_required_actions=("Complete A Fairy Tale II - Cure a Queen stage 2 objective",),
            add_auto_actions=(
                "The Godfather gave me permission to use fairy rings. Nuff's message says AIR, DLR, DJQ, AJS in order.",
            ),
            source=FAIRY_TALE_II_STAGE_ACTION_SOURCE,
        ),
        QuestStageRequirementCleanup(
            stage=3,
            remove_required_actions=("Complete A Fairy Tale II - Cure a Queen stage 3 objective",),
            add_auto_actions=(
                "I must pickpocket the Queen's secateurs from the Fairy Godfather without being detected.",
            ),
            source=FAIRY_TALE_II_STAGE_ACTION_SOURCE,
        ),
        QuestStageRequirementCleanup(
            stage=4,
            remove_required_actions=("Complete A Fairy Tale II - Cure a Queen stage 4 objective",),
            add_auto_actions=(
                "Fairy Nuff needs Magic essence: a Star flower from CKP and powdered Gorak claws from DIR.",
            ),
            source=FAIRY_TALE_II_STAGE_ACTION_SOURCE,
        ),
        QuestStageRequirementCleanup(
            stage=5,
            remove_required_actions=("Complete A Fairy Tale II - Cure a Queen stage 5 objective",),
            add_auto_actions=(
                "Back at the hideout, use a dose of the magic essence potion on the queen, who finally regains her senses.",
            ),
            source=FAIRY_TALE_II_STAGE_ACTION_SOURCE,
        ),
    ),
    "lunar_diplomacy": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_actions=("Complete Lunar Diplomacy stage 1 objective",),
            add_auto_actions=(
                "Brundt must issue me a Seal of passage before Lokar can take me to the Lady Zay.",
            ),
            add_produced_inventory=(("Seal of passage", 1),),
            source=LUNAR_DIPLOMACY_STAGE_ACTION_SOURCE,
        ),
        QuestStageRequirementCleanup(
            stage=2,
            remove_required_actions=("Complete Lunar Diplomacy stage 2 objective",),
            add_auto_actions=(
                "The Lady Zay is jinxed. I must follow Captain Bentley and Bird's-Eye Jack's investigation.",
            ),
            source=LUNAR_DIPLOMACY_STAGE_ACTION_SOURCE,
        ),
        QuestStageRequirementCleanup(
            stage=3,
            remove_required_actions=("Complete Lunar Diplomacy stage 3 objective",),
            add_auto_actions=(
                "The five emerald glyphs are visible. Captain Bentley can now sail to Lunar Isle.",
            ),
            source=LUNAR_DIPLOMACY_STAGE_ACTION_SOURCE,
        ),
        QuestStageRequirementCleanup(
            stage=4,
            remove_required_actions=("Complete Lunar Diplomacy stage 4 objective",),
            add_auto_actions=(
                "The Oneiromancer needs a Waking sleep vial, a Lunar staff, and eight ceremonial garments.",
            ),
            source=LUNAR_DIPLOMACY_STAGE_ACTION_SOURCE,
        ),
        QuestStageRequirementCleanup(
            stage=5,
            remove_required_actions=("Complete Lunar Diplomacy stage 5 objective",),
            add_auto_actions=(
                "I have the ritual equipment. I must wear the outfit and staff, soak the kindling, and light the brazier.",
            ),
            source=LUNAR_DIPLOMACY_STAGE_ACTION_SOURCE,
        ),
        QuestStageRequirementCleanup(
            stage=6,
            remove_required_actions=("Complete Lunar Diplomacy stage 6 objective",),
            add_auto_actions=(
                "I must complete all six lessons in the Dream World. Finished lessons survive a failed visit.",
            ),
            source=LUNAR_DIPLOMACY_STAGE_ACTION_SOURCE,
        ),
        QuestStageRequirementCleanup(
            stage=7,
            remove_required_actions=("Complete Lunar Diplomacy stage 7 objective",),
            add_auto_actions=(
                "I defeated Me and read My life. I should return to the Oneiromancer.",
            ),
            source=LUNAR_DIPLOMACY_STAGE_ACTION_SOURCE,
        ),
    ),
    "the_fremennik_trials": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_actions=("Complete The Fremennik Trials stage 1 objective",),
            add_auto_actions=(
                "Brundt requires seven distinct council votes. I may complete the trials in any order.",
            ),
            source=THE_FREMENNIK_TRIALS_STAGE_ACTION_SOURCE,
        ),
        QuestStageRequirementCleanup(
            stage=2,
            remove_required_actions=("Complete The Fremennik Trials stage 2 objective",),
            add_auto_actions=(
                "Offer the beer to the Council workman. He will give you a cherry bomb, something he picked up from his outings, as a gift.",
            ),
            add_consumed_inventory=(("Beer", 1),),
            add_produced_inventory=(("Strange object", 1),),
            source=THE_FREMENNIK_TRIALS_STAGE_ACTION_SOURCE,
        ),
        QuestStageRequirementCleanup(
            stage=3,
            remove_required_inventory=("Raw shark", "Hatchet", "Raw potato", "Cabbage", "Onion"),
            remove_required_actions=("Complete The Fremennik Trials stage 3 objective",),
            add_required_tools=(("Hatchet", 1),),
            add_auto_actions=(
                "The low-alcohol beer keeps you clear-headed and Manni concedes.",
                "You perform on the longhall stage. As you finish, Fossegrimen's quest blessing leaves the lyre.",
            ),
            add_consumed_inventory=(
                ("Strange object", 1),
                ("Raw shark", 1),
                ("Potato", 1),
                ("Cabbage", 1),
                ("Onion", 1),
            ),
            add_produced_inventory=(("Lyre", 1),),
            source=THE_FREMENNIK_TRIALS_STAGE_ACTION_SOURCE,
        ),
        QuestStageRequirementCleanup(
            stage=4,
            remove_required_actions=("Complete The Fremennik Trials stage 4 objective",),
            add_auto_actions=("You escaped my house. My vote remains yours.",),
            source=THE_FREMENNIK_TRIALS_STAGE_ACTION_SOURCE,
        ),
        QuestStageRequirementCleanup(
            stage=5,
            remove_required_actions=("Complete The Fremennik Trials stage 5 objective",),
            add_auto_actions=(
                "You completed the bargain. My vote is yours.",
                "You navigated the maze. My vote is yours.",
            ),
            source=THE_FREMENNIK_TRIALS_STAGE_ACTION_SOURCE,
        ),
        QuestStageRequirementCleanup(
            stage=6,
            remove_required_actions=("Complete The Fremennik Trials stage 6 objective",),
            add_auto_actions=(
                "The Draugen is defeated. You have my vote.",
                "Koschei tested your bravery. My vote is yours.",
            ),
            source=THE_FREMENNIK_TRIALS_STAGE_ACTION_SOURCE,
        ),
        QuestStageRequirementCleanup(
            stage=7,
            remove_required_actions=("Complete The Fremennik Trials stage 7 objective",),
            add_auto_actions=(
                "I am a citizen of Rellekka and have a Fremennik name.",
            ),
            source=THE_FREMENNIK_TRIALS_STAGE_ACTION_SOURCE,
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
    "cabin_fever": tuple(
        QuestStageRequirementCleanup(**row)
        for row in cabin_fever_data.CABIN_FEVER_STAGE_REQUIREMENT_CLEANUPS
    ),
    "cold_war": COLD_WAR_STAGE_CLEANUPS,
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
                "Hatchet",
            ),
            remove_required_inventory_options=("Summer pie", "Agility potion"),
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
        QuestStageRequirementCleanup(stage=3, remove_required_inventory=("Hatchet",)),
        QuestStageRequirementCleanup(
            stage=5,
            remove_required_inventory=("Yak hide armour", "Fremennik round shield"),
            remove_required_actions=("Complete The Fremennik Isles stage 5 objective",),
            add_required_actions=("Cure and stitch yak-hide armour", "Make a Fremennik round shield"),
        ),
    ),
    "kings_ransom": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Animate rock scroll",),
            remove_required_inventory_options=(
                "Granite",
                "Ring of stone",
                "Telekinetic Grab",
                "Lockpick",
            ),
            add_required_inventory_options=(
                (
                    ("Granite (500g)", 1),
                    ("Granite (2kg)", 1),
                    ("Granite (5kg)", 1),
                    ("Ring of stone", 1),
                ),
            ),
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
            add_auto_actions=(
                "Copy at least four distinct Scabarite note identities into the research book.",
            ),
            source=DEALING_WITH_SCABARAS_DARKAN_SOURCE,
        ),
        QuestStageRequirementCleanup(
            stage=3,
            remove_required_actions=("Complete Dealing with Scabaras stage 3 objective",),
            add_auto_actions=(
                "Use the key, allocate four unique power settings, stoke the furnace, "
                "and complete all four rooms in one timed attempt.",
            ),
            source=DEALING_WITH_SCABARAS_DARKAN_SOURCE,
        ),
        QuestStageRequirementCleanup(
            stage=4,
            remove_required_actions=("Complete Dealing with Scabaras stage 4 objective",),
            add_auto_actions=(
                "After pulling all the levers you will be allowed to enter the antechamber.",
            ),
            source=DEALING_WITH_SCABARAS_WIKI_SOURCE,
        ),
        QuestStageRequirementCleanup(
            stage=5,
            remove_required_actions=("Complete Dealing with Scabaras stage 5 objective",),
            add_auto_actions=("Enter the newly opened hallway.",),
            source=DEALING_WITH_SCABARAS_WIKI_SOURCE,
        ),
        QuestStageRequirementCleanup(
            stage=6,
            remove_required_actions=("Complete Dealing with Scabaras stage 6 objective",),
            add_auto_actions=(
                "I must endure two different attack styles and persuade the High Priest that the "
                "Devourer caused the heresy.",
            ),
            source=DEALING_WITH_SCABARAS_DARKAN_SOURCE,
        ),
        QuestStageRequirementCleanup(
            stage=7,
            remove_required_actions=("Complete Dealing with Scabaras stage 7 objective",),
            add_auto_actions=(
                "The High Priest of Scabaras has recovered. I should return to Sophanem.",
            ),
            source=DEALING_WITH_SCABARAS_DARKAN_SOURCE,
        ),
    ),
    "horror_from_the_deep": (
        QuestStageRequirementCleanup(
            stage=6,
            remove_required_inventory=("Sword", "Arrow"),
        ),
    ),
    "ghosts_ahoy": (
        QuestStageRequirementCleanup(stage=1, remove_required_inventory=("Dye",)),
    ),
    "roving_elves": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Good Food", "Antipoison potion"),
        ),
    ),
    "rum_deal": tuple(QuestStageRequirementCleanup(**row) for row in rum_deal_data.RUM_DEAL_STAGE_REQUIREMENT_CLEANUPS),
    "spirits_of_the_elid": (
        QuestStageRequirementCleanup(
            stage=2,
            remove_required_inventory=("Telegrab",),
            remove_required_actions=("Complete Spirits of the Elid stage 2 objective",),
            add_required_actions=("Cast Telegrab for the water channel puzzle",),
        ),
    ),
    "enakhras_lament": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Sandstone", "Runes"),
        ),
        QuestStageRequirementCleanup(
            stage=4,
            remove_required_inventory=("Fire Bolt",),
        ),
        QuestStageRequirementCleanup(
            stage=5,
            remove_required_inventory=("Crumble Undead", "Wind Bolt"),
            remove_required_actions=("Complete Enakhra's Lament stage 5 objective",),
            add_required_actions=("Cast Crumble Undead during the boneguard fight",),
        ),
    ),
    "in_aid_of_the_myreque": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Food",),
        ),
        QuestStageRequirementCleanup(stage=2, remove_required_inventory=("Nails",)),
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
            remove_required_inventory_options=("Shilo Village", "Antipoison", "Prayer Book"),
            remove_required_tools=("Any woodcutting hatchet",),
            remove_required_actions=("Complete Back to my Roots stage 1 objective",),
            add_auto_actions=("Reach the Karamja jungle route",),
        ),
    ),
    "rocking_out": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Pirate clothing", "Brimhaven tablet", "Ectophial"),
            remove_required_inventory_options=("Rimmington", "Rimmington tablet", "Love Story"),
            remove_required_actions=("Complete Rocking Out stage 1 objective",),
            add_auto_actions=("Reach the Rimmington customs office",),
        ),
    ),
    "glorious_memories": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=(
                "Teleport to House",
                "Player-owned house",
                "Rellekka",
                "Rellekka tablet",
                "Ring of wealth",
                "Earth rune",
                "Earth staff",
                "Lava battlestaff",
                "Mindspike (earth)",
                "Mud battlestaff",
            ),
            remove_required_inventory_options=("Staff", "Pole"),
            add_required_inventory_options=(
                (
                    ("Earth rune", 10),
                    ("Staff of earth", 1),
                    ("Lava battlestaff", 1),
                    ("Mindspike (earth)", 1),
                    ("Mud battlestaff", 1),
                ),
            ),
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
            remove_required_actions=("Complete The Eyes of Glouphrie stage 3 objective",),
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
                "Water rune",
                "Water staff",
                "Desert clothing",
                "Weight-reducing clothing",
            ),
            remove_required_inventory_options=(
                "Waterskin",
                "Enchanted water tiara",
                "Explorer's ring",
                "Energy potion",
                "Amulet of glory",
                "Ring of duelling",
            ),
            remove_required_tools=("Tinderbox", "Hatchet"),
            add_auto_actions=(
                "Cast Enchant Level 1 Jewellery for the sapphire preparations",
                "Reach the Muspah cave route through Rellekka and Pollnivneach",
            ),
            remove_required_actions=("Complete The Tale of the Muspah stage 1 objective",),
        ),
        QuestStageRequirementCleanup(
            stage=2,
            remove_required_inventory=("Rellekka",),
            remove_required_tools=("Knife",),
            remove_required_actions=("Complete The Tale of the Muspah stage 2 objective",),
            add_auto_actions=("Reach Rellekka",),
        ),
        QuestStageRequirementCleanup(
            stage=3,
            remove_required_inventory=("Pollnivneach",),
            remove_required_tools=("Spade",),
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
        QuestStageRequirementCleanup(stage=7, remove_required_inventory=("Antipoison",)),
    ),
    "troll_romance": (
        QuestStageRequirementCleanup(stage=1, remove_required_inventory=("Combat gear and good food",)),
    ),
    "do_no_evil": (
        QuestStageRequirementCleanup(stage=2, remove_required_inventory=CAT_FOLLOWER_STATE_NAMES),
        QuestStageRequirementCleanup(
            stage=3,
            remove_required_inventory=("M'amulet mould",),
            remove_required_actions=("Complete Do No Evil stage 3 objective",),
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
                "Mourner gear",
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
        QuestStageRequirementCleanup(stage=3, remove_required_inventory=("Hatchet",)),
    ),
    "regicide": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Bow", "Arrows", "Underground Pass (dungeon)"),
            add_required_inventory=(("Rope", 1),),
        ),
    ),
    "wanted": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Seers' headband", "Rope", "Lumbridge Swamp Caves"),
            remove_required_tools=("Tinderbox",),
        ),
    ),
    "the_hand_in_the_sand": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Brimhaven", "Yanille", "Explorer's Ring 3"),
        ),
    ),
    "the_slug_menace": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=(
                "Earth talisman",
                "Water talisman",
                "Fire talisman",
                "Air talisman",
                "Mind talisman",
                "Elemental talisman",
                "Omni-talisman",
                "Abyss",
                "Great Orb Project",
            ),
            remove_required_inventory_options=("Rune essence", "Pure essence"),
            add_required_inventory_options=(
                (("Rune essence", 5), ("Pure essence", 5)),
                (("Earth talisman", 1), ("Elemental talisman", 1), ("Omni-talisman", 1)),
                (("Water talisman", 1), ("Elemental talisman", 1), ("Omni-talisman", 1)),
                (("Fire talisman", 1), ("Elemental talisman", 1), ("Omni-talisman", 1)),
                (("Air talisman", 1), ("Elemental talisman", 1), ("Omni-talisman", 1)),
                (("Mind talisman", 1), ("Omni-talisman", 1)),
            ),
        ),
    ),
    "gunnars_ground": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=(
                "The lodestone in Edgeville activated",
                "Amulet of glory",
                "Using a skull sceptre",
            ),
        ),
    ),
    "mountain_daughter": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=(
                "Hatchet",
                "White Wolf Mountain",
                "Super energy potion",
                "Enchanted Lyre",
                "Weight-reducing clothing",
                "Games Necklace",
                "Ring of slaying",
            ),
            add_required_tools=(("Hatchet", 1),),
        ),
    ),
    "recipe_for_disaster_freeing_evil_dave": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=CAT_FOLLOWER_STATE_NAMES,
        ),
        QuestStageRequirementCleanup(
            stage=2,
            remove_required_inventory=CAT_FOLLOWER_STATE_NAMES,
        ),
    ),
    "recipe_for_disaster_freeing_sir_amik_varze": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Hatchet",),
            remove_required_inventory_options=("Fairytale III - Battle at Orks Rift",),
        ),
    ),
    "throne_of_miscellania": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Woodcutting", "Hatchet", "Rake", "Ring"),
            remove_required_inventory_options=("Harpoon",),
            remove_required_tools=("Pickaxe", "Hammer"),
        ),
    ),
    "legends_quest": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=(
                "Hatchet",
                "RuneScape Germany",
                "RuneScape France",
                "RuneScape Brazilian",
                "Air rune",
                "Blood rune",
                "Nature rune",
                "Death rune",
                "Fire rune",
            ),
            add_required_inventory_options=(
                (("Rune hatchet", 1), ("Dragon hatchet", 1)),
            ),
        ),
    ),
    "royal_trouble": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Energy potion", "Giant Sea Snake", "Rope"),
            remove_required_inventory_options=("Coal", "Agility potion", "Agility"),
        ),
    ),
    "summers_end": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=(
                "Summoning pouch",
                "Blue charm",
                "Giant chinchompa",
                "Albino Rat",
                "Hatchet",
            ),
            add_required_inventory_options=(
                tuple(
                    (pouch.pouch_name, 1)
                    for pouch in SUMMONING_POUCHES
                    if pouch.charm == "Blue charm"
                ),
            ),
            add_required_tools=(("Hatchet", 1),),
        ),
    ),
    "smoking_kills": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory_options=CAT_FOLLOWER_STATE_NAMES,
        ),
        QuestStageRequirementCleanup(
            stage=2,
            remove_required_inventory_options=CAT_FOLLOWER_STATE_NAMES,
        ),
        QuestStageRequirementCleanup(
            stage=5,
            remove_required_inventory_options=CAT_FOLLOWER_STATE_NAMES,
        ),
    ),
    "the_giant_dwarf": (
        QuestStageRequirementCleanup(stage=1, remove_required_inventory=("Telekinetic Grab",)),
    ),
    "the_temple_at_senntisten": (
        QuestStageRequirementCleanup(stage=1, remove_required_inventory=("Telekinetic Grab",)),
    ),
    "the_darkness_of_hallowvale": (
        QuestStageRequirementCleanup(stage=1, remove_required_inventory=("Nails",)),
        QuestStageRequirementCleanup(stage=9, remove_required_inventory=("Telekinetic Grab",)),
    ),
    "nomads_requiem": (
        QuestStageRequirementCleanup(stage=5, remove_required_inventory=("Fire wave",)),
    ),
    "my_arms_big_adventure": (
        QuestStageRequirementCleanup(
            stage=2,
            remove_required_inventory=("Coins", "Tool leprechaun"),
            remove_required_inventory_options=("Compost", "Supercompost"),
            add_required_inventory_options=(
                (("Compost", 1), ("Supercompost", 8)),
            ),
        ),
    ),
    "the_chosen_commander": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Seers' Village Tasks", "Coins"),
        ),
    ),
    "olafs_quest": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Hatchet",),
            add_required_tools=(("Hatchet", 1),),
        ),
    ),
    "as_a_first_resort": AS_A_FIRST_RESORT_STAGE_CLEANUPS,
    "the_branches_of_darkmeyer": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Hatchet",),
            add_required_tools=(("Hatchet", 1),),
        ),
    ),
    "the_great_brain_robbery": (
        QuestStageRequirementCleanup(stage=1, remove_required_inventory=("Nails", "Fur")),
    ),
    "the_golem": (
        QuestStageRequirementCleanup(
            stage=2,
            remove_required_inventory_options=("Soft clay", "Jug", "Water"),
            add_required_inventory=(("Soft clay", 4),),
        ),
    ),
    "perils_of_ice_mountain": (
        QuestStageRequirementCleanup(stage=3, remove_required_inventory=("Nail",)),
    ),
    "toktz_ket_dill": (
        QuestStageRequirementCleanup(stage=1, remove_required_inventory=("A crush weapon",)),
    ),
    "land_of_the_goblins": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=("Recommends Combat level 85 +",),
        ),
    ),
    "the_firemakers_curse": (
        QuestStageRequirementCleanup(
            stage=1,
            remove_required_inventory=(
                "Food",
                "Let Them Eat Pie",
                "Weight-reducing clothing",
                "Attack speed",
                "Expensive_spices_(necklace)",
            ),
        ),
    ),
}

__all__ = ("QUEST_STAGE_REQUIREMENT_CLEANUPS_BY_ID",)
