"""Source-backed Rum Deal stage corrections."""

from dataclasses import replace


QUEST_ID = "rum_deal"
DARKAN_AUDIT_ROOT = "/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit"
RUM_DEAL_TARGET_CONTRACT = f"{DARKAN_AUDIT_ROOT}/evidence/static/rum-deal-target-contract.json"
RUM_DEAL_FINAL_PREEOC_SOURCE = f"{DARKAN_AUDIT_ROOT}/sources/rum-deal-final-preeoc-oldid-6556008.json"
RUM_DEAL_BLINDWEED_SOURCE = f"{DARKAN_AUDIT_ROOT}/sources/rum-deal-blindweed-final-preeoc-oldid-4361673.json"
RUM_DEAL_FEVER_SPIDER_SOURCE = f"{DARKAN_AUDIT_ROOT}/sources/rum-deal-fever-spider-final-preeoc-oldid-6469080.json"
RUM_DEAL_FISHBOWL_NET_SOURCE = f"{DARKAN_AUDIT_ROOT}/sources/rum-deal-fishbowl-net-final-preeoc-oldid-6358392.json"
RUM_DEAL_HOLY_WRENCH_SOURCE = f"{DARKAN_AUDIT_ROOT}/sources/rum-deal-holy-wrench-final-preeoc-oldid-6518059.json"
RUM_DEAL_TRANSCRIPT_HISTORY = f"{DARKAN_AUDIT_ROOT}/sources/rum-deal-transcript-history.json"
RUM_DEAL_STAGE_SOURCE = "; ".join(
    (
        RUM_DEAL_TARGET_CONTRACT,
        RUM_DEAL_FINAL_PREEOC_SOURCE,
        RUM_DEAL_BLINDWEED_SOURCE,
        RUM_DEAL_FEVER_SPIDER_SOURCE,
        RUM_DEAL_FISHBOWL_NET_SOURCE,
        RUM_DEAL_HOLY_WRENCH_SOURCE,
        RUM_DEAL_TRANSCRIPT_HISTORY,
    )
)

RUM_DEAL_STAGE_REQUIREMENT_CLEANUPS = (
    {
        "stage": 1,
        "remove_required_inventory": (
            "Slayer gloves",
            "Armour",
            "Food",
            "Seed dibber",
            "Rake",
            "Ectophial",
            "Relicym's balm",
            "Ring of charos",
        ),
        "remove_required_actions": ("Complete Rum Deal stage 1 objective",),
        "add_auto_actions": (
            "Accept Pirate Pete's offer, reach Braindeath Island, receive the Blindweed seed, and rake and plant the surviving patch",
        ),
        "source": RUM_DEAL_STAGE_SOURCE,
    },
    {
        "stage": 2,
        "remove_required_inventory": ("Bucket",),
        "remove_required_actions": ("Complete Rum Deal stage 2 objective",),
        "add_auto_actions": (
            "Wait 4 minutes 35 seconds, harvest the Blindweed, add it to the hopper, then collect and add stagnant water",
        ),
        "source": RUM_DEAL_STAGE_SOURCE,
    },
    {
        "stage": 3,
        "remove_required_actions": ("Complete Rum Deal stage 3 objective",),
        "add_auto_actions": (
            "Catch and pressurise five sea creatures, bless the wrench with at least 470 current Prayer points without draining them, then defeat the Evil spirit",
        ),
        "source": RUM_DEAL_STAGE_SOURCE,
    },
    {
        "stage": 4,
        "remove_required_actions": ("Complete Rum Deal stage 4 objective",),
        "add_required_tools": (("Slayer gloves", 1),),
        "add_auto_actions": (
            "Defeat a Fever spider while wearing Slayer gloves, add its body to the hopper, give the swill to Captain Donnie, and report to Captain Braindeath",
        ),
        "source": RUM_DEAL_STAGE_SOURCE,
    },
)

RUM_DEAL_COMBAT_ENCOUNTER_STAGES = {
    "rum_deal_evil_spirit_150": 3,
    "rum_deal_fever_spider_49": 4,
}
RUM_DEAL_COMBAT_GUARANTEED_DROPS = {
    "rum_deal_evil_spirit_150": (),
    "rum_deal_fever_spider_49": (("Fever spider body", 1),),
}


def relocate_combat_encounters(quest_id, requirements):
    if quest_id != QUEST_ID:
        return requirements
    moved_ids = frozenset(RUM_DEAL_COMBAT_ENCOUNTER_STAGES)
    encounters = {
        encounter.encounter_id: encounter
        for requirement in requirements
        for encounter in requirement.combat_encounters
        if encounter.encounter_id in moved_ids
    }
    if encounters.keys() != moved_ids:
        raise ValueError("Rum Deal combat encounter catalog changed")
    encounters = {
        encounter_id: replace(
            encounter,
            guaranteed_drops=RUM_DEAL_COMBAT_GUARANTEED_DROPS[encounter_id],
        )
        for encounter_id, encounter in encounters.items()
    }
    return tuple(
        replace(
            requirement,
            combat_encounters=tuple(
                encounter
                for encounter in requirement.combat_encounters
                if encounter.encounter_id not in moved_ids
            )
            + tuple(
                encounters[encounter_id]
                for encounter_id, stage in RUM_DEAL_COMBAT_ENCOUNTER_STAGES.items()
                if stage == requirement.stage
            ),
        )
        for requirement in requirements
    )
