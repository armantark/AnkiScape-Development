# 05: Ammunition in the real slot, Ava's devices and runes in the carried pack

**What to build:** The hidden `combat_supply_loadout` stores for ammo and runes go. Ammunition sits in the real Ammunition slot as one stack with its count, shown in the Equipment tab like any worn item; the rest stays in the Bank. Casual mode wears the best type the weapon can fire, and a bank run tops up that type or switches when it runs out. Fired ammo: with an Ava's device, its rates apply. Without one, auto pickup returns 50% of all fired ammo at no time cost (the owner's balance rule, not a period value). An Ava's device gets the period on and off toggle, one global setting, which turns off its incidental iron or steel items and leaves arrow collection on, as `ammo-facts.md` section A states. Casual mode wears the highest-strength type the weapon and levels allow. Running out starts a bank trip, which switches type if the worn type is gone. The owner can change these in his next grill, so keep each rule in one place. Runes sit in the carried pack, one slot per rune type, and a fight spends them from there; a bank run restocks them. Saves migrate with nothing lost: the best compatible loaded ammo goes to the slot, other loaded ammo and loaded runes return to the Bank. The facts are in `ammo-facts.md`. Items after the 2012 cutoff are not built: no general rune pouch and no Tirannwn quiver. Period rune holders that already exist keep their behavior.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] Played at 10x: Shortbow, 840 Bronze arrows in the Bank; a fight puts the stack in the slot; the Equipment tab shows the count; the count falls and recovered arrows return at the stated rate; running out starts a bank run or a danger stop as ammunition does today.
- [x] With Ava's attractor and accumulator, over a seeded sample, the rates match `ammo-facts.md`; without a device the rate is 50%; the toggle saves and changes only the incidental items.
- [x] A rune stack takes one carried slot per type, a spell spends it, and running out starts a bank run or stop; the pack's 28 slots stay honest with food and loot.
- [x] A save with 918 Bronze and 18 Iron loaded, and with loaded runes, migrates with every item accounted for; undo and reload hold.
- [x] Offscreen captures of the Equipment slot count and the toggle, default size and 560 tall, dark and light.
