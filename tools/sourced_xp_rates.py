"""Pinned pre-EOC XP/hour rates, for use by tools/xp_rate_audit.py.

Every rate here was read from a wiki revision dated strictly before the
`2012-11-20` EOC cutoff, per memory-bank/pre-eoc-source-verification-standard.md.
Ranges are kept as ranges; no midpoints were invented. A method with no
pre-cutoff rate is simply absent — absence is a finding, not a gap to fill.

`xp_per_action` is the period XP for one action, so the audit can derive
actions/hour = xp_per_hour / xp_per_action without a second source.
"""

from __future__ import annotations

# (target_id, low_xp_hr, high_xp_hr, xp_per_action, assumed_level, citation)
Rate = tuple

MINING: dict[str, Rate] = {
    # "about 45000 XP per hour; the fastest mining experience in the free game"
    # F2P Mining training, oldid 6571684, 2012-11-18T05:53:07Z.
    # P2P Mining training, oldid 6564341: "35k to 38k per hour for most".
    "iron": (35_000, 45_000, 35.0, 99, "F2P Mining training oldid 6571684; P2P oldid 6564341"),
    # Concentrated gold, Living Rock Caverns, no familiar, rune pick/adze.
    "gold": (35_000, 40_000, 65.0, 99, "P2P Mining training oldid 6564341"),
}
# Deliberately absent: copper, tin, coal, mithril, adamantite, runite. No
# pre-cutoff guide states an XP/hour for any of them. Runite's absence is
# itself the signal — it is discussed only as a money method
# ("300k to 600k coins per hour", P2P Mining training oldid 6564341).

WOODCUTTING: dict[str, Rate] = {
    # P2P Woodcutting training, oldid 6548109, 2012-11-11T15:28:57Z.
    # NOTE: every rate in this guide's table assumes woodcutting urns.
    "tree": (10_000, 15_000, 25.0, 99, "P2P Woodcutting training oldid 6548109"),
    "oak": (18_000, 45_000, 37.5, 99, "P2P Woodcutting training oldid 6548109"),
    "willow": (30_000, 60_000, 67.5, 99, "P2P Woodcutting training oldid 6548109"),
    "maple": (36_000, 36_000, 100.0, 99, "P2P Woodcutting training oldid 6548109"),
    "yew": (23_000, 38_000, 175.0, 99, "P2P Woodcutting training oldid 6548109"),
    "magic": (17_000, 30_000, 250.0, 99, "P2P Woodcutting training oldid 6548109"),
    # Ivy has an explicit by-level table; the level-99 row is 80k.
    "ivy": (60_000, 80_000, 332.5, 99, "P2P Woodcutting training oldid 6548109 (lvl-99 row)"),
}

# Thieving is not implemented yet; these are the harvested targets for the
# contract, kept here so the audit can grade Thieving the day it lands.
THIEVING: dict[str, Rate] = {
    "menaphite_thug_blackjack": (
        200_000, 270_000, 275.0, 99,
        "Menaphite Thug oldid 6546629: '270,000 thieving experience per hour at 99'. "
        "275 = 2 picks x 137.5 per knock-out cycle (3.6s).",
    ),
    "dwarf_trader": (150_000, 225_000, 556.5, 99, "Trader oldid 6382333; Thieving training oldid 6393196"),
    "knight_of_ardougne": (180_000, 180_000, 84.3, 99, "Thieving training oldid 6393196 ('upwards of 180,000')"),
    "gnome": (150_000, 150_000, 198.5, 95, "Gnome oldid 6192050 (triple loot, 85 Agility)"),
    "master_farmer": (70_000, 100_000, 43.0, 99, "Thieving training oldid 6393196"),
    # Stall rates come from the Thieving article's own E.P.S. column, which is a
    # stated period rate. XP/hr = E.P.S. x 3600. Single-stall, no world-hopping.
    "stall_vegetable": (18_000, 18_000, 10.0, 2, "Thieving oldid 6563563, E.P.S. column (5.0/s)"),
    "stall_bakers": (23_040, 23_040, 16.0, 5, "Thieving oldid 6563563, E.P.S. column (6.4/s)"),
    "stall_silk": (10_800, 10_800, 24.0, 20, "Thieving oldid 6563563, E.P.S. column (3.0/s)"),
    "stall_silver": (6_480, 6_480, 54.0, 50, "Thieving oldid 6563563, E.P.S. column (1.8/s)"),
    "stall_spice": (3_600, 3_600, 81.0, 65, "Thieving oldid 6563563, E.P.S. column (1.0/s)"),
    "stall_gem": (3_240, 3_240, 160.0, 75, "Thieving oldid 6563563, E.P.S. column (0.9/s)"),
    "wall_safe": (20_000, 20_000, 70.0, 60, "Thieving training oldid 6393196 ('around 20k/h')"),
}

BY_SKILL = {
    "Mining": MINING,
    "Woodcutting": WOODCUTTING,
    "Thieving": THIEVING,
}
