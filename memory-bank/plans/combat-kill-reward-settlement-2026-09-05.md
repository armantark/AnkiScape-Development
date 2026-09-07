# Combat kill reward settlement

The owner prioritised responsibility splits and simplification on 2026-09-05. This slice removes the duplicated reward settlement from the two kill paths in the combat burst. It preserves behavior.

## Contract

Keep the burst function at its current path. Add one private function in the same combat engine module for kill reward settlement. Pass the player data, enemy, target ID, RNG, pending drops, and XP reward mapping. Return the updated player data, this kill's clue refusal, and prayer delay. The caller retains the first refusal and advances its attack clock. The function updates the existing pending drop and XP mappings, which remain owned by the burst. Do not introduce a state bag or claim exclusive ownership of XP: attacks also add XP.

Preserve operation order: roll drops using ownership that includes pending drops; apply triple charms; record observed drops before prayer interception; apply prayer kill effects; aggregate prayer XP; accumulate retained drops. Keep kill counters, stop conditions, respawn, regeneration and retaliation resets in their existing callers. Preserve the distinct reset behavior of the two kill paths. Preserve RNG calls and consumption. Do not change public signatures, pins, tests as instruments, UI, or mechanics.

## Ownership and acceptance

The combat implementation agent owns the combat engine change, focused behavior coverage, and this slice's evidence and Memory Bank notes in this worktree. The orchestrator owns review and promotion. No other agent writes these files.

Compare baseline and candidate whole returned results, player data, and RNG state for direct and reflected kills, both cadences, multiple kills, clue ownership and refusal, charms, observed drops and prayer interception. Use existing test coverage where it establishes these cases. Add only missing high-signal coverage. New functions must satisfy the installed complexity limits; the existing burst must shrink without moving its ratchet identity. Retain raw comparison evidence and source hashes. Run runtime checks on the MBP only after the orchestrator transfers mirror ownership. Both full verification lanes, repository checks, independent cross-lineage review, normal commit hooks and merged-tree promotion are required for acceptance.

## Execution

2026-09-06: The orchestrator created the guarded worktree from published main 518a651db9e12e80ae9a1fd6e2b7b11c7357b360. Static authoring can proceed while the shop gate owns the MBP. No local product runtime or remote sync is authorised yet.
