from __future__ import annotations

from .dependencies import *
from .contract import *
from .ids import *
from .sources import *
from .catalog import _quest_with_stage_requirements, _catalog_int, _quest_from_catalog, _quest_catalog_row_id
from .catalog_overrides import *
from .definitions import *

from .another_cook import apply_another_cook_opening
from . import definitions as _definitions

QUEST_OVERRIDE_ORDER = (
    'cooks_assistant',
    'shield_of_arrav',
    'fight_arena',
    'witchs_house',
    'merlins_crystal',
    'heroes_quest',
    'family_crest',
    'temple_of_ikov',
    'demon_slayer',
    'dragon_slayer',
    'ernest_the_chicken',
    'black_knights_fortress',
    'goblin_diplomacy',
    'vampyre_slayer',
    'the_restless_ghost',
    'imp_catcher',
    'pirates_treasure',
    'jungle_potion',
    'shilo_village',
    'lost_city',
    'druidic_ritual',
    'rune_mysteries',
    'the_knights_sword',
    'priest_in_peril',
    'tai_bwo_wannai_trio',
    'mournings_end_part_ii',
    'swan_song',
    'lunar_diplomacy',
    'legacy_of_seergaze',
)
MINIQUEST_ORDER = (
    'bar_crawl',
    'hunt_for_surok',
    'lair_of_tarn_razorlor',
    'skippy_and_the_mogres',
)
QUEST_OVERRIDES = tuple(_definitions._QUESTS_BY_ID[quest_id] for quest_id in QUEST_OVERRIDE_ORDER)
QUEST_OVERRIDES_BY_ID = {quest.id: quest for quest in QUEST_OVERRIDES}
MINIQUESTS = tuple(_definitions._QUESTS_BY_ID[quest_id] for quest_id in MINIQUEST_ORDER)


# The taught non-combat item work stays on quest cards, with no new Utility rows.
QUEST_SUPPLY_RECIPES_BY_ID = {
    COOKS_ASSISTANT_ID: (
        QuestSupplyRecipe(step="take the bucket beside the prized cow", product="Bucket",
                          source="https://runescape.wiki/w/Cook's_Assistant?oldid=6540848"),
        QuestSupplyRecipe(step="take the kitchen pot", product="Empty pot",
                          source="https://runescape.wiki/w/Cook's_Assistant?oldid=6540848"),
    ),
    BLACK_KNIGHTS_FORTRESS_ID: (
        QuestSupplyRecipe(step="pick a Monastery cabbage", product="Cabbage",
                          source="https://runescape.wiki/w/Black_Knights'_Fortress_(quest)?oldid=6569597"),
    ),
    DEMON_SLAYER_ID: (
        QuestSupplyRecipe(step="take the castle kitchen bucket", product="Bucket",
                          source="https://runescape.wiki/w/Demon_Slayer_(historical)?oldid=6448395"),
        QuestSupplyRecipe(step="fill the bucket", product="Bucket of water", inputs=(("Bucket", 1),),
                          source="https://runescape.wiki/w/Demon_Slayer_(historical)?oldid=6448395"),
    ),
    ERNEST_THE_CHICKEN_ID: (
        QuestSupplyRecipe(step="take fish food upstairs", product="Fish food",
                          source="https://runescape.wiki/w/Ernest_the_Chicken?oldid=6542622"),
        QuestSupplyRecipe(step="take poison from the manor table", product="Poison",
                          source="https://runescape.wiki/w/Ernest_the_Chicken?oldid=6542622"),
    ),
    FISHING_CONTEST_ID: (
        QuestSupplyRecipe(step="take garlic in Seers' Village", product="Garlic",
                          source="https://runescape.wiki/w/Fishing_Contest?oldid=6326002"),
        QuestSupplyRecipe(step="dig red vine worms", product="Red vine worm",
                          required_tools=(("Spade", 1),),
                          source="https://runescape.wiki/w/Fishing_Contest?oldid=6326002"),
    ),
    GERTRUDES_CAT_ID: (
        QuestSupplyRecipe(step="milk the Lumbridge cow", product="Bucket of milk", inputs=(("Bucket", 1),),
                          source="https://runescape.wiki/w/Gertrude's_Cat?oldid=6326014"),
        QuestSupplyRecipe(step="pick doogle leaves behind Gertrude's house", product="Doogle leaves",
                          source="https://runescape.wiki/w/Gertrude's_Cat?oldid=6326014"),
    ),
    MERLINS_CRYSTAL_ID: (
        QuestSupplyRecipe(step="take the bucket by the beehives", product="Bucket",
                          source="https://runescape.wiki/w/Merlin's_Crystal?oldid=6569685"),
        QuestSupplyRecipe(step="take insect repellent in Catherby", product="Insect repellent",
                          source="https://runescape.wiki/w/Merlin's_Crystal?oldid=6569685"),
    ),
    PIRATES_TREASURE_ID: (
        QuestSupplyRecipe(step="buy rum from Zambo", product="Karamjan rum", coins=30,
                          source="https://runescape.wiki/w/Pirate's_Treasure?oldid=6514086"),
        QuestSupplyRecipe(step="take the spade in Falador's Estate Agent building", product="Spade",
                          source="https://runescape.wiki/w/Pirate's_Treasure?oldid=6514086"),
    ),
    PLAGUE_CITY_ID: (
        QuestSupplyRecipe(step="take a bucket in Edmond's garden", product="Bucket",
                          source="https://runescape.wiki/w/Plague_City?oldid=6544754"),
        QuestSupplyRecipe(step="fill a bucket in Edmond's house", product="Bucket of water", inputs=(("Bucket", 1),),
                          source="https://runescape.wiki/w/Plague_City?oldid=6544754"),
        QuestSupplyRecipe(step="buy chocolate from Wydin", product="Chocolate bar", coins=20,
                          source="https://runescape.wiki/w/Chocolate_bar?oldid=6550445"),
        QuestSupplyRecipe(step="grind the chocolate bar", product="Chocolate dust", inputs=(("Chocolate bar", 1),),
                          required_tools=(("Pestle and mortar", 1),),
                          source="https://runescape.wiki/w/Chocolate_bar?oldid=6550445"),
        QuestSupplyRecipe(step="milk a dairy cow", product="Bucket of milk", inputs=(("Bucket", 1),),
                          source="https://runescape.wiki/w/Bucket_of_milk?oldid=6288698"),
        QuestSupplyRecipe(step="pick snape grass on the peninsula", product="Snape grass",
                          source="https://runescape.wiki/w/Snape_grass?oldid=6269500"),
    ),
    SKIPPY_AND_THE_MOGRES_ID: (
        QuestSupplyRecipe(step="take a bucket by the Port Sarim farming shop", product="Bucket",
                          source="https://runescape.wiki/w/Bucket?oldid=6337544"),
        QuestSupplyRecipe(step="take a bowl in Lumbridge Castle kitchen", product="Bowl",
                          source="https://runescape.wiki/w/Bowl?oldid=5102426"),
        QuestSupplyRecipe(step="fill the bucket", product="Bucket of water", inputs=(("Bucket", 1),),
                          source="https://runescape.wiki/w/Mogre_(lore_activity)?oldid=6070158"),
        QuestSupplyRecipe(step="pick nettles near Draynor jail", product="Nettles",
                          required_tools=(("Leather gloves", 1),),
                          source="https://runescape.wiki/w/Mogre_(lore_activity)?oldid=6070158"),
        QuestSupplyRecipe(step="fill the bowl", product="Bowl of water", inputs=(("Bowl", 1),),
                          source="https://runescape.wiki/w/Nettle_tea?oldid=6241728"),
        QuestSupplyRecipe(step="mix nettles into water", product="Nettle-water", inputs=(("Bowl of water", 1), ("Nettles", 1)),
                          source="https://runescape.wiki/w/Nettle_tea?oldid=6241728"),
        QuestSupplyRecipe(step="boil the nettle-water", product="Nettle tea", inputs=(("Nettle-water", 1),),
                          required_skills=(QuestSkillRequirement("cooking", "Cooking", 20),),
                          xp_rewards=(QuestXpReward("cooking", 61),),
                          source="https://runescape.wiki/w/Nettle_tea?oldid=6241728"),
        QuestSupplyRecipe(step="buy chocolate from Wydin", product="Chocolate bar", coins=20,
                          source="https://runescape.wiki/w/Chocolate_bar?oldid=6550445"),
        QuestSupplyRecipe(step="grind the chocolate bar", product="Chocolate dust", inputs=(("Chocolate bar", 1),),
                          required_tools=(("Pestle and mortar", 1),),
                          source="https://runescape.wiki/w/Chocolate_bar?oldid=6550445"),
        QuestSupplyRecipe(step="milk a dairy cow", product="Bucket of milk", inputs=(("Bucket", 1),),
                          source="https://runescape.wiki/w/Bucket_of_milk?oldid=6288698"),
        QuestSupplyRecipe(step="pick snape grass on the peninsula", product="Snape grass",
                          source="https://runescape.wiki/w/Snape_grass?oldid=6269500"),
    ),
    DRAGON_SLAYER_ID: (
        QuestSupplyRecipe(step="take a plank on Entrana", product="Plank",
                          source="https://runescape.wiki/w/Dragon_Slayer?oldid=6461164"),
        QuestSupplyRecipe(step="smith steel nails", product="Steel nails", quantity=15, inputs=(("Steel bar", 1),),
                          required_skills=(QuestSkillRequirement("smithing", "Smithing", 34),),
                          required_tools=(("Hammer", 1),), xp_rewards=(QuestXpReward("smithing", 37.5),),
                          source="https://runescape.wiki/w/Steel_nails?oldid=6446028"),
    ),
    HEROES_QUEST_ID: (
        QuestSupplyRecipe(step="buy a fishing rod from Gerrant", product="Fishing rod", coins=5,
                          source="https://runescape.wiki/w/Heroes'_Quest?oldid=6534275; "
                                 "https://runescape.wiki/w/Fishing_rod?oldid=6438198"),
        QuestSupplyRecipe(step="buy fishing bait from Gerrant", product="Fishing bait", coins=3,
                          source="https://runescape.wiki/w/Heroes'_Quest?oldid=6534275; "
                                 "https://runescape.wiki/w/Fishing_bait?oldid=6319816"),
    ),
    MONKS_FRIEND_ID: (
        QuestSupplyRecipe(step="buy a jug at Aemad's Adventuring Supplies", product="Jug", coins=1,
                          source="https://runescape.wiki/w/Monk's_Friend?oldid=6514084; "
                                 "https://wiki.darkan.org/index.php?title=Aemad%27s_Adventuring_Supplies&oldid=40707"),
        QuestSupplyRecipe(step="fill the jug at Cedric's well", product="Jug of water", inputs=(("Jug", 1),),
                          source="https://runescape.wiki/w/Monk's_Friend?oldid=6514084"),
        QuestSupplyRecipe(step="cut a tree near Cedric", product="Logs", required_tools=(("Hatchet", 1),),
                          required_skills=(QuestSkillRequirement("woodcutting", "Woodcutting", 1),),
                          xp_rewards=(QuestXpReward("woodcutting", 25),),
                          source="https://runescape.wiki/w/Monk's_Friend?oldid=6514084; "
                                 "https://wiki.darkan.org/index.php?title=Logs&oldid=31356"),
    ),
    CLOCK_TOWER_ID: (
        QuestSupplyRecipe(step="take the water bucket by the zoo well", product="Bucket of water",
                          source="https://runescape.wiki/w/Clock_Tower?oldid=6565072"),
    ),
    TREE_GNOME_VILLAGE_ID: (
        QuestSupplyRecipe(step="cut a tree for Commander Montai", product="Logs", required_tools=(("Hatchet", 1),),
                          required_skills=(QuestSkillRequirement("woodcutting", "Woodcutting", 1),),
                          xp_rewards=(QuestXpReward("woodcutting", 25),),
                          source="https://runescape.wiki/w/Tree_Gnome_Village?oldid=6541699; "
                                 "https://wiki.darkan.org/index.php?title=Logs&oldid=31356"),
    ),
    SHILO_VILLAGE_ID: (
        QuestSupplyRecipe(step="buy a chisel from Jiminua", product="Chisel", coins=14,
                          source="https://runescape.wiki/w/Shilo_Village?oldid=6389566; "
                                 "https://runescape.wiki/w/Chisel?oldid=6133640"),
    ),
    TAI_BWO_WANNAI_TRIO_ID: (
        QuestSupplyRecipe(step="net karambwanji south of Tai Bwo Wannai", product="Raw karambwanji",
                          required_tools=(("Small fishing net", 1),),
                          required_skills=(QuestSkillRequirement("fishing", "Fishing", 5),),
                          xp_rewards=(QuestXpReward("fishing", 5),),
                          source="https://runescape.wiki/w/Tai_Bwo_Wannai_Trio?oldid=6529797; "
                                 "https://wiki.darkan.org/index.php?title=Raw_karambwanji&oldid=44929"),
        QuestSupplyRecipe(step="catch karambwan north of the shipyard", product="Raw karambwan",
                          inputs=(("Raw karambwanji", 1),), required_tools=(("Karambwan vessel", 1),),
                          required_skills=(QuestSkillRequirement("fishing", "Fishing", 65),),
                          xp_rewards=(QuestXpReward("fishing", 105),),
                          source="https://runescape.wiki/w/Raw_karambwan?oldid=6096116"),
    ),
    THE_FREMENNIK_TRIALS_ID: (
        QuestSupplyRecipe(step="buy beer at the Seers' Village bar", product="Beer", coins=2,
                          source="https://runescape.wiki/w/The_Fremennik_Trials?oldid=6548589; "
                                 "https://runescape.wiki/w/Strange_object?oldid=5163331"),
    ),
    "the_tale_of_the_muspah": (
        QuestSupplyRecipe(step="mine and cut a cave sapphire", product="Sapphire",
                          required_tools=(("Pickaxe", 1), ("Chisel", 1)),
                          required_skills=(QuestSkillRequirement("mining", "Mining", 8),),
                          source="https://runescape.wiki/w/The_Tale_of_the_Muspah?oldid=6539749"),
    ),
    THE_KNIGHTS_SWORD_ID: (
        QuestSupplyRecipe(step="mine blurite in the ice dungeon", product="Blurite ore",
                          required_skills=(QuestSkillRequirement("mining", "Mining", 10),),
                          required_tools=(("Pickaxe", 1),), xp_rewards=(QuestXpReward("mining", 17.5),),
                          source="https://runescape.wiki/w/The_Knight's_Sword?oldid=6514292; "
                                 "https://runescape.wiki/w/Blurite_ore?oldid=6298112"),
    ),
}


def _quest_with_supply_recipes(quest):
    recipes = QUEST_SUPPLY_RECIPES_BY_ID.get(quest.id)
    return replace(quest, supply_recipes=recipes) if recipes is not None else quest


QUESTS: Tuple[QuestDefinition, ...] = tuple(
    apply_another_cook_opening(_quest_with_supply_recipes(_quest_with_stage_requirements(
        replace(QUEST_OVERRIDES_BY_ID[row_id], release_order=_catalog_int(row, "release_order", 9999))
        if row_id in QUEST_OVERRIDES_BY_ID
        else _quest_from_catalog(row),
        row,
    )))
    for row in PRE_EOC_QUEST_CATALOG
    for row_id in (_quest_catalog_row_id(row),)
) + tuple(
    _quest_with_supply_recipes(_quest_with_stage_requirements(quest, {})) for quest in MINIQUESTS
)
QUESTS_BY_ID: Dict[str, QuestDefinition] = {quest.id: quest for quest in QUESTS}
QUEST_DISPLAY_NAMES: Dict[str, str] = {quest.id: quest.display_name for quest in QUESTS}

# Compatibility export retained for callers that were added during the first
# quest-lock pass. Unlock quest ids now all resolve to playable QuestDefinition
# rows, so there are no state-only references left.
QUEST_REFERENCES: Tuple[QuestReference, ...] = ()
QUEST_REFERENCES_BY_ID: Dict[str, QuestReference] = {}

QUEST_UNLOCK_RULES: Tuple[QuestUnlockRule, ...] = (QuestUnlockRule(BIG_CHOMPY_BIRD_HUNTING_ID, "target", "utility", (chompy_hunting_data.CHOMPY_HUNTING_ACTIVITY_ID,), "Big Chompy Bird Hunting", chompy_hunting_data.BIG_CHOMPY_BIRD_HUNTING_STAGE_ACTION_SOURCE),
    QuestUnlockRule(RUNE_MYSTERIES_ID, "target", "mining", ("rune_essence",), "Rune Mysteries", RUNE_ESSENCE_MINE_SOURCE),
    QuestUnlockRule(
        LOST_CITY_ID,
        "target",
        "runecrafting",
        ("craft_cosmic_runes", "bind_cosmic_tiara"),
        "Lost City",
        RUNECRAFTING_BASICS_SOURCE,
    ),
    QuestUnlockRule(LUNAR_DIPLOMACY_ID, "target", "runecrafting", ("craft_astral_runes",), "Lunar Diplomacy", RUNECRAFTING_ALTARS_SOURCE),
    QuestUnlockRule(
        MOURNINGS_END_PART_II_ID,
        "target",
        "runecrafting",
        ("craft_death_runes", "bind_death_tiara"),
        "Mourning's End Part II",
        RUNECRAFTING_BASICS_SOURCE,
    ),
    QuestUnlockRule(
        LEGACY_OF_SEERGAZE_ID,
        "target",
        "runecrafting",
        ("craft_blood_runes", "bind_blood_tiara"),
        "Legacy of Seergaze",
        RUNECRAFTING_BASICS_SOURCE,
    ),
    QuestUnlockRule(SWAN_SONG_ID, "target", "fishing", ("catch_monkfish",), "Swan Song", RAW_MONKFISH_SOURCE),
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
) + (TargetUnlockRule("target", "fishing", ("catch_karambwan",), (TargetUnlockRequirement("quest_started", "Start Tai Bwo Wannai Trio", RAW_KARAMBWAN_SOURCE, TAI_BWO_WANNAI_TRIO_ID),)),
    TargetUnlockRule("target", "utility", ("collect_ugthanki_dung",), (TargetUnlockRequirement("quest_started", "Start The Feud", "https://runescape.wiki/w/Ugthanki_dung?oldid=6288566", THE_FEUD_ID),)),
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
        skill_id="crafting",
        target_ids=("craft_fremennik_round_shield",),
        requirements=(
            TargetUnlockRequirement(
                kind="quest_stage",
                reason="Reach The Fremennik Isles traditional rites",
                source=THE_FREMENNIK_ISLES_SOURCE,
                quest_id=THE_FREMENNIK_ISLES_ID,
                stage=5,
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
        id="cabin_fever_bill_teach_coins",
        display_name="Cabin Fever: Speak to Bill Teach",
        source="https://runescape.wiki/w/Cabin_Fever?oldid=6533785",
        item_name="Coins",
        quantity=10000,
        required_quest="cabin_fever",
    ),
    ClaimDefinition(
        id="rocking_out_bill_teach_magical_cage",
        display_name="Rocking Out: Speak to Bill Teach",
        source="https://runescape.wiki/w/Rocking_Out?oldid=6521879",
        item_name="Magical cage",
        required_quest=ROCKING_OUT_ID,
    ),
    ClaimDefinition(
        id="the_golem_thammarons_throne_gems",
        display_name="The Golem: Chisel Thammaron's throne",
        source="https://runescape.wiki/w/The_Golem?oldid=6543894",
        claim_type="item_bundle",
        item_name="Ruby",
        items=(("Ruby", 2), ("Emerald", 2), ("Sapphire", 2)),
        required_quest="the_golem",
        required_tools=(("Chisel", 1), ("Hammer", 1)),
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
    *(
        ClaimDefinition(
            id=claim_id,
            display_name=(
                f"Stronghold of Player Safety: Antique lamp {index} (500 XP)"
            ),
            source=STRONGHOLD_PLAYER_SAFETY_LAMP_SOURCE,
            claim_type="xp_lamp",
            item_name="Antique lamp",
            required_quest="",
            xp_amount=500.0,
            minimum_level=1,
            delivery_required=True,
        )
        for index, claim_id in enumerate(
            STRONGHOLD_PLAYER_SAFETY_LAMP_CLAIM_IDS, start=1
        )
    ),
    *_quest_lamp_claims(),
)
CLAIMS_BY_ID: Dict[str, ClaimDefinition] = {claim.id: claim for claim in CLAIMS}


def default_quest_states() -> Dict[str, Dict[str, object]]:
    return {quest.id: {"started": False, "progress": 0, "completed": False} for quest in QUESTS}


def default_claim_states() -> Dict[str, Dict[str, object]]:
    states = {}
    for claim in CLAIMS:
        state = {"claimed": False}
        if claim.delivery_required:
            state["delivered"] = False
        states[claim.id] = state
    return states


default_quest_states.__module__ = "ankiscape.data.quest_data"
default_claim_states.__module__ = "ankiscape.data.quest_data"


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
            "required_tools": claim.required_tools,
            "required_runecrafting_level": claim.required_runecrafting_level,
            "xp_amount": claim.xp_amount,
            "skill_options": claim.skill_options,
            "minimum_level": claim.minimum_level,
            "delivery_required": claim.delivery_required,
        }
        for claim in CLAIMS
    }
    from ..achievement_diary_data import diary_lamp_claims_as_dict

    claims.update(diary_lamp_claims_as_dict())
    return claims


claims_as_dict.__module__ = "ankiscape.data.quest_data"

__all__ = (
    'QUEST_OVERRIDES', 'QUEST_OVERRIDES_BY_ID', 'MINIQUESTS', 'QUESTS', 'QUESTS_BY_ID', 'QUEST_DISPLAY_NAMES', 'QUEST_REFERENCES', 'QUEST_REFERENCES_BY_ID', 'QUEST_UNLOCK_RULES', 'TARGET_UNLOCK_RULES',
    'TUTORIAL_ISLAND_STARTER_KIT_ITEMS', 'CLAIMS', 'CLAIMS_BY_ID', 'default_quest_states', 'default_claim_states', 'claims_as_dict',
)
