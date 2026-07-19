# Abyssal demon and Nechryael special-mechanic source audit

Date: `2026-07-19`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **qualitative behavior pinned; implementation values source-blocked.
Neither target may certify its Slayer family yet.**

Scope: resolve the two distinctive-mechanic blockers already named by the
Sumona, Duradel/Lapalok, and Kuradal pool audits. This audit does not reopen
their settled family membership, Slayer gates, pool rows, or the general
multi-enemy encounter pattern.

## Evidence

### Abyssal demon

`Abyssal demon` oldid
[`6565795`](https://runescape.wiki/w/Abyssal_demon?oldid=6565795),
`2012-11-17T10:10:43Z`, is the cutoff authority:

- the demon teleports itself and the player around the room together;
- the player ends in one of the eight spaces adjacent to the demon;
- terrain can leave ordinary melee unable to resume;
- when auto-retaliate is off, the player must explicitly resume attacking;
- ranged or magic often avoids the run-back interruption; and
- Slayer 85, 1,500 LP, 150 Slayer XP, melee, and the period drop boundary
  remain as already encoded.

The cutoff revision does **not** provide a teleport chance, a trigger event,
an interruption duration, or a distribution for the terrain-blocked outcome.
Its talk revision
[`5619836`](https://runescape.wiki/w/Talk:Abyssal_demon?oldid=5619836),
`2012-05-17T07:28:44Z`, was checked and contains no surviving special-mechanic
rate.

The Darkan snapshot pinned at
`c343a917712649675989315009ce250639e0850f` supplies the ordinary stats but no
Abyssal-teleport combat script. `game-main` likewise supplies only the ordinary
target definition. Modern/OSRS trigger rates are lower-tier and post-cutoff;
they cannot be projected backward over the missing period value.

**Finding:** `source_blocked`. The settled `mapless teleport interruption`
cannot yet be translated into attack-delay, disengagement, missed-player-action,
or another reducer outcome without choosing a new player-visible magnitude.
The existing generic target therefore remains usable data but not a
fully-functional certifying variant under Slayer Owner decision 20.

## Nechryael and Death spawn

`Nechryael` oldid
[`6530507`](https://runescape.wiki/w/Nechryael?oldid=6530507),
`2012-11-04T05:15:19Z`, pins:

- a Nechryael may randomly summon up to two level-46 Death spawns while engaged
  in melee;
- the spawns attack alongside their summoner even in a single-combat zone;
- they are accurate, hit up to 21 LP, and protection prayers do not reduce
  their period attack;
- auto-retaliate does not engage them;
- distance can make them lose interest after a few seconds; and
- ignoring the spawns and continuing to fight the Nechryael is an authentic
  strategy.

`Death spawn` oldid
[`6327456`](https://runescape.wiki/w/Death_spawn?oldid=6327456),
`2012-09-30T22:33:40Z`, additionally pins:

- 600 LP, level 46, attack speed 6, max hit 21, and a magical-melee attack;
- no Slayer requirement and no Slayer XP/family credit;
- guaranteed Accursed ashes when killed;
- direct player engagement is manual and is unavailable while the summoning
  Nechryael retains the single-combat engagement;
- the spawn exists for a limited duration and fades even when the player has
  engaged it; and
- a combat familiar does not attack it without an explicit order.

The cutoff revisions do **not** state the summon probability, exact lifetime,
or exact de-aggro distance/duration. The last pre-cutoff talk revisions
(`Talk:Nechryael` oldid `6571419`, `2012-11-18T05:28:29Z`; `Talk:Death spawn`
oldid `4549165`, `2011-07-22T04:06:40Z`) contain no rate or lifetime evidence.

Darkan's pinned `NechryaelCombat.java` supplies a lower-tier **1/10 per attack**
summon roll and always creates two spawns. Its `Nechryael.java` removes both
spawns when the Nechryael leaves combat **or dies**. That death cleanup conflicts
with the cutoff strategy text, which recommends killing the Nechryael before
dealing with or avoiding its still-present spawn. Darkan's Death-spawn data also
uses max hit 50 instead of the cutoff 21. `game-main` has target definitions but
no summon hook.

**Finding:** `source_blocked`. The owner-settled engaged-target plus pressure-
roster pattern in `multi-enemy-encounter-contract-2026-07-18.md` determines the
runtime shape, but the per-encounter source still does not determine the summon
admission rate or roster lifetime. The contradictory Darkan cleanup cannot
close those fields. Nechryael therefore remains non-certifying rather than
shipping a persuasive partial loop.

## Runtime seam once values close

Both mechanics belong inside the pure Combat burst transaction in
`logic_pure.apply_combat_burst_pure`, so the existing outer review snapshot
makes admission, damage, target pressure, timers, drops, XP, assignment credit,
death, and retreat undo-atomic.

- Abyssal interruption must be evaluated only at its source trigger and may
  alter only the current encounter's attack/disengagement state; it must never
  create global coordinates or a wall-clock timer.
- Death spawns become a visible pressure roster with Nechryael as the engaged
  target. They never grant Nechryael credit or Slayer XP. Manual engagement,
  Accursed-ash drops, finite lifetime, and main-target death must use the
  general multi-enemy contract once the missing values are pinned.

Required regression coverage after closure:

1. deterministic admission boundary and RNG draw order;
2. persisted cross-review state and exact expiry boundary;
3. Combat-class/protection behavior and bounded incoming pressure;
4. main-target kill with surviving/expiring spawn state;
5. manual spawn kill with Accursed ashes but zero Slayer credit/XP;
6. death, retreat, target change, and Answer Card undo;
7. readiness moving each family from its named special-mechanic blocker only
   after the complete loop is executable.

No owner-level design question emerged. This is period-value harvesting work,
not a design fork.
