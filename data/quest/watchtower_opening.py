"""Watchtower's directed investigation; historical evidence is metadata only."""

from pathlib import Path as _Path

from .contract import QuestStage, QuestStageRequirement, QuestSkillRequirement
from ...generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG as _CATALOG

__all__ = ()

QUEST_ID = "watchtower"
COMMISSION_PROOF = "Receive the Watchtower Wizard's missing-crystals commission"
SEARCH_PROOF = "Find Fingernails in the bushes outside the Watchtower"
PRESENTATION_PROOF = "Give the bush evidence to the Watchtower Wizard and finish his explanation"
OPENING_PROOFS = (COMMISSION_PROOF, SEARCH_PROOF, PRESENTATION_PROOF)
PHASE_EVENTS = {
    "commission": ("quest_service", "watchtower_commission"),
    "search": ("quest_service", "watchtower_bush_search"),
    "present": ("quest_service", "watchtower_present_fingernails"),
}
PHASE_PROOFS = dict(zip(PHASE_EVENTS, OPENING_PROOFS))
# PLACEHOLDER(watchtower.fingernails_transaction_quantity): qualified period bush-grant and Wizard-debit counts would replace this owner-approved provisional count
CLUE_QUANTITY = 1
SOURCE = "https://runescape.wiki/w/Watchtower?oldid=6525573"
FINGERNAILS_SOURCE = "https://runescape.wiki/w/Fingernails?oldid=6407465"

# W6525573:30 disagrees: Magic 15. Both struct627 bodies and RuneHQ,
# Tip.It and Sal's give Magic 14; this is not unanimous dated-source agreement.
WATCHTOWER_SKILLS = tuple(QuestSkillRequirement(*row) for row in (
    ("agility", "Agility", 25), ("herblore", "Herblore", 14),
    ("magic", "Magic", 14), ("mining", "Mining", 40),
    ("thieving", "Thieving", 15),
))
WATCHTOWER_REQUIREMENTS = ("Agility 25", "Herblore 14", "Magic 14", "Mining 40", "Thieving 15")
PENDING_JOURNAL = (
    "Speak to the Watchtower Wizard about the missing power crystals.",
    "Search the bushes north-east of the Watchtower for Fingernails.",
    "Give the Fingernails to the Wizard and finish asking what to do next.",
)
COMMISSION_JOURNAL = (
    "The Watchtower Wizard asked me to investigate the missing power crystals.",
    "I can now use the ladder to reach him.",
)
SEARCH_JOURNAL = "I found Fingernails by searching the bushes outside the Watchtower."
COMPLETED_JOURNAL = (
    "I investigated the missing power crystals for the Watchtower Wizard.",
    "I searched the bushes and gave him the Fingernails.",
    "After I asked what to do next, he identified the thieves as Skavids, servants of the ogres, and asked me to recover the four crystals.",
)
LEGACY_JOURNAL = ("No bush-investigation evidence is recorded.",)
WATCHTOWER_JOURNAL_STAGES = tuple(
    QuestStage(row["stage"], PENDING_JOURNAL if row["stage"] == 1 else tuple(row["journal"]))
    for quest in _CATALOG if quest["id"] == QUEST_ID
    for row in quest["journal_stages"]
)


def opening_stage_requirements(quest_id, requirements):
    if quest_id != QUEST_ID:
        return requirements
    opening = QuestStageRequirement(
        stage=1, description="Investigate the missing power crystals for the Watchtower Wizard.",
        required_skills=(QuestSkillRequirement("agility", "Agility", 18),),
        required_actions=OPENING_PROOFS, source=SOURCE,
    )
    return tuple(opening if row.stage == 1 else row for row in requirements)


_ASSET_DIR = _Path(__file__).resolve().parent / "watchtower_assets"
WATCHTOWER_ITEM_IMAGES = {"Fingernails": str(_ASSET_DIR / "fingernails.png")}
WATCHTOWER_ITEMS = {
    "Fingernails": {
        "category": "material", "source_item_id": 2384, "model_id": 1787,
        "stackable": False, "tradeable": False, "client_options": ("Destroy",),
        "source": FINGERNAILS_SOURCE,
        "provenance_sources": ("F6407465", "cache727_items", "cache742_items", "asset"),
        "destroy_warning": "This item will likely break if you put it down here, and you will have to go looking for another.",
        "asset_provenance": str(_ASSET_DIR / "fingernails.provenance.json"),
        "license_note": "Historical inventory image pinned; Inventory license template recorded; template terms not resolved.",
    },
}

# Supplying paths are evidence locators, never runtime dependencies. Original
# locators refer to the unnumbered wikitext or original HTML, not reader extracts.
SOURCE_RECORDS = {
    "W6525573": {
        "page": "Watchtower", "url": SOURCE, "timestamp": "2012-11-03T08:25:45Z",
        "body": "sources/watchtower-6525573.txt",
        "sha256": "8e6725ed4adcb188e8dcaaf682f86eea4c62008909b59197b474062d93a3c142",
        "locators": ("23", "28–35", "36–51", "65", "67", "71–73", "75–77", "79"),
        "conditions": "Initial northern trellis needs Agility 18; after commission the ladder is permitted. Search relevant bushes north-east of the tower. Return and conclude the conversation before the excluded ogre route at 79.",
        "quantities_units": "Agility 18 initial; quest-wide Agility 25, Herblore 14, Magic 15, Mining 40, Thieving 15; four crystals; whole-quest 23–43 Coins and 2 Ropes, not opening costs; Fingernails count not stated",
        "corroboration": "RuneHQ HTML263/270 commission/search/presentation/conclusion; F6407465:19/21 acquisition/giving; no prerequisite quest in W28–35 and RuneHQ/Sal's requirements",
        "disagreements": "W30 Magic 15 versus cache and three guides Magic 14. W73 optional other finds versus guides' collect-all advice; advice is not a prerequisite. No independent directional corroboration for north-east (north-west places tower relative to Yanille). Exact return-dialogue sequence has single-wiki support.",
        "return_dialogue": "'What should I do?' then 'So what do I do?\"",
        "missing_fields": "Numeric Fingernails grant/debit, search probability, bush IDs, empty-bush timing, reacquisition gates: not stated",
    },
    "F6407465": {
        "page": "Fingernails", "url": FINGERNAILS_SOURCE, "timestamp": "2012-10-14T21:36:01Z",
        "body": "sources/fingernails-6407465.txt",
        "sha256": "9c3b51255ef0860a7922463b826b452fed830512a486a687006e56dc9c82bbca",
        "locators": ("2–3", "8–10", "14", "19", "21"),
        "conditions": "Nontradeable, unequippable, nonstackable; acquired by bush search and given to Wizard. Later cave acquisition does not establish opening search.",
        "quantities_units": "Numeric grant/debit and physical nail count: not stated; value=1 is not quantity evidence",
        "corroboration": "W73–77 and RuneHQ HTML270", "disagreements": "not stated",
        "missing_fields": "Search probability and transaction quantity: not stated",
    },
    "RuneHQ": {
        "page": "RuneHQ Watchtower", "url": "https://web.archive.org/web/20121103183241id_/http://www.runehq.com:80/quest/watchtower",
        "timestamp": "2012-11-03T18:32:41Z", "body": "sources/runehq-watchtower-20121103183241.html",
        "sha256": "c60e0a8515bf710bafb6c105abaeb31f14c9ed65f688b3a3c8693eeb5812b838",
        "locators": ("HTML245–250", "HTML263", "HTML270", "HTML272"),
        "conditions": "Commission, bush search, Wizard takes Fingernails and concludes; other finds have no use. No quest prerequisite.",
        "quantities_units": "Agility 25, Herblore 14, Magic 14, Mining 40, Thieving 15; Fingernails numeral not stated",
        "corroboration": "W67/73–77 and F19/21; caches, Tip.It and Sal's on skills",
        "disagreements": "Collect-all advice differs from W73 optionality; Magic 14 differs from W30 Magic 15",
        "missing_fields": "Independent north-east direction, exact return dialogue and numeric grant/debit: not stated",
    },
    "TipIt": {
        "page": "Tip.It Watchtower", "url": "https://web.archive.org/web/20121119221212id_/http://www.tip.it:80/runescape/index.php?rs2quest_id=64",
        "timestamp": "2012-11-19T22:12:12Z", "body": "sources/tipit-watchtower-20121119221212.html",
        "sha256": "f89dd6db5e9f6e8e74f6d056078a4d5df6e6e545f2ceb7f4a63f4a479e585cfe",
        "locators": ("HTML246", "HTML255", "HTML271"),
        "conditions": "Quest-wide skills; ladder permission after starting",
        "quantities_units": "Magic 14; initial numeric trellis threshold not stated",
        "corroboration": "Caches, RuneHQ and Sal's Magic 14; W65 ladder permission",
        "disagreements": "W30 Magic 15; collect-all advice versus W73 optionality",
        "missing_fields": "Numeric Fingernails grant/debit and independent exact dialogue: not stated",
    },
    "Sals": {
        "page": "Sal's Realm Watchtower", "url": "https://web.archive.org/web/20120920041841id_/http://runescape.salmoneus.net/quests/watchtower.html",
        "timestamp": "2012-09-20T04:18:41Z", "body": "sources/sals-watchtower-20120920041841.html",
        "sha256": "f3398c0675fa54650bc58eb18cedb686e54739f3442cc1cc311ede3e0e7c9537",
        "locators": ("HTML174–175", "HTML193–200"),
        "conditions": "Quest-wide skills, no quest prerequisites; commission and later-use candle",
        "quantities_units": "Magic 14; numeric Fingernails grant/debit not stated",
        "corroboration": "Caches, RuneHQ and Tip.It Magic 14",
        "disagreements": "W30 Magic 15; collect-all advice versus W73 optionality",
        "missing_fields": "Independent exact return dialogue and north-east direction: not stated",
    },
}
for _build, _cache, _date in ((727, 309, "2012-07-24"), (742, 544, "2012-11-07")):
    SOURCE_RECORDS[f"cache{_build}_items"] = {
        "page": f"Client build {_build}/cache{_cache} item 2384", "url": f"https://archive.openrs2.org/caches/runescape/{_cache}",
        "timestamp": _date, "body": f"sources/cache-{_build}-items.txt", "locators": ("1",),
        "sha256": "f5350a071b252e060c983744fd678b88c0f4f047b5972852a764e4e8be05323d",
        "conditions": "Item 2384 Fingernails, model 1787, nonstackable, nonexchangeable, Destroy",
        "quantities_units": "Item identity, not quantity; grant/debit not stated",
        "corroboration": "Other bracketed client and F6407465", "disagreements": "not stated",
        "missing_fields": "Search probability and transaction quantity: not stated",
    }
    SOURCE_RECORDS[f"cache{_build}_struct627"] = {
        "page": f"Client build {_build}/cache{_cache} struct627", "url": f"https://archive.openrs2.org/caches/runescape/{_cache}",
        "timestamp": _date, "body": f"sources/cache-{_build}-struct627.txt", "locators": ("10–19", "14–15"),
        "sha256": "f1eb7ae9df53afb7f128c5aea8c0a230ac3fba563e3515c0a3133aeb85d8b454",
        "conditions": "Quest-wide start skills; skill 6 is Magic, level 14",
        "quantities_units": "Agility 25, Herblore 14, Magic 14, Mining 40, Thieving 15",
        "corroboration": "Other bracketed cache, RuneHQ HTML247, Tip.It HTML246, Sal's HTML174",
        "disagreements": "W6525573:30 Magic 15", "missing_fields": "Opening transactions: not stated",
    }
SOURCE_RECORDS["asset"] = {
    "page": "File:Fingernails.png", "url": "https://runescape.wiki/w/File:Fingernails.png?oldid=6410504",
    "timestamp": "2012-10-15T02:21:48Z", "locators": ("1–3",),
    "body": "sources/fingernails-file-6410504.txt",
    "sha256": "8babb6a54becb9d2e6a943b9ceb507d71eca44786579244440b382559a14b3e4",
    "conditions": "Selected upload 2011-11-21T01:58:16Z; archive filename 2014 is replacement boundary, not upload date",
    "quantities_units": "29×25 pixels, 1210 bytes; model 1787 does not authenticate PNG",
    "corroboration": "F6407465:3 image association; binary SHA-1 matches historical imageinfo",
    "disagreements": "not stated", "missing_fields": "Inventory license template observed; template terms not resolved",
}
PROVISIONAL_COUNT_DECISION = {
    "authority": "Owner answer 2026-10-24 08:54 PDT",
    "value": CLUE_QUANTITY, "unit": "inventory object",
    "transaction": "One object granted by successful directed search, one debited at presentation",
    "historical_quantity": "not stated",
    "replacement_evidence": "Explicitly quantified period bush grant and Wizard debit",
    "interpretation": "Provisional representation, not one physical nail or a historical one-per-search rate",
}

# Exact original supplying lines, including W77's malformed closing quote.
SOURCE_RECORDS['W6525573']["original_lines"] = {
    23: '|start = Begin the quest by speaking to [[Watchtower Wizard]] north-west of [[Yanille]] in the [[Watchtower (building)|Watchtower]]. You must climb the trellis (requiring an agility level of 18) on the north side of the tower to get up for the first time.',
    28: '|requirements=',
    29: '{{Skillreq|Herblore|14}}',
    30: '{{Skillreq|Magic|15}}',
    31: '{{Skillreq|Thieving|15}}',
    32: '{{Skillreq|Agility|25}}',
    33: '{{Skillreq|Mining|40}}',
    34: '*Must be able to defeat a level 68 [[ogre]] and survive against several aggressive level 53 ogres',
    35: '*Ability to survive against several level 111 [[Blue dragon]]s in a confined dungeon situation',
    65: "Begin the quest by talking to the [[Watchtower Wizard]] on the top floor of the Watchtower, just north of Yanille. Be careful as the guide marker in RuneScape leads far away from the tower. To ascend the tower, you must climb up the trellis on the northern side of the building, as the guards will not let you climb up the ladder. After starting the quest you'll be allowed to proceed up the ladder.",
    67: 'The Watchtower Wizard will tell you that the [[crystal (quest item)|power crystals]] that protect Yanille from the ogres to the south are missing, and suggests you to look outside the bushes to find some clues.',
    71: "'''''NOTE:''''' The bushes to search are just north-east of the Watchtower.",
    73: 'You should take the [[lit candle]] from the ground floor of the Watchtower, if you did not bring a light source. Search the bushes outside and show any items that you get to the wizard. The bushes that contain the items are a stark contrast from the empty ones, so search them to find some [[fingernails]]. Other items obtained include an [[old robe]], a [[damaged dagger]], an [[unusual armour]] and a [[tattered eye patch]], but these items have no apparent use and are not necessary for the quest.',
    75: 'Go back inside the Watchtower and talk to the Watchtower Wizard again.',
    77: 'During this conversation you \'\'\'MUST\'\'\' ask him \'Shall I search the caves?\' or \'What should I do?\', and then ask \'So what do I do?" If you do not, it will be as if you never talked to him at all, and Og will not talk to you later on. He will tell you that [[Skavid]]s, the servants of the ogres, have stolen the four [[crystal (quest item)|crystals]]. Your job is to recover them.',
}
SOURCE_RECORDS['F6407465']["original_lines"] = {
    2: '|name = Fingernails',
    3: '|image = [[File:Fingernails.png|Fingernails]]',
    8: '|tradeable = No',
    9: '|equipable = No',
    10: '|stackable = No',
    14: '|destroy = This item will likely break if you put it down here, and you will have to go looking for another.',
    19: "'''Fingernails''' is a quest item that appears in the [[Watchtower]] quest. The player can find it by searching the bushes surrounding the Watchtower outside the north wall of [[Yanille]].",
    21: 'The fingernails must be given to the wizard in the Watchtower in order for him to be able to identify who stole the [[Crystal (quest item)|power crystals]] that make the tower operate.',
}
SOURCE_RECORDS['RuneHQ']["original_lines"] = {
    247: '14 <a href="/guide.php?type=skill&amp;id=389">Magic</a><br />',
    263: 'Once you have reached the top floor of the watchtower, talk to to the <a href="/database.php?type=person&amp;id=136">Watchtower Wizard</a>, who will start complaining. Choose the option "What\'s the matter?" and he\'ll tell you that the watchtower is not working and therefore the people of Yanille are not protected against the Ogres. Ask him what he means and the wizard will explain that the tower uses a magical spell to ward off the Ogres. He will then tell you that they no longer have the knowledge about the spell but that the essence of the spell been kept in 4 crystals that power the shield. Ask way why the spell is not working. He will inform you that the crystals have been stolen. Offer your help and he will tell you to search for clues in the surrounding area.',
    270: 'Go down sets of stairs to the first floor and pick up the <a href="/database.php?type=item&amp;id=310">Lit candle</a> from the table as you will need it later in the quest. Search the bushes around the watchtower for some <a href="/database.php?type=item&amp;id=408">Fingernails</a>, a <a href="/database.php?type=item&amp;id=1829">Tattered eye patch</a>, a <a href="/database.php?type=item&amp;id=1827">Damaged dagger</a>, an <a href="/database.php?type=item&amp;id=1830">Unusual armour</a>, and an <a href="/database.php?type=item&amp;id=1828">Old robe</a>. Once you have found them all, head back to the <a href="/database.php?type=person&amp;id=136">Watchtower Wizard</a> using the ladder on the first floor and show him the items. He will take the <a href="/database.php?type=item&amp;id=408">Fingernails</a> and tells you that the creature that took the crystals is a Skavid, a servant of the Ogres, who live in the caves. Ask what you can do about it and he will you that it would be useless to search the caves without a map. He will suggest that you talk to the surrounding tribes and sends you on mission to recover the 4 crystals.',
    272: '<span class="smallbold">Note: </span>You may drop the remaining items as they have no use during or after the quest.',
}
SOURCE_RECORDS['TipIt']["original_lines"] = {
    246: '<p><b>Start location:</b> Watchtower on the north-west corner of the wall surrounding Yanille. On the North side of the tower, find the "climb trellis" spot to climb up to the second floor.  Then go up the ladder and talk with the Watchtower Wizard on the third floor.</p><div><b>Required:</b> <p><u>Skills</u>: Level 25 Agility, Level 14 Herblore, Level 14 Magic, Level 40 Mining, Level 15 Thieving</p><p><u>Other Skills:</u> Be able to kill level 68 monsters.</p>',
}
SOURCE_RECORDS['Sals']["original_lines"] = {
    174: '    <li><strong>Skills:</strong> Ability to defeat level 68 enemies, 14 <a href="skills/herblore.html" class="skill">Herblore</a>, 14 <a href="skills/magic.html" class="skill">Magic</a>, 15 <a href="skills/thieving.html" class="skill">Thieving</a>, 25 <a href="skills/agility.html" class="skill">Agility</a>, 40 <a href="skills/mining.html" class="skill">Mining</a></li>',
    175: '    <li><strong>Quests:</strong> None.</li>',
}
SOURCE_RECORDS["W6525573"]["revision"] = 6525573
SOURCE_RECORDS["F6407465"]["revision"] = 6407465
SOURCE_RECORDS["asset"]["revision"] = 6410504
SOURCE_RECORDS["RuneHQ"]["capture"] = "20121103183241"
SOURCE_RECORDS["TipIt"]["capture"] = "20121119221212"
SOURCE_RECORDS["Sals"]["capture"] = "20120920041841"
