# The Crucible Horizontal Implementation Source Audit

Date: `2026-07-26`

Schema version claimed: **86**.

## Scope decision

This family ships the whole of the period arena that AnkiScape has a surface
for: the combat-level entry gate, the bounty fee, the four lessons, assigned
bounty targets fought through real review combat, the rank ladder with its
Supreme Champion event, and Marv's Trophy bone shop.

The settled owner answer in `recon-coverage-closure-2026-07-18.md` item 2 asked
for "authentic fees and risk … sourced coin sink on death, the opponent's
sourced fee on kill (symmetric, source-shaped) … trophy bones and the Supreme
Champion ladder kept." All four are implemented. Two clauses of that record
turned out to disagree with the period sources; both corrections are below.

## Sources in required order

### 1. Darkan

- repository:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server`
- commit: `c95aca409f397cab12c13b6d5269b73f6cd8abe9`
- `src/main/java/com/rs/game/content/minigames/crucible/Crucible.java`
- `src/main/java/com/rs/game/content/minigames/crucible/CrucibleController.java`
- `src/main/java/com/rs/game/content/Potions.kt`, `checkPVPPotionBoosts`

Sourced facts harvested:

- `CrucibleController.start` calls `Potion.checkPVPPotionBoosts(player)`, adds
  `Effect.OVERLOAD_PVP_REDUCTION`, and skulls the player. `sendDeath` calls the
  same pair again on every respawn.
- `checkPVPPotionBoosts` lowers each boosted skill to
  `base + flat + base * multiplier` with `(5, 0.15)` for Attack, Strength and
  Defence, `(5, 0.1)` for Ranged and `(5, 0.0)` for Magic. This is the identical
  routine the Clan Wars red portal uses.
- `sendDeath` calls `player.sendPVPItemsOnDeath(killer)`, which hands the items
  to the killer and writes **no** gravestone and **no** Death's Office entry.
- `processTeleport` refuses unconditionally, in both modes.
- `Crucible.updateRank` documents the client tier argument exactly: `-1` none,
  `0` displayed as rank 6, `1..5` counting down to rank 1, `6` Supreme Champion,
  `7` a transient invulnerability display.
- `Crucible.updateRankPoints` is a display call only. Darkan never awards a
  point, never sets a threshold, and never charges a fee: the reward hatch and
  the bounty-fee interface are opened as bare interfaces with no logic behind
  them.

### 2. The rev-727 cache (2012-07-24)

Read with `tools/OpenRs2Cs2Disassembler.java` against
`~/Library/Caches/codex/2012scape-openrs2/extracted/727-2012-07-24/cache`.
Rev 742 was also queried; its CS2 does not decode with the bundled opcode table,
but its item and object definitions do.

- Script **6284** maps tier `-1..7` to graphics `11233..11240` and the displayed
  rank text `"6".."1"`, and switches overlay 1296 component 0 to
  `"Supreme Champions:"` at tier 6. It reads **no** varp or varbit, so the tier
  arrives already computed and the thresholds are server-side.
- Script **6288** renders `"+ N rank pt"` in green for a delta of 1 or more and
  `"- all rank pts"` in red for zero or less. It mutates no stored value, so the
  client proves that a wipe *display* exists but not what triggers it.
- Interface **1298** states the bounty fee arithmetic verbatim:
  `F = ( X - Y ) + Z`, where X is "the appropriate amount of risk for your
  combat levels", Y is "the value of items you are risking", and Z is the
  target-abandonment amount. It also says the fee leaves the money pouch on
  entry and that "a certain amount … (potentially all of it)" comes back at an
  arena bank. Rev 742 object `72936` carries a `"Get fee"` option, corroborating
  the refund. **No numeric constant for X, Y or Z exists in any script.**
- Interface **1297** labels its currency column `"Cost (Trophy Bones)"`. Script
  **6275** fills the prices from enums **5899** (taunts), **5900** (titles) and
  **5901** (extras). Enum 5901 is `1=>24, 2=>36, 3=>48, 4=>60, 5=>15`; 5899 is
  `1-2=>12, 3-10=>36`; 5900 is `1-2=>12, 3-20=>30`. Enum **2118** holds the ten
  exact taunt names.
- Interface **1292**, the Crucible warning, reads "If you die you will lose all
  the items you are carrying."
- Item definitions: `24444 Trophy bones`, `24463 Supreme champion's helm`,
  present identically in rev 727 and rev 742.

### 3. Pinned historical wiki

- `Crucible` oldid `6538845`, `2012-11-06T11:34:47Z`
- `Update:The Crucible` oldid `5778674`, `2012-06-19T12:15:18Z`
- `Trophy bones` oldid `5971782`, `2012-07-22T02:00:10Z`
- `Supreme champion's helm` oldid `6555268`, `2012-11-14T13:40:17Z`
- `Rogue (Marv)` oldid `6224467`, `2012-09-09T21:16:13Z`

Sourced facts harvested:

- Released `2012-06-19`, entrance north-east of Edgeville.
- Full participation needs membership and **combat level 60**; below that a
  player reaches the tutorials and the waiting room only.
- The player is matched against another player of similar combat skill, each is
  the other's assigned target, only that target is attackable, and the fight
  runs until one dies or leaves. The victor loots the loser's equipment and
  inventory. **Protect Item prayers and curses are disabled.**
- The loser's variable fee component is paid to the victor; the flat component is
  paid to the opponent when a player abandons a live target.
- Vanquished players drop **Trophy bones**, the arena's reward currency, spent
  with **Marv** at the "Crucible rewards" shop.
- Four lessons, each awarding one set of Trophy bones, capped at four sets.
- The reward table matches the cache enums row for row.
- The **Supreme champion's helm** costs 60 Trophy bones, is cosmetic with no
  combat bonuses, and is sold only to a player who has been Supreme Champion at
  least once.
- The Supreme Champion event fires every half hour, removes normal targets,
  makes the arena **safe**, names one of the highest-ranked players as champion,
  and leaves the champion invulnerable for the first two of its two and a half
  minutes. **Each successful hit on the Supreme Champion awards one rank point** —
  the only numeric point rule any source gives.
- Rank points were on the HiScores; five players were listed and the highest
  recorded score was 560.

## Two corrections to our own records

Both follow the standing lesson in `design-thread-queue.md` section 5: when a
settled record and a pinned revision disagree, re-read the revision.

1. **There is no selectable safe mode.** Darkan's `Crucible.entrance` offers
   "Which Bounty Hunter mode would you like to enter as?" with safe and
   dangerous options. That prompt names Bounty Hunter, not the Crucible, and no
   period source describes a mode choice. Both pinned revisions say ordinary
   Crucible combat was dangerous, and cache interface 1292 says all carried
   items are lost. The arena therefore ships dangerous-only, and the sourced
   safe window is the Supreme Champion event. Darkan's option is treated as a
   reconstruction artefact.

2. **A dangerous death writes no grave.** The 2026-07-18 record says "dangerous
   death through the ordinary death/grave pipeline per the wilderness-risk
   precedent". Darkan's `sendPVPItemsOnDeath` creates no gravestone and no
   Death's Office entry, and the cache warning says the items are lost. The
   family therefore passes `no_grave=True` and `safe_death=False`, the same path
   the Clan Wars red portal already uses. `tests/test_crucible.py`
   `test_a_dangerous_death_destroys_everything_and_pays_the_victor` fails if a
   grave is ever restored.

3. **Rank points persist across visits.** An earlier draft read Darkan's
   per-controller `points` field as the whole rule and made the ladder
   per-visit. Under that reading Supreme Champion was unreachable — 400 reviews
   of real play never got there, because a death reset the counter — which would
   have shipped the Supreme helm as an inert row. The article's HiScores figure
   of 560 settles it: points are a persistent per-player total. What triggers
   the client's "- all rank pts" wipe is stated nowhere, so no wipe is shipped.

## What is not shipped, and why

The period reward interface has two more rows than this family sells: three
fissure energy boosts (24, 36 and 48 Trophy bones) and a 15-bone Rogue glove
repair. AnkiScape has neither fissure travel nor a Rogue glove, so either
purchase would take the player's bones and change nothing. An omitted row is
honest; an inert one is the defect this programme keeps catching. Queued as
design decision 3.5.

The three Supreme Champion weapons — Decimation, Annihilation and Obliteration —
are likewise deferred. They are content rather than reward rows, and the rate at
which taking them increased Trophy bone income is stated nowhere.

## Placeholders registered

Five, all in `memory-bank/placeholder-values.md`:
`crucible.rank_point_thresholds`, `crucible.points_per_kill`,
`crucible.bones_per_kill`, `crucible.risk_expectation_per_level`,
`crucible.abandonment_fee`.

Every one of them is a value the period demonstrably had — a threshold the
client's own tier list needs, a delta script 6288 renders, a currency both
revisions describe, a fee interface 1298 names — and none of them invents a
mechanic. The one exact point rule, one rank point per successful hit on the
champion, ships as a real constant rather than a placeholder.

### Rank-threshold depth re-walk — 2026-08-03

`crucible.rank_point_thresholds` remains source-blocked after re-walking the
full available caller chain:

- Darkan `CrucibleController.java:28-33` initializes `rank` and `points` to
  zero (or unranked for its reconstruction-only dangerous branch) and contains
  no later write to either field.
- Darkan `Crucible.java:86-122` merely forwards those values to client script
  6284 and the overlay text. Git history first adds that display bridge in
  `684c25528`; its parent contains no hidden promotion routine.
- Rev-727 script 6284 maps the already-computed tier to the six rank graphics
  and Supreme Champion state. Script 6288 renders an already-computed point
  delta. Neither reads persistent state or compares a threshold.
- Crucible oldid `6538845` and the launch update oldid `5778674` establish the
  ladder and point-earning events but state only that rank rises "every few rank
  points". No complete period table survives in the pinned source trail.

The existing 1/3/6/10/15/25 progression remains a registered reachability
placeholder, not a period claim. A server promotion routine or independently
dated complete table would retire it. No owner design gap surfaced.

### Ordinary-kill rank-point depth re-walk — 2026-08-03

`crucible.points_per_kill` remains source-blocked after exhausting the same
server, client, and period-history boundary:

- Launch-update oldid `5778674`, dated `2012-06-19T12:15:18Z`, says players
  earn points "for every target slain" and extra points from the Supreme
  Champion, but gives no ordinary-kill amount.
- Crucible oldid `6538845`, dated `2012-11-06T11:34:47Z`, gives the one exact
  amount that survives: every successful hit on the Supreme Champion awards
  one rank point. The complete pre-cutoff article history adds no numeric
  ordinary-kill award. The cutoff talk history adds none either.
- Darkan `CrucibleController.java` initializes `points` to zero and contains no
  award write. History commit `684c25528` adds only the display bridge;
  `Crucible.updateRankPoints` forwards a supplied delta and current total.
- Rev-727 script 6288 renders a supplied positive delta as added rank points or
  clears the display for a nonpositive value. It does not calculate an award,
  read a stored total, or identify the action that produced the delta.

The existing one-point ordinary-kill award remains a disclosed reachability
placeholder. It is not inferred from the separate champion-hit rule. A period
server award routine or an exact ordinary-kill statement would retire it. No
owner design gap surfaced.

### Trophy-bone depth re-walk — 2026-08-03

`crucible.bones_per_kill` remains source-blocked, but the adjacent tutorial
award is exact and no longer belongs in the placeholder register:

- Launch-update oldid `5778674`, dated `2012-06-19T12:15:18Z`, says vanquished
  players drop Trophy bones and that taking Supreme Champion weapons increases
  their rate. It gives neither the ordinary award nor the boosted one.
- Crucible oldid `6538845`, dated `2012-11-06T11:34:47Z`, says Trophy bones are
  obtained from defeating enemies. Its complete pre-cutoff history adds no
  quantity. The cutoff article does explicitly say tutorials award up to four,
  one from each tutorial.
- Trophy bones oldid `5971782`, dated `2012-07-22T02:00:10Z`, and its complete
  29-revision pre-cutoff history state the reward uses and tutorial cap but no
  ordinary-kill amount. Its item infobox identifies the bone as stackable and
  non-tradeable.
- Rev-727, rev-741, and rev-742 item definitions agree that item 24444 is
  `stackable=true` and `exchangeable=false`. Rev-727 scripts contain no push of
  item 24444 and no Trophy-bone text; interface 1297:125 labels the cost column
  but computes no award.
- Darkan history commit `684c25528` packages a defeated player's non-food loot
  inside exactly one metadata-bearing item 24444. That 2023 loot-key
  reconstruction treats the item as non-stackable, contrary to all three
  period client definitions. It is useful death-custody evidence, not evidence
  for the authentic currency amount.

The two-bone ordinary-kill value remains a disclosed reachability placeholder.
`CRUCIBLE_LESSON_BONE_AWARD = 1` is now recorded as exact because the cutoff
article states the four-total cap and one from each tutorial. No owner design
gap surfaced.

### Bounty-fee depth re-walk — 2026-08-03

The old fee abstraction was materially below every surviving period amount. It
quoted a bare combat-level-60 player at about 29,000 coins and a maxed player at
about 60,000, despite three independent period observations in the 500,000-coin
range:

- Crucible talk oldid `5909709`, dated `2012-07-08T17:42:36Z`, preserves a
  launch-day `2012-06-19T12:34Z` report for combat level 60: about 50,000 coins
  with meaningful gear and 500,000 with no risk. The complete talk history
  traces that statement to oldid `5778707` at the same timestamp.
- The original `Crucible bounty fee interface.png`, uploaded
  `2012-06-24T20:37:44Z`, SHA-1
  `fa17c698eef51283bb81784ea0605d7dc1fe4cdf`, shows the exact single quote
  `F=535,362`, `X-Y=486,693`, and `Z=48,669`. The capture does not identify the
  player's combat stats or when the screenshot itself was taken, so it is an
  amount anchor rather than a schedule.
- Cutoff Crucible oldid `6538845` reports about 518,000 coins for a maxed player
  carrying nothing during the August money-pouch exploit. The same revision
  says the launch hotfix cut the original fee to one tenth, so the surviving
  500,000-ish figures must not be divided by ten again.

The client and server searches still do not recover the authentic curve.
Rev-727 interface 1298 receives rendered X, Y, Z, and F values and contains no
fee constants; no rev-727 client script writes its numeric components. Darkan's
Crucible reconstruction opens the interface but implements no fee calculation,
and its history adds none.

The corrected bounded placeholder therefore starts X at 450,000 coins for
combat level 60 (the reported 500,000 no-risk total less the 50,000
gear-independent component), then adds 400 coins per level above 60. This keeps
the sourced combat-level dependence and yields 531,200 total at level 138,
inside the surviving 518,000-to-535,362 observations. Z is corrected from 5,000
to 50,000, bounded independently by the exact 48,669 screenshot component. Both
values remain registered; neither is represented as the lost server formula.
No owner design gap surfaced.

### Target-level matching depth re-walk — 2026-08-03

The exact matching band and its frequencies remain source-blocked:

- Cutoff Crucible oldid `6538845` says the intended match was another player
  with similar combat skill, then records the observed failure: relatively low
  combat players could fight maxed players.
- The complete pre-cutoff article history repeats the same qualitative rule and
  criticism. The cutoff talk history adds only that match selection was flawed;
  neither history preserves an exact combat-level pair or range.
- Rev-727 interfaces and scripts contain no matching table or target selector.
- Darkan's complete Crucible history from `53122a021` onward adds participant
  sets and, later, an unused `BH_TARGETS` map. No revision assigns a Crucible
  target or computes a combat-level band.

The old placeholder cycle `-8/0/+8/+20` could not reproduce the sourced failure:
a level-60 entrant topped out at level 80. The corrected cycle keeps three
ordinary near-level opponents and uses `+78`, clamped to the real 138 combat
cap, so the minimum eligible player can actually encounter the documented
maxed mismatch. The fourth-slot frequency is a disclosed reachability choice,
not a recovered period probability. No owner design gap surfaced.

## Asset provenance

`tools/fetch_crucible_assets.py` installs `activityicons/crucible.png` from
`File:Crucible symbol.png`. The recorded upload timestamp is
`2012-07-18T15:55:12Z`, inside the period, sha1
`5fde2cb546557da1a6448709ed12d5e1527868e9`, and the entry is in
`assets_provenance.json`. `File:Crucible entrance.png` was deliberately avoided:
it has the better name but its only upload is from 2022.

## Test coverage

`tests/test_crucible.py`, 34 tests in six classes: data and registration, the
entry gate, the arena, rewards, the view, persistence, the command router, and
runtime integration. Plus one case in `tests/test_direct_action_undo_seam.py`.

Nothing under test is mocked. `_play` drives the real
`apply_combat_burst_pure` from a real `default_player_data`, and
`CrucibleRewardTest` plays the arena — re-entering after each death, the way a
player would — until it has genuinely been named Supreme Champion and holds
enough Trophy bones to buy the most expensive row plus the helm. Only then does
it assert that any of them can be bought.

## What this family does NOT model

Added 2026-07-26 after an independent audit of the merged family. Recorded here
because a gap that is only absent from the code reads, later, as a gap nobody
noticed.

- **The Supreme Champion's invulnerable phase.** The event is one review long, so
  the sourced two-of-two-and-a-half-minutes invulnerable share has no window to
  occupy and the champion is attackable throughout. Design fork 3.6.
- **The ordinary target during an event.** A player with a live bounty keeps it
  while the champion event runs, and there is no separate champion opponent; the
  event pays rank points on hits against the target already assigned.
- **The membership requirement.** The Crucible was members-only content. AnkiScape
  has no membership concept, so the gate is combat level and the entry fee alone.
- **The waiting room.** It exists as text on the panel, not as a state with its own
  transitions.
- **Looting a defeated rival's actual items.** A dangerous death destroys the
  loser's carried items and pays the fee's risk component to the victor in coins.
  The period let the victor take the items themselves. Modelling that needs a rival
  inventory, which nothing in the family has.
- **Three champion weapons, the fissure energy boosts and the Rogue glove repair.**
  Deferred depth; the shop rows are covered by design fork 3.5.

Two verification figures worth keeping, from a real-kernel probe across 1,543
reviews at seed 7: 48 entries produced 48 kills and 47 dangerous deaths, and the
first championship arrived at review 149. Isolated single visits at combat levels
60 and 99 across seeds 0 to 99 all ended in a dangerous death within 500 reviews
and none reached champion. The championship is therefore reachable only by
re-entering after death, which is how a player plays but is worth stating, and the
death rate is close to total. Whether that is faithful punishment for dangerous
content or a broken risk model is being checked independently.
