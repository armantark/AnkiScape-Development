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
| `skeletal_horror.shared_bonuses` | Empty bonus map | Skeletal Horror | Exact values from the revision-727 `developer-information/npcListBonuses.txt` row, corroborated by a symbolic cache/server definition |
| `skeletal_horror.phase_320_stats` | Attack 320, Strength 320, Defence 320, Magic 320 | Skeletal Horror | An authentic combat definition or period server script for NPC 9176 |
| `skeletal_horror.phase_260_stats` | Attack 260, Strength 260, Defence 260, Magic 260 | Skeletal Horror | An authentic combat definition or period server script for NPC 9177 |
| `skeletal_horror.phase_180_stats` | Attack 180, Strength 180, Defence 180, Magic 180 | Skeletal Horror | An authentic combat definition or period server script for NPC 9178 |
| `skeletal_horror.phase_100_stats` | Attack 100, Strength 100, Defence 100, Magic 100 | Skeletal Horror | An authentic combat definition or period server script for NPC 9179 |
| `skeletal_horror.magic_style_chance` | 0.5 | Skeletal Horror | The authentic Skeletal Horror combat script or selector weights for Melee versus Magic |
| `duel_arena_cap_thresholds` | Duellist's cap tiers unlock at 0, 10, 100, 500, 2,000, and 5,000 wins | Duel Arena | A pre-`2012-11-20T00:00:00Z` server/config source or dated page that states all six thresholds. The current fallback is the six near-cutoff wiki tier revisions created about five hours after the cutoff; rev-742 and both emulator lineages prove the six item tiers but not the win counts. |
| `tears_of_guthix.tears_per_tick` | 1 tear per tick | Tears of Guthix | The authentic cavern collection rate. The period article reports 267 tears at 316 quest points, which caps at 300 ticks, so the true rate is at most about one per tick — but it states no rate |
| `tears_of_guthix.green_tear_chance` | 0.055 | Tears of Guthix | The authentic stream-switch timing and the roll for catching a green tear. Derived only as the share that turns 300 ticks into the reported 267 net tears |
| `daily_challenges.reward_xp` | 100 XP per level of the challenge's level requirement | Daily Challenges | The cutoff page says a completed challenge grants "extra experience" but states no amount, and no recovered Darkan or cache table holds the per-challenge reward. A Darkan challenge-reward table or the cache's challenge config would replace it. |
| `daily_challenges.assignment_weights` | uniform draw over the eligible pool | Daily Challenges | The period picks the new challenge from the pool the player qualifies for; the relative weights inside that pool are server behaviour no recovered source states. Darkan's challenge assignment code would replace it. |
| `crucible.rank_point_thresholds` | Promotion at 1, 3, 6, 10, 15 and 25 rank points | The Crucible | Rev-727 script 6284 proves the tier list exactly but receives an already-computed tier and reads no varp, so the thresholds are server-side. The pinned article says only that "every few rank points" raised a rank. A period rank table or a decoded server routine would settle it. |
| `crucible.points_per_kill` | 1 rank point | The Crucible | The launch update says points were earned "for every target slain" without a number, and rev-727 script 6288 only renders an already-computed delta. The one exact point rule that *is* sourced — one point per successful hit on the Supreme Champion — is shipped as a real constant, not a placeholder. |
| `crucible.bones_per_kill` | 2 Trophy bones | The Crucible | Both pinned revisions say vanquished players dropped Trophy bones and that they are the Crucible's reward currency, but neither states the quantity, and no recovered cache enum holds it. |
| `crucible.lesson_bone_award` | 1 Trophy bone per lesson | The Crucible | The article and the item page both state the four-lesson cap of "one set of Trophy bones" each without ever stating the set size. |
| `crucible.risk_expectation_per_level` | 400 coins per combat level | The Crucible | Rev-727 interface 1298 states the fee shape exactly — `F = (X - Y) + Z` — but holds placeholders rather than constants for X. The single recorded figure, 518,000 coins refunded to a maxed player carrying nothing, comes from a money-pouch exploit report and is not a fee schedule. |
| `crucible.abandonment_fee` | 5,000 coins | The Crucible | The flat Z component is stated to exist and to be paid to the opponent on abandonment, and rev 742 carries a "Get fee" bank option, but no source gives it a value. |
| `treasure_trails.easy_step_count_distribution` | uniform over 1 to 5 steps | Treasure Trails | The pinned page states the range ("Easy trails can be between 1 and 5 clues long") but not the shape inside it, and Darkan's `1 + Utils.random(3)` cannot reach five, so the reconstruction cannot settle it either. A cache-side trail-length script or a corrected Darkan roll would. |
