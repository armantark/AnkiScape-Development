# Slayer Dagannoth Combat source audit — 2026-07-18

## Decision

Implement the two ordinary Lighthouse combat forms as the playable
Dagannoth-family targets: level 74 ranged and level 92 melee. Both retain
their own combat identity and share the exact generic Darkan ordinary, charm,
and medium-clue selectors.

The Slayer family is source-baseline rather than quest-gated. AnkiScape has no
location selection inside a generic Combat target, so these two forms
represent the ordinary family without importing the Lighthouse's Horror from
the Deep route gate. This follows the existing location-flattening boundary:
Waterbirth Island, Chaos Tunnels, Dagannoth Kings, quest encounters, and
Daemonheim remain separate contexts rather than being silently mixed into
these rows.

## Period authority

RuneScape Wiki `Dagannoth (Lighthouse)`, oldid `6548464`, timestamp
`2012-11-11T22:16:11Z`, is inside the frozen cutoff:
<https://runescape.wiki/w/Dagannoth_(Lighthouse)?oldid=6548464>.

The revision establishes:

- two ordinary forms, level 74 ranged and level 92 melee;
- 700/1,200 LP and 70/120 Slayer XP;
- six-tick attacks for both;
- an approximate 100-LP ranged maximum and exact 80-LP melee maximum;
- ranged poor accuracy and more accurate melee;
- aggression, non-poisonous attacks, and susceptibility to player poison;
- guaranteed Bones and the exact visible generic drop identities;
- Chaeldar assignment; and
- the location-specific fact that these particular spawns appear after Horror
  from the Deep.

The page also makes clear that Lighthouse Dagannoths do not drop hides, while
the Waterbirth and Chaos-Tunnel populations have different loot identities.
Those location-specific tables are not merged.

RuneScape Wiki `Dagannoth (Chaos Tunnels)`, oldid `6518124`, timestamp
`2012-11-01T23:28:15Z`, and `Dagannoth`, oldid `6542625`, timestamp
`2012-11-08T07:00:38Z`, were checked to preserve that boundary. Their level
88/90 combat records, seven-tick Chaos cadence, retreats, hides, Fremennik
equipment, and Waterbirth access are location variants, not substitutes for
the selected ordinary rows.

## Executable combat definitions

Darkan commit `d759fdd779ae38836900b0dea3c4357bc1a82458` supplies:

- `data/npcs/combatdefs/uncategorized/dagannoth/dagannoth_(74).json:1-30`:
  700 LP, Attack 68, Strength 70, Defence 50, Magic/Ranged 1, ranged style,
  80 maximum hit, aggression, and 59-tick respawn;
- `data/npcs/combatdefs/uncategorized/dagannoth/dagannoth_(92).json:1-30`:
  1,200 LP, Attack 68, Strength 70, Defence 71, Magic/Ranged 1, melee style,
  80 maximum hit, aggression, and 59-tick respawn; and
- `developer-information/npcListBonuses.txt:1338-1343`: all-zero bonuses for
  level 74, and 50 Magic/Ranged defence for level 92.

The level-74 row uses Darkan's exact 80-LP maximum because the period page's
100 is explicitly approximate. Both use the period-exact six-tick cadence.

## Drops

Darkan `data/npcs/drops/dagannoth.json:1-369` contains guaranteed Bones plus
34 nonzero sibling rows. `src/main/java/com/rs/utils/drop/DropList.java:43-68`
proves that every nonzero sibling occupies one cumulative selector even when
the JSON denominators differ. The least common denominator is 1,100:

| Output group | Source rate | Slots |
|---|---:|---:|
| Pearl bolt tips ×12; Lobster pot; Harpoon; Fishing bait ×50 | each 5/220 | each 25 |
| Feather ×15; Raw sardine ×5; Raw herring ×4; Raw lobster; Seaweed ×10; Oyster pearls ×1–2; Water runes ×15–30; Steel arrows ×15; Coins ×1–85; Bronze spear; Iron spear; Bronze hatchet; Poison ivy seed; Cactus seed; Belladonna seed; Toadflax seed; Irit seed; Avantoe seed | each 9/220 | each 45 |
| Opal bolt tips ×12; Raw tuna; Casket; Mithril javelins ×3–4; Mithril spear; Ranarr seed; Kwuarm seed; Snapdragon seed; Cadantine seed; Lantadyme seed; Dwarf weed seed | each 3/220 | each 15 |
| Torstol seed | 1/100 | 11 |
| Empty | remainder | 14 |

The nonempty slots total 1,086, leaving 14 explicit empty slots. The result
preserves every marginal source probability and prevents impossible
multi-drops from sibling rows.

Darkan `data/npcs/charmDrops.txt:49` supplies thresholds `13-6-25-1`.
Lossless enumeration of the inclusive, overlapping choice in
`src/main/java/com/rs/tools/old/CharmDrop.java:54-75` yields a 1,212-slot
selector: 68 Gold, 26 Green, 212 Crimson, 6 Blue, and 900 empty.

`src/main/java/com/rs/utils/NPCClueDrops.java:81` adds an independent 1/128
medium clue. The period page visibly corroborates the clue tier. Its generic
rare-drop-table transclusion has no recovered executable rate in the pinned
Darkan target, so it remains `source_blocked` rather than receiving an
invented roll.

## Assets

- `combatenemies/dagannoth.png` uses the cutoff
  `File:Dagannoth ranged.png` revision from `2011-11-19T16:36:18Z`, SHA-1
  `0072acb0d06db051d4a96354b6054ae4e34fa758`.
- `combatenemies/dagannoth_level_92.png` uses the cutoff
  `File:Dagannoth melee.png` revision from `2011-11-19T18:45:30Z`, SHA-1
  `6613209af2eb8e024148d3449ed770ba67f9f82c`.

Both pass through the standard 48-pixel Combat-enemy pipeline and retain full
provenance in `assets_provenance.json`.

## Readiness and design-gap result

Both target IDs belong to the one `dagannoths` family. Registering them
advances Chaeldar from 23/34 to 24/34. Ten families remain blocked, and
Chaeldar remains hidden and unrenormalized.

No owner-facing design gap emerged. The omitted location and boss variants
are already explicit future context seams, not unresolved choices for this
ordinary-family closure.

## Verification

Focused Combat, Slayer, roster, and metadata coverage passes 359 tests. The
focused real offscreen Qt Combat picker passes. Full non-Qt discovery passes
all 1,677 tests with 215 declared Qt-environment skips. Full real offscreen Qt
discovery executes all 1,677 tests with zero skips or failures in 353.314
seconds.

Test quality reports zero hard issues across 73 files and 1,677 methods; the
four structural-clone groups are unchanged. Reachability remains at 1,253
actions, 1,865 reachable items, 288 orphan inputs, and 313 blocked actions.
Documentation, compilation, provenance JSON, diff hygiene, readiness, and
worktree safety pass.

A two-leaf read-only Codex Workflow (`1e59a4a7-e589-4243-822a-fb753f3c5a67`)
was stopped after both bounded reviewers spent 27 minutes repeatedly widening
their searches without producing a candidate ledger or final artifact. No
reviewer finding is claimed here; the closure rests on the cited source
reproduction and root-run verification above.

Results: `status-updates/slayer-dagannoth-results-2026-07-18.html`; mobile
copy: <https://vzhh6w72sawc.postplan.dev>.
