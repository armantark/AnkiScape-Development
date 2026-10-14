# NPC-shop local reproduction — 2026-10-14

Status: blocked on inconsistent reproduction target and six live price-key differences; no digest implementation.
Main/source: 2fe9135819c85b04693f40ff5ed1a7ccd2973590; unchanged full generator, original exit0.
Local shop revision: 63ddf5c31c15d3da77c64ea2cd25bad6a5db2ee5; tree40956e744d6f482d5bdf910ad2e9aaa6b65a0289.
All274 top-level JSON blobs matched qualified hashes; snapshot SHA2564ca07f3b63d94f75489e2d41970b2597d62c92c15f8be76762c0ab4bb34ac742.
Only source-root path provenance normalized; generated output files remain unchanged.
First catalog semantic difference: /SHOP_COVERAGE_SUMMARY/player_sell_price_count: existing6820, generated6828.
First ledger semantic difference: /shops/3/stock_rows/1/item_name: existing"Bronze arrow", generated"Bronze arrows".
Summary matched after only its three source-root citations were normalized; this does not establish catalog/ledger equality.
No digest, output row/header, price, policy, baseline, test, audit, UI or source repository was changed.
Unblock: an approved reproduction contract that resolves stale derived records and the six live price-key differences while preserving required runtime values.
Evidence: /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/npc-shop/reproduction-1
receipt.json SHA2561b6af3bf6e37fcdda80cb831a93e36380770458bae2f80aeb57dc1f94ea6d925
comparison.json SHA256ce6ffb0a415cccf75ca78ac8e2a189cb6408d5928527bf53320bef77a4a4dc45
comparison-normalized.json SHA25636f7195438b55aa56b46f29e991deca0d1834ae7b4ec41e0069ed5f02d28d3ea
This is a per-slice source blocker; the whole goal remains active.

Independent input qualification finds6827 entries in each retained price map versus summary6820, and59 stale ledger names.
The full generator derives its summary from map length and copies catalog stock names to ledger; no input can satisfy both retained contradictions.
Six runtime keys differ: Bullseye lantern, Mining helmet, Mithril arrow, Oil lamp, Oil lantern and Spiked gauntlets.
All281 retained originals still match size/hash; no copied-through partial refresh substitutes for full source reproduction.
Qualification: /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/npc-shop/input-qualification-1
report.md SHA256bdbbef0c5bd7f3a2c97ff268825db85821f67884919635e13c6e98bfd20b0984
verdict.json SHA256fe0962deb408044a9d38bee924a9d6842e333a9647e8a98133d4c1766bba14f9
