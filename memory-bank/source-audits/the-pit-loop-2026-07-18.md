# The Pit Invitation and Review Loop

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **eligible-course set pinned; invitation automation owner-settled;
challenge budget remains a labeled abstraction.**

## Pinned period evidence

`The Pit` oldid `6551042` (`2012-11-13T04:44:38Z`) establishes:

- a completed lap on an eligible Agility course has a chance to attract the
  Talent Scout even if obstacles were failed;
- the exact recruiting courses are Gnome Stronghold basic and advanced,
  Agility Pyramid, Barbarian Outpost basic and advanced, Ape Atoll,
  Wilderness, Werewolf, and Dorgesh-Kaan;
- the invitation is lost if the player does not speak to the Scout within
  roughly one source minute;
- one of six challenges is chosen at random;
- success pays course-and-challenge-scaled Agility XP and the first success
  awards a gorilla mask;
- failure still pays reduced course-and-challenge-scaled Agility XP;
- ordinary success may be gambled at equal `2x/1x/0.5x` odds; and
- an Agility/Max/Completionist cape permits reduced-XP practice without the
  gamble.

`Talent scout` oldid `6448152` (`2012-10-21T02:21:10Z`) says broadly that the
Scout appears at any course except Burthorpe and requires free hands and no
familiar for entry. The focused Pit page's explicit recruiting list is the
course-set authority. Penguin is absent from that list, and independent
period-lineage spawn data contains Talent Scouts at several courses in the
focused list but no Penguin-course Scout. Therefore neither Burthorpe nor
Penguin can generate ordinary invitations.

Sources:

- <https://runescape.wiki/w/The_Pit?oldid=6551042>
- <https://runescape.wiki/w/Talent_scout?oldid=6448152>
- 2011Scape rev-667 spawn files:
  `spawns_9781.plugin.kts`, `spawns_10039.plugin.kts`,
  `spawns_11050.plugin.kts`, and `spawns_13356.plugin.kts`.

## Exact invitation coverage

The live course-target mapping is:

| Eligible | Ineligible |
|---|---|
| `gnome_normal` | `burthorpe_course` |
| `gnome_advanced` | `penguin_course` |
| `barbarian_normal` | Brimhaven Arena and other non-lap Activities |
| `barbarian_advanced` | Bandos's Throne Room and other incidental courses not named by the focused source |
| `agility_pyramid` | Shortcuts and non-course Agility actions |
| `ape_atoll` | |
| `wilderness_course` | |
| `werewolf_course` | |
| `dorgesh_kaan` | |

This is nine eligible live course variants out of the eleven ordinary lap
course targets, so the practical answer is **yes, most courses**, but not all.

## One global checkbox

Use one Agility-wide setting:

**Automatically accept Talent Scout invitations** — default **checked**.

The same checkbox appears and behaves identically regardless of Casual or
Advanced mode. It is not copied into per-course settings, and neither mode
silently overrides it.

When checked:

- a successful invitation roll after an eligible completed lap immediately
  arms The Pit as the next Agility review sequence;
- the challenge retains the originating course for its exact reward table;
- completing or leaving The Pit returns to that originating course
  automatically; and
- no offer popup or manual target selection is required.

When unchecked:

- the invitation becomes a pending Talent Scout offer;
- the player may accept or decline it through the Activity surface; and
- the existing no-wall-clock abstraction keeps the offer until that explicit
  decision rather than inventing a wall-clock minute.

The entry gate still matters. Auto-accept may stow weapon/shield items through
the ordinary safe equipment flow when inventory space exists, but it must not
silently dismiss a familiar. If a familiar is active, reuse the settled
Summoning confirmation before dismissal; declining or postponing that
confirmation leaves the invitation pending.

## Challenge and reward contract

The existing six-review challenge and four-success threshold remain labeled
AnkiScape abstractions pending exact source-time reconciliation. One bounded
challenge step resolves per review; no arena pathing or timer loop exists.

The source course/challenge XP matrices, reduced failure rewards, first gorilla
mask, skillcape practice route, and equal-odds post-success gamble remain
source-shaped. The challenge must store the originating course rather than
looking at the currently selected `the_pit` target when calculating or
recording the reward.

## Implementation mismatch recorded on 2026-07-18

The current implementation is not yet aligned with this contract:

- `agility_logic.py:_finish_lap` rolls an invitation after every course target
  without checking the eligible set, so Burthorpe and Penguin can incorrectly
  trigger it;
- no global auto-accept checkbox exists;
- `_pit_review` records the current target rather than a persisted originating
  course, so course-scaled reward identity is lost after selecting The Pit; and
- existing tests cover active/corrupt invitation state but not the nine
  eligible and two ineligible course boundaries.

The implementation pass must fix those concrete mismatches and add targeted
eligibility, auto-accept, familiar-confirmation, origin-course, return-target,
and undo coverage. This design thread does not modify the live Agility code.
