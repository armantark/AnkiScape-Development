# Bittercap spore identity — 2026-10-14

Status: **implemented at the Farming material boundary**. Cutoff: `2012-11-20T00:00:00Z`.

The Bittercap crop keeps its `Mushroom spore` input key. Vinesweeper and the Master Farmer grant `Bittercap mushroom spore`. Both names identify item `5282`, so planting accepts either stack.

| Value | Exact source |
| --- | --- |
| The mushroom row names `Bittercap mushroom spore`, level 53, 61.5 plant XP, 57.7 harvest XP and six 40-minute stages. | RuneScape Wiki `Farming`, oldid `6565110`, `2012-11-17T05:59:19Z`. |
| `Bittercap mushroom spore` is item `5282`: price 7, buy limit 100, cache value 85. | `data/grand_exchange_period_source.json`, provenance `Exchange:Bittercap mushroom spore`, oldid `6561263`, `2012-11-16T02:24:06Z`. |
| Item `5282` has `uidName=bittercap_mushroom_spore` and the Bittercap spore examine text. | Darkan `data/items/config.json` at commit `1912a55cb245cc4410e51b200f9ad4c5e480510f`. |
| Seed `5282` produces item `6004` at level 53 with 61.5/57.7 XP. | Darkan `src/main/java/com/rs/game/content/skills/farming/ProduceType.java`, same commit. |

Independent qualification: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/bittercap-identity-qualification-1/report.md` and `verdict.json`, which hold the file hashes.

## Rule

`logic/farming/materials.py` resolves each Farming requirement map before any check or debit. A sufficient `Mushroom spore` stack is used first. Otherwise one `Bittercap mushroom spore` stack must cover the whole amount plus any separate requirement on that key. Two short stacks are never pooled. When neither stack covers the seed, the original requirement and refusal text stand.

## Kept unchanged

- Crop `bittercap`, Farming item `farming_mushroom_spore`, label `Mushroom spore`, image `farmingitems/mushroom_spore.png`.
- Registry rows `material_mushroom_spore` and `material_bittercap_mushroom_spore`, with their keys, labels and null `source_item_id`.
- Both saved inventory keys and counts: no rename, merge or migration.
- Every producer, rate, price and the Miscellania `Mushroom spore` output.

Not established: a shared registry ID for the two rows. Neither `source_item_id` is assigned here.
