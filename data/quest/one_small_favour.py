"""Source-bound first journal deeds; action descriptions are not recovered dialogue."""

from pathlib import Path

QUEST_ID = 'one_small_favour'
BLUNT_HATCHET = 'Blunt hatchet'
source_item_id = 4415
FORESTER_GRANT_QUANTITY = 1
BRIAN_TAKE_QUANTITY = 1
BLUNT_HATCHET_ICON = str(Path(__file__).resolve().parent / 'assets' / 'blunt_hatchet.png')

OPENING_DEEDS = (
    {'event_type': 'quest_service', 'event_id': 'one_small_favour:yanni_commission',
     'proof': 'One Small Favour: accept Yanni’s request for red mahogany'},
    {'event_type': 'quest_service', 'event_id': 'one_small_favour:forester_hatchet',
     'proof': 'One Small Favour: receive the Jungle Forester’s Blunt hatchet'},
    {'event_type': 'quest_service', 'event_id': 'one_small_favour:shanks_referral',
     'proof': 'One Small Favour: obtain Captain Shanks’s referral to Port Sarim'},
    {'event_type': 'quest_service', 'event_id': 'one_small_favour:brian_handoff',
     'proof': 'One Small Favour: hand the Blunt hatchet to Brian for sharpening'},
    {'event_type': 'quest_service', 'event_id': 'one_small_favour:aggie_request',
     'proof': 'One Small Favour: agree to find Aggie’s missing apprentice Jimmy'},
    {'event_type': 'quest_service', 'event_id': 'one_small_favour:ham_entry',
     'proof': 'One Small Favour: pick the H.A.M. entrance lock and climb down'},
    {'event_type': 'quest_service', 'event_id': 'one_small_favour:johanhus_request',
     'proof': 'One Small Favour: obtain Johanhus’s request for one month’s supply of chickens from Fred'},
 )
OPENING_PROOFS = tuple(deed['proof'] for deed in OPENING_DEEDS)
REPLACEMENT_EVENT_ID = 'one_small_favour:replace_hatchet'
REPLACEMENT_MESSAGE = 'The Jungle Forester replaced the lost Blunt hatchet.'

OPENING_SOURCE = (
    'W One Small Favour oldid 6546338 (2012-11-10T04:51:00Z), lines 78, 83–84, 91–93; '
    'Q Quick guide oldid 6178350 (2012-09-02T13:09:44Z), lines 43–45, 50–52; '
    'T Tip.It capture 20121119221247, lines 251, 255, 259, 263, 267, 271.'
)
BLUNT_HATCHET_ITEMS = {
    BLUNT_HATCHET: {
        'category': 'material', 'source_item_id': source_item_id,
        'stackable': False, 'tradeable': False,
        'source': 'B oldid 5806478 lines 8–10, 14–15, 20; ' + OPENING_SOURCE,
    },
}

PERIOD_SOURCES = {'W': {'id': 'W',
       'title': 'One Small Favour',
       'saved': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1430-one-small-favour-forester-to-ham-opening/sources/one-small-favour-6546338.txt',
       'revision_or_build': '6546338',
       'timestamp_utc': '2012-11-10T04:51:00Z',
       'date_utc': '2012-11-10',
       'url': 'https://runescape.wiki/w/index.php?title=One_Small_Favour&oldid=6546338&action=raw',
       'rung': 'R4 dated wiki',
       'sha256': '9caa22d5a9e4e6a45b4f423d7741db07a5f9c07785a45c104f15126cacfa25eb',
       'original': None},
 'Q': {'id': 'Q',
       'title': 'One Small Favour/Quick guide',
       'saved': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1430-one-small-favour-forester-to-ham-opening/sources/one-small-favour-quick-guide-6178350.txt',
       'revision_or_build': '6178350',
       'timestamp_utc': '2012-09-02T13:09:44Z',
       'date_utc': '2012-09-02',
       'url': 'https://runescape.wiki/w/index.php?title=One_Small_Favour%2FQuick_guide&oldid=6178350&action=raw',
       'rung': 'R4 dated wiki',
       'sha256': 'cc708c976f977ac7fe024ee1c8f0c0a0e98e79fb227fcee033c929e810c6bc6d',
       'original': None},
 'B': {'id': 'B',
       'title': 'Blunt hatchet',
       'saved': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1430-one-small-favour-forester-to-ham-opening/sources/one-small-favour-blunt-hatchet-oldid-5806478.txt',
       'revision_or_build': '5806478',
       'timestamp_utc': '2012-06-21T23:50:22Z',
       'date_utc': '2012-06-21',
       'url': 'https://runescape.wiki/w/index.php?title=Blunt_hatchet&oldid=5806478&action=raw',
       'rung': 'R4 dated wiki',
       'sha256': 'ea3aa7f545654450531ca03a459a16e83597304cae7c7485d67f63b5bcc5ec5f',
       'original': None},
 'H': {'id': 'H',
       'title': 'H.A.M. Hideout',
       'saved': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1430-one-small-favour-forester-to-ham-opening/sources/ham-hideout-6436476.txt',
       'revision_or_build': '6436476',
       'timestamp_utc': '2012-10-18T09:19:58Z',
       'date_utc': '2012-10-18',
       'url': 'https://runescape.wiki/w/index.php?title=H.A.M._Hideout&oldid=6436476&action=raw',
       'rung': 'R4 dated wiki',
       'sha256': 'f9f6baf52dccbf41d733cb99278bf4a0c7ee3ee834815887595b991751d0f1c8',
       'original': None},
 'G': {'id': 'G',
       'title': 'One Small Favour Quest Guide — Global RuneScape',
       'saved': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1430-one-small-favour-forester-to-ham-opening/sources/unit-3452-tea-globalrs-20121024035309-20261023.html',
       'revision_or_build': 'capture 20121024035309',
       'timestamp_utc': '2012-10-24T03:53:09Z',
       'date_utc': '2012-10-24',
       'url': 'https://web.archive.org/web/20121024035309id_/http://www.global-rs.com/quests/onesmallfavour/',
       'rung': 'Independent contemporary article (consensus check)',
       'sha256': '52f4e4a1ffa24fb6773b03893b230e1c6cf6b08e3964147ac001611113f4fabb',
       'original': '/Users/armantarkhanian/Documents/2012scape with '
                   'bots/memory-bank/audit/sources/unit-3452-tea-globalrs-20121024035309-20261023.html'},
 'T': {'id': 'T',
       'title': 'One Small Favour — Tip.It RuneScape Quest Database',
       'saved': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1430-one-small-favour-forester-to-ham-opening/sources/tipit-20121119221247.html',
       'revision_or_build': 'capture 20121119221247',
       'timestamp_utc': '2012-11-19T22:12:47Z',
       'date_utc': '2012-11-19',
       'url': 'https://web.archive.org/web/20121119221247id_/http://www.tip.it:80/runescape/index.php?rs2quest_id=90',
       'rung': 'Independent contemporary article (consensus check)',
       'sha256': '2e82c1cf336310066fbe19cad24d6cae1796017fc90c42e1ed921292e3c0a60f',
       'original': None},
 'I': {'id': 'I',
       'title': 'File:Blunt hatchet.png',
       'saved': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1430-one-small-favour-forester-to-ham-opening/sources/blunt-hatchet-20111118.png',
       'revision_or_build': 'historical imageinfo',
       'timestamp_utc': '2011-11-18T05:39:54Z',
       'date_utc': '2011-11-18',
       'url': 'https://runescape.wiki/images/archive/20140502173803%21Blunt_hatchet.png?a4164',
       'rung': 'R4 dated wiki asset; visual only',
       'sha256': 'f77e78293dd6f01d55c0ac968e3c8f33b67e32fadff360cda59c9d3708c3ae9a',
       'original': None},
 'C': {'id': 'C',
       'title': 'OpenRS2 One Small Favour retained cache comparison',
       'saved': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1430-one-small-favour-forester-to-ham-opening/sources/openrs2-cache-727-742-one-small-favour.json',
       'revision_or_build': '727/728/729/736/741/742',
       'timestamp_utc': '2012-07-24 through 2012-11-07; times not stated',
       'date_utc': '2012-07-24',
       'url': 'https://archive.openrs2.org/caches',
       'rung': 'R1 build727; R3 other historical caches; retained extract',
       'sha256': '34a9f354ed864082e1cfc1edcf05a02c58bb359e58a99f3683257c17ec36a467',
       'original': None},
 'K': {'id': 'K',
       'title': 'Darkan One Small Favour frozen target contract',
       'saved': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1430-one-small-favour-forester-to-ham-opening/sources/one-small-favour-target-contract.json',
       'revision_or_build': 'iteration112; baseline406b38a7c8a983c75f5eec22f4ad260679d3c15e',
       'timestamp_utc': None,
       'date_utc': 'not stated',
       'url': 'local retained audit/evidence/static/one-small-favour-target-contract.json',
       'rung': 'R1 restoration qualification; not a period article',
       'sha256': 'f27b8386347d55d88e9ee2b381a1d514bc39d851df8f49cea5e612bb19e9a269',
       'original': None},
 'D': {'id': 'D',
       'title': 'Darkan OneSmallFavour.kt',
       'saved': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1430-one-small-favour-forester-to-ham-opening/sources/OneSmallFavour.kt',
       'revision_or_build': 'HEAD517bdeaaf16dbe3cbfe80ee74a91f7fbe944aaed; supplying '
                            'opening2a967f71b6f4b3a613c1a5ccba2cb5f3130c7274',
       'timestamp_utc': '2026-07-14T09:22:09Z',
       'date_utc': '2026-07-14',
       'url': 'src/main/java/com/rs/game/content/quests/onesmallfavour/OneSmallFavour.kt',
       'rung': 'R1 modern restoration implementation; not historical proof',
       'sha256': 'ffa29107d9c7089035a9c28b6cd1f564342a327aad1bc2b5ac3f8c6e5e38a375',
       'original': None},
 'DH': {'id': 'DH',
        'title': 'Darkan HAMHideout.java',
        'saved': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1430-one-small-favour-forester-to-ham-opening/sources/HAMHideout.java',
        'revision_or_build': 'HEAD517bdeaaf; history in ham-provenance.log',
        'timestamp_utc': None,
        'date_utc': 'not stated',
        'url': 'src/main/java/com/rs/game/content/world/areas/h_a_m_hideout/HAMHideout.java',
        'rung': 'R1 implementation; provenance by line in ham-blame.txt',
        'sha256': '6b5973a057cdfb321745f9b3d700f16c9b375c77f9c12415f977e6482e3d7c5d',
        'original': None},
 'DT': {'id': 'DT',
        'title': 'Darkan Thieving.java',
        'saved': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1430-one-small-favour-forester-to-ham-opening/sources/Thieving.java',
        'revision_or_build': 'supplying HAM_TRAPDOOR ba1f5e8eb0a3bad405025a4e747d23385c5192f0',
        'timestamp_utc': '2026-07-19T21:49:59Z',
        'date_utc': '2026-07-19',
        'url': 'src/main/java/com/rs/game/content/skills/thieving/Thieving.java',
        'rung': 'R1 restoration implementation; not historical proof',
        'sha256': '79e2d4bf5bf268553a84ca6b84afa06bc3b0696f4159fb84eda1d5c49c1df18a',
        'original': None}}

PASSAGE_NOTES = {
    'commission': 'W78; Q43; independent G125 (capture 20121024035309) and T251. '
        'D190 describes a walking stick; W78 antique polish. Only their common red-mahogany commission is used.',
    'forester': 'Q44; B20 (oldid 5806478); independent T255 explicitly obtains the blunt axe. '
        'W83 supplies the sharpening favour. G129 describes sharpening, not an explicit inventory grant.',
    'shanks': 'W84; Q45; B20; independent G131 and T259. No hatchet transfer. '
        'W84 permits an optional 26–42-Coin ticket or alternative travel; T259 permits teleporting. '
        'No fixed debit or mandatory voyage.',
    'brian': 'W91; Q50; independent T263 explicitly says Brian takes the blunt axe now. '
        'G133 describes the favour, not an explicit inventory transfer.',
    'aggie': 'W92; Q51; independent G135 and T267. Missing apprentice Jimmy. '
        'Conflicting accounts of Brian’s friend’s legal status are excluded.',
    'hideout_johanhus': 'W93; Q52; independent G137–141 and T271. A month’s supply is duration, '
        'not a numeric bird count. W95, Q55–56 and G145–147 start excluded Fred/Seth work.',
    'identity_properties': 'C retains item 4415 across builds 727/728/729/736/741/742; D30. '
        'Cache identity does not establish custody. B8–10 and B14–15 supply nontradeable, '
        'not equipable, not stackable, Drop and no shop. Independent property corroboration was not found.',
    'quantities': 'D150–178 and D192/195–196: +1 and −1 from reconstruction commit '
        '2a967f71b6f4b3a613c1a5ccba2cb5f3130c7274, 2026-07-14T09:22:09Z, '
        'corroborated by singular period transfers. Server checkpoints are not journal stages.',
    'recovery': 'D193 is an implementation lead only. Original replacement terms were not found '
        'in checked period sources. Authority: decisions.md:3, owner answer 2026-10-24 08:59 PDT: '
        'Keep Discard and replace a lost hatchet on an extra quest review after Shanks, before Brian.',
    'entrance_numbers': 'H oldid 6436476 (2012-10-18T09:19:58Z), line 20: hand entry and '
        '0.5 XP per attempt. DH58–85 and DT57 implement level 15 and 4 XP on success; '
        'DT supplying commit ba1f5e8eb0a3bad405025a4e747d23385c5192f0, 2026-07-19T21:49:59Z. '
        'Disagreement and missing independent numeric corroboration remain. This opening adds '
        'no Thieving threshold, lockpick, XP, probability or RNG.',
}
