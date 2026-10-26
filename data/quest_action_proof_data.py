"""Bindings from genuine player actions to durable quest proofs."""

from .quest.enakhra_opening import PROOFS as ENAKHRA_PROOFS, EVENT_PREFIX
from .quest.elemental_workshop_iii import ACQUIRE_EVENT, ACQUIRE_PROOF, READ_EVENT, READ_PROOF

ORONWEN_REPAIR_PROOF = "Have Oronwen repair the mourner trousers"

DO_NO_EVIL_MAMULET_MOULD_PROOF = (
    "Recover an m'amulet mould before making the monkeyspeak amulet"
)
FREMENNIK_ISLES_YAK_HIDE_PROOF = "Cure and stitch yak-hide armour"
FREMENNIK_ISLES_ROUND_SHIELD_PROOF = "Make a Fremennik round shield"
MOURNER_FOOD_STORES_PROOF = "Use the rotten apple to sabotage the mourner food stores"
BIOHAZARD_CAULDRON_ACTION = "Put the rotten apple in the Mourner HQ cauldron"
THAKKRAD_CURED_YAK_HIDE_PROOF = "Cure yak-hide with Thakkrad"
SPIRITS_OF_THE_ELID_TELEGRAB_PROOF = "Cast Telegrab for the water channel puzzle"

# Each rule is (required proofs, emitted proofs). Runtime code calls the rule
# only after the named action succeeds; prerequisites support genuine multi-step work.
QUEST_ACTION_PROOF_RULES = {
    ACQUIRE_EVENT: ((), (ACQUIRE_PROOF,)),
    READ_EVENT: ((), (READ_PROOF,)),
    ("quest_service", "oronwen_repair"): ((), (ORONWEN_REPAIR_PROOF,)),
    ("magic", "crumble_undead_first_boneguard"): (
        (), ("Cast Crumble Undead during the boneguard fight",),
    ),
    (
        "magic",
        "telegrab_ancestral_key",
    ): ((), (SPIRITS_OF_THE_ELID_TELEGRAB_PROOF,)),
    (
        "utility",
        "collect_evergreen_sap",
    ): ((), ("Collect a bucket of sap from an evergreen tree",)),
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

# Repeated partial deliveries/splits may leave the boolean proof list unchanged.
for _action, _prerequisite in (
    ("offer_help", None), ("deliver_sandstone", "offer_help"), ("receive_32kg", "offer_help"),
    ("chisel_base", "receive_32kg"), ("talk_after_base", "chisel_base"), ("place_base", "talk_after_base"),
    ("split_10kg", "offer_help"), ("split_5kg", "offer_help"), ("split_2kg", "offer_help"),
):
    QUEST_ACTION_PROOF_RULES[("quest_service", EVENT_PREFIX + _action)] = (
        (ENAKHRA_PROOFS[_prerequisite],) if _prerequisite else (),
        (ENAKHRA_PROOFS["deliver_sandstone"], ENAKHRA_PROOFS[_action]) if _action == "receive_32kg" else (ENAKHRA_PROOFS[_action],),
    )
QUEST_ACTION_PROOF_RULES.update({
    ("mining", "sandstone"): ((), ("Mine sandstone",)),
    ("mining", "coal"): ((), ("Mine coal",)),
})

# The reachability audit uses the same event bindings, but proves an event only
# when the corresponding action or source is reachable in its fixed-point graph.
QUEST_ACTION_PROOF_AUDIT_SOURCES = {
    ("magic", "telegrab_ancestral_key"): (
        "Magic:telegrab_ancestral_key",
        "",
    ),
    ("utility", "collect_evergreen_sap"): ("Utility:collect_evergreen_sap", ""),
    ("magic", "crumble_undead_first_boneguard"): (
        "Magic:crumble_undead_first_boneguard", "",
    ),
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
