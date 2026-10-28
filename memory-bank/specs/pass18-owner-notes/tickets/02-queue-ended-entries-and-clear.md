# 02: Ended entries leave the queue, and Clear always ends at Bankstanding

**What to build:** A done or stopped entry leaves the queue when it ends; the Event log keeps its line and the review HUD keeps the stop reason. The five places count only entries still to run. Clear queue always stops what runs, also a hand-started action, and switches to Bankstanding with "The queue was cleared." and no dialog; Resume offers what ran. A Pass 17 save that still holds passed entries loads with them dropped. See spec "Action queue: ended entries and Clear".

**Blocked by:** 01 (The queue makes exactly the count the player picks)

**Status:** claimed by Opus 5.5 implementer on goal/pass18-02-ended-entries-and-clear

- [ ] After an entry is done, the queue box no longer lists it and "Queue: n of 5" counts only the entries left; the Event log still reads "Queue: <name> done".
- [ ] A stopped entry leaves the box; its reason shows in the Event log and on the review HUD.
- [ ] With a plan waiting behind a hand-started Woodcutting, Clear queue ends at Bankstanding, no dialog, and the HUD offers "Resume Woodcutting".
- [ ] A finished five-entry plan frees all five places at once.
- [ ] A saved Pass 17 queue with an index past two done entries loads with only the remaining entries.
