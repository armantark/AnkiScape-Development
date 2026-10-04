# Papercuts fixed — 2026-10-04

- 2026-10-04T00:31:24-07:00: Runtime forwarding-removal startup source reads exceeded the tool output budget (`Warning: truncated output (original token count: 43279)`); use bounded source reads and a total output budget per call. The direct-owner draft then hit the installed preflight authority: `runtime/runtime_actions.py: fan-out 120 (was 119)`; root notified, cap unchanged.

Source reads now use bounded output. The import refusal was resolved by using the existing combat dependency for the same wilderness function objects; the unchanged installed preflight exited 0. The retired carried forwarding module remains deleted.
