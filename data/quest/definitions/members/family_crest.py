from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

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

QUEST = QuestDefinition(
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
    )

_REWARD_ITEM_FRAGMENT_0 = {
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
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'FAMILY_CREST_STAGES', 'FAMILY_CREST_STAGE_REQUIREMENTS',
)
