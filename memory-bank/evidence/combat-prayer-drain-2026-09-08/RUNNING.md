# Prayer-drain runtime handoff

## Goal

Run four remote jobs against the pinned prayer-drain source tree. Retain one exact identity and one output directory for each job.

## Context

The source inventory SHA-256 is `248d5502a017d83e2a060a2041061a5acd442a8101200bea52029ac3de1a2850`. The inventory has 1,185 entries.

The one-job harness is `runtime-harness.py.gz`. The stored SHA-256 is `2732e1e734a79f359ac1a5ed95705d8bb0ea4b4d15680e37e1218fc54ee067c4`.

The decoded harness SHA-256 is `f96e818d23d32721069821cb1bbf8c27c335c017035a95fb0961edc60def6888`. The decoded harness has 13,958 bytes.

## Scope

The harness runs one lane and one job type. It does not resume or relaunch a failed job.

The harness rejects a busy mirror. It saves the pending identity before the launch SSH call.

## Steps

Do not start a runtime job until the operational review passes.

1. Decode the harness and check its hash.

```bash
cd '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/pool/.treehouse/ankiscape_fork-091389/13/ankiscape_fork'
env -u PYTHONOPTIMIZE python3 -c 'import gzip,hashlib,pathlib; source=pathlib.Path("memory-bank/evidence/combat-prayer-drain-2026-09-08/runtime-harness.py.gz"); raw=gzip.decompress(source.read_bytes()); assert hashlib.sha256(raw).hexdigest()=="f96e818d23d32721069821cb1bbf8c27c335c017035a95fb0961edc60def6888"; pathlib.Path("/tmp/ankiscape-prayer-drain-runtime-harness-f96e818d.py").write_bytes(raw)'
```

2. Decode the inert safety check and check its hash.

```bash
env -u PYTHONOPTIMIZE python3 -c 'import gzip,hashlib,pathlib; source=pathlib.Path("memory-bank/evidence/combat-prayer-drain-2026-09-08/runtime-safety-check.py.gz"); raw=gzip.decompress(source.read_bytes()); assert hashlib.sha256(raw).hexdigest()=="efc91844b1d3961d409ac33d6d0aca2b838f3da5e073fdd2327a4765358d1e89"; pathlib.Path("/tmp/ankiscape-prayer-drain-runtime-safety-check-efc91844.py").write_bytes(raw)'
```

3. Run the inert safety check.

```bash
env -u PYTHONOPTIMIZE python3 -B /tmp/ankiscape-prayer-drain-runtime-safety-check-efc91844.py --harness memory-bank/evidence/combat-prayer-drain-2026-09-08/runtime-harness.py.gz --output /tmp/ankiscape-prayer-drain-runtime-safety-check.json
```

4. Read the safety-check result. Require `status: PASS`, `actual_remote_calls: 0`, and unchanged product imports.

```bash
cat /tmp/ankiscape-prayer-drain-runtime-safety-check.json
```

Do not reuse an output directory. A nonempty output directory stops the harness.

5. Run the plain focused job.

```bash
env -u PYTHONOPTIMIZE python3 -B /tmp/ankiscape-prayer-drain-runtime-harness-f96e818d.py --root '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/pool/.treehouse/ankiscape_fork-091389/13/ankiscape_fork' --output /tmp/ankiscape-prayer-drain-plain-focused-2026-09-08 --lane plain --kind focused --timeout 1800
```

6. Run the plain comparison job.

```bash
env -u PYTHONOPTIMIZE python3 -B /tmp/ankiscape-prayer-drain-runtime-harness-f96e818d.py --root '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/pool/.treehouse/ankiscape_fork-091389/13/ankiscape_fork' --output /tmp/ankiscape-prayer-drain-plain-comparison-2026-09-08 --lane plain --kind comparison --timeout 1800
```

7. Run the Qt focused job.

```bash
env -u PYTHONOPTIMIZE python3 -B /tmp/ankiscape-prayer-drain-runtime-harness-f96e818d.py --root '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/pool/.treehouse/ankiscape_fork-091389/13/ankiscape_fork' --output /tmp/ankiscape-prayer-drain-qt-focused-2026-09-08 --lane qt --kind focused --timeout 1800
```

8. Run the Qt comparison job.

```bash
env -u PYTHONOPTIMIZE python3 -B /tmp/ankiscape-prayer-drain-runtime-harness-f96e818d.py --root '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/pool/.treehouse/ankiscape_fork-091389/13/ankiscape_fork' --output /tmp/ankiscape-prayer-drain-qt-comparison-2026-09-08 --lane qt --kind comparison --timeout 1800
```

## Verification

Each successful job writes `accepted.json`. Each file must report `status: PASS` and the requested lane and job type.

Each job also writes `identity.json`, `run.log`, `run.report`, `completion.json`, `before.json`, `after.json`, and `local-after.json`.

A comparison job also writes `comparison.json`. It must contain nine ordered cases with complete return and pickle-byte equality.

A focused job must report three tests and zero skips.

## Failure rule

Do not run the same command again after a failure or timeout. Use `identity.json` or `interrupted.json` to inspect the exact remote run.
