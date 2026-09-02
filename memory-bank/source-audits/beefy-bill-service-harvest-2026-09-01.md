# Beefy Bill banking-service harvest

Date: 2026-09-01

## Scope and evidence rule

This harvest concerns Beefy Bill (NPC `246`) and the pre-EOC banking service
identified by the Lumbridge medium achievement. The cutoff is
`2012-11-20T00:00:00Z`.

The cut, accepted-item set, formula/rounding, stack limit, service gate,
refusal text, and transaction unit are server behaviour. Under
`memory-bank/pre-eoc-source-verification-standard.md`, the RuneScape Wiki may
corroborate a value but may not independently supply it. No Darkan or
independent game-main service handler was found, and a cache cannot establish
server-side fee or transfer behaviour. Therefore none of those values is
pinned for implementation.

## Result

**The service exists, but its implementation contract is source-blocked.**

Do not implement a coin fee, a percentage calculation, an item whitelist, a
Ring of Charos exception, a quantity/stack rule, a refusal message, or an
access gate as settled period behaviour from this harvest.

| Requested value | Status | What the searched sources establish |
| --- | --- | --- |
| Cut and its form | **Unrecovered / source_blocked** | No period-lineage server source supplies a fee or fee algorithm. The wiki supplies a 10% claim only, which cannot close this server-side value by itself. |
| Accepted items | **Unrecovered / source_blocked** | No server source supplies an exhaustive whitelist. The wiki names candidate item classes only. |
| Exact item IDs and variants | **Unrecovered / source_blocked** | The cache confirms several definitions named `Pot of flour` and `Raw beef`; it does not bind any one of them to NPC `246`. |
| Quantity, stack, batch, and rounding rule | **Unrecovered / source_blocked** | No handler or protocol source was found. The wiki wording is insufficient to derive a safe formula. |
| Level, quest, or location precondition | **Unrecovered / source_blocked** | The wiki labels the NPC `members = No` and `quest = No`, but neither proves the service's complete gate. No implementation source supplies one. |
| Refusal result or player-visible text | **Unrecovered / source_blocked** | The only candidate text is a wiki Trivia claim, which the standard treats as historical/unclear without independent proof. |

## Pinned client and diary facts

These are narrower than the requested service contract and must not be
expanded into it.

1. **NPC identity and client options are pinned.** The rev-727 client
   definition for NPC `246` is exactly:

   ```
   246    Beefy Bill    [Talk-to, null, Trade, null, null]
   ```

   Source: `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/727-2012-07-24/cache/`, NPC definition `246`, rev-727 dated `2012-07-24`.
   The same row occurs in the independent later client cache at
   `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/742-2012-11-07/cache/`, rev-742 dated `2012-11-07`.
   This directly establishes that the client had `Talk-to` and `Trade`, and
   did not expose a `Bank` NPC option in either build. It does **not** establish
   what a conversation or item-on-NPC action transfers or charges.

2. **The achievement requires a Beefy Bill bank action.**
   `memory-bank/source-audits/achievement-diary-harvest-2026-07-26.json`
   records source `Darkan rev-727 cache enum 3483`, task `111`, name
   `Where's The Beef?`, description:

   ```
   Get Beefy Bill to bank something for you.
   ```

   The related dormant task ledger records `source_id=111` and the permanent
   achievement-page reference `oldid=6549949`,
   `2012-11-12T17:54:35Z`,
   `https://runescape.wiki/w/Special:PermanentLink/6549949`.
   This identifies the service objective, not its item, fee, or server rules.

3. **Candidate item identities in the rev-727 cache are not service bindings.**
   The cache has `1739 Cowhide`, `1933 Pot of flour`, `2132 Raw beef`, and
   `2142 Cooked meat`. Its name search also returns `1934`, `2516`, and
   `2517` as `Pot of flour`, and `2132`, `2133`, `4287`, and `4288` as
   `Raw beef`. The cache therefore cannot turn the wiki's generic prose into
   a safe exact-item whitelist.

   Source: `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/727-2012-07-24/cache/`, item definitions queried with
   `tools/query_openrs2_cache.sh`.

## Wiki corroboration lead — not an implementation pin

The nearest useful pre-cutoff revision is:

- Page: `Beefy Bill`
- `oldid`: `6521052`
- UTC timestamp: `2012-11-02T16:58:56Z`
- Permanent link: https://runescape.wiki/w/Special:PermanentLink/6521052

Its literal article lead says that Beefy Bill can transport `flour`,
`cowhides`, and `raw beef` to the bank; it describes a `10% commission`, says
an activated `Ring of Charos` makes it free, and says access is by talking to
him or using the respective items on him, with no right-click `Bank` option.
The no-right-click part is corroborated by the two client NPC definitions
above.

The same article lead says that inventories of exactly `10` or `20` of the
items are efficient because the player banks `9` and Beefy Bill takes one. It
does not state the actual rounding rule, whether mixed types are one batch,
or the maximum accepted stack. Do not derive an algorithm from that prose.

The article's `Trivia` section additionally claims all of the following:

- one submitted item is taken and not returned;
- on free-to-play worlds, a full bank at `68` slots, or `88` after email
  registration, prevents banking a new item unless that item is already banked;
- cooked beef is refused with exactly `It's unhygienic to mix raw and cooked meats.`

Those are explicitly Trivia claims, so section provenance makes them
historical/unclear even before the missing independent server corroboration.
They are leads, not pinned refusal behaviour or a settled exclusion list.

## Search order actually followed

1. **Darkan.** Searched
   `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/`
   across non-`*AuditProbe.kt` Java/Kotlin sources for `Beefy Bill`,
   `BeefyBill`, literal NPC ID `246`, `cowhide`, `cow hide`, and bank/deposit
   combinations. Searched the Lumbridge dispatcher and the history of the
   candidate terms. No handler keys NPC `246` to a banking service or an
   item-on-NPC banking action.

   The service-adjacent data found is only
   `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/items/shops/beefy_bills_supplies.json`, whose latest supplying commit is
   `7107bcf13833eb72d0eefd249a17aad48cf3a2e1`
   (`2023-06-22T19:58:56-04:00`, `Added shops and animations`). It is shop
   stock, not banking behaviour. The current Lumbridge dispatcher,
   `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/world/areas/lumbridge/Lumbridge.java`, has latest commit
   `3b47cfdfae8b95d543edc2c360aaad5086047804`
   (`2026-08-21T11:49:57-07:00`, `Talking to Bob, Explorer Jack or the Lumbridge shopkeepers did nothing at all`) and contains no NPC `246` handler. No
   frozen Darkan audit contract for this service was present.

2. **Rev-727 cache.** Queried NPC definition `246` and searched client
   interfaces for `Beefy` and `cowhide`; neither string occurred in the
   interface dump. A `Bank` interface search returned ordinary bank interfaces,
   proving the reader can find a positive control. The NPC row above is the
   relevant result. This client cache cannot settle a server fee, acceptance
   rules, transfer batch, or refusal response.

3. **game-main.** Searched all `294` Java/Kotlin plugin source files in
   `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/`.
   `BEEFY_BILL` occurs only in
   `game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Npcs.kt`, where it is
   `const val BEEFY_BILL = 246`; it has no handler. `COWHIDE` occurs only in
   item constants, tanning data, and pickpocket data, not in a Beefy Bill
   service. This checkout is an export without `.git`; provenance lookup
   returned exactly `fatal: not a git repository (or any of the parent directories): .git`.
   Its README also states that content is partial, so the omission cannot prove
   historical absence.

4. **Other on-disk OpenRS2 caches.** Queried NPC `246` in rev-728
   (`2012-08-01`), rev-729 (`2012-08-11`), rev-736 (`2012-10-09`), rev-741
   (`2012-11-04`), and rev-742 (`2012-11-07`), each under
   `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/<rev-date>/cache/`.
   Every build reports exactly `[Talk-to, null, Trade, null, null]`. None
   exposes the server implementation needed for the requested values.

5. **RuneScape Wiki corroboration.** Inspected literal wikitext at pre-cutoff
   `oldid=6521052`, quoted above. It is the only source found that states
   candidate fee, items, access, and refusal details. Since it is corroboration
   only and no independent server layer states those values, it does not close
   them.

## Evidence that would settle the blocked contract

A period-lineage server handler or a contemporaneous server/packet capture that
binds NPC `246` to its item-on-NPC or dialogue service would settle the cut,
formula, accepted IDs, stack/batch behavior, gates, and refusal text. A Darkan
high-fidelity restoration of that handler, with its supplying commit and an
independent period corroboration, would also be sufficient. A client cache
alone would still be insufficient for the fee or transfer semantics.

## Deliberate non-actions

I created this audit only. I did not edit implementation code, existing
records, the Darkan checkout, cache files, worktrees, or `memory-bank/papercuts.md`; the latter is an existing file and the task explicitly permits no edits beyond this new audit. I did not run tests, generators, state-changing Git commands, create a placeholder entry, or commit.
