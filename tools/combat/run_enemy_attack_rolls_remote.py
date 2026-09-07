"""Pinned enemy-roll runtime jobs; --guard-only never contacts the host."""

import argparse
import fcntl
import gzip
import hashlib
import json
import os
from pathlib import Path
import shlex
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools import run_remote_tests as remote

BASELINE = '30377177ba69e1aa112a8d8b384cfd205d6d593133821bdbf74ce85fbcd323f6'
SOURCES = {
    'logic_pure/logic_pure_combat_engine.py': '486a532d00d4e5693894b77a022ef83a32e03f55e841c2ff92ab12fc7e9ad2d4',
    'tests/combat/test_enemy_attack_rolls.py': 'f9d87f74b3d3b6aef50c538fb8c259c3cb5cdbfed532da46e7878240843925f5',
    'tools/combat/compare_enemy_attack_rolls.py': '9653e8edfbabae995a5fa80a0f10a6944ccc58d148dec3fb484cc1f7f742a252',
}
SELECTORS = ['CombatEnemyAttackRollsTest', 'CombatEnemyAttackStyleTest']
EXPECTED_CASES = ['initial:melee', 'initial:ranged', 'initial:magic', 'initial:magic_melee', 'override:ranged', 'override:magic_melee', 'early-exit:teleport', 'early-exit:unequip', 'max-hit:lifepoints', 'max-hit:old-hp', 'max-hit:derived-ranged', 'max-hit:derived-melee', 'weakening:False', 'weakening:True', 'defence-drain:1', 'defence-drain:2', 'live-curse-spell:(9,)', 'live-curse-spell:(3, 6)', 'live-prayer-depletion:(3,)', 'live-prayer-depletion:(1, 1, 1)', 'bypass:dragonfire', 'bypass:wyvern']
EV = ROOT / 'memory-bank/evidence/combat-enemy-attack-rolls-2026-09-05'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--guard-only', action='store_true')
parser.add_argument('--baseline', type=Path, default=EV / 'baseline-engine.py.gz')
parser.add_argument('--inventory', type=Path, default=EV / 'source-inventory.json.gz')
parser.add_argument('--candidate-sha256', default=SOURCES['logic_pure/logic_pure_combat_engine.py'])
args = parser.parse_args()
if sys.flags.optimize or 'PYTHONOPTIMIZE' in os.environ:
    raise SystemExit('Refusing to run with optimizations; the pins are assertions.')
inventory_bytes = args.inventory.read_bytes()
assert hashlib.sha256(inventory_bytes).hexdigest() == '426cafbfbd349229fb59de064f290cc31a5bf233188d64011a6435ae47e94562', 'Inventory hash differs.'
expected = json.loads(gzip.decompress(inventory_bytes))
assert hashlib.sha256(gzip.decompress(args.baseline.read_bytes())).hexdigest() == BASELINE, 'Baseline source hash differs.'
assert args.candidate_sha256 == SOURCES['logic_pure/logic_pure_combat_engine.py'], 'Candidate source hash differs.'
actual = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in expected}
assert actual == expected and len(actual) == 771
assert all(actual[p] == digest for p, digest in SOURCES.items())
assert remote.HOST == 'armans-macbook-pro'
assert str(remote.REMOTE_REPO) == '/Users/armantarkhanian/ankiscape-remote-test-host/ankiscape_fork'
if args.guard_only:
    print(json.dumps({'status': 'GUARD_PASS', 'sources': actual, 'remote_calls': 0}))
    raise SystemExit(0)
OUT = Path(tempfile.mkdtemp(prefix='ankiscape-enemy-rolls-', dir='/tmp'))
REMOTE_OUT = remote.REMOTE_ROOT / 'reports' / OUT.name
report = {'local_root': str(ROOT), 'local_output': str(OUT), 'remote_output': str(REMOTE_OUT), 'local_sources_before': actual, 'jobs': [], 'ownership': 'not_acquired'}


def save():
    (OUT / 'capture.json').write_text(json.dumps(report, indent=2) + '\n')


save()
print('CAPTURE_DIRECTORY', OUT, flush=True)

SETUP = '''import gzip,hashlib,json,os,sys
from pathlib import Path
root=Path(%r)
out=Path(%r)
assert sys.flags.optimize==0 and 'PYTHONOPTIMIZE' not in os.environ
out.mkdir(parents=True,exist_ok=True)
ev=root/'memory-bank/evidence/combat-enemy-attack-rolls-2026-09-05'
expected=json.loads(gzip.decompress((ev/'source-inventory.json.gz').read_bytes()))
actual={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in expected}
assert actual==expected and len(actual)==771
baseline=gzip.decompress((ev/'baseline-engine.py.gz').read_bytes())
assert hashlib.sha256(baseline).hexdigest()==%r
(out/'baseline.py').write_bytes(baseline)
result={'sources':actual,'baseline_bytes':len(baseline),'baseline_sha256':hashlib.sha256(baseline).hexdigest(),'python':sys.executable,'version':sys.version,'optimize':sys.flags.optimize,'pythonoptimize_present':'PYTHONOPTIMIZE' in os.environ}
print(json.dumps(result,indent=2))
''' % (str(remote.REMOTE_REPO), str(REMOTE_OUT), BASELINE)

SNAPSHOT = '''import gzip,hashlib,json
from pathlib import Path
root=Path(%r)
ev=root/'memory-bank/evidence/combat-enemy-attack-rolls-2026-09-05'
expected=json.loads(gzip.decompress((ev/'source-inventory.json.gz').read_bytes()))
actual={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in expected}
print(json.dumps(actual,indent=2))
assert actual==expected
''' % str(remote.REMOTE_REPO)

try:
    with remote.LOCAL_MIRROR_LOCK_PATH.open('a+', encoding='utf-8') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        report['ownership'] = 'acquired'
        save()
        try:
            remote._preflight('plain')
            remote._preflight('qt')
            remote._sync(ROOT)
            setup_command = shlex.join(['env', '-u', 'PYTHONOPTIMIZE', '/opt/homebrew/bin/python3', '-B', '-c', SETUP])
            setup = remote._ssh(setup_command, label='combat frozen source setup', repeat_safe=True)
            (OUT / 'remote-before.json').write_text(setup)
            assert json.loads(setup)['sources'] == actual
            for lane in ('plain', 'qt'):
                interpreter = '/opt/homebrew/bin/python3' if lane == 'plain' else str(remote.REMOTE_VENV / 'bin/python')
                environment = ['env', '-u', 'PYTHONOPTIMIZE', 'PATH=/opt/homebrew/bin:/usr/bin:/bin', 'PYTHONDONTWRITEBYTECODE=1', f'ANKISCAPE_GAME_MAIN={remote.REMOTE_GAME_MAIN}', f'ANKISCAPE_DARKAN_WORLD_SERVER={remote.REMOTE_DARKAN}']
                environment.append(f'PYTHONPATH={remote.REMOTE_PLAIN_SITE}' if lane == 'plain' else 'QT_QPA_PLATFORM=offscreen')
                for kind in ('comparison', 'focused'):
                    stem = f'{lane}-{kind}'
                    stdout_path, stderr_path = REMOTE_OUT / (stem + '.stdout'), REMOTE_OUT / (stem + '.stderr')
                    if kind == 'comparison':
                        arguments = ['tools/combat/compare_enemy_attack_rolls.py', '--baseline', str(REMOTE_OUT / 'baseline.py'), '--candidate-sha256', SOURCES['logic_pure/logic_pure_combat_engine.py'], '--inventory', str(remote.REMOTE_REPO / 'memory-bank/evidence/combat-enemy-attack-rolls-2026-09-05/source-inventory.json.gz'), '--output', str(REMOTE_OUT / (stem + '.json'))]
                    else:
                        arguments = ['run_tests.py', '--verbosity', '2', *SELECTORS]
                    command = shlex.join([*environment, interpreter, '-B', *arguments])
                    if kind == 'comparison':
                        preflight_arguments = [*arguments[:-1], str(REMOTE_OUT / (stem + '-preflight.json')), '--preflight']
                        preflight_command = shlex.join([*environment, interpreter, '-B', *preflight_arguments])
                        command = '( ' + preflight_command + ' && ' + command + ' )'
                    shell = '\n'.join((f'{command} > {shlex.quote(str(stdout_path))} 2> {shlex.quote(str(stderr_path))}', 'job_exit=$?', f'cat {shlex.quote(str(stdout_path))}', f'cat {shlex.quote(str(stderr_path))} >&2', 'exit "$job_exit"'))
                    job = {'lane': lane, 'kind': kind, 'command': command, 'remote_stdout': str(stdout_path), 'remote_stderr': str(stderr_path)}
                    report['jobs'].append(job)
                    save()
                    original_ssh = remote._ssh

                    def capture_ssh(command, *, label, repeat_safe=False):
                        if label == 'remote lane launch':
                            job['run'] = json.loads(remote._pending_path().read_text())
                            save()
                        return original_ssh(command, label=label, repeat_safe=repeat_safe)

                    with patch.object(remote, '_remote_lane_command', return_value=shlex.join(['/bin/sh', '-c', shell])), patch.object(remote, '_ssh', side_effect=capture_ssh):
                        code, output = remote._stream_remote_run('combat-' + stem, timeout=900, poll_interval=3)
                    job['exit_code'] = code
                    (OUT / (stem + '.log')).write_text(output)
                    for suffix, path in [('stdout', stdout_path), ('stderr', stderr_path), ('report', Path(job['run']['report_path']))]:
                        body = remote._ssh('cat ' + shlex.quote(str(path)), label='combat raw report read', repeat_safe=True)
                        (OUT / (stem + '.' + suffix)).write_text(body)
                    if kind == 'comparison':
                        remote_json = REMOTE_OUT / (stem + '.json')
                        body = remote._ssh('cat ' + shlex.quote(str(remote_json)), label='combat comparison payload read', repeat_safe=True)
                        (OUT / (stem + '.json')).write_text(body)
                    save()
                    print('TERMINAL_JOB', stem, code, flush=True)
                    if code != 0:
                        raise RuntimeError(f'{stem} failed with exit {code}; frozen artifacts retained')
                    if kind == 'comparison':
                        result = json.loads(body)
                        assert result['status'] == 'PASS'
                        assert [row['case'] for row in result['cases']] == EXPECTED_CASES
                        assert all(row['equal'] for row in result['cases'])
                        assert result['sources_before'] == actual == result['sources_after']
                        preflight_body = remote._ssh('cat ' + shlex.quote(str(REMOTE_OUT / (stem + '-preflight.json'))), label='enemy rolls preflight report read', repeat_safe=True)
                        (OUT / (stem + '-preflight.json')).write_text(preflight_body)
                        assert json.loads(preflight_body)['status'] == 'PREFLIGHT_PASS'
                    else:
                        summary = remote.parse_unittest_summary(output)
                        assert summary.tests == 10 and summary.skipped == 0, summary
        finally:
            try:
                after = remote._ssh(shlex.join(['env', '-u', 'PYTHONOPTIMIZE', '/opt/homebrew/bin/python3', '-B', '-c', SNAPSHOT]), label='combat final source snapshot', repeat_safe=True)
                (OUT / 'remote-after.json').write_text(after)
                report['remote_sources_unchanged'] = json.loads(after) == actual
                save()
                if not report['remote_sources_unchanged']:
                    raise RuntimeError('Remote source hashes changed.')
            finally:
                report['pending_record_exists'] = remote._pending_path().exists()
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
                report['ownership'] = 'released'
                save()
                if report['pending_record_exists']:
                    raise RuntimeError('Pending remote run remains; acceptance blocked.')
except BaseException as error:
    report['error'] = repr(error)
    save()
    raise
finally:
    report['local_sources_after'] = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in expected}
    report['local_sources_unchanged'] = report['local_sources_after'] == actual
    save()
    if not report['local_sources_unchanged']:
        raise RuntimeError('Local source hashes changed.')
