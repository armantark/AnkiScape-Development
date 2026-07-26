# Placeholder values

Status: **live register.** Every placeholder in the codebase appears here, and
`tests/test_placeholder_register.py` fails if this file and the code disagree.

A placeholder is a value the period game had and we could not recover without an
intense dig. It exists so the mechanic around it can ship complete. It is not an
invention: an invention is a value the period never had, and those still wait.

Authority: `pre-eoc-source-verification-standard.md`, "Breadth-Phase
Placeholders".

## How to add one

1. Mark the value in code: `# PLACEHOLDER(<id>): <what would settle it>`
2. Add a row below with the same id.
3. Run `python3 -m unittest tests.test_placeholder_register`.

## Register

| id | value | family it unblocks | what would settle it |
| --- | --- | --- | --- |
| `duel_arena_cap_thresholds` | Duellist's cap tiers unlock at 0, 10, 100, 500, 2,000, and 5,000 wins | Duel Arena | A pre-`2012-11-20T00:00:00Z` server/config source or dated page that states all six thresholds. The current fallback is the six near-cutoff wiki tier revisions created about five hours after the cutoff; rev-742 and both emulator lineages prove the six item tiers but not the win counts. |
