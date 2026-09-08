# Runtime diff-only simplification review

| Location | Unrequested complexity | Smaller replacement |
| --- | --- | --- |
| `prepare_session` | The P4 runner decoded the baseline and created a remote temporary file because its comparison required plain source. | Use the synchronized `baseline-engine.py.gz` path directly because the P13 comparison decompresses and verifies it. |
| Driver selectors and comparison labels | The P4 runner carried eight test methods and twenty comparison labels for player attack rolls. | Bind exactly four test methods and four differential labels for enemy unequip. |

No other valid deletion was found. The remaining lock, pending-run record, source guards, raw reports, resume path, and acceptance checks each enforce a required stop.
