"""Prepared equipment fixtures prove the worn modifier, not earned acquisition."""

import copy
import hashlib
import json
from pathlib import Path
import random
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import EQUIPMENT_DATA, ITEM_DEFINITIONS, ORE_DATA, SMITHING_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.brawling_gloves_data import BRAWLING_GLOVE_DATA
from ankiscape.data.equipment_condition_data import EQUIPMENT_CONDITION_DATA
from ankiscape.data.urn_data import URN_TIERS_BY_ID
from ankiscape.logic.cooking_gauntlets_logic import goldsmith_smelting_xp_pure
from ankiscape.logic.equipment_instance_logic import sanitize_equipment_instance_state_pure
from ankiscape.runtime.runtime_actions import handle_smithing_answer, run_answer_with_carried_overlay
from tests.runtime_actions.test_sawmill_plank_diary import _JsonCollection
from tests.test_combat_quest_gate import _answer_review
from tests.test_integration_smoke import _DummyMW, _install_runtime_fakes, _load_addon_as_package
from tests.test_runtime_actions import _context


GOLD = "smelt_gold_bar"
GLOVES = "Goldsmith gauntlets"


def _player(target=GOLD):
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    spec = SMITHING_DATA[target]
    player.update(current_smith=target, smithing_level=max(40, spec["level"]), smithing_exp=0.0)
    player["inventory"] = {**spec["requirements"], **spec.get("required_items", {})}
    player["equipment"]["hands"] = GLOVES
    return player


def _supplied_pack(player, view, advanced):
    target = player["current_smith"]
    player.update(
        carried_inventory={target: dict(view)},
        carried_primed_targets={target: True},
        carried_churn={target: 0},
        carried_advanced_targets={target: advanced},
        carried_layout={target: dict(view)} if advanced else {},
    )


class GoldsmithGauntletTests(unittest.TestCase):
    def _context(self, player, *, rolls=(0.99,) * 20):
        # Keep the independent Shattered Heart roll from replacing the product.
        calls = {"xp": [], "saves": 0, "errors": [], "awards": []}
        ctx = _context(player, calls, random_values=rolls)
        award = ctx.award_skill_exp

        def captured_award(key, amount):
            calls["awards"].append((key, amount))
            return award(key, amount)

        ctx.award_skill_exp = captured_award
        return ctx, calls

    def _addon(self, *, worn=True, ores=1):
        original_modules = dict(sys.modules)
        original_random = random.getstate()
        self.addCleanup(random.setstate, original_random)
        random.seed(2026)
        self.addCleanup(lambda: (sys.modules.clear(), sys.modules.update(original_modules)))
        _install_runtime_fakes()
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        collection = _JsonCollection(directory.name)
        collection.set_config("ankiscape_cadence_kernel", False)
        collection.set_config("ankiscape_review_action_multiplier", 1)
        sys.modules["aqt"].mw = _DummyMW(collection)
        addon = _load_addon_as_package("ankiscape_goldsmith_modifier")
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _text: None
        addon.update_review_hud = lambda *_args: None
        addon.show_error_message = lambda _title, message: self.fail(message)
        addon._state.current_skill = "Smithing"
        addon._state.review_undo_stack.clear()
        addon._state.direct_action_undo_stack.clear()
        player = _player()
        player["inventory"]["Gold ore"] = ores
        if not worn:
            player["equipment"]["hands"] = None
            player["inventory"][GLOVES] = 1
        _supplied_pack(player, {"Gold ore": ores}, True)
        addon._state.player_data = player
        for package in ("ankiscape", addon.__name__):
            popups = patch.object(sys.modules[f"{package}.core.logic"], "_popups_enabled", return_value=False)
            popups.start()
            self.addCleanup(popups.stop)
        addon.save_player_data()
        return addon, collection

    def _snapshot(self, addon, collection):
        live = copy.deepcopy(addon._state.player_data)
        persisted = json.loads(collection.path.read_text())
        self.assertEqual(persisted["ankiscape_player_data"], json.loads(json.dumps(live)))
        return (
            live,
            persisted,
            addon.random.getstate(),
        )

    def test_recipe_and_registered_asset_are_preserved(self):
        spec = SMITHING_DATA[GOLD]
        for key, value in {"level": 40, "exp": 22.5, "requirements": {"Gold ore": 1},
                           "output_item": "Gold bar", "output_qty": 1, "source_item_id": 2357}.items():
            with self.subTest(field=key):
                self.assertEqual(spec[key], value)
        self.assertEqual(EQUIPMENT_DATA[GLOVES].slot, "hands")
        self.assertEqual(EQUIPMENT_DATA[GLOVES].source_item_id, 776)
        registered = next(item for item in ITEM_DEFINITIONS if item.storage_key == GLOVES)
        icon = Path(registered.asset_path)
        self.assertTrue(icon.is_file())
        self.assertEqual(hashlib.sha256(icon.read_bytes()).hexdigest(),
                         "b00f54b3f0d34a8b0dcde877e277141cdb138970f8047019b65ef092e78c80f3")

    def test_only_actual_worn_goldsmith_gauntlets_change_gold_xp(self):
        cases = [("empty", None), ("missing", None), ("banked", None), ("remembered", None),
                 ("family", "Family gauntlets"), ("cooking", "Cooking gauntlets"),
                 ("chaos", "Chaos gauntlets"), ("goldsmith", GLOVES)]
        for case, hands in cases:
            with self.subTest(case=case):
                player = _player()
                player["equipment"]["hands"] = hands
                if case == "missing":
                    player["equipment"].pop("hands")
                if case == "banked":
                    player["inventory"][GLOVES] = 1
                if case == "remembered":
                    player["family_gauntlet_enchantment"] = "goldsmith"
                    player["cooking_equipment_choices"] = {GOLD: "cooking"}
                before = copy.deepcopy(player)
                expected = 56.2 if hands == GLOVES else 22.5
                self.assertEqual(goldsmith_smelting_xp_pure(player, GOLD, 22.5), expected)
                self.assertEqual(player, before)
                ctx, calls = self._context(player)
                self.assertTrue(handle_smithing_answer(ctx))
                self.assertEqual(calls["awards"], [("smithing_exp", expected)])
                self.assertEqual(player["smithing_exp"], expected)
                self.assertEqual(player["inventory"].get("Gold ore", 0), 0)
                self.assertEqual(player["inventory"]["Gold bar"], 1)
                self.assertEqual(player["equipment"], before["equipment"])
                for key in ("family_gauntlet_enchantment", "cooking_equipment_choices", "cooking_equipment_swap"):
                    self.assertEqual(player.get(key), before.get(key))
                for item in (GLOVES, "Family gauntlets", "Cooking gauntlets", "Chaos gauntlets"):
                    self.assertEqual(player["inventory"].get(item), before["inventory"].get(item))
        for equipment in (None, [], "Goldsmith gauntlets"):
            with self.subTest(malformed_equipment=equipment):
                player = {"equipment": equipment}
                before = copy.deepcopy(player)
                self.assertEqual(goldsmith_smelting_xp_pure(player, GOLD, 22.5), 22.5)
                self.assertEqual(player, before)

    def test_other_smithing_actions_keep_catalog_xp(self):
        for target in ("smelt_silver_bar", "forge_bronze_dagger"):
            with self.subTest(target=target):
                player = _player(target)
                spec = SMITHING_DATA[target]
                self.assertEqual(goldsmith_smelting_xp_pure(player, target, spec["exp"]), spec["exp"])
                before = dict(player["inventory"])
                ctx, calls = self._context(player)
                self.assertTrue(handle_smithing_answer(ctx))
                self.assertEqual(calls["awards"], [("smithing_exp", spec["exp"])])
                for item, count in spec["requirements"].items():
                    self.assertEqual(player["inventory"].get(item, 0), before[item] - count)
                for item, count in spec.get("required_items", {}).items():
                    self.assertEqual(player["inventory"][item], count)
                self.assertEqual(player["inventory"][spec["output_item"]], spec["output_qty"])

    def test_refused_and_failed_actions_award_no_goldsmith_xp(self):
        for case in ("no ore", "level 39", "unknown", "failed iron"):
            with self.subTest(case=case):
                player = _player("smelt_iron_bar" if case == "failed iron" else GOLD)
                if case == "no ore":
                    player["inventory"].pop("Gold ore")
                elif case == "level 39":
                    player["smithing_level"] = 39
                elif case == "unknown":
                    player["current_smith"] = "unknown"
                before = copy.deepcopy(player)
                ctx, calls = self._context(player, rolls=(0.999,))
                self.assertEqual(handle_smithing_answer(ctx), case == "failed iron")
                self.assertEqual(calls["awards"], [])
                self.assertEqual(player["smithing_exp"], 0)
                self.assertEqual(player["equipment"], before["equipment"])
                self.assertEqual(player["inventory"].get("Gold bar", 0), 0)
                self.assertEqual(player["inventory"].get("Iron bar", 0), 0)
                if case == "failed iron":
                    self.assertEqual(player["inventory"].get("Iron ore", 0), 0)
                else:
                    self.assertEqual(player["inventory"], before["inventory"])

    def test_brawling_and_goldsmith_gloves_do_not_stack(self):
        brawling = BRAWLING_GLOVE_DATA["smithing"]["item_name"]
        for worn, banked, expected in ((brawling, GLOVES, 33.75), (GLOVES, brawling, 56.2)):
            with self.subTest(worn=worn):
                player = _player()
                player["equipment"]["hands"] = worn
                player["inventory"][banked] = 1
                player = sanitize_equipment_instance_state_pure(player, EQUIPMENT_CONDITION_DATA)
                before = copy.deepcopy(player["equipment_instances"])
                self.assertEqual(len(before), 1)
                ctx, calls = self._context(player)
                self.assertTrue(handle_smithing_answer(ctx))
                self.assertEqual(calls["awards"], [("smithing_exp", expected)])
                self.assertEqual(player["equipment"]["hands"], worn)
                for instance_id, record in before.items():
                    consumed = int(worn == brawling and record["location"] == "equipped:hands")
                    self.assertEqual(player["equipment_instances"][instance_id]["condition"],
                                     record["condition"] - consumed)
                self.assertEqual(player["inventory"][banked], 1)

    def test_carried_overlay_preserves_bank_and_excludes_gold_from_urns(self):
        tier = URN_TIERS_BY_ID["smithing_strong_urn"]
        for advanced in (False, True):
            for target in (GOLD, "smelt_bronze_bar"):
                with self.subTest(advanced=advanced, target=target):
                    player = _player(target)
                    spec = SMITHING_DATA[target]
                    player["smithing_level"] = 60
                    player["inventory"] = {item: count * 2 for item, count in spec["requirements"].items()}
                    player["inventory"].update({tier.item_active: 1, "Coins": 123, "Ruby": 2})
                    player.update(active_urn_smithing=tier.id, urn_progress_smithing=10.0)
                    _supplied_pack(player, {**spec["requirements"], tier.item_active: 1}, advanced)
                    ctx, calls = self._context(player)
                    self.assertTrue(run_answer_with_carried_overlay(ctx, "smithing", handle_smithing_answer))
                    for item, count in spec["requirements"].items():
                        self.assertEqual(player["inventory"][item], count)
                    self.assertEqual(player["inventory"][spec["output_item"]], 1)
                    self.assertEqual(calls["awards"], [("smithing_exp", 56.2 if target == GOLD else spec["exp"])])
                    self.assertEqual(player["equipment"]["hands"], GLOVES)
                    self.assertEqual(player["inventory"]["Coins"], 123)
                    self.assertEqual(player["inventory"]["Ruby"], 2)
                    self.assertEqual(player["active_urn_smithing"], tier.id)
                    self.assertEqual(player["urn_progress_smithing"], 10.0 + (0 if target == GOLD else spec["exp"]))

    def test_two_bars_receive_two_awards(self):
        player = _player()
        player["inventory"]["Gold ore"] = 2
        ctx, calls = self._context(player)
        for index in range(2):
            with self.subTest(bar=index + 1):
                self.assertTrue(handle_smithing_answer(ctx))
                self.assertEqual(player["inventory"].get("Gold ore", 0), 1 - index)
                self.assertEqual(player["inventory"]["Gold bar"], index + 1)
        self.assertFalse(handle_smithing_answer(ctx))
        self.assertEqual(calls["awards"], [("smithing_exp", 56.2)] * 2)
        self.assertEqual(player["smithing_exp"], 112.4)
        self.assertEqual(player["inventory"]["Gold bar"], 2)

    def test_review_undo_restores_complete_save_and_replay(self):
        addon, collection = self._addon()
        before = self._snapshot(addon, collection)
        _answer_review(addon)
        after = self._snapshot(addon, collection)
        self.assertEqual(after[0]["smithing_exp"], 56.2)
        self.assertEqual(after[0]["inventory"]["Gold bar"], 1)
        self.assertEqual(after[0]["inventory"].get("Gold ore", 0), 0)
        self.assertNotEqual(after[2], before[2])
        addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
        self.assertEqual(self._snapshot(addon, collection), before)
        _answer_review(addon)
        self.assertEqual(self._snapshot(addon, collection), after)

    def test_manual_moves_and_review_undo_remain_in_order(self):
        addon, collection = self._addon(worn=False, ores=2)
        boundaries = [self._snapshot(addon, collection)]
        self.assertTrue(addon.on_equip_item(GLOVES))
        self.assertEqual(addon._state.player_data["equipment"]["hands"], GLOVES)
        self.assertEqual(addon._state.player_data["inventory"][GLOVES], 0)
        boundaries.append(self._snapshot(addon, collection))
        _answer_review(addon)
        self.assertEqual(addon._state.player_data["smithing_exp"], 56.2)
        boundaries.append(self._snapshot(addon, collection))
        self.assertTrue(addon.on_unequip_slot("hands"))
        self.assertFalse(addon._state.player_data["equipment"].get("hands"))
        self.assertEqual(addon._state.player_data["inventory"][GLOVES], 1)
        boundaries.append(self._snapshot(addon, collection))
        _answer_review(addon)
        self.assertEqual(addon._state.player_data["smithing_exp"], 78.7)
        self.assertEqual(addon._state.player_data["inventory"]["Gold bar"], 2)
        for operation, expected in zip(
            ("Answer Card", "AnkiScape direct action", "Answer Card", "AnkiScape direct action"),
            reversed(boundaries),
        ):
            with self.subTest(operation=operation, xp=expected[0]["smithing_exp"]):
                self.assertEqual(addon._state.player_data["cooking_equipment_swap"], {})
                addon._on_state_did_undo(SimpleNamespace(operation=operation))
                self.assertEqual(self._snapshot(addon, collection), expected)
        self.assertEqual(addon._state.player_data["cooking_equipment_swap"], {})
