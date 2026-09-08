# Static verification proposal

Status: prepared, not executed. The compressed script is outside the runtime source inventory. It refuses optimized Python, checks the copied fixed instrument hashes, and then calls the installed gate functions without changes. It parses the baseline and four candidate sources, measures each function and file, applies the installed metric/layout ratchets, restores the complete engine and added-module patch forward and backward in a temporary directory, and retains raw subprocess output and full source maps before and after. A product-import sentinel and a measured module list prevent a static check from becoming product execution.

The instrument pins retain their original version observations as historical data. Current bytes must match before execution; they have not been checked in this preparation. The new guard and comparator are measured against empty base files, so all their functions must meet the normal limits. Restoration compares full bytes, not only hashes. The script does not run Vulture. After static review, run the installed gate's `dead_code_findings` on the same baseline/candidate snapshots and compare candidate findings minus baseline findings, retaining raw stdout, stderr, and return codes with the unchanged `VULTURE_MIN_CONFIDENCE` and exclusion list. This is a proposal; the normal commit hook remains authoritative.

```sh
python3 -B -c 'import gzip; from pathlib import Path; exec(compile(gzip.decompress(Path("memory-bank/evidence/combat-wyvern-breath-2026-09-07/static-verification.py.gz").read_bytes()), "wyvern-static-verification.py", "exec"))'
```

The parent must verify the script and binding hashes before running this command. No runtime source changed. Source, guard, comparison, full-lane, and merged-tree acceptance remain separate gates.

The new specials module is absent from the baseline snapshot. Forward restoration must reproduce its complete bytes; reverse restoration must remove it. Its functions and file size are measured against the absent baseline with the existing thresholds. The previous failed static run and original independent review remain historical evidence; this correction has not been checked.
