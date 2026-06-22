# Quest Historical Wiki Combat Stat Audit - 2026-06-22

## Scope

This slice answers the "is every single quest done?" concern by making the next
source tier explicit for the remaining combat backlog. It does not claim full
minute-detail quest parity. The runtime already blocks all 194 pre-EOC catalog
quests through stage requirements, but 109 combat encounters still lack
resolver-ready NPC stats and remain hard-blocked.

## Source Order

1. Local 2011Scape remains the preferred source for quest/NPC mechanics.
2. Local Darkan/2012scape remains the preferred source for exact NPC combat
   definitions and beast metadata.
3. Pinned historical RuneScape Wiki monster revisions through 2012-11-19 are a
   follow-up source tier when local data is missing.
4. OSRS wiki remains cross-check only.

## Backend

- Added `tools/audit_quest_historical_wiki_combat_stats.py`.
- The tool fetches pinned historical monster revisions via the RuneScape Wiki
  API, caches responses in `tools/.cache/quest_historical_wiki_combat_stats`,
  retries transient failures, and handles HTTP 429 with a slower retry path.
- It parses `Infobox Monster` and `Infobox NPC` metadata into source-visible
  stats/configs.
- It intentionally treats historical life points, max hit, and attack-style
  prose as `historical_wiki_metadata_only` unless the page also exposes the
  style-critical hidden stats needed by AnkiScape's combat resolver.
- `tools/audit_quest_combat_stat_gaps.py` now defines unresolved combat debt as
  "not resolver-ready" instead of "empty `npc_stats`", so future HP-only
  metadata cannot make a combat gap disappear.

## Frontend

- No new widget behavior was needed.
- Added an offscreen Qt regression test for Fight Arena. With combat resolving
  enabled and an overpowered player, Khazard scorpion and Khazard ogre still
  show `combat_missing_stats` while the sourced Bouncer row remains selectable.

## Source Findings

`python3 tools/audit_quest_combat_stat_gaps.py` still reports:

- `statless_combat_encounters: 109`
- `darkan_hitpoints_only_metadata: 51`
- `darkan_missing_resolver_stats: 18`
- `darkan_same_name_wrong_level: 9`
- `no_local_source_match: 12`
- `parser_or_variant_level: 19`

`python3 tools/audit_quest_historical_wiki_combat_stats.py` reports:

- `combat_gaps_checked: 109`
- `historical_wiki_metadata_only: 77`
- `historical_wiki_no_monster_metadata: 32`
- `historical_wiki_resolver_stats_available: 0`

Historical pages checked in this pass commonly expose life points, max hit, and
attack style. Examples include Khazard scorpion and Khazard ogre, but those
pages do not expose Attack, Strength, and Defence, so they must remain blocked
until a source with resolver-ready melee stats is found.

## Manual Anki Test Instructions

1. Start Anki with this add-on active.
2. Ensure combat resolving is enabled in saved data for the test profile:
   `player_data["quest_combat_config"] = {"resolver_enabled": True}`.
3. Put Fight Arena in progress at stage 2:
   `player_data["quests"]["fight_arena"] = {"started": True, "progress": 2, "completed": False}`.
4. Add `Armour x1` to the inventory and set high combat levels.
5. Open the Quests tab.
6. Confirm Fight Arena is still visible as in progress.
7. Confirm the row shows missing-stat blockers for Khazard scorpion and Khazard
   ogre, and a battle blocker for Bouncer.
8. Answer one Quest review.
9. Confirm Bouncer can resolve, but the quest does not complete or advance past
   the current stage while Khazard scorpion and Khazard ogre remain unresolved.

## Deferred Gaps

- Full minute-detail per-stage route, branch, follower, puzzle, and quest-item
  transformation extraction is still open.
- The 109 unresolved combat rows remain active quest debt.
- Historical wiki monster metadata is useful evidence, but in this pass it did
  not provide resolver-ready hidden stats for any remaining combat row.
