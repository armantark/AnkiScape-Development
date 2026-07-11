# Gap Grill 16: Skilling Runtime Provenance

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

## Reconstruction evidence inspected

- `game-main` `PotionType.kt`, `Potion.kt`, `Potions.kt`, and
  `potionDrinking.plugin.kts`: Crafting and Fletching potion dose families;
  exact +3 current-level strategy; dose replacement; and drinking delay.
- `game-main` `stat_restoration.plugin.kts`: all temporary non-Constitution,
  non-Prayer levels move one point toward base every 100 game ticks.
- `game-main` `BrawlingGloves.kt`, `PlayerExt.kt`, and live skilling call sites:
  per-skill glove items and maximum charges; level-scaled first-use charges;
  Wilderness/non-Wilderness XP multipliers; one charge per XP award;
  disintegration at zero; and live calls from Mining, Smithing, Woodcutting,
  Fishing, Cooking, and Firemaking.

## Evidence boundary

These files establish the reconstruction's internally consistent runtime and
are sufficient to settle the AnkiScape product shape. They are not, by
themselves, period proof. Exact potion-restoration pacing, brawling-glove
multipliers and charges, glove acquisition, and Wilderness danger cadence must
still be corroborated by pinned pre-cutoff evidence or high-fidelity Darkan
before implementation values are declared final.

The product decisions do not depend on those unresolved numbers: potions use
the target-local `Use potions` contract, and brawling gloves use a target-local
`Train in Wilderness` checkbox plus shared equipment, HP, inventory, death, and
undo contracts.
