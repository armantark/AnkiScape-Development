# Slayer points and reward catalog reconnaissance — 2026-07-15

Status: **cutoff primary table pinned; cross-source value reconciliation open**.
Cutoff: `2012-11-20T00:00:00Z`.

## Primary period source

RuneScape Wiki, `Slayer points`, oldid `6520963`, timestamp
`2012-11-02T15:54:41Z`:
<https://runescape.wiki/w/Slayer_points?oldid=6520963>.

The historical wikitext was read through the MediaWiki revisions API. This is a
period primary table, not a current-page reconstruction; individual values still
need the corroboration required by `pre-eoc-source-verification-standard.md`.

## Point rules stated by the period page

- Smoking Kills unlocks Slayer reward points.
- The first four consecutive qualifying tasks award no points; points begin with
  the fifth.
- Every 10th qualifying task uses the master-specific tenth-task award and every
  50th uses the fiftieth-task award.
- Turael/Spria tasks award zero and do not advance the qualifying streak;
  replacing another master's task through them resets the streak to zero.
- Challenges count as assignments and may add their own bonus XP and points.
- The stated point cap is 64,011.

The page describes 10th and 50th rewards as 5x and 15x ordinary points, but its
Mazchna row gives `2 / 5 / 15`, which does not satisfy that formula. Darkan's
current `Master.java` independently contains the same `2 / 5 / 15` row, but
Darkan and its rev-727 base are not independent corroboration. Preserve the
conflict; do not normalize the row during implementation without resolving it.

## Cutoff reward catalog

### Repeatable purchases

| Reward | Cost |
|---|---:|
| 10,000 Slayer XP | 400 points |
| Ring of slaying (8 charges) | 75 points |
| 250 Magic Dart casts: 250 death runes and 1,000 mind runes | 35 points |
| 250 broad-tipped bolts | 35 points |
| 250 broad arrows | 35 points |

The XP purchase is a sourced direct reward. AnkiScape's established rule grants
XP for implemented skills immediately; it is not converted into invented review
work.

### Permanent learn/unlock purchases

| Unlock | Cost | Period requirement/effect lead |
|---|---:|---|
| Fletch broad arrows and broad-tipped bolts | 300 | 52/55 Fletching |
| Craft rings of slaying | 300 | 75 Crafting; assists allowed in source |
| Craft Slayer helmets | 400 | 55 Crafting; component and full-helmet chain |
| Allow Kuradal to assign aquanites | 50 | 78 Slayer to receive/kill |
| Deliver killing blows quicker | 400 | Automatic finisher with required item present |
| Attack ice strykewyrms without a fire cape | 2,000 | 93 Slayer; weaker than fire-cape route |

The 75-Slayer text for the quick-finisher reward was not enforced by the period
game according to the same source. Treat it as interface text, not a proven gate.

### Assignment operations

| Operation | Cost | Period effect |
|---|---:|---|
| Skip current assignment | 30 | Cancel without resetting the qualifying streak |
| Remove current assignment | 100 | Cancel and block it from future rolls |

The period page states one block slot per 50 quest points, up to six at 300 quest
points. Removing a block restores the task to rolls but refunds no points.

### Parked co-op purchases

The same cutoff table includes co-op food sharing, potion sharing, and two pets.
They are historically live but depend entirely on Social Slayer. Under Owner
decision 4 they remain in the completeness ledger and create no solo runtime,
UI, storage, or reward-shop rows.

## Open ring-of-slaying abstraction

The ring's eight charged teleports were a principal period benefit. Its task
check duplicates AnkiScape's persistent task display, while the global transport
network is deliberately excluded by `systemPatterns.md`. The ring already has a
source-backed Crafting recipe lead in the repository, so leaving all of its
runtime effects inert would create a dead permanent unlock and dead item chain.

A product decision is required before the reward catalog can close: either let a
charge remove an abstract Slayer-trip run-energy cost, or explicitly retain the
ring as a task-check/collection item with no teleport substitute.
