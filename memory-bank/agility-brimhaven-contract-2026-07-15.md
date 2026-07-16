# Brimhaven Agility Arena — review-native design contract (2026-07-15)

Status: **owner-delegated and design-closed; implementation belongs in a new
thread.** This contract intentionally flattens the period arena's visible map
while preserving its ticket chase, streak pressure, obstacle identity, failure
risk, and reward economy.

Source ledger: `source-audits/agility-tables-2026-07-13.md` and
`source-audits/agility-fail-consequences-2026-07-15.md`. Cutoff:
`2012-11-20T00:00:00Z`.

## Period identity being preserved

The pinned `Brimhaven Agility Arena`, oldid
[`6556177`](https://runescape.wiki/w/Brimhaven_Agility_Arena?oldid=6556177),
establishes the recognizable loop:

- a 5x5 field with 24 taggable pillars and one exit;
- one active pillar at a time;
- the first successful tag activates the player but awards no ticket;
- every subsequent active pillar tagged without a miss awards one ticket;
- missing a pillar resets activation;
- adjacent platforms are connected by named Agility obstacles that award XP and
  may fail for damage; and
- tickets persist as items and may be exchanged in fixed bundles for XP or
  rewards.

The original active-pillar change used elapsed seconds. That fact informs the
existence of pressure but does **not** license a runtime wall clock. AnkiScape's
project-wide invariant is stronger: only reviews/actions or explicit commands
advance gameplay.

## Player experience

Brimhaven is one Agility training target. Starting it opens an arena stint; it
does not open a map or a second movement interface. The player answers cards as
normal. Each answered review attempts the next obstacle on an implied route to
the active pillar.

One concise line carries the whole minigame:

```text
{obstacle and outcome} · {crossings remaining} · {attempts remaining} · {activation/streak} · {banked tickets}
```

That line changes after every answer. Course art and the current obstacle icon
may accompany it, but coordinates, arrows, tiles, and manual path selection do
not.

## Flattened pillar chase

### Hidden geometry, visible pressure

Internally retain a virtual current pillar and a randomly chosen different
target pillar on the sourced 5x5 grid. The required crossing count is their
Manhattan distance (`1..8`). The coordinates exist only to generate the same
near-versus-far pressure as the arena; they are not exposed as a map.

The stint begins on the exit platform. For each chase, choose one shortest
Manhattan route to the target. Every successful crossing advances the hidden
position by one platform along that route; a failure leaves it in place. If a
chase is missed, the next target is generated from the last platform actually
reached rather than teleporting the player back to an invented start point.

Each pillar chase gets **eight answered-review attempts**, anchored to the
maximum eight-edge distance across a 5x5 grid. This is a deliberate AnkiScape
action-budget abstraction, not a seconds conversion:

- obstacle success consumes one attempt and removes one required crossing;
- obstacle failure consumes one attempt, applies its consequence, and removes
  no crossing;
- reaching zero crossings tags the pillar immediately and starts the next
  chase on the following review;
- reaching zero attempts first misses the pillar, resets activation, and starts
  a new chase on the following review; and
- undo restores the exact prior route, RNG, LP, XP, activation, and tickets.

There is no waiting after an early tag. The next pillar lights immediately in
the abstraction because idle time has no gameplay value in Anki.

### Activation and tickets

```text
inactive + successful tag -> active, +0 tickets
active   + successful tag -> active, +1 ticket
active   + missed chase   -> inactive, +0 tickets
inactive + missed chase   -> inactive, +0 tickets
```

Stopping Brimhaven training ends the stint and clears activation, but never
deletes already earned tickets. Closing and reopening the menu while Brimhaven
remains the active training target does not end the stint. Save/load preserves
the active chase exactly; elapsed real time changes nothing.

## Obstacle generation

The route generator chooses one eligible arena obstacle for each implied edge.
That obstacle remains the current crossing until it succeeds or the chase is
missed; a failure retries the same obstacle on the next review. No manual route
choice is required.

- Level-20 obstacles join the pool at Agility 20.
- Level-40 obstacles join at Agility 40.
- Below those levels, the generator uses the no-requirement pool rather than
  creating an impossible route.
- This owner-delegated contract adopts the audited candidate endpoint curves as
  `provisional/rs3` hidden-roll inputs. They are preferable to fabricating a new
  per-obstacle table, but remain explicitly non-period-closed and replaceable by
  later Darkan/period evidence.
- Plank balance becomes the sourced safe-plank choice: guaranteed traversal and
  `6 XP`. The cracked-plank failure branch is omitted because the flattened UI
  offers no meaningful visual choice.
- Sawblade becomes guaranteed traversal with `0 XP`; it remains flavor and
  route texture rather than a fake timing test.
- Darts retain an additional session-local `-2 effective Agility` consequence
  on failure. It affects the remainder of that chase and clears when the chase
  ends, whether by tag or miss. This review-bounded recovery is an explicit
  AnkiScape abstraction; it creates no wall-clock or global noncombat-stat timer.

The successful obstacle XP table and Karamja-glove modifier remain exactly as
audited. Failure XP is not period-closed; use the smallest labeled abstraction:
`0 XP` for a failed random obstacle. A failure leaves the implied route at the
same crossing.

### Failure damage abstraction

The period source fixes ordinary Arena failure damage to `20..60 LP` and says
lower current LP produces lower damage, but gives no equation. Use:

```text
damage = clamp(floor(current_lp / 10), 20, 60)
```

This is `ankiscape_failure_damage_abstraction`: monotonic in current LP, bounded
exactly by the sourced interval, deterministic for undo/testing, and no more
complicated than the evidence permits. Existing death, auto-eat, and grave
handling remain authoritative.

## Entry and stint boundary

- Starting a new stint costs the sourced `200 coins`.
- Completion of `Rocking Out` waives the fee.
- The fee is charged only when a stint begins, never per menu open, review, or
  pillar.
- Selecting another training target or pressing Stop Training ends the stint.
- Insufficient coins visibly locks stint start unless the quest waiver applies.

## Tickets and redemption

Tickets are durable, bankable inventory items. Arena progress awards them to the
normal owned-item store; leaving the activity cannot destroy them.

Expose the sourced XP exchanges as explicit player commands:

| Tickets | Base Agility XP | With equipped Karamja gloves 2/3/4 |
|---:|---:|---:|
| 1 | 240 | 264 |
| 10 | 2,480 | 2,728 |
| 25 | 6,500 | 7,150 |
| 100 | 28,000 | 30,800 |
| 1,000 | 320,000 | 352,000 |

Do not auto-redeem or silently optimize bundles. The increasing exchange rate
is the player's bank-versus-spend decision.

Also expose the period item rewards:

| Tickets | Reward |
|---:|---|
| 3 | Grimy toadflax |
| 5 | Grimy wergali |
| 10 | Grimy snapdragon |
| 800 | Pirate's hook |

These are ordinary non-Daemonheim herbs. Their inclusion does not reopen the
parked Dungeoneering herb family.

## UI contract

The Skills target panel needs only:

1. the ordinary Brimhaven target row and lock/entry explanation;
2. the single live narrative/status line;
3. activation and ticket counts;
4. Stop Training through the existing global control; and
5. a compact Redeem Tickets action opening the fixed XP/item bundle choices.

No grid, minimap, joystick, route picker, countdown animation, wall-clock timer,
or separate minigame window is warranted.

## Atomic implementation boundary

Ship Brimhaven only when all of these land together:

- persisted/undoable stint, virtual route, attempts, activation, and tickets;
- obstacle XP, provisional failure labels, damage, temporary Agility drain, and
  existing LP/death integration;
- admission and Rocking Out waiver;
- XP and item redemption;
- the one-line Skills UI surface; and
- focused pure, integration, end-to-end, and offscreen Qt coverage.

Do not ship a ticket counter without the chase, a chase without redemption, or
an attractive UI over wall-clock or non-undoable state.

## Owner decisions embodied here

- Flatten the spatial mechanics and narrate what is happening in one line.
- Never use wall-clock time anywhere in AnkiScape.
- Use product judgment to make Brimhaven compelling without requiring the owner
  to remember or reconstruct the original activity.
