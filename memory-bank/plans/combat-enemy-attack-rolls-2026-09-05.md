# Combat enemy attack rolls

The approved scope is one deterministic calculation shared by initial combat setup and each selected enemy attack. Base: `0af0b0d5492fd8415c7eb52dba80c886691c5fa0`. This source worktree owns the engine, missing focused coverage, comparison probe, and its evidence. The orchestrator owns runtime authorisation, review, and promotion.

## Contract

Add one private helper in the existing combat engine. Inputs are current player data, enemy, player combat class, player style ID, prepared player totals, prepared enemy totals, prepared prayer effects, enemy attack factor, weakening equipment mapping, and weakening active flag. Return exactly the enemy attack roll, player defence roll, enemy accuracy, and enemy maximum hit.

Reuse existing formula functions and preserve arithmetic order. Resolve enemy style within the calculation; magic-melee uses Attack and stab bonus against magic defence. Preserve the existing maximum-hit resolver call. Read current player defence on each call. Keep totals and prayer effects prepared by the burst. Sample weakening equipment once before initial calculation and pass the same mapping and flag to later calls.

Keep initial accuracy calculation even when no retaliation occurs. Keep attack selection and selected-style overrides in the caller. Live rescaling still receives both raw rolls. RNG, damage, protection, special attacks, encounter state, and control flow remain in their existing callers. Leave pressure attacks and public interfaces unchanged. Do not add a context object or general framework.

## Acceptance

Freeze the exact base engine and retain its hash. Reuse existing focused tests and add only missing coverage. A bounded differential probe must compare complete returned player/result values and RNG state/calls across initial reporting, style overrides and early exits, maximum-hit branches, weakening, changing defence, live curse/prayer/spell effects, and special damage bypasses. Avoid a Cartesian matrix.

Retain a portable explicit source inventory. Correct and wrong source preflight must finish or stop before product imports. Local work is limited to static parsers/analyzers and preflight until the orchestrator transfers the MBP mirror. Human review diff must be at most 25,000 bytes; machine evidence is separate. Parent full diff review, cross-lineage review, authorised runtime, normal commit hooks, both full lanes, and merged-tree checks remain required. Focused comparison alone is not full acceptance.

## Runtime checkpoint 2026-09-07

The approved scope remains unchanged. Focused and differential checks passed in both lanes; retained raw evidence is indexed by `memory-bank/evidence/combat-enemy-attack-rolls-2026-09-05/runtime/manifest.json`. This checkpoint does not close cross-lineage review, full branch lanes, commit hooks, merged-tree checks, or parent native acceptance.
