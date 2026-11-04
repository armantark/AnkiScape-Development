"""Deadline cleanup still exercises a live child after slow interpreter startup."""

import unittest

from tests.promotion import test_local_test_host


class LocalDeadlineReadinessTests(unittest.TestCase):
    def test_startup_longer_than_deadline_still_checks_child_cleanup(self):
        fixture = test_local_test_host.LocalTestHostTests()
        self.addCleanup(fixture.doCleanups)
        fixture.setUp()
        for early_exit in (False, True):
            with self.subTest(early_exit=early_exit):
                # Each case needs a fresh readiness record and owned process group.
                (fixture.root / "child.json").unlink(missing_ok=True)
                fixture._assert_deadline_stops_child(early_exit=early_exit, startup_delay=1.2)
