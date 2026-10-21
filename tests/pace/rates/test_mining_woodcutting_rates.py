"""Plan Part J item 1, XP per tick at speed 1 and speed 10: Mining and Woodcutting."""

from tests.pace.rates import rate_property


class MiningWoodcuttingRateTests(rate_property.RatePropertyCase):
    GROUPS = ("mining", "woodcutting")
