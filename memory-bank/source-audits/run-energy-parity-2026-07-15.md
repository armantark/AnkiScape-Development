# RuneScape run-energy parity verdict for the 2012-11-20 freeze

## Executive verdict

| Question | Verdict for 2012-11-20 | Confidence | Controlling evidence |
|---|---|---:|---|
| 1. Does Agility affect drain or only recovery? | **It is not recovery-only. Agility affected running endurance as well as recovery.** The source-safe formulation is that Agility increased the distance obtainable per run-energy point; representing that benefit on the drain side is therefore the correct AnkiScape model family. Whether the original server implemented this as a smaller drain debit or another net-loss mechanism is not exposed by the period source. | **High** for the running-endurance effect; **source_blocked** for the server's internal placement | Jagex's 9 June 2009 update says Agility both reduced recharge time and “increases the distance you can run per run energy point.” ([oldid 4264036, revision timestamp 2011-05-10T23:09:21Z](https://runescape.wiki/w/Update:Run_energy_upgrade?oldid=4264036)) |
| 2. What does negative weight do? | **Treat effective weight below 0 kg as 0 kg for drain.** | **Medium** | The closest pre-freeze `Weight` revision explicitly equates negative and 0 kg, and the closest `Energy` revision's timed trivia groups 0 kg and negative weight together. The latter article also contains a directly contradictory prose sentence saying negative weight improves drain below 0, so this cannot honestly be high confidence. ([oldid 6512729, 2012-10-31T17:47:14Z](https://runescape.wiki/w/Weight?oldid=6512729); [oldid 6357372, 2012-10-06T18:25:51Z](https://runescape.wiki/w/Energy?oldid=6357372)) |
| 3. What exact drain and recovery formulas were live? | **`source_blocked` for the exact period formulas.** The closest sourceable characterization is: Agility improves both running endurance and recovery; greater positive weight increases drain; effective negative weight most likely clamps to 0; recovery occurs while not running and rises with Agility. Model A is the closer reconstruction, but its constants remain emulator evidence, not a pinned 2012 formula. | **source_blocked** for exact constants; **high** for the Agility model family; **medium** for the negative-weight clamp | The official update fixes the Agility behavior, while the closest period `Energy` and `Weight` pages provide only prose and mutually inconsistent timing/negative-weight statements rather than an equation. ([oldid 4264036, 2011-05-10T23:09:21Z](https://runescape.wiki/w/Update:Run_energy_upgrade?oldid=4264036); [oldid 6357372, 2012-10-06T18:25:51Z](https://runescape.wiki/w/Energy?oldid=6357372); [oldid 6512729, 2012-10-31T17:47:14Z](https://runescape.wiki/w/Weight?oldid=6512729)) |
| 4. Is running 2 tiles per tick? | **Yes: running is 2 squares/tiles per tick and walking is 1.** | **High** | The closest pre-freeze `Game tick` revision states the 2:1 per-tick mapping, and the closest `Energy` revision independently describes running as exactly twice walking speed. ([oldid 6117417, 2012-08-20T11:46:01Z](https://runescape.wiki/w/Game_tick?oldid=6117417); [oldid 6357372, 2012-10-06T18:25:51Z](https://runescape.wiki/w/Energy?oldid=6357372)) |

**Bottom line:** AnkiScape should model the freeze-date Agility lever as **drain-based in effect (Model A family), not recovery-only (Model B family)**. The exact Model A constants should retain an `emulator_reconstruction`/`source_blocked` provenance label rather than being presented as period-sourced truth. ([oldid 4264036, 2011-05-10T23:09:21Z](https://runescape.wiki/w/Update:Run_energy_upgrade?oldid=4264036); `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/mechanics/run/RunEnergy.kt:21-44`)

## 1. Agility: the load-bearing fork

The governing dated change is Jagex's **9 June 2009 Run energy upgrade**. It adjusted both drain and return rates and said that Agility now improved recharge time **and** distance per run-energy point, with an especially larger benefit at levels 50–99. That rules out the local Darkan behavior as a complete freeze-date model, because Darkan's running debit has weight and a base constant but no Agility term. ([oldid 4264036, revision timestamp 2011-05-10T23:09:21Z](https://runescape.wiki/w/Update:Run_energy_upgrade?oldid=4264036); `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/model/entity/Entity.java:784-789`)

The closest pre-freeze `Agility` article says higher Agility recharges energy more quickly and identifies the 9 June 2009 rest update, but it does not supply a drain equation or negate the official update's separate running-endurance statement. ([oldid 6477884, revision timestamp 2012-10-26T18:06:37Z](https://runescape.wiki/w/Agility?oldid=6477884))

The contemporaneous talk page is non-authoritative but directionally consistent: comments dated immediately after the 9 June 2009 update report a change to running time as well as restore rate. It is corroboration only, not the basis of the verdict. ([oldid 6106277, revision timestamp 2012-08-18T17:55:52Z](https://runescape.wiki/w/Talk:Energy?oldid=6106277))

**Verdict:** Agility was a running-endurance lever and a recovery lever on 2012-11-20. Calling it “recovery-only” would contradict the official 2009 update; calling the original server's exact internal operation a literal subtraction from drain is `source_blocked`. ([oldid 4264036, revision timestamp 2011-05-10T23:09:21Z](https://runescape.wiki/w/Update:Run_energy_upgrade?oldid=4264036))

## 2. Negative weight: explicit conflict in the period Wiki

Evidence for a zero clamp:

- The closest pre-freeze `Weight` revision says negative weight has the same run-energy effect as 0 kg. ([oldid 6512729, revision timestamp 2012-10-31T17:47:14Z](https://runescape.wiki/w/Weight?oldid=6512729))
- The closest pre-freeze `Energy` revision says in its trivia that the 100%-to-0% duration is the same category for “0 kg or negative weight.” ([oldid 6357372, revision timestamp 2012-10-06T18:25:51Z](https://runescape.wiki/w/Energy?oldid=6357372))
- The 2012 `Talk:Energy` revision contains an older explanation that negative gear remains useful because it offsets subsequently carried positive weight without lowering stamina; this is weak talk-page corroboration for a floor at 0. ([oldid 6106277, revision timestamp 2012-08-18T17:55:52Z](https://runescape.wiki/w/Talk:Energy?oldid=6106277))
- Model A applies `coerceAtLeast(0.0)` before its weight exponent. (`/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/mechanics/run/RunEnergy.kt:42-44`)

Evidence against a zero clamp:

- A prose sentence in the same closest `Energy` revision says negative weight improves drain compared with 0 kg. This conflicts with that article's own timed trivia and with the closer-dated `Weight` page. ([oldid 6357372, revision timestamp 2012-10-06T18:25:51Z](https://runescape.wiki/w/Energy?oldid=6357372))
- Darkan passes negative weight through `min(weight, 64)` with no lower clamp. (`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/model/entity/Entity.java:784-789`)

**Verdict:** use `max(weight, 0)` for run-energy drain, **medium confidence**. The direct `Weight` statement and the `Energy` timed grouping outweigh one conflicting sentence, but the period record is not unanimous. ([oldid 6512729, revision timestamp 2012-10-31T17:47:14Z](https://runescape.wiki/w/Weight?oldid=6512729); [oldid 6357372, revision timestamp 2012-10-06T18:25:51Z](https://runescape.wiki/w/Energy?oldid=6357372))

## 3. Formula reconstruction and the exact-source boundary

### What the pinned period sources establish

The closest `Energy` revision establishes that energy depletes while running, recovers while not running, positive carried weight raises the depletion rate, and recovery rises with Agility. It gives level-1 recovery observations of 0.45 energy/second while walking or standing, 2.8 energy/second while resting, and about 25 seconds from 0 to 100 near a musician; it does not give a complete equation. ([oldid 6357372, revision timestamp 2012-10-06T18:25:51Z](https://runescape.wiki/w/Energy?oldid=6357372))

That same revision also gives incompatible-looking observations: it groups 0 kg and negative weight into a 62-second depletion time, yet separately reports about 95 seconds of running at 99 Agility and 0 kg; its recovery prose says each level above 1 removes about one second from full recharge while its level-1 rate and level-70/90 examples do not define one consistent interpolation. These are observations and wiki prose, not a sufficiently reliable exact formula. ([oldid 6357372, revision timestamp 2012-10-06T18:25:51Z](https://runescape.wiki/w/Energy?oldid=6357372))

### Model A: closest supported reconstruction, not period authority

The local 2011Scape checkout identifies itself as a 2011 experience and links a revision-667 cache, so it is a reconstruction rather than a primary source. (`/Users/ArmanTarkhanian1/Downloads/game-main/README.md:13-21`; `/Users/ArmanTarkhanian1/Downloads/game-main/README.md:28-46`)

Its exact drain candidate is:

```text
D_A(L, W) = (0.7 - 0.002L) / 0.92^(max(W, 0) / 10)
```

where the code applies the debit only while running and moving; the formula and zero floor are directly visible in the local implementation. (`/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/mechanics/run/RunEnergy.kt:21-22`; `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/mechanics/run/RunEnergy.kt:36-50`)

Its exact per-tick recovery candidates are linear interpolation by Agility level from 1 through 99: walking `0.27 -> 0.36`, ordinary rest `1.68 -> 2.4`, and musician rest `2.28 -> 4.0`. (`/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/mechanics/run/RunEnergy.kt:56-65`; `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/mechanics/run/RunEnergy.kt:77-81`)

A 2023 2011Scape commit changed the same file from the Darkan-style formula family to the present Model A family with the message that run-energy depletion and restoration had changed in 2009. This is useful reconstruction provenance, but it is a modern emulator-maintainer judgment rather than contemporaneous RuneScape evidence. ([2011Scape/game commit `d7c427039602832fce68cfe3a40262dc5f5df4d4`, 2023-03-06T20:35:16Z](https://github.com/2011Scape/game/commit/d7c427039602832fce68cfe3a40262dc5f5df4d4))

### Model B: exact local behavior and why it loses the parity fork

Darkan debits `(min(weight, 64) / 100) + 0.64` when a second running step exists; no Agility term or lower weight floor appears in that debit. (`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/model/entity/Entity.java:758-789`)

Darkan's non-running recovery is `(8 + floor(Agility/6)) / 100` per processing call, replaced by a flat `1.68` while resting or `2.28` near a musician. Its restore and drain methods add or subtract exactly the passed double with a 0–100 bound. (`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/model/entity/player/Player.java:1088-1097`; `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/model/entity/player/Player.java:1264-1281`)

A separate GitHub #727 emulator, Jupiter, contains the same linear/capped-above drain expression, but that is only low-weight emulator clustering and does not override the Jagex update. ([CSS-Lletya/Jupiter, `src/com/jupiter/game/Entity.java:405-410`, commit `b68857b9d1da0f54a2f0e631749403035e064676`](https://github.com/CSS-Lletya/Jupiter/blob/b68857b9d1da0f54a2f0e631749403035e064676/src/com/jupiter/game/Entity.java#L405-L410))

**Exact-formula verdict:** `source_blocked`. No inspected pre-freeze oldid supplies a complete drain or recovery equation, and the numerical statements in the closest `Energy` oldid are not internally sufficient to derive one uniquely. Model A should be used if AnkiScape must choose between the two on-disk implementations, because only its model family includes the officially documented running-endurance benefit from Agility. ([oldid 4264036, revision timestamp 2011-05-10T23:09:21Z](https://runescape.wiki/w/Update:Run_energy_upgrade?oldid=4264036); [oldid 6357372, revision timestamp 2012-10-06T18:25:51Z](https://runescape.wiki/w/Energy?oldid=6357372); `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/mechanics/run/RunEnergy.kt:21-44`)

## 4. Movement rate

The closest pre-freeze `Game tick` revision describes the main RuneScape tick as approximately 0.6 seconds and explicitly maps running to 2 squares per tick and walking to 1 square per tick. ([oldid 6117417, revision timestamp 2012-08-20T11:46:01Z](https://runescape.wiki/w/Game_tick?oldid=6117417))

The closest `Energy` revision independently says running is exactly twice walking and gives 20 versus 10 squares in the same six-second interval. ([oldid 6357372, revision timestamp 2012-10-06T18:25:51Z](https://runescape.wiki/w/Energy?oldid=6357372))

Darkan's movement loop also processes two steps for run and one for walk, which corroborates the pinned Wiki evidence. (`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/model/entity/Entity.java:758-772`)

**Verdict:** running = 2 tiles/tick; walking = 1 tile/tick, **high confidence**. ([oldid 6117417, revision timestamp 2012-08-20T11:46:01Z](https://runescape.wiki/w/Game_tick?oldid=6117417))

## Rework date and history search

The sourceable governing rework is **2009-06-09**, not a change between the 2011 and 2012 emulator targets. Jagex's update changed drain and return, introduced ordinary rest and faster musician recovery, rebalanced energy-restoring consumables, and expanded Agility's benefit to both recharge and distance per energy point. ([oldid 4264036, revision timestamp 2011-05-10T23:09:21Z](https://runescape.wiki/w/Update:Run_energy_upgrade?oldid=4264036))

The MediaWiki history lookup requested for the freeze returned these closest revisions at or before 2012-11-20: `Run` oldid 80708 at 2007-03-11T17:51:17Z and `Run energy` oldid 121017 at 2007-04-29T22:28:58Z, both redirects to `Energy`; `Energy` oldid 6357372 at 2012-10-06T18:25:51Z; `Weight` oldid 6512729 at 2012-10-31T17:47:14Z; and `Agility` oldid 6477884 at 2012-10-26T18:06:37Z. ([Run oldid 80708](https://runescape.wiki/w/Run?oldid=80708); [Run energy oldid 121017](https://runescape.wiki/w/Run_energy?oldid=121017); [Energy oldid 6357372](https://runescape.wiki/w/Energy?oldid=6357372); [Weight oldid 6512729](https://runescape.wiki/w/Weight?oldid=6512729); [Agility oldid 6477884](https://runescape.wiki/w/Agility?oldid=6477884))

The relevant `Energy` wording was checked across oldids 4119366 (2011-04-08T01:18:31Z), 4995346 (2011-11-28T20:37:33Z), 5120601 (2012-01-07T20:05:33Z), 5436165 (2012-03-29T17:22:41Z), 5706060 (2012-06-03T04:00:29Z), 5906348 (2012-07-08T11:20:19Z), and 6357372 (2012-10-06T18:25:51Z); the same relevant claims about Agility recovery, negative-weight improvement, the 0-or-negative timed grouping, and 99-Agility running persisted through those snapshots. ([oldid 4119366](https://runescape.wiki/w/Energy?oldid=4119366); [oldid 4995346](https://runescape.wiki/w/Energy?oldid=4995346); [oldid 5120601](https://runescape.wiki/w/Energy?oldid=5120601); [oldid 5436165](https://runescape.wiki/w/Energy?oldid=5436165); [oldid 5706060](https://runescape.wiki/w/Energy?oldid=5706060); [oldid 5906348](https://runescape.wiki/w/Energy?oldid=5906348); [oldid 6357372](https://runescape.wiki/w/Energy?oldid=6357372))

**History verdict:** no 2011-to-2012-11-20 run-energy/weight rework was found in the requested page histories. The dated rework that explains the fork is 9 June 2009; a categorical claim that no unrecorded server-side adjustment occurred later remains `source_blocked`. ([oldid 4264036, revision timestamp 2011-05-10T23:09:21Z](https://runescape.wiki/w/Update:Run_energy_upgrade?oldid=4264036); history snapshots listed immediately above)

## OpenRS2 cache results

### Item weights

The item-definition decoder successfully opened the seven requested client caches: `652-2011-06-08`, `727-2012-07-24`, `728-2012-08-01`, `729-2012-08-11`, `736-2012-10-09`, `741-2012-11-04`, and `742-2012-11-07`. The queried IDs were Boots of lightness 88, spotted cape 10069, spottier cape 10071, Agile top 14936, and Agile legs 14938. (cache revision ids `652-2011-06-08`, `727-2012-07-24`, `728-2012-08-01`, `729-2012-08-11`, `736-2012-10-09`, `741-2012-11-04`, `742-2012-11-07`)

The revision-652 decoder returned no usable name or client parameters for IDs 14936 and 14938. Revisions 727 through 742 returned stable names and client-parameter maps for all five queried items, but no decoded weight field or weight parameter for any of them. The caches therefore do **not** source the sign or magnitude of these weights. (cache revision ids `652-2011-06-08`, `727-2012-07-24`, `728-2012-08-01`, `729-2012-08-11`, `736-2012-10-09`, `741-2012-11-04`, `742-2012-11-07`)

**Cache weight status:** `source_blocked (decoded, but weight is not present in the decoded client item definitions)`, not `not_decoded`. No `+12.0` or `+10.0` weight values appeared in the decoded client definitions for IDs 14936/14938. (cache revision ids `727-2012-07-24`, `728-2012-08-01`, `729-2012-08-11`, `736-2012-10-09`, `741-2012-11-04`, `742-2012-11-07`)

The closest pre-freeze Wiki nevertheless supplies the live item sign independently: Agile top is **-12 kg** and Agile legs are **-10 kg**. ([oldid 6512729, revision timestamp 2012-10-31T17:47:14Z](https://runescape.wiki/w/Weight?oldid=6512729))

The suspected sign anomaly exists in Darkan's server-side JSON on adjacent duplicate IDs, not the primary item IDs: 14936 is -12.0 while 14937 is +12.0, and 14938 is -10.0 while 14939 is +10.0. The server loads item weight from that JSON and only applies negative weight when the item is equipped. (`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/items/config.json:167904-167945`; `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/utils/ItemConfig.java:34-45`; `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/utils/ItemConfig.java:131-138`)

### CS2

The revision-742 CS2 index reported 6,936 archives, but the available Darkan decoder successfully decoded only 30 and failed on 6,906; none of those 30 decoded scripts contained the literal terms `energy`, `stamina`, or `rest` in the script name/string operands. That partial scan cannot establish that no relevant energy-orb script exists. (cache revision id `742-2012-11-07`)

**CS2 status:** `not_decoded` for formula-relevant coverage. No client-side drain or recovery formula is claimed from this cache. (cache revision id `742-2012-11-07`)

## Source-blocked ledger

1. **Original server drain equation:** `source_blocked`. Checked the closest pre-freeze `Run`/`Run energy` redirects, `Energy`, `Weight`, `Agility`, `Game tick`, the official 2009 update, the two local emulators, one #727 web emulator, and cache revisions 652/727/728/729/736/741/742; none is a contemporaneous source containing the complete equation. ([oldid 6357372, 2012-10-06T18:25:51Z](https://runescape.wiki/w/Energy?oldid=6357372); [oldid 6512729, 2012-10-31T17:47:14Z](https://runescape.wiki/w/Weight?oldid=6512729); [oldid 6477884, 2012-10-26T18:06:37Z](https://runescape.wiki/w/Agility?oldid=6477884); [oldid 4264036, 2011-05-10T23:09:21Z](https://runescape.wiki/w/Update:Run_energy_upgrade?oldid=4264036); cache revision ids `652-2011-06-08`, `727-2012-07-24`, `728-2012-08-01`, `729-2012-08-11`, `736-2012-10-09`, `741-2012-11-04`, `742-2012-11-07`)
2. **Original server recovery equation:** `source_blocked`. The closest period `Energy` page supplies observational rates but no consistent complete interpolation, and the official update supplies behavior rather than constants. ([oldid 6357372, 2012-10-06T18:25:51Z](https://runescape.wiki/w/Energy?oldid=6357372); [oldid 4264036, 2011-05-10T23:09:21Z](https://runescape.wiki/w/Update:Run_energy_upgrade?oldid=4264036))
3. **Weight values from the client caches:** `source_blocked (decoded; field absent)`. The sign is sourced instead from the period `Weight` oldid and corroborated by Darkan's separate server JSON. ([oldid 6512729, 2012-10-31T17:47:14Z](https://runescape.wiki/w/Weight?oldid=6512729); cache revision ids `727-2012-07-24`, `728-2012-08-01`, `729-2012-08-11`, `736-2012-10-09`, `741-2012-11-04`, `742-2012-11-07`; `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/items/config.json:167904-167945`)
4. **A later unrecorded rework between 2011 and 2012-11-20:** `source_blocked` as an absolute negative. No such rework was found in the requested page histories; the only sourced governing rework found was 2009-06-09. ([oldid 4264036, 2011-05-10T23:09:21Z](https://runescape.wiki/w/Update:Run_energy_upgrade?oldid=4264036); [oldid 4119366](https://runescape.wiki/w/Energy?oldid=4119366); [oldid 6357372](https://runescape.wiki/w/Energy?oldid=6357372))

## Compact summary

1. **Agility:** affects running endurance and recovery; not recovery-only — **high**. ([oldid 4264036, 2011-05-10T23:09:21Z](https://runescape.wiki/w/Update:Run_energy_upgrade?oldid=4264036))
2. **Negative weight:** clamp effective drain weight to 0 kg — **medium** because the closest period pages conflict. ([oldid 6512729, 2012-10-31T17:47:14Z](https://runescape.wiki/w/Weight?oldid=6512729); [oldid 6357372, 2012-10-06T18:25:51Z](https://runescape.wiki/w/Energy?oldid=6357372))
3. **Exact formulas:** **source_blocked**; Model A is the closest supported reconstruction, with its constants still labelled emulator-derived. ([oldid 4264036, 2011-05-10T23:09:21Z](https://runescape.wiki/w/Update:Run_energy_upgrade?oldid=4264036); `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/mechanics/run/RunEnergy.kt:21-44`)
4. **Movement:** run = 2 tiles/tick; walk = 1 tile/tick — **high**. ([oldid 6117417, 2012-08-20T11:46:01Z](https://runescape.wiki/w/Game_tick?oldid=6117417))

**Bottom line:** use a **drain-based Agility lever (Model A family)** for the 2012-11-20 freeze; do not use recovery-only Model B parity. ([oldid 4264036, 2011-05-10T23:09:21Z](https://runescape.wiki/w/Update:Run_energy_upgrade?oldid=4264036))
