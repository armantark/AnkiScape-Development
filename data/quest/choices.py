from __future__ import annotations

from .dependencies import *
from .contract import *
from .ids import *
from .sources import *

SHIELD_ROUTE_PHOENIX = "Join the Phoenix Gang"
SHIELD_ROUTE_BLACK_ARM = "Join the Black Arm Gang"
SHIELD_VARIANT_PHOENIX = "phoenix"
SHIELD_VARIANT_BLACK_ARM = "black_arm"
HEROES_ROUTE_PHOENIX = SHIELD_ROUTE_PHOENIX
HEROES_ROUTE_BLACK_ARM = SHIELD_ROUTE_BLACK_ARM
HEROES_VARIANT_PHOENIX = SHIELD_VARIANT_PHOENIX
HEROES_VARIANT_BLACK_ARM = SHIELD_VARIANT_BLACK_ARM
TEMPLE_OF_IKOV_ROUTE_GUARDIANS = "Side with the Guardians of Armadyl"
TEMPLE_OF_IKOV_ROUTE_LUCIEN = "Side with Lucien"
TEMPLE_OF_IKOV_VARIANT_GUARDIANS = "guardians"
TEMPLE_OF_IKOV_VARIANT_LUCIEN = "lucien"
HAZEEL_CULT_ROUTE_CARNILLEAN = "Side with Ceril Carnillean"
HAZEEL_CULT_ROUTE_HAZEEL = "Side with Hazeel's cult"
HAZEEL_CULT_VARIANT_CARNILLEAN = "carnillean"
HAZEEL_CULT_VARIANT_HAZEEL = "hazeel"
VOID_STARES_BACK_ROUTE_KORASI = "Sacrifice Korasi"
VOID_STARES_BACK_ROUTE_JESSIKA = "Sacrifice Jessika"
TEMPLE_OF_IKOV_BOW_OPTIONS: Tuple[Tuple[str, int], ...] = (
    ("Yew shortbow", 1),
    ("Yew longbow", 1),
    ("Yew comp bow", 1),
    ("Magic shortbow", 1),
    ("Magic longbow", 1),
    ("Magic comp bow", 1),
    ("Dark bow", 1),
)

SHIELD_OF_ARRAV_CHOICES: Tuple[QuestChoice, ...] = (
    QuestChoice(
        stage=4,
        prompt="Choose a gang.",
        options=(
            QuestChoiceOption("Phoenix Gang", SHIELD_ROUTE_PHOENIX, "Jonny the beard and the Phoenix shield half."),
            QuestChoiceOption("Black Arm Gang", SHIELD_ROUTE_BLACK_ARM, "Phoenix crossbows and the Black Arm shield half."),
        ),
        source=f"{DARKAN_SHIELD_OF_ARRAV_STRAVEN_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_KATRINE_SOURCE}; {SHIELD_OF_ARRAV_WIKI_SOURCE}",
    ),
)

HEROES_QUEST_CHOICES: Tuple[QuestChoice, ...] = (
    QuestChoice(
        stage=9,
        prompt="Choose the gang contact to use for Scarface Pete's mansion.",
        options=(
            QuestChoiceOption(
                "Phoenix Gang",
                HEROES_ROUTE_PHOENIX,
                "Use the secret panel and a Black Arm Gang partner's miscellaneous key to confront Grip.",
            ),
            QuestChoiceOption("Black Arm Gang", HEROES_ROUTE_BLACK_ARM, "Use Trobert's deputy guard route."),
        ),
        source=f"{HEROES_QUEST_KATRINE_SOURCE}; {HEROES_QUEST_STRAVEN_SOURCE}; {HEROES_QUEST_WIKI_SOURCE}",
    ),
)

TEMPLE_OF_IKOV_CHOICES: Tuple[QuestChoice, ...] = (
    QuestChoice(
        stage=9,
        prompt="Choose who to aid.",
        options=(
            QuestChoiceOption("Guardians of Armadyl", TEMPLE_OF_IKOV_ROUTE_GUARDIANS, "Receive an Armadyl pendant and confront Lucien."),
            QuestChoiceOption("Lucien", TEMPLE_OF_IKOV_ROUTE_LUCIEN, "Take the Staff of Armadyl for Lucien."),
        ),
        source=f"{TEMPLE_OF_IKOV_GUARDIAN_SOURCE}; {TEMPLE_OF_IKOV_LUCIEN_VARROCK_SOURCE}; {TEMPLE_OF_IKOV_WIKI_SOURCE}",
    ),
)

HAZEEL_CULT_CHOICES: Tuple[QuestChoice, ...] = (
    QuestChoice(
        stage=1,
        prompt="Choose who to help.",
        options=(
            QuestChoiceOption("Ceril Carnillean", HAZEEL_CULT_ROUTE_CARNILLEAN, "Stop the cult and expose Butler Jones."),
            QuestChoiceOption("Hazeel's cult", HAZEEL_CULT_ROUTE_HAZEEL, "Help revive Hazeel."),
        ),
        source="https://runescape.wiki/w/Hazeel_Cult?oldid=6579784",
    ),
)

VOID_STARES_BACK_CHOICES: Tuple[QuestChoice, ...] = (
    QuestChoice(
        stage=5,
        prompt="Choose who makes the sacrifice.",
        options=(
            QuestChoiceOption("Korasi", VOID_STARES_BACK_ROUTE_KORASI, "Korasi sacrifices herself before the Pest Queen fight."),
            QuestChoiceOption("Jessika", VOID_STARES_BACK_ROUTE_JESSIKA, "Jessika sacrifices herself before the Pest Queen fight."),
        ),
        source="https://runescape.wiki/w/The_Void_Stares_Back%2FQuick_guide?oldid=6549181",
    ),
)

QUEST_CHOICE_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestChoice, ...]] = {
    HAZEEL_CULT_ID: HAZEEL_CULT_CHOICES,
    THE_VOID_STARES_BACK_ID: VOID_STARES_BACK_CHOICES,
}

__all__ = (
    'SHIELD_ROUTE_PHOENIX', 'SHIELD_ROUTE_BLACK_ARM', 'SHIELD_VARIANT_PHOENIX', 'SHIELD_VARIANT_BLACK_ARM', 'HEROES_ROUTE_PHOENIX', 'HEROES_ROUTE_BLACK_ARM', 'HEROES_VARIANT_PHOENIX', 'HEROES_VARIANT_BLACK_ARM',
    'TEMPLE_OF_IKOV_ROUTE_GUARDIANS', 'TEMPLE_OF_IKOV_ROUTE_LUCIEN', 'TEMPLE_OF_IKOV_VARIANT_GUARDIANS', 'TEMPLE_OF_IKOV_VARIANT_LUCIEN', 'HAZEEL_CULT_ROUTE_CARNILLEAN', 'HAZEEL_CULT_ROUTE_HAZEEL',
    'HAZEEL_CULT_VARIANT_CARNILLEAN', 'HAZEEL_CULT_VARIANT_HAZEEL', 'VOID_STARES_BACK_ROUTE_KORASI', 'VOID_STARES_BACK_ROUTE_JESSIKA', 'TEMPLE_OF_IKOV_BOW_OPTIONS', 'SHIELD_OF_ARRAV_CHOICES', 'HEROES_QUEST_CHOICES',
    'TEMPLE_OF_IKOV_CHOICES', 'HAZEEL_CULT_CHOICES', 'VOID_STARES_BACK_CHOICES', 'QUEST_CHOICE_REPLACEMENTS_BY_ID',
)
