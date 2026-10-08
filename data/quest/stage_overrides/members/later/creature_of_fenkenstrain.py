from __future__ import annotations

from ....contract import QuestStageRequirementCleanup


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
)
