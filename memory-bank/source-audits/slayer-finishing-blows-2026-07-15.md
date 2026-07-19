# Slayer finishing blows and quick-kill unlock — 2026-07-15

Status: **period mechanic, cutoff exclusions, and review mapping closed**.
Cutoff: `2012-11-20T00:00:00Z`.

## Core reward evidence

RuneScape Wiki, `Slayer points`, oldid `6520963`, timestamp
`2012-11-02T15:54:41Z`:
<https://runescape.wiki/w/Slayer_points?oldid=6520963>.

The historical wikitext records `Ability to deliver killing blows quicker` for
400 Slayer points. It identifies rockslugs, desert lizards, zygomites, and
gargoyles as the affected families and states that they die normally at zero LP
only while the required item is in the player's inventory. It also states that
the unlock works with ranged and magic attacks and does not apply to the
experimental fungicide used during Chaeldar's challenge.

This proves that the reward automates the finisher but does not remove its item
requirement.

## Period target rows

### Rockslug

RuneScape Wiki, `Rock slug`, oldid `6530509`, timestamp
`2012-11-04T05:20:18Z`:
<https://runescape.wiki/w/Rock_slug?oldid=6530509>.

- A bag of salt is consumed to finish the rockslug at 1–39 LP.
- Using it too early consumes the bag without effect.
- Without a successful finisher, the rockslug does not die normally.

### Desert lizard

RuneScape Wiki, `Desert lizard`, oldid `6548273`, timestamp
`2012-11-11T18:54:08Z`:
<https://runescape.wiki/w/Desert_lizard?oldid=6548273>.

- An ice cooler is consumed to finish the lizard at 1–30 LP.
- Using it too early consumes the cooler without effect.
- The lizard otherwise cannot be killed.

### Mutated zygomite

RuneScape Wiki, `Mutated zygomite`, oldid `6530349`, timestamp
`2012-11-04T01:56:40Z`:
<https://runescape.wiki/w/Mutated_zygomite?oldid=6530349>.

- Fungicide spray is used below 20 LP and spends one charge.
- Using it too early spends a charge without killing the zygomite.
- Chaeldar's experimental spray has its own random kill, enrage, and full-heal
  outcomes and is explicitly outside the automatic-finisher reward.

### Gargoyle

RuneScape Wiki, `Gargoyle`, oldid `6579781`, timestamp
`2012-11-19T03:45:52Z`:
<https://runescape.wiki/w/Gargoyle?oldid=6579781>.

- A rock hammer finishes the gargoyle below 90 LP and is not consumed.
- The 400-point unlock automatically smashes it at zero LP while the hammer is
  in inventory.
- The manual finisher may be used before zero once the threshold is reached.

## Existing AnkiScape gate

`source-audits/combat-enemy-roster-step1-data-report-2026-07-07.md`
intentionally excludes rockslug and gargoyle because Combat cannot yet express
their required item-on-target finisher. Shipping them as ordinary enemies would
be a parity regression.

## Post-cutoff unlimited-shaker exclusion

The current item records date all four unlimited shakers to `2015-06-08`, more
than two years after the cutoff:

- `Salt shaker`, item `34960`:
  <https://runescape.wiki/w/Salt_shaker>;
- `Ice shaker`, item `34961`:
  <https://runescape.wiki/w/Ice_shaker>;
- `Fungicide shaker`, item `34962`:
  <https://runescape.wiki/w/Fungicide_shaker>; and
- `Explosive shaker`, item `34963`:
  <https://runescape.wiki/w/Explosive_shaker>.

Exact-name queries against revs 727, 728, 729, 736, 741, and 742 returned no
matching item definitions. The four shakers are excluded rather than treated as
period upgrades or equipment. Their underlying one-use supplies remain live.

## Closed design constraints

- The required item must remain meaningful before and after buying the unlock.
- Consumable finishers spend exactly one item or charge on each use; the rock
  hammer is a presence check.
- Drops, XP, assignment decrement, and kill telemetry happen only after the
  successful finisher.
- The automatic unlock folds the finisher into the final damaging Combat action.
- Experimental fungicide remains a challenge-specific exception.
- Unlimited shaker replacements do not exist at the cutoff.

## Review-native mapping

The source describes a separate manual action before the unlock and an automatic
finisher afterward. The manual action consumes the next correct review and
commits the consumable spend, kill, drops, XP, assignment progress, and undo
record atomically. The 400-point unlock folds those effects into the final
damaging review while retaining the item check and consumable spend.

The action selector disables manual finishers until the source LP threshold is
valid. The period game's early, ineffective consumable use is intentionally not
encoded; this removes a UI misclick trap without changing the item requirement,
review cost, successful spend, or unlock value.

## Implementation-readiness follow-up — 2026-07-17

The four finishing-item acquisition rows are source-ready:

| Item | Source item | Inventory shape | Shop acquisition |
|---|---:|---|---|
| Bag of salt | 4161 | stackable; consumed once | Turael stock 1,000 at 10 coins |
| Rock hammer | 4162 | non-stackable; reusable presence check | Turael stock 10 at 500 coins |
| Ice cooler | 6696 | stackable; consumed once | Turael stock 1,000 at 1 coin |
| Fungicide spray 10 | 7421 | non-stackable charged tool | Turael stock 10 at 300 coins |

The source rows are
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/items/shops/turaels_slayer_equipment.json`.
The generated shop stock already retained these item IDs and stackability
values, but `shop_extra_items_as_dict()` dropped both fields before the shared
item registry was built. Commit `2ddbb0a` now preserves them. Regression
coverage pins all four source identities and inventory shapes at both the shop
catalog and consolidated item-registry boundaries.

At that implementation-readiness checkpoint, this did **not** certify any
finisher family for runtime admission:

- Rockslug and Gargoyle have useful 2011Scape Combat candidates, but their
  reconstructed 50/100-LP death-blow thresholds conflict with the period
  1–39/below-90 evidence above. Gargoyle's candidate also leaks the
  Kuradal's-Dungeon-only Ferocious-ring drop into its global table.
- Desert lizard and Mutated zygomite do not have complete reconciled Combat
  rows in the pinned local reconstructions.
- All four target images and provenance rows are absent, and the Combat asset
  fetcher correctly refuses unknown target IDs.

## Live implementation follow-up — 2026-07-17

The generic manual/automatic finisher runtime and Desert lizard landed
together. The target now has a reconciled Combat row, one exact 100,000-slot
Darkan selector, period level/XP/finisher gates, a proven sprite, an eight-skin
Desert-heat supply pack, and real Qt selection. See
`slayer-desert-lizard-combat-2026-07-17.md`.

Rockslug and Gargoyle are now live with reconciled target/drop rows, exact
period finishing windows, source-specific behavior, proven period icons, and
the shared finisher runtime. Rockslug consumes one Bag of salt and stops
retaliating at 10 LP. Gargoyle retains its reusable Rock hammer and carries
tick-exact regeneration across review boundaries. See
`slayer-rockslug-gargoyle-combat-2026-07-17.md`.

Mutated zygomite is now live with both ordinary variants, Lost City and Slayer
57 gates, charged-spray preservation/reload behavior, reconciled drops, and
period assets. See `slayer-mutated-zygomite-combat-2026-07-18.md`. This closes
the ordinary finishing-blow family blocker.
