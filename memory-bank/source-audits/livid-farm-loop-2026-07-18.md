# Livid Farm review-native contract

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **period cycle, cadence unit, and under-level duty policy closed;
reward-ladder and wish design active.**

## Pinned period evidence

`Livid Farm`, oldid `6569596` (`2012-11-17T21:40:18Z`), establishes:

- entry after `Lunar Diplomacy`, with the Lunar spellbook active and unboosted
  levels 70 Magic, 60 Agility, 60 Crafting, 60 Farming, and 50 Construction;
- one-minute rounds in a fixed five-round cycle, with twelve complete cycles
  per source hour;
- three Cure Plant duties, three Fertile Soil duties, and two fence repairs in
  every round;
- Energy Transfer on rounds one, two, and four, and two String Jewellery
  bundles on rounds three and five;
- exact rune costs, Magic XP, secondary-skill XP, and Produce points for every
  duty;
- participation below a duty's Magic level with no Magic XP, half Produce
  points, and full Farming, Construction, Crafting, or Agility XP;
- optional Ibis, Suqah, and Murky Pat distractions that grant ordinary spell
  XP and refunded-plus-bonus runes but no Produce points;
- a cumulative spell-unlock ladder ending at 850,000 Produce points, followed
  by point-spending wishes; and
- no completion bonus for finishing every source round or cycle.

Source:

- <https://runescape.wiki/w/Livid_Farm?oldid=6569596>

The page's early recommendation says a five-round cycle uses 87 Astral runes,
43 Nature runes, and 6 Law runes, while its later full-cycle calculation and
the literal spell requirements total 97 Astral, 43 Nature, 6 Law, 535 Earth,
and 20 Water. The 87-Astral summary conflicts with the task table and remains
rejected unless an independent source explains the missing ten. The literal
per-duty spell rows own implementation.

### 850,000 versus the stale 880,000 calculation

The cutoff Livid Farm page's spell table, cap prose, reward transaction, and
trivia all set Borrowed Power at 850,000 Produce points. `Borrowed Power`, oldid
`6587752` (`2012-11-19T14:23:14Z`), independently says the spell costs 850,000.

The same Livid Farm revision nevertheless retains a later “557 cycles” estimate
and rune-cost formula based on 880,000 points. Revision `4657954`
(`2011-08-23T17:45:46Z`) shows why: Borrowed Power originally cost 880,000
points when that cycle calculation was written. The unlock was later reduced to
850,000, while the worked estimate was not updated.

AnkiScape therefore uses the cutoff 850,000 threshold and rejects the stale
880,000 calculation. At 1,580 points per full-reward cycle, the final unlock
requires 538 emitted cycles. From a fresh 6:5 residual, that is 449 successful
reviews. Any remainder above 850,000 survives the final deduction and becomes
the first wish balance.

Additional source:

- <https://runescape.wiki/w/Borrowed_Power?oldid=6587752>
- <https://runescape.wiki/w/Livid_Farm?oldid=4657954>

## Exact five-round cycle

One complete cycle contains:

| Duty | Count | Produce points at full Magic | Magic XP each | Secondary XP each |
|---|---:|---:|---:|---:|
| Cure Plant | 15 | 20 | 60 | 91.8 Farming |
| Fertile Soil | 15 | 20 | 87 | 91.8 Farming |
| Plank Make / repair fence | 10 | 20 | 90 | 54.6 Construction |
| String Jewellery / deposit bundle | 4 | 120 | 83 | 270 Crafting |
| Energy Transfer / encourage Pauline | 3 | 100 | 100 | 169.7 Agility |

At Magic 91 or above, one full cycle therefore grants exactly:

- 1,580 Produce points;
- 3,737 Magic XP;
- 2,754 Farming XP;
- 546 Construction XP;
- 1,080 Crafting XP; and
- 509.1 Agility XP.

The cycle consumes the literal combined spell cost of 97 Astral, 43 Nature, 6
Law, 535 Earth, and 20 Water runes before staff or tome substitution. Rune
substitution must use the ordinary Magic equipment contract rather than a
Livid-Farm-only infinite-rune exception.

## Cadence unit

The five-round cycle is one declared `activity_group`. AnkiScape does not
simulate plot positions, diseased-plant pictures, encouragement dialogue,
individual clicks, or the sixty-second reset.

The source gives twelve complete cycles per hour. AnkiScape's world cadence
gives ten answered cards per source hour, so the live rate is exactly:

```text
12 cycles / 10 reviews = 6 cycles / 5 successful reviews
```

The cadence residual therefore admits six whole cycles for every five
successful Livid Farm reviews. Most reviews resolve one cycle; the residual
review resolves two. The result line always reports the emitted cycle count and
the exact aggregate rune, Produce-point, and XP deltas so the double emission
never looks like an unexplained bonus.

`Again` is a cadence wait: it emits no cycle, consumes no runes, and grants no
points or XP. It advances only the ordinary answered-card world systems and
does not inflate any activity-failure statistic.

At multiplier `M`, advance `M` cadence steps while preserving the exact 6:5
residual. Stop before a cycle whose complete rune cost cannot be paid. Never
partially consume a cycle or silently omit one of its admitted duties.

One undo restores the full review batch: cadence residual, runes, Produce
points, all five skills' XP, spell unlocks, wish eligibility, and any terminal
resource pause.

The cycle grouping is an explicit AnkiScape abstraction. Its source rate and
contents are exact, while its one-line atomic presentation deliberately removes
the repetitive field interface.

## Under-level duty policy

The entry level of 70 Magic can fully cast only Cure Plant. The remaining
duties become full-reward at Magic levels 80, 83, 86, and 91, but the source
still permits them beforehand for:

- their full secondary-skill XP;
- half their Produce points; and
- no Magic XP, while retaining the real rune cost.

One standing **Farm routine** policy applies in both UI modes:

1. **Complete every duty** (default)
2. **Conserve runes — full-reward duties only**

The default preserves the source's basic strategy and the identity of helping
with the complete farm routine. At Magic 70, a cycle still performs all five
duty families, grants 940 Produce points, grants Magic XP only for the fifteen
Cure Plant casts, and grants every exact secondary-skill reward. Each later
duty threshold automatically changes its own Magic XP and Produce payout to
the full row.

The conserve-runes policy omits only duties whose spell level exceeds the
player's current effective Magic level. It never earns their secondary XP or
points. Current temporary Magic boosts count exactly as they do for ordinary
spell eligibility; entry's unboosted requirements remain unchanged.

If the selected policy cannot pay its complete next-cycle rune cost, the
activity pauses and lists the missing runes. It does not silently switch policy,
partially execute a cycle, buy runes, or pull them from the Bank.

This is one descriptive dropdown, not five duty checkboxes and not a
Casual/Advanced split.

## Authentic full-reward milestone projection

The exact cumulative thresholds remain:

| Unlock | Produce threshold | Earliest successful review |
|---|---:|---:|
| South Falador Teleport | 69,840 | 38 |
| Repair Rune Pouch | 139,760 | 75 |
| North Ardougne Teleport | 227,120 | 120 |
| Remote Farm | 314,480 | 167 |
| Spiritualise Food | 401,840 | 213 |
| Make Leather | 489,200 | 259 |
| Disruption Shield | 576,560 | 305 |
| Vengeance Group | 663,920 | 351 |
| Teleport to Trollheim | 744,400 | 394 |
| Group Teleport to Trollheim | 806,400 | 426 |
| Borrowed Power | 850,000 | 449 |

These projections assume the full 1,580-point routine from Magic 91 onward and
a fresh cadence residual. Reduced-reward cycles take longer; temporary Magic
boosts or a pre-existing residual may shift the exact review on which a
threshold is crossed. The runtime owns the actual cumulative point balance, not
this explanatory projection.
