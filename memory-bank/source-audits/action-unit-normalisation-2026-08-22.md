# Action-unit normalisation audit — 2026-08-22

## Runecrafting

The player-facing action is a whole altar batch, not one essence. `runtime/runtime_actions_production.py:1189-1275` calls `apply_runecrafting_action_pure` once for one successful review and awards the returned batch XP once. For standard runes, `logic_pure/logic_pure_runecrafting.py:422-458`:

- consumes `min(capacity, available essence of the first permitted type present)`, so one review consumes 1 to the batch capacity, not exactly one essence;
- produces the corresponding rune multiplier for every essence used; and
- pays `base_exp × essence_used` Runecrafting XP.

The base capacity is 28 essence with a tiara, hood, or staff, and 27 with an inventory talisman (`logic_pure/logic_pure_runecrafting.py:182-189`). Owned, level-eligible pouches add their current capacities (`logic_pure/logic_pure_runecrafting.py:217-232`): small 3, medium 6, large 9, giant 12 (`data/runecrafting_data.py:294-299`). Thus the executable maximum is 58 essence for a standard-rune review (28 + 3 + 6 + 9 + 12), subject to essence on hand and pouch degradation. Combination runes are likewise a batch: one review consumes up to 56 pure essence and the same count of component runes (26 base + up to 30 pouch), consumes one talisman unless Magic Imbue is active, produces up to that many combination runes, and pays `base_exp × craft_count` (`logic_pure/logic_pure_runecrafting.py:460-495`).

**Unit conclusion:** the ledger's complete-altar-trip rates already use the same action boundary as an AnkiScape Runecrafting review. Multiplying trips/hour by essence/trip would convert to essence/hour, not reviews/hour.
