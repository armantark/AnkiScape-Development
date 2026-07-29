# Conquest source harvest

Date: `2026-07-28`

Cutoff: RuneScape immediately before EOC, `2012-11-20T00:00:00Z`.

Status: **the ordinary Conquest roster, commands, setup budget, turn phases,
entry gate, rating start, reward shape, shared commendation wallet, and unique
reward are pinned.** Exact rating arithmetic, the turn-to-commendation-ratio
curve, several phase-boundary details, and the period obstacle layouts remain
placeholder candidates. No source code was changed.

## Scope and settled adaptation

The owner-settled Conquest shape is an **auto-played real board**, not a matchup
roll. The internal engine preserves the authentic board, troops, ranges,
commands, and victory rules. The same modest heuristic plays both sides. The
player chooses the army loadout and an aggressive, defensive, or balanced
doctrine; one review resolves one complete turn exchange and reports a one-line
result. There is no player-facing board UI
(`memory-bank/source-audits/competitive-tier-adaptations-2026-07-18.md:24-34`).

All competitive activities receive solo adaptations with labelled bounded
simulations
(`memory-bank/ankiscape-completion-starter-grill-2026-07-17.md:645-652`). One
answer must do bounded work, inactive sessions must not advance, and only state
that can change a later decision, visible status, reward, cost, or failure may
persist (`memory-bank/simulation-computation-budget-contract-2026-07-17.md:20-42`).

One correction to the earlier design shorthand is source-determined, not a new
fork: commendations are **not rating-scaled and are not a winner-only reward**.
The period game gives both players the same match-length ratio, then multiplies
it by each player's combat-level band. Winning grants no extra commendations.
The implementation must follow that sourced rule rather than the phrase “wins
pay rating-scaled commendations” in the earlier adaptation note.

## Sources used, in required order

### 1. Darkan

Local aggregate checkout:

- `/Users/ArmanTarkhanian1/Documents/2012scape with bots`
- aggregate commit `86aacbe739f78bf51e2299725d500f5bb3cf091a`
- world-server commit `1d64aefaf2bd9df890226c75c2356df0c8180183`

There is no Conquest implementation in the Darkan minigame tree. Filename and
content searches under
`darkan-world-server/src/main/java/com/rs/game/content/minigames/` returned no
Conquest controller, troop table, command table, rating routine, reward routine,
entry object, or battlefield definition. Darkan's own minigame-universe audit
records the absence explicitly:

- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/tools/build-minigame-universe.py:30`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/tools/build-minigame-universe.py:39` — `"Conquest": None`

The paired client identifies itself as build `727` at
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-client/src/main/java/com/rs/Loader.java:37`.
Darkan therefore supplies negative server evidence and the route into its cache,
not Conquest mechanics.

### 2. Rev-727 and rev-742 caches

Immutable cache paths:

- rev `727`, 2012-07-24:
  `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/727-2012-07-24/cache/`
- rev `742`, 2012-11-07:
  `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/742-2012-11-07/cache/`

The Conquest interface/client-script archives below are byte-identical between
rev 727 and rev 742. They close client-visible labels and gates, not hidden
server formulas.

| cache index/archive | exact period evidence |
| --- | --- |
| config index `2`, archive `26` | `Conquest` |
| interface index `3`, archive `1008` | Accepting an offered truce ends Conquest in a draw |
| interface index `3`, archive `1009` | `Conquest Ranking: 1000` |
| interface index `3`, archives `1016`, `1022` | `Conquest Options` |
| interface index `3`, archive `1019` | Resigning ends Conquest immediately; an accepted truce ends it in a draw |
| interface index `3`, archive `1026` | `Regular Conquest`; `Staked Conquest` |
| client-script index `12`, archives `404`, `405` | `Conquest Ranking: ` |
| client-script index `12`, archives `424`, `425` | A disconnected opponent may be waited for, or the remaining player may end Conquest and be declared the winner |
| client-script index `12`, archive `468` | `1250 Conquest ranking required.` |
| quick-chat index `24`, archive `0` | `Conquest`; `Conquest lobby`; `Conquests` |
| quick-chat index `24`, archive `1` | Regular/staked invitations, win/loss/draw result phrases, and the tutorial start |
| music index `17`, archives `5`, `14` | `Right of Conquest`; `Conquest` |

The caches corroborate the `1,000` initial/displayed rating, `1,250` gate,
truce-as-draw, immediate resignation, disconnect-win flow, tutorial, lobby, and
regular/staked mode names. They contain no decoded troop-stat, command-cost,
rating-equation, or commendation-ratio table.

### 3. game-main / 2011Scape

Local extracted tree:

- `/Users/ArmanTarkhanian1/Downloads/game-main`
- not a Git checkout; no commit hash is available
- `README.md:1-4,46-48,66-73` identifies 2011Scape and its rev-667 cache

Whole-tree search found no Conquest implementation. The only named row is the
music key `right_of_conquest` at
`/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/music/music_by_region.yaml:2922`.
The local cache files are zero-byte placeholders, so this lineage supplies no
mechanical values.

### 4. Pinned historical wiki revisions

| key | page | oldid | UTC timestamp | what it supplies |
| --- | --- | ---: | --- | --- |
| `C` | [Conquest](https://runescape.wiki/w/Conquest?oldid=6570865) | `6570865` | `2012-11-18T04:29:06Z` | Main rules, setup, troops, commands, rating, commendations, timers |
| `CG` | [Conquest/Guide](https://runescape.wiki/w/Conquest/Guide?oldid=6404899) | `6404899` | `2012-10-14T17:36:15Z` | Command-point examples, second-player advantage, obstacles |
| `UC` | [Update:Conquest](https://runescape.wiki/w/Update%3AConquest?oldid=3346147) | `3346147` | `2010-10-18T20:32:26Z` | Official launch gate, Captain Ethar, shared-wallet cap, deflector identity |
| `UAVD` | [Update:A Void Dance](https://runescape.wiki/w/Update%3AA_Void_Dance?oldid=5508644) | `5508644` | `2012-04-18T19:02:04Z` | Quest-chain requirements |
| `UTVSB` | [Update:The Void Stares Back](https://runescape.wiki/w/Update%3AThe_Void_Stares_Back?oldid=5508651) | `5508651` | `2012-04-18T19:06:18Z` | Conquest-tutorial quest gate |
| `TVSB` | [The Void Stares Back](https://runescape.wiki/w/The_Void_Stares_Back?oldid=6549183) | `6549183` | `2012-11-12T07:10:29Z` | Quest-only modified Conquest and pest troops |
| `AVD` | [A Void Dance](https://runescape.wiki/w/A_Void_Dance?oldid=6543386) | `6543386` | `2012-11-08T19:44:16Z` | Fifty-commendation quest reward |
| `VKC` | [Void knight commendations](https://runescape.wiki/w/Void_knight_commendations?oldid=6441647) | `6441647` | `2012-10-19T04:44:16Z` | Shared wallet, cap, and reward shop |
| `VKD` | [Void knight deflector](https://runescape.wiki/w/Void_knight_deflector?oldid=6441661) | `6441661` | `2012-10-19T05:27:22Z` | Deflector rating and purchase gates |
| `CC` | [Completionist cape](https://runescape.wiki/w/Completionist_cape?oldid=6560039) | `6560039` | `2012-11-15T20:34:20Z` | `1,250` rating trim requirement |
| `P0` | [Update:Patch Notes (31 January 2012)](https://runescape.wiki/w/Update%3APatch_Notes_%2831_January_2012%29?oldid=5201175) | `5201175` | `2012-01-31T13:41:27Z` | Rating can gain again from `0` |

## Entry, location, and quest relationships

| rule | pinned value | provenance |
| --- | --- | --- |
| membership | Members-only safe minigame | `C`, `UC` |
| combat requirement | Combat level **40** | `UC`: “the only requirement is a minimum combat level of 40” |
| skill requirements | None stated | `UC`: combat 40 is the “only requirement” |
| activity start | Talk to **Captain Ethar** | `UC` |
| location | Void Knights' Outpost | `C`, `UC` |
| travel | Talk to the squire at Port Sarim | `C` |
| ordinary-match quest gate | None | `UC`: A Void Dance is narrative context, while combat 40 remains the only requirement |
| tutorial relationship | Completing the Conquest tutorial is required to start **The Void Stares Back** | `UTVSB` |
| quest-chain relationship | `Quiet Before the Swarm` → `A Void Dance` → `The Void Stares Back`; the tutorial is an additional TVSB prerequisite | `UAVD`, `UTVSB` |
| A Void Dance reward | **50** Void Knight commendation points | `AVD` |

Neither `A Void Dance` nor `The Void Stares Back` gates ordinary Conquest.
`The Void Stares Back` requires the tutorial, not a rated win, a rating threshold,
or a complete PvP match.

## Setup and deployment

| rule | pinned value | provenance |
| --- | --- | --- |
| setup budget | **1,000** squad resources/setup points per side | `C` |
| selected commands | At most **4** | `C` |
| deployment zone | Each side's first **3 rows** | `C` |
| placement within zone | Free placement inside those rows | `C` |
| troop duplicates | No per-type cap recovered; period guides describe repeated Champions and ten-Halberdier armies | `C`, `CG` |
| formal squad-size cap | Unresolved; ten-unit formations and a full default squad strongly suggest **10**, but no pre-cutoff rule text states a universal maximum | `C`, `CG` |

The cheapest pinned unit is the `25`-point Scout, so the `1,000`-point budget by
itself cannot substitute for the unresolved unit-count cap.

## Ordinary player troop roster

All seven player-recruitable period troop types are below. There is **no combat
triangle** or sourced type-advantage table. Damage, health, movement, and range
are the troop mechanics; commands modify them temporarily. Alleged “hybrid
units” found in later wiki material are a wiki ghost with no pinned period troop
identity and are deliberately omitted.

| troop | setup cost | LP | damage | movement | attack range | special rule | provenance |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Scout | `25` | `100` | `100` | `6` | `1` | None documented | [Scout (Conquest)](https://runescape.wiki/w/Scout_%28Conquest%29?oldid=4877028), oldid `4877028`, `2011-10-27T08:36:23Z` |
| Foot Soldier | `50` in cutoff wikitext; `30` in release-era UI image | `300` | `100` | `4` | `1` | None documented | [Foot Soldier](https://runescape.wiki/w/Foot_Soldier?oldid=4528699), oldid `4528699`, `2011-07-15T02:36:41Z`; [Footsoldierdetails.png](https://runescape.wiki/w/File%3AFootsoldierdetails.png?oldid=6096263), oldid `6096263`, `2012-08-15T23:41:46Z` |
| Halberdier | `75` | `200` | `200` | `4` | `2` | Only melee troop with range greater than `1` | [Halberdier](https://runescape.wiki/w/Halberdier?oldid=4566229), oldid `4566229`, `2011-07-25T07:04:56Z`; `C` |
| Archer | `100` | `100` | `100` | `3` | `6` | None documented | [Archer (Conquest)](https://runescape.wiki/w/Archer_%28Conquest%29?oldid=5905197), oldid `5905197`, `2012-07-08T10:16:56Z` |
| Mage | `100` | `100` | `200` | `4` | **`4`** | None documented | [Mage (Conquest)](https://runescape.wiki/w/Mage_%28Conquest%29?oldid=5073281), oldid `5073281`, `2011-12-21T03:31:14Z`; [Magerdetails.png](https://runescape.wiki/w/File%3AMagerdetails.png?oldid=6096269), oldid `6096269`, `2012-08-15T23:45:02Z` |
| Knight | `100` | `300` | `300` | `4` | **`1`** | None documented | [Knight (Conquest)](https://runescape.wiki/w/Knight_%28Conquest%29?oldid=4517686), oldid `4517686`, `2011-07-11T16:07:07Z`; [Knightdetails.png](https://runescape.wiki/w/File%3AKnightdetails.png?oldid=6096268), oldid `6096268`, `2012-08-15T23:44:40Z` |
| Champion | `200` | **`500`** | `400` | `4` | `1` | None documented | [Champion](https://runescape.wiki/w/Champion?oldid=4618443), oldid `4618443`, `2011-08-11T02:31:25Z`; `C` records the 2010 reduction from `600` to `500` LP |

### Roster corrections that must survive implementation

- **Knight range is `1`, not `4`.** The Knight article copied movement into its
  range field. The period in-game details image reads movement `4`, damage
  `300`, health `300`, range `1`, cost `100`; the main page independently says
  the Halberdier is the only melee troop with range above one.
- **Mage range is `4`, not `3`.** Both the infobox and period in-game details
  image read `4`; one prose sentence saying it attacks three spaces away is the
  bad row.
- **Champion LP is `500`, not `600`.** The page records the `2010-10-12`
  reduction from `600` to `500`.
- **Foot Soldier cost is conflicted.** Nearer-cutoff wikitext says `50`; the
  original game details image says `30`. It remains a placeholder candidate.
- There is **no sourced combat triangle**, no attack-style advantage matrix, and
  no player-recruitable hybrid roster.

## Quest-only pest troop roster

These six troops belong to the modified AI Conquest encounter in `The Void
Stares Back`. They are not player-recruitable ordinary Conquest units and must
not enter the regular loadout catalog.

| pest troop | UI cost | LP | damage | movement | range | exact special/relationship | provenance |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Defiler | `100` | `200` | `200` | `4` | `4` | Similar to a Mage; no additional innate rule recovered | [DefilerDetails(void3).png](https://runescape.wiki/w/File%3ADefilerDetails%28void3%29.png?oldid=4956223), oldid `4956223`, `2011-11-19T23:10:34Z`; `TVSB` |
| Ravager | `100` | `300` | `300` | `6` | `1` | Scout movement and Knight damage | [Ravagerdetails(void3).png](https://runescape.wiki/w/File%3ARavagerdetails%28void3%29.png?oldid=4988074), oldid `4988074`, `2011-11-27T13:47:19Z`; `TVSB` |
| Shifter | `10` | `200` | `200` | `10` | `1` | No additional innate Conquest rule recovered | [Shifterdetails(void3).png](https://runescape.wiki/w/File%3AShifterdetails%28void3%29.png?oldid=4993707), oldid `4993707`, `2011-11-28T14:02:08Z`; `TVSB` |
| Spinner | `30` | `800` | `100` | `6` | `1` | Explicitly does **not** heal units in this encounter | [Spinnerdetails(void3).png](https://runescape.wiki/w/File%3ASpinnerdetails%28void3%29.png?oldid=4996530), oldid `4996530`, `2011-11-29T00:15:51Z`; `TVSB` |
| Splatter | `25` | `600` | `100` | `6` | `1` | On death, deals `100` LP to every adjacent unit within `1` square; may move beside a friendly unit and suicide | [Splatterdetails(void3).png](https://runescape.wiki/w/File%3ASplatterdetails%28void3%29.png?oldid=4996775), oldid `4996775`, `2011-11-29T01:30:08Z`; `TVSB` |
| Torcher | unresolved | `100` | `100` | unresolved | unresolved | Similar to an Archer | `TVSB`; no pre-cutoff numeric details image recovered |

A later page gives the Torcher cost/movement/range as `75`/`4`/`6`, but that
page misses the cutoff and cannot independently close the values.

## Commands

A loadout selects at most four commands. Commands may be used during any phase
of the player's turn. All costs, effects, durations, and cooldowns below come
from `C`, oldid `6570865`.

| command | command-point cost | exact effect | duration | cooldown |
| --- | ---: | --- | --- | ---: |
| Battle Cry | `75` | One controlled troop gains `+200` damage and `+200` health | Until the start of the player's next turn | `5` turns |
| Stoicism | **`75`** | One controlled troop gains `+400` health | Until the start of the player's next turn | `5` turns |
| Regenerate | `150` | Completely restores one controlled troop's health | Immediate | `4` turns |
| Bombard | `200` | Reduces one enemy troop's health by `100`; a Bombard kill grants no command points | Immediate | `2` turns |
| Winds of Fate | `150` | Randomly selects one command and completes its cooldown | Immediate | `2` turns |
| Charge | `75` | Doubles one controlled troop's movement attribute | Current turn | `5` turns |
| Chastise | `50` | One enemy troop cannot move or attack; cannot target the opponent's last remaining troop | Opponent's next turn | `3` turns |
| Vigilance | `50` | One controlled troop strikes first when defending | Until the start of the player's next turn | `3` turns |
| Shield Wall | `50` | All damage dealt to one controlled troop is reduced to `100` | Until the start of the player's next turn | `5` turns |

There is no tenth cutoff command. The unresolved detail is when a “turn” ticks a
cooldown: owner-turn start, owner-turn end, or every player turn. That boundary
belongs in the placeholder register rather than being inferred.

## Turn structure and command points

### Four phases

`C` states that every turn has four ordered phases:

1. **Selection** — choose one troop; the UI shows its movement and targets.
2. **Movement** — move that troop until its movement is exhausted or stop early.
3. **Combat** — attack with the selected troop or end the turn.
4. **Rally** — inspect the board and issue final commands before ending the turn.

Commands may be issued in any phase. One turn therefore activates one troop for
movement and at most one ordinary attack; commands are separate actions.

### Command-point income

| mechanism | pinned evidence | status |
| --- | --- | --- |
| ordinary passive increment | **25 command points** | `CG`: the first player receives none on the very first move, so the second player begins `25` points ahead |
| opening player | No passive points on the first move | `CG` |
| normal troop defeat | Grants command points | `C` |
| defeat amount | Examples equal the defeated troop's setup cost: Scout `25`; Archer or Mage `100` | `CG`; strong reconstruction, but no single formal equation was recovered |
| Bombard defeat | Grants `0` command points | `C` |
| starting balance | Not formally stated | Placeholder candidate |
| passive-grant phase | Not formally stated | Placeholder candidate |

The period evidence strongly supports “normal kill award = defeated troop cost,”
but implementation should preserve the placeholder marker until a server routine
or decoded CS2 operand closes the equation.

## Victory, draw, resignation, disconnect, and timers

| outcome/rule | pinned behavior | provenance |
| --- | --- | --- |
| ordinary victory | Kill all opposing troops | `C` |
| truce | A mutually accepted truce ends in a draw | `C`; rev-727/rev-742 interface archive `1008`/`1019` |
| resignation | Ends Conquest immediately | rev-727/rev-742 interface archive `1019`; `C` |
| early ending | An early truce, resignation, or army elimination gives neither player rating change or commendations | `C` |
| disconnect | Remaining player may wait or accept victory | `C`; rev-727/rev-742 CS2 archives `424`, `425` |
| automatic-match turn timer | `1` minute | `C` |
| invited-match timer choices | `30` seconds through `3` minutes, in `30`-second intervals | `C` |
| timer warning | Bell at `10` seconds remaining | `C` |
| timer expiry behavior | Unresolved | No pre-cutoff rule states whether expiry ends the phase, ends the turn, or forfeits |

The exact threshold separating an “early” unrated/unrewarded game from a valid
rated match is not recovered.

## Rating

| rating rule | pinned value | provenance |
| --- | --- | --- |
| starting rating | **1,000** | `C`; rev-727/rev-742 interface archive `1009` |
| update shape | Depends on result and both players' ratings; symmetric gain/loss in the documented example | `C` |
| worked example | Rating `2,500` defeats rating `1,311`; winner gains `11`, loser loses `11` | `C` |
| zero | Rating `0` is attainable and can gain again | `P0` |
| hiscores threshold | **1,250** | `C` |
| deflector threshold | **1,250** | `C`, `VKD`; rev-727/rev-742 CS2 archive `468` |
| trimmed Completionist requirement | **1,250** | `CC` |
| exact equation/K-factor | Unresolved | No server routine, decoded script, or historical equation recovered |
| minimum/maximum cap | Unresolved | `0` is observed, but not expressly defined as a floor; no maximum is stated |
| truce arithmetic | Qualitative only | `C`: near-ties generally cost both a small amount; the leading player may receive more |

The system is Elo-shaped because the change depends on both ratings, but calling
it a particular Elo formula would invent the K-factor and expectation curve.
`1,250` is an unlock threshold, not a rating cap.

## Commendation awards

### Period match formula

A match determines one shared **Commendation Ratio** from `1` through `10`, with
longer matches receiving the higher ratio. Both players receive the same ratio;
winning gives no bonus. Each player's combat-level band then multiplies it.
Source: `C`.

| combat level | multiplier | possible award shape | maximum | provenance |
| --- | ---: | --- | ---: | --- |
| `40-69` | `×2` | `2, 4, 6, …, 20` | `20` | `C` |
| `70-99` | `×3` | `3, 6, 9, …, 30` | `30` | `C` |
| `100+` | `×4` | `4, 8, 12, …, 40` | `40` | `C` |

The worked example is approximately `19` rounds at ratio `7`: a level `85`
player receives `3 × 7 = 21`; a level `112` player receives `4 × 7 = 28`.
A thirty-minute game using three-minute turns and only five turns per player is
explicitly not enough to reach the maximum.

The exact turn-count thresholds for ratios `1` through `10` are not stated. That
curve is the largest reward placeholder candidate.

### Shared wallet

`C`, `UC`, and `VKC` establish one wallet shared by Pest Control, Conquest, and
`A Void Dance`:

- commendations appear as “Pest Points” while on a lander;
- the wallet cap is **500**;
- Conquest's launch doubled the former cap from `250` to `500` because two
  activities could award the currency;
- `A Void Dance` awards **50** into the same wallet.

### Existing AnkiScape integration point

AnkiScape already stores that exact shared balance at the top level:

- default key: `"pest_control_commendations": 0` at
  `logic/pest_control_logic.py:71-83`;
- sanitizer and cap application at `logic/pest_control_logic.py:133-156`;
- cap `500` at `data/pest_control_data.py:19-23`;
- new-save default merge at `core/storage_pure.py:545-565`;
- Pest Control capped credit at `logic/pest_control_logic.py:350-369`;
- Void seal spending at `logic/pest_control_logic.py:551-568`.

Conquest must credit and debit `pest_control_commendations`; it must not create a
Conquest-only currency. Credit must pass through the same `500` cap. The current
Void seal purchase path checks only for an active Pest Control session, so the
mechanical implementation should also preserve the project's one-active-activity
contract when a Conquest session exists; this audit does not change that code.

## Rewards and unlocks

### Conquest-specific unlock

The **Void knight deflector** is the unique Conquest reward.

| requirement/property | pinned value | provenance |
| --- | --- | --- |
| rating requirement | **1,250** | `C`, `VKD`; cache CS2 archive `468` |
| commendation price | **150** | `VKC`, `VKD` |
| wallet | Shared Pest Control/Conquest commendations | `C`, `UC`, `VKC` |
| set behavior | May replace one non-helm Void armour component while retaining the set effect; cannot replace the special helm | `VKD` |

Rating `1,250` also enables Conquest hiscores placement and is one trimmed
Completionist-cape requirement. It does not directly award the cape.

### Shared commendation shop at cutoff

| reward | cost/gate | provenance |
| --- | --- | --- |
| Void knight mace | `250` commendations | `VKC` |
| Void knight top | `250` | `VKC` |
| Void knight robe | `250` | `VKC` |
| Void knight gloves | `150` | `VKC` |
| Void melee helm | `200` | `VKC` |
| Void magic helm | `200` | `VKC` |
| Void ranger helm | `200` | `VKC` |
| Void knight deflector | `150` plus rating `1,250` | `VKC`, `VKD` |
| Void knight seal | `10`; `8` charges | `VKC` |
| Elite top upgrade | `100` plus ordinary top and completion of `The Void Stares Back` | `VKC` |
| Elite robe upgrade | `100` plus ordinary robe and completion of `The Void Stares Back` | `VKC` |
| Herb pack | `30`; Herblore `25` | `VKC` |
| Mineral pack | `15` | `VKC` |
| Seed pack | `15`; Farming `25` | `VKC` |
| Ravager/Shifter/Spinner/Torcher charms | `2` each; bundles of `1`, `14`, or `28` | `VKC` |

No standalone cosmetic override or cosmetic item earned specifically through
ordinary Conquest was recovered. The elite torso variants and their `100,000`-
coin colour change are `The Void Stares Back` quest rewards, not Conquest
rewards. The six pest troops are quest encounter units, not troop skins.

## Battlefield and layout record

| feature | pinned record | provenance |
| --- | --- | --- |
| playable-board statement | **20×20 squares** | `C` |
| conflicting statement | **22×22** | Scout article oldid `4877028` |
| owner-settled implementation board | **20×20** | `memory-bank/source-audits/competitive-tier-adaptations-2026-07-18.md:24-31` |
| deployment | First `3` rows per side | `C` |
| obstacles | Exist and affect manoeuvring | `CG` |
| map count/names/weights | Unresolved | No pre-cutoff table recovered |
| obstacle coordinates/shapes | Unresolved | No pre-cutoff table recovered |

The `20×20`/`22×22` conflict may be playable squares versus a border-inclusive
measurement, but no period source proves that explanation. The settled engine
uses `20×20`; `conquest.board_size` remains a placeholder candidate so a decoded
interface grid or period map can replace the disputed value cleanly.

## Regular and staked modes

Rev-727 and rev-742 interface archive `1026` exposes **Regular Conquest** and
**Staked Conquest**. The current owner-settled solo adaptation specifies the
board game, doctrines, rating, and commendations, and therefore maps the regular
mode. No stake denomination, escrow, settlement, or anti-faucet contract was
harvested. Staked Conquest is period data depth outside this mechanical-completion
pass, not permission to mint simulated-opponent wealth.

## Bounded solo mechanical mapping

The authentic two-player game maps onto the settled one-player adaptation as
follows.

| period system | bounded solo mapping |
| --- | --- |
| two human commanders | One player-selected loadout/doctrine and one labelled simulated opponent |
| hidden decision-making | The same modest deterministic/seeded heuristic controls both armies; doctrine changes priorities, not troop stats or matchup odds |
| board | One bounded `20×20` board state generated once at match start; no offscreen population or world simulation |
| setup | Both sides receive the same sourced `1,000` points, unit-cap placeholder, deployment rows, and command-count limit |
| turns | One review resolves one complete player/opponent turn exchange through the four sourced phases |
| movement/combat | Legal destinations and attacks come only from sourced movement, range, damage, LP, obstacles, and command effects |
| result | Elimination, truce/draw, resignation, disconnect-equivalent termination, and early-game reward suppression retain their sourced meanings |
| rating | Apply the same opponent-rating-sensitive update to both sides once the exact formula or registered placeholder is supplied |
| commendations | Compute one match-length ratio, multiply independently by the player's combat band, credit the existing shared wallet, and cap at `500` |
| persistence | Persist only setup/loadout, doctrine, board and troop state, command points/cooldowns, turn owner/count, rating inputs, and terminal/reward state |
| bounded work | At most the fixed board and fixed squad cap are inspected per turn; no background loop, missed-turn replay, or inactive-session advancement |
| undo | Restore the one atomic review exchange, not a hidden simulation trace |

A smaller matchup roll would erase the player's sourced loadout, ranges,
obstacles, commands, cooldowns, and doctrine choice. The bounded board reducer is
therefore justified under the simulation budget contract.

## Placeholder candidates

These are **candidates only**. They are not yet rows in
`memory-bank/placeholder-values.md`, because this harvest does not modify code.
Each implementation value must carry `# PLACEHOLDER(<id>)` and a matching live
register row. Confidence describes the proposed temporary value, not historical
closure.

| proposed id | temporary value or shape | confidence | what it unblocks | what would settle it |
| --- | --- | --- | --- | --- |
| `conquest.board_size` | `20×20` playable squares | high | Board allocation and coordinate bounds | Decoded period board interface/map showing whether the `22×22` statement includes borders |
| `conquest.squad_unit_cap` | `10` troops per side | medium | Setup validation and bounded heuristic work | Period setup interface operand or server-side squad validator |
| `conquest.foot_soldier_cost` | `50` setup points | medium | Exact `1,000`-point loadout validation | Period client troop config or patch note resolving the `30` UI image against the nearer-cutoff `50` wikitext |
| `conquest.starting_command_points` | `0` | medium | Initial command availability | Server start-state routine or decoded interface varp/CS2 operand |
| `conquest.passive_command_points` | `25` at the start of each ordinary owner turn, except the opening player receives none on turn one | high on amount; medium on phase | Command economy | Server turn-transition routine or decoded CS2 showing the exact grant boundary |
| `conquest.kill_command_points` | Award the defeated troop's setup cost for a normal attack kill; `0` for Bombard | high | Kill rewards and command feedback loop | Server defeat routine or period rules text stating the equation directly |
| `conquest.command_cooldown_boundary` | Decrement once at the start of the command owner's turn | low | All nine command cooldowns | Server command scheduler or decoded CS2 phase transition |
| `conquest.first_player_selection` | Seeded fair choice between sides | low | Match initialization and the sourced second-player CP advantage | Period matchmaking/start routine |
| `conquest.early_game_eligibility_threshold` | Unassigned; implementation must choose and label the minimum turn count | low | Rating and commendation suppression for early elimination/truce/resignation | Server reward routine or dated guide stating the threshold |
| `conquest.rating_formula` | Opponent-rating-sensitive symmetric update calibrated to preserve the sourced `2500` vs `1311` → `±11` example | low | Persistent rating | Period server formula, cache script operands, or official equation |
| `conquest.turn_ratio_curve` | Monotone `1-10` commendation-ratio table preserving the sourced ratio `7` around `19` rounds and the five-turn-each example below maximum | low | Match commendation payout | Period reward routine or complete dated ratio table |
| `conquest.turn_timeout_resolution` | Force the current player to end the turn without forfeiting | low | `30`-second to `3`-minute turn timers | Period server timeout routine or dated gameplay recording |
| `conquest.battlefield_layouts` | Small seeded fixed obstacle-layout pool on the bounded board | low | Authentic range/pathing interaction | Period map-region data, interface tile grid, or dated screenshots sufficient to reconstruct obstacle coordinates |
| `conquest.pest_movement_range_cost` | Torcher movement `4`, range `6`, cost `75`; keep quest-only | low | Complete `The Void Stares Back` pest roster only | Pre-cutoff Torcher details image, quest server table, or period client config |

The unknown ratio curve and exact rating formula must not be described as
period-accurate. The Foot Soldier and board-size rows are source conflicts, not
permission to invent a third value.

## Conflicts and exclusions

- **Darkan/game-main absence:** neither emulator supplies a Conquest server
  implementation. Wiki values are therefore the primary supplier, with the
  byte-identical rev-727/rev-742 client interfaces as corroboration where they
  expose a value.
- **Board size:** main page `20×20`; Scout page `22×22`. Use the settled `20×20`
  board under a placeholder marker until client geometry resolves the count.
- **Foot Soldier cost:** cutoff wikitext `50`; release-era details image `30`.
  Use the nearer-cutoff `50` under a placeholder marker.
- **Knight range:** bad infobox `4`; in-game image and melee-range prose prove
  `1`.
- **Mage range:** bad prose `3`; infobox and in-game image prove `4`.
- **Champion LP:** original `600`; post-balance cutoff value `500`.
- **Reward wording:** the earlier AnkiScape design note says “wins pay
  rating-scaled commendations”; the period source says both sides receive the
  same turn-scaled ratio, multiplied by combat-level band, with no winner bonus.
- **No combat triangle:** no pinned source defines one; do not add it.
- **No hybrid roster:** later hybrid-unit claims do not resolve to a pinned
  period troop definition; omit them.
- **No invented cosmetics:** the deflector is a functional reward. Quest torso
  colours and pest troops are not ordinary Conquest cosmetic unlocks.
- **No staked-mode faucet:** the cache proves the mode name, not a safe solo
  economy contract.

## Design forks

**None for the core family.** The owner already settled the real-board,
same-heuristic, loadout-plus-doctrine adaptation. The remaining uncertainties
are source values suitable for explicit placeholders, not taste calls.

Staked Conquest remains period data depth. Adding simulated-opponent stakes would
require a separate economy contract; it is not part of the settled regular-mode
mechanical completion and is not decided here.
