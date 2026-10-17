# Agility trip-cost input audit — 2026-07-15

Cutoff: `2012-11-20T00:00:00Z`. This audit answers the open sourcing item in
`agility-run-energy-contract-2026-07-14.md`; it does not implement the model.
Period facts and AnkiScape abstractions are deliberately separated.

## Verdict

1. The Explorer's-ring conflict is closed. The freeze-date effect is **10%**, not
   `1.125`: Explorer's ring 3 and 4 each say that every essence has a 10% chance
   to produce an extra elemental rune and that the extra rune awards the base XP
   again. The old `Template:Runering` value `1.125` is a stale helper and loses
   to the later item pages.
2. Runecrafting standard-altars have explicit seconds-per-circuit. Those times
   can directly produce a review cost for a whole travel-dominated conversion.
3. Crafting and Smithing each have a conditioned bank-to-station circuit whose
   source action count lets the existing one-review-per-processing-action model
   subtract the interaction portion. Those **target-specific** remainders close.
4. Prayer has period XP/hour anchors, but the closed Ectofuntus circuit includes
   grinding, slime collection, worship, and token collection in addition to
   travel. The formula `R / actions_per_hour - 1` would incorrectly make all of
   those stages Agility-waivable. A pure Prayer trip cost remains blocked.

## 1. Runecrafting elemental-ring conflict

### Controlling evidence

- `Explorer's ring 3`, oldid
  [`6518088`](https://runescape.wiki/w/Explorer%27s_ring_3?oldid=6518088),
  `2012-11-01T23:05:00Z`: 10% chance per essence for Air, Earth, Fire, or Water;
  every extra rune awards the base XP again.
- `Explorer's ring 4`, oldid
  [`6555772`](https://runescape.wiki/w/Explorer%27s_ring_4?oldid=6555772),
  `2012-11-14T22:44:53Z`: the same 10% rule and the worked expectation of `2.8`
  extra essence-equivalents from 28 essence.
- `Template:Runering`, oldid
  [`1731915`](https://runescape.wiki/w/Template%3ARunering?oldid=1731915),
  `2009-09-14T23:10:05Z`: hardcodes `1.125` for Air, Water, Earth, and Fire.
- `Template:Runecrafting training`, oldid
  [`1736191`](https://runescape.wiki/w/Template%3ARunecrafting_training?oldid=1736191),
  `2009-09-16T19:20:31Z`: multiplies the route calculation by that helper.

The template is older by more than three years and conflicts with two later
item-specific pages. No averaging is valid. The freeze-date multiplier is
`1.10` when the ring is equipped and `1.00` otherwise.

Runecrafting gloves double only the ordinary rune XP; the ring's extra-rune XP
is not doubled (`Explorer's ring 2`, oldid
[`6060464`](https://runescape.wiki/w/Explorer%27s_ring_2?oldid=6060464)). The
combined expected multiplier is therefore `2.10`, not `2.20` or the stale
template-derived `2.25`. This changes XP output, not route duration or circuit
count.

### Corrected elemental rows

The route inputs come from `Free-to-play Runecrafting training`, oldid
[`6547046`](https://runescape.wiki/w/Free-to-play_Runecrafting_training?oldid=6547046),
`2012-11-10T19:16:38Z`. The guide supplies `Time` and `Ess`; the normal XP per
essence is pinned in `Runecrafting`, oldid
[`6580390`](https://runescape.wiki/w/Runecrafting?oldid=6580390),
`2012-11-19T06:05:25Z`.

| Route | Seconds/circuit | Essence | Base XP/essence | No-ring XP/hour | Correct 10% ring XP/hour | Stale 12.5% result |
|---|---:|---:|---:|---:|---:|---:|
| Air, Varrock west | 75 | 28 | 5.0 | 6,720 | **7,392** | 7,560 |
| Water, Draynor | 135 | 28 | 6.0 | 4,480 | **4,928** | 5,040 |
| Earth, Varrock east | 90 | 28 | 6.5 | 7,280 | **8,008** | 8,190 |
| Fire, Al Kharid | 80 | 28 | 7.0 | 8,820 | **9,702** | 9,923 after rounding |

The earlier recon's `8,820` Fire row is the **no-ring** rate. The old helper
would also multiply Fire, so it cannot simultaneously be described as a
template-rendered ring rate.

The ring changes XP per conversion, not circuit count. With `R = 1000`, the
whole-trip review costs are therefore obtained directly from the sourced
circuits per hour, independent of either ring multiplier:

```text
travel_reviews_per_conversion = 1000 / (3600 / seconds_per_circuit) - 1
```

| Route | Conversions/hour | Reviews including conversion | Travel reviews |
|---|---:|---:|---:|
| Air | 48 | 20.8333 | 19.8333 |
| Water | 26.6667 | 37.5 | 36.5 |
| Earth | 40 | 25 | 24 |
| Fire | 45 | 22.2222 | 21.2222 |

These are route-specific values, not one Runecrafting constant. The Nature
fairy-ring/glory route remains the better member anchor: oldid
[`6530445`](https://runescape.wiki/w/Pay-to-play_Runecrafting_training?oldid=6530445)
states 30 two-minute trips/hour with 43 essence, so the same calculation gives
`32.3333` travel reviews plus one conversion review.

## 2. Crafting

`Pay-to-play Crafting training`, oldid
[`6547050`](https://runescape.wiki/w/Pay-to-play_Crafting_training?oldid=6547050),
`2012-11-10T19:18:30Z`, supplies several conditioned rates:

| Method | Period statement | Actions/hour | What it proves |
|---|---|---:|---|
| Dragonhide bodies | about 1,000 bodies/hour; 186 base XP/body, 3 leather/body | 1,000 | A bank-adjacent optimal method already meets `R=1000`; the proposed formula yields zero extra reviews. |
| Elemental battlestaves | about 2,200/hour; 100 XP for water staff | 2,200 | It exceeds one action/review and requires the cadence overflow rule; it cannot define positive travel cost. |
| Unstrung symbols | 40,000 XP/hour; 50 XP each; 27 per load | 800 | **Closed target anchor:** 27 action reviews account for the 27 furnace crafts; the remaining `6.75` reviews represent the bank/furnace circuit. |
| Ardougne urns | about 420 urns/hour; 95 XP each | 420 | The rate contains mining clay, softening, wheel, kiln, and movement. Calling the full remainder a bank run would be false. |

The unstrung-symbol recipe is corroborated by
`/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting/silver/SilverData.kt:15`
and `SilverAction.kt:28`. Its exact calculation is:

```text
40,000 / 50 = 800 actions/hour
1000 / 800 - 1 = 1/4 overhead review/action
27 * 1/4 = 27/4 = 6.75 circuit reviews/load
```

**Finding:** Crafting closes only when costs are target-specific. Under the
contract's “optimal period route” rule, dragonhide bodies contradict the prior
`weak` per-skill tier: the source-supported formula returns zero. Do not turn the
symbol circuit into a positive cost on every Crafting method.

## 3. Smithing

The cleaner standard-anvil anchor is in `Free-to-play Smithing training`, oldid
[`6545681`](https://runescape.wiki/w/Free-to-play_Smithing_training?oldid=6545681),
`2012-11-10T00:05:33Z`: level-33 iron platebodies at the Varrock west-bank
anvils, hammer plus 25 bars, five bars/body, five bodies and 625 XP/load,
approximately 65,000 XP/hour, and roughly 35 seconds/circuit. The emulator
corroborates the five-bar, 125-XP recipe at
`/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/smithing/data/BarType.kt:23`,
`SmithingType.kt:301`, `BarProducts.kt:263`, and `SmithingAction.kt:35`.

```text
65,000 / 125 = 520 actions/hour
1000 / 520 - 1 = 12/13 overhead review/action
5 * 12/13 = 60/13 = 4.615384... circuit reviews/load

cross-check: 625 * 3600 / 35 = 64,285.7 XP/hour
```

The `65,000` quote and `35`-second circuit agree within ordinary guide rounding.
Five action reviews account for the five body interactions; the remaining
`60/13` reviews cover bank/anvil travel and bank interaction. This is a closed
target-specific anchor.

`Pay-to-play Smithing training`, oldid
[`6487800`](https://runescape.wiki/w/Pay-to-play_Smithing_training?oldid=6487800),
`2012-10-28T04:53:46Z`, supplies additional methods that should not replace it:

| Method | Period statement | Derived action rate | Proven inclusions / ambiguity |
|---|---|---:|---|
| Adamant platebody | up to 200,000 XP/hour; 312.5 XP/body; 5 bars | 640 bodies/hour | A faster target-specific alternative, but the page gives no independent circuit-time check. |
| Mithril bar, normal furnace | 300 bars/hour; 9,000 XP/hour | 300 bars/hour | Explicit full-cycle rate, but ore/coal load and smelting time dominate. |
| Gold bars | 55,000–90,000 XP/hour at 56.2 XP/ore | about 979–1,601 ores/hour | Range crosses `R`; Varrock armour and concentration change it. |
| Cannonballs | about 13,000 XP/hour; 25.6 XP/steel bar | about 508 bars/hour | Long cannonball processing animation is the method's defining delay. |

For adamant platebodies the proposed formula gives `0.5625` extra reviews per
body, or `2.8125` per five-body/25-bar load. Keep it as a rate lead; the iron row
has the stronger internal circuit cross-check. Neither value licenses one global
Smithing cost across furnace, anvil, cannonball, and Blast Furnace methods.

## 4. Prayer

`Pay-to-play Prayer training`, oldid
[`6571012`](https://runescape.wiki/w/Pay-to-play_Prayer_training?oldid=6571012),
`2012-11-18T04:42:08Z`, supplies two useful but differently conditioned anchors:

| Method | Period statement | Actions/hour | Why it cannot isolate travel |
|---|---|---:|---|
| Gilded altar, dragon bones | approximately 230,000 XP/hour at 252 XP/bone, using house teleport, ring teleport, and a War tortoise | about 912.70 bones/hour | Includes altar offering, banking, teleports, familiar handling, and burner assumptions. |
| Ectofuntus, dragon bones | 13 bones in about 4.5 minutes; 3,744 XP/set; 49,920 XP/hour | 173.33 bones/hour | Includes grinding, slime collection, worship, token collection, teleporting, and banking. Most of the remainder is not travel. The fully conditioned setup additionally uses the level-58 Agility shortcut and a level-52 Spirit terrorbird carrying 12 buckets (`Ectofuntus` oldid [`6544994`](https://runescape.wiki/w/Ectofuntus?oldid=6544994), `2012-11-09T13:32:24Z`). |

The 230,000 rate yields about `0.09565` extra review per bone under the proposed
formula. Multiplying that by an AnkiScape 28-bone load gives about `2.678`
reviews, but the source method used a War tortoise and does not state a matching
28-bone player load. That number is useful only as a bounded design lead.

The same oldid reports a non-rigorous 43-bone, roughly two-minute trip producing
over 284,000 XP/hour. Its three figures are not arithmetically exact:
`43 × 252 × 30 = 325,080`, not 284,000. Preserve the observation; do not choose
one implied time silently.

### Bury and Scatter have no travel (Pass 16, 2026-10-15)

Burying bones and scattering ashes need no altar. Darkan buries from the
inventory item click (`InventoryOptionsHandler.java:407-409` calls
`Burying.Bone.bury`, which checks only the `canBury()` tick delay at
`Burying.java:98`; commit `1912a55cb245cc4410e51b200f9ad4c5e480510f`), and
`Bones` oldid [`6477812`](https://runescape.wiki/w/Bones?oldid=6477812) says
"Normal bones give 4.5 Prayer experience when buried". The optimal route
therefore buries beside the bank, like the Crafting and Herblore bank methods:
every `bury_*` and `scatter_*` target costs `0.0` travel reviews
(`period_route`, "Working at the bank") in `logic/agility_travel.py`.

The `2.678` lead above came from the gilded altar rate, so it stays with the
altar methods only: `gilded_altar_*` targets, and the Ectofuntus, which already
took the same lead from the Prayer handler default and keeps it because its
multi-stage cycle still isolates no travel cost. Owner decision: Pass 16 spec,
"Prayer bank trips".

## Shipping consequence

The source-safe input shape is:

```text
Runecrafting: route-specific circuit seconds -> exact whole-trip reviews
Crafting:     target-specific symbol circuit -> 27/4 reviews/load
Smithing:     target-specific iron-body circuit -> 60/13 reviews/load
Prayer:       total multi-stage cycle anchors -> pure travel source_blocked
```

If AnkiScape still wants one per-skill cost instead of route/target costs, the
smallest honest abstraction is to choose it from the walk/stand tier and label it
`ankiscape_trip_abstraction`. Do not cite one conditioned target as proof of a
universal skill duration. A later implementation should also reconsider Crafting
(`none` for its optimal bank method), Prayer (separate altar and Ectofuntus
cycles), and Combat (its only modeled restock trip was declared unaffected),
rather than preserving those tier labels by inertia.
