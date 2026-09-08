# Carried processing reconciliation

## Settled scope and ownership

Author owns only pooled P5, branch `goal/carried-processing-reconciliation-2026-09-07`, lease `f24443365b33d0881b586a945ef823cd`, based on `0005e1cb42530706ab9ceb85e5be80ce3a0685f9`. Parent owns remote execution, review, composition, and promotion. P13 ownership has ended. Quest and roster remain ahead in promotion order.

Original `runtime/runtime_actions_carried_overlay.py` SHA256: `72dfdb810cc19a30337e1077dd31771dc30315a2e740e28e0f39944565a85484`. Extract only its processing inventory reconciliation at original lines 641-676 into one local pure helper. Keep handler invocation, callbacks, cadence, winter-storage rollback, travel, and persistence in the wrapper. No UI changes or broader refactor.

## Contract

Inputs are original bank, scoped inventory, post-handler inventory, post-handler carried view, the ordered recipe/presence/consumable requirement maps, and hidden potion/alternative sets. Return reconciled bank and carried view without mutating inputs. Preserve restoration differences for absent potions versus absent alternatives. Consume keys in recipe, presence, consumable order, including repeated keys. Preserve integer conversion, clamping, positive carried filtering, bank zero entries, handler results including explicit False, and callback/save ordering.

## Success criteria and evidence

Keep existing tests unchanged. Add focused contract tests and a frozen immutable-baseline differential probe with exact whole-source guards before product imports. Compare whole player state, return, ordered callbacks and save snapshots, handler calls, and RNG order. Cover success, rejection, inventory replacement, partial/no consumption, output/input overlap, hidden items, advanced presence, potions, repeated category keys, zeros, and a real handler priming/depletion/banking/refill sequence. Prepare pre-import stop canaries. Measure helper and wrapper with the unchanged installed gate; preserve gate source and thresholds. Human diff must remain at most 25 KB; machine evidence is separate.

## Execution boundary

No product imports, tests, or runtime have run in this slice. Local static AST/hash checks and gate measurement are permitted. No remote/network calls, model/agent calls, installs, Git mutations beyond later parent-authorized commit, baseline/pin/instrument changes, user saves, or external effects. Parent must supply independent review and runtime proof before authorizing commit. Missing focused/differential/full branch/composition/native proof remains explicit.

## Static preparation checkpoint — 2026-09-07

Helper `_reconcile_processing_inventory` and its one caller are authored. The ordered key tuple retains category duplicates. The helper receives the actual post-handler scoped dictionary, including in-place aliasing; it introduces no pre-handler copy. Removing this helper and restoring the original block reproduces the entire original source byte-for-byte.

Installed gate source SHA256 `41a91e5164b7bace435c7dc035fd51363bf3c5923dd727e85365644c19f9a70c` loaded CCN 15, cognitive 15, Halstead 80 with no overrides. Wrapper measured CCN 189 → 165, cognitive 267 → 229, Halstead 11.831521739130435 → 10.96951219512195. Helper measured 13 / 15 / 3.3846153846153846. Other new functions introduce no above-limit measurements. This is static API measurement, not a commit gate or behavior proof.

Evidence lives in `memory-bank/evidence/carried-processing-reconciliation-2026-09-07/`. `source-manifest.json.gz` SHA256 is `30f83b86b72eedfcef5667ef798eaa16f81292a30c457338ce4140fb2f8856cb`. It guards 904 source/config/evidence files before product imports. Frozen baseline is the full original module. Differential cases include in-place/replaced inventories, partial/no consumption, input/output overlap, explicit False/None/zero results, presence/potion/alternative handling, repeated categories, real winter-storage rejection rollback, child-cadence rejection, and a real Firemaking trip. Stop canaries install a product-import sentinel and attempt invalid manifest, changed-source and missing-source inputs.

No product import, test, canary or differential has executed. Parent must first review and run the pre-import canaries; then run the focused tests plus unchanged processing-wrapper tests and the pinned differential on its owned runtime host. Full branch, composition, independent review and shared native proof remain pending. No commit is authorized yet.
