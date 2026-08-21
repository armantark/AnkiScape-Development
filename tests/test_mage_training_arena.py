from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import pkg_alias  # noqa: F401
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
from ankiscape.data.achievement_diary_data import ACHIEVEMENT_DIARY_CATALOG
from ankiscape.data.mage_training_arena_data import (
    MAGE_TRAINING_ARENA_ACTIVITY_ID,
    MAGE_TRAINING_ARENA_ENCHANTMENT_REWARD_RUNES,
    MAGE_TRAINING_ARENA_GRAVEYARD_REWARD_RUNES,
    MAGE_TRAINING_ARENA_POINT_CAPS,
    MAGE_TRAINING_ARENA_REWARDS,
    MAGE_TRAINING_ARENA_ROOM_IDS,
)
from ankiscape.logic.achievement_diary_logic import refresh_achievement_diaries_pure
from ankiscape.logic.cadence_coverage import cadence_coverage_rows_pure
from ankiscape.logic.mage_training_arena_logic import (
    apply_mage_training_arena_command_pure,
    apply_mage_training_arena_review_pure,
    default_mage_training_arena_state_pure,
    enter_mage_training_arena_pure,
    mage_training_arena_view_pure,
    purchase_mage_training_arena_reward_pure,
    sanitize_mage_training_arena_state_pure,
    set_mage_training_arena_policy_pure,
)
from ankiscape.logic_pure.logic_pure import can_equip_item_pure, equip_item_pure
from ankiscape.runtime.runtime_actions import RuntimeActionContext, handle_utility_answer


ROOT = Path(__file__).resolve().parents[1]


def _player(level: int = 99):
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data["magic_level"] = level
    data["defense_level"] = level
    data["constitution_level"] = level
    data["combat_lifepoints"] = max(100, level * 10)
    for item in (
        "Air rune",
        "Water rune",
        "Earth rune",
        "Fire rune",
        "Law rune",
        "Nature rune",
        "Cosmic rune",
        "Blood rune",
        "Death rune",
    ):
        data["inventory"][item] = 100_000
    return data


def _entered(room_policy: str = "auto", *, level: int = 99):
    data = _player(level)
    data, ok, info = set_mage_training_arena_policy_pure(
        data,
        {
            "room_policy": room_policy,
            "approach": "fast_rewards",
            "reward_goal": "bones_to_peaches",
        },
    )
    if not ok:
        raise AssertionError(info)
    data, ok, info = enter_mage_training_arena_pure(data)
    if not ok:
        raise AssertionError(info)
    return data


def _checkpoints(data, count: int, rng=lambda: 0.5):
    results = []
    for _ in range(10_000):
        data, ok, result = apply_mage_training_arena_review_pure(data, rng)
        if not ok:
            raise AssertionError(result)
        if result.get("checkpoint"):
            results.append(result)
            if len(results) == count:
                return data, results
    raise AssertionError(f"only reached {len(results)} of {count} checkpoints")


def _earn_costs_through_play(data, costs):
    review_counts = {}
    for room_id, target in costs.items():
        if target <= data["mage_training_arena"]["wallets"][room_id]:
            continue
        data, ok, info = set_mage_training_arena_policy_pure(
            data,
            {
                "room_policy": room_id,
                "approach": "fast_rewards",
                "reward_goal": "master_wand",
            },
        )
        if not ok:
            raise AssertionError(info)
        data, ok, info = enter_mage_training_arena_pure(data)
        if not ok:
            raise AssertionError(info)
        reviews = 0
        while data["mage_training_arena"]["wallets"][room_id] < target:
            data, ok, result = apply_mage_training_arena_review_pure(
                data, lambda: 0.99
            )
            if not ok:
                raise AssertionError(result)
            reviews += 1
            if reviews > 50_000:
                raise AssertionError(f"{room_id} did not fund {target} points")
        review_counts[room_id] = review_counts.get(room_id, 0) + reviews
        data, ok, info = apply_mage_training_arena_command_pure(data, "leave")
        if not ok:
            raise AssertionError(info)
    return data, review_counts


def _buy_reward_through_play(data, reward_id, observed_reviews):
    reward = next(row for row in MAGE_TRAINING_ARENA_REWARDS if row.id == reward_id)
    if reward.required_item and data["inventory"].get(reward.required_item, 0) <= 0:
        prerequisite = next(
            row for row in MAGE_TRAINING_ARENA_REWARDS
            if row.output_item == reward.required_item
        )
        data = _buy_reward_through_play(data, prerequisite.id, observed_reviews)
    data, reviews = _earn_costs_through_play(data, reward.cost_map())
    for room_id, count in reviews.items():
        observed_reviews[room_id] = observed_reviews.get(room_id, 0) + count
    before_wallets = dict(data["mage_training_arena"]["wallets"])
    before_output = (
        data["inventory"].get(reward.output_item, 0) if reward.output_item else 0
    )
    data, ok, info = purchase_mage_training_arena_reward_pure(data, reward.id)
    if not ok:
        raise AssertionError(info)
    if reward.output_item:
        if data["inventory"][reward.output_item] != before_output + reward.output_count:
            raise AssertionError(f"{reward.id} output did not arrive")
    for room_id, cost in reward.cost_map().items():
        if data["mage_training_arena"]["wallets"][room_id] != before_wallets[room_id] - cost:
            raise AssertionError(f"{reward.id} did not spend its {room_id} price")
    return data


class MageTrainingArenaDataAndEntryTests(unittest.TestCase):
    def test_activity_items_asset_and_point_caps_are_registered(self):
        self.assertGreaterEqual(CURRENT_CONFIG_VERSION, 93)
        self.assertIn(MAGE_TRAINING_ARENA_ACTIVITY_ID, UTILITY_ACTIVITY_DATA)
        activity = UTILITY_ACTIVITY_DATA[MAGE_TRAINING_ARENA_ACTIVITY_ID]
        self.assertEqual(activity["skill_requirements"], {"magic": 7})
        self.assertTrue(Path(activity["icon_path"]).is_file())
        self.assertEqual(
            MAGE_TRAINING_ARENA_POINT_CAPS,
            {
                "telekinetic": 4_000,
                "alchemist": 8_000,
                "enchantment": 16_000,
                "graveyard": 4_000,
            },
        )
        for item in (
            "Progress hat",
            "Beginner wand",
            "Apprentice wand",
            "Teacher wand",
            "Master wand",
            "Mages' book",
            "Infinity gloves",
            "Infinity hat",
            "Infinity top",
            "Infinity bottoms",
            "Infinity boots",
        ):
            self.assertIn(item, EXTRA_ITEM_DATA)
            self.assertIn(item, EQUIPMENT_DATA)
        for wand in ("Beginner wand", "Apprentice wand", "Teacher wand", "Master wand"):
            self.assertEqual(EQUIPMENT_DATA[wand].slot, "weapon")
            self.assertTrue(Path(EXTRA_ITEM_IMAGES[wand]).is_file())
        self.assertEqual(EQUIPMENT_DATA["Master wand"].bonuses.attack_magic, 20)
        self.assertEqual(EQUIPMENT_DATA["Master wand"].bonuses.magic_damage, 10)
        self.assertEqual(EQUIPMENT_DATA["Mages' book"].source_item_id, 6889)
        self.assertEqual(EQUIPMENT_DATA["Mages' book"].slot, "shield")
        self.assertEqual(EQUIPMENT_DATA["Mages' book"].bonuses.attack_magic, 15)
        self.assertEqual(EQUIPMENT_DATA["Mages' book"].bonuses.defence_magic, 15)
        self.assertEqual(
            EQUIPMENT_DATA["Infinity top"].skill_requirements,
            (("defense", 50), ("magic", 25)),
        )
        self.assertEqual(EQUIPMENT_DATA["Infinity top"].bonuses.attack_magic, 22)
        self.assertEqual(EQUIPMENT_DATA["Infinity top"].bonuses.defence_magic, 22)

        provenance = json.loads((ROOT / "assets_provenance.json").read_text(encoding="utf-8"))
        row = provenance["activityicons/mage_training_arena.png"]
        self.assertEqual(row["file_title"], "Infinity hat.png")
        self.assertLess(row["timestamp"], "2012-11-20T00:00:00Z")
        for wand in ("beginner", "apprentice", "teacher", "master"):
            asset = provenance[f"activityitems/mage_training_arena_{wand}_wand.png"]
            self.assertLess(asset["timestamp"], "2012-11-20T00:00:00Z")
        for item in (
            "Mages' book",
            "Infinity gloves",
            "Infinity hat",
            "Infinity top",
            "Infinity bottoms",
            "Infinity boots",
        ):
            self.assertTrue(Path(EXTRA_ITEM_IMAGES[item]).is_file())
            slug = item.lower().replace(" ", "_").replace("'", "")
            asset = provenance[f"activityitems/mage_training_arena_{slug}.png"]
            self.assertLess(asset["timestamp"], "2012-11-20T00:00:00Z")

    def test_reward_prices_match_the_pinned_period_shop_table(self):
        self.assertEqual(
            {reward.id: reward.costs for reward in MAGE_TRAINING_ARENA_REWARDS},
            {
                "infinity_gloves": (175, 225, 1_500, 175),
                "infinity_hat": (350, 400, 3_000, 350),
                "infinity_top": (400, 450, 4_000, 400),
                "infinity_bottoms": (450, 500, 5_000, 450),
                "infinity_boots": (120, 120, 1_200, 120),
                "battlestaff": (1, 2, 20, 2),
                "beginner_wand": (30, 30, 300, 30),
                "apprentice_wand": (60, 60, 600, 60),
                "teacher_wand": (150, 200, 1_500, 150),
                "master_wand": (240, 240, 2_400, 240),
                "mages_book": (500, 550, 6_000, 500),
                "bones_to_peaches": (200, 300, 2_000, 200),
                "mist_rune": (1, 1, 15, 1),
                "dust_rune": (1, 1, 15, 1),
                "mud_rune": (1, 1, 15, 1),
                "smoke_rune": (1, 1, 15, 1),
                "steam_rune": (1, 1, 15, 1),
                "lava_rune": (1, 1, 15, 1),
                "cosmic_rune": (0, 0, 5, 0),
                "chaos_rune": (0, 1, 5, 1),
                "nature_rune": (0, 1, 0, 1),
                "death_rune": (2, 1, 20, 1),
                "law_rune": (2, 0, 0, 0),
                "soul_rune": (2, 2, 25, 2),
                "blood_rune": (2, 2, 25, 2),
            },
        )
        definitions = {item.storage_key for item in ITEM_DEFINITIONS}
        self.assertTrue(
            all(
                not reward.output_item or reward.output_item in definitions
                for reward in MAGE_TRAINING_ARENA_REWARDS
            )
        )

    def test_cutoff_magic_equipment_requirements_use_the_shared_gate(self):
        player = _player()
        player["defense_level"] = 49
        player["magic_level"] = 99
        allowed, reason = can_equip_item_pure("Infinity top", EQUIPMENT_DATA, player)
        self.assertFalse(allowed)
        self.assertEqual(reason, "Requires level 50 Defense")

        player["defense_level"] = 50
        player["magic_level"] = 59
        allowed, reason = can_equip_item_pure("Mages' book", EQUIPMENT_DATA, player)
        self.assertFalse(allowed)
        self.assertEqual(reason, "Requires level 60 Magic")

        player["magic_level"] = 60
        allowed, reason = can_equip_item_pure("Mages' book", EQUIPMENT_DATA, player)
        self.assertTrue(allowed, reason)

    def test_cadence_coverage_names_all_four_activity_owned_room_profiles(self):
        row = next(
            row
            for row in cadence_coverage_rows_pure()
            if row["action_id"] == MAGE_TRAINING_ARENA_ACTIVITY_ID
        )
        self.assertEqual(row["mode"], "activity_group")
        self.assertEqual(
            row["includes"],
            tuple(
                f"mage_training_arena:{room_id}"
                for room_id in MAGE_TRAINING_ARENA_ROOM_IDS
            ),
        )
        self.assertIn("registered placeholder", row["source_reason"])

    def test_level_seven_enters_once_receives_hat_and_credits_the_diary_counter(self):
        blocked, ok, info = enter_mage_training_arena_pure(_player(6))
        self.assertFalse(ok)
        self.assertIn("Magic level 7", info["reason"])
        self.assertEqual(blocked["mage_training_arena"]["entries"], 0)

        entered, ok, info = enter_mage_training_arena_pure(_player(7))
        self.assertTrue(ok, info)
        self.assertEqual(entered["mage_training_arena"]["entries"], 1)
        self.assertEqual(entered["inventory"]["Progress hat"], 1)
        self.assertEqual(
            entered["activity_session"],
            {"active_id": MAGE_TRAINING_ARENA_ACTIVITY_ID},
        )
        enchant = next(
            row for row in mage_training_arena_view_pure(entered)["room_options"]
            if row["id"] == "enchantment"
        )
        telekinetic = next(
            row for row in mage_training_arena_view_pure(entered)["room_options"]
            if row["id"] == "telekinetic"
        )
        self.assertTrue(enchant["runnable"])
        self.assertFalse(telekinetic["runnable"])

        task = next(
            task
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
            if task.id == "miscellaneous_miscellaneous_mage_training_arena"
        )
        self.assertEqual(task.conditions[0].kind, "counter")
        self.assertEqual(task.conditions[0].key, "mage_training_arena.entries")
        refreshed, newly = refresh_achievement_diaries_pure(entered)
        self.assertIn(task.id, newly)
        self.assertIn(task.id, refreshed["achievement_diaries"]["completed_tasks"])

    def test_entry_refuses_another_persistent_activity(self):
        data = _player()
        data["activity_session"] = {"active_id": "clan_wars"}
        _, ok, info = enter_mage_training_arena_pure(data)
        self.assertFalse(ok)
        self.assertIn("persistent activity", info["reason"])


class MageTrainingArenaRoomMechanicsTests(unittest.TestCase):
    def test_each_room_earns_only_its_own_points_through_the_real_handler(self):
        observed = {}
        for room_id in MAGE_TRAINING_ARENA_ROOM_IDS:
            with self.subTest(room=room_id):
                data, results = _checkpoints(_entered(room_id), 1)
                result = results[0]
                observed[room_id] = result["points_gained"]
                self.assertEqual(result["room"], room_id)
                self.assertGreater(result["points_gained"], 0)
                for other in MAGE_TRAINING_ARENA_ROOM_IDS:
                    expected = result["points_gained"] if other == room_id else 0
                    self.assertEqual(data["mage_training_arena"]["wallets"][other], expected)
        self.assertEqual(observed, {"telekinetic": 2, "alchemist": 1, "enchantment": 1, "graveyard": 1})

    def test_alchemist_checkpoint_uses_full_high_alchemy_runes_and_xp(self):
        data = _entered("alchemist")
        before_nature = data["inventory"]["Nature rune"]
        before_fire = data["inventory"]["Fire rune"]
        data, results = _checkpoints(data, 1)
        result = results[0]
        self.assertEqual(before_nature - data["inventory"]["Nature rune"], 3)
        self.assertEqual(before_fire - data["inventory"]["Fire rune"], 25)
        self.assertEqual(result["alchemy_casts"], 5)
        self.assertEqual(result["magic_xp"], 525.0)

    def test_telekinetic_fifth_maze_bonus_and_enchantment_thresholds_occur(self):
        telekinetic, results = _checkpoints(_entered("telekinetic"), 5)
        self.assertEqual([row["points_gained"] for row in results], [2, 2, 2, 2, 10])
        self.assertTrue(results[-1]["five_maze_bonus"])
        self.assertEqual(telekinetic["mage_training_arena"]["wallets"]["telekinetic"], 18)

        enchantment, results = _checkpoints(_entered("enchantment"), 20, rng=lambda: 0.99)
        self.assertGreater(results[9]["points_gained"], 1)
        self.assertIn("rune_reward", results[19])
        reward_item = next(iter(results[19]["rune_reward"]))
        self.assertIn(reward_item, MAGE_TRAINING_ARENA_ENCHANTMENT_REWARD_RUNES)
        self.assertEqual(results[19]["rune_reward"][reward_item], 3)
        self.assertGreater(enchantment["magic_exp"], 0)

    def test_graveyard_tracks_the_bone_cycle_and_uses_the_full_reward_set(self):
        data, results = _checkpoints(_entered("graveyard"), 2, rng=lambda: 0.99)
        self.assertEqual(results[0]["bones_collected"], 10)
        self.assertGreater(results[1]["bones_collected"], 0)
        reward_item = next(iter(results[0]["rune_reward"]))
        self.assertIn(reward_item, MAGE_TRAINING_ARENA_GRAVEYARD_REWARD_RUNES)
        self.assertEqual(data["mage_training_arena"]["wallets"]["graveyard"], 2)

    def test_graveyard_death_returns_to_lobby_and_loses_only_graveyard_points(self):
        data = _entered("graveyard")
        data["combat_lifepoints"] = 20
        data["mage_training_arena"]["wallets"] = {
            "telekinetic": 40,
            "alchemist": 50,
            "enchantment": 60,
            "graveyard": 7,
        }
        died, ok, result = apply_mage_training_arena_review_pure(data, lambda: 0.0)
        self.assertTrue(ok, result)
        self.assertTrue(result["died"])
        self.assertEqual(result["points_lost"], 7)
        self.assertEqual(
            died["mage_training_arena"]["wallets"],
            {"telekinetic": 40, "alchemist": 50, "enchantment": 60, "graveyard": 0},
        )
        self.assertFalse(died["mage_training_arena"]["active"])
        self.assertEqual(died["activity_session"]["active_id"], "")
        self.assertEqual(died["combat_lifepoints"], 990)
        self.assertNotEqual(died["equipment"], {"destroyed": True})

    def test_falling_bones_roll_only_on_a_checkpoint_and_converted_fruit_heals(self):
        data = _entered("graveyard")
        data["combat_lifepoints"] = 500
        first, ok, result = apply_mage_training_arena_review_pure(data, lambda: 0.0)
        self.assertTrue(ok, result)
        self.assertTrue(result["checkpoint"])
        self.assertEqual(result["fruit_eaten"], 1)
        self.assertEqual(first["combat_lifepoints"], 500)

        before = first["combat_lifepoints"]
        waiting, ok, result = apply_mage_training_arena_review_pure(first, lambda: 0.0)
        self.assertTrue(ok, result)
        self.assertFalse(result["checkpoint"])
        self.assertEqual(waiting["combat_lifepoints"], before)

    def test_unlocked_bones_to_peaches_heals_eighty_after_falling_bone_damage(self):
        data = _entered("graveyard")
        data["mage_training_arena"]["completed"] = True
        data["combat_lifepoints"] = 500
        after, ok, result = apply_mage_training_arena_review_pure(data, lambda: 0.0)
        self.assertTrue(ok, result)
        self.assertEqual(result["fruit"], "peaches")
        self.assertEqual(result["fruit_eaten"], 1)
        self.assertEqual(after["combat_lifepoints"], 560)

    def test_missing_runes_pause_the_selected_room_without_mutation(self):
        data = _entered("telekinetic")
        data["inventory"]["Law rune"] = 0
        before = copy.deepcopy(data)
        unchanged, ok, result = apply_mage_training_arena_review_pure(data)
        self.assertFalse(ok)
        self.assertIn("Law rune", result["reason"])
        self.assertEqual(unchanged, before)


class MageTrainingArenaRewardAndPolicyTests(unittest.TestCase):
    def test_every_cutoff_reward_purchases_atomically_and_wearables_equip(self):
        for reward in MAGE_TRAINING_ARENA_REWARDS:
            with self.subTest(reward=reward.id):
                data = _player()
                data["mage_training_arena"]["wallets"] = reward.cost_map()
                if reward.required_item:
                    data["inventory"][reward.required_item] = 1
                before_output = (
                    data["inventory"].get(reward.output_item, 0)
                    if reward.output_item
                    else 0
                )
                bought, ok, info = purchase_mage_training_arena_reward_pure(
                    data,
                    reward.id,
                )
                self.assertTrue(ok, info)
                self.assertEqual(
                    bought["mage_training_arena"]["wallets"],
                    {room_id: 0 for room_id in MAGE_TRAINING_ARENA_ROOM_IDS},
                )
                self.assertEqual(
                    bought["mage_training_arena"]["purchases"][reward.id],
                    1,
                )
                if reward.required_item:
                    self.assertEqual(bought["inventory"][reward.required_item], 0)
                if reward.output_item:
                    self.assertEqual(
                        bought["inventory"][reward.output_item],
                        before_output + reward.output_count,
                    )
                if reward.unlock:
                    self.assertTrue(bought["mage_training_arena"]["completed"])
                if reward.output_item in EQUIPMENT_DATA:
                    inventory, equipment, equipped = equip_item_pure(
                        reward.output_item,
                        bought["inventory"],
                        bought["equipment"],
                        EQUIPMENT_DATA,
                    )
                    self.assertTrue(equipped)
                    self.assertEqual(
                        equipment[EQUIPMENT_DATA[reward.output_item].slot],
                        reward.output_item,
                    )
                    self.assertEqual(
                        inventory[reward.output_item],
                        bought["inventory"][reward.output_item] - 1,
                    )

    def test_battlestaff_price_is_earned_through_all_four_rooms(self):
        observed_reviews = {}
        bought = _buy_reward_through_play(
            _player(),
            "battlestaff",
            observed_reviews,
        )
        self.assertEqual(bought["mage_training_arena"]["purchases"]["battlestaff"], 1)
        self.assertEqual(bought["inventory"]["Battlestaff"], 1)
        self.assertEqual(set(observed_reviews), set(MAGE_TRAINING_ARENA_ROOM_IDS))
        self.assertTrue(all(count > 0 for count in observed_reviews.values()))

    def test_wand_upgrade_cannot_skip_its_predecessor(self):
        reward = next(row for row in MAGE_TRAINING_ARENA_REWARDS if row.id == "master_wand")
        data = _player()
        data["mage_training_arena"]["wallets"] = reward.cost_map()
        _, ok, info = purchase_mage_training_arena_reward_pure(data, reward.id)
        self.assertFalse(ok)
        self.assertIn("Teacher wand", info["reason"])

    def test_policy_commands_lock_mid_session_and_the_view_owns_all_flags(self):
        data = _player()
        planned, ok, info = set_mage_training_arena_policy_pure(
            data,
            {"room_policy": "enchantment", "approach": "conserve_runes", "reward_goal": "cosmic_rune"},
        )
        self.assertTrue(ok, info)
        idle = mage_training_arena_view_pure(planned)
        self.assertTrue(idle["can_enter"])
        self.assertTrue(idle["policy_controls_enabled"])
        self.assertEqual(idle["primary_label"], "Enter Arena")
        self.assertFalse(idle["leave_visible"])

        entered, ok, _ = enter_mage_training_arena_pure(planned)
        self.assertTrue(ok)
        active = mage_training_arena_view_pure(entered)
        self.assertFalse(active["policy_controls_enabled"])
        self.assertTrue(active["can_review"])
        self.assertTrue(active["leave_visible"])
        self.assertEqual(active["selected_room"], "enchantment")
        _, ok, info = set_mage_training_arena_policy_pure(entered, {"room_policy": "graveyard"})
        self.assertFalse(ok)
        self.assertIn("Leave the Arena", info["reason"])

    def test_a_funded_auto_goal_pauses_cleanly_instead_of_erroring(self):
        data = _entered("auto")
        reward = next(row for row in MAGE_TRAINING_ARENA_REWARDS if row.id == "bones_to_peaches")
        data["mage_training_arena"]["wallets"] = reward.cost_map()
        paused, ok, result = apply_mage_training_arena_review_pure(data)
        self.assertTrue(ok, result)
        self.assertTrue(result["goal_ready"])
        self.assertTrue(result["terminal"])
        self.assertFalse(result["advanced"])
        self.assertTrue(paused["mage_training_arena"]["active"])
        self.assertEqual(paused["mage_training_arena"]["current_room"], "")

    def test_command_router_covers_plan_entry_purchase_leave_and_unknown(self):
        data = _player()
        planned, ok, _ = apply_mage_training_arena_command_pure(
            data,
            "set_policy",
            {"room_policy": "enchantment", "approach": "fast_rewards", "reward_goal": "cosmic_rune"},
        )
        self.assertTrue(ok)
        entered, ok, _ = apply_mage_training_arena_command_pure(planned, "enter")
        self.assertTrue(ok)
        left, ok, _ = apply_mage_training_arena_command_pure(entered, "leave")
        self.assertTrue(ok)
        _, ok, info = apply_mage_training_arena_command_pure(left, "unknown")
        self.assertFalse(ok)
        self.assertIn("Unknown", info["reason"])


class MageTrainingArenaPersistenceRuntimeAndUiTests(unittest.TestCase):
    def test_legacy_unlock_and_interrupted_room_migrate_into_current_schema(self):
        old = _player()
        old["config_version"] = 89
        old["mage_training_arena"] = {
            "completed": True,
            "active": True,
            "entries": 3,
            "current_room": "enchantment",
            "wallets": {"telekinetic": 2, "enchantment": 4},
        }
        old["activity_session"] = {"active_id": MAGE_TRAINING_ARENA_ACTIVITY_ID}
        migrated = migrate_loaded_data(old, ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        state = migrated["mage_training_arena"]
        self.assertTrue(state["completed"])
        self.assertTrue(state["active"])
        self.assertEqual(state["entries"], 3)
        self.assertEqual(state["wallets"]["telekinetic"], 2)
        self.assertEqual(state["wallets"]["enchantment"], 4)
        self.assertEqual(migrated["activity_session"]["active_id"], MAGE_TRAINING_ARENA_ACTIVITY_ID)

    def test_sanitizer_clamps_wallets_and_repairs_invalid_policy(self):
        clean = sanitize_mage_training_arena_state_pure(
            {
                "room_policy": "dragonstone_only",
                "approach": "balanced",
                "reward_goal": "all_rewards",
                "wallets": {room: 999_999 for room in MAGE_TRAINING_ARENA_ROOM_IDS},
            }
        )
        self.assertEqual(clean["room_policy"], "auto")
        self.assertEqual(clean["approach"], "fast_rewards")
        self.assertEqual(clean["reward_goal"], "bones_to_peaches")
        self.assertEqual(clean["wallets"], MAGE_TRAINING_ARENA_POINT_CAPS)

    def test_runtime_dispatches_every_room_and_observes_each_point_wallet(self):
        observed = {}
        for room_id in MAGE_TRAINING_ARENA_ROOM_IDS:
            with self.subTest(room=room_id):
                player = _entered(room_id)
                calls = {"errors": [], "saves": 0}
                ctx = RuntimeActionContext(
                    player_data=player,
                    random_random=lambda: 0.5,
                    show_error_message=lambda title, message: calls["errors"].append((title, message)),
                    deactivate_current_skill=lambda: None,
                    award_skill_exp=lambda _key, amount: amount,
                    award_hidden_skill_exp=lambda *_args: None,
                    level_up_check=lambda *_args: None,
                    check_achievements=lambda *_args: None,
                    save_player_data=lambda: calls.__setitem__("saves", calls["saves"] + 1),
                    refresh_skill_availability=lambda: None,
                    show_exp=lambda *_args: None,
                    show_activity_gain=lambda *_args: None,
                    implemented_exp_keys_snapshot=lambda: {},
                    show_quest_exp_delta=lambda *_args: None,
                )
                for _ in range(100):
                    self.assertTrue(handle_utility_answer(ctx))
                    if player["mage_training_arena"]["wallets"][room_id]:
                        break
                self.assertEqual(calls["errors"], [])
                observed[room_id] = player["mage_training_arena"]["wallets"][room_id]
        self.assertEqual(
            observed,
            {"telekinetic": 2, "alchemist": 1, "enchantment": 1, "graveyard": 1},
        )

    def test_runtime_dispatches_a_real_room_checkpoint_and_persists(self):
        player = _entered("enchantment")
        calls = {"saves": 0, "activity": [], "xp": [], "errors": [], "deactivated": False}
        ctx = RuntimeActionContext(
            player_data=player,
            random_random=lambda: 0.5,
            show_error_message=lambda title, message: calls["errors"].append((title, message)),
            deactivate_current_skill=lambda: calls.__setitem__("deactivated", True),
            award_skill_exp=lambda _key, amount: amount,
            award_hidden_skill_exp=lambda *_args: None,
            level_up_check=lambda *_args: None,
            check_achievements=lambda *_args: None,
            save_player_data=lambda: calls.__setitem__("saves", calls["saves"] + 1),
            refresh_skill_availability=lambda: None,
            show_exp=lambda amount: calls["xp"].append(float(amount)),
            show_activity_gain=lambda message: calls["activity"].append(str(message)),
            implemented_exp_keys_snapshot=lambda: {},
            show_quest_exp_delta=lambda *_args: None,
        )
        self.assertTrue(handle_utility_answer(ctx))
        self.assertEqual(calls["errors"], [])
        self.assertEqual(calls["saves"], 1)
        self.assertGreater(player["mage_training_arena"]["wallets"]["enchantment"], 0)
        self.assertGreater(calls["xp"][0], 0)
        self.assertIn("Enchanting Chamber", calls["activity"][0])

        self.assertTrue(handle_utility_answer(ctx))
        telemetry = player["action_telemetry"]["actions"][
            f"utility:{MAGE_TRAINING_ARENA_ACTIVITY_ID}"
        ]
        self.assertEqual(telemetry["attempts"], 1)
        self.assertEqual(telemetry["cadence_waits"], 1)

    def test_runtime_deactivates_cleanly_when_the_goal_is_funded(self):
        player = _entered("auto")
        reward = next(row for row in MAGE_TRAINING_ARENA_REWARDS if row.id == "bones_to_peaches")
        player["mage_training_arena"]["wallets"] = reward.cost_map()
        calls = {"saves": 0, "activity": [], "errors": [], "deactivated": False}
        ctx = RuntimeActionContext(
            player_data=player,
            random_random=lambda: 0.5,
            show_error_message=lambda title, message: calls["errors"].append((title, message)),
            deactivate_current_skill=lambda: calls.__setitem__("deactivated", True),
            award_skill_exp=lambda _key, amount: amount,
            award_hidden_skill_exp=lambda *_args: None,
            level_up_check=lambda *_args: None,
            check_achievements=lambda *_args: None,
            save_player_data=lambda: calls.__setitem__("saves", calls["saves"] + 1),
            refresh_skill_availability=lambda: None,
            show_exp=lambda *_args: None,
            show_activity_gain=lambda message: calls["activity"].append(str(message)),
            implemented_exp_keys_snapshot=lambda: {},
            show_quest_exp_delta=lambda *_args: None,
        )
        self.assertTrue(handle_utility_answer(ctx))
        self.assertEqual(calls["errors"], [])
        self.assertTrue(calls["deactivated"])
        self.assertEqual(calls["saves"], 1)
        self.assertIn("funded", calls["activity"][0])

    def test_again_is_non_productive_and_keeps_room_state_exactly(self):
        data = _entered("enchantment")
        before = json.loads(json.dumps(data["mage_training_arena"]))
        unchanged, ok, result = apply_mage_training_arena_review_pure(data, productive=False)
        self.assertTrue(ok, result)
        self.assertFalse(result["advanced"])
        self.assertEqual(unchanged["mage_training_arena"], before)


try:
    from aqt.qt import QApplication
    from ankiscape.ui.mage_training_arena_panel import HAS_QT, MageTrainingArenaPanel
except Exception:
    QApplication = None
    HAS_QT = False
    MageTrainingArenaPanel = None


@unittest.skipUnless(HAS_QT, "Qt lane only")
class MageTrainingArenaQtPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_panel_activates_layout_before_the_560_point_geometry_probe(self):
        panel = MageTrainingArenaPanel(_player())
        panel.show()
        panel.resize(760, 560)
        for _ in range(4):
            QApplication.processEvents()
        self.assertLessEqual(panel.sizeHint().height(), 560)
        self.assertLessEqual(panel.layout().minimumSize().height(), 560)
        self.assertEqual(panel.primary_button.text(), "Enter Arena")
        self.assertTrue(panel.wallets.wordWrap())
        panel.close()


if __name__ == "__main__":
    unittest.main()
