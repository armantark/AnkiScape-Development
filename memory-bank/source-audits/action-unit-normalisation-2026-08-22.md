# Action-unit normalisation audit — 2026-08-22

## Runecrafting

The player-facing action is a whole altar batch, not one essence. `runtime/runtime_actions_production.py:1189-1275` calls `apply_runecrafting_action_pure` once for one successful review and awards the returned batch XP once. For standard runes, `logic_pure/logic_pure_runecrafting.py:422-458`:

- consumes `min(capacity, available essence of the first permitted type present)`, so one review consumes 1 to the batch capacity, not exactly one essence;
- produces the corresponding rune multiplier for every essence used; and
- pays `base_exp × essence_used` Runecrafting XP.

The pure kernel's base capacity is 28 essence with a tiara, hood, or staff, and 27 with an inventory talisman (`logic_pure/logic_pure_runecrafting.py:182-189`). Owned, level-eligible pouches add their current capacities (`logic_pure/logic_pure_runecrafting.py:189-204`): small 3, medium 6, large 9, giant 12 (`data/runecrafting_data.py:294-299`), so the isolated pure-function ceiling is 58.

The player-facing runtime does **not** reach that pouch ceiling. Standard Runecrafting is packed through the 28-slot carried overlay as a one-input recipe (`65dd909d:runtime/runtime_actions_carried.py:488-548,871-1002`). The packer carries at most 28 loose essence (`logic/inventory_pure.py:16,248-288`), and its only bag definition is the Coal bag (`logic/inventory_pure.py:32-40`); essence pouches neither add carried essence nor hold separate pouch contents. The handler therefore sees at most 28 essence: it consumes 27 with talisman access or 28 with tiara/hood/staff access, regardless of owned pouch capacities. Pouches raise a pure-function cap that the standard player-facing path cannot fill. Combination runes follow a separate unscoped path and can consume up to 56 pure essence plus 56 component runes per review (`logic_pure/logic_pure_runecrafting.py:432-467`), but the ledger deliberately excludes combination-rune rates.

**Unit conclusion:** the ledger's complete-altar-trip boundary is still the same boundary as an AnkiScape standard-rune review; multiplying trips/hour by essence/trip would incorrectly change the action to essence. However, pouch routes carrying 43 or 52 essence must be re-denominated against AnkiScape's actual 28-essence review payout, because the executable runtime does not load those pouch contents.

## Smithing

At the default review-action multiplier of 1, one successful review applies exactly one selected recipe. `runtime/runtime_actions_production.py:1395-1500` calls `apply_smithing_action_pure` once; `logic_pure/logic_pure_smithing.py:350-386` deducts that recipe's requirements, adds its declared output quantity, and returns that recipe's XP for one award. The pure function explicitly defines this as “one source-shaped Smithing action”; the older entry point likewise says XP-bearing Smithing ignores recipe batch size (`logic_pure/logic_pure_smithing.py:275-298`). Examples from `data/smithing_data.py` are:

- one mithril-bar action consumes 1 mithril ore + 4 coal, produces 1 mithril bar, and pays 30 XP (`data/smithing_data.py:184-204`);
- one mithril-dart-tip action consumes 1 mithril bar, produces 10 tips, and pays 50 XP (`data/smithing_data.py:2036-2055`); and
- one mithril-platebody action consumes 5 mithril bars, produces 1 platebody, and pays 250 XP (`data/smithing_data.py:2414-2434`).

A configured review-action multiplier can repeat the same normal action 1 to 10 times per review (`__init__.py:5395-5435`; `logic_pure/logic_pure_progression.py:329-345`), but that common outer multiplier does not change the cross-skill unit comparison at the invariant's stated one-action setting.

**Unit conclusion:** Smithing ledger rates expressed as bars/hour or forged items/hour already count the corresponding AnkiScape action. Blast Furnace may process an in-game inventory as a route, but each bar is one AnkiScape Smithing action; no inventory-size conversion is due.

## Crafting

At multiplier 1, one successful review resolves one selected recipe. The handler performs one `apply_crafting_pure` call and awards its returned XP once (`runtime/runtime_actions_production.py:502-552`). The pure action deliberately caps `batch_count` at 1 because Crafting is XP-bearing (`logic_pure/logic_pure_production.py:221-249`):

- it consumes one recipe's `requirements` quantities;
- `required_items` are availability gates/tools and are not consumed;
- leather recipes consume one Thread only on the recipe's one-in-five thread roll;
- it produces one recipe's `output_qty`, plus any declared byproducts; and
- it pays exactly one recipe's `exp`.

**Unit conclusion:** a Crafting ledger row expressed as completed recipe outputs/hour is already in AnkiScape actions/hour. An output stack made by one recipe (rather than each member of that stack) is the action unit; there is no inventory-batch conversion.

## Magic

At multiplier 1, one successful review is one cast. `runtime/runtime_actions_magic.py:417-514` invokes `apply_magic_action_pure` once, increments `magic_actions_completed` by 1, and awards the returned Magic XP once. The pure function names its boundary “one ... noncombat cast” (`logic_pure/logic_pure_magic.py:376-398`): it consumes one cast's effective rune cost (staff-covered elemental runes are waived), consumes that spell's dynamic item requirements, applies the spell effect, and returns the spell's flat `exp` (`logic_pure/logic_pure_magic.py:398-552`).

Spell effects do not redefine the action boundary. High Level Alchemy consumes one selected tradeable item and one cast's runes, produces coins, and pays 65 Magic XP (`data/magic_data.py:95`; `logic_pure/logic_pure_magic.py:411-415`). By contrast, inventory spells such as Humidify, Superglass Make, and String Jewellery affect their coded inventory batch in one cast while still paying one flat Magic XP award (`logic_pure/logic_pure_magic.py:433-472`; `data/magic_data.py:405-409`).

**Unit conclusion:** the common action unit is casts/hour, not items transformed/hour. A ledger rate inferred from flat Magic XP per cast is directly comparable; a rate based on the number of inventory items affected by a batch spell would require conversion back to casts.

## Prayer

An XP-bearing Prayer review consumes one material unit. After any runtime-side access/cadence step, `runtime/runtime_actions_production.py:771-869` calls `apply_prayer_action_pure` once, increments `prayer_actions_completed` by 1, and awards its returned XP once. The pure function is explicitly “one normal Prayer training action”: it deducts one target's requirements, adds declared byproducts/outputs, and returns one target's XP (`logic_pure/logic_pure_prayer.py:121-145`). `data/prayer_data.py:119-161` makes the concrete units:

- bury/scatter consumes 1 bone or ash, produces nothing, and pays that material's base XP;
- Ectofuntus consumes 1 bonemeal (or ash) + 1 bucket of slime, returns the containers, produces 5 Ecto-tokens, and pays 4× base XP; and
- a gilded altar consumes 1 bone or ash and pays up to 3.5× base XP.

Hosted gilded-altars have one player-visible exception: the first stint spends 1 to 10 successful reviews finding a house, with no material consumed and no XP, before one-material offering reviews begin (`runtime/runtime_actions_production.py:782-803`; `logic_pure/logic_pure_prayer.py:148-162`). Owned altars instead consume marrentill once when a stint begins according to the burner count (`runtime/runtime_actions_production.py:794-809`).

**Unit conclusion:** Prayer ledger rates in bones/ashes offered per hour are AnkiScape XP-bearing actions/hour. Ectofuntus must be counted in worships/material units, not its component preparation clicks; hosted-house search is separate modeled review friction rather than a different material unit.

## Common-unit restatement

The common unit is **one XP-bearing invocation of the selected skill handler at review-action multiplier 1**. Banking, travel, hosted-house search, and cadence waits are review friction around that action, not extra units inside it. In particular, one standard Runecrafting invocation is one complete altar load. Multiplying trips/hour by essence/load would answer “essence/hour,” not “AnkiScape actions/hour.”

| Skill | One AnkiScape action at multiplier 1 |
|---|---|
| Runecrafting | One complete standard-rune altar load |
| Smithing | One selected smelt or forge recipe; mixed routes count each separately |
| Crafting | One selected recipe, regardless of its output stack size |
| Magic | One spell cast, including a cast with an inventory-wide effect |
| Prayer | One bone, ash, bonemeal, or ash unit buried, scattered, or offered |

The original deterministic-artisan rows are already in that common unit:

| Ledger row | Checkable arithmetic | Actions/hour |
|---|---:|---:|
| Crafting — urns | 39,900 ÷ 95 | 420 |
| Prayer — gilded dragon bones | 230,000 ÷ 252 | 912.698 ≈ 913 |
| Crafting — dragonhide body | 186,000 ÷ 186 | 1,000 |
| Magic — High Level Alchemy | 78,000 ÷ 65 | 1,200 |
| Magic — superheat mithril | 84,800 ÷ 53 | 1,600 |
| Crafting — elemental battlestaves | 220,000 ÷ 100 | 2,200 |

Every Smithing extension row is also already in handler invocations/hour. Mixed Blast Furnace cycles must count each separate smelt and forge invocation:

| Ledger row | Checkable arithmetic | Actions/hour |
|---|---:|---:|
| Ordinary mithril bars | 7,500 ÷ 30 = 9,000 ÷ 36 | 250 |
| Gold bars with stated modifiers | 65,000 ÷ 56.2 to 70,000 ÷ 56.2 | 1,156.584–1,245.552 ≈ 1,157–1,246 |
| Cannonballs | 11,000 ÷ 25.6 | 429.688 ≈ 430 |
| F2P iron platebodies | 65,000 ÷ 125 | 520 |
| Pack-Yak iron platebodies | 95,000 ÷ 125 to 100,000 ÷ 125 | 760–800 |
| F2P mithril platebodies | 130,000 ÷ 250 | 520 |
| F2P adamant platebodies | 162,000 ÷ 312.5 | 518.4 |
| P2P adamant platebodies | 200,000 ÷ 312.5 | up to 640 |
| Blast Furnace mithril bolts | (50,000–60,000) ÷ (30 + 50 XP/cycle) × 2 actions/cycle | 1,250–1,500 |
| Blast Furnace mithril ranged components, Sacred clay hammer | 100,000 ÷ (30 + 100 XP/cycle) × 2 actions/cycle | 1,538.462 ≈ 1,538 |
| Blast Furnace mithril platebodies, Sacred clay hammer | 70,000 ÷ 650 XP/cycle × 6 actions/cycle | 646.154 ≈ 646 |

Every Runecrafting extension row counts one complete altar-load invocation, so no essence multiplication is due:

| Ledger row | Checkable arithmetic | Actions/hour |
|---|---:|---:|
| Air, Varrock west on foot | 6,720 ÷ 140 = 7,392 ÷ 154 = 13,440 ÷ 280 = 14,112 ÷ 294 | 48 |
| Air, Varrock-teleport return | 8,910 ÷ (27 × 5) | 66 |
| Fire, Al Kharid on foot | 8,820 ÷ (28 × 7) | 45 |
| Nature, Edgeville/fairy ring/glory | 11,600 ÷ (43 × 9) | 29.974 ≈ 30.0 |
| Nature, Spirit graahk, small+medium+large | 16,000 ÷ 387; 17,000–18,000 ÷ 387 | 41.344; 43.928–46.512 |
| Nature, Spirit graahk, medium+large+giant | 27,000 ÷ (52 × 9) | 57.692 ≈ 57.7 |
| Nature, Zanaris | 5,800 ÷ (43 × 9) | 14.987 ≈ 15.0 |

### Current-runtime pouch correction

The source action boundary matches, but the current player-facing pouch payload does not. The runtime carried overlay supplies at most 28 loose essence, so a standard Nature-rune review pays at most `28 × 9 = 252 XP`, not the source routes' 387 or 468 XP loads. If `R` is recomputed as the cadence denominator needed for **current executable XP/review**, the pouch rows become:

| Pouch route | Arithmetic against current 252-XP review | Executable-payout R |
|---|---:|---:|
| Edgeville/fairy ring/glory | 11,600 ÷ 252 | 46.032 |
| Spirit graahk, ordinary | 16,000 ÷ 252 | 63.492 |
| Spirit graahk, fast clicker | 17,000–18,000 ÷ 252 | 67.460–71.429 |
| Spirit graahk, medium+large+giant | 27,000 ÷ 252 | 107.143 |
| Zanaris | 5,800 ÷ 252 | 23.016 |

These are not evidence that one review equals one essence. They quantify a separate executable mismatch: pouches are recognized by the pure Runecrafting kernel but do not load pouch-contained essence through the carried overlay.

## Verdict

**The contradiction survives.** Smithing and Runecrafting were already using the same action boundary: one successful AnkiScape handler invocation. The proposed `trips/hour × essence/trip` conversion is therefore a unit change, not a normalisation.

- On the ledger's source-action measure, Smithing plus Runecrafting span 14.987 to 1,538.462 actions/hour: **102.65×**. Excluding the internally contradictory Zanaris row, they still span 29.974 to 1,538.462: **51.29×**.
- Across all five audited skills, the ledger spans 14.987 to 2,200 actions/hour: **146.79×**.
- Even if every pouch row is instead recomputed against the current runtime's smaller 28-essence payout, Smithing plus Runecrafting still span 23.016 to 1,538.462: **66.84×**, and all five skills span 23.016 to 2,200: **95.59×**.
- Smithing alone spans 250 to 1,538.462: **6.15×**, so the universal constant already fails without relying on Runecrafting at all.

No cadence constant, XP value, or executable behavior is changed by this audit.
