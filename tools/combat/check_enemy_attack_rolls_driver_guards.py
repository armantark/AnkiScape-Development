"""Exercise only local pre-import guards; run after parent review."""
import contextlib
import gzip
import io
import json
from pathlib import Path
import runpy
import sys
import subprocess
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
DRIVER = ROOT / 'tools/combat/run_enemy_attack_rolls_remote.py'
EV = ROOT / 'memory-bank/evidence/combat-enemy-attack-rolls-2026-09-05'
sys.path.insert(0, str(ROOT))
from tools import run_remote_tests as remote

attempts = []


def audit(event, args):
    if event == 'import' and args[0].split('.')[0] in {'ankiscape', 'pkg_alias', 'tests'}:
        attempts.append(args[0])
        raise RuntimeError('Product import attempted during driver canary.')


sys.addaudithook(audit)
with tempfile.TemporaryDirectory(prefix='enemy-roll-guard-') as directory:
    scratch = Path(directory)
    wrong_baseline = scratch / 'wrong-baseline.py.gz'
    wrong_baseline.write_bytes(gzip.compress(b'wrong baseline'))
    wrong_inventory = scratch / 'wrong-inventory.json.gz'
    wrong_inventory.write_bytes(gzip.compress(b'{}'))
    cases = [
        ('correct', [], None),
        ('wrong-baseline', ['--baseline', str(wrong_baseline)], 'Baseline source hash differs.'),
        ('wrong-candidate', ['--candidate-sha256', '0' * 64], 'Candidate source hash differs.'),
        ('wrong-inventory', ['--inventory', str(wrong_inventory)], 'Inventory hash differs.'),
    ]
    rows = []
    for name, arguments, expected_error in cases:
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(remote, '_ssh', side_effect=RuntimeError('Remote call forbidden.')) as ssh, patch.object(remote, '_sync', side_effect=RuntimeError('Sync forbidden.')) as sync, patch.object(sys, 'argv', [str(DRIVER), '--guard-only', *arguments]), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                runpy.run_path(str(DRIVER), run_name='__main__')
            except SystemExit as error:
                assert expected_error is None and error.code == 0
                outcome = 'GUARD_PASS'
            except AssertionError as error:
                assert expected_error is not None and str(error) == expected_error
                outcome = str(error)
            else:
                raise AssertionError('Driver did not terminate at the guard.')
        assert ssh.call_count == sync.call_count == 0 and not attempts
        rows.append({'case': name, 'outcome': outcome, 'remote_calls': ssh.call_count, 'sync_calls': sync.call_count, 'stdout': stdout.getvalue(), 'stderr': stderr.getvalue()})
    optimized_bootstrap = """import runpy, sys, types
remote = types.ModuleType('tools.run_remote_tests')
tools = types.ModuleType('tools')
tools.run_remote_tests = remote
sys.modules.update({'tools': tools, 'tools.run_remote_tests': remote})
def audit(event, args):
    if event == 'import' and args[0].split('.')[0] in {'ankiscape', 'pkg_alias', 'tests'}:
        raise RuntimeError('Product import attempted during optimized canary.')
sys.addaudithook(audit)
sys.argv = [sys.argv[1], '--guard-only']
runpy.run_path(sys.argv[0], run_name='__main__')
"""
    optimized = subprocess.run([sys.executable, '-B', '-O', '-c', optimized_bootstrap, str(DRIVER)], capture_output=True, text=True, timeout=30)
    assert optimized.returncode == 1 and optimized.stdout == ''
    assert optimized.stderr.strip() == 'Refusing to run with optimizations; the pins are assertions.'
    rows.append({'case': 'optimized-interpreter', 'outcome': optimized.stderr.strip(), 'remote_calls': 0, 'sync_calls': 0, 'stdout': optimized.stdout, 'stderr': optimized.stderr})
    assert not any(name.split('.')[0] in {'ankiscape', 'pkg_alias', 'tests'} for name in sys.modules)
    print(json.dumps({'status': 'PASS', 'cases': rows, 'product_import_attempts': attempts}, indent=2))
