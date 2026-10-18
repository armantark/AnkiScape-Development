import copy
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.herblore_data import (
    CLEAN_TARGETS,
    DUNGEONEERING_CLEAN_TARGETS,
    DUNGEONEERING_FINISHED_TARGETS,
    DUNGEONEERING_HERBLORE_TARGETS,
    DUNGEONEERING_UNF_TARGETS,
    FINISHED_TARGETS,
    HERBLORE_TARGETS,
    UNF_TARGETS,
    herblore_extra_items_as_dict,
    herblore_targets_as_dict,
)
from ankiscape.logic_pure.logic_pure import apply_herblore_action_pure, can_herblore_target_pure
from tests import test_integration_smoke as runtime_fixture
from tests.test_combat_quest_gate import _answer_review
from tests.test_storage_runtime import Collection


class HerbloreDataTests(unittest.TestCase):
    def test_relicyms_drinkable_mix_reaches_registry_and_market_unchanged(self):
        from ankiscape.core.constants import EXTRA_ITEM_DATA, HERBLORE_EXTRA_ITEM_DATA, ITEM_DEFINITIONS
        from ankiscape.data.grand_exchange_data import GE_ITEM_CATALOG
        from ankiscape.data.item_values import ITEM_VALUES, STACKABLE_ITEM_NAMES

        name = "Relicym's mix (2)"
        for items in (HERBLORE_EXTRA_ITEM_DATA, EXTRA_ITEM_DATA):
            self.assertEqual((items[name]["item_id"], items[name]["tradeable"], items[name]["stackable"]),
                             (11437, True, False))
        item = next(item for item in ITEM_DEFINITIONS if item.storage_key == name)
        self.assertEqual((item.source_item_id, item.tradeable, item.stackable), (11437, True, False))
        spec = GE_ITEM_CATALOG[name]
        self.assertEqual((spec["source_item_id"], spec["guide_price"], spec["buy_limit"]), (11437, 268, 1000))
        self.assertEqual(spec["guide_price_provenance"]["oldid"], 6095907)
        self.assertEqual(spec["buy_limit_source"]["oldid"], 6457777)
        self.assertEqual(ITEM_VALUES[name], 150)
        self.assertNotIn(name, STACKABLE_ITEM_NAMES)
        self.assertEqual({item.storage_key for item in ITEM_DEFINITIONS
                          if item.storage_key.startswith("Relicym's mix")}, {name})

    def test_magic_essence_mix_preserves_its_distinct_item_identity(self):
        target = next(target for target in FINISHED_TARGETS if target.id == "finished_magic_essence_mix")
        self.assertEqual(target.display_name, "Magic essence mix (2)")
        self.assertEqual(target.output_item, "Magic essence mix (2)")
        self.assertEqual(target.requirements, (("Magic essence (2)", 1), ("Caviar", 1)))
        self.assertEqual(herblore_extra_items_as_dict()["Magic essence mix (2)"]["item_id"], 11489)

    def test_shrink_me_quick_is_a_live_period_quest_recipe(self):
        target = next(target for target in FINISHED_TARGETS if target.id == "finished_shrink_me_quick")
        self.assertEqual(target.level, 52)
        self.assertEqual(target.exp, 6.0)
        self.assertEqual(
            target.requirements,
            (("Tarromin potion (unf)", 1), ("Shrunk ogleroot", 1)),
        )
        self.assertEqual(target.output_item, "Shrink-me-quick")

        items = herblore_extra_items_as_dict()
        self.assertEqual(items["Shrink-me-quick"]["item_id"], 11204)
        self.assertFalse(items["Shrink-me-quick"]["tradeable"])
        self.assertFalse(items["Shrink-me-quick"]["stackable"])
        self.assertEqual(items["Shrunk ogleroot"]["item_id"], 11205)
        self.assertTrue(items["Shrunk ogleroot"]["stackable"])

        inventory = {"Tarromin potion (unf)": 1, "Shrunk ogleroot": 1}
        self.assertTrue(
            can_herblore_target_pure(
                52,
                inventory,
                "finished_shrink_me_quick",
                herblore_targets_as_dict(),
            )
        )
        result, exp, ok = apply_herblore_action_pure(
            "finished_shrink_me_quick",
            inventory,
            herblore_targets_as_dict(),
        )
        self.assertTrue(ok)
        self.assertEqual(exp, 6.0)
        self.assertEqual(
            result,
            {
                "Tarromin potion (unf)": 0,
                "Shrunk ogleroot": 0,
                "Shrink-me-quick": 1,
            },
        )

    def test_period_clean_herb_levels_are_pinned(self):
        expected_levels = {
            "clean_guam": 1,
            "clean_marrentill": 5,
            "clean_tarromin": 11,
            "clean_harralander": 20,
            "clean_ranarr": 25,
            "clean_toadflax": 30,
            "clean_spirit_weed": 35,
            "clean_irit": 40,
            "clean_wergali": 41,
            "clean_avantoe": 48,
            "clean_kwuarm": 54,
            "clean_snapdragon": 59,
            "clean_cadantine": 65,
            "clean_lantadyme": 67,
            "clean_dwarf_weed": 70,
            "clean_torstol": 75,
            "clean_fellstalk": 91,
        }
        targets = {target.id: target for target in CLEAN_TARGETS}

        self.assertEqual(
            {target_id: targets[target_id].level for target_id in expected_levels},
            expected_levels,
        )
        self.assertEqual(targets["clean_guam"].exp, 2.5)
        self.assertEqual(
            targets["clean_guam"].source,
            "https://runescape.wiki/w/Grimy_guam?oldid=6560041",
        )

    def test_daemonheim_target_family_is_not_in_overworld_catalog(self):
        herb_ids = {
            "sagawort",
            "featherfoil",
            "valerian",
            "aloe",
            "wormwood",
            "magebane",
            "winter_grip",
            "lycopus",
            "buckthorn",
        }
        self.assertEqual(
            {target.id.removeprefix("clean_") for target in DUNGEONEERING_CLEAN_TARGETS},
            herb_ids,
        )
        self.assertEqual(
            {target.id.removeprefix("unf_") for target in DUNGEONEERING_UNF_TARGETS},
            herb_ids,
        )
        self.assertEqual(len(DUNGEONEERING_CLEAN_TARGETS), 9)
        self.assertEqual(len(DUNGEONEERING_UNF_TARGETS), 9)
        self.assertEqual(len(DUNGEONEERING_FINISHED_TARGETS), 36)
        self.assertEqual(len(DUNGEONEERING_HERBLORE_TARGETS), 54)

        deferred_ids = {target.id for target in DUNGEONEERING_HERBLORE_TARGETS}
        active_ids = {target.id for target in HERBLORE_TARGETS}
        self.assertTrue(deferred_ids.isdisjoint(active_ids))
        self.assertTrue(all(target.subgroup != "dungeoneering" for target in HERBLORE_TARGETS))
        self.assertTrue(deferred_ids.isdisjoint(herblore_targets_as_dict()))

        self.assertEqual(len(CLEAN_TARGETS), 27)
        self.assertEqual(len(UNF_TARGETS), 22)
        self.assertEqual(len(FINISHED_TARGETS), 70)

    def test_daemonheim_item_identities_remain_registered_for_old_saves(self):
        registered_items = herblore_extra_items_as_dict()
        deferred_items = {
            item_name
            for target in DUNGEONEERING_HERBLORE_TARGETS
            for item_name in (
                target.output_item,
                *(name for name, _quantity in target.requirements),
                *(name for name, _quantity in target.byproducts),
            )
        }

        self.assertTrue(deferred_items)
        self.assertTrue(deferred_items.issubset(registered_items))
        self.assertIn("Grimy sagewort", registered_items)
        self.assertIn("Strong survivalist's potion", registered_items)

    def test_daemonheim_recipe_cannot_run_through_overworld_pure_logic(self):
        active_data = herblore_targets_as_dict()
        inventory = {"Grimy sagewort": 1}

        self.assertFalse(can_herblore_target_pure(99, inventory, "clean_sagawort", active_data))
        result, exp, ok = apply_herblore_action_pure("clean_sagawort", inventory, active_data)
        self.assertFalse(ok)
        self.assertEqual(exp, 0)
        self.assertIs(result, inventory)


class RelicymReviewPersistenceTests(unittest.TestCase):
    def setUp(self):
        modules = patch.dict(sys.modules)
        modules.start()
        self.addCleanup(modules.stop)
        runtime_fixture._install_runtime_fakes()

    def _open(self, collection):
        self.collection = collection
        sys.modules["aqt"].mw = runtime_fixture._DummyMW(collection)
        self.addon = runtime_fixture._load_addon_as_package("ankiscape_relicym_review")
        addon = self.addon
        addon.load_player_data()
        addon.update_review_hud = lambda *_args: None
        addon._refresh_skill_availability = lambda: None
        addon._update_review_context_surface = lambda: None
        addon._show_exp = lambda *_args: None
        addon.check_achievements = lambda _data: None
        addon.show_error_message = lambda _title, message: self.fail(message)

    def _reload(self):
        addon = self.addon
        addon.save_player_data()
        if isinstance(self.collection, runtime_fixture._DummyCol):
            self.collection._store = json.loads(json.dumps(self.collection._store))
        else:
            self.collection.close()
            self.collection.reopen()
        addon.load_player_data()

    def _assert_recipe_at_capacity(self):
        addon = self.addon
        target, name = "finished_relicyms_mix", "Relicym's mix (2)"
        pack = {name: 26, "Relicym's balm (2)": 1, "Roe": 1}
        player = addon._state.player_data
        player.update(inventory={name: 30, "Relicym's balm (2)": 10, "Roe": 10, "Coins": 7},
                      herblore_level=99, herblore_exp=13034431, current_herblore=target,
                      carried_advanced_targets={target: True}, carried_layout={target: pack})
        addon._state.current_skill = "Herblore"
        self._reload()
        before = copy.deepcopy(addon._state.player_data), addon._state.current_skill
        _answer_review(addon)
        after = copy.deepcopy(addon._state.player_data), addon._state.current_skill
        self.assertEqual(after[0]["inventory"], before[0]["inventory"]
                         | {name: 31, "Relicym's balm (2)": 9, "Roe": 9})
        self.assertEqual(after[0]["herblore_exp"], 13034445)
        self.assertEqual(after[0]["carried_inventory"][target], {name: 26})
        self.assertEqual(after[0]["carried_churn"][target], 2)
        self._reload()
        self.assertEqual((addon._state.player_data, addon._state.current_skill), after)
        addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card"))
        self.assertEqual((addon._state.player_data, addon._state.current_skill), before)
        _answer_review(addon)
        self.assertEqual((addon._state.player_data, addon._state.current_skill), after)

    def _assert_saved_active_pack(self):
        addon = self.addon
        plunder = sys.modules[f"{addon.__name__}.logic.pyramid_plunder_logic"]
        target, name = plunder.PYRAMID_PLUNDER_ACTIVITY_ID, "Relicym's mix (2)"
        player = addon._state.player_data
        player.update(thieving_level=91, inventory={name: 30, "Shark": 2, "Coins": 7},
                      carried_advanced_targets={target: True}, carried_layout={target: {name: 30}})
        player["quests"]["icthlarins_little_helper"] = {"started": True, "completed": False}
        player, entered, info = plunder.enter_pyramid_plunder_pure(player)
        self.assertTrue(entered, info)
        self.assertEqual(info["pack"], {name: 28})
        player["carried_inventory"] = {target: {name: 30}, "other_target": {"Shark": 1}}
        addon._state.player_data, addon._state.current_skill = player, "Activities"
        before = copy.deepcopy(player)
        self.assertEqual(plunder.pyramid_plunder_view_pure(player)["pack_slots"], 28)
        self.assertEqual(player, before)
        self._reload()
        loaded = copy.deepcopy(addon._state.player_data)
        self.assertEqual(loaded["carried_inventory"], {target: {name: 28}, "other_target": {"Shark": 1}})
        self.assertEqual(loaded["carried_layout"][target], {name: 30})
        self.assertEqual({item: qty for item, qty in loaded["inventory"].items() if qty > 0},
                         before["inventory"])
        self._reload()
        self.assertEqual((addon._state.player_data, addon._state.current_skill), (loaded, "Activities"))

    def test_recipe_and_old_pack_preserve_ownership_undo_and_reload(self):
        self._open(runtime_fixture._DummyCol())
        self._assert_recipe_at_capacity()
        self._assert_saved_active_pack()

    @unittest.skipIf(Collection is None, "Anki runtime is not installed")
    def test_recipe_and_old_pack_survive_real_collection_close_and_reopen(self):
        with tempfile.TemporaryDirectory() as directory:
            collection = Collection(str(Path(directory) / "collection.anki2"))
            try:
                self._open(collection)
                self._assert_recipe_at_capacity()
                self._assert_saved_active_pack()
            finally:
                collection.close()


if __name__ == "__main__":
    unittest.main()
