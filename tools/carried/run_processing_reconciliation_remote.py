"""Run the pinned carried proofs on the existing mirror, retaining resumable evidence."""

import argparse
import base64
import fcntl
import gzip
import hashlib
import json
import os
from pathlib import Path
import shlex
import sys
import time
import uuid
from unittest.mock import patch

EVIDENCE = Path('memory-bank/evidence/carried-processing-reconciliation-2026-09-07')
MANIFEST = EVIDENCE / 'final-source-manifest.json.gz'
PIN = 'c2d0e39132fb5d8b9081a21caf0ffa69e4f2ec88cb3141402bed70f4a0c6203f'
SELECTORS = [
    'tests.runtime_actions.test_carried_processing_reconciliation',
    'tests.test_runtime_actions.TestProcessingPackOverlay',
    'tests.test_runtime_actions.TestCarriedOverlayWrapper',
] + ['tests.test_runtime_actions.TestRuntimeActions.' + name for name in (
    'test_fletching_handler_and_carried_overlay_consume_selected_coloured_feathers',
    'test_crafting_handler_and_carried_overlay_reconcile_thread_consumption',
    'test_crafting_carried_overlay_requires_and_retains_mould',
    'test_cannonball_advanced_pack_carries_and_retains_ammo_mould',
    'test_unfired_clay_ring_carried_overlay_reconciles_and_retains_mould',
    'test_crafting_carried_overlay_retains_one_thread_across_leather_actions',
    'test_crafting_advanced_layout_refills_consumed_thread_from_bank_before_resuming',
)]
CASES = [f'{name}-replace-{replaced}' for replaced in (False, True) for name in (
    'partial', 'rejected', 'none_return', 'zero_return', 'dry', 'output_over_input'
)] + ['rejection-winter-True-child-cadence-False',
      'rejection-winter-False-child-cadence-True', 'real-firemaking-trip',
      'real-advanced-thread', 'real-advanced-mould', 'real-advanced-feathers']


def save(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def local_sources(root):
    raw = (root / MANIFEST).read_bytes()
    if hashlib.sha256(raw).hexdigest() != PIN:
        raise ValueError('final source manifest pin mismatch; no remote calls permitted')
    manifest = json.loads(gzip.decompress(raw))
    if len(manifest['files']) != 903:
        raise ValueError('expected exactly 903 pinned source files')
    for name, expected in manifest['files'].items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'local source mismatch: {name}')
    return manifest


def remote_prefix(remote, lane):
    environment = ['env', '-u', 'PYTHONOPTIMIZE', 'PATH=/opt/homebrew/bin:/usr/bin:/bin',
                   f'ANKISCAPE_GAME_MAIN={remote.REMOTE_GAME_MAIN}',
                   f'ANKISCAPE_DARKAN_WORLD_SERVER={remote.REMOTE_DARKAN}']
    if lane == 'plain':
        environment += [f'PYTHONPATH={remote.REMOTE_PLAIN_SITE}', '/opt/homebrew/bin/python3']
    else:
        environment += ['QT_QPA_PLATFORM=offscreen', str(remote.REMOTE_VENV / 'bin/python')]
    return shlex.join(environment + ['-B'])


def guard_command(remote, lane, output):
    return remote_prefix(remote, lane) + ' ' + shlex.join([
        'tools/carried/compare_processing_reconciliation.py', '--root', str(remote.REMOTE_REPO),
        '--manifest', str(remote.REMOTE_REPO / MANIFEST), '--manifest-sha256', PIN,
        '--output', str(output), '--guard-only'])


def capture_guard(remote, lane, output, destination, manifest):
    command = (f'cd {shlex.quote(str(remote.REMOTE_REPO))} && '
               + guard_command(remote, lane, output) + f' && cat {shlex.quote(str(output))}')
    try:
        raw = remote._ssh(command, label='carried source guard', repeat_safe=True)
    except remote.SSHCommandError as error:
        destination.with_suffix('.error.txt').write_text(str(error))
        raise
    destination.with_suffix('.raw.json').write_text(raw)
    if json.loads(raw) != {'guards_passed': True, 'product_imports': False}:
        raise ValueError('remote source guard did not report a pre-import success')
    save(destination, {'manifest_sha256': PIN, 'manifest': manifest, 'guard': json.loads(raw)})


def observe_existing(remote, pending, timeout):
    started = time.monotonic()
    while True:
        code = remote._completion_report(pending['report_path'])
        if code is not None:
            output = remote._ssh('cat ' + shlex.quote(pending['log_path']),
                                 label='carried exact-run final log', repeat_safe=True)
            return code, output
        if time.monotonic() - started >= timeout:
            raise TimeoutError(f"same remote run remains pending: {pending['run_id']}")
        time.sleep(5)


def run_jobs(args, remote, manifest):
    state_path = args.output / 'state.json'
    state = json.loads(state_path.read_text()) if state_path.exists() else None
    pending_path = remote._pending_path()
    if pending_path.exists():
        pending = json.loads(pending_path.read_text())
        if state is None or state['current'] is None or pending != state['current']['pending']:
            raise RuntimeError('another or unknown remote run owns the mirror pending record')
    if state is None:
        remote._sync(args.root)
        state = {'manifest_sha256': PIN, 'root': str(args.root), 'session': uuid.uuid4().hex,
                 'completed': [], 'current': None}
        save(state_path, state)
    if state['manifest_sha256'] != PIN or state['root'] != str(args.root):
        raise ValueError('saved run belongs to another source binding or root')
    for lane in ('plain', 'qt'):
        remote._preflight(lane)
        for kind in ('focused', 'comparison'):
            if f'{lane}-{kind}' not in state['completed']:
                run_job(args, remote, manifest, state, lane, kind)
    save(args.output / 'complete.json', {'jobs': state['completed'], 'manifest_sha256': PIN})


def launch_job(args, remote, state, lane, kind, job, stem, result_path):
    state_path = args.output / 'state.json'
    pending_path = remote._pending_path()
    original_ssh = remote._ssh
    command = remote_prefix(remote, lane) + ' '
    if kind == 'focused':
        command += shlex.join(['-m', 'unittest', *SELECTORS])
    else:
        command += shlex.join([
            'tools/carried/compare_processing_reconciliation.py', '--root', str(remote.REMOTE_REPO),
            '--manifest', str(remote.REMOTE_REPO / MANIFEST), '--manifest-sha256', PIN,
            '--output', result_path])
    command = guard_command(remote, lane, str(stem) + '-launch.json') + ' && ' + command

    def launch_ssh(text, *, label, repeat_safe=False):
        if label == 'remote lane launch':
            pending = json.loads(pending_path.read_text())
            state['current'] = {'job': job, 'pending': pending, 'result_path': result_path}
            save(state_path, state)
        return original_ssh(text, label=label, repeat_safe=repeat_safe)

    with patch.object(remote, '_remote_lane_command', return_value=command), \
         patch.object(remote, '_ssh', side_effect=launch_ssh):
        return remote._stream_remote_run(lane, timeout=args.timeout, poll_interval=5)


def validate_job_output(args, remote, manifest, lane, kind, job, raw, result_path):
    if kind == 'focused':
        summary = remote.parse_unittest_summary(raw)
        if summary.tests != 34 or summary.skipped != 0:
            raise ValueError(f'{job}: expected 34 tests and zero skips, got {summary}')
    else:
        reader = ('import base64,pathlib; print(base64.b64encode(pathlib.Path('
                  + repr(result_path) + ').read_bytes()).decode())')
        encoded = remote._ssh(remote_prefix(remote, lane) + ' -c ' + shlex.quote(reader),
                              label='carried comparison bytes', repeat_safe=True)
        packed = base64.b64decode(encoded.strip(), validate=True)
        (args.output / f'{job}.json.gz').write_bytes(packed)
        report = json.loads(gzip.decompress(packed))
        if (report['manifest_sha256'] != PIN or report['source_files'] != 903
                or report['baseline_commit'] != manifest['baseline_commit']):
            raise ValueError('comparison output source binding mismatch')
        rows = report['comparisons']
        if [row['case'] for row in rows] != CASES:
            raise ValueError('comparison must contain exactly the 18 named cases in order')
        if not all(row['equal'] is True and row['baseline'] == row['candidate'] for row in rows):
            raise ValueError('complete comparison payload differs')


def run_job(args, remote, manifest, state, lane, kind):
    state_path = args.output / 'state.json'
    pending_path = remote._pending_path()
    job = f'{lane}-{kind}'
    if state['current'] is not None and state['current']['job'] != job:
        raise ValueError('saved active job differs from the next required job')
    local_sources(args.root)
    stem = remote.REMOTE_ROOT / 'reports' / f"carried-{state['session']}-{job}"
    result_path = str(stem) + '.json.gz'
    guard_phase = 'before' if state['current'] is None else 'resume-before'
    capture_guard(remote, lane, f'{stem}-{guard_phase}.json',
                  args.output / f'{job}-{guard_phase}.json', manifest)
    if state['current'] is None:
        code, raw = launch_job(args, remote, state, lane, kind, job, stem, result_path)
    else:
        code, raw = observe_existing(remote, state['current']['pending'], args.timeout)
    (args.output / f'{job}.log').write_text(raw)
    save(args.output / f'{job}-completion.json', {'exit_code': code, 'run': state['current']})
    capture_guard(remote, lane, str(stem) + '-after.json',
                  args.output / f'{job}-after.json', manifest)
    local_sources(args.root)
    if code != 0:
        raise RuntimeError(f'{job} failed with exit {code}; retained exact run must not relaunch')
    validate_job_output(args, remote, manifest, lane, kind, job, raw, result_path)
    if pending_path.exists():
        if json.loads(pending_path.read_text()) != state['current']['pending']:
            raise RuntimeError('pending run identity changed; refusing to clear it')
        pending_path.unlink()
    state['completed'].append(job)
    state['current'] = None
    save(state_path, state)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--timeout', type=float, default=1800)
    parser.add_argument('--guard-only', action='store_true')
    args = parser.parse_args()
    if sys.flags.optimize or os.environ.get('PYTHONOPTIMIZE'):
        raise SystemExit('optimized interpreter refused; no remote calls permitted')
    if args.timeout <= 0:
        parser.error('--timeout must be positive')
    args.root = args.root.resolve()
    args.output = args.output.resolve()
    manifest = local_sources(args.root)
    args.output.mkdir(parents=True, exist_ok=True)
    if args.guard_only:
        save(args.output / 'local-guard.json', {'source_files': 903, 'manifest_sha256': PIN,
                                             'remote_calls': False, 'product_imports': False})
        return
    sys.path.insert(0, str(args.root))
    from tools import run_remote_tests as remote
    remote.LOCAL_MIRROR_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with remote.LOCAL_MIRROR_LOCK_PATH.open('a+') as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit(f'remote mirror busy: {remote.LOCAL_MIRROR_LOCK_PATH}')
        run_jobs(args, remote, manifest)


if __name__ == '__main__':
    main()
