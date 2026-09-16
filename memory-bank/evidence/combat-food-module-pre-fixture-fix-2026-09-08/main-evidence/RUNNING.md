# Combat food module revised author packet

Status: The revised source-only candidate is frozen. Runtime tests, remote sync, and product imports have not started.

Root review found that the first packet treated the rejected preview-only draft as the baseline. That exact packet is archived at `memory-bank/evidence/combat-food-module-pre-root-review-2026-09-08` with 23 copied files plus its archive manifest.

The branch baseline contains five definitions that move unchanged into `logic_pure/logic_pure_combat_food.py`: the default food tuple, consumption, loaded count, banked count, and loaded-food availability. Their source, AST, and prior namespace bindings are exact. The preview helper is new: it extracts the branch baseline's inline preview loop and exists only in the food module and engine. Supplies does not export it.

The focused runtime proposal contains nine selectors. Four existing combat tests cover consumption, loaded and banked food, auto-flee, and refill. Four narrow preview tests cover the new helper and full preview route. One narrow identity test checks the exact default tuple and every namespace that exposed the five moved definitions at the branch baseline.

The comparator still covers 15 complete preview return-or-exception cases and no longer accepts an unused output parameter. Its source preflight passes against the complete pinned inventory without product imports.

The installed source gate passes the revised candidate. The new module has 112 lines. The `logic_pure` directory has 27 Python files. The gate limits are 1,000 lines for a grown code file and 40 code files in one directory.

Root owns independent review and runtime. Root must inspect the frozen harness and run its inert safety checker before the harness can touch the remote mirror.

Root ran the inert harness safety checker after the packet freeze. All four safety-stop cases passed with zero remote calls and no product imports. Root's independent AST proof also passed. The retained results are `parent-inert-safety-check.json` and `parent-ast-proof.json`; product runtime remains unauthorized and unstarted.
