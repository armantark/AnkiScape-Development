# 10: Elegant, minimal menu copy

**What to build:** Opus rewrites the text of the Pass 17 hill-climb screens (the Resume and stop lines on the review HUD, the queue box, the combat setup panel) and sets the final text of every Pass 18 string (add feedback, refusal causes, Mix with, Wyson's offers, supply-step lines). Elegant and minimal: a label where a label serves, no sentence that explains what a control already shows. `AGENTS.md` gains one line with that rule. See spec "Menu copy".

**Blocked by:** 03 (queue box), 04 (supply steps), 05 (dye mixing), 06 (Wyson)

**Status:** claimed by Opus 5.5 implementer on goal/pass18-10-menu-copy

- [ ] A before-and-after table of every changed string is saved under the evidence folder.
- [ ] Every test that pins a changed string pins the new one; no text is cut or elided at 560 points tall.
- [ ] The orchestrator's native look shows the new text in real Anki.
