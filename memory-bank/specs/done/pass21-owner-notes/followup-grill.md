# Pass 21 follow-up: owner answers, 2026-11-05

These answers settle `open-questions.md`. The ammo return rate stays open and is not part of this work.

## Owner's words

- Which ammo is worn, 08:12: "Sure unless you have one already equipped manually/intentionally then it should pick that one. Or for transparency you could have a little checkbox somewhere (albeit don't want to devolve into checkbox hell again)". To the question "at each bank run wear the strongest type your bow and levels allow".
- First card of a fight, 08:12: "Yes". To "Starting a target fills the slot from the Bank at no cost; a trip happens only when the slot runs out mid-fight".
- Plan rows, 08:12: "It needs to be intelligent rather than just a flat acceptance of all rows. Like it should look ahead to see what you will have from previous steps, and only allow those for future queue steps; everything else should stay grayed out".
- Diary tiers, 08:12: "Yes". To "A tier is claimable when all of its live rows are done, and it stays claimed when dormant rows wake up later".
- Visible mark, 08:37: "Yes". To "show the word "Manual" beside the count in the Ammunition slot. If you remove the stack by hand, the automatic choice starts again", with no checkbox.
- Click on a gray row, 08:37: "I guess". To "one click selects the gray row, with Add and Start off".

## Contract

1. **Strongest ammo.** At each bank run, the slot takes the strongest type that the weapon and levels allow. This replaces "keeps its type until it runs out".
2. **Manual stack.** A stack the player equips by hand stays worn through bank runs and refills from the same type while the Bank holds it. When that type is gone from the Bank, the automatic choice starts again. Removing the stack by hand also starts the automatic choice again. The mark persists in the save. A save without the mark is automatic.
3. **The word.** The Ammunition slot shows "Manual" beside the count while the mark is set. This is the only interface addition for ammo, and it must read correctly in dark and light themes.
4. **First card.** Starting a target with an empty slot fills it from the Bank at no cost, so the first card fires shots. A trip happens only when the slot runs out in a fight. A fight with no ammo in the Bank keeps its existing refusal.
5. **Plan look-ahead.** A row with materials missing can be queued only when earlier queue entries supply every missing input in a count that makes at least one of the row's output. The count box limit follows that supply. Every other such row stays gray. This replaces the acceptance of all rows. Level, quest and tool locks do not change.
6. **Gray row click.** One click selects a gray row in every list that takes plan rows. Add and Start are off for it. Add must not stay on the earlier target. A row with materials in the Bank does not change.
7. **Queue edits.** Removing or moving an earlier entry so that a later plan row loses its supply must leave no entry that stops with a surprise. Use the existing queue stop behavior if it covers this, and record what happens.
8. **Diary tiers.** A tier is claimable when all of its live rows are done, and it stays claimed when dormant rows wake up later.
