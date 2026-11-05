# 12: Search boxes select the phrase, and Combat search matches names

**What to build:** A double click in any of the 27 search boxes selects the whole phrase, through one search-specific line edit. Combat search matches monster name, group and logged drops only; the tooltip option goes away with its only user. Grill answer 11 and the decision recorded in `grill.md`.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] A real double-click event selects the phrase in every search box; a census test finds no search box that uses a plain line edit.
- [x] "bat" gives Giant bat and Guard (battleaxe) in Combat. "Stolen Hearts" still ranks first in Quests, and "tara" still finds tiara.
