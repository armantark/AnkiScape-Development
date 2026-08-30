# Doogle leaves acquisition audit — 2026-08-30

## Scope and verdict

This slice closes the ordinary acquisition route for `Doogle leaves`, the
missing input at Gertrude's Cat stage 5. The existing quest stage consumes one
Raw sardine and one Doogle leaves and produces one Doogle sardine.

**Verdict:** one zero-XP Utility gathering review represents the documented
pickup behind Gertrude's house and grants the two Doogle leaves stated by the
pre-cutoff quest guide. The page states the quantity directly, so there is no
hidden roll and no placeholder value.

## Provenance handoff

The Darkan project thread supplied revision `5819038` as a lead through a
doorbell. AnkiScape independently fetched and pinned the same permanent
revision before using it. This record is the shared stop marker so neither
project harvests the source again.

The Darkan evidence store remains read-only and was not copied into this
repository:

`/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/gertrudes-cat-build727-oldid-5819038.json`

## Period evidence

### Acquisition and quantity

AnkiScape fetched the permanent revision directly with `curl`:

```text
https://runescape.wiki/w/Special:PermanentLink/5819038
```

The request resolved to `https://runescape.wiki/?oldid=5819038` with HTTP 200.
The MediaWiki revision API independently returned:

| Field | Pinned value |
| --- | --- |
| Title | `Gertrude's Cat` |
| Revision | `5819038` |
| Parent | `5807360` |
| UTC timestamp | `2012-06-24T05:50:56Z` |

This revision predates the `2012-11-20` cutoff. The broader quest catalog also
cites later revision `6326014`; it is not counted as independent corroboration.
This acquisition audit intentionally pins `5819038`, the doorbell lead that
AnkiScape was required to reproduce independently. Its literal wikitext states:

```text
*[[Doogle leaves]] (Can be obtained from behind Gertrude's house)
```

The walkthrough then fixes the batch quantity and the item direction:

```text
Head behind it and pick up two [[Doogle leaves]] if you haven't done so already.
```

```text
Use the [[Doogle leaves]] on the raw sardine to make a [[Doogle sardine]]
```

Doogle leaves are therefore the gathered input. Doogle sardine is the quest
stage product, not an acquisition source.

### Darkan behavior

The read-only Darkan checkout was inspected at current HEAD
`6277992980582f7b3da3a48e722e96cfa5b0a57d`.

- `src/main/java/com/rs/game/content/quests/gertrudescat/GertrudesCat.java:47`
  says that Doogle leaves are obtained behind Gertrude's house. Git attributes
  that line to `d7f3572fb83d175e950e78dd9fd2e14c0983f6c8`.
- `src/main/java/com/rs/game/content/quests/gertrudescat/GertrudeD.java:84`
  points the player to the bush out back. Git attributes that line to
  `c6fbe036b1743f4dd6067ec178332c69c3708856`.
- `src/main/java/com/rs/game/content/quests/gertrudescat/GertrudesCat.java:296-302`
  registers Raw sardine `327` plus Doogle leaves `1573`, deletes one of each,
  and adds Doogle sardine `1552`. The transaction body was supplied by commit
  `1276a1d5db061dba0235fc88e0be5ca3165676ff`.

Darkan corroborates the source location and the transformation. It does not
implement or state the ground-pickup quantity, so the pinned period wiki
revision supplies the directly stated quantity of two.

### Item identity

The exact command was run against both Darkan's revision-727 cache base and the
independent closest-to-cutoff revision-742 cache:

```text
tools/query_openrs2_cache.sh '/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/727-2012-07-24/cache' --id 1552 1573
tools/query_openrs2_cache.sh '/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/742-2012-11-07/cache' --id 1552 1573
```

Both builds agree:

| ID | Item | Model | Stackable | Exchangeable | Inventory option |
| ---: | --- | ---: | --- | --- | --- |
| 1552 | Doogle sardine | 34098 | No | No | `Drop` |
| 1573 | Doogle leaves | 2364 | No | No | `Drop` |

The item registry now preserves those IDs and flags instead of inheriting the
generic quest-item defaults.

## Product translation

- `gather_doogle_leaves` is a zero-XP Utility gathering action with no material
  requirements.
- One successful review grants two Doogle leaves. The two-item batch comes from
  the literal cutoff walkthrough, not an inferred respawn rate.
- The row uses the existing Utility selector, saved `current_utility` target,
  generic runtime action, telemetry, persistence, and answer-undo paths.
- Gertrude's Cat stage 5 remains the only transformation: one Raw sardine plus
  one Doogle leaves produces one Doogle sardine.

## Asset provenance

The established quest-item art was already present and is reused rather than
fetched again. Both archive objects were independently downloaded and matched
the hashes in `assets_provenance.json`.

| Asset | Source UTC timestamp | Source SHA-1 | Source dimensions | Normalized local dimensions | Normalized local SHA-1 |
| --- | --- | --- | --- | --- | --- |
| `questitems/doogle_leaves.png` | `2011-11-20T04:06:53Z` | `ab8edfd7de3a2bf9503ee43ed99e39f52250bfbd` | 30×23 | 29×22 | `0a831800824a90d7fd02f868eb7493bec616ea1a` |
| `questitems/doogle_sardine.png` | `2011-11-28T11:28:05Z` | `e8d2006198864a4959b66be100b21bb9e7970f4c` | 32×24 | 32×24 | `de3294d3eb8fdb74e04990fa27fc3a8b37b6dc52` |

The Doogle leaves local sprite is tightly cropped to its 29×22 alpha bounds.
The source archive URL and source revision metadata remain pinned in
`assets_provenance.json`.

## Explicit abstractions and omissions

- The Utility row does not model travel, world coordinates, bush depletion, or
  wall-clock ground-spawn respawn time.
- The quest guide's one-time wording, "if you haven't done so already", is not
  turned into persistent world-object state. The established Utility contract
  represents one repeatable source trip per successful review.
- No gather probability or hidden roll exists in the evidence used here. No
  entry is added to `memory-bank/placeholder-values.md`.
- Alternative sources are not needed to make the authentic ordinary route live.

## Second-level surfaces

- Reachability still contains `Stew` before and after this slice, but its chosen
  route changes from `shop:warrior_guild_food_shop` to
  `quest:gertrudes_cat`. This is pre-existing route-attribution order
  dependence, not an item loss, and is not fixed in this slice.
- `Doogle sardine` retains its pre-existing `food` category. The pinned quest
  evidence proves that Fluffs consumes it, not that the player can eat it. A
  separate item-page audit must settle the category before it changes.

## Reachability result

| Pin | Before | After |
| --- | ---: | ---: |
| `action_count` | 1600 | 1601 |
| `reachable_item_count` | 2217 | 2230 |
| `orphan_input_count` | 192 | 192 |
| `root_orphan_count` | 40 | 40 |
| `cascade_orphan_count` | 152 | 152 |
| `unresolved_action_count` | 284 | 284 |
| `seed_item_count` | 1164 | 1176 |

Gertrude's Cat stage 5 no longer appears in
`blocked_quest_stage_products`. The completable-quest count rises from 40 to 43;
Gertrude's Cat, Icthlarin's Little Helper, and Smoking Kills are the three new
completable quests.

## Acceptance contract

- A Utility review must add exactly two Doogle leaves and no XP.
- The Doogle leaves row must use the existing pre-cutoff quest-item sprite.
- Doogle leaves and Doogle sardine must retain IDs 1573 and 1552 and remain
  non-stackable and non-exchangeable.
- The selected Utility target must persist through the generic saved-target path.
- Answer undo must restore the exact pre-review inventory.
- Reachability must route Doogle leaves through
  `Utility:gather_doogle_leaves`, route Doogle sardine through
  `quest-stage:gertrudes_cat:5`, and clear the Gertrude stage-5 blocker.

## Verification

Focused behavior checks passed before the full lanes:

```text
Ran 4 tests in 4.391s
OK
Ran 1 test in 1.249s
OK
```

The final post-review lanes passed against the final candidate state:

```text
Plain: Ran 4535 tests in 396.606s
OK (skipped=513)
Qt: Ran 4535 tests in 686.415s
OK (skipped=3)
```

The three-skip result proves the offscreen Qt lane ran; the 513-skip result is
the plain lane. The supporting audits returned:

```text
Audited 606 Markdown and 441 HTML files.
Documentation audit passed.
4500 tests across 221 files
hard issues: 0
structural clone candidates: 31 groups
```

The final reachability measurement retained the seven after-pins in the table
above, 146 blocked quest-stage rows globally, and 43 completable quests. It
returned exit 1 because the project-wide baseline still contains 284 unresolved
actions; the Doogle leaves route, Gertrude's Cat stage 5, and the three affected
quest chains are resolved and covered by focused assertions.

Kimi K3 could not perform the requested review because its provider returned
HTTP 403 `You've reached your weekly (7-day) usage limit`. Opus was used as the
disclosed taste substitute; its valid source and coverage findings were applied.
A final GLM 5.3 Flash cross-lineage review reported no actionable findings.
