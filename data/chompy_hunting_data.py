"""Source-backed Chompy hunting acquisition data."""

from __future__ import annotations

from typing import Any


CHOMPY_HUNTING_ACTIVITY_ID = "hunt_chompy_birds"
BIG_CHOMPY_BIRD_HUNTING_WIKI_SOURCE = "https://runescape.wiki/w/Big_Chompy_Bird_Hunting?oldid=6408629"
RAW_CHOMPY_WIKI_SOURCE = "https://runescape.wiki/w/Raw_chompy?oldid=6286360"
DARKAN_REV = "a2568b880390ef697b1b17e825fdef7868bed67f"
DARKAN_ROOT = "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server"
BIG_CHOMPY_BIRD_HUNTING_STAGE_ACTION_SOURCE = (
    f"{BIG_CHOMPY_BIRD_HUNTING_WIKI_SOURCE}; {DARKAN_ROOT}/src/main/java/"
    "com/rs/game/content/miniquests/recipe_for_disaster/freeing_skrach_uglogwee/"
    f"FreeingSkrachUglogwee.kt @ {DARKAN_REV}"
)
CHOMPY_HUNTING_SOURCE = (
    f"{BIG_CHOMPY_BIRD_HUNTING_STAGE_ACTION_SOURCE}; {RAW_CHOMPY_WIKI_SOURCE}; "
    f"{DARKAN_ROOT}/data/npcs/drops/chompy_bird.json; "
    f"{DARKAN_ROOT}/data/npcs/combatdefs/uncategorized/chompy_bird (noanims).json; "
    f"{DARKAN_ROOT}/src/main/java/com/rs/game/content/skills/fletching/Fletching.java "
    f"@ {DARKAN_REV}"
)

BIG_CHOMPY_STAGE_REQUIREMENT_CLEANUPS: tuple[dict[str, Any], ...] = (
    {
        "stage": 1,
        "remove_required_actions": (
            "Complete Big Chompy Bird Hunting stage 1 objective",
        ),
        "add_auto_actions": (
            "Fletch ogre arrows from achey logs, feathers, and wolfbone arrowtips, then give six arrows to Rantz",
        ),
        "source": BIG_CHOMPY_BIRD_HUNTING_STAGE_ACTION_SOURCE,
    },
    {
        "stage": 2,
        "remove_required_actions": (
            "Complete Big Chompy Bird Hunting stage 2 objective",
        ),
        "add_auto_actions": (
            "Retrieve the ogre bellows, fill them with swamp gas, inflate swamp toads, and place the bait for Rantz",
        ),
        "source": BIG_CHOMPY_BIRD_HUNTING_STAGE_ACTION_SOURCE,
    },
    {
        "stage": 3,
        "remove_required_actions": (
            "Complete Big Chompy Bird Hunting stage 3 objective",
        ),
        "add_auto_actions": (
            "Lure and kill a Chompy bird with an ogre bow and ogre arrows, pluck it, take the raw chompy to Rantz, gather the three seasonings from Rantz, Fycie and Bugs, then spit-roast the seasoned chompy for him",
        ),
        "source": BIG_CHOMPY_BIRD_HUNTING_STAGE_ACTION_SOURCE,
    },
)


def chompy_hunting_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        CHOMPY_HUNTING_ACTIVITY_ID: {
            "display_name": "Hunt Chompy birds",
            "requirements": {"Ogre arrow": 1},
            "required_item_options": (("Ogre bow",),),
            "output_item": "Raw chompy",
            "output_qty": 1,
            "batch_size": 1,
            "group": "gathering",
            "source": CHOMPY_HUNTING_SOURCE,
            "source_status": "pinned/Darkan+period-wiki",
        }
    }
