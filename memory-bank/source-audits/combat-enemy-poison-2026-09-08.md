# Enemy poison extraction evidence — 2026-09-08

## Boundary

The engine keeps positive enemy poison-damage normalization and the truthy potion-event append after automatic food consumption. The existing specials module owns the positive gate, one float-converted RNG draw, the unchanged TypeError/ValueError fallback, poison application, the status write, and antipoison consumption. The status write precedes consumption. Existing private exports remain.

Root verified whole-engine and specials AST inverse equality. The helper is exact except that it returns the antipoison event. Root found no later potion_event consumer and verified the model chance is exactly 0.4; the frozen threshold case tests that boundary. No UI, RNG policy, gameplay rule, callback, wrapper, new module, or fallback was added.

## Verification

Evidence directory: `memory-bank/evidence/combat-enemy-poison-2026-09-08/`.

- `source-static-report.json`, `source-static-raw.json.gz`, and `source-static-measure.py.gz` retain reproducible source-only metrics, tool pins, file-growth checks and directory module counts. All fixed ratchets pass. The initial E303 failure and authorized whitespace correction remain recorded separately.
- `parent-proof-retention.json` binds the exact parent AST, inert safety, and five source-guard results. No product import attempt occurred in the source-guard verification.
- `final-opus-review-retention.json` binds the exact review input, retry command, outputs and parent resolutions. Opus session 20073 approves the poison slice.
- `runtime-retention-manifest.json` binds all 42 files from the four parent-run jobs. `parent-runtime-verification.json` records exact run identifiers and results. Plain and Qt each passed three focused tests with zero skips and twelve complete differential cases. Root checked complete pickle bytes and restricted-decoded structures, exact RNG traces, route outcomes, nonmutation, and all 1263 source pins.

These runtime measurements are dated parent evidence. This author did not run product code or remote commands. The full branch gate, post-merge gate and native programme acceptance remain pending. The source is not landed. The handoff contains the remaining manual instructions.
