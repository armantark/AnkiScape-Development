"""Bindings from genuine player actions to durable quest proofs."""

DO_NO_EVIL_MAMULET_MOULD_PROOF = (
    "Recover an m'amulet mould before making the monkeyspeak amulet"
)
FREMENNIK_ISLES_YAK_HIDE_PROOF = "Cure and stitch yak-hide armour"
FREMENNIK_ISLES_ROUND_SHIELD_PROOF = "Make a Fremennik round shield"
MOURNER_FOOD_STORES_PROOF = "Use the rotten apple to sabotage the mourner food stores"
BIOHAZARD_CAULDRON_ACTION = "Put the rotten apple in the Mourner HQ cauldron"
THAKKRAD_CURED_YAK_HIDE_PROOF = "Cure yak-hide with Thakkrad"

# Each rule is (required proofs, emitted proofs). Runtime code calls the rule
# only after the named action succeeds; prerequisites support genuine multi-step work.
QUEST_ACTION_PROOF_RULES = {
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
        "crafting",
        "craft_fremennik_round_shield",
    ): ((), (FREMENNIK_ISLES_ROUND_SHIELD_PROOF,)),
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
    ("crafting", "craft_fremennik_round_shield"): (
        "Crafting:craft_fremennik_round_shield",
        "",
    ),
}
