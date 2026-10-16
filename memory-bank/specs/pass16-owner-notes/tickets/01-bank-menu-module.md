# 01: Bank right-click menu in its own module

**What to build:** The Bank item right-click menu builder moves out of the main UI module into its own UI module, with no change in behavior. Tickets 06, 11 and 12 add entries to this menu, and the main UI module cannot grow.

**Blocked by:** None (can start immediately)

**Status:** open

- [ ] The Bank right-click menu for every item kind (equip, eat or drink, break, open, loot, start trail, tool belt attach, rogue kit) shows the same entries in the same order as before.
- [ ] The main UI module shrinks by the moved block; the new module holds only the menu builder and its private helpers.
- [ ] Existing Bank menu tests pass unchanged, and the offscreen Qt lane passes for the Bank tab.
