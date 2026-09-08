# Wyvern runtime preparation

Status: driver and inert canary prepared, not executed. Product sources, probe, guard, and inventory remain frozen. The parent reports current product static session 39751 exited zero with all five ratchets passing and full forward/reverse restoration, including removal of the new module. The current seven-case product guard exited zero without product imports. Their exact raw files are retained separately. These observations do not cover the new driver or canary.

The driver uses the existing remote runner and mirror lock. Local guard-only mode imports no runner or product module. Each of four jobs has local and remote source guards; the remote command guards the sources again immediately before its payload. The focused selection requires five methods and zero skips. Comparison requires nineteen ordered cases, complete byte equality, explicit RNG totals, and route agreement. Both plain and Qt lanes must pass.

A pending launch identity is saved before launch. A timeout resumes its exact report and log without sync or relaunch. Foreign pending state is refused before sync. Initial before-evidence is retained across resumes; failure logs, completion reports, source-guard failures, and source maps remain reviewable. The inert canary uses fake SSH and synthetic bytes, never a game result. It exercises launch timeout, failed exact-run resume, foreign ownership, evidence retention, source-guard errors, and comparison acceptance refusals.

The driver/canary binding is separate from the frozen product inventory. Review both complete packets and the static script before running any command. The prepared static script measures both new files against an empty baseline through the unchanged installed gate functions and thresholds. No source-changing sync may occur while the parent's current mirror owner remains active.

```sh
python3 -B -c 'import gzip; from pathlib import Path; exec(compile(gzip.decompress(Path("memory-bank/evidence/combat-wyvern-breath-2026-09-07/runtime-static-verification.py.gz").read_bytes()), "wyvern-runtime-static.py", "exec"))'
python3 -B tools/combat/run_wyvern_breath_remote.py --guard-only --output /tmp/ankiscape-wyvern-local-guard-2026-09-07
python3 -B tools/combat/check_wyvern_remote_resume.py --output /tmp/ankiscape-wyvern-inert-resume-2026-09-07.json
```

Only the parent may authorize and launch the runtime command after review, local canaries, and mirror availability. Repeat the exact same command and output directory to resume its saved run.

```sh
python3 -B tools/combat/run_wyvern_breath_remote.py --output /tmp/ankiscape-wyvern-runtime-2026-09-07
```
