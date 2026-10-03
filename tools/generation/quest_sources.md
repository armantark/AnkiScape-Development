# Quest catalog retained inputs

`quest_sources.json.gz` pins the inputs for `tools/build_pre_eoc_quest_catalog.py`.
It is UTF-8 JSON with sorted keys, compressed with a zero gzip timestamp.
It contains source responses and lookup tables, not generated quest rows.

The snapshot retains the wiki API responses used by the checked-in catalog,
including the release list, historical revisions, current-revision fallbacks,
and revision-parsed HTML. Keys retain the original
`wikitext_<title>_<old|current>` and `parse_<oldid>` cache names. Revision IDs,
timestamps, redirect results and missing-page responses stay in each payload.

The emulator inputs are the parsed 2011Scape journals and wearable-item flags,
and the normalized 2011Scape and Darkan NPC lookup rows used by the catalog.
Rejected local NPC ambiguities remain so pruning cannot create a unique match.
NPC `source` paths are relative to game-main or the Darkan world server.
The builder expands these paths against canonical roots before formatting.
Mirror path lengths cannot change the catalog's line wrapping.
NPC `field_order` preserves the catalog's dictionary order despite sorted JSON.
The checked-in `tools/combat/quest_stat_sources.json` supplies reviewed variants.

`source_revisions` records emulator commits, or null for the game-main archive.
It also records SHA-256 hashes for contributing NPC files, quest journal files,
items.yml, npcList.txt and beasts.txt. Hashes cover only the files that supply
retained rows.

## Refresh

Run the extractor with emulator roots set through `ANKISCAPE_GAME_MAIN` and
`ANKISCAPE_DARKAN_WORLD_SERVER`. The builder stays offline. Missing pins or
response keys fail explicitly. Live Darkan helpers remain available to the
combat-gap audit, separate from catalog generation.

To recreate the pin with an existing wiki response cache, use:

```bash
python3 tools/generation/refresh_quest_sources.py --offline --wiki-cache /path/to/pre_eoc_quest_catalog --check-catalog generated/quest_catalog_generated.py
python3 tools/build_pre_eoc_quest_catalog.py
git diff --exit-code -- generated/quest_catalog_generated.py
```

The `--check-catalog` gate refuses to write a pin if the candidate bytes differ.
The extractor writes its candidate catalog in a temporary directory. It never
writes the checked-in catalog. It replaces the pin only after a complete run.
It can recreate a missing pin from the source files and the wiki response cache.

For a deliberate source refresh, use a new cache directory and omit `--offline`.
Use `--output /path/to/candidate.json.gz` to keep the candidate separate for review.
The extractor sends `User-Agent: AnkiScape parity audit`. Requests carry no
personal contact information. Historical requests use
`rvstart=2012-11-19T23:59:59Z` and `rvdir=older`. Current fallbacks retain the
original extraction policy and print a warning with the page title. Network
calls retry connection resets or refusals, timeouts, incomplete reads, HTTP 429
and HTTP 5xx responses up to six times; all other failures raise immediately.
MediaWiki error bodies fail before
cache publication. Successful responses are cached as produced. No network
operation occurs in the builder.

## Known post-cutoff citations

These 19 citations are inherited from the base catalog. They postdate the
historical cutoff and remain open source debt. No catalog row changed.
Timestamps below come from the retained MediaWiki revision responses.
Nested `item_rewards[].source` (6 references) and `stage_requirements[].source`
(4 references, oldids 36916143 and 36823822) repeat these oldids.

| Quest | Field | oldid | Revision timestamp (UTC) |
| --- | --- | --- | --- |
| Imp Catcher | source | 36916143 | 2026-01-16T13:18:20Z |
| Imp Catcher | reward_source | 36916143 | 2026-01-16T13:18:20Z |
| Jungle Potion | reward_source | 36838894 | 2025-10-04T11:56:01Z |
| Legends' Quest | reward_source | 37055891 | 2026-05-28T17:33:25Z |
| Rune Mysteries | source | 36916140 | 2026-01-16T13:17:23Z |
| Rune Mysteries | reward_source | 36916140 | 2026-01-16T13:17:23Z |
| Shades of Mort'ton | reward_source | 36858841 | 2025-11-04T20:55:50Z |
| Haunted Mine | reward_source | 37056938 | 2026-05-30T12:49:25Z |
| Roving Elves | reward_source | 37058108 | 2026-05-31T22:20:57Z |
| Ghosts Ahoy | reward_source | 37062886 | 2026-06-07T19:22:15Z |
| Making History | reward_source | 36914139 | 2026-01-10T17:30:49Z |
| Recipe for Disaster: Another Cook's Quest | source | 36823822 | 2025-09-18T21:00:51Z |
| Recipe for Disaster: Another Cook's Quest | reward_source | 36591879 | 2024-11-30T09:33:33Z |
| Recipe for Disaster: Another Cook's Quest | journal_source | 36823822 | 2025-09-18T21:00:51Z |
| Rag and Bone Man | reward_source | 37066418 | 2026-06-10T17:42:30Z |
| Royal Trouble | reward_source | 37046082 | 2026-05-17T17:55:33Z |
| Myths of the White Lands | reward_source | 36845210 | 2025-10-13T10:24:58Z |
| Forgiveness of a Chaos Dwarf | reward_source | 36923176 | 2026-01-25T16:10:22Z |
| The Void Stares Back | reward_source | 37062517 | 2026-06-06T18:42:09Z |
