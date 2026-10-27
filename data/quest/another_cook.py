"""Opening-only Another Cook overlay; later generated fields remain unverified."""

from dataclasses import replace

from .contract import QuestStage, QuestStageRequirement, QuestSkillRequirement

QUEST_ID = 'recipe_for_disaster_another_cooks_quest'
OPENING_STAGE = 1
ADVANCE = 100
COOKING_REQUIREMENT = 10
REQUESTED_INGREDIENTS = (('Eye of newt', 221, 1), ("Greenman's ale", 1909, 1),
                         ('Rotten tomato', 2518, 1), ('Dirty blast', 7497, 1))
STORAGE_IDENTITIES = {'Ashes': 592, 'Fruit blast': 2084, 'Fruit blast (9514)': 9514,
                      "Premade fr' blast": 2034, 'Dirty blast': 7497}
ELIGIBLE_COCKTAILS = ('Fruit blast', 'Fruit blast (9514)')
# PLACEHOLDER(quests.another_cook.dirty_blast_xp): independent pre-cutoff numeric Cooking XP evidence resolving Dirty blast oldid6084510 versus the Darkan omission
DIRTY_BLAST_BASE_XP = 5.0

_PACKET = '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1390-another-cook-dirty-blast-opening/'
SOURCE_INDEX = _PACKET + 'source-index.json'
OPENING_URL = 'https://runescape.wiki/w/index.php?title=Recipe_for_Disaster&oldid=6538752'
OPENING_SOURCE = OPENING_URL + ' lines 70–84, 93–102 (2012-11-06T06:20:48Z)'
DIRTY_BLAST_SOURCE = 'https://runescape.wiki/w/index.php?title=Dirty_blast&oldid=6084510'
CACHE_SOURCE = 'OpenRS2 cache 727 (2012-07-24) and 742 (2012-11-07); ' + SOURCE_INDEX
PERIOD_SOURCES = (
    dict(url=OPENING_URL, timestamp='2012-11-06T06:20:48Z', passages='70–84, 93–102: commission, advance, eligible cocktails and preparation before hand-in',
         body_path=_PACKET + 'sources/recipe-for-disaster-6538752.txt',
         sha256='c583ca6b47a69d622bf73851315e67c02468bc2f2939e90085696defe219d1e5',
         api_sha256='a16a0272328a38cf18659406f4d7be4bca83f51dd8c6398e7d8fffe0b1da8a28'),
    dict(url=DIRTY_BLAST_SOURCE, timestamp='2012-08-13T06:52:56Z', passages='20: 5 Cooking XP and quest begun; conflicts with Darkan omission',
         body_path=_PACKET + 'sources/dirty-blast-6084510.txt',
         sha256='4a8178217950901e8bd176dbd4197557a542071985a064ec5afc7b99112d6704'),
    dict(url='https://web.archive.org/web/20121107054633id_/http://www.runehq.com/quest/recipe-for-disaster',
         timestamp='2012-11-07T05:46:33Z', passages='322, 327, 329: advance and purchasable mixing route',
         body_path=_PACKET + 'sources/runehq-20121107054633.html',
         sha256='a71877e1a88a0a3c89db5e42b77e6bfb0377306e2bb8e1d1dc43783c835cb194'),
    dict(url='https://web.archive.org/web/20120920041824id_/http://runescape.salmoneus.net/quests/recipe-for-disaster.html',
         timestamp='2012-09-20T04:18:24Z', passages='305–308: conflicting traded-cocktail exclusion, not adopted',
         body_path=_PACKET + 'sources/sals-20120920041824.html',
         sha256='1f27f0d2c002e8110a4f8d9e41d37c914e2eff4cc9d38ac9b5eef314d920ba82'),
)
SOURCE_LIMITATIONS = (
    'Numeric IDs are cache/reconstruction facts, not dated prose consensus; retained item reports SHA-256 '
    '3887183d15026ec5f60a775dfcf644b979fd241a2b0d3584e195baea286071a2.',
    '9514 suffix is a storage compatibility decision accepting the special cocktail, not a recovered period name.',
    'Darkan AnotherCooksQuestState.kt:50–58 awards no preparation XP; 5.0 needs independent pre-cutoff numeric corroboration.',
    'Darkan is modern reconstruction: origin 8433aa485dc02cf5c2fb7206edb87d549488fa94; lifecycle b2f533cb8854fc788aa86d12a97853c30d132ecf; '
    'aggregate 8ce74d20eefd61a7ce6a41101484931d944d7b76; two-ID acceptance 675abb549c625d4801dfb2360ae2ec16dea82e70. See sources/darkan/lineage.json.',
    'Rev667 unavailable, not checked-negative. Cache definitions cannot establish server XP, provenance, atomicity or obtainability; 9514 gains no acquisition route.',
    'Fruit Blast6309046, Premade Fruit Blast6080846, Lemon5838228, Lemon slices5838230 and Orange6359054 carry beta markers. '
    'Their health/stat values are not adopted; Fruit Blast 80 LP versus Cooking6548144 90 LP remains outside this opening. '
    'Recipe/eligibility is corroborated by non-beta RFD6538752, Dirty blast6084510, Gnome cooking6438943 and archived guides. '
    'Shaker/glass wiki tradeability versus cache exchangeability does not establish new GE permissions.',
    'Asset source bytes and normalized pixels are separate evidence: most bundled ingredient pixels agree despite byte differences; '
    'Fruit blast, Knife and Coins pixel discrepancies remain unresolved. Rotten tomato art is later hand-in work.',
    'Additional supplying definitions and corroboration remain in source-index.json and assertions.json; later 2025 fields are not period-qualified.',
)
OPENING_ITEM_DATA = {
    name: dict(category='material', source_item_id=STORAGE_IDENTITIES[name], stackable=False,
               tradeable=False, source=f'{DIRTY_BLAST_SOURCE}; {CACHE_SOURCE}; {SOURCE_LIMITATIONS[1]}')
    for name in ('Dirty blast', 'Fruit blast (9514)')
}
STATIC_JOURNAL = ("Speak to the Cook in Lumbridge Castle's kitchen.",)
COMMISSION_JOURNAL = (
    "The Cook asked me for an Eye of newt, a Greenman's ale, a Rotten tomato and a Dirty blast.",
    'He gave me 100 Coins for the ingredients and said I could keep the change.',
    "I need to add Ashes to a Fruit blast to prepare the Dirty blast. Blurberry's premade drink will not work.",
)
PREPARED_LINE = 'I added Ashes to a Fruit blast and prepared a Dirty blast.'


def apply_another_cook_opening(quest):
    if quest.id != QUEST_ID:
        return quest
    # Import locally: the proof-rule owner also imports other quest data overlays.
    from ..quest_action_proof_data import ANOTHER_COOK_DIRTY_BLAST_PROOF
    opening = QuestStageRequirement(
        stage=OPENING_STAGE, description='Prepare a Dirty blast for the Cook',
        required_skills=(QuestSkillRequirement('cooking', 'Cooking', COOKING_REQUIREMENT),),
        required_actions=(ANOTHER_COOK_DIRTY_BLAST_PROOF,), source=OPENING_SOURCE,
    )
    return replace(quest,
                   stage_requirements=tuple(opening if row.stage == OPENING_STAGE else row for row in quest.stage_requirements),
                   journal_stages=tuple(QuestStage(OPENING_STAGE, STATIC_JOURNAL) if row.stage == OPENING_STAGE else row for row in quest.journal_stages),
                   source=f'Opening only: {OPENING_SOURCE}; later fields retain: {quest.source}')
