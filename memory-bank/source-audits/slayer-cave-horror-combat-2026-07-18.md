# Slayer Cave horror Combat source audit — 2026-07-18

## Decision

Implement the ordinary level-80 Cave horror as Chaeldar's twenty-third
executable family. Preserve Cabin Fever and lit-cave access, the close-combat
Witchwood protection rule, its real unprotected consequence, the ranged
safespot exception, exact Darkan selectors, and the Black mask route.

AnkiScape has no player-to-enemy distance. Ranged combat therefore clears the
special Witchwood requirement exactly as the period safespot rule allows, but
otherwise keeps the standard reciprocal Combat loop. This is the smallest
no-position flattening and does not manufacture a location or movement system.

## Period authority

RuneScape Wiki `Cave horror`, oldid `6550392`, timestamp
`2012-11-12T23:52:45Z`, is inside the frozen cutoff:
<https://runescape.wiki/w/Cave_horror?oldid=6550392>.

The period revision establishes:

- combat level 80, 550 LP, Slayer 58, and 55 Slayer XP;
- aggressive magical melee with a four- or five-tick cadence and 94-LP
  published maximum;
- Cabin Fever and lit-light-source cave access;
- a Witchwood icon for close combat, with Slayer helmets as effective
  substitutes;
- an unprotected scream that deals 86–87 LP and drains one combat stat by 5;
- Protect/Deflect Melee preventing the scream damage;
- the ability to omit the icon while using a long-range safespot;
- guaranteed Big bones and the rare Black mask (10); and
- assignment by Chaeldar and Sumona, but not Duradel/Lapalok or Kuradal.

The four-tick lower cadence endpoint and 87-LP upper scream endpoint are
conservative bounded representations of literal period ranges. Neither is
described as an exact hidden server roll.

## Executable combat definition

Darkan commit `d759fdd779ae38836900b0dea3c4357bc1a82458` supplies:

- `data/npcs/combatdefs/uncategorized/cave_horror (noanims).json:1-30`:
  550 LP, Attack 80, Strength 77, Defence 62, Magic 80, Ranged 1, 90 maximum
  hit, aggressive melee, and a 39-tick respawn;
- `developer-information/npcListBonuses.txt:4355-4359`: zero attack, defence,
  and strength bonuses; and
- `src/main/java/com/rs/game/content/skills/slayer/npcs/combat/`
  `CaveHorrorCombat.java:39-55`: without Witchwood protection, choose one
  implemented combat stat, reduce it by 5 to a floor of 0, and replace the
  ordinary hit with special scream damage.

The period maximum takes precedence over Darkan's 90-LP ordinary maximum in
the historical record, but the executable ordinary attack retains Darkan's
90-LP value because the period page only states an approximate 94. The
unprotected close-combat scream uses the period-exact visible 87-LP upper
endpoint rather than Darkan's conflicting one-third-of-maximum-LP formula.

## Access and protection

The existing Combat route gates represent:

- completed `cabin_fever`;
- one equipped or carried item from the canonical lit-light-source set; and
- Slayer level 58.

Protective equipment accepts either `Witchwood icon` in the neck slot or any
ordinary/full Slayer-helmet variant in the head slot. This extends the shared
protective-equipment schema from one slot to source-declared alternative
slots. The extension is conditional on melee combat, so ranged and Magic
loadouts do not receive a false Witchwood warning.

The scream replaces each ordinary enemy attack, deals a fixed 87 LP, and
drains one of Attack, Defence, Strength, Ranged, Prayer, or Magic by 5 to a
floor of 0. Protect/Deflect Melee blocks the damage but not the stat drain,
matching the period page's literal damage-prevention claim without inventing
prayer protection for the drain.

## Drops

Darkan `data/npcs/drops/cave_horror.json:1-214` supplies guaranteed Big bones
and one 128-slot ordinary selector:

| Output | Slots |
|---|---:|
| Coins ×44 | 28 |
| Darkan rare-seed table | 18 |
| Darkan variable-allotment table | 15 |
| Darkan herb table | 13 |
| Coins ×132 | 12 |
| Limpwurt root | 7 |
| Teak logs ×4 | 7 |
| Nature runes ×6 | 6 |
| Nature runes ×4 | 5 |
| Darkan gem table | 5 |
| Mithril hatchet | 3 |
| Mahogany logs ×2 | 3 |
| Rune dagger | 1 |
| Adamant full helm | 1 |
| Mithril kiteshield | 1 |
| Nature runes ×3 | 1 |
| Coins ×440 | 1 |
| Empty | 1 |

The nonempty source rows total 127/128, so the final empty slot is explicit.
`special_tables/variable_allotment.json:1-63` is reproduced as an exact
263-slot nested selector with its original quantity ranges.

Darkan `data/npcs/charmDrops.txt:33` supplies thresholds `5-2-14-1`.
Lossless enumeration of the inclusive, overlapping selection in
`src/main/java/com/rs/tools/old/CharmDrop.java:54-75` produces a 1,212-slot
selector: 28 Gold, 10 Green, 136 Crimson, 6 Blue, and 1,032 empty.

The independent `long_curved_bone` table preserves Long bone at 1/400 and
Curved bone at 1/5,000. The drop JSON adds Black mask (10) at 1/512, and
`src/main/java/com/rs/utils/NPCClueDrops.java:119` adds an independent 1/128
hard clue.

## Asset

`combatenemies/cave_horror.png` is pinned to the pre-cutoff
`File:Cave horror icon.png` revision from `2010-06-01T15:33:33Z`, SHA-1
`0c632df9c05357407838d2c1d4ff48b4d9d141ff`. The standard Combat-enemy
pipeline normalizes the 48×48 raster and records full provenance in
`assets_provenance.json`.

## Readiness and design-gap result

Registering `cave_horror` advances Chaeldar from 22/34 to 23/34. Eleven
families remain blocked, and Chaeldar remains hidden and unrenormalized.

No owner-facing design gap emerged.

## Verification

Focused Combat, Slayer, roster, and metadata coverage passes 409 tests. The
focused real offscreen Qt Combat picker passes. Full non-Qt discovery passes
all 1,675 tests with 215 declared Qt-environment skips. Full real offscreen Qt
discovery executes all 1,675 tests with zero skips or failures in 370.085
seconds.

Test quality reports zero hard issues across 73 files and 1,675 methods; the
four structural-clone groups are unchanged. Documentation passes across 343
Markdown and 349 HTML files before the results artifact, then 350 HTML files
after it. Compilation,
provenance JSON, diff hygiene, readiness, and worktree safety pass.
Reachability rises from 1,864 to 1,865 reachable items, while orphan inputs
remain 288 and unresolved actions remain 313.

Results: `status-updates/slayer-cave-horror-results-2026-07-18.html`;
mobile copy: <https://pmzz0dpygpxu.postplan.dev>.
