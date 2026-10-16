# 07: Slayer master picker

**What to build:** The recorded owner decision 6 in the Slayer contract: the Masters tab shows one card per live master with name and chathead; an ineligible master is greyed with each unmet requirement stated. Mazchna needs combat level 20 only, because Priest in Peril stopped gating Morytania in March 2012. "Get assignment" uses the last eligible master the player used. A locked master refuses a task everywhere.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] At combat level 20 or more, the Mazchna card is enabled and gives a Mazchna task through real reviews.
- [x] Below combat 20, Mazchna is greyed with "Combat level 20"; Vannaka is greyed with "Combat level 40" below 40.
- [x] The assignment command refuses a locked master even when called directly.
- [x] The Assignment tab button and empty state name and use the last eligible master, else Turael.
- [x] The stale "More masters unlock..." note is gone.
- [x] Mazchna's Priest in Peril requirement is removed; the source audit and its test cite Priest in Peril oldid 6487728 and Mazchna oldid 6548393. The stale "remain hidden" Kanban text is corrected.
- [x] Offscreen Qt capture of the Masters tab at 560 px with clean text-fit checks; one play-checklist line.
