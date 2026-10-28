# 03: One Gather row replaces the 31 free-pickup rows in Utilities

**What to build:** The Utilities list hides the 31 free-pickup rows and shows one Gather row in the Gathering group. Its detail box lists the 31 items with icons, and the player picks one; Start and Add to queue run the picked row's existing action, so ids, saves, queue entries, Resume and quest supply steps do not change. Search finds the Gather row by item name. Quest-gated pickups show their lock. Opus writes the menu text. See spec "The Gather row".

**Blocked by:** None (can start immediately)

**Status:** not started

- [ ] Utilities shows one Gather row and none of the 31 free-pickup rows.
- [ ] Queuing "Gather Redberries" ×10 gives 10 Redberries over the expected cards.
- [ ] Searching "banana" shows the Gather row with Bananas picked.
- [ ] A save whose current action is `pick_bananas` resumes it, and Resume names "Gather Bananas".
- [ ] Goblin Diplomacy still completes from raw supplies in 10 quest reviews.
- [ ] Grab Desert Phoenix feather shows its quest lock in the picker and cannot start.
- [ ] The frontend-taste review approves the detail box, and the native check finds no truncated text.
