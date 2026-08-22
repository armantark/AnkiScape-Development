# Action-unit normalisation audit — 2026-08-22

## Runecrafting

The player-facing action is a whole altar batch, not one essence. `runtime/runtime_actions_production.py:1189-1275` calls `apply_runecrafting_action_pure` once for one successful review and awards the returned batch XP once. For standard runes, `logic_pure/logic_pure_runecrafting.py:422-458`:

- consumes `min(capacity, available essence of the first permitted type present)`, so one review consumes 1 to the batch capacity, not exactly one essence;
- produces the corresponding rune multiplier for every essence used; and
- pays `base_exp × essence_used` Runecrafting XP.

The base capacity is 28 essence with a tiara, hood, or staff, and 27 with an inventory talisman (`logic_pure/logic_pure_runecrafting.py:182-189`). Owned, level-eligible pouches add their current capacities (`logic_pure/logic_pure_runecrafting.py:217-232`): small 3, medium 6, large 9, giant 12 (`data/runecrafting_data.py:294-299`). Thus the executable maximum is 58 essence for a standard-rune review (28 + 3 + 6 + 9 + 12), subject to essence on hand and pouch degradation. Combination runes are likewise a batch: one review consumes up to 56 pure essence and the same count of component runes (26 base + up to 30 pouch), consumes one talisman unless Magic Imbue is active, produces up to that many combination runes, and pays `base_exp × craft_count` (`logic_pure/logic_pure_runecrafting.py:460-495`).

**Unit conclusion:** the ledger's complete-altar-trip rates already use the same action boundary as an AnkiScape Runecrafting review. Multiplying trips/hour by essence/trip would convert to essence/hour, not reviews/hour.

## Smithing

At the default review-action multiplier of 1, one successful review applies exactly one selected recipe. `runtime/runtime_actions_production.py:1395-1500` calls `apply_smithing_action_pure` once; `logic_pure/logic_pure_smithing.py:356-392` deducts that recipe's requirements, adds its declared output quantity, and returns that recipe's XP for one award. The pure function explicitly defines this as “one source-shaped Smithing action”; the older entry point likewise says XP-bearing Smithing ignores recipe batch size (`logic_pure/logic_pure_smithing.py:281-304`). Examples from `data/smithing_data.py` are:

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
