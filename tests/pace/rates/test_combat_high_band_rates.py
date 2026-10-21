"""Plan Part J item 1, XP per tick at speed 1 and speed 10: Sol's band 60, 80 and 99 Combat pairs."""

from tests.pace.rates import rate_property


class CombatHighBandRateTests(rate_property.RatePropertyCase):
    GROUPS = ("combat band 60", "combat band 80", "combat band 99")
