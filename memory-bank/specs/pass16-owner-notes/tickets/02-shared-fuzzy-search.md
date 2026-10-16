# 02: One fuzzy, ranked search for every search bar

**What to build:** Every search bar (Skills target lists, Quests, Bank, Grand Exchange, shops, Help, Achievements, Collections) uses one pure matcher. It ranks exact name, then name prefix, then all tokens in the name, then tokens in metadata, then fuzzy matches. "tara" finds the tiaras, and "Stolen Hearts" is the first quest result. See the spec's Search matcher decision.

**Blocked by:** None (can start immediately)

**Status:** claimed by sol-02

- [ ] Typing "tara" in the Crafting target search shows "Tiara"; in Runecrafting it shows the tiara rows.
- [ ] Typing "Stolen Hearts" in the Quests tab shows Stolen Hearts first; quests that only list it as a requirement follow.
- [ ] With a query present, the chosen quest Sort orders results inside each match tier; with no query, the Sort alone orders them.
- [ ] Tokens shorter than four characters match only as substrings; a near miss outside the fuzzy rule is not shown.
- [ ] Bank, Grand Exchange and shop searches use the same matcher; no second matcher remains.
- [ ] Each search still updates on every keystroke without a visible delay on the largest list.
