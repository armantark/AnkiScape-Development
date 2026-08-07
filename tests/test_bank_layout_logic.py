import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic.bank_layout_logic import (
    bank_sections_pure,
    create_bank_tab_pure,
    delete_bank_tab_pure,
    move_bank_item_pure,
    reconcile_bank_layout_state_pure,
    rename_bank_tab_pure,
    reorder_bank_tab_pure,
    set_bank_tab_icon_pure,
)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import CURRENT_CONFIG_VERSION, migrate_loaded_data


class BankLayoutLogicTest(unittest.TestCase):
    def _state(self):
        return reconcile_bank_layout_state_pure(
            {},
            {"Coal": 214, "Oak logs": 8, "Lobster": 3},
            answered_reviews=12,
        )

    def test_reconcile_assigns_one_home_and_uses_answered_review_counters(self):
        state = self._state()
        self.assertEqual([tab["id"] for tab in state["tabs"]], ["main"])
        self.assertEqual(
            [state["items"][name]["position"] for name in state["items"]],
            [0, 1, 2],
        )
        self.assertEqual(state["items"]["Coal"]["added_review"], 12)
        self.assertEqual(state["items"]["Coal"]["used_review"], 12)

        unchanged = reconcile_bank_layout_state_pure(
            state,
            {"Coal": 214, "Oak logs": 8, "Lobster": 3},
            answered_reviews=99,
        )
        self.assertEqual(unchanged["items"]["Coal"]["used_review"], 12)

        changed = reconcile_bank_layout_state_pure(
            unchanged,
            {"Coal": 215, "Oak logs": 8, "Lobster": 3, "Shrimp": 1},
            answered_reviews=100,
        )
        self.assertEqual(changed["items"]["Coal"]["added_review"], 12)
        self.assertEqual(changed["items"]["Coal"]["used_review"], 100)
        self.assertEqual(changed["items"]["Shrimp"]["added_review"], 100)
        self.assertEqual(changed["items"]["Shrimp"]["position"], 3)

    def test_swap_insert_and_empty_custom_tab_auto_delete(self):
        state = self._state()
        state, tab_id = create_bank_tab_pure(state, "Coal")
        self.assertEqual(state["items"]["Coal"]["tab_id"], tab_id)

        state = move_bank_item_pure(state, "Oak logs", tab_id, 0, "insert")
        self.assertEqual(
            sorted(
                (
                    (row["position"], name)
                    for name, row in state["items"].items()
                    if row["tab_id"] == tab_id
                )
            ),
            [(0, "Oak logs"), (1, "Coal")],
        )
        state = move_bank_item_pure(state, "Coal", tab_id, 0, "swap")
        self.assertEqual(state["items"]["Coal"]["position"], 0)
        self.assertEqual(state["items"]["Oak logs"]["position"], 1)

        unchanged = move_bank_item_pure(state, "Coal", tab_id, 0, "swap")
        self.assertEqual(unchanged, state)
        state = move_bank_item_pure(state, "Coal", tab_id, 1, "swap")
        self.assertEqual(state["items"]["Oak logs"]["position"], 0)
        self.assertEqual(state["items"]["Coal"]["position"], 1)

        state = move_bank_item_pure(state, "Coal", "main", 0, "insert")
        state = move_bank_item_pure(state, "Oak logs", "main", 0, "insert")
        self.assertEqual([tab["id"] for tab in state["tabs"]], ["main"])

    def test_tab_customization_reorder_and_delete_return_items_to_main(self):
        state = self._state()
        state, first_id = create_bank_tab_pure(state, "Coal")
        state, second_id = create_bank_tab_pure(state, "Oak logs")
        state = rename_bank_tab_pure(state, first_id, "Ore")
        state = set_bank_tab_icon_pure(state, first_id, "Lobster", {"Lobster": 3})
        state = reorder_bank_tab_pure(state, second_id, 1)
        self.assertEqual([tab["id"] for tab in state["tabs"]], ["main", second_id, first_id])
        self.assertEqual(state["tabs"][2]["name"], "Ore")
        self.assertEqual(state["tabs"][2]["icon_item"], "Lobster")
        self.assertEqual(
            set_bank_tab_icon_pure(state, first_id, "Shrimp", {"Lobster": 3}),
            state,
        )

        state = delete_bank_tab_pure(state, first_id)
        self.assertEqual(state["items"]["Coal"]["tab_id"], "main")
        self.assertNotIn(first_id, [tab["id"] for tab in state["tabs"]])

    def test_each_sort_mode_orders_a_seeded_fixture_inside_categories(self):
        state = self._state()
        state["items"]["Coal"].update(added_review=3, used_review=5)
        state["items"]["Oak logs"].update(added_review=7, used_review=4)
        state["items"]["Lobster"].update(added_review=2, used_review=9)
        inventory = {"Coal": 214, "Oak logs": 8, "Lobster": 3}
        categories = {"Coal": "Ores", "Oak logs": "Logs", "Lobster": "Food"}
        values = {"Coal": 100, "Oak logs": 20, "Lobster": 80}

        expected = {
            "manual": ["Coal", "Oak logs", "Lobster"],
            "mru": ["Lobster", "Coal", "Oak logs"],
            "date_added": ["Oak logs", "Coal", "Lobster"],
            "alphabetical": ["Coal", "Lobster", "Oak logs"],
            "quantity": ["Coal", "Oak logs", "Lobster"],
            "value": ["Coal", "Lobster", "Oak logs"],
        }
        for sort_mode, order in expected.items():
            with self.subTest(sort_mode=sort_mode):
                sections = bank_sections_pure(
                    state,
                    inventory,
                    "main",
                    sort_mode,
                    auto_categories=False,
                    categories=categories,
                    values=values,
                )
                self.assertEqual([row["name"] for row in sections[0]["items"]], order)

        categorized = bank_sections_pure(
            state,
            inventory,
            "main",
            "alphabetical",
            auto_categories=True,
            categories=categories,
            values=values,
        )
        self.assertEqual([section["label"] for section in categorized], ["Ores", "Logs", "Food"])

    def test_save_reload_preserves_one_home_tab_and_review_counters(self):
        state = self._state()
        state = set_bank_tab_icon_pure(state, "main", "Lobster", {"Lobster": 3})
        state, tab_id = create_bank_tab_pure(state, "Coal")
        state = rename_bank_tab_pure(state, tab_id, "Ore")
        state = set_bank_tab_icon_pure(state, tab_id, "Lobster", {"Lobster": 3})
        state["selected_tab"] = tab_id
        state["sort_mode"] = "quantity"
        state["drop_mode"] = "insert"
        state["auto_categories"] = False
        loaded = migrate_loaded_data(
            {
                "config_version": CURRENT_CONFIG_VERSION,
                "inventory": {"Coal": 214, "Oak logs": 8, "Lobster": 3},
                "shop_market_clock": {"answered_cards": 12},
                "bank_layout": state,
            },
            ORE_DATA,
            ITEM_DEFINITIONS,
        )
        self.assertEqual(loaded["bank_layout"]["items"]["Coal"]["tab_id"], tab_id)
        self.assertEqual(loaded["bank_layout"]["items"]["Coal"]["added_review"], 12)
        self.assertEqual(loaded["bank_layout"]["items"]["Coal"]["used_review"], 12)
        self.assertEqual(loaded["bank_layout"]["tabs"][0]["icon_item"], "Lobster")
        self.assertEqual(loaded["bank_layout"]["tabs"][1]["name"], "Ore")
        self.assertEqual(loaded["bank_layout"]["tabs"][1]["icon_item"], "Lobster")
        self.assertEqual(loaded["bank_layout"]["selected_tab"], tab_id)
        self.assertEqual(loaded["bank_layout"]["sort_mode"], "quantity")
        self.assertEqual(loaded["bank_layout"]["drop_mode"], "insert")
        self.assertFalse(loaded["bank_layout"]["auto_categories"])

    def test_new_items_append_after_even_a_corrupt_large_saved_position(self):
        raw = self._state()
        raw["items"]["Lobster"]["position"] = 2_000_000
        raw["items"]["Lobster"]["tab_id"] = "missing-tab"
        raw["tabs"][0]["icon_item"] = "Unowned"
        state = reconcile_bank_layout_state_pure(
            raw,
            {"Coal": 214, "Oak logs": 8, "Lobster": 3, "Shrimp": 1},
            answered_reviews=13,
        )
        ordered = sorted(
            (row["position"], name) for name, row in state["items"].items()
        )
        self.assertEqual(ordered[-1], (3, "Shrimp"))
        self.assertEqual(state["tabs"][0]["icon_item"], "")


if __name__ == "__main__":
    unittest.main()
