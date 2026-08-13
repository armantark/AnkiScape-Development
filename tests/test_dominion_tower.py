"""Dominion Tower: the roster, the wheel, the factor, and every reward.

The tests below drive the real command and review handlers from a fresh
`default_player_data`. Nothing about the tower is mocked: the quest gates read
the real quest ledger, the fights run through `apply_combat_burst_pure`, and the
glove, dreadnip, mine and Ascendancy-mine rewards are each reached by actually
killing the bosses their unlock condition names.
"""

from __future__ import annotations

import copy
import json
import os
import random
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import (
    EQUIPMENT_DATA,
    EXTRA_ITEM_DATA,
    EXTRA_ITEM_IMAGES,
    ITEM_DEFINITIONS,
    ORE_DATA,
    UTILITY_ACTIVITY_DATA,
)
from ankiscape.core.storage_pure import (
    CURRENT_CONFIG_VERSION,
    default_player_data,
    migrate_loaded_data,
)
from ankiscape.data.dominion_tower_data import (
    DOMINION_TOWER_ACTIVITY_ID,
    DOMINION_TOWER_ASSET_MANIFEST,
    DOMINION_TOWER_BOSS_CLASS_MIN_FLOOR,
    DOMINION_TOWER_COMBAT_LEVEL_REQUIREMENT,
    DOMINION_TOWER_ENCOUNTERS,
    DOMINION_TOWER_ENCOUNTERS_BY_ID,
    DOMINION_TOWER_GLOVE_SETS,
    DOMINION_TOWER_HANDICAP_COUNT,
    DOMINION_TOWER_HANDICAP_IDS,
    DOMINION_TOWER_HANDICAPS,
    DOMINION_TOWER_HANDICAPS_BY_ID,
    DOMINION_TOWER_JOURNAL_PAGE,
    DOMINION_TOWER_MAX_FACTOR,
    DOMINION_TOWER_MINE,
    DOMINION_TOWER_MINE_COST,
    DOMINION_TOWER_MODES_BY_ID,
    DOMINION_TOWER_NPCS,
    DOMINION_TOWER_QUEST_POOL,
    DOMINION_TOWER_QUEST_REQUIREMENT,
    DOMINION_TOWER_REWARD_CREDIT_CAP,
    DOMINION_TOWER_SPECIAL_MATCHES,
    DOMINION_TOWER_SWORD,
    DOMINION_TOWER_XP_BOOK,
    RECIPE_FOR_DISASTER_REQUIREMENT_ID,
    RECIPE_FOR_DISASTER_SUBQUESTS,
    dominion_tower_encounter_total_level_pure,
)
from ankiscape.logic.dominion_tower_logic import (
    _nudged_handicap,
    apply_dominion_tower_command_pure,
    apply_dominion_tower_review_pure,
    default_dominion_tower_state_pure,
    dominion_tower_available_encounters_pure,
    dominion_tower_can_review_pure,
    dominion_tower_completed_quests_pure,
    dominion_tower_round_factor_pure,
    dominion_tower_view_pure,
    dominion_tower_xp_book_amount_pure,
    sanitize_dominion_tower_state_pure,
)
from ankiscape.logic.summoning_logic import summon_familiar_pure
from ankiscape.runtime.runtime_actions import RuntimeActionContext, handle_utility_answer


_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _complete(data, *quest_ids):
    quests = dict(data.get("quests") or {})
    for quest_id in quest_ids:
        ids = (
            RECIPE_FOR_DISASTER_SUBQUESTS
            if quest_id == RECIPE_FOR_DISASTER_REQUIREMENT_ID
            else (quest_id,)
        )
        for actual in ids:
            quests[actual] = {
                **(quests.get(actual) or {}),
                "started": True,
                "completed": True,
            }
    data["quests"] = quests
    return data


def _player(*quest_ids, **overrides):
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data["dominion_tower"] = default_dominion_tower_state_pure()
    data.update(
        {
            "attack_level": 99,
            "strength_level": 99,
            "defense_level": 99,
            "constitution_level": 99,
            "magic_level": 99,
            "ranged_level": 99,
            "prayer_level": 99,
            "summoning_level": 99,
            "combat_lifepoints": 990,
        }
    )
    _complete(data, *quest_ids)
    data.update(overrides)
    return data


def _geared(data):
    data["equipment"] = {
        **(data.get("equipment") or {}),
        "weapon": "Dharok's greataxe",
        "body": "Dragon chainbody",
        "legs": "Dragon platelegs",
        "head": "Berserker helm",
        "cape": "Fire cape",
        "neck": "Amulet of strength",
        "feet": "Rune boots",
    }
    data["inventory"] = {**(data.get("inventory") or {}), "Shark": 1_000_000}
    data["combat_supply_loadout"] = {
        **(data.get("combat_supply_loadout") or {}),
        "food": {"Shark": 28},
    }
    return data


# Twenty of the tower's own thirty-eight, chosen because their bosses are the
# cheapest to actually fight. The gate needs twenty and every quest on the list
# unlocks at least one boss, so no legal entrant ever faces a one-boss tower.
WEAK_QUESTS = (
    "demon_slayer",
    "vampyre_slayer",
    "dragon_slayer",
    "wanted",
    "the_chosen_commander",
    "mountain_daughter",
    "the_fremennik_trials",
    "haunted_mine",
    "lost_city",
    "troll_stronghold",
    "shadow_of_the_storm",
    "horror_from_the_deep",
    "fight_arena",
    "holy_grail",
    "a_void_dance",
    "family_crest",
    "between_a_rock",
    "missing_my_mummy",
    "toktz_ket_dill",
    "spirits_of_the_elid",
)


def _twenty_quests():
    """The cheapest legal entry: twenty of the tower's own thirty-eight."""
    assert len(WEAK_QUESTS) == DOMINION_TOWER_QUEST_REQUIREMENT
    assert set(WEAK_QUESTS) <= set(DOMINION_TOWER_QUEST_POOL)
    return WEAK_QUESTS


def _reach_encounter(test, data, rng, encounter_id, *, limit=4000):
    """Keep playing real endurance floors until the tower draws this boss.

    The tower picks the next boss itself, so the only honest way to a specific
    arena is to keep fighting until it comes up.
    """
    for _ in range(limit):
        view = dominion_tower_view_pure(data)
        if view["offer_row"]:
            data, ok, info = apply_dominion_tower_command_pure(
                data, "accept_handicap", {}, rng
            )
            test.assertTrue(ok, info)
            continue
        if not view["active"]:
            if view["dominion_factor"] > 0:
                data, ok, info = apply_dominion_tower_command_pure(
                    data, "claim_rewards", {}, rng
                )
                test.assertTrue(ok, info)
            data, ok, info = apply_dominion_tower_command_pure(
                data, "start_mode", {"mode": "endurance"}, rng
            )
            test.assertTrue(ok, info)
            continue
        if data["dominion_tower"]["encounter_id"] == encounter_id:
            return data
        data["combat_lifepoints"] = 990
        data, ok, result = apply_dominion_tower_review_pure(
            data, rng, equipment_data=EQUIPMENT_DATA
        )
        test.assertTrue(ok, result)
    raise AssertionError(f"the tower never drew {encounter_id}")


def _run_match(test, data, rng, *, limit=600):
    """Take every offered handicap, then review until the match resolves."""
    for _ in range(limit):
        view = dominion_tower_view_pure(data)
        if view["offer_row"]:
            data, ok, info = apply_dominion_tower_command_pure(
                data, "accept_handicap", {}, rng
            )
            test.assertTrue(ok, info)
            continue
        if not view["active"]:
            return data, {}
        data, ok, result = apply_dominion_tower_review_pure(
            data, rng, equipment_data=EQUIPMENT_DATA
        )
        test.assertTrue(ok, result)
        if result.get("won") or result.get("player_died"):
            return data, result
    raise AssertionError("the match never resolved")


class DominionTowerDataTest(unittest.TestCase):
    """The roster and the wheel, exactly as the pinned revision prints them."""

    def test_forty_eight_encounters_split_six_to_a_class(self):
        counts: dict[str, int] = {}
        for row in DOMINION_TOWER_ENCOUNTERS:
            counts[row["class"]] = counts.get(row["class"], 0) + 1
        self.assertEqual(counts, {letter: 6 for letter in "ABCDEFGH"})
        self.assertEqual(len(DOMINION_TOWER_ENCOUNTERS), 48)

    def test_only_class_a_waits_for_floor_six(self):
        self.assertEqual(DOMINION_TOWER_BOSS_CLASS_MIN_FLOOR["A"], 6)
        self.assertEqual(
            {letter for letter, floor in DOMINION_TOWER_BOSS_CLASS_MIN_FLOOR.items() if floor == 1},
            set("BCDEFGH"),
        )

    def test_every_encounter_names_a_real_quest_and_real_npcs(self):
        for row in DOMINION_TOWER_ENCOUNTERS:
            self.assertTrue(row["quest_id"], row["id"])
            self.assertTrue(row["npcs"], row["id"])
            for npc_key in row["npcs"]:
                self.assertIn(npc_key, DOMINION_TOWER_NPCS)

    def test_the_quest_pool_is_the_thirty_eight_the_gate_counts(self):
        self.assertEqual(len(DOMINION_TOWER_QUEST_POOL), 38)
        self.assertEqual(len(set(DOMINION_TOWER_QUEST_POOL)), 38)
        self.assertEqual(DOMINION_TOWER_QUEST_REQUIREMENT, 20)

    def test_the_wheel_holds_twenty_two_handicaps_with_sourced_deltas(self):
        self.assertEqual(DOMINION_TOWER_HANDICAP_COUNT, 22)
        self.assertEqual(len(set(DOMINION_TOWER_HANDICAP_IDS)), 22)
        # Four spot values from the pinned table, top, middle and bottom.
        self.assertEqual(DOMINION_TOWER_HANDICAPS_BY_ID["disease"]["factor_delta"], -70)
        self.assertEqual(DOMINION_TOWER_HANDICAPS_BY_ID["no_prayer"]["factor_delta"], 130)
        self.assertEqual(DOMINION_TOWER_HANDICAPS_BY_ID["life_saver"]["factor_delta"], -200)
        self.assertEqual(
            DOMINION_TOWER_HANDICAPS_BY_ID["no_special_attacks"]["factor_delta"], -100
        )

    def test_a_nudge_lands_on_the_handicap_before_it_and_wraps(self):
        # "If you get Reduced Magic Attack and nudge one position, you get Disease"
        self.assertEqual(_nudged_handicap("reduced_magic_attack"), "disease")
        # "nudging once from Disease goes to No Special Attacks"
        self.assertEqual(_nudged_handicap("disease"), "no_special_attacks")

    def test_the_three_glove_sets_partition_classes_a_b_and_c(self):
        claimed: set[str] = set()
        for row in DOMINION_TOWER_GLOVE_SETS:
            self.assertEqual(len(row["encounters"]), 6)
            classes = [
                DOMINION_TOWER_ENCOUNTERS_BY_ID[encounter_id]["class"]
                for encounter_id in row["encounters"]
            ]
            self.assertEqual(sorted(classes), ["A", "A", "B", "B", "C", "C"])
            claimed |= set(row["encounters"])
        self.assertEqual(
            claimed,
            {
                encounter["id"]
                for encounter in DOMINION_TOWER_ENCOUNTERS
                if encounter["class"] in ("A", "B", "C")
            },
        )

    def test_every_special_match_names_real_npcs_and_real_handicaps(self):
        self.assertEqual(len(DOMINION_TOWER_SPECIAL_MATCHES), 10)
        for row in DOMINION_TOWER_SPECIAL_MATCHES:
            self.assertTrue(row["npcs"], row["id"])
            for npc_key in row["npcs"]:
                self.assertIn(npc_key, DOMINION_TOWER_NPCS)
            for handicap_id in row["handicaps"]:
                self.assertIn(handicap_id, DOMINION_TOWER_HANDICAPS_BY_ID)
            if row["requires_encounter"]:
                self.assertIn(row["requires_encounter"], DOMINION_TOWER_ENCOUNTERS_BY_ID)

    def test_no_encounter_is_worth_zero_dominion_factor(self):
        for row in DOMINION_TOWER_ENCOUNTERS:
            self.assertGreater(
                dominion_tower_encounter_total_level_pure(row["id"]), 0, row["id"]
            )

    def test_the_activity_and_its_items_are_registered(self):
        self.assertIn(DOMINION_TOWER_ACTIVITY_ID, UTILITY_ACTIVITY_DATA)
        item_ids = {
            "Goliath gloves": 22358,
            "Spellcaster gloves": 22366,
            "Swift gloves": 22362,
            "Dreadnip": 22370,
            DOMINION_TOWER_XP_BOOK: 22340,
            DOMINION_TOWER_JOURNAL_PAGE: 22381,
            DOMINION_TOWER_MINE: 22371,
            DOMINION_TOWER_SWORD: 22346,
        }
        for item_name, item_id in item_ids.items():
            self.assertEqual(EXTRA_ITEM_DATA[item_name]["item_id"], item_id)
        for item_name in ("Goliath gloves", "Spellcaster gloves", "Swift gloves"):
            self.assertIn(item_name, EQUIPMENT_DATA)
            self.assertEqual(EQUIPMENT_DATA[item_name].slot, "hands")
            self.assertEqual(
                EQUIPMENT_DATA[item_name].source_item_id, item_ids[item_name]
            )

    def test_every_asset_is_pinned_to_a_pre_cutoff_upload(self):
        with open(os.path.join(_ROOT, "assets_provenance.json"), encoding="utf-8") as handle:
            provenance = json.load(handle)
        for row in DOMINION_TOWER_ASSET_MANIFEST:
            path = str(row["output_path"])
            self.assertTrue(os.path.exists(os.path.join(_ROOT, path)), path)
            self.assertIn(path, provenance)
            stamp = str(provenance[path].get("timestamp", ""))
            self.assertTrue(stamp, path)
            self.assertLess(stamp, "2012-11-20T00:00:00Z", path)

    def test_the_glove_art_is_wired_into_the_item_images(self):
        for item_name in ("Goliath gloves", "Spellcaster gloves", "Swift gloves"):
            self.assertIn(item_name, EXTRA_ITEM_IMAGES)


class DominionTowerGateTest(unittest.TestCase):
    """The 110-combat gate, the twenty-quest gate, and the Strange face."""

    def test_a_low_level_player_is_refused_by_both_gates(self):
        data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        data["dominion_tower"] = default_dominion_tower_state_pure()
        view = dominion_tower_view_pure(data)
        self.assertFalse(view["requirements_met"])
        self.assertIn(
            f"Combat level {DOMINION_TOWER_COMBAT_LEVEL_REQUIREMENT} (you are 3)",
            view["entry_reasons"],
        )
        self.assertIn(
            "20 of the tower's 38 quests (0 complete)", view["entry_reasons"]
        )
        _updated, ok, info = apply_dominion_tower_command_pure(
            data, "talk_to_face", {}, random.random
        )
        self.assertFalse(ok)
        self.assertIn("110 combat", info["reason"])

    def test_nineteen_quests_are_one_short(self):
        data = _player(*DOMINION_TOWER_QUEST_POOL[:19])
        view = dominion_tower_view_pure(data)
        self.assertEqual(view["completed_quests"], 19)
        self.assertIn(
            "20 of the tower's 38 quests (19 complete)", view["entry_reasons"]
        )

    def test_recipe_for_disaster_counts_only_when_every_subquest_is_done(self):
        data = _player()
        _complete(data, *RECIPE_FOR_DISASTER_SUBQUESTS[:-1])
        self.assertNotIn(
            RECIPE_FOR_DISASTER_REQUIREMENT_ID, dominion_tower_completed_quests_pure(data)
        )
        _complete(data, RECIPE_FOR_DISASTER_SUBQUESTS[-1])
        self.assertIn(
            RECIPE_FOR_DISASTER_REQUIREMENT_ID, dominion_tower_completed_quests_pure(data)
        )

    def test_the_face_must_be_met_before_any_mode_opens(self):
        data = _player(*_twenty_quests())
        view = dominion_tower_view_pure(data)
        self.assertEqual(view["entry_reasons"], ("Talk to the Strange face",))
        _updated, ok, info = apply_dominion_tower_command_pure(
            data, "start_mode", {"mode": "climber"}, random.random
        )
        self.assertFalse(ok)
        self.assertIn("Strange face", info["reason"])
        data, ok, info = apply_dominion_tower_command_pure(
            data, "talk_to_face", {}, random.random
        )
        self.assertTrue(ok, info)
        self.assertEqual(dominion_tower_view_pure(data)["entry_reasons"], ())

    def test_only_bosses_of_completed_quests_appear(self):
        data = _player("demon_slayer")
        self.assertEqual(
            dominion_tower_available_encounters_pure(data, 1), ("delrith",)
        )
        _complete(data, "dragon_slayer")
        self.assertEqual(
            sorted(dominion_tower_available_encounters_pure(data, 1)),
            ["delrith", "elvarg", "melzar_the_mad"],
        )

    def test_class_a_bosses_stay_shut_until_floor_six(self):
        data = _player("nomads_requiem")
        self.assertEqual(dominion_tower_available_encounters_pure(data, 5), ())
        self.assertEqual(
            sorted(dominion_tower_available_encounters_pure(data, 6)),
            ["decaying_avatar", "nomad"],
        )


class DominionTowerFactorTest(unittest.TestCase):
    """Darkan's product, the wheel's deltas, and the two endurance rules."""

    def _state(self, **overrides):
        state = default_dominion_tower_state_pure()
        state.update(overrides)
        return state

    def test_climber_pays_a_hundred_times_the_arena_level_total(self):
        state = self._state(mode="climber", encounter_id="delrith")
        self.assertEqual(dominion_tower_round_factor_pure(state), 27 * 100)

    def test_endurance_pays_a_tenth_of_that(self):
        state = self._state(mode="endurance", encounter_id="delrith")
        self.assertEqual(dominion_tower_round_factor_pure(state), 27 * 10)

    def test_the_wheel_deltas_are_added_to_the_round(self):
        state = self._state(
            mode="climber", encounter_id="delrith", handicaps=["no_prayer", "life_saver"]
        )
        self.assertEqual(dominion_tower_round_factor_pure(state), 2700 + 130 - 200)

    def test_endurance_halves_again_past_floor_thirty(self):
        state = self._state(mode="endurance", encounter_id="delrith", progress=30)
        self.assertEqual(dominion_tower_round_factor_pure(state), 27 * 10 // 2)

    def test_freestyle_pays_nothing(self):
        state = self._state(mode="freestyle", encounter_id="delrith")
        self.assertEqual(dominion_tower_round_factor_pure(state), 0)

    def test_a_multi_npc_arena_sums_every_combatant(self):
        # The Pest Queen arena is the queen plus four drones.
        self.assertEqual(
            dominion_tower_encounter_total_level_pure("pest_queen"),
            DOMINION_TOWER_NPCS["pest_queen"]["level"]
            + 4 * DOMINION_TOWER_NPCS["pest_drone"]["level"],
        )


class DominionTowerHandicapTest(unittest.TestCase):
    """The spinner is mandatory, respinnable, nudgeable, and it bites."""

    def _entered(self, rng=None):
        rng = rng or random.Random(3).random
        data = _geared(_player(*_twenty_quests()))
        data, ok, info = apply_dominion_tower_command_pure(data, "talk_to_face", {}, rng)
        self.assertTrue(ok, info)
        data, ok, info = apply_dominion_tower_command_pure(
            data, "start_mode", {"mode": "climber"}, rng
        )
        self.assertTrue(ok, info)
        return data, rng

    def test_the_doors_will_not_open_until_the_spinner_is_answered(self):
        data, rng = self._entered()
        view = dominion_tower_view_pure(data)
        self.assertTrue(view["offer_row"])
        self.assertFalse(dominion_tower_can_review_pure(data))
        _updated, ok, info = apply_dominion_tower_review_pure(
            data, rng, equipment_data=EQUIPMENT_DATA
        )
        self.assertFalse(ok)
        self.assertIn("handicap", info["reason"])
        data, ok, info = apply_dominion_tower_command_pure(
            data, "accept_handicap", {}, rng
        )
        self.assertTrue(ok, info)
        self.assertTrue(dominion_tower_can_review_pure(data))

    def test_a_nudge_moves_the_spinner_one_place_and_the_limit_holds(self):
        data, rng = self._entered()
        before = dominion_tower_view_pure(data)["offer_row"]["id"]
        data, ok, _info = apply_dominion_tower_command_pure(data, "nudge_handicap", {}, rng)
        self.assertTrue(ok)
        self.assertEqual(
            dominion_tower_view_pure(data)["offer_row"]["id"], _nudged_handicap(before)
        )
        for _ in range(2):
            data, ok, _info = apply_dominion_tower_command_pure(
                data, "nudge_handicap", {}, rng
            )
            self.assertTrue(ok)
        _updated, ok, info = apply_dominion_tower_command_pure(
            data, "nudge_handicap", {}, rng
        )
        self.assertFalse(ok)
        self.assertIn("nudge further", info["reason"])

    def test_the_respin_is_allowed_once(self):
        data, rng = self._entered()
        data, ok, _info = apply_dominion_tower_command_pure(data, "respin_handicap", {}, rng)
        self.assertTrue(ok)
        _updated, ok, info = apply_dominion_tower_command_pure(
            data, "respin_handicap", {}, rng
        )
        self.assertFalse(ok)
        self.assertIn("already respun", info["reason"])

    def _forced(self, handicap_id):
        """Enter climber and take exactly the handicap under test."""
        rng = random.Random(11).random
        data = _geared(_player(*_twenty_quests()))
        data, ok, info = apply_dominion_tower_command_pure(data, "talk_to_face", {}, rng)
        self.assertTrue(ok, info)
        data, ok, info = apply_dominion_tower_command_pure(
            data, "start_mode", {"mode": "climber"}, rng
        )
        self.assertTrue(ok, info)
        state = dict(data["dominion_tower"])
        state["offer"] = {"handicap_id": handicap_id, "respins_used": 0, "nudges_used": 0}
        data["dominion_tower"] = state
        data, ok, info = apply_dominion_tower_command_pure(data, "accept_handicap", {}, rng)
        self.assertTrue(ok, info)
        return data, rng

    def test_poison_actually_poisons_at_the_stated_ninety_eight(self):
        data, _rng = self._forced("poison")
        effects = data.get("combat_status_effects") or {}
        self.assertIn("poison", effects)

    def test_halved_life_points_halves_the_bar(self):
        data, _rng = self._forced("halved_life_points")
        self.assertLessEqual(data["combat_lifepoints"], 495)

    def test_disease_drains_one_skill_by_fourteen(self):
        data, _rng = self._forced("disease")
        currents = data.get("combat_current_levels") or {}
        drained = {
            skill: level for skill, level in currents.items() if int(level) < 99
        }
        self.assertEqual(
            len(drained), 1, data.get("dominion_tower", {}).get("last_result")
        )
        self.assertEqual(list(drained.values())[0], 85)

    def test_monster_stun_silences_the_arena_for_the_stated_ten_seconds(self):
        data, rng = self._forced("monster_stun")
        self.assertEqual(data["dominion_tower"]["match"]["stun_ticks"], 16)
        before = data["combat_lifepoints"]
        data, ok, _result = apply_dominion_tower_review_pure(
            data, rng, equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok)
        self.assertEqual(data["combat_lifepoints"], before)

    def test_no_prayer_switches_the_prayers_off_for_the_slice(self):
        data, rng = self._forced("no_prayer")
        data["combat_selected_prayers"] = ["protect_from_melee"]
        data["combat_prayer_uptime"] = "always"
        data, ok, result = apply_dominion_tower_review_pure(
            data, rng, equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok)
        self.assertEqual(result["prayer_uptime"], 0.0)

    def test_no_familiar_dismisses_and_blocks_summoning_during_the_match(self):
        rng = random.Random(11).random
        data = _geared(_player(*_twenty_quests()))
        data["summoning_state"]["summoning_points_current"] = 99
        data["inventory"] = {**data["inventory"], "Spirit wolf pouch": 2}
        data, ok, info = summon_familiar_pure(data, "spiritwolf")
        self.assertTrue(ok, info)
        expected_points = data["summoning_state"]["summoning_points_current"]
        data, ok, info = apply_dominion_tower_command_pure(data, "talk_to_face", {}, rng)
        self.assertTrue(ok, info)
        state = dict(data["dominion_tower"])
        state["defeated"] = {"delrith": 1}
        data["dominion_tower"] = state
        data, ok, info = apply_dominion_tower_command_pure(
            data,
            "start_mode",
            {"mode": "freestyle", "encounter_id": "delrith", "handicaps": ["no_familiar"]},
            rng,
        )
        self.assertTrue(ok, info)
        self.assertEqual(data["summoning_state"]["active_follower"], {})
        pouch_count = data["inventory"]["Spirit wolf pouch"]
        blocked, ok, info = summon_familiar_pure(data, "spiritwolf")
        self.assertFalse(ok, info)
        self.assertEqual(blocked["inventory"]["Spirit wolf pouch"], pouch_count)
        self.assertEqual(blocked["summoning_state"]["active_follower"], {})
        data, ok, result = apply_dominion_tower_review_pure(
            data, rng, equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, result)
        self.assertEqual(data["summoning_state"]["active_follower"], {})
        for _ in range(20):
            if not data["dominion_tower"]["mode"]:
                break
            data, ok, result = apply_dominion_tower_review_pure(
                data, lambda: 0.1, equipment_data=EQUIPMENT_DATA
            )
            self.assertTrue(ok, result)
        self.assertFalse(data["dominion_tower"]["mode"])
        self.assertEqual(
            data["summoning_state"]["summoning_points_current"], expected_points
        )

    def test_removed_armour_is_banked_instead_of_deleted(self):
        cases = (
            ("no_body_armour", "body", "Dragon chainbody"),
            ("no_shield", "shield", "Rune kiteshield"),
        )
        for handicap_id, slot, item_name in cases:
            with self.subTest(handicap=handicap_id):
                data, rng = self._forced(handicap_id)
                data["equipment"] = {
                    **data["equipment"],
                    "weapon": "Abyssal whip",
                    slot: item_name,
                }
                before = int(data["inventory"].get(item_name, 0))
                data, ok, result = apply_dominion_tower_review_pure(
                    data, rng, equipment_data=EQUIPMENT_DATA
                )
                self.assertTrue(ok, result)
                self.assertNotIn(slot, data["equipment"])
                self.assertEqual(int(data["inventory"].get(item_name, 0)), before + 1)

    def test_no_food_restores_auto_eat_and_the_food_loadout_after_the_slice(self):
        data, rng = self._forced("no_food")
        expected_loadout = copy.deepcopy(data["combat_supply_loadout"])
        data["combat_auto_eat_food"] = "Shark"
        data, ok, result = apply_dominion_tower_review_pure(
            data, rng, equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, result)
        self.assertEqual(data["combat_auto_eat_food"], "Shark")
        self.assertEqual(data["combat_supply_loadout"], expected_loadout)

    def test_every_accepted_handicap_joins_the_suffered_set_forever(self):
        data, _rng = self._forced("no_food")
        self.assertIn("no_food", data["dominion_tower"]["suffered_handicaps"])
        state = sanitize_dominion_tower_state_pure(
            {**data["dominion_tower"], "mode": "", "roster": []}
        )
        self.assertIn("no_food", state["suffered_handicaps"])


class DominionTowerRunTest(unittest.TestCase):
    """A real climber run: wins, floors, factor, defeat, and the reward box."""

    def _entered(self, *quests, mode="climber", seed=5):  # noqa: D401
        rng = random.Random(seed).random
        data = _geared(_player(*quests, *_twenty_quests()))
        data, ok, info = apply_dominion_tower_command_pure(data, "talk_to_face", {}, rng)
        self.assertTrue(ok, info)
        data, ok, info = apply_dominion_tower_command_pure(
            data, "start_mode", {"mode": mode}, rng
        )
        self.assertTrue(ok, info)
        return data, rng

    def test_a_win_pays_factor_advances_the_floor_and_picks_a_new_boss(self):
        data, rng = self._entered()
        first = dominion_tower_view_pure(data)["encounter_name"]
        self.assertTrue(first)
        data, result = _run_match(self, data, rng)
        self.assertTrue(result.get("won"), result)
        view = dominion_tower_view_pure(data)
        self.assertEqual(view["progress"], 1)
        self.assertEqual(view["boss_kills"], 1)
        self.assertGreater(view["dominion_factor"], 0)
        self.assertEqual(view["max_floor_climber"], 1)
        self.assertTrue(view["active"])
        self.assertEqual(view["floor"], 2)
        self.assertEqual(
            view["dominion_factor"], result["factor"]
        )

    def test_a_live_match_cannot_be_left_before_victory_or_defeat(self):
        rng = random.Random(5).random
        data = _geared(_player(*_twenty_quests()))
        state = dict(data["dominion_tower"])
        state["defeated"] = {"delrith": 1}
        data["dominion_tower"] = state
        data, ok, info = apply_dominion_tower_command_pure(data, "talk_to_face", {}, rng)
        self.assertTrue(ok, info)
        data, ok, info = apply_dominion_tower_command_pure(
            data,
            "start_mode",
            {"mode": "freestyle", "encounter_id": "delrith"},
            rng,
        )
        self.assertTrue(ok, info)
        roster_before = len(data["dominion_tower"]["roster"])
        updated, ok, info = apply_dominion_tower_command_pure(data, "leave", {}, rng)
        self.assertFalse(ok)
        self.assertIn("victory or defeat", info["reason"])
        self.assertEqual(len(updated["dominion_tower"]["roster"]), roster_before)
        self.assertEqual(updated["activity_session"]["active_id"], DOMINION_TOWER_ACTIVITY_ID)

    def test_a_defeat_ends_the_run_and_costs_the_last_round(self):
        """A stripped fighter against a heavy boss loses, safely, and pays."""
        data, rng = self._entered(mode="endurance", seed=17)
        data = _reach_encounter(self, data, rng, "toktz_ket_dill", limit=900)
        banked = dominion_tower_view_pure(data)["dominion_factor"]
        self.assertGreater(banked, 0)
        last_round = int(data["dominion_tower"]["last_round_factor"])
        data["equipment"] = {}
        data["combat_supply_loadout"] = {}
        data["inventory"] = {}
        data["combat_lifepoints"] = 20
        data, result = _run_match(self, data, rng, limit=900)
        self.assertTrue(result.get("player_died"), result)
        view = dominion_tower_view_pure(data)
        self.assertFalse(view["active"])
        self.assertEqual(view["mode"], "")
        self.assertEqual(view["dominion_factor"], banked - last_round)
        # The tower is a safe minigame, so nothing was lost with the run.
        self.assertNotIn("combat_grave", result)

    def test_a_multi_npc_arena_empties_one_body_at_a_time(self):
        data, rng = self._entered(mode="endurance", seed=15)
        data = _reach_encounter(self, data, rng, "golems")
        view = dominion_tower_view_pure(data)
        self.assertEqual(len(view["roster_names"]), 3)
        seen = {len(view["roster_names"])}
        for _ in range(400):
            view = dominion_tower_view_pure(data)
            if view["offer_row"]:
                data, ok, info = apply_dominion_tower_command_pure(
                    data, "accept_handicap", {}, rng
                )
                self.assertTrue(ok, info)
                continue
            data, ok, result = apply_dominion_tower_review_pure(
                data, rng, equipment_data=EQUIPMENT_DATA
            )
            self.assertTrue(ok, result)
            if result.get("won") or result.get("player_died"):
                break
            seen.add(len(dominion_tower_view_pure(data)["roster_names"]))
        self.assertEqual(seen, {3, 2, 1})

    def test_the_pest_queen_drones_heal_her_until_they_are_killed(self):
        """Class A waits for floor six, and the drones keep the queen alive."""
        data, rng = self._entered("the_void_stares_back", mode="endurance", seed=9)
        self.assertNotIn(
            "pest_queen", dominion_tower_available_encounters_pure(data, 5)
        )
        self.assertIn("pest_queen", dominion_tower_available_encounters_pure(data, 6))
        data = _reach_encounter(self, data, rng, "pest_queen", limit=900)
        view = dominion_tower_view_pure(data)
        self.assertEqual(len(view["roster_names"]), 5)
        self.assertEqual(view["roster_names"].count("Pest drone"), 4)
        healed = 0
        for _ in range(40):
            data["combat_lifepoints"] = 990
            data, ok, result = apply_dominion_tower_review_pure(
                data, rng, equipment_data=EQUIPMENT_DATA
            )
            self.assertTrue(ok, result)
            healed += int(result.get("roster_healing", 0) or 0)
            if healed:
                break
        self.assertGreater(healed, 0)

    def test_the_reward_box_pays_a_book_and_resets_the_factor(self):
        data, rng = self._entered()
        data, result = _run_match(self, data, rng)
        self.assertTrue(result.get("won"))
        data, ok, info = apply_dominion_tower_command_pure(data, "leave", {}, rng)
        self.assertTrue(ok, info)
        banked = dominion_tower_view_pure(data)["dominion_factor"]
        self.assertGreater(banked, 0)
        data, ok, info = apply_dominion_tower_command_pure(data, "claim_rewards", {}, rng)
        self.assertTrue(ok, info)
        self.assertEqual(info["factor"], banked)
        self.assertGreaterEqual(int(data["inventory"].get(DOMINION_TOWER_XP_BOOK, 0)), 1)
        self.assertEqual(dominion_tower_view_pure(data)["dominion_factor"], 0)
        self.assertEqual(dominion_tower_view_pure(data)["progress"], 0)

    def test_the_reward_box_caps_repeated_capped_item_rolls_per_box(self):
        data, rng = self._entered()
        data, result = _run_match(self, data, rng)
        self.assertTrue(result.get("won"), result)
        data, ok, info = apply_dominion_tower_command_pure(data, "leave", {}, rng)
        self.assertTrue(ok, info)
        blood_rune_roll = lambda: 5.2 / 14
        data, ok, info = apply_dominion_tower_command_pure(
            data, "claim_rewards", {}, blood_rune_roll
        )
        self.assertTrue(ok, info)
        self.assertEqual(info["granted"]["Blood rune"], 20)
        self.assertEqual(int(data["inventory"].get("Blood rune", 0)), 20)

    def test_an_empty_factor_cannot_be_claimed(self):
        rng = random.Random(5).random
        data = _geared(_player(*_twenty_quests()))
        data, ok, info = apply_dominion_tower_command_pure(data, "talk_to_face", {}, rng)
        self.assertTrue(ok, info)
        _updated, ok, info = apply_dominion_tower_command_pure(
            data, "claim_rewards", {}, rng
        )
        self.assertFalse(ok)
        self.assertIn("no dominion factor", info["reason"])

    def test_the_xp_book_needs_level_seventy_five_and_pays_the_stated_ratios(self):
        data, rng = self._entered()
        data, _result = _run_match(self, data, rng)
        data, ok, _info = apply_dominion_tower_command_pure(data, "leave", {}, rng)
        self.assertTrue(ok)
        data, ok, _info = apply_dominion_tower_command_pure(data, "claim_rewards", {}, rng)
        self.assertTrue(ok)
        factor = data["dominion_tower"]["xp_book_factors"][0]
        data["prayer_level"] = 70
        _updated, ok, info = apply_dominion_tower_command_pure(
            data, "read_xp_book", {"skill": "prayer"}, rng
        )
        self.assertFalse(ok)
        self.assertIn("level 75", info["reason"])
        before = float(data.get("attack_exp", 0.0))
        data, ok, info = apply_dominion_tower_command_pure(
            data, "read_xp_book", {"skill": "attack"}, rng
        )
        self.assertTrue(ok, info)
        self.assertAlmostEqual(
            float(data["attack_exp"]) - before,
            dominion_tower_xp_book_amount_pure(factor, "attack"),
            places=1,
        )
        # Magic and Ranged pay strictly less than melee at the same factor.
        self.assertLess(
            dominion_tower_xp_book_amount_pure(factor, "magic"),
            dominion_tower_xp_book_amount_pure(factor, "attack"),
        )
        self.assertLess(
            dominion_tower_xp_book_amount_pure(factor, "prayer"),
            dominion_tower_xp_book_amount_pure(factor, "ranged"),
        )

    def test_freestyle_pays_no_factor_and_counts_no_boss_kill(self):
        data, rng = self._entered()
        data, _result = _run_match(self, data, rng)
        data, ok, info = apply_dominion_tower_command_pure(data, "leave", {}, rng)
        self.assertTrue(ok, info)
        beaten = next(iter(data["dominion_tower"]["defeated"]))
        kills_before = dominion_tower_view_pure(data)["boss_kills"]
        factor_before = dominion_tower_view_pure(data)["dominion_factor"]
        data, ok, info = apply_dominion_tower_command_pure(
            data,
            "start_mode",
            {"mode": "freestyle", "encounter_id": beaten},
            rng,
        )
        self.assertTrue(ok, info)
        data, result = _run_match(self, data, rng)
        self.assertTrue(result.get("won"), result)
        view = dominion_tower_view_pure(data)
        self.assertEqual(view["boss_kills"], kills_before)
        self.assertEqual(view["dominion_factor"], factor_before)
        self.assertGreater(sum(result.get("xp_rewards", {}).values()), 0.0)

    def test_freestyle_refuses_a_boss_that_was_never_beaten(self):
        rng = random.Random(5).random
        data = _geared(_player(*_twenty_quests()))
        data, ok, info = apply_dominion_tower_command_pure(data, "talk_to_face", {}, rng)
        self.assertTrue(ok, info)
        _updated, ok, info = apply_dominion_tower_command_pure(
            data, "start_mode", {"mode": "freestyle", "encounter_id": "nomad"}, rng
        )
        self.assertFalse(ok)
        self.assertIn("Defeat a boss", info["reason"])

    def test_special_mode_waits_for_climber_exposure(self):
        rng = random.Random(5).random
        data = _geared(_player(*_twenty_quests()))
        data, ok, info = apply_dominion_tower_command_pure(data, "talk_to_face", {}, rng)
        self.assertTrue(ok, info)
        _updated, ok, info = apply_dominion_tower_command_pure(
            data, "start_mode", {"mode": "special", "special_id": "just_die_already"}, rng
        )
        self.assertFalse(ok)
        self.assertIn("Climber mode first", info["reason"])

    def test_the_easy_sunfreet_match_waives_the_combat_gate(self):
        rng = random.Random(4).random
        data = _geared(_player(*_twenty_quests()))
        data["dominion_tower"] = {**data["dominion_tower"], "talked_with_face": True}
        for level in ("attack", "strength", "defense", "ranged", "magic"):
            data[f"{level}_level"] = 3
        data["constitution_level"] = 10
        data["prayer_level"] = 1
        data["summoning_level"] = 1
        self.assertLess(
            dominion_tower_view_pure(data)["entry_reasons"].__len__(), 3
        )
        data, ok, info = apply_dominion_tower_command_pure(
            data,
            "start_mode",
            {"mode": "special", "special_id": "the_fire_it_burns_easy"},
            rng,
        )
        self.assertTrue(ok, info)
        self.assertEqual(dominion_tower_view_pure(data)["roster_names"], ("Sunfreet",))


class DominionTowerRewardLadderTest(unittest.TestCase):
    """Every reward, reached by killing the bosses its unlock condition names."""

    @classmethod
    def setUpClass(cls):
        """One long, real endurance grind shared by the reward assertions.

        Nothing here is stubbed. Delrith is the only boss the player has
        unlocked, so every endurance floor is a Delrith fight, and the run is
        replayed until the boss-kill counter passes the five hundred the glove,
        dreadnip, mine and Ascendancy-mine unlocks all read.
        """
        rng = random.Random(21).random
        data = _geared(_player(*_twenty_quests()))
        data, ok, info = apply_dominion_tower_command_pure(data, "talk_to_face", {}, rng)
        assert ok, info
        kills = 0
        guard = 0
        while kills < 505 and guard < 12000:
            guard += 1
            view = dominion_tower_view_pure(data)
            if not view["active"]:
                data, ok, info = apply_dominion_tower_command_pure(
                    data, "start_mode", {"mode": "endurance"}, rng
                )
                assert ok, info
                continue
            data, ok, result = apply_dominion_tower_review_pure(
                data, rng, equipment_data=EQUIPMENT_DATA
            )
            assert ok, result
            if result.get("player_died"):
                data["combat_lifepoints"] = 990
            kills = dominion_tower_view_pure(data)["boss_kills"]
        assert kills >= 505, kills
        cls.ground = data
        cls.rng = rng

    def setUp(self):
        self.data = copy.deepcopy(self.ground)

    def test_the_grind_really_happened_through_the_review_handler(self):
        view = dominion_tower_view_pure(self.data)
        self.assertGreaterEqual(view["boss_kills"], 505)
        self.assertGreaterEqual(view["max_floor_endurance"], 1)
        self.assertGreater(int(self.data["dominion_tower"]["total_score"]), 0)

    def test_the_marker_climbs_its_three_kill_stages(self):
        self.assertEqual(dominion_tower_view_pure(self.data)["marker_stage"], 3)
        self.assertEqual(dominion_tower_view_pure(self.data)["marker_boost"], 8)

    def test_reward_credits_wait_for_an_unlock_then_accrue(self):
        data = self.data
        # Five hundred kills alone unlock nothing that spends a credit.
        self.assertEqual(dominion_tower_view_pure(data)["reward_credits"], 0)
        data, ok, info = apply_dominion_tower_command_pure(data, "spectate", {}, self.rng)
        self.assertTrue(ok, info)
        view = dominion_tower_view_pure(data)
        self.assertEqual(view["reward_credits"], 1)
        self.assertLessEqual(view["reward_credits"], DOMINION_TOWER_REWARD_CREDIT_CAP)

    def test_the_dreadnip_needs_the_spectate_as_well_as_the_kills(self):
        data = self.data
        self.assertNotIn("dreadnip", dominion_tower_view_pure(data)["unlocked_rewards"])
        _updated, ok, info = apply_dominion_tower_command_pure(
            data, "claim_reward", {"reward_id": "dreadnip"}, self.rng
        )
        self.assertFalse(ok)
        self.assertIn("locked", info["reason"])
        data, ok, info = apply_dominion_tower_command_pure(data, "spectate", {}, self.rng)
        self.assertTrue(ok, info)
        self.assertIn("dreadnip", dominion_tower_view_pure(data)["unlocked_rewards"])
        credits_before = dominion_tower_view_pure(data)["reward_credits"]
        data, ok, info = apply_dominion_tower_command_pure(
            data, "claim_reward", {"reward_id": "dreadnip"}, self.rng
        )
        self.assertTrue(ok, info)
        self.assertEqual(int(data["inventory"].get("Dreadnip", 0)), 100)
        self.assertEqual(EXTRA_ITEM_DATA[info["item_name"]]["item_id"], 22370)
        view = dominion_tower_view_pure(data)
        self.assertEqual(view["reward_credits"], credits_before - 1)
        dreadnip_row = next(
            row for row in view["claim_reward_rows"] if row["id"] == "dreadnip"
        )
        self.assertFalse(dreadnip_row["ready"])

    def test_the_ascendancy_mines_arrive_ten_at_a_time_and_repeat(self):
        data = self.data
        data, ok, info = apply_dominion_tower_command_pure(
            data, "claim_reward", {"reward_id": "ascendancy_mines"}, self.rng
        )
        self.assertTrue(ok, info)
        self.assertEqual(int(data["inventory"].get("Ascendancy mine", 0)), 10)
        self.assertFalse(dominion_tower_view_pure(data)["ascendancy_ready"])
        _updated, ok, info = apply_dominion_tower_command_pure(
            data, "claim_reward", {"reward_id": "ascendancy_mines"}, self.rng
        )
        self.assertFalse(ok)
        self.assertIn("1,000", info["reason"])

    def test_the_mines_need_every_special_match_and_then_cost_coins(self):
        data = self.data
        self.assertNotIn("mines", dominion_tower_view_pure(data)["unlocked_rewards"])
        _updated, ok, info = apply_dominion_tower_command_pure(
            data, "buy_mines", {"quantity": 10}, self.rng
        )
        self.assertFalse(ok)
        self.assertIn("special match", info["reason"])
        state = dict(data["dominion_tower"])
        state["specials_done"] = [
            row["id"]
            for row in DOMINION_TOWER_SPECIAL_MATCHES
            if not row["npcs"][0].startswith("sunfreet")
        ]
        data["dominion_tower"] = state
        self.assertIn("mines", dominion_tower_view_pure(data)["unlocked_rewards"])
        data["inventory"] = {**data["inventory"], "Coins": DOMINION_TOWER_MINE_COST * 10}
        data, ok, info = apply_dominion_tower_command_pure(
            data, "buy_mines", {"quantity": 10}, self.rng
        )
        self.assertTrue(ok, info)
        self.assertEqual(int(data["inventory"].get(DOMINION_TOWER_MINE, 0)), 10)
        self.assertEqual(int(data["inventory"].get("Coins", 0)), 0)

    def test_the_gloves_need_their_own_six_bosses_on_top_of_the_five_hundred(self):
        data = self.data
        view = dominion_tower_view_pure(data)
        self.assertEqual(view["claimable_gloves"], ())
        _updated, ok, info = apply_dominion_tower_command_pure(
            data, "claim_reward", {"reward_id": "goliath_gloves"}, self.rng
        )
        self.assertFalse(ok)
        self.assertIn("locked", info["reason"])

    def test_beating_set_one_makes_the_goliath_gloves_claimable(self):
        """The six set-one bosses are beaten for real, then the gloves claimed."""
        data = copy.deepcopy(self.ground)
        rng = random.Random(33).random
        set_one = next(row for row in DOMINION_TOWER_GLOVE_SETS if row["id"] == "set_1")
        for encounter_id in set_one["encounters"]:
            _complete(data, DOMINION_TOWER_ENCOUNTERS_BY_ID[encounter_id]["quest_id"])
        for encounter_id in set_one["encounters"]:
            for _ in range(20):
                if int((data["dominion_tower"]["defeated"] or {}).get(encounter_id, 0)):
                    break
                data = _reach_encounter(self, data, rng, encounter_id, limit=12000)
                # Nomad is a ten-thousand-lifepoint fight; keep the fighter fed
                # the way the tower's own bank chest would between floors.
                for _ in range(400):
                    data["combat_lifepoints"] = max(
                        1, int(data.get("combat_lifepoints", 1))
                    )
                    data["combat_supply_loadout"] = {
                        **(data.get("combat_supply_loadout") or {}),
                        "food": {"Shark": 28},
                    }
                    if not dominion_tower_view_pure(data)["active"]:
                        break
                    view = dominion_tower_view_pure(data)
                    if view["offer_row"]:
                        data, ok, info = apply_dominion_tower_command_pure(
                            data, "accept_handicap", {}, rng
                        )
                        self.assertTrue(ok, info)
                        continue
                    data, ok, result = apply_dominion_tower_review_pure(
                        data, rng, equipment_data=EQUIPMENT_DATA
                    )
                    self.assertTrue(ok, result)
                    if result.get("won") or result.get("player_died"):
                        break
            self.assertGreater(
                int((data["dominion_tower"]["defeated"] or {}).get(encounter_id, 0)),
                0,
                encounter_id,
            )
        view = dominion_tower_view_pure(data)
        self.assertIn("Goliath gloves", view["claimable_gloves"])
        self.assertIn("goliath_gloves", view["unlocked_rewards"])
        data, ok, info = apply_dominion_tower_command_pure(
            data, "claim_reward", {"reward_id": "goliath_gloves"}, rng
        )
        self.assertTrue(ok, info)
        self.assertEqual(int(data["inventory"].get("Goliath gloves", 0)), 1)
        self.assertEqual(EQUIPMENT_DATA["Goliath gloves"].bonuses.melee_strength, 13)


class DominionTowerPowerupTest(unittest.TestCase):
    """Journal pages, bombs, the horn, the potions, and the tower weapons."""

    def _in_arena(self):
        rng = random.Random(13).random
        data = _geared(_player(*_twenty_quests()))
        data, ok, info = apply_dominion_tower_command_pure(data, "talk_to_face", {}, rng)
        self.assertTrue(ok, info)
        data, ok, info = apply_dominion_tower_command_pure(
            data, "start_mode", {"mode": "endurance"}, rng
        )
        self.assertTrue(ok, info)
        return data, rng

    def _freestyle_nomad(self):
        rng = random.Random(13).random
        data = _geared(_player(*_twenty_quests()))
        state = dict(data["dominion_tower"])
        state["defeated"] = {"nomad": 1}
        data["dominion_tower"] = state
        data, ok, info = apply_dominion_tower_command_pure(data, "talk_to_face", {}, rng)
        self.assertTrue(ok, info)
        data, ok, info = apply_dominion_tower_command_pure(
            data, "start_mode", {"mode": "freestyle", "encounter_id": "nomad"}, rng
        )
        self.assertTrue(ok, info)
        return data, rng

    def test_a_bomb_takes_the_stated_share_of_the_target(self):
        data, rng = self._in_arena()
        data["inventory"] = {**data["inventory"], "Diminutive bomb": 1}
        before = dominion_tower_view_pure(data)["engaged_lifepoints"]
        data, ok, info = apply_dominion_tower_command_pure(
            data, "use_powerup", {"item": "Diminutive bomb"}, rng
        )
        self.assertTrue(ok, info)
        after = dominion_tower_view_pure(data)["engaged_lifepoints"]
        self.assertEqual(before - after, max(1, before // 10))
        self.assertEqual(int(data["inventory"].get("Diminutive bomb", 0)), 0)

    def test_only_four_bombs_land_in_one_match(self):
        data, rng = self._in_arena()
        data["inventory"] = {**data["inventory"], "Massive bomb": 10}
        for _ in range(4):
            data, ok, info = apply_dominion_tower_command_pure(
                data, "use_powerup", {"item": "Massive bomb"}, rng
            )
            self.assertTrue(ok, info)
        _updated, ok, info = apply_dominion_tower_command_pure(
            data, "use_powerup", {"item": "Massive bomb"}, rng
        )
        self.assertFalse(ok)
        self.assertIn("4 bombs", info["reason"])

    def test_the_horn_spawns_scorpion_meat_and_the_meat_heals_two_twenty(self):
        data, rng = self._in_arena()
        state = dict(data["dominion_tower"])
        state["help_horn_charges"] = 5
        data["dominion_tower"] = state
        data, ok, info = apply_dominion_tower_command_pure(
            data, "use_powerup", {"item": "Help horn"}, rng
        )
        self.assertTrue(ok, info)
        self.assertEqual(int(data["inventory"].get("Scorpion meat", 0)), 1)
        self.assertEqual(data["dominion_tower"]["help_horn_charges"], 4)
        data["combat_lifepoints"] = 400
        data, ok, info = apply_dominion_tower_command_pure(
            data, "eat_scorpion_meat", {}, rng
        )
        self.assertTrue(ok, info)
        self.assertEqual(data["combat_lifepoints"], 620)

    def test_scorpion_meat_will_not_be_eaten_outside_the_tower(self):
        data = _player(*_twenty_quests())
        data["inventory"] = {**data["inventory"], "Scorpion meat": 1}
        _updated, ok, info = apply_dominion_tower_command_pure(
            data, "eat_scorpion_meat", {}, random.random
        )
        self.assertFalse(ok)
        self.assertIn("Dominion Tower", info["reason"])

    def test_the_no_powerups_handicap_blocks_every_power_up(self):
        data, rng = self._in_arena()
        state = dict(data["dominion_tower"])
        state["handicaps"] = ["no_powerups"]
        data["dominion_tower"] = state
        data["inventory"] = {**data["inventory"], "Colossal bomb": 1}
        _updated, ok, info = apply_dominion_tower_command_pure(
            data, "use_powerup", {"item": "Colossal bomb"}, rng
        )
        self.assertFalse(ok)
        self.assertIn("No Power-ups", info["reason"])

    def test_a_tower_weapon_is_wielded_for_the_match_and_burns_charges(self):
        data, rng = self._in_arena()
        data["inventory"] = {**data["inventory"], "Dominion sword": 1}
        data, ok, info = apply_dominion_tower_command_pure(
            data, "use_powerup", {"item": "Dominion sword"}, rng
        )
        self.assertTrue(ok, info)
        self.assertEqual(data["dominion_tower"]["weapon_powerup"]["charges"], 500)
        data, ok, result = apply_dominion_tower_review_pure(
            data, rng, equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, result)
        weapon = data["dominion_tower"]["weapon_powerup"]
        self.assertEqual(500 - weapon.get("charges", 0), result["ticks_elapsed"])

    def test_the_crossbow_spends_one_charge_per_shot_fired(self):
        data, rng = self._freestyle_nomad()
        data["equipment"] = {"weapon": "Rune crossbow"}
        data["combat_attack_style"] = "ranged_rapid"
        data["combat_supply_loadout"] = {"ammo": {"Broad-tipped bolts": 100}}
        data["inventory"] = {**data["inventory"], "Dominion crossbow": 1}
        data, ok, info = apply_dominion_tower_command_pure(
            data, "use_powerup", {"item": "Dominion crossbow"}, rng
        )
        self.assertTrue(ok, info)
        data, ok, result = apply_dominion_tower_review_pure(
            data, rng, equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, result)
        shots = sum(int(quantity) for quantity in result["ammo_used"].values())
        self.assertGreater(shots, 0)
        self.assertEqual(100 - data["dominion_tower"]["weapon_powerup"]["charges"], shots)
        self.assertNotEqual(shots, 6)

    def test_the_staff_spends_one_charge_per_magic_hit(self):
        data, _unused_rng = self._freestyle_nomad()
        rng = lambda: 0.1
        data["equipment"] = {"weapon": "Staff"}
        data["combat_attack_style"] = "magic_standard"
        data["current_combat_spell"] = "wind_strike"
        data["combat_supply_loadout"] = {
            "runes": {"Air rune": 100, "Mind rune": 100}
        }
        data["inventory"] = {**data["inventory"], "Dominion staff": 1}
        data, ok, info = apply_dominion_tower_command_pure(
            data, "use_powerup", {"item": "Dominion staff"}, rng
        )
        self.assertTrue(ok, info)
        data, ok, result = apply_dominion_tower_review_pure(
            data, rng, equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["combat_class"], "magic")
        self.assertGreater(result["player_damage"], 0)
        self.assertEqual(100 - data["dominion_tower"]["weapon_powerup"]["charges"], 2)

    def test_the_staff_does_not_spend_a_charge_when_every_cast_misses(self):
        rng = lambda: 0.999999
        data, _unused_rng = self._freestyle_nomad()
        data["equipment"] = {"weapon": "Staff"}
        data["combat_attack_style"] = "magic_standard"
        data["current_combat_spell"] = "wind_strike"
        data["combat_supply_loadout"] = {
            "runes": {"Air rune": 100, "Mind rune": 100}
        }
        data["inventory"] = {**data["inventory"], "Dominion staff": 1}
        data, ok, info = apply_dominion_tower_command_pure(
            data, "use_powerup", {"item": "Dominion staff"}, rng
        )
        self.assertTrue(ok, info)
        data, ok, result = apply_dominion_tower_review_pure(
            data, rng, equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["player_damage"], 0)
        self.assertGreater(sum(result["runes_used"].values()), 0)
        self.assertEqual(data["dominion_tower"]["weapon_powerup"]["charges"], 100)

    def test_the_staff_charges_only_the_landed_cast_in_a_mixed_slice(self):
        # Seed 1 makes the slice cast twice with exactly one cast landing, so
        # a charge count of one distinguishes landed-hit budgeting from the
        # old per-attack-opportunity derivation, which would charge two.
        rng = random.Random(1).random
        data, _unused_rng = self._freestyle_nomad()
        data["equipment"] = {"weapon": "Staff"}
        data["combat_attack_style"] = "magic_standard"
        data["current_combat_spell"] = "wind_strike"
        data["combat_supply_loadout"] = {
            "runes": {"Air rune": 100, "Mind rune": 100}
        }
        data["inventory"] = {**data["inventory"], "Dominion staff": 1}
        data, ok, info = apply_dominion_tower_command_pure(
            data, "use_powerup", {"item": "Dominion staff"}, rng
        )
        self.assertTrue(ok, info)
        data, ok, result = apply_dominion_tower_review_pure(
            data, rng, equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["player_hits_landed"], 1)
        self.assertGreater(result["player_damage"], 0)
        self.assertGreaterEqual(sum(result["runes_used"].values()), 2)
        self.assertEqual(100 - data["dominion_tower"]["weapon_powerup"]["charges"], 1)

    def test_the_dominion_staff_needs_its_ninety_magic(self):
        data, rng = self._in_arena()
        data["magic_level"] = 80
        data["inventory"] = {**data["inventory"], "Dominion staff": 1}
        _updated, ok, info = apply_dominion_tower_command_pure(
            data, "use_powerup", {"item": "Dominion staff"}, rng
        )
        self.assertFalse(ok)
        self.assertIn("level 90", info["reason"])

    def test_the_tower_potions_only_work_inside_and_restore_what_they_say(self):
        data, rng = self._in_arena()
        data["inventory"] = {**data["inventory"], "Dom super prayer": 1}
        data["combat_prayer_points"] = 0
        data, ok, info = apply_dominion_tower_command_pure(
            data, "drink_potion", {"item": "Dom super prayer"}, rng
        )
        self.assertTrue(ok, info)
        self.assertEqual(data["combat_prayer_points"], 990)
        outside = _player(*_twenty_quests())
        outside["inventory"] = {**outside["inventory"], "Dom super prayer": 1}
        _updated, ok, info = apply_dominion_tower_command_pure(
            outside, "drink_potion", {"item": "Dom super prayer"}, rng
        )
        self.assertFalse(ok)
        self.assertIn("inside the tower", info["reason"])

    def test_rewards_exchange_into_a_single_book(self):
        data, rng = self._in_arena()
        data["inventory"] = {
            **data["inventory"],
            "Scorpion meat": 28,
            "Diminutive bomb": 2,
        }
        data, ok, info = apply_dominion_tower_command_pure(
            data, "exchange_rewards", {}, rng
        )
        self.assertTrue(ok, info)
        self.assertEqual(info["exchanged"], 30)
        self.assertEqual(int(data["inventory"].get("Scorpion meat", 0)), 0)
        self.assertEqual(int(data["inventory"].get(DOMINION_TOWER_XP_BOOK, 0)), 1)

    def test_each_xp_book_keeps_the_factor_that_created_it(self):
        data = _player(*_twenty_quests())
        data["inventory"] = {**data["inventory"], "Scorpion meat": 1}
        data, ok, first = apply_dominion_tower_command_pure(
            data, "exchange_rewards", {}, random.random
        )
        self.assertTrue(ok, first)
        data["inventory"] = {**data["inventory"], "Scorpion meat": 2}
        data, ok, second = apply_dominion_tower_command_pure(
            data, "exchange_rewards", {}, random.random
        )
        self.assertTrue(ok, second)
        self.assertEqual(data["dominion_tower"]["xp_book_factors"], [500, 1000])
        before = float(data.get("attack_exp", 0.0))
        data, ok, info = apply_dominion_tower_command_pure(
            data, "read_xp_book", {"skill": "attack"}, random.random
        )
        self.assertTrue(ok, info)
        first_paid = float(data["attack_exp"]) - before
        before = float(data["attack_exp"])
        data, ok, info = apply_dominion_tower_command_pure(
            data, "read_xp_book", {"skill": "attack"}, random.random
        )
        self.assertTrue(ok, info)
        second_paid = float(data["attack_exp"]) - before
        self.assertEqual(first_paid, dominion_tower_xp_book_amount_pure(500, "attack"))
        self.assertEqual(second_paid, dominion_tower_xp_book_amount_pure(1000, "attack"))


class DominionTowerPersistenceTest(unittest.TestCase):
    """Sanitize, migrate, and the runtime handler."""

    def test_the_default_state_survives_a_sanitize_round_trip(self):
        state = default_dominion_tower_state_pure()
        self.assertEqual(sanitize_dominion_tower_state_pure(state), state)

    def test_a_legacy_global_book_factor_survives_state_only_sanitization(self):
        state = sanitize_dominion_tower_state_pure({"xp_book_factor": 750})
        self.assertEqual(state["xp_book_factors"], [750])

    def test_legacy_global_factor_values_every_book_held_at_migration(self):
        legacy = _player(*_twenty_quests())
        legacy["inventory"] = {
            **legacy["inventory"],
            DOMINION_TOWER_XP_BOOK: 2,
        }
        legacy["dominion_tower"] = {"xp_book_factor": 1000}
        data = migrate_loaded_data(legacy, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(
            dominion_tower_view_pure(data)["xp_book_factors"],
            [1000, 1000],
        )
        before = float(data.get("attack_exp", 0.0))

        for _ in range(2):
            data, ok, info = apply_dominion_tower_command_pure(
                data, "read_xp_book", {"skill": "attack"}, random.random
            )
            self.assertTrue(ok, info)

        self.assertEqual(
            float(data["attack_exp"]) - before,
            2 * dominion_tower_xp_book_amount_pure(1000, "attack"),
        )
        self.assertEqual(
            int(data["inventory"].get(DOMINION_TOWER_XP_BOOK, 0)),
            0,
        )
        self.assertEqual(data["dominion_tower"]["xp_book_factors"], [])

    def test_legacy_factor_without_a_book_cannot_value_a_new_exchange(self):
        legacy = _player(*_twenty_quests())
        legacy["inventory"] = {**legacy["inventory"], "Scorpion meat": 1}
        legacy["dominion_tower"] = {"xp_book_factor": 750}
        data = migrate_loaded_data(legacy, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(dominion_tower_view_pure(data)["xp_book_factors"], [])

        data, ok, info = apply_dominion_tower_command_pure(
            data, "exchange_rewards", {}, random.random
        )
        self.assertTrue(ok, info)
        self.assertEqual(data["dominion_tower"]["xp_book_factors"], [500])
        before = float(data.get("attack_exp", 0.0))
        data, ok, info = apply_dominion_tower_command_pure(
            data, "read_xp_book", {"skill": "attack"}, random.random
        )
        self.assertTrue(ok, info)
        self.assertEqual(
            float(data["attack_exp"]) - before,
            dominion_tower_xp_book_amount_pure(500, "attack"),
        )

    def test_junk_state_is_rebuilt_rather_than_trusted(self):
        state = sanitize_dominion_tower_state_pure(
            {
                "mode": "not-a-mode",
                "encounter_id": "not-a-boss",
                "roster": [{"npc_key": "nope"}, "junk"],
                "handicaps": ["nope", "no_prayer"],
                "dominion_factor": DOMINION_TOWER_MAX_FACTOR * 5,
                "reward_credits": 900,
                "journal_pages": 900,
            }
        )
        self.assertEqual(state["mode"], "")
        self.assertEqual(state["roster"], [])
        self.assertEqual(state["handicaps"], ["no_prayer"])
        self.assertEqual(state["dominion_factor"], DOMINION_TOWER_MAX_FACTOR)
        self.assertEqual(state["reward_credits"], DOMINION_TOWER_REWARD_CREDIT_CAP)
        self.assertEqual(state["journal_pages"], 20)

    def test_a_legacy_save_gains_the_tower_at_the_current_schema(self):
        legacy = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        legacy.pop("dominion_tower", None)
        legacy["config_version"] = 30
        migrated = migrate_loaded_data(legacy, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(
            migrated["dominion_tower"], default_dominion_tower_state_pure()
        )

    def test_an_active_run_survives_a_save_and_load(self):
        rng = random.Random(6).random
        data = _geared(_player(*_twenty_quests()))
        data, ok, _info = apply_dominion_tower_command_pure(data, "talk_to_face", {}, rng)
        self.assertTrue(ok)
        data, ok, _info = apply_dominion_tower_command_pure(
            data, "start_mode", {"mode": "endurance"}, rng
        )
        self.assertTrue(ok)
        data, ok, _result = apply_dominion_tower_review_pure(
            data, rng, equipment_data=EQUIPMENT_DATA
        )
        self.assertTrue(ok)
        before = dominion_tower_view_pure(data)
        reloaded = migrate_loaded_data(
            json.loads(json.dumps(data)), ORE_DATA, ITEM_DEFINITIONS
        )
        after = dominion_tower_view_pure(reloaded)
        self.assertEqual(after["mode"], before["mode"])
        self.assertEqual(after["encounter_name"], before["encounter_name"])
        self.assertEqual(after["engaged_lifepoints"], before["engaged_lifepoints"])
        self.assertEqual(reloaded["activity_session"]["active_id"], DOMINION_TOWER_ACTIVITY_ID)

    def test_the_runtime_utility_handler_drives_a_real_round(self):
        rng = random.Random(8)
        data = _geared(_player(*_twenty_quests()))
        data, ok, _info = apply_dominion_tower_command_pure(
            data, "talk_to_face", {}, rng.random
        )
        self.assertTrue(ok)
        data, ok, _info = apply_dominion_tower_command_pure(
            data, "start_mode", {"mode": "endurance"}, rng.random
        )
        self.assertTrue(ok)
        data["current_utility"] = DOMINION_TOWER_ACTIVITY_ID
        messages: list[str] = []
        saves: list[int] = []
        ctx = RuntimeActionContext(
            player_data=data,
            random_random=rng.random,
            show_error_message=lambda *args: self.fail(f"unexpected runtime error {args}"),
            deactivate_current_skill=lambda: None,
            award_skill_exp=lambda *_args: self.fail("the pure activity owns XP"),
            award_hidden_skill_exp=lambda *_args: None,
            level_up_check=lambda *_args: None,
            check_achievements=lambda *_args: None,
            save_player_data=lambda: saves.append(1),
            refresh_skill_availability=lambda: None,
            refresh_skill_availability_partial=lambda *_args: None,
            can_smith_any=lambda: True,
            show_exp=lambda amount: messages.append(float(amount)),
            show_activity_gain=lambda message: messages.append(str(message)),
            implemented_exp_keys_snapshot=lambda: {},
            show_quest_exp_delta=lambda *_args: None,
        )
        before = dominion_tower_view_pure(data)["engaged_lifepoints"]
        self.assertTrue(handle_utility_answer(ctx))
        self.assertTrue(saves)
        self.assertTrue(messages)
        self.assertLess(dominion_tower_view_pure(data)["engaged_lifepoints"], before)


class DominionTowerTarnPhaseTest(unittest.TestCase):
    """The tower's Tarn is two forms and four optional dogs, not one fight.

    "Tarn starts the match in mutant form with four large Terror dogs next to
    him... Once mutant Tarn is slain, his ghost form appears... The match is won
    by killing the ghost Tarn. The terror dogs do not have to be killed."
    """

    def _freestyle_tarn(self):
        rng = random.Random(11).random
        data = _geared(_player(*_twenty_quests()))
        state = dict(data["dominion_tower"])
        state["defeated"] = {"tarn_razorlor": 1}
        data["dominion_tower"] = state
        data, ok, info = apply_dominion_tower_command_pure(data, "talk_to_face", {}, rng)
        self.assertTrue(ok, info)
        data, ok, info = apply_dominion_tower_command_pure(
            data, "start_mode", {"mode": "freestyle", "encounter_id": "tarn_razorlor"}, rng
        )
        self.assertTrue(ok, info)
        return data, rng

    def test_the_match_opens_on_the_mutant_beside_four_dogs(self):
        data, _rng = self._freestyle_tarn()
        roster = data["dominion_tower"]["roster"]
        self.assertEqual(
            [member["npc_key"] for member in roster],
            ["mutant_tarn", *["terror_dog_110"] * 4],
        )
        view = dominion_tower_view_pure(data)
        self.assertEqual(view["engaged_name"], "Mutant tarn")
        # The tower states the mutant's own style, so it is not the lair's melee.
        self.assertEqual(DOMINION_TOWER_NPCS["mutant_tarn"]["attack_styles"], ("magic",))
        self.assertEqual(DOMINION_TOWER_NPCS["tarn_ghost"]["attack_styles"], ("melee",))

    def test_the_ghost_rises_when_the_mutant_falls_and_ends_the_match_alone(self):
        data, rng = self._freestyle_tarn()
        seen_ghost = False
        for _ in range(600):
            data["combat_lifepoints"] = 990
            data, ok, result = apply_dominion_tower_review_pure(
                data, rng, equipment_data=EQUIPMENT_DATA
            )
            self.assertTrue(ok, result)
        fought_ids = set()
            self.assertFalse(result.get("player_died"), result)
            if result.get("won"):
                break
            keys = [member["npc_key"] for member in data["dominion_tower"]["roster"]]
            if "mutant_tarn" not in keys:
                # The mutant left one form behind, not an empty slot, and the
                # dogs the player never touched are all still in the arena.
                self.assertEqual(keys, ["tarn_ghost", *["terror_dog_110"] * 4])
            fought_ids.add(result["npc_id"])
                self.assertEqual(
                    dominion_tower_view_pure(data)["engaged_name"], "Tarn"
                )
                seen_ghost = True
        else:
            self.fail("the match never resolved")

        self.assertTrue(seen_ghost, "the ghost form never appeared")
        # Won with every dog alive: the ghost's death is the whole victory
        # condition, so the arena must not wait on the minions.
        self.assertEqual(data["dominion_tower"]["defeated"]["tarn_razorlor"], 2)


if __name__ == "__main__":
        self.assertEqual(fought_ids, {14429, 14430})
    unittest.main()
