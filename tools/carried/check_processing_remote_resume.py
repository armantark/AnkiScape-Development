"""Canary the remote driver's resumption using only inert fakes and temporary files."""

import argparse
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if sys.flags.optimize:
        raise SystemExit('optimized interpreter refused')
    driver_path = Path(__file__).with_name('run_processing_reconciliation_remote.py')
    spec = importlib.util.spec_from_file_location('inert_carried_driver', driver_path)
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    with tempfile.TemporaryDirectory(prefix='carried-resume-canary-') as temporary:
        root = Path(temporary)
        output = root / 'output'
        output.mkdir()
        pending_path = root / 'pending.json'
        pending = {'run_id': 'inert-first-run', 'log_path': '/inert/first.log',
                   'report_path': '/inert/first.report'}
        events = []

        def ssh(command, *, label, repeat_safe=False):
            events.append(['ssh', label, command])
            if label == 'remote lane launch':
                return ''
            if label == 'carried exact-run final log':
                if command != 'cat /inert/first.log':
                    raise AssertionError('resumption read a different log')
                return 'Inert failed-job output; no test results were fabricated.\n'
            raise AssertionError(f'unexpected fake SSH operation: {label}')

        def stream(lane, *, timeout, **_options):
            events.append(['launch', lane])
            pending_path.write_text(json.dumps(pending))
            remote._ssh('INERT LAUNCH ONLY', label='remote lane launch')
            raise TimeoutError('inert observation timeout after launch')

        def completion(path):
            events.append(['observe', path])
            if path != pending['report_path']:
                raise AssertionError('resumption observed a different report')
            return 23

        remote = SimpleNamespace(
            REMOTE_ROOT=Path('/inert'), REMOTE_REPO=Path('/inert/repo'),
            REMOTE_GAME_MAIN=Path('/inert/game'), REMOTE_DARKAN=Path('/inert/darkan'),
            REMOTE_PLAIN_SITE=Path('/inert/plain'), REMOTE_VENV=Path('/inert/qt'),
            _sync=lambda path: events.append(['sync', str(path)]),
            _preflight=lambda lane: events.append(['preflight', lane]),
            _pending_path=lambda: pending_path, _ssh=ssh, _stream_remote_run=stream,
            _completion_report=completion, _remote_lane_command=lambda lane: '',
        )

        def fake_guard(_remote_arg, lane, remote_output, destination, manifest):
            events.append(['fake-source-guard', str(remote_output), destination.name])
            destination.write_text(json.dumps(events[-1]))
            destination.with_suffix('.raw.json').write_text(json.dumps(events[-1]))

        run_args = SimpleNamespace(root=root, output=output, timeout=1)
        with patch.object(driver, 'local_sources', return_value={}), \
             patch.object(driver, 'capture_guard', side_effect=fake_guard):
            try:
                driver.run_jobs(run_args, remote, {})
            except TimeoutError as error:
                if str(error) != 'inert observation timeout after launch':
                    raise
            else:
                raise AssertionError('launch did not surface the observation timeout')
            first_state = json.loads((output / 'state.json').read_text())
            assert first_state['current']['pending'] == pending
            assert json.loads(pending_path.read_text()) == pending
            assert first_state['completed'] == []
            first_events = list(events)
            initial_guard = (output / 'plain-focused-before.json').read_bytes()
            initial_raw = (output / 'plain-focused-before.raw.json').read_bytes()
            try:
                driver.run_jobs(run_args, remote, {})
            except RuntimeError as error:
                assert str(error) == 'plain-focused failed with exit 23; retained exact run must not relaunch'
            else:
                raise AssertionError('inert failed run was accepted')
            assert sum(event[0] == 'launch' for event in events) == 1
            assert sum(event[0] == 'sync' for event in events) == 1
            assert ['observe', pending['report_path']] in events
            assert json.loads((output / 'state.json').read_text())['current']['pending'] == pending
            assert (output / 'plain-focused.log').read_text().startswith('Inert failed-job output;')
            assert json.loads((output / 'plain-focused-completion.json').read_text())['exit_code'] == 23
            resume_events = events[len(first_events):]
            assert (output / 'plain-focused-before.json').read_bytes() == initial_guard
            assert (output / 'plain-focused-before.raw.json').read_bytes() == initial_raw
            assert (output / 'plain-focused-resume-before.json').exists()
            assert (output / 'plain-focused-resume-before.raw.json').exists()
            unrelated = dict(pending, run_id='inert-unrelated-run')
            pending_path.write_text(json.dumps(unrelated))
            event_count = len(events)
            try:
                driver.run_jobs(run_args, remote, {})
            except RuntimeError as error:
                assert str(error) == 'another or unknown remote run owns the mirror pending record'
            else:
                raise AssertionError('unrelated pending run was accepted')
            assert len(events) == event_count
            assert json.loads(pending_path.read_text()) == unrelated
            unrelated_refused = len(events) == event_count
            fresh_output = root / 'fresh-output'
            fresh_output.mkdir()
            fresh_args = SimpleNamespace(root=root, output=fresh_output, timeout=1)
            fresh_event_count = len(events)
            try:
                driver.run_jobs(fresh_args, remote, {})
            except RuntimeError as error:
                assert str(error) == 'another or unknown remote run owns the mirror pending record'
            else:
                raise AssertionError('fresh run accepted an unrelated pending record')
            assert len(events) == fresh_event_count
            assert not (fresh_output / 'state.json').exists()
            assert json.loads(pending_path.read_text()) == unrelated
            report = {'inert_only': True, 'product_imports': False, 'real_remote_calls': False,
                      'launch_timeout_retained_identity': pending, 'first_events': first_events,
                      'resume_events': resume_events, 'resume_launches': 0, 'resume_syncs': 0,
                      'resumed_failed_exit': 23, 'unrelated_pending_refused_before_operations': unrelated_refused,
                      'fresh_foreign_pending_refused_before_operations': len(events) == fresh_event_count,
                      'initial_before_evidence_unchanged': (
                          (output / 'plain-focused-before.json').read_bytes() == initial_guard
                          and (output / 'plain-focused-before.raw.json').read_bytes() == initial_raw)}
    args.output.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
