"""Source-backed Zogre Flesh Eaters stage corrections."""

from dataclasses import replace


QUEST_ID = "zogre_flesh_eaters"
DARKAN_AUDIT_ROOT = "/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit"
ZOGRE_FLESH_EATERS_TARGET_CONTRACT = f"{DARKAN_AUDIT_ROOT}/evidence/static/zogre-flesh-eaters-target-contract.json"
ZOGRE_FLESH_EATERS_FINAL_PREEOC_SOURCE = f"{DARKAN_AUDIT_ROOT}/sources/zogre-flesh-eaters-final-preeoc-oldid-6441901.json"
ZOGRE_FLESH_EATERS_BUILD_727_SOURCE = f"{DARKAN_AUDIT_ROOT}/sources/zogre-flesh-eaters-build727-oldid-5981068.json"
ZOGRE_FLESH_EATERS_STAGE_SOURCE = (
    f"{ZOGRE_FLESH_EATERS_TARGET_CONTRACT}; "
    f"{ZOGRE_FLESH_EATERS_FINAL_PREEOC_SOURCE}; "
    f"{ZOGRE_FLESH_EATERS_BUILD_727_SOURCE}"
)

ZOGRE_FLESH_EATERS_STAGE_REQUIREMENT_CLEANUPS = (
    {
        "stage": 1,
        "remove_required_inventory": ("Achey tree logs",),
        "remove_required_actions": ("Complete Zogre Flesh Eaters stage 1 objective",),
        "add_auto_actions": (
            "Speak to the ogre guard, open Jiggig's barricade, and enter the tomb",
        ),
        "source": ZOGRE_FLESH_EATERS_STAGE_SOURCE,
    },
    {
        "stage": 2,
        "remove_required_actions": ("Complete Zogre Flesh Eaters stage 2 objective",),
        "add_auto_actions": (
            "Defeat the crypt zombie, recover the tomb evidence, show it in Yanille, and search Sithik's room",
        ),
        "source": ZOGRE_FLESH_EATERS_STAGE_SOURCE,
    },
    {
        "stage": 3,
        "remove_required_actions": ("Complete Zogre Flesh Eaters stage 3 objective",),
        "add_auto_actions": (
            "Draw and sign an accurate portrait of Sithik, then present the complete evidence to Zavistic Rarve for the strange potion",
        ),
        "source": ZOGRE_FLESH_EATERS_STAGE_SOURCE,
    },
    {
        "stage": 4,
        "remove_required_inventory": ("Vial of water", "Rogue's purse", "Snake weed"),
        "remove_required_actions": ("Complete Zogre Flesh Eaters stage 4 objective",),
        "add_auto_actions": (
            "Drug Sithik's tea, leave and return after his transformation, then interrogate him about the disease and brutal arrows",
        ),
        "source": ZOGRE_FLESH_EATERS_STAGE_SOURCE,
    },
    {
        "stage": 5,
        "remove_required_inventory": ("Wolf Bones", "Bowstring"),
        "remove_required_actions": ("Complete Zogre Flesh Eaters stage 5 objective",),
        "add_auto_actions": (
            "Report Sithik's confession to Grish, receive the ogre gate key and bow knowledge, and return to the tomb",
        ),
        "source": ZOGRE_FLESH_EATERS_STAGE_SOURCE,
    },
    {
        "stage": 6,
        "remove_required_actions": ("Complete Zogre Flesh Eaters stage 6 objective",),
        "add_auto_actions": (
            "Open the stone doors, defeat Slash Bash, recover the ogre artefact, and return it to Grish",
        ),
        "source": ZOGRE_FLESH_EATERS_STAGE_SOURCE,
    },
)

ZOGRE_FLESH_EATERS_COMBAT_ENCOUNTER_STAGES = {
    "zogre_flesh_eaters_zombie_39": 2,
    "zogre_flesh_eaters_slash_bash_111": 6,
}
ZOGRE_FLESH_EATERS_COMBAT_GUARANTEED_DROPS = {
    "zogre_flesh_eaters_zombie_39": (("Ruined backpack", 1),),
    "zogre_flesh_eaters_slash_bash_111": (
        ("Zogre bones", 2),
        ("Ourg bones", 3),
        ("Ogre artefact", 1),
    ),
}
ZOGRE_FLESH_EATERS_ITEM_REWARDS = (("Black prism", 1),)
ZOGRE_FLESH_EATERS_XP_REWARDS = (
    ("fletching", 2000),
    ("herblore", 2000),
    ("ranged", 2000),
)


def relocate_combat_encounters(quest_id, requirements):
    if quest_id != QUEST_ID:
        return requirements
    moved_ids = frozenset(ZOGRE_FLESH_EATERS_COMBAT_ENCOUNTER_STAGES)
    encounters = {
        encounter.encounter_id: encounter
        for requirement in requirements
        for encounter in requirement.combat_encounters
        if encounter.encounter_id in moved_ids
    }
    if encounters.keys() != moved_ids:
        raise ValueError("Zogre Flesh Eaters combat encounter catalog changed")
    encounters = {
        encounter_id: replace(
            encounter,
            guaranteed_drops=ZOGRE_FLESH_EATERS_COMBAT_GUARANTEED_DROPS[encounter_id],
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
                for encounter_id, stage in ZOGRE_FLESH_EATERS_COMBAT_ENCOUNTER_STAGES.items()
                if stage == requirement.stage
            ),
        )
        for requirement in requirements
    )
