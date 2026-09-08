# Diff-only simplification review

| Location | Unrequested complexity | Smaller replacement |
| --- | --- | --- |
| `logic_pure/logic_pure_combat_engine.py` helper extraction | The first layout-only extraction grew the already-oversized engine from 3,010 to 3,015 lines. | Keep the exact moved statements and event mapping, but use their compact existing forms for slot ordering and the returned event. The final engine is 3,009 lines. |
| `memory-bank/evidence/combat-unequip-transaction-2026-09-07/static-verification.py` imports | `deepcopy` was imported but never used. | Delete the import. |

No other valid deletion was found. The three test routes each cover a distinct required state transition, the whole-engine probe owns equivalence plus genuine-route evidence, and the guard owns failure-before-import canaries that the comparison probe cannot safely test itself.
