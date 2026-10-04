# Cleanup source checkpoint, 2026-10-04

The goal remains active. Current main is `28481d9295db918396d5d0188f69c1ea36f102b5`.
Source acceptance does not grant runtime, native or promotion acceptance.

Combat clock source `6175db9b4e2dd6ce713e23814bca27a5da410ae1` has Astra source acceptance with no findings.
Root verified complete-parent AST equality after helper expansion. Other functions and exports remain unchanged.
Root remeasured the helper at CCN 2, cognitive 1 and Halstead difficulty 0.5, against unchanged 15/15/80 limits.
The parent measures CCN 167 and cognitive 279. The parent remains over limits.
Root audited all 155100 burst pairs and 2042 direct pairs. Both comparisons have zero differences.
Six binding refusal canaries stopped before cases. The one-tick mutation changed returned clocks in 64 cases and exited 1.
Both focused lanes passed 406 tests without skips: plain 8.713s; Qt 8.698s.
Runtime proof: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/6175db9b4e2dd6ce713e23814bca27a5da410ae1/runtime-clock-proof/retention-manifest.json`.
Focused proof: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/6175db9b4e2dd6ce713e23814bca27a5da410ae1/focused-clock-lanes/retention-manifest.json`.

Carried bank-gate source `16d8840410a9b6f1c27411e0d66893acb0fd2286` uses baseline `7e08030e3aa0323e5cc22d45865f9d458ec50fdc`.
The source has Astra acceptance with no findings. Root verified recursive AST equality and clean source.
Root remeasured the bank gate at 11/13 and route metadata at 6/8. Both pass the unchanged limits.
The parent measures 33/27 and remains over limits. The rejected first helper and its metric reports remain preserved.
Source proof: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/16d8840410a9b6f1c27411e0d66893acb0fd2286/source-review-root-check/retention-manifest.json`.
Root audited all 1158 complete dispatcher pairs, with zero differences and no check violations.
The corpus retains 132 inherited directed rows, all 1000 generated rows and 26 added rows.
All 13 required bank paths ran. The 32-review Firemaking refill sequence passed.
Four binding canaries stopped before cases. The metadata mutation changed actual state and callbacks in six cases.
Runtime proof: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/16d8840410a9b6f1c27411e0d66893acb0fd2286/runtime-bank-gate-proof/retention-manifest.json`.
Both carried focused lanes passed 241 tests without skips: plain 15.389s; Qt 15.773s.
No full-suite, native or promotion acceptance follows for either source.
The locked MacBook blocks genuine Anki Undo and native acceptance. No new waiver exists.
Preserve earlier accepted sources, Magic candidate `a8137bab` and Dream's dependency gate.
