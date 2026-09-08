# Combat food module revised author packet

Status: The revised candidate is frozen. Parent-accepted focused and differential runtime proof is complete in plain and Qt lanes.

Root review found that the first packet treated the rejected preview-only draft as the baseline. That exact packet is archived at `memory-bank/evidence/combat-food-module-pre-root-review-2026-09-08` with 23 copied files plus its archive manifest.

The branch baseline contains five definitions that move unchanged into `logic_pure/logic_pure_combat_food.py`: the default food tuple, consumption, loaded count, banked count, and loaded-food availability. Their source, AST, and prior namespace bindings are exact. The preview helper is new: it extracts the branch baseline's inline preview loop and exists only in the food module and engine. Supplies does not export it.

The focused runtime proposal contains nine selectors. Four existing combat tests cover consumption, loaded and banked food, auto-flee, and refill. Four narrow preview tests cover the new helper and full preview route. One narrow identity test checks the exact default tuple and every namespace that exposed the five moved definitions at the branch baseline.

The comparator still covers 15 complete preview return-or-exception cases and no longer accepts an unused output parameter. Its source preflight passes against the complete pinned inventory without product imports.

The 34.642-second temporary-index slop check covered only selected product and test paths. The first full staged slop gate exposed six archived `.py` copies as new code and failed in 42.253 seconds. Those copies now use deterministic gzip storage with exact decoded bindings, and the previous raw archive manifest is preserved. The same full staged gate passed in 37.564 seconds with empty stdout and stderr. The cached diff check then exposed context-space lines in nine retained raw prompt and diff files. Those nine files now also use deterministic gzip storage with exact decoded bindings. All eight pre-change manifest snapshots remain preserved, and a new unpinned storage overlay owns the current mappings. The new module has 112 lines. The `logic_pure` directory has 27 Python files. The gate limits are 1,000 lines for a grown code file and 40 code files in one directory.

Root owns the full source, composition, native programme, commit, and landing gates.

Root ran the inert harness safety checker after the packet freeze. All four safety-stop cases passed with zero remote calls and no product imports. Root's independent AST proof also passed. The retained results are `parent-inert-safety-check.json` and `parent-ast-proof.json`.

The first plain comparison then exposed an unreachable authored route. The case requested 100 lifepoints but retained Constitution level 1, so preview clamped the player to 10 lifepoints. Baseline and candidate matched in all 15 cases. The exact failed state remains in `memory-bank/evidence/combat-food-module-runtime-attempt-1-2026-09-08`.

The parent authorized one comparator-only correction: add `constitution_level=10` to `risk:safe-threshold`. Product and test bytes stayed unchanged. The corrected inert canary passed all four cases with zero remote calls.

The corrected plain and Qt focused lanes each passed nine tests with zero skips in 0.002 seconds. Both corrected differential lanes passed all 15 cases. Complete values, pickle bytes, restricted-unpickler structures, routes, and input state match the baseline.

All four corrected jobs match the same 1,218-entry source inventory before and after. The complete 42-file runtime packet and its raw-to-gzip bindings are in `runtime-acceptance.json` and `accepted-runtime/`.

Focused and differential proof is complete. Root review, a normal branch commit, the full source gate, merge into composition tree I, the exact post-merge gate, and main landing remain pending. Native programme acceptance is a separate programme check.
