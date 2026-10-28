# 08: Bank rows never overlap

**What to build:** Find what gives the bank grid less height than its rows need with a bank the owner's size, and fix that cause, so every row and category heading keeps its full height and the grid scrolls. Also show the cut Bank Claims description line whole. Nothing else on the Bank tab changes. See spec "Bank rows"; the owner's save copy for local reproduction is `/Users/armantarkhanian/Code/ankiscape-pass18/native/owner-player-data.json` (never commit it), and the native look that reproduced the overlap is `/Users/armantarkhanian/Code/ankiscape-pass18/native/look-2/`.

**Blocked by:** None (can start immediately)

**Status:** open

- [ ] The cause is named in the commit message, with the measurement that shows it.
- [ ] With about 150 item kinds across the auto categories, at the default size, 560 points tall and full width, no two cells overlap and no heading overlaps a cell.
- [ ] The Bank Claims description line shows whole at the default size and 560 points tall.
- [ ] The orchestrator's native look with the owner's save shows no overlap in real Anki.
