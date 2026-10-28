# 03: Action queue engine

**What to build:** A pure queue saved in the profile: up to five entries, each an action in the last action shape (ticket 02) and a target count in that action's unit; a current index, the current entry's done count and a paused flag. Skill, utility and activity entries count the review's gain of the action's output item from the review item changes (ticket 01); combat counts kills; a quest entry has no count and ends when the quest stops. After each review the runtime advances the queue: an entry that reaches its count starts the next one. When the runtime is about to switch to Bankstanding for a missing material or requirement, the queue gives that entry's notice and starts the next entry; only a finished or empty queue lets the switch to Bankstanding happen, with the usual notice. A manual Stop pauses the queue, Resume continues the current entry, Clear empties it. The queue never repeats. No panel in this ticket; ticket 04 builds it.

**Blocked by:** 01 (Review item changes), 02 (Last action record and Resume)

**Status:** done

- [x] Pure tests: advance on count, pass on shortfall with a notice, pause and resume, clear, the five-entry cap refuses a sixth, no repeat after the last entry.
- [x] Real review handler: a three-entry chain (mine iron ore, smelt, smith) runs through its counts, passes an entry that runs short, and ends at Bankstanding with the notice.
- [x] A quest entry ends when its quest stops and the next entry starts.
- [x] The queue survives a profile reload.
