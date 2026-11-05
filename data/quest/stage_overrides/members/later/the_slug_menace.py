"""Authored opening wording; period bindings live in the_slug_menace_sources.json."""

from ....contract import QuestStage, QuestStageRequirementCleanup

QUEST_ID = 'the_slug_menace'
OPENING_ACTIONS = (
    "Receive Tiffy's Witchaven mission, password and Commorb v2",
    "Finish O'Niall's referral to Mayor Hobb, Brother Maledict and Holgart",
    "Talk to Mayor Hobb about the Saradomin shrine and receive Savant's scan request",
    "Scan Mayor Hobb with Commorb v2",
)
OPENING_JOURNAL = (
    "Talk to Sir Tiffy Cashien in Falador Park about a job. He sends you to investigate Witchaven and report to Col. Jake O'Niall.",
    'Tiffy upgrades your Commorb to Commorb v2, or supplies Commorb v2 if you do not have a Commorb. The password is: "In Falador, the geese fly backwards on Tuesday."',
    "In Witchaven, finish O'Niall's referral to Mayor Hobb, Brother Maledict and Holgart.",
    "Talk to Mayor Hobb about the shrine to Saradomin. Savant asks you to scan him.",
    "Use Commorb v2 to scan Mayor Hobb. Savant detects two life forms but is unsure what it means.",
)
LEGACY_OPENING_JOURNAL = (
    "This opening covers Tiffy's Witchaven mission, O'Niall's referral and Mayor Hobb's Commorb v2 scan.",
)
_SOURCE = (
    'W1 https://runescape.wiki/w/index.php?title=The_Slug_Menace&oldid=6588246 L52-72; '
    'T1 capture 20121119222000 L127-139; S1 capture 20121018051313 L87-115; '
    'data/quest/the_slug_menace_sources.json'
)
SLUG_MENACE_OPENING_ITEMS = {
    'Commorb': dict(category='material', item_id=6635, stackable=False, tradeable=False,
                    source=_SOURCE + '; C1 oldid=5775688 L20,26; B2 items.commorb.id=6635 (Wanted! only)'),
    'Commorb v2': dict(category='material', item_id=9681, stackable=False, tradeable=False,
                       source=_SOURCE + '; C2 oldid=5783735 L2,20; B1 item 9681'),
}
THE_SLUG_MENACE_CLEANUPS = (
    QuestStageRequirementCleanup(
        stage=1,
        remove_required_inventory=('Swamp paste', 'Earth talisman', 'Water talisman', 'Fire talisman',
                                   'Air talisman', 'Mind talisman', 'Elemental talisman',
                                   'Omni-talisman', 'Abyss', 'Great Orb Project'),
        remove_required_tools=('Chisel',),
        remove_required_inventory_options=('Rune essence', 'Pure essence'),
        remove_required_actions=('Complete The Slug Menace stage 1 objective',),
        add_auto_actions=OPENING_ACTIONS,
        add_produced_inventory=(('Commorb v2', 1),), source=_SOURCE,
    ),
    QuestStageRequirementCleanup(stage=5, add_required_inventory=(('Swamp paste', 1),), source=_SOURCE),
    QuestStageRequirementCleanup(
        stage=6, add_required_tools=(('Chisel', 1),),
        add_required_inventory_options=(
            (('Rune essence', 5), ('Pure essence', 5)),
            (('Earth talisman', 1), ('Elemental talisman', 1), ('Omni-talisman', 1)),
            (('Water talisman', 1), ('Elemental talisman', 1), ('Omni-talisman', 1)),
            (('Fire talisman', 1), ('Elemental talisman', 1), ('Omni-talisman', 1)),
            (('Air talisman', 1), ('Elemental talisman', 1), ('Omni-talisman', 1)),
            (('Mind talisman', 1), ('Omni-talisman', 1)),
        ), source=_SOURCE,
    ),
)


def slug_menace_opening_journal_stages(quest_id, stages):
    if quest_id != QUEST_ID:
        return stages
    return tuple(QuestStage(1, OPENING_JOURNAL) if stage.stage == 1 else stage for stage in stages)
