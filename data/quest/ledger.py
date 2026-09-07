from __future__ import annotations

from .dependencies import *
from .contract import *
from .ids import *
from .sources import *
from .catalog import _quest_with_stage_requirements, _catalog_int, _quest_from_catalog, _quest_catalog_row_id
from .catalog_overrides import *
from .definitions import *

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
    'hunt_for_surok',
    'lair_of_tarn_razorlor',
)
QUEST_OVERRIDES = tuple(_definitions._QUESTS_BY_ID[quest_id] for quest_id in QUEST_OVERRIDE_ORDER)
QUEST_OVERRIDES_BY_ID = {quest.id: quest for quest in QUEST_OVERRIDES}
MINIQUESTS = tuple(_definitions._QUESTS_BY_ID[quest_id] for quest_id in MINIQUEST_ORDER)


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

QUEST_UNLOCK_RULES: Tuple[QuestUnlockRule, ...] = (QuestUnlockRule(BIG_CHOMPY_BIRD_HUNTING_ID, "target", "utility", (chompy_hunting_data.CHOMPY_HUNTING_ACTIVITY_ID,), "Big Chompy Bird Hunting", chompy_hunting_data.BIG_CHOMPY_BIRD_HUNTING_STAGE_ACTION_SOURCE),
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
