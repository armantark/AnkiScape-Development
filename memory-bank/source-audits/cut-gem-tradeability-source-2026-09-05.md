# Cut Jade and Red topaz tradeability source audit

Date: 2026-09-05. Scope: ordinary cut Jade 1611 and Red topaz 1613 only.
Baseline: `1932b3c07b5dd8bdb598889f2f503607ac92b791`.
Disposition: both items are **source-qualified** for player trading. This audit
changes no product data or behavior. Independent review confirmed both qualifications; record-level corrections are documented below.

## Qualified claims

| Storage key | Item identity | Literal item tradeability | Period GE price | Period buy limit |
|---|---|---|---|---|
| Jade | 1611 | `tradeable = Yes`, oldid 6382597, 2012-10-11T07:41:03Z | 89 coins, oldid 6570800, 2012-11-18T04:16:44Z | 1,000 |
| Red topaz | 1613 | `tradeable = Yes`, oldid 6397770, 2012-10-13T23:42:38Z | 157 coins, oldid 6562932, 2012-11-16T05:00:40Z | 1,000 |

The literal item fields prove player tradeability independently of the GE
flag. The Exchange records separately prove the named item's numeric ID,
period GE listing, guide-price snapshot, and per-item limit. Prices are dated
snapshots, not live prices or a claim about the exact market close on
2012-11-19. All four revisions precede `2012-11-20T00:00:00Z`.

- [Jade item revision](https://runescape.wiki/w/Jade?oldid=6382597): the single
  main `Infobox Item` identifies Jade and explicitly sets `tradeable = Yes`.
- [Red topaz item revision](https://runescape.wiki/w/Red_topaz?oldid=6397770):
  the single main item infobox explicitly sets `tradeable = Yes`. Its ordinary
  acquisition prose also mentions buying from another player.
- [Exchange:Jade](https://runescape.wiki/w/Exchange:Jade?oldid=6570800): literal
  `Item=Jade`, `ItemId=1611`, `Price=89`, `Value=150`, `Limit=1000`.
- [Exchange:Red topaz](https://runescape.wiki/w/Exchange:Red_topaz?oldid=6562932):
  literal `Item=Red topaz`, `ItemId=1613`, `Price=157`, `Value=200`, `Limit=1000`.

The complete main-slot text was inspected for both item pages and both
Exchange pages. None contains a beta marker or a competing item infobox.
The item articles mention RuneScape Classic history, and Red topaz has an
`RSC page` link; those are links or historical paragraphs within the ordinary
RuneScape item article, not alternate definitions used by this audit. Jade's
opening disambiguation explicitly distinguishes the gem from Jade the NPC.
The cut-item names, uncut inputs, Crafting levels, and XP match the current
recipes. No live template expansion supplies a qualified field.

## Identity and current storage keys

The rev-727 cache dated 2012-07-24 and the independent rev-742 cache dated
2012-11-07 both return exact IDs 1611 as `Jade` and 1613 as `Red topaz`.
Both are unstackable, have `Craft` and `drop` inventory options, and carry the
client `exchangeable=true` flag. These client records corroborate identity
and GE eligibility; they do not establish direct player tradeability.
The original runs did not record their loaded decoder. The wrapper checks
that Darkan core 2.0.5 exists, but its broad classpath includes other Gradle
JARs. That existence check and the retained 2.0.5 inventory do not prove which
decoder the original runs loaded. The dated archives are independent of
Darkan's reconstruction. The original
stdout files are byte-identical and do not identify their input directories.
Their source association comes from the recorded original commands, cwd, and
output paths. After the queries, a read-only comparison proved that every
extracted file matched its dated ZIP member: 39 files for rev 727 and 40 for
rev 742, with no missing or extra files. This binds the extracted inputs at
the later comparison time. It does not make the unchanged stdout files
self-identifying or prove the directories could not have changed between the
queries and that comparison. `cache-input-binding.json` preserves this limit.

Darkan's current `GemCutting.java` maps uncut 1627 to cut 1611 with 20 XP at
level 13, and uncut 1629 to cut 1613 with 25 XP at level 16. This is current
reconstruction corroboration, not an additional period tradeability source.
No Darkan source or harvest ledger was modified.

In `data/crafting_data.py:185`, the `cut_jade` recipe outputs the exact key
`Jade`; line 186 outputs `Red topaz` from `cut_red_topaz`. Both explicitly set
`tradeable=False`, and neither supplies `source_item_id`. The recipe converter
at line 434 carries those values into the output specification.
`core/item_registry.py:214` registers each Crafting output with that same
name. Its definition builder at line 84 sets `storage_key=name`, takes the
tradeability flag, and reads the optional source ID. The qualified historical
IDs therefore attach to these exact ordinary cut-item keys, not their uncut
inputs or another variant.

`build_item_definitions()` keeps the first row for each storage key. Its
Crafting loop also overlays matching `EXTRA_ITEM_DATA` fields. The source
packet now retains exact syntax checks for `ORE_DATA`, `GEM_DATA`, and
`EXTRA_ITEM_DATA`, plus the first-write guard and the shop-only exclusion
chain. `GEM_DATA` has four literal uncut-gem keys. The other two maps are
computed; a source text or literal-key absence does not prove their evaluated
contents. The driver then read the three evaluated maps on the authorized MacBook
candidate `3c401d0cf9349271f38aefca8582cb39afd2b645`: all six selected-key
memberships were false. Its `core`, `data`, `generated`, and `logic` Git trees
are identical to this source baseline, and the unchanged `pkg_alias.py` skips
the root initializer. The complete production Python diff adds only shared
dispatcher state and changes its root consumers. The retained mining supplier
also contains neither exact cut-item name. These checks close finding 3 for
the selected Crafting rows; the original stdout and exact source-tree binding
are retained in `evaluated-map-source-binding.json`.

The retained cohort and static recipe reads agree that the current registry
flags exclude both items. These false flags are contradicted by the qualified
item records; they are not evidence that the items were nontradeable.

## GE records and missing generated entries

The unchanged generated cache-value table contains Jade at 150 and Red topaz
at 200. Both names occur in its exchangeable-name set; neither occurs in its
stackable-name set. Those numbers are cache values, not the recovered GE
prices. The period guide-price, price-provenance, and buy-limit dictionaries
contain neither storage key. These conclusions came from exact-key AST reads;
the source-audit agent imported no product module for those reads.

The complete retained [2012 buy-limit revision](https://runescape.wiki/w/Calculator:Grand_Exchange_buying_limits?oldid=6457777),
timestamp `2012-10-23T03:28:03Z`, independently agrees with the two per-item
Exchange limits. Its literal Jade row starts at content line 4958 and its
Red topaz row at line 7133; each next line is `|1000`. The whole original
cached JSON is preserved with deterministic gzip, without reserialization.
The global table and per-item pages are separate period records from the
same wiki, not two independent publishers.

`data/grand_exchange_data.py:41` requires registry tradeability and membership
in the exchangeable-name set. It selects a positive period price, otherwise
the cache value, and emits no buy limit when the generated limit is missing.
Thus changing only the two false flags would enable cache-value pricing
without the already qualified period limits and prices. The generator obtains
its item names from `GE_ITEM_CATALOG` through `_registered_item_names()` at
`tools/generate_ge_period_data.py:153`. The two false flags therefore exclude
these names from that harvest input. This explains their exclusion under the
current generator; it does not claim an independently observed historical
execution of the original harvest.

## Smallest supported future implementation

1. Remove the two explicit false recipe overrides so the existing true default
   applies. Set their existing `source_item_id` field to 1611 and 1613 to retain
   the verified identity in the registry.
2. Add only these two keys to the current period price, buy-limit, and price
   provenance dictionaries through the existing `write_generated` entry point
   in `tools/generate_ge_period_data.py:283`. Supply the existing full maps plus
   the two qualified rows; preserve every other entry and the global limit
   source. Use the exact nine-key provenance row order: `price`, `page_title`,
   `oldid`, `timestamp`, `price_date`, `page_item`, `item_id`, `cache_value`, and
   `page_limit`. `qualified-generated-rows.json` records both fully populated
   rows in this existing shape. Do not replace the maps with a two-item harvest
   or invoke the generator's full re-harvest entry point for this bounded edit.
3. Verify the two registry rows and GE catalog rows, and prove that all other
   catalog entries and generated entries are unchanged. Runtime and UI checks
   belong to that future implementation, not this source-only pass.

The implementation needs no new market rule, fallback, source-ID registry
redesign, or changes to generated cache values. This recommendation does not
approve or perform product changes. Both selected items have positive source
support; no selected item remains source-blocked.

## Retained evidence and checks

The sibling `cut-gem-tradeability-2026-09-05/` directory contains exact API
responses and HTTP headers, exact derived main-slot wikitext, request URLs and
capture times, cache query output, the complete retained global revision,
claim records, source excerpts, and SHA-256/byte provenance. `manifest.json`
binds each retained file. `source-bindings.json` records the inspected baseline
files, exact generated keys, and the current Darkan identity excerpt.
`provenance.json` records both archive hashes, query commands and source limits.

The historical API's first combined-title request returned `invalidparammix`;
its exact response is retained as rejected evidence. Four separate-title
requests succeeded. The error response contributes no item claim. Source
fetching used bounded curl retries. Cache queries returned exit code 0.
The source-audit agent performed no product tests, MacBook calls, native Anki
actions, or source-checkout writes. The driver's later read-only map evaluation
is retained separately. Documentation validation and independent review are recorded
when completed below.

## Independent review disposition

Opus confirmed both historical tradeability qualifications and reported no
blocking source finding. Its five record-level findings are handled as follows:

1. The Exchange inspection notes now describe their actual ExchangeItem
   templates and noinclude notes.
2. The packet retains the explicit cwd, absolute query paths, source commits,
   and later archive-member comparison. Original stdout bytes are unchanged;
   their lack of embedded source identification is stated above.
3. The first-write guard and exact syntax checks are retained. The driver
   confirmed all six evaluated-map memberships are false, and identical source
   trees bind that result to this baseline. Finding 3 is closed.
4. The global buy-limit source now records its actual title, oldid 6457777,
   and timestamp `2012-10-23T03:28:03Z`, instead of querying it with item keys.
5. The prospective provenance rows use the existing nine-key shape. The audit
   identifies the current generator's GE catalog filter and preserves the
   warning against a full re-harvest.

All five source-record findings are resolved. The driver performed the
read-only map evaluation; this source agent ran no product test or MacBook
command. Product runtime acceptance is outside this source-only packet.
No product behavior or generated map was changed.

HTTP headers are stored as deterministic gzip. Their original CRLF bytes,
status-line trailing spaces, and terminal blank lines are preserved exactly;
the archive manifest records both stored and decompressed hashes and lengths.
The five raw header payloads were byte-compared before packaging. No source
content was trimmed or normalized.

The retained archive checker was reformatted after a normal commit hook
rejected its compressed Python layout. Its AST is unchanged; before and after
source hashes are recorded in provenance. The checker was not rerun.

Original source-packet checks, before the measured replay: documentation
validation passed with 657 Markdown and 445 HTML files. Owned-file whitespace checks passed. The manifest binds
26 files totaling 145,909 bytes before the manifest itself. No product
implementation or acceptance gate is claimed by this source draft.

## Measured decoder replay correction

A later scoped replay queried only IDs 1611 and 1613 against the same two
cache inputs with an explicit classpath that includes the selected core 2.0.5
JAR and excludes core 2.0.6. Immediately before each query, every extracted
file was rechecked against its ZIP member and the prior retained hashes; all
39 rev-727 files and all 40 rev-742 files matched, with no missing or extra
files. The new stdout records the input path and loaded class source before
calling the unchanged item query. Its two item rows are byte-identical to the
original 521-byte output for each cache. The old stdout remains unchanged.

The loaded `ItemDefinitions` source is the selected core 2.0.5 JAR with
SHA-256 `bfaf99f7bb04a55418a9aeb07a01f2724034692637b435a87df4f3f4b029e3fe`.
Both package version metadata fields are null; the dependency path and JAR
hash provide the version binding. `cache-decoder-replay.json` retains the
exact compile/query arguments, class hashes, input checks, timestamps, output
hashes, and byte comparisons. `cache-decoder-replay-provenance.json` retains
the selected and excluded dependencies and classpath order.

This new measurement corrects the earlier unproven decoder-version claim.
It does not establish the original classpath or loaded JAR. The existing
`cache-input-binding.json` is preserved as a historical capture: its 2.0.5
entry is an available dependency inventory. The literal period item fields
and separate Exchange qualifications remain unchanged. No new source claim
about direct player tradeability is inferred from the decoder.
