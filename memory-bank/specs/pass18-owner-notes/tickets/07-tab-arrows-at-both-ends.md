# 07: One tab arrow at each end of the tab bar

**What to build:** The top-level tab bar keeps Qt's own scrolling, but "<" sits at the left end and ">" at the right end, with the tabs offset by the arrow's width so no tab sits under an arrow. Each arrow is disabled at its end, and the selected tab always scrolls fully into view. See spec "Tab arrows" and code facts B section 3, option 1.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] At menu widths 720 and 980, the left arrow is at the bar's left end and the right arrow at its right end; scrolled fully either way, no tab overlaps an arrow.
- [x] At the first tab the left arrow is disabled; at the last, the right arrow is.
- [x] Selecting each of the 11 tabs leaves it fully visible.
- [x] The tab-bar test checks positions under the product style instead of replacing the style.
- [x] The orchestrator's native look shows the arrows at both ends in real Anki.
