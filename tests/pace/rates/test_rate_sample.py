"""The Part J rate sample covers what the plan says it covers, and every group runs."""

import importlib
import math
import pkgutil
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic.cadence_coverage import cadence_coverage_rows_pure
from ankiscape.runtime.runtime_actions_context import ONE_PER_CARD_HANDLER_KEYS
from tests.pace import rates
from tests.pace.rates import rate_property

# Farming grows between cards and Slayer rides on Combat: neither is a card's route.
_NOT_CARD_ROUTES = frozenset({"farming", "slayer"})


class RateSampleTests(unittest.TestCase):
    def setUp(self):
        self.rows = cadence_coverage_rows_pure()
        self.sampled = [route for routes in rate_property.SAMPLE.values() for route in routes]

    def test_every_rate_limited_route_is_sampled(self):
        rate_limited = {(row["handler_key"], row["action_id"]) for row in self.rows if row["mode"] == "rate_limited"}
        self.assertTrue(rate_limited)
        self.assertLessEqual(rate_limited, {(route.handler_key, route.action_id) for route in self.sampled})

    def test_every_handler_key_paced_by_ticks_has_at_least_three_catalog_routes(self):
        catalog = {(row["handler_key"], row["action_id"]) for row in self.rows}
        paced = {row["handler_key"] for row in self.rows} - ONE_PER_CARD_HANDLER_KEYS - _NOT_CARD_ROUTES
        by_key: dict[str, set[str]] = {}
        for route in self.sampled:
            self.assertIn((route.handler_key, route.action_id), catalog, route)
            by_key.setdefault(route.handler_key, set()).add(route.action_id)
        self.assertEqual(set(by_key), paced)
        for handler_key, action_ids in by_key.items():
            self.assertGreaterEqual(len(action_ids), 3, handler_key)

    def test_every_group_runs_in_exactly_one_test_module(self):
        groups = []
        for module_info in pkgutil.iter_modules(rates.__path__):
            module = importlib.import_module(f"{rates.__name__}.{module_info.name}")
            groups += [
                group
                for value in vars(module).values()
                if isinstance(value, type) and issubclass(value, rate_property.RatePropertyCase)
                for group in value.GROUPS
            ]
        self.assertCountEqual(groups, rate_property.SAMPLE)


class PairedSeedComparisonTests(unittest.TestCase):
    def test_a_consistent_offset_cannot_hide_inside_shared_seed_variance(self):
        x1 = [float(100 * seed) for seed in rate_property.SEEDS]
        for offset in (-1, 1):
            with self.subTest(offset=offset):
                x10 = [value + offset for value in x1]
                apart = rate_property.standard_errors_apart(x1, x10)
                self.assertTrue(math.isinf(apart), apart)
                self.assertEqual(math.copysign(1.0, apart), offset)
