# Jade Vine review-native contract

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **source shape pinned and owner-delegated design closed; current runtime
gaps recorded.**

## Pinned period evidence

`Jade vine`, oldid `6579442` (`2012-11-18T23:48:25Z`), establishes:

- level 53 Farming and completion of `Back to my Roots`;
- one unique patch outside Handelmort Mansion;
- 50 Farming XP for planting, about sixteen source hours of growth, and 1,500
  Farming XP for checking health;
- ordinary Farming disease and death, with ten wildblood hops as protection;
- no branch or Wild Vine progression until health has been checked;
- five visible branches growing approximately every 30–60 source minutes;
- 30 Farming XP for each branch pruned;
- an unseen sixth branch turning the plant into a Wild Jade Vine;
- 2,500 Slayer XP and a replacement seed after killing the Wild Vine; and
- Horacio's alternative removal service after health check for five coconuts
  and five watermelons, enabling another 1,500-XP growth cycle.

`Wild jade vine`, oldid `6457741` (`2012-10-23T02:22:38Z`), additionally
establishes:

- level 167, 2,500 LP, and level 59 Slayer;
- melee, Magic, and Ranged attacks with maximum hit 158 and poison beginning
  at 70;
- damage only from hatchets and dreadnips;
- 2,500 Slayer XP, 202 Woodcutting XP, ordinary Combat XP, and a replacement
  seed on a valid kill;
- a secateurs requirement before the fight;
- a stump-cutting step after victory; and
- leaving the dangerous encounter without completion.

Sources:

- <https://runescape.wiki/w/Jade_vine?oldid=6579442>
- <https://runescape.wiki/w/Wild_jade_vine?oldid=6457741>

Exact hidden disease rolls continue to use the existing Farming evidence and
contract. Exact Wild Vine attack distribution, bind behavior, and any combat
implementation values not stated above remain implementation-source work.

## World-clock growth

Jade Vine is an ordinary background Farming patch. It never reads the wall
clock and never performs offline catch-up.

- Sixteen source hours become 160 answered cards through the established
  `10 cards = 1 source hour` Farming clock.
- The six 160-minute growth stages retain their exact stage boundaries through
  the existing rational farm-clock minutes.
- After the health-check review, each branch interval is independently drawn
  from the sourced 30–60-minute range, or 5–10 answered cards.
- Disease, cure, death, compost, wildblood-hop protection, HUD alerts, and undo
  reuse the ordinary Farming contract.

The branch counter does not begin at maturity. Health check is the boundary
that arms branch growth.

## One saved policy, not a checkbox wall

The Handelmort patch detail exposes one saved **Jade Vine policy**:

1. **Keep tame — prune branches** (default)
2. **Train Slayer — let it grow wild**
3. **Train Farming — uproot and replant**

The status line always shows the selected policy, current visible branch count,
next branch boundary in reviews, and whether the next unpruned branch makes the
vine wild. This resolves the semantic concern raised by the independent Fable
review without splitting one decision into multiple toggles.

### Keep tame

When a branch becomes available, the plan automatically queues one ordinary
`Prune` Farming step. A successful review removes one branch and grants exactly
30 Farming XP. Multiple accumulated branches require one source action each;
there is no passive XP grant or six-branch batch.

The queued prune is automatic but not free. It follows the existing Farming
rule that a queued field verb preempts the next successful foreground review.
`Again` advances growth but performs no prune. If repeated `Again` answers let
the unseen sixth branch arrive first, the vine authentically becomes wild.

### Train Slayer

No prune is queued. Five visible branches accumulate at their sourced
intervals, and the next interval changes the patch to `wild`. The Farming HUD
then exposes the Wild Vine encounter rather than calling it a crop ready to
chop.

### Train Farming

After the 1,500-XP health-check review, the saved policy asks Horacio to remove
the plant as an automatic direct NPC transaction. It atomically consumes five
coconuts and five watermelons, clears the patch, and queues the ordinary
one-review Plant step from the existing patch plan.

If the payment is unavailable, no substitute resources or silent policy change
occurs. The patch says `Replant blocked` and continues its authentic branch
growth. The player may supply the goods or change the one saved policy before
it becomes wild.

## Wild Vine Combat

The Wild Vine is an ordinary persistent Combat encounter, never a Farming
`Chop` shortcut:

- start preflight requires Slayer 59, a usable equipped hatchet through the
  shared target-equipment rules, and secateurs through inventory or toolbelt;
- one successful Combat review advances exactly `6 × M` immediate ticks;
- enemy LP, attack phases, poison, bind/status state, Prayer, supplies,
  specials, and RNG persist through the ordinary encounter contract;
- `Again` advances the world and farm clocks but no Combat state;
- death uses the ordinary dangerous-PvM grave path and leaves the patch wild;
- fleeing ends the active encounter and restores the Wild Vine for a later
  full-health attempt; and
- no review may kill the vine and begin another Farming or Combat cycle with
  unused ticks.

The killing review grants ordinary damage-based Combat XP, 2,500 Slayer XP, and
202 Woodcutting XP. Because secateurs are a mandatory preflight item and
cutting the defeated stump has no alternative benefit, AnkiScape performs that
stump cut atomically and grants the replacement seed in the same review. It
does not encode the source's forget-to-cut mistake as another mandatory card.

The fight preserves the source's hatchet-only damage, three attack styles,
poison, and bind effect. It adds no invented weakness, drop table, decay,
timeout, or wild-state expiration.

## Seed recovery and loss prevention

If the patch is empty or dead and the player owns no Jade vine seed anywhere,
the patch exposes Horacio's sourced replacement-seed claim as a free direct
command. It never consumes a review and never duplicates a seed while one
already exists or a living vine occupies the patch.

## Current implementation mismatches

The existing Farming slice has Jade Vine data but does not implement this
complete loop:

- `farming_logic.py:_process_patch_boundaries` makes all six outputs available
  at maturity before health check, rather than starting 30–60-minute branch
  growth after the check;
- `farming_logic.py:_harvest` creates a carried `Jade vine branch` item, while
  the pinned source only awards pruning XP;
- `farming_logic.py:_chop` instantly marks the level-167 monster killed with no
  Combat, Slayer XP, Woodcutting XP, poison, or requirements;
- seed recovery is deferred to a separate generic clear review;
- no saved policy or Horacio five-coconut/five-watermelon service exists; and
- `tests/test_farming.py` currently locks in the instant six-prune and
  instant-chop behavior.

The later implementation pass must replace those assertions, attach the
encounter to live cadence coverage, and preserve the rest of the Farming queue
and disease contract.

## Fable consultation

Fable's first unconstrained proposal was rejected because it used wall-clock
timestamps and invented growth stages, drops, weaknesses, and a weekly wither.
Its constrained critique correctly identified that policy timing needed clearer
language and recommended surfacing branch progress. The integrated design keeps
one descriptive policy dropdown and the visible branch/status line, while
rejecting its proposed second toggle and every invented mechanic.
