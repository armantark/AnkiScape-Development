"""Hand-maintained period reward overrides at the live catalog boundary.

Generated family modules retain their registered placeholder fallback values.
This overlay is authoritative for live lamp rewards; it does not retire the
placeholder register. Tasks, gates, equipment and source identities stay intact.
The retained source packet supplies the revision bodies and independent archive
captures cited below; no live revisions are fetched to apply these overrides.
"""

from dataclasses import replace

from .contract import DiaryFamily, DiaryLamp, DiaryTier


# Each pin records the retained wiki revision/date and exact reward lines,
# followed by the independent archive/date and its matching reward lines.
# Wiki "over"/"above" wording conflicts with inclusive "minimum"/"N+"
# archive statements; the latter select the inclusive live boundaries.
_PINS = {
    # A: sources/ardougne-achievements-6579397.txt and
    # sources/extra-http-www-tip-it-runescape-page-ardougne-tasks-htm-20120614213944.html
    "ardougne": (
        "https://runescape.wiki/w/index.php?title=Ardougne_achievements&oldid=6579397",
        "2012-11-18T22:07:06Z", ("279", "480", "685", "795"),
        "https://web.archive.org/web/20120614213944id_/http://www.tip.it:80/runescape/?page=ardougne_tasks.htm",
        "2012-06-14T21:39:44Z", ("1021", "1083", "1144", "1205"),
    ),
    # F: sources/falador-achievements-6571459.txt and
    # sources/extra-http-www-tip-it-runescape-page-falador-tasks-htm-20120419111015.html.
    # RuneHQ independently confirms inclusive Elite floors (saved body
    # sources/runehq-falador-20121015174934.html), lines 361–363, UTC
    # 2012-10-15T17:49:34Z. The owner's 2026-10-20 21:29 answer assigns
    # the original identifier to 84 and the missing 50,000-XP lamp to 72.
    "falador": (
        "https://runescape.wiki/w/index.php?title=Falador_achievements&oldid=6571459",
        "2012-11-18T05:31:03Z", ("158", "363", "535", "662-664"),
        "https://web.archive.org/web/20120419111015id_/http://www.tip.it/runescape/?page=falador_tasks.htm",
        "2012-04-19T11:10:15Z", ("888", "943", "1000", "1062"),
    ),
    # R: sources/fremennik-achievements-6555812.txt and
    # sources/extra-http-www-tip-it-runescape-page-fremennik-tasks-htm-20120328083655.html.
    # sources/runehq-fremennik-province-20120816021833.html, UTC
    # 2012-08-16T02:18:33Z, lines 282, 356 also state inclusive floors.
    "fremennik": (
        "https://runescape.wiki/w/index.php?title=Fremennik_achievements&oldid=6555812",
        "2012-11-14T23:17:11Z", ("189", "342", "498", "636-637"),
        "https://web.archive.org/web/20120328083655id_/http://www.tip.it:80/runescape/?page=fremennik_tasks.htm",
        "2012-03-28T08:36:55Z", ("921", "982", "1040", "1108"),
    ),
    # K: sources/karamja-achievements-6372400.txt and
    # sources/extra-http-www-tip-it-runescape-page-karamja-tasks-htm-20120805193609.html
    "karamja": (
        "https://runescape.wiki/w/index.php?title=Karamja_achievements&oldid=6372400",
        "2012-10-09T03:25:58Z", ("171", "412", "576", "706-707"),
        "https://web.archive.org/web/20120805193609id_/http://www.tip.it:80/runescape/?page=karamja_tasks.htm",
        "2012-08-05T19:36:09Z", ("875", "929", "984", "1043"),
    ),
    # L: sources/lumbridge-achievements-6549949.txt and
    # sources/extra-http-www-tip-it-runescape-page-lumbridge-tasks-htm-20120419085553.html.
    # Wiki explicitly says "or higher"/"or above"; older oldid 3162002,
    # line 380 says "over level 49", a retained historical wording conflict.
    # Beginner's original (500, 1) is unresolved and remains the same object.
    "lumbridge": (
        "https://runescape.wiki/w/index.php?title=Lumbridge_achievements&oldid=6549949",
        "2012-11-12T17:54:35Z", ("814", "938", "1050"),
        "https://web.archive.org/web/20120419085553id_/http://www.tip.it/runescape/?page=lumbridge_tasks.htm",
        "2012-04-19T08:55:53Z", ("1435", "1489", "1547"),
    ),
    # M: sources/morytania-achievements-6530421.txt and
    # sources/extra-http-www-tip-it-runescape-page-morytania-tasks-htm-20120703001723.html.
    # Wiki Elite statements are also explicitly inclusive.
    "morytania": (
        "https://runescape.wiki/w/index.php?title=Morytania_achievements&oldid=6530421",
        "2012-11-04T03:16:45Z", ("154", "360", "501", "621-622"),
        "https://web.archive.org/web/20120703001723id_/http://www.tip.it:80/runescape/?page=morytania_tasks.htm",
        "2012-07-03T00:17:23Z", ("954", "1019", "1083", "1145"),
    ),
    # S: sources/seers-village-achievements-6504286.txt and
    # sources/final-http-www-tip-it-runescape-page-seers-village-tasks-htm-20120419110632.html.
    # The original 25,000-XP lamp is unresolved: wiki line 617 says 70 or
    # above; Tip.It line 994 says 80+. Reuse its level-1 fallback object.
    # This dispute does not affect the four supported 30,000-XP lamps at 83+.
    "seers": (
        "https://runescape.wiki/w/index.php?title=Seers%27_Village_achievements&oldid=6504286",
        "2012-10-30T17:38:08Z", ("182", "341", "493", "616"),
        "https://web.archive.org/web/20120419110632id_/http://www.tip.it/runescape/?page=seers_village_tasks.htm",
        "2012-04-19T11:06:32Z", ("813", "874", "937", "994"),
    ),
    # V: sources/varrock-achievements-6476032.txt and
    # sources/extra-http-www-tip-it-runescape-page-varrock-tasks-htm-20121025081303.html.
    # Wiki and Tip.It support inclusive minima; RuneHQ's "above" wording
    # remains a conflict, not unanimous corroboration.
    "varrock": (
        "https://runescape.wiki/w/index.php?title=Varrock_achievements&oldid=6476032",
        "2012-10-26T14:55:51Z", ("256", "518", "697", "840-841"),
        "https://web.archive.org/web/20121025081303id_/http://www.tip.it:80/runescape/?page=varrock_tasks.htm",
        "2012-10-25T08:13:03Z", ("1054", "1115", "1176", "1238"),
    ),
}

_MINIMUMS = {
    "ardougne": (25, 45, 60), "falador": (30, 40, 50),
    "fremennik": (30, 40, 50), "karamja": (30, 40, 50),
    "lumbridge": (30, 35, 49), "morytania": (25, 46, 65),
    "seers": (30, 40, 50), "varrock": (30, 40, 50),
}
_ELITE = {
    "ardougne": ((50000, 85),) * 4,
    "falador": ((50000, 84), (50000, 72), (30000, 90), (30000, 90)),
    "fremennik": ((40000, 89),) + ((30000, 86),) * 4,
    "karamja": ((30000, 64), (55000, 87), (55000, 87)),
    "morytania": ((40000, 75), (50000, 80), (50000, 80)),
    "seers": ((25000, 1),) + ((30000, 83),) * 4,
    "varrock": ((30000, 65),) + ((40000, 88),) * 3,
}


def _source(family_id: str, tier_index: int) -> str:
    wiki, date, lines, archive, archive_date, archive_lines = _PINS[family_id]
    source = (f"{wiki} (UTC {date}, lines {lines[tier_index]}); "
              f"{archive} (UTC {archive_date}, lines {archive_lines[tier_index]})")
    if family_id == "falador" and tier_index == 3:
        source += ("; https://web.archive.org/web/20121015174934id_/"
                   "http://www.runehq.com:80/task/falador "
                   "(UTC 2012-10-15T17:49:34Z, lines 361-363)")
    if family_id == "fremennik" and tier_index == 3:
        source += ("; https://web.archive.org/web/20120816021833id_/"
                   "http://www.runehq.com:80/task/fremennik-province "
                   "(UTC 2012-08-16T02:18:33Z, lines 282, 356)")
    return source


def _override_tier_lamps(family_id: str, tier: DiaryTier) -> DiaryTier:
    tier_name = tier.id.removeprefix(f"{family_id}_")
    if tier_name in ("easy", "medium", "hard"):
        index = ("easy", "medium", "hard").index(tier_name)
        lamp = replace(tier.lamp, minimum_level=_MINIMUMS[family_id][index],
                       source=_source(family_id, index))
        return replace(tier, lamp=lamp)
    if tier_name != "elite" or family_id not in _ELITE:
        return tier
    lamps = tuple(
        DiaryLamp(experience, minimum, source=_source(family_id, 3))
        for experience, minimum in _ELITE[family_id]
    )
    # The disputed Seers original keeps its exact generated fallback object.
    original = tier.lamp if family_id == "seers" else lamps[0]
    return replace(tier, lamp=original, extra_lamps=lamps[1:])


def _override_family_lamps(family: DiaryFamily) -> DiaryFamily:
    if family.id not in _MINIMUMS:
        return family
    return replace(family, tiers=tuple(_override_tier_lamps(family.id, tier) for tier in family.tiers))


def apply_lamp_reward_overrides(families: tuple[DiaryFamily, ...]) -> tuple[DiaryFamily, ...]:
    """Replace only lamp fields, preserving generated objects everywhere else."""
    return tuple(_override_family_lamps(family) for family in families)
