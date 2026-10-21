"""Plan Part J item 1, XP per tick at speed 1 and speed 10: Firemaking, Cooking and Herblore."""

from tests.pace.rates import rate_property


class FiremakingCookingHerbloreRateTests(rate_property.RatePropertyCase):
    GROUPS = ("firemaking", "cooking", "herblore")
