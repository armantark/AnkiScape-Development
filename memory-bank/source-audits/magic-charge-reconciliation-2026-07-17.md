# Magic Charge source reconciliation — 2026-07-17

## Finding

`magic_data.py` cited RuneScape Wiki oldid `6549273` as the pre-EOC Charge
spell. The local historical resolver shows that revision is the unrelated
level-9 Charge Prayer page. It therefore cannot support any Magic row.

The nearest pre-cutoff spell revision is:

- `Charge (spell)`, oldid `6593039`, 2012-11-20 08:00:37 UTC:
  https://runescape.wiki/w/Charge_%28spell%29?oldid=6593039

The data pin is corrected to that revision and covered by a regression test.

## Facts closed by the corrected spell page

- Charge requires level 80 Magic.
- It consumes three fire, three blood, and three air runes and awards 180 Magic
  XP.
- Its effect lasts seven minutes.
- It adds 100 old-system life points to the maximum hit of Saradomin Strike,
  Claws of Guthix, and Flames of Zamorak. It does not affect Storm of Armadyl.
- The player must wear a god cape for the damage effect to work.
- The page says Charge cannot be recast while already active, despite also
  describing a one-minute cast interval. The currently owner-approved
  AnkiScape contract refreshes the review-driven duration on recast; this
  source conflict is recorded rather than silently rewriting shipped behavior.

## Related Mage Arena evidence

- `Mage Arena`, oldid `6512911`, 2012-10-31 18:05:45 UTC:
  https://runescape.wiki/w/Mage_Arena?oldid=6512911
- `God capes`, oldid `6591725`, 2012-11-20 05:46:27 UTC:
  https://runescape.wiki/w/God_capes?oldid=6591725

Together these revisions establish:

- defeating Kolodion is followed by choosing Saradomin, Guthix, or Zamorak;
- praying at that statue grants exactly one corresponding cape, and the Chamber
  guardian grants the first matching staff;
- other god staves cost 80,000 coins;
- each god spell requires 100 arena casts before use outside the arena;
- a player may own only one god cape at a time, may replace it at another
  statue after destroying the current cape, and may reclaim a lost cape without
  fighting Kolodion again;
- a god staff cannot be equipped with another god's cape; Charge requires the
  appropriate cape and staff pairing for its 50% higher god-spell hit.

## Runtime comparison

The live five-review Mage Arena landmark only records completion.
All three god spells and Charge then unlock together. God staves exist in the
equipment/shop data, but the landmark grants none; god capes are not live
equipment; there is no god alignment, per-spell arena attunement, cape
replacement/reclaim action, or gameplay reader for Charge's damage boost.

The duration clock is independently valid and remains shipped. Completing the
damage effect and reward path requires the owner-level abstraction recorded in
`memory-bank/design-gaps-grill-harvest-2026-07-17.md`.
