"""Plan Part J item 1, XP per tick at speed 1 and speed 10: Utility / Activities."""

from tests.pace.rates import rate_property


class ActivityRateTests(rate_property.RatePropertyCase):
    GROUPS = ("utility",)
