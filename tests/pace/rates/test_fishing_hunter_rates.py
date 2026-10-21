"""Plan Part J item 1, XP per tick at speed 1 and speed 10: Fishing and Hunter."""

from tests.pace.rates import rate_property


class FishingHunterRateTests(rate_property.RatePropertyCase):
    GROUPS = ("fishing", "hunter")
