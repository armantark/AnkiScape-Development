import sys
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import (
    ITEM_DEFINITIONS,
    ORE_DATA,
    QUEST_DATA,
    QUEST_UNLOCK_RULES,
    UTILITY_ACTIVITY_DATA,
)
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.agility_data import AGILITY_TARGETS_BY_ID
from ankiscape.data.shop_data import SHOP_DATA
from ankiscape.logic.agility_logic import default_agility_state_pure
from ankiscape.logic.shop_logic import apply_shop_buy_pure, shop_access_lock_reason_pure
from ankiscape.logic_pure.logic_pure_production import (
    apply_utility_activity_pure,
    utility_activity_locked_reasons_pure,
)
from ankiscape.logic_pure.logic_pure_quest import (
    start_quest_pure,
    target_unlock_locked_reasons_pure,
)
from ankiscape.runtime.runtime_actions import handle_agility_answer
from tests.test_integration_smoke import (
    _FakeReviewer,
    _install_runtime_fakes,
    _load_addon_as_package,
)
from tests.quest_action_proof_helpers import quest_action_proofs_for_quest
from tests.test_runtime_actions import _context
from tests.reachability.live_report import live_reachability_report


ROOT_ROUTES = {
    "Karamjan rum": "shop:karamja_wines_spirits_and_beers",
    "Ugthanki dung": "Utility:collect_ugthanki_dung",
    "Pyramid top": "Agility:agility_pyramid:retrieve_top",
    "Raw karambwan": "shop:tiadeches_karambwan_stall",
    "Fish food": "Utility:collect_fish_food",
    "Insect repellent": "Utility:collect_insect_repellent",
}

DOWNSTREAM_QUEST_ROUTES = {
    "Blamish oil": "quest-stage:heroes_quest:3",
    "Blamish snail slime": "quest-stage:heroes_quest:2",
    "Bucket of wax": "quest-stage:merlins_crystal:4",
    "Casket (Pirate's Treasure)": "quest:pirates_treasure",
    "Excalibur": "quest-stage:merlins_crystal:6",
    "Fire feather": "quest-stage:heroes_quest:8",
    "Grail bell": "quest-stage:holy_grail:5",
    "Grimy key": "quest-stage:ernest_the_chicken:5",
    "Holy grail": "quest-stage:holy_grail:9",
    "Holy table napkin": "quest-stage:holy_grail:3",
    "Ice gloves": "quest-stage:heroes_quest:7",
    "Id papers": "quest-stage:heroes_quest:9",
    "Magic gold feather": "quest-stage:holy_grail:7",
    "Magic whistle": "quest-stage:holy_grail:4",
    "Oil can": "quest-stage:ernest_the_chicken:7",
    "Oily fishing rod": "quest-stage:heroes_quest:4",
    "Pete's candlestick": "quest-stage:heroes_quest:10",
    "Poisoned fish food": "quest-stage:ernest_the_chicken:3",
    "Pressure gauge": "quest-stage:ernest_the_chicken:4",
    "Rubber tube": "quest-stage:ernest_the_chicken:6",
    "Thieves' armband": "quest-stage:heroes_quest:11",
}


def _answer_review(addon):
    addon._state.card_turned = True
    addon._state.answer_shown = True
    addon._state.exp_awarded = False
    addon.on_answer_card(
        _FakeReviewer(),
        4,
        lambda _self, _ease: "answered",
    )


class TestEarlyQuestItemReachability(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = live_reachability_report()

    def test_each_repaired_root_has_a_live_route(self):
        for item_name, route in ROOT_ROUTES.items():
            with self.subTest(item_name=item_name):
                self.assertEqual(self.report["routes"].get(item_name), route)

    def test_newly_reachable_quest_products_have_expected_routes(self):
        for item_name, route in DOWNSTREAM_QUEST_ROUTES.items():
            with self.subTest(item_name=item_name):
                self.assertEqual(self.report["routes"].get(item_name), route)

    def test_agility_pyramid_full_lap_credits_pyramid_top_to_inventory(self):
        player = {
            **default_agility_state_pure(),
            "current_agility": "agility_pyramid",
            "agility_level": 30,
            "agility_exp": 0.0,
            "inventory": {},
            "equipment": {},
            "completed_achievements": [],
        }
        calls = {"xp": [], "saves": 0, "errors": []}

        for _stage in AGILITY_TARGETS_BY_ID["agility_pyramid"].stages:
            self.assertTrue(
                handle_agility_answer(
                    _context(
                        player,
                        calls,
                        random_values=(0.99, 0.99, 0.99, 0.99),
                    )
                )
            )

        self.assertEqual(player["inventory"]["Pyramid top"], 1)
        self.assertEqual(player["agility_lap_counts"]["total"], 1)

    def test_ugthanki_dung_is_a_registered_source_item(self):
        definition = next(
            item for item in ITEM_DEFINITIONS if item.storage_key == "Ugthanki dung"
        )

        self.assertEqual(definition.source_item_id, 4601)
        self.assertFalse(definition.stackable)
        self.assertFalse(definition.tradeable)

    def test_world_acquisition_actions_produce_the_registered_items(self):
        for activity_id, inventory, output_item in (
            ("collect_fish_food", {}, "Fish food"),
            ("collect_insect_repellent", {}, "Insect repellent"),
            ("collect_ugthanki_dung", {"Bucket": 1}, "Ugthanki dung"),
        ):
            with self.subTest(activity_id=activity_id):
                updated, exp, ok, processed = apply_utility_activity_pure(
                    activity_id, inventory, UTILITY_ACTIVITY_DATA
                )
                self.assertTrue(ok)
                self.assertEqual(exp, 0)
                self.assertEqual(processed, 1)
                self.assertEqual(updated[output_item], 1)
                if activity_id == "collect_ugthanki_dung":
                    self.assertEqual(updated["Bucket"], 0)

    def test_ugthanki_route_unlocks_when_the_feud_starts(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["inventory"]["Bucket"] = 1

        self.assertEqual(
            utility_activity_locked_reasons_pure(
                player,
                "collect_ugthanki_dung",
                UTILITY_ACTIVITY_DATA,
                QUEST_UNLOCK_RULES,
            ),
            ("Start The Feud",),
        )
        player["quests"]["the_feud"] = {
            "started": True,
            "progress": 0,
            "completed": False,
        }
        self.assertEqual(
            utility_activity_locked_reasons_pure(
                player,
                "collect_ugthanki_dung",
                UTILITY_ACTIVITY_DATA,
                QUEST_UNLOCK_RULES,
            ),
            (),
        )

    def test_karambwan_fishing_and_shop_unlock_when_the_quest_starts(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["quests"]["tai_bwo_wannai_trio"] = {
            "started": True,
            "progress": 0,
            "completed": False,
        }

        self.assertEqual(
            target_unlock_locked_reasons_pure(
                player,
                "fishing",
                "catch_karambwan",
                QUEST_UNLOCK_RULES,
            ),
            (),
        )
        self.assertIsNone(
            shop_access_lock_reason_pure(
                player,
                SHOP_DATA["tiadeches_karambwan_stall"],
            )
        )


class TestPiratesTreasureRepairedProductFlow(unittest.TestCase):
    def setUp(self):
        self._original_modules = dict(sys.modules)
        _install_runtime_fakes()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._original_modules)

    def test_shop_bought_rum_completes_through_real_review_answers(self):
        player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        player["inventory"].update({"Coins": 100, "Spade": 1})
        player, purchase = apply_shop_buy_pure(
            player,
            "karamja_wines_spirits_and_beers",
            "karamja_wines_spirits_and_beers:2:431",
            1,
        )
        self.assertTrue(purchase["allowed"])
        self.assertEqual(player["inventory"]["Karamjan rum"], 1)
        player, started = start_quest_pure(player, "pirates_treasure", QUEST_DATA)
        self.assertTrue(started)

        addon = _load_addon_as_package("ankiscape_early_quest_items_e2e")
        addon.check_achievements = lambda _data: None
        addon.save_player_data = lambda: None
        addon._refresh_skill_availability = lambda: None
        addon._show_activity_gain = lambda _text: None
        addon._show_exp = lambda _amount: None
        addon.level_up_check = lambda _skill, _data: None
        addon.update_review_hud = lambda _data, _skill: None
        addon.show_error_message = lambda _title, _message: None
        addon._state.player_data = player
        addon._state.current_skill = "Quests"
        addon._state.review_undo_stack.clear()
        addon._state.direct_action_undo_stack.clear()

        for _review in range(3):
            _answer_review(addon)

        self.assertTrue(addon._state.player_data["quests"]["pirates_treasure"]["completed"])
        self.assertEqual(addon._state.player_data["inventory"]["Karamjan rum"], 0)
        self.assertEqual(addon._state.player_data["inventory"]["Casket (Pirate's Treasure)"], 1)
        self.assertEqual(
            quest_action_proofs_for_quest(addon._state.player_data, "pirates_treasure", QUEST_DATA),
            (
                "Smuggle Karamjan rum off Karamja",
                "Open One-Eyed Hector's chest at the Blue Moon Inn",
                "Read the pirate message and dig in Falador Park",
            ),
        )


if __name__ == "__main__":
    unittest.main()
