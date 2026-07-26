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
