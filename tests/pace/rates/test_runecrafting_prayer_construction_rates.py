"""Plan Part J item 1, XP per tick at speed 1 and speed 10: Runecrafting, Prayer and Construction."""

from tests.pace.rates import rate_property


class RunecraftingPrayerConstructionRateTests(rate_property.RatePropertyCase):
    GROUPS = ("runecrafting", "prayer", "construction")
