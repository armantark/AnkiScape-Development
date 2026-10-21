"""Plan Part J item 1, XP per tick at speed 1 and speed 10: Combat's own sample and Sol's band 20 and 40 pairs."""

from tests.pace.rates import rate_property


class CombatRateTests(rate_property.RatePropertyCase):
    GROUPS = ("combat", "combat band 20", "combat band 40")
