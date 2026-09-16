# Combat food module author packet

Status: The source-only candidate is frozen. Runtime tests, remote sync, and product imports have not started.

The rejected preview-only candidate is preserved unchanged at `memory-bank/evidence/combat-preview-food-file-growth-blocked-2026-09-08`. The retry boundary ruling is preserved at `memory-bank/evidence/combat-food-module-boundary-2026-09-08`.

This candidate moves the existing combat food priority tuple and five existing food helpers into `logic_pure/logic_pure_combat_food.py`. The engine calls the moved preview helper. The model and supplies modules directly re-export the names they exposed before the move. The helper definitions are source and AST identical to their pre-move forms.

The installed source gate passes the final candidate. The new module has 112 lines. The `logic_pure` directory has 27 Python files. The gate limits are 1,000 lines for a grown code file and 40 code files in one directory.

Root owns review and runtime. The frozen runtime harness accepts one lane and one job, stops on existing or racing pending work, pins the complete source inventory, and retains the remote identity before launch. Root must inspect and run the inert safety checker before the harness can touch the remote mirror.
