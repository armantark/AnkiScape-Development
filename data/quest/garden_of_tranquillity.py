from .contract import QuestStage
from ...generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG


# Source: https://runescape.wiki/w/index.php?title=Garden_of_Tranquillity&oldid=6541904
# Revision timestamp: 2012-11-08T00:20:27Z.
# Packet SHA-256: 6df88b7bc6cc0881c2cdbcc02a47e8e216328c3168b2adf27e950cd104352030.
# Remove only the leading # and italic delimiter pairs ''; L60 introduces the
# answers and L69 resumes the ring paragraph. L65 originally reads:
# #You of course ''(Player Name), ''no one could ever challenge your greatness!
# Revision 5942764 (2012-07-16T04:34:08Z) repeats these answers, but shares the
# publisher and is not independent corroboration. RuneHQ capture 20121113235302
# supports answer 5's flattery but recommends different answers 6-7. Sal's capture
# 20121018045254 supports answers 6-7 but recommends a different answer 5.
# These guides do not unanimously agree or establish that alternatives are invalid.
# The quick-guide packet has no historical revision and supplies no corroboration.
GARDEN_OF_TRANQUILLITY_ANSWERS = (
    "Show them a range of colours so that they can come to a compromise.",  # L61 → 5
    "Take his generous gift even though you have no need for it.",  # L62 → 6
    "It's absolutely, unquestionably the most interesting thing I've ever done!",  # L63 → 7
    "Put on the silly helmet and jump into the cannon.",  # L64 → 8
    "You of course (Player Name), no one could ever challenge your greatness!",  # L65 → 9
    "Ask me nicely and I might consider it.",  # L66 → 10
    "No, especially not that wise old man, who doesn't look at all suspicious.",  # L67 → 11
)


def _adapt_garden_journal_stage(raw_stage):
    journal = tuple(raw_stage["journal"])
    if raw_stage["stage"] == 1:
        journal = journal[:5] + GARDEN_OF_TRANQUILLITY_ANSWERS + journal[5:]
    return QuestStage(raw_stage["stage"], journal)


GARDEN_OF_TRANQUILLITY_JOURNAL_STAGES = tuple(
    _adapt_garden_journal_stage(stage)
    for quest in PRE_EOC_QUEST_CATALOG if quest["id"] == "garden_of_tranquillity"
    for stage in quest["journal_stages"]
)
