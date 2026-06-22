# Quest A Soul's Bane and Dorgeshuun combat split - 2026-06-22

## Scope

This slice continues the quest-stage parity goal without claiming full catalog
completion. It replaces bad generated combat rows for A Soul's Bane and enriches
one Death to the Dorgeshuun generated row through focused `quest_data.py`
overrides instead of editing `quest_catalog_generated.py`.

## Source-backed changes

- A Soul's Bane now uses a focused full-stage replacement:
  - Stage 1 requires `Rope x1` before entering Tolna's rift.
  - Stage 2 is a required action, `Fill the rage meter with an anger weapon`.
    This intentionally replaces the generated "Angry unicorn", "Angry bear",
    "Angry giant rat", and "Angry goblin" combat rows. Local Darkan has angry
    room NPC identities, but the exact quest mechanic is a rage-meter action, and
    the available combatdefs do not justify silently converting it into four
    resolver-ready fights.
  - Stage 3 requires five Fear reapers, five Confusion beasts, and three
    Hopeless creatures. The counts come from Darkan's historical quick guide
    revision and the stats/configs come from local Darkan combatdefs:
    `fear_reaper_(42) (noanims).json`,
    `confusion_beast_(43) (noanims).json`, and
    `hopeless_creature_(40) (noanims).json`.
  - Stage 4 requires three Tolna heads. The count comes from the Darkan quick
    guide and the resolver stats come from local Darkan `tolna (noanims).json`;
    Darkan `npcList.txt` identifies Tolna NPC ids 3658-3660 as level 46.
- Death to the Dorgeshuun keeps the generated stage placement and replaces the
  statless `Senior guard x3 (level 22)` encounter with `Senior H.A.M. guard`
  quantity 3. The local Darkan `h.a.m._guard_(22) (noanims).json` combatdef and
  `npcList.txt` id 1712 provide resolver stats/configs for the level 22 guard.

## Source conflicts and decisions

- 2011Scape local data identified A Soul's Bane item/spawn context but did not
  provide a complete quest plugin for these mechanics, so this slice used Darkan
  sources next in the required precedence order.
- Darkan `developer-information/beasts.txt` has conflicting or post-EOC-shaped
  metadata for some related rows, including Tolna and H.A.M. Guard entries. This
  slice uses local Darkan combatdefs for resolver stats and records the
  combatdef path in `npc_stats_source`; no `beasts.txt` values were merged for
  these rows.
- OSRS/Fandom pages were treated only as cross-checks during investigation. The
  committed rows cite historical runescape.wiki revisions, the Darkan quick
  guide, Darkan `npcList.txt`, and Darkan combatdef files.

## Audit result

- `tools/audit_quest_stage_gate_coverage.py` reports 194/194 quests with at
  least one machine-readable stage requirement, 384 stage rows, 119 quests with
  combat blockers, and 174 resolver-ready combat rows out of 283 combat rows.
- `tools/audit_quest_combat_stat_gaps.py` reports 109 remaining statless combat
  rows: 51 Darkan hitpoints-only metadata, 18 Darkan rows missing style-critical
  resolver stats, 9 same-name/wrong-level rows, 12 no-local-source rows, and 19
  parser/variant-level rows.

## Deferred

This is not full quest parity. Remaining work still includes source-backed
minute-detail per-stage extraction, exact route and branch flags, quest-item
transformations, puzzle/follower state, remaining combat stat reconciliation,
and a full combat simulation beyond the current one-enemy-per-review resolver.
