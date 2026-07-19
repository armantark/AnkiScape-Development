# Livid Farm review-native contract

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **period cycle and cadence unit pinned; under-level duty policy grill
active.**

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

## Under-level duty fork

The entry level of 70 Magic can fully cast only Cure Plant. The remaining
duties become full-reward at Magic levels 80, 83, 86, and 91, but the source
still permits them beforehand for:

- their full secondary-skill XP;
- half their Produce points; and
- no Magic XP, while retaining the real rune cost.

The open owner decision is whether default automation performs every duty for
maximum Produce and secondary XP or skips reduced-reward duties to conserve
runes. This must be one standing policy, not five duty checkboxes or a
Casual/Advanced split.

