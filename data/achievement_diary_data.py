"""Achievement diary catalog: regional families, tiers, tasks and rewards.

The owner's design contract is
``memory-bank/achievement-diary-item-grants-design.md``. It fixes the shape:
eight regional equipment families, a Beginner-only Burthorpe/Taverley onboarding
set, and a Miscellaneous pool that keeps its sourced coin payouts.

Task conditions are declared as data rather than as lambdas so the panel can
render a requirement line and a progress figure from the same object the engine
evaluates, and so a task cannot quietly acquire a rule the logic layer does not
own.

The generated catalog takes its task identity and membership from Darkan's
period achievement system. Ordinary requirements remain visible as access gates
but never complete a deed. Un-curated deeds remain visible as dormant tasks with
no predicate. Fixed designed denominators also reserve source-incomplete cutoff
slots without fabricating names.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Tuple

from .achievement_diaries.contract import (
    ACHIEVEMENTS_SOURCE,
    DiaryCondition,
    DiaryFamily,
    DiaryLamp,
    DiaryTask,
    DiaryTier,
)


# Condition kinds. Each names a state surface that already exists in the save,
# which is what makes retroactive credit honest: a task is credited because the
# proving counter is there, never because the player's XP makes it plausible.
CONDITION_KINDS: Tuple[str, ...] = (
    "skill_level",      # key: skill id, amount: level
    "quest",            # key: quest id
    "ledger_output",       # key: "<skill id>:<item name>", amount: quantity
    "ledger_action",       # key: "<skill id>:<action id>", amount: successes
    "ledger_action_family",  # key: "<skill id>:<family id>", amount: successes
    "counter",             # key: dotted player_data path, amount: threshold
    "combat_kill",         # key: combat target id, amount: lifetime kills
    "shop_transaction",    # key: "<type>|<shop id>|<row/action id>", amount: transactions
    "state_equals",        # key: dotted player_data path, expected: exact value
    "hold_item",           # key: item name, amount: quantity held or worn
    "equipped_item",       # key: "<slot>|<item name>", amount: 1
    "any_of",              # key: "", amount: 1, meaning lives in `alternatives`
    "derived_value",       # key: DIARY_DERIVED_VALUES name, amount: threshold
)

# The kinds an ``any_of`` alternative may take: the plain state reads only. A
# disjunction of disjunctions has no source behind it, and the flat form is what
# the panel can render.
# Config v108 changes these stable source rows from requirement gates or dotted
# counter shims to deed predicates. Migration must re-prove them from durable
# evidence instead of retaining completion earned under the superseded rule.
V108_DEED_REVALIDATION_SOURCE_IDS = frozenset({
    5, 15, 29, 40, 44, 50, 52, 56, 79, 84, 86, 88, 99, 104, 105,
    108, 109, 110, 112, 113, 114, 125, 134, 139, 152, 165, 171, 175,
    179, 184, 199, 200, 201, 214, 226, 230, 232, 243, 246, 247, 250,
    253, 263, 271, 272, 288, 302, 305, 309, 310, 311, 314, 323, 336,
    357, 945, 962, 972, 986, 987, 3003, 3004, 3005, 3019,
})


# Config v121 removed proxy completions for the exact rows that were dormant
# when that migration shipped. This historical set must not follow later
# catalog activations, or old saves retain deeds their counters cannot prove.
V121_DORMANT_REVALIDATION_TASK_IDS = frozenset({
    'ardougne_easy_a_cat_is_for_life', 'ardougne_easy_boot_camp',
    'ardougne_easy_breaking_and_entering',
    'ardougne_easy_creator_and_destroyer', 'ardougne_easy_party_pooper',
    'ardougne_easy_preaching_to_the_infected',
    'ardougne_easy_red_revolution', 'ardougne_easy_the_essence_of_magic',
    'ardougne_easy_yoink', 'ardougne_elite_abyssal_valet',
    'ardougne_elite_almost_made_in_ardougne',
    'ardougne_elite_honestly_it_s_not_a_purse',
    'ardougne_elite_you_could_just_knock',
    'ardougne_hard_a_taste_of_the_exotic', 'ardougne_hard_artillery_strike',
    'ardougne_hard_blood_bank_withdrawal', 'ardougne_hard_brace_yourself',
    'ardougne_hard_get_your_stinking_hands_off_me',
    'ardougne_hard_it_just_croaked', 'ardougne_hard_just_like_that',
    'ardougne_hard_living_on_a_prayer', 'ardougne_hard_monkey_business',
    'ardougne_hard_nice_view', 'ardougne_hard_not_on_my_watch',
    'ardougne_hard_vine_detta', 'ardougne_hard_you_re_the_dirty_rascal',
    'ardougne_medium_a_natural_thief', 'ardougne_medium_a_visit_to_charlie',
    'ardougne_medium_are_you_chicken', 'ardougne_medium_arriving_in_style',
    'ardougne_medium_fearless_fishing', 'ardougne_medium_green_fingers',
    'ardougne_medium_i_wonder_what_this_does',
    'ardougne_medium_meeting_history_again',
    'ardougne_medium_sandy_s_secret_getaway',
    'ardougne_medium_the_coal_train', 'ardougne_medium_volatile_valuables',
    'ardougne_medium_water_logged', 'ardougne_medium_what_a_melon',
    'burthorpe_period_a_farmer_in_the_making',
    'burthorpe_period_a_new_threat', 'burthorpe_period_a_pocket_or_two',
    'burthorpe_period_are_you_in_rubble', 'burthorpe_period_arise_hero',
    'burthorpe_period_arm_the_militia', 'burthorpe_period_bank_on_it',
    'burthorpe_period_bottoms_up', 'burthorpe_period_bring_him_down',
    'burthorpe_period_feed_the_refugees', 'burthorpe_period_fine_fine_axe',
    'burthorpe_period_fire_in_the_troll',
    'burthorpe_period_fisherman_s_friends',
    'burthorpe_period_hammer_the_anvil', 'burthorpe_period_heimward_bound',
    'burthorpe_period_jack_of_some_trades',
    'burthorpe_period_like_a_house_on_fire',
    'burthorpe_period_make_them_feel_special',
    'burthorpe_period_mission_complete',
    'burthorpe_period_my_axe_is_my_buddy',
    'burthorpe_period_no_stone_unturned',
    'burthorpe_period_one_thing_after_another',
    'burthorpe_period_out_of_water', 'burthorpe_period_party_on_dudes',
    'burthorpe_period_pocket_wolf', 'burthorpe_period_problem_officer',
    'burthorpe_period_raiders_of_the_frost_dark',
    'burthorpe_period_raising_the_stokes', 'burthorpe_period_rendezvous',
    'burthorpe_period_room_to_manoeuvre',
    'burthorpe_period_spiritual_healing', 'burthorpe_period_super_tuber',
    'burthorpe_period_the_circle_of_life',
    'burthorpe_period_the_red_mist_descends',
    'burthorpe_period_there_s_no_place_like_burthorpe',
    'burthorpe_period_walking_in_the_air_altar',
    'burthorpe_period_we_re_done_here', 'burthorpe_period_wicked',
    'falador_easy_chinchompa_powered', 'falador_easy_disarm_and_embark',
    'falador_easy_elementary_medicine', 'falador_easy_family_values',
    'falador_easy_going_along_with_the_fro',
    'falador_easy_mudskip_the_light_fantastic', 'falador_easy_sir_mitt',
    'falador_easy_sniffing_out_the_mole', 'falador_elite_altar_ed_state',
    'falador_elite_i_swear_i_heard_it_scream',
    'falador_elite_i_ve_changed_my_mind',
    'falador_hard_a_knight_in_the_darkness', 'falador_hard_banned_for_life',
    'falador_hard_child_of_saradomin',
    'falador_hard_i_heard_you_like_mudskips',
    'falador_hard_it_matches_my_eyes', 'falador_hard_it_spoiled_my_view',
    'falador_hard_mass_production', 'falador_hard_the_mogre_mash',
    'falador_hard_the_stonemasons', 'falador_medium_blinded_with_science',
    'falador_medium_climbing_the_walls', 'falador_medium_fruit_of_the_loom',
    'falador_medium_fun_for_the_whole_family',
    'falador_medium_is_it_so_hard_to_walk_round',
    'falador_medium_look_spiffy_for_tiffy',
    'falador_medium_stoic_sweetcorn_guardian',
    'falador_medium_these_aren_t_the_coins_you_re_looking_for',
    'falador_medium_they_have_families_to_feed',
    'fremennik_easy_a_familiar_feeling', 'fremennik_easy_assaulted_goodies',
    'fremennik_easy_hunting_the_hunter', 'fremennik_easy_king_conifer',
    'fremennik_easy_oxymoron_incarnate', 'fremennik_easy_peer_off_the_pier',
    'fremennik_easy_why_did_the_lobster_blush',
    'fremennik_elite_astronomical', 'fremennik_elite_axe_ll_grease',
    'fremennik_elite_first_stryke', 'fremennik_elite_jaws_breaker',
    'fremennik_elite_leap_of_faith', 'fremennik_elite_limber_lumber_jumper',
    'fremennik_elite_no_smoke_without_pyre',
    'fremennik_elite_this_hasta_work', 'fremennik_hard_a_periodic_table',
    'fremennik_hard_defeating_deadly_dagannoths',
    'fremennik_hard_dress_to_impress', 'fremennik_hard_fish_fingers',
    'fremennik_hard_how_to_maim_your_dragon', 'fremennik_hard_pyre_at_will',
    'fremennik_hard_runes_on_the_moon', 'fremennik_medium_big_game_hunter',
    'fremennik_medium_cool_story_bro',
    'fremennik_medium_fairy_mountaineering',
    'fremennik_medium_fremennik_history_101',
    'fremennik_medium_grand_theft_fish', 'fremennik_medium_who_s_a_good_boy',
    'fremennik_medium_yak_attack', 'fremennik_medium_you_know_you_want_it',
    'fremennik_medium_you_really_don_t_need_any_more_shoes',
    'karamja_easy_avast_ardougne', 'karamja_easy_beachcomber',
    'karamja_easy_five_a_day', 'karamja_easy_fruity_catch',
    'karamja_easy_i_m_lichen_this', 'karamja_easy_it_s_a_jungle_ogre',
    'karamja_easy_put_to_port_in_port_sarim',
    'karamja_easy_show_that_you_cairn',
    'karamja_elite_at_one_plus_fifty_five_with_nature',
    'karamja_elite_boxing_clever', 'karamja_elite_crunchy_coating',
    'karamja_elite_it_s_a_snap', 'karamja_elite_ten_in_a_row',
    'karamja_elite_the_power_of_lava', 'karamja_elite_tread_carefully',
    'karamja_elite_walkies', 'karamja_hard_a_palm_for_each_finger',
    'karamja_hard_can_opener', 'karamja_hard_deadwing',
    'karamja_hard_drop_it_like_it_s_hot', 'karamja_hard_flawless_victory',
    'karamja_hard_i_d_be_kharazi_to_eat_this',
    'karamja_hard_quick_as_a_shot', 'karamja_hard_yes_my_master',
    'karamja_medium_back_cran_door', 'karamja_medium_dungeons_and_dragons',
    'karamja_medium_falling_with_style', 'karamja_medium_horseless_carriage',
    'karamja_medium_hotfooting_it',
    'karamja_medium_hunters_of_the_horned_graahk',
    'karamja_medium_just_the_ticket', 'karamja_medium_romancing_the_stone',
    'karamja_medium_scourge_of_scurvy',
    'karamja_medium_shipping_out_from_the_shipyard',
    'karamja_medium_stairway_to_haven', 'karamja_medium_thank_you_madam',
    'karamja_medium_that_s_not_a_knife',
    'karamja_medium_the_roots_of_all_evil',
    'karamja_medium_they_like_me_they_really_like_me',
    'lumbridge_beginner_a_grave_consideration', 'lumbridge_beginner_doom',
    'lumbridge_beginner_grinding_my_gears',
    'lumbridge_beginner_hail_to_the_duke_baby',
    'lumbridge_beginner_master_of_all_i_survey',
    'lumbridge_beginner_passing_out', 'lumbridge_beginner_raise_the_roof',
    'lumbridge_beginner_sage_advice',
    'lumbridge_beginner_shrimpin_ain_t_easy',
    'lumbridge_beginner_tinkle_the_ivories',
    'lumbridge_beginner_window_shopping', 'lumbridge_easy_camping_trip',
    'lumbridge_easy_come_in_here_and_say_that',
    'lumbridge_easy_eye_on_the_prize',
    'lumbridge_easy_i_can_t_hear_dead_people', 'lumbridge_easy_iron_on',
    'lumbridge_easy_it_was_dead_already', 'lumbridge_easy_klept_old_man_ia',
    'lumbridge_easy_money_down_the_drayn',
    'lumbridge_easy_nowt_tool_look_at', 'lumbridge_easy_ratatouille',
    'lumbridge_easy_what_is_this_place',
    'lumbridge_hard_a_body_in_the_sewers',
    'lumbridge_hard_blast_and_hellfire',
    'lumbridge_hard_building_up_strength',
    'lumbridge_hard_gods_give_me_strength',
    'lumbridge_hard_have_your_cake_and_eat_it',
    'lumbridge_hard_not_waving_but_drowning',
    'lumbridge_medium_always_be_prepared',
    'lumbridge_medium_everybody_loves_coal',
    'lumbridge_medium_weeping_willow', 'lumbridge_medium_where_s_the_beef',
    'miscellaneous_miscellaneous_all_fired_up',
    'miscellaneous_miscellaneous_blast_furnace',
    'miscellaneous_miscellaneous_champion_s_challenge',
    'miscellaneous_miscellaneous_defeat_bork',
    'miscellaneous_miscellaneous_tai_bwo_wannai_cleanup',
    'morytania_easy_blooming_marvellous',
    'morytania_easy_chisellin_conchiolin', 'morytania_easy_cranius_lupus',
    'morytania_easy_dislike_anthrope', 'morytania_easy_fortified_spirit',
    'morytania_easy_lab_clean_up_assistant', 'morytania_easy_struck_a_ghast',
    'morytania_easy_wurt_a_bundle', 'morytania_elite_as_good_as_renew',
    'morytania_elite_bros_before_barrows',
    'morytania_elite_fremennik_export',
    'morytania_elite_not_such_a_rotten_idea',
    'morytania_elite_on_wings_of_bling', 'morytania_elite_set_it_on_fiyr',
    'morytania_elite_thoroughly_a_ghast',
    'morytania_hard_better_than_cursing_the_darkness',
    'morytania_hard_detarnation', 'morytania_hard_huge_success',
    'morytania_hard_i_brought_your_stuff_back',
    'morytania_hard_just_one_more_key', 'morytania_hard_raising_the_stakes',
    'morytania_hard_runecraft_carrier',
    'morytania_hard_shade_shattering_ka_bloom',
    'morytania_hard_they_ll_just_throw_it_away_again',
    'morytania_hard_time_salver', 'morytania_medium_ad_myre_the_goods',
    'morytania_medium_brain_bending',
    'morytania_medium_finding_your_balance',
    'morytania_medium_flamtaer_will_get_you_everywhere',
    'morytania_medium_fun_guy_but_bitter',
    'morytania_medium_gate_spectre_ations',
    'morytania_medium_i_wonder_how_far_it_ghost',
    'morytania_medium_izzy_wizzy_let_s_get_lizzy',
    'morytania_medium_plenty_mort_where_that_came_from',
    'morytania_medium_polterheist', 'morytania_medium_the_higher_the_badder',
    'morytania_medium_the_yeast_they_can_do',
    'morytania_medium_travelling_on_the_slime_trail',
    'seers_easy_a_seer_ing_light', 'seers_easy_bunch_of_flours',
    'seers_easy_happy_hour', 'seers_easy_jute_alors',
    'seers_easy_la_morte_d_arthur', 'seers_easy_reflax_actions',
    'seers_easy_sinclair_swirling', 'seers_easy_stir_galahad',
    'seers_easy_why', 'seers_elite_it_s_a_trap_no_wait_it_s_a_pie',
    'seers_elite_make_a_bolt_for_it', 'seers_elite_plentypotionentiary',
    'seers_elite_the_long_of_it', 'seers_hard_alch_aholic',
    'seers_hard_at_home_on_the_range', 'seers_hard_beware_of_the_dog',
    'seers_hard_gonna_need_a_bigger_range', 'seers_hard_island_hopper',
    'seers_hard_prayer_of_attorney', 'seers_hard_water_palaver',
    'seers_medium_at_least_it_doesn_t_need_walking',
    'seers_medium_familiar_fire_familiarity',
    'seers_medium_fleeing_the_scene',
    'seers_medium_i_can_seer_my_house_from_here',
    'seers_medium_it_s_a_slightly_magical_stick',
    'seers_medium_it_s_only_a_model', 'seers_medium_king_coal',
    'seers_medium_mastering_the_elements', 'seers_medium_sniper_training',
    'varrock_easy_doing_the_ironing', 'varrock_easy_essential_facilitator',
    'varrock_easy_jumping_off_point', 'varrock_easy_making_learning_fun',
    'varrock_easy_plank_you_very_much', 'varrock_easy_pot_stop',
    'varrock_easy_relocation_relocation_relocation',
    'varrock_easy_strike_a_pose', 'varrock_elite_a_bolt_from_the_blue',
    'varrock_elite_a_ton_of_earth', 'varrock_elite_double_jointed',
    'varrock_elite_it_all_adze_up', 'varrock_elite_mind_your_back',
    'varrock_elite_nomadness', 'varrock_elite_red_red_pies_of_summer',
    'varrock_elite_splitting_headache',
    'varrock_elite_stick_a_bork_in_him_he_s_done',
    'varrock_hard_burning_bush',
    'varrock_hard_but_it_won_t_warp_you_anywhere',
    'varrock_hard_changing_rooms', 'varrock_hard_hand_me_downs',
    'varrock_hard_intersceptre', 'varrock_hard_lighten_up',
    'varrock_hard_living_on_the_edge',
    'varrock_hard_put_your_smithing_hat_on', 'varrock_hard_waka_waka_waka',
    'varrock_hard_who_ate_all_the_pie', 'varrock_medium_a_lick_of_paint',
    'varrock_medium_engage', 'varrock_medium_faster_pussycat_kill_kill',
    'varrock_medium_for_fast_transactions', 'varrock_medium_master_scrumper',
    'varrock_medium_point_of_en_tree', 'varrock_medium_promised_the_earth',
    'varrock_medium_return_to_senntisten',
    'varrock_medium_royale_with_thieve', 'varrock_medium_the_body_shop',
    'varrock_medium_what_lies_below', 'varrock_medium_with_a_ten_foot_pole',
    'varrock_medium_you_wouldn_t_like_me_when_i_m_angry',
})


BASE_CONDITION_KINDS: Tuple[str, ...] = (
    "skill_level",
    "quest",
    "ledger_output",
    "ledger_action",
    "ledger_action_family",
    "counter",
    "combat_kill",
    "shop_transaction",
    "state_equals",
    "hold_item",
    "equipped_item",
)


# The live catalog. Regional families are generated from Darkan's tier tables
# joined to the pinned pre-cutoff wiki requirement columns; see
# ``tools/generate_achievement_diary_data.py``.
from .achievement_diary_catalog import (  # noqa: E402  (avoids a cycle at import)
    DIARY_FAMILIES,
    diary_equipment_data_as_dict,
)

ACHIEVEMENT_DIARY_CATALOG: Tuple[DiaryFamily, ...] = DIARY_FAMILIES


def diary_lamp_claim_id(tier_id: str) -> str:
    return f"achievement_diary_{tier_id}_xp_lamp"


DIARY_LAMP_CLAIM_IDS_BY_TIER = {
    tier.id: diary_lamp_claim_id(tier.id)
    for family in ACHIEVEMENT_DIARY_CATALOG
    for tier in family.tiers
    if tier.lamp is not None
}


def diary_lamp_claims_as_dict() -> dict[str, dict[str, Any]]:
    """Bank Claim rows created by regional diary tier claims."""

    claims: dict[str, dict[str, Any]] = {}
    for family in ACHIEVEMENT_DIARY_CATALOG:
        for tier in family.tiers:
            lamp = tier.lamp
            if lamp is None:
                continue
            claim_id = diary_lamp_claim_id(tier.id)
            claims[claim_id] = {
                "id": claim_id,
                "display_name": (
                    f"{family.name} {tier.name}: reward lamp"
                    f" ({lamp.experience:,} XP)"
                ),
                "claim_type": "xp_lamp",
                "item_name": "Reward lamp",
                "quantity": 1,
                "items": (),
                "source": tier.source or family.source,
                "required_quest": "",
                "required_runecrafting_level": 0,
                "required_diary_tier": tier.id,
                "xp_amount": float(lamp.experience),
                # Empty is the established Bank Claim representation for any
                # trainable skill; the claims logic expands it at render/spend time.
                "skill_options": lamp.skills,
                "minimum_level": lamp.minimum_level,
            }
    return claims


def _assert_derived_values_are_registered() -> None:
    """A ``derived_value`` typo must be an ImportError, never a silent row.

    The evaluator falls back to zero for an unknown name, so nothing else would
    ever say the row is impossible: the panel would render an honest-looking
    0/153 forever.
    """

    from ..logic.achievement_diary_derived import (  # noqa: E402  (avoids a cycle)
        DIARY_DERIVED_VALUE_CEILINGS,
        DIARY_DERIVED_VALUES,
    )

    for family in ACHIEVEMENT_DIARY_CATALOG:
        for tier in family.tiers:
            for task in tier.tasks:
                for condition in task.conditions:
                    if condition.kind != "derived_value":
                        continue
                    if condition.key not in DIARY_DERIVED_VALUES:
                        raise ImportError(
                            f"{task.id}: derived_value {condition.key!r} is not in"
                            " DIARY_DERIVED_VALUES"
                        )
                    if condition.key not in DIARY_DERIVED_VALUE_CEILINGS:
                        raise ImportError(
                            f"{task.id}: derived_value {condition.key!r} has no"
                            " entry in DIARY_DERIVED_VALUE_CEILINGS"
                        )


_assert_derived_values_are_registered()

__all__ = [
    "ACHIEVEMENT_DIARY_CATALOG",
    "ACHIEVEMENTS_SOURCE",
    "BASE_CONDITION_KINDS",
    "CONDITION_KINDS",
    "DiaryCondition",
    "DiaryFamily",
    "DiaryLamp",
    "DiaryTask",
    "DiaryTier",
    "V108_DEED_REVALIDATION_SOURCE_IDS",
    "V121_DORMANT_REVALIDATION_TASK_IDS",
    "diary_equipment_data_as_dict",
]
