# Vinesweeper flattened activity contract

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **period structure pinned and owner design closed; the board puzzle is
deliberately omitted.**

## Pinned period evidence

`Vinesweeper`, oldid `6288368` (`2012-09-24T04:55:21Z`), establishes:

- a safe members Farming/Hunter minigame at Winkin's Farm;
- a spade requirement satisfied by the tool belt;
- ten free starting flags, a maximum of ten, and replacement flags costing
  either 500 coins or 50 Vinesweeper points;
- a grid whose uncovered numbers identify adjacent seeds;
- one point per empty square uncovered, a ten-point penalty for digging up a
  seed, and a lost flag for an incorrect placement;
- correct seed flags paying a variable reward described as level-related,
  apparently random, commonly in the 100–200 range and reaching the 300s;
- rabbits racing farmers to flagged seeds, with a lost flag and no points when
  a rabbit wins;
- Ogleroots bought for 10 coins or found while digging, with each successful
  rabbit repulsion granting 30 Hunter XP and a random point award;
- Farming XP coming only from point redemption, at one point per XP from level
  40 and a level-scaled cost reaching 7.75 points per XP below level 40;
- a persistent point balance and an exact point shop containing Farming seeds,
  compost potion (4), flags, and direct Farming XP; and
- familiars and pets being barred from entry.

Source:

- <https://runescape.wiki/w/Vinesweeper?oldid=6288368>

The revision itself says the correct-flag and Ogleroot point awards appear
random and does not publish their distribution. It also does not provide
probabilities for safe digs, destroyed seeds, correct flags, rabbit threats, or
found Ogleroots. Those weights remain `source_blocked`; implementation may use a
clearly labeled bounded abstraction only after one final emulator/cache search.

## Deliberate flattening

AnkiScape does not reproduce Minesweeper. There is no grid, tile selection,
number inspection, confidence control, path state, farmer actor, rabbit actor,
or invisible board simulation.

Each successful review resolves exactly one automatic, narrated
Vinesweeper operation from the source-shaped outcome set:

- uncover safe ground and gain its point;
- identify and correctly flag a seed, temporarily spending and then recovering
  one flag while receiving the bounded point award;
- make a mistaken dig or flag and apply the matching point or flag loss; or
- repel a rabbit with an Ogleroot, preserving the flagged-seed reward and
  granting 30 Hunter XP.

This is a single bounded outcome roll and a few scalar deltas, not a backend
simulation of a field. The result line reports the operation, point change,
flag change, coin change, and Hunter XP when applicable. There is no strategy
selector: without a visible board, cautious/aggressive modes would be fake
agency.

`Again` performs no Vinesweeper operation, grants no points or XP, and loses no
flag. It advances only the ordinary answered-card world systems. There is no
wall-clock timer, daily limit, session expiry, or offline catch-up.

Cadence class is `source_blocked_activity` until the outcome weights are
resolved. At multiplier `M`, resolve up to `M` complete operations, stopping
when the activity cannot afford a required flag or when the player leaves. One
undo restores the complete review batch, including every point, flag, coin,
Ogleroot, and XP delta.

## Automatic supplies

The player receives the source ten free flags once. Flags are an
activity-local charge meter capped at ten; they do not clutter the ordinary
inventory.

When a replacement is required, automation:

1. spends 500 coins;
2. if coins are unavailable, spends 50 Vinesweeper points; and
3. pauses the activity only when neither payment is possible.

The status line shows the current flag count and the payment used. There is no
trip to Mrs Winkin and no refill toggle.

Rabbit handling is equally automatic. A found Ogleroot is used first. If a
rabbit threatens and no root is held, the activity buys one for 10 coins and
uses it immediately. If neither a root nor 10 coins is available, the rabbit
wins and the source flag/no-points consequence applies. Any excess roots are
refunded on leaving, matching the source without making them a general
inventory-management chore.

## Rewards and persistence

Vinesweeper points persist across visits. Leaving clears only the discarded
field abstraction and refunds excess Ogleroots; there is no board to save or
resume.

Mrs Winkin's complete cutoff shop is one bespoke point-shop surface backed by
the shared activity wallet:

- direct Farming XP uses the source level-scaled point cost and is a
  `direct_command`;
- every period seed row and compost potion (4) remains available at the exact
  point price in the pinned revision;
- bought items enter the ordinary inventory/bank transaction and retain their
  real downstream Farming or Herblore uses; and
- buying flags uses the same 50-point source price as automatic replenishment.

Reward redemption consumes no review and is never cadence-multiplied.

## Entry and follower boundary

Entry requires the tool-belt spade or an ordinary carried spade. The
Tool-Leprechaun teleport is flattened into the Activity's direct location
transition and consumes no review.

An active familiar or pet cannot enter. The shared follower-dismissal
confirmation appears before the transition; AnkiScape does not silently dismiss
one. After confirmation, the follower uses its ordinary dismissal state and
the activity opens.

## Implementation acceptance

The implementation pass must prove:

1. no board, tile, NPC, or timer state exists;
2. one successful review mutates only the bounded source-shaped outcome;
3. `Again`, multiplier, terminal, save/load, and undo behavior follow this
   contract;
4. flag replacement uses coins, then points, then a visible pause;
5. rabbit defense uses found or automatically purchased Ogleroots before
   applying the source failure;
6. Farming XP can arise only from point redemption and Hunter XP only from
   rabbit repulsion;
7. the complete cutoff shop uses exact prices and real item outputs; and
8. familiar/pet entry invokes the shared confirmation rather than creating a
   Vinesweeper-only follower rule.

