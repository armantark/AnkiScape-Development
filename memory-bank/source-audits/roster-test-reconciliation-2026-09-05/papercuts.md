# Review packet friction

2026-09-06T02:16:52.003839+00:00 — Copying the preserved test directory into the author review packet also copied 12 historical Python 3.13/3.14 bytecode files. Removed only those copies from the new review packet; original test-directory caches remain untouched. No project code was imported or executed.

2026-09-06T03:19:47.854052+00:00 — Parent roster metadata inspection printed a result row with 804 hashes instead of keys; the output reported 41315 original tokens truncated. Changed schema inspection to key-only output.

2026-09-06T03:19:47.854052+00:00 — Parent release search guessed absent .github, tools/build_addon.py and manifest.json paths and reported No such file or directory. Use the tracked file inventory before scoped reads.

2026-09-06T03:19:47.854052+00:00 — Parent release object count passed rev-list object-plus-path output to cat-file without %(rest), which produced a misleading zero count. Corrected the parser with --no-object-names and measured 9404 new blobs and 1228167375 bytes; the zero is not a repository measurement.

2026-09-06T03:19:47.854052+00:00 — Author retention read guessed audit.md while the directory inventory was still running; cat reported No such file or directory. The listed file is report.md. Complete inventory before dependent reads.

2026-09-06T03:19:47.854052+00:00 — Author release search used a broad text match against generated shop_data.py and emitted 85202 original tokens before truncation. Use filename-only discovery or a bounded match with maximum column width for generated literals.

2026-09-06T03:19:47.854052+00:00 — Author independent relocation validator dropped the final newline through splitlines and initially assumed payload stderr was empty. Corrected the parser and verified the exact MODULE_SURFACE_ENV: python=3.14.6 hash_seed=0 line in all payload stderr files; the final independent report passed.

2026-09-06T03:21:54.952183+00:00 — The post-retention documentation audit returned dangling_test_selector for memory-bank/source-audits/combat-enemy-roster-step1-data-report-2026-07-07.md:99 and :100. Exact selector diagnostics are retained in evidence/roster/operations/documentation-audit.json.gz. The historical audit must remain unchanged; the parent must resolve the historical-selector gate policy before claiming a clean documentation pass.
