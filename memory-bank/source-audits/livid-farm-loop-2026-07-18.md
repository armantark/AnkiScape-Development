# Livid Farm review-native contract

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **owner-design loop closed; period cycle, cadence unit, distractions,
spell ladder, Borrowed Power, and wishes are implementation-ready except for
the explicitly source-blocked hidden rolls and effect magnitudes below.**

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

## Pacing decision

The full progression remains intentionally long. The owner confirmed that
Livid Farm's notorious slog is part of the activity's identity, so AnkiScape
does not add a catch-up multiplier, first-clear bonus, streak bonus, or
accelerated reward mode. At full output, the exact fresh-state path remains 538
emitted cycles and 449 successful reviews.

The mitigation is legibility rather than compression:

- every cycle grants its substantial source XP and Produce immediately;
- every spell threshold is visible before it is reached;
- progress and the next unlock remain visible;
- leaving and returning preserves points and cadence residual; and
- no source field, dialogue, or puzzle must be babysat.

## Automatic distractions

The three optional source distractions are folded into the emitted cycle. They
never become a separate review, dialogue question, or manual reaction:

| Distraction | Required spell | Level | Cost | Magic XP | Successful reward |
|---|---|---:|---|---:|---|
| Sick ibis | Monster Examine | 66 | 1 Astral, 1 Cosmic, 1 Mind | 61 | 10 Water, 1 Astral, 16 Earth, 1 Cosmic, 1 Mind |
| Suqah attack | Energy Transfer | 91 | 3 Astral, 2 Law, 1 Nature | 100 | 10 Water, 3 Astral, 16 Earth, 2 Law, 1 Nature |
| Murky Pat | Vengeance Other | 93 | 3 Astral, 10 Earth, 2 Death | 108 | 15 Water, 3 Astral, 20 Earth, 2 Death |

The source says each distraction is optional, grants no Produce points, and
refunds its cast runes plus bonus Earth and Water runes on success. A player
below the spell level may still complete it for the rune reward but receives
no Magic XP. The Suqah's half-special-bar cost does not create persistent
special depletion: the source explicitly says another cannot occur before the
bar naturally replenishes.

Period evidence does not expose the occurrence rate or relative weights.
Those hidden rolls remain `source_blocked`. If implementation must proceed
before stronger evidence appears, use one clearly labeled provisional global
calibration—one seeded distraction opportunity per twelve emitted cycles,
uniformly selecting among the three—rather than inventing three separate
tables. At most one distraction resolves in a cycle. It resolves only when its
complete rune cost is present; otherwise the distraction is skipped without
blocking or partially mutating the ordinary cycle. The result line includes
its exact XP and net rune delta. Undo restores the opportunity roll and every
delta.

## Spell ladder and claiming

Crossing a cumulative Produce threshold claims the corresponding spell
automatically. Pauline's source dialogue is presentation, not an AnkiScape
action, so claiming consumes no review. The first ten claims do not spend
Produce. Borrowed Power atomically deducts 850,000 points when claimed, and any
remainder becomes the first wish balance.

Each unlocked spell joins the ordinary Lunar-spell registry with its period
Magic, rune, XP, target, item, and equipment rules. The focused Livid contract
owns only its unlock:

- South Falador and North Ardougne Teleports become direct destination
  transitions;
- Repair Rune Pouch repairs an essence pouch and gives it five times the
  ordinary deterioration interval;
- Remote Farm reads the existing Farming patch state and may cure a diseased
  patch;
- Spiritualise Food consumes eligible food through the Summoning familiar
  heal/stat-boost contract;
- Make Leather tans up to five hides per cast through the ordinary inventory
  transaction;
- Teleport to Trollheim targets the herb-patch destination; and
- Disruption Shield, Vengeance Group, and Group Teleport to Trollheim remain
  fully registered source content but naturally have no usable consumer until
  PvP or multiplayer aid exists. They receive no permanent “future” lock or
  cleanup-only UI state.

Exact cast costs and effect magnitudes not stated by the pinned Livid Farm
revision remain owned by the individual spell audit. The activity must not
invent Livid-only versions of Farming, Summoning, tanning, teleport, PvP, or
essence-pouch behavior.

## Borrowed Power

`Borrowed Power`, oldid `6587752` (`2012-11-19T14:23:14Z`), closes the capstone:

- it is a level-99 Lunar spell costing three Astral runes per cast;
- it casts exactly one selected standard-spellbook spell through an equipped
  Arcane capacitor necklace;
- charging consumes 1,000 times that spell's normal rune cost and installs
  exactly 1,000 charges;
- one account may own only one capacitor and it may hold only one spell;
- each cast consumes three Astral runes and one charge, awards the borrowed
  spell's ordinary Magic XP, and cannot autocast;
- the necklace crumbles when the final charge is consumed or its charges are
  removed; and
- the supported list is Wind Wave, Water Wave, Earth Wave, Fire Wave, Magic
  Dart, Vulnerability, Enfeeble, Entangle, Telekinetic Grab, Teleport to House,
  High Alchemy, and Bones to Peaches.

The capacitor bypasses the standard-spellbook selection boundary, not the
borrowed action's target, quest, item, equipment, inventory, or encounter
requirements unless an individual period source proves otherwise. Charging or
replacing its binding is an atomic inventory command, not a review. An
insufficient 1,000-cast rune bundle changes nothing.

## Wishes

After Borrowed Power, Produce continues accumulating from ordinary cycles up
to the source maximum wallet of 850,000. Wishes are direct commands in the
Livid Farm reward surface: a valid purchase atomically spends points and
applies its output without consuming a review or any runes.

| Wish | Cost | AnkiScape behavior |
|---|---:|---|
| Vial My Herbs | 5,500 | Convert every clean herb in carried inventory, noted or not, into its unfinished potion, capped at 50 of each herb. Cave nightshade is excluded. |
| Turn Lunar Lumber Into Runes | 5,500 | Convert all carried Lunar lumber. A 28-lumber batch yields 25 Astral and 10 each Nature, Death, Earth, Cosmic, and Water runes. Partial batches use one deterministic residual so repeated small conversions equal the full-batch ratio rather than rounding free runes into existence. |
| Give me an Arcane Capacitor | 18,000 | Grant one uncharged capacitor. The one-owned rule rejects the purchase atomically while another exists. |
| I'd Like a New Patch! | 18,000 | Create the one-time allotment patch; it persists until its first clearing and then disappears. |
| More Planks Please | 18,000 | For the sourced 20-minute duration, Plank Make has about a 1-in-10 chance to add the source noted plank output; Lunar lumber is excluded. |
| Gimme Herbs | 18,000 | Grant noted 3 grimy kwuarm, 3 grimy irit, 2 grimy cadantine, 2 grimy avantoe, and 1 grimy lantadyme. |
| Let it rain seeds | 18,000 | Auto-collect the source watermelon, cactus, poison ivy, strawberry, curry-tree, and orange-tree seed shower through the ordinary inventory/Bank Claim overflow path. Exact quantities remain `source_blocked`. |
| Reduce The Fish I Burn | 18,000 | Apply the sourced 30-minute non-Daemonheim fish-burn reduction. Its exact magnitude remains `source_blocked`; do not substitute a modern rate. |
| Protect a Patch for me! | 37,000 | Grant the source scroll. Only one protection may be active; it protects ten trees of the selected ordinary or fruit-tree type. |
| Let it Rain Awesome Seeds | 55,000 | Auto-collect exactly 4 ranarr, 4 watermelon, 6 curry-tree, 2 pineapple, 2 papaya, and 4 willow seeds through the ordinary inventory/Bank Claim overflow path. |

The two sourced minute durations use the shared short-duration
answered-card clock, never the wall clock. They preserve the source 20:30
ratio, advance on every answered card including Again, participate in undo,
and affect only admitted eligible actions. They project through the shared
temporary-effect UI rather than creating Livid-specific HUD controls.

Ground-spawn clicking is not retained as a manual seed-pickup minigame. The
wish purchase already is the meaningful choice; automatic collection preserves
the sourced reward without introducing an inventory race against a timer.

## Explicitly unresolved

- distraction occurrence rate and relative weights: `source_blocked` hidden
  rolls, with the single provisional fallback above;
- the exact seed quantities for `Let it rain seeds`: `source_blocked`;
- the exact burn-chance magnitude for `Reduce The Fish I Burn`:
  `source_blocked`; and
- individual spell cast data not stated on the Livid page: owned by each
  spell's focused period audit, not guessed here.

These gaps do not reopen the activity's product design. They are bounded source
tasks for implementation.
