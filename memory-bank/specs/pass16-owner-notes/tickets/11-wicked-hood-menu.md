# 11: Wicked hood right-click menu

**What to build:** The Wicked hood's right-click menu, in the Bank and on the Equipment head slot, offers "Withdraw essence (N left)", a "Withdraw runes" submenu of fed altars with counts, a "Teleport" submenu of fed altars marked with any level lock, and Wear or Remove. Each entry calls the existing hood command and is disabled with the refusal reason when the command would refuse. A Bank-held hood works from the menu; output goes to the current Runecrafting target's carried pack. In the Auto carried layout, a fed hood that is not worn joins the pack of a Runecrafting target whose altar it fed when nothing else gives access. The Runecrafting panel card stays.

**Blocked by:** 01 (Bank right-click menu in its own module)

**Status:** open

- [ ] A Bank-held fed hood's menu withdraws essence into the current Runecrafting pack and the count drops.
- [ ] The rune and teleport submenus list only fed altars, with counts and level locks.
- [ ] The worn hood shows the same menu on the head slot.
- [ ] An Auto layout Runecrafting session at a fed altar packs the hood and grants entry with no talisman, through real reviews.
- [ ] The Runecrafting card still works.
- [ ] Offscreen Qt capture of both menus at 560 px with clean text-fit checks; one play-checklist line.
