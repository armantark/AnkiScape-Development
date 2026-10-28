# 03: The queue box shows every entry, folds, and confirms each add

**What to build:** The queue box has no scroll bar and is as tall as its one to five entries; the tab page above gives up the height. Its title line folds and unfolds it; it starts open and remembers the fold. Each add highlights the new row for about 1.5 seconds and the Add button reads "Added ✓ (n of 5)" for the same time. Each refused add names its real cause. The hint leaves no single word on its last line. See spec "Queue box and add feedback". Ticket 10 sets the final copy.

**Blocked by:** 02 (Ended entries leave the queue, and Clear always ends at Bankstanding)

**Status:** done

- [x] With 1, 3 and 5 entries at the default size and at 560 points tall, every row shows and no scroll bar appears; a long entry wraps whole.
- [x] A click on the title line folds the box to that line; a second click unfolds it; the fold survives closing and reopening the menu.
- [x] After an add, the new row is highlighted and the button reads "Added ✓ (n of 5)"; both return to normal after about 1.5 seconds.
- [x] Queue full, nothing chosen, a locked or complete quest, and a count below 1 each show their own text.
- [x] Offscreen screenshots, dark and light, 560 points tall; the orchestrator's native look shows the same in real Anki. (Offscreen part done; the native look is open.)
