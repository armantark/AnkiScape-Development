# 09: Wicked hood withdraws all its essence to the Bank

**What to build:** "Withdraw essence" moves the hood's whole remaining daily allowance into the Bank in one click; the Bank menu label and the Runecrafting card's tooltip say so. The daily amount stays 100 plus 25 per Runespan robe piece, up to 175. The refill text reads the player's world-day length in place of the fixed "240". Altar access does not change. The play checklist's hood feeding line loses its undo step, and every remaining play-checklist undo step says "Edit > Undo (Cmd+Z)".

**Blocked by:** None (can start immediately)

**Status:** done

- [x] A real withdrawal moves 100 essence into the Bank and leaves 0; a second withdrawal the same world day moves nothing.
- [x] The refill text shows 100 for a profile whose world day is 100 cards.
- [x] The existing hood pack tests still show 28 essence for a worn hood and 27 for a packed hood.
- [x] The play checklist names "Edit > Undo (Cmd+Z)" wherever it uses the undo.
