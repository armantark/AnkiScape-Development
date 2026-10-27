# 12: Follow-ups from the landed tickets

**What to build:** Two gaps that tickets 08 and 11 left. (1) Ticket 11 renamed the 2012 item "Grain" to "Wheat" and migrates it in the Bank, but shop save rows and Grand Exchange offers stored under "Grain" are not migrated, because the shop name lookup reads only the crafting rename map: a player with a Grain offer or shop row must load with it as Wheat, with no lost coins or items. (2) Ticket 08 changed remaining times to cards, but Fish Flingers still reads "8 catches over 1,000 ticks"; the owner's rule is that a player who counts cards never reads ticks, so it reads in cards at the player's game speed.

**Blocked by:** None (can start immediately)

**Status:** open

- [ ] A save with a Grain Grand Exchange offer (buy and sell) and a Grain shop row loads with Wheat in each, and collecting the offer gives Wheat or the coins it should.
- [ ] Fish Flingers names its length in cards at the current game speed, and a search finds no player-visible tick count left outside setting labels.
- [ ] Focused tests and the full plain lane pass apart from the known base failures.
