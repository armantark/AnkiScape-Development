# 04: Queue panel

**What to build:** The player builds and watches the queue from the main menu: an "Add to queue" control beside each Start control in the skill, utility, activity, quest and combat lists; a count box whose default is the most the Bank allows now, which the player can type over; a compact queue list with the current entry, its done count, and Clear. The place and look come from the hill-climb loop (spec, "The hill-climb loop"), task: "queue 100 iron ore then smelt them into bars, then clear the queue". The count box ignores the mouse wheel (ticket 05).

**Blocked by:** 03 (Action queue engine), 05 (Mouse wheel guard)

**Status:** open

- [ ] Adding, counting, the five-entry cap, and Clear work through the real widgets offscreen.
- [ ] The default count equals the most the Bank allows for that action now.
- [ ] Hill-climb rounds recorded; the probe passes and the taste vote approves, or five rounds end with the best candidate reported.
- [ ] Offscreen captures at 560 points tall, dark and light, `text_fit_defects` clean; one play-checklist line added.
