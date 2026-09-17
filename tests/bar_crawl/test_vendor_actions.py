import copy
from pathlib import Path
import runpy
import tempfile
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import QUEST_DATA
from ankiscape.logic_pure.logic_pure import start_quest_pure
from ankiscape.data import quest_action_proof_data as proofs
from ankiscape.data.shop_data import SHOP_VENDOR_ACTIONS
from tools import generate_npc_shop_data as generator
from ankiscape.logic.shop_logic import (
    apply_shop_vendor_action_pure,
    default_shop_state_pure,
)


BAR_CRAWL_PURCHASES = (
    (
        'bar_crawl_blue_moon_inn_uncle_humphreys_gutrot',
        50,
        proofs.BAR_CRAWL_BLUE_MOON_INN_PROOF,
        "Drink Uncle Humphrey's Gutrot at Blue Moon Inn",
    ),
    (
        'bar_crawl_blurberrys_bar_fire_toad_blast',
        10,
        proofs.BAR_CRAWL_BLURBERRYS_BAR_PROOF,
        "Drink Fire Toad Blast at Blurberry's Bar",
    ),
    (
        'bar_crawl_dead_mans_chest_supergrog',
        15,
        proofs.BAR_CRAWL_DEAD_MANS_CHEST_PROOF,
        "Drink Supergrog at Dead Man's Chest",
    ),
    (
        'bar_crawl_dragon_inn_fire_brandy',
        12,
        proofs.BAR_CRAWL_DRAGON_INN_PROOF,
        'Drink Fire Brandy at Dragon Inn',
    ),
    (
        'bar_crawl_flying_horse_inn_heart_stopper',
        8,
        proofs.BAR_CRAWL_FLYING_HORSE_INN_PROOF,
        'Drink Heart Stopper at Flying Horse Inn',
    ),
    (
        'bar_crawl_foresters_arms_liverbane_ale',
        18,
        proofs.BAR_CRAWL_FORESTERS_ARMS_PROOF,
        "Drink Liverbane Ale at Forester's Arms",
    ),
    (
        'bar_crawl_jolly_boar_inn_olde_suspiciouse',
        10,
        proofs.BAR_CRAWL_JOLLY_BOAR_INN_PROOF,
        'Drink Olde Suspiciouse at Jolly Boar Inn',
    ),
    (
        'bar_crawl_karamja_wines_spirits_and_beers_ape_bite_liqueur',
        7,
        proofs.BAR_CRAWL_KARAMJA_WINES_SPIRITS_AND_BEERS_PROOF,
        'Drink Ape Bite Liqueur at Karamja Wines, Spirits, and Beers',
    ),
    (
        'bar_crawl_rising_sun_hand_of_death_cocktail',
        70,
        proofs.BAR_CRAWL_RISING_SUN_PROOF,
        'Drink Hand of Death Cocktail at Rising Sun',
    ),
    (
        'bar_crawl_rusty_anchor_black_skull_ale',
        8,
        proofs.BAR_CRAWL_RUSTY_ANCHOR_PROOF,
        'Drink Black Skull Ale at Rusty Anchor',
    ),
)


class TestBarCrawlVendorActions(unittest.TestCase):
    def _start(self, player):
        player, started = start_quest_pure(player, "bar_crawl", QUEST_DATA)
        self.assertTrue(started)
        return player

    def test_generator_owns_drinks_and_preserves_the_pinned_shop_snapshot(self):
        root = Path(__file__).resolve().parents[2]
        shipped = root / "data" / "shop_data.py"
        before = runpy.run_path(str(shipped))
        expected_ids = {row[0] for row in BAR_CRAWL_PURCHASES}
        self.assertEqual(
            {row["id"] for row in generator.VENDOR_ACTIONS if row["id"].startswith("bar_crawl_")},
            expected_ids,
        )
        items = {995: ("Coins", True)}
        for action in SHOP_VENDOR_ACTIONS.values():
            for row in action["inputs"] + action["outputs"]:
                items[row["item_id"]] = (row["item_name"], row["tradeable"])
        with tempfile.TemporaryDirectory(dir=root / "tmp") as directory:
            directory = Path(directory)
            items_path = directory / "items.yml"
            items_path.write_text("".join(
                f"- id: {item_id}\n  name: {name}\n  tradeable: {str(tradeable).lower()}\n"
                for item_id, (name, tradeable) in items.items()
            ))
            output = directory / "shop_data.py"
            generator.rewrite_services_from_generated(
                shipped, output, items_path, vendor_actions_only=True,
            )
            first = output.read_bytes()
            generator.rewrite_services_from_generated(
                output, output, items_path, vendor_actions_only=True,
            )
            self.assertEqual(output.read_bytes(), first)
            after = runpy.run_path(str(output))
            self.assertEqual(after["SHOP_VENDOR_ACTIONS"], SHOP_VENDOR_ACTIONS)
            self.assertEqual(
                {key for key in after["SHOP_VENDOR_ACTIONS"] if key.startswith("bar_crawl_")},
                expected_ids,
            )
            for key in before:
                if key.isupper() and key != "SHOP_VENDOR_ACTIONS":
                    with self.subTest(catalog=key):
                        self.assertEqual(after[key], before[key])

    def test_unstarted_crawl_refuses_every_drink_without_mutating_state(self):
        for action_id, price, _, _ in BAR_CRAWL_PURCHASES:
            with self.subTest(action_id=action_id):
                player = {
                    **default_shop_state_pure(),
                    "inventory": {"Coins": price},
                    "quest_action_proofs": [],
                }
                before = copy.deepcopy(player)
                updated, result = apply_shop_vendor_action_pure(player, action_id)
                self.assertFalse(result["allowed"])
                self.assertEqual(result["reason"], "Requires starting Alfred Grimhand's Barcrawl")
                self.assertEqual(updated, before)
                self.assertEqual(player, before)

    def test_catalog_and_proof_bindings_match_the_source_boundary(self):
        action_ids = {row[0] for row in BAR_CRAWL_PURCHASES}
        self.assertEqual(
            {key for key in SHOP_VENDOR_ACTIONS if key.startswith("bar_crawl_")},
            action_ids,
        )
        self.assertEqual(len({row[2] for row in BAR_CRAWL_PURCHASES}), 10)
        for action_id, price, proof, expected_proof in BAR_CRAWL_PURCHASES:
            with self.subTest(action_id=action_id):
                action = SHOP_VENDOR_ACTIONS[action_id]
                self.assertEqual(set(action), set(SHOP_VENDOR_ACTIONS["benny_buy_varrock_herald"]) | {"access"})
                self.assertEqual(action["access"], {
                    "kind": "quest", "quest_id": "bar_crawl", "stage": "started",
                    "label": "Alfred Grimhand's Barcrawl",
                })
                self.assertEqual(action["id"], action_id)
                self.assertEqual(action["price"], price)
                self.assertEqual(action["currency_id"], 995)
                self.assertEqual(action["currency_item_name"], "Coins")
                self.assertEqual(action["action_type"], "direct_purchase")
                self.assertEqual(action["inputs"], [])
                self.assertEqual(action["outputs"], [])
                self.assertIn(
                    "memory-bank/source-audits/bar-crawl-harvest-2026-09-02.md",
                    action["source"],
                )
                self.assertEqual(proof, expected_proof)
                self.assertEqual(
                    proofs.QUEST_ACTION_PROOF_RULES[("shop_vendor_action", action_id)],
                    ((), (proof,)),
                )

    def test_each_purchase_spends_only_its_price_and_emits_only_its_proof(self):
        for action_id, price, proof, _ in BAR_CRAWL_PURCHASES:
            for coins in (price, price + 1):
                with self.subTest(action_id=action_id, coins=coins):
                    player = {"inventory": {"Coins": coins, "Beer": 2}, "quest_action_proofs": []}
                    player = self._start(player)
                    before = copy.deepcopy(player)
                    updated, result = apply_shop_vendor_action_pure(player, action_id)

                    self.assertTrue(result["allowed"])
                    self.assertEqual(result["total_price"], price)
                    self.assertEqual(updated["inventory"].get("Coins", 0), coins - price)
                    self.assertEqual(
                        {name: quantity for name, quantity in updated["inventory"].items() if name != "Coins"},
                        {"Beer": 2},
                    )
                    self.assertEqual(updated["quest_action_proofs"], [proof])
                    self.assertEqual(updated["shop_events"][-1]["inventory_delta"], {"Coins": -price})
                    self.assertEqual(player, before)

    def test_insufficient_coins_refuse_each_purchase_without_proofs_or_events(self):
        for action_id, price, _, _ in BAR_CRAWL_PURCHASES:
            for coins in (0, price - 1):
                with self.subTest(action_id=action_id, coins=coins):
                    player = {**default_shop_state_pure(), "inventory": {"Coins": coins}, "quest_action_proofs": []}
                    player = self._start(player)
                    before = copy.deepcopy(player)
                    updated, result = apply_shop_vendor_action_pure(player, action_id)

                    self.assertFalse(result["allowed"])
                    self.assertEqual(result["reason"], "missing_requirements")
                    self.assertEqual(updated, before)
                    self.assertEqual(player, before)

    def test_successive_purchases_add_no_other_drinks_proofs(self):
        player = {"inventory": {"Coins": sum(row[1] for row in BAR_CRAWL_PURCHASES)}}
        player = self._start(player)
        expected_proofs = set()
        for action_id, _, proof, _ in BAR_CRAWL_PURCHASES:
            with self.subTest(action_id=action_id):
                player, result = apply_shop_vendor_action_pure(player, action_id)
                self.assertTrue(result["allowed"])
                expected_proofs.add(proof)
                self.assertEqual(player["quest_action_proofs"], sorted(expected_proofs))
        self.assertEqual(player["inventory"].get("Coins", 0), 0)


if __name__ == "__main__":
    unittest.main()
