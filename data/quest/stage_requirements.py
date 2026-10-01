from __future__ import annotations

from .dependencies import *

STAGE_REQUIREMENT_REPLACEMENT_ORDER = (
    'hazeel_cult',
    'jungle_potion',
    'shilo_village',
    'icthlarins_little_helper',
    'smoking_kills',
    'diamond_in_the_rough',
    'stolen_hearts',
    'cooks_assistant',
    'holy_grail',
    'tree_gnome_village',
    'fishing_contest',
    'gertrudes_cat',
    'clock_tower',
    'monks_friend',
    'tribal_totem',
    'scorpion_catcher',
    'sheep_herder',
    'plague_city',
    'biohazard',
    'waterfall_quest',
    'dwarf_cannon',
    'fight_arena',
    'demon_slayer',
    'dragon_slayer',
    'goblin_diplomacy',
    'ernest_the_chicken',
    'black_knights_fortress',
    'vampyre_slayer',
    'the_restless_ghost',
    'imp_catcher',
    'pirates_treasure',
    'druidic_ritual',
    'rune_mysteries',
    'priest_in_peril',
    'nature_spirit',
    'a_fairy_tale_i_growing_pains',
    'a_souls_bane',
    'witchs_house',
    'lost_city',
    'tai_bwo_wannai_trio',
    'carnillean_rising',
    'deadliest_catch',
    'wolf_whistle',
    'song_from_the_depths',
    'some_like_it_cold',
    'the_fremennik_isles',
)

from . import definitions as _definitions
from . import stage_overrides as _stage_overrides

_FRAGMENTS_BY_QUEST = {
    **_definitions._STAGE_REQUIREMENT_REPLACEMENTS_BY_QUEST,
    **_stage_overrides._STAGE_REQUIREMENT_REPLACEMENTS_BY_QUEST,
}
QUEST_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID = {}
for _quest_id in STAGE_REQUIREMENT_REPLACEMENT_ORDER:
    QUEST_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID.update(_FRAGMENTS_BY_QUEST[_quest_id])

__all__ = (
    'QUEST_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID',
)
