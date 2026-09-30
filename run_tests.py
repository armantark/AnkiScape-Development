import argparse
import difflib
import json
import os
import sys
import unittest
from collections import Counter
from collections.abc import Iterable


def iter_tests(suite: unittest.TestSuite) -> Iterable[unittest.TestCase]:
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from iter_tests(test)
        else:
            yield test


def select_tests(
    suite: unittest.TestSuite,
    selectors: list[str],
) -> tuple[unittest.TestSuite, list[str]]:
    tests = list(iter_tests(suite))
    if not selectors:
        return unittest.TestSuite(tests), [test.id() for test in tests]

    test_ids = [test.id() for test in tests]
    chosen = {test_id for selector in selectors for test_id in matching_ids(selector, test_ids)}
    selected = [test for test in tests if test.id() in chosen]
    return unittest.TestSuite(selected), [test.id() for test in selected]


def matching_ids(selector: str, test_ids: list[str]) -> list[str]:
    # Whole dotted names win, so `test_x` cannot also select a sibling module
    # such as `test_x_ui`; a bare fragment still works when no name equals it.
    wanted = f".{selector.casefold().strip('.')}."
    whole = [test_id for test_id in test_ids if wanted in f".{test_id.casefold()}."]
    return whole or [test_id for test_id in test_ids if selector.casefold() in test_id.casefold()]


def selector_suggestions(selector: str, test_ids: list[str]) -> list[str]:
    candidates = sorted({
        component
        for test_id in test_ids
        for component in (test_id, *test_id.split("."))
    })
    return difflib.get_close_matches(selector, candidates, n=5, cutoff=0.45)


def resolve_selectors(selectors: list[str], test_ids: list[str]) -> tuple[list[str], list[str]]:
    resolved: list[str] = []
    unresolved: list[str] = []
    components = {
        component
        for test_id in test_ids
        for component in test_id.split(".")
    }
    component_names = {component.casefold(): component for component in components}
    for selector in selectors:
        if matching_ids(selector, test_ids):
            resolved.append(selector)
            continue
        normalized_path = selector.replace("\\", "/")
        if normalized_path.casefold().endswith(".py"):
            module_name = normalized_path.rsplit("/", 1)[-1][:-3]
            if component := component_names.get(module_name.casefold()):
                resolved.append(f"{component}.")
                continue
        unresolved.append(selector)
    return resolved, unresolved


def report_refusals(test_ids: list[str], unresolved: list[str]) -> bool:
    duplicates = sorted(test_id for test_id, count in Counter(test_ids).items() if count > 1)
    if duplicates:
        print(f"Discovered {len(duplicates)} unittest IDs more than once:", file=sys.stderr)
        for test_id in duplicates:
            print(f"  {test_id}", file=sys.stderr)
    if unresolved:
        print(f"No unambiguous unittest ID matched: {', '.join(unresolved)}", file=sys.stderr)
        for selector in unresolved:
            suggestions = selector_suggestions(selector, test_ids)
            if suggestions:
                print(f"Closest matches for {selector!r}: {', '.join(suggestions)}", file=sys.stderr)
    return bool(duplicates or unresolved)


def test_result_exit_code(result: unittest.TestResult, *, focused: bool) -> int:
    if not result.wasSuccessful():
        return 1
    if focused and result.testsRun > 0 and len(result.skipped) == result.testsRun:
        return 2
    return 0


def print_count_inventory(suite: unittest.TestSuite, count: int) -> None:
    print(f"Matching tests: {count}", flush=True)
    for test in iter_tests(suite):
        method = getattr(test, test._testMethodName)
        skipped = type(test) if getattr(type(test), "__unittest_skip__", False) else method
        if getattr(skipped, "__unittest_skip__", False):
            print(f"Static skip: {test.id()}: {skipped.__unittest_skip_why__}", file=sys.stderr)
    print(
        "Runtime skips: unknown until tests run; metadata applies to this interpreter only.",
        file=sys.stderr,
    )


def write_skip_report(result: unittest.TestResult) -> None:
    skip_report = os.environ.get("ANKISCAPE_TEST_SKIP_REPORT")
    if not skip_report:
        return
    # Optional diagnostics must not change the unittest result or stdout contracts.
    try:
        with open(skip_report, "w", encoding="utf-8") as report:
            json.dump([(test.id(), reason) for test, reason in result.skipped], report)
    except Exception as exc:
        print(f"warning: skipped-test report could not be written: {exc}", file=sys.stderr)


def main() -> int:
    root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root)

    parser = argparse.ArgumentParser(
        description="Discover AnkiScape tests and select them by verified test-id fragments.",
    )
    parser.add_argument(
        "selectors",
        nargs="*",
        help=(
            "case-insensitive dotted names matched as whole segments of discovered "
            "unittest IDs, or as fragments when no whole segment matches"
        ),
    )
    inventory = parser.add_mutually_exclusive_group()
    inventory.add_argument(
        "--count",
        action="store_true",
        help=(
            "print only 'Matching tests: N' to stdout without running tests or applying "
            "the ID cap; report class/method skip metadata for this interpreter to stderr; "
            "runtime skips remain unknown"
        ),
    )
    inventory.add_argument(
        "--list",
        action="store_true",
        help=(
            "list matching test IDs without running them, then a last 'Matching tests: N' "
            "line; N counts every discovered match, skipped ones too, so on the same tree "
            "it equals the Ran count that run_remote_tests.py --expected-tests checks for "
            "the same selectors, and that run passes only when none of the N skip in its lane"
        ),
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=200,
        help="maximum IDs printed by --list (default: 200)",
    )
    parser.add_argument(
        "--verbosity",
        type=int,
        choices=(0, 1, 2),
        default=1,
        help="unittest output verbosity (default: 1; use 2 for focused diagnosis)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="print only failures and the final unittest summary",
    )
    parser.add_argument("--failfast", action="store_true")
    args = parser.parse_args()

    if args.max_results < 1:
        parser.error("--max-results must be at least 1")

    # Ensure project root is importable for tests
    if root not in sys.path:
        sys.path.insert(0, root)

    from tests import install_offscreen_modal_guard

    install_offscreen_modal_guard()

    try:
        from aqt.qt import QFont
    except ImportError:
        pass
    else:
        QFont.insertSubstitution("Sans Serif", "Arial")

    # Discover and run tests under tests/
    loader = unittest.TestLoader()
    # Rooting discovery at the checkout gives each module one `tests.` name; a
    # module imported under a second name would otherwise run its tests twice.
    # A TestCase class imported into another test module is collected there
    # again under the same ID, which the duplicate check refuses.
    suite = loader.discover(start_dir=os.path.join(root, "tests"), pattern="test_*.py", top_level_dir=root)
    all_ids = [test.id() for test in iter_tests(suite)]
    selectors, unresolved = resolve_selectors(args.selectors, all_ids)
    if report_refusals(all_ids, unresolved):
        return 2
    suite, selected_ids = select_tests(suite, selectors)

    if args.selectors and not selected_ids:
        print(f"No discovered unittest ID matched: {', '.join(args.selectors)}", file=sys.stderr)
        return 2

    if args.count:
        print_count_inventory(suite, len(selected_ids))
        return 0

    if args.list:
        for test_id in selected_ids[:args.max_results]:
            print(test_id)
        # The count goes to stderr so stdout stays a clean ID list; flushing keeps it last in merged output.
        sys.stdout.flush()
        unprinted = len(selected_ids) - args.max_results
        if unprinted > 0:
            print(
                f"Matching tests: {len(selected_ids)}. Refusing to print the last {unprinted}; "
                f"narrow the selector or pass --max-results {len(selected_ids)}.",
                file=sys.stderr,
            )
            return 2
        print(f"Matching tests: {len(selected_ids)}", file=sys.stderr)
        return 0

    verbosity = 0 if args.quiet else args.verbosity
    runner = unittest.TextTestRunner(verbosity=verbosity, failfast=args.failfast)
    result = runner.run(suite)
    write_skip_report(result)
    returncode = test_result_exit_code(result, focused=bool(args.selectors))
    if returncode == 2:
        print(
            "All selected tests were skipped. Use .venv-qt/bin/python with "
            "QT_QPA_PLATFORM=offscreen for Qt tests.",
            file=sys.stderr,
        )
    return returncode


if __name__ == "__main__":
    raise SystemExit(main())
