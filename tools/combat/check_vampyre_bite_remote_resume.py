"""Check exact-run resumption with inert fakes; never import the real runner."""

import argparse
import base64
import copy
import gzip
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch


def expect_error(action, error_type, message):
    try:
        action()
    except error_type as error:
        assert str(error) == message
    else:
        raise AssertionError('expected refusal did not occur')


def make_remote(root, pending, events):
    pending_path = root / 'pending.json'

    def ssh(command, *, label, repeat_safe=False):
        events.append(['ssh', label, command, repeat_safe])
        if label == 'remote lane launch':
            return ''
        if label == 'vampyre bite exact-run final log':
            assert command == 'cat /inert/first.log'
            return 'Inert failed-job output; no test results were fabricated.\n'
        if label == 'vampyre bite exact-run report':
            assert command == 'cat /inert/first.report'
            return '23\n'
        raise AssertionError(f'unexpected fake SSH operation: {label}')

    def stream(lane, *, timeout, poll_interval):
        events.append(['launch', lane, timeout, poll_interval])
        pending_path.write_text(json.dumps(pending))
        remote._ssh('INERT LAUNCH ONLY', label='remote lane launch')
        raise TimeoutError('inert observation timeout after launch')

    def completion(path):
        events.append(['observe', path])
        assert path == pending['report_path']
        return 23

    remote = SimpleNamespace(
        REMOTE_ROOT=Path('/inert'), REMOTE_REPO=Path('/inert/repo'),
        REMOTE_GAME_MAIN=Path('/inert/game'), REMOTE_DARKAN=Path('/inert/darkan'),
        REMOTE_PLAIN_SITE=Path('/inert/plain'), REMOTE_VENV=Path('/inert/qt'),
        _sync=lambda path: events.append(['sync', str(path)]),
        _preflight=lambda lane: events.append(['preflight', lane]),
        _pending_path=lambda: pending_path, _ssh=ssh, _stream_remote_run=stream,
        _completion_report=completion, _remote_lane_command=lambda lane: lane,
    )
    return remote


def refuse_foreign(driver, args, remote, events, pending):
    foreign = dict(pending, run_id='inert-unrelated-run')
    remote._pending_path().write_text(json.dumps(foreign))
    count = len(events)
    expect_error(lambda: driver.run_jobs(args, remote, {}), RuntimeError,
                 'another or unknown remote run owns the mirror pending record')
    assert len(events) == count
    assert json.loads(remote._pending_path().read_text()) == foreign


def resume_canary(driver, root):
    output = root / 'output'
    output.mkdir()
    pending = {'run_id': 'inert-first-run', 'log_path': '/inert/first.log',
               'report_path': '/inert/first.report'}
    events = []
    remote = make_remote(root, pending, events)
    args = SimpleNamespace(root=root, output=output, timeout=1)

    def fake_guard(_remote, lane, remote_output, destination, sources):
        events.append(['fake-source-guard', lane, str(remote_output), destination.name, sources])
        destination.write_text(json.dumps(events[-1]))
        destination.with_suffix('.raw.json').write_text(json.dumps(events[-1]))

    with patch.object(driver, 'local_sources', return_value={}), \
         patch.object(driver, 'capture_guard', side_effect=fake_guard):
        expect_error(lambda: driver.run_jobs(args, remote, {}), TimeoutError,
                     'inert observation timeout after launch')
        state = json.loads((output / 'state.json').read_text())
        assert state['current']['pending'] == pending
        assert state['completed'] == []
        first_events = list(events)
        before = {path.name: path.read_bytes() for path in output.glob('plain-focused-before*.json')}
        expect_error(lambda: driver.run_jobs(args, remote, {}), RuntimeError,
                     'plain-focused failed with exit 23; retained exact run must not relaunch')
        assert sum(event[0] == 'launch' for event in events) == 1
        assert sum(event[0] == 'sync' for event in events) == 1
        assert ['observe', pending['report_path']] in events
        assert json.loads((output / 'state.json').read_text())['current']['pending'] == pending
        assert json.loads(remote._pending_path().read_text()) == pending
        assert json.loads((output / 'plain-focused-completion.json').read_text())['exit_code'] == 23
        assert (output / 'plain-focused.log').read_text().startswith('Inert failed-job output;')
        assert (output / 'plain-focused.report').read_text() == '23\n'
        assert all((output / name).read_bytes() == raw for name, raw in before.items())
        assert len(list(output.glob('plain-focused-resume-before-*.json'))) == 2
        resume_events = events[len(first_events):]
        refuse_foreign(driver, args, remote, events, pending)
        fresh = root / 'fresh-output'
        fresh.mkdir()
        refuse_foreign(driver, SimpleNamespace(root=root, output=fresh, timeout=1), remote, events, pending)
        assert not (fresh / 'state.json').exists()
    return {'inert_only': True, 'real_remote_calls': False, 'product_imports': False,
            'launch_timeout_retained_identity': pending, 'first_events': first_events,
            'resume_events': resume_events, 'resume_launches': 0, 'resume_syncs': 0,
            'resumed_failed_exit': 23, 'initial_before_evidence_unchanged': True,
            'existing_and_fresh_foreign_pending_refused': True}


def guard_error_canary(driver, root):
    class InertSSHError(RuntimeError):
        pass

    message = "inert source guard failed: stdout=''; stderr='inventory mismatch before imports'"
    remote = make_remote(root, {}, [])
    remote.SSHCommandError = InertSSHError
    destination = root / 'guard.json'
    with patch.object(remote, '_ssh', side_effect=InertSSHError(message)):
        expect_error(lambda: driver.capture_guard(remote, 'plain', '/inert/guard.json', destination, {}),
                     InertSSHError, message)
    assert destination.with_suffix('.error.txt').read_text() == message
    assert not destination.exists()
    return {'error_retained_verbatim': message}


def acceptance_canary(driver):
    payload = base64.b64encode(b'INERT BYTES, NOT A GAME RESULT OR PICKLE').decode()
    rows = [{'case': label, 'equal': True, 'rng_calls': 1, 'route_pass': True,
             'expected': {'inert_route': True}, 'observed': {'inert_route': True},
             'baseline_pickle_base64': payload, 'candidate_pickle_base64': payload}
            for label in driver.CASES]
    driver.validate_cases(rows)
    swapped = copy.deepcopy(rows)
    swapped[0], swapped[1] = swapped[1], swapped[0]
    expect_error(lambda: driver.validate_cases(swapped), ValueError,
                 'comparison must contain exactly the sixteen named cases in order')
    unequal = copy.deepcopy(rows)
    unequal[0]['candidate_pickle_base64'] = base64.b64encode(b'OTHER INERT BYTES').decode()
    expect_error(lambda: driver.validate_cases(unequal), ValueError,
                 'complete output and RNG payload differs or has no draws')
    no_draws = copy.deepcopy(rows)
    no_draws[0]['rng_calls'] = 0
    expect_error(lambda: driver.validate_cases(no_draws), ValueError,
                 'complete output and RNG payload differs or has no draws')
    wrong_route = copy.deepcopy(rows)
    wrong_route[0]['observed']['inert_route'] = False
    expect_error(lambda: driver.validate_cases(wrong_route), ValueError,
                 'advertised comparison route was not exercised')
    return {'inert_only': True, 'game_or_test_execution': False,
            'synthetic_rows_accepted': len(rows), 'swapped_order_refused': True,
            'unequal_payload_refused': True, 'zero_rng_calls_refused': True,
            'route_observation_mismatch_refused': True}


def compressed_comparison_canary(driver, root):
    remote = make_remote(root, {}, [])
    destination = root / 'comparison.json.gz'
    report = {'status': 'PASS', 'baseline_commit': driver.BASELINE_COMMIT,
              'baseline_sha256': driver.BASELINE, 'inventory_sha256': driver.PIN,
              'sources_before': {}, 'sources_after': {}, 'cases': []}
    raw = gzip.compress(json.dumps(report).encode(), mtime=0)
    with patch.object(remote, '_ssh', return_value=base64.b64encode(raw).decode()), \
         patch.object(driver, 'validate_cases') as validate:
        driver.retain_comparison(remote, 'plain', '/inert/result.json.gz', destination, {})
        validate.assert_called_once_with([])
    assert destination.read_bytes() == raw
    report['inventory_sha256'] = 'inert-wrong-binding'
    invalid = gzip.compress(json.dumps(report).encode(), mtime=0)
    with patch.object(remote, '_ssh', return_value=base64.b64encode(invalid).decode()):
        expect_error(lambda: driver.retain_comparison(remote, 'plain', '/inert/result.json.gz', destination, {}),
                     ValueError, 'comparison source binding or status differs')
    assert destination.read_bytes() == invalid
    return {'inert_only': True, 'gzip_decoded': True, 'exact_bytes_retained': True,
            'wrong_inventory_refused_with_raw_retained': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if sys.flags.optimize or 'PYTHONOPTIMIZE' in os.environ:
        raise SystemExit('optimized interpreter refused')

    def forbid_product(event, values):
        if event == 'import' and (values[0].startswith(('ankiscape', 'pkg_alias', 'tests'))
                                  or values[0] == 'tools.run_remote_tests'):
            raise RuntimeError('inert canary attempted a product or real-runner import')

    sys.addaudithook(forbid_product)
    path = Path(__file__).with_name('run_vampyre_bite_remote.py')
    spec = importlib.util.spec_from_file_location('inert_vampyre_bite_driver', path)
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    with tempfile.TemporaryDirectory(prefix='vampyre-bite-resume-canary-') as temporary:
        root = Path(temporary)
        report = resume_canary(driver, root)
        report['source_guard_error'] = guard_error_canary(driver, root)
        report['acceptance_stops'] = acceptance_canary(driver)
        report['compressed_comparison'] = compressed_comparison_canary(driver, root)
    args.output.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
