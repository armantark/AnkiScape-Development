"""One unpatched reachability report per test process.

A live build walks every action and quest and takes about nine seconds on the
test host, so the unpatched callers across the suite share one build. Each
caller gets its own deep copy, so no test can see another test's edits. Tests
that patch game data must still call build_reachability_report() directly.
"""

import copy
from functools import cache
from typing import Any

from tools.audit_item_reachability import build_reachability_report


@cache
def _shared_build() -> dict[str, Any]:
    return build_reachability_report()


def live_reachability_report() -> dict[str, Any]:
    return copy.deepcopy(_shared_build())
