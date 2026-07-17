# Agility carried-weight input audit — 2026-07-15

Cutoff: `2012-11-20T00:00:00Z`. This audit closes the item-input portion of the
Agility run-energy harvest. It does not implement a weight model. Item weights,
representative inventories, and AnkiScape defaults are kept separate because
only the first category is a RuneScape fact.

## Verdict

1. RuneScape defines weight per item, not per skill. A single “Woodcutting
   weight” or “Smithing weight” is therefore an AnkiScape abstraction.
2. The most faithful input is the weight of the target-specific carried pack
   that AnkiScape already models: sum each carried item, equipped item, and
   weight-reducing item, then clamp the result at `0 kg`.
3. If implementation still needs one scalar per skill, the representative loads
   below are defensible defaults, but they must be stored and described as
   `ankiscape_representative_load`, not cited as period-authentic constants.
4. The old contract's statement that Prayer is “near-zero weight” is false for
   its own dragon-bone route: 28 dragon bones weigh `42 kg` in the available
   item config.
5. The Agile top/legs sign conflict is a data-quality trap. Period evidence and
   the primary Darkan item IDs say `-12 kg` and `-10 kg`; the positive duplicate
   IDs and positive game-main rows do not overturn them.

## Evidence and confidence

The period `Weight` page, oldid
[`6512729`](https://runescape.wiki/w/Weight?oldid=6512729), is controlling for
the behavioral rules and weight-reduction equipment: carried and equipped items
contribute to total weight, negative total weight is treated as `0 kg` for run
energy, Agile top is `-12 kg`, and Agile legs are `-10 kg`.

Individual ordinary-item weights below were checked in both Darkan
(`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/items/config.json`,
commit `32c65effabe8dc5e232fa72659237061394e06ae`) and 2011Scape
(`/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml`). Agreement is
independent emulator convergence, not a pinned period fact. The 2012 client
caches expose item identity but no weight field, so ordinary-item rows remain
**emulator reconstruction** unless independently period-corroborated.

| Item | Weight | Config lines | Disposition |
|---|---:|---|---|
| Rune essence | 0 kg | `items.yml:18745-18748` | Emulator reconstruction |
| Pure essence | 0 kg | `items.yml:87379-87382` | Emulator reconstruction |
| Small / medium / large / giant pouch | 1 kg each | `items.yml:60224-60227`, `60230-60233`, `60242-60245`, `60254-60257` | Emulator reconstruction |
| Nature tiara | 1 kg | `items.yml:60635`; Darkan `config.json:62497` | Emulator convergence |
| Amulet of glory (4) | 0 kg | `items.yml:21125`; Darkan `config.json:19987` | Emulator convergence |
| Dragon bones | 1.5 kg | `items.yml:4007-4010` | Emulator reconstruction |
| Magic logs | 2 kg | `items.yml:19285-19288` | Emulator reconstruction |
| Iron ore | 2.25 kg | `items.yml:3063-3066` | Emulator reconstruction |
| Raw shark | 0.7 kg | `items.yml:2625-2628` | Emulator reconstruction |
| Raw rocktail | 0.3 kg | `items.yml:179820-179823` | Emulator reconstruction |
| Red chinchompa | 0 kg | `items.yml:108959`; Darkan `config.json:112731`; period item page oldid `6447108` | Period-corroborated convergence |
| Box trap | 0.2 kg | `items.yml:108696-108699` | Emulator reconstruction |
| Adamant bar | 2.04 kg | `items.yml:25493-25496` | Emulator reconstruction |
| Adamant platebody | 11 kg | `items.yml:12632-12635` | Emulator reconstruction |
| Green dragon leather | 3.1 kg | `items.yml:21557-21560` | Emulator reconstruction |
| Green d'hide body | 6.8 kg | `items.yml:12871-12874` | Emulator reconstruction |
| Vial of water | 0.02 kg | `items.yml:1580-1583` | Emulator reconstruction |
| Clean torstol | 0 kg | `items.yml:1832-1835` | Emulator reconstruction |
| Extreme attack/strength/defence/magic/ranging and clean torstol | 0 kg each | `items.yml:180083`, `180107`, `180131`, `180155`, `180179`, `1835`; matching Darkan rows | Emulator convergence |

### Post-closure dangerous-course pack inputs — 2026-07-17

The carried-risk amendment makes food and course requirements part of the
actual Agility target pack, so their weights are now runtime inputs rather than
incidental Bank items. The same 2011Scape item config supplies:

| Item family | Weight | Config lines | Disposition |
|---|---:|---|---|
| Shark / swordfish / lobster | 0.6 / 0.4 / 0.3 kg | `items.yml:2637-2641`, `2565-2569`, `2601-2605` | Emulator reconstruction |
| Tuna / salmon / trout | 0.4 / 0.5 / 0.4 kg | `items.yml:2493-2497`, `2301-2305`, `2325-2329` | Emulator reconstruction |
| Cooked meat / cooked chicken | 0.25 / 0.1 kg | `items.yml:24179-24183`, `24167-24171` | Emulator reconstruction |
| Shrimps / crayfish | 0.5 / 0.1 kg | `items.yml:2217-2221`, `152489-152493` | Emulator reconstruction |
| Ninja monkey greegree / Ring of charos / Mith grapple | 0 / 0 / 0 kg | `items.yml:42517-42521`, `45019-45024`, `102273-102277` | Emulator reconstruction |
| Lit torch / candle lantern / oil lamp / oil lantern | 0.5 / 0.9 / 0.4 / 0.9 kg | `items.yml:4641-4645`, `49659-49663`, `49617-49621`, `49695-49699` | Emulator reconstruction |
| Bullseye / sapphire / emerald lantern | 1.0 / 1.3 / 1.3 kg | `items.yml:49749-49753`, `51073-51077`, `98084-98088` | Emulator reconstruction |
| Lit mining helmet / crossbow | 1.0 / 2.0 kg | `items.yml:56563-56567`, `8050-8055` | Emulator reconstruction |

The AnkiScape names distinguish lit state and, for the Ape Atoll requirement,
the small ninja variant; the emulator rows use the shared base-object names.
The weight is therefore inherited from the matching physical item row, not
invented independently. `Penguin suit` remains `source_blocked` because neither
audited config exposes that synthetic combined inventory identity; its current
zero contribution is an explicit `ankiscape_weight_abstraction`, not a sourced
claim.

The first refill after a dangerous-course pack is exhausted uses the existing
one-review weak-route bank-trip abstraction. This is labeled
`ankiscape_trip_abstraction`: the exact course-to-bank routes are not period
rate claims, but replenishing a physical food pack cannot be free.

### Agile sign-conflict resolution

The same game-main config reports positive weights for item IDs `14936` and
`14938` (`items.yml:177190-177194`, `177254-177258`). Darkan's item config instead
has the primary top/legs rows at `-12` and `-10`
(`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/items/config.json:167904-167913`,
`167926-167935`) while duplicate IDs `14937`/`14939` are positive. Because the
period Weight page independently names the negative values, the controlling
loadout values are:

```text
Agile top  = -12 kg
Agile legs = -10 kg
Agile set  = -22 kg
```

The positive rows are not a second valid gameplay interpretation; they are
conflicting emulator data and must not be averaged or silently selected.

The same sign trap affects other weight-reduction gear in 2011Scape. Period
pages plus Darkan control the equipped values: Boots of lightness `-4.5 kg`
([oldid `6020719`](https://runescape.wiki/w/Boots_of_lightness?oldid=6020719)),
Spotted cape `-2.2 kg` ([oldid
`6308186`](https://runescape.wiki/w/Spotted_cape?oldid=6308186)), and Spottier
cape `-4.5 kg` ([oldid
`6308184`](https://runescape.wiki/w/Spottier_cape?oldid=6308184)). This corrects
the earlier contract's `-2.3 kg` Spotted-cape approximation.

## Representative target loads

The arithmetic below deliberately uses full or route-appropriate inventories.
It demonstrates the magnitude and supplies possible defaults; it does **not**
turn the result into a period per-skill constant.

| Handler / representative target | Load arithmetic | Representative carried weight | Modeling consequence |
|---|---|---:|---|
| Runecrafting, sourced level-50 Nature route | 3 pouches × 1 kg + Nature tiara 1 kg; essence/glory 0 kg | **4 kg** | Light; Boots alone clamp effective weight to zero |
| Prayer, 28 dragon bones (`ankiscape_representative_peak_load`) | 28 × 1.5 kg | **42 kg** | Heavy; the sourced 43-bone War-tortoise route's exact player/familiar split is `source_blocked` |
| Woodcutting, 28 magic logs | 28 × 2 kg | **56 kg** | Heavy gathering load |
| Mining, 28 iron ore | 28 × 2.25 kg | **63 kg** | Heavy gathering load |
| Fishing, 28 raw sharks | 28 × 0.7 kg | **19.6 kg** | Moderate and target-dependent |
| Fishing, 28 raw rocktails | 28 × 0.3 kg | **8.4 kg** | Same skill, materially different target |
| Hunter, five box traps plus caught red chins | 5 × 0.2 kg; catches 0 kg | **1 kg** outbound | Traps are deployed and catches stack at 0 kg; the optimal route has no recurring deposit trip |
| Smithing, 25 adamant bars | 25 × 2.041 kg Darkan / 2.04 kg 2011Scape | **51.025 / 51 kg** inbound | Tiny precision conflict must stay recorded |
| Crafting, 27 green dragon leather | 27 × 3.1 kg | **83.7 kg** inbound | Very heavy, but a bank-standing method makes trip weight irrelevant |
| Cooking, 28 raw rocktails | 28 × 0.3 kg | **8.4 kg** inbound | Target-specific; station placement dominates |
| Firemaking, 28 magic logs | 28 × 2 kg | **56 kg** | Heavy inventory, short bank-side route |
| Fletching, 28 magic logs | 28 × 2 kg | **56 kg** | Heavy inventory, but no travel in the optimal bank method |
| Herblore, four overload batches | Four each of five extreme potions plus clean torstol | **0 kg** | Period-relevant high-level pack; bank-standing |

Combat has no honest representative scalar: armor, weapon, ammunition, food,
potions, summoning inventory, and loot policy all vary independently. Use its
actual equipped/carried state if combat ever participates in the run-energy
model; otherwise leave it out rather than inventing one loadout and calling it
the skill's weight.

## Recommended data contract

```text
effective_weight_kg = max(
    0,
    sum(carried_item_weight × quantity)
  + sum(equipped_item_weight)
)
```

Prefer the runtime target pack. If a target has no item-weight record, mark that
target `source_blocked` for the weight lever or use an explicit
`ankiscape_weight_abstraction`; do not substitute the skill-level representative
load without labeling it. The movement tier remains a separate question: a
heavy inventory at a bank chest (Fletching/Crafting) should not create a travel
bonus merely because the items are heavy.

## Required contract corrections before implementation

- Replace “model per-skill” with “model the actual target load where available;
  labeled representative load otherwise.”
- Correct Prayer from near-zero to a heavy `42 kg` representative bone load.
- Keep RC route weight exact: the sourced Nature route is three pouches
  (`3 kg`) plus the equipped Nature tiara (`1 kg`) for `4 kg` total.
- Preserve the `0 kg` effective-weight clamp and the period-backed Agile
  `-22 kg` set value.
- Do not apply the weight lever to a route whose sourced optimal method has no
  meaningful travel segment.
- Under the current optimal-route rule, Crafting and Hunter are `none`, and
  Combat remains `none` until a non-restock travel transaction exists; weight
  alone cannot create an Agility throughput gain.
- Preserve item precision conflicts rather than silently rounding: Runite ore
  is `2.267 kg` in Darkan versus `2.25 kg` in 2011Scape, and Adamant bars are
  `2.041 kg` versus `2.04 kg`.
