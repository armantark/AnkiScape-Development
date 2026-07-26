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
| `daily_challenges.reward_xp` | 100 XP per level of the challenge's level requirement | Daily Challenges | The cutoff page says a completed challenge grants "extra experience" but states no amount, and no recovered Darkan or cache table holds the per-challenge reward. A Darkan challenge-reward table or the cache's challenge config would replace it. |
| `daily_challenges.assignment_weights` | uniform draw over the eligible pool | Daily Challenges | The period picks the new challenge from the pool the player qualifies for; the relative weights inside that pool are server behaviour no recovered source states. Darkan's challenge assignment code would replace it. |
| `treasure_trails.easy_step_count_distribution` | uniform over 1 to 5 steps | Treasure Trails | The pinned page states the range ("Easy trails can be between 1 and 5 clues long") but not the shape inside it, and Darkan's `1 + Utils.random(3)` cannot reach five, so the reconstruction cannot settle it either. A cache-side trail-length script or a corrected Darkan roll would. |
