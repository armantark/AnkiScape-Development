# Spotted and Spottier cape source qualification

Both capes qualify as period-tradeable Grand Exchange items. This packet supplies source evidence only. It changes no product data.

Scope: `Spotted cape` / `10069` and `Spottier cape` / `10071`. Cutoff: `2012-11-20T00:00:00Z`. The source checkout is pool15 at `1932b3c07b5dd8bdb598889f2f503607ac92b791`.

The retained files are in `cape-tradeability-2026-09-05/`, beside this audit. `manifest.json` binds every packet file. Compressed responses retain the complete original bytes. Main-slot files retain the exact UTF-8 content string, without template expansion. Gzip headers have zero modification time and no original filename.

## Controlling period fields

| Storage key | Item ID | Unmarked item revision | Item timestamp | Literal tradeable field |
| --- | --- | --- | --- | --- |
| Spotted cape | 10069 | [5549170](https://runescape.wiki/w/Spotted_cape?oldid=5549170) | 2012-05-01T08:02:49Z | `Yes`, main-slot line 8 |
| Spottier cape | 10071 | [5728066](https://runescape.wiki/w/Spottier_cape?oldid=5728066) | 2012-06-07T20:51:13Z | `Yes`, main-slot line 9 |

Both unmarked pages state `stackable = No` and `exchange = gemw`. These are literal infobox fields. No rendered template result supplies a value.

The item pages contain no item IDs; their literal names join to IDs `10069` and `10071` through the paired `Item` and `ItemId` fields in the Exchange records.

| Exchange item | Revision and timestamp | ItemId | Price | Literal Date | Value | Limit |
| --- | --- | --- | --- | --- | --- | --- |
| Spotted cape | [6563180](https://runescape.wiki/w/Exchange:Spotted_cape?oldid=6563180), 2012-11-16T05:35:25Z | 10069 | 406 | 05:35, November 16, 2012 (UTC) | 400 | 100 |
| Spottier cape | [6571613](https://runescape.wiki/w/Exchange:Spottier_cape?oldid=6571613), 2012-11-18T05:44:24Z | 10071 | 633 | 05:44, November 18, 2012 (UTC) | 800 | 100 |

Each Exchange main slot supplies `Item` on line 4, `ItemId` on line 5, `Price` on line 6, `Date` on line 8, `Value` on line 10, and `Limit` on line 12. Neither Exchange record carries a beta marker. The records also retain `Last` and `LastDate`; they do not supply the selected guide price.

The retained global table independently lists both exact Exchange titles with limit `100`. Its revision is `6457777`, timestamp `2012-10-23T03:28:03Z`. Spotted cape appears on content lines 8408–8409; Spottier cape appears on lines 8414–8415. `global-buy-limits-oldid-6457777.json.gz` preserves the existing source; no new table harvest ran.

`qualified-capes.json` records the exact field lines, source titles, revision metadata, and two qualified generated rows.

Each `qualified_generated_row` combines the evidence in one record; its `buy_limit` belongs in the separate `PERIOD_GE_BUY_LIMITS` map, not in the provenance returned by `_price_row`.

## Beta marker controls

The requested Spotted cape revision `6308186` is dated `2012-09-27T22:29:04Z`. The requested Spottier cape revision `6308184` is dated `2012-09-27T22:29:00Z`. Both carry `{{beta}}` on line 1.

The bounded June lookup returned revisions `5828595` and `5828618`, dated `2012-06-25T20:04:05Z` and `2012-06-25T20:04:18Z`. Both still carry the marker. Their explicit parent revisions are the unmarked controlling records above.

All three retained item revisions for each cape contain the same literal `tradeable = Yes` field. Only the unmarked parent supplies the final tradeability claim. The clean November Exchange record establishes the later market identity and values. The packet does not use beta combat bonuses, item-weight prose, or other unrelated page text.

## Dated cache identity and decoder provenance

The rev-727 archive is dated `2012-07-24`; the rev-742 archive is dated `2012-11-07`. Each selected query returns the same identity rows:

| Item ID | Literal name | Stackable | Client exchangeable | Inventory options |
| --- | --- | --- | --- | --- |
| 10069 | Spotted cape | false | true | `[null, Wear, null, null, drop]` |
| 10071 | Spottier cape | false | true | `[null, Wear, null, null, drop]` |

These are client facts. The exchangeable flag does not establish direct player tradeability; the unmarked literal item fields supply that claim.

The initial files `cache-727-items-10069-10071.txt` and `cache-742-items-10069-10071.txt` are identical at 471 bytes with SHA-256 `988da764705875b66031b1f7a10e7a421ed21cea8124196402699a8c32db8ad0` and alone identify neither input cache nor decoder; the `INPUT_CACHE` and `CLASS` lines in `cache-727-provenance-replay.txt` and `cache-742-provenance-replay.txt` supply those bindings.

Before each initial query, every extracted input file matched its dated ZIP member by SHA-256 and byte count. There were 39 files for rev 727 and 40 for rev 742, with no extra or missing files. The ZIP hashes match the permanent source standard:

- Rev 727: `ba79072542d1bda4d8140be38839b540133e79bc40c80665ef1772be178b29f8`.
- Rev 742: `9f5fdba0d22cdc1b4ad86c984cc0ba4bcd4b3c22039f3290ba48f5083bc100b8`.

The precheck found two installed decoder JARs. The shell wrapper's current constructed classpath places `2.0.6` before `2.0.5`. It stopped before any query under that ambiguous wrapper configuration. This observation cannot establish which JAR an earlier source pass loaded.

This packet invokes the unchanged `tools/OpenRs2CacheItemSearch.java` source with an explicit classpath that excludes the competing `2.0.6` decoder. The selected installed `2.0.5` JAR has SHA-256 `bfaf99f7bb04a55418a9aeb07a01f2724034692637b435a87df4f3f4b029e3fe`. The original parser source and wrapper have exact Git blobs and checkout hashes in `cache-decoder-provenance.json`.

The separate provenance replay rechecks the archive and extracted hashes. Its output prints the actual input path and loaded class origins before the two cape rows. `ItemDefinitions` reports this source URL:

```text
file:/Users/ArmanTarkhanian1/.gradle/caches/modules-2/files-2.1/rs.darkan/core/2.0.5/5a13ad7bada8a9b1587bfa72fb013283102c6b7d/core-2.0.5.jar
```

Java reports both package version fields as `null`. The artifact path and checksum establish the selected decoder identity; no declared package version is invented. The query-class origin is the recorded pool15 temporary compilation directory. Its source, compiled-class hashes, exact compile/query argv, working directory, JAR timestamps, and original/current classpath orders are retained in the two provenance JSON files.

The two cache builds are independent dated client inputs. They share a decoder and do not constitute two independent server-tradeability proofs. No shared wrapper or configuration changed.

## Static source ownership and current-state limits

`static-source-bindings.json` binds source excerpts and literal table membership to the pool15 baseline. The author used AST parsing and literal data only. No product module was imported, and no runtime map was evaluated.

- `data/agility_data.py:505` supplies the two storage names and asset names. Its equipment set includes both capes. The extra-item constructor at line 552 supplies source `Agility`, category `equipment`, tradeability false, and no source ID for these two names.
- `1932b3c0:core/constants.py:2740` merges the Agility rows into the quest-related extra metadata. Later maps can override those fields. At this baseline, the literal shop extra-item map contains neither cape, so the shop-only overlay cannot supply their metadata.
- `data/equipment_data.py:359` and `:374` include both capes, and `_apply_equipment_metadata` at `1932b3c0:core/constants.py:2722` overlays equipment fields but never `tradeable` or `source_item_id`, so Agility remains the literal owner of those two fields.
- `core/item_registry.py:84` reads `tradeable` and `source_item_id` from the final metadata. The extra-item loop uses the metadata's source name.
- The generated cache-value table already has values `400` and `800`, both exchangeable names, and neither stackable name. No spelling alias is required.
- The generated period guide-price, buy-limit, and price-provenance maps contain neither cape at this baseline. Existing NPC shop price tables contain cape prices, but those tables do not create item registry metadata.

`retained-cohort-rows.json` copies only the two prior cohort rows with the source file hash. They record source `Agility`, false tradeability, missing source IDs, and unresolved status. This is a prior snapshot, not an evaluation of the current driver tree. The driver must verify the complete evaluated owner chain before implementation.

## Smallest future implementation

1. Confirm the two evaluated cape rows on the driver's accepted tree.
2. Add only these two names to the Agility tradeable set and their two exact source IDs to its existing ID map.
3. Use the existing period-data writer for only the two qualified price, provenance, and buy-limit rows. Preserve every other generated entry and the existing global limit source.
4. Verify both capes enter ordinary buy/sell behavior with the correct values, while all unrelated item rows remain unchanged.

No broad shop regeneration, alias layer, owner-map redesign, new acquisition route, or cache-value change is indicated by this source packet. The driver owns implementation, runtime checks, review, and commits. This source author performed no product tests, MacBook calls, native actions, or product edits.
