# Pass 21: questions for the owner's next grill

The owner, 2026-11-04 23:28: "I'm sleeping work unattended and gather loose questions/decisions into a file we can go over in a grill for me when I ask". Each entry says what the build did by default.

## Waiting

(Entries are added as the run finds them.)

1. **A rune pouch.** No general rune pouch existed by the 2012 cutoff (`Large rune pouch` and `Small rune pouch` are later items), and period staves and boxes hold only restricted runes. You wrote "which can be helped with a rune pouch". Should the game make an exception and add one? Default built: no pouch; runes take one carried slot per type.
2. **Quivers.** Tirannwn quivers arrived in 2014, and their ammunition storage in 2015, so they are after the cutoff. Should they be an exception? Default built: none.
3. **Ava's toggle.** Should it switch off arrow collection too? Default built: it switches off only the incidental iron or steel items, as in 2012, and arrow collection stays on.
4. **"Like 50%".** Half of all fired ammo, or half of the ground share (2012 left 80% on the ground, so 40% of shots)? Default built: 50% of all fired ammo, at no time cost.
5. **Which ammo is worn.** Default built: the highest-strength type your weapon and levels allow. Running out starts a bank trip, which switches type. Other choices: lowest first, or a choice per target.
6. **Is the toggle global?** Default built: one global setting, not per combat preset.

7. **The 22 new diary deeds.** The names and sentences, such as "Yew Can't Park Here" and "Beard Snatcher", are in `/Users/ArmanTarkhanian1/Documents/ankiscape-pass21/reports/04.md` if a report file exists, and in `memory-bank/diary-curation-ledger/dormant-task-ledger.jsonl`. Three are invented because no period seam exists: Off the Wall, Beard Snatcher, Leaf Me Alone. Default built: as written; review them when you like.
8. **Retroactive diary credit.** A save with earlier action history completes a new deed at its next refresh, with no new action, for example three past yew chops. The same rule applies to every ledger row. Default built: keep.
9. **Diary tiers with dormant rows.** A tier with dormant rows cannot reach "Ready to Claim", because the claim rule counts non-dormant rows against a total of 12. Fremennik Easy has 3 such rows. This predates Pass 21, and I left it. Should a tier be claimable when all its live rows are done?

10. **A plan with no producer.** Add on a plan-only row with an empty queue starts the entry, and the next review stops it: "You need 1 Soft clay to craft Bowl (unfired)." The entry is then gone. Should Add refuse with that message, or should the entry wait for its input? Default built: as described.
11. **Activities list.** Only Utilities and the skill lists take plan-only rows. The Activities list stays as it was. Default built: leave it.

12. **First card of a bow fight.** With an empty Ammunition slot, the first card is a bank trip with no shots, because arrows in the Bank must be fetched. At 10x that is one card with no attack when you start a bow target. Should starting a target equip ammunition at once at no cost? Default built: a bank trip.
13. **Which stack stays worn.** The slot keeps its current type until it runs out, so a better type in the Bank waits. The first native run wore Iron and the second wore Bronze with 200 Iron in the Bank; I could not explain the second from the code. Do you want it to switch to the best type at each bank run? Default built: keep the current type.
14. **Native gap.** The tester could not set up a Magic spell through the menu ("only Crush styles" with a staff), so runes in the pack passed only through tests. It also lost Anki once while reopening Equipment after a fight, with no crash report and no crash output, so the cause is unknown. Tell me if that happens to you. Your Studio Anki did segfault at 22:28 on 2026-11-04 with the menu open, and the MacBook's reports for that day show Qt's accessibility cache, the known Qt 6.11 bug.
15. **The stale Next line.** Tests prove the fix, but the native run did not reach that line, because it appears only at a quest's completion. Your play is its first real check.
