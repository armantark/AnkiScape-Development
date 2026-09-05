"""Coverage evidence must distinguish callable bodies under Python's real tracer."""

import ast
import sys
import types
import unittest

from tools.dispatcher.state_coverage import StateAccesses


class DispatcherStateCoverageTest(unittest.TestCase):
    def test_decorated_duplicate_names_and_deferred_comprehensions_stay_distinct(self):
        source = '''def decorate(function):
    return function

def choose(first):
    if first:
        @decorate
        def action():
            return _state.value
    else:
        @decorate
        def action():
            return (_state.value for _ in range(1))
    return action

read = lambda: _state.value
'''
        survey = StateAccesses()
        survey.visit(ast.parse(source))
        namespace = {"_state": types.SimpleNamespace(value=23)}
        filename = "dispatcher-coverage-fixture.py"
        exec(compile(source, filename, "exec"), namespace)
        observed = set()

        def trace(frame, event, _arg):
            if frame.f_code.co_filename != filename:
                return None
            if event == "line" and frame.f_lineno in survey.line_names:
                observed.add(survey.frame_name(frame))
            return trace

        previous_trace = sys.gettrace()
        try:
            sys.settrace(trace)
            self.assertEqual(namespace["choose"](True)(), 23)
            deferred = namespace["choose"](False)()
            self.assertEqual(list(deferred), [23])
            self.assertEqual(namespace["read"](), 23)
        finally:
            sys.settrace(previous_trace)

        self.assertEqual(len(survey.functions), 3)
        self.assertEqual(observed, set(survey.functions))
        self.assertNotIn(None, observed)
