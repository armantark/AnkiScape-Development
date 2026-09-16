"""Bindings from genuine player actions to durable quest proofs."""

DO_NO_EVIL_MAMULET_MOULD_PROOF = (
    "Recover an m'amulet mould before making the monkeyspeak amulet"
)
FREMENNIK_ISLES_YAK_HIDE_PROOF = "Cure and stitch yak-hide armour"
MOURNER_FOOD_STORES_PROOF = "Use the rotten apple to sabotage the mourner food stores"
BIOHAZARD_CAULDRON_ACTION = "Put the rotten apple in the Mourner HQ cauldron"
THAKKRAD_CURED_YAK_HIDE_PROOF = "Cure yak-hide with Thakkrad"

BAR_CRAWL_BLUE_MOON_INN_PROOF = "Drink Uncle Humphrey's Gutrot at Blue Moon Inn"
BAR_CRAWL_BLURBERRYS_BAR_PROOF = "Drink Fire Toad Blast at Blurberry's Bar"
BAR_CRAWL_DEAD_MANS_CHEST_PROOF = "Drink Supergrog at Dead Man's Chest"
BAR_CRAWL_DRAGON_INN_PROOF = "Drink Fire Brandy at Dragon Inn"
BAR_CRAWL_FLYING_HORSE_INN_PROOF = "Drink Heart Stopper at Flying Horse Inn"
BAR_CRAWL_FORESTERS_ARMS_PROOF = "Drink Liverbane Ale at Forester's Arms"
BAR_CRAWL_JOLLY_BOAR_INN_PROOF = "Drink Olde Suspiciouse at Jolly Boar Inn"
BAR_CRAWL_KARAMJA_WINES_SPIRITS_AND_BEERS_PROOF = "Drink Ape Bite Liqueur at Karamja Wines, Spirits, and Beers"
BAR_CRAWL_RISING_SUN_PROOF = "Drink Hand of Death Cocktail at Rising Sun"
BAR_CRAWL_RUSTY_ANCHOR_PROOF = "Drink Black Skull Ale at Rusty Anchor"

# Each rule is (required proofs, emitted proofs). Runtime code calls the rule
# only after the named action succeeds; prerequisites support genuine multi-step work.
QUEST_ACTION_PROOF_RULES = {
    (
        "shop_vendor_action",
        "bar_crawl_blue_moon_inn_uncle_humphreys_gutrot",
    ): ((), (BAR_CRAWL_BLUE_MOON_INN_PROOF,)),
    (
        "shop_vendor_action",
        "bar_crawl_blurberrys_bar_fire_toad_blast",
    ): ((), (BAR_CRAWL_BLURBERRYS_BAR_PROOF,)),
    (
        "shop_vendor_action",
        "bar_crawl_dead_mans_chest_supergrog",
    ): ((), (BAR_CRAWL_DEAD_MANS_CHEST_PROOF,)),
    (
        "shop_vendor_action",
        "bar_crawl_dragon_inn_fire_brandy",
    ): ((), (BAR_CRAWL_DRAGON_INN_PROOF,)),
    (
        "shop_vendor_action",
        "bar_crawl_flying_horse_inn_heart_stopper",
    ): ((), (BAR_CRAWL_FLYING_HORSE_INN_PROOF,)),
    (
        "shop_vendor_action",
        "bar_crawl_foresters_arms_liverbane_ale",
    ): ((), (BAR_CRAWL_FORESTERS_ARMS_PROOF,)),
    (
        "shop_vendor_action",
        "bar_crawl_jolly_boar_inn_olde_suspiciouse",
    ): ((), (BAR_CRAWL_JOLLY_BOAR_INN_PROOF,)),
    (
        "shop_vendor_action",
        "bar_crawl_karamja_wines_spirits_and_beers_ape_bite_liqueur",
    ): ((), (BAR_CRAWL_KARAMJA_WINES_SPIRITS_AND_BEERS_PROOF,)),
    (
        "shop_vendor_action",
        "bar_crawl_rising_sun_hand_of_death_cocktail",
    ): ((), (BAR_CRAWL_RISING_SUN_PROOF,)),
    (
        "shop_vendor_action",
        "bar_crawl_rusty_anchor_black_skull_ale",
    ): ((), (BAR_CRAWL_RUSTY_ANCHOR_PROOF,)),
    (
        "shop_buy",
        "hamabs_crafting_emporium:3:4020",
    ): ((), (DO_NO_EVIL_MAMULET_MOULD_PROOF,)),
    (
        "shop_service",
        "thakkrad_cure_yak_hide",
    ): ((), (THAKKRAD_CURED_YAK_HIDE_PROOF,)),
    (
        "crafting",
        "leather_yakhide_armour_10824",
    ): ((THAKKRAD_CURED_YAK_HIDE_PROOF,), (FREMENNIK_ISLES_YAK_HIDE_PROOF,)),
    (
        "crafting",
        "leather_yakhide_armour",
    ): ((THAKKRAD_CURED_YAK_HIDE_PROOF,), (FREMENNIK_ISLES_YAK_HIDE_PROOF,)),
    (
        "quest_stage",
        f"biohazard:{BIOHAZARD_CAULDRON_ACTION}",
    ): ((), (MOURNER_FOOD_STORES_PROOF,)),
}

# The reachability audit uses the same event bindings, but proves an event only
# when the corresponding action or source is reachable in its fixed-point graph.
QUEST_ACTION_PROOF_AUDIT_SOURCES = {
    ("shop_buy", "hamabs_crafting_emporium:3:4020"): (
        "shop:hamabs_crafting_emporium",
        "M'amulet mould",
    ),
    ("shop_service", "thakkrad_cure_yak_hide"): (
        "Shop service:thakkrad_cure_yak_hide",
        "",
    ),
    ("crafting", "leather_yakhide_armour_10824"): (
        "Crafting:leather_yakhide_armour_10824",
        "",
    ),
    ("crafting", "leather_yakhide_armour"): (
        "Crafting:leather_yakhide_armour",
        "",
    ),
}
