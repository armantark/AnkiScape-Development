# 05: Mix dyes from the Bank, and mix green and purple in Utilities

**What to build:** Utilities gains "Mix green dye" (Blue + Yellow) and "Mix purple dye" (Blue + Red) beside "Mix orange dye", citing the Dyes revision 5953125 quote. The Bank's right-click menu on a dye gains "Mix with", listing each held dye that mixes with it and the result; a click mixes one pair at once, no card, as one Edit > Undo step, from the same recipes as the Utility rows. See spec "Dyes".

**Blocked by:** None (can start immediately)

**Status:** claimed by GPT-6.1 Sol implementer on goal/pass18-05-dye-mixing

- [ ] Searching Utilities for "dye" shows Mix orange, Mix green and Mix purple, each with its two inputs.
- [ ] Right-clicking Red dye with Yellow dye and Blue dye held shows "Mix with" entries for Yellow (Orange dye) and Blue (Purple dye); with no partner dye held, no "Mix with" entry shows.
- [ ] One click turns one Red dye and one Yellow dye into one Orange dye; Edit > Undo restores both.
- [ ] Offscreen screenshots of the menu, dark and light; the orchestrator's native look shows it in real Anki.
