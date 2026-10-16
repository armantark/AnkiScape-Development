# 01: Bank right-click menu in its own module

**What to build:** The Bank item right-click menu builder moves out of the main UI module into its own UI module, with no change in behavior. Tickets 06, 11 and 12 add entries to this menu, and the main UI module cannot grow.

A pure move fails the commit hook: the builder is a nested closure, and any wrapper that holds it measures cognitive complexity 174 against the limit of 15. So the menu splits into one top-level function per menu section (start trail, tool belt, equip, eat or drink, and so on), each within the hook's limits, called in the existing order by one short builder. The builder reads its state and callbacks from one context object that the Bank tab creates once. A new menu entry then means one new section function.

**Blocked by:** None (can start immediately)

**Status:** claimed by sol-01

- [ ] The Bank right-click menu for every item kind (equip, eat or drink, break, open, loot, start trail, tool belt attach, rogue kit) shows the same entries in the same order as before.
- [ ] The main UI module shrinks by the moved block; the new module holds only the menu builder and its private helpers.
- [ ] Existing Bank menu tests pass unchanged, and the offscreen Qt lane passes for the Bank tab.
