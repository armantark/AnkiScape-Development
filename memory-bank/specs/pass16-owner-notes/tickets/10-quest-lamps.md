# 10: Quest lamps

**What to build:** Quest lamps follow the spec's Quest lamps decision. The quest-complete message names the lamps now waiting in Bank Claims, with count and XP. A lamp with exactly one allowed skill reads "Claim" and pays that skill with no grid. A choice lamp keeps the select-then-confirm grid. Every lamp row has "Destroy", which asks for confirmation with the 2012 destroy warning and forfeits the lamp for good; Undo restores it. The Elder Kiln lamp needs level 75.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] Completing Stolen Hearts through real reviews shows a message that names its waiting lamps.
- [x] The Stolen Hearts Agility and Thieving lamps and the Myths of the White Lands Agility reward pay on "Claim" with no dialog.
- [x] A choice lamp opens the grid even when only one allowed skill meets the minimum.
- [x] Destroy asks for confirmation; on confirm the row leaves Bank Claims and never returns; Undo restores it.
- [x] The Elder Kiln lamp needs level 75.
- [x] Offscreen Qt capture of Bank Claims rows and the confirmation at 560 px with clean text-fit checks; one play-checklist line.
