# 08: Remaining times in cards, not ticks

**What to build:** One shared formatter turns a remaining tick count into "N cards left" at the player's current game speed, rounded up, "1 card left" in the singular, through the existing ticks-to-cards converter. It replaces every remaining time shown in ticks: poison and poison immunity on the review HUD and the combat target, the Mining extra-ore bonus, Fist of Guthix, Tears of Guthix, collection ticks and Juna's cavern time. Setting labels that are not remaining times, such as "Auto-bury/scatter combat drops (costs simulated ticks)", keep their wording.

**Blocked by:** None (can start immediately)

**Status:** open

- [ ] Unit tests: 150 ticks at 10x reads "3 cards left"; 60 ticks at 10x reads "1 card left"; 600 ticks at 10x reads "10 cards left".
- [ ] A real antipoison dose in combat shows "Poison immune: N cards left" on the review HUD.
- [ ] A search for remaining-time texts in ticks finds none left.
- [ ] One play-checklist line added.
