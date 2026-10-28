# 02: Last action record and the Resume button on the review HUD

**What to build:** Every switch to Bankstanding, automatic or a manual Stop, first saves a last action record (the action kind and every key its start path needs: skill and target key, utility id, quest id, combat target and combat action). While the current action is Bankstanding and a last action exists, the review HUD shows "Resume" plus the action's display name beside "Bank run", for example "Resume Black Knights' Fortress". A click starts that action through the same start function its tab uses, so every requirement check runs; a refusal shows the same reason and starts nothing; a quest resumes at its saved step. The button's look goes through the hill-climb loop (spec, "The hill-climb loop"), task: "restart the quest that stopped".

**Blocked by:** None (can start immediately)

**Status:** done

- [x] The last action record is saved by the switch to Bankstanding for skills, utilities and activities, quests and combat, and survives a profile reload.
- [x] Black Knights' Fortress blocked for an iron chainbody, then given one, resumes at its step from the Resume click (real review handler).
- [x] A Resume click with the requirement still missing shows the same reason text and leaves Bankstanding.
- [x] Hill-climb rounds recorded under the evidence folder; the probe passes and the taste vote approves, or five rounds end with the best candidate reported.
- [x] One play-checklist line added.
