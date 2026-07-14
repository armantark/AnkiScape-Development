# Agility obstacle fail-chance source audit — 2026-07-13

## Scope and evidence contract

This audit searches for the fail-chance curves needed by the pre-EOC Agility course model. It does not revisit settled obstacle, damage, XP, or mastery-cutoff evidence. No value ships unless its expression and every numeric parameter are cited and tiered.

## Avenue 1 — Pinned pre-EOC RuneScape Wiki

### Method and exhaustion record

I used `tools/wiki_parity.py` against the RuneScape Wiki import and searched literal revision wikitext, not rendered modern dependencies. The search covered the `Agility` skill page plus all ten course/activity pages from the preceding audit, every revision at or before the cutoff, for **3,592 main-page revisions** in total:

| Page | Revisions read | Newest pinned oldid | Oldest revision reached |
|---|---:|---:|---|
| Agility | 1,697 | [`6477884`](https://runescape.wiki/?oldid=6477884), 2012-10-26 | `3298`, 2006-03-22 |
| Gnome Stronghold Agility Course | 268 | [`6391497`](https://runescape.wiki/?oldid=6391497), 2012-10-12 | `73814`, 2007-03-02 |
| Barbarian Outpost Agility Course | 226 | [`6549278`](https://runescape.wiki/?oldid=6549278), 2012-11-12 | `35135`, 2006-11-02 |
| Wilderness Agility Course | 250 | [`6487716`](https://runescape.wiki/?oldid=6487716), 2012-10-28 | `172158`, 2007-06-12 |
| Burthorpe Agility Course | 38 | [`6130636`](https://runescape.wiki/?oldid=6130636), 2012-08-23 | `5202426`, 2012-01-31 |
| Agility Pyramid | 196 | [`6457748`](https://runescape.wiki/?oldid=6457748), 2012-10-23 | `23136`, 2006-09-10 |
| Ape Atoll Agility Course | 255 | [`6538325`](https://runescape.wiki/?oldid=6538325), 2012-11-06 | `100558`, 2007-04-06 |
| Werewolf Agility Course | 134 | [`6288778`](https://runescape.wiki/?oldid=6288778), 2012-09-24 | `619287`, 2008-10-15 |
| Dorgesh-Kaan Agility Course | 118 | [`6547042`](https://runescape.wiki/?oldid=6547042), 2012-11-10 | `444758`, 2008-05-25 |
| Penguin Agility Course | 23 | [`5988056`](https://runescape.wiki/?oldid=5988056), 2012-07-25 | `1893326`, 2009-11-08 |
| Brimhaven Agility Arena | 387 | [`6556177`](https://runescape.wiki/?oldid=6556177), 2012-11-15 | `24532`, 2006-09-17 |

I separately read **all 188 revisions** of the eight pre-cutoff talk pages that exist. `Talk:Burthorpe Agility Course`, `Talk:Dorgesh-Kaan Agility Course`, and `Talk:Penguin Agility Course` did not exist before the cutoff. The dependency search read all 87 revisions of [`Template:Agility courses` oldid `6164175`](https://runescape.wiki/?oldid=6164175), [`Calculator:Agility` oldid `5669907`](https://runescape.wiki/?oldid=5669907), [`Calculator:Template/Agility` oldid `5965582`](https://runescape.wiki/?oldid=5965582), and [`Calculator talk:Agility` oldid `5591478`](https://runescape.wiki/?oldid=5591478). None contains a failure formula. No other pre-cutoff `Template:`, `Calculator:`, or `Module:` title with an Agility prefix existed; modern similarly named templates/modules resolve only to post-cutoff creations.

Search terms included `fail`, `failure rate`, `chance`, `success`, `probability`, `formula`, `percent`, `%`, ratios, and level/failure co-occurrences. This recovered removed statements that are absent from the final pinned pages, but **no revision states a level-to-success expression, random-roll ceiling, or complete pair of interpolation endpoints**.

### Removed quantitative observations recovered from page history

These are period leads, not shippable curves:

- **Agility Pyramid (Tier 2 historical wiki, unusable as a curve).** [`oldid 391182` (2008-04-02)](https://runescape.wiki/?oldid=391182) listed approximate fail rates by obstacle: rolling blocks `10–15%`, low walls `5%`, moving blocks timing-dependent, ledges `20%`, planks `25%`, cross/climb gaps `30–40%`, and jump gaps `40%`. The page states no player Agility level. Its own talk page later asked what level those rates represented and said a sliding scale was missing; level-68 and level-69 players reported respectively zero failures in an hour and two failures in 20 minutes ([`Talk:Agility Pyramid` oldid `6452823`](https://runescape.wiki/?oldid=6452823), preserving an April 2008 discussion). Those percentages therefore cannot supply a curve or a fixed implementation constant.
- **Brimhaven Arena (Tier 2 historical wiki, unusable as a level curve).** [`oldid 4129788` (2011-04-10)](https://runescape.wiki/?oldid=4129788) printed: low wall `5%` fail; rope swing `60%` success; log balance `10%` fail; ledge `10%`; pillars `50%`; monkey bars `20%`; rope balance `55%`; spiked floor `80%`; pressure pads `60%`; hand-holds `70%`; spinning blades `70%`; darts `80%`. It gives no level anchor for any percentage except the obstacle requirements and says the spiked-floor value depends on Agility level. The final pinned page removed several numbers or reduced them to qualitative labels. Talk-page testing at level `76` observed **34 failures in 100 spinning-blade attempts at both 85 kg and 0 kg**, which rejects weight as an input and materially conflicts with an unconditional `70%` fail constant ([`Talk:Brimhaven Agility Arena` oldid `5190243`](https://runescape.wiki/?oldid=5190243)). The same talk revision contains unresolved anecdotes over whether Agility level changes Arena failure. These are useful measurements, not an exact roll.
- **Advanced Gnome signpost (Tier 2 talk observation only).** A player reported approximately `40–50%` failure at level `85` after the 2009 high-level-course update ([`Talk:Agility` oldid `5439133`](https://runescape.wiki/?oldid=5439133), originally added in [`oldid 1646188`](https://runescape.wiki/?oldid=1646188)); the pinned course page proves zero failure at level `89` ([`oldid 6391497`](https://runescape.wiki/?oldid=6391497)). This bounds two points observationally but supplies neither the intervening shape nor the roll ceiling. Assuming linearity would invent both.
- **Werewolf deathslide contradiction.** The pinned page characterises failure as rare around level `72` and impossible from `93` ([`oldid 6288778`](https://runescape.wiki/?oldid=6288778)), but its talk page records `4/6` failures at level `74` and 0 kg ([`oldid 5608966`](https://runescape.wiki/?oldid=5608966); an earlier version said `3/5` in [`oldid 2408286`](https://runescape.wiki/?oldid=2408286)). The sample is small, but the contradiction is too large to silently treat “rare” as a numeric endpoint.
- **Dorgesh-Kaan contradiction.** The pinned course page says the fail rate decreases with Agility but never reaches zero ([`oldid 6547042`](https://runescape.wiki/?oldid=6547042)). A talk-page player claimed they stopped failing around level `84` ([`Talk:Agility` oldid `5439133`](https://runescape.wiki/?oldid=5439133)). The article and anecdote conflict; neither gives a formula.

### Course-by-course result after avenue 1

| Course/activity | Deep-history result for the curve |
|---|---|
| Gnome Stronghold normal | Not applicable: settled as unfailable. |
| Gnome advanced | `source_blocked`; one level-85 observation (`~40–50%` fail) and the settled level-89 zero point, but no function/ceiling. |
| Barbarian normal + advanced | `source_blocked`; every page/talk revision gives only the mastery point, including a briefly disputed `92` versus corrected `93`, never a curve. |
| Wilderness | `source_blocked`; all 250 revisions discuss consequences and the `26.6%` LP damage roll, not obstacle success probability. |
| Burthorpe | `source_blocked`; all 38 revisions contain no quantitative chance. |
| Agility Pyramid | `source_blocked`; removed approximate obstacle percentages have no Agility level and are explicitly challenged by the talk page. |
| Ape Atoll | `source_blocked`; all 255 revisions prove only `100%` success from level `75`. |
| Werewolf | `source_blocked`; no formula and a material page/talk contradiction at levels `72–74`. |
| Dorgesh-Kaan | `source_blocked`; no formula and a page/talk contradiction over whether failure reaches zero. |
| Penguin | `source_blocked`; all 23 revisions contain no quantitative chance. |
| Brimhaven | `source_blocked`; removed percentages lack level anchors and conflict with a controlled level-76 observation. |

## Avenue 2 — OSRS gate, formula, and contamination checks

### The OSRS roll expression, and a hidden post-2013 contamination

OSRS uses two integer endpoints, `low` at level 1 and `high` at level 99, and a random integer with **256 outcomes (`0..255`)**. Before a global engine change in November–December 2023, its exact expression was:

```text
c_old(L) = floor(low * (99 - L) / 98)
         + floor(high * (L - 1) / 98)
         + 1

P(success at L) = clamp(c_old(L), 0, 256) / 256
P(fail at L)    = 1 - P(success at L)
```

The literal pre-change implementation is preserved in [`Module:Skilling success chart` oldid `14480493` (2023-10-17)](https://oldschool.runescape.wiki/?oldid=14480493). OSRS then changed the **engine-level `stat_random` function** between 2023-11-01 and 2023-12-12 so that it no longer decreases at certain levels. The current expression instead rounds the two terms after adding them:

```text
c_new(L) = floor(low * (99 - L) / 98
               + high * (L - 1) / 98
               + 0.5)
         + 1
```

The change window and current expression are explicit in [`Skilling success rate` oldid `15208182`](https://oldschool.runescape.wiki/?oldid=15208182) and [`Module:Skilling success chart` oldid `15084668`](https://oldschool.runescape.wiki/?oldid=15084668). This is a real post-2013 formula contamination that does **not** appear on individual course histories. Consequently, no current OSRS chart can be used unchanged for a 2007-derived value. A row passes only when both its old endpoint constants and `c_old` can be recovered.

### Exact current OSRS leads (before gating)

All endpoint pairs below use the 256-outcome expression above. “Jagex” means the obstacle page labels the data `jagex=yes` or directly cites a Jagex developer; it does not by itself close either date gap.

| Course | Failable obstacle | `low`, `high` | OSRS revision / provenance |
|---|---|---:|---|
| Barbarian normal | Rope swing | `200, 280` | Jagex-labelled chart, [`oldid 15232854`](https://oldschool.runescape.wiki/?oldid=15232854) |
| Barbarian normal | Log balance | `180, 260` | Jagex-labelled chart, [`oldid 15232855`](https://oldschool.runescape.wiki/?oldid=15232855) |
| Barbarian normal | Balancing ledge | `200, 280` | Jagex-labelled chart, [`oldid 15232856`](https://oldschool.runescape.wiki/?oldid=15232856) |
| Wilderness | Rope swing | `200, 250` | Mod Ash supplied level-1/99 endpoints, [`oldid 15219008`](https://oldschool.runescape.wiki/?oldid=15219008) |
| Wilderness | Third stepping stone | `180, 250` | same Jagex statement, [`oldid 15210051`](https://oldschool.runescape.wiki/?oldid=15210051) |
| Wilderness | Log balance | `200, 250` | same Jagex statement, [`oldid 15232857`](https://oldschool.runescape.wiki/?oldid=15232857) |
| Agility Pyramid | Rolling/tilting stone block | `168, 320` | Jagex-labelled chart, [`oldid 15232864`](https://oldschool.runescape.wiki/?oldid=15232864) |
| Agility Pyramid | Low wall | `245, 255` | Jagex-labelled chart, [`oldid 15232863`](https://oldschool.runescape.wiki/?oldid=15232863) |
| Agility Pyramid | Ledge | `181, 320` | Jagex-labelled chart, [`oldid 15232862`](https://oldschool.runescape.wiki/?oldid=15232862) |
| Agility Pyramid | Plank | `166, 340` | Jagex-labelled chart, [`oldid 15232839`](https://oldschool.runescape.wiki/?oldid=15232839) |
| Agility Pyramid | Cross gap | `180, 308` | Jagex-labelled chart, [`oldid 15232861`](https://oldschool.runescape.wiki/?oldid=15232861) |
| Agility Pyramid | Jump gap | `185, 329` | same revision as cross gap |
| Penguin | Failable platform/stepping-stone check(s) | `155, 308` | Mod Ash supplied `61%–121%` level-1/99 endpoints on 2022-04-26; [`oldid 15201377`](https://oldschool.runescape.wiki/?oldid=15201377) |
| Penguin | Icicles / `Tread-softly` check | `155, 308` | same dated Jagex statement; [`oldid 15201378`](https://oldschool.runescape.wiki/?oldid=15201378) |
| Brimhaven (post-rework) | Spinning blades | `153, 255` | community sample, not Jagex; [`oldid 15201364`](https://oldschool.runescape.wiki/?oldid=15201364) |
| Brimhaven (post-rework) | Darts | `131, 255` | community sample, not Jagex; [`oldid 15232832`](https://oldschool.runescape.wiki/?oldid=15232832) |

Current OSRS has no expression/endpoints for Ape Atoll, Werewolf deathslide, Dorgesh-Kaan cables/ladders, Penguin crushers or ice slope, the Pyramid moving block, or the other Brimhaven obstacles. Those pages either have no success section or are explicitly categorised `Needs skilling success chart`.

### Both update-history gates, course by course

The RuneScape-side gate uses each current RuneScape Wiki course page's curated `Update history`, plus the skill-wide history in [`Agility` oldid `37030075`](https://runescape.wiki/?oldid=37030075). The OSRS-side gate uses the current course `Changes` section and the global 2023 `stat_random` change above. “Pass” means no recorded obstacle/fail-rate/difficulty/XP divergence relevant to the hidden roll; visual, sound, and interface-only patches are listed but do not masquerade as balance changes.

| Course | RuneScape 2007 → 2012 gate | OSRS 2013 → present gate | Verdict |
|---|---|---|---|
| Gnome normal | **Pass for failure**: 2009–2012 entries are model, sound, render, and environment changes; normal course remained unfailable ([RS `oldid 36940652`](https://runescape.wiki/?oldid=36940652)). | 2024 increased XP/hour and added marks ([OSRS `oldid 15239935`](https://oldschool.runescape.wiki/?oldid=15239935)); no failure formula is needed. | n/a, unfailable. |
| Gnome advanced | **Fail as an OSRS bridge**: the advanced fork was added on 2009-06-22, after the 2007 OSRS backup ([period page `oldid 6391497`](https://runescape.wiki/?oldid=6391497)). | No OSRS version to audit. | `source_blocked`. |
| Barbarian normal | **Pass for the normal fail roll**: 2009–2012 course entries concern the later advanced fork, visuals, pathing, and a skill-guide requirement, not the normal obstacle chances ([RS `oldid 36940456`](https://runescape.wiki/?oldid=36940456)). | **Pass for the quoted roll.** The 2016-02-18 rope-swing change enlarged only the click zone; the 2024-05-08 change added Strength XP and marks. Neither is a failure rebalance ([OSRS `oldid 15239937`](https://oldschool.runescape.wiki/?oldid=15239937)). The Jagex-labelled endpoint pages post-date those changes, but the course history contains no post-2013 fail-rate change to contaminate them; applying the recovered pre-2023 `c_old` also reproduces the independently settled level-93 mastery point. | **Tier 3 usable** for the three normal obstacles. |
| Barbarian advanced | **Fail as an OSRS bridge**: added in 2009, after the backup; its course was also streamlined on 2009-11-09 ([RS `oldid 36940456`](https://runescape.wiki/?oldid=36940456)). | No OSRS version. | `source_blocked`. |
| Wilderness | **Pass for the quoted roll.** From 2007 through the cutoff the history records stone alignment (2008-08-05), adding the visible end to the log (2010-05-13), and a gate examine update (2012-01-31), but no fail-rate rebalance. RS3 did not amend the fail rates and make level 99 infallible until 2016-08-15, after the target ([RS `oldid 37025989`](https://runescape.wiki/?oldid=37025989)). | **Pass for the quoted roll.** The 2016-02-18 change enlarged the rope click zone; the April 2024 work added an optional dispenser, rewards, combat-state changes, and a streak. The update record states no obstacle fail-rate change ([OSRS `oldid 15247615`](https://oldschool.runescape.wiki/?oldid=15247615)). | **Tier 3 usable** for the three main-course obstacles. |
| Burthorpe | **No 2007 bridge**: the course itself was added on 2012-01-31 ([RS `oldid 36940651`](https://runescape.wiki/?oldid=36940651)). | Absent from the 2007 OSRS base. | `source_blocked`. |
| Agility Pyramid | **Fail**: Jagex “improved the code behind” the course on 2009-10-20, an unbounded mechanics change, and the OSRS endpoints are numerically incompatible with the recovered 2008 fail-rate observations (arithmetic below) ([RS `oldid 37047173`](https://runescape.wiki/?oldid=37047173)). | **Pass in isolation for the quoted roll.** The 2016-02-11 change altered lap XP and pyramid-top value, not obstacle failure; later entries are click-box/animation changes ([OSRS `oldid 15221341`](https://oldschool.runescape.wiki/?oldid=15221341)). That cannot cure the failed 2007→2012 gate. | All six current pairs disqualified; moving block still has none; `source_blocked`. |
| Ape Atoll | **Pass for the fail roll**: 2009–2012 entries are animation, blocking, sound, and displayed-bonus fixes; no fail-rate rebalance is recorded ([RS `oldid 37010378`](https://runescape.wiki/?oldid=37010378)). | **Fail**: on 2024-05-15 OSRS made the stepping stone and second tree unfailable ([OSRS `oldid 15256499`](https://oldschool.runescape.wiki/?oldid=15256499)). Pre-change [`oldid 304871`](https://oldschool.runescape.wiki/?oldid=304871) gives only the level-75 cutoff. | `source_blocked`. |
| Werewolf | **Fail**: Jagex rewrote course code/fixed a stepping-stone bug on 2009-11-09 and fixed a location that was not checking Agility on 2009-12-08 ([RS `oldid 37004943`](https://runescape.wiki/?oldid=37004943)). | **Fail**: stick XP doubled on 2018-07-12 and a route skip was removed on 2019-01-17 ([OSRS `oldid 15239940`](https://oldschool.runescape.wiki/?oldid=15239940)). Pre-change [`oldid 6331620`](https://oldschool.runescape.wiki/?oldid=6331620) is qualitative only. | `source_blocked`. |
| Dorgesh-Kaan | **Fail**: the 2009-07-21 skill-guide entry explicitly refers to “recent changes” to the course, and Surefooted failure prevention was fixed on 2011-07-26 ([RS `oldid 37001484`](https://runescape.wiki/?oldid=37001484)). | **Fail under the literal course-change gate**: marks were added on 2024-05-08 ([OSRS `oldid 15239941`](https://oldschool.runescape.wiki/?oldid=15239941)); pre-change [`oldid 14555439`](https://oldschool.runescape.wiki/?oldid=14555439) has no curve. | `source_blocked`. |
| Penguin | **Pass**: the only 2007–2012 course update was a 2009-07-08 fix allowing under-level players to exit; it did not change obstacle chances, difficulty, or XP ([RS `oldid 36940203`](https://runescape.wiki/?oldid=36940203)). | **Pass after recovery**: the course has no OSRS `Changes` section. The global 2023 interpolation change is real, but both endpoints were disclosed by Jagex on 2022-04-26 and `c_old` is preserved in `oldid 14480493`. | **Tier 3 usable** for stepping stones and icicles only. |
| Brimhaven | **Fail**: Jagex “rewrote a fair amount of the logic” on 2009-11-17 ([RS `oldid 37010381`](https://runescape.wiki/?oldid=37010381)). | **Fail**: OSRS made obstacles unfailable at 99 on 2017-02-23, then standardised tier fail rates on 2024-05-08 ([OSRS `oldid 15262280`](https://oldschool.runescape.wiki/?oldid=15262280)). The oldest pre-change page recovered, [`oldid 156066`](https://oldschool.runescape.wiki/?oldid=156066), is qualitative only. | Post-rework sample pairs disqualified; all rows `source_blocked`. |

### Tier 3 values that survive both gates

For the normal Barbarian course, use `c_old` with the obstacle endpoints in the lead table. The rope swing and balancing ledge use `(200, 280)`; the log balance uses `(180, 260)`. At level `93`, the log—the last of the three to reach certainty—gives

```text
c_log(93) = floor(180 * 6 / 98) + floor(260 * 92 / 98) + 1
          = 11 + 244 + 1
          = 256
```

so the Tier 3 formula independently reproduces the Tier 2 statement that a flawless normal lap is guaranteed from `93`. At level `92`, it gives `254/256 = 99.21875%` success, also preserving a non-zero failure chance immediately below mastery. [`Ropeswing oldid 15232854`](https://oldschool.runescape.wiki/?oldid=15232854); [`log oldid 15232855`](https://oldschool.runescape.wiki/?oldid=15232855); [`ledge oldid 15232856`](https://oldschool.runescape.wiki/?oldid=15232856); Tier 3.

For the Wilderness main course, rope swing and log balance use `(200, 250)`; the third stepping stone uses `(180, 250)`. At the period course gate `L=52`, `c_old` gives success `226/256 = 88.28125%` on rope/log and `217/256 = 84.765625%` on the stepping stones. At `L=99`, all three give `251/256 = 98.046875%`, retaining a `5/256 = 1.953125%` failure chance. That agrees with the later RS3 history's implication that level-99 failure existed until its 2016-08-15 change. [`Rope oldid 15219008`](https://oldschool.runescape.wiki/?oldid=15219008); [`stones oldid 15210051`](https://oldschool.runescape.wiki/?oldid=15210051); [`log oldid 15232857`](https://oldschool.runescape.wiki/?oldid=15232857); Tier 3.

For the Penguin course's failable stepping-stone/platform check(s) after the explicitly safe first jump, and for each `Tread-softly` icicle check, use the recovered pre-2023 OSRS expression with `low=155`, `high=308`:

```text
c_penguin(L) = floor(155 * (99 - L) / 98)
             + floor(308 * (L - 1) / 98)
             + 1

P_fail(L) = 1 - clamp(c_penguin(L), 0, 256) / 256
```

At the course requirement `L=30`, `c=201`, so `P_fail=55/256=21.484375%`. At `L=65`, `c=255`, so one outcome in 256 still fails. At `L=66`, `c=257`, clamped to `256`, so failure is exactly zero. The modern icicles prose says level 65 is guaranteed because the post-2023 `c_new` reaches 256 one level earlier; the stepping-stone page still says 66. That internal modern inconsistency is precisely why the pre-change expression, not the rendered modern chart, is cited here.

No OSRS formula survives both gates for the other course obstacles.

### Stop-rule contradiction: OSRS Pyramid endpoints versus the settled 2008 observations

This contradiction disqualifies the Pyramid endpoints but does not halt the remaining hunt avenues. Every Pyramid obstacle requires level `30`, and each OSRS success curve rises with level, so its level-30 failure chance is the **maximum** it can produce for an eligible player. Using the recovered pre-2023 `c_old` rather than the contaminated modern rounding gives:

| Pyramid obstacle | OSRS `c_old(30)` | Maximum eligible OSRS fail chance | Settled 2008 pre-EOC observation, player level unstated | Result |
|---|---:|---:|---:|---|
| Rolling block | `213/256` success | `43/256 = 16.796875%` [`oldid 15232864`](https://oldschool.runescape.wiki/?oldid=15232864) | approximately `10–15%` [`RS oldid 391182`](https://runescape.wiki/?oldid=391182) | Slightly outside the approximate band. |
| Low wall | `248/256` success | `8/256 = 3.125%` [`oldid 15232863`](https://oldschool.runescape.wiki/?oldid=15232863) | `5%` [`RS oldid 391182`](https://runescape.wiki/?oldid=391182) | OSRS maximum is lower. |
| Ledge | `222/256` success | `34/256 = 13.28125%` [`oldid 15232862`](https://oldschool.runescape.wiki/?oldid=15232862) | `20%` [`RS oldid 391182`](https://runescape.wiki/?oldid=391182) | OSRS maximum is lower. |
| Plank | `217/256` success | `39/256 = 15.234375%` [`oldid 15232839`](https://oldschool.runescape.wiki/?oldid=15232839) | `25%` [`RS oldid 391182`](https://runescape.wiki/?oldid=391182) | OSRS maximum is lower. |
| Cross gap | `218/256` success | `38/256 = 14.84375%` [`oldid 15232861`](https://oldschool.runescape.wiki/?oldid=15232861) | approximately `30–40%` [`RS oldid 391182`](https://runescape.wiki/?oldid=391182) | Mutually incompatible if the observation measures this roll. |
| Jump gap | `228/256` success | `28/256 = 10.9375%` [`oldid 15232861`](https://oldschool.runescape.wiki/?oldid=15232861) | `40%` [`RS oldid 391182`](https://runescape.wiki/?oldid=391182) | Mutually incompatible if the observation measures this roll. |

The unknown 2008 player level cannot reconcile the rows: raising it above `30` only lowers every OSRS failure chance. The period figures are approximate observations rather than source code, but Tier 2 outranks Tier 3, and the `2009-10-20` main-line “improved the code” entry is a plausible divergence point. Per the audit's conflict rule, the OSRS Pyramid endpoints remain disqualified; later emulator results are recorded with their own standing rather than silently used to choose a side.

## Avenue 3 — Other pre-EOC emulators

### Disk check and repository set

The required local check covered `~/Downloads` and `~/Documents`. No 2009scape, Kronos, Apollo, Luna, Elvarg, RuneSource, 2006scape, or 2007scape source checkout was present. The one relevant local tree was a downloaded 2011Scape source snapshot at `~/Downloads/game-main`; its Barbarian plugin still says `TO-DO: Add Fail changes` at lines 10–14 and contains no roll. Public repositories were therefore read without cloning. Every source link below is pinned to a commit.

### 2009scape: an implemented curve, but an emulator invention that conflicts with period evidence

The official 2009scape GitLab is mirrored at [`downthecrop/2009scape-mirror`](https://github.com/downthecrop/2009scape-mirror). At commit [`65725314a2c75122d30e5d32b788af950e8ec5a4`](https://github.com/downthecrop/2009scape-mirror/tree/65725314a2c75122d30e5d32b788af950e8ec5a4), its shared handler implements a real expression ([`AgilityHandler.java`, lines 23–40](https://github.com/downthecrop/2009scape-mirror/blob/65725314a2c75122d30e5d32b788af950e8ec5a4/Server/src/main/content/global/skill/agility/AgilityHandler.java#L23-L40)):

```text
d = player_agility - obstacle_parameter_r
if d > 69: fail = false
otherwise:
    a = 0.01 * (1 + d)
    fail iff a * U <= b * V
    where U,V are independent Uniform[0,1) draws
```

The parameter named `failChance` in the source is `b`; it is **not** the resulting failure probability. Integrating the two random draws gives the exact curve:

```text
P_fail(L; r,b) = 0                                      if L-r > 69
                = b / (2a)                              if b <= a
                = 1 - a / (2b)                          if b > a
where a = 0.01 * (1 + L-r).
```

This is continuous-double RNG, not a roll against 255, and it has no RuneScape/Jagex citation in the code or history. The handler's surviving file history begins with a 2023 repository reorganisation; its older lineage is visible in Arios. The same lines appear verbatim in [`arios530/Arios-530` at `f004fb70...`, lines 23–37](https://github.com/arios530/Arios-530/blob/f004fb70be59987334a0e6770bb167b6fb339dc3/Arios-Server/src/org/arios/game/content/skill/member/agility/AgilityHandler.java#L23-L37) and the Arios derivative [`Rhiel/inferno-ps-game-server`, lines 22–37](https://github.com/Rhiel/inferno-ps-game-server/blob/2e849272312dc757a9637f7019933621a4d54816/src/org/arios/game/content/skill/member/agility/AgilityHandler.java#L22-L37). This is one copied lineage, **not three independent emulators agreeing**.

2009scape supplies these parameters:

| Course / obstacle | `r`, `b` in emulator | Consequence of the shared curve |
|---|---:|---|
| Barbarian rope / log / ledge | `1,.10` / `1,.50` / `1,.30` | Source calls at [`BarbarianOutpostCourse.kt` lines 87–110 and 151–163](https://github.com/downthecrop/2009scape-mirror/blob/65725314a2c75122d30e5d32b788af950e8ec5a4/Server/src/main/content/global/skill/agility/BarbarianOutpostCourse.kt#L87-L110). All become infallible at level 71, contradicting the sourced level-93 mastery point. At the real course requirement, level 35, the formula yields `14.29%`, `65%`, and `42.86%` respectively. |
| Wilderness entrance / rope / stepping stones / log | `1,.30` / `1,.10` / `1,.30` / `1,.50` | Calls at [`WildernessCourse.kt` lines 63–78, 147–171, and 195–209](https://github.com/downthecrop/2009scape-mirror/blob/65725314a2c75122d30e5d32b788af950e8ec5a4/Server/src/main/content/global/skill/agility/WildernessCourse.kt#L63-L78). Again, every check is forced to zero at level 71. |
| Pyramid low wall, ledge, plank, cross gap, jump gap | `10,.009` | One shared parameter for all five, with an explicit level-75 bypass ([`AgilityPyramidCourse.java` lines 206–247, 289–352, 488–505](https://github.com/downthecrop/2009scape-mirror/blob/65725314a2c75122d30e5d32b788af950e8ec5a4/Server/src/main/content/global/skill/agility/pyramid/AgilityPyramidCourse.java#L488-L505)). It therefore cannot reproduce Avenue 1's distinct approximate `5%`, `20%`, `25%`, `30–40%`, and `40%` obstacle rates at any one level. |
| Pyramid rolling block | `2,.30` | Separate call at [`RollingBlock.java` lines 26–36](https://github.com/downthecrop/2009scape-mirror/blob/65725314a2c75122d30e5d32b788af950e8ec5a4/Server/src/main/content/global/skill/agility/pyramid/RollingBlock.java#L26-L36); it is forced to zero from level 72, unlike the other Pyramid checks' explicit 75. |
| Brimhaven rope / low wall / rope balance / log | `1,.10` / `1,.05` / `1,.10` / `1,.10` | [`BrimhavenCourse.java` lines 33–71 and 157–178](https://github.com/downthecrop/2009scape-mirror/blob/65725314a2c75122d30e5d32b788af950e8ec5a4/Server/src/main/content/global/skill/agility/brimhaven/BrimhavenCourse.java#L33-L71). |
| Brimhaven handholds / monkey bars / ledge / pillars | all `1,.15` | [`BrimhavenCourse.java` lines 99–154, 181–252, and 288–319](https://github.com/downthecrop/2009scape-mirror/blob/65725314a2c75122d30e5d32b788af950e8ec5a4/Server/src/main/content/global/skill/agility/brimhaven/BrimhavenCourse.java#L99-L154). |
| Brimhaven floor spikes / pressure pads | both `20,.25` | [`FloorSpikes.java` lines 35–47](https://github.com/downthecrop/2009scape-mirror/blob/65725314a2c75122d30e5d32b788af950e8ec5a4/Server/src/main/content/global/skill/agility/brimhaven/FloorSpikes.java#L35-L47) and [`PressurePad.java` lines 35–47](https://github.com/downthecrop/2009scape-mirror/blob/65725314a2c75122d30e5d32b788af950e8ec5a4/Server/src/main/content/global/skill/agility/brimhaven/PressurePad.java#L35-L47). |
| Brimhaven spinning blades / darts | both `40,.15` | [`SpinningBlades.java` lines 35–47](https://github.com/downthecrop/2009scape-mirror/blob/65725314a2c75122d30e5d32b788af950e8ec5a4/Server/src/main/content/global/skill/agility/brimhaven/SpinningBlades.java#L35-L47) and [`DartTrap.java` lines 40–55](https://github.com/downthecrop/2009scape-mirror/blob/65725314a2c75122d30e5d32b788af950e8ec5a4/Server/src/main/content/global/skill/agility/brimhaven/DartTrap.java#L40-L55). At level 76, `a=.37`, so spinning blades predict `.15/(2*.37)=20.27%`, materially below Avenue 1's controlled `34/100`. |

There is no Gnome advanced, Ape Atoll, Werewolf, Dorgesh-Kaan, or Penguin course implementation in this tree. The ordinary Gnome course has no failure roll.

**Verdict:** the expression is a valuable emulator lead and the most complete implementation found, but it is not a tiered source value. Its copied lineage, lack of provenance, non-255 RNG shape, inconsistent mastery levels, and direct Brimhaven/Pyramid conflicts make every one of its parameters `source_blocked` for shipping.

### Bounded search of other emulator families

| Project | Pinned search and result |
|---|---|
| Arios 530 and Inferno | Exact shared handler shown above. These are ancestors/derivatives of the 2009scape implementation, not independent corroboration. |
| Kronos | [`TristanRSPS/KronosRSPS` at `e0b92878...`](https://github.com/TristanRSPS/KronosRSPS/tree/e0b92878dad313586f17110f96cccfd9199b8933): full recursive tree search and reads of `BarbarianCourse.java`, `GnomeStrongholdCourse.java`, and `WildernessCourse.java`; obstacle movement and XP only, no fail/chance/random call. |
| Apollo | [`apollo-rsps/apollo` at `87553a83...`](https://github.com/apollo-rsps/apollo/tree/87553a83840503815ce9d0a1dd39a28855d3b561): recursive tree contains no Agility course implementation. |
| Luna | [`luna-rs/luna` at `78bec8cf...`](https://github.com/luna-rs/luna/tree/78bec8cfb0e5c78011be0c0bdb3f7d4dc29d63c2): read the Agility core plus complete Gnome, Barbarian, and Wilderness scripts. The actions always complete; there is no failure branch ([Barbarian script](https://github.com/luna-rs/luna/blob/78bec8cfb0e5c78011be0c0bdb3f7d4dc29d63c2/src/main/kotlin/game/game/skill/agility/course/barbarian_outpost.kts), [Wilderness script](https://github.com/luna-rs/luna/blob/78bec8cfb0e5c78011be0c0bdb3f7d4dc29d63c2/src/main/kotlin/game/game/skill/agility/course/wilderness_course.kts)). |
| 2006Scape | [`2006-Scape/2006Scape` at `7f1dc47c...`](https://github.com/2006-Scape/2006Scape/tree/7f1dc47c982fcb20aace35e23d37c238422460ab): read every file under `content/skills/agility`, including Ape Atoll, Barbarian, Gnome, Pyramid, Werewolf, and Wilderness. No obstacle fail/chance roll exists; the sole random call chooses Brimhaven's next ticket pillar ([`Agility.java` lines 662–694](https://github.com/2006-Scape/2006Scape/blob/7f1dc47c982fcb20aace35e23d37c238422460ab/2006Scape%20Server/src/main/java/com/rs2/game/content/skills/agility/Agility.java#L662-L694)). |
| Elvarg and RuneSource | Recursive pinned-tree searches of [`RSPSApp/elvarg-rsps` at `478e6567...`](https://github.com/RSPSApp/elvarg-rsps/tree/478e6567aa533ae9f1d1bbf4971027b818c76a9a) and [`dozmus/runesource` at `6233edaa...`](https://github.com/dozmus/runesource/tree/6233edaa1a52b4f47640d0bccbc078af03354baf) found no Agility course source. |
| 2011Scape | Local downloaded snapshot: the Barbarian plugin's lines 10–14 explicitly say `TO-DO: Add Fail changes`; no failure roll exists. The public repository search found installers, client/web/wiki projects, and an empty `Freq-R/2011scape-Game`, not a second server implementation. |
| 633/Lletya completeness lead | [`CSS-Lletya/633-official` at `1b54cb99...`](https://github.com/CSS-Lletya/633-official/tree/1b54cb99edc9a940ce1bce07bec1c079ac8ac079): recursive read of `skills/skills/agility` finds course movement but no chance calculation. |

No independent emulator agrees with 2009scape's curve or parameters, and none supplies a second formula.

## Avenue 4 — RS3 fallback

### RS3's roll and its 2018 contamination

The current RuneScape Wiki describes the same `stat_random` mechanic family: integer `low` and `high` values represent levels 1 and 99, intermediate levels are interpolated, and the result is compared with an integer random roll. Its [`Skilling success chance` oldid `37009675`](https://runescape.wiki/?oldid=37009675) records a **3 September 2018 global rewrite** that allowed levels above 99 and “effectively” shifted chances. The current [`Module:Skilling success chart` oldid `36863307`](https://runescape.wiki/?oldid=36863307) uses two floored interpolation terms and a `2,550,001`-outcome scaled roll. Today's rendered RS3 chart is therefore contaminated for the 2012 cutoff.

The pre-rewrite expression is nevertheless recoverable from the OSRS pre-2023 implementation in Avenue 2 and independently present in the local 2011Scape snapshot's generic `interpolate` helper (`game/plugins/src/main/kotlin/gg/rsmod/plugins/api/ext/MiscExt.kt:51-57`; its bounded roll is at lines 43-49, and the pickpocket caller supplies ceiling `255` at `PickpocketTarget.kt:539-551`):

```text
c_pre2018(L) = floor(low * (99-L) / 98)
             + floor(high * (L-1) / 98)
             + 1
P_success    = clamp(c_pre2018, 0, 256) / 256
P_fail       = 1 - P_success
```

RS3 can therefore supply Tier 4 **endpoints** only where the course's post-cutoff update history contains no failure rebalance. The expression comes from the recovered older engine family, not from silently applying today's RS3 formula.

### Course results

| Course | Current RS3 endpoint evidence | RS3 post-2012 contamination check | Tier 4 verdict |
|---|---|---|---|
| Gnome advanced signpost | `low=-1780`, `high=496`, Jagex-labelled chart ([`oldid 36847895`](https://runescape.wiki/?oldid=36847895)) | No course-history fail rebalance, but the endpoints fail a stronger period observation: `c_pre2018(85)=171`, hence `P_fail=85/256=33.203125%`, outside the recovered roughly `40–50%` at level 85. They do reach zero by 89. | Disqualified by Tier 2 contradiction; `source_blocked`. |
| Barbarian normal | RS3 repeats OSRS's `200/280`, `180/260`, `200/280` ([rope `oldid 36847906`](https://runescape.wiki/?oldid=36847906), [log `oldid 36847904`](https://runescape.wiki/?oldid=36847904), [ledge `oldid 36847903`](https://runescape.wiki/?oldid=36847903)). | The only post-cutoff balance entry is 2016 XP, not failure. | Corroborates the higher-priority Tier 3 OSRS result; no Tier 4 substitution needed. |
| Barbarian advanced | Only the balance beam has a new chart, `-1635/400` ([`oldid 37068611`](https://runescape.wiki/?oldid=37068611)); the shared log retains the normal `180/260` pair. | No recorded post-cutoff failure rebalance. | The balance-beam row is a usable Tier 4 lead (`43/256` fail at 90, `1/256` at 92, zero at 93), and the shared log is covered by Tier 3. The period page says “several” advanced obstacles fail without enumerating the rest, so the **complete advanced-course set** remains `source_blocked`. |
| Wilderness main | Current RS3 uses `200/255` for rope/log and `180/255` for stones ([rope `oldid 36872685`](https://runescape.wiki/?oldid=36872685), [stones `oldid 36872686`](https://runescape.wiki/?oldid=36872686), [log `oldid 36872687`](https://runescape.wiki/?oldid=36872687)), reflecting the 2016 change that made level 99 infallible. | **Contaminated:** 2016-08-15 amended fail rates. | Cannot replace Tier 3 OSRS `high=250`; access-walkway endpoints remain absent. |
| Burthorpe log beam and low wall | Both have `low=153`, `high=1263`, Jagex-labelled charts ([`oldid 36872294`](https://runescape.wiki/?oldid=36872294), [`oldid 36872295`](https://runescape.wiki/?oldid=36872295)). The pages also state failure is disabled after three completed laps. | Course history after its 2012 release records only animation/environment changes, no failure rebalance. | **Tier 4 usable.** Both failable obstacles use `c_pre2018(L;153,1263)` against 256, subject to the sourced three-lap bypass. |
| Agility Pyramid | Current normal endpoints match the OSRS leads: stone `168/320`, wall `245/255`, ledge `181/320`, plank `166/340`, cross gap `180/308`, jump gap `185/329` ([stone `oldid 36847883`](https://runescape.wiki/?oldid=36847883), [wall `37056065`](https://runescape.wiki/?oldid=37056065), [ledge `36847885`](https://runescape.wiki/?oldid=36847885), [plank `36847919`](https://runescape.wiki/?oldid=36847919), [gaps `36847886`](https://runescape.wiki/?oldid=36847886)). Moving-block endpoints are absent. | **Contaminated:** 2016-03-14 reduced every obstacle's failure rate. The same constants also conflict with the 2008 measurements as shown in Avenue 2. | `source_blocked`. |
| Ape Atoll | Current Jagex-labelled charts are stepping stone `100/325`; rope, skull, monkeybars, and trees `120/325` ([oldids `36855411`–`36855415`](https://runescape.wiki/?oldid=36855411)). | **Contaminated:** 2016-03-14 reduced course failure rates. | `source_blocked`; no pre-change endpoints recovered. |
| Werewolf | No endpoint chart or exact multi-variable expression was found. The live page adds Strength and carried weight to Agility, and only gives a modern guaranteed-success condition. | 2019 added skillcape failure prevention; no numerical course rebalance is recorded, but there is no formula to preserve. | `source_blocked`: expression and all endpoints missing. |
| Dorgesh-Kaan | Fallen ladder alone has `low=-319`, `high=360` ([`oldid 36847897`](https://runescape.wiki/?oldid=36847897)); cable pages have no chart ([`oldid 35928240`](https://runescape.wiki/?oldid=35928240)). | No post-cutoff numerical rebalance is recorded, but the partial current chart cannot cover the period page's cables-and-ladders failures. Worse, `high=360` forces the ladder chance to zero at high level, contradicting the settled period statement that course failure never reaches zero. | `source_blocked`: stronger period evidence disqualifies the ladder pair, and cable endpoints are missing. |
| Penguin | Current RS3 has stepping stones/icicles `180/308` and ice slope `140/366`; crusher has no chart ([stones `oldid 36856199`](https://runescape.wiki/?oldid=36856199), [icicles `36856198`](https://runescape.wiki/?oldid=36856198), [ice `36856197`](https://runescape.wiki/?oldid=36856197)). | **Contaminated:** 2016-03-14 “greatly reduced” course failure rates. | Cannot fill the Tier 3 OSRS gaps; `source_blocked` for crusher and ice slope. |
| Brimhaven Arena | All twelve random obstacles have Jagex-labelled endpoints; full table below. | **Pass:** after the cutoff the course history changes interfaces, click areas, rewards, and item handling, but records no fail-rate change. The 2009 main-line logic rewrite is already incorporated because RS3 is the continuing branch. | **Tier 4 usable for all random obstacles.** |

### Brimhaven Tier 4 endpoint set

Every row uses `c_pre2018` above and a 256-outcome ceiling. The wrong plank and sawblade remain timing/choice mechanics and do not use this random roll.

| Random obstacle | `low`, `high` | Pinned RS3 revision |
|---|---:|---|
| Rope swing | `100,310` | [`oldid 36858429`](https://runescape.wiki/?oldid=36858429) |
| Low wall | `220,460` | [`oldid 36858443`](https://runescape.wiki/?oldid=36858443) |
| Log balance | `180,420` | [`oldid 36858444`](https://runescape.wiki/?oldid=36858444) |
| Balancing ledge | `140,370` | [`oldid 36858453`](https://runescape.wiki/?oldid=36858453) |
| Pillars | `120,340` | [`oldid 36858441`](https://runescape.wiki/?oldid=36858441) |
| Monkey bars | `160,400` | [`oldid 36858440`](https://runescape.wiki/?oldid=36858440) |
| Balancing rope | `200,440` | [`oldid 36858451`](https://runescape.wiki/?oldid=36858451) |
| Floor spikes | `60,250` | [`oldid 36858447`](https://runescape.wiki/?oldid=36858447) |
| Pressure pads | `40,230` | [`oldid 36858432`](https://runescape.wiki/?oldid=36858432) |
| Hand holds | `80,280` | [`oldid 36858446`](https://runescape.wiki/?oldid=36858446) |
| Spinning blades | `30,210` | [`oldid 36858445`](https://runescape.wiki/?oldid=36858445) |
| Darts | `20,190` | [`oldid 36858456`](https://runescape.wiki/?oldid=36858456) |

The strongest validation is independent of the modern chart. For spinning blades at the Avenue 1 measurement level `L=76`:

```text
c(76) = floor(30 * 23 / 98) + floor(210 * 75 / 98) + 1
      = 7 + 160 + 1
      = 168
P_fail = (256 - 168) / 256 = 88/256 = 34.375%
```

That is effectively exact agreement with the period controlled result `34 failures / 100 attempts`. It also sharply falsifies 2009scape's `20.27%` prediction. Brimhaven therefore has a complete zero-invention Tier 4 failure model despite failing the OSRS 2007→2012 bridge: the main-line RS3 endpoints include the 2009 rewrite, the post-2012 history is clean, the pre-2018 roll is recovered, and a period experiment independently corroborates the result.

## Avenue 5 — OpenRS2 cache completeness check

A bounded revision-`742` (`2012-11-07`) name/option query through `tools/query_openrs2_cache_definitions.sh` returned every already-tabulated failable obstacle group and no new obstacle, so no period obstacle is missing from the tables. The cache corroborates client identity and options only and supplies no roll, endpoint, XP value, or timer; it changes no failure row.

## Per-obstacle result table

Define the recovered period expression once:

```text
F(L; low, high) = 1 - clamp(
    floor(low * (99-L) / 98)
  + floor(high * (L-1) / 98)
  + 1,
  0, 256) / 256
```

`F` is the failure probability; the roll has 256 outcomes (`0..255`). “Blocked” means at least one expression parameter is absent or disqualified—not that failure behavior itself is unknown.

| Course / failable obstacle | Result | Tier and gate disposition |
|---|---|---|
| Gnome advanced — signpost | `source_blocked`: RS3 `-1780/496` predicts `33.203125%` failure at 85, contradicting the period `40–50%` observation ([`oldid 36847895`](https://runescape.wiki/?oldid=36847895)). | RS3 Tier 4 lead rejected; no OSRS course. |
| Barbarian normal — rope swing | `F(L;200,280)` ([`oldid 15232854`](https://oldschool.runescape.wiki/?oldid=15232854)) | **Tier 3.** RS 2007→2012 pass; OSRS course-rate pass; global 2023 formula contamination recovered. |
| Barbarian normal — log balance | `F(L;180,260)` ([`oldid 15232855`](https://oldschool.runescape.wiki/?oldid=15232855)) | **Tier 3**, same gates; this row reaches certainty at the sourced level 93. |
| Barbarian normal — balancing ledge | `F(L;200,280)` ([`oldid 15232856`](https://oldschool.runescape.wiki/?oldid=15232856)) | **Tier 3**, same gates. |
| Barbarian advanced — shared log balance | `F(L;180,260)` from the shared normal-course obstacle; it retains `2/256` failure at 92 and reaches zero at 93. | **Tier 3** for this identified row; both normal-course roll gates passed. |
| Barbarian advanced — balance beam | `F(L;-1635,400)` ([`oldid 37068611`](https://runescape.wiki/?oldid=37068611)); `43/256` fail at 90, `1/256` at 92, zero at 93. | **Tier 4 lead** with clean RS3 post-cutoff history. |
| Barbarian advanced — other “several” failable obstacles | `source_blocked`: the period page does not enumerate the full failable set and no other endpoint charts exist. | OSRS bridge fails because the advanced course was added in 2009; partial rows cannot complete the course. |
| Wilderness access walkway | `source_blocked`: no endpoints and no mastery point. | No OSRS/RS3 chart; emulator value has no provenance. |
| Wilderness main — rope swing | `F(L;200,250)` ([`oldid 15219008`](https://oldschool.runescape.wiki/?oldid=15219008)) | **Tier 3.** RS roll gate pass; OSRS course-rate pass; global formula recovered. |
| Wilderness main — third stepping stone | `F(L;180,250)` ([`oldid 15210051`](https://oldschool.runescape.wiki/?oldid=15210051)) | **Tier 3**, same gates. |
| Wilderness main — log balance | `F(L;200,250)` ([`oldid 15232857`](https://oldschool.runescape.wiki/?oldid=15232857)) | **Tier 3**, same gates. |
| Burthorpe — log beam | `F(L;153,1263)`, bypassed after three completed laps ([`oldid 36872294`](https://runescape.wiki/?oldid=36872294)) | **Tier 4.** No OSRS bridge (course added 2012); RS3 post-cutoff rate history passes. |
| Burthorpe — obstacle low wall | `F(L;153,1263)`, same three-lap bypass ([`oldid 36872295`](https://runescape.wiki/?oldid=36872295)) | **Tier 4**, same gates. |
| Pyramid — rolling blocks | `source_blocked`: OSRS/RS3 `168/320` is disqualified by the 2009 code change and period observation conflict. | Tier 3/4 leads rejected. |
| Pyramid — low walls | `source_blocked`: `245/255` disqualified by the same gates/conflict. | Tier 3/4 leads rejected. |
| Pyramid — moving blocks | `source_blocked`: no endpoint pair in any source. | No formula lead. |
| Pyramid — cross ledges | `source_blocked`: `181/320` disqualified. | Tier 3/4 leads rejected. |
| Pyramid — planks | `source_blocked`: `166/340` disqualified. | Tier 3/4 leads rejected. |
| Pyramid — cross gaps | `source_blocked`: `180/308` disqualified. | Tier 3/4 leads rejected. |
| Pyramid — jump gaps | `source_blocked`: `185/329` disqualified. | Tier 3/4 leads rejected. |
| Ape Atoll — final climb-down tree | `source_blocked`: period cutoff is known, but endpoint pair is not. | RS 2007→2012 pass; OSRS post-2013 failure change fails; RS3 2016 rate change contaminates `120/325`. |
| Werewolf — deathslide | `source_blocked`: exact Agility/Strength/weight expression and endpoints absent. | Both branch leads lack a recoverable curve. |
| Dorgesh-Kaan — cables | `source_blocked`: endpoint pairs absent. | RS history fails; OSRS absent; RS3 incomplete. |
| Dorgesh-Kaan — ladders | `source_blocked`: one modern `-319/360` ladder lead does not cover the period behavior. | Partial Tier 4 lead rejected. |
| Penguin — ice crushers | `source_blocked`: no endpoint pair. | OSRS and RS3 both lack a period-valid pair. |
| Penguin — platform/stepping-stone rolls after the safe first jump | `F(L;155,308)` ([`oldid 15201377`](https://oldschool.runescape.wiki/?oldid=15201377)) | **Tier 3.** RS 2007→2012 pass; OSRS course pass; global formula recovered. |
| Penguin — four icicle rolls | `F(L;155,308)` each ([`oldid 15201378`](https://oldschool.runescape.wiki/?oldid=15201378)) | **Tier 3**, same gates. |
| Penguin — ice slope (except safe final step) | `source_blocked`: no period-valid endpoint pair. | RS3 `140/366` is contaminated by the 2016 rate reduction. |
| Brimhaven — rope swing | `F(L;100,310)` | **Tier 4**, [`Avenue 4 endpoint source`](#brimhaven-tier-4-endpoint-set); RS3 post-cutoff pass. |
| Brimhaven — low wall | `F(L;220,460)` | **Tier 4**, same gate/source. |
| Brimhaven — log balance | `F(L;180,420)` | **Tier 4**, same gate/source. |
| Brimhaven — balancing ledge | `F(L;140,370)` | **Tier 4**, same gate/source. |
| Brimhaven — pillars | `F(L;120,340)` | **Tier 4**, same gate/source. |
| Brimhaven — monkey bars | `F(L;160,400)` | **Tier 4**, same gate/source. |
| Brimhaven — balancing rope | `F(L;200,440)` | **Tier 4**, same gate/source. |
| Brimhaven — floor spikes | `F(L;60,250)` | **Tier 4**, same gate/source. |
| Brimhaven — pressure pads | `F(L;40,230)` | **Tier 4**, same gate/source. |
| Brimhaven — hand holds | `F(L;80,280)` | **Tier 4**, same gate/source. |
| Brimhaven — spinning blades | `F(L;30,210)`; predicts `34.375%` failure at level 76 versus observed `34/100`. | **Tier 4**, independently period-corroborated. |
| Brimhaven — darts | `F(L;20,190)` | **Tier 4**, same gate/source. |

## Synthesis: can Agility ship with zero invented constants?

### Direct answer, per course

**Yes for some routes, no for the complete ten-course set.** Use `F(L;low,high)` from the per-obstacle table with a 256-outcome ceiling for every shippable random roll.

| Course | Zero-invention verdict | Exact parameters, tier, and both branch gates |
|---|---|---|
| Gnome Stronghold | Normal route: **SHIPPABLE** because it has no failable obstacle. Advanced route: **SOURCE_BLOCKED**. | Signpost endpoint pair missing; RS3 `-1780/496` is contradicted by the level-85 period observation. RS 2007→2012 OSRS-licensing gate fails because advanced was added in 2009; OSRS post-2013 gate is n/a. |
| Barbarian Outpost | Normal route: **SHIPPABLE**. Advanced route: **SOURCE_BLOCKED**. | Normal rope/ledge `200/280`, log `180/260`, `F`, ceiling 256, Tier 3. RS 2007→2012 gate **passes** for the normal roll; OSRS post-2013 rate gate **passes**, and global 2023 formula contamination is recovered. Advanced lacks the complete failable set/endpoints. |
| Wilderness | Main loop: **SHIPPABLE**. Access walkway: **SOURCE_BLOCKED**; therefore the whole location is not complete. | Main rope/log `200/250`, third stone `180/250`, `F`, ceiling 256, Tier 3. RS 2007→2012 roll gate **passes**; OSRS post-2013 rate gate **passes**, global formula recovered. Walkway endpoints and mastery behavior are missing. |
| Burthorpe | **SHIPPABLE.** | Log beam and low wall both `153/1263`, `F`, ceiling 256, plus the sourced bypass after three completed laps; Tier 4. RS 2007→2012 OSRS bridge **does not exist** because the course was added in 2012; OSRS post-2013 gate n/a. RS3 post-cutoff failure-rate gate **passes**. |
| Agility Pyramid | **SOURCE_BLOCKED.** | Moving-block endpoints are missing; every other OSRS/RS3 pair is disqualified by the 2009 main-line code change, the RS3 2016 failure rebalance, and conflict with the 2008 observations. |
| Ape Atoll | **SOURCE_BLOCKED.** | Final-tree endpoints are missing. RS 2007→2012 gate **passes**, but OSRS post-2013 gate **fails** on the 2024 failure change; RS3 `120/325` is contaminated by the 2016 rate reduction. |
| Werewolf | **SOURCE_BLOCKED.** | The multi-variable Agility/Strength/weight expression and endpoints are missing. Both branch searches lack a recoverable period curve. |
| Dorgesh-Kaan | **SOURCE_BLOCKED.** | Cable and ladder endpoints are missing/disqualified; period behavior never reaches zero, while the lone modern ladder pair does. |
| Penguin | Platform jumps and icicles: **SHIPPABLE**; crushers and ice slope: **SOURCE_BLOCKED**, so the full course is incomplete. | Platforms/icicles `155/308`, `F`, ceiling 256, Tier 3. RS 2007→2012 gate **passes**; OSRS post-2013 course gate **passes**, global formula recovered. Crusher pair absent; RS3 slope pair contaminated by 2016. |
| Brimhaven Arena | **SHIPPABLE** for every random obstacle. | Tier 4, `F`, ceiling 256; pairs are rope `100/310`, wall `220/460`, log `180/420`, ledge `140/370`, pillars `120/340`, monkey bars `160/400`, rope balance `200/440`, spikes `60/250`, pads `40/230`, hand holds `80/280`, blades `30/210`, darts `20/190`. RS 2007→2012 OSRS-licensing gate **fails** because of the 2009 logic rewrite, and OSRS post-2013 gate **fails** due its 2017/2024 changes; RS3 main-line post-cutoff rate gate **passes**, so Tier 4 is licensed instead. |

### Does the 2011Scape/OSRS architectural agreement hold?

**Yes.** 2011Scape's generic helper (`MiscExt.kt:51-57`) implements the same two-floored-terms-plus-one interpolation as the recovered pre-2023 OSRS `stat_random`. Its pickpocket target code (`PickpocketTarget.kt:539-551`) supplies level endpoints `1` and `99` and a `255` cap; the helper at `MiscExt.kt:43-49` compares the interpolated integer to `nextInt(cap)`. OSRS uses the same endpoint interpretation and interpolation but a literal `0..255` roll, i.e. 256 outcomes. The off-by-one ceiling/comparator details are not identical, but the architecture is unmistakably the same mechanic family. This is strong evidence that the OSRS endpoint pairs describe the kind of hidden roll the 2012 game ran; it does **not** waive either course-history gate for a particular pair.

### RS main-line 2007→2012 gate, one line per course

| Course | OSRS-licensing gate result |
|---|---|
| Gnome | Normal **pass**; advanced **fail/no bridge** because it was added in 2009. |
| Barbarian | Normal **pass**; advanced **fail/no bridge** because it was added and streamlined in 2009. |
| Wilderness | Main quoted roll **pass**; 2008–2012 history has no fail-rate rebalance. |
| Burthorpe | **Fail/no bridge**; course added 2012, after the OSRS backup. |
| Pyramid | **Fail**; 2009-10-20 “improved the code behind” the course. |
| Ape Atoll | **Pass**; no 2007–2012 failure-rate rebalance recorded. |
| Werewolf | **Fail**; 2009 code rewrite and missing Agility-check fix. |
| Dorgesh-Kaan | **Fail**; 2009 “recent changes” and 2011 Surefooted failure fix. |
| Penguin | **Pass**; only an under-level exit fix appears in the interval. |
| Brimhaven | **Fail**; 2009-11-17 rewrote “a fair amount” of course logic. |

### The proposed global clumsiness constant

The owner's fallback is:

```text
p_fail(L) = C * (M-L) / (M-R)    for R <= L < M
p_fail(L) = 0                     for L >= M
```

where `R` is the sourced course requirement, `M` the sourced mastery cutoff, and `C` one global failure probability at `R`.

| Blocked course/component | Constraint on `C` | Arithmetic and limitation |
|---|---:|---|
| Gnome advanced | **`40% <= C <= 50%`** | `R=85`, `M=89`, and the observation is at `L=85`; therefore `p(85)=C*(89-85)/(89-85)=C≈40–50%`. This is the tightest valid numeric interval. |
| Barbarian advanced | **`0% < C <= 100%`** | With `R=90`, `M=93`, the explicit rare failure at 92 gives `p(92)=C/3>0`, but “rare” has no numeric magnitude. The course is blocked independently because its failable set/endpoints are not enumerated. |
| Wilderness access walkway | **`0% <= C <= 100%`**, but unusable | No mastery cutoff or quantitative observation exists, so no value narrows `C`, and the fallback cannot be instantiated without inventing `M`. |
| Agility Pyramid | **`40% <= C <= 100%`; conditionally `∅` if the table rates share one player level.** | At any eligible level, linear decay implies `p(L)<=C`, so the largest reported rate (`40%` jump gap) requires `C>=40%`. One global course curve would give the same probability to every obstacle at the same level, while the 2008 rows report about `5%`, `10–15%`, `20%`, `25%`, `30–40%`, and `40%`; those cannot all equal one `p(L)`. Because the source does not state the measurement level(s) or `M`, only the envelope bound is unconditional. |
| Ape Atoll | **`0% <= C <= 100%`** | `R=48`, `M=75`; the zero at 75 is built into the fallback for every `C` and supplies no start-rate bound. No intermediate quantitative observation survives. |
| Werewolf | **Strict feasible set `∅`.** | `R=60`, `M=93`, `L=74`. The older `3/5` anecdote requires `C=(3/5)*(93-60)/(93-74)=99/95=104.2105%`; the later `4/6` requires `C=(4/6)*33/19=22/19=115.7895%`. Both exceed the probability ceiling. They also conflict with the period description “rare around 72.” |
| Dorgesh-Kaan | **Strict feasible set `∅` for this fallback shape.** | The sourced behavior says failure remains possible even at 99 and never reaches zero. Any finite `M` forces zero, while `C=0` contradicts observed failure. No numeric constant can repair the missing/asymptotic shape. |
| Penguin crushers/ice slope | **`0% <= C <= 100%`**, but unusable | The complete-course mastery cutoff and quantitative observations are absent. The shippable platform/icicle pairs do not license inventing the missing groups' `M` or endpoints. |

Brimhaven is not a fallback constraint anymore: its actual Tier 4 curve supplies `34.375%` at level 76 and matches `34/100`. Translating that observation into `C` would require an unsourced mastery cutoff, so doing so would reintroduce the very invention this audit avoids.

**Global conclusion:** if every anecdotal point is demanded literally, the single-constant fallback's feasible set is **empty**, because Werewolf requires `C>100%` and Dorgesh-Kaan rejects any finite zero cutoff; Pyramid is also inconsistent if its listed rates share a measurement level. After explicitly excluding those mutually inconsistent/model-incompatible observations, the tightest surviving evidence-bound interval is **`C ∈ [40%,50%]`**, supplied entirely by Gnome advanced and weakly supported by the Pyramid envelope `C>=40%`.

The probability interval is the sourced deliverable; no rounding convention is sourced. If encoded using the recovered OSRS/RS3 `0..255` roll, it permits `103..128` failing outcomes out of 256 (an inclusive stored threshold of `102..127`). If encoded literally with 2011Scape's `nextInt(255)`/inclusive-comparison convention, it permits `102..127` failing outcomes out of 255 (stored threshold `101..126`). Choosing an integer within either representation would remain an owner balance decision.

## Remaining `source_blocked` rows and exhaustive search record

| Blocked row(s) | Avenue 1: pinned pre-EOC | Avenue 2: OSRS + both gates | Avenue 3: emulators | Avenue 4: RS3 | Avenue 5: cache | Exact missing piece |
|---|---|---|---|---|---|---|
| Gnome advanced signpost | Main revisions, talk revisions, skill article, templates/calculators: observation `40–50%` at 85 and zero at 89, no endpoints. | No OSRS advanced course because it post-dates the 2007 backup. | 2011Scape has no roll; 2009scape has no advanced Gnome implementation; other bounded projects add none. | `-1780/496` found but rejected because it predicts `33.203125%` at 85. | Confirms signpost `43581 [Run-across]` only. | A period-consistent `low/high` pair. |
| Barbarian advanced full set | Pinned page says “several” can fail, log can still fail at 92, all reach zero at 93; no enumeration or curve. | No OSRS advanced course; normal-course pairs cannot enumerate the advanced branch. | 2011Scape explicitly says `Add Fail changes`; 2009scape implements only the old normal route; Luna/Kronos do not add failures. | Shared log has `180/260`; balance beam lead `-1635/400`; remaining failable obstacles/endpoints unknown. | Confirms objects/options only. | Complete failable-obstacle enumeration and endpoint pair for each remaining roll. |
| Wilderness access walkway | Pinned course page proves it can fail and drop the player among wolves; no curve/cutoff. Main/talk/template search adds none. | No access-walkway success chart or historical pair; main-loop pairs do not cover it. | 2009scape has an unproven `r=1,b=.30` entrance invention and forces zero at 71; no independent agreement. | No endpoint chart. | Does not expose the server roll. | Walkway `low/high` endpoints; fallback also lacks `M`. |
| Pyramid rolling/wall/moving/ledge/plank/cross/jump | Pinned 2008 page supplies approximate per-obstacle observations but no levels, endpoints, ceiling, or mastery cutoff; full revision/talk/template search finds no formula. | Six modern pairs found, but the 2009 main-line code update fails the bridge and their maxima contradict the 2008 rows; moving blocks have no pair. | 2009scape uses one `.009` curve for five unlike obstacles plus a separate rolling-block curve; it conflicts with the observations and has no provenance. Other emulators have no roll. | 2016 reduced all failure rates; modern pairs are contaminated; moving block still absent. | Confirms object groups only. | Period-valid pair for every type, especially moving blocks; no sourced fallback `M`. |
| Ape Atoll final climb-down | Pinned revisions establish the final tree can fail and zero at 75; no curve. | RS gate passes, but OSRS 2024 changed which obstacles fail; pre-change page gives only the cutoff. | 2009scape lacks the course; 2006Scape has movement but no failure roll; no independent implementation. | Tree `120/325` exists only after the 2016 failure-rate reduction. | Confirms course objects only. | Pre-2016/pre-cutoff final-tree endpoints. |
| Werewolf deathslide | Main/talk history yields the level-74 `3/5` and `4/6` anecdotes, “rare around 72,” and zero at 93, but no Agility/Strength/weight formula. | 2009 main-line course rewrite fails the bridge; OSRS pre-change pages remain qualitative. | 2009scape lacks the course; 2006Scape has no failure roll; other bounded projects add none. | No success chart/expression; modern prose only adds conditional Strength/weight facts. | Confirms zip-line IDs/options only. | Full multi-input expression and parameters; the linear fallback is mathematically inconsistent with the anecdotes. |
| Dorgesh-Kaan cables/ladders | Pinned course/talk search says failures decrease but never reach zero; no curve. | 2009/2011 main-line changes fail the bridge; OSRS has no chance expression. | 2009scape and the other period emulators lack the course. | Cable has no chart; ladder `-319/360` forces zero and contradicts period evidence. | Confirms cable/ladder identities only. | Period-valid non-zero-at-99 expression and all cable/ladder parameters. |
| Penguin crushers and ice slope | Pinned revisions prove all four groups can fail, with first platform/final step safe; no formula for missing groups. | Platforms/icicles pass with `155/308`; no crusher/slope pair exists. | No 2009scape/2011Scape/other bounded emulator implementation supplies a roll. | Crusher has no pair; slope `140/366` is contaminated by the 2016 rate reduction. | Confirms crusher-entry, snow-jump, and ice objects only. | Period-valid crusher and ice-slope endpoint pairs. |

No unchecked avenue remains for these rows: pinned page/talk/history/template space, both OSRS history gates and pre-change revisions, the required emulator set, RS3 with its post-cutoff history, and the last pre-cutoff cache have all been recorded above.
