# 01: Review item changes in the event log and popup, with repeats collapsed

**What to build:** After each review, the event log's XP line lists what the review made and used, gains first: "+62 XP · Smithing · +2 Iron bar · −4 Iron ore"; a potion drunk shows as "−1 Antipoison (3)". The XP popup shows only the product gain, for example "+2 Iron bar". Identical rows next to each other with the same review age collapse into one row ending " - x5", with only "x5" in a new muted orange from the event-log tone set, legible in dark and light themes. Rows of different review ages never merge. The item changes come from one new pure function that compares the before-review save with the after-review save (Bank and carried pack), which ticket 03 reuses for queue counts.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] The pure item-change function returns signed counts for Bank and carried pack together, and an empty mapping for a review that changed no items.
- [x] A real smelting review through the review handler shows its XP line with the bar gained and the ore used.
- [x] Five identical "The ore was too impure" rows of one review show as one row with " - x5"; two such rows of the next older review show as a separate row with " - x2".
- [x] The popup shows the product gain only.
- [x] Offscreen event log captures at 560 points tall, dark and light, with `text_fit_defects` clean; one play-checklist line added.
