from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

from tests.quest_action_proofs.test_writer_ownership import _production_store_sites
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
import ankiscape.core.storage_pure as storage_pure
from ankiscape.core.storage_pure import (
    CURRENT_CONFIG_VERSION, default_player_data, migrate_loaded_data,
)
from ankiscape.data.quest_action_proof_data import (
    BIOHAZARD_CAULDRON_ACTION,
    DO_NO_EVIL_MAMULET_MOULD_PROOF,
    FREMENNIK_ISLES_YAK_HIDE_PROOF,
    MOURNER_FOOD_STORES_PROOF,
    THAKKRAD_CURED_YAK_HIDE_PROOF,
)
from ankiscape.logic.shop_logic import apply_shop_buy_pure, apply_shop_service_pure, rollback_shop_event_pure
from ankiscape.logic_pure.logic_pure_quest import apply_quest_progress_pure, quest_current_stage_blockers_pure
from ankiscape.logic_pure.quest_action_proofs import (
    quest_action_proof_completed_pure,
    quest_action_proofs_for_reachable_events_pure,
    record_quest_stage_action_proofs_pure,
    record_runtime_quest_action_proofs_pure,
    retract_shop_event_quest_action_proofs_pure,
    sanitize_quest_action_proofs_pure,
)
from ankiscape.runtime.runtime_actions import handle_crafting_answer
from ankiscape.tools.quest_action_proof_reachability import reachable_quest_action_proof_events
from tests.quest_action_proof_helpers import quest_required_action_proofs_for_quest
from tests.test_combat_quest_gate import _answer_review, _maxed_player_for_quest
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package
from tests.test_runtime_actions import _context


class TestQuestActionProofStore(unittest.TestCase):
    def test_store_is_unique_global_membership(self):
        player = {"quest_action_proofs": ["proof-b", "proof-a", "proof-b", 7]}

        self.assertEqual(
            sanitize_quest_action_proofs_pure(player["quest_action_proofs"]),
            ["proof-a", "proof-b"],
        )
        self.assertTrue(quest_action_proof_completed_pure(player, "proof-a"))
        self.assertFalse(quest_action_proof_completed_pure(player, "proof-c"))
        self.assertFalse(
            record_runtime_quest_action_proofs_pure(
                player,
                "crafting",
                "unmapped_target",
            )
        )

    def test_shop_retraction_preserves_non_shop_proofs_without_backfill(self):
        event = {
            "event_id": "shop_evt_2",
            "type": "service",
            "service_id": "thakkrad_cure_yak_hide",
        }
        player = {
            "quest_action_proofs": [
                THAKKRAD_CURED_YAK_HIDE_PROOF,
                FREMENNIK_ISLES_YAK_HIDE_PROOF,
                MOURNER_FOOD_STORES_PROOF,
            ],
            "shop_events": [
                {
                    "event_id": "shop_evt_1",
                    "type": "buy",
                    "row_id": "hamabs_crafting_emporium:3:4020",
                },
                event,
            ],
        }
        before_events = copy.deepcopy(player["shop_events"])

        self.assertTrue(retract_shop_event_quest_action_proofs_pure(player, event))

        self.assertEqual(
            player["quest_action_proofs"],
            sorted((FREMENNIK_ISLES_YAK_HIDE_PROOF, MOURNER_FOOD_STORES_PROOF)),
        )
        self.assertEqual(player["shop_events"], before_events)

    def test_runtime_bindings_are_idempotent_and_support_genuine_sequences(self):
        player = {"quest_action_proofs": []}

        self.assertFalse(
            record_runtime_quest_action_proofs_pure(
                player,
                "crafting",
                "leather_yakhide_armour_10824",
            )
        )
        self.assertEqual(player["quest_action_proofs"], [])
        self.assertTrue(
            record_runtime_quest_action_proofs_pure(
                player,
                "shop_service",
                "thakkrad_cure_yak_hide",
            )
        )
        self.assertTrue(
            record_runtime_quest_action_proofs_pure(
                player,
                "crafting",
                "leather_yakhide_armour_10824",
            )
        )
        self.assertFalse(
            record_runtime_quest_action_proofs_pure(
                player,
                "crafting",
                "leather_yakhide_armour_10824",
            )
        )
        self.assertEqual(
            player["quest_action_proofs"],
            sorted((THAKKRAD_CURED_YAK_HIDE_PROOF, FREMENNIK_ISLES_YAK_HIDE_PROOF)),
        )

    def test_reachability_sources_obey_the_same_multi_step_rules(self):
        crafting_only = quest_action_proofs_for_reachable_events_pure(
            (),
            {("crafting", "leather_yakhide_armour_10824")},
        )
        self.assertNotIn(FREMENNIK_ISLES_YAK_HIDE_PROOF, crafting_only)

        reachable = quest_action_proofs_for_reachable_events_pure(
            (),
            {
                ("shop_buy", "hamabs_crafting_emporium:3:4020"),
                ("shop_service", "thakkrad_cure_yak_hide"),
                ("crafting", "leather_yakhide_armour_10824"),
            },
        )
        self.assertIn(DO_NO_EVIL_MAMULET_MOULD_PROOF, reachable)
        self.assertIn(FREMENNIK_ISLES_YAK_HIDE_PROOF, reachable)

        wrong_row = reachable_quest_action_proof_events(
            (),
            (),
            {"Ring mould": {"shop:hamabs_crafting_emporium"}},
        )
        self.assertNotIn(("shop_buy", "hamabs_crafting_emporium:3:4020"), wrong_row)
        exact_row = reachable_quest_action_proof_events(
            (),
            (),
            {"M'amulet mould": {"shop:hamabs_crafting_emporium"}},
        )
        self.assertIn(("shop_buy", "hamabs_crafting_emporium:3:4020"), exact_row)

    def test_quest_stage_action_records_exact_and_cross_quest_proofs(self):
        player = {"quest_action_proofs": []}

        changed = record_quest_stage_action_proofs_pure(
            player,
            "biohazard",
            (BIOHAZARD_CAULDRON_ACTION,),
        )

        self.assertTrue(changed)
        self.assertEqual(
            player["quest_action_proofs"],
            sorted((BIOHAZARD_CAULDRON_ACTION, MOURNER_FOOD_STORES_PROOF)),
        )

    def test_old_saves_start_empty_without_telemetry_inventory_or_local_backfill(self):
        legacy = {
            "config_version": 121,
            "inventory": {"M'amulet mould": 1, "Cured yak-hide": 2},
            "action_telemetry": {
                "by_action": {
                    "crafting:leather_yakhide_armour": {"successes": 99},
                },
            },
            "quest_stage_actions": {
                "biohazard": [BIOHAZARD_CAULDRON_ACTION],
            },
            "quest_action_proofs": [
                DO_NO_EVIL_MAMULET_MOULD_PROOF,
                MOURNER_FOOD_STORES_PROOF,
            ],
        }

        migrated = migrate_loaded_data(legacy, ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["quest_action_proofs"], [])
        self.assertNotIn("quest_stage_actions", migrated)

    def test_v122_proofs_survive_upgrade_and_legacy_stage_actions_are_dropped(self):
        current = {
            "config_version": 122,
            "quest_stage_actions": {"biohazard": [BIOHAZARD_CAULDRON_ACTION]},
            "quest_action_proofs": ["proof-b", "proof-a", "proof-b", None],
        }

        migrated = migrate_loaded_data(current, ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION)
        self.assertEqual(migrated["quest_action_proofs"], ["proof-a", "proof-b"])
        self.assertNotIn("quest_stage_actions", migrated)

    def test_retired_proof_is_subtracted_and_no_longer_satisfies_a_gate(self):
        current = {
            "config_version": 122,
            "quest_action_proofs": [MOURNER_FOOD_STORES_PROOF, "surviving proof"],
        }
        with patch.object(
            storage_pure,
            "RETIRED_QUEST_ACTION_PROOFS",
            {MOURNER_FOOD_STORES_PROOF},
        ):
            migrated = migrate_loaded_data(current, ORE_DATA, ITEM_DEFINITIONS)
        target_id = "target_quest"
        migrated["quests"][target_id] = {
            "started": True,
            "progress": 1,
            "completed": False,
        }
        quest_data = {
            target_id: {
                "stages": 1,
                "point_reward": 0,
                "rewards": {},
                "stage_requirements": (
                    {
                        "stage": 1,
                        "required_actions": (MOURNER_FOOD_STORES_PROOF,),
                        "source": "test source",
                    },
                ),
            },
        }

        self.assertEqual(migrated["quest_action_proofs"], ["surviving proof"])
        self.assertEqual(
            tuple(
                blocker.get("action_id")
                for blocker in quest_current_stage_blockers_pure(
                    migrated,
                    target_id,
                    quest_data,
                )
                if blocker["kind"] == "required_action"
            ),
            (MOURNER_FOOD_STORES_PROOF,),
        )

    def test_next_config_bump_retires_current_version_proofs(self):
        current = {
            "config_version": CURRENT_CONFIG_VERSION,
            "quest_action_proofs": [MOURNER_FOOD_STORES_PROOF, "surviving proof"],
        }
        with patch.multiple(
            storage_pure,
            CURRENT_CONFIG_VERSION=CURRENT_CONFIG_VERSION + 1,
            RETIRED_QUEST_ACTION_PROOFS={MOURNER_FOOD_STORES_PROOF},
        ):
            migrated = migrate_loaded_data(current, ORE_DATA, ITEM_DEFINITIONS)

        self.assertEqual(migrated["config_version"], CURRENT_CONFIG_VERSION + 1)
        self.assertEqual(migrated["quest_action_proofs"], ["surviving proof"])


class TestQuestActionProofIntegration(unittest.TestCase):
    def test_pure_quest_flow_reads_a_proof_earned_by_another_quest(self):
        source_id = "biohazard"
        target_id = "target_quest"
        quest_data = {
            source_id: {
                "stages": 1,
                "point_reward": 0,
                "rewards": {},
                "stage_requirements": (
                    {
                        "stage": 1,
                        "auto_actions": (BIOHAZARD_CAULDRON_ACTION,),
                        "source": "test source",
                    },
                ),
            },
            target_id: {
                "stages": 1,
                "point_reward": 0,
                "rewards": {},
                "stage_requirements": (
                    {
                        "stage": 1,
                        "required_actions": (MOURNER_FOOD_STORES_PROOF,),
                        "source": "test source",
                    },
                ),
            },
        }
        player = {
            "inventory": {},
            "quests": {
                source_id: {"started": True, "progress": 1, "completed": False},
                target_id: {"started": True, "progress": 1, "completed": False},
            },
            "quest_points": 0,
            "quest_action_proofs": [],
            "quest_route_states": {},
            "pending_skill_exp_rewards": {},
        }
        self.assertEqual(
            tuple(
                blocker["kind"]
                for blocker in quest_current_stage_blockers_pure(
                    player,
                    target_id,
                    quest_data,
                )
            ),
            ("required_action",),
        )

        player, progressed, _completed = apply_quest_progress_pure(
            player,
            source_id,
            quest_data,
        )
        self.assertTrue(progressed)
        self.assertEqual(player["current_quest"], source_id)
        self.assertIn(MOURNER_FOOD_STORES_PROOF, player["quest_action_proofs"])
        self.assertEqual(
            quest_current_stage_blockers_pure(player, target_id, quest_data),
            (),
        )

        player, progressed, completed = apply_quest_progress_pure(
            player,
            target_id,
            quest_data,
        )
        self.assertTrue(progressed)
        self.assertTrue(completed)

    def test_shop_purchase_proves_recovery_only_after_a_successful_buy(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["quests"]["do_no_evil"] = {"started": True, "progress": 3, "completed": False}
        denied, result = apply_shop_buy_pure(
            player,
            "hamabs_crafting_emporium",
            "hamabs_crafting_emporium:3:4020",
        )
        self.assertFalse(result["allowed"])
        self.assertNotIn(DO_NO_EVIL_MAMULET_MOULD_PROOF, denied["quest_action_proofs"])
        action_ids = {
            row.get("action_id")
            for row in quest_current_stage_blockers_pure(player, "do_no_evil", QUEST_DATA)
        }
        self.assertIn(DO_NO_EVIL_MAMULET_MOULD_PROOF, action_ids)
        self.assertNotIn("Complete Do No Evil stage 3 objective", action_ids)

        player["inventory"]["Coins"] = 10_000
        player["quests"]["monkey_madness"] = {
            "started": True,
            "progress": 1,
            "completed": False,
        }
        bought, result = apply_shop_buy_pure(
            player,
            "hamabs_crafting_emporium",
            "hamabs_crafting_emporium:3:4020",
        )
        self.assertTrue(result["allowed"])
        self.assertEqual(bought["inventory"]["M'amulet mould"], 1)
        self.assertIn(DO_NO_EVIL_MAMULET_MOULD_PROOF, bought["quest_action_proofs"])
        self.assertNotIn(
            DO_NO_EVIL_MAMULET_MOULD_PROOF,
            {row.get("action_id") for row in quest_current_stage_blockers_pure(bought, "do_no_evil", QUEST_DATA)},
        )
        self.assertEqual(
            quest_required_action_proofs_for_quest(bought, "do_no_evil", QUEST_DATA),
            (DO_NO_EVIL_MAMULET_MOULD_PROOF,),
        )

    def test_purchase_rollback_keeps_only_retained_support(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["inventory"]["Coins"] = 10_000
        player["quests"]["monkey_madness"] = {
            "started": True, "progress": 1, "completed": False,
        }
        first, first_buy = apply_shop_buy_pure(
            player, "hamabs_crafting_emporium", "hamabs_crafting_emporium:3:4020",
        )
        self.assertTrue(first_buy["allowed"])
        second, second_buy = apply_shop_buy_pure(
            first, "hamabs_crafting_emporium", "hamabs_crafting_emporium:3:4020",
        )
        self.assertTrue(second_buy["allowed"])
        before = copy.deepcopy(second)

        retained, rollback = rollback_shop_event_pure(second, second_buy["event_id"])

        self.assertTrue(rollback["allowed"])
        self.assertEqual(second, before)
        self.assertEqual(retained["inventory"]["M'amulet mould"], 1)
        self.assertIn(DO_NO_EVIL_MAMULET_MOULD_PROOF, retained["quest_action_proofs"])
        self.assertIn(
            first_buy["event_id"],
            {event["event_id"] for event in retained["shop_events"]},
        )

        restored, rollback = rollback_shop_event_pure(retained, first_buy["event_id"])

        self.assertTrue(rollback["allowed"])
        self.assertEqual(restored["inventory"]["M'amulet mould"], 0)
        self.assertNotIn(DO_NO_EVIL_MAMULET_MOULD_PROOF, restored["quest_action_proofs"])
        self.assertEqual(
            {
                event["rolled_back_event_id"]
                for event in restored["shop_events"]
                if event["type"] == "rollback"
            },
            {first_buy["event_id"], second_buy["event_id"]},
        )

    def test_service_rollback_keeps_crafting_proof_chain_reachable(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["quests"]["the_fremennik_isles"] = {
            "started": True, "progress": 5, "completed": False,
        }
        player["inventory"].update({"Yak-hide": 2, "Thread": 1, "Coins": 10})
        player["crafting_level"] = 99
        first, first_service = apply_shop_service_pure(player, "thakkrad_cure_yak_hide")
        self.assertTrue(first_service["allowed"])
        second, second_service = apply_shop_service_pure(first, "thakkrad_cure_yak_hide")
        self.assertTrue(second_service["allowed"])
        before = copy.deepcopy(second)

        retained, rollback = rollback_shop_event_pure(second, second_service["event_id"])

        self.assertTrue(rollback["allowed"])
        self.assertEqual(second, before)
        self.assertEqual(retained["inventory"]["Cured yak-hide"], 1)
        self.assertEqual(retained["inventory"]["Yak-hide"], 1)
        self.assertEqual(retained["inventory"]["Coins"], 5)
        self.assertIn(THAKKRAD_CURED_YAK_HIDE_PROOF, retained["quest_action_proofs"])
        before_blockers = quest_current_stage_blockers_pure(
            retained, "the_fremennik_isles", QUEST_DATA
        )
        self.assertIn(
            FREMENNIK_ISLES_YAK_HIDE_PROOF,
            {row.get("action_id") for row in before_blockers},
        )

        retained["current_craft"] = "leather_yakhide_armour_10824"
        calls = {"xp": [], "saves": 0, "errors": []}
        self.assertTrue(handle_crafting_answer(_context(retained, calls, [0.0])))

        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["errors"], [])
        self.assertIn(FREMENNIK_ISLES_YAK_HIDE_PROOF, retained["quest_action_proofs"])
        after_blockers = quest_current_stage_blockers_pure(
            retained, "the_fremennik_isles", QUEST_DATA
        )
        self.assertNotIn(
            FREMENNIK_ISLES_YAK_HIDE_PROOF,
            {row.get("action_id") for row in after_blockers},
        )

    def test_shop_purchase_rollback_retracts_its_proof(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["inventory"]["Coins"] = 10_000
        player["quests"]["do_no_evil"] = {"started": True, "progress": 3, "completed": False}
        player["quests"]["monkey_madness"] = {
            "started": True,
            "progress": 1,
            "completed": False,
        }
        bought, buy = apply_shop_buy_pure(
            player,
            "hamabs_crafting_emporium",
            "hamabs_crafting_emporium:3:4020",
        )
        self.assertTrue(buy["allowed"])
        self.assertIn(DO_NO_EVIL_MAMULET_MOULD_PROOF, bought["quest_action_proofs"])

        restored, rollback = rollback_shop_event_pure(bought, buy["event_id"])

        self.assertTrue(rollback["allowed"])
        self.assertEqual(restored["inventory"]["M'amulet mould"], 0)
        self.assertEqual(restored["inventory"]["Coins"], 10_000)
        self.assertNotIn(DO_NO_EVIL_MAMULET_MOULD_PROOF, restored["quest_action_proofs"])
        self.assertIn(
            DO_NO_EVIL_MAMULET_MOULD_PROOF,
            {row.get("action_id") for row in quest_current_stage_blockers_pure(restored, "do_no_evil", QUEST_DATA)},
        )

    def test_yak_hide_proof_requires_service_then_real_crafting(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["quests"]["the_fremennik_isles"] = {
            "started": True,
            "progress": 5,
            "completed": False,
        }
        player["inventory"].update({"Yak-hide": 1, "Thread": 1, "Coins": 100})
        player["crafting_level"] = 99
        self.assertNotIn(
            "Complete The Fremennik Isles stage 5 objective",
            {row.get("action_id") for row in quest_current_stage_blockers_pure(player, "the_fremennik_isles", QUEST_DATA)},
        )

        player, service = apply_shop_service_pure(
            player,
            "thakkrad_cure_yak_hide",
        )
        self.assertTrue(service["allowed"])
        self.assertIn(THAKKRAD_CURED_YAK_HIDE_PROOF, player["quest_action_proofs"])
        self.assertNotIn(FREMENNIK_ISLES_YAK_HIDE_PROOF, player["quest_action_proofs"])

        player["current_craft"] = "leather_yakhide_armour_10824"
        calls = {"xp": [], "saves": 0, "errors": []}
        self.assertTrue(handle_crafting_answer(_context(player, calls, [0.0])))
        self.assertEqual(calls["saves"], 1)
        self.assertIn(FREMENNIK_ISLES_YAK_HIDE_PROOF, player["quest_action_proofs"])
        self.assertEqual(
            quest_required_action_proofs_for_quest(player, "the_fremennik_isles", QUEST_DATA),
            (FREMENNIK_ISLES_YAK_HIDE_PROOF,),
        )

        inventory_only = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        inventory_only["inventory"].update({"Cured yak-hide": 1, "Thread": 1})
        inventory_only["crafting_level"] = 99
        inventory_only["current_craft"] = "leather_yakhide_armour_10824"
        self.assertTrue(handle_crafting_answer(_context(inventory_only, random_values=[0.0])))
        self.assertNotIn(
            FREMENNIK_ISLES_YAK_HIDE_PROOF,
            inventory_only["quest_action_proofs"],
        )

    def test_round_shield_requires_rites_and_records_real_crafting(self):
        proof = "Make a Fremennik round shield"
        output = "Fremennik round shield"
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["quests"]["the_fremennik_isles"] = {"started": True, "progress": 5, "completed": False}
        player["inventory"].update({"Arctic pine logs": 2, "Bronze nails": 1, "Rope": 1, "Hammer": 1, output: 1})
        player["crafting_level"] = 1
        player["woodcutting_level"] = 56
        player["current_craft"] = "craft_fremennik_round_shield"
        player["quests"]["the_fremennik_isles"]["progress"] = 4
        before = copy.deepcopy(player["inventory"])
        calls = {"xp": [], "saves": 0, "errors": []}
        self.assertFalse(handle_crafting_answer(_context(player, calls)))
        self.assertEqual(player["inventory"], before)
        self.assertNotIn(proof, player["quest_action_proofs"])

        player["quests"]["the_fremennik_isles"]["progress"] = 5
        action_ids = {row.get("action_id") for row in quest_current_stage_blockers_pure(player, "the_fremennik_isles", QUEST_DATA)}
        self.assertIn(proof, action_ids)
        calls = {"xp": [], "saves": 0, "errors": []}
        self.assertTrue(handle_crafting_answer(_context(player, calls, [0.99])))
        item_names = ("Arctic pine logs", "Bronze nails", "Rope", "Hammer", output)
        self.assertEqual({item: player["inventory"][item] for item in item_names}, dict(zip(item_names, (0, 0, 0, 1, 2))))
        self.assertEqual((player["crafting_exp"], calls["xp"], calls["saves"]), (34.0, [34.0], 1))
        self.assertIn(proof, player["quest_action_proofs"])
        action_ids = {row.get("action_id") for row in quest_current_stage_blockers_pure(player, "the_fremennik_isles", QUEST_DATA)}
        self.assertNotIn(proof, action_ids)
        self.assertEqual(quest_required_action_proofs_for_quest(player, "the_fremennik_isles", QUEST_DATA), (proof,))


class TestQuestActionProofReviewFlow(unittest.TestCase):
    def setUp(self) -> None:
        self._original_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self) -> None:
        sys.modules.clear()
        sys.modules.update(self._original_modules)

    def test_real_review_action_satisfies_another_quests_global_requirement(self):
        addon = _load_addon_as_package("ankiscape_quest_action_proof_e2e")
        saved = []
        errors = []
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: saved.append(copy.deepcopy(addon._state.player_data))
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _text: None
        addon._show_exp = lambda _amount: None
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda title, message: errors.append((title, message))

        player = _maxed_player_for_quest("biohazard")
        player["quests"]["biohazard"] = {
            "started": True,
            "progress": 7,
            "completed": False,
        }
        player["quests"]["mournings_end_part_i"] = {
            "started": True,
            "progress": 5,
            "completed": False,
        }
        player["inventory"]["Rotten apple"] = 1
        player["inventory"]["Sieve"] = 1
        player["current_quest"] = "biohazard"
        before = quest_current_stage_blockers_pure(
            player,
            "mournings_end_part_i",
            QUEST_DATA,
        )
        self.assertIn(
            MOURNER_FOOD_STORES_PROOF,
            {blocker.get("action_id") for blocker in before},
        )
        addon._state.player_data = player
        addon._state.current_skill = "Quests"
        addon._state.review_undo_stack.clear()

        _answer_review(addon)

        self.assertFalse(errors)
        self.assertEqual(addon._state.player_data["current_quest"], "biohazard")
        self.assertIn(MOURNER_FOOD_STORES_PROOF, addon._state.player_data["quest_action_proofs"])
        self.assertEqual(len(saved), 1)
        self.assertIn(MOURNER_FOOD_STORES_PROOF, saved[0]["quest_action_proofs"])
        after = quest_current_stage_blockers_pure(
            addon._state.player_data,
            "mournings_end_part_i",
            QUEST_DATA,
        )
        self.assertNotIn(
            MOURNER_FOOD_STORES_PROOF,
            {blocker.get("action_id") for blocker in after},
        )
        self.assertIn(
            "Complete Mourning's End Part I stage 5 objective",
            {blocker.get("action_id") for blocker in after},
        )


class TestQuestActionProofWriterOwnership(unittest.TestCase):
    def test_production_proof_writers_are_genuine_action_seams(self):
        call_sites, mention_counts, retired_writes, retired_mentions = _production_store_sites(
            Path(__file__).resolve().parents[1]
        )

        self.assertEqual(
            call_sites,
            {
                ("logic/shop_logic.py", "apply_shop_buy_pure", "record_runtime_quest_action_proofs_pure"),
                ("logic/shop/services.py", "_apply_service_like", "record_runtime_quest_action_proofs_pure"),
                ("logic/shop_logic.py", "rollback_shop_event_pure", "retract_shop_event_quest_action_proofs_pure"),
                ("logic_pure/quest/stage_items.py", "consume_stage_rows_pure", "record_quest_stage_action_proofs_pure"),
                ("logic_pure/quest/stage_items.py", "apply_fenkenstrain_stage_two_items_pure", "record_quest_stage_action_proofs_pure"),
                ("runtime/runtime_actions_shared.py", "_record_action", "record_runtime_quest_action_proofs_pure"),
                ("logic_pure/quest/one_small_favour.py", "_apply_opening_deed_pure", "record_runtime_quest_action_proofs_pure"),
                ("logic_pure/quest/another_cook.py", "_commit_commission_pure", "record_runtime_quest_action_proofs_pure"),
                ("logic_pure/quest/another_cook.py", "_prepare_dirty_blast_pure", "record_runtime_quest_action_proofs_pure"),
                ("logic_pure/quest/oronwen.py", "apply_oronwen_review_pure", "record_runtime_quest_action_proofs_pure"),
                ("logic_pure/quest/grand_tree.py", "apply_grand_tree_review_pure", "record_runtime_quest_action_proofs_pure"),
                ("logic_pure/quest/watchtower.py", "apply_watchtower_review_pure", "record_runtime_quest_action_proofs_pure"),
                ("logic_pure/quest/toktz_opening.py", "apply_toktz_opening_review_pure", "record_runtime_quest_action_proofs_pure"),
                ("logic_pure/quest/enakhra.py", "apply_enakhra_opening_action_pure", "record_runtime_quest_action_proofs_pure"),
                ("logic_pure/quest/elemental_workshop.py", "search_chapel_bookcase_pure", "record_runtime_quest_action_proofs_pure"),
                ("logic_pure/quest/elemental_workshop.py", "read_ragged_book_pure", "record_runtime_quest_action_proofs_pure"),
                ("logic_pure/quest/murder_mystery.py", "search_murder_mystery_barrel_pure", "record_quest_stage_action_proofs_pure"),
                ("logic_pure/quest/murder_mystery.py", "apply_murder_mystery_opening_items_pure", "record_quest_stage_action_proofs_pure"),
                ("logic_pure/quest/witchs_house.py", "apply_witchs_house_service_pure", "record_quest_stage_action_proofs_pure"),
                ("logic_pure/quest/hazeel.py", "apply_hazeel_opening_action_pure", "record_quest_stage_action_proofs_pure"),
            },
        )
        self.assertEqual(
            mention_counts,
            {
                "core/quest_storage.py": 8,
                "logic/shop_logic.py": 5,
                "logic/shop/services.py": 3,
                "logic_pure/logic_pure_quest.py": 1,
                "logic_pure/quest/stage_items.py": 1,
                "logic_pure/logic_pure_state.py": 5,
                "logic_pure/quest/one_small_favour.py": 3,
                "logic_pure/quest/another_cook.py": 4,
                "logic_pure/quest/oronwen.py": 3,
                "logic_pure/quest/journal.py": 1,
                "logic_pure/quest/grand_tree.py": 3,
                "logic_pure/quest/watchtower.py": 3,
                "logic_pure/quest/toktz_opening.py": 3,
                "logic_pure/quest/enakhra.py": 3,
                "logic_pure/quest/elemental_workshop.py": 4,
                "logic_pure/quest/murder_mystery.py": 1,
                "logic_pure/quest/witchs_house.py": 1,
                "logic_pure/quest/hazeel.py": 1,
                "logic_pure/quest/hazeel_journal.py": 1,
                "logic_pure/quest_action_proofs.py": 25,
                "runtime/runtime_actions_shared.py": 3,
            },
        )
        self.assertEqual(retired_writes, set())
        self.assertEqual(retired_mentions, {"core/quest_storage.py": 1})


if __name__ == "__main__":
    unittest.main()
