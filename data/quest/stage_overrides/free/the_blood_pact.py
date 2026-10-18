from __future__ import annotations

from ...contract import QuestStage, QuestStageRequirementCleanup


THE_BLOOD_PACT_OPENING_ACTIONS = (
    "Agree to help Xenia rescue Ilona from the Zamorakian cultists in the Lumbridge graveyard.",
    "Enter the Lumbridge Catacombs with Xenia.",
    "Watch Reese, Caitlin and Kayle take Ilona deeper into the dungeon; Reese invokes the blood pact and orders Kayle to guard the door.",
    "Proceed north into the front chamber, where Kayle stands opposite you.",
    "Kayle injures Xenia with his sling.",
    "Xenia asks you to fight on alone and defeat the cultists.",
)

THE_BLOOD_PACT_CLEANUPS = (
    QuestStageRequirementCleanup(
        stage=1,
        remove_required_actions=("Complete The Blood Pact stage 1 objective",),
        add_auto_actions=THE_BLOOD_PACT_OPENING_ACTIONS,
        source="https://runescape.wiki/w/The_Blood_Pact?oldid=6538296",
    ),
)

# The same period guide used by the journals places each cultist beyond the
# previous fight: https://runescape.wiki/w/The_Blood_Pact?oldid=6538296
THE_BLOOD_PACT_COMBAT_PREREQUISITES = {
    "the_blood_pact_caitlin_3": ("the_blood_pact_kayle_3",),
    "the_blood_pact_reese_3": ("the_blood_pact_caitlin_3",),
}

THE_BLOOD_PACT_STAGES = (
    QuestStage(1, THE_BLOOD_PACT_OPENING_ACTIONS),
    QuestStage(2, (
        "Defeat Kayle.",
        "Proceed West.",
        "Defeat Caitlin.",
        "Go south and operate the winch.",
        "Talk to Caitlin.",
    )),
    QuestStage(3, (
        "Go down one of the staircases to the West.",
        "Go South and open the tomb door.",
        "Defeat Reese.",
        "Untie Ilona.",
        "A cutscene will occur.",
        "Quest complete!",
    )),
)
