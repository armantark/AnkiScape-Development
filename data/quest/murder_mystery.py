"""Hand-audited two-pickup opening; product wording is not original dialogue.

Source bodies are retained in the item-1260 evidence packet. Historical guides
supply the deeds, not AnkiScape stage numbering or transaction internals.
"""

from .contract import QuestStage, QuestStageRequirementCleanup

QUEST_ID = 'murder_mystery'
OPENING_ACTION = "Search the eastern murder scene and collect the Pungent pot and Criminal's dagger"
OPENING_OUTPUTS = (("Pungent pot", 1), ("Criminal's dagger", 1))
SOURCE_CUTOFF = "2012-11-20T00:00:00Z"
PERIOD_SOURCES = {
    'W1': {
        'title': 'Murder Mystery',
        'url': 'https://runescape.wiki/w/index.php?title=Murder_Mystery&oldid=6569570',
        'revision': '6569570',
        'timestamp': '2012-11-17T21:22:05Z',
        'saved_body': 'sources/murder-mystery-final-preeoc-oldid-6569570.txt',
        'sha256': '31126f1476e5bf3f743f191b078d60124a031734683be709428a483dcb47cc4a',
        'original_lines': (37, 39, 41, 43, 44, 45, 46, 47, 48, 50, 54),
        'extracts': {
            37: "To begin, talk to one of the guards near [[Sinclair Mansion]], located directly north of the Seers' Village. They tell you that [[Lord Sinclair]] has been murdered and they cannot figure out who killed him. Offer your help, and he says that you should question the family to gather information about the murder.",
            39: "First, search the murder scene, which is on the eastern side of the mansion. Inside will be a [[pungent pot]] which you should collect, along with the [[criminal's dagger]].",
            41: "Search the smashed window to find the [[criminal's thread]]. You will need to talk to the guard there to be able to investigate it. Whilst in this area, you must also investigate the wooden gate. Then, go around to the various bedrooms belonging to the suspects to find a number of silver items, all contained within barrels in each room. (There are four rooms upstairs and two on the ground floor.) Look for:",
            43: "*[[Anna Sinclair|Anna's]] [[Silver necklace]]",
            44: "*[[Bob Sinclair|Bob's]] [[Silver cup]]",
            45: "*[[Carol Sinclair|Carol's]] [[Silver bottle]]",
            46: "*[[David Sinclair|David's]] [[Silver book]]",
            47: "*[[Elizabeth Sinclair|Elizabeth's]] [[Silver needle]]",
            48: "*[[Frank Sinclair|Frank's]] [[Silver pot]]",
            50: 'Tip: As soon as you figure out whose fingerprint it is, check their story about how they used their poison. Verify that their story is not true by checking that area and then talk to the guard to finish the quest. You no longer have to talk to everyone else in the mansion to be able to finish the quest.',
            54: "Now it's time to get your first piece of evidence. Go to the Gardener's shed and search the sacks to find some [[flypaper]], you may need up to seven sheets, so collect them all if you have the inventory space. Go to the kitchen and fill your pot with flour (the kitchen is next to the stairs). Use the flour on the criminal's dagger, then use the dagger on a piece of flypaper to get an [[unknown print]] (Fill five pots with flour from the Sinclair Mansion' is also a easy [[Seers' Village Tasks|Seers' Village task]]).",
        },
    },
    'W2': {
        'title': 'Murder Mystery/Quick guide',
        'url': 'https://runescape.wiki/w/index.php?title=Murder_Mystery%2FQuick_guide&oldid=6512948',
        'revision': '6512948',
        'timestamp': '2012-10-31T18:08:41Z',
        'saved_body': 'sources/murder-mystery-quick-guide-oldid-6512948.txt',
        'sha256': '6a70bea37dc7a128a27d7f4c08f4b6d6f674bfa774c8335a4410e0036a86212b',
        'original_lines': (15, 18, 19, 21, 22, 31, 32, 33, 34),
        'extracts': {
            15: '*Talk to a [[Guard (Sinclair Mansion)|guard]] near [[Sinclair Mansion]] which is located North of [[Camelot Castle]].',
            18: '*Head to the Eastern side of the mansion.',
            19: "*Take the [[Pungent pot]] and [[Criminal's dagger]].",
            21: '*Talk to the guard there and then search the window.',
            22: "*Go in each of the suspects' rooms and look in the barrels to find:",
            31: "*Go to the gardener's shed and take seven flypapers from the sack.",
            32: '*Fill a [[pot]] with [[flour]] from the kitchen. ',
            33: '*Use the flour on the dagger and use flypaper to lift the fingerprint.',
            34: '*Repeat with the silver objects.',
        },
    },
    'W3': {
        'title': 'Pungent pot',
        'url': 'https://runescape.wiki/w/index.php?title=Pungent_pot&oldid=5133180',
        'revision': '5133180',
        'timestamp': '2012-01-09T23:59:00Z',
        'saved_body': 'sources/murder-mystery-pungent-pot-oldid-5133180.txt',
        'sha256': '84a1d0c7c02505c0fb906a0c86e5c6512ef78c776179f34ec6943e1fce555fcb',
        'original_lines': (3, 7, 8, 9, 10, 11, 15, 16, 17, 18),
        'extracts': {
            3: '|name = Pungent pot',
            7: '|members = Yes',
            8: '|quest = Yes',
            9: '|tradeable = No',
            10: '|equipable = No',
            11: '|stackable = No',
            15: '|examine = A pot found at the murder scene, with a sickly odour.',
            16: '}}',
            17: '',
            18: "[[File:Pungent pot detail.png|left|100px]]The '''Pungent pot''' is a [[quest]] [[item]] found at the murder scene during the [[Murder Mystery]] quest. It is later used as evidence during the murder investigation.",
        },
    },
    'W4': {
        'title': "Criminal's dagger",
        'url': 'https://runescape.wiki/w/index.php?title=Criminal%27s_dagger&oldid=6260613',
        'revision': '6260613',
        'timestamp': '2012-09-18T19:18:26Z',
        'saved_body': 'sources/murder-mystery-criminal-dagger-oldid-6260613.txt',
        'sha256': '3b4f40a7e3423291617febd854280424eaeedc1518820086075794a2ed1abfb4',
        'original_lines': (3, 7, 8, 9, 10, 11, 17, 21),
        'extracts': {
            3: "|name = Criminal's dagger",
            7: '|members = Yes',
            8: '|quest = Yes - [[Murder Mystery]]',
            9: '|stackable = No',
            10: '|equipable = No',
            11: '|tradeable = No',
            17: '|examine = A flimsy-looking dagger found at the crime scene./A flimsy looking dagger found at the crime scene coated with a thin layer of flour.',
            21: "The '''Criminal's dagger''' is a quest [[item]] that is found at the murder scene during the [[Murder Mystery]] [[quest]]. This dagger cannot be equipped and is used to help gather evidence against the culprit during the quest. In the quest, you must obtain the criminal's fingerprints by using a [[pot of flour]] on the dagger, then using [[flypaper]] on the dagger. You must do the same with the items belonging to the suspects. Then compare them by using a suspect's fingerprints on the criminal's fingerprint.",
        },
    },
    'A1': {
        'title': "Quest: Murder Mystery | Sal's Realm of RuneScape",
        'url': 'https://web.archive.org/web/20121018060902id_/http://runescape.salmoneus.net/quests/murder-mystery.html',
        'replay': '20121018060902',
        'timestamp': '2012-10-18T06:09:02Z',
        'saved_body': 'sources/sals-murder-mystery-20121018060902.html',
        'sha256': 'd49436b57a19bd67412ad9347138d2acd16fc89aa279750d1a98b72fbe5246a0',
        'original_lines': (191, 192, 193, 194, 195, 196, 199, 200, 201, 202),
        'extracts': {
            191: '<p><a id="fqw1" name="fqw1"></a>Start off by talking to one of the guards near <strong>Sinclair',
            192: 'Mansion</strong>, located',
            193: 'just north of the <a href="locations/seers-village.html">Seers\' Village</a>. He tells you that Lord',
            194: "Sinclair has been murdered and they can't figure out who killed him. Offer",
            195: 'your help, and he says that you should question the family about where',
            196: 'they were and such info that would help solve the crime.</p>',
            199: '<p><a id="fqw2" name="fqw2"></a>Go inside of the mansion and take a look at the east-most',
            200: 'room. This is where the murder took place, and the main evidence of the',
            201: 'crime can be found. <a id="fqw3" name="fqw3"></a>Take the Pungent Pot<img src="assets/images/quests/murder-mystery/pungentpot.gif" alt="Pungent pot" width="29" height="31" style="vertical-align:middle;" /> from the table, as well as the Criminal\'s Dagger<img src="assets/images/quests/murder-mystery/dagger.gif" alt="Criminal\'s dagger" width="24" height="34" style="vertical-align:middle;" /> from the center of the room. <a id="fqw4" name="fqw4"></a>Investigate the Smashed Window on the eastern',
            202: 'wall to find the Criminal\'s Thread<img src="assets/images/quests/murder-mystery/thread.gif" alt="Thread" width="31" height="31" style="vertical-align:middle;" />.</p>',
        },
    },
    'A2': {
        'title': 'Murder Mystery - RuneScape Guide - RuneHQ',
        'url': 'https://web.archive.org/web/20121103153756id_/http://www.runehq.com:80/quest/murder-mystery',
        'replay': '20121103153756',
        'timestamp': '2012-11-03T15:37:56Z',
        'saved_body': 'sources/runehq-murder-mystery-20121103153756.html',
        'sha256': 'd336f6838bc74b6d5c9357392df54faec96ce009f769b102a586a4cf5bcf718f',
        'original_lines': (251, 258, 310),
        'extracts': {
            251: 'Talk to the guard near the gate of the Sinclair Mansion, North of Seer\'s Village, and offer him help in finding the culprit. <span class="justbold">Note:</span> You must speak to everyone around the house and include every single option to complete the quest.',
            258: "Go to the room with all the evidence, including the Criminal's Dagger and pick up the Pungent Pot.",
            310: "Head back to the crime scene pick up the Criminal's dagger (see image step 2). Use your pot of flour with the dagger coat it with flour. Use a Flypaper with the dagger to obtain a Unknown print.",
        },
    },
}

CONFIGURATION_PROVENANCE = {
    "cache_rows": "sources/cache-row-verification.json",
    "cache_rows_sha256": "6e36d014c76d238138b37c45a684b4b4251278fc6f171121020c16e316da34d0",
    "cache_packet": "sources/openrs2-cache-727-742-murder-mystery.json",
    "cache_packet_sha256": "83a60209f945d0c2f7518df834bddd3a17f9fc4b13e1efe8bd298d9f6d5fa728",
    "builds": (727, 728, 729, 736, 741, 742),
    "cache_bounds": ("2012-07-24", "2012-11-07"),
    "cache_qualification": "Retained normalized rows verified; original archive bytes not redecoded. November 8–19 changes cannot be excluded. Darkan and 727 share a lineage.",
    "ids": {"Pungent pot": 1812, "clean dagger": 1813, "dusted dagger": 1814, "Empty pot": 1931},
    "configured_667": "sources/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt:1746–1748",
    "configured_667_qualification": "Modern emulation configuration; upstream supplying commit and historical authorship date not stated.",
    "darkan_body": "sources/darkan/MurderMystery.kt",
    "darkan_lines": (83, 84, 85, 214, 215, 216, 217, 354),
    "darkan_commit": "bdea22f7f98391da022256269db4fac4f095247b",
    "darkan_qualification": "Restoration code, not period server code; constants and dusting map distinguish clean 1813 from dusted 1814. Cache names alone do not.",
}
SOURCE_DECISIONS = {
    "selected_opening": "W1/W2/A1: commission and eastern collection of both items before the window.",
    "A2_disagreement": "A2:258 collects the pot, A2:310 delays the dagger until flour work. A2:251 requires every conversation/option; W1:50 disagrees. Neither A2 ordering nor its whole-quest conversation requirement is adopted.",
    "Darkan_disagreement": "Combined window/thread recovery and sequential partial grants are excluded. Restoration countAnywhere uniqueness is not adopted.",
    "historical_spawn": "not stated",
    "historical_capacity": "not stated",
    "historical_repeat_pickup": "not stated",
    "original_server_atomicity": "not found",
    "original_dialogue_transcript": "not found",
    "stage_endpoint": "Owner R1/R2, sources/owner-rulings.md:17–18; assigned in memory-bank/design-thread-queue.md:3019. Guides do not define AnkiScape stages.",
}
ASSET_SEARCH = {
    "saved_body": "sources/registry-asset-search.json",
    "sha256": "48f0128ebd9429bc0a2ff33adc35868e6028abb902a05bd46e4f64241e0c544a",
    "bitmap": "not found",
    "provenance": "not found",
    "artwork_certification": "not found",
}
_OPENING_SOURCE = "; ".join(PERIOD_SOURCES[key]["url"] for key in ("W1", "W2", "A1"))
_ID_SOURCE = "sources/cache-row-verification.json; sources/openrs2-cache-727-742-murder-mystery.json; configured-667 Items.kt:1746–1748"
MURDER_MYSTERY_OPENING_ITEMS = {
    "Pungent pot": {
        "category": "material", "item_id": 1812,
        "stackable": False, "tradeable": False,
        "source": PERIOD_SOURCES["W3"]["url"] + "; " + _OPENING_SOURCE + "; " + _ID_SOURCE,
    },
    "Criminal's dagger": {
        "category": "material", "item_id": 1813,
        "stackable": False, "tradeable": False,
        "source": PERIOD_SOURCES["W4"]["url"] + "; " + _OPENING_SOURCE + "; " + _ID_SOURCE
        + "; restoration Darkan MurderMystery.kt:83–85,214–217,354 @ "
        + CONFIGURATION_PROVENANCE["darkan_commit"] + " (clean 1813, dusted 1814; not period server code)",
    },
}
MURDER_MYSTERY_OPENING_CLEANUPS = (
    QuestStageRequirementCleanup(
        stage=1,
        remove_required_inventory=("Empty pot",),
        remove_required_actions=("Complete Murder Mystery stage 1 objective",),
        add_auto_actions=(OPENING_ACTION,),
        add_produced_inventory=OPENING_OUTPUTS,
        source=_OPENING_SOURCE,
    ),
)

OPENING_JOURNAL = (
    "At Sinclair Mansion, north of Seers' Village, a guard reports that Lord Sinclair has been murdered and the guards cannot identify the killer.",
    "Offer your help. The guard asks you to question the family to gather information about the murder.",
    "First, search the eastern murder scene and collect one Pungent pot and one Criminal's dagger.",
)
INVESTIGATION_JOURNAL = (
    "Talk to the guard at the smashed window, then search it for the Criminal's thread.",
    "Investigate the wooden gate.",
    "Search the barrels in the suspects' bedrooms for Anna's Silver necklace, Bob's Silver cup, Carol's Silver bottle, David's Silver book, Elizabeth's Silver needle and Frank's Silver pot.",
)
LEGACY_OPENING_JOURNAL = (
    "The guards at Sinclair Mansion, north of Seers' Village, cannot identify Lord Sinclair's murderer and ask for help gathering information from the family.",
    "The eastern murder scene contains a Pungent pot and Criminal's dagger.",
)


def murder_mystery_opening_journal_stages(quest_id, stages):
    if quest_id != QUEST_ID:
        return stages
    replacements = {1: OPENING_JOURNAL, 2: INVESTIGATION_JOURNAL}
    return tuple(
        QuestStage(row.stage, replacements[row.stage]) if row.stage in replacements else row
        for row in stages
    )
