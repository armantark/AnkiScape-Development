# Slayer Turael/Spria assignment-pool audit — 2026-07-17

Status: **source contract provisionally closed; runtime certification failed**.
Cutoff: `2012-11-20T00:00:00Z`.

## Scope and result

This pass certifies the complete ordinary assignment contract for the
Turael/Spria functional master role under Slayer owner decisions 18–20. It does
not expose Slayer gameplay.

The reconciled pool has **23 families** with a total raw weight of **355**:

- 21 families carried by the cutoff Turael/Spria tables;
- Gelatinous abominations, attested by their cutoff page and Troll Warzone but
  omitted from the stale master tables; and
- Grotworms, attested by all three cutoff monster pages and Darkan but omitted
  from the stale master tables.

Trolls are excluded. Their Turael row was an unexplained anonymous wiki edit,
Spria never listed them, the cutoff cross-master table assigns them only to
Chaeldar and Sumona, and Darkan assigns them only to Vannaka, Chaeldar, and
Sumona.

The historical pages do not publish task weights. The table therefore uses
explicit `provisional/*` hidden-roll values under the owner-authorized
calibration rule. No provisional value is described as period-closed.

## Assignment table

`Class` means baseline versus authentic player-gated eligibility. Turael/Spria
themselves have no Slayer or Combat requirement; Spria is the quest-reactive
successor after While Guthix Sleeps.

| Family | Weight | Count | Gate | Class | Value status |
|---|---:|---:|---|---|---|
| Banshees | 30 | 15–50 | 15 Slayer; Priest in Peril route | player-gated | weight `provisional/darkan+game-main`; count/level closed |
| Bats | 10 | 15–50 | none | baseline | weight `provisional/darkan+game-main`; count closed |
| Bears | 10 | 15–50 | none | baseline | weight `provisional/darkan+game-main`; count closed |
| Birds | 10 | 15–50 | none | baseline | weight `provisional/darkan+game-main`; count closed |
| Cave bugs | 10 | 15–50 | 7 Slayer | player-gated | weight `provisional/darkan+game-main`; count/level closed |
| Cave slimes | 30 | 15–50 | 17 Slayer | player-gated | weight `provisional/darkan+game-main`; count/level closed |
| Cows | 10 | 15–50 | none | baseline | weight `provisional/darkan+game-main`; count closed |
| Crawling hands | 30 | 15–50 | 5 Slayer | player-gated | weight `provisional/darkan+game-main`; count/level closed |
| Desert lizards | 30 | 15–50 | 22 Slayer | player-gated | weight `provisional/darkan+game-main`; count/level closed |
| Dogs | 15 | 15–50 | none | baseline | weight `provisional/darkan+game-main`; count closed |
| Dwarves | 10 | 15–50 | none | baseline | weight `provisional/darkan+game-main`; count closed |
| Ghosts | 15 | 15–50 | none | baseline | weight `provisional/darkan+game-main`; count closed |
| Goblins | 10 | 15–50 | none | baseline | weight `provisional/darkan+game-main`; count closed |
| Gelatinous abominations | 30 | 15–50 | worn Spiked gauntlets to finish | baseline | membership closed; weight `provisional/denominator-closure`; count `abstraction/turael-default` |
| Grotworms | 15 | 15–30 | none | baseline | membership `provisional/period-pages+darkan`; weight/count `provisional/darkan` |
| Icefiends | 10 | 10–20 | none | baseline | weight `provisional/darkan+game-main`; corrected count closed |
| Minotaurs | 10 | 15–50 | none | baseline | weight `provisional/darkan+game-main`; count closed |
| Monkeys | 10 | 15–50 | none | baseline | weight `provisional/darkan+game-main`; count closed |
| Scorpions | 10 | 15–50 | none | baseline | weight `provisional/darkan+game-main`; count closed |
| Skeletons | 15 | 15–50 | none | baseline | weight `provisional/darkan+game-main`; count closed |
| Spiders | 10 | 15–50 | none | baseline | weight `provisional/darkan+game-main`; count closed |
| Wolves | 15 | 15–50 | none | baseline | weight `provisional/darkan+game-main`; count closed |
| Zombies | 10 | 15–50 | none | baseline | weight `provisional/darkan+game-main`; count closed |

The raw weights sum to `355`. At this pool size:

- `10 / 355 = 2.8169…%`, rendered by game-main as `2.82`;
- `15 / 355 = 4.2253…%`, rendered as `4.23`; and
- `30 / 355 = 8.4507…%`, rendered as `8.45`.

That denominator is not arbitrary. Darkan's 22 executable rows total 325.
Adding the period-attested Gelatinous-abomination family at weight 30 closes the
game-main denominator exactly. Trolls cannot fill the same slot because the
independent cutoff assignment table and Darkan both exclude Turael.

## Period wiki evidence

### Master tables and general assignment ledger

1. `Turael`, oldid `6585248`, timestamp `2012-11-19T12:04:14Z`:
   <https://runescape.wiki/w/Turael?oldid=6585248>.

   This is the cutoff-nearest master page. It establishes no master-level
   Slayer/Combat requirement, zero Slayer points/streak contribution, the
   ordinary 15–50 rows, and the corrected 10–20 Icefiend row.

2. `Spria`, oldid `6538791`, timestamp `2012-11-06T08:27:01Z`:
   <https://runescape.wiki/w/Spria?oldid=6538791>.

   The page says Spria gives the same tasks as Turael and has no separate
   master-level Slayer/Combat requirement. While Guthix Sleeps supplies the
   successor access gate. Its anonymous 11–50 Icefiend edit conflicts with the
   corrected Turael row and both emulator implementations.

3. `Slayer assignment`, oldid `6303852`, timestamp
   `2012-09-27T13:49:08Z`:
   <https://runescape.wiki/w/Slayer_assignment?oldid=6303852>.

   The literal cross-master table supplies family Slayer levels, qualifying
   variants, protective/finisher items, and the strongest evidence against
   Turael Trolls: its Troll row names only Chaeldar and Sumona.

4. `Slayer Masters`, oldid `6461968`, timestamp
   `2012-10-23T20:43:28Z`:
   <https://runescape.wiki/w/Slayer_Masters?oldid=6461968>.

   This corroborates the Turael/Spria functional role and master-level
   requirement boundary.

### Gelatinous-abomination recovery

1. `Gelatinous abomination`, oldid `6079671`, timestamp
   `2012-08-12T00:24:00Z`:
   <https://runescape.wiki/w/Gelatinous_abomination?oldid=6079671>.

   The literal infobox says `Turael = Yes`, Slayer level 1, and 5 Slayer XP.
   The article calls the creature a low-level Slayer assignment and requires
   worn Spiked gauntlets for the finishing blow.

2. `Troll Warzone`, oldid `6550701`, timestamp
   `2012-11-13T02:57:56Z`:
   <https://runescape.wiki/w/Troll_Warzone?oldid=6550701>.

   The Corrupted Depths tutorial gives a distinct fixed five-kill Gelatinous
   assignment and records a historical bug where the family could not be
   assigned. That tutorial count is not reused for ordinary assignments.

3. `Spiked gauntlets`, oldid `5827717`, timestamp
   `2012-06-25T19:55:33Z`:
   <https://runescape.wiki/w/Spiked_gauntlets?oldid=5827717>.

   The gauntlets cost 6 coins from any Slayer master, have one free sample, and
   must be worn to kill Gelatinous abominations.

No cutoff source states an ordinary Gelatinous task count. The smallest
explicit abstraction is Turael's otherwise universal 15–50 default. The
separate tutorial challenge remains exactly five and never enters the ordinary
weighted pool.

### Grotworm recovery

The three cutoff monster pages independently mark Turael as an assigning master:

- `Young grotworm`, oldid `6490000`, timestamp `2012-10-28T18:43:01Z`:
  <https://runescape.wiki/w/Young_grotworm?oldid=6490000>;
- `Grotworm`, oldid `6565933`, timestamp `2012-11-17T10:57:23Z`:
  <https://runescape.wiki/w/Grotworm?oldid=6565933>; and
- `Mature grotworm`, oldid `6549792`, timestamp
  `2012-11-12T13:20:02Z`:
  <https://runescape.wiki/w/Mature_grotworm?oldid=6549792>.

The cross-master assignment table omits Turael from its Grotworm row, so
membership is not described as historically closed. Darkan independently
implements the Turael family at weight 15 and count 15–30. The combined row is
retained as `provisional/period-pages+darkan`, not silently erased.

### Troll exclusion

Trolls first appeared in Turael's page at oldid `5366519`, timestamp
`2012-03-11T23:09:26Z`, through an unexplained anonymous edit:
<https://runescape.wiki/w/Turael?oldid=5366519>.

That edit left the table's rowspans malformed. Spria never received the row.
The cutoff cross-master assignment table names only Chaeldar and Sumona, and
Darkan contains Troll tasks only for Vannaka, Chaeldar, and Sumona. The row is
therefore treated as a period-wiki error rather than pool content.

### Icefiend count conflict

- Turael oldid `4333693`, timestamp `2011-05-29T05:47:21Z`, explicitly
  corrected Icefiends to 10–20:
  <https://runescape.wiki/w/Turael?oldid=4333693>.
- Spria oldid `6028793`, timestamp `2012-08-03T00:30:40Z`, anonymously changed
  its stale value to 11–50:
  <https://runescape.wiki/w/Spria?oldid=6028793>.
- Both Darkan and game-main independently implement 10–20.

Because Spria's own article says the pool is the same as Turael's, the
Turael-specific correction plus emulator convergence wins. The live contract is
10–20.

## Emulator evidence

### Darkan

Repository:
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server`

Nested repository commit:
`c343a917712649675989315009ce250639e0850f`.

- `Task.java:21-42` supplies 22 executable Turael rows, their raw weights, and
  count ranges.
- `TaskMonster.java:24-135` supplies family identities and Slayer/quest gates.
  Line 134 preserves the unimplemented enum-position stub
  `//111 GELATINOUS_ABOMINATIONS`; Grotworms occupy enum id 112.
- `SlayerTaskManager.java:116-147` applies weighted selection after family
  eligibility, previous-task, and player block-list filtering.
- `Master.java:23` incorrectly gives Turael point rewards and a Combat 3 floor.
  Period master pages override both user-visible claims.

### game-main

Snapshot:
`/Users/ArmanTarkhanian1/Downloads/game-main` (not a Git checkout).

- `SlayerMaster.kt:67` explicitly says the table contains only monsters for
  which the project currently has definitions.
- `SlayerMaster.kt:71-118` supplies the independently reconstructed
  `2.82/4.23/8.45` weights and the 10–20 Icefiend exception.
- Desert lizards, dogs, and monkeys are commented implementation omissions,
  not evidence against membership.
- No active assignment generator consumes this table, so it is corroborating
  data rather than executable runtime proof.

The two implementations converge on every shared raw-weight ratio and count.
They do not independently prove hidden period weights, which is why all weights
remain explicitly provisional.

## Current AnkiScape readiness

Turael/Spria remains absent from live Slayer assignment generation.

The current Combat registry has at least one ordinary variant for 17 of the 23
families. It has no Desert lizard, Dog/Jackal, Gelatinous abomination,
Grotworm, Icefiend, or Monkey target. Existing Banshee combat also lacks the
sourced unprotected-earmuff consequence, and Gelatinous abominations require a
new worn-Spiked-gauntlets finisher. Those are baseline certification blockers,
not player-facing locked rows.

This source pass also found and fixed one independent Combat defect:
`Cave slime` now carries its source `poisonDamage = 3`, and a deterministic
combat regression proves that a successful poison roll reaches persistent
player poison state.

No owner-level design question emerged. The remaining work is ordinary
implementation and source verification:

1. add the six absent family targets and qualifying variants;
2. implement Banshee and Gelatinous protective/finisher consequences;
3. close target-local route/context dependencies for the certifying variants;
4. add the machine-checkable Slayer family/readiness registry; and
5. certify the whole role before exposing `Get assignment`.

