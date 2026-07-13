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
    # F2P Mining training oldid 6571684 (2012-11-18): "about 45000 XP per hour;
    # the fastest mining experience in the free game" — quoted WITH urns.
    # P2P Mining training oldid 6564341 (2012-11-16): "35k to 38k per hour for most".
    "iron": Rate(35_000, 45_000, 35.0, 99, ("urns", "dropping"),
                 "F2P Mining training oldid 6571684; P2P oldid 6564341"),
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

BY_SKILL = {
    "Mining": MINING,
    "Woodcutting": WOODCUTTING,
    "Thieving": THIEVING,
}
