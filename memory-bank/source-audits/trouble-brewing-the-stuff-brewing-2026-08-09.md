# Trouble Brewing The stuff and mature-ale brewing

Date: `2026-08-09`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **verified and implemented with one registered hidden-roll placeholder.**

## Period record

`Brewing`, oldid `6447660`, timestamp `2012-10-20T22:19:26Z`, identifies
brewing as Cooking and fixes the vat sequence: two buckets of water, two barley
malts, optional `The stuff` immediately after the malt, the ale-specific
ingredient, and one ale yeast. One vat fills eight beer glasses or two calquat
kegs. Its Dwarven stout row fixes Cooking level `19`, four Hammerstone hops, and
`215` Cooking XP. The same revision says ordinary ale can mature naturally and
that `The stuff` increases the chance of mature ale by 50 percent.

Source: <https://runescape.wiki/w/Brewing?oldid=6447660>

`The Stuff`, oldid `6447071`, timestamp `2012-10-20T15:26:18Z`, confirms that
the non-tradeable reward is added after water and malt and before the other ale
ingredient and yeast. `Honest Jimmy's House of Stuff`, oldid `6393015`,
timestamp `2012-10-13T04:08:35Z`, fixes its shop price at `5` Pieces of Eight.

Sources:

- <https://runescape.wiki/w/The_Stuff?oldid=6447071>
- <https://runescape.wiki/w/Honest_Jimmy%27s_House_of_Stuff?oldid=6393015>

## Cache and reconstruction evidence

OpenRS2 cache `544`, RuneScape revision `742`, dated `2012-11-07`, pins these
item identities and client properties:

| item | id | relevant property |
| --- | ---: | --- |
| Dwarven stout | `1913` | exchangeable; `Drink` |
| Dwarven stout (m) | `5747` | exchangeable; distinct recolour; `Drink` |
| Ale yeast | `5767` | vat ingredient |
| Beer glass | `1919` | collection container |
| Bucket of water | `1929` | vat ingredient |
| Barley malt | `6008` | vat ingredient |
| Hammerstone hops | `5994` | Dwarven stout ingredient |
| The stuff | `8988` | non-stackable and non-exchangeable |

The cutoff Exchange revisions also keep the two newly registered market rows
fully usable: `Exchange:Ale yeast` oldid `6561111`, timestamp
`2012-11-16T02:02:53Z`, gives guide price `31` and limit `100`;
`Exchange:Dwarven stout (m)` oldid `6561755`, timestamp
`2012-11-16T03:22:35Z`, gives guide price `25,372` and limit `100`. The complete
buy-limit table remains oldid `6457777`, timestamp `2012-10-23T03:28:03Z`.

Darkan commit `ed7fb12685102a37a0be4b36d255ed96cf99b98d` corroborates the
full-vat item chain. `Brewery.java:36-42`, `150-172`, `175-211`, and `238-269`
cover identities, water/malt consumption, the ale ingredient, yeast, and
collection. `Brewable.java:22-33` fixes Dwarven stout's ordinary/mature IDs,
level, four-hop ingredient, and `215` XP.

The Darkan reconstruction uses a `10%` natural mature roll and `75%` with `The
stuff` at `Brewery.java:228-233`. This is useful reconstruction evidence, not a
period-primary formula. The period article's informal level-based observation
and 50-percent-increase wording do not settle an exact hidden roll. The live
values therefore remain registered as
`cooking.dwarven_stout_mature_chance`; a period server maturity routine would
replace them.

## AnkiScape translation

- Honest Jimmy now sells one non-stackable, non-tradeable `The stuff` for five
  Pieces through the existing atomic purchase and direct-undo seam.
- Cooking exposes two explicit level-19 Dwarven stout targets. Both consume a
  full vat's ingredients and eight beer glasses, return two empty buckets, and
  award `215` XP. The second target also consumes one `The stuff`.
- The mature outcome awards eight `Dwarven stout (m)`. The other outcome awards
  eight ordinary `Dwarven stout` with the same XP; it is not mislabeled as a
  burn or failed action.
- One answered card represents adding the ingredients, fermentation, and
  collection for the whole vat. This is the settled review-action flattening;
  no wall-clock or login timer enters gameplay.
- The existing Cooking selector owns the two rows under `Brewing`. Its details
  state the mature and ordinary outputs, placeholder mature chance, full-vat
  abstraction, materials, and returned buckets. The Trouble Brewing reward
  combo adds the source sprite and a concise purpose tooltip.

## Explicit omissions

- Only Dwarven stout is implemented in this breadth slice. The other sourced
  ales are catalog depth, not missing mechanics: the representative row already
  exercises brewing, optional additive consumption, alternate maturation,
  batch outputs, container returns, XP, persistence, undo, UI, and assets.
- Intermediate vat states, spoiled ale, calquat-keg collection, exact object
  coordinates, animations, and dialogue are not represented. They add content
  or presentation depth to the same flattened review action.
- Darkan accepts `The stuff` after the ale-specific ingredient, while the period
  article requires it immediately after malt. The period ordering owns the
  description; the flattened action consumes the complete recipe atomically.
- Darkan's collection routine multiplies the `215` table value by eight. The
  cutoff article labels `215` as the Dwarven stout recipe's Experience value,
  so the period table owns the live full-vat award rather than the
  reconstruction's multiplier.

## Verification

- Focused Cooking, Trouble Brewing, runtime, Grand Exchange, registry,
  placeholder, and asset checks: 491 tests pass.
- Focused real offscreen Qt: three interaction checks pass. Dark-mode captures
  show the five-Piece reward and both expanded Brewing rows without elision.
- Fable found no content or layout defect after the corrected expanded-group
  capture. Kimi K3 could not complete the required independent taste pass: the
  provider returned HTTP 403 with `You've reached your usage limit for this
  billing cycle.` This record does not claim Kimi approval.
- Full plain discovery: 3,927 tests pass with 482 expected skips.
- Full real offscreen-Qt discovery: 3,927 tests pass with three intentional
  skips.
- Documentation: 533 Markdown and 431 HTML files pass the docs audit.
- Test quality: zero hard issues across 3,893 tests in 177 files.
- Reachability is 1,513 actions, 2,316 reachable items, 170 known orphan inputs,
  and 190 known blocked actions.
- Compilation, tracked JSON parsing, diff hygiene, placeholder registration,
  asset normalization, and worktree safety pass.
