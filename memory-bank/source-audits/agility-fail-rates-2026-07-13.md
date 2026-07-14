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

This contradiction halts the audit before the independent-emulator avenue. Every Pyramid obstacle requires level `30`, and each OSRS success curve rises with level, so its level-30 failure chance is the **maximum** it can produce for an eligible player. Using the recovered pre-2023 `c_old` rather than the contaminated modern rounding gives:

| Pyramid obstacle | OSRS `c_old(30)` | Maximum eligible OSRS fail chance | Settled 2008 pre-EOC observation, player level unstated | Result |
|---|---:|---:|---:|---|
| Rolling block | `213/256` success | `43/256 = 16.796875%` [`oldid 15232864`](https://oldschool.runescape.wiki/?oldid=15232864) | approximately `10–15%` [`RS oldid 391182`](https://runescape.wiki/?oldid=391182) | Slightly outside the approximate band. |
| Low wall | `248/256` success | `8/256 = 3.125%` [`oldid 15232863`](https://oldschool.runescape.wiki/?oldid=15232863) | `5%` [`RS oldid 391182`](https://runescape.wiki/?oldid=391182) | OSRS maximum is lower. |
| Ledge | `222/256` success | `34/256 = 13.28125%` [`oldid 15232862`](https://oldschool.runescape.wiki/?oldid=15232862) | `20%` [`RS oldid 391182`](https://runescape.wiki/?oldid=391182) | OSRS maximum is lower. |
| Plank | `217/256` success | `39/256 = 15.234375%` [`oldid 15232839`](https://oldschool.runescape.wiki/?oldid=15232839) | `25%` [`RS oldid 391182`](https://runescape.wiki/?oldid=391182) | OSRS maximum is lower. |
| Cross gap | `218/256` success | `38/256 = 14.84375%` [`oldid 15232861`](https://oldschool.runescape.wiki/?oldid=15232861) | approximately `30–40%` [`RS oldid 391182`](https://runescape.wiki/?oldid=391182) | Mutually incompatible if the observation measures this roll. |
| Jump gap | `228/256` success | `28/256 = 10.9375%` [`oldid 15232861`](https://oldschool.runescape.wiki/?oldid=15232861) | `40%` [`RS oldid 391182`](https://runescape.wiki/?oldid=391182) | Mutually incompatible if the observation measures this roll. |

The unknown 2008 player level cannot reconcile the rows: raising it above `30` only lowers every OSRS failure chance. The period figures are approximate observations rather than source code, but Tier 2 outranks Tier 3, and the `2009-10-20` main-line “improved the code” entry is a plausible divergence point. Per the audit's stop rule, the OSRS Pyramid endpoints remain disqualified and no emulator result should be used to choose a side without owner acknowledgement of this conflict.

## Avenue 3 — Other pre-EOC emulators

TODO

## Avenue 4 — RS3 fallback

TODO

## Avenue 5 — OpenRS2 cache completeness check

TODO

## Per-obstacle result table

TODO

## Synthesis: can Agility ship with zero invented constants?

TODO

## Remaining `source_blocked` rows and exhaustive search record

TODO
