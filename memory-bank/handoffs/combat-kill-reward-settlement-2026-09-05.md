# Combat kill reward settlement

Focused verification passed; full lanes, normal commit, and merged-tree promotion remain pending. Branch: `goal/combat-kill-reward-settlement-2026-09-05`. Base: `518a651db9e12e80ae9a1fd6e2b7b11c7357b360`.

One private helper replaces duplicate kill reward code. It preserves drop ownership, charm rewards, observation before prayer interception, prayer XP, and retained loot. Callers retain counters, refusal, attack delay, and distinct respawn rules.

Measured engine lines: 3,045 → 3,037; burst cyclomatic complexity: 348 → 342; cognitive complexity: 690 → 674. The helper measures 4 and 2. Other existing definitions have identical normalized ASTs. Both Opus static reviews passed; records bind the reviewed source versions.

The first plain comparison matched all 32 complete player/result/RNG payloads. One of 16 focused tests failed on its incorrect expected refusal. The parent approved `You already have a clue scroll: Clue scroll (easy)` and strengthened the chained-kill assertion to 9. Engine and probe bytes stayed unchanged.

The corrected plain and Qt lanes each passed 32 comparisons and 16 focused tests, with zero skips. All baseline/candidate pickle bytes matched; primitive-only observations matched across lanes. Over 50 ticks, the direct non-live fixture gives 13 kills without burial and 9 with burial, with 40.5 Prayer XP. Both use 26 RNG calls and end with empty encounter mappings; this does not establish a persisted attack clock.

All 769 listed source hashes matched before/after locally/remotely. The 128,059-byte baseline matched its frozen hash. All four jobs exited 0; pending record absent, lock released, mirror returned to orchestrator.

Raw capture:

- Local: `/tmp/ankiscape-combat-focused-corrected-9kp5kuyr`
- Remote: `/Users/armantarkhanian/ankiscape-remote-test-host/reports/ankiscape-combat-focused-corrected-9kp5kuyr`

Index: `memory-bank/evidence/combat-kill-reward-settlement-2026-09-05/manifest.json`. It binds separate failed and corrected runtime manifests. The failed capture is immutable. A retained `source_path` identifies its snapshot origin; the current file can differ. Historical parent preflight receipts bind the earlier probe.

Next: review final diff/evidence; run both full lanes and required checks; obtain orchestrator approval for normal author commit; complete merged-tree promotion checks. Reuse captured focused commands and hashes, syncing inventory gzip first. Run without `-O`/`PYTHONOPTIMIZE`. The inventory does not detect new unlisted files.

Installed static analyzers parse source without product imports. `complexipy` exits 1 for existing findings but writes valid JSON.

```bash
cd '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/combat-kill-reward-settlement'
/Users/ArmanTarkhanian1/.local/bin/lizard --csv logic_pure/logic_pure_combat_engine.py
mkdir -p /tmp/ankiscape-combat-kill-reward-parent-metrics-2026-09-05
/Users/ArmanTarkhanian1/.local/bin/complexipy logic_pure/logic_pure_combat_engine.py --output-format json --output /tmp/ankiscape-combat-kill-reward-parent-metrics-2026-09-05 -q -i
/Users/ArmanTarkhanian1/.local/bin/radon hal -f -j logic_pure/logic_pure_combat_engine.py
```
