Historical flat-layout record. Capture `9829` and the review below apply only
to the earlier flat paths. The current package layout and fresh verification
contract are in `shop-package-split-2026-09-05.md`.

# Shop domain split: author review record

Status: the author changes remain frozen after parent static proof, independent
review acceptance, and focused MacBook capture `9829` PASS. Full test lanes,
the normal promotion gate, and native interface acceptance remain pending. No
commit was created. A normal author commit was refused by the directory cap.
The parent controls all remote execution.

Baseline: `814b4d591df4525e0bda4a1f858baf6345ed4d38`.
The original shop source SHA-256 is
`faf88588cc138c54456ffcf05476113666a9869591f72fd48a168118696dda7f`.

## Module ownership

The shop module exceeds the owner file limit. The split gives state and service
operations their own modules while preserving the existing import surface.

| Module | Responsibility | Functions | Lines |
| --- | --- | ---: | ---: |
| `logic/shop_logic.py` | Views, search, purchase, sale, wilderness effects, dispatch, rollback, and existing imports | 14 | 611 |
| `logic/shop_state.py` | State, migration, access checks, stock, inventory, history, and diary counters | 39 | 613 |
| `logic/shop_services.py` | Services, vendor actions, potion decanting, and flask conversion | 18 | 658 |

Each source file is below 1,000 lines. The file hashes and all function locations
are in `shop-domain-split-2026-09-05/module-ownership.json` beside this record.

The existing module imports both parts. Services imports state. State imports no
shop module. The wilderness import remains local to its function.

All original imports stay in their original order. The existing module also
imports every moved function and constant under its original name, including
private helpers. All function bodies and constant expressions remain unchanged.
The stock maps and service maps use the existing imported objects.

Eleven moved public functions receive only an original-module metadata value.
Their execution globals must remain the real implementation module dictionary.
There are no wrappers, replacement globals, proxies, or new function objects.

## Static evidence and remaining checks

An author AST check confirmed all 71 function bodies once, unchanged, and found
no missing global names in the three modules. The changed Python files parse.
`git diff --check` passed. These are static checks; they do not prove runtime
behavior or public dump equality.

The read-only proof script is
`/tmp/verify-shop-domain-split-2026-09-05.py`.
Its SHA-256 is
`e47a57cb5a5c08c33ebe71e5a4993499389f24f717742009b20ba9bafc7a69dd`.
The parent reviewed and executed the complete script. It returned
`PASS_STATIC_ONLY`; the exact JSON is retained in
`shop-domain-split-2026-09-05/static-parent-proof.json`, with SHA-256
`f17d4aa5f460b9c9304567184908ce8a3f743bba74cd622e9ea3d72e07c67736`.
Focused runtime and public-payload verification passed as recorded below.
It takes the original source from
`/tmp/shop-domain-split-baseline-814b4d59.py`, checks the fixed baseline hash,
compares each function and constant, and reconstructs the original source bytes.
It also checks the actual proof-writer call sites and identifier counts without
importing add-on code. Its output reports static evidence only.

`tests/shops/test_module_boundaries.py` adds one test. Each shop part imports
first in a fresh process. The test checks native globals, the existing module's
function identities, public metadata, and shared map identities.

The existing proof-writer ownership test now names the service call in
`logic/shop_services.py`. Measured identifier counts are five in the existing
module and three in services. The proof store count remains 24 on this baseline.
The independent retained-proof repair changes that store count to 25; preserve
both changes when the branches are combined. The purchase and rollback call
sites stay in the existing module.

No surface pin, test gate, consumer, UI file, or proof-store implementation changes.
The full public dumps now match their baselines. Parent acceptance still
requires native checks, both full test lanes, the required audits, and normal
commit hooks.

## Focused behavior selectors

Run these through the parent-controlled test lane. The new boundary test checks
execution ownership; existing behavior tests carry the regression evidence.

```text
tests.shops.test_module_boundaries.ShopModuleBoundariesTest.test_parts_import_independently_and_keep_native_globals
tests.test_shop_logic.TestShopLogic.test_batched_view_models_match_one_call_per_shop
tests.test_shop_logic.TestShopLogic.test_saved_lantern_shop_rows_and_undo_events_migrate_exact_item_names
tests.test_shop_logic.TestShopLogic.test_buy_live_stock_records_event_and_rollback_restores_state
tests.test_shop_logic.TestShopLogic.test_restock_uses_market_tick_for_touched_shop
tests.test_shop_logic.TestShopLogic.test_services_vendor_actions_and_generic_transaction_wrapper
tests.test_shop_logic.TestShopLogic.test_bob_barter_preserves_doses_and_rolls_back_independently
tests.test_shop_logic.TestShopLogic.test_teplin_fills_only_new_six_dose_flasks_and_preserves_remainders
tests.test_shop_logic.TestShopLogic.test_teplin_decants_only_one_to_four_dose_flasks_into_vials
tests.test_shop_logic.TestShopLogic.test_wilderness_ambush_slots_trigger_damage_and_rollback
tests.test_shop_logic.TestShopLogic.test_gather_sell_buy_coin_loop_end_to_end
tests.test_quest_action_proofs.TestQuestActionProofIntegration.test_shop_purchase_proves_recovery_only_after_a_successful_buy
tests.test_quest_action_proofs.TestQuestActionProofIntegration.test_shop_purchase_rollback_retracts_its_proof
tests.test_quest_action_proofs.TestQuestActionProofIntegration.test_yak_hide_proof_requires_service_then_real_crafting
tests.test_quest_action_proofs.TestQuestActionProofWriterOwnership.test_production_proof_writers_are_genuine_action_seams
tests.test_world_clock_no_input_mutation
tests.test_storage_pure.TestStoragePure.test_v108_seeds_new_deed_outputs_and_preserves_durable_shop_counts
tests.test_storage_pure.TestStoragePure.test_migrate_legacy_shop_arrows_into_canonical_stacks
tests.test_achievement_diary_ledger_wiring.CurationLedgerWiringTest.test_shop_diary_mapping_matches_the_live_ledger_exactly
tests.test_achievement_diary_ledger_wiring.CurationLedgerWiringTest.test_shop_service_uses_its_service_id_for_durable_diary_credit
tests.test_item_reachability_audit.TestItemReachabilityAudit.test_inaccessible_shop_services_stay_blocked_with_reachable_inputs
tests.test_item_reachability_audit.TestItemReachabilityAudit.test_numeric_shop_service_gate_opens_at_reachable_partial_stage
```

Also run all of `tests.test_shop_logic` and the normal module-surface gate.
Use the existing native shop test for the unchanged browse and detail interface:

```text
tests.test_main_menu_widget.MainMenuWidgetTest.test_shop_opens_browse_first_and_detail_is_collapsible
```

For manual verification, open the shop browse view in the native test environment.
Buy an available stock item, check the history, and undo the purchase.
Run a potion exchange, then undo it. Check that inventory quantities return to
their initial values and that all visible labels remain complete.

## MacBook capture passed

The parent ran shop capture `9829` after the Pouch gate completed. The terminal
report is `PASS`, with completion time `2026-09-06T01:53:48.484800+00:00`.
Local copy session `25971` exited `0` and retained the complete top-level report
from `/tmp/shop-domain-split-bnvi5u5o`. Full shop gates and native acceptance
remain pending.

The prepared script is `/tmp/ankiscape-shop-domain-split-capture-2026-09-05.py`.
Its SHA-256 is
`deccfca3d8a376cc4b2358d1b1a9f7f9c225e0752d363c95f5ee5f0d9e71f4fb`.
The fixed bindings file is
`/tmp/ankiscape-shop-domain-split-bindings-2026-09-05.json`, with SHA-256
`0473ab356907c7fad08aa7fffcfd1034f4fa358f84248ea77e9a7fc8888c231a`.
The parent reviewed and executed these exact files. Their byte-exact copies
are retained as `capture-script.py.txt` and `capture-bindings.json` beside the
ownership record.

The bindings cover 37 source and test files. The script checks them before and
after every child command. It records command arguments, status, raw streams,
stream hashes, and checks in atomic report checkpoints. Any source mismatch,
failed command, missing named test, or changed public payload stops capture.
The `--source-hash-canary` option supplies one deliberately wrong expected hash;
it must stop before launching a runtime command and does not edit source.

Both retained discovery lists from source-bound baseline
`814b4d591df4525e0bda4a1f858baf6345ed4d38` contain 5,567 unique IDs. Their
raw SHA-256 is
`0cf05aa2519522896ae1435810c22cbe96d9894675711749cba5e1f96ecd211d`.
The capture requires only the new boundary test, then exact ordered equality
with the baseline after that ID is removed. It uses canonical `run_tests.py`
discovered IDs, which omit the leading `tests.` package prefix in the selector
list above.

Each lane executed all 24 named focused checks without skips, including native
module globals and proof-writer ownership. Each also ran all five existing
module-surface tests with one expected skip: the inner plain interpreter cannot
import the root without `aqt`. Its exact reason is:

```text
root initializer requires aqt; use the offscreen Qt interpreter
```

The Qt root-digest test passed in both surface-suite invocations.

| Environment | Focused tests | Focus duration | Surface tests | Surface duration |
| --- | --- | --- | --- | --- |
| Plain | 24, no skips | 15.537 s | 5, one expected skip | 11.839 s |
| Offscreen Qt | 24, no skips | 15.979 s | 5, one expected skip | 12.019 s |

The capture completed 29 child commands and 29 checks. All eleven plain and
twelve Qt public payloads match their full baseline bytes. Source hashes match
before and after every command. Discovery contains 5,568 IDs in both lanes,
with only the new boundary test added to the 5,567-ID baseline. Existing ID
order is preserved.

The parent independently checked the 29 commands, 37 source bindings, 58 raw
stream bindings, 23 complete payloads, and named test outcomes. The retention
pass repeated source/stream hash checks and full payload byte comparisons.
Every original top-level report file is retained under `remote-report/`. Large
JSON files and raw streams use gzip; `report-retention.json` binds both raw and
compressed bytes. All 67 files decompress or copy to the original bytes.
Raw report size is 126,938,323 bytes; retained report size is 12,247,093 bytes.
These checks read local files and did not rerun the add-on.

The frozen independent-review packet is at
`/var/folders/rt/xd67_cfj3jg9pkgkc0jnhk300000gr/T/shop-domain-split-review-2026-09-05-8zazyt13`.
It contains the complete tracked and untracked product/test diff, baseline and
candidate source, unchanged pins, the audit snapshot, parent static proof, and
prepared capture files. Its manifest SHA-256 is
`4199ea27f01b3acc1d5e9cedb7852782c43f35c4d765bcd5c5dff04428fe602a`.
The full product/test diff SHA-256 is
`024f060c8b62a2263b73e2f83ec503de6c483b8e3613bf16e8d8159820b6855a`.
The packet remains immutable as the accepted source-review record. Later documentation
updates do not change that source snapshot or imply runtime acceptance.

## Prepared driver and local guard canary

The driver is `/tmp/ankiscape-shop-domain-split-driver-2026-09-05.py`, with
SHA-256 `2be201d873f6a546a2a6519910f43e4514d367f706cd8d776a39376d441ec4a6`.
It binds canonical `tools/run_remote_tests.py` to SHA-256
`5de9414af35bb4688810d7d3f9b3331b205988b74a30706de6eca07af2de5e42`.
The parent approved the reviewed driver and repeated its local guard canary.
Pouch gate `9150` returned its terminal PASS receipt before capture. Shop
capture `9829` then passed. The parent now owns retained-proof full gate
`90613` on exact commit `66bcbc6fbc2482c87c78ef75ff5a440c83c5c85b`;
this evidence-retention pass issued no remote command.

It uses the canonical nonblocking mirror lock, pending-run reconciliation,
both preflights, verified capture uploads, one sync, and one canonical launch.
The canonical runner retains sole ownership of pending and completion records.
No custom pending-file deletion, restoration, or completion override is added.

The driver's local `--source-hash-canary` rejected the deliberate wrong source
hash before runner import or mirror-lock acquisition. The result
is `PASS`, with zero remote commands and all 37 source bindings unchanged.
The exact output is retained as `driver-local-canary.json` beside the ownership
record. That canary result proves only the local guard. The remote capture
subsequently passed as recorded above; its own remote-canary option was not run. The capture
and product/test files remain frozen.

## Independent review accepted

The parent read the complete Opus review `97188`, which returned `ACCEPT`.
The exact raw response is retained as `independent-opus-review.txt`, with SHA-256
`2979d3a2167311833b01644648833c6cc90f563429637652f3341f2410164691`.
`independent-review-resolution.md` records all three optional findings.

F1 and F2 require no test changes. The filename-based ownership selector is
independent of the native-globals property under test; selecting by globals
could hide an invalid function. The existing static and runtime identity checks
are sufficient, and conditional attribute checks would not catch absence.
F3 is applied in the matrix: parent static proof and independent review passed,
and the focused capture now passed. Full gates and native acceptance remain
pending.

The reviewer's unavailable Write call made no edit and needs no follow-up.
All product/test, capture, and driver files remain frozen. Normal author commit
`22501` failed with exit `1`: `logic` has 89 code files, compared with 87 at the
base, and the directory cap is 40. Exact hook output is retained in
`author-commit-hook-failure.txt`. No commit exists. The parent approved the
direction of a coherent `logic/shop/` package; the concrete source rewrite
still awaits review. Current capture evidence remains valid for the current
frozen layout and becomes historical evidence after that rewrite. New source
bindings, independent delta review, and a fresh capture will then be required.

The raw accepted source diff is retained as `product-and-tests.diff.gz`. Gzip
decodes to the original SHA-256
`024f060c8b62a2263b73e2f83ec503de6c483b8e3613bf16e8d8159820b6855a`.
This resolves eight staged whitespace warnings caused by raw diff context
lines without altering evidence bytes. The exact check output is retained in
`staged-whitespace-failure.txt.gz` and recorded in the papercuts log.
