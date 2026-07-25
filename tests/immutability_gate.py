"""Shared machinery for the per-module input-immutability gates.

The `*_logic.py` helpers open with a working copy of the save so that a failed
action can be discarded.  Several of them used to deep-copy the whole save for
that, which costs about 2 ms per call.  A shallow `dict(player_data)` is only
correct while the function never writes *through* a nested value it did not
rebuild itself, and the existing suites cannot detect a violation: they do
``player, ok, result = apply_X(player)``, which overwrites the evidence.

Rather than hand-write a reachable fixture for every mutator, this gate wraps
the functions under test and then replays the module's own existing test file.
Those tests already drive the real mutation paths, so the wrapper sees the
calls that matter.  After every wrapped call it compares the mapping arguments
against a snapshot taken before the call; any difference is a live-save leak.

Two properties make this a check rather than a restatement of the change:

* it must pass against the deep-copying code as well, and
* it asserts each wrapped function was actually called, so a gate cannot pass
  by never reaching the code it guards.

What this gate does and does not guarantee.  It proves **no observable mutation
during the call**, for the paths the replayed suite actually drives.  It cannot
see a write that stores a value equal to the one already there, because it
detects leaks by comparing the mapping for inequality — such a write is real
write-through that happens to be invisible on this data, and would corrupt the
save on different data.  `test_write_through_probe.py` closes that hole for the
highest-consequence helpers by passing in containers that refuse mutation
outright, so any write-through raises regardless of the value written.
"""

from __future__ import annotations

import copy
import io
import sys
import unittest
from collections.abc import Mapping
from typing import Any, Callable, Iterable, Sequence


class _Recorder:
    def __init__(self) -> None:
        self.violations: list[str] = []
        self.calls: dict[str, int] = {}


def _wrap(name: str, func: Callable[..., Any], recorder: _Recorder) -> Callable[..., Any]:
    def guarded(*args: Any, **kwargs: Any) -> Any:
        # Keyword mappings are snapshotted too. Several helpers take the save as
        # `player_data=`, and watching positional arguments alone let those calls
        # satisfy the non-vacuity assert while going completely unchecked.
        snapshots = [
            (f"argument {index}", arg, copy.deepcopy(arg))
            for index, arg in enumerate(args)
            if isinstance(arg, Mapping)
        ]
        snapshots += [
            (f"keyword {key!r}", value, copy.deepcopy(value))
            for key, value in kwargs.items()
            if isinstance(value, Mapping)
        ]
        recorder.calls[name] = recorder.calls.get(name, 0) + 1
        result = func(*args, **kwargs)
        for label, arg, before in snapshots:
            if arg != before:
                recorder.violations.append(f"{name} mutated the mapping passed as {label}")
        return result

    guarded.__name__ = getattr(func, "__name__", name)
    guarded.__wrapped__ = func  # type: ignore[attr-defined]
    return guarded


def _rebind(original: Any, replacement: Any) -> None:
    """Swap every module-level reference to `original`, by identity.

    The suites import these helpers by name (``from x_logic import apply_x``),
    so patching the defining module alone would miss the copy the test file
    already holds.
    """
    for module in list(sys.modules.values()):
        namespace = getattr(module, "__dict__", None)
        if not isinstance(namespace, dict):
            continue
        for key, value in list(namespace.items()):
            if value is original:
                namespace[key] = replacement


def replay_module_suite(
    test_case: unittest.TestCase,
    logic_module: Any,
    function_names: Sequence[str],
    suite_names: Iterable[str],
    extra_calls: Iterable[Callable[[], Any]] = (),
) -> None:
    """Run `suite_names` with `function_names` guarded against input mutation."""
    recorder = _Recorder()
    wrappers: list[tuple[Any, Any]] = []
    for name in function_names:
        original = getattr(logic_module, name)
        wrapper = _wrap(name, original, recorder)
        wrappers.append((original, wrapper))
        _rebind(original, wrapper)
    try:
        for extra_call in extra_calls:
            extra_call()
        loader = unittest.TestLoader()
        suite = unittest.TestSuite(
            loader.loadTestsFromName(suite_name) for suite_name in suite_names
        )
        result = unittest.TextTestRunner(
            stream=io.StringIO(), verbosity=0
        ).run(suite)
    finally:
        for original, wrapper in wrappers:
            _rebind(wrapper, original)

    test_case.assertTrue(
        result.wasSuccessful(),
        "the replayed suite must pass under the gate; failures: "
        + "; ".join(str(failure[0]) for failure in result.failures + result.errors),
    )
    test_case.assertEqual(
        sorted(set(recorder.violations)),
        [],
        "a guarded helper wrote through a nested value of the save it was given",
    )
    never_called = [name for name in function_names if not recorder.calls.get(name)]
    test_case.assertEqual(
        never_called,
        [],
        "the replayed suite never called these guarded helpers, so the gate "
        "would pass vacuously",
    )


def assert_direct_calls(
    test_case: unittest.TestCase,
    cases: Iterable[tuple[str, Callable[[], dict], Callable[[dict], Any], Sequence[str]]],
) -> None:
    """Cover entry points the module's own suite never reaches.

    Each case must land on its success path, otherwise it would only prove that
    a refusal leaves the save alone.
    """
    for label, make_player, call, owned_keys in cases:
        with test_case.subTest(function=label):
            player = make_player()
            baseline = copy.deepcopy(player)
            returned = call(player)
            test_case.assertEqual(
                player, baseline, f"{label} mutated the save it was given"
            )
            if isinstance(returned, tuple) and len(returned) >= 2:
                test_case.assertTrue(
                    returned[1],
                    f"{label} refused the action, so the gate proves nothing",
                )
            assert_owned_keys_are_fresh(test_case, label, player, returned, owned_keys)


def assert_owned_keys_are_fresh(
    test_case: unittest.TestCase,
    label: str,
    player: Mapping[str, Any],
    result: Any,
    owned_keys: Sequence[str],
) -> None:
    """Each key the helper rewrites must come back as a distinct object."""
    if isinstance(result, tuple):
        result = result[0]
    test_case.assertIsInstance(result, dict, f"{label} returned no save mapping")
    for key in owned_keys:
        if not isinstance(player.get(key), (dict, list)):
            continue
        test_case.assertIsNot(
            result[key],
            player[key],
            f"{label} returned the caller's own {key!r} object, so a later "
            "write would reach the live save",
        )
