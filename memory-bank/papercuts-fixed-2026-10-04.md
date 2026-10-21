# Papercuts fixed — 2026-10-04

- 2026-10-04T00:31:24-07:00: Runtime forwarding-removal startup source reads exceeded the tool output budget (`Warning: truncated output (original token count: 43279)`); use bounded source reads and a total output budget per call. The direct-owner draft then hit the installed preflight authority: `runtime/runtime_actions.py: fan-out 120 (was 119)`; root notified, cap unchanged.

Source reads now use bounded output. The import refusal was resolved by using the existing combat dependency for the same wilderness function objects; the unchanged installed preflight exited 0. The retired carried forwarding module remains deleted.

- 2026-10-04T07:57:01Z: Cleanup evidence reads returned truncated output for whole memory-bank reads, a 976-line worktree inventory, a recursive scratch inventory (142718 tokens), and full-proof.json (46997 tokens). Root now projects typed JSON fields and uses bounded reads plus top-level file discovery. Source decisions use complete targeted bytes.
- 2026-10-04T07:57:01Z: Native lock probe assumed the ioreg JSON root was a list and failed with `AttributeError: 'str' object has no attribute 'get'`; three identical retries did not address the data-shape error. Root inspected the mapping and reads its authoritative IOConsoleLocked key. The read-only probe passed.
- 2026-10-04T07:57:01Z: Native task inspection with includeOutputs=false still returned full command strings. Root now projects the structured response before printing it; no task message was sent.
- 2026-10-04T07:57:01Z: Remote test discovery guessed nonexistent globs: `rg: tools/remote_test*.py: No such file or directory (os error 2)` and `rg: tools/remote/*.py: No such file or directory (os error 2)`. Root uses the verified tools/run_remote_tests.py and tools/promotion paths.
