# Bogrog pouch-exchange source audit (2026-07-17)

Scope: close Bogrog's pre-EOC pouch-for-shard service as a real Shop action.
Cutoff: 2012-11-20.

## Pinned period sources

- **Bogrog**, oldid
  [6222092](https://runescape.wiki/w/Bogrog?oldid=6222092),
  2012-09-09 19:35:09 UTC.
- **Summoning pouches**, oldid
  [6438719](https://runescape.wiki/w/Summoning_pouches?oldid=6438719),
  2012-10-18 21:44:17 UTC, already transcribed by
  `tools/generate_summoning_catalog.py`.

The tables give an explicit required Summoning level and returned-shard count
for each accepted pouch. The level column must be used directly: it contains
exceptions such as Bull ant requiring level 47 and is not safely reconstructed
from a single formula. Pouches are exchanged for 70% of their creation shards,
rounded up, but the explicit source row remains authoritative.

## Closed catalog

The generated Summoning catalog contains 78 eligible surface pouches. Meerkat
and Ghast have no fabricated ordinary infusion/exchange row and remain
excluded. Each accepted service carries:

- the exact pouch item ID and canonical pouch name;
- the exact source-table level;
- the exact returned spirit-shard count; and
- the stable familiar ID used by the Summoning catalog.

Pack yak is the high-end regression row: level 97 and 148 shards. Bull ant is
the exception regression row: level 47 rather than a derived level.

## Implemented boundary

Bogrog appears as an NPC provider in the existing Shop surface. Exchange is a
free, immediate, quantity-aware service: it consumes only owned pouches,
clamps an oversized request, returns the exact shards, awards no Summoning XP,
and does not advance the shop/economy clock. The ordinary Shop event ledger
makes the whole batch independently undoable.

`tools/generate_npc_shop_data.py --services-only` regenerates all 78 rows from
the pinned Summoning catalog. The generated Shop catalog and coverage ledger
therefore cannot silently drift from pouch data.
