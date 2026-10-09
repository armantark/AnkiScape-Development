from __future__ import annotations

from ....contract import QuestStageRequirementCleanup, _stage_req


UNDERGROUND_PASS_STAGE_ADDITIONS = (
    _stage_req(
        1,
        "Generated from source-backed quest stage checkpoints.",
        "https://runescape.wiki/w/Underground_Pass?oldid=6582023",
        required_inventory_options=(
            (
                ("Shortbow", 1),
                ("Longbow", 1),
                ("Oak shortbow", 1),
                ("Oak longbow", 1),
                ("Willow shortbow", 1),
                ("Willow longbow", 1),
                ("Maple shortbow", 1),
                ("Maple longbow", 1),
                ("Yew shortbow", 1),
                ("Yew longbow", 1),
                ("Magic shortbow", 1),
                ("Magic longbow", 1),
                ("Yew comp bow", 1),
                ("Magic comp bow", 1),
                ("Dark bow", 1),
            ),
        ),
        consumed_inventory_options=(
            (
                ("Bronze arrows", 1),
                ("Iron arrows", 1),
                ("Steel arrows", 1),
                ("Mithril arrows", 1),
                ("Adamant arrows", 1),
                ("Rune arrows", 1),
                ("Dragon arrows", 1),
            ),
        ),
        auto_actions=(
            "To begin, talk to King Lathas on the first floor of the Ardougne Castle.",
            "Ask King Lathas if his scouts have found a way through the mountains.",
            "As the ruse about the plague is now known to you, West Ardougne can be accessed through the front gates, so head through and walk all the way west through the city until you find the cave entrance with Koftik standing outside.",
            "Talk to him and he'll explain more about the pass and tell you to meet him inside, next to the bridge.",
            "Walk inside (1), and you'll see three paths branching off in different directions.",
            "Climb over the rocks to go around the swamp and get to where Koftik is standing next to a fire (2).",
            "Talk to him and he'll tell you it looks like there have been others in the cave already.",
            'Use the damp cloth on an arrow, then right-click and "light arrow" - or use the arrow on the fire nearby - to get a fire arrow, or a lit arrow if you used its bronze counterpart.',
            "Equip the bow and arrow.",
            "Move into the small room (3) to your north.",
            "Click on it and you'll fire your lit arrow at the rope.",
            "If you succeed, the draw-bridge will drop and you'll automatically walk across the bridge.",
        ),
    ),
)


UNDERGROUND_PASS_CLEANUPS = (
    QuestStageRequirementCleanup(
        stage=1,
        remove_required_actions=("Complete Underground Pass stage 1 objective",),
    ),
)
