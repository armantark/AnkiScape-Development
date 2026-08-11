from __future__ import annotations

import copy
import json
import sys
import types
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import (
    COMBAT_ENEMY_IMAGES,
    COMBAT_ITEM_IMAGES,
    DEFAULT_COMBAT_TARGET,
    EQUIPMENT_DATA,
    EQUIPMENT_ITEM_DATA,
    ITEM_DEFINITIONS,
    ORE_DATA,
)
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.core.target_metadata import combat_target_rows
from ankiscape.data.achievement_diary_data import ACHIEVEMENT_DIARY_CATALOG
from ankiscape.data.combat_data import COMBAT_ENEMY_DATA
from ankiscape.data.grand_exchange_data import GE_ITEM_CATALOG
from ankiscape.data.slayer_data import DURADEL_MASTER, SLAYER_FAMILIES_BY_ID
from ankiscape.logic import slayer_logic
from ankiscape.logic.achievement_diary_logic import task_progress_pure
from ankiscape.logic.slayer_logic import slayer_target_ids_for_assignment_pure
from ankiscape.logic_pure.logic_pure_combat_engine import apply_combat_burst_pure
from ankiscape.runtime.runtime_actions import RuntimeActionContext, handle_combat_answer
from tools.audit_item_reachability import build_reachability_report


PROTECTIVE_SHIELD_IDS = {
    "Elemental shield": 2890,
    "Mind shield": 9731,
    "Body shield": 18691,
    "Cosmic shield": 20436,
    "Chaos shield": 20438,
    "Dragonfire shield": 11284,
}
DOWNSTREAM_ITEMS = (
    "Super prayer (1)",
    "Super prayer (2)",
    "Super prayer (3)",
    "Super prayer (4)",
    "Super prayer flask (1)",
    "Super prayer flask (2)",
    "Super prayer flask (3)",
    "Super prayer flask (4)",
    "Super prayer flask (5)",
    "Super prayer flask (6)",
    "Wyvern bonemeal",
    "Wyvern bones",
)


def _player(**overrides):
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data.update(
        {
            "current_combat_target": "skeletal_wyvern",
            "slayer_level": 72,
            "attack_level": 1,
            "strength_level": 1,
            "defense_level": 99,
            "constitution_level": 99,
            "combat_lifepoints": 990,
            "combat_auto_flee": False,
            "combat_auto_eat_food": [],
            "combat_attack_style": "melee_accurate",
        }
    )
    data.update(overrides)
    return data


def _live_encounter_player(**overrides):
    data = _player(
        combat_encounter={
            "target_id": "skeletal_wyvern",
            "enemy_lifepoints": 2000,
            "player_attack_ticks_remaining": 0,
            "enemy_attack_ticks_remaining": 0,
        }
    )
    data.update(overrides)
    return data


def _runtime_context(
    player_data,
    rng=lambda: 0.0,
    save_player_data=lambda: None,
    show_activity_gain=lambda *_args: None,
):
    return RuntimeActionContext(
        player_data=player_data,
        random_random=rng,
        show_error_message=lambda title, message: (_ for _ in ()).throw(
            AssertionError(f"{title}: {message}")
        ),
        deactivate_current_skill=lambda: None,
        award_skill_exp=lambda _exp_key, base_exp: base_exp,
        award_hidden_skill_exp=lambda *_args: None,
        level_up_check=lambda *_args: None,
        check_achievements=lambda *_args: None,
        save_player_data=save_player_data,
        refresh_skill_availability=lambda: None,
        refresh_skill_availability_partial=lambda *_args: None,
        can_smith_any=lambda: True,
        show_exp=lambda *_args: None,
        show_activity_gain=show_activity_gain,
        implemented_exp_keys_snapshot=lambda: {},
        show_quest_exp_delta=lambda *_args: None,
        cadence_live_enabled=True,
    )


def _enabled_duradel():
    return replace(DURADEL_MASTER, runtime_enabled=True)


class SkeletalWyvernDataAndSurfaceTests(unittest.TestCase):
    def test_period_data_items_assets_and_market_rows_are_registered(self):
        enemy = COMBAT_ENEMY_DATA["skeletal_wyvern"]
        self.assertEqual(
            (
                enemy["level"],
                enemy["required_slayer_level"],
                enemy["stats"]["hitpoints"],
                enemy["slayer_xp"],
                enemy["max_hit"],
            ),
            (198, 72, 2000, 210.0, 139),
        )
        self.assertEqual(
            enemy["drops"]["guaranteed"], (("Wyvern bones", 1),)
        )
        self.assertEqual(
            tuple(row.get("max_hit") for row in enemy["attack_table"][:2]),
            (139, 139),
        )
        self.assertEqual(
            enemy["protective_equipment"]["items"],
            tuple(PROTECTIVE_SHIELD_IDS),
        )

        registered = {item.storage_key: item for item in ITEM_DEFINITIONS}
        self.assertEqual(registered["Wyvern bones"].source_item_id, 6812)
        self.assertEqual(registered["Wyvern bones"].noted_item_id, 6816)
        self.assertEqual(registered["Wyvern bonemeal"].source_item_id, 6810)
        self.assertTrue(Path(registered["Wyvern bones"].asset_path or "").is_file())
        self.assertTrue(Path(COMBAT_ENEMY_IMAGES["skeletal_wyvern"]).is_file())
        for shield_name, item_id in PROTECTIVE_SHIELD_IDS.items():
            with self.subTest(shield=shield_name):
                item = registered[shield_name]
                self.assertEqual(item.source_item_id, item_id)
                self.assertEqual(item.equipment_slot, "shield")
                self.assertTrue(Path(item.asset_path or "").is_file())
                self.assertEqual(item.asset_path, COMBAT_ITEM_IMAGES[shield_name])
                self.assertIn(shield_name, GE_ITEM_CATALOG)

    def test_combat_selector_applies_the_slayer_gate_and_exposes_the_real_row(self):
        def row_for(player):
            rows = combat_target_rows(
                player,
                COMBAT_ENEMY_DATA,
                COMBAT_ITEM_IMAGES,
                EQUIPMENT_ITEM_DATA,
                DEFAULT_COMBAT_TARGET,
                COMBAT_ENEMY_IMAGES,
            )
            return next(row for row in rows if row.target_id == "skeletal_wyvern")

        locked = row_for(_player(slayer_level=71))
        self.assertFalse(locked.enabled)
        self.assertEqual(locked.locked_reasons, ("Slayer level 72",))

        unlocked = row_for(_player(slayer_level=72))
        self.assertTrue(unlocked.enabled)
        self.assertEqual(unlocked.label, "Skeletal Wyvern (Lvl 198)")
        self.assertEqual(unlocked.icon_path, COMBAT_ENEMY_IMAGES["skeletal_wyvern"])
        self.assertIn("Wyvern ice breath", unlocked.tooltip)
        self.assertEqual(
            SLAYER_FAMILIES_BY_ID["skeletal_wyverns"].target_ids,
            ("skeletal_wyvern",),
        )

    def test_reachability_starts_at_the_combat_drop_and_lights_the_full_chain(self):
        report = build_reachability_report()
        self.assertEqual(report["routes"]["Wyvern bones"], "combat:skeletal_wyvern")
        orphan_items = {row["item"] for row in report["orphan_inputs"]}
        self.assertNotIn("Wyvern bones", orphan_items)
        self.assertNotIn("Wyvern bonemeal", orphan_items)
        for item_name in DOWNSTREAM_ITEMS:
            with self.subTest(item=item_name):
                self.assertIn(item_name, report["routes"])


class SkeletalWyvernKernelTests(unittest.TestCase):
    def test_breath_uses_only_the_six_period_shields_and_applies_freeze_cadence(self):
        for shield_name in PROTECTIVE_SHIELD_IDS:
            with self.subTest(shield=shield_name):
                protected, ok, result = apply_combat_burst_pure(
                    _live_encounter_player(equipment={"shield": shield_name}),
                    COMBAT_ENEMY_DATA,
                    EQUIPMENT_DATA,
                    ticks=1,
                    rng=lambda: 0.999999,
                    live_cadence=True,
                )
                self.assertTrue(ok, result)
                self.assertEqual(result["enemy_damage"], 150)
                self.assertEqual(result["unprotected_attacks"], 0)
                self.assertEqual(
                    result["enemy_specials"],
                    (
                        {
                            "kind": "wyvern_breath",
                            "protected": True,
                            "shield_item": shield_name,
                            "max_hit": 150,
                            "delay_ticks": 5,
                        },
                    ),
                )
                self.assertEqual(
                    protected["combat_encounter"]["player_attack_ticks_remaining"],
                    8,
                )

        for scenario, overrides in {
            "no shield": {},
            "anti-dragon shield": {"equipment": {"shield": "Anti-dragon shield"}},
            "antifire": {"combat_antifire_ticks_remaining": 600},
            "super antifire": {"combat_super_antifire_ticks_remaining": 600},
        }.items():
            with self.subTest(scenario=scenario):
                unprotected, ok, result = apply_combat_burst_pure(
                    _live_encounter_player(**overrides),
                    COMBAT_ENEMY_DATA,
                    EQUIPMENT_DATA,
                    ticks=1,
                    rng=lambda: 0.999999,
                    live_cadence=True,
                )
                self.assertTrue(ok, result)
                self.assertEqual(result["enemy_damage"], 500)
                self.assertEqual(result["unprotected_attacks"], 1)
                self.assertFalse(result["enemy_specials"][0]["protected"])
                self.assertEqual(result["enemy_specials"][0]["max_hit"], 500)
                self.assertEqual(
                    unprotected["combat_encounter"]["player_attack_ticks_remaining"],
                    8,
                )

        ordinary, ok, result = apply_combat_burst_pure(
            _live_encounter_player(),
            COMBAT_ENEMY_DATA,
            EQUIPMENT_DATA,
            ticks=1,
            rng=lambda: 0.0,
            live_cadence=True,
        )
        self.assertTrue(ok, result)
        self.assertEqual(result["enemy_specials"], ())
        self.assertEqual(
            ordinary["combat_encounter"]["player_attack_ticks_remaining"], 3
        )

    def test_magic_defence_reduces_the_shielded_breath_maximum(self):
        results = []
        for magic_level in (1, 99):
            _, ok, result = apply_combat_burst_pure(
                _live_encounter_player(
                    magic_level=magic_level,
                    equipment={"shield": "Elemental shield"},
                ),
                COMBAT_ENEMY_DATA,
                EQUIPMENT_DATA,
                ticks=1,
                rng=lambda: 0.999999,
                live_cadence=True,
            )
            self.assertTrue(ok, result)
            results.append(result)

        self.assertEqual(results[0]["enemy_specials"][0]["max_hit"], 150)
        self.assertLess(
            results[1]["enemy_specials"][0]["max_hit"],
            results[0]["enemy_specials"][0]["max_hit"],
        )

    def test_real_runtime_surfaces_protected_and_unprotected_breath(self):
        for scenario, equipment, expected in (
            (
                "protected",
                {"shield": "Elemental shield"},
                "Wyvern ice breath · protected by Elemental shield · next attack delayed",
            ),
            (
                "unprotected",
                {},
                "Wyvern ice breath · unprotected · next attack delayed",
            ),
        ):
            with self.subTest(scenario=scenario):
                gains = []
                self.assertTrue(
                    handle_combat_answer(
                        _runtime_context(
                            _live_encounter_player(equipment=equipment),
                            rng=lambda: 0.999999,
                            show_activity_gain=gains.append,
                        )
                    )
                )
                self.assertEqual(gains[0], expected)

    def test_real_runtime_kill_awards_bones_slayer_credit_and_persists_state(self):
        player = _player(
            attack_level=99,
            strength_level=99,
            equipment={"shield": "Elemental shield"},
            combat_encounter={
                "target_id": "skeletal_wyvern",
                "enemy_lifepoints": 1,
                "player_attack_ticks_remaining": 0,
                "enemy_attack_ticks_remaining": 6,
            },
            slayer_assignment={
                "master_id": "duradel_lapalok",
                "family_id": "skeletal_wyverns",
                "initial_count": 40,
                "remaining": 40,
            },
            slayer_exp=0.0,
        )
        diary_task = next(
            task
            for family in ACHIEVEMENT_DIARY_CATALOG
            for tier in family.tiers
            for task in tier.tasks
            if task.id == "falador_hard_why_oh_wyvern"
        )
        self.assertFalse(task_progress_pure(player, diary_task)[0])
        below_gate = copy.deepcopy(player)
        below_gate["slayer_level"] = 71
        below_gate["combat_kill_counts"]["skeletal_wyvern"] = 1
        self.assertFalse(task_progress_pure(below_gate, diary_task)[0])

        saved_states = []
        with patch.dict(
            slayer_logic.SLAYER_MASTERS_BY_ID,
            {"duradel_lapalok": _enabled_duradel()},
        ):
            self.assertEqual(
                slayer_target_ids_for_assignment_pure(player),
                ("skeletal_wyvern",),
            )
            self.assertTrue(
                handle_combat_answer(
                    _runtime_context(
                        player,
                        save_player_data=lambda: saved_states.append(
                            json.loads(json.dumps(player))
                        ),
                    )
                )
            )

            self.assertEqual(player["inventory"]["Wyvern bones"], 1)
            self.assertEqual(player["combat_kill_counts"]["skeletal_wyvern"], 1)
            self.assertTrue(task_progress_pure(player, diary_task)[0])
            self.assertEqual(player["slayer_assignment"]["remaining"], 39)
            self.assertEqual(player["slayer_exp"], 210.0)
            self.assertEqual(player["combat_last_result"]["slayer"]["slayer_xp"], 210.0)

            self.assertEqual(len(saved_states), 1)
            loaded = migrate_loaded_data(saved_states[0], ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(loaded["current_combat_target"], "skeletal_wyvern")
        self.assertEqual(loaded["equipment"]["shield"], "Elemental shield")
        self.assertEqual(loaded["inventory"]["Wyvern bones"], 1)
        self.assertEqual(loaded["combat_kill_counts"]["skeletal_wyvern"], 1)
        self.assertEqual(loaded["slayer_assignment"]["remaining"], 39)
        self.assertEqual(loaded["slayer_exp"], 210.0)
        self.assertEqual(loaded["combat_encounter"], {})


class SkeletalWyvernReviewUndoTests(unittest.TestCase):
    def setUp(self):
        from tests.test_integration_smoke import _install_runtime_fakes

        self._orig_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._orig_modules)

    def test_real_review_undo_and_replay_restore_every_wyvern_mutation(self):
        from tests.test_integration_smoke import (
            _DummyCol,
            _DummyMW,
            _FakeReviewer,
            _load_addon_as_package,
        )

        addon = _load_addon_as_package("ankiscape_skeletal_wyvern_review")
        addon.mw = _DummyMW(_DummyCol())
        addon.save_player_data = lambda: None
        addon.level_up_check = lambda *_args: None
        addon.check_achievements = lambda *_args: None
        addon.update_review_hud = lambda *_args: None
        addon.update_review_status_badge = lambda *_args: None
        addon.update_review_fill_drawer = lambda *_args: None
        addon.update_review_event_log_drawer = lambda *_args: None
        addon._update_review_bank_run_surface = lambda: None
        addon._update_review_context_surface = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_exp = lambda *_args: None
        addon.show_error_message = lambda title, message: self.fail(
            f"{title}: {message}"
        )
        addon.player_data = _player(
            attack_level=99,
            strength_level=99,
            equipment={"shield": "Elemental shield"},
            combat_encounter={
                "target_id": "skeletal_wyvern",
                "enemy_lifepoints": 1,
                "player_attack_ticks_remaining": 0,
                "enemy_attack_ticks_remaining": 6,
            },
            slayer_assignment={
                "master_id": "duradel_lapalok",
                "family_id": "skeletal_wyverns",
                "initial_count": 40,
                "remaining": 40,
            },
            slayer_exp=0.0,
        )
        addon.current_skill = "Combat"
        addon._REVIEW_UNDO_STACK.clear()
        initial = copy.deepcopy(addon.player_data)
        addon_slayer_logic = sys.modules[
            f"{addon.__name__}.logic.slayer_logic"
        ]
        duradel = addon_slayer_logic.SLAYER_MASTERS_BY_ID["duradel_lapalok"]
        original_random = addon.random.random
        addon.random.random = lambda: 0.0

        def answer_once():
            addon.card_turned = True
            addon.answer_shown = True
            addon.exp_awarded = False
            addon.on_answer_card(
                _FakeReviewer(), 4, lambda _self, _ease: "answered"
            )

        try:
            with patch.dict(
                addon_slayer_logic.SLAYER_MASTERS_BY_ID,
                {"duradel_lapalok": replace(duradel, runtime_enabled=True)},
            ):
                answer_once()
                first_result = copy.deepcopy(addon.player_data)
                self.assertEqual(first_result["inventory"]["Wyvern bones"], 1)
                self.assertEqual(
                    first_result["combat_kill_counts"]["skeletal_wyvern"], 1
                )
                self.assertEqual(first_result["slayer_assignment"]["remaining"], 39)
                self.assertEqual(first_result["slayer_exp"], 210.0)
                self.assertEqual(len(addon._REVIEW_UNDO_STACK), 1)

                addon._on_state_did_undo(
                    types.SimpleNamespace(operation="Answer Card")
                )
                self.assertEqual(addon.player_data, initial)
                self.assertEqual(addon._REVIEW_UNDO_STACK, [])

                answer_once()
                self.assertEqual(addon.player_data, first_result)
        finally:
            addon.random.random = original_random


if __name__ == "__main__":
    unittest.main()
