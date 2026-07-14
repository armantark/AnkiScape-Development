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

TODO

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
