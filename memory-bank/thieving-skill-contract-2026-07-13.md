# Thieving — implementation contract (2026-07-13)

Settled by three rounds of owner grilling. Everything here is decided; nothing
in this file is open for the implementer to relitigate. Where a value is not
stated here, it is **not yet known** and must be read from the sources named
below — never invented, never taken from the prose dossier's shorthand.

Companion documents:
- Source dossier (prose, uses a shorthand that has already caused one
  misreading): `memory-bank/source-audits/thieving-source-dossier-2026-07-13.md`
- Decisions of record: `memory-bank/future-work-kanban.md`, the Thieving card.
- Sourced XP/hour, already pinned: `tools/sourced_xp_rates.py:74-97`.
- Verification standard: `memory-bank/pre-eoc-source-verification-standard.md`.

## Sources, and which one wins

Two emulators exist and they are **not** peers.

| | path | standing |
|---|---|---|
| **2011Scape** | `~/Downloads/game-main` (its README is literally `<h1>2011Scape</h1>`; `gg.rsmod` is only the framework it builds on) | **trusted — ships** |
| **Darkan** | `~/Documents/2012scape with bots/darkan-world-server` | established inventor — divergence column only |

Thieving lives at
`game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/thieving/`.

Where they conflict, **2011Scape ships**, including the rows OSRS cannot referee
(Paladin, Gnome, Hero — all invalidated by OSRS's May-2024 "Project Rebalance:
Skilling"). OSRS's published endpoints matched 2011Scape exactly on eight
independent rows and contradicted Darkan on nearly all of them. Cherry-picking
Darkan only where the referee is absent would be selecting the source by
convenience.

If 2011Scape is silent and only Darkan has a row, the row is `source_blocked`
and Darkan's value is recorded as a lead, not shipped.

## The notation trap — read before recording a single number

In `PickpocketTarget.kt`, `minChance` and `maxChance` are **not a fraction and
not a probability**. They are the level-1 and level-99 endpoints of a linear
interpolation rolled against a ceiling of **255 that is identical for every
target**:

```
chance(level) = (minChance + (maxChance - minChance) * (level - 1) / 98) / 255
```

There is ONE roll shape, not one per denominator. Reading the endpoints as
fractions manufactures phantom conflicts — it is what produced the illusion of a
"3x Paladin disagreement," which is really 3.9pp at level 70 and **0.0pp at 99**.

The helper is `MiscExt.kt:29-34`; the roll is `PickpocketTarget.kt: fun roll`.

## Stalls — the settled model

**Catch chance is zero.** 2011Scape calls `handleSuccess` with no roll in front
of it (`Stalls.kt:33`). The only failure path is `caughtByGuard`, which is purely
positional (`it.sees(player, 8)`, `Stalls.kt:65`) and attaches to two of sixteen
stalls — Draynor's wine (`StallTarget.kt:157`) and seed (`:188`), both Market
Guard 2236. Every other row carries `guards = listOf()` and cannot fail.
AnkiScape has no location layer, so the guard cannot be modelled; **zero is the
faithful value, not a shortcut.** Do not invent a catch constant. Do not port the
guard.

**The restock timer is the rate limiter, and it is exact.** A game tick is 0.6s,
so from `respawnTicks` alone:

```
actions_per_hour = 6000 / respawnTicks      # exact rational, no rounding
```

Which is one call into the shipped kernel, per stall, with no free parameter:

```python
rate_limited_profile_pure(f"thieving:{stall_id}", 6000, respawn_ticks)
```

`cadence_kernel.py:175`. Rates above `R = 1000` (the vegetable, baker, and wall
safe stalls) must declare `overflow_policy=CAP_ONE_ACTION`; the kernel raises if
they don't (`:169`).

This reproduces the period XP/hour with **zero invented constants**. 2011Scape's
`respawnTicks` and the 2012 wiki's experience-per-second column are the same
numbers, derived independently and never in contact:

| stall | lvl | xp | respawnTicks | implied xp/hr | wiki E.P.S. × 3600 |
|---|---|---|---|---|---|
| Vegetable | 2 | 10 | 3 (1.8s) | 20,000 | 18,000 |
| Baker | 5 | 16 | 3 (1.8s) | 32,000 | 23,040 |
| Silk | 20 | 24 | 8 (4.8s) | 18,000 | 10,800 |
| Silver | 50 | 54 | 50 (30s) | **6,480** | **6,480** |
| Spice | 65 | 81 | 133 (79.8s) | 3,654 | 3,600 |
| Gem | 75 | 160 | 300 (180s) | 3,200 | 3,240 |

The three high-level rows agree to within rounding. **Any nonzero catch constant
would push every stall below its own sourced rate** — reintroducing the exact
defect the cadence kernel exists to remove.

**The wall safe is the exception that proves the rule.** It is the only
stall-family row carrying chance endpoints (`lowChance = 8, highChance = 160`,
`StallTarget.kt:263-264`) — the same interpolate-against-255 shape as
pickpocketing — and the only one whose unconditional success (70 xp / 3s =
84,000/hr) overshoots its sourced ceiling (~20,000/hr, `sourced_xp_rates.py:96`).
It fails because the period game meant it to. Ship those endpoints. Note the
fields are declared but **unused** in `Stalls.kt`: 2011Scape carried the data and
never wired it.

**Ship the level inversion.** The level-5 baker stall out-earns the level-75 gem
stall by ~7x, in both sources. That is authentic — pre-EOC players camped gem
stalls for the *gems*, and the wiki's own escape hatch ("ideal to world hop") is
a location mechanic we cannot model and must not fake. It is safe because the bad
option is never the best available one: at 75 Thieving the player already has
knights of Ardougne (180,000/hr) and blackjacking (200,000–270,000/hr). The gem
stall's poor XP is the price of its loot table, which we do model.
**Do not invent a world-hop abstraction to "fix" this.**

## Pickpocketing — the settled model

Ship **2011Scape's table wholesale**, pinned `provisional/2011Scape`.

Multi-pickpocket is 2011Scape's rule (`Pickpocketing.kt:97-113`), which the
period wiki corroborates over Darkan's `getRandomInclusive(50) < 5`:

```kotlin
return if (thievingLevelOvershoot >= 10 && agilityLevelOvershoot >= 0 && player.world.random(7) == 1) {
    when {
        thievingLevelOvershoot >= 30 && agilityLevelOvershoot >= 20 -> 4
        thievingLevelOvershoot >= 20 && agilityLevelOvershoot >= 10 -> 3
        else -> 2
    }
} else { 1 }
```

Stun and damage on a failed pickpocket: 2011Scape's values.

## Failure stake (owner-settled, round 1)

A failed attempt costs the review, applies the sourced damage to the **shared
combat lifepoint pool**, and stuns, so the next review only clears the stun.
Thieving gets a food loadout on the existing `combat_supply_loadout` substrate.

One casual toggle governs both stall guards and blackjack thugs: **"Fight back
when caught"**, default off. Unchecked means you flee for one round of damage;
checked means a real combat encounter. Three casual controls total — the owner
fears checkbox hell, and full control lives in the advanced editors.

## Content rulings

- **Pompous Merchant ships** on the pinned 2012 wiki page's authority (level 1,
  8 XP, 3 coins, stun, 10 LP), not Darkan's. The caches' missing `Pickpocket`
  option is recorded as a conflict, not a veto.
- **Desert Phoenix is NOT a Thieving target.** Both caches show `Grab-feather`;
  2011Scape has it only as a spawn. It ships as a **Utility activity** yielding
  one Phoenix feather, gated on The Golem, with **no Thieving level and no XP**.
  This also closes a live bug: `herblore_data.py:188` ships Super antifire (3)
  requiring a Phoenix feather that nothing in the game currently yields.
- **Pirates' Hideout chest parks.** Its XP is literally `?` in the period record.
  Ships only if a pre-cutoff value surfaces.
- **Pyramid Plunder is excluded from the skill** and belongs to the Activities
  program (it grants Strength and Runecrafting XP and gates on a Strength level).
  Sorceress's Garden, the Rogues' Den maze, and the Thieves' Guild go with it.
  The Rogues' Den **wall safes are separable and do ship.**
- **The Feud ships with this build** — it gates blackjacking. Dorgesh-Kaan chests
  and Lletya elves ship gated and dark behind their quests.
- Blocked rewards, listed on their own cards, not here: the rogue outfit
  (x1.025 XP, Rogues' Den maze only) and the Ardougne cloak (achievement
  diaries).

## Invariants

- **NEVER invent a value.** No source states it → `source_blocked`, and the row
  parks. Absence of evidence is a finding and recording it correctly is worth
  more than filling the cell.
- **Preserve source base XP exactly.** Any rate correction rides the cadence
  profile, never the XP value.
- The kernel is integer/rational (`Fraction`) throughout. **No float is ever
  persisted.** A refractory period is a deterministic residual schedule, not a
  probability lottery.
- Every shipped number carries a `file:line` citation into 2011Scape or a pinned
  wiki `oldid`.

## Owner amendments during implementation

The owner explicitly overrode the earlier source-blocking interpretation for
blackjacking and asked the implementer to resolve it. The shipped minimal loop
uses period-wiki player-visible values and the Darkan hidden knockout roll as a
clearly labelled provisional bridge. Menaphite thug is the only blackjack row
whose XP, loot, failure damage, and two-pick cycle are fully closed.

For stalls, exact 2011Scape respawn cadence remains authoritative when the
period wiki's rounded XP/hour disagrees. Acceptance therefore uses 6,480 for
silver, `486000/133` for spice, and 3,200 for gem, without tuning constants.

Closure audit clarified two source paths that the initial implementation had
collapsed. Wall safes use `MiscExt.kt`'s standalone three-argument interpolation
with a strict comparison, then deal the sourced 20–60 LP trap hit. Thieving is
one foreground action per answered card, so a global action multiplier never
advances its review-based cadence more than once. Failure damage shares Combat's
auto-eat/death/grave substrate; choosing fight-back starts the Menaphite combat
encounter without first applying the flee-only 40 LP hit.
