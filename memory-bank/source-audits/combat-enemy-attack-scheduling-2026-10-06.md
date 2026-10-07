# Enemy attack scheduling source and focused checks

Source: `3b4b04f1eec6d5968c7d9f3fcd89cfab01d02c43`.
Base: `edeafd88c824e8a354b856cf37042ff68810bc5a`.
Branch: `codex/combat-enemy-attack-scheduling-2026-10-06`; pooled checkout 4 is clean.
The two-file extraction moves the retaliation latch and attack-due condition to the existing enemy-turn module.
Root expansion restores the complete engine AST. Every prior enemy-turn definition remains unchanged.
Committed source bytes match the root check. Astra and Kimi K3 approve this exact source with no findings.
The final helper measures CCN 5, cognitive 3 and Halstead difficulty 3.1818181818181817 under unchanged 15/15/80 limits.
The parent measures CCN 161, cognitive 269 and Halstead difficulty 16.638297872340427. The parent remains over limits.
Each lane collected a fresh inventory of 406 tests on the same source.
The plain lane passed 406 tests without skips in 8.762s; the Qt lane passed 406 tests without skips in 8.738s.
Root verified every inventory and run log hash, exact source binding and outer exit 0.
Evidence: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/3b4b04f1eec6d5968c7d9f3fcd89cfab01d02c43/source-review-and-focused-lanes/retention-manifest.json`.
Complete behavior proof, native acceptance, full branch and merged gates, and promotion remain pending.
No prior clock or supply proof accepts this scheduling source. Canonical main remains unchanged.
