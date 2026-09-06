# Source audit friction

2026-09-06T01:33:40.251227+00:00 — Source lookup used a guessed `Server/data/configs/item/items.yml` path and a shortened `/Users/ArmanTarkhanian1/Documents/2012scape` path; both failed. Exact retained roots are `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml` and `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/`.
2026-09-06T01:39:45.104739+00:00 — The current `Silvthrill rod` Wiki title has no pre-cutoff revision; `redirects=1` resolves `Silvthril rod`, oldid `6359850`. Raw negative and redirected responses are retained.
2026-09-06T01:39:45.104762+00:00 — A guessed `data/quest_catalog.json` path did not exist and an unmatched shell `data/item_catalog*` glob failed; use `generated/quest_catalog_generated.py` with static AST extraction.
2026-09-06T01:39:45.104764+00:00 — Retained cache evidence differs by packet: Fremennik rows are under `selected_row_sets/<hash>/definitions`, not `rows`; initial normalization raised `KeyError: rows` before any product change.
2026-09-06T01:43:18.972627+00:00 — `git rev-parse HEAD` under `/Users/ArmanTarkhanian1/Downloads/game-main` returned `fatal: not a git repository (or any of the parent directories): .git`; this retained extraction has exact file hashes but no available checkout commit.
