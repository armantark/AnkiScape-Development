"""Source-backed Cabin Fever stage corrections."""


DARKAN_AUDIT_ROOT = "/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit"
CABIN_FEVER_TARGET_CONTRACT = f"{DARKAN_AUDIT_ROOT}/evidence/static/cabin-fever-target-contract.json"
CABIN_FEVER_BUILD_727_SOURCE = f"{DARKAN_AUDIT_ROOT}/sources/cabin-fever-build727-oldid-5870979.json"
CABIN_FEVER_FINAL_PREEOC_SOURCE = f"{DARKAN_AUDIT_ROOT}/sources/cabin-fever-final-preeoc-oldid-6533785.json"
CABIN_FEVER_TRANSCRIPT_HISTORY = f"{DARKAN_AUDIT_ROOT}/sources/cabin-fever-transcript-history.json"
CABIN_FEVER_STAGE_SOURCE = "; ".join(
    (
        CABIN_FEVER_TARGET_CONTRACT,
        CABIN_FEVER_BUILD_727_SOURCE,
        CABIN_FEVER_FINAL_PREEOC_SOURCE,
        CABIN_FEVER_TRANSCRIPT_HISTORY,
    )
)

CABIN_FEVER_STAGE_REQUIREMENT_CLEANUPS = (
    {
        "stage": 1,
        "remove_required_inventory_options": ("Ghosts Ahoy",),
        "remove_required_actions": ("Complete Cabin Fever stage 1 objective",),
        "add_auto_actions": ("Reach the Port Phasmatys charter route",),
        "source": CABIN_FEVER_STAGE_SOURCE,
    },
    {
        "stage": 2,
        "remove_required_actions": ("Complete Cabin Fever stage 2 objective",),
        "add_auto_actions": (
            "Swing between the ships, consuming one quest rope per swing, disable the enemy cannon with one fuse and a retained tinderbox, then repair exactly three hull holes with two repair planks, ten tacks, and one swamp paste each",
        ),
        "source": CABIN_FEVER_STAGE_SOURCE,
    },
    {
        "stage": 3,
        "remove_required_actions": ("Complete Cabin Fever stage 3 objective",),
        "add_auto_actions": (
            "Steal exactly ten plunder from the enemy hold and store it once aboard The Adventurous",
        ),
        "source": CABIN_FEVER_STAGE_SOURCE,
    },
    {
        "stage": 4,
        "remove_required_actions": ("Complete Cabin Fever stage 4 objective",),
        "add_auto_actions": (
            "Repair the broken cannon with one barrel, load every shot in gunpowder-ramrod-payload-fuse order, then score one canister hit and three cannonball hits with the retained tinderbox, cleaning between shots",
        ),
        "source": CABIN_FEVER_STAGE_SOURCE,
    },
)

CABIN_FEVER_UNLOCKS = (
    "Mos Le'Harmless travel",
    "Fever spider Slayer assignments",
    "Cave horror Slayer assignments",
    "Jungle horror Slayer assignments",
)
