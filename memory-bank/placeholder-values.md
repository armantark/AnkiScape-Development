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
