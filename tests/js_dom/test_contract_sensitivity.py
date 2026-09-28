"""Keep the injection contracts sensitive to execution, not source spelling."""

from contextlib import ExitStack
import unittest
from unittest.mock import patch

from tests import test_js_bridge_contract as bridge
from tests import test_js_injection_contract_extra as extra
from tests.js_dom.fixture import HAS_AQT


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class TestJsContractSensitivity(unittest.TestCase):
    def test_behavior_contracts_reject_commented_out_scripts(self):
        for module, case in ((bridge, bridge.TestJsBridgeContract),
                             (extra, extra.TestJSInjectionContractExtra)):
            for name in unittest.defaultTestLoader.getTestCaseNames(case):
                with self.subTest(contract=name), ExitStack() as stack:
                    for builder in ("build_reviewer_js", "build_overview_js", "build_deck_browser_js"):
                        stack.enter_context(patch.object(module, builder, _commented(getattr(module, builder))))
                    result = unittest.TestResult()
                    unittest.TestSuite([case(name)]).run(result)
                    self.assertTrue(result.failures, f"{name} accepted inert JavaScript: {result}")
                    self.assertEqual(result.errors, [])
                    self.assertEqual(result.skipped, [])

    def test_reviewer_contract_accepts_equivalent_element_removal(self):
        def remove_element(*_args):
            return "document.getElementById('ankiscape-float')?.remove();"

        for module, case in ((bridge, bridge.TestJsBridgeContract),
                             (extra, extra.TestJSInjectionContractExtra)):
            with self.subTest(module=module.__name__):
                with patch.object(module, "build_reviewer_js", remove_element):
                    suite = unittest.TestSuite(
                        case(name) for name in unittest.defaultTestLoader.getTestCaseNames(case)
                        if name.startswith("test_reviewer")
                    )
                    result = unittest.TestResult()
                    suite.run(result)
                self.assertEqual(result.failures, [])
                self.assertEqual(result.errors, [])
                self.assertEqual(result.skipped, [])
                self.assertGreater(result.testsRun, 0)


def _commented(builder):
    def build(*args):
        return "\n".join("// " + line for line in builder(*args).splitlines())

    return build
