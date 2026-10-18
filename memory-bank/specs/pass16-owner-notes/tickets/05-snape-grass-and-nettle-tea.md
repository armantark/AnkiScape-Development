# 05: Snape grass row and the nettle tea name

**What to build:** A player doing Skippy and the Mogres can find every ingredient. A "Gather snape grass" Utilities row models the 2012 Hobgoblin Peninsula spawn (3 clumps a trip, no requirement) and names the site. The Cooking row that boils nettle-water is named for its product, nettle tea, and the drinks family has a readable label.

**Blocked by:** None (can start immediately)

**Status:** done by sol-05

- [x] Answering reviews on "Gather snape grass" adds Snape grass to the player's items; the row cites Snape grass oldid 6269500 and the Darkan spawn list.
- [x] The row text names the Hobgoblin Peninsula.
- [x] The Cooking row that makes Nettle tea is labelled by its product, following the other Cooking rows' naming; a search for "nettle tea" finds it.
- [x] The drinks group header reads as a word, not the raw family key.
- [x] Skippy and the Mogres completes end to end with gathered snape grass and no combat drop.

The existing selector supplies the readable Drinks header from the family key; the Qt check covers it.

Verification note: tree item text needs direct width and height checks as well as `text_fit_defects`. The site is on a second line so the full row fits at 720 by 560 px.
