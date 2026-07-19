# Slayer Fire giant Combat source audit — 2026-07-18

## Decision

Implement the ordinary level-86 Fire giant as Chaeldar's twentieth executable
family. The same representative also satisfies the already-reconciled Sumona,
Duradel/Lapalok, and Kuradal family identity when those hidden registries are
activated. No owner-facing design choice is required.

The target deliberately excludes Daemonheim variants and does not manufacture
location-specific Wilderness, Smoke Dungeon, or quest rules. Those contexts
belong to future location selection, not the ordinary monster identity.

## Period authority

RuneScape Wiki `Fire giant`, oldid `6555306`, timestamp
`2012-11-14T14:38:57Z`, is inside the frozen cutoff:
<https://runescape.wiki/w/Fire_giant?oldid=6555306>.

The revision establishes the ordinary representative's:

- combat level 86, 1,110 LP, and 111 Slayer XP;
- melee style, five-tick attack speed, and 116-LP maximum hit;
- aggressive behavior;
- no Slayer-level requirement;
- guaranteed Big bones;
- non-poisonous attacks and susceptibility to player poison; and
- assignment by Chaeldar, Sumona, Duradel, and Kuradal.

The page contains separate Daemonheim and location-context material. Those
variants are not folded into the ordinary target.

## Executable combat definition

Darkan commit `d759fdd779ae38836900b0dea3c4357bc1a82458` provides
the executable combat record at
`data/npcs/combatdefs/uncategorized/fire_giant/fire_giant_(86).json:1-38`:
1,110 LP, Attack/Strength/Defence 65, Magic/Ranged 1, melee, a 116-LP
maximum, aggressive range four, and a 59-tick respawn.

The definition names slash as the attack channel but does not provide numeric
attack or defence bonuses. The live row therefore preserves the exact levels
and uses the existing zero-bonus fallback rather than inventing unseen values.

## Drops

Darkan
`data/npcs/drops/fire_giant.json:1-257` supplies guaranteed Big bones and one
complete 128-slot ordinary selector:

| Output | Slots |
|---|---:|
| Coins ×60 | 40 |
| Darkan herb table | 19 |
| Darkan gem table | 11 |
| Fire runes ×150 | 10 |
| Chaos runes ×5 | 7 |
| Coins ×15 | 7 |
| Coins ×25 | 6 |
| Rune arrows ×12 | 5 |
| Blood runes ×5 | 4 |
| Steel hatchet | 3 |
| Lobster | 3 |
| Mithril sq shield | 2 |
| Coins ×300 | 2 |
| Steel bar | 2 |
| Fire battlestaff | 1 |
| Rune scimitar | 1 |
| Fire runes ×37 | 1 |
| Law runes ×2 | 1 |
| Coins ×50 | 1 |
| Strength potion (2) | 1 |
| Darkan standard rare table | 1 |

`DropList.java:43-68,98-109` proves that sibling non-zero rows form one
cumulative selector while zero-rate tables remain separate. The nested
standard rare selector is reproduced exactly from
`data/npcs/drops/special_tables/rdt_standard.json:1-117`; its 128 slots include
the existing Darkan gem and mega-rare selectors and therefore preserve nested
roll semantics.

Darkan `data/npcs/charmDrops.txt:60` gives thresholds `56-7-5-2`.
`CharmDrop.java:54-75` rolls an inclusive value from 0 through 100, collects
every threshold that passes, and chooses uniformly among the eligible charms.
Lossless enumeration produces a 404-slot selector:

| Output | Slots |
|---|---:|
| Gold charm | 207 |
| Green charm | 11 |
| Crimson charm | 7 |
| Blue charm | 3 |
| Empty | 176 |

The independent `long_curved_bone` table at
`data/npcs/drops/tertiaries/long_curved_bone.json:1-31` gives Long bone at
1/400 and Curved bone at 1/5,000. A 100,000-slot table represents both exactly:
250 Long-bone slots, 20 Curved-bone slots, and 99,730 empty slots.

No Fire giant entry exists in Darkan's `NPCClueDrops.java`, so no clue roll is
invented.

## Asset

The period page's enemy image resolves to `File:Fire giant.png`.
`combatenemies/fire_giant.png` is pinned to the pre-cutoff revision from
`2011-11-21T02:39:58Z`, SHA-1
`ce3de1d4ee5883da4ffab4d45576a643aa8c319b`. The fetcher records the archived
image URL and normalizes the raster through the standard Combat-enemy path.

## Readiness and scope

Registering `fire_giant` advances Chaeldar from 19/34 to 20/34. Fourteen
families remain blocked, and Chaeldar remains hidden and unrenormalized.
No quest work, location system, Daemonheim behavior, or Dungeoneering data is
introduced.

No owner-facing design gap emerged.

## Workflow and verification

Codex Workflows run `04fa8f85-fe0b-4a7b-84f3-0a0f960907ca` attempted two
bounded Sol-high read-only checks on build
`0.1.0+codex.20260718221923`. Both jobs failed before session creation with
zero tokens and zero tool calls: `provider emitted no startup event within
30s`, `session_id=null`, and provider exit `-15`. The primary independently
reproduced the period page, Darkan definitions, selector arithmetic, registry
mapping, and asset provenance. The new runtime signature was reported to the
Workflows owner; no native-subagent fallback was used.

Focused Combat, Slayer, roster, and metadata coverage passes 347 tests. The
real offscreen Qt Combat-picker regression also passes. Full non-Qt discovery
passes all 1,665 tests with 215 declared Qt-environment skips. Full real
offscreen Qt discovery executes all 1,665 tests with zero skips or failures in
375.550 seconds.

Test quality reports zero hard issues across 73 files and 1,665 methods; the
four structural-clone groups are the unchanged high-signal baseline.
Documentation passes across 337 Markdown and 346 HTML files. Compilation,
JSON parsing, diff hygiene, readiness, and worktree safety pass. Reachability
remains at 1,253 actions, 1,851 reachable items, 293 orphan inputs, and 320
unresolved actions; this enemy-only slice introduces no new action or item
identity.

Results:
`status-updates/slayer-fire-giant-results-2026-07-18.html`; mobile copy:
<https://6v3lhweptj0p.postplan.dev>.
