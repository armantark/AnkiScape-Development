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

## Ammo return, 2026-11-05

Owner's words:

- 08:54: "Well for balance I'd like either this or the pickup button. I'm leaning toward the pickup button. The button should only show if you're using a ranged weapon with ammo tho"
- 08:54: "If you click the button you get 100% of what's available back; some might despawn by the time 10x ticks happen"
- 09:00: "No, if we have the pickup button then there's no automatic pickup besides Ava's devices"
- Earlier: "to simulate how annoying it is to manually pick up the ammo", and of bones: "I guess it is already balanced". Bones do not change. The laziness curve and the low-coin rule are not built, because the owner chose the button over them.

Contract:

9. **Each shot.** 20% of shots break, with or without a device. With no device, every unbroken shot lands in a ground pile, and nothing returns by itself. A worn Ava's device keeps its 60% or 72% in the slot, and the rest of its unbroken shots land in the pile. This replaces the flat 50% rule.
10. **Ground pile.** The pile persists in the save and is covered by the existing review undo. Each landed arrow disappears a fixed count of game ticks after it lands. Use 350 ticks: Darkan's `World.addGroundItem` uses 60 seconds hidden and 150 seconds visible, which is 210 seconds. Because the ticks of a card advance together (60 at 10x), some arrows can disappear on the card that reaches their time. A target change does not clear the pile.
11. **Button.** The review HUD shows "Pick up ammo (N)" only while the worn weapon is a ranged weapon that uses ammo. N is the count in the pile. A click returns 100% of the pile, costs no card and no ticks, and adds to the worn stack when the type matches and to the Bank otherwise. The button is off when N is 0. No sentence explains the button.
12. **Event log.** Use one existing-style line per card with counts of fired, broken and landed arrows, and a line for each pickup with its count. Change no other panel.
