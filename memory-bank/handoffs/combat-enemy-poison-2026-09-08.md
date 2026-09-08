# Enemy poison extraction

## Change

The existing specials module owns the positive poison gate, one float-converted RNG draw, the unchanged TypeError/ValueError fallback, poison application, the status write, and antipoison consumption. The engine keeps enemy damage normalization and the truthy potion-event append at the same location after food. The status write precedes consumption. Existing engine private exports remain. No UI or gameplay rule changed.

## Accepted evidence

Root accepted the independent review and all four focused/differential runtime jobs. Plain and Qt each ran three focused tests in 0.003s with zero skips and compared twelve complete payload pairs. Root verified pickle-byte equality, RestrictedUnpickler structure equality, exact RNG draws/counts, route outcomes, input nonmutation, and all 1263 source bindings before and after execution. These are dated parent-run results, not a rerun by this author.

The exact 42 runtime files are retained under `memory-bank/evidence/combat-enemy-poison-2026-09-08/runtime/`. `runtime-retention-manifest.json` binds each stored and decoded artifact; `parent-runtime-verification.json` records exact run identifiers and results. The same evidence directory retains source-only measurements, instrument pins, raw analyzer output, AST inverse proof, source-guard checks, inert safety proof, and the fixed runtime protocol. All static metric, layout, file-growth and module-count ratchets pass.

## Review resolution

Opus session 20073 approves the poison slice. Root verified that the helper preserves the original statements except for returning the antipoison event. Whole-function AST inspection found no later consumer of the caller's potion_event local. The model chance is exactly 0.4, so the frozen threshold test checks the exact boundary. The source guard already verifies the baseline specials bytes. No additional fallback, import removal, test change or report field was required. Exact review inputs, outputs and resolutions remain in `final-opus-review-retention.json`.

## Remaining work

Full branch and post-merge gates remain pending. The source is not landed; native programme acceptance remains unproven. Root owns gate execution and promotion.

On the approved loaded add-on, use a poisonous target and a loaded Antipoison (1). Observe poison application followed by one automatic cure, the expected vial replacement, and no duplicate potion event. Repeat without antipoison and with active immunity. Confirm the displayed state agrees with the stored status and dose changes. This native check remains unperformed. Run only after the parent approves the native test environment; this author has no runtime ownership.
