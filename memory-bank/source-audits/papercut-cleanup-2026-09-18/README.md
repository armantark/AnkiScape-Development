# Papercut cleanup evidence

This directory records a one-time maintenance task. The implementation goal remains paused.

`inventory.json` assigns every dated incident in the frozen source set to a cause group. `inventory-coverage.json` records the independent coverage check. The sources come from baseline `7f736d5c63ca0d301b1789798e75fa2737435f4c`; each source has a byte hash. Two logs can describe the same event, so entry counts are not counts of unique incidents.

The inventory distinguishes earlier repairs, this pass, operator errors, external limits, owner decisions and paused feature work. `fixed-this-pass` records implemented repairs with regression evidence; landing still requires the exact final full-gate receipt. A source record is evidence of a historical incident, not proof of a current defect.

Run the coverage check from the repository root:

```sh
python3 tools/maintenance/audit_papercut_inventory.py memory-bank/source-audits/papercut-cleanup-2026-09-18/inventory.json
```

Expect an empty `errors` list and exit 0. The checker rejects gaps, extra lines, duplicate assignments, source hash changes and missing evidence. The retained canaries demonstrate refusal as well as success.

Author reports retain their original scope and results. Root reports and gate receipts establish acceptance. `review-resolution.md` records the response to independent review. Compressed probe source is inert historical evidence; it does not run as part of the add-on.

The architecture analysis and copy-paste prompt for Fable are in `memory-bank/handoffs/fable-grill-papercuts-2026-09-19.md` after finalization. This task does not call Fable.

`final-verification.md` separates the failed early documentation check from final acceptance. New incidents from this maintenance run are appended to the main papercut log; the inventory source set stays frozen at its declared baseline. Compressed one-off probes are historical evidence, not installed tools.
