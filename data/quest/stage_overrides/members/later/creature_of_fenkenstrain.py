from __future__ import annotations

from ....contract import QuestStageRequirementCleanup, _stage_req


CREATURE_OF_FENKENSTRAIN_CLEANUPS = (
    QuestStageRequirementCleanup(
        stage=1,
        remove_required_inventory=("Ecto token",),
        remove_required_tools=("Spade",),
        remove_required_inventory_options=("Amulet of ghostspeak", "Cramulet"),
        add_required_inventory_options=((("Ghostspeak amulet", 1), ("Cramulet", 1)),),
        remove_required_actions=("Complete Creature of Fenkenstrain stage 1 objective",),
        add_auto_actions=(
            "To start the quest, read the signpost in the centre of Canifis.",
            "After you've started the quest, go northeast to Fenkenstrain's Castle.",
            "Talk to Dr. Fenkenstrain and a job interview will commence.",
            'When asked to describe yourself in one word, answer "braindead" and that your best skill is gravedigging.',
            "Wear your Amulet of ghostspeak and talk to the headless Gardener Ghost.",
            "Offer to help find his head, which is buried in a grave in the Haunted Woods",
            "take him south into the Haunted Woods.",
        ),
        source="https://runescape.wiki/w/Creature_of_Fenkenstrain?oldid=6535792",
    ),
    QuestStageRequirementCleanup(
        stage=2,
        remove_required_actions=("Complete Creature of Fenkenstrain stage 2 objective",),
        source="https://runescape.wiki/w/Creature_of_Fenkenstrain?oldid=6535792",
    ),
)


_STAGE_TWO_ACTIONS = (
    "Follow the Gardener Ghost's directions closely and you should reach his grave soon enough.",
    "Make sure the grave's name matches the ghost's, dig, and you will get the head.",
    "Go to the bar in Canifis.",
    "Search the bookcase in the west room for The Joy of Gravedigging and you will find a marble amulet.",
    "Search the east room's bookcase for Handy Maggot Avoidance Techniques and you will find the obsidian amulet.",
    "Use them with each other to get a star amulet.",
)

CREATURE_OF_FENKENSTRAIN_STAGE_ADDITIONS = (
    _stage_req(
        2,
        "Dig up the Gardener Ghost's head and combine the castle bookcase amulets.",
        "https://runescape.wiki/w/Creature_of_Fenkenstrain?oldid=6535792; "
        "https://runescape.wiki/w/Pickled_brain?oldid=6174247; "
        "AnkiScape stage boundary: retained Fenkenstrain qualification sources/qualification-report.md:3; "
        "Smallest complete implementation boundary: stage 2 atomic review advances progress 2 to 3 "
        "with empty head, Brain and Star retained",
        required_inventory=(("Spade", 1), ("Pickled brain", 1)),
        produced_inventory=(("Decapitated head", 1), ("Star amulet", 1)),
        auto_actions=_STAGE_TWO_ACTIONS,
    ),
)

# Ordered internal steps; only the head and Star are retained stage outputs.
CREATURE_OF_FENKENSTRAIN_STAGE_TWO_TRANSACTION = (
    {"required_inventory": (("Spade", 1),), "consumed_inventory": (),
     "produced_inventory": (("Decapitated head", 1),)},
    {"required_inventory": (("Pickled brain", 1),), "consumed_inventory": (),
     "produced_inventory": ()},
    {"required_inventory": (), "consumed_inventory": (),
     "produced_inventory": (("Marble amulet", 1),)},
    {"required_inventory": (), "consumed_inventory": (),
     "produced_inventory": (("Obsidian amulet", 1),)},
    {"required_inventory": (), "consumed_inventory": (("Marble amulet", 1), ("Obsidian amulet", 1)),
     "produced_inventory": (("Star amulet", 1),)},
)

CREATURE_OF_FENKENSTRAIN_ITEM_FRAGMENT = {
    name: {
        "item_id": item_id,
        "category": "material",
        "members": True,
        "equipable": False,
        "tradeable": False,
        "stackable": False,
        "source": f"https://runescape.wiki/w/{article}?oldid={oldid}; "
                  "retained build-727/cache-309 identity comparison (2012-07-24)",
    }
    for name, item_id, article, oldid in (
        ("Decapitated head", 4197, "Decapitated_head_(Creature_of_Fenkenstrain)", 6547064),
        ("Pickled brain", 4199, "Pickled_brain", 6174247),
        ("Marble amulet", 4187, "Marble_amulet", 6130186),
        ("Obsidian amulet", 4188, "Obsidian_amulet", 6074919),
        ("Star amulet", 4183, "Star_amulet", 5691056),
    )
}
