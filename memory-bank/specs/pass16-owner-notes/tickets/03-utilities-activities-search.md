# 03: Search bar on Utilities and Activities

**What to build:** The Utilities and Activities lists get the shared filter bar that the Skills target lists use. Typing filters the tree, opens the groups that hold a match, and shows an empty row when nothing matches. The current utility or activity never changes while the player types.

**Blocked by:** None (can start immediately)

**Status:** open

- [ ] Typing "bowl" in Utilities shows "Fill bowl with water" and hides non-matching rows; clearing the query restores the full tree.
- [ ] The Activities list has the same bar and behavior.
- [ ] Favourites, the context menu, the details stack and the landmarks group work on a filtered tree.
- [ ] Filtering leaves the selected action unchanged.
- [ ] Offscreen Qt capture at 560 px with clean text-fit checks; one play-checklist line.
