# TzHaar Fight Cave horizontal-MVP source audit — 2026-07-20

## Scope and cutoff

This audit pins the smallest readily available 2012-11-20-or-earlier data set
needed to exercise the settled Fight Cave mechanics end to end. It does not
claim exhaustive NPC formula or navigation parity. Evidence priority follows
`memory-bank/pre-eoc-source-verification-standard.md`.

## Period sources

The following RuneScape Wiki revisions were fetched through the MediaWiki API
and inspected as immutable oldids:

| Subject | Oldid | Revision timestamp | Used for |
|---|---:|---|---|
| TzHaar Fight Cave | 6584235 | 2012-11-19T10:51:07Z | 63 waves, roster construction, enemy table, safe-death framing, partial/completion rewards |
| Fire cape | 6591500 | 2012-11-20T05:39:41Z | item 6570, non-tradeable cape, +11 defence, +4 strength, +2 prayer |
| TzTok-Jad | 6547334 | 2012-11-10T23:42:23Z | telegraphed ranged/magic attacks and period combat profile |
| Tz-Kih | 6451296 | before cutoff | 100 LP, melee, 44 max, prayer drain of raw damage plus 10 with a minimum of 10 |
| Tz-Kek | 6235920 | before cutoff | 200 LP large form, 100 LP small forms, 10 recoil, two-way split |
| Tok-Xil | 6207144 | before cutoff | 400 LP and melee/ranged combat profile |
| Yt-MejKot | 6548201 | before cutoff | 800 LP, melee, healing role and approximately 280 max hit |
| Ket-Zek | 6207126 | before cutoff | 1,600 LP, magic/melee profile and 540 max hit |
| Yt-HurKot | 6054672 | before cutoff | four 600-LP healers joining Jad at half health |

Canonical revision URLs use the form
`https://runescape.wiki/w/<Page>?oldid=<oldid>`. The Fight Cave revision's
literal table and binary wave construction reconcile to 63 waves, 192 initial
spawns, 272 enemies after all Tz-Kek splits, and 276 after one Jad healer set.

## Emulator convergence

Darkan commit `1c55b68bd9ad607dee30240094b866b3d92d9c46` provides a second,
independent implementation witness:

- `src/main/java/com/rs/game/content/minigames/fightcaves/FightCavesController.java:58-60`
  contains the exact 63-row wave table reproduced in `fight_caves_data.py`.
- `FightCavesController.java:79-85` blocks followers at entry.
- `FightCavesController.java:193-225` spawns each literal wave and four Jad
  healers.
- `FightCavesController.java:295-305` advances when the roster empties and
  routes defeat through safe death.
- `FightCavesController.java:324-359` awards item 6570 plus 16,064 TokKul on
  completion and uses `currentWave * 8032 / 63` for partial TokKul.
- `FightCavesController.java:370-375` preserves the controller across logout.
- `npcs/TzTok_Jad.java:47-70` spawns the first healer set at half health and a
  second set only after the first set restored Jad to full before dying.
- `npcs/YtHurKot.java:25-41` uses 100-LP heals. Its four-tick cadence is
  explicitly labeled a local reconstruction rather than recovered period data.

## Reconciled values and conflicts

- The period Fight Cave page gives Jad 2,550 LP; Darkan combat definitions use
  2,450. The period page wins for this cutoff-facing implementation.
- The Fight Cave table lists a 305 Yt-MejKot max hit, while the dedicated
  period page says approximately 280 and Darkan converges on 280. The MVP uses
  the lower convergent 280 and records the table conflict rather than presenting
  false precision.
- The period page's practical target order is represented by Casual priority:
  Tz-Kih, Tok-Xil, Ket-Zek, Yt-MejKot, then Tz-Kek. During Jad, live
  Yt-HurKot healers outrank Jad so Casual does not ignore the core healer
  mechanic. Advanced mode remains explicit player target selection.

## Labeled review-driven abstractions

These translations are mechanic-complete but are not claimed as period-exact
rates:

- One review advances exactly one live six-tick Combat slice against the
  engaged target.
- Every other roster member gets one ordinary Combat pressure attempt per
  review. Accuracy, defence and protection prayers still use the shared Combat
  formulas; damage is then resolved atomically through the shared failure-damage
  and carried-food channel.
- Yt-MejKot's reported healing-every-two-attacks behavior becomes one
  100-LP heal every two reviews while it remains alive.
- Each Yt-HurKot heals Jad for 100 LP per review. The exact period tick cadence
  is `source_blocked`; preserving the healer count, trigger, quantum and second
  generation is the horizontal-mechanics priority.
- Jad chooses and visibly announces the next ranged or magic style after each
  engaged review. The following review resolves through the ordinary protection
  prayer path.
- Leaving and safe defeat pay the integer-floor Darkan formula. There is no
  wall-clock timeout and no ordinary mid-instance bank trip.

## Explicit omissions and source-blocked items

- Exact NPC attack/defence bonus arrays, spawn coordinates, movement/pathing,
  safespots and line-of-sight behavior are not modeled by the review substrate.
- Exact Yt-HurKot period heal interval remains `source_blocked`.
- The discrepancy between 192, 272 and 276 commonly reported total-monster
  counts is definitional: initial roster, all split forms, and one healer set.
- Multi-healer simultaneous pressure is flattened to one bounded attempt per
  living unengaged member; it is not a claim about server-tick simultaneity.
- Slayer-on-Jad side rewards and task gating are outside this activity slice and
  remain owned by the Slayer contracts.

## Implementation mapping

- `fight_caves_data.py`: literal waves, combat profiles, items and source labels.
- `fight_caves_logic.py`: persistent roster/session reducer, target policies,
  healing, split, telegraph, safe defeat and rewards.
- `logic_pure.py`: reusable incoming roster-pressure attempt, generic recoil and
  prayer-drain fields, safe-death mode, and sealed-instance no-bank mode.
- `ui.py`: compact Activities detail card with roster, policy, target, explicit
  Leave and Jad telegraph.
- `tests/test_fight_caves.py`: source-shaped data, state, command and combat
  regressions.

