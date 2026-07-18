"""Pinned pre-EOC XP/hour rates, for use by tools/xp_rate_audit.py.

Every rate was read from a wiki revision dated strictly before the `2012-11-20`
EOC cutoff, per memory-bank/pre-eoc-source-verification-standard.md. Ranges stay
ranges; no midpoints were invented. A method with no pre-cutoff rate is absent —
absence is a finding, not a gap to fill.

`includes` is the load-bearing field. A quoted XP/hour is measured under some set
of conditions, and if a modifier is baked into the quote, granting it a second
time at runtime double-counts it. The 2012 F2P Mining guide quotes iron at 45k
*with urns*; base is therefore ~37.5k. Feed 45k into a cadence contract and then
award urn XP separately and you land at 54k. Every rate must declare what is
already inside it.
"""

from __future__ import annotations

from typing import NamedTuple


class Rate(NamedTuple):
    low_xp_hr: int
    high_xp_hr: int
    xp_per_action: float
    level: int
    includes: tuple[str, ...]  # modifiers baked INTO the quote; never re-apply
    citation: str

    def base_xp_hr(self, urn_fraction: float = 0.20) -> tuple[float, float]:
        """Strip modifiers the runtime grants separately, leaving base XP/hour.

        Urns return 20% of the base XP used to fill them, so a quote of X with
        urns implies a base of X / 1.20.
        """
        divisor = 1.0 + (urn_fraction if "urns" in self.includes else 0.0)
        return (self.low_xp_hr / divisor, self.high_xp_hr / divisor)

    def actions_per_hour(self) -> tuple[float, float]:
        lo, hi = self.base_xp_hr()
        return (lo / self.xp_per_action, hi / self.xp_per_action)


MINING: dict[str, Rate] = {
    # P2P Mining training oldid 6564341 (2012-11-16): "35k to 38k per hour for most".
    "iron": Rate(35_000, 38_000, 35.0, 99, ("dropping",),
                 "P2P Mining training oldid 6564341"),
    # F2P Mining training oldid 6571684 (2012-11-18): "about 45000 XP per hour;
    # the fastest mining experience in the free game" — quoted WITH urns. This
    # remains a separate evidence row because its modifier does not apply to the
    # P2P endpoint above.
    "iron_f2p_urns": Rate(45_000, 45_000, 35.0, 99, ("urns", "dropping"),
                          "F2P Mining training oldid 6571684"),
    # Concentrated gold, Living Rock Caverns, no familiar, rune pick/adze.
    "gold": Rate(35_000, 40_000, 65.0, 99, ("dropping",),
                 "P2P Mining training oldid 6564341"),
}
# Deliberately absent: copper, tin, coal, mithril, adamantite, runite. No
# pre-cutoff guide states an XP/hour for any of them. Runite's absence is itself
# the signal — it is discussed only as a money method ("300k to 600k coins per
# hour", P2P Mining training oldid 6564341). A runite cadence contract therefore
# cannot be derived from these pages and stays source_blocked.

WOODCUTTING: dict[str, Rate] = {
    # P2P Woodcutting training oldid 6548109 (2012-11-11). The guide's table
    # header states outright: "Experience with urns will be included".
    "tree": Rate(10_000, 15_000, 25.0, 99, ("urns",), "P2P Woodcutting training oldid 6548109"),
    "oak": Rate(18_000, 45_000, 37.5, 99, ("urns",), "P2P Woodcutting training oldid 6548109"),
    "willow": Rate(30_000, 60_000, 67.5, 99, ("urns",), "P2P Woodcutting training oldid 6548109"),
    "maple": Rate(36_000, 36_000, 100.0, 99, ("urns",), "P2P Woodcutting training oldid 6548109"),
    "yew": Rate(23_000, 38_000, 175.0, 99, ("urns",), "P2P Woodcutting training oldid 6548109"),
    "magic": Rate(17_000, 30_000, 250.0, 99, ("urns",), "P2P Woodcutting training oldid 6548109"),
    # Ivy yields no logs, so urns cannot apply; the by-level table's 99 row is 80k.
    "ivy": Rate(60_000, 80_000, 332.5, 99, (), "P2P Woodcutting training oldid 6548109 (lvl-99 row)"),
}

# Thieving is not implemented yet. Kept here so the audit can grade it the day
# it lands, and so the contract can be written against measured numbers.
THIEVING: dict[str, Rate] = {
    "menaphite_thug_blackjack": Rate(
        200_000, 270_000, 275.0, 99, (),
        "Menaphite Thug oldid 6546629: '270,000 xp/hr at 99 thieving'. "
        "275 = two picks x 137.5 per knock-out; the page gives a 3.6s cycle.",
    ),
    "dwarf_trader": Rate(150_000, 225_000, 556.5, 99, (),
                         "Trader oldid 6382333; Thieving training oldid 6393196"),
    "knight_of_ardougne": Rate(180_000, 180_000, 84.3, 99, ("multi-loot",),
                               "Thieving training oldid 6393196 ('upwards of 180,000')"),
    "gnome": Rate(150_000, 150_000, 198.5, 95, ("multi-loot", "85 Agility"),
                  "Gnome oldid 6192050 (triple loot)"),
    "master_farmer": Rate(70_000, 100_000, 43.0, 99, (), "Thieving training oldid 6393196"),
    # Stall rates are the Thieving article's own E.P.S. column x 3600 — a stated
    # period rate. Single-stall; the page notes gem stalls are "ideal to world hop",
    # so these are per-stall contributions, not a player's ceiling.
    "stall_vegetable": Rate(18_000, 18_000, 10.0, 2, (), "Thieving oldid 6563563 E.P.S. 5.0/s"),
    "stall_bakers": Rate(23_040, 23_040, 16.0, 5, (), "Thieving oldid 6563563 E.P.S. 6.4/s"),
    "stall_silk": Rate(10_800, 10_800, 24.0, 20, (), "Thieving oldid 6563563 E.P.S. 3.0/s"),
    "stall_silver": Rate(6_480, 6_480, 54.0, 50, (), "Thieving oldid 6563563 E.P.S. 1.8/s"),
    "stall_spice": Rate(3_600, 3_600, 81.0, 65, (), "Thieving oldid 6563563 E.P.S. 1.0/s"),
    "stall_gem": Rate(3_240, 3_240, 160.0, 75, (), "Thieving oldid 6563563 E.P.S. 0.9/s"),
    "wall_safe": Rate(20_000, 20_000, 70.0, 60, (), "Thieving training oldid 6393196 ('around 20k/h')"),
}

FISHING: dict[str, Rate] = {
    # P2P Fishing training oldid 6567695, 2012-11-17. Every rate here is the
    # guide's own no-urn, no-familiar baseline where it states one.
    "shark": Rate(20_000, 20_000, 110.0, 76, (),
                  "P2P Fishing oldid 6567695: 'only 20k experience per hour'"),
    "monkfish": Rate(25_000, 40_000, 120.0, 85, (),
                     "P2P Fishing oldid 6567695: '25k-40k per hour without urns'"),
    # Fly fishing is a mixed trout/salmon catch; the guide gives a combined rate
    # and the F2P page gives the blended 58 xp/catch. Graded against the blend.
    "trout": Rate(36_000, 40_000, 58.0, 77, (),
                  "P2P Fishing oldid 6567695: '36-40k/hr with no familiars or urns'; "
                  "F2P oldid 6576399 gives the blended 58 xp/catch"),
    # Barbarian fishing, cutting method, explicit no-urn no-familiar baseline.
    "leaping_sturgeon": Rate(30_000, 35_000, 90.0, 70, (),
                             "P2P Fishing oldid 6567695: '30k-35k with neither urns nor familiars'"),
    # FLAG: the rocktail quote folds urns in and cannot be decomposed. Recorded
    # with urns declared so the audit strips an estimated share, but this row is
    # the weakest in the table and must not be used to set a cadence contract.
    "rocktail": Rate(48_000, 48_000, 380.0, 90, ("urns",),
                     "P2P Fishing oldid 6567695: 'roughly 48,000 per hour ... if fishing urns "
                     "are present' — urns NOT decomposable; treat as indicative only"),
}

HUNTER: dict[str, Rate] = {
    # Hunter training oldid 6549266, 2012-11-12. Level-matched rates only.
    "catch_red_chinchompa": Rate(50_000, 100_000, 265.0, 63, (), "Hunter training oldid 6549266"),
    "catch_chinchompa": Rate(15_000, 82_000, 198.0, 53, (), "Hunter training oldid 6549266"),
    "catch_red_salamander": Rate(40_000, 110_000, 272.0, 59, (), "Hunter training oldid 6549266"),
    "catch_black_salamander": Rate(30_000, 200_000, 304.0, 67, (), "Hunter training oldid 6549266"),
    "catch_orange_salamander": Rate(60_000, 90_000, 224.0, 47, (), "Hunter training oldid 6549266"),
    "catch_dark_kebbit": Rate(35_000, 55_000, 132.0, 57, (), "Hunter training oldid 6549266 (falconry)"),
    "catch_spotted_kebbit": Rate(30_000, 40_000, 104.0, 43, (), "Hunter training oldid 6549266 (falconry)"),
    "barehand_black_warlock": Rate(
        140_000,
        140_000,
        650.0,
        95,
        (),
        "Hunter training oldid 6549266 (barehand butterfly catching)",
    ),
}
# The 140k/hr figure is for BAREHAND catching (650 Hunter XP/catch, level 95).
# `catch_black_warlock` remains the incompatible 54-XP butterfly-net route.

COOKING: dict[str, Rate] = {
    # P2P Cooking training oldid 6579488, 2012-11-19. The no-urn column.
    # Cooking's roll is a BURN roll, so these grade the burn rate, not cadence.
    "cook_lobster": Rate(150_000, 150_000, 120.0, 60, (), "P2P Cooking oldid 6579488 (no urns, range)"),
    "cook_monkfish": Rate(190_000, 190_000, 150.0, 84, (), "P2P Cooking oldid 6579488 (no urns)"),
    "cook_shark": Rate(263_000, 263_000, 210.0, 92, ("cooking gauntlets",),
                  "P2P Cooking oldid 6579488 (no urns; gauntlets needed for the quoted burn-stop)"),
    "cook_tuna": Rate(125_000, 125_000, 100.0, 30, (), "P2P Cooking oldid 6579488 (no urns, range)"),
}

FIREMAKING: dict[str, Rate] = {
    # P2P Firemaking training oldid 6487910, 2012-10-28.
    # FLAG: the same revision states magic-log XP as both 303.8 (body + bonfire
    # table) and 308.8 (header table). Not averaged — 303.8 used, discrepancy
    # recorded in the provenance ledger.
    "magic_logs": Rate(364_560, 364_560, 303.8, 75, (),
                  "P2P Firemaking oldid 6487910: '1200 logs per hour ... 364,560 experience' "
                  "(ordinary fire, no Penance horn). XP/log stated inconsistently as 303.8/308.8."),
}

# --- Deterministic artisan methods: the cleanest possible read of R ---
#
# These have NO success roll. No adapter, no probability, no modifier estimation.
# So XP/review IS XP/action, and `sourced XP/hr / XP/action` measures R directly,
# with nothing in the path. That makes them better evidence for R than anything
# derived from a rolled skill.
#
# They converge on ~900-1,200. The High Alchemy row is not even inference: the
# period page states the cast count outright — "can be cast up to exactly 1200
# times in one hour which adds up to 78,000 xp/hr".
DETERMINISTIC: dict[str, Rate] = {
    "magic/high_alchemy": Rate(78_000, 78_000, 65.0, 55, ("fire staff",),
                               "High Level Alchemy oldid 6587004: 'up to exactly 1200 times in "
                               "one hour which adds up to 78,000 xp/hr'"),
    "crafting/dragonhide_body": Rate(186_000, 186_000, 186.0, 63, (),
                                     "P2P Crafting training oldid 6547050 (level-63 row)"),
    "prayer/gilded_altar_dragon_bones": Rate(230_000, 230_000, 252.0, 1, ("gilded altar 350%",),
                                             "P2P Prayer training oldid 6571012"),
    "crafting/battlestaves": Rate(220_000, 220_000, 100.0, 54, (),
                                  "P2P Crafting training oldid 6547050 ('~2,200 battlestaves/hr')"),
    "crafting/urns_ardougne": Rate(39_900, 39_900, 95.0, 59, (),
                                   "P2P Crafting training oldid 6547050 ('~420 urns/hr')"),
    "magic/superheat_mithril": Rate(84_800, 84_800, 53.0, 43, ("fire staff",),
                                    "Superheat Item oldid 6586989: '1600 mithril bars per hour' "
                                    "x 53 magic xp/cast"),
}
# Click-spam outliers deliberately excluded from the R estimate: fletching bolts
# are quoted at 250-560k XP/hr on 5-7 XP actions, implying 50,000-80,000 actions
# per hour. Those are not a player action rate; they are a mouse-macro rate, and
# the guide says so ("click-intensive"). Recording them as an R signal would be
# reading a UI limit as a game constant.

BY_SKILL = {
    "Mining": MINING,
    "Woodcutting": WOODCUTTING,
    "Fishing": FISHING,
    "Hunter": HUNTER,
    "Cooking": COOKING,
    "Firemaking": FIREMAKING,
    "Thieving": THIEVING,
}
