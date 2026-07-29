"""Capes of Accomplishment and Distinction, and the Taskmaster presentation.

Design contract clauses D8, D12, D13 and D15 of
``memory-bank/achievement-diary-item-grants-design.md``.

Nothing here stubs the system under test. Every player starts from a real
``default_player_data``, every purchase goes through the Cabinet's real command
dispatcher, and every cape is equipped through the real equipment path — so a
cape that cannot actually be earned, bought or worn fails a test rather than
shipping as an inert row.
"""

from __future__ import annotations

import os
import sys
import unittest

# The runtime harness lives beside this file; `unittest discover` puts the tests
# directory on the path but `python3 -m unittest tests.<module>` does not.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import EQUIPMENT_DATA, HUNTER_DATA, ORE_DATA
from ankiscape.core.skill_registry import trainable_skill_definitions
from ankiscape.core.storage_pure import (
    CURRENT_CONFIG_VERSION,
    default_player_data,
    migrate_loaded_data,
)
from ankiscape.data.achievement_cape_data import (
    PRESTIGE_CAPES,
    PRESTIGE_CAPES_BY_ID,
    SKILLCAPE_LEVEL,
    SKILLCAPE_PRICE,
    SKILLCAPES,
    skillcape_definitions,
)
from ankiscape.data.quest_data import QUESTS
from ankiscape.logic.achievement_diary_logic import (
    achievement_cabinet_view_pure,
    apply_achievement_diary_command_pure,
    taskmaster_presentation_pure,
)
from ankiscape.logic.agility_logic import agility_effective_level_pure
from ankiscape.logic.cape_logic import (
    SKILLCAPE_EFFECTIVE_LEVEL,
    cape_view_pure,
    effective_roll_level_pure,
    latent_cutoff_skills_pure,
    prestige_cape_eligible_pure,
    refresh_capes_pure,
    skillcapes_are_trimmed_pure,
)
from ankiscape.logic.music_log_logic import refresh_music_log_pure
from ankiscape.logic_pure.logic_pure_gathering import (
    calculate_hunter_success_probability_pure,
)
from ankiscape.logic_pure.logic_pure_equipment import can_equip_item_pure, equip_item_pure
from ankiscape.runtime.runtime_actions import handle_cooking_answer

# Reuse the existing RuntimeActionContext harness rather than keeping a second
# copy of it in step with the real one.
from test_runtime_actions import _context


def _player(**overrides) -> dict:
    player = default_player_data(ORE_DATA)
    player.update(overrides)
    return player


def _buy(player: dict, cape_id: str):
    """Buy through the Cabinet's real dispatcher, not through a helper."""

    return apply_achievement_diary_command_pure(player, "purchase_cape", {"cape_id": cape_id})


def _wear(player: dict, item_name: str) -> dict:
    allowed, reason = can_equip_item_pure(item_name, EQUIPMENT_DATA, player)
    assert allowed, f"{item_name} could not be equipped: {reason}"
    inventory, equipment, _worn = equip_item_pure(
        item_name, player["inventory"], player["equipment"], EQUIPMENT_DATA
    )
    player["inventory"], player["equipment"] = inventory, equipment
    return player


class SkillcapeTest(unittest.TestCase):
    """D12: the 99 gate, the price, the master, trimming and the keepsake."""

    def test_every_skillcape_hood_and_trim_is_registered_wearable_equipment(self):
        for cape in skillcape_definitions():
            for name in (cape.cape, cape.trimmed_cape, cape.hood):
                self.assertIn(name, EQUIPMENT_DATA, name)
                row = EQUIPMENT_DATA[name]
                self.assertEqual(row.skill_requirements, ((cape.skill_id, SKILLCAPE_LEVEL),))
                self.assertGreater(row.source_item_id, 0, name)
                self.assertTrue(row.source, name)
            self.assertEqual(EQUIPMENT_DATA[cape.cape].bonuses.prayer, 0)
            self.assertEqual(EQUIPMENT_DATA[cape.trimmed_cape].bonuses.prayer, 4)
            self.assertEqual(EQUIPMENT_DATA[cape.hood].bonuses.prayer, 0)
            self.assertTrue(cape.master, cape.skill_id)

    def test_dungeoneering_skillcape_is_live_and_purchasable(self):
        trainable = {skill.id for skill in trainable_skill_definitions()}
        self.assertIn("dungeoneering", trainable)
        row = next(cape for cape in SKILLCAPES if cape.skill_id == "dungeoneering")
        self.assertEqual(row.master, "Thok, Master of Dungeoneering")
        self.assertIn(
            "dungeoneering", {cape.skill_id for cape in skillcape_definitions()}
        )
        self.assertIn("Dungeoneering cape", EQUIPMENT_DATA)
        self.assertEqual(latent_cutoff_skills_pure(), ())

        player = _player(dungeoneering_level=SKILLCAPE_LEVEL)
        player["inventory"] = {"Coins": SKILLCAPE_PRICE}
        player, ok, info = _buy(player, "dungeoneering")
        self.assertTrue(ok, info)
        self.assertIn("Thok", info["message"])
        self.assertEqual(player["inventory"]["Dungeoneering cape"], 1)

    def test_the_all_skills_gate_counts_all_twenty_five_cutoff_skills(self):
        player = _maxed(_player())
        ok, reason = prestige_cape_eligible_pure(player, "max")
        self.assertTrue(ok, reason)

        row = next(
            item for item in cape_view_pure(player)["completionist"] if item["id"] == "max"
        )
        self.assertEqual(row["need"], 25)
        self.assertEqual(row["have"], 25)
        self.assertEqual(row["label"], "Level 99 in every skill")

    def test_a_cape_is_earned_bought_from_its_master_and_worn(self):
        player = _player(mining_level=SKILLCAPE_LEVEL)
        player["inventory"] = {"Coins": SKILLCAPE_PRICE}

        player, ok, info = _buy(player, "mining")
        self.assertTrue(ok, info)
        self.assertIn("Dwarf", info["message"])
        self.assertEqual(player["inventory"].get("Coins", 0), 0)
        self.assertEqual(player["inventory"]["Mining cape"], 1)
        self.assertEqual(player["inventory"]["Mining hood"], 1)

        player = _wear(player, "Mining cape")
        self.assertEqual(player["equipment"]["cape"], "Mining cape")

    def test_the_gate_and_the_price_both_refuse(self):
        broke = _player(mining_level=SKILLCAPE_LEVEL)
        broke["inventory"] = {"Coins": SKILLCAPE_PRICE - 1}
        _same, ok, info = _buy(broke, "mining")
        self.assertFalse(ok)
        self.assertIn("99,000", info["reason"])

        low = _player(mining_level=98)
        low["inventory"] = {"Coins": SKILLCAPE_PRICE}
        _same, ok, info = _buy(low, "mining")
        self.assertFalse(ok)
        self.assertIn("99", info["reason"])

    def test_buying_twice_is_refused(self):
        player = _player(mining_level=SKILLCAPE_LEVEL)
        player["inventory"] = {"Coins": SKILLCAPE_PRICE * 2}
        player, ok, _info = _buy(player, "mining")
        self.assertTrue(ok)
        _same, ok, info = _buy(player, "mining")
        self.assertFalse(ok)
        self.assertIn("already own", info["reason"])

    def test_a_second_99_trims_a_cape_in_the_bank_and_one_being_worn(self):
        player = _player(mining_level=SKILLCAPE_LEVEL, fishing_level=SKILLCAPE_LEVEL)
        player["inventory"] = {"Coins": SKILLCAPE_PRICE * 2}
        player, ok, _info = _buy(player, "mining")
        self.assertTrue(ok)
        # Two 99s already: Darkan's `checkMulti99s` hands over the trimmed cape.
        self.assertEqual(player["inventory"]["Mining cape (t)"], 1)

        # And a cape bought before the second 99 is trimmed retroactively,
        # wherever it sits.
        early = _player(mining_level=SKILLCAPE_LEVEL)
        early["inventory"] = {"Coins": SKILLCAPE_PRICE}
        early, ok, _info = _buy(early, "mining")
        self.assertTrue(ok)
        self.assertFalse(skillcapes_are_trimmed_pure(early))
        early = _wear(early, "Mining cape")
        early["fishing_level"] = SKILLCAPE_LEVEL
        early = refresh_capes_pure(early)
        self.assertTrue(skillcapes_are_trimmed_pure(early))
        self.assertEqual(early["equipment"]["cape"], "Mining cape (t)")
        self.assertNotIn("Mining cape", early["inventory"])

    def test_the_keepsake_records_the_first_99_and_never_moves(self):
        player = _player(mining_level=SKILLCAPE_LEVEL)
        player = refresh_capes_pure(player)
        self.assertEqual(player["capes"]["keepsake_skill"], "mining")

        player["fishing_level"] = SKILLCAPE_LEVEL
        player = refresh_capes_pure(player)
        self.assertEqual(player["capes"]["keepsake_skill"], "mining")
        self.assertEqual(cape_view_pure(player)["keepsake_cape"], "Mining cape")


class EffectiveLevelTest(unittest.TestCase):
    """D13: one effective-level mechanism, and it reaches 100."""

    def test_a_worn_cape_puts_the_skill_at_100_and_leaves_the_others_alone(self):
        player = _player(mining_level=SKILLCAPE_LEVEL, fishing_level=50)
        player["inventory"] = {"Coins": SKILLCAPE_PRICE}
        player, ok, _info = _buy(player, "mining")
        self.assertTrue(ok)

        self.assertEqual(effective_roll_level_pure(player, "mining", 99), 99)
        player = _wear(player, "Mining cape")
        self.assertEqual(effective_roll_level_pure(player, "mining", 99), 100)
        self.assertEqual(effective_roll_level_pure(player, "fishing", 50), 50)

    def test_agility_reads_the_shared_seam_rather_than_a_second_mechanism(self):
        player = _player(agility_level=SKILLCAPE_LEVEL)
        player["inventory"] = {"Coins": SKILLCAPE_PRICE}
        player, ok, _info = _buy(player, "agility")
        self.assertTrue(ok)
        self.assertEqual(agility_effective_level_pure(player), 99)
        player = _wear(player, "Agility cape")
        self.assertEqual(agility_effective_level_pure(player), 100)
        self.assertEqual(effective_roll_level_pure(player, "agility", 99), 100)

    def test_a_trimmed_cape_boosts_exactly_as_the_untrimmed_one_does(self):
        player = _player(mining_level=SKILLCAPE_LEVEL, fishing_level=SKILLCAPE_LEVEL)
        player["inventory"] = {"Coins": SKILLCAPE_PRICE}
        player, ok, _info = _buy(player, "mining")
        self.assertTrue(ok)
        player = _wear(player, "Mining cape (t)")
        self.assertEqual(effective_roll_level_pure(player, "mining", 99), 100)

    def test_invisible_familiar_boost_adds_after_the_visible_cape_boost(self):
        player = _player(
            mining_level=SKILLCAPE_LEVEL,
            equipment={"cape": "Mining cape"},
        )
        player["summoning_state"]["active_follower"] = {
            "kind": "familiar",
            "entity_id": "lavatitan",
        }

        self.assertEqual(effective_roll_level_pure(player, "mining", 99), 110)

    def test_a_real_review_changes_its_outcome_because_the_cape_is_worn(self):
        """The seam reaches a shipped handler, not just a helper.

        Same target, same roll, same level: the cape is the only difference, and
        it is the difference between nothing and a Roe. This is the Cooking
        member of the 39 roll paths the boost actually moves; the count itself
        is pinned by the test below.
        """

        def gut(equipment: dict) -> tuple:
            calls = {"xp": [], "saves": 0, "errors": []}
            player = {
                "inventory": {"Leaping trout": 1},
                "equipment": equipment,
                "cooking_level": 99,
                "cooking_exp": 0,
                "current_cooking": "gut_leaping_trout",
                "cooking_success_count": 0,
                "cooking_burn_count": 0,
                "completed_achievements": [],
            }
            handle_cooking_answer(_context(player, calls, random_values=[0.4420] * 10))
            return player["inventory"].get("Roe", 0), player["cooking_exp"]

        self.assertEqual(gut({}), (0, 0))
        self.assertEqual(gut({"cape": "Cooking cape"}), (1, 10.0))

    def test_the_boost_moves_thirty_nine_roll_paths_not_one(self):
        """Design fork 3.10 said "exactly one". Measured, it is 39.

        The claim mattered: an owner told the rule is nearly a no-op may decide
        differently knowing it changes 33 Hunter catches, 3 Firemaking burns, 2
        Thieving yields and 1 Cooking gut. Hunter is measured here because it is
        by far the largest share and its formula is the reason — Darkan's
        `Utils.skillSuccess` interpolates on `level / 99.0` without clamping the
        input, so any level above 99 keeps moving, while the period tables that
        do saturate at 99 stay silent.
        """

        changed = [
            name
            for name, spec in HUNTER_DATA.items()
            if calculate_hunter_success_probability_pure(99, spec)
            != calculate_hunter_success_probability_pure(SKILLCAPE_EFFECTIVE_LEVEL, spec)
        ]
        self.assertEqual(len(changed), 33)
        self.assertIn("catch_crimson_swift", changed)

    def test_the_operate_boost_has_full_uptime_and_needs_no_activation(self):
        """The real-time operate boost is abstracted to full uptime while worn."""

        player = _player(agility_level=SKILLCAPE_LEVEL)
        player["inventory"] = {"Coins": SKILLCAPE_PRICE}
        player, _ok, _info = _buy(player, "agility")
        player = _wear(player, "Agility cape")
        self.assertEqual(player.get("agility_boost_actions_remaining", 0), 0)
        for _ in range(50):
            self.assertEqual(agility_effective_level_pure(player), 100)


def _maxed(player: dict) -> dict:
    for skill in trainable_skill_definitions():
        player[f"{skill.id}_level"] = SKILLCAPE_LEVEL
    return player


def _all_quests_done(player: dict) -> dict:
    quests = dict(player.get("quests") or {})
    for quest in QUESTS:
        state = dict(quests.get(quest.id) or {})
        state["completed"] = True
        quests[quest.id] = state
    player["quests"] = quests
    return player


class PrestigeCapeTest(unittest.TestCase):
    """D15: quest point, Max, Completionist and both Veteran capes."""

    def test_every_prestige_cape_is_registered_wearable_equipment(self):
        for cape in PRESTIGE_CAPES:
            self.assertIn(cape.cape, EQUIPMENT_DATA, cape.cape)
            self.assertIn(cape.hood, EQUIPMENT_DATA, cape.hood)
            self.assertGreater(EQUIPMENT_DATA[cape.cape].source_item_id, 0)
            self.assertTrue(cape.seller, cape.id)
            self.assertGreater(cape.price, 0, cape.id)

    def test_max_and_completionist_capes_use_cache_bonus_blocks(self):
        for name, attack, defence, prayer in (
            ("Max cape", 5, 11, 10),
            ("Completionist cape", 10, 12, 13),
        ):
            bonuses = EQUIPMENT_DATA[name].bonuses
            for field in (
                "attack_stab",
                "attack_slash",
                "attack_crush",
                "attack_magic",
                "attack_ranged",
            ):
                self.assertEqual(getattr(bonuses, field), attack, (name, field))
            for field in (
                "defence_stab",
                "defence_slash",
                "defence_crush",
                "defence_magic",
                "defence_ranged",
            ):
                self.assertEqual(getattr(bonuses, field), defence, (name, field))
            self.assertEqual(bonuses.prayer, prayer, name)

    def test_the_quest_point_cape_is_earned_by_finishing_every_quest(self):
        player = _player()
        player["inventory"] = {"Coins": PRESTIGE_CAPES_BY_ID["quest_point"].price}
        _same, ok, info = _buy(player, "quest_point")
        self.assertFalse(ok)
        self.assertIn("quest", info["reason"].lower())

        player = _all_quests_done(player)
        player, ok, info = _buy(player, "quest_point")
        self.assertTrue(ok, info)
        self.assertIn("Wise Old Man", info["message"])
        player = _wear(player, "Quest point cape")
        self.assertEqual(player["equipment"]["cape"], "Quest point cape")

    def test_the_max_cape_is_earned_by_99_in_every_skill(self):
        player = _player()
        player["inventory"] = {"Coins": PRESTIGE_CAPES_BY_ID["max"].price}
        _same, ok, info = _buy(player, "max")
        self.assertFalse(ok)
        self.assertIn("short of 99", info["reason"])

        player = _maxed(player)
        player, ok, info = _buy(player, "max")
        self.assertTrue(ok, info)
        self.assertEqual(player["inventory"].get("Coins", 0), 0)
        player = _wear(player, "Max cape")
        self.assertEqual(player["equipment"]["cape"], "Max cape")

    def test_both_veteran_capes_are_earned_from_simulated_world_time(self):
        for cape_id, years in (("veteran_5", 5), ("veteran_10", 10)):
            cape = PRESTIGE_CAPES_BY_ID[cape_id]
            self.assertEqual(cape.threshold, 240 * 365 * years)
            player = _player()
            player["inventory"] = {"Coins": cape.price}
            player["shop_market_clock"] = {
                "version": 1,
                "answered_cards": cape.threshold - 1,
                "market_tick": 0,
            }
            _same, ok, info = _buy(player, cape_id)
            self.assertFalse(ok)
            self.assertIn("answered cards", info["reason"])

            player["shop_market_clock"]["answered_cards"] = cape.threshold
            player, ok, info = _buy(player, cape_id)
            self.assertTrue(ok, info)
            self.assertIn("Hans", info["message"])
            player = _wear(player, cape.cape)
            self.assertEqual(player["equipment"]["cape"], cape.cape)

    def test_the_completionist_cape_is_earned_by_meeting_every_live_requirement(self):
        player = _maxed(_all_quests_done(_player()))
        player["inventory"] = {"Coins": PRESTIGE_CAPES_BY_ID["completionist"].price}
        diaries = dict(player["achievement_diaries"])
        diaries["taskmaster"] = True
        player["achievement_diaries"] = diaries
        # Earn the music rather than assert it: finishing every quest unlocks
        # every live track, which is exactly what the requirement measures.
        player, _newly = refresh_music_log_pure(player)

        rows = {row["id"]: row for row in cape_view_pure(player)["completionist"]}
        for row_id in ("max", "quests", "taskmaster", "music"):
            self.assertTrue(rows[row_id]["met"], row_id)
        # The families whose feature has not shipped stay latent, and a latent
        # row never blocks the purchase.
        self.assertTrue(rows["boss_long_tail"]["latent"])
        self.assertFalse(rows["boss_long_tail"]["met"])

        player, ok, info = _buy(player, "completionist")
        self.assertTrue(ok, info)
        self.assertIn("Museum guard", info["message"])
        player = _wear(player, "Completionist cape")
        self.assertEqual(player["equipment"]["cape"], "Completionist cape")

    def test_lost_quest_cape_eligibility_unequips_the_owned_cape(self):
        player = _all_quests_done(_player())
        player["inventory"] = {"Coins": PRESTIGE_CAPES_BY_ID["quest_point"].price}
        player, ok, info = _buy(player, "quest_point")
        self.assertTrue(ok, info)
        player = _wear(player, "Quest point cape")

        player["quests"][QUESTS[0].id]["completed"] = False
        player = refresh_capes_pure(player)

        self.assertNotEqual(player["equipment"].get("cape"), "Quest point cape")
        self.assertEqual(player["inventory"].get("Quest point cape"), 1)

    def test_lost_quest_cape_eligibility_prevents_re_equipping(self):
        player = _all_quests_done(_player())
        player["inventory"] = {"Coins": PRESTIGE_CAPES_BY_ID["quest_point"].price}
        player, ok, info = _buy(player, "quest_point")
        self.assertTrue(ok, info)

        player["quests"][QUESTS[0].id]["completed"] = False
        allowed, reason = can_equip_item_pure("Quest point cape", EQUIPMENT_DATA, player)

        self.assertFalse(allowed)
        self.assertIn("quest", reason.lower())

    def test_completionist_names_what_is_still_outstanding(self):
        _same, ok, info = _buy(_player(), "completionist")
        self.assertFalse(ok)
        for expected in ("Level 99 in every skill", "Every quest complete", "Taskmaster"):
            self.assertIn(expected, info["reason"])


class TaskmasterPresentationTest(unittest.TestCase):
    """D8: the one-time completion presentation."""

    def test_nothing_is_presented_before_taskmaster_is_earned(self):
        presentation = taskmaster_presentation_pure(_player())
        self.assertFalse(presentation["earned"])
        self.assertFalse(presentation["show"])

    def test_the_presentation_shows_once_and_then_never_again(self):
        player = _player()
        diaries = dict(player["achievement_diaries"])
        diaries["taskmaster"] = True
        player["achievement_diaries"] = diaries

        self.assertTrue(achievement_cabinet_view_pure(player)["taskmaster_presentation"]["show"])
        player, ok, info = apply_achievement_diary_command_pure(
            player, "acknowledge_taskmaster", {}
        )
        self.assertTrue(ok, info)
        self.assertIn("Taskmaster", info["message"])
        self.assertFalse(achievement_cabinet_view_pure(player)["taskmaster_presentation"]["show"])
        self.assertTrue(taskmaster_presentation_pure(player)["earned"])

        _same, ok, info = apply_achievement_diary_command_pure(
            player, "acknowledge_taskmaster", {}
        )
        self.assertFalse(ok)
        self.assertIn("already", info["reason"])

    def test_an_unearned_presentation_cannot_be_acknowledged(self):
        _same, ok, info = apply_achievement_diary_command_pure(
            _player(), "acknowledge_taskmaster", {}
        )
        self.assertFalse(ok)
        self.assertIn("not complete", info["reason"])

    def test_taskmaster_grants_no_cape_stat_or_item(self):
        """The design contract: no invented cape, stats or mechanical perk."""

        player = _player()
        diaries = dict(player["achievement_diaries"])
        diaries["taskmaster"] = True
        player["achievement_diaries"] = diaries
        before = dict(player["inventory"])
        player, ok, _info = apply_achievement_diary_command_pure(
            player, "acknowledge_taskmaster", {}
        )
        self.assertTrue(ok)
        self.assertEqual(player["inventory"], before)


class CapeMigrationTest(unittest.TestCase):
    def test_an_old_save_gains_the_cape_state_and_its_keepsake_on_load(self):
        player = _player(mining_level=SKILLCAPE_LEVEL)
        player.pop("capes", None)
        player["config_version"] = 88

        migrated = migrate_loaded_data(player, ORE_DATA)
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["capes"]["keepsake_skill"], "mining")

    def test_an_unknown_keepsake_is_sanitized_away(self):
        player = _player()
        player["capes"] = {"version": 1, "keepsake_skill": "wizardry"}
        self.assertEqual(refresh_capes_pure(player)["capes"]["keepsake_skill"], "")


if __name__ == "__main__":
    unittest.main()
