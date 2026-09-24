# Dream transaction boundary: retained selection evidence

The root selected the three-input Dream transaction boundary. This is architectural selection only. The Magic module prerequisite is unlanded. No Dream implementation is authorized, and this packet establishes no gate result.

## Contract and evidence

Use the [revised contract](contract.md) for the selected boundary. The [original contract](contract.before-review.md), [raw Opus review](SUMMARY.md) and [review stderr](SUMMARY.md) remain unchanged. The [manifest](SUMMARY.md) binds each exact retained file to its source path, byte length and SHA-256 hash.

The root checked the source block and corrected the review before it supplied the revised contract. The author of this packet copied and hashed the supplied files only. The source-complexity measurements in those files are attributed selection evidence, not measurements repeated by this documentation slice.

## Root corrections to the raw review

- `data.get("inventory", {}) or {}` normalizes falsy inventory values only. It does not normalize an arbitrary truthy non-Mapping. Preserve the existing downstream behavior.
- The engine reaches Magic behavior indirectly through `logic_pure_combat_model` today. The raw review does not prove a direct engine-to-Magic-module import. Preserve the dependency direction and require the accepted Magic module first.
- Affordability uses sanitized values, but debit remains raw `inventory[rune] -= amount`. Preserve missing-key and incompatible-value behavior; do not add a guard or generalize all non-integer values as failures.
- The helper mutates the supplied data in place and returns one result object. The engine stores that object directly in `combat_last_result` and returns the same object. Preserve debit order and no-write behavior when unaffordable.

The revised contract also preserves the transaction's zero lifepoint default, distinct from the caller's maximum-lifepoint eligibility default. The caller keeps the unconditional maximum read, eligibility, cost calculation, final-result write and early tuple return.

## Acceptance limits

Opus accepts the architectural boundary, not an implemented change. Its raw comments are preserved as review data; the revised contract contains the root's corrections. The Magic prerequisite must land before Dream implementation can be authorized. The unchanged gate must then measure any exact helper; no future pass is predicted.

The gathering Drop boundary remains fallback evidence only. Neither the fallback nor this packet creates an authoring assignment. P4's full gate continues under root ownership with no passing result claimed here. There is no whole-goal block.
