# Agility failure-consequence audit — 2026-07-15

Cutoff: `2012-11-20T00:00:00Z`. This is the consequence companion to
`agility-fail-rates-2026-07-13.md`. It distinguishes period-proven behavior,
provisional hidden-roll parameters, and AnkiScape design abstractions. It does
not implement a failure model.

## Verdict

The earlier universal rule — “failed course obstacle = 0 XP + LP damage + a
stage-counter drop” — is not faithful. Period sources prove at least five
different result shapes:

1. **Cross with a penalty:** Gnome advanced still crosses the signpost, pauses,
   loses LP, and invalidates only the lap used for Agile-legs progress.
2. **Retry / positional setback:** Wilderness and Pyramid failures put the
   player behind the obstacle, in a dungeon, or one pyramid level lower.
3. **Damage without displacement:** Wilderness's third stone and Burthorpe's
   novice failures do not produce the same course reset as a fall.
4. **Reduced XP on failure:** Werewolf deathslide awards at least `180 XP`, can
   still deliver the stick, and therefore completes rather than resetting.
5. **State damage:** Dorgesh-Kaan damages the retrieved part; Brimhaven darts
   additionally drain `2 Agility levels`.

AnkiScape should encode a small per-obstacle consequence record. Reusing
Thieving's `failure_damage` channel is appropriate for LP loss, but that channel
cannot replace XP, position, lap-validity, or item-state fields.

## Provenance rule for failure rates

The period wiki proves which obstacles fail and often what happens, but almost
never supplies the server roll. Under
`pre-eoc-source-verification-standard.md`, modern OSRS/RS3 endpoint tables do
not become period facts merely because their update histories are clean.
Accordingly, the exact curves recovered in the 2026-07-13 audit have these
shipping labels:

- Barbarian normal, Wilderness main, and Penguin platform/icicles are
  **candidates** for `provisional/osrs`, after the recorded branch-history gates;
  they remain `source_blocked` until that owner abstraction is adopted.
- Burthorpe and Brimhaven endpoint rows are candidates for
  `provisional/rs3`, not “historically closed,” and remain `source_blocked`
  unless adopted. Brimhaven's spinning-blade row has unusually strong period
  corroboration (`34/100` failures at level 76 versus the candidate curve's
  `34.375%`), but the other eleven endpoint pairs remain modern-supplied.
- Every other exact rate: `source_blocked` until the owner chooses a labeled
  AnkiScape fallback.

This corrects the older audit's “zero-invention Tier 4” wording without
discarding its valuable formula recovery or exhaustive branch-history work.

## Period consequence ledger

`xp_on_fail = source_blocked` means the page gives successful obstacle XP but
does not say what a failed attempt awards. It is not permission to silently use
zero.

### Gnome Stronghold

Source: `Gnome Stronghold Agility Course`, oldid
[`6391497`](https://runescape.wiki/w/Gnome_Stronghold_Agility_Course?oldid=6391497),
`2012-10-12T18:29:49Z`.

| Route / obstacle | Can fail | Rate | XP on fail | Damage | Setback / state |
|---|---|---|---|---|---|
| Normal course, all obstacles | No | n/a | n/a | None | None |
| Advanced signpost | Yes | `source_blocked`; observed roughly `40–50%` at 85, zero from 89 | `source_blocked` | Up to `70 LP`; exact function blocked | **Still crosses**; pauses a few seconds; lap does not count toward Agile legs. No course-stage drop is sourced. |

The page does not say that signpost failure cancels the ordinary `605 XP` lap
bonus. Treat Agile-legs lap validity and XP-lap validity as separate until a
source establishes otherwise.

### Barbarian Outpost

Source: `Barbarian Outpost Agility Course`, oldid
[`6549278`](https://runescape.wiki/w/Barbarian_Outpost_Agility_Course?oldid=6549278),
`2012-11-12T10:22:50Z`.

| Route / obstacle | Can fail | Rate | XP on fail | Damage | Setback / state |
|---|---|---|---|---|---|
| Normal rope swing | Yes | `source_blocked`; candidate `provisional/osrs F(L;200,280)` | `source_blocked` | Yes; amount blocked | Climb back to the obstacle's starting point and retry. |
| Normal log balance | Yes | `source_blocked`; candidate `provisional/osrs F(L;180,260)` | `source_blocked` | Yes; amount blocked | Exact landing/recovery is blocked. |
| Normal balancing ledge | Yes | `source_blocked`; candidate `provisional/osrs F(L;200,280)` | `source_blocked` | Yes; amount blocked | Climb back to the obstacle's starting point and retry. |
| Normal obstacle net / walls | No | n/a | n/a | None from course failure | None |
| Advanced shared rope | Yes; same normal-course obstacle | `source_blocked`; candidate `provisional/osrs F(L;200,280)` | `source_blocked` | `source_blocked` | Return to rope start. |
| Advanced shared log | Yes | `source_blocked`; candidate `provisional/osrs F(L;180,260)` | `source_blocked`; failed log forfeits lap bonus | `source_blocked` | Exact physical recovery blocked. |
| Advanced balance beam | Failable-set membership itself is `source_blocked` | Candidate `provisional/rs3 F(L;-1635,400)` | `source_blocked` | `source_blocked` | `source_blocked` |
| Other advanced obstacles | Page says “several,” but set is incomplete | `source_blocked` | `source_blocked` | `source_blocked` | `source_blocked` |

A failed normal rope or ledge is a same-obstacle retry, not evidence for a
global one-stage decrement. The advanced log proves a separate `lap_valid=false`
effect.

### Wilderness

Source: `Wilderness Agility Course`, oldid
[`6487716`](https://runescape.wiki/w/Wilderness_Agility_Course?oldid=6487716),
`2012-10-28T02:29:46Z`.

| Obstacle | Can fail | Rate | XP on fail | Damage | Setback / state |
|---|---|---|---|---|---|
| Access walkway | Yes | `source_blocked` | `source_blocked` | `source_blocked` | Falls among wolves outside/below the entrance path. |
| Obstacle pipe | No | n/a | n/a | None | None |
| Rope swing | Yes | `source_blocked`; candidate `provisional/osrs F(L;200,250)` | `source_blocked` | Amount blocked | Drops to the underground dungeon; climb out and redo the missed obstacle to preserve the bonus. |
| Third stepping stone | Yes | `source_blocked`; candidate `provisional/osrs F(L;180,250)` | `source_blocked` | `26.6%` of remaining LP, rounded down; page conflicts on `200` versus `208` maximum | Put behind the failed stones; retry to preserve the bonus. |
| Log balance | Yes | `source_blocked`; candidate `provisional/osrs F(L;200,250)` | `source_blocked` | Amount blocked | Drops to the underground dungeon; climb out and redo the missed obstacle. |
| Final rocks | No | n/a | `0` if the ordered prerequisites were missed | None | Awards no bonus unless every obstacle was completed in order/retried. |

Preserve the page's internal `200`/`208` damage-cap conflict. Do not choose one
as a period fact.

### Burthorpe

Source: `Burthorpe Agility Course`, oldid
[`6130636`](https://runescape.wiki/w/Burthorpe_Agility_Course?oldid=6130636),
`2012-08-23T14:17:25Z`.

| Obstacle | Can fail | Rate | XP on fail | Damage | Setback / state |
|---|---|---|---|---|---|
| Log beam | Yes, only in the first few Agility levels | `source_blocked`; candidate `provisional/rs3 F(L;153,1263)`; modern page says disabled after three laps | `source_blocked` | **None** | Exact recovery blocked |
| Obstacle low wall | Same | Same candidate; period rate remains blocked | `source_blocked` | **None** | Exact recovery blocked |
| Other obstacles | No failure identified | n/a | n/a | None | None |

The freeze-date oldid says “first few Agility levels,” not “after three laps.”
The three-lap bypass comes from a modern RS3 row and must remain part of the
`provisional/rs3` package rather than being described as period-proven.

### Agility Pyramid

Source: `Agility Pyramid`, oldid
[`6457748`](https://runescape.wiki/w/Agility_Pyramid?oldid=6457748),
`2012-10-23T02:32:50Z`.

| Obstacle | Can fail | Rate | XP on fail | Damage | Setback |
|---|---|---|---|---:|---|
| Rolling block | Yes | `source_blocked` | `source_blocked` | `60 LP` (`10 LP` when deliberately going backward) | One pyramid level down |
| Low wall | Yes | `source_blocked` | `source_blocked` | `40 LP` | Slip; exact stage/side blocked |
| Moving block | Yes, timing-based | Player timing, not a sourced random curve | Successful XP is already `0` | `80 LP` | One pyramid level down |
| Cross ledge | Yes | `source_blocked` | `source_blocked` | `100 LP` | One pyramid level down |
| Cross plank | Yes | `source_blocked` | `source_blocked` | `100 LP` | One pyramid level down |
| Cross gap | Yes | `source_blocked` | `source_blocked` | `80 LP` | One pyramid level down |
| Jump gap | Yes | `source_blocked` | `source_blocked` | `80 LP` | One pyramid level down |

The exact ordered stage reached on the lower floor is absent. “One level down”
should therefore be represented by a course-floor checkpoint, not guessed as a
universal `stage - 1`.

### Ape Atoll

Source: `Ape Atoll Agility Course`, oldid
[`6538325`](https://runescape.wiki/w/Ape_Atoll_Agility_Course?oldid=6538325),
`2012-11-06T00:27:47Z`.

| Obstacle | Can fail | Rate | XP on fail | Damage | Setback / state |
|---|---|---|---|---|---|
| Final climb-down | Yes below 75 | `source_blocked`; zero from level 75 | **`0 XP`:** failure loses the final `100 XP` and `300 XP` bonus, which is more than half the `580 XP` lap | About `70–80 LP` near full health, falling toward `30 LP` at lower health | Lap bonus/final reward lost; exact landing stage blocked |
| Other obstacles | The pinned page does not safely enumerate them as failable | `source_blocked` | `source_blocked` | `source_blocked` | `source_blocked` |

Do not expand the failable set from a later post-change table.

### Werewolf

Source: `Werewolf Agility Course`, oldid
[`6288778`](https://runescape.wiki/w/Werewolf_Agility_Course?oldid=6288778),
`2012-09-24T05:54:46Z`.

| Obstacle | Can fail | Rate | XP on fail | Damage | Setback / state |
|---|---|---|---|---|---|
| Deathslide | Yes; only failable obstacle | `source_blocked`; rare around 72, zero from 93; Agility/Strength/weight expression absent | **At least `180 XP`, increasing with distance before the fall; success is `200 XP`** | Can exceed `300 LP`; near-end falls about `100–150 LP` | Still reaches the end and may return the stick for its `190 XP` bonus; no stage reset |

This is the decisive counterexample to universal `xp_on_fail=0` and universal
stage loss. The exact partial-XP mapping is blocked; a bounded AnkiScape
abstraction may choose `180 XP` because it is the sourced minimum, but it must
not invent a distance curve that Anki reviews cannot represent.

### Dorgesh-Kaan

Source: `Dorgesh-Kaan Agility Course`, oldid
[`6547042`](https://runescape.wiki/w/Dorgesh-Kaan_Agility_Course?oldid=6547042),
`2012-11-10T19:12:05Z`.

| Obstacles | Can fail | Rate | XP on fail | Damage | Setback / state |
|---|---|---|---|---|---|
| Cables and ladders | Yes, even at 99 | `source_blocked`; decreases but never reaches zero | `source_blocked` | About `100 LP` | Falls to lower dungeon; retrieved part is damaged; return via north stairs. The lap's requested-part reward is therefore invalidated. |
| Walls / tunnel | No failure identified by the pinned page | n/a | n/a | None | None |

The retrieved-part damage needs its own `lap_item_valid=false` state. A simple
stage decrement cannot reproduce it.

### Penguin

Source: `Penguin Agility Course`, oldid
[`5988056`](https://runescape.wiki/w/Penguin_Agility_Course?oldid=5988056),
`2012-07-25T13:51:02Z`.

| Obstacle group | Can fail | Rate | XP on fail | Damage | Setback / state |
|---|---|---|---|---|---|
| Ice crushers | Yes | `source_blocked` | `source_blocked` | `source_blocked` | `source_blocked` |
| Platform jumps after safe first jump | Yes | `source_blocked`; candidate `provisional/osrs F(L;155,308)` | `source_blocked` | `source_blocked` | `source_blocked` |
| Four icicle checks | Yes; incorrect click always hurts | `source_blocked`; candidate `provisional/osrs F(L;155,308)` for Agility checks | `source_blocked` | `source_blocked` | `source_blocked` |
| Ice slope except safe last step | Yes, partly timing-based | `source_blocked` | `source_blocked` | `source_blocked` | `source_blocked` |

The page recommends food and warns that the slope can consume enough food to
risk death, but it supplies no per-failure damage number or recovery position.

### Brimhaven Agility Arena

Source: `Brimhaven Agility Arena`, oldid
[`6556177`](https://runescape.wiki/w/Brimhaven_Agility_Arena?oldid=6556177),
`2012-11-15T03:00:35Z`.

All ordinary random obstacle failures deal `20–60 LP` based on current LP. The
exact damage function is blocked. The page gives successful immediate XP but
does not state XP on a random failed attempt, so `xp_on_fail` remains blocked
for every row. The modern endpoint rows remain `source_blocked`; if the owner
adopts them, they may ship only as `provisional/rs3`.

| Obstacle | Candidate rate | Successful XP | Failure-specific state / recovery |
|---|---|---:|---|
| Low wall | `source_blocked`; candidate `provisional/rs3 F(L;220,460)` | 8 | Slow recovery; exact platform side blocked |
| Rope swing | `source_blocked`; candidate `provisional/rs3 F(L;100,310)` | 20 | Recovery over 12 seconds; falls to lower level |
| Log balance | `source_blocked`; candidate `provisional/rs3 F(L;180,420)` | 12 | Recovery over 12 seconds |
| Ledge | `source_blocked`; candidate `provisional/rs3 F(L;140,370)` | 16 | Recovery over 12 seconds |
| Safe/cracked plank | Deterministic player choice | 6 | One plank safe, two unsafe; safe choice changes with pillar |
| Pillars | `source_blocked`; candidate `provisional/rs3 F(L;120,340)` | 18 | Only second pillar can fail; recovery over 12 seconds |
| Monkey bars | `source_blocked`; candidate `provisional/rs3 F(L;160,400)` | 14 | Recovery over 12 seconds |
| Rope balance | `source_blocked`; candidate `provisional/rs3 F(L;200,440)` | 10 | Recovery over 12 seconds |
| Sawblade | Deterministic timing | 0 | Failure may still pass or may push back; `20–60 LP` general statement applies |
| Spiked floor | `source_blocked`; candidate `provisional/rs3 F(L;60,250)` | 24 | Fast, about 4-second recovery |
| Pressure pads | `source_blocked`; candidate `provisional/rs3 F(L;40,230)` | 26 | Fast, about 4-second recovery |
| Hand-holds | `source_blocked`; candidate `provisional/rs3 F(L;80,280)` | 22 | Only third hold can fail; recovery over 12 seconds |
| Spinning blades | `source_blocked`; candidate `provisional/rs3 F(L;30,210)` | 28 | Fast recovery; candidate curve period-corroborated at level 76 |
| Darts | `source_blocked`; candidate `provisional/rs3 F(L;20,190)` | 30 | Also drains `2 Agility levels`; fast recovery |

For AnkiScape's grid, a random failure should normally leave the player on the
origin platform and consume the review; that is a **minimal arena abstraction**
from the recovery behavior, not a sourced universal rule. Sawblade is the
exception: the source explicitly permits either pass-through or pushback.

## Shortcut consequence and XP conflict

The five logical shortcuts in `agility-tables-2026-07-13.md` are implemented by
three deterministic 2011Scape handlers at
`/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/agility/agility_shortcuts.plugin.kts`,
but period sources conflict with that executable:

- `Agility`, oldid
  [`6477884`](https://runescape.wiki/w/Agility?oldid=6477884), says stiles
  award `3 XP` and the level-51 sewer pipe awards `0 XP` with a chance of small
  damage.
- `Shortcuts`, oldid
  [`6345639`](https://runescape.wiki/w/Shortcuts?oldid=6345639), says the two
  named stiles award no XP and lists the pipe at level 51.
- `Talk:Agility`, oldid
  [`5349634`](https://runescape.wiki/w/Talk:Agility?oldid=5349634), specifically
  reports no XP at the Falador cabbage-patch stile.
- 2011Scape gives all stiles `3 XP`, both pipe directions level `53` and
  `7.5 XP`, and has no damage/failure branch (`lines 234-243`, `416-505`).

| Shortcut | Period can-fail result | Rate | XP on adverse event | Damage / recovery |
|---|---|---|---|---|
| Edgeville Dungeon monkey bars | `source_blocked`; emulator is deterministic | `source_blocked` | `source_blocked` | `source_blocked`; emulator crosses safely |
| Fred the Farmer stile | `source_blocked`; emulator is deterministic | `source_blocked` | n/a; ordinary XP conflicts (`0` versus `3`) | `source_blocked`; emulator crosses safely |
| Falador cabbage-patch stile | `source_blocked`; emulator is deterministic | `source_blocked` | n/a; period page/talk support ordinary `0 XP` | `source_blocked`; emulator crosses safely |
| Edgeville → Varrock pipe | Yes for an adverse damage roll; traversal failure not proven | `source_blocked` | Period table gives `0 XP` | Small LP damage; exact amount and final side blocked |
| Varrock → Edgeville pipe | Same bidirectional hazard | `source_blocked` | Period table gives `0 XP` | Small LP damage; exact amount and final side blocked |

The earlier rule “shortcuts give reduced XP on fail” is still wrong as a global
model. The pipe has a period damage chance and `0 XP` regardless; the other
four have no proven failure event. Resolve the ordinary stile XP conflict before
implementation rather than fabricating failure branches for them.

## Recommended consequence schema

```text
can_fail
fail_rate_source        # period | provisional/osrs | provisional/rs3 | abstraction
xp_on_fail
failure_damage
position_result         # cross | stay | retry | checkpoint | lower_floor | end
lap_xp_valid
lap_reward_valid        # Agile piece, stick, requested part, ticket streak
stat_drain               # Brimhaven darts
```

This is small enough to remain data-driven and expressive enough to reproduce
every period-proven branch. A single numeric stage decrement is not.

## Open design decision

Where the exact roll remains blocked, a labeled fallback is permitted by owner
ruling. The source-constrained options are:

1. Use the provisional OSRS/RS3 curves where they exist, retaining their labels.
2. Use one minimal AnkiScape curve for remaining random obstacles, constrained
   by the period mastery cutoffs/observations and overridden only where the
   source proves a different shape (Dorgesh-Kaan never reaches zero; Werewolf is
   multi-input; Pyramid has distinct obstacle difficulties).
3. Treat timing/choice obstacles as deterministic review outcomes rather than
   forcing them through the random-failure fallback.

The exact fallback belongs in the owner grill after the Brimhaven activity loop
is designed; this audit supplies the constraints but does not manufacture a
choice.
