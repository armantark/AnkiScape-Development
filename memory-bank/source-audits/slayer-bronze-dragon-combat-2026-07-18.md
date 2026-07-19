# Slayer Bronze dragon Combat source audit — 2026-07-18

## Decision

Implement the ordinary level-131 Bronze dragon as Chaeldar's twenty-second
executable family. Preserve metal-dragon dragonfire, the guaranteed
metal-bar drop, exact Darkan selectors, and both period clue tiers.

The live Combat model has no player-to-enemy distance. It therefore represents
the encounter at melee distance and uses Darkan's exact adjacent 1/2
melee-versus-dragonfire selector as a labeled bounded abstraction. This is a
pattern-determined flattening of an unavailable positioning dimension, not an
owner-facing design choice.

Locations, access fees, route items, Chaos Tunnels, Brimhaven Dungeon,
quest-only tail bones, post-cutoff drops, and Daemonheim/Dungeoneering are
excluded.

## Period authority

RuneScape Wiki `Bronze dragon`, oldid `6550367`, timestamp
`2012-11-12T23:35:12Z`, is inside the frozen cutoff:
<https://runescape.wiki/w/Bronze_dragon?oldid=6550367>.

The period revision establishes:

- combat level 131, 1,220 LP, and 125 Slayer XP;
- aggressive six-tick melee plus long-range and melee-range dragonfire;
- an approximately 123-LP melee maximum and 500-plus dragonfire;
- non-poisonous attacks and susceptibility to player poison;
- Magic/stab weakness context;
- guaranteed Dragon bones and five Bronze bars;
- assignment by Chaeldar; and
- no Draconic-visage drop.

RuneScape Wiki `Metal dragons`, oldid `6098088`, timestamp
`2012-08-16T15:56:19Z`, corroborates the ranged dragonfire identity and the
replacement of dragonhide with metal bars.

RuneScape Wiki `Dragonfire`, oldid `6534496`, timestamp
`2012-11-04T21:56:22Z`, establishes that metal-dragon dragonfire works at
range, Protect from Magic does not protect against it, one shield or ordinary
antifire layer is partial protection, and shield plus antifire or super
antifire is full protection.

## Executable combat definition

Darkan commit `d759fdd779ae38836900b0dea3c4357bc1a82458` provides
the executable record at
`data/npcs/combatdefs/uncategorized/bronze_dragon.json:1-31`: 1,220 LP,
Attack/Strength/Defence 112, Magic 100, Ranged 1, 123 melee maximum, and a
59-tick respawn.

`developer-information/npcListBonuses.txt:1592` supplies exact
stab/slash/crush/magic/ranged defences of 50/70/70/30/90.

`src/main/java/com/rs/game/content/world/npcs/MetalDragonCombat.java:41-61`
chooses melee on one of two adjacent attacks and dragonfire otherwise. It
also supplies the same 0–50 partial and zero full-protection tiers already
used by the shared dragonfire engine. At range Darkan always chooses
dragonfire; because AnkiScape does not represent distance, the adjacent 1/2
selector is used globally and labeled as an abstraction. The frozen period
500-plus envelope is represented conservatively as a 500-LP maximum rather
than importing Darkan's possible 600-LP upper roll.

## Drops

Darkan `data/npcs/drops/bronze_dragon.json:1-306` supplies guaranteed Dragon
bones and five Bronze bars plus one 128-slot ordinary selector:

| Output | Slots |
|---|---:|
| Coins ×196 | 39 |
| Adamant javelins ×30 | 20 |
| Coins ×330 | 10 |
| Fire runes ×50 | 8 |
| Adamant darts (p) ×16 | 7 |
| Mithril bolts ×2–12 | 6 |
| Law runes ×10 | 5 |
| Mithril 2h sword | 4 |
| Darkan gem table | 4 |
| Mithril hatchet | 3 |
| Mithril battleaxe | 3 |
| Rune knives ×2 | 3 |
| Blood runes ×15 | 3 |
| Adamant bar | 3 |
| Swordfish ×2 | 2 |
| Mithril kiteshield | 1 |
| Adamant platebody | 1 |
| Rune longsword | 1 |
| Death runes ×25 | 1 |
| Coins ×690 | 1 |
| Swordfish | 1 |
| Darkan standard rare table | 1 |
| Empty | 1 |

The source rows total 127/128, so the final empty slot is explicit rather than
silently renormalizing the table.

Darkan `data/npcs/charmDrops.txt:28` supplies thresholds `14-31-12-3`.
Lossless enumeration of Darkan's inclusive multi-threshold choice produces a
1,212-slot selector: 60 Gold, 264 Green, 48 Crimson, 12 Blue, and 828 empty.

The two rate-1/2,048 rows in the drop JSON remain independent Dragon
plateskirt and Dragon platelegs rolls. `NPCClueDrops.java:117,178` supplies
independent 1/128 hard and 1/500 elite clue rolls. The period page corroborates
both clue tiers and both dragon-leg drops. Quest-only Bronze dragon tail-bones
and post-cutoff additions are excluded.

## Asset

`combatenemies/bronze_dragon.png` is pinned to the pre-cutoff
`File:Bronze dragon.png` revision from `2010-12-11T13:46:01Z`, SHA-1
`4a044b1ab7f14969bbb5dffcf951f9d898c3cd85`. The raster is fetched and
normalized through the standard Combat-enemy pipeline, with full provenance
in `assets_provenance.json`.

## Readiness and design-gap result

Registering `bronze_dragon` advances Chaeldar from 21/34 to 22/34. Twelve
families remain blocked, and Chaeldar remains hidden and unrenormalized.

No owner-facing design gap emerged.

## Verification

Focused Combat, Slayer, roster, and metadata coverage passes 352 tests. The
real offscreen Qt Combat picker passes. Full non-Qt discovery passes all 1,670
tests with 215 declared Qt-environment skips. Full real offscreen Qt discovery
executes all 1,670 tests with zero skips or failures in 458.150 seconds.

Test quality reports zero hard issues across 73 files and 1,670 methods; the
four structural-clone groups are unchanged. Documentation passes across 340
Markdown and 348 HTML files before the results artifact. Compilation,
provenance JSON, diff hygiene, readiness, and worktree safety pass.
Reachability rises from 1,861 to 1,864 reachable items, while orphan inputs
remain 288 and unresolved actions remain 313.

Codex Workflows run `46d1ea65-5035-4477-bbfa-cf9c9a0cec48` attempted two
bounded Sol-high read-only leaves on build
`0.1.0+codex.20260718230940`. Shared capacity queued both correctly. One leaf
never acquired a worker/session after its slot; the other created session
`019f7915-50a2-70b0-b21c-40fd78283e61` but emitted an immediate deprecated
`[features].web_search_request` configuration error and repeated
model-refresh child-process timeouts. Neither made a tool call or produced a
usable final. The primary independently reproduced the complete contract,
implementation map, tests, and asset provenance, then canceled the stuck run.
No native-subagent fallback was used.

Results: `status-updates/slayer-bronze-dragon-results-2026-07-18.html`;
mobile copy: <https://pbdlptcksw7s.postplan.dev>.
