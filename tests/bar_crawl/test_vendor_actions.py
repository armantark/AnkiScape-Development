import copy
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data import quest_action_proof_data as proofs
from ankiscape.data.shop_data import SHOP_VENDOR_ACTIONS
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
                self.assertEqual(set(action), set(SHOP_VENDOR_ACTIONS["benny_buy_varrock_herald"]))
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
                    before = copy.deepcopy(player)
                    updated, result = apply_shop_vendor_action_pure(player, action_id)

                    self.assertFalse(result["allowed"])
                    self.assertEqual(result["reason"], "missing_requirements")
                    self.assertEqual(updated, before)
                    self.assertEqual(player, before)

    def test_successive_purchases_add_no_other_drinks_proofs(self):
        player = {"inventory": {"Coins": sum(row[1] for row in BAR_CRAWL_PURCHASES)}}
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
