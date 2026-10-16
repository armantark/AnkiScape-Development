"""Locked shops follow open shops throughout a search and name their wall."""

import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.search_match import match_rank
from ankiscape.data.shop_data import SHOP_DATA
from ankiscape.logic.shop_fixtures import build_shop_fixture_player_data
from ankiscape.logic.shop_logic import search_shop_catalog_pure, shop_selector_entries_pure

VISIBLE_SHOP_IDS = [shop_id for shop_id, shop in SHOP_DATA.items() if shop["visibility"] != "hidden"]


class LockedShopOrderTest(unittest.TestCase):
    def _canifis(self, data: dict) -> tuple[dict, bool]:
        """Canifis's entry, and whether it sits in the open block."""
        entries = shop_selector_entries_pure(data, VISIBLE_SHOP_IDS)
        locked = [entry["locked"] for entry in entries]
        self.assertEqual(locked, sorted(locked), "a locked shop sits among open ones")
        index = next(index for index, entry in enumerate(entries) if entry["shop_id"] == "canifis_general_store")
        return entries[index], index < locked.index(True)

    def test_browse_list_moves_a_shop_into_the_open_block_when_its_quest_completes(self) -> None:
        data = build_shop_fixture_player_data()
        canifis, in_open_block = self._canifis(data)
        self.assertTrue(canifis["locked"])
        self.assertEqual(canifis["label"], "Canifis General Store · Requires Priest in Peril")
        self.assertFalse(in_open_block)

        data["quests"] = {"priest_in_peril": {"started": True, "progress": 1, "completed": True}}
        canifis, in_open_block = self._canifis(data)
        self.assertFalse(canifis["locked"])
        self.assertRegex(canifis["label"], r"^Canifis General Store · \d+ live · general store$")
        self.assertTrue(in_open_block)

    def test_search_cut_keeps_every_open_row_and_names_each_locked_rows_wall(self) -> None:
        data = build_shop_fixture_player_data()
        everything = search_shop_catalog_pure(data, "fish", limit=10_000)["results"]
        open_rows = [result for result in everything if not result["lock_reason"]]
        locked_rows = [result for result in everything if result["lock_reason"]]
        self.assertIn(
            ("Etceteria Fish", "Requires The Fremennik Trials"),
            [(row.get("shop_name"), row["lock_reason"]) for row in locked_rows],
        )

        def rank(row):
            return match_rank("fish", row.get("item_name", row.get("display_name", "")),
                              row.get("shop_name", ""), row.get("provider", ""))

        locked = [bool(row["lock_reason"]) for row in everything]
        self.assertEqual(locked, sorted(locked), "a locked row sits among open stock")
        for rows in (open_rows, locked_rows):
            keys = [(rank(row), row.get("item_name", row.get("display_name", "")).casefold(),
                     row.get("shop_name", "").casefold()) for row in rows]
            self.assertEqual(keys, sorted(keys))
        cut = search_shop_catalog_pure(data, "fish", limit=len(open_rows))["results"]
        self.assertEqual(cut, open_rows)


if __name__ == "__main__":
    unittest.main()
