# 09: XP drops carry tenths as whole numbers

**What to build:** Each XP drop shows, per skill, the change in that skill's whole-number total across the review, so tenths carry forward: four 4.5 XP burials read +4, +5, +4, +5. A skill whose whole number did not change is left out; a review with no change shows no XP drop. The popup, the event log and the Qt fallback show the same text. Stored XP stays exact.

**Blocked by:** None (can start immediately)

**Status:** claimed by sol-09

- [ ] Four real Bury reviews from a total ending in .0 show +4, +5, +4, +5, and the stored Prayer XP grows by 18.0.
- [ ] A combat review that gains 0.8 Attack XP without crossing a whole number shows no Attack entry.
- [ ] Multi-skill drops keep their per-skill breakdown with whole numbers.
- [ ] The event log entry equals the popup text.
