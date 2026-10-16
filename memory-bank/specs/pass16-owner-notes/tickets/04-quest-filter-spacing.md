# 04: Even spacing under the quest search bar

**What to build:** The filter row under the quest search bar sits on one spacing scale: items centred on each line, each label next to its box, checkboxes and boxes aligned. Opus 5.5 authors this ticket at the owner's request ("Fix it with Opus 5.5").

**Blocked by:** None (can start immediately)

**Status:** open

- [ ] A before capture of the Quests tab at 720 px wide and 560 px tall is saved with the ticket evidence.
- [ ] After the change, the checkboxes and label-and-box pairs share one baseline per line, and the gaps follow one scale.
- [ ] Every other surface that uses the shared filter bar or flow layout (Shop, Grand Exchange, Achievements, Help, skill target bars) is recaptured and shows no regression.
- [ ] The Bank and Quests 720 px fit test still passes; text-fit checks are clean.
- [ ] Ends `built; the owner's look in Anki waits` once the automated layers pass.
