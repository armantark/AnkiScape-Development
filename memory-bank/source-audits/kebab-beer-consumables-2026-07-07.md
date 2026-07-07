# Kebab and Beer Consumables — Source Audit

Audited and **implemented** 2026-07-07 (owner: both edible with source
effects; combat auto-eat opt-in only, satisfied by excluding them from
COMBAT_FOOD_DATA).

## Kebab (2011Scape `Foods.kt calculateKebabEffect`, wiki-pinned Oct 2011:
`https://runescape.wiki/w/Kebab?oldid=4868155`)

Roll `Random.nextDouble(100)`:

| Range | Effect |
| --- | --- |
| < 8.71 | nothing ("That kebab didn't seem to do a lot.") |
| < 69.95 | heal 10% of max Constitution (LP) |
| < 91.07 | heal uniform 100..200 LP (`nextInt(100, 201)`) |
| < 94.72 | heal 300 LP **and** +2..3 (`nextInt(2, 4)`) to Attack, Strength, Defence current levels |
| else | lower a random non-Constitution skill (ids 0..24) by a few levels |

Kebab is excluded from the normal heal path (`heal = 0` in `Food.kt`; no
"restores health" message branch).

## Beer (2011Scape `PotionType.BEER` — it is a *potion* in the engine)

Strategies applied to current levels: `beerHealth` = +1 Constitution tick
(10 LP heal), `beerStrength` = `+floor(currentStrength * 0.04)`,
`beerDrain` = `-floor(currentAttack * 0.07)`.

## Implementation

The drain-only `combat_stat_drains` scaffolding was generalized into a signed
`combat_current_levels` substrate (engine `setCurrentLevel` model: absolute
current levels, absence = base; restores 1 toward base per 100 ticks in both
directions). This is shared infrastructure future potions reuse via
`apply_combat_stat_delta_pure`. `apply_consumable_pure(player_data, item_name,
rng)` consumes one item, applies heals + boosts/drains, and is undo-safe.
`CONSUMABLE_DATA` (combat_data.py) holds the source tables; the Bank
right-click Eat/Drink action routes through `on_consume_item`. Storage config
28 drops the dead scaffolding key. Combat auto-eat still ignores both (they
are not in COMBAT_FOOD_DATA), satisfying the opt-in decision; a future
food-priority opt-in for in-combat drinking remains available.

### Remaining follow-up

Kebab/beer are consumable from the Bank (out of combat). In-combat auto-eat
opt-in (ranking them in food priority so auto-eat may drink them) is the
one deferred piece; it needs auto-eat to understand stat side effects.
