# Item-pack and Magic-essence identity audit — 2026-07-16

## Scope

This pass verifies the contents of every supply pack sold by a live AnkiScape
shop and resolves the conflicting product identity of the Barbarian Herblore
Magic essence mix recipe. The evidence standard is
`memory-bank/pre-eoc-source-verification-standard.md`.

## Supply packs

The local 2011Scape item plugin is executable primary implementation evidence:

- `.../content/items/packs/PackData.kt:9-16` maps Vial, Vial of water, Eye of
  newt, Empty sack, Basket, Juju vial, and Raw bird meat packs to 50 of the
  corresponding noted item, and the Spirit shard pack to 5,000 Spirit shards.
- `.../content/items/packs/packs.plugin.kts:3-14` exposes both `open` and
  `open-all`, removes the selected pack count, and adds the exact multiplied
  contents.

AnkiScape intentionally collapses noted and unnoted bank identities, so its
pack outputs use the canonical unnoted display names while preserving the exact
quantities. `shop_data.py` contains precisely these eight live pack identities.

Verdict: implemented without abstraction. Opening one pack and opening all
owned packs are instantaneous Bank actions and are undoable as one atomic
direct action.

## Magic essence mix

The local 2011Scape `PotionData.kt:373-379` calls the row
`MAGIC_ESSENCE_MIX` but sets `product = Items.MAGIC_POTION_2`. That product is
an isolated transcription error rather than the period item identity:

- the local cache constants `Items.kt:10243-10246` define item 11489 as
  `MAGIC_ESSENCE_MIX_2` and 11491 as `MAGIC_ESSENCE_MIX_1`;
- Darkan `developer-information/itemReqs.txt:1756` defines item 11489 as the
  level-61, 43-XP product of Magic essence (2) plus Caviar;
- Darkan `CraftablePotion.java:176` independently carries the same output and
  ingredients;
- Darkan `Potions.kt:355-358` treats 11489/11491 as the drinkable Magic essence
  mix dose family;
- the period cache item definition names are `Magic essence mix (2)` and
  `Magic essence mix (1)`.

Verdict: the canonical recipe output is `Magic essence mix (2)`, item 11489.
The 2011Scape product field is rejected because it conflicts with the cache
identity and two independent Darkan producer/consumer paths. The RuneScape Wiki
asset `File:Magic essence mix (2).png` is provenance-recorded in
`assets_provenance.json`.

## Juju farming dose family

Darkan cache constants identify the full decant/consumption family:

- `Items.kt:17565-17568`: doses 4–1 are item ids 20011–20014.
- the Farming contract section 23 fixes a five-farm-minute effect and a
  one-in-three bonus-herb roll; this is the answer-driven Farming clock, never
  wall time.

The four dose assets are sourced from the RuneScape Wiki and recorded in
`assets_provenance.json`. Dose 4 is reachable through Bob Barter; doses 2 and 1
are the preserved remainders after drinking.
