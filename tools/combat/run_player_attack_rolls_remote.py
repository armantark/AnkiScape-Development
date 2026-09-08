"""Run the pinned player-roll proofs with retained, resumable mirror ownership."""

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

EVIDENCE = Path('memory-bank/evidence/combat-player-attack-rolls-2026-09-07')
INVENTORY = EVIDENCE / 'source-inventory.json.gz'
PIN = '976d29addd0a0e68659e27c23f2f3019f0a2ea2d63435fe3daf6311ddc939308'
BASELINE = '486a532d00d4e5693894b77a022ef83a32e03f55e841c2ff92ab12fc7e9ad2d4'
CANDIDATE = '2b5a8a808f688cb179e59f882e58abefb1cb008d00cbca42e771d393d1c10ba8'
SELECTORS = ['CombatPlayerAttackRollsTest'] + ['CombatLogicTest.' + name for name in (
    'test_cockatrice_drains_reduce_later_attacks_in_the_same_review',
    'test_basilisk_prayer_blocks_unshielded_damage_but_not_random_stat_drain',
    'test_aberrant_spectre_prayer_blocks_drain_but_not_stench_damage',
)]
CASES = [label for kind in ('melee', 'ranged', 'magic') for label in (
    f'initial:{kind}', f'drain:{kind}:live=False', f'drain:{kind}:live=True',
)] + ['rng-seeded:melee', 'spectre:blocked=False', 'spectre:blocked=True',
      'basilisk:prayer-still-drains', 'ranged-prayer:eagle_eye', 'ranged-prayer:rigour',
      'charge:False', 'charge:True', 'charge:after-drain', 'guild:single', 'guild:multi']


def save(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def local_sources(root):
    raw = (root / INVENTORY).read_bytes()
    if hashlib.sha256(raw).hexdigest() != PIN:
        raise ValueError('source inventory pin mismatch; no remote calls permitted')
    sources = json.loads(gzip.decompress(raw))
    if len(sources) != 877:
        raise ValueError('expected exactly 877 pinned source files')
    for name, expected in sources.items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'local source mismatch: {name}')
    return sources


def remote_prefix(remote, lane):
    environment = ['env', '-u', 'PYTHONOPTIMIZE', 'PATH=/opt/homebrew/bin:/usr/bin:/bin',
                   f'ANKISCAPE_GAME_MAIN={remote.REMOTE_GAME_MAIN}',
                   f'ANKISCAPE_DARKAN_WORLD_SERVER={remote.REMOTE_DARKAN}']
    if lane == 'plain':
        environment += [f'PYTHONPATH={remote.REMOTE_PLAIN_SITE}', '/opt/homebrew/bin/python3']
    else:
        environment += ['QT_QPA_PLATFORM=offscreen', str(remote.REMOTE_VENV / 'bin/python')]
    return shlex.join(environment + ['-B'])


def probe_command(remote, lane, baseline, output, *, preflight=False):
    arguments = ['tools/combat/compare_player_attack_rolls.py', '--baseline', baseline,
                 '--candidate-sha256', CANDIDATE, '--inventory', str(remote.REMOTE_REPO / INVENTORY),
                 '--inventory-sha256', PIN, '--output', str(output)]
    if preflight:
        arguments.append('--preflight')
    return remote_prefix(remote, lane) + ' ' + shlex.join(arguments)


def capture_guard(remote, lane, baseline, output, destination, sources):
    command = (f'cd {shlex.quote(str(remote.REMOTE_REPO))} && '
               + probe_command(remote, lane, baseline, output, preflight=True)
               + f' && cat {shlex.quote(str(output))}')
    try:
        raw = remote._ssh(command, label='player source guard', repeat_safe=True)
    except remote.SSHCommandError as error:
        destination.with_suffix('.error.txt').write_text(str(error))
        raise
    destination.with_suffix('.raw.json').write_text(raw)
    report = json.loads(raw)
    if report != {'baseline_sha256': BASELINE, 'inventory_sha256': PIN,
                  'sources_before': sources, 'sources_after': sources,
                  'status': 'PREFLIGHT_PASS', 'product_imported': False}:
        raise ValueError('remote source guard did not report the complete pinned inventory')
    save(destination, report)


def prepare_session(args, remote, sources):
    path = args.output / 'state.json'
    state = json.loads(path.read_text()) if path.exists() else None
    pending_path = remote._pending_path()
    if pending_path.exists():
        pending = json.loads(pending_path.read_text())
        if state is None or state['current'] is None or pending != state['current']['pending']:
            raise RuntimeError('another or unknown remote run owns the mirror pending record')
    if state is not None:
        if state['inventory_sha256'] != PIN or state['root'] != str(args.root):
            raise ValueError('saved run belongs to another source binding or root')
        if json.loads((args.output / 'local-before.json').read_text()) != sources:
            raise ValueError('initial local source snapshot differs')
        return state
    save(args.output / 'local-before.json', sources)
    remote._sync(args.root)
    session = uuid.uuid4().hex
    baseline = str(remote.REMOTE_ROOT / 'reports' / f'player-rolls-{session}-baseline.py')
    setup = ('import gzip,hashlib; from pathlib import Path; '
             f'raw=gzip.decompress(Path({str(remote.REMOTE_REPO / EVIDENCE / "baseline-engine.py.gz")!r}).read_bytes()); '
             f'assert hashlib.sha256(raw).hexdigest()=={BASELINE!r}; Path({baseline!r}).write_bytes(raw)')
    remote._ssh(remote_prefix(remote, 'plain') + ' -c ' + shlex.quote(setup),
                label='player baseline setup', repeat_safe=True)
    state = {'inventory_sha256': PIN, 'root': str(args.root), 'session': session,
             'baseline': baseline, 'completed': [], 'current': None}
    save(path, state)
    return state


def observe_existing(remote, pending, timeout):
    started = time.monotonic()
    while True:
        code = remote._completion_report(pending['report_path'])
        if code is not None:
            raw = remote._ssh('cat ' + shlex.quote(pending['log_path']),
                              label='player exact-run final log', repeat_safe=True)
            return code, raw
        if time.monotonic() - started >= timeout:
            raise TimeoutError(f"same remote run remains pending: {pending['run_id']}")
        time.sleep(5)


def launch_job(args, remote, state, lane, job, command, result_path):
    original_ssh = remote._ssh

    def launch_ssh(text, *, label, repeat_safe=False):
        if label == 'remote lane launch':
            pending = json.loads(remote._pending_path().read_text())
            state['current'] = {'job': job, 'pending': pending, 'result_path': result_path}
            save(args.output / 'state.json', state)
        return original_ssh(text, label=label, repeat_safe=repeat_safe)

    with patch.object(remote, '_remote_lane_command', return_value=command), \
         patch.object(remote, '_ssh', side_effect=launch_ssh):
        return remote._stream_remote_run(lane, timeout=args.timeout, poll_interval=5)


def validate_cases(rows):
    if [row['case'] for row in rows] != CASES:
        raise ValueError('comparison must contain exactly the 20 named cases in order')
    for row in rows:
        before = base64.b64decode(row['baseline_pickle_base64'], validate=True)
        after = base64.b64decode(row['candidate_pickle_base64'], validate=True)
        if row['equal'] is not True or before != after or row['rng_calls'] <= 0:
            raise ValueError('complete output and RNG payload differs or has no draws')
        if row['route_pass'] is not True or any(row['route_observed'][key] != value for key, value in row['route_expected'].items()):
            raise ValueError('advertised comparison route was not exercised')


def retain_comparison(remote, lane, result_path, destination, sources):
    reader = ('import base64,pathlib; print(base64.b64encode(pathlib.Path('
              + repr(result_path) + ').read_bytes()).decode())')
    encoded = remote._ssh(remote_prefix(remote, lane) + ' -c ' + shlex.quote(reader),
                          label='player comparison bytes', repeat_safe=True)
    raw = base64.b64decode(encoded.strip(), validate=True)
    destination.write_bytes(raw)
    report = json.loads(raw)
    if (report['status'] != 'PASS' or report['baseline_sha256'] != BASELINE
            or report['inventory_sha256'] != PIN
            or report['sources_before'] != sources or report['sources_after'] != sources):
        raise ValueError('comparison source binding or status differs')
    validate_cases(report['cases'])


def accept_job(args, remote, state, lane, kind, sources):
    current = state['current']
    job = current['job']
    if kind == 'focused':
        summary = remote.parse_unittest_summary((args.output / f'{job}.log').read_text())
        if summary.tests != 8 or summary.skipped != 0:
            raise ValueError(f'{job}: expected 8 tests and zero skips, got {summary}')
    else:
        retain_comparison(remote, lane, current['result_path'], args.output / f'{job}.json', sources)
    pending_path = remote._pending_path()
    if pending_path.exists():
        if json.loads(pending_path.read_text()) != current['pending']:
            raise RuntimeError('pending run identity changed; refusing to clear it')
        pending_path.unlink()
    state['completed'].append(job)
    state['current'] = None
    save(args.output / 'state.json', state)


def run_job(args, remote, sources, state, lane, kind):
    job = f'{lane}-{kind}'
    if job in state['completed']:
        return
    if state['current'] is not None and state['current']['job'] != job:
        raise ValueError('saved active job differs from the next required job')
    local_sources(args.root)
    stem = remote.REMOTE_ROOT / 'reports' / f"player-rolls-{state['session']}-{job}"
    result_path = str(stem) + '.json'
    phase = 'before' if not (args.output / f'{job}-before.json').exists() else 'resume-before-' + uuid.uuid4().hex[:8]
    capture_guard(remote, lane, state['baseline'], f'{stem}-{phase}.json', args.output / f'{job}-{phase}.json', sources)
    if state['current'] is None:
        command = (remote_prefix(remote, lane) + ' ' + shlex.join(['run_tests.py', '--verbosity', '2', *SELECTORS])
                   if kind == 'focused' else probe_command(remote, lane, state['baseline'], result_path))
        command = probe_command(remote, lane, state['baseline'], str(stem) + '-launch.json', preflight=True) + ' && ' + command
        code, raw = launch_job(args, remote, state, lane, job, command, result_path)
    else:
        code, raw = observe_existing(remote, state['current']['pending'], args.timeout)
    (args.output / f'{job}.log').write_text(raw)
    save(args.output / f'{job}-completion.json', {'exit_code': code, 'run': state['current']})
    report = remote._ssh('cat ' + shlex.quote(state['current']['pending']['report_path']),
                         label='player exact-run report', repeat_safe=True)
    (args.output / f'{job}.report').write_text(report)
    if int(report.strip()) != code:
        raise ValueError('completion report changed')
    capture_guard(remote, lane, state['baseline'], str(stem) + '-after.json', args.output / f'{job}-after.json', sources)
    save(args.output / f'{job}-local-after.json', local_sources(args.root))
    if code != 0:
        raise RuntimeError(f'{job} failed with exit {code}; retained exact run must not relaunch')
    accept_job(args, remote, state, lane, kind, sources)


def run_jobs(args, remote, sources):
    state = prepare_session(args, remote, sources)
    for lane in ('plain', 'qt'):
        remote._preflight(lane)
        for kind in ('focused', 'comparison'):
            run_job(args, remote, sources, state, lane, kind)
    save(args.output / 'complete.json', {'jobs': state['completed'], 'inventory_sha256': PIN})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--timeout', type=float, default=1800)
    parser.add_argument('--guard-only', action='store_true')
    args = parser.parse_args()
    if sys.flags.optimize or 'PYTHONOPTIMIZE' in os.environ:
        raise SystemExit('optimized interpreter refused; no remote calls permitted')
    if args.timeout <= 0:
        parser.error('--timeout must be positive')
    args.root, args.output = args.root.resolve(), args.output.resolve()
    if args.output.is_relative_to(args.root):
        parser.error('--output must be outside the source tree')
    sources = local_sources(args.root)
    args.output.mkdir(parents=True, exist_ok=True)
    if args.guard_only:
        save(args.output / 'local-guard.json', {'source_files': len(sources), 'inventory_sha256': PIN,
                                              'remote_calls': False, 'product_imports': False})
        return
    sys.path.insert(0, str(args.root))
    from tools import run_remote_tests as remote
    if remote.HOST != 'armans-macbook-pro' or str(remote.REMOTE_REPO) != '/Users/armantarkhanian/ankiscape-remote-test-host/ankiscape_fork':
        raise ValueError('remote host or repository pin differs')
    remote.LOCAL_MIRROR_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with remote.LOCAL_MIRROR_LOCK_PATH.open('a+') as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit(f'remote mirror busy: {remote.LOCAL_MIRROR_LOCK_PATH}')
        run_jobs(args, remote, sources)


if __name__ == '__main__':
    main()
