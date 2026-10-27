# 07: Combat setup panel hill-climb, with prayers that run when ticked

**What to build:** The hill-climb loop (spec, "The hill-climb loop") rebuilds the combat setup panel from "Combat mode" to "Current target", including the advanced preset editor, until a player with no guide completes its task list from screenshots alone and the taste vote approves. First candidate: a ticked "Prayers/Curses" keeps the chosen prayers on all fight ("Always 100%") unless the advanced editor sets a lower uptime; with no prayer chosen, the game picks the best prayers by the rule "Supply mode" uses; saves holding the old "Off" uptime follow the new rule. The max-hit preview uses the same prayer drain per card as a real fight, and every prayer setting change rebuilds the target tooltips. During a fight the review HUD shows the active prayers beside the prayer points, for example "Prayer 38/43 · Burst of Strength". Every setting the panel has now stays reachable. The play checklist's max-hit line names the Combat target row tooltip and the exact settings the final rule needs.

**Blocked by:** 06 (Move the combat setup panel into its own module), 02 (Last action record and Resume)

**Status:** done

- [x] A fight through the real review handler with Prayers/Curses ticked and Burst of Strength chosen drains prayer points and raises the max hit.
- [x] The max-hit tooltip changes at once after a prayer setting change and matches a real fight's drain.
- [x] The review HUD shows the active prayers during a fight.
- [x] Hill-climb rounds recorded; the probe passes every task and the taste vote approves, or five rounds end with the best candidate reported.
- [x] Offscreen captures at 560 points tall, dark and light, `text_fit_defects` clean; the play-checklist max-hit line corrected.
