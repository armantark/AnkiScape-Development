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

Six, all in `memory-bank/placeholder-values.md`:
`crucible.rank_point_thresholds`, `crucible.points_per_kill`,
`crucible.bones_per_kill`, `crucible.lesson_bone_award`,
`crucible.risk_expectation_per_level`, `crucible.abandonment_fee`.

Every one of them is a value the period demonstrably had — a threshold the
client's own tier list needs, a delta script 6288 renders, a currency both
revisions describe, a fee interface 1298 names — and none of them invents a
mechanic. The one exact point rule, one rank point per successful hit on the
champion, ships as a real constant rather than a placeholder.

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
