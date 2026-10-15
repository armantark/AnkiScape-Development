# Source-packet CLIs work outside the checkout — 2026-10-14

Main `fdb1ac49f986437c9b9fba6d8dd313146fb19124` landed through tools/promotion_gate.py land at 2026-10-14T21:49:02.896801+00:00, actual exit0. The source freezer and evidence retainer find the checkout before package imports in direct script mode. Standard help and argument refusal work from an unrelated directory; module mode and all safety checks keep their meaning.

Source `49bdf2e2cecd647498b0fe6e3804ca04a0671198` has independent Astra and Zhipu acceptance with no remaining findings. All three source-code/test files on the exact merged tree match the reviewed source bytes.

The original isolated regression was RED in four canaries, then GREEN: one test, zero skips, actual exit0. Its unrelated sentinel stayed unchanged. The original17-test adjacent run's outer exit stays UNVERIFIED. New full gate proof supplies integration acceptance and does not change that original receipt.

The exact full remote-lane gate exited0 and passed all nine checks. Plain:5328 tests,641.555s,580 skips. Qt:5328 tests,869.612s,5 skips. Docs, test quality, reachability, layout, clean tree, diff and papercut checks all passed. No test, limit, baseline or native criterion changed.

Retained packet: [/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/retained-papercut-fdb1ac49/retention-manifest.json](/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/retained-papercut-fdb1ac49/retention-manifest.json), SHA256`031270690bc8e77e534c48369fdfa4afb47682f90d91d8934cbc8490c8667b8c`, 43 files, 148866 bytes. It contains the original receipts, independent reviews, exact full-gate certificate and official land log.

Only the proven standalone freezer incident2026-10-08T02:05:24.428137+00:00 moved to the fixed log. Mixed host/path incidents stay open. No native action or existing UI change was part of this developer-tool slice; no push occurred.
