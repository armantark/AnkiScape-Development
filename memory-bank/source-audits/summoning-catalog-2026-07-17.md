# Summoning surface catalog source audit (2026-07-17)

Scope: close the pouch, scroll, familiar-duration, Summoning-point, role, and
ordinary training rows needed for implementation. Cutoff is 2012-11-20.

## Pinned sources

1. **Summoning pouches**, oldid
   [6438719](https://runescape.wiki/w/Summoning_pouches?oldid=6438719),
   2012-10-18 21:44:17 UTC.
2. **Summoning scrolls**, oldid
   [6520851](https://runescape.wiki/w/Summoning_scrolls?oldid=6520851),
   2012-11-02 14:16:52 UTC.
3. **Summoning familiars**, oldid
   [6579789](https://runescape.wiki/w/Summoning_familiars?oldid=6579789),
   2012-11-19 04:08:58 UTC.
4. 2011Scape rev-667 snapshot:
   `SummoningPouchData.kt`, `SummoningScrollData.kt`, `Items.kt`, and
   `summoning_crafting.plugin.kts`.
5. Darkan commit `d02d8b88a1c7f654a24cdd3cc5a4fb7c9a11a87a`,
   `Pouch.java` and `Scroll.java`, for the non-infusion Meerkats and Ghast item
   identities.

Revision IDs and timestamps were retrieved through the MediaWiki revisions API.
`tools/generate_summoning_catalog.py` fetches the three literal pinned
wikitext revisions with retrying network calls and regenerates the checked-in
Python catalog.

## Closed catalog

- The ordinary surface infusion table has **78 pouch recipes**. Each row records
  level, exact shard count, charm family, tertiary item or items, creation XP,
  and Bogrog's level and 70%-return shard count.
- The surface scroll table has **68 named scroll rows**. Fetch Casket is a real
  period row but is not created from a pouch. The remaining 67 craftable scroll
  targets convert one matching pouch into ten scrolls.
- Shared scrolls remain one target with multiple valid input pouches: Call to
  Arms has four Void-pouch inputs, Petrifying Gaze has seven spirit-trice inputs,
  and Titan's Constitution has Fire, Ice, and Moss titan inputs.
- The familiar table has **80 surface familiars**: the 78 infusion familiars
  plus Meerkats and the Ghast familiar. It supplies each sourced duration,
  initial Summoning-point cost, role evidence, BoB capacity, forager delivery
  shape, boost summary, special name, and source ability summary.
- Meerkats and Ghast are explicit `craftable=False` catalog rows. Their pouches
  remain summonable items with Treasure Trails and Temple Trekking/Burgh de Rott
  Ramble acquisition routes respectively; they are not fabricated obelisk
  recipes.
- Spirit cobra accepts either ordinary or swamp snake hide. Ice titan requires
  both Air and Water talismans, while Wolpertinger requires both Raw rabbit and
  Wolf bones. These semantics are encoded instead of flattening every
  multi-tertiary row into the same transaction.
- The period wiki rows win over emulator discrepancies. Examples include Giant
  chinchompa creation XP and Rise from the Ashes creation/use XP and point cost.
  The emulators supply stable item IDs and explicit shared-scroll mappings, not
  authority to overwrite the closer period table.

## Isolation result

The generator stops the pouch and scroll inputs at their literal
`Dungeoneering` headings. Darkan Bloodrager, Stormbringer, Hoardstalker,
Skinweaver, Worldbearer, and Deathslinger rows and Stealing Creation clay
familiars never enter `SUMMONING_CATALOG` or the ordinary training targets.
Tests assert the 80-familiar, 78-infusion, and 67-scroll surface counts and the
absence of those closed-session families.

## Review-duration calibration

The source duration minutes are preserved as provenance data. Runtime lifetime
is an explicit review-native balance abstraction: one answered-card world tick
spends two source-duration units, with a two-review minimum. Thus the sourced
4-minute Dreadfowl lasts 2 answered cards, the 58-minute Pack yak lasts 29, and
the 151-minute Rune minotaur lasts 76. This avoids wall-clock gameplay, keeps
the shortest familiar useful, and preserves ordering and approximate ratios.
It is not a claim that one review equals two real minutes.

## Remaining source work

- Exact passive-foraging output tables and roll cadence remain a separate
  ability harvest. Delivery mode and the sourced 30-item familiar-storage
  capacity are already closed.
- Exact combat-special damage/effect semantics, familiar attack cadence, and
  familiar combat XP remain a separate ability harvest. No generic familiar
  damage target is invented.
- Per-tertiary reachability remains an economy audit. A catalog row may be
  source-correct but visibly input-blocked until its actual quest, activity,
  drop, Hunter, shop, or skilling route exists.
- The full pet catalog and acquisition matrix remain separate from these 80
  summonable familiar rows and are not counted as ordinary pouch targets.

