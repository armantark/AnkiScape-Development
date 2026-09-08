# Dragonfire damage extraction handoff

## Goal

Verify that the private helper preserves ordinary dragonfire behavior.

## Context

The branch is `goal/combat-dragonfire-damage-2026-09-08`.
The frozen base is P5 commit `9826842463f2e73d178d2042e8d5b726a8dd5aa2`.
The parent accepted the retained Opus product review as `PASS` with terminal status `0`.
The parent also accepted the eight-case pre-import guard with terminal status `0` and no product import attempt. Its exact 2,361-byte result is retained in `memory-bank/evidence/combat-dragonfire-damage-2026-09-08/parent-preimport-guard.json.gz`.
The parent accepted the corrected static, local guard, inert resume, and remote runtime evidence. Both remote lanes ran three focused tests with zero skips and all 12 comparison cases. The accepted 38-file runtime packet is indexed by `memory-bank/evidence/combat-dragonfire-damage-2026-09-08/accepted-runtime-68011.json`; the failed session `45231` and its frozen source packet remain retained separately.

## Scope

The helper moves the protection lookup and one damage roll to `logic_pure/logic_pure_combat_specials.py`.
The caller keeps attack selection, Wyvern precedence, counters, timing, life-point limits, and result data.
The existing `combat_dragonfire_protection_pure` engine export remains in use.
The test files have no changes.

## Verification

Do not change a product file or a proof tool after the source freeze.

1. Review `memory-bank/evidence/combat-dragonfire-damage-2026-09-08/product.diff`.
2. Run the pinned static ratchet and reversible patch check.
3. Confirm the retained pre-import guard evidence.
4. Run the local-only driver guard and inert resume canary.
5. Use the resumable driver for the three focused tests and the comparison in the plain lane and the Qt lane.

```sh
python3 -B -c 'import gzip; from pathlib import Path; exec(compile(gzip.decompress(Path("memory-bank/evidence/combat-dragonfire-damage-2026-09-08/static-verification.py.gz").read_bytes()), "dragonfire-damage-static-verification.py", "exec"))'
python3 -B tools/combat/run_dragonfire_damage_remote.py --guard-only --output /tmp/ankiscape-dragonfire-local-guard-2026-09-08
python3 -B tools/combat/check_dragonfire_damage_remote_resume.py --output /tmp/ankiscape-dragonfire-inert-resume-2026-09-08.json
python3 -B tools/combat/run_dragonfire_damage_remote.py --output /tmp/ankiscape-dragonfire-runtime-2026-09-08
```

The static check must report no syntax, metric, layout, file-growth, restoration, source, or product-import failure across all six candidate Python files.
The guard must report eight accepted canary cases and no product import.
The local driver guard must report 1,083 source files, no remote call, and no product import.
The inert canary must prove that a retained run resumes without a second launch or sync, refuses foreign pending state, preserves guard errors, and rejects incomplete comparison evidence.
Each focused lane must run three tests with zero skips.
Each comparison lane must pass all 12 cases.
Each case must have equal complete values, equal pickle bytes, and the expected route data.
The source maps before and after the comparison must equal the frozen inventory.

## Accepted outcome

The parent accepted the source, proof instruments, corrected route expectations, local checks, remote runtime, and retained evidence. Integration remains parent-owned.
