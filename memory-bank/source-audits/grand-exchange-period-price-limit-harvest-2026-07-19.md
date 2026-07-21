# Grand Exchange period price and buy-limit harvest

Date: 2026-07-19

Status: **source-ready period rows generated; 19 collapsed identities remain
buy-limit blocked and use no invented value.**

## Scope and cutoff

This pass pins the nearest useful pre-EOC Grand Exchange guide-price and
four-hour buy-limit rows for the 1,657 registered, cache-exchangeable AnkiScape
items. The cutoff is `2012-11-20T00:00:00Z`.

The reproducible harvester is `tools/generate_ge_period_data.py`. It resolves
literal historical wikitext, checkpoints every response under the ignored
`tools/.cache/grand_exchange_period/` directory, retries network failures and
`HTTP 429` responses, and writes
`grand_exchange_period_generated.py`. It never reads the wall clock to derive
gameplay.

## Period sources

### Complete buy-limit table

RuneScape Wiki `Calculator:Grand Exchange buying limits`, oldid `6457777`,
timestamp `2012-10-23T03:28:03Z`:

<https://runescape.wiki/w/Calculator%3AGrand_Exchange_buying_limits?oldid=6457777>

Its literal table supplies the item title and four-hour limit. The generated
catalog maps exact names, the registry's already-established singular/plural
identity bridge, Unicode fraction spellings, and the period `helm` versus cache
`med helm` display-name difference.

### Item-level Exchange records

Each registered item is independently resolved at `Exchange:<item>` to the
latest revision before the cutoff. Those template records carry `Item`,
`ItemId`, `Price`, `Date`, `Value`, and `Limit`. The generated provenance table
keeps every page title, oldid, UTC timestamp, displayed price date, item ID,
cache value, and page limit.

Representative rows:

| Item | Price | Limit | Page oldid | Revision timestamp |
|---|---:|---:|---:|---|
| Logs | 106 | 25,000 | 6519754 | 2012-11-02T11:05:48Z |
| Yew logs | 494 | 25,000 | 6563500 | 2012-11-16T06:22:26Z |
| Basket | 2 | 1,000 | 6540082 | 2012-11-07T02:25:59Z |

The item-level `Limit` field agrees with the October aggregate table for 1,319
generated price rows. Nine rows conflict. The later item-level revision wins
under the nearest-pre-cutoff rule:

- Basket: `1,000` over table `100`;
- Cabbages (10): `1,000` over `10,000`;
- Hammer: `1,000` over `100`;
- Juju vial of water: `5,000` over `10,000`;
- Onion: `1,000` over `10,000`;
- Onions (10): `1,000` over `10,000`;
- Potatoes (10): `1,000` over `10,000`;
- Raw rabbit: `5,000` over `10,000`; and
- Wolf bones: `1,000` over `10,000`.

The historical Exchange template's cache-value field exactly matches the
rev-727/742-lineage cache value for 1,197 of 1,328 resolved rows. The remaining
131 value-field differences are retained as dated evidence of period
configuration drift; the Exchange price itself is never replaced by either
cache value.

The official Grand Exchange Database was checked first through Wayback. For
Logs, the CDX record exposes 2012 captures on April 13, May 2, June 20, August
19, and then December 19, with no cutoff-adjacent November capture. The
November 2 historical Exchange revision is therefore the nearest period price
record, not an OSRS or modern RS3 substitution.

## Coverage and fail-closed boundary

- 1,328 registered items have a direct dated period Exchange price.
- 1,638 registered items have a period buy limit.
- The other 329 items retain the explicitly authorized cache-value fallback;
  they do not claim a historical GE price.
- Nineteen registered identities collapse multiple period item variants and
  cannot be mapped to one limit without guessing: Black warlock, Cape, Feather
  headdress, Flowers, Fremennik cloak, Fremennik shirt, Pirate bandana, Pirate
  leggings, Priest gown, Robe top, Ruby harvest, Snowy knight, Stripy pirate
  shirt, Tribal top, Villager armband, Villager hat, Villager robe, Villager
  sandals, and Woven top.
- Those nineteen rows keep `buy_limit=None`; buy offers fail closed. Sell-side
  catalog visibility remains valid because exchangeability comes from the
  period cache rather than the unresolved limit.

No OSRS or modern RS3 price or limit supplies any generated value. No creative
design gap emerged.

## Runtime boundary and verification

`grand_exchange_data.py` now prefers the generated period price and limit maps,
retains per-row provenance, and falls back to the cache value only when the
period price is absent. The catalog is still restricted to registered,
tradeable, cache-exchangeable, non-Coin items.

- 52 focused GE catalog, offer, storage, item-value, alias, and harvester tests
  pass.
- Tests pin the Logs and Yew logs rows, cutoff timestamps, generated row counts,
  later-item conflict precedence, alias normalization, and the exact 19-row
  fail-closed set.
- Results:
  `status-updates/grand-exchange-period-harvest-results-2026-07-19.html`;
  mobile copy: `https://fptne6w8pjqm.postplan.dev`.
- Workflow `7d851241-e251-437f-a9c7-e2d48ffe4be6` produced no review or writes.
  Its read-only Sol-high leaf acquired a slot but never established a provider
  session or emitted a tool call; stderr repeatedly reported
  `failed to refresh available models: timeout waiting for child process to
  exit`. The primary cancelled it and independently reproduced the contract
  and code seams.

## Registered-item continuation — 2026-07-19

The Long kebbit reward-chain implementation registered two additional exact
period Exchange identities:

| Item | Price | Limit | Page oldid | Revision timestamp |
|---|---:|---:|---:|---|
| Long kebbit bolts | 392 | 1,000 | 6562614 | 2012-11-16T04:14:14Z |
| Long kebbit spike | 2,070 | 5,000 | 6570835 | 2012-11-18T04:24:48Z |

The generated catalog now has 1,330 direct period prices and 1,640 period buy
limits for 1,659 registered items. The original 1,328/1,638 counts above are
the historical closure checkpoint, not the current generated totals.

## Registered-item continuation — 2026-07-20

The Vinesweeper breadth slice registered all four exact Compost-potion dose
identities. Regeneration recovered a `1,000` four-hour limit for every dose and
direct period Exchange prices of `1,858`, `3,447`, `7,174`, and `12,282` coins
from one through four doses. It also recovered the previously registered
`Combat hood 0` record at `3,111` coins and a limit of `10`; that identity no
longer belongs in the fail-closed set. The generated catalog now has `1,336`
direct period prices and `1,646` period buy limits for `1,665` registered items.
